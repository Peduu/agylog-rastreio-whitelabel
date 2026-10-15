"""Prazo de entrega por faixa de CEP (Pedro + senior do TI, 15/10/2026).

A API do TMS nao traz prazo nem destino. O prazo sai de dado real:
- CEP do destinatario: banco do sistema de subir arquivos (envios_modelos.db, tabela registros_modelo), que o
  portal so LE (nunca grava) e que recebe o CEP sozinho a cada arquivo novo;
- tabela oficial de prazo por faixa de CEP (cep_inicial, cep_final, dias), importada no admin;
- data de cadastro no TMS: ocorrencia "1" (Criacao da solicitacao).

Regras que nao podem regredir: nada inventado (sem CEP ou sem faixa = sem prazo); o cliente so ve prazo enquanto o pedido
esta a caminho e nunca prazo vencido / "em atraso"; liga e desliga pelo admin (comeca desligado ate conferir com o TMS).
"""
import re
import sqlite3
import time
from datetime import datetime, timedelta, timezone

BRASILIA = timezone(timedelta(hours=-3))
A_CAMINHO = {"preparacao_transporte", "transferencia_franquia", "chegada_franquia", "em_rota_entrega"}
TABELAS_MODELOS = ("registros_modelo", "registros_modelo_legado")
_CACHE_CEP = {}            # codigo -> (cep, instante); o mesmo pedido e consultado de 30 em 30 s pela pagina aberta
_CACHE_SEGUNDOS = 600


def normalizar_cep(valor):
    """8 digitos ou "". Aceita 7 digitos (Excel come o zero da frente: 1310100 -> 01310100)."""
    d = re.sub(r"\D", "", str(valor or ""))
    if len(d) == 7:
        d = "0" + d
    return d if len(d) == 8 else ""


def criar_tabelas(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prazos_cep (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cep_inicial TEXT NOT NULL,
            cep_final TEXT NOT NULL,
            dias INTEGER NOT NULL,
            criado_em TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_prazos_cep_faixa ON prazos_cep(cep_inicial, cep_final)")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS config_portal (
            chave TEXT PRIMARY KEY,
            valor TEXT
        )
    """)


def ler_config(conn, chave, padrao=""):
    row = conn.execute("SELECT valor FROM config_portal WHERE chave = ?", (chave,)).fetchone()
    return row[0] if row and row[0] is not None else padrao


def gravar_config(conn, chave, valor):
    conn.execute("INSERT OR REPLACE INTO config_portal (chave, valor) VALUES (?, ?)",
                 (chave, str(valor)))


def configuracao(conn):
    return {
        "ligado": ler_config(conn, "prazo_cep_ligado", "0") == "1",
        "contagem": ler_config(conn, "prazo_cep_contagem", "corridos"),
    }


def substituir_faixas(conn, faixas):
    """Troca a tabela inteira (e a tabela oficial; nao mistura com a anterior). faixas = [(cep_ini, cep_fim, dias)]."""
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("DELETE FROM prazos_cep")
    conn.executemany("INSERT INTO prazos_cep (cep_inicial, cep_final, dias, criado_em) VALUES (?, ?, ?, ?)",
                     [(a, b, d, agora) for a, b, d in faixas])


def ler_faixas(linhas):
    """linhas = dicts com as colunas do arquivo. Devolve (faixas validas, ignoradas)."""
    def pegar(row, *nomes):
        for n in nomes:
            if n in row and str(row[n]).strip():
                return str(row[n]).strip()
        return ""

    faixas, ignoradas = [], 0
    for row in linhas:
        row = {str(k or "").strip().lower().replace(" ", "_"): v for k, v in row.items()}
        ini = normalizar_cep(pegar(row, "cep_inicial", "cep_ini", "cep_inicio", "inicio", "inicial", "de"))
        fim = normalizar_cep(pegar(row, "cep_final", "cep_fim", "fim", "final", "ate", "até"))
        dias_txt = pegar(row, "dias", "prazo", "prazo_dias", "dias_prazo", "prazo_(dias)")
        try:
            dias = int(float(dias_txt.replace(",", ".")))
        except ValueError:
            dias = -1
        if not ini or not fim or ini > fim or dias < 0 or dias > 120:
            ignoradas += 1
            continue
        faixas.append((ini, fim, dias))
    return faixas, ignoradas


def dias_para_cep(conn, cep):
    """Dias da faixa que contem o CEP (a mais estreita, se houver sobreposicao) ou None."""
    cep = normalizar_cep(cep)
    if not cep:
        return None
    row = conn.execute("""
        SELECT dias FROM prazos_cep
        WHERE cep_inicial <= ? AND cep_final >= ?
        ORDER BY CAST(cep_final AS INTEGER) - CAST(cep_inicial AS INTEGER) ASC, id ASC
        LIMIT 1
    """, (cep, cep)).fetchone()
    return int(row[0]) if row else None


def somar_dias(base, dias, uteis=False):
    """Data base + dias corridos, ou + dias uteis (pula sabado e domingo; feriados nao entram)."""
    if not uteis:
        return base + timedelta(days=dias)
    d, faltam = base, dias
    while faltam > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            faltam -= 1
    return d


def _data(texto):
    t = str(texto or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(t[:19], fmt)
        except ValueError:
            continue
    return None


def data_cadastro_tms(ocorrencias):
    """Data da ocorrencia "1" (Criacao da solicitacao) no TMS; sem ela, a primeira ocorrencia com data."""
    lista = [o for o in (ocorrencias or []) if _data(o.get("dtOcorrencia"))]
    cadastro = next((o for o in lista if str(o.get("codigoOcorrencia", "")).strip() == "1"), None)
    alvo = cadastro or (min(lista, key=lambda o: _data(o["dtOcorrencia"])) if lista else None)
    return _data(alvo["dtOcorrencia"]).date() if alvo else None


def cep_do_pedido(caminho_db, codigos):
    """CEP do destinatario no banco do sistema de subir arquivos (so leitura), pelo pedido ou pelo AR. "" se nao achar."""
    codigos = [str(c or "").strip().upper() for c in codigos if str(c or "").strip()]
    if not codigos or not caminho_db:
        return ""
    chave = "|".join([str(caminho_db)] + codigos)
    guardado = _CACHE_CEP.get(chave)
    if guardado and time.time() - guardado[1] < _CACHE_SEGUNDOS:
        return guardado[0]
    cep = ""
    try:
        conn = sqlite3.connect(f"file:{caminho_db}?mode=ro", uri=True)
        try:
            for tabela in TABELAS_MODELOS:
                colunas = {r[1] for r in conn.execute(f"PRAGMA table_info({tabela})").fetchall()}
                if "destinatario_cep" not in colunas:
                    continue
                chaves = [c for c in ("nroPedido", "idSolicitacaoInterno") if c in colunas]
                if not chaves:
                    continue
                marcas = ",".join("?" * len(codigos))
                onde = " OR ".join(f"UPPER(TRIM(CAST({c} AS TEXT))) IN ({marcas})" for c in chaves)
                ordem = "ORDER BY datetime(criado_em) DESC, rowid DESC" if "criado_em" in colunas else "ORDER BY rowid DESC"
                for (valor,) in conn.execute(f"SELECT destinatario_cep FROM {tabela} WHERE {onde} {ordem} LIMIT 5",
                                             codigos * len(chaves)).fetchall():
                    cep = normalizar_cep(valor)
                    if cep:
                        break
                if cep:
                    break
        finally:
            conn.close()
    except sqlite3.Error:
        cep = ""
    _CACHE_CEP[chave] = (cep, time.time())
    return cep


def calcular(conn, caminho_modelos, codigos, ocorrencias):
    """Detalhe do calculo (para o simulador do admin e para a pagina): dict ou None quando falta algum dado real."""
    cfg = configuracao(conn)
    cep = cep_do_pedido(caminho_modelos, codigos)
    dias = dias_para_cep(conn, cep) if cep else None
    base = data_cadastro_tms(ocorrencias)
    detalhe = {"cep": cep, "dias": dias, "cadastro": base, "contagem": cfg["contagem"], "ligado": cfg["ligado"], "prazo": None}
    if cep and dias is not None and base:
        detalhe["prazo"] = somar_dias(base, dias, cfg["contagem"] == "uteis")
    return detalhe


def prazo_para_cliente(detalhe, status_key, hoje=None):
    """"dd/mm/aaaa" so com tudo real, ligado, pedido a caminho e prazo de hoje em diante (nunca vencido). Senao ""."""
    if not detalhe or not detalhe.get("ligado") or not detalhe.get("prazo") or status_key not in A_CAMINHO:
        return ""
    if detalhe["prazo"] < (hoje or datetime.now(BRASILIA).date()):
        return ""
    return detalhe["prazo"].strftime("%d/%m/%Y")
