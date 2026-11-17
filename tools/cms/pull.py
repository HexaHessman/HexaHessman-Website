#!/usr/bin/env python3
"""Fetch the editors' changes from Supabase into data/cms.json (tools/cms/cms.py then puts them into the pages).

Runs in .github/workflows/cms-publish.yml with SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.
New photos are downloaded into assets/cms/ so the site never depends on Supabase to show them.

    python3 tools/cms/pull.py          fetch the changes
    python3 tools/cms/pull.py --done   record a finished publish (the last step of the workflow)
"""
import json, os, re, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "data", "cms.json")
MEDIA = os.path.join(ROOT, "assets", "cms")
URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

if not URL or not KEY:
    print("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing; leaving data/cms.json as it is.")
    sys.exit(0)

H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}


def get(table, query=""):
    req = urllib.request.Request(f"{URL}/rest/v1/{table}?{query}", headers=H)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


if "--done" in sys.argv:
    n = len(get("cms_edits", "select=id"))
    body = json.dumps({"requested_by": os.environ.get("PUBLISHED_BY") or "website", "status": "done", "edits": n}).encode()
    req = urllib.request.Request(f"{URL}/rest/v1/cms_publishes", data=body, method="POST",
                                 headers={**H, "Content-Type": "application/json", "Prefer": "return=minimal"})
    urllib.request.urlopen(req, timeout=60).read()
    print("recorded the publish")
    sys.exit(0)

rows = get("cms_edits", "select=kind,o,t,scope&order=id.asc")
edits = [{"o": r["o"], "t": r["t"], "scope": r["scope"] or "*"} for r in rows if r["kind"] == "text"]
images = []
os.makedirs(MEDIA, exist_ok=True)
for r in rows:
    if r["kind"] != "image":
        continue
    t = r["t"]
    if t.startswith("http"):
        name = re.sub(r"[^\w.-]+", "-", urllib.parse.unquote(t.split("?")[0].rsplit("/", 1)[-1])).strip("-") or "photo.jpg"
        local = os.path.join(MEDIA, name)
        if not os.path.exists(local):
            with urllib.request.urlopen(t, timeout=120) as resp, open(local, "wb") as f:
                f.write(resp.read())
        t = "/assets/cms/" + name
    images.append({"o": r["o"], "t": t, "scope": r["scope"] or "*"})

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"edits": edits, "images": images}, f, ensure_ascii=False, indent=1)
print(f"pulled {len(edits)} word changes and {len(images)} photo changes")
