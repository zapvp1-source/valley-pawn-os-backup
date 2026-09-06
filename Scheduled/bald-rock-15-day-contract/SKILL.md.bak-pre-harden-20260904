---
name: bald-rock-15-day-contract
description: Daily 9 AM — scan every Bald Rock reservation checking in within 15 days. (1) Send contract if missing, (2) remind if unsigned ≤3 days out, (3) send age/ID (30+) verification request alongside every new contract and track replies — manual workaround, DocuSign IDV add-on not purchased (cost doesn't justify volume). DMs Joshua a Slack summary.
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.

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
2. **Pull candidate reservations from Guesty.** Open Chrome, navigate to `https://app.guesty.com/reservations`. The default "Upcoming Bookings" view already filters status=Confirmed and check-out in the future. Confirm the listing is "Mountain Luxury / Mountain Valley Luxury with Pool and Hot Tub". Capture every reservation whose `checkIn` date falls anywhere from today through today+15 (inclusive). For each, record: confirmation code, full guest name, check-in datetime, channel (VRB-… = VRBO; HM… = Airbnb). Skip any with check-in in the past (the guest is already in-house).
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
