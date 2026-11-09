// Floating back button (white, bottom-right; user, 2026-11-08) on the product and principal pages: returns to the page the visitor came from, where they were
// on it. Landed here from outside the site (a search, a shared link)? Then it opens the page one level up instead.
// Usage: <script src="/assets/back-btn.js" data-up="/commodities/" data-spot="urea" defer></script>
(() => {
  const me = document.currentScript, up = (me && me.dataset.up) || '/';
  const css = `.back-btn { position: fixed; right: 22px; bottom: 22px; z-index: 40; display: inline-flex; align-items: center; gap: 10px;
      height: 46px; padding: 0 18px 0 14px; border-radius: 999px; border: 1px solid rgba(15,42,30,.12);
      background: #FCFCFC; color: #0F2A1E; font: 500 14px/1 var(--sans, system-ui); letter-spacing: .01em; cursor: pointer;
      -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px); box-shadow: 0 6px 24px rgba(0,0,0,.28);
      opacity: 0; transform: translateY(8px); transition: opacity .4s, transform .4s, background .2s, border-color .2s; }
    .back-btn.on { opacity: 1; transform: none; }
    .back-btn:hover { background: #fff; border-color: rgba(15,42,30,.3); }
    .back-btn:focus-visible { outline: 2px solid #FCFCFC; outline-offset: 3px; }
    .back-btn svg { width: 18px; height: 18px; transition: transform .2s; }
    .back-btn:hover svg { transform: translateX(-3px); }
    html.no-scroll .back-btn { opacity: 0; pointer-events: none; }
    @media (max-width: 600px) { .back-btn { right: 14px; bottom: 14px; height: 42px; padding: 0 15px 0 12px; font-size: 13px; } }
    @media (prefers-reduced-motion: reduce) { .back-btn, .back-btn svg { transition: none; } }`;
  document.head.insertAdjacentHTML('beforeend', `<style>${css}</style>`);
  const b = document.createElement('button');
  b.type = 'button'; b.className = 'back-btn'; b.setAttribute('aria-label', 'Go back');
  b.innerHTML = '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M16 10H4M9 5l-5 5 5 5"/></svg><span>Back</span>';
  document.body.appendChild(b);
  requestAnimationFrame(() => setTimeout(() => b.classList.add('on'), 300));

  // Commodities products (data-spot = the product's slug): Back always returns to the main Commodities page, at the
  // spot the visitor had scrolled to (cscroll.js keeps it); never been there? then it lands on this product in the list
  // (client, 2026-11-07). Other pages: step back in history, or one level up when they came from outside the site.
  const spot = me && me.dataset.spot;
  let ref = null; try { ref = document.referrer ? new URL(document.referrer) : null; } catch {}
  const fromSite = !!ref && ref.origin === location.origin && history.length > 1;
  b.addEventListener('click', () => {
    if (spot) {
      if (fromSite && ref.pathname === up) { const here = location.href; history.back(); setTimeout(() => { if (location.href === here) location.href = up; }, 600); return; }
      let saved = null; try { saved = sessionStorage.getItem('cs-y:' + up); sessionStorage.setItem('cs-restore', '1'); } catch {}
      location.href = saved !== null ? up : up + '#' + spot;
      return;
    }
    if (fromSite) {
      const here = location.href;
      history.back();
      setTimeout(() => { if (location.href === here) location.href = up; }, 600);   // nothing to go back to after all
    } else location.href = up;
  });
})();
