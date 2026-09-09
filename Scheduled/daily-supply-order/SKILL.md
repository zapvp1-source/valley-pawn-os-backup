---
name: daily-supply-order
description: Tuesday 6 AM — Scan #supply-request for the past week, resolve Amazon product details via browser, and compile structured order data (does NOT add to cart, no Slack notification)
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22; v3 2026-09-08):** If this run fails, errors out, or cannot complete its core work, do NOT message Joshua, Preston, or anyone else, in any medium. Instead append ONE row to the fleet failure ledger `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` (use `mcp__Control_your_Mac__osascript` `do shell script "printf ... >> file"` if file tools cannot reach it) in exactly this form: `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or: yes, <the single thing only Joshua can do>> | OPEN |`. The `fleet-guardian` task reads this ledger twice a day, re-runs whatever is safe to re-run, rolls anything that truly needs Joshua into `Life OS/HUMAN_QUEUE.md`, and sends Joshua at most ONE consolidated plain-language DM per day. Individual tasks never DM about failures. All technical detail goes in the run output/log/STATUS file for the next Claude session to pick up. Never send failure notices to any team channel, store manager, employee, or Preston. FIELD COMMUNICATION RULE (unchanged): anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This v3 supersedes both the v2 one-line-DM rule and any older rule in this file.



> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

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

## Weekly Supply Order — Step 1: Scan & Data Collection (runs Tuesday 6 AM)

Your job is to scan #supply-request for supply requests from the past 7 days, navigate to each Amazon URL in Chrome to resolve product details, and DM Joshua a structured SUPPLY_ORDER_DATA message. You do NOT add anything to the Amazon cart — that happens later during checkout.

---

### STEP 1 — Scan #supply-request

- Use `slack_read_channel` on the #supply-request channel
- Use `oldest` param = epoch seconds for 7 days ago: run `date -d "7 days ago 00:00:00" +%s`
- For each message, capture: message text, sender Slack user ID, timestamp (ts)
- For each message that has a thread, call `slack_read_thread` to read the replies
  - If any thread reply indicates the item was already handled ("already ordered", "I got this", "handled", "ordered", etc.), **skip that item entirely**
- Look up each requester's display name using `slack_read_user_profile` with their Slack user ID

---

### STEP 2 — Categorize each request

For each supply request (that was not already handled in the thread):

1. **Extract the store** — look for store names in the message text: Culpeper, Harrisonburg, Waynesboro, Roanoke, Lexington. If unclear, note as "Unknown Store".
2. **Extract quantity** — default to 1 if not specified
3. **Identify the URL type:**
   - Has an Amazon URL (amazon.com) → proceed to Step 3
   - Has a non-Amazon URL → flag as MANUAL_ITEM with reason "non-Amazon link"
   - Text-only request (no URL) → flag as MANUAL_ITEM with reason "text-only request"

---

### STEP 3 — Resolve Amazon product details via browser

For each item with an Amazon URL:

1. Navigate to the URL using Chrome: `navigate({url})`
2. Read the page to find: product title, current price
3. Extract the ASIN from the URL path (e.g., `/dp/B08XYZ1234`) or from the page
4. Build the canonical URL: `https://www.amazon.com/dp/{ASIN}`
5. If the page is broken, unavailable, or doesn't show a product → flag as MANUAL_ITEM with reason "broken link"

---

### STEP 4 — Build and send SUPPLY_ORDER_DATA to Joshua

Send a single Slack DM to Joshua (user ID: **U03BB52MDSA**) with the following format.

**If there are NO items at all (nothing requested this week):**
```
[SUPPLY_ORDER_DATA — Week of {YYYY-MM-DD}]
NO_ORDERS
[END_SUPPLY_ORDER_DATA]
```

**If there ARE items:**
```
[SUPPLY_ORDER_DATA — Week of {YYYY-MM-DD}]
CULPEPER:
• {Product Title} | {https://www.amazon.com/dp/ASIN} | ${price} | qty:{qty} | {Requester Full Name} | {requester_slack_user_id}
HARRISONBURG:
• {Product Title} | {https://www.amazon.com/dp/ASIN} | ${price} | qty:{qty} | {Requester Full Name} | {requester_slack_user_id}
WAYNESBORO:
• {Product Title} | {https://www.amazon.com/dp/ASIN} | ${price} | qty:{qty} | {Requester Full Name} | {requester_slack_user_id}
ROANOKE:
• {Product Title} | {https://www.amazon.com/dp/ASIN} | ${price} | qty:{qty} | {Requester Full Name} | {requester_slack_user_id}
LEXINGTON:
• {Product Title} | {https://www.amazon.com/dp/ASIN} | ${price} | qty:{qty} | {Requester Full Name} | {requester_slack_user_id}
MANUAL_ITEMS:
• {description or product name} | {Store} | {reason: text-only request / non-Amazon link / broken link} | {Requester Full Name} | {requester_slack_user_id}
[END_SUPPLY_ORDER_DATA]
```

**Formatting rules:**
- Only include store sections that actually have items
- Include the MANUAL_ITEMS section only if there are manual items
- Use today's date (the Tuesday) for "Week of YYYY-MM-DD"
- Send exactly ONE DM — do not send multiple messages
- Do NOT add any items to the Amazon cart

<!-- migrated to working model 2026-06-15 -->