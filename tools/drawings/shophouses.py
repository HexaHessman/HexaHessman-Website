"""A row of Singapore shophouses with the HexaHessman shop in the middle, drawn as white line art (after the
client's illustration), for the About hero. Every stroke carries --d, a delay that grows left to right and bottom
to top within each house, so the CSS can draw the street in like a pen. Writes assets/about-shophouses.svg.
Run: python3 tools/drawings/shophouses.py /Users/poopiepie/Hexahessman
"""
import math, os, sys

W, H = 1600, 640
GROUND = 600
out = []

def p(d, cls="", x=0, y=0, extra=""):
    # delay: a sweep from left to right, each house drawn from the street up
    delay = 0.15 + (x / W) * 2.6 + (1 - y / H) * 0.9
    out.append(f'<path class="{cls}" d="{d}" pathLength="1" style="--d:{delay:.2f}s"{extra}/>')

def rect(x, y, w, h, cls=""):
    p(f"M{x:.1f},{y:.1f}h{w:.1f}v{h:.1f}h{-w:.1f}Z", cls, x + w / 2, y + h / 2)

def line(x1, y1, x2, y2, cls=""):
    p(f"M{x1:.1f},{y1:.1f}L{x2:.1f},{y2:.1f}", cls, (x1 + x2) / 2, (y1 + y2) / 2)

def arch_window(x, y, w, h, panes=True, shutters=False):
    r = w / 2
    p(f"M{x:.1f},{y + h:.1f}V{y + r:.1f}A{r:.1f},{r:.1f} 0 0 1 {x + w:.1f},{y + r:.1f}V{y + h:.1f}Z", "", x + r, y + h / 2)
    p(f"M{x + 4:.1f},{y + h:.1f}V{y + r:.1f}A{r - 4:.1f},{r - 4:.1f} 0 0 1 {x + w - 4:.1f},{y + r:.1f}V{y + h:.1f}", "t", x + r, y + h / 2)
    if panes:
        line(x + r, y + 4, x + r, y + h, "t")
        for k in range(1, 4):
            line(x + 4, y + r + (h - r) * k / 4, x + w - 4, y + r + (h - r) * k / 4, "t")
        for a in (-60, -30, 0, 30, 60):   # fan light
            t = math.radians(a - 90)
            line(x + r, y + r, x + r + (r - 4) * math.cos(t), y + r + (r - 4) * math.sin(t), "t")
    if shutters:
        for sx in (x - w * 0.42, x + w + 2):
            rect(sx, y + r * 0.6, w * 0.4, h - r * 0.6, "t")
            for k in range(1, 9):
                line(sx + 2, y + r * 0.6 + (h - r * 0.6) * k / 9, sx + w * 0.4 - 2, y + r * 0.6 + (h - r * 0.6) * k / 9, "t")

def louvre_window(x, y, w, h, n=10):
    rect(x, y, w, h); rect(x + 4, y + 4, w - 8, h - 8, "t")
    line(x + w / 2, y + 4, x + w / 2, y + h - 4, "t")
    for k in range(1, n):
        line(x + 6, y + h * k / n, x + w - 6, y + h * k / n, "t")

def pilaster(x, y, w, h, capital=True):
    rect(x, y, w, h)
    line(x + w * 0.3, y + 16, x + w * 0.3, y + h - 6, "t"); line(x + w * 0.7, y + 16, x + w * 0.7, y + h - 6, "t")
    if capital:   # a little Corinthian head
        p(f"M{x - 5:.1f},{y:.1f}h{w + 10:.1f}l-4,10h{-w - 2:.1f}Z", "", x + w / 2, y)
        for k in range(3):
            cx = x + w * (0.2 + 0.3 * k)
            p(f"M{cx:.1f},{y + 10:.1f}q-5,6 0,12 q5,-6 0,-12", "t", cx, y + 12)
        rect(x - 3, y + h - 6, w + 6, 6)

def balustrade(x, y, w, h=30, n=None):
    line(x, y, x + w, y); line(x, y + h, x + w, y + h); line(x, y + 4, x + w, y + 4, "t")
    n = n or int(w // 9)
    for k in range(n + 1):
        bx = x + w * k / n
        p(f"M{bx:.1f},{y + 4:.1f}c-3,7 -3,10 0,13 c3,3 3,6 0,{h - 17:.1f}", "t", bx, y + h / 2)

def tiles(x1, x2, y, h, slope=0):
    p(f"M{x1:.1f},{y + h:.1f}L{x1 + 10:.1f},{y:.1f}H{x2 - 10:.1f}L{x2:.1f},{y + h:.1f}Z", "", (x1 + x2) / 2, y)
    for k in range(1, int(h // 6)):
        line(x1 + 10 - 10 * k * 6 / h, y + k * 6, x2 - 10 + 10 * k * 6 / h, y + k * 6, "t")
    xx = x1 + 14
    while xx < x2 - 12:
        line(xx, y + 2, xx - 4, y + h - 2, "t"); xx += 9

def plant(cx, base, s=1.0, pot=True):
    if pot:
        p(f"M{cx - 10 * s:.1f},{base:.1f}l3,{-22 * s:.1f}h{14 * s:.1f}l3,{22 * s:.1f}Z", "", cx, base - 10)
        base -= 22 * s
    for a, L in ((-70, 46), (-40, 58), (-15, 64), (10, 60), (35, 52), (65, 40), (-95, 30), (95, 30)):
        t = math.radians(a - 90); ex, ey = cx + L * s * math.cos(t), base + L * s * math.sin(t)
        mx, my = cx + L * s * 0.5 * math.cos(t) - 8 * s * math.sin(t), base + L * s * 0.5 * math.sin(t) + 8 * s * math.cos(t)
        p(f"M{cx:.1f},{base:.1f}Q{mx:.1f},{my:.1f} {ex:.1f},{ey:.1f}", "t", ex, ey)
        lx, ly = ex - (ex - cx) * 0.35, ey - (ey - base) * 0.35   # a leaf
        p(f"M{lx:.1f},{ly:.1f}q{(ex - lx) * 0.5 + 6 * s:.1f},{(ey - ly) * 0.5 - 4 * s:.1f} {ex - lx:.1f},{ey - ly:.1f}q{-(ex - lx) * 0.5 - 6 * s:.1f},{-(ey - ly) * 0.5 + 4 * s:.1f} {-(ex - lx):.1f},{-(ey - ly):.1f}", "t", ex, ey)

def bistro(cx):
    p(f"M{cx - 16},{GROUND - 34}h32M{cx},{GROUND - 34}V{GROUND}M{cx - 10},{GROUND}h20", "", cx, GROUND - 20)
    for d in (-34, 34):   # folding chairs
        x = cx + d
        p(f"M{x - 8},{GROUND}L{x + 8},{GROUND - 40}M{x + 8},{GROUND}L{x - 8},{GROUND - 26}M{x - 10},{GROUND - 26}h18M{x + 4},{GROUND - 40}l8,0", "t", x, GROUND - 20)

def door_glass(x, y, w, h):
    rect(x, y, w, h); line(x + w / 2, y, x + w / 2, y + h)
    for dx in (0, w / 2):
        rect(x + dx + 6, y + 8, w / 2 - 12, h * 0.55, "t"); rect(x + dx + 6, y + h * 0.62, w / 2 - 12, h * 0.32, "t")

def hh_logo(cx, cy, s):
    # the HexaHessman mark: two tall frames either side and a diamond in a diamond
    for dx in (-s * 0.62, s * 0.38):
        rect(cx + dx, cy - s * 0.5, s * 0.24, s)
    p(f"M{cx:.1f},{cy - s * 0.36:.1f}L{cx + s * 0.36:.1f},{cy:.1f}L{cx:.1f},{cy + s * 0.36:.1f}L{cx - s * 0.36:.1f},{cy:.1f}Z", "", cx, cy)
    p(f"M{cx:.1f},{cy - s * 0.2:.1f}L{cx + s * 0.2:.1f},{cy:.1f}L{cx:.1f},{cy + s * 0.2:.1f}L{cx - s * 0.2:.1f},{cy:.1f}Z", "t", cx, cy)

# ---------------- house 1: two-storey, arched upper windows behind a balustraded verandah, café below
X0, X1 = 150, 600
line(X0 - 30, GROUND, W - 80, GROUND)   # the street
rect(X0, 250, X1 - X0, GROUND - 250)
p(f"M{X0 - 10},250h{X1 - X0 + 20}v-14h{-(X1 - X0 + 20)}Z", "", (X0 + X1) / 2, 243)
rect(X0 + 150, 196, 160, 40); line(X0 + 150, 206, X0 + 310, 206, "t")   # roof parapet + water tank
for k in range(5):
    line(X0 + 160 + k * 34, 196, X0 + 160 + k * 34, 236, "t")
for i, ax in enumerate((X0 + 70, X0 + 170, X0 + 270, X0 + 350)):
    arch_window(ax, 280, 64, 104)
for px in (X0 + 6, X0 + 140, X0 + 245, X0 + 328, X1 - 34):
    pilaster(px, 268, 26, 140)
balustrade(X0 - 6, 390, X1 - X0 + 12, 34)
line(X0 - 14, 428, X1 + 14, 428); line(X0 - 14, 436, X1 + 14, 436)
for px in (X0 + 6, X0 + 200, X1 - 34):
    pilaster(px, 440, 28, GROUND - 440)
p(f"M{X0 + 46},{GROUND}V500A70,70 0 0 1 {X0 + 186},500V{GROUND}", "", X0 + 116, 520)   # arched café front
rect(X0 + 66, 506, 100, 94, "t")
rect(X0 + 232, 456, 120, 26)   # the café sign
p(f"M{X0 + 246},{474}h92M{X0 + 252},{466}h80", "t", X0 + 292, 470)
door_glass(X0 + 262, 500, 82, 100)
rect(X0 + 370, 470, 60, 70, "t")
for k in range(1, 4):
    line(X0 + 370, 470 + k * 17, X0 + 430, 470 + k * 17, "t")
bistro(X0 + 116); bistro(X0 + 410)
plant(X0 + 200, GROUND, 0.9); plant(X1 - 20, GROUND, 0.8)
plant(X0 + 120, 390, 0.6, pot=True); plant(X0 + 300, 390, 0.55, pot=True); plant(X1 - 70, 390, 0.6, pot=True)

# ---------------- house 2: the HexaHessman shophouse, three storeys, tall and central
M0, M1 = 610, 830
rect(M0, 150, M1 - M0, GROUND - 150)
p(f"M{M0 - 12},150h{M1 - M0 + 24}l-10,-18h{-(M1 - M0 + 4)}Z", "", (M0 + M1) / 2, 140)   # cornice
p(f"M{M0 + 20},132V96h{M1 - M0 - 40}v36", "", (M0 + M1) / 2, 110)
p(f"M{M0 + 30},96l{(M1 - M0 - 60) / 2},-26l{(M1 - M0 - 60) / 2},26", "", (M0 + M1) / 2, 84)   # pediment
for px in (M0 + 4, M1 - 26):
    pilaster(px, 160, 22, 120)
louvre_window(M0 + 52, 172, 64, 96); louvre_window(M0 + 124, 172, 64, 96)
balustrade(M0 + 30, 282, M1 - M0 - 60, 22)
line(M0 - 8, 310, M1 + 8, 310); line(M0 - 8, 318, M1 + 8, 318)
arch_window(M0 + 70, 330, 80, 110)
for px in (M0 + 4, M1 - 26):
    pilaster(px, 326, 22, 120)
plant(M0 + 46, 446, 0.75, pot=False); plant(M1 - 40, 446, 0.85, pot=False)
rect(M0 + 10, 452, M1 - M0 - 20, 46)   # the sign band
hh_logo((M0 + M1) / 2, 466, 22)
out.append(f'<text x="{(M0 + M1) / 2}" y="491" text-anchor="middle" class="sign" style="--d:2.1s">HEXA HESSMAN</text>')
p(f"M{M0 + 30},{GROUND}V540A80,40 0 0 1 {M1 - 30},540V{GROUND}", "", (M0 + M1) / 2, 540)
door_glass(M0 + 60, 530, M1 - M0 - 120, 70)
for px in (M0 + 4, M1 - 26):
    pilaster(px, 500, 22, GROUND - 500, capital=False)

# ---------------- house 3: tiled roof, plain upper windows, awning over the shop
R0, R1 = 840, 1150
tiles(R0 - 6, R1 + 6, 190, 44)
rect(R0, 234, R1 - R0, GROUND - 234)
for wx in (R0 + 40, R0 + 130, R0 + 220):
    rect(wx, 270, 54, 86); line(wx + 27, 270, wx + 27, 356, "t"); line(wx, 300, wx + 54, 300, "t")
rect(R0 + 40, 372, R1 - R0 - 80, 30, "t")   # a long sign board
p(f"M{R0 - 8},430h{R1 - R0 + 16}l-14,36h{-(R1 - R0 - 12)}Z", "", (R0 + R1) / 2, 448)   # awning
for k in range(1, 16):
    line(R0 - 8 + (R1 - R0 + 16) * k / 16, 430, R0 - 1 + (R1 - R0 + 2) * k / 16, 466, "t")
rect(R0 + 30, 480, 110, 120); line(R0 + 85, 480, R0 + 85, GROUND, "t")
rect(R0 + 170, 480, 110, 120); line(R0 + 225, 480, R0 + 225, GROUND, "t")
line(R1 - 6, 234, R1 - 6, GROUND, "t")

# ---------------- house 4: arched windows with louvred shutters, double doors
F0, F1 = 1160, 1460
tiles(F0 - 6, F1 + 6, 200, 40)
rect(F0, 240, F1 - F0, GROUND - 240)
for ax in (F0 + 52, F0 + 132, F0 + 212):
    arch_window(ax, 280, 44, 92, panes=False, shutters=True)
line(F0 - 8, 410, F1 + 8, 410); line(F0 - 8, 418, F1 + 8, 418)
rect(F0 + 40, 450, 90, 150); line(F0 + 85, 450, F0 + 85, GROUND, "t")
rect(F0 + 190, 450, 90, 150); line(F0 + 235, 450, F0 + 235, GROUND, "t")
for dx in (F0 + 48, F0 + 93, F0 + 198, F0 + 243):
    rect(dx, 462, 30, 60, "t"); rect(dx, 534, 30, 56, "t")
pilaster(F0 + 4, 248, 20, 160, capital=False); pilaster(F1 - 24, 248, 20, 160, capital=False)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" class="shop-svg" role="img" aria-label="The HexaHessman shophouse on a Singapore street, drawn in line">'
       + "".join(out) + "</svg>\n")
root = sys.argv[1] if len(sys.argv) > 1 else "."
path = os.path.join(root, "assets/about-shophouses.svg")
open(path, "w").write(svg)
print(len(out), "strokes", os.path.getsize(path) // 1024, "KB")
