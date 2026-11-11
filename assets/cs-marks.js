// Commodities scroll: the 3D drawing of the HexaHessman mark (logo.html?embed, as in the preloader), very faint
// behind the words. It travels down through each section (from under its title), tilted, turns as you scroll past and fades in and out,
// light enough not to distract. One shared iframe moves from group to group. Waits for cscroll.js to render.
(() => {
  if (innerWidth <= 900) return;   // desktop only: on phones the text column is too narrow behind the window
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let tries = 0;
  const start = () => {
    const chs = [...document.querySelectorAll('#cscroll .cs-chapter')];
    if (!chs.length || !document.querySelector('#cscroll .cs-item')) { if (tries++ < 60) setTimeout(start, 250); return; }
    const box = document.createElement('div'); box.className = 'cs-logo3d'; box.setAttribute('aria-hidden', 'true');
    box.innerHTML = '<iframe src="/logo.html?embed&ink=green&center&zoom=2&spin=' + (reduce ? 0 : 16) + '&v=7" title="" tabindex="-1" loading="lazy"></iframe>';
    (document.getElementById('cscroll') || document.body).appendChild(box); const f = box.firstChild;
    let raf = 0, lastT = -1;
    const ease = x => x * x * (3 - 2 * x);
    const frame = () => {
      raf = 0; const vh = innerHeight; let hit = null;
      // one group screen at a time (client, 2026-11-11): the mark fades in as the screen arrives, stays behind its words
      // while it is pinned, and fades out as it leaves
      for (const ch of chs) {
        const pin = ch.querySelector('.cs-pin').getBoundingClientRect();
        if (pin.bottom > vh * 0.15 && pin.top < vh * 0.85) { hit = { pin, cut: ch.querySelector('.cs-list').getBoundingClientRect().top, pan: ch.querySelector('.cs-panel').getBoundingClientRect(), dir: ch.classList.contains('text-right') ? 1 : -1 }; break; }
      }
      const setPause = v => { if (box._p !== v && f.contentWindow) { box._p = v; f.contentWindow.postMessage({ type: 'logo-pause', v }, '*'); } };
      if (!hit) { box.style.opacity = '0'; setPause(true); return; }
      const { pin, cut, pan, dir } = hit;
      const o = ease(Math.min(1, Math.max(0, 1 - Math.abs(pin.top) / (vh * 0.6)))) * 0.2;
      box.style.opacity = o.toFixed(3);
      setPause(o < 0.004);
      const off = 0;   // it stays put behind the words and spins on its own (client, 2026-11-08)
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
