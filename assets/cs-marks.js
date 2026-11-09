// Commodities scroll: the 3D drawing of the HexaHessman mark (logo.html?embed, as in the preloader), very faint
// behind the words. It travels down through each section (from under its title), tilted, turns as you scroll past and fades in and out,
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
    const runs = [...document.querySelectorAll('#cscroll .cs-chapter')].map(ch => { const its = [...ch.querySelectorAll('.cs-item')]; return its.length ? [its[0], its[its.length - 1], ch.querySelector('.cs-items') || its[0]] : null; }).filter(Boolean);
    const box = document.createElement('div'); box.className = 'cs-logo3d'; box.setAttribute('aria-hidden', 'true');
    box.innerHTML = '<iframe src="/logo.html?embed&ink=green&center&zoom=2&spin=' + (reduce ? 0 : 16) + '&v=7" title="" tabindex="-1" loading="lazy"></iframe>';
    (document.getElementById('cscroll') || document.body).appendChild(box); const f = box.firstChild;
    let raf = 0, lastT = -1;
    const ease = x => x * x * (3 - 2 * x);
    const frame = () => {
      raf = 0; const vh = innerHeight; let hit = null;
      // the mark rides from the first product's centre down to the middle of the second (e.g. Caustic Soda → half of Soda Ash)
      for (const [a, b, start] of runs) {
        const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        const ca = ra.top + ra.height * 0.22, cb = rb.top + rb.height * 0.6;   // from the top of the section's first product to its last
        const t = (vh * 0.5 - ca) / (cb - ca);
        if (t > -0.4 && t < 1.08) { hit = { t, r: (a.querySelector('.cs-text') || a).getBoundingClientRect(), cut: start.getBoundingClientRect().top, pan: (a.closest('.cs-chapter').querySelector('.cs-panel') || a).getBoundingClientRect(), ca, cb, k: runs.indexOf(runs.find(x => x[0] === a)), dir: a.closest('.text-right') ? 1 : -1 }; break; }
      }
      const setPause = v => { if (box._p !== v && f.contentWindow) { box._p = v; f.contentWindow.postMessage({ type: 'logo-pause', v }, '*'); } };
      if (!hit) { box.style.opacity = '0'; setPause(true); return; }
      const { t, r, cut, pan, ca, cb, k, dir } = hit, tc = Math.min(1, Math.max(0, t));
      const o = Math.min(ease(Math.min(1, Math.max(0, (t + 0.4) / 0.4))), ease(Math.min(1, Math.max(0, (1.08 - t) / 0.3)))) * 0.2;
      box.style.opacity = o.toFixed(3);
      setPause(o < 0.004);
      // it glides in from the outer edge on the text's side (text on the left: from the left; picture on the left: from
      // the right), settles behind the words and keeps drifting a little the same way (user, 2026-11-06)
      // it glides in from the outer edge on the text's side and settles centred on the words, staying there
      // (no drift toward the middle; client, 2026-11-07)
      const slide = ease(Math.min(1, Math.max(0, (t + 0.4) / 0.75)));
      const off = 0;   // no gliding in or sinking: it stays put behind the words and spins on its own, 2x bigger (client, 2026-11-08)
      // sized to the words column and centred in it, so it sits behind the words and buttons, not the photo (client, 2026-11-07)
      const colL = dir < 0 ? 0 : pan.right, colR = dir < 0 ? pan.left : innerWidth, colW = colR - colL;
      const size = Math.round(Math.min(colW * 1.25, vh * 1.25));
      if (box._w !== size) { box._w = size; box.style.width = size + 'px'; }
      box.style.left = (colL + colW * 0.5 + off).toFixed(0) + 'px';   // (?center: the drawing sits in its frame's centre)
      box.style.top = (vh * 0.5).toFixed(0) + 'px';
      // never over the section's title: hidden above the line where the products start, and comes out from under it
      const topPx = vh * 0.5, half = box.offsetHeight / 2, edge = cut - (topPx - half);
      const vm = edge > -160 ? `linear-gradient(to bottom, transparent ${edge.toFixed(0)}px, #000 ${(edge + 160).toFixed(0)}px)` : 'linear-gradient(#000, #000)';
      // and never onto the photo: it fades out before the picture's edge, keeping to the words and buttons (client, 2026-11-07)
      const bx = parseFloat(box.style.left) - box.offsetWidth / 2, GAP = 36, SOFT = 180;
      const hm = dir < 0
        ? `linear-gradient(to right, #000 ${(pan.left - GAP - SOFT - bx).toFixed(0)}px, transparent ${(pan.left - GAP - bx).toFixed(0)}px)`
        : `linear-gradient(to right, transparent ${(pan.right + GAP - bx).toFixed(0)}px, #000 ${(pan.right + GAP + SOFT - bx).toFixed(0)}px)`;
      const m = vm + ', ' + hm;
      if (box._m !== m) { box._m = m; box.style.webkitMaskImage = m; box.style.maskImage = m; box.style.webkitMaskComposite = 'source-in'; box.style.maskComposite = 'intersect'; }
    };
    const ask = () => { if (!raf) raf = requestAnimationFrame(frame); };
    addEventListener('scroll', ask, { passive: true }); addEventListener('resize', ask); f.addEventListener('load', ask); ask();
  };
  start();
})();
