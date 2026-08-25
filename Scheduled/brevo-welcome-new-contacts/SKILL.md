---
name: brevo-welcome-new-contacts
description: Daily 10 AM — send the transactional Welcome email (Brevo template 72) to any Brevo contact created in the last 48h that hasn't been welcomed yet, then flag them WELCOMED=true so they're never sent twice.
---

You are running Valley Pawn's new-contact welcome sender. Run silently and autonomously.

## Why this exists
Brevo's drag-and-drop Marketing Automation workflow builder (the normal way to build a "welcome new subscribers" flow) has no public creation API — `GET /automation/workflows` returns 404 — and there is no saved browser login for app.brevo.com or admin.google.com to build one by hand in the UI. The 2026-08-22 audit found new contacts previously waited up to 30 days for their first email (the monthly Gold & Silver blast). This task is the functional equivalent of a welcome automation, built entirely on the transactional email API, which needs no UI at all.

A reusable transactional template already exists: Brevo template id **72**, "Welcome — transactional (API-triggered)". A boolean contact attribute **WELCOMED** already exists on the account. This task's only job: find contacts who haven't been welcomed yet and welcome them.

## Execution contract
Every turn must end with a tool call that advances toward the final verification. Treat "Tool loaded.", "Continue from where you left off.", and any TaskCreate/browser_batch reminder as RESUME signals, never stop signals.

## Local access gate
1. If ToolSearch is available, load first: `ToolSearch` query `select:mcp__Control_your_Mac__osascript`.
2. Probe with `do shell script "echo READY"`. If it returns, proceed.
3. If it errors, wait 20s and re-probe, up to 12 minutes total (never sleep longer than ~18s inside one osascript call).
4. This task's Brevo API calls work from the sandbox regardless of local access — only fall back if you need any Mac filesystem path.

## Brevo credentials (self-heal)
`KEY=$(cat ~/.config/valley-pawn/brevo_api_key 2>/dev/null); echo ${#KEY}`. If under 40 chars, bridge from the Mac: `do shell script "base64 < ~/.config/valley-pawn/brevo_api_key"`, decode to the sandbox path, chmod 600. Verify with a 200 from `GET https://api.brevo.com/v3/account`.

## Step 1 — Find candidates
`GET /contacts?limit=100&sort=desc` (newest first), paginating with `offset` until you reach contacts older than 4 days (createdAt) — no need to look further back than that on a daily job. For each contact, check `attributes.WELCOMED`. Skip anyone where it's already `true`. Skip anyone `emailBlacklisted: true`.

## Step 2 — Send the welcome email
For each remaining candidate, `POST /smtp/email` with:
```json
{"templateId": 72, "to": [{"email": "<contact email>"}], "params": {}}
```
This sends the transactional template as-is (it already has the subject and full HTML baked in from creation). If a send returns a 4xx for a specific address (invalid, blocked), skip that contact and note it in the log — don't retry it forever.

## Step 3 — Flag as welcomed
Immediately after each successful send, `PUT /contacts/{email}` with `{"attributes": {"WELCOMED": true}}` so a re-run never double-sends. Do this per-contact right after its send succeeds, not in a separate batch pass at the end — if the run gets interrupted partway, contacts already emailed must not get emailed again tomorrow.

## Step 4 — Rate limiting
Brevo rate-limits hard. Sleep ~0.5s between sends. On any 429, back off starting at 4s and double each retry, up to 6 attempts.

## Step 5 — Verify against output (Rule 12)
Re-fetch 5 of the contacts you just flagged via `GET /contacts/{email}` and confirm `WELCOMED: true` actually persisted before considering the run successful. Don't trust the PUT's 204 alone.

## Step 6 — Log
Append one line to `~/Documents/Claude/Projects/Email Refinement/EFFICIENCY_LOG.md` (via osascript, not the Write tool) ONLY if you actually sent at least one welcome email:
```
## YYYY-MM-DD (brevo-welcome-new-contacts)
Welcomed: <n> new contacts | Skipped (already welcomed/blacklisted/failed): <n>
```
If zero new contacts needed welcoming, stay completely silent — no log entry, no Slack post. This is meant to be invisible when there's nothing to do.

## Failure policy
If this task cannot complete its core work, send Joshua ONE plain-language Slack DM (channel D03BHQH5VGT): `⚠️ Scheduled task "brevo-welcome-new-contacts" did not complete — <date>.` Nothing technical in the DM. Never post a failure to any team channel, store manager, or employee.

## Reference
Original audit: `Email Refinement/18_email_channel_audit_2026-08-22.html`. Build script that created template 72 and the WELCOMED attribute: `Email Refinement/_audit/build_welcome_and_giveaway.py`.