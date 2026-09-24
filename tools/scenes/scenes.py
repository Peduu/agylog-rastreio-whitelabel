"""Cenas SVG animadas por cliente (portal de rastreio). Saida: static/scenes/<cliente>.js via tools/scenes/build.py.

Cada cliente e um "kit" (cores, logo, personalidade). As cenas sao as mesmas para todos e usam so o kit.
"""

import math
import random
import re


def _crop(x, y, w, h, W, H):
    """Recorte do logo (em px do arquivo original) + proporcao resultante."""
    return dict(crop=(x, y, w, h, W, H), ar=w / h)


KITS = {
    "panini": dict(name="Panini", pfx="pa", dark=True, panel="#110500", ink="#FFE9A8", accent="#CC0000", onAccent="#FFFFFF",
                   body="#CC0000", cab="#B30000", stripe="#FFD600", plate=None, logo="/static/logos/logo-panini.png?v=2",
                   ar=2000 / 470, prop="packs", glow="#FFD600", sky="fill", door="#FFD600", seal="#FFD600", sealInk="#7a0000"),
    "brb": dict(name="BRB", pfx="bb", dark=True, panel="#0d111a", ink="#BBD4FF", accent="#4d9fff", onAccent="#FFFFFF",
                body="#0d2f6e", bodyStroke="#2f6fd6", cab="#071c47", stripe="#4d9fff", plate="#000000", plateStroke="#4d9fff",
                wall="#0d2f6e", wallOp=".96", wallStroke="#2f6fd6", logo="/static/logos/logo-brb.png?v=2", blend=True,
                prop="cards", glow="#4d9fff", sky="fill", door="#4d9fff", **_crop(70, 171, 387, 173, 512, 512)),
    "inter": dict(name="Inter", pfx="in", dark=True, panel="#110500", ink="#FFD9B8", accent="#FF7A00", onAccent="#FFFFFF",
                  body="#F6EFE8", bodyStroke="#e2d2c2", cab="#FF7A00", stripe="#FF7A00", plate=None,
                  wall="#F6EFE8", wallOp=".92", wallStroke="#e2d2c2", logo="/static/logos/logo-inter.png?v=2", ar=370 / 260,
                  prop="cards", glow="#FF7A00", sky="fill", door="#FF7A00"),
    "brbdux": dict(name="BRB DUX", pfx="bd", dark=True, panel="#000000", ink="#FFFFFF", accent="#FFFFFF", onAccent="#0b0b0e",
                   body="#15151a", bodyStroke="#5a5a64", cab="#0a0a0d", stripe="#FFFFFF", plate="#000000", plateStroke="#FFFFFF",
                   wall="#0f0f13", wallOp=".97", wallStroke="#6a6a74", logo="/static/logos/logo-brbdux.png", blend=True,
                   prop=None, glow="#FFFFFF", sky="fill", door="#b8b8c2", signFill="#2b2b31", **_crop(93, 164, 326, 207, 512, 512)),
    "tricard": dict(name="Tricard", pfx="tr", dark=True, panel="#0d111a", ink="#B7E9E1", accent="#00B8A0", onAccent="#FFFFFF",
                    body="#1B3F7A", bodyStroke="#2a58a6", cab="#132E5C", stripe="#00B8A0", plate="#1B3F7A", plateStroke="#00B8A0",
                    wall="#1B3F7A", wallOp=".96", wallStroke="#2a58a6", logo="/static/logos/logo-tricard-header-white.png",
                    prop="cards", glow="#00B8A0", sky="fill", door="#00B8A0", **_crop(40, 40, 1279, 391, 1359, 471)),
    "pinbank": dict(name="PinBank", pfx="pb", dark=True, panel="#0d111a", ink="#FFE2B0", accent="#F5A623", onAccent="#1a1206",
                    body="#1f2b45", bodyStroke="#3a4a70", cab="#111827", stripe="#F5A623", plate="#111827", plateStroke="#F5A623",
                    wall="#1a2338", wallOp=".96", wallStroke="#3a4a70", logo="/static/logos/logo-pinbank.png",
                    prop="cards", glow="#F5A623", sky="fill", door="#F5A623", signFill="#D9800F", **_crop(105, 42, 391, 125, 600, 202)),
    "ip2w": dict(name="IP2W", pfx="ip", dark=True, panel="#0d111a", ink="#BFF3EC", accent="#3ECFC0", onAccent="#06302c",
                 body="#14283f", bodyStroke="#2b4a6b", cab="#0a1624", stripe="#3ECFC0", plate="#0d1b2a", plateStroke="#3ECFC0",
                 wall="#13263b", wallOp=".96", wallStroke="#2b4a6b", logo="/static/logos/logo-ip2w.png?v=1", ar=925 / 408,
                 prop=None, glow="#3ECFC0", sky="fill", door="#3ECFC0", signFill="#1f9e92"),
    "caoa": dict(name="CAOA", pfx="ca", dark=False, panel="#eef0f6", ink="#100c5a", accent="#5dba8d", onAccent="#FFFFFF",
                 body="#FFFFFF", bodyStroke="#c9cee0", cab="#100c5a", wall="#FFFFFF", wallOp=".92", wallStroke="#c9cee0",
                 stripe="#5dba8d", plate="#FFFFFF", plateStroke="#d5d8e6", logo="/static/logos/logo-caoa.png?v=1", ar=698 / 198,
                 prop="car", glow="#5dba8d", sky="fill", door="#5dba8d"),
    "ccxp": dict(name="CCXP 26", pfx="cx", dark=True, panel="#000000", ink="#FFFFFF", accent="#E33781", onAccent="#FFFFFF",
                 body="#17171d", cab="#101015", stripe="#E33781", plate="#000000", plateStroke="#E33781",
                 logo="/static/logos/logo-ccxp.png?v=1", blend=True, prop="spot", glow="#E33781", sky="outline", door="#E33781",
                 neon=True, wall="#0b0b10", wallOp=".95", wallStroke="#E33781", **_crop(4, 5, 539, 125, 545, 140)),
}

# O CCXP trata os status de problema com a animacao de reenvio propria (resolveCcXpTreatment no front): nao ganha essas cenas.
SEM_CENA = {"ccxp": {"atencao", "devolucao", "devolvido"}}


WARN, RET = "#FFB020", "#E5484D"
SKIN = "#f0c9a6"
GROUND, ROAD_BOTTOM, VEH_Y = 234, 286, 256


CSS = """
.__P__bob{animation:__P__bob .8s ease-in-out infinite}
@keyframes __P__bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-1.6px)}}
.__P__spin{animation:__P__spin .55s linear infinite}
@keyframes __P__spin{to{transform:rotate(360deg)}}
.__P__hand{animation:__P__spin 4s linear infinite}
.__P__dash{stroke-dasharray:18 16;animation:__P__dash .9s linear infinite}
.__P__dashl{stroke-dasharray:18 16;animation:__P__dashl .9s linear infinite}
@keyframes __P__dashl{to{stroke-dashoffset:34}}
@keyframes __P__dash{to{stroke-dashoffset:-34}}
.__P__far{animation:__P__scroll 46s linear infinite}
.__P__near{animation:__P__scroll 20s linear infinite}
@keyframes __P__scroll{to{transform:translateX(-400px)}}
.__P__bounce{animation:__P__bounce 1.1s ease-in-out infinite}
@keyframes __P__bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
.__P__pulse{animation:__P__pulse 1.7s ease-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes __P__pulse{0%{transform:scale(.4);opacity:.9}100%{transform:scale(1.7);opacity:0}}
.__P__tw{animation:__P__tw 2.4s ease-in-out infinite}
@keyframes __P__tw{0%,100%{opacity:.12}50%{opacity:.95}}
.__P__float{animation:__P__float 3.2s ease-in-out infinite}
@keyframes __P__float{0%{transform:translateY(6px) rotate(-6deg);opacity:0}30%{opacity:1}100%{transform:translateY(-30px) rotate(10deg);opacity:0}}
.__P__knock{animation:__P__knock 1.8s ease-in-out infinite}
@keyframes __P__knock{0%,100%{transform:rotate(0)}12%{transform:rotate(-30deg)}24%{transform:rotate(0)}36%{transform:rotate(-30deg)}48%{transform:rotate(0)}}
.__P__pop{animation:__P__pop 2.2s ease-in-out infinite;transform-box:fill-box;transform-origin:50% 100%}
@keyframes __P__pop{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}
.__P__k1,.__P__k2,.__P__k3{animation:__P__kn 1.8s ease-out infinite;opacity:0}
.__P__k2{animation-delay:.12s}.__P__k3{animation-delay:.24s}
@keyframes __P__kn{0%,100%{opacity:0}10%{opacity:1}30%{opacity:0}}
.__P__chev{animation:__P__chev 1.4s linear infinite;opacity:0}
@keyframes __P__chev{0%{transform:translateX(30px);opacity:0}20%{opacity:1}80%{opacity:1}100%{transform:translateX(-30px);opacity:0}}
.__P__drive{animation:__P__drive 6.5s ease-in-out infinite}
@keyframes __P__drive{0%{transform:translateX(46px);opacity:0}12%{opacity:1}80%{opacity:1}100%{transform:translateX(-30px);opacity:0}}
.__P__sway{animation:__P__sway 5s ease-in-out infinite}
@keyframes __P__sway{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(6deg)}}
.__P__car{animation:__P__carmove 7s linear infinite}
@keyframes __P__carmove{0%{transform:translateX(0)}100%{transform:translateX(-520px)}}
.__P__lift{animation:__P__lift 4s ease-in-out infinite}
@keyframes __P__lift{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.25)}}
.__P__walk{animation:__P__walk 6s ease-in-out infinite}
@keyframes __P__walk{0%,4%{transform:translateX(0);opacity:0}12%{opacity:1}80%{transform:translateX(-122px);opacity:1}92%,100%{transform:translateX(-132px);opacity:0}}
.__P__swing{animation:__P__swing 3.6s ease-in-out infinite}
@keyframes __P__swing{0%,100%{transform:rotate(-1.6deg)}50%{transform:rotate(1.6deg)}}
.__P__draw{stroke-dasharray:100;animation:__P__draw 3.4s ease-in-out infinite}
@keyframes __P__draw{0%{stroke-dashoffset:100;opacity:0}3%{opacity:1}26%{stroke-dashoffset:0}90%{stroke-dashoffset:0;opacity:1}98%{stroke-dashoffset:0;opacity:0}100%{stroke-dashoffset:100;opacity:0}}
.__P__head{animation:__P__head 3.4s ease-in-out infinite}
@keyframes __P__head{0%,22%{opacity:0}30%,90%{opacity:1}98%,100%{opacity:0}}
.__P__cross{animation:__P__cross 7.4s linear infinite}
@keyframes __P__cross{0%{transform:translateX(-290px)}100%{transform:translateX(290px)}}
.__P__arrive{animation:__P__arrive 9s cubic-bezier(.2,.7,.25,1) infinite}
@keyframes __P__arrive{0%{transform:translateX(-270px);opacity:0}3%{transform:translateX(-262px);opacity:1}30%{transform:translateX(0);opacity:1}88%{transform:translateX(0);opacity:1}95%,100%{transform:translateX(0);opacity:0}}
.__P__wspin{animation:__P__wspin 9s cubic-bezier(.2,.7,.25,1) infinite}
@keyframes __P__wspin{0%{transform:rotate(0)}30%{transform:rotate(760deg)}100%{transform:rotate(760deg)}}
.__P__gate{animation:__P__gate 9s ease-in-out infinite;transform-box:fill-box;transform-origin:50% 0}
@keyframes __P__gate{0%,32%{transform:scaleY(1)}44%,86%{transform:scaleY(.07)}96%,100%{transform:scaleY(1)}}
.__P__glowin{animation:__P__glowin 9s ease-in-out infinite}
@keyframes __P__glowin{0%,32%{opacity:0}44%,86%{opacity:1}96%,100%{opacity:0}}
.__P__drop{animation:__P__drop 6s ease-in-out infinite}
@keyframes __P__drop{0%{transform:translate(16px,-50px) rotate(12deg) scale(1);opacity:0}8%{opacity:1}22%{transform:translate(0,0) rotate(0) scale(1);opacity:1}28%{transform:translate(0,1.5px) rotate(0) scale(.95);opacity:1}33%{transform:translate(0,0) rotate(0) scale(1);opacity:1}90%{transform:translate(0,0) rotate(0) scale(1);opacity:1}98%,100%{transform:translate(0,0) rotate(0) scale(1);opacity:0}}
.__P__laser{animation:__P__laser 6s ease-in-out infinite}
@keyframes __P__laser{0%,34%{transform:translateX(0);opacity:0}38%{opacity:1}58%{transform:translateX(104px);opacity:1}62%,100%{transform:translateX(104px);opacity:0}}
.__P__dot{animation:__P__dot 1.4s ease-in-out infinite}
@keyframes __P__dot{0%,100%{opacity:.25;transform:translateY(0)}40%{opacity:1;transform:translateY(-3px)}}
.__P__conf{animation:__P__conf 4.2s ease-in infinite;opacity:0}
@keyframes __P__conf{0%{transform:translateY(-14px) rotate(0);opacity:0}12%{opacity:1}100%{transform:translateY(74px) rotate(200deg);opacity:0}}
@media (prefers-reduced-motion:reduce){svg *{animation:none!important}}
"""


def _css_for(css, inner, p):
    """Mantem so as regras/keyframes que a cena usa (cada cena carrega o proprio CSS, entao o peso importa)."""
    linhas = [l for l in css.replace("__P__", p).strip().splitlines() if l]
    rx = re.compile(r"\.(" + re.escape(p) + r"\w+)")
    usadas = []
    for l in linhas:
        if l.startswith("."):
            if any(c in inner for c in rx.findall(l.split("{", 1)[0])):
                usadas.append(l)
        elif l.startswith("@media"):
            usadas.append(l)
    corpo = "".join(usadas)
    kf = []
    for l in linhas:
        if l.startswith("@keyframes"):
            nome = l.split("{", 1)[0].split()[1]
            if nome in corpo or nome in inner:
                kf.append(l)
    return "".join(usadas + kf)


def frame(k, p, inner, label, defs=""):
    css = _css_for(CSS, inner, p)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" role="img" class="agy-scene" aria-label="{label}" '
            f'style="width:100%;height:100%;display:block;font-family:Inter,system-ui,Segoe UI,sans-serif">'
            f'<style>{css}</style><defs>'
            f'<radialGradient id="{p}glow" cx="50%" cy="55%" r="55%"><stop offset="0" stop-color="{k["glow"]}" stop-opacity=".16"/>'
            f'<stop offset="1" stop-color="{k["glow"]}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{p}glass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b8e2ff"/>'
            f'<stop offset="1" stop-color="#5f9fd0"/></linearGradient>'
            f'<linearGradient id="{p}beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff6c8" stop-opacity=".55"/>'
            f'<stop offset="1" stop-color="#fff6c8" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="{p}fadeg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".07" stop-color="#fff"/><stop offset=".93" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="{p}fade"><rect width="400" height="300" fill="url(#{p}fadeg)"/></mask>'
            f'<linearGradient id="{p}spotA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{k["accent"]}" stop-opacity=".42"/>'
            f'<stop offset="1" stop-color="{k["accent"]}" stop-opacity="0"/></linearGradient>{defs}</defs>'
            f'<rect width="400" height="300" fill="url(#{p}glow)"/>{inner}</svg>')


def skyline(k, p, scroll=True):
    def layer(seed, hmin, hmax, op, outline):
        r = random.Random(seed); x = 0; out = ""
        while x < 400:
            w = r.randint(22, 46); h = r.randint(hmin, hmax)
            if outline:
                out += f'<rect x="{x}" y="{GROUND-h}" width="{w}" height="{h}" fill="none" stroke="{k["accent"]}" stroke-opacity="{op*3.2:.2f}" stroke-width="1.2"/>'
            else:
                out += f'<rect x="{x}" y="{GROUND-h}" width="{w}" height="{h}" fill="{k["ink"]}" fill-opacity="{op}"/>'
            if r.random() < .55:
                out += f'<rect class="{p}tw" style="animation-delay:{r.random()*2:.1f}s" x="{x+w//2-2}" y="{GROUND-h+10}" width="4" height="5" fill="{k["glow"]}"/>'
            x += w + r.randint(2, 10)
        return out
    outline = k["sky"] == "outline"
    far, near = layer(3, 50, 110, .06, False), layer(11, 32, 78, .10 if not outline else .05, outline)
    if scroll:
        f = f'<g class="{p}far">{far}<g transform="translate(400,0)">{far}</g></g>'
        n = f'<g class="{p}near">{near}<g transform="translate(400,0)">{near}</g></g>'
    else:
        f, n = far, near
    return f + n


def road(k, p, moving=True, cy=None):
    dash = f'class="{p}dashl"' if moving else 'stroke-dasharray="18 16"'
    return (f'<rect x="0" y="{GROUND}" width="400" height="{ROAD_BOTTOM-GROUND}" fill="{k["ink"]}" fill-opacity=".10"/>'
            f'<line x1="0" x2="400" y1="{GROUND}" y2="{GROUND}" stroke="{k["ink"]}" stroke-opacity=".28" stroke-width="1.5"/>'
            f'<line {dash} x1="0" x2="400" y1="{VEH_Y+8 if cy is None else cy}" y2="{VEH_Y+8 if cy is None else cy}" stroke="{k["ink"]}" stroke-opacity=".32" stroke-width="2"/>')


def logo_img(k, x, y, w, h):
    """Logo do cliente numa area x,y,w,h (com recorte e mistura 'screen' quando o arquivo tem fundo preto)."""
    blend = ' style="mix-blend-mode:screen"' if k.get("blend") else ""
    c = k.get("crop")
    if c:
        sx, sy, sw, sh, W, H = c
        return (f'<svg x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" viewBox="{sx} {sy} {sw} {sh}" '
                f'preserveAspectRatio="xMidYMid meet" overflow="hidden"{blend}><image href="{k["logo"]}" width="{W}" height="{H}"/></svg>')
    return f'<image href="{k["logo"]}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" preserveAspectRatio="xMidYMid meet"{blend}/>'


def plate(k, cx, cy, w, h, unflip=False, r=4, bg=True):
    pad = 3
    iw, ih = w - 2 * pad, h - 2 * pad
    lw, lh = (ih * k["ar"], ih) if iw / ih > k["ar"] else (iw, iw / k["ar"])
    s = ""
    if bg and k.get("plate"):
        s += (f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" rx="{r}" fill="{k["plate"]}" '
              f'stroke="{k.get("plateStroke","#000")}" stroke-width="1.3"/>')
    s += logo_img(k, cx - lw / 2, cy - lh / 2, lw, lh)
    if unflip:
        s = f'<g transform="translate({cx},{cy}) scale(-1,1) translate({-cx},{-cy})">{s}</g>'
    return s


def truck(k, p, x, y, scale=1.0, flip=False, wheels=True, beam=False, inner_class="", extra="", shadow=True, skirt=False):
    """Caminhao baú virado p/ direita; ground y=0. flip espelha (logo desespelhado). wheels: True gira sempre, 'arrive' gira ao chegar."""
    fx = -scale if flip else scale
    g = f'<g transform="translate({x},{y}) scale({fx},{scale})"><g class="{inner_class}">'
    if shadow:
        g += '<ellipse cx="96" cy="1" rx="102" ry="4" fill="#000" fill-opacity=".28"/>'
    if beam and k["dark"]:
        g += f'<polygon points="192,-36 250,-52 250,-14" fill="url(#{p}beam)"/>'
    neon = 'style="filter:drop-shadow(0 0 3px %s) drop-shadow(0 0 9px rgba(227,55,129,.55))"' % k["accent"] if k.get("neon") else ""
    g += f'<g {neon}>'
    g += '<rect x="0" y="-24" width="192" height="8" rx="2" fill="#15151b"/>'
    if skirt:                                                            # saia entre as rodas (esconde quem passa por tras do caminhao)
        g += '<rect x="44" y="-17" width="96" height="14" fill="#1b1c23"/>'
    g += f'<rect x="0" y="-84" width="130" height="60" rx="6" fill="{k["body"]}"' + (f' stroke="{k["accent"]}" stroke-width="1.6"' if k.get("neon") else (f' stroke="{k["bodyStroke"]}" stroke-width="1.4"' if k.get("bodyStroke") else "")) + '/>'
    g += '<rect x="0" y="-84" width="130" height="7" rx="6" fill="#fff" fill-opacity=".16"/>'
    g += f'<rect x="0" y="-36" width="130" height="8" fill="{k["stripe"]}"/>'
    g += '<line x1="5" y1="-80" x2="5" y2="-30" stroke="#000" stroke-opacity=".25"/>'
    g += plate(k, 66, -58, 108, 40, unflip=flip, bg=False)
    g += (f'<path d="M130,-70 L164,-70 Q172,-70 177,-60 L190,-40 Q192,-37 192,-33 L192,-24 L130,-24 Z" fill="{k["cab"]}"' +
          (f' stroke="{k["accent"]}" stroke-width="1.6"' if k.get("neon") else "") + '/>')
    g += f'<path d="M139,-64 L162,-64 Q167,-64 170,-58 L179,-44 L139,-44 Z" fill="url(#{p}glass)"/>' + extra
    g += '<rect x="186" y="-38" width="6" height="7" rx="2" fill="#fff3c4"/>'
    g += '<rect x="126" y="-24" width="68" height="6" rx="2" fill="#22232b"/></g>'
    for wx in (34, 150):
        spin = (f'class="{p}spin"' if wheels is True else f'class="{p}wspin"' if wheels == "arrive"
                else f'style="{wheels[6:]}"' if isinstance(wheels, str) and wheels.startswith("style:") else "")
        g += (f'<g transform="translate({wx},-13)"><circle r="13" fill="#15151b"/><circle r="5.2" fill="#cfd3da"/>'
              f'<g {spin}><rect x="-1.2" y="-10.5" width="2.4" height="6" fill="#8a8f99"/><rect x="-1.2" y="4.5" width="2.4" height="6" fill="#8a8f99"/></g></g>')
    return g + "</g></g>"


def house(k, p, x, y, w=104, lit=False, op=1.0):
    win = "#ffd27a" if lit else k["ink"]
    wop = ".9" if lit else ".10"
    return (f'<g opacity="{op}"><rect x="{x}" y="{y-58}" width="{w}" height="58" fill="{k["ink"]}" fill-opacity=".14" stroke="{k["ink"]}" stroke-opacity=".28"/>'
            f'<polygon points="{x-8},{y-58} {x+w/2},{y-92} {x+w+8},{y-58}" fill="{k["ink"]}" fill-opacity=".22"/>'
            f'<rect x="{x+14}" y="{y-42}" width="26" height="22" rx="2" fill="{win}" fill-opacity="{wop}" stroke="{k["ink"]}" stroke-opacity=".3"/>'
            f'<line x1="{x+27}" x2="{x+27}" y1="{y-42}" y2="{y-20}" stroke="{k["ink"]}" stroke-opacity=".3"/>'
            f'<rect x="{x+w*0.56}" y="{y-42}" width="22" height="42" rx="2" fill="{k["door"]}"/>'
            f'<circle cx="{x+w*0.56+17}" cy="{y-20}" r="1.8" fill="#fff3c4"/></g>')


def wall(k):
    if k.get("wall"):
        return f'fill="{k["wall"]}" fill-opacity="{k["wallOp"]}" stroke="{k["wallStroke"]}" stroke-opacity="{.7 if k.get("neon") else 1}"'
    return f'fill="{k["ink"]}" fill-opacity=".16" stroke="{k["ink"]}" stroke-opacity=".3"'


def facade(k, wx, wy, ww, wh, dw, dh, h_logo, roof=18, logo_w=None, door_x=None):
    """Fachada do galpao: parede, telhado, logo centrado entre telhado e porta (com assert de colisao). Retorna (svg, dx)."""
    dx = wx + ww / 2 - dw / 2 if door_x is None else door_x
    topo, porta_topo = wy - wh, wy - dh
    cy_logo = (topo + porta_topo) / 2
    assert topo + 4 <= cy_logo - h_logo / 2 and cy_logo + h_logo / 2 <= porta_topo - 4, "logo do galpao colide com telhado/porta"
    lx = wx + ww / 2
    s = (f'<rect x="{wx}" y="{wy-wh}" width="{ww}" height="{wh}" {wall(k)}/>'
         f'<polygon points="{wx-6},{wy-wh} {wx+ww+6},{wy-wh} {wx+ww},{wy-wh-roof} {wx},{wy-wh-roof}" fill="{k["ink"]}" fill-opacity=".26"/>'
         + plate(k, lx, cy_logo, logo_w or (ww - 40), h_logo, r=5, bg=False))
    return s, dx


def warehouse(k, p, x, y, w=150, op=1.0, logo=True):
    """Galpao pequeno de fundo (sem logo quando distante)."""
    return (f'<g opacity="{op}"><rect x="{x}" y="{y-74}" width="{w}" height="74" {wall(k)}/>'
            f'<polygon points="{x-6},{y-74} {x+w+6},{y-74} {x+w},{y-88} {x},{y-88}" fill="{k["ink"]}" fill-opacity=".26"/>'
            + (plate(k, x + w / 2, y - 60, 104, 34, r=5, bg=False) if logo else "") +
            f'<rect x="{x+w/2-28}" y="{y-38}" width="56" height="38" fill="{k["door"]}" fill-opacity=".85"/>'
            + "".join(f'<line x1="{x+w/2-28}" x2="{x+w/2+28}" y1="{y-38+i*7}" y2="{y-38+i*7}" stroke="#000" stroke-opacity=".25"/>' for i in range(1, 6)) + '</g>')


def pack(x, y, rot=0, cls=""):
    return (f'<g transform="translate({x},{y}) rotate({rot})"><g class="{cls}"><rect x="-8" y="-11" width="16" height="22" rx="2" fill="#CC0000"/>'
            f'<polygon points="-8,-11 -4,-8 0,-11 4,-8 8,-11 8,-8 -8,-8" fill="#FFD600"/><polygon points="-8,11 -4,8 0,11 4,8 8,11 8,8 -8,8" fill="#FFD600"/>'
            f'<polygon points="0,-5 1.5,-1.5 5,-1 2.3,1.3 3,5 0,3 -3,5 -2.3,1.3 -5,-1 -1.5,-1.5" fill="#FFD600"/></g></g>')


def cardpiece(k, x, y, rot=0, cls="", s=1.0):
    """Cartao de credito na cor da marca (personalidade dos bancos)."""
    return (f'<g transform="translate({x},{y}) rotate({rot}) scale({s})"><g class="{cls}"><rect x="-13" y="-8.5" width="26" height="17" rx="3" fill="{k["accent"]}"/>'
            f'<rect x="-13" y="-4.2" width="26" height="3.6" fill="#000" fill-opacity=".38"/>'
            f'<rect x="-9.5" y="1.6" width="7" height="5" rx="1.2" fill="#fff" fill-opacity=".85"/>'
            f'<rect x="1" y="3.6" width="8" height="1.8" rx=".9" fill="#fff" fill-opacity=".6"/></g></g>')


def star(x, y, s, p, d):
    return (f'<path class="{p}tw" style="animation-delay:{d}s" transform="translate({x},{y}) scale({s})" d="M0,-6 L1.6,-1.6 L6,0 L1.6,1.6 L0,6 L-1.6,1.6 L-6,0 L-1.6,-1.6 Z" fill="#fff"/>')


def car(k, p, x, y, s=.62):
    return (f'<g transform="translate({x},{y}) scale({-s},{s})"><path d="M0,0 L0,-14 Q0,-18 6,-18 L14,-18 L22,-28 Q24,-30 28,-30 L52,-30 Q56,-30 58,-27 L64,-18 L74,-18 Q80,-18 80,-12 L80,0 Z" fill="{k["accent"]}"/>'
            f'<path d="M24,-19 L29,-27 L40,-27 L40,-19 Z M44,-19 L44,-27 L52,-27 L58,-19 Z" fill="#eaf6ff"/>'
            f'<circle cx="18" cy="0" r="8" fill="#15151b"/><circle cx="62" cy="0" r="8" fill="#15151b"/></g>')


def courier(k, p, x, y, knock=True):
    arm = f'<g transform="translate(7,-38)"><g class="{p}knock"><rect x="-2" y="0" width="4" height="15" rx="2" fill="{k["accent"]}"/></g></g>' if knock else ""
    return (f'<g transform="translate({x},{y})"><rect x="-6" y="-16" width="5" height="16" fill="#2a2f3a"/><rect x="1" y="-16" width="5" height="16" fill="#2a2f3a"/>'
            f'<rect x="-9" y="-40" width="18" height="26" rx="5" fill="{k["accent"]}"/><circle cx="0" cy="-47" r="7" fill="#f0c9a6"/>'
            f'<path d="M-7,-49 A7,7 0 0 1 7,-49 L9,-49 L-7,-49Z" fill="{k["cab"] if k["dark"] else k["body"]}"/>{arm}'
            f'<g transform="translate(-24,-32)"><rect width="22" height="17" rx="2" fill="#c9975b"/><rect x="9" width="4" height="17" fill="#e6c48f"/></g></g>')


def bubble(k, p, cx, cy):
    hw, top, bot, r, tc = 101, -27, 23, 13, 24
    d = (f"M{-hw+r},{top} H{hw-r} A{r},{r} 0 0 1 {hw},{top+r} V{bot-r} A{r},{r} 0 0 1 {hw-r},{bot} H{tc+8} L{tc},{bot+10} L{tc-8},{bot} "
         f"H{-hw+r} A{r},{r} 0 0 1 {-hw},{bot-r} V{top+r} A{r},{r} 0 0 1 {-hw+r},{top} Z")
    t = 'text-rendering="geometricPrecision"'
    return (f'<g transform="translate({cx},{cy})"><g class="{p}pop"><path d="{d}" fill="#fff" stroke="{WARN}" stroke-width="2.4" stroke-linejoin="round"/>'
            f'<g transform="translate(-74,-2)"><circle r="12" fill="none" stroke="#2b2f3a" stroke-width="2.1"/><line class="{p}hand" x1="0" y1="0" x2="0" y2="-7.5" stroke="#2b2f3a" stroke-width="2.1" stroke-linecap="round"/>'
            f'<line x1="0" y1="0" x2="5.4" y2="0" stroke="#2b2f3a" stroke-width="2.1" stroke-linecap="round"/></g>'
            f'<text {t} x="-52" y="-4" font-size="17" font-weight="700" fill="#1c202b" letter-spacing="-.01em">Insucesso</text>'
            f'<text {t} x="-52" y="13" font-size="11.5" font-weight="500" fill="#3f4556">Nova tentativa <tspan font-weight="700">em breve</tspan></text></g></g>')


def props_ambient(k, p, scene):
    s = ""
    if k["prop"] == "spot":
        s += (f'<g transform="translate(60,-6)"><g class="{p}sway"><polygon points="-14,0 14,0 70,250 -70,250" fill="url(#{p}spotA)" opacity=".55"/></g></g>'
              f'<g transform="translate(340,-6)"><g class="{p}sway" style="animation-delay:-2.5s"><polygon points="-14,0 14,0 70,250 -70,250" fill="url(#{p}spotA)" opacity=".55"/></g></g>'
              + star(36, 58, 1, p, 0) + star(370, 74, .8, p, .8) + star(300, 40, .7, p, 1.4) + star(120, 30, .9, p, .4))
    return s


def box(k, p, x, y, w=54, h=40):
    lw, lh = 40, 21
    return (f'<g transform="translate({x},{y})"><rect x="0" y="{-h}" width="{w}" height="{h}" fill="#c9975b"/>'
            f'<polygon points="0,{-h} 9,{-h-10} {w+9},{-h-10} {w},{-h}" fill="#e2bb86"/>'
            f'<polygon points="{w},{-h} {w+9},{-h-10} {w+9},-10 {w},0" fill="#a97a44"/>'
            f'<rect x="{w/2-5}" y="{-h}" width="10" height="{h}" fill="#e6c48f" fill-opacity=".85"/>'
            + plate(k, w / 2, -h / 2 + 2, lw, lh, r=3) + '</g>')


def circ_arrow(R=13.5, a0=150, a1=-100, head=10.5, hw=7.2):
    """Seta circular aberta (anti-horaria): comeca embaixo a esquerda, contorna pela direita, sobe e termina no alto a esquerda apontando p/ a esquerda."""
    r0, r1 = math.radians(a0), math.radians(a1)
    x0, y0 = R * math.cos(r0), R * math.sin(r0)
    x1, y1 = R * math.cos(r1), R * math.sin(r1)
    vx, vy = R * math.sin(r1), -R * math.cos(r1)          # tangente no fim (sentido do movimento)
    n = math.hypot(vx, vy); vx, vy = vx / n, vy / n
    tip = (x1 + vx * head, y1 + vy * head)
    b1 = (x1 - vy * hw, y1 + vx * hw); b2 = (x1 + vy * hw, y1 - vx * hw)
    d = f"M{x0:.2f},{y0:.2f} A{R},{R} 0 1 0 {x1:.2f},{y1:.2f}"
    pts = f"{b1[0]:.2f},{b1[1]:.2f} {b2[0]:.2f},{b2[1]:.2f} {tip[0]:.2f},{tip[1]:.2f}"
    return d, pts


def uturn_sign(k, p, x, top_y):
    r = 26
    d, pts = circ_arrow()
    return (f'<g transform="translate({x},{GROUND+2})"><rect x="-1.8" y="{top_y-GROUND-2+r}" width="3.6" height="{GROUND+2-top_y-r}" fill="{k["ink"]}" fill-opacity=".55"/>'
            f'<g transform="translate(0,{top_y-GROUND-2})"><circle class="{p}pulse" r="{r}" fill="none" stroke="{k["accent"]}" stroke-width="2.4"/>'
            f'<g class="{p}swing" style="transform-origin:0 {r+10}px"><circle r="{r}" fill="{k.get("signFill", k["accent"])}" stroke="#fff" stroke-width="3"/>'
            f'<path class="{p}draw" pathLength="100" d="{d}" fill="none" stroke="#fff" stroke-width="4.2" stroke-linecap="round"/>'
            f'<polygon class="{p}head" points="{pts}" fill="#fff" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></g></g></g>')


def walker(k, p, x, y):
    return (f'<g transform="translate({x},{y})"><g class="{p}walk"><g class="{p}bob"><rect x="-6" y="-16" width="5" height="16" fill="#2a2f3a"/><rect x="1" y="-16" width="5" height="16" fill="#2a2f3a"/>'
            f'<rect x="-9" y="-40" width="18" height="26" rx="5" fill="{k["accent"]}"/><circle cx="0" cy="-47" r="7" fill="#f0c9a6"/>'
            f'<path d="M-7,-49 A7,7 0 0 1 7,-49 L9,-49 L-7,-49Z" fill="{k["cab"] if k["dark"] else k["body"] if k["body"]!="#FFFFFF" else "#100c5a"}"/>'
            f'<g transform="translate(-40,-40) scale(.62)">{box(k, p, 0, 0)}</g></g></g></g>')


# ---------------------------------------------------------------- cenas

def scene_em_rota(k, p):
    ty = VEH_Y + 16                                                      # caminhao na faixa da direita (a mais proxima); o carro vem na contramao, na faixa de tras
    topo = GROUND - 58
    poste = lambda x: (f'<g transform="translate({x},0)"><rect x="-1.4" y="{topo}" width="2.8" height="58" fill="{k["ink"]}" fill-opacity=".34"/>'
                       f'<rect x="-11" y="{topo-2}" width="22" height="3" rx="1.5" fill="{k["ink"]}" fill-opacity=".34"/><circle cx="10" cy="{topo+2}" r="2.6" fill="#ffd27a" fill-opacity=".8"/></g>')
    fio = lambda x1, x2: "".join(f'<path d="M{x1+dx},{topo-1} Q{(x1+x2)/2+dx},{topo+13} {x2+dx},{topo-1}" fill="none" stroke="{k["ink"]}" stroke-opacity=".3" stroke-width="1"/>' for dx in (-9, 9))
    postes = poste(60) + poste(260) + fio(60, 260) + fio(260, 460)
    nuvem = lambda x, y, sc: (f'<g transform="translate({x},{y}) scale({sc})" fill="{k["ink"]}" fill-opacity=".07"><ellipse cx="0" cy="0" rx="34" ry="9"/>'
                              f'<ellipse cx="-16" cy="-6" rx="18" ry="8"/><ellipse cx="12" cy="-8" rx="20" ry="9"/></g>')
    nuvens = nuvem(90, 62, 1) + nuvem(300, 40, .8)
    kf = (f'<style>@keyframes {p}pl{{to{{transform:translateX(-400px)}}}}@keyframes {p}cl{{to{{transform:translateX(-400px)}}}}</style>')
    driver = (f'<circle cx="157" cy="-54" r="5.2" fill="{SKIN}"/><path d="M151.4,-56 A5.6,5.6 0 0 1 162.6,-56 L165,-56 L151.4,-56Z" fill="{k["cab"]}"/>'
              f'<rect x="148" y="-49.5" width="18" height="6" rx="3" fill="{k["accent"]}"/>')
    s = (kf + f'<g mask="url(#{p}fade)"><g style="animation:{p}cl 70s linear infinite">{nuvens}<g transform="translate(400,0)">{nuvens}</g></g>'
         + skyline(k, p) + road(k, p, cy=260) +
         f'<g style="animation:{p}pl 5s linear infinite">{postes}<g transform="translate(400,0)">{postes}</g></g></g>' + props_ambient(k, p, "rota"))
    if k["prop"] == "car":
        s += f'<g transform="translate(470,0)"><g class="{p}car">{car(k, p, 0, GROUND+13)}</g></g>'
    lines = "".join(f'<line class="{p}dashl" style="animation-delay:{i*.15}s" x1="{62-i*6}" x2="{84-i*6}" y1="{ty-34+i*14}" y2="{ty-34+i*14}" stroke="{k["ink"]}" stroke-opacity=".28" stroke-width="2" stroke-linecap="round"/>' for i in range(3))
    s += lines + truck(k, p, 104, ty, 1.0, beam=True, inner_class=f"{p}bob", extra=driver)
    if k["prop"] == "packs":
        s += pack(80, 218, -8, f"{p}float") + f'<g style="animation-delay:-1.6s">{pack(62, 232, 10, p+"float")}</g>'
    if k["prop"] == "cards":
        s += cardpiece(k, 82, 220, -8, f"{p}float") + f'<g style="animation-delay:-1.6s">{cardpiece(k, 62, 234, 10, p+"float")}</g>'
    return frame(k, p, s, f"Pedido em rota de entrega - {k['name']}")


def scene_atencao(k, p):
    dur = 2.4
    s = f'<g mask="url(#{p}fade)">' + skyline(k, p, scroll=False) + road(k, p, moving=False) + "</g>" + props_ambient(k, p, "atencao")
    kf = (f'<style>@keyframes {p}fl{{0%,62%{{opacity:1}}72%,78%{{opacity:.04}}88%,100%{{opacity:1}}}}'
          f'@keyframes {p}qm{{0%{{transform:translateY(0) rotate(0) scale(1)}}9%{{transform:translateY(-6px) rotate(-9deg) scale(1.14)}}19%{{transform:translateY(0) rotate(8deg) scale(1)}}'
          f'30%{{transform:translateY(-3px) rotate(-6deg) scale(1.05)}}42%{{transform:translateY(0) rotate(4deg) scale(1)}}56%,100%{{transform:translateY(0) rotate(0) scale(1)}}}}</style>')
    s += kf + f'<g style="animation:{p}fl {dur}s ease-in-out infinite">' + house(k, p, 262, GROUND + 4, 112, lit=False) + '</g>'
    s += truck(k, p, 18, VEH_Y, .80, wheels=False)
    kn = "".join(f'<path class="{p}k{i+1}" d="M{236-i*7},{GROUND-38} q-5,4 0,8" fill="none" stroke="{WARN}" stroke-width="2" stroke-linecap="round" transform="translate(0,{i*6})"/>' for i in range(3))
    # interrogacao (desenhada, sem texto) sobre o entregador: ninguem atende
    duvida = (f'<g transform="translate(232,168)"><g style="transform-box:fill-box;transform-origin:50% 100%;animation:{p}qm {dur}s ease-in-out infinite">'
              f'<path d="M-8,-12 C-8,-24 8,-24 8,-12 C8,-5 0,-5 0,3" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round"/>'
              f'<circle cx="0" cy="12" r="5.6" fill="#fff"/>'
              f'<path d="M-8,-12 C-8,-24 8,-24 8,-12 C8,-5 0,-5 0,3" fill="none" stroke="{WARN}" stroke-width="5.4" stroke-linecap="round"/>'
              f'<circle cx="0" cy="12" r="3.4" fill="{WARN}"/></g></g>')
    s += courier(k, p, 232, GROUND + 8) + kn + duvida + bubble(k, p, 295, 104)
    if k["prop"] == "packs":
        s += pack(196, GROUND - 2, 12)
    if k["prop"] == "cards":
        s += cardpiece(k, 196, GROUND + 4, 12)
    return frame(k, p, s, f"Entrega malsucedida, insucesso, nova tentativa em breve - {k['name']}")


def scene_preparacao(k, p):
    s = f'<g mask="url(#{p}fade)">' + skyline(k, p, scroll=False) + f'<rect x="0" y="{GROUND}" width="400" height="{ROAD_BOTTOM-GROUND}" fill="{k["ink"]}" fill-opacity=".10"/>' + "</g>"
    s += props_ambient(k, p, "prep")
    wx, wy, ww, wh = 6, GROUND + 2, 176, 132     # galpao em escala: porta > 2x a altura da caixa
    dw, dh = 104, 84
    h_logo = 36 if k["ar"] > 2.5 else 40
    fs, dx = facade(k, wx, wy, ww, wh, dw, dh, h_logo, roof=18, logo_w=136)
    s += (fs +
          f'<rect x="{dx}" y="{wy-dh}" width="{dw}" height="{dh}" fill="#000" fill-opacity=".78"/>'
          f'<rect x="{dx}" y="{wy-dh}" width="{dw}" height="10" fill="{k["door"]}" fill-opacity=".92"/>'
          f'<line x1="{dx}" x2="{dx+dw}" y1="{wy-dh+5}" y2="{wy-dh+5}" stroke="#000" stroke-opacity=".28"/>')
    by, bdx, bdy = 226, 16, -14          # bdx/bdy: profundidade da esteira (mesma perspectiva das caixas e do arco)
    x0 = dx + 4
    pernas = [150 + i * 60 for i in range(4)]
    for lx in pernas:                    # pernas de tras: mais altas e mais escuras
        s += f'<rect x="{lx+bdx}" y="{by+10+bdy}" width="6" height="{ROAD_BOTTOM-by-10}" fill="#22252d"/>'
    for lx in pernas:                    # pernas da frente
        s += f'<rect x="{lx}" y="{by+10}" width="6" height="{ROAD_BOTTOM-by-10}" fill="#2a2d36"/>'
    s += (f'<polygon points="{x0},{by} 400,{by} {400+bdx},{by+bdy} {x0+bdx},{by+bdy}" fill="#3c404c"/>'
          f'<line class="{p}dash" x1="{x0+bdx/2+4}" x2="{400+bdx/2}" y1="{by+bdy/2}" y2="{by+bdy/2}" stroke="#5c6170" stroke-width="2"/>'
          f'<rect x="{x0}" y="{by}" width="{400-x0}" height="10" rx="2" fill="#2a2d36"/>'
          f'<line x1="{x0}" x2="400" y1="{by+.8}" y2="{by+.8}" stroke="#565b69" stroke-width="1.4"/>')
    sx = 262
    fx, fy = sx + bdx, by + bdy          # moldura de tras: os pes ficam na borda de tras da esteira
    s += (f'<g transform="translate({fx},{fy})"><rect x="-30" y="-78" width="6" height="78" fill="#2c303b"/><rect x="30" y="-78" width="6" height="78" fill="#2c303b"/>'
          f'<rect x="-30" y="-84" width="66" height="8" rx="3" fill="#2c303b"/></g>'
          f'<polygon points="{sx-30},{by-84} {fx-30},{fy-84} {fx+36},{fy-84} {sx+36},{by-84}" fill="#4a4f5c"/>'
          f'<rect x="{fx-24}" y="{fy-78}" width="54" height="78" fill="#000" fill-opacity=".14"/>')
    for d in (0, -2.2, -4.4):
        s += (f'<g transform="translate({dx+6},{by-3})"><g style="animation:{p}belt 6.6s linear infinite;animation-delay:{d}s">{box(k, p, 0, 0)}</g></g>')
    s += (f'<g transform="translate({sx},{by})"><rect x="-30" y="-78" width="6" height="78" fill="#3f4451"/><rect x="30" y="-78" width="6" height="78" fill="#3f4451"/>'
          f'<rect x="-30" y="-84" width="66" height="8" rx="3" fill="#3f4451"/><rect class="{p}tw" x="-24" y="-74" width="54" height="2.4" fill="{k["accent"]}" style="animation-duration:1.4s"/></g>')
    s += f'<style>@keyframes {p}belt{{0%{{transform:translateX(0);opacity:0}}5%{{opacity:1}}90%{{opacity:1}}100%{{transform:translateX(320px);opacity:0}}}}</style>'
    return frame(k, p, s, f"Pedido em preparacao para transporte - {k['name']}")


def scene_devolucao(k, p):
    """Ciclo infinito: o operador sai de tras do caminhao com uma caixa, entrega no galpao do remetente (a caixa desliza para dentro da porta),
    volta para tras do caminhao para pegar outra e recomeca. Ninguem aparece nem some do nada."""
    dur, SP = 8.0, .85
    s = f'<g mask="url(#{p}fade)">' + skyline(k, p, scroll=False) + road(k, p, moving=False) + "</g>"
    wx, wy, ww, wh = 6, GROUND + 2, 150, 132     # galpao em escala: porta maior que a pessoa
    dw, dh = 78, 80
    h_logo = 38 if k["ar"] > 2.5 else 40
    fs, dx = facade(k, wx, wy, ww, wh, dw, dh, h_logo, roof=15, logo_w=112)
    porta_e = wx + ww / 2 - dw / 2
    s += (fs +
          f'<rect x="{porta_e}" y="{wy-dh}" width="{dw}" height="{dh}" fill="#000" fill-opacity=".72"/>'
          f'<rect x="{porta_e}" y="{wy-dh}" width="{dw}" height="7" fill="{k["door"]}"/>'
          f'<rect x="{porta_e}" y="{wy-6}" width="{dw}" height="6" fill="#3a3e4a"/><rect x="{porta_e}" y="{wy-6}" width="{dw}" height="1.6" fill="#fff" fill-opacity=".25"/>')
    s += uturn_sign(k, p, 188, 88)
    x0, cy, D = 292, GROUND + 14, 176                                       # comeca escondido atras do caminhao (que vai de 214 a 379)
    bl_x, bl_y = x0 - 44, cy - 35 * SP + 10                                 # caixa nas maos (virado para a esquerda)
    kf = (f'<style>@keyframes {p}wk{{0%,8%{{transform:translateX(0) scaleX(-1)}}46%,57%{{transform:translateX({-D}px) scaleX(-1)}}58%{{transform:translateX({-D}px) scaleX(1)}}'
          f'92%{{transform:translateX(0) scaleX(1)}}93%,100%{{transform:translateX(0) scaleX(-1)}}}}'
          f'@keyframes {p}bx{{0%,8%{{transform:translateX(0)}}46%{{transform:translateX({-D}px)}}58%,94%{{transform:translateX({-D-100}px)}}94.01%,100%{{transform:translateX(0)}}}}'
          f'@keyframes {p}pu{{0%,44%{{transform:translateX(0)}}50%{{transform:translateX(7px)}}56%,100%{{transform:translateX(0)}}}}</style>'
          f'<clipPath id="{p}bc"><rect x="{porta_e}" y="0" width="{400-porta_e}" height="300"/></clipPath>')
    s += kf
    s += (f'<g transform="translate({x0},{cy})"><g style="animation:{p}wk {dur}s ease-in-out infinite"><g transform="scale({SP})"><g class="{p}bob">'
          + person(k, k["accent"], cap=k["cab"]) +
          f'<g transform="translate(5,-35)"><g style="transform-origin:0 0;animation:{p}pu {dur}s ease-in-out infinite"><rect x="0" y="-2" width="15" height="4" rx="2" fill="{k["accent"]}"/></g></g></g></g></g></g>')
    s += (f'<g clip-path="url(#{p}bc)"><g transform="translate({bl_x:.1f},{bl_y:.1f})"><g style="animation:{p}bx {dur}s ease-in-out infinite">'
          f'<g transform="scale(.55)">{box(k, p, 0, 0)}</g></g></g></g>')
    s += truck(k, p, 214, VEH_Y, .86, wheels=False, skirt=True)             # o caminhao esconde o operador quando ele sai/volta
    s += f'<polygon points="212,{VEH_Y-22} 186,{VEH_Y} 194,{VEH_Y} 218,{VEH_Y-18}" fill="#3a3e4a"/>'
    return frame(k, p, s, f"Pedido em devolucao ao remetente - {k['name']}")


# --- personagens e pecas das cenas novas

SKIN = "#f0c9a6"
SHIRT = "#8b93b8"


def person(k, vest, cap=None, hair=None, stripes=True):
    """Pessoa virada p/ a direita (o chamador espelha com scale(-1,1)); sem bracos: cada cena desenha os seus."""
    s = ('<rect x="-6" y="-16" width="5" height="16" fill="#2a2f3a"/><rect x="1" y="-16" width="5" height="16" fill="#2a2f3a"/>'
         f'<rect x="-9" y="-40" width="18" height="26" rx="5" fill="{vest}"/>')
    if stripes:
        s += '<rect x="-9" y="-31" width="18" height="2.4" fill="#fff" fill-opacity=".55"/><rect x="-9" y="-25" width="18" height="2.4" fill="#fff" fill-opacity=".55"/>'
    s += f'<circle cx="0" cy="-47" r="7" fill="{SKIN}"/>'
    if cap:
        s += f'<path d="M-7,-49 A7,7 0 0 1 7,-49 L10,-49 L-7,-49Z" fill="{cap}"/>'
    if hair:
        s += f'<path d="M-7.2,-48 A7.2,7.2 0 0 1 7.2,-48 L5,-51 Q0,-53 -5,-51 Z" fill="{hair}"/>'
    return s


def operador(k, p, x, y, flip=False, dur=6.0, at=45, sc=1.0):
    """Operador com prancheta (colete na cor da marca). O check da prancheta aparece em at% do ciclo de dur segundos."""
    fx = -sc if flip else sc
    kf = (f'<style>@keyframes {p}ck{{0%,{at}%{{stroke-dashoffset:100;opacity:0}}{at+1}%{{stroke-dashoffset:100;opacity:1}}{at+8}%{{stroke-dashoffset:0;opacity:1}}'
          f'90%{{stroke-dashoffset:0;opacity:1}}96%,100%{{stroke-dashoffset:0;opacity:0}}}}'
          f'@keyframes {p}wr{{0%,100%{{transform:rotate(0)}}22%{{transform:rotate(-5deg)}}46%{{transform:rotate(1deg)}}70%{{transform:rotate(-4deg)}}}}</style>')
    lines = "".join(f'<rect x="3" y="{-3+i*3.6:.1f}" width="{8.4 if i != 2 else 5.6}" height="1.2" rx=".6" fill="#2b2f3a" fill-opacity=".38"/>' for i in range(3))
    check = (f'<path pathLength="100" stroke-dasharray="100" d="M3.2,7 l2.3,2.4 l4.6,-5" fill="none" stroke="{k["accent"]}" stroke-width="1.7" '
             f'stroke-linecap="round" stroke-linejoin="round" style="animation:{p}ck {dur}s ease-in-out infinite"/>')
    return (kf + f'<g transform="translate({x},{y}) scale({fx},{sc})">' + person(k, k["accent"], cap=k["cab"]) +
            f'<g transform="translate(5,-35)"><g style="transform-origin:0 0;animation:{p}wr {dur}s ease-in-out infinite">'
            f'<rect x="-1" y="-1.7" width="13" height="3.4" rx="1.7" fill="{k["accent"]}" transform="rotate(28)"/>'
            f'<g transform="translate(9,-3) rotate(-6)"><rect x="0" y="-9" width="13" height="19" rx="1.6" fill="#fff" stroke="#aab0c6" stroke-width=".9"/>'
            f'<rect x="3.6" y="-10.7" width="5.8" height="3.2" rx=".8" fill="#2b2f3a"/>' + (f'<g transform="translate(13,0) scale(-1,1)">{lines}{check}</g>' if flip else lines + check) + '</g></g></g></g>')


def seal(k, p, cx, cy, r=22, dur=6.0, at=10, t0=14, t1=34, out=86):
    """Selo de check animado na cor da marca: aparece em at%, desenha o check de t0% a t1% e some em out% (ciclo de dur s)."""
    ring = k.get("seal", k["accent"])
    ink = k.get("sealInk", k["onAccent"])
    kf = (f'<style>@keyframes {p}sp{{0%,{at-1}%{{transform:scale(0)}}{at+5}%{{transform:scale(1)}}{out}%{{transform:scale(1)}}{out+6}%,100%{{transform:scale(0)}}}}'
          f'@keyframes {p}tk{{0%,{t0-1}%{{stroke-dashoffset:100;opacity:0}}{t0}%{{stroke-dashoffset:100;opacity:1}}{t1}%{{stroke-dashoffset:0;opacity:1}}'
          f'{out}%{{stroke-dashoffset:0;opacity:1}}{out+5}%,100%{{stroke-dashoffset:0;opacity:0}}}}</style>')
    return (kf + f'<g transform="translate({cx},{cy})"><g style="transform-box:fill-box;transform-origin:center;animation:{p}sp {dur}s cubic-bezier(.3,1.4,.5,1) infinite">'
            f'<circle class="{p}pulse" r="{r}" fill="none" stroke="{ring}" stroke-width="2.4"/>'
            f'<circle r="{r}" fill="{ring}" stroke="#fff" stroke-opacity=".9" stroke-width="2.6"/>'
            f'<path pathLength="100" stroke-dasharray="100" d="M{-r*.42:.1f},{r*.04:.1f} L{-r*.1:.1f},{r*.36:.1f} L{r*.46:.1f},{-r*.32:.1f}" fill="none" '
            f'stroke="{ink}" stroke-width="{r*.21:.1f}" stroke-linecap="round" stroke-linejoin="round" style="animation:{p}tk {dur}s ease-in-out infinite"/></g></g>')


def timer(k, p, cx, cy, dur=6.0, sc=1.0):
    """Ampulheta que se transforma em cronometro (como no GIF antigo): a areia cai (recortada pelo vidro), o vidro achata e vira o disco
    do relogio, o ponteiro gira, e o relogio volta a ser ampulheta com a areia em cima."""
    cap = k["ink"] if k["dark"] else k["cab"]
    a = k["accent"]
    e = "ease-in-out"
    an = lambda n: f"animation:{p}{n} {dur}s {e} infinite"
    up = "M-15,-25 H15 C15,-11 2.6,-5 2.6,0 H-2.6 C-2.6,-5 -15,-11 -15,-25 Z"
    lo = "M-2.6,0 H2.6 C2.6,5 15,11 15,25 H-15 C-15,11 -2.6,5 -2.6,0 Z"
    kf = (f'<style>'
          f'@keyframes {p}gl{{0%,40%{{transform:scaleY(1);opacity:1}}50%,84%{{transform:scaleY(.35);opacity:0}}96%,100%{{transform:scaleY(1);opacity:1}}}}'
          f'@keyframes {p}tc{{0%,40%{{transform:translateY(0);opacity:1}}48%,88%{{transform:translateY(4px);opacity:0}}97%,100%{{transform:translateY(0);opacity:1}}}}'
          f'@keyframes {p}bc{{0%,40%{{transform:translateY(0);opacity:1}}46%,88%{{transform:translateY(-7px);opacity:0}}97%,100%{{transform:translateY(0);opacity:1}}}}'
          f'@keyframes {p}st{{0%,6%{{transform:translateY(7px)}}38%,90%{{transform:translateY(27px)}}98%,100%{{transform:translateY(7px)}}}}'
          f'@keyframes {p}sb{{0%,6%{{transform:translateY(20px)}}38%,50%{{transform:translateY(0)}}51%,100%{{transform:translateY(20px)}}}}'
          f'@keyframes {p}sm{{0%,6%{{opacity:0}}9%,35%{{opacity:1}}39%,100%{{opacity:0}}}}'
          f'@keyframes {p}dc{{0%,42%{{transform:translateY(9px) scale(0)}}47%{{transform:translateY(5px) scale(.55)}}54%{{transform:translateY(0) scale(1.08)}}58%,82%{{transform:translateY(0) scale(1)}}88%{{transform:translateY(7px) scale(.5)}}93%,100%{{transform:translateY(9px) scale(0)}}}}'
          f'@keyframes {p}fc{{0%,52%{{transform:scale(0)}}58%{{transform:scale(1.1)}}61%,80%{{transform:scale(1)}}86%,100%{{transform:scale(0)}}}}'
          f'@keyframes {p}bt{{0%,54%{{transform:scale(0)}}60%{{transform:scale(1.2)}}63%,82%{{transform:scale(1)}}88%,100%{{transform:scale(0)}}}}'
          f'@keyframes {p}hd{{0%,60%{{transform:rotate(0)}}82%,100%{{transform:rotate(720deg)}}}}</style>'
          f'<clipPath id="{p}cu"><path d="{up}"/></clipPath><clipPath id="{p}cl"><path d="{lo}"/></clipPath>')
    glass = (f'<g style="{an("gl")}"><path d="M-15,-25 H15 C15,-11 2.6,-5 2.6,0 C2.6,5 15,11 15,25 H-15 C-15,11 -2.6,5 -2.6,0 C-2.6,-5 -15,-11 -15,-25 Z" fill="#fff" fill-opacity=".28"/>'
             f'<g clip-path="url(#{p}cu)"><rect x="-16" y="-26" width="32" height="26" fill="{a}" style="transform:translateY(7px);{an("st")}"/></g>'
             f'<g clip-path="url(#{p}cl)"><path d="M-16,27 V21 L0,6 L16,21 V27 Z" fill="{a}" style="{an("sb")}"/></g>'
             f'<line x1="0" y1="-1" x2="0" y2="21" stroke="{a}" stroke-width="1.5" style="{an("sm")}"/>'
             f'<path d="M-15,-25 H15 C15,-11 2.6,-5 2.6,0 C2.6,5 15,11 15,25 H-15 C-15,11 -2.6,5 -2.6,0 C-2.6,-5 -15,-11 -15,-25 Z" fill="none" stroke="{a}" stroke-opacity=".85" stroke-width="1.8"/></g>')
    caps = (f'<rect x="-19" y="-30" width="38" height="4.6" rx="2" fill="{cap}" style="{an("tc")}"/>'
            f'<rect x="-19" y="25.4" width="38" height="4.6" rx="2" fill="{cap}" style="{an("bc")}"/>')
    watch = (f'<g style="transform:scale(0);{an("dc")}"><circle r="22" fill="{a}"/></g>'
             f'<g style="transform:scale(0);{an("bt")}"><rect x="-4.5" y="-30" width="9" height="6.5" rx="2" fill="{a}"/>'
             f'<rect x="-3.2" y="-2" width="6.4" height="3.6" rx="1.6" fill="{a}" transform="translate(-16,-16) rotate(-42)"/>'
             f'<rect x="-3.2" y="-2" width="6.4" height="3.6" rx="1.6" fill="{a}" transform="translate(16,-16) rotate(42)"/></g>'
             f'<g style="transform:scale(0);{an("fc")}"><circle r="17" fill="#fff"/>'
             + "".join(f'<line x1="0" y1="-14.6" x2="0" y2="-12" stroke="#2b2f3a" stroke-opacity=".45" stroke-width="1.6" transform="rotate({d})"/>' for d in (0, 90, 180, 270)) +
             f'<g style="{an("hd")}"><line x1="0" y1="0" x2="0" y2="-11.5" stroke="#1c202b" stroke-width="2.6" stroke-linecap="round"/></g><circle r="2.8" fill="#1c202b"/></g>')
    return (kf + f'<g transform="translate({cx},{cy}) scale({sc})"><g class="{p}bob">{glass}{caps}{watch}</g></g>')


def rollgate(k, dx, top, dw, dh, style, op=".92"):
    """Portao de enrolar (cor da porta); style = animacao inline (senao o portao fica fechado)."""
    return (f'<g style="transform-box:fill-box;transform-origin:50% 0;{style}"><rect x="{dx}" y="{top}" width="{dw}" height="{dh}" fill="{k["door"]}" fill-opacity="{op}"/>'
            + "".join(f'<line x1="{dx}" x2="{dx+dw}" y1="{top+i*10}" y2="{top+i*10}" stroke="#000" stroke-opacity=".28"/>' for i in range(1, int(dh // 10) + 1)) + '</g>')


def _tf(X, Y, S, base):
    """Transformacao relativa a base=(X0,Y0,S0): para animar um objeto (posicionado por translate+scale da base) ate (X,Y) na escala S."""
    X0, Y0, S0 = base
    return f"translate({(X-X0)/S0:.2f}px,{(Y-Y0)/S0:.2f}px) scale({S/S0:.4f})"


# --- cenas novas (todos os clientes)

def _rack(k, p, x, w=84, top=100):
    """Estante do galpao (fundo): 3 niveis com caixas; o item da personalidade fica no nivel de cima."""
    ink, r = k["ink"], random.Random(x)
    s = ""
    for px in (x, x + w - 4):
        s += f'<rect x="{px}" y="{top}" width="4" height="{GROUND-top}" fill="{ink}" fill-opacity=".26"/>'
    for i, ny in enumerate((top + 30, top + 74, top + 118)):
        s += f'<rect x="{x}" y="{ny}" width="{w}" height="4" fill="{ink}" fill-opacity=".34"/>'
        cx = x + 8
        while cx < x + w - 22:
            bw, bh = r.randint(14, 24), r.randint(14, 26)
            s += f'<rect x="{cx}" y="{ny-bh}" width="{bw}" height="{bh}" fill="#c9975b" fill-opacity=".55"/>'
            cx += bw + r.randint(3, 8)
    yb = top + 30
    if k["prop"] == "packs":
        s += pack(x + w - 22, yb - 12, -6) + pack(x + w - 38, yb - 12, 8)
    elif k["prop"] == "cards":
        s += cardpiece(k, x + w - 24, yb - 10, -8) + cardpiece(k, x + w - 40, yb - 10, 8)
    elif k["prop"] == "car":
        s += car(k, p, x + w - 14, yb, .3)
    return s


def scene_aguardando(k, p):
    dur = 6.0
    s = f'<rect x="0" y="{GROUND}" width="400" height="{ROAD_BOTTOM-GROUND}" fill="{k["ink"]}" fill-opacity=".10"/>'
    s += f'<line x1="0" x2="400" y1="{GROUND}" y2="{GROUND}" stroke="{k["ink"]}" stroke-opacity=".28" stroke-width="1.5"/>'
    s += _rack(k, p, 12) + _rack(k, p, 304)
    s += props_ambient(k, p, "aguard")
    # bancada
    s += (f'<rect x="108" y="206" width="184" height="8" rx="2" fill="{k["ink"]}" fill-opacity=".36"/>'
          f'<rect x="118" y="214" width="6" height="{GROUND-214}" fill="{k["ink"]}" fill-opacity=".28"/><rect x="276" y="214" width="6" height="{GROUND-214}" fill="{k["ink"]}" fill-opacity=".28"/>')
    # caixa em 3D (escala .7: cabe na bancada e fica proporcional ao operador) com logo a esquerda e etiqueta a direita
    bx, by, bw, bh, dx, dy = 157, 206, 112, 70, 12, 12
    s += (f'<g transform="translate({bx},{by}) scale(.7)"><rect x="0" y="{-bh}" width="{bw}" height="{bh}" fill="#c9975b"/>'
          f'<polygon points="0,{-bh} {dx},{-bh-dy} {bw+dx},{-bh-dy} {bw},{-bh}" fill="#e2bb86"/>'
          f'<polygon points="{bw},{-bh} {bw+dx},{-bh-dy} {bw+dx},{-dy} {bw},0" fill="#a97a44"/>'
          f'<polygon points="{bw*.30},{-bh} {bw*.30+dx},{-bh-dy} {bw*.30+dx+14},{-bh-dy} {bw*.30+14},{-bh}" fill="#e6c48f" fill-opacity=".9"/>'
          + plate(k, 40, -bh / 2, 64, 34, r=3) +
          f'<g transform="translate(78,{-bh+14})"><g class="{p}drop"><rect width="28" height="38" rx="2.5" fill="#fff" stroke="#00000022"/>'
          f'<rect x="4" y="4" width="9" height="9" fill="{k["accent"]}"/><rect x="16" y="5" width="8" height="2" fill="#2b2f3a"/><rect x="16" y="9" width="8" height="2" fill="#2b2f3a"/>'
          + "".join(f'<rect x="{4+i*3.1:.1f}" y="18" width="{1 if i%3 else 2}" height="16" fill="#1c202b"/>' for i in range(8)) +
          f'</g></g>'
          f'<g style="opacity:0" class="{p}laser"><rect x="-6" y="{-bh}" width="14" height="{bh}" fill="url(#{p}trail)"/><rect x="7" y="{-bh}" width="2.4" height="{bh}" fill="{k["accent"]}"/></g></g>')
    s += timer(k, p, 202, 112, dur, .95)
    s += operador(k, p, 330, GROUND + 16, flip=True, dur=dur, at=62, sc=1.2)
    trail = (f'<linearGradient id="{p}trail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{k["accent"]}" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="{k["accent"]}" stop-opacity=".55"/></linearGradient>')
    return frame(k, p, s, f"Aguardando postagem - {k['name']}", trail)


def _depot(k, wx, wy, ww, wh, hole, h_logo, logo_w, roof=16, logo_cx=None):
    """Galpao em primeiro plano (base abaixo da faixa do caminhao): a parede oculta o caminhao que passa atras, e o vao (hole) deixa ve-lo.
    A borda do vao e inclinada (ocultacao angular). Retorna (interior, parede) para desenhar o caminhao entre os dois."""
    hy0 = min(y for _, y in hole)
    topo = wy - wh
    cy_logo = (topo + hy0) / 2
    assert topo + 4 <= cy_logo - h_logo / 2 and cy_logo + h_logo / 2 <= hy0 - 4, "logo do galpao colide com telhado/vao"
    inner = "M" + " L".join(f"{x},{y}" for x, y in hole) + " Z"
    if hole[1][0] == wx + ww and hole[2][0] == wx + ww:               # vao aberto ate a borda direita: parede em L (sem aresta sobre o vao)
        contorno = f"M{wx},{topo} H{wx+ww} V{hy0} L{hole[0][0]},{hy0} L{hole[3][0]},{wy} H{wx} Z"
        rule = ""
    else:
        contorno = f"M{wx},{topo} H{wx+ww} V{wy} H{wx} Z {inner}"
        rule = ' fill-rule="evenodd"'
    interior = (f'<path d="{inner}" fill="#000" fill-opacity=".84"/>'
                f'<path d="{inner}" fill="{k["door"]}" fill-opacity=".10"/>')
    parede = (f'<path d="{contorno}"{rule} fill="{k["panel"]}"/>'
              f'<path d="{contorno}"{rule} {wall(k)}/>'
              f'<polygon points="{wx-6},{topo} {wx+ww+6},{topo} {wx+ww},{topo-roof} {wx},{topo-roof}" fill="{k["ink"]}" fill-opacity=".26"/>'
              + plate(k, wx + ww / 2 if logo_cx is None else logo_cx, cy_logo, logo_w, h_logo, r=5, bg=False))
    return interior, parede


def _camadas_caminhao(k, p, base, anims, wheels, dur, sw, b_primeiro, beam=False):
    """Caminhao em duas camadas com a MESMA animacao: ATRAS da parede (dentro da garagem) e NA FRENTE dela (na pista). A troca de camada
    acontece em sw% do ciclo, quando o caminhao esta todo sobre o vao (nenhuma parede o cobre), entao a troca e invisivel.
    Sombra unica (uma so, para nao dobrar a transparencia). Retorna (estilos, sombra, camada_de_tras, camada_da_frente)."""
    if b_primeiro:      # sai da garagem: comeca atras (com fade-in dentro do vao escuro) e termina na frente
        vb = f"0%,{sw}%{{opacity:1}}{sw+.01:.2f}%,100%{{opacity:0}}"
        va = f"0%,{sw}%{{opacity:0}}{sw+.01:.2f}%,100%{{opacity:1}}"
    else:               # entra na garagem: comeca na frente e termina atras
        va = f"0%,{sw}%{{opacity:1}}{sw+.01:.2f}%,100%{{opacity:0}}"
        vb = f"0%,{sw}%{{opacity:0}}{sw+.01:.2f}%,100%{{opacity:1}}"
    kf = f'<style>@keyframes {p}ob{{{vb}}}@keyframes {p}oa{{{va}}}</style>'

    anims = [anims] if isinstance(anims, str) else list(anims)
    abre = "".join(f'<g style="{a}">' for a in anims)
    fecha = "</g>" * len(anims)

    def camada(nome):
        return (f'<g style="animation:{p}{nome} {dur}s linear infinite"><g transform="translate({base[0]},{base[1]}) scale({base[2]})">{abre}'
                + truck(k, p, 0, 0, 1.0, wheels=wheels, beam=beam, shadow=False) + f'{fecha}</g></g>')
    sombra = (f'<g transform="translate({base[0]},{base[1]}) scale({base[2]})">{abre}'
              f'<ellipse cx="96" cy="0" rx="100" ry="3" fill="#000" fill-opacity=".28"/>{fecha}</g>')
    return kf, sombra, camada("ob"), camada("oa")


def _caixa_portao(k, hx0, hx1, top, h=16):
    """Parte de cima do portao (rolo/caixa do portao), sempre visivel no alto do vao."""
    return (f'<rect x="{hx0}" y="{top}" width="{hx1-hx0}" height="{h}" fill="{k["door"]}" fill-opacity=".95"/>'
            + "".join(f'<line x1="{hx0}" x2="{hx1}" y1="{top+i*5}" y2="{top+i*5}" stroke="#000" stroke-opacity=".28"/>' for i in (1, 2)) +
            f'<rect x="{hx0}" y="{top+h-3}" width="{hx1-hx0}" height="3" fill="#000" fill-opacity=".35"/>')


def scene_transferencia(k, p):
    """Garagem cortada pela borda esquerda do quadro. O caminhao ja esta na linha da rua, dentro do vao: o portao abre, ele sai (passando a frente
    da pilastra direita) e o portao fecha. Sem mover o caminhao de lado."""
    dur = 9.0
    s = f'<g mask="url(#{p}fade)">' + skyline(k, p, scroll=False) + road(k, p, moving=False) + "</g>" + props_ambient(k, p, "transf")
    wy, topo = 276, 112
    wx, ww = -60, 260                                                       # a parede passa da borda esquerda; pilastra direita de 188 a 200
    hx0, hx1, hy0 = -50, 188, 187
    hole = [(hx0, hy0), (hx1, hy0), (hx1, wy), (hx0, wy)]
    h_logo = 36 if k["ar"] > 2.5 else 40
    interior, parede = _depot(k, wx, wy, ww, wy - topo, hole, h_logo, 132, roof=14, logo_cx=100)
    placa = (f'<rect x="367" y="176" width="3" height="58" fill="{k["ink"]}" fill-opacity=".5"/>'
             f'<rect x="350" y="160" width="36" height="22" rx="3" fill="{k["cab"]}" stroke="{k["accent"]}" stroke-width="1.6"/>'
             f'<path d="M357,171 H377 M371,165.5 L377,171 L371,176.5" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
    base = (24, wy - 2, .8)                                                 # ja na linha da rua, dentro do vao
    kf = (f'<style>@keyframes {p}tx{{0%,24%{{transform:translateX(0)}}100%{{transform:translateX({(470-24)/.8:.1f}px)}}}}'
          f'@keyframes {p}wsp{{0%,24%{{transform:rotate(0)}}100%{{transform:rotate(2600deg)}}}}'
          f'@keyframes {p}gt{{0%,10%{{transform:scaleY(1)}}22%,74%{{transform:scaleY(.02)}}86%,100%{{transform:scaleY(1)}}}}'
          f'@keyframes {p}gi{{0%,12%{{opacity:0}}22%,74%{{opacity:1}}86%,100%{{opacity:0}}}}</style>')
    estilos, sombra, atras, frente = _camadas_caminhao(
        k, p, base, f"animation:{p}tx {dur}s cubic-bezier(.5,0,.8,.8) infinite", f"style:animation:{p}wsp {dur}s cubic-bezier(.5,0,.8,.8) infinite", dur, 26, True, beam=True)
    s += placa + operador(k, p, 228, GROUND + 16, flip=True, dur=dur, at=24, sc=.95)          # na faixa de tras: o caminhao passa a frente dele
    s += (kf + estilos + interior + f'<g style="opacity:1;animation:{p}gi {dur}s ease-in-out infinite"><rect x="{hx0}" y="{hy0}" width="{hx1-hx0}" height="{wy-hy0}" fill="{k["door"]}" fill-opacity=".12"/></g>'
          + sombra + atras + rollgate(k, hx0, hy0 + 16, hx1 - hx0, wy - hy0 - 16, f"transform:scaleY(1);animation:{p}gt {dur}s ease-in-out infinite", op="1")
          + parede + _caixa_portao(k, hx0, hx1, hy0) + frente)
    return frame(k, p, s, f"Pedido em transferencia entre unidades - {k['name']}")


def scene_chegada(k, p):
    """Garagem cortada pela borda direita do quadro. O caminhao chega na linha da rua, passa a frente da pilastra esquerda e entra no vao com o
    portao aberto; o portao fecha. Sem mover o caminhao de lado."""
    dur = 9.0
    s = f'<g mask="url(#{p}fade)">' + skyline(k, p, scroll=False) + road(k, p, moving=False) + "</g>" + props_ambient(k, p, "cheg")
    wy, topo = 276, 112
    wx, ww = 200, 260                                                       # pilastra esquerda de 200 a 212; a parede passa da borda direita
    hx0, hx1, hy0 = 212, 450, 187
    hole = [(hx0, hy0), (hx1, hy0), (hx1, wy), (hx0, wy)]
    h_logo = 36 if k["ar"] > 2.5 else 40
    interior, parede = _depot(k, wx, wy, ww, wy - topo, hole, h_logo, 132, roof=14, logo_cx=300)
    base = (8, wy - 2, .8)
    X = lambda x: _tf(x, wy - 2, .8, base)
    kf = (f'<style>@keyframes {p}tr{{0%{{transform:{X(-190)};animation-timing-function:cubic-bezier(.2,.7,.25,1)}}'
          f'24%{{transform:{X(8)};animation-timing-function:linear}}40%{{transform:{X(8)};animation-timing-function:ease-in-out}}'
          f'58%,100%{{transform:{X(224)}}}}}'
          f'@keyframes {p}wsp{{0%{{transform:rotate(0);animation-timing-function:cubic-bezier(.2,.7,.25,1)}}24%{{transform:rotate(1000deg);animation-timing-function:linear}}'
          f'40%{{transform:rotate(1000deg);animation-timing-function:ease-in-out}}58%,100%{{transform:rotate(2000deg)}}}}'
          f'@keyframes {p}gt{{0%,26%{{transform:scaleY(1)}}38%,72%{{transform:scaleY(.02)}}82%,100%{{transform:scaleY(1)}}}}'
          f'@keyframes {p}gi{{0%,28%{{opacity:0}}38%,72%{{opacity:1}}82%,100%{{opacity:0}}}}</style>')
    estilos, sombra, atras, frente = _camadas_caminhao(k, p, base, f"animation:{p}tr {dur}s linear infinite", f"style:animation:{p}wsp {dur}s linear infinite", dur, 58, False)
    s += operador(k, p, 184, GROUND + 16, flip=True, dur=dur, at=26, sc=.95)          # operador confere a entrada (faixa de tras: o caminhao passa a frente dele)
    s += (kf + estilos + interior + f'<g style="opacity:1;animation:{p}gi {dur}s ease-in-out infinite"><rect x="{hx0}" y="{hy0}" width="{hx1-hx0}" height="{wy-hy0}" fill="{k["door"]}" fill-opacity=".12"/></g>'
          + sombra + atras + rollgate(k, hx0, hy0 + 16, hx1 - hx0, wy - hy0 - 16, f"transform:scaleY(1);animation:{p}gt {dur}s ease-in-out infinite", op="1")
          + parede + _caixa_portao(k, hx0, hx1, hy0) + frente)
    return frame(k, p, s, f"Pedido chegou na franquia - {k['name']}")


def scene_devolvido(k, p):
    """Caixa dentro do galpao do remetente: o portao fecha em sincronia com o check sendo desenhado; operador confere."""
    dur = 6.0
    s = f'<g mask="url(#{p}fade)">' + skyline(k, p, scroll=False) + road(k, p, moving=False) + "</g>" + props_ambient(k, p, "devd")
    wx, wy, ww, wh = 84, GROUND + 2, 232, 140
    dw, dh = 132, 90
    fs, dx = facade(k, wx, wy, ww, wh, dw, dh, 40 if k["ar"] <= 2.5 else 36, roof=16, logo_w=150)
    kf = f'<style>@keyframes {p}gt{{0%,8%{{transform:scaleY(.07)}}40%,84%{{transform:scaleY(1)}}100%{{transform:scaleY(.07)}}}}</style>'
    s += (fs + f'<rect x="{dx}" y="{wy-dh}" width="{dw}" height="{dh}" fill="#000" fill-opacity=".78"/>'
          f'<rect x="{dx}" y="{wy-dh}" width="{dw}" height="80" fill="{k["door"]}" fill-opacity=".10"/>'
          f'<rect x="{dx+18}" y="{wy-10}" width="{dw-36}" height="7" rx="1.5" fill="{k["ink"]}" fill-opacity=".34"/>'
          f'<g class="{p}bob">{box(k, p, dx+dw/2-33, wy-8, 66, 48)}</g>' + kf +
          rollgate(k, dx, wy - dh, dw, dh, f"transform:scaleY(1);animation:{p}gt {dur}s ease-in-out infinite") +
          f'<rect x="{dx}" y="{wy-dh}" width="{dw}" height="7" fill="{k["door"]}"/>')
    s += operador(k, p, 46, GROUND + 16, flip=False, dur=dur, at=40, sc=.95)
    s += seal(k, p, wx + ww - 4, wy - wh - 6, 24, dur=dur, at=6, t0=8, t1=40, out=84)
    return frame(k, p, s, f"Pedido devolvido ao remetente - {k['name']}")


def _burst(k, p, ox, oy, dur, at):
    """Confete que estoura em at% do ciclo (itens da personalidade: figurinhas, cartoes, estrelas)."""
    kf = (f'<style>@keyframes {p}bu{{0%,{at}%{{opacity:0;transform:translate(0,0) rotate(0)}}{at+3}%{{opacity:1}}{at+22}%{{transform:translate(var(--dx),calc(var(--dy) - 22px)) rotate(120deg)}}'
          f'{at+38}%{{opacity:1}}{min(at+46, 96)}%,100%{{opacity:0;transform:translate(var(--dx),calc(var(--dy) + 46px)) rotate(240deg)}}}}</style>')
    pos = [(-62, -46), (-40, -70), (-14, -84), (14, -84), (40, -70), (62, -46), (-52, -20), (52, -20)]
    cores = [k["accent"], "#ffffff", k["ink"], k["accent"], "#ffffff", k["ink"], k["accent"], "#ffffff"]
    s = kf
    for i, (dx, dy) in enumerate(pos):
        if k["prop"] == "packs" and i % 2 == 0:
            item = pack(0, 0, 0, "")
        elif k["prop"] == "cards" and i % 2 == 0:
            item = cardpiece(k, 0, 0, 0, "", .8)
        elif k["prop"] == "spot" and i % 2 == 0:
            item = '<path d="M0,-6 L1.6,-1.6 L6,0 L1.6,1.6 L0,6 L-1.6,1.6 L-6,0 L-1.6,-1.6 Z" fill="#fff"/>'
        else:
            item = f'<rect x="-3" y="-3" width="6" height="6" rx="1" fill="{cores[i]}"/>'
        s += f'<g transform="translate({ox},{oy})"><g style="opacity:0;--dx:{dx}px;--dy:{dy}px;animation:{p}bu {dur}s ease-out infinite">{item}</g></g>'
    return s


def scene_entregue(k, p):
    """O entregador sai de tras da van com a caixa, entrega ao morador (que pula de alegria), volta para tras da van enquanto o
    morador fecha a porta. Ciclo continuo: ninguem aparece nem some do nada."""
    dur, SP = 9.5, .78
    s = f'<g mask="url(#{p}fade)">' + skyline(k, p, scroll=False) + road(k, p, moving=False) + "</g>" + props_ambient(k, p, "entr")
    hx, hy, hw, hh = 250, GROUND + 4, 124, 62
    dw, dh = 34, 54
    dx = hx + 12
    dcx = dx + dw / 2
    roof = f'{hx-10},{hy-hh} {hx+hw/2},{hy-hh-30} {hx+hw+10},{hy-hh}'
    s += (f'<rect x="{hx}" y="{hy-hh}" width="{hw}" height="{hh}" fill="{k["panel"]}"/><polygon points="{roof}" fill="{k["panel"]}"/>'
          f'<rect x="{hx}" y="{hy-hh}" width="{hw}" height="{hh}" fill="{k["ink"]}" fill-opacity=".14" stroke="{k["ink"]}" stroke-opacity=".28"/>'
          f'<polygon points="{roof}" fill="{k["ink"]}" fill-opacity=".22"/>'
          f'<rect x="{hx+62}" y="{hy-48}" width="44" height="24" rx="2" fill="#ffd27a" fill-opacity=".22" stroke="{k["ink"]}" stroke-opacity=".3"/>'
          f'<line x1="{hx+84}" x2="{hx+84}" y1="{hy-48}" y2="{hy-24}" stroke="{k["ink"]}" stroke-opacity=".3"/>'
          f'<rect x="{dx}" y="{hy-dh}" width="{dw}" height="{dh}" fill="#241b2b" fill-opacity=".94"/>'
          f'<rect x="{dx}" y="{hy-dh+14}" width="{dw}" height="{dh-14}" fill="#ffd27a" fill-opacity=".30"/>')
    cx0, cx1, cy = 118, 240, GROUND + 14                                     # comeca escondido atras da van e para diante da porta
    D = cx1 - cx0
    ch_x, ch_y = dcx - 16, hy - 12                                          # caixa junto ao peito do morador (canto inferior esq.)
    car_hand = (cx0 + 20 * SP - 13.5, cy - 35 * SP + 10)                    # caixa nas maos do entregador (no inicio)
    r0 = (car_hand[0] - ch_x, car_hand[1] - ch_y)
    r1 = (r0[0] + D, r0[1])
    kf = (f'<style>@keyframes {p}cw{{0%,6%{{transform:translateX(0) scaleX(1)}}30%,53%{{transform:translateX({D}px) scaleX(1)}}53.5%,56%{{transform:translateX({D}px) scaleX(-1)}}'
          f'80%,95%{{transform:translateX(0) scaleX(-1)}}96%,100%{{transform:translateX(0) scaleX(1)}}}}'
          f'@keyframes {p}bx{{0%,6%{{transform:translate({r0[0]:.1f}px,{r0[1]:.1f}px)}}30%,35%{{transform:translate({r1[0]:.1f}px,{r1[1]:.1f}px)}}39%{{transform:translate({r1[0]*.4:.1f}px,{r1[1]-9:.1f}px)}}43%,100%{{transform:translate(0,0)}}}}'
          f'@keyframes {p}wv{{0%,28%{{transform:rotate(0)}}34%{{transform:rotate(8deg)}}38%{{transform:rotate(-6deg)}}44%{{transform:rotate(-78deg)}}48%{{transform:rotate(-52deg)}}'
          f'52%{{transform:rotate(-78deg)}}56%{{transform:rotate(-50deg)}}62%,100%{{transform:rotate(0)}}}}'
          f'@keyframes {p}ra{{0%,26%{{transform:rotate(-8deg)}}32%,37%{{transform:rotate(40deg)}}43%,74%{{transform:rotate(-14deg)}}80%,100%{{transform:rotate(-8deg)}}}}'
          f'@keyframes {p}hp{{0%,45%{{transform:translateY(0)}}48%{{transform:translateY(-6px)}}51%{{transform:translateY(0)}}54%{{transform:translateY(-6px)}}57%,100%{{transform:translateY(0)}}}}'
          f'@keyframes {p}lf{{0%,4%{{transform:translateX(0) scaleX(1)}}12%,66%{{transform:translateX({dw}px) scaleX(.18)}}76%,100%{{transform:translateX(0) scaleX(1)}}}}</style>')
    s += kf
    # morador na porta, de frente para o entregador (as maos descem para receber a caixa e sobem ao peito; pula de alegria)
    s += (f'<g style="animation:{p}hp {dur}s ease-in-out infinite"><g transform="translate({dcx+5},{hy-2}) scale({-SP},{SP})">'
          + person(k, SHIRT, hair="#3a2c24", stripes=False) +
          f'<g transform="translate(5,-35)"><g style="transform-origin:0 0;animation:{p}ra {dur}s ease-in-out infinite"><rect x="0" y="-2" width="15" height="4" rx="2" fill="{SHIRT}"/></g></g></g></g>')
    # entregador: sai de tras da van com a caixa, entrega, faz joinha, vira e volta para tras da van
    s += (f'<g transform="translate({cx0},{cy})"><g style="animation:{p}cw {dur}s ease-in-out infinite"><g transform="scale({SP})"><g class="{p}bob">'
          + person(k, k["accent"], cap=k["cab"]) +
          f'<g transform="translate(5,-35)"><g style="transform-origin:0 0;animation:{p}wv {dur}s ease-in-out infinite"><rect x="0" y="-2" width="15" height="4" rx="2" fill="{k["accent"]}"/></g></g></g></g></g></g>')
    # caixa: acompanha o entregador, passa para o morador (mesmo pulo dele) e fica com ele
    s += (f'<g transform="translate({ch_x:.1f},{ch_y})"><g style="animation:{p}bx {dur}s ease-in-out infinite"><g style="animation:{p}hp {dur}s ease-in-out infinite">'
          f'<g transform="scale(.5)">{box(k, p, 0, 0)}</g></g></g></g>')
    # folha da porta: abre para o lado e fecha no final (o morador entra com a caixa)
    s += (f'<g transform="translate({dx},{hy-dh})"><g style="transform-origin:0 0;animation:{p}lf {dur}s ease-in-out infinite">'
          f'<rect width="{dw}" height="{dh}" fill="{k["door"]}"/><circle cx="{dw-6}" cy="{dh*.55:.1f}" r="1.9" fill="#fff3c4"/></g></g>')
    s += truck(k, p, 8, VEH_Y, .8, wheels=False)                             # van na frente do entregador (ele sai de tras dela e volta para tras dela)
    s += seal(k, p, hx + hw / 2, 104, 18, dur=dur, at=44, t0=48, t1=56, out=90)
    s += _burst(k, p, dcx, hy - 70, dur, 44)
    return frame(k, p, s, f"Pedido entregue - {k['name']}")


SCENE_FUNCS = {
    "aguardando_postagem": scene_aguardando,
    "preparacao_transporte": scene_preparacao,
    "transferencia_franquia": scene_transferencia,
    "chegada_franquia": scene_chegada,
    "em_rota_entrega": scene_em_rota,
    "atencao": scene_atencao,
    "devolucao": scene_devolucao,
    "devolvido": scene_devolvido,
    "entregue": scene_entregue,
}

# prefixo curto e unico por (cliente, status): evita colisao de ids/classes entre cenas na mesma pagina
SID_PFX = {"aguardando_postagem": "ap", "preparacao_transporte": "pt", "transferencia_franquia": "tf", "chegada_franquia": "cf",
           "em_rota_entrega": "er", "atencao": "at", "devolucao": "dv", "devolvido": "dd", "entregue": "en"}


def prefixo(client, sid):
    return f"{KITS[client]['pfx']}{SID_PFX[sid]}_"


def scenes_for(client):
    """{status: svg} do cliente (sem os status que o cliente trata a parte)."""
    kit, skip = KITS[client], SEM_CENA.get(client, set())
    return {sid: fn(kit, prefixo(client, sid)) for sid, fn in SCENE_FUNCS.items() if sid not in skip}
