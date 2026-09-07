#!/usr/bin/env python3
"""Bravo <-> eBay link: put the Bravo intake code into each listing's SKU (Custom label).

Source of the code, in order: (1) the code still in the live title "(VAP031234)",
(2) engine/data/recoverable_codes.json (original titles preserved by the title-stripper and
    other state files before the code was removed).
Only listings whose SKU is EMPTY are touched. SKU is invisible to buyers. Every write goes to
engine/ledger.jsonl with before/after so it can be reverted (--revert <run_id>).

Usage: sku_link.py [Store|all] [--apply] [--revert RUN_ID]
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ebay_common import *  # noqa

REC = os.path.join(DATA_DIR, "recoverable_codes.json")
recoverable = json.load(open(REC)) if os.path.exists(REC) else {}


def plan_for(store):
    tok = token_for(store)
    items = active_items(tok)
    plan, skipped_has_sku, no_code = [], 0, 0
    for it in items:
        if it["SKU"].strip():
            skipped_has_sku += 1
            continue
        m = CODE_RE.search(it["Title"])
        code = m.group(1) if m else (recoverable.get(it["ItemID"], [None])[0])
        if not code or code.upper().startswith("SN") or code[-1].isalpha():
            # "(SN48849347C)" is a serial number in the title, not a Bravo item number
            no_code += 1
            continue
        plan.append((it["ItemID"], code, "title" if m else "state"))
    return tok, len(items), plan, skipped_has_sku, no_code


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    if "--revert" in sys.argv:
        run_id = sys.argv[sys.argv.index("--revert") + 1]
        rows = [json.loads(l) for l in open(LEDGER) if l.strip()]
        rows = [r for r in rows if r.get("run_id") == run_id and r.get("action") == "sku_set" and r.get("ok")]
        print("revert %d SKU sets from run %s%s" % (len(rows), run_id, "" if apply else " (dry)"))
        if apply:
            with Lock():
                for r in rows:
                    ok, err = revise(token_for(r["store"]), r["ItemID"], "<SKU></SKU>")
                    ledger_append({"run_id": run_id + "-revert", "store": r["store"], "ItemID": r["ItemID"],
                                   "action": "sku_clear", "before": r["after"], "after": "", "ok": ok, "err": err[:1]})
        return
    stores = STORE_ORDER if (not args or args[0].lower() == "all") else [args[0]]
    run_id = time.strftime("%Y%m%d-%H%M%S") + "-skulink"
    total_ok = total_fail = 0
    summary = []
    ctx = Lock() if apply else None
    if ctx: ctx.__enter__()
    try:
        for store in stores:
            tok, n, plan, has_sku, no_code = plan_for(store)
            print("%-12s active %3d | already SKU %3d | linkable %3d (title %d, state %d) | no code %3d"
                  % (store, n, has_sku, len(plan), sum(1 for p in plan if p[2] == "title"),
                     sum(1 for p in plan if p[2] == "state"), no_code))
            for iid, code, src in plan[:3]:
                print("    %s <- %s (%s)" % (iid, code, src))
            ok = fail = 0
            if apply:
                for iid, code, src in plan:
                    good, err = revise(tok, iid, "<SKU>%s</SKU>" % escape(code))
                    ledger_append({"run_id": run_id, "store": store, "ItemID": iid, "action": "sku_set",
                                   "before": "", "after": code, "source": src, "ok": good,
                                   "err": [e[1] for e in err][:1] if not good else []})
                    if good: ok += 1
                    else:
                        fail += 1
                        print("    FAIL %s: %s" % (iid, err[:1]))
                    time.sleep(0.2)
                print("%-12s APPLIED %d, failed %d" % (store, ok, fail))
            summary.append((store, n, len(plan), ok, fail))
            total_ok += ok; total_fail += fail
    finally:
        if ctx: ctx.__exit__(None, None, None)
    print("SUMMARY run_id=%s applied=%d failed=%d %s" % (run_id, total_ok, total_fail, "" if apply else "(dry run — add --apply)"))
    os.makedirs(DATA_DIR, exist_ok=True)
    json.dump({"run_id": run_id, "apply": apply, "stores": summary},
              open(os.path.join(DATA_DIR, "sku_link_last_run.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
