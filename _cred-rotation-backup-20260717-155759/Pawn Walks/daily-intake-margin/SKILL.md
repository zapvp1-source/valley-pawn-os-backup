---
name: daily-intake-margin
description: Pipeline-driven daily intake margin report for Valley Pawn — fires at 7:30 AM, reads yesterday's Bravo buys-from-public CSVs from the Data Extraction output folder, runs T1/T2/T3 valuation, flags items below 30% margin, and posts a per-store summary to #pawn-walks. Zero computer-use; no Parallels grant required.
---

You are running the Valley Pawn daily intake margin report for Full Circle Finance Inc. The goal: grade yesterday's pawn intake (buys from the public) against independent item-level value estimates, flag overpay risk (items where trusted margin < 30%), and post a per-store summary to #pawn-walks.

**How this task works:** The valuation engine runs natively on the Mac (NOT inside Parallels). Drop a shell command via `mcp__Control_your_Mac__osascript`, read the JSON summary it produces, then handle Slack fallback and alerts. No computer-use. No Parallels grant. No browser.

WARNING: DO NOT use the Write tool to run the script. Use `mcp__Control_your_Mac__osascript` for all host-side execution and file I/O.

WARNING: Always notify Joshua on failure. At any error exit code or missing output, DM Joshua at U03BB52MDSA immediately. Never silently exit.

WARNING — GLOBAL RULE: NEVER post a failure, error, or warning message to ANY Slack channel (including #pawn-walks). Channels receive success summaries only. ALL failure/error notifications go to Joshua by DM (U03BB52MDSA) only.

---

# Step 1 — Determine date

Default: yesterday. Override if this is a manual re-run for a specific date.

```
DATE_STR = (today - 1 day).isoformat()   # e.g. 2026-06-09
LOG_FILE = /tmp/daily_intake_{DATE_STR_no_dashes}.log
SCRIPT   = /Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/run_daily_intake.py
JSON_OUT = /Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/daily/{DATE_STR}_intake_margin_summary.json
```

---

# Step 2 — Run the pipeline script via osascript

Execute via `mcp__Control_your_Mac__osascript`:

```applescript
do shell script "/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/run_daily_intake.py' > /tmp/daily_intake_YYYYMMDD.log 2>&1; echo EXIT:$?"
```

Replace `YYYYMMDD` with the actual date (no dashes). For a specific date re-run, pass the date arg:

```applescript
do shell script "/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/run_daily_intake.py' '2026-06-09' > /tmp/daily_intake_20260609.log 2>&1; echo EXIT:$?"
```

The command returns immediately with something like `EXIT:0` or `EXIT:1` (it's a short-running script — should complete in < 120 seconds with T3 cache hits).

**If EXIT:1 is returned:** read the log (`cat /tmp/daily_intake_YYYYMMDD.log`) via osascript, then go to Error handling. DM Joshua with the last 20 lines.

---

# Step 3 — Read the JSON summary

After EXIT:0, read the summary JSON via osascript:

```applescript
do shell script "cat '/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/daily/{DATE_STR}_intake_margin_summary.json'"
```

Parse the JSON. Key fields:

| Field | Meaning |
|---|---|
| `items` | Total items processed |
| `trusted` | Items with high/medium confidence valuation |
| `flags` | Trusted items with margin < 30% (overpay risk) |
| `avg_margin` | Company-wide avg margin (decimal, e.g. 0.54 = 54%) |
| `stores` | Per-store dict: `{total_items, trusted_items, avg_margin, flags}` |
| `slack_posted` | True if Python script already posted to Slack |
| `slack_skipped` | True if < 3 items (skip is intentional) |
| `slack_error` | `"token_not_found"` or `"post_failed"` if Slack failed |
| `excel_path` | Path to saved .xlsx (null if openpyxl missing) |
| `info` | Present on no-activity days ("No buys-from-public…") |

---

# Step 4 — Slack post (fallback if Python couldn't post)

**If `slack_posted = true`:** Script already posted to #pawn-walks. Skip this step. Proceed to Step 5.

**If `slack_skipped = true` (items < 3 or no-activity day):** No post needed. Proceed to Step 5.

**If `slack_error = "token_not_found"` or `slack_error = "post_failed"`:** The script couldn't post. The JSON summary contains the pre-formatted message in `slack_message` — post that string verbatim using `slack_send_message` to channel `C0B8WR95N31` (#pawn-walks). If `slack_message` is missing/null, build it from the JSON summary using the format below. (This fallback path is the PRIMARY posting method — no bot token exists on the Mac, so `token_not_found` is expected.)

Message format:
```
📋 *Intake Margin — {DATE_STR}*
*{STORE}*: {N} items | Avg margin {X}% | {N} overpay flags
...
Company: {N} items total | Avg {X}% | {N} total flags
```

Skip stores where `total_items = 0`. Skip the post entirely if company `items < 3`.

---

# Step 5 — Flag alert (DM Joshua if flags exist)

If `flags > 0` after a successful run:

DM Joshua at U03BB52MDSA:
```
⚑ Intake flags {DATE_STR}: {N} item(s) below 30% margin across {STORE_LIST}.
Excel detail → {excel_path}
```

If `flags = 0` and run was clean: no DM needed.

---

# Step 6 — No-activity day handling

If JSON contains `"info": "No buys-from-public..."` and `items = 0`:
- This is normal (slow day, weekend, or holiday). No Slack post. No DM.
- Confirm in the task log: "No intake activity for {DATE_STR} — skipping."

---

# Error handling

| Condition | Action |
|---|---|
| EXIT:1 from script | Read log via osascript cat; DM Joshua with last 20 lines. Do NOT post anything to #pawn-walks. |
| JSON not found after EXIT:0 | DM Joshua: "Script exited 0 but JSON not found at {path}" |
| Slack post fails (all methods) | DM Joshua with the full formatted message inline |
| CRITICAL import error (logged) | DM Joshua; do not retry automatically |
| Partial stores only | Post what the JSON has; note in DM which stores are missing |

Never silently exit. On success: post summary to channel. On any failure: DM Joshua only — never the channel.

---

# Reference

- Script: `/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/run_daily_intake.py`
- Output folder: `/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/daily/`
- Bravo CSVs: `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/`
- Slack channel: `C0B8WR95N31` (#pawn-walks, private)
- Joshua DM: `U03BB52MDSA`
- Schedule: 7:30 AM daily
- Python: `/usr/bin/python3` (system Python 3 on host Mac)
- Token: `SLACK_BOT_TOKEN` env var → config JSON → shell profile (script handles all fallbacks)
- No Parallels. No computer-use. No browser.

# Background

Built 2026-06-10. Part of the Valley Pawn Intake Margin Reporting project.
Pipeline: T1 melt (precious metals) → T2 COMP (internal sold history, model-token match) → T3 external (eBay Browse for general merch; DuckDuckGo gun-value sites for firearms).
Flag threshold: trusted margin < 30%. Target margin: 50%.
Additive only — does not modify any existing Bravo reports, handlers, or pipeline cells.
