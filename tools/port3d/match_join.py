# Make a branch clip start exactly on the intro's last frame: for the first frames, scale/shift and colour-match the
# branch to the intro end frame and ease that correction out; crossfade from the intro frame over the first few frames.
# Usage: venv/bin/python match_join.py <intro_last.jpg> <branch.mp4> <out.mp4> <scale> <dx> <dy>   (dx, dy in 1920px)
import sys, os, subprocess, tempfile, glob
import numpy as np
from PIL import Image
last, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
S0, DX0, DY0 = float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
EASE_N, FADE_N, COL_N = 30, 10, 48
A = Image.open(last).convert('RGB'); W, H = A.size; Aa = np.asarray(A, np.float32)
with tempfile.TemporaryDirectory() as tmp:
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-q:v', '1', os.path.join(tmp, 'f%04d.png')], check=True)
    files = sorted(glob.glob(os.path.join(tmp, 'f*.png')))
    first = None
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB').resize((W, H), Image.LANCZOS)
        t = min(1.0, i / EASE_N); e = t * t * (3 - 2 * t)              # 0 at the join, 1 when the correction is gone
        s = S0 + (1 - S0) * e; dx = DX0 * (1 - e); dy = DY0 * (1 - e)
        if abs(s - 1) > 1e-4 or abs(dx) > .1 or abs(dy) > .1:
            sw, sh = W * s, H * s
            x0 = (sw - W) / 2 - dx; y0 = (sh - H) / 2 - dy
            im = im.resize((round(sw), round(sh)), Image.LANCZOS).crop((round(x0), round(y0), round(x0) + W, round(y0) + H))
        arr = np.asarray(im, np.float32)
        if first is None:   # colour correction measured on the aligned first frame
            gain = Aa.reshape(-1, 3).mean(0) / np.maximum(1, arr.reshape(-1, 3).mean(0)); first = True
        c = 1 - min(1.0, i / COL_N); c = c * c * (3 - 2 * c)
        arr = arr * (1 + (gain - 1) * c)
        if i < FADE_N:
            k = i / FADE_N; k = k * k * (3 - 2 * k)
            arr = Aa * (1 - k) + arr * k
        Image.fromarray(arr.clip(0, 255).astype(np.uint8)).save(f)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24', '-i', os.path.join(tmp, 'f%04d.png'), '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], check=True)
print('done', out, len(files), 'frames')
