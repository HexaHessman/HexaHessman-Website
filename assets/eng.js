// Engineering hub motion: smooth scroll, the centred statement that lights up word by word and then fades away
// word by word as you scroll through its pinned section, and the fade/photo reveals on each principal's stop.
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const clamp = v => Math.min(1, Math.max(0, v));

  if (window.Lenis && !reduce) {
    const lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
    const raf = t => { lenis.raf(t); requestAnimationFrame(raf); }; requestAnimationFrame(raf);
    window.__lenis = lenis;
  }

  // menu links to a part of this page (/engineering/#components) glide there instead of jumping
  const jump = (hash, smooth) => {
    const el = hash && hash.length > 1 && document.getElementById(decodeURIComponent(hash.slice(1)));
    if (!el) return false;
    const y = Math.max(0, el.getBoundingClientRect().top + scrollY - (innerWidth <= 860 ? 90 : 120));
    if (window.__lenis) window.__lenis.scrollTo(y, smooth ? { duration: 1.4 } : { immediate: true });
    else scrollTo({ top: y, behavior: smooth ? 'smooth' : 'auto' });
    return true;
  };
  window.__csJump = jump;
  if (location.hash) setTimeout(() => jump(location.hash, false), 60);

  const io = new IntersectionObserver(es => { for (const e of es) if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } },
    { rootMargin: '0px 0px -12% 0px', threshold: 0.01 });
  document.querySelectorAll('.eprin [data-reveal]').forEach(el => io.observe(el));

  const sec = document.querySelector('.ewords'); if (!sec) return;
  if (reduce) { sec.classList.add('still'); return; }
  const p = sec.querySelector('.ewords-text');
  const words = p.textContent.trim().split(/\s+/); p.textContent = '';
  const ws = words.map((w, i) => { const s = document.createElement('span'); s.className = 'w'; s.textContent = w; p.appendChild(s); if (i < words.length - 1) p.appendChild(document.createTextNode(' ')); return s; });
  const n = ws.length, soft = 5, last = new Array(n).fill(-1);
  // progress through the pinned section: 0–0.42 words light up, hold, 0.56–0.94 they fade away in the same order
  function update() {
    const r = sec.getBoundingClientRect();
    const t = clamp(-r.top / Math.max(1, r.height - innerHeight));
    const a = clamp(t / 0.42), b = clamp((t - 0.56) / 0.38);
    for (let i = 0; i < n; i++) {
      const lit = clamp((a * (n + soft) - i) / soft), gone = clamp((b * (n + soft) - i) / soft);
      const o = Math.round(((0.1 + 0.9 * lit) * (1 - gone)) * 1000) / 1000;
      if (o !== last[i]) { last[i] = o; ws[i].style.opacity = o; ws[i].style.transform = gone ? `translateY(${(-gone * 14).toFixed(1)}px)` : ''; }
    }
  }
  addEventListener('scroll', update, { passive: true }); addEventListener('resize', update); update();
})();
