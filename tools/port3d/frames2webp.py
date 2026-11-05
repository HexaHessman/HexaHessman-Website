# Extract every frame of a video (via ffmpeg JPEGs) and save as WebP for scroll scrubbing, plus a manifest.
# Usage: venv/bin/python frames2webp.py <video.mp4> <out_dir> [width] [quality]
import sys, os, subprocess, tempfile, json, glob
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; W = int(sys.argv[3]) if len(sys.argv) > 3 else 1600; Q = int(sys.argv[4]) if len(sys.argv) > 4 else 72
os.makedirs(out, exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-vf', f'scale={W}:-2', '-q:v', '2', os.path.join(tmp, 'f%04d.jpg')], check=True)
    files = sorted(glob.glob(os.path.join(tmp, 'f*.jpg')))
    for f in files:
        Image.open(f).save(os.path.join(out, os.path.basename(f).replace('.jpg', '.webp')), 'WEBP', quality=Q, method=5)
json.dump({'count': len(files), 'pattern': 'f%04d.webp'}, open(os.path.join(out, 'manifest.json'), 'w'))
print('frames', len(files))
