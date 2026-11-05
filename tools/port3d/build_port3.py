# Stage 3: the detailed, textured port. Container ship (lofted hull with a weathered paint atlas, hatch covers, 9-wide
# container stack with lashing bridges and one open crate, accommodation with bridge wings, anchors, rails), the hand-built
# bunker tanker with its hose crane and the real STS coupling chain, a concrete quay with gantry cranes, a container yard,
# light masts, mooring lines and distant cranes. Textures come from texgen.py.
# Usage: Blender -b -P build_port3.py -- <out_dir> <tex_dir>
# Axes: +X = bow, +Y = tanker side, -Y = quay side, +Z = up. Metres. The waterline is moved to z = 0 at the end.
import bpy, bmesh, sys, math, os, random
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
OUT, TEX = argv[0], argv[1]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
col = bpy.context.collection
rng = random.Random(7)

def srgb(h):
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)

def _bsdf(m):
    try: m.use_nodes = True
    except Exception: pass
    return m.node_tree.nodes.get('Principled BSDF')

def mat(name, hexcol, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name); b = _bsdf(m)
    b.inputs['Base Color'].default_value = (*srgb(hexcol), 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    return m

def tex_mat(name, file, rough=0.6, metal=0.0, normal=None, nstr=1.0, rough_map=None):
    m = bpy.data.materials.new(name); b = _bsdf(m); nt = m.node_tree
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(TEX, file), check_existing=True)
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if normal:
        img = bpy.data.images.load(os.path.join(TEX, normal), check_existing=True); img.colorspace_settings.name = 'Non-Color'
        tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = img
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = nstr
        nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    if rough_map:
        ri = bpy.data.images.load(os.path.join(TEX, rough_map), check_existing=True); ri.colorspace_settings.name = 'Non-Color'
        tr = nt.nodes.new('ShaderNodeTexImage'); tr.image = ri
        nt.links.new(tr.outputs['Color'], b.inputs['Roughness'])
    return m

# ---------------------------------------------------------------- materials
HULL_T = tex_mat('hull_ship', 'hull_ship.jpg', 0.55)
DECK_T = tex_mat('deck_ship', 'deck_ship.jpg', 0.85)
TH_T = tex_mat('hull_tanker', 'hull_tanker.jpg', 0.55)
TDECK_T = tex_mat('deck_tanker', 'deck_tanker.jpg', 0.8)
WALL_T = tex_mat('wall_white', 'wall_white.jpg', 0.5)
CONC_T = tex_mat('concrete', 'quay_concrete.jpg', 0.9, 0.0, 'quay_concrete_nor.jpg', 0.8, 'quay_concrete_rough.jpg')
CONT = [tex_mat('cont_green', 'cont_green.jpg', 0.6, 0.0, 'cont_normal.jpg', 0.8),
        tex_mat('cont_green2', 'cont_green2.jpg', 0.6, 0.0, 'cont_normal.jpg', 0.8),
        tex_mat('cont_pale', 'cont_pale.jpg', 0.7, 0.0, 'cont_normal.jpg', 0.8),
        tex_mat('cont_dark', 'cont_dark.jpg', 0.6, 0.0, 'cont_normal.jpg', 0.8)]
CONT_W = [0.42, 0.22, 0.24, 0.12]
INSIDE_T = tex_mat('crate_inside', 'crate_inside.jpg', 0.8, 0.0, 'cont_normal.jpg', 0.8)
WOOD_T = tex_mat('crate_floor', 'crate_floor.jpg', 0.85)
GREEN = mat('green_paint', '1B4634', 0.55)
HATCH = mat('hatch_green', '24503D', 0.7)
WHITE = mat('white_paint', 'E9E7E0', 0.5)
WINDOW = mat('window', '1E2E36', 0.15, 0.3)
YELLOW = mat('yellow', 'D9A82A', 0.6)
BLACK = mat('black', '17191B', 0.85)
STEEL = mat('stainless', 'C2C6C1', 0.35, 0.85)
DOOR_HW = mat('door_hardware', '5E6461', 0.55, 0.5)
RED = mat('red', 'B4382A', 0.5)
ORANGE = mat('orange', 'E25A1C', 0.5)
PIPE = mat('pipe_green', '2E7A5A', 0.5)
CAST = mat('casting', '2A2F2D', 0.7)
CAST_T = tex_mat('casting_rusty', 'casting_metal.jpg', 0.75)
LASH = mat('lashing_grey', '8B918B', 0.6, 0.3)
CRANE = tex_mat('crane_green', 'crane_metal.jpg', 0.6, 0.0, 'crane_metal_nor.jpg', 0.9, 'crane_metal_rough.jpg')
ROPE = mat('rope', 'C9B98A', 0.9)
FAR = mat('far_grey', '8F9AA0', 0.9)

# ---------------------------------------------------------------- helpers
def obj_from_bmesh(name, bm, material, smooth=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); col.objects.link(o)
    me.materials.append(material)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return o

def uv_world(bm, su, sv, off=(0, 0, 0), zoff=0.0):
    """planar UVs per face by dominant normal axis, in metres / tile size (for tiling textures)."""
    uvl = bm.loops.layers.uv.verify(); bm.normal_update(); off = Vector(off)
    for f in bm.faces:
        n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            p = l.vert.co + off
            if ax == 0: u, v = p.y, p.z - zoff
            elif ax == 1: u, v = p.x, p.z - zoff
            else: u, v = p.x, p.y
            l[uvl].uv = (u / su, v / sv)

def box(name, size, loc, material, rot=(0, 0, 0), uv=None):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if uv: uv_world(bm, uv[0], uv[1], loc, uv[2] if len(uv) > 2 else 0.0)
    o = obj_from_bmesh(name, bm, material); o.location = loc; o.rotation_euler = rot; return o

def cyl(name, r, h, loc, material, rot=(0, 0, 0), segs=16):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r, depth=h)
    o = obj_from_bmesh(name, bm, material, smooth=True); o.location = loc; o.rotation_euler = rot; return o

def sphere(name, r, loc, material):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=r); o = obj_from_bmesh(name, bm, material, smooth=True); o.location = loc; return o

def tube(name, a, b, r, material, segs=10):
    a, b = Vector(a), Vector(b); d = b - a
    o = cyl(name, r, d.length, (a + b) / 2, material, segs=segs); o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = d.to_track_quat('Z', 'Y'); return o

class MB:
    """Accumulates many boxes and tubes into ONE mesh (one draw call on the web)."""
    def __init__(self): self.bm = bmesh.new()
    def box(self, size, loc, rot_z=0.0):
        r = bmesh.ops.create_cube(self.bm, size=1.0)
        M = Matrix.Translation(Vector(loc)) @ Matrix.Rotation(rot_z, 4, 'Z') @ Matrix.Diagonal((*size, 1.0))
        bmesh.ops.transform(self.bm, matrix=M, verts=r['verts'])
    def tube(self, a, b, r, segs=8, caps=True):
        a, b = Vector(a), Vector(b); d = b - a
        if d.length < 1e-4: return
        M = Matrix.Translation((a + b) / 2) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        res = bmesh.ops.create_cone(self.bm, cap_ends=caps, segments=segs, radius1=r, radius2=r, depth=d.length, matrix=M)
        for v in res['verts']:
            for f in v.link_faces:
                if len(f.verts) == 4: f.smooth = True
    def ring(self, c, r, tr, axis='Y', segs=12):
        c = Vector(c); pts = []
        for k in range(segs + 1):
            a = 2 * math.pi * k / segs
            p = Vector((math.cos(a) * r, 0, math.sin(a) * r)) if axis == 'Y' else Vector((0, math.cos(a) * r, math.sin(a) * r))
            pts.append(c + p)
        for k in range(segs): self.tube(pts[k], pts[k + 1], tr, 6, caps=False)
    def done(self, name, material, uv=None):
        if uv: uv_world(self.bm, *uv)
        return obj_from_bmesh(name, self.bm, material)

def strip(name, pts, height, material, thick=0.08):
    bm = bmesh.new(); lo = [bm.verts.new(p) for p in pts]; hi = [bm.verts.new((p[0], p[1], p[2] + height)) for p in pts]
    for k in range(len(pts) - 1): bm.faces.new([lo[k], lo[k + 1], hi[k + 1], hi[k]])
    o = obj_from_bmesh(name, bm, material); o.modifiers.new('solid', 'SOLIDIFY').thickness = thick; return o

def rails_into(mb, pts, height=1.1, every=3, r=0.05):
    for k in range(len(pts) - 1):
        a, b = Vector(pts[k]), Vector(pts[k + 1])
        mb.tube(a + Vector((0, 0, height)), b + Vector((0, 0, height)), r, 6)
        mb.tube(a + Vector((0, 0, height * 0.55)), b + Vector((0, 0, height * 0.55)), r * 0.7, 6)
    for k in range(0, len(pts), every):
        p = Vector(pts[k]); mb.tube(p, p + Vector((0, 0, height)), r * 0.8, 6)

def rope(name, a, b, sag, r=0.045):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 2; cu.fill_mode = 'FULL'
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2); a, b = Vector(a), Vector(b)
    for i, p in enumerate((a, (a + b) / 2 - Vector((0, 0, sag)), b)):
        bp = sp.bezier_points[i]; bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); col.objects.link(o); o.data.materials.append(ROPE); return o

def loft(name, x0, x1, depth, hb, rake, nx, nz, material, deck_material, deck_tile=8.0):
    """Lofted hull with an atlas UV: +Y side -> top half (bow on the left), -Y side -> bottom half (bow on the right);
    the deck (top faces) gets planar UVs for a tiling deck texture."""
    bm = bmesh.new(); xl = bm.verts.layers.float.new('xp'); rows = []
    for i in range(nx + 1):
        x = x0 + (x1 - x0) * i / nx; row = []
        for j in range(nz + 1):
            h = depth * j / nz; w = hb(min(x, x1 - 0.01), h); xx = x + rake(x, h)
            vs = bm.verts.new((xx, w, h)); vs[xl] = x
            vp = None
            if w > 0.02: vp = bm.verts.new((xx, -w, h)); vp[xl] = x
            row.append((vs, vp))
        rows.append(row)
    def face(vs):
        vs = [v for v in vs if v is not None]
        if len(set(vs)) >= 3:
            try: bm.faces.new(vs)
            except ValueError: pass
    for i in range(nx):
        for j in range(nz):
            a, b = rows[i][j], rows[i][j + 1]; c, d = rows[i + 1][j], rows[i + 1][j + 1]
            face([a[0], c[0], d[0], b[0]])
            face([a[1] or a[0], b[1] or b[0], d[1] or d[0], c[1] or c[0]])
        face([rows[i][0][0], rows[i][0][1] or rows[i][0][0], rows[i + 1][0][1] or rows[i + 1][0][0], rows[i + 1][0][0]])
    face([rows[0][j][0] for j in range(nz + 1)] + [rows[0][j][1] for j in range(nz, -1, -1) if rows[0][j][1]])
    face([rows[i][nz][0] for i in range(nx + 1)] + [rows[i][nz][1] for i in range(nx, -1, -1) if rows[i][nz][1]])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    uvl = bm.loops.layers.uv.new('UVMap'); L = x1 - x0; deck_faces = set()
    for f in bm.faces:
        n = f.normal
        if n.z > 0.9:
            deck_faces.add(f.index)
            for l in f.loops: l[uvl].uv = (l.vert.co.x / deck_tile, l.vert.co.y / deck_tile)
            continue
        side = 1 if f.calc_center_median().y > 0 else -1
        for l in f.loops:
            x = l.vert[xl]; h = max(0.0, min(depth, l.vert.co.z))
            l[uvl].uv = (((x1 - x) / L, 0.5 + 0.5 * h / depth) if side > 0 else ((x - x0) / L, 0.5 * h / depth))
    o = obj_from_bmesh(name, bm, material, smooth=True); o.data.materials.append(deck_material)
    for p in o.data.polygons:
        if p.index in deck_faces: p.material_index = 1; p.use_smooth = False
    return o

# ---------------------------------------------------------------- the container ship hull
L, B, D, DRAFT = 150.0, 25.0, 14.0, 7.0
X_STERN, X_BOW = -75.0, 75.0
def halfbreadth(x, h):
    t = h / D
    # flared bow: fine entrance at the keel, almost full breadth at deck level until close to the stem (like the photo)
    if x >= 25:  f = max(0.0, 1.0 - ((x - 25.0) / (X_BOW - 25.0)) ** (1.9 + 2.6 * t ** 1.5))
    elif x <= -45: f = 1.0 - 0.3 * ((-45.0 - x) / 30.0) ** 1.5
    else: f = 1.0
    f = f ** 0.75
    fwd = max(0.0, min(1.0, (x - 20.0) / 55.0))
    bilge = 1.0 - (max(0.0, 1.0 - t / 0.35)) ** 2 * 0.35
    vee = 0.25 + 0.75 * t ** 0.9
    return B / 2 * f * (bilge * (1.0 - fwd) + vee * fwd)
def stem_x(h): return X_BOW + 4.0 * (h / D) ** 1.6
def ship_rake(x, h): return (stem_x(h) - X_BOW) * ((x - 60) / 15.0) if x > 60 else 0.0
loft('hull', X_STERN, X_BOW, D, halfbreadth, ship_rake, 90, 14, HULL_T, DECK_T)
def deck_edge(x, s, inset=0.05):
    xs = min(x, X_BOW - 0.01); return (x + ship_rake(x, D), s * (halfbreadth(xs, D) - inset), D)

# forecastle bulwark (solid plating) with a yellow rail on top; open yellow rails along the rest of the deck edge
yel = MB()
for s in (1, -1):
    fwd = [deck_edge(x, s, 0.04) for x in [48 + 27 * i / 30 for i in range(31)]]
    strip(f'bulwark_{s}', fwd, 1.3, GREEN, 0.1)
    rails_into(yel, [(p[0], p[1], p[2] + 1.3) for p in fwd], 0.25, 4, 0.05)
    aft = [deck_edge(x, s, 0.15) for x in [-73 + 121 * i / 80 for i in range(81)]]
    rails_into(yel, aft, 1.1, 3, 0.045)
yel.done('rails_yellow', YELLOW)
# mooring gear on the foredeck: windlasses, bitts, fairleads; breakwater-free foredeck like the photo
gear = MB()
for x in (52.0, 60.0):
    for s in (-1, 1):
        gear.tube((x - 0.9, s * 5.5, D + 0.9), (x + 0.9, s * 5.5, D + 0.9), 1.0, 14)       # windlass drum
        gear.box((2.4, 1.6, 0.8), (x, s * 5.5, D + 0.4))
        gear.tube((x + 4, s * 9.0, D), (x + 4, s * 9.0, D + 1.1), 0.32, 10); gear.tube((x + 4.9, s * 9.0, D), (x + 4.9, s * 9.0, D + 1.1), 0.32, 10)
for x in (-40.0, -10.0, 20.0, -66.0):
    for s in (-1, 1):
        y = s * (halfbreadth(x, D) - 1.2); gear.tube((x, y, D), (x, y, D + 0.9), 0.3, 10); gear.tube((x + 0.8, y, D), (x + 0.8, y, D + 0.9), 0.3, 10)
gear.done('deck_gear', BLACK)
# anchors in their hawse pockets, both bows
for s in (1, -1):
    x, hz = 66.0, 11.6
    w = halfbreadth(x, hz); dw = halfbreadth(x + 0.5, hz) - halfbreadth(x - 0.5, hz)
    ang = math.atan2(s * dw, 1.0); y = s * (w + 0.12)
    pocket = box(f'hawse_pocket_{s}', (2.2, 0.2, 3.0), (x + ship_rake(x, hz), y - s * 0.12, hz - 0.6), mat(f'pocket_{s}', '102A20', 0.8), (0, 0, ang))
    an = MB(); cx = x + ship_rake(x, hz)
    an.box((0.32, 0.32, 2.6), (0, 0, 0)); an.box((1.8, 0.36, 0.36), (0, 0, -1.25))
    for k in (-1, 1): an.box((0.36, 0.3, 1.1), (k * 0.85, 0, -0.85))
    a = an.done(f'anchor_{s}', mat(f'anchor_{s}', '35383A', 0.6, 0.4)); a.location = (cx, y + s * 0.15, hz - 0.3); a.rotation_euler = (0, 0, ang)

# ---------------------------------------------------------------- bunker station (unchanged geometry, painted)
ST_X, ST_W, ST_H = 32.0, 9.0, 4.2
ST_Z = D - 0.4 - ST_H / 2
st_y = halfbreadth(ST_X, ST_Z)
box('station_recess', (ST_W, 2.6, ST_H), (ST_X, st_y - 1.3 + 0.05, ST_Z), mat('station_dark', '1F2A27', 0.8))
box('station_frame_top', (ST_W + 0.6, 0.5, 0.35), (ST_X, st_y - 0.2, ST_Z + ST_H / 2 + 0.17), WHITE)
box('station_frame_bot', (ST_W + 0.6, 0.5, 0.35), (ST_X, st_y - 0.2, ST_Z - ST_H / 2 - 0.17), WHITE)
for sx in (-1, 1): box(f'station_post_{sx}', (0.5, 0.5, ST_H + 0.7), (ST_X + sx * (ST_W / 2 + 0.3), st_y - 0.2, ST_Z), WHITE)
box('station_platform', (ST_W - 0.6, 2.2, 0.15), (ST_X, st_y - 1.2, ST_Z - ST_H / 2 + 0.9), STEEL)
st_r = MB(); rails_into(st_r, [(ST_X - ST_W / 2 + 0.4 + k * (ST_W - 0.8) / 6, st_y - 0.35, ST_Z - ST_H / 2 + 0.98) for k in range(7)], 1.0, 2, 0.04); st_r.done('station_rail', WHITE)
MANIFOLD = []
for k in range(3):
    mx_ = ST_X - 1.6 + k * 1.6
    cyl(f'manifold_pipe_{k}', 0.14, 1.6, (mx_, st_y - 1.5, ST_Z - 0.4), STEEL, rot=(math.pi / 2, 0, 0))
    cyl(f'manifold_valve_{k}', 0.26, 0.5, (mx_, st_y - 1.7, ST_Z - 0.4), RED, rot=(math.pi / 2, 0, 0))
    MANIFOLD.append(Vector((mx_, st_y - 0.6, ST_Z - 0.4)))

# ---------------------------------------------------------------- the container module (textured)
CW, CH, CL = 2.44, 2.59, 12.19
def uv_container(bm, off=Vector()):
    """atlas: top half long side (u reads left->right from outside), bottom: door end | closed end | roof."""
    uvl = bm.loops.layers.uv.verify(); bm.normal_update()
    for f in bm.faces:
        n = f.normal
        for l in f.loops:
            p = l.vert.co + off
            fx = (p.x + CL / 2) / CL; fy = (p.y + CW / 2) / CW; fz = (p.z + CH / 2) / CH
            fx, fy, fz = (min(1, max(0, t)) for t in (fx, fy, fz))
            if abs(n.y) > 0.7: uv = ((1 - fx) if n.y > 0 else fx, 0.5 + 0.5 * fz)
            elif n.x < -0.7: uv = (0.25 * (1 - fy), 0.5 * fz)
            elif n.x > 0.7: uv = (0.25 + 0.25 * fy, 0.5 * fz)
            else: uv = (0.5 + 0.5 * fx, 0.5 * fy)
            l[uvl].uv = uv

def container_module(name, paint, open_doors=False):
    parts = []
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((CL - 0.14, CW - 0.04, CH - 0.04)), verts=bm.verts); bmesh.ops.translate(bm, vec=Vector((0.05, 0, 0)), verts=bm.verts)
    uv_container(bm); body = obj_from_bmesh(name + '_body', bm, paint); parts.append(body)
    bm = bmesh.new()
    for sx in (1, -1):
        for sy in (1, -1):
            for sz in (1, -1):
                r = bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=Vector((0.18, 0.18, 0.12)), verts=r['verts'])
                bmesh.ops.translate(bm, vec=Vector((sx * (CL / 2 - 0.09), sy * (CW / 2 - 0.08), sz * (CH / 2 - 0.05))), verts=r['verts'])
    for sy in (1, -1):   # corner posts at the door end
        r = bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=Vector((0.16, 0.16, CH - 0.2)), verts=r['verts'])
        bmesh.ops.translate(bm, vec=Vector((-CL / 2 + 0.1, sy * (CW / 2 - 0.08), 0)), verts=r['verts'])
    for zc in (CH / 2 - 0.08, -CH / 2 + 0.08):
        r = bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=Vector((0.16, CW - 0.2, 0.16)), verts=r['verts']); bmesh.ops.translate(bm, vec=Vector((-CL / 2 + 0.1, 0, zc)), verts=r['verts'])
    uv_world(bm, 0.9, 0.9)
    parts.append(obj_from_bmesh(name + '_castings', bm, CAST_T))
    doors = []
    for s in (1, -1):
        hl = Vector((-CL / 2 + 0.06, s * (CW / 2 - 0.1), 0))
        hinge = bpy.data.objects.new(f'{name}_hinge_{s}', None); col.objects.link(hinge); hinge.location = hl; parts.append(hinge)
        bm = bmesh.new(); r = bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=Vector((0.08, CW / 2 - 0.12, CH - 0.26)), verts=r['verts']); bmesh.ops.translate(bm, vec=Vector((0, -s * (CW / 4 - 0.05), 0)), verts=r['verts'])
        uv_container(bm, hl)
        door = obj_from_bmesh(f'{name}_door_{s}', bm, paint); door.parent = hinge; parts.append(door); doors.append(hinge)
        bm = bmesh.new()
        for k in range(2):   # two locking bars per door with guide brackets, cam keepers and a handle
            yb = -s * (CW / 4 - 0.05) + (k - 0.5) * 0.52
            rb = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.032, radius2=0.032, depth=CH - 0.36)
            bmesh.ops.translate(bm, vec=Vector((-0.11, yb, 0)), verts=rb['verts'])
            for zc in (-(CH / 2 - 0.28), CH / 2 - 0.28):   # cam keepers top and bottom
                rk = bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=Vector((0.07, 0.12, 0.12)), verts=rk['verts']); bmesh.ops.translate(bm, vec=Vector((-0.09, yb, zc)), verts=rk['verts'])
            for zc in (-0.62, 0.0, 0.62):   # guide brackets
                rg = bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=Vector((0.05, 0.1, 0.04)), verts=rg['verts']); bmesh.ops.translate(bm, vec=Vector((-0.08, yb, zc)), verts=rg['verts'])
            rh = bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=Vector((0.045, 0.32, 0.045)), verts=rh['verts']); bmesh.ops.translate(bm, vec=Vector((-0.13, yb + 0.13 * s, -0.25)), verts=rh['verts'])
        for zc in (-(CH / 2 - 0.3), -0.42, 0.42, CH / 2 - 0.3):   # four hinges on the outer edge
            rq = bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=Vector((0.08, 0.1, 0.15)), verts=rq['verts']); bmesh.ops.translate(bm, vec=Vector((-0.05, s * 0.02, zc)), verts=rq['verts'])
        bars = obj_from_bmesh(f'{name}_bars_{s}', bm, DOOR_HW, smooth=False); bars.parent = hinge; parts.append(bars)
    if open_doors:
        doors[0].rotation_euler = (0, 0, math.radians(-112)); doors[1].rotation_euler = (0, 0, math.radians(112))
        bm = bmesh.new(); r = bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=Vector((CL - 0.3, CW - 0.2, 0.06)), verts=r['verts']); bmesh.ops.translate(bm, vec=Vector((0.05, 0, -CH / 2 + 0.12)), verts=r['verts'])
        uvl = bm.loops.layers.uv.verify()
        for f in bm.faces:
            for l in f.loops: l[uvl].uv = ((l.vert.co.x + CL / 2) / CL, (l.vert.co.y + CW / 2) / CW)
        parts.append(obj_from_bmesh(name + '_floor', bm, WOOD_T))
        me = body.data; bmh = bmesh.new(); bmh.from_mesh(me)
        for f in list(bmh.faces):
            if f.normal.x < -0.9: bmh.faces.remove(f)
        bmh.to_mesh(me); bmh.free()
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        x0i, x1i = -CL / 2 + 0.14, CL / 2 - 0.1
        bmesh.ops.scale(bm, vec=Vector((x1i - x0i, CW - 0.14, CH - 0.14)), verts=bm.verts); bmesh.ops.translate(bm, vec=Vector(((x0i + x1i) / 2, 0, 0)), verts=bm.verts)
        bm.normal_update()
        for f in list(bm.faces):
            if f.normal.x < -0.9: bm.faces.remove(f)
        uv_container(bm)
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
        inner = obj_from_bmesh(name + '_interior', bm, INSIDE_T); parts.append(inner)
        for ob in (inner, parts[-2]):
            me2 = ob.data; ca = me2.color_attributes.new('Col', 'BYTE_COLOR', 'CORNER')
            for poly in me2.polygons:
                for li in poly.loop_indices:
                    co = me2.vertices[me2.loops[li].vertex_index].co; t = (co.x - x0i) / (x1i - x0i)
                    b = max(0.18, 1.0 - 0.82 * t ** 0.8) * (0.85 if co.z > 0 else 1.0); ca.data[li].color = (b, b, b, 1.0)
            me2.color_attributes.active_color = ca
    root = bpy.data.objects.new(name, None); col.objects.link(root)
    for p in parts:
        if p.parent is None: p.parent = root
    return root

modules = []
for i, paint in enumerate(CONT):
    m = container_module(f'box{i}', paint); m.hide_render = True; m.hide_viewport = True
    for p in m.children_recursive: p.hide_render = True; p.hide_viewport = True
    modules.append(m)
def place_container(name, module, loc, rot_z):
    inst = bpy.data.objects.new(name, None); col.objects.link(inst)
    for p in module.children_recursive:
        if p.type != 'MESH': continue
        d = p.copy(); d.data = p.data; d.hide_render = False; d.hide_viewport = False; col.objects.link(d)
        m = p.matrix_basis.copy(); q = p.parent
        while q is not None and q is not module:      # module-space transform (hidden templates are not evaluated, so
            m = q.matrix_basis @ m; q = q.parent       # matrix_world would be stale for parts parented to a door hinge)
        d.parent = inst; d.matrix_parent_inverse.identity(); d.matrix_basis = m
    inst.rotation_euler = (0, 0, rot_z); inst.location = loc; return inst

# ---------------------------------------------------------------- hatch covers, stack, lashing bridges
COLS, ROWS, BAYS = 9, 5, 6
GAPY, GAPX, HC = 0.08, 1.6, 1.8
stack_front_x = 36.0
OPEN_COL, OPEN_ROW = 4, 4
open_module = container_module('crate', CONT[0], open_doors=True)
bay_cx = [stack_front_x - CL / 2 - b * (CL + GAPX) for b in range(BAYS)]
STACK_HALF = COLS * (CW + GAPY) / 2
hatch = MB()
for b, cx in enumerate(bay_cx):
    hatch.box((CL + 0.5, 2 * STACK_HALF - 0.6, HC), (cx, 0, D + HC / 2))
    hatch.box((CL + 0.7, 0.2, 0.25), (cx, STACK_HALF - 0.2, D + HC + 0.02)); hatch.box((CL + 0.7, 0.2, 0.25), (cx, -STACK_HALF + 0.2, D + HC + 0.02))
hatch.done('hatch_covers', HATCH)
for b, cx in enumerate(bay_cx):
    for row in range(ROWS):
        for c in range(COLS):
            loc = (cx, (c - (COLS - 1) / 2) * (CW + GAPY), D + HC + CH / 2 + row * CH)
            if b == 0 and row == OPEN_ROW and c == OPEN_COL:
                open_module.rotation_euler = (0, 0, math.pi); open_module.location = loc
            else:
                place_container(f'c_{b}_{row}_{c}', rng.choices(modules, CONT_W)[0], loc, math.pi)
lash = MB(); lrail = MB()
for b in range(BAYS - 1):
    xg = bay_cx[b] - CL / 2 - GAPX / 2; z0 = D + HC; zt = z0 + 2 * CH
    for j in range(COLS + 1):
        y = (j - COLS / 2) * (CW + GAPY)
        for sx in (-0.55, 0.55): lash.box((0.16, 0.16, zt - z0), (xg + sx, y, (z0 + zt) / 2))
    for zp in (z0 + CH, zt):
        lash.box((1.3, 2 * STACK_HALF + 0.4, 0.07), (xg, 0, zp))
        for sx in (-0.6, 0.6): lrail.tube((xg + sx, -STACK_HALF - 0.2, zp + 1.0), (xg + sx, STACK_HALF + 0.2, zp + 1.0), 0.03, 6)
    for j in range(COLS):   # lashing rods: an X from each bridge platform to the corner castings of the tiers either side
        yc = (j - (COLS - 1) / 2) * (CW + GAPY)
        for s in (-1, 1):
            for dy in (-0.9, 0.9):
                lash.tube((xg + s * 0.55, yc + dy * 0.6, z0 + CH + 0.1), (xg + s * (GAPX / 2 + 0.05), yc + dy, z0 + 2 * CH - 0.05), 0.022, 5)
                lash.tube((xg + s * 0.55, yc + dy * 0.6, z0 + 0.1), (xg + s * (GAPX / 2 + 0.05), yc + dy, z0 + CH - 0.05), 0.022, 5)
lash.done('lashing_bridges', LASH); lrail.done('lashing_rails', YELLOW)

# ---------------------------------------------------------------- accommodation, bridge, funnel
ACC_L, ACC_W, ACC_H = 12.0, 21.5, 18.0
acc_x = bay_cx[-1] - CL / 2 - 7.0
box('accommodation', (ACC_L, ACC_W, ACC_H), (acc_x, 0, D + ACC_H / 2), WALL_T, uv=(6.0, 3.0, D))
box('bridge_house', (8.0, ACC_W * 0.92, 3.4), (acc_x + 1.0, 0, D + ACC_H + 1.7), WHITE)
box('bridge_glass_f', (0.12, ACC_W * 0.9, 1.5), (acc_x + 5.02, 0, D + ACC_H + 2.0), WINDOW)
for s in (1, -1): box(f'bridge_glass_{s}', (7.4, 0.12, 1.5), (acc_x + 1.0, s * (ACC_W * 0.46 + 0.02), D + ACC_H + 2.0), WINDOW)
box('bridge_roof', (8.6, ACC_W * 0.95, 0.3), (acc_x + 1.0, 0, D + ACC_H + 3.55), WHITE)
box('bridge_wings', (3.6, B + 2.6, 0.35), (acc_x + 3.4, 0, D + ACC_H - 0.15), WHITE)
for s in (1, -1):
    box(f'wing_cab_{s}', (3.0, 2.4, 2.9), (acc_x + 3.4, s * (B / 2 + 0.1), D + ACC_H + 1.4), WHITE)
    box(f'wing_glass_{s}', (0.12, 2.2, 1.3), (acc_x + 4.95, s * (B / 2 + 0.1), D + ACC_H + 1.9), WINDOW)
wr = MB()
for s in (1, -1):
    rails_into(wr, [(acc_x + 5.1, s * (ACC_W * 0.46 + 0.1 + k * (B / 2 - ACC_W * 0.46 - 1.2) / 3), D + ACC_H) for k in range(4)], 1.1, 1, 0.045)
    for k in range(5):   # external walkways down each side of the block
        z = D + 3.0 * (k + 1)
        wr.box((ACC_L, 1.0, 0.12), (acc_x, s * (ACC_W / 2 + 0.5), z))
        rails_into(wr, [(acc_x - ACC_L / 2 + q * ACC_L / 4, s * (ACC_W / 2 + 1.0), z) for q in range(5)], 1.0, 1, 0.04)
rails_into(wr, [(acc_x - 3.2 + q * 1.6, 0, 0) for q in range(1)], 0.1, 1, 0.01)
wr.done('acc_rails', WHITE)
mast = MB()
mast.tube((acc_x, 0, D + ACC_H + 3.7), (acc_x, 0, D + ACC_H + 13.0), 0.22, 10)
mast.box((0.25, 7.0, 0.25), (acc_x, 0, D + ACC_H + 10.5)); mast.box((0.25, 4.0, 0.25), (acc_x, 0, D + ACC_H + 12.2))
mast.box((0.5, 5.2, 0.3), (acc_x + 2.6, 0, D + ACC_H + 5.0)); mast.tube((acc_x + 2.6, 0, D + ACC_H + 3.7), (acc_x + 2.6, 0, D + ACC_H + 4.85), 0.15, 8)
mast.box((1.6, 1.6, 2.0), (acc_x - 2.5, 4.0, D + ACC_H + 4.7)); mast.box((1.6, 1.6, 2.0), (acc_x - 2.5, -4.0, D + ACC_H + 4.7))
mast.done('radar_mast', WHITE)
for s in (1, -1): sphere(f'radome_{s}', 0.9, (acc_x - 2.5, s * 4.0, D + ACC_H + 6.4), WHITE)
box('funnel', (5.5, 4.4, 9.0), (acc_x - 10.0, 0, D + ACC_H - 2.5), GREEN)
box('funnel_band', (5.6, 4.5, 1.2), (acc_x - 10.0, 0, D + ACC_H + 0.6), WHITE)
box('funnel_top', (5.6, 4.5, 0.6), (acc_x - 10.0, 0, D + ACC_H + 2.2), BLACK)
for s in (1, -1): cyl(f'exhaust_{s}', 0.45, 1.6, (acc_x - 10.4, s * 0.9, D + ACC_H + 3.1), BLACK)
box('lifeboat', (7.0, 3.0, 2.6), (acc_x - 1.0, (ACC_W / 2 + 2.0), D + 10.0), ORANGE)
box('lifeboat_canopy', (6.0, 2.6, 0.8), (acc_x - 1.0, (ACC_W / 2 + 2.0), D + 11.6), ORANGE)
box('lifeboat_davit', (7.4, 0.3, 0.3), (acc_x - 1.0, (ACC_W / 2 + 2.0), D + 12.3), WHITE)
fm = MB(); fm.tube((50, 2.6, D), (50, 2.6, D + 20), 0.2, 10); fm.box((0.2, 3.4, 0.2), (50, 2.6, D + 15.5)); fm.box((1.4, 1.4, 0.15), (50, 2.6, D + 11.0))
fm.done('foremast', WHITE)

# ---------------------------------------------------------------- the bunker tanker (hand-built, textured)
TL, TB, TD, TDRAFT = 50.0, 10.5, 4.6, 2.3
TK_X, TK_Y = 28.0, B / 2 + 6.0
def t_half(x, h):
    t = h / TD
    if x >= 10: f = max(0.0, 1.0 - ((x - 10.0) / 15.0) ** 1.7)
    elif x <= -17: f = 1.0 - 0.35 * ((-17.0 - x) / 8.0) ** 1.4
    else: f = 1.0
    f = f ** 0.7
    fwd = max(0.0, min(1.0, (x - 5.0) / 20.0))
    bilge = 1.0 - (max(0.0, 1.0 - t / 0.4)) ** 2 * 0.4
    vee = 0.3 + 0.7 * t ** 0.9
    return TB / 2 * f * (bilge * (1 - fwd) + vee * fwd)
def t_rake(x, h): return 1.5 * (h / TD) ** 1.5 * ((x - 19) / 6.0) if x > 19 else 0.0
troot = bpy.data.objects.new('tanker', None); col.objects.link(troot)
troot.location = (TK_X, TK_Y, DRAFT - TDRAFT)
before = set(bpy.data.objects)
loft('t_hull', -TL / 2, TL / 2, TD, t_half, t_rake, 50, 8, TH_T, TDECK_T, 6.0)
tr = MB()
for s in (1, -1):
    pts = [(x + t_rake(x, TD), s * (t_half(min(x, TL / 2 - 0.01), TD) - 0.02), TD) for x in [-22 + i * 1.5 for i in range(30)]]
    strip(f't_bulwark_{s}', pts, 0.5, GREEN)
    rails_into(tr, [(p[0], p[1], p[2] + 0.5) for p in pts], 0.6, 2, 0.035)
def wbox(name, size, loc, uvz):
    return box(name, size, loc, WALL_T, uv=(6.0, 2.6, uvz))
wbox('t_house', (7.5, 8.0, 5.0), (15.5, 0, TD + 2.5), TD)
wbox('t_bridge', (6.0, 7.0, 2.6), (15.5, 0, TD + 6.3), TD + 5.0)
box('t_bridge_wing', (2.0, 10.6, 0.3), (15.5, 0, TD + 5.1), WHITE)
box('t_bridge_glass_f', (0.12, 6.4, 1.0), (18.55, 0, TD + 6.7), WINDOW)
for s in (1, -1): box(f't_bridge_glass_{s}', (5.4, 0.12, 0.9), (15.5, s * 3.55, TD + 6.7), WINDOW)
box('t_bridge_top', (6.2, 7.2, 0.25), (15.5, 0, TD + 7.7), WHITE)
rails_into(tr, [(12.6 + k * 1.45, s * 5.2, TD + 5.25) for s in (1,) for k in range(5)], 1.0, 1, 0.035)
rails_into(tr, [(12.6 + k * 1.45, -5.2, TD + 5.25) for k in range(5)], 1.0, 1, 0.035)
rails_into(tr, [(12.5 + k * 1.5, s * 3.5, TD + 7.85) for s in (1,) for k in range(5)], 0.9, 1, 0.03)
tm = MB(); tm.tube((14.5, 0, TD + 7.8), (14.5, 0, TD + 14.5), 0.12, 8); tm.box((0.15, 3.6, 0.15), (14.5, 0, TD + 13.0))
tm.box((1.8, 0.3, 0.2), (15.5, 0, TD + 8.4)); tm.tube((15.5, 0, TD + 7.8), (15.5, 0, TD + 8.3), 0.08, 6)
tm.box((0.5, 0.5, 0.5), (18.6, 2.8, TD + 8.0)); tm.done('t_mast', WHITE)
sphere('t_radome', 0.55, (16.5, -2.6, TD + 8.4), WHITE)
box('t_liferaft', (1.4, 0.9, 0.8), (13.0, 4.3, TD + 5.6), ORANGE)
def deck_slab(name, x0, x1, hb, z0, h, material, inset=0.1):
    bm = bmesh.new(); vs = []
    for z in (z0, z0 + h):
        for x in (x0, x1):
            w = hb(x) - inset; vs.append((bm.verts.new((x, -w, z)), bm.verts.new((x, w, z))))
    (a0, a1), (b0, b1), (c0, c1), (d0, d1) = vs
    for f in ([a0, b0, b1, a1], [c0, c1, d1, d0], [a0, c0, d0, b0], [a1, b1, d1, c1], [a0, a1, c1, c0], [b0, d0, d1, b1]): bm.faces.new(f)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return obj_from_bmesh(name, bm, material)
deck_slab('t_focsle', 19.5, 24.6, lambda x: t_half(min(x, 24.9), TD), TD, 0.8, GREEN)
tg = MB()
tg.tube((21.3, 0, TD + 1.3), (22.7, 0, TD + 1.3), 0.6, 12); tg.box((1.8, 1.4, 0.5), (22.0, 0, TD + 1.0))
for x in (-23.0, -10.0, 8.0, 20.5):
    for s in (1, -1): tg.tube((x, s * (TB / 2 - 0.8), TD), (x, s * (TB / 2 - 0.8), TD + 0.8), 0.22, 8)
tg.tube((-24.3, 0, TD + 0.9), (-22.7, 0, TD + 0.9), 0.7, 12)
for x in (-14.0, -7.0, 0.0, 7.0, 14.0):   # tyre fenders hung on the side facing the ship (and the other side)
    for s in (1, -1):
        w = t_half(x, TD - 1.2) + 0.25
        tg.ring((x, s * w, TD - 1.2), 0.55, 0.22, 'Y' if False else 'X', 14)
tg.done('t_gear', BLACK)
wbox('t_aft_house', (5.5, 6.5, 3.0), (-19.5, 0, TD + 1.5), TD)
box('t_funnel', (2.0, 1.6, 2.6), (-21.5, 0, TD + 4.3), GREEN); box('t_funnel_top', (2.1, 1.7, 0.35), (-21.5, 0, TD + 5.75), BLACK)
rails_into(tr, [(-22.2 + k * 1.35, s * 3.2, TD + 3.0) for s in (1,) for k in range(5)], 0.9, 1, 0.03)
tp = MB()
for y in (-1.1, 1.1):
    tp.tube((-17.0, y, TD + 0.95), (12.0, y, TD + 0.95), 0.2, 12); tp.tube((-17.0, y * 1.6, TD + 0.75), (12.0, y * 1.6, TD + 0.75), 0.12, 10)
for i, x in enumerate((3.0, 4.6, 6.2)): tp.tube((x, -3.1, TD), (x, -3.1, TD + 1.0), 0.14, 10)
for x in (-12.0, -5.0, 2.0, 9.0):   # branch pipes to the tank domes
    for s in (1, -1): tp.tube((x, s * 1.6, TD + 0.75), (x, s * 2.6, TD + 0.75), 0.1, 8)
tp.done('t_pipes', PIPE)
tw = MB()
for x in range(-16, 12, 4): tw.box((0.3, 3.8, 0.75), (x, 0, TD + 0.375))
tw.box((29.0, 1.6, 0.12), (-2.5, 0, TD + 1.75))
for s in (1, -1):
    tw.tube((-17.0, s * 0.8, TD + 2.75), (12.0, s * 0.8, TD + 2.75), 0.04, 6)
    for x in range(-16, 13, 4): tw.tube((x, s * 0.8, TD + 1.8), (x, s * 0.8, TD + 2.75), 0.035, 6)
for i, x in enumerate((-12.0, -5.0, 2.0, 9.0)):
    for s in (1, -1):
        tw.tube((x, s * 3.0, TD), (x, s * 3.0, TD + 0.55), 1.0, 20); tw.tube((x, s * 3.0, TD + 0.55), (x, s * 3.0, TD + 0.85), 0.45, 12)
    tw.tube((x + 2.0, 3.9, TD), (x + 2.0, 3.9, TD + 3.2), 0.2, 10)
tw.box((4.0, 1.0, 0.8), (-6.0, -3.6, TD + 0.4))
tw.done('t_deck_white', WHITE)
for i in range(4): sphere(f't_vent_cap_{i}', 0.3, ((-12.0, -5.0, 2.0, 9.0)[i] + 2.0, 3.9, TD + 3.3), WHITE)
tv = MB()
for i, x in enumerate((3.0, 4.6, 6.2)):
    tv.tube((x, -3.1, TD + 1.0), (x, -3.1, TD + 1.6), 0.28, 12); tv.tube((x, -3.1, TD + 1.7), (x, -3.1, TD + 1.76), 0.3, 14)
tv.box((0.8, 0.5, 1.1), (11.0, 4.5, TD + 0.55)); tv.box((0.8, 0.5, 1.1), (-15.0, -4.5, TD + 0.55))     # fire stations
tv.tube((10.0, -4.0, TD), (10.0, -4.0, TD + 1.4), 0.12, 8); tv.tube((10.0, -4.0, TD + 1.4), (10.8, -4.0, TD + 1.8), 0.1, 8)   # fire monitor
tv.done('t_red', RED)
lr = MB()
for (x, s) in ((-8.0, -1), (4.0, 1), (-18.0, 1)):
    lr.ring((x, s * (TB / 2 - 0.05), TD + 1.05), 0.35, 0.07, 'X', 12)
lr.done('t_liferings', ORANGE)
for i in range(3): cyl(f't_spare_hose_{i}', 0.16, 3.8, (-6.0, -3.6, TD + 0.95 + i * 0.1), STEEL, rot=(0, math.pi / 2, 0), segs=12)
PED = Vector((1.0, -1.2, 0.0))
pd = MB()
pd.tube((PED.x, PED.y, TD), (PED.x, PED.y, TD + 4.4), 1.0, 20); pd.tube((PED.x, PED.y, TD + 4.4), (PED.x, PED.y, TD + 4.75), 1.25, 20)
pd.tube((PED.x, PED.y, TD + 4.75), (PED.x, PED.y, TD + 5.5), 0.85, 20); pd.box((1.6, 1.3, 1.4), (PED.x - 1.2, PED.y + 0.9, TD + 5.6))
rails_into(pd, [(PED.x - 1.3 + k * 0.65, PED.y - 1.3, TD + 4.75) for k in range(5)], 0.9, 1, 0.03)
pd.done('t_crane_pedestal', WHITE)
for o in set(bpy.data.objects) - before:
    if o.parent is None: o.parent = troot
tr.done('t_rails', WHITE).parent = troot
bpy.context.view_layer.update()

# ---- bunkering connection (same hardware as stage 2)
HOSE_R = 0.15
base = troot.matrix_world @ Vector((PED.x, PED.y, TD + 5.5))
head = Vector((ST_X + 1.0, st_y + 2.6, D + 9.5))
knee = base + Vector((0.9, -0.4, 6.0))
cr = MB()
cr.tube(base, knee, 0.34, 14); cr.tube(knee, head, 0.26, 14)
cr.box((0.9, 0.9, 0.9), knee)
cr.done('boom', WHITE)
tube('boom_cyl', base + Vector((0.6, 0.6, 0.3)), knee + Vector((-0.5, 0.2, -1.0)), 0.12, STEEL, 8)
cyl('head_cross', 0.14, 5.0, head, STEEL, rot=(0, math.pi / 2, 0))
for k in range(3):
    hx = ST_X - 1.6 + k * 1.6
    riser_top = Vector((hx, st_y + 2.4, D + 9.4)); riser_len = 1.6
    cyl(f'riser_{k}', 0.11, riser_len, riser_top - Vector((0, 0, riser_len / 2)), STEEL, segs=12)
    fl = riser_top - Vector((0, 0, riser_len)); cyl(f'riser_flange_{k}', 0.24, 0.08, fl, CAST, segs=16); cyl(f'riser_flange2_{k}', 0.24, 0.08, fl - Vector((0, 0, 0.1)), CAST, segs=16)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.3, radius2=HOSE_R + 0.03, depth=0.7); cone = obj_from_bmesh(f'restrictor_{k}', bm, BLACK, smooth=True); cone.location = fl - Vector((0, 0, 0.45))
    top = fl - Vector((0, 0, 0.8))
    chain_top = MANIFOLD[k] + Vector((0, 1.9, 0))
    cu = bpy.data.curves.new(f'hose_{k}', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = HOSE_R; cu.bevel_resolution = 8; cu.fill_mode = 'FULL'
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(3)
    for i, pt in enumerate([top, Vector((hx, st_y + 2.3, ST_Z - 2.4)), Vector((hx, st_y + 1.4, ST_Z - 3.3)), chain_top]):
        bp = sp.bezier_points[i]; bp.co = pt; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    h = bpy.data.objects.new(f'hose_{k}', cu); col.objects.link(h); h.data.materials.append(STEEL)
    cyl(f'hose_band_{k}', HOSE_R + 0.03, 0.5, Vector((hx, st_y + 2.3, ST_Z + 1.2)), RED, segs=16)
    cyl(f'hose_strap_{k}', HOSE_R + 0.04, 0.12, Vector((hx, st_y + 2.3, ST_Z - 0.6)), BLACK, segs=16)
    y = chain_top.y; z = chain_top.z
    def part(name, r, length, y0, material=STEEL):
        cyl(f'{name}_{k}', r, length, Vector((hx, y0 - length / 2, z)), material, rot=(math.pi / 2, 0, 0), segs=20); return y0 - length
    y = part('hose_end_flange', 0.26, 0.10, y, CAST)
    y = part('erc_half_a', 0.21, 0.32, y)
    y = part('erc_break_ring', 0.24, 0.06, y, RED)
    y = part('erc_half_b', 0.21, 0.32, y)
    y = part('erc_flange', 0.26, 0.10, y, CAST)
    y = part('qcdc', 0.23, 0.36, y)
    y = part('presentation_flange', 0.30, 0.10, y, CAST)
    y = part('manifold_spool', 0.14, max(0.2, y - (MANIFOLD[k].y - 0.6)), y)
    tube(f'wire_{k}', riser_top + Vector((0.35, 0, 0)), Vector((hx + 0.3, st_y + 2.3, ST_Z - 0.6)), 0.02, BLACK, 6)
box('drip_tray', (ST_W - 1.0, 2.0, 0.25), (ST_X, st_y - 1.1, ST_Z - ST_H / 2 + 0.45), BLACK)
# the tanker's own mooring lines to the ship's deck
for (tx, sx_) in ((-23.0, -8.0), (20.5, 52.0), (-10.0, 20.0), (8.0, 38.0)):
    a = troot.matrix_world @ Vector((tx, -(TB / 2 - 0.8), TD + 0.7))
    rope(f't_line_{tx}', a, (sx_, halfbreadth(sx_, D) - 0.6, D + 0.6), 0.6)

# ---------------------------------------------------------------- quay: concrete, fenders, bollards, mooring lines
Q_EDGE = -(B / 2 + 3.0); Q_TOP = DRAFT + 3.0; Q_W = 70.0
box('quay', (520, Q_W, 12.0), (-60, Q_EDGE - Q_W / 2, Q_TOP - 6.0), CONC_T, uv=(3.5, 3.5))
qf = MB(); qb = MB()
for i in range(40):
    x = -310 + i * 13
    qf.tube((x, Q_EDGE + 0.55, DRAFT - 1.5), (x, Q_EDGE + 0.55, Q_TOP - 0.3), 0.75, 14)
    if i % 2 == 0:
        qb.tube((x + 6, Q_EDGE - 1.6, Q_TOP), (x + 6, Q_EDGE - 1.6, Q_TOP + 0.75), 0.42, 12); qb.box((1.1, 1.1, 0.2), (x + 6, Q_EDGE - 1.6, Q_TOP + 0.8))
qf.done('quay_fenders', BLACK); qb.done('quay_bollards', YELLOW)
box('quay_line', (520, 0.3, 0.02), (-60, Q_EDGE - 3.0, Q_TOP + 0.01), YELLOW)
box('quay_cap', (520, 0.6, 0.25), (-60, Q_EDGE - 0.3, Q_TOP + 0.12), WHITE)
for (sx_, qx) in ((70.0, 96.0), (64.0, 84.0), (40.0, 18.0), (-50.0, -28.0), (-68.0, -94.0), (-72.0, -106.0)):
    rope(f'mline_{sx_}', (sx_, -(halfbreadth(sx_, D) - 0.3), D + 0.8), (qx, Q_EDGE - 1.6, Q_TOP + 0.6), 1.2, 0.06)

# ---------------------------------------------------------------- STS gantry cranes (like the green ones in the photo)
def sts_crane(name, x, yw, yl, zq, boom_deg=78):
    m = MB(); w = MB(); k = MB()
    for lx in (x - 9, x + 9):
        for ly in (yw, yl):
            m.box((1.5, 1.5, 42), (lx, ly, zq + 21)); k.box((6.0, 2.2, 1.8), (lx, ly, zq + 0.9))
        m.box((1.4, abs(yw - yl) + 1.5, 2.4), (lx, (yw + yl) / 2, zq + 42.5))
        m.box((1.0, abs(yw - yl), 1.2), (lx, (yw + yl) / 2, zq + 13))
        m.tube((lx, yw, zq + 13.5), (lx, yl, zq + 41), 0.4, 8); m.tube((lx, yl, zq + 13.5), (lx, yw, zq + 41), 0.4, 8)
    for ly in (yw, yl):
        m.box((19.5, 1.4, 2.0), (x, ly, zq + 42)); m.box((18.0, 1.0, 1.2), (x, ly, zq + 13))
    back = yl - 24
    for gx in (x - 3, x + 3):
        m.box((1.2, abs(yw - back), 2.6), (gx, (yw + back) / 2, zq + 44.5))
        L_ = 55.0; a = math.radians(boom_deg); tip = Vector((gx, yw + L_ * math.cos(a), zq + 44.5 + L_ * math.sin(a)))
        m.tube((gx, yw, zq + 44.5), tip, 0.75, 6)
        apex = Vector((x + (gx - x) * 0.3, yw - 7, zq + 78))
        m.tube((gx, yw, zq + 44), apex, 0.6, 6); m.tube((gx, yl, zq + 44), apex, 0.6, 6)
        m.tube(apex, (gx, yw + 0.6 * L_ * math.cos(a), zq + 44.5 + 0.6 * L_ * math.sin(a)), 0.18, 5)
        m.tube(apex, (gx, back, zq + 46), 0.18, 5)
    m.tube((x - 2, yw - 7, zq + 78), (x + 2, yw - 7, zq + 78), 0.6, 6)
    w.box((9.0, 12.0, 6.0), (x, back + 7, zq + 49)); w.box((3.0, 3.2, 2.8), (x, yl - 3, zq + 41.0))
    w.box((5.0, 7.0, 2.0), (x, yl - 6, zq + 46.8))
    k.box((520, 0.3, 0.1), (x, yw, zq + 0.05)) if False else None
    o1 = m.done(name + '_frame', CRANE, uv=(4.0, 4.0)); o2 = w.done(name + '_house', WHITE); o3 = k.done(name + '_bogies', BLACK)
    return [o1, o2, o3]
YW, YL = Q_EDGE - 4.0, Q_EDGE - 34.0
crane_parts = sts_crane('sts_0', -58.0, YW, YL, Q_TOP)
for i, cx in enumerate((-122.0, -186.0)):
    for p in crane_parts:
        d = p.copy(); d.data = p.data; col.objects.link(d); d.location = (cx - (-58.0), 0, 0); d.name = p.name.replace('sts_0', f'sts_{i + 1}')
rl = MB()
for ly in (YW, YL): rl.box((520, 0.25, 0.08), (-60, ly, Q_TOP + 0.04))
rl.done('crane_rails', BLACK)
# container yard behind the cranes
for i in range(14):
    for j in range(4):
        for h in range(1 + (i * 7 + j * 3) % 3):
            x = -175 + i * 14.0; y = YL - 6 - j * (CW + 0.4)
            place_container(f'yard_{i}_{j}_{h}', rng.choices(modules, CONT_W)[0], (x, y, Q_TOP + CH / 2 + h * CH), 0.0)
lp = MB()
for i in range(8):
    x = -190 + i * 50.0; y = Q_EDGE - 48
    lp.tube((x, y, Q_TOP), (x, y, Q_TOP + 32), 0.35, 8); lp.box((3.0, 1.2, 0.8), (x, y, Q_TOP + 32.3))
lp.done('light_masts', mat('mast_grey', 'B8BCB8', 0.5, 0.4))

# ---------------------------------------------------------------- distant cranes and skyline (hazed out by the fog)
far = []
for (fx, fy, rz) in ((-420, 380, math.pi), (-500, 380, math.pi), (-580, 380, math.pi), (-660, 380, math.pi), (-300, 420, math.pi),
                     (-700, -60, -math.pi / 2), (-700, -140, -math.pi / 2), (-700, 30, -math.pi / 2), (250, 520, math.pi), (330, 520, math.pi)):
    for p in crane_parts:
        d = p.copy(); d.data = p.data; col.objects.link(d)
        M = Matrix.Translation((fx, fy, 0)) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Translation((58.0, -YW, 0))
        d.matrix_world = M; far.append(d)
sk = MB(); r2 = random.Random(3)
# distant shoreline city: low warehouses, mid-rise blocks and a few towers, 1.4-2 km out, hazed by the viewer's fog
for band, (x0, n, hmin, hmax) in enumerate(((-1900, 150, 5, 22), (-2200, 120, 8, 34), (-2500, 70, 14, 55))):
    for i in range(n):
        y = -2000 + (4000 / n) * i + r2.uniform(-10, 10); x = x0 + r2.uniform(-60, 60)
        h = r2.uniform(hmin, hmax) * (1.7 if r2.random() < 0.05 else 1.0)
        sk.box((r2.uniform(14, 45), r2.uniform(12, 38), h), (x, y, DRAFT + h / 2 - 1))
sk.done('skyline', FAR)

root_all = [o for o in col.objects if o.parent is None]
for o in root_all: o.location.z -= DRAFT
bpy.context.view_layer.update()

# ---------------------------------------------------------------- quick check render + export
water = box('water', (4000, 4000, 0.1), (0, 0, -0.05), mat('water', '2A4F70', 0.12))
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 4.5; so = bpy.data.objects.new('sun', sun); col.objects.link(so); so.rotation_euler = (math.radians(50), math.radians(10), math.radians(70))
world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True; world.node_tree.nodes['Background'].inputs[0].default_value = (0.55, 0.66, 0.8, 1); world.node_tree.nodes['Background'].inputs[1].default_value = 0.7
engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
sc.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
sc.render.resolution_x = 1600; sc.render.resolution_y = 900; sc.render.image_settings.file_format = 'JPEG'
def shoot(name, loc, target, lens=35):
    cam = bpy.data.cameras.new(name); cam.lens = lens; cam.clip_end = 3000; co = bpy.data.objects.new(name, cam); col.objects.link(co)
    co.location = loc; d = Vector(target) - Vector(loc); co.rotation_mode = 'QUATERNION'; co.rotation_quaternion = d.to_track_quat('-Z', 'Y')
    sc.camera = co; sc.render.filepath = os.path.join(OUT, name + '.jpg'); bpy.ops.render.render(write_still=True); print('RENDER', name)
shoot('front', (X_BOW + 68, 2.5, 8), (14, 0, 3), lens=35)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'port.blend'))
bpy.data.objects.remove(water)
for o in list(bpy.data.objects):
    if o.type in ('CAMERA', 'LIGHT'): bpy.data.objects.remove(o)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'port.glb'), export_format='GLB', use_visible=True, export_apply=True,
    export_image_format='AUTO', export_vertex_color='ACTIVE', export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6)
print('OBJECTS', len([o for o in bpy.data.objects if o.type == 'MESH' and o.visible_get()]))
print('GLB')
print('SAVED')
