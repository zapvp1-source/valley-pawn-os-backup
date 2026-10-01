#!/usr/bin/env python3
"""parity_check.py <channel_id> <header-prefix> <candidate.txt> — compare a native agent's rendered post
with the most recent real post in the channel that starts with the same header. Prints a line diff after
normalising whitespace. Read-only. Used before switching any report to a native agent (Joshua 9/30:
"make sure the publication formatting is the same")."""
import difflib, json, os, sys, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack
ch, prefix, cand = sys.argv[1], sys.argv[2], open(sys.argv[3]).read()
tok = vp_slack.token()
r = json.load(urllib.request.urlopen(urllib.request.Request("https://slack.com/api/conversations.history?" +
    urllib.parse.urlencode({"channel": ch, "limit": "100"}), headers={"Authorization": "Bearer " + tok}), timeout=30))
live = next((m for m in r.get("messages", []) if (m.get("text") or "").startswith(prefix)), None)
if not live:
    print("no live post starting with %r found" % prefix); sys.exit(1)
a = [l.rstrip() for l in live["text"].replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").splitlines()]
b = [l.rstrip() for l in vp_slack.to_mrkdwn(cand).splitlines()]
d = list(difflib.unified_diff(a, b, "live (%s)" % live.get("ts"), "native", lineterm="", n=0))
print("IDENTICAL" if not d else "\n".join(d[:80]))
print("live by:", live.get("user") or live.get("bot_id"), "| lines live=%d native=%d" % (len(a), len(b)))
