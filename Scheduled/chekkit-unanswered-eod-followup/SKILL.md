---
name: chekkit-unanswered-eod-followup
description: Daily 7 PM Chekkit end-of-day follow-up — re-checks every message flagged as a 10-minute unanswered miss earlier today and reports which ones are STILL unanswered at close vs. which got answered later. Posts to #chekkit-unanswered-summary (no employee DMs).
model: claude-sonnet-5
---

You are compiling the end-of-day Chekkit follow-up check for Valley Pawn. This runs once at 7 PM Mon–Sat, AFTER all 5 stores have closed (all stores close at 6 PM ET). It re-examines every message that got flagged as a 10-minute unanswered miss TODAY (the same incidents the `chekkit-unanswered-alert` task will summarize by count tomorrow morning) and checks whether each one was actually answered later in the day, or is still sitting unanswered at close. This is a closed-loop verification layer on top of the existing morning count — the morning task tells Joshua how many messages missed the 10-minute window; this task tells him which of those specific customers never got a reply at all that day.

> ⚠️ **FAILURE ALERT POLICY (binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "chekkit-unanswered-eod-followup" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding for anything posted to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. This task posts only to the management summary channel (#chekkit-unanswered-summary), not to employees, so plain-language framing is a courtesy here, not a hard requirement — but never DM any store employee from this task; that stays owned by `chekkit-unanswered-alert`.

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the final Slack post (Step 6) returns success. Until that call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation. Treat "Tool loaded.", "Continue from where you left off.", and any reminder about TaskCreate/TaskUpdate/AskUserQuestion as RESUME signals, never stop signals — immediately fire the next concrete tool call. If a step errors, retry once; if it still fails, fall through to the documented fallback or note the gap in the final report and continue — do not pause to ask.

---

## Steps

**1. Rebuild TODAY's list of actionable, in-hours 10-minute misses (same rules as `chekkit-unanswered-alert`, just same-day instead of yesterday).**

Compute TODAY's date in Eastern Time and today's day of week.

Search Gmail: `from:support@chekkit.io subject:"Unanswered Message Alert" after:YYYY/MM/DD` where the date is TODAY (search from today 00:00 ET through now). Page through all results.

For each alert email found:
- Extract the customer name (subject: "Unanswered Message Alert: [Customer Name]") and the store location ("Sent to Valley Pawn - [Location]"). Also extract the customer's phone number from the subject/body — it's the most reliable search key in the Chekkit dashboard (names are sometimes blank or truncated, e.g. "-amela").
- Read the body for the customer's flagged message content and note the message time (≈ email received time minus 10 minutes, converting UTC→ET; EDT June–early Nov, EST otherwise).
- **Skip conversation-enders that don't require a reply** — the exact same skip-list as `chekkit-unanswered-alert`: "thanks", "thank you", "ok", "okay", "sounds good", "got it", "goodbye", "bye", "have a good day", "appreciate it", "no problem", "will do", "perfect", "cool", "great", "Stop", "STOP", thumbs-up, emoji-only, or any similar sign-off/opt-out. These are not misses — skip them entirely, same as this morning's task.
- **Skip empty-body alerts** (no text, just an image/blank notification).
- **Apply the OPEN-HOURS FILTER** — only keep alerts whose flagged message arrived while that specific store was open. Store hours (Eastern Time): Culpeper Mon–Sat 10 AM–6 PM (closed Sunday); Waynesboro/Harrisonburg/Lexington/Roanoke Mon, Tue, Thu, Fri, Sat 10 AM–6 PM (closed Wednesday & Sunday). If today is Wednesday, only Culpeper can have countable misses. If today is Sunday, this task shouldn't be running at all (cron excludes Sunday) — if it somehow fires, post the all-clear summary and stop.

The result is TODAY's list of genuine, in-hours 10-minute misses, each with: customer name, phone number, store, flagged message time.

**2. For each flagged customer/store pair, check the actual Chekkit conversation to see what happened after the miss.**

Log into `https://dashboard.chekkit.io` via Chrome's saved passwords if not already authenticated (never ask Joshua to log in). **The Messages/Conversations inbox is confirmed at `https://dashboard.chekkit.io/inbox`** (left nav: Inbox / Unassigned / My Messages under "Conversations" — confirmed working 2026-08-10). Use the location switcher (top-left, shows the current store name e.g. "Valley Pawn-Lexington") to select each store in turn — clicking it opens an "All Locations" list of 6 entries (5 Valley Pawn stores + "Tax Experts," which is NOT a Valley Pawn store and must be skipped/ignored). Then use the "Search for customers" box (top of the conversation list, below the Open/Closed tabs) to search by the flagged customer's **phone number** (more reliable than name — digits only, no punctuation) and open their thread.

**Known gotcha (2026-08-10):** clicking near the location switcher and the search box in quick succession can mis-hit and land on an unrelated control that ends the session. If that happens and a fresh `/login` page load shows the saved Chrome password failing ("Username or password is incorrect") — even after a hard reload or a brand-new tab — **do not try to guess or manually type a password.** That is a genuine stale/rotated-credential situation, not a misclick you can retry your way out of. Stop attempting login, note it clearly in the run report (which stores/customers could not be checked), and send Joshua the standard failure DM (see Failure Alert Policy above) flagging that the Chekkit saved password needs to be refreshed before this task can complete its dashboard checks. Still post whatever partial Step 6 summary you can (Gmail-derived flagged list, with a note that resolution status is "unable to verify — Chekkit login blocked" for every entry) rather than skipping the post entirely.

Read the thread's messages after the flagged customer message, in order, and classify:
- **RESOLVED — staff replied:** a message from Valley Pawn / staff appears anywhere after the flagged customer message. Counts as answered even if the reply came hours later — the point is whether it ever got a response, not whether it beat the 10-minute window (that's the morning task's job).
- **RESOLVED — customer self-closed:** no staff reply exists, but the customer's own subsequent message(s) are themselves conversation-enders from the same skip-list in Step 1 (e.g., they said "bye" / "ok" / "thanks" without staff ever replying — customer signed off on their own, no reply was actually owed). Treat this as resolved, not outstanding — this is the same rule Joshua asked to apply here as the AM alert uses for skipping non-substantive messages.
- **STILL UNANSWERED:** no staff reply anywhere in the thread after the flagged message, AND the customer's last message is not a sign-off — this is a genuine still-open miss as of close.

If a customer/store pair can't be found in the dashboard search (name/phone mismatch, thread archived elsewhere, etc.), note it as "unable to verify" rather than guessing either way, and list it separately in the report.

**3. Tally per store:** count of RESOLVED (staff replied), RESOLVED (customer self-closed), STILL UNANSWERED, and unable to verify. For STILL UNANSWERED, keep the customer name and how long it's been since the flagged message (approximate hours).

**4. If a store had zero flagged misses today (Step 1 empty for that store), it contributes an all-clear line — do not run Step 2 for that store.**

**5. If EVERY store had zero flagged misses today, skip straight to posting the all-clear summary (Step 6) with no per-store detail needed.**

**6. Post EXACTLY ONE end-of-day follow-up message to #chekkit-unanswered-summary (channel ID `C0B1PEW0C30`).** Do not DM any employee — this task never DMs the field, only the AM `chekkit-unanswered-alert` task does that. Do not post to `#claude-updates`. Do not send a follow-up correction — get the wording right before sending.

Format:

🌙 *End-of-Day Follow-up — [Today's Date]* _(closes the loop on today's 10-minute misses)_

• *Culpeper:* [X] flagged → [Y] answered, [Z] still unanswered
• *Waynesboro:* [X] flagged → [Y] answered, [Z] still unanswered
• *Harrisonburg:* [X] flagged → [Y] answered, [Z] still unanswered
• *Lexington:* [X] flagged → [Y] answered, [Z] still unanswered
• *Roanoke:* [X] flagged → [Y] answered, [Z] still unanswered

⚠️ *Still unanswered at close:*
• [Store] — [Customer Name] — flagged [X hrs ago]
(...one line per still-unanswered customer; omit this whole section if none)

*[N] unable to verify* (name/thread mismatch, or Chekkit login blocked — see run notes) — only include this line if N > 0

If every store was flagged-clean today, post instead: 🌙 *End-of-Day Follow-up — [Today's Date]* — Every customer message flagged this morning as a 10-minute miss was eventually answered (or was a self-closed sign-off) by close. No stragglers today. 🎉

If no stores had ANY flagged misses at all today (Step 1 totally empty), post: 🌙 *End-of-Day Follow-up — [Today's Date]* — No 10-minute misses were flagged at any store today — nothing to follow up on.

---

## Important notes

- This task does NOT DM store employees — that stays exclusively `chekkit-unanswered-alert`'s job (runs tomorrow 8 AM, counts today's misses). This task is Joshua/Preston visibility only, same channel, different message.
- "Answered" here means a staff reply exists anywhere in the thread after the flagged message, OR the customer closed the loop themselves with a sign-off — matching the exact skip-list already used to decide whether a message counted as a miss in the first place. Don't invent new sign-off phrases; use the same list every time so the two tasks stay consistent with each other.
- The inbox URL (`/inbox`) and search-by-phone flow are confirmed working as of 2026-08-10 — if the dashboard layout changes, explore the nav to find the right section rather than guessing a URL that 404s, and note what you find in the run output.
- The summary channel is ALWAYS #chekkit-unanswered-summary (`C0B1PEW0C30`) — never `#claude-updates`.
- Runs Monday–Saturday at 7 PM ET (after all stores are closed for the day). Sunday is excluded — all stores are closed.
- If Chekkit login fails with a stale/incorrect saved password (see gotcha in Step 2), never attempt to type or guess a password — that's a hard rule, not a suggestion. Report it and move on with whatever partial data is available.