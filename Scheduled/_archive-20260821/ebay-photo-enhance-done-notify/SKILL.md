---
name: ebay-photo-enhance-done-notify
description: Daily check on the eBay photo 1600px-upscale backlog; Slack Joshua on progress/completion
model: claude-haiku-4-5
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


> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


Check the progress of the eBay photo 1600px-upscale backlog (driven by the quota-safe runner run_pass2.sh + ebay_photo_enhance.py, scheduled via launchd com.valleypawn.ebay-photo-upscale at 4am ET daily), then notify Joshua on Slack only when there's something worth telling him.

Use the osascript tool (mcp__Control_your_Mac__osascript) for all local reads.

1. Read state:
   - ps -ax | grep '[e]bay_photo_enhance.py' | wc -l   (0 = no run in progress)
   - tail -40 ~/enhance_run.log        (per-store results from the most recent run)
   - Progress from state + the photos.json snapshots:
     /usr/bin/python3 - <<'PY'
     import json,os,glob
     st=json.load(open(os.path.expanduser('~/ebay_photo_enhance_state.json')))
     up={k for k,v in st.items() if v.get('upscaled')}
     tot=done=0; per={}
     for f in glob.glob('/Users/joshuadavis/Documents/Claude/Projects/eBay/*_photos.json'):
         store=os.path.basename(f).split('_photos')[0]
         d=json.load(open(f)); ids=[str(it['id']) for it in d if it.get('pics')]
         du=sum(1 for i in ids if i in up)
         per[store]=(du,len(ids)); tot+=len(ids); done+=du
     print('TOTAL',done,'/',tot)
     for s,(a,b) in sorted(per.items()): print(s,a,'/',b)
     PY

2. Interpret:
   - COMPLETE when done == tot (every listing with photos is marked upscaled) AND no run is in progress.
   - If not complete, note how many remain and whether the last run stopped on the eBay usage limit (grep 'STOP' ~/enhance_run.log) — that's expected; it resumes next morning.

3. If COMPLETE: verify it's really live. Pick 2-3 upscaled item IDs from ~/ebay_photo_enhance_state.json, GetItem their first PictureURL, download it, and check dimensions with PIL (max side should be ~1600). Reuse the eBay Trading API auth pattern from ebay_photo_enhance.py (tokens from ~/ebay_weekly_rankings.py STORES; GetItem call). If GetItem itself 503s / hits the usage limit, note that verification was blocked and report counts only.

4. Slack DM to Joshua (user_id U03BB52MDSA as channel_id) ONLY IF: the backlog just reached COMPLETE, OR a run happened since yesterday and progress changed, OR an error/anomaly appeared. Keep it short and skimmable: total upscaled X/Y, per-store, whether last run hit the limit (normal), and — if complete — confirmation that sampled live primaries measure ~1600px. If nothing changed and it's still mid-backlog with no new run, do NOT DM — just output a brief report.
   Note in the completion DM that the whole thing is reversible via:
   /usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/eBay/ebay_photo_enhance.py' --revert --apply

This is an automated run with no user present — execute autonomously, make reasonable choices, and only take the Slack 'send' action described above. End with <run-summary>one or two sentences on progress and whether anything changed since last run</run-summary>.