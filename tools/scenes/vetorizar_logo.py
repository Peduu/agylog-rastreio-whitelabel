"""Vetoriza o logo de um cliente (PNG -> caminhos SVG) com o potrace, que acha quinas e curvas sem "espinhos" nem ondulacao.

Uso: python tools/scenes/vetorizar_logo.py caoa pinbank ...   (sem argumentos: todos)
Grava/atualiza tools/scenes/logos_vetor.py. So o build precisa de `pip install potracer pillow numpy scipy`; o portal nao.

Como funciona: cada cor vira uma mascara de cobertura (as bordas herdam a cor cheia mais proxima). A fonte e levada a uma largura de trabalho
(LARG): fontes com anti-aliasing sobem ou descem ate ela com filtro suave; fontes com alpha so 0/255 (serrilhadas) NAO sao ampliadas (ampliar so
amplifica a escada). A cor de cada pixel de borda vem misturada com o fundo, entao so o miolo das formas define a cor.
A camada base e a silhueta inteira, para nao haver frestas entre cores.
"""
import json
import os
import sys

import numpy as np
import potrace
from PIL import Image
from scipy.ndimage import binary_dilation, binary_erosion, distance_transform_edt

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
LARG = 800            # largura de trabalho (px) das fontes com anti-aliasing (sobem ou descem ate ela); as serrilhadas ficam no tamanho nativo


def _hex(rgb):
    return "#%02X%02X%02X" % tuple(int(round(v)) for v in rgb)


def _d(curvas):
    partes = []
    for c in curvas:
        p = c.start_point
        partes.append(f"M{p.x:.1f},{p.y:.1f}")
        for seg in c.segments:
            if seg.is_corner:
                partes.append(f"L{seg.c.x:.1f},{seg.c.y:.1f}L{seg.end_point.x:.1f},{seg.end_point.y:.1f}")
            else:
                partes.append(f"C{seg.c1.x:.1f},{seg.c1.y:.1f} {seg.c2.x:.1f},{seg.c2.y:.1f} {seg.end_point.x:.1f},{seg.end_point.y:.1f}")
        partes.append("Z")
    return "".join(partes)


def vetorizar(png, paleta, opcoes=None):
    """paleta: cores aproximadas (RGB) na ordem de pintura; a primeira e a base. Retorna (largura, altura, [(hex, d), ...])."""
    opcoes = opcoes or {}
    im = Image.open(png).convert("RGBA")
    a = np.array(im).astype(float)
    alpha = a[:, :, 3] / 255
    rgb = a[:, :, :3]
    if "alpha" in opcoes:                                              # logo sobre fundo liso: a cobertura sai da cor
        alpha = opcoes["alpha"](rgb)
    serrilhado = len(np.unique((alpha * 255).astype(int))) <= 3
    cheio = alpha >= .75
    pal = np.array(paleta, float)
    cls = np.argmin(((rgb[:, :, None, :] - pal[None, None, :, :]) ** 2).sum(axis=3), axis=2)
    interior = binary_erosion(cheio, iterations=2 if alpha.shape[1] >= 600 else 1)   # a cor da borda vem misturada com o fundo: classifica so o miolo
    if not interior.any():
        interior = cheio
    _, idx = distance_transform_edt(~interior, return_indices=True)     # a borda herda a classe do miolo mais proximo
    cls = cls[idx[0], idx[1]]
    ys, xs = np.where(alpha >= .5)                                      # recorta a margem transparente
    y0, y1, x0, x1 = max(ys.min() - 1, 0), min(ys.max() + 2, alpha.shape[0]), max(xs.min() - 1, 0), min(xs.max() + 2, alpha.shape[1])
    alpha, cls, rgb, cheio = alpha[y0:y1, x0:x1], cls[y0:y1, x0:x1], rgb[y0:y1, x0:x1], cheio[y0:y1, x0:x1]
    h0, w0 = alpha.shape
    esc = 1.0 if serrilhado else LARG / w0
    w, h = max(1, int(round(w0 * esc))), max(1, int(round(h0 * esc)))
    cores = [_hex(np.median(rgb[cheio & (cls == i)], axis=0)) if (cheio & (cls == i)).any() else _hex(pal[i]) for i in range(len(pal))]
    base = cls == 0
    perto = binary_dilation(base, iterations=2)
    saida = []
    for i in range(len(pal)):
        cov = alpha * ((base | ((cls != 0) & perto)) if i == 0 else (cls == i))
        if esc != 1.0:
            cov = np.array(Image.fromarray((cov * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS), dtype=float) / 255
        mask = cov >= .5
        curvas = potrace.Bitmap(~mask).trace(turdsize=max(4, int(w * h / 40000)), alphamax=1.0, opticurve=True, opttolerance=0.4)   # o potracer inverte a entrada
        d = _d(curvas)
        if d:
            saida.append((cores[i], d))
    return w, h, saida


CLIENTES = {
    "caoa": ("static/logos/logo-caoa.png", [(14, 1, 73), (103, 201, 152)]),
    "brb": ("static/logos/logo-brb-card-trim.png", [(252, 252, 252), (16, 181, 229)]),
    "brbdux": ("static/logos/logo-brbdux-trim.png", [(252, 252, 252)]),
    "inter": ("static/logos/logo-inter.png", [(255, 255, 255)], {"alpha": lambda c: np.clip(c[:, :, 2] / 255, 0, 1)}),   # so o "inter" branco (o laranja e o fundo)
    "tricard": ("static/logos/logo-tricard-header-white.png", [(252, 252, 252), (72, 232, 200)]),
    "pinbank": ("static/logos/logo-pinbank-real.png", [(245, 166, 35), (0, 255, 255)]),
    "ip2w": ("static/logos/logo-ip2w.png", [(252, 252, 252), (62, 207, 192)]),
    "ccxp": ("static/logos/logo-ccxp.png", [(252, 252, 252), (227, 55, 129)]),
}

if __name__ == "__main__":
    alvo = os.path.join(AQUI, "logos_vetor.py")
    dados = {}
    if os.path.exists(alvo):
        ns = {}
        exec(open(alvo, encoding="utf-8").read(), ns)
        dados = ns.get("LOGOS", {})
    for nome in (sys.argv[1:] or CLIENTES):
        arq, paleta, *resto = CLIENTES[nome]
        w, h, caminhos = vetorizar(os.path.join(RAIZ, arq), paleta, resto[0] if resto else None)
        dados[nome] = dict(w=w, h=h, paths=caminhos)
        print(nome, w, h, [len(d) for _, d in caminhos], "bytes de caminho")
    with open(alvo, "w", encoding="utf-8", newline="\n") as f:
        f.write('"""GERADO por tools/scenes/vetorizar_logo.py - logos em vetor (nao editar a mao)."""\n\nLOGOS = ')
        f.write(json.dumps(dados, ensure_ascii=False, indent=1))
        f.write("\n")
