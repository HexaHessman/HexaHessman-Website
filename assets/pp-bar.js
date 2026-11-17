// Product pages: the "where it comes from" bar takes its widths from the percentages in its legend, so changing a
// number in the website editor (/admin) moves the bar too, on the live page and in the editor's preview (user, 2026-11-17).
// The generator still writes the starting widths, so the bar is right before this runs.
(() => {
  const fit = mix => {
    const bar = mix.querySelector('.pp-bar'), segs = bar ? [...bar.children] : [], rows = [...mix.querySelectorAll('.pp-legend > span')];
    if (!segs.length || segs.length !== rows.length) return;
    const parts = rows.map(r => {
      const b = r.querySelector('b'), v = b ? parseFloat(b.textContent.replace(',', '.').replace(/[^\d.]/g, '')) : NaN;
      const name = [...r.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim();
      return { v: isFinite(v) && v >= 0 ? v : 0, name, shown: b ? b.textContent.trim() : '' };
    });
    const sum = parts.reduce((a, p) => a + p.v, 0); if (!sum) return;
    parts.forEach((p, i) => { segs[i].style.width = (p.v / sum * 100).toFixed(3) + '%'; });
    bar.setAttribute('aria-label', parts.map(p => `${p.name} ${p.shown}`).join(', '));
  };
  document.querySelectorAll('.pp-mix').forEach(mix => {
    fit(mix);
    const leg = mix.querySelector('.pp-legend');
    if (leg) new MutationObserver(() => fit(mix)).observe(leg, { subtree: true, childList: true, characterData: true });
  });
})();
