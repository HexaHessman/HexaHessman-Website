// The Commodities hub's long scroll, laid out like Terminal's homepage: each product group pins one big shaped
// window (top notch, an indent on the inner edge, bleeding off the screen) to one side while that group's
// products scroll past on the other side, each paragraph lighting up word by word. Groups alternate sides:
// Fertilizer & Phosphate text left / window right, Metallurgical Reductants text right / window left, and so on.
// The 3D scene (sulphur3d.html?mode=all) plays in the windows, each group's window showing that group's chapter.
// Two copies of the scene take turns (even groups / odd groups), so neighbouring windows never share one; each copy
// is sized and cut to its window's shape and moved with it every frame.
// Some groups show a video loop in their window instead of the 3D scene (VIDEOS, by group slug).
// Mounts into <section id="cscroll">. Product data comes from /assets/commodities-data.json.
(async () => {
  const sec = document.getElementById('cscroll'); if (!sec) return;
  const data = await fetch('/assets/commodities-data.json').then(r => r.json()).catch(() => null);
  if (!data) { sec.remove(); return; }
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const hub = JSON.parse(sec.dataset.intro || 'null') || { h2: 'Specialist supply across five industrial value chains', p: '' };
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const pad = n => String(n).padStart(2, '0');
  // windows that play a filmed loop instead of the 3D scene (the grab comes down, opens and pours, then again)
  const VIDEOS = {
    'fertilizer-phosphate': { d: '/assets/commodities/grab-loop.mp4', m: '/assets/commodities/grab-loop-m.mp4', poster: '/assets/commodities/grab-loop.jpg' },
    // recorded from the 3D scene itself (one full turn every 8 s), so they keep turning when the scroll stops (2026-11-06)
    'industrial-chemicals': { d: '/assets/commodities/iso-loop.mp4', m: '/assets/commodities/iso-loop-m.mp4', poster: '/assets/commodities/iso-loop.jpg', pos: '50% 50%' },
    'petroleum-oilfield': { d: '/assets/commodities/ibc-loop.mp4', m: '/assets/commodities/ibc-loop-m.mp4', poster: '/assets/commodities/ibc-loop.jpg', pos: '50% 50%' },
    biomass: { d: '/assets/commodities/chips-loop.mp4', m: '/assets/commodities/chips-loop-m.mp4', poster: '/assets/commodities/chips-loop.jpg', pos: '74% 50%' },   // conveyor dropping wood chips onto a heap (2026-11-05)
  };
  const vidTag = v => v ? `<video class="cs-vid" muted loop playsinline preload="none" poster="${v.poster}" data-src="${innerWidth <= 900 ? v.m : v.d}"${v.pos ? ` style="object-position:${v.pos}"` : ''}></video>` : '';

  // one screen per group (client, 2026-11-11): the window, and beside it the group's name with all its products
  const chapters = data.map((g, gi) => `
    <div class="cs-chapter ${gi % 2 ? 'text-right' : 'text-left'}" data-g="${gi}" id="${g.slug}" style="--n:${g.products.length}">
      <div class="cs-pin">
        <div class="cs-stick"><div class="cs-panel" aria-hidden="true">${vidTag(VIDEOS[g.slug])}</div></div>
        <div class="cs-copy" data-reveal="copy">
          <h2 class="cs-category"><a href="/commodities/${g.slug}/">${esc(g.name)}</a></h2>
          <div class="cs-list"><div class="cs-track">
            ${g.products.map((p, pi) => `
            <article class="cs-item" id="${p.slug}" style="--i:${pi}">
              <h3 class="cs-title"><a href="/commodities/${g.slug}/${p.slug}/">${esc(p.name)}</a></h3>
              <p class="cs-lead">${esc(p.lead || p.short)}</p>
              <a class="cs-view" href="/commodities/${g.slug}/${p.slug}/">View product <span aria-hidden="true">→</span></a>
            </article>`).join('')}
          </div></div>
        </div>
      </div>
    </div>`).join('');

  sec.innerHTML = `
    <div class="cs-wins" aria-hidden="true">
      <iframe class="cs-win" src="/sulphur3d.html?mode=all&v=1110a" title="" tabindex="-1"></iframe>
      <iframe class="cs-win" src="/sulphur3d.html?mode=all&v=1110a" title="" tabindex="-1"></iframe>
    </div>
    <div class="cs-flow">
      <div class="cs-intro">
        <h2 class="cs-h2 cs-lit">${esc(hub.h2)}</h2>
        ${hub.p ? `<p class="cs-fill">${esc(hub.p)}</p>` : ''}
      </div>
      ${chapters}
    </div>`;

  // ---- split-line reveals: wrap each line of text in a mask so it can slide up into place ----
  function splitLines(el) {
    if (el.querySelector('.mask')) { el.style.setProperty('--lines', el.querySelectorAll('.mask').length); return; }   // already split by hand
    const target = el.querySelector('a') || el;
    const text = target.textContent.trim(); target.textContent = '';
    const spans = [];
    for (const w of text.split(/\s+/)) { const s = document.createElement('span'); s.className = 'w'; s.textContent = w + ' '; target.appendChild(s); spans.push(s); }
    const lines = []; let lastTop = null;
    for (const s of spans) { const t = s.offsetTop; if (t !== lastTop) { lines.push([]); lastTop = t; } lines[lines.length - 1].push(s); }
    target.textContent = '';
    for (const ws of lines) { const mask = document.createElement('span'); mask.className = 'mask'; const inner = document.createElement('span'); inner.className = 'line'; inner.textContent = ws.map(s => s.textContent).join('').trim(); mask.appendChild(inner); target.appendChild(mask); }
    el.style.setProperty('--lines', lines.length);
  }
  sec.querySelectorAll('[data-reveal="split"]').forEach(splitLines);
  const io = new IntersectionObserver(entries => { for (const e of entries) if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }, { rootMargin: '0px 0px -12% 0px', threshold: 0.01 });
  sec.querySelectorAll('[data-reveal]').forEach(el => io.observe(el));

  // ---- paragraphs that light up word by word ----
  // (the intro heading lights up the same way as its line: client, 2026-11-12)
  const fills = [...sec.querySelectorAll('.cs-lit, .cs-fill')].map(p => {
    const words = p.textContent.trim().split(/\s+/); p.textContent = '';
    const spans = words.map((w, i) => { const s = document.createElement('span'); s.className = 'w'; s.textContent = w; p.appendChild(s); if (i < words.length - 1) p.appendChild(document.createTextNode(' ')); return s; });
    return { p, spans, last: -1 };
  });
  if (reduce) sec.classList.add('still');

  // ---- smooth scroll (Lenis), as on the reference site ----
  if (window.Lenis && !reduce) {
    const lenis = new Lenis({ lerp: 0.1, smoothWheel: true, wheelMultiplier: 1, touchMultiplier: 1 });
    const raf = t => { lenis.raf(t); requestAnimationFrame(raf); }; requestAnimationFrame(raf);
    window.__lenis = lenis;
  }

  // ---- links to a section (/commodities/#urea, from the header menu) land on it ----
  const jump = (hash, smooth) => {
    const el = hash && hash.length > 1 && document.getElementById(decodeURIComponent(hash.slice(1)));
    if (!el || !sec.contains(el)) return false;
    const item = el.classList.contains('cs-item');
    const ch = item ? el.closest('.cs-chapter') : el;
    // desktop: a group or a product lands on its group's screen; phones: a product lands just below the pinned window
    let y = ch.getBoundingClientRect().top + scrollY;
    const g = groups.find(x => x.ch === ch);
    if (innerWidth > 900 && item && g && g.travel) y += innerHeight * DWELL_IN + Math.min(g.travel, Math.max(0, el.offsetTop - 26));
    if (innerWidth <= 900 && item) y = el.getBoundingClientRect().top + scrollY - ch.querySelector('.cs-stick').offsetHeight - 16;
    y = Math.max(0, Math.round(y));
    if (window.__lenis) window.__lenis.scrollTo(y, smooth ? { duration: 1.4 } : { immediate: true });
    else scrollTo({ top: y, behavior: smooth ? 'smooth' : 'auto' });
    if (!smooth) setTimeout(() => sec.querySelectorAll('[data-reveal]:not(.in)').forEach(r => { const rb = r.getBoundingClientRect(); if (rb.bottom > 0 && rb.top < innerHeight) { r.classList.add('in'); io.unobserve(r); } }), 60);
    return true;
  };
  window.__csJump = jump;
  // coming back (browser Back, or the Back button on a product page): land where the visitor left off. The browser's own
  // restore loses out to the pinned sections growing the page as it loads, so keep the spot ourselves.
  const KEY = 'cs-y:' + location.pathname;
  addEventListener('pagehide', () => { try { sessionStorage.setItem(KEY, String(Math.round(scrollY))); } catch {} });
  const nav = performance.getEntriesByType && performance.getEntriesByType('navigation')[0];
  // (the Back button on a product page sets cs-restore when it opens this page fresh rather than stepping back)
  let back = null; try { const again = sessionStorage.getItem('cs-restore') === '1'; sessionStorage.removeItem('cs-restore');
    back = (nav && nav.type === 'back_forward') || again ? sessionStorage.getItem(KEY) : null; } catch {}
  if (back !== null) {
    const y = +back, go = () => { if (window.__lenis) window.__lenis.scrollTo(y, { immediate: true }); else scrollTo(0, y); };
    [30, 300, 700].forEach(t => setTimeout(go, t));
    setTimeout(() => sec.querySelectorAll('[data-reveal]:not(.in)').forEach(r => { const rb = r.getBoundingClientRect(); if (rb.bottom > 0 && rb.top < innerHeight) { r.classList.add('in'); io.unobserve(r); } }), 760);
  } else if (location.hash) { setTimeout(() => jump(location.hash, false), 30); setTimeout(() => jump(location.hash, false), 700); }
  addEventListener('hashchange', () => jump(location.hash, true));

  // ---- the window shape (after Terminal's): a notch stepping down along the top, an indent on the inner edge,
  // rounded corners; the outer edge runs off the screen. `inner` is the side facing the text. ----
  function shape(w, h, inner) {
    const d = Math.max(18, Math.min(30, w * 0.04)), far = innerWidth <= 900 ? w + 120 : w;   // desktop: the window closes inside the page; phone: it still bleeds off the edge
    let pts = [[0, 0], [w * 0.5, 0], [w * 0.5 + d, d], [far, d], [far, h], [0, h], [0, h * 0.82], [d, h * 0.82 - d], [d, h * 0.43 + d], [0, h * 0.43]];
    if (inner === 'right') pts = pts.map(([px, py]) => [w - px, py]);
    const n = pts.length, r = 16; let out = '';
    for (let i = 0; i < n; i++) {
      const p = pts[i], a = pts[(i + n - 1) % n], b = pts[(i + 1) % n];
      const la = Math.hypot(a[0] - p[0], a[1] - p[1]), lb = Math.hypot(b[0] - p[0], b[1] - p[1]);
      const ka = Math.min(r / la, 0.5), kb = Math.min(r / lb, 0.5);
      const s = [p[0] + (a[0] - p[0]) * ka, p[1] + (a[1] - p[1]) * ka], e = [p[0] + (b[0] - p[0]) * kb, p[1] + (b[1] - p[1]) * kb];
      out += (i ? 'L' : 'M') + s[0].toFixed(1) + ' ' + s[1].toFixed(1) + 'Q' + p[0].toFixed(1) + ' ' + p[1].toFixed(1) + ' ' + e[0].toFixed(1) + ' ' + e[1].toFixed(1);
    }
    return out + 'Z';
  }

  // each group: its window, its scroll span, and its stretch of the scene (chapters weighted by product count)
  const total = data.reduce((a, g) => a + g.products.length, 0);
  let acc = 0;
  const groups = [...sec.querySelectorAll('.cs-chapter')].map((ch, gi) => {
    const n = data[gi].products.length, from = acc / total; acc += n;
    return { ch, gi, pin: ch, panel: ch.querySelector('.cs-panel'), txt: ch.querySelector('.cs-copy'), video: ch.querySelector('.cs-vid'), from, to: acc / total, copy: gi % 2 };
  });
  // the inner (text-facing) edge: on phones the window sits above the text, so its indent faces left
  const innerOf = g => innerWidth <= 900 ? 'left' : (g.ch.classList.contains('text-left') ? 'left' : 'right');
  // each window gets its shape drawn as an outline (a thin cream line); the scene / video sit on top, cut to the same
  // shape, so only the outer half of the line shows
  const SVGNS = 'http://www.w3.org/2000/svg';
  function shapePanels() {
    for (const g of groups) {
      const w = g.panel.offsetWidth, h = g.panel.offsetHeight, d = shape(w, h, innerOf(g));
      let svg = g.panel.querySelector('.cs-outline');
      if (!svg) {
        svg = document.createElementNS(SVGNS, 'svg'); svg.setAttribute('class', 'cs-outline');
        svg.appendChild(document.createElementNS(SVGNS, 'path'));
        const run = document.createElementNS(SVGNS, 'path'); run.setAttribute('class', 'cs-run'); svg.appendChild(run);   // the light that travels round the line
        g.panel.prepend(svg);
      }
      svg.setAttribute('viewBox', `0 0 ${w} ${h}`); svg.firstChild.setAttribute('d', d);
      const run = svg.lastChild; run.setAttribute('d', d);
      if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {   // one short bright dash, 7% of the way round, circling in ~8 s
        const L = run.getTotalLength(); run.style.strokeDasharray = `${(L * 0.07).toFixed(1)} ${L.toFixed(1)}`;
        if (run._anim) run._anim.cancel();
        run._anim = run.animate([{ strokeDashoffset: 0 }, { strokeDashoffset: -L * 1.07 }], { duration: Math.max(7000, L * 2.4), iterations: Infinity, easing: 'linear' });
      }
      if (g.video) g.video.style.clipPath = `path('${d}')`;
    }
    sized = [null, null];
  }

  // ---- every frame: each scene copy rides on the window it plays in, words light up, the scene follows its group ----
  const wins = [...sec.querySelectorAll('.cs-win')];
  const ready = new Set(), lastP = [-1, -1];
  let sized = [null, null];
  wins.forEach((f, c) => f.addEventListener('load', () => { ready.add(f); lastP[c] = -1; }));
  function tick() {
    const vh = innerHeight;
    const r = sec.getBoundingClientRect();
    const near = r.bottom > -vh && r.top < vh * 2;
    const best = [null, null], area = [0, 0];
    if (near) for (const g of groups) {
      if (g.video) continue;   // this window plays its own video
      const b = g.panel.getBoundingClientRect(); const seen = Math.min(b.bottom, vh) - Math.max(b.top, 0);
      if (seen > area[g.copy]) { area[g.copy] = seen; best[g.copy] = { g, b }; }
    }
    wins.forEach((f, c) => {
      const hit = best[c];
      const pause = v => { if (f._paused !== v && ready.has(f)) { f._paused = v; f.contentWindow.postMessage({ type: 'scene-pause', v }, '*'); } };
      if (!hit) { if (f.style.visibility !== 'hidden') f.style.visibility = 'hidden'; pause(true); return; }
      pause(false);
      const { g, b } = hit;
      if (sized[c] !== g) {   // size and shape it to this window
        sized[c] = g; lastP[c] = -1; f.dataset.jump = '1'; f.style.visibility = 'hidden';   // stays hidden until its own chapter is on
        f.style.width = b.width + 'px'; f.style.height = b.height + 'px';
        f.style.clipPath = `path('${shape(b.width, b.height, innerOf(g))}')`;
      }
      f.style.transform = `translate3d(${b.left.toFixed(1)}px, ${b.top.toFixed(1)}px, 0)`;
      if (f.style.visibility !== 'visible' && !f.dataset.jump) f.style.visibility = 'visible';
      // this group's stretch of the scene, as its products scroll past (kept clear of the neighbouring chapters)
      const pr = g.pin.getBoundingClientRect();
      const local = Math.min(1, Math.max(0, (vh * 0.5 - pr.top) / Math.max(1, pr.height - vh * 0.5)));
      const p = g.from + (g.to - g.from) * (0.04 + 0.92 * local);
      if (ready.has(f) && Math.abs(p - lastP[c]) > 0.0005) {
        const jump = !!f.dataset.jump; lastP[c] = p;
        f.contentWindow.postMessage({ type: 'hero-progress', p, grabSide: 0.5, jump }, '*');
        if (jump) { delete f.dataset.jump; setTimeout(() => requestAnimationFrame(() => requestAnimationFrame(() => { if (sized[c] === g) f.style.visibility = 'visible'; })), 60); }   // show it once the cut has rendered
      }
    });
    if (near) scrollLists();
    // words: a paragraph lights up as it rises from the bottom of the screen to a little above the middle
    if (near && !reduce) for (const f of fills) {
      const b = f.p.getBoundingClientRect(); if (b.bottom < -50 || b.top > vh + 50) continue;
      const span = innerWidth <= 900 ? 0.22 : 0.45;   // on phones the text slides under the pinned window sooner
      const t = Math.min(1, Math.max(0, (vh * 0.92 - b.top) / (vh * span + b.height * 0.5)));
      const n = f.spans.length, soft = 4, lit = t * (n + soft);
      const q = Math.round(lit * 20); if (q === f.last) continue; f.last = q;
      f.spans.forEach((s, i) => { s.style.opacity = (0.16 + 0.84 * Math.min(1, Math.max(0, (lit - i) / soft))).toFixed(3); });
    }
    requestAnimationFrame(tick);
  }
  // video windows: load when close, play only while on screen (a still frame for reduced motion)
  const vio = new IntersectionObserver(entries => { for (const e of entries) {
    const v = e.target;
    if (e.isIntersecting) { if (!v.src) { v.src = v.dataset.src; v.load(); } if (!reduce) v.play().catch(() => {}); }
    else v.pause();
  } }, { rootMargin: '50% 0px' });
  sec.querySelectorAll('.cs-vid').forEach(v => vio.observe(v));

  // desktop (client, 2026-11-11): the group's name stays at the window's top edge; under it the products scroll past
  // at their full size, spaced as before, but only inside the window's height: nothing shows above the name's line or
  // below the window's bottom edge. Each group's screen stays pinned for as long as its list takes to scroll through.
  const DWELL_IN = 0.12, DWELL_OUT = 0.28;   // screens of scrolling before the list moves, and after it ends
  function fit() {
    // one size for every group's name (client, 2026-11-11): the size that lets the longest word ("Metallurgical") fit
    let kh = 1;
    if (innerWidth > 900) for (const g of groups) {
      const c = g.txt, h = c.querySelector('.cs-category'); c.style.setProperty('--kh', 1);
      for (let k = 1; k > 0.5 && h.scrollWidth > h.clientWidth + 1; ) { k -= 0.02; c.style.setProperty('--kh', k.toFixed(3)); }
      kh = Math.min(kh, parseFloat(c.style.getPropertyValue('--kh')));
    }
    for (const g of groups) {
      const c = g.txt;
      g.list = c.querySelector('.cs-list'); g.track = c.querySelector('.cs-track');
      c.style.setProperty('--kh', innerWidth > 900 ? kh.toFixed(3) : 1); g.ch.style.height = ''; g.track.style.transform = ''; g.travel = 0;
      if (innerWidth <= 900) continue;
      const room = g.list.clientHeight, need = g.track.offsetHeight;
      g.travel = Math.max(0, need - room);
      g.base = 0;   // a short list starts right under the group's name, like the long ones (client, 2026-11-12)
      g.ch.style.height = Math.round(innerHeight * (1 + DWELL_IN + DWELL_OUT) + g.travel) + 'px';
      g.lastY = null;
    }
  }
  function scrollLists() {
    if (innerWidth <= 900) return;
    for (const g of groups) {
      if (!g.track) continue;
      const r = g.ch.getBoundingClientRect(); if (r.bottom < -innerHeight || r.top > innerHeight * 2) continue;
      const y = g.base - Math.min(g.travel, Math.max(0, -r.top - innerHeight * DWELL_IN));
      if (y !== g.lastY) { g.lastY = y; g.track.style.transform = `translate3d(0, ${y.toFixed(1)}px, 0)`; }
    }
  }
  const layout = () => { fit(); shapePanels(); };
  layout();
  addEventListener('resize', layout);
  document.fonts && document.fonts.ready.then(layout);
  requestAnimationFrame(tick);
})();
