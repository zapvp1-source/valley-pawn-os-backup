#!/usr/bin/env python3
"""shop_weekly_report.py — native vp-website-shop-weekly-report (2026-10-14, Google re-grant prep).

The SKILL's 4 checks, without Claude or the WordPress.com connector:
  1. Site traffic, last 7 days vs the 7 before — from the GA4 Data API (the Mac has no WordPress.com
     stats token; GA4 page views / users replace Jetpack views / visitors, plus /shop/ page views).
  2. WooCommerce order count (wc/v3/reports/orders/totals, App Password) — expected 0.
  3. /shop/ live card count (class="vp-card") + the WooCommerce-hijack check (body class woocommerce-shop).
  4. One short plain DM to Joshua (under 150 words) + the eBay Seller Hub Traffic Report reminder.

    shop_weekly_report.py --render       # prints the DM, sends nothing
    shop_weekly_report.py --send         # DM once (skips if one went out in the last 5 days)

Failure policy v3: traffic pull impossible -> no DM, ONE ledger row ("Google access needs one approval"
when it is the scope). Steps 2-3 failing just become a "couldn't check X this week" line.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HOME = Path.home()
OS_DIR = HOME / "Documents/Claude/Projects/Valley Pawn OS"
AN_BIN = HOME / "Documents/Claude/Projects/Website/analytics/bin"
sys.path.insert(0, str(AN_BIN))
from google_auth import ANALYTICS_SCOPE, NeedsGrant, api_post, has_scope  # noqa: E402

TASK = "vp-website-shop-weekly-report"
PY = "/usr/bin/python3"
URL = "https://analyticsdata.googleapis.com/v1beta/properties/353209303:runReport"
LEDGER = OS_DIR / "fleet/FAILURE_LEDGER.md"
STATE = OS_DIR / "fleet/state/shop_weekly_report.json"
RENDER_DIR = OS_DIR / "fleet/test_output/shop_weekly_render"


def now() -> dt.datetime:
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("America/New_York"))
    except Exception:
        return dt.datetime.now()


def ledger(sentence: str, needs: str = "no") -> None:
    with LEDGER.open("a") as f:
        f.write(f"| {now():%Y-%m-%d %H:%M ET} (native) | {TASK} | {sentence} | NEEDS_HUMAN: {needs} | OPEN |\n")


def ga(a: dt.date, b: dt.date) -> dict:
    r = api_post(URL, {"dateRanges": [{"startDate": str(a), "endDate": str(b)}],
                       "metrics": [{"name": "screenPageViews"}, {"name": "totalUsers"}]}, ANALYTICS_SCOPE)
    v = [float(x["value"]) for x in (r.get("rows") or [{}])[0].get("metricValues", [])] or [0, 0]
    r2 = api_post(URL, {"dateRanges": [{"startDate": str(a), "endDate": str(b)}],
                        "dimensions": [{"name": "pagePath"}], "metrics": [{"name": "screenPageViews"}],
                        "dimensionFilter": {"filter": {"fieldName": "pagePath",
                                                       "stringFilter": {"matchType": "BEGINS_WITH", "value": "/shop"}}},
                        "limit": 50}, ANALYTICS_SCOPE)
    shop = sum(float(x["metricValues"][0]["value"]) for x in r2.get("rows", []) or [])
    return {"views": int(v[0]), "users": int(v[1]), "shop": int(shop)}


def chg(c: int, p: int) -> str:
    if not p:
        return "no prior week to compare"
    x = round((c - p) / p * 100)
    return "flat vs prior week" if x == 0 else f"{'+' if x > 0 else ''}{x}% vs prior week"


def woo_orders() -> int | None:
    try:
        from wp_client import WP
        st, j = WP(timeout=60).get_json("/wc/v3/reports/orders/totals")
        if st != 200 or not isinstance(j, list):
            return None
        return int(sum(int(x.get("total", 0) or 0) for x in j))
    except Exception:
        return None


def shop_cards() -> tuple[int | None, bool]:
    try:
        req = urllib.request.Request(f"https://thevalleypawn.com/shop/?v={int(time.time())}",
                                     headers={"User-Agent": "Mozilla/5.0 (Macintosh) ValleyPawnOps"})
        with urllib.request.urlopen(req, timeout=60) as r:
            h = r.read().decode("utf-8", "ignore")
        hijack = bool(re.search(r'<body[^>]*class="[^"]*woocommerce-shop', h))
        return h.count('class="vp-card"'), hijack
    except Exception:
        return None, False


def compose() -> tuple[int, str]:
    if not has_scope(ANALYTICS_SCOPE):
        raise NeedsGrant("analytics scope missing")
    y = now().date() - dt.timedelta(days=1)
    a = y - dt.timedelta(days=6)
    cur, prev = ga(a, y), ga(a - dt.timedelta(days=7), a - dt.timedelta(days=1))
    orders = woo_orders()
    cards, hijack = shop_cards()
    L = [f"Website check — week of {a.strftime('%b')} {a.day} to {y.strftime('%b')} {y.day}"]
    L.append(f"• Site: {cur['views']:,} page views ({chg(cur['views'], prev['views'])}), "
             f"{cur['users']:,} visitors ({chg(cur['users'], prev['users'])}).")
    L.append(f"• Shop page: {cur['shop']:,} views ({chg(cur['shop'], prev['shop'])}).")
    if cards is None:
        L.append("• Couldn't check the shop page item count this week.")
    elif hijack or cards == 0:
        L.append(f"• ⚠️ The shop page looks BROKEN right now ({cards} items showing) — it needs a look today.")
    else:
        L.append(f"• Shop page is live with {cards:,} items.")
    if orders is None:
        L.append("• Couldn't check website orders this week.")
    elif orders == 0:
        L.append("• Website orders: 0 (expected — shoppers check out on eBay).")
    else:
        L.append(f"• ⚠️ Website orders: {orders} — someone checked out on the website itself, which isn't "
                 "supposed to happen. Worth a look at who and what.")
    L.append("• For clicks from the site to eBay, eBay Seller Hub > Performance > Traffic has the detail.")
    return 0, "\n".join(L)


def recent_sent(days: int = 5) -> bool:
    try:
        last = dt.datetime.fromisoformat(json.loads(STATE.read_text())["last_sent"])
        return (now() - last).days < days
    except Exception:
        return False


def main() -> int:
    send = "--send" in sys.argv
    try:
        _, msg = compose()
    except NeedsGrant as e:
        print("NO ACCESS — " + str(e), file=sys.stderr)
        if send:
            ledger("Google access needs one approval — the weekly website + shop DM was not sent.",
                   "yes, double-click 'Grant Google Access.command' in Valley Pawn OS and click Allow once")
        return 1
    except Exception as e:
        print(f"FAILED — {type(e).__name__}: {e}", file=sys.stderr)
        if send:
            ledger("The weekly website + shop DM was not sent (the traffic numbers could not be pulled).")
        return 2
    if not send:
        RENDER_DIR.mkdir(parents=True, exist_ok=True)
        (RENDER_DIR / f"{now():%Y-%m-%d}.txt").write_text(msg + "\n")
        print(msg)
        print(f"({len(msg.split())} words)")
        return 0
    if recent_sent():
        print("already sent in the last 5 days — skip")
        return 0
    r = subprocess.run([PY, str(OS_DIR / "bin/vp_slack.py"), "dm", msg], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        ledger("The weekly website + shop DM did not go out (Slack refused it).")
        return 2
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"last_sent": now().isoformat(), "text": msg}, indent=1, ensure_ascii=False))
    print("SENT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
