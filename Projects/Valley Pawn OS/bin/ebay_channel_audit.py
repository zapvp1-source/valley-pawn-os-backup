#!/usr/bin/env python3
"""ebay_channel_audit.py — native replacement for Cowork `ebay-weekly-channel-audit` (Mon 11:45 ET ->
#ebay-performance C0ANVN5KX4Y). Built 2026-10-14 (Mac-first). Cloud copy trig_01SK1GpYNeXBW4K1VDhgtRM4
has been dark/partial since 9/14 because a cloud session cannot read ~/.vp_secrets/ebay_store_tokens.py.

READ-ONLY END TO END (ebay-context hard rules; the SKILL's CRITICAL SAFETY RULE). The only eBay calls in
this file are GetMyeBaySelling, GetSellerTransactions, GetAccount, GetStore, GetItem, GetMyMessages,
GetFeedback, GetBestOffers. There is no Revise/End/Add/Relist/Respond/SetUserPreferences anywhere in it,
and it never exec()s or imports any ~/ebay_*.py (credentials come only from ~/.vp_secrets).
Best Offer is reported, never switched (Rule 2); video-game listings that take offers are FLAGGED only.

Method = the last good live runs (eBay/audit_weekly/2026-09-07/{audit,sample_getitem,analyze,analyze2}.py):
  pull all 5 stores (active, sold 90d in 30-day chunks, fees 90d via GetAccount in 30-day chunks with the
  9/07 fee-type mapping, GetStore, messages 60d, feedback, active Best Offers) + ~/ebay_markdown_state.json;
  GetItem sample for the listing-quality fields the bulk call leaves blank (all listings at stores with
  <=40, 60 at random elsewhere); week-over-week deltas vs the newest prior folder that holds a LIVE pull.
Outputs (live only): eBay/audit_weekly/<DATE>/{raw_pull.json, sample_results.json, summary.json, summary.md},
the #ebay-performance post (the 9/07 layout + the SKILL's headline line), a dated CHANGELOG line, and an
OPEN_ITEMS_REGISTER row for anything actionable. NOT done natively: the claude.ai "eBay Channel Pulse"
artifact refresh (SKILL step 6) — a Mac script cannot publish a claude.ai artifact.

  ebay_channel_audit.py --render     live pull, writes ONLY to fleet/test_output/ebay_channel_audit_render/,
                                     prints the post; no Slack, no CHANGELOG, no register
  ebay_channel_audit.py --send       (launchd wrapper; gated by vp_live.sh)
  ebay_channel_audit.py --render --from DIR   re-analyse an existing raw_pull.json/sample_results.json
Failure policy v3: a store that fails is labelled PARTIAL in the post (the SKILL's rule); no token / all
stores failed / fee types unrecognisable -> ONE ledger row, nothing posted.
"""
import datetime as dt
import json
import os
import random
import re
import statistics
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

AGENT = "ebay-weekly-channel-audit"
ETZ = ZoneInfo("America/New_York")
HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
CHANGELOG = os.path.join(OS_DIR, "CHANGELOG.md")
REGISTER = os.path.join(HOME, "Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md")
BASE = os.path.join(HOME, "Documents/Claude/Projects/eBay/audit_weekly")
RENDER_DIR = os.path.join(OS_DIR, "fleet/test_output/ebay_channel_audit_render")
MD_STATE = os.path.join(HOME, "ebay_markdown_state.json")
CH = "C0ANVN5KX4Y"
NS = "urn:ebay:apis:eBLBaseComponents"
URL = "https://api.ebay.com/ws/api.dll"
STORES = ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]
READ_CALLS = {"GetMyeBaySelling", "GetSellerTransactions", "GetAccount", "GetStore", "GetItem",
              "GetMyMessages", "GetFeedback", "GetBestOffers"}
GAME_RE = re.compile(r"video game|\b(ps[1-5]|playstation|xbox|nintendo|switch oled|game ?boy|game ?cube|wii|sega|atari|n64)\b", re.I)

RENDER = "--render" in sys.argv
NOW = dt.datetime.now(dt.timezone.utc)
DATE = dt.datetime.now(ETZ).strftime("%Y-%m-%d")
if "--render" in sys.argv and "--as-of" in sys.argv:      # render-only replay label (compare with a past post)
    DATE = sys.argv[sys.argv.index("--as-of") + 1]


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def log(*a):
    print(dt.datetime.now(ETZ).strftime("%H:%M:%S"), *a, flush=True)


def ledger(sentence, needs="no"):
    if RENDER:
        log("[render] would write ledger row:", sentence)
        return
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n"
                % (dt.datetime.now(ETZ).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence, needs))


# ---------------------------------------------------------------- eBay Trading API (read calls only)
def load_tokens():
    sys.path.insert(0, os.path.join(HOME, ".vp_secrets"))
    from ebay_store_tokens import STORES as TOK, APP_ID, DEV_ID, CERT_ID  # never hardcode
    return {s["name"]: s["token"] for s in TOK}, (APP_ID, DEV_ID, CERT_ID)


def call(tok, keys, name, inner, tries=3):
    if name not in READ_CALLS:                       # belt and braces: this task never writes to eBay
        raise RuntimeError("refusing non-read eBay call %s" % name)
    body = ('<?xml version="1.0" encoding="utf-8"?><%sRequest xmlns="%s">'
            '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>%s</%sRequest>'
            % (name, NS, tok, inner, name)).encode()
    h = {"X-EBAY-API-SITEID": "0", "X-EBAY-API-COMPATIBILITY-LEVEL": "967", "X-EBAY-API-CALL-NAME": name,
         "X-EBAY-API-APP-NAME": keys[0], "X-EBAY-API-DEV-NAME": keys[1], "X-EBAY-API-CERT-NAME": keys[2],
         "X-EBAY-API-IAF-TOKEN": tok, "Content-Type": "text/xml"}
    last = None
    for i in range(tries):
        try:
            with urlopen(Request(URL, data=body, headers=h), timeout=120) as r:
                return ET.fromstring(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            time.sleep(3 * (i + 1))
    raise RuntimeError("%s failed: %s" % (name, str(last)[:200]))


def q(n):
    return "{%s}%s" % (NS, n)


def T(el, tag, d=None):
    if el is None:
        return d
    x = el.find(q(tag))
    return x.text if x is not None and x.text is not None else d


def iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def pdate(s):
    try:
        return dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
    except Exception:
        return None


def aging_bucket(days):
    if days is None:
        return "unknown"
    for lim, b in ((30, "0-30"), (60, "31-60"), (90, "61-90"), (180, "91-180"), (365, "181-365")):
        if days <= lim:
            return b
    return "365+"


def active_listings(tok, keys):
    items, page = [], 1
    while True:
        r = call(tok, keys, "GetMyeBaySelling",
                 "<ActiveList><Include>true</Include><Pagination><EntriesPerPage>200</EntriesPerPage>"
                 "<PageNumber>%d</PageNumber></Pagination></ActiveList><DetailLevel>ReturnAll</DetailLevel>" % page)
        if T(r, "Ack") == "Failure":
            raise RuntimeError("GetMyeBaySelling Failure: %s" % (r.findtext(".//" + q("LongMessage")) or "")[:150])
        al = r.find(q("ActiveList"))
        if al is None:
            break
        items.extend(al.findall(q("ItemArray") + "/" + q("Item")) or al.findall(".//" + q("Item")))
        tot = int(T(al.find(q("PaginationResult")), "TotalNumberOfPages", "1") or 1)
        if page >= tot:
            break
        page += 1
    return [parse_item(i) for i in items]


def parse_item(it):
    ld, sp = it.find(q("ListingDetails")), it.find(q("SellingStatus"))
    start = T(ld, "StartTime")
    st = pdate(start) if start else None
    days = (NOW - st).days if st else None
    price = None
    for p in (q("CurrentPrice"), q("ConvertedCurrentPrice")):
        x = sp.find(p) if sp is not None else None
        if x is not None:
            try:
                price = float(x.text)
                break
            except Exception:
                pass
    if price is None:
        x = it.find(q("BuyItNowPrice"))
        try:
            price = float(x.text) if x is not None else None
        except Exception:
            price = None
    title = T(it, "Title", "") or ""
    return {"id": T(it, "ItemID"), "title": title, "price": price, "qty": int(T(it, "Quantity", "1") or 1),
            "days_live": days, "start": start, "aging_bucket": aging_bucket(days), "sku": T(it, "SKU")}


def sold(tok, keys, days_back=90):
    out = []
    for chunk in range(0, days_back, 30):
        e = NOW - dt.timedelta(days=chunk)
        s = NOW - dt.timedelta(days=min(chunk + 30, days_back))
        page = 1
        while True:
            r = call(tok, keys, "GetSellerTransactions",
                     "<ModTimeFrom>%s</ModTimeFrom><ModTimeTo>%s</ModTimeTo><IncludeContainingOrder>true</IncludeContainingOrder>"
                     "<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>"
                     "<DetailLevel>ReturnAll</DetailLevel>" % (iso(s), iso(e), page))
            if T(r, "Ack") == "Failure":
                raise RuntimeError("GetSellerTransactions Failure")
            for tx in r.findall(".//" + q("Transaction")):
                it = tx.find(q("Item"))
                amt, created = T(tx, "TransactionPrice"), T(tx, "CreatedDate")
                ld = it.find(q("ListingDetails")) if it is not None else None
                start = T(ld, "StartTime") if ld is not None else None
                dts = None
                if start and created and pdate(start) and pdate(created):
                    dts = (pdate(created) - pdate(start)).days
                out.append({"item_id": T(it, "ItemID") if it is not None else None,
                            "price": float(amt) if amt else None, "created": created,
                            "qty": int(T(tx, "QuantityPurchased", "1") or 1), "days_to_sell": dts})
            tot = int(T(r.find(".//" + q("PaginationResult")), "TotalNumberOfPages", "1") or 1)
            if page >= tot:
                break
            page += 1
    seen, ded = set(), []
    for o in out:
        k = (o["item_id"], o["created"])
        if k not in seen:
            seen.add(k)
            ded.append(o)
    return ded


def fees(tok, keys, days_back=90):
    ents = []
    for c in range(0, days_back, 30):
        e = NOW - dt.timedelta(days=c)
        b = NOW - dt.timedelta(days=min(c + 30, days_back))
        page = 1
        while True:
            r = call(tok, keys, "GetAccount",
                     "<AccountHistorySelection>BetweenSpecifiedDates</AccountHistorySelection><BeginDate>%s</BeginDate>"
                     "<EndDate>%s</EndDate><DetailLevel>ReturnAll</DetailLevel><Pagination><EntriesPerPage>200</EntriesPerPage>"
                     "<PageNumber>%d</PageNumber></Pagination>" % (iso(b), iso(e), page))
            if T(r, "Ack") == "Failure":
                raise RuntimeError("GetAccount Failure")
            for en in r.findall(".//" + q("AccountEntry")):
                try:
                    amt = abs(float(T(en, "GrossDetailAmount") or 0))
                except Exception:
                    amt = 0.0
                ents.append({"type": T(en, "AccountDetailsEntryType"), "amt": amt, "date": T(en, "Date")})
            tot = int(T(r.find(".//" + q("PaginationResult")), "TotalNumberOfPages", "1") or 1)
            if page >= tot:
                break
            page += 1
    return ents


def classify_message(subject):
    s = (subject or "").lower()
    if any(k in s for k in ("return", "refund")):
        return "return_refund"
    if any(k in s for k in ("case", "dispute", "inr", "inad", "item not")):
        return "case_dispute"
    return "other"


def messages_feedback(tok, keys):
    rec = {"messages": [], "feedback": {}, "neg_neutral": [], "err": []}
    win = "<StartTime>%s</StartTime><EndTime>%s</EndTime>" % (iso(NOW - dt.timedelta(days=60)), iso(NOW))
    try:
        page, tot = 1, 1
        while page <= min(tot, 3):                     # cap 600 messages, as the 9/07 run did
            r = call(tok, keys, "GetMyMessages", win + "<DetailLevel>ReturnHeaders</DetailLevel><Pagination>"
                     "<EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>" % page)
            for m in r.findall(".//" + q("Message")):
                rec["messages"].append({"read": T(m, "Read"), "subject": T(m, "Subject"),
                                        "category": classify_message(T(m, "Subject"))})
            tot = int(T(r.find(".//" + q("PaginationResult")), "TotalNumberOfPages", "1") or 1)
            page += 1
        rec["messages_truncated"] = tot > 3
    except Exception as e:
        rec["err"].append("msg:" + str(e)[:200])
    try:
        r = call(tok, keys, "GetFeedback", "<DetailLevel>ReturnAll</DetailLevel><Pagination><EntriesPerPage>200</EntriesPerPage>"
                 "<PageNumber>1</PageNumber></Pagination>")
        rec["feedback"] = {"score": T(r, "FeedbackScore")}
        allc = []
        for f in r.findall(".//" + q("FeedbackDetail")):
            ct, tm = T(f, "CommentType"), T(f, "CommentTime")
            allc.append((ct, tm))
            if ct in ("Negative", "Neutral"):
                rec["neg_neutral"].append({"type": ct, "text": T(f, "CommentText"), "date": tm, "item": T(f, "ItemID"),
                                           "feedback_id": T(f, "FeedbackID"), "response": T(f, "Response")})
        for days, k in ((30, "pos_pct_1mo"), (182, "pos_pct_6mo"), (365, "pos_pct_12mo")):
            w = [ct for ct, tm in allc if tm and pdate(tm) and pdate(tm) >= NOW - dt.timedelta(days=days)]
            rec["feedback"][k] = round(100.0 * sum(1 for t in w if t == "Positive") / len(w), 1) if w else None
    except Exception as e:
        rec["err"].append("fb:" + str(e)[:200])
    return rec


def offers(tok, keys):
    out = {"offers": [], "err": []}
    try:
        r = call(tok, keys, "GetBestOffers", "<BestOfferStatus>Active</BestOfferStatus><DetailLevel>ReturnAll</DetailLevel>")
        for arr in r.findall(".//" + q("BestOfferArray")):
            for bo in arr.findall(q("BestOffer")):
                exp = T(bo, "ExpirationTime")
                et = pdate(exp) if exp else None
                out["offers"].append({"id": T(bo, "BestOfferID"), "status": T(bo, "Status"), "expire": exp,
                                      "item": T(bo, "ItemID"),
                                      "expiring_soon": bool(et and (et - NOW) < dt.timedelta(hours=48))})
    except Exception as e:
        out["err"].append(str(e)[:200])
    return out


def get_item(tok, keys, iid):
    r = call(tok, keys, "GetItem", "<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel><IncludeItemSpecifics>true</IncludeItemSpecifics>" % iid)
    it = r.find(q("Item"))
    if it is None:
        return None
    pd, bo, rp = it.find(q("PictureDetails")), it.find(q("BestOfferDetails")), it.find(q("ReturnPolicy"))
    title = T(it, "Title", "") or ""
    cat = T(it.find(q("PrimaryCategory")), "CategoryName", "") or ""
    return {"id": iid, "pics": len(pd.findall(q("PictureURL"))) if pd is not None else 0,
            "best_offer": (T(bo, "BestOfferEnabled") or "false").lower() == "true",
            "dispatch_max": T(it, "DispatchTimeMax"), "returns_accepted": T(rp, "ReturnsAcceptedOption"),
            "returns_within": T(rp, "ReturnsWithinOption"), "shipping_cost_paid_by": T(rp, "ShippingCostPaidByOption"),
            "specifics_count": len(it.findall(".//" + q("NameValueList"))), "title_len": len(title),
            "is_game": bool(GAME_RE.search(title + " " + cat)), "title": title}


def pull(out_dir):
    try:
        toks, keys = load_tokens()
    except Exception as e:
        ledger("The weekly eBay channel audit could not load the eBay store logins on the Mac, so nothing was posted.")
        log("token load failed:", type(e).__name__)
        sys.exit(3)
    raw, errs, sample = {}, {}, {}
    rnd = random.Random(DATE)
    for name in STORES:
        tok = toks.get(name)
        rec = {}
        if not tok:
            errs[name] = ["no token"]
            raw[name] = {"active": [], "sold90": [], "fees90": []}
            continue
        log("==", name)
        for key, fn in (("active", lambda: active_listings(tok, keys)), ("sold90", lambda: sold(tok, keys)),
                        ("fees90", lambda: fees(tok, keys))):
            try:
                rec[key] = fn()
            except Exception as e:
                rec[key] = []
                errs.setdefault(name, []).append("%s: %s" % (key, str(e)[:150]))
            log("  ", key, len(rec[key]))
        try:
            st = call(tok, keys, "GetStore", "").find(q("Store"))
            rec["store_info"] = {"subscription": T(st, "SubscriptionLevel") or T(st, "Subscription") if st is not None else None}
        except Exception as e:
            rec["store_info"] = {"error": str(e)[:150]}
        rec["msgfb"] = messages_feedback(tok, keys)
        rec["offers"] = offers(tok, keys)
        raw[name] = rec
        ids = [a["id"] for a in rec["active"] if a.get("id")]
        # 2026-10-21: was "<= 40 else sample(ids, 60)" — a store with 41-59 listings (Waynesboro 41 on 10/19)
        # crashed the whole run with ValueError. Take every listing up to 60, else a random 60.
        pick = ids if len(ids) <= 60 else rnd.sample(ids, 60)
        got, bad = [], 0
        for iid in pick:
            try:
                g = get_item(tok, keys, iid)
                if g:
                    got.append(g)
            except Exception:
                bad += 1
        sample[name] = {"sample_size": len(got), "population_size": len(ids), "errors": bad, "items": got}
        log("   sample", len(got), "of", len(ids))
    try:
        raw["_markdown_state"] = json.load(open(MD_STATE))
    except Exception as e:
        raw["_markdown_state"] = {"error": str(e)[:150]}
    raw["_store_errors"] = errs
    raw["_pull_time_utc"] = NOW.isoformat()
    os.makedirs(out_dir, exist_ok=True)
    json.dump(raw, open(os.path.join(out_dir, "raw_pull.json"), "w"), indent=1)
    json.dump(sample, open(os.path.join(out_dir, "sample_results.json"), "w"), indent=1)
    return raw, sample


# ---------------------------------------------------------------- analysis (the 9/07 analyze + analyze2)
def recat(type_str):
    t = (type_str or "").lower()
    if t == "customcode":
        return "final_value_fee"
    if t == "feead":
        return "promoted_listings"
    if t == "feeinsertion":
        return "insertion"
    if t == "feereturnshipping":
        return "return_shipping"
    if "final value" in t or "fvf" in t or "finalvalue" in t:
        return "final_value_fee"
    if "promoted" in t or "ad fee" in t:
        return "promoted_listings"
    if "insertion" in t:
        return "insertion"
    if "international" in t:
        return "international"
    if "return" in t:
        return "return_shipping"
    if "subscription" in t or "store" in t:
        return "subscription"
    return "other"


def median(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 1) if xs else None


def analyse(raw, sample):
    md = raw.get("_markdown_state") or {}
    if not isinstance(md, dict) or "error" in md:
        md = {}
    S, ch = {}, {"fees90_by_category": {}, "fee_types_other": {}}
    for name in STORES:
        rec = raw.get(name, {})
        act, sl, fe = rec.get("active", []), rec.get("sold90", []), rec.get("fees90", [])
        mf, of = rec.get("msgfb", {}) or {}, rec.get("offers", {}) or {}
        lv = sum((a.get("price") or 0) * (a.get("qty") or 1) for a in act)
        aged = [a for a in act if (a.get("days_live") or 0) > 90]
        units = sum(s.get("qty") or 1 for s in sl)
        rev = sum((s.get("price") or 0) * (s.get("qty") or 1) for s in sl)
        cats, ftot = {}, 0.0
        for f in fe:
            c = recat(f.get("type"))
            cats[c] = round(cats.get(c, 0) + (f.get("amt") or 0), 2)
            ftot += f.get("amt") or 0
            ch["fees90_by_category"][c] = round(ch["fees90_by_category"].get(c, 0) + (f.get("amt") or 0), 2)
            if c == "other":
                ch["fee_types_other"][f.get("type") or "?"] = round(ch["fee_types_other"].get(f.get("type") or "?", 0) + (f.get("amt") or 0), 2)
        msgs = mf.get("messages", [])
        unread = [m for m in msgs if (m.get("read") or "").lower() == "false"]
        nn = mf.get("neg_neutral", [])
        bo = of.get("offers", [])
        capped = [{"item_id": iid, "baseline": st.get("baseline"), "last_cut": st.get("last")}
                  for iid, st in md.items() if isinstance(st, dict) and st.get("store") == name
                  and (st.get("cuts") or 0) >= 3 and any(a.get("id") == iid for a in act)]
        items = (sample.get(name) or {}).get("items", [])
        n = len(items)
        trs = sum(1 for i in items if i.get("dispatch_max") in ("0", "1") and i.get("returns_within") in ("Days_30", "Days_60")
                  and i.get("shipping_cost_paid_by") == "Seller" and i.get("returns_accepted") == "ReturnsAccepted")
        no_ret = sum(1 for i in items if i.get("returns_accepted") and i.get("returns_accepted") != "ReturnsAccepted")
        S[name] = {
            "active_count": len(act), "listed_value": round(lv, 2),
            "aged_90plus_count": len(aged), "aged_90plus_value": round(sum((a.get("price") or 0) * (a.get("qty") or 1) for a in aged), 2),
            "sold90_units": units, "sold90_revenue": round(rev, 2),
            "days_to_sell_median": median([s.get("days_to_sell") for s in sl]),
            "fees90_by_category": cats, "fees90_total": round(ftot, 2),
            "fee_pct_of_revenue": round(100.0 * ftot / rev, 1) if rev else None,
            "promoted_spend_90d": cats.get("promoted_listings", 0.0),
            "messages_unread_60d": len(unread),
            "unread_return_refund": sum(1 for m in unread if m.get("category") == "return_refund"),
            "unread_case_dispute": sum(1 for m in unread if m.get("category") == "case_dispute"),
            "feedback": mf.get("feedback", {}),
            "neg_neutral": nn, "neg_neutral_no_response_count": sum(1 for x in nn if not x.get("response")),
            "open_best_offers": len(bo), "best_offers_expiring_48h": sum(1 for o in bo if o.get("expiring_soon")),
            "markdown_capped_count": len(capped), "markdown_capped_items": capped,
            "subscription": (rec.get("store_info") or {}).get("subscription"),
            "sample_size": n,
            "sample_best_offer_enabled_pct": round(100.0 * sum(1 for i in items if i.get("best_offer")) / n, 1) if n else None,
            "sample_no_returns_pct": round(100.0 * no_ret / n, 1) if n else None,
            "sample_no_returns": no_ret,
            "sample_days14_returns": sum(1 for i in items if i.get("returns_within") == "Days_14"),
            "sample_trs_eligible_pct": round(100.0 * trs / n, 1) if n else None,
            "sample_dispatch_breakdown": _count(items, "dispatch_max"),
            "sample_shipping_paid_by_breakdown": _count(items, "shipping_cost_paid_by"),
            "sample_avg_photos": round(sum(i.get("pics") or 0 for i in items) / n, 1) if n else None,
            "sample_games_with_offers": [i["id"] for i in items if i.get("is_game") and i.get("best_offer")],
        }
    keys_sum = ["active_count", "listed_value", "aged_90plus_count", "aged_90plus_value", "sold90_units", "sold90_revenue",
                "fees90_total", "messages_unread_60d", "unread_return_refund", "unread_case_dispute",
                "neg_neutral_no_response_count", "open_best_offers", "best_offers_expiring_48h", "markdown_capped_count", "sample_size"]
    for k in keys_sum:
        ch[k] = round(sum(S[n][k] for n in STORES), 2)
    ch["fee_pct_of_revenue"] = round(100.0 * ch["fees90_total"] / ch["sold90_revenue"], 1) if ch["sold90_revenue"] else None
    allitems = [i for n in STORES for i in (sample.get(n) or {}).get("items", [])]
    m = len(allitems)
    ch["sample_no_returns_pct"] = round(100.0 * sum(1 for i in allitems if i.get("returns_accepted") and i.get("returns_accepted") != "ReturnsAccepted") / m, 1) if m else None
    ch["sample_trs_eligible_pct"] = round(100.0 * sum(1 for i in allitems if i.get("dispatch_max") in ("0", "1") and i.get("returns_within") in ("Days_30", "Days_60")
                                                      and i.get("shipping_cost_paid_by") == "Seller" and i.get("returns_accepted") == "ReturnsAccepted") / m, 1) if m else None
    ch["sample_best_offer_enabled_pct"] = round(100.0 * sum(1 for i in allitems if i.get("best_offer")) / m, 1) if m else None
    return {"stores": S, "channel": ch, "pull_time_utc": raw.get("_pull_time_utc"), "store_errors": raw.get("_store_errors", {}),
            "live_pull": True, "method": "native bin/ebay_channel_audit.py (9/07 method)"}


def _count(items, k):
    out = {}
    for i in items:
        v = i.get(k) or "unknown"
        out[v] = out.get(v, 0) + 1
    return out


def prior_summary(exclude):
    """Newest earlier folder whose summary came from a LIVE pull (has raw_pull.json) — 10/05 was carried forward."""
    if not os.path.isdir(BASE):
        return None, None
    for d in sorted(os.listdir(BASE), reverse=True):
        p = os.path.join(BASE, d)
        if d >= exclude or not os.path.isfile(os.path.join(p, "raw_pull.json")) or not os.path.isfile(os.path.join(p, "summary.json")):
            continue
        try:
            return d, json.load(open(os.path.join(p, "summary.json")))
        except Exception:
            continue
    return None, None


# ---------------------------------------------------------------- rendering
def money(v):
    return "${:,.0f}".format(v or 0)


def sdelta(v, fmt="{:+,}"):
    return fmt.format(v)


def compose(sm, pdate_s, prev, out_rel):
    c, S = sm["channel"], sm["stores"]
    errs = sm.get("store_errors") or {}
    partial = sorted(errs)
    title = "eBay Channel Pulse — %s (weekly, trailing 90d, %s, read-only)" % (
        DATE, "all 5 stores" if not partial else "PARTIAL — %s incomplete" % ", ".join(partial))
    head = ("Headline: %d active listings / %s listed value · %d sold units / %s revenue (90d) · fees %s (%s%% of revenue) · "
            "%d listings aged >90d (%s) · %d unread messages (%d return/refund)"
            % (c["active_count"], money(c["listed_value"]), c["sold90_units"], money(c["sold90_revenue"]), money(c["fees90_total"]),
               c["fee_pct_of_revenue"], c["aged_90plus_count"], money(c["aged_90plus_value"]), c["messages_unread_60d"],
               c["unread_return_refund"]))
    lines = [title, "", head, ""]
    if partial:
        lines += ["Partial data: " + "; ".join("%s (%s)" % (n, ", ".join(e.split(":")[0] for e in errs[n])) for n in partial)
                  + " — those numbers are missing, not zero.", ""]
    hold = []
    if (c.get("sample_no_returns_pct") or 0) == 0:
        hold.append("no-returns 0%")
    if hold:
        lines += ["Holding steady: %s (GetItem-sample verified, %d listings)." % (", ".join(hold), c["sample_size"]), ""]
    dark = [n for n in STORES if (S[n]["promoted_spend_90d"] or 0) < 25 and n not in partial]
    still = "TRS Plus eligibility %s%% channel-wide (dispatch time + free returns)." % (
        "still 0" if (c.get("sample_trs_eligible_pct") or 0) == 0 else c.get("sample_trs_eligible_pct"))
    if dark:
        still += " Promoted Listings ~$0 at %d of 5 stores (%s)." % (len(dark), ", ".join(dark))
    lines += ["Still open (ops-policy calls, not automated): " + still, "", "New this week:"]
    new = []
    if prev:
        pc = prev["channel"]
        new.append("vs %s: active %s, listed value %s, 90d revenue %s, fee %% %+.1fpt, aged >90d %s / %s, unread %s"
                   % (pdate_s, sdelta(c["active_count"] - pc.get("active_count", 0)),
                      ("+" if c["listed_value"] >= pc.get("listed_value", 0) else "-") + money(abs(c["listed_value"] - pc.get("listed_value", 0))),
                      ("+" if c["sold90_revenue"] >= pc.get("sold90_revenue", 0) else "-") + money(abs(c["sold90_revenue"] - pc.get("sold90_revenue", 0))),
                      (c["fee_pct_of_revenue"] or 0) - (pc.get("fee_pct_of_revenue") or 0),
                      sdelta(c["aged_90plus_count"] - pc.get("aged_90plus_count", 0)),
                      ("+" if c["aged_90plus_value"] >= pc.get("aged_90plus_value", 0) else "-") + money(abs(c["aged_90plus_value"] - pc.get("aged_90plus_value", 0))),
                      sdelta(c["messages_unread_60d"] - pc.get("messages_unread_60d", 0))))
    exp = [(n, S[n]["best_offers_expiring_48h"]) for n in STORES if S[n]["best_offers_expiring_48h"]]
    if exp:
        n_exp = sum(x for _, x in exp)
        new.append("%d open Best Offer%s expiring within 48 h (%s) — none answered yet, needs a pricing call."
                   % (n_exp, "" if n_exp == 1 else "s", ", ".join("%s x%d" % e for e in exp)))
    cap = [(n, S[n]["markdown_capped_count"]) for n in STORES if S[n]["markdown_capped_count"]]
    if cap:
        new.append("%d listings sit at their 3rd markdown cut with no further scheduled action (%s)."
                   % (sum(x for _, x in cap), ", ".join("%s %d" % e for e in cap)))
    games = [(n, len(S[n]["sample_games_with_offers"])) for n in STORES if S[n]["sample_games_with_offers"]]
    if games:
        new.append("%d video-game / console / game-accessory listings in the sample take offers (%s) — the standing rule is no offers on video games; store's call to switch off, not changed here."
                   % (sum(x for _, x in games), ", ".join("%s %d" % g for g in games)))
    nr = [(n, S[n]["sample_no_returns"]) for n in STORES if S[n]["sample_no_returns"]]
    if nr:
        new.append("No-returns listings back in the sample: %s." % ", ".join("%s %d" % x for x in nr))
    d14 = [(n, S[n]["sample_days14_returns"]) for n in STORES if S[n]["sample_days14_returns"]]
    if d14:
        new.append("14-day-return listings in the sample: %s (template default, not fixed at the source)." % ", ".join("%s %d" % x for x in d14))
    since = pdate(prev.get("pull_time_utc") or "") if prev else None
    fresh_nn = [(n, x) for n in STORES for x in S[n]["neg_neutral"]
                if since and x.get("date") and pdate(x["date"]) and pdate(x["date"]) > since]
    if fresh_nn:
        new.append("%d new negative/neutral feedback since %s (%s)." % (
            len(fresh_nn), pdate_s, ", ".join(sorted({n for n, _ in fresh_nn}))))
    other = c["fees90_by_category"].get("other", 0)
    if c["fees90_total"] and other / c["fees90_total"] > 0.05:
        new.append("Fee types shifted again: %s of 90d fees didn't map to a known category (%s)." % (
            money(other), ", ".join(sorted(c["fee_types_other"]))[:120]))
    if c["unread_case_dispute"]:
        new.append("%d unread case/dispute-subject messages." % c["unread_case_dispute"])
    if not new:
        new.append("Nothing new flagged.")
    lines += ["• " + x for x in new]
    lines += ["", "Full writeup: Projects/eBay/audit_weekly/%s/summary.md" % out_rel]
    return "\n".join(lines), new, fresh_nn


def summary_md(sm, post, pdate_s):
    S, c = sm["stores"], sm["channel"]
    rows = ["| Store | Active | Listed value | Sold 90d (units/$) | Fees 90d | Fee % | Aged >90d ($) | Days-to-sell (median) |",
            "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for n in STORES:
        s = S[n]
        rows.append("| %s | %d | %s | %d / %s | %s | %s%% | %s (%d listings) | %s |" % (
            n, s["active_count"], money(s["listed_value"]), s["sold90_units"], money(s["sold90_revenue"]), money(s["fees90_total"]),
            s["fee_pct_of_revenue"], money(s["aged_90plus_value"]), s["aged_90plus_count"], s["days_to_sell_median"]))
    rows.append("| **Channel** | **%d** | **%s** | **%d / %s** | **%s** | **%s%%** | **%s (%d)** | — |" % (
        c["active_count"], money(c["listed_value"]), c["sold90_units"], money(c["sold90_revenue"]), money(c["fees90_total"]),
        c["fee_pct_of_revenue"], money(c["aged_90plus_value"]), c["aged_90plus_count"]))
    q_rows = ["| Store | Sample | Best Offer on | No-returns | TRS-eligible | Avg photos | Dispatch | Return shipping paid by |",
              "|---|---:|---:|---:|---:|---:|---|---|"]
    for n in STORES:
        s = S[n]
        q_rows.append("| %s | %d | %s%% | %s%% | %s%% | %s | %s | %s |" % (
            n, s["sample_size"], s["sample_best_offer_enabled_pct"], s["sample_no_returns_pct"], s["sample_trs_eligible_pct"],
            s["sample_avg_photos"], s["sample_dispatch_breakdown"], s["sample_shipping_paid_by_breakdown"]))
    fb = ["- %s: score %s, positive 1/6/12 mo %s/%s/%s%%, neg/neutral without a reply field %d, open Best Offers %d (%d expiring 48 h), unread %d (%d return/refund, %d case)" % (
        n, S[n]["feedback"].get("score"), S[n]["feedback"].get("pos_pct_1mo"), S[n]["feedback"].get("pos_pct_6mo"),
        S[n]["feedback"].get("pos_pct_12mo"), S[n]["neg_neutral_no_response_count"], S[n]["open_best_offers"],
        S[n]["best_offers_expiring_48h"], S[n]["messages_unread_60d"], S[n]["unread_return_refund"], S[n]["unread_case_dispute"]) for n in STORES]
    return "\n".join([
        "# eBay Channel Pulse — %s" % DATE, "",
        "**Window:** trailing 90 days · **Method:** live eBay Trading API, all 5 store accounts, read-only "
        "(GetMyeBaySelling, GetSellerTransactions, GetAccount, GetStore, GetItem, GetMyMessages, GetFeedback, GetBestOffers), "
        "native Mac run (`Valley Pawn OS/bin/ebay_channel_audit.py`). Nothing on eBay was changed. Listing-quality fields come "
        "from a GetItem sample (%d listings), not the bulk pull. Week-over-week base: %s." % (c["sample_size"], pdate_s or "none (first native run)"),
        "", "## Slack post (as sent)", "", "```", post, "```", "",
        "## Per-store table", ""] + rows + ["", "## Listing quality (GetItem sample)", ""] + q_rows + [
        "", "## Reputation, offers, messages", ""] + fb + [
        "", "## Fees by category (90d, channel)", "", "```", json.dumps(c["fees90_by_category"], indent=1), "```", "",
        "## Method notes", "",
        "- Feedback 'no seller response' is a known GetFeedback gap (replies sent via RespondToFeedback don't always show); "
        "the reliable record is ~/ebay_feedback_answered.json. Read the count as a ceiling, not a trend.",
        "- Not measured (API scope gap): impressions, click-through, conversion, seller level / Top Rated (see the monthly ratings sweep).",
        "- The claude.ai 'eBay Channel Pulse' artifact is NOT refreshed by this native run (a Mac script cannot publish it).",
        "- Store errors: %s" % (json.dumps(sm.get("store_errors")) if sm.get("store_errors") else "none"), ""])


def main():
    out_dir = RENDER_DIR if RENDER else os.path.join(BASE, DATE)
    if arg("--from"):                                   # re-analyse a past pull; output still goes to out_dir
        os.makedirs(out_dir, exist_ok=True)
        raw = json.load(open(os.path.join(arg("--from"), "raw_pull.json")))
        sample = json.load(open(os.path.join(arg("--from"), "sample_results.json")))
    else:
        raw, sample = pull(out_dir)
    errs = raw.get("_store_errors") or {}
    if len([n for n in STORES if errs.get(n)]) == len(STORES):
        ledger("The weekly eBay channel audit could not pull any store from eBay, so nothing was posted.")
        return 2
    sm = analyse(raw, sample)
    c = sm["channel"]
    if c["fees90_total"] and c["fees90_by_category"].get("other", 0) / c["fees90_total"] > 0.25:
        ledger("The weekly eBay channel audit withheld its post: most fees came back under fee types it doesn't recognise.")
        json.dump(sm, open(os.path.join(out_dir, "summary.json"), "w"), indent=1)
        return 2
    pd_s, prev = prior_summary(DATE)
    sm["compared_to"] = pd_s
    post, flags, fresh_nn = compose(sm, pd_s, prev, DATE)
    json.dump(sm, open(os.path.join(out_dir, "summary.json"), "w"), indent=1)
    open(os.path.join(out_dir, "summary.md"), "w").write(summary_md(sm, post, pd_s))
    if RENDER:
        print(post)
        log("[render] files in %s; nothing posted, no CHANGELOG, no register" % out_dir)
        return 0
    env = dict(os.environ, VP_TASK=AGENT)
    marker = "eBay Channel Pulse — %s" % DATE
    h = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "has", CH, marker, "20"],
                       capture_output=True, text=True, env=env)
    if h.returncode == 0:
        log("already posted today — not posting again")
        return 0
    p = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "post", CH, post],
                       capture_output=True, text=True, env=env)
    if p.returncode != 0:
        ledger("The weekly eBay channel audit ran but its #ebay-performance post did not go through.")
        log("FAIL post:", (p.stderr or p.stdout).strip()[:200])
        return 1
    log("posted", p.stdout.strip())
    # CHANGELOG (top, newest-first) — what compile-monthly-minutes reads
    try:
        entry = ("## %s (ebay-weekly-channel-audit, native)\n\n- %s active / %s listed · 90d %d units / %s · fees %s%% · aged >90d %d (%s). %s Full: `eBay/audit_weekly/%s/summary.md`.\n\n"
                 % (DATE, c["active_count"], money(c["listed_value"]), c["sold90_units"], money(c["sold90_revenue"]),
                    c["fee_pct_of_revenue"], c["aged_90plus_count"], money(c["aged_90plus_value"]),
                    " ".join(flags[:3])[:600], DATE))
        txt = open(CHANGELOG).read()
        open(CHANGELOG, "w").write(entry + txt)
    except OSError as e:
        log("changelog write failed:", e)
    # Open Items Register — actionable, clearly Claude-executable items (never fixed here)
    acts = [f for f in flags if any(k in f for k in ("Best Offers expiring", "video-game", "No-returns", "new negative"))]
    if acts:
        try:
            with open(REGISTER, "a") as f:
                f.write("| %s | 1 — Valley Pawn (eBay) | Weekly eBay channel audit flags: %s | OPEN | Read-only audit — a remediation session or the store decides; details in eBay/audit_weekly/%s/summary.md |\n"
                        % (DATE, " ".join(acts)[:700], DATE))
        except OSError as e:
            log("register write failed:", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
