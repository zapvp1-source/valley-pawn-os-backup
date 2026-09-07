#!/usr/bin/env python3
"""Add the Brevo email lane to Fleet Guardian's output-verification manifest.
Email Dept plan 2026-09-05 (file 19), Phase 0 item 5. Additive-only; backs up first."""
import json, os, shutil

P = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS/fleet/expected_outputs.json")
B = P + ".bak-pre-20260905-emaildept"
if not os.path.exists(B):
    shutil.copy2(P, B)

d = json.load(open(P))
have = {e["task"] for e in d["entries"]}

new = [
    {"task": "brevo-weekly-efficiency-audit", "output": "slack:#email-campiagns",
     "channel_id": "C0APR5WUL2Z", "marker": "Email channel efficiency",
     "cadence": "weekly-friday-0800et", "grace_hours": 5,
     "_added": "2026-09-05 Email Dept review (plan file 19, Phase 0 item 5) — marker verified against the real 2026-08-28 and 2026-09-04 posts in C0APR5WUL2Z"},
    {"task": "brevo-preflight-watchdog", "output": "slack:#email-campiagns",
     "channel_id": "C0APR5WUL2Z", "marker": "Email watchdog:",
     "cadence": "daily-0700et", "grace_hours": 6,
     "_added": "2026-09-05 Email Dept review — marker verified against the real 8/28, 8/31, 9/1, 9/3, 9/4 and 9/5 posts. This is the guard that stops an untracked campaign from sending, so its silence matters."},
    {"task": "monthly-we-buy-gold-silver-email", "output": "slack:#email-campiagns",
     "channel_id": "C0APR5WUL2Z", "marker": "Monthly Gold & Silver Campaign Launched",
     "cadence": "monthly-day1-0900et", "grace_hours": 8,
     "_added": "2026-09-05 Email Dept review — marker verified against the real 2026-09-01 post. NOTE: cron corrected 2026-09-05 from '15 2 1 * *' (the send was landing ~2:20 AM) to '0 9 1 * *'; first 9 AM send is 2026-10-01."},
    {"task": "brevo-stage-next-quarter", "output": "slack:#email-campiagns",
     "channel_id": "C0APR5WUL2Z", "marker": "Weekly email calendar:",
     "cadence": "quarterly-day25-0600et", "grace_hours": 12,
     "_added": "2026-09-05 Email Dept review (plan file 19, Phase 1 item 7) — NEW task, first run 2026-10-25. Marker is the exact Step 6 line in its SKILL.md. It has no successful post yet, so treat absence before 2026-10-25 as unverified, NOT as a miss."},
]

added = [e for e in new if e["task"] not in have]
d["entries"].extend(added)
d["_readme"].append(
    "2026-09-05 Email Dept review: +4 entries covering the Brevo email lane (Friday efficiency audit, "
    "daily preflight watchdog, monthly gold send, new quarterly calendar stager). The weekly Thursday "
    "send is already covered by the vp-deal-of-week-monday-pick entry plus vp-thursday-email-watchdog. "
    "Plan of record: Email Refinement/19_EMAIL_DEPT_AUTOMATION_PLAN_2026-09-05.md."
)
json.dump(d, open(P, "w"), indent=1, ensure_ascii=False)
print("added:", [e["task"] for e in added], "| total entries", len(d["entries"]))
