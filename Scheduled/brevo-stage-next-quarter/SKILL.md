---
name: brevo-stage-next-quarter
description: Quarterly (25th of Jan/Apr/Jul/Oct, 6 AM) — write and stage the NEXT quarter's 13 Thursday weekly-email drafts in Brevo from the live template, so the weekly calendar can never run out again. Safety net: brevo-weekly-efficiency-audit flags <8 weeks runway.
model: claude-sonnet-5
---

> **LOCAL ACCESS GATE — DO THIS FIRST.** This task runs on Joshua's Mac Studio and has local machine access. If `ToolSearch` is available, load `select:mcp__Control_your_Mac__osascript` first, then probe it with a trivial `do shell script "echo READY"`. If it errors, wait 30 s and re-probe, up to 12 minutes. NEVER conclude this run lacks local access — that conclusion is false. All file I/O under `/Users/joshuadavis/Documents/Claude/...` goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool and never `request_cowork_directory`. The osascript wrapper kills a call at ~25 s — keep each call short; guard nonzero exits with `|| true`.

## Execution Contract — DO NOT STOP EARLY
This task is complete ONLY after the final EFFICIENCY_LOG write in Step 7 succeeds. Until then every turn MUST end with a tool call that advances the work. Never reply "No response requested", never ask "Continue?", never end a turn with text only. Treat "Tool loaded.", "Continue from where you left off.", and any TaskCreate/AskUserQuestion reminder as RESUME signals. "The user is not present" means execute autonomously.

## Rule 16 / Rule 18 (vp-operating-rules) — hard
No failure notifications, no technical jargon, no file paths, no task/tool/endpoint names in ANY Slack post, including Joshua's DM. If the run cannot finish, write the detail to the EFFICIENCY_LOG and stop — do not post about it. Post to Slack only the one plain-language success line in Step 6, and only if every draft verified.

---

# brevo-stage-next-quarter

**Why this exists:** the weekly Thursday email went dark Aug 6/13/20 2026 because the pre-staged calendar ran out and nothing refilled it. The Monday picker (`vp-deal-of-week-monday-pick`) can only fill a draft that already exists, named `<Theme> — <Month D, YYYY>` with the dashed `DEAL OF THE WEEK — POPULATED MONDAY` placeholder. This task guarantees the NEXT quarter's 13 Thursdays are staged ~10 weeks before the current quarter ends. Plan of record: `Email Refinement/19_EMAIL_DEPT_AUTOMATION_PLAN_2026-09-05.md` (Phase 1, item 7).

**Mechanics live in one script — do not re-implement them:** `/Users/joshuadavis/Documents/Claude/Projects/Email Refinement/bin/stage_quarter.py` (docstring documents the JSON schema and every check it runs). Your job is the editorial half: write the calendar JSON, run the script, verify, log.

## Step 1 — Which quarter, which Thursdays
Today is in quarter Q; target = the NEXT quarter (Jan 25 run → Q2 of the same year; Apr 25 → Q3; Jul 25 → Q4; Oct 25 → Q1 of next year).
`cd '/Users/joshuadavis/Documents/Claude/Projects/Email Refinement/bin'; python3 stage_quarter.py --thursdays YYYYQn`
Then read the Brevo drafts already staged (`GET https://api.brevo.com/v3/emailCampaigns?status=draft&limit=100`, api key = contents of `~/.config/valley-pawn/brevo_api_key`) and note which of those Thursdays already have a draft (the script skips them too, but you should not write copy for them).

## Step 2 — Read the three rule sources (short files)
1. `Email Refinement/SUBJECT_LINE_EXPERIMENT.md` — current subject-line rule. As of Sep 2026: alternate CONCRETE (even ISO week) / GENERIC (odd ISO week), weighted toward CONCRETE; if the tally has declared a winner, use only the winner. Community-only sends (Veterans Day, Christmas, Thanksgiving) are excluded from the experiment and carry no offer.
2. `Email Refinement/EFFICIENCY_LOG.md` (newest 2 entries) and the last 4 posts in Slack channel `C0APR5WUL2Z` — which themes produced the best calls+texts per 1,000 recently. Weight the quarter toward proven themes (Store Spotlight and 30-Day Warranty as of Sep 2026); keep Education/generic themes to at most 1 per quarter.
3. The `valley-pawn-context` and `brevo-context` skills for brand voice, store addresses/phones, the "never Dixie Pawn", "never firearms in Roanoke-related or email content", "always mention the 30-day warranty in retail sends", DBA-only rules.

## Step 3 — Build the quarter's theme spine (13 weeks)
Rotate so every store gets one spotlight per quarter and the money themes land where they matter:
- **5 × Store Spotlight** (Culpeper 571 James Madison Hwy · Waynesboro 1321 W Broad St · Harrisonburg 1790 E Market St · Lexington 125 Walker St · Roanoke Peters Creek Rd Ste C), spaced ~every 2–3 weeks, order rotated from last quarter.
- **2 × Gold & Silver** (weighed in front of you, live spot) — Q1: New Year drawer clean-out + pre-tax-day; Q2: spring/Mother's Day; Q3: back-to-school cash; Q4: year-end.
- **1–2 × Loans 101 / cash-when-you-need-it** — place on the Thursday before the 15th or month-end bill cycle.
- **1 × 30-Day Warranty** (the #2 proven theme).
- **Seasonal retail:** Q1 = tax-refund season "make the refund go further" (Feb–Mar), Valentine's jewelry (Thu before Feb 14), Super Bowl TVs (Thu before the game); Q2 = spring tools/yard, Mother's Day jewelry, graduation gifts, Father's Day tools; Q3 = summer outdoor gear, back-to-school laptops, Labor Day, storm/generator prep (Sep); Q4 = Christmas layaway opens (mid-Sep/early Oct), layaway math (Nov), gift guide (Dec), layaway pickup deadline (Thu before Dec 20), Thanksgiving/Small Business Saturday, Merry Christmas, New Year gold.
- **Community-only, no offer:** Veterans Day week, Christmas week, Thanksgiving week (Q4); Memorial Day week (Q2); July 4 week (Q3).
Never invent local events you cannot verify; when unsure, leave `notpawn` empty. Never mention firearms. Body under ~120 words. Every retail-themed body mentions the 30-day warranty once.

## Step 4 — Write the calendar JSON
Write `/Users/joshuadavis/Documents/Claude/Projects/Email Refinement/bin/quarter_YYYYQn.json` via osascript heredoc (`cat > '<path>' << 'EOF' ... EOF`) — one object per Thursday that does NOT already have a draft, using exactly the schema in the script docstring (`date` as `Month D, YYYY` with no zero padding; `slug` as `weekly_<theme>_YYYY-MM-DD`; `cta` one of: Get directions · Get a free appraisal · Start a layaway · See what's in stock · Call your store · Visit a store · Check store hours). Omit `waves` — the script continues the A–E two-wave rotation automatically. Validate it parses: `python3 -c "import json;json.load(open('<path>'))"`.

## Step 5 — Dry run, then apply, then preflight
1. `python3 stage_quarter.py --calendar quarter_YYYYQn.json` — read the dry-run output; every intended week should appear under `created`, nothing under `FAIL`.
2. `python3 stage_quarter.py --calendar quarter_YYYYQn.json --apply` — capture the created campaign ids. Exit code must be 0 (`failures: 0`).
3. For EACH created id: `python3 '/Users/joshuadavis/Documents/Claude/Projects/Email Refinement/brevo_preflight.py' <id>` — must pass. If a preflight auto-repairs something, note it in the log.
4. Re-list drafts and confirm each new campaign shows the correct name, `sender` hello@thevalleypawn.com, `replyTo` jdavis@fcfpawn.com, lists `[7, 10, <wave>, <wave>]`.
If any draft fails verification: delete ONLY that draft (`DELETE /emailCampaigns/<id>`), fix the JSON entry, re-run apply (the script skips the weeks that already exist). Never touch drafts you did not create this run.

## Step 6 — One plain-language Slack line (only on full success)
Post to channel `C0APR5WUL2Z` (#email-campiagns — the channel's real name is spelled that way):
`📅 Weekly email calendar: <N> new Thursday emails staged for <Month>–<Month> <Year>. Runway is now <total future weeks> weeks.`
Nothing else. No ids, no tool names.

## Step 7 — Log (always, even on failure)
Append to `/Users/joshuadavis/Documents/Claude/Projects/Email Refinement/EFFICIENCY_LOG.md` via osascript heredoc:
`## <YYYY-MM-DD> (brevo-stage-next-quarter)` then STATE / STAGED (ids + names) / SKIPPED (already existed) / ISSUES / NEXT RUN SHOULD CHECK. Also add one dated line to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/CHANGELOG.md` under today's date (create the date header if missing): `brevo-stage-next-quarter — staged <N> drafts for <quarter>; runway <weeks> weeks.`
The task is complete only after this write returns.