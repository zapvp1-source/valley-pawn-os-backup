#!/usr/bin/env python3
"""chekkit_len_failed_read.py -- READ-ONLY, GET only (2026-11-19, Joshua "do it all": shorten wording, stop texting failed numbers).
Per store since 2026-09-01:
  - real sent length of review invites, gold blasts and win-back texts (and the review link length)
  - numbers whose most recent tracked text failed delivery (carrier codes 30003/30005/30006/30008) and never delivered after
Writes fleet/state/chekkit_len_failed.json (counts only) and fleet/state/chekkit_failed/<STORE>.txt (numbers, stays on this Mac)."""
import sys, os, json, time, re, collections, threading, statistics, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_api as ck
UTC = dt.timezone.utc
SINCE = dt.datetime(2026, 9, 1, tzinfo=UTC)
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fleet", "state")
os.makedirs(os.path.join(ROOT, "chekkit_failed"), exist_ok=True)
BAD = {"30003", "30005", "30006", "30008"}

def fam(t):
    t = (t or "").strip().lower()
    if t.startswith("hi from valley pawn in") or "need cash? no credit check" in t: return "winback"
    if "buys gold and silver" in t: return "gold"
    if "review" in t and "http" in t: return "review"
    return None

def phone_of(c):
    for k in ("phone", "customerPhone", "phoneNumber", "to"):
        if c.get(k): return str(c[k])
    for k in ("customer", "contact"):
        v = c.get(k)
        if isinstance(v, dict):
            for kk in ("phone", "phoneNumber", "mobile"):
                if v.get(kk): return str(v[kk])
    return ""

res = {}
def store(code):
    r = {"len": collections.defaultdict(list), "link": [], "conv_keys": [], "failed": 0, "failed_no_phone": 0, "conversations": 0, "errors": 0}
    res[code] = r; failed = []
    if not ck.token(code): r["error"] = "no token"; return
    before = None
    for _ in range(400):
        try: b = ck.get(code, "/v1/conversations?limit=50" + ("&before=" + before if before else "")) or {}
        except Exception as e: r["errors"] += 1; r["error"] = str(e)[:120]; break
        convs = b.get("conversations") or []; stop = False
        for c in convs:
            if not r["conv_keys"]: r["conv_keys"] = sorted(c.keys())
            last = ck.ts(c.get("lastMessageAt"))
            if last and last < SINCE: stop = True; continue
            try: msgs = (ck.get(code, "/v1/conversations/%s/messages?limit=500" % (c.get("id") or c.get("_id"))) or {}).get("messages") or []
            except Exception: r["errors"] += 1; continue
            r["conversations"] += 1
            tracked = []
            for m in msgs:
                t = ck.ts(m.get("createdAt"))
                if not t or t < SINCE or m.get("sender") in ("customer", "note", "event"): continue
                f = fam(m.get("text"))
                if f:
                    r["len"][f].append(len(m.get("text") or ""))
                    if f == "review":
                        u = re.search(r"https?://\S+", m.get("text") or "")
                        if u: r["link"].append(len(u.group(0)))
                if m.get("status") in ("delivered", "undelivered", "failed"): tracked.append((t, m.get("status"), str(m.get("errorCode") or "")))
            replied = any(m.get("sender") == "customer" and (ck.ts(m.get("createdAt")) or SINCE) >= SINCE for m in msgs)
            if tracked:
                tracked.sort()
                if tracked[-1][1] != "delivered" and tracked[-1][2] in BAD and not replied:
                    p = re.sub(r"\D", "", phone_of(c))[-10:]
                    if p: failed.append(p + "\t" + tracked[-1][2])
                    else: r["failed_no_phone"] += 1
            time.sleep(0.1)
        nb = b.get("nextBefore")
        if stop or not nb or nb == before or not convs: break
        before = nb; time.sleep(0.3)
    r["failed"] = len(failed)
    open(os.path.join(ROOT, "chekkit_failed", code + ".txt"), "w").write("\n".join(sorted(set(failed))) + "\n")
    out = {}
    for f, L in r["len"].items():
        out[f] = {"n": len(L), "min": min(L), "median": statistics.median(L), "max": max(L), "over160": sum(1 for x in L if x > 160)}
    r["len"] = out
    r["link"] = {"n": len(r["link"]), "min": min(r["link"]), "max": max(r["link"])} if r["link"] else {}

th = [threading.Thread(target=store, args=(c,)) for c in ("CUL", "WAY", "HAR", "LEX", "ROA")]
[t.start() for t in th]; [t.join() for t in th]
json.dump({"generated_at": dt.datetime.now(UTC).isoformat(), "stores": res}, open(os.path.join(ROOT, "chekkit_len_failed.json"), "w"), indent=1)
for c, r in res.items(): print(c, r["conversations"], r["failed"], r["failed_no_phone"], r["errors"], r.get("error", ""))
