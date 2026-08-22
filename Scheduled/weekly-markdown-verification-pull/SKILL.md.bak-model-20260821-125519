---
name: weekly-markdown-verification-pull
description: Sunday 7PM — drops the markdown-verification trigger for all 5 stores (PART 1 of 2, mirrors the monday-bravo-combined-run/compile split). No Slack post, no waiting for results.
---

You are Part 1 of Valley Pawn's weekly aged-inventory markdown verification. This checks whether inventory sitting on the shelf over a year has actually had its price reduced, per Joshua's 2026-08-10 request to Preston: "Need workflow to insure markdown are being done... look at if aged inv has sales prices." Part 2 (`weekly-markdown-verification-review`, Monday ~9:35 AM ET) reads what this drops and posts the summary — this task only drops the trigger and exits. Target wall time: under 5 minutes.

> **LOCAL ACCESS GATE — DO THIS FIRST.** This task runs on Joshua's Mac Studio and has local access via `mcp__Control_your_Mac__osascript`. That tool may be deferred (not pre-loaded) — that is not the same as unavailable.
> 1. If `ToolSearch` is available, load it: `ToolSearch` query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe with `do shell script "echo READY"`. If it returns, proceed.
> 3. If it errors as not-connected, wait 30s and re-probe, up to 12 minutes total, before concluding local access is unavailable.
> **Timeout rule:** the osascript wrapper kills any call over ~25s. Never sleep >18s inside one call.
> **Filesystem rule:** all I/O under `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool (that folder is outside this task's sandbox).

Steps:

1. Contention check: `do shell script "bash '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh' check"`. If BUSY, wait 60s and re-check once. If still BUSY, exit silently (no Slack, no DM) — this is a low-urgency weekly pull, not worth forcing through a collision. It will get another chance next week, and Part 2 will just report "no fresh data" if nothing landed (see its own instructions).

2. If CLEAR, generate a trigger ID `markdown-verification-YYYY-MM-DDTHH-MM-SS` (derive date/time via `do shell script "date -u +%Y-%m-%dT%H-%M-%S"`), and write this exact trigger JSON to `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/<id>.json` via osascript `do shell script "cat > '.../triggers/<id>.json' <<'EOF' ... EOF"` (or an equivalent heredoc-safe single shell command):
```json
{
  "id": "<id>",
  "requested_at": "<ISO8601 with -04:00 offset>",
  "reports": [
    {"name": "markdown-verification", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "<today's YYYY-MM-DD>"}
  ]
}
```
Do not alter key names — a malformed trigger gets silently renamed and never runs.

3. Do NOT poll for the result. This 5-store pull takes roughly 15-20 minutes to run serially (confirmed via a live smoke test 2026-08-13 — each store took 150-260 seconds) — Part 2 fires Monday morning, many hours later, so there is no need to wait here. Waiting risks the session running out of context mid-wait (the exact failure `monday-bravo-combined-run` hit before it was split into two tasks — do not repeat that mistake here).

4. Log the trigger ID to a small marker file so Part 2 can find it: `do shell script "echo '<id>' > '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/_last_markdown_verification_trigger.txt'"`.

5. Exit. No Slack post, no DM, regardless of outcome — this task is silent by design (mirrors monday-bravo-combined-run). If the contention check was BUSY and you skipped dropping a trigger, still write the marker file step but with the PRIOR trigger id unchanged (do not overwrite it with nothing) so Part 2 falls back to last week's data source correctly if truly nothing new landed.