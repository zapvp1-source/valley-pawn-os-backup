#!/usr/bin/env python3
"""slack_msg_raw.py <channel> <ts> — print one message's raw text + block structure (read-only)."""
import json, os, sys, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack
tok = vp_slack.token(); ch, ts = sys.argv[1], sys.argv[2]
r = json.load(urllib.request.urlopen(urllib.request.Request("https://slack.com/api/conversations.history?" + urllib.parse.urlencode(
    {"channel": ch, "latest": ts, "oldest": ts, "inclusive": "true", "limit": "1"}), headers={"Authorization": "Bearer " + tok}), timeout=30))
if not r.get("messages") and len(sys.argv) > 3:   # a thread reply: conversations.replies on the parent
    r = json.load(urllib.request.urlopen(urllib.request.Request("https://slack.com/api/conversations.replies?" + urllib.parse.urlencode(
        {"channel": ch, "ts": sys.argv[3], "limit": "20"}), headers={"Authorization": "Bearer " + tok}), timeout=30))
    r["messages"] = [m for m in r.get("messages", []) if m.get("ts") == ts]
for m in r.get("messages", []):
    print("TEXT:", json.dumps(m.get("text"))[:1500])
    print("BLOCKS:", json.dumps(m.get("blocks"))[:3000])
