import os
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _m in ("pandas", "openpyxl", "openpyxl.styles", "openpyxl.utils"):
    sys.modules.setdefault(_m, MagicMock())  # importação de planilha não é usada aqui
os.environ.setdefault("SECRET_KEY", "teste-local")
os.chdir(tempfile.mkdtemp())  # banco descartável
_c = sqlite3.connect("database.db")
_c.execute("CREATE TABLE IF NOT EXISTS rastreios (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT)")
_c.commit()
_c.close()
sys.path.insert(0, ROOT)
import app as portal  # noqa: E402

CASOS = {
    "CAOA1": "preparacao_transporte",
    "CAOA2": "em_rota_entrega",
    "CAOA3": "atencao",
    "CAOA4": "devolucao",
}


class DemoCaoaTest(unittest.TestCase):
    def setUp(self):
        self.client = portal.app.test_client()

    def test_cada_codigo_devolve_o_status_esperado(self):
        for codigo, status in CASOS.items():
            with self.subTest(codigo=codigo):
                r = self.client.post("/api/rastrear", json={"codigo": codigo, "cliente": "caoa"})
                self.assertEqual(r.status_code, 200)
                d = r.get_json()
                self.assertTrue(d["ok"])
                self.assertEqual(d["status"], status)
                self.assertTrue(d["stages"])
                self.assertTrue(d["history"])
                self.assertTrue(d["cliente"])

    def test_etapas_ate_o_status_atual_tem_data(self):
        d = self.client.post("/api/rastrear", json={"codigo": "CAOA2", "cliente": "caoa"}).get_json()
        com_data = [s["key"] for s in d["stages"] if s["date"]]
        self.assertIn("em_rota_entrega", com_data)
        self.assertIn("aguardando_postagem", com_data)

    def test_codigo_comum_nao_e_demo(self):
        self.assertIsNone(portal._resposta_demo_caoa("ABC123"))

    def test_codigo_desconhecido_segue_o_fluxo_normal(self):
        with patch.object(portal, "buscar_rastreio_publico", return_value=None) as busca:
            r = self.client.post("/api/rastrear", json={"codigo": "CAOA9", "cliente": "caoa"})
        self.assertEqual(r.status_code, 404)
        busca.assert_called_once()

    def test_demo_nao_consulta_banco_nem_tms(self):
        with patch.object(portal, "buscar_rastreio_publico", side_effect=AssertionError("nao deveria consultar")):
            r = self.client.post("/api/rastrear", json={"codigo": "CAOA1", "cliente": "caoa"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()["demo"])

    def test_demo_so_vale_na_pagina_do_caoa(self):
        for cliente in ("ccxp", "panini", ""):
            with self.subTest(cliente=cliente), patch.object(portal, "buscar_rastreio_publico", return_value=None):
                r = self.client.post("/api/rastrear", json={"codigo": "CAOA4", "cliente": cliente})
            self.assertEqual(r.status_code, 404)


if __name__ == "__main__":
    unittest.main()
