#!/usr/bin/env python3
"""chekkit_text_sample.py — READ-ONLY (2026-10-23). Samples recent messages per store to label message kinds for the
census: prints sentBy counts for business rows and 40 distinct event texts. GET only."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_api as ck
for code in ("CUL", "WAY"):
    b = ck.get(code, "/v1/conversations?limit=50") or {}
    by = collections.Counter(); ev = collections.Counter(); ch = collections.Counter()
    for c in b.get("conversations") or []:
        for m in (ck.get(code, "/v1/conversations/%s/messages?limit=500" % c.get("id")) or {}).get("messages") or []:
            ch[(m.get("sender"), str(m.get("channel")), str(m.get("type")))] += 1
            if m.get("sender") == "business": by[m.get("sentBy")] += 1
            if m.get("sender") == "event": ev[(m.get("text") or "")[:90]] += 1
    print(code, "CHANNELS", ch.most_common(12)); print(code, "SENTBY", by.most_common(12))
    for t, n in ev.most_common(25): print("  EV", n, repr(t))
