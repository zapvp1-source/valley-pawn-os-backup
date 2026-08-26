#!/usr/bin/env python3
"""Weekly website health crawl for thevalleypawn.com.
Writes a JSON scan result next to this script's parent folder.
Stdlib only. Run on the Mac host.
"""
import json, re, sys, time, urllib.request, urllib.error
from html.parser import HTMLParser
from datetime import date

BASE = "https://thevalleypawn.com"
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1")
OUT = "/Users/joshuadavis/Documents/Claude/Projects/Website/AUDIT_2026-08-22/weekly_scan_%s.json" % date.today().isoformat()

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read() if e.fp else b"", {}
    except Exception as e:
        return -1, str(e).encode(), {}

# --- sitemap ---
urls = []
for sm in ("/sitemap-1.xml", "/sitemap_index.xml", "/sitemap.xml"):
    st, body, _ = fetch(BASE + sm)
    if st == 200:
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body.decode("utf-8", "replace"))
        if sm != "/sitemap-1.xml" and any(l.endswith(".xml") for l in locs):
            # index: expand sub-sitemaps
            sub = []
            for l in locs:
                st2, b2, _ = fetch(l)
                if st2 == 200:
                    sub += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", b2.decode("utf-8", "replace"))
            locs = [l for l in sub if not l.endswith(".xml")]
        urls = [l for l in locs if not l.endswith(".xml")]
        if urls:
            sitemap_used = sm
            break
if not urls:
    json.dump({"error": "no sitemap urls"}, open(OUT, "w"))
    sys.exit(1)
urls = sorted(set(urls))

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""; self.in_title = False
        self.meta_desc = None; self.robots = None; self.canonical = None
        self.jsonld = []; self.in_jsonld = False; self.cur = []
        self.tel = 0; self.sms = 0; self.mailto = 0
        self.h1 = 0
        self.in_script = 0; self.in_style = 0
        self.text = []
        self.assets = set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title": self.in_title = True
        elif tag == "meta":
            n = (a.get("name") or "").lower()
            if n == "description" and self.meta_desc is None: self.meta_desc = a.get("content") or ""
            elif n == "robots": self.robots = a.get("content") or ""
        elif tag == "link":
            rel = (a.get("rel") or "").lower()
            if "canonical" in rel: self.canonical = a.get("href")
            if "stylesheet" in rel and a.get("href"): self.assets.add(a["href"])
        elif tag == "script":
            self.in_script += 1
            if (a.get("type") or "").lower() == "application/ld+json":
                self.in_jsonld = True; self.cur = []
            if a.get("src"): self.assets.add(a["src"])
        elif tag == "style": self.in_style += 1
        elif tag == "img":
            if a.get("src"): self.assets.add(a["src"])
        elif tag == "a":
            h = (a.get("href") or "").lower()
            if h.startswith("tel:"): self.tel += 1
            elif h.startswith("sms:"): self.sms += 1
            elif h.startswith("mailto:"): self.mailto += 1
        elif tag == "h1": self.h1 += 1
    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
        elif tag == "script":
            self.in_script = max(0, self.in_script - 1)
            if self.in_jsonld:
                self.jsonld.append("".join(self.cur)); self.in_jsonld = False
        elif tag == "style": self.in_style = max(0, self.in_style - 1)
    def handle_data(self, d):
        if self.in_title: self.title += d
        if self.in_jsonld: self.cur.append(d)
        elif not self.in_script and not self.in_style: self.text.append(d)

pages = []
errors = []
for u in urls:
    st, body, hdrs = fetch(u)
    if st != 200:
        errors.append({"url": u, "status": st, "note": body[:200].decode("utf-8","replace") if st == -1 else ""})
        pages.append({"url": u, "status": st})
        continue
    html = body.decode("utf-8", "replace")
    p = P()
    try: p.feed(html)
    except Exception as e:
        errors.append({"url": u, "status": 200, "note": "parse: %s" % e})
    ld = []
    for i, blk in enumerate(p.jsonld):
        try:
            json.loads(blk); ld.append({"i": i, "ok": True})
        except Exception as e:
            ld.append({"i": i, "ok": False, "err": str(e), "head": blk.strip()[:300]})
    words = len(re.findall(r"\w+", " ".join(p.text)))
    php_fatal = bool(re.search(r"Fatal error|Uncaught (Error|Exception)|critical error on this website", html))
    pages.append({
        "url": u, "status": st, "title": p.title.strip(),
        "title_len": len(p.title.strip()),
        "brand_twice": p.title.count("Valley Pawn") >= 2,
        "meta_desc": p.meta_desc, "robots": p.robots, "canonical": p.canonical,
        "jsonld": ld, "jsonld_broken": sum(1 for x in ld if not x["ok"]),
        "tel": p.tel, "sms": p.sms, "mailto": p.mailto,
        "h1": p.h1, "words": words, "html_bytes": len(body),
        "php_fatal": php_fatal,
        "assets": sorted(p.assets)[:120],
    })
    time.sleep(0.15)

# --- page-weight sample (HTML + assets) ---
def weight(page):
    total = page.get("html_bytes", 0)
    seen = set()
    for a in page.get("assets", []):
        if a.startswith("//"): a = "https:" + a
        elif a.startswith("/"): a = BASE + a
        if not a.startswith("http") or a in seen: continue
        seen.add(a)
        st, b, _ = fetch(a, timeout=20)
        if st == 200: total += len(b)
    return round(total / 1024)

by_url = {pg["url"].rstrip("/") + "/": pg for pg in pages if pg.get("status") == 200}
sample_urls = []
def pick(pred):
    for k in sorted(by_url):
        if pred(k): return k
    return None
home = BASE + "/"
loc = pick(lambda k: "/locations/" in k and k != BASE + "/locations/")
gold = pick(lambda k: "/sell-gold-" in k)
shop = pick(lambda k: k == BASE + "/shop/")
blog = pick(lambda k: re.search(r"/(how-|why-|what-|pawn-shop-|top-)", k))
weights = {}
for name, k in [("home", home), ("location", loc), ("sell_gold_city", gold), ("shop", shop), ("blog", blog)]:
    if k and k in by_url:
        weights[name] = {"url": k, "kb": weight(by_url[k])}

ok = [pg for pg in pages if pg.get("status") == 200]
indexable = [pg for pg in ok if "noindex" not in ((pg.get("robots") or "").lower())]
metrics = {
    "sitemap": sitemap_used, "total_pages": len(urls),
    "ok_200": len(ok), "errors_4xx_5xx": [{"url": e["url"], "status": e["status"]} for e in errors if e.get("status") != 200],
    "indexable": len(indexable),
    "zero_tel_pages": [pg["url"] for pg in ok if pg["tel"] == 0],
    "indexable_missing_meta_desc": [pg["url"] for pg in indexable if not (pg.get("meta_desc") or "").strip()],
    "broken_jsonld_pages": [{"url": pg["url"], "errs": [x for x in pg["jsonld"] if not x["ok"]]} for pg in ok if pg["jsonld_broken"]],
    "zero_h1_pages": [pg["url"] for pg in ok if pg["h1"] == 0],
    "multi_h1_pages": [pg["url"] for pg in ok if pg["h1"] > 1],
    "titles_over_62": [pg["url"] for pg in ok if pg["title_len"] > 62],
    "brand_twice_titles": [pg["url"] for pg in ok if pg["brand_twice"]],
    "php_fatal_pages": [pg["url"] for pg in ok if pg["php_fatal"]],
    "avg_sample_weight_kb": round(sum(w["kb"] for w in weights.values()) / len(weights)) if weights else None,
    "sample_weights": weights,
}
json.dump({"date": date.today().isoformat(), "metrics": metrics,
           "pages": [{k: v for k, v in pg.items() if k != "assets"} for pg in pages]},
          open(OUT, "w"), indent=1)
print("WROTE", OUT)
print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in metrics.items() if k != "sample_weights"}, indent=1))
