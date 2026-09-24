"""Vetoriza o logo de um cliente (PNG -> caminhos SVG) para ficar nitido em qualquer tamanho nas cenas.

Uso: python tools/scenes/vetorizar_logo.py caoa
Grava/atualiza tools/scenes/logos_vetor.py. So o build precisa de `pip install scikit-image scipy pillow numpy`; o portal nao.

Como funciona: cada cor vira uma mascara (as bordas herdam a cor cheia mais proxima); o contorno sai por marching squares com precisao de
sub-pixel e e suavizado. Depois o contorno vira geometria limpa: quinas reconstruidas por intersecao de retas, trechos retos viram linhas
(ajustadas por minimos quadrados) e trechos curvos viram poucos beziers cubicos (ajuste de Schneider) com tangente continua. Assim o logo
sai limpo mesmo o PNG original tendo a borda serrilhada (alpha so 0 ou 255).
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter, gaussian_filter1d
from skimage import measure

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
SIGMA = 1.3          # suavizacao da mascara (px do arquivo) antes de achar o contorno
SUAV = 4.0           # suavizacao do contorno (amostras de 1 px)
ANG = 38             # graus: acima disso o ponto e uma quina
RETO_JAN, RETO_DEV, RETO_MIN = 16, .35, 22      # janela, desvio maximo (px) e comprimento minimo de um trecho reto
TOL = .45            # erro maximo (px) do ajuste dos beziers


def _reamostrar(pts, passo=1.0):
    p = np.vstack([pts, pts[:1]])
    seg = np.hypot(*np.diff(p, axis=0).T)
    acum = np.concatenate([[0], np.cumsum(seg)])
    n = max(8, int(acum[-1] / passo))
    t = np.linspace(0, acum[-1], n, endpoint=False)
    return np.column_stack([np.interp(t, acum, p[:, 0]), np.interp(t, acum, p[:, 1])])


def _suavizar(p, sigma):
    return np.column_stack([gaussian_filter1d(p[:, k], sigma, mode="wrap") for k in (0, 1)])


def _unit(v):
    n = np.hypot(*v)
    return v / n if n > 1e-9 else v


def _reta(pts):
    """Reta de minimos quadrados; direcoes a menos de 3 graus da horizontal/vertical sao encaixadas (o desenho original e ortogonal ali)."""
    c = pts.mean(axis=0)
    _, _, vt = np.linalg.svd(pts - c)
    d = vt[0] if vt[0][0] > 0 or (vt[0][0] == 0 and vt[0][1] > 0) else -vt[0]
    if abs(d[1]) < .052:
        d = np.array([1.0, 0.0])
    elif abs(d[0]) < .052:
        d = np.array([0.0, 1.0])
    return c, d


def _dist_reta(pts, c, d):
    r = pts - c
    return np.abs(r[:, 0] * d[1] - r[:, 1] * d[0])


def _quinas(p, k=8):
    n = len(p)
    v1 = p - np.roll(p, k, axis=0)
    v2 = np.roll(p, -k, axis=0) - p
    ang = np.degrees(np.abs(np.arctan2(v1[:, 0] * v2[:, 1] - v1[:, 1] * v2[:, 0], (v1 * v2).sum(axis=1))))
    cand = [i for i in range(n) if ang[i] > ANG and ang[i] == ang[np.arange(i - 10, i + 11) % n].max()]
    return sorted(cand)


def _retos(R):
    """Intervalos (ini, fim) de R onde o contorno e reto."""
    m = len(R)
    ok = np.zeros(m, bool)
    for i in range(m):
        a, b = max(0, i - RETO_JAN), min(m, i + RETO_JAN + 1)
        if b - a < 2 * RETO_JAN * .6:
            continue
        c, d = _reta(R[a:b])
        ok[i] = _dist_reta(R[a:b], c, d).max() < RETO_DEV
    out, i = [], 0
    while i < m:
        if ok[i]:
            j = i
            while j + 1 < m and ok[j + 1]:
                j += 1
            if j - i + 1 >= RETO_MIN:
                out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out


def _bez(P0, P1, P2, P3, u):
    u = u[:, None]
    return (1 - u) ** 3 * P0 + 3 * (1 - u) ** 2 * u * P1 + 3 * (1 - u) * u ** 2 * P2 + u ** 3 * P3


def _ajustar(pts, t0, t1):
    """Ajuste de Schneider: pts de P0 a P3, t0 = tangente saindo de P0, t1 = tangente saindo de P3 (para dentro da curva). Lista de beziers."""
    P0, P3 = pts[0], pts[-1]
    m = len(pts)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    u = np.concatenate([[0], np.cumsum(seg)])
    L = u[-1]
    if m < 3 or L < 1e-6:
        return [(P0, P0 + (P3 - P0) / 3, P3 - (P3 - P0) / 3, P3)]
    u = u / L
    b0, b1, b2, b3 = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u ** 2, u ** 3
    A1, A2 = t0[None, :] * b1[:, None], t1[None, :] * b2[:, None]
    C = np.array([[(A1 * A1).sum(), (A1 * A2).sum()], [(A1 * A2).sum(), (A2 * A2).sum()]])
    tmp = pts - (P0[None, :] * (b0 + b1)[:, None] + P3[None, :] * (b2 + b3)[:, None])
    X = np.array([(A1 * tmp).sum(), (A2 * tmp).sum()])
    det = C[0, 0] * C[1, 1] - C[0, 1] * C[1, 0]
    dist = np.hypot(*(P3 - P0))
    a1 = a2 = dist / 3
    if abs(det) > 1e-9:
        a1 = (X[0] * C[1, 1] - X[1] * C[0, 1]) / det
        a2 = (C[0, 0] * X[1] - C[1, 0] * X[0]) / det
    if a1 < dist * .01 or a2 < dist * .01 or a1 > dist * 1.5 or a2 > dist * 1.5:
        a1 = a2 = dist / 3
    P1, P2 = P0 + t0 * a1, P3 + t1 * a2
    err = np.hypot(*(_bez(P0, P1, P2, P3, u) - pts).T)
    if err.max() <= TOL or m <= 6:
        return [(P0, P1, P2, P3)]
    k = int(np.clip(err.argmax(), 3, m - 4))
    tc = _unit(pts[min(k + 4, m - 1)] - pts[max(k - 4, 0)])
    return _ajustar(pts[:k + 1], t0, -tc) + _ajustar(pts[k:], tc, t1)


def _fmt(q):
    return f"{q[0]:.2f},{q[1]:.2f}"


def _partes(R):
    """Divide o trecho R em pecas: ('r', c, d, ini, fim) retas e ('c', ini, fim) curvas."""
    m = len(R)
    pecas, cur = [], 0
    for s, e in _retos(R):
        if s > cur + 1:
            pecas.append(["c", cur, s])
        c, d = _reta(R[s:e + 1])
        pecas.append(["r", c, d, s, e])
        cur = e
    if cur < m - 2:
        pecas.append(["c", cur, m - 1])
    return pecas


def _proj(q, c, d):
    return c + d * np.dot(q - c, d)


def _interseccao(c1, d1, c2, d2, fallback):
    mat = np.array([d1, -d2]).T
    if abs(np.linalg.det(mat)) < .15:
        return fallback
    t = np.linalg.solve(mat, c2 - c1)
    q = c1 + d1 * t[0]
    return q if np.hypot(*(q - fallback)) < 8 else fallback


CURTO, CANTO = 50, 14   # runs menores que CURTO viram uma reta; nas maiores ignora-se CANTO amostras junto de cada quina (a suavizacao as arredonda)


def _caminho(p, quinas):
    n = len(p)
    if quinas:
        idx_q = list(quinas)
    else:                                                              # contorno liso fechado: corta no meio do maior trecho reto
        rot = _retos(np.vstack([p, p[:RETO_JAN]]))
        i0 = 0
        if rot:
            s, e = max(rot, key=lambda x: x[1] - x[0])
            i0 = ((s + e) // 2) % n
        idx_q = [i0]
    k = len(idx_q)
    runs, pecas, aparadas = [], [], []
    for j in range(k):
        a, b = idx_q[j], idx_q[(j + 1) % k]
        ids = np.arange(a, b if b > a else b + n) % n if quinas else np.arange(a, a + n) % n
        R = np.concatenate([p[ids], [p[b % n]]])
        runs.append(R)
        L = len(R)
        if quinas and L < CURTO:
            c, d = _reta(R[4:L - 4] if L > 12 else R)
            pecas.append([["r", c, d, 0, L - 1]])
            aparadas.append(R)
        else:
            Rt = R[CANTO:L - CANTO] if quinas else R
            aparadas.append(Rt)
            pecas.append(_partes(Rt))
    vert = []
    for j in range(k):
        fb = p[idx_q[j]]
        ant, pos = pecas[j - 1], pecas[j]
        Ra, Rp = aparadas[j - 1], aparadas[j]
        ra = ant[-1] if ant and ant[-1][0] == "r" and ant[-1][4] >= len(Ra) - 1 - 22 else None
        rp = pos[0] if pos and pos[0][0] == "r" and pos[0][3] <= 22 else None
        if quinas:
            if ra is None:
                c, d = _reta(Ra[-14:])
                ra = ["r", c, d]
            if rp is None:
                c, d = _reta(Rp[:14])
                rp = ["r", c, d]
            vert.append(_interseccao(ra[1], ra[2], rp[1], rp[2], fb))
        else:
            vert.append(_proj(fb, rp[1], rp[2]) if rp is not None else fb)
    d_out = "M" + _fmt(vert[0])
    for j in range(k):
        R, P = aparadas[j], pecas[j]
        v0, v1 = vert[j], vert[(j + 1) % k]
        m = len(R)
        nos = []
        for it, pc in enumerate(P):
            if pc[0] == "r":
                _, c, d, s, e = pc
                a_ = v0 if (it == 0 and s <= 22) else _proj(R[s], c, d)
                b_ = v1 if (it == len(P) - 1 and e >= m - 1 - 22) else _proj(R[e], c, d)
                nos.append((a_, b_, _unit(b_ - a_) if np.hypot(*(b_ - a_)) > 1e-6 else d))
            else:
                nos.append(None)
        for it, pc in enumerate(P):
            if pc[0] == "r":
                a_, b_, _ = nos[it]
                if it == 0 and not np.allclose(a_, v0):
                    d_out += "L" + _fmt(a_)
                elif it > 0 and P[it - 1][0] == "r":
                    d_out += "L" + _fmt(a_)
                d_out += "L" + _fmt(b_)
            else:
                ini, fim = pc[1], pc[2]
                pts = R[ini:fim + 1].copy()
                ant, prox = (nos[it - 1] if it > 0 else None), (nos[it + 1] if it + 1 < len(P) else None)
                if ant is not None:
                    pts[0] = ant[1]
                elif it == 0 and quinas:
                    d_out += "L" + _fmt(pts[0])
                if prox is not None:
                    pts[-1] = prox[0]
                t0 = ant[2] if ant is not None else _unit(pts[min(6, len(pts) - 1)] - pts[0])
                t1 = -prox[2] if prox is not None else _unit(pts[max(-7, -len(pts))] - pts[-1])
                for (_, Q1, Q2, Q3) in _ajustar(pts, t0, t1):
                    d_out += f"C{_fmt(Q1)} {_fmt(Q2)} {_fmt(Q3)}"
                if prox is None and quinas:
                    d_out += "L" + _fmt(v1)
        if not P:
            d_out += "L" + _fmt(v1)
    return d_out + "Z"


def _contornos(cov):
    campo = np.pad(gaussian_filter(cov.astype(float), SIGMA), 2)
    partes = []
    for c in measure.find_contours(campo, .5):
        pts = _reamostrar(np.column_stack([c[:, 1] - 2 + .5, c[:, 0] - 2 + .5]))     # (x, y), centro do pixel
        if len(pts) < 12:
            continue
        pts = _suavizar(pts, SUAV)
        partes.append(_caminho(pts, _quinas(pts)))
    return "".join(partes)


def vetorizar(png, cores):
    """cores: lista de (hex, funcao(rgb)->bool) que reconhece cada cor nos pixels cheios (alpha > 90%). Retorna (largura, altura, [(hex, d), ...])."""
    im = Image.open(png).convert("RGBA")
    w, h = im.size
    a = np.array(im).astype(float)
    alpha = a[:, :, 3] / 255
    rgb = a[:, :, :3].astype(int)
    cheio = alpha > .9
    zonas = []
    for _, sel in cores:                                               # zona de cada cor = pixels cheios da cor, engordados 4 px
        z = Image.fromarray(((cheio & sel(rgb)) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
        zonas.append(np.array(z) > 0)
    saida = []
    for i, (hexa, _) in enumerate(cores):
        outras = np.zeros_like(zonas[0])
        for j, z in enumerate(zonas):
            if j != i:
                outras |= z
        dono = zonas[i] & ~(outras & ~zonas[i])
        saida.append((hexa, _contornos((alpha * dono).astype(np.float32))))
    return w, h, saida


CLIENTES = {
    "caoa": ("static/logos/logo-caoa.png", [
        ("#0E0149", lambda c: (c.sum(axis=2) < 330)),                    # azul-marinho das letras
        ("#67C998", lambda c: c[:, :, 1] > c[:, :, 0] + 60),             # verde dos acentos
    ]),
}

if __name__ == "__main__":
    alvo = os.path.join(AQUI, "logos_vetor.py")
    dados = {}
    if os.path.exists(alvo):
        ns = {}
        exec(open(alvo, encoding="utf-8").read(), ns)
        dados = ns.get("LOGOS", {})
    for nome in (sys.argv[1:] or CLIENTES):
        arq, cores = CLIENTES[nome]
        w, h, caminhos = vetorizar(os.path.join(RAIZ, arq), cores)
        dados[nome] = dict(w=w, h=h, paths=caminhos)
        print(nome, w, h, [len(d) for _, d in caminhos], "bytes de caminho")
    with open(alvo, "w", encoding="utf-8", newline="\n") as f:
        f.write('"""GERADO por tools/scenes/vetorizar_logo.py - logos em vetor (nao editar a mao)."""\n\nLOGOS = ')
        f.write(json.dumps(dados, ensure_ascii=False, indent=1))
        f.write("\n")
