#!/usr/bin/env python3
import re, json, os, subprocess, html as H, time
WORK = '/tmp/vp-shop-run'
RAW = WORK + '/raw'
CJ = WORK + '/cookiejar.txt'
os.makedirs(RAW, exist_ok=True)
if os.path.exists(CJ):
    try:
        os.remove(CJ)
    except Exception:
        open(CJ, 'w').close()
STORES = [
    ('Culpeper', 'vpculpeper'),
    ('Waynesboro', 'valleypawnwaynesboro'),
    ('Harrisonburg', 'valleypawnharrisonburg'),
    ('Lexington', 'valleypawnlexington'),
    ('Roanoke', 'valleypawnroanoke'),
]
COLORS = {'Culpeper':'#0099DD','Waynesboro':'#2D1A5E','Harrisonburg':'#E07A5F','Lexington':'#3DB8E8','Roanoke':'#2A9D8F'}
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
Q = chr(34)

def fetch(url, path, referer):
    cmd = ['curl','-sL','--compressed','-m','60','-c',CJ,'-b',CJ,'-A',UA,
           '-H','Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           '-H','Accept-Language: en-US,en;q=0.9',
           '-H','Upgrade-Insecure-Requests: 1',
           '-H','Referer: ' + referer,
           '-H','Sec-Fetch-Dest: document',
           '-H','Sec-Fetch-Mode: navigate',
           '-H','Sec-Fetch-Site: same-origin',
           '-H','Sec-Fetch-User: ?1',
           url,'-o',path]
    subprocess.run(cmd, check=False)
    try:
        return open(path, encoding='utf-8', errors='ignore').read()
    except Exception:
        return ''

RE_ID = re.compile('ebay\\.com/itm/(\\d+)')
RE_IMG = re.compile('imageId=([A-Za-z0-9~_\\-]+)')
RE_TITLE = re.compile('str-item-card__property-title.*?<span class=str-text-span[^>]*>(.*?)</span>', re.S)
RE_ALT = re.compile('aria-label=' + Q + '([^' + Q + ']+)' + Q + '[^>]*class=str-item-card__link')
RE_PRICE = re.compile('str-item-card__property-displayPrice' + Q + '?>([^<]+)<')
RE_PRICE_OK = re.compile('^\\$[\\d,]+\\.?\\d*$')

def parse(page_html, store):
    out = []
    chunks = page_html.split('<article')
    for ch in chunks[1:]:
        ch = ch.split('</article>')[0]
        if 'str-item-card' not in ch:
            continue
        m = RE_ID.search(ch)
        if not m:
            continue
        iid = m.group(1)
        mi = RE_IMG.search(ch)
        if not mi:
            continue
        img = mi.group(1)
        mt = RE_TITLE.search(ch)
        title = H.unescape(mt.group(1)).strip() if mt else ''
        if not title:
            ma = RE_ALT.search(ch)
            title = H.unescape(ma.group(1)).strip() if ma else ''
        title = re.sub('\\s*Opens in a new window or tab\\s*', '', title)
        title = re.sub('\\s+', ' ', title).strip()
        mp = RE_PRICE.search(ch)
        price = H.unescape(mp.group(1)).strip() if mp else ''
        if not (title and price and img):
            continue
        if not RE_PRICE_OK.match(price):
            continue
        if re.search('Shop on eBay', title, re.I):
            continue
        out.append({'t':title,'p':price,'u':'https://www.ebay.com/itm/'+iid,'img':'https://i.ebayimg.com/images/g/'+img+'/s-l500.webp','s':store})
    return out

def main():
    fetch('https://www.ebay.com/', RAW + '/_warmup.html', 'https://www.google.com/')
    time.sleep(2)
    seen = set()
    items = []
    counts = {}
    referer = 'https://www.ebay.com/'
    for name, slug in STORES:
        got = 0
        for pgn in range(1, 9):
            url = 'https://www.ebay.com/str/' + slug + '?_pgn=' + str(pgn) + '&_ipg=240&_tab=shop'
            path = RAW + '/' + slug + '_' + str(pgn) + '.html'
            html_txt = fetch(url, path, referer)
            referer = url
            if len(html_txt) < 50000:
                print('WARN short retry')
                time.sleep(6)
                html_txt = fetch(url, path, referer)
                if len(html_txt) < 50000:
                    print('WARN still short giving up')
                    break
            parsed = parse(html_txt, name)
            new = [x for x in parsed if x['u'] not in seen]
            for x in new:
                seen.add(x['u'])
            items.extend(new)
            got += len(new)
            print(name + ' pg' + str(pgn) + ' parsed=' + str(len(parsed)) + ' new=' + str(len(new)))
            if len(new) == 0:
                break
            time.sleep(2.5)
        counts[name] = got
        time.sleep(3)
    db = {'colors': COLORS, 'items': items}
    with open(WORK + '/items.json', 'w') as f:
        json.dump(db, f)
    print('DONE counts=' + str(counts) + ' total=' + str(len(items)))

main()
