#!/usr/bin/env python3
"""eBay API verification probe for the intake-valuation Tier 3.
Reads App/Cert ID from the existing ebay_weekly_rankings.py (does not print secrets).
Mints an app-level OAuth token (client_credentials) and tests:
  1) Browse API           -> active listing prices (general availability)
  2) Marketplace Insights -> true SOLD comps last 90d (restricted; needs app approval)
"""
import re, json, base64, urllib.request, urllib.parse, statistics

SRC = "/Users/joshuadavis/Documents/valley-pawn/ebay_weekly_rankings.py"
txt = open(SRC).read()
APP_ID  = re.search(r'APP_ID\s*=\s*"([^"]+)"', txt).group(1)
CERT_ID = re.search(r'CERT_ID\s*=\s*"([^"]+)"', txt).group(1)

def _read_err(e):
    try: return e.read().decode()[:300]
    except: return str(e)

def get_token():
    cred = base64.b64encode(f"{APP_ID}:{CERT_ID}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
    }).encode()
    req = urllib.request.Request(
        "https://api.ebay.com/identity/v1/oauth2/token", data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "Authorization": f"Basic {cred}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def api_get(url, token):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, json.load(r)

def browse(q, token):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search?" + urllib.parse.urlencode(
        {"q": q, "limit": 25, "filter": "conditions:{USED}"})
    st, d = api_get(url, token)
    prices = []
    for it in d.get("itemSummaries", []):
        p = it.get("price", {}).get("value")
        if p:
            try: prices.append(float(p))
            except: pass
    return d.get("total"), prices

def insights(q, token):
    url = "https://api.ebay.com/buy/marketplace_insights/v1_beta/item_sales/search?" + urllib.parse.urlencode(
        {"q": q, "limit": 25})
    return api_get(url, token)

print("App ID prefix:", APP_ID[:12], "…   (creds read OK)")
try:
    tok = get_token()
    access = tok["access_token"]
    print(f"OAuth token: ACQUIRED  (expires_in={tok.get('expires_in')}s)")
except urllib.error.HTTPError as e:
    print("OAuth token: FAILED", e.code, _read_err(e)); raise SystemExit
except Exception as e:
    print("OAuth token: FAILED", e); raise SystemExit

print("\n--- Browse API (active USED listings) ---")
for q in ["Springfield Armory Prodigy 9mm", "Meze Audio Elite headphones", "Milwaukee 2922-20"]:
    try:
        total, prices = browse(q, access)
        if prices:
            prices.sort()
            print(f"  '{q}': total={total}  used-price n={len(prices)}  "
                  f"range ${min(prices):,.0f}-${max(prices):,.0f}  median ${statistics.median(prices):,.0f}")
        else:
            print(f"  '{q}': total={total}  (no priced used items)")
    except urllib.error.HTTPError as e:
        print(f"  '{q}': HTTP {e.code} {_read_err(e)}")

print("\n--- Marketplace Insights API (true SOLD, last 90d) ---")
try:
    st, d = insights("Springfield Armory Prodigy 9mm", access)
    recs = d.get("itemSales", [])
    print(f"  status={st}  sold records returned={len(recs)}  -> APPROVED")
except urllib.error.HTTPError as e:
    print(f"  HTTP {e.code}: {_read_err(e)}")
    print("  -> NOT approved for Marketplace Insights (expected; needs eBay application). Browse API is the fallback.")
