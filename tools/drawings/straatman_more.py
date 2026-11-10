"""Catalogue-style line drawings for the other three Straatman products, to sit faint behind their words on the
Straatman page the way the quick release hook drawing does (qrh.py): the SafeCom ship-to-shore link cabinet, the
smart bollard and the berthing aid system. Same pens as fenders.py (thin outlines, light fill, dashed hidden lines,
dash-dot centre lines, dimension arrows) in HexaHessman green.
Writes assets/engineering/straatman/{ssl,bollard,bas}-drawing.svg.

Run:  python3 tools/drawings/straatman_more.py /Users/poopiepie/Hexahessman
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fenders import svg, dim_h, dim_v   # noqa: E402
from qrh import circle, rect, line, sector   # noqa: E402


def text(x, y, s, size=30, anchor="middle"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="font-size:{size}px;letter-spacing:.08em">{s}</text>'


# ---------------------------------------------------------------- ship-to-shore link cabinet
def ssl():
    b = ''
    # front elevation: a two-bay console on a plinth
    x0, y0, w, h = 140, 120, 760, 980
    b += rect(x0 - 14, y0 + h, w + 28, 50, rx=3)                         # plinth
    b += rect(x0, y0, w, h, rx=6)                                         # carcass
    b += rect(x0 - 10, y0 - 34, w + 20, 34, "o", rx=3)                    # roof
    for k in range(2):                                                    # the two doors
        dx = x0 + 18 + k * (w / 2)
        dw = w / 2 - 36
        b += rect(dx, y0 + 18, dw, h - 36, "w", rx=4)
        b += rect(dx + dw - 30, y0 + h / 2 - 70, 14, 140, "f", rx=7)      # handle
        b += circle(dx + dw - 23, y0 + h / 2 + 96, 9, "t")                # key lock
    # left bay: one touch screen above, a second below
    L = x0 + 18
    b += rect(L + 50, y0 + 70, 250, 190, "f", rx=6) + rect(L + 66, y0 + 86, 218, 158, "o", rx=2)
    b += ''.join(line(L + 82, y0 + 110 + i * 22, L + 82 + 70 + (i % 3) * 30, y0 + 110 + i * 22, "t") for i in range(6))
    b += rect(L + 50, y0 + 460, 250, 190, "f", rx=6) + rect(L + 66, y0 + 476, 218, 158, "o", rx=2)
    b += text(L + 175, y0 + 568, "SAFECOM", 22)
    # right bay: screen, keyboard, then rows of lamps and switches
    R = x0 + w / 2 + 18
    b += rect(R + 50, y0 + 70, 250, 170, "f", rx=6) + rect(R + 66, y0 + 86, 218, 138, "o", rx=2)
    b += '<path class="t" d="M' + f'{R + 80},{y0 + 200} ' + ' '.join(f'L{R + 80 + i * 24},{y0 + 200 - (40 if i % 2 else 10) - i * 3}' for i in range(9)) + '"/>'
    b += rect(R + 50, y0 + 290, 250, 120, "o", rx=4)                      # keyboard
    for r in range(4):
        for c in range(9):
            b += rect(R + 62 + c * 26, y0 + 302 + r * 26, 20, 20, "t", rx=3)
    for r in range(3):                                                    # lamps and switches
        for c in range(6):
            cx, cy = R + 80 + c * 38, y0 + 470 + r * 54
            b += circle(cx, cy, 12, "w") + (circle(cx, cy, 4, "t") if (r + c) % 2 else '')
    for c in range(4):
        cx = R + 96 + c * 56
        b += circle(cx, y0 + 690, 20, "w") + line(cx, y0 + 690, cx + 11, y0 + 676)
    # cable glands under the cabinet, the ship-shore link cable leaving to the side
    for i in range(5):
        b += rect(x0 + 120 + i * 60, y0 + h + 50, 30, 24, "o", rx=3)
    b += '<path class="o" d="M' + f'{x0 + 135},{y0 + h + 74} C{x0 + 140},{y0 + h + 140} {x0 + 520},{y0 + h + 120} {x0 + w + 120},{y0 + h + 160}"/>'
    # side elevation, to the right: depth of the cabinet
    sx = 1010
    b += rect(sx, y0, 220, h, rx=6) + rect(sx - 10, y0 - 34, 240, 34, "o", rx=3) + rect(sx - 8, y0 + h, 236, 50, rx=3)
    b += line(sx + 34, y0 + 18, sx + 34, y0 + h - 18, "h")                # door hinge line, hidden
    b += rect(sx + 70, y0 + 120, 110, 380, "o", rx=4)                     # rack inside, dashed
    for i in range(7):
        b += line(sx + 70, y0 + 160 + i * 50, sx + 180, y0 + 160 + i * 50, "h")
    # the ship-shore plug at the end of the cable
    px, py = x0 + w + 140, y0 + h + 160
    b += rect(px, py - 34, 120, 68, "w", rx=12) + circle(px + 40, py, 12, "t") + circle(px + 80, py, 12, "t")
    # centre lines and dimensions
    b += f'<line class="c" x1="{x0 + w / 2}" y1="{y0 - 70}" x2="{x0 + w / 2}" y2="{y0 + h + 90}"/>'
    b += dim_h(x0, x0 + w, y0 - 90, "W", ext_from=y0 - 36)
    b += dim_v(x0 - 70, y0 - 34, y0 + h + 50, "H", ext_from=x0 - 12, tx=-34)
    b += dim_h(sx, sx + 220, y0 - 90, "D", ext_from=y0 - 36)
    return svg(1320, 1480, '<g transform="translate(0,80)">' + b + '</g>')   # room above for the W / D dimensions


# ---------------------------------------------------------------- smart bollard
def bollard():
    b = ''
    cx = 640
    # plan view on top: the round head with its two horns, the base plate and its bolt circle
    py = 330
    b += rect(cx - 230, py - 230, 460, 460, rx=10)
    for a in range(8):
        t = math.radians(a * 45 + 22.5)
        bx, by = cx + 185 * math.cos(t), py + 185 * math.sin(t)
        b += circle(bx, by, 16) + circle(bx, by, 6, "t")
    b += circle(cx, py, 150, "w") + circle(cx, py, 118)
    b += ('<path class="f" d="M' + f'{cx - 118},{py - 30} L{cx - 210},{py - 44} Q{cx - 236},{py} {cx - 210},{py + 44} L{cx - 118},{py + 30} Z"/>')
    b += ('<path class="f" d="M' + f'{cx + 118},{py - 30} L{cx + 210},{py - 44} Q{cx + 236},{py} {cx + 210},{py + 44} L{cx + 118},{py + 30} Z"/>')
    b += circle(cx, py, 30, "o") + circle(cx, py, 10, "t")               # the load pin, seen end on
    b += f'<line class="c" x1="{cx - 290}" y1="{py}" x2="{cx + 290}" y2="{py}"/><line class="c" x1="{cx}" y1="{py - 290}" x2="{cx}" y2="{py + 290}"/>'
    # line pull arrows in plan: the mooring lines leaving the bollard
    for a in (-28, 8, 40):
        t = math.radians(a)
        b += line(cx + 150 * math.cos(t), py + 150 * math.sin(t), cx + 420 * math.cos(t), py + 420 * math.sin(t), "h")
    b += sector(cx + 150, py, 70, -40, 28)
    # elevation below: the bollard on the quay
    gy = 1180
    b += line(200, gy, 1100, gy)
    for i in range(44):
        x = 210 + i * 20 + (i % 3) * 3
        b += circle(x, gy + 12 + (i * 7) % 16, 2.2 + (i % 2), "t")
    b += rect(cx - 230, gy - 40, 460, 40, rx=2)                           # base plate
    for x in (cx - 190, cx + 190):
        b += line(x, gy - 54, x, gy + 70, "h") + rect(x - 14, gy - 54, 28, 14, "o", rx=2)
    # body: a waisted barrel up to the head, the horns either side
    b += ('<path class="f" d="M' + f'{cx - 150},{gy - 40} C{cx - 110},{gy - 160} {cx - 110},{gy - 300} {cx - 130},{gy - 380} '
          f'L{cx + 130},{gy - 380} C{cx + 110},{gy - 300} {cx + 110},{gy - 160} {cx + 150},{gy - 40} Z"/>')
    b += rect(cx - 170, gy - 430, 340, 50, rx=8)                          # head
    b += ('<path class="f" d="M' + f'{cx - 130},{gy - 420} L{cx - 260},{gy - 470} Q{cx - 290},{gy - 440} {cx - 262},{gy - 400} L{cx - 130},{gy - 384} Z"/>')
    b += ('<path class="f" d="M' + f'{cx + 130},{gy - 420} L{cx + 260},{gy - 470} Q{cx + 290},{gy - 440} {cx + 262},{gy - 400} L{cx + 130},{gy - 384} Z"/>')
    # the load pin through the body (hidden), its cable down to the junction box on the quay
    b += rect(cx - 160, gy - 250, 320, 44, "h", rx=10)
    b += circle(cx + 175, gy - 228, 14, "w")
    b += '<path class="o" d="M' + f'{cx + 189},{gy - 228} C{cx + 280},{gy - 220} {cx + 300},{gy - 80} {cx + 330},{gy - 70}"/>'
    b += rect(cx + 330, gy - 110, 120, 110, "w", rx=6) + rect(cx + 350, gy - 92, 80, 40, "o", rx=2)
    b += circle(cx + 366, gy - 30, 6, "t") + circle(cx + 390, gy - 30, 6, "t") + circle(cx + 414, gy - 30, 6, "t")
    # a mooring line on the horn
    b += '<path class="o" d="M' + f'{cx - 120},{gy - 330} C{cx - 300},{gy - 340} {cx - 420},{gy - 420} {cx - 480},{gy - 560}"/>'
    b += '<path class="o" d="M' + f'{cx - 120},{gy - 304} C{cx - 310},{gy - 312} {cx - 440},{gy - 400} {cx - 506},{gy - 548}"/>'
    b += f'<line class="c" x1="{cx}" y1="{gy - 500}" x2="{cx}" y2="{gy + 80}"/>'
    b += dim_h(cx - 230, cx + 230, gy + 110, "B", ext_from=gy + 4, ty=48)
    b += dim_v(cx + 520, gy - 430, gy, "H", ext_from=cx + 270, tx=36)
    b += dim_h(cx - 230, cx + 230, py - 280, "A", ext_from=py - 232)
    return svg(1280, 1360, b)


# ---------------------------------------------------------------- berthing aid system
def seg_digit(x, y, s, on):
    """one seven-segment digit, the lit segments drawn filled"""
    w, hh, t = s * .6, s, s * .12
    pos = {'a': (x + t, y, w - 2 * t, t), 'g': (x + t, y + hh / 2 - t / 2, w - 2 * t, t), 'd': (x + t, y + hh - t, w - 2 * t, t),
           'f': (x, y + t, t, hh / 2 - t * 1.5), 'b': (x + w - t, y + t, t, hh / 2 - t * 1.5),
           'e': (x, y + hh / 2 + t / 2, t, hh / 2 - t * 1.5), 'c': (x + w - t, y + hh / 2 + t / 2, t, hh / 2 - t * 1.5)}
    return ''.join(rect(*pos[k], "f" if k in on else "t", rx=2) for k in pos)


DIG = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abcfgd'}


def bas():
    b = ''
    # the display board on its mast
    bx, by, bw, bh = 120, 110, 700, 520
    b += rect(bx, by, bw, bh, rx=8) + rect(bx + 22, by + 22, bw - 44, bh - 44, "w", rx=4)
    rows = (("DISTANCE", "14.2", "m"), ("SPEED", "0.08", "m/s"), ("ANGLE", "1.6", "°"))
    for i, (lab, val, unit) in enumerate(rows):
        y = by + 52 + i * 150
        b += text(bx + 60, y + 26, lab, 26, "start")
        x = bx + 290
        for ch in val:
            if ch == '.':
                b += circle(x + 4, y + 104, 7, "f"); x += 20; continue
            b += seg_digit(x, y + 10, 100, DIG[ch]); x += 78
        b += text(bx + bw - 60, y + 104, unit, 26, "end")
    for x in (bx + 200, bx + bw - 200):                                   # the mast and its brace
        b += rect(x - 14, by + bh, 28, 420, rx=2)
    b += line(bx + 200, by + bh + 120, bx + bw - 200, by + bh + 120) + line(bx + 200, by + bh + 120, bx + bw - 200, by + bh + 260, "t")
    gy = by + bh + 420
    b += line(60, gy, 1260, gy)
    for i in range(58):
        x = 70 + i * 20 + (i % 3) * 3
        b += circle(x, gy + 12 + (i * 7) % 16, 2.2 + (i % 2), "t")
    # the two laser sensors on the quay edge, their beams reaching out to the hull of the approaching ship
    hull = 'M960,180 C1040,260 1090,420 1110,640 C1124,800 1120,880 1110,940'
    b += f'<path class="f" d="{hull} L1260,940 L1260,180 Z"/>'
    b += line(1130, 300, 1260, 300, "t") + line(1150, 460, 1260, 460, "t") + line(1160, 620, 1260, 620, "t")
    for (sx, sy, tx, ty) in ((900, gy - 60, 1104, 560), (980, gy - 60, 1116, 760)):
        b += rect(sx - 26, sy - 30, 52, 60, "w", rx=6) + circle(sx, sy, 12, "o")
        b += line(sx, sy + 30, sx, gy, "o")
        b += f'<line class="h" x1="{sx + 12}" y1="{sy - 6}" x2="{tx}" y2="{ty}"/>'
        b += circle(tx, ty, 8, "a")
    b += sector(900, gy - 60, 80, 40, 75)
    b += f'<line class="c" x1="{bx + bw / 2}" y1="{by - 40}" x2="{bx + bw / 2}" y2="{gy + 40}"/>'
    b += dim_h(bx, bx + bw, by - 60, "L", ext_from=by - 8)
    b += dim_v(bx - 50, by, gy, "H", ext_from=bx - 8, tx=-34)
    return svg(1320, 1240, b)


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    out = os.path.join(root, "assets/engineering/straatman"); os.makedirs(out, exist_ok=True)
    for name, fn in (("ssl", ssl), ("bollard", bollard), ("bas", bas)):
        p = os.path.join(out, f"{name}-drawing.svg")
        with open(p, "w") as f:
            f.write(fn())
        print(f"{name}-drawing.svg", os.path.getsize(p) // 1024, "KB")
