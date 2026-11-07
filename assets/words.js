// Site-wide: headings fade in word by word and paragraphs fade up as they come into view (user, 2026-11-06).
// Skips the header, footer, forms and the parts that already animate their own words (Commodities scroll,
// arrival headline, team lookbook, timeline, globe cards, entrance captions).
(() => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const SKIP = '#site-header, .site-header, .site-footer, footer, form, .cscroll, .arrive, .tl-head, .about-hero2, .tl-info, .tl-grid, .gp-line, .globe-side, #captions, .choice, .vy-text, .dg, .spin-row, button, .pill, .mega, .drawer';
  const heads = [...document.querySelectorAll('main h1, main h2, main h3, section h1, section h2, section h3')].filter(e => !e.closest(SKIP) && !e.dataset.words);
  const paras = [...document.querySelectorAll('main p, section p, main li, section li')].filter(e => !e.closest(SKIP) && !e.closest('h1,h2,h3') && e.textContent.trim().length > 2);
  const split = el => {   // wrap each word, keeping any inline tags (e.g. the mint <em> words)
    const walk = n => {
      if (n.nodeType === 3) {
        const parts = n.textContent.split(/(\s+)/); if (parts.length < 2 && !n.textContent.trim()) return;
        const frag = document.createDocumentFragment();
        for (const p of parts) { if (!p) continue; if (/^\s+$/.test(p)) frag.appendChild(document.createTextNode(p)); else { const s = document.createElement('span'); s.className = 'fw'; s.textContent = p; frag.appendChild(s); } }
        n.replaceWith(frag);
      } else if (n.nodeType === 1 && !/^(svg|img|br)$/i.test(n.tagName)) [...n.childNodes].forEach(walk);
    };
    [...el.childNodes].forEach(walk);
    [...el.querySelectorAll('.fw')].forEach((w, i) => w.style.setProperty('--wi', i));
    el.dataset.words = '1'; el.classList.add('fw-h');
  };
  heads.forEach(split);
  paras.forEach(p => p.classList.add('fw-p'));
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('fw-in'); io.unobserve(e.target); } }), { threshold: 0.15, rootMargin: '0px 0px -6% 0px' });
  [...heads, ...paras].forEach(el => io.observe(el));
})();
