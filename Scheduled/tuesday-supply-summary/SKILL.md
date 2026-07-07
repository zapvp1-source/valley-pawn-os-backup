---
name: tuesday-supply-summary
description: Tuesday 10 AM — Read the 6 AM order data from Joshua's DM history, format it, and either auto-approve (total < $350) or DM Joshua asking him to reply 'order' to confirm or 'skip' to cancel
model: claude-sonnet-5
---


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

## Weekly Supply Order — Step 2: Summary & Auto-Approval Gate (runs Tue 10 AM)

---

### STEP 0 — Re-enable the checkout task

Before doing anything else, call `update_scheduled_task` with `taskId: "tuesday-supply-checkout"` and `enabled: true`.

This re-arms the checkout watcher for this week's order cycle.

---

### STEP 1 — Read SUPPLY_ORDER_DATA from Joshua's DMs

- Read Joshua's DMs using `slack_read_channel` with channel_id = **U03BB52MDSA**
- Use `oldest` param = start of today (midnight) in epoch seconds: `date -d "today 00:00:00" +%s`
- Find the message containing `[SUPPLY_ORDER_DATA —`
- Parse all items between `[SUPPLY_ORDER_DATA —` and `[END_SUPPLY_ORDER_DATA]`
- For each bullet point under a store heading, extract:
  - Product title
  - Amazon URL
  - Price
  - Quantity (the number after `qty:`)
  - Requester full name
  - Store name (from the section heading)
- Note any MANUAL_ITEMS separately
- If no SUPPLY_ORDER_DATA is found: DM Joshua "⚠️ The 6 AM supply scan doesn't appear to have run yet (or found no requests). Check #supply-request or run the scan manually." Then stop.

---

### STEP 2 — Compute total and branch on the $350 auto-order threshold

Compute the estimated total: `Σ (price × qty)` across every Amazon-orderable item (skip MANUAL_ITEMS in the total).

**Threshold rule:** orders under **$350.00** are AUTO-APPROVED — no Joshua confirmation required. Orders at or above $350 still go through the manual "reply order/skip" gate.

Branch on the total:

**A) If total < $350 → AUTO-APPROVE (no confirmation needed):**

DM Joshua (channel_id = **U03BB52MDSA**) with this format. The `[AUTO_ORDER_APPROVED —` marker is the trigger the checkout task watches for:

```
📦 *Weekly Supply Order — Auto-Approved* (under $350 threshold)

[AUTO_ORDER_APPROVED — {YYYY-MM-DD}]

*{STORE NAME}:*
• {Product title} (qty {qty}) — ${price} — requested by {Requester Name}
[repeat per store, omit stores with no items]

*Estimated Total: ${sum}* ({item count} items) — under $350, placing automatically. Next supply-checkout run (≤15 min) will add to cart and check out.
```

If there are MANUAL_ITEMS, append at the bottom:
```
⚠️ *Manual Items (not on Amazon — action needed):*
• {item description} — {Store} — {Requester Name}
```

Then **stop** — the checkout task will pick up the `[AUTO_ORDER_APPROVED —` marker on its next 15-min run and execute the order without further confirmation.

**B) If total ≥ $350 → ASK FOR CONFIRMATION (existing behavior):**

DM Joshua (channel_id = **U03BB52MDSA**) with this format:

```
📦 *Weekly Supply Order — Ready for Review*

Here's what came in from #supply-request this week:

*{STORE NAME}:*
• {Product title} (qty {qty}) — ${price} — requested by {Requester Name}
[repeat per store, omit stores with no items]

*Estimated Total: ${sum}* ({item count} items) — above the $350 auto-order threshold, needs your confirmation.

Reply _order_ to confirm and I'll add everything to the cart and check out within 15 minutes. Reply _skip_ to cancel this week's order.
*Sent using* Claude
```

If there are MANUAL_ITEMS, append at the bottom (same format as branch A).

---

### IMPORTANT NOTES

- Always complete Step 0 (re-enable checkout task) before anything else, even if no order data is found
- The $350 threshold applies to the Amazon-orderable items total only — manual items don't count toward it
- The `[AUTO_ORDER_APPROVED —` marker is the trigger for the checkout task; do NOT include it in the ≥$350 branch (that branch waits for Joshua's "order" reply)
- Do not send anything to #supply-request or other channels — DM Joshua only
- The estimated total is the sum of all item prices × quantities

<!-- migrated to working model 2026-06-15 -->