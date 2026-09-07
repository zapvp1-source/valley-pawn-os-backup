#!/usr/bin/env python3
"""Valley Pawn eBay engine — Layer 1: nightly SNAPSHOT (read-only).

One pull per store per day. Everything downstream (rules, apply, publish) reads these files
instead of calling eBay again.

  engine/data/YYYY-MM-DD/<Store>.json   full per-store snapshot
  engine/data/latest/<Store>.json       copy of the newest complete snapshot per store
  engine/data/latest/channel.json       roll-up + completeness flags (Rule 18: a store is
                                         either COMPLETE or absent — never partial)
  engine/data/item_cache.json           GetItem detail cache (refreshed when new / >7 days /
                                         title or price changed) — keeps daily GetItem volume low

Read calls only: GetMyeBaySelling, GetItem, GetSellerTransactions, GetAccount, GetStore,
GetMyMessages, GetFeedback, GetBestOffers. No Revise/End/Respond anywhere in this file.
Usage: ebay_snapshot.py [Store|all] [--max-getitem N]
"""
import json, os, sys, time, shutil
from datetime import datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ebay_common import *  # noqa

now = datetime.now(timezone.utc)
TODAY = now.strftime("%Y-%m-%d")
CACHE = os.path.join(DATA_DIR, "item_cache.json")
CACHE_MAX_AGE_DAYS = 7
MARKDOWN_STATE = os.path.expanduser("~/ebay_markdown_state.json")
TERMINAL_STATE = os.path.expanduser("~/ebay_markdown_terminal_state.json")


def q(n): return "{%s}%s" % (NS, n)


def T(el, tag, d=None):
    if el is None: return d
    x = el.find(q(tag))
    return x.text if x is not None and x.text is not None else d


def dt(s):
    try:
        return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def item_detail(r):
    """Flatten a GetItem response into the fields the rules layer needs."""
    it = r.find(".//" + q("Item"))
    rp = it.find(q("ReturnPolicy")); bo = it.find(q("BestOfferDetails")); pd = it.find(q("PictureDetails"))
    ld = it.find(q("ListingDetails")); ss = it.find(q("SellingStatus"))
    specifics = {}
    for nv in it.findall(".//" + q("ItemSpecifics") + "/" + q("NameValueList")):
        specifics[T(nv, "Name", "")] = [v.text for v in nv.findall(q("Value")) if v.text]
    price = T(ss, "CurrentPrice") or T(it, "StartPrice") or T(it, "BuyItNowPrice")
    return {
        "ItemID": T(it, "ItemID"), "Title": T(it, "Title", ""), "SKU": T(it, "SKU", "") or "",
        "price": float(price) if price else None, "currency": T(it, "Currency"),
        "start": T(ld, "StartTime"), "end": T(ld, "EndTime"), "status": T(ss, "ListingStatus"),
        "qty": int(T(it, "Quantity", "1") or 1), "qty_sold": int(T(ss, "QuantitySold", "0") or 0),
        "category_id": T(it.find(q("PrimaryCategory")), "CategoryID"),
        "category_name": T(it.find(q("PrimaryCategory")), "CategoryName"),
        "condition_id": T(it, "ConditionID"), "condition": T(it, "ConditionDisplayName"),
        "pics": len(pd.findall(q("PictureURL"))) if pd is not None else 0,
        "pic_urls": [p.text for p in pd.findall(q("PictureURL"))] if pd is not None else [],
        "specifics": specifics, "specifics_count": len(specifics),
        "best_offer": (T(bo, "BestOfferEnabled") or "false").lower() == "true",
        "bo_auto_accept": T(it.find(q("ListingDetails")), "BestOfferAutoAcceptPrice"),
        "bo_min_accept": T(it.find(q("ListingDetails")), "MinimumBestOfferPrice"),
        "dispatch_max": T(it, "DispatchTimeMax"),
        "returns_accepted": T(rp, "ReturnsAcceptedOption"), "returns_within": T(rp, "ReturnsWithinOption"),
        "return_shipping_paid_by": T(rp, "ShippingCostPaidByOption"),
        "watch_count": T(it, "WatchCount"), "hit_count": T(it, "HitCount"),
        "site": T(it, "Site"), "listing_type": T(it, "ListingType"),
        "url": T(ld, "ViewItemURL"),
        "fetched": TODAY,
    }


def refresh_details(tok, actives, cache, budget):
    """GetItem for items that are new, stale, or whose title/price changed. Returns calls used."""
    used = 0
    for a in actives:
        iid = a["ItemID"]
        c = cache.get(iid)
        stale = (c is None or (now - dt(c["fetched"] + "T00:00:00")).days > CACHE_MAX_AGE_DAYS
                 or c.get("Title") != a["Title"] or (a["StartPrice"] and c.get("price") not in (None, float(a["StartPrice"]))))
        if not stale: continue
        if used >= budget: break
        r, err = get_item(tok, iid)
        used += 1
        if r is not None:
            cache[iid] = item_detail(r)
        time.sleep(0.15)
    return used


def sold(tok, days_back=90):
    out = []
    for chunk in range(0, days_back, 30):
        e = now - timedelta(days=chunk); s = now - timedelta(days=min(chunk + 30, days_back))
        page = 1
        while True:
            r = call(tok, "GetSellerTransactions",
                     "<ModTimeFrom>%s</ModTimeFrom><ModTimeTo>%s</ModTimeTo><IncludeContainingOrder>true</IncludeContainingOrder>"
                     "<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination><DetailLevel>ReturnAll</DetailLevel>"
                     % (s.strftime("%Y-%m-%dT%H:%M:%S.000Z"), e.strftime("%Y-%m-%dT%H:%M:%S.000Z"), page))
            if not ack_ok(r): break
            for tx in r.findall(".//" + q("Transaction")):
                it = tx.find(q("Item")); ld = it.find(q("ListingDetails")) if it is not None else None
                start = T(ld, "StartTime"); created = T(tx, "CreatedDate"); amt = T(tx, "TransactionPrice")
                st, ct = dt(start or ""), dt(created or "")
                out.append({"ItemID": T(it, "ItemID") if it is not None else None, "Title": T(it, "Title") if it is not None else None,
                            "SKU": (T(it, "SKU") if it is not None else None) or "",
                            "price": float(amt) if amt else None, "created": created,
                            "qty": int(T(tx, "QuantityPurchased", "1") or 1),
                            "days_to_sell": (ct - st).days if (st and ct) else None,
                            "order_id": T(tx.find(q("ContainingOrder")), "OrderID"),
                            "buyer": T(tx.find(q("Buyer")), "UserID")})
            pr = r.find(".//" + q("PaginationResult"))
            if page >= int(T(pr, "TotalNumberOfPages", "1") or 1): break
            page += 1
    seen, ded = set(), []
    for o in out:
        k = (o["ItemID"], o["created"])
        if k in seen: continue
        seen.add(k); ded.append(o)
    return ded


FEE_KEYWORDS = [("promoted", "promoted_listings"), ("ad fee", "promoted_listings"), ("final value", "final_value_fee"),
                ("fvf", "final_value_fee"), ("insertion", "insertion"), ("international", "international"),
                ("return", "return_shipping"), ("subscription", "subscription"), ("store", "subscription")]


def fees(tok, days_back=90):
    ents = []
    for c in range(0, days_back, 30):
        e = now - timedelta(days=c); b = now - timedelta(days=min(c + 30, days_back))
        page = 1
        while True:
            r = call(tok, "GetAccount",
                     "<AccountHistorySelection>BetweenSpecifiedDates</AccountHistorySelection><BeginDate>%s</BeginDate><EndDate>%s</EndDate>"
                     "<DetailLevel>ReturnAll</DetailLevel><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>"
                     % (b.strftime("%Y-%m-%dT%H:%M:%S.000Z"), e.strftime("%Y-%m-%dT%H:%M:%S.000Z"), page))
            if not ack_ok(r): break
            for en in r.findall(".//" + q("AccountEntry")):
                typ = T(en, "AccountDetailsEntryType") or ""; desc = T(en, "Description") or ""
                amt = T(en, "GrossDetailAmount")
                try: a = abs(float(amt)) if amt else 0.0
                except Exception: a = 0.0
                cat = "other"
                for kw, c2 in FEE_KEYWORDS:
                    if kw in (typ + " " + desc).lower(): cat = c2; break
                if cat == "other" and typ == "CustomCode": cat = "final_value_fee"  # observed 2026-08-31
                ents.append({"type": typ, "desc": desc[:80], "amt": a, "category": cat, "date": T(en, "Date"), "ItemID": T(en, "ItemID")})
            pr = r.find(".//" + q("PaginationResult"))
            if page >= int(T(pr, "TotalNumberOfPages", "1") or 1): break
            page += 1
    return ents


def messages(tok):
    out, page, tot = [], 1, 1
    while page <= min(tot, 3):
        r = call(tok, "GetMyMessages",
                 "<StartTime>%s</StartTime><EndTime>%s</EndTime><DetailLevel>ReturnHeaders</DetailLevel>"
                 "<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>"
                 % ((now - timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%S.000Z"), now.strftime("%Y-%m-%dT%H:%M:%S.000Z"), page))
        if not ack_ok(r): break
        for m in r.findall(".//" + q("Message")):
            s = (T(m, "Subject") or "")
            sl = s.lower()
            cat = "return_refund" if any(k in sl for k in ("return", "refund")) else \
                  "case_dispute" if any(k in sl for k in ("case", "dispute", "item not")) else \
                  "offer" if "offer" in sl else "question" if "question" in sl else "other"
            out.append({"id": T(m, "MessageID"), "read": (T(m, "Read") or "").lower() == "true", "subject": s[:120],
                        "sender": T(m, "Sender"), "date": T(m, "ReceiveDate"), "ItemID": T(m, "ItemID"), "category": cat})
        tot = int(T(r.find(".//" + q("PaginationResult")), "TotalNumberOfPages", "1") or 1)
        page += 1
    return out, tot > 3


def feedback(tok):
    r = call(tok, "GetFeedback", "<DetailLevel>ReturnAll</DetailLevel><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>1</PageNumber></Pagination>")
    rec = {"score": T(r, "FeedbackScore"), "positive_pct": T(r, "PositiveFeedbackPercent"), "recent": [], "neg_neutral": []}
    for f in r.findall(".//" + q("FeedbackDetail")):
        row = {"type": T(f, "CommentType"), "date": T(f, "CommentTime"), "ItemID": T(f, "ItemID"), "id": T(f, "FeedbackID")}
        rec["recent"].append(row)
        if row["type"] in ("Negative", "Neutral"):
            rec["neg_neutral"].append(dict(row, text=T(f, "CommentText"), buyer=T(f, "CommentingUser"), response=T(f, "Response")))
    def pct(days):
        w = [c["type"] for c in rec["recent"] if dt(c["date"] or "") and dt(c["date"]) >= now - timedelta(days=days)]
        return (round(100.0 * sum(1 for x in w if x == "Positive") / len(w), 1) if w else None, len(w))
    rec["pos_1mo"], rec["pos_6mo"], rec["pos_12mo"] = pct(30), pct(182), pct(365)
    return rec


def best_offers(tok):
    out = []
    r = call(tok, "GetBestOffers", "<BestOfferStatus>Active</BestOfferStatus><DetailLevel>ReturnAll</DetailLevel>")
    for arr in r.findall(".//" + q("BestOfferArray")):
        for bo in arr.findall(q("BestOffer")):
            exp = T(bo, "ExpirationTime"); et = dt(exp or "")
            out.append({"id": T(bo, "BestOfferID"), "status": T(bo, "Status"), "expire": exp, "ItemID": T(bo, "ItemID"),
                        "price": T(bo, "Price"), "qty": T(bo, "Quantity"), "buyer": T(bo.find(q("Buyer")), "UserID"),
                        "hours_left": round((et - now).total_seconds() / 3600, 1) if et else None})
    return out


def snapshot_store(store, cache, budget):
    tok = token_for(store)
    rec = {"store": store, "date": TODAY, "pull_time_utc": now.isoformat(), "complete": True, "errors": {}}
    actives = active_items(tok)                      # hard requirement — if this fails, store is incomplete
    used = refresh_details(tok, actives, cache, budget)
    rec["active"] = []
    for a in actives:
        d = dict(cache.get(a["ItemID"], {}))
        d.update({"ItemID": a["ItemID"], "Title": a["Title"], "SKU": a["SKU"] or d.get("SKU", ""),
                  "list_price": float(a["StartPrice"]) if a["StartPrice"] else d.get("price"),
                  "start": a["StartTime"] or d.get("start")})
        st = dt(d.get("start") or "")
        d["days_live"] = (now - st).days if st else None
        d["detail_cached"] = a["ItemID"] in cache
        m = CODE_RE.search(a["Title"])
        d["bravo_code"] = d["SKU"] or (m.group(1) if m else "")
        rec["active"].append(d)
    rec["getitem_calls"] = used
    rec["detail_coverage"] = round(100.0 * sum(1 for x in rec["active"] if x["detail_cached"]) / max(1, len(rec["active"])), 1)
    for key, fn in (("sold90", lambda: sold(tok)), ("fees90", lambda: fees(tok)), ("feedback", lambda: feedback(tok)),
                    ("best_offers", lambda: best_offers(tok))):
        try:
            rec[key] = fn()
        except Exception as e:
            rec[key] = None; rec["errors"][key] = str(e)[:200]; rec["complete"] = False
    try:
        rec["messages"], rec["messages_truncated"] = messages(tok)
    except Exception as e:
        rec["messages"] = None; rec["errors"]["messages"] = str(e)[:200]; rec["complete"] = False
    try:
        r = call(tok, "GetStore", "")
        rec["store_subscription"] = T(r.find(q("Store")), "Subscription") if r.find(q("Store")) is not None else None
    except Exception as e:
        rec["store_subscription"] = None
    return rec


def rollup(stores_done):
    ch = {"date": TODAY, "stores": {}, "complete_stores": [], "incomplete_stores": []}
    for s in STORE_ORDER:
        p = os.path.join(DATA_DIR, "latest", s + ".json")
        if not os.path.exists(p):
            ch["incomplete_stores"].append(s); continue
        d = json.load(open(p))
        if d.get("date") != TODAY or not d.get("complete"):
            ch["incomplete_stores"].append(s)
        else:
            ch["complete_stores"].append(s)
        act = d["active"]; sold90 = d.get("sold90") or []; fees90 = d.get("fees90") or []
        val = sum((x.get("list_price") or 0) for x in act)
        aged = [x for x in act if (x.get("days_live") or 0) > 90]
        ch["stores"][s] = {
            "date": d.get("date"), "complete": d.get("complete"), "active": len(act), "listed_value": round(val, 2),
            "aged90": len(aged), "aged90_value": round(sum((x.get("list_price") or 0) for x in aged), 2),
            "sold90_units": len(sold90), "sold90_revenue": round(sum((x.get("price") or 0) * x.get("qty", 1) for x in sold90), 2),
            "fees90": round(sum(x["amt"] for x in fees90), 2),
            "sku_set": sum(1 for x in act if x.get("SKU")), "pics_lt8": sum(1 for x in act if x.get("detail_cached") and x.get("pics", 0) < 8),
            "specifics_lt5": sum(1 for x in act if x.get("detail_cached") and x.get("specifics_count", 0) < 5),
            "unread_msgs": sum(1 for m in (d.get("messages") or []) if not m["read"]),
            "unread_return_refund": sum(1 for m in (d.get("messages") or []) if not m["read"] and m["category"] == "return_refund"),
            "open_offers": len(d.get("best_offers") or []),
            "offers_expiring_48h": sum(1 for o in (d.get("best_offers") or []) if (o.get("hours_left") or 999) < 48),
            "feedback_score": (d.get("feedback") or {}).get("score"), "pos_12mo": (d.get("feedback") or {}).get("pos_12mo"),
            "neg_neutral_unanswered_12mo": sum(1 for f in ((d.get("feedback") or {}).get("neg_neutral") or [])
                                              if not f.get("response") and dt(f["date"] or "") and dt(f["date"]) >= now - timedelta(days=365)),
            "detail_coverage": d.get("detail_coverage"),
        }
    json.dump(ch, open(os.path.join(DATA_DIR, "latest", "channel.json"), "w"), indent=1)
    return ch


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    budget = int(sys.argv[sys.argv.index("--max-getitem") + 1]) if "--max-getitem" in sys.argv else 700
    stores = STORE_ORDER if (not args or args[0].lower() == "all") else [args[0]]
    os.makedirs(os.path.join(DATA_DIR, TODAY), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "latest"), exist_ok=True)
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    for s in stores:
        t0 = time.time()
        try:
            rec = snapshot_store(s, cache, budget)
        except Exception as e:
            print("%-12s FAILED (no file written): %s" % (s, str(e)[:160]))
            continue
        json.dump(cache, open(CACHE, "w"))
        p = os.path.join(DATA_DIR, TODAY, s + ".json")
        json.dump(rec, open(p, "w"), indent=1)
        if rec["complete"]:
            shutil.copy(p, os.path.join(DATA_DIR, "latest", s + ".json"))
        print("%-12s active %3d | detail %5.1f%% (%d GetItem) | sold90 %3s | fees90 %3s | msgs %3s | offers %2s | %s | %.0fs"
              % (s, len(rec["active"]), rec["detail_coverage"], rec["getitem_calls"],
                 len(rec["sold90"] or []), len(rec["fees90"] or []), len(rec["messages"] or []), len(rec["best_offers"] or []),
                 "COMPLETE" if rec["complete"] else "INCOMPLETE %s" % rec["errors"], time.time() - t0))
    ch = rollup(stores)
    print("channel.json: complete=%s incomplete=%s" % (ch["complete_stores"], ch["incomplete_stores"]))


if __name__ == "__main__":
    main()
