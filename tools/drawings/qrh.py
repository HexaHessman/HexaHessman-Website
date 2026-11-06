"""A Straatman quick release mooring hook (double hook on a pedestal with capstan), drawn as a catalogue-style
technical drawing in HexaHessman green: plan view on top, side elevation below, swing marks, centre lines and
dimension arrows, after the layout drawings on Straatman's old HexaHessman page. Same pens as fenders.py.
Writes assets/engineering/straatman/qrh-drawing.svg.

Run:  python3 tools/drawings/qrh.py /Users/poopiepie/Hexahessman
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fenders import svg, arrow, dim_h, dim_v   # noqa: E402


def circle(cx, cy, r, cls="o"):
    return f'<circle class="{cls}" cx="{cx}" cy="{cy}" r="{r}"/>'


def rect(x, y, w, h, cls="f", rx=0):
    return f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>'


def line(x1, y1, x2, y2, cls="o"):
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'


def sector(cx, cy, r, a0, a1, cls="f"):
    """a filled pie slice (angles in degrees, 0 = right, counter-clockwise up): the swing marks"""
    p0 = (cx + r * math.cos(math.radians(a0)), cy - r * math.sin(math.radians(a0)))
    p1 = (cx + r * math.cos(math.radians(a1)), cy - r * math.sin(math.radians(a1)))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f'<path class="{cls}" d="M{cx},{cy} L{p0[0]:.1f},{p0[1]:.1f} A{r},{r} 0 {large} 0 {p1[0]:.1f},{p1[1]:.1f} Z"/>'


def bolt_plan(cx, cy):
    return circle(cx, cy, 13) + circle(cx, cy, 5, "t")


def plan():
    """top view: two hooks side by side on one base plate, the capstan beside them"""
    b = ''
    # base plate and its anchor bolts
    b += rect(880, 120, 300, 320, rx=6)
    for x in (910, 1150):
        for y in (150, 410):
            b += bolt_plan(x, y)
    # gearbox and capstan drum (seen from above)
    b += rect(1180, 215, 90, 110, rx=4) + circle(1300, 270, 62, "w") + circle(1300, 270, 40) + circle(1300, 270, 14, "t")
    b += rect(1362, 248, 80, 44, rx=8) + ''.join(line(1374 + i * 12, 248, 1374 + i * 12, 292, "t") for i in range(6))   # motor, finned
    for k, y in enumerate((210, 330)):   # the two hooks
        top, bot = y - 26, y + 26
        b += (f'<path class="f" d="M1040,{top} L600,{top} Q560,{top} 548,{y - 10} L540,{y} L548,{y + 10} Q560,{bot} 600,{bot} L1040,{bot} Z"/>')
        b += circle(1040, y, 34, "w") + circle(1040, y, 13)          # pivot boss and pin
        b += rect(780, top + 8, 70, 36, "o", rx=3)                     # latch housing
        b += line(860, y, 1000, y, "h")                                # release linkage, hidden
        b += circle(640, y, 8, "t")
        b += sector(470, y, 34, 90, 270)                               # swing in plan: ±90° from the quay line
        b += f'<line class="c" x1="430" y1="{y}" x2="1110" y2="{y}"/>'
    b += f'<line class="c" x1="1030" y1="90" x2="1030" y2="470"/><line class="c" x1="1300" y1="180" x2="1300" y2="360"/>'
    # swing arc of the hook nose about its pivot
    r = 1040 - 540
    a = math.radians(14)
    b += f'<path class="h" d="M{1040 - r * math.cos(a):.1f},{270 - r * math.sin(a):.1f} A{r},{r} 0 0 0 {1040 - r * math.cos(a):.1f},{270 + r * math.sin(a):.1f}"/>'
    b += dim_h(880, 1180, 70, "B", ext_from=120)
    b += dim_h(540, 1040, 500, "D", ext_from=360, ty=48)
    b += dim_v(1490, 120, 440, "A", ext_from=1180, tx=34)
    return b


def elevation():
    """side view: the hook arm reaching out from its pedestal, the capstan above, the control box and its cable"""
    b = ''
    gy = 930
    # ground: concrete, hatched with dots
    b += line(640, gy, 1560, gy)
    for i in range(48):
        x = 650 + i * 19 + (i % 3) * 3
        b += circle(x, gy + 12 + (i * 7) % 16, 2.2 + (i % 2), "t")
    # base plate, anchor bolts going into the concrete
    b += rect(900, gy - 34, 440, 34, rx=2)
    for x in (930, 1310):
        b += line(x, gy - 46, x, gy + 52, "h") + rect(x - 12, gy - 46, 24, 12, "o", rx=2)
    # pedestal
    b += rect(1010, 690, 160, 206, rx=3)
    b += line(1010, 760, 1170, 760, "t") + line(1010, 830, 1170, 830, "t")
    # the hook: a long arm from its pivot, the free end curling up into the beak that holds the eye of the line
    b += ('<path class="f" d="M1090,640 L790,640 C752,640 726,626 712,600 L694,560 C684,538 652,532 640,556 '
          'C632,574 640,608 662,640 C686,676 716,700 760,704 L1090,704 A32,32 0 0 0 1090,640 Z"/>')
    b += circle(1090, 672, 40, "w") + circle(1090, 672, 15)            # pivot boss and pin
    b += circle(812, 672, 13) + circle(960, 672, 13)                    # linkage pins
    b += rect(840, 652, 90, 34, "o", rx=3)                              # latch housing
    b += line(880, 640, 912, 572) + circle(916, 562, 11, "w")           # release lever
    b += line(812, 672, 960, 672, "h")
    # gearbox with the motor hanging off its side, the capstan drum on top
    b += rect(1150, 560, 150, 130, rx=4) + rect(1170, 584, 60, 40, "o", rx=2)
    b += rect(1300, 590, 130, 74, "w", rx=10) + ''.join(line(1316 + i * 14, 590, 1316 + i * 14, 664, "t") for i in range(8))
    b += rect(1180, 540, 100, 20, rx=2)                                 # bottom flange
    b += '<path class="f" d="M1192,540 C1204,500 1204,452 1192,412 L1268,412 C1256,452 1256,500 1268,540 Z"/>'   # warping drum
    b += rect(1172, 394, 116, 20, rx=3)                                 # top flange
    b += f'<line class="c" x1="1230" y1="360" x2="1230" y2="720"/>'
    # control box on the pedestal, its cable trailing to a plug on the quay
    b += rect(1196, 730, 118, 118, rx=4) + rect(1214, 748, 82, 54, "o", rx=2) + circle(1230, 822, 7, "t") + circle(1256, 822, 7, "t") + circle(1282, 822, 7, "t")
    b += '<path class="o" d="M1314,830 C1380,840 1400,900 1470,916"/>' + rect(1470, 904, 44, 22, "w", rx=4)
    # swing mark for the hook in elevation: 45° up from the deck
    b += sector(600, 520, 44, 0, 45)
    # centre lines
    b += f'<line class="c" x1="1090" y1="600" x2="1090" y2="960"/><line class="c" x1="600" y1="672" x2="1140" y2="672"/>'
    # dimensions
    b += dim_h(640, 1430, gy + 74, "C", ext_from=gy + 4, ty=48)
    b += dim_v(1540, 394, gy, "H", ext_from=1440, tx=36)
    b += dim_v(590, 640, gy, "h", ext_from=640, tx=-32)
    return b


def qrh():
    # the side view sits under the plan with clear air between them; the empty left margin trimmed off
    return svg(1240, 1290, '<g transform="translate(-400,10)">' + plan() + '<g transform="translate(0,170)">' + elevation() + '</g></g>')


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    out = os.path.join(root, "assets/engineering/straatman"); os.makedirs(out, exist_ok=True)
    p = os.path.join(out, "qrh-drawing.svg")
    with open(p, "w") as f:
        f.write(qrh())
    print("qrh-drawing.svg", os.path.getsize(p) // 1024, "KB")
