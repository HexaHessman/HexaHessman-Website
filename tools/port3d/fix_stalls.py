# The AI clip stalls for a frame (a repeat) and catches up later with a double step. Take the repeat out and put an
# optical-flow in-between into the double step: same frame count, same overall timing, even motion.
import sys, numpy as np, cv2, subprocess, tempfile, os
src, out = sys.argv[1], sys.argv[2]
cap = cv2.VideoCapture(src); F = []
while True:
    ok, f = cap.read()
    if not ok: break
    F.append(f)
g = lambda x: cv2.cvtColor(cv2.resize(x, (480, 270), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
def mid(a, b):
    ga, gb = [cv2.cvtColor(x, cv2.COLOR_BGR2GRAY) for x in (a, b)]
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    fab = dis.calc(ga, gb, None); fba = dis.calc(gb, ga, None)
    H, W = ga.shape; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    wa = cv2.remap(a, xx + fba[..., 0] * 0.5, yy + fba[..., 1] * 0.5, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    wb = cv2.remap(b, xx + fab[..., 0] * 0.5, yy + fab[..., 1] * 0.5, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return cv2.addWeighted(wa, 0.5, wb, 0.5, 0)
for _ in range(8):
    d = np.array([np.abs(g(F[i]) - g(F[i - 1])).mean() for i in range(1, len(F))])   # d[i-1] = motion into frame i
    loc = lambda i: np.median(d[max(0, i - 8):i + 8])
    stalls = [i for i in range(1, len(F)) if d[i - 1] < 0.3 * loc(i - 1)]
    if not stalls: break
    s = stalls[0]
    jumps = [j for j in range(s + 2, min(len(F), s + 30)) if d[j - 1] > 1.4 * loc(j - 1)]
    before = [j for j in range(max(1, s - 12), s) if d[j - 1] > 1.4 * loc(j - 1)]   # a double step just before the stall
    if jumps and (not before or jumps[0] - s <= s - before[-1]):
        j = jumps[0]
        F = F[:s] + F[s + 1:j] + [mid(F[j - 1], F[j])] + F[j:]
        print(f'stall {s} out, in-between added before {j}')
    elif before:
        j = before[-1]
        F = F[:j] + [mid(F[j - 1], F[j])] + F[j:s] + F[s + 1:]
        print(f'in-between added before {j}, stall {s} out')
    else:
        F[s] = mid(F[s - 1], F[s + 1]); print(f'stall {s} filled in place (no catch-up after it)')
with tempfile.TemporaryDirectory() as tmp:
    for i, f in enumerate(F): cv2.imwrite(os.path.join(tmp, f'f{i:04d}.png'), f)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24', '-i', os.path.join(tmp, 'f%04d.png'), '-c:v', 'libx264', '-crf', '10', '-pix_fmt', 'yuv420p', out], check=True)
print('frames', len(F))
