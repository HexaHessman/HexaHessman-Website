"""Make a clip meet the held hero frame exactly: same position, same colours.

At the meeting frame (first frame for a button clip, last frame for the intro) we measure the small shift/scale (ECC
affine on edges) and the colour difference (per-channel mean and spread in Lab) against the hero. Those corrections are
applied fully at the meeting frame and eased out over R frames, so the clip lands on / leaves from the hero with no jump.
Usage: python match_hero.py <in.mp4> <hero.png> <out.mp4> <start|end> [R=24] [crf=21]
"""
import sys, subprocess, numpy as np, cv2
src, heroP, out, where = sys.argv[1:5]; R = int(sys.argv[5]) if len(sys.argv) > 5 else 24; CRF = sys.argv[6] if len(sys.argv) > 6 else '21'
cap = cv2.VideoCapture(src); F = []
while True:
    ok, f = cap.read()
    if not ok: break
    F.append(f)
H, W = F[0].shape[:2]; N = len(F)
hero = cv2.resize(cv2.imread(heroP), (W, H), interpolation=cv2.INTER_AREA)
m = 0 if where == 'start' else N - 1
def edges(im):
    x = cv2.cvtColor(cv2.resize(im, (480, 270), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32); x = cv2.GaussianBlur(x, (5, 5), 0)
    x = np.abs(cv2.Laplacian(x, cv2.CV_32F, ksize=3)); return cv2.GaussianBlur(x, (5, 5), 0)
w = np.eye(2, 3, dtype=np.float32)
try: cc, w = cv2.findTransformECC(edges(hero), edges(F[m]), w, cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)
except cv2.error: cc = 0
A = np.vstack([w, [0, 0, 1]]).astype(np.float64); S = np.diag([480 / W, 270 / H, 1]); A = np.linalg.inv(S) @ A @ S   # hero coords -> clip coords, full size
# colour: Lab statistics of the clip's meeting frame (after alignment) vs the hero
al = cv2.warpAffine(F[m], A[:2].astype(np.float32), (W, H), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
lab = lambda x: cv2.cvtColor(x, cv2.COLOR_BGR2LAB).astype(np.float32)
Lh, Lf = lab(hero), lab(al)
mh, sh = Lh.reshape(-1, 3).mean(0), Lh.reshape(-1, 3).std(0); mf, sf = Lf.reshape(-1, 3).mean(0), Lf.reshape(-1, 3).std(0)
print(f'{src}: ecc {cc:.2f}, shift {A[0,2]:+.1f},{A[1,2]:+.1f}px, scale {np.sqrt(abs(np.linalg.det(A[:2,:2]))):.4f}, Lab mean {mf.round(1)} -> {mh.round(1)}')
def fix(f, k):
    if k <= 0: return f
    Ak = np.eye(3) * (1 - k) + A * k
    g = cv2.warpAffine(f, Ak[:2].astype(np.float32), (W, H), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
    L = lab(g); L2 = (L - mf) / (sf + 1e-6) * sh + mh
    L = L * (1 - k) + L2 * k
    return cv2.cvtColor(np.clip(L, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '24', '-i', '-', '-an', '-c:v', 'libx264', '-preset', 'slow',
                      '-crf', CRF, '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
for i, f in enumerate(F):
    dist = i if where == 'start' else N - 1 - i
    x = max(0.0, 1 - dist / R); k = x * x * (3 - 2 * x)
    if dist == 0: f = hero.copy()                       # the meeting frame IS the hero frame
    else: f = fix(f, k)
    p.stdin.write(f.tobytes())
p.stdin.close(); p.wait()
