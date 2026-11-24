// Terminal-style lines in the big empty bands (each page's closing call-to-action, section#cta): two thin rounded
// step lines run in from the top and the sides, and a short light travels along each. Drawn to the section's size.
// On first view they draw themselves down from the top, then the light starts (client, 2026-11-07).
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const secs = [...document.querySelectorAll('section#cta, [data-lines]')]; if (!secs.length) return;
  // a polyline with rounded corners (radius r)
  const round = (pts, r) => {
    let d = `M${pts[0][0]},${pts[0][1]}`;
    for (let i = 1; i < pts.length - 1; i++) {
      const [ax, ay] = pts[i - 1], [px, py] = pts[i], [bx, by] = pts[i + 1];
      const la = Math.hypot(ax - px, ay - py), lb = Math.hypot(bx - px, by - py), k = Math.min(pts[i][2] || r, la / 2, lb / 2);   // (a point may carry its own radius)
      const s = [px + (ax - px) * k / la, py + (ay - py) * k / la], e = [px + (bx - px) * k / lb, py + (by - py) * k / lb];
      d += `L${s[0].toFixed(1)},${s[1].toFixed(1)}Q${px},${py} ${e[0].toFixed(1)},${e[1].toFixed(1)}`;
    }
    const z = pts[pts.length - 1]; return d + `L${z[0]},${z[1]}`;
  };
  const bg = el => { for (let e = el; e; e = e.parentElement) { const c = getComputedStyle(e).backgroundColor; if (c && c !== 'transparent' && !/rgba\(.*,\s*0\)$/.test(c)) return c; } return ''; };
  const reach = sec => {
    const prev = sec.previousElementSibling;
    if (!prev || prev.offsetHeight < 40 || bg(prev) !== bg(sec)) return 0;
    const kids = [...prev.children].filter(e => e.offsetHeight && getComputedStyle(e).position !== 'absolute');
    const last = kids[kids.length - 1]; if (!last) return 0;
    const gap = sec.getBoundingClientRect().top - last.getBoundingClientRect().bottom;
    return gap > 40 ? Math.min(gap * 0.5, 140) : 0;
  };
  // Product pages (client, 2026-11-25): the two lines join Related products to the closing band. The left one comes down
  // from the top of the Related products section through the gap between the first two cards; the right one comes in
  // from the page's right edge beside the heading and turns down through the gap between the last two. Both carry on
  // into the band. Only where the three cards stand in one row (on phones they are stacked: the lines keep "reach").
  const through = sec => {
    const prev = sec.previousElementSibling;
    if (!prev || prev.id !== 'related' || bg(prev) !== bg(sec)) return null;
    const cards = [...prev.querySelectorAll('.grid > .card')]; if (cards.length < 3) return null;
    const q = cards.map(c => c.getBoundingClientRect()), s = sec.getBoundingClientRect(), n = q.length;
    if (Math.abs(q[0].top - q[n - 1].top) > 4 || q[1].left - q[0].right < 8) return null;
    const h2 = prev.querySelector('h2'); let hr = null;
    if (h2) { const rg = document.createRange(); rg.selectNodeContents(h2); hr = rg.getBoundingClientRect(); }
    const cardsTop = q[0].top - s.top, top = prev.getBoundingClientRect().top - s.top;
    const yIn = hr && hr.height ? (hr.top + hr.bottom) / 2 - s.top : cardsTop - 40;   // the height the right line comes in at: the middle of the heading
    return { x1: (q[0].right + q[1].left) / 2 - s.left, x2: (q[n - 2].right + q[n - 1].left) / 2 - s.left, top, yIn, turn: Math.max(6, cardsTop - yIn - 6),
      clear: !hr || hr.right - s.left < (q[0].right + q[1].left) / 2 - s.left - 18, prev };   // clear: the heading's words end before the left line
  };
  const draw = (sec) => {
    const w = sec.offsetWidth, h = sec.offsetHeight; if (w < 300 || h < 160) return;
    let svg = sec.querySelector(':scope > .deco-lines');
    if (!svg) { svg = document.createElementNS(NS, 'svg'); svg.setAttribute('class', 'deco-lines'); svg.setAttribute('aria-hidden', 'true'); sec.prepend(svg); }
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`); svg.innerHTML = '';
    const r = Math.min(70, h * 0.18), narrow = w < 760;
    // the two lines start at 42% and 64% of the width, or where the page says (product pages: under the Product types line, product-lines.js)
    const thru = through(sec);
    const x1 = thru ? thru.x1 : +sec.dataset.x1 || w * (narrow ? 0.46 : 0.42), x2 = thru ? thru.x2 : +sec.dataset.x2 || w * (narrow ? 0.7 : 0.64);
    let left = [[x1, -2], [x1, h * 0.2], [w * 0.1, h * 0.2], [w * 0.1, h * 0.62], [w * 0.06, h * 0.66], [-2, h * 0.66]];
    let right = [[x2, -2], [x2, h * 0.3], [w * 0.93, h * 0.3], [w * 0.93, h * 0.58], [w + 2, h * 0.58]];
    // when the section above has the same colour (no edge shows, as under Related products on the product pages), the
    // lines don't start in mid air: they come in from the page's left and right edges, up in the gap under that
    // section's content, and turn down into the band (client, 2026-11-17)
    const up = thru ? 0 : reach(sec);
    svg.style.overflow = up || thru ? 'visible' : '';
    // the band clips what leaves it (overflow: hidden); where the lines start above it, only its sides clip
    sec.style.overflowX = up || thru ? 'clip' : ''; sec.style.overflowY = up || thru ? 'visible' : '';
    if (thru) {
      // the left line: straight down from the top of Related products (or, where the heading's words are in the way, in from the left edge under them)
      left = thru.clear ? [[x1, thru.top], ...left.slice(1)] : [[-2, thru.yIn + thru.turn * 0.55], [x1, thru.yIn + thru.turn * 0.55, thru.turn * 0.4], ...left.slice(1)];
      right = [[w + 2, thru.yIn], [x2, thru.yIn, thru.turn], ...right.slice(1)];
    }
    if (up) { left = [[-2, -up], [x1, -up], ...left.slice(1)]; right = [[w + 2, -up], [x2, -up], ...right.slice(1)]; }
    const first = !sec.dataset.drawn && !reduce;   // the first time the band comes into view, the lines draw themselves down
    if (first) sec._go = [];   // (a redraw before it is seen replaces the waiting lines)
    [left, right].forEach((pts, i) => {
      const d = round(pts, r);
      const base = document.createElementNS(NS, 'path'); base.setAttribute('d', d); base.setAttribute('class', 'dl-line'); svg.appendChild(base);
      if (reduce) return;
      const run = document.createElementNS(NS, 'path'); run.setAttribute('d', d); run.setAttribute('class', 'dl-run'); svg.appendChild(run);
      const L = run.getTotalLength(); run.style.strokeDasharray = `${Math.min(140, L * 0.12).toFixed(0)} ${L.toFixed(0)}`;
      const startRun = (wait) => run.animate([{ strokeDashoffset: L * 0.12 + 140 }, { strokeDashoffset: -L }], { duration: 5200 + i * 1400, iterations: Infinity, easing: 'cubic-bezier(.45,.05,.4,1)', delay: wait + i * 1600 });
      if (!first) { startRun(0); return; }
      // hidden until the band is on screen, then drawn from the top, down and across; the light starts once it is drawn
      base.style.strokeDasharray = `${L.toFixed(1)} ${L.toFixed(1)}`; base.style.strokeDashoffset = L.toFixed(1); run.style.opacity = '0';
      const DRAW = 1800 + i * 300;
      sec._go.push(() => {
        base.animate([{ strokeDashoffset: L }, { strokeDashoffset: 0 }], { duration: DRAW, delay: i * 250, easing: 'cubic-bezier(.45,.05,.25,1)', fill: 'forwards' })
          .finished.then(() => { base.style.strokeDasharray = ''; base.style.strokeDashoffset = ''; });
        run.style.opacity = ''; startRun(DRAW + i * 250);
      });
    });
    if (first && !sec._io) {
      sec._io = new IntersectionObserver((es, io) => { if (!es.some(e => e.isIntersecting)) return; io.disconnect(); sec.dataset.drawn = '1'; (sec._go || []).forEach(f => f()); sec._go = []; },
        { rootMargin: '0px 0px -15% 0px', threshold: 0.2 });
      sec._io.observe(sec);
      if (thru) sec._io.observe(thru.prev);   // the lines start up in Related products: draw them when that comes on screen
    }
  };
  const all = () => secs.forEach(draw);
  window.__decoLines = all;
  all(); addEventListener('resize', () => { clearTimeout(all.t); all.t = setTimeout(all, 150); });
  // where the lines follow the Related products cards, they are drawn again once the page and its fonts have settled
  if (document.querySelector('#related + section#cta')) { addEventListener('load', all); if (document.fonts && document.fonts.ready) document.fonts.ready.then(all); }
})();
