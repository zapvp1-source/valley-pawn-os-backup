#!/usr/bin/env python3
"""canvas_access_probe.py — READ-ONLY diagnosis of canvases.edit restricted_action (2026-10-14).

For each live weekly canvas: files.info (owner, channel linkage, access fields), canvases.sections.lookup
(read path), and for every channel the canvas is attached to: conversations.info (is_member, posting
restrictions where visible) and whether the bot has recent messages there. Also auth.test + token scopes.
Never calls an edit/set/post method. Prints JSON-ish lines for a human to read.
"""
import json, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack

CANVASES = {"loan": "F0BH6BJ0PK7", "layaway": "F0BJ48BMZGQ", "employee": "F0BH9UK284S",
            "aged": "F0BHDL6AULU", "store": "F0BH6S9U5FX"}
SKIP = {"preview", "preview_highlight", "preview_plain_text", "lines", "lines_more", "title_blocks", "blocks"}


def scopes():
    req = urllib.request.Request("https://slack.com/api/auth.test",
                                 headers={"Authorization": "Bearer " + vp_slack.token()})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.headers.get("x-oauth-scopes"), json.load(r)


sc, at = scopes()
print("auth.test:", json.dumps({k: at.get(k) for k in ("ok", "user", "user_id", "bot_id", "team", "team_id", "error")}))
print("scopes:", sc)
chans = set()
for kind, cid in CANVASES.items():
    print("\n==========", kind, cid)
    fi = vp_slack.call("files.info", params={"file": cid})
    if not fi.get("ok"):
        print("files.info error:", fi.get("error"), fi.get("needed"))
    else:
        f = fi.get("file", {})
        slim = {k: v for k, v in f.items() if k not in SKIP and not k.startswith("thumb")}
        print("files.info:", json.dumps(slim, default=str)[:4000])
        for k in ("channels", "groups", "ims"):
            chans.update(f.get(k) or [])
        for k in ("linked_channel_id", "canvas_channel_id"):
            if f.get(k):
                chans.add(f[k])
    lk = vp_slack.call("canvases.sections.lookup", {"canvas_id": cid, "criteria": {"section_types": ["any_header"]}})
    print("sections.lookup: ok=%s error=%s n=%s" % (lk.get("ok"), lk.get("error"), len(lk.get("sections") or [])))
chans.add("C04N24STDP1")
for ch in sorted(chans):
    print("\n----- channel", ch)
    ci = vp_slack.call("conversations.info", params={"channel": ch})
    if ci.get("ok"):
        c = ci["channel"]
        keep = ("name", "is_member", "is_archived", "is_private", "is_general", "is_read_only", "is_thread_only",
                "is_ext_shared", "is_org_shared", "creator", "properties", "posting_restricted_to",
                "threads_restricted_to", "canvas", "tabs", "meeting_notes")
        print("conversations.info:", json.dumps({k: c.get(k) for k in keep if k in c}, default=str)[:4000])
    else:
        print("conversations.info error:", ci.get("error"), ci.get("needed"))
    h = vp_slack.call("conversations.history", params={"channel": ch, "limit": 15})
    if h.get("ok"):
        mine = [m for m in h.get("messages", []) if m.get("bot_id") == at.get("bot_id")]
        print("history ok; last bot msg ts:", mine[0].get("ts") if mine else None, "of", len(h.get("messages", [])))
    else:
        print("history error:", h.get("error"))
print("\nexit=0")
