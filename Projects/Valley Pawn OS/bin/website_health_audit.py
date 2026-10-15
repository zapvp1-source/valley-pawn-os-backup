#!/usr/bin/env python3
"""website_health_audit.py [--render] [--send] [--scan <weekly_scan_*.json>] [--day YYYY-MM-DD]

Native replacement (Mac-first wave 2, 2026-10-14) for the Cowork task `weekly-website-health-audit` (Mon 05:15 ET).
  1 crawl: Website/AUDIT_2026-08-22/bin/weekly_crawl.py (the same stdlib crawler the Cowork run used) ->
    weekly_scan_<today>.json. --render with --scan reuses a saved scan and crawls nothing.
  2 auto-fix (SKILL rule 2, additive only): an INDEXABLE page with no meta description gets one ONLY if it is a
    commercial/customer page (Claude classifies title+URL+size; utility/data/QR/link-in-bio pages are flagged for
    Joshua instead, never auto-written or noindexed). Never overwrites an existing description (re-read via REST
    context=edit first). Written via WPCode 1135's _yoast_wpseo_metadesc REST field, 116-163 chars, ends in a
    period. Broken JSON-LD is FLAGGED, never guessed at. Body copy, clusters, footer: never touched.
  3 every fix verified on the LIVE page (cache-busted re-fetch, CDN-lag aware) before it is counted.
  4 metrics in the baseline's definitions, appended to weekly-history.json (one entry per date; re-run replaces it)
  5 digest to #website (C0ASE9C0GQ0), the 10/5 layout; posted every week, clean run or not
  6 CHANGELOG entry; OPEN_ITEMS_REGISTER row when something was auto-fixed or needs Joshua
Duplicate guard: a "Weekly Website Health Audit — <date>" post already in #website today = no second post.
--render prints the digest and writes nothing (no WP writes, no history, no post).
"""
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vp_ai  # noqa: E402
import vp_slack  # noqa: E402

TASK = "weekly-website-health-audit"
ET = ZoneInfo("America/New_York")
PROJ = os.path.expanduser("~/Documents/Claude/Projects")
AUD = os.path.join(PROJ, "Website/AUDIT_2026-08-22")
HIST = os.path.join(AUD, "weekly-history.json")
CRAWL = os.path.join(AUD, "bin/weekly_crawl.py")
OS_DIR = os.path.dirname(HERE)
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
CHANGELOG = os.path.join(OS_DIR, "CHANGELOG.md")
OPEN_ITEMS = os.path.join(PROJ, "Life OS/OPEN_ITEMS_REGISTER.md")
CH = "C0ASE9C0GQ0"
BASE = "https://thevalleypawn.com"
sys.path.insert(0, os.path.join(PROJ, "Website/analytics/bin"))


def ledger(sentence):
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), TASK, sentence))


def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


def md(d):
    return "%d/%d" % (d.month, d.day)


def path_of(url):
    return url.replace(BASE, "") or "/"


def metrics_of(scan):
    m = scan["metrics"]
    sw = m.get("sample_weights") or {}
    return {"total_pages_in_sitemap": m["total_pages"], "ok_200": m["ok_200"], "errors_4xx_5xx": len(m["errors_4xx_5xx"]),
            "indexable_pages": m["indexable"], "noindex_pages": m["ok_200"] - m["indexable"],
            "zero_tel_pages": len(m["zero_tel_pages"]), "indexable_missing_meta_description": len(m["indexable_missing_meta_desc"]),
            "broken_jsonld_pages": len(m["broken_jsonld_pages"]), "zero_h1_pages": len(m["zero_h1_pages"]),
            "titles_over_62_chars": len(m["titles_over_62"]), "brand_twice_titles": len(m["brand_twice_titles"]),
            "avg_sample_page_weight_kb": m.get("avg_sample_weight_kb"),
            "sample_weights_kb": {k: v["kb"] for k, v in sw.items()}}


def prior_scan(day):
    best = None
    for p in glob.glob(os.path.join(AUD, "weekly_scan_*.json")):
        d = os.path.basename(p)[12:22]
        if d < day.isoformat() and (best is None or d > best[0]):
            best = (d, p)
    return (best[0], json.load(open(best[1]))) if best else (None, None)


def classify(pages):
    """Claude: commercial page that deserves a description, or a utility/data page that needs Joshua's call."""
    if not pages:
        return {}
    items = [{"url": p["url"], "title": p.get("title"), "words": p.get("words"), "h1": p.get("h1"), "tel": p.get("tel")} for p in pages]
    out = vp_ai.ask_json(
        "For each page of thevalleypawn.com (a pawn shop website) say whether it is a normal customer-facing page/blog "
        "post that should have a search description (\"commercial\"), or a machine/utility page — a raw data feed, "
        "widget endpoint, QR/link-in-bio page, default WordPress content, test page — that a person should decide "
        "about (\"utility\"). Answer JSON {\"<url>\": \"commercial\"|\"utility\"}.\n" + json.dumps(items), max_tokens=3000)
    return {u: (v if v in ("commercial", "utility") else "utility") for u, v in out.items()}


def write_desc(page, examples):
    sys_ = ("You write meta descriptions for Valley Pawn (thevalleypawn.com), a family-owned pawn shop with five Virginia "
            "stores. Same voice as the site's existing descriptions. Rules: 116-163 characters; lead with the offer; include "
            "a call to action (call or text, visit, stop in); end with a period; plain words; never 'Dixie Pawn', 'Full "
            "Circle Finance', firearms, 'no credit check', invented prices or claims beyond the page title. Output ONLY the description.")
    for _ in range(3):
        d = vp_ai.ask("Existing descriptions on the site:\n- " + "\n- ".join(examples) +
                      "\n\nWrite the description for this page.\nURL: %s\nTitle: %s" % (page["url"], page.get("title")), system=sys_, max_tokens=1500).strip().strip('"')
        if 116 <= len(d) <= 163 and d.endswith("."):
            return d
    return None


def find_post(wp, slug):
    for kind in ("pages", "posts"):
        st, j = wp.get_json("/wp/v2/%s?slug=%s&context=edit&_fields=id,meta,link" % (kind, slug))
        if st == 200 and isinstance(j, list) and j:
            return kind, j[0]
    return None, None


def apply_fix(page, desc):
    from wp_client import WP
    wp = WP()
    slug = path_of(page["url"]).strip("/").split("/")[-1]
    kind, post = find_post(wp, slug)
    if not post:
        return {"ok": False, "why": "no WP page/post for slug %s" % slug}
    cur = ((post.get("meta") or {}).get("_yoast_wpseo_metadesc") or "").strip()
    if cur:
        return {"ok": False, "why": "already has a description in WordPress (not overwritten)", "id": post["id"]}
    st, body = wp._req("/wp/v2/%s/%d" % (kind, post["id"]), method="POST",
                       data=json.dumps({"meta": {"_yoast_wpseo_metadesc": desc}}).encode(), headers={"Content-Type": "application/json"})
    if st != 200:
        return {"ok": False, "why": "REST write HTTP %s" % st, "id": post["id"]}
    import html as H
    ok, _ = wp.wait_live(path_of(page["url"]), lambda h: H.escape(desc[:60], quote=True) in h or desc[:60] in h, tries=9, delay=20)
    return {"ok": ok, "why": "" if ok else "written but not visible on the live page yet", "id": post["id"], "kind": kind}


def history():
    try:
        return json.load(open(HIST))
    except (OSError, ValueError):
        return []


def delta(a, b, unit=""):
    if a is None or b is None:
        return "%s%s" % (b, unit)
    if a == b:
        return "%s%s → %s%s (steady)" % (a, unit, b, unit)
    return "%s%s → %s%s (%+d)" % (a, unit, b, unit, b - a)


def main():
    render = "--render" in sys.argv
    send = "--send" in sys.argv and not render
    day = dt.date.fromisoformat(arg("--day")) if arg("--day") else dt.datetime.now(ET).date()
    if arg("--scan"):
        scan = json.load(open(arg("--scan")))
        day = dt.date.fromisoformat(scan["date"])
    else:
        if not send:
            print("render needs --scan <weekly_scan_*.json> (no live crawl in render)")
            return 2
        p = subprocess.run(["/usr/bin/python3", CRAWL], capture_output=True, text=True, timeout=3600)
        print(p.stdout[-1500:], p.stderr[-500:])
        f = os.path.join(AUD, "weekly_scan_%s.json" % day)
        if p.returncode != 0 or not os.path.exists(f):
            ledger("Weekly website crawl did not finish, so no health audit posted this week.")
            return 1
        scan = json.load(open(f))
    m = scan["metrics"]
    hist = [h for h in history() if h.get("date") != day.isoformat()]
    prev = max((h for h in hist if h.get("date", "") < day.isoformat()), key=lambda h: h["date"], default=None)
    pm = (prev or {}).get("metrics", {})
    pdate = dt.date.fromisoformat(prev["date"]) if prev else None
    cur = metrics_of(scan)
    pd, pscan = prior_scan(day)
    prev_urls = {pg["url"] for pg in (pscan or {}).get("pages", [])}
    pages = {pg["url"]: pg for pg in scan["pages"]}
    new_urls = sorted(u for u in pages if prev_urls and u not in prev_urls)
    flagged_before = " ".join(" ".join(h.get("new_issues_found", [])) for h in hist)

    # 2 auto-fix candidates
    missing = [pages[u] for u in m["indexable_missing_meta_desc"] if u in pages]
    kinds = classify(missing) if missing else {}
    examples = [pg["meta_desc"] for pg in scan["pages"] if (pg.get("meta_desc") or "") and 116 <= len(pg["meta_desc"]) <= 163][:6]
    fixes, decisions, still_open = [], [], []
    for pg in missing:
        u = pg["url"]
        if kinds.get(u) != "commercial":
            (still_open if path_of(u) in flagged_before else decisions).append(
                "%s is indexable with no search description and looks like a behind-the-scenes/utility page, not a customer page — hide it from search, or is it meant to be public?" % path_of(u))
            continue
        desc = write_desc(pg, examples)
        if not desc:
            decisions.append("%s is missing a search description and I couldn't write one that met the length rule — needs a hand-written one." % path_of(u))
            continue
        if render:
            fixes.append({"page": u, "what": "WOULD add missing meta description", "before": "(empty)", "after": desc, "verified_live": None})
            continue
        r = apply_fix(pg, desc)
        if r["ok"]:
            fixes.append({"page": u, "what": "Added missing meta description (WP %s %s, via Yoast REST field)" % (r.get("kind", "post")[:-1], r.get("id")),
                          "before": "(empty)", "after": desc, "verified_live": True})
        else:
            decisions.append("%s is missing a search description; the automatic fix did not land (%s)." % (path_of(u), r["why"]))
    for b in m["broken_jsonld_pages"]:
        decisions.append("%s has page data (structured data) that no longer parses — flagged, not auto-edited." % path_of(b["url"]))
    for e in m["errors_4xx_5xx"]:
        decisions.append("%s returned an error (%s) during the crawl." % (path_of(e["url"]), e["status"]))
    for u in m["php_fatal_pages"]:
        decisions.append("%s shows a site error message on the live page." % path_of(u))

    # 4 history entry
    new_issues = ["New page since %s: '%s' (%s words, %s)" % (md(pdate) if pdate else "last run", path_of(u), pages[u].get("words"),
                  "has a description" if (pages[u].get("meta_desc") or "").strip() else "no description") for u in new_urls]
    entry = {"date": day.isoformat(), "metrics": cur, "auto_fixes": fixes, "new_issues_found": new_issues + decisions,
             "still_open_from_baseline": (prev or {}).get("still_open_from_baseline", []), "source": "native website_health_audit.py"}

    # metric is the POST-fix count, as the live runs record it (10/12: 2 missing, 1 fixed -> 1)
    cur["indexable_missing_meta_description"] -= len(fixes)
    entry["metrics"] = cur
    # 5 digest (10/5 layout)
    clean = not fixes and not decisions and all(cur.get(k) == pm.get(k) for k in
            ("indexable_missing_meta_description", "broken_jsonld_pages", "zero_tel_pages", "errors_4xx_5xx"))
    L = ["*Weekly Website Health Audit — %s*" % day.strftime("%a %b %-d, %Y"), ""]
    if clean:
        L += ["Clean run, no changes needed. Everything flagged in prior runs stayed fixed.", ""]
    L.append("Week-over-week (vs %s):" % (md(pdate) if pdate else "first run"))
    tp = cur["total_pages_in_sitemap"] - pm.get("total_pages_in_sitemap", cur["total_pages_in_sitemap"])
    newtxt = ""
    if new_urls:
        newtxt = " — new: " + ", ".join(path_of(u) for u in new_urls[:4]) + (" +%d more" % (len(new_urls) - 4) if len(new_urls) > 4 else "")
    L.append("• Pages in sitemap: %s%s" % (delta(pm.get("total_pages_in_sitemap"), cur["total_pages_in_sitemap"]), newtxt if tp or new_urls else ""))
    L.append("• Broken/unparseable JSON-LD: %s" % delta(pm.get("broken_jsonld_pages"), cur["broken_jsonld_pages"]))
    L.append("• Indexable pages missing a meta description: %s%s" % (delta(pm.get("indexable_missing_meta_description"), cur["indexable_missing_meta_description"]),
             (" — after %d auto-fixed this run" % len(fixes)) if fixes else ""))
    L.append("• Pages with zero click-to-call links: %s" % delta(pm.get("zero_tel_pages"), cur["zero_tel_pages"]))
    L.append("• Zero-H1 pages: %s" % delta(pm.get("zero_h1_pages"), cur["zero_h1_pages"]))
    L.append("• Titles over 62 chars: %s" % delta(pm.get("titles_over_62_chars"), cur["titles_over_62_chars"]))
    L.append("• 404s/5xxs hit during crawl: %d" % cur["errors_4xx_5xx"])
    a, b = pm.get("avg_sample_page_weight_kb"), cur["avg_sample_page_weight_kb"]
    L.append("• Avg sampled page weight: %sKB → %sKB%s" % (a, b, (" (%+dKB)" % (b - a)) if a is not None and b is not None else ""))
    L += ["", "Auto-fixed this run: nothing — no new issues in the auto-fixable categories." if not fixes else "Auto-fixed this run:"]
    for f in fixes:
        L.append("• %s — added a search description%s: \"%s\"" % (path_of(f["page"]), " (verified live)" if f["verified_live"] else "", f["after"]))
    for u in new_urls:
        pg = pages[u]
        idx = "noindex" not in (pg.get("robots") or "").lower()
        L += ["", "New this week: %s — %s, %s, %d H1, %s, %d tel links." % (path_of(u), "indexed" if idx else "noindex",
              "has a description" if (pg.get("meta_desc") or "").strip() else "no description", pg.get("h1") or 0,
              "valid schema" if not pg.get("jsonld_broken") else "BROKEN schema", pg.get("tel") or 0)]
    if decisions:
        L += ["", "Needs a decision:"] + ["• " + d for d in decisions]
    if still_open:
        L += ["", "Still open from earlier runs:"] + ["• " + d for d in still_open]
    L += ["", "Full metrics in weekly-history.json."]
    text = "\n".join(L)
    print("=== POST %s\n%s" % (CH, text))
    if not send:
        return 0
    json.dump(hist + [entry], open(HIST, "w"), indent=1)
    if vp_slack.has(CH, "Weekly Website Health Audit — %s" % day.strftime("%a %b %-d, %Y"), 20):
        print("already posted today")
    else:
        os.environ["VP_TASK"] = TASK
        vp_slack.post(CH, text)
    note = ("## %s (weekly-website-health-audit, native)\n\n- Crawled %d sitemap pages (%d indexable), %d errors, %d broken JSON-LD, "
            "%d missing descriptions (%d auto-fixed and verified live), %d new pages since %s. Digest posted to #website. History: "
            "`Website/AUDIT_2026-08-22/weekly-history.json`.%s\n\n" % (day, cur["total_pages_in_sitemap"], cur["indexable_pages"],
            cur["errors_4xx_5xx"], cur["broken_jsonld_pages"], cur["indexable_missing_meta_description"], len(fixes), len(new_urls),
            md(pdate) if pdate else "-", (" Needs Joshua: " + " ".join(decisions)) if decisions else ""))
    txt = open(CHANGELOG).read()
    i = txt.find("\n## ")
    open(CHANGELOG, "w").write(txt[:i + 1] + note + txt[i + 1:] if i >= 0 else txt + "\n" + note)
    if fixes or decisions:
        with open(OPEN_ITEMS, "a") as f:
            f.write("| %s | 1 — Valley Pawn | **weekly-website-health-audit (native):** %s%s | OPEN | Review in #website digest %s |\n" % (
                day, ("auto-fixed: " + "; ".join("%s meta description" % path_of(x["page"]) for x in fixes) + ". ") if fixes else "",
                ("needs a decision: " + " ".join(decisions)) if decisions else "", day))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        if "--send" in sys.argv:
            ledger("Weekly website health audit did not complete (%s)." % type(e).__name__)
        print("ERROR", type(e).__name__, e)
        sys.exit(1)
