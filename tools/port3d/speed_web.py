"""Shorten a clip to a target length by squeezing its slow parts most, then write the web versions.

Speed is re-shaped by the clip's own motion: each source frame gets a weight w = floor + motion, so stretches with little
motion (holds, slow drifts) are passed through quickly while fast parts keep close to their own pace. Frames are taken
at the new positions (nearest frame, so nothing is blended soft). Options:
  --reverse        play the clip backwards first (a pull-back becomes a fly-in)
  --lead IMG N     the first N frames ease in from IMG (the held hero frame), so the cut from the still is invisible
  --tail IMG N     the last N frames ease onto IMG (so a fly-in ends exactly on the held frame)
Writes <out>.mp4 (1920 wide) and <out>-m.mp4 (1280 wide), plus <out>-4k.mp4 if the source is 4K.
Usage: python speed_web.py <in.mp4> <seconds> <out_base> [--floor 0.45] [--reverse] [--lead img N] [--tail img N]
"""
import sys, subprocess, numpy as np, cv2

args = sys.argv[1:]
src, secs, out = args[0], float(args[1]), args[2]
opt = lambda k, n=1: (args[args.index(k) + 1: args.index(k) + 1 + n] if k in args else None)
FLOOR = float((opt('--floor') or ['0.45'])[0]); REV = '--reverse' in args
lead = opt('--lead', 2); tail = opt('--tail', 2)

cap = cv2.VideoCapture(src); F = []
while True:
    ok, f = cap.read()
    if not ok: break
    F.append(f)
if REV: F = F[::-1]
H0, W0 = F[0].shape[:2]; N = len(F)
g = lambda x: cv2.cvtColor(cv2.resize(x, (480, 270), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
G = [g(f) for f in F]
d = np.array([0.0] + [float(np.abs(G[i] - G[i - 1]).mean()) for i in range(1, N)])
k = np.arange(-6, 7); ker = np.exp(-0.5 * (k / 2.5) ** 2); ker /= ker.sum()
d = np.convolve(np.pad(d, 6, mode='edge'), ker, mode='valid')          # no jitter in the speed curve
w = FLOOR * d.mean() + d
# --head N0 N1 F: source frames before N0 play F times faster (easing back to normal by N1); the rest keeps its pace
head = opt('--head', 3)
if head:
    n0, n1, fac = int(head[0]), int(head[1]), float(head[2])
    x = np.clip((np.arange(N) - n0) / max(1, n1 - n0), 0, 1); x = x * x * (3 - 2 * x)
    r = np.clip(np.arange(N) / 14.0, 0, 1); r = r * r * (3 - 2 * r)          # the speed-up itself eases in over the first 14 source frames
    m = 1 / fac + (1 - 1 / fac) * x; m = 1 - (1 - m) * r
    Cold = np.sum(w[1:]); w = w * m; secs = secs * np.sum(w[1:]) / Cold
C = np.concatenate([[0], np.cumsum(w[1:])])
M = int(round(secs * 24))
s = np.interp(np.linspace(0, C[-1], M), C, np.arange(N, dtype=np.float64))
idx = [int(round(v)) for v in s]
# in-between frames by optical flow at the exact new positions (no frame skipping, no blending soft)
dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
SC = 0.5 if W0 >= 3000 else 1.0                       # flow at half size on 4K, scaled back up
def at(t):
    i = int(np.floor(t)); a = np.float32(t - i)
    if a < 0.02 or i >= N - 1: return F[min(i, N - 1)]
    if a > 0.98: return F[i + 1]
    A, B = F[i], F[i + 1]
    sa, sb = [cv2.cvtColor(cv2.resize(x, None, fx=SC, fy=SC, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY) for x in (A, B)]
    fab = dis.calc(sa, sb, None); fba = dis.calc(sb, sa, None)
    if SC != 1: fab = cv2.resize(fab, (W0, H0)) / SC; fba = cv2.resize(fba, (W0, H0)) / SC
    yy, xx = np.mgrid[0:H0, 0:W0].astype(np.float32)
    # warp only the nearer real frame (a 50/50 blend of two frames smears detail); cubic keeps edges crisp
    if a <= 0.5: return cv2.remap(A, xx + fba[..., 0] * a, yy + fba[..., 1] * a, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return cv2.remap(B, xx + fab[..., 0] * (1 - a), yy + fab[..., 1] * (1 - a), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
frames = [at(v) for v in s]

def ease(n, i): x = (i + 1) / n; return x * x * (3 - 2 * x)
if lead:
    im = cv2.resize(cv2.imread(lead[0]), (W0, H0), interpolation=cv2.INTER_AREA).astype(np.float32); n = int(lead[1])
    for i in range(min(n, len(frames))): a = ease(n, i); frames[i] = np.clip(im * (1 - a) + frames[i].astype(np.float32) * a, 0, 255).astype(np.uint8)
if tail:
    im = cv2.resize(cv2.imread(tail[0]), (W0, H0), interpolation=cv2.INTER_AREA).astype(np.float32); n = int(tail[1])
    for j in range(min(n, len(frames))):
        i = len(frames) - n + j; a = ease(n, j); frames[i] = np.clip(frames[i].astype(np.float32) * (1 - a) + im * a, 0, 255).astype(np.uint8)

def write(path, width, crf, extra=()):
    h = int(round(width * H0 / W0 / 2) * 2)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{width}x{h}', '-r', '24', '-i', '-',
                          '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), *extra, '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path], stdin=subprocess.PIPE)
    for f in frames: p.stdin.write(cv2.resize(f, (width, h), interpolation=cv2.INTER_AREA if width < W0 else cv2.INTER_CUBIC).tobytes())
    p.stdin.close(); p.wait()
write(out + '.mp4', 1920, 18)
write(out + '-m.mp4', 1280, 22)
if W0 >= 2560: write(out + '-hd.mp4', 2560, 19)
if W0 >= 3840: write(out + '-4k.mp4', 3840, 16)
cv2.imwrite(out + '-first.jpg', frames[0], [cv2.IMWRITE_JPEG_QUALITY, 93]); cv2.imwrite(out + '-last.jpg', frames[-1], [cv2.IMWRITE_JPEG_QUALITY, 93])
print(f'{src}: {N} frames -> {M} ({secs}s), source used {idx[0]}..{idx[-1]}')
