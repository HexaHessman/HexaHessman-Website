# For each footage frame: which 3D frame matches it best (timing), and how well (ECC cc), plus the warp's scale/shift.
import sys, os, numpy as np, cv2
src, sdir = sys.argv[1], sys.argv[2]
cap = cv2.VideoCapture(src); F = []
while True:
    ok, f = cap.read()
    if not ok: break
    F.append(cv2.resize(f, (480, 270), interpolation=cv2.INTER_AREA))
def edges(im):
    x = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32); x = cv2.GaussianBlur(x, (5, 5), 0)
    x = np.abs(cv2.Laplacian(x, cv2.CV_32F, ksize=3)); x = cv2.GaussianBlur(x, (5, 5), 0); return (x - x.mean()) / (x.std() + 1e-6)
SH = [edges(cv2.resize(cv2.imread(os.path.join(sdir, f'f{k:04d}.png')), (480, 270), interpolation=cv2.INTER_AREA)) for k in range(120)]
best = []
for i, f in enumerate(F[:120]):
    e = edges(f); sc = [float((e * SH[k]).mean()) for k in range(max(0, i - 30), min(120, i + 31))]
    k = int(np.argmax(sc)) + max(0, i - 30); best.append(k)
    w = np.eye(3, dtype=np.float32)
    try: cc, w = cv2.findTransformECC(e, SH[i], w, cv2.MOTION_HOMOGRAPHY, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 1e-5), None, 5)
    except cv2.error: cc = -1
    if i % 8 == 0: print(f'footage {i:3d} best 3D frame {k:3d} (offset {k - i:+d})  ecc(same i) {cc:.2f}  scale {np.sqrt(abs(np.linalg.det(w[:2,:2]))):.3f}  shift {w[0,2]:+.1f},{w[1,2]:+.1f}px@480')
