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
    return '<nav class="crumbs" aria-label="Breadcrumb">' + "".join(parts) + "</nav>"


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
    thead = ""
    if block.get("headers"):
        thead = "<thead><tr>" + "".join(f"<th>{esc(h)}</th>" for h in block["headers"]) + "</tr></thead>"
    title = f'<h3 class="spec-title">{esc(block["title"])}</h3>' if block.get("title") else ""
    return f'{title}<table class="spec">{thead}<tbody>{"".join(rows)}</tbody></table>'


def defs_table(defs):
    rows = [(t, d) for t, d in defs if not is_placeholder(d)]
    if not rows:
        return ""
    return '<table class="spec"><tbody>' + "".join(f"<tr><td>{esc(t)}</td><td>{esc(d)}</td></tr>" for t, d in rows) + "</tbody></table>"


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
    if s.get("spec"):
        tables = [spec_table(b) for b in s["spec"]]
        tables = [t for t in tables if t]
        body.append('<div class="spec-stack">' + "".join(tables) + "</div>")
    if s.get("note") and not is_placeholder(s["note"]):
        body.append(f'<p class="note">{esc(s["note"])}</p>')
    content = "".join(b for b in body if b)
    if not content.strip():
        return ""
    return section(content, title=s.get("title"), id_=slugify(s.get("title", "")))


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
.spec-stack { display: grid; gap: 34px; }
.spec-title { margin-bottom: 12px; }
.card .apps { margin-top: 10px; font-size: 14px; color: var(--ink-soft); }
.card ul.list { margin-top: 6px; }
.who { font-size: clamp(18px, 1.6vw, 24px); letter-spacing: -.01em; max-width: 60ch; }
.cta-band { border: 1px solid var(--line); border-radius: 12px; padding: clamp(28px, 4vw, 48px); display: grid; gap: 18px; background: rgba(var(--ink-rgb),.03); }
.cta-band h2 { max-width: 20ch; }
.related { display: grid; gap: 18px; }
/* 3D mount points (#hero-3d on two group pages, #globe on contact) are empty until the scenes are mounted:
   hide them and keep the plain hero's full top padding so the breadcrumb clears the header bar. */
.hero-3d:empty, .globe:empty { display: none; }
.hero-3d:empty + .hero.plain, .globe:empty + .hero.plain { padding-top: 170px; }
.hero .wrap .coverage { font-family: var(--mono); font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
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
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300..700&family=Geist+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/header.css?v=2610k">
<link rel="stylesheet" href="/assets/site.css?v=2611e">
<style>{PAGE_CSS}{extra_head}</style>
{head_tags}</head>
<body{f' class="{body_class}"' if body_class else ""}>
<div id="site-header"></div>
<main>
{body}
</main>
<div id="site-footer"></div>
<script src="/assets/site-header.js?v=2610k" defer></script>
<script src="/assets/site-footer.js" defer></script>
{body_scripts}</body>
</html>
"""


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
    cells = "".join(f'<div class="pcell" data-i="{i}"><span class="ph"><i></i><b>Partner logo</b></span></div>' for i in range(20))
    body = [f'''<section class="arrive" id="partners" aria-label="Partners">
  <div class="arrive-top">{logo}<div class="arrive-word">HexaHessman</div>
  <p class="eyebrow arrive-eyebrow">Commodities Supply</p>
  <h1 class="arrive-title">Trusted by producers and buyers across nine markets</h1></div>
  <div class="pwall"><div class="pgrid">{cells}</div></div>
  <div class="arrive-cue">Scroll to explore</div>
</section>''', f'<section id="cscroll" class="cscroll" data-intro="{intro}"></section>']

    cards = []
    for g in C.GROUPS:
        extra = f'<p class="apps">{esc(g["hub_products"])}</p>'
        cards.append(card(g["name"], g["serves"], href=group_url(g["slug"]), more="View group →", extra=extra))
    body.append(section(grid(cards, "c3"), title="Product groups", eyebrow="What we supply",
                        lead="Five groups, each built around the industries it serves.", id_="groups"))

    how = spec_table({"rows": H["how"]})
    body.append(section(how, title="How we supply", id_="how-we-supply"))

    body.append(section(f"""<div class="cta-band">
  <h2>{esc(H["cta_h"])}</h2><p class="lead">{esc(H["cta_p"])}</p>{buttons(H["cta_buttons"])}</div>""", id_="cta"))

    write("/commodities/index.html", page("Commodities Supply", meta_desc(H["lead"]), "\n".join(body), body_scripts='<script src="https://cdn.jsdelivr.net/npm/lenis@1/dist/lenis.min.js"></script>\n<script src="/assets/cscroll.js?v=2611d" defer></script>\n<script src="/assets/arrive.js?v=2610k" defer></script>\n'))


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


def build_product(p):
    g = GROUP_BY_SLUG[p["group"]]
    body = [hero_plain([("Home", "/"), ("Commodities Supply", "/commodities/"), (g["name"], group_url(g["slug"])), (short_name(p["slug"]), None)],
                       g["name"], p["title"], p["hero"])]
    for s in p["sections"]:
        body.append(render_section(s))
    # related products
    rel = []
    for name in p.get("related", []):
        slug = PRODUCT_NAME_TO_SLUG.get(name)
        if slug and slug in PRODUCT_BY_SLUG:
            rel.append(card(short_name(slug), descriptor(slug), href=product_url(slug), more="View product →"))
    if rel:
        body.append(section(grid(rel, "c4"), title="Related products", id_="related"))
    body.append(enquiry_block())
    write(f"{product_url(p['slug'])}index.html", page(short_name(p["slug"]), meta_desc(p["hero"][-1] if len(p["hero"]) > 1 and len(clean(p["hero"][0])) < 70 else p["hero"][0]), "\n".join(body)))


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
    one = "".join(f'<li class="mq-cell"><a href="/engineering/{slug}/" tabindex="-1"><img src="/assets/engineering/logo-{slug}-green.png?v=1" alt="{esc_attr(names[slug])}" class="mq-logo mq-{slug}"></a></li>'
                  for slug, _, _ in H["principals"])
    track = f'<ul class="mq-set">{one * 2}</ul><ul class="mq-set" aria-hidden="true">{one * 2}</ul>'
    body = [f'''<section class="arrive eng-arrive" aria-label="Engineering Solutions">
  <div class="arrive-top">{ARRIVE_LOGO}<div class="arrive-word">HexaHessman</div>
  <p class="eyebrow arrive-eyebrow">Engineering Solutions</p>
  <h1 class="arrive-title">{esc(H["h1"])}</h1></div>
  <div class="mq" aria-label="Principals we represent"><p class="mq-label">Principals we represent</p><div class="mq-view"><div class="mq-track">{track}</div></div></div>
  <div class="arrive-cue">Scroll to explore</div>
</section>''']
    body.append(f'<section class="ewords" aria-label="About the division"><div class="ewords-pin"><p class="ewords-text">{esc(H["statement"])}</p></div></section>')

    stops = []
    n = len(H["principals"])
    for i, (slug, name, short) in enumerate(H["principals"]):
        pr = PR[slug]
        tags = "".join(f"<li>{esc(t)}</li>" for t in H["principal_tags"].get(slug, []))
        cov = f'<p class="ep-cov">{esc(pr["coverage"])}</p>' if pr.get("coverage") else ""
        stops.append(f'''<article class="ep {'right' if i % 2 else 'left'}" id="{slug}">
  <a class="ep-photo cs-photo" href="/engineering/{slug}/" data-reveal="photo" tabindex="-1" aria-hidden="true"><img src="/assets/engineering/{slug}.jpg?v=1" alt="" loading="lazy" decoding="async" width="1200" height="900"></a>
  <div class="ep-copy">
    <div class="ep-top" data-reveal="fade"><span class="ep-n">{i + 1:02d} / {n:02d}</span><span class="eyebrow">{esc(pr["eyebrow"])}</span></div>
    <img class="ep-logo mq-{slug}" src="/assets/engineering/logo-{slug}-green.png?v=1" alt="{esc_attr(name)}" data-reveal="fade">
    <h2 class="ep-short" data-reveal="fade">{esc(short)}</h2>
    <p class="ep-brief" data-reveal="fade">{esc(pr["hero"][0])}</p>
    <ul class="ep-tags" data-reveal="fade">{tags}</ul>
    <div class="ep-foot" data-reveal="fade">{cov}<a class="pill solid" href="/engineering/{slug}/">Read more about {esc(name)} →</a></div>
  </div>
</article>''')
    body.append(f'<section class="eprin" id="principals" aria-label="Principals we represent">{"".join(stops)}</section>')

    comps = "".join(f'<div class="card"><h3>{esc(cat)}</h3>{ul_list(items)}</div>' for cat, items in H["components_list"])
    body.append(section(f'<div class="grid c3">{comps}</div><div style="height:28px"></div>{buttons(["Request a quote"], first_solid=False)}',
                        title="Engineering Components", lead=H["components"], id_="components"))
    body.append(section(grid([card(h, d) for h, d in H["services"]], "c3"), title="Services", id_="services"))
    body.append(section(ul_list(H["sectors"]), title="Sectors served", id_="sectors"))
    steps = "".join(f'<div class="card"><span class="n">{i + 1:02d}</span><h3>{esc(h)}</h3><p>{esc(d)}</p></div>' for i, (h, d) in enumerate(H["lifecycle"]))
    body.append(section(f'<div class="steps">{steps}</div>', title="Project lifecycle", id_="lifecycle"))
    body.append(section(f'<div class="cta-band"><h2>{esc(H["cta_h"])}</h2>{buttons(H["cta_buttons"])}</div>', id_="cta"))
    scripts = ('<script src="https://cdn.jsdelivr.net/npm/lenis@1/dist/lenis.min.js"></script>\n'
               '<script src="/assets/arrive.js?v=2610k" defer></script>\n<script src="/assets/eng.js?v=2610k" defer></script>\n')
    write("/engineering/index.html", page("Engineering Solutions", meta_desc(H["lead"]), "\n".join(body), body_scripts=scripts, body_class="eng"))


def build_principal(pr):
    extra = f'<p class="coverage">{esc(pr["coverage"])}</p>' if pr.get("coverage") else ""
    body = [hero_plain([("Home", "/"), ("Engineering Solutions", "/engineering/"), (pr["name"], None)],
                       "Engineering Solutions", pr["h1"], pr["hero"], extra=f'<p class="eyebrow">{esc(pr["eyebrow"])}</p>{extra}')]
    for s in pr["sections"]:
        body.append(render_section(s))
    cta = ""
    if pr.get("cta_h"):
        cta += f"<h2>{esc(pr['cta_h'])}</h2>"
    if pr.get("cta_p"):
        cta += f'<p class="lead">{esc(pr["cta_p"])}</p>'
    cta += buttons(pr["cta_buttons"])
    body.append(section(f'<div class="cta-band">{cta}</div>', id_="cta"))
    write(f"/engineering/{pr['slug']}/index.html", page(pr["name"], meta_desc(pr["hero"][0]), "\n".join(body), body_class="eng"))


def avatar_svg(name):
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    return (f'<svg class="avatar" viewBox="0 0 96 96" role="img" aria-label="{esc_attr(name)}">'
            f'<circle cx="48" cy="48" r="46" fill="none" stroke="currentColor" stroke-width="1.2" opacity=".5"/>'
            f'<text x="48" y="56" text-anchor="middle" font-family="Geist Mono, monospace" font-size="26" fill="currentColor">{initials}</text></svg>')


def photo(slug, name):
    return f'<img class="avatar photo" src="/assets/team/{slug}.jpg" alt="{esc_attr(name)}" loading="lazy" width="360" height="360">'


def team_card(name, role, entity, slug=None):
    pic = photo(slug, name) if slug else avatar_svg(name)
    return f'<div class="card team-card">{pic}<h3>{esc(name)}</h3><p>{esc(role)}</p><p class="apps">{esc(entity)}</p></div>'


ABOUT_CSS = """
.about-hero { position: relative; height: 210svh; }   /* the hero holds for about a screen while the logo turns */
.about-pin { position: sticky; top: 0; height: 100svh; min-height: 0; align-items: flex-end; padding-top: 140px; }
.about-logo { position: absolute; inset: 0; z-index: 0; pointer-events: none; }
.about-logo iframe { width: 100%; height: 100%; border: 0; display: block; background: transparent; opacity: 0; animation: aboutLogoIn .9s ease .2s forwards; }
@keyframes aboutLogoIn { to { opacity: 1; } }
.about-pin .wrap { max-width: 600px; }
.about-pin h1 { text-shadow: 0 2px 28px rgba(15,42,30,.85); }
.about-cue { position: absolute; right: var(--gutter); bottom: clamp(48px, 7vw, 96px); z-index: 1; display: flex; align-items: center; gap: 12px; font-family: var(--mono); font-size: 11px; letter-spacing: .15em; text-transform: uppercase; color: var(--muted); }
.about-cue i { width: 1px; height: 44px; background: linear-gradient(var(--ink-soft), transparent); animation: aboutCue 2.2s ease-in-out infinite; transform-origin: top; }
@keyframes aboutCue { 0% { transform: scaleY(0); } 50% { transform: scaleY(1); } 100% { transform: scaleY(1); opacity: 0; } }
@media (max-width: 720px) { .about-pin { padding-bottom: 72px; } .about-cue { display: none; } }
@media (prefers-reduced-motion: reduce) { .about-logo iframe { animation: none; opacity: 1; } .about-cue i { animation: none; } }
.timeline { display: grid; gap: 0; }
.timeline .row { display: grid; grid-template-columns: 120px 1fr; gap: 20px; padding: 18px 0; border-top: 1px solid var(--line); }
.timeline .row:last-child { border-bottom: 1px solid var(--line); }
.timeline .year { font-family: var(--mono); font-size: 20px; letter-spacing: -.02em; }
.markets { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
.markets span { font-family: var(--mono); font-size: 11px; letter-spacing: .14em; text-transform: uppercase; padding: 8px 12px; border: 1px solid var(--line); border-radius: 999px; color: var(--ink-soft); }
/* ---- the team lookbook: one line of people in the middle of the stage, the front one sharp, the rest a step back
   each (smaller, fainter, more blurred); a press walks the line forward. A part of the globe sits at the right edge. ---- */
.tl { padding-bottom: 0; }
.tl .section-head { margin-bottom: clamp(16px, 3vh, 36px); }
.tl-wrap { position: relative; }
.tl-stage { position: relative; height: 100svh; min-height: 640px; max-height: 1040px; overflow: hidden; --fw: min(66vh, 46vw); }
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
.tl-globe { position: absolute; z-index: 1; left: 50%; top: -2.5%; height: 220%; aspect-ratio: 1; transform: translateX(-50%); pointer-events: none; }
.tl-globe canvas { width: 100%; height: 100%; display: block; }
.tl-globe-label { position: absolute; left: 0; top: 0; margin: -30px 0 0 10px; padding: 4px 8px; border: 1px solid var(--line-strong); border-radius: 4px; background: rgba(15,42,30,.75);
  font: 400 11px/1.3 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--ink-soft); white-space: nowrap; opacity: 0; transition: opacity .4s; }
.tl-foot { display: contents; }
.tl-info { position: absolute; z-index: 3; left: var(--gutter); top: clamp(120px, 21vh, 200px); max-width: min(560px, 48vw); display: grid; gap: 10px; pointer-events: none; }
.tl-count { font: 400 12px/1 var(--mono); letter-spacing: .18em; color: var(--muted); }
.tl-name { font-size: clamp(34px, 4.6vw, 72px); font-weight: 500; line-height: .98; letter-spacing: -.04em; text-shadow: 0 2px 28px rgba(15,42,30,.9); }
.tl-role { font-size: clamp(16px, 1.5vw, 22px); color: var(--ink); }
.tl-where { font: 400 11px/1.5 var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.tl-desc { margin-top: 8px; max-width: 40ch; font-size: clamp(15px, 1.15vw, 17px); line-height: 1.5; color: var(--ink-soft); }
.tl-info.swap .tl-name, .tl-info.swap .tl-role, .tl-info.swap .tl-where, .tl-info.swap .tl-desc { animation: tlSwap .7s cubic-bezier(.2,.7,.2,1) both; }
.tl-info.swap .tl-role { animation-delay: .06s; } .tl-info.swap .tl-where { animation-delay: .12s; } .tl-info.swap .tl-desc { animation-delay: .18s; }
@keyframes tlSwap { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
.tl-ctrl { position: absolute; z-index: 3; right: var(--gutter); bottom: clamp(36px, 6vh, 72px); display: flex; gap: 10px; align-items: center; }
.tl-hint { font: 400 11px/1 var(--mono); letter-spacing: .15em; text-transform: uppercase; color: var(--muted); margin-right: 8px; }
.tl-ctrl button { width: 54px; height: 54px; border-radius: 50%; border: 1px solid var(--line-strong); background: rgba(15,42,30,.55); color: var(--ink); cursor: pointer; display: grid; place-items: center;
  -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); transition: background .25s, color .25s, transform .25s; }
.tl-ctrl button:hover { background: var(--ink); color: var(--paper); }
.tl-ctrl button:active { transform: scale(.94); }
.tl-ctrl svg { width: 20px; height: 20px; }
/* everyone at once, under the line (for people who would rather not step through); a card jumps the line to that person */
.tl-all { padding: clamp(56px, 9vh, 110px) var(--gutter) 0; }
.tl-all .eyebrow { margin-bottom: 26px; }
.tl-grid { list-style: none; display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px 24px; max-width: 1040px; margin: 0 auto; }   /* three across, in the order of the customer's team sheet */
.tl-grid button { width: 100%; display: grid; gap: 4px; justify-items: center; text-align: center; background: none; border: 0; color: var(--ink); font: inherit; cursor: pointer; padding: 0; }
.tl-grid-pic { display: block; width: 100%; aspect-ratio: 900 / 781; overflow: hidden; margin-bottom: 12px; border-radius: 8px; background: radial-gradient(ellipse at 50% 100%, rgba(238,227,199,.12), rgba(238,227,199,.03) 70%); border: 1px solid var(--line); transition: border-color .3s, background .3s; }
.tl-grid-pic img { width: 100%; height: 100%; object-fit: cover; display: block; filter: saturate(0); transition: transform .5s cubic-bezier(.2,.7,.2,1); }
.tl-grid button:hover .tl-grid-pic { border-color: var(--line-strong); background: radial-gradient(ellipse at 50% 100%, rgba(238,227,199,.2), rgba(238,227,199,.05) 70%); }
.tl-grid button:hover img { transform: scale(1.04); }
.tl-grid b { font-weight: 500; font-size: 16px; letter-spacing: -.01em; }
.tl-grid span:not(.tl-grid-pic) { font-size: 13px; color: var(--ink-soft); }
.tl-grid small { font: 400 10px/1.5 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
@media (max-width: 900px) {   /* phones: the figure fills the width, the write-up and buttons sit below the stage */
  .tl-stage { --fw: min(96vw, 70vh); height: calc(var(--fw) * .868 + 16px); min-height: 0; max-height: none; }
  .tl-stage::after { height: 22%; }
  .tl-globe { left: 108%; top: 5%; height: 170%; }
  .tl-foot { display: grid; gap: 20px; padding: 22px 20px 0; }
  .tl-info, .tl-ctrl { position: static; max-width: none; }
  .tl-globe-label { margin: 14px 0 0 0; translate: -50% 0; }   /* the label hangs under the pin, clear of the head and the edge */
  .tl-name { font-size: clamp(30px, 9vw, 46px); }
  .tl-hint { display: none; } .tl-ctrl button { width: 50px; height: 50px; }
  .tl-all { padding: 48px 20px 0; }
  .tl-grid { gap: 20px 10px; }
  .tl-grid b { font-size: 13px; } .tl-grid span:not(.tl-grid-pic) { font-size: 11px; } .tl-grid small { font-size: 8.5px; letter-spacing: .08em; }
}
@media (prefers-reduced-motion: reduce) { .tl-cut, .tl-cut.far { transition: none; } .tl-info.swap * { animation: none; } }
/* the closing call: plain and centred, no card */
.cta-band.plain { border: 0; background: none; border-radius: 0; padding: clamp(24px, 6vh, 72px) 0 clamp(16px, 3vh, 32px); justify-items: center; text-align: center; gap: 22px; }
.cta-band.plain h2 { max-width: 14ch; font-size: clamp(36px, 4.6vw, 72px); font-weight: 500; line-height: 1.0; letter-spacing: -.04em; text-wrap: balance; }
.cta-band.plain .lead { max-width: 46ch; }
.cta-band.plain .btn-row { justify-content: center; margin-top: 10px; }
"""


def build_about():
    A = C.ABOUT
    # hero: the 3D drawing of the mark (logo.html?embed) draws itself on behind the headline
    body = [f"""<section class="about-hero"><div class="hero about-pin">
  <div class="about-logo"><iframe src="/logo.html?embed&v=2" title="" aria-hidden="true" tabindex="-1"></iframe></div>
  <div class="wrap">
    {crumbs([("Home", "/"), ("About", None)])}
    <p class="eyebrow">{esc(A["eyebrow"])}</p>
    <h1>{esc(A["h1"])}</h1>
    <p class="lead">{esc(A["lead"])}</p>
  </div>
  <div class="about-cue" aria-hidden="true"><span>Scroll</span><i></i></div>
</div></section>
<script>
(() => {{  // the drawing leans toward the cursor
  const f = document.querySelector('.about-logo iframe'); if (!f) return;
  addEventListener('pointermove', e => f.contentWindow && f.contentWindow.postMessage({{ type: 'logo-pointer', x: (e.clientX / innerWidth - .5) * 2, y: (e.clientY / innerHeight - .5) * 2 }}, '*'), {{ passive: true }});
  // one full turn while the hero scrolls by
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const sec = f.closest('.about-hero');
  const send = () => {{ const r = sec.getBoundingClientRect(); const p = Math.min(1, Math.max(0, -r.top / Math.max(1, r.height - innerHeight))); f.contentWindow && f.contentWindow.postMessage({{ type: 'logo-scroll', p }}, '*'); }};
  addEventListener('scroll', send, {{ passive: true }}); f.addEventListener('load', send); send();
}})();
</script>"""]
    body.append(section("".join(f"<p>{esc(p)}</p>" for p in A["story"]), title="Our story", id_="story"))
    tl = "".join(f'<div class="row"><div class="year">{esc(y)}</div><div>{esc(t)}</div></div>' for y, t in A["timeline"])
    body.append(section(f'<div class="timeline">{tl}</div>', title="Timeline", id_="timeline"))
    structure = grid([card("Commodities Supply", "Operating division", href="/commodities/", more="View →"),
                      card("Engineering Solutions", "Operating division", href="/engineering/", more="View →"),
                      card("HexaHessman Asset Management (HHAM)", "Investment arm")], "c3")
    body.append(section(f'<p class="lead">{esc(A["group_p"])}</p><div style="height:28px"></div>{structure}', title=A["group_h"], eyebrow="Group structure", id_="group"))
    body.append(section(grid([card(h, p, href=href, more="Learn more →") for h, p, href in A["specialise"]], "c3"), title="What we specialise in", id_="specialise"))
    body.append(section(grid([card(v, None) for v in A["values"]], "c4"), title="Our values", id_="values"))
    markets = '<div class="markets">' + "".join(f"<span>{esc(m)}</span>" for m in A["markets"]) + "</div>"
    body.append(section(f'<p class="lead">{esc(A["reach_p"])}</p>{markets}', title=A["reach_h"], id_="reach"))
    # the team lookbook: everyone in one line (team-lookbook.js), a part of the globe at the side (team-globe.js)
    people = [dict(name=n, role=r, entity=e, slug=slug, office=o, city=A["office_pins"][o][0], country=A["office_pins"][o][1],
                   lat=A["office_pins"][o][2], lon=A["office_pins"][o][3], blurb=b) for n, r, e, slug, o, b in A["team"]]
    arrow = lambda d: f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="{"M4 12h16M13 5l7 7-7 7" if d > 0 else "M20 12H4M11 5l-7 7 7 7"}"/></svg>'
    fallback = "".join(f'<li><b>{esc(n)}</b> — {esc(r)}, {esc(e)}</li>' for n, r, e, _, _, _ in A["team"])
    body.append(f'''<section class="section tl" id="team" data-people="{_html.escape(json.dumps(people, ensure_ascii=False), quote=True)}">
  <div class="wrap section-head"><p class="eyebrow">Our people</p><h2>{esc(A["team_h"])}</h2><p class="lead">{esc(A["team_lead"])}</p></div>
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
  <div class="wrap tl-all">
    <p class="eyebrow">All eighteen</p>
    <ul class="tl-grid">{"".join(f'<li><button type="button" data-i="{i}"><span class="tl-grid-pic"><img src="/assets/team/cut/{slug}.webp?v=1" alt="" loading="lazy" decoding="async" width="900" height="781"></span><b>{esc(n)}</b><span>{esc(r)}</span><small>{esc(e)}</small></button></li>' for i, (n, r, e, slug, _, _) in enumerate(A["team"]))}</ul>
  </div>
  <noscript><div class="wrap"><ul>{fallback}</ul></div></noscript>
</section>''')
    # the closing call: no card, centred, about working with the people above
    body.append(section(f'<div class="cta-band plain"><p class="eyebrow">{esc(A["cta_eyebrow"])}</p><h2>{esc(A["cta_h"])}</h2><p class="lead">{esc(A["cta_p"])}</p>{buttons(A["cta_buttons"])}</div>', id_="cta"))
    head_tags = ('<script type="importmap">{ "imports": { "three": "/assets/vendor/three.module.js?v=160", '
                 '"three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/" } }</script>\n')
    scripts = '<script src="/assets/team-lookbook.js?v=8" defer></script>\n<script type="module" src="/assets/team-globe.js?v=4"></script>\n'
    write("/about/index.html", page("About", meta_desc(A["story"][0]), "\n".join(body), extra_head=ABOUT_CSS, head_tags=head_tags, body_scripts=scripts))


CONTACT_CSS = """
.form { display: grid; gap: 18px; max-width: 720px; }
.form .two { display: grid; gap: 18px; grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr)); }
.form label { display: grid; gap: 8px; font-family: var(--mono); font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.form input, .form select, .form textarea { width: 100%; padding: 14px 16px; border-radius: 8px; border: 1px solid var(--line-strong); background: rgba(255,255,255,.03); color: var(--ink); font: inherit; font-size: 15px; letter-spacing: 0; text-transform: none; }
.form input:focus, .form select:focus, .form textarea:focus { outline: 1px solid var(--ink-soft); outline-offset: 1px; }
.form select option { color: #111; }
.form textarea { min-height: 160px; resize: vertical; }
.form input[type=file] { padding: 10px 12px; }
.form .help { font-size: 13px; color: var(--muted); text-transform: none; letter-spacing: 0; font-family: var(--sans); }
.form .help.error { color: #f0b49a; }
.form input.invalid { border-color: #f0b49a; }
.contact-card h3 { margin-bottom: 6px; }
.contact-person { display: flex; gap: 14px; align-items: center; margin-top: 12px; }
.contact-person .avatar.photo { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; flex: none; background: #fff; border: 1px solid var(--line); }
.contact-card .role { color: var(--muted); font-size: 14px; }
.contact-card a { display: inline-block; margin-top: 12px; text-decoration: none; font-family: var(--mono); font-size: 13px; }
.office .country { font-family: var(--mono); font-size: 11px; letter-spacing: .15em; text-transform: uppercase; color: var(--muted); margin-bottom: 10px; display: block; }
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
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) err = 'Please enter a valid email address.';
    else if (freeRe.test(domain)) err = 'Please use your company email address — ' + domain + ' is a personal email provider.';
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
    body = ['<section id="globe" class="globe"></section>']
    body.append(hero_plain([("Home", "/"), ("Contact", None)], K["eyebrow"], K["h1"], [K["lead"]]))
    body.append(section(grid([card(h, p) for h, p in K["commitments"]], "c2") + '<div style="height:24px"></div>' + buttons(["Message us on WhatsApp (+65 8061 9119)"]),
                        title="Response commitments", id_="response"))

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
    <label>Company email *<input type="email" name="email" id="email" required autocomplete="email" placeholder="name@yourcompany.com" aria-describedby="email-help"><span class="help" id="email-help">Please use your company email. Personal addresses (Gmail, Yahoo, Outlook, etc.) are not accepted.</span></label>
    <label>Phone / WhatsApp<input type="text" name="phone" autocomplete="tel"></label>
  </div>
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
    body.append(section(form, title=K["form_h"], id_="quote"))

    direct = []
    for label, name, role, email in K["direct"]:
        inner = f'<p class="eyebrow">{esc(label)}</p>'
        if name:
            slug = name.lower().replace(" ", "-")
            inner += f'<div class="contact-person">{photo(slug, name)}<div><h3>{esc(name)}</h3><p class="role">{esc(role)}</p></div></div>'
        inner += f'<a href="mailto:{email}">{esc(email)}</a>'
        direct.append(f'<div class="card contact-card">{inner}</div>')
    body.append(section(grid(direct, "c3"), title="Direct contacts", id_="direct"))

    offices = []
    for country, entity, addr in K["offices"]:
        offices.append(f'<div class="card office" data-country="{esc_attr(country)}"><span class="country">{esc(country)}</span><h3>{esc(entity)}</h3><p>{esc(addr)}</p></div>')
    # The #globe scene (globe.js) renders the office list itself; this grid is the plain fallback.
    body.append(section(grid(offices, "c3"), title="All offices", id_="offices"))

    hours = "".join(f'<div class="row"><div>{esc(d)}</div><div class="muted">{esc(t)}</div></div>' for d, t in K["hours"])
    body.append(section(f'<div class="hours">{hours}</div>', title="Operating hours", id_="hours"))
    body.append(CONTACT_JS)
    head_tags = ('<script type="importmap">{ "imports": { "three": "/assets/vendor/three.module.js?v=160", '
                 '"three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/" } }</script>\n')
    body_scripts = '<script type="module" src="/assets/globe.js?v=2"></script>\n'
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
