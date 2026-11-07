"""Real footage -> Terminal-style lines and dots, with a particle sweep that crosses the whole screen.

Footage frame i and wire frame i come from the same camera path (the AI footage follows our 3D path); each wire frame is
nudged onto its footage frame with a homography (ECC on edge maps, smoothed over time) so the lines sit on the real
objects. After the footage ends the wire frames carry on alone, so the camera goes all the way in.

  before T0   the real photo, nothing else (the hero, no particles)
  T0 -> T1    a band of bright dots sweeps across the screen (left to right, slightly tilted). Ahead of it the photo;
              in the band the photo breaks into sparkling dots; behind it the photo is gone to near-black and only the
              thin lines and floating dots remain
  after T1    lines and dots only, on to the end of the wire frames
Usage: python terminal_sweep.py <footage.mp4> <shaded_dir> <wire_dir> <out.mp4> <T0> <T1> [out_width]
"""
import sys, os, subprocess, tempfile, glob
import numpy as np, cv2

src, sdir, wdir, out, T0, T1 = sys.argv[1:7]; T0, T1 = int(T0), int(T1)
OW = int(sys.argv[7]) if len(sys.argv) > 7 else 1920
# sweep shape: 'linear' (left to right) or 'radial:cx,cy' (bursts out from a point to every corner)
MODE = sys.argv[8] if len(sys.argv) > 8 else 'linear'
wires = sorted(glob.glob(os.path.join(wdir, 'f*.png'))); NW = len(wires)
cap = cv2.VideoCapture(src); real = []
while True:
    ok, f = cap.read()
    if not ok: break
    real.append(f)
NF = len(real); H0, W0 = real[0].shape[:2]
W, H = OW, int(round(OW * H0 / W0 / 2) * 2)
print('footage', NF, 'wire', NW, 'out', W, H)

# ---- timing: which 3D frame each footage frame matches (the AI runs a few frames ahead of our path) ----
def edges_n(im):
    x = cv2.cvtColor(cv2.resize(im, (480, 270), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32); x = cv2.GaussianBlur(x, (5, 5), 0)
    x = np.abs(cv2.Laplacian(x, cv2.CV_32F, ksize=3)); x = cv2.GaussianBlur(x, (5, 5), 0); return (x - x.mean()) / (x.std() + 1e-6)
NS = len(glob.glob(os.path.join(sdir, 'f*.png')))
SHE = [edges_n(cv2.imread(os.path.join(sdir, f'f{k:04d}.png'))) for k in range(NS)]
kb = []
for i in range(NF):
    e = edges_n(real[i]); lo, hi = max(0, i - 4), min(NS - 1, i + 10)
    sc = [float((e * SHE[k]).mean()) for k in range(lo, hi + 1)]; kb.append(lo + int(np.argmax(sc)))
off = np.array(kb) - np.arange(NF)
off_s = np.array([np.median(off[max(0, i - 6):i + 7]) for i in range(NF)])              # a steady offset, no jitter
off_s = np.convolve(np.pad(off_s, 6, mode='edge'), np.ones(13) / 13, mode='valid')
KMAP = [min(NW - 1, max(0, int(round(i + off_s[i])))) for i in range(NF)]
for i in range(1, NF): KMAP[i] = max(KMAP[i], KMAP[i - 1])                                  # never backwards
TAIL = list(range(KMAP[-1] + 1, NW))                                                        # after the footage: the rest of the path
if os.environ.get('KMAPJSON'):        # the wire layer was rendered to follow the footage exactly: frame i goes with frame i
    import json as _j
    _km = _j.load(open(os.environ['KMAPJSON']))
    SHK = [min(NS - 1, int(round(v))) for v in _km[:NF]]
    KMAP = list(range(NF)); TAIL = list(range(NF, NW))
else:
    SHK = KMAP
print('3D offset per footage frame, start/mid/end:', round(off_s[0], 1), round(off_s[NF // 2], 1), round(off_s[-1], 1), '| tail frames', len(TAIL))

# ---- alignment at footage size: footage i -> its matching shaded frame ----
def edges(im, s=0.25):
    x = cv2.cvtColor(cv2.resize(im, (int(W0 * s), int(H0 * s)), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
    x = cv2.GaussianBlur(x, (5, 5), 0); x = np.abs(cv2.Laplacian(x, cv2.CV_32F, ksize=3)); return cv2.GaussianBlur(x, (5, 5), 0)
S = np.diag([0.25, 0.25, 1]).astype(np.float32); Si = np.linalg.inv(S)
Hs = {}; w = np.eye(3, dtype=np.float32)
for i in range(NF):
    shp = os.path.join(sdir, f'f{min(SHK[i], NS - 1):04d}.png')
    if not os.path.exists(shp): continue
    sh = cv2.resize(cv2.imread(shp), (W0, H0), interpolation=cv2.INTER_AREA)
    try:
        cc, w2 = cv2.findTransformECC(edges(real[i]), edges(sh), w.copy(), cv2.MOTION_HOMOGRAPHY, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)
        if cc > 0.4: w = w2
    except cv2.error: pass
    Hs[i] = Si @ w @ S
keys = sorted(Hs); Hsm = {}
for i in keys:
    nb = [Hs[j] / Hs[j][2, 2] for j in keys if abs(j - i) <= 2]; Hsm[i] = np.mean(nb, axis=0)
# the last aligned warp eases back to identity over the frames after the footage, so the wire layer never jumps
last = Hsm[keys[-1]] if keys else np.eye(3)
Sc = np.diag([W / W0, H / H0, 1]).astype(np.float64); Sci = np.linalg.inv(Sc)
print('aligned', len(Hsm))

# ---- the sweep ----
ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
if MODE.startswith('radial'):
    cx, cy = (float(v) for v in MODE.split(':')[1].split(','))
    dd = np.sqrt(((xs / W - cx) * (W / H)) ** 2 + (ys / H - cy) ** 2)
    u = dd / dd.max()                                    # 0 at the burst point -> 1 at the farthest corner
else:
    u = xs / W * 0.86 + (1 - ys / H) * 0.14              # position along the sweep (left -> right, a little upward)
rng = np.random.default_rng(11)
grain = rng.random((H, W), dtype=np.float32)
ragged = cv2.GaussianBlur(rng.random((H, W), dtype=np.float32), (0, 0), H / 25); ragged = (ragged - ragged.mean()) / (ragged.std() + 1e-6)
def sm(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
BAND = 0.08
BG = np.array([8, 6, 3], np.float32)                     # #030608 in BGR
DOT = np.array([255, 242, 232], np.float32)              # cool white

with tempfile.TemporaryDirectory() as tmp:
    for i in range(NF + len(TAIL)):
        kw = KMAP[i] if i < NF else TAIL[i - NF]
        wire = cv2.imread(wires[kw]); wire = cv2.resize(wire, (W, H), interpolation=cv2.INTER_AREA) if wire.shape[:2] != (H, W) else wire
        if i < NF and i in Hsm: Hm = Sc @ Hsm[i] @ Sci
        elif i >= NF: k = min(1, (i - NF + 1) / 18); k = k * k * (3 - 2 * k); Hm = Sc @ (last * (1 - k) + np.eye(3) * k) @ Sci
        else: Hm = np.eye(3)
        wire = cv2.warpPerspective(wire, Hm, (W, H), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, borderValue=tuple(int(c) for c in BG)).astype(np.float32)
        glow = np.clip(wire - BG, 0, 255)
        if i >= NF:
            o = wire
        else:
            f = cv2.resize(real[i], (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
            t = sm((i - T0) / max(1, T1 - T0))
            if i < T0:
                o = f
            else:
                X = (-0.06 + 1.2 * t) if MODE.startswith('radial') else (-0.2 + 1.45 * t)   # where the front is
                fr = (X - u) + ragged * (0.022 if MODE.startswith('radial') else 0.008)   # a slightly ragged front, less of a perfect circle                         # > 0 behind the front
                behind = sm(fr / BAND)                                # 0 ahead .. 1 well behind
                band = np.exp(-((fr - BAND * 0.25) / (BAND * 0.45)) ** 2)   # the bright band at the front
                ahead_spray = np.exp(-((fr + BAND * 0.6) / (BAND * 0.5)) ** 2) # a few dots fly ahead of it
                dark = f * (1 - behind[..., None] * 0.96) + BG * behind[..., None] * 0.96   # the photo sinks to near-black behind
                dark *= (1 - 0.25 * t)                                                  # the whole picture dims as it goes
                dots = (grain < 0.045 * band + 0.008 * ahead_spray).astype(np.float32)   # a light ring of dots, not a wall of snow (user, 2026-11-06)
                dots = cv2.GaussianBlur(dots, (0, 0), max(0.7, H / 1600)) * 2.6           # soft little points of light
                dots += (grain > 1 - 0.35 * band).astype(np.float32) * 0.0                # (reserved)
                lines = glow * (behind[..., None] * 1.0 + band[..., None] * 1.1)   # the lines flare as the band passes, then settle
                base = dark
                o = 255 - (255 - base) * (255 - np.clip(lines + DOT * np.clip(dots, 0, 1)[..., None], 0, 255)) / 255
        cv2.imwrite(os.path.join(tmp, f'f{i:04d}.png'), np.clip(o, 0, 255).astype(np.uint8))
        if i % 24 == 0: print('frame', i)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24', '-i', os.path.join(tmp, 'f%04d.png'), '-c:v', 'libx264', '-preset', 'slow', '-crf', '12', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], check=True)
print('done', out)
