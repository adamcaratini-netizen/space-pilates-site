#!/usr/bin/env python3
"""Site integrity checks, run at the end of tools/build-pages.py (or on their own).
Exits non-zero on any failure so a broken build is never deployed by accident."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_PAGES = {"mariana-tools.html", "book-a-call.html", "waiver.html", "about.html"}
BANNED = r"\b(burn|burns|burning|crush|crushing|hustle|torch|shred|shredded|toned|slim|slimming|bikini|lose weight|weight loss|burn fat|fat burning|earn your body|sweat it out|beast mode)\b"
CLAIMS = r"(\d+\s?%|\bstudies show\b|\bresearch shows\b|\bscientifically proven\b|\bclinically proven\b|\bcures?\b|\bheals?\b)"

errors = []
vercel = json.loads((ROOT / "vercel.json").read_text())
redirect_srcs = {r["src"] for r in vercel["routes"] if r.get("status") in (301, 302, 308)}


def no_dup_keys(pairs):
    # json.loads keeps the LAST of two equal keys without a word, so a second "sameAs" silently
    # replaced the studio's real social links on the home page until 2026-10-21.
    keys = [k for k, _ in pairs]
    dups = sorted({k for k in keys if keys.count(k) > 1})
    if dups:
        raise ValueError(f"duplicate key(s) {dups}")
    return dict(pairs)


def route_exists(path):
    path = path.split("#")[0].split("?")[0]
    if path in ("", "/"):
        return True
    if path in redirect_srcs or path.startswith("/api/"):
        return True
    # Mirror Vercel: the first route whose src matches wins, and the catch-all serves the path
    # as-is. There is no automatic ".html", so /pilates-x needs its own route or it 404s.
    for r in vercel["routes"]:
        src = re.sub(r"\(\?<(\w+)>", r"(?P<\1>", r["src"])
        m = re.fullmatch(src, path)
        if not m:
            continue
        if r.get("status") or not r.get("dest"):
            if r.get("continue"):
                continue
            return bool(r.get("status"))
        dest = r["dest"]
        for k, val in m.groupdict().items():
            dest = dest.replace(f"${k}", val)
        dest = re.sub(r"\$1", m.group(1) if m.groups() else "", dest)
        return dest.startswith("/api/") or (ROOT / dest.strip("/")).is_file()
    return False


def page_route(f):
    rel = f.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel == "terms-and-conditions.html":
        return "/terms"
    return "/" + rel[:-5]


pages = [f for f in ROOT.rglob("*.html") if "node_modules" not in f.parts and ".git" not in f.parts and f.name not in SKIP_PAGES]
inbound = {}
for f in pages:
    html = f.read_text(errors="ignore")
    me = page_route(f)
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            json.loads(block, object_pairs_hook=no_dup_keys)
        except (json.JSONDecodeError, ValueError) as e:
            errors.append(f"{me}: invalid JSON-LD ({e})")
    if "/_vercel/insights/script.js" not in html:
        errors.append(f"{me}: missing Vercel Web Analytics tag")
    if "data-space-events" not in html:
        errors.append(f"{me}: missing conversion events script")
    for href in set(re.findall(r'href="(/[^"]*)"', html)):
        if href.startswith("//"):
            continue
        if not route_exists(href):
            errors.append(f"{me}: broken internal link {href}")
        target = href.split("#")[0].split("?")[0].rstrip("/") or "/"
        if target != me:
            inbound.setdefault(target, set()).add(me)

sitemap = [re.sub(r"^https://[^/]+", "", u) or "/" for u in re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text())]
for u in sitemap:
    if not route_exists(u):
        errors.append(f"sitemap: {u} does not resolve")
    if u != "/" and not inbound.get(u):
        errors.append(f"orphan: {u} has no inbound links from any page")

for md in sorted((ROOT / "content" / "learn").glob("*.md")):
    text = md.read_text()
    body = text.split("\n---\n", 1)[-1]
    if "—" in text:
        errors.append(f"{md.name}: contains an em dash")
    for m in re.finditer(BANNED, body, re.I):
        errors.append(f"{md.name}: banned brand word {m.group(0)!r}")
    for m in re.finditer(CLAIMS, body, re.I):
        ctx = body[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
        if not re.search(r"\b(not|never|no|isn't|doesn't|won't|cannot|can't)\b", ctx, re.I):
            errors.append(f"{md.name}: claim needs review {m.group(0)!r}: ...{ctx}...")
    words = len(re.findall(r"[A-Za-z']+", body))
    if words < 700:
        errors.append(f"{md.name}: only {words} words")

if errors:
    print("\nSITE CHECK FAILED:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print(f"\nsite check ok: {len(pages)} pages, {len(sitemap)} sitemap URLs, all linked, all JSON-LD valid")
