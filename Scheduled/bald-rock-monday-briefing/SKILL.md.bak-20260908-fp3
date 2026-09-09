---
name: bald-rock-monday-briefing
description: Monday 8 AM weekly Bald Rock STR briefing — bookings, gap nights, pricing flags, age/ID verification status, action items → Slack #airbnb
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.



## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

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
You are running the weekly Bald Rock briefing for Joshua Davis. Property: 282 Bald Rock Road, Verona VA — "Mountain Luxury / Mountain Valley Luxury with Pool and Hot Tub" — listed on Airbnb and VRBO, channel-managed in Guesty.

GOAL
Post a TIGHT one-screen Slack message to channel C0B10UG937H (#airbnb).

FAILURE / DEGRADATION POLICY (read first)
- CORE source = Guesty (the reservation list). If Guesty itself is fully unreachable, post NOTHING to Slack and end the run silently (Joshua reviews every run inside Claude). Do NOT post error lines or partial-failure notices to Slack.
- NON-CORE sources = DocuSign, and each booking channel's payment page (Airbnb earnings / VRBO supply portal). A single non-core source being unreachable must NEVER abort the whole briefing. Recover via the resilient paths below; if you still cannot get it, POST THE FULL BRIEFING and mark only the affected line as "channel status: unverified — <source> unreachable 🚨". One dead link must not kill the briefing.
- SELF-HEAL: URLs drift. Always try the documented URL, then the discovery path. If you find a corrected/working URL for any source, note it at the END of the run inside Claude (not Slack) as: "🔧 URL DRIFT — <source> now lives at <url>; update the task." so the task can be healed.

DATA SOURCES
1. Guesty (reservation list + inbox) — `https://app.guesty.com/reservations?status=confirmed`. Log in with **email + password** as `fullcirclepawn@gmail.com` (NOT Google SSO, NOT jdavis@fcfpawn.com — that misdirection broke prior tasks May 9–22). Filter to Mountain Luxury, status=Confirmed, check-out in future. Use Guesty for: list of upcoming reservations, nights, ANR, payout amount, conversation thread (to verify automated messages fired AND to check age/ID verification reply status — see below), and the guest's phone field (load-bearing — see Lockbox check). To read a reservation's financials/phone: click the row → Overview shows payout + ANR; Guests tab shows phone; "Open in inbox" opens the conversation thread.
2. DocuSign MCP — `getEnvelopes` from last 21 days, account `320a0ff8-3001-4e1a-93b4-4fc3004b1116`. status=completed means signed; status=sent means sent-but-not-signed; status=voided means superseded (ignore, look for a later envelope to the same guest).
3. **Payment status comes from the BOOKING CHANNEL, not Guesty.** Guesty's "Paid / Balance Due / Not Paid" field is unreliable for Airbnb and VRBO because those platforms collect the guest's money and pay the host directly, bypassing Guesty. Pull the truth from:
   - **Airbnb reservations** (codes start with `HM`): live earnings page is `https://www.airbnb.com/earnings` → **Upcoming** and **Paid** tabs (the old `/hosting/earnings/transaction-history` path 404s — don't rely on it). Match the row by amount + payout date; report status (Scheduled for <date> / Paid out on <date> / Past) and amount. Alternate path: open `https://www.airbnb.com/hosting/stay/<HMcode>` → "$X Total for N nights" card → **View earnings**.
   - **VRBO reservations** (codes start with `VRB-`): live owner portal is **`https://www.vrbo.com/supply/home?propertyId=119604391`**. The old `/lodge-host/reservations` path is DEAD (404) and the account-menu "Owner Dashboard" link redirects through a logout back into that dead path — do NOT use either. From the supply dashboard, open the guest under **"Your guests"** (or **Inbox** → the reservation); the right-side panel shows **"Expected payout for N nights"** (net host payout), the Res ID (e.g. HA-G14CTK), and "Booked through Vrbo on <date>", and the thread logs "Guest made a payment" events. Left-nav **Payments → Payment history** is only a CSV export of PAST payouts — for an upcoming reservation use the per-guest panel. VRBO releases the host payout ~1 day after check-in, so before check-in report "VRBO expected payout $X — releases after check-in"; after check-in report it released/processing.
4. Read the `bald-rock-property` skill for property facts.

OUTPUT FORMAT — strict. Slack mrkdwn. Post a single message to channel_id C0B10UG937H with exactly these sections:

*Bald Rock Weekly Briefing — Week of <Monday date>*

*Next 14 days*
• <First name Last initial> — <check-in date> → <check-out date> (<n>n, <Airbnb|VRBO>) — <in-house | upcoming> — contract sent <✅|⏳> signed <✅|⏳>
(One line per reservation. If none, say "No bookings in next 14 days.")

*Same-day check-in / check-out this week*
• <Any same-day turnovers between Monday and Sunday. If none, write "None" with check-out / next-check-in gap context.>

*Revenue this week*
• <For each in-house or checking-in-this-week reservation:>
  <First name + last initial> — payout $X (Yn × $Z ANR) — *channel status: <Paid out on YYYY-MM-DD | Scheduled for YYYY-MM-DD | VRBO expected payout $X, releases after check-in | Pending | unverified — <source> unreachable 🚨>* (source: <Airbnb earnings | VRBO Payments>)
  (Do NOT use the Guesty "Paid / Not Paid" field — unreliable for Airbnb/VRBO.)

*Automated messages*
<One liner. ONLY after actually reading the Guesty inbox thread for each in-house and same-week-check-in guest. Confirm whether the automated messages (Booking Confirmation, Check-in Instructions, Arrival Welcome, How is everything?, Check-out Instructions) fired on schedule. Flag exceptions — e.g. late bookings where Check-in Instructions could not fire because booking-to-check-in < 5 days.>

*Age/ID verification (30+ policy)*
<For every reservation in the "Next 14 days" list, read the Guesty conversation thread and check for the age-verification request (a prior message containing "primary guest to be 30 or older") and any guest reply since. Classify each guest as VERIFIED (guest replied confirming 30+ or sent ID), PENDING (request sent, no reply yet), or NOT YET ASKED (should not normally happen — the daily bald-rock-15-day-contract task sends this alongside every new contract — flag as a gap if found).
Report as:
✅ Verified: <n> — names
⏳ Pending (asked, no reply): <n> — names + how many days since asked
🚨 Not yet asked: <n> — names (flag as a process gap if any)
If all guests in the next 14 days are verified, write "All upcoming guests verified ✅".
This is a manual workaround (DocuSign's ID Verification add-on was priced out 2026-08-07 as not worth it at Bald Rock's booking volume — $75/mo minimum for 30 verifications/month). Treat this section with the same weight as the contract sent/signed columns — Joshua wants to know by name who hasn't confirmed, every week, without having to ask.>

*Lockbox check (next 7 days)*
<One liner per upcoming guest checking in within 7 days. The Arrival Welcome message sends the guest's 10-digit phone as the lockbox code (drop the +1). Verify each upcoming guest's phone field is populated and valid +1XXXXXXXXXX. If missing/malformed, flag with 🚨 and the guest name — Joshua must reset the touchpad lockbox to match. If all good: "All upcoming guests have phone on file ✅".>

— auto-brief

RULES
- channel_id: C0B10UG937H
- NO pricing flags, NO commentary on contracts beyond sent/signed status, NO door codes, NO Wi-Fi passwords, NO guest emails or phone numbers (first name + last initial only).
- Under 1800 characters total (raised slightly from 1500 to fit the new Age/ID Verification section — keep every section as tight as possible to stay close to the original budget).
- You MUST verify automated messages fired by reading the Guesty inbox — do not assert without checking.
- You MUST pull payment status from Airbnb/VRBO (per the resilient paths above), not Guesty.
- For the Lockbox check, you MUST check the actual phone field on each upcoming reservation in Guesty's Guests tab.
- For the Age/ID verification section, you MUST actually read each guest's Guesty thread — do not assume verified without seeing a reply.
- Follow the FAILURE / DEGRADATION POLICY above: stay silent only if Guesty (core) is down; for any single non-core source, degrade gracefully, post the full briefing, and flag the one affected line. Never hard-abort the whole briefing over one source.

<!-- migrated to working model 2026-06-15 --><!-- Age/ID verification section added 2026-08-07 per Joshua's directive: treat age verification like the contract workflow, weekly scan, report who hasn't sent ID, attached to this weekly update -->
