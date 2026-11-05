// Extra chapters for the commodities scroll, drawn in the site's blueprint style. Each builder returns
// { world, rig, update(lp, t, dt) } where lp is 0..1 through the chapter and t is seconds.
// ISO tank (industrial chemicals) and IBC totes (petroleum & oilfield) are 3D models made from reference
// images (Tripo, Draco-compressed); the wood chips (biomass) are a particle heap under a chute.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

let INK = 0xeee3c7, BG = 0x0f2a1e;
export function setPalette(ink, bg) { INK = ink; BG = bg; }

const loader = new GLTFLoader();
const draco = new DRACOLoader(); draco.setDecoderPath('https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/libs/draco/gltf/'); loader.setDRACOLoader(draco);

const fillMat = () => new THREE.MeshBasicMaterial({ color: BG, polygonOffset: true, polygonOffsetFactor: 1.5, polygonOffsetUnits: 1.5 });
const lineMat = (opacity = 0.85) => new THREE.LineBasicMaterial({ color: INK, transparent: true, opacity });
/** a drawn solid: filled with the paper colour, outlined on its sharp edges */
function drawn(geo, { angle = 28, opacity = 0.85, fill = true } = {}) {
  const g = new THREE.Group();
  if (fill) g.add(new THREE.Mesh(geo, fillMat()));
  g.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo, angle), lineMat(opacity)));
  return g;
}
/** a thin bar between two points */
function bar(a, b, r = 0.03, opacity = 0.7) {
  const d = new THREE.Vector3().subVectors(b, a), len = d.length();
  const m = drawn(new THREE.BoxGeometry(r * 2, len, r * 2), { opacity, angle: 60 });
  m.position.copy(a).addScaledVector(d, 0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.clone().normalize());
  return m;
}
const V = (x, y, z) => new THREE.Vector3(x, y, z);

/** a scanned model in the engraving look: khaki steel shading with ink lines along its creases */
const steelMat = () => new THREE.MeshStandardMaterial({ color: 0x9c9d82, roughness: 0.72, metalness: 0.28, envMapIntensity: 0.8 });
function loadDrawn(url, { height, onReady }) {
  const g = new THREE.Group();
  loader.load(url, gltf => {
    const box = new THREE.Box3().setFromObject(gltf.scene), size = box.getSize(new THREE.Vector3()), ctr = box.getCenter(new THREE.Vector3());
    const s = height / size.y;
    gltf.scene.traverse(o => {
      if (!o.isMesh) return;
      o.material = steelMat();
      const edges = new THREE.LineSegments(new THREE.EdgesGeometry(o.geometry, 32), lineMat(0.5));
      o.add(edges);
    });
    gltf.scene.position.copy(ctr).multiplyScalar(-s); gltf.scene.position.y += height / 2; gltf.scene.scale.setScalar(s);
    g.add(gltf.scene); onReady && onReady(size.clone().multiplyScalar(s));
  }, undefined, e => console.warn('model failed', url, e));
  return g;   // origin at the bottom centre of the model once loaded
}

// ---------- ISO tank container ----------
export function buildIso() {
  const world = new THREE.Group(); world.visible = false;
  const H = 2.5;
  const tank = loadDrawn('/assets/models/iso.d.glb', { height: H }); world.add(tank);
  const rig = { pos: V(0.5, 1.6, 13.0), look: V(0, -0.2, 0), roll: -0.04, fov: 34 };
  return { world, rig, update(lp, t) {
    // rolls in from the right, turning slowly to show its length, then settles three-quarters on
    const e = 1 - Math.pow(1 - Math.min(1, lp * 1.3), 3);
    const narrow = innerWidth < innerHeight, sc = narrow ? 0.9 : 1.35;
    tank.scale.setScalar(sc);
    tank.position.set(THREE.MathUtils.lerp(10, narrow ? 0.3 : -0.2, e), -3.4 + Math.sin(t * 0.5) * 0.02, THREE.MathUtils.lerp(-4, narrow ? -0.5 : 2.6, e));
    tank.rotation.set(0, THREE.MathUtils.lerp(-0.9, -0.42, e) + Math.sin(t * 0.18) * 0.03, 0);
  } };
}

// ---------- IBC totes: three of them slide in and park ----------
export function buildIbc() {
  const world = new THREE.Group(); world.visible = false;
  const totes = [0, 1, 2].map(() => loadDrawn('/assets/models/ibc.d.glb', { height: 2.0 }));
  for (const t of totes) world.add(t);
  const rig = { pos: V(0.6, 1.9, 12.5), look: V(0.6, -0.9, 0), roll: -0.06, fov: 34 };
  return { world, rig, update(lp, t) {
    const e = 1 - Math.pow(1 - Math.min(1, lp * 1.25), 3);
    const narrow = innerWidth < innerHeight;
    totes.forEach((g, i) => {
      const x = THREE.MathUtils.lerp(-9, narrow ? 0.2 : -1.8, e) + i * (narrow ? 2.0 : 2.9), z = (narrow ? -1.6 : 0.6) - i * 2.2;
      g.position.set(x, -3.4 + Math.sin(t * 0.6 + i) * 0.01, z); g.rotation.y = -0.35 + i * 0.05 + Math.sin(t * 0.15 + i) * 0.02;
    });
  } };
}

// ---------- wood chips: a chute pours chips that heap up as you scroll ----------
export function buildChips() {
  const world = new THREE.Group(); world.visible = false;
  const N = 2200, FLOOR = -3.4;
  const chute = drawn(new THREE.BoxGeometry(0.9, 0.25, 3.6), { angle: 60, opacity: 0.85 }); chute.position.set(-3.2, 2.6, -1.2); chute.rotation.set(0.55, 0.35, 0.1); world.add(chute);
  world.add(bar(V(-4.2, 3.6, -2.4), V(-4.2, FLOOR, -2.4), 0.05, 0.6));
  const geo = new THREE.BoxGeometry(0.36, 0.06, 0.22);
  const chips = new THREE.InstancedMesh(geo, new THREE.MeshStandardMaterial({ color: 0xd9cfb3, roughness: 0.95, metalness: 0, flatShading: true }), N);
  chips.frustumCulled = false; world.add(chips);
  const pos = new Float32Array(N * 3), vel = new Float32Array(N * 3), rot = new Float32Array(N * 3), state = new Uint8Array(N), tgt = new Float32Array(N * 2);
  const pileAt = V(-0.6, FLOOR, -0.4), mouth = V(-2.6, 2.0, -0.3);
  const m = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), p = new THREE.Vector3(), s = new THREE.Vector3(1, 1, 1);
  const ZERO = new THREE.Matrix4().set(0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,1);
  for (let i = 0; i < N; i++) chips.setMatrixAt(i, ZERO);
  let released = 0;
  const gauss = () => (Math.random() + Math.random() + Math.random() - 1.5) / 1.5;
  const pileH = (x, z, n) => { const r = Math.hypot(x - pileAt.x, (z - pileAt.z) / 0.8); const H = 0.4 + 2.6 * n, base = 1.2 + 2.6 * n; return FLOOR + Math.max(0, H * (1 - r / base)); };
  const pile = new THREE.Mesh(new THREE.ConeGeometry(1, 1, 40, 1, true), fillMat()); pile.position.copy(pileAt); world.add(pile);
  const rig = { pos: V(0.4, 1.4, 12.5), look: V(-0.6, -1.4, -0.4), roll: -0.03, fov: 34 };
  return { world, rig, chips, pos, state: () => state, released: () => released, pileH, update(lp, t, dt = 1 / 60) {
    const n = Math.min(1, lp * 1.15);
    const want = Math.floor(n * N);
    for (; released < want; released++) { const i = released; pos[i*3] = mouth.x + gauss() * 0.3; pos[i*3+1] = mouth.y + Math.random() * 0.2; pos[i*3+2] = mouth.z + gauss() * 0.25;
      vel[i*3] = 1.6 + gauss() * 0.5; vel[i*3+1] = -0.4 + gauss() * 0.3; vel[i*3+2] = gauss() * 0.3; rot[i*3] = Math.random() * 6; rot[i*3+1] = Math.random() * 6; rot[i*3+2] = Math.random() * 6; state[i] = 1; }
    const H = 0.4 + 2.6 * n, base = 1.2 + 2.6 * n; pile.scale.set(base, H, base * 0.8); pile.position.y = FLOOR + H / 2; pile.visible = n > 0.02;
    for (let i = 0; i < released; i++) {
      if (state[i] === 1) {
        vel[i*3+1] -= 9 * dt; pos[i*3] += vel[i*3] * dt; pos[i*3+1] += vel[i*3+1] * dt; pos[i*3+2] += vel[i*3+2] * dt;
        rot[i*3] += 4 * dt; rot[i*3+2] += 3 * dt;
        const floor = pileH(pos[i*3], pos[i*3+2], n);
        if (pos[i*3+1] <= floor + 0.03) {           // lands, then rolls down the slope to its place on the heap
          pos[i*3+1] = floor + 0.03; state[i] = 3; rot[i*3] = gauss() * 0.4; rot[i*3+2] = gauss() * 0.4;
          const a = Math.random() * Math.PI * 2, r = base * (0.08 + 0.9 * Math.sqrt(Math.random()));
          tgt[i*2] = pileAt.x + Math.cos(a) * r; tgt[i*2+1] = pileAt.z + Math.sin(a) * r * 0.8;
        }
      } else if (state[i] === 3) {
        pos[i*3] += (tgt[i*2] - pos[i*3]) * Math.min(1, 6 * dt); pos[i*3+2] += (tgt[i*2+1] - pos[i*3+2]) * Math.min(1, 6 * dt);
        pos[i*3+1] = pileH(pos[i*3], pos[i*3+2], n) + 0.03; rot[i*3+1] += 2 * dt;
        if (Math.abs(tgt[i*2] - pos[i*3]) + Math.abs(tgt[i*2+1] - pos[i*3+2]) < 0.02) state[i] = 2;
      } else {
        pos[i*3+1] = pileH(pos[i*3], pos[i*3+2], n) + 0.03;   // resting chips ride up with the growing heap
      }
      q.setFromEuler(e.set(rot[i*3], rot[i*3+1], rot[i*3+2]));
      chips.setMatrixAt(i, m.compose(p.set(pos[i*3], pos[i*3+1], pos[i*3+2]), q, s));
    }
    chips.instanceMatrix.needsUpdate = true;
    chute.rotation.z = 0.1 + Math.sin(t * 1.3) * 0.01;
  } };
}
