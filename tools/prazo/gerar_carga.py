"""Gera a carga da vistoria (prazo registrado do TMS, prazo proprio por cliente+CEP, bloqueios) a partir do relatorio de
entregas do TMS e confere com o codigo novo do portal (prazo_cep.py). So totais na tela; a carga vai para OUT (segredo)."""
import base64, csv, gzip, os, re, sqlite3, sys
from collections import Counter, defaultdict
from datetime import datetime, date, timedelta

REL, ABR, WT, OUT = sys.argv[1:5]
sys.path.insert(0, WT)
import prazo_cep as P

CORTE = date(2026, 10, 8)


def ler(caminho):
    with open(caminho, encoding="latin1", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


faixas, _ = P.ler_faixas(ler(ABR))
geral = sqlite3.connect(":memory:")
P.criar_tabelas(geral)
P.substituir_faixas(geral, faixas)


def uteis(a, b):
    if b < a:
        return -1
    n, d = 0, a
    while d < b:
        d += timedelta(days=1)
        if d.weekday() < 5 and d not in P.feriados_nacionais(d.year):
            n += 1
    return n


pedidos = []
for l in ler(REL):
    try:
        pa = datetime.strptime(l["Dt. Prazo Atual"].strip()[:10], "%d/%m/%Y").date()
        cad = datetime.strptime(l["Dt. Cadastro"].strip()[:16], "%d/%m/%Y %H:%M").date()
    except ValueError:
        continue
    cep = P.normalizar_cep(l["CEP Pessoa Visita"])
    sv = "4" if l["Tipo Serviço"] == "Entrega Convencional" else "8"
    base = P.base_da_contagem(cad)
    pedidos.append(dict(nome=l["Cliente"], nome_fil=l["Filial"], pedido=(l["Nro. Pedido"] or "").strip().upper(), cli=P.so_digitos(l["CNPJ Cliente"]),
                        fil=P.so_digitos(l["CNPJ Filial"]), cep=cep, cad=cad, base=base, pa=pa, sv=sv,
                        dias=uteis(base, pa), geral=P._dias_tabela_geral(geral, cep, sv) if cep else None))
print("pedidos com prazo no relatorio:", len(pedidos))

filiais = defaultdict(set)
for p in pedidos:
    filiais[p["cli"]].add(p["fil"])
dup = {cli: next(iter(f)) for cli, f in filiais.items() if len(f) == 1 and next(iter(f)) != cli}
print("clientes com uma filial de CNPJ diferente (repete a chave no CNPJ do cliente):", len(dup))


def chaves(p):
    # A API devolve o CNPJ do cliente para quase todos e o da filial para alguns (Tricard, Cartao de Todos...): os dados
    # valem nas duas chaves, cada uma com TODOS os pedidos que caem nela (cliente = todas as filiais juntas; conflito = nada).
    return {p["fil"], p["cli"]} - {""}


def montar(amostra):
    obs = defaultdict(list)
    for p in amostra:
        if p["cep"] and p["dias"] >= 0:
            for k in chaves(p):
                obs[(k, p["cep"])].append(p)
    # Chave que junta filiais (a API devolve o mesmo CNPJ para todas): o prazo observado num CEP so vale se TODAS as filiais
    # com pedidos naquela regiao foram vistas naquele CEP (uma filial nao responde pela outra: BRB CARD x BRB AGENCIA no DF).
    filiais_regiao = defaultdict(set)
    for p in amostra:
        if p["cep"]:
            for k in chaves(p):
                filiais_regiao[(k, P.regiao_cep(p["cep"]))].add(p["fil"])
    cli_cep = []
    for (fil, cep), ps in obs.items():
        dias = {p["dias"] for p in ps}
        if len(dias) != 1:
            continue
        if not filiais_regiao[(fil, P.regiao_cep(cep))] <= {p["fil"] for p in ps}:
            continue
        d = dias.pop()
        if any(p["geral"] != d for p in ps) and len(ps) < 2:
            continue                           # diverge da tabela geral com uma observacao so: nao basta
        cli_cep.append((fil, cep, d))
    conf = defaultdict(Counter)
    for p in amostra:
        if p["cep"] and p["geral"] is not None:
            for k in chaves(p):
                conf[(k, P.regiao_cep(p["cep"]))]["ok" if P.somar_dias(p["base"], p["geral"], True) == p["pa"] else "erro"] += 1
    def ruim(c):
        return c["erro"] and not (c["ok"] + c["erro"] >= 100 and c["erro"] / (c["ok"] + c["erro"]) <= 0.002)
    bloq = [(fil, reg) for (fil, reg), c in conf.items() if ruim(c)]
    lib = [(fil, reg) for (fil, reg), c in conf.items() if reg in ("DF", "SP04") and not ruim(c) and c["ok"] >= 3]
    tms = [(p["pedido"], k, p["pa"].isoformat()) for p in amostra if p["pedido"] and ";" not in p["pedido"] for k in chaves(p)]
    return cli_cep, bloq, lib, tms


def carregar(cli_cep, bloq, lib, tms):
    c = sqlite3.connect(":memory:")
    P.criar_tabelas(c)
    P.substituir_faixas(c, faixas)
    n = (P.substituir_prazos_cliente(c, cli_cep), P.substituir_bloqueios(c, bloq), P.substituir_liberados(c, lib),
         P.substituir_prazos_tms(c, tms))
    P.gravar_config(c, "prazo_cep_contagem", "uteis")
    return c, n


API_FILIAL = ("TRICARD", "CARTAO DE TODOS", "CALCARD")   # sondas 3/4: a API devolve o CNPJ da filial nesses


def chave_api(p, modo):
    if modo == "filial":
        return p["fil"]
    if modo == "cliente":
        return p["cli"]
    return p["fil"] if p["nome"].upper().startswith(API_FILIAL) or p["nome_fil"] == "BRB PAY" else p["cli"]


ERROS = Counter()


def conferir(nome, c, amostra, com_registrado, modo="api"):
    r = Counter()
    for p in amostra:
        k = [chave_api(p, modo)]
        if com_registrado and P.prazo_tms_registrado(c, [p["pedido"]], k, p["cad"]):
            prazo = P.prazo_tms_registrado(c, [p["pedido"]], k, p["cad"])
        else:
            d = P.dias_para_cep(c, p["cep"], p["sv"], k) if p["cep"] else None
            prazo = P.somar_dias(p["base"], d, True) if d is not None else None
        r["sem" if prazo is None else ("certo" if prazo == p["pa"] else "ERRADO")] += 1
        if prazo is not None and prazo != p["pa"] and not com_registrado and modo == "api":
            obs = c.execute("SELECT dias FROM prazos_cep_cliente WHERE cnpj = ? AND cep = ?", (k[0], p["cep"])).fetchone()
            ERROS[(p["nome"][:10], p["nome_fil"][:12], P.regiao_cep(p["cep"]), "observado=" + str(obs[0] if obs else None),
                   "geral=" + str(p["geral"]), "tms=" + str(p["dias"]))] += 1
    n = sum(r.values())
    print(f"  {nome:52} certo {r['certo']/n:6.1%} | ERRADO {r['ERRADO']} ({r['ERRADO']/n:.2%}) | sem {r['sem']/n:5.1%}")


treino = [p for p in pedidos if p["cad"] < CORTE]
teste = [p for p in pedidos if p["cad"] >= CORTE]
c, n = carregar(*montar(treino))
print("conferencia com o codigo novo (aprende ate 07/10, confere 08-15/10), carga do treino:", n)
for modo in ("api", "filial", "cliente"):
    conferir(f"so a regra, teste cego, chave {modo}", c, teste, False, modo)
print("erros do teste cego (chave api):", ERROS.most_common(12))

cli_cep, bloq, lib, tms = montar(pedidos)
c, n = carregar(cli_cep, bloq, lib, tms)
print("carga final (todos os pedidos): proprio cliente+CEP, bloqueios, liberados, registrados:", n)
for modo in ("api", "filial", "cliente"):
    conferir(f"pagina com a carga final, chave {modo}", c, pedidos, True, modo)
conferir("so a regra com a carga final, chave api", c, pedidos, False)
print("bloqueios por regiao:", Counter(reg for _, reg in bloq), "| liberados:", Counter(reg for _, reg in lib))

texto = "\n".join(["#TMS"] + [";".join(x) for x in tms] + ["#CLI"] + [f"{a};{b};{d}" for a, b, d in cli_cep]
                  + ["#BLQ"] + [f"{a};{b}" for a, b in bloq] + ["#LIB"] + [f"{a};{b}" for a, b in lib])
blob = base64.b64encode(gzip.compress(texto.encode(), 9)).decode()
partes = [blob[i:i + 45000] for i in range(0, len(blob), 45000)]
os.makedirs(OUT, exist_ok=True)
for i, parte in enumerate(partes, 1):
    open(os.path.join(OUT, f"parte{i}.b64"), "w").write(parte)
print("carga:", len(blob), "caracteres em", len(partes), "partes")
