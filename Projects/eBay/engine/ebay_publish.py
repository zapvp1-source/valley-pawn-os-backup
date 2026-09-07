#!/usr/bin/env python3
"""Valley Pawn eBay engine — Layer 4: PUBLISH (deterministic formatter).

Builds the plain-language Slack posts from the snapshot + queue. Nothing here is
re-worded by a model at run time — this is the same fix that cured the illegible
#aged-inventory-review post: one formatter owns the message, byte for byte.

  weekly   -> the Monday "eBay Weekly" post for #ebay-performance
  daily    -> the daily new-listings + net-change line for #ebay-listings
  manager  -> one short DM body per store manager
  monthly  -> the 1st-of-month roll-up

Hard gates (Rule 18 — withhold, never caveat):
  * every store must be COMPLETE in channel.json, else print NOTHING and exit 2
  * detail coverage must be >= 90% per store for any quality figure to be printed
  * no failure text, no technical jargon, no counts of things that did not happen (Rule 16)

Usage: ebay_publish.py weekly|daily|manager|monthly [--store NAME]
Exit 0 = body on stdout, post it verbatim. Exit 2 = withhold (reason on stderr).
"""
import json, os, sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ebay_common import DATA_DIR, STORE_ORDER

now = datetime.now(timezone.utc)
MIN_COVERAGE = 90.0
MANAGERS = {"Roanoke": ("Benjie", "U0631AECK4K"), "Culpeper": ("Sandi", "U04C5DL5EKH"),
            "Waynesboro": ("Chadd", "U04U136MF6V"), "Harrisonburg": ("Walker", "U09UTFT4P7X"),
            "Lexington": ("Uriah", "U09H9ES2LKA")}


def load(n):
    p = os.path.join(DATA_DIR, "latest", n)
    return json.load(open(p)) if os.path.exists(p) else None


def withhold(msg):
    sys.stderr.write("WITHHOLD: %s\n" % msg)
    sys.exit(2)


def money(x):
    return "${:,.0f}".format(x or 0)


def applied_last_7d(store=None):
    """Counts of changes the ledger says were actually applied to eBay in the last 7 days.
    The queue says what SHOULD change; only this says what DID. Publications use this one."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ledger.jsonl")
    if not os.path.exists(p):
        return {}
    cutoff = (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    by = {}
    for line in open(p):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if not r.get("ok") or (r.get("ts") or "") < cutoff:
            continue
        if store and r.get("store") != store:
            continue
        if str(r.get("run_id", "")).endswith("-revert"):
            continue
        by[r.get("kind") or r.get("action")] = by.get(r.get("kind") or r.get("action"), 0) + 1
    return by


def gate():
    ch = load("channel.json")
    if not ch:
        withhold("no snapshot")
    missing = [s for s in STORE_ORDER if s not in ch["complete_stores"]]
    if missing:
        withhold("%d of 5 stores complete, missing %s" % (len(ch["complete_stores"]), ", ".join(missing)))
    stale = [s for s in STORE_ORDER if ch["stores"][s]["date"] != ch["date"]]
    if stale:
        withhold("stale snapshot for %s" % ", ".join(stale))
    q = load("queue.json")
    if not q:
        withhold("no rule queue")
    return ch, q


def qrows(q, kind=None, store=None, mode=None):
    return [r for r in q["queue"]
            if (kind is None or r["kind"] == kind) and (store is None or r["store"] == store)
            and (mode is None or r["mode"] == mode)]


def weekly(ch, q):
    S = ch["stores"]
    tot = lambda f: sum(S[s][f] or 0 for s in STORE_ORDER)
    L = []
    L.append("*eBay — week of %s*" % now.strftime("%b %-d"))
    L.append("%d listings live, %s of inventory. Last 90 days: %d sold for %s."
             % (tot("active"), money(tot("listed_value")), tot("sold90_units"), money(tot("sold90_revenue"))))
    L.append("")
    L.append("```")
    L.append("Store          Live   Value    Sold 90d   Rev 90d   Aged 90d+")
    for s in sorted(STORE_ORDER, key=lambda x: -(S[x]["sold90_revenue"] or 0)):
        d = S[s]
        L.append("%-13s %5d %8s %9d %9s %6d / %s"
                 % (s, d["active"], money(d["listed_value"]), d["sold90_units"],
                    money(d["sold90_revenue"]), d["aged90"], money(d["aged90_value"])))
    L.append("%-13s %5d %8s %9d %9s %6d / %s"
             % ("TOTAL", tot("active"), money(tot("listed_value")), tot("sold90_units"),
                money(tot("sold90_revenue")), tot("aged90"), money(tot("aged90_value"))))
    L.append("```")

    # Rule 18: this line reports only what the ledger says actually changed on eBay in the last
    # 7 days — never what the queue merely planned. A planned-but-unapplied fix must not appear.
    by = applied_last_7d()
    if by:
        names = {"returns_fix": "put back on 30-day returns", "bestoffer_on": "had Best Offer turned back on",
                 "sku_set": "linked back to their Bravo item number"}
        L.append("")
        L.append("*Fixed automatically this week:* " + ", ".join("%d %s" % (v, names.get(k, k)) for k, v in sorted(by.items())) + ".")

    needs = []
    for kind, label in (("offer_expiring", "offer%s waiting on an answer, expiring within two days"),
                        ("buyer_msg_unread", "unread message%s from a buyer"),
                        ("feedback_unanswered", "recent feedback comment%s with no reply")):
        rows = qrows(q, kind=kind)
        if rows:
            per = {}
            for r in rows: per[r["store"]] = per.get(r["store"], 0) + 1
            needs.append("• %d %s — %s" % (len(rows), label % ("" if len(rows) == 1 else "s"),
                                           ", ".join("%s %d" % (s, per[s]) for s in STORE_ORDER if s in per)))
    aged = qrows(q, kind="aged_90") + qrows(q, kind="at_markdown_floor")
    if aged:
        per = {}
        for r in aged: per[r["store"]] = per.get(r["store"], 0) + 1
        needs.append("• %d listings past 90 days that need a price cut or a pull — %s"
                     % (len(aged), ", ".join("%s %d" % (s, per[s]) for s in STORE_ORDER if s in per)))
    if needs:
        L.append("")
        L.append("*Needs a person this week:*")
        L += needs

    cov = [s for s in STORE_ORDER if (S[s]["detail_coverage"] or 0) >= MIN_COVERAGE]
    if len(cov) == 5:
        pics = sum(S[s]["pics_lt8"] for s in STORE_ORDER)
        spec = sum(S[s]["specifics_lt5"] for s in STORE_ORDER)
        L.append("")
        L.append("*Listing quality:* %d listings have fewer than 8 photos and %d have fewer than 5 item specifics — "
                 "these are the two things eBay's search uses most." % (pics, spec))
    return "\n".join(L)


def manager(ch, q, store):
    who = MANAGERS.get(store, (store, ""))[0]
    d = ch["stores"][store]
    L = ["Hi %s — your eBay listings this week." % who,
         "%d live, %s of inventory. %d sold in the last 90 days for %s."
         % (d["active"], money(d["listed_value"]), d["sold90_units"], money(d["sold90_revenue"]))]
    done = sum(applied_last_7d(store).values())   # ledger, not queue (Rule 18)
    if done:
        L.append("We fixed %d listing settings for you automatically — nothing for you to do there." % done)
    todo = []
    for kind, one, many in (("offer_expiring", "offer waiting on your answer (expires within 2 days)",
                             "offers waiting on your answer (expiring within 2 days)"),
                            ("buyer_msg_unread", "unread message from a buyer", "unread messages from buyers"),
                            ("photos_low", "listing with fewer than 8 photos", "listings with fewer than 8 photos"),
                            ("aged_90", "listing past 90 days needing a cut or a pull",
                             "listings past 90 days needing a cut or a pull"),
                            ("at_markdown_floor", "listing already at the lowest price — pull or relist",
                             "listings already at the lowest price — pull or relist")):
        rows = qrows(q, kind=kind, store=store)
        if rows:
            todo.append("• %d %s" % (len(rows), one if len(rows) == 1 else many))
    if todo:
        L.append("")
        L.append("Worth your time:")
        L += todo
    else:
        L.append("Nothing needs your attention this week.")
    return "\n".join(L)


def daily(ch, q):
    S = ch["stores"]
    L = ["*eBay listings — %s*" % now.strftime("%A, %b %-d")]
    tot_active = sum(S[s]["active"] for s in STORE_ORDER)
    tot_value = sum(S[s]["listed_value"] for s in STORE_ORDER)
    prev = None
    for back in range(1, 8):
        p = os.path.join(DATA_DIR, (now - timedelta(days=back)).strftime("%Y-%m-%d"))
        if os.path.isdir(p):
            try:
                prev = sum(len(json.load(open(os.path.join(p, s + ".json")))["active"]) for s in STORE_ORDER)
                prev_date = (now - timedelta(days=back)).strftime("%b %-d")
                break
            except Exception:
                prev = None
    for s in sorted(STORE_ORDER, key=lambda x: -S[x]["active"]):
        L.append("• %s — %d live, %s" % (s, S[s]["active"], money(S[s]["listed_value"])))
    L.append("*Total: %d listings, %s.*" % (tot_active, money(tot_value)))
    if prev is not None:
        delta = tot_active - prev
        L.append("Net change since %s: %s%d listings." % (prev_date, "+" if delta >= 0 else "", delta))
    return "\n".join(L)


def monthly(ch, q):
    S = ch["stores"]
    L = ["*eBay — month in review*"]
    tot = lambda f: sum(S[s][f] or 0 for s in STORE_ORDER)
    L.append("%d listings live, %s of inventory. Trailing 90 days: %d sold for %s, fees %s (%.1f%% of sales)."
             % (tot("active"), money(tot("listed_value")), tot("sold90_units"), money(tot("sold90_revenue")),
                money(tot("fees90")), 100.0 * tot("fees90") / max(1.0, tot("sold90_revenue"))))
    L.append("")
    for s in sorted(STORE_ORDER, key=lambda x: -(S[x]["sold90_revenue"] or 0)):
        d = S[s]
        L.append("• *%s* — %d live, %s sold (90d), feedback %s at %s%% positive"
                 % (s, d["active"], money(d["sold90_revenue"]), d["feedback_score"],
                    (d["pos_12mo"] or [None])[0] if isinstance(d["pos_12mo"], list) else d["pos_12mo"]))
    aged = tot("aged90")
    L.append("")
    L.append("%d listings are past 90 days, holding %s of inventory." % (aged, money(tot("aged90_value"))))
    return "\n".join(L)


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "weekly"
    ch, q = gate()
    if what == "weekly":
        print(weekly(ch, q))
    elif what == "daily":
        print(daily(ch, q))
    elif what == "monthly":
        print(monthly(ch, q))
    elif what == "manager":
        store = sys.argv[sys.argv.index("--store") + 1] if "--store" in sys.argv else None
        if store:
            print(manager(ch, q, store))
        else:
            for s in STORE_ORDER:
                print("=== %s (%s %s)" % (s, MANAGERS[s][0], MANAGERS[s][1]))
                print(manager(ch, q, s)); print()
    else:
        withhold("unknown output %s" % what)


if __name__ == "__main__":
    main()
