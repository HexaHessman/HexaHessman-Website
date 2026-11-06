"""Split the orange fender panels out of a photo so they can be animated in one by one.
For each photo writes <slug>-base.jpg (the photo with the orange panels turned to a dull grey) and
<slug>-p<N>.webp (each panel, transparent outside it, cropped to its box), plus <slug>-panels.json with the boxes
in % of the photo, ordered left to right. Stacking every panel on the base gives back the exact photo.
Run: python3 tools/drawings/orange_layers.py <site root> spc-cone fe-element
"""
import sys, os, json, colorsys
from collections import deque
from PIL import Image, ImageFilter

def is_orange(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return (h < 0.075 or h > 0.97) and s > 0.45 and v > 0.28 and r > g + 40

def run(root, slug, min_area=0.0012):
    src = os.path.join(root, f"assets/engineering/shibata/{slug}.jpg")
    im = Image.open(src).convert("RGB"); W, H = im.size; px = im.load()
    mask = Image.new("L", (W, H), 0); m = mask.load()
    for y in range(H):
        for x in range(W):
            if is_orange(*px[x, y]): m[x, y] = 255
    # soften: close small holes, grow by a pixel so the edge fringe goes with the panel
    mask = mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(3)); m = mask.load()
    seen = bytearray(W * H); comps = []
    for y in range(H):
        for x in range(W):
            if m[x, y] < 128 or seen[y * W + x]: continue
            q = deque([(x, y)]); seen[y * W + x] = 1; pts = []
            while q:
                cx, cy = q.popleft(); pts.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < W and 0 <= ny < H and not seen[ny * W + nx] and m[nx, ny] >= 128:
                        seen[ny * W + nx] = 1; q.append((nx, ny))
            if len(pts) >= min_area * W * H: comps.append(pts)
    # far panels touch each other in the photo: split a blob wherever its column count drops to a thin neck
    split = []
    for pts in comps:
        xs = [a for a, _ in pts]; x0, x1 = min(xs), max(xs) + 1
        col = [0] * (x1 - x0)
        for a, _ in pts: col[a - x0] += 1
        peak = max(col); cuts = [x0]; low = False
        for i, c in enumerate(col):
            if c < peak * 0.22 and not low and i - (cuts[-1] - x0) > 3: cuts.append(x0 + i); low = True
            elif c >= peak * 0.22: low = False
        cuts.append(x1)
        parts = [[(a, b) for a, b in pts if lo <= a < hi] for lo, hi in zip(cuts, cuts[1:])]
        split += [q for q in parts if len(q) >= min_area * W * H * 0.5]
    comps = split
    comps.sort(key=lambda p: min(a for a, _ in p))
    base = im.copy(); bp = base.load(); out = []
    for i, pts in enumerate(comps):
        xs = [a for a, _ in pts]; ys = [b for _, b in pts]; x0, x1, y0, y1 = min(xs), max(xs) + 1, min(ys), max(ys) + 1
        layer = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0)); lp = layer.load()
        for a, b in pts:
            r, g, bl = px[a, b]; lp[a - x0, b - y0] = (r, g, bl, 255)
            l = int(0.30 * r + 0.55 * g + 0.15 * bl); bp[a, b] = (l, l, l)   # the panel, greyed, on the base
        layer = layer.filter(ImageFilter.SMOOTH) if False else layer
        layer.save(os.path.join(root, f"assets/engineering/shibata/{slug}-p{i}.webp"), "WEBP", quality=90, method=6)
        out.append({"l": round(x0 / W * 100, 3), "t": round(y0 / H * 100, 3), "w": round((x1 - x0) / W * 100, 3), "h": round((y1 - y0) / H * 100, 3)})
    base.save(os.path.join(root, f"assets/engineering/shibata/{slug}-base.jpg"), quality=88, optimize=True, progressive=True)
    json.dump(out, open(os.path.join(root, f"assets/engineering/shibata/{slug}-panels.json"), "w"))
    print(slug, (W, H), len(out), "panels")

if __name__ == "__main__":
    root = sys.argv[1]
    for s in sys.argv[2:]: run(root, s)
