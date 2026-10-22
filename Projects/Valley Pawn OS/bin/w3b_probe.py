#!/usr/bin/env python3
"""w3b_probe.py — READ-ONLY probes for the Mac-first wave 3 SECOND PASS (2026-10-20). Never writes, joins or posts.
  w3b_probe.py slack            can the ops bot READ each channel the second-pass agents need? (history limit=1;
                                never conversations.join — a join leaves a visible message)
  w3b_probe.py sheet            tab names + first rows of the Valley Pawn Trends sheet (gun audit) via the Sheets API
  w3b_probe.py chekkit          Chekkit leaderboard 'reviews' per store for last month (bonus close input)
  w3b_probe.py usearch          one Unified Search query (entity check evidence path works?)
  w3b_probe.py files            Slack files:read works? (newest file in #monthly-gun-audit: name + bytes fetched)
"""
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OS_DIR = os.path.dirname(HERE)
PROJ = os.path.dirname(OS_DIR)

CHANNELS = {
    "monthly-gun-audit": "C07CPN020G0", "new-customers": "C0BHF9NM0BH", "ceo-briefs": "C0C06PWLQCR",
    "policy-announcements": "C03BHQ9RLR0", "general": "C03BETSS669", "store-performance": "C03CGTN3KN1",
    "employee-performance": "C0ATTLPQHR8", "loan-review": "C0B08RS2BMK", "layaway-review": "C04N24STDP1",
    "aged-inventory-review": "C04NGH4FF35", "items-to-price": "C0BA5U0GENL", "pawn-walks": "C0B8WR95N31",
    "jewlery-counts": "C0BM9NHGTT4", "bonus-goals": "C04TXF0KGNL", "google-reviews": "C04NDE52U2G",
    "weekly-returns-summary": "C0B1K4WK2HZ", "deal-of-the-week": "C0AVCANK7E3", "company-performance": "C0B26GD8D2R",
    "first-payment-default": "C0B17894S2Y", "timekeeping-summary": "C0AN6TNA4ES", "daily-funds-reconcilation": "C0B3R9B3S8H",
    "social-media": "C0BMRC2LN3D", "email-campiagns": "C0APR5WUL2Z", "website": "C0ASE9C0GQ0", "ai-marketing": "C0BCEESUANM",
    "ebay-performance": "C0ANVN5KX4Y", "blog-posts": "C0APY6TE604", "scrap-rankings": "C05EHBH4G67",
}
TRENDS = "16Tzy6C-JlmJ-XIo-IrVwUOqSmOekIQ46K1b3t2nggWo"  # 2026-10-21: jdavis@fcfpawn.com copy (old fullcirclepawn@gmail.com sheet 1sLid9zjLUkH-B8MOE5Fr_aemw35bxyAbtuUz4BTVA6s retired)


def slack():
    import vp_slack
    bad = 0
    for name, ch in CHANNELS.items():
        r = vp_slack.call("conversations.history", params={"channel": ch, "limit": 1})
        st = "member" if r.get("ok") else r.get("error")
        bad += 0 if r.get("ok") else 1
        print("%-26s %s  %s" % (name, ch, st))
    print("NOT READABLE: %d" % bad)


def sheet():
    sys.path.insert(0, os.path.join(PROJ, "Website", "analytics", "bin"))
    import google_auth
    tok = google_auth.access_token(require="https://www.googleapis.com/auth/spreadsheets")
    def get(url):
        return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": "Bearer " + tok}), timeout=30))
    meta = get("https://sheets.googleapis.com/v4/spreadsheets/%s?fields=properties.title,sheets.properties" % TRENDS)
    print("title:", meta["properties"]["title"])
    for s in meta["sheets"]:
        p = s["properties"]
        print("== tab %r id=%s rows=%s cols=%s" % (p["title"], p["sheetId"], p["gridProperties"]["rowCount"], p["gridProperties"]["columnCount"]))
        v = get("https://sheets.googleapis.com/v4/spreadsheets/%s/values/%s" % (TRENDS, urllib.parse.quote("'%s'!A1:P80" % p["title"])))
        for row in v.get("values", []):
            print("  |", " | ".join(row))


def chekkit():
    import reviews_weekly as rw
    today = dt.date.today()
    first = today.replace(day=1)
    last_end = first - dt.timedelta(days=1)
    frm, to = last_end.replace(day=1).isoformat(), last_end.isoformat()
    for s in ["CUL", "HAR", "LEX", "ROA", "WAY"]:
        try:
            tok = rw.token(s)
            _, loc = rw.leaderboard(tok, frm, to)
            print(s, frm, to, "reviews.total=", (loc.get("reviews") or {}).get("total"))
        except Exception as e:
            print(s, "ERROR", type(e).__name__, str(e)[:120])


def usearch():
    r = subprocess.run(["/usr/bin/python3", os.path.join(PROJ, "Unified Search", "usearch.py"), "query", "annual report",
                        "--mail", "--from", "scc.virginia.gov", "-n", "3", "--json"], capture_output=True, text=True, timeout=120)
    print("rc", r.returncode, (r.stdout or "")[:1500], (r.stderr or "")[-400:])


def files():
    import vp_slack
    r = vp_slack.call("conversations.history", params={"channel": "C07CPN020G0", "limit": 20})
    for m in r.get("messages", []):
        for f in m.get("files") or []:
            url = f.get("url_private_download") or f.get("url_private")
            req = urllib.request.Request(url, headers={"Authorization": "Bearer " + vp_slack.token()})
            b = urllib.request.urlopen(req, timeout=60).read()
            print("file", f.get("name"), f.get("mimetype"), "bytes", len(b), "starts", b[:4])
            return
    print("no files visible:", r.get("error") or "ok/no files")


if __name__ == "__main__":
    {"slack": slack, "sheet": sheet, "chekkit": chekkit, "usearch": usearch, "files": files}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
