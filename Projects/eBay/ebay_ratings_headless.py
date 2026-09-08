#!/usr/bin/env python3
"""Valley Pawn — headless monthly eBay ratings/standing sweep for all 5 stores.

Replaces the Chrome-dependent half of `monthly-ebay-ratings-sweep`, which could only ever read
Seller Hub for whichever store account Chrome happened to be signed into (August 2026 captured
Lexington only; September captured nothing).

Pulls, per store, with no browser:
  - feedback score, 1/6/12-month positive / neutral / negative counts, positive %
  - Top Rated Seller status and eBay's own site-visibility flags (GetUser -> SellerInfo)

Seller Standards (late shipment rate, defect rate, cases closed without resolution, standards
level, next evaluation date) come from `sell/analytics/v1/seller_standards_profile` via
`ebay_analytics_auth.py`, using the 5 store refresh tokens minted 2026-09-06 (full 3-legged OAuth,
~sell.analytics.readonly~ scope; good ~547 days). If that module or its saved tokens are ever
missing, this script reports standards as UNAVAILABLE rather than guessing (Rule 18) — it must
never estimate a standards level.

Usage: python3 ebay_ratings_headless.py            # prints a markdown report to stdout
"""
import datetime
import json
import os
import sys
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen
from urllib.error import HTTPError

sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
from ebay_store_tokens import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from ebay_analytics_auth import access_token as _analytics_token
except Exception:
    _analytics_token = None

NS = "urn:ebay:apis:eBLBaseComponents"
URL = "https://api.ebay.com/ws/api.dll"
RANKINGS = os.path.expanduser("~/ebay_weekly_rankings.py")


def stores():
    ns = {}
    exec(compile(open(RANKINGS).read(), RANKINGS, "exec"), ns)
    return ns["STORES"]


def call(token, name, inner):
    body = (f'<?xml version="1.0" encoding="utf-8"?><{name}Request xmlns="{NS}">'
            f'<RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>'
            f'{inner}</{name}Request>').encode()
    h = {"X-EBAY-API-SITEID": "0", "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
         "X-EBAY-API-CALL-NAME": name, "X-EBAY-API-APP-NAME": APP, "X-EBAY-API-DEV-NAME": DEV,
         "X-EBAY-API-CERT-NAME": CERT, "X-EBAY-API-IAF-TOKEN": token, "Content-Type": "text/xml"}
    return ET.fromstring(urlopen(Request(URL, data=body, headers=h), timeout=60).read().decode())


def q(node, path):
    return node.findtext(path.replace("{}", "{" + NS + "}"))


def profile(token):
    u = call(token, "GetUser", "<DetailLevel>ReturnAll</DetailLevel>")
    # NOTE: no DetailLevel — "ReturnSummary" makes eBay throw "System error"; the bare call
    # returns FeedbackSummary with PeriodInDays buckets (30 / 180 / 365).
    fb = call(token, "GetFeedback", "")
    s = fb.find(f".//{{{NS}}}FeedbackSummary")

    def per(days):
        out = {}
        for kind in ("Positive", "Neutral", "Negative"):
            for e in s.findall(f"{{{NS}}}{kind}FeedbackPeriodArray/{{{NS}}}FeedbackPeriod"):
                if q(e, "{}PeriodInDays") == days:
                    out[kind] = int(q(e, "{}Count") or 0)
        return out

    m1, m6, m12 = per("30"), per("180"), per("365")
    tot12 = sum(m12.values()) or 1
    return {
        "user": q(u, ".//{}User/{}UserID"),
        "score": q(u, ".//{}User/{}FeedbackScore"),
        "positive_pct_lifetime": q(u, ".//{}User/{}PositiveFeedbackPercent"),
        "registered": q(u, ".//{}User/{}RegistrationDate"),
        "top_rated": q(u, ".//{}SellerInfo/{}TopRatedSeller"),
        "top_rated_program": q(u, ".//{}TopRatedSellerDetails/{}TopRatedProgram"),
        "good_standing": q(u, ".//{}SellerInfo/{}GoodStanding"),
        "m1": m1, "m6": m6, "m12": m12,
        "pos12_pct": round(100.0 * m12.get("Positive", 0) / tot12, 2),
    }


STANDARDS_URL = "https://api.ebay.com/sell/analytics/v1/seller_standards_profile/PROGRAM_US/CURRENT"
# The metrics that matter for a plain-language read — everything else (min days on site, min
# transaction count, min GMV) is an eligibility gate all 5 stores clear comfortably and isn't
# worth reporting monthly.
KEY_METRICS = {
    "SHIPPING_MISS_RATE": "Late shipment rate",
    "DEFECTIVE_TRANSACTION_RATE": "Transaction defect rate",
    "DEFECTIVE_TRANSACTION_COUNT": "Transaction defect count",
    "CLAIMS_SAF_RATE": "Cases closed without seller resolution",
    "VALID_TRACKING_UPLOADED_WITHIN_HANDLING_RATE": "Tracking uploaded on time",
}


def standards(store_name):
    if _analytics_token is None:
        return {"error": "ebay_analytics_auth.py not importable"}
    tok = _analytics_token(store_name.lower())
    req = Request(STANDARDS_URL, headers={"Authorization": f"Bearer {tok}", "Accept": "application/json"})
    try:
        with urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode())
    except HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read()[:200].decode(errors='replace')}"}
    out = {"level": d.get("standardsLevel"), "eval_date": d.get("cycle", {}).get("evaluationDate", "")[:10],
           "eval_month": d.get("cycle", {}).get("evaluationMonth"), "metrics": {}, "below": []}
    for m in d.get("metrics", []):
        key = m.get("metricKey")
        if key not in KEY_METRICS:
            continue
        v = m.get("value")
        if isinstance(v, dict):
            display = v.get("value")
            if "numerator" in v:
                display = f"{v['value']}% ({v['numerator']}/{v['denominator']})"
        else:
            display = v
        out["metrics"][KEY_METRICS[key]] = display
        if m.get("level") == "BELOW_STANDARD":
            out["below"].append(KEY_METRICS[key])
    return out


def main():
    rows = []
    for st in stores():
        try:
            p = profile(st["token"])
            p["store"] = st["name"]
            rows.append(p)
        except Exception as e:
            rows.append({"store": st["name"], "error": repr(e)[:140]})

    good = [r for r in rows if "error" not in r]
    good.sort(key=lambda r: -r["pos12_pct"])
    today = datetime.date.today()
    print(f"# eBay Ratings Sweep — {today:%B %Y}\n")
    print(f"Headless pull (no browser), all 5 store accounts, run {today.isoformat()}.\n")
    print("| Rank | Store | Username | Feedback Score | 12-mo Positive % | Top Rated Seller |")
    print("|---|---|---|---|---|---|")
    for i, r in enumerate(good, 1):
        # GetUser only returns TopRatedSellerDetails/TopRatedProgram for accounts that are IN the
        # program (verified 2026-09-06: present for Waynesboro + Culpeper, absent for the three
        # stores whose public profiles show no badge). Absence == not Top Rated.
        tr = f"Yes ({r['top_rated_program']})" if r.get("top_rated_program") else "No"
        gs = {"true": "", "false": " — NOT in good standing"}.get(str(r["good_standing"]).lower(), "")
        print(f"| {i} | {r['store']} | {r['user']} | {r['score']} | {r['pos12_pct']}% | {tr}{gs} |")
    print("\n## Feedback detail by store\n")
    for r in good:
        f = lambda d: f"{d.get('Positive',0)}/{d.get('Neutral',0)}/{d.get('Negative',0)}"  # noqa: E731
        print(f"### {r['store']} — {r['user']}")
        print(f"- Feedback score: {r['score']} | lifetime positive: {r['positive_pct_lifetime']}% | member since {(r['registered'] or '')[:10]}")
        print(f"- Positive/Neutral/Negative — 1-mo: {f(r['m1'])} · 6-mo: {f(r['m6'])} · 12-mo: {f(r['m12'])}\n")
    for r in rows:
        if "error" in r:
            print(f"- {r['store']}: PULL FAILED — {r['error']}")
    print("\n## Seller Standards\n")
    if _analytics_token is None:
        print("UNAVAILABLE this run — `ebay_analytics_auth.py` could not be imported. Nothing is "
              "estimated here on purpose (Rule 18).")
    else:
        std_rows = []
        for st in stores():
            s = standards(st["name"])
            s["store"] = st["name"]
            std_rows.append(s)
        print("| Store | Level | Evaluated | Late Shipment | Defect Rate | Cases w/o Resolution | Tracking On Time |")
        print("|---|---|---|---|---|---|---|")
        for s in std_rows:
            if "error" in s:
                print(f"| {s['store']} | UNAVAILABLE | — | pull failed: {s['error'][:80]} | | | |")
                continue
            m = s["metrics"]
            print(f"| {s['store']} | {s['level']} | {s['eval_date']} | "
                  f"{m.get('Late shipment rate','—')} | "
                  f"{m.get('Transaction defect rate', m.get('Transaction defect count','—'))} | "
                  f"{m.get('Cases closed without seller resolution','—')} | "
                  f"{m.get('Tracking uploaded on time','—')} |")
        below = [(s["store"], s["below"]) for s in std_rows if s.get("below")]
        if below:
            print("\n**Below standard on:**")
            for store, metrics in below:
                print(f"- {store}: {', '.join(metrics)}")
        else:
            print("\nNo store is below standard on any metric this cycle.")


if __name__ == "__main__":
    main()
