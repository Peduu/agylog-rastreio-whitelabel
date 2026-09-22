import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import re

import pandas as pd


DB_PATH = "/home/rastreamento/database.db"


def conectar_banco():
    return sqlite3.connect(DB_PATH)


def ler_arquivo(caminho_arquivo: str) -> pd.DataFrame:
    caminho = Path(caminho_arquivo)

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    extensao = caminho.suffix.lower()

    if extensao == ".csv":
        try:
            df = pd.read_csv(caminho_arquivo, dtype=str, encoding="utf-8", sep=";")
            if len(df.columns) == 1:
                df = pd.read_csv(caminho_arquivo, dtype=str, encoding="utf-8", sep="\t")
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(caminho_arquivo, dtype=str, encoding="latin1", sep=";")
                if len(df.columns) == 1:
                    df = pd.read_csv(caminho_arquivo, dtype=str, encoding="latin1", sep="\t")
            except Exception:
                df = pd.read_csv(caminho_arquivo, dtype=str, encoding="latin1", sep="\t")
        except Exception:
            df = pd.read_csv(caminho_arquivo, dtype=str, encoding="utf-8", sep="\t")
    elif extensao in [".xlsx", ".xls"]:
        df = pd.read_excel(caminho_arquivo, dtype=str)
    else:
        raise ValueError("Formato não suportado. Use .csv, .xlsx ou .xls")

    df = df.fillna("")
    df.columns = [str(col).strip().lower() for col in df.columns]

    print(f"Colunas encontradas no arquivo: {list(df.columns)}")
    return df


def garantir_colunas_rastreios(cursor):
    colunas_existentes = {
        row[1]
        for row in cursor.execute("PRAGMA table_info(rastreios)").fetchall()
    }

    if "cnpj_cliente" not in colunas_existentes:
        cursor.execute("ALTER TABLE rastreios ADD COLUMN cnpj_cliente TEXT")

    if "ultima_atualizacao_api" not in colunas_existentes:
        cursor.execute("ALTER TABLE rastreios ADD COLUMN ultima_atualizacao_api TEXT")

    if "nota_fiscal" not in colunas_existentes:
        cursor.execute("ALTER TABLE rastreios ADD COLUMN nota_fiscal TEXT")

    if "serie_nota_fiscal" not in colunas_existentes:
        cursor.execute("ALTER TABLE rastreios ADD COLUMN serie_nota_fiscal TEXT")

    if "data_postagem" not in colunas_existentes:
        cursor.execute("ALTER TABLE rastreios ADD COLUMN data_postagem TEXT")

    if "data_cadastro_portal" not in colunas_existentes:
        cursor.execute("ALTER TABLE rastreios ADD COLUMN data_cadastro_portal TEXT")


def normalizar_cnpj(valor):
    return re.sub(r"\D+", "", str(valor or ""))


def obter_dias_previsao_por_cnpj(cursor, cnpj_cliente):
    cnpj_normalizado = normalizar_cnpj(cnpj_cliente)
    if not cnpj_normalizado:
        return None

    regras = cursor.execute("""
        SELECT identificador, dias_previsao
        FROM regras_previsao
        WHERE ativo = 1
          AND tipo_regra = 'CNPJ'
        ORDER BY prioridade ASC, id ASC
    """).fetchall()

    for identificador, dias_previsao in regras:
        if normalizar_cnpj(identificador) == cnpj_normalizado:
            return int(dias_previsao)

    return None


def criar_tabelas():
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            cnpj_cliente TEXT,
            is_admin INTEGER DEFAULT 0,
            aprovado INTEGER DEFAULT 1
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rastreios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            destinatario TEXT NOT NULL,
            previsao TEXT,
            data_postagem TEXT,
            data_cadastro_portal TEXT,
            data_baixa TEXT,
            recebido_por TEXT,
            ultimo_status TEXT,
            status_badge TEXT,
            cnpj_cliente TEXT,
            ultima_atualizacao_api TEXT,
            nota_fiscal TEXT,
            serie_nota_fiscal TEXT
        )
        """
    )

    garantir_colunas_rastreios(cursor)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS log_acessos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            email_informado TEXT,
            sucesso INTEGER,
            ip TEXT,
            data_hora TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS log_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            nome_usuario TEXT,
            tipo_importacao TEXT,
            nome_arquivo TEXT,
            inseridos INTEGER,
            atualizados INTEGER,
            ignorados INTEGER,
            data_hora TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS regras_previsao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ativo INTEGER DEFAULT 1,
            prioridade INTEGER DEFAULT 100,
            tipo_regra TEXT NOT NULL,
            identificador TEXT NOT NULL,
            codigo_ocorrencia TEXT NOT NULL,
            dias_previsao INTEGER NOT NULL,
            descricao TEXT,
            data_criacao TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def padronizar_colunas_usuarios(df: pd.DataFrame) -> pd.DataFrame:
    mapa_colunas = {
        "nome": ["nome", "usuario", "usuário", "name", "nome_completo", "nome_usuario"],
        "email": ["email", "e-mail", "mail", "email_usuario", "email_cliente", "login"],
        "senha": ["senha", "password", "senha_usuario", "pass"],
        "cnpj_cliente": ["cnpj_cliente", "cnpj", "documento", "cnpj_empresa"],
        "is_admin": ["is_admin", "admin", "administrador", "tipo", "tipo_usuario", "nivel_acesso"],
    }

    colunas_renomear = {}

    for coluna_padrao, aliases in mapa_colunas.items():
        for alias in aliases:
            if alias in df.columns:
                colunas_renomear[alias] = coluna_padrao
                break

    if colunas_renomear:
        print(f"Renomeando colunas: {colunas_renomear}")
        df = df.rename(columns=colunas_renomear)

    return df


def padronizar_colunas_rastreios(df: pd.DataFrame) -> pd.DataFrame:
    mapa_colunas = {
        "codigo": [
            "codigo", "código", "cod_rastreio", "rastreio",
            "tracking", "tracking_code", "codigo_rastreio", "ar"
        ],
        "destinatario": [
            "destinatario", "destinatário", "nome_destinatario",
            "cliente", "nome_cliente"
        ],
        "previsao": [
            "previsao", "previsão", "previsao_entrega",
            "data_previsao"
        ],
        "data_postagem": [
            "data_postagem", "data postagem", "dt_postagem",
            "postagem", "data de postagem"
        ],
        "data_baixa": [
            "data_baixa", "baixa", "data baixa", "data_da_baixa", "dt_baixa"
        ],
        "recebido_por": [
            "recebido_por", "recebido por", "recebedor",
            "quem_recebeu", "recebido"
        ],
        "ultimo_status": [
            "ultimo_status", "último_status", "ultimo status",
            "status", "descricao_status", "status_atual"
        ],
        "status_badge": [
            "status_badge", "badge", "tipo_status",
            "faixa_status", "status_resumido", "badge_status"
        ],
        "cnpj_cliente": [
            "cnpj_cliente", "cnpj", "cnpj embarcador",
            "cnpj_embarcador", "documento", "cnpj_empresa"
        ],
        "nota_fiscal": [
            "nota_fiscal", "nota fiscal", "nf", "numero_nf", "numero_nota",
            "nro_nota", "nronota", "número_nf", "número_nota"
        ],
        "serie_nota_fiscal": [
            "serie_nota_fiscal", "serie nota fiscal", "serie_nf", "serie",
            "nro_serie", "serie_nota"
        ],
    }

    colunas_renomear = {}

    for coluna_padrao, aliases in mapa_colunas.items():
        for alias in aliases:
            if alias in df.columns:
                colunas_renomear[alias] = coluna_padrao
                break

    if colunas_renomear:
        print(f"Renomeando colunas: {colunas_renomear}")

    return df.rename(columns=colunas_renomear)


def importar_usuarios(caminho_arquivo: str):
    df = ler_arquivo(caminho_arquivo)
    df = padronizar_colunas_usuarios(df)

    colunas_necessarias = {"nome", "email", "senha"}
    faltando = colunas_necessarias - set(df.columns)

    if faltando:
        raise ValueError(
            f"Colunas obrigatórias ausentes no arquivo de usuários: {sorted(faltando)}\n"
            f"Colunas encontradas: {sorted(df.columns)}"
        )

    conn = conectar_banco()
    cursor = conn.cursor()

    inseridos = 0
    atualizados = 0
    ignorados = 0

    for idx, row in df.iterrows():
        nome = str(row["nome"]).strip()
        email = str(row["email"]).strip()
        senha = str(row["senha"]).strip()

        cnpj_cliente = None
        if "cnpj_cliente" in df.columns:
            cnpj_valor = str(row["cnpj_cliente"]).strip()
            if cnpj_valor and cnpj_valor.lower() != "nan":
                cnpj_cliente = cnpj_valor

        is_admin = 0
        if "is_admin" in df.columns:
            valor_admin = str(row["is_admin"]).strip().upper()
            if valor_admin in ["1", "TRUE", "SIM", "YES", "ADMIN", "ADMINISTRADOR"]:
                is_admin = 1

        if not nome or not email or not senha:
            print(f"Linha {idx + 2}: ignorada - dados incompletos")
            ignorados += 1
            continue

        usuario_existente = cursor.execute(
            "SELECT id FROM usuarios WHERE email = ?",
            (email,)
        ).fetchone()

        if usuario_existente:
            cursor.execute(
                """
                UPDATE usuarios
                SET nome = ?,
                    senha = ?,
                    cnpj_cliente = COALESCE(?, cnpj_cliente),
                    is_admin = ?
                WHERE email = ?
                """,
                (nome, senha, cnpj_cliente, is_admin, email)
            )
            atualizados += 1
            print(f"Atualizado: {email} - {nome}")
        else:
            cursor.execute(
                """
                INSERT INTO usuarios (nome, email, senha, cnpj_cliente, is_admin, aprovado)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (nome, email, senha, cnpj_cliente, is_admin)
            )
            inseridos += 1
            print(f"Inserido: {email} - {nome}")

    conn.commit()
    conn.close()

    print("\n" + "=" * 50)
    print("IMPORTAÇÃO DE USUÁRIOS")
    print("=" * 50)
    print(f"Inseridos: {inseridos}")
    print(f"Atualizados: {atualizados}")
    print(f"Ignorados: {ignorados}")
    print("=" * 50)

    return inseridos, atualizados, ignorados


def importar_rastreios(caminho_arquivo: str):
    df = ler_arquivo(caminho_arquivo)
    df = padronizar_colunas_rastreios(df)

    colunas_necessarias = {"codigo", "destinatario"}
    faltando = colunas_necessarias - set(df.columns)

    if faltando:
        raise ValueError(
            f"Colunas obrigatórias ausentes no arquivo de rastreios: {sorted(faltando)}\n"
            f"Colunas encontradas: {sorted(df.columns)}"
        )

    conn = conectar_banco()
    cursor = conn.cursor()
    garantir_colunas_rastreios(cursor)

    inseridos = 0
    atualizados = 0
    ignorados = 0

    for _, row in df.iterrows():
        codigo = str(row["codigo"]).strip().upper()
        destinatario = str(row["destinatario"]).strip() if str(row["destinatario"]).strip() else None
        data_cadastro_portal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        previsao = str(row["previsao"]).strip() if "previsao" in df.columns and str(row["previsao"]).strip() else None
        data_postagem = str(row["data_postagem"]).strip() if "data_postagem" in df.columns and str(row["data_postagem"]).strip() else None
        data_baixa = str(row["data_baixa"]).strip() if "data_baixa" in df.columns and str(row["data_baixa"]).strip() else None
        recebido_por = str(row["recebido_por"]).strip() if "recebido_por" in df.columns and str(row["recebido_por"]).strip() else None
        ultimo_status = str(row["ultimo_status"]).strip() if "ultimo_status" in df.columns and str(row["ultimo_status"]).strip() else None
        status_badge = str(row["status_badge"]).strip() if "status_badge" in df.columns and str(row["status_badge"]).strip() else None
        nota_fiscal = str(row["nota_fiscal"]).strip() if "nota_fiscal" in df.columns and str(row["nota_fiscal"]).strip() else None
        serie_nota_fiscal = str(row["serie_nota_fiscal"]).strip() if "serie_nota_fiscal" in df.columns and str(row["serie_nota_fiscal"]).strip() else None

        cnpj_cliente = None
        if "cnpj_cliente" in df.columns:
            cnpj_valor = str(row["cnpj_cliente"]).strip()
            if cnpj_valor and cnpj_valor.lower() != "nan":
                cnpj_cliente = cnpj_valor

        if not previsao and cnpj_cliente:
            dias_previsao = obter_dias_previsao_por_cnpj(cursor, cnpj_cliente)
            if dias_previsao is not None:
                previsao = (datetime.now() + pd.Timedelta(days=dias_previsao)).strftime("%d/%m/%Y")

        if not codigo or not destinatario:
            ignorados += 1
            continue

        rastreio_existente = cursor.execute(
            """
            SELECT id FROM rastreios
            WHERE codigo = ?
              AND COALESCE(cnpj_cliente, '') = COALESCE(?, '')
            """,
            (codigo, cnpj_cliente)
        ).fetchone()

        if rastreio_existente:
            cursor.execute(
                """
                UPDATE rastreios
                SET destinatario = COALESCE(?, destinatario),
                    previsao = ?,
                    data_postagem = COALESCE(?, data_postagem),
                    data_baixa = COALESCE(?, data_baixa),
                    recebido_por = COALESCE(?, recebido_por),
                    ultimo_status = COALESCE(?, ultimo_status),
                    status_badge = COALESCE(?, status_badge),
                    cnpj_cliente = COALESCE(?, cnpj_cliente),
                    data_cadastro_portal = COALESCE(data_cadastro_portal, ?),
                    nota_fiscal = COALESCE(?, nota_fiscal),
                    serie_nota_fiscal = COALESCE(?, serie_nota_fiscal)
                WHERE codigo = ?
                  AND COALESCE(cnpj_cliente, '') = COALESCE(?, '')
                """,
                (
                    destinatario,
                    previsao,
                    data_postagem,
                    data_baixa,
                    recebido_por,
                    ultimo_status,
                    status_badge,
                    cnpj_cliente,
                    data_cadastro_portal,
                    nota_fiscal,
                    serie_nota_fiscal,
                    codigo,
                    cnpj_cliente,
                )
            )
            atualizados += 1
        else:
            cursor.execute(
                """
                INSERT INTO rastreios (
                    codigo,
                    destinatario,
                    previsao,
                    data_postagem,
                    data_cadastro_portal,
                    data_baixa,
                    recebido_por,
                    ultimo_status,
                    status_badge,
                    cnpj_cliente,
                    nota_fiscal,
                    serie_nota_fiscal
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    codigo,
                    destinatario,
                    previsao,
                    data_postagem,
                    data_cadastro_portal,
                    data_baixa,
                    recebido_por,
                    ultimo_status,
                    status_badge,
                    cnpj_cliente,
                    nota_fiscal,
                    serie_nota_fiscal,
                )
            )
            inseridos += 1

    conn.commit()
    conn.close()

    return inseridos, atualizados, ignorados


def mostrar_uso():
    print("=" * 50)
    print("IMPORTADOR DE DADOS - CorelliLog")
    print("=" * 50)
    print("\nUso:")
    print("  python importar_dados.py usuarios /caminho/arquivo.csv")
    print("  python importar_dados.py rastreios /caminho/arquivo.csv")
    print("")
    print("Colunas esperadas para USUÁRIOS:")
    print("  - nome")
    print("  - email/login")
    print("  - senha")
    print("  - cnpj_cliente opcional")
    print("  - is_admin opcional")
    print("")
    print("Colunas esperadas para RASTREIOS:")
    print("  - codigo")
    print("  - destinatario")
    print("  - cnpj_cliente opcional")
    print("  - nota_fiscal opcional")
    print("  - serie_nota_fiscal opcional")
    print("  - previsao, data_postagem, data_baixa, recebido_por, ultimo_status, status_badge opcionais")
    print("=" * 50)


if __name__ == "__main__":
    criar_tabelas()

    if len(sys.argv) != 3:
        mostrar_uso()
        sys.exit(1)

    tipo_importacao = sys.argv[1].strip().lower()
    caminho_arquivo = sys.argv[2].strip()

    try:
        if tipo_importacao == "usuarios":
            inseridos, atualizados, ignorados = importar_usuarios(caminho_arquivo)
        elif tipo_importacao == "rastreios":
            inseridos, atualizados, ignorados = importar_rastreios(caminho_arquivo)

            print("\n" + "=" * 50)
            print("IMPORTAÇÃO DE RASTREIOS")
            print("=" * 50)
            print(f"Inseridos: {inseridos}")
            print(f"Atualizados: {atualizados}")
            print(f"Ignorados: {ignorados}")
            print("=" * 50)
        else:
            print("Tipo de importação inválido.")
            mostrar_uso()
            sys.exit(1)
    except Exception as e:
        print(f"Erro na importação: {e}")
        sys.exit(1)
