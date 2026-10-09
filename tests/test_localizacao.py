"""localizacao.py: localizacao publica do pedido a partir das ocorrencias do TMS (spec 08/10/2026, texto simples 09/10)."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import localizacao as L  # noqa: E402

SAO = ("SAO PAULO", "SP")
CWB = ("CURITIBA", "PR")
LDB = ("LONDRINA", "PR")


def oc(data, cidade_uf, unidade="SAO", lat="", lon="", codigo="17"):
    cidade, uf = cidade_uf
    return {"dtOcorrencia": data, "nomeCidade": cidade, "uf": uf, "unidadeOcorrencia": unidade,
            "latitude": lat, "longitude": lon, "codigoOcorrencia": codigo, "descricaoOcorrencia": "x"}


def rota(*paradas):
    """Ocorrencias do TMS ja no formato de ocorrencias_com_local, uma por parada, um dia depois da outra."""
    return L.ocorrencias_com_local([oc(f"2026-10-0{6 + i} 14:20:00", p) for i, p in enumerate(paradas)])


def texto(loc):
    """A linha como o cliente le: cidades com seta entre elas."""
    partes = [c["t"] for c in loc["linha"]] + (["em trânsito"] if loc["transito"] else [])
    return " → ".join(partes)


def bandeira(loc):
    return [c["uf"] for c in loc["linha"] if c["atual"]]


class NormalizacaoTests(unittest.TestCase):
    def test_normalizar(self):
        self.assertEqual(L.normalizar("São Paulo"), "SAO PAULO")
        self.assertEqual(L.normalizar("  sao   paulo "), "SAO PAULO")
        self.assertEqual(L.normalizar("Santa Bárbara d'Oeste"), "SANTA BARBARA D OESTE")

    def test_localizar_cidade_so_com_nome_e_uf_exatos(self):
        c = L.localizar_cidade("CURITIBA", "pr")
        self.assertEqual((c["cidade"], c["uf"]), ("Curitiba", "PR"))
        self.assertAlmostEqual(c["lat"], -25.42, delta=0.05)
        self.assertAlmostEqual(c["lon"], -49.26, delta=0.05)
        self.assertEqual(L.localizar_cidade("Sao Paulo", "SP")["cidade"], "São Paulo")
        self.assertIsNone(L.localizar_cidade("Curitiba", "SC"))     # UF errada: nunca chuta outra cidade
        self.assertIsNone(L.localizar_cidade("Curitba", "PR"))      # grafia errada: sem ponto
        self.assertIsNone(L.localizar_cidade("Curitiba", ""))


class OcorrenciasTests(unittest.TestCase):
    def test_ordena_descarta_sem_cidade_e_nao_copia_lat_lon(self):
        lista = [oc("2026-10-07 09:10:00", CWB, "CWB", lat="-1.2345", lon="-2.3456"),
                 oc("2026-10-06 14:20:00", SAO),
                 oc("2026-10-06 15:00:00", ("", "")),
                 oc("data ruim", SAO)]
        r = L.ocorrencias_com_local(lista)
        self.assertEqual([o["cidade"] for o in r], ["SAO PAULO", "CURITIBA"])
        self.assertEqual(r[1]["unidade"], "CWB")
        self.assertNotIn("-1.2345", json.dumps(r))


class MontarTests(unittest.TestCase):
    def test_sem_localizacao(self):
        self.assertIsNone(L.montar_localizacao_publica(rota(SAO), "aguardando_postagem"))
        self.assertIsNone(L.montar_localizacao_publica([], "transferencia_franquia"))
        self.assertIsNone(L.montar_localizacao_publica(rota(SAO), "status_desconhecido"))

    def test_preparacao(self):
        loc = L.montar_localizacao_publica(rota(SAO), "preparacao_transporte")
        self.assertEqual(texto(loc), "São Paulo/SP")
        self.assertEqual(bandeira(loc), ["SP"])
        self.assertEqual([(t["slot"], t["titulo"]) for t in loc["trilho"]], [(2, "São Paulo/SP"), (3, "Destino")])
        self.assertEqual([p["papel"] for p in loc["pontos"]], ["atual"])

    def test_transferencia_saindo_da_origem(self):
        loc = L.montar_localizacao_publica(rota(SAO), "transferencia_franquia")
        self.assertEqual(texto(loc), "São Paulo/SP → em trânsito")
        self.assertEqual(loc["trilho"][0], {"slot": 1, "titulo": "São Paulo/SP", "sub": "saiu · 06/10 14:20"})
        self.assertEqual(loc["trilho"][1]["titulo"], "Unidade de entrega")

    def test_transferencia_em_outra_unidade(self):
        loc = L.montar_localizacao_publica(rota(SAO, CWB), "transferencia_franquia")
        self.assertEqual(texto(loc), "São Paulo/SP → Curitiba/PR")
        self.assertEqual(bandeira(loc), ["PR"])                       # bandeira so do estado onde o pedido ESTA
        self.assertEqual(loc["trilho"][1], {"slot": 2, "titulo": "Curitiba/PR", "sub": "agora · 07/10 14:20"})
        self.assertEqual([p["papel"] for p in loc["pontos"]], ["origem", "atual"])
        self.assertEqual([p["uf"] for p in loc["pontos"]], ["SP", "PR"])
        self.assertEqual([p["nome"] for p in loc["pontos"]], ["São Paulo/SP", "Curitiba/PR"])   # rotulo das cidades no mapa
        self.assertEqual(loc["atualizado"], "07/10 14:20")

    def test_cidade_repetida_em_seguida_vira_uma_parada(self):
        loc = L.montar_localizacao_publica(rota(SAO, SAO, CWB, CWB), "transferencia_franquia")
        self.assertEqual([p["papel"] for p in loc["pontos"]], ["origem", "atual"])

    def test_passagem_aparece_no_mapinha(self):
        loc = L.montar_localizacao_publica(rota(SAO, CWB, LDB), "transferencia_franquia")
        self.assertEqual(texto(loc), "São Paulo/SP → Londrina/PR")
        self.assertEqual([p["papel"] for p in loc["pontos"]], ["origem", "passagem", "atual"])

    def test_chegada(self):
        loc = L.montar_localizacao_publica(rota(SAO, LDB), "chegada_franquia")
        self.assertEqual(texto(loc), "São Paulo/SP → Londrina/PR")
        self.assertEqual(loc["trilho"][2], {"slot": 3, "titulo": "Seu endereço", "sub": "próxima etapa", "icone": "chegada"})
        self.assertEqual([p["papel"] for p in loc["pontos"]], ["origem", "atual", "destino"])

    def test_em_rota(self):
        loc = L.montar_localizacao_publica(rota(SAO, LDB), "em_rota_entrega")
        self.assertEqual(texto(loc), "São Paulo/SP → Londrina/PR")
        self.assertEqual(loc["trilho"][2]["sub"], "em rota · 07/10 14:20")

    def test_tentativa(self):
        loc = L.montar_localizacao_publica(rota(SAO, LDB), "atencao")
        self.assertEqual(texto(loc), "São Paulo/SP → Londrina/PR")
        self.assertEqual(loc["trilho"][2]["sub"], "tentativa · 07/10 14:20")

    def test_entregue_bandeira_xadrez_no_lugar_do_pin(self):
        loc = L.montar_localizacao_publica(rota(SAO, LDB), "entregue")
        self.assertEqual(texto(loc), "São Paulo/SP → Londrina/PR")
        self.assertEqual([p["papel"] for p in loc["pontos"]], ["origem", "destino"])

    def test_entrega_na_mesma_cidade(self):
        loc = L.montar_localizacao_publica(rota(SAO), "em_rota_entrega")
        self.assertEqual(texto(loc), "São Paulo/SP")
        self.assertEqual([p["papel"] for p in loc["pontos"]], ["atual", "destino"])
        self.assertEqual([t["slot"] for t in loc["trilho"]], [2, 3])

    def test_devolucao(self):
        loc = L.montar_localizacao_publica(rota(SAO, CWB), "devolucao")
        self.assertEqual(texto(loc), "São Paulo/SP → Curitiba/PR")
        self.assertEqual([t["slot"] for t in loc["trilho"]], [1, 2])
        self.assertNotIn("destino", [p["papel"] for p in loc["pontos"]])
        self.assertEqual(texto(L.montar_localizacao_publica(rota(SAO, CWB), "devolvido")), "São Paulo/SP → Curitiba/PR")

    def test_ccxp_nunca_devolucao_nem_remetente(self):
        for st in ("atencao", "devolucao", "devolvido"):
            loc = L.montar_localizacao_publica(rota(SAO, CWB), st, "ccxp")
            self.assertEqual(texto(loc), "São Paulo/SP → Curitiba/PR", st)
            bruto = json.dumps(loc, ensure_ascii=False).lower()
            self.assertNotIn("devol", bruto)
            self.assertNotIn("remetente", bruto)

    def test_privacidade_pontos_sao_do_ibge_e_nunca_do_tms(self):
        lista = L.ocorrencias_com_local([oc("2026-10-06 14:20:00", SAO), oc("2026-10-07 09:10:00", CWB, lat="-1.2345", lon="-2.3456")])
        loc = L.montar_localizacao_publica(lista, "transferencia_franquia")
        bruto = json.dumps(loc)
        self.assertNotIn("1.2345", bruto)
        self.assertNotIn("2.3456", bruto)
        atual = loc["pontos"][-1]
        ibge = L.localizar_cidade("Curitiba", "PR")
        self.assertEqual((atual["lat"], atual["lon"]), (ibge["lat"], ibge["lon"]))

    def test_cidade_sem_ibge_entra_no_texto_mas_nao_no_mapa(self):
        loc = L.montar_localizacao_publica(rota(SAO, ("CIDADE QUE NAO EXISTE", "PR")), "transferencia_franquia")
        self.assertEqual(texto(loc), "São Paulo/SP → Cidade Que Nao Existe/PR")
        self.assertEqual(loc["pontos"], [])                           # sem a cidade atual no IBGE nao ha mapinha


if __name__ == "__main__":
    unittest.main()
