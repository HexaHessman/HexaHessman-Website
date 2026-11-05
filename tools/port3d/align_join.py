# Seamless join: make a branch clip start exactly on the intro's last frame.
# 1. Find the precise transform (homography: scale, shift, tiny rotation/perspective) between the branch's first frame
#    and the intro's last frame with OpenCV ECC.
# 2. Apply that SAME transform to every branch frame (constant, so nothing zooms or slides during the clip).
# 3. Match the branch's colour to the intro (per-channel mean/std from the aligned first frame), constant for the clip.
# 4. Crossfade only the first FADE frames from the intro frame (geometry already matches, so this only hides texture noise).
# Usage: venv/bin/python align_join.py <intro_last.jpg> <branch.mp4> <out.mp4> [fade_frames]
import sys, os, subprocess, tempfile, glob
import numpy as np, cv2

last, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
FADE = int(sys.argv[4]) if len(sys.argv) > 4 else 6
A = cv2.imread(last, cv2.IMREAD_COLOR); H, W = A.shape[:2]

with tempfile.TemporaryDirectory() as tmp:
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-q:v', '1', os.path.join(tmp, 'f%04d.png')], check=True)
    files = sorted(glob.glob(os.path.join(tmp, 'f*.png')))
    B0 = cv2.resize(cv2.imread(files[0]), (W, H), interpolation=cv2.INTER_AREA)

    # ECC on a blurred greyscale pyramid: coarse (1/4) then full-ish (1/2)
    def grey(im, s):
        g = cv2.cvtColor(cv2.resize(im, (int(W * s), int(H * s)), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
        return cv2.GaussianBlur(g, (5, 5), 0)
    warp = np.array([[1.03, 0, -0.015 * W - 24], [0, 1.03, -0.015 * H - 16], [0, 0, 1]], np.float32)   # rough start: 3% zoom + shift
    for s in (0.25, 0.5):
        S = np.diag([s, s, 1]).astype(np.float32); Si = np.diag([1 / s, 1 / s, 1]).astype(np.float32)
        w_s = S @ warp @ Si
        crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-7)
        _, w_s = cv2.findTransformECC(grey(A, s), grey(B0, s), w_s, cv2.MOTION_HOMOGRAPHY, crit, None, 5)
        warp = Si @ w_s @ S
    def apply(im): return cv2.warpPerspective(im, warp, (W, H), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)

    B0w = apply(B0).astype(np.float32); Af = A.astype(np.float32)
    m = (slice(40, H - 40), slice(40, W - 40))
    mu_a, sd_a = Af[m].reshape(-1, 3).mean(0), Af[m].reshape(-1, 3).std(0)
    mu_b, sd_b = B0w[m].reshape(-1, 3).mean(0), B0w[m].reshape(-1, 3).std(0)
    gain = sd_a / np.maximum(1, sd_b); bias = mu_a - mu_b * gain
    print('warp', np.round(warp, 4).tolist())
    print('first-frame difference: raw %.2f, aligned %.2f, aligned+colour %.2f' % (
        np.abs(Af - B0.astype(np.float32)).mean(), np.abs(Af - B0w).mean(), np.abs(Af - (B0w * gain + bias)).mean()))

    # de-stutter: a frame that nearly repeats the previous one while its neighbours move is rebuilt by optical-flow
    # interpolation between the previous and next frames (Seedance sometimes holds a frame, then jumps)
    raw = [cv2.resize(cv2.imread(f), (W, H), interpolation=cv2.INTER_AREA) for f in files]
    small = [cv2.cvtColor(cv2.resize(r, (480, 270)), cv2.COLOR_BGR2GRAY).astype(np.float32) for r in raw]
    d = [0.0] + [float(np.abs(small[i] - small[i - 1]).mean()) for i in range(1, len(small))]
    for i in range(2, len(raw) - 2):
        around = (d[i - 1] + d[i + 2]) / 2
        if around > 0.9 and d[i] < 0.35 * around and d[i + 1] > 1.5 * around:
            g0 = cv2.cvtColor(raw[i - 1], cv2.COLOR_BGR2GRAY); g1 = cv2.cvtColor(raw[i + 1], cv2.COLOR_BGR2GRAY)
            flow = cv2.calcOpticalFlowFarneback(g0, g1, None, 0.5, 4, 25, 4, 7, 1.5, 0)
            gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
            a = cv2.remap(raw[i - 1], gx - flow[..., 0] * 0.5, gy - flow[..., 1] * 0.5, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            b = cv2.remap(raw[i + 1], gx + flow[..., 0] * 0.5, gy + flow[..., 1] * 0.5, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            raw[i] = cv2.addWeighted(a, 0.5, b, 0.5, 0)
            print('rebuilt held frame', i, 'diffs', round(d[i], 2), round(d[i + 1], 2), 'around', round(around, 2))
    for i, f in enumerate(files):
        x = apply(raw[i]).astype(np.float32) * gain + bias
        if i < FADE:
            k = i / FADE; k = k * k * (3 - 2 * k)
            x = Af * (1 - k) + x * k
        cv2.imwrite(f, np.clip(x, 0, 255).astype(np.uint8))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24', '-i', os.path.join(tmp, 'f%04d.png'), '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], check=True)
print('done', out, len(files))
