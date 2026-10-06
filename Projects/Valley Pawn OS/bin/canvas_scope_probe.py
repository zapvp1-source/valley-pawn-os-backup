#!/usr/bin/env python3
"""canvas_scope_probe.py — read-only: can the ops bot token read/update Slack canvases? Prints the token's
scopes and the result of canvases.sections.lookup on each weekly canvas. Never writes anything."""
import json, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack
tok = vp_slack.token()
req = urllib.request.Request("https://slack.com/api/auth.test", headers={"Authorization": "Bearer " + tok})
with urllib.request.urlopen(req, timeout=20) as r:
    print("scopes:", r.headers.get("x-oauth-scopes"))
for cid in ("F0BH6BJ0PK7", "F0BJ48BMZGQ", "F0BH9UK284S", "F0BHDL6AULU", "F0BH6S9U5FX"):
    r = vp_slack.call("canvases.sections.lookup", {"canvas_id": cid, "criteria": {"section_types": ["any_header"]}})
    print(cid, "ok=%s error=%s needed=%s" % (r.get("ok"), r.get("error"), r.get("needed")))
