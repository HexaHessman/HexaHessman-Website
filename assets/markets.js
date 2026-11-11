// Commodities hub: market prices, under the product scroll (client, 2026-11-11; after chemportal.com.tr/markets).
// A live strip (TradingView's free ticker tape, as on petrolodex.com) for the markets it can show, then one dated
// reference card per product from /assets/market-prices.json. Cards without a price are skipped, so the file can hold
// entries ready for the team to fill in. Mounts into <section id="markets">.
(async () => {
  const sec = document.getElementById('markets'); if (!sec) return;
  const data = await fetch('/assets/market-prices.json', { cache: 'no-cache' }).then(r => r.json()).catch(() => null);
  if (!data) { sec.remove(); return; }
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const num = v => Number(v).toLocaleString('en-US', { maximumFractionDigits: 2 });
  const move = c => {
    if (c === null || c === undefined || c === '') return '';
    const k = Number(c), cls = k > 0 ? 'up' : k < 0 ? 'down' : 'flat', arrow = k > 0 ? '↗' : k < 0 ? '↘' : '→';
    return `<span class="mk-move ${cls}">${arrow} ${k > 0 ? '+' : k < 0 ? '−' : ''}${num(Math.abs(k))}</span>`;
  };
  const cards = (data.cards || []).filter(c => c.price !== null && c.price !== undefined && c.price !== '');
  const live = data.live || [];
  const tv = live.length ? 'https://www.tradingview-widget.com/embed-widget/ticker-tape/?locale=en#' + encodeURIComponent(JSON.stringify({
    symbols: live.map(s => ({ proName: s.symbol, title: s.title })), showSymbolLogo: false, isTransparent: true, displayMode: 'regular', colorTheme: 'light', width: '100%', height: 46 })) : '';
  const fmtDate = d => { try { return new Date(d + 'T00:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }); } catch { return d; } };

  sec.innerHTML = `
    <div class="mk-head">
      <p class="mk-eyebrow">Market prices</p>
      <h2 class="mk-h2">Reference prices</h2>
      <p class="mk-lead">Dated reference prices for the products we supply, with live benchmarks. Indicative only, not offers.</p>
    </div>
    ${tv ? `<div class="mk-live"><p class="mk-label"><i aria-hidden="true"></i>Live markets <span>· futures may be delayed</span></p>
      <div class="mk-tape"><iframe src="${tv}" title="Live commodity prices" loading="lazy" scrolling="no"></iframe></div></div>` : ''}
    <div class="mk-grid">
      ${cards.map((c, i) => `
      <article class="mk-card" style="--i:${i}">
        <p class="mk-date">${esc(c.date)}</p>
        <h3 class="mk-name"><a href="${esc(c.href)}">${esc(c.product)}</a></h3>
        <p class="mk-price"><b>$${num(c.price)}</b> <span>${esc(c.unit)}</span></p>
        ${move(c.change)}
        <p class="mk-basis">${esc(c.basis)}</p>
        <p class="mk-src">Source: ${c.source_url ? `<a href="${esc(c.source_url)}" target="_blank" rel="noopener">${esc(c.source)}</a>` : esc(c.source)}</p>
      </article>`).join('')}
      <article class="mk-card mk-ask" style="--i:${cards.length}">
        <p class="mk-date">Updated weekly</p>
        <h3 class="mk-name">Today's price</h3>
        <p class="mk-basis">Sulphur, metallurgical coke, bitumen, methanol and every other product: message our supply team for a firm price on your volume and port.</p>
        <a class="mk-wa" href="https://wa.me/6580619119" target="_blank" rel="noopener">WhatsApp us <span aria-hidden="true">→</span></a>
      </article>
    </div>
    <p class="mk-note">Reference prices are published benchmarks for the stated basis and date, shown for information. They are not offers or quotations. Last updated ${esc(fmtDate(data.updated))}.</p>`;

  // cards rise in as the section comes up
  const io = new IntersectionObserver(es => { for (const e of es) if (e.isIntersecting) { sec.classList.add('in'); io.disconnect(); } }, { rootMargin: '0px 0px -15% 0px' });
  io.observe(sec);
})();
