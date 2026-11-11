"""Re-time a clip with a speed curve over its own time, with smooth in-between frames (optical flow).

From the first frame the camera eases up to full speed over RAMP seconds, glides at an even speed up to source second
END (the AI footage's own speed wobbles are evened out), then the clip plays on at its own pace. The first frame is unchanged, so the clip still starts exactly on the held hero frame.
Made for the homepage Commodities door (2026-11-11, user: the start was slow, the wireframe should spread fast).
Usage: python speed_curve.py <in.mp4> <out.mp4> [RAMP=0.7] [END=4.0]
"""
import sys, os, subprocess, tempfile, numpy as np, cv2
src, out = sys.argv[1:3]
RAMP = float(sys.argv[3]) if len(sys.argv) > 3 else 0.7
END = float(sys.argv[4]) if len(sys.argv) > 4 else 4.0
cap = cv2.VideoCapture(src); FPS = cap.get(cv2.CAP_PROP_FPS) or 24; F = []
while True:
    ok, f = cap.read()
    if not ok: break
    F.append(f)
N = len(F)

# 1. the camera's own motion per frame (median optical flow), and how far it has travelled by each frame
dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
g = lambda x: cv2.cvtColor(cv2.resize(x, (640, 360), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
G = [g(f) for f in F]
m = np.array([0.0] + [float(np.median(np.linalg.norm(dis.calc(G[i - 1], G[i], None), axis=2))) for i in range(1, N)])
M = np.cumsum(m)
# 2. the new pace: from the held frame the camera eases up to full speed over RAMP seconds (smoothstep, no kick),
# glides at that speed until source second END, then the clip plays on at its own pace. Full speed = the camera's own
# speed at END, so the hand-over is seamless.
e = int(round(END * FPS)); vmax = float(np.mean(m[max(1, e - 4): e + 5]))
ramp_n = RAMP * FPS; ramp_dist = vmax * ramp_n / 2
if ramp_dist > M[e]: ramp_n = 2 * M[e] / vmax; ramp_dist = M[e]
glide_n = (M[e] - ramp_dist) / vmax
def dist(j):   # distance travelled by output frame j
    if j <= ramp_n: x = j / ramp_n; return vmax * ramp_n * (x ** 3 - x ** 4 / 2)   # integral of smoothstep
    return ramp_dist + vmax * (j - ramp_n)
n_a = int(np.ceil(ramp_n + glide_n))
s = [float(np.interp(dist(j), M, np.arange(N))) for j in range(n_a)]
s += list(np.arange(e + (n_a - ramp_n - glide_n), N - 1, 1.0)) + [N - 1]
s = np.maximum.accumulate(np.array(s)); s[0] = 0

def at(t):
    i = int(np.floor(t)); a = np.float32(t - i)
    if a < 1e-3 or i >= N - 1: return F[min(i, N - 1)]
    if a > 1 - 1e-3: return F[i + 1]
    P, Q = F[i], F[i + 1]
    gp, gq = cv2.cvtColor(P, cv2.COLOR_BGR2GRAY), cv2.cvtColor(Q, cv2.COLOR_BGR2GRAY)
    sc = 0.5 if P.shape[1] >= 3000 else 1.0
    if sc != 1: gp, gq = [cv2.resize(x, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA) for x in (gp, gq)]
    fpq = dis.calc(gp, gq, None); fqp = dis.calc(gq, gp, None)
    if sc != 1: fpq = cv2.resize(fpq, (P.shape[1], P.shape[0])) / sc; fqp = cv2.resize(fqp, (P.shape[1], P.shape[0])) / sc
    H, W = P.shape[:2]; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    if a <= 0.5: return cv2.remap(P, xx + fqp[..., 0] * a, yy + fqp[..., 1] * a, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return cv2.remap(Q, xx + fpq[..., 0] * (1 - a), yy + fpq[..., 1] * (1 - a), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
with tempfile.TemporaryDirectory() as tmp:
    for j, t in enumerate(s): cv2.imwrite(os.path.join(tmp, f'f{j:04d}.png'), at(t))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(tmp, 'f%04d.png'),
                    '-c:v', 'libx264', '-qp', '0', '-preset', 'veryfast', '-pix_fmt', 'yuv444p', out], check=True)
print(f'{N} frames ({N / FPS:.2f} s) -> {len(s)} frames ({len(s) / FPS:.2f} s)')
