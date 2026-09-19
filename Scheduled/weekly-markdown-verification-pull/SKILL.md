---
name: weekly-markdown-verification-pull
description: Sunday 7PM — drops the markdown-verification trigger for all 5 stores (PART 1 of 2, mirrors the monday-bravo-combined-run/compile split). Unconditional trigger-drop, no contention gate (hardened 2026-08-21). Sends one quiet dispatch DM to Joshua (no channel post) so Fleet Guardian can verify it actually ran.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the dispatch DM described at the end of the steps below) returns success.

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
You are Part 1 of Valley Pawn's weekly aged-inventory markdown verification. This checks whether inventory sitting on the shelf over a year has actually had its price reduced, per Joshua's 2026-08-10 request to Preston: "Need workflow to insure markdown are being done... look at if aged inv has sales prices." Part 2 (`weekly-markdown-verification-review`, Monday ~9:35 AM ET) reads what this drops and posts the summary — this task only drops the trigger and exits. Target wall time: under 5 minutes.

> **HARDENING NOTE (2026-08-21) — no contention check, on purpose.** This task used to open with a call to `_bravo_foreground_guard.sh check` and would silently skip the week if it came back BUSY. That was the wrong pattern for this task and caused repeated silent no-ops (confirmed 2026-08-21: two consecutive BUSY hits on transient, unrelated pipeline activity killed a run that had zero actual collision risk). Per `bravo-context`'s own architecture section: this task only ever writes ONE JSON file into `triggers/` — it never touches Bravo's screen directly. Trigger-drop tasks are already safely serialized by `bravo_watcher.ahk`'s atomic claim mechanism. **Do not re-add a contention check here.**

> **FLEET GUARDIAN COVERAGE (2026-08-21) — same fix as `monday-bravo-combined-run`.** This task is now `rerun-safe` in `fleet/rerun_manifest.json` (it was previously misclassified as Bravo-driving/verify-only — corrected, since a trigger-drop is not screen-driving) and has an entry in `fleet/expected_outputs.json` (marker: the dispatch DM in Step 2 below, cadence weekly-sunday, grace_hours 2). If this task ever fails to run or dies mid-run again, the Fleet Guardian's Sunday 9:45 PM pass will detect the missing DM and re-run it automatically — this is why Step 2's DM is not optional, it's the mechanism that makes future silent failures self-healing instead of something a human has to notice.

> **LOCAL ACCESS GATE — DO THIS FIRST.** This task runs on Joshua's Mac Studio and has local access via `mcp__Control_your_Mac__osascript`. That tool may be deferred (not pre-loaded) — that is not the same as unavailable.
> 1. If `ToolSearch` is available, load it: `ToolSearch` query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe with `do shell script "echo READY"`. If it errors as not-connected, wait 30s and re-probe, up to 12 minutes total, before concluding local access is unavailable.
> **Timeout rule:** the osascript wrapper kills any call over ~25s. Never sleep >18s inside one call.
> **Filesystem rule:** all I/O under `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool (that folder is outside this task's sandbox).

Steps:

1. Generate a trigger ID `markdown-verification-YYYY-MM-DDTHH-MM-SS` (derive date/time via `do shell script "date -u +%Y-%m-%dT%H-%M-%S"`), and write this exact trigger JSON to `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/<id>.json` via osascript `do shell script "cat > '.../triggers/<id>.json' <<'EOF' ... EOF"` (or an equivalent heredoc-safe single shell command):
```json
{
  "id": "<id>",
  "requested_at": "<ISO8601 with -04:00 offset>",
  "reports": [
    {"name": "markdown-verification", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "<today's YYYY-MM-DD>"}
  ]
}
```
Do not alter key names — a malformed trigger gets silently renamed and never runs. If the write itself errors (disk/permission issue, not a Bravo/contention issue), retry once; if it still fails, log the error to `logs/_last_markdown_verification_trigger.txt` prefixed `ERROR:` instead of a trigger id, and still send the Step 2 DM but noting the failure plainly (e.g. "Markdown-verification pull dispatched — FAILED to write trigger, see log") so Guardian's marker search still finds a dated line to reason about and a human/Guardian knows to look closer, rather than pure silence.

2. Log the trigger ID to a small marker file so Part 2 can find it: `do shell script "echo '<id>' > '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/_last_markdown_verification_trigger.txt'"`. Then send Joshua ONE quiet Slack DM (channel D03BHQH5VGT, not any team channel) via `slack_send_message`: "Markdown-verification pull dispatched — <today's date>." That's it — one line, no jargon, no channel post. This DM is the Fleet Guardian's marker (see above) — always send it, success or logged-error case, so a missing Sunday run is detectable.

3. Do NOT poll for the result. This 5-store pull takes roughly 15-20 minutes to run serially (confirmed via a live smoke test 2026-08-13 — each store took 150-260 seconds) — Part 2 fires Monday morning, many hours later, so there is no need to wait here. Waiting risks the session running out of context mid-wait (the exact failure `monday-bravo-combined-run` hit before it was split into two tasks — do not repeat that mistake here).

4. Exit. No team-channel post, regardless of outcome — this task is silent to the field by design (mirrors monday-bravo-combined-run); the one Joshua DM in Step 2 is the only output.

## Final step (MANDATORY) — write the publication receipt

This task publishes to a surface with no readable history (a DM or a Slack canvas), so this receipt
is the ONLY evidence the task ran and delivered. Without it, a healthy run and a dead task are
indistinguishable in the fleet audit, and this task will read as AWAITING RECEIPTS forever.

Run this as the LAST action of the task, only after the publication actually succeeded:

```bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_receipt.py" write weekly-markdown-verification-pull \
  --surface slack-dm --target "D03BHQH5VGT" --note "<first line of what you published>"
```

Rules:
- Write it ONLY on a real, confirmed send. Never write a receipt for something you did not publish.
- If the task is silent by design this run (nothing to report), still write the receipt, with
  `--note "checked, nothing to report"`. Recording the look is what makes the silence trustworthy.
- If the publication FAILED, write it with `--ok false` and the reason in `--note`. Do not post the
  failure to Slack (Rule 16).


## Precondition (MANDATORY) — FLEET PUBLISH GUARD

Before publishing ANYTHING — a channel post, a DM to Joshua, a DM to a store manager, a canvas
refresh, an email, a Facebook post — check whether the fleet publish guard is armed:

```bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_dryrun.py" status
```

Exit code 0 means **ARMED**. When it is armed:

- Do the ENTIRE task for real — same pull, same data, same compile, same message text. The point is
  to test the task, not to skip it.
- Publish NOTHING. Not to a channel, not to a DM, not to a manager, not to a canvas, not anywhere.
- Instead write exactly what you would have published to
  `Valley Pawn OS/fleet/test_output/<task-name>-<YYYYMMDD-HHMMSS>.txt`, with a first line naming the
  channel or person it would have gone to.
- Do NOT write a normal publication receipt. A diverted run is not evidence that the task delivered,
  and recording it as one would corrupt the fleet audit.
- Say clearly in your final summary that the guard was armed and nothing was published.

Exit code 1 means not armed — run and publish normally.

This guard is ENFORCED for native scripts (they all publish through `vp_slack.py`, which intercepts
them). A Cowork task like this one has no such chokepoint, so here the guard is only as good as this
instruction. Honour it exactly. The guard always carries an expiry and disarms itself, so a stale
flag can never silence this task indefinitely.
