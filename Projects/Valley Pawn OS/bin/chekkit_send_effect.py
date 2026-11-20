#!/usr/bin/env python3
"""chekkit_send_effect.py [--since YYYY-MM-DD] -- READ-ONLY (2026-11-18, Joshua: "evaluate the effectiveness of the
sends"). GET only (conversations + messages) through chekkit_api. For every text since the date: counts by store,
month and kind; what the unclassified automated ("event") texts are; and for each automated send whether the
customer wrote back within 72 hours or opted out. Writes fleet/state/chekkit_send_effect.json. No sends, no edits,
no Slack. Stores no phone numbers or names."""
import sys, os, json, time, re, collections, threading, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_api as ck
UTC = dt.timezone.utc
since_s = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else "2026-08-01"
SINCE = dt.datetime.fromisoformat(since_s).replace(tzinfo=UTC)
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fleet", "state", "chekkit_send_effect.json")
STOPS = ("stop", "unsubscribe", "stopall", "cancel", "quit", "end")


def kind(m):
    s = m.get("sender"); t = (m.get("text") or "").strip().lower()
    if s == "customer": return "inbound_customer"
    if s == "note": return "internal_note"
    if s == "ai": return "chekkit_ai"
    if "(automated reply" in t: return "auto_ai_reply"
    if t.startswith("hi, this is valley pawn in") and "missed your call" in t: return "auto_missed_call"
    if t.startswith("hi from valley pawn in") or "need cash? no credit check" in t: return "auto_winback"
    if "thevalleypawn.com/app" in t and "payment" in t: return "auto_app_link"
    if "review" in t and ("google" in t or "leave" in t or "http" in t): return "review_invite"
    if "shop" in t and ("ebay" in t or "online" in t or "thevalleypawn.com/shop" in t): return "shop_online_campaign"
    if s == "event": return "event_other"
    if s == "business": return "owner_or_campaign" if (m.get("sentBy") or "") in ("Joshua Davis", "") else "staff_text"
    return "other_" + str(s)


def pattern(t):
    t = re.sub(r"https?://\S+", "<link>", (t or "").strip().lower())
    t = re.sub(r"\d", "#", t)
    return " ".join(t.split()[:7])[:70]


res = {}
def store(code):
    r = {"months": collections.Counter(), "event_patterns": collections.Counter(), "campaign_patterns": collections.Counter(),
         "sent": collections.Counter(), "replied72h": collections.Counter(), "stop72h": collections.Counter(),
         "msg_keys": collections.Counter(), "event_types": collections.Counter(), "conversations": 0, "errors": 0, "pages": 0}
    res[code] = r
    if not ck.token(code):
        r["error"] = "no token"; return
    before = None
    for _ in range(400):
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
            rows = sorted(((ck.ts(m.get("createdAt")), m) for m in msgs if ck.ts(m.get("createdAt"))), key=lambda x: x[0])
            inbound = [(t, (m.get("text") or "").strip().lower()) for t, m in rows if m.get("sender") == "customer"]
            for t, m in rows:
                if t < SINCE: continue
                k = kind(m); r["months"][t.strftime("%Y-%m") + ":" + k] += 1
                for key in m.keys(): r["msg_keys"][key] += 1
                if k == "event_other":
                    r["event_patterns"][pattern(m.get("text"))] += 1
                    r["event_types"][str(m.get("type") or m.get("eventType") or m.get("channel") or "")] += 1
                if k == "owner_or_campaign": r["campaign_patterns"][pattern(m.get("text"))] += 1
                if k in ("inbound_customer", "internal_note"): continue
                r["sent"][k] += 1
                rep = [x for tt, x in inbound if t < tt <= t + dt.timedelta(hours=72)]
                if rep:
                    r["replied72h"][k] += 1
                    if any(x.strip(" .!").split(" ")[0] in STOPS for x in rep if x): r["stop72h"][k] += 1
            time.sleep(0.12)
        nb = b.get("nextBefore")
        if stop or not nb or nb == before or not convs: break
        before = nb; time.sleep(0.4)

th = [threading.Thread(target=store, args=(c,)) for c in ("CUL", "WAY", "HAR", "LEX", "ROA")]
[t.start() for t in th]; [t.join() for t in th]
for c, r in res.items():
    r["months"] = dict(sorted(r["months"].items()))
    r["event_patterns"] = r["event_patterns"].most_common(15); r["campaign_patterns"] = r["campaign_patterns"].most_common(12)
    for k in ("sent", "replied72h", "stop72h", "event_types"): r[k] = dict(r[k])
    r["msg_keys"] = sorted(r["msg_keys"])
json.dump({"since": since_s, "generated_at": dt.datetime.now(UTC).isoformat(), "stores": res}, open(OUT, "w"), indent=1)
for c, r in res.items(): print(c, r["conversations"], r["pages"], r["errors"], r.get("error", ""), r["sent"])
