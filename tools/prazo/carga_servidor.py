import gzip, json, os, random, shutil, sqlite3, sys, time, urllib.request
from datetime import datetime

DB = os.environ.get("CARGA_DB", "/home/rastreamento/database.db")
APP = os.environ.get("CARGA_APP", "/home/rastreamento")
PASTA = os.environ.get("CARGA_PASTA", "/tmp/prazo-vistoria")
URL = os.environ.get("CARGA_URL", "http://127.0.0.1:8000/api/rastrear")
gravar = os.environ.get("CONFIRMAR", "").strip() == "CARREGAR"
TABELAS = ("prazos_tms", "prazos_cep_cliente", "prazos_cep_bloqueio", "prazos_cep_liberado")
sys.path.insert(0, APP)
try:
    import prazo_cep
    for nome in ("substituir_prazos_tms", "substituir_prazos_cliente", "substituir_bloqueios", "substituir_liberados"):
        if not hasattr(prazo_cep, nome):
            sys.exit(f"ERRO: o prazo_cep.py do servidor e anterior a vistoria (falta {nome}). Nada foi alterado.")
    secoes = {"#TMS": [], "#CLI": [], "#BLQ": [], "#LIB": []}
    atual = None
    for linha in gzip.open(os.path.join(PASTA, "vistoria.txt.gz")).read().decode("utf-8").splitlines():
        if linha in secoes:
            atual = linha
        elif atual and linha.strip():
            secoes[atual].append(tuple(linha.split(";")))
    print("carga: registrados do TMS", len(secoes["#TMS"]), "| cliente+CEP", len(secoes["#CLI"]), "| bloqueios", len(secoes["#BLQ"]),
          "| liberados", len(secoes["#LIB"]))
    if len(secoes["#TMS"]) < 10000 or len(secoes["#CLI"]) < 1000 or not secoes["#BLQ"] or not secoes["#LIB"]:
        sys.exit("ERRO: carga incompleta. Nada foi alterado.")
    if not os.path.exists(DB):
        sys.exit(f"ERRO: {DB} nao existe. Nada foi alterado.")
    conn = sqlite3.connect(DB)
    try:
        def contar():
            r = {}
            for t in TABELAS:
                existe = conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (t,)).fetchone()
                r[t] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] if existe else None
            return r
        try:
            config = prazo_cep.configuracao(conn)
        except sqlite3.Error:
            config = "sem config_portal"
        print("antes:", contar(), "| config:", config)
        if not gravar:
            print("SO RELATO: nada gravado. Para gravar, rode de novo com confirmar = CARREGAR.")
        else:
            os.makedirs(os.path.join(APP, "backups"), exist_ok=True)
            destino = os.path.join(APP, "backups", f"prazo-vistoria-{datetime.now():%Y%m%d-%H%M%S}.db")
            copia = sqlite3.connect(destino)
            conn.backup(copia)
            copia.close()
            print("backup do banco:", destino)
            with conn:
                prazo_cep.criar_tabelas(conn)
                n = (prazo_cep.substituir_prazos_tms(conn, secoes["#TMS"]), prazo_cep.substituir_prazos_cliente(conn, secoes["#CLI"]),
                     prazo_cep.substituir_bloqueios(conn, secoes["#BLQ"]), prazo_cep.substituir_liberados(conn, secoes["#LIB"]))
            print("gravado (registrados, cliente+CEP, bloqueios, liberados):", n, "| depois:", contar())
    finally:
        conn.close()

    if gravar:
        # Conferencia na propria pagina: pedidos registrados escolhidos ao acaso; so totais no log (repositorio publico).
        random.seed(time.time())
        amostra = random.sample(secoes["#TMS"], 28)
        r = {"com previsao = TMS": 0, "com previsao DIFERENTE": 0, "sem previsao (vencido, entregue ou fora de a caminho)": 0,
             "nao achou": 0, "erro": 0}
        for pedido, cnpj, prazo in amostra:
            try:
                req = urllib.request.Request(URL, data=json.dumps({"codigo": pedido}).encode(), headers={"Content-Type": "application/json"})
                d = json.loads(urllib.request.urlopen(req, timeout=40).read().decode("utf-8"))
                if not d.get("ok"):
                    r["nao achou"] += 1
                elif not d.get("previsao"):
                    r["sem previsao (vencido, entregue ou fora de a caminho)"] += 1
                elif d["previsao"] == datetime.strptime(prazo, "%Y-%m-%d").strftime("%d/%m/%Y"):
                    r["com previsao = TMS"] += 1
                else:
                    r["com previsao DIFERENTE"] += 1
            except Exception:
                r["erro"] += 1
            time.sleep(2.2)
        print("conferencia na pagina (28 pedidos ao acaso):", r)
finally:
    shutil.rmtree(PASTA, ignore_errors=True)
