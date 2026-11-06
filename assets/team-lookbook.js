// The About page's team lookbook, after a runway show: everyone stands in one line in the middle of the stage,
// the person at the front sharp and full size, the rest waiting behind, each a step further back, smaller and
// more out of focus. Pressing Next walks the line forward one person: the next one steps up into focus while the
// one at the front walks off past the camera, then quietly rejoins the back of the queue (the line is a circle).
// Arrow keys and a swipe do the same. Mounts into <section id="team" data-people="[...]">.
(() => {
  const sec = document.getElementById('team'); if (!sec) return;
  let people = []; try { people = JSON.parse(sec.dataset.people || '[]'); } catch (e) { return; }
  const n = people.length; if (!n) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const VISIBLE = 8, STEP_MS = reduce ? 0 : 900;   // people shown in the queue; how long one step takes
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const pad = k => String(k).padStart(2, '0');

  const stage = sec.querySelector('.tl-stage'), queue = sec.querySelector('.tl-queue');
  const info = sec.querySelector('.tl-info');
  queue.innerHTML = people.map((p, i) => `<img class="tl-cut" src="/assets/team/cut/${p.slug}.webp?v=2" alt="${esc(p.name)}" width="900" height="781" decoding="async" draggable="false">`).join('');
  const cuts = [...queue.children];
  let active = 0, busy = false;

  // each figure's place on the path: o is how many places it is from the front (negative = still to come, on the right;
  // positive = already past, on the left). Row d = |o| back is smaller by a shrinking amount, closer to the last,
  // stands a little higher and is more blurred and fainter. A press moves everyone one place along the path, left
  // to right: the next person steps up to the front, the front one moves off to the right, the last on the right
  // fades out and a new one fades in at the far left. Offsets are in fractions of the front figure's size.
  const SPAN = 4;   // places shown on each side
  const pose = (el, o) => {
    const far = Math.abs(o) > SPAN, d = Math.min(Math.abs(o), SPAN + 1), side = Math.sign(o);   // those still to come wait on the right, so → pulls the next one in from the right
    const A = innerWidth <= 900 ? 0.45 : 0.5, R = 0.7;   // first step aside; how much each next step shrinks
    const s = d ? 1 / (1 + 0.55 * d) : 1, x = side * A * (1 - Math.pow(R, d)) / (1 - R), y = d ? -(1 - s) * 0.5 : -0.06;   // the front person stands a little higher
    el.style.setProperty('--x', (x * 100).toFixed(1) + '%'); el.style.setProperty('--y', (y * 100).toFixed(1) + '%');
    el.style.setProperty('--s', s.toFixed(3)); el.style.setProperty('--b', Math.min(10, 1.8 * d).toFixed(1) + 'px');
    el.style.setProperty('--o', far ? '0' : Math.max(0.3, 1 - 0.13 * d).toFixed(2));
    el.classList.toggle('far', far); el.style.zIndex = 60 - d;
  };
  // place from the front, the circle of people unrolled: half wait on the left, half have passed on the right
  const offset = i => { const m = (i - active + n) % n; return m <= n / 2 ? m : m - n; };
  const layout = () => cuts.forEach((el, i) => pose(el, offset(i)));
  addEventListener('resize', () => { if (!busy) layout(); });

  function write() {
    const p = people[active];
    info.querySelector('.tl-name').textContent = p.name;
    info.querySelector('.tl-role').textContent = p.role;
    info.querySelector('.tl-where').textContent = `${p.entity} · ${p.city}`;
    info.querySelector('.tl-desc').textContent = p.blurb || '';
    info.classList.remove('swap'); void info.offsetWidth; info.classList.add('swap');
    window.__teamCurrent = p;
    document.dispatchEvent(new CustomEvent('team-change', { detail: p }));   // the globe turns to this office
  }

  function step(dir) {
    if (busy) return; busy = true;
    active = (active + (dir > 0 ? 1 : n - 1)) % n;
    layout(); write();
    setTimeout(() => { busy = false; }, STEP_MS);
  }

  // the grid of everyone under the line: a card brings that person to the front
  function jump(i, stay) {
    if (busy || i === active) return; busy = true;
    active = i; layout(); write();
    if (!stay) stage.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    setTimeout(() => { busy = false; }, STEP_MS);
  }
  sec.querySelectorAll('.tl-grid button').forEach(b => b.addEventListener('click', () => jump(+b.dataset.i)));
  // the grid of everyone: each card slides in when its row comes on screen, left to right along the row
  const cells = [...sec.querySelectorAll('.tl-grid li')];
  const cols = () => getComputedStyle(sec.querySelector('.tl-grid')).gridTemplateColumns.split(' ').length;
  const gio = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.style.setProperty('--c', cells.indexOf(e.target) % cols()); e.target.classList.add('in'); gio.unobserve(e.target);
  }), { threshold: 0.2 });
  cells.forEach(c => gio.observe(c));
  window.__teamStep = step; window.__teamJump = jump;

  // controls: the buttons, the arrow keys while the stage is on screen, a swipe or a tap on the line
  sec.querySelector('.tl-next').addEventListener('click', () => step(1));
  sec.querySelector('.tl-prev').addEventListener('click', () => step(-1));
  let onScreen = false;
  new IntersectionObserver(([e]) => { onScreen = e.isIntersecting; }, { threshold: 0.4 }).observe(stage);
  addEventListener('keydown', e => {
    if (!onScreen || e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); step(1); }
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); step(-1); }
  });
  let down = null;
  queue.addEventListener('pointerdown', e => { down = { x: e.clientX, y: e.clientY, t: performance.now() }; });
  queue.addEventListener('pointerup', e => {
    if (!down) return; const dx = e.clientX - down.x, dy = e.clientY - down.y, dt = performance.now() - down.t; down = null;
    if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) step(dx < 0 ? 1 : -1);
    else if (Math.hypot(dx, dy) < 8 && dt < 500) {   // a tap: whoever stands nearest the tap comes to the front (left goes left, right goes right)
      let best = active, bd = Infinity;
      cuts.forEach((el, i) => { if (el.classList.contains('far')) return; const r = el.getBoundingClientRect(); const d = Math.abs(r.left + r.width / 2 - e.clientX); if (d < bd) { bd = d; best = i; } });
      if (best !== active) { const o = offset(best); if (Math.abs(o) === 1) step(o); else jump(best, true); }
    }
  });

  layout(); write();
})();
