"""Dotted world trade map for a product page's PRODUCT RESOURCES block (after the client's sulphur map, 2026-11-11).

Land is drawn as a grid of small squares from assets/vendor/land-110m.json; places are dots (export source, restricted
export source, major import market) with dotted routes between them. A route that crosses the Pacific leaves by one
edge and comes back in at the other. Usage: python3 tools/drawings/trade_map.py   (writes every map in MAPS)
"""
import json, math, os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 1600, 760                       # drawing size
LON0, LON1, LAT0, LAT1 = -168, 190, 80, -58   # window (the map runs a little past 180° so the far east of Russia shows whole)
STEP = 2.1                             # degrees between dots
COL = {"export": "#F2D935", "restricted": "#F08A24", "import": "#F5F2E8"}
LEGEND = [("export", "Export source"), ("restricted", "Restricted export source"), ("import", "Major import market")]

MAPS = {
    "sulphur-trade-map": {
        "places": [("Canada", -114, 54, "export", "nw"), ("Russia · Kazakhstan", 53, 49, "restricted", "ne"), ("Middle East", 51, 26, "export", "sw"),
                   ("Morocco", -7, 32, "import", "nw"), ("China", 119, 32, "import", "ne"), ("India", 73, 20, "import", "se"),
                   ("Indonesia", 121, -3, "import", "se"), ("Brazil", -43, -22, "import", "se")],
        "routes": [("Middle East", "Morocco", .18), ("Middle East", "China", -.22), ("Middle East", "India", .2), ("Middle East", "Indonesia", .12),
                   ("Middle East", "Brazil", .34), ("Canada", "China", "pacific"), ("Canada", "Indonesia", "pacific")],
    },
}


def land_mask():
    t = json.load(open(os.path.join(ROOT, "assets/vendor/land-110m.json")))
    sx, sy = t["transform"]["scale"]; tx, ty = t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0; pts = []
        for dx, dy in a:
            x += dx; y += dy; pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    S = 4; im = Image.new("L", (360 * S, 180 * S), 0); d = ImageDraw.Draw(im)
    def ring(idx):
        out = []
        for i in idx:
            out += arcs[i] if i >= 0 else arcs[~i][::-1]
        return out
    def polys(g):
        if g["type"] == "Polygon": yield g["arcs"]
        elif g["type"] == "MultiPolygon": yield from g["arcs"]
        elif g["type"] == "GeometryCollection":
            for q in g["geometries"]: yield from polys(q)
    for obj in t["objects"].values():
        for poly in polys(obj):
            for k, r in enumerate(poly):
                pts = [((lo + 180) * S, (90 - la) * S) for lo, la in ring(r)]
                if len(pts) > 2: d.polygon(pts, fill=255 if k == 0 else 0)
    return im, S


def X(lon): return (lon - LON0) / (LON1 - LON0) * W
def Y(lat): return (LAT0 - lat) / (LAT0 - LAT1) * H


def build(name, spec):
    im, S = land_mask(); px = im.load()
    sq = W / ((LON1 - LON0) / STEP) * 0.62; path = []
    lat = LAT0 - STEP / 2
    while lat > LAT1:
        lon = LON0 + STEP / 2
        while lon < LON1:
            lo = ((lon + 180) % 360) - 180
            if lat > -60 and px[min(360 * S - 1, int((lo + 180) * S)), min(180 * S - 1, int((90 - lat) * S))] > 127:
                path.append(f"M{X(lon) - sq / 2:.1f} {Y(lat) - sq / 2:.1f}h{sq:.1f}v{sq:.1f}h-{sq:.1f}z")
            lon += STEP
        lat -= STEP
    P = {n: (X(lo), Y(la), kind, side) for n, lo, la, kind, side in spec["places"]}
    routes = ""
    for a, b, bend in spec["routes"]:
        (x1, y1, *_), (x2, y2, *_) = P[a], P[b]
        if bend == "pacific":   # out past the left edge, back in from the right
            routes += f'<path d="M{x1:.0f} {y1:.0f}Q{x1 * .45:.0f} {y1 + 6:.0f} -20 {y1 + 70:.0f}"/><path d="M{W + 20} {(y1 + y2) / 2 + 20:.0f}Q{(x2 + W) / 2:.0f} {y2 - 20 if y2 < H / 2 else y2 - 110:.0f} {x2:.0f} {y2:.0f}"/>'
        else:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2; dx, dy = x2 - x1, y2 - y1
            routes += f'<path d="M{x1:.0f} {y1:.0f}Q{mx - dy * bend:.0f} {my + dx * bend:.0f} {x2:.0f} {y2:.0f}"/>'
    dots = labels = ""
    for n, (x, y, kind, side) in P.items():
        dots += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="7.5" fill="{COL[kind]}"/><circle cx="{x:.0f}" cy="{y:.0f}" r="13" fill="{COL[kind]}" opacity=".18"/>'
        ax = "end" if "w" in side else "start"; ox = -16 if "w" in side else 16; oy = -16 if "n" in side else 30
        labels += f'<text x="{x + ox:.0f}" y="{y + oy:.0f}" text-anchor="{ax}">{n}</text>'
    lg = ""; lx = 44
    for kind, text in LEGEND:
        if not any(p[2] == kind for p in P.values()): continue
        lg += f'<circle cx="{lx}" cy="{H + 46}" r="8" fill="{COL[kind]}"/><text x="{lx + 22}" y="{H + 53}">{text}</text>'; lx += 60 + len(text) * 13.4
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H + 90}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="21" letter-spacing="1.5">'
           f'<rect width="{W}" height="{H + 90}" fill="#161613"/><path d="{"".join(path)}" fill="#4B4A3D"/>'
           f'<g fill="none" stroke="#D9C232" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="1 9" opacity=".9">{routes}</g>{dots}'
           f'<g fill="#EDEAD9">{labels}</g><g fill="#D8D5C4">{lg}</g></svg>')
    out = os.path.join(ROOT, "assets/products/resources", name + ".svg"); open(out, "w").write(svg)
    print(out, len(svg) // 1024, "KB", len(path), "dots")


if __name__ == "__main__":
    for n, s in MAPS.items(): build(n, s)
