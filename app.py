import os
import random
import sqlite3
import string
import tempfile
import requests
import html
import re
import csv
import copy
import json
import threading
import time
import unicodedata
from depara_ocorrencias import DE_PARA_OCORRENCIAS, DE_PARA_INSUCESSO
from datetime import datetime, timedelta
from collections import OrderedDict
from io import StringIO

from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    send_from_directory,
    session,
)

from importar_dados import importar_rastreios

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "")
if not app.secret_key:
    raise RuntimeError("SECRET_KEY nao configurada")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
app.config["SESSION_REFRESH_EACH_REQUEST"] = True

MAX_LOGIN_TENTATIVAS = 5
TEMPO_BLOQUEIO_MINUTOS = 5
VINCULOS_AR_DB_PATH = os.environ.get(
    "VINCULOS_AR_DB_PATH",
    os.path.abspath(os.path.join(app.root_path, "..", "subir_arquivos", "vinculos_ar.db"))
)

TMS_API_URL = os.getenv(
    "TMS_API_URL",
    "https://corellilog.tmselite.com/api/ocorrencias/ocorrencianotafiscaldepara"
)
TMS_API_TOKEN = os.getenv("TMS_API_TOKEN", "").strip()
TMS_API_TIMEOUT = float(os.getenv("TMS_API_TIMEOUT", "12"))
TMS_API_DEBUG = os.getenv("TMS_API_DEBUG", "").strip() == "1"
INTERLOG_API_BASE_URL = os.getenv("INTERLOG_API_BASE_URL", "https://www.sicloweb.com.br/api/v1")
INTERLOG_API_TOKEN = os.getenv("INTERLOG_API_TOKEN", "").strip()
INTERLOG_API_TIMEOUT = 20
MODELOS_DB_PATH = os.getenv("MODELOS_DB_PATH", "").strip()

PUBLIC_TRACKING_CACHE_TTL = max(5, int(os.getenv("PUBLIC_TRACKING_CACHE_TTL", "45")))
PUBLIC_TRACKING_RATE_LIMIT = max(1, int(os.getenv("PUBLIC_TRACKING_RATE_LIMIT", "30")))
PUBLIC_TRACKING_RATE_WINDOW = max(10, int(os.getenv("PUBLIC_TRACKING_RATE_WINDOW", "60")))
PUBLIC_TRACKING_ARCHIVE_FALLBACK = os.getenv(
    "PUBLIC_TRACKING_ARCHIVE_FALLBACK", "0"
).strip() == "1"
_PUBLIC_TRACKING_CACHE = {}
_PUBLIC_TRACKING_CACHE_LOCK = threading.Lock()
_PUBLIC_TRACKING_RATE = {}
_PUBLIC_TRACKING_RATE_LOCK = threading.Lock()


def _carregar_cnpjs_por_cliente():
    bruto = os.getenv("PUBLIC_TRACKING_CLIENT_CNPJS", "{}").strip() or "{}"
    try:
        configurado = json.loads(bruto)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("PUBLIC_TRACKING_CLIENT_CNPJS deve ser um JSON valido") from exc

    if not isinstance(configurado, dict):
        raise RuntimeError("PUBLIC_TRACKING_CLIENT_CNPJS deve ser um objeto JSON")

    return {
        str(cliente).strip().lower(): str(cnpj).strip()
        for cliente, cnpj in configurado.items()
        if str(cliente).strip() and normalizar_cnpj(cnpj)
    }


def _cliente_tracking_normalizado(cliente):
    cliente = str(cliente or "").strip().lower()
    return cliente if re.fullmatch(r"[a-z0-9_-]{1,40}", cliente) else ""


def _ip_consulta_publica():
    # O Nginx deste host sobrescreve X-Real-IP com o endereco do cliente.
    return str(request.headers.get("X-Real-IP") or request.remote_addr or "desconhecido").strip()


def _excedeu_limite_consulta_publica(ip):
    agora = time.monotonic()
    inicio = agora - PUBLIC_TRACKING_RATE_WINDOW
    with _PUBLIC_TRACKING_RATE_LOCK:
        acessos = [instante for instante in _PUBLIC_TRACKING_RATE.get(ip, []) if instante >= inicio]
        excedeu = len(acessos) >= PUBLIC_TRACKING_RATE_LIMIT
        if not excedeu:
            acessos.append(agora)
        _PUBLIC_TRACKING_RATE[ip] = acessos
        return excedeu


def _obter_cache_tracking(chave):
    agora = time.monotonic()
    with _PUBLIC_TRACKING_CACHE_LOCK:
        item = _PUBLIC_TRACKING_CACHE.get(chave)
        if not item or item[0] <= agora:
            _PUBLIC_TRACKING_CACHE.pop(chave, None)
            return None
        return copy.deepcopy(item[1])


def _salvar_cache_tracking(chave, resultado):
    with _PUBLIC_TRACKING_CACHE_LOCK:
        _PUBLIC_TRACKING_CACHE[chave] = (
            time.monotonic() + PUBLIC_TRACKING_CACHE_TTL,
            copy.deepcopy(resultado),
        )


def _log_tms_debug(mensagem):
    if TMS_API_DEBUG:
        print(mensagem)


def _obter_primeiro_valor(item, *campos):
    if not isinstance(item, dict):
        return ""

    for campo in campos:
        valor = item.get(campo)
        if valor is None:
            continue

        texto = str(valor).strip()
        if texto and texto.lower() not in {"null", "none"}:
            return texto

    return ""


def _consultar_tms_api(payload, tipo_consulta, codigo, cnpj_cliente, headers):
    try:
        _log_tms_debug(f"[API] Consultando {tipo_consulta} | codigo={codigo} | cnpj={cnpj_cliente}")

        response = requests.post(
            TMS_API_URL,
            json=payload,
            headers=headers,
            timeout=TMS_API_TIMEOUT
        )

        _log_tms_debug(f"[API] Status HTTP ({tipo_consulta}): {response.status_code}")

        if response.status_code != 200:
            print(f"[API] HTTP {response.status_code} em {tipo_consulta} | codigo={codigo}")
            return None

        data = response.json()

        if data.get("flagErro"):
            mensagens = data.get("listaMensagens") or []
            mensagem = mensagens[0] if mensagens else "flagErro=True"
            _log_tms_debug(f"[API] flagErro=True ({tipo_consulta}) | codigo={codigo} | mensagem={mensagem}")
            return None

        resultados = data.get("listaResultados")
        quantidade_resultados = (
            len(resultados)
            if isinstance(resultados, list)
            else 1 if resultados else 0
        )
        _log_tms_debug(f"[API] listaResultados ({tipo_consulta}): {quantidade_resultados}")

        if not resultados:
            return None

        if isinstance(resultados, dict):
            resultados = [resultados]

        if not isinstance(resultados, list) or len(resultados) == 0:
            return None

        resultados_ordenados = ordenar_ocorrencias_por_data(resultados)

        ocorrencia_postagem = next(
            (
                item for item in resultados_ordenados
                if str(item.get("codigoOcorrencia", "")).strip() == "25"
            ),
            None
        )

        data_postagem = (
            str(ocorrencia_postagem.get("dtOcorrencia", "")).strip()
            if ocorrencia_postagem
            else None
        )

        previsao = calcular_previsao_api(resultados_ordenados, cnpj_cliente)
        ultimo = resultados_ordenados[-1]

        codigo_ocorrencia = str(ultimo.get("codigoOcorrencia", "")).strip()
        descricao_api = str(ultimo.get("descricaoOcorrencia", "")).strip()
        data_ocorrencia = str(ultimo.get("dtOcorrencia", "")).strip()
        cidade = str(ultimo.get("nomeCidade", "")).strip()
        uf = str(ultimo.get("uf", "")).strip()

        depara = DE_PARA_OCORRENCIAS.get(codigo_ocorrencia, {})

        if depara:
            status_badge = depara.get("statusBadge", "Atualizado via API")
            ultimo_status = depara.get("ultimoStatus", "")
        else:
            match_insucesso = re.fullmatch(r"4\s*-\s*(\d+)", codigo_ocorrencia)

            if match_insucesso:
                codigo_insucesso = match_insucesso.group(1)
                motivo = DE_PARA_INSUCESSO.get(codigo_insucesso)
                status_badge = "DEVOLVIDO"

                if motivo:
                    ultimo_status = f"Nao entregue por {motivo}"
                    descricao_api = "Volume nao entregue"
                else:
                    ultimo_status = "Nao entregue"
            else:
                status_badge = "Atualizado via API"
                ultimo_status = ""

        if descricao_api:
            if ultimo_status and descricao_api.lower() != ultimo_status.lower():
                ultimo_status = f"{ultimo_status} - {descricao_api}"
            elif not ultimo_status:
                ultimo_status = descricao_api

        if not ultimo_status:
            ultimo_status = f"Ocorrencia {codigo_ocorrencia}" if codigo_ocorrencia else "Ocorrencia localizada"

        localidade = " / ".join([v for v in [cidade, uf] if v]).strip()

        # Histórico completo de ocorrências (cada uma com sua data real),
        # para persistir e alimentar as datas por etapa no portal.
        ocorrencias_mapeadas = []
        for item in resultados_ordenados:
            cod_oc = str(item.get("codigoOcorrencia", "")).strip()
            dt_oc = str(item.get("dtOcorrencia", "")).strip()
            if not dt_oc:
                continue

            desc_oc = str(item.get("descricaoOcorrencia", "")).strip()
            dep_oc = DE_PARA_OCORRENCIAS.get(cod_oc, {})
            if dep_oc:
                badge_oc = dep_oc.get("statusBadge", "")
            elif re.fullmatch(r"4\s*-\s*(\d+)", cod_oc):
                badge_oc = "DEVOLVIDO"
            else:
                badge_oc = ""

            ocorrencias_mapeadas.append({
                "codigoOcorrencia": cod_oc,
                "descricao": desc_oc,
                "statusBadge": badge_oc,
                "dtOcorrencia": dt_oc,
            })

        resultado_final = {
            "codigo": codigo,
            "destinatario": localidade or "Consulta via API",
            "previsao": previsao,
            "dataBaixa": formatar_data_exibicao(data_ocorrencia),
            "recebidoPor": "",
            "ultimoStatus": ultimo_status,
            "statusBadge": status_badge,
            "dataPostagem": formatar_data_exibicao(data_postagem),
            "ocorrencias": ocorrencias_mapeadas
        }

        _log_tms_debug(
            f"[API] Resultado final ({tipo_consulta}): "
            f"status={resultado_final['statusBadge']} | codigo={codigo}"
        )
        return resultado_final

    except requests.RequestException as e:
        print(f"[API] Erro requests ({tipo_consulta}) no codigo {codigo}: {e}")
        return None
    except Exception as e:
        print(f"[API] Erro geral ({tipo_consulta}) no codigo {codigo}: {e}")
        return None

# ============================================================
# BANCO
# ============================================================

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def resolver_modelos_db_path():
    candidatos = []

    if MODELOS_DB_PATH:
        candidatos.append(MODELOS_DB_PATH)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidatos.extend([
        "/home/subir_arquivos/envios_modelos.db",
        os.path.abspath(os.path.join(base_dir, "..", "subir_arquivos", "envios_modelos.db")),
        os.path.abspath(os.path.join(os.getcwd(), "subir_arquivos", "envios_modelos.db")),
    ])

    vistos = set()
    for caminho in candidatos:
        if not caminho or caminho in vistos:
            continue
        vistos.add(caminho)
        if os.path.exists(caminho):
            return caminho

    return candidatos[0] if candidatos else ""


def get_modelos_db_connection():
    caminho = resolver_modelos_db_path()
    if not caminho or not os.path.exists(caminho):
        raise FileNotFoundError(f"Banco de modelos nao encontrado: {caminho}")
    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    return conn


def garantir_tabelas_app():
    conn = get_db_connection()
    cursor = conn.cursor()
    colunas_rastreios = {
        row[1]
        for row in cursor.execute("PRAGMA table_info(rastreios)").fetchall()
    }

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rastreios_ocorrencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            codigo_ocorrencia TEXT,
            descricao TEXT,
            status_badge TEXT,
            dt_ocorrencia TEXT NOT NULL,
            UNIQUE(codigo, codigo_ocorrencia, dt_ocorrencia)
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_rast_ocorr_codigo
        ON rastreios_ocorrencias(codigo)
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solicitacoes_custodia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_ar TEXT NOT NULL,
            tipo_solicitacao TEXT NOT NULL,
            nome TEXT,
            endereco TEXT,
            numero TEXT,
            complemento TEXT,
            bairro TEXT,
            cidade TEXT,
            cep TEXT,
            uf TEXT,
            ponto_referencia TEXT,
            usuario_id INTEGER,
            status TEXT DEFAULT 'ABERTO',
            data_criacao TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consulta_rastreio_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            codigo TEXT NOT NULL,
            status_badge TEXT,
            origem TEXT,
            data_hora TEXT NOT NULL
        )
    """)

    cursor.execute("""
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
    """)

    if "data_cadastro_portal" not in colunas_rastreios:
        cursor.execute("ALTER TABLE rastreios ADD COLUMN data_cadastro_portal TEXT")

    colunas_regras = {
        row[1]
        for row in cursor.execute("PRAGMA table_info(regras_previsao)").fetchall()
    }
    if "codigo_ocorrencia" in colunas_regras:
        cursor.execute("""
            UPDATE regras_previsao
            SET codigo_ocorrencia = COALESCE(NULLIF(codigo_ocorrencia, ''), 'GERAL')
        """)

    conn.commit()
    conn.close()


# ============================================================
# AUXILIARES
# ============================================================

def gerar_captcha_texto(tamanho=6):
    caracteres = string.ascii_uppercase + string.digits
    return "".join(random.choices(caracteres, k=tamanho))


def gerar_captcha_svg(texto):
    largura = 180
    altura = 60

    chars_svg = []
    x = 20

    for char in texto:
        y = random.randint(35, 48)
        rot = random.randint(-18, 18)
        size = random.randint(26, 32)
        chars_svg.append(
            f"<text x='{x}' y='{y}' font-size='{size}' "
            f"transform='rotate({rot} {x},{y})' "
            f"fill='#eaf2ff' font-family='Arial, sans-serif' font-weight='700'>{html.escape(char)}</text>"
        )
        x += 24

    linhas = []
    for _ in range(5):
        x1 = random.randint(0, largura)
        y1 = random.randint(0, altura)
        x2 = random.randint(0, largura)
        y2 = random.randint(0, altura)
        linhas.append(
            f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' "
            f"stroke='rgba(255,255,255,0.18)' stroke-width='1' />"
        )

    pontos = []
    for _ in range(40):
        cx = random.randint(0, largura)
        cy = random.randint(0, altura)
        r = random.randint(1, 2)
        pontos.append(
            f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='rgba(255,255,255,0.12)' />"
        )

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}">
      <rect width="100%" height="100%" rx="12" fill="#0f172a"/>
      {''.join(linhas)}
      {''.join(pontos)}
      {''.join(chars_svg)}
    </svg>
    """
    return svg.strip()


def parse_data_ocorrencia(valor):
    valor = str(valor or "").strip()
    if not valor:
        return None

    formatos = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
    ]

    for formato in formatos:
        try:
            if formato.startswith("%Y-%m-%d") and len(valor) >= 19:
                return datetime.strptime(valor[:19], formato)
            return datetime.strptime(valor, formato)
        except ValueError:
            pass

    return None


def formatar_data_exibicao(valor):
    texto = str(valor or "").strip()
    if not texto:
        return ""

    data = parse_data_ocorrencia(texto)
    if not data:
        return texto

    if data.hour == 0 and data.minute == 0 and data.second == 0:
        return data.strftime("%d/%m/%Y")

    return data.strftime("%d/%m/%Y às %H:%M")


def ordenar_ocorrencias_por_data(resultados):
    return sorted(
        resultados,
        key=lambda item: parse_data_ocorrencia(item.get("dtOcorrencia")) or datetime.min
    )


def _split_data_etapa(valor):
    """Converte uma data crua em {date, time} para exibir na etapa da timeline.

    Aceita ISO, DD/MM/YYYY e tambem o formato de exibicao 'DD/MM/YYYY às HH:MM'
    (como o data_baixa/data_postagem sao gravados no banco).
    """
    texto = str(valor or "").strip().replace(" às ", " ")
    if not texto:
        return None
    dt = parse_data_ocorrencia(texto)
    if not dt:
        return None
    hora = "" if (dt.hour == 0 and dt.minute == 0 and dt.second == 0) else dt.strftime("%H:%M")
    return {"date": dt.strftime("%d/%m/%Y"), "time": hora}


def persistir_ocorrencias(conn, codigo, ocorrencias):
    """Grava (idempotente) o histórico de ocorrencias de um rastreio.

    Usa INSERT OR IGNORE apoiado na UNIQUE(codigo, codigo_ocorrencia, dt_ocorrencia),
    de modo que reexecucoes do coletor nao duplicam linhas.
    """
    if not codigo or not ocorrencias:
        return

    codigo = str(codigo).strip().upper()

    for oc in ocorrencias:
        dt = str(oc.get("dtOcorrencia") or "").strip()
        if not dt:
            continue
        try:
            conn.execute("""
                INSERT OR IGNORE INTO rastreios_ocorrencias
                    (codigo, codigo_ocorrencia, descricao, status_badge, dt_ocorrencia)
                VALUES (?, ?, ?, ?, ?)
            """, (
                codigo,
                str(oc.get("codigoOcorrencia") or "").strip(),
                str(oc.get("descricao") or "").strip(),
                str(oc.get("statusBadge") or "").strip(),
                dt,
            ))
        except Exception as erro:
            print(f"[OCORRENCIAS] Falha ao gravar {codigo}: {erro}")


def carregar_datas_etapas(codigo):
    """Retorna {status_key: {date, time}} com a data mais antiga de cada etapa.

    Mapeia cada ocorrencia (status_badge do TMS) para a etapa publica via
    converter_status_publico e mantem, por etapa, a ocorrencia mais antiga.
    Falhas degradam para dicionario vazio (o portal apenas nao mostra a data).
    """
    codigo = str(codigo or "").strip().upper()
    if not codigo:
        return {}

    try:
        conn = get_db_connection()
        rows = conn.execute("""
            SELECT status_badge, dt_ocorrencia
            FROM rastreios_ocorrencias
            WHERE codigo = ?
            ORDER BY dt_ocorrencia ASC
        """, (codigo,)).fetchall()
        conn.close()
    except Exception as erro:
        print(f"[OCORRENCIAS] Falha ao ler {codigo}: {erro}")
        return {}

    datas = {}
    for row in rows:
        stage_key = converter_status_publico(row["status_badge"])
        if not stage_key:
            continue
        dt = parse_data_ocorrencia(row["dt_ocorrencia"])
        if not dt:
            continue
        if stage_key not in datas or dt < datas[stage_key]:
            datas[stage_key] = dt

    return {
        chave: {
            "date": valor.strftime("%d/%m/%Y"),
            "time": "" if (valor.hour == 0 and valor.minute == 0 and valor.second == 0) else valor.strftime("%H:%M"),
        }
        for chave, valor in datas.items()
    }


def montar_datas_etapas_ocorrencias(ocorrencias):
    """Monta datas da timeline a partir do histórico cru vindo do TMS.

    O rastreio público consulta o TMS em tempo real e, nesses casos, as datas
    ainda podem não existir em rastreios_ocorrencias. Este fallback usa apenas
    datas reais da API; etapa sem ocorrência segue vazia.
    """
    datas = {}
    primeira_ocorrencia = None

    for ocorrencia in ocorrencias or []:
        dt = parse_data_ocorrencia(ocorrencia.get("dtOcorrencia"))
        if not dt:
            continue

        if primeira_ocorrencia is None or dt < primeira_ocorrencia:
            primeira_ocorrencia = dt

        status_badge = str(ocorrencia.get("statusBadge") or "").strip().upper()
        if status_badge in {"CRIADA", "ARQUIVO RECEBIDO", "SOLICITAÇÃO REALIZADA"}:
            stage_key = "aguardando_postagem"
        elif status_badge in {"POSTADO", "OBJETO POSTADO", "PRE CADASTRADO", "EM SEPARAÇÃO"}:
            stage_key = "preparacao_transporte"
        else:
            stage_key = converter_status_publico(status_badge)
        if not stage_key:
            continue

        if stage_key not in datas or dt < datas[stage_key]:
            datas[stage_key] = dt

    if primeira_ocorrencia and "aguardando_postagem" not in datas:
        datas["aguardando_postagem"] = primeira_ocorrencia

    return {
        chave: {
            "date": valor.strftime("%d/%m/%Y"),
            "time": "" if (valor.hour == 0 and valor.minute == 0 and valor.second == 0) else valor.strftime("%H:%M"),
        }
        for chave, valor in datas.items()
    }


def normalizar_cnpj(valor):
    return re.sub(r"\D+", "", str(valor or ""))


def _normalizar_nome_validacao(valor):
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    return " ".join(texto.casefold().split())


def _nome_mascarado_simplecompany(nome):
    partes = str(nome or "").strip().split()
    if not partes:
        return ""
    primeiro = partes[0]
    return primeiro[:1] + "*" * max(len(primeiro) - 1, 0) + " " + " ".join(
        "*" * len(parte) for parte in partes[1:]
    )


def _buscar_nome_pedido_simplecompany(codigo):
    conn = get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT destinatario
            FROM rastreios
            WHERE codigo = ?
              AND replace(replace(replace(replace(IFNULL(cnpj_cliente, ''), '.', ''), '/', ''), '-', ''), ' ', '') = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (str(codigo or "").strip().upper(), "65949995000187"),
        ).fetchone()
        return str(row["destinatario"] or "").strip() if row else ""
    finally:
        conn.close()


def registrar_consulta_rastreio(usuario_id, codigo, status_badge="", origem=""):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO consulta_rastreio_log (
            usuario_id, codigo, status_badge, origem, data_hora
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        usuario_id,
        str(codigo or "").strip().upper(),
        str(status_badge or "").strip(),
        str(origem or "").strip(),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()


def buscar_rastreio_no_banco(codigo):
    conn = get_db_connection()

    row = conn.execute("""
        SELECT codigo, destinatario, previsao, data_postagem, data_baixa, recebido_por,
               ultimo_status, status_badge, cnpj_cliente, data_cadastro_portal
        FROM rastreios
        WHERE codigo = ?
    """, (codigo,)).fetchone()

    conn.close()

    if not row:
        return None

    resultado = {
        "codigo": row["codigo"],
        "destinatario": row["destinatario"],
        "previsao": row["previsao"],
        "dataPostagem": formatar_data_exibicao(row["data_postagem"]),
        "dataBaixa": formatar_data_exibicao(row["data_baixa"]),
        "recebidoPor": row["recebido_por"],
        "ultimoStatus": row["ultimo_status"],
        "statusBadge": row["status_badge"],
        "cnpjCliente": row["cnpj_cliente"],
        "dataCadastroPortal": row["data_cadastro_portal"],
        "dataPostagemRaw": row["data_postagem"],
        "dataBaixaRaw": row["data_baixa"],
        "datasEtapas": carregar_datas_etapas(row["codigo"])
    }

    return aplicar_previsao_oficial(resultado)


def buscar_vinculo_ar(codigo):
    codigo = str(codigo or "").strip().upper()
    if not codigo:
        return None

    if not os.path.exists(VINCULOS_AR_DB_PATH):
        return None

    conn = None
    try:
        conn = sqlite3.connect(VINCULOS_AR_DB_PATH)
        conn.row_factory = sqlite3.Row

        row = conn.execute("""
            SELECT ar_pai, ar_filho, nome_cliente, destinatario_nome
            FROM vinculos_ar
            WHERE UPPER(TRIM(ar_filho)) = ?
            LIMIT 1
        """, (codigo,)).fetchone()

        if not row:
            return None

        ar_pai = str(row["ar_pai"] or "").strip().upper()
        ar_filho = str(row["ar_filho"] or "").strip().upper()

        if not ar_pai or ar_pai == codigo:
            return None

        return {
            "ar_pai": ar_pai,
            "ar_filho": ar_filho,
            "nome_cliente": str(row["nome_cliente"] or "").strip(),
            "destinatario_nome": str(row["destinatario_nome"] or "").strip(),
        }
    except Exception as e:
        print(f"[VINCULO_AR] Erro ao consultar vínculo para {codigo}: {e}")
        return None
    finally:
        if conn:
            conn.close()


def enriquecer_resultado_com_vinculo(resultado, codigo_consultado, vinculo):
    if not resultado:
        return None

    resultado = dict(resultado)
    codigo_consultado = str(codigo_consultado or "").strip().upper()

    if not vinculo:
        resultado["codigo"] = codigo_consultado or resultado.get("codigo", "")
        return resultado

    ar_pai = str(vinculo.get("ar_pai") or "").strip().upper()
    ar_filho = str(vinculo.get("ar_filho") or codigo_consultado).strip().upper()
    destinatario_vinculo = str(vinculo.get("destinatario_nome") or "").strip()

    if destinatario_vinculo and not str(resultado.get("destinatario") or "").strip():
        resultado["destinatario"] = destinatario_vinculo

    resultado["codigo"] = codigo_consultado or ar_filho or resultado.get("codigo", "")
    resultado["codigoReferencia"] = ar_pai or resultado.get("codigo", "")
    resultado["codigoPai"] = ar_pai
    resultado["codigoFilho"] = ar_filho
    resultado["observacaoVinculo"] = f"Consulta realizada pela AR pai {ar_pai}."

    return resultado


def buscar_rastreio_logado(codigo, is_admin, cnpj_cliente, lista_cnpjs_admin):
    codigo_limpo = str(codigo or "").strip().upper()
    if not codigo_limpo:
        return None

    vinculo = buscar_vinculo_ar(codigo_limpo)
    codigo_referencia = vinculo["ar_pai"] if vinculo else codigo_limpo

    if vinculo:
        print(f"[RASTREIO] Código {codigo_limpo} vinculado à AR pai {codigo_referencia}")

    resultado_api = None
    resultado_banco = None

    if not is_admin:
        resultado_api = buscar_rastreio_na_api(codigo_referencia, cnpj_cliente)
    else:
        for cnpj in lista_cnpjs_admin:
            resultado_api = buscar_rastreio_na_api(codigo_referencia, cnpj)
            if resultado_api:
                print(f"[RASTREIO] Código {codigo_referencia} encontrado via API no CNPJ {cnpj}")
                break

    resultado_banco = buscar_rastreio_no_banco(codigo_referencia)

    if resultado_api:
        if resultado_banco and resultado_banco.get("destinatario"):
            resultado_api["destinatario"] = resultado_banco["destinatario"]
        elif vinculo and vinculo.get("destinatario_nome"):
            resultado_api["destinatario"] = vinculo["destinatario_nome"]
        else:
            resultado_api["destinatario"] = "Buscando nome do destinatário..."

        previsao_fixa = ""
        if resultado_banco and resultado_banco.get("previsao"):
            previsao_fixa = resultado_banco.get("previsao")
        elif resultado_api.get("previsao"):
            previsao_fixa = resultado_api.get("previsao")

        if previsao_fixa:
            resultado_api["previsao"] = previsao_fixa

        resultado_api = enriquecer_resultado_com_vinculo(resultado_api, codigo_limpo, vinculo)
        anexar_rastreio_terceiro(resultado_api)
        return resultado_api

    if resultado_banco:
        resultado_banco = enriquecer_resultado_com_vinculo(resultado_banco, codigo_limpo, vinculo)
        anexar_rastreio_terceiro(resultado_banco)
        return resultado_banco

    return None


def buscar_rastreio_publico(codigo, cliente=""):
    codigo_limpo = str(codigo or "").strip().upper()
    if not codigo_limpo:
        return None

    vinculo = buscar_vinculo_ar(codigo_limpo)
    codigo_referencia = vinculo["ar_pai"] if vinculo else codigo_limpo
    resultado_arquivado = buscar_rastreio_no_banco(codigo_referencia)

    cnpj_cliente = obter_cnpj_prioritario_do_codigo(codigo_referencia)
    cliente = _cliente_tracking_normalizado(cliente)
    cnpjs_por_cliente = _carregar_cnpjs_por_cliente()
    if cliente and cliente in cnpjs_por_cliente:
        cnpj_cliente = cnpjs_por_cliente[cliente]

    if not cnpj_cliente or not TMS_API_TOKEN:
        resultado = resultado_arquivado if PUBLIC_TRACKING_ARCHIVE_FALLBACK else None
        if resultado:
            resultado = enriquecer_resultado_com_vinculo(resultado, codigo_limpo, vinculo)
            anexar_rastreio_terceiro(resultado)
        return resultado

    chave_cache = (codigo_referencia, normalizar_cnpj(cnpj_cliente))
    resultado = _obter_cache_tracking(chave_cache)
    if resultado is None:
        resultado = buscar_rastreio_na_api(codigo_referencia, cnpj_cliente)
        _salvar_cache_tracking(chave_cache, resultado or False)
    if not resultado:
        resultado = resultado_arquivado if PUBLIC_TRACKING_ARCHIVE_FALLBACK else None
        if resultado:
            resultado = enriquecer_resultado_com_vinculo(resultado, codigo_limpo, vinculo)
            anexar_rastreio_terceiro(resultado)
        return resultado

    # O banco permanece apenas como arquivo e fonte de dados auxiliares. Status,
    # ocorrencias e datas acima sempre vieram da consulta em tempo real ao TMS.
    if resultado_arquivado and resultado_arquivado.get("destinatario"):
        resultado["destinatario"] = resultado_arquivado["destinatario"]

    resultado = enriquecer_resultado_com_vinculo(resultado, codigo_limpo, vinculo)
    anexar_rastreio_terceiro(resultado)
    return resultado


def listar_cnpjs_clientes():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT DISTINCT cnpj_cliente
        FROM usuarios
        WHERE cnpj_cliente IS NOT NULL
          AND TRIM(cnpj_cliente) <> ''
    """).fetchall()
    conn.close()

    return [row["cnpj_cliente"] for row in rows]


def listar_cnpjs_disponiveis():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT cnpj_cliente AS cnpj
        FROM usuarios
        WHERE cnpj_cliente IS NOT NULL AND TRIM(cnpj_cliente) <> ''
        UNION
        SELECT cnpj_cliente AS cnpj
        FROM rastreios
        WHERE cnpj_cliente IS NOT NULL AND TRIM(cnpj_cliente) <> ''
        ORDER BY cnpj
    """).fetchall()
    conn.close()

    vistos = OrderedDict()
    for row in rows:
        bruto = str(row["cnpj"] or "").strip()
        normalizado = normalizar_cnpj(bruto)
        if normalizado and normalizado not in vistos:
            vistos[normalizado] = bruto

    return [{"valor": valor, "normalizado": chave} for chave, valor in vistos.items()]


def obter_cnpj_prioritario_do_codigo(codigo):
    conn = get_db_connection()
    row = conn.execute("""
        SELECT cnpj_cliente
        FROM rastreios
        WHERE codigo = ?
          AND cnpj_cliente IS NOT NULL
          AND TRIM(cnpj_cliente) <> ''
        LIMIT 1
    """, (codigo,)).fetchone()
    conn.close()
    return row["cnpj_cliente"] if row else ""


def obter_regra_previsao(cnpj_cliente="", uf=""):
    conn = get_db_connection()
    regras = conn.execute("""
        SELECT id, tipo_regra, identificador, dias_previsao, descricao
        FROM regras_previsao
        WHERE ativo = 1
        ORDER BY prioridade ASC, id ASC
    """).fetchall()
    conn.close()

    cnpj_normalizado = normalizar_cnpj(cnpj_cliente)
    uf_normalizada = str(uf or "").strip().upper()

    for regra in regras:
        tipo = str(regra["tipo_regra"] or "").strip().upper()
        identificador = str(regra["identificador"] or "").strip()

        if tipo == "CNPJ" and cnpj_normalizado and normalizar_cnpj(identificador) == cnpj_normalizado:
            return regra

        if tipo == "UF" and uf_normalizada and identificador.upper() == uf_normalizada:
            return regra

    return None


def calcular_previsao_por_regra(data_base, cnpj_cliente="", uf=""):
    if not data_base:
        return ""

    regra = obter_regra_previsao(cnpj_cliente, uf)
    if not regra:
        return ""

    previsao = data_base + timedelta(days=int(regra["dias_previsao"]))
    return previsao.strftime("%d/%m/%Y")


def salvar_previsao_no_banco(codigo, cnpj_cliente, previsao):
    if not codigo or not previsao:
        return

    conn = get_db_connection()
    conn.execute("""
        UPDATE rastreios
        SET previsao = ?
        WHERE codigo = ?
          AND COALESCE(cnpj_cliente, '') = COALESCE(?, '')
    """, (previsao, codigo, cnpj_cliente))
    conn.commit()
    conn.close()


def aplicar_previsao_oficial(resultado):
    if not resultado:
        return resultado

    data_base = (
        parse_data_ocorrencia(resultado.get("dataCadastroPortal")) or
        parse_data_ocorrencia(resultado.get("dataPostagem")) or
        datetime.now()
    )

    previsao_regra = calcular_previsao_por_regra(
        data_base,
        resultado.get("cnpjCliente"),
        ""
    )

    if previsao_regra:
        resultado["previsao"] = previsao_regra
        salvar_previsao_no_banco(
            resultado.get("codigo"),
            resultado.get("cnpjCliente"),
            previsao_regra
        )

    return resultado


def buscar_rastreio_terceiro(codigo):
    codigo = str(codigo or "").strip().upper()
    if not codigo or not INTERLOG_API_TOKEN:
        return None

    url = f"{INTERLOG_API_BASE_URL.rstrip('/')}/{INTERLOG_API_TOKEN}/delivery/{codigo}/track"

    try:
        response = requests.get(url, timeout=INTERLOG_API_TIMEOUT)
        if response.status_code != 200:
            return None

        payload = response.json()
        if not isinstance(payload, dict):
            return None

        status = str(payload.get("status", "")).strip().lower()
        if status not in {"success", "sucess"}:
            return None

        found = payload.get("found")
        if str(found).strip().lower() not in {"true", "1"} and found is not True:
            return None

        registros = payload.get("data") or []
        if isinstance(registros, dict):
            registros = [registros]

        if not isinstance(registros, list) or not registros:
            return None

        registros_ordenados = sorted(
            registros,
            key=lambda item: (
                parse_data_ocorrencia(
                    _obter_primeiro_valor(
                        item,
                        "data_hora_movimento",
                        "dataHoraMovimento",
                        "data_movimento",
                        "dataMovimento",
                        "data_entrega",
                        "dataEntrega",
                    )
                )
                or datetime.min
            )
        )

        ultimo = registros_ordenados[-1]
        codigo_finalizacao = _obter_primeiro_valor(
            ultimo,
            "codigo_finalizacao",
            "codigoFinalizacao",
            "finalizacao",
        )

        mapa_finalizacao = {
            "0": "Pendente",
            "1": "Entregue",
            "2": "Devolvido",
            "3": "Sinistrado",
        }

        cidade = _obter_primeiro_valor(ultimo, "cidade_entrega", "cidadeEntrega", "cidade")
        uf = _obter_primeiro_valor(ultimo, "uf_entrega", "ufEntrega", "uf")
        codigo_correios = _obter_primeiro_valor(
            ultimo,
            "codentregacorreio",
            "codigoEntregaCorreio",
        )

        if not codigo_correios:
            return None

        return {
            "codigoTerceiro": codigo_correios,
        }

    except requests.RequestException as e:
        print(f"[INTERLOG] Erro requests no codigo {codigo}: {e}")
        return None
    except Exception as e:
        print(f"[INTERLOG] Erro geral no codigo {codigo}: {e}")
        return None


def buscar_codigo_correios_manual(codigo):
    codigo = str(codigo or "").strip().upper()
    if not codigo:
        return ""

    conn = get_db_connection()
    try:
        row = conn.execute("""
            SELECT codigo_correios
            FROM rastreios
            WHERE codigo = ?
            LIMIT 1
        """, (codigo,)).fetchone()
        return str(row["codigo_correios"] or "").strip().upper() if row else ""
    finally:
        conn.close()


def buscar_rastreio_na_api(codigo, cnpj_cliente, somente_pedido=False):
    if not cnpj_cliente:
        print(f"[API] Codigo {codigo}: sem cnpj_cliente")
        return None

    headers = {
        "Authorization": f"Bearer {TMS_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    if not somente_pedido:
        payload_nota = {
            "cnpjEmbarcador": cnpj_cliente,
            "listaNotasFiscais": [codigo]
        }

        resultado = _consultar_tms_api(payload_nota, "NOTA", codigo, cnpj_cliente, headers)
        if resultado:
            return resultado

    payload_pedido = {
        "cnpjEmbarcador": cnpj_cliente,
        "listaPedidos": [codigo]
    }

    resultado = _consultar_tms_api(payload_pedido, "PEDIDO", codigo, cnpj_cliente, headers)
    if resultado:
        return resultado

    return None

    if not cnpj_cliente:
        print(f"[API] Código {codigo}: sem cnpj_cliente")
        return None

    headers = {
        "Authorization": f"Bearer {TMS_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def log_debug(mensagem):
        if TMS_API_DEBUG:
            print(mensagem)

    def consultar_api(payload, tipo_consulta):
        try:
            print(f"[API] Consultando {tipo_consulta} | código={codigo} | cnpj={cnpj_cliente}")
            import json

            print("\n========== DEBUG CURL ==========")
            curl = f"""
curl -X POST "{TMS_API_URL}" \\
-H "Authorization: Bearer {TMS_API_TOKEN}" \\
-H "Content-Type: application/json" \\
-H "Accept: application/json" \\
-d '{json.dumps(payload)}'
"""
            print(curl)
            print("========== FIM CURL ==========\n")

            response = requests.post(
                TMS_API_URL,
                json=payload,
                headers=headers,
                timeout=TMS_API_TIMEOUT
            )

            print(f"[API] Status HTTP ({tipo_consulta}): {response.status_code}")
            print(f"[API] Resposta bruta ({tipo_consulta}): {response.text[:1000]}")

            if response.status_code != 200:
                return None

            data = response.json()

            if data.get("flagErro"):
                print(f"[API] flagErro=True ({tipo_consulta}) | mensagens={data.get('listaMensagens')} | erros={data.get('listaErros')}")
                return None

            resultados = data.get("listaResultados")
            print(f"[API] listaResultados ({tipo_consulta}): {resultados}")

            if not resultados:
                return None

            if isinstance(resultados, dict):
                resultados = [resultados]

            if not isinstance(resultados, list) or len(resultados) == 0:
                return None

            resultados_ordenados = ordenar_ocorrencias_por_data(resultados)

            ocorrencia_postagem = next(
                (
                    item for item in resultados_ordenados
                    if str(item.get("codigoOcorrencia", "")).strip() == "25"
                ),
                None
            )

            data_postagem = (
                str(ocorrencia_postagem.get("dtOcorrencia", "")).strip()
                if ocorrencia_postagem
                else None
            )

            previsao = calcular_previsao_api(resultados_ordenados, cnpj_cliente)
            ultimo = resultados_ordenados[-1]

            codigo_ocorrencia = str(ultimo.get("codigoOcorrencia", "")).strip()
            descricao_api = str(ultimo.get("descricaoOcorrencia", "")).strip()
            data_ocorrencia = str(ultimo.get("dtOcorrencia", "")).strip()
            cidade = str(ultimo.get("nomeCidade", "")).strip()
            uf = str(ultimo.get("uf", "")).strip()

            depara = DE_PARA_OCORRENCIAS.get(codigo_ocorrencia, {})

            if depara:
                status_badge = depara.get("statusBadge", "Atualizado via API")
                ultimo_status = depara.get("ultimoStatus", "")
            else:
                match_insucesso = re.fullmatch(r"4\s*-\s*(\d+)", codigo_ocorrencia)

                if match_insucesso:
                    codigo_insucesso = match_insucesso.group(1)
                    motivo = DE_PARA_INSUCESSO.get(codigo_insucesso)
                    status_badge = "DEVOLVIDO"

                    if motivo:
                        ultimo_status = f"Não entregue por {motivo}"
                        descricao_api = "Volume não entregue"
                    else:
                        ultimo_status = "Não entregue"
                else:
                    status_badge = "Atualizado via API"
                    ultimo_status = ""

            if descricao_api:
                if ultimo_status and descricao_api.lower() != ultimo_status.lower():
                    ultimo_status = f"{ultimo_status} - {descricao_api}"
                elif not ultimo_status:
                    ultimo_status = descricao_api

            if not ultimo_status:
                ultimo_status = f"Ocorrência {codigo_ocorrencia}" if codigo_ocorrencia else "Ocorrência localizada"

            localidade = " / ".join([v for v in [cidade, uf] if v]).strip()

            resultado_final = {
                "codigo": codigo,
                "destinatario": localidade or "Consulta via API",
                "previsao": previsao,
                "dataBaixa": formatar_data_exibicao(data_ocorrencia),
                "recebidoPor": "",
                "ultimoStatus": ultimo_status,
                "statusBadge": status_badge,
                "dataPostagem": formatar_data_exibicao(data_postagem)
            }

            print(f"[API] Resultado final ({tipo_consulta}): {resultado_final}")
            return resultado_final

        except requests.RequestException as e:
            print(f"[API] Erro requests ({tipo_consulta}) no código {codigo}: {e}")
            return None
        except Exception as e:
            print(f"[API] Erro geral ({tipo_consulta}) no código {codigo}: {e}")
            return None

    payload_nota = {
        "cnpjEmbarcador": cnpj_cliente,
        "listaNotasFiscais": [codigo]
    }

    resultado = consultar_api(payload_nota, "NOTA")
    if resultado:
        return resultado

    payload_pedido = {
        "cnpjEmbarcador": cnpj_cliente,
        "listaPedidos": [codigo]
    }

    resultado = consultar_api(payload_pedido, "PEDIDO")
    if resultado:
        return resultado

    return None


def anexar_rastreio_terceiro(resultado):
    if not resultado:
        return resultado

    codigo_referencia = resultado.get("codigoReferencia") or resultado.get("codigo")
    codigo_correios_manual = buscar_codigo_correios_manual(codigo_referencia)
    rastreio_terceiro = (
        {"codigoTerceiro": codigo_correios_manual}
        if codigo_correios_manual
        else buscar_rastreio_terceiro(codigo_referencia)
    )
    if rastreio_terceiro:
        resultado["rastreioTerceiro"] = rastreio_terceiro

    return resultado


def listar_colunas_modelos():
    conn = get_modelos_db_connection()
    rows = conn.execute("PRAGMA table_info(registros_modelo)").fetchall()
    conn.close()
    return [row["name"] for row in rows]


def normalizar_colunas_modelos(colunas_solicitadas):
    disponiveis = listar_colunas_modelos()
    if not colunas_solicitadas:
        return disponiveis

    permitidas = []
    for coluna in colunas_solicitadas:
        nome = str(coluna or "").strip()
        if nome and nome in disponiveis and nome not in permitidas:
            permitidas.append(nome)

    return permitidas or disponiveis


def consultar_modelos_db(filtros, colunas=None, limite=100):
    colunas = normalizar_colunas_modelos(colunas)
    colunas_query = list(colunas)
    if "id" not in colunas_query:
        colunas_query.insert(0, "id")
    limite = max(1, min(int(limite or 100), 1000))

    busca = str((filtros or {}).get("busca", "")).strip()
    modelo = str((filtros or {}).get("modelo", "")).strip()
    uf = str((filtros or {}).get("uf", "")).strip().upper()
    cidade = str((filtros or {}).get("cidade", "")).strip()
    nome_arquivo = str((filtros or {}).get("nome_arquivo", "")).strip()

    where = []
    params = []

    if busca:
        termo = f"%{busca}%"
        where.append("""
            (
                idSolicitacaoInterno LIKE ?
                OR IFNULL(nroPedido, '') LIKE ?
                OR IFNULL(destinatario_nome, '') LIKE ?
                OR IFNULL(nome_arquivo, '') LIKE ?
                OR IFNULL(destinatario_cep, '') LIKE ?
                OR IFNULL(destinatario_cpf, '') LIKE ?
                OR IFNULL(destinatario_cnpj, '') LIKE ?
            )
        """)
        params.extend([termo] * 7)

    if modelo:
        where.append("modelo_nome = ?")
        params.append(modelo)

    if uf:
        where.append("UPPER(IFNULL(destinatario_uf, '')) = ?")
        params.append(uf)

    if cidade:
        where.append("IFNULL(destinatario_cidade, '') LIKE ?")
        params.append(f"%{cidade}%")

    if nome_arquivo:
        where.append("IFNULL(nome_arquivo, '') LIKE ?")
        params.append(f"%{nome_arquivo}%")

    query = f"SELECT {', '.join(colunas_query)} FROM registros_modelo"
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY datetime(criado_em) DESC, id DESC LIMIT ?"
    params.append(limite)

    conn = get_modelos_db_connection()
    rows = conn.execute(query, tuple(params)).fetchall()
    conn.close()

    registros = []
    for row in rows:
        item = dict(row)
        for chave in ["criado_em", "atualizado_em"]:
            if chave in item:
                item[chave] = formatar_data_exibicao(item.get(chave))
        registros.append(item)

    return {
        "colunas": colunas,
        "registros": registros,
        "total": len(registros),
    }


def obter_detalhes_modelo_registro(registro_id):
    conn = get_modelos_db_connection()
    row = conn.execute("""
        SELECT *
        FROM registros_modelo
        WHERE id = ?
        LIMIT 1
    """, (registro_id,)).fetchone()

    if not row:
        conn.close()
        return None

    registro = dict(row)
    solicitacao = registro.get("idSolicitacaoInterno")
    extras_rows = conn.execute("""
        SELECT campo, valor
        FROM registros_modelo_legado
        WHERE id_solicitacao_interno = ?
        ORDER BY campo ASC
    """, (solicitacao,)).fetchall()
    conn.close()

    for chave in ["criado_em", "atualizado_em"]:
        registro[chave] = formatar_data_exibicao(registro.get(chave))

    extras = [{"campo": item["campo"], "valor": item["valor"]} for item in extras_rows]

    return {
        "registro": registro,
        "extras": extras,
    }


def obter_meta_modelos_db():
    conn = get_modelos_db_connection()
    total_registros = conn.execute("SELECT COUNT(*) FROM registros_modelo").fetchone()[0]
    total_modelos = conn.execute("SELECT COUNT(DISTINCT modelo_nome) FROM registros_modelo").fetchone()[0]
    total_arquivos = conn.execute("SELECT COUNT(DISTINCT nome_arquivo) FROM registros_modelo").fetchone()[0]
    ultima_atualizacao = conn.execute("""
        SELECT atualizado_em
        FROM registros_modelo
        ORDER BY datetime(atualizado_em) DESC, id DESC
        LIMIT 1
    """).fetchone()
    modelos = conn.execute("""
        SELECT DISTINCT modelo_nome
        FROM registros_modelo
        WHERE modelo_nome IS NOT NULL AND TRIM(modelo_nome) <> ''
        ORDER BY modelo_nome ASC
    """).fetchall()
    ufs = conn.execute("""
        SELECT DISTINCT destinatario_uf
        FROM registros_modelo
        WHERE destinatario_uf IS NOT NULL AND TRIM(destinatario_uf) <> ''
        ORDER BY destinatario_uf ASC
    """).fetchall()
    conn.close()

    return {
        "resumo": {
            "total_registros": total_registros,
            "total_modelos": total_modelos,
            "total_arquivos": total_arquivos,
            "ultima_atualizacao": formatar_data_exibicao(ultima_atualizacao[0] if ultima_atualizacao else ""),
        },
        "colunas": listar_colunas_modelos(),
        "modelos": [row[0] for row in modelos],
        "ufs": [row[0] for row in ufs],
        "caminho": resolver_modelos_db_path(),
    }


def obter_agencia_registro_modelo(registro):
    if not registro:
        return ""

    for chave in ["OBS1", "observacoes", "OBS2", "OBS3"]:
        valor = str(registro.get(chave, "") or "").strip()
        if valor:
            return valor

    return ""


def buscar_modelo_por_codigo(codigo, colunas=None):
    codigo = str(codigo or "").strip()
    if not codigo:
        return None

    colunas = normalizar_colunas_modelos(colunas)
    colunas_query = list(colunas)
    for obrigatoria in ["id", "OBS1", "observacoes"]:
        if obrigatoria not in colunas_query:
            colunas_query.append(obrigatoria)

    conn = get_modelos_db_connection()
    row = conn.execute(f"""
        SELECT {', '.join(colunas_query)}
        FROM registros_modelo
        WHERE idSolicitacaoInterno = ?
           OR IFNULL(nroPedido, '') = ?
        ORDER BY datetime(criado_em) DESC, id DESC
        LIMIT 1
    """, (codigo, codigo)).fetchone()
    conn.close()

    if not row:
        return None

    registro = dict(row)
    for chave in ["criado_em", "atualizado_em"]:
        if chave in registro:
            registro[chave] = formatar_data_exibicao(registro.get(chave))

    registro["agencia"] = obter_agencia_registro_modelo(registro)
    return registro


def login_bloqueado():
    bloqueado_ate = session.get("login_bloqueado_ate")
    if not bloqueado_ate:
        return False, 0

    agora = datetime.now()
    ate = datetime.fromisoformat(bloqueado_ate)

    if agora >= ate:
        session.pop("login_bloqueado_ate", None)
        session.pop("login_tentativas", None)
        return False, 0

    segundos_restantes = int((ate - agora).total_seconds())
    return True, segundos_restantes


def registrar_log_acesso(usuario_id, email_informado, sucesso, ip):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO log_acessos (
            usuario_id,
            email_informado,
            sucesso,
            ip,
            data_hora
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        usuario_id,
        email_informado,
        sucesso,
        ip,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()


# ============================================================
# ROTAS PRINCIPAIS
# ============================================================

@app.after_request
def add_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "script-src 'self'; "
        "connect-src 'self' https://viacep.com.br; "
        "frame-ancestors 'none';"
    )
    return response


@app.route("/api/session", methods=["GET"])
def api_session():
    if "usuario_id" not in session:
        return jsonify({
            "success": False,
            "authenticated": False
        }), 401

    return jsonify({
        "success": True,
        "authenticated": True,
        "usuario": {
            "id": session.get("usuario_id"),
            "nome": session.get("usuario_nome"),
            "email": session.get("usuario_email"),
            "is_admin": session.get("is_admin"),
            "cnpj_cliente": session.get("cnpj_cliente")
        }
    })


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/admin")
def admin():
    if "usuario_id" not in session:
        return "Não autenticado", 401

    if session.get("is_admin") != 1:
        return "Acesso negado", 403

    return render_template(
        "admin.html",
        usuario_nome=session.get("usuario_nome", "Administrador"),
        usuario_email=session.get("usuario_email", ""),
        is_admin=bool(session.get("is_admin"))
    )


@app.route("/admin/modelos")
def admin_modelos():
    if "usuario_id" not in session:
        return "Não autenticado", 401

    if session.get("is_admin") != 1:
        return "Acesso negado", 403

    return render_template(
        "admin_modelos.html",
        usuario_nome=session.get("usuario_nome", "Administrador"),
        usuario_email=session.get("usuario_email", ""),
        is_admin=bool(session.get("is_admin"))
    )


@app.route("/custodia")
def custodia():
    if "usuario_id" not in session:
        return "Não autenticado", 401

    return render_template(
        "custodia.html",
        usuario_nome=session.get("usuario_nome", "Usuário"),
        usuario_email=session.get("usuario_email", ""),
        is_admin=bool(session.get("is_admin"))
    )


# ============================================================
# COMPATIBILIDADE COM FRONT
# ============================================================

@app.route("/style.css")
def style_css():
    return send_from_directory("static", "style.css")


@app.route("/script.js")
def script_js():
    return send_from_directory("static", "script.js")


@app.route("/admin.css")
def admin_css():
    return send_from_directory("static", "admin.css")


@app.route("/admin.js")
def admin_js():
    return send_from_directory("static", "admin.js")


# ============================================================
# CAPTCHA LOGIN
# ============================================================

@app.route("/api/captcha/login", methods=["GET"])
def captcha_login():
    codigo = gerar_captcha_texto()
    session["login_captcha"] = codigo

    svg = gerar_captcha_svg(codigo)

    return jsonify({
        "success": True,
        "svg": svg
    })


# ============================================================
# LOGIN
# ============================================================

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email", "").strip()
    senha = data.get("senha", "").strip()
    captcha_answer = data.get("captcha_answer", "").strip().upper()
    honeypot = data.get("honeypot", "").strip()
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    bloqueado, segundos_restantes = login_bloqueado()
    if bloqueado:
        return jsonify({
            "success": False,
            "message": "Acesso temporariamente bloqueado por excesso de tentativas.",
            "locked": True,
            "seconds_remaining": segundos_restantes
        }), 429

    if honeypot:
        return jsonify({
            "success": False,
            "message": "Falha de validação."
        }), 400

    if not email or not senha or not captcha_answer:
        return jsonify({
            "success": False,
            "message": "Informe e-mail, senha e captcha."
        }), 400

    captcha_salvo = session.get("login_captcha", "")
    if not captcha_salvo or captcha_answer != captcha_salvo:
        tentativas = session.get("login_tentativas", 0) + 1
        session["login_tentativas"] = tentativas

        if tentativas >= MAX_LOGIN_TENTATIVAS:
            bloqueado_ate = datetime.now() + timedelta(minutes=TEMPO_BLOQUEIO_MINUTOS)
            session["login_bloqueado_ate"] = bloqueado_ate.isoformat()

            return jsonify({
                "success": False,
                "message": "Acesso bloqueado por excesso de tentativas.",
                "locked": True,
                "seconds_remaining": TEMPO_BLOQUEIO_MINUTOS * 60
            }), 429

        novo_captcha = gerar_captcha_texto()
        session["login_captcha"] = novo_captcha

        return jsonify({
            "success": False,
            "message": "Captcha inválido.",
            "new_captcha": novo_captcha
        }), 401

    conn = get_db_connection()

    usuario = conn.execute(
        "SELECT id, nome, email, senha, is_admin, cnpj_cliente, aprovado FROM usuarios WHERE email = ?",
        (email,)
    ).fetchone()

    if not usuario:
        conn.close()
        registrar_log_acesso(None, email, 0, ip)

        tentativas = session.get("login_tentativas", 0) + 1
        session["login_tentativas"] = tentativas

        if tentativas >= MAX_LOGIN_TENTATIVAS:
            bloqueado_ate = datetime.now() + timedelta(minutes=TEMPO_BLOQUEIO_MINUTOS)
            session["login_bloqueado_ate"] = bloqueado_ate.isoformat()

            return jsonify({
                "success": False,
                "message": "Acesso bloqueado por excesso de tentativas.",
                "locked": True,
                "seconds_remaining": TEMPO_BLOQUEIO_MINUTOS * 60
            }), 429

        novo_captcha = gerar_captcha_texto()
        session["login_captcha"] = novo_captcha

        return jsonify({
            "success": False,
            "message": "Usuário não encontrado.",
            "new_captcha": novo_captcha
        }), 401

    if usuario["senha"] != senha:
        conn.close()
        registrar_log_acesso(usuario["id"], email, 0, ip)

        tentativas = session.get("login_tentativas", 0) + 1
        session["login_tentativas"] = tentativas

        if tentativas >= MAX_LOGIN_TENTATIVAS:
            bloqueado_ate = datetime.now() + timedelta(minutes=TEMPO_BLOQUEIO_MINUTOS)
            session["login_bloqueado_ate"] = bloqueado_ate.isoformat()

            return jsonify({
                "success": False,
                "message": "Acesso bloqueado por excesso de tentativas.",
                "locked": True,
                "seconds_remaining": TEMPO_BLOQUEIO_MINUTOS * 60
            }), 429

        novo_captcha = gerar_captcha_texto()
        session["login_captcha"] = novo_captcha

        return jsonify({
            "success": False,
            "message": "Senha inválida.",
            "new_captcha": novo_captcha
        }), 401

    if not usuario["aprovado"]:
        conn.close()
        registrar_log_acesso(usuario["id"], email, 0, ip)

        novo_captcha = gerar_captcha_texto()
        session["login_captcha"] = novo_captcha

        return jsonify({
            "success": False,
            "message": "Seu cadastro ainda está pendente de liberação pelo administrador.",
            "new_captcha": novo_captcha
        }), 403

    conn.close()

    session.permanent = True
    session["usuario_id"] = usuario["id"]
    session["usuario_email"] = usuario["email"]
    session["usuario_nome"] = usuario["nome"]
    session["is_admin"] = bool(usuario["is_admin"])
    session["cnpj_cliente"] = usuario["cnpj_cliente"]

    session["login_tentativas"] = 0
    session.pop("login_bloqueado_ate", None)
    session["login_captcha"] = gerar_captcha_texto()

    registrar_log_acesso(usuario["id"], usuario["email"], 1, ip)

    return jsonify({
        "success": True,
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "is_admin": usuario["is_admin"]
        }
    })


# ============================================================
# CADASTRO
# ============================================================

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    nome = data.get("nome", "").strip()
    sobrenome = data.get("sobrenome", "").strip()
    email = data.get("email", "").strip().lower()
    senha = data.get("senha", "").strip()
    confirmar_senha = data.get("confirmar_senha", "").strip()

    if not nome or not sobrenome or not email or not senha or not confirmar_senha:
        return jsonify({
            "success": False,
            "message": "Preencha todos os campos do cadastro."
        }), 400

    if senha != confirmar_senha:
        return jsonify({
            "success": False,
            "message": "As senhas não coincidem."
        }), 400

    if len(senha) < 8:
        return jsonify({
            "success": False,
            "message": "A senha deve ter pelo menos 8 caracteres."
        }), 400

    nome_completo = f"{nome} {sobrenome}".strip()

    conn = get_db_connection()
    existente = conn.execute(
        "SELECT id FROM usuarios WHERE email = ?",
        (email,)
    ).fetchone()

    if existente:
        conn.close()
        return jsonify({
            "success": False,
            "message": "Já existe um usuário com esse e-mail."
        }), 409

    conn.execute("""
        INSERT INTO usuarios (nome, email, senha, is_admin, cnpj_cliente, aprovado)
        VALUES (?, ?, ?, 0, NULL, 0)
    """, (nome_completo, email, senha))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Cadastro enviado com sucesso. Aguarde a liberação"
    })


# ============================================================
# LOGOUT
# ============================================================

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/api/admin/regras-previsao", methods=["GET"])
def listar_regras_previsao():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "NÃ£o autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, ativo, prioridade, tipo_regra, identificador, codigo_ocorrencia,
               dias_previsao, descricao, data_criacao
        FROM regras_previsao
        ORDER BY prioridade ASC, id ASC
    """).fetchall()
    conn.close()

    return jsonify({
        "success": True,
        "regras": [dict(row) for row in rows]
    })


@app.route("/api/admin/regras-previsao", methods=["POST"])
def criar_regra_previsao():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "NÃ£o autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    data = request.get_json() or {}
    tipo_regra = str(data.get("tipo_regra", "")).strip().upper()
    identificador = str(data.get("identificador", "")).strip()
    codigo_ocorrencia = "GERAL"
    descricao = str(data.get("descricao", "")).strip()

    try:
        dias_previsao = int(data.get("dias_previsao", 0))
        prioridade = int(data.get("prioridade", 100))
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Dias e prioridade precisam ser numÃ©ricos."}), 400

    if tipo_regra not in ["CNPJ", "UF"]:
        return jsonify({"success": False, "message": "Tipo de regra invÃ¡lido."}), 400

    if not identificador:
        return jsonify({"success": False, "message": "Preencha o identificador da regra."}), 400

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO regras_previsao (
            ativo, prioridade, tipo_regra, identificador,
            codigo_ocorrencia, dias_previsao, descricao, data_criacao
        )
        VALUES (1, ?, ?, ?, ?, ?, ?, ?)
    """, (
        prioridade,
        tipo_regra,
        identificador,
        codigo_ocorrencia,
        dias_previsao,
        descricao,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Regra cadastrada com sucesso."})


@app.route("/api/admin/regras-previsao/<int:regra_id>", methods=["DELETE"])
def excluir_regra_previsao(regra_id):
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "NÃ£o autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    conn = get_db_connection()
    conn.execute("DELETE FROM regras_previsao WHERE id = ?", (regra_id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Regra removida com sucesso."})


@app.route("/api/admin/regras-previsao/modelo-csv", methods=["GET"])
def baixar_modelo_regras_previsao_csv():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Nao autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    conteudo = "\n".join([
        "tipo_regra;identificador;dias_previsao;prioridade;descricao",
        "CNPJ;12345678000199;3;10;Regra para cliente exemplo",
        "UF;SP;2;20;Regra por UF"
    ])
    return Response(
        "\ufeff" + conteudo,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=modelo_regras_previsao.csv"}
    )


@app.route("/api/admin/regras-previsao/importar-csv", methods=["POST"])
def importar_regras_previsao_csv():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Nao autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    arquivo = request.files.get("arquivo")
    if not arquivo or not arquivo.filename:
        return jsonify({"success": False, "message": "Envie um arquivo CSV."}), 400

    bruto = arquivo.read()
    conteudo = None
    for encoding in ["utf-8-sig", "utf-8", "latin1"]:
        try:
            conteudo = bruto.decode(encoding)
            break
        except UnicodeDecodeError:
            continue

    if conteudo is None:
        return jsonify({"success": False, "message": "Nao foi possivel ler o arquivo CSV."}), 400

    leitor = csv.DictReader(StringIO(conteudo), delimiter=";")
    inseridos = 0
    ignorados = 0
    conn = get_db_connection()

    for row in leitor:
        tipo_regra = str(row.get("tipo_regra", "")).strip().upper()
        identificador = str(row.get("identificador", "")).strip()
        descricao = str(row.get("descricao", "")).strip()

        try:
            dias_previsao = int(str(row.get("dias_previsao", "")).strip())
            prioridade = int(str(row.get("prioridade", "")).strip() or "100")
        except ValueError:
            ignorados += 1
            continue

        if tipo_regra not in ["CNPJ", "UF"] or not identificador:
            ignorados += 1
            continue

        conn.execute("""
            INSERT INTO regras_previsao (
                ativo, prioridade, tipo_regra, identificador,
                codigo_ocorrencia, dias_previsao, descricao, data_criacao
            )
            VALUES (1, ?, ?, ?, 'GERAL', ?, ?, ?)
        """, (
            prioridade,
            tipo_regra,
            identificador,
            dias_previsao,
            descricao,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        inseridos += 1

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": f"Importacao concluida. Inseridas: {inseridos}. Ignoradas: {ignorados}."
    })


# ============================================================
# RASTREIO
# ============================================================

def calcular_previsao_api(resultados, cnpj_cliente=""):
    if not resultados:
        return ""

    resultados_ordenados = ordenar_ocorrencias_por_data(resultados)
    primeira = resultados_ordenados[0]
    data_base = parse_data_ocorrencia(primeira.get("dtOcorrencia"))
    uf = str(primeira.get("uf", "")).strip().upper()
    return calcular_previsao_por_regra(data_base, cnpj_cliente, uf)


@app.route("/api/rastreio", methods=["POST"])
def rastreio():
    if "usuario_id" not in session:
        return jsonify({
            "success": False,
            "message": "Usuário não autenticado"
        }), 401

    data = request.get_json() or {}
    codigos = data.get("codigos", [])

    resultados = []
    is_admin = bool(session.get("is_admin"))
    cnpj_cliente = session.get("cnpj_cliente")

    print(f"[RASTREIO] is_admin={is_admin} | cnpj_cliente={cnpj_cliente} | codigos={codigos}")

    lista_cnpjs_admin = []
    if is_admin:
        lista_cnpjs_admin = listar_cnpjs_clientes()
        codigo_prioritario = str(codigos[0]).strip().upper() if codigos else ""
        vinculo_prioritario = buscar_vinculo_ar(codigo_prioritario) if codigo_prioritario else None
        codigo_prioritario_referencia = (
            vinculo_prioritario["ar_pai"] if vinculo_prioritario else codigo_prioritario
        )
        cnpj_prioritario = obter_cnpj_prioritario_do_codigo(codigo_prioritario_referencia) if codigo_prioritario_referencia else ""
        if cnpj_prioritario:
            lista_cnpjs_admin = [cnpj_prioritario] + [
                cnpj for cnpj in lista_cnpjs_admin
                if normalizar_cnpj(cnpj) != normalizar_cnpj(cnpj_prioritario)
            ]
        print(f"[RASTREIO] CNPJs admin: {lista_cnpjs_admin}")

    for codigo in codigos:
        codigo_limpo = str(codigo).strip().upper()
        if not codigo_limpo:
            continue

        resultado = buscar_rastreio_logado(
            codigo_limpo,
            is_admin,
            cnpj_cliente,
            lista_cnpjs_admin
        )

        if resultado:
            resultados.append(resultado)
            print(f"[RASTREIO] Código {codigo_limpo}: retornado com sucesso")
        else:
            print(f"[RASTREIO] Código {codigo_limpo}: sem resultado nem API nem banco")

    for item in resultados:
        registrar_consulta_rastreio(
            session["usuario_id"],
            item.get("codigo"),
            item.get("statusBadge"),
            "consulta"
        )

    return jsonify({
        "success": True,
        "resultados": resultados
    })


# ============================================================
# ADMINISTRADOR - IMPORTAÇÃO DE RASTREIOS
# ============================================================

@app.route("/api/admin/importar-rastreios", methods=["POST"])
def importar_rastreios_admin():
    if "usuario_id" not in session:
        return jsonify({
            "success": False,
            "message": "Não autenticado."
        }), 401

    if session.get("is_admin") != 1:
        return jsonify({
            "success": False,
            "message": "Acesso negado."
        }), 403

    arquivo = request.files.get("arquivo")

    if not arquivo or not arquivo.filename:
        return jsonify({
            "success": False,
            "message": "Nenhum arquivo enviado."
        }), 400

    extensao = os.path.splitext(arquivo.filename)[1].lower()
    if extensao not in [".csv", ".xlsx", ".xls"]:
        return jsonify({
            "success": False,
            "message": "Formato inválido. Envie CSV ou Excel."
        }), 400

    caminho_temp = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=extensao) as temp:
            arquivo.save(temp.name)
            caminho_temp = temp.name

        inseridos, atualizados, ignorados = importar_rastreios(caminho_temp)

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO log_updates (
                usuario_id,
                nome_usuario,
                tipo_importacao,
                nome_arquivo,
                inseridos,
                atualizados,
                ignorados,
                data_hora
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["usuario_id"],
            session["usuario_nome"],
            "rastreios",
            arquivo.filename,
            inseridos,
            atualizados,
            ignorados,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Importação realizada com sucesso.",
            "inseridos": inseridos,
            "atualizados": atualizados,
            "ignorados": ignorados
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro na importação: {str(e)}"
        }), 500

    finally:
        if caminho_temp and os.path.exists(caminho_temp):
            os.remove(caminho_temp)


# ============================================================
# ADMIN - LOGS DE UPDATES
# ============================================================

@app.route("/api/admin/log-updates", methods=["GET"])
def listar_log_updates():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, nome_usuario, tipo_importacao, nome_arquivo,
               inseridos, atualizados, ignorados, data_hora
        FROM log_updates
        ORDER BY id DESC
        LIMIT 50
    """).fetchall()
    conn.close()

    logs = [{
        "id": row["id"],
        "nome_usuario": row["nome_usuario"],
        "tipo_importacao": row["tipo_importacao"],
        "nome_arquivo": row["nome_arquivo"],
        "inseridos": row["inseridos"],
        "atualizados": row["atualizados"],
        "ignorados": row["ignorados"],
        "data_hora": row["data_hora"]
    } for row in rows]

    return jsonify({
        "success": True,
        "logs": logs
    })


# ============================================================
# ADMIN - LOGS DE ACESSO
# ============================================================

@app.route("/api/admin/log-acessos", methods=["GET"])
def listar_log_acessos():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, usuario_id, email_informado, sucesso, ip, data_hora
        FROM log_acessos
        ORDER BY id DESC
        LIMIT 100
    """).fetchall()
    conn.close()

    logs = [{
        "id": row["id"],
        "usuario_id": row["usuario_id"],
        "email_informado": row["email_informado"],
        "sucesso": row["sucesso"],
        "ip": row["ip"],
        "data_hora": row["data_hora"]
    } for row in rows]

    return jsonify({
        "success": True,
        "logs": logs
    })


# ============================================================
# ADMIN - DASHBOARD
# ============================================================

@app.route("/api/admin/dashboard", methods=["GET"])
def dashboard_admin():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado"}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado"}), 403

    conn = get_db_connection()

    total_rastreios = conn.execute("SELECT COUNT(*) FROM rastreios").fetchone()[0]
    total_usuarios = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    total_entregas = total_rastreios
    entregas_finalizadas = conn.execute("""
        SELECT COUNT(*)
        FROM rastreios
        WHERE UPPER(COALESCE(status_badge, '')) = 'ENTREGUE'
    """).fetchone()[0]
    entregas_pendentes = total_entregas - entregas_finalizadas
    logins_hoje = conn.execute("""
        SELECT COUNT(*) FROM log_acessos
        WHERE sucesso = 1
        AND date(data_hora) = date('now')
    """).fetchone()[0]
    ultima_importacao = conn.execute("""
        SELECT data_hora
        FROM log_updates
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()
    ultima_entrega = conn.execute("""
        SELECT codigo, status_badge, previsao
        FROM rastreios
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    conn.close()

    return jsonify({
        "success": True,
        "dashboard": {
            "total_rastreios": total_rastreios,
            "total_usuarios": total_usuarios,
            "total_entregas": total_entregas,
            "entregas_finalizadas": entregas_finalizadas,
            "entregas_pendentes": entregas_pendentes,
            "logins_hoje": logins_hoje,
            "ultima_importacao": ultima_importacao["data_hora"] if ultima_importacao else "Nunca",
            "ultima_entrega": {
                "codigo": ultima_entrega["codigo"],
                "status_badge": ultima_entrega["status_badge"],
                "previsao": ultima_entrega["previsao"]
            } if ultima_entrega else None
        }
    })


@app.route("/api/client/dashboard", methods=["GET"])
def dashboard_cliente():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "NÃ£o autenticado"}), 401

    usuario_id = session["usuario_id"]
    conn = get_db_connection()

    consultas_hoje = conn.execute("""
        SELECT COUNT(*) AS total
        FROM consulta_rastreio_log
        WHERE usuario_id = ?
          AND date(data_hora) = date('now')
    """, (usuario_id,)).fetchone()["total"]

    ultimo_rastreio = conn.execute("""
        SELECT codigo, status_badge, data_hora
        FROM consulta_rastreio_log
        WHERE usuario_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (usuario_id,)).fetchone()

    cnpj_cliente = session.get("cnpj_cliente")
    total_documentos = 0
    if cnpj_cliente:
        total_documentos = conn.execute("""
            SELECT COUNT(*) AS total
            FROM rastreios
            WHERE cnpj_cliente = ?
        """, (cnpj_cliente,)).fetchone()["total"]

    total_custodias_abertas = conn.execute("""
        SELECT COUNT(*) AS total
        FROM solicitacoes_custodia
        WHERE usuario_id = ?
          AND status = 'ABERTO'
    """, (usuario_id,)).fetchone()["total"]
    conn.close()

    return jsonify({
        "success": True,
        "dashboard": {
            "consultas_hoje": consultas_hoje,
            "documentos_disponiveis": total_documentos,
            "custodias_abertas": total_custodias_abertas,
            "ultimo_rastreio": {
                "codigo": ultimo_rastreio["codigo"],
                "status_badge": ultimo_rastreio["status_badge"],
                "data_hora": ultimo_rastreio["data_hora"]
            } if ultimo_rastreio else None
        }
    })


@app.route("/api/client/entregas-dashboard", methods=["GET"])
def dashboard_entregas_cliente():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Nao autenticado"}), 401

    usuario_id = session["usuario_id"]
    cnpj_cliente = session.get("cnpj_cliente")
    conn = get_db_connection()
    data_hoje = datetime.now().strftime("%Y-%m-%d")

    total_entregas_hoje = 0
    entregas_finalizadas = 0
    entregas_em_aberto = 0
    ultima_entrega = None

    if cnpj_cliente:
        total_entregas_hoje = conn.execute("""
            SELECT COUNT(*) AS total
            FROM rastreios
            WHERE cnpj_cliente = ?
              AND data_cadastro_portal IS NOT NULL
              AND date(data_cadastro_portal) >= ?
        """, (cnpj_cliente, data_hoje)).fetchone()["total"]

        entregas_finalizadas = conn.execute("""
            SELECT COUNT(*) AS total
            FROM rastreios
            WHERE cnpj_cliente = ?
              AND data_cadastro_portal IS NOT NULL
              AND date(data_cadastro_portal) >= ?
              AND UPPER(COALESCE(status_badge, '')) = 'ENTREGUE'
        """, (cnpj_cliente, data_hoje)).fetchone()["total"]

        entregas_em_aberto = conn.execute("""
            SELECT COUNT(*) AS total
            FROM rastreios
            WHERE cnpj_cliente = ?
              AND data_cadastro_portal IS NOT NULL
              AND date(data_cadastro_portal) >= ?
              AND UPPER(COALESCE(status_badge, '')) <> 'ENTREGUE'
        """, (cnpj_cliente, data_hoje)).fetchone()["total"]

        ultima_entrega = conn.execute("""
            SELECT codigo, status_badge, previsao, data_cadastro_portal
            FROM rastreios
            WHERE cnpj_cliente = ?
              AND data_cadastro_portal IS NOT NULL
              AND date(data_cadastro_portal) >= ?
            ORDER BY data_cadastro_portal DESC, id DESC
            LIMIT 1
        """, (cnpj_cliente, data_hoje)).fetchone()

    total_custodias_abertas = conn.execute("""
        SELECT COUNT(*) AS total
        FROM solicitacoes_custodia
        WHERE usuario_id = ?
          AND status = 'ABERTO'
    """, (usuario_id,)).fetchone()["total"]
    conn.close()

    return jsonify({
        "success": True,
        "dashboard": {
            "entregas_hoje": total_entregas_hoje,
            "entregas_finalizadas": entregas_finalizadas,
            "entregas_em_aberto": entregas_em_aberto,
            "custodias_abertas": total_custodias_abertas,
            "ultima_entrega": {
                "codigo": ultima_entrega["codigo"],
                "status_badge": ultima_entrega["status_badge"],
                "previsao": ultima_entrega["previsao"],
                "data_cadastro_portal": ultima_entrega["data_cadastro_portal"]
            } if ultima_entrega else None
        }
    })


# ============================================================
# ADMIN - USUÁRIOS
# ============================================================

@app.route("/api/admin/usuarios", methods=["GET"])
def listar_usuarios_admin():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, nome, email, is_admin, cnpj_cliente, aprovado
        FROM usuarios
        ORDER BY nome ASC
    """).fetchall()
    conn.close()

    usuarios = [{
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "is_admin": row["is_admin"],
        "cnpj_cliente": row["cnpj_cliente"],
        "aprovado": row["aprovado"]
    } for row in rows]

    return jsonify({
        "success": True,
        "usuarios": usuarios
    })


@app.route("/api/admin/cnpjs", methods=["GET"])
def listar_cnpjs_admin():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "NÃ£o autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    return jsonify({
        "success": True,
        "cnpjs": listar_cnpjs_disponiveis()
    })


@app.route("/api/admin/database-overview", methods=["GET"])
def database_overview_admin():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "NÃ£o autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    cnpj = str(request.args.get("cnpj", "")).strip()
    status = str(request.args.get("status", "")).strip()

    conn = get_db_connection()
    query = """
        SELECT codigo, destinatario, previsao, ultimo_status, status_badge, cnpj_cliente, ultima_atualizacao_api
        FROM rastreios
        WHERE 1 = 1
    """
    params = []

    if cnpj:
        query += " AND cnpj_cliente = ?"
        params.append(cnpj)

    if status:
        query += " AND status_badge = ?"
        params.append(status)

    query += " ORDER BY id DESC LIMIT 50"

    rastreios = conn.execute(query, tuple(params)).fetchall()
    usuarios = conn.execute("""
        SELECT id, nome, email, cnpj_cliente, aprovado, is_admin
        FROM usuarios
        ORDER BY id DESC
        LIMIT 20
    """).fetchall()
    resumo_status = conn.execute("""
        SELECT COALESCE(status_badge, 'SEM STATUS') AS status_badge, COUNT(*) AS total
        FROM rastreios
        GROUP BY COALESCE(status_badge, 'SEM STATUS')
        ORDER BY total DESC
        LIMIT 8
    """).fetchall()
    conn.close()

    return jsonify({
        "success": True,
        "overview": {
            "rastreios": [dict(row) for row in rastreios],
            "usuarios": [dict(row) for row in usuarios],
            "status": [dict(row) for row in resumo_status]
        }
    })


@app.route("/api/admin/modelos-db/meta", methods=["GET"])
def meta_modelos_db_admin():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    try:
        return jsonify({
            "success": True,
            "meta": obter_meta_modelos_db()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao carregar metadados: {str(e)}"
        }), 500


@app.route("/api/admin/modelos-db", methods=["GET"])
def consultar_modelos_db_admin():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    colunas = [
        item.strip()
        for item in str(request.args.get("colunas", "")).split(",")
        if item.strip()
    ]
    filtros = {
        "busca": request.args.get("busca", ""),
        "modelo": request.args.get("modelo", ""),
        "uf": request.args.get("uf", ""),
        "cidade": request.args.get("cidade", ""),
        "nome_arquivo": request.args.get("nome_arquivo", ""),
    }
    limite = request.args.get("limite", "100")

    try:
        resultado = consultar_modelos_db(filtros, colunas=colunas, limite=limite)
        return jsonify({
            "success": True,
            "resultado": resultado
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro na consulta: {str(e)}"
        }), 500


@app.route("/api/admin/modelos-db/<int:registro_id>", methods=["GET"])
def detalhes_modelos_db_admin(registro_id):
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    try:
        detalhes = obter_detalhes_modelo_registro(registro_id)
        if not detalhes:
            return jsonify({
                "success": False,
                "message": "Registro não encontrado."
            }), 404

        return jsonify({
            "success": True,
            "detalhes": detalhes
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao carregar detalhes: {str(e)}"
        }), 500


@app.route("/api/admin/modelos-db/bipar", methods=["POST"])
def bipar_modelos_db_admin():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    data = request.get_json() or {}
    codigo = str(data.get("codigo", "")).strip()
    colunas = data.get("colunas") or []

    try:
        registro = buscar_modelo_por_codigo(codigo, colunas=colunas)
        if not registro:
            return jsonify({
                "success": False,
                "message": "Cartão/AR não encontrado na base."
            }), 404

        return jsonify({
            "success": True,
            "registro": registro
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro na bipagem: {str(e)}"
        }), 500


@app.route("/api/admin/modelos-db/exportar", methods=["GET"])
def exportar_modelos_db_admin():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    colunas = [
        item.strip()
        for item in str(request.args.get("colunas", "")).split(",")
        if item.strip()
    ]
    filtros = {
        "busca": request.args.get("busca", ""),
        "modelo": request.args.get("modelo", ""),
        "uf": request.args.get("uf", ""),
        "cidade": request.args.get("cidade", ""),
        "nome_arquivo": request.args.get("nome_arquivo", ""),
    }
    limite = request.args.get("limite", "1000")

    try:
        resultado = consultar_modelos_db(filtros, colunas=colunas, limite=limite)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao preparar exportação: {str(e)}"
        }), 500

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(resultado["colunas"])

    for registro in resultado["registros"]:
        writer.writerow([registro.get(coluna, "") for coluna in resultado["colunas"]])

    csv_content = "\ufeff" + output.getvalue()
    output.close()

    return Response(
        csv_content,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=modelos_enderecos.csv"}
    )


@app.route("/api/admin/usuarios/<int:usuario_id>/aprovar", methods=["POST"])
def aprovar_usuario_admin(usuario_id):
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    data = request.get_json() or {}
    cnpj_cliente = str(data.get("cnpj_cliente", "")).strip()

    if not cnpj_cliente:
        return jsonify({
            "success": False,
            "message": "Informe o CNPJ do cliente."
        }), 400

    conn = get_db_connection()

    usuario = conn.execute("""
        SELECT id, email
        FROM usuarios
        WHERE id = ?
    """, (usuario_id,)).fetchone()

    if not usuario:
        conn.close()
        return jsonify({
            "success": False,
            "message": "Usuário não encontrado."
        }), 404

    conn.execute("""
        UPDATE usuarios
        SET aprovado = 1,
            cnpj_cliente = ?
        WHERE id = ?
    """, (cnpj_cliente, usuario_id))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Usuário aprovado com sucesso."
    })


@app.route("/api/admin/usuarios/<int:usuario_id>/bloquear", methods=["POST"])
def bloquear_usuario_admin(usuario_id):
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    conn = get_db_connection()

    usuario = conn.execute("""
        SELECT id
        FROM usuarios
        WHERE id = ?
    """, (usuario_id,)).fetchone()

    if not usuario:
        conn.close()
        return jsonify({
            "success": False,
            "message": "Usuário não encontrado."
        }), 404

    conn.execute("""
        UPDATE usuarios
        SET aprovado = 0
        WHERE id = ?
    """, (usuario_id,))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Usuário bloqueado com sucesso."
    })


@app.route("/api/admin/custodias", methods=["GET"])
def listar_custodias_admin():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    status = str(request.args.get("status", "")).strip().upper()

    conn = get_db_connection()

    if status:
        rows = conn.execute("""
            SELECT sc.id, sc.codigo_ar, sc.tipo_solicitacao, sc.nome, sc.endereco,
                   sc.numero, sc.complemento, sc.bairro, sc.cidade, sc.cep, sc.uf,
                   sc.ponto_referencia, sc.usuario_id, sc.status, sc.data_criacao,
                   u.nome AS nome_usuario, u.email AS email_usuario
            FROM solicitacoes_custodia sc
            LEFT JOIN usuarios u ON u.id = sc.usuario_id
            WHERE sc.status = ?
            ORDER BY sc.id DESC
        """, (status,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT sc.id, sc.codigo_ar, sc.tipo_solicitacao, sc.nome, sc.endereco,
                   sc.numero, sc.complemento, sc.bairro, sc.cidade, sc.cep, sc.uf,
                   sc.ponto_referencia, sc.usuario_id, sc.status, sc.data_criacao,
                   u.nome AS nome_usuario, u.email AS email_usuario
            FROM solicitacoes_custodia sc
            LEFT JOIN usuarios u ON u.id = sc.usuario_id
            ORDER BY sc.id DESC
        """).fetchall()

    conn.close()

    custodias = [{
        "id": row["id"],
        "codigo_ar": row["codigo_ar"],
        "tipo_solicitacao": row["tipo_solicitacao"],
        "nome": row["nome"],
        "endereco": row["endereco"],
        "numero": row["numero"],
        "complemento": row["complemento"],
        "bairro": row["bairro"],
        "cidade": row["cidade"],
        "cep": row["cep"],
        "uf": row["uf"],
        "ponto_referencia": row["ponto_referencia"],
        "status": row["status"],
        "data_criacao": row["data_criacao"],
        "nome_usuario": row["nome_usuario"],
        "email_usuario": row["email_usuario"]
    } for row in rows]

    return jsonify({"success": True, "custodias": custodias})


@app.route("/api/admin/custodias/<int:custodia_id>/concluir", methods=["POST"])
def concluir_custodia_admin(custodia_id):
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    conn = get_db_connection()

    row = conn.execute("""
        SELECT id, status
        FROM solicitacoes_custodia
        WHERE id = ?
    """, (custodia_id,)).fetchone()

    if not row:
        conn.close()
        return jsonify({"success": False, "message": "Solicitação não encontrada."}), 404

    conn.execute("""
        UPDATE solicitacoes_custodia
        SET status = 'CONCLUIDO'
        WHERE id = ?
    """, (custodia_id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Solicitação concluída com sucesso."})


import csv
import io
from flask import Response


@app.route("/api/admin/custodias/exportar", methods=["GET"])
def exportar_custodias_admin():
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    status = str(request.args.get("status", "")).strip().upper()

    conn = get_db_connection()

    if status:
        rows = conn.execute("""
            SELECT sc.id, sc.codigo_ar, sc.tipo_solicitacao, sc.nome, sc.endereco,
                   sc.numero, sc.complemento, sc.bairro, sc.cidade, sc.cep, sc.uf,
                   sc.ponto_referencia, sc.status, sc.data_criacao,
                   u.nome AS nome_usuario, u.email AS email_usuario
            FROM solicitacoes_custodia sc
            LEFT JOIN usuarios u ON u.id = sc.usuario_id
            WHERE sc.status = ?
            ORDER BY sc.id DESC
        """, (status,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT sc.id, sc.codigo_ar, sc.tipo_solicitacao, sc.nome, sc.endereco,
                   sc.numero, sc.complemento, sc.bairro, sc.cidade, sc.cep, sc.uf,
                   sc.ponto_referencia, sc.status, sc.data_criacao,
                   u.nome AS nome_usuario, u.email AS email_usuario
            FROM solicitacoes_custodia sc
            LEFT JOIN usuarios u ON u.id = sc.usuario_id
            ORDER BY sc.id DESC
        """).fetchall()

    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "id", "codigo_ar", "tipo_solicitacao", "nome", "endereco", "numero",
        "complemento", "bairro", "cidade", "cep", "uf", "ponto_referencia",
        "status", "data_criacao", "nome_usuario", "email_usuario"
    ])

    for row in rows:
        writer.writerow([
            row["id"],
            row["codigo_ar"],
            row["tipo_solicitacao"],
            row["nome"],
            row["endereco"],
            row["numero"],
            row["complemento"],
            row["bairro"],
            row["cidade"],
            row["cep"],
            row["uf"],
            row["ponto_referencia"],
            row["status"],
            row["data_criacao"],
            row["nome_usuario"],
            row["email_usuario"],
        ])

    csv_content = "\ufeff" + output.getvalue()
    output.close()

    return Response(
        csv_content,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=custodias.csv"}
    )


@app.route("/api/admin/usuarios/<int:usuario_id>/definir-admin", methods=["POST"])
def definir_admin(usuario_id):
    if "usuario_id" not in session:
        return jsonify({"success": False, "message": "Não autenticado."}), 401

    if session.get("is_admin") != 1:
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    data = request.get_json() or {}
    is_admin = int(data.get("is_admin", 0))

    conn = get_db_connection()
    conn.execute(
        "UPDATE usuarios SET is_admin = ? WHERE id = ?",
        (is_admin, usuario_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ============================================================
# CUSTODIA - FUNÇÕES
# ============================================================

@app.route("/api/custodia/buscar", methods=["POST"])
def buscar_custodia():
    if "usuario_id" not in session:
        return jsonify({
            "success": False,
            "message": "Usuário não autenticado."
        }), 401

    data = request.get_json() or {}
    codigo = str(data.get("codigo", "")).strip().upper()

    if not codigo:
        return jsonify({
            "success": False,
            "message": "Informe um código de rastreio."
        }), 400

    conn = get_db_connection()
    row = conn.execute("""
        SELECT codigo, destinatario, status_badge, ultimo_status
        FROM rastreios
        WHERE codigo = ?
    """, (codigo,)).fetchone()
    conn.close()

    if not row:
        return jsonify({
            "success": False,
            "message": "AR não encontrada."
        }), 404

    def normalizar(texto):
        return (texto or "").upper().replace("Ó", "O").strip()

    status_badge = normalizar(row["status_badge"])
    ultimo_status = normalizar(row["ultimo_status"])

    if status_badge != "CUSTODIA" and "CUSTODIA" not in ultimo_status:
        return jsonify({
            "success": False,
            "message": "Esta AR não está em custódia."
        }), 400

    return jsonify({
        "success": True,
        "ar": {
            "codigo": row["codigo"],
            "destinatario": row["destinatario"] or "Buscando nome...",
            "statusBadge": row["status_badge"],
            "ultimoStatus": row["ultimo_status"]
        }
    })


@app.route("/api/custodia/solicitar", methods=["POST"])
def solicitar_custodia():
    if "usuario_id" not in session:
        return jsonify({
            "success": False,
            "message": "Usuário não autenticado."
        }), 401

    data = request.get_json() or {}

    codigo_ar = str(data.get("codigo_ar", "")).strip().upper()
    tipo_solicitacao = str(data.get("tipo_solicitacao", "")).strip()

    if not codigo_ar or tipo_solicitacao not in ["MESMO_ENDERECO", "NOVO_ENDERECO"]:
        return jsonify({
            "success": False,
            "message": "Dados inválidos."
        }), 400

    nome = str(data.get("nome", "")).strip()
    endereco = str(data.get("endereco", "")).strip()
    numero = str(data.get("numero", "")).strip()
    complemento = str(data.get("complemento", "")).strip()
    bairro = str(data.get("bairro", "")).strip()
    cidade = str(data.get("cidade", "")).strip()
    cep = str(data.get("cep", "")).strip()
    uf = str(data.get("uf", "")).strip()
    ponto_referencia = str(data.get("ponto_referencia", "")).strip()

    if tipo_solicitacao == "NOVO_ENDERECO":
        obrigatorios = [nome, endereco, numero, bairro, cidade, cep, uf]
        if not all(obrigatorios):
            return jsonify({
                "success": False,
                "message": "Preencha os campos obrigatórios do novo endereço."
            }), 400

    conn = get_db_connection()

    existente = conn.execute("""
        SELECT id
        FROM solicitacoes_custodia
        WHERE codigo_ar = ?
          AND status = 'ABERTO'
        LIMIT 1
    """, (codigo_ar,)).fetchone()

    if existente:
        conn.close()
        return jsonify({
            "success": False,
            "message": "Já existe uma solicitação em aberto para esta AR."
        }), 409

    conn.execute("""
        INSERT INTO solicitacoes_custodia (
            codigo_ar,
            tipo_solicitacao,
            nome,
            endereco,
            numero,
            complemento,
            bairro,
            cidade,
            cep,
            uf,
            ponto_referencia,
            usuario_id,
            status,
            data_criacao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        codigo_ar,
        tipo_solicitacao,
        nome,
        endereco,
        numero,
        complemento,
        bairro,
        cidade,
        cep,
        uf,
        ponto_referencia,
        session["usuario_id"],
        "ABERTO",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Solicitação enviada com sucesso."
    })


@app.route("/tracking/<codigo>")
def tracking_publico_codigo(codigo):
    codigo = str(codigo).strip().upper()
    return render_template("tracking_publico.html", codigo=codigo)



@app.route("/tracking/<cliente>/")
def tracking_publico_cliente_sem_codigo(cliente):
    return render_template("tracking_publico.html", codigo="")

@app.route("/tracking/<cliente>/<codigo>")
def tracking_publico_cliente(cliente, codigo):
    codigo = str(codigo).strip().upper()
    return render_template("tracking_publico.html", codigo=codigo)

@app.route("/tracking")
def tracking_publico():
    return render_template("tracking_publico.html", codigo="")


@app.route("/tracking/simplecompany")
@app.route("/tracking/simplecompany/<codigo>")
def tracking_publico_simplecompany(codigo=""):
    codigo = str(codigo).strip().upper()
    return render_template("tracking_simplecompany.html", codigo=codigo)


@app.route("/api/rastrear", methods=["POST"])
def api_rastrear_publico():
    data = request.get_json() or {}
    codigo = str(data.get("codigo", "")).strip().upper()
    cliente = _cliente_tracking_normalizado(data.get("cliente", ""))

    if not codigo or len(codigo) > 80 or not re.fullmatch(r"[A-Z0-9._/-]+", codigo):
        return jsonify({
            "ok": False,
            "error": "Código inválido."
        }), 400

    if _excedeu_limite_consulta_publica(_ip_consulta_publica()):
        response = jsonify({
            "ok": False,
            "error": "Muitas consultas. Aguarde um minuto e tente novamente."
        })
        response.headers["Retry-After"] = str(PUBLIC_TRACKING_RATE_WINDOW)
        return response, 429

    resultado = buscar_rastreio_publico(codigo, cliente)

    if not resultado:
        return jsonify({
            "ok": False,
            "error": "Código não encontrado."
        }), 404

    status_badge = str(resultado.get("statusBadge") or "").upper()

    status_key = converter_status_publico(status_badge)

    # Hotfix público exclusivo do CCXP: o TMS continua sendo a fonte da
    # ocorrência, mas nenhum estado de insucesso/reenvio vaza como devolução.
    if cliente == "ccxp":
        texto_origem = f"{status_badge} {resultado.get('ultimoStatus') or ''}"
        texto_normalizado = "".join(
            caractere for caractere in unicodedata.normalize("NFD", texto_origem)
            if unicodedata.category(caractere) != "Mn"
        ).lower()
        tem_reenvio = (
            "tratamento de pendencia" in texto_normalizado
            and "reentregar" in texto_normalizado
        )
        eh_insucesso = (
            tem_reenvio
            or status_badge in {"PENDENTE", "CUSTODIA", "DEVOLVIDO"}
            or status_key in {"devolucao", "devolvido"}
            or any(marcador in texto_normalizado for marcador in (
                "nao entregue",
                "entrega nao realizada",
                "insucesso",
                "devolucao",
                "devolvido",
            ))
        )

        if eh_insucesso:
            status_ccxp = "ccxp_tratado" if tem_reenvio else "ccxp_aguardando_tratativa"
            titulo_ccxp = (
                "Tratado"
                if tem_reenvio
                else "Aguardando tratativa para reenvio"
            )
            descricao_ccxp = (
                "Credencial terá uma nova tentativa."
                if tem_reenvio
                else ""
            )
            descricao_timeline_ccxp = (
                "Credencial terá uma nova tentativa."
                if tem_reenvio
                else "Aguardando tratativa para reenvio."
            )
            motivo_ccxp = ""
            if "cep incorreto" in texto_normalizado:
                motivo_ccxp = "Não entregue: CEP incorreto."
            elif "numero nao localizado" in texto_normalizado:
                motivo_ccxp = "Não entregue: número não localizado."
            historico_original = montar_historico_publico(resultado)
            data_ccxp = (
                str(historico_original[0].get("when") or "-")
                if historico_original
                else "-"
            )
            etapas_ccxp = []
            for etapa in montar_etapas_publicas(status_key, resultado):
                if etapa.get("key") in {"atencao", "devolucao", "devolvido", "entregue"}:
                    continue
                if etapa.get("key") == "em_rota_entrega" and not (
                    str(etapa.get("date") or "").strip()
                    or str(etapa.get("time") or "").strip()
                ):
                    continue
                etapa_segura = dict(etapa)
                etapa_segura["attention"] = False
                if etapa_segura.get("key") == "em_rota_entrega":
                    etapa_segura["done"] = True
                etapas_ccxp.append(etapa_segura)
            etapas_ccxp.append({
                "key": "ccxp_tratativa",
                "title": "Reenvio",
                "desc": descricao_timeline_ccxp,
                "date": data_ccxp,
                "time": "",
                "icon": "➜",
                "done": False,
                "attention": False,
            })

            historico_ccxp = [{
                "title": titulo_ccxp,
                "desc": descricao_ccxp,
                "when": data_ccxp,
                "theme": "",
            }]
            if motivo_ccxp:
                historico_ccxp.append({
                    "title": "Ocorrência na entrega",
                    "desc": motivo_ccxp,
                    "when": data_ccxp,
                    "theme": "",
                })

            resposta_ccxp = {
                "ok": True,
                "cliente": resultado.get("destinatario") or "-",
                "status": status_ccxp,
                "status_label": titulo_ccxp,
                "stages": etapas_ccxp,
                "history": historico_ccxp,
                "rastreioTerceiro": resultado.get("rastreioTerceiro"),
            }
            if tem_reenvio:
                resposta_ccxp["kind"] = "reenvio"
            return jsonify(resposta_ccxp)

    return jsonify({
        "ok": True,
        "cliente": resultado.get("destinatario") or "-",
        "status": status_key,
        "status_label": resultado.get("statusBadge") or "-",
        "stages": montar_etapas_publicas(status_key, resultado),
        "history": montar_historico_publico(resultado),
        "rastreioTerceiro": resultado.get("rastreioTerceiro")
    })


@app.route("/api/rastrear/simplecompany", methods=["POST"])
def api_rastrear_simplecompany():
    data = request.get_json() or {}
    codigo = str(data.get("codigo", "")).strip().upper()
    nome_informado = str(data.get("nome", "")).strip()
    cnpj_simplecompany = "65949995000187"

    if not codigo or len(codigo) > 80 or not re.fullmatch(r"[A-Z0-9._/-]+", codigo):
        return jsonify({"ok": False, "error": "Informe um número de pedido válido."}), 400

    nome_cadastrado = _buscar_nome_pedido_simplecompany(codigo)
    if not nome_cadastrado or not nome_informado or _normalizar_nome_validacao(nome_informado) != _normalizar_nome_validacao(nome_cadastrado):
        return jsonify({"ok": False, "error": "O nome informado não confere com o pedido."}), 403

    if _excedeu_limite_consulta_publica(_ip_consulta_publica()):
        response = jsonify({
            "ok": False,
            "error": "Muitas consultas. Aguarde um minuto e tente novamente."
        })
        response.headers["Retry-After"] = str(PUBLIC_TRACKING_RATE_WINDOW)
        return response, 429

    # Simple Company consulta exclusivamente a listaPedidos do TMS.
    resultado = buscar_rastreio_na_api(codigo, cnpj_simplecompany, somente_pedido=True)
    if not resultado:
        return jsonify({"ok": False, "error": "Pedido não encontrado."}), 404

    status_badge = str(resultado.get("statusBadge") or "").upper()
    status_key = converter_status_publico(status_badge)
    return jsonify({
        "ok": True,
        "pedido": codigo,
        "status": status_key,
        "status_label": resultado.get("statusBadge") or "-",
        "stages": montar_etapas_publicas(status_key, resultado),
        "history": montar_historico_publico(resultado),
    })


@app.route("/api/rastrear/simplecompany/dica", methods=["GET"])
def api_dica_simplecompany():
    codigo = str(request.args.get("codigo", "")).strip().upper()
    if not codigo or len(codigo) > 80 or not re.fullmatch(r"[A-Z0-9._/-]+", codigo):
        return jsonify({"ok": False, "error": "Pedido inválido."}), 400
    nome = _buscar_nome_pedido_simplecompany(codigo)
    if not nome:
        return jsonify({"ok": False, "error": "Pedido não encontrado."}), 404
    return jsonify({"ok": True, "nome_mascarado": _nome_mascarado_simplecompany(nome)})


def converter_status_publico(status_badge):
    status = (status_badge or "").strip().upper()

    if status == "ENTREGUE":
        return "entregue"

    if status == "EM ROTA":
        return "em_rota_entrega"

    if status in ["EM SEPARAÇÃO", "POSTADO", "ARQUIVO RECEBIDO", "SOLICITAÇÃO REALIZADA", "OBJETO POSTADO", "PRE CADASTRADO"]:
        return "preparacao_transporte"

    if status in ["RECEBIDO", "LIBERADO PARA ENTREGA", "PROCESSADO", "RECEBIDO PARCIAL", "TRANSFERÊNCIA ENTREGA RECEBIDA"]:
        return "chegada_franquia"

    if status in ["EM TRANSFERÊNCIA", "PENDENTE", "EM TRANSFERÊNCIA ENTREGA", "REDESPACHADO", "AGENDADO"]:
        return "transferencia_franquia"

    if status in ["REAGENDADO", "REENTREGAR", "CUSTODIA", "CANCELADA"]:
        return "atencao"

    if status == "DEVOLVIDO":
        return "devolvido"
    if status in ["EM DEVOLUÇÃO", "DEVOLUÇÃO EM ROTA", "DEVOLUÇÃO COM PENDÊNCIA"]:
        return "devolucao"

    if status in ["CANCELADO", "SINISTRO", "INCINERADO"]:
        return "atencao"

    return "preparacao_transporte"


def montar_etapas_publicas(status_key, resultado):
    stages = [
        {
            "key": "aguardando_postagem",
            "title": "Pedido recebido",
            "desc": "Solicitação recebida pela operação.",
            "icon": "⏳",
            "date": "",
            "time": "",
            "done": True
        },
        {
            "key": "preparacao_transporte",
            "title": "Preparação",
            "desc": "Pedido em preparação para transporte.",
            "icon": "📦",
            "date": "",
            "time": "",
            "done": status_key in [
                "preparacao_transporte",
                "transferencia_franquia",
                "chegada_franquia",
                "em_rota_entrega",
                "atencao",
                "devolucao",
                "devolvido",
                "entregue"
            ]
        },
        {
            "key": "transferencia_franquia",
            "title": "Transferência",
            "desc": "Pedido em transferência entre unidades.",
            "icon": "🚚",
            "date": "",
            "time": "",
            "done": status_key in [
                "transferencia_franquia",
                "chegada_franquia",
                "em_rota_entrega",
                "atencao",
                "devolucao",
                "devolvido",
                "entregue"
            ]
        },
        {
            "key": "chegada_franquia",
            "title": "Unidade final",
            "desc": "Pedido recebido na unidade responsável.",
            "icon": "📦",
            "date": "",
            "time": "",
            "done": status_key in [
                "chegada_franquia",
                "em_rota_entrega",
                "atencao",
                "devolucao",
                "devolvido",
                "entregue"
            ]
        },
        {
            "key": "em_rota_entrega",
            "title": "Em rota",
            "desc": "Pedido em rota para entrega.",
            "icon": "🚚",
            "date": "",
            "time": "",
            "done": status_key in ["em_rota_entrega", "entregue", "devolucao", "devolvido"]
        },
        {
            "key": "devolucao",
            "title": "Em devolução",
            "desc": "O objeto está sendo devolvido ao remetente.",
            "icon": "\U000021a9",
            "date": "",
            "time": "",
            "done": status_key in ["devolucao", "devolvido"],
        },
        {
            "key": "devolvido",
            "title": "Devolvido",
            "desc": "Objeto devolvido ao remetente.",
            "icon": "✅",
            "date": "",
            "time": "",
            "done": status_key == "devolvido"
        },
        {
            "key": "entregue",
            "title": "Entregue",
            "desc": "Previsão para entrega.",
            "icon": "🏁",
            "date": resultado.get("previsao") or "",
            "time": "",
            "done": status_key == "entregue"
        },
    ]

    # Preenche a data real de cada etapa. Prioridade: ocorrencia persistida;
    # senao, uma data ja conhecida na linha do rastreio. Etapa sem data fica
    # vazia (o front trata) — nunca se inventa data.
    datas = dict(resultado.get("datasEtapas") or {})
    for chave, data_etapa in montar_datas_etapas_ocorrencias(resultado.get("ocorrencias")).items():
        datas.setdefault(chave, data_etapa)

    for stage in stages:
        chave = stage["key"]
        data_etapa = datas.get(chave)

        if not data_etapa:
            if chave == "aguardando_postagem":
                data_etapa = (
                    _split_data_etapa(resultado.get("dataCadastroPortal"))
                    or _split_data_etapa(resultado.get("dataPostagemRaw"))
                    or _split_data_etapa(resultado.get("dataPostagem"))
                )
            elif chave == "preparacao_transporte":
                data_etapa = (
                    _split_data_etapa(resultado.get("dataPostagemRaw"))
                    or _split_data_etapa(resultado.get("dataPostagem"))
                )

            # Etapa do status atual sem ocorrencia persistida: usa a data da
            # ultima ocorrencia (data_baixa), que ja esta no banco. Cobre
            # pedidos antigos que o coletor nao reprocessa.
            if not data_etapa and chave == status_key:
                data_etapa = (
                    _split_data_etapa(resultado.get("dataBaixaRaw"))
                    or _split_data_etapa(resultado.get("dataBaixa"))
                )

        if data_etapa:
            stage["date"] = data_etapa["date"]
            stage["time"] = data_etapa["time"]

    if status_key == "atencao":
        for stage in stages:
            if stage["key"] == "em_rota_entrega":
                stage["attention"] = True

    return stages


def montar_historico_publico(resultado):
    historico = []

    if resultado.get("observacaoVinculo"):
        historico.append({
            "title": "Consulta vinculada",
            "desc": resultado.get("observacaoVinculo"),
            "when": "-",
            "theme": ""
        })

    historico.append({
        "title": resultado.get("statusBadge") or "Status atualizado",
        "desc": resultado.get("ultimoStatus") or "Atualização registrada no sistema.",
        "when": resultado.get("dataBaixa") or resultado.get("previsao") or "-",
        "theme": "success" if resultado.get("statusBadge") == "ENTREGUE" else ""
    })

    return historico


garantir_tabelas_app()


if __name__ == "__main__":
    app.run(debug=True)
