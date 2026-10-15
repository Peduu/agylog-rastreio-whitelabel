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

Vistoria de 15/10/2026 (relatorio de entregas do TMS, 21 mil pedidos, + sondas so leitura no servidor):
- prazo registrado do TMS (tabela prazos_tms, o "Dt. Prazo Atual" de cada pedido) vale antes de qualquer calculo;
- CEP: base de enderecos + rastreios.cep do portal (so na linha do mesmo cliente do TMS); CEPs diferentes = conflito = nada;
- servico do pedido vem da API (campo "servico": 4 = Convencional, 8 = Expressa/Leve);
- alguns clientes tem prazo proprio no TMS (BRB CARD no DF, CAOA, CCXP em alguns CEPs): prazo observado no TMS por cliente+CEP
  (prazos_cep_cliente) vale antes da tabela geral, e onde a tabela geral errou para o cliente (prazos_cep_bloqueio) so vale o
  observado. Teste cego (aprende ate 07/10, confere 08-15/10): 81% certo, 1 erro em 11.700, o resto sem prazo.
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
FAIXAS_DF = (("70000000", "72799999"), ("73000000", "73699999"))
FAIXA_SP04 = ("04000000", "04999999")
SEM_PRAZO_CONFIAVEL = FAIXAS_DF + (FAIXA_SP04,)   # so quando o cliente do pedido nao e conhecido
REGIOES = ("DF", "SP04", "resto")
# Campo "servico" das ocorrencias da API x "Sigla do Servico" da abrangencia (conferido em 728 pedidos, 15/10/2026).
SERVICOS_API = {"4": ("ENT_CONV",), "8": ("ENT_EXP", "LEVE")}
_CACHE_CEP = {}            # codigo -> (cep, instante); o mesmo pedido e consultado de 30 em 30 s pela pagina aberta
_CACHE_SEGUNDOS = 600


def so_digitos(valor):
    return re.sub(r"\D", "", str(valor or ""))


def _cnpjs(cnpjs):
    vistos = []
    for c in cnpjs or ():
        d = so_digitos(c)
        if d and d not in vistos:
            vistos.append(d)
    return vistos


def regiao_cep(cep):
    """Regiao do CEP para o bloqueio por cliente: "DF", "SP04" (Sao Paulo zona sul) ou "resto"."""
    if any(a <= cep <= b for a, b in FAIXAS_DF):
        return "DF"
    return "SP04" if FAIXA_SP04[0] <= cep <= FAIXA_SP04[1] else "resto"


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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prazos_cep_cliente (
            cnpj TEXT NOT NULL,
            cep TEXT NOT NULL,
            dias INTEGER NOT NULL,
            PRIMARY KEY (cnpj, cep)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prazos_cep_bloqueio (
            cnpj TEXT NOT NULL,
            regiao TEXT NOT NULL,
            PRIMARY KEY (cnpj, regiao)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prazos_tms (
            pedido TEXT NOT NULL,
            cnpj TEXT NOT NULL,
            prazo TEXT NOT NULL,
            carregado_em TEXT NOT NULL,
            PRIMARY KEY (pedido, cnpj)
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


def substituir_prazos_cliente(conn, linhas):
    """Troca o prazo observado no TMS por cliente+CEP. linhas = [(cnpj, cep, dias)]. Mesmo cliente+CEP com dias diferentes =
    conflito = fica de fora. Devolve quantas entraram."""
    validas, conflito = {}, set()
    for cnpj, cep, dias in linhas:
        cnpj, cep = so_digitos(cnpj), normalizar_cep(cep)
        try:
            dias = int(dias)
        except (TypeError, ValueError):
            continue
        if cnpj and cep and 0 <= dias <= 120:
            if validas.get((cnpj, cep), dias) != dias:
                conflito.add((cnpj, cep))
            validas[(cnpj, cep)] = dias
    for chave in conflito:
        validas.pop(chave)
    conn.execute("DELETE FROM prazos_cep_cliente")
    conn.executemany("INSERT INTO prazos_cep_cliente (cnpj, cep, dias) VALUES (?, ?, ?)",
                     [(c, e, d) for (c, e), d in validas.items()])
    return len(validas)


def substituir_bloqueios(conn, linhas):
    """Troca as regioes onde a tabela geral erra para o cliente. linhas = [(cnpj, regiao)]. Devolve quantas entraram."""
    validas = {(so_digitos(c), r) for c, r in linhas if so_digitos(c) and r in REGIOES}
    conn.execute("DELETE FROM prazos_cep_bloqueio")
    conn.executemany("INSERT INTO prazos_cep_bloqueio (cnpj, regiao) VALUES (?, ?)", sorted(validas))
    return len(validas)


def substituir_prazos_tms(conn, linhas):
    """Troca o prazo registrado do TMS por pedido ("Dt. Prazo Atual"). linhas = [(pedido, cnpj, AAAA-MM-DD)]. Mesmo pedido do
    mesmo cliente com datas diferentes = conflito = fica de fora. Devolve quantos entraram."""
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    validas, conflito = {}, set()
    for pedido, cnpj, prazo in linhas:
        pedido, cnpj = str(pedido or "").strip().upper(), so_digitos(cnpj)
        try:
            prazo = datetime.strptime(str(prazo or "").strip(), "%Y-%m-%d").date().isoformat()
        except ValueError:
            continue
        if pedido and cnpj:
            if validas.get((pedido, cnpj), prazo) != prazo:
                conflito.add((pedido, cnpj))
            validas[(pedido, cnpj)] = prazo
    for chave in conflito:
        validas.pop(chave)
    conn.execute("DELETE FROM prazos_tms")
    conn.executemany("INSERT INTO prazos_tms (pedido, cnpj, prazo, carregado_em) VALUES (?, ?, ?, ?)",
                     [(p, c, d, agora) for (p, c), d in validas.items()])
    return len(validas)


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


def _dias_tabela_geral(conn, cep, servico=None):
    """Tabela geral (abrangencia do TMS). Em cada servico vale a faixa mais estreita que contem o CEP. Servico do pedido
    conhecido (4 ou 8): so os servicos dele, e todos com o mesmo prazo. Desconhecido: TODOS os servicos da tabela cobrem o
    CEP com o MESMO prazo (nada de chute)."""
    servicos = {r[0] for r in conn.execute("SELECT DISTINCT servico FROM prazos_cep").fetchall()}
    por_servico = {}
    for servico_faixa, dias in conn.execute("""
        SELECT servico, dias FROM prazos_cep
        WHERE cep_inicial <= ? AND cep_final >= ?
        ORDER BY CAST(cep_final AS INTEGER) - CAST(cep_inicial AS INTEGER) ASC, id ASC
    """, (cep, cep)).fetchall():
        por_servico.setdefault(servico_faixa, int(dias))
    alvo = SERVICOS_API.get(str(servico or "").strip())
    if alvo and set(alvo) <= servicos:
        valores = {por_servico.get(s) for s in alvo}
        return next(iter(valores)) if len(valores) == 1 and None not in valores else None
    if not por_servico or set(por_servico) != servicos or len(set(por_servico.values())) != 1:
        return None
    return next(iter(por_servico.values()))


def dias_para_cep(conn, cep, servico=None, cnpjs=()):
    """Dias para o CEP ou None.
    Com o cliente do pedido (CNPJs do TMS): 1) prazo observado no TMS para o cliente+CEP (0 dia = vence no cadastro = nada);
    2) regiao bloqueada para o cliente (a tabela geral errou para ele) = nada; 3) tabela geral pelo servico do pedido.
    Sem o cliente: tabela geral, e nada no DF e em SP 04xxx (onde ha clientes com prazo proprio no TMS)."""
    cep = normalizar_cep(cep)
    if not cep:
        return None
    cnpjs = _cnpjs(cnpjs)
    if cnpjs and not conn.execute("SELECT 1 FROM prazos_cep_bloqueio LIMIT 1").fetchone():
        cnpjs = []   # sem a conferencia por cliente carregada, vale a regra antiga (nunca a tabela geral no DF/SP 04xxx)
    if not cnpjs:
        if any(a <= cep <= b for a, b in SEM_PRAZO_CONFIAVEL):
            return None
        return _dias_tabela_geral(conn, cep, servico)
    marcas = ",".join("?" * len(cnpjs))
    observados = dict(conn.execute(f"SELECT cnpj, dias FROM prazos_cep_cliente WHERE cep = ? AND cnpj IN ({marcas})",
                                   [cep] + cnpjs).fetchall())
    if observados:
        dias = int(next(observados[c] for c in cnpjs if c in observados))
        return dias if dias > 0 else None
    if conn.execute(f"SELECT 1 FROM prazos_cep_bloqueio WHERE regiao = ? AND cnpj IN ({marcas}) LIMIT 1",
                    [regiao_cep(cep)] + cnpjs).fetchone():
        return None
    return _dias_tabela_geral(conn, cep, servico)


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


def servico_tms(ocorrencias):
    """Servico do pedido no TMS (campo "servico" das ocorrencias da API). "" se faltar ou vier misturado."""
    valores = {str(o.get("servico") or "").strip() for o in ocorrencias or []} - {""}
    return next(iter(valores)) if len(valores) == 1 else ""


def cnpjs_tms(ocorrencias):
    """CNPJs do pedido no TMS (embarcador e remetente), so digitos, sem repetir."""
    return _cnpjs(o.get(campo) for o in ocorrencias or [] for campo in ("cnpj", "cnpjRemetente"))


def cep_do_pedido(caminho_db, codigos, conn_portal=None, cnpjs=()):
    """CEP do destinatario, so de dado real e so leitura: base de enderecos do sistema de subir arquivos (pedido ou AR) e
    rastreios.cep do portal (so na linha do mesmo cliente do TMS, porque numero de pedido se repete entre clientes).
    Fontes com CEPs diferentes = conflito = "" (nunca escolher um no chute)."""
    codigos = [str(c or "").strip().upper() for c in codigos if str(c or "").strip()]
    cnpjs = _cnpjs(cnpjs)
    if not codigos:
        return ""
    chave = "|".join([str(caminho_db or ""), "1" if conn_portal is not None else "0"] + codigos + ["#"] + cnpjs)
    guardado = _CACHE_CEP.get(chave)
    if guardado and time.time() - guardado[1] < _CACHE_SEGUNDOS:
        return guardado[0]
    ceps = set()
    marcas = ",".join("?" * len(codigos))
    if caminho_db:
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
                    onde = " OR ".join(f"{c} IN ({marcas})" for c in chaves)
                    for (valor,) in conn.execute(f"SELECT destinatario_cep FROM {tabela} WHERE {onde} LIMIT 20",
                                                 codigos * len(chaves)).fetchall():
                        if normalizar_cep(valor):
                            ceps.add(normalizar_cep(valor))
            finally:
                conn.close()
        except sqlite3.Error:
            pass
    if conn_portal is not None and cnpjs:
        try:
            for valor, cnpj in conn_portal.execute(f"SELECT cep, cnpj_cliente FROM rastreios WHERE codigo IN ({marcas})",
                                                   codigos).fetchall():
                if so_digitos(cnpj) in cnpjs and normalizar_cep(valor):
                    ceps.add(normalizar_cep(valor))
        except sqlite3.Error:   # banco sem rastreios.cep: so a base de enderecos
            pass
    cep = next(iter(ceps)) if len(ceps) == 1 else ""
    _CACHE_CEP[chave] = (cep, time.time())
    return cep


def prazo_tms_registrado(conn, pedidos, cnpjs):
    """Prazo do TMS ("Dt. Prazo Atual") registrado para o pedido do mesmo cliente. None se nao houver ou se nao for unico."""
    pedidos = [str(p or "").strip().upper() for p in pedidos if str(p or "").strip()]
    cnpjs = _cnpjs(cnpjs)
    if not pedidos or not cnpjs:
        return None
    datas = set()
    for (valor,) in conn.execute(f"SELECT DISTINCT prazo FROM prazos_tms WHERE pedido IN ({','.join('?' * len(pedidos))}) "
                                 f"AND cnpj IN ({','.join('?' * len(cnpjs))})", pedidos + cnpjs).fetchall():
        try:
            datas.add(datetime.strptime(str(valor), "%Y-%m-%d").date())
        except ValueError:
            return None
    return next(iter(datas)) if len(datas) == 1 else None


def calcular(conn, caminho_modelos, codigos, ocorrencias, cnpjs=(), servico=None, pedidos_tms=None):
    """Detalhe do calculo (para o simulador do admin e para a pagina).
    1) prazo registrado do TMS para o pedido (fonte "tms"); 2) CEP x tabela, contado do cadastro no TMS (fonte "tabela")."""
    cfg = configuracao(conn)
    base = data_cadastro_tms(ocorrencias)
    detalhe = {"cep": "", "dias": None, "cadastro": base, "contagem": cfg["contagem"], "ligado": cfg["ligado"],
               "prazo": None, "fonte": ""}
    registrado = prazo_tms_registrado(conn, pedidos_tms if pedidos_tms else codigos, cnpjs)
    if registrado:
        detalhe.update(prazo=registrado, fonte="tms")
        return detalhe
    cep = cep_do_pedido(caminho_modelos, codigos, conn, cnpjs)
    dias = dias_para_cep(conn, cep, servico, cnpjs) if cep else None
    detalhe.update(cep=cep, dias=dias)
    if cep and dias is not None and base:
        uteis = cfg["contagem"] == "uteis"
        detalhe["prazo"] = somar_dias(base_da_contagem(base) if uteis else base, dias, uteis)
        detalhe["fonte"] = "tabela"
    return detalhe


def prazo_para_cliente(detalhe, status_key, hoje=None):
    """"dd/mm/aaaa" so com tudo real, ligado, pedido a caminho e prazo de hoje em diante (nunca vencido). Senao ""."""
    if not detalhe or not detalhe.get("ligado") or not detalhe.get("prazo") or status_key not in A_CAMINHO:
        return ""
    if detalhe["prazo"] < (hoje or datetime.now(BRASILIA).date()):
        return ""
    return detalhe["prazo"].strftime("%d/%m/%Y")
