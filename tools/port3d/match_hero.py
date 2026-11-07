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
al = cv2.warpAffine(F[m], A[:2].astype(np.float32), (W, H), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
lab = lambda x: cv2.cvtColor(x, cv2.COLOR_BGR2LAB).astype(np.float32)
# a tone curve per channel that turns the clip's meeting frame into the hero's colours (keeps blacks black)
def curve(src_ch, ref_ch):
    hs = np.bincount(src_ch.ravel(), minlength=256).astype(np.float64); hr = np.bincount(ref_ch.ravel(), minlength=256).astype(np.float64)
    cs = np.cumsum(hs) / hs.sum(); cr = np.cumsum(hr) / hr.sum()
    lut = np.interp(cs, cr, np.arange(256)); lut[0] = 0
    k = np.exp(-0.5 * (np.arange(-8, 9) / 3.0) ** 2); k /= k.sum()
    lut = np.convolve(np.pad(lut, 8, mode='edge'), k, mode='valid')          # smooth curve, no banding
    return np.clip(np.maximum.accumulate(lut), 0, 255).astype(np.float32)
Lh, Lf = lab(hero), lab(al)
mh, sh = Lh.reshape(-1, 3).mean(0), Lh.reshape(-1, 3).std(0); mf, sf = Lf.reshape(-1, 3).mean(0), Lf.reshape(-1, 3).std(0)
LUT = [curve(al[..., c], hero[..., c]) for c in range(3)]
# GRADE=hold,fade: the colour curve is on in full until frame 'hold', then eases off by frame 'fade' ('all' = whole clip)
import os
G = os.environ.get('GRADE', ''); BL = int(os.environ.get('BLEND', '0'))
# KEEP=1: the meeting frame stays the clip's own frame (graded and placed onto the hero), so a held still can be cut FROM the clip
# HOLDOUT=<png>: save that meeting frame; FLOWBLEND=n: land on the hero over n frames with the hero warped to each frame's motion (no ghosting)
KEEP = os.environ.get('KEEP') == '1'; HOLDOUT = os.environ.get('HOLDOUT', ''); FB = int(os.environ.get('FLOWBLEND', '0'))
dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
DENSE = os.environ.get('DENSE') == '1'; RES = None   # DENSE=1: ease the frame onto the hero with a per-pixel flow field instead of one affine shift
def flow_to_hero(f):   # field fl with hero(x) ~ f(x + fl(x)): remap(f, x + k*fl) moves f a fraction k of the way onto the hero
    sc = 0.5 if W >= 3000 else 1.0
    a, b = [cv2.cvtColor(cv2.resize(x, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY) for x in (hero, f)]
    fl = dis.calc(a, b, None)
    if sc != 1: fl = cv2.resize(fl, (W, H)) / sc
    return cv2.GaussianBlur(fl, (0, 0), 3)
def hero_onto(f):   # the hero, moved by optical flow so it lines up with frame f pixel for pixel
    sc = 0.5 if W >= 3000 else 1.0
    a, b = [cv2.cvtColor(cv2.resize(x, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY) for x in (f, hero)]
    fl = dis.calc(a, b, None)
    if sc != 1: fl = cv2.resize(fl, (W, H)) / sc
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    return cv2.remap(hero, xx + fl[..., 0], yy + fl[..., 1], cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
def grade_k(i):
    if not G: return None
    if G == 'all': return 1.0
    h, f = (int(v) for v in G.split(','))
    if i <= h: return 1.0
    x = min(1.0, (i - h) / max(1, f - h)); return 1 - x * x * (3 - 2 * x)
def grade(f, k):
    g = np.stack([LUT[c][f[..., c]] for c in range(3)], -1)
    return np.clip(f.astype(np.float32) * (1 - k) + g * k, 0, 255).astype(np.uint8)
print(f'{src}: ecc {cc:.2f}, shift {A[0,2]:+.1f},{A[1,2]:+.1f}px, scale {np.sqrt(abs(np.linalg.det(A[:2,:2]))):.4f}, Lab mean {mf.round(1)} -> {mh.round(1)}')
def fix(f, k):
    if k <= 0: return f
    Ak = np.eye(3) * (1 - k) + A * k
    g = cv2.warpAffine(f, Ak[:2].astype(np.float32), (W, H), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
    L = lab(g); L2 = (L - mf) / (sf + 1e-6) * sh + mh
    L = L * (1 - k) + L2 * k
    return cv2.cvtColor(np.clip(L, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '24', '-i', '-', '-an', '-c:v', 'libx264', '-preset', 'slow',
                      '-crf', CRF, '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
for i, f in enumerate(F):
    dist = i if where == 'start' else N - 1 - i
    x = max(0.0, 1 - dist / R); k = x * x * (3 - 2 * x)
    gk = grade_k(i)
    if dist == 0 and not KEEP: f = hero.copy()          # the meeting frame IS the hero frame
    elif gk is not None:
        f = grade(f, gk)                                # colour: the hero's grade (curve) instead of the Lab nudge
        if k > 0 and DENSE:                             # only the leftover mismatch at the meeting frame eases out; the camera keeps its own speed
            if RES is None: RES = flow_to_hero(grade(F[m], 1.0) if G else F[m])
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            f = cv2.remap(f, xx + RES[..., 0] * k, yy + RES[..., 1] * k, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        elif k > 0:                                     # position: still eased onto the hero near the meeting frame
            Ak = np.eye(3) * (1 - k) + A * k
            f = cv2.warpAffine(f, Ak[:2].astype(np.float32), (W, H), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
    else: f = fix(f, k)
    if 0 < dist < FB:                                   # flow-matched landing: no double image, no soft frames
        x = 1 - dist / FB; b = x * x * (3 - 2 * x)
        f = np.clip(f.astype(np.float32) * (1 - b) + hero_onto(f).astype(np.float32) * b, 0, 255).astype(np.uint8)
    if dist == 0 and HOLDOUT: cv2.imwrite(HOLDOUT, f)
    if 0 < dist < BL:                                   # BLEND=n: dissolve onto the hero over the last n frames (sharp footage shows small texture differences)
        x = 1 - dist / BL; b = x * x * (3 - 2 * x)
        f = np.clip(f.astype(np.float32) * (1 - b) + hero.astype(np.float32) * b, 0, 255).astype(np.uint8)
    p.stdin.write(f.tobytes())
p.stdin.close(); p.wait()
