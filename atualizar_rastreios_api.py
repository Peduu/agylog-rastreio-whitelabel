import os
import sqlite3
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from app import buscar_rastreio_na_api, persistir_ocorrencias


DB_PATH = os.getenv("DB_PATH", "database.db")
LIMITE = int(os.getenv("API_UPDATE_BATCH_SIZE", "300"))
MAX_BATCHES = int(os.getenv("API_UPDATE_MAX_BATCHES", "8"))
MAX_WORKERS = int(os.getenv("API_UPDATE_MAX_WORKERS", "16"))
COMMIT_EVERY = int(os.getenv("API_UPDATE_COMMIT_EVERY", "25"))
VERBOSE_ITENS = os.getenv("API_UPDATE_VERBOSE_ITEMS", "").strip() == "1"

STATUS_FINAIS = ("ENTREGUE", "DEVOLVIDO", "CANCELADO", "CANCELADA")


def conectar():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def criar_indices(conn):
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_rastreios_fila_atualizacao
        ON rastreios(status_badge, ultima_atualizacao_api, data_cadastro_portal)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_rastreios_codigo
        ON rastreios(codigo)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_rastreios_data_cadastro_portal
        ON rastreios(data_cadastro_portal)
    """)
    conn.commit()


def buscar_rastreios_para_atualizar(conn):
    return conn.execute("""
        SELECT codigo, cnpj_cliente, status_badge, ultima_atualizacao_api, data_cadastro_portal
        FROM rastreios
        WHERE status_badge IS NULL
           OR status_badge = ''
           OR status_badge NOT IN ('ENTREGUE', 'DEVOLVIDO', 'CANCELADO', 'CANCELADA')
        ORDER BY
            CASE
                WHEN data_cadastro_portal IS NOT NULL AND date(data_cadastro_portal) >= date('now') THEN 0
                WHEN data_cadastro_portal IS NOT NULL AND date(data_cadastro_portal) >= date('now', '-2 day') THEN 1
                ELSE 2
            END,
            CASE
                WHEN ultima_atualizacao_api IS NULL THEN 0
                WHEN data_cadastro_portal IS NOT NULL AND date(data_cadastro_portal) >= date('now') THEN 1
                ELSE 2
            END,
            ultima_atualizacao_api ASC,
            data_cadastro_portal DESC,
            codigo ASC
        LIMIT ?
    """, (LIMITE,)).fetchall()


def atualizar_rastreio(conn, codigo, cnpj_cliente, resultado, agora):
    conn.execute("""
        UPDATE rastreios
        SET
            previsao = COALESCE(?, previsao),
            data_baixa = COALESCE(?, data_baixa),
            recebido_por = COALESCE(?, recebido_por),
            ultimo_status = COALESCE(?, ultimo_status),
            status_badge = COALESCE(?, status_badge),
            data_postagem = COALESCE(NULLIF(data_postagem, ''), ?),
            ultima_atualizacao_api = ?
        WHERE codigo = ? AND COALESCE(cnpj_cliente, '') = ?
    """, (
        resultado.get("previsao"),
        resultado.get("dataBaixa"),
        resultado.get("recebidoPor"),
        resultado.get("ultimoStatus"),
        resultado.get("statusBadge"),
        resultado.get("dataPostagem"),
        agora,
        codigo,
        cnpj_cliente
    ))

    # Persiste o histórico de ocorrências para alimentar as datas por etapa
    # no portal público. Idempotente (INSERT OR IGNORE).
    persistir_ocorrencias(conn, codigo, resultado.get("ocorrencias"))


def marcar_tentativa(conn, codigo, cnpj_cliente, agora):
    conn.execute("""
        UPDATE rastreios
        SET ultima_atualizacao_api = ?
        WHERE codigo = ? AND COALESCE(cnpj_cliente, '') = ?
    """, (agora, codigo, cnpj_cliente))


def log_item(mensagem):
    if VERBOSE_ITENS:
        print(mensagem)


def consultar_api(row):
    codigo = str(row["codigo"] or "").strip().upper()
    cnpj = str(row["cnpj_cliente"] or "").strip()

    if not codigo:
        return {"tipo": "ignorar", "codigo": "", "cnpj": cnpj}

    if not cnpj:
        return {"tipo": "sem_cnpj", "codigo": codigo, "cnpj": cnpj}

    try:
        resultado = buscar_rastreio_na_api(codigo, cnpj)
        if resultado:
            return {"tipo": "ok", "codigo": codigo, "cnpj": cnpj, "resultado": resultado}
        return {"tipo": "nao_encontrado", "codigo": codigo, "cnpj": cnpj}
    except Exception as error:
        return {"tipo": "erro", "codigo": codigo, "cnpj": cnpj, "erro": str(error)}


def processar_lote(conn, lote_numero, rastreios):
    print(f"Lote {lote_numero}: {len(rastreios)} registro(s)")

    atualizados = 0
    nao_encontrados = 0
    sem_cnpj = 0
    erros = 0
    processados_desde_commit = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(consultar_api, row) for row in rastreios]

        for future in as_completed(futures):
            item = future.result()
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tipo = item["tipo"]
            codigo = item["codigo"]
            cnpj = item["cnpj"]

            if tipo == "ignorar":
                continue

            if tipo == "sem_cnpj":
                sem_cnpj += 1
                marcar_tentativa(conn, codigo, cnpj, agora)
                log_item(f"SEM CNPJ: {codigo}")

            elif tipo == "ok":
                atualizar_rastreio(conn, codigo, cnpj, item["resultado"], agora)
                atualizados += 1
                log_item(f"OK: {codigo} | {item['resultado'].get('statusBadge')}")

            elif tipo == "nao_encontrado":
                marcar_tentativa(conn, codigo, cnpj, agora)
                nao_encontrados += 1
                log_item(f"NAO ENCONTRADO: {codigo}")

            elif tipo == "erro":
                marcar_tentativa(conn, codigo, cnpj, agora)
                erros += 1
                print(f"ERRO {codigo}: {item['erro']}")

            processados_desde_commit += 1
            if processados_desde_commit >= COMMIT_EVERY:
                conn.commit()
                processados_desde_commit = 0

    if processados_desde_commit:
        conn.commit()

    print(
        f"Lote {lote_numero} concluido | "
        f"atualizados={atualizados} | "
        f"nao_encontrados={nao_encontrados} | "
        f"sem_cnpj={sem_cnpj} | "
        f"erros={erros}"
    )

    return {
        "atualizados": atualizados,
        "nao_encontrados": nao_encontrados,
        "sem_cnpj": sem_cnpj,
        "erros": erros
    }


def main():
    print("=" * 60)
    print(f"Iniciando atualizacao API: {datetime.now()}")
    print(f"DB_PATH={DB_PATH}")
    print(
        f"LIMITE={LIMITE} | MAX_BATCHES={MAX_BATCHES} | "
        f"MAX_WORKERS={MAX_WORKERS} | COMMIT_EVERY={COMMIT_EVERY} | "
        f"VERBOSE_ITENS={VERBOSE_ITENS}"
    )
    print("=" * 60)

    conn = conectar()
    criar_indices(conn)

    totais = {
        "atualizados": 0,
        "nao_encontrados": 0,
        "sem_cnpj": 0,
        "erros": 0,
        "selecionados": 0,
        "lotes": 0
    }

    for lote_numero in range(1, MAX_BATCHES + 1):
        rastreios = buscar_rastreios_para_atualizar(conn)
        if not rastreios:
            print(f"Lote {lote_numero}: fila vazia, encerrando.")
            break

        totais["selecionados"] += len(rastreios)
        totais["lotes"] += 1
        resumo = processar_lote(conn, lote_numero, rastreios)

        for chave, valor in resumo.items():
            totais[chave] += valor

        if len(rastreios) < LIMITE:
            print(f"Lote {lote_numero}: abaixo do limite, encerrando.")
            break

    conn.close()

    print("=" * 60)
    print(f"Finalizado: {datetime.now()}")
    print(f"Lotes executados: {totais['lotes']}")
    print(f"Selecionados: {totais['selecionados']}")
    print(f"Atualizados: {totais['atualizados']}")
    print(f"Nao encontrados: {totais['nao_encontrados']}")
    print(f"Sem CNPJ: {totais['sem_cnpj']}")
    print(f"Erros: {totais['erros']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
