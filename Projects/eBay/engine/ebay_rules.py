#!/usr/bin/env python3
"""Valley Pawn eBay engine — Layer 2: RULES (pure, deterministic, no network, no writes).

Reads engine/data/latest/<Store>.json and emits an action queue with a reason per row:

  AUTO   — deterministic and proven safe; ebay_apply.py may execute these
           returns_fix, bestoffer_on, sku_set
  FLAG   — needs a human or a judgment model; published, never auto-applied
           offer_expiring, return_msg_unread, feedback_unanswered, photos_low,
           specifics_low, title_short, aged_30/60/90, at_markdown_floor, no_bravo_link

Writes engine/data/latest/queue.json. Rule 18: a store missing from channel.json's
complete list is skipped entirely rather than partially evaluated.

Usage: ebay_rules.py [--json]
"""
import json, os, sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ebay_common import DATA_DIR, STORE_ORDER, CODE_RE

now = datetime.now(timezone.utc)
MARKDOWN_STATE = os.path.expanduser("~/ebay_markdown_state.json")
TERMINAL_STATE = os.path.expanduser("~/ebay_markdown_terminal_state.json")
FEEDBACK_ANSWERED = os.path.expanduser("~/ebay_feedback_answered.json")
try:
    _a = json.load(open(FEEDBACK_ANSWERED))
    ANSWERED = set(str(x) for x in (_a if isinstance(_a, list) else _a.keys()))
except Exception:
    ANSWERED = set()

# Listing-Age Standard (signed policy, 2026-08-05) — day thresholds
AGE_FIRST, AGE_SECOND, AGE_PULL = 30, 60, 90
PHOTO_MIN, SPECIFICS_MIN, TITLE_MIN = 8, 5, 60
BO_ACCEPT, BO_DECLINE = 0.90, 0.75


def load(name):
    p = os.path.join(DATA_DIR, "latest", name)
    return json.load(open(p)) if os.path.exists(p) else None


def dt(s):
    try:
        return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def evaluate(store, snap, mstate):
    q = []

    def add(kind, mode, item, reason, **kw):
        row = {"store": store, "kind": kind, "mode": mode, "ItemID": item.get("ItemID"),
               "title": (item.get("Title") or "")[:70], "price": item.get("list_price") or item.get("price"),
               "days_live": item.get("days_live"), "reason": reason}
        row.update(kw)
        q.append(row)

    for it in snap["active"]:
        iid = it["ItemID"]
        detailed = it.get("detail_cached")

        # --- AUTO: policy drift (the two levers proven safe since 2026-08-23) ---
        if detailed:
            if (it.get("returns_accepted") or "") != "ReturnsAccepted" or (it.get("returns_within") or "") != "Days_30":
                add("returns_fix", "AUTO", it, "returns %s/%s -> ReturnsAccepted/Days_30"
                    % (it.get("returns_accepted"), it.get("returns_within")))
            if not it.get("best_offer") and (it.get("list_price") or 0) > 0:
                add("bestoffer_on", "AUTO", it, "Best Offer off; enable at %d%%/%d%% of list"
                    % (BO_ACCEPT * 100, BO_DECLINE * 100))

        # --- AUTO: Bravo link ---
        if not (it.get("SKU") or "").strip():
            m = CODE_RE.search(it.get("Title") or "")
            if m:
                add("sku_set", "AUTO", it, "Bravo code %s in title, SKU empty" % m.group(1), code=m.group(1))
            else:
                add("no_bravo_link", "FLAG", it, "no SKU and no Bravo code in title — cannot cost-check or reconcile")

        # --- FLAG: Listing-Age Standard ---
        d = it.get("days_live")
        st = mstate.get(iid) or {}
        cuts = st.get("cuts", 0)
        if d is not None:
            if cuts >= 3:
                add("at_markdown_floor", "FLAG", it, "at the 30%% floor since %s — pull or relist" % st.get("last", "?"), cuts=cuts)
            elif d >= AGE_PULL:
                add("aged_90", "FLAG", it, "%d days live, %d cuts — pull or final relist" % (d, cuts), cuts=cuts)
            elif d >= AGE_SECOND:
                add("aged_60", "FLAG", it, "%d days live, %d cuts — second reduction or relist" % (d, cuts), cuts=cuts)
            elif d >= AGE_FIRST:
                add("aged_30", "FLAG", it, "%d days live, %d cuts — send offer to watchers or first cut" % (d, cuts), cuts=cuts)

        # --- FLAG: listing quality (never auto-written; see the 2026-08-22 incident) ---
        if detailed:
            if it.get("pics", 0) < PHOTO_MIN:
                add("photos_low", "FLAG", it, "%d photos, standard is %d-12" % (it.get("pics", 0), PHOTO_MIN))
            if it.get("specifics_count", 0) < SPECIFICS_MIN:
                add("specifics_low", "FLAG", it, "%d item specifics, target %d+" % (it.get("specifics_count", 0), SPECIFICS_MIN))
            if len(it.get("Title") or "") < TITLE_MIN:
                add("title_short", "FLAG", it, "title %d chars of 80" % len(it.get("Title") or ""))

    # --- FLAG: time-sensitive, not per-listing ---
    idx = {i["ItemID"]: i for i in snap["active"]}
    for o in (snap.get("best_offers") or []):
        if (o.get("hours_left") or 999) < 48:
            it = idx.get(o.get("ItemID")) or {}
            q.append({"store": store, "kind": "offer_expiring", "mode": "FLAG", "ItemID": o.get("ItemID"),
                      "title": (it.get("Title") or "")[:70], "price": o.get("price"), "days_live": None,
                      "listed_at": it.get("list_price"), "buyer": o.get("buyer"),
                      "reason": "offer of %s from %s expires in %.0f h%s"
                                % (o.get("price"), o.get("buyer"), o.get("hours_left") or 0,
                                   " (asking %s)" % it.get("list_price") if it.get("list_price") else "")})

    # A message from sender "eBay" is eBay's own status mail (Return approved / Refund issued /
    # payout), not a buyer waiting on us. Counting those as "unread return messages" is what made
    # every prior audit report 22-26 of them; only a real buyer message needs a person.
    for m in (snap.get("messages") or []):
        if m["read"]:
            continue
        sender = (m.get("sender") or "").strip().lower()
        if sender in ("ebay", "ebay.com", ""):
            if m["category"] in ("return_refund", "case_dispute"):
                q.append({"store": store, "kind": "return_notice_unread", "mode": "FLAG", "ItemID": m.get("ItemID"),
                          "title": m["subject"][:70], "price": None, "days_live": None,
                          "reason": "eBay status notice, unread — informational, no reply needed"})
            continue
        q.append({"store": store, "kind": "buyer_msg_unread", "mode": "FLAG", "ItemID": m.get("ItemID"),
                  "title": m["subject"][:70], "price": None, "days_live": None,
                  "reason": "unread message from buyer %s, %s" % (m.get("sender"), (m.get("date") or "")[:10])})

    # eBay's GetFeedback does NOT reliably return our own reply, so "response is empty" is not
    # proof it is unanswered (proven 2026-09-05). ~/ebay_feedback_answered.json is the real ledger.
    for f in ((snap.get("feedback") or {}).get("neg_neutral") or []):
        d = dt(f.get("date") or "")
        if f.get("response") or str(f.get("id")) in ANSWERED:
            continue
        if d and d >= now - timedelta(days=365):
            q.append({"store": store, "kind": "feedback_unanswered", "mode": "FLAG", "ItemID": f.get("ItemID"),
                      "title": (f.get("text") or "")[:70], "price": None, "days_live": None,
                      "reason": "%s feedback %s from %s, no reply on record"
                                % (f["type"], (f.get("date") or "")[:10], f.get("buyer"))})
    return q


def main():
    ch = load("channel.json")
    if not ch:
        raise SystemExit("no channel.json — run ebay_snapshot.py first")
    mstate = json.load(open(MARKDOWN_STATE)) if os.path.exists(MARKDOWN_STATE) else {}
    queue, skipped = [], []
    for s in STORE_ORDER:
        if s not in ch["complete_stores"]:
            skipped.append(s); continue
        snap = load(s + ".json")
        queue += evaluate(s, snap, mstate)
    out = {"date": ch["date"], "generated": now.isoformat(), "skipped_stores": skipped, "queue": queue}
    json.dump(out, open(os.path.join(DATA_DIR, "latest", "queue.json"), "w"), indent=1)

    if "--json" in sys.argv:
        print(json.dumps(out, indent=1)); return
    kinds = {}
    for r in queue:
        kinds.setdefault((r["mode"], r["kind"]), []).append(r)
    print("queue for %s  (skipped: %s)" % (out["date"], skipped or "none"))
    for mode in ("AUTO", "FLAG"):
        for (m, k), rows in sorted(kinds.items()):
            if m != mode: continue
            per = {}
            for r in rows: per[r["store"]] = per.get(r["store"], 0) + 1
            print("  %-4s %-22s %4d   %s" % (m, k, len(rows), " ".join("%s:%d" % (s[:3].upper(), per[s]) for s in STORE_ORDER if s in per)))
    print("total %d rows (%d AUTO, %d FLAG)" % (len(queue), sum(1 for r in queue if r["mode"] == "AUTO"),
                                                sum(1 for r in queue if r["mode"] == "FLAG")))


if __name__ == "__main__":
    main()
