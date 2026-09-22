---
name: connector-probe-oneshot
description: One-time probe: records whether mcp__Control_your_Mac__osascript is available inside a scheduled-task session. Auto-disables after one run.
---

You are a ONE-SHOT DIAGNOSTIC PROBE. Do exactly this and nothing else. Do not touch Bravo, Parallels, Slack, or any business system. Publish nothing anywhere.

BACKGROUND: the `Control_your_Mac` connector (tool name `mcp__Control_your_Mac__osascript`) disappeared from scheduled-task sessions around 2026-09-12. Eleven weekly Valley Pawn tasks gate on it and have been failing. Joshua may have just reinstalled it. An interactive session cannot answer whether a SCHEDULED session has it, because tool availability differs by session type — only a scheduled session can answer that, which is why this task exists.

STEP 1. Determine whether the tool is available to you.
- Use ToolSearch with the query: select:mcp__Control_your_Mac__osascript
- Then also try a keyword search: osascript control your mac shell
- Note plainly whether an exact tool named `mcp__Control_your_Mac__osascript` is present. Do NOT count near-matches like computer-use or claude-in-chrome — those are different capabilities and counting them would give a false positive, which is worse than no answer.

STEP 2. If and ONLY IF the exact tool IS present, run the single harmless command `echo CONNECTOR_ALIVE` through it and record the exact output. Nothing else. No file writes, no app control.

STEP 3. Write your finding to this file, creating it fresh (overwrite if it exists):
/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/CONNECTOR_PROBE.md

Use exactly this structure:

# Control_your_Mac probe — scheduled session
- Ran at: <timestamp>
- Exact tool `mcp__Control_your_Mac__osascript` present: YES or NO
- ToolSearch select result: <what came back, verbatim or "no match">
- ToolSearch keyword result: <names of any tools returned, or "no match">
- echo test output: <the output, or "not attempted — tool absent">
- VERDICT: one sentence. If YES: the connector is back for scheduled sessions and the eleven weekly tasks can use it again. If NO: it is still unavailable to scheduled sessions regardless of what the app's settings show, and those tasks must keep using the native/host-queue path.

STEP 4. Post NOTHING to Slack. Send NO DM. Do not write to FAILURE_LEDGER.md. The file above is the entire deliverable.

Be precise and literal. A wrong YES here would send someone to rebuild eleven tasks on a capability that does not exist.