---
name: jewelry-onhand-nightly-compare
description: Nightly 9:45 PM (Mon-Sat) — compare the freeze-window Bravo jewelry counts against the same night's manager PM sheets, flag real variances, DM Joshua, and track day-over-day trend.
model: claude-sonnet-5
---

Part 2 of 2 of Valley Pawn's nightly jewelry count reconciliation. `jewelry-onhand-nightly-pull` ran at 8:30 PM and pulled 5-store jewelry on-hand counts from Bravo inside the after-close freeze window. Your job is the analysis.

═══ RULE 0 — NEVER REQUEST FOLDER ACCESS. THIS KILLED THE FIRST TWO RUNS. ═══
Do NOT call `mcp__cowork__request_cowork_directory` under any circumstances, and do not use the Read/Write/Edit tools for anything under /Users/joshuadavis/Documents/. That tool opens an interactive approval prompt. You run unattended at 9:45 PM with nobody at the keyboard, so it times out and the whole run aborts having done nothing. That is exactly what happened on 2026-08-10: both nightly tasks fired on time, sat on a folder-permission prompt ~30 minutes, then died silently.

Reach EVERY file — read or write, any path, including the STATUS.md in the Jewelry Count Reconciliation project folder — through `mcp__Control_your_Mac__osascript` shell commands (cat, ls, printf, python3). That is how the other unattended tasks do all file work and it never prompts. If a path seems unreachable, the answer is another osascript command, never a folder request.

osascript quirks: the wrapper dies after ~25s, so never chain sleeps longer than ~18s in one call; and a command whose last stage exits non-zero (grep with no match) makes the call throw — append `|| true`.

WHY THIS IS VALID (and what made earlier versions invalid):
Bravo's jewelry report is a live on-hand query with no as-of-date capability. The manager's sheet is a physical count at 6 PM close. They only line up when Bravo is queried while nothing is moving. All stores close 6 PM / reopen 10 AM, so tonight's 8:30 PM pull and tonight's 6 PM count describe the SAME frozen state. Any comparison mixing periods — a mid-morning pull against a prior day's sheet — is uninterpretable noise. Confirm both sides come from the same freeze window before drawing any conclusion.

STORE-CLOSURE NUANCE — critical for judging completeness:
- Culpeper: open Mon-Sat.
- Harrisonburg, Waynesboro, Lexington, Roanoke: open Mon, Tue, Thu, Fri, Sat — CLOSED WEDNESDAY.
On a Wednesday run only Culpeper has a new sheet; that is expected, not a failure. For the four closed stores on Wednesday, compare tonight's Bravo count against their most recent (Tuesday) sheet — inside a continuous closed period nothing moved, so those should match essentially exactly. Drift there is a genuine red flag, since no legitimate transaction could explain it.

STEP 1 — Load the Bravo side (osascript).
Read output/<YYYY-MM-DD>_<STORE>_jewelry-case-counts.csv for CUL, HAR, LEX, ROA, WAY under /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/.
Verify each file's mtime is TONIGHT after 8:30 PM — an older file is stale data from a previous run, not tonight's freeze-window pull. Verify every row has status=ok.

HARD RULE — never publish partial, stale, or unverified data. If any store is missing, stale, or has a non-ok row, do NOT compare and do NOT publish numbers. DM Joshua one plain line saying tonight's count didn't complete, and stop. All-or-nothing.

STEP 2 — Load the manager side (Chrome).
Tonight's PM sheets are in Slack #end-of-day (channel C03C7HV8L48), posted roughly 6:15-8:15 PM. Typical posters: Sandi=Culpeper, Walker=Harrisonburg, Martin D.=Lexington, Benjie=Roanoke, Preston/Chadd=Waynesboro — confirm from each sheet's printed header rather than assuming.

These sheets are PHOTOGRAPHS. Slack's API cannot read image pixels — use the Claude-in-Chrome browser tools and read them visually. Go to https://app.slack.com/client/T03BL4W1DCL/C03C7HV8L48 and zoom into each "JEWELRY DAILY COUNT" image. Use the PM COUNT column. Confirm the handwritten DATE matches today — it sometimes differs from the Slack post date, and sheets often stack several days on one page, so read the right block. Sanity-check each sheet's own TOTALS line against the sum of its categories; if they disagree you misread a digit — re-zoom before trusting it.

STEP 3 — Compare, with the correct category mapping.
Sheet has 5 lines: RINGS, BRACELETS, NECKLACES, EARRINGS, PENDANTS. Bravo reports 6 categories:
- Rings → RINGS, Bracelets → BRACELETS, Earrings → EARRINGS, Pendants → PENDANTS
- **Chains + Necklaces summed → NECKLACES** (Bravo splits what the sheet counts as one line; confirmed 2026-08-09)
Build a per-store table: category, Bravo count, sheet count, variance, plus store totals.

STEP 4 — Analyze, don't just tabulate.
Inside a true freeze window a healthy process should be at or very near zero variance. Deltas of 1-3 are ordinary. Larger gaps are real exceptions — name the store, category, and size.

Compare against prior nights' RUN RECORDs in the STATUS file to spot patterns: a variance repeating in the same store/category night after night is a process or data problem; a one-night spike is more likely a miscount. Say which you're seeing. Watch ROANOKE PENDANTS specifically — an earlier time-mismatched comparison suggested a large gap there, but that comparison was invalid; freeze-window runs are the first trustworthy read on whether anything is actually wrong at that store.

Do not overstate confidence. If a number looks impossible (a category swinging by hundreds overnight), treat it as a suspect read rather than a business event, and say so.

STEP 5 — Report to Joshua only.
Send ONE Slack DM (channel D03BHQH5VGT). This is a loss-prevention audit — never a shared channel, never a store manager or employee. Plain everyday language: no jargon, no file paths, no system or tool names. Lead with the bottom line — did tonight's counts match, and what looks off. Short enough to read on a phone; on a clean night a couple of lines is enough.

STEP 6 — Log it (osascript append, not the Edit tool).
Append a dated RUN RECORD to /Users/joshuadavis/Documents/Claude/Projects/Jewelry Count Reconciliation/STATUS.md with the full per-store table, which freeze window both sides came from, and your read on any exception. This builds the night-over-night history the trend analysis depends on.

NOTE ON THE OLDER TASK: a separate live task, `jewelry-count-reconciliation` (7:47 PM daily), still runs the older sold-based flow comparison. Leave it completely alone — additive-only rule. Once this on-hand method has a solid multi-night record, Joshua can retire the older one.

Failure policy: if this run fails or cannot complete, send Joshua exactly ONE plain-language Slack DM saying tonight's jewelry comparison did not complete. No technical detail in the DM; put it in your run output.