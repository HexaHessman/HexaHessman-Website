// Product pages (client, 2026-11-12): ONE connected glowing line in our green crosses the Product types section from
// left to right: in from the left edge above the cards, down between the first two, along under the cards, up between
// the last two and out to the right edge. Where it turns under the cards, two short drops carry on down through the
// bottom of the section; the closing band's two lines (deco-lines.js) start at those same two points, so the lines
// read as one run down the page. The section is marked data-pp-lines by the generator. Desktop only.
(() => {
  const sec = document.querySelector('[data-pp-lines]'); if (!sec) return;
  const NS = 'http://www.w3.org/2000/svg';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  // a polyline with rounded corners (radius r)
  const round = (pts, r) => {
    let d = `M${pts[0][0]},${pts[0][1]}`;
    for (let i = 1; i < pts.length - 1; i++) {
      const [ax, ay] = pts[i - 1], [px, py] = pts[i], [bx, by] = pts[i + 1];
      const la = Math.hypot(ax - px, ay - py), lb = Math.hypot(bx - px, by - py), k = Math.min(r, la / 2, lb / 2);
      if (la < 1 || lb < 1) continue;
      const s = [px + (ax - px) * k / la, py + (ay - py) * k / la], e = [px + (bx - px) * k / lb, py + (by - py) * k / lb];
      d += `L${s[0].toFixed(1)},${s[1].toFixed(1)}Q${px.toFixed(1)},${py.toFixed(1)} ${e[0].toFixed(1)},${e[1].toFixed(1)}`;
    }
    const z = pts[pts.length - 1]; return d + `L${z[0]},${z[1]}`;
  };
  const svg = document.createElementNS(NS, 'svg'); svg.setAttribute('class', 'pp-lines'); svg.setAttribute('aria-hidden', 'true'); sec.prepend(svg);
  let seen = false, anims = [], last = '';
  const draw = () => {
    const W = document.documentElement.clientWidth, H = sec.offsetHeight, box = sec.getBoundingClientRect();
    // the cards the line threads between: the photos and the words beside them where the page has that layout, else the grid's own cards
    const duo = sec.querySelector('.pp-duo'), grid = duo || sec.querySelector('.pp-types, .pp-feats');
    const cards = duo ? [...duo.querySelectorAll('.pp-type'), duo.querySelector('.pp-side')].filter(Boolean) : grid ? [...grid.children] : [];
    const cta = document.querySelector('section#cta');
    const tell = (a, b) => { if (!cta) return; const was = cta.dataset.x1 + '|' + cta.dataset.x2;   // the closing band starts its lines under ours
      if (a === null) { delete cta.dataset.x1; delete cta.dataset.x2; } else { cta.dataset.x1 = a.toFixed(1); cta.dataset.x2 = b.toFixed(1); }
      if (was !== cta.dataset.x1 + '|' + cta.dataset.x2 && window.__decoLines) window.__decoLines(); };
    if (W <= 900 || !cards.length || H < 120) { svg.innerHTML = ''; last = ''; tell(null); return; }
    const under = [...sec.children].filter(e => e !== svg).pop() || grid;   // the last block in the section (grade cards, where there are any)
    const g = grid.getBoundingClientRect(), top = g.top - box.top, bottom = under.getBoundingClientRect().bottom - box.top;
    const rows = cards.map(c => c.getBoundingClientRect()), first = rows.filter(q => Math.abs(q.top - rows[0].top) < 4);
    const key = [W, H, Math.round(box.left), Math.round(top), Math.round(bottom), first.length, Math.round(first[0].left)].join(',');
    if (key === last) return; last = key;
    anims.forEach(a => a.cancel()); anims = []; svg.innerHTML = '';
    svg.style.left = (-box.left) + 'px'; svg.style.width = W + 'px'; svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    // the two verticals: in the gaps beside the first and the last card where there are three or more across, else just outside the cards
    let xl, xr;
    if (first.length >= 3) { xl = (first[0].right + first[1].left) / 2; xr = (first[first.length - 2].right + first[first.length - 1].left) / 2; }
    else { xl = Math.max(10, first[0].left - 26); xr = Math.min(W - 10, first[first.length - 1].right + 26); }
    const head = sec.querySelector('.pp-h'), hb = head ? head.getBoundingClientRect().bottom - box.top : top - 30;
    const y1 = Math.max(8, (hb + top) / 2);              // the line runs between the heading and the cards
    const yb = bottom + (H - bottom) * 0.5;              // and turns in the space under them
    const r = Math.min(40, (H - bottom) * 0.42, Math.max(6, (top - hb) * 0.9));
    tell(xl, xr);
    const lines = [
      round([[-2, y1], [xl, y1], [xl, yb], [xr, yb], [xr, y1], [W + 2, y1]], r),   // the one line, left to right
      // (the two straight drops from its corners down to the bottom of the section were removed: client, 2026-11-12)
    ];
    lines.forEach((d, i) => {
      const base = document.createElementNS(NS, 'path'); base.setAttribute('d', d); base.setAttribute('class', 'ppl-line'); svg.appendChild(base);
      if (reduce) return;
      const run = document.createElementNS(NS, 'path'); run.setAttribute('d', d); run.setAttribute('class', 'ppl-run'); svg.appendChild(run);
      const L = run.getTotalLength(), dash = i ? L : Math.min(170, L * 0.07);
      run.style.strokeDasharray = `${dash.toFixed(0)} ${(L + dash).toFixed(0)}`;
      // the light travels the whole line from left to right (6.4 s a pass); as it turns under the cards, a short one runs down each drop
      const T = 6400, at = i === 1 ? 0.36 : 0.6;
      const light = (wait) => anims.push(i === 0
        ? run.animate([{ strokeDashoffset: dash }, { strokeDashoffset: -L }], { duration: T, iterations: Infinity, easing: 'linear', delay: wait })
        : run.animate([{ strokeDashoffset: L, offset: 0 }, { strokeDashoffset: L, offset: at }, { strokeDashoffset: -L, offset: Math.min(1, at + 0.16) }, { strokeDashoffset: -L, offset: 1 }], { duration: T, iterations: Infinity, easing: 'linear', delay: wait }));
      if (i) run.style.strokeLinecap = 'butt';   // (a round end would leave a dot where a drop starts)
      run.style.strokeDashoffset = dash;   // off the line until its first pass
      if (seen) { light(0); return; }
      // first time on screen: the lines draw themselves in from the sides, then the lights start
      base.style.strokeDasharray = `${L.toFixed(1)} ${L.toFixed(1)}`; base.style.strokeDashoffset = L.toFixed(1);
      const DRAW = i ? 500 : 2200, wait = i === 1 ? 800 : i === 2 ? 1350 : 0;   // the line draws itself in from the left; each drop follows as it passes
      base._go = () => { anims.push(base.animate([{ strokeDashoffset: L }, { strokeDashoffset: 0 }], { duration: DRAW, delay: wait, easing: i ? 'ease-out' : 'cubic-bezier(.45,.05,.25,1)', fill: 'forwards' })); light(2400); };
    });
    if (seen) return;
    if (svg._io) svg._io.disconnect();
    svg._io = new IntersectionObserver(([e], io) => { if (!e.isIntersecting) return; io.disconnect(); seen = true; svg.querySelectorAll('.ppl-line').forEach(b => b._go && b._go()); }, { threshold: 0.2 });
    svg._io.observe(sec);
  };
  draw();
  addEventListener('resize', () => { clearTimeout(draw.t); draw.t = setTimeout(draw, 120); });
  addEventListener('load', draw);
  if (window.ResizeObserver) new ResizeObserver(() => { clearTimeout(draw.t); draw.t = setTimeout(draw, 120); }).observe(sec);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(draw);
})();
