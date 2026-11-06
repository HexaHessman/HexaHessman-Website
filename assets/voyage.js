// The About page's voyage timeline: a top-view ship sails down the sea lane as you scroll, staying level with the
// middle of the screen; the route behind it turns from dashed to a lit line, each year's diamond lights as the ship
// reaches it; it sails straight, no lean. Mounts into <section class="vy">.
(() => {
  const sec = document.querySelector('.vy'); if (!sec) return;
  const lane = sec.querySelector('.vy-lane'), ship = sec.querySelector('.vy-ship'), stops = [...sec.querySelectorAll('.vy-stop')];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  // photo and words rise in once on screen
  // the two sides slide in from their edges each time a year comes on screen, and slide back out when it leaves
  const io = new IntersectionObserver(es => es.forEach(e => e.target.classList.toggle('seen', e.isIntersecting)), { threshold: 0.22 });
  stops.forEach(s => io.observe(s));
  let y = 0, target = 0, lastT = 0, raf = 0;
  const measure = () => {
    const r = lane.getBoundingClientRect(), sh = ship.offsetHeight;
    // the ship's bow sits at the middle of the screen, held inside the lane
    target = Math.max(0, Math.min(r.height - sh, innerHeight * 0.55 - r.top - sh * 0.72));
  };
  const frame = () => {
    raf = 0; measure();
    y = reduce ? target : y + (target - y) * 0.12;
    ship.style.setProperty('--y', y.toFixed(1) + 'px');   // straight down the lane, no lean
    const laneTop = lane.getBoundingClientRect().top, bow = laneTop + y + ship.offsetHeight * 0.72;
    stops.forEach(s => { const n = s.getBoundingClientRect(); s.classList.toggle('on', n.top + n.height / 2 < bow); });
    if (Math.abs(target - y) > 0.3) raf = requestAnimationFrame(frame);
  };
  const ask = () => { if (!raf) raf = requestAnimationFrame(frame); };
  addEventListener('scroll', ask, { passive: true }); addEventListener('resize', ask); ask();
})();
