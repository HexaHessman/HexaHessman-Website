"""Real footage -> Terminal-style particles, as a sweep that spreads out from the thing we are zooming into.

The AI footage follows our 3D camera path, so footage frame i and 3D frame i are the same camera. Each wire frame is
still nudged onto its footage frame with a homography (ECC on edge maps, smoothed over time) so the glowing lines sit
exactly on the real containers.

Look, frame by frame:
  before T0      the "hero" state: the container stack and the quay containers already carry faint lines and drifting
                 dust (the client's reference), the rest is the real photo
  T0 -> T1       a front spreads out from the stack across the whole frame; where it passes, the real picture breaks
                 up into dust and sinks into the dark green while the lines and particles take over
  after T1       pure lines and particles (the wire frames), through the container and on
Usage: python particle_sweep.py <footage.mp4|-> <shaded_dir> <wire_dir> <out.mp4> <T0> <T1> [centres] [hero_out.jpg]
  footage '-' = no footage (wire only).  centres = where the sweep starts, "cx,cy;cx,cy" as fractions of the frame.
"""
import sys, os, subprocess, tempfile, glob
import numpy as np, cv2

src, sdir, wdir, out, T0, T1 = sys.argv[1:7]; T0, T1 = int(T0), int(T1)
# where the sweep starts: one or more points "cx,cy;cx,cy" as fractions of the frame (the stack, the quay containers)
CENTRES = [tuple(float(v) for v in c.split(',')) for c in (sys.argv[7] if len(sys.argv) > 7 else '0.5,0.5').split(';')]
HERO = sys.argv[8] if len(sys.argv) > 8 else ''
BG = np.array([0x0e, 0x14, 0x07], np.float32)          # #07140e, BGR

wires = sorted(glob.glob(os.path.join(wdir, 'f*.png'))); NW = len(wires)
real = []
if src != '-':
    cap = cv2.VideoCapture(src)
    while True:
        ok, f = cap.read()
        if not ok: break
        real.append(f)
NF = len(real)
H, W = (real[0].shape[:2] if NF else cv2.imread(wires[0]).shape[:2])
print('footage', NF, 'frames, wire', NW, 'frames, size', W, H)

# ---- alignment: footage frame i -> shaded frame i (edges at quarter scale), smoothed over 5 frames ----
def edges(im, s=0.25):
    x = cv2.cvtColor(cv2.resize(im, (int(W * s), int(H * s)), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
    x = cv2.GaussianBlur(x, (5, 5), 0); x = np.abs(cv2.Laplacian(x, cv2.CV_32F, ksize=3)); return cv2.GaussianBlur(x, (5, 5), 0)
S = np.diag([0.25, 0.25, 1]).astype(np.float32); Si = np.linalg.inv(S)
Hs = {}; w = np.eye(3, dtype=np.float32)
for i in range(NF):
    shp = os.path.join(sdir, f'f{i:04d}.png')
    if not os.path.exists(shp): continue
    sh = cv2.imread(shp); sh = cv2.resize(sh, (W, H), interpolation=cv2.INTER_AREA) if sh.shape[:2] != (H, W) else sh
    try:
        cc, w2 = cv2.findTransformECC(edges(real[i]), edges(sh), w.copy(), cv2.MOTION_HOMOGRAPHY, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)
        if cc > 0.4: w = w2
    except cv2.error: pass
    Hs[i] = Si @ w @ S
keys = sorted(Hs); Hsm = {}
for i in keys:
    nb = [Hs[j] / Hs[j][2, 2] for j in keys if abs(j - i) <= 2]; Hsm[i] = np.mean(nb, axis=0)
print('aligned', len(Hsm), 'frames')

# ---- the sweep ----
ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
d = np.min([np.sqrt(((xs / W - cx) * (W / H)) ** 2 + (ys / H - cy) ** 2) for cx, cy in CENTRES], axis=0)   # distance from the nearest start point, in frame heights
rng = np.random.default_rng(7)
noise = cv2.GaussianBlur(rng.random((H, W), dtype=np.float32), (0, 0), max(2, H / 90)); noise = (noise - noise.mean()) / (noise.std() + 1e-6)   # soft blobs, the ragged front
grain = rng.random((H, W), dtype=np.float32)                                                                                      # pixel dust
def smooth(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
R_HERO, R_END, BAND = 0.2, 1.6, 0.16

with tempfile.TemporaryDirectory() as tmp:
    for i in range(NW):
        wire = cv2.imread(wires[i])
        if wire.shape[:2] != (H, W): wire = cv2.resize(wire, (W, H), interpolation=cv2.INTER_AREA)
        if i in Hsm: wire = cv2.warpPerspective(wire, Hsm[i], (W, H), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, borderValue=tuple(int(c) for c in BG))
        wire = wire.astype(np.float32)
        glow = np.clip(wire - BG, 0, 255)
        t = smooth((i - T0) / max(1, T1 - T0))
        R = R_HERO + (R_END - R_HERO) * t
        front = d - R + noise * 0.05                           # <0 inside the swept area
        m_lines = smooth((BAND * 1.6 - front) / (BAND * 1.6))  # lines and dust lead the front
        m_sink = smooth((BAND * 0.5 - front) / BAND)           # the real picture goes a little later
        hero = i < T0 or t < 1e-6
        if hero: m_lines *= 0.8; m_sink *= 0.0   # hero state: faint lines and dust, nothing sinks yet
        if i < NF:
            f = real[i].astype(np.float32)
            edge = 0 * front if hero else np.exp(-((front / (BAND * 0.6)) ** 2))   # the band where the picture is breaking up
            dust = (grain < (0.16 * edge)).astype(np.float32)[..., None]       # a few pixels that have already flown off
            spark = (grain > 1 - 0.2 * edge).astype(np.float32)[..., None]     # many flare white as they go: the picture turns to bright dust
            base = f * (1 - m_sink[..., None]) * (1 - dust) + BG * (m_sink[..., None] + dust * (1 - m_sink[..., None]))
            glow = glow * (m_lines * (1 + 0.9 * edge))[..., None] + spark * 150
        else:
            base = np.broadcast_to(BG, (H, W, 3)).astype(np.float32)
        o = 255 - (255 - base) * (255 - glow) / 255          # screen blend
        o = np.clip(o, 0, 255).astype(np.uint8)
        cv2.imwrite(os.path.join(tmp, f'f{i:04d}.png'), o)
        if i == 0 and HERO: cv2.imwrite(HERO, o, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if i % 24 == 0: print('frame', i, 'R', round(R, 2))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24', '-i', os.path.join(tmp, 'f%04d.png'), '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], check=True)
print('done', out)
