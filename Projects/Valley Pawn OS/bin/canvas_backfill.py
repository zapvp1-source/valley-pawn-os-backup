#!/usr/bin/env python3
"""canvas_backfill.py — fill each department canvas now with the latest real report from every channel that
feeds it (2026-11-09 Slack Restructure), so the canvases are useful before the next scheduled run.
One section per source report, keyed by the report's own title line. Skips the 'moved to' pointer posts."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack, vp_canvas_section as vc
OS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
routes = json.load(open(os.path.join(OS, "fleet/slack_routes.json")))["rules"]
DEPT_OF = {"C03CGTN3KN1": "scoreboard", "C04N24STDP1": "loans", "C04NGH4FF35": "aged", "C0BMRC2LN3D": "marketing", "C0B26GD8D2R": "leadership", "C0B3R9B3S8H": "daily"}
sources = {d: [(c, None)] for c, d in DEPT_OF.items()}
for r in routes:
    if r.get("action") == "redirect":
        sources[DEPT_OF[r["to"]]].append((r["channel"], r["channel_name"]))
SKIP = ("moved to <#", "has joined the channel", "Route self-test")
def title(t):
    first = next((l for l in t.splitlines() if l.strip()), "Report")
    first = re.sub(r":[a-z0-9_+-]+:", "", first); first = re.sub(r"[*_`]", "", first)
    first = re.sub(r"<[^|>]+\|([^>]+)>", r"\1", first).strip(" —-|")
    return re.split(r" — | \| ", first)[0][:70] or "Report"
for dept, chans in sources.items():
    for ch, name in chans:
        r = vp_slack.call("conversations.history", params={"channel": ch, "limit": 40})
        if not r.get("ok"):
            print(dept, name or ch, "read failed", r.get("error")); continue
        seen = set()
        for m in r.get("messages", []):
            t = (m.get("text") or "").strip()
            if not t or any(s in t for s in SKIP) or m.get("subtype") in ("channel_join", "channel_purpose", "channel_topic"):
                continue
            if not (m.get("bot_id") or "Sent using" in t):   # automated reports only
                continue
            key = title(t)
            if key in seen: continue
            seen.add(key)
            if len(seen) > 3: break                          # latest 3 distinct reports per source
            try:
                vc.write({"canvas": dept, "section_key": key}, t.replace("*Sent using* Claude", "").strip())
                print(dept, "<-", name or "(own)", "|", key)
            except Exception as e:
                print(dept, "write failed", key, e)
print("backfill done")
