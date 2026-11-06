// Two small behaviours on the principal pages:
//  - [data-spin] pictures hold a 360° turntable clip; the frame shown follows the picture's place on screen (about one
//    and a quarter turns while it crosses the viewport), so the part turns as you scroll;
//  - .spin-row (the fuel tiles) gets an 'in' class when it scrolls into view (the tiles rise / drop into place in CSS),
//    and each tile is a button that opens its drop-down under the row, one at a time.
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.spin-row').forEach(row => {
    const tiles = [...row.querySelectorAll('[aria-controls]')], panels = tiles.map(t => document.getElementById(t.getAttribute('aria-controls')));
    tiles.forEach((t, i) => t.addEventListener('click', () => {
      const open = t.getAttribute('aria-expanded') !== 'true';
      tiles.forEach((o, j) => { const on = open && j === i; o.setAttribute('aria-expanded', String(on)); panels[j].classList.toggle('open', on); panels[j].setAttribute('aria-hidden', String(!on)); });
    }));
    new IntersectionObserver(([e], io) => { if (e.isIntersecting) { row.classList.add('in'); io.disconnect(); } }, { threshold: 0.25 }).observe(row);
  });
  // photos with layered orange panels: the panels rise into place one by one once the photo is on screen
  document.querySelectorAll('.zig-layers').forEach(f => new IntersectionObserver(([e], io) => { if (e.isIntersecting) { f.classList.add('in'); io.disconnect(); } }, { threshold: 0.4 }).observe(f));
  // clips that play once each time they come into view (the SPC fenders being fitted) and rest on their last frame
  document.querySelectorAll('video.zig-appear').forEach(v => new IntersectionObserver(([e]) => {
    if (e.isIntersecting) { v.currentTime = 0; v.play().catch(() => {}); } else { v.pause(); v.currentTime = 0; }
  }, { threshold: 0.45 }).observe(v));
  // labelled diagrams: the labels pop out one by one once the picture is well on screen
  document.querySelectorAll('.dg').forEach(dg => new IntersectionObserver(([e], io) => { if (e.isIntersecting) { dg.classList.add('in'); io.disconnect(); } }, { threshold: 0.45 }).observe(dg));
  // [data-spin]: a 360° turntable stored as still frames (<base>000.webp … ); the frame drawn follows the picture's place
  // on screen — about one and a quarter turns while it crosses the viewport — eased so it glides (the way Apple does it)
  const spins = [...document.querySelectorAll('[data-spin]')].map((el, k) => {
    const n = +el.dataset.frames || 96, base = el.dataset.spin, cv = el.querySelector('canvas'), ctx = cv.getContext('2d');
    const imgs = Array.from({ length: n }, (_, i) => { const im = new Image(); im.decoding = 'async'; im.src = `${base}${String(i).padStart(3, '0')}.webp`; return im; });
    imgs[0].onload = () => el.classList.add('ready');
    return { el, n, imgs, ctx, cur: 0, drawn: -1, phase: k * 0.17 };
  });
  if (!spins.length) return;
  const target = s => { const r = s.el.getBoundingClientRect(); return (innerHeight - r.top) / (innerHeight + r.height) * 1.25 + s.phase; };
  spins.forEach(s => { s.cur = target(s); });
  const frame = () => {
    for (const s of spins) {
      const r = s.el.getBoundingClientRect(); if (r.bottom < -100 || r.top > innerHeight + 100) continue;
      const t = target(s); s.cur += reduce ? t - s.cur : (t - s.cur) * 0.14;
      let i = Math.round((((s.cur % 1) + 1) % 1) * s.n) % s.n;
      if (!s.imgs[i].complete || !s.imgs[i].naturalWidth) {   // not loaded yet: show the nearest frame that is
        for (let d = 1; d < s.n; d++) { const j = (i - d + s.n) % s.n; if (s.imgs[j].complete && s.imgs[j].naturalWidth) { i = j; break; } }
      }
      if (i !== s.drawn && s.imgs[i].complete && s.imgs[i].naturalWidth) { s.ctx.drawImage(s.imgs[i], 0, 0, 760, 760); s.drawn = i; s.el.classList.add('ready'); }
    }
    requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
})();
