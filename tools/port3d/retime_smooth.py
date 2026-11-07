"""Smooth a clip's speed without changing where it starts and ends, and move its path map the same way.

The AI footage speeds up and slows down a little from frame to frame. We measure its motion, blur that speed curve
(sigma frames) and re-sample the footage along the smoothed curve (in-between frames by optical flow). The path map
(which 3D position each footage frame shows, from make_kmap.py) is re-sampled at the same source times, so a line
layer rendered from the new map still sits exactly on the footage.
Usage: python retime_smooth.py <footage.mp4> <kmap.json> <out.mp4> <out_kmap.json> [sigma=6]
"""
import sys, os, json, subprocess, tempfile, numpy as np, cv2
src, kin, out, kout = sys.argv[1:5]; SIG = float(sys.argv[5]) if len(sys.argv) > 5 else 6
cap = cv2.VideoCapture(src); F = []
while True:
    ok, f = cap.read()
    if not ok: break
    F.append(f)
N = len(F); km = json.load(open(kin)); tail = km[N:]
g = lambda x: cv2.cvtColor(cv2.resize(x, (480, 270), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
G = [g(f) for f in F]
d = np.array([1e-3] + [float(np.abs(G[i] - G[i - 1]).mean()) + 1e-3 for i in range(1, N)])   # motion into frame i
C = np.cumsum(d); C -= C[0]
k = np.arange(-int(4 * SIG), int(4 * SIG) + 1); w = np.exp(-0.5 * (k / SIG) ** 2); w /= w.sum()
vs = np.convolve(np.pad(d, len(k) // 2, mode='edge'), w, mode='valid')
D = np.cumsum(vs); D -= D[0]; D *= C[-1] / D[-1]                     # same total motion, smooth speed
s = np.interp(D, C, np.arange(N, dtype=np.float64))                    # source time for each output frame
s[0], s[-1] = 0, N - 1
dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
def at(t):
    i = int(np.floor(t)); a = np.float32(t - i)
    if a < 1e-3 or i >= N - 1: return F[min(i, N - 1)]
    A, B = F[i], F[i + 1]
    ga, gb = cv2.cvtColor(A, cv2.COLOR_BGR2GRAY), cv2.cvtColor(B, cv2.COLOR_BGR2GRAY)
    sc = 0.5 if A.shape[1] >= 3000 else 1.0   # flow at half size on 4K, scaled back up
    if sc != 1: ga, gb = [cv2.resize(x, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA) for x in (ga, gb)]
    fab = dis.calc(ga, gb, None); fba = dis.calc(gb, ga, None)
    if sc != 1: fab = cv2.resize(fab, (A.shape[1], A.shape[0])) / sc; fba = cv2.resize(fba, (A.shape[1], A.shape[0])) / sc
    ga = ga if sc == 1 else cv2.resize(ga, (A.shape[1], A.shape[0]))
    H, W = ga.shape; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    if a <= 0.5: return cv2.remap(A, xx + fba[..., 0] * a, yy + fba[..., 1] * a, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)   # nearer frame only
    return cv2.remap(B, xx + fab[..., 0] * (1 - a), yy + fab[..., 1] * (1 - a), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
with tempfile.TemporaryDirectory() as tmp:
    for j, t in enumerate(s): cv2.imwrite(os.path.join(tmp, f'f{j:04d}.png'), at(t))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24', '-i', os.path.join(tmp, 'f%04d.png'), '-c:v', 'libx264', '-crf', '10', '-pix_fmt', 'yuv420p', out], check=True)
kmn = list(np.interp(s, np.arange(N), km[:N]))
for i in range(1, len(kmn)): kmn[i] = max(kmn[i], kmn[i - 1] + 0.05)
json.dump([float(v) for v in kmn] + tail, open(kout, 'w'))
print('frames', N, '| speed before: max jump', round(float((d[1:] / vs[1:]).max()), 2), '| after: smooth | map', len(kmn) + len(tail))
