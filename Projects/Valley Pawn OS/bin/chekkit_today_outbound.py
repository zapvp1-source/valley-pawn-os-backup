#!/usr/bin/env python3
"""chekkit_today_outbound.py -- READ-ONLY, GET only (2026-11-19 incident check). Every non-customer message at each store
since 15:00 UTC today, grouped by wording (digits masked), with count, first/last time and sender.
Writes fleet/state/chekkit_today_outbound.txt. No phone numbers or names stored."""
import sys, os, re, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_api as ck
UTC = dt.timezone.utc
since = dt.datetime(2026, 11, 19, 15, 0, tzinfo=UTC)
out = []
for code in ("HAR", "WAY", "CUL", "LEX", "ROA"):
    c = collections.Counter(); first = {}; last = {}
    before = None
    for _ in range(60):
        b = ck.get(code, "/v1/conversations?limit=50" + ("&before=" + before if before else "")) or {}
        convs = b.get("conversations") or []
        stop = False
        for cv in convs:
            lt = ck.ts(cv.get("lastMessageAt"))
            if lt and lt < since:
                stop = True; continue
            ms = (ck.get(code, "/v1/conversations/%s/messages?limit=60" % (cv.get("id") or cv.get("_id"))) or {}).get("messages") or []
            for m in ms:
                t = ck.ts(m.get("createdAt"))
                if not t or t < since or m.get("sender") in ("customer", "note"):
                    continue
                txt = re.sub(r"\d", "#", " ".join((m.get("text") or "").split()))[:220]
                k = (str(m.get("sender")), str(m.get("sentBy")), txt)
                c[k] += 1
                first[k] = min(first.get(k, t), t); last[k] = max(last.get(k, t), t)
        nb = b.get("nextBefore")
        if stop or not nb or nb == before or not convs:
            break
        before = nb
    out.append("== %s" % code)
    for k, v in c.most_common(15):
        out.append("%4d  %s-%s UTC  sender=%s by=%s | %s" % (v, first[k].strftime("%H:%M"), last[k].strftime("%H:%M"), k[0], k[1], k[2]))
open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fleet", "state", "chekkit_today_outbound.txt"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
