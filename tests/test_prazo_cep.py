"""Prazo de entrega por faixa de CEP (prazo_cep.py + endpoints): so dado real, desligado por padrao, nunca vencido."""
import io
import os
import sqlite3
import tempfile
import unittest
from datetime import date, datetime, timedelta
from unittest.mock import patch

from test_demo_caoa import portal

import prazo_cep as P


def banco_modelos(linhas):
    """Banco do sistema de subir arquivos (so o que o portal le): registros_modelo."""
    caminho = os.path.join(tempfile.mkdtemp(), "envios_modelos.db")
    c = sqlite3.connect(caminho)
    c.execute("CREATE TABLE registros_modelo (id INTEGER PRIMARY KEY, idSolicitacaoInterno TEXT, nroPedido TEXT,"
              " destinatario_cep TEXT, criado_em TEXT)")
    c.executemany("INSERT INTO registros_modelo (idSolicitacaoInterno, nroPedido, destinatario_cep, criado_em) VALUES (?, ?, ?, ?)", linhas)
    c.commit()
    c.close()
    return caminho


class FuncoesTest(unittest.TestCase):
    def setUp(self):
        P._CACHE_CEP.clear()

    def test_normalizar_cep(self):
        self.assertEqual(P.normalizar_cep("30140-071"), "30140071")
        self.assertEqual(P.normalizar_cep(1310100), "01310100")          # Excel comeu o zero
        self.assertEqual(P.normalizar_cep("123"), "")
        self.assertEqual(P.normalizar_cep(1310100.0), "01310100")       # coluna REAL
        self.assertEqual(P.normalizar_cep("1310100.0"), "01310100")     # export do pandas
        self.assertEqual(P.normalizar_cep("30140071.0"), "30140071")
        self.assertEqual(P.normalizar_cep(3014.5), "")
        self.assertEqual(P.normalizar_cep(None), "")

    def test_ler_faixas_ignora_linha_ruim(self):
        faixas, ign = P.ler_faixas([
            {"CEP Inicial": "01000-000", "CEP Final": "05999-999", "Dias": "2"},
            {"cep_inicial": "30000000", "cep_final": "39999999", "prazo": "10"},
            {"cep_inicial": "50000000", "cep_final": "40000000", "dias": "3"},   # invertida
            {"cep_inicial": "", "cep_final": "1", "dias": "x"},
        ])
        self.assertEqual(faixas, [("01000000", "05999999", 2, ""), ("30000000", "39999999", 10, "")])
        self.assertEqual(ign, 2)

    def test_faixa_mais_estreita_e_dias(self):
        c = sqlite3.connect(":memory:")
        P.criar_tabelas(c)
        P.substituir_faixas(c, [("30000000", "39999999", 10), ("30100000", "30199999", 3)])
        self.assertEqual(P.dias_para_cep(c, "30140071"), 3)
        self.assertEqual(P.dias_para_cep(c, "35000000"), 10)
        self.assertIsNone(P.dias_para_cep(c, "01310100"))

    def test_tabela_do_tms_como_vem(self):
        linhas = [{"CEP Inicial": "07000-000", "CEP Final": "07099-999", "Sigla do Serviço": s, "Prazo Entrega": "8",
                   "Prazo Entrega Ult. Milha": "2"} for s in ("ENT_CONV", "ENT_EXP", "LEVE")]
        faixas, ign = P.ler_faixas(linhas)
        self.assertEqual(ign, 0)
        self.assertEqual(sorted(faixas), [("07000000", "07099999", 8, "ENT_CONV"), ("07000000", "07099999", 8, "ENT_EXP"),
                                          ("07000000", "07099999", 8, "LEVE")])        # "Prazo Entrega", nunca a ultima milha

    def test_servicos_precisam_concordar(self):
        c = sqlite3.connect(":memory:")
        P.criar_tabelas(c)
        P.substituir_faixas(c, [
            ("07000000", "07099999", 8, "ENT_CONV"), ("07000000", "07099999", 8, "ENT_EXP"), ("07000000", "07099999", 8, "LEVE"),
            ("30000000", "31999999", 8, "ENT_CONV"), ("30000000", "31999999", 8, "ENT_EXP"), ("30000000", "31999999", 8, "LEVE"),
            ("30000001", "31999999", 4, "ENT_CONV"),                      # BH: convencional 4, os outros 8 -> diverge
            ("72980000", "73699999", 4, "LEVE"),                          # so um servico cobre -> sem prazo
        ])
        self.assertEqual(P.dias_para_cep(c, "07050000"), 8)
        self.assertIsNone(P.dias_para_cep(c, "30140071"))
        self.assertIsNone(P.dias_para_cep(c, "73000000"))
        self.assertIsNone(P.dias_para_cep(c, "99999999"))

    def test_feriados_nacionais(self):
        self.assertIn(date(2026, 10, 12), P.feriados_nacionais(2026))
        self.assertIn(date(2026, 4, 3), P.feriados_nacionais(2026))     # Sexta-feira Santa de 2026
        self.assertIn(date(2026, 11, 20), P.feriados_nacionais(2026))
        self.assertEqual(P.somar_dias(date(2026, 9, 24), 8, uteis=True), date(2026, 10, 6))   # pedido 632: igual ao TMS
        self.assertEqual(P.somar_dias(date(2026, 10, 8), 8, uteis=True), date(2026, 10, 21))  # pula o 12/10

    def test_regra_do_tms_conferida_no_relatorio(self):
        # cadastro no sabado conta da segunda (19/09, 26/09, 03/10 e 10/10 de 2026 bateram 100% com o TMS)
        def prazo(cad, dias=8):
            return P.somar_dias(P.base_da_contagem(cad), dias, uteis=True)
        self.assertEqual(prazo(date(2026, 9, 19)), date(2026, 10, 1))
        self.assertEqual(prazo(date(2026, 10, 3)), date(2026, 10, 16))
        self.assertEqual(prazo(date(2026, 10, 10)), date(2026, 10, 22))    # base = segunda 12/10 (feriado), conta de 13/10
        self.assertEqual(prazo(date(2026, 9, 24)), date(2026, 10, 6))     # dia util: do proprio dia (pedido 632)
        c = sqlite3.connect(":memory:")
        P.criar_tabelas(c)
        P.substituir_faixas(c, [("70000000", "73699999", 8, ""), ("04000000", "04999999", 8, ""), ("01000000", "01999999", 8, "")])
        self.assertIsNone(P.dias_para_cep(c, "70040000"))                 # DF: TMS sem prazo real
        self.assertIsNone(P.dias_para_cep(c, "04538000"))                 # SP 04xxx: TMS mistura ultima milha
        self.assertEqual(P.dias_para_cep(c, "01310100"), 8)
        self.assertEqual(P.dias_para_cep(c, "72900000"), 8)               # entorno (GO) continua

    def test_somar_dias(self):
        sexta = date(2026, 10, 16)
        self.assertEqual(P.somar_dias(sexta, 3), date(2026, 10, 19))
        self.assertEqual(P.somar_dias(sexta, 3, uteis=True), date(2026, 10, 21))   # pula sabado e domingo

    def test_cadastro_e_a_ocorrencia_1(self):
        oc = [{"codigoOcorrencia": "28", "dtOcorrencia": "2026-09-25 08:00:00"},
              {"codigoOcorrencia": "1", "dtOcorrencia": "2026-09-24 13:50:00"}]
        self.assertEqual(P.data_cadastro_tms(oc), date(2026, 9, 24))
        self.assertIsNone(P.data_cadastro_tms([{"codigoOcorrencia": "28", "dtOcorrencia": "2026-09-25 08:00:00"}]))   # sem o "1": sem prazo
        self.assertIsNone(P.data_cadastro_tms([]))

    def test_cep_do_pedido_so_leitura(self):
        caminho = banco_modelos([("AR1", "632", "06000-000", "2026-09-24 13:40:00"), ("AR2", "777", "", "2026-09-24 13:40:00")])
        self.assertEqual(P.cep_do_pedido(caminho, ["632"]), "06000000")
        self.assertEqual(P.cep_do_pedido(caminho, ["XYZ", "AR1"]), "06000000")      # tambem pelo AR
        self.assertEqual(P.cep_do_pedido(caminho, ["777"]), "")                     # sem CEP: sem prazo
        self.assertEqual(P.cep_do_pedido("/nao/existe.db", ["632"]), "")

    def tabela_bh(self):
        c = sqlite3.connect(":memory:")
        P.criar_tabelas(c)
        P.substituir_faixas(c, [(i, f, d, s) for (i, f, d) in (("30000000", "31999999", 8), ("70000000", "73699999", 8),
                                                              ("04000000", "04999999", 8), ("01000000", "01999999", 8))
                                for s in ("ENT_CONV", "ENT_EXP", "LEVE")] + [("30000001", "31999999", 4, "ENT_CONV")])
        return c

    def test_servico_do_pedido_resolve_divergencia(self):
        c = self.tabela_bh()
        self.assertIsNone(P.dias_para_cep(c, "30140071"))                    # servico desconhecido: diverge, nada
        self.assertEqual(P.dias_para_cep(c, "30140071", servico="4"), 4)     # 4 = Convencional
        self.assertEqual(P.dias_para_cep(c, "30140071", servico="8"), 8)     # 8 = Expressa/Leve (iguais)
        self.assertIsNone(P.dias_para_cep(c, "30140071", servico="99"))      # servico que nao conhecemos: todos iguais
        self.assertIsNone(P.dias_para_cep(c, "99999999", servico="4"))

    def test_prazo_proprio_do_cliente_e_bloqueio(self):
        c = self.tabela_bh()
        P.substituir_prazos_cliente(c, [("11.111.111/0001-11", "70040000", 6), ("11111111000111", "70050000", 0),
                                        ("11111111000111", "123", 5), ("x", "70040000", 2)])
        P.substituir_bloqueios(c, [("11111111000111", "DF"), ("22222222000122", "SP04"), ("11111111000111", "lua")])
        cli, outro = ["11111111000111"], ["33333333000133"]
        self.assertEqual(P.dias_para_cep(c, "70040000", "8", cli), 6)        # observado no TMS vale antes de tudo
        self.assertIsNone(P.dias_para_cep(c, "70050000", "8", cli))          # 0 dia = vence no cadastro: nunca mostra
        self.assertIsNone(P.dias_para_cep(c, "70060000", "8", cli))          # DF bloqueado para o cliente
        self.assertEqual(P.dias_para_cep(c, "01310100", "8", cli), 8)        # fora do DF a tabela geral vale
        self.assertEqual(P.dias_para_cep(c, "70060000", "8", outro), 8)      # cliente sem erro no DF: tabela geral
        self.assertIsNone(P.dias_para_cep(c, "04538000", "8", ["22222222000122"]))
        self.assertIsNone(P.dias_para_cep(c, "70060000", "8"))               # cliente desconhecido: regra antiga (sem DF)
        self.assertIsNone(P.dias_para_cep(c, "04538000"))
        self.assertEqual(P.dias_para_cep(c, "70040000", "8", ["", None, "11111111000111"]), 6)
        self.assertEqual(c.execute("SELECT COUNT(*) FROM prazos_cep_cliente").fetchone()[0], 2)
        self.assertEqual(c.execute("SELECT COUNT(*) FROM prazos_cep_bloqueio").fetchone()[0], 2)
        self.assertEqual(P.substituir_prazos_cliente(c, [("1", "70040000", 6), ("1", "70040000", 7), ("1", "01310100", 8)]), 1)

    def test_sem_conferencia_por_cliente_vale_a_regra_antiga(self):
        c = self.tabela_bh()
        P.substituir_prazos_cliente(c, [("11111111000111", "70040000", 6)])    # bloqueios nao carregados
        self.assertIsNone(P.dias_para_cep(c, "70040000", "8", ["11111111000111"]))
        self.assertIsNone(P.dias_para_cep(c, "70060000", "8", ["33333333000133"]))
        self.assertEqual(P.dias_para_cep(c, "01310100", "8", ["33333333000133"]), 8)

    def test_cep_em_conflito_ou_de_outro_cliente(self):
        base = banco_modelos([("AR1", "500", "06000-000", "2026-09-24 13:40:00"), ("AR2", "500", "07000-000", "2026-09-25 13:40:00"),
                              ("AR3", "600", "08000-000", "2026-09-25 13:40:00")])
        self.assertEqual(P.cep_do_pedido(base, ["500"]), "")                        # dois CEPs para o mesmo numero: nada
        portal_db = sqlite3.connect(":memory:")
        portal_db.execute("CREATE TABLE rastreios (id INTEGER PRIMARY KEY, codigo TEXT, cnpj_cliente TEXT, cep TEXT)")
        portal_db.executemany("INSERT INTO rastreios (codigo, cnpj_cliente, cep) VALUES (?, ?, ?)", [
            ("633", "65.949.995/0001-87", "20960-000"), ("700", "11111111000111", "01310100"), ("600", "1", "09000000")])
        simple = ["65949995000187"]
        self.assertEqual(P.cep_do_pedido(base, ["633"], portal_db, simple), "20960000")   # so no rastreios do portal
        self.assertEqual(P.cep_do_pedido(base, ["700"], portal_db, simple), "")           # linha de outro cliente
        self.assertEqual(P.cep_do_pedido(base, ["633"], portal_db), "")                   # sem cliente do TMS: nao usa
        self.assertEqual(P.cep_do_pedido(base, ["600"], portal_db, ["1"]), "")            # base e rastreios divergem
        self.assertEqual(P.cep_do_pedido(base, ["600"], portal_db, simple), "08000000")
        sem_coluna = sqlite3.connect(":memory:")
        sem_coluna.execute("CREATE TABLE rastreios (id INTEGER PRIMARY KEY, codigo TEXT)")
        self.assertEqual(P.cep_do_pedido(base, ["600"], sem_coluna, simple), "08000000")  # banco sem rastreios.cep

    def test_prazo_registrado_do_tms(self):
        c = sqlite3.connect(":memory:")
        P.criar_tabelas(c)
        n = P.substituir_prazos_tms(c, [("633", "65949995000187", "2026-10-26"), ("634", "1", "26/10/2026"), ("", "1", "2026-10-26"),
                                        ("635", "65949995000187", "2026-10-20"), ("635", "11111111000111", "2026-10-27")])
        self.assertEqual(n, 3)
        self.assertEqual(P.prazo_tms_registrado(c, ["633"], ["65949995000187"]), date(2026, 10, 26))
        self.assertIsNone(P.prazo_tms_registrado(c, ["633"], ["11111111000111"]))      # outro cliente: nao vale
        self.assertIsNone(P.prazo_tms_registrado(c, ["633"], []))
        self.assertIsNone(P.prazo_tms_registrado(c, ["635"], ["65949995000187", "11111111000111"]))   # duas datas: nada
        detalhe = P.calcular(c, "", ["633"], [], cnpjs=["65949995000187"])
        self.assertEqual((detalhe["prazo"], detalhe["fonte"]), (date(2026, 10, 26), "tms"))
        detalhe = P.calcular(c, "", ["999"], [], cnpjs=["65949995000187"])
        self.assertEqual((detalhe["prazo"], detalhe["fonte"]), (None, ""))
        self.assertEqual(P.substituir_prazos_tms(c, [("633", "1", "2026-10-26"), ("633", "1", "2026-10-27"), ("7", "1", "2026-10-27")]), 1)
        self.assertIsNone(P.prazo_tms_registrado(c, ["633"], ["1"]))                   # conflito na carga: fica de fora

    def test_calcular_com_servico_e_cliente(self):
        c = self.tabela_bh()
        P.gravar_config(c, "prazo_cep_contagem", "uteis")
        base = banco_modelos([("AR1", "BH1", "30140-071", "2026-10-14 10:00:00")])
        oc = [{"codigoOcorrencia": "1", "dtOcorrencia": "2026-10-14 19:10:00"}]
        d = P.calcular(c, base, ["BH1"], oc, cnpjs=["33333333000133"], servico="4")
        self.assertEqual((d["cep"], d["dias"], d["prazo"], d["fonte"]), ("30140071", 4, date(2026, 10, 20), "tabela"))
        self.assertIsNone(P.calcular(c, base, ["BH1"], oc)["prazo"])                     # sem servico: diverge, nada

    def test_servico_e_cnpjs_das_ocorrencias(self):
        oc = [{"servico": "8", "cnpj": "11.111.111/0001-11", "cnpjRemetente": ""},
              {"servico": 8, "cnpj": "11111111000111", "cnpjRemetente": "22222222000122"}]
        self.assertEqual(P.servico_tms(oc), "8")
        self.assertEqual(P.cnpjs_tms(oc), ["11111111000111", "22222222000122"])
        self.assertEqual(P.servico_tms(oc + [{"servico": "4"}]), "")                    # misturado: desconhecido
        self.assertEqual((P.servico_tms([]), P.cnpjs_tms(None)), ("", []))

    def test_prazo_para_cliente(self):
        hoje = date(2026, 10, 15)
        base = {"ligado": True, "prazo": date(2026, 10, 20)}
        self.assertEqual(P.prazo_para_cliente(base, "em_rota_entrega", hoje), "20/10/2026")
        self.assertEqual(P.prazo_para_cliente(dict(base, ligado=False), "em_rota_entrega", hoje), "")
        self.assertEqual(P.prazo_para_cliente(base, "entregue", hoje), "")
        self.assertEqual(P.prazo_para_cliente(base, "atencao", hoje), "")
        self.assertEqual(P.prazo_para_cliente(dict(base, prazo=date(2026, 10, 14)), "em_rota_entrega", hoje), "")   # nunca atraso
        self.assertEqual(P.prazo_para_cliente(dict(base, prazo=None), "em_rota_entrega", hoje), "")


class EndpointsTest(unittest.TestCase):
    def setUp(self):
        P._CACHE_CEP.clear()
        conn = portal.get_db_connection()          # outros testes trocam a pasta atual: garante as tabelas no banco da vez
        P.criar_tabelas(conn)
        conn.commit()
        conn.close()
        self.client = portal.app.test_client()
        with self.client.session_transaction() as s:
            s["usuario_id"] = 1
            s["usuario_nome"] = "Admin"
            s["is_admin"] = 1
        limiter = patch.object(portal, "_excedeu_limite_consulta_publica", return_value=False)
        limiter.start()
        self.addCleanup(limiter.stop)
        hoje = datetime.now().date()
        self.cadastro = hoje - timedelta(days=1)
        self.modelos = banco_modelos([("AR9", "PED9", "30140071", "2026-10-01 10:00:00")])
        caminho = patch.object(portal, "resolver_modelos_db_path", return_value=self.modelos)
        caminho.start()
        self.addCleanup(caminho.stop)
        self.addCleanup(self.desligar)

    def desligar(self):
        conn = portal.get_db_connection()
        P.gravar_config(conn, "prazo_cep_ligado", "0")
        P.gravar_config(conn, "prazo_cep_contagem", "corridos")
        for tabela in ("prazos_cep", "prazos_tms", "prazos_cep_cliente", "prazos_cep_bloqueio"):
            conn.execute(f"DELETE FROM {tabela}")
        conn.commit()
        conn.close()

    def resultado(self, badge="EM ROTA"):
        return {"codigo": "PED9", "codigoCliente": "PED9", "statusBadge": badge, "ultimoStatus": "x", "dataBaixa": "",
                "ocorrencias": [{"codigoOcorrencia": "1", "dtOcorrencia": self.cadastro.strftime("%Y-%m-%d 09:00:00")}],
                "ocorrenciasLocal": [], "datasEtapas": {}}

    def importar(self, texto):
        dados = {"arquivo": (io.BytesIO(texto.encode("utf-8")), "faixas.csv")}
        return self.client.post("/api/admin/prazos-cep/importar", data=dados, content_type="multipart/form-data").get_json()

    def test_fluxo_completo_desligado_ate_ligar(self):
        r = self.importar("cep_inicial;cep_final;dias\n30000000;39999999;10\nlixo;;\n")
        self.assertTrue(r["success"], r)
        self.assertEqual((r["inseridas"], r["ignoradas"]), (1, 1))
        estado = self.client.get("/api/admin/prazos-cep").get_json()
        self.assertEqual((estado["total"], estado["ligado"], estado["contagem"]), (1, False, "corridos"))   # comeca desligado

        with patch.object(portal, "buscar_rastreio_publico", return_value=self.resultado()):
            d = self.client.post("/api/rastrear", json={"codigo": "PED9"}).get_json()
            self.assertEqual(d["previsao"], "")                                   # desligado: nada para o cliente
            sim = self.client.get("/api/admin/prazos-cep/simular?codigo=PED9").get_json()
        esperado = (self.cadastro + timedelta(days=10)).strftime("%d/%m/%Y")
        self.assertEqual((sim["cep"], sim["dias"], sim["prazo"], sim["motivo"]), ("30140071", 10, esperado, ""))
        self.assertEqual(sim["cliente_veria"], esperado)

        self.assertTrue(self.client.post("/api/admin/prazos-cep/config", json={"ligado": True}).get_json()["ligado"])
        with patch.object(portal, "buscar_rastreio_publico", return_value=self.resultado()):
            d = self.client.post("/api/rastrear", json={"codigo": "PED9"}).get_json()
        self.assertEqual(d["previsao"], esperado)
        with patch.object(portal, "buscar_rastreio_publico", return_value=self.resultado("ENTREGUE")):
            self.assertEqual(self.client.post("/api/rastrear", json={"codigo": "PED9"}).get_json()["previsao"], "")

    def test_prazo_vencido_nunca_aparece(self):
        self.importar("cep_inicial;cep_final;dias\n30000000;39999999;0\n")
        self.client.post("/api/admin/prazos-cep/config", json={"ligado": True})
        velho = self.resultado()
        velho["ocorrencias"] = [{"codigoOcorrencia": "1", "dtOcorrencia": "2026-01-01 09:00:00"}]
        with patch.object(portal, "buscar_rastreio_publico", return_value=velho):
            d = self.client.post("/api/rastrear", json={"codigo": "PED9"}).get_json()
        self.assertEqual(d["previsao"], "")
        self.assertNotIn("atras", str(d).lower())

    def test_sem_cep_ou_fora_da_tabela_nao_inventa(self):
        self.importar("cep_inicial;cep_final;dias\n01000000;05999999;2\n")
        self.client.post("/api/admin/prazos-cep/config", json={"ligado": True})
        with patch.object(portal, "buscar_rastreio_publico", return_value=self.resultado()):
            self.assertEqual(self.client.post("/api/rastrear", json={"codigo": "PED9"}).get_json()["previsao"], "")
            sim = self.client.get("/api/admin/prazos-cep/simular?codigo=PED9").get_json()
        self.assertEqual(sim["motivo"], "sem prazo confiável para este CEP e cliente")

    def test_prazo_registrado_do_tms_na_pagina_sem_vazar_dado_interno(self):
        conn = portal.get_db_connection()
        prazo = datetime.now().date() + timedelta(days=5)
        P.substituir_prazos_tms(conn, [("PED9", "65949995000187", prazo.isoformat())])
        conn.commit()
        conn.close()
        self.client.post("/api/admin/prazos-cep/config", json={"ligado": True})
        ao_vivo = dict(self.resultado(), cnpjsTms=["65949995000187"], servicoTms="4")
        arquivado = dict(self.resultado(), cnpjCliente="65.949.995/0001-87", ocorrencias=[])
        outro = dict(self.resultado(), cnpjsTms=["11111111000111"])
        for res, esperado in ((ao_vivo, prazo.strftime("%d/%m/%Y")), (arquivado, prazo.strftime("%d/%m/%Y")), (outro, "")):
            with patch.object(portal, "buscar_rastreio_publico", return_value=res):
                d = self.client.post("/api/rastrear", json={"codigo": "PED9"}).get_json()
            self.assertEqual(d["previsao"], esperado)
            self.assertNotIn("cnpj", str(d).lower())
            self.assertNotIn("servicoTms", str(d))
        with patch.object(portal, "buscar_rastreio_publico", return_value=ao_vivo):
            sim = self.client.get("/api/admin/prazos-cep/simular?codigo=PED9").get_json()
        self.assertEqual((sim["prazo"], sim["fonte"], sim["motivo"]), (prazo.strftime("%d/%m/%Y"), "prazo registrado do TMS", ""))
        estado = self.client.get("/api/admin/prazos-cep").get_json()
        self.assertEqual(estado["registrados_tms"], 1)

    def test_cep_do_rastreios_do_portal_quando_a_base_nao_tem(self):
        conn = portal.get_db_connection()
        conn.execute("CREATE TABLE IF NOT EXISTS rastreios (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT)")
        colunas = {r[1] for r in conn.execute("PRAGMA table_info(rastreios)").fetchall()}
        for coluna in ("cnpj_cliente", "cep"):
            if coluna not in colunas:
                conn.execute(f"ALTER TABLE rastreios ADD COLUMN {coluna} TEXT")
        conn.execute("INSERT INTO rastreios (codigo, cnpj_cliente, cep) VALUES ('SIM633', '65949995000187', '30140071')")
        conn.commit()
        conn.close()
        self.addCleanup(self.apagar_rastreio, "SIM633")
        self.importar("cep_inicial;cep_final;dias\n30000000;39999999;10\n")
        self.client.post("/api/admin/prazos-cep/config", json={"ligado": True})
        res = dict(self.resultado(), codigo="SIM633", codigoCliente="SIM633", cnpjsTms=["65949995000187"])
        with patch.object(portal, "buscar_rastreio_publico", return_value=res):
            d = self.client.post("/api/rastrear", json={"codigo": "SIM633"}).get_json()
        self.assertEqual(d["previsao"], (self.cadastro + timedelta(days=10)).strftime("%d/%m/%Y"))
        P._CACHE_CEP.clear()
        res["cnpjsTms"] = ["11111111000111"]                                   # o TMS diz outro cliente: CEP nao serve
        with patch.object(portal, "buscar_rastreio_publico", return_value=res):
            self.assertEqual(self.client.post("/api/rastrear", json={"codigo": "SIM633"}).get_json()["previsao"], "")

    def apagar_rastreio(self, codigo):
        conn = portal.get_db_connection()
        conn.execute("DELETE FROM rastreios WHERE codigo = ?", (codigo,))
        conn.commit()
        conn.close()

    def test_importa_o_arquivo_do_tms_em_latin1(self):
        cab = "CEP Inicial;CEP Final;Sigla Unidade de Coleta;Sigla do Serviço;Prazo Entrega;Prazo Coleta;Prazo Entrega Ult. Milha;Descrição;"
        linhas = [cab] + [f"86000-001;86124-999;SAO;{s};8;2;2;;" for s in ("ENT_CONV", "ENT_EXP", "LEVE")]
        dados = {"arquivo": (io.BytesIO(("\n".join(linhas) + "\n").encode("latin1")), "abrangencia.csv")}
        r = self.client.post("/api/admin/prazos-cep/importar", data=dados, content_type="multipart/form-data").get_json()
        self.assertTrue(r["success"], r)
        self.assertEqual((r["inseridas"], r["servicos"]), (3, ["ENT_CONV", "ENT_EXP", "LEVE"]))
        conn = portal.get_db_connection()
        self.assertEqual(P.dias_para_cep(conn, "86010000"), 8)
        conn.close()

    def test_contagem_e_acesso_restrito(self):
        self.assertEqual(self.client.post("/api/admin/prazos-cep/config", json={"contagem": "uteis"}).get_json()["contagem"], "uteis")
        self.assertEqual(self.client.post("/api/admin/prazos-cep/config", json={"contagem": "x"}).status_code, 400)
        anonimo = portal.app.test_client()
        self.assertEqual(anonimo.get("/api/admin/prazos-cep").status_code, 401)
        self.assertEqual(anonimo.get("/api/admin/prazos-cep/simular?codigo=PED9").status_code, 401)


if __name__ == "__main__":
    unittest.main()
