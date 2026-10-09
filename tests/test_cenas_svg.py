"""Cenas SVG por cliente: os arquivos em static/scenes devem estar em dia com o gerador e respeitar as regras do portal."""
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "scenes"))
import scenes  # noqa: E402

STATUS = ["aguardando_postagem", "preparacao_transporte", "transferencia_franquia", "chegada_franquia", "em_rota_entrega",
          "atencao", "devolucao", "devolvido", "entregue"]


def ler(*partes):
    with open(os.path.join(ROOT, *partes), encoding="utf-8") as f:
        return f.read()


def carregar(cliente):
    txt = ler("static", "scenes", f"{cliente}.js")
    ini = txt.index("= {") + 2
    return json.loads(txt[ini:txt.rindex("};") + 1])


class CenasSvgTest(unittest.TestCase):
    def test_arquivos_em_dia_com_o_gerador(self):
        for c in scenes.KITS:
            self.assertEqual(carregar(c), scenes.scenes_for(c), f"{c}.js desatualizado: rode python tools/scenes/build.py")

    def test_status_por_cliente(self):
        for c in scenes.KITS:
            esperado = set(STATUS) - scenes.SEM_CENA.get(c, set())
            self.assertEqual(set(carregar(c)), esperado, c)

    def test_ccxp_nao_tem_devolucao_nem_problemas(self):
        self.assertEqual(set(STATUS) - set(carregar("ccxp")), {"atencao", "devolucao", "devolvido"})

    def test_regras_das_cenas(self):
        for c in scenes.KITS:
            for sid, svg in carregar(c).items():
                tag = f"{c}/{sid}"
                self.assertTrue(svg.startswith("<svg") and svg.endswith("</svg>"), tag)
                self.assertNotRegex(svg, r"(?i)<script|onload=|onclick=|javascript:", tag)
                self.assertIn('role="img"', svg, tag)
                self.assertIn("prefers-reduced-motion", svg, tag)
                # so recursos locais (CSP do portal: img-src 'self' data:)
                for u in re.findall(r'(?:href|src)="([^"#][^"]*)"', svg):
                    self.assertTrue(u.startswith("/static/logos/"), f"{tag}: recurso externo {u}")
                    self.assertTrue(os.path.exists(os.path.join(ROOT, u.split("?")[0].lstrip("/"))), f"{tag}: {u} nao existe")
                self.assertLess(len(svg), 40 * 1024, f"{tag}: cena grande demais")
                # ids unicos e prefixados por cena (varias cenas nunca convivem, mas o prefixo evita colisao com o resto da pagina)
                ids = re.findall(r' id="([^"]+)"', svg)
                self.assertEqual(len(ids), len(set(ids)), f"{tag}: ids repetidos")
                pref = scenes.prefixo(c, sid)
                self.assertTrue(all(i.startswith(pref) for i in ids), f"{tag}: id sem prefixo {pref}")
                # texto so no balao do insucesso
                textos = re.findall(r"<text[^>]*>(.*?)</text>", svg)
                if sid == "atencao":
                    self.assertTrue(any("Insucesso" in t for t in textos), tag)
                else:
                    self.assertEqual(textos, [], f"{tag}: cena sem texto")

    def test_manifesto_inclui_tudo(self):
        man = ler("deploy", "deploy-manifest.tsv")
        for c in scenes.KITS:
            self.assertIn(f"static/scenes/{c}.js\t", man, c)
        for arq in ("logo-panini-cena.png", "logo-panini-cena-s.png"):
            self.assertIn(f"static/logos/{arq}\t", man, arq)

    def test_portal_conhece_todos_os_clientes(self):
        js = ler("static", "tracking_publico.js")
        lista = re.search(r"CLIENTES_COM_CENAS = \[(.*?)\]", js).group(1)
        self.assertEqual(set(re.findall(r"'([a-z0-9]+)'", lista)), set(scenes.KITS))


if __name__ == "__main__":
    unittest.main()
