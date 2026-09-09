---
name: bald-rock-15-day-contract
description: Daily 9 AM — scan every Bald Rock reservation checking in within 15 days. (1) Send contract if missing, (2) remind if unsigned ≤3 days out, (3) send age/ID (30+) verification request alongside every new contract and track replies — manual workaround, DocuSign IDV add-on not purchased (cost doesn't justify volume). DMs Joshua a Slack summary.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22; v3 2026-09-08):** If this run fails, errors out, or cannot complete its core work, do NOT message Joshua, Preston, or anyone else, in any medium. Instead append ONE row to the fleet failure ledger `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` (use `mcp__Control_your_Mac__osascript` `do shell script "printf ... >> file"` if file tools cannot reach it) in exactly this form: `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or: yes, <the single thing only Joshua can do>> | OPEN |`. The `fleet-guardian` task reads this ledger twice a day, re-runs whatever is safe to re-run, rolls anything that truly needs Joshua into `Life OS/HUMAN_QUEUE.md`, and sends Joshua at most ONE consolidated plain-language DM per day. Individual tasks never DM about failures. All technical detail goes in the run output/log/STATUS file for the next Claude session to pick up. Never send failure notices to any team channel, store manager, employee, or Preston. FIELD COMMUNICATION RULE (unchanged): anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This v3 supersedes both the v2 one-line-DM rule and any older rule in this file.

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the Slack DM described at the end of the steps below) returns success.

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

## Objective

Three-phase daily run for **282 Bald Rock Road, Verona, VA 24482**:

1. **SEND** — for every guest in Guesty with check-in **within the next 15 days** and NO non-voided DocuSign envelope in the past 30 days, send the matching DocuSign rental contract (VRBO direct-to-email, Airbnb via embedded-link in Guesty thread).
2. **REMIND** — for every guest with an existing non-voided envelope that is **NOT** in `completed`/`signed` status AND whose check-in is **≤3 days away**, send a reminder.
3. **VERIFY (age/ID, 30+ policy)** — for every guest who just had a contract sent in Step 1 (first time only, not on repeat runs) AND for any guest with a signed/sent contract who has NOT yet been sent the age-verification request, send the age-verification request via the Guesty thread. Track replies. This step exists because DocuSign's built-in ID Verification add-on was priced out on 2026-08-07 ($75/month minimum for 30 verifications — not worth it at Bald Rock's ~2-4 guests/month volume) — see the `real-estate-context` skill / decision log. Until that changes, this manual ask-and-log step IS the property's age-verification control, and it is treated with the same rigor and de-dup discipline as contract delivery — never skip it, never send it twice to the same guest.

Repeat runs are idempotent — DocuSign envelope state and the de-dup check make this safe to run daily. DM Joshua a Slack summary covering all three phases.

## Authoritative reference — read this first

**`anthropic-skills:bald-rock-property` → "Contracts" section** holds the operational manual: template IDs, channel detection rules, the VRBO direct-email flow, the Airbnb embedded-link-via-Guesty workaround (including the `charCodeAt` URL-extraction bypass that's required until DocuSign MCP beta access lands), de-duplication rules, voiding procedure, and the welcome-message copy. Treat that section as the source of truth — this prompt is only the orchestration layer around it.

Also relevant: the **"Looking up reservation data in Guesty"** subsection for navigating Guesty to find each guest's name, email, conversation thread, and channel.

## Run

1. **Compute window** — `today` and `today + 15 days` in Joshua's local timezone (`YYYY-MM-DD` for both). The window is INCLUSIVE on both ends.
2. **Pull candidate reservations from Guesty.** Capture every reservation whose `checkIn` date falls anywhere from today through today+15 (inclusive). For each, record: confirmation code, full guest name, check-in datetime, channel (VRB-… = VRBO; HM… = Airbnb). Skip any with check-in in the past (the guest is already in-house), and skip anything cancelled or that is an *inquiry* rather than a confirmed booking.

   **PRIMARY PATH — Guesty's internal REST API (added 2026-09-04, use this first).** The `/reservations` grid is unreliable in unattended runs: on 2026-09-04 it never rendered after 60+ seconds and repeatedly froze the Chrome renderer, taking same-origin tabs with it. Instead, load any `app.guesty.com` page, then call Guesty's own REST API in-page (JS injection) using the Okta bearer token already in `localStorage`:
   - Reservations → `/api/reservations-reports`. **Quirk:** it accepts only ONE `columns` value per request — fetch each needed column in its own request and merge on `_id`.
   - Guest conversation threads → `/api/inbox/conversations?type=guest`
   - Message history for a thread → `/api/communication/conversations/<id>/posts`
   Far faster than the UI and does not depend on grid rendering.

   **FALLBACK — the UI.** Only if the API path fails: navigate to `https://app.guesty.com/reservations`. The default "Upcoming Bookings" view already filters status=Confirmed and check-out in the future. Confirm the listing is "Mountain Luxury / Mountain Valley Luxury with Pool and Hot Tub". If the grid has not rendered within ~60 seconds, do NOT keep waiting on it — reload once, then return to the API path.
3. **Classify each candidate via DocuSign API.** For EACH candidate, call `getEnvelopes` with `accountId = 320a0ff8-3001-4e1a-93b4-4fc3004b1116`, `from_date = today - 30 days`, and `search_text = <guest last name>`. Filter to envelopes for the same guest, excluding any with status = `voided`. Classify:
   - **SEND** — no matching non-voided envelope. Proceed to Step 4.
   - **SIGNED** — envelope status is `completed` or `signed`. Nothing to do here; still eligible for Step 6 (VERIFY) if not yet verified.
   - **UNSIGNED** — envelope exists with status in {`sent`, `delivered`, `created`, `signed` (incomplete)}. Proceed to Step 5 for reminder evaluation; still eligible for Step 6 (VERIFY).
4. **SEND phase** — for candidates classified SEND, follow the bald-rock-property skill's Contracts section:
   - VRBO → VRBO Contract template (`c264e23c-5ff7-47eb-b676-fc469048f331`), direct to the guest's real email from Guesty Reservation → Guests. DocuSign MCP `createEnvelope` if available; otherwise the Templates UI fallback.
   - Airbnb → Airbnb Rental Contract template (`cf0bdcb8-4476-4d69-a88c-ba6b605a6034`) via the embedded-link workaround: send to `jdavis@fcfpawn.com` as the placeholder recipient, pull the email from Gmail MCP, extract the signing URL via `charCodeAt`, then post the welcome message + URL into the guest's Guesty conversation thread (`Via Airbnb`).
5. **REMIND phase** — for candidates classified UNSIGNED, compute `days_until_checkin = checkIn.date - today`. If `days_until_checkin <= 3` AND `days_until_checkin >= 0`, send a reminder. Per-channel logic:
   - **VRBO unsigned ≤3 days** — call DocuSign `sendReminder` for the envelope's recipient (recipientId is typically "1" for the Guest role). Use `accountId = 320a0ff8-3001-4e1a-93b4-4fc3004b1116`. Set the reminder email blurb (if supported) to: "Hi <FirstName>, your check-in at Mountain Luxury is on <CheckInDate>. We still need this short rental agreement signed before you arrive — please take a moment to complete it. Let me know if anything's not working. — Joshua"
   - **Airbnb unsigned ≤3 days** — `sendReminder` won't reach the guest (recipient is `jdavis@fcfpawn.com` placeholder). Instead, re-derive the signing URL using the documented pattern `https://www.docusign.net/Signing/EmailStart.aspx?a=<envelopeId>&etti=1&acct=320a0ff8-3001-4e1a-93b4-4fc3004b1116&er=1`. If that shape doesn't work, fall back to re-extracting the URL from the original `dse@docusign.net` Gmail message (search `from:dse@docusign.net <guest name>`) via the `charCodeAt` workaround. Then post into the Guesty conversation thread: "Hi <FirstName>, just a friendly reminder — your stay at Mountain Luxury starts <CheckInDate> and we still need the rental agreement signed before you arrive. You can complete it here: <signingUrl>. Let me know if anything isn't working! — Joshua"
   - Skip reminders for UNSIGNED candidates with `days_until_checkin > 3` (too early to nag). Record them as "watching" in the summary.
6. **VERIFY phase (age/ID, 30+ policy)** — for every candidate from Step 2 (regardless of SEND/SIGNED/UNSIGNED classification):
   - **De-dup check first.** Read the guest's Guesty conversation thread (Airbnb or VRBO channel as applicable). Search for a prior message from Joshua containing the phrase "primary guest to be 30 or older" (the age-verification request). If found, this guest has ALREADY been asked — do not re-send. Instead check whether the guest replied after that message:
     - If the guest's reply (or any later message) affirmatively confirms age 30+ or includes an ID/photo, mark **VERIFIED**.
     - If no guest reply since the request, mark **PENDING** (still waiting).
   - **If NOT found (never asked)** — send the request now, via the same channel as the contract (Guesty thread `Via Airbnb` for Airbnb reservations, or the VRBO guest email/thread for VRBO reservations). Use this message, signed per the standing signature rule (Best, Joshua — no Full Circle Finance Inc branding):
     > "Hi <FirstName>, quick note ahead of your stay at Mountain Luxury on <CheckInDate> — our booking policy requires the primary guest to be 30 or older. Could you reply to confirm, or send a quick photo of your ID? Just need this on file before check-in. Thanks! — Joshua"
   - Mark newly-sent requests as **PENDING** (awaiting reply) in the log.
   - Do NOT send more than one age-verification request per guest, ever — the de-dup check is load-bearing, same discipline as the DocuSign envelope de-dup in Steps 3-4.
7. **Log every guest processed** — date, check-in date, days-until-checkin, channel, action (sent/reminded/watching/signed/failed), envelope ID, reason, AND age-verification status (verified/pending/just-requested).

## Notify

DM Joshua on Slack (his user ID is `U03BB52MDSA`):

> 🏠 Bald Rock contracts (run YYYY-MM-DD)
> Window: <today> → <today+15>
> Candidates scanned: <n>
>
> ✅ Sent: <n> (VRBO: …, Airbnb: …) — name + check-in date
> 🔔 Reminded (unsigned, ≤3 days out): <n> — name + check-in date + envelope ID + status
> 👀 Watching (unsigned, >3 days out): <n> — name + check-in date + days-until + envelope ID + status
> 📝 Already signed: <n> — name + check-in date
> 🪪 Age/ID verification — requested today: <n> names | still pending (asked previously, no reply yet): <n> names | verified: <n> names
> ⚠️ Failed: <list with reason>

If a phase has zero items, still include the line with `0` so Joshua sees the run executed the check, not just a no-op.

## Constraints

- Skip cancelled reservations.
- Skip reservations where check-in is in the past (guest already in-house).
- Never use `zapvp1@me.com` as the placeholder email — Gmail MCP can't read iCloud. Always use `jdavis@fcfpawn.com`.
- Don't add custom tabs/fields — the templates are pre-configured.
- If Guesty login fails, DM Joshua immediately and stop — never send partial contracts under uncertainty.
- When the DocuSign MCP beta access lands, switch to the preferred-path API flows in the bald-rock-property skill (createEnvelope + createRecipientView for embedded URLs) and skip the UI workaround.
- The de-dup check is the single source of truth for "did we already send this?" — do not rely on date-window arithmetic alone. This applies equally to the age-verification request (Step 6) — never send it twice to the same guest.
- **Reminders are once-per-day, max.** The daily cadence + DocuSign's own throttle (a reminder can't fire twice within 24 hours via the API) keep this from spamming guests. Do NOT loop or batch-fire reminders inside a single run.
- If DocuSign's ID Verification add-on pricing/terms change in the future (e.g. a lower-volume tier becomes available), flag it in the run log for Joshua's review — do not switch mechanisms without his sign-off, since it's a purchase decision.

<!-- migrated to working model 2026-06-15 --><!-- age/ID verification step added 2026-08-07 per Joshua's directive to treat it as part of the standing contract workflow after DocuSign IDV add-on was priced out as not worth it -->

---

## Hardening block (added 2026-09-04 — HARDENING_STANDARD.md requirements #2, #3, #4, #5)

**Why this exists.** On 2026-09-04 this task fired on time at 04:06, ran cleanly for five
minutes, then died silently and produced nothing. App log:

    04:11:00 Not auto-approving "mcp__...__listRecipients" in scheduled task
             "bald-rock-15-day-contract": rule(s) not in stored approvals (stored count=4)

It stalled on a tool permission with nobody present to approve it, and the hung-run reaper
killed it before it ever reached the failure-DM step. Root cause is fixed at the registry level
(`Valley Pawn OS/bin/taskperms_registry_edit.py`). The steps below are the second layer, so a
run that goes wrong for ANY other reason still ends loudly instead of silently.

**A. Catch-up on missed windows (requirement #4) — do this BEFORE Step 1.**
Read Joshua's DM channel `D03BHQH5VGT` and look for a message containing
`🏠 Bald Rock contracts (run` dated *yesterday*. If yesterday's summary is absent, the
previous run died — widen nothing and change nothing about the logic (the 15-day window plus
the de-dup guards already make the run self-correcting), but add a line to today's DM:
`↺ Caught up: no summary posted <yesterday's date>` so the gap is visible. Never back-fill by
re-sending contracts — the DocuSign envelope check in Step 3 is the only authority on what was
already sent.

**B. Never stall on a permission prompt (requirement #3).**
If any tool call fails or hangs because a permission was not auto-approved, do NOT wait on it.
Retry once; if it fails the same way, take the documented alternate path and note the substitution
in the run log. Known alternates:
- `listRecipients` unavailable → the Guest role recipientId is `"1"` for these templates; use it.
- DocuSign MCP unavailable entirely → the DocuSign web UI via Chrome (Templates fallback).
- Guesty grid unavailable → the REST API path in Step 2.
A permission stall must never be the reason this task produces no output.

**C. Self-verify output before exiting (requirement #2).**
After sending the Slack DM, read `D03BHQH5VGT` back and confirm a message containing
`🏠 Bald Rock contracts (run <today>)` is actually present. If it is not, retry the DM once.
If it still is not there, the run has FAILED even if every earlier step succeeded — write the
failure to the run log and send the one-line plain-language failure DM. A run that cannot confirm
its own output treats itself as failed.

**D. Duplicate guard on every external write (requirement #5).**
Already load-bearing in Steps 3–6 (DocuSign envelope check; the "primary guest to be 30 or older"
thread scan). Extend the same discipline to the summary DM itself: if a
`🏠 Bald Rock contracts (run <today>)` message is ALREADY in the channel when the run
starts, this task has already completed today — exit without re-sending anything to anyone.

**E. Age-exception guests.** A guest with a documented age exception granted by Joshua in the
thread is logged VERIFIED (with the exception noted), not PENDING — so the 30+ request is never
re-sent to someone he has already cleared. As of 2026-09-04 this applies to Sophia Bozzella
(age 28, exception granted 2026-06-06 and reaffirmed 2026-08-11).
