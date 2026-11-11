// "Back to top" button on the main pages only (Commodities, Engineering, About, Contact; client, 2026-11-10): the same
// white pill as the Back button on the product and principal pages, bottom right, its right edge lined up with the
// header bar. It shows once the page has scrolled past the first screen.
(() => {
  const css = `.top-btn { position: fixed; right: 22px; bottom: 22px; z-index: 40; display: inline-flex; align-items: center; justify-content: center;
      width: 48px; height: 48px; padding: 0; border-radius: 50%; border: 1px solid rgba(15,42,30,.12);
      background: #FCFCFC; color: #0F2A1E; font: 500 14px/1 var(--sans, system-ui); letter-spacing: .01em; cursor: pointer;
      box-shadow: 0 6px 24px rgba(0,0,0,.28); opacity: 0; pointer-events: none; transform: translateY(8px);
      transition: opacity .4s, transform .4s, background .2s, border-color .2s; }
    .top-btn.on { opacity: 1; pointer-events: auto; transform: none; }
    .top-btn:hover { background: #fff; border-color: rgba(15,42,30,.3); }
    .top-btn:focus-visible { outline: 2px solid #FCFCFC; outline-offset: 3px; }
    .top-btn svg { width: 20px; height: 20px; transition: transform .2s; }
    .top-btn:hover svg { transform: translateY(-3px); }
    html.no-scroll .top-btn { opacity: 0; pointer-events: none; }
    @media (max-width: 600px) { .top-btn { bottom: 14px; width: 44px; height: 44px; } }
    @media (prefers-reduced-motion: reduce) { .top-btn, .top-btn svg { transition: none; } }`;
  document.head.insertAdjacentHTML('beforeend', `<style>${css}</style>`);
  const b = document.createElement('button');
  b.type = 'button'; b.className = 'top-btn'; b.setAttribute('aria-label', 'Back to top');
  b.innerHTML = '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M10 16V4M5 9l5-5 5 5"/></svg>';   // just the arrow in a circle (client, 2026-11-11)
  document.body.appendChild(b);
  const align = () => { const bar = document.querySelector('.site-header .bar'); if (!bar) return;
    const r = bar.getBoundingClientRect(); if (r.width) b.style.right = Math.max(10, document.documentElement.clientWidth - r.right) + 'px'; };
  align(); addEventListener('resize', align); addEventListener('load', align); setTimeout(align, 400);
  const show = () => b.classList.toggle('on', scrollY > innerHeight * 0.9);
  addEventListener('scroll', show, { passive: true }); show();
  b.addEventListener('click', () => {
    if (window.__lenis) window.__lenis.scrollTo(0, { duration: 1.4 });
    else scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  });
})();
