// Commodities scroll: the 3D drawing of the HexaHessman mark (logo.html?embed, as in the preloader), very faint
// behind the words. It travels down through each section, tilted, turns as you scroll past and fades in and out,
// light enough not to distract. One shared iframe moves from product to product. Waits for cscroll.js to render.
(() => {
  if (innerWidth <= 900) return;   // desktop only: on phones the text column is too narrow behind the window
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let tries = 0;
  const start = () => {
    const items = [...document.querySelectorAll('#cscroll .cs-item')];
    if (!items.length) { if (tries++ < 60) setTimeout(start, 250); return; }
    // one run per section (client, 2026-11-07): the mark is there from the section's first product and travels slowly
    // down with the reader all the way to its last product, turning, fading in at the start and out at the end
    const runs = [...document.querySelectorAll('#cscroll .cs-chapter')].map(ch => { const its = [...ch.querySelectorAll('.cs-item')]; return its.length ? [its[0], its[its.length - 1]] : null; }).filter(Boolean);
    const box = document.createElement('div'); box.className = 'cs-logo3d'; box.setAttribute('aria-hidden', 'true');
    box.innerHTML = '<iframe src="/logo.html?embed&ink=green&v=6" title="" tabindex="-1" loading="lazy"></iframe>';
    (document.getElementById('cscroll') || document.body).appendChild(box); const f = box.firstChild;
    let raf = 0, lastT = -1;
    const ease = x => x * x * (3 - 2 * x);
    const frame = () => {
      raf = 0; const vh = innerHeight; let hit = null;
      // the mark rides from the first product's centre down to the middle of the second (e.g. Caustic Soda → half of Soda Ash)
      for (const [a, b] of runs) {
        const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        const ca = ra.top + ra.height * 0.22, cb = rb.top + rb.height * 0.6;   // from the top of the section's first product to its last
        const t = (vh * 0.5 - ca) / (cb - ca);
        if (t > -0.4 && t < 1.08) { hit = { t, r: ra, ca, cb, k: runs.indexOf(runs.find(x => x[0] === a)), dir: a.closest('.text-right') ? 1 : -1 }; break; }
      }
      const setPause = v => { if (box._p !== v && f.contentWindow) { box._p = v; f.contentWindow.postMessage({ type: 'logo-pause', v }, '*'); } };
      if (!hit) { box.style.opacity = '0'; setPause(true); return; }
      const { t, r, ca, cb, k, dir } = hit, tc = Math.min(1, Math.max(0, t));
      const turn = (k + tc) * 0.6;   // one continuous turn down the whole page: each run carries on from where the last ended, so it never flips back
      const o = Math.min(ease(Math.min(1, Math.max(0, (t + 0.4) / 0.4))), ease(Math.min(1, Math.max(0, (1.08 - t) / 0.3)))) * 0.2;
      box.style.opacity = o.toFixed(3);
      setPause(o < 0.004);
      // it glides in from the outer edge on the text's side (text on the left: from the left; picture on the left: from
      // the right), settles behind the words and keeps drifting a little the same way (user, 2026-11-06)
      const slide = ease(Math.min(1, Math.max(0, (t + 0.4) / 0.75)));
      const off = dir * innerWidth * (0.42 * (1 - slide) - 0.07 * tc);
      box.style.left = (r.left + r.width * 0.5 + off).toFixed(0) + 'px';
      box.style.top = (vh * (0.3 + 0.4 * tc)).toFixed(0) + 'px';   // sinks slowly down the screen as the reader goes through the section
      if (!reduce && Math.abs(turn - lastT) > 0.002 && f.contentWindow) { lastT = turn; f.contentWindow.postMessage({ type: o < 0.02 ? 'logo-scroll-set' : 'logo-scroll', p: turn }, '*'); }
    };
    const ask = () => { if (!raf) raf = requestAnimationFrame(frame); };
    addEventListener('scroll', ask, { passive: true }); addEventListener('resize', ask); f.addEventListener('load', ask); ask();
  };
  start();
})();
