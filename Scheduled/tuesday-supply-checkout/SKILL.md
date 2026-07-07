---
name: tuesday-supply-checkout
description: Tuesdays 10 AM–6 PM every 15 min — Self-determining checkout. Reads SUPPLY_ORDER_DATA directly, computes the total, and auto-places orders under $350. Multi-address checkout, sets REQUIRED per-store Location tag (accounting), Amex 3001.
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

## Weekly Supply Order — Self-Determining Checkout (runs every 15 min, Tue 10 AM–6 PM)

Your job: read SUPPLY_ORDER_DATA from Joshua's DMs, decide whether to place the order based on the total, then add all items to the Amazon Business cart and complete a multi-address checkout — all in the same browser session.

**Decision rule (no dependency on any other task or marker):**
- If SUPPLY_ORDER_DATA total < **$350** → **place the order now**, no confirmation needed
- If total ≥ $350 → only proceed if Joshua replied "order" in DMs today
- If Joshua replied "skip" → stop for today

This is the only task that drives the weekly supply order. It does NOT wait for any marker from `tuesday-supply-summary`. If that summary task posts something, fine. If it doesn't, this task still places the order.

---

### STEP 1 — Idempotency check (do this FIRST)

- Read Joshua's DMs: `slack_read_channel` with channel_id = **U03BB52MDSA**, `oldest` = start of today (midnight) in epoch seconds: `date -d "today 00:00:00" +%s`
- Look for a message containing `[ORDER_CONFIRMED —` from today
- If found: an order was already placed today → **stop silently** (do not place a second order, do not post anything)

---

### STEP 2 — Read SUPPLY_ORDER_DATA and compute total

- In the same DM history from today, find the message containing `[SUPPLY_ORDER_DATA —`
- Parse all items between `[SUPPLY_ORDER_DATA —` and `[END_SUPPLY_ORDER_DATA]`
- For each bullet point under a store heading, extract:
  - Product title
  - Amazon URL (the `https://www.amazon.com/dp/...` link)
  - Price
  - Quantity (the number after `qty:`)
  - Requester full name
  - Requester Slack user ID (the `U0...` code)
  - Store name (CULPEPER, HARRISONBURG, WAYNESBORO, ROANOKE, or LEXINGTON)
- Compute `total = Σ (price × qty)` across Amazon-orderable items (skip MANUAL_ITEMS)
- Note any MANUAL_ITEMS separately (mentioned in the final DM, not ordered via Amazon)
- If no SUPPLY_ORDER_DATA is found in today's DMs: **stop silently** — the 6 AM scan task hasn't posted yet (or there were no requests). Next 15-min run will check again.

---

### STEP 3 — Decide whether to place the order

- If `total < 350.00` → **GO**. Proceed to Step 4. No Slack post needed before placing.
- If `total >= 350.00`:
  - Look for a Joshua message in today's DMs containing the word "order" (case-insensitive, standalone word — ignore "ordered", "reordered", etc., and ignore the bot's own confirmation message)
  - If found → **GO**. Proceed to Step 4.
  - Look for a Joshua message containing the word "skip" (case-insensitive)
  - If found → **stop silently** for today
  - Otherwise → **stop silently**. Next 15-min run will check again.

If proceeding to Step 4, you do NOT need to post a "starting checkout" message — just go.

---

### STEP 4 — Add all items to Amazon Business cart

For each item in SUPPLY_ORDER_DATA (skip MANUAL_ITEMS):

1. Navigate to the product page: `navigate("{amazon.com/dp/ASIN URL}")`
2. Wait 3 seconds for the page to fully load
3. If quantity > 1: use `find` to locate the **Quantity dropdown** (one-time purchase combobox), then `form_input` with `value: "{qty}"` to set it
4. Take a `screenshot` to locate the yellow "Add to cart" button visually
5. Click the Add to Cart button using **coordinate click** (`computer.left_click` with `coordinate: [x, y]` from the screenshot) — see CRITICAL NOTE below about why ref-based clicks fail
6. Wait **5 seconds** after the click — Amazon needs time to process the cart submission before you navigate away
7. Verify the cart count icon in the top-right incremented before moving on. If it didn't increment, scroll up, re-screenshot, and retry the coordinate click

Repeat for all items. All items must be added before proceeding to checkout.

⚠️ **CRITICAL — coordinate clicks beat ref clicks for Add to Cart:** Amazon's anti-automation will silently swallow `left_click` calls dispatched via `ref` IDs on Add-to-Cart buttons — the form submits but the cart never updates. Coordinate clicks (real mouse events) work reliably. Always: screenshot → identify yellow "Add to cart" button → coordinate click → wait 5s before navigating away.

⚠️ **CRITICAL — bulk-add URLs don't work:** Do NOT try `/gp/aws/cart/add.html?ASIN.1=...` — Amazon shows a "Cart is empty / Go To Cart" interstitial and items don't actually get added. Use the per-product approach above.

---

### STEP 5 — Clean up the cart

1. Navigate to `https://www.amazon.com/gp/cart/view.html`
2. Wait 3 seconds, then screenshot
3. **Verify item count and subtotal** — the cart subtotal should be roughly the sum of your SUPPLY_ORDER_DATA prices (Amazon Business may have a different price than the 6 AM scan grabbed — small drift is OK)
4. **Deselect any pre-existing items** that aren't part of this week's order: scroll through the cart, find any item NOT in SUPPLY_ORDER_DATA, and **uncheck its checkbox** (don't delete — Joshua may want it later). Joshua often has saved-for-later/parked items in the cart
5. Confirm the subtotal in the right-hand panel now shows only your supply items (e.g. "(10 items): $188.63")

---

### STEP 6 — Proceed to checkout and select multi-address shipping

1. Click **Proceed to checkout** in the right panel
2. Amazon may show a "Need anything else?" upsell page — click **Continue to checkout** to skip
3. On the main checkout page, find and click **"Deliver to multiple addresses"** (link is below the default delivery address block)
4. You should land on a multi-address item assignment page (URL contains `itemselect`)

---

### STEP 7 — Assign per-store shipping addresses

For each item row, click the address dropdown and select the right store from the visible label text. Joshua has these store addresses saved in his Amazon Business account (visible labels):

- **CULPEPER** → "Valley Pawn Culpeper" (571 JAMES MADISON HWY STE C, CULPEPER, VA)
- **HARRISONBURG** → "Team valley pawn Harrisonburg" (1790 E MARKET ST, HARRISONBURG, VA)
- **WAYNESBORO** → "Valley Pawn Waynesboro" (1321 W BROAD ST, WAYNESBORO, VA)
- **ROANOKE** → "Valley Roanoke (Gold N Pawn)" (2362 PETERS CREEK RD NW STE C, AND D, ROANOKE, VA)
- **LEXINGTON** → "Team valley pawn lexington" (125 WALKER ST, LEXINGTON, VA)

**How to set each address:**
1. Take a screenshot to see the current item list
2. Click an item's address dropdown (it currently reads "Joshua Davis, 844 Cypress …")
3. The dropdown opens — coordinate-click the matching store label
4. Wait ~5 seconds for "Updating your order" to finish — the list will reshuffle (the just-assigned item moves down, the next un-assigned item floats up)
5. Re-screenshot, then repeat for the next item

⚠️ **The page re-renders after every selection** — refs go stale fast. Identify each dropdown by its visual position in a fresh screenshot, not by stored ref IDs.

⚠️ **The list reorders after each change** — what was at position 1 may be at position 4 next. Always read the current list, then click the dropdown for the FIRST item that still shows "Joshua Davis, 844 Cypress …".

Continue until every item shows a store address. Click **Continue** in the right panel.

---

### STEP 7B — Set the Location field (store, for accounting) — REQUIRED, must be set

As of 6/18/2026 the Amazon Business account has a **REQUIRED** "Location" business-order field — a dropdown with six values: **Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke, Corporate**. Because it is required, **the order will NOT place until every required Location field is set.** It tags each order with its store for QuickBooks accounting (flows into the Business Analytics "Location" column and onto invoices). Set it to match each shipment's ship-to store.

1. After assigning addresses (Step 7) and continuing, look on the checkout/review page for **"Location"** order-information dropdown(s). Amazon surfaces required business-order fields on the review page — for a multi-address order, **usually once per ship-to group/shipment**.
2. For each Location dropdown, select the store that matches that block's ship-to address — same store mapping as Step 7 (Culpeper→Culpeper, Waynesboro→Waynesboro, Harrisonburg→Harrisonburg, Lexington→Lexington, Roanoke→Roanoke). If a block ships to a non-store address (e.g. Joshua's St Augustine home), select **Corporate**.
3. **Edge case — a single order-level Location field for a mixed-store cart:** if Amazon shows only ONE required Location dropdown for the whole multi-store order (cannot be set per store), you still must set it to place the order. Select the store that has the **most line items** in this order (the ship-to address you set in Step 7 remains the authoritative per-item accounting key; the monthly allocation reads ship-to, not this field). Do not block the order over this.
4. **Take a screenshot before placing the order and confirm no Location dropdown still reads "Select" / is empty.** If any required Location is unset, Amazon will reject "Place your order." Set every one, then proceed.
5. If, after a genuine check, no Location field appears at all on this order, proceed normally (some order types may not surface it) — do not invent a step that isn't on screen.

> Why this exists: store-level P&Ls allocate Amazon "Store Supplies" by store. Ship-to address is the authoritative key (the monthly pull reads it); the required Location tag gives clean native accounting and a cross-check.

---

### STEP 8 — Select Amex ending 3001 as payment

Back on the main checkout page, check the **Payment method** section. The default is usually **American Express ending in 2003** — this is NOT what we want.

1. Click **Change** next to the payment method
2. On the payment selection page, you'll see multiple cards. Select the radio button for:
   - **"American Express ending in 3001"** — labeled "Provided by your organization" — Joshua Davis — exp 12/2030
   - (NOT the "Business Platinum Card® ending in 3001" — that's a different card with the same last-4)
3. Click **Use this payment method**
4. You should return to the main checkout page with "Paying with American Express 3001" displayed

---

### STEP 9 — Place the order

1. Verify the final summary panel on the right:
   - Items count matches SUPPLY_ORDER_DATA (counting qty 2 sticky-tabs etc. as 2)
   - Shipping: $0.00
   - Tax: collected per shipping state
   - Order total looks correct (items + tax)
   - "Paying with American Express 3001" ✓
   - "Delivering to multiple addresses" ✓
   - Every required **Location** field is set (Step 7B) ✓
2. Click **Place your order** in the upper-right
3. Wait 8 seconds for the confirmation page. If Amazon blocks placement citing a missing required field, return to the Location field(s), set any that are empty, and place again.

---

### STEP 10 — Capture order confirmation (record EVERY order number)

⚠️ **CRITICAL — multi-address checkout creates MULTIPLE order numbers, one per ship-to address (and Amazon may further split a single store into several orders by fulfillment center).** There is NO single aggregate order number. Do NOT invent or report one — a fabricated number (e.g. a made-up `106-...`) will not exist in Amazon and breaks verification.

On the confirmation page, find and record:
- **Every** order number shown (format `XXX-XXXXXXX-XXXXXXX`) — there will be several. Map each order number → its ship-to store → its per-order total.
- Grand total charged (must equal the sum of all per-order totals, and match the SUPPLY_ORDER_DATA total)
- Per-address delivery dates if shown (Amazon usually breaks them out by ship-to address)

If the confirmation page doesn't cleanly list each number, open **Your Orders** (`https://www.amazon.com/your-orders/orders?timeFilter=months-3`), read the order cards placed today (each card shows its Ship-to store, Total, and `Order # XXX-XXXXXXX-XXXXXXX`), and record each store-addressed order. **Verify the store-addressed orders sum to the SUPPLY_ORDER_DATA total before proceeding** — that sum check is your proof the order actually went through.

Build a per-store map like:
`HARRISONBURG → #113-… → $47.76`, `WAYNESBORO → #113-…, #113-… → $128.41`, etc.

---

### STEP 11 — Post the summary and send confirmation DMs

Do all three of the following, in order.

**(A) Post the weekly summary to #supply-order-summary (channel_id `C0B3EE3A6LC`):**
```
:package: *Weekly Supply Order — Placed* (Week of {YYYY-MM-DD})

Placed {Day Mon D} on Amex ending 3001 · *Total ${grand_total}* · {N} items. Shipped via Amazon "deliver to multiple addresses," which splits it into per-store orders:

*{Store}* — ${store_total} — Order(s) #{order_number(s) for this store} — req. {Requester Name}
• {Product Name} ({qty})
[repeat each item under the store]

[repeat the store block for every store]

[Include only if there were manual items:]
:warning: *Needs manual action:* {item} — {Store} — {reason} — req. {Requester Name}

_Estimated delivery: {per-store/overall delivery dates, or "check Amazon Business for per-store dates"}._
```

**(B) DM Joshua (U03BB52MDSA)** — keep the `[ORDER_CONFIRMED —` marker EXACTLY (Step 1 idempotency depends on it):
```
✅ *Supply Order Placed!*

[ORDER_CONFIRMED — {YYYY-MM-DD}]
Total: ${grand_total} on Amex ending 3001 ({N} items)
Orders (split by ship-to store):
• {Store} — #{order_number(s)} — ${store_total}
[repeat per store]
Estimated delivery: {delivery dates, or "check your Amazon Business account"}

*Items ordered:*
• {Product Name} (qty {qty}) → {Store} — requested by {Requester Name}
[repeat for each item]

[Include only if there were manual items:]
⚠️ *Needs Manual Action:*
• {item description} — {Store} — {reason} — requested by {Requester Name}
```

**(C) DM each requester** (use their Slack user IDs from SUPPLY_ORDER_DATA). One message per person; if a requester had items going to one store, include that store's order number(s):
```
📦 *Your supply request was ordered!*

• {Product Name} (qty {qty}) — shipping to {Store}
[repeat their items]

Order #{this store's order number(s)} · Estimated delivery: {delivery date, or "check with Joshua"}
```

**Do NOT disable this task after a successful order.** The cron schedule (`*/15 11-18 * * 2`) means it only fires on Tuesdays, and the Step 1 ORDER_CONFIRMED idempotency check prevents a duplicate order on the same day. Leaving the task permanently enabled means it self-fires next Tuesday with no dependency on any other task re-enabling it.

---

### IMPORTANT NOTES

- The `[ORDER_CONFIRMED —` marker in Joshua's DM is essential for idempotency — always include it exactly as shown
- **Report only REAL order numbers** captured in Step 10 — one per ship-to store (more if Amazon split a store). Never fabricate a single aggregate order number; multi-address checkout does not produce one.
- If Amazon Business shows you are not logged in, do NOT attempt to log in — DM Joshua: "⚠️ Amazon Business session expired. Please log in and reply 'order' again to retry." Then stop.
- If checkout fails partway through, DM Joshua explaining exactly what was completed and what remains to be done manually
- Do NOT place the order more than once — always check for the `[ORDER_CONFIRMED —` marker first (Step 1)
- This task stays permanently enabled; the ORDER_CONFIRMED check is what prevents same-day duplicates. Do not toggle `enabled: false` on success.
- Payment is **always** Amex ending 3001 (the "Provided by your organization" American Express card, exp 12/2030) — never use the default Amex 2003 or the Business Platinum 3001
- The default address (Joshua Davis, 844 Cypress Crossing, St Augustine FL) is wrong for supply orders — you MUST use "Deliver to multiple addresses" and assign each item to its requester's store
- The **Location** order field (Step 7B) is **REQUIRED** — the order will not place until every Location dropdown is set to its store (Corporate for non-store ship-to). Always set it; verify none are empty before placing.

<!-- migrated to working model 2026-06-15 -->
<!-- 2026-06-18: added Step 7B Location store accounting tag (set REQUIRED 2026-06-18) -->
