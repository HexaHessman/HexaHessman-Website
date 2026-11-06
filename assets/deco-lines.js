// Terminal-style lines in the big empty bands (each page's closing call-to-action, section#cta): two thin rounded
// step lines run in from the top and the sides, and a short light travels along each. Drawn to the section's size.
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
    const left = [[w * (narrow ? 0.46 : 0.42), -2], [w * (narrow ? 0.46 : 0.42), h * 0.2], [w * 0.1, h * 0.2], [w * 0.1, h * 0.62], [w * 0.06, h * 0.66], [-2, h * 0.66]];
    const right = [[w * (narrow ? 0.7 : 0.64), -2], [w * (narrow ? 0.7 : 0.64), h * 0.3], [w * 0.93, h * 0.3], [w * 0.93, h * 0.58], [w + 2, h * 0.58]];
    [left, right].forEach((pts, i) => {
      const d = round(pts, r);
      const base = document.createElementNS(NS, 'path'); base.setAttribute('d', d); base.setAttribute('class', 'dl-line'); svg.appendChild(base);
      if (reduce) return;
      const run = document.createElementNS(NS, 'path'); run.setAttribute('d', d); run.setAttribute('class', 'dl-run'); svg.appendChild(run);
      const L = run.getTotalLength(); run.style.strokeDasharray = `${Math.min(140, L * 0.12).toFixed(0)} ${L.toFixed(0)}`;
      run.animate([{ strokeDashoffset: L * 0.12 + 140 }, { strokeDashoffset: -L }], { duration: 5200 + i * 1400, iterations: Infinity, easing: 'cubic-bezier(.45,.05,.4,1)', delay: i * 1600 });
    });
  };
  const all = () => secs.forEach(draw);
  all(); addEventListener('resize', () => { clearTimeout(all.t); all.t = setTimeout(all, 150); });
})();
