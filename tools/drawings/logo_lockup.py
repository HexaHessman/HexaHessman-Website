"""The HexaHessman logo (client's picture of 2026-11-26: emblem + HEXA / HESSMAN) as clean artwork.

The emblem is straight lines only, so it is redrawn from measurements of the picture (two frames, a square on its
corner woven through them); the lettering is traced with potrace. Everything is in the picture's own pixel units.

  python3 tools/drawings/logo_lockup.py <site root> <picture>

Writes assets/logo-lockup.svg, the tab icons (assets/favicon.svg, favicon-32.png, apple-touch-icon.png, /favicon.ico)
and puts the lockup into the header, the footer and logo.html, and the emblem into the generator (SPX_MARK).
"""
import os, re, subprocess, sys, tempfile
from PIL import Image, ImageDraw
import numpy as np

ROOT, SRC = sys.argv[1].rstrip("/"), sys.argv[2]

# ---------------------------------------------------------------- the emblem, from measurements
X0, X3, YT, YB = 102.2, 569.6, 585.3, 1073.2      # the two frames, outside edges
T, FW = 35.7, 178.5                                # band thickness, frame width
L1, R0 = X0 + FW, X3 - FW                          # the frames' facing edges (280.7, 391.1)
CX, CY = (X0 + X3) / 2, (YT + YB) / 2
RO, RI = 191.2, 139.9                              # the square's corners, outside and inside, from its centre
GAP, CUT = 21.4, 14.2                              # the breaks in the weave: along the diagonal, and beside a band
ul_o, ul_i = CX + CY - RO, CX + CY - RI            # upper left edge:  x + y
lr_o, lr_i = CX + CY + RO, CX + CY + RI            # lower right edge: x + y
ur_o, ur_i = CX - CY + RO, CX - CY + RI            # upper right edge: x - y
ll_o, ll_i = CX - CY - RO, CX - CY - RI            # lower left edge:  x - y
lb0, lb1 = L1 - T, L1                              # left frame's inner band
rb0, rb1 = R0, R0 + T                              # right frame's inner band
xa, xb = (rb0 + rb1) / 2, (lb0 + lb1) / 2          # where the square's arms end, inside those bands
cl, cr = lb0 - CUT, rb1 + CUT                      # where the two short ends are cut off

POLYS = [
    # left frame: top, outer side, bottom
    [(X0, YT), (L1, YT), (L1, YT + T), (X0 + T, YT + T), (X0 + T, YB - T), (L1, YB - T), (L1, YB), (X0, YB)],
    # its inner band: a short piece cut on the slant above the square, the rest from the square down
    [(lb0, YT + 1), (lb1, YT + 1), (lb1, ul_o - GAP - lb1), (lb0, ul_o - GAP - lb0)],
    [(lb0, (ul_o - lb0 + ul_i - lb1) / 2), (lb1, (ul_o - lb0 + ul_i - lb1) / 2), (lb1, YB - 1), (lb0, YB - 1)],
    # right frame
    [(X3, YT), (R0, YT), (R0, YT + T), (X3 - T, YT + T), (X3 - T, YB - T), (R0, YB - T), (R0, YB), (X3, YB)],
    # its inner band: the long piece cut on the slant above the square's lower edge, the short one below it
    [(rb0, YT + 1), (rb1, YT + 1), (rb1, lr_i - GAP - rb1), (rb0, lr_i - GAP - rb0)],
    [(rb0, (lr_i - rb0 + lr_o - rb1) / 2), (rb1, (lr_i - rb0 + lr_o - rb1) / 2), (rb1, YB - 1), (rb0, YB - 1)],
    # the square, upper half: left corner, top corner, the arm running into the right frame, and the short lower end
    [(CX - RO, CY), (CX, CY - RO), (xa, xa - ur_o), (xa, xa - ur_i), (CX, CY - RI), (CX - RI, CY),
     (cl, cl - ll_i), (cl, cl - ll_o)],
    # the square, lower half: right corner, bottom corner, the arm running into the left frame, and the short upper end
    [(CX + RO, CY), (CX, CY + RO), (xb, xb - ll_o), (xb, xb - ll_i), (CX, CY + RI), (CX + RI, CY),
     (cr, cr - ur_i), (cr, cr - ur_o)],
]


def area(p):
    return sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))


POLYS = [p if area(p) > 0 else p[::-1] for p in POLYS]      # all the same way round, so they add up when filled
n = lambda v: ("%.2f" % v).rstrip("0").rstrip(".")
MARK_D = "".join("M" + "L".join(n(x) + " " + n(y) for x, y in p) + "Z" for p in POLYS)

# ---------------------------------------------------------------- the lettering, traced
K = 4
BX0, BY0, BX1, BY1 = 95, 578, 1887, 1086
im = Image.open(SRC).convert("L").crop((BX0, BY0, BX1, BY1))
big = np.asarray(im.resize((im.width * K, im.height * K), Image.BICUBIC)).copy()
big[:, : int((581 - BX0) * K)] = 255                         # the emblem is drawn above, not traced
with tempfile.TemporaryDirectory() as d:
    Image.fromarray(((big > 145) * 255).astype("uint8")).convert("1").save(d + "/w.pbm")
    subprocess.run(["potrace", d + "/w.pbm", "-s", "-o", d + "/w.svg", "-t", "60", "-a", "1.0", "-O", "0.4", "-u", "10"], check=True)
    traced = open(d + "/w.svg").read()
WORD = "".join('<path d="%s"/>' % " ".join(p.split()) for p in re.findall(r'<path d="([^"]+)"', traced))
WORD_G = '<g transform="translate(%d,%d) scale(%s,-%s)">%s</g>' % (BX0, BY1, "%g" % (0.1 / K), "%g" % (0.1 / K), WORD)

VB = "100 583 1781 497"                                      # the whole logo with a hair of room
INNER = '<g fill="currentColor"><path d="%s"/>%s</g>' % (MARK_D, WORD_G)
LOCKUP = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" role="img" aria-label="HexaHessman">%s</svg>\n' % (VB, INNER)
INLINE = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" class="hh-lockup" aria-hidden="true">%s</svg>' % (VB, INNER)
open(ROOT + "/assets/logo-lockup.svg", "w").write(LOCKUP)

# ---------------------------------------------------------------- tab icons: the emblem, cream on the site green
GREEN, CREAM = "#0F2A1E", "#EEE3C7"
S = 512; MH = 0.74 * S; k = MH / (YB - YT)
ox, oy = (S - (X3 - X0) * k) / 2 - X0 * k, (S - MH) / 2 - YT * k
open(ROOT + "/assets/favicon.svg", "w").write(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d"><rect width="%d" height="%d" rx="96" fill="%s"/>'
    '<path transform="translate(%s,%s) scale(%s)" fill="%s" d="%s"/></svg>\n' % (S, S, S, S, GREEN, n(ox), n(oy), "%.5f" % k, CREAM, MARK_D))


def icon(px, radius=0.1875, pad=0.74):
    q = 8 if px <= 64 else 4; W = px * q
    tile = Image.new("RGBA", (W, W), (0, 0, 0, 0)); dr = ImageDraw.Draw(tile)
    dr.rounded_rectangle((0, 0, W - 1, W - 1), radius=int(W * radius), fill=GREEN)
    kk = pad * W / (YB - YT); dx, dy = (W - (X3 - X0) * kk) / 2 - X0 * kk, (W - pad * W) / 2 - YT * kk
    for p in POLYS:
        dr.polygon([(x * kk + dx, y * kk + dy) for x, y in p], fill=CREAM)
    return tile.resize((px, px), Image.LANCZOS)


icon(32, pad=0.8).save(ROOT + "/assets/favicon-32.png")
icon(180, radius=0, pad=0.66).convert("RGB").save(ROOT + "/assets/apple-touch-icon.png")     # iOS rounds it itself
icon(48, pad=0.8).save(ROOT + "/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])


# ---------------------------------------------------------------- put it where the pages draw it
def sub(path, pattern, repl, count=1):
    s = open(ROOT + "/" + path, encoding="utf-8").read()
    s2, k2 = re.subn(pattern, lambda m: repl, s, flags=re.S)
    assert k2 == count, (path, pattern[:50], k2)
    open(ROOT + "/" + path, "w", encoding="utf-8").write(s2)


LOCK_RE = r'<svg xmlns="http://www\.w3\.org/2000/svg" viewBox="[^"]+" class="hh-lockup" aria-hidden="true">.*?</svg>'
sub("assets/site-header.js", LOCK_RE, INLINE)
sub("assets/site-footer.js", LOCK_RE, INLINE)
sub("tools/sitegen/build.py", r'SPX_MARK = "[^"]*"', 'SPX_MARK = "%s"' % MARK_D)
print("lockup %d bytes, emblem path %d bytes" % (len(LOCKUP), len(MARK_D)))
print("frames x %s %s | %s %s, y %s %s; square top %s bottom %s; meets the frames at y %s (top) and %s (bottom)" % (
    n(X0), n(L1), n(R0), n(X3), n(YT), n(YB), n(CY - RO), n(CY + RO), n(ul_o - L1), n(L1 - ll_o)))
