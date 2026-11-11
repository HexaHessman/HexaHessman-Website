// Product pages (client's PDF, 2026-11-11): a round Back button and a "Contact <name>" pill float bottom right, lined up
// with the header's right edge. The pill opens a card with the person's photo, title and email.
// Back works as before (back-btn.js): it returns to the main Commodities page where the visitor left off.
// Usage: <script src="/assets/product-contact.js" data-up="/commodities/" data-spot="urea" data-name="…" data-role="…"
//         data-entity="…" data-email="…" data-photo="…" data-linkedin="…" defer></script>
(() => {
  const me = document.currentScript, d = (me && me.dataset) || {}, up = d.up || '/';
  const esc = s => String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const css = `.pc-dock { position: fixed; right: 22px; bottom: 22px; z-index: 40; display: flex; align-items: center; gap: 12px; font-family: 'Montserrat', var(--sans, system-ui);
      opacity: 0; transform: translateY(8px); transition: opacity .4s, transform .4s; }
    .pc-dock.on { opacity: 1; transform: none; }
    html.no-scroll .pc-dock { opacity: 0; pointer-events: none; }
    .pc-back, .pc-open { background: #FCFCFC; color: #0C1410; border: 1.6px solid #1B221F; cursor: pointer; box-shadow: 0 6px 22px rgba(0,0,0,.26); transition: background .2s, transform .2s; }
    .pc-back { width: 46px; height: 46px; border-radius: 50%; display: grid; place-items: center; padding: 0; }
    .pc-back svg { width: 22px; height: 22px; transition: transform .2s; }
    .pc-back:hover svg { transform: translateX(-3px); }
    .pc-open { height: 54px; border-radius: 999px; display: flex; align-items: center; gap: 10px; padding: 0 22px 0 8px; text-align: left; font: 700 13px/1.25 'Montserrat', var(--sans, system-ui); }
    .pc-open:hover, .pc-back:hover { background: #fff; transform: translateY(-1px); }
    .pc-open img { width: 44px; height: 44px; border-radius: 50%; object-fit: cover; object-position: 50% 12%; background: #1B221F; filter: grayscale(1); }
    .pc-open span { display: block; }
    .pc-veil { position: fixed; inset: 0; z-index: 90; display: grid; place-items: center; padding: 20px; background: rgba(60,66,63,.62); opacity: 0; pointer-events: none; transition: opacity .3s; font-family: 'Montserrat', var(--sans, system-ui); }
    .pc-veil.on { opacity: 1; pointer-events: auto; }
    .pc-card { position: relative; width: min(940px, 100%); background: #263C34; color: #fff; border-radius: 34px; padding: clamp(26px, 4vw, 56px); display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 6fr); gap: clamp(20px, 3vw, 44px); align-items: center;
      transform: translateY(14px) scale(.98); transition: transform .35s cubic-bezier(.2,.7,.2,1); box-shadow: 0 30px 80px rgba(0,0,0,.4); }
    .pc-veil.on .pc-card { transform: none; }
    .pc-x { position: absolute; left: 30px; top: 28px; width: 46px; height: 46px; border-radius: 50%; border: 2px solid #fff; background: none; color: #fff; cursor: pointer; display: grid; place-items: center; padding: 0; }
    .pc-x svg { width: 22px; height: 22px; }
    .pc-x:hover { background: rgba(255,255,255,.12); }
    .pc-photo { display: block; width: 100%; max-height: 62vh; object-fit: contain; object-position: 50% 100%; filter: grayscale(1) contrast(1.05); margin-top: 20px; }
    .pc-name { margin: 0; font-weight: 700; font-size: clamp(19px, 1.9vw, 24px); }
    .pc-role { margin: 6px 0 26px; font-weight: 400; font-size: clamp(17px, 1.8vw, 23px); line-height: 1.35; }
    .pc-line { display: flex; align-items: center; gap: 16px; margin-top: 14px; color: #fff; text-decoration: none; font-weight: 700; font-size: clamp(15px, 1.5vw, 19px); overflow-wrap: anywhere; }
    .pc-line i { flex: none; width: 38px; height: 38px; border-radius: 9px; background: #fff; color: #263C34; display: grid; place-items: center; }
    .pc-line i svg { width: 22px; height: 22px; }
    .pc-line:hover span { text-decoration: underline; text-underline-offset: 4px; }
    @media (max-width: 700px) { .pc-dock { right: 14px; bottom: 14px; gap: 8px; } .pc-back { width: 42px; height: 42px; } .pc-open { height: 48px; padding: 0 16px 0 6px; font-size: 12px; } .pc-open img { width: 38px; height: 38px; }
      .pc-card { grid-template-columns: 1fr; border-radius: 26px; padding: 76px 24px 30px; } .pc-photo { max-height: 34vh; margin-top: 0; } .pc-x { left: 20px; top: 18px; } }
    @media (prefers-reduced-motion: reduce) { .pc-dock, .pc-veil, .pc-card { transition: none; } }`;
  document.head.insertAdjacentHTML('beforeend', `<style>${css}</style>`);

  const dock = document.createElement('div'); dock.className = 'pc-dock';
  dock.innerHTML = `<button type="button" class="pc-back" aria-label="Go back"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg></button>`
    + (d.name ? `<button type="button" class="pc-open" aria-haspopup="dialog">${d.photo ? `<img src="${esc(d.photo)}" alt="">` : ''}<span>Contact<br>${esc(d.name)}</span></button>` : '');
  document.body.appendChild(dock);
  const align = () => { const bar = document.querySelector('.site-header .bar'); if (!bar) return;
    const r = bar.getBoundingClientRect(); if (r.width) dock.style.right = Math.max(10, document.documentElement.clientWidth - r.right) + 'px'; };
  align(); addEventListener('resize', align); addEventListener('load', align); setTimeout(align, 400);
  requestAnimationFrame(() => setTimeout(() => dock.classList.add('on'), 300));

  // ---- Back: to the main Commodities page, at the spot the visitor had scrolled to (as back-btn.js)
  const spot = d.spot;
  let ref = null; try { ref = document.referrer ? new URL(document.referrer) : null; } catch {}
  const fromSite = !!ref && ref.origin === location.origin && history.length > 1;
  dock.querySelector('.pc-back').addEventListener('click', () => {
    const stepBack = () => { const here = location.href; history.back(); setTimeout(() => { if (location.href === here) location.href = up; }, 600); };
    if (spot) {
      if (fromSite && ref.pathname === up) return stepBack();
      let saved = null; try { saved = sessionStorage.getItem('cs-y:' + up); sessionStorage.setItem('cs-restore', '1'); } catch {}
      location.href = saved !== null ? up : up + '#' + spot;
    } else if (fromSite) stepBack(); else location.href = up;
  });

  // ---- the contact card
  const open = dock.querySelector('.pc-open'); if (!open) return;
  const veil = document.createElement('div'); veil.className = 'pc-veil'; veil.setAttribute('role', 'dialog'); veil.setAttribute('aria-modal', 'true'); veil.setAttribute('aria-label', 'Contact ' + d.name);
  veil.innerHTML = `<div class="pc-card">
      <button type="button" class="pc-x" aria-label="Close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
      ${d.photo ? `<img class="pc-photo" src="${esc(d.photo)}" alt="${esc(d.name)}">` : '<span></span>'}
      <div>
        <p class="pc-name">${esc(d.name)}</p>
        <p class="pc-role">${esc(d.role)}${d.entity ? `<br>(${esc(d.entity)})` : ''}</p>
        ${d.email ? `<a class="pc-line" href="mailto:${esc(d.email)}"><i aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M4 7l8 6 8-6"/></svg></i><span>${esc(d.email)}</span></a>` : ''}
        ${d.linkedin ? `<a class="pc-line" href="${esc(d.linkedin)}" target="_blank" rel="noopener"><i aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M6.5 8.8H3.6V20h2.9V8.8zM5 4a1.7 1.7 0 100 3.4A1.7 1.7 0 005 4zm15.4 9.6c0-3-1.6-5-4.2-5-1.5 0-2.5.8-3 1.6V8.8h-2.8V20h2.9v-6c0-1.5.8-2.5 2-2.5 1.3 0 2 .9 2 2.5v6h3.1v-6.4z"/></svg></i><span>LinkedIn profile</span></a>` : ''}
      </div>
    </div>`;
  document.body.appendChild(veil);
  let last = null;
  const show = v => { veil.classList.toggle('on', v); document.documentElement.classList.toggle('pc-lock', v);
    if (window.__lenis) v ? window.__lenis.stop() : window.__lenis.start();
    if (v) { last = document.activeElement; veil.querySelector('.pc-x').focus(); } else if (last) last.focus(); };
  open.addEventListener('click', () => show(true));
  veil.querySelector('.pc-x').addEventListener('click', () => show(false));
  veil.addEventListener('click', e => { if (e.target === veil) show(false); });
  addEventListener('keydown', e => { if (e.key === 'Escape' && veil.classList.contains('on')) show(false); });
})();
