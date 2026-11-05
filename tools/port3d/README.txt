Port 3D model (entrance scene) - how to rebuild

1. Textures:  python3 -m venv venv && venv/bin/pip install pillow numpy
              venv/bin/python texgen.py <tex_dir>
2. Model:     /Applications/Blender.app/Contents/MacOS/Blender -b -P build_port3.py -- <out_dir> <tex_dir>
3. Copy <out_dir>/port.glb to assets/models/port.glb, and <tex_dir>/clouds.png + water_normal.jpg to assets/models/.
Preview: http://localhost:8765/port-view.html  (add ?grey for the old grey stage-1 model)
