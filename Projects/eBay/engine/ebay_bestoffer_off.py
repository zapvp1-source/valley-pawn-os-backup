#!/usr/bin/env python3
"""Valley Pawn eBay engine — switch Best Offer OFF where it should never have been on.

Built 2026-10-20 (full eBay audit). ADDITIVE: touches nothing else in the engine. Two jobs,
both Joshua-directed:

  --video-games   Rule 2 (Joshua 2026-09-17, verbatim: "We do not want make an offer on video
                  games at all"). Every active listing in the eBay Video Games tree (1249 +
                  children) or whose title carries a game/console hint that currently has
                  Best Offer ON is switched OFF. Flagged weekly since 9/17 (59-64 listings),
                  assigned "Owner: Marketing" in the 10/12 CEO brief, never executed.
  --august        Joshua said YES on 2026-09-17 to undoing the ~193 Culpeper listings our own
                  2026-08-23 remediation (ebay_policy_fix.py BESTOFFER) turned ON. The one-shot
                  that was to do it failed three times (HUMAN_QUEUE 9/17). Reads
                  ~/ebay_policy_fix_state.json and switches OFF exactly those listings whose
                  recorded prior value was OFF. Never exec()s ebay_policy_fix.py.

Safety: dry run by default (--apply to write). One engine-wide lock. GetItem re-read before
every write: skipped if not Active, if Best Offer is already OFF, or if a Best Offer is
pending (eBay refuses the revise — left for next week). Every write appended to
engine/ledger.jsonl as kind "bestoffer_off" with before/after. This script can only ever
write <BestOfferEnabled>false</BestOfferEnabled> — there is no code path that writes true.
Pacing 0.3 s. Spot-checks 3 random applied items live afterwards.

Usage: ebay_bestoffer_off.py --video-games [--august] [--store NAME] [--apply]
"""
import json, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ebay_common import *  # noqa
from ebay_rules import is_no_offer_item  # category tree 1249 + title hints (proven 9/17)

POLICY_STATE = os.path.expanduser("~/ebay_policy_fix_state.json")
OUT_DIR = os.path.expanduser("~/Documents/Claude/Projects/eBay")
XML_OFF = "<BestOfferDetails><BestOfferEnabled>false</BestOfferEnabled></BestOfferDetails>"


def q(tag):
    return "{%s}%s" % (NS, tag)


def live_state(tok, iid):
    """(status, best_offer_on, title, category_id, has_pending_offer) from a fresh GetItem."""
    r, err = get_item(tok, iid)
    if r is None:
        return None, None, "", "", False, err
    it = r.find(".//" + q("Item"))
    status = it.findtext(".//" + q("SellingStatus") + "/" + q("ListingStatus"), "")
    bo = (it.findtext(".//" + q("BestOfferDetails") + "/" + q("BestOfferEnabled"), "false") or "false").lower() == "true"
    pending = int(it.findtext(".//" + q("BestOfferDetails") + "/" + q("BestOfferCount"), "0") or 0) > 0
    title = it.findtext(q("Title"), "") or ""
    cat = it.findtext(".//" + q("PrimaryCategory") + "/" + q("CategoryID"), "") or ""
    return status, bo, title, cat, pending, None


def august_targets():
    """ItemIDs from ebay_policy_fix_state.json whose BESTOFFER prior value was OFF."""
    if not os.path.exists(POLICY_STATE):
        print("NOTE: %s not found — --august skipped" % POLICY_STATE)
        return {}
    st = json.load(open(POLICY_STATE))
    out = {}

    def walk(o, store_hint=None):
        if isinstance(o, dict):
            # common shapes: {"<store>": {"<itemid>": {...}}} or {"<itemid>": {"store":..,"fix":..}}
            for k, v in o.items():
                if isinstance(v, dict) and k.isdigit() and len(k) >= 9:
                    fix = str(v.get("fix") or v.get("kind") or v.get("type") or "")
                    prior = v.get("prior") or v.get("before") or v.get("prev") or {}
                    txt = json.dumps(v).lower()
                    if "bestoffer" in txt:
                        prior_off = ("false" in json.dumps(prior).lower()) or ('"before": "false"' in txt) or ('"prior": "false"' in txt)
                        store = v.get("store") or store_hint
                        if store:
                            out[k] = (store, prior_off, fix)
                else:
                    walk(v, store_hint=k if isinstance(v, dict) and not k.isdigit() else store_hint)
    walk(st)
    return out


def main():
    apply = "--apply" in sys.argv
    do_games = "--video-games" in sys.argv
    do_aug = "--august" in sys.argv
    only = sys.argv[sys.argv.index("--store") + 1] if "--store" in sys.argv else None
    if not (do_games or do_aug):
        raise SystemExit("say what to do: --video-games and/or --august")
    run_id = time.strftime("%Y%m%d-%H%M%S") + "-bestoffer-off"
    plan = {}   # (store, iid) -> reason
    stores = [s for s in STORE_ORDER if only is None or s == only]

    if do_aug:
        for iid, (store, prior_off, fix) in august_targets().items():
            if (only is None or store == only) and prior_off:
                plan[(store, iid)] = "august-remediation-revert"
        print("august revert candidates (prior value OFF): %d" % sum(1 for v in plan.values() if v.startswith("august")))

    if do_games:
        for store in stores:
            tok = token_for(store)
            items = active_items(tok)
            hits = [i for i in items if is_no_offer_item(i)]
            print("%-12s active %d  title/category game hits %d" % (store, len(items), len(hits)))
            for i in hits:
                plan.setdefault((store, i["ItemID"]), "video-game")

    # verify each candidate live, decide
    todo, skipped = [], {"not_active": 0, "already_off": 0, "pending_offer": 0, "not_game": 0, "err": 0}
    for (store, iid), reason in sorted(plan.items()):
        tok = token_for(store)
        status, bo, title, cat, pending, err = live_state(tok, iid)
        time.sleep(0.25)
        if err:
            skipped["err"] += 1; continue
        if status != "Active":
            skipped["not_active"] += 1; continue
        if not bo:
            skipped["already_off"] += 1; continue
        if reason == "video-game" and not is_no_offer_item({"Title": title, "category_id": cat}):
            skipped["not_game"] += 1; continue
        if pending:
            skipped["pending_offer"] += 1; continue
        todo.append((store, iid, reason, title, cat))
    print("\nplanned %d  skipped %s" % (len(todo), skipped))
    for store, iid, reason, title, cat in todo:
        print("  %-12s %s %-26s cat %-7s %s" % (store, iid, reason, cat, title[:60]))
    if not apply:
        print("\nDRY RUN — add --apply to switch Best Offer OFF on the %d listings above." % len(todo))
        return 0
    ok, fail, done = 0, 0, []
    with Lock():
        for store, iid, reason, title, cat in todo:
            good, err = revise(token_for(store), iid, XML_OFF)
            ledger_append({"run_id": run_id, "store": store, "ItemID": iid, "kind": "bestoffer_off",
                           "reason": reason, "before": "BestOffer=ON", "after": "BestOffer=OFF", "ok": good,
                           "title": title[:80], "err": [e[1] for e in err][:1] if not good else []})
            if good:
                ok += 1; done.append((store, iid))
            else:
                fail += 1; print("  FAIL %s %s: %s" % (store, iid, [e[2] for e in err][:1]))
            time.sleep(0.3)
    # spot-check
    checks = []
    for store, iid in random.sample(done, min(3, len(done))):
        st, bo, _, _, _, _ = live_state(token_for(store), iid)
        checks.append((store, iid, st, "OFF" if bo is False else "ON"))
    print("run_id=%s applied=%d failed=%d" % (run_id, ok, fail))
    print("spot-check:", checks)
    # plain-language summary file
    by = {}
    for s, i in done:
        by[s] = by.get(s, 0) + 1
    try:
        p = os.path.join(OUT_DIR, "bestoffer_off_%s.md" % time.strftime("%Y-%m-%d"))
        with open(p, "a") as f:
            f.write("# Best Offer switched OFF — %s (run %s)\n\n" % (time.strftime("%Y-%m-%d %H:%M"), run_id))
            f.write("Applied %d, failed %d. Per store: %s. Skipped: %s. Spot-check: %s\n\n"
                    % (ok, fail, by, skipped, checks))
            for store, iid, reason, title, cat in todo:
                f.write("- %s %s %s — %s\n" % (store, iid, reason, title))
        print("summary:", p)
    except OSError as e:
        print("summary write failed:", e)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
