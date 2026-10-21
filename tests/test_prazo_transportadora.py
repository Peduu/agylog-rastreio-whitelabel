"""Previsao das transportadoras (prazo_transportadora.py): Total > Logan > prazo do TMS/CEP, nunca vencida, so a caminho."""
import io
import json
import os
import tempfile
import unittest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

from test_demo_caoa import portal

import prazo_cep as P
import prazo_transportadora as T


def arquivo_logan(pedidos):
    caminho = os.path.join(tempfile.mkdtemp(), "previsoes_logan.json")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump({"atualizado_em": "x", "pedidos": pedidos}, f)
    return caminho


class FuncoesTest(unittest.TestCase):
    def test_data_de(self):
        self.assertEqual(T.data_de("20261024"), date(2026, 10, 24))
        self.assertEqual(T.data_de("2026-10-24"), date(2026, 10, 24))
        self.assertEqual(T.data_de("2026-10-24T00:00:00"), date(2026, 10, 24))
        self.assertEqual(T.data_de("24/10/2026 18:00"), date(2026, 10, 24))
        for ruim in (None, "", "None", "2026-13-01", "20261399", "123", 20261024.5):
            self.assertIsNone(T.data_de(ruim), ruim)

    def test_previsao_total_atualizada_primeiro(self):
        payload = {"data": [
            {"pedido": "OUTRO", "previsaoEntrega": "2026-10-20"},
            {"pedido": "omlt1", "previsaoEntrega": "2026-10-22", "previsaoEntregaAtualizada": "2026-10-25T00:00:00"},
        ]}
        self.assertEqual(T.previsao_total(payload, "OMLT1"), date(2026, 10, 25))
        payload["data"][1]["previsaoEntregaAtualizada"] = None
        self.assertEqual(T.previsao_total(payload, "OMLT1"), date(2026, 10, 22))
        payload["data"][1]["previsaoEntrega"] = None          # como a Total devolvia em 21/10/2026
        self.assertIsNone(T.previsao_total(payload, "OMLT1"))
        self.assertIsNone(T.previsao_total({"data": []}, "OMLT1"))
        self.assertIsNone(T.previsao_total(None, "OMLT1"))

    def test_previsao_logan_do_arquivo_da_rotina(self):
        hoje = date(2026, 10, 21)
        caminho = arquivo_logan({
            "PED1": {"previsao": "2026-10-24", "visto_em": "2026-10-21 10:00:00"},
            "VELHA": {"previsao": "2026-10-24", "visto_em": "2026-10-10 10:00:00"},   # rotina nao reve ha 11 dias
            "AR1": {"previsao": "2026-10-26", "visto_em": "2026-10-21 10:00:00"},
        })
        self.assertEqual(T.previsao_logan(["ped1", None], caminho, hoje), date(2026, 10, 24))
        self.assertIsNone(T.previsao_logan(["VELHA"], caminho, hoje))
        self.assertIsNone(T.previsao_logan(["PED1", "AR1"], caminho, hoje))         # duas datas = nada
        self.assertIsNone(T.previsao_logan(["NAO_TEM"], caminho, hoje))
        self.assertIsNone(T.previsao_logan(["PED1"], os.path.join(tempfile.mkdtemp(), "x.json"), hoje))
        quebrado = os.path.join(tempfile.mkdtemp(), "q.json")
        with open(quebrado, "w") as f:
            f.write("{quebrado")
        self.assertIsNone(T.previsao_logan(["PED1"], quebrado, hoje))

    def test_rele_quando_o_arquivo_muda(self):
        hoje = date(2026, 10, 21)
        caminho = arquivo_logan({"PED1": {"previsao": "2026-10-24", "visto_em": "2026-10-21 10:00:00"}})
        self.assertEqual(T.previsao_logan(["PED1"], caminho, hoje), date(2026, 10, 24))
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump({"pedidos": {"PED1": {"previsao": "2026-10-27", "visto_em": "2026-10-21 11:00:00"}, "PAD": {}}}, f)
        os.utime(caminho, ns=(os.stat(caminho).st_atime_ns, os.stat(caminho).st_mtime_ns + 10_000_000))
        self.assertEqual(T.previsao_logan(["PED1"], caminho, hoje), date(2026, 10, 27))

    def test_primeira_valida_pula_vencida(self):
        hoje = date(2026, 10, 21)
        self.assertEqual(T.primeira_valida([date(2026, 10, 20), None, date(2026, 10, 23)], hoje), date(2026, 10, 23))
        self.assertEqual(T.primeira_valida([date(2026, 10, 21)], hoje), date(2026, 10, 21))
        self.assertIsNone(T.primeira_valida([None, date(2026, 10, 1)], hoje))


class TotalCacheTest(unittest.TestCase):
    def setUp(self):
        portal._TOTAL_EXPRESS_CACHE.clear()
        for nome, valor in (("TOTAL_EXPRESS_API_USER", "u"), ("TOTAL_EXPRESS_API_PASSWORD", "p")):
            p = patch.object(portal, nome, valor)
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(portal._TOTAL_EXPRESS_CACHE.clear)

    def resposta(self, payload):
        r = MagicMock(status_code=200)
        r.json.return_value = payload
        return r

    def test_mesma_consulta_guarda_a_previsao(self):
        payload = {"data": [{"pedido": "OMLT1", "previsaoEntregaAtualizada": "2026-10-25", "tracking": []}]}
        with patch.object(portal.requests, "post", return_value=self.resposta(payload)) as post:
            self.assertEqual(portal.buscar_codigo_correios_total("OMLT1"), "")
            self.assertEqual(portal.previsao_total_em_cache("omlt1"), date(2026, 10, 25))
            portal.buscar_codigo_correios_total("OMLT1")                  # cache: nenhuma consulta a mais
        self.assertEqual(post.call_count, 1)

    def test_sem_previsao_ou_sem_consulta(self):
        self.assertIsNone(portal.previsao_total_em_cache("NUNCA"))
        payload = {"data": [{"pedido": "OMLT2", "previsaoEntrega": None, "previsaoEntregaAtualizada": None}]}
        with patch.object(portal.requests, "post", return_value=self.resposta(payload)):
            portal.buscar_codigo_correios_total("OMLT2")
        self.assertIsNone(portal.previsao_total_em_cache("OMLT2"))


class PaginaTest(unittest.TestCase):
    def setUp(self):
        P._CACHE_CEP.clear()
        portal._TOTAL_EXPRESS_CACHE.clear()
        conn = portal.get_db_connection()
        P.criar_tabelas(conn)
        P.gravar_config(conn, "prazo_cep_ligado", "1")
        conn.commit()
        conn.close()
        self.addCleanup(self.desligar)
        self.client = portal.app.test_client()
        limiter = patch.object(portal, "_excedeu_limite_consulta_publica", return_value=False)
        limiter.start()
        self.addCleanup(limiter.stop)
        self.hoje = datetime.now(P.BRASILIA).date()

    def desligar(self):
        conn = portal.get_db_connection()
        P.gravar_config(conn, "prazo_cep_ligado", "0")
        conn.commit()
        conn.close()
        portal._TOTAL_EXPRESS_CACHE.clear()

    def resultado(self, badge="EM ROTA"):
        return {"codigo": "PED9", "codigoCliente": "PED9", "statusBadge": badge, "ultimoStatus": "x", "dataBaixa": "",
                "ocorrencias": [], "ocorrenciasLocal": [], "datasEtapas": {}}

    def consultar(self, logan, badge="EM ROTA", detalhe_cep=None):
        with patch.object(T, "LOGAN_PREVISOES_FILE", arquivo_logan(logan)), \
                patch.object(portal, "buscar_rastreio_publico", return_value=self.resultado(badge)), \
                patch.object(portal, "_detalhe_prazo", return_value=detalhe_cep):
            return self.client.post("/api/rastrear", json={"codigo": "PED9"}).get_json()

    def logan(self, dias):
        return {"PED9": {"previsao": (self.hoje + timedelta(days=dias)).isoformat(),
                         "visto_em": self.hoje.strftime("%Y-%m-%d 08:00:00")}}

    def test_previsao_da_logan_na_pagina(self):
        d = self.consultar(self.logan(3))
        self.assertEqual(d["previsao"], (self.hoje + timedelta(days=3)).strftime("%d/%m/%Y"))
        self.assertNotIn("logan", json.dumps(d).lower())                    # nada de nome de fonte para o cliente

    def test_vencida_passa_para_o_prazo_do_tms_cep(self):
        cep = {"ligado": True, "prazo": self.hoje + timedelta(days=5), "fonte": "tabela"}
        d = self.consultar(self.logan(-1), detalhe_cep=cep)
        self.assertEqual(d["previsao"], (self.hoje + timedelta(days=5)).strftime("%d/%m/%Y"))
        self.assertEqual(self.consultar(self.logan(-1))["previsao"], "")    # nada valido = nada

    def test_total_vem_antes_da_logan(self):
        portal._TOTAL_EXPRESS_CACHE["PED9"] = (portal.time.monotonic() + 60, "", self.hoje + timedelta(days=2))
        d = self.consultar(self.logan(4))
        self.assertEqual(d["previsao"], (self.hoje + timedelta(days=2)).strftime("%d/%m/%Y"))

    def test_entregue_ou_desligado_nao_mostra(self):
        self.assertEqual(self.consultar(self.logan(3), badge="ENTREGUE")["previsao"], "")
        self.desligar()
        self.assertEqual(self.consultar(self.logan(3))["previsao"], "")

    def test_arquivo_ruim_nao_derruba_a_pagina(self):
        with patch.object(T, "previsao_logan", side_effect=RuntimeError("x")), \
                patch.object(portal, "buscar_rastreio_publico", return_value=self.resultado()), \
                patch.object(portal, "_detalhe_prazo", return_value=None):
            r = self.client.post("/api/rastrear", json={"codigo": "PED9"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["previsao"], "")


if __name__ == "__main__":
    unittest.main()
