#!/usr/bin/env python3
"""
Tier 3 — eBay market valuation (general merchandise).
Goal data = ALL eBay SOLD transactions (Marketplace Insights). Until that app access is approved,
this uses the Browse API (active listings) with title model-matching + outlier trim + a sold-haircut
as a clearly-labeled approximation. The provider interface is identical, so swapping active->sold
later is a one-function change (use_insights=True).

Run: values a real sample of general-merch intake items and prints cost vs eBay estimate.
"""
import re, json, base64, urllib.request, urllib.parse, statistics, time, glob

SRC_CREDS = "/Users/joshuadavis/Documents/valley-pawn/ebay_weekly_rankings.py"
BASE = "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/"
SOLD_HAIRCUT = 0.88  # active asking -> sold approximation; removed once Insights (true sold) is live
STOP = set("THE AND FOR WITH MODEL SERIAL NUMBER NO SIZE COLOR USED NEW ITEM MISC GENT GENTS "
           "LADY LADYS BLACK WHITE BLUE RED GREEN SILVER GOLD".split())
# categories that DON'T go to eBay: precious metals (melt) and firearms (eBay bans gun sales)
SKIP = re.compile(r'GOLD|SILVER|COIN|BULLION|PISTOL|REVOLVER|RIFLE|SHOTGUN|FIREARM|AMMUN|FIREARM PARTS', re.I)

_t = open(SRC_CREDS).read()
APP = re.search(r'APP_ID\s*=\s*"([^"]+)"', _t).group(1)
CERT = re.search(r'CERT_ID\s*=\s*"([^"]+)"', _t).group(1)

def token():
    cred = base64.b64encode(f"{APP}:{CERT}".encode()).decode()
    data = urllib.parse.urlencode({"grant_type":"client_credentials",
        "scope":"https://api.ebay.com/oauth/api_scope"}).encode()
    req = urllib.request.Request("https://api.ebay.com/identity/v1/oauth2/token", data=data,
        headers={"Content-Type":"application/x-www-form-urlencoded","Authorization":f"Basic {cred}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["access_token"]

PARTS = re.compile(r'\b(PART|PARTS|MANUAL|DECAL|STICKER|COVER|CASE|REPLACEMENT|CHARGER|CABLE|'
                   r'PROTECTOR|MOUNT|BRACKET|FILTER|BELT|BLADE|FOR|GENUINE OEM|REPAIR)\b', re.I)
MELT_RE = re.compile(r'\d\s*DWT|\b\d{1,2}\s*K\b|STERLING|14K|10K|18K', re.I)
def toks(s):
    s = re.sub(r'[^A-Z0-9 ]',' ', (s or '').upper())
    return [t for t in s.split() if len(t)>=2 and t not in STOP]
def digits(ts): return [t for t in ts if any(c.isdigit() for c in t)]
def model_keys(ts):  # distinctive model numbers: digit-bearing, length>=3 (drops noise like "20")
    return [t for t in ts if any(c.isdigit() for c in t) and len(t)>=3]

def ebay_estimate(desc, access, use_insights=False):
    """Returns (sold_estimate, n_used, note). use_insights flips to true-sold once app is approved."""
    q_toks = toks(desc)
    mk = model_keys(q_toks)
    # build a focused query: brand/model words + model numbers
    q = " ".join(q_toks[:6])
    if use_insights:
        endpoint = "https://api.ebay.com/buy/marketplace_insights/v1_beta/item_sales/search?"
        key = "itemSales"
    else:
        endpoint = "https://api.ebay.com/buy/browse/v1/item_summary/search?"
        key = "itemSummaries"
    url = endpoint + urllib.parse.urlencode({"q": q, "limit": 50, "filter":"conditions:{USED}"})
    req = urllib.request.Request(url, headers={"Authorization":f"Bearer {access}",
        "X-EBAY-C-MARKETPLACE-ID":"EBAY_US"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
    except Exception as e:
        return None, 0, f"err:{getattr(e,'code',e)}"
    prices=[]
    for it in d.get(key, []):
        title = it.get("title","")
        if PARTS.search(title): continue            # drop parts / accessory / "for <model>" listings
        ttoks = set(toks(title))
        # match: title contains >=1 distinctive model number; else >=2 signature brand/model words
        if mk:
            if not (set(mk) & ttoks): continue
        else:
            sig=[t for t in q_toks if len(t)>=4]
            if len(set(sig) & ttoks) < 2: continue
        p = it.get("price",{}).get("value") or it.get("lastSoldPrice",{}).get("value")
        if p:
            try: prices.append(float(p))
            except: pass
    if len(prices) < 3:
        return None, len(prices), "thin"
    prices.sort()
    lo,hi = int(len(prices)*0.10), int(len(prices)*0.90) or len(prices)
    core = prices[lo:hi] or prices
    med = statistics.median(core)
    est = med if use_insights else round(med*SOLD_HAIRCUT,2)
    return round(est,2), len(core), ("INSIGHTS-sold" if use_insights else f"browse*{SOLD_HAIRCUT}")

def money(x):
    x=(x or '').replace('$','').replace(',','').strip()
    try: return float(x)
    except: return None

def load_merch_sample(n=20):
    rows=[]
    for f in glob.glob(BASE+'2024-*_buys-from-public.csv'):
        with open(f, newline='') as fh:
            for row in __import__('csv').DictReader(fh):
                cat=(row.get('Category') or '')
                amt=money(row.get('Loan Amount'))
                desc=row.get('Full Description') or ''
                if amt is None or SKIP.search(cat): continue
                if MELT_RE.search(desc): continue     # precious-metal/jewelry -> melt engine, not eBay
                if not model_keys(toks(desc)): continue   # need a distinctive model number for clean matching
                rows.append({'cat':cat.strip(),'desc':desc.strip(),'cost':amt})
    rows.sort(key=lambda r:r['cost'], reverse=True)
    # de-dup by description, take top n by cost
    seen=set(); out=[]
    for r in rows:
        k=r['desc'][:40]
        if k in seen: continue
        seen.add(k); out.append(r)
        if len(out)>=n: break
    return out

def main():
    acc = token()
    sample = load_merch_sample(20)
    print(f"Tier-3 eBay valuation on {len(sample)} real general-merch intake items")
    print(f"(active-listing + {SOLD_HAIRCUT} sold-haircut; flips to ALL-eBay-SOLD once Insights approved)\n")
    print(f"{'Category':22} {'Paid':>7} {'eBayEst':>8} {'n':>3} {'Margin':>7}  Description")
    flags=0
    for it in sample:
        est,n,note = ebay_estimate(it['desc'], acc)
        time.sleep(0.3)
        if est is None:
            print(f"{it['cat'][:22]:22} {it['cost']:>7,.0f} {'—':>8} {n:>3} {'—':>7}  {it['desc'][:34]} [{note}]")
            continue
        m=(est-it['cost'])/est if est>0 else None
        flag = " OVERPAY" if it['cost']>est else (" <50%" if (m is not None and m<0.5) else "")
        if flag: flags+=1
        ms = f"{m*100:.0f}%" if m is not None else "—"
        print(f"{it['cat'][:22]:22} {it['cost']:>7,.0f} {est:>8,.0f} {n:>3} {ms:>7}  {it['desc'][:34]}{flag}")
    print(f"\nFlagged (overpay or <50%): {flags}/{len(sample)}")

if __name__=='__main__':
    main()
