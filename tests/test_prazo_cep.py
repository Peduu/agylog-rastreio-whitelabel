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
        self.assertEqual(P.normalizar_cep(None), "")

    def test_ler_faixas_ignora_linha_ruim(self):
        faixas, ign = P.ler_faixas([
            {"CEP Inicial": "01000-000", "CEP Final": "05999-999", "Dias": "2"},
            {"cep_inicial": "30000000", "cep_final": "39999999", "prazo": "10"},
            {"cep_inicial": "50000000", "cep_final": "40000000", "dias": "3"},   # invertida
            {"cep_inicial": "", "cep_final": "1", "dias": "x"},
        ])
        self.assertEqual(faixas, [("01000000", "05999999", 2), ("30000000", "39999999", 10)])
        self.assertEqual(ign, 2)

    def test_faixa_mais_estreita_e_dias(self):
        c = sqlite3.connect(":memory:")
        P.criar_tabelas(c)
        P.substituir_faixas(c, [("30000000", "39999999", 10), ("30100000", "30199999", 3)])
        self.assertEqual(P.dias_para_cep(c, "30140071"), 3)
        self.assertEqual(P.dias_para_cep(c, "35000000"), 10)
        self.assertIsNone(P.dias_para_cep(c, "01310100"))

    def test_somar_dias(self):
        sexta = date(2026, 10, 16)
        self.assertEqual(P.somar_dias(sexta, 3), date(2026, 10, 19))
        self.assertEqual(P.somar_dias(sexta, 3, uteis=True), date(2026, 10, 21))   # pula sabado e domingo

    def test_cadastro_e_a_ocorrencia_1(self):
        oc = [{"codigoOcorrencia": "28", "dtOcorrencia": "2026-09-25 08:00:00"},
              {"codigoOcorrencia": "1", "dtOcorrencia": "2026-09-24 13:50:00"}]
        self.assertEqual(P.data_cadastro_tms(oc), date(2026, 9, 24))
        self.assertEqual(P.data_cadastro_tms([{"codigoOcorrencia": "28", "dtOcorrencia": "2026-09-25 08:00:00"}]), date(2026, 9, 25))
        self.assertIsNone(P.data_cadastro_tms([]))

    def test_cep_do_pedido_so_leitura(self):
        caminho = banco_modelos([("AR1", "632", "06000-000", "2026-09-24 13:40:00"), ("AR2", "777", "", "2026-09-24 13:40:00")])
        self.assertEqual(P.cep_do_pedido(caminho, ["632"]), "06000000")
        self.assertEqual(P.cep_do_pedido(caminho, ["XYZ", "AR1"]), "06000000")      # tambem pelo AR
        self.assertEqual(P.cep_do_pedido(caminho, ["777"]), "")                     # sem CEP: sem prazo
        self.assertEqual(P.cep_do_pedido("/nao/existe.db", ["632"]), "")

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
        conn.execute("DELETE FROM prazos_cep")
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
        self.assertEqual(sim["motivo"], "CEP fora de todas as faixas da tabela")

    def test_contagem_e_acesso_restrito(self):
        self.assertEqual(self.client.post("/api/admin/prazos-cep/config", json={"contagem": "uteis"}).get_json()["contagem"], "uteis")
        self.assertEqual(self.client.post("/api/admin/prazos-cep/config", json={"contagem": "x"}).status_code, 400)
        anonimo = portal.app.test_client()
        self.assertEqual(anonimo.get("/api/admin/prazos-cep").status_code, 401)
        self.assertEqual(anonimo.get("/api/admin/prazos-cep/simular?codigo=PED9").status_code, 401)


if __name__ == "__main__":
    unittest.main()
