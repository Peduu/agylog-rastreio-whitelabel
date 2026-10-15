"""Prazo de entrega por faixa de CEP (Pedro + senior do TI, 15/10/2026).

A API do TMS nao traz prazo nem destino. O prazo sai de dado real:
- CEP do destinatario: banco do sistema de subir arquivos (envios_modelos.db, tabela registros_modelo), que o
  portal so LE (nunca grava) e que recebe o CEP sozinho a cada arquivo novo;
- tabela oficial de prazo por faixa de CEP, importada no admin: a abrangencia do TMS como vem (CEP Inicial, CEP Final,
  Prazo Entrega, Sigla do Servico) ou so cep_inicial;cep_final;dias. Vale para todos os clientes. O servico do pedido nao
  e conhecido, entao o prazo so vale onde TODOS os servicos da tabela cobrem o CEP com o MESMO prazo (senao, nada);
- dias uteis pulam sabado, domingo e feriados nacionais (o 632 confere: cadastro 24/09 + 8 uteis = 06/10, igual ao TMS);
- data de cadastro no TMS: ocorrencia "1" (Criacao da solicitacao).

Regras que nao podem regredir: nada inventado (sem CEP ou sem faixa = sem prazo); o cliente so ve prazo enquanto o pedido
esta a caminho e nunca prazo vencido / "em atraso"; liga e desliga pelo admin (comeca desligado ate conferir com o TMS).
"""
import re
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone

BRASILIA = timezone(timedelta(hours=-3))
A_CAMINHO = {"preparacao_transporte", "transferencia_franquia", "chegada_franquia", "em_rota_entrega"}
TABELAS_MODELOS = ("registros_modelo", "registros_modelo_legado")
# Conferido com o relatorio de entregas do TMS (21.071 pedidos, 15/10/2026): nestes CEPs o "Prazo Atual" do TMS nao segue a
# tabela de abrangencia (DF: o TMS grava prazo = dia do cadastro; SP 04xxx: metade usa o prazo de ultima milha). Sem prazo
# aqui para nunca mostrar data diferente da do TMS.
SEM_PRAZO_CONFIAVEL = (
    ("70000000", "72799999"), ("73000000", "73699999"),   # Distrito Federal
    ("04000000", "04999999"),                             # Sao Paulo, zona sul (04xxx)
)
_CACHE_CEP = {}            # codigo -> (cep, instante); o mesmo pedido e consultado de 30 em 30 s pela pagina aberta
_CACHE_SEGUNDOS = 600


def normalizar_cep(valor):
    """8 digitos ou "". Aceita 7 digitos (Excel come o zero da frente: 1310100 -> 01310100) e numero com ".0"
    (coluna REAL ou export do pandas: 1310100.0), sem nunca juntar as casas decimais ao CEP."""
    if isinstance(valor, float):
        valor = int(valor) if valor.is_integer() else ""
    texto = re.sub(r"\.0+$", "", str(valor or "").strip())
    d = re.sub(r"\D", "", texto)
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
            servico TEXT NOT NULL DEFAULT '',
            criado_em TEXT NOT NULL
        )
    """)
    if "servico" not in {r[1] for r in conn.execute("PRAGMA table_info(prazos_cep)").fetchall()}:
        conn.execute("ALTER TABLE prazos_cep ADD COLUMN servico TEXT NOT NULL DEFAULT ''")
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
    """Troca a tabela inteira (e a tabela oficial; nao mistura com a anterior). faixas = [(cep_ini, cep_fim, dias[, servico])]."""
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("DELETE FROM prazos_cep")
    conn.executemany("INSERT INTO prazos_cep (cep_inicial, cep_final, dias, servico, criado_em) VALUES (?, ?, ?, ?, ?)",
                     [(f[0], f[1], f[2], (f[3] if len(f) > 3 else "") or "", agora) for f in faixas])


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
        dias_txt = pegar(row, "dias", "prazo", "prazo_dias", "dias_prazo", "prazo_(dias)", "prazo_entrega")   # TMS: "Prazo Entrega"
        servico = pegar(row, "sigla_do_serviço", "sigla_do_servico", "servico", "serviço").upper()
        try:
            dias = int(float(dias_txt.replace(",", ".")))
        except ValueError:
            dias = -1
        if not ini or not fim or ini > fim or dias < 0 or dias > 120:
            ignoradas += 1
            continue
        faixas.append((ini, fim, dias, servico))
    return faixas, ignoradas


def dias_para_cep(conn, cep):
    """Dias para o CEP ou None. Em cada servico vale a faixa mais estreita que contem o CEP; o prazo so existe se TODOS
    os servicos da tabela cobrem o CEP e dao o MESMO prazo (o servico do pedido nao e conhecido: nada de chute)."""
    cep = normalizar_cep(cep)
    if not cep or any(a <= cep <= b for a, b in SEM_PRAZO_CONFIAVEL):
        return None
    servicos = {r[0] for r in conn.execute("SELECT DISTINCT servico FROM prazos_cep").fetchall()}
    por_servico = {}
    for servico, dias in conn.execute("""
        SELECT servico, dias FROM prazos_cep
        WHERE cep_inicial <= ? AND cep_final >= ?
        ORDER BY CAST(cep_final AS INTEGER) - CAST(cep_inicial AS INTEGER) ASC, id ASC
    """, (cep, cep)).fetchall():
        por_servico.setdefault(servico, int(dias))
    if not por_servico or set(por_servico) != servicos or len(set(por_servico.values())) != 1:
        return None
    return next(iter(por_servico.values()))


def _pascoa(ano):
    """Domingo de Pascoa (algoritmo de Meeus/Butcher)."""
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(ano, mes, dia).date()


def feriados_nacionais(ano):
    """Feriados nacionais (lei): 1/1, Sexta-feira Santa, 21/4, 1/5, 7/9, 12/10, 2/11, 15/11, 20/11, 25/12."""
    fixos = [(1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (11, 20), (12, 25)]
    return {datetime(ano, m, d).date() for m, d in fixos} | {_pascoa(ano) - timedelta(days=2)}


def base_da_contagem(cadastro):
    """Como o TMS: cadastro no sabado ou domingo conta a partir da segunda-feira (mesmo se a segunda for feriado)."""
    if cadastro and cadastro.weekday() >= 5:
        return cadastro + timedelta(days=7 - cadastro.weekday())
    return cadastro


def somar_dias(base, dias, uteis=False):
    """Data base + dias corridos, ou + dias uteis (pula sabado, domingo e feriados nacionais)."""
    if not uteis:
        return base + timedelta(days=dias)
    d, faltam = base, dias
    while faltam > 0:
        d += timedelta(days=1)
        if d.weekday() < 5 and d not in feriados_nacionais(d.year):
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
    """Data da ocorrencia "1" (Criacao da solicitacao) no TMS. Sem ela: None (nada de outra data no lugar)."""
    cadastro = next((o for o in (ocorrencias or []) if str(o.get("codigoOcorrencia", "")).strip() == "1"
                     and _data(o.get("dtOcorrencia"))), None)
    return _data(cadastro["dtOcorrencia"]).date() if cadastro else None


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
        conn = sqlite3.connect(Path(caminho_db).resolve().as_uri() + "?mode=ro", uri=True)
        try:
            for tabela in TABELAS_MODELOS:
                colunas = {r[1] for r in conn.execute(f"PRAGMA table_info({tabela})").fetchall()}
                if "destinatario_cep" not in colunas:
                    continue
                chaves = [c for c in ("nroPedido", "idSolicitacaoInterno") if c in colunas]
                if not chaves:
                    continue
                marcas = ",".join("?" * len(codigos))
                onde = " OR ".join(f"{c} IN ({marcas})" for c in chaves)
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
        uteis = cfg["contagem"] == "uteis"
        detalhe["prazo"] = somar_dias(base_da_contagem(base) if uteis else base, dias, uteis)
    return detalhe


def prazo_para_cliente(detalhe, status_key, hoje=None):
    """"dd/mm/aaaa" so com tudo real, ligado, pedido a caminho e prazo de hoje em diante (nunca vencido). Senao ""."""
    if not detalhe or not detalhe.get("ligado") or not detalhe.get("prazo") or status_key not in A_CAMINHO:
        return ""
    if detalhe["prazo"] < (hoje or datetime.now(BRASILIA).date()):
        return ""
    return detalhe["prazo"].strftime("%d/%m/%Y")
