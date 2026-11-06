// Render frames of port-view.html (shaded) or port-wire.html (lines + particles) along a camera path, headless.
//   node render_path.mjs <page-url> <path.json> <out_dir> <W> <H> [from] [to]
// path.json: { "fps": 24, "seconds": 8, "fov": 36, "keys": [ { "t": 0, "pos": [x,y,z], "tgt": [x,y,z] }, ... ] }
// The camera runs through the keys on a Catmull-Rom curve with one smooth ease over the whole move (no bumps), so
// both pages produce frame k from exactly the same camera, and frames line up with each other.
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync, readFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { mkdtempSync } from 'node:fs';

const [url, pathFile, out, W = '1920', H = '1080', FROM = '0', TO = ''] = process.argv.slice(2);
const P = JSON.parse(readFileSync(pathFile, 'utf8'));
const N = Math.round((P.fps || 24) * (P.seconds || 8));
// KMAP=<file.json>: output frame j is drawn at path position kmap[j] (fractional frames allowed), so a layer can be made to
// follow footage that runs slightly ahead of or behind the path without ever holding a frame
const KM = process.env.KMAP ? JSON.parse(readFileSync(process.env.KMAP, 'utf8')) : null;
const from = +FROM, to = TO === '' ? (KM ? KM.length - 1 : N - 1) : +TO;
mkdirSync(out, { recursive: true });

// ---- the path: Catmull-Rom through the keys (clamped ends), time eased once over the whole move ----
const keys = P.keys.slice().sort((a, b) => a.t - b.t);
// the speed profile: a short smooth ramp in, steady through the middle, a short ramp out (one continuous move, no bumps)
const sstep = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const RIN = P.ramp_in ?? 0.14, ROUT = P.ramp_out ?? 0.12;
const vel = u => sstep(0, RIN, u) * (1 - sstep(1 - ROUT, 1, u));
const TAB = []; { let acc = 0; const M = 2000; for (let i = 0; i <= M; i++) { TAB.push(acc); acc += vel(i / M) / M; } for (let i = 0; i <= M; i++) TAB[i] /= acc; }
const ease = P.ease === 'linear' ? (x => x) : P.ease === 'smooth' ? (x => x * x * x * (x * (x * 6 - 15) + 10)) : (x => TAB[Math.round(Math.min(1, Math.max(0, x)) * 2000)]);
function catmull(p0, p1, p2, p3, t) {
  const t2 = t * t, t3 = t2 * t;
  return p1.map((_, i) => 0.5 * ((2 * p1[i]) + (-p0[i] + p2[i]) * t + (2 * p0[i] - 5 * p1[i] + 4 * p2[i] - p3[i]) * t2 + (-p0[i] + 3 * p1[i] - 3 * p2[i] + p3[i]) * t3));
}
function at(u, field) {   // u in 0..1 along the eased timeline
  const s = keys[0].t + (keys[keys.length - 1].t - keys[0].t) * u;
  let i = 0; while (i < keys.length - 2 && s > keys[i + 1].t) i++;
  const a = keys[Math.max(0, i - 1)], b = keys[i], c = keys[i + 1], d = keys[Math.min(keys.length - 1, i + 2)];
  const t = (s - b.t) / (c.t - b.t);
  return catmull(a[field], b[field], c[field], d[field], Math.min(1, Math.max(0, t)));
}
const cam = k => { const u = ease(k / (N - 1)); return { pos: at(u, 'pos'), tgt: at(u, 'tgt') }; };

// ---- headless chrome ----
const CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const port = 9400 + Math.floor(Math.random() * 400);
const prof = mkdtempSync(join(process.env.TMPDIR || tmpdir(), 'rp-'));
const chrome = spawn(CH, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, '--hide-scrollbars', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', `--window-size=${W},${H}`, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let ws;
for (let i = 0; i < 80; i++) {
  try { const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); const pg = list.find(t => t.type === 'page'); if (pg) { ws = new WebSocket(pg.webSocketDebuggerUrl); break; } } catch {}
  await sleep(150);
}
await new Promise(r => ws.addEventListener('open', r));
let id = 0; const pend = new Map();
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } });
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const evalJs = async (expression) => { const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true }); if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 400)); return r.result?.result?.value; };
await send('Emulation.setDeviceMetricsOverride', { width: +W, height: +H, deviceScaleFactor: 1, mobile: false });
await send('Page.enable'); await send('Runtime.enable');
await send('Page.navigate', { url });
// wait for the model: port-wire sets window.__ready, port-view marks #load done
for (let i = 0; i < 600; i++) { const ok = await evalJs(`!!(window.__ready || (document.getElementById('load') && document.getElementById('load').classList.contains('done')))`).catch(() => false); if (ok) break; await sleep(500); }
await sleep(1500);   // sky / env textures
// hide the view page's buttons and captions, then take over the camera: stop the page's own loop, fix the size, set the lens
await evalJs(`(() => { const st = document.createElement('style'); st.textContent = '.bar,.tip,.load{display:none!important}'; document.head.appendChild(st); return true; })()`);
await evalJs(`(() => {
  const V = window.__wire || window.__view; window.__V = V;
  if (V.lock) V.lock(${W}, ${H}, 1); else { V.renderer.setAnimationLoop(null); V.renderer.setPixelRatio(1); V.renderer.setSize(${W}, ${H}, false); V.composer.setPixelRatio(1); V.composer.setSize(${W}, ${H}); if (V.gtao) V.gtao.setSize(${W}, ${H}); V.camera.aspect = ${W} / ${H}; V.camera.updateProjectionMatrix(); }
  V.camera.fov = ${P.fov || 36}; V.camera.updateProjectionMatrix();
  window.__setCam = (p, t, k) => { V.camera.position.set(p[0], p[1], p[2]); V.camera.lookAt(t[0], t[1], t[2]); V.camera.updateMatrixWorld();
    if (V.dotMat) V.dotMat.uniforms.uTime.value = k / ${P.fps || 24};
    if (window.__ghost && ${JSON.stringify(P.ghost_fade || null)}) { const [g0, g1] = ${JSON.stringify(P.ghost_fade || [0, 1])}; window.__ghost.mat.opacity = window.__ghost.base * Math.min(1, Math.max(0, (g1 - k) / (g1 - g0))); }
    if (V.scene && V.scene.__water) V.scene.__water.material.uniforms.time.value = k / ${P.fps || 24} * 0.5;
    V.draw(); return true; };
  return true; })()`);
const t0 = Date.now();
for (let k = from; k <= to; k++) {
  const f = join(out, `f${String(k).padStart(4, '0')}.png`); if (existsSync(f)) continue;
  const kk = KM ? KM[k] : k, c = cam(kk);
  await evalJs(`window.__setCam(${JSON.stringify(c.pos)}, ${JSON.stringify(c.tgt)}, ${kk})`);
  await evalJs(`window.__setCam(${JSON.stringify(c.pos)}, ${JSON.stringify(c.tgt)}, ${kk})`);   // twice: the water / temporal passes settle
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync(f, Buffer.from(shot.result.data, 'base64'));
  if ((k - from) % 12 === 0) console.log(`frame ${k}/${to}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
chrome.kill();
console.log('done', out);
process.exit(0);
