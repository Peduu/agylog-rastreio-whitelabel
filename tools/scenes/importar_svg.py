"""Importa um logo que JA E VETOR (SVG oficial) para o formato de logos_vetor.py, sem rasterizar nem retracar.

Aplica de forma exata as translacoes (transform="translate(...)") dos grupos e elementos nas coordenadas
absolutas dos caminhos; <rect> (com rx/ry) vira caminho. Outras transformacoes (scale, rotate, matrix)
nao sao suportadas e geram erro, para nunca sair um logo torto em silencio.
"""
import re
import xml.etree.ElementTree as ET

_NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_ARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}
_TRANSLATE = re.compile(r"^\s*translate\(\s*([-+.\deE]+)(?:[\s,]+([-+.\deE]+))?\s*\)\s*$")


def _fmt(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _tokens(d):
    """Comandos e numeros; nos arcos as flags (4o e 5o parametro) sao um caractere so ('a1 1 0 00-2 2' e valido)."""
    out, i, cmd, n = [], 0, None, 0
    while i < len(d):
        ch = d[i]
        if ch.isalpha():
            cmd, n = ch, 0
            out.append(ch)
            i += 1
        elif ch in " ,\t\r\n":
            i += 1
        elif cmd and cmd.upper() == "A" and n % 7 in (3, 4):
            out.append(ch)
            i += 1
            n += 1
        else:
            m = _NUM.match(d, i)
            if not m:
                raise ValueError(f"caminho invalido perto de {d[i:i + 20]!r}")
            out.append(m.group())
            i = m.end()
            n += 1
    return out


def transladar(d, dx, dy):
    """Soma (dx, dy) nas coordenadas absolutas do caminho; comandos relativos nao mudam."""
    if not dx and not dy:
        return " ".join(_tokens(d))
    out, cmd, n, primeiro = [], None, 0, True
    for t in _tokens(d):
        if t.isalpha():
            cmd, n = t, 0
            out.append(t)
            continue
        up = cmd.upper()
        k = n % _ARGS[up] if _ARGS[up] else 0
        absoluto = cmd.isupper() or (primeiro and cmd == "m" and n < 2)   # o 1o 'm' de um caminho e absoluto
        v = float(t)
        if absoluto:
            if up in ("M", "L", "T", "C", "S", "Q"):
                v += dx if k % 2 == 0 else dy
            elif up == "H":
                v += dx
            elif up == "V":
                v += dy
            elif up == "A" and k in (5, 6):
                v += dx if k == 5 else dy
        out.append(t if (up == "A" and k in (3, 4)) else _fmt(v))
        n += 1
        if cmd.lower() == "m" and n >= 2:
            primeiro = False
    return " ".join(out)


def _rect(el):
    x, y = float(el.get("x", 0)), float(el.get("y", 0))
    w, h = float(el.get("width")), float(el.get("height"))
    rx = el.get("rx")
    ry = el.get("ry")
    rx = float(rx if rx is not None else (ry or 0))
    ry = float(ry if ry is not None else rx)
    rx, ry = min(rx, w / 2), min(ry, h / 2)
    if not rx:
        return f"M{_fmt(x)} {_fmt(y)} H{_fmt(x + w)} V{_fmt(y + h)} H{_fmt(x)} Z"
    return (f"M{_fmt(x + rx)} {_fmt(y)} H{_fmt(x + w - rx)} A{_fmt(rx)} {_fmt(ry)} 0 0 1 {_fmt(x + w)} {_fmt(y + ry)} "
            f"V{_fmt(y + h - ry)} A{_fmt(rx)} {_fmt(ry)} 0 0 1 {_fmt(x + w - rx)} {_fmt(y + h)} H{_fmt(x + rx)} "
            f"A{_fmt(rx)} {_fmt(ry)} 0 0 1 {_fmt(x)} {_fmt(y + h - ry)} V{_fmt(y + ry)} A{_fmt(rx)} {_fmt(ry)} 0 0 1 {_fmt(x + rx)} {_fmt(y)} Z")


def _cor(c):
    c = (c or "#000").strip()
    if re.fullmatch(r"#[0-9a-fA-F]{3}", c):
        c = "#" + "".join(ch * 2 for ch in c[1:])
    return c.upper()


def importar(arquivo, cores=None):
    """Retorna (largura, altura, [(cor, d), ...]) na ordem de pintura. cores troca uma cor oficial por outra ({'#000000': '#0B1B3F'})."""
    cores = {_cor(k): v for k, v in (cores or {}).items()}
    raiz = ET.parse(arquivo).getroot()
    vb = [float(v) for v in raiz.get("viewBox").replace(",", " ").split()]
    if vb[0] or vb[1]:
        raise ValueError("viewBox com origem diferente de 0 0 nao suportado")
    saida = []

    def visitar(el, dx, dy, fill):
        tf = el.get("transform")
        if tf:
            m = _TRANSLATE.match(tf)
            if not m:
                raise ValueError(f"transformacao nao suportada: {tf}")
            dx, dy = dx + float(m.group(1)), dy + float(m.group(2) or 0)
        fill = el.get("fill", fill)
        tag = el.tag.split("}")[-1]
        if tag == "path":
            saida.append((cores.get(_cor(fill), _cor(fill)), transladar(el.get("d"), dx, dy)))
        elif tag == "rect":
            saida.append((cores.get(_cor(fill), _cor(fill)), transladar(_rect(el), dx, dy)))
        elif tag in ("g", "svg"):
            for filho in el:
                visitar(filho, dx, dy, fill)
        elif tag not in ("title", "desc", "defs"):
            raise ValueError(f"elemento nao suportado: {tag}")

    visitar(raiz, 0.0, 0.0, raiz.get("fill", "#000"))
    return vb[2], vb[3], saida
