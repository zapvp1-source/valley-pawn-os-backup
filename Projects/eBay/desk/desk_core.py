#!/usr/bin/env python3
"""eBay Desk — core logic (step 1 of EBAY_DESK_DIRECT_LISTING_DESIGN_2026-11-17.md).

OFFLINE BY CONSTRUCTION: this module imports no network library and no eBay token file.
It only turns files into plans:
  - eBay GetOrders XML (saved to disk)         -> orders
  - orders                                     -> "Ring these sales" queue (per store)
  - queue + Bravo daily sold export CSVs       -> rung / not rung after 24 h
  - Bravo sold export + live eBay listing snap -> double-sell list (PLAN ONLY, never ends a listing)
Nothing here writes to eBay or Bravo. Python 3.9 stdlib only.
"""
import csv, glob, json, os, re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

NS = "urn:ebay:apis:eBLBaseComponents"
STORE_CODE = {"Culpeper": "CUL", "Roanoke": "ROA", "Waynesboro": "WAY", "Harrisonburg": "HAR", "Lexington": "LEX"}
# Same rule as engine/ebay_common.py CODE_RE (tightened 2026-09-17): store prefix + 5 or more digits.
CODE_RE = re.compile(r"\(((?:VAP|VP|VA|CUL|ROA|WAY|HAR|LEX)\d{5,})\)")
BARE_CODE_RE = re.compile(r"^(?:VAP|VP|VA|CUL|ROA|WAY|HAR|LEX)\d{5,}$")
NOT_RUNG_AFTER_HOURS = 24


def _q(tag):
    return "{%s}%s" % (NS, tag)


def _txt(el, path, default=""):
    cur = el
    for part in path.split("/"):
        cur = cur.find(_q(part)) if cur is not None else None
    return (cur.text or default) if cur is not None else default


def _dt(s):
    """eBay UTC timestamp '2026-11-17T15:04:05.000Z' -> aware datetime."""
    s = s.strip().replace("Z", "")
    s = s.split(".")[0]
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)


def bravo_code(sku, title):
    """Bravo item number for an eBay line: SKU first (desk listings), else the (CODE) in the title
    (Bravo-created listings). Returns '' when neither holds a real Bravo number."""
    sku = (sku or "").strip().upper()
    if BARE_CODE_RE.match(sku):
        return sku
    m = CODE_RE.search(title or "")
    return m.group(1).upper() if m else ""


def parse_get_orders(xml_text, store):
    """One GetOrders response -> list of line dicts (one per transaction line).
    Cancelled orders and orders that are not paid are skipped: nothing to ring."""
    root = ET.fromstring(xml_text)
    ack = root.findtext(_q("Ack"), "")
    if ack not in ("Success", "Warning"):
        raise ValueError("GetOrders Ack=%r for %s" % (ack, store))
    out = []
    for o in root.iter(_q("Order")):
        status = _txt(o, "OrderStatus")
        cancel = _txt(o, "CancelStatus", "NotApplicable")
        paid = _txt(o, "PaidTime")
        if status in ("Cancelled", "CancelPending", "Inactive") or cancel in ("CancelComplete", "CancelCompleteForFullRefund", "CancelRequested", "CancelPending"):
            continue
        if not paid:
            continue
        order_id = _txt(o, "OrderID")
        for tr in o.iter(_q("Transaction")):
            title = _txt(tr, "Item/Title")
            sku = _txt(tr, "Item/SKU") or _txt(tr, "Variation/SKU")
            qty = int(_txt(tr, "QuantityPurchased", "1") or 1)
            price = float(_txt(tr, "TransactionPrice", "0") or 0)
            out.append({
                "store": store, "order_id": order_id, "line_id": _txt(tr, "OrderLineItemID") or order_id,
                "item_id": _txt(tr, "Item/ItemID"), "title": title, "sku": sku,
                "bravo_no": bravo_code(sku, title), "qty": qty,
                "ring_price": round(price * qty, 2), "paid_utc": _dt(paid).isoformat(),
                "buyer": _txt(o, "BuyerUserID"),
            })
    return out


def build_ring_queue(lines, prior=None):
    """Merge freshly pulled lines into the saved queue. Key = store + line_id, so re-pulling the
    same order never duplicates it and never resets a line a store already marked rung."""
    q = {(r["store"], r["line_id"]): dict(r) for r in (prior or [])}
    for ln in lines:
        k = (ln["store"], ln["line_id"])
        if k in q:
            continue
        row = dict(ln)
        row["state"] = "needs_number" if not ln["bravo_no"] else "to_ring"
        q[k] = row
    return sorted(q.values(), key=lambda r: (r["store"], r["paid_utc"], r["line_id"]))


def money(v):
    """'$1,234.50' -> 1234.5 ; '(5.00)' -> -5.0 ; blank or junk -> 0.0"""
    t = (v or "").strip().replace("$", "").replace(",", "")
    neg = t.startswith("(") and t.endswith(")")
    try:
        x = float(t.strip("()") or 0)
    except ValueError:
        return 0.0
    return -x if neg else x


def load_bravo_sold(paths):
    """Bravo daily 'sold-discount-detail' CSVs (Number,Status,Category,Description,Cost,Price,
    Last Sold Price,Date) -> {item number: {'date': date, 'price': float}} (latest sale wins)."""
    sold = {}
    for p in paths:
        with open(p, newline="", encoding="utf-8", errors="ignore") as fh:
            for r in csv.DictReader(fh):
                num = (r.get("Number") or "").strip().upper()
                if not num or (r.get("Status") or "").strip().upper() != "SOLD":
                    continue
                try:
                    d = datetime.strptime((r.get("Date") or "").strip(), "%m/%d/%Y").date()
                except ValueError:
                    continue
                price = money(r.get("Last Sold Price"))
                if num not in sold or d >= sold[num]["date"]:
                    sold[num] = {"date": d, "price": price}
    return sold


def check_rung(queue, bravo_sold, now_utc):
    """Mark each queue line: rung (Bravo shows the item SOLD on/after the eBay paid date),
    to_ring (still inside 24 h), or not_rung (older than 24 h and Bravo has no sale).
    A Bravo sale dated BEFORE the eBay order is not this sale and does not count."""
    out = []
    for r in queue:
        row = dict(r)
        if row["state"] == "needs_number":
            out.append(row); continue
        paid = datetime.fromisoformat(row["paid_utc"])
        hit = bravo_sold.get(row["bravo_no"])
        if hit and hit["date"] >= (paid - timedelta(hours=5)).date():
            row["state"] = "rung"
            row["bravo_sold_date"] = hit["date"].isoformat()
            row["price_gap"] = round(hit["price"] - row["ring_price"], 2)
        elif now_utc - paid > timedelta(hours=NOT_RUNG_AFTER_HOURS):
            row["state"] = "not_rung"
            row["hours_open"] = int((now_utc - paid).total_seconds() // 3600)
        else:
            row["state"] = "to_ring"
        out.append(row)
    return out


def double_sell_plan(active_by_store, bravo_sold, ebay_sold_codes=()):
    """Items Bravo shows SOLD that are still live on eBay and were not sold on eBay.
    Returns a PLAN (list of dicts). It never ends a listing."""
    skip = {c.upper() for c in ebay_sold_codes}
    plan = []
    for store, items in active_by_store.items():
        for it in items:
            code = bravo_code(it.get("SKU"), it.get("Title"))
            if code and code in bravo_sold and code not in skip:
                plan.append({"store": store, "item_id": it.get("ItemID"), "bravo_no": code,
                             "title": it.get("Title"), "sold_in_store": bravo_sold[code]["date"].isoformat(),
                             "action": "END_LISTING (planned, not sent)"})
    return plan


def store_summary(checked):
    s = {}
    for r in checked:
        d = s.setdefault(r["store"], {"to_ring": 0, "rung": 0, "not_rung": 0, "needs_number": 0, "not_rung_dollars": 0.0})
        d[r["state"]] += 1
        if r["state"] == "not_rung":
            d["not_rung_dollars"] = round(d["not_rung_dollars"] + r["ring_price"], 2)
    return s
