"""/api/rastrear devolve a localizacao publica (cartao "Onde esta seu pedido")."""
import json
import unittest
from unittest.mock import MagicMock, patch

from test_demo_caoa import portal


def texto(loc):
    partes = [c["t"] for c in loc["linha"]] + (["em trânsito"] if loc["transito"] else [])
    return " → ".join(partes)


class LocalizacaoApiTest(unittest.TestCase):
    def setUp(self):
        self.client = portal.app.test_client()
        limiter = patch.object(portal, "_excedeu_limite_consulta_publica", return_value=False)
        limiter.start()
        self.addCleanup(limiter.stop)

    def consulta(self, codigo, cliente):
        r = self.client.post("/api/rastrear", json={"codigo": codigo, "cliente": cliente})
        self.assertEqual(r.status_code, 200)
        return r.get_json()

    def test_demonstracao_por_status(self):
        with patch.object(portal, "buscar_rastreio_publico", side_effect=AssertionError("consulta real")):
            self.assertIsNone(self.consulta("ROTA1", "paranabanco")["localizacao"])
            self.assertEqual(texto(self.consulta("ROTA2", "paranabanco")["localizacao"]), "São Paulo/SP")
            loc = self.consulta("ROTA3", "paranabanco")["localizacao"]
            self.assertEqual(texto(loc), "São Paulo/SP → Curitiba/PR")
            self.assertEqual([p["papel"] for p in loc["pontos"]], ["origem", "atual"])
            self.assertEqual(texto(self.consulta("ROTA4", "brb")["localizacao"]), "São Paulo/SP → Londrina/PR")
            self.assertEqual(texto(self.consulta("ROTA5", "brb")["localizacao"]), "São Paulo/SP → Londrina/PR")
            self.assertEqual(texto(self.consulta("ROTA9", "caoa")["localizacao"]), "São Paulo/SP → Londrina/PR")

    def test_liberado_para_todos_e_volta_ao_modo_demo_pela_variavel(self):
        self.assertEqual(portal.LOCALIZACAO_PUBLICA, "todos")                # padrao desde 15/10/2026
        with patch.object(portal, "buscar_rastreio_publico", side_effect=AssertionError("consulta real")):
            self.assertIsNotNone(self.consulta("AGY5", "paranabanco")["localizacao"])
            self.assertIsNone(self.consulta("AGY1", "paranabanco")["localizacao"])      # aguardando postagem: sem cidade
            with patch.object(portal, "LOCALIZACAO_PUBLICA", "demo"):
                for n in range(1, 10):
                    self.assertIsNone(self.consulta(f"AGY{n}", "paranabanco")["localizacao"], f"AGY{n}")
                self.assertIsNotNone(self.consulta("ROTA5", "paranabanco")["localizacao"])
            d = self.consulta("rota3", "paranabanco")
            self.assertTrue(d["demo"])
            self.assertIn("ROTA3", d["cliente"])
            self.assertEqual(d["status"], "transferencia_franquia")

    def test_previsao_de_entrega_na_resposta(self):
        with patch.object(portal, "buscar_rastreio_publico", side_effect=AssertionError("consulta real")):
            d = self.consulta("ROTA3", "paranabanco")
            self.assertRegex(d["previsao"], r"^\d{2}/\d{2}/\d{4}$")
            self.assertIn(f'previsão · {d["previsao"][:5]}', json.dumps(d["localizacao"], ensure_ascii=False))
            self.assertEqual(self.consulta("AGY9", "paranabanco")["previsao"], "")   # entregue: sem previsao
            self.assertEqual(self.consulta("AGY6", "brb")["previsao"], "")           # tentativa: sem previsao
            r = self.client.post("/api/rastrear/simplecompany", json={"codigo": "AGY5", "nome": "Demonstração AGY"})
            self.assertRegex(r.get_json()["previsao"], r"^\d{2}/\d{2}/\d{4}$")

    def test_ccxp_sem_devolucao_na_localizacao(self):
        with patch.object(portal, "buscar_rastreio_publico", side_effect=AssertionError("consulta real")):
            for codigo in ("ROTA6", "ROTA7", "ROTA8"):
                d = self.consulta(codigo, "ccxp")
                self.assertEqual(texto(d["localizacao"]), "São Paulo/SP → Londrina/PR", codigo)
                bruto = json.dumps(d, ensure_ascii=False).lower()
                self.assertNotIn("devol", bruto)
                self.assertNotIn("remetente", bruto)

    def test_consulta_real_usa_cidade_do_tms_e_nunca_lat_lon(self):
        tms = {"flagErro": False, "listaResultados": [
            {"dtOcorrencia": "2026-10-06 14:20:00", "codigoOcorrencia": "28", "descricaoOcorrencia": "Recebimento de volumes para entrega",
             "unidadeOcorrencia": "SAO", "nomeCidade": "SAO PAULO", "uf": "SP", "latitude": "-23.987654", "longitude": "-46.123456"},
            {"dtOcorrencia": "2026-10-07 09:10:00", "codigoOcorrencia": "17", "descricaoOcorrencia": "Recebimento de transferencia entre unidades",
             "unidadeOcorrencia": "CWB", "nomeCidade": "CURITIBA", "uf": "PR", "latitude": "-25.111111", "longitude": "-49.999999"},
        ]}
        resp = MagicMock(status_code=200)
        resp.json.return_value = tms
        with patch.object(portal.requests, "post", return_value=resp), \
                patch.object(portal, "calcular_previsao_api", return_value=""):   # previsao le o banco; nao e o foco aqui
            resultado = portal._consultar_tms_api({"listaPedidos": ["X"]}, "PEDIDO", "X", "00000000000000", {})
        self.assertEqual([(o["cidade"], o["uf"], o["unidade"]) for o in resultado["ocorrenciasLocal"]],
                         [("SAO PAULO", "SP", "SAO"), ("CURITIBA", "PR", "CWB")])
        with patch.object(portal, "buscar_rastreio_publico", return_value=resultado), \
                patch.object(portal, "converter_status_publico", return_value="transferencia_franquia"):
            with patch.object(portal, "LOCALIZACAO_PUBLICA", "demo"):
                self.assertIsNone(self.consulta("PEDIDOREAL1", "paranabanco")["localizacao"])   # modo demo: so nos ROTA
            d = self.consulta("PEDIDOREAL1", "paranabanco")
        self.assertEqual(texto(d["localizacao"]), "São Paulo/SP → Curitiba/PR")
        bruto = json.dumps(d)
        for proibido in ("23.987654", "46.123456", "25.111111", "49.999999", "latitude", "longitude"):
            self.assertNotIn(proibido, bruto)


if __name__ == "__main__":
    unittest.main()
