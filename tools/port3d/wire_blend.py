# Real footage -> Terminal-style wireframe, mid-zoom.
# For each footage frame i the matching 3D frame is k = round(i*(N3-1)/(N-1)) (Seedance follows our timing exactly).
# Inside the transition window the wireframe frame k is warped by the homography that maps the 3D shaded frame k onto
# footage frame i (ECC on edge maps, smoothed over time), so the glowing lines sit on the real ship. Blend:
# lines draw on over the footage (screen) first, then the footage sinks into the background green, then pure wireframe.
# Usage: venv/bin/python wire_blend.py <footage.mp4> <shaded_dir> <shaded_prefix> <wire_dir> <wire_prefix> <t0> <t1> <out.mp4>
import sys, os, subprocess, tempfile
import numpy as np, cv2

src, sdir, spre, wdir, wpre, T0, T1, out = sys.argv[1:9]; T0, T1 = int(T0), int(T1)
BG = np.array([0x0e, 0x14, 0x07], np.float32)          # #07140e in BGR
cap = cv2.VideoCapture(src); real = []
while True:
    ok, f = cap.read()
    if not ok: break
    real.append(f)
N = len(real); H, W = real[0].shape[:2]
N3 = len([f for f in os.listdir(wdir) if f.startswith(wpre)])
kof = lambda i: min(N3 - 1, int(round(i * (N3 - 1) / (N - 1))))

def edges(im, s=0.25):
    x = cv2.cvtColor(cv2.resize(im, (int(W * s), int(H * s)), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
    x = cv2.GaussianBlur(x, (5, 5), 0); x = np.abs(cv2.Laplacian(x, cv2.CV_32F, ksize=3)); return cv2.GaussianBlur(x, (5, 5), 0)
S = np.diag([0.25, 0.25, 1]).astype(np.float32); Si = np.linalg.inv(S)
lo, hi = max(0, T0 - 8), min(N - 1, T1 + 8)
Hs = {}; w = np.eye(3, dtype=np.float32)
for i in range(lo, hi + 1):
    sh = cv2.imread(os.path.join(sdir, f'{spre}{kof(i):04d}.jpg'))
    try:
        cc, w2 = cv2.findTransformECC(edges(real[i]), edges(sh), S @ w @ Si if False else w.copy(), cv2.MOTION_HOMOGRAPHY,
                                      (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)
        if cc > 0.45: w = w2
    except cv2.error: pass
    Hs[i] = Si @ w @ S        # full-res: maps footage coords -> 3D coords (used with WARP_INVERSE_MAP)
# temporal smoothing of the homographies (5-frame window)
keys = sorted(Hs); Hsm = {}
for i in keys:
    nb = [Hs[j] / Hs[j][2, 2] for j in keys if abs(j - i) <= 2]; Hsm[i] = np.mean(nb, axis=0)

def ease(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
with tempfile.TemporaryDirectory() as tmp:
    for i in range(N):
        f = real[i].astype(np.float32)
        if i < T0: o = f
        else:
            k = kof(i); wire = cv2.imread(os.path.join(wdir, f'{wpre}{k:04d}.jpg'))
            if i <= T1 + 8 and i in Hsm:
                wire = cv2.warpPerspective(wire, Hsm[i], (W, H), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, borderValue=tuple(int(c) for c in BG))
            wire = wire.astype(np.float32)
            t = (i - T0) / max(1, T1 - T0)
            lines = ease(t / 0.55)                         # outlines draw on first
            sink = ease((t - 0.25) / 0.75)                 # then the footage sinks into the green
            base = f * (1 - sink) + BG * sink
            glow = np.clip(wire - BG, 0, 255) * lines      # only the bright line/dot part of the wireframe
            o = 255 - (255 - base) * (255 - glow) / 255    # screen blend
            if i > T1: o = wire
        cv2.imwrite(os.path.join(tmp, f'f{i:04d}.png'), np.clip(o, 0, 255).astype(np.uint8))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24', '-i', os.path.join(tmp, 'f%04d.png'), '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], check=True)
print('done', out, N, 'frames, transition', T0, '->', T1)
