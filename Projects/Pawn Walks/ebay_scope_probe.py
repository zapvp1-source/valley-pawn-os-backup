#!/usr/bin/env python3
"""
eBay API SOLD-DATA ACCESS PROBE — definitive, credential-based test.
Run: python3 ebay_scope_probe.py

Answers ONE question with evidence rather than documentation: can THIS app
(FullCirc-ValleyPa-PRD) obtain real eBay SOLD/completed sales data through the API?

Tests, in order:
  1. Baseline app OAuth (proves credentials still work at all)
  2. OAuth WITH the buy.marketplace.insights scope (true 90-day SOLD comps)
  3. A live Marketplace Insights item_sales/search call, if a token was granted
  4. Browse API for comparison (known active-only)

NEVER prints credentials — only which step succeeded or failed, and the raw eBay
error code, which is what actually settles the question.
"""
import re, json, base64, sys, urllib.request, urllib.parse, urllib.error

SRC_CREDS  = "/Users/joshuadavis/Documents/valley-pawn/ebay_weekly_rankings.py"
TOKEN_URL  = "https://api.ebay.com/identity/v1/oauth2/token"
BROWSE_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
INSIGHTS_URL = "https://api.ebay.com/buy/marketplace_insights/v1_beta/item_sales/search"

BASE_SCOPE     = "https://api.ebay.com/oauth/api_scope"
INSIGHTS_SCOPE = "https://api.ebay.com/oauth/api_scope/buy.marketplace.insights"


def creds():
    txt = open(SRC_CREDS).read()
    app  = re.search(r'APP_ID\s*=\s*["\']([^"\']+)["\']', txt)
    cert = re.search(r'CERT_ID\s*=\s*["\']([^"\']+)["\']', txt)
    if not (app and cert):
        print("FATAL: could not locate APP_ID/CERT_ID in the source script.")
        sys.exit(2)
    return app.group(1), cert.group(1)


def get_token(app, cert, scope, label):
    auth = base64.b64encode(f"{app}:{cert}".encode()).decode()
    data = urllib.parse.urlencode({"grant_type": "client_credentials", "scope": scope}).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, headers={
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            tok = json.loads(r.read().decode())
            print(f"  [{label}] ✅ TOKEN GRANTED (expires {tok.get('expires_in')}s)")
            return tok.get("access_token")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400]
        print(f"  [{label}] ❌ DENIED  HTTP {e.code}")
        print(f"      eBay says: {body}")
        return None
    except Exception as e:
        print(f"  [{label}] ❌ ERROR {e}")
        return None


def call(url, token, params, label):
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(r.read().decode())
            n = d.get("total", len(d.get("itemSales", d.get("itemSummaries", []))))
            print(f"  [{label}] ✅ RETURNED DATA — total={n}")
            sample = (d.get("itemSales") or d.get("itemSummaries") or [])[:3]
            for s in sample:
                price = (s.get("lastSoldPrice") or s.get("price") or {}).get("value")
                date  = s.get("lastSoldDate", "")
                print(f"        {str(price):>10}  {date:<26} {s.get('title','')[:56]}")
            return True
    except urllib.error.HTTPError as e:
        print(f"  [{label}] ❌ HTTP {e.code} — {e.read().decode()[:300]}")
    except Exception as e:
        print(f"  [{label}] ❌ {e}")
    return False


def main():
    app, cert = creds()
    print(f"=== eBay SOLD-data access probe — app ...{app[-6:]} ===\n")

    print("STEP 1 — baseline app OAuth (do the credentials work at all?)")
    base = get_token(app, cert, BASE_SCOPE, "base scope")
    if not base:
        print("\nVERDICT: credentials themselves are failing — fix that before concluding "
              "anything about sold-data access.")
        return 1

    print("\nSTEP 2 — request the SOLD-data scope (buy.marketplace.insights)")
    ins = get_token(app, cert, INSIGHTS_SCOPE, "insights scope")

    print("\nSTEP 3 — live Marketplace Insights call (true sold comps)")
    if ins:
        call(INSIGHTS_URL, ins, {"q": "STIHL BG 50", "limit": 5,
                                 "filter": "lastSoldDate:[2026-05-01T00:00:00Z..]"}, "item_sales/search")
    else:
        print("  skipped — no insights token was granted")
        print("  (trying the endpoint with the BASE token anyway, to see the exact refusal)")
        call(INSIGHTS_URL, base, {"q": "STIHL BG 50", "limit": 5}, "item_sales w/ base token")

    print("\nSTEP 4 — Browse API (control: known ACTIVE-only)")
    call(BROWSE_URL, base, {"q": "STIHL BG 50", "limit": 3}, "browse active")

    print("\n" + "=" * 62)
    print("VERDICT: SOLD DATA VIA API IS " + ("AVAILABLE ✅" if ins else "NOT AVAILABLE ❌"))
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
