#!/usr/bin/env python3
"""Fetch one store's eBay inventory via the storefront endpoint. Usage: fetch_store.py <StoreName> <slug>
Writes parts/<StoreName>.json = [{t,p,u,img,s}, ...]"""
import re, json, time, urllib.request, http.cookiejar, sys, os

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    })
    with opener.open(req, timeout=25) as r:
        return r.read().decode("utf-8", "ignore")

TITLE_RE = re.compile(r'str-item-card__property-title[^>]*>.*?class=[\'"]?str-text-span[^>]*>([^<]*)<', re.S)
PRICE_RE = re.compile(r'str-item-card__property-displayPrice[^>]*>([^<]*)<')
ITEM_RE = re.compile(r'ebay\.com/itm/(\d+)')
IMG_RE = re.compile(r'imageId=([A-Za-z0-9~_-]+)')

def parse_articles(html_text):
    chunks = html_text.split('<article')
    items = []
    for c in chunks:
        if 'str-item-card' not in c:
            continue
        m_id = ITEM_RE.search(c)
        m_title = TITLE_RE.search(c)
        m_price = PRICE_RE.search(c)
        m_img = IMG_RE.search(c)
        if not (m_id and m_title and m_price):
            continue
        title = m_title.group(1).strip()
        price = m_price.group(1).strip()
        if not re.match(r'^\$[\d,]+\.?\d*$', price):
            continue
        img = f"https://i.ebayimg.com/images/g/{m_img.group(1)}/s-l500.webp" if m_img else ""
        items.append({"id": m_id.group(1), "t": title, "p": price,
                       "u": f"https://www.ebay.com/itm/{m_id.group(1)}", "img": img})
    return items

def fetch_page_with_retry(url, label, tries=4):
    for attempt in range(1, tries + 1):
        try:
            html_text = fetch(url)
        except Exception as e:
            print(f"{label} ERROR (attempt {attempt}): {e}", file=sys.stderr, flush=True)
            time.sleep(3 * attempt)
            continue
        parsed = parse_articles(html_text)
        if parsed:
            return parsed
        print(f"{label} 0 items attempt {attempt} len={len(html_text)} -- retrying", file=sys.stderr, flush=True)
        time.sleep(4 * attempt)
    return []

def main():
    name, slug = sys.argv[1], sys.argv[2]
    seen_ids = set()
    store_items = []
    for pgn in range(1, 6):
        url = f"https://www.ebay.com/str/{slug}?_pgn={pgn}&_ipg=240&_tab=shop"
        label = f"{name} page {pgn}"
        parsed = fetch_page_with_retry(url, label)
        new = [i for i in parsed if i["id"] not in seen_ids]
        if not new:
            print(f"{label}: 0 new, stop", file=sys.stderr, flush=True)
            break
        for i in new:
            seen_ids.add(i["id"])
            store_items.append(i)
        print(f"{label}: +{len(new)} (total {len(store_items)})", file=sys.stderr, flush=True)
        if len(parsed) < 200:
            break
        time.sleep(2)
    os.makedirs("parts", exist_ok=True)
    out = [{"t": i["t"], "p": i["p"], "u": i["u"], "img": i["img"], "s": name} for i in store_items]
    with open(f"parts/{name}.json", "w") as f:
        json.dump(out, f)
    print(f"DONE {name}: {len(out)}", flush=True)

if __name__ == "__main__":
    main()
