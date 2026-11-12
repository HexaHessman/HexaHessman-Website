// Contact page globe: a blueprint-style wireframe Earth (cream lines on dark green) with a pin for each
// HexaHessman office. Picking an office turns the globe to face it and shows who is in charge there.
// Mounts into <section id="globe">. Country outlines come from world-atlas (TopoJSON) at runtime.
import * as THREE from 'three';

const P = (slug, name, role) => ({ slug, name, role, email: slug.split('-').map(w => w[0].toUpperCase() + w.slice(1)).join('.') + '@HexaHessman.com' });
const OFFICES = [
  { id: 'sg', country: 'Singapore', entity: 'Headquarters', address: '39 Arab Street, Singapore 199738', extra: 'Warehouse: 10 Buroh Street, West Connect Building, Singapore 627564', lat: 1.3005, lon: 103.859,
    leads: [P('hafriz-razif', 'Hafriz Razif', 'Chief Executive Officer'), P('aizat-amin', 'Aizat Amin', 'Head of Engineering Solutions'), P('adam-yeoh', 'Adam Yeoh', 'Head of Commodity Supply'), P('azmi-mahmood', 'Azmi Mahmood', 'Principal Advisor')] },
  { id: 'id', country: 'Indonesia', entity: 'PT. HexaHessman Indonesia', address: 'The CEO Building Level 12, Jl. TB Simatupang No. 18 C, Jakarta Selatan 12430', lat: -6.29, lon: 106.80,
    leads: [P('krishna-hartono', 'Krishna Hartono', 'Regional Business Director'), P('yos-rizaldy', 'Yos Rizaldy', 'Regional Business Director')] },
  { id: 'kr', country: 'South Korea', entity: 'HexaHessman Korea', address: '#619, 87 Ogeum-ro, Songpa-gu, Seoul 05542', lat: 37.505, lon: 127.11, leads: [P('eddie-jeong', 'Eddie Jeong', 'Regional Business Director')] },
  { id: 'my', country: 'Malaysia', entity: 'HexaHessman Sdn Bhd', address: 'Unit 9-6, Binjai 8 Premium Soho, 2 Lorong Binjai, 50450 Kuala Lumpur', lat: 3.158, lon: 101.72, leads: [P('anuar-ebrahim', 'Anuar Ebrahim', 'Director of Trading'), P('zulkurnain-rahman', 'Zulkurnain Rahman', 'Principal Advisor')] },
  { id: 'th', country: 'Thailand', entity: 'HexaHessman Thailand', address: '118/3 Moo 7, Tambon Bang Sao Thong, Amphoe Bang Sao Thong, Samut Prakan 10570', lat: 13.56, lon: 100.80, leads: [P('hasareeyan-amin', 'Hasareeyan Amin', 'Regional Business Director')] },
  { id: 'in', country: 'India', entity: 'HexaHessman India', address: '129/1, Lal Bagh Main Road, Bengaluru 560027', lat: 12.955, lon: 77.59 },
  { id: 'uk', country: 'United Kingdom', entity: 'HexaHessman UK', address: '128 City Road, London EC1V 2NX', lat: 51.527, lon: -0.089, leads: [P('nigel-edwards', 'Nigel Edwards', 'Principal Advisor')] },
  { id: 'tr', country: 'Türkiye', entity: 'HexaHessman Turkey', address: 'Gökçe Apartmanı No: 22/12, Mustafa Kemal Mahallesi, 2124. Cadde, Çankaya, Ankara 06530', lat: 39.91, lon: 32.80, leads: [P('cemal-koc', 'Cemal Koc', 'Regional Business Director')] },
  { id: 'us', country: 'United States', entity: 'HexaHessman US', address: '730 N Milwaukee Ave, Chicago, IL 60642', lat: 41.90, lon: -87.66 },
];

const sec = document.getElementById('globe'); if (!sec) throw new Error('no #globe');
// the people for each office come from the About team (data-people), everyone in that office
let TEAM = []; try { TEAM = JSON.parse(sec.dataset.people || '[]'); } catch (e) {}
if (TEAM.length) OFFICES.forEach(o => { o.leads = TEAM.filter(p => p.office === o.id).map(p => P(p.slug, p.name, p.role)); });
// who stands where in an office's line (the middle one stands in front): Adam Yeoh in the middle, Hafriz Razif on his right (user, 2026-11-07)
// each cutout's head sits a little differently in its photo: dx moves the head onto its spot (in % of the figure's width),
// s can even out a figure's size
const FIT = { 'azmi-mahmood': { dx: -2.4 }, 'aizat-amin': { dx: -0.1 }, 'adam-yeoh': { dx: 1.1 }, 'hafriz-razif': { dx: -0.1 }, 'connie-tai': { dx: -9 } };   // Connie: Azmi's size, her shoulder tucked behind Hafriz's as Azmi's is behind Aizat's (client, 2026-11-07)
// (client, 2026-11-10) Singapore's line is Aizat, Azmi (in the middle) and Adam only; Yos stands in the middle for Indonesia;
// Thailand: Hasareeyan Amin (he replaces Thanin, client 2026-11-12) stands in front, Parin beside him. The office's list in the card keeps everyone, with Connie and Hafriz switched.
const LINE_ORDER = { sg: ['aizat-amin', 'azmi-mahmood', 'adam-yeoh'], id: ['krishna-hartono', 'yos-rizaldy', 'yani-lee'], th: ['hasareeyan-amin', 'parin-udornwong'] };
// an office with two people has no middle: the one named here stands in front, the other a step back beside them
const FRONT = { th: 'hasareeyan-amin' };
const LIST_ORDER = { sg: ['azmi-mahmood', 'aizat-amin', 'adam-yeoh', 'connie-tai', 'hafriz-razif'], th: ['hasareeyan-amin', 'parin-udornwong'] };
const byOrder = ord => (a, b) => (ord.indexOf(a.slug) + 99) % 99 - (ord.indexOf(b.slug) + 99) % 99;
OFFICES.forEach(o => { if (!o.leads) return;
  const lo = LIST_ORDER[o.id], li = LINE_ORDER[o.id];
  o.list = lo ? o.leads.slice().sort(byOrder(lo)) : o.leads.slice();
  if (li) { o.leads = o.leads.filter(p => li.includes(p.slug) || o.id !== 'sg').sort(byOrder(li)); } });
const INK = 0xeee3c7, PAPER = 0x0F2A1E;
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

// ---------- markup ----------
sec.innerHTML = `
  <div class="globe-stage"><canvas class="globe-canvas"></canvas><div class="globe-labels"></div><div class="gp-line" aria-hidden="true"></div></div>
  <div class="globe-side">
    <div class="eyebrow">Global reach, local impact</div>
    <h2>Nine markets. One standard of delivery.</h2>
    <div class="globe-list" role="tablist">${OFFICES.map((o, i) => `<button role="tab" data-i="${i}" aria-selected="${i === 0}">${o.country}</button>`).join('')}</div>
    <div class="globe-card" aria-live="polite"></div>
  </div>`;
const line = sec.querySelector('.gp-line');
addEventListener('resize', () => { const n = line.querySelector('.gp-names'); if (n) n.style.bottom = `calc(2% + ${Math.max(0, ...[...n.children].map(c => c.offsetHeight)) + 4}px)`; });
const canvas = sec.querySelector('.globe-canvas'), labelsEl = sec.querySelector('.globe-labels'), card = sec.querySelector('.globe-card'), tabs = [...sec.querySelectorAll('.globe-list button')];

// ---------- scene ----------
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(28, 1, 0.1, 50); camera.position.set(0, 0.3, 4.55); camera.lookAt(0, 0, 0);
const globe = new THREE.Group(); scene.add(globe);
const R = 1;
const toVec = (lat, lon, r = R) => { const phi = THREE.MathUtils.degToRad(90 - lat), th = THREE.MathUtils.degToRad(lon + 180); return new THREE.Vector3(-r * Math.sin(phi) * Math.cos(th), r * Math.cos(phi), r * Math.sin(phi) * Math.sin(th)); };

// the body: paper-coloured, so lines on the far side are hidden; a faint rim so the sphere reads against the page
globe.add(new THREE.Mesh(new THREE.SphereGeometry(R * 0.995, 64, 48), new THREE.MeshBasicMaterial({ color: 0x1a4232, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 })));
const rim = new THREE.Mesh(new THREE.SphereGeometry(R * 1.0, 64, 48), new THREE.ShaderMaterial({ transparent: true, depthWrite: false, uniforms: { c: { value: new THREE.Color(INK) } },
  vertexShader: `varying vec3 vN, vV; void main(){ vN = normalize(normalMatrix * normal); vec4 mv = modelViewMatrix * vec4(position,1.0); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }`,
  fragmentShader: `uniform vec3 c; varying vec3 vN, vV; void main(){ float f = pow(1.0 - max(dot(vN, vV), 0.0), 3.2); gl_FragColor = vec4(c, f * 0.35); }` }));
globe.add(rim);

// graticule every 15°
{ const pts = [];
  for (let lat = -75; lat <= 75; lat += 15) for (let lon = -180; lon < 180; lon += 3) { pts.push(toVec(lat, lon, R * 1.001), toVec(lat, lon + 3, R * 1.001)); }
  for (let lon = -180; lon < 180; lon += 15) for (let lat = -90; lat < 90; lat += 3) { pts.push(toVec(lat, lon, R * 1.001), toVec(lat + 3, lon, R * 1.001)); }
  globe.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: INK, transparent: true, opacity: 0.14 }))); }

// land outlines, drawn on as they arrive
const landMat = new THREE.LineBasicMaterial({ color: INK, transparent: true, opacity: 0.0 });
let landLines = null, landTotal = 0, drawT = 0;
(async () => {
  try {
    const [topo] = await Promise.all([fetch('/assets/vendor/land-110m.json').then(r => r.json()), loadTopojson()]);
    const mesh = window.topojson.mesh(topo, topo.objects.land);
    const pts = [];
    for (const line of mesh.coordinates) for (let i = 1; i < line.length; i++) { pts.push(toVec(line[i - 1][1], line[i - 1][0], R * 1.002), toVec(line[i][1], line[i][0], R * 1.002)); }
    const geo = new THREE.BufferGeometry().setFromPoints(pts); geo.setDrawRange(0, 0);
    landLines = new THREE.LineSegments(geo, landMat); landTotal = pts.length; globe.add(landLines);
  } catch (e) { console.warn('land outlines unavailable', e); }
})();
function loadTopojson() { return new Promise((res, rej) => { if (window.topojson) return res(); const s = document.createElement('script'); s.src = '/assets/vendor/topojson-client.min.js'; s.onload = res; s.onerror = rej; document.head.appendChild(s); }); }

// pins: a dot and a ring on the surface, a short stem; the active one is brighter and larger
const pins = OFFICES.map((o, i) => {
  const g = new THREE.Group(); const p = toVec(o.lat, o.lon, R * 1.003); g.position.copy(p); g.lookAt(p.clone().multiplyScalar(2));
  const dot = new THREE.Mesh(new THREE.CircleGeometry(0.012, 20), new THREE.MeshBasicMaterial({ color: INK }));
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.03, 0.034, 40), new THREE.MeshBasicMaterial({ color: INK, transparent: true, opacity: 0.7, side: THREE.DoubleSide }));
  const halo = new THREE.Mesh(new THREE.RingGeometry(0.055, 0.058, 48), new THREE.MeshBasicMaterial({ color: INK, transparent: true, opacity: 0.0, side: THREE.DoubleSide }));
  const stem = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 0, 0.12)]), new THREE.LineBasicMaterial({ color: INK, transparent: true, opacity: 0.5 }));
  g.add(dot, ring, halo, stem); globe.add(g);
  const label = document.createElement('button'); label.className = 'globe-label'; label.textContent = o.country; label.dataset.i = i; labelsEl.appendChild(label);
  label.addEventListener('click', () => select(i, true));
  return { g, dot, ring, halo, stem, label, world: new THREE.Vector3() };
});

// ---------- selection and motion ----------
let active = -1, userTouched = false, lastAuto = 0;
const targetQ = new THREE.Quaternion(), FACE = new THREE.Vector3(0, 0.18, 1).normalize();
function select(i, byUser) {
  if (byUser) userTouched = true;
  active = i; lastAuto = performance.now();
  const o = OFFICES[i];
  // turn the globe so this office faces the camera
  const v = toVec(o.lat, o.lon, 1); targetQ.setFromUnitVectors(v, FACE);
  tabs.forEach((t, k) => t.setAttribute('aria-selected', String(k === i)));
  pins.forEach((p, k) => p.label.classList.toggle('active', k === i));
  // the office's people step out in front of the globe, as in the About lineup: the first in front, the rest either side
  const L = o.leads || [], mid = (L.length - 1) / 2, GAP = 36;   // head-to-head spacing, in % of a figure's width
  // an office of two: both the same size, standing a little further apart, so neither is the bigger one (client, 2026-11-12).
  // FRONT only decides who overlaps whom where their shoulders meet.
  const pair = L.length === 2, PAIR_GAP = 52, fk = pair ? L.findIndex(l => l.slug === FRONT[o.id]) : -1;
  const pos = k => { if (pair) return { d: 0.5, x: (k - mid) * PAIR_GAP, z: k === fk ? 10 : 9 };
    const d = Math.abs(k - mid); return { d, x: Math.sign(k - mid) * Math.min(d, 2) * GAP, z: 10 - Math.round(d) }; };
  line.innerHTML = L.map((l, k) => { const { d, x, z } = pos(k), f = FIT[l.slug] || {};
    return `<figure class="gp-fig" style="--x:${(x + (f.dx || 0)).toFixed(1)}%;--s:${((1 - 0.16 * d) * (f.s || 1)).toFixed(3)};--z:${z};--k:${k}">
      <img src="/assets/team/cut/${l.slug}.webp?v=2" alt="" draggable="false"></figure>`; }).join('')
    // the names share one top line (client, 2026-11-07), each centred under its person
    // (spread a little wider than the people, so every title has room; they needn't sit exactly under each head)
    // (a pair's names sit exactly under the two heads; long names wrap onto a second line and never run into each other)
    + `<div class="gp-names">${L.map((l, k) => { const step = pair ? PAIR_GAP * 0.46 : Math.max(GAP * 0.46, Math.min(20, 90 / L.length));
        return `<p class="gp-name" style="--k:${k};left:${(50 + (k - mid) * step).toFixed(1)}%;width:${Math.min(30, step - 1).toFixed(1)}%"><b>${l.name}</b><span>${l.role}</span></p>`; }).join('')}</div>`;
  // the names hang from one top line, set high enough that the longest title (wrapped onto more lines) still shows in full
  const names = line.querySelector('.gp-names');
  const fitNames = () => { const h = Math.max(0, ...[...names.children].map(n => n.offsetHeight)); names.style.bottom = `calc(2% + ${h + 4}px)`; };
  fitNames(); requestAnimationFrame(fitNames); if (document.fonts) document.fonts.ready.then(fitNames);
  line.classList.remove('in'); void line.offsetWidth; line.classList.add('in');
  const people = (o.list || L).map(l => `
      <div class="lead"><div><div class="who">${l.name}</div><div class="muted">${l.role}</div></div></div>`   /* no personal emails (client, 2026-11-06) */).join('');
  card.innerHTML = `
    <div class="globe-card-head"><span class="eyebrow">${o.entity}</span><h3>${o.country}</h3></div>
    <p class="addr">${o.address}${o.extra ? `<br><span class="muted">${o.extra}</span>` : ''}</p>
    ${people || `<div class="lead"><div class="avatar" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div>
      <div><div class="who">Office enquiries</div><div class="muted">Reach this office through our Singapore team</div><a href="mailto:inquiry@hexahessman.com">inquiry@hexahessman.com</a></div></div>`}`;
}
tabs.forEach(t => t.addEventListener('click', () => select(+t.dataset.i, true)));

// drag to turn
let drag = null;
canvas.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY, q: globe.quaternion.clone() }; userTouched = true; canvas.setPointerCapture(e.pointerId); });
canvas.addEventListener('pointermove', e => { if (!drag) return; const dx = (e.clientX - drag.x) / 200, dy = (e.clientY - drag.y) / 200;
  const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(dy, dx, 0)); globe.quaternion.copy(q.multiply(drag.q)); targetQ.copy(globe.quaternion); });
// a click (not a drag) on or near an office's dot picks that office (user, 2026-11-06)
canvas.addEventListener('pointerup', e => {
  const moved = drag ? Math.hypot(e.clientX - drag.x, e.clientY - drag.y) : 99;
  drag = null; lastAuto = performance.now();
  if (moved > 6) return;
  const r = canvas.getBoundingClientRect();
  // the nearest dot under the pointer; if two are close, the one nearer the camera (front of the globe) wins
  let best = -1, bz = Infinity;
  pins.forEach((p, i) => {
    const w = new THREE.Vector3(); p.g.getWorldPosition(w);
    const v = w.project(camera), x = (v.x * 0.5 + 0.5) * r.width, y = (-v.y * 0.5 + 0.5) * r.height;
    const d = Math.hypot(x - (e.clientX - r.left), y - (e.clientY - r.top));
    if (d < 30 && v.z + d * 0.0004 < bz) { bz = v.z + d * 0.0004; best = i; }
  });
  if (best >= 0) select(best, true);
});
canvas.addEventListener('pointermove', e => { if (drag) return; canvas.style.cursor = 'grab'; });

// ---------- size and loop ----------
const stage = sec.querySelector('.globe-stage');
function size() { const w = stage.clientWidth, h = stage.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); camera.fov = w < 520 ? 34 : 28; camera.updateProjectionMatrix(); }
new ResizeObserver(size).observe(stage); size();
const _p = new THREE.Vector3(), _n = new THREE.Vector3(), camDir = new THREE.Vector3();
let visible = true; new IntersectionObserver(([e]) => { visible = e.isIntersecting; }, { threshold: 0.02 }).observe(sec);
const clock = new THREE.Clock();
function tick() {
  requestAnimationFrame(tick);
  const dt = Math.min(clock.getDelta(), 0.05), now = performance.now();
  if (!visible) return;
  // land draw-on
  if (landLines && drawT < 1) { drawT = Math.min(1, drawT + dt / (reduce ? 0.01 : 2.4)); landLines.geometry.setDrawRange(0, Math.floor(landTotal * drawT)); landMat.opacity = 0.9 * Math.min(1, drawT * 2); }
  // turn towards the chosen office; tour the offices until someone takes over
  if (!drag) {
    globe.quaternion.slerp(targetQ, 1 - Math.pow(0.0025, dt));
    // (no automatic switching between countries, user 2026-11-07: the globe stays on the office that was picked)
  }
  // pins and labels: stronger when facing us, hidden on the far side
  camera.getWorldDirection(camDir);
  const w = stage.clientWidth, h = stage.clientHeight;
  pins.forEach((p, i) => {
    p.g.getWorldPosition(_p); _n.copy(_p).normalize(); const facing = -_n.dot(camDir);
    const on = i === active;
    p.ring.material.opacity = THREE.MathUtils.lerp(p.ring.material.opacity, (on ? 0.95 : 0.6) * Math.max(0, facing), 0.15);
    p.halo.material.opacity = THREE.MathUtils.lerp(p.halo.material.opacity, (on ? 0.6 + 0.3 * Math.sin(now / 300) : 0) * Math.max(0, facing), 0.15);
    p.stem.material.opacity = (on ? 0.8 : 0.35) * Math.max(0, facing);
    const s = on ? 1.6 : 1; p.g.scale.setScalar(THREE.MathUtils.lerp(p.g.scale.x, s, 0.15));
    _p.project(camera); const x = (_p.x * 0.5 + 0.5) * w, y = (-_p.y * 0.5 + 0.5) * h;
    p.label.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px)`;
    const show = on && facing > 0.12;
    p.label.style.opacity = show ? String(Math.min(1, (facing - 0.12) * 3)) : '0';
    p.label.style.pointerEvents = show ? 'auto' : 'none';
  });
  renderer.render(scene, camera);
}
select(0, false); tick();
