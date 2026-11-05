# Procedural textures for the port model: weathered hull atlases (ship + tanker), container atlases (4 paint variants +
# a shared corrugation normal map), the open crate's interior, floor planks, deck, concrete, accommodation wall tile and
# a tileable water normal map. Everything is generated (noise, streaks, text) so the look can be tuned by re-running.
# Usage: venv/bin/python texgen.py <out_dir>
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
SUP = '/System/Library/Fonts/Supplemental/'
F_BOLD, F_DIN, F_DINA, F_ARIAL = SUP + 'Arial Bold.ttf', SUP + 'DIN Condensed Bold.ttf', SUP + 'DIN Alternate Bold.ttf', SUP + 'Arial.ttf'

def rgb(h): return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0

def _grid_resize(g, w, h):
    im = Image.fromarray(g.astype(np.float32), mode='F').resize((w, h), Image.BICUBIC)
    return np.asarray(im, np.float32)

def noise(w, h, cell, octaves=4, seed=0, tile=False, aspect=1.0):
    """fbm value noise in [0,1]; cell = feature size in px (x), aspect stretches features vertically."""
    r = np.random.default_rng(seed); out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0.0; c = float(cell)
    for _ in range(octaves):
        gw = max(2, int(round(w / c))); gh = max(2, int(round(h / (c * aspect))))
        g = r.random((gh, gw)).astype(np.float32)
        if tile:
            n = _grid_resize(np.tile(g, (3, 3)), 3 * w, 3 * h)[h:2 * h, w:2 * w]
        else:
            n = _grid_resize(np.pad(g, 1, mode='reflect'), w + int(2 * w / gw), h + int(2 * h / gh))[int(h / gh):int(h / gh) + h, int(w / gw):int(w / gw) + w]
        out += amp * n; tot += amp; amp *= 0.5; c = max(1.0, c / 2)
    out /= tot
    return (out - out.min()) / max(1e-6, out.max() - out.min())

def mix(img, color, m):
    """img (h,w,3) float, color rgb or (h,w,3), m (h,w) in [0,1]."""
    return img * (1 - m[..., None]) + np.asarray(color, np.float32) * m[..., None]

def streaks(h, w, n, xs, y0s, lens, widths, seed, strength=(0.4, 0.9)):
    """Vertical rust/dirt drips. xs, y0s: arrays or callables; returns a mask (h,w)."""
    r = np.random.default_rng(seed); m = np.zeros((h, w), np.float32)
    for i in range(n):
        x0 = xs(r) if callable(xs) else xs[i]; y0 = y0s(r, x0) if callable(y0s) else y0s[i]
        L = r.uniform(*lens); wd = r.uniform(*widths); s = r.uniform(*strength)
        ya, yb = int(max(0, y0)), int(min(h, y0 + L))
        if yb <= ya: continue
        ys = np.arange(ya, yb); t = (ys - y0) / L
        wob = np.cumsum(r.normal(0, 0.15, len(ys)))                       # drips wander a little
        xa, xb = int(max(0, x0 - 4 * wd - 6)), int(min(w, x0 + 4 * wd + 6))
        if xb <= xa: continue
        xx = np.arange(xa, xb)
        widen = 1 + 0.8 * t                                               # streaks spread as they run down
        prof = np.exp(-((xx[None, :] - x0 - wob[:, None]) / (wd * widen[:, None])) ** 2)
        flick = 0.6 + 0.4 * _grid_resize(r.random((max(2, len(ys) // 6), 1)).astype(np.float32), 1, len(ys))[:, 0]
        val = s * ((1 - t) ** 1.3)[:, None] * flick[:, None] * prof
        m[ya:yb, xa:xb] = np.maximum(m[ya:yb, xa:xb], val)
    return np.clip(m, 0, 1)

def text_layer(size, text, font_path, height_px, x, y, fill=255, anchor='lm', sx=1.0, rotate=0):
    """Render text into an L mask at (x,y). sx squeezes horizontally (for anisotropic texel sizes)."""
    W, H = size; f = ImageFont.truetype(font_path, max(4, int(height_px * 1.38)))
    bb = f.getbbox(text); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    tmp = Image.new('L', (tw + 8, th + 8), 0); ImageDraw.Draw(tmp).text((4 - bb[0], 4 - bb[1]), text, font=f, fill=fill)
    tmp = tmp.resize((max(1, int((tw + 8) * sx)), max(1, int((th + 8) * height_px / max(1, th)))), Image.LANCZOS)
    if rotate: tmp = tmp.rotate(rotate, expand=True, resample=Image.BICUBIC)
    lay = Image.new('L', (W, H), 0)
    ox = {'l': x, 'm': x - tmp.width / 2, 'r': x - tmp.width}[anchor[0]]; oy = {'t': y, 'm': y - tmp.height / 2, 'b': y - tmp.height}[anchor[1]]
    lay.paste(tmp, (int(ox), int(oy)))
    return np.asarray(lay, np.float32) / 255.0

def logo_layer(size, x, y, hpx, sx=1.0, line=None):
    """The HexaHessman mark, flat: two tall frames with a tilted square between, drawn as outlines."""
    W, H = size; s = hpx; lw = line or max(2, int(s * 0.07))
    lay = Image.new('L', (W, H), 0); d = ImageDraw.Draw(lay)
    bw = 0.34 * s
    for bx, top in ((x, y + 0.14 * s), (x + 0.66 * s * sx, y)):
        d.rectangle([bx, top, bx + bw * sx, top + 0.86 * s], outline=255, width=lw)
    cx, cy, rr = x + 0.5 * s * sx, y + 0.55 * s, 0.24 * s
    pts = [(cx + rr * math.cos(a) * sx, cy + rr * math.sin(a)) for a in (math.radians(35 + 90 * k) for k in range(4))]
    d.polygon(pts, outline=255, width=lw)
    return np.asarray(lay, np.float32) / 255.0


F_GEIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts', 'Geist-SemiBold.ttf')
if not os.path.exists(F_GEIST): F_GEIST = os.environ.get('GEIST_TTF', F_BOLD)

def _mark_img(box_px, ss=4):
    """The HexaHessman mark exactly as the site header SVG (viewBox 48): two double-outlined bars and a
    double-outlined diamond between them. Returns an L image box_px square (supersampled for clean lines)."""
    S = box_px * ss; k = S / 48.0
    im = Image.new('L', (S, S), 0); d = ImageDraw.Draw(im)
    def rect(x, y, w, h, sw):
        lw = max(1, int(round(sw * k))); d.rectangle([x * k, y * k, (x + w) * k, (y + h) * k], outline=255, width=lw)
    def poly(pts, sw):
        lw = max(1, int(round(sw * k))); q = [(x * k, y * k) for x, y in pts]; d.line(q + [q[0], q[1]], fill=255, width=lw, joint='curve')
    rect(2.5, 3, 13, 42, 1.6); rect(5.5, 6, 7, 36, 1.0)
    rect(32.5, 3, 13, 42, 1.6); rect(35.5, 6, 7, 36, 1.0)
    poly([(24, 9.5), (38.5, 24), (24, 38.5), (9.5, 24)], 1.6); poly([(24, 14), (34, 24), (24, 34), (14, 24)], 1.0)
    return im.resize((box_px, box_px), Image.LANCZOS)

def brand_layer(size, cx, cy, box_px, sx=1.0, mark_only=False):
    """Logo lockup as in the site header: 26px mark, 9px gap, 'HexaHessman' at 20px Geist SemiBold (-0.03em).
    Rendered isotropically, then squeezed by sx for textures whose texels are not square. Centred on (cx, cy)."""
    mark = _mark_img(int(box_px))
    if mark_only: lock = mark
    else:
        fs = box_px * 20 / 26; f = ImageFont.truetype(F_GEIST, int(round(fs))); gap = box_px * 9 / 26
        chars = 'HexaHessman'; track = -0.03 * fs
        widths = [f.getlength(c) for c in chars]; tw = sum(widths) + track * (len(chars) - 1)
        W = int(box_px + gap + tw + 4); H = int(box_px)
        lock = Image.new('L', (W, H), 0); lock.paste(mark, (0, 0))
        d = ImageDraw.Draw(lock); x = box_px + gap; asc, desc = f.getmetrics()
        for c, w in zip(chars, widths):
            d.text((x, H / 2), c, font=f, fill=255, anchor='lm'); x += w + track
    lock = lock.resize((max(1, int(lock.width * sx)), lock.height), Image.LANCZOS)
    lay = Image.new('L', size, 0); lay.paste(lock, (int(cx - lock.width / 2), int(cy - lock.height / 2)))
    return np.asarray(lay, np.float32) / 255.0

def save(img, name, q=88):
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, name), quality=q)
    print('TEX', name, img.shape[1], 'x', img.shape[0])

def normal_from_height(hm, strength):
    gy, gx = np.gradient(hm.astype(np.float32))
    n = np.dstack((-gx * strength, gy * strength, np.ones_like(hm)))   # +Y up in tangent space, rows go down
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n * 0.5 + 0.5

# ================================================================== hull atlases
def hull_atlas(fname, X0, X1, D, W, HH, green, red, boot_h, wl_h, name, name_x, name_h, name_size, marks_x, seed, scuffs=()):
    """Atlas: top half = the +Y (tanker) side seen from outside (bow on the left); bottom half = the -Y (quay) side
    (bow on the right). Rows run from the deck edge (top) to the keel (bottom). Columns are linear in hull station x."""
    ppm_u = W / (X1 - X0); ppm_v = HH / D; sx = ppm_u / ppm_v
    def side(seed2, bow_left):
        r = np.random.default_rng(seed2)
        hrow = D * (1 - (np.arange(HH) + 0.5) / HH)                  # height above keel per row
        img = np.zeros((HH, W, 3), np.float32) + green
        n1 = noise(W, HH, 220, 4, seed2); n2 = noise(W, HH, 30, 3, seed2 + 1)
        img *= (0.9 + 0.16 * n1 + 0.05 * n2)[..., None]
        # plate seams: strakes every 2.4 m, butts every ~9.6 m
        for hs in np.arange(2.4, D, 2.4):
            rr = int((1 - hs / D) * HH)
            if 0 < rr < HH - 1: img[rr] *= 0.86; img[rr + 1] *= 1.04
        for xs in np.arange(X0 + 4.8, X1, 9.6):
            c = int((xs - X0) * ppm_u)
            if 0 < c < W - 1: img[:, c] *= 0.88; img[:, c + 1] *= 1.03
        # red underwater / boot-top below boot_h
        below = (hrow < boot_h)[:, None] * np.ones((1, W), bool)
        redimg = np.zeros_like(img) + red; redimg *= (0.88 + 0.2 * noise(W, HH, 120, 4, seed2 + 2))[..., None]
        img = np.where(below[..., None], redimg, img)
        # waterline fouling: a dark green-brown band at the waterline, fading upwards
        dist = (hrow - wl_h)
        band = np.exp(-np.clip(dist, 0, None) / 0.35) * (dist > -0.25)
        img = mix(img, rgb('3A3A22'), (band[:, None] * (0.55 + 0.35 * noise(W, HH, 18, 3, seed2 + 3)) * 0.8))
        # grime just above the boot-top and under the deck edge
        g1 = np.exp(-np.clip(hrow - boot_h, 0, None) / 0.9) * (hrow >= boot_h)
        g2 = np.exp(-np.clip(D - hrow, 0, None) / 0.5)
        img *= (1 - 0.25 * g1[:, None] * noise(W, HH, 40, 3, seed2 + 4))[..., None]
        img *= (1 - 0.18 * g2[:, None])[..., None]
        # rust: drips from the deck edge, from scuppers, and big ones from the hawse pipes
        deck_row = 2
        m = streaks(HH, W, int(W / 22), lambda r: r.uniform(0, W), lambda r, x: deck_row + r.uniform(0, 6),
                    (0.8 * ppm_v, 4.5 * ppm_v), (0.8, 2.6), seed2 + 5, (0.45, 0.95))
        scup = np.arange(X0 + 6, X1 - 6, 7.5)
        sxp = [(s - X0) * ppm_u + r.uniform(-8, 8) for s in scup]
        m = np.maximum(m, streaks(HH, W, len(sxp), sxp, [(1 - (D - 1.6) / D) * HH] * len(sxp), (1.5 * ppm_v, 5 * ppm_v), (1.2, 2.6), seed2 + 6, (0.5, 0.9)))
        for hx in marks_x.get('hawse', []):
            c = (hx - X0) * ppm_u; m = np.maximum(m, streaks(HH, W, 9, [c + r.uniform(-14, 14) for _ in range(9)], [(1 - marks_x['hawse_h'] / D) * HH + r.uniform(0, 6) for _ in range(9)], (0.5 * (marks_x['hawse_h'] - wl_h) * ppm_v, (marks_x['hawse_h'] - wl_h) * ppm_v), (2, 5), seed2 + 7, (0.6, 1.0)))
        rustc = (rgb('7A3E1E')[None, None, :] * (0.75 + 0.45 * noise(W, HH, 14, 3, seed2 + 8))[..., None])
        img = mix(img, rustc, m * (hrow >= boot_h)[:, None] * 0.95)
        spots = np.clip((noise(W, HH, 10, 3, seed2 + 9) - 0.78) * 6, 0, 1) * (0.4 + 0.6 * noise(W, HH, 200, 2, seed2 + 10))
        img = mix(img, rgb('6E3A1C'), spots * 0.8)
        for x0 in scuffs:   # tyre rub marks on the tanker
            c = (x0 - X0) * ppm_u
            cc = np.arange(W)[None, :]; rr = hrow[:, None]
            mk = np.exp(-((cc - c) / (1.6 * ppm_u)) ** 2) * np.exp(-((rr - (D - 1.3)) / 0.7) ** 2) * noise(W, HH, 6, 2, seed2 + int(x0) + 50)
            img = mix(img, rgb('1A1A1A'), np.clip(mk * 1.4, 0, 0.85))
        if bow_left: img = img[:, ::-1]
        return img
    def decorate(img, bow_left):
        Hh, Ww = img.shape[:2]; lay = np.zeros((Hh, Ww), np.float32)
        col = lambda x: ((X1 - x) if bow_left else (x - X0)) * ppm_u
        row = lambda h: (1 - h / D) * Hh
        # ship's name near the bow
        cx = col(name_x); lay = np.maximum(lay, text_layer((Ww, Hh), name, F_BOLD, name_size * ppm_v, cx, row(name_h), anchor='mm', sx=sx))
        # draft marks at the stem, midship and stern: metre numbers with half-metre ticks
        for xm in marks_x['draft']:
            c = col(xm)
            for mtr in range(1, int(D * 0.75)):
                lay = np.maximum(lay, text_layer((Ww, Hh), f'{mtr}M', F_DINA, 0.3 * ppm_v, c, row(mtr), anchor='lm', sx=sx))
                lay = np.maximum(lay, text_layer((Ww, Hh), str(int(5)), F_DINA, 0.2 * ppm_v, c, row(mtr + 0.5), anchor='lm', sx=sx) * 0.9)
        # Plimsoll load-line mark amidships
        if marks_x.get('plimsoll') is not None:
            c = col(marks_x['plimsoll']); hcen = wl_h + marks_x['plimsoll_fb']; r0 = 0.55 * ppm_v
            L = Image.new('L', (Ww, Hh), 0); d = ImageDraw.Draw(L); yy = row(hcen)
            d.ellipse([c - r0 * sx, yy - r0, c + r0 * sx, yy + r0], outline=255, width=3)
            d.rectangle([c - 0.75 * ppm_u, yy - 1.5, c + 0.75 * ppm_u, yy + 1.5], fill=255)
            d.rectangle([c - 1.1 * ppm_u, row(hcen + 1.0) - 1, c + 1.1 * ppm_u, row(hcen + 1.0) + 1], fill=255)   # deck line
            for k, lab in enumerate(('TF', 'F', 'T', 'S', 'W')):
                yk = row(hcen + 0.25 - k * 0.12)
                d.rectangle([c + (1.1 if not bow_left else -1.6) * ppm_u, yk - 1, c + (1.6 if not bow_left else -1.1) * ppm_u, yk + 1], fill=255)
            lay = np.maximum(lay, np.asarray(L, np.float32) / 255)
            lay = np.maximum(lay, text_layer((Ww, Hh), 'L   R', F_DINA, 0.4 * ppm_v, c, row(hcen + 0.35), anchor='mm', sx=sx))
        dirt = 0.8 + 0.2 * noise(Ww, Hh, 12, 3, 77)
        return mix(img, rgb('E9E7E0'), lay * dirt)
    top = decorate(side(seed, True), True); bot = decorate(side(seed + 100, False), False)
    save(np.vstack([top, bot]), fname)

hull_atlas('hull_ship.jpg', -75.0, 75.0, 14.0, 4096, 512, rgb('1B4634'), rgb('8E3F2B'), 8.0, 7.0,
           'HEXA HESSMAN', 50.5, 11.6, 1.7, {'draft': [72.0, -73.0], 'hawse': [66.0], 'hawse_h': 11.8, 'plimsoll': 4.0, 'plimsoll_fb': 2.6}, 11)
hull_atlas('hull_tanker.jpg', -25.0, 25.0, 4.6, 2048, 256, rgb('1D4A37'), rgb('8E3F2B'), 2.9, 2.3,
           'HEXA BUNKER 1', 19.0, 3.7, 0.55, {'draft': [23.0, -24.0], 'hawse': [21.5], 'hawse_h': 3.9}, 21, scuffs=(-14.0, -7.0, 0.0, 7.0, 14.0))

# ================================================================== container atlases
# layout (image rows top-down): top half = long side (12.19 x 2.59 m); bottom half: [0,1/4] door end, [1/4,1/2] closed end,
# [1/2,1] roof. The same layout is used for the shared normal map and the crate interior.
CL, CW, CH = 12.19, 2.44, 2.59
def corr_profile(u, pitch, flat=0.36):
    """trapezoidal corrugation height in [0,1] for coordinate u (metres) with the given pitch."""
    p = (u / pitch) % 1.0
    up, down = (0.5 - flat) / 2, (0.5 - flat) / 2
    h = np.where(p < flat, 1.0, np.where(p < flat + up, 1 - (p - flat) / up, np.where(p < 0.5 + flat / 2 + down, 0.0, (p - (0.5 + flat / 2 + down)) / max(1e-6, 1 - (0.5 + flat / 2 + down)))))
    return np.clip(h, 0, 1)

def container_atlas(fname, W, base, logo=None, logo_col='EDEBE3', code='HXHU 401287 4', rust=0.5, seed=0, interior=False):
    H = W // 2; half = H // 2
    img = np.zeros((H, W, 3), np.float32) + base
    # --- long side
    sw, sh = W, half; ppm = sw / CL
    u = (np.arange(sw) + 0.5) / ppm
    corr = corr_profile(u, 0.278)[None, :] * np.ones((sh, 1))
    side = np.zeros((sh, sw, 3), np.float32) + base
    side *= (0.93 + 0.1 * corr)[..., None]
    side *= (0.92 + 0.14 * noise(sw, sh, 60, 4, seed))[..., None]
    rails_m = np.zeros((sh, sw), np.float32); rails_m[:int(0.11 * sh / CH * 1)] = 1
    top_r = int(0.12 / CH * sh); bot_r = int(0.16 / CH * sh); post = int(0.17 * ppm)
    side[:top_r] *= 0.82; side[sh - bot_r:] *= 0.75; side[:, :post] *= 0.86; side[:, sw - post:] *= 0.86
    if not interior:
        lay = np.zeros((sh, sw), np.float32)
        sxs = ppm / (sh / CH)                       # texel aspect of the side region (width px per m / height px per m)
        if logo:
            lay = np.maximum(lay, brand_layer((sw, sh), sw * 0.5, sh * 0.5, 1.15 / CH * sh, sxs))
        lay = np.maximum(lay, text_layer((sw, sh), code, F_DINA, 0.2 / CH * sh, int(sw - 0.5 * ppm), int(0.35 / CH * sh), anchor='rm'))
        lay = np.maximum(lay, text_layer((sw, sh), '45G1', F_DINA, 0.16 / CH * sh, int(sw - 0.5 * ppm), int(0.62 / CH * sh), anchor='rm'))
        lay *= (0.75 + 0.25 * corr) * (0.8 + 0.2 * noise(sw, sh, 8, 2, seed + 1))
        side = mix(side, rgb(logo_col), lay)
    # weathering: drips from the top rail, rust along the bottom rail and in the grooves, faded patches
    m = streaks(sh, sw, int(28 * rust + 6), lambda r: r.uniform(0, sw), lambda r, x: top_r + r.uniform(0, 3), (0.3 * sh, 0.9 * sh), (1.0, 3.0), seed + 2, (0.2, 0.6))
    rows = np.arange(sh)[:, None]
    bottom = np.exp(-np.clip(sh - bot_r - rows, 0, None) / (0.25 * sh)) * noise(sw, sh, 10, 3, seed + 3)
    groove = (1 - corr) * np.clip((noise(sw, sh, 14, 3, seed + 4) - 0.7) * 3, 0, 1) * 0.6
    rustm = np.clip(m * 0.7 + bottom * 0.8 * rust + groove * rust, 0, 1)
    side = mix(side, rgb('6F3A1D') * (0.8 + 0.3 * noise(sw, sh, 9, 2, seed + 5))[..., None], rustm * 0.9)
    fade = np.clip((noise(sw, sh, 120, 3, seed + 6) - 0.55) * 2.5, 0, 1) * 0.25
    side = mix(side, side * 0.6 + 0.4 * 0.75, fade)
    img[:half] = side
    # --- door end (2.44 x 2.59 m) with two doors, horizontal panel swages, gasket frame and markings
    dw = W // 4; dpm = dw / CW
    door = np.zeros((half, dw, 3), np.float32) + base
    rows_m = (np.arange(half) + 0.5) / (half / CH)
    sw_h = corr_profile(rows_m, 0.48, 0.6)[:, None] * np.ones((1, dw))
    door *= (0.93 + 0.08 * sw_h)[..., None] * (0.92 + 0.14 * noise(dw, half, 30, 3, seed + 7))[..., None]
    fr = int(0.1 * dpm)
    door[:fr] *= 0.7; door[half - fr:] *= 0.7; door[:, :fr] *= 0.7; door[:, dw - fr:] *= 0.7; door[:, dw // 2 - 2: dw // 2 + 2] *= 0.45
    if not interior:
        lay = np.zeros((half, dw), np.float32)
        lay = np.maximum(lay, text_layer((dw, half), code, F_DINA, 0.13 * dpm, int(dw * 0.94), int(0.3 * dpm), anchor='rm'))
        lay = np.maximum(lay, text_layer((dw, half), '45G1', F_DINA, 0.11 * dpm, int(dw * 0.94), int(0.48 * dpm), anchor='rm'))
        for k, t in enumerate(('MAX GROSS 32.500 KG', 'TARE        3.800 KG', 'NET        28.700 KG', 'CU.CAP     76.3 CU.M')):
            lay = np.maximum(lay, text_layer((dw, half), t, F_DINA, 0.06 * dpm, int(dw * 0.06), int((0.3 + k * 0.09) * dpm), anchor='lm') * 0.9)
        if logo: lay = np.maximum(lay, brand_layer((dw, half), dw * 0.73, half * 0.7, 0.5 / CH * half, dpm / (half / CH), mark_only=True))
        L = Image.new('L', (dw, half), 0); ImageDraw.Draw(L).rectangle([int(dw * 0.08), int(half * 0.78), int(dw * 0.2), int(half * 0.86)], fill=200)  # CSC plate
        lay = np.maximum(lay, np.asarray(L, np.float32) / 255)
        door = mix(door, rgb(logo_col), lay * (0.85 + 0.15 * noise(dw, half, 6, 2, seed + 8)))
    m = streaks(half, dw, 10, lambda r: r.uniform(0, dw), lambda r, x: fr + r.uniform(0, 3), (0.3 * half, 0.9 * half), (0.8, 2.0), seed + 9, (0.2, 0.55))
    door = mix(door, rgb('6F3A1D'), np.clip(m * 0.7 + (np.arange(half)[:, None] > half * 0.85) * noise(dw, half, 8, 2, seed + 10) * rust, 0, 1) * 0.8)
    img[half:, :dw] = door
    # --- closed end: vertical corrugation, a little code
    ce = np.zeros((half, dw, 3), np.float32) + base
    uc = (np.arange(dw) + 0.5) / dpm
    ce *= (0.93 + 0.1 * corr_profile(uc, 0.278)[None, :])[..., None] * (0.9 + 0.15 * noise(dw, half, 30, 3, seed + 11))[..., None]
    ce = mix(ce, rgb('6F3A1D'), streaks(half, dw, 8, lambda r: r.uniform(0, dw), lambda r, x: r.uniform(0, 4), (0.3 * half, half), (0.8, 2), seed + 12, (0.2, 0.6)) * 0.8)
    img[half:, dw:2 * dw] = ce
    # --- roof: dented, dirty, rusty
    rw = W // 2
    roof = np.zeros((half, rw, 3), np.float32) + base
    roof *= (0.8 + 0.25 * noise(rw, half, 40, 4, seed + 13))[..., None]
    roof = mix(roof, rgb('5B3A22'), np.clip((noise(rw, half, 16, 4, seed + 14) - 0.62) * 2 * rust, 0, 0.5))
    roof = mix(roof, rgb('3A3A34'), np.clip((noise(rw, half, 90, 3, seed + 15) - 0.4), 0, 0.5))
    if interior: roof = np.zeros((half, rw, 3), np.float32) + base * (0.85 + 0.1 * noise(rw, half, 60, 3, seed + 16))[..., None]
    img[half:, 2 * dw:] = roof
    save(img, fname)

container_atlas('cont_green.jpg', 2048, rgb('23503A'), logo='HexaHessman', code='HXHU 401287 4', rust=0.55, seed=31)
container_atlas('cont_green2.jpg', 1024, rgb('2E6245'), logo=None, code='HXHU 552018 0', rust=0.6, seed=41)
container_atlas('cont_pale.jpg', 1024, rgb('B9B6A8'), logo=None, logo_col='22312B', code='TGHU 873301 2', rust=0.7, seed=51)
container_atlas('cont_dark.jpg', 1024, rgb('183A2A'), logo=None, code='HXHU 330915 6', rust=0.65, seed=61)
container_atlas('crate_inside.jpg', 1024, rgb('6D7369'), logo=None, rust=0.25, seed=71, interior=True)

# shared normal map for every container (same atlas layout)
def container_normal(fname, W):
    H = W // 2; half = H // 2; hm = np.zeros((H, W), np.float32)
    u = (np.arange(W) + 0.5) / (W / CL); hm[:half] = corr_profile(u, 0.278)[None, :] * 3.0
    hm[:half] += noise(W, half, 50, 3, 3) * 0.6
    dw = W // 4; dpm = dw / CW
    rows_m = (np.arange(half) + 0.5) / (half / CH)
    hm[half:, :dw] = corr_profile(rows_m, 0.48, 0.6)[:, None] * 2.0 + noise(dw, half, 20, 3, 4) * 0.4
    uc = (np.arange(dw) + 0.5) / dpm; hm[half:, dw:2 * dw] = corr_profile(uc, 0.278)[None, :] * 3.0
    hm[half:, 2 * dw:] = noise(W // 2, half, 60, 4, 5) * 2.5
    p = np.pad(hm, 1, mode='edge'); hm = sum(p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9.0
    save(normal_from_height(hm, 1.2), fname, 92)
container_normal('cont_normal.jpg', 1024)

# ================================================================== crate floor planks (12 x 2.3 m)
def planks(fname, W=1024, H=256):
    r = np.random.default_rng(5); img = np.zeros((H, W, 3), np.float32)
    y = 0
    while y < H:
        h = min(int(r.uniform(0.11, 0.17) / 2.3 * H), H - y); tone = rgb(r.choice(['8A6A45', '7B5C3A', '96744C', '6E5233'])) * r.uniform(0.9, 1.08)
        grain = noise(W, max(2, h), 3, 3, int(r.integers(1e6)), aspect=0.08)
        img[y:y + h] = tone * (0.85 + 0.25 * grain)[..., None]
        img[y:y + 1] *= 0.35
        cut = int(r.uniform(0.1, 0.9) * W); img[y:y + h, cut:cut + 2] *= 0.4
        y += h
    img = mix(img, rgb('2E2418'), np.clip((noise(W, H, 40, 4, 9) - 0.55) * 2.5, 0, 0.8))   # stains
    save(img, fname)
planks('crate_floor.jpg')

# ================================================================== tileable deck, concrete, wall, water
def tile_deck(fname, base, W=1024, seed=0):
    img = np.zeros((W, W, 3), np.float32) + base
    img *= (0.85 + 0.25 * noise(W, W, 160, 5, seed, tile=True))[..., None]
    img = mix(img, rgb('6A3B1E'), np.clip((noise(W, W, 18, 4, seed + 1, tile=True) - 0.7) * 3.5, 0, 0.85))
    img = mix(img, rgb('2C2C28'), np.clip((noise(W, W, 70, 4, seed + 2, tile=True) - 0.6) * 1.5, 0, 0.45))
    save(img, fname)
tile_deck('deck_ship.jpg', rgb('5E6B63'), seed=81)
tile_deck('deck_tanker.jpg', rgb('2F5E49'), seed=91)

def tile_concrete(fname, W=1024):
    img = np.zeros((W, W, 3), np.float32) + rgb('A9A496')
    img *= (0.8 + 0.2 * noise(W, W, 200, 5, 101, tile=True) + 0.02 * noise(W, W, 4, 2, 102, tile=True))[..., None]
    img = mix(img, rgb('4A473F'), np.clip((noise(W, W, 120, 5, 103, tile=True) - 0.6) * 1.2, 0, 0.28))
    img[:3] *= 0.6; img[:, :3] *= 0.6                       # expansion joints at the tile edges (8 m slabs)
    save(img, fname)
tile_concrete('concrete.jpg')

def tile_wall(fname, W=512, H=256, seed=111):
    """6 m x 3 m of white superstructure: two windows per tile, a deck line, rust drips from the window corners."""
    ppm = W / 6.0; img = np.zeros((H, W, 3), np.float32) + rgb('E6E4DC')
    img *= (0.94 + 0.08 * noise(W, H, 60, 4, seed, tile=True))[..., None]
    img[int(H * 0.96):] *= 0.78
    L = Image.new('L', (W, H), 0); d = ImageDraw.Draw(L); win = Image.new('L', (W, H), 0); dw = ImageDraw.Draw(win)
    for cx in (1.5, 4.5):
        x0, x1 = int((cx - 0.6) * ppm), int((cx + 0.6) * ppm); y0, y1 = int(H * 0.28), int(H * 0.6)
        d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], fill=255); dw.rectangle([x0, y0, x1, y1], fill=255)
    frame = np.asarray(L, np.float32) / 255; glass = np.asarray(win, np.float32) / 255
    img = mix(img, rgb('B9BAB4'), frame * 0.8)
    sky = np.linspace(1, 0, H)[:, None] * np.ones((1, W))
    img = mix(img, (rgb('2B3D48')[None, None, :] * (0.7 + 0.6 * sky[..., None])), glass)
    m = streaks(H, W, 8, [int((c + dx) * ppm) for c in (1.5, 4.5) for dx in (-0.55, 0.55, -0.1, 0.3)], [int(H * 0.61)] * 8, (0.15 * H, 0.38 * H), (0.8, 1.8), seed + 1, (0.3, 0.7))
    img = mix(img, rgb('8A5A35'), m * 0.7)
    save(img, fname)
tile_wall('wall_white.jpg')

def water_normal(fname, W=512):
    hm = noise(W, W, 64, 5, 121, tile=True) * 1.0 + noise(W, W, 16, 3, 122, tile=True) * 0.35
    save(normal_from_height(hm, 6.0), fname, 92)
water_normal('water_normal.jpg')

def clouds(fname, W=2048):
    n = noise(W, W, 260, 6, 131, tile=True) * 0.75 + noise(W, W, 60, 4, 132, tile=True) * 0.25
    a = np.clip((n - 0.52) / 0.22, 0, 1) ** 1.4
    shade = 0.82 + 0.18 * np.clip((n - 0.5) / 0.3, 0, 1)
    rgba = np.dstack([shade, shade, shade * 1.01, a])
    Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA').save(os.path.join(OUT, fname)); print('TEX', fname)
clouds('clouds.png')
print('DONE')
