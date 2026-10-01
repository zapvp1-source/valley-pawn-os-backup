---
name: sunday-checklist-summary
description: Every Sunday 8 PM: summarize Preston's #in-store-checklists notes by store for the prior Mon–Sat and log TODOs into Apple Reminders.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---
This is an automated run of a scheduled task. The user is not present to answer questions. For implementation details, execute autonomously without asking clarifying questions — make reasonable choices and note them in your output. "write" actions (e.g. MCP tools that send, post, create, update, or delete), only take them if the task file asks for that specific action. When in doubt, producing a report of what you found is the correct output.

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access. That conclusion is false** and is the single most common cause of a false failure on this platform. If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.


## Failure policy (Rule 16 / Hardening Standard #6 — updated 2026-09-05)
Retry once, then try the documented alternate path. If still failing: write the technical detail to this task's run log/STATUS file and stop. Silence in every Slack channel. At most ONE plain-language DM to Joshua (D03BHQH5VGT), and only if a decision only he can make is blocking. Never post failure notices, technical jargon, or partial/incomplete data anywhere.

> ⚠️ **FIELD COMMUNICATION RULE (retained from the 2026-07-22 v2 banner):** anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths.

> 🛑 **NO-DUPLICATE RULE (added 2026-09-30) — read before STEP 5.** The 8/10–8/15 store-checklist TO-DOs were created in Apple Reminders TWICE — once by a manual backfill session on Fri 8/21 12:58 PM and again by this task's Sun 8/23 8:11 PM run — with differently worded titles, because nothing checked whether the same week's photo had already been logged. Every reminder this task creates must now pass STEP 4.5 first. Title wording is NEVER the match key; the source (week + photo filename / Slack message) in the reminder NOTES is. Reminders must be ENUMERATED via the EventKit CLIs in `/Users/joshuadavis/Documents/Claude/Projects/Life OS/bin/` (`ekrem`, `ekremnotes`) — NEVER via AppleScript (`get name of lists`, `reminders of list`), which silently sees only a subset of this Mac's lists (15 of 46 on 2026-09-09).


You are running an automated weekly review for Joshua Davis (CEO of Valley Pawn / Full Circle Finance Inc). This runs every Sunday at 8:00 PM ET. Be fully autonomous — do not ask questions, just complete the work.

GOAL
Review the past week of the Valley Pawn "in-store checklists" Slack channel, summarize by store what Preston Peters (Operations Manager) talked about, identify any TO-DOs, and log those TO-DOs into Apple Reminders.

STEP 1 — Determine the date window.
The window is LAST WEEK, Monday through Saturday (the most recent Mon–Sat that just ended before this Sunday run). Use a bash `date` call to compute the exact dates. Example: if today is Sunday 2026-06-28, the window is Mon 2026-06-22 through Sat 2026-06-27. Note the window explicitly in your summary. Record the window's MONDAY as `WEEK` in YYYY-MM-DD form — STEP 4.5 keys on it. Only photos/messages POSTED inside this window belong to this run; never process an older week's posts (dates mentioned elsewhere in this file, e.g. "August 11th", are examples, not targets).

STEP 2 — Read the Slack channel.
Channel: #in-store-checklists, channel ID `C0B5Q65QZUJ` (private). Use the Slack MCP tool `mcp__f92ce7c6-0353-4419-8491-f0843b182ff2__slack_read_channel` to read messages in the window, and `slack_read_thread` to expand any threaded replies. Focus on messages from Preston Peters (Slack user `U03BWMEM9GR`, preston@fcfpawn.com) — what he flagged, asked for, instructed, or noted. Include relevant replies/context from store employees when they clarify a Preston item.

Almost every one of Preston's posts in this channel is a PHOTO of a paper "In-Store Checklist" form with little or no caption text — the Slack read tool only returns the filename/ID for these, not the pixels. Do NOT treat "no caption text" as "nothing to report." This is the normal case, not the exception. Every message with a file attachment must go through STEP 2.5 below — confirmed working end-to-end on 2026-08-21.

STEP 2.5 — Read the checklist photos via the browser (proven working method — follow exactly).
For every Preston message in the window that has a file attachment:
1. If Chrome MCP tools are deferred, load them in one call: `ToolSearch` with query `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__tabs_close_mcp`.
2. Call `tabs_context_mcp` with `createIfEmpty:true`, then `navigate` the tab to `https://slack.com/app_redirect?channel=C0B5Q65QZUJ`. This rides Joshua's already-authenticated Slack session on his own Mac — do not attempt to log in or enter any credentials.
3. An interstitial page appears ("Redirecting to in-store-checklists... Or, you can open this link in your browser"). Take a screenshot, then click the "open this link in your browser" text link. Wait ~2-3 seconds (use the `wait` action, not a long sleep) and screenshot again — you should now be on `https://app.slack.com/client/{TEAM_ID}/C0B5Q65QZUJ` showing the channel itself, already logged in. (Team ID as of 2026-08-21 is `T03BL4W1DCL` — if the redirect ever lands you straight on that URL, skip step 3's click.)
4. The channel loads scrolled to the newest messages. Use `scroll` (up = older, down = newer) on the message pane to find the date range you need — Slack shows date divider pills ("Tuesday, August 11th" etc.) so you can navigate visually. This channel is low-volume (a handful of posts a week), so scrolling to the right dates is quick; do not overthink it with in-app search.
5. Each checklist photo renders inline in the message list once you scroll it into view (may take a second to load from blurry placeholder to sharp — screenshot again if it still looks blurry). Once sharp, use the `zoom` action on the image's region (get the bounding box from a screenshot first) to read it at full resolution — you have native vision, no external OCR needed. Read: the Store name (top-left field), the Date, every Yes/No checkbox that's marked No (these are flags), and the full handwritten "Additional Notes" section at the bottom — that notes section is where Preston/the store manager write real instructions and is the single most important field to capture completely and accurately.
   - If the inline image is too small/cropped to read even after zoom, click it to open Slack's full-size lightbox viewer, then use the lightbox's own zoom-to-fit / minus button (or zoom the whole modal region) before reading — do not stay stuck on a partial crop.
6. Note in your working notes which store/date each photo covers, every "No" checkbox, and the verbatim (or near-verbatim) Additional Notes text. Also note each photo's FILENAME (e.g. IMG_2990.jpg, from the Slack read tool's file info) — it is the dedupe source key in STEP 4.5.
7. Feed all of this into STEP 3 (per-store summary) and STEP 4 (TO-DO extraction) exactly as if it had arrived as message text from Preston. Mark in your output which items came from a photo transcription so Joshua can spot-check if something looks off.
8. Close any tabs you opened before finishing.

Fallback — only if Chrome MCP is genuinely unavailable (not deferred — actually failing after loading), or the Slack web session shows a real login wall (email/password prompt) instead of landing straight in the channel: do not attempt to log in or guess credentials. Note in the output, per affected message, that the image could not be read this run, with its filename, timestamp, and date, so Joshua can open it manually. Continue with everything else that could be determined. This should be rare — as of 2026-08-21 this flow works reliably with no login prompt.

STEP 3 — Summarize by store.
Group Preston's notes (from text and from STEP 2.5 transcriptions) under each of the 5 stores:
- Culpeper
- Waynesboro
- Harrisonburg
- Lexington
- Roanoke
For each store, write a short bullet summary of what Preston discussed that week — including flagged "No" checkboxes and Additional Notes content from checklist photos. If a note is company-wide (not store-specific), put it under a "Company / All Stores" heading. If a store had nothing (genuinely no posts, or posts fully transcribed with nothing notable), say "No notes this week."

STEP 4 — Extract TO-DOs and classify each.
For every actionable item Preston raised (from text or from a transcribed photo — including anything implied by a "No" checkbox plus its context, and everything in "Additional Notes"), classify it as either:
  (A) CORPORATE / COMPANY deliverable — something Joshua or the corporate office owns (e.g., order signage company-wide, fix a policy, vendor/payroll/marketing/IT items, anything not a single-store floor task).
  (B) STORE / EMPLOYEE deliverable — a task a specific store or its employees must do (e.g., "Lexington needs to redo the jewelry case," "Roanoke clean the back room," a specific checklist "No" item).
Write a clear, action-oriented reminder title for each (start with a verb; include the store name in store items, e.g. "Lexington: re-merchandise jewelry case"). If a due date is implied, include it.
Tag every TO-DO with its SOURCE KEY: the photo filename stem (e.g. `IMG_2990`) for photo items, or `slack-ts-<message ts>` for typed-text items.

STEP 4.5 — Duplicate guard (MANDATORY before any reminder is created).
Run, via `mcp__Control_your_Mac__osascript` `do shell script` (use `quoted form of` for every argument):
  `/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/checklist_reminder_dedupe.py" check --week <WEEK> --source <KEY1> --source <KEY2> ... || true`
One `--source` per distinct source key from STEP 4. It checks, in order: the state ledger `Valley Pawn OS/fleet/state/sunday-checklist-summary_created.json`; the live Reminders NOTES of all 6 canonical lists via `Life OS/bin/ekremnotes` (EventKit — it compiles itself from `ekremnotes.swift` on first use); and, only if that is unavailable, the Unified Search index snapshot of Reminders. A match = any reminder, OPEN or COMPLETED, whose notes carry the same photo/message key AND the same week. It prints `LOGGED <key> via=... evidence=...` or `NEW <key>` per source, then a `CHECKS ...` line.
- `LOGGED` → create NOTHING from that source, even if this run worded or split its items differently. List those items in the output under "Already logged — not re-created" with the evidence shown.
- `NEW` → proceed to STEP 5 for that source's items.
- If the script's last line shows BOTH `live=unavailable` and `index=unavailable` (exit 3), or the script itself cannot run: create NO reminders this run. Put the full TO-DO list in the output instead (grouped Corporate vs each store) and append one FAILURE_LEDGER row ("checklist reminders not logged — duplicate check could not run"). A missed reminder is recoverable; a duplicate set is what this guard exists to stop.
- Within one run, never create two reminders from the same source + same Additional Notes line.

STEP 5 — Log TO-DOs into Apple Reminders (via `mcp__Control_your_Mac__osascript`).
First enumerate the existing Reminders lists so you use exact names — with EventKit, never AppleScript:
  `"/Users/joshuadavis/Documents/Claude/Projects/Life OS/bin/ekrem" lists`
As of 2026-08-21 these lists exist and are the canonical destinations — do not recreate them, just confirm they're still present:
  "Preston Joshua" (corporate), "Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke" (one per store).
- CORPORATE deliverables → add to the list named exactly **"Preston Joshua"**.
- STORE deliverables → add to that store's own list by exact name match (Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke).
- If, on some future run, a list from this canonical set is genuinely missing from `ekrem lists` output (renamed/deleted), do not silently drop the item and do not just fall back — re-run `ekrem lists` once to confirm, and if it's truly gone, create a new list with that exact name (AppleScript is acceptable for this one CREATE action only: `tell application "Reminders" to make new list with properties {name:"<StoreName>"}`), confirm it now appears in `ekrem lists`, add the reminder there, then note in the output that you had to recreate a missing list.

To add a reminder (only for sources STEP 4.5 returned as NEW), use ekrem — due-date argument `none` leaves the reminder undated exactly as before (ekrem prints a harmless "bad date none" line, then "OK added ... :: <id>"):
  do shell script "'/Users/joshuadavis/Documents/Claude/Projects/Life OS/bin/ekrem' add " & quoted form of "<List>" & " " & quoted form of "<title>" & " none " & quoted form of "<notes>"
Notes text (same content as before, plus the key line at the end):
  "From #in-store-checklists week of <window>. Source: <text message | photo transcription, Preston Peters post <date/time>, <image filename>>. <supporting detail — flagged checkbox and/or verbatim note text>. Dedupe key: wk=<WEEK> src=<KEY>"
(Get the exact key line from `/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/checklist_reminder_dedupe.py" key --week <WEEK> --source <KEY>` if unsure.) Every body should say clearly whether the item came from typed text or a photo transcription, and include enough of the original note/flag that Joshua can verify it against the source photo if needed.
IMMEDIATELY after each successful add (before the next add), record it:
  `/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/checklist_reminder_dedupe.py" record --week <WEEK> --source <KEY> --list <List> --title <title> --id <id from the ekrem OK line>`
so a crash or re-run can never create the same item twice. If `ekrem add` itself errors, retry once; if it still fails, fall back to the AppleScript create (`tell application "Reminders" to make new reminder at end of list "<List>" with properties {name:"<title>", body:"<notes>"}`) — still followed by `record`.

IMPORTANT — Reminders permission: this Mac may need automation/Reminders access granted the first time. If the ekrem/osascript calls error with a permissions failure ("ERROR: no Reminders access" or an automation error), DO NOT silently fail. Instead: (a) still produce the full summary and the complete TODO list (clearly grouped into Corporate vs each store) in your output so nothing is lost, and (b) state clearly at the top of the output that reminders could not be written because Reminders access needs to be approved on the Mac, and the listed items should be added manually or the task re-run once access is granted.

STEP 6 — Output.
Produce a clean summary report with: the date window; per-store sections of what Preston discussed (noting which items came from a photo transcription, including any flagged "No" checkboxes); a "TO-DOs Logged" section listing each reminder created and which Reminders list it went into (Corporate vs store); an "Already logged — not re-created" section (from STEP 4.5, if any); an "Images not read this run" section (if any, should be rare per STEP 2.5) with filename/timestamp/date; and any fallback/permission notes. This output is delivered to Joshua as the run notification.

Do not post anything back into the Slack channel. Do not message employees. The only writes you perform are to Apple Reminders and to this task's state ledger (`Valley Pawn OS/fleet/state/sunday-checklist-summary_created.json`) — plus a FAILURE_LEDGER row if STEP 4.5 blocks creation.