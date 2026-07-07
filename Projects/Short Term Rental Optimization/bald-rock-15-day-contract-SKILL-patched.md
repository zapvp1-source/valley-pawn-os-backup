---
name: bald-rock-15-day-contract
description: Daily 9 AM — for any Bald Rock reservation checking in exactly 15 days from today, send the matching DocuSign rental contract per channel (VRBO direct-to-email, Airbnb via embedded-link in Guesty thread). All operational details live in the bald-rock-property skill's Contracts section. DMs Joshua a Slack summary.
---

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

## Objective

Send the DocuSign rental contract for **282 Bald Rock Road, Verona, VA 24482** to every guest whose check-in is **exactly 15 days from today** in Guesty, including a warm welcome note. Cover both Airbnb and VRBO. DM Joshua a Slack summary when done.

## Authoritative reference — read this first

**`anthropic-skills:bald-rock-property` → "Contracts" section** holds the operational manual: template IDs, channel detection rules, the VRBO direct-email flow, the Airbnb embedded-link-via-Guesty workaround (including the `charCodeAt` URL-extraction bypass that's required when the Gmail MCP plaintext URL is mangled), de-duplication rules, voiding procedure, and the welcome-message copy. Treat that section as the source of truth — this prompt is only the orchestration layer around it.

Also relevant: the **"Looking up reservation data in Guesty"** subsection for navigating Guesty to find each guest's name, email, conversation thread, and channel.

## Prerequisite — DocuSign MCP must be working

Before doing anything else, call `mcp__8ff1eb8f-1c43-4cbb-bcb3-9167c3c96cc7__getAccount` against `320a0ff8-3001-4e1a-93b4-4fc3004b1116` once to verify the DocuSign MCP is reachable. If it errors, DM Joshua and stop — do NOT fall through to the UI Templates page silently.

## Run

1. **Compute target date** — `today + 15 days` in Joshua's local timezone (`YYYY-MM-DD`).
2. **Pull matching reservations from Guesty.** Open Chrome, navigate to `https://app.guesty.com/reservations`. Filter to status=Confirmed, listing="Mountain Luxury / Mountain Valley Luxury with Pool and Hot Tub". Capture every reservation whose `checkIn` falls on the target date. Record: confirmation code, full guest name, guest email (may be empty/`--` for Airbnb), check-in datetime, channel.
3. **De-dupe** — query the DocuSign MCP `getEnvelopes` with `from_date = today - 30 days`, then call `listRecipients` on any envelope whose subject contains "Mountain Luxury" or "Bald Rock". Skip if a non-voided envelope to the same guest name already exists. (UI fallback: `apps.docusign.com/send/documents?view=sent`.)
4. **Send contracts** following the bald-rock-property skill's Contracts section:
   - **VRBO matches** → VRBO Contract template via DocuSign MCP `createEnvelope`, direct to the real guest email captured in step 2. The MCP path is preferred over the Templates UI fallback — it's faster and idempotent.
   - **Airbnb matches** → real email FIRST, workaround only as fallback:
     - **(a) Check the Guesty conversation thread for a real email FIRST.** Open the inbox conversation, read messages. Guests frequently volunteer their real email + phone in reply to the booking-confirmation automation ("My email is X, phone is Y"). If a real email exists, send the Airbnb Contract template directly to that email via `createEnvelope` — same flow as VRBO. **This is dramatically more reliable than the placeholder workaround and must always be tried first.**
     - **(b) Only if no real email is in the thread**, fall through to the placeholder workaround: send to `jdavis@fcfpawn.com` (the documented placeholder — see Constraints), then pull the DocuSign email via Gmail MCP `search_threads` + `get_thread`. The `plaintextBody` field usually contains a clean signing URL; only if the URL is mangled does the `charCodeAt` Chrome bypass apply. Then post the welcome message + URL into the guest's Guesty conversation thread (`Via Airbnb`).
5. **VERIFY THE GUESTY THREAD POST COMPLETED** — for every Airbnb fallback (b) send, the run is NOT complete until you have confirmed the message appears as a "Joshua Davis" / "Via Airbnb" entry in the conversation (re-read the conversation after Send and check for the just-posted message). If the post step errored, void the envelope via `updateEnvelope` and DM Joshua to handle manually. **Do NOT mark the guest as "sent" just because the envelope was created** — the envelope without the URL delivery is useless to the guest.
6. **Log every guest processed** — date, target check-in date, channel, contract method (`vrbo-direct` / `airbnb-direct-from-thread` / `airbnb-placeholder-via-guesty`), envelope ID, AND the verification status of the Guesty thread post (where applicable), success/failure with reason.

## Notify

DM Joshua on Slack (his user ID is `U03BB52MDSA`):

> 🏠 Bald Rock 15-day contracts (run YYYY-MM-DD)
> Target check-in: <date>
> ✅ Sent: <n> (VRBO: …, Airbnb direct: …, Airbnb via Guesty thread: …)
> ⏭ Skipped (already sent): <list>
> ⚠️ Failed: <list with reason>

If zero matches, post: "No Bald Rock contracts due today (no check-ins on YYYY-MM-DD)."

## Constraints

- Skip cancelled reservations.
- **NEVER use fake placeholder addresses like `<guest>.<initials>.baldrock@placeholder.com` or any address on a non-existent domain.** The May 4 batch did this and 11 guests never received their contracts because the DocuSign email went into a black hole AND the workaround Guesty thread post step was skipped. The ONLY acceptable placeholder is `jdavis@fcfpawn.com` (the documented Gmail address Joshua actually owns and can read).
- Never use `zapvp1@me.com` as the placeholder email — Gmail MCP can't read iCloud. Always use `jdavis@fcfpawn.com`.
- Don't add custom tabs/fields — the templates are pre-configured.
- If Guesty login fails (Google SSO callback hang has happened repeatedly), DM Joshua immediately and stop — never send partial contracts under uncertainty. The May 9–22 run window had 14 consecutive days of SSO failures; do not let that recur silently.
- When the DocuSign MCP beta access for `createRecipientView` lands, fall through to the preferred-path API flows in the skill (createEnvelope + createRecipientView for embedded URLs) and skip the UI/Gmail workaround entirely.

## Change log

- **2026-05-23** — Patch following the audit Joshua requested. Added prerequisite MCP-health check; added explicit "check Guesty thread for real email FIRST" rule for Airbnb; added mandatory verification of the Guesty thread post step; explicitly forbid `*@placeholder.com` fake emails; added SSO-fail loudness; recorded the May 4 fake-email batch + May 9–22 SSO-fail history as cautionary background.
