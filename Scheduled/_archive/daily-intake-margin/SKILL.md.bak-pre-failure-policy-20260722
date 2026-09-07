---
name: daily-intake-margin
description: Pipeline-driven daily intake margin report — reads yesterday's Bravo buys CSVs, runs T1/T2/T3 valuation, flags overpay risk, posts per-store summary to #pawn-walks. 7:30 AM daily. No computer-use.
model: claude-sonnet-5
---


You are running the Valley Pawn daily intake margin report for Full Circle Finance Inc. The goal: grade yesterday's pawn intake (loans + buys from the public) against independent item-level value estimates, flag overpay risk (items where trusted margin < 30%), and post a per-store summary to #pawn-walks.

**How this task works:** The valuation engine runs natively on the Mac (NOT inside Parallels). Run a shell command via mcp__Control_your_Mac__osascript, read the JSON summary it produces, then handle Slack fallback and alerts. No computer-use. No Parallels grant. No browser.

WARNING: DO NOT use the Write tool to run the script. Use mcp__Control_your_Mac__osascript for all host-side execution and file I/O.
WARNING: Always notify Joshua on failure. At any error exit code or missing output, DM Joshua at U03BB52MDSA immediately. Never silently exit.
WARNING — GLOBAL RULE: NEVER post a failure, error, or warning message to ANY Slack channel (including #pawn-walks). Channels receive success summaries only. ALL failure/error notifications go to Joshua by DM (U03BB52MDSA) only.

---

# Step 1 — Determine date

Use yesterday's date. Format: YYYY-MM-DD (e.g. 2026-06-09).
LOG_FILE = /tmp/daily_intake_YYYYMMDD.log  (no dashes in filename)
SCRIPT   = /Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/run_daily_intake.py
JSON_OUT = /Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/daily/{DATE}_intake_margin_summary.json

---

# Step 2 — Run the pipeline script via osascript

Execute via mcp__Control_your_Mac__osascript:

```
do shell script "/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/run_daily_intake.py' > /tmp/daily_intake_YYYYMMDD.log 2>&1; echo EXIT:$?"
```

Replace YYYYMMDD with the actual date digits (no dashes).

The osascript call returns EXIT:0 (success) or EXIT:1 (error) immediately. The script completes in under 120 seconds.

If EXIT:1: Read log via osascript `do shell script "tail -20 '/tmp/daily_intake_YYYYMMDD.log'"` then go to Error handling. DM Joshua with the last 20 lines. Do NOT post anything to the channel.

---

# Step 3 — Read the JSON summary

After EXIT:0, read the summary JSON via osascript:

```
do shell script "cat '/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/daily/{DATE}_intake_margin_summary.json'"
```

Key fields to check:
- items: total items processed
- trusted: items with high/medium confidence valuation
- flags: trusted items with margin < 30% (overpay risk)
- avg_margin: company-wide avg margin (decimal, 0.54 = 54%)
- stores: per-store dict {total_items, trusted_items, avg_margin, flags}
- slack_posted: true if Python script already posted to Slack
- slack_skipped: true if fewer than 3 items (intentional skip)
- slack_error: "token_not_found" or "post_failed" if Slack failed
- slack_message: pre-formatted Slack message string (post this verbatim in Step 4)
- excel_path: path to saved .xlsx
- info: present on no-activity days

---

# Step 4 — Slack post (PRIMARY path — script has no token)

If slack_posted = true: Script already posted. Skip this step.

If slack_skipped = true AND slack_message is null (items < 3 or no-activity day): No post needed. Proceed to Step 5.

If slack_error = "token_not_found" or "post_failed": EXPECTED — no bot token exists on the Mac. Post the `slack_message` string from the JSON VERBATIM via slack_send_message to channel C0B8WR95N31 (#pawn-walks). If slack_message is missing/null, build it from the JSON:

📋 *Intake Margin — {DATE}*
*{STORE}*: {N} items | Avg margin {X}% | {N} overpay flags
...
Company: {N} items total | Avg {X}% | {N} total flags

Skip stores where total_items = 0. Skip post entirely if company items < 3.

---

# Step 5 — Flag alert (DM Joshua if flags exist)

If flags > 0 after a successful run:
DM Joshua at U03BB52MDSA:
"⚑ Intake flags {DATE}: {N} item(s) below 30% margin across {STORE_LIST}.
Excel detail → {excel_path}"

If flags = 0 and run was clean: no DM needed.

---

# Step 6 — No-activity day

If JSON contains info field like "No buys-from-public..." and items = 0:
This is normal (slow day, weekend, holiday). No Slack post. No DM. Log internally.

---

# Error handling — DM ONLY, never channel

- EXIT:1 from script: Read log via osascript; DM Joshua with last 20 lines. NEVER post failure to #pawn-walks or any channel.
- JSON not found after EXIT:0: DM Joshua "Script exited 0 but JSON not found at {path}"
- Slack post fails all methods: DM Joshua with the full formatted message inline
- Never silently exit. On success: post summary to channel. On any failure: DM Joshua only — never the channel.

---

# Reference

- Script: /Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/run_daily_intake.py
- Output folder: /Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/daily/
- Bravo CSVs: /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/
- Slack channel: C0B8WR95N31 (#pawn-walks, private) — SUCCESS summaries only
- Joshua DM: U03BB52MDSA — ALL failure notifications
- Python: /usr/bin/python3 (system Python 3 on host Mac)
- No Parallels. No computer-use. No browser.
- Script saves slack_message into the JSON; the MCP post in Step 4 is the primary posting path.

<!-- migrated to working model 2026-06-15 -->