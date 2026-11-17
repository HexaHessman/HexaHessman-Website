/* HexaHessman website editor.
   The list of every word and photo on the site comes from seed.json (written by tools/cms/cms.py on every build).
   Changes are kept in Supabase (or, before it is connected, in this browser) as {kind, o: original, t: new, scope}.
   Publish starts the GitHub workflow that writes them into the pages (see supabase/README.md). */
(() => {
"use strict";
const CFG = window.HH_CMS_CONFIG || {};
const LIVE = !!(CFG.supabaseUrl && CFG.supabaseAnonKey && window.supabase);
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const norm = s => String(s ?? "").replace(/\s+/g, " ").trim();
const ago = iso => {
  if (!iso) return "never";
  const s = (Date.now() - new Date(iso).getTime()) / 1000;
  if (s < 60) return "just now";
  if (s < 3600) return Math.floor(s / 60) + " min ago";
  if (s < 86400) return Math.floor(s / 3600) + " h ago";
  if (s < 86400 * 7) return Math.floor(s / 86400) + " d ago";
  return new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
};
const initials = s => (String(s || "?").replace(/@.*/, "").split(/[.\s_-]+/).filter(Boolean).slice(0, 2).map(w => w[0]).join("") || "?").toUpperCase();
const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };

/* ---------- icons (thin line, Apple-like) ---------- */
const ICONS = {
  home: '<path d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-4.5v-6h-5v6H5a1 1 0 0 1-1-1z"/>',
  file: '<path d="M6 3h8l4 4v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/><path d="M14 3v4h4M8.5 12h7M8.5 16h7"/>',
  type: '<path d="M5 7V5h14v2M12 5v14M9 19h6"/>',
  layout: '<rect x="3.5" y="4" width="17" height="16" rx="2"/><path d="M3.5 8.5h17M3.5 16h17"/>',
  image: '<rect x="3.5" y="4.5" width="17" height="15" rx="2"/><circle cx="9" cy="10" r="1.8"/><path d="m20.5 16-5-5-9 8.5"/>',
  clock: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
  users: '<circle cx="9" cy="8.5" r="3.2"/><path d="M3.5 19.5c.6-3 2.8-4.8 5.5-4.8s4.9 1.8 5.5 4.8"/><path d="M15.5 5.6a3 3 0 0 1 0 5.8M17.5 14.9c1.6.6 2.7 2.2 3 4.6"/>',
  send: '<path d="M20.5 3.5 10 14M20.5 3.5 14 20.5l-4-6.5-6.5-4z"/>',
  more: '<circle cx="5.5" cy="12" r="1.2"/><circle cx="12" cy="12" r="1.2"/><circle cx="18.5" cy="12" r="1.2"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  search: '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/>',
  external: '<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
  arrow: '<path d="M7 17 17 7M9 7h8v8"/>',
  chevron: '<path d="m6 9 6 6 6-6"/>',
  back: '<path d="M15 5 8 12l7 7"/>',
  desktop: '<rect x="3" y="4.5" width="18" height="12" rx="1.5"/><path d="M9 20h6M12 16.5V20"/>',
  phone: '<rect x="7" y="3" width="10" height="18" rx="2.2"/><path d="M11 18h2"/>',
  edit: '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>',
  sparkle: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
  upload: '<path d="M12 16V4M7 9l5-5 5 5M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3"/>',
  undo: '<path d="M9 14 4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 0 12h-3"/>',
  globe: '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.5 2.6 3.6 5.5 3.6 8.5s-1.1 5.9-3.6 8.5c-2.5-2.6-3.6-5.5-3.6-8.5S9.5 6.1 12 3.5z"/>',
  check: '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
};
const ic = n => `<i data-i="${n}"><svg viewBox="0 0 24 24">${ICONS[n] || ""}</svg></i>`;
const paintIcons = (root = document) => $$("i[data-i]:empty", root).forEach(el => { el.innerHTML = `<svg viewBox="0 0 24 24">${ICONS[el.dataset.i] || ""}</svg>`; });

/* ---------- toast, modal, menu ---------- */
let toastT;
const toast = (msg, kind = "") => { const t = $("#toast"); t.textContent = msg; t.className = "toast" + (kind ? " toast--" + kind : ""); t.hidden = false; clearTimeout(toastT); toastT = setTimeout(() => t.hidden = true, 3800); };
const modal = (html, onMount) => {
  const m = $("#modal"), box = $("#modalBox");
  box.innerHTML = `<button class="iconbtn modal__close" type="button" aria-label="Close">&times;</button>${html}`;
  m.hidden = false; paintIcons(box);
  const close = () => { m.hidden = true; box.innerHTML = ""; document.removeEventListener("keydown", key); };
  const key = e => { if (e.key === "Escape") close(); };
  document.addEventListener("keydown", key);
  $(".modal__close", box).onclick = close;
  m.onclick = e => { if (e.target === m) close(); };
  if (onMount) onMount(box, close);
  return close;
};
const confirmBox = (title, text, label = "OK", danger = false) => new Promise(res => modal(`<h2>${esc(title)}</h2><p class="muted">${esc(text)}</p><div class="modal__foot"><button class="btn" data-no>Cancel</button><button class="btn ${danger ? "btn--danger" : "btn--dark"}" data-yes>${esc(label)}</button></div>`, (box, close) => {
  $("[data-no]", box).onclick = () => { close(); res(false); };
  $("[data-yes]", box).onclick = () => { close(); res(true); };
}));
const popMenu = (anchor, items) => {
  $$(".menu").forEach(m => m.remove());
  const m = document.createElement("div"); m.className = "menu";
  m.innerHTML = items.map((it, i) => `<button data-i="${i}">${esc(it[0])}</button>`).join("");
  document.body.appendChild(m);
  const r = anchor.getBoundingClientRect();
  m.style.left = Math.min(r.left, innerWidth - 200) + "px"; m.style.top = (r.top - m.offsetHeight - 8 > 0 ? r.top - m.offsetHeight - 8 : r.bottom + 8) + "px";
  m.onclick = e => { const b = e.target.closest("button"); if (!b) return; m.remove(); items[+b.dataset.i][1](); };
  setTimeout(() => document.addEventListener("click", function off(e) { if (!m.contains(e.target)) { m.remove(); document.removeEventListener("click", off); } }), 0);
};

/* ---------- the site's words and photos ---------- */
let SEED = { pages: [], shared: [], fields: {} };
let ALL = [], BYURL = {}, IMGUSE = {};
const F = k => SEED.fields[k];
const loadSeed = async () => {
  SEED = await (await fetch("seed.json?t=" + Date.now(), { cache: "no-store" })).json();
  ALL = SEED.pages.concat(SEED.shared);
  BYURL = Object.fromEntries(ALL.map(p => [p.url, p]));
  IMGUSE = {};
  for (const p of SEED.pages) for (const im of p.images) (IMGUSE[im.o] = IMGUSE[im.o] || { o: im.o, t: im.t, kind: im.kind, pages: [] }).pages.push(p.url);
};
const pageName = url => url === "@fonts" ? "Fonts" : (BYURL[url] && BYURL[url].title) || url;
const whereText = (k, url) => {
  const w = (F(k).where || []).filter(u => u !== url);
  if (!w.length) return "";
  const pages = w.filter(u => !u.startsWith("@")).length, shared = w.filter(u => u.startsWith("@")).map(u => pageName(u));
  const bits = [];
  if (pages) bits.push(`${pages} other page${pages > 1 ? "s" : ""}`);
  if (shared.length) bits.push("the " + shared.join(" and ").toLowerCase());
  return "also on " + bits.join(" and ");
};

/* ---------- storage: this browser (draft mode) ---------- */
const LKEY = "hh-cms-v1";
const LocalStore = {
  _d: null,
  load() {
    if (this._d) return this._d;
    try { this._d = JSON.parse(localStorage.getItem(LKEY) || "null"); } catch (e) { this._d = null; }
    this._d = Object.assign({ edits: [], history: [], publishes: [] }, this._d || {});
    return this._d;
  },
  save() { try { localStorage.setItem(LKEY, JSON.stringify(this._d)); } catch (e) { toast("This browser's storage is full. Download the changes file.", "err"); } },
  async user() { return { email: "draft@this-browser", name: "You", role: "owner" }; },
  async edits() { return this.load().edits; },
  async upsert(row) { const d = this.load(); const i = d.edits.findIndex(e => e.kind === row.kind && e.o === row.o && e.scope === row.scope); row.updated_at = new Date().toISOString(); row.updated_by = "You"; if (i >= 0) d.edits[i] = row; else d.edits.push(row); this.save(); },
  async remove(kind, o, scope) { const d = this.load(); d.edits = d.edits.filter(e => !(e.kind === kind && e.o === o && e.scope === scope)); this.save(); },
  async history(limit = 200) { return this.load().history.slice(0, limit); },
  async addHistory(h) { const d = this.load(); d.history.unshift(Object.assign({ at: new Date().toISOString(), by: "You" }, h)); d.history = d.history.slice(0, 500); this.save(); },
  async publishes() { return this.load().publishes; },
  async upload(file) {
    if (file.size > 1.6e6) throw new Error("In draft mode files must be under 1.6 MB. Once the editor is connected, bigger photos and videos work.");
    return await new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(r.result); r.onerror = rej; r.readAsDataURL(file); });
  },
  async publish() { download(); const d = this.load(); d.publishes.unshift({ status: "done", created_at: new Date().toISOString(), requested_by: "You" }); this.save(); return { message: "Draft mode: the changes file was downloaded. Send it to your web developer to publish." }; },
  async signOut() {},
};

/* ---------- storage: Supabase (live) ---------- */
let sb = null;
const SupaStore = {
  _me: null,
  async user() {
    const { data } = await sb.auth.getUser();
    if (!data || !data.user) return null;
    const email = data.user.email.toLowerCase();
    const r = await sb.from("cms_users").select("email,name,role").ilike("email", email).maybeSingle();
    if (!r.data) return { email, name: email, role: null };
    return this._me = { email, name: r.data.name || email, role: r.data.role };
  },
  async edits() {
    const out = [];
    for (let from = 0; ; from += 1000) {
      const { data, error } = await sb.from("cms_edits").select("kind,o,t,scope,page,updated_at,updated_by").order("id").range(from, from + 999);
      if (error) throw error;
      out.push(...data); if (data.length < 1000) break;
    }
    return out;
  },
  async upsert(row) {
    const r = Object.assign({}, row, { updated_at: new Date().toISOString(), updated_by: this._me && this._me.email });
    const { error } = await sb.from("cms_edits").upsert(r, { onConflict: "kind,o,scope" });
    if (error) throw error;
  },
  async remove(kind, o, scope) { const { error } = await sb.from("cms_edits").delete().match({ kind, o, scope }); if (error) throw error; },
  async history(limit = 200) { const { data, error } = await sb.from("cms_history").select("*").order("at", { ascending: false }).limit(limit); if (error) throw error; return data; },
  async addHistory(h) { await sb.from("cms_history").insert(Object.assign({ by: this._me && this._me.email }, h)); },
  async publishes() { const { data } = await sb.from("cms_publishes").select("*").order("created_at", { ascending: false }).limit(30); return data || []; },
  async upload(file) {
    const name = `${Date.now()}-${file.name.toLowerCase().replace(/[^a-z0-9.]+/g, "-")}`;
    const { error } = await sb.storage.from("media").upload(name, file, { cacheControl: "31536000", upsert: false, contentType: file.type });
    if (error) throw error;
    const url = sb.storage.from("media").getPublicUrl(name).data.publicUrl;
    await sb.from("cms_media").insert({ path: name, url, name: file.name, created_by: this._me && this._me.email });
    return url;
  },
  async token() { const { data } = await sb.auth.getSession(); return data.session && data.session.access_token; },
  async publish() {
    const r = await fetch("/api/publish/", { method: "POST", headers: { "Content-Type": "application/json", Authorization: "Bearer " + await this.token() }, body: "{}" });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.error || "Publishing failed.");
    return j;
  },
  async team(body) {
    const r = await fetch("/api/users/", { method: "POST", headers: { "Content-Type": "application/json", Authorization: "Bearer " + await this.token() }, body: JSON.stringify(body) });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.error || "That did not work.");
    return j;
  },
  async signOut() { await sb.auth.signOut(); },
};
const Store = LIVE ? SupaStore : LocalStore;

/* ---------- state ---------- */
let ME = null, EDITS = new Map(), HIST = [], PUBS = [];
const ek = (kind, o, scope) => kind + "\u0001" + o + "\u0001" + scope;
const loadEdits = async () => { EDITS = new Map((await Store.edits()).map(e => [ek(e.kind, e.o, e.scope), e])); };
const editFor = (kind, o, url) => EDITS.get(ek(kind, o, url)) || EDITS.get(ek(kind, o, "*")) || null;
const textNow = (k, url) => { const e = editFor("text", F(k).o, url); return e ? e.t : F(k).o; };
const imgNow = (o, url) => { const e = editFor("image", o, url); return e ? e.t : o; };
const lastPublish = () => PUBS.find(p => p.status === "done") || null;
const pending = () => {
  const since = lastPublish() ? new Date(lastPublish().created_at).getTime() : 0;
  const seen = new Set();
  for (const h of HIST) if (new Date(h.at).getTime() > since) seen.add(ek(h.kind, h.o, h.scope));
  return seen.size;
};
const refreshPub = () => {
  const n = pending(), lp = lastPublish();
  $("#pubTitle").textContent = n ? `${n} change${n > 1 ? "s" : ""} waiting` : "Everything is published";
  $("#pubText").textContent = n ? "Publish to put them on the website." : lp ? `Last published ${ago(lp.created_at)}.` : "Your changes go live when you publish.";
  $("#pubMeter").style.width = n ? Math.min(100, 12 + n * 8) + "%" : "100%";
  $("#publishBtn").disabled = !n && LIVE;
};
let saving = 0;
const saveState = (txt, on) => { const s = $("#saveState"); s.textContent = txt; s.classList.toggle("on", !!on); };

/* save one change. scope '*' = everywhere these words appear, or a page address = that page only */
async function setText(k, url, value, onlyHere) {
  const o = F(k).o, v = value.replace(/\s+$/g, "").replace(/^\s+/g, "");
  const scope = onlyHere ? url : "*";
  const other = onlyHere ? "*" : url;
  const before = (EDITS.get(ek("text", o, scope)) || {}).t ?? o;
  saving++; saveState("Saving…");
  try {
    if (EDITS.has(ek("text", o, other)) && url && !url.startsWith("@")) {   // moved between "this page" and "everywhere"
      if (onlyHere === false) { await Store.remove("text", o, other); EDITS.delete(ek("text", o, other)); }
    }
    if (!v || v === o) { if (EDITS.has(ek("text", o, scope))) { await Store.remove("text", o, scope); EDITS.delete(ek("text", o, scope)); } }
    else { const row = { kind: "text", o, t: v, scope, page: url }; await Store.upsert(row); EDITS.set(ek("text", o, scope), Object.assign({ updated_at: new Date().toISOString(), updated_by: ME.email }, row)); }
    if (before !== (v || o)) { const h = { kind: "text", o, scope, page: url, before, after: v && v !== o ? v : null, at: new Date().toISOString(), by: ME.email }; HIST.unshift(h); await Store.addHistory(h); }
    saveState("All changes saved", true);
  } catch (e) { console.error(e); saveState(""); toast("Could not save: " + (e.message || e), "err"); }
  finally { saving--; refreshPub(); }
}
async function setImage(o, url, value, onlyHere) {
  const scope = onlyHere ? url : "*";
  const before = (EDITS.get(ek("image", o, scope)) || {}).t ?? o;
  try {
    if (!value || value === o) { await Store.remove("image", o, scope); EDITS.delete(ek("image", o, scope)); }
    else { const row = { kind: "image", o, t: value, scope, page: url }; await Store.upsert(row); EDITS.set(ek("image", o, scope), Object.assign({ updated_at: new Date().toISOString() }, row)); }
    const h = { kind: "image", o, scope, page: url, before, after: value && value !== o ? value : null, at: new Date().toISOString(), by: ME.email };
    HIST.unshift(h); await Store.addHistory(h);
    saveState("All changes saved", true);
  } catch (e) { console.error(e); toast("Could not save: " + (e.message || e), "err"); }
  refreshPub();
}

/* the changes file (draft mode) */
function download() {
  const edits = [...EDITS.values()];
  const out = { edits: edits.filter(e => e.kind === "text").map(e => ({ o: e.o, t: e.t, scope: e.scope })), images: edits.filter(e => e.kind === "image").map(e => ({ o: e.o, t: e.t, scope: e.scope })) };
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([JSON.stringify(out, null, 1)], { type: "application/json" }));
  a.download = "hexahessman-changes.json"; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 2000);
}

/* ---------- router ---------- */
const view = () => $("#view");
const route = () => {
  const h = location.hash.replace(/^#/, "") || "/";
  const [path, qs] = h.split("?");
  const q = new URLSearchParams(qs || "");
  $$("#nav a").forEach(a => a.classList.toggle("on", ("/" + a.dataset.r) === path || (a.dataset.r === "dashboard" && path === "/") || (a.dataset.r === "pages" && path === "/page") || (a.dataset.r === "shared" && path === "/page" && (q.get("u") || "").startsWith("@"))));
  if (path === "/page" && (q.get("u") || "").startsWith("@")) $('#nav a[data-r="pages"]').classList.remove("on");
  $("#app").classList.remove("sideopen");
  window.scrollTo(0, 0);
  if (path === "/pages") return viewPages(q);
  if (path === "/page") return viewEditor(q.get("u"), q.get("k"));
  if (path === "/shared") return viewShared();
  if (path === "/photos") return viewPhotos(q);
  if (path === "/fonts") return viewFonts();
  if (path === "/activity") return viewActivity();
  if (path === "/team") return viewTeam();
  if (path === "/search") return viewSearch(q.get("q") || "");
  return viewDashboard();
};
const go = h => { if (location.hash === h) route(); else location.hash = h; };

/* ---------- page status ---------- */
const pageChanged = p => {
  // a page counts as changed when any of its words or photos differ from the original
  for (const f of p.fields) { const o = F(f.k).o; if (EDITS.has(ek("text", o, p.url)) || EDITS.has(ek("text", o, "*"))) return true; }
  for (const im of p.images) if (EDITS.has(ek("image", im.o, p.url)) || EDITS.has(ek("image", im.o, "*"))) return true;
  return false;
};
const pageWaiting = p => {
  for (const f of p.fields) if (textNow(f.k, p.url) !== F(f.k).t) return true;
  for (const im of p.images) if (imgNow(im.o, p.url) !== im.t) return true;
  return false;
};
const statusDot = p => pageWaiting(p) ? '<span class="dot dot--wait">Waiting to publish</span>' : pageChanged(p) ? '<span class="dot dot--live">Edited, live</span>' : '<span class="dot">Original</span>';

/* ---------- dashboard ---------- */
async function viewDashboard() {
  const hr = new Date().getHours(), hello = hr < 12 ? "Good morning" : hr < 18 ? "Good afternoon" : "Good evening";
  const first = (ME.name || "").split(/[\s@.]/)[0];
  const words = Object.keys(SEED.fields).length, photos = Object.keys(IMGUSE).length;
  const edited = [...EDITS.values()].length;
  // changes per day, last 14 days: dark = still live now, grey = since undone
  const days = [...Array(14)].map((_, i) => { const d = new Date(); d.setHours(0, 0, 0, 0); d.setDate(d.getDate() - 13 + i); return d; });
  const counts = days.map(d => { const a = d.getTime(), b = a + 86400000; const hs = HIST.filter(h => { const t = new Date(h.at).getTime(); return t >= a && t < b; }); return [hs.filter(h => h.after != null).length, hs.filter(h => h.after == null).length]; });
  const max = Math.max(4, ...counts.map(c => Math.max(c[0], c[1])));
  // pages by area, and how many of each have been edited
  const areas = ["Home", "Commodities", "Engineering", "Company", "Legal and other"];
  const byArea = areas.map(a => { const ps = SEED.pages.filter(p => p.area === a); return { a, n: ps.length, e: ps.filter(pageChanged).length }; });
  const editedPages = SEED.pages.filter(pageChanged).length;
  const C = 2 * Math.PI * 52, frac = SEED.pages.length ? editedPages / SEED.pages.length : 0, wait = SEED.pages.filter(pageWaiting).length / Math.max(1, SEED.pages.length);
  view().innerHTML = `
    <div class="pagehead"><div class="grow"><h1>${hello}${first ? ", " + esc(first[0].toUpperCase() + first.slice(1)) : ""}</h1><p class="muted">Change any words or photo on the website, then publish.</p></div>
      <a class="btn" href="#/pages">${ic("edit")}<span>Edit a page</span></a></div>
    <div class="stats">
      <div class="stat"><span>Pages</span><b>${SEED.pages.length}</b><span class="chip-ic">${ic("file")}</span></div>
      <div class="stat"><span>Texts you can edit</span><b>${words.toLocaleString()}</b><span class="chip-ic">${ic("sparkle")}</span></div>
      <div class="stat"><span>Waiting to publish</span><b>${pending()}</b><span class="chip-ic">${ic("send")}</span></div>
      <div class="stat"><span>Last published</span><b style="font-size:18px;padding-top:5px">${esc(ago(lastPublish() && lastPublish().created_at))}</b><span class="chip-ic">${ic("clock")}</span></div>
    </div>
    <div class="grid3">
      <div class="card"><div class="card__head"><h2>Pages edited</h2><a class="iconbtn" href="#/pages" aria-label="All pages">${ic("arrow")}</a></div>
        <div class="card__body">
          <div class="donut"><svg width="150" height="150" viewBox="0 0 120 120" aria-hidden="true">
            <circle cx="60" cy="60" r="52" fill="none" stroke="#eeeef1" stroke-width="13"/>
            <circle cx="60" cy="60" r="52" fill="none" stroke="#a1a1a6" stroke-width="13" stroke-linecap="round" stroke-dasharray="${(C * Math.max(frac, 0.0001)).toFixed(1)} ${C.toFixed(1)}" transform="rotate(-90 60 60)"/>
            <circle cx="60" cy="60" r="52" fill="none" stroke="#1d1d1f" stroke-width="13" stroke-linecap="round" stroke-dasharray="${(C * Math.max(wait, 0.0001)).toFixed(1)} ${C.toFixed(1)}" transform="rotate(-90 60 60)"/>
            <text x="60" y="58" text-anchor="middle" font-size="22" font-weight="600" fill="#1d1d1f">${editedPages}</text>
            <text x="60" y="75" text-anchor="middle" font-size="9" fill="#86868b">of ${SEED.pages.length} pages</text></svg></div>
          <div class="legend"><span><i style="background:#1d1d1f"></i>Waiting</span><span><i style="background:#a1a1a6"></i>Edited</span><span><i style="background:#eeeef1"></i>Original</span></div>
        </div></div>
      <div class="card"><div class="card__head"><h2>Changes, last 14 days</h2><a class="iconbtn" href="#/activity" aria-label="Activity">${ic("arrow")}</a></div>
        <div class="card__body">
          <div class="legend" style="margin-bottom:6px"><span><i style="background:#1d1d1f"></i>Changed</span><span><i style="background:#a1a1a6"></i>Undone</span></div>
          <div class="bars">${counts.map(c => `<div><span style="height:${(c[0] / max * 100).toFixed(1)}%"></span><span class="g" style="height:${(c[1] / max * 100).toFixed(1)}%"></span></div>`).join("")}</div>
          <div class="bars-x">${days.map((d, i) => `<span>${i % 2 ? "" : d.toLocaleDateString("en-GB", { day: "numeric", month: "short" })}</span>`).join("")}</div>
        </div></div>
      <div class="card"><div class="card__head"><h2>Recent activity</h2><a class="iconbtn" href="#/activity" aria-label="Activity">${ic("arrow")}</a></div>
        <div class="res">${HIST.slice(0, 5).map(h => `<a href="${h.scope === "@fonts" ? "#/fonts" : h.page ? "#/page?u=" + encodeURIComponent(h.page) : "#/activity"}"><span class="txt">${h.scope === "@fonts" ? esc(fontLine(h)) : h.kind === "image" ? "Photo replaced" : esc((h.after ?? h.o).slice(0, 70))}</span><span class="meta">${esc(h.page ? pageName(h.page) : "")} · ${esc(ago(h.at))}${h.after == null ? " · undone" : ""}</span></a>`).join("") || '<div class="empty">No changes yet. Pick a page and click any words to change them.</div>'}</div></div>
    </div>
    <div class="card"><div class="card__head"><h2>${ic("file")} All pages</h2></div>
      <div class="card__body">${pagesTable(SEED.pages)}</div></div>`;
  paintIcons(view()); bindRows();
}
const pagesTable = ps => `<div class="tablewrap"><table class="table"><thead><tr><th>${ic("file")}Page</th><th class="hide-s">${ic("layout")}Section</th><th class="hide-s">${ic("edit")}Texts</th><th class="hide-s">${ic("image")}Photos</th><th>${ic("globe")}Status</th></tr></thead><tbody>
  ${ps.map(p => `<tr data-go="#/page?u=${encodeURIComponent(p.url)}"><td class="t">${esc(p.title)}<span class="url">${esc(p.url.startsWith("@") ? "On every page" : p.url)}</span></td><td class="hide-s">${esc(p.area)}</td><td class="hide-s">${p.fields.length}</td><td class="hide-s">${p.images.length}</td><td>${statusDot(p)}</td></tr>`).join("")}
  </tbody></table></div>`;
const bindRows = () => $$("tr[data-go]", view()).forEach(tr => tr.onclick = () => go(tr.dataset.go));

/* ---------- pages ---------- */
let pagesFilter = "All";
function viewPages() {
  const areas = ["All", "Home", "Commodities", "Engineering", "Company", "Legal and other"];
  const draw = () => {
    const ps = SEED.pages.filter(p => pagesFilter === "All" || p.area === pagesFilter);
    $("#pagesBody").innerHTML = pagesTable(ps); paintIcons($("#pagesBody")); bindRows();
    $$(".chip", view()).forEach(c => c.classList.toggle("on", c.dataset.a === pagesFilter));
  };
  view().innerHTML = `<div class="pagehead"><div class="grow"><h1>Pages</h1><p class="muted">Open a page to change its words and photos. You can also click straight on the words in the preview.</p></div></div>
    <div class="chips">${areas.map(a => `<button class="chip" data-a="${esc(a)}">${esc(a)}</button>`).join("")}</div>
    <div class="card"><div class="card__body" id="pagesBody"></div></div>`;
  $$(".chip", view()).forEach(c => c.onclick = () => { pagesFilter = c.dataset.a; draw(); });
  draw();
}
function viewShared() {
  view().innerHTML = `<div class="pagehead"><div class="grow"><h1>Menu and footer</h1><p class="muted">These parts appear on every page. A change here shows everywhere.</p></div></div>
    <div class="card"><div class="card__body">${pagesTable(SEED.shared)}</div></div>`;
  paintIcons(view()); bindRows();
}

/* ---------- the page editor ---------- */
let PV = null;   // the live preview: { url, frame, index: Map(text -> [nodes]), imgs }
function viewEditor(url, focusKey) {
  const p = BYURL[url];
  if (!p) { view().innerHTML = '<div class="empty">That page was not found.</div>'; return; }
  const shared = url.startsWith("@");
  const pvUrl = shared ? (p.file.includes("commodities-data") ? "/commodities/" : p.file.includes("product-contact") ? "/commodities/fertilizer-phosphate/sulphur/" : "/") : url;
  // group the boxes by section
  const groups = [];
  const meta = p.fields.filter(f => f.tag === "title" || f.tag === "meta");
  if (meta.length) groups.push({ name: "Google and browser tab", fields: meta, shut: true });
  for (const f of p.fields) {
    if (f.tag === "title" || f.tag === "meta") continue;
    const name = f.sec || (shared ? p.title : "Top of the page");
    let g = groups[groups.length - 1];
    if (!g || g.name !== name || g.meta) { g = { name, fields: [] }; groups.push(g); }
    g.fields.push(f);
  }
  const box = f => {
    const k = f.k, v = textNow(k, url), o = F(k).o, live = F(k).t;
    const onlyHere = EDITS.has(ek("text", o, url)) && !shared;
    const w = whereText(k, url);
    const changed = v !== o, waiting = v !== live;
    const big = /^h[12]$/.test(f.tag);
    return `<div class="fld${changed ? " changed" : ""}" data-k="${k}" id="f-${k}">
      <div class="fld__top"><span class="lbl">${esc(f.label)}</span>${w ? `<span class="where">· ${esc(w)}</span>` : ""}<span class="state">${waiting ? '<span class="badge">Not published</span>' : changed ? '<span class="badge badge--live">Edited</span>' : ""}</span></div>
      <textarea rows="1" class="${big ? "big" : ""}" spellcheck="true">${esc(v)}</textarea>
      <div class="fld__foot">${w && !shared ? `<label><input type="checkbox" data-only ${onlyHere ? "checked" : ""}> Only on this page</label>` : ""}${changed ? `<button class="linkbtn" data-reset type="button">Back to the original</button>` : ""}</div>
    </div>`;
  };
  view().innerHTML = `
    <div class="pagehead"><div class="grow">
      <a class="muted small" href="${shared ? "#/shared" : "#/pages"}" style="display:inline-flex;align-items:center;gap:4px">${ic("back")}${shared ? "Menu and footer" : "Pages"}</a>
      <h1 style="margin-top:6px">${esc(p.title)}</h1><p class="muted">${shared ? "Shown on every page" : esc(url)} · ${p.fields.length} texts${p.images.length ? " · " + p.images.length + " photos" : ""}</p></div>
      ${shared ? "" : `<a class="btn" href="${esc(url)}" target="_blank" rel="noopener">${ic("external")}<span>Open page</span></a>`}</div>
    <div class="ed">
      <div class="ed__list">
        <div class="ed__tools"><input type="search" id="fq" placeholder="Find on this page…"></div>
        ${groups.map((g, gi) => `<section class="grp${g.shut ? " shut" : ""}" data-g="${gi}"><div class="grp__head"><b>${esc(g.name)}</b><span>${g.fields.length}</span>${ic("chevron")}</div><div class="grp__body">${g.fields.map(box).join("")}</div></section>`).join("")}
        ${p.images.length ? `<section class="grp" data-g="photos"><div class="grp__head"><b>Photos</b><span>${p.images.length}</span>${ic("chevron")}</div><div class="grp__body"><div class="edphotos">${p.images.map(im => photoCard(im.o, url)).join("")}</div></div></section>` : ""}
      </div>
      <div class="pv"><div class="pv__bar"><span class="url">${esc(location.origin + pvUrl)}</span>
        <div class="seg"><button class="on" data-dev="desktop">${ic("desktop")}Desktop</button><button data-dev="phone">${ic("phone")}Phone</button></div></div>
        <div class="pv__stage" id="stage"><iframe id="pvf" title="Preview" src="${esc(pvUrl)}${pvUrl.includes("?") ? "&" : "?"}cms-preview=1"></iframe><div class="pv__hint" id="pvHint">Click any words in the preview to change them</div></div></div>
    </div>`;
  paintIcons(view());
  const list = $(".ed__list", view());
  // boxes grow with their words
  const fit = ta => { ta.style.height = "auto"; ta.style.height = ta.scrollHeight + 2 + "px"; };
  $$("textarea", list).forEach(fit);
  $$(".grp__head", list).forEach(h => h.onclick = () => { h.parentNode.classList.toggle("shut"); $$("textarea", h.parentNode).forEach(fit); });
  // typing: show it in the preview at once, save a moment later
  const savers = {};
  list.addEventListener("input", e => {
    const ta = e.target.closest("textarea"); if (!ta) return;
    fit(ta);
    const fl = ta.closest(".fld"), k = fl.dataset.k;
    pvSetText(k, url, ta.value);
    fl.classList.toggle("changed", norm(ta.value) !== F(k).o);
    saveState("Editing…");
    (savers[k] = savers[k] || debounce(async () => { const only = $("[data-only]", fl); await setText(k, url, norm(ta.value), !!(only && only.checked)); paintState(fl); }, 650))();
  });
  list.addEventListener("change", async e => {
    const cb = e.target.closest("[data-only]"); if (!cb) return;
    const fl = cb.closest(".fld"), k = fl.dataset.k, o = F(k).o, ta = $("textarea", fl);
    if (cb.checked) { await setText(k, url, norm(ta.value), true); if (EDITS.has(ek("text", o, "*"))) { /* keep the everywhere change for the other pages */ } }
    else { if (EDITS.has(ek("text", o, url))) { await Store.remove("text", o, url); EDITS.delete(ek("text", o, url)); } await setText(k, url, norm(ta.value), false); }
    paintState(fl);
  });
  list.addEventListener("click", async e => {
    const r = e.target.closest("[data-reset]");
    if (r) {
      const fl = r.closest(".fld"), k = fl.dataset.k, ta = $("textarea", fl), only = $("[data-only]", fl);
      ta.value = F(k).o; fit(ta); pvSetText(k, url, ta.value);
      await setText(k, url, F(k).o, !!(only && only.checked));
      if (only && only.checked) { only.checked = false; }
      paintState(fl); return;
    }
    const ph = e.target.closest("[data-photo]");
    if (ph) photoModal(ph.dataset.photo, url, () => { const c = ph; c.outerHTML = photoCard(ph.dataset.photo, url); paintIcons(list); pvSetImg(ph.dataset.photo, url); });
  });
  const paintState = fl => {
    const k = fl.dataset.k, v = textNow(k, url), o = F(k).o, live = F(k).t;
    fl.classList.toggle("changed", v !== o);
    $(".state", fl).innerHTML = v !== live ? '<span class="badge">Not published</span>' : v !== o ? '<span class="badge badge--live">Edited</span>' : "";
    const foot = $(".fld__foot", fl);
    const has = $("[data-reset]", foot);
    if (v !== o && !has) foot.insertAdjacentHTML("beforeend", '<button class="linkbtn" data-reset type="button">Back to the original</button>');
    if (v === o && has) has.remove();
  };
  // find on this page
  $("#fq").addEventListener("input", e => {
    const q = norm(e.target.value).toLowerCase();
    $$(".fld", list).forEach(fl => { fl.hidden = !!q && !$("textarea", fl).value.toLowerCase().includes(q); });
    $$(".grp", list).forEach(g => { if (g.dataset.g === "photos") return; const any = $$(".fld", g).some(fl => !fl.hidden); g.hidden = !!q && !any; if (q && any) g.classList.remove("shut"); });
  });
  // preview: desktop / phone
  const stage = $("#stage"), frame = $("#pvf");
  let dev = "desktop";
  const size = () => {
    const W = stage.clientWidth, H = stage.clientHeight;
    if (dev === "phone") { const w = 390, h = 844, s = Math.min(1, (H - 40) / h, (W - 40) / w); Object.assign(frame.style, { width: w + "px", height: h + "px", transform: `scale(${s})`, left: ((W - w * s) / 2) + "px", top: "20px" }); }
    else { const w = Math.max(1280, W), s = W / w; Object.assign(frame.style, { width: w + "px", height: (H / s) + "px", transform: `scale(${s})`, left: "0", top: "0" }); }
    stage.classList.toggle("phone", dev === "phone");
  };
  $$("[data-dev]", view()).forEach(b => b.onclick = () => { dev = b.dataset.dev; $$("[data-dev]", view()).forEach(x => x.classList.toggle("on", x === b)); size(); });
  size(); addEventListener("resize", size);
  frame.addEventListener("load", () => pvMount(frame, p, url));
  setTimeout(() => { const h = $("#pvHint"); if (h) h.hidden = true; }, 6000);
  if (focusKey) setTimeout(() => focusField(focusKey), 60);
}
function focusField(k) {
  const fl = $("#f-" + k); if (!fl) return;
  const g = fl.closest(".grp"); if (g) g.classList.remove("shut");
  fl.hidden = false;
  fl.scrollIntoView({ behavior: "smooth", block: "center" });
  const ta = $("textarea", fl); ta.style.height = "auto"; ta.style.height = ta.scrollHeight + 2 + "px";
  setTimeout(() => ta.focus({ preventScroll: true }), 250);
  fl.classList.add("flash"); setTimeout(() => fl.classList.remove("flash"), 1400);
}

/* the preview knows which words on the page belong to which box */
function pvMount(frame, p, url) {
  let doc; try { doc = frame.contentDocument; } catch (e) { return; }
  if (!doc) return;
  const st = doc.createElement("style");
  st.textContent = `[data-cms-hit]{outline:2px solid rgba(0,113,227,.55)!important;outline-offset:3px;border-radius:3px;cursor:text!important}`;
  doc.head.appendChild(st);
  // the boxes on this page, and the menu, footer and other shared parts that show on it
  const keys = new Map();
  for (const f of p.fields) keys.set(f.k, url);
  for (const s of SEED.shared) for (const f of s.fields) if (!keys.has(f.k)) keys.set(f.k, s.url);
  const index = () => {   // live text -> [text nodes]
    const map = new Map(), w = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, { acceptNode: n => n.parentNode && /^(SCRIPT|STYLE|NOSCRIPT)$/.test(n.parentNode.nodeName) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
    for (let n; (n = w.nextNode());) { const t = norm(n.nodeValue); if (t) (map.get(t) || map.set(t, []).get(t)).push(n); }
    return map;
  };
  PV = { frame, doc, url, keys, shown: new Map() };
  // show the saved (not yet published) changes in the preview, once the page has drawn its menu and footer
  const paintDrafts = () => {
    const idx = index();
    for (const [k, u] of keys) {
      const live = F(k).t, now = textNow(k, u === url ? url : u);
      if (now !== live && idx.has(live)) for (const n of idx.get(live)) n.nodeValue = n.nodeValue.replace(n.nodeValue.trim(), now);
      PV.shown.set(k, now);
    }
    for (const im of p.images) { const now = imgNow(im.o, url); if (now !== im.t) pvMedia(doc, im.o, im.t, now); }
  };
  pvFonts(doc);
  setTimeout(paintDrafts, 700); setTimeout(paintDrafts, 1800);
  // click any words: open their box
  const findKey = el => {
    for (let e = el, i = 0; e && i < 5 && e !== doc.body; e = e.parentElement, i++) {
      const t = norm(e.innerText || e.textContent);
      if (!t) continue;
      for (const [k] of keys) if (PV.shown.get(k) === t || (!PV.shown.has(k) && F(k).t === t)) return k;
    }
    return null;
  };
  let hit = null;
  doc.addEventListener("mouseover", e => { const k = findKey(e.target); if (hit) hit.removeAttribute("data-cms-hit"); hit = k ? e.target : null; if (hit) hit.setAttribute("data-cms-hit", ""); }, true);
  doc.addEventListener("click", e => {
    const a = e.target.closest("a, button");
    const k = findKey(e.target);
    if (a || k) { e.preventDefault(); e.stopPropagation(); }
    if (!k) { if (a) toast("Links are switched off in the preview so you can click words. Use Open page to browse."); return; }
    if (keys.get(k) !== url) {   // a menu or footer text: edit it in its own place
      const s = BYURL[keys.get(k)];
      confirmBox("This is part of the " + s.title.toLowerCase(), "It shows on every page. Open the " + s.title.toLowerCase() + " to change it?", "Open").then(y => y && go(`#/page?u=${encodeURIComponent(s.url)}&k=${k}`));
      return;
    }
    focusField(k);
  }, true);
}
function pvSetText(k, url, value) {
  if (!PV || !PV.doc) return;
  const before = PV.shown.has(k) ? PV.shown.get(k) : F(k).t, now = norm(value) || F(k).o;
  if (before === now) return;
  const w = PV.doc.createTreeWalker(PV.doc.body, NodeFilter.SHOW_TEXT);
  for (let n; (n = w.nextNode());) if (norm(n.nodeValue) === before) n.nodeValue = n.nodeValue.replace(n.nodeValue.trim(), now);
  // a Google map whose place is this box: show the new place (after a short pause, so it doesn't reload on every key)
  $$("iframe[src*='google.']", PV.doc).forEach(f => {
    try { const u = new URL(f.src); if (!/\/maps/.test(u.pathname) || norm(u.searchParams.get("q") || "") !== before) return;
      u.searchParams.set("q", now); clearTimeout(f._t); f._t = setTimeout(() => { f.src = u.toString(); }, 700); } catch (e) {}
  });
  PV.shown.set(k, now);
}
function pvSetImg(o, url) {
  if (!PV || !PV.doc) return;
  const now = imgNow(o, url);
  pvMedia(PV.doc, o, (IMGUSE[o] || {}).t, now);
}
/* in the preview, put the new photo or video in the spot that showed o (or its published version t) */
function pvMedia(doc, o, t, now) {
  $$("img, video, video source", doc).forEach(el => {
    const s = el.getAttribute("data-cms-o") || el.getAttribute("src");
    if (!s || (s !== o && s !== t)) return;
    if (el.tagName === "SOURCE") { if (isVid(now)) { el.src = now; el.parentNode.load(); } return; }
    const wantVid = isVid(now);
    if ((el.tagName === "VIDEO") === wantVid) { el.setAttribute("srcset", ""); el.setAttribute("sizes", ""); el.src = now; el.setAttribute("data-cms-o", o); return; }
    const n = doc.createElement(wantVid ? "video" : "img");
    for (const a of ["class", "id", "style", "width", "height"]) if (el.hasAttribute(a)) n.setAttribute(a, el.getAttribute(a));
    if (wantVid) { n.classList.add("cms-vid"); n.muted = true; n.loop = true; n.autoplay = true; n.playsInline = true; n.setAttribute("muted", ""); }
    else { n.classList.toggle("cms-vid", false); n.alt = el.getAttribute("aria-label") || ""; }
    n.setAttribute("data-cms-o", o); n.src = now; el.replaceWith(n); if (wantVid) n.play().catch(() => {});
  });
}

/* ---------- photos ---------- */
const imgSrc = s => s;   // site paths, Supabase links and (draft mode) data links all work as they are
const isVid = u => /^data:video\/|\.(mp4|webm|mov|m4v)(\?|$)/i.test(u || "");
const thumb = (u, cls) => isVid(u) ? `<video class="${cls}" src="${esc(u)}#t=0.5" muted playsinline preload="metadata"></video>` : "";
function photoCard(o, url) {
  const now = url ? imgNow(o, url) : imgNow(o, "*"), live = (IMGUSE[o] || {}).t || o;
  const name = o.split("?")[0].split("/").pop();
  const badge = now !== live ? '<span class="badge">Not published</span>' : now !== o ? '<span class="badge badge--live">Replaced</span>' : "";
  return `<div class="ph" data-photo="${esc(o)}"><div class="ph__img" style="${isVid(now) ? "" : `background-image:url('${esc(imgSrc(now)).replace(/'/g, "%27")}')`}">${thumb(now, "ph__vid")}${badge}${isVid(now) ? '<span class="ph__play" aria-hidden="true"></span>' : ""}</div><div class="ph__meta"><b>${esc(name)}</b><span>${(IMGUSE[o] || { pages: [] }).pages.length} page${(IMGUSE[o] || { pages: [] }).pages.length === 1 ? "" : "s"}</span></div></div>`;
}
function photoModal(o, url, done) {
  const use = IMGUSE[o] || { pages: [url] };
  const now = imgNow(o, url || "*");
  const onlyHere = url && EDITS.has(ek("image", o, url));
  const vidOnly = (IMGUSE[o] || {}).kind === "video", picOnly = (IMGUSE[o] || {}).kind === "share";
  const what = vidOnly ? "video" : picOnly ? "photo" : "photo or video";
  modal(`<h2>Replace ${vidOnly ? "video" : "photo"}</h2>
    ${isVid(now) ? `<video class="modal__img" src="${esc(now)}" muted loop autoplay playsinline controls></video>` : `<img class="modal__img" src="${esc(imgSrc(now))}" alt="">`}
    <p class="muted small">${esc(o.split("?")[0])}<br>Used on: ${use.pages.map(u => esc(pageName(u))).join(", ")}</p>
    ${url && use.pages.length > 1 ? `<label class="small"><input type="checkbox" id="phOnly" ${onlyHere ? "checked" : ""}> Only on ${esc(pageName(url))}</label>` : ""}
    <p class="muted small">Use the same shape (wide, tall or square) as the one it replaces, so it fits the layout.${vidOnly ? "" : " Photos: JPG or WebP, ideally under 600 KB."}${picOnly ? "" : " Videos: MP4, a few seconds long, under 20 MB. They play silently on a loop."}</p>
    <div class="modal__foot">${now !== o ? '<button class="btn" data-orig>Back to the original</button>' : ""}<button class="btn btn--dark" data-up>${ic("upload")}<span>Choose a new ${what}</span></button></div>`,
  (box, close) => {
    const scopeUrl = url || "*";
    const only = () => !!($("#phOnly", box) && $("#phOnly", box).checked);
    const orig = $("[data-orig]", box);
    if (orig) orig.onclick = async () => { await setImage(o, scopeUrl, o, only()); close(); done && done(); toast("Photo set back to the original."); };
    $("[data-up]", box).onclick = () => {
      const pick = $("#filePick"); pick.value = "";
      pick.accept = vidOnly ? "video/mp4,video/webm,video/quicktime" : picOnly ? "image/*" : "image/*,video/mp4,video/webm,video/quicktime";
      pick.onchange = async () => {
        const f = pick.files[0]; if (!f) return;
        const vid = /^video\//.test(f.type) || isVid(f.name);
        if (vidOnly && !vid) return toast("This spot holds a video: choose an MP4 video.", "err");
        if (picOnly && vid) return toast("This spot only takes a photo.", "err");
        if (vid && f.size > 50e6) return toast("That video is over 50 MB. Please use a shorter or smaller MP4 (under 20 MB is best).", "err");
        $("[data-up] span", box).textContent = "Uploading…";
        try { const u = await Store.upload(f); await setImage(o, scopeUrl, u, only()); close(); done && done(); toast((vid ? "Video" : "Photo") + " in place. Publish to put it on the website."); }
        catch (e) { toast(e.message || "Upload failed.", "err"); $("[data-up] span", box).textContent = "Choose a new " + what; }
      };
      pick.click();
    };
  });
}
function viewPhotos(q) {
  const filter = q.get("p") || "";
  const list = Object.values(IMGUSE).filter(x => !filter || x.pages.includes(filter));
  view().innerHTML = `<div class="pagehead"><div class="grow"><h1>Photos and videos</h1><p class="muted">${list.length} photos and videos on the website. Click one to replace it with a new photo or a video.</p></div>
    <select id="phFilter" style="width:auto;min-width:220px"><option value="">All pages</option>${SEED.pages.filter(p => p.images.length).map(p => `<option value="${esc(p.url)}" ${p.url === filter ? "selected" : ""}>${esc(p.title)}</option>`).join("")}</select></div>
    <div class="photos">${list.map(x => photoCard(x.o, filter || null)).join("") || '<div class="empty">No photos.</div>'}</div>`;
  paintIcons(view());
  $("#phFilter").onchange = e => go("#/photos" + (e.target.value ? "?p=" + encodeURIComponent(e.target.value) : ""));
  $(".photos", view()).addEventListener("click", e => { const c = e.target.closest("[data-photo]"); if (c) photoModal(c.dataset.photo, filter || null, () => viewPhotos(q)); });
}

/* ---------- fonts ----------
   Four groups (tools/cms/fonts.json). A choice is saved like a word change: kind "text", o "font:<group>", t the font,
   scope "@fonts". On publish tools/cms/cms.py writes assets/cms-fonts.css, which every page loads last. */
const FONTCFG = () => SEED.fonts || { groups: [], fonts: [], live: {} };
const fontGroup = id => FONTCFG().groups.find(g => g.id === id) || { id, name: id, default: "", vars: [] };
const fontInfo = name => FONTCFG().fonts.find(f => f.name === name) || { name, kind: "sans", spec: "" };
const fontNow = id => (EDITS.get(ek("text", "font:" + id, "@fonts")) || {}).t || fontGroup(id).default;
const fontLive = id => FONTCFG().live["font:" + id] || fontGroup(id).default;
const fontStack = name => { const k = fontInfo(name).kind; return `"${name}", ` + (k === "serif" ? "Georgia, serif" : k === "mono" ? '"Courier New", monospace' : '"Helvetica Neue", Arial, sans-serif'); };
const fontLine = h => `Font for ${fontGroup(h.o.slice(5)).name}: ${h.after || fontGroup(h.o.slice(5)).default + " (the original)"}`;
const fontUrl = names => "https://fonts.googleapis.com/css2?" + [...new Set(names)].map(n => { const f = fontInfo(n); return "family=" + n.replace(/ /g, "+") + (f.spec ? ":" + f.spec : ""); }).join("&") + "&display=swap";
const fontsLoaded = new Set();
function loadFonts(doc, names) {   // add the Google Fonts for these families to a document (this page, or the preview)
  const want = names.filter(n => n && !(doc === document && fontsLoaded.has(n)));
  if (!want.length) return;
  for (let i = 0; i < want.length; i += 12) {
    const l = doc.createElement("link"); l.rel = "stylesheet"; l.href = fontUrl(want.slice(i, i + 12)); doc.head.appendChild(l);
  }
  if (doc === document) want.forEach(n => fontsLoaded.add(n));
}
function pvFonts(doc) {   // the preview shows the saved (not yet published) font choices
  if (!doc) return;
  const groups = FONTCFG().groups, rules = [], names = [];
  for (const g of groups) { const n = fontNow(g.id); if (n !== fontLive(g.id) || n !== g.default) { names.push(n); for (const v of g.vars) rules.push(`${v}: ${fontStack(n)} !important;`); } }
  let st = doc.getElementById("cms-pv-fonts");
  if (!st) { st = doc.createElement("style"); st.id = "cms-pv-fonts"; doc.head.appendChild(st); }
  st.textContent = rules.length ? `:root, .cscroll { ${rules.join(" ")} }` : "";
  loadFonts(doc, names);
}
async function setFont(id, name) {
  const o = "font:" + id, g = fontGroup(id), key = ek("text", o, "@fonts");
  const before = fontNow(id);
  if (before === name) return;
  saving++; saveState("Saving…");
  try {
    if (name === g.default) { if (EDITS.has(key)) { await Store.remove("text", o, "@fonts"); EDITS.delete(key); } }
    else { const row = { kind: "text", o, t: name, scope: "@fonts", page: "@fonts" }; await Store.upsert(row); EDITS.set(key, Object.assign({ updated_at: new Date().toISOString(), updated_by: ME.email }, row)); }
    const h = { kind: "text", o, scope: "@fonts", page: "@fonts", before, after: name === g.default ? null : name, at: new Date().toISOString(), by: ME.email };
    HIST.unshift(h); await Store.addHistory(h);
    saveState("All changes saved", true);
  } catch (e) { console.error(e); saveState(""); toast("Could not save: " + (e.message || e), "err"); }
  finally { saving--; refreshPub(); }
}
function viewFonts() {
  const { groups, fonts } = FONTCFG();
  loadFonts(document, fonts.map(f => f.name));
  const kinds = [["sans", "Clean (sans serif)"], ["serif", "Classic (serif)"], ["mono", "Typewriter (monospace)"]];
  const options = (g, cur) => (g.mono ? [kinds[2], kinds[0], kinds[1]] : kinds).map(([k, label]) =>
    `<optgroup label="${label}">${fonts.filter(f => f.kind === k).map(f => `<option value="${esc(f.name)}" ${f.name === cur ? "selected" : ""}>${esc(f.name)}${f.name === g.default ? " (original)" : ""}</option>`).join("")}</optgroup>`).join("");
  const card = g => {
    const cur = fontNow(g.id), live = fontLive(g.id);
    const badge = cur !== live ? '<span class="badge">Not published</span>' : cur !== g.default ? '<span class="badge badge--live">Changed</span>' : "";
    return `<div class="card fontcard" data-g="${esc(g.id)}">
      <div class="fontcard__top"><div class="grow"><h2>${esc(g.name)} ${badge}</h2><p class="muted small">${esc(g.hint)}</p></div>
        <select data-font aria-label="Font for ${esc(g.name)}">${options(g, cur)}</select></div>
      <div class="fontcard__sample${g.upper ? " up" : ""}" style='font-family:${esc(fontStack(cur))}'>${esc(g.sample)}</div>
      <div class="fontcard__foot"><span class="muted small">Now: <b>${esc(cur)}</b>${cur !== g.default ? ` · original: ${esc(g.default)}` : ""}</span>${cur !== g.default ? '<button class="linkbtn" data-orig type="button">Back to the original</button>' : ""}</div>
    </div>`;
  };
  view().innerHTML = `<div class="pagehead"><div class="grow"><h1>Fonts</h1><p class="muted">The website uses four groups of fonts. Pick a font for a group and every page changes together. Open any page to see it in the preview, then publish.</p></div>
    <a class="btn" href="#/page?u=%2F">${ic("desktop")}<span>See it on the home page</span></a></div>
    <div class="fontgrid">${groups.map(card).join("")}</div>`;
  paintIcons(view());
  $$(".fontcard", view()).forEach(c => {
    const id = c.dataset.g;
    $("[data-font]", c).onchange = async e => { await setFont(id, e.target.value); viewFonts(); toast("Font saved. Publish to put it on the website."); };
    const o = $("[data-orig]", c); if (o) o.onclick = async () => { await setFont(id, fontGroup(id).default); viewFonts(); toast("Back to the original font."); };
  });
}

/* ---------- search everywhere ---------- */
function viewSearch(q) {
  const s = norm(q).toLowerCase();
  const hits = [];
  if (s.length >= 2) for (const [k, f] of Object.entries(SEED.fields)) {
    const where = (f.where || []);
    const cur = textNow(k, where[0] || "*");
    if (cur.toLowerCase().includes(s) || f.o.toLowerCase().includes(s)) hits.push({ k, cur, where });
    if (hits.length > 300) break;
  }
  const mark = t => { const i = t.toLowerCase().indexOf(s); return i < 0 ? esc(t) : esc(t.slice(0, i)) + "<mark>" + esc(t.slice(i, i + s.length)) + "</mark>" + esc(t.slice(i + s.length)); };
  view().innerHTML = `<div class="pagehead"><div class="grow"><h1>Search</h1><p class="muted">${s.length < 2 ? "Type at least two letters." : `${hits.length}${hits.length > 300 ? "+" : ""} result${hits.length === 1 ? "" : "s"} for “${esc(q)}”`}</p></div></div>
    ${hits.length ? `<div class="card"><div class="res">${hits.map(h => { const u = h.where[0]; const names = h.where.slice(0, 3).map(pageName).join(", ") + (h.where.length > 3 ? ` and ${h.where.length - 3} more` : ""); return `<a href="#/page?u=${encodeURIComponent(u)}&k=${h.k}"><span class="txt">${mark(h.cur.length > 220 ? h.cur.slice(0, 220) + "…" : h.cur)}</span><span class="meta">${esc(names)}</span></a>`; }).join("")}</div></div>` : ""}`;
}

/* ---------- activity ---------- */
function viewActivity() {
  const rows = HIST.slice(0, 200);
  view().innerHTML = `<div class="pagehead"><div class="grow"><h1>Activity</h1><p class="muted">Every change, newest first. Undo puts the words back as they were before that change.</p></div></div>
    <div class="card">${rows.length ? rows.map((h, i) => `<div class="act"><span class="avatar">${esc(initials(h.by))}</span>
      <span class="what">${h.scope === "@fonts" ? esc(fontLine(h)) : h.kind === "image" ? `Photo ${h.after ? "replaced" : "set back to the original"}` : h.after == null ? `Set back to the original: “${esc(h.o.slice(0, 120))}”` : `<s>${esc((h.before || "").slice(0, 120))}</s> → ${esc(h.after.slice(0, 160))}`}</span>
      <button class="btn btn--sm" data-undo="${i}">${ic("undo")}Undo</button>
      <span class="meta">${esc(h.page ? pageName(h.page) : "")}${h.scope !== "*" && h.scope !== "@fonts" ? " only" : ""} · ${esc(h.by || "")} · ${esc(ago(h.at))}</span></div>`).join("") : '<div class="empty">No changes yet.</div>'}</div>`;
  paintIcons(view());
  $$("[data-undo]", view()).forEach(b => b.onclick = async () => {
    const h = rows[+b.dataset.undo];
    if (!await confirmBox("Undo this change?", "The words go back to how they were before it. You can publish afterwards.", "Undo")) return;
    if (h.scope === "@fonts") await setFont(h.o.slice(5), h.before || fontGroup(h.o.slice(5)).default);
    else if (h.kind === "image") await setImage(h.o, h.scope === "*" ? (h.page || "*") : h.scope, h.before, h.scope !== "*");
    else {
      const k = Object.keys(SEED.fields).find(x => SEED.fields[x].o === h.o);
      if (!k) { toast("Those words are no longer on the website.", "err"); return; }
      await setText(k, h.scope === "*" ? (h.page || "*") : h.scope, h.before ?? h.o, h.scope !== "*");
    }
    toast("Undone."); viewActivity();
  });
}

/* ---------- team ---------- */
async function viewTeam() {
  view().innerHTML = `<div class="pagehead"><div class="grow"><h1>Team</h1><p class="muted">The people who can sign in and change the website.</p></div>${LIVE && ME.role === "owner" ? `<button class="btn btn--dark" id="addPerson">${ic("users")}<span>Add a person</span></button>` : ""}</div>
    <div class="card"><div class="card__body" id="teamBody"><div class="empty">Loading…</div></div></div>`;
  paintIcons(view());
  const body = $("#teamBody");
  if (!LIVE) { body.innerHTML = '<div class="empty">Team accounts work once the editor is connected (see the setup guide). In draft mode only this browser can edit.</div>'; return; }
  if (ME.role !== "owner") { body.innerHTML = '<div class="empty">Only the owner account can add or remove people.</div>'; return; }
  const draw = async () => {
    try {
      const { users } = await Store.team({ action: "list" });
      body.innerHTML = `<div class="tablewrap"><table class="table"><thead><tr><th>Name</th><th class="hide-s">Email</th><th>Role</th><th class="hide-s">Last signed in</th><th></th></tr></thead><tbody>${users.map(u => `<tr data-e="${esc(u.email)}"><td class="t">${esc(u.name || "")}</td><td class="hide-s">${esc(u.email)}</td><td>${u.role === "owner" ? "Owner" : "Editor"}</td><td class="hide-s">${esc(u.lastSignIn ? ago(u.lastSignIn) : "never")}</td><td style="text-align:right"><button class="iconbtn" data-more="${esc(u.email)}" aria-label="More">${ic("more")}</button></td></tr>`).join("")}</tbody></table></div>`;
      paintIcons(body);
      $$("[data-more]", body).forEach(b => b.onclick = e => { e.stopPropagation(); const email = b.dataset.more; popMenu(b, [
        ["Set a new password", () => passwordModal(email)],
        ["Make owner", async () => { try { await Store.team({ action: "update", email, role: "owner" }); draw(); } catch (er) { toast(er.message, "err"); } }],
        ["Make editor", async () => { try { await Store.team({ action: "update", email, role: "editor" }); draw(); } catch (er) { toast(er.message, "err"); } }],
        ["Remove from the team", async () => { if (await confirmBox("Remove " + email + "?", "They will no longer be able to sign in.", "Remove", true)) { try { await Store.team({ action: "remove", email }); draw(); } catch (er) { toast(er.message, "err"); } } }],
      ]); });
    } catch (e) { body.innerHTML = `<div class="empty">${esc(e.message)}</div>`; }
  };
  draw();
  const add = $("#addPerson");
  if (add) add.onclick = () => modal(`<h2>Add a person</h2>
    <label class="field"><span>Name</span><input type="text" id="tName"></label>
    <label class="field"><span>Email</span><input type="email" id="tEmail"></label>
    <label class="field"><span>Password (at least 10 characters; share it with them yourself)</span><input type="text" id="tPass" autocomplete="new-password"></label>
    <label class="field"><span>Role</span><select id="tRole"><option value="editor">Editor: words, photos and publishing</option><option value="owner">Owner: also adds and removes people</option></select></label>
    <div class="modal__foot"><button class="btn" data-no>Cancel</button><button class="btn btn--dark" data-yes>Add</button></div>`, (box, close) => {
      $("[data-no]", box).onclick = close;
      $("[data-yes]", box).onclick = async () => {
        try { const r = await Store.team({ action: "create", name: $("#tName").value.trim(), email: $("#tEmail").value.trim(), password: $("#tPass").value, role: $("#tRole").value }); close(); toast(r.message || "Added."); draw(); }
        catch (e) { toast(e.message, "err"); }
      };
    });
  const passwordModal = email => modal(`<h2>New password</h2><p class="muted">For ${esc(email)}. At least 10 characters.</p><label class="field"><span>Password</span><input type="text" id="np" autocomplete="new-password"></label><div class="modal__foot"><button class="btn" data-no>Cancel</button><button class="btn btn--dark" data-yes>Save</button></div>`, (box, close) => {
    $("[data-no]", box).onclick = close;
    $("[data-yes]", box).onclick = async () => { try { await Store.team({ action: "password", email, password: $("#np").value }); close(); toast("Password changed."); } catch (e) { toast(e.message, "err"); } };
  });
}

/* ---------- publish ---------- */
async function publish() {
  const n = pending();
  if (!LIVE) { await Store.publish(); toast("Draft mode: the changes file was downloaded."); return; }
  if (!await confirmBox("Publish to the website?", `${n} change${n === 1 ? "" : "s"} will go live on hexahessman.com in about three minutes.`, "Publish")) return;
  const b = $("#publishBtn"); b.disabled = true; $("span", b).textContent = "Publishing…";
  try { const r = await Store.publish(); toast(r.message || "Publishing."); PUBS = await Store.publishes(); }
  catch (e) { toast(e.message, "err"); }
  finally { $("span", b).textContent = "Publish to website"; refreshPub(); }
}

/* ---------- start ---------- */
async function enter() {
  $("#login").hidden = true; $("#app").hidden = false;
  $("#localBanner").hidden = LIVE;
  $("#meName").textContent = ME.name || ME.email;
  $("#meAvatar").textContent = initials(ME.name || ME.email);
  $$('#nav a[data-r="team"]').forEach(a => a.hidden = LIVE && ME.role !== "owner");
  paintIcons();
  try { await Promise.all([loadSeed(), loadEdits(), Store.history(500).then(h => HIST = h), Store.publishes().then(p => PUBS = p)]); }
  catch (e) { console.error(e); toast("Could not load: " + (e.message || e), "err"); }
  refreshPub();
  addEventListener("hashchange", route);
  route();
}
function bindChrome() {
  $("#publishBtn").onclick = publish;
  $("#downloadBtn").onclick = download;
  $("#sideToggle").onclick = () => $("#app").classList.toggle("sideopen");
  $("#meMenu").onclick = e => { e.stopPropagation(); popMenu($("#meMenu"), [
    ["Open the website", () => open("/", "_blank")],
    ...(LIVE ? [["Sign out", async () => { await Store.signOut(); location.reload(); }]] : [["Download the changes file", download], ["Clear all draft changes", async () => { if (await confirmBox("Clear all draft changes?", "Every change kept in this browser is removed. This cannot be undone.", "Clear", true)) { localStorage.removeItem(LKEY); location.reload(); } }]]),
  ]); };
  const q = $("#q");
  const run = debounce(() => { const v = q.value.trim(); if (v.length >= 2) go("#/search?q=" + encodeURIComponent(v)); }, 250);
  q.addEventListener("input", run);
  q.addEventListener("keydown", e => { if (e.key === "Enter") { const v = q.value.trim(); if (v) go("#/search?q=" + encodeURIComponent(v)); } });
  addEventListener("keydown", e => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); q.focus(); q.select(); } });
  addEventListener("beforeunload", e => { if (saving) { e.preventDefault(); e.returnValue = ""; } });
}
async function start() {
  bindChrome(); paintIcons();
  if (!LIVE) { ME = await Store.user(); return enter(); }
  sb = window.supabase.createClient(CFG.supabaseUrl, CFG.supabaseAnonKey, { auth: { persistSession: true, autoRefreshToken: true } });
  const show = msg => { $("#app").hidden = true; $("#login").hidden = false; const er = $("#loginErr"); er.hidden = !msg; er.textContent = msg || ""; };
  const tryEnter = async () => {
    const u = await Store.user();
    if (!u) return show();
    if (!u.role) { await Store.signOut(); return show(u.email + " is not on the team. Ask the owner to add you."); }
    ME = u; enter();
  };
  $("#loginForm").onsubmit = async e => {
    e.preventDefault();
    const fd = new FormData(e.target), b = $("button[type=submit]", e.target);
    b.disabled = true; b.textContent = "Signing in…";
    const { error } = await sb.auth.signInWithPassword({ email: String(fd.get("email")).trim(), password: String(fd.get("password")) });
    b.disabled = false; b.textContent = "Sign in";
    if (error) return show(error.message === "Invalid login credentials" ? "That email and password do not match." : error.message);
    tryEnter();
  };
  $("#forgot").onclick = async () => {
    const email = $("#loginForm").email.value.trim();
    if (!email) return show("Type your email first, then press Forgot your password.");
    const { error } = await sb.auth.resetPasswordForEmail(email, { redirectTo: location.origin + "/admin/" });
    show(error ? error.message : "If that email is on the team, a link to set a new password is on its way.");
  };
  sb.auth.onAuthStateChange(async (ev) => {
    if (ev === "PASSWORD_RECOVERY") {
      const p = prompt("Choose a new password (at least 10 characters):");
      if (p && p.length >= 10) { const { error } = await sb.auth.updateUser({ password: p }); toast(error ? error.message : "Password changed."); }
    }
  });
  tryEnter();
}
start();
})();
