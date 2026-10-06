#!/usr/bin/env python3
"""online_store_audit.py [--render] — native replacement for Cowork `weekly-online-store-audit`
(Sunday 08:00 ET, built 2026-10-05). The SKILL's steps, nothing re-derived:

  1 pull every store's active listings (GetSellerList, Fine) + last-7-day sales (GetSellerTransactions)
    and auto-fix ONLY the returns policy: any active listing not on ReturnsAccepted / Days_30 /
    buyer-pays-return-shipping -> ReviseFixedPriceItem with a <ReturnPolicy> block.
    BEST OFFER IS NEVER WRITTEN (Joshua 2026-09-17). This file contains no BestOfferDetails write path.
    Video-game listings found with Best Offer ON are only reported, never switched.
  2 spot-check up to 3 fixed items fresh via GetItem; any spot-check failure is said in the post.
  3 post to #ebay-performance the same summary the old ~/vp_weekly_online_store_audit.py printed
    (same lines, same table) + the "Needs a human" callout the Cowork task added.
  Outputs (live only): eBay/weekly_audit/<DATE>/report.json + summary.md, latest.json (trend base),
  fix_history.log, reversible write state in ~/vp_ebay_fix_state.json (same key format as before).

  --render   read-only: pulls eBay, writes NOTHING (no eBay revise, no files, no Slack), prints the
             post exactly as it would go out; "auto-fixed" counts = listings that WOULD be fixed.
Failure (a store's pull fails, Slack refuses): one row in fleet/FAILURE_LEDGER.md, nothing posted —
never a partial estate.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

AGENT = "weekly-online-store-audit"
ETZ = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
BASE = os.path.expanduser("~/Documents/Claude/Projects/eBay/weekly_audit")
STATE_PATH = os.path.expanduser("~/vp_ebay_fix_state.json")
CH = "C0ANVN5KX4Y"   # #ebay-performance
NS = "urn:ebay:apis:eBLBaseComponents"
URL = "https://api.ebay.com/ws/api.dll"
ORDER = ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]   # order of every past post
RET30 = ("<ReturnPolicy><ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>"
         "<RefundOption>MoneyBack</RefundOption>"
         "<ReturnsWithinOption>Days_30</ReturnsWithinOption>"
         "<ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption></ReturnPolicy>")
GAME_RE = re.compile(r"video game|\b(ps[1-5]|playstation|xbox|nintendo|switch oled|game ?boy|game ?cube|wii|sega|atari|n64)\b", re.I)

RENDER = "--render" in sys.argv
NOW = dt.datetime.now(dt.timezone.utc)
DATE = dt.datetime.now(ETZ).strftime("%Y-%m-%d")


def ledger(sentence):
    try:
        with open(LEDGER, "a") as f:
            f.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                    % (dt.datetime.now(ETZ).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def load_tokens():
    sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
    from ebay_store_tokens import STORES as TOK, APP_ID, DEV_ID, CERT_ID  # never hardcode
    return {s["name"].lower(): s["token"] for s in TOK}, (APP_ID, DEV_ID, CERT_ID)


def call(tok, keys, name, inner, retries=3):
    body = ('<?xml version="1.0" encoding="utf-8"?><%sRequest xmlns="%s">'
            '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>%s</%sRequest>'
            % (name, NS, tok, inner, name)).encode()
    h = {"X-EBAY-API-SITEID": "0", "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
         "X-EBAY-API-CALL-NAME": name, "X-EBAY-API-APP-NAME": keys[0],
         "X-EBAY-API-DEV-NAME": keys[1], "X-EBAY-API-CERT-NAME": keys[2],
         "X-EBAY-API-IAF-TOKEN": tok, "Content-Type": "text/xml"}
    last = None
    for i in range(retries):
        try:
            return ET.fromstring(urlopen(Request(URL, data=body, headers=h), timeout=120).read().decode())
        except (URLError, HTTPError, ET.ParseError, OSError) as e:
            last = e
            time.sleep(3 * (i + 1))
    raise RuntimeError("%s failed after %d tries: %s" % (name, retries, last))


def q(n):
    return "{%s}%s" % (NS, n)


def t(el, tag, d=None):
    if el is None:
        return d
    x = el.find(q(tag))
    return x.text if x is not None and x.text is not None else d


def err(r):
    return (r.findtext(".//" + q("LongMessage")) or r.findtext(".//" + q("ShortMessage")) or t(r, "Ack", "") or "")[:200]


def age_days(start):
    try:
        st = dt.datetime.strptime(start[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
        return (NOW - st).days
    except Exception:
        return None


def iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def pull_store(tok, keys):
    items, page = {}, 1
    while True:
        inner = ("<EndTimeFrom>%s</EndTimeFrom><EndTimeTo>%s</EndTimeTo><GranularityLevel>Fine</GranularityLevel>"
                 "<IncludeItemSpecifics>true</IncludeItemSpecifics>"
                 "<Pagination><EntriesPerPage>100</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>"
                 % (iso(NOW), iso(NOW + dt.timedelta(days=120)), page))
        r = call(tok, keys, "GetSellerList", inner)
        if t(r, "Ack") == "Failure":
            raise RuntimeError("GetSellerList: " + err(r))
        for it in r.findall(".//" + q("Item")):
            iid = t(it, "ItemID")
            if not iid:
                continue
            pd, rp = it.find(q("PictureDetails")), it.find(q("ReturnPolicy"))
            ss, ld, bo = it.find(q("SellingStatus")), it.find(q("ListingDetails")), it.find(q("BestOfferDetails"))
            items[iid] = {
                "title": t(it, "Title", ""),
                "category": t(it.find(q("PrimaryCategory")), "CategoryName", "") or "",
                "price": t(ss, "CurrentPrice") or t(it, "StartPrice"),
                "pics": len(pd.findall(q("PictureURL"))) if pd is not None else 0,
                "specifics": len(it.findall(".//" + q("NameValueList"))),
                "best_offer": t(bo, "BestOfferEnabled") if bo is not None else t(it, "BestOfferEnabled"),
                "returns": t(rp, "ReturnsAcceptedOption"),
                "returns_within": t(rp, "ReturnsWithinOption"),
                "ret_ship_by": t(rp, "ShippingCostPaidByOption"),
                "start": t(ld, "StartTime"),
                "sku": t(it, "SKU"),
            }
        tot = int(t(r.find(".//" + q("PaginationResult")), "TotalNumberOfPages", "1") or 1)
        if page >= tot:
            break
        page += 1
    sold, page = [], 1
    while True:
        inner = ("<ModTimeFrom>%s</ModTimeFrom><ModTimeTo>%s</ModTimeTo><IncludeContainingOrder>true</IncludeContainingOrder>"
                 "<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>"
                 % (iso(NOW - dt.timedelta(days=7)), iso(NOW), page))
        r = call(tok, keys, "GetSellerTransactions", inner)
        if t(r, "Ack") == "Failure":
            raise RuntimeError("GetSellerTransactions: " + err(r))
        for tx in r.findall(".//" + q("Transaction")):
            amt = t(tx, "TransactionPrice")
            sold.append({"price": float(amt) if amt else 0, "qty": int(t(tx, "QuantityPurchased", "1") or 1)})
        tot = int(t(r.find(".//" + q("PaginationResult")), "TotalNumberOfPages", "1") or 1)
        if page >= tot:
            break
        page += 1
    return items, sold


def is_game(v):
    return "video game" in v["category"].lower() or bool(GAME_RE.search(v["title"]))


def money(v, dec=2):
    return ("${:,.%df}" % dec).format(v)


def main():
    try:
        toks, keys = load_tokens()
    except Exception as e:
        ledger("The weekly online-store audit could not load the eBay store logins (%s)." % type(e).__name__)
        print("FAIL load tokens:", e)
        return 1
    state = {}
    if os.path.exists(STATE_PATH):
        try:
            state = json.load(open(STATE_PATH))
        except Exception:
            state = {}
    stores, fix_log, fixed_ids, failures, games_bo = {}, [], [], [], []
    for name in ORDER:
        tok = toks.get(name.lower())
        if not tok:
            ledger("The weekly online-store audit had no eBay login for %s, so nothing was posted." % name)
            print("FAIL no token for", name)
            return 1
        try:
            items, sold = pull_store(tok, keys)
        except Exception as e:
            ledger("The weekly online-store audit could not pull %s's eBay listings, so nothing was posted." % name)
            print("FAIL pull %s: %s" % (name, e))
            return 1
        print("== %s: %d active, %d sold/7d, %d with category name" % (
            name, len(items), len(sold), sum(1 for v in items.values() if v["category"])), file=sys.stderr)
        fixed = fail = 0
        for iid, v in items.items():
            if v["best_offer"] == "true" and is_game(v):
                games_bo.append((name, iid, v["title"]))
            if v["returns"] == "ReturnsAccepted" and v["returns_within"] == "Days_30" and v["ret_ship_by"] == "Buyer":
                continue
            if RENDER:
                fixed += 1
                continue
            try:
                r = call(tok, keys, "ReviseFixedPriceItem", "<Item><ItemID>%s</ItemID>%s</Item>" % (iid, RET30))
                ok, msg = t(r, "Ack", "") in ("Success", "Warning"), err(r)
            except Exception as e:
                ok, msg = False, str(e)[:200]
            if ok:
                fixed += 1
                fixed_ids.append((name, iid))
                state["W|%s|%s|ret" % (name, iid)] = {
                    "before": {"returns": v["returns"], "returns_within": v["returns_within"], "ret_ship_by": v["ret_ship_by"]},
                    "label": "weekly auto-fix -> 30d returns", "date": DATE}
                fix_log.append("%s  RETURNS  %s  %s" % (DATE, name, iid))
            else:
                fail += 1
                failures.append((name, iid, msg))
        ages = [a for a in (age_days(v["start"]) for v in items.values()) if a is not None]
        pics = [v["pics"] for v in items.values()]
        spec = [v["specifics"] for v in items.values()]
        rev7 = sum(x["price"] * x["qty"] for x in sold)
        over180 = [v for v in items.values() if (age_days(v["start"]) or 0) > 180]
        stores[name] = {
            "active": len(items),
            "sold_7d": len(sold),
            "revenue_7d": round(rev7, 2),
            "rev_per_listing_7d": round(rev7 / len(items), 2) if items else 0,
            "median_pics": sorted(pics)[len(pics) // 2] if pics else 0,
            "under_8_pics_pct": round(100 * sum(1 for p in pics if p < 8) / len(pics), 1) if pics else 0,
            "median_specifics": sorted(spec)[len(spec) // 2] if spec else 0,
            "over_90d_count": sum(1 for a in ages if a > 90),
            "over_180d_count": len(over180),
            "over_180d_value": round(sum(float(v["price"] or 0) for v in over180), 2),
            "no_sku_pct": round(100 * sum(1 for v in items.values() if not v["sku"]) / len(items), 1) if items else 0,
            "fixed_returns_this_run": fixed,
            "fixed_best_offer_this_run": 0,
            "fix_failures_this_run": fail,
        }
        if not RENDER:
            json.dump(state, open(STATE_PATH, "w"), indent=1)
    if sum(v["active"] for v in stores.values()) == 0:
        ledger("The weekly online-store audit got zero active listings from eBay for every store, so nothing was posted.")
        print("FAIL zero listings estate-wide")
        return 1

    # Step 2 — spot-check up to 3 fixes fresh (live only)
    spot = []
    for name, iid in fixed_ids[:3]:
        try:
            r = call(toks[name.lower()], keys, "GetItem", "<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel>" % iid)
            rp = r.find(".//" + q("ReturnPolicy"))
            spot.append((name, iid, t(rp, "ReturnsAcceptedOption") == "ReturnsAccepted" and t(rp, "ReturnsWithinOption") == "Days_30"
                         and t(rp, "ShippingCostPaidByOption") == "Buyer"))
        except Exception:
            spot.append((name, iid, False))

    S = stores
    tot = {
        "active": sum(v["active"] for v in S.values()),
        "sold_7d": sum(v["sold_7d"] for v in S.values()),
        "revenue_7d": round(sum(v["revenue_7d"] for v in S.values()), 2),
        "over_180d_count": sum(v["over_180d_count"] for v in S.values()),
        "over_180d_value": round(sum(v["over_180d_value"] for v in S.values()), 2),
        "fixed_returns_this_run": sum(v["fixed_returns_this_run"] for v in S.values()),
        "fixed_best_offer_this_run": 0,
    }
    report = {"date": DATE, "stores": S, "totals": tot}
    prior = None
    latest_path = os.path.join(BASE, "latest.json")
    try:
        prior = json.load(open(latest_path))
    except Exception:
        prior = None
    if prior and prior.get("date") == DATE:   # re-run on the same day: compare with the one before
        prior = None
    label = "WoW"
    if prior:
        gap = (dt.date.fromisoformat(DATE) - dt.date.fromisoformat(prior["date"])).days
        if gap > 9:   # weeks were missed — say what we compare with, never call it week-over-week
            label = "vs %s" % dt.date.fromisoformat(prior["date"]).strftime("%b %-d")

    def delta(cur, prev):
        if not prev:
            return ""
        d = cur - prev
        return " (%s%.0f%% %s)" % ("+" if d >= 0 else "", 100 * d / prev, label)

    by_store = {}
    for n, _, _ in [(f[0], 0, 0) for f in fixed_ids]:
        by_store[n] = by_store.get(n, 0) + 1
    if RENDER:
        by_store = {n: v["fixed_returns_this_run"] for n, v in S.items() if v["fixed_returns_this_run"]}
    where = ""
    if len(by_store) == 1 and tot["fixed_returns_this_run"]:
        where = " (all %s)" % list(by_store)[0]
    elif len(by_store) > 1:
        where = " (" + ", ".join("%s %d" % (n, c) for n, c in by_store.items()) + ")"

    lines = ["# Weekly Online Store Audit — %s" % DATE, ""]
    lines.append("**Estate:** %d active listings, %d sold in 7 days, %s revenue%s" % (
        tot["active"], tot["sold_7d"], money(tot["revenue_7d"]),
        delta(tot["revenue_7d"], prior["totals"]["revenue_7d"]) if prior else ""))
    lines.append("**Auto-fixed this run:** %d listings -> 30-day returns%s, 0 listings -> Best Offer ON" % (
        tot["fixed_returns_this_run"], where))
    lines.append("**Aged inventory:** %d listings over 180 days, %s tied up%s" % (
        tot["over_180d_count"], money(tot["over_180d_value"]),
        delta(tot["over_180d_value"], prior["totals"]["over_180d_value"]) if prior else ""))
    lines.append("")
    lines.append("| Store | Active | Sold/7d | Rev/7d | Rev/listing | <8 photos | >180d | SKU missing |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for name in ORDER:
        v = S[name]
        lines.append("| %s | %d | %d | %s | %s | %.0f%% | %d | %.0f%% |" % (
            name, v["active"], v["sold_7d"], money(v["revenue_7d"], 0), money(v["rev_per_listing_7d"], 0),
            v["under_8_pics_pct"], v["over_180d_count"], v["no_sku_pct"]))
    summary = "\n".join(lines)

    # Needs-a-human callout (SKILL Step 3)
    notes = []
    if failures:
        per = {}
        for n, _, _ in failures:
            per[n] = per.get(n, 0) + 1
        pending = all("offer" in (m or "").lower() for _, _, m in failures)
        why = (" — eBay won't change the return policy while a buyer's offer is pending; self-resolving, will retry next week"
               if pending else " — eBay refused the change; will retry next week (item IDs in this week's report)")
        notes.append("%s could not be switched to 30-day returns%s." % (
            ", ".join("%s %d listing%s" % (n, c, "" if c == 1 else "s") for n, c in per.items()), why))
    if games_bo:
        per = {}
        for n, _, _ in games_bo:
            per[n] = per.get(n, 0) + 1
        notes.append("Best Offer is switched ON for %d video-game listing%s (%s) — video games never take offers, so the "
                     "store should switch these off; the item list is in this week's audit report." % (
                         len(games_bo), "" if len(games_bo) == 1 else "s",
                         ", ".join("%s %d" % (n, per[n]) for n in ORDER if n in per)))
    if prior:
        for name in ORDER:
            p = prior.get("stores", {}).get(name)
            v = S[name]
            if not p:
                continue
            aged_up = v["over_180d_count"] > p.get("over_180d_count", 0)
            rpl_drop = p.get("rev_per_listing_7d", 0) > 0 and v["rev_per_listing_7d"] < 0.8 * p["rev_per_listing_7d"]
            if aged_up and rpl_drop:
                notes.append("%s: listings over 180 days up %d -> %d and revenue per listing down %s -> %s %s." % (
                    name, p["over_180d_count"], v["over_180d_count"], money(p["rev_per_listing_7d"], 0),
                    money(v["rev_per_listing_7d"], 0), label))
    if not any(n.split(":")[0] in ORDER for n in notes):
        notes.append("No store crossed into a new risk zone this week.")
    if spot:
        good = sum(1 for s in spot if s[2])
        if good == len(spot):
            notes.append("Spot-checked %d of the %d auto-fixes live — all confirmed on 30-day buyer-pay returns." % (len(spot), len(fixed_ids)))
        else:
            bad = ", ".join("%s %s" % (s[0], s[1]) for s in spot if not s[2])
            notes.append("Spot-check: %d of %d auto-fixes did NOT show 30-day buyer-pay returns when re-read from eBay (%s)." % (
                len(spot) - good, len(spot), bad))
    post = summary + "\n\n**Needs a human:** " + " ".join(notes)

    if RENDER:
        for n, i, ttl in games_bo[:2]:
            try:
                r = call(toks[n.lower()], keys, "GetItem", "<ItemID>%s</ItemID>" % i)
                print("[render] GetItem %s %s BestOfferEnabled=%s cat=%s" % (n, i, r.findtext(".//" + q("BestOfferEnabled")),
                      r.findtext(".//" + q("PrimaryCategory") + "/" + q("CategoryName"))), file=sys.stderr)
            except Exception as e:
                print("[render] GetItem %s failed: %s" % (i, e), file=sys.stderr)
        print(post)
        print("\n[render] nothing written, nothing revised, nothing posted. Would-fix listings: %d. Video-game Best Offer ON: %d."
              % (tot["fixed_returns_this_run"], len(games_bo)), file=sys.stderr)
        return 0

    outdir = os.path.join(BASE, DATE)
    os.makedirs(outdir, exist_ok=True)
    report["fix_failures"] = [{"store": n, "item": i, "msg": m} for n, i, m in failures]
    report["video_game_best_offer_on"] = [{"store": n, "item": i, "title": ttl} for n, i, ttl in games_bo]
    report["spot_check"] = [{"store": n, "item": i, "ok": ok} for n, i, ok in spot]
    json.dump(report, open(os.path.join(outdir, "report.json"), "w"), indent=1)
    open(os.path.join(outdir, "summary.md"), "w").write(summary)
    json.dump(report, open(latest_path, "w"), indent=1)
    if fix_log:
        with open(os.path.join(BASE, "fix_history.log"), "a") as f:
            f.write("\n".join(fix_log) + "\n")

    env = dict(os.environ, VP_TASK=AGENT)
    marker = "Weekly Online Store Audit — %s" % DATE
    h = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "has", CH, marker, "20"],
                       capture_output=True, text=True, timeout=60, env=env)
    if h.returncode == 0:
        print("already posted today — not posting again")
        return 0
    p = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "post", CH, post],
                       capture_output=True, text=True, timeout=90, env=env)
    if p.returncode != 0:
        ledger("The weekly online-store audit ran but its #ebay-performance post did not go through.")
        print("FAIL post:", (p.stderr or p.stdout).strip()[:200])
        return 1
    print("posted", p.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
