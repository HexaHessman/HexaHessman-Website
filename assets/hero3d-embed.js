// Mounts the scroll-driven 3D hero on a group page. The page gives an empty <section id="hero-3d">;
// this fills it with a sticky iframe of the scene (sulphur3d.html in embed mode) and posts the section's
// scroll progress to it, so the grab (fertilizer) or the bags (reductants) move as the visitor scrolls.
(() => {
  const sec = document.getElementById('hero-3d'); if (!sec) return;
  const path = location.pathname;
  const mode = sec.dataset.mode || (path.includes('metallurgical-reductants') ? 'bags' : 'grab');
  const copy = sec.dataset.copy !== 'off';
  // pull the title block out of the plain hero that follows, so the scene carries the page's own words
  const plain = sec.nextElementSibling && sec.nextElementSibling.classList.contains('hero') ? sec.nextElementSibling : null;
  let copyHTML = '';
  if (copy && plain) {
    const crumbs = plain.querySelector('.crumbs'), eyebrow = plain.querySelector('.eyebrow'), h1 = plain.querySelector('h1');
    copyHTML = `<div class="hero-3d-copy">${crumbs ? crumbs.outerHTML : ''}${eyebrow ? eyebrow.outerHTML : ''}${h1 ? h1.outerHTML : ''}</div>`;
    if (crumbs) crumbs.remove(); if (eyebrow) eyebrow.remove(); if (h1) h1.remove();
    plain.classList.add('after-3d');
  }
  sec.innerHTML = `<div class="hero-3d-sticky">
    <iframe src="/sulphur3d.html?mode=${mode}" title="${mode === 'bags' ? 'Jumbo bags moving through the yard' : 'A grab carrying sulphur over a ship\'s hold'}" aria-hidden="true" tabindex="-1"></iframe>
    ${copyHTML}
    <div class="scroll-cue"><span>Scroll</span><i><svg viewBox="0 0 24 24"><path d="M12 4v16M6 14l6 6 6-6"/></svg></i></div>
  </div>`;
  const frame = sec.querySelector('iframe');
  let last = -1, ready = false;
  frame.addEventListener('load', () => { ready = true; send(true); });
  function send(force) {
    const r = sec.getBoundingClientRect();
    const p = Math.min(1, Math.max(0, -r.top / Math.max(1, r.height - innerHeight)));
    if (!ready || (!force && Math.abs(p - last) < 0.0005)) return;
    last = p; frame.contentWindow && frame.contentWindow.postMessage({ type: 'hero-progress', p }, '*');
    sec.querySelector('.scroll-cue').style.opacity = p > 0.05 ? '0' : '';
  }
  addEventListener('scroll', () => send(false), { passive: true });
  addEventListener('resize', () => send(true));
})();
