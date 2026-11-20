#!/usr/bin/env python3
"""chekkit_overlap_read.py [--since YYYY-MM-DD] -- READ-ONLY (2026-11-19, Joshua: "evaluate this properly in chekkit ...
make sure we dont have redundant efforts anywhere via text"). GET only. Per store since the date:
  - every automated/campaign text grouped by its wording (names and numbers masked), with counts per month
  - what is scheduled (the text of 'scheduled message for <date>' log lines) by date
  - estimated billable parts (a text over 160 characters counts as several)
  - delivery failures
  - overlap: customers who got 2+ different automated sends within 7 days, and 3+ automated texts in 30 days
Writes fleet/state/chekkit_overlap_read.json. Stores no phone numbers or customer names."""
import sys, os, json, time, re, collections, threading, hashlib, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_api as ck
UTC = dt.timezone.utc
since_s = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else "2026-09-01"
SINCE = dt.datetime.fromisoformat(since_s).replace(tzinfo=UTC)
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fleet", "state", "chekkit_overlap_read.json")

def tmpl(t):
    t = re.sub(r"https?://\S+", "<link>", (t or "").strip())
    t = re.sub(r"^(hi|hey|hello|happy birthday,?|happy anniversary)\s+[A-Za-z'\-]+([,!])", r"\1 <name>\2", t, flags=re.I)
    t = re.sub(r"\d", "#", t)
    return " ".join(t.split())[:150]

def parts(t):
    n = len(t or "")
    return 1 if n <= 160 else -(-n // 153)

def family(text, sender, sent_by):
    t = (text or "").strip().lower()
    if sender in ("customer", "note"): return None
    if sender == "event":
        return "LOG:scheduled" if t.startswith("scheduled message for") else None
    if "(automated reply" in t or sender == "ai": return "ai_reply"
    if "missed your call" in t: return "missed_call"
    if t.startswith("hi from valley pawn in") or "need cash? no credit check" in t: return "winback"
    if "review" in t and ("google" in t or "leave" in t or "http" in t): return "review_invite"
    if "buys gold and silver" in t or "we buy gold" in t: return "gold_campaign"
    if "thevalleypawn.com/app" in t: return "app_link"
    if "thevalleypawn.com/shop" in t or "shop us online" in t or "ebay" in t: return "shop_online"
    if t.startswith("thanks for reaching out") or t.startswith("thanks for messaging") or "we will text you as soon as" in t or "we have received your message" in t: return "auto_ack"
    if (sent_by or "") in ("Joshua Davis", ""): return "owner_other"
    return "staff"

AUTO = {"missed_call", "winback", "review_invite", "gold_campaign", "app_link", "shop_online", "owner_other"}
res = {}
def store(code):
    r = {"by_month": collections.Counter(), "parts_by_month": collections.Counter(), "templates": collections.Counter(),
         "scheduled": collections.Counter(), "status": collections.Counter(), "pairs7d": collections.Counter(),
         "auto_per_customer_30d": collections.Counter(), "customers_with_auto": 0, "conversations": 0, "errors": 0}
    res[code] = r
    if not ck.token(code):
        r["error"] = "no token"; return
    before = None
    for _ in range(400):
        try:
            b = ck.get(code, "/v1/conversations?limit=50" + ("&before=" + before if before else "")) or {}
        except Exception as e:
            r["errors"] += 1; r["error"] = str(e)[:120]; break
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
            autos = []
            for m in msgs:
                t = ck.ts(m.get("createdAt"))
                if not t or t < SINCE: continue
                fam = family(m.get("text"), m.get("sender"), m.get("sentBy"))
                if not fam: continue
                mo = t.strftime("%Y-%m")
                if fam == "LOG:scheduled":
                    r["scheduled"][tmpl(m.get("text"))[:150]] += 1; continue
                r["by_month"][mo + ":" + fam] += 1
                r["parts_by_month"][mo] += parts(m.get("text"))
                r["status"][str(m.get("status")) + "/" + str(m.get("errorCode") or "")] += 1
                if fam != "staff": r["templates"][fam + " | " + tmpl(m.get("text"))] += 1
                if fam in AUTO: autos.append((t, fam))
            if autos:
                r["customers_with_auto"] += 1
                autos.sort()
                seen = set()
                for i, (t1, f1) in enumerate(autos):
                    for t2, f2 in autos[i + 1:]:
                        if (t2 - t1).days > 7: break
                        if f1 != f2 and (f1, f2) not in seen:
                            seen.add((f1, f2)); r["pairs7d"][" + ".join(sorted((f1, f2)))] += 1
                last30 = [f for t, f in autos if t >= dt.datetime.now(UTC) - dt.timedelta(days=30)]
                r["auto_per_customer_30d"][min(len(last30), 5)] += 1
            time.sleep(0.12)
        nb = b.get("nextBefore")
        if stop or not nb or nb == before or not convs: break
        before = nb; time.sleep(0.4)

th = [threading.Thread(target=store, args=(c,)) for c in ("CUL", "WAY", "HAR", "LEX", "ROA")]
[t.start() for t in th]; [t.join() for t in th]
for c, r in res.items():
    r["by_month"] = dict(sorted(r["by_month"].items())); r["parts_by_month"] = dict(sorted(r["parts_by_month"].items()))
    r["templates"] = r["templates"].most_common(25); r["scheduled"] = r["scheduled"].most_common(12)
    r["status"] = dict(r["status"]); r["pairs7d"] = dict(r["pairs7d"]); r["auto_per_customer_30d"] = dict(r["auto_per_customer_30d"])
json.dump({"since": since_s, "generated_at": dt.datetime.now(UTC).isoformat(), "stores": res}, open(OUT, "w"), indent=1)
for c, r in res.items(): print(c, r["conversations"], r["errors"], r.get("error", ""))
