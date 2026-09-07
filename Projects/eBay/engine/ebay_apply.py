#!/usr/bin/env python3
"""Valley Pawn eBay engine — Layer 3: APPLY (the only module that writes to eBay).

Executes ONLY the AUTO rows in data/latest/queue.json, one engine-wide lock, every change
appended to ledger.jsonl with before/after so any run can be reverted.

Whitelisted actions — nothing else can ever be applied by this module:
  returns_fix    -> ReturnsAccepted / Days_30 / buyer pays return shipping
  bestoffer_on   -> Best Offer on, auto-accept 90% of list, auto-decline below 75%
  sku_set        -> Bravo item number into the SKU (custom label) field; buyers never see it

Deliberately NOT here (judgment, or burned us before): titles, item specifics, categories,
photos, price cuts (the markdown engine owns those), ending listings (the terminal task owns
that), feedback replies.

Usage: ebay_apply.py [--apply] [--kind returns_fix,bestoffer_on,sku_set] [--store NAME]
       ebay_apply.py --revert RUN_ID [--apply]
Dry run by default: prints exactly what it would do and changes nothing.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ebay_common import *  # noqa

ALLOWED = ("returns_fix", "bestoffer_on", "sku_set")
BO_ACCEPT, BO_DECLINE = 0.90, 0.75


def queue_rows():
    p = os.path.join(DATA_DIR, "latest", "queue.json")
    if not os.path.exists(p):
        raise SystemExit("no queue.json — run ebay_snapshot.py then ebay_rules.py")
    q = json.load(open(p))
    if q.get("skipped_stores"):
        print("NOTE: %s skipped by the rules layer (incomplete snapshot) — not touched here."
              % ", ".join(q["skipped_stores"]))
    return [r for r in q["queue"] if r["mode"] == "AUTO" and r["kind"] in ALLOWED]


def snap_index(store):
    p = os.path.join(DATA_DIR, "latest", store + ".json")
    return {i["ItemID"]: i for i in json.load(open(p))["active"]}


def build(row, item):
    """Return (inner_xml, before, after) for one AUTO row."""
    k = row["kind"]
    if k == "returns_fix":
        before = "%s/%s/%s" % (item.get("returns_accepted"), item.get("returns_within"),
                               item.get("return_shipping_paid_by"))
        xml = ("<ReturnPolicy><ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>"
               "<ReturnsWithinOption>Days_30</ReturnsWithinOption>"
               "<ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption></ReturnPolicy>")
        return xml, before, "ReturnsAccepted/Days_30/Buyer"
    if k == "bestoffer_on":
        price = float(item.get("list_price") or item.get("price") or 0)
        if price <= 0:
            return None, None, None
        acc, dec = round(price * BO_ACCEPT, 2), round(price * BO_DECLINE, 2)
        if not (dec < acc < price):
            return None, None, None
        xml = ("<BestOfferDetails><BestOfferEnabled>true</BestOfferEnabled></BestOfferDetails>"
               "<ListingDetails><BestOfferAutoAcceptPrice>%.2f</BestOfferAutoAcceptPrice>"
               "<MinimumBestOfferPrice>%.2f</MinimumBestOfferPrice></ListingDetails>" % (acc, dec))
        return xml, "off", "on, accept>=%.2f decline<%.2f" % (acc, dec)
    if k == "sku_set":
        code = row.get("code")
        if not code or item.get("SKU"):
            return None, None, None
        return "<SKU>%s</SKU>" % escape(code), "", code
    return None, None, None


def revert(run_id, apply):
    rows = [json.loads(l) for l in open(LEDGER) if l.strip()]
    rows = [r for r in rows if r.get("run_id") == run_id and r.get("ok")]
    print("revert %d change(s) from %s%s" % (len(rows), run_id, "" if apply else "  (dry run)"))
    if not apply:
        for r in rows[:10]:
            print("  %s %s %s -> %s" % (r["store"], r["ItemID"], r["after"], r["before"]))
        return
    with Lock():
        for r in rows:
            if r["kind"] == "sku_set":
                xml = "<SKU></SKU>"
            elif r["kind"] == "returns_fix":
                a, w, s = (r["before"].split("/") + ["", "", ""])[:3]
                xml = ("<ReturnPolicy><ReturnsAcceptedOption>%s</ReturnsAcceptedOption>"
                       "<ReturnsWithinOption>%s</ReturnsWithinOption>"
                       "<ShippingCostPaidByOption>%s</ShippingCostPaidByOption></ReturnPolicy>"
                       % (a or "ReturnsNotAccepted", w or "Days_30", s or "Buyer"))
            elif r["kind"] == "bestoffer_on":
                xml = "<BestOfferDetails><BestOfferEnabled>false</BestOfferEnabled></BestOfferDetails>"
            else:
                continue
            ok, err = revise(token_for(r["store"]), r["ItemID"], xml)
            ledger_append({"run_id": run_id + "-revert", "store": r["store"], "ItemID": r["ItemID"],
                           "kind": r["kind"], "before": r["after"], "after": r["before"], "ok": ok,
                           "err": [e[1] for e in err][:1] if not ok else []})
            time.sleep(0.2)


def main():
    if "--revert" in sys.argv:
        return revert(sys.argv[sys.argv.index("--revert") + 1], "--apply" in sys.argv)
    apply = "--apply" in sys.argv
    kinds = sys.argv[sys.argv.index("--kind") + 1].split(",") if "--kind" in sys.argv else list(ALLOWED)
    only = sys.argv[sys.argv.index("--store") + 1] if "--store" in sys.argv else None
    rows = [r for r in queue_rows() if r["kind"] in kinds and (only is None or r["store"] == only)]
    if not rows:
        print("nothing to apply"); return
    run_id = time.strftime("%Y%m%d-%H%M%S") + "-apply"
    idx, ok, fail, skip = {}, 0, 0, 0
    ctx = Lock() if apply else None
    if ctx: ctx.__enter__()
    try:
        for r in rows:
            if r["store"] not in idx:
                idx[r["store"]] = snap_index(r["store"])
            item = idx[r["store"]].get(r["ItemID"])
            if not item:
                skip += 1; continue
            xml, before, after = build(r, item)
            if xml is None:
                skip += 1; continue
            if not apply:
                print("  %-12s %-13s %s  %s -> %s" % (r["store"], r["kind"], r["ItemID"], before, after))
                continue
            good, err = revise(token_for(r["store"]), r["ItemID"], xml)
            ledger_append({"run_id": run_id, "store": r["store"], "ItemID": r["ItemID"], "kind": r["kind"],
                           "before": before, "after": after, "ok": good,
                           "err": [e[1] for e in err][:1] if not good else []})
            if good:
                ok += 1
            else:
                fail += 1
                print("  FAIL %s %s: %s" % (r["store"], r["ItemID"], [e[1] for e in err][:1]))
            time.sleep(0.2)
    finally:
        if ctx: ctx.__exit__(None, None, None)
    if apply:
        print("run_id=%s applied=%d failed=%d skipped=%d" % (run_id, ok, fail, skip))
        print("revert with: ebay_apply.py --revert %s --apply" % run_id)
    else:
        print("%d change(s) planned, %d skipped. Dry run — add --apply." % (len(rows) - skip, skip))


if __name__ == "__main__":
    main()
