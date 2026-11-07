#!/usr/bin/env python3
"""Generate the HexaHessman static content pages from content.py into the site root.

Usage: python3 build.py [site_root]   (default /Users/poopiepie/Hexahessman)
Does not touch /index.html or anything in /assets/.
"""
import json
import html as _html
import os
import re
import sys

import content as C

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/Users/poopiepie/Hexahessman"
WRITTEN = []

# ------------------------------------------------------------------ text helpers
_CONFIRM = re.compile(r"\s*\[(?:confirm|Add |if applicable|range|e\.g\.|and pastilles)[^\]]*\]")
_ANYBRACKET = re.compile(r"\s*\[[^\]]*\]")


def is_placeholder(s):
    """True when the text is nothing but a bracketed note (or empty after stripping notes)."""
    if s is None:
        return True
    t = _ANYBRACKET.sub("", s).strip(" ·/—-")
    return t == ""


def clean(s):
    """Drop bracketed editorial notes from copy that is otherwise real."""
    s = _CONFIRM.sub("", s)
    s = _ANYBRACKET.sub("", s)
    s = re.sub(r"\s+·\s*$", "", s)          # trailing "· lumps" separators left behind
    s = re.sub(r"\s*/\s*$", "", s)
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s


def esc(s):
    return _html.escape(clean(s), quote=False)


def esc_attr(s):
    return _html.escape(clean(s), quote=True)


def meta_desc(text, n=158):
    t = clean(text)
    if len(t) <= n:
        return t
    cut = t[:n].rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:—-") + "…"


# ------------------------------------------------------------------ url helpers
PRODUCT_BY_SLUG = {p["slug"]: p for p in C.PRODUCTS}
GROUP_BY_SLUG = {g["slug"]: g for g in C.GROUPS}
PRODUCT_NAME_TO_SLUG = {}
for g in C.GROUPS:
    for slug, name, _ in g["products"]:
        PRODUCT_NAME_TO_SLUG[name] = slug
for p in C.PRODUCTS:
    PRODUCT_NAME_TO_SLUG.setdefault(p["title"], p["slug"])
PRODUCT_NAME_TO_SLUG.update(C.RELATED_ALIASES)


def group_url(gslug):
    return f"/commodities/{gslug}/"


def product_url(pslug):
    return f"/commodities/{PRODUCT_BY_SLUG[pslug]['group']}/{pslug}/"


def short_name(pslug):
    g = GROUP_BY_SLUG[PRODUCT_BY_SLUG[pslug]["group"]]
    for s, name, _ in g["products"]:
        if s == pslug:
            return name
    return PRODUCT_BY_SLUG[pslug]["title"]


def descriptor(pslug):
    g = GROUP_BY_SLUG[PRODUCT_BY_SLUG[pslug]["group"]]
    for s, _, d in g["products"]:
        if s == pslug:
            return d
    return ""


# ------------------------------------------------------------------ html components
def buttons(labels, first_solid=True):
    out = []
    for i, label in enumerate(labels):
        href = C.BUTTONS[label]
        cls = "pill solid" if (i == 0 and first_solid) else "pill"
        extra = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        out.append(f'<a class="{cls}" href="{href}"{extra}>{esc(label)}</a>')
    return '<div class="btn-row">' + "".join(out) + "</div>"


def crumbs(items):
    """items: list of (label, href or None for current)."""
    parts = []
    for i, (label, href) in enumerate(items):
        inner = f'<a href="{href}">{esc(label)}</a>' if href else esc(label)
        parts.append(inner if i == 0 else f"<span>{inner}</span>")
    return ""   # no breadcrumbs anywhere on the site (user, 2026-11-06); kept as a function so the pages need no other change


def hero_plain(crumb_items, eyebrow, h1, paras, btns=None, extra=""):
    lead = f'<p class="lead">{esc(paras[0])}</p>' if paras else ""
    rest = "".join(f'<p class="lead">{esc(p)}</p>' for p in paras[1:])
    b = buttons(btns) if btns else ""
    return f"""<section class="hero plain"><div class="wrap">
  {crumbs(crumb_items) if crumb_items else ""}
  <p class="eyebrow">{esc(eyebrow)}</p>
  <h1>{esc(h1)}</h1>
  {lead}{rest}{extra}{b}
</div></section>"""


def hero_image(img, eyebrow, h1, lead, btns):
    return f"""<section class="hero">
  <div class="media"><img src="{img}" alt=""></div>
  <div class="wrap">
    <p class="eyebrow">{esc(eyebrow)}</p>
    <h1>{esc(h1)}</h1>
    <p class="lead">{esc(lead)}</p>
    {buttons(btns)}
  </div>
</section>"""


def section(body, title=None, eyebrow=None, lead=None, id_=None, cls="section"):
    head = ""
    if title or eyebrow or lead:
        head = '<div class="section-head">'
        if eyebrow:
            head += f'<p class="eyebrow">{esc(eyebrow)}</p>'
        if title:
            head += f"<h2>{esc(title)}</h2>"
        if lead:
            head += f'<p class="lead">{esc(lead)}</p>'
        head += "</div>"
    idattr = f' id="{id_}"' if id_ else ""
    return f'<section class="{cls}"{idattr}><div class="wrap">{head}{body}</div></section>\n'


def ul_list(items):
    items = [i for i in items if not is_placeholder(i)]
    if not items:
        return ""
    return '<ul class="list">' + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def spec_table(block):
    rows = []
    for r in block["rows"]:
        cells = list(r)
        # drop a row whose value cells are all placeholders
        if all(is_placeholder(c) or c in ("—", "") for c in cells[1:]):
            continue
        tds = [f"<td>{esc(cells[0])}</td>"]
        for c in cells[1:]:
            tds.append("<td>—</td>" if is_placeholder(c) else f"<td>{esc(c)}</td>")
        rows.append("<tr>" + "".join(tds) + "</tr>")
    if not rows:
        return ""
    # every table reads as a chart with a header row (user, 2026-11-06); two-column tables without headers get the plain pair
    heads = block.get("headers") or (["Parameter", "Specification"] if all(len(r) == 2 for r in block["rows"]) else None)
    thead = ""
    if heads:
        thead = "<thead><tr>" + "".join(f"<th>{esc(h)}</th>" for h in heads) + "</tr></thead>"
    title = f'<h3 class="spec-title">{esc(block["title"])}</h3>' if block.get("title") else ""
    wide = " wide" if heads and len(heads) >= 4 else ""   # four or more columns get more room
    return f'{title}<div class="spec-scroll{wide}"><table class="spec">{thead}<tbody>{"".join(rows)}</tbody></table></div>'


def defs_table(defs):
    rows = [(t, d) for t, d in defs if not is_placeholder(d)]
    if not rows:
        return ""
    return '<div class="spec-scroll"><table class="spec"><tbody>' + "".join(f"<tr><td>{esc(t)}</td><td>{esc(d)}</td></tr>" for t, d in rows) + "</tbody></table></div>"


def card(h, p, href=None, more=None, extra=""):
    tag = "a" if href else "div"
    hrefattr = f' href="{href}"' if href else ""
    m = f'<span class="more">{esc(more)}</span>' if more else ""
    return f'<{tag} class="card"{hrefattr}><h3>{esc(h)}</h3>{"<p>" + esc(p) + "</p>" if p else ""}{extra}{m}</{tag}>'


def grid(cards_html, cols="c3"):
    return f'<div class="grid {cols}">{"".join(cards_html)}</div>'


def render_section(s, h_level=2):
    """Generic renderer for a content section dict (see content.py)."""
    body = []
    if s.get("paras"):
        body.append("".join(f"<p>{esc(p)}</p>" for p in s["paras"] if not is_placeholder(p)))
    if s.get("items"):
        body.append(ul_list(s["items"]))
    if s.get("defs"):
        body.append(defs_table(s["defs"]))
    if s.get("lists"):   # (heading, items): "Characteristics", "Applications"…
        body.append("".join(f'<h3 class="zig-sub">{esc(h)}</h3>{ul_list(items)}' for h, items in s["lists"]))
    if s.get("sublists"):
        cards = []
        for head, items in s["sublists"]:
            cards.append(f'<div class="card"><h3>{esc(head)}</h3>{ul_list(items)}</div>')
        body.append(grid(cards, "c2"))
    if s.get("cards"):
        cards = []
        for name, desc, apps in s["cards"]:
            extra = f'<p class="apps">{esc(apps)}</p>' if apps else ""
            cards.append(card(name, desc, extra=extra))
        body.append(grid(cards, "c3"))
    if s.get("links"):
        cards = []
        for label, href in s["links"]:
            cards.append(f'<a class="card" href="{href}" target="_blank" rel="noopener"><h3>{esc(label)}</h3><span class="more">Learn more →</span></a>')
        body.append(grid(cards, "c4"))
    if s.get("fuels"):   # (label, id, blurb, link): four photo tiles in one line that rise / drop in alternately, each with a drop-down (assets/spin-row.js)
        tiles = "".join(
            f'<button type="button" class="fuel-tile" style="--i:{i}" aria-expanded="false" aria-controls="fuel-{cid}">'
            f'<img src="{s.get("tile_dir", "/assets/engineering/fuel-")}{cid}.jpg" alt="" loading="lazy" decoding="async" width="900" height="675"><span class="fuel-veil"></span>'
            f'<span class="fuel-label">{esc(label)}</span><span class="fuel-more">Learn more</span></button>' for i, (label, cid, _, _) in enumerate(s["fuels"]))
        panels = "".join(
            f'<div class="spin-panel" id="fuel-{cid}" aria-hidden="true"><div class="spin-panel-in"><div><p>{esc(blurb)}</p>'
            + (f'<div class="btn-row"><a class="pill" href="{href}">Read more about {esc(label)}</a></div>' if href.startswith("#") else   # a section further down this page
               f'<div class="btn-row"><a class="pill" href="{href}" target="_blank" rel="noopener">{esc(label)} at manntek.se</a></div>')
            + '</div></div></div>' for label, cid, blurb, href in s["fuels"])
        body.append(f'<div class="spin-row fuel-row"><div class="fuel-tiles">{tiles}</div><div class="spin-panels">{panels}</div></div>')
    if s.get("diagram"):   # an image with labels that pop out one at a time, each with a leader line drawn to its part (assets/spin-row.js adds .in)
        d = s["diagram"]; W, H = d["w"], d["h"]
        lines = "".join(f'<line x1="{lx}" y1="{ly}" x2="{px}" y2="{py}" pathLength="1" style="--i:{i}"/><circle cx="{px}" cy="{py}" r="7" style="--i:{i}"/>' for i, (_, lx, ly, px, py) in enumerate(d["labels"]))
        tags = "".join(f'<span class="dg-tag" style="left:{lx / W * 100:.2f}%;top:{ly / H * 100:.2f}%;--i:{i}">{esc(lab)}</span>' for i, (lab, lx, ly, _, _) in enumerate(d["labels"]))
        body.append(f'<div class="dg-scroll"><figure class="dg" style="aspect-ratio:{W}/{H}"><img src="{d["img"]}" alt="{esc_attr(s["title"])}" loading="lazy" decoding="async" width="{W}" height="{H}">'
                    f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="none" aria-hidden="true">{lines}</svg>{tags}</figure></div>')
    if s.get("videos"):   # (title, YouTube id): embedded players, two across
        vids = "".join(
            f'<figure class="yt"><div class="yt-frame"><iframe src="https://www.youtube-nocookie.com/embed/{vid}?rel=0" title="{esc_attr(vt)}" loading="lazy" '
            f'allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe></div>'
            f'<figcaption>{esc(vt)}</figcaption></figure>' for vt, vid in s["videos"])
        body.append(f'<div class="yt-grid">{vids}</div>')
    if s.get("spec"):
        tables = [spec_table(b) for b in s["spec"]]
        tables = [t for t in tables if t]
        body.append('<div class="spec-stack">' + "".join(tables) + "</div>")
    if s.get("note") and not is_placeholder(s["note"]):
        body.append(f'<p class="note">{esc(s["note"])}</p>')
    content = "".join(b for b in body if b)
    if not content.strip():
        return ""
    if s.get("media"):   # the product's picture on one side, its text on the other
        m = s["media"]
        if m.get("video"):   # a turntable cut into 96 still frames (<clip>/000.webp …); spin-row.js draws the frame that matches the scroll
            media = (f'<figure class="zig-media" data-spin="{m["video"]}/" data-frames="96"><canvas width="760" height="760" role="img" aria-label="{esc_attr(s["title"])}, turning"></canvas>'
                     f'<img class="spin-still" src="{m["video"]}/000.webp" alt="" width="760" height="760"></figure>')
        elif m.get("layers"):   # the photo with its orange panels as separate layers that arrive one by one (ends on the exact photo)
            slug = m["layers"]; base = f"/assets/engineering/shibata/{slug}"
            with open(os.path.join(ROOT, f"assets/engineering/shibata/{slug}-panels.json")) as fh:
                panels = json.load(fh)
            pl = "".join(f'<img class="pl" src="{base}-p{i}.webp" alt="" style="left:{p["l"]}%;top:{p["t"]}%;width:{p["w"]}%;height:{p["h"]}%;--i:{i}">' for i, p in enumerate(panels))
            media = f'<figure class="zig-media zig-layers"><img class="pl-base" src="{base}-base.jpg" alt="{esc_attr(s["title"])}" loading="lazy" decoding="async">{pl}</figure>'
        elif m.get("appear"):   # a clip that plays once each time it comes into view and rests on its last frame (spin-row.js)
            media = (f'<figure class="zig-media zig-photo"><video class="zig-appear" muted playsinline preload="auto" poster="{m["appear"]}.jpg" aria-label="{esc_attr(s["title"])}">'
                     f'<source src="{m["appear"]}.mp4" type="video/mp4"></video></figure>')
        elif m.get("loop"):   # a floating clip that starts and ends on the photo, so it loops seamlessly
            media = (f'<figure class="zig-media zig-photo"><video autoplay muted loop playsinline preload="metadata" poster="{m["loop"]}.jpg" aria-label="{esc_attr(s["title"])}">'
                     f'<source src="{m["loop"]}.mp4" type="video/mp4"></video></figure>')
        else:
            media = f'<figure class="zig-media{" zig-photo" if m["image"].endswith(".jpg") else ""}"><img src="{m["image"]}" alt="{esc_attr(s["title"])}" loading="lazy" decoding="async"></figure>'
        # the product's technical drawing, faded like a background behind the words (user, 2026-11-06; drawings from the old site / the 2026 profile)
        dw = f' style="width:{s["drawing_w"]}"' if s.get("drawing_w") else ""   # a squarer drawing can ask for less width
        drw = f'<img class="zig-drawing" src="{s["drawing"]}" alt="" aria-hidden="true" loading="lazy"{dw}>' if s.get("drawing") else ""
        html = section(f'<div class="zig {s.get("side", "left")}">{media}<div class="zig-text{" has-drawing" if drw else ""}">{drw}<h2>{esc(s["title"])}</h2>{content}</div></div>', id_=slugify(s.get("title", "")))
    else:
        html = section(content, title=s.get("title"), id_=slugify(s.get("title", "")), cls="section centered-head" if (s.get("spec") or s.get("defs")) and not s.get("media") else "section")
    if s.get("draw"):   # a technical drawing faint behind the section's words
        html = html.replace('<section class="section"', '<section class="section has-draw"', 1).replace('<div class="wrap">', f'<img class="bg-draw" src="{s["draw"]}" alt="" aria-hidden="true" loading="lazy"><div class="wrap">', 1)
    return html

def slugify(t):
    t = re.sub(r"[^a-z0-9]+", "-", clean(t).lower()).strip("-")
    return t or None


def enquiry_block(extra_id="enquiry"):
    E = C.ENQUIRY
    return section(
        f"""<div class="enquiry" id="{extra_id}">
  <h2>{esc(E["h2"])}</h2>
  <p class="lead">{esc(E["p"])}</p>
  {buttons(E["buttons"])}
  <div class="partner"><h3>{esc(E["partner_h"])}</h3><p>{esc(E["partner_p"])}</p></div>
</div>""")


# ------------------------------------------------------------------ page shell
PAGE_CSS = """
.trio { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: clamp(36px, 5vw, 56px) clamp(24px, 3vw, 48px); align-items: start; }   /* three to a row, no boxes (user, 2026-11-06) */
.trio-col { border-top: 1px solid var(--line); padding-top: 22px; display: grid; gap: 12px; align-content: start; }
.trio-col h3 { font-size: clamp(19px, 1.5vw, 22px); font-weight: 400; letter-spacing: -.015em; }
.trio-col > p { color: var(--ink-soft); font-size: 15.5px; line-height: 1.55; }
.trio-col .list { margin: 0; }
.trio-col .list li { font-size: 15.5px; }
.trio-sub { margin-top: 6px; font-size: 14px; font-weight: 500; color: var(--muted); }
.col-pic { margin: 10px 0 0; }
.col-pic img { display: block; width: 100%; height: auto; }
.col-pic.photo img { aspect-ratio: 4 / 3; object-fit: cover; border-radius: 4px; }
.col-pic.cut img { aspect-ratio: 4 / 3; object-fit: contain; }   /* the profile's cut-outs sit free on the page */
@media (max-width: 900px) { .trio { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 600px) { .trio { grid-template-columns: 1fr; } }
.spec-stack { display: grid; gap: 34px; }
.spec-title { margin-bottom: 14px; text-align: center; }
.centered-head .wrap > p { width: min(880px, 100%); margin: 0 auto 24px; color: var(--ink-soft); }   /* a note above a chart lines up with it */
.card .apps { margin-top: 10px; font-size: 14px; color: var(--ink-soft); }
.card ul.list { margin-top: 6px; }
.who { font-size: clamp(18px, 1.6vw, 24px); letter-spacing: -.01em; max-width: 60ch; }
.cta-band { display: grid; gap: 22px; padding: clamp(24px, 6vh, 72px) 0 clamp(16px, 3vh, 32px); justify-items: center; text-align: center; }   /* no box: the user wants no cards anywhere */
.cta-band h2 { max-width: 18ch; font-size: clamp(28px, 3.2vw, 46px); font-weight: 400; line-height: 1.08; letter-spacing: -.03em; text-wrap: balance; }
.cta-band .lead { max-width: 46ch; }
.cta-band .btn-row { justify-content: center; margin-top: 10px; }
.related { display: grid; gap: 18px; }
/* 3D mount points (#hero-3d on two group pages, #globe on contact) are empty until the scenes are mounted:
   hide them and keep the plain hero's full top padding so the breadcrumb clears the header bar. */
.hero-3d:empty, .globe:empty { display: none; }
.hero-3d:empty + .hero.plain, .globe:empty + .hero.plain { padding-top: 170px; }
.hero .wrap .coverage { font-size: clamp(15px, 1.15vw, 17px); color: var(--muted); margin-top: 6px; }
/* catalogue-style line drawings, translucent behind the words (Shibata page) */
.has-draw { position: relative; overflow: hidden; }
.has-draw > .wrap { position: relative; z-index: 1; }
.bg-draw { position: absolute; z-index: 0; right: -3%; top: 50%; width: min(1180px, 92vw); height: auto; transform: translateY(-50%); opacity: .1; pointer-events: none; user-select: none; }   /* lighter so the words read clearly (user, 2026-11-06) */
.hero.has-draw .bg-draw { top: auto; bottom: 4%; transform: none; opacity: .09; }
@media (max-width: 720px) { .bg-draw { right: -20%; width: 150vw; opacity: .08; } }
.pr-hero { min-height: 86vh; }
.pr-hero .media img { filter: none; }
.pr-hero .media::after { background: linear-gradient(180deg, rgba(0,0,0,.05) 30%, rgba(0,0,0,.62)); }
.contact-hero .media::after { background: linear-gradient(90deg, rgba(10,22,16,.78), rgba(10,22,16,.35) 55%, rgba(10,22,16,.1)), linear-gradient(180deg, transparent 50%, rgba(0,0,0,.5)); }
.pr-hero .wrap, .pr-hero .crumbs, .pr-hero .crumbs a, .pr-hero .eyebrow { color: #fff; }
.pr-hero .crumbs, .pr-hero .eyebrow { opacity: .85; }
.pr-hero h1 { color: #fff; font-size: clamp(34px, 4.2vw, 60px); }
.pr-hero .lead { color: rgba(255,255,255,.9); max-width: 58ch; }
.pr-hero .pr-cov { font-size: 15px; color: rgba(255,255,255,.72); }
.pr-photo .media::after { background: linear-gradient(180deg, rgba(15,42,30,.5) 0%, rgba(15,42,30,.58) 45%, rgba(15,42,30,.86) 100%); }   /* a dark HexaHessman-green veil so the words read on any photo */
.pr-logo { position: absolute; z-index: 2; right: var(--gutter); top: clamp(150px, 20vh, 200px); width: auto; height: 54px; max-width: 34vw; object-fit: contain; filter: brightness(0) invert(1); opacity: .92; }   /* in white, so every part reads on the photo */
.pr-logo.mq-shibata { height: 46px; } .pr-logo.mq-manntek { height: 70px; } .pr-logo.mq-straatman { height: 58px; } .pr-logo.mq-raythink { height: 60px; }
@media (max-width: 720px) { .pr-logo { top: 104px; height: 34px; } .pr-logo.mq-manntek { height: 44px; } }
.product-hero { min-height: 74vh; }
.product-hero .media::after { background: linear-gradient(90deg, rgba(10,22,16,.82), rgba(10,22,16,.45) 55%, rgba(10,22,16,.15)), linear-gradient(180deg, transparent 45%, rgba(10,22,16,.55)); }
.product-hero .lead + .lead { margin-top: -6px; }
.pr-intro { display: grid; justify-items: center; text-align: center; gap: 22px; }
.pr-intro .lead { max-width: 58ch; color: var(--ink); }
.pr-intro .coverage { font-size: 15px; color: var(--muted); }
.centered-head .section-head { margin-left: auto; margin-right: auto; text-align: center; justify-items: center; }
.pr-logo { display: block; width: min(340px, 64vw); height: auto; margin: 0 auto 6px; }
.hero.has-logo .wrap { text-align: center; justify-items: center; margin-left: auto; margin-right: auto; }
.hero.has-logo .crumbs { justify-content: center; }
.hero.has-logo .lead, .hero.has-logo .coverage { margin-left: auto; margin-right: auto; }
/* solutions by fuel: four photo tiles in one line; they rise (1st, 3rd) and drop (2nd, 4th) into place when the row scrolls in; a tile opens its drop-down */
.fuel-tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: clamp(10px, 1.6vw, 22px); }
.fuel-tile { position: relative; aspect-ratio: 4 / 3; overflow: hidden; display: grid; place-items: center; align-content: center; gap: 16px; padding: 0; border: 0; background: #0F2A1E; color: #fff; font: inherit; cursor: pointer;
  opacity: 0; transform: translateY(70px); transition: opacity .8s cubic-bezier(.2,.7,.2,1), transform .8s cubic-bezier(.2,.7,.2,1); transition-delay: calc(var(--i) * .12s); }
.fuel-tile:nth-child(even) { transform: translateY(-70px); }
.fuel-row.in .fuel-tile { opacity: 1; transform: none; }
.fuel-tile img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transition: transform .6s cubic-bezier(.2,.7,.2,1); }
.fuel-tile:hover img { transform: scale(1.05); }
.fuel-veil { position: absolute; inset: 0; background: rgba(0,0,0,.45); transition: background .3s; }
.fuel-tile:hover .fuel-veil, .fuel-tile[aria-expanded="true"] .fuel-veil { background: rgba(15,42,30,.6); }
.fuel-label { position: relative; font-size: clamp(20px, 2.3vw, 34px); font-weight: 600; letter-spacing: .04em; text-transform: uppercase; }
.fuel-more { position: relative; padding: 9px 16px; border: 1px solid rgba(255,255,255,.85); border-radius: 4px; font-size: 13px; font-weight: 500; letter-spacing: .02em; }
.fuel-tile[aria-expanded="true"] .fuel-more { background: #fff; color: #0F2A1E; }
.spin-panel { display: grid; grid-template-rows: 0fr; transition: grid-template-rows .55s cubic-bezier(.2,.7,.2,1); }
.spin-panel.open { grid-template-rows: 1fr; }
.spin-panel-in { overflow: hidden; }
.spin-panel-in > div { display: grid; gap: 18px; max-width: 62ch; margin-top: 26px; padding-top: 24px; border-top: 1px solid var(--line); }
.spin-panel-in p { font-size: clamp(17px, 1.35vw, 20px); color: var(--ink); }
@media (prefers-reduced-motion: reduce) { .fuel-tile { opacity: 1; transform: none; transition: none; } }
@media (max-width: 720px) { .fuel-tiles { grid-template-columns: 1fr 1fr; } .fuel-label { font-size: 18px; } }
/* the labelled system diagram: labels pop out one by one (dot, then the leader line draws, then the tag) */
.dg-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.dg { position: relative; margin: 0; min-width: 860px; border-radius: 14px; overflow: hidden; }
.dg img { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.dg svg { position: absolute; inset: 0; width: 100%; height: 100%; }
.dg line { stroke: #fff; stroke-width: 2.2; vector-effect: non-scaling-stroke; stroke-dasharray: 1; stroke-dashoffset: 1; }
.dg circle { fill: #fff; stroke: #0F2A1E; stroke-width: 3; transform-box: fill-box; transform-origin: center; transform: scale(0); }
.dg-tag { position: absolute; transform: translate(-50%, -50%) scale(.85); opacity: 0; padding: 7px 13px; border-radius: 980px; white-space: nowrap;
  background: rgba(255,255,255,.88); -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px); color: #0F2A1E; font-size: clamp(11px, 1.05vw, 15px); font-weight: 500; letter-spacing: -.01em; box-shadow: 0 6px 20px rgba(0,0,0,.18); }
.dg.in circle { transform: scale(1); transition: transform .5s cubic-bezier(.3,1.6,.5,1) calc(var(--i) * .35s); }
.dg.in line { stroke-dashoffset: 0; transition: stroke-dashoffset .6s ease calc(var(--i) * .35s + .15s); }
.dg.in .dg-tag { opacity: 1; transform: translate(-50%, -50%) scale(1); transition: opacity .5s ease calc(var(--i) * .35s + .45s), transform .6s cubic-bezier(.3,1.5,.5,1) calc(var(--i) * .35s + .45s); }
@media (prefers-reduced-motion: reduce) { .dg circle, .dg-tag { transform: translate(0,0); } .dg circle { transform: none; } .dg line { stroke-dashoffset: 0; } .dg-tag { opacity: 1; transform: translate(-50%, -50%); } }
/* photos on the principal pages (Shibata): plain photos, the orange-panel layers, the floating clips */
.zig-photo img, .zig-photo video, .zig-layers { border-radius: 4px; }
.zig-photo video { display: block; width: 100%; height: auto; aspect-ratio: 3 / 4; object-fit: cover; mix-blend-mode: normal; }
.zig-layers { position: relative; overflow: hidden; }
.zig-layers .pl-base { display: block; width: 100%; height: auto; max-height: none; margin: 0; }
.zig-layers .pl { position: absolute; display: block; max-height: none; margin: 0; clip-path: inset(100% 0 0 0); }
.zig-layers.in .pl { clip-path: inset(0 0 0 0); transition: clip-path .9s cubic-bezier(.2,.7,.2,1) calc(.3s + var(--i) * .45s); }
@media (prefers-reduced-motion: reduce) { .zig-layers .pl { clip-path: none; } }
.zig-sub { margin: 26px 0 8px; font-size: 16px; font-weight: 600; letter-spacing: -.01em; }
.zig-text > p + p { margin-top: 14px; }
/* a product with its picture: picture one side, text the other, alternating down the page (as on the principal's own site) */
.zig { display: grid; grid-template-columns: 1fr 1fr; gap: clamp(28px, 5vw, 80px); align-items: center; }
.zig.right .zig-media { order: 2; }
.zig-media { margin: 0; }
.zig-text.has-drawing { position: relative; isolation: isolate; }
.zig-drawing { position: absolute; z-index: -1; left: 50%; top: 50%; width: 130%; max-width: none; height: auto; transform: translate(-50%, -50%); opacity: .1; pointer-events: none; user-select: none; }
@media (max-width: 720px) { .zig-drawing { width: 110%; opacity: .08; } }
.zig-media video, .zig-media img { display: block; width: 100%; height: auto; }
.zig-media[data-spin] { position: relative; aspect-ratio: 1; }
.zig-media canvas, .zig-media .spin-still { position: absolute; inset: 0; width: 100%; height: 100%; mix-blend-mode: multiply; }   /* the frames' off-white studio ground melts into the page */
.zig-media.ready .spin-still { display: none; }
.zig-media img { width: auto; max-width: 100%; max-height: 72vh; margin: 0 auto; }
.zig-text h2 { margin-bottom: 20px; }
.zig-text .spec-stack { margin-top: 18px; }
@media (max-width: 720px) { .zig { grid-template-columns: 1fr; gap: 24px; } .zig.right .zig-media { order: 0; } .zig-media img { max-height: 60vh; } }
.pr-media { margin: clamp(8px, 2vw, 24px) auto 0; }
.pr-media video { display: block; width: 100%; height: auto; aspect-ratio: 16 / 9; border-radius: 12px; background: #fff; object-fit: cover; }
.yt-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: clamp(16px, 2.4vw, 32px); }
@media (max-width: 720px) { .yt-grid { grid-template-columns: 1fr; } }
.yt-frame { position: relative; aspect-ratio: 16 / 9; border-radius: 10px; overflow: hidden; background: rgba(var(--ink-rgb),.06); }
.yt-frame iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
.yt figcaption { margin-top: 10px; font-size: 15px; color: var(--muted); }
.steps { display: grid; gap: 18px; grid-template-columns: repeat(auto-fit, minmax(min(100%, 200px), 1fr)); }
.steps .card .n { font-family: var(--mono); font-size: 12px; letter-spacing: .15em; color: var(--muted); margin-bottom: 10px; display: block; }
@media (max-width: 640px) { .spec th, .spec td { padding: 10px 8px; font-size: 14px; } .spec td:first-child { width: auto; } }
"""


def page(title, description, body, extra_head="", head_tags="", body_scripts="", body_class=""):
    """extra_head: CSS appended to the page <style>; head_tags: raw tags for <head>; body_scripts: raw tags before </body>."""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · HexaHessman</title>
<meta name="description" content="{esc_attr(description)}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300..700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/header.css?v=2611d">
<link rel="stylesheet" href="/assets/site.css?v=2612z">
<style>{PAGE_CSS}{extra_head}</style>
{head_tags}</head>
<body{f' class="{body_class}"' if body_class else ""}>
<div id="site-header"></div>
<main>
{body}
</main>
<div id="site-footer"></div>
<script src="/assets/site-header.js?v=2612e" defer></script>
<script src="/assets/deco-lines.js?v=2" defer></script>
<script src="/assets/words.js?v=3" defer></script>
<script src="/assets/site-footer.js" defer></script>
{body_scripts}</body>
</html>
"""


def back_btn(up):
    """the floating Back button on product and principal pages (user, 2026-11-06); `up` is where it goes with no history"""
    return f'<script src="/assets/back-btn.js?v=1" data-up="{up}" defer></script>\n'


def write(relpath, html):
    full = os.path.join(ROOT, relpath.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)
    WRITTEN.append(full)


# ------------------------------------------------------------------ pages
def build_commodities_hub():
    H = C.COMMODITIES_HUB
    # the long scroll: every product in every group, over the 3D scenes (cscroll.js fills it)
    import json as _json
    intro = _json.dumps({"h2": H["h1"], "p": H["lead"]}, ensure_ascii=False).replace('"', '&quot;')
    # arrival from the entrance zoom: the logo draws on, then the partner logo wall (placeholders until real logos arrive)
    logo = ('<svg class="arrive-mark" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true">'
            '<rect x="2.5" y="3" width="13" height="42"/><rect x="5.5" y="6" width="7" height="36" stroke-width=".8"/>'
            '<rect x="32.5" y="3" width="13" height="42"/><rect x="35.5" y="6" width="7" height="36" stroke-width=".8"/>'
            '<path d="M24 9.5 L38.5 24 L24 38.5 L9.5 24 Z"/><path d="M24 14 L34 24 L24 34 L14 24 Z" stroke-width=".8"/></svg>')
    # partner logos in a hairline grid with a cross at each corner (after pestimesh.vercel.app's client grid); placeholders for now
    cells = "".join(f'<div class="pcell" data-i="{i}"><i class="x tl"></i><i class="x tr"></i><i class="x bl"></i><i class="x br"></i><span class="ph"><i></i><b>Partner logo</b></span></div>' for i in range(12))   # two rows (user, 2026-11-06)
    # hero: the bulk port at dusk, edge to edge, with the headline pushed to the left over the sky (user, 2026-11-06)
    body = [f'''<section class="arrive com-arrive" id="partners" aria-label="Partners">
  <div class="com-hero"><video class="com-hero-vid" muted playsinline preload="auto" poster="/assets/commodities/crane-loop.jpg" aria-label="A harbour crane loading jumbo bags onto a ship at dusk"><source media="(max-width: 720px)" src="/assets/commodities/crane-loop-m.mp4" type="video/mp4"><source src="/assets/commodities/crane-loop.mp4" type="video/mp4"></video>
  <div class="arrive-top com-top">
  <p class="eyebrow arrive-eyebrow">Commodities Supply</p>
  <h1 class="arrive-title">Trusted by producers and buyers across nine markets</h1></div></div>
<script>
(() => {{   // 3 s still, the crane swings to its left end, 3 s still there, swings back right, and round again (client, 2026-11-07)
  const v = document.querySelector('.com-hero-vid'); if (!v || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const HOLD = 3000, RATE = 0.75, LEFT = 3.05;   // LEFT: the moment in the clip the crane reaches its left end (it rests there 2.9-3.2 s)
  let timer = 0, held = false;
  const start = () => {{ v.playbackRate = RATE; const p = v.play(); if (p && p.catch) p.catch(() => {{}}); watch(); }};
  const hold = () => {{ clearTimeout(timer); timer = setTimeout(start, HOLD); }};
  const watch = () => {{   // stop on the left end once per round
    if (v.paused) return;
    if (!held && v.currentTime >= LEFT) {{ held = true; v.pause(); hold(); return; }}
    requestAnimationFrame(watch);
  }};
  v.addEventListener('ended', () => {{ v.pause(); v.currentTime = 0; held = false; hold(); }});
  v.addEventListener('ratechange', () => {{ if (v.playbackRate !== RATE) v.playbackRate = RATE; }});
  hold();
}})();
</script>
  <div class="pwall"><div class="pgrid">{cells}</div></div>
</section>''', f'<section id="cscroll" class="cscroll" data-intro="{intro}"></section>']

    # (Product groups and How we supply removed, user 2026-11-06)

    body.append(section(f"""<div class="cta-band">
  <h2>{esc(H["cta_h"])}</h2><p class="lead">{esc(H["cta_p"])}</p>{buttons(H["cta_buttons"])}</div>""", id_="cta"))

    write("/commodities/index.html", page("Commodities Supply", meta_desc(H["lead"]), "\n".join(body), body_scripts='<script src="https://cdn.jsdelivr.net/npm/lenis@1/dist/lenis.min.js"></script>\n<script src="/assets/cscroll.js?v=2611p" defer></script>\n<script src="/assets/cs-marks.js?v=15" defer></script>\n<script src="/assets/arrive.js?v=2612a" defer></script>\n'))


def build_group(g):
    body = []
    if g.get("hero3d"):
        body.append('<section id="hero-3d" class="hero-3d"></section>')
    body.append(hero_plain([("Home", "/"), ("Commodities Supply", "/commodities/"), (g["name"], None)],
                           "Commodities Supply", g["name"], [g["lead"]]))
    body.append(section(f'<p class="who">{esc(g["who"])}</p>', eyebrow="Who it’s for", id_="who"))
    cards = [card(name, desc, href=f"{group_url(g['slug'])}{slug}/", more="View product →") for slug, name, desc in g["products"]]
    body.append(section(grid(cards, "c3"), title="Products", id_="products"))
    body.append(section(f'<div class="cta-band"><p class="lead">{esc(C.GROUP_CTA)}</p>{buttons(C.GROUP_CTA_BUTTONS)}</div>', id_="cta"))
    # hero3d-embed.js mounts a sticky scroll-driven scene in #hero-3d and lifts the breadcrumb/eyebrow/h1
    # out of the .hero.plain that directly follows it.
    scripts = '<script src="/assets/hero3d-embed.js" defer></script>\n' if g.get("hero3d") else ""
    write(f"/commodities/{g['slug']}/index.html", page(g["name"], meta_desc(g["lead"]), "\n".join(body), body_scripts=scripts))


def col_img(src, alt=""):
    """a picture at the top of a column: cut-outs (png/webp from the profile) sit free on the page, photos fill a frame"""
    if not src:
        return ""
    kind = "cut" if src.split("?")[0].endswith((".png", ".webp")) else "photo"
    return f'<figure class="col-pic {kind}"><img src="{src}" alt="{esc_attr(alt)}" loading="lazy" decoding="async"></figure>'


def product_sections(p):
    """Product pages, shorter (user, 2026-11-06): forms / grades three across, every short list section (features,
    applications, packaging, industries, terms…) side by side three to a row, and the spec charts full width."""
    secs = [x for x in p["sections"] if x.get("title") != "Distribution"]
    first, cols, rest = [], [], []
    for x in secs:
        if x.get("defs") and not x.get("spec") and not x.get("paras"):
            first.append(x)                                   # forms / grades → three across, with pictures
        elif x.get("spec") or x.get("defs") or x.get("cards") or x.get("note"):
            rest.append(x)                                     # charts and anything wide stay full width
        else:
            cols.append(x)                                     # short sections → one row of columns
    out = []
    for x in first:
        imgs = x.get("imgs", {})
        items = "".join(f'<div class="trio-col"><h3>{esc(t)}</h3><p>{esc(d)}</p>{col_img(imgs.get(t), t)}</div>' for t, d in x["defs"] if not is_placeholder(d))   # pictures under the words, so the headings line up
        out.append(section(f'<div class="trio">{items}</div>', title=x.get("title"), id_=slugify(x.get("title", ""))))
    if cols:
        items = []
        for x in cols:
            inner = "".join(f"<p>{esc(t)}</p>" for t in x.get("paras", []) if not is_placeholder(t))
            if x.get("items"):
                inner += ul_list(x["items"])
            for h, its in x.get("sublists", []):
                inner += f'<h4 class="trio-sub">{esc(h)}</h4>{ul_list(its)}'
            if inner.strip():
                items.append(f'<div class="trio-col" id="{slugify(x.get("title", "")) or ""}"><h3>{esc(x.get("title", ""))}</h3>{inner}{col_img(x.get("img"), x.get("title", ""))}</div>')
        out.append(section(f'<div class="trio">{"".join(items)}</div>', id_="details"))
    for x in rest:
        out.append(render_section(x))
    return out


def build_product(p):
    g = GROUP_BY_SLUG[p["group"]]
    # a photo hero like the old site's product pages: the product's photo (from the 2026 profile where it has one), the
    # name and its intro over it (user, 2026-11-06)
    hero_img = f"/assets/products/hero/{p['slug']}.jpg" if os.path.exists(os.path.join(ROOT, f"assets/products/hero/{p['slug']}.jpg")) else f"/assets/products/{p['slug']}.jpg"
    intro = "".join(f'<p class="lead">{esc(x)}</p>' for x in p["hero"] if not is_placeholder(x))
    # the Distribution line sits under the intro instead of being a section of its own (user, 2026-11-06)
    dist = " ".join(clean(x) for d in p["sections"] if d.get("title") == "Distribution" for x in d.get("paras", []) if not is_placeholder(x))
    dist = f'<p class="pr-cov">{esc(dist)}</p>' if dist else ""
    body = [f"""<section class="hero pr-hero product-hero"><div class="media"><img src="{hero_img}" alt="{esc_attr(short_name(p["slug"]))}" fetchpriority="high"></div>
<div class="wrap"><p class="eyebrow">{esc(g["name"])}</p><h1>{esc(p["title"])}</h1>{intro}{dist}</div></section>"""]
    body += product_sections(p)
    # related products
    rel = []
    for name in p.get("related", []):
        slug = PRODUCT_NAME_TO_SLUG.get(name)
        if slug and slug in PRODUCT_BY_SLUG:
            rel.append(card(short_name(slug), descriptor(slug), href=product_url(slug), more="View product →"))
    if rel:
        body.append(section(grid(rel, "c4"), title="Related products", id_="related"))
    body.append(enquiry_block())
    write(f"{product_url(p['slug'])}index.html", page(short_name(p["slug"]), meta_desc(p["hero"][-1] if len(p["hero"]) > 1 and len(clean(p["hero"][0])) < 70 else p["hero"][0]), "\n".join(body), body_scripts=back_btn(group_url(g["slug"]))))


ARRIVE_LOGO = ('<svg class="arrive-mark" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true">'
               '<rect x="2.5" y="3" width="13" height="42"/><rect x="5.5" y="6" width="7" height="36" stroke-width=".8"/>'
               '<rect x="32.5" y="3" width="13" height="42"/><rect x="35.5" y="6" width="7" height="36" stroke-width=".8"/>'
               '<path d="M24 9.5 L38.5 24 L24 38.5 L9.5 24 Z"/><path d="M24 14 L34 24 L24 34 L14 24 Z" stroke-width=".8"/></svg>')


def build_engineering_hub():
    """Terminal-style hub: arrival (logo draws, headline) -> sliding carousel of the principals' logos ->
    a centred statement that lights up word by word and then fades away word by word as you scroll ->
    one stop per principal (logo, brief, key products, photo, Read more) -> components, services, lifecycle, CTA.
    Motion lives in /assets/eng.js; styles in site.css under "engineering hub"."""
    H = C.ENGINEERING_HUB
    PR = {p["slug"]: p for p in C.PRINCIPALS}
    names = {slug: name for slug, name, _ in H["principals"]}
    # carousel: the four logos repeated so one copy always fills the widest screen; eng.js doesn't need to clone
    one = "".join(f'<li class="mq-cell"><a href="/engineering/{slug}/" tabindex="-1"><img src="/assets/engineering/logo-{slug}.svg?v=3" alt="{esc_attr(names[slug])}" class="mq-logo mq-{slug}"></a></li>'
                  for slug, _, _ in H["principals"])
    track = f'<ul class="mq-set">{one * 2}</ul><ul class="mq-set" aria-hidden="true">{one * 2}</ul>'
    # hero: the port photo edge to edge, the headline lower left (as Commodities; user, 2026-11-06), then the line drawing
    body = [f'''<section class="arrive eng-arrive com-arrive" aria-label="Engineering Solutions">
  <div class="com-hero"><video class="eng-hero-vid" muted loop playsinline preload="auto" poster="/assets/engineering/hero-sts-1920.jpg" aria-label="Two ships moored side by side, the sea moving between them and the pneumatic fenders bobbing, cargo hoses crossing the gap"></video>
<script>
(() => {{   // the ship-to-ship loop: only the sea and the fenders move (client, 2026-11-07); a sharper file on big screens, a light one on phones
  const v = document.querySelector('.eng-hero-vid'); if (!v) return;
  const small = matchMedia('(max-width: 720px)').matches, hd = !small && screen.width * (devicePixelRatio || 1) >= 2400;
  if (small) v.poster = '/assets/engineering/hero-sts-m.jpg';
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  v.src = '/assets/engineering/sts-loop' + (small ? '-m' : hd ? '-hd' : '') + '.mp4';
  const go = () => {{ const p = v.play(); if (p && p.catch) p.catch(() => {{}}); }}; go(); v.addEventListener('canplay', go, {{ once: true }});
}})();
</script>
  <div class="arrive-top com-top">
  <p class="eyebrow arrive-eyebrow">Engineering Solutions</p>
  <h1 class="arrive-title">{esc(H["h1"])}</h1></div></div>
  <div class="mq" aria-label="Principals we represent"><p class="mq-label">Principals we represent</p><div class="mq-view"><div class="mq-track">{track}</div></div></div>
</section>''']
    body.append(section(grid([card(h, d) for h, d in H["services"]], "c3"), title="Services", id_="services", cls="section centered-head"))   # moved up, in place of the long statement (user, 2026-11-05)

    stops = []
    n = len(H["principals"])
    for i, (slug, name, short) in enumerate(H["principals"]):
        pr = PR[slug]
        tags = " · ".join(esc(t) for t in H["principal_tags"].get(slug, []))   # a plain line, not chips (user: no circles)
        cov = f'<p class="ep-cov">{esc(pr["coverage"])}</p>' if pr.get("coverage") else ""
        stops.append(f'''<article class="ep {'right' if i % 2 else 'left'}" id="{slug}">
  <a class="ep-photo cs-photo" href="/engineering/{slug}/" data-reveal="photo" tabindex="-1" aria-hidden="true"><img src="/assets/engineering/{slug}.jpg?v=1" alt="" loading="lazy" decoding="async" width="1200" height="900"><svg class="ep-run" aria-hidden="true"><rect pathLength="100"/></svg></a>
  <div class="ep-copy">
    <img class="ep-logo mq-{slug}" src="/assets/engineering/logo-{slug}.svg?v=3" alt="{esc_attr(name)}" data-reveal="fade">
    <h2 class="ep-short" data-reveal="fade">{esc(short)}</h2>
    <p class="ep-brief" data-reveal="fade">{esc(pr["hero"][0])}</p>
    <p class="ep-tags" data-reveal="fade">{tags}</p>
    <div class="ep-foot" data-reveal="fade">{cov}<a class="pill solid" href="/engineering/{slug}/">Read more about {esc(name)} →</a></div>
  </div>
</article>''')
    body.append(f'<section class="eprin" id="principals" aria-label="Principals we represent">{"".join(stops)}</section>')

    body.append(section(f'<div class="cta-band"><h2>{esc(H["cta_h"])}</h2>{buttons(H["cta_buttons"])}</div>', id_="cta"))
    # (the cone fender line drawing under the hero was tried and removed, user 2026-11-06; eng-draw.html is kept, unused)
    scripts = ('<script src="https://cdn.jsdelivr.net/npm/lenis@1/dist/lenis.min.js"></script>\n'
               '<script src="/assets/arrive.js?v=2612a" defer></script>\n<script src="/assets/eng.js?v=2611a" defer></script>\n')
    write("/engineering/index.html", page("Engineering Solutions", meta_desc(H["lead"]), "\n".join(body), body_scripts=scripts, body_class="eng"))


def build_principal(pr):
    extra = f'<p class="coverage">{esc(pr["coverage"])}</p>' if pr.get("coverage") else ""
    hero = hero_plain([("Home", "/"), ("Engineering Solutions", "/engineering/"), (pr["name"], None)],
                      "Engineering Solutions", pr["h1"], pr["hero"], extra=extra)
    if pr.get("hero_img"):   # a photo hero (title + subheader on the picture), then the logo and the intro under it
        # title and subheader on the photo; the intro and coverage are the subheader (user, 2026-11-06: no breadcrumbs, no logo block)
        cov = f'<p class="pr-cov">{esc(pr["coverage"])}</p>' if pr.get("coverage") else ""
        logo = f'<img class="pr-logo mq-{pr["slug"]}" src="{pr["logo"]}" alt="{esc_attr(pr["name"])}">' if pr.get("logo") else ""   # the principal's logo, top right of its photo (user, 2026-11-06)
        hero = f"""<section class="hero pr-hero pr-photo"><div class="media"><img src="{pr["hero_img"]}" alt="" fetchpriority="high"></div>
<div class="wrap"><h1>{esc(pr["h1"])}</h1><p class="lead">{esc(pr["hero"][0])}</p>{cov}</div>{logo}</section>"""
    if pr.get("hero_draw"):
        hero = hero.replace('<section class="hero plain">', '<section class="hero plain has-draw">', 1).replace('<div class="wrap">', f'<img class="bg-draw" src="{pr["hero_draw"]}" alt="" aria-hidden="true"><div class="wrap">', 1)
    body = [hero]
    if pr.get("hero_video"):   # a silent looping product clip (path without extension: .mp4 + .jpg poster)
        v = pr["hero_video"]
        body.append(f'<div class="wrap pr-media"><video autoplay muted loop playsinline preload="metadata" poster="{v}.jpg" aria-label="{esc_attr(pr["name"])} product, turning"><source src="{v}.mp4" type="video/mp4"></video></div>')
    for s in pr["sections"]:
        body.append(render_section(s))
    cta = ""
    if pr.get("cta_h"):
        cta += f"<h2>{esc(pr['cta_h'])}</h2>"
    if pr.get("cta_p"):
        cta += f'<p class="lead">{esc(pr["cta_p"])}</p>'
    cta += buttons(pr["cta_buttons"])
    body.append(section(f'<div class="cta-band">{cta}</div>', id_="cta"))
    scripts = '<script src="/assets/spin-row.js?v=6" defer></script>' if any(s.get("fuels") or s.get("media") or s.get("diagram") for s in pr["sections"]) else ""
    write(f"/engineering/{pr['slug']}/index.html", page(pr["name"], meta_desc(pr["hero"][0]), "\n".join(body), body_scripts=scripts + back_btn("/engineering/"), body_class="eng"))


def avatar_svg(name):
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    return (f'<svg class="avatar" viewBox="0 0 96 96" role="img" aria-label="{esc_attr(name)}">'
            f'<circle cx="48" cy="48" r="46" fill="none" stroke="currentColor" stroke-width="1.2" opacity=".5"/>'
            f'<text x="48" y="56" text-anchor="middle" font-family="Geist, Arial, sans-serif" font-size="26" fill="currentColor">{initials}</text></svg>')


def photo(slug, name):
    return f'<img class="avatar photo" src="/assets/team/{slug}.jpg" alt="{esc_attr(name)}" loading="lazy" width="360" height="360">'


def team_card(name, role, entity, slug=None):
    pic = photo(slug, name) if slug else avatar_svg(name)
    return f'<div class="card team-card">{pic}<h3>{esc(name)}</h3><p>{esc(role)}</p><p class="apps">{esc(entity)}</p></div>'


# a bulk carrier seen from above, bow pointing down the lane, in the same cream line style as the scroll scenes:
# hull and deck edge, accommodation and bridge wings at the stern, five hatch covers with their ribs, deck cranes,
# forecastle with windlasses; the wake (two V lines and foam) trails behind the stern
def _ship_svg():
    hatches = "".join(f'<rect class="s-f" x="30" y="{92 + i * 50}" width="60" height="42" rx="2"/><line x1="60" y1="{92 + i * 50}" x2="60" y2="{134 + i * 50}"/>'
                      + "".join(f'<line class="s-t" x1="30" y1="{92 + i * 50 + k * 10.5}" x2="90" y2="{92 + i * 50 + k * 10.5}"/>' for k in (1, 2, 3)) for i in range(5))
    cranes = "".join(f'<circle class="s-f" cx="{x}" cy="{y}" r="5"/><line x1="{x}" y1="{y}" x2="{x + dx}" y2="{y + 30}"/>' for x, y, dx in ((24, 138, 10), (96, 188, -10), (24, 238, 10), (96, 288, -10)))
    return ('<svg class="vy-svg" viewBox="-60 -170 240 600" aria-hidden="true">'
            '<g class="vy-wake"><path d="M30,14 L-40,-160"/><path d="M90,14 L160,-160"/><path class="w2" d="M44,14 L4,-120"/><path class="w2" d="M76,14 L116,-120"/>'
            '<ellipse cx="60" cy="-10" rx="22" ry="34"/><ellipse class="w2" cx="60" cy="-60" rx="16" ry="40"/></g>'
            '<path class="s-f" d="M20,14 L100,14 Q108,14 108,24 L108,300 Q108,362 60,414 Q12,362 12,300 L12,24 Q12,14 20,14 Z"/>'
            '<path class="s-t" d="M24,22 L96,22 L100,30 L100,300 Q100,352 60,398 Q20,352 20,300 L20,30 Z"/>'
            '<rect class="s-f" x="28" y="24" width="64" height="44" rx="3"/><rect class="s-f" x="8" y="44" width="104" height="10" rx="2"/>'
            '<circle class="s-f" cx="60" cy="34" r="7"/><line x1="40" y1="60" x2="80" y2="60"/>'
            + hatches + cranes +
            '<path class="s-t" d="M24,350 Q60,336 96,350"/><circle class="s-f" cx="46" cy="364" r="5"/><circle class="s-f" cx="74" cy="364" r="5"/>'
            '<line class="s-t" x1="60" y1="372" x2="60" y2="396"/></svg>')
SHIP_SVG = _ship_svg()


ABOUT_CSS = """
/* About hero: the shophouse street drawn in line, stroke by stroke, left to right and street up */
.story-grid { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: clamp(28px, 5vw, 80px); align-items: start; }   /* text straight under the title, no gap (user, 2026-11-06) */
.story-text { display: grid; gap: 14px; }
.story-logo { aspect-ratio: 1; width: 100%; max-width: 460px; justify-self: center; margin-top: clamp(-90px, -6vw, -40px); opacity: 0; transition: opacity .8s ease; }
.story-logo.in { opacity: 1; }
.story-logo iframe { width: 100%; height: 100%; border: 0; display: block; background: transparent; }
@media (max-width: 820px) { .story-grid { grid-template-columns: 1fr; } .story-logo { max-width: 360px; } }
.about-hero2 { position: relative; width: 100%; aspect-ratio: 16 / 9; max-height: 100svh; min-height: 560px; overflow: hidden; background: #0F2A1E; }   /* full 16:9, the drawing fills it, words over the top (user, 2026-11-06) */
.about-hero2 .wrap { position: absolute; z-index: 2; left: var(--gutter); bottom: clamp(32px, 7%, 80px); width: min(640px, 100% - 2 * var(--gutter)); display: grid; gap: 12px; justify-items: start; text-align: left; }   /* bottom left (user) */
.about-hero2 .crumbs { justify-content: flex-start; }
.about-hero2::before { content: ""; position: absolute; inset: 0; z-index: 1; pointer-events: none; background: radial-gradient(ellipse 70% 62% at 0% 100%, rgba(15,42,30,.96) 30%, rgba(15,42,30,.7) 58%, transparent 80%); }
.about-street { position: absolute; inset: 0; z-index: 0; display: flex; align-items: flex-end; justify-content: center; }
.shop-draw { position: relative; width: 100%; }   /* the whole street, edge to edge, standing on the bottom of the frame */
.shop-draw img { display: block; width: 100%; height: auto;   /* fades in from left to right behind a wide soft edge, no pen line (user, 2026-11-06) */
  -webkit-mask-image: linear-gradient(90deg, #000 0%, #000 30%, transparent 70%); mask-image: linear-gradient(90deg, #000 0%, #000 30%, transparent 70%);
  -webkit-mask-size: 300% 100%; mask-size: 300% 100%; -webkit-mask-repeat: no-repeat; mask-repeat: no-repeat;
  -webkit-mask-position: 100% 0; mask-position: 100% 0; opacity: 0; }
.about-hero2.go .shop-draw img { animation: shopSweep 2.8s cubic-bezier(.4,.1,.25,1) forwards, shopFade 1.4s ease forwards; }   /* starts once the drawing has loaded */
/* the words come in after the drawing (client, 2026-11-07) */
.about-hero2 .wrap > * { opacity: 0; transform: translateY(18px); transition: opacity .9s ease, transform 1s cubic-bezier(.2,.7,.2,1); }
.about-hero2.words .wrap > * { opacity: 1; transform: none; }
.about-hero2.words .wrap > :nth-child(2) { transition-delay: .1s; } .about-hero2.words .wrap > :nth-child(3) { transition-delay: .2s; } .about-hero2.words .wrap > :nth-child(4) { transition-delay: .35s; }
@keyframes shopSweep { to { -webkit-mask-position: 0 0; mask-position: 0 0; } }
@keyframes shopFade { to { opacity: 1; } }
@media (prefers-reduced-motion: reduce) { .shop-draw img { animation: none; opacity: 1; -webkit-mask-image: none; mask-image: none; } }
.shop-svg { display: block; width: 100%; height: auto; }
.shop-svg path { fill: none; stroke: #EEE3C7; stroke-width: 1.3; stroke-linejoin: round; stroke-linecap: round; vector-effect: non-scaling-stroke;
  stroke-dasharray: 1; stroke-dashoffset: 1; animation: shopDraw 1.4s cubic-bezier(.4,.1,.3,1) forwards; animation-delay: var(--d); }
.shop-svg path.t { stroke-width: .8; stroke-opacity: .7; animation-duration: 1s; }
.shop-traced path { fill: #EEE3C7; fill-opacity: 0; stroke-width: .9; animation: shopDraw 1.3s cubic-bezier(.4,.1,.3,1) forwards, shopFill .8s ease forwards; animation-delay: var(--d), calc(var(--d) + .7s); }   /* the client's drawing, traced: outline draws, then the line fills in */
@keyframes shopFill { to { fill-opacity: 1; stroke-opacity: 0; } }
.shop-svg text { fill: #EEE3C7; font: 600 15px var(--sans); letter-spacing: 2px; opacity: 0; animation: shopFade 1s ease forwards; animation-delay: var(--d); }
@keyframes shopDraw { to { stroke-dashoffset: 0; } }
@keyframes shopFade { to { opacity: 1; } }
@media (prefers-reduced-motion: reduce) { .shop-svg path { animation: none; stroke-dashoffset: 0; } .shop-traced path { fill-opacity: 1; stroke-opacity: 0; } .shop-svg text { animation: none; opacity: 1; } }
@media (max-width: 720px) { .about-hero2 { aspect-ratio: auto; height: auto; min-height: 0; padding-top: 300px; } .about-street { position: relative; } }
.about-hero { position: relative; height: 210svh; }   /* the hero holds for about a screen while the logo turns */
.about-pin { position: sticky; top: 0; height: 100svh; min-height: 0; align-items: flex-end; padding-top: 140px; }
.about-logo { position: absolute; inset: 0; z-index: 0; pointer-events: none; }
.about-logo iframe { width: 100%; height: 100%; border: 0; display: block; background: transparent; opacity: 0; animation: aboutLogoIn .9s ease .2s forwards; }
@keyframes aboutLogoIn { to { opacity: 1; } }
.about-pin .wrap { max-width: 600px; }
.about-pin h1 { text-shadow: 0 2px 28px rgba(15,42,30,.85); }
.about-cue { position: absolute; right: var(--gutter); bottom: clamp(48px, 7vw, 96px); z-index: 1; display: flex; align-items: center; gap: 12px; font-family: var(--sans); font-size: 14px; letter-spacing: -.01em; text-transform: none; color: var(--muted); }
.about-cue i { width: 1px; height: 44px; background: linear-gradient(var(--ink-soft), transparent); animation: aboutCue 2.2s ease-in-out infinite; transform-origin: top; }
@keyframes aboutCue { 0% { transform: scaleY(0); } 50% { transform: scaleY(1); } 100% { transform: scaleY(1); opacity: 0; } }
@media (max-width: 720px) { .about-pin { padding-bottom: 72px; } .about-cue { display: none; } }
@media (prefers-reduced-motion: reduce) { .about-logo iframe { animation: none; opacity: 1; } .about-cue i { animation: none; } }
/* ---- the voyage timeline: a white section with green words (user, 2026-11-05) ---- */
.vy { --vy-fg: #0F2A1E; --vy-fg-rgb: 15,42,30; background: #FFFFFF; color: var(--vy-fg);   /* pure white, the same as the ship clip's ground */
  --paper: #FFFFFF; --ink: #0F2A1E; --ink-soft: rgba(15,42,30,.78); --muted: rgba(15,42,30,.58); --line: rgba(15,42,30,.14); --line-strong: rgba(15,42,30,.3); }
.vy-head { text-align: center; margin-left: auto; margin-right: auto; justify-items: center; }
.vy-wrap { position: relative; width: min(var(--max), 100% - 2 * var(--gutter)); margin: 0 auto; padding: 40px 0 120px; }
.vy-lane { position: absolute; left: 50%; top: 0; bottom: 0; width: 240px; transform: translateX(-50%); pointer-events: none; }
.vy-water { position: absolute; inset: 0; overflow: hidden;   /* a drawn river: wobbly banks, ripples that drift past the ship */
  background: url("/assets/about/river-bank.svg") left top / 34px 320px repeat-y, url("/assets/about/river-bank.svg") right top / 34px 320px repeat-y; 
  -webkit-mask-image: linear-gradient(90deg, transparent, #000 30%, #000 70%, transparent); mask-image: linear-gradient(90deg, transparent, #000 30%, #000 70%, transparent); }
.vy-water::before { content: ""; position: absolute; left: 22px; right: 22px; top: 0; height: calc(100% + 320px); background: url("/assets/about/river-ripples.svg") center top / 240px 320px repeat; animation: vyFlow 16s linear infinite; will-change: transform; }
@keyframes vyFlow { to { transform: translate3d(0, -320px, 0); } }   /* GPU only: smooth, no repaint */
.vy-route { display: none; }
.vy-done { position: absolute; left: 50%; top: 0; width: 1.5px; margin-left: -.75px; height: var(--done, 0px); background: linear-gradient(rgba(var(--vy-fg-rgb),.15), rgba(var(--vy-fg-rgb),.85)); }
.vy-lane { z-index: 2; }   /* the ship passes over the year diamonds */
.vy-ship { position: absolute; left: 50%; top: 0; width: 64px; margin-left: -32px; transform: translateY(var(--y, 0px)); }   /* straight down, no lean; smaller (user) */
.vy-hull { position: relative; display: block; width: 100%; height: auto; }
.vy-shipvid { display: block; width: 100%; height: auto; mix-blend-mode: multiply; }   /* the clip's white ground drops out on the white section; only the ink shows */
/* engraved water parting around the hull (bow wave below, wash above): two copies drift back along the hull and
   cross-fade, so the strokes seem to flow past the ship without anything jumping (user's drawing, 2026-11-06) */
.vy-water2 { position: absolute; left: -107.9%; top: -38%; width: 309.7%; height: 152.9%; background: url("/assets/about/ship-water.webp") center / 100% 100% no-repeat;
  opacity: .55; pointer-events: none; transform-origin: 51% 63%; animation: vyWaterA 3.2s ease-in-out infinite; }
.vy-water2.w-b { animation-name: vyWaterB; }
@keyframes vyWaterA { 0% { opacity: .55; transform: translateY(0) scale(1, 1); } 50% { opacity: .2; transform: translateY(-2.2%) scale(1.04, 1.02); } 100% { opacity: .55; transform: translateY(0) scale(1, 1); } }
@keyframes vyWaterB { 0% { opacity: .15; transform: translateY(-2.2%) scale(1.04, 1.02); } 50% { opacity: .5; transform: translateY(0) scale(1, 1); } 100% { opacity: .15; transform: translateY(-2.2%) scale(1.04, 1.02); } }
@media (prefers-reduced-motion: reduce) { .vy-water2 { animation: none; } .vy-water2.w-b { display: none; } }
.vy-wakeline { position: absolute; left: 50%; bottom: 97%; width: 260%; height: 150%; transform: translateX(-50%); overflow: visible; }
.vy-wakeline path { fill: none; stroke: var(--vy-fg); stroke-width: 1.1; stroke-linecap: round; vector-effect: non-scaling-stroke; stroke-opacity: .5; stroke-dasharray: 10 9; animation: vyWake2 1.4s linear infinite; }
.vy-wakeline .w2 { stroke-opacity: .32; stroke-dasharray: 6 10; animation-duration: 1.9s; }
.vy-wakeline .w3 { stroke-opacity: .25; stroke-dasharray: 3 7; animation-duration: 1.1s; }
@keyframes vyWake2 { to { stroke-dashoffset: -38; } }
.vy-svg { display: block; width: 100%; height: auto; overflow: visible; filter: drop-shadow(0 0 10px rgba(var(--vy-fg-rgb),.18)); }
.vy-svg path, .vy-svg rect, .vy-svg circle, .vy-svg line, .vy-svg ellipse { fill: none; stroke: var(--vy-fg); stroke-width: 1.3; stroke-linejoin: round; vector-effect: non-scaling-stroke; }
.vy-svg .s-f { fill: rgba(var(--vy-fg-rgb),.07); }
.vy-svg .s-t { stroke-opacity: .55; stroke-width: .9; }
.vy-wake path, .vy-wake ellipse { stroke-opacity: .35; stroke-dasharray: 6 8; animation: vyWake 1.6s linear infinite; }
.vy-wake .w2 { stroke-opacity: .22; animation-duration: 2.3s; }
@keyframes vyWake { to { stroke-dashoffset: -28; } }
.vy-stop { position: relative; display: grid; grid-template-columns: 1fr 240px 1fr; align-items: center; min-height: 72vh; }
.vy-stop .vy-photo { grid-column: 1; grid-row: 1; justify-self: end; }
.vy-stop .vy-text { grid-column: 3; grid-row: 1; }
.vy-stop.r .vy-photo { grid-column: 3; justify-self: start; }
.vy-stop.r .vy-text { grid-column: 1; text-align: right; justify-self: end; }
.vy-photo { position: relative; margin: 0; width: min(420px, 100%); aspect-ratio: 4 / 3; }
.vy-photo img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; border-radius: 6px; filter: saturate(.85); }
.vy-frame { position: absolute; inset: -12px; width: calc(100% + 24px); height: calc(100% + 24px); overflow: visible; pointer-events: none; }
.vy-frame rect { x: 1px; y: 1px; width: calc(100% - 2px); height: calc(100% - 2px); rx: 10px; fill: none; }
.vy-line { stroke: rgba(var(--vy-fg-rgb),.28); stroke-width: 1.2; }
.vy-run { stroke: var(--vy-fg); stroke-width: 2; stroke-linecap: round; stroke-dasharray: 9 91; filter: drop-shadow(0 0 5px rgba(var(--vy-fg-rgb),.9)); animation: vyRun 7s linear infinite; }
.vy-stop:nth-child(even) .vy-run { animation-delay: -3.5s; }
@keyframes vyRun { to { stroke-dashoffset: -100; } }
.vy-gem { position: absolute; right: -18px; bottom: -18px; width: 11px; height: 11px; border: 1.2px solid rgba(var(--vy-fg-rgb),.7); transform: rotate(45deg); background: var(--paper); }
.vy-stop.r .vy-gem { right: auto; left: -18px; }
.vy-text { max-width: 400px; display: grid; gap: 10px; }
.vy-year { font-size: clamp(32px, 3.6vw, 52px); font-weight: 400; letter-spacing: -.04em; line-height: 1; color: var(--ink); }
.vy-text h3 { font-size: clamp(19px, 1.6vw, 23px); font-weight: 500; }
.vy-text p:last-child { color: var(--ink-soft); font-size: 16px; line-height: 1.55; }
.vy-node { position: absolute; left: 50%; top: 50%; width: 13px; height: 13px; margin: -6.5px 0 0 -6.5px; border: 1.3px solid rgba(var(--vy-fg-rgb),.45); background: var(--paper); transform: rotate(45deg) scale(.8); transition: transform .5s, background .5s, border-color .5s, box-shadow .5s; }
.vy-stop.on .vy-node { background: var(--vy-fg); border-color: var(--vy-fg); transform: rotate(45deg) scale(1); box-shadow: 0 0 14px rgba(var(--vy-fg-rgb),.7); }
/* each side slides in from its own edge, every time the year comes on screen (voyage.js toggles .seen) */
.vy-stop .vy-photo, .vy-stop .vy-text { opacity: 0; transition: opacity .9s cubic-bezier(.2,.7,.2,1), transform 1s cubic-bezier(.2,.7,.2,1); }
.vy-stop.l .vy-photo, .vy-stop.r .vy-text { transform: translateX(-90px); }
.vy-stop.l .vy-text, .vy-stop.r .vy-photo { transform: translateX(90px); }
.vy-stop .vy-text { transition-delay: .12s; }
.vy-stop.seen .vy-photo, .vy-stop.seen .vy-text { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) { .vy-stop .vy-photo, .vy-stop .vy-text { opacity: 1; transform: none; } .vy-water, .vy-run, .vy-wakeline path, .vy-water::before { animation: none; } }
@media (max-width: 820px) {
  .vy-lane { left: 34px; width: 68px; }
  .vy-ship { width: 40px; margin-left: -20px; }
  .vy-stop .vy-photo, .vy-stop .vy-text { transform: translateX(50px) !important; }
  .vy-stop.seen .vy-photo, .vy-stop.seen .vy-text { transform: none !important; }
  .vy-stop, .vy-stop.r { grid-template-columns: 68px 1fr; min-height: 0; padding: 40px 0; gap: 22px 0; }
  .vy-stop .vy-photo, .vy-stop.r .vy-photo { grid-column: 2; grid-row: 1; justify-self: stretch; width: auto; margin: 12px 12px 0 12px; }
  .vy-stop .vy-text, .vy-stop.r .vy-text { grid-column: 2; grid-row: 2; text-align: left; justify-self: start; }
  .vy-stop.r .vy-gem { left: auto; right: -18px; }
  .vy-node { left: 34px; top: 52px; }
}
.timeline { display: grid; gap: 0; }
.timeline .row { display: grid; grid-template-columns: 120px 1fr; gap: 20px; padding: 18px 0; border-top: 1px solid var(--line); }
.timeline .row:last-child { border-bottom: 1px solid var(--line); }
.timeline .year { font-family: var(--mono); font-size: 20px; letter-spacing: -.02em; }
.markets { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
.markets span { font-family: var(--sans); font-size: 14px; letter-spacing: -.01em; text-transform: none; padding: 8px 12px; border: 1px solid var(--line); border-radius: 999px; color: var(--ink-soft); }
/* ---- the team lookbook: one line of people in the middle of the stage, the front one sharp, the rest a step back
   each (smaller, fainter, more blurred); a press walks the line forward. A part of the globe sits at the right edge. ---- */
.tl { padding-bottom: 0; }   /* dark green (tried white 2026-11-06; user wanted it back) */
.tl + section, .tl ~ .section { }
/* the header, set like the Commodities hub's: centred, no eyebrow, a large title over text that lights up word by word (client, 2026-11-07) */
.tl-head { display: grid; gap: clamp(28px, 4vh, 48px); justify-items: center; text-align: center; padding: clamp(20px, 6vh, 80px) var(--g) 0; margin-bottom: clamp(16px, 3vh, 36px); }
.tl-title { max-width: 18ch; font-size: clamp(30px, 3.4vw, 50px); font-weight: 400; line-height: 1.06; letter-spacing: -.03em; }
.tl-title em { font-style: normal; color: inherit; }
.tl-fill { max-width: 32ch; font-size: clamp(17px, 1.35vw, 21px); line-height: 1.35; letter-spacing: -.01em; color: var(--ink); }
.tl-title .w, .tl-fill .w { opacity: .16; transition: opacity .25s linear; }
@media (prefers-reduced-motion: reduce) { .tl-title .w, .tl-fill .w { opacity: 1 !important; } }
.tl-wrap { position: relative; }
.tl-stage { position: relative; height: 82svh; min-height: 560px; max-height: 860px; overflow: hidden; --fw: min(50vh, 34vw); }   /* smaller (user, 2026-11-05: people, globe and name too big) */
.tl-stage::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 30%; z-index: 2; pointer-events: none; background: linear-gradient(transparent, rgba(15,42,30,.55) 60%, #0F2A1E); }
.tl-queue { position: absolute; inset: 0; z-index: 2; cursor: pointer; touch-action: pan-y; }
.tl-cut { position: absolute; left: 50%; bottom: 0;
  -webkit-mask-image: linear-gradient(to top, transparent 0%, rgba(0,0,0,.6) 16%, #000 36%); mask-image: linear-gradient(to top, transparent 0%, rgba(0,0,0,.6) 16%, #000 36%);   /* each figure dissolves at the bottom, whatever height its row stands at */ width: var(--fw); height: auto; transform-origin: 50% 100%; user-select: none; -webkit-user-drag: none;
  transform: translate3d(calc(-50% + var(--x, 0%)), var(--y, 0%), 0) scale(var(--s, 1));   /* --x/--y/--s/--b/--o: set per figure by team-lookbook.js */
  filter: blur(var(--b, 0px)); opacity: var(--o, 1);
  transition: transform .9s cubic-bezier(.2,.7,.2,1), filter .9s, opacity .9s, visibility 0s; will-change: transform, filter, opacity; }
.tl-cut.far { visibility: hidden; transition: transform .9s cubic-bezier(.2,.7,.2,1), filter .9s, opacity .9s, visibility 0s linear .9s; }
.tl-cut.out { transform: translate3d(-50%, 10%, 0) scale(1.5); filter: blur(16px); opacity: 0; }   /* walks off past the camera */
/* the globe: big and low in the middle, its centre just below the stage, so its upper curve rises behind the
   people's shoulders; the office in focus lands high on the right of the disc, clear of the heads */
.tl-globe { position: absolute; z-index: 1; left: 50%; top: 4%; height: 170%; aspect-ratio: 1; transform: translateX(-50%); pointer-events: none; }
.tl-globe canvas { width: 100%; height: 100%; display: block; }
.tl-globe-label { position: absolute; left: 0; top: 0; margin: -30px 0 0 10px; padding: 4px 8px; border: 1px solid var(--line-strong); border-radius: 4px; background: rgba(15,42,30,.75);
  font: 500 14px/1.3 var(--sans); letter-spacing: -.01em; text-transform: none; color: var(--ink-soft); white-space: nowrap; opacity: 0; transition: opacity .4s; }
.tl-foot { display: contents; }
.tl-info { position: absolute; z-index: 3; left: var(--gutter); top: clamp(70px, 12vh, 130px); max-width: min(560px, 48vw); display: grid; gap: 10px; pointer-events: none; }
.tl-count { font: 400 12px/1 var(--mono); letter-spacing: .18em; color: var(--muted); }
.tl-name { font-size: clamp(26px, 2.6vw, 38px); font-weight: 400; line-height: .98; letter-spacing: -.04em; text-shadow: 0 2px 28px rgba(15,42,30,.9); }
.tl-role { font-size: clamp(16px, 1.5vw, 22px); color: var(--ink); }
.tl-where { font-size: 15px; line-height: 1.5; color: var(--muted); }
.tl-desc { margin-top: 8px; max-width: 40ch; font-size: clamp(15px, 1.15vw, 17px); line-height: 1.5; color: var(--ink-soft); }
.tl-info.swap .tl-name, .tl-info.swap .tl-role, .tl-info.swap .tl-where, .tl-info.swap .tl-desc { animation: tlSwap .7s cubic-bezier(.2,.7,.2,1) both; }
.tl-info.swap .tl-role { animation-delay: .06s; } .tl-info.swap .tl-where { animation-delay: .12s; } .tl-info.swap .tl-desc { animation-delay: .18s; }
@keyframes tlSwap { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
.tl-ctrl { position: absolute; z-index: 3; right: var(--gutter); bottom: clamp(36px, 6vh, 72px); display: flex; gap: 10px; align-items: center; }
.tl-hint { font: 500 14px/1.3 var(--sans); letter-spacing: -.01em; text-transform: none; color: var(--muted); margin-right: 8px; }
.tl-ctrl button { width: 54px; height: 54px; border-radius: 50%; border: 1px solid var(--line-strong); background: rgba(15,42,30,.55); color: var(--ink); cursor: pointer; display: grid; place-items: center;
  -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); transition: background .25s, color .25s, transform .25s; }
.tl-ctrl button:hover { background: var(--ink); color: var(--paper); }
.tl-ctrl button:active { transform: scale(.94); }
.tl-ctrl svg { width: 20px; height: 20px; }
/* everyone at once, under the line (for people who would rather not step through); a card jumps the line to that person */
.tl-all { padding: clamp(56px, 9vh, 110px) var(--gutter) clamp(56px, 9vh, 110px); }
/* the grid of everyone on white, green words (user, 2026-11-06) */
.tl-all .eyebrow { max-width: 1040px; margin: 0 auto 26px; }
.tl-grid li { opacity: 0; transform: translateY(28px); transition: opacity .7s cubic-bezier(.2,.7,.2,1), transform .7s cubic-bezier(.2,.7,.2,1); transition-delay: calc(var(--c, 0) * .14s); }
.tl-grid li.in { opacity: 1; transform: none; }   /* each row arrives left to right (team-lookbook.js) */
@media (prefers-reduced-motion: reduce) { .tl-grid li { opacity: 1; transform: none; } }
.tl-grid { list-style: none; display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px 24px; max-width: 1040px; margin: 0 auto; }   /* three across, in the order of the customer's team sheet */
.tl-grid button { width: 100%; display: grid; gap: 4px; justify-items: center; text-align: center; background: none; border: 0; color: var(--ink); font: inherit; cursor: pointer; padding: 0; }
.tl-grid-pic { display: block; width: 100%; aspect-ratio: 900 / 781; overflow: hidden; margin-bottom: 12px; border-radius: 8px; background: radial-gradient(ellipse at 50% 100%, rgba(238,227,199,.12), rgba(238,227,199,.03) 70%); transition: background .3s; }
.tl-grid-pic img { width: 100%; height: 100%; object-fit: cover; display: block; filter: saturate(0); transition: transform .5s cubic-bezier(.2,.7,.2,1); }
.tl-grid button:hover .tl-grid-pic { border-color: var(--line-strong); background: radial-gradient(ellipse at 50% 100%, rgba(238,227,199,.2), rgba(238,227,199,.05) 70%); }
.tl-grid button:hover img { transform: scale(1.04); }
.tl-grid b { font-weight: 500; font-size: 16px; letter-spacing: -.01em; }
.tl-grid span:not(.tl-grid-pic) { font-size: 13px; color: var(--ink-soft); }
.tl-grid small { font-size: 13px; line-height: 1.5; color: var(--muted); }
@media (max-width: 900px) {   /* phones: the figure fills the width, the write-up and buttons sit below the stage */
  .tl-stage { --fw: min(84vw, 60vh); height: calc(var(--fw) * .868 + 16px); min-height: 0; max-height: none; }
  .tl-stage::after { height: 22%; }
  .tl-globe { left: 108%; top: 5%; height: 170%; }
  .tl-foot { display: grid; gap: 20px; padding: 22px 20px 0; }
  .tl-info, .tl-ctrl { position: static; max-width: none; }
  .tl-globe-label { margin: 14px 0 0 0; translate: -50% 0; }   /* the label hangs under the pin, clear of the head and the edge */
  .tl-name { font-size: clamp(26px, 7.5vw, 36px); }
  .tl-hint { display: none; } .tl-ctrl button { width: 50px; height: 50px; }
  .tl-all { padding: 48px 20px 0; }
  .tl-grid { gap: 20px 10px; }
  .tl-grid b { font-size: 13px; } .tl-grid span:not(.tl-grid-pic) { font-size: 11px; } .tl-grid small { font-size: 11px; }
}
@media (prefers-reduced-motion: reduce) { .tl-cut, .tl-cut.far { transition: none; } .tl-info.swap * { animation: none; } }
/* the closing call: plain and centred, no card */
.cta-band.plain { border: 0; background: none; border-radius: 0; padding: clamp(24px, 6vh, 72px) 0 clamp(16px, 3vh, 32px); justify-items: center; text-align: center; gap: 22px; }
.cta-band.plain h2 { max-width: 18ch; font-size: clamp(28px, 3.2vw, 46px); font-weight: 400; line-height: 1.08; letter-spacing: -.03em; text-wrap: balance; }
.cta-band.plain .lead { max-width: 46ch; }
.cta-band.plain .btn-row { justify-content: center; margin-top: 10px; }

/* Our team, Terminal-style (client, 2026-11-06): white ground, hairline cells with corner crosses, photos fill the cells */
.tg { background: #FCFCFC; --paper: #FCFCFC; --paper-2: #FCFCFC; --paper-rgb: 252,252,252;
  --ink: #0F2A1E; --ink-soft: rgba(15,42,30,.8); --ink-rgb: 15,42,30; --muted: rgba(15,42,30,.58); --line: rgba(15,42,30,.13); --line-strong: rgba(15,42,30,.3);
  --tg-hi: #0F2A1E; color: var(--ink); overflow: hidden; padding-bottom: clamp(64px, 10vh, 120px); }
.tg-head { text-align: center; justify-items: center; margin-left: auto; margin-right: auto; }
.tg-grid { list-style: none; margin: 0 auto; padding: 0; width: min(960px, calc(100% - 2 * var(--gutter))); display: grid; grid-template-columns: repeat(3, 1fr);   /* 3 across, row for row as the client's team sheet (client, 2026-11-07) */
  border-left: 1px solid var(--line); position: relative; }
.tg-grid::before, .tg-grid::after { content: ""; position: absolute; left: -50vw; right: -50vw; height: 1px; top: 0; background: linear-gradient(90deg, transparent, var(--line) 20%, var(--line) 80%, transparent); }
.tg-grid::after { top: auto; bottom: 0; }
.tg-cell { position: relative; border-right: 1px solid var(--line); border-bottom: 1px solid var(--line); transition: box-shadow .35s ease; }
.tg-cell::after { content: ""; position: absolute; inset: -1px; pointer-events: none; border: 1.5px solid var(--tg-hi); opacity: 0; transition: opacity .3s ease; z-index: 3;
  box-shadow: 0 0 10px rgba(15,42,30,.45), inset 0 0 8px rgba(15,42,30,.25);
  -webkit-mask-image: linear-gradient(180deg, transparent 0%, #000 45%); mask-image: linear-gradient(180deg, transparent 0%, #000 45%); }   /* the lines light up, fading out toward the top, as on Terminal */
.tg-cell:hover::after { opacity: 1; }
.tg-empty:hover::after { opacity: 0; }
/* the little crosses at the corners; on hover they flicker and turn green */
.tg-x { position: absolute; width: 13px; height: 13px; z-index: 4; pointer-events: none; }
.tg-x::before, .tg-x::after { content: ""; position: absolute; background: rgba(15,42,30,.45); transition: background .3s; }
.tg-x::before { left: 6px; top: 0; width: 1px; height: 13px; } .tg-x::after { top: 6px; left: 0; height: 1px; width: 13px; }
.tg-x.tl { left: -7px; top: -7px; } .tg-x.tr { right: -7px; top: -7px; } .tg-x.bl { left: -7px; bottom: -7px; } .tg-x.br { right: -7px; bottom: -7px; }
.tg-cell:hover .tg-x { animation: tgFlicker .5s steps(1) 1; }
.tg-cell:hover .tg-x::before, .tg-cell:hover .tg-x::after { background: var(--tg-hi); }
@keyframes tgFlicker { 0% { opacity: 1; } 15% { opacity: .1; } 30% { opacity: 1; } 45% { opacity: .2; } 60%, 100% { opacity: 1; } }
/* the photo: a square that fills the cell, the person standing in it; it slides up into the cell when its row arrives */
.tg-pic { padding: 8px; }
.tg-slide { aspect-ratio: 1 / 1; overflow: hidden; position: relative; border-radius: 2px;
  background: radial-gradient(ellipse 85% 75% at 50% 80%, #12261b, #0a1610 62%, #050b08); }   /* almost black, a dark-dark green (user, 2026-11-06) */
.tg-slide img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 50% 100%; display: block;
  transform: translateY(101%); filter: saturate(.15) contrast(1.02); transition: transform .9s cubic-bezier(.645,.045,.355,1), filter .5s ease, scale .6s cubic-bezier(.2,.7,.2,1);
  transition-delay: calc(var(--c, 0) * .12s), 0s, 0s; }
.tg-cell.in .tg-slide img { transform: none; }
.tg-cell:hover .tg-slide img { filter: none; scale: 1.04; }
.tg-meta { display: grid; gap: 3px; justify-items: center; text-align: center; padding: 16px 10px 20px; border-top: 1px solid var(--line); position: relative; transition: background .35s ease, box-shadow .35s ease, border-color .35s ease; }
.tg-cell:hover .tg-meta { border-top-color: var(--tg-hi); background: radial-gradient(ellipse 70% 90% at 50% 50%, rgba(15,42,30,.04), rgba(15,42,30,.11)); box-shadow: inset 0 0 26px rgba(15,42,30,.22); }   /* the name cell fills with a soft green glow (Terminal's hover, our green) */
.tg-meta b { font-weight: 500; font-size: 17px; letter-spacing: -.015em; color: var(--ink); transition: color .3s; }
.tg-meta span { font-size: 13.5px; color: var(--muted); }
.tg-meta small { font-size: 13px; color: var(--muted); opacity: .8; }
.tg-cell:hover .tg-meta b { color: #0F2A1E; }
@media (max-width: 900px) {
  .tg-grid { grid-template-columns: repeat(2, 1fr); width: calc(100% - 32px); }
  .tg-empty { display: none; }
  .tg-pic { padding: 5px; } .tg-meta { padding: 14px 8px 16px; } .tg-meta b { font-size: 15px; } .tg-meta span { font-size: 12.5px; } .tg-meta small { font-size: 11.5px; }
}
@media (prefers-reduced-motion: reduce) { .tg-slide img { transform: none; transition: none; } .tg-cell:hover .tg-x { animation: none; } }
"""


def build_about():
    A = C.ABOUT
    # hero: the 3D drawing of the mark (logo.html?embed) draws itself on behind the headline
    # hero: the HexaHessman shophouse on its street, redrawn as line art (tools/drawings/shophouses.py), drawing itself in
    # one image of the client's drawing, fading in from left to right (the traced 861-path SVG drew too slowly)
    shop = '<div class="shop-draw" role="img" aria-label="The HexaHessman shophouse on a Singapore street, in line"><img src="/assets/about-shophouses.jpg" alt="" width="2000" height="826" fetchpriority="high"></div>'
    body = [f"""<section class="about-hero2">
  <div class="wrap">
    {crumbs([("Home", "/"), ("About", None)])}
    <p class="eyebrow">{esc(A["eyebrow"])}</p>
    <h1>{esc(A["h1"])}</h1>
    <p class="lead">{esc(A["lead"])}</p>
  </div>
  <div class="about-street">{shop}</div>
<script>
(() => {{   // the drawing sweeps in once it has loaded, then the words follow
  const h = document.currentScript.closest('.about-hero2'), img = h.querySelector('.shop-draw img');
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) {{ h.classList.add('go', 'words'); return; }}
  let done = false;
  const go = () => {{ if (done) return; done = true; h.classList.add('go'); setTimeout(() => h.classList.add('words'), 1600); }};
  if (img.complete && img.naturalWidth) go(); else {{ img.addEventListener('load', go, {{ once: true }}); img.addEventListener('error', go, {{ once: true }}); setTimeout(go, 3000); }}
}})();
</script>
</section>"""]
    # Our story, with the 3D drawn HexaHessman mark beside it: it draws itself on when the section comes into view and
    # turns a little as you scroll (logo.html?embed; the src is set on arrival so the drawing starts then)
    story = "".join(f"<p>{esc(p)}</p>" for p in A["story"])

    # the voyage timeline: a sea lane down the middle with a top-view ship that sails it as you scroll (assets/voyage.js),
    # the years alternating either side, each with a framed photo that has a light running round its outline
    stops = "".join(f'''<article class="vy-stop {'r' if i % 2 else 'l'}">
  <figure class="vy-photo"><img src="{img}" alt="" loading="lazy" decoding="async"><svg class="vy-frame" aria-hidden="true"><rect class="vy-line" pathLength="100"/><rect class="vy-run" pathLength="100"/></svg></figure>
  <div class="vy-text"><p class="vy-year">{esc(y)}</p><h3>{esc(h)}</h3><p>{esc(p)}</p></div>
</article>''' for i, (y, h, p, img) in enumerate(A["timeline"]))
    voyage = (f'''<section class="section vy" id="timeline" aria-label="{esc_attr(A["timeline_h"])}">
  <div class="wrap section-head vy-head"><h2>{esc(A["timeline_h"])}</h2><p class="lead">{esc(A["timeline_lead"])}</p></div>
  <div class="vy-wrap">
    <div class="vy-lane" aria-hidden="true">
      <div class="vy-ship"><video class="vy-shipvid" autoplay muted loop playsinline preload="auto" poster="/assets/about/ship-water.jpg?v=2" aria-hidden="true"><source src="/assets/about/ship-water.mp4?v=2" type="video/mp4"></video></div></div>
    {stops}
  </div>
</section>''')
    specialise = section(grid([card(h, p, href=href, more="Learn more →") for h, p, href in A["specialise"]], "c3"), title="What we specialise in", id_="specialise")
    # the team lookbook: everyone in one line (team-lookbook.js), a part of the globe at the side (team-globe.js)
    people = [dict(name=n, role=r, entity=e, slug=slug, office=o, city=A["office_pins"][o][0], country=A["office_pins"][o][1],
                   lat=A["office_pins"][o][2], lon=A["office_pins"][o][3], blurb=b) for n, r, e, slug, o, b in A["team"]]
    arrow = lambda d: f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="{"M4 12h16M13 5l7 7-7 7" if d > 0 else "M20 12H4M11 5l-7 7 7 7"}"/></svg>'
    fallback = "".join(f'<li><b>{esc(n)}</b>: {esc(r)}, {esc(e)}</li>' for n, r, e, _, _, _ in A["team"])
    team_title = re.sub(r"\[(.+?)\]", r"<em>\1</em>", _html.escape(A["team_h"], quote=False))
    body.append(f'''<section class="section tl" id="team" data-people="{_html.escape(json.dumps(people, ensure_ascii=False), quote=True)}">
  <div class="tl-head"><h2 class="tl-title">{team_title}</h2><p class="tl-fill">{esc(A["team_lead"])}</p></div>
  <div class="tl-wrap">
    <div class="tl-stage">
      <div class="tl-globe" aria-hidden="true"><canvas></canvas><div class="tl-globe-label"></div></div>
      <div class="tl-queue"></div>
    </div>
    <div class="tl-foot">
      <div class="tl-info" aria-live="polite"><h3 class="tl-name"></h3><p class="tl-role"></p><p class="tl-where"></p><p class="tl-desc"></p></div>
      <div class="tl-ctrl"><span class="tl-hint">Next person</span><button class="tl-prev" type="button" aria-label="Previous person">{arrow(-1)}</button><button class="tl-next" type="button" aria-label="Next person">{arrow(1)}</button></div>
    </div>
  </div>
  <noscript><div class="wrap"><ul>{fallback}</ul></div></noscript>
<script>
(() => {{   // the header set like the Commodities one: the title and the text light up word by word as you scroll (client, 2026-11-07)
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const fills = [...document.querySelectorAll('.tl-title, .tl-fill')].map(p => {{
    const words = p.textContent.trim().split(/\\s+/); p.textContent = '';
    const spans = words.map((w, i) => {{ const s = document.createElement('span'); s.className = 'w'; s.textContent = w; p.appendChild(s); if (i < words.length - 1) p.appendChild(document.createTextNode(' ')); return s; }});
    return {{ p, spans, last: -1 }};
  }});
  const tick = () => {{ const vh = innerHeight;
    for (const f of fills) {{ const b = f.p.getBoundingClientRect(); if (b.bottom < -50 || b.top > vh + 50) continue;
      const t = Math.min(1, Math.max(0, (vh * 0.92 - b.top) / (vh * (innerWidth <= 900 ? 0.3 : 0.45) + b.height * 0.5)));
      const n = f.spans.length, soft = 4, lit = t * (n + soft), q = Math.round(lit * 20);
      if (q === f.last) continue; f.last = q;
      f.spans.forEach((s, i) => {{ s.style.opacity = (0.16 + 0.84 * Math.min(1, Math.max(0, (lit - i) / soft))).toFixed(3); }});
    }}
    requestAnimationFrame(tick); }};
  requestAnimationFrame(tick);
}})();
</script>
</section>''')
    story_sec = section(f'''<div class="story-grid"><div class="story-text">{story}</div>
  <div class="story-logo" aria-hidden="true"><iframe data-src="/logo.html?embed&story&v=9" title="" tabindex="-1"></iframe></div></div>
<script>
(() => {{
  const box = document.querySelector('.story-logo'), f = box && box.querySelector('iframe'); if (!f) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  new IntersectionObserver(([e], io) => {{ if (e.isIntersecting) {{ f.src = f.dataset.src; box.classList.add('in'); io.disconnect(); }} }}, {{ threshold: 0.35 }}).observe(box);
  if (reduce) return;
  const sec = box.closest('section');
  const send = () => {{ const r = sec.getBoundingClientRect(); const p = (innerHeight - r.top) / (innerHeight + r.height); if (f.contentWindow && f.src) f.contentWindow.postMessage({{ type: 'logo-scroll', p: (p - 0.5) * 0.35 }}, '*'); }};
  addEventListener('scroll', send, {{ passive: true }}); f.addEventListener('load', send);
}})();
</script>''', title="Our story", id_="story")
    # Our team: everyone in a white Terminal-style grid (terminal-industries.com/about "Our Leaders"): hairline cells with
    # corner crosses, square photos that slide up into their cells, the cell lights up green on hover (client, 2026-11-06)
    cross = lambda pos: f'<i class="tg-x {pos}" aria-hidden="true"></i>'
    cells = "".join(f'''<li class="tg-cell">{cross("tl")}{cross("tr")}{cross("bl")}{cross("br")}
  <div class="tg-pic"><div class="tg-slide"><img src="/assets/team/cut/{slug}.webp?v=2" alt="{esc_attr(n)}" loading="lazy" decoding="async" width="900" height="781"></div></div>
  <div class="tg-meta"><b>{esc(n)}</b><span>{esc(r)}</span><small>{esc(e)}</small></div></li>''' for n, r, e, slug, _, _ in A["team"])
    our_team = f'''<section class="section tg" id="our-team">
  <div class="wrap section-head tg-head"><p class="eyebrow">Our team</p><h2>The people behind every delivery</h2></div>
  <ul class="tg-grid">{cells}{'<li class="tg-cell tg-empty" aria-hidden="true"></li>' * ((-len(A["team"])) % 3)}</ul>
<script>
(() => {{   // each photo slides up into its cell as its row comes on screen, left to right along the row
  const cells = [...document.querySelectorAll('.tg-cell')], g = document.querySelector('.tg-grid');
  const cols = () => getComputedStyle(g).gridTemplateColumns.split(' ').length;
  const io = new IntersectionObserver(es => es.forEach(e => {{ if (!e.isIntersecting) return;
    e.target.style.setProperty('--c', cells.indexOf(e.target) % cols()); e.target.classList.add('in'); io.unobserve(e.target); }}), {{ threshold: 0.25 }});
  cells.forEach(c => io.observe(c));
}})();
</script>
</section>'''
    # order (client, 2026-11-06): Seamless solutions across borders (the lookbook), Our voyage, Our story, What we specialise in, Our team
    body += [voyage, story_sec, specialise, our_team]
    # the closing call: no card, centred, about working with the people above
    body.append(section(f'<div class="cta-band plain"><p class="eyebrow">{esc(A["cta_eyebrow"])}</p><h2>{esc(A["cta_h"])}</h2><p class="lead">{esc(A["cta_p"])}</p>{buttons(A["cta_buttons"])}</div>', id_="cta"))
    head_tags = ('<script type="importmap">{ "imports": { "three": "/assets/vendor/three.module.js?v=160", '
                 '"three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/" } }</script>\n')
    scripts = '<script src="/assets/team-lookbook.js?v=12" defer></script>\n<script src="/assets/voyage.js?v=8" defer></script>\n<script type="module" src="/assets/team-globe.js?v=15"></script>\n'
    write("/about/index.html", page("About", meta_desc(A["story"][0]), "\n".join(body), extra_head=ABOUT_CSS, head_tags=head_tags, body_scripts=scripts))


CONTACT_CSS = """
/* Drop us a line: white section, the boxes and fields stay green (client, 2026-11-06) */
#quote { background: #FCFCFC; --paper: #FCFCFC; --paper-2: #FCFCFC; --paper-rgb: 252,252,252;
  --ink: #0F2A1E; --ink-soft: rgba(15,42,30,.8); --ink-rgb: 15,42,30; --muted: rgba(15,42,30,.6); --line: rgba(15,42,30,.14); --line-strong: rgba(15,42,30,.3); color: var(--ink); }
#quote .contact-aside {
  --paper: #0F2A1E; --paper-2: #0F2A1E; --paper-rgb: 15,42,30;
  --ink: #eee3c7; --ink-soft: #d2c6aa; --ink-rgb: 238,227,199; --muted: rgba(238,227,199,.62); --line: rgba(238,227,199,.16); --line-strong: rgba(238,227,199,.32); }
#quote .contact-aside { background: #0F2A1E; color: var(--ink); border-color: #0F2A1E; }
/* the fields: light grey fills with green type, so they sit easily on the white (user, 2026-11-06) */
#quote .form input, #quote .form select, #quote .form textarea { background-color: #EEF0EE; color: #0F2A1E; border-color: #E2E5E2; }
#quote .form input::placeholder, #quote .form textarea::placeholder { color: rgba(15,42,30,.45); }
#quote .form input:focus, #quote .form select:focus, #quote .form textarea:focus { background-color: #FCFCFC; border-color: #0F2A1E; box-shadow: 0 0 0 3px rgba(15,42,30,.10); }
#quote .form input:-webkit-autofill { -webkit-text-fill-color: #0F2A1E; -webkit-box-shadow: 0 0 0 40px #EEF0EE inset; }
#quote .form .help.error { color: #b5472a; }
#quote .form input.invalid { border-color: #c8603f; }
/* the enquiry form beside its box: labels above, quiet filled fields, one clear button (user: "like a normal contact us form") */
.contact-grid { display: grid; grid-template-columns: minmax(260px, 360px) 1fr; gap: clamp(28px, 4vw, 64px); align-items: start; }
.contact-aside { position: sticky; top: 110px; display: grid; gap: 22px; padding: clamp(24px, 2.6vw, 34px); border: 1px solid var(--line-strong); border-radius: 16px; background: rgba(var(--ink-rgb), .035); }
.contact-aside .ca-item { display: grid; gap: 6px; padding-top: 18px; border-top: 1px solid var(--line); }
.contact-aside h3 { font-size: 18px; font-weight: 500; }
.contact-aside p { font-size: 15px; line-height: 1.55; color: var(--ink-soft); }
.contact-aside .ca-mail { display: grid; gap: 14px; padding-top: 20px; border-top: 1px solid var(--line); }
.contact-aside .ca-mail .pill { justify-self: start; font-size: 14.5px; }
.contact-aside .ca-wa { justify-self: start; margin-top: 8px; font-size: 14.5px; }
.form { display: grid; gap: 20px; }
.form .two { display: grid; gap: 20px; grid-template-columns: 1fr 1fr; }
.form label { display: grid; gap: 8px; font-family: var(--sans); font-size: 14px; font-weight: 500; letter-spacing: -.005em; text-transform: none; color: var(--ink); }
.form input, .form select, .form textarea { width: 100%; height: 50px; padding: 0 16px; border-radius: 10px; border: 1px solid var(--line-strong); background: rgba(var(--ink-rgb), .05); color: var(--ink); font: 400 16px/1.4 var(--sans); transition: border-color .2s, background .2s; -webkit-appearance: none; appearance: none; }
.form select { background-image: linear-gradient(45deg, transparent 50%, currentColor 50%), linear-gradient(135deg, currentColor 50%, transparent 50%); background-position: calc(100% - 22px) 22px, calc(100% - 17px) 22px; background-size: 5px 5px; background-repeat: no-repeat; padding-right: 40px; }
.form input::placeholder, .form textarea::placeholder { color: var(--muted); }
.form input:focus, .form select:focus, .form textarea:focus { outline: none; border-color: var(--ink); background: rgba(var(--ink-rgb), .08); }
.form select option { color: #111; }
.form textarea { height: auto; min-height: 170px; padding: 14px 16px; resize: vertical; }
.form input[type=file] { height: auto; padding: 12px 14px; }
.form .help { font-size: 13px; font-weight: 400; color: var(--muted); text-transform: none; letter-spacing: 0; font-family: var(--sans); }
.form .btn-row .pill { min-width: 200px; }
.form .help-row { margin-top: -10px; }
.form .two { align-items: end; }
@media (max-width: 900px) { .contact-grid { grid-template-columns: 1fr; } .contact-aside { position: static; order: 2; } .form .two { grid-template-columns: 1fr; } }
.form .help.error { color: #f0b49a; }
.form input.invalid { border-color: #f0b49a; }
.contact-card h3 { margin-bottom: 6px; }
.contact-person { display: flex; gap: 14px; align-items: center; margin-top: 12px; }
.contact-person .avatar.photo { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; flex: none; background: #fff; border: 1px solid var(--line); }
.contact-card .role { color: var(--muted); font-size: 14px; }
.contact-card a { display: inline-block; margin-top: 12px; text-decoration: none; font-family: var(--mono); font-size: 13px; }
.office .country { font-family: var(--sans); font-size: 14px; letter-spacing: -.01em; text-transform: none; color: var(--muted); margin-bottom: 10px; display: block; }
.hours .row { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; padding: 16px 0; border-top: 1px solid var(--line); }
.hours .row:last-child { border-bottom: 1px solid var(--line); }
"""

CONTACT_JS = """
<script>
(() => {
  // Deep links from product/principal pages (#quote, #datasheet, #sample, #service) pre-select the enquiry type.
  const h = location.hash.replace('#', '');
  const sel = document.getElementById('enquiring');
  if (!sel) return;
  if (h === 'service') sel.value = 'Engineering Solutions';
  else if (h === 'datasheet' || h === 'sample') sel.value = 'Commodities Supply';
  const msg = document.getElementById('message');
  const hints = { datasheet: 'Please send the technical datasheet / SDS for: ', sample: 'Please arrange a sample of: ', service: 'Servicing / maintenance request for: ' };
  if (msg && hints[h] && !msg.value) msg.value = hints[h];
})();
(() => {
  // Company email only: reject free / personal mailbox providers (any country domain, e.g. yahoo.co.id, hotmail.co.uk).
  const form = document.querySelector('form.form'), email = document.getElementById('email'), help = document.getElementById('email-help');
  if (!form || !email) return;
  const FREE = 'gmail|googlemail|yahoo|ymail|rocketmail|hotmail|outlook|live|msn|windowslive|icloud|me|mac|aol|aim|proton|protonmail|pm|tutanota|tuta|gmx|mail|email|inbox|yandex|zohomail|fastmail|hey|web|libero|seznam|qq|163|126|yeah|sina|sohu|aliyun|foxmail|naver|daum|hanmail|nate|rediffmail|mailinator|guerrillamail|temp-mail|10minutemail';
  const TLD = 'com|net|org|co|me|de|fr|it|es|nl|be|ch|at|se|no|dk|fi|pl|cz|ru|ua|cn|jp|kr|in|id|sg|my|th|ph|vn|hk|tw|tr|uk|us|ca|au|nz|br|mx|ar|za|ie|ae|sa|pk|bd|lk|eg|ng';
  const freeRe = new RegExp('^(' + FREE + ')(\\\\.(' + TLD + '))+$', 'i');
  const tip = help.textContent;
  function check() {
    const v = email.value.trim(), domain = v.includes('@') ? v.split('@').pop().toLowerCase() : '';
    let err = '';
    if (!v) err = 'Please enter your company email.';
    else if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(v)) err = 'Please enter a valid email address.';
    else if (freeRe.test(domain)) err = 'Please use your company email address. ' + domain + ' is a personal email provider.';
    email.setCustomValidity(err);
    email.classList.toggle('invalid', !!err && v !== '');
    help.textContent = err && v ? err : tip; help.classList.toggle('error', !!err && v !== '');
    return !err;
  }
  email.addEventListener('blur', check);
  email.addEventListener('input', () => { if (email.classList.contains('invalid')) check(); });
  form.addEventListener('submit', (e) => {
    const ok = check();
    if (!ok || !form.checkValidity()) { e.preventDefault(); if (!ok) { email.focus(); help.classList.add('error'); } else form.reportValidity(); }
  });
})();
</script>"""


def build_contact():
    K = C.CONTACT_PAGE
    body = []
    body.append(f"""<section class="hero pr-hero contact-hero"><div class="media"><img src="/assets/contact-office.jpg" alt="The HexaHessman office" fetchpriority="high"></div>
<div class="wrap">{crumbs([("Home", "/"), ("Contact", None)])}<p class="eyebrow">{esc(K["eyebrow"])}</p><h1>{esc(K["h1"])}</h1><p class="lead">{esc(K["lead"])}</p></div></section>""")   # their office photo (from hexahessman.com's about page)
    team = [{"name": n, "role": r, "slug": s, "office": o} for n, r, e, s, o, _ in C.ABOUT["team"]]   # everyone in each office, Singapore included (user, 2026-11-06)
    body.append(f'<section id="globe" class="globe" data-people="{_html.escape(json.dumps(team, ensure_ascii=False), quote=True)}"></section>')   # the office globe, under the photo hero

    groups_opts = "".join(f'<option>{esc(g["name"])}</option>' for g in C.GROUPS)
    principal_opts = "".join(f'<option>{esc(p["name"])}</option>' for p in C.PRINCIPALS)
    enq_opts = "".join(f'<option>{esc(o)}</option>' for o in K["enquiring"])
    countries = ["Singapore", "Malaysia", "Thailand", "Indonesia", "Vietnam", "India", "South Korea", "Türkiye", "United Kingdom", "United States", "Other"]
    country_opts = '<option value="">Select…</option>' + "".join(f"<option>{esc(c)}</option>" for c in countries)
    form = f"""
<span id="datasheet"></span><span id="sample"></span><span id="service"></span>
<form class="form" action="#" method="post" enctype="multipart/form-data" novalidate>
  <div class="two">
    <label>Full name *<input type="text" name="name" required autocomplete="name"></label>
    <label>Company *<input type="text" name="company" required autocomplete="organization"></label>
  </div>
  <div class="two">
    <label>Company email *<input type="email" name="email" id="email" required autocomplete="email" placeholder="name@yourcompany.com" aria-describedby="email-help"></label>
    <label>Phone<input type="text" name="phone" autocomplete="tel"></label>
  </div>
  <span class="help help-row" id="email-help">Please use your company email. Personal addresses (Gmail, Yahoo, Outlook, etc.) are not accepted.</span>
  <label>Country<select name="country">{country_opts}</select></label>
  <label>I’m enquiring about *<select id="enquiring" name="enquiring" required>{enq_opts}</select></label>
  <label>Product group / product or principal<select name="product">
    <option value="">Select…</option>
    <optgroup label="Commodities Supply">{groups_opts}</optgroup>
    <optgroup label="Engineering Solutions">{principal_opts}</optgroup>
  </select></label>
  <label>Quantity, destination port &amp; Incoterm<input type="text" name="quantity"><span class="help">For Commodities Supply enquiries.</span></label>
  <label>Message *<textarea id="message" name="message" required></textarea></label>
  <label>Attachment<input type="file" name="attachment"><span class="help">Specification / tender document (optional).</span></label>
  <div class="btn-row"><button class="pill solid" type="submit">Send enquiry</button></div>
</form>"""
    # the form with a box beside it: response commitments and the enquiries email (user, 2026-11-06)
    # Commodities Supply gets a WhatsApp button to Adam Yeoh (user, 2026-11-06). The number is the site's existing
    # WhatsApp line (+65 8061 9119) until a direct number for Adam is supplied.
    WA = {"Commodities Supply": ('https://wa.me/6580619119?text=Hi%2C%20I%27d%20like%20to%20ask%20about%20commodities%20supply.', "WhatsApp us")}
    # Engineering enquiries go by email: its button sits under its own text, like Commodities' WhatsApp (client, 2026-11-07)
    WA["Engineering Solutions"] = ("mailto:inquiry@hexahessman.com", "inquiry@hexahessman.com")
    commits = "".join(f'<div class="ca-item"><h3>{esc(h)}</h3><p>{esc(p)}</p>'
                      + (f'<a class="pill ca-wa" href="{WA[h][0]}"{"" if WA[h][0].startswith("mailto:") else ' target="_blank" rel="noopener"'}>{esc(WA[h][1])}</a>' if h in WA else '')
                      + '</div>' for h, p in K["commitments"])
    aside = f'''<aside class="contact-aside" id="response">
  <p class="eyebrow">Response commitments</p>{commits}
</aside>'''
    body.append(section(f'<div class="contact-grid">{aside}<div class="contact-form">{form}</div></div>', title=K["form_h"], id_="quote"))

    # (the "Direct contacts" block was removed at the user's request, 2026-11-05)

    offices = []
    for country, entity, addr in K["offices"]:
        offices.append(f'<div class="card office" data-country="{esc_attr(country)}"><span class="country">{esc(country)}</span><h3>{esc(entity)}</h3><p>{esc(addr)}</p></div>')
    # The #globe scene (globe.js) renders the office list itself; this grid is the plain fallback.
    # ("All offices" removed, user 2026-11-06: the globe already lists every office)

    hours = "".join(f'<div class="row"><div>{esc(d)}</div><div class="muted">{esc(t)}</div></div>' for d, t in K["hours"])
    # ("Operating hours" removed, user 2026-11-06)
    body.append(CONTACT_JS)
    head_tags = ('<script type="importmap">{ "imports": { "three": "/assets/vendor/three.module.js?v=160", '
                 '"three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/" } }</script>\n')
    body_scripts = '<script type="module" src="/assets/globe.js?v=18"></script>\n'
    write("/contact/index.html", page("Contact", meta_desc(K["lead"]), "\n".join(body), extra_head=CONTACT_CSS,
                                      head_tags=head_tags, body_scripts=body_scripts))


def build_legal():
    for slug, title in C.LEGAL:
        body = hero_plain([("Home", "/"), (title, None)], "Legal", title,
                          [f"The {title} text for hexahessman.com will follow. For any questions in the meantime, contact inquiry@hexahessman.com."])
        write(f"/{slug}/index.html", page(title, f"{title} for hexahessman.com.", body))


def build_404():
    body = hero_plain([("Home", "/")], "404", "Page not found",
                      ["The page you are looking for has moved or does not exist."],
                      btns=None) + section(buttons(["View all commodities", "Request a quote"]), id_="links")
    write("/404.html", page("Page not found", "The page you are looking for has moved or does not exist.", body))


def main():
    build_commodities_hub()
    for g in C.GROUPS:
        build_group(g)
    for p in C.PRODUCTS:
        build_product(p)
    build_engineering_hub()
    for pr in C.PRINCIPALS:
        build_principal(pr)
    build_about()
    build_contact()
    build_legal()
    build_404()
    for w in WRITTEN:
        print(w)
    print(f"{len(WRITTEN)} files written")


if __name__ == "__main__":
    main()
