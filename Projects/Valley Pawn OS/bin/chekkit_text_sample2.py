#!/usr/bin/env python3
"""chekkit_text_sample2.py — READ-ONLY (2026-10-24). For CUL+WAY, recent conversations: business messages in Sep vs
Oct 2026 grouped by sentBy and by the first 60 chars of text, to label the census. GET only."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_api as ck
for code in ("WAY", "HAR"):
    by = collections.Counter(); tx = collections.Counter(); before = None; n = 0
    for _ in range(8):
        b = ck.get(code, "/v1/conversations?limit=50" + ("&before=" + before if before else "")) or {}
        for c in b.get("conversations") or []:
            n += 1
            for m in (ck.get(code, "/v1/conversations/%s/messages?limit=500" % c.get("id")) or {}).get("messages") or []:
                ts = (m.get("createdAt") or "")[:7]
                if m.get("sender") == "business" and ts in ("2026-09", "2026-10"):
                    by[(ts, m.get("sentBy"), str(m.get("channel")))] += 1
                    if ts == "2026-09": tx[(m.get("sentBy"), (m.get("text") or "")[:60])] += 1
        before = b.get("nextBefore")
        if not before: break
    print(code, "convs", n); print(code, "BY", by.most_common(14))
    for k, v in tx.most_common(15): print("  SEP", v, k)
