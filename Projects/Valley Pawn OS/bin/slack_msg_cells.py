#!/usr/bin/env python3
"""slack_msg_cells.py <channel> <ts> — read-only: print one message's table block as plain cell rows
(rich_text styles shown as *bold* / _italic_), so a native port can copy a past post's table exactly."""
import json, os, sys, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack
r = vp_slack.call("conversations.history", params={"channel": sys.argv[1], "latest": sys.argv[2], "oldest": sys.argv[2], "inclusive": "true", "limit": 1})
for m in r.get("messages", []):
    for b in m.get("blocks") or []:
        if b.get("type") != "table":
            print("BLOCK", b.get("type")); continue
        for row in b["rows"]:
            out = []
            for c in row:
                t = ""
                for el in c.get("elements", []):
                    for e in el.get("elements", []):
                        s = e.get("text", "")
                        st = e.get("style") or {}
                        if st.get("bold"): s = "*" + s + "*"
                        if st.get("italic"): s = "_" + s + "_"
                        t += s
                out.append(t)
            print(" | ".join(out))
