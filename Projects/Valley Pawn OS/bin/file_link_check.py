#!/usr/bin/env python3
"""file_link_check.py (2026-11-14) — read-only self-test for vp_slack.permalink(): finds the newest files the
ops bot sent to Joshua's DM and prints the link each would get. Posts nothing, uploads nothing."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack as v
ch = v.dm_channel(v.JOSHUA)
r = v.call("conversations.history", params={"channel": ch, "limit": 40})
print("history ok:", r.get("ok"), r.get("error", ""))
n = 0
for m in r.get("messages", []):
    for f in m.get("files") or []:
        print("FILE", f.get("id"), f.get("name"), "| msg-permalink:", f.get("permalink"))
        print("  computed:", v.permalink(f.get("id"), f.get("name") or ""))
        n += 1
    if n >= 3: break
fl = v.call("files.list", params={"count": 3, "types": "spreadsheets"})
print("files.list:", fl.get("ok"), fl.get("error", ""))
for f in fl.get("files") or []:
    print("LIST", f.get("id"), f.get("name"), "->", v.permalink(f.get("id"), f.get("name") or ""))
fi = v.call("files.info", params={"file": "F000"})
print("files.info scope probe:", fi.get("error"), fi.get("needed", ""))
a = v.call("auth.test", payload={})
print("auth.test:", a.get("ok"), a.get("url"), a.get("user_id"))
