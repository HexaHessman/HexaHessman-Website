// Buttons (user, 2026-11-17): on hover the colour changes and the words roll up, a copy coming in from below.
// Only buttons that hold plain words are touched (or plain word pieces, like the header's "Request" "a quote");
// the copy is hidden from screen readers.
(() => {
  const into = node => {
    const t = node.textContent.trim();
    if (!t) return;
    node.textContent = '';
    const box = document.createElement('span'); box.className = 'roll';
    const a = document.createElement('span'); a.className = 'roll-a'; a.textContent = t;
    const b = document.createElement('span'); b.className = 'roll-b'; b.textContent = t; b.setAttribute('aria-hidden', 'true');
    box.append(a, b); node.append(box);
  };
  const roll = el => {
    if (el.dataset.roll) return;
    const kids = [...el.children];
    if (!kids.length) { el.dataset.roll = '1'; into(el); return; }
    const loose = [...el.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim());
    if (loose || !kids.every(k => k.tagName === 'SPAN' && !k.children.length)) return;
    el.dataset.roll = '1';
    kids.forEach(into);
  };
  const all = () => document.querySelectorAll('.btn, a.pill, button.pill').forEach(roll);
  all();
  // the header and footer are drawn by script: catch their buttons too
  addEventListener('DOMContentLoaded', all);
  addEventListener('load', all);
})();
