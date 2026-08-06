#!/usr/bin/env python3
import re, json, os, subprocess, sys, html as H

BASE = "/Users/joshuadavis/Documents/Claude/Projects/Website/shop-build"
RAW  = os.path.join(BASE, "raw")
os.makedirs(RAW, exist_ok=True)

STORES = [
    ("Culpeper",      "vpculpeper"),
    ("Waynesboro",    "valleypawnwaynesboro"),
    ("Harrisonburg",  "valleypawnharrisonburg"),
    ("Lexington",     "valleypawnlexington"),
    ("Roanoke",       "valleypawnroanoke"),
]
COLORS = {"Culpeper":"#0099DD","Waynesboro":"#2D1A5E","Harrisonburg":"#E07A5F",
          "Lexington":"#3DB8E8","Roanoke":"#2A9D8F"}

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

def fetch(url, path):
    cmd = ["curl","-sL","--compressed","-m","60","-A",UA,
           "-H","Accept: text/html,*/*;q=0.8",
           "-H","Accept-Language: en-US,en;q=0.9",
           "-H","Upgrade-Insecure-Requests: 1",
           "-H","Sec-Fetch-Dest: document",
           "-H","Sec-Fetch-Mode: navigate",
           "-H","Sec-Fetch-Site: none",
           "-H","Sec-Fetch-User: ?1",
           url,"-o",path]
    subprocess.run(cmd, check=False)
    try:
        return open(path, encoding="utf-8", errors="ignore").read()
    except Exception:
        return ""

RE_ID    = re.compile(r'ebay\.com/itm/(\d+)')
RE_IMG   = re.compile(r'imageId=([A-Za-z0-9~_\-]+)')
RE_TITLE = re.compile(r'str-item-card__property-title.*?<span class=str-text-span[^>]*>(.*?)</span>', re.S)
RE_ALT   = re.compile(r'aria-label="([^"]+)"[^>]*class=str-item-card__link')
RE_PRICE = re.compile(r'str-item-card__property-displayPrice"?>([^<]+)<')
RE_PRICE_OK = re.compile(r'^\$[\d,]+\.?\d*$')

def parse(page_html, store):
    out = []
    chunks = page_html.split('<article')
    for ch in chunks[1:]:
        ch = ch.split('</article>')[0]
        if 'str-item-card' not in ch: continue
        m = RE_ID.search(ch)
        if not m: continue
        iid = m.group(1)
        mi = RE_IMG.search(ch)
        if not mi: continue
        img = mi.group(1)
        mt = RE_TITLE.search(ch)
        title = H.unescape(mt.group(1)).strip() if mt else ""
        if not title:
            ma = RE_ALT.search(ch)
            title = H.unescape(ma.group(1)).strip() if ma else ""
        title = re.sub(r'\s*Opens in a new window or tab\s*','',title)
        title = re.sub(r'\s+',' ',title).strip()
        mp = RE_PRICE.search(ch)
        price = H.unescape(mp.group(1)).strip() if mp else ""
        if not (title and price and img): continue
        if not RE_PRICE_OK.match(price): continue
        if re.search(r'Shop on eBay', title, re.I): continue
        out.append({"t":title,"p":price,
                    "u":"https://www.ebay.com/itm/"+iid,
                    "img":"https://i.ebayimg.com/images/g/%s/s-l500.webp"%img,
                    "s":store})
    return out

def main():
    seen = set(); items = []; counts = {}
    for name, slug in STORES:
        got = 0
        for pgn in range(1, 9):
            url = "https://www.ebay.com/str/%s?_pgn=%d&_ipg=240&_tab=shop" % (slug, pgn)
            path = os.path.join(RAW, "%s_%d.html" % (slug, pgn))
            html_txt = fetch(url, path)
            if len(html_txt) < 50000:
                print("WARN %s pg%d short=%d" % (name, pgn, len(html_txt)), flush=True)
                break
            parsed = parse(html_txt, name)
            new = [x for x in parsed if x["u"] not in seen]
            for x in new: seen.add(x["u"])
            items.extend(new)
            got += len(new)
            print("%s pg%d parsed=%d new=%d" % (name, pgn, len(parsed), len(new)), flush=True)
            if len(new) == 0:
                break
        counts[name] = got
    db = {"colors": COLORS, "items": items}
    with open(os.path.join(BASE, "items.json"), "w") as f:
        json.dump(db, f)
    print("DONE counts=%s total=%d" % (counts, len(items)), flush=True)

main()
