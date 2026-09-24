"""Regra de negocio: o CCXP NAO tem devolucao nem 'devolvido'. Nada disso pode sair da API publica do CCXP (status, etapas, historico)."""
import json
import os
import sqlite3
import sys
import tempfile
import unicodedata
import unittest
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

# (statusBadge do TMS, texto da ultima ocorrencia)
ENTRADAS = [
    ("DEVOLVIDO", "Devolvido ao remetente"),
    ("DEVOLVIDO", ""),
    ("EM DEVOLUÇÃO", "Pedido em retorno ao remetente"),
    ("DEVOLUÇÃO EM ROTA", ""),
    ("DEVOLUÇÃO COM PENDÊNCIA", ""),
    ("CUSTODIA", "DEVOLUCAO REALIZADA"),
    ("PENDENTE", "Não entregue por CEP incorreto - volume não entregue"),
    ("REENTREGAR", "Tratamento de pendência: REENTREGAR"),
    ("EM ROTA", "Entrega não realizada, devolução agendada"),
    ("ENTREGUE", "Entregue ao destinatário"),
]


def _sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").lower()


class CcxpSemDevolucaoTest(unittest.TestCase):
    def setUp(self):
        self.client = portal.app.test_client()

    def _consultar(self, badge, ultimo, cliente="ccxp"):
        resultado = {"statusBadge": badge, "ultimoStatus": ultimo, "dataBaixa": "16/09/2026 10:05", "previsao": "17/09/2026",
                     "codigoCliente": "CCXP-TESTE", "datasEtapas": {}}
        with patch.object(portal, "buscar_rastreio_publico", return_value=resultado), \
                patch.object(portal, "_excedeu_limite_consulta_publica", return_value=False):
            r = self.client.post("/api/rastrear", json={"codigo": "TESTE123", "cliente": cliente})
        self.assertEqual(r.status_code, 200, (badge, ultimo))
        return r.get_json()

    def test_nenhuma_resposta_do_ccxp_menciona_devolucao(self):
        for badge, ultimo in ENTRADAS:
            with self.subTest(badge=badge, ultimo=ultimo):
                d = self._consultar(badge, ultimo)
                self.assertNotIn("devol", _sem_acento(json.dumps(d, ensure_ascii=False)), d)
                self.assertNotIn(d["status"], ("devolucao", "devolvido"))
                self.assertFalse({"devolucao", "devolvido"} & {s["key"] for s in d["stages"]})

    def test_devolucao_vira_insucesso_com_tratativa(self):
        for badge, ultimo in ENTRADAS[:7]:
            with self.subTest(badge=badge):
                d = self._consultar(badge, ultimo)
                self.assertIn(d["status"], ("ccxp_aguardando_tratativa", "ccxp_tratado"))

    def test_outros_clientes_continuam_com_devolucao(self):
        d = self._consultar("DEVOLVIDO", "", cliente="panini")
        self.assertEqual(d["status"], "devolvido")

    def test_cenas_do_ccxp_nao_tem_devolucao(self):
        with open(os.path.join(ROOT, "static", "scenes", "ccxp.js"), encoding="utf-8") as f:
            txt = f.read()
        self.assertNotIn("devol", _sem_acento(txt))


if __name__ == "__main__":
    unittest.main()
