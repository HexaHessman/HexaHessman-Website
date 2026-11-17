#!/usr/bin/env python3
"""HexaHessman CMS engine: find every word and photo on the site, and write the editors' changes back into it.

    python3 tools/cms/cms.py            apply data/cms.json to the site, then write admin/seed.json
    python3 tools/cms/cms.py seed       only write admin/seed.json
    python3 tools/cms/cms.py apply FILE apply a changes file downloaded from the admin (local draft mode)

How it works
- Every page is plain HTML (most of it written by tools/sitegen/build.py), plus a few shared files: the menu
  (assets/site-header.js), the footer (assets/site-footer.js), the enquiry form on product pages
  (assets/product-contact.js) and the list on the Commodities page (assets/commodities-data.json).
- A "field" is one run of words as it stands in those files: a heading, a paragraph, a button, a photo description,
  a page's Google title and description, a team member's line, a menu label. Its key is a hash of its ORIGINAL words,
  so an edit stays attached to it however many times it is changed.
- data/cms.json holds the edits: {"edits": [{"o": original, "t": new words, "scope": "*" | "/page/url/"}],
  "images": [{"o": "/assets/old.jpg", "t": "/assets/cms/new.jpg", "scope": "*" | "/page/url/"}]}.
  scope "*" changes the words wherever they appear (every page, the menu, the footer); a page address only there.
- Only whole runs are replaced, never part of a sentence, so changing "Urea" never touches "Urea fertilizer".
- Pages the generator rebuilds start from the original words each time; files it does not rebuild (the homepage,
  the menu, the footer, the Commodities list) are changed in place, and data/cms-applied.json remembers what was
  written into them so the next change (or an undo) finds it again.
"""
import hashlib, html, json, os, re, sys, time, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CMS = os.path.join(ROOT, "data", "cms.json")
APPLIED = os.path.join(ROOT, "data", "cms-applied.json")
SEED = os.path.join(ROOT, "admin", "seed.json")
FONTS = os.path.join(ROOT, "tools", "cms", "fonts.json")
FONTS_CSS = os.path.join(ROOT, "assets", "cms-fonts.css")
FONT_SCOPE = "@fonts"   # font choices are saved as changes with this scope and o = "font:<group id>"

SHARED = [  # (file, name shown in the admin)
    ("assets/site-header.js", "Menu"),
    ("assets/site-footer.js", "Footer"),
    ("assets/product-contact.js", "Product enquiry form"),
    ("assets/commodities-data.json", "Commodities list"),
]
SKIP_DIRS = {"admin", "api", "assets", "tools", "data", "supabase", "node_modules", "individual", "masters", "previews"}
NOT_PAGES = {"logo.html", "sulphur3d.html", "eng-draw.html"}


def key_of(orig):
    return hashlib.sha1(orig.encode("utf-8")).hexdigest()[:12]


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def has_words(s):
    return any(c.isalnum() for c in s)


# ---------------------------------------------------------------- the files

def site_pages():
    """[(url, relpath)] for every live page."""
    out = []
    for dp, dns, fns in os.walk(ROOT):
        rel = os.path.relpath(dp, ROOT)
        top = rel.split(os.sep)[0]
        if rel != "." and (top in SKIP_DIRS or top.startswith(".")):
            dns[:] = []
            continue
        if rel == ".":
            dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]
            for f in ("index.html", "404.html"):
                if os.path.exists(os.path.join(ROOT, f)):
                    out.append(("/" if f == "index.html" else "/404.html", f))
            continue
        if "index.html" in fns:
            out.append(("/" + rel.replace(os.sep, "/") + "/", os.path.join(rel, "index.html")))
    # only pages that are published (tracked by git), not scratch pages
    tracked = None
    try:
        import subprocess
        tracked = set(subprocess.run(["git", "ls-files", "*.html"], cwd=ROOT, capture_output=True, text=True).stdout.split())
    except Exception:
        pass
    if tracked:
        out = [(u, f) for u, f in out if f.replace(os.sep, "/") in tracked]
    order = {"/": 0, "/commodities/": 1, "/engineering/": 2, "/about/": 3, "/contact/": 4}
    return sorted(out, key=lambda x: (order.get(x[0], 5 if x[0].startswith("/commodities/") else 6 if x[0].startswith("/engineering/") else 7), x[0]))


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def write(rel, s):
    with open(os.path.join(ROOT, rel), "w", encoding="utf-8") as f:
        f.write(s)


# ---------------------------------------------------------------- HTML

TOKEN = re.compile(r"(<!--.*?-->|<script\b.*?</script\s*>|<style\b.*?</style\s*>|<svg\b.*?</svg\s*>|<template\b.*?</template\s*>|<[^>]+>)", re.S | re.I)
ATTR = re.compile(r'(\s)([\w:-]+)="([^"]*)"')
BAR_LABEL = {"pp-bar-t": "Bar heading", "pp-total": "Bar total", "pp-call": "Note beside the bar"}
TEXT_ATTRS = {"alt": "Photo description", "title": "Hover text", "aria-label": "Screen reader label", "placeholder": "Box hint"}
META_TEXT = {"description": "Google description", "og:title": "Share title", "og:description": "Share description",
             "twitter:title": "Share title", "twitter:description": "Share description"}
TAG_LABEL = {"h1": "Main heading", "h2": "Heading", "h3": "Sub-heading", "h4": "Sub-heading", "h5": "Small heading", "h6": "Small heading",
             "p": "Paragraph", "a": "Link", "button": "Button", "li": "List item", "td": "Table", "th": "Table heading",
             "dt": "Label", "dd": "Value", "label": "Form label", "option": "Choice", "figcaption": "Caption",
             "blockquote": "Quote", "title": "Browser tab title", "small": "Small print", "strong": "Bold text", "em": "Text",
             "span": "Text", "div": "Text", "summary": "Question"}
JSON_SKIP_KEYS = {"slug", "href", "url", "src", "img", "image", "photo", "poster", "id", "office", "lat", "lon", "code", "icon",
                  "file", "path", "video", "jump", "key", "type", "class", "color", "pos", "side"}
VID_EXT = re.compile(r"(\.(mp4|webm|mov|m4v)(\?[^\"']*)?$)|^data:video/", re.I)


MAP_SRC = re.compile(r"https://(www\.)?google\.[a-z.]+/maps\?", re.I)


def map_query(src):
    """the place / address a Google map iframe shows (its q=)"""
    qs = urllib.parse.parse_qs(urllib.parse.urlsplit(src).query)
    return norm(qs.get("q", [""])[0])


def map_with(src, q):
    """the same map, showing another place"""
    u = urllib.parse.urlsplit(src)
    pairs = [(k, (q if k == "q" else v)) for k, v in urllib.parse.parse_qsl(u.query, keep_blank_values=True)]
    return urllib.parse.urlunsplit(u._replace(query=urllib.parse.urlencode(pairs, quote_via=urllib.parse.quote)))


def is_video(u):
    return bool(u and VID_EXT.search(u))


def keep_attrs(tok, names):
    return {k.lower(): v for _, k, v in ATTR.findall(tok) if k.lower() in names}


def img_to_video(tok, src):
    """a photo swapped for a video in the editor: the same spot, playing muted on a loop like the site's other clips"""
    a = keep_attrs(tok, {"class", "id", "style", "width", "height", "alt"})
    alt = html.unescape(a.pop("alt", ""))
    cls = (html.unescape(a.pop("class", "")) + " cms-vid").strip()
    extra = "".join(f' {k}="{v}"' for k, v in a.items())
    label = f' aria-label="{html.escape(alt, quote=True)}"' if alt.strip() else ' aria-hidden="true"'
    return f'<video class="{html.escape(cls, quote=True)}"{extra} src="{html.escape(src, quote=True)}" autoplay muted loop playsinline preload="metadata"{label}></video>'


def video_to_img(tok, src):
    """the other way round: a video put in by the editor goes back to being a photo"""
    a = keep_attrs(tok, {"class", "id", "style", "width", "height", "aria-label"})
    alt = html.unescape(a.pop("aria-label", ""))
    cls = " ".join(c for c in html.unescape(a.pop("class", "")).split() if c != "cms-vid")
    extra = (f' class="{html.escape(cls, quote=True)}"' if cls else "") + "".join(f' {k}="{v}"' for k, v in a.items())
    return f'<img{extra} src="{html.escape(src, quote=True)}" alt="{html.escape(alt, quote=True)}" loading="lazy" decoding="async">'


IMG_EXT = re.compile(r"\.(jpe?g|png|webp|gif|avif|svg)(\?[^\"']*)?$", re.I)


def tag_name(tok):
    m = re.match(r"<\s*/?\s*([a-zA-Z][\w-]*)", tok)
    return m.group(1).lower() if m else ""


def json_strings(obj, path=""):
    """yield (key, string) for the human-readable strings inside a JSON value"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                if k.lower() not in JSON_SKIP_KEYS and has_words(v) and not v.startswith(("/", "http", "#", "data:")):
                    yield k, v
            else:
                yield from json_strings(v, k)
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, str):
                if has_words(v) and not v.startswith(("/", "http", "#")) and path.lower() not in JSON_SKIP_KEYS:
                    yield path, v
            else:
                yield from json_strings(v, path)


def json_tokens(s, escape_attr):
    """the ways a string can be written as a JSON value (a value, not a key)"""
    outs = set()
    for ea in (False, True):
        t = json.dumps(s, ensure_ascii=ea)
        outs.add(html.escape(t, quote=True) if escape_attr else t)
    if escape_attr:   # the generator writes ' as-is inside double-quoted attributes
        outs |= {t.replace("&#x27;", "'") for t in list(outs)}
    return outs


def replace_json_tokens(s, lookup, escape_attr, seen):
    """replace JSON string values (never keys) equal to a lookup key"""
    for cur, new in lookup.items():
        for tok in json_tokens(cur, escape_attr):
            if tok not in s:
                continue
            newtok = json.dumps(new, ensure_ascii=False)
            if escape_attr:
                newtok = html.escape(newtok, quote=True).replace("&#x27;", "'")
            s, n = re.subn(re.escape(tok) + r"(?!\s*:)", lambda m: newtok, s)
            if n:
                seen.add(cur)
    return s


def scan_html(src, lookup=None, img_lookup=None):
    """Walk an HTML page. Without lookups: return its fields and photos. With lookups: return the page with matching
    runs of words / photo paths replaced, plus the set of texts found."""
    fields, images, seen = [], [], set()
    parts = TOKEN.split(src)
    out = []
    stack_tag, section, in_title = "", "", False
    in_legend, bar_box = False, ""
    drop_close = 0   # a video tag the editor turned back into a photo leaves its </video> behind: drop it
    meta_props = None
    for i, part in enumerate(parts):
        if i % 2 == 1:   # a tag, comment, or script/style/svg block
            tok = part
            name = tag_name(tok)
            low = tok[:20].lower()
            if low.startswith(("<!--", "<script", "<style", "<svg", "<template")):
                out.append(tok)
                continue
            closing = tok.startswith("</")
            if not closing:
                stack_tag = name
                in_title = name == "title"
                # the product pages' "where it comes from" bar: name its boxes plainly (pp-bar.js sizes the bar
                # from the legend's percentages, so changing a number moves the bar)
                cm = re.search(r'\bclass="([^"]*)"', tok)
                if cm:
                    c = cm.group(1).split()
                    in_legend = "pp-legend" in c or (in_legend and not ({"pp-total", "pp-call", "pp-drops"} & set(c)))
                    bar_box = BAR_LABEL.get(next((x for x in c if x in BAR_LABEL), ""), "")
                else:
                    bar_box = ""
                if name == "section":
                    m = re.search(r'\bid="([^"]+)"', tok)
                    section = m.group(1).replace("-", " ").capitalize() if m else section
                # attributes
                if name == "meta":
                    mm = re.search(r'\b(?:name|property)="([^"]+)"', tok)
                    meta_props = mm.group(1).lower() if mm else None
                swap = []   # the new photo / video path, when this tag's media is replaced
                cms_vid = name == "video" and "cms-vid" in tok
                def attr(m):
                    sp, an, av = m.group(1), m.group(2), m.group(3)
                    anl = an.lower()
                    val = html.unescape(av)
                    if anl in TEXT_ATTRS or (name == "meta" and anl == "content" and meta_props in META_TEXT):
                        n = norm(val)
                        if n and has_words(n):
                            if lookup is None:
                                fields.append({"o": n, "tag": "meta" if name == "meta" else anl,
                                               "label": META_TEXT.get(meta_props) if name == "meta" else TEXT_ATTRS[anl], "sec": section})
                            elif n in lookup:
                                seen.add(n)
                                return f'{sp}{an}="{html.escape(lookup[n], quote=True)}"'
                    elif (name == "img" and anl == "src") or (name == "video" and anl == "poster") or \
                            (name == "meta" and anl == "content" and meta_props in ("og:image", "twitter:image")) or \
                            (anl == "src" and (cms_vid or (name in ("video", "source") and is_video(val)))):
                        kind = "share" if name == "meta" else "video" if (anl == "src" and name in ("video", "source")) else name
                        if lookup is None and img_lookup is None:
                            if not val.startswith("data:"):
                                images.append({"src": val, "sec": section, "kind": kind})
                        elif img_lookup and val in img_lookup:
                            new = img_lookup[val]
                            # a photo spot takes a photo or a video; a video spot of the site's own takes only a video,
                            # and a poster or share picture only a photo
                            if (kind == "video" and not cms_vid and not is_video(new)) or (kind in ("share",) or anl == "poster") and is_video(new):
                                return m.group(0)
                            seen.add("img:" + val)
                            if (name == "img" and anl == "src") or cms_vid:
                                swap.append(new)
                            return f'{sp}{an}="{html.escape(new, quote=True)}"'
                    elif name == "iframe" and anl == "src" and MAP_SRC.match(val):
                        q = map_query(val)
                        if q:
                            if lookup is None:
                                fields.append({"o": q, "tag": "map", "label": "Google map: place or address (the pin moves to it)", "sec": section})
                            elif q in lookup:
                                seen.add(q)
                                return f'{sp}{an}="{html.escape(map_with(val, lookup[q]), quote=True)}"'
                    elif anl.startswith("data-") and val[:1] in "[{":
                        try:
                            data = json.loads(val)
                        except Exception:
                            return m.group(0)
                        if lookup is None:
                            for k, v in json_strings(data):
                                fields.append({"o": norm(v), "tag": "data", "label": k.replace("_", " ").capitalize() if k else "Text", "sec": section})
                        else:
                            hits = {c: t for c, t in lookup.items() if c in av or html.escape(c) in html.unescape(av) or c in val}
                            if hits:
                                av2 = replace_json_tokens(av, hits, True, seen)
                                if av2 != av:
                                    return f"{sp}{an}=\"{av2}\""
                    return m.group(0)
                if lookup is not None or img_lookup is not None or True:
                    new_tok = ATTR.sub(attr, tok)
                    if lookup is not None or img_lookup is not None:
                        tok = new_tok
                if swap and name == "img":
                    # the old srcset would keep showing the old photo on sharp screens
                    tok = re.sub(r'\s(srcset|sizes)="[^"]*"', "", tok)
                    if is_video(swap[0]):
                        tok = img_to_video(tok, swap[0])
                elif swap and cms_vid and not is_video(swap[0]):
                    tok = video_to_img(tok, swap[0])
                    drop_close += 1
            else:
                if name == "title":
                    in_title = False
                if name == "video" and drop_close:
                    drop_close -= 1
                    continue
            out.append(tok)
            continue
        # a run of text
        text = part
        val = html.unescape(text)
        n = norm(val)
        if n and has_words(n):
            if stack_tag in ("h1", "h2") and lookup is None:
                section = n if len(n) < 80 else n[:77] + "…"
            if lookup is None:
                label = TAG_LABEL.get("title" if in_title else stack_tag, "Text")
                if bar_box:
                    label = bar_box
                elif in_legend:
                    label = "Bar percentage (the bar follows it)" if stack_tag == "b" else "Bar part name"
                fields.append({"o": n, "tag": "title" if in_title else stack_tag, "label": label, "sec": section})
            elif n in lookup:
                seen.add(n)
                lead = val[:len(val) - len(val.lstrip())]
                trail = val[len(val.rstrip()):]
                text = lead + html.escape(lookup[n], quote=False) + trail
        out.append(text)
    if lookup is None and img_lookup is None:
        return fields, images
    return "".join(out), seen


# ---------------------------------------------------------------- JS and JSON

JS_STR = re.compile(r"""(?<![\w$])('(?:[^'\\\n]|\\.)*'|"(?:[^"\\\n]|\\.)*")""")
TPL = re.compile(r"`(?:[^`\\]|\\.)*`", re.S)
JS_NOT_TEXT = {"Escape", "Enter", "Tab", "ArrowDown", "ArrowUp", "ArrowLeft", "ArrowRight", "Home", "End", "UTC"}


SVG_PATH = re.compile(r"[MmLlHhVvCcSsQqTtAaZz][\d\s.,MmLlHhVvCcSsQqTtAaZz-]*")


def js_text_ok(s):
    if SVG_PATH.fullmatch(s.strip()):
        return False
    if not has_words(s) or s in JS_NOT_TEXT or len(s) > 400:
        return False
    if s.startswith(("/", "#", ".", "http", "data:", "mailto:", "tel:")) or re.search(r"[<>{}=;]|\$\{", s):
        return False
    if re.search(r"[a-z][A-Z]", s) and " " not in s:   # camelCase identifiers
        return False
    if not re.search(r"[A-Z]", s[:1]) and " " not in s:   # lower-case single words are code (class names, events)
        return False
    if re.fullmatch(r"[\w-]+\s*[\w-]*\(.*\)", s) or re.fullmatch(r"[\d.\s%a-z-]+", s):   # CSS values
        return False
    return True


def js_unquote(lit):
    try:
        if lit[0] == "'":
            body = lit[1:-1].replace("\\'", "'").replace('"', '\\"')
            return json.loads('"' + body + '"')
        return json.loads(lit)
    except Exception:
        return lit[1:-1]


def js_quote(s, q):
    body = json.dumps(s, ensure_ascii=False)[1:-1]
    if q == "'":
        body = body.replace('\\"', '"').replace("'", "\\'")
    return q + body + q


def scan_js(src, lookup=None):
    fields, seen = [], set()
    # text between tags inside template literals (the footer and menu are written as HTML in the script)
    def tpl(m):
        t = m.group(0)
        def seg(mm):
            raw = mm.group(1)
            n = norm(html.unescape(raw))
            if not n or not has_words(n) or "${" in raw or SVG_PATH.fullmatch(n):
                return mm.group(0)
            if lookup is None:
                fields.append({"o": n, "tag": "js", "label": "Text", "sec": ""})
                return mm.group(0)
            if n in lookup:
                seen.add(n)
                lead = raw[:len(raw) - len(raw.lstrip())]
                trail = raw[len(raw.rstrip()):]
                return ">" + lead + html.escape(lookup[n], quote=False).replace("`", "\\`").replace("${", "\\${") + trail + "<"
            return mm.group(0)
        t = re.sub(r">([^<>`]+)<", seg, t)
        # attribute texts inside the template (aria-label, alt, placeholder)
        def at(mm):
            an, av = mm.group(1), mm.group(2)
            n = norm(html.unescape(av))
            if not n or not has_words(n) or "${" in av:
                return mm.group(0)
            if lookup is None:
                fields.append({"o": n, "tag": an, "label": TEXT_ATTRS.get(an, "Text"), "sec": ""})
                return mm.group(0)
            if n in lookup:
                seen.add(n)
                return f'{an}="{html.escape(lookup[n], quote=True)}"'
            return mm.group(0)
        t = re.sub(r'\b(aria-label|alt|placeholder|title)="([^"$]*)"', at, t)
        return t
    src2 = TPL.sub(tpl, src)

    def lit(m):
        raw = m.group(1)
        s = js_unquote(raw)
        if not js_text_ok(s):
            return raw
        if lookup is None:
            fields.append({"o": norm(s), "tag": "js", "label": "Text", "sec": ""})
            return raw
        n = norm(s)
        if n in lookup:
            seen.add(n)
            return js_quote(lookup[n], raw[0])
        return raw
    # string literals outside template literals only
    pieces, last = [], 0
    for m in TPL.finditer(src2):
        pieces.append(("code", src2[last:m.start()]))
        pieces.append(("tpl", m.group(0)))
        last = m.end()
    pieces.append(("code", src2[last:]))
    out = []
    for kind, p in pieces:
        if kind == "code":
            # leave comments alone
            segs = re.split(r"(//[^\n]*|/\*.*?\*/)", p, flags=re.S)
            out.append("".join(s if (j % 2) else JS_STR.sub(lit, s) for j, s in enumerate(segs)))
        else:
            out.append(p)
    res = "".join(out)
    return (fields, []) if lookup is None else (res, seen)


def scan_json(src, lookup=None):
    if lookup is None:
        data = json.loads(src)
        return [{"o": norm(v), "tag": "data", "label": k.replace("_", " ").capitalize() if k else "Text", "sec": ""} for k, v in json_strings(data)], []
    seen = set()
    return replace_json_tokens(src, lookup, False, seen), seen


def scan_file(rel, src, lookup=None, img_lookup=None):
    if rel.endswith(".html"):
        return scan_html(src, lookup, img_lookup)
    if rel.endswith(".js"):
        if img_lookup and lookup is None:
            return src, set()
        return scan_js(src, lookup)
    if rel.endswith(".json"):
        if img_lookup and lookup is None:
            return src, set()
        return scan_json(src, lookup)
    raise ValueError(rel)


# ---------------------------------------------------------------- apply

def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def apply(cms=None, quiet=False):
    cms = cms if cms is not None else load_json(CMS, {})
    edits = cms.get("edits") or []
    fonts_css(edits)
    edits = [e for e in edits if e.get("scope") != FONT_SCOPE]
    images = cms.get("images") or []
    # photos chosen in draft mode arrive inside the changes file: save them as files in assets/cms/
    for e in images:
        t = e.get("t") or ""
        m = re.match(r"data:(?:image|video)/([\w+.-]+);base64,(.*)", t, re.S)
        if m:
            import base64
            raw = base64.b64decode(m.group(2))
            ext = {"jpeg": "jpg", "svg+xml": "svg", "quicktime": "mov"}.get(m.group(1), m.group(1))
            name = hashlib.sha1(raw).hexdigest()[:12] + "." + ext
            os.makedirs(os.path.join(ROOT, "assets", "cms"), exist_ok=True)
            with open(os.path.join(ROOT, "assets", "cms", name), "wb") as f:
                f.write(raw)
            e["t"] = "/assets/cms/" + name
    applied = load_json(APPLIED, {})
    files = [(u, f) for u, f in site_pages()] + [(None, f) for f, _ in SHARED]
    changed = 0
    new_applied = {}
    for url, rel in files:
        if not os.path.exists(os.path.join(ROOT, rel)):
            continue
        # the words this file should carry: a change for this page wins over a change everywhere
        want = {}
        for e in edits:
            o, t, sc = norm(e.get("o", "")), e.get("t"), e.get("scope", "*")
            if not o or t is None:
                continue
            t = str(t).strip()
            if sc == "*" and o not in want:
                want[o] = t
        if url:
            for e in edits:
                o, t, sc = norm(e.get("o", "")), e.get("t"), e.get("scope", "*")
                if o and t is not None and sc == url:
                    want[o] = str(t).strip()
        want_img = {}
        for e in images:
            o, t, sc = e.get("o"), e.get("t"), e.get("scope", "*")
            if o and t and (sc == "*" or sc == url):
                if sc == url or o not in want_img:
                    want_img[o] = t
        prev = applied.get(rel, {})
        prev_txt = {k: v for k, v in prev.items() if not k.startswith("img:")}
        prev_img = {k[4:]: v for k, v in prev.items() if k.startswith("img:")}
        lookup = {}
        for o in set(want) | set(prev_txt):
            target = want.get(o, o)
            for cur in (prev_txt.get(o), o):
                if cur is not None and cur != target:
                    lookup.setdefault(cur, target)
        img_lookup = {}
        for o in set(want_img) | set(prev_img):
            target = want_img.get(o, o)
            for cur in (prev_img.get(o), o):
                if cur and cur != target:
                    img_lookup.setdefault(cur, target)
        src = read(rel)
        new = src
        seen = set()
        if lookup or img_lookup:
            if rel.endswith(".html"):
                new, seen = scan_html(src, lookup or {}, img_lookup or None)
            elif lookup:
                new, seen = scan_file(rel, src, lookup)
        if new != src:
            write(rel, new)
            changed += 1
            if not quiet:
                print("cms:", rel)
        # remember what this file now carries in place of its original words
        rec = {}
        for o, t in want.items():
            if t != o and (t in seen or o in seen or prev_txt.get(o) in seen or (prev_txt.get(o) == t and t in new)):
                rec[o] = t
        for o, t in want_img.items():
            if t != o and ("img:" + o in seen or "img:" + str(prev_img.get(o)) in seen or (prev_img.get(o) == t and t in new)):
                rec["img:" + o] = t
        if rec:
            new_applied[rel] = rec
    os.makedirs(os.path.dirname(APPLIED), exist_ok=True)
    with open(APPLIED, "w", encoding="utf-8") as f:
        json.dump(new_applied, f, ensure_ascii=False, indent=1, sort_keys=True)
    if not quiet:
        print(f"cms: {len(edits)} word changes, {len(images)} photo changes, {changed} files updated")
    return changed


# ---------------------------------------------------------------- seed (what the admin shows)

def page_title(src):
    m = re.search(r"<title>(.*?)</title>", src, re.S)
    t = html.unescape(m.group(1)).strip() if m else ""
    return re.sub(r"\s*·\s*HexaHessman$", "", t) or "Home"


def area_of(url):
    if url == "/":
        return "Home"
    if url.startswith("/commodities/"):
        return "Commodities"
    if url.startswith("/engineering/"):
        return "Engineering"
    if url in ("/about/", "/contact/"):
        return "Company"
    return "Legal and other"


def seed():
    applied = load_json(APPLIED, {})
    cms = load_json(CMS, {})
    edits, images = cms.get("edits") or [], cms.get("images") or []
    live_fonts = {e["o"]: e["t"] for e in edits if e.get("scope") == FONT_SCOPE}
    edits = [e for e in edits if e.get("scope") != FONT_SCOPE]
    fields = {}   # key -> {o, t, n (how many places)}
    pages = []

    def add(rel, url, flist, ilist):
        # words now on the page that came from an edit are listed under their original words
        back = {norm(str(e.get("t", ""))): norm(e.get("o", "")) for e in edits if e.get("o") and e.get("t") is not None}
        back.update({v: k for k, v in applied.get(rel, {}).items() if not k.startswith("img:")})
        back_img = {e["t"]: e["o"] for e in images if e.get("o") and e.get("t")}
        back_img.update({v: k[4:] for k, v in applied.get(rel, {}).items() if k.startswith("img:")})
        out, keys_here = [], set()
        for f in flist:
            cur = f["o"]
            orig = back.get(cur, cur)
            k = key_of(orig)
            if k not in fields:
                fields[k] = {"o": orig, "t": cur, "where": []}
            if url and url not in fields[k]["where"]:
                fields[k]["where"].append(url)
            elif not url and ("@" + rel) not in fields[k]["where"]:
                fields[k]["where"].append("@" + rel)
            if k in keys_here and f["tag"] not in ("title", "meta"):
                continue   # the same words twice on one page: one box changes both
            keys_here.add(k)
            out.append({"k": k, "tag": f["tag"], "label": f["label"], "sec": f["sec"]})
        imgs, seen_src = [], set()
        for im in ilist:
            cur = im["src"]
            orig = back_img.get(cur, cur)
            if orig in seen_src:
                continue
            seen_src.add(orig)
            imgs.append({"o": orig, "t": cur, "sec": im["sec"], "kind": im["kind"]})
        return out, imgs

    for url, rel in site_pages():
        src = read(rel)
        flist, ilist = scan_html(src)
        out, imgs = add(rel, url, flist, ilist)
        pages.append({"url": url, "file": rel, "title": page_title(src), "area": area_of(url), "fields": out, "images": imgs})
    shared = []
    for rel, name in SHARED:
        if not os.path.exists(os.path.join(ROOT, rel)):
            continue
        flist, _ = scan_file(rel, read(rel))
        out, _ = add(rel, None, flist, [])
        shared.append({"url": "@" + rel, "file": rel, "title": name, "area": "Shared", "fields": out, "images": []})
    fcfg = load_json(FONTS, {"groups": [], "fonts": []})
    fcfg = {"groups": fcfg["groups"], "fonts": fcfg["fonts"], "live": live_fonts}
    data = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "pages": pages, "shared": shared, "fields": fields, "fonts": fcfg}
    os.makedirs(os.path.dirname(SEED), exist_ok=True)
    with open(SEED, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    nf = sum(len(p["fields"]) for p in pages + shared)
    ni = sum(len(p["images"]) for p in pages)
    print(f"cms: admin/seed.json with {len(pages)} pages, {len(shared)} shared parts, {len(fields)} different texts, {nf} boxes, {ni} photos")


def fonts_css(edits):
    """write assets/cms-fonts.css: the Google Fonts for the chosen families, and the group variables pointing at them.
    Groups left on their original font are not mentioned, so with no choices the file is only a comment."""
    cfg = load_json(FONTS, {"groups": [], "fonts": []})
    known = {f["name"]: f for f in cfg["fonts"]}
    chosen = {e["o"][5:]: e["t"] for e in edits if e.get("scope") == FONT_SCOPE and str(e.get("o", "")).startswith("font:")}
    fams, rules = [], []
    for g in cfg["groups"]:
        name = chosen.get(g["id"])
        if not name or name == g["default"] or name not in known:
            continue
        f = known[name]
        fall = {"serif": 'Georgia, "Times New Roman", serif', "mono": '"Courier New", monospace'}.get(f["kind"], '"Helvetica Neue", Arial, sans-serif')
        for v in g["vars"]:
            rules.append(f'  {v}: "{name}", {fall};')
        fam = "family=" + name.replace(" ", "+") + (":" + f["spec"] if f["spec"] else "")
        if fam not in fams:
            fams.append(fam)
    css = "/* Fonts chosen in the website editor (/admin, Fonts). Written by tools/cms/cms.py: do not edit by hand. */\n"
    if rules:
        css += f'@import url("https://fonts.googleapis.com/css2?{"&".join(fams)}&display=swap");\n'
        css += ":root, .cscroll {\n" + "\n".join(rules) + "\n}\n"
    old = read("assets/cms-fonts.css") if os.path.exists(FONTS_CSS) else None
    if old != css:
        write("assets/cms-fonts.css", css)
    changed = [g["name"] for g in cfg["groups"] if chosen.get(g["id"]) not in (None, g["default"]) and chosen.get(g["id"]) in known]
    print(f"cms: fonts: {', '.join(changed) if changed else 'all original'}")


def run():
    apply()
    seed()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        run()
    elif args[0] == "seed":
        seed()
    elif args[0] == "apply":
        cms = load_json(args[1], None) if len(args) > 1 else None
        if len(args) > 1:
            if cms is None:
                sys.exit(f"could not read {args[1]}")
            os.makedirs(os.path.dirname(CMS), exist_ok=True)
            with open(CMS, "w", encoding="utf-8") as f:
                json.dump(cms, f, ensure_ascii=False, indent=1)
        apply()
        seed()
    else:
        sys.exit(__doc__)
