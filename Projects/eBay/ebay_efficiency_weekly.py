#!/usr/bin/env python3
"""
Valley Pawn — eBay Weekly Efficiency Scorecard (all 5 stores)
ADDITIVE companion to ebay_weekly_rankings.py — does NOT modify it.

Core-5 efficiency KPIs per store + channel, from the eBay Trading API (current tokens, no extra scope):
  1. Sell-through rate   = units sold (last 30d) / active listings
  2. Days-to-sell         = median (sale date - listing start date) for last-30d sales
  3. Aged inventory       = active listings live > 90 days: count, value, % of active value
  4. Revenue / listing    = sales (last 30d) / active listings
  5. New listings (7d)    = listings created in the last 7 days (GetSellerList by StartTime)

Posts a per-store table (ranked by sell-through) + channel totals to Slack #ebay-performance.

Usage:
  python3 ebay_efficiency_weekly.py            # DRY RUN (prints, no post)
  python3 ebay_efficiency_weekly.py --post     # posts to Slack

Canonical location: ~/ebay_efficiency_weekly.py (home). Reuses tokens from ebay_weekly_rankings.py.
"""

import json
import os
import statistics
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

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
EASTERN  = timezone(timedelta(hours=-4))

SALES_WINDOW_DAYS = 30
VELOCITY_WINDOW_DAYS = 7
AGED_DAYS = 90


def load_stores():
    for p in RANKINGS_PATHS:
        if os.path.exists(p):
            ns = {}
            exec(compile(open(p).read(), p, "exec"), ns)  # trusted local file
            if "STORES" in ns:
                return ns["STORES"]
    raise SystemExit("Could not find ebay_weekly_rankings.py to load store tokens.")


def _post(token, call_name, inner):
    body = (f'<?xml version="1.0" encoding="utf-8"?>'
            f'<{call_name}Request xmlns="urn:ebay:apis:eBLBaseComponents">'
            f'<RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>'
            f'{inner}</{call_name}Request>').encode("utf-8")
    headers = {
        "X-EBAY-API-SITEID": "0",
        "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
        "X-EBAY-API-CALL-NAME": call_name,
        "X-EBAY-API-APP-NAME": APP_ID,
        "X-EBAY-API-DEV-NAME": DEV_ID,
        "X-EBAY-API-CERT-NAME": CERT_ID,
        "X-EBAY-API-IAF-TOKEN": token,
        "Content-Type": "text/xml",
    }
    with urlopen(Request(EBAY_URL, data=body, headers=headers), timeout=90) as r:
        return ET.fromstring(r.read().decode("utf-8"))


def _parse_dt(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def get_active(token, aged_cutoff_utc):
    """Active count + value + aged(>90d) count + value."""
    total = value = aged_ct = 0
    aged_val = 0.0
    value = 0.0
    page = 1
    while True:
        inner = ("<ActiveList><Include>true</Include>"
                 f"<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination>"
                 "</ActiveList>")
        root = _post(token, "GetMyeBaySelling", inner)
        if root.findtext(f"{{{NS}}}Ack", "") == "Failure":
            return None
        for it in root.findall(f".//{{{NS}}}ActiveList/{{{NS}}}ItemArray/{{{NS}}}Item"):
            total += 1
            qty = it.findtext(f".//{{{NS}}}QuantityAvailable") or it.findtext(f".//{{{NS}}}Quantity") or "1"
            try:
                qty = max(int(qty), 1)
            except ValueError:
                qty = 1
            pr = (it.findtext(f".//{{{NS}}}SellingStatus/{{{NS}}}CurrentPrice")
                  or it.findtext(f".//{{{NS}}}BuyItNowPrice")
                  or it.findtext(f".//{{{NS}}}StartPrice") or "0")
            try:
                pr = float(pr)
            except ValueError:
                pr = 0.0
            value += pr * qty
            st = _parse_dt(it.findtext(f".//{{{NS}}}ListingDetails/{{{NS}}}StartTime"))
            if st and st < aged_cutoff_utc:
                aged_ct += 1
                aged_val += pr * qty
        tp = root.findtext(f".//{{{NS}}}ActiveList/{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try:
            tp = int(tp)
        except (TypeError, ValueError):
            tp = page
        if page >= tp:
            break
        page += 1
    return {"active": total, "active_value": value, "aged_ct": aged_ct, "aged_val": aged_val}


def get_sold(token, from_iso, to_iso):
    """Units + revenue + sold events [(item_id, sold_at)] for orders created in window."""
    units = 0
    revenue = 0.0
    events = []
    page = 1
    while True:
        inner = (f"<CreateTimeFrom>{from_iso}</CreateTimeFrom><CreateTimeTo>{to_iso}</CreateTimeTo>"
                 "<OrderStatus>Completed</OrderStatus>"
                 f"<Pagination><EntriesPerPage>100</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination>")
        root = _post(token, "GetOrders", inner)
        if root.findtext(f"{{{NS}}}Ack", "") == "Failure":
            return None
        for order in root.findall(f".//{{{NS}}}Order"):
            paid = _parse_dt(order.findtext(f".//{{{NS}}}PaidTime")) or _parse_dt(order.findtext(f".//{{{NS}}}CreatedTime"))
            for txn in order.findall(f".//{{{NS}}}TransactionArray/{{{NS}}}Transaction"):
                q = txn.findtext(f"{{{NS}}}QuantityPurchased") or "1"
                try:
                    q = max(int(q), 1)
                except ValueError:
                    q = 1
                units += q
                tp = txn.findtext(f".//{{{NS}}}TransactionPrice")
                try:
                    revenue += float(tp) * q if tp else 0.0
                except ValueError:
                    pass
                item_id = txn.findtext(f".//{{{NS}}}Item/{{{NS}}}ItemID")
                sold_at = _parse_dt(txn.findtext(f"{{{NS}}}CreatedDate")) or paid
                if item_id and sold_at:
                    events.append((item_id, sold_at))
        if root.findtext(f".//{{{NS}}}HasMoreOrders", "false").strip().lower() == "true":
            page += 1
        else:
            break
    return {"units": units, "revenue": revenue, "events": events}


def get_start_map(token, from_iso, to_iso):
    """{ItemID: StartTime} for listings started in window (active + ended), via GetSellerList."""
    m = {}
    page = 1
    while True:
        inner = (f"<StartTimeFrom>{from_iso}</StartTimeFrom><StartTimeTo>{to_iso}</StartTimeTo>"
                 "<GranularityLevel>Coarse</GranularityLevel>"
                 f"<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination>")
        root = _post(token, "GetSellerList", inner)
        if root.findtext(f"{{{NS}}}Ack", "") == "Failure":
            break
        for it in root.findall(f".//{{{NS}}}ItemArray/{{{NS}}}Item"):
            iid = it.findtext(f"{{{NS}}}ItemID")
            st = _parse_dt(it.findtext(f".//{{{NS}}}ListingDetails/{{{NS}}}StartTime"))
            if iid and st:
                m[iid] = st
        tp = root.findtext(f".//{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try:
            tp = int(tp)
        except (TypeError, ValueError):
            tp = page
        if page >= tp:
            break
        page += 1
    return m


def get_new_count(token, from_iso, to_iso):
    """Listings created in window (incl. already-sold), via GetSellerList by StartTime."""
    count = 0
    page = 1
    while True:
        inner = (f"<StartTimeFrom>{from_iso}</StartTimeFrom><StartTimeTo>{to_iso}</StartTimeTo>"
                 "<DetailLevel>ReturnAll</DetailLevel>"
                 f"<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination>")
        root = _post(token, "GetSellerList", inner)
        if root.findtext(f"{{{NS}}}Ack", "") == "Failure":
            return None
        count += len(root.findall(f".//{{{NS}}}ItemArray/{{{NS}}}Item"))
        tp = root.findtext(f".//{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
        try:
            tp = int(tp)
        except (TypeError, ValueError):
            tp = page
        if page >= tp:
            break
        page += 1
    return count


def main():
    do_post = "--post" in sys.argv
    now = datetime.now(EASTERN)
    sales_from = (now - timedelta(days=SALES_WINDOW_DAYS))
    vel_from = (now - timedelta(days=VELOCITY_WINDOW_DAYS))
    aged_cutoff = (now - timedelta(days=AGED_DAYS)).astimezone(timezone.utc)

    def iso(dt):
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    map_from = now - timedelta(days=120)
    sales_from_iso, now_iso, vel_from_iso = iso(sales_from), iso(now), iso(vel_from)
    map_from_iso = iso(map_from)

    rows = []
    for s in load_stores():
        name = s["name"]
        a = get_active(s["token"], aged_cutoff)
        sold = get_sold(s["token"], sales_from_iso, now_iso)
        new7 = get_new_count(s["token"], vel_from_iso, now_iso)
        if a is None or sold is None:
            rows.append({"name": name, "error": True})
            print(f"  {name}: ERROR")
            continue
        # days-to-sell: map sold ItemIDs to their listing StartTime (last 120d of listings)
        start_map = get_start_map(s["token"], map_from_iso, now_iso)
        dts = []
        for iid, sold_at in sold["events"]:
            st = start_map.get(iid)
            if st:
                d = (sold_at - st).days
                if d >= 0:
                    dts.append(d)
        active = a["active"] or 1
        st_rate = 100.0 * sold["units"] / active
        rev_per = sold["revenue"] / active
        med_dts = statistics.median(dts) if dts else None
        aged_pct = 100.0 * a["aged_val"] / a["active_value"] if a["active_value"] else 0.0
        row = {
            "name": name, "error": False,
            "active": a["active"], "active_value": a["active_value"],
            "aged_ct": a["aged_ct"], "aged_val": a["aged_val"], "aged_pct": aged_pct,
            "units": sold["units"], "revenue": sold["revenue"],
            "st_rate": st_rate, "rev_per": rev_per, "med_dts": med_dts,
            "new7": new7 if new7 is not None else 0,
        }
        rows.append(row)
        dts_s = f"{med_dts:.0f}d" if med_dts is not None else "n/a"
        print(f"  {name}: ST {st_rate:.0f}% | {dts_s} to sell | aged {a['aged_ct']} (${a['aged_val']:,.0f}, {aged_pct:.0f}%) "
              f"| ${rev_per:,.0f}/listing | +{row['new7']} new(7d) | {a['active']} active")

    ok = [r for r in rows if not r.get("error")]
    ok.sort(key=lambda r: r["st_rate"], reverse=True)

    lines = [f"📊 *eBay Efficiency — Weekly* — 30-day window ({sales_from.strftime('%b %-d')}–{now.strftime('%b %-d, %Y')})\n"]
    for i, r in enumerate(ok):
        medal = MEDALS[i] if i < len(MEDALS) else f"{i+1}."
        dts_s = f"{r['med_dts']:.0f}d" if r["med_dts"] is not None else "n/a"
        lines.append(
            f"{medal} *{r['name']}* — *{r['st_rate']:.0f}% sell-through* "
            f"({r['units']} sold / {r['active']} active) | {dts_s} to sell | "
            f"aged>90d: {r['aged_ct']} (${r['aged_val']:,.0f}, {r['aged_pct']:.0f}%) | "
            f"${r['rev_per']:,.0f}/listing | +{r['new7']} new(7d)"
        )
    for r in [r for r in rows if r.get("error")]:
        lines.append(f"⚠️ *{r['name']}* — data unavailable")

    if ok:
        t_units = sum(r["units"] for r in ok)
        t_active = sum(r["active"] for r in ok)
        t_rev = sum(r["revenue"] for r in ok)
        t_agedct = sum(r["aged_ct"] for r in ok)
        t_agedval = sum(r["aged_val"] for r in ok)
        t_actval = sum(r["active_value"] for r in ok)
        t_new7 = sum(r["new7"] for r in ok)
        all_dts = [d for r in ok for d in ([r["med_dts"]] if r["med_dts"] is not None else [])]
        med_all = f"{statistics.median(all_dts):.0f}d" if all_dts else "n/a"
        st_all = 100.0 * t_units / t_active if t_active else 0.0
        aged_pct_all = 100.0 * t_agedval / t_actval if t_actval else 0.0
        lines.append(
            f"\n📦 *Channel: {st_all:.0f}% sell-through* ({t_units} sold / {t_active} active) | "
            f"~{med_all} median to sell | aged>90d: {t_agedct} (${t_agedval:,.0f}, {aged_pct_all:.0f}% of ${t_actval:,.0f}) | "
            f"${t_rev / t_active if t_active else 0:,.0f}/listing | +{t_new7} new(7d)"
        )
    msg = "\n".join(lines)
    print("\n" + msg)

    if do_post:
        payload = json.dumps({"text": msg}).encode("utf-8")
        with urlopen(Request(SLACK_WEBHOOK, data=payload, headers={"Content-Type": "application/json"}), timeout=15) as r:
            if r.read().decode().strip() != "ok":
                raise RuntimeError("Slack webhook non-ok")
        print("\n✅ Posted to Slack #ebay-performance")
    else:
        print("\n(dry run — not posted; add --post to send)")


if __name__ == "__main__":
    main()
