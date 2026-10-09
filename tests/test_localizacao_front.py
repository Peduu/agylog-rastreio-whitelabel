"""Cartao de localizacao no navegador (static/localizacao.js): cores do mapa = cores das cenas de cada cliente."""
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "scenes"))
import scenes  # noqa: E402


def cores_do_mapa():
    with open(os.path.join(ROOT, "static", "localizacao.js"), encoding="utf-8") as f:
        js = f.read()
    bloco = re.search(r"const CORES = \{(.*?)\n  \};", js, re.S).group(1)
    return {c: {"acento": a, "tinta": t, "painel": p} for c, a, t, p in re.findall(
        r"(\w+): \{ acento: '(#[0-9A-Fa-f]{6})', tinta: '(#[0-9A-Fa-f]{6})', painel: '(#[0-9A-Fa-f]{6})' \}", bloco)}


class CoresDoMapaTest(unittest.TestCase):
    def test_todo_cliente_com_as_cores_do_tema(self):
        cores = cores_do_mapa()
        for c, k in scenes.KITS.items():
            self.assertIn(c, cores, f"{c} sem cores no mapa")
            self.assertEqual(cores[c], {"acento": k["accent"], "tinta": k["ink"], "painel": k["panel"]}, c)

    def test_pagina_padrao_tem_cores(self):
        self.assertIn("agy", cores_do_mapa())

    def test_sem_cena_de_rota(self):
        with open(os.path.join(ROOT, "static", "localizacao.js"), encoding="utf-8") as f:
            js = f.read()
        self.assertNotIn("-rota.js", js)
        self.assertNotIn("innerHTML = String", js)              # nome de cidade nunca vai para innerHTML


if __name__ == "__main__":
    unittest.main()
