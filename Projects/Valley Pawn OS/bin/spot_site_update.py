#!/usr/bin/env python3
"""spot_site_update.py [--render] — push the canonical spot prices (spot_prices.json) to the website (2026-10-05).

The calculators on thevalleypawn.com read window.VP_GOLD_SPOT / VP_SILVER_SPOT. Those were hard-coded in three header
snippets (HFCM #2 4629.50, WPCode #1116 4604.40, an inline 4399.40) and had not been updated since early September.
This writes the numbers into a small published page, /spot-prices-feed/, via WP REST (site app password); WPCode #1116
fetches that page in the browser and overrides the hard-coded fallback. Creates the page on first run. Refuses to
publish a price that fetch_spot_prices.py marked stale or that is outside sane bounds."""
import base64, datetime as dt, json, os, sys, urllib.request
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
CREDS = os.path.expanduser("~/Documents/Claude/Projects/Website/shop-build/.wp_app_credentials")
kv = dict(l.strip().split("=", 1) for l in open(CREDS) if "=" in l)
A = "Basic " + base64.b64encode(("%s:%s" % (kv["WP_USER"].strip().strip('"'), kv["WP_APP_PASSWORD"].strip().strip('"'))).encode()).decode()
def wp(path, payload=None, method="GET"):
    r = urllib.request.Request("https://thevalleypawn.com/wp-json/wp/v2" + path, data=json.dumps(payload).encode() if payload is not None else None,
                               method=method, headers={"Authorization": A, "Content-Type": "application/json", "User-Agent": "ValleyPawnOps/1.0"})
    with urllib.request.urlopen(r, timeout=60) as x:
        return json.load(x)
sp = json.load(open(os.path.join(OS_DIR, "spot_prices.json")))
g, s = float(sp["gold_usd_per_ozt"]), float(sp["silver_usd_per_ozt"])
age_h = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(sp["updated_at"])).total_seconds() / 3600
if not (1000 < g < 15000 and 5 < s < 400) or age_h > 72:
    print("refusing: gold %s silver %s age %.0fh" % (g, s, age_h)); sys.exit(1)
body = "<!-- wp:paragraph --><p>gold: %.2f<br>silver: %.2f<br>updated: %s</p><!-- /wp:paragraph -->" % (g, s, sp["updated_at"])
pages = wp("/pages?slug=spot-prices-feed&status=publish,draft,private&context=edit&_fields=id,status")
if "--render" in sys.argv:
    print("would write", body, "to", pages); sys.exit(0)
if pages:
    wp("/pages/%d" % pages[0]["id"], {"content": body, "status": "publish"}, "POST"); pid = pages[0]["id"]
else:
    pid = wp("/pages", {"title": "Spot prices feed", "slug": "spot-prices-feed", "content": body, "status": "publish",
                        "comment_status": "closed", "ping_status": "closed"}, "POST")["id"]
pub = json.load(urllib.request.urlopen(urllib.request.Request("https://thevalleypawn.com/wp-json/wp/v2/pages?slug=spot-prices-feed&_fields=id,content", headers={"User-Agent": "Mozilla/5.0"}), timeout=30))
ok = pub and ("gold: %.2f" % g) in pub[0]["content"]["rendered"]
print("spot feed page %d -> gold %.2f silver %.2f | public read %s" % (pid, g, s, "OK" if ok else "MISMATCH"))
sys.exit(0 if ok else 1)
