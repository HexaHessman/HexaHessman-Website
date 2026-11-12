// Commodities arrival: logo draws on, the headline lights up letter by letter, the partner wall fades in cell by cell.
(() => {
  const box = document.querySelector('.arrive'); if (!box) return;
  const h = box.querySelector('.arrive-title');
  h.innerHTML = h.textContent.split(' ').map(w => '<span style="white-space:nowrap">' + [...w].map(c => '<span class="ch">' + c + '</span>').join('') + '</span>').join(' ');
  const chs = [...h.querySelectorAll('.ch')];
  const cells = [...box.querySelectorAll('.pcell')];
  // stagger like a wave from the centre outwards
  const cols = () => getComputedStyle(box.querySelector('.pgrid')).gridTemplateColumns.split(' ').length;
  const stagger = () => { if (!cells.length) return; const c = cols(); cells.forEach((el, i) => { const x = i % c, y = Math.floor(i / c); el.style.transitionDelay = (0.05 * (Math.abs(x - (c - 1) / 2) + y)) + 's, 0s'; }); };
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let started = false;
  const start = () => {
    if (started) return; started = true;
    box.classList.add('on');
    if (reduce) { chs.forEach(c => c.classList.add('lit')); box.classList.add('listed'); return; }
    setTimeout(() => chs.forEach((c, i) => setTimeout(() => c.classList.add('lit'), 22 * i)), 250);   /* no logo to wait for now */
    stagger(); setTimeout(() => box.classList.add('listed'), 250 + 22 * chs.length + 150);
  };
  if (document.readyState === 'complete') requestAnimationFrame(start); else addEventListener('load', () => requestAnimationFrame(start), { once: true });
  setTimeout(() => requestAnimationFrame(start), 2500);   // do not wait for ever on a slow video or embed: the headline and the logo wall still arrive

  // the logo wall shows ten of the twelve logos; every few seconds the two that are waiting take the place of two
  // random ones on the wall, so the wall keeps changing and every logo gets its turn (client, 2026-11-12)
  const grid = box.querySelector('.pgrid[data-logos]');
  if (grid) {
    let all = []; try { all = JSON.parse(grid.dataset.logos); } catch (e) {}
    const srcOf = f => '/assets/partners/' + f + '?v=3', clsOf = f => 'plogo plogo-' + f.split('.')[0];
    const shown = () => cells.filter(c => c.offsetParent !== null && c.querySelector('.plogo'));   // phones show fewer cells
    const fileOf = c => { const m = (c.querySelector('.plogo').getAttribute('src') || '').match(/partners\/([^?]+)/); return m ? m[1] : ''; };
    all.forEach(([f]) => { const im = new Image(); im.src = srcOf(f); });   // ready before their turn
    // which logo each cell holds is kept here (not read back from the page), so two swaps close together can never
    // put one logo in two cells
    const held = new Map(cells.map(c => [c, c.querySelector('.plogo') ? fileOf(c) : '']));
    const byFile = new Map(all.map(l => [l[0], l]));
    let lastCells = [], busy = false;
    const put = (cell, [f, name], wait) => setTimeout(() => {
      const img = cell.querySelector('.plogo'); if (!img) return;
      if (reduce) { img.className = clsOf(f); img.src = srcOf(f); img.alt = name; return; }
      img.classList.add('swap-out');
      setTimeout(() => {
        img.className = clsOf(f) + ' swap-in'; img.src = srcOf(f); img.alt = name;
        const show = () => requestAnimationFrame(() => requestAnimationFrame(() => { img.className = clsOf(f); }));
        if (img.decode) img.decode().then(show, show); else show();
      }, 470);
    }, wait);
    const swap = () => {
      if (busy || document.hidden || !box.classList.contains('listed')) return;
      const vis = shown(); if (vis.length < 2) return;
      const on = new Set(vis.map(c => held.get(c))), waiting = all.filter(([f]) => !on.has(f)); if (!waiting.length) return;
      // two random cells, not the two that changed last time; two of the logos that are waiting come in
      let pool = vis.filter(c => !lastCells.includes(c)); if (pool.length < 2) pool = vis.slice();
      const picks = []; while (picks.length < Math.min(2, waiting.length) && pool.length) picks.push(pool.splice(Math.floor(Math.random() * pool.length), 1)[0]);
      const incoming = waiting.sort(() => Math.random() - 0.5).slice(0, picks.length);
      busy = true; setTimeout(() => { busy = false; }, 1600);
      picks.forEach((c, k) => { held.set(c, incoming[k][0]); put(c, byFile.get(incoming[k][0]), k * 350); });
      lastCells = picks;
    };
    setInterval(swap, 3200);
  }
})();
