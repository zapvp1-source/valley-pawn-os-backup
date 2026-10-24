#!/usr/bin/env python3
"""chekkit_text_census.py [--since YYYY-MM-DD] — READ-ONLY (2026-10-23). Counts every text in Chekkit since a date,
per store and by kind, for the November team deck. GET only (conversations + messages). Writes
fleet/state/chekkit_text_census.json and prints a summary. No Slack, no sends, no edits."""
import sys, os, json, time, collections, threading, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_api as ck
UTC = dt.timezone.utc
since_s = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else "2026-01-01"
SINCE = dt.datetime.fromisoformat(since_s).replace(tzinfo=UTC)
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fleet", "state", "chekkit_text_census.json")

def kind(m):
    s = m.get("sender"); t = (m.get("text") or "").strip().lower()
    if s == "customer": return "inbound_customer"
    if s == "note": return "internal_note"
    if s == "ai": return "chekkit_ai"
    if "(automated reply" in t: return "auto_ai_reply"
    if t.startswith("hi, this is valley pawn in") and "missed your call" in t: return "auto_missed_call"
    if t.startswith("hi from valley pawn in"): return "auto_winback"
    if "review" in t and ("google" in t or "leave" in t or "http" in t) and s == "event": return "review_invite"
    if s == "event": return "event_other"
    if s == "business": return "staff_text"
    return "other_" + str(s)

res = {}
def store(code):
    r = {"kinds": collections.Counter(), "months": collections.Counter(), "conversations": 0, "first": None, "last": None, "errors": 0, "pages": 0}
    res[code] = r
    try:
        ck.token(code) or (_ for _ in ()).throw(RuntimeError("no token"))
    except Exception as e:
        r["error"] = str(e); return
    before = None
    for _ in range(600):
        try:
            b = ck.get(code, "/v1/conversations?limit=50" + ("&before=" + before if before else "")) or {}
        except Exception as e:
            r["errors"] += 1; r["error"] = str(e)[:120]; break
        r["pages"] += 1
        convs = b.get("conversations") or []
        stop = False
        for c in convs:
            last = ck.ts(c.get("lastMessageAt"))
            if last and last < SINCE:
                stop = True; continue
            try:
                msgs = (ck.get(code, "/v1/conversations/%s/messages?limit=500" % (c.get("id") or c.get("_id"))) or {}).get("messages") or []
            except Exception:
                r["errors"] += 1; continue
            r["conversations"] += 1
            for m in msgs:
                t = ck.ts(m.get("createdAt"))
                if not t or t < SINCE: continue
                k = kind(m); r["kinds"][k] += 1; r["months"][t.strftime("%Y-%m") + ":" + ("in" if k == "inbound_customer" else "out")] += 1
                d = t.date().isoformat(); r["first"] = min(r["first"] or d, d); r["last"] = max(r["last"] or d, d)
            time.sleep(0.15)
        nb = b.get("nextBefore")
        if stop or not nb or nb == before or not convs: break
        before = nb; time.sleep(0.5)

th = [threading.Thread(target=store, args=(c,)) for c in ("CUL", "WAY", "HAR", "LEX", "ROA")]
[t.start() for t in th]; [t.join() for t in th]
tot = collections.Counter()
for c, r in res.items():
    tot.update(r["kinds"]); r["kinds"] = dict(r["kinds"]); r["months"] = dict(sorted(r["months"].items()))
out = {"since": since_s, "generated_at": dt.datetime.now(UTC).isoformat(), "total": dict(tot), "stores": res}
json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps({"since": since_s, "total": dict(tot)}, indent=1))
for c, r in res.items(): print(c, r.get("conversations"), r.get("pages"), r.get("first"), r.get("last"), r.get("errors"), r.get("error", ""), r["kinds"])
