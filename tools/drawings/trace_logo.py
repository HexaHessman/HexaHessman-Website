"""Trace a small raster logo into a crisp multi-colour SVG: upscale, split into its main colours, potrace each colour
layer and stack them. Usage: python3 trace_logo.py in.png out.svg "#hex1,#hex2,..."  (the logo's colours)"""
import sys, os, subprocess, tempfile, re
from PIL import Image, ImageFilter

src, dst, cols = sys.argv[1], sys.argv[2], [c.strip() for c in sys.argv[3].split(",")]
im = Image.open(src).convert("RGBA")
S = 8; W, H = im.size
big = im.resize((W * S, H * S), Image.LANCZOS)
px = big.load(); pal = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in cols]
layers = [Image.new("1", big.size, 1) for _ in pal]
lp = [l.load() for l in layers]
for y in range(big.height):
    for x in range(big.width):
        r, g, b, a = px[x, y]
        if a < 110: continue
        k = min(range(len(pal)), key=lambda i: (r - pal[i][0]) ** 2 + (g - pal[i][1]) ** 2 + (b - pal[i][2]) ** 2)
        lp[k][x, y] = 0
paths = []
for k, layer in enumerate(layers):
    layer = layer.convert("L").filter(ImageFilter.MedianFilter(5)).point(lambda v: 255 if v > 127 else 0).convert("1")
    with tempfile.TemporaryDirectory() as d:
        pbm, svg = os.path.join(d, "l.pbm"), os.path.join(d, "l.svg")
        layer.save(pbm); subprocess.run(["potrace", pbm, "-s", "-o", svg, "-t", "40", "-a", "1.1", "-O", "0.6", "-u", "1"], check=True)
        body = open(svg).read()
    ds = re.findall(r'<path d="([^"]+)"', body)
    paths.append(f'<g fill="{cols[k]}">' + "".join(f'<path d="{" ".join(d.split())}"/>' for d in ds) + "</g>")
w, h = W * S, H * S
out = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><g transform="translate(0,{h}) scale(1,-1)">'
       + "".join(paths) + "</g></svg>\n")
open(dst, "w").write(out); print(dst, len(out) // 1024, "KB")
