"""Cenas SVG animadas por cliente (portal de rastreio). Saida: static/scenes/<cliente>.js via tools/scenes/build.py."""

import math

import random


KITS = {
    "caoa": dict(name="CAOA", dark=False, panel="#eef0f6", ink="#100c5a", accent="#5dba8d", body="#FFFFFF", bodyStroke="#c9cee0",
                 cab="#100c5a", wall="#FFFFFF", wallOp=".92", wallStroke="#c9cee0", stripe="#5dba8d", plate="#FFFFFF",
                 plateStroke="#d5d8e6", logo="/static/logos/logo-caoa.png?v=1", ar=698 / 198, prop="car", glow="#5dba8d",
                 sky="fill", door="#5dba8d"),
}


WARN, RET = "#FFB020", "#E5484D"
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
@media (prefers-reduced-motion:reduce){svg *{animation:none!important}}
"""


def frame(k, p, inner, label, defs=""):
    css = CSS.replace("__P__", p)
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
    rnd = random.Random(7)
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


def road(k, p, moving=True):
    dash = f'class="{p}dashl"' if moving else 'stroke-dasharray="18 16"'
    return (f'<rect x="0" y="{GROUND}" width="400" height="{ROAD_BOTTOM-GROUND}" fill="{k["ink"]}" fill-opacity=".10"/>'
            f'<line x1="0" x2="400" y1="{GROUND}" y2="{GROUND}" stroke="{k["ink"]}" stroke-opacity=".28" stroke-width="1.5"/>'
            f'<line {dash} x1="0" x2="400" y1="{VEH_Y+8}" y2="{VEH_Y+8}" stroke="{k["ink"]}" stroke-opacity=".32" stroke-width="2"/>')


def plate(k, cx, cy, w, h, unflip=False, r=4, bg=True):
    pad = 3
    iw, ih = w - 2 * pad, h - 2 * pad
    lw, lh = (ih * k["ar"], ih) if iw / ih > k["ar"] else (iw, iw / k["ar"])
    s = ""
    if bg and k.get("plate"):
        s += (f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" rx="{r}" fill="{k["plate"]}" '
              f'stroke="{k.get("plateStroke","#000")}" stroke-width="1.3"/>')
    s += f'<image href="{k["logo"]}" x="{cx-lw/2}" y="{cy-lh/2}" width="{lw}" height="{lh}" preserveAspectRatio="xMidYMid meet"/>'
    if unflip:
        s = f'<g transform="translate({cx},{cy}) scale(-1,1) translate({-cx},{-cy})">{s}</g>'
    return s


def truck(k, p, x, y, scale=1.0, flip=False, wheels=True, beam=False, inner_class=""):
    """Caminhao baú virado p/ direita; ground y=0. flip espelha (logo desespelhado)."""
    fx = -scale if flip else scale
    g = f'<g transform="translate({x},{y}) scale({fx},{scale})"><g class="{inner_class}">'
    g += '<ellipse cx="96" cy="1" rx="102" ry="4" fill="#000" fill-opacity=".28"/>'
    if beam and k["dark"]:
        g += f'<polygon points="192,-36 250,-52 250,-14" fill="url(#{p}beam)"/>'
    neon = 'style="filter:drop-shadow(0 0 3px %s) drop-shadow(0 0 9px rgba(227,55,129,.55))"' % k["accent"] if k.get("neon") else ""
    g += f'<g {neon}>'
    g += '<rect x="0" y="-24" width="192" height="8" rx="2" fill="#15151b"/>'
    g += f'<rect x="0" y="-84" width="130" height="60" rx="6" fill="{k["body"]}"' + (f' stroke="{k["accent"]}" stroke-width="1.6"' if k.get("neon") else (f' stroke="{k["bodyStroke"]}" stroke-width="1.4"' if k.get("bodyStroke") else "")) + '/>'
    g += '<rect x="0" y="-84" width="130" height="7" rx="6" fill="#fff" fill-opacity=".16"/>'
    g += f'<rect x="0" y="-36" width="130" height="8" fill="{k["stripe"]}"/>'
    g += '<line x1="5" y1="-80" x2="5" y2="-30" stroke="#000" stroke-opacity=".25"/>'
    g += plate(k, 66, -58, 108, 40, unflip=flip, bg=False)
    g += (f'<path d="M130,-70 L164,-70 Q172,-70 177,-60 L190,-40 Q192,-37 192,-33 L192,-24 L130,-24 Z" fill="{k["cab"]}"' +
          (f' stroke="{k["accent"]}" stroke-width="1.6"' if k.get("neon") else "") + '/>')
    g += f'<path d="M139,-64 L162,-64 Q167,-64 170,-58 L179,-44 L139,-44 Z" fill="url(#{p}glass)"/>'
    g += '<rect x="186" y="-38" width="6" height="7" rx="2" fill="#fff3c4"/>'
    g += '<rect x="126" y="-24" width="68" height="6" rx="2" fill="#22232b"/></g>'
    for wx in (34, 150):
        spin = f'class="{p}spin"' if wheels else ""
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


def warehouse(k, p, x, y, w=150, op=1.0):
    return (f'<g opacity="{op}"><rect x="{x}" y="{y-74}" width="{w}" height="74" {wall(k)}/>'
            f'<polygon points="{x-6},{y-74} {x+w+6},{y-74} {x+w},{y-88} {x},{y-88}" fill="{k["ink"]}" fill-opacity=".26"/>'
            + plate(k, x + w / 2, y - 60, 104, 34, r=5, bg=False) +
            f'<rect x="{x+w/2-28}" y="{y-38}" width="56" height="38" fill="{k["accent"]}" fill-opacity=".85"/>'
            + "".join(f'<line x1="{x+w/2-28}" x2="{x+w/2+28}" y1="{y-38+i*7}" y2="{y-38+i*7}" stroke="#000" stroke-opacity=".25"/>' for i in range(1, 6)) + '</g>')


def pack(x, y, rot=0, cls=""):
    return (f'<g transform="translate({x},{y}) rotate({rot})"><g class="{cls}"><rect x="-8" y="-11" width="16" height="22" rx="2" fill="#CC0000"/>'
            f'<polygon points="-8,-11 -4,-8 0,-11 4,-8 8,-11 8,-8 -8,-8" fill="#FFD600"/><polygon points="-8,11 -4,8 0,11 4,8 8,11 8,8 -8,8" fill="#FFD600"/>'
            f'<polygon points="0,-5 1.5,-1.5 5,-1 2.3,1.3 3,5 0,3 -3,5 -2.3,1.3 -5,-1 -1.5,-1.5" fill="#FFD600"/></g></g>')


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


def scene_em_rota(k, p):
    s = f'<g mask="url(#{p}fade)">' + skyline(k, p) + road(k, p) + "</g>" + props_ambient(k, p, "rota")
    if k["prop"] == "car":
        s += f'<g transform="translate(470,0)"><g class="{p}car">{car(k, p, 0, GROUND+11)}</g></g>'
    lines = "".join(f'<line class="{p}dashl" style="animation-delay:{i*.15}s" x1="{62-i*6}" x2="{84-i*6}" y1="{VEH_Y-34+i*14}" y2="{VEH_Y-34+i*14}" stroke="{k["ink"]}" stroke-opacity=".28" stroke-width="2" stroke-linecap="round"/>' for i in range(3))
    s += lines + truck(k, p, 104, VEH_Y, 1.0, beam=True, inner_class=f"{p}bob")
    if k["prop"] == "packs":
        s += pack(80, 202, -8, f"{p}float") + f'<g style="animation-delay:-1.6s">{pack(62, 216, 10, p+"float")}</g>'
    return frame(k, p, s, f"Pedido em rota de entrega - {k['name']}")


def scene_atencao(k, p):
    s = f'<g mask="url(#{p}fade)">' + skyline(k, p, scroll=False) + road(k, p, moving=False) + "</g>" + props_ambient(k, p, "atencao")
    s += house(k, p, 262, GROUND + 4, 112, lit=False)
    s += truck(k, p, 18, VEH_Y, .80, wheels=False)
    kn = "".join(f'<path class="{p}k{i+1}" d="M{236-i*7},{GROUND-38} q-5,4 0,8" fill="none" stroke="{WARN}" stroke-width="2" stroke-linecap="round" transform="translate(0,{i*6})"/>' for i in range(3))
    s += courier(k, p, 232, GROUND + 8) + kn + bubble(k, p, 295, 104)
    if k["prop"] == "packs":
        s += pack(196, GROUND - 2, 12)
    return frame(k, p, s, f"Entrega malsucedida, insucesso, nova tentativa em breve - {k['name']}")


def scene_preparacao(k, p):
    s = f'<g mask="url(#{p}fade)">' + skyline(k, p, scroll=False) + f'<rect x="0" y="{GROUND}" width="400" height="{ROAD_BOTTOM-GROUND}" fill="{k["ink"]}" fill-opacity=".10"/>' + "</g>"
    s += props_ambient(k, p, "prep")
    wx, wy, ww, wh = 6, GROUND + 2, 176, 132     # galpao em escala: porta > 2x a altura da caixa
    dw, dh = 104, 84
    dx = wx + ww / 2 - dw / 2
    s += (f'<rect x="{wx}" y="{wy-wh}" width="{ww}" height="{wh}" {wall(k)}/>'
          f'<polygon points="{wx-6},{wy-wh} {wx+ww+6},{wy-wh} {wx+ww},{wy-wh-18} {wx},{wy-wh-18}" fill="{k["ink"]}" fill-opacity=".26"/>'
          + plate(k, wx + ww / 2, wy - wh + 36, 136, 40, r=5, bg=False) +
          f'<rect x="{dx}" y="{wy-dh}" width="{dw}" height="{dh}" fill="#000" fill-opacity=".78"/>'
          f'<rect x="{dx}" y="{wy-dh}" width="{dw}" height="10" fill="{k["accent"]}" fill-opacity=".92"/>'
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
    s = f'<g mask="url(#{p}fade)">' + skyline(k, p, scroll=False) + road(k, p, moving=False) + "</g>"
    wx, wy, ww, wh = 6, GROUND + 2, 150, 132     # galpao em escala: porta maior que a pessoa (58 px)
    dw, dh = 78, 80
    s += (f'<rect x="{wx}" y="{wy-wh}" width="{ww}" height="{wh}" {wall(k)}/>'
          f'<polygon points="{wx-6},{wy-wh} {wx+ww+6},{wy-wh} {wx+ww},{wy-wh-15} {wx},{wy-wh-15}" fill="{k["ink"]}" fill-opacity=".26"/>'
          + plate(k, wx + ww / 2, wy - 100, 112, 34, bg=False) +
          f'<rect x="{wx+ww/2-dw/2}" y="{wy-dh}" width="{dw}" height="{dh}" fill="#000" fill-opacity=".72"/>'
          f'<rect x="{wx+ww/2-dw/2}" y="{wy-dh}" width="{dw}" height="7" fill="{k["accent"]}"/>')
    s += uturn_sign(k, p, 188, 88)
    s += truck(k, p, 214, VEH_Y, .86, wheels=False)
    s += f'<polygon points="212,{VEH_Y-22} 186,{VEH_Y} 194,{VEH_Y} 218,{VEH_Y-18}" fill="#3a3e4a"/>'
    s += walker(k, p, 214, GROUND + 14)
    return frame(k, p, s, f"Pedido em devolucao ao remetente - {k['name']}")


SCENE_FUNCS = {
    "preparacao_transporte": scene_preparacao,
    "em_rota_entrega": scene_em_rota,
    "atencao": scene_atencao,
    "devolucao": scene_devolucao,
}
