# -*- coding: utf-8 -*-
"""Gera banner, terminal e divisor Matrix (SVG animado) em ../assets."""
import random
from xml.sax.saxutils import escape

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
random.seed(2026)
GREEN = "#00ff41"

# ---------------------------------------------------------------- BANNER
W, H = 1000, 300
pool = list("ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ") + list("0123456789:.=*+<>|Z01")

def rain_layer(step, size, lh, nmin, nmax, dmin, dmax, opacity, x0):
    out = []
    x = x0
    while x < W:
        n = random.randint(nmin, nmax)
        dur = random.uniform(dmin, dmax)
        delay = -random.uniform(0, dur)
        ts = []
        for i in range(n):
            c = escape(random.choice(pool))
            if i == n - 1:
                fill, op = "#d9ffe3", 1.0
            elif i == n - 2:
                fill, op = "#7dff9f", 0.95
            else:
                fill, op = GREEN, max(0.07, (i / (n - 2)) ** 1.6 * 0.85)
            dy = 0 if i == 0 else lh
            ts.append(f'<tspan x="{x}" dy="{dy}" fill="{fill}" fill-opacity="{op:.2f}">{c}</tspan>')
        out.append(
            f'<text class="f" y="0" style="animation-duration:{dur:.2f}s;animation-delay:{delay:.2f}s">{"".join(ts)}</text>'
        )
        x += step
    return f'<g font-size="{size}" opacity="{opacity}">' + "".join(out) + "</g>"

far = rain_layer(20, 10, 12, 10, 20, 9, 16, 0.38, 10)
near = rain_layer(14, 14, 16, 8, 17, 4.5, 10, 1, 7)

CH = 13.2  # largura de caractere em 22px
lines = ["Wake up, Luna...", "The Matrix has you...", "Follow the white rabbit."]
D = 12.0
clips, texts = [], []
kt, xs = [0.0], []
for i, t in enumerate(lines):
    w = len(t) * CH
    x0 = (W - w) / 2
    a = i / 3
    times = [0, a, a + 0.12, a + 0.30, a + 0.33, 1]
    vals = [0, 0, w, w, 0, 0]
    clips.append(
        f'<clipPath id="cl{i}"><rect x="{x0:.1f}" y="188" height="36" width="0">'
        f'<animate attributeName="width" dur="{D}s" repeatCount="indefinite" '
        f'keyTimes="{";".join(f"{v:.4f}" for v in times)}" values="{";".join(f"{v:.1f}" for v in vals)}"/></rect></clipPath>'
    )
    texts.append(
        f'<text x="{x0:.1f}" y="212" font-size="22" fill="{GREEN}" textLength="{w:.1f}" lengthAdjust="spacing" '
        f'clip-path="url(#cl{i})" filter="url(#glow)">{escape(t)}</text>'
    )
# cursor unico percorrendo as 3 linhas
ck, cv = [], []
for i, t in enumerate(lines):
    w = len(t) * CH
    x0 = (W - w) / 2
    a = i / 3
    for tt, xx in [(a, x0), (a + 0.12, x0 + w), (a + 0.30, x0 + w), (a + 0.33, x0)]:
        if ck and tt <= ck[-1]:
            tt = ck[-1] + 0.0001
        ck.append(tt); cv.append(xx)
ck.append(1.0); cv.append(cv[0])
ck[0] = 0.0
cursor = (
    f'<g class="b"><rect y="190" width="11" height="30" fill="{GREEN}" filter="url(#glow)">'
    f'<animate attributeName="x" dur="{D}s" repeatCount="indefinite" '
    f'keyTimes="{";".join(f"{v:.4f}" for v in ck)}" values="{";".join(f"{v:.1f}" for v in cv)}"/></rect></g>'
)

banner = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Luna Lab - Matrix digital rain banner">
<title>LUNA LAB // lunalab2026</title>
<defs>
<style>
text{{font-family:'MS Gothic','Noto Sans Mono CJK JP','Courier New',Courier,monospace}}
.f{{animation-name:fall;animation-timing-function:linear;animation-iteration-count:infinite}}
.t{{font-family:'Courier New',Courier,'Liberation Mono','DejaVu Sans Mono',monospace;font-weight:bold}}
.g1{{animation:g1 5s infinite}}
.g2{{animation:g2 5s infinite .12s}}
.b{{animation:blink 1s steps(1) infinite}}
.s{{animation:scan 4.5s linear infinite}}
.k{{animation:blink 2s steps(1) infinite}}
@keyframes fall{{from{{transform:translateY(-300px)}}to{{transform:translateY(330px)}}}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
@keyframes scan{{from{{transform:translateY(-70px)}}to{{transform:translateY(310px)}}}}
@keyframes g1{{0%,88%,100%{{opacity:0;transform:translate(0,0)}}89%{{opacity:.85;transform:translate(-6px,2px)}}91%{{opacity:0}}93%{{opacity:.75;transform:translate(5px,-2px)}}95%{{opacity:0}}}}
@keyframes g2{{0%,88%,100%{{opacity:0;transform:translate(0,0)}}90%{{opacity:.8;transform:translate(6px,-1px)}}92%{{opacity:0}}94%{{opacity:.7;transform:translate(-5px,2px)}}96%{{opacity:0}}}}
</style>
<filter id="glow" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<radialGradient id="vig" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#000" stop-opacity=".93"/><stop offset=".7" stop-color="#000" stop-opacity=".72"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<linearGradient id="scanG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset=".5" stop-color="{GREEN}" stop-opacity=".16"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></linearGradient>
<pattern id="lines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".28"/></pattern>
{"".join(clips)}
</defs>
<rect width="{W}" height="{H}" fill="#000800"/>
{far}
{near}
<ellipse cx="500" cy="150" rx="430" ry="125" fill="url(#vig)"/>
<rect class="s" width="{W}" height="70" fill="url(#scanG)"/>
<rect width="{W}" height="{H}" fill="url(#lines)"/>
<text x="500" y="92" font-size="14" text-anchor="middle" fill="{GREEN}" fill-opacity=".85" textLength="330" lengthAdjust="spacing">&gt; SYSTEM.BOOT // lunalab2026 <tspan class="k">_</tspan></text>
<g class="t" font-size="72" text-anchor="middle">
<text class="g1" x="500" y="162" fill="#ff2a55" textLength="410" lengthAdjust="spacing">LUNA LAB</text>
<text class="g2" x="500" y="162" fill="#00ffd5" textLength="410" lengthAdjust="spacing">LUNA LAB</text>
<text x="500" y="162" fill="{GREEN}" textLength="410" lengthAdjust="spacing" filter="url(#glow)">LUNA LAB</text>
</g>
{"".join(texts)}
{cursor}
<text x="500" y="262" font-size="13" text-anchor="middle" fill="{GREEN}" fill-opacity=".6" textLength="440" lengthAdjust="spacing">[ JAVASCRIPT | TYPESCRIPT | REACT | NODE.JS | PYTHON ]</text>
<rect x="3" y="3" width="{W-6}" height="{H-6}" rx="6" fill="none" stroke="{GREEN}" stroke-opacity=".45"/>
<path d="M3 30V3h30M{W-33} 3h30v27M3 {H-30}v27h30M{W-33} {H-3}h30v-27" fill="none" stroke="{GREEN}" stroke-width="3" filter="url(#glow)"/>
</svg>
'''
open(os.path.join(OUT, "matrix-banner.svg"), "w", encoding="utf-8").write(banner)

# ---------------------------------------------------------------- TERMINAL
TW, TH = 860, 340
CW = 9.6
x0, y0, lh = 28, 96, 28
script = [
    ("cmd", "whoami"),
    ("out", "lunalab2026 :: dev curioso, apaixonado por terminal"),
    ("cmd", "cat stack.txt"),
    ("out", "JavaScript | TypeScript | React | Node.js | Python"),
    ("cmd", "git log --oneline -1"),
    ("out", "a1b2c3d feat: construindo algo incrível"),
    ("cmd", "echo $MISSION"),
    ("out", "aprender, construir, compartilhar. repetir."),
    ("cmd", ""),
]
# cronograma
t = 0.8
sched = []
for kind, txt in script:
    full = ("$ " if kind == "cmd" else "> ") + txt
    d = max(0.15, len(txt) * 0.055) if txt else 0.15
    sched.append((t, d, full, kind))
    t += d + (0.45 if kind == "cmd" else 0.75)
DT = t + 4.5
def f(v): return f"{v:.4f}"
els = []
for i, (s, d, full, kind) in enumerate(sched):
    w = len(full) * CW
    y = y0 + i * lh
    kts = [0, s / DT, (s + d) / DT, (DT - 0.5) / DT, 1]
    vals = [0, 0, w, w, 0]
    els.append(
        f'<clipPath id="t{i}"><rect x="{x0}" y="{y-20}" height="28" width="0"><animate attributeName="width" dur="{DT:.2f}s" repeatCount="indefinite" '
        f'keyTimes="{";".join(f(v) for v in kts)}" values="{";".join(f"{v:.1f}" for v in vals)}"/></rect></clipPath>'
    )
for i, (s, d, full, kind) in enumerate(sched):
    w = len(full) * CW
    y = y0 + i * lh
    if kind == "cmd":
        body = f'<tspan fill="{GREEN}" font-weight="bold">$ </tspan><tspan fill="#e6fff0">{escape(full[2:])}</tspan>'
    else:
        body = f'<tspan fill="#00c832">&gt; </tspan><tspan fill="#7dff9f">{escape(full[2:])}</tspan>'
    els.append(f'<text x="{x0}" y="{y}" font-size="16" textLength="{w:.1f}" lengthAdjust="spacing" clip-path="url(#t{i})" xml:space="preserve">{body}</text>')
# cursor
kx, vx, ky, vy = [0.0], [x0 + 2 * CW], [0.0], [y0 - 16]
for i, (s, d, full, kind) in enumerate(sched):
    w = len(full) * CW
    a, b = s / DT, (s + d) / DT
    if i > 0:
        pw = len(sched[i - 1][2]) * CW
        kx.append(a - 0.0005); vx.append(x0 + pw)
        ky.append(a); vy.append(y0 + i * lh - 16)
    kx.append(a); vx.append(x0 + (2 * CW if i == 0 else 0))
    kx.append(b); vx.append(x0 + w)
# garante ordem estrita
def fix(k):
    out = []
    for v in k:
        if out and v <= out[-1]:
            v = out[-1] + 0.0001
        out.append(v)
    return out
kx[0] = 0.0
vx[0] = x0 + 0
kx = fix(kx); kx.append(1.0); vx.append(x0)
ky = fix(ky); ky.append(1.0); vy.append(vy[0])
cursor_t = (
    f'<g class="b"><rect width="9" height="19" fill="{GREEN}">'
    f'<animate attributeName="x" dur="{DT:.2f}s" repeatCount="indefinite" keyTimes="{";".join(f(v) for v in kx)}" values="{";".join(f"{v:.1f}" for v in vx)}"/>'
    f'<animate attributeName="y" dur="{DT:.2f}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{";".join(f(v) for v in ky)}" values="{";".join(f"{v}" for v in vy)}"/>'
    f'</rect></g>'
)
term = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TW} {TH}" width="{TW}" height="{TH}" role="img" aria-label="Terminal animado: whoami, stack, git log">
<title>luna@matrix: ~</title>
<defs>
<style>
text{{font-family:'Courier New',Courier,'Liberation Mono','DejaVu Sans Mono',monospace}}
.b{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
</style>
<filter id="gl" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="sl" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".3"/></pattern>
{"".join(e for e in els if e.startswith("<clipPath"))}
</defs>
<rect x="1" y="1" width="{TW-2}" height="{TH-2}" rx="10" fill="#020a03" stroke="{GREEN}" stroke-opacity=".55" stroke-width="2"/>
<path d="M11 1h{TW-22}a10 10 0 0 1 10 10v22H1V11A10 10 0 0 1 11 1z" fill="#07200c"/>
<circle cx="26" cy="22" r="6" fill="#ff5f56"/><circle cx="48" cy="22" r="6" fill="#ffbd2e"/><circle cx="70" cy="22" r="6" fill="#27c93f"/>
<text x="{TW/2}" y="27" font-size="14" text-anchor="middle" fill="{GREEN}" fill-opacity=".85">luna@matrix: ~/lunalab2026</text>
<g filter="url(#gl)">
{"".join(e for e in els if e.startswith("<text"))}
{cursor_t}
</g>
<rect x="1" y="1" width="{TW-2}" height="{TH-2}" rx="10" fill="url(#sl)"/>
</svg>
'''
open(os.path.join(OUT, "terminal.svg"), "w", encoding="utf-8").write(term)

# ---------------------------------------------------------------- DIVIDER
div = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 34" width="1000" height="34" role="img" aria-label="Divisor Matrix">
<defs>
<linearGradient id="sw" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset=".5" stop-color="{GREEN}"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></linearGradient>
<filter id="g" x="-5%" y="-300%" width="110%" height="700%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<style>text{{font-family:'Courier New',Courier,'Liberation Mono','DejaVu Sans Mono',monospace}}.p{{animation:pulse 2.4s ease-in-out infinite}}@keyframes pulse{{0%,100%{{opacity:.45}}50%{{opacity:1}}}}</style>
</defs>
<rect width="1000" height="34" rx="6" fill="#020a03"/>
<rect x="0" y="16" width="1000" height="2" fill="#003b00"/>
<rect y="15" width="260" height="4" fill="url(#sw)" filter="url(#g)"><animate attributeName="x" from="-260" to="1000" dur="3.2s" repeatCount="indefinite"/></rect>
<rect x="188" y="4" width="624" height="26" fill="#020a03"/>
<text class="p" x="500" y="22" font-size="13" text-anchor="middle" fill="{GREEN}" textLength="600" lengthAdjust="spacing">01001100 01010101 01001110 01000001 :: 01001100 01000001 01000010</text>
</svg>
'''
open(os.path.join(OUT, "divider.svg"), "w", encoding="utf-8").write(div)
print("ok")
