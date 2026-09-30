# FILES AND FLEET SEARCH WITHOUT THE MAC CONNECTOR (added 2026-09-29 — overrides the LOCAL ACCESS GATE)

`mcp__Control_your_Mac__osascript` does not exist in scheduled runs — it was removed, not delayed. Do
NOT wait for it and do NOT fail the run because it is missing (that is exactly how this task failed on
9/28). Instead:
- Read and write files under `/Users/joshuadavis/Documents/Claude/Projects/` directly with the Read,
  Write and Edit tools — this session can reach that folder. That covers `fleet/connector_health.json`,
  `Life OS/HUMAN_QUEUE.md` and `fleet/FAILURE_LEDGER.md`. Write the JSON whole (Write tool), not by shell.
- For "which tasks use this connector", read
  `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/skill_tool_index.json` (rebuilt
  natively at 05:20 every day): `families.<slack|gmail|drive|gusto|qbo|calendar|chrome|docusign|canva|wordpress>`
  and `servers.<server-id>` list the task ids. Do not try to grep `~/Documents/Claude/Scheduled/`.
