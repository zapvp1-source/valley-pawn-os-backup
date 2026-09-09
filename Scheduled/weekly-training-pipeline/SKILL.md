---
name: weekly-training-pipeline
description: Reads last week's customer calls (HAR/WAY/LEX), produces the four training packs (store coaching, teachable-call library, policy queue, inventory want-list) plus the scoreboard, and — for this test week — DMs everything to Joshua instead of managers/Preston/#call-insights.
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

You are running the Valley Pawn weekly call-training pipeline. This is a fresh session with no memory of prior conversations — everything you need is below or on disk at the paths given.

## DISTRIBUTION MODE: TEST — read this first
This task is in a one-week trial. **Every output this run goes ONLY to Joshua Davis via Slack DM** (Slack user_id `U03BB52MDSA`, via the Slack MCP tool whose `slack_search_users` description confirms `U03BB52MDSA` is the logged-in user — that is Joshua). Do **not** post to any store manager, Preston Peters, `#call-insights`, or any other channel this run, even though the permanent design (see the plan doc below) eventually routes packs to those people. Do not push any policy draft into Gusto e-signature, do not post a public "Call of the Week," do not share the library folder — those are LIVE-mode actions only. At the end of your DM to Joshua, ask him to confirm the packs look right before you switch to live distribution next week. If a future edit to this task changes "DISTRIBUTION MODE: TEST" to "DISTRIBUTION MODE: LIVE," follow the live routing in the plan doc instead of this paragraph.

## Background — read before doing anything
Read these two files in full first:
- `/Users/joshuadavis/Documents/Claude/Projects/Call Analysis/TRAINING_PROGRAM_PLAN.md` — the design: the weekly cycle, the reading rubric, the four packs, the scoreboard, who gets what in LIVE mode.
- `/Users/joshuadavis/Documents/Claude/Projects/Call Analysis/FINDINGS_v2_2026-08-31_week.md` — last week's fully-corrected findings, so you know the baseline numbers and the format that worked.

Also load the `enterprise-map` and `valley-pawn-context` skills for company context, and `vp-operating-rules` for the standing rules (no individual employee data to any shared/public channel — Joshua's own DM is fine; withhold rather than caveat if data is incomplete; fix-forward; no failure jargon).

## Step 1 — Define the review window
Previous Monday through Sunday, relative to today. Stores in scope: Harrisonburg (HAR), Waynesboro (WAY), Lexington (LEX) — the three on Zoom Phone. HAR/WAY/LEX are closed Wednesdays and Sundays, so a missing recordings file for those two weekdays is expected, not a gap (see `CLOSED_WEEKDAYS = {2, 6}` pattern already used in `analyze_week.py`). Only treat a missing day as incomplete if it's a day the stores were open.

## Step 2 — Ingest (resumable, safe to re-run)
Working directory: `/Users/joshuadavis/Documents/Claude/Projects/Zoom Call Pipeline/`
- Run `python3 harvest_transcripts.py --since <window-start> --until <window-end>` to pull any recordings not already transcribed for the window. It skips files already on disk, so it's safe even if partially run before.
- If it reports transcription failures or the Zoom API errors out entirely, DM Joshua a one-line heads-up (no jargon) and stop — do not publish a partial or invented week.

## Step 3 — Batch and read
Working directory: `/Users/joshuadavis/Documents/Claude/Projects/Call Analysis/`
- Run `python3 make_batches.py` for the window (CUSTOMER-only calls, matching its existing filters) to produce `batches/<window>/batch_NN.txt`.
- Dispatch one parallel subagent (general-purpose, via the Agent tool, all batches in a single message so they run concurrently) per batch file. Give each subagent the shared reading rubric and ask it to tag every call:
  - **Type** — loan inquiry · selling to us · buying from us · existing-loan admin · hours · spam · other
  - **Outcome** — quoted · not quoted · appointment set · name captured · we had it · we didn't have it · turned away
  - **Verification** — was identity confirmed before anything was disclosed? yes/no/n/a
  - **Conduct flag** — none/LOW/MEDIUM/HIGH + category, with a verbatim quote and the call ID
  - **Exemplar flag** — none/STRONG/EXCEPTIONAL + which skill it demonstrates, with the call ID
  - **Want-list** — item asked for, not in stock
  - **Policy gap** — a rule stated wrong, inconsistently, or invented, with a verbatim quote
  Every finding must cite a call ID, date, and store — no unsourced claims.
- Aggregate every subagent's output into one structured findings set for the week.

## Step 4 — Pull audio for anything flagged
Use `pull_calls.py --info` first to confirm each flagged call's metadata, then pull audio for every MEDIUM/HIGH conduct item and every STRONG/EXCEPTIONAL exemplar. Convert each to AAC (.m4a) via ffmpeg (`-ar 44100 -ac 1 -c:a aac -b:a 96k`) so it opens cleanly in QuickTime Player — Music's importer has repeatedly failed on Zoom's native format, don't repeat that mistake. Save to `/Users/joshuadavis/Documents/Claude/Projects/Call Analysis/audio/<window>/`, named descriptively (store, subject, severity).

## Step 5 — Build the four packs + scoreboard
Write these files to `/Users/joshuadavis/Documents/Claude/Projects/Call Analysis/Weekly Packs/<window-start-date>/`:
1. `coaching_pack_HAR.md`, `coaching_pack_WAY.md`, `coaching_pack_LEX.md` — that store's quote/capture/verification rates vs. prior week, every MEDIUM/HIGH conduct item with the local audio file path and verbatim quote, the store's best call with what made it good, 2-3 "do this instead" notes.
2. `library_nominations.md` — every STRONG/EXCEPTIONAL exemplar this week, tagged by skill (using the skill taxonomy in the plan doc), with the audio path.
3. `policy_queue.md` — new policy gaps found this week, plus the standing 8-item queue from the plan doc if still open, each with a verbatim quote and call ID.
4. `want_list.md` — every item asked for and not in stock, with counts, cross-checked against what other stores have if you can determine it.
5. `scoreboard.md` — the 5 metrics (quote rate, capture rate, verification rate, conduct incidents, want-list fills) this week vs. the Aug 31 week baseline in FINDINGS_v2.

## Step 6 — Deliver (TEST MODE — see top of this prompt)
Send Joshua Davis (Slack DM, user_id `U03BB52MDSA`) a series of messages, one per pack, each capped well under 5000 characters:
1. One message per store coaching pack — condensed (top items only, HIGH conduct first), noting the full file path for the rest.
2. One message with the library nominations (call + skill + audio path).
3. One message with the policy queue.
4. One message with the want-list.
5. One message with the scoreboard, framed against baseline.
6. A final message: "TEST WEEK run complete — packs above and saved under Weekly Packs/<window-start-date>/. Nothing went to managers, Preston, or #call-insights this week. Confirm these look right and I'll switch this task to live distribution next Monday."

Never put an individual employee's name next to a MEDIUM/HIGH conduct item in anything other than this DM to Joshua — that rule doesn't relax even in test mode, it's just that Joshua is currently the only recipient.

## Step 7 — Log it
Append one entry to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/CHANGELOG.md` (newest first, matching existing convention) noting: window covered, calls processed, packs produced, TEST MODE delivery, and any open issues (e.g. the store-label/direction metadata bug from FINDINGS_v2, or the still-open Lexington firearm disposition) that remain unresolved.

## Rules that apply every run
- Rule 18: withhold rather than publish an incomplete or invented week.
- Rule 12: don't diagnose from metadata alone — if something looks off (e.g. a week with suspiciously few conduct flags), spot-check the actual transcript/audio before concluding anything.
- Never post individual employee performance data anywhere but this DM.
- Nothing produced here feeds bonus qualifiers, ever.
- If you hit a blocker only Joshua can resolve (Zoom auth expired, a script errors and you can't fix it, ffmpeg missing, etc.), DM him plainly what's blocked and what you tried — no jargon, no silent failure.