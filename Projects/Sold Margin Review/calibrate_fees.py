#!/usr/bin/env python3
"""
Valley Pawn — eBay fee calibration from OUR OWN orders (BLEND_V2 Phase 4)
=========================================================================

Replaces the fair-value blend's fee GUESS (13%) with a MEASUREMENT.

Data source: the same 5 store Trading-API tokens already flowing daily in
`~/Documents/valley-pawn/ebay_weekly_rankings.py` (imported, not copied —
one place owns those credentials). GetSellerTransactions with
IncludeFinalValueFee returns the REAL final value fee eBay charged us per
transaction — sanctioned API, no approval needed, our own data.

Writes `.channel_calibration.json`:
    {fee_rate, n_transactions, gross, fees, free_shipping_share, measured_at}
fair_value.py loads it at import and prefers it over the default.

Shipping absorbed on free-shipping listings is NOT visible via this API
(label cost isn't in GetSellerTransactions) — the category constants in
fair_value.py stay in force; this file measures how OFTEN we ship free so
the constants' weight is at least known. Run monthly-ish; it's cheap.

Usage:  python3 calibrate_fees.py           # last 30 days, all 5 stores
"""

from __future__ import annotations
import os, sys, json, datetime
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

_HERE    = os.path.dirname(os.path.abspath(__file__))
CAL_FILE = os.path.join(_HERE, ".channel_calibration.json")

sys.path.insert(0, os.path.expanduser("~/Documents/valley-pawn"))
import ebay_weekly_rankings as ewr          # tokens + creds live there, once

NS = ewr.NS


def _call(token: str, time_from: str, time_to: str, page: int) -> str:
    body = f"""<?xml version="1.0" encoding="utf-8"?>
<GetSellerTransactionsRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>
  <ModTimeFrom>{time_from}</ModTimeFrom>
  <ModTimeTo>{time_to}</ModTimeTo>
  <IncludeFinalValueFee>true</IncludeFinalValueFee>
  <DetailLevel>ReturnAll</DetailLevel>
  <Pagination><EntriesPerPage>100</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination>
</GetSellerTransactionsRequest>""".encode("utf-8")
    headers = {
        "X-EBAY-API-SITEID": "0",
        "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
        "X-EBAY-API-CALL-NAME": "GetSellerTransactions",
        "X-EBAY-API-APP-NAME": ewr.APP_ID,
        "X-EBAY-API-DEV-NAME": ewr.DEV_ID,
        "X-EBAY-API-CERT-NAME": ewr.CERT_ID,
        "X-EBAY-API-IAF-TOKEN": token,
        "Content-Type": "text/xml",
    }
    with urlopen(Request(ewr.EBAY_URL, data=body, headers=headers), timeout=40) as r:
        return r.read().decode("utf-8")


def _f(el, tag) -> float:
    v = el.findtext(f"{{{NS}}}{tag}")
    if v is None:
        v = el.findtext(f".//{{{NS}}}{tag}")
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def calibrate(days: int = 30) -> dict:
    now = datetime.datetime.now(datetime.timezone.utc)
    t_to = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    t_from = (now - datetime.timedelta(days=min(days, 30))).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    gross = fees = 0.0
    n = free_ship = 0
    per_store = {}
    for store in ewr.STORES:
        s_gross = s_fees = 0.0
        s_n = 0
        page = 1
        while True:
            try:
                root = ET.fromstring(_call(store["token"], t_from, t_to, page))
            except Exception as e:
                per_store[store["name"]] = {"error": str(e)}
                break
            if root.findtext(f"{{{NS}}}Ack", "") in ("Failure",):
                msg = root.findtext(f".//{{{NS}}}ShortMessage", "API error")
                per_store[store["name"]] = {"error": msg}
                break
            for txn in root.findall(f".//{{{NS}}}Transaction"):
                price = _f(txn, "TransactionPrice")
                fvf   = _f(txn, "FinalValueFee")
                if price <= 0 or fvf <= 0:
                    continue   # unpaid/cancelled/no-fee rows teach us nothing
                ship = 0.0
                sd = txn.find(f".//{{{NS}}}ShippingServiceSelected")
                if sd is not None:
                    ship = _f(sd, "ShippingServiceCost")
                if ship == 0.0:
                    free_ship += 1
                s_gross += price + ship
                s_fees  += fvf
                s_n     += 1
            if root.findtext(f".//{{{NS}}}HasMoreTransactions", "false").strip().lower() == "true":
                page += 1
            else:
                break
        else:
            continue
        if s_n:
            per_store[store["name"]] = {"n": s_n, "gross": round(s_gross, 2),
                                        "fees": round(s_fees, 2),
                                        "fee_rate": round(s_fees / s_gross, 4)}
        gross += s_gross; fees += s_fees; n += s_n

    out = {"measured_at": now.isoformat(timespec="seconds"),
           "window_days": days, "n_transactions": n,
           "gross": round(gross, 2), "fees": round(fees, 2),
           "fee_rate": round(fees / gross, 4) if gross else None,
           "free_shipping_share": round(free_ship / n, 3) if n else None,
           "per_store": per_store}

    # Only persist a calibration that is actually evidence: enough transactions
    # and a sane rate. A weird month must not silently poison every fair value.
    if n >= 25 and out["fee_rate"] and 0.05 <= out["fee_rate"] <= 0.25:
        tmp = CAL_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(out, f, indent=2)
        os.replace(tmp, CAL_FILE)
        out["persisted"] = True
    else:
        out["persisted"] = False
        out["why_not"] = (f"n={n} (<25) or fee_rate {out['fee_rate']} outside 5-25% — "
                          "defaults stay in force")
    return out


if __name__ == "__main__":
    r = calibrate(int(sys.argv[1]) if len(sys.argv) > 1 else 30)
    slim = {k: v for k, v in r.items() if k != "per_store"}
    print(json.dumps(slim, indent=2))
    for name, s in r["per_store"].items():
        print(f"  {name}: {json.dumps(s)}")
