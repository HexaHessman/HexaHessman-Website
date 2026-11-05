// Shared header for every page: logo, main navigation with the two division mega menus,
// the Request-a-quote button, and a mobile drawer. Links are root-relative so nested pages work.
// Usage: <script src="/assets/site-header.js" defer></script> anywhere in <body>.
(() => {
  const SITE = {
    commodities: {
      title: 'Commodities Supply', href: '/commodities/',
      footer: 'Direct-from-source supply across Southeast Asia and beyond.', footerLink: ['View all commodities', '/commodities/'],
      groups: [
        { title: 'Fertilizer & Phosphate Value Chain', href: '/commodities/#fertilizer-phosphate', anchor: true, items: [
          ['Sulphur', 'sulphur'], ['Sulphuric Acid', 'sulphuric-acid'], ['Phosphoric Acid', 'phosphoric-acid'], ['Rock Phosphate', 'rock-phosphate'],
          ['Mono Ammonium Phosphate (MAP)', 'map'], ['Diammonium Phosphate (DAP)', 'dap'], ['Urea', 'urea'], ['Ammonium Sulphate', 'ammonium-sulphate']] },
        { title: 'Metallurgical Reductants', href: '/commodities/#metallurgical-reductants', anchor: true, items: [
          ['Semi Coke', 'semi-coke'], ['Metallurgical Coke', 'metallurgical-coke'], ['Calcined Pet Coke', 'calcined-pet-coke'], ['Graphite Pet Coke', 'graphite-pet-coke']] },
        { title: 'Industrial Chemicals', href: '/commodities/#industrial-chemicals', anchor: true, items: [
          ['Methanol', 'methanol'], ['Caustic Soda', 'caustic-soda'], ['Soda Ash', 'soda-ash']] },
        { title: 'Petroleum & Oilfield Products', href: '/commodities/#petroleum-oilfield', anchor: true, items: [
          ['Bitumen', 'bitumen'], ['Base Oil', 'base-oil'], ['Barite Powder', 'barite-powder'], ['Bentonite', 'bentonite']] },
        { title: 'Biomass & Renewable Fuels', href: '/commodities/#biomass', anchor: true, items: [
          ['Wood Chips', 'wood-chips'], ['Coconut Shell Charcoal', 'coconut-shell-charcoal']] },
      ],
    },
    engineering: {
      title: 'Engineering Solutions', href: '/engineering/',
      footer: '48-hour face-to-face response for servicing and maintenance enquiries.', footerLink: ['View Engineering Solutions', '/engineering/'],
      groups: [
        { title: 'Principals we represent', items: [
          ['ShibataFenderTeam — fender systems', '/engineering/shibata/'], ['MannTek — transfer & bunkering couplings', '/engineering/manntek/'],
          ['Straatman — mooring systems', '/engineering/straatman/'], ['Raythink — gas-leak detection & monitoring', '/engineering/raythink/']] },
        { title: 'Products & services', items: [
          ['Engineering Components', '/engineering/#components'], ['Storage Tank Solutions', '/engineering/#services'],
          ['Project Management & EPC Support', '/engineering/#services'], ['After-sales service & maintenance', '/engineering/#services']] },
      ],
    },
  };
  const LOGO = `<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="miter" aria-hidden="true">
      <rect x="2.5" y="3" width="13" height="42"/><rect x="5.5" y="6" width="7" height="36" stroke-width="1"/>
      <rect x="32.5" y="3" width="13" height="42"/><rect x="35.5" y="6" width="7" height="36" stroke-width="1"/>
      <path d="M24 9.5 L38.5 24 L24 38.5 L9.5 24 Z"/><path d="M24 14 L34 24 L24 34 L14 24 Z" stroke-width="1"/></svg>`;
  const path = location.pathname.replace(/index\.html$/, '');
  const active = (href) => (href === '/' ? path === '/' : path.startsWith(href)) ? ' class="active"' : '';
  const link = (label, href, group) => `<a href="${group ? (group.anchor ? '/commodities/#' + href : group.href + href + '/') : href}">${label}</a>`;

  function mega(key) {
    const d = SITE[key];
    return `<div class="mega" data-menu="${key}" hidden>
      <div class="mega-inner">
        <div class="mega-cols cols-${d.groups.length}">
          ${d.groups.map(g => `<div class="mega-col"><h4>${g.href ? `<a href="${g.href}">${g.title}</a>` : g.title}</h4><ul>${g.items.map(([l, h]) => `<li>${link(l, h, g.href ? g : null)}</li>`).join('')}</ul></div>`).join('')}
        </div>
        <div class="mega-foot"><span>${d.footer}</span><a href="${d.footerLink[1]}">${d.footerLink[0]} →</a></div>
      </div></div>`;
  }
  function drawer() {
    const sec = (key) => { const d = SITE[key]; return `<details><summary>${d.title}</summary>
      ${d.groups.map(g => `<div class="drawer-group"><div class="drawer-group-title">${g.href ? `<a href="${g.href}">${g.title}</a>` : g.title}</div>${g.items.map(([l, h]) => link(l, h, g.href ? g : null)).join('')}</div>`).join('')}
      <a class="drawer-all" href="${d.href}">${d.footerLink[0]} →</a></details>`; };
    return `<div class="drawer" hidden>
      <a href="/">Home</a>${sec('commodities')}${sec('engineering')}<a href="/about/">About</a><a href="/contact/">Contact</a>
      <a class="btn primary drawer-cta" href="/contact/#quote"><span>Request</span><span>a quote</span></a>
      <div class="drawer-meta">inquiry@hexahessman.com · +65 8506 6316</div></div>`;
  }

  const html = `<header class="site-header">
    <div class="bar">
      <a class="logo-link" href="/" aria-label="HexaHessman home">${LOGO}<span class="word">HexaHessman</span></a>
      <nav class="nav">
        <a href="/"${active('/')}>Home</a>
        <a href="/commodities/" data-menu="commodities"${active('/commodities/')}>Commodities Supply<i class="chev"></i></a>
        <a href="/engineering/" data-menu="engineering"${active('/engineering/')}>Engineering Solutions<i class="chev"></i></a>
        <a href="/about/"${active('/about/')}>About</a>
        <a href="/contact/"${active('/contact/')}>Contact</a>
      </nav>
      <div class="actions"><a class="btn primary" href="/contact/#quote"><span>Request</span><span>a quote</span></a></div>
      <button class="menu-btn" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
    </div>
    ${mega('commodities')}${mega('engineering')}${drawer()}
  </header>`;

  const mount = document.getElementById('site-header') || document.body;
  if (mount === document.body) document.body.insertAdjacentHTML('afterbegin', html); else mount.outerHTML = html;

  // mega menus: open on hover/focus over the trigger or the panel, close when the pointer leaves both
  const header = document.querySelector('.site-header');
  // a menu link to a section of the page we are already on: close the menus and glide there instead of reloading
  header.addEventListener('click', (e) => {
    const a = e.target.closest('a[href*="#"]'); if (!a) return;
    const u = new URL(a.href, location.href);
    if (u.pathname !== location.pathname || !u.hash || !window.__csJump) return;
    e.preventDefault();
    header.querySelectorAll('.mega').forEach(m => m.hidden = true); header.classList.remove('menu-open');
    const dr = header.querySelector('.drawer'); if (dr && !dr.hidden) { dr.hidden = true; header.classList.remove('drawer-open'); document.documentElement.classList.remove('no-scroll'); const b = header.querySelector('.menu-btn'); b && b.setAttribute('aria-expanded', 'false'); }
    history.replaceState(null, '', u.hash); window.__csJump(u.hash, true);
  });
  // tighten the top gap once the page has scrolled (the header itself stays fixed on every page)
  const onScroll = () => header.classList.toggle('scrolled', scrollY > 40);
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  const megas = [...header.querySelectorAll('.mega')];
  let closeT = 0;
  const open = (key) => { clearTimeout(closeT); megas.forEach(m => { m.hidden = m.dataset.menu !== key; }); header.classList.add('menu-open'); };
  const close = () => { closeT = setTimeout(() => { megas.forEach(m => m.hidden = true); header.classList.remove('menu-open'); }, 140); };
  header.querySelectorAll('.nav a[data-menu]').forEach(a => {
    a.addEventListener('pointerenter', () => open(a.dataset.menu)); a.addEventListener('focus', () => open(a.dataset.menu)); a.addEventListener('pointerleave', close);
  });
  megas.forEach(m => { m.addEventListener('pointerenter', () => open(m.dataset.menu)); m.addEventListener('pointerleave', close); });
  header.addEventListener('focusout', (e) => { if (!header.contains(e.relatedTarget)) close(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') { megas.forEach(m => m.hidden = true); header.classList.remove('menu-open'); } });

  // mobile drawer
  const btn = header.querySelector('.menu-btn'), dr = header.querySelector('.drawer');
  btn.addEventListener('click', () => { const on = dr.hidden; dr.hidden = !on; btn.setAttribute('aria-expanded', String(on)); header.classList.toggle('drawer-open', on); document.documentElement.classList.toggle('no-scroll', on); });
})();
