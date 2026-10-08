---
name: zz-cloudtest-timestamp
description: TEST ONLY 2026-10-07: writes one tiny marker file under fleet/state/cloudtest/ so we can learn how Cowork cloud copies are created and switched off. No Slack, no email, no other tools.
---

TEST TASK — harmless. Do exactly one thing and stop.

Use ONLY the Write tool (no shell, no browser, no Slack, no email, no other connectors, no other tools at all) to create ONE new file in this folder:
/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/state/cloudtest/

File name: run-<8 random lowercase letters>.txt  (pick fresh random letters every run so files never collide)

File contents (plain text, one item per line, copy values literally from your own context; write "unknown" for anything you can't see):
- task: zz-cloudtest-timestamp
- date_from_context: <today's date as given in your context>
- working_directory: <your primary working directory / cwd as stated in your environment section>
- additional_dirs: <any additional working directories listed>
- platform: <platform / OS listed in your environment section>
- shell_tool_named: <the exact name of any shell/bash tool you have, or "none">
- browser_tool_present: <yes/no — do you have any Chrome/browser tool>
- session_hint: <any session id, scratchpad path or outputs path visible in your context>

If the folder doesn't exist or the Write fails, do nothing else — do not retry with other tools, do not message anyone. Then stop.