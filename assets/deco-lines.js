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
      const la = Math.hypot(ax - px, ay - py), lb = Math.hypot(bx - px, by - py), k = Math.min(r, la / 2, lb / 2);
      const s = [px + (ax - px) * k / la, py + (ay - py) * k / la], e = [px + (bx - px) * k / lb, py + (by - py) * k / lb];
      d += `L${s[0].toFixed(1)},${s[1].toFixed(1)}Q${px},${py} ${e[0].toFixed(1)},${e[1].toFixed(1)}`;
    }
    const z = pts[pts.length - 1]; return d + `L${z[0]},${z[1]}`;
  };
  const draw = (sec) => {
    const w = sec.offsetWidth, h = sec.offsetHeight; if (w < 300 || h < 160) return;
    let svg = sec.querySelector(':scope > .deco-lines');
    if (!svg) { svg = document.createElementNS(NS, 'svg'); svg.setAttribute('class', 'deco-lines'); svg.setAttribute('aria-hidden', 'true'); sec.prepend(svg); }
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`); svg.innerHTML = '';
    const r = Math.min(70, h * 0.18), narrow = w < 760;
    // the two lines start at 42% and 64% of the width, or where the page says (product pages: under the Product types line, product-lines.js)
    const x1 = +sec.dataset.x1 || w * (narrow ? 0.46 : 0.42), x2 = +sec.dataset.x2 || w * (narrow ? 0.7 : 0.64);
    const left = [[x1, -2], [x1, h * 0.2], [w * 0.1, h * 0.2], [w * 0.1, h * 0.62], [w * 0.06, h * 0.66], [-2, h * 0.66]];
    const right = [[x2, -2], [x2, h * 0.3], [w * 0.93, h * 0.3], [w * 0.93, h * 0.58], [w + 2, h * 0.58]];
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
      sec._io = new IntersectionObserver(([e], io) => { if (!e.isIntersecting) return; io.disconnect(); sec.dataset.drawn = '1'; (sec._go || []).forEach(f => f()); sec._go = []; },
        { rootMargin: '0px 0px -15% 0px', threshold: 0.2 });
      sec._io.observe(sec);
    }
  };
  const all = () => secs.forEach(draw);
  window.__decoLines = all;
  all(); addEventListener('resize', () => { clearTimeout(all.t); all.t = setTimeout(all, 150); });
})();
