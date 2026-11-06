"""Which (fractional) path position each footage frame shows, then the rest of the path one frame at a time.
Usage: python make_kmap.py <footage.mp4> <shaded_dir> <path_frames> <out.json>"""
import sys, os, json, numpy as np, cv2
src, sdir, NP, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
def edges(im):
    x = cv2.cvtColor(cv2.resize(im, (480, 270), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32); x = cv2.GaussianBlur(x, (5, 5), 0)
    x = np.abs(cv2.Laplacian(x, cv2.CV_32F, ksize=3)); x = cv2.GaussianBlur(x, (5, 5), 0); return (x - x.mean()) / (x.std() + 1e-6)
cap = cv2.VideoCapture(src); F = []
while True:
    ok, f = cap.read()
    if not ok: break
    F.append(edges(f))
NS = len([f for f in os.listdir(sdir) if f.endswith('.png')]); SH = [edges(cv2.imread(os.path.join(sdir, f'f{k:04d}.png'))) for k in range(NS)]
pos = []
for i, e in enumerate(F):
    lo, hi = max(0, i - 4), min(NS - 1, i + 10)
    sc = np.array([float((e * SH[k]).mean()) for k in range(lo, hi + 1)]); b = int(np.argmax(sc))
    if 0 < b < len(sc) - 1:      # parabola through the peak: a fractional position
        y0, y1, y2 = sc[b - 1], sc[b], sc[b + 1]; d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-9); b = b + max(-0.5, min(0.5, d))
    pos.append(lo + b)
off = np.array(pos) - np.arange(len(F))
off = np.array([np.median(off[max(0, i - 8):i + 9]) for i in range(len(F))])
off = np.convolve(np.pad(off, 10, mode='edge'), np.ones(21) / 21, mode='valid')      # a smooth, steady lead
km = [float(i + off[i]) for i in range(len(F))]
for i in range(1, len(km)): km[i] = max(km[i], km[i - 1] + 0.3)                       # always moving forward
step = 1.0; k = km[-1]
while k + step <= NP - 1: k += step; km.append(float(k))                              # the rest of the path, at the path's own pace
json.dump(km, open(out, 'w'))
print('frames', len(km), '(footage', len(F), ') lead start/mid/end', round(off[0], 2), round(off[len(off) // 2], 2), round(off[-1], 2))
