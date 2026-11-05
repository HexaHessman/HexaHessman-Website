// A part of the globe at the side of the team lookbook: the same blueprint wireframe Earth as the Contact page,
// sitting half off the edge of the stage. Whenever the person at the front changes (the 'team-change' event
// from team-lookbook.js), the globe turns so their office faces us, with a pin and a small city label on it.
// Mounts into .tl-globe (a canvas and a label) inside <section id="team" data-people="[...]">.
import * as THREE from 'three';

const sec = document.getElementById('team'), host = sec && sec.querySelector('.tl-globe'); if (!host) throw new Error('no .tl-globe');
const canvas = host.querySelector('canvas'), label = host.querySelector('.tl-globe-label');
const people = JSON.parse(sec.dataset.people || '[]');
const offices = [...new Map(people.map(p => [p.office, p])).values()];   // one pin per office
const INK = 0xeee3c7;
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 50); camera.position.set(0, 0, 4.3); camera.lookAt(0, 0, 0);
const globe = new THREE.Group(); scene.add(globe);
const R = 1;
const toVec = (lat, lon, r = R) => { const phi = THREE.MathUtils.degToRad(90 - lat), th = THREE.MathUtils.degToRad(lon + 180); return new THREE.Vector3(-r * Math.sin(phi) * Math.cos(th), r * Math.cos(phi), r * Math.sin(phi) * Math.sin(th)); };

// the body hides lines on the far side; a faint rim so the sphere reads against the page
globe.add(new THREE.Mesh(new THREE.SphereGeometry(R * 0.995, 64, 48), new THREE.MeshBasicMaterial({ color: 0x14372a, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 })));
globe.add(new THREE.Mesh(new THREE.SphereGeometry(R, 64, 48), new THREE.ShaderMaterial({ transparent: true, depthWrite: false, uniforms: { c: { value: new THREE.Color(INK) } },
  vertexShader: `varying vec3 vN, vV; void main(){ vN = normalize(normalMatrix * normal); vec4 mv = modelViewMatrix * vec4(position,1.0); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }`,
  fragmentShader: `uniform vec3 c; varying vec3 vN, vV; void main(){ float f = pow(1.0 - max(dot(vN, vV), 0.0), 3.2); gl_FragColor = vec4(c, f * 0.35); }` })));
// graticule every 15°
{ const pts = [];
  for (let lat = -75; lat <= 75; lat += 15) for (let lon = -180; lon < 180; lon += 3) pts.push(toVec(lat, lon, R * 1.001), toVec(lat, lon + 3, R * 1.001));
  for (let lon = -180; lon < 180; lon += 15) for (let lat = -90; lat < 90; lat += 3) pts.push(toVec(lat, lon, R * 1.001), toVec(lat + 3, lon, R * 1.001));
  globe.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: INK, transparent: true, opacity: 0.13 }))); }
// land outlines, drawn on as they arrive
const landMat = new THREE.LineBasicMaterial({ color: INK, transparent: true, opacity: 0 });
let landLines = null, landTotal = 0, drawT = 0;
(async () => {
  try {
    const [topo] = await Promise.all([fetch('/assets/vendor/land-110m.json').then(r => r.json()), loadTopojson()]);
    const mesh = window.topojson.mesh(topo, topo.objects.land), pts = [];
    for (const line of mesh.coordinates) for (let i = 1; i < line.length; i++) pts.push(toVec(line[i - 1][1], line[i - 1][0], R * 1.002), toVec(line[i][1], line[i][0], R * 1.002));
    const geo = new THREE.BufferGeometry().setFromPoints(pts); geo.setDrawRange(0, 0);
    landLines = new THREE.LineSegments(geo, landMat); landTotal = pts.length; globe.add(landLines);
  } catch (e) { console.warn('land outlines unavailable', e); }
})();
function loadTopojson() { return new Promise((res, rej) => { if (window.topojson) return res(); const s = document.createElement('script'); s.src = '/assets/vendor/topojson-client.min.js'; s.onload = res; s.onerror = rej; document.head.appendChild(s); }); }

// a pin per office: a dot and a ring; the one in focus grows a pulsing halo and a stem
const pins = offices.map(o => {
  const g = new THREE.Group(); const p = toVec(o.lat, o.lon, R * 1.003); g.position.copy(p); g.lookAt(p.clone().multiplyScalar(2));
  const dot = new THREE.Mesh(new THREE.CircleGeometry(0.012, 20), new THREE.MeshBasicMaterial({ color: INK }));
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.03, 0.034, 40), new THREE.MeshBasicMaterial({ color: INK, transparent: true, opacity: 0.5, side: THREE.DoubleSide }));
  const halo = new THREE.Mesh(new THREE.RingGeometry(0.055, 0.058, 48), new THREE.MeshBasicMaterial({ color: INK, transparent: true, opacity: 0, side: THREE.DoubleSide }));
  const stem = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3(0, 0, 0.14)]), new THREE.LineBasicMaterial({ color: INK, transparent: true, opacity: 0.4 }));
  g.add(dot, ring, halo, stem); globe.add(g);
  return { id: o.office, g, ring, halo, stem };
});

// turning: the office in focus lands a little left of the globe's centre, the part of the globe that is on screen
// (the globe's centre sits at the right edge below the stage, so the upper left of the disc is the part that shows)
let activeId = null;
const targetQ = new THREE.Quaternion(), FACE = new THREE.Vector3(0.55, 1.0, 1).normalize();
function focus(p) { if (!p) return; activeId = p.office; label.textContent = p.city; targetQ.setFromUnitVectors(toVec(p.lat, p.lon, 1), FACE); }
document.addEventListener('team-change', e => focus(e.detail));
focus(window.__teamCurrent || people[0]);
if (reduce) globe.quaternion.copy(targetQ);

// the renderer: a browser with many 3D tabs open can refuse a WebGL context for a while, so keep trying rather
// than giving up (three.js itself recovers a context that is lost and handed back later)
let renderer = null, tries = 0;
function makeRenderer() {
  if (renderer) return true;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true }); renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5)); size(); return true; }   // (the canvas is big, so a modest pixel ratio)
  catch (e) { tries++; if (tries === 1) console.warn('team globe: no WebGL context yet, retrying', e.message || e); return false; }
}
function size() { const w = host.clientWidth, h = host.clientHeight; if (renderer) renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
new ResizeObserver(size).observe(host); size();
let visible = true; new IntersectionObserver(([e]) => { visible = e.isIntersecting; }, { threshold: 0.01 }).observe(sec);
const _p = new THREE.Vector3(), _n = new THREE.Vector3(), camDir = new THREE.Vector3(), clock = new THREE.Clock();
function tick() {
  if (!makeRenderer()) { if (tries < 60) setTimeout(tick, 1500); return; }
  requestAnimationFrame(tick);
  const dt = Math.min(clock.getDelta(), 0.05), now = performance.now();
  if (!visible) return;
  if (landLines && drawT < 1) { drawT = Math.min(1, drawT + dt / (reduce ? 0.01 : 2.4)); landLines.geometry.setDrawRange(0, Math.floor(landTotal * drawT)); landMat.opacity = 0.85 * Math.min(1, drawT * 2); }
  globe.quaternion.slerp(targetQ, reduce ? 1 : 1 - Math.pow(0.004, dt));
  camera.getWorldDirection(camDir);
  const w = host.clientWidth, h = host.clientHeight;
  pins.forEach(p => {
    p.g.getWorldPosition(_p); _n.copy(_p).normalize(); const facing = Math.max(0, -_n.dot(camDir));
    const on = p.id === activeId;
    p.ring.material.opacity = THREE.MathUtils.lerp(p.ring.material.opacity, (on ? 0.95 : 0.5) * facing, 0.15);
    p.halo.material.opacity = THREE.MathUtils.lerp(p.halo.material.opacity, (on ? 0.6 + 0.3 * Math.sin(now / 300) : 0) * facing, 0.15);
    p.stem.material.opacity = (on ? 0.8 : 0.3) * facing;
    p.g.scale.setScalar(THREE.MathUtils.lerp(p.g.scale.x, on ? 1.7 : 1, 0.15));
    if (on) {
      _p.project(camera); const x = (_p.x * 0.5 + 0.5) * w, y = (-_p.y * 0.5 + 0.5) * h;
      label.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px)`;
      label.style.opacity = facing > 0.2 ? String(Math.min(1, (facing - 0.2) * 3)) : '0';
    }
  });
  renderer.render(scene, camera);
}
tick();
