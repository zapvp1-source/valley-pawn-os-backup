#!/usr/bin/env python3
"""Full rollback of the 2026-11-09 Slack Restructure (Joshua: 'put everything back').
Deletes the bot's own 'moved to' pointer posts, the department canvases + self-test canvas, and the
self-test posts in #vp-ops-shadow. Bot deletes only what it created."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack
OS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
st = json.load(open(os.path.join(OS, "fleet/state/slack_restructure.json")))
for ch, info in st.get("pointers", {}).items():
    r = vp_slack.call("chat.delete", {"channel": ch, "ts": info["ts"]}); print("pointer", ch, r.get("ok"), r.get("error"))
cv = json.load(open(os.path.join(OS, "fleet/canvas_state/dept_canvases.json")))
for k, v in cv.items():
    r = vp_slack.call("canvases.delete", {"canvas_id": v["id"]}); print("canvas", k, r.get("ok"), r.get("error"))
for ts in ["1794245928.538269", "1794245928.884659", "1794245929.672689", "1794249490.073799", "1794249490.505969", "1794249491.914169"]:
    r = vp_slack.call("chat.delete", {"channel": "C0BLQSABGGY", "ts": ts}); print("selftest", ts, r.get("ok"), r.get("error"))
os.rename(os.path.join(OS, "fleet/canvas_state/dept_canvases.json"), os.path.join(OS, "fleet/canvas_state/dept_canvases.rolledback-20261109.json"))
st["rolled_back"] = "2026-11-09"; json.dump(st, open(os.path.join(OS, "fleet/state/slack_restructure.json"), "w"), indent=1)
print("rollback done")
