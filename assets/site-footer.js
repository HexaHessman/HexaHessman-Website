// Shared footer (skeleton G5). Usage: <div id="site-footer"></div><script src="/assets/site-footer.js" defer></script>
(() => {
  const html = `<footer class="site-footer">
    <div class="foot-inner">
      <div class="foot-brand">
        <a class="logo-link" href="/" aria-label="HexaHessman home"><svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="miter" aria-hidden="true">
          <rect x="2.5" y="3" width="13" height="42"/><rect x="5.5" y="6" width="7" height="36" stroke-width="1"/>
          <rect x="32.5" y="3" width="13" height="42"/><rect x="35.5" y="6" width="7" height="36" stroke-width="1"/>
          <path d="M24 9.5 L38.5 24 L24 38.5 L9.5 24 Z"/><path d="M24 14 L34 24 L24 34 L14 24 Z" stroke-width="1"/></svg><span class="word">HexaHessman</span></a>
        <p class="foot-tag">Navigating with Excellence in Consultancy, Energy and Engineering.</p>
        <p class="foot-desc">HexaHessman Global Group is an international holding and investment platform overseeing a portfolio of operating companies across diverse sectors, with a presence in key global markets and a focus on visionary leadership, innovation and sustainable value creation.</p>
      </div>
      <div class="foot-col"><h4>Company</h4><a href="/about/">About</a><a href="/about/#reach">Global Presence</a><a href="/contact/">Contact</a><a class="foot-cta" href="/contact/#quote">Partner With Us →</a></div>
      <div class="foot-col"><h4>Divisions</h4><a href="/commodities/">Commodities Supply</a><a href="/engineering/">Engineering Solutions</a></div>
      <div class="foot-col"><h4>Get in touch</h4><span>39 Arab Street, Singapore 199738</span><a href="mailto:inquiry@hexahessman.com">inquiry@hexahessman.com</a><a href="https://wa.me/6580619119">WhatsApp +65 8061 9119</a><span>Mon–Fri, 09:00–17:00 SGT</span><a href="#" rel="noopener">LinkedIn</a></div>
    </div>
    <div class="foot-legal"><span>© 2026 HexaHessman Pte. Ltd. · UEN 202419032H · A member of HexaHessman Global Group</span><span><a href="/privacy/">Privacy Policy</a> · <a href="/terms/">Terms of Use</a> · <a href="/cookies/">Cookie Notice</a></span></div>
  </footer>`;
  const mount = document.getElementById('site-footer');
  if (mount) mount.outerHTML = html; else document.body.insertAdjacentHTML('beforeend', html);
})();
