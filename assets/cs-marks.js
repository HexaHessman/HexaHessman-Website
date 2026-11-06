// Commodities scroll: the 3D drawing of the HexaHessman mark (logo.html?embed, as in the preloader), very faint
// behind the words. It sits behind every fourth product, tilted, turns as you scroll past and fades in and out,
// light enough not to distract. One shared iframe moves from product to product. Waits for cscroll.js to render.
(() => {
  if (innerWidth <= 900) return;   // desktop only: on phones the text column is too narrow behind the window
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let tries = 0;
  const start = () => {
    const items = [...document.querySelectorAll('#cscroll .cs-item')];
    if (!items.length) { if (tries++ < 60) setTimeout(start, 250); return; }
    // each run spans two products (e.g. Metallurgical Coke → Calcined Pet Coke); the mark travels down with the
    // reader through the run, turning slowly, fading in at its start and out at its end
    // runs, by product slug: first product → the one after it (user picked the last two, 2026-11-06)
    const START = ['sulphuric-acid', 'dap', 'metallurgical-coke', 'caustic-soda', 'base-oil', 'wood-chips'];
    const runs = START.map(id => { const i = items.findIndex(it => it.id === id); return i >= 0 && items[i + 1] ? [items[i], items[i + 1]] : null; }).filter(Boolean);
    const box = document.createElement('div'); box.className = 'cs-logo3d'; box.setAttribute('aria-hidden', 'true');
    box.innerHTML = '<iframe src="/logo.html?embed&ink=green&v=5" title="" tabindex="-1" loading="lazy"></iframe>';
    (document.getElementById('cscroll') || document.body).appendChild(box); const f = box.firstChild;
    let raf = 0, lastT = -1;
    const ease = x => x * x * (3 - 2 * x);
    const frame = () => {
      raf = 0; const vh = innerHeight; let hit = null;
      // the mark rides from the first product's centre down to the middle of the second (e.g. Caustic Soda → half of Soda Ash)
      for (const [a, b] of runs) {
        const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        const ca = ra.top + ra.height * 0.22, cb = rb.top + rb.height / 2;   // from the top of the first product to the middle of the next
        const t = (vh * 0.5 - ca) / (cb - ca);
        if (t > -0.4 && t < 1.08) { hit = { t, r: ra, ca, cb, k: runs.indexOf(runs.find(x => x[0] === a)) }; break; }
      }
      const setPause = v => { if (box._p !== v && f.contentWindow) { box._p = v; f.contentWindow.postMessage({ type: 'logo-pause', v }, '*'); } };
      if (!hit) { box.style.opacity = '0'; setPause(true); return; }
      const { t, r, ca, cb, k } = hit, tc = Math.min(1, Math.max(0, t));
      const turn = (k + tc) * 0.6;   // one continuous turn down the whole page: each run carries on from where the last ended, so it never flips back
      const o = Math.min(ease(Math.min(1, Math.max(0, (t + 0.4) / 0.4))), ease(Math.min(1, Math.max(0, (1.08 - t) / 0.3)))) * 0.25;
      box.style.opacity = o.toFixed(3);
      setPause(o < 0.004);
      box.style.left = (r.left + r.width * 0.6).toFixed(0) + 'px';
      box.style.top = (ca + (cb - ca) * tc).toFixed(0) + 'px';   // follows the reader down until the middle of the second product
      if (!reduce && Math.abs(turn - lastT) > 0.002 && f.contentWindow) { lastT = turn; f.contentWindow.postMessage({ type: o < 0.02 ? 'logo-scroll-set' : 'logo-scroll', p: turn }, '*'); }
    };
    const ask = () => { if (!raf) raf = requestAnimationFrame(frame); };
    addEventListener('scroll', ask, { passive: true }); addEventListener('resize', ask); f.addEventListener('load', ask); ask();
  };
  start();
})();
