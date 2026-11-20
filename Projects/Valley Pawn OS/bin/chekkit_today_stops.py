#!/usr/bin/env python3
"""chekkit_today_stops.py -- READ-ONLY, GET only (2026-11-19). Per store: customers who received today's Shop Us Online
text (contains 'pay your loan from your phone'), how many of them replied at all afterwards, and how many replied with an
opt-out word (stop, unsubscribe, cancel, end, quit, remove, opt out). Also opt-out replies today from anyone else.
Counts only -> fleet/state/chekkit_today_stops.json."""
import sys, os, re, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_api as ck
UTC = dt.timezone.utc
since = dt.datetime(2026, 11, 19, 5, 0, tzinfo=UTC)
OPT = re.compile(r"\b(stop|stopall|unsubscribe|cancel|end|quit|remove|opt.?out)\b", re.I)
res = {}
for code in ("HAR", "WAY", "CUL", "LEX", "ROA"):
    r = {"got_text": 0, "replied": 0, "opted_out": 0, "other_optouts_today": 0, "conversations": 0, "errors": 0}
    before = None
    for _ in range(80):
        try:
            b = ck.get(code, "/v1/conversations?limit=50" + ("&before=" + before if before else "")) or {}
        except Exception:
            r["errors"] += 1; break
        convs = b.get("conversations") or []
        stop = False
        for cv in convs:
            lt = ck.ts(cv.get("lastMessageAt"))
            if lt and lt < since:
                stop = True; continue
            try:
                ms = (ck.get(code, "/v1/conversations/%s/messages?limit=60" % (cv.get("id") or cv.get("_id"))) or {}).get("messages") or []
            except Exception:
                r["errors"] += 1; continue
            r["conversations"] += 1
            sent = None; replies = []
            for m in ms:
                t = ck.ts(m.get("createdAt"))
                if not t or t < since: continue
                tx = m.get("text") or ""
                if m.get("sender") == "customer": replies.append((t, tx))
                elif "pay your loan from your phone" in tx.lower(): sent = t if sent is None else min(sent, t)
            if sent:
                r["got_text"] += 1
                after = [x for x in replies if x[0] >= sent]
                if after: r["replied"] += 1
                if any(OPT.search(x[1]) and len(x[1]) < 60 for x in after): r["opted_out"] += 1
            elif any(OPT.search(x[1]) and len(x[1]) < 60 for x in replies):
                r["other_optouts_today"] += 1
        nb = b.get("nextBefore")
        if stop or not nb or nb == before or not convs: break
        before = nb
    res[code] = r
    print(code, r, flush=True)
json.dump({"generated_at": dt.datetime.now(UTC).isoformat(), "stores": res}, open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fleet", "state", "chekkit_today_stops.json"), "w"), indent=1)
