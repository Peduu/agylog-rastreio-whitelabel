"""Fidelidade dos dados do mapinha (exigencia do Pedro, 08/10/2026): se esta escrito Curitiba, o ponto esta em Curitiba.

Confere a tabela de municipios (sede, IBGE) contra os contornos das UFs que o navegador desenha: os mesmos dados,
na mesma ordem lon/lat, tem que concordar entre si.
"""
import json
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def carregar():
    with open(os.path.join(RAIZ, "data", "municipios.json"), encoding="utf-8") as f:
        municipios = [dict(uf=uf, nome=nome, lat=lat, lon=lon, capital=cap == 1) for uf, nome, lat, lon, cap in json.load(f)]
    pasta = os.path.join(RAIZ, "static", "data", "uf")
    with open(os.path.join(pasta, "indice.json"), encoding="utf-8") as f:
        indice = json.load(f)
    ufs = {}
    for uf in indice:
        with open(os.path.join(pasta, f"{uf}.json"), encoding="utf-8") as f:
            ufs[uf] = json.load(f)
    return municipios, ufs, indice


def dentro(lon, lat, aneis):
    """Ray casting (par/impar) somando todos os aneis da UF."""
    dentro_ = False
    for anel in aneis:
        j = len(anel) - 1
        for i in range(len(anel)):
            xi, yi = anel[i]
            xj, yj = anel[j]
            if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
                dentro_ = not dentro_
            j = i
    return dentro_


def dist_borda(lon, lat, aneis):
    melhor = float("inf")
    for anel in aneis:
        for (x1, y1), (x2, y2) in zip(anel, anel[1:] + anel[:1]):
            dx, dy = x2 - x1, y2 - y1
            t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((lon - x1) * dx + (lat - y1) * dy) / (dx * dx + dy * dy)))
            px, py = x1 + t * dx, y1 + t * dy
            melhor = min(melhor, ((lon - px) ** 2 + (lat - py) ** 2) ** 0.5)
    return melhor


class FidelidadeGeoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.municipios, cls.ufs, cls.indice = carregar()
        cls.por_nome = {(m["uf"], m["nome"]): m for m in cls.municipios}

    def test_indice_cobre_cada_contorno(self):
        for uf, (x0, y0, x1, y1) in self.indice.items():
            for anel in self.ufs[uf]:
                for lon, lat in anel:
                    self.assertTrue(x0 <= lon <= x1 and y0 <= lat <= y1, uf)

    def test_todos_os_municipios_e_as_27_ufs(self):
        self.assertEqual(len(self.municipios), 5571)
        self.assertEqual(len(self.ufs), 27)
        self.assertEqual({m["uf"] for m in self.municipios}, set(self.ufs))

    def test_capitais_dentro_da_propria_uf(self):
        capitais = [m for m in self.municipios if m["capital"]]
        self.assertEqual(len(capitais), 27)
        for m in capitais:
            self.assertTrue(dentro(m["lon"], m["lat"], self.ufs[m["uf"]]), f'{m["nome"]}/{m["uf"]} fora da UF')

    def test_quase_todos_os_municipios_dentro_da_uf_ou_colados_na_borda(self):
        fora = [m for m in self.municipios if not dentro(m["lon"], m["lat"], self.ufs[m["uf"]])]
        longe = [f'{m["nome"]}/{m["uf"]}' for m in fora if dist_borda(m["lon"], m["lat"], self.ufs[m["uf"]]) > 0.05]
        self.assertLessEqual(len(fora), len(self.municipios) // 100, f"{len(fora)} fora da UF")
        self.assertEqual(longe, [], "sede longe da propria UF")

    def test_curitiba_e_curitiba_nao_guarapuava(self):
        ctba = self.por_nome[("PR", "Curitiba")]
        gpv = self.por_nome[("PR", "Guarapuava")]
        self.assertAlmostEqual(ctba["lat"], -25.42, delta=0.05)
        self.assertAlmostEqual(ctba["lon"], -49.27, delta=0.05)
        self.assertGreaterEqual(ctba["lon"] - gpv["lon"], 2.0)
        self.assertTrue(dentro(ctba["lon"], ctba["lat"], self.ufs["PR"]))
        self.assertFalse(dentro(ctba["lon"], ctba["lat"], self.ufs["SC"]))

    def test_cidades_das_unidades_dentro_da_uf(self):
        for uf, nome in (("SP", "São Paulo"), ("PR", "Curitiba"), ("PR", "Londrina"), ("RS", "Porto Alegre"),
                         ("SC", "Florianópolis"), ("DF", "Brasília"), ("RJ", "Rio de Janeiro"), ("MG", "Belo Horizonte")):
            m = self.por_nome[(uf, nome)]
            self.assertTrue(dentro(m["lon"], m["lat"], self.ufs[uf]), f"{nome}/{uf}")


if __name__ == "__main__":
    unittest.main()
