#!/usr/bin/env python3
"""
Valley Pawn — eBay Daily Listings Report (all 5 stores)
ADDITIVE companion to ebay_weekly_rankings.py — does NOT modify it.

Per store, pulls the active listings via the eBay Trading API (GetMyeBaySelling -> ActiveList)
and reports:
  • Items listed the PRIOR day (new listings, by StartTime, ET)
  • Total active listings
  • Total value of active listings (sum of current price x quantity)

Posts a ranked summary to Slack #ebay-performance.

Usage:
  python3 ebay_daily_listings.py            # DRY RUN: prints, does NOT post
  python3 ebay_daily_listings.py --post     # posts to Slack

Reuses the per-store tokens from ebay_weekly_rankings.py (never duplicated here).
Canonical location: ~/ebay_daily_listings.py (home) — Desktop is synced/volatile, do not run from there.
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

# Same Slack webhook the rankings script uses (#ebay-performance)
SLACK_WEBHOOK = open(os.path.expanduser("~/.vp_secrets/slack_webhook_ebay_markdown")).read().strip()  # never hardcode -- see ~/.vp_secrets/slack_webhook_ebay_markdown

import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID, DEV_ID, CERT_ID  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py

RANKINGS_PATHS = [
    os.path.expanduser("~/ebay_weekly_rankings.py"),
    os.path.expanduser("~/Desktop/ebay_weekly_rankings.py"),
    os.path.expanduser("~/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py"),
]

NS       = "urn:ebay:apis:eBLBaseComponents"
EBAY_URL = "https://api.ebay.com/ws/api.dll"
MEDALS   = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

# Eastern Time offset (EDT = -4). Simple fixed offset is fine for a day-boundary report.
EASTERN = timezone(timedelta(hours=-4))


def load_stores():
    for p in RANKINGS_PATHS:
        if os.path.exists(p):
            ns = {}
            exec(compile(open(p).read(), p, "exec"), ns)  # trusted local file
            if "STORES" in ns:
                return ns["STORES"]
    raise SystemExit("Could not find ebay_weekly_rankings.py to load store tokens.")


def _active_page(token, page):
    body = f"""<?xml version="1.0" encoding="utf-8"?>
<GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>
  <ActiveList>
    <Include>true</Include>
    <Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination>
  </ActiveList>
</GetMyeBaySellingRequest>""".encode("utf-8")
    headers = {
        "X-EBAY-API-SITEID": "0",
        "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
        "X-EBAY-API-CALL-NAME": "GetMyeBaySelling",
        "X-EBAY-API-APP-NAME": APP_ID,
        "X-EBAY-API-DEV-NAME": DEV_ID,
        "X-EBAY-API-CERT-NAME": CERT_ID,
        "X-EBAY-API-IAF-TOKEN": token,
        "Content-Type": "text/xml",
    }
    with urlopen(Request(EBAY_URL, data=body, headers=headers), timeout=60) as r:
        return r.read().decode("utf-8")


def get_listings(store, day_start_utc, day_end_utc):
    name, token = store["name"], store["token"]
    total = 0
    total_value = 0.0
    listed_yday = 0
    listed_yday_value = 0.0
    page = 1
    while True:
        try:
            root = ET.fromstring(_active_page(token, page))
        except Exception as e:
            return {"name": name, "error": str(e)}
        ack = root.findtext(f"{{{NS}}}Ack", "")
        if ack in ("Failure",):
            msgs = root.findall(f".//{{{NS}}}ShortMessage")
            return {"name": name, "error": msgs[0].text if msgs else "API error"}

        items = root.findall(f".//{{{NS}}}ActiveList/{{{NS}}}ItemArray/{{{NS}}}Item")
        for it in items:
            total += 1
            qty = it.findtext(f".//{{{NS}}}QuantityAvailable") or it.findtext(f".//{{{NS}}}Quantity") or "1"
            try:
                qty = int(qty)
            except ValueError:
                qty = 1
            price_txt = (it.findtext(f".//{{{NS}}}SellingStatus/{{{NS}}}CurrentPrice")
                         or it.findtext(f".//{{{NS}}}BuyItNowPrice")
                         or it.findtext(f".//{{{NS}}}StartPrice") or "0")
            try:
                price = float(price_txt)
            except ValueError:
                price = 0.0
            total_value += price * max(qty, 1)

            start = it.findtext(f".//{{{NS}}}ListingDetails/{{{NS}}}StartTime")
            if start:
                try:
                    st = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                except ValueError:
                    try:
                        st = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                    except ValueError:
                        st = None
                if st and day_start_utc <= st < day_end_utc:
                    listed_yday += 1
                    listed_yday_value += price * max(qty, 1)

        total_pages = root.findtext(f".//{{{NS}}}ActiveList/{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try:
            total_pages = int(total_pages)
        except (TypeError, ValueError):
            total_pages = page
        if page >= total_pages:
            break
        page += 1

    return {
        "name": name, "error": None,
        "total": total, "total_value": total_value,
        "listed_yday": listed_yday, "listed_yday_value": listed_yday_value,
    }


def _sellerlist_page(token, start_iso, end_iso, page):
    body = f"""<?xml version="1.0" encoding="utf-8"?>
<GetSellerListRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>
  <StartTimeFrom>{start_iso}</StartTimeFrom>
  <StartTimeTo>{end_iso}</StartTimeTo>
  <DetailLevel>ReturnAll</DetailLevel>
  <Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination>
</GetSellerListRequest>""".encode("utf-8")
    headers = {
        "X-EBAY-API-SITEID": "0",
        "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
        "X-EBAY-API-CALL-NAME": "GetSellerList",
        "X-EBAY-API-APP-NAME": APP_ID,
        "X-EBAY-API-DEV-NAME": DEV_ID,
        "X-EBAY-API-CERT-NAME": CERT_ID,
        "X-EBAY-API-IAF-TOKEN": token,
        "Content-Type": "text/xml",
    }
    with urlopen(Request(EBAY_URL, data=body, headers=headers), timeout=90) as r:
        return r.read().decode("utf-8")


def get_listed_yesterday(store, start_iso, end_iso):
    """True count of listings CREATED yesterday, incl. items that already sold/ended.
    Uses GetSellerList filtered by StartTime (active + ended)."""
    token = store["token"]
    count = 0
    value = 0.0
    page = 1
    while True:
        try:
            root = ET.fromstring(_sellerlist_page(token, start_iso, end_iso, page))
        except Exception as e:
            return {"listed_err": str(e)}
        if root.findtext(f"{{{NS}}}Ack", "") == "Failure":
            msgs = root.findall(f".//{{{NS}}}ShortMessage")
            return {"listed_err": msgs[0].text if msgs else "GetSellerList error"}
        for it in root.findall(f".//{{{NS}}}ItemArray/{{{NS}}}Item"):
            count += 1
            price_txt = (it.findtext(f".//{{{NS}}}StartPrice")
                         or it.findtext(f".//{{{NS}}}SellingStatus/{{{NS}}}CurrentPrice")
                         or it.findtext(f".//{{{NS}}}BuyItNowPrice") or "0")
            try:
                value += float(price_txt)
            except ValueError:
                pass
        total_pages = root.findtext(f".//{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try:
            total_pages = int(total_pages)
        except (TypeError, ValueError):
            total_pages = page
        if page >= total_pages:
            break
        page += 1
    return {"listed_yday": count, "listed_yday_value": value, "listed_err": None}


def post_to_slack(message):
    payload = json.dumps({"text": message}).encode("utf-8")
    req = Request(SLACK_WEBHOOK, data=payload, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=15) as r:
        if r.read().decode().strip() != "ok":
            raise RuntimeError("Slack webhook returned non-ok response")


def main():
    do_post = "--post" in sys.argv

    now_et = datetime.now(EASTERN)
    y_start_et = (now_et - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    y_end_et = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
    day_start_utc = y_start_et.astimezone(timezone.utc)
    day_end_utc = y_end_et.astimezone(timezone.utc)
    label = y_start_et.strftime("%a %b %-d, %Y")

    start_iso = day_start_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end_iso = day_end_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    stores = load_stores()
    results = []
    for s in stores:
        r = get_listings(s, day_start_utc, day_end_utc)  # totals: active count + total value
        # True "listed yesterday" incl. same-day sold items (GetSellerList by StartTime)
        ly = get_listed_yesterday(s, start_iso, end_iso)
        if not ly.get("listed_err"):
            r["listed_yday"] = ly["listed_yday"]
            r["listed_yday_value"] = ly["listed_yday_value"]
        results.append(r)
        if r.get("error"):
            print(f"  {r['name']}: ERROR {r['error']}")
        else:
            print(f"  {r['name']}: +{r['listed_yday']} listed yday | {r['total']} active | ${r['total_value']:,.2f} value")

    ok = [r for r in results if not r.get("error")]
    bad = [r for r in results if r.get("error")]
    ok.sort(key=lambda r: (r["listed_yday"], r["total_value"]), reverse=True)

    lines = [f"🧾 *eBay Daily Listings* — new listings on *{label}*\n"]
    for i, r in enumerate(ok):
        medal = MEDALS[i] if i < len(MEDALS) else f"{i+1}."
        lines.append(
            f"{medal} *{r['name']}* — *+{r['listed_yday']}* new "
            f"(${r['listed_yday_value']:,.0f}) | {r['total']} active | ${r['total_value']:,.0f} total value"
        )
    for r in bad:
        lines.append(f"⚠️ *{r['name']}* — data unavailable")

    tot_new = sum(r["listed_yday"] for r in ok)
    tot_new_val = sum(r["listed_yday_value"] for r in ok)
    tot_active = sum(r["total"] for r in ok)
    tot_val = sum(r["total_value"] for r in ok)
    lines.append(
        f"\n📦 *Combined: +{tot_new} new listings (${tot_new_val:,.0f}) yesterday | "
        f"{tot_active} active | ${tot_val:,.0f} total listed value*"
    )
    msg = "\n".join(lines)
    print("\n" + msg)

    if do_post:
        post_to_slack(msg)
        print("\n✅ Posted to Slack #ebay-performance")
    else:
        print("\n(dry run — not posted; add --post to send to Slack)")


if __name__ == "__main__":
    main()
