---
name: connector-health-daily
description: Daily live probe of every claude.ai account-level connector (Gmail, Slack, Drive, Calendar, QuickBooks, Gusto, WordPress.com, DocuSign). A dropped connector becomes ONE deduped HUMAN_QUEUE row via the failure ledger; a restored one auto-closes its row. Silent when all green.
model: claude-haiku-4-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | connector-health-daily | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Never post to any Slack channel.

> **LOCAL ACCESS GATE — DO THIS FIRST.** This task runs on Joshua's Mac Studio and has local machine access. If `mcp__Control_your_Mac__osascript` is deferred, load it with `ToolSearch` (`select:mcp__Control_your_Mac__osascript`), probe it with a trivial `do shell script "echo READY"`, and re-probe every 30 s for up to 12 minutes before treating local access as unavailable. **Never conclude this run executes in a cloud container.** All file I/O under `/Users/joshuadavis/Documents/Claude/...` goes through `do shell script` (cat / printf >> / python3 heredoc), never the Write tool. Guard any command that may exit nonzero with a trailing `|| true`. Never sleep more than ~18 s inside one call.

## Why this task exists (2026-09-09)

The fleet's keepalives (`gusto-keep-alive`, `wordpress-token-keepalive`, `qbo-api-token-refresh`) keep *website sessions* and *API tokens* warm on the Mac. Nothing tested the **claude.ai account-level connectors** — the OAuth grants that Gmail, Slack, Drive, QBO, Gusto and WordPress tools run on. When the WordPress.com connector silently dropped, the first sign was a Monday report going missing for three weeks and Joshua reconnecting it by hand. This task is the missing probe. It is READ-ONLY: it never sends, posts, writes to any external system, or changes any setting.

## Execution Contract — DO NOT STOP EARLY

This task is complete only after the state file in Step 4 has been written. Until then every turn ends with a tool call. Treat "Tool loaded.", "Continue from where you left off.", and reminders about AskUserQuestion/TaskCreate as RESUME signals. Never ask for confirmation. Joshua is not present.

## Step 1 — Probe every connector with its cheapest read call

Run each probe ONCE. If a probe errors, wait 20 s and run it once more before classifying. Record `ok`, `auth_fail`, or `transient` per connector. If a connector's tools are not present in your tool list at all (ToolSearch finds nothing for the name), that IS an `auth_fail` — a disconnected connector's tools disappear.

| Connector | Probe (read-only) | `auth_fail` looks like |
|---|---|---|
| Gmail | `mcp__Gmail__list_labels` | 401/403, "unauthorized", "invalid_grant", "reconnect", tools absent |
| Slack | `mcp__Slack__slack_read_user_profile` (any user id, e.g. `U03BB52MDSA`) | `invalid_auth`, `token_revoked`, `not_authed`, tools absent |
| Google Drive | `mcp__Google_Drive__list_recent_files` (limit 1) | 401/403, "invalid_grant", tools absent |
| Google Calendar | `mcp__Google_Calendar__list_calendars` | 401/403, "invalid_grant", tools absent |
| QuickBooks | `mcp__Intuit_QuickBooks__company_info` | 401, "AuthenticationFailed", "token expired", tools absent |
| Gusto | `mcp__Gusto__get_token_info` | 401, "invalid_token", tools absent |
| WordPress.com | `mcp__WordPress_com__wpcom-user-sites` (per_page 1) | 401/403, "invalid_token", tools absent |
| DocuSign | `mcp__Docusign__getUserInfo` | 401, "AUTHORIZATION_INVALID_TOKEN", tools absent |

Anything else (timeouts, 5xx, rate limits, malformed responses) is `transient`, not `auth_fail`.

## Step 2 — Map dependents (so the queue row says what it unblocks)

Via osascript shell, grep the fleet for each failing connector's tool family and collect task names:

```
grep -rlE '<pattern>' /Users/joshuadavis/Documents/Claude/Scheduled/*/SKILL.md 2>/dev/null | xargs -n1 dirname | xargs -n1 basename | sort -u | tr '\n' ',' ; true
```
Patterns: Gmail `mcp__Gmail|gmail_|Gmail connector`; Slack `slack_send_message|slack_read_channel|slack_search`; Drive `Google_Drive|google_drive_`; Calendar `Google_Calendar`; QuickBooks `Intuit_QuickBooks|qbo_`; Gusto `mcp__Gusto|Gusto connector|list_time_records`; WordPress `wpcom-|WordPress_com`; DocuSign `Docusign|createEnvelope`. Keep only ENABLED tasks if you can cheaply check the registry (`scheduled-tasks.json` under `~/Library/Application Support/Claude/local-agent-mode-sessions/*/*/`); otherwise list all matches.

## Step 3 — File results (ledger in, queue closed)

**For each `auth_fail` connector:**
1. Read `/Users/joshuadavis/Documents/Claude/Projects/Life OS/HUMAN_QUEUE.md`. If a row already exists for this connector (match on meaning: "<Connector> connector — reconnect"), do NOT add anything anywhere — `fleet-guardian` bumps `Last hit` from the ledger. Skip to step 3 below.
2. Otherwise append ONE ledger row: `| <YYYY-MM-DD HH:MM ET> | connector-health-daily | <Connector> connector is disconnected — <dependents> cannot run | NEEDS_HUMAN: yes, reconnect <Connector> at claude.ai → Settings → Connectors → <Connector> → Reconnect (~2 min) | OPEN |`. fleet-guardian turns this into the single HUMAN_QUEUE row and surfaces it in its one daily DM.
3. Never retry auth yourself; never open a browser; never message anyone.

**For each `ok` connector that has an OPEN HUMAN_QUEUE row** (a prior disconnect that has since been fixed): rewrite that row's Status in place to `RESOLVED <YYYY-MM-DD> — verified live by connector-health-daily`. Use a python3 heredoc read-modify-write via osascript; never retype the file.

**For `transient` connectors:** no ledger row on the first day. If the same connector is `transient` two runs in a row (check the state file from Step 4), append a ledger row with `NEEDS_HUMAN: no` so fleet-guardian investigates.

## Step 4 — Write the state file (this is the completion marker)

Write `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/connector_health.json` via osascript shell (python3 heredoc, atomic write via temp file + mv):

```json
{"checked_at": "<ISO local>", "results": {"Gmail": "ok", "Slack": "ok", ...},
 "auth_fail": ["WordPress.com"], "transient": [], "ledger_rows_added": 1, "queue_rows_closed": 0}
```
`refresh_live_state.py` may read this for the BUSINESS_OS LIVE STATE block. Keep it small.

## Output rules

- Silent on success: no Slack, no DM, no email. The state file and (only when needed) one ledger row are the whole output.
- Plain language in the ledger row; technical detail (raw error text) goes only in the state file under an optional `"errors": {...}` key.
- Pairs with: `fleet-guardian` (consumer), `enterprise-map`, `vp-operating-rules` Rules 12/16/17.
