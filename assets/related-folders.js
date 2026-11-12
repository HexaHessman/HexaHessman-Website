// Product pages, Related products (client, 2026-11-12): a black band with three green "folders", the same notched
// shape as the two doors on the homepage. Each card gets a green fill cut to the folder shape and a thin cream
// outline; the notch sits at the top on the 1st and 3rd card and at the bottom on the 2nd.
(() => {
  const cards = [...document.querySelectorAll('#related .card')]; if (!cards.length) return;
  const NS = 'http://www.w3.org/2000/svg';
  function shape(w, h, notchTop) {
    const r = Math.min(18, h / 5), nw = Math.min(w * 0.42, 190), nd = Math.min(20, h * 0.1), s = 24, cx = w / 2;
    const a = cx - nw / 2 - s, b = cx - nw / 2, c = cx + nw / 2, d = cx + nw / 2 + s;
    const top = notchTop ? `L${a},0 C${a + s * .55},0 ${b - s * .45},${nd} ${b},${nd} L${c},${nd} C${c + s * .45},${nd} ${d - s * .55},0 ${d},0 ` : '';
    const bot = notchTop ? '' : `L${d},${h} C${d - s * .55},${h} ${c + s * .45},${h - nd} ${c},${h - nd} L${b},${h - nd} C${b - s * .45},${h - nd} ${a + s * .55},${h} ${a},${h} `;
    return `M${r},0 ${top}L${w - r},0 Q${w},0 ${w},${r} L${w},${h - r} Q${w},${h} ${w - r},${h} ${bot}L${r},${h} Q0,${h} 0,${h - r} L0,${r} Q0,0 ${r},0 Z`;
  }
  cards.forEach(el => {
    el.classList.add('rf');
    const bg = document.createElement('span'); bg.className = 'rf-bg'; bg.setAttribute('aria-hidden', 'true');
    const svg = document.createElementNS(NS, 'svg'); svg.setAttribute('class', 'rf-line'); svg.setAttribute('aria-hidden', 'true');
    svg.appendChild(document.createElementNS(NS, 'path'));
    el.prepend(bg, svg);
  });
  const draw = () => cards.forEach((el, i) => {
    const w = el.offsetWidth, h = el.offsetHeight; if (!w || !h) return;
    const d = shape(w, h, i % 2 === 0), svg = el.querySelector('.rf-line');
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`); svg.firstChild.setAttribute('d', d);
    el.querySelector('.rf-bg').style.clipPath = `path('${d}')`;
  });
  draw(); addEventListener('resize', draw); addEventListener('load', draw);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(draw);
  if (window.ResizeObserver) { const ro = new ResizeObserver(draw); cards.forEach(c => ro.observe(c)); }
})();
