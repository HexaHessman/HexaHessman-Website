"""Technical line drawings of three ShibataFenderTeam fender types, in the style of the principal's catalogue
drawings (thin outlines, light grey fill, dashed hidden lines, dash-dot centre lines, dimension arrows), drawn in
HexaHessman green. Writes assets/engineering/draw/{cylindrical,roller,pneumatic}.svg.

Run:  python3 tools/drawings/fenders.py /Users/poopiepie/Hexahessman
"""
import math, sys, os

INK = "#0F2A1E"
STYLE = f"""<style>
.o{{fill:none;stroke:{INK};stroke-width:2.2;stroke-linejoin:round;stroke-linecap:round}}
.f{{fill:{INK};fill-opacity:.07;stroke:{INK};stroke-width:2.2;stroke-linejoin:round}}
.t{{fill:none;stroke:{INK};stroke-width:1.3}}
.h{{fill:none;stroke:{INK};stroke-width:1.6;stroke-dasharray:14 9}}
.c{{fill:none;stroke:{INK};stroke-width:1.3;stroke-dasharray:34 8 4 8}}
.d{{fill:none;stroke:{INK};stroke-width:1.4}}
.a{{fill:{INK}}}
.w{{fill:#FCFCFC;stroke:{INK};stroke-width:2.2}}
text{{font-family:"DIN Alternate","Geist",Arial,sans-serif;fill:{INK};font-size:40px}}
</style>"""


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{STYLE}{body}</svg>\n'


def arrow(x, y, ang, s=22):
    """a filled arrowhead with its tip at (x, y), pointing along ang (radians)"""
    a1, a2 = ang + math.pi - 0.22, ang + math.pi + 0.22
    return f'<path class="a" d="M{x:.1f},{y:.1f} L{x + s * math.cos(a1):.1f},{y + s * math.sin(a1):.1f} L{x + s * math.cos(a2):.1f},{y + s * math.sin(a2):.1f}Z"/>'


def dim_h(x1, x2, y, label, ext_from=None, ty=-22):
    out = f'<line class="d" x1="{x1}" y1="{y}" x2="{x2}" y2="{y}"/>' + arrow(x1, y, math.pi) + arrow(x2, y, 0)
    if ext_from is not None:
        for x in (x1, x2):
            out += f'<line class="t" x1="{x}" y1="{ext_from}" x2="{x}" y2="{y + 18}"/>'
    return out + f'<text x="{(x1 + x2) / 2}" y="{y + ty}" text-anchor="middle">{label}</text>'


def dim_v(x, y1, y2, label, ext_from=None, tx=-26):
    out = f'<line class="d" x1="{x}" y1="{y1}" x2="{x}" y2="{y2}"/>' + arrow(x, y1, -math.pi / 2) + arrow(x, y2, math.pi / 2)
    if ext_from is not None:
        for y in (y1, y2):
            out += f'<line class="t" x1="{ext_from}" y1="{y}" x2="{x + 18}" y2="{y}"/>'
    return out + f'<text x="{x + tx}" y="{(y1 + y2) / 2 + 14}" text-anchor="middle">{label}</text>'


def chain(x1, y1, x2, y2, link=34, wide=17):
    """a chain from (x1,y1) to (x2,y2): alternating face-on links (rounded outline with a slot) and edge-on links"""
    L = math.hypot(x2 - x1, y2 - y1); n = max(2, int(L // (link * 0.82)))
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    out = ''
    for i in range(n):
        t = (i + 0.5) / n; cx, cy = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        if i % 2 == 0:
            out += (f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({ang:.1f})">'
                    f'<rect class="w" x="{-link / 2}" y="{-wide / 2}" width="{link}" height="{wide}" rx="{wide / 2}"/>'
                    f'<rect class="t" x="{-link / 2 + 8}" y="-2.5" width="{link - 16}" height="5" rx="2.5"/></g>')
        else:
            out += (f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({ang:.1f})">'
                    f'<rect class="w" x="{-link / 2}" y="-4" width="{link}" height="8" rx="4"/></g>')
    return out


def hatch(x, y1, y2, side=1, step=34, w=60):
    out = f'<line class="o" x1="{x}" y1="{y1}" x2="{x}" y2="{y2}"/>'
    for y in range(int(y1), int(y2), step):
        out += f'<line class="t" x1="{x}" y1="{y + 30}" x2="{x + side * w}" y2="{y - 10}" stroke-dasharray="22 8"/>'
    return out


# ---------------------------------------------------------------- cylindrical fender, chain-hung
def cylindrical():
    b = ''
    for px in (280, 858):   # wall plates with four bolts and a shackle bar
        b += f'<rect class="f" x="{px}" y="77" width="106" height="106"/>'
        for bx, by in ((14, 14), (92, 14), (14, 92), (92, 92)):
            b += f'<circle class="w" cx="{px + bx}" cy="{77 + by}" r="8"/><circle class="a" cx="{px + bx}" cy="{77 + by}" r="2.6"/>'
        b += f'<rect class="w" x="{px + 46}" y="88" width="14" height="66" rx="7"/><rect class="w" x="{px + 34}" y="138" width="38" height="18" rx="4"/>'
    b += chain(333, 160, 333, 340) + chain(911, 160, 911, 340)
    # bar through the bore, end brackets
    b += '<rect class="f" x="356" y="362" width="532" height="46" rx="4"/>'
    b += '<path class="f" d="M312,352 L342,334 L362,350 L362,412 L344,412 Z"/><circle class="w" cx="333" cy="352" r="11"/>'
    b += '<path class="f" d="M932,352 L902,334 L882,350 L882,412 L900,412 Z"/><circle class="w" cx="911" cy="352" r="11"/>'
    # the rubber body
    b += '<rect class="f" x="398" y="295" width="450" height="260"/>'
    for y in (312, 328, 522, 539):
        b += f'<line class="t" x1="398" y1="{y}" x2="848" y2="{y}"/>'
    for y in (362, 408, 490):
        b += f'<line class="h" x1="400" y1="{y}" x2="846" y2="{y}"/>'
    b += '<line class="c" x1="370" y1="425" x2="880" y2="425"/>'
    b += dim_h(398, 848, 675, 'L', ext_from=575)
    # side view against the quay wall
    b += hatch(1437, 12, 742)
    b += '<path class="f" d="M1437,82 L1414,82 L1388,150 L1398,182 L1437,182 Z"/><circle class="w" cx="1404" cy="148" r="10"/>'
    b += '<circle class="f" cx="1307" cy="425" r="130"/><circle class="w" cx="1307" cy="425" r="63"/>'
    b += '<path class="f" d="M1290,360 a34,34 0 1 1 52,0 L1328,410 L1304,410 Z"/>'
    b += chain(1400, 160, 1322, 368)
    b += '<line class="c" x1="1160" y1="425" x2="1455" y2="425"/><line class="c" x1="1307" y1="275" x2="1307" y2="575"/>'
    b += dim_h(1178, 1437, 675, 'OD')
    b += '<line class="t" x1="1178" y1="425" x2="1178" y2="693"/>'
    return svg(1700, 754, b)


# ---------------------------------------------------------------- roller / wheel fender
def roller():
    b = ''
    # plan view: frame, wheel, hub housings
    b += '<rect class="f" x="50" y="238" width="520" height="319"/><line class="o" x1="75" y1="238" x2="75" y2="557"/><line class="o" x1="547" y1="238" x2="547" y2="557"/>'
    b += '<rect class="o" x="112" y="280" width="398" height="236"/>'
    b += '<path class="f" d="M248,280 L240,303 L382,303 L374,280 Z"/><path class="f" d="M248,516 L240,492 L382,492 L374,516 Z"/>'
    b += '<rect class="w" x="80" y="303" width="460" height="190" rx="46"/>'
    b += '<line class="t" x1="96" y1="330" x2="524" y2="330"/><line class="t" x1="96" y1="466" x2="524" y2="466"/>'
    b += dim_v(655, 303, 492, 'F', ext_from=540, tx=-22)
    b += dim_v(745, 238, 557, 'H', ext_from=570, tx=-26)
    # side view: mounting plate and fork, the wheel, its deflection
    cx, cy, r = 1180, 407, 228
    b += f'<circle class="f" cx="{cx}" cy="{cy}" r="{r}"/>'
    b += f'<path class="h" d="M{cx - r + 22},{cy + 140} Q{cx},{cy + 186} {cx + r - 22},{cy + 140}"/>'
    b += '<path class="w" d="M918,160 L1438,160 L1410,252 L1372,252 L1240,456 Q1180,520 1120,456 L988,252 L950,252 Z"/>'
    b += f'<circle class="w" cx="{cx}" cy="{cy}" r="56"/>'
    b += f'<line class="c" x1="1100" y1="{cy}" x2="1530" y2="{cy}"/><line class="c" x1="{cx}" y1="330" x2="{cx}" y2="490"/>'
    b += '<text x="1180" y="560" text-anchor="middle" style="font-size:30px">Deflection</text>'
    b += dim_v(1180, 572, 635, '', tx=0)
    b += dim_h(918, 1438, 70, 'A', ty=-14)
    b += '<line class="t" x1="918" y1="60" x2="918" y2="160"/><line class="t" x1="1438" y1="60" x2="1438" y2="160"/>'
    b += dim_v(1520, 160, 407, 'B', ext_from=1440, tx=-26)
    b += dim_v(1610, 160, 635, 'C', ext_from=1440, tx=-26)
    b += dim_h(950, 1406, 728, 'ØD', ty=-20)
    b += '<line class="t" x1="950" y1="407" x2="950" y2="740"/><line class="t" x1="1406" y1="407" x2="1406" y2="740"/><line class="t" x1="1180" y1="635" x2="1620" y2="635"/>'
    return svg(1960, 760, b)


# ---------------------------------------------------------------- pneumatic fender with chain & tyre net
def pneumatic():
    b = '<text x="100" y="100" style="font-size:34px;font-weight:700;letter-spacing:1px">CHAIN &amp; TYRES</text>'
    # the inflated body, hemispherical ends
    b += '<path class="f" d="M330,168 L1030,168 Q1105,168 1105,240 L1105,500 Q1105,572 1030,572 L330,572 Q255,572 255,500 L255,240 Q255,168 330,168 Z"/>'
    xs = (430, 597, 765, 935)
    for x in xs:   # tyres: on top and bottom seen edge-on, two rows face-on, joined by short chain lengths
        for y in (172, 548):
            b += f'<ellipse class="w" cx="{x}" cy="{y}" rx="62" ry="26"/><ellipse class="t" cx="{x}" cy="{y}" rx="36" ry="11"/>'
        for y in (285, 432):
            b += f'<circle class="w" cx="{x}" cy="{y}" r="60"/><circle class="t" cx="{x}" cy="{y}" r="50"/><circle class="w" cx="{x}" cy="{y}" r="32"/>'
            b += f'<path class="o" d="M{x - 24},{y} L{x + 24},{y} M{x},{y - 24} L{x},{y + 24}" style="stroke-width:5"/>'
        for y1, y2 in ((198, 225), (345, 372), (492, 522)):
            b += f'<rect class="w" x="{x - 6}" y="{y1}" width="12" height="{y2 - y1}" rx="6"/>'
    for a, c in zip(xs, xs[1:]):
        for y in (172, 285, 432, 548):
            b += f'<rect class="w" x="{a + 64}" y="{y - 6}" width="{c - a - 128}" height="12" rx="6"/>'
    # end nets: chains from the tyre rows to a swivel ring at each end
    for sx, ex, ring in ((255, 128, 1), (1105, 1232, -1)):
        hx = sx + ring * -2
        for y in (175, 230, 285, 355, 432, 490, 548):
            b += chain(sx + (-1 if ring > 0 else 1) * 4, y, ex + ring * 18, 355, link=26, wide=12)
        b += f'<circle class="w" cx="{ex}" cy="355" r="20"/><circle class="t" cx="{ex}" cy="355" r="10"/>'
        b += chain(ex - ring * 8, 372, ex - ring * 70, 460, link=30, wide=14)
    b += '<line class="t" x1="255" y1="500" x2="255" y2="700"/><line class="t" x1="1105" y1="500" x2="1105" y2="700"/>'
    b += dim_h(255, 1105, 684, 'L')
    # end view: tyres all round the rim, spokes to the hub
    cx, cy, R = 1590, 360, 205
    b += f'<circle class="f" cx="{cx}" cy="{cy}" r="{R}"/><circle class="t" cx="{cx}" cy="{cy}" r="{R - 62}"/>'
    for k in range(12):
        ang = k * math.pi / 6; px, py = cx + R * math.cos(ang), cy + R * math.sin(ang)
        b += f'<g transform="translate({px:.1f},{py:.1f}) rotate({math.degrees(ang) + 90:.1f})"><rect class="w" x="-48" y="-18" width="96" height="36" rx="18"/></g>'
        sx, sy = cx + 34 * math.cos(ang), cy + 34 * math.sin(ang)
        b += f'<line class="o" x1="{sx:.1f}" y1="{sy:.1f}" x2="{cx + (R - 26) * math.cos(ang):.1f}" y2="{cy + (R - 26) * math.sin(ang):.1f}"/>'
        for rr in (R - 62, R - 26):
            b += f'<path class="o" d="M{cx + rr * math.cos(ang) - 7:.1f},{cy + rr * math.sin(ang) - 7:.1f} l14,14 m0,-14 l-14,14" style="stroke-width:3.2"/>'
    b += f'<circle class="w" cx="{cx}" cy="{cy}" r="30"/><circle class="t" cx="{cx}" cy="{cy}" r="14"/>'
    b += chain(cx + 6, cy + 12, cx + 64, cy + 104, link=26, wide=12)
    b += dim_v(1905, cy - R + 30, cy + R - 30, 'ØD', ext_from=1700, tx=-36)
    return svg(2000, 720, b)


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    out = os.path.join(root, "assets/engineering/draw"); os.makedirs(out, exist_ok=True)
    for name, fn in (("cylindrical", cylindrical), ("roller", roller), ("pneumatic", pneumatic)):
        with open(os.path.join(out, f"{name}.svg"), "w") as f:
            f.write(fn())
        print(name, os.path.getsize(os.path.join(out, f"{name}.svg")) // 1024, "KB")
