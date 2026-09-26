#!/usr/bin/env python3
"""bot_channel_check.py [channel_id ...] — can the ops bot post to each channel? Read-only.
With no args, checks every slack: channel in fleet/expected_outputs.json whose task is enabled-or-native.
For public channels the bot is not in, tries conversations.join (harmless, public only) and reports.
Private channels need a human /invite @vp_ops_engine — printed as NEEDS INVITE."""
import json, os, sys, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack
tok = vp_slack.token()
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
ids = sys.argv[1:]
if not ids:
    m = json.load(open(os.path.join(OS_DIR, "fleet/expected_outputs.json")))["entries"]
    ids = sorted({e["channel_id"] for e in m if str(e.get("output","")).startswith("slack:") and e.get("channel_id")})
def call(method, **kw):
    req = urllib.request.Request("https://slack.com/api/%s" % method, data=urllib.parse.urlencode(kw).encode(),
                                 headers={"Authorization": "Bearer " + tok})
    return json.load(urllib.request.urlopen(req, timeout=20))
need = []
for ch in ids:
    # the bot has no channels:read scope (conversations.info -> missing_scope); history is the probe
    r = call("conversations.history", channel=ch, limit="1")
    if r.get("ok"):
        print("%s  member" % ch); continue
    err = r.get("error")
    if err == "not_in_channel":
        j = call("conversations.join", channel=ch)
        if j.get("ok"):
            print("%s  joined (was public, not a member)" % ch); continue
        print("%s  NEEDS INVITE (%s; join: %s)" % (ch, err, j.get("error"))); need.append(ch); continue
    print("%s  %s" % (ch, err)); need.append(ch)
print("SUMMARY needs_invite=%d" % len(need))
