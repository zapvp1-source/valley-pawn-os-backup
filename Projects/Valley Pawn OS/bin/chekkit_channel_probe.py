#!/usr/bin/env python3
"""chekkit_channel_probe.py — READ-ONLY (2026-10-21). Which channels do Chekkit conversations carry per store
(SMS only, or Facebook Messenger too)? Prints counts + one sample's keys/channel fields per store."""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_api as ck
for code in ("CUL", "WAY", "HAR", "LEX", "ROA"):
    try:
        cs = (ck.get(code, "/v1/conversations?limit=50") or {}).get("conversations") or []
        keys = set(); ch = collections.Counter()
        for c in cs:
            keys |= set(c.keys())
            ch[str(c.get("channel") or c.get("channelType") or c.get("type") or c.get("source") or c.get("medium") or "?")] += 1
        print(code, "convs", len(cs), dict(ch))
        if cs:
            s = cs[0]
            print("  keys:", sorted(keys))
            print("  sample:", json.dumps({k: s[k] for k in s if k not in ("contact", "lastMessage")}, default=str)[:500])
            ms = ck.messages(code, s["id"])
            if ms:
                print("  msg keys:", sorted(ms[0].keys()), "| channel:", ms[0].get("channel") or ms[0].get("type"))
    except Exception as e:
        print(code, "ERR", e)
