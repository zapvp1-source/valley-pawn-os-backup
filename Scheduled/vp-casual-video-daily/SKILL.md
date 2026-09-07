---
name: vp-casual-video-daily
description: Daily 7 PM ET — process casual-video-inbox: Whisper captions + lower-third + end-card, then AUTO-schedule to Brand FB/IG/TikTok/X via Publer at the next evening slot. Success DM only; failures silent (Claude self-heals via completion notification).
model: claude-sonnet-5
---

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


> ⚠️ **FAILURE HANDLING (Rule 16, supersedes the 2026-07-22 v2 DM policy — updated 2026-09-06).** Failure notices NEVER go to Slack — not to a team channel, not to a store manager, and not to Joshua's DM. If this run fails or cannot complete its core work, append one dated plain-language line plus the technical detail to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/STATUS.md` under a `## Run holds` heading and stop. The next session picks it up from there. Anything that does go to the field stays in plain everyday language — no error codes, no tool or file names. This replaces every 'DM Joshua that it did not complete' and every 'stay silent on Slack' instruction elsewhere in this file.


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
This is an automated run of a scheduled task. The user is not present. Execute autonomously. End with <run-summary>one or two sentences</run-summary>.


## Job
Process Valley Pawn's casual-video inbox and auto-schedule the results to social via Publer. This is the phone-shot casual video pipeline (Joshua's 2026-07-06 decision: AUTO-SCHEDULE, no approval gate; channels = Brand FB + IG + TikTok + X).

## Steps
1. Check the inbox via the Control-your-Mac osascript tool:
   `do shell script "ls ~/Documents/Claude/Projects/'Valley Pawn Studios'/casual-video-inbox/*.mp4 ~/Documents/Claude/Projects/'Valley Pawn Studios'/casual-video-inbox/*.mov 2>/dev/null"`
   If NO video files: end silently (run-summary: "inbox empty") — but FIRST run the empty-streak check below. Do nothing else.

   **Empty-streak check (added 2026-09-05 — the lane ran against an empty folder for 60+ days with nothing noticing).**
   Bump a counter and escalate ONCE per streak, to a file, never to Slack (Rule 16):
   `do shell script "D=~/Documents/Claude/Projects/'Valley Pawn Studios'; C=$D/.casual_inbox_empty_streak; N=$(cat $C 2>/dev/null || echo 0); N=$((N+1)); echo $N > $C; echo $N"`
   - If the returned count is **14 or a multiple of 14**, append to `Valley Pawn Studios/STATUS.md` under `## Run holds`:
     `YYYY-MM-DD — casual video: nobody has dropped a clip in the inbox for N days, so this lane has published nothing. Needs an owner and a weekly ask, or it should be paused.`
   - Otherwise write nothing anywhere.
   When files ARE found (step 2), reset the counter first: `do shell script "echo 0 > ~/Documents/Claude/Projects/'Valley Pawn Studios'/.casual_inbox_empty_streak"`
2. If files exist, run the processor (note the PATH export — ffmpeg lives in /opt/homebrew/bin):
   `do shell script "export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH; cd ~/Documents/Claude/Projects/'Refine Social Media' && python3 casual_video_processor.py 2>&1 | tail -30"`
   The script transcribes (faster-whisper/openai-whisper; if neither is importable, first run `python3 -m pip install --user faster-whisper` — it may take a few minutes), burns brand-spec captions, adds lower-third + end-card, normalizes to 9:16, then tries Publer API media upload + scheduling (Brand+BrandIG+BrandTikTok in one job at the next 6 PM ET slot, BrandTwitter in a second job with a ≤270-char caption).
3. Parse the JSON status lines it prints:
   - status "scheduled": success for that file.
   - status "needs_ui_upload": Publer's API media upload failed. Fall back to the Chrome MCP Publer UI flow: open app.publer.com, use the LOCKED account-picker pattern (search-token + JS DOM query — NEVER positional icon clicks; tokens: Brand FB="Valley Pawn", IG="valley_pawn", TikTok="Valley Pawn" tiktok row, X="valleypawn"), upload the MP4 from casual-video-inbox/outbox/ via the file input inside .droparea index 5, paste the caption from the status JSON (main_caption; x_caption for the X composer), Schedule for the target_slot time. Wait for the green "Successfully posted" banner between composers. One composer for FB+IG+TikTok is fine if Publer allows; otherwise separate composers per network.
   - status "failed": leave the file in the inbox, note in run-summary. Silent to Joshua.
4. On ≥1 successfully scheduled video, DM Joshua Davis on Slack (find him via user search) ONE message:
   "🎬 Casual video scheduled: {N} clip(s) → Brand FB/IG/TikTok/X, going live {day} {time} ET."
5. HARD GUARDRAILS: Publer only — NEVER Meta Graph API, NEVER open instagram.com/facebook.com against Valley Pawn accounts, NEVER developers.facebook.com. No firearms content — if a transcript mentions firearms/guns, do NOT schedule it; leave the processed file in outbox/ and note it in run-summary only.
