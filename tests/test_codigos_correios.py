"""Tela do admin 'Codigos dos Correios': grava rastreios.codigo_correios e o portal passa a mostrar o botao dos Correios."""
import os
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import MagicMock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _m in ("pandas", "openpyxl", "openpyxl.styles", "openpyxl.utils"):
    sys.modules.setdefault(_m, MagicMock())
os.environ.setdefault("SECRET_KEY", "teste-local")
os.chdir(tempfile.mkdtemp())
_c = sqlite3.connect("database.db")
_c.execute("CREATE TABLE IF NOT EXISTS rastreios (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT)")
_c.commit()
_c.close()
sys.path.insert(0, ROOT)
import app as portal  # noqa: E402


class CodigosCorreiosTest(unittest.TestCase):
    def setUp(self):
        conn = sqlite3.connect("database.db")
        colunas = [r[1] for r in conn.execute("PRAGMA table_info(rastreios)")]
        if "codigo_correios" not in colunas:
            conn.execute("ALTER TABLE rastreios ADD COLUMN codigo_correios TEXT")
        conn.execute("""CREATE TABLE IF NOT EXISTS log_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER, nome_usuario TEXT,
            tipo_importacao TEXT, nome_arquivo TEXT, inseridos INTEGER, atualizados INTEGER,
            ignorados INTEGER, data_hora TEXT)""")
        conn.execute("DELETE FROM rastreios")
        conn.execute("INSERT INTO rastreios (codigo) VALUES ('OMLTCO4BFTYE8QC'), ('OMLTAAAA00001')")
        conn.commit()
        conn.close()
        self.client = portal.app.test_client()

    def _logar(self, is_admin):
        with self.client.session_transaction() as sess:
            sess["usuario_id"] = 1
            sess["usuario_nome"] = "Teste"
            sess["is_admin"] = is_admin

    def test_interpreta_formatos_colados(self):
        pares, invalidas = portal.interpretar_codigos_correios(
            "OMLTCO4BFTYE8QC\tAD943406192BR\n"
            "ad111111111br ; omltaaaa00001\n"
            "\n"
            "OMLTX=AD222222222BR\n"
            "linha sem codigo\n"
        )
        self.assertEqual(pares, {
            "OMLTCO4BFTYE8QC": "AD943406192BR",
            "OMLTAAAA00001": "AD111111111BR",
            "OMLTX": "AD222222222BR",
        })
        self.assertEqual(invalidas, ["linha sem codigo"])

    def test_admin_grava_e_portal_mostra_botao(self):
        self._logar(1)
        resp = self.client.post("/api/admin/codigos-correios", json={
            "texto": "OMLTCO4BFTYE8QC AD943406192BR\nNAOEXISTE123 AD333333333BR",
        })
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["gravados"], [{"pedido": "OMLTCO4BFTYE8QC", "correios": "AD943406192BR"}])
        self.assertEqual(data["nao_encontrados"], ["NAOEXISTE123"])

        resultado = portal.anexar_rastreio_terceiro({"codigo": "OMLTCO4BFTYE8QC"})
        self.assertEqual(resultado["rastreioTerceiro"], {"codigoTerceiro": "AD943406192BR"})

    def test_quem_nao_e_admin_nao_grava(self):
        self._logar(0)
        resp = self.client.post("/api/admin/codigos-correios", json={"texto": "OMLTCO4BFTYE8QC AD943406192BR"})
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(portal.buscar_codigo_correios_manual("OMLTCO4BFTYE8QC"), "")

    def test_sem_login_nao_grava(self):
        resp = self.client.post("/api/admin/codigos-correios", json={"texto": "OMLTCO4BFTYE8QC AD943406192BR"})
        self.assertEqual(resp.status_code, 401)


if __name__ == "__main__":
    unittest.main()
