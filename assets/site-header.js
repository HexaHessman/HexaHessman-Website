// Shared header for every page: logo, main navigation with the two division mega menus,
// the Request-a-quote button, and a mobile drawer. Links are root-relative so nested pages work.
// Usage: <script src="/assets/site-header.js" defer></script> anywhere in <body>.
(() => {
  // a group heading opens the main Commodities page at that group (jump), its products open their own pages (client, 2026-11-10)
  const SITE = {
    commodities: {
      title: 'Commodities Supply', href: '/commodities/',
      footer: 'Direct-from-source supply across Southeast Asia and beyond.', footerLink: ['View all commodities', '/commodities/'],
      groups: [
        { title: 'Fertilizer & Phosphate Value Chain', href: '/commodities/fertilizer-phosphate/', jump: '/commodities/#fertilizer-phosphate', items: [
          ['Sulphur', 'sulphur'], ['Sulphuric Acid', 'sulphuric-acid'], ['Phosphoric Acid', 'phosphoric-acid'], ['Rock Phosphate', 'rock-phosphate'],
          ['Mono Ammonium Phosphate', 'map'], ['Diammonium Phosphate', 'dap'], ['Urea', 'urea'], ['Ammonium Sulphate', 'ammonium-sulphate']] },
        { title: 'Metallurgical Reductants', href: '/commodities/metallurgical-reductants/', jump: '/commodities/#metallurgical-reductants', items: [
          ['Semi Coke', 'semi-coke'], ['Metallurgical Coke', 'metallurgical-coke'], ['Calcined Pet Coke', 'calcined-pet-coke'], ['Graphite Pet Coke', 'graphite-pet-coke']] },
        { title: 'Industrial Chemicals', href: '/commodities/industrial-chemicals/', jump: '/commodities/#industrial-chemicals', items: [
          ['Methanol', 'methanol'], ['Caustic Soda', 'caustic-soda'], ['Soda Ash', 'soda-ash']] },
        { title: 'Petroleum & Oilfield Products', href: '/commodities/petroleum-oilfield/', jump: '/commodities/#petroleum-oilfield', items: [
          ['Bitumen', 'bitumen'], ['Base Oil', 'base-oil'], ['Barite Powder', 'barite-powder'], ['Bentonite', 'bentonite']] },
        { title: 'Biomass & Renewable Fuels', href: '/commodities/biomass/', jump: '/commodities/#biomass', items: [
          ['Wood Chips', 'wood-chips'], ['Coconut Shell Charcoal', 'coconut-shell-charcoal']] },
      ],
    },
    engineering: {
      title: 'Engineering Solutions', href: '/engineering/',
      footer: '48-hour face-to-face response for servicing and maintenance enquiries.', footerLink: ['View Engineering Solutions', '/engineering/'],
      groups: [
        { title: '', items: [   // names only, as on the old site's menu (user, 2026-11-06); Storage Tank Fabrication removed (client, 2026-11-06)
          // the client's order (2026-11-12): Shibata, MannTek, Straatman. Raythink is hidden from the menu for now (its page is still built)
          ['Shibata Fenders Team', '/engineering/shibata/'], ['MannTek Solutions', '/engineering/manntek/'], ['Straatman Mooring Systems', '/engineering/straatman/']] },
      ],
    },
  };
  // the client's own logo (mark + HEXA / HESSMAN in Montserrat Bold), traced from the cover of their 2026 business profile (client, 2026-11-10)
  const LOGO = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="74 80 5681 1606" class="hh-lockup" aria-hidden="true"><g transform="translate(0.000000,1734.000000) scale(0.100000,-0.100000)"
fill="currentColor" stroke="none">
<path d="M780 8510 l0 -7990 2740 0 2740 0 0 2067 0 2068 940 -940 940 -940
970 970 970 970 0 -2098 0 -2097 2745 0 2745 0 0 7990 0 7990 -2740 0 -2740 0
0 -2102 0 -2103 -975 975 -975 975 -2867 -2868 -2868 -2867 1200 -1200 c660
-660 1203 -1200 1207 -1200 5 0 8 228 8 507 l0 508 -692 692 -693 693 1053
1053 1052 1052 0 -4688 0 -4687 -2020 0 -2020 0 0 7270 0 7270 2020 0 2020 0
0 -1557 0 -1558 360 360 360 360 0 1557 0 1558 -2740 0 -2740 0 0 -7990z
m14070 0 l0 -7270 -2020 0 -2020 0 0 2102 0 2103 1532 1532 1533 1533 -1173
1172 -1172 1173 0 -515 0 -515 660 -660 660 -660 -2347 -2347 c-1292 -1292
-2352 -2348 -2358 -2348 -5 0 -432 422 -947 937 l-938 938 0 2825 0 2825 940
940 940 940 975 -975 975 -975 0 -2245 0 -2245 360 360 360 360 0 4142 0 4143
2020 0 2020 0 0 -7270z"/>
<path d="M16570 11205 l0 -2915 738 2 737 3 3 1133 2 1132 1205 0 1205 0 0
-1135 0 -1135 740 0 740 0 0 2915 0 2915 -740 0 -740 0 0 -1200 0 -1200 -1205
0 -1205 0 -2 1198 -3 1197 -737 3 -738 2 0 -2915z"/>
<path d="M22895 14108 c-3 -7 -4 -1318 -3 -2913 l3 -2900 2323 -3 2322 -2 0
585 0 585 -1585 0 -1585 0 0 585 0 585 1390 0 1390 0 0 585 0 585 -1390 0
-1390 0 0 575 0 575 1540 0 1540 0 0 585 0 585 -2275 0 c-1811 0 -2277 -3
-2280 -12z"/>
<path d="M27893 14108 c2 -7 439 -648 971 -1425 l966 -1411 -1035 -1482 c-569
-816 -1035 -1486 -1035 -1491 0 -5 369 -8 856 -7 l857 3 622 920 c343 505 627
920 631 922 5 1 290 -413 634 -922 l625 -925 1547 0 c1028 0 1549 3 1553 10 3
6 100 247 215 538 l208 527 1274 0 1273 0 167 -430 c92 -236 185 -478 208
-537 l41 -108 790 0 c481 0 789 4 787 9 -1 5 -554 1317 -1228 2915 l-1225
2906 -757 0 c-588 0 -759 -3 -764 -12 -5 -7 -554 -1277 -1221 -2823 -666
-1545 -1216 -2808 -1220 -2806 -6 4 -1862 2704 -1950 2838 -14 21 30 87 936
1397 523 756 954 1382 957 1391 6 13 -84 15 -858 15 l-865 0 -562 -850 -563
-850 -272 410 c-149 226 -401 607 -561 848 l-290 437 -859 3 c-685 2 -857 0
-853 -10z m9315 -2545 c226 -587 410 -1068 408 -1070 -1 -2 -378 -2 -837 -1
l-835 3 420 1067 c232 588 423 1068 426 1068 3 0 191 -480 418 -1067z"/>
<path d="M30225 7953 c-1002 -65 -1764 -570 -1960 -1298 -80 -299 -72 -686 21
-964 88 -262 286 -530 511 -691 252 -179 957 -444 1639 -614 454 -114 705
-258 807 -466 31 -63 32 -69 32 -195 0 -127 -1 -132 -32 -195 -170 -346 -803
-407 -1550 -149 -456 158 -901 402 -1204 661 -31 26 -59 48 -62 48 -6 0 -572
-1120 -572 -1132 0 -24 356 -272 542 -377 190 -107 500 -245 719 -320 l91 -31
1246 0 1246 0 90 39 c682 296 1051 833 1051 1531 0 442 -129 779 -408 1071
-290 305 -600 459 -1362 678 -460 133 -556 163 -693 217 -269 107 -433 202
-509 295 -170 210 -128 501 89 617 306 163 910 91 1638 -195 147 -58 497 -224
604 -287 35 -20 65 -35 67 -33 12 12 554 1143 551 1151 -2 5 -54 40 -117 78
-534 321 -1141 508 -1810 558 -123 9 -543 11 -665 3z"/>
<path d="M35370 7953 c-980 -71 -1718 -541 -1938 -1233 -79 -249 -98 -588 -47
-843 86 -424 354 -787 721 -974 341 -174 920 -378 1464 -513 574 -144 841
-339 858 -629 17 -309 -187 -490 -601 -532 -591 -60 -1529 280 -2152 780 -55
44 -103 77 -107 73 -8 -9 -568 -1117 -568 -1125 0 -3 61 -52 135 -107 309
-232 675 -425 1087 -574 l128 -46 1253 0 1253 0 149 73 c607 298 921 729 976
1339 50 557 -135 1021 -543 1364 -279 234 -581 363 -1378 589 -690 196 -1001
350 -1101 547 -52 101 -61 243 -24 350 19 53 90 138 144 172 159 100 472 127
804 71 423 -72 1023 -291 1437 -525 51 -28 93 -50 95 -48 4 4 555 1149 555
1153 0 2 -49 32 -108 68 -554 332 -1133 512 -1826 567 -117 9 -556 11 -666 3z"/>
<path d="M38590 5070 l0 -2840 660 0 660 0 2 1806 3 1806 695 -1591 694 -1591
485 2 485 3 696 1593 695 1594 6 -1809 c3 -994 7 -1809 7 -1810 1 -2 295 -3
652 -3 l650 0 0 2840 0 2840 -806 -2 -805 -3 -784 -1720 c-431 -946 -787
-1726 -792 -1732 -5 -8 -293 613 -787 1700 -428 941 -785 1722 -793 1735 l-13
22 -805 0 -805 0 0 -2840z"/>
<path d="M16570 5065 l0 -2835 740 0 740 0 0 1055 0 1055 1205 0 1205 0 0
-1055 0 -1055 740 0 740 0 0 2835 0 2835 -740 0 -740 0 0 -1200 0 -1200 -1205
0 -1205 0 -2 1198 -3 1197 -737 3 -738 2 0 -2835z"/>
<path d="M22897 7893 c-4 -3 -7 -1279 -7 -2835 l0 -2828 2325 0 2325 0 0 505
0 505 -1585 0 -1585 0 0 585 0 585 1390 0 1390 0 0 585 0 585 -1390 0 -1390 0
0 575 0 575 1540 0 1540 0 0 585 0 585 -2273 0 c-1251 0 -2277 -3 -2280 -7z"/>
<path d="M46615 5074 c-671 -1555 -1221 -2831 -1223 -2835 -2 -5 338 -9 755
-9 l758 0 181 458 180 457 1274 0 1273 0 177 -455 176 -455 788 -3 c663 -2
787 0 783 12 -14 35 -2342 5558 -2362 5604 l-24 52 -758 0 -758 0 -1220 -2826z
m2351 268 l412 -1067 -419 -3 c-230 -1 -607 -1 -838 0 l-419 3 422 1071 c231
590 423 1070 426 1067 2 -2 190 -484 416 -1071z"/>
<path d="M52140 5065 l0 -2835 695 0 695 0 2 1711 3 1710 1276 -1708 1276
-1708 711 -3 712 -2 0 2835 0 2835 -690 0 -690 0 -2 -1793 -3 -1794 -1340
1793 -1340 1793 -652 1 -653 0 0 -2835z"/>
</g>
</svg>`;
  const path = location.pathname.replace(/index\.html$/, '');
  const active = (href) => (href === '/' ? path === '/' : path.startsWith(href)) ? ' class="active"' : '';
  const link = (label, href, group) => `<a href="${group ? group.href + href + '/' : href}">${label}</a>`;   // each product opens its own page (user, 2026-11-06)

  function mega(key) {
    const d = SITE[key];
    return `<div class="mega" data-menu="${key}" hidden>
      <div class="mega-inner">
        <div class="mega-cols cols-${d.groups.length}">
          ${d.groups.map(g => `<div class="mega-col">${g.title ? `<h4>${g.href ? `<a href="${g.jump || g.href}">${g.title}</a>` : g.title}</h4>` : ''}<ul>${g.items.map(([l, h]) => `<li>${link(l, h, g.href ? g : null)}</li>`).join('')}</ul></div>`).join('')}
        </div>
        <div class="mega-foot"><span>${d.footer}</span><a href="${d.footerLink[1]}">${d.footerLink[0]} →</a></div>
      </div></div>`;
  }
  function drawer() {
    // each division opens its own list in the small-screen menu, with a link to its main page (client, 2026-11-12: the drop-downs were missing here)
    // the word opens the division's main page; only the plus beside it opens the list (client, 2026-11-12)
    const sec = (key) => { const d = SITE[key]; return `<div class="drawer-sec"><div class="drawer-row"><a href="${d.href}">${d.title}</a><button type="button" class="drawer-plus" aria-expanded="false" aria-label="Show the ${d.title} list"><i aria-hidden="true"></i></button></div><div class="drawer-sub" hidden>
      ${d.groups.map(g => `<div class="drawer-group">${g.title ? `<div class="drawer-group-title">${g.href ? `<a href="${g.jump || g.href}">${g.title}</a>` : g.title}</div>` : ''}${g.items.map(([l, h]) => link(l, h, g.href ? g : null)).join('')}</div>`).join('')}
      <a class="drawer-all" href="${d.href}">${d.footerLink[0]} →</a></div></div>`; };
    return `<div class="drawer" data-lenis-prevent hidden>
      <a href="/">Home</a>${sec('commodities')}${sec('engineering')}<a href="/about/">About</a><a href="/contact/">Contact</a>
      <a class="btn primary drawer-cta" href="/contact/#quote"><span>Request</span><span>a quote</span></a></div>`;
  }

  const html = `<header class="site-header">
    <div class="bar">
      <a class="logo-link" href="/" aria-label="HexaHessman home">${LOGO}</a>
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
  dr.addEventListener('click', (e) => { const b = e.target.closest('.drawer-plus'); if (!b) return;
    const sub = b.closest('.drawer-sec').querySelector('.drawer-sub'), on = sub.hidden; sub.hidden = !on; b.setAttribute('aria-expanded', String(on)); b.closest('.drawer-sec').classList.toggle('open', on); });
  btn.addEventListener('click', () => { const on = dr.hidden; dr.hidden = !on; btn.setAttribute('aria-expanded', String(on)); header.classList.toggle('drawer-open', on); document.documentElement.classList.toggle('no-scroll', on); });
})();
