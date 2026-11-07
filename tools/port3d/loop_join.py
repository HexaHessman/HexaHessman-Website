import cv2, numpy as np, subprocess, sys
src, out, K = sys.argv[1], sys.argv[2], int(sys.argv[3])
cap = cv2.VideoCapture(src); F = []
while True:
    ok, f = cap.read()
    if not ok: break
    F.append(f)
N = len(F); L = N - K; h, w = F[0].shape[:2]
dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
S = 0.5
xx, yy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
def flow(a, b):
    ga = cv2.cvtColor(cv2.resize(a, None, fx=S, fy=S, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    gb = cv2.cvtColor(cv2.resize(b, None, fx=S, fy=S, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    f = dis.calc(ga, gb, None)
    f = cv2.GaussianBlur(f, (0, 0), 2)
    return cv2.resize(f, (w, h), interpolation=cv2.INTER_LINEAR) / S
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{w}x{h}', '-r', '24', '-i', '-',
                      '-c:v', 'libx264', '-preset', 'slow', '-crf', '12', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for i in range(L):
    if i < K:
        t = i / K; t = t * t * (3 - 2 * t)
        A, B = F[L + i], F[i]
        fab = flow(A, B)   # A(x) ~ B(x + fab)
        Aw = cv2.remap(A, xx - t * fab[..., 0], yy - t * fab[..., 1], cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        Bw = cv2.remap(B, xx + (1 - t) * fab[..., 0], yy + (1 - t) * fab[..., 1], cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        f = cv2.addWeighted(Aw, 1 - t, Bw, t, 0)
    else:
        f = F[i]
    p.stdin.write(f.tobytes())
    if i == 0: cv2.imwrite(out.replace('.mp4', '-first.png'), f)
p.stdin.close(); p.wait(); print('frames', N, '->', L)
