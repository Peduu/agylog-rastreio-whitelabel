"""Demonstrações genéricas, isolamento de dados reais e regras por cliente."""
import json
import unittest
from unittest.mock import patch

from test_demo_caoa import portal


class DemoAgyTest(unittest.TestCase):
    def setUp(self):
        self.client = portal.app.test_client()
        limiter = patch.object(portal, "_excedeu_limite_consulta_publica", return_value=False)
        limiter.start()
        self.addCleanup(limiter.stop)

    def test_todos_estados_em_todos_os_temas_sem_consulta_real(self):
        estados = ["aguardando_postagem", "preparacao_transporte", "transferencia_franquia",
                   "chegada_franquia", "em_rota_entrega", "atencao", "devolucao",
                   "devolvido", "entregue", "atencao"]
        with patch.object(portal, "buscar_rastreio_publico", side_effect=AssertionError("Consulta real")):
            for cliente in ("", "caoa", "panini", "tricard", "BRB", "BRBDUX", "pinbank", "inter", "ccxp"):
                for numero, estado in enumerate(estados, 1):
                    with self.subTest(cliente=cliente, codigo=numero):
                        r = self.client.post("/api/rastrear", json={"codigo": f" agy{numero} ", "cliente": cliente})
                        self.assertEqual(r.status_code, 200)
                        d = r.get_json()
                        esperado = estado
                        if cliente == "ccxp":
                            self.assertNotIn("devol", json.dumps(d, ensure_ascii=False).lower())
                            if numero in (6, 7, 8):
                                esperado = "ccxp_aguardando_tratativa"
                            elif numero == 10:
                                esperado = "ccxp_tratado"
                                self.assertEqual(d["kind"], "reenvio")
                        self.assertEqual(d["status"], esperado)
                        self.assertTrue(d["demo"])
                        self.assertIn("DEMONSTRAÇÃO", d["cliente"])
                        self.assertTrue(d["history"])
                        self.assertTrue(any(e["date"] for e in d["stages"] if e["done"]))

    def test_codigos_nao_reservados_continuam_na_consulta_real(self):
        for codigo in ("AGY11", "AGY100", "AGY01", "OMLTCOXUXHTZ4Q"):
            with self.subTest(codigo=codigo), patch.object(portal, "buscar_rastreio_publico", return_value=None) as busca:
                r = self.client.post("/api/rastrear", json={"codigo": codigo, "cliente": "caoa"})
                self.assertEqual(r.status_code, 404)
                busca.assert_called_once_with(codigo, "caoa")

    def test_simplecompany_demo_exige_nome_ficticio_e_nao_consulta_dados_reais(self):
        with patch.object(portal, "_buscar_nome_pedido_simplecompany", side_effect=AssertionError("Banco real")), \
             patch.object(portal, "buscar_rastreio_na_api", side_effect=AssertionError("TMS real")):
            for numero in range(1, 11):
                codigo = f"AGY{numero}"
                hint = self.client.get(f"/api/rastrear/simplecompany/dica?codigo={codigo}")
                self.assertEqual(hint.status_code, 200)
                negado = self.client.post("/api/rastrear/simplecompany", json={"codigo": codigo, "nome": "Outro"})
                self.assertEqual(negado.status_code, 403)
                r = self.client.post("/api/rastrear/simplecompany", json={"codigo": codigo, "nome": "Demonstração AGY"})
                self.assertEqual(r.status_code, 200)
                self.assertTrue(r.get_json()["demo"])

    def test_nome_demo_nao_libera_pedido_real(self):
        with patch.object(portal, "_buscar_nome_pedido_simplecompany", return_value="Pessoa real"), \
             patch.object(portal, "buscar_rastreio_na_api", side_effect=AssertionError("Não deve consultar")):
            r = self.client.post("/api/rastrear/simplecompany", json={"codigo": "PEDIDO123", "nome": "Demonstração AGY"})
            self.assertEqual(r.status_code, 403)

    def test_demo_respeita_limite_de_consultas(self):
        with patch.object(portal, "_excedeu_limite_consulta_publica", return_value=True):
            r = self.client.post("/api/rastrear", json={"codigo": "AGY1", "cliente": "caoa"})
            self.assertEqual(r.status_code, 429)
            self.assertIn("Retry-After", r.headers)


if __name__ == "__main__":
    unittest.main()
