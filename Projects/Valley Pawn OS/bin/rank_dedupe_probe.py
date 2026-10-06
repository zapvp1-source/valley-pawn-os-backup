#!/usr/bin/env python3
"""read-only: why did store_rankings' duplicate guard miss? prints has() and marker matches."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack
m = "Report Period: 2026-10-04 (month-to-date)"
print("has(20h) =", vp_slack.has("C03CGTN3KN1", m, 20))
r = vp_slack.call("conversations.history", params={"channel": "C03CGTN3KN1", "oldest": str(time.time() - 20*3600), "limit": 200})
print("ok", r.get("ok"), "n", len(r.get("messages", [])), r.get("error"))
for x in r.get("messages", []):
    t = x.get("text") or ""
    print(x.get("ts"), x.get("user"), m in t, repr(t[50:110]))
