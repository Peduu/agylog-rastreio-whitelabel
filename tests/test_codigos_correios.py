"""Tela do admin 'Codigos dos Correios': grava rastreios.codigo_correios e o portal passa a mostrar o botao dos Correios."""
import os
import sqlite3
import sys
import tempfile
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch

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
        portal._TOTAL_EXPRESS_CACHE.clear()
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

    def test_interpreta_csv_total(self):
        conteudo = (
            "Pedido,ID Redespacho,Redespacho\n"
            "OMLTCO4BFTYE8QC,123,AD943406192BR\n"
            "OMLTCO7QHQHLTSC,456,AD943409123BR\n"
        ).encode("cp1252")
        pares, invalidas, conflitos, total = portal.interpretar_csv_total(conteudo)
        self.assertEqual(pares, {
            "OMLTCO4BFTYE8QC": "AD943406192BR",
            "OMLTCO7QHQHLTSC": "AD943409123BR",
        })
        self.assertEqual(invalidas, [])
        self.assertEqual(conflitos, {})
        self.assertEqual(total, 2)

    def test_csv_total_nao_grava_conflito(self):
        conteudo = (
            "Pedido;Redespacho\n"
            "OMLTCO4BFTYE8QC;AD943406192BR\n"
            "OMLTCO4BFTYE8QC;AD943409123BR\n"
        ).encode("utf-8")
        pares, invalidas, conflitos, total = portal.interpretar_csv_total(conteudo)
        self.assertEqual(pares, {})
        self.assertEqual(invalidas, [])
        self.assertEqual(conflitos, {
            "OMLTCO4BFTYE8QC": ["AD943406192BR", "AD943409123BR"],
        })
        self.assertEqual(total, 2)

    def test_admin_importa_csv_total(self):
        self._logar(1)
        conteudo = (
            "Pedido,Redespacho\n"
            "OMLTCO4BFTYE8QC,AD943406192BR\n"
            "NAOEXISTE123,AD333333333BR\n"
        ).encode("utf-8")
        resp = self.client.post(
            "/api/admin/codigos-correios",
            data={"arquivo": (BytesIO(conteudo), "relatorio_total.csv")},
            content_type="multipart/form-data",
        )
        data = resp.get_json()
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["gravados"], [
            {"pedido": "OMLTCO4BFTYE8QC", "correios": "AD943406192BR"},
        ])
        self.assertEqual(data["nao_encontrados"], ["NAOEXISTE123"])
        self.assertEqual(data["total_linhas"], 2)

    def test_csv_total_exige_colunas_corretas(self):
        self._logar(1)
        resp = self.client.post(
            "/api/admin/codigos-correios",
            data={"arquivo": (BytesIO(b"Pedido,Codigo\nOMLTCO4BFTYE8QC,AD943406192BR\n"), "invalido.csv")},
            content_type="multipart/form-data",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Pedido e Redespacho", resp.get_json()["message"])

    def test_simplecompany_recebe_codigo_correios(self):
        conn = sqlite3.connect("database.db")
        conn.execute(
            "UPDATE rastreios SET codigo_correios = ? WHERE codigo = ?",
            ("AD943406192BR", "OMLTCO4BFTYE8QC"),
        )
        conn.commit()
        conn.close()

        resultado = {
            "codigo": "OMLTCO4BFTYE8QC",
            "statusBadge": "EM ROTA",
            "ocorrencias": [],
        }
        with (
            patch.object(portal, "_buscar_nome_pedido_simplecompany", return_value="Cliente Teste"),
            patch.object(portal, "_excedeu_limite_consulta_publica", return_value=False),
            patch.object(portal, "buscar_rastreio_na_api", return_value=resultado),
        ):
            resp = self.client.post(
                "/api/rastrear/simplecompany",
                json={"codigo": "OMLTCO4BFTYE8QC", "nome": "Cliente Teste"},
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.get_json()["rastreioTerceiro"],
            {"codigoTerceiro": "AD943406192BR"},
        )

        pagina = self.client.get("/tracking/simplecompany/OMLTCO4BFTYE8QC")
        self.assertEqual(pagina.status_code, 200)
        self.assertIn(b'id="correiosTracking"', pagina.data)

    def test_total_extrai_apenas_evento_do_pedido_exato(self):
        payload = {"data": [
            {"pedido": "OUTRO", "tracking": [
                {"descricao": "REDESPACHADO CORREIO - AD111111111BR"}]},
            {"pedido": "OMLTCO4BFTYE8QC", "tracking": [
                {"descricao": "MOVIMENTAÇÃO AD222222222BR"},
                {"descricao": "REDESPACHADO CORREIO - AD943406192BR"}]},
        ]}
        self.assertEqual(
            portal.extrair_codigo_correios_total(payload, "OMLTCO4BFTYE8QC"),
            "AD943406192BR",
        )
        payload["data"][1]["tracking"].append(
            {"descricao": "REDESPACHADO CORREIO - AD943409123BR"}
        )
        self.assertEqual(portal.extrair_codigo_correios_total(payload, "OMLTCO4BFTYE8QC"), "")

    def test_total_automatico_alimenta_portal_e_usa_cache(self):
        resposta = MagicMock(status_code=200)
        resposta.json.return_value = {"data": [{
            "pedido": "OMLTCO4BFTYE8QC",
            "tracking": [{"descricao": "REDESPACHADO CORREIO - AD943406192BR"}],
        }]}
        with (
            patch.object(portal, "TOTAL_EXPRESS_API_USER", "usuario-teste"),
            patch.object(portal, "TOTAL_EXPRESS_API_PASSWORD", "senha-teste"),
            patch.object(portal.requests, "post", return_value=resposta) as post,
        ):
            resultado = portal.anexar_rastreio_terceiro({"codigo": "OMLTCO4BFTYE8QC"})
            self.assertEqual(resultado["rastreioTerceiro"], {"codigoTerceiro": "AD943406192BR"})
            self.assertEqual(portal.buscar_codigo_correios_total("OMLTCO4BFTYE8QC"), "AD943406192BR")
            post.assert_called_once()
            self.assertEqual(post.call_args.kwargs["json"]["pedidos"], ["OMLTCO4BFTYE8QC"])

    def test_total_falha_sem_expor_credencial_e_preserva_manual(self):
        conn = sqlite3.connect("database.db")
        conn.execute(
            "UPDATE rastreios SET codigo_correios = ? WHERE codigo = ?",
            ("AD943406192BR", "OMLTCO4BFTYE8QC"),
        )
        conn.commit()
        conn.close()
        with (
            patch.object(portal, "TOTAL_EXPRESS_API_USER", "usuario-teste"),
            patch.object(portal, "TOTAL_EXPRESS_API_PASSWORD", "senha-teste"),
            patch.object(portal.requests, "post", side_effect=portal.requests.Timeout),
        ):
            resultado = portal.anexar_rastreio_terceiro({"codigo": "OMLTCO4BFTYE8QC"})
        self.assertEqual(resultado["rastreioTerceiro"], {"codigoTerceiro": "AD943406192BR"})
        self.assertNotIn("OMLTCO4BFTYE8QC", portal._TOTAL_EXPRESS_CACHE)

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
