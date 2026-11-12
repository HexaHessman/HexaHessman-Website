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
})();
