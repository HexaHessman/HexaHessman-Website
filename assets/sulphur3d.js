// HexaHessman · Sulphur — one WebGL scene, two worlds, one camera driven by scroll.
//   Chapter 1 (top):    your drawing of the ship is the set; a real 3D grab comes down, pours sulphur and lifts away, on a loop.
//   Transition:         the camera dives toward the heap and the screen dips into the background green.
//   Chapter 2 (below):  bagged sulphur comes out and drifts away along a row, fading into the distance.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { buildIso, buildIbc, buildChips, setPalette } from './scene-chapters.js?v=2611e';

const BG = 0x0F2A1E, CREAM = new THREE.Color(0xe6d9b6), INK = new THREE.Color(0xd8ccae);
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const smooth = THREE.MathUtils.smoothstep, lerp = THREE.MathUtils.lerp;

// ---------- renderer, scene, light ----------
const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.setClearColor(BG, 1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(BG, 26, 70);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.add(new THREE.HemisphereLight(0xe8dfc4, 0x0F2A1E, 0.9));
const key = new THREE.DirectionalLight(0xfff1d6, 2.2); key.position.set(-6, 9, 7); scene.add(key);
const rim = new THREE.DirectionalLight(0x9fb89a, 0.8); rim.position.set(8, 4, -6); scene.add(rim);
const fill = new THREE.DirectionalLight(0xf2e8cf, 0.55); fill.position.set(2, 10, 12); scene.add(fill);

const camera = new THREE.PerspectiveCamera(34, innerWidth / innerHeight, 0.1, 140);
const draco = new DRACOLoader().setDecoderPath('https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/libs/draco/gltf/');
const loader = new GLTFLoader().setDRACOLoader(draco);

// cream edge glow shared by the steel, the grab and the bags
function addRim(mat, { desat = 0, tint = new THREE.Vector3(1.02, 1.0, 0.82), rimK = 0.18, panel = 0 } = {}) {
  mat.onBeforeCompile = sh => {
    sh.uniforms.uRim = { value: CREAM };
    if (panel) sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vPanelPos; varying vec3 vPanelN;')
      .replace('#include <begin_vertex>', '#include <begin_vertex>\nvPanelPos = (modelMatrix * vec4(transformed, 1.0)).xyz; vPanelN = normalize(mat3(modelMatrix) * objectNormal);');
    const panelCode = panel ? `
        vec3 ptw = pow(abs(normalize(vPanelN)), vec3(4.0)); ptw /= (ptw.x + ptw.y + ptw.z);
        float pl = plate(vPanelPos.zy) * ptw.x + plate(vPanelPos.xz) * ptw.y + plate(vPanelPos.xy) * ptw.z;
        diffuseColor.rgb = mix(diffuseColor.rgb, uRim, pl * 0.12);` : '';
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', '#include <common>\nuniform vec3 uRim;' + (panel ? `
        varying vec3 vPanelPos; varying vec3 vPanelN;
        float plate(vec2 c) { vec2 q = c / vec2(${(panel * 1.6).toFixed(2)}, ${panel.toFixed(2)}); vec2 g = abs(fract(q - 0.5) - 0.5) / fwidth(q); return 1.0 - min(min(g.x, g.y), 1.0); }` : ''))
      .replace('#include <map_fragment>', `#include <map_fragment>
        float lum = dot(diffuseColor.rgb, vec3(0.299, 0.587, 0.114));
        diffuseColor.rgb = mix(diffuseColor.rgb, lum * vec3(${tint.x.toFixed(3)}, ${tint.y.toFixed(3)}, ${tint.z.toFixed(3)}), ${desat.toFixed(3)});` + panelCode)
      .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
        float fres = pow(1.0 - abs(dot(normalize(normal), normalize(vViewPosition))), 3.0);
        totalEmissiveRadiance += uRim * fres * ${rimK.toFixed(3)};`);
  };
  mat.customProgramCacheKey = () => `rim-${desat}-${rimK}-${panel}`;
}

// =====================================================================================
// CHAPTER 1 — the drawing is the set; the grab and the pour are real 3D, composited into it
// =====================================================================================
const scene1 = new THREE.Scene();                     // the grab lives in its own scene, no fog
scene1.environment = scene.environment;
scene1.add(new THREE.HemisphereLight(0xe8dfc4, 0x0F2A1E, 1.0));
{ const k = new THREE.DirectionalLight(0xfff1d6, 2.4); k.position.set(-6, 8, 10); scene1.add(k);
  const f = new THREE.DirectionalLight(0xdfe6d2, 0.7); f.position.set(6, 2, 8); scene1.add(f);
  const front = new THREE.DirectionalLight(0xf3ead6, 0.55); front.position.set(-2, 4, 12); scene1.add(front); }
const pourScene = new THREE.Scene();                  // the grains are drawn last, over the composite
const cam1 = new THREE.PerspectiveCamera(30, innerWidth / innerHeight, 0.1, 200);
const DEPTH1 = 30;                                    // how far in front of the camera the grab hangs

// the plate: your drawing with the grab removed; the visible part of it (cover-fit) is plateView
const PLATE = { w: 1672, h: 941 };
const plateTex = new THREE.TextureLoader().load('assets/grab-empty.jpg');
plateTex.colorSpace = THREE.SRGBColorSpace; plateTex.anisotropy = 8;
const plateView = { cx: 0.5, cy: 0.5, sx: 1, sy: 1 };
function layoutPlate() {
  const a = innerWidth / innerHeight, A = PLATE.w / PLATE.h;
  if (a > A) { plateView.sx = 1; plateView.sy = A / a; } else { plateView.sx = a / A; plateView.sy = 1; }
  const want = a < 1 ? 0.6 : 0.5;                     // on phones, keep the grab in view
  plateView.cx = THREE.MathUtils.clamp(want, plateView.sx / 2, 1 - plateView.sx / 2);
  plateView.cy = 0.5;
  cam1.aspect = a; cam1.updateProjectionMatrix();
}
const _v = new THREE.Vector3();
function plateToWorld(px, py, depth, out) {           // plate pixel -> point at that depth in front of cam1
  const nx = ((px / PLATE.w - plateView.cx) / plateView.sx) * 2, ny = -((py / PLATE.h - plateView.cy) / plateView.sy) * 2;
  const h = Math.tan(THREE.MathUtils.degToRad(cam1.fov / 2)) * depth;
  return out.set(nx * h * cam1.aspect, ny * h, -depth);
}
function worldToPlate(p) {                            // world point -> plate pixel
  _v.copy(p).project(cam1);
  return { x: (_v.x / 2 * plateView.sx + plateView.cx) * PLATE.w, y: (-_v.y / 2 * plateView.sy + plateView.cy) * PLATE.h };
}

// the heap's outline, read from the plate, so falling grains land on the drawn sulphur
const heapTop = new Float32Array(PLATE.w).fill(PLATE.h * 0.74);
new THREE.ImageLoader().load('assets/grab-empty.jpg', img => {
  const c = document.createElement('canvas'); c.width = PLATE.w; c.height = PLATE.h;
  const g = c.getContext('2d', { willReadFrequently: true }); g.drawImage(img, 0, 0, PLATE.w, PLATE.h);
  const d = g.getImageData(0, 0, PLATE.w, PLATE.h).data;
  const lum = new Uint8Array(PLATE.w * PLATE.h);
  for (let i = 0; i < lum.length; i++) lum[i] = 0.299 * d[i * 4] + 0.587 * d[i * 4 + 1] + 0.114 * d[i * 4 + 2];
  const bright = (x, y) => lum[y * PLATE.w + x] >= 150;
  const wide = (x, y) => { for (let k = -9; k <= 9; k++) if (!bright(THREE.MathUtils.clamp(x + k, 0, PLATE.w - 1), y)) return false; return true; };   // a 19px bright band: heap, not a rib
  for (let x = 0; x < PLATE.w; x++) {
    for (let y = 560; y < PLATE.h - 4; y++) {
      let ok = true;
      for (let k = 0; k < 4 && ok; k++) if (!wide(x, y + k)) ok = false;
      if (ok) { heapTop[x] = y; break; }
    }
  }
  for (let x = 2; x < PLATE.w - 2; x++) heapTop[x] = (heapTop[x - 2] + heapTop[x - 1] + heapTop[x] + heapTop[x + 1] + heapTop[x + 2]) / 5;
});

// ---------- the grab: Higgsfield model split in Blender into frame, two arms, two jaws ----------
// Linkage (model units, x/y = Blender x/z): the jaws turn on a shared hinge; each arm turns on its top pin T
// and stretches slightly so its lower end stays on the jaw corner B as the jaw swings.
const LINK = { hinge: new THREE.Vector2(0, 0.3305), T: new THREE.Vector2(0.1349, 0.5208), B: new THREE.Vector2(0.3333, 0.2805) };
const CLOSED = THREE.MathUtils.degToRad(-14), OPEN = THREE.MathUtils.degToRad(10);
const grab = new THREE.Group(); scene1.add(grab);
const parts = {};
function setJaws(theta) {
  for (const sd of [-1, 1]) {
    const jaw = parts[sd < 0 ? 'jawL' : 'jawR'], arm = parts[sd < 0 ? 'armL' : 'armR'];
    if (!jaw || !arm) continue;
    const a = sd * theta; jaw.rotation.z = a;
    const bx = sd * LINK.B.x - LINK.hinge.x, by = LINK.B.y - LINK.hinge.y;
    const b2x = LINK.hinge.x + bx * Math.cos(a) - by * Math.sin(a), b2y = LINK.hinge.y + bx * Math.sin(a) + by * Math.cos(a);
    const tx = sd * LINK.T.x, ty = LINK.T.y;
    arm.rotation.z = Math.atan2(b2y - ty, b2x - tx) - Math.atan2(LINK.B.y - ty, sd * LINK.B.x - tx);
    arm.scale.setScalar(Math.hypot(b2x - tx, b2y - ty) / Math.hypot(sd * LINK.B.x - tx, LINK.B.y - ty));
  }
}
const model = new THREE.Group(); grab.add(model);   // model units: the grab is about 1 tall, base at y = 0
// the load: a core filling the bucket, covered in thousands of real 3D grains; the whole thing is
// tagged blue so the composite shader tones it as sulphur rather than steel
const SAND_TAG = new THREE.Color(0.55, 0.6, 1.0);
const sandMat = new THREE.MeshStandardMaterial({ color: SAND_TAG, roughness: 1.0, metalness: 0, flatShading: true, envMapIntensity: 0.3 });
const grainGeo = new THREE.DodecahedronGeometry(1, 0);
const CORE = { cx: 0.165, cy: 0.155, cz: 0.115, y: 0.17 };     // ellipsoid filling the bucket: y 0.015 .. 0.325, crown just over the rim
const cap = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 24), sandMat.clone());
cap.material.color = new THREE.Color(0.45, 0.5, 1.0);          // slightly darker core, so the grains stand off it
cap.scale.set(CORE.cx, CORE.cy, CORE.cz); cap.position.set(0, CORE.y, 0); model.add(cap);
const NL = reduce ? 2000 : 8000;                               // grains sitting on the load
const loadGrains = new THREE.InstancedMesh(grainGeo, sandMat, NL); loadGrains.frustumCulled = false; model.add(loadGrains);
const loadMats = [], loadOrder = [...Array(NL).keys()];
const ZERO = new THREE.Matrix4().set(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1);
{ const m = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), pos = new THREE.Vector3(), sc = new THREE.Vector3();
  for (let i = 0; i < NL; i++) {
    // a point on the core's surface, weighted to the top where it shows; a little jitter so they overlap like a real heap
    let th = Math.random() * Math.PI * 2, ph = Math.acos(Math.random() < 0.72 ? Math.random() : -Math.random());
    const r = 0.98 + Math.random() * 0.06;
    pos.set(Math.sin(ph) * Math.cos(th) * CORE.cx * r, Math.cos(ph) * CORE.cy * r + CORE.y, Math.sin(ph) * Math.sin(th) * CORE.cz * r);
    const g = 0.0028 + Math.random() * 0.003; sc.set(g * (0.7 + Math.random() * 0.6), g * (0.7 + Math.random() * 0.6), g * (0.7 + Math.random() * 0.6));
    q.setFromEuler(e.set(Math.random() * 6.3, Math.random() * 6.3, Math.random() * 6.3));
    loadMats.push(m.clone().compose(pos, q, sc)); loadGrains.setMatrixAt(i, loadMats[i]);
  }
  for (let i = NL - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [loadOrder[i], loadOrder[j]] = [loadOrder[j], loadOrder[i]]; }
  loadGrains.instanceMatrix.needsUpdate = true; }
let released = 0;
const fit = { scale: 1, base: new THREE.Vector3(0, 0, -DEPTH1), screenH: 1 };
// target in the drawing (plate pixels): the closed jaws span x 832..1215 and their tips sit at y 452
const GRAB_TARGET = { left: 832, right: 1215, bottom: 452 };
const GRAB_TILT = 0.34;                               // radians: we see into the jaws from above, as in the drawing
function jawsBoxPlate() {
  const box = new THREE.Box3(); for (const k of ['jawL', 'jawR']) if (parts[k]) box.expandByObject(parts[k], true);   // precise: the real vertices
  let x0 = 1e9, x1 = -1e9, y1 = -1e9;
  for (let i = 0; i < 8; i++) {
    const p = worldToPlate(new THREE.Vector3(i & 1 ? box.max.x : box.min.x, i & 2 ? box.max.y : box.min.y, i & 4 ? box.max.z : box.min.z));
    x0 = Math.min(x0, p.x); x1 = Math.max(x1, p.x); y1 = Math.max(y1, p.y);
  }
  return { x0, x1, y1, cz: (box.min.z + box.max.z) / 2 };
}
function fitGrab() {                                   // scale and place the 3D grab over the drawn one
  if (!parts.jawL) return;
  setJaws(CLOSED); grab.rotation.set(GRAB_TILT, 0, 0);
  grab.scale.setScalar(1); grab.position.set(0, 0, -DEPTH1); grab.updateMatrixWorld(true);
  for (let it = 0; it < 3; it++) {
    const b = jawsBoxPlate();
    grab.scale.multiplyScalar((GRAB_TARGET.right - GRAB_TARGET.left) / (b.x1 - b.x0)); grab.updateMatrixWorld(true);
    const b2 = jawsBoxPlate();
    const have = plateToWorld((b2.x0 + b2.x1) / 2, b2.y1, -b2.cz, new THREE.Vector3());
    const want = plateToWorld((GRAB_TARGET.left + GRAB_TARGET.right) / 2, GRAB_TARGET.bottom, -b2.cz, new THREE.Vector3());
    grab.position.add(want.sub(have)); grab.updateMatrixWorld(true);
  }
  fit.scale = grab.scale.x; fit.base.copy(grab.position);
  fit.screenH = 2 * Math.tan(THREE.MathUtils.degToRad(cam1.fov / 2)) * DEPTH1;
}
async function loadGrab() {
  try {
    const gltf = await loader.loadAsync('assets/models/grab5.d.glb');
    const obj = gltf.scene;
    obj.traverse(o => {
      if (o.name) { const key = o.name.startsWith('frame') ? 'frame' : o.name.slice(0, 4); if (/^(frame|armL|armR|jawL|jawR)$/.test(key) && !parts[key]) parts[key] = o; }
      if (!o.isMesh) return;
      o.material = o.material.clone(); o.material.metalness = 0.55; o.material.roughness = 0.42; o.material.envMapIntensity = 1.2;
      o.material.color = new THREE.Color(0.95, 0.93, 0.85);
      addRim(o.material, { desat: 0.75, tint: new THREE.Vector3(0.98, 1.0, 0.9), rimK: 0.3, panel: 0.55 });   // plate seams like the drawing
    });
    model.add(obj);
    // hoist cables up out of frame
    const wire = new THREE.MeshStandardMaterial({ color: 0x9a9888, roughness: 0.5, metalness: 0.6 });
    for (const x of [-0.04, 0, 0.04]) { const c = new THREE.Mesh(new THREE.CylinderGeometry(0.004, 0.004, 3, 6), wire); c.position.set(x, 0.98 + 1.5, 0); model.add(c); }
    fitGrab();
  } catch (e) { console.warn('grab model missing', e); }
}

// ---------- the pour: grains fall from between the jaws and land on the drawn heap ----------
const dotTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 32; const g = c.getContext('2d'); g.fillStyle = '#fff'; g.beginPath(); g.arc(16, 16, 13, 0, 6.283); g.fill(); return new THREE.CanvasTexture(c); })();
const NP = reduce ? 1200 : 7000;
const pPos = new Float32Array(NP * 3).fill(-999), pVel = new Float32Array(NP * 3), pLife = new Float32Array(NP), pKind = new Uint8Array(NP);
const pGeo = new THREE.BufferGeometry(); pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3).setUsage(THREE.DynamicDrawUsage));
const pour = new THREE.Points(pGeo, new THREE.PointsMaterial({ color: 0xf1ede2, map: dotTex, size: 0.07, sizeAttenuation: true, transparent: true, opacity: 0.8, alphaTest: 0.35, depthWrite: false }));
pour.frustumCulled = false;                          // particles move every frame; never cull on a stale bound
pourScene.add(pour);
let pCursor = 0, pAcc = 0;
const gauss = () => (Math.random() + Math.random() + Math.random() - 1.5) / 1.5;
function emitGrain(x, y, z, vx, vy, vz, kind, life) {
  const i = pCursor; pCursor = (pCursor + 1) % NP;
  pPos[i * 3] = x; pPos[i * 3 + 1] = y; pPos[i * 3 + 2] = z; pVel[i * 3] = vx; pVel[i * 3 + 1] = vy; pVel[i * 3 + 2] = vz; pKind[i] = kind; pLife[i] = life;
}
const _m = new THREE.Vector3(), _w = new THREE.Vector3();
function floorY(x, z) {                               // world height of the drawn heap under a grain
  const px = THREE.MathUtils.clamp(Math.round(worldToPlate(_w.set(x, 0, z)).x), 0, PLATE.w - 1);
  return plateToWorld(px, heapTop[px], -z, _w).y;
}
function stepPour(dt, flow) {
  const s = fit.scale;
  pAcc += (reduce ? 500 : 4500) * flow * dt;
  model.localToWorld(_m.set(0, 0.03, 0));            // from the jaw tips, so grains never overlap the jaws
  while (pAcc >= 1) { pAcc -= 1; emitGrain(_m.x + gauss() * 0.17 * s, _m.y + Math.random() * 0.05 * s, _m.z + gauss() * 0.09 * s, gauss() * 0.07 * s, -0.1 * s - Math.random() * 0.25 * s, gauss() * 0.03 * s, 1, 6); }
  const g = 1.25 * s;                                 // gravity scaled to the grab, so the fall reads at the right size
  for (let i = 0; i < NP; i++) {
    if (!pKind[i]) continue;
    pLife[i] -= dt;
    pVel[i * 3 + 1] -= g * dt;
    pPos[i * 3] += pVel[i * 3] * dt; pPos[i * 3 + 1] += pVel[i * 3 + 1] * dt; pPos[i * 3 + 2] += pVel[i * 3 + 2] * dt;
    const fy = floorY(pPos[i * 3], pPos[i * 3 + 2]);
    if (pPos[i * 3 + 1] <= fy || pLife[i] <= 0) {
      if (pKind[i] === 1 && Math.random() < 0.3) emitGrain(pPos[i * 3], fy, pPos[i * 3 + 2], gauss() * 0.12 * s, (0.05 + Math.random() * 0.12) * s, gauss() * 0.05 * s, 2, 0.4);
      pKind[i] = 0; pPos[i * 3 + 1] = -999;
    }
  }
  pGeo.attributes.position.needsUpdate = true;
}


// ---------- the grains: as the load sinks, its grains spill from the gap between the jaws, fall, and pile up on the heap ----------
const NF = reduce ? 3000 : 12000;
const fallGrains = new THREE.InstancedMesh(grainGeo, sandMat, NF); fallGrains.frustumCulled = false; scene1.add(fallGrains);
for (let i = 0; i < NF; i++) fallGrains.setMatrixAt(i, ZERO);
const fPos = new Float32Array(NF * 3), fVel = new Float32Array(NF * 3), fRot = new Float32Array(NF * 3), fSpin = new Float32Array(NF * 3), fSize = new Float32Array(NF * 3), fState = new Uint8Array(NF);
let fCursor = 0, fAcc = 0;
const _fm = new THREE.Matrix4(), _fq = new THREE.Quaternion(), _fe = new THREE.Euler(), _fp = new THREE.Vector3(), _fs = new THREE.Vector3();
function spawnFall(x, y, z, vx, vy, vz, size) {
  const i = fCursor; fCursor = (fCursor + 1) % NF;
  fPos[i * 3] = x; fPos[i * 3 + 1] = y; fPos[i * 3 + 2] = z; fVel[i * 3] = vx; fVel[i * 3 + 1] = vy; fVel[i * 3 + 2] = vz;
  for (let k = 0; k < 3; k++) { fRot[i * 3 + k] = Math.random() * 6.3; fSpin[i * 3 + k] = gauss() * 6; fSize[i * 3 + k] = size * (0.7 + Math.random() * 0.6); }
  fState[i] = 1;
}
function restoreLoad() {                               // a new loop: the bucket is full again
  for (let i = 0; i < NL; i++) loadGrains.setMatrixAt(i, loadMats[i]);
  loadGrains.instanceMatrix.needsUpdate = true; released = 0;
}
function updateLoad(g) {                               // the core sinks as the jaws open; its grains are let go in a shuffled order
  if (g.poured <= 0 && released > 0) restoreLoad();
  cap.visible = g.poured < 0.995;
  cap.scale.y = Math.max(0.001, CORE.cy * (1 - g.poured)); cap.position.y = CORE.y - 0.13 * g.poured;
  const want = Math.min(NL, Math.floor(g.poured * NL * 1.02));
  if (want > released) {
    const s = fit.scale; model.localToWorld(_m.set(0, 0.03, 0));
    for (; released < want; released++) {
      const i = loadOrder[released]; loadGrains.setMatrixAt(i, ZERO);
      spawnFall(_m.x + gauss() * 0.14 * s, _m.y + Math.random() * 0.04 * s, _m.z + gauss() * 0.08 * s, gauss() * 0.06 * s, -0.1 * s - Math.random() * 0.2 * s, gauss() * 0.03 * s, (0.0028 + Math.random() * 0.003) * s);
    }
    loadGrains.instanceMatrix.needsUpdate = true;
  }
}
function stepGrains(dt, g, t) {
  const s = fit.scale, grav = 1.25 * s;
  // more grains than sit on the surface pour out of the body of the load
  fAcc += (reduce ? 800 : 3200) * g.flow * dt; model.localToWorld(_m.set(0, 0.03, 0));
  while (fAcc >= 1) { fAcc -= 1; spawnFall(_m.x + gauss() * 0.14 * s, _m.y + Math.random() * 0.04 * s, _m.z + gauss() * 0.08 * s, gauss() * 0.06 * s, -0.1 * s - Math.random() * 0.2 * s, gauss() * 0.03 * s, (0.0028 + Math.random() * 0.003) * s); }
  const fade = smooth(t, LOOP - 1.8, LOOP - 0.3);      // the landed grains settle into the heap before the next loop
  for (let i = 0; i < NF; i++) {
    const st = fState[i]; if (!st) continue;
    if (st === 1) {
      fVel[i * 3 + 1] -= grav * dt;
      fPos[i * 3] += fVel[i * 3] * dt; fPos[i * 3 + 1] += fVel[i * 3 + 1] * dt; fPos[i * 3 + 2] += fVel[i * 3 + 2] * dt;
      for (let k = 0; k < 3; k++) fRot[i * 3 + k] += fSpin[i * 3 + k] * dt;
      const fy = floorY(fPos[i * 3], fPos[i * 3 + 2]);
      if (fPos[i * 3 + 1] <= fy) {                     // lands: a short skid, then it stays on the heap
        fPos[i * 3 + 1] = fy + fSize[i * 3 + 1] * 0.6; fPos[i * 3] += gauss() * 0.08 * s; fPos[i * 3 + 2] += gauss() * 0.04 * s; fState[i] = 2;
      }
    }
    const k = st === 2 ? 1 - fade : 1;
    if (k <= 0.001) { fState[i] = 0; fallGrains.setMatrixAt(i, ZERO); continue; }
    _fq.setFromEuler(_fe.set(fRot[i * 3], fRot[i * 3 + 1], fRot[i * 3 + 2]));
    fallGrains.setMatrixAt(i, _fm.compose(_fp.set(fPos[i * 3], fPos[i * 3 + 1], fPos[i * 3 + 2]), _fq, _fs.set(fSize[i * 3] * k, fSize[i * 3 + 1] * k, fSize[i * 3 + 2] * k)));
  }
  fallGrains.instanceMatrix.needsUpdate = true;
}

// ---------- the move: driven by the scroll, closed and holding the load the whole time ----------
// Desktop: the grab travels from the left of the screen to the right over the hold. Phone: it rides down as you scroll.
const LOOP = 15;                                       // kept for the debug stepper
function grabAt(s, t) {                                // s: 0..1 through the chapter; t: seconds, for a gentle sway
  const H = fit.screenH, W = H * cam1.aspect;
  let x = 0, y = 0;
  if (cam1.aspect > 1) x = (lerp(0.2, 0.8, s) - 0.5) * W - fit.base.x;   // screen-left to screen-right
  else y = lerp(0.2, -0.2, s) * H;                                        // top to lower, over the hold
  y += Math.sin(t * 0.9) * 0.006 * H;                                     // hanging on its ropes
  return { x, y, theta: CLOSED, flow: 0, poured: 0, sway: Math.sin(t * 1.1) * 0.012 };
}

// =====================================================================================
// CHAPTER 2 — the bags (world origin)
// =====================================================================================
const bagsWorld = new THREE.Group(); scene.add(bagsWorld);
const floorMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, fog: true,
  uniforms: THREE.UniformsUtils.merge([THREE.UniformsLib.fog, { uColor: { value: INK }, uMouse: { value: new THREE.Vector2(999, 999) }, uTime: { value: 0 }, uSize: { value: 3.3 } }]),
  vertexShader: /* glsl */`
    #include <fog_pars_vertex>
    varying vec2 vXZ; varying float vEdge; varying float vDist;
    void main() {
      vec3 p = position;
      float r = length(p.xz - vec2(-2.0, -12.0));   // flat floor: no upward bend at the edges
      vXZ = p.xz; vEdge = r;
      vec4 mvPosition = modelViewMatrix * vec4(p, 1.0);
      vDist = -mvPosition.z;
      gl_Position = projectionMatrix * mvPosition;
      #include <fog_vertex>
    }`,
  fragmentShader: /* glsl */`
    #include <fog_pars_fragment>
    uniform vec3 uColor; uniform vec2 uMouse; uniform float uTime, uSize;
    varying vec2 vXZ; varying float vEdge; varying float vDist;
    float hexDist(vec2 p) { p = abs(p); return max(dot(p, normalize(vec2(1.0, 1.7320508))), p.x); }
    void main() {
      vec2 uv = vXZ / uSize;
      vec2 r = vec2(1.0, 1.7320508), h = r * 0.5;
      vec2 a = mod(uv, r) - h, b = mod(uv - h, r) - h;
      vec2 gv = dot(a, a) < dot(b, b) ? a : b;
      float d = 0.5 - hexDist(gv);
      float w = fwidth(d);
      float front = 1.0 - smoothstep(9.0, 38.0, vDist);
      float line = 1.0 - smoothstep(0.0, w * 1.3 + 0.003 + 0.007 * front, d);
      float inner = (1.0 - smoothstep(0.0, w * 1.2 + 0.002, abs(d - 0.055))) * (0.35 + 0.5 * front);
      vec2 cell = uv - gv;
      float near = smoothstep(5.5, 0.0, length(cell * uSize - uMouse));
      float shimmer = 0.5 + 0.5 * sin(uTime * 0.6 + cell.x * 1.7 + cell.y * 2.3);
      float alpha = (line + inner) * (0.12 + 0.62 * front + 0.05 * shimmer + 0.45 * near);
      alpha *= smoothstep(40.0, 16.0, vEdge);
      gl_FragColor = vec4(uColor, alpha);
      #include <fog_fragment>
    }`,
});
const floor = new THREE.Mesh(new THREE.PlaneGeometry(110, 110, 200, 200).rotateX(-Math.PI / 2), floorMat);
floor.position.y = -3.4; scene.add(floor);

const BAG_H = 4.1;
// the row slants across to the right (less depth), so a few bags cover the width
const PATH = { from: new THREE.Vector3(-9.5, 0.0, 6.5), to: new THREE.Vector3(24, 5.6, -14) };
const PATH_LEN = PATH.from.distanceTo(PATH.to);
const GAP = 7, S0 = PATH_LEN * 0.3, DRIFT = reduce ? 0.08 : 0.2, SCROLL_GAIN = 2.2;   // bags closer together (client, 2026-11-10; was 11.5), drifting slowly
const POOL = Math.ceil(PATH_LEN / GAP) + 2;
const bags = [];
const hash = k => { const x = Math.sin(k * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
async function loadBags() {
  let template;
  try {
    const gltf = await loader.loadAsync('assets/models/jumbo-bag.d.glb');
    const obj = gltf.scene;
    obj.traverse(o => { if (o.isMesh && o.material.map) o.material.map.anisotropy = 8; });
    const bb = new THREE.Box3().setFromObject(obj), size = bb.getSize(new THREE.Vector3()), c = bb.getCenter(new THREE.Vector3());
    obj.position.sub(c);
    const g = new THREE.Group(); g.add(obj); g.scale.setScalar(BAG_H / size.y);
    template = new THREE.Group(); template.add(g);
  } catch (e) { console.warn('bag model missing', e); template = new THREE.Mesh(new THREE.BoxGeometry(BAG_H, BAG_H, BAG_H), new THREE.MeshStandardMaterial({ color: 0x5a6646 })); }
  for (let i = 0; i < POOL; i++) {
    const b = template.clone(true), mats = [];
    b.traverse(o => { if (o.isMesh) { o.material = o.material.clone(); o.material.envMapIntensity = 0.9; addRim(o.material, { desat: 0.45 }); mats.push(o.material); } });
    b.userData.mats = mats; b.visible = false; bagsWorld.add(b); bags.push(b);
  }
}
function placeBag(b, k, sPos, t) {
  b.position.lerpVectors(PATH.from, PATH.to, sPos / PATH_LEN);
  const ph = hash(k) * 6.283;
  b.position.y += Math.sin(t * 0.7 + ph) * 0.18;
  const yaw = -0.5 + (hash(k + 7) - 0.5) * 0.7, spin = (hash(k + 13) < 0.5 ? -1 : 1) * (0.05 + hash(k + 3) * 0.05);
  b.rotation.set(0.1 + Math.sin(t * 0.45 + ph) * 0.05, yaw + t * spin, Math.sin(t * 0.38 + ph * 1.3) * 0.06);
  const op = Math.min(smooth(sPos, 0, 2), 1 - smooth(sPos, PATH_LEN * 0.62, PATH_LEN * 0.92));
  for (const m of b.userData.mats) { m.opacity = op; m.transparent = op < 0.999; m.side = op < 0.999 ? THREE.FrontSide : THREE.DoubleSide; }
}
function updateBags(D, t) {
  for (const b of bags) b.visible = false;
  if (!bags.length) return;
  // every bag on the same spacing along the belt (the first two used to sit on their own spacing, so a new bag arrived
  // half inside the second one: the "two bags" glitch)
  const kLo = Math.max(0, Math.ceil((D + S0 - PATH_LEN) / GAP)), kHi = Math.floor((D + S0) / GAP);
  for (let k = kLo; k <= kHi; k++) { const s = D + S0 - k * GAP; if (s < 0 || s > PATH_LEN) continue; const b = bags[k % POOL]; b.visible = true; placeBag(b, k, s, t); }
}

// =====================================================================================
// CAMERA, SCROLL, COMPOSITING
// =====================================================================================
const RIG = { bags: { pos: new THREE.Vector3(1.0, 2.6, 13.5), look: new THREE.Vector3(2.0, 1.6, -6), roll: -0.2, fov: 34 } };
setPalette(0xeee3c7, BG);
const EXTRA = { iso: buildIso(), ibc: buildIbc(), chips: buildChips() };
for (const k in EXTRA) { scene.add(EXTRA[k].world); RIG[k] = EXTRA[k].rig; }
// the commodities hub (?mode=all) runs one long scroll through all five product groups, in the customer's order;
// each chapter's share of the scroll is its number of products
const CHAPTERS = [{ id: 'grab', n: 8 }, { id: 'bags', n: 4 }, { id: 'iso', n: 3 }, { id: 'ibc', n: 4 }, { id: 'chips', n: 2 }];
{ const total = CHAPTERS.reduce((a, c) => a + c.n, 0); let acc = 0; for (const c of CHAPTERS) { c.from = acc / total; acc += c.n; c.to = acc / total; } }
const chapterAt = p => CHAPTERS.find(c => p < c.to) || CHAPTERS[CHAPTERS.length - 1];
const BAGS_SPAN = 24;                                 // how far the bag belt travels over its chapter in ?mode=all (slower: about two bags, user 2026-11-06)
const SWAP = 0.38;                                   // scroll progress where the picture cuts from the ship to the bags
if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
scrollTo(0, 0);
let scrollTarget = 0, scrollSmooth = 0;
// embed mode (?mode=grab|bags): a group page hosts this scene in an iframe and posts its own scroll progress (0..1);
// the page UI is hidden and only that chapter plays
const EMBED = new URLSearchParams(location.search).get('mode');
if (EMBED) document.documentElement.classList.add('embed');
function embedScroll(p) {
  const max = Math.max(1, document.documentElement.scrollHeight - innerHeight);
  if (EMBED === 'all') return max * p;
  return EMBED === 'bags' ? max * (SWAP + 0.09 + p * (1 - SWAP - 0.09)) : max * SWAP * 0.98 * p;
}
let grabSideTarget = 1, grabSide = 1;
if (EMBED) { scrollTarget = scrollSmooth = embedScroll(0); addEventListener('message', e => { if (e.data && e.data.type === 'hero-progress') { scrollTarget = embedScroll(Math.min(1, Math.max(0, +e.data.p || 0))); if (e.data.jump) scrollSmooth = scrollTarget; /* a new window cuts straight to its chapter */ if (e.data.grabSide !== undefined) grabSideTarget = +e.data.grabSide; } }); }
else addEventListener('scroll', () => { scrollTarget = scrollY; }, { passive: true });
const caps = [...document.querySelectorAll('.cap')], hint = document.getElementById('hint'), veil = document.getElementById('veil');

const mouse = new THREE.Vector2(), ndc = new THREE.Vector2(), ray = new THREE.Raycaster();
const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 3.4), hit = new THREE.Vector3();
addEventListener('pointermove', e => {
  mouse.set(e.clientX / innerWidth - 0.5, e.clientY / innerHeight - 0.5);
  ndc.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  ray.setFromCamera(ndc, camera);
  if (ray.ray.intersectPlane(groundPlane, hit)) floorMat.uniforms.uMouse.value.set(hit.x, hit.z);
});
function frame() { const a = innerWidth / innerHeight; camera.aspect = a; camera.fov = a < 1 ? 58 : RIG.bags.fov; camera.updateProjectionMatrix(); }

// chapter 1 compositing: the drawing (sulphur whitened) + the 3D grab drawn in the same engraved style
const POST_DPR = Math.min(devicePixelRatio, 2);   // full retina resolution (user found 1.5 blurry)
const rtColor = new THREE.WebGLRenderTarget(1, 1, { type: THREE.HalfFloatType, samples: 4 });
const rtNormal = new THREE.WebGLRenderTarget(1, 1, { type: THREE.HalfFloatType });
rtNormal.depthTexture = new THREE.DepthTexture(1, 1);
const normalMat = new THREE.MeshNormalMaterial();
const compMat = new THREE.ShaderMaterial({
  uniforms: { tPlate: { value: plateTex }, tColor: { value: rtColor.texture }, tNormal: { value: rtNormal.texture }, tDepth: { value: rtNormal.depthTexture },
    uView: { value: new THREE.Vector4(0.5, 0.5, 1, 1) }, uRes: { value: new THREE.Vector2() }, uNear: { value: 0.1 }, uFar: { value: 200 },
    uTime: { value: 0 }, uInk: { value: new THREE.Color(0xe9dfc3) } },
  vertexShader: 'varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }',
  fragmentShader: /* glsl */`
    uniform sampler2D tPlate, tColor, tNormal, tDepth; uniform vec4 uView; uniform vec2 uRes; uniform float uNear, uFar, uTime; uniform vec3 uInk;
    varying vec2 vUv;
    float linDepth(vec2 uv) { float z = texture2D(tDepth, uv).x * 2.0 - 1.0; return (2.0 * uNear * uFar) / (uFar + uNear - z * (uFar - uNear)); }
    vec3 nrm(vec2 uv) { return texture2D(tNormal, uv).xyz * 2.0 - 1.0; }
    float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
    void main() {
      // the drawing, cover-fitted, with the sulphur lifted towards white
      vec2 puv = vec2(uView.x, 1.0 - uView.y) + (vUv - 0.5) * uView.zw;
      vec3 plate = texture2D(tPlate, puv).rgb;
      float pl = dot(plate, vec3(0.299, 0.587, 0.114));
      float sand = smoothstep(0.22, 0.42, pl);
      plate = mix(plate, vec3(pl) * vec3(1.06, 1.05, 1.0) * 1.22, sand * 0.75);
      // the 3D grab in the same engraved style: ink edges, sepia-steel tone
      vec2 px = 1.0 / uRes;
      float raw = texture2D(tDepth, vUv).x;
      bool obj = raw < 0.99999;
      vec3 col = texture2D(tColor, vUv).rgb;
      float sandC = step(0.06, col.b - col.r);
      float d = linDepth(vUv), en = 0.0, ed = 0.0; vec3 n0 = nrm(vUv);
      for (int i = -1; i <= 1; i++) for (int j = -1; j <= 1; j++) {
        if (i == 0 && j == 0) continue;
        vec2 o = vec2(float(i), float(j)) * px * 1.2;
        float rawN = texture2D(tDepth, vUv + o).x;
        if (obj && rawN < 0.99999) en = max(en, 1.0 - dot(n0, nrm(vUv + o)));
        if (obj != (rawN < 0.99999)) { vec3 nb = texture2D(tColor, vUv + o).rgb; float sandN = obj ? sandC : step(0.06, nb.b - nb.r); ed = max(ed, 1.0 - 0.9 * sandN); }
        else if (obj) ed = max(ed, abs(linDepth(vUv + o) - d) / max(d, 0.001) * 30.0);
      }
      float edge = max(smoothstep(0.16, 0.45, en), smoothstep(0.35, 1.0, ed));
      edge *= 1.0 - 0.9 * sandC;                                                  // no ink on the sulphur itself
      float lum = dot(col, vec3(0.299, 0.587, 0.114));
      vec3 steel = mix(vec3(0.022, 0.026, 0.018), vec3(0.42, 0.40, 0.27), smoothstep(0.0, 0.5, pow(lum, 0.8)))
                 + vec3(0.30, 0.28, 0.20) * pow(max(lum, 0.0), 3.0);               // khaki plate steel, cream glints on the edges
      vec3 g = mix(col * 0.4, steel, 0.9);
      vec2 fc = gl_FragCoord.xy;
      float h1 = smoothstep(0.42, 0.5, abs(fract((fc.x + fc.y) / 4.0) - 0.5));
      g *= 1.0 - 0.35 * (1.0 - smoothstep(0.03, 0.22, lum)) * h1;
      float isSand = obj ? smoothstep(0.03, 0.09, col.b - col.r) : 0.0;          // the tagged sulphur in the jaws
      vec3 sandCol = mix(vec3(0.22, 0.21, 0.18), vec3(0.74, 0.71, 0.62), smoothstep(0.06, 0.65, lum));   // the heap's own beige-white, shaded
      g = mix(g, sandCol, isSand);
      vec3 outc = obj ? g : plate;
      outc = mix(outc, uInk * 0.9, edge * 0.65);
      outc += (hash(fc + fract(uTime) * 91.0) - 0.5) * 0.02;
      gl_FragColor = vec4(outc, 1.0);
      #include <colorspace_fragment>
    }`,
  depthTest: false, depthWrite: false,
});
const postScene = new THREE.Scene(), postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
postScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), compMat));
function sizePost() {
  const w = Math.round(innerWidth * POST_DPR), h = Math.round(innerHeight * POST_DPR);
  rtColor.setSize(w, h); rtNormal.setSize(w, h); compMat.uniforms.uRes.value.set(w, h);
  layoutPlate(); fitGrab();
}
function renderFrame() {
  if (!state.inHold) { renderer.setRenderTarget(null); renderer.render(scene, camera); return; }
  const u = compMat.uniforms;
  u.uView.value.set(plateView.cx, plateView.cy, plateView.sx, plateView.sy); u.uNear.value = cam1.near; u.uFar.value = cam1.far; u.uTime.value = simT;
  renderer.setRenderTarget(rtColor); renderer.render(scene1, cam1);
  scene1.overrideMaterial = normalMat; renderer.setRenderTarget(rtNormal); renderer.render(scene1, cam1); scene1.overrideMaterial = null;
  renderer.setRenderTarget(null); renderer.render(postScene, postCam);
  renderer.autoClear = false; renderer.render(pourScene, cam1); renderer.autoClear = true;
}
addEventListener('resize', () => { renderer.setSize(innerWidth, innerHeight); frame(); sizePost(); });
frame();

const clock = new THREE.Clock();
const camPos = new THREE.Vector3(), camLook = new THREE.Vector3();
let bagDrift = 0, simT = 0, loopT = 0;
const state = {};
function update(dt) {
  simT += dt; const t = simT;
  scrollSmooth += (scrollTarget - scrollSmooth) * Math.min(1, 0.08 * dt * 60);
  const max = Math.max(1, document.documentElement.scrollHeight - innerHeight);
  const p = scrollSmooth / max;
  for (const c of caps) c.classList.toggle('show', p >= +c.dataset.from && p < +c.dataset.to);
  hint.classList.toggle('gone', scrollSmooth > 40);
  veil.style.opacity = (smooth(p, SWAP - 0.08, SWAP) * (1 - smooth(p, SWAP, SWAP + 0.07))).toFixed(3);
  if (EMBED === 'all') return updateAll(p, t, dt);
  bagsWorld.visible = true;
  const inHold = p < SWAP;
  state.p = p; state.inHold = inHold;
  if (inHold) {
    loopT = (loopT + dt) % LOOP;
    const g = grabAt(THREE.MathUtils.clamp(p / SWAP, 0, 1), t);
    grab.position.set(fit.base.x + g.x, fit.base.y + g.y, fit.base.z);
    grab.rotation.set(GRAB_TILT, 0, g.sway);
    setJaws(g.theta);
    updateLoad(g);
    stepPour(dt, g.flow); stepGrains(dt, g, loopT);
    state.loopT = loopT;
  } else {
    bagDrift += DRIFT * dt;
    const into = Math.max(0, scrollSmooth - SWAP * max);
    updateBags(bagDrift + (into / 100) * SCROLL_GAIN, t);
    floorMat.uniforms.uTime.value = t;
    const m = reduce ? 0 : 1;
    camera.position.set(RIG.bags.pos.x + mouse.x * 1.2 * m, RIG.bags.pos.y - mouse.y * 0.6 * m, RIG.bags.pos.z);
    camera.lookAt(RIG.bags.look); camera.rotateZ(RIG.bags.roll);
  }
}
function placeCamera(rig) {
  const m = reduce ? 0 : 1;
  camera.position.set(rig.pos.x + mouse.x * 1.2 * m, rig.pos.y - mouse.y * 0.6 * m, rig.pos.z);
  camera.lookAt(rig.look); camera.rotateZ(rig.roll);
}
function updateAll(p, t, dt) {
  const c = chapterAt(p), lp = THREE.MathUtils.clamp((p - c.from) / (c.to - c.from), 0, 1);
  // the picture dips to the paper colour at every chapter boundary
  let v = 0; for (const b of CHAPTERS.slice(1)) v = Math.max(v, smooth(p, b.from - 0.018, b.from) * (1 - smooth(p, b.from, b.from + 0.018)));
  veil.style.opacity = v.toFixed(3);
  state.p = p; state.inHold = c.id === 'grab'; state.chapter = c.id; state.lp = lp;
  bagsWorld.visible = c.id === 'bags'; for (const k in EXTRA) EXTRA[k].world.visible = c.id === k;
  floorMat.uniforms.uTime.value = t;
  if (c.id === 'grab') {
    loopT = (loopT + dt) % LOOP;
    // the grab keeps to the side opposite the product being read (text left -> grab right, and back),
    // swinging across as the next product comes up
    grabSide += (grabSideTarget - grabSide) * Math.min(1, dt * 1.8);
    const g = grabAt(grabSide * grabSide * (3 - 2 * grabSide), t);
    grab.position.set(fit.base.x + g.x, fit.base.y + g.y, fit.base.z); grab.rotation.set(GRAB_TILT, 0, g.sway);
    setJaws(g.theta); updateLoad(g); stepPour(dt, g.flow); stepGrains(dt, g, loopT);
  } else if (c.id === 'bags') {
    bagDrift += DRIFT * dt;
    updateBags(bagDrift + lp * BAGS_SPAN, t);
    placeCamera(RIG.bags);
  } else {
    EXTRA[c.id].update(lp, t, dt);
    placeCamera(RIG[c.id]);
  }
}
let paused = false;
addEventListener('message', e => { if (e.data && e.data.type === 'scene-pause') { paused = !!e.data.v; clock.getDelta(); } });   // host hides this copy: skip all work
function tick() { if (!paused) { update(Math.min(clock.getDelta(), 0.05)); renderFrame(); } requestAnimationFrame(tick); }
sizePost();
tick();

await Promise.all([loadGrab(), loadBags()]);
document.getElementById('loading').classList.add('done');
window.__debug = { scene, scene1, camera, cam1, renderer, bags, grab, state, parts, setJaws, fit, heapTop, plateView, worldToPlate, EXTRA, RIG,
  // for testing in a background tab, where requestAnimationFrame is paused: jump scroll / loop time and run forward
  floorY, grains: () => ({ fPos, fState, fSize }), plateToWorld, worldToPlate, cam1, model,
  advance(seconds, scrollPx, atLoopT) { if (scrollPx !== undefined) { scrollTarget = scrollPx; scrollSmooth = scrollPx; } if (atLoopT !== undefined) loopT = atLoopT; for (let i = 0; i < seconds * 60; i++) update(1 / 60); renderFrame(); },
  maxScroll: () => document.documentElement.scrollHeight - innerHeight };
