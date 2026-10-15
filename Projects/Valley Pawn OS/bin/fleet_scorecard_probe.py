#!/usr/bin/env python3
"""fleet_scorecard_probe.py — READ-ONLY Slack dump used to build/verify the daily fleet scorecard
coverage (2026-10-14). Lists every channel the vp_ops bot (Goldilocks) is a member of, plus the
bot<->Joshua DM, and writes every message from the last N days (default 9) — ts, channel, author,
subtype, first 160 chars of text, and the plain text of any table/section blocks' first line — to
fleet/state/fleet_scorecard_probe.json. Posts nothing.

    fleet_scorecard_probe.py [days]
"""
import json, os, sys, time, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack

OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
OUT = os.path.join(OS_DIR, "fleet/state/fleet_scorecard_probe.json")
days = float(sys.argv[1]) if len(sys.argv) > 1 else 9
oldest = time.time() - days * 86400

chans = {}
cursor = None
err = None
for _ in range(20):
    p = {"types": "public_channel,private_channel", "limit": 200, "exclude_archived": "true"}
    if cursor:
        p["cursor"] = cursor
    r = vp_slack.call("users.conversations", params=p)
    if not r.get("ok"):
        err = r.get("error")
        break
    for c in r.get("channels", []):
        chans[c["id"]] = c.get("name", "")
    cursor = (r.get("response_metadata") or {}).get("next_cursor")
    if not cursor:
        break
man = json.load(open(os.path.join(OS_DIR, "fleet/expected_outputs.json")))
for e in man.get("entries", []):
    ch = e.get("channel_id") or ""
    if ch.startswith("C") and ch not in chans:
        chans[ch] = "(manifest) " + e.get("output", "")
try:
    dm = vp_slack.dm_channel(vp_slack.JOSHUA)
    chans[dm] = "DM-joshua-goldilocks"
except SystemExit as e:
    dm = None

out = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "list_error": err, "channels": chans, "messages": []}
for ch, name in chans.items():
    cur = None
    for _ in range(10):
        p = {"channel": ch, "oldest": str(oldest), "limit": 200}
        if cur:
            p["cursor"] = cur
        try:
            r = vp_slack.call("conversations.history", params=p)
        except Exception as e:
            out["messages"].append({"ch": ch, "err": str(e)})
            break
        if not r.get("ok"):
            out["messages"].append({"ch": ch, "name": name, "err": r.get("error")})
            break
        for m in r.get("messages", []):
            out["messages"].append({"ch": ch, "name": name, "ts": m.get("ts"),
                                    "who": m.get("user") or m.get("bot_id") or m.get("username"),
                                    "bot": bool(m.get("bot_id")), "sub": m.get("subtype"),
                                    "t": (m.get("text") or "")[:160].replace("\n", " / "),
                                    "rc": m.get("reply_count", 0)})
        cur = (r.get("response_metadata") or {}).get("next_cursor")
        if not r.get("has_more") or not cur:
            break
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT + ".tmp", "w"), indent=0)
os.replace(OUT + ".tmp", OUT)
print("channels=%d messages=%d list_error=%s dm=%s" % (len(chans), len(out["messages"]), err, dm))
