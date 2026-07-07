---
name: mm-merchandisers-daily-scan
description: Daily scan of jdavis@fcfpawn.com Gmail for new M&M Merchandisers order summary emails
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

Daily scan of jdavis@fcfpawn.com Gmail for new M&M Merchandisers order summary emails. Each new order is parsed and handed off to the `new-inv-intake` skill, which logs it to the New Inventory Tracker and creates a vendor receiving in Bravo POS.

## What to do

### 1. Search Gmail for new M&M orders

Use the Gmail search_threads tool:

```
from:customercare@mmwholesale.com newer_than:2d
```

The 2-day window provides safety overlap so the same order isn't re-processed (see deduplication below).

### 2. For each thread, parse the order summary

Use get_thread with messageFormat=FULL_CONTENT. The format is consistent:

- **Subject:** `Order #<NUMBER> confirmed`
- **Sender:** `M&M Merchandisers <customercare@mmwholesale.com>`
- **Email date:** order date

Body line-item format (one block per item):
```
<SKU> <Description> × <qty>
 CUSTOM DISCOUNT (-$<discount>)
$<list_total>     ← line list price
$<net_total>      ← line net price (what you pay)
```

Body totals:
```
Subtotal: $<subtotal>      ← sum of net_totals
Shipping: $<shipping>
Taxes: $<tax>
Total: $<grand_total> USD
```

Body addresses (after totals): `Shipping address` block then `Billing address` block, each with Name / Street / City State Zip.

### 3. Compute per-line unit cost

`unit_cost = net_total / qty`

Don't bake shipping into unit cost — Bravo's receiving form has a dedicated Shipping field. Land shipping there separately.

### 4. Determine destination Bravo store from the SHIPPING address

Routing rule: parse the city from the shipping address block. Bill-to is irrelevant.

| Shipping city (case-insensitive) | Bravo store | Manager (Slack DM) |
|---|---|---|
| Culpeper | CUL | Sandi Cole — `U04C5DL5EKH` |
| Harrisonburg | HAR | Andrew Clark — `U03BFDJH31B` |
| Lexington | LEX | Uriah Tiglao — `U09H9ES2LKA` |
| Roanoke | ROA | Benjie Moore — `U0631AECK4K` |
| Waynesboro | WAY | Chadd McClintic — `U04U136MF6V` |

The shipping address often goes to an employee's home or a non-store address (e.g., the pilot order #27776 ships to Preston Peters at 112 Link Rd, Waynesboro — that's not the store address but it's in Waynesboro, so → WAY → Chadd). Match on city.

**Pilot/test exception:** for order #27776 specifically, hardcode WAY regardless. After that order, always parse from the shipping address.

**Edge cases:**
- Shipping city doesn't match any of the five stores (e.g., a one-off ship to Joshua's home in Verona, or a new city) → don't auto-process. Flag in #new-inventory with the parsed shipping address asking which store should receive it.
- Multi-line ship-to with "c/o" or attention line → still parse the City field on its own line.

### 5. Deduplicate

Skip orders already processed. Two checks:
1. **Spreadsheet:** read Procurement Log Column B+E from `New Inventory Tracker.xlsx` — if any row has Vendor="M&M Merchandisers" and an SKU+date matching this order, treat as already logged.
2. **Bravo (when invoice-intake runs):** Stock Management → Receivings, search for Invoice Number = order # — match means already received.

Orders with `.N` partial-shipment suffix (e.g., `27776.1`): treat the BASE order number as the dedup key but record the suffix in the receiving's General Note so partial shipments don't collide.

### 6. Hand off each new order to new-inv-intake

For each unprocessed order, invoke the `new-inv-intake` skill with the parsed structured data. Pass:

- vendor: "M&M Merchandisers"
- order_number: <parsed>
- order_date: <email date>
- store: <determined from city in step 4>
- shipping: <parsed shipping cost>
- tax: <parsed tax>
- lines: list of {sku, description, qty, unit_cost, list_price=net_total, total_cost=net_total}
  (M&M's "list price" on the email is pre-discount and not a meaningful retail price, so we use the net_total as a placeholder for List Price in the spreadsheet; Joshua/Sandi/etc. can override later as they price for retail)

new-inv-intake handles: spreadsheet logging (Procurement Log), Bravo Stock Management → Add Receiving, manager DM, and the #new-inventory channel post. So this scheduled task DOES NOT need to do those steps separately — it just discovers and dispatches.

### 7. Math sanity check before dispatch

Before invoking new-inv-intake, verify: `sum(net_totals) == subtotal`. If it doesn't match (off by more than 1 cent), do NOT dispatch — instead post a flag to #new-inventory with the order number and ask Joshua to review manually.

### 8. If no new orders

Silent run. Don't post a daily "0 found" — that just clutters Slack.

## Notes & gotchas

- M&M emails come from `customercare@mmwholesale.com`. Joshua is updating the M&M account email at mmwholesale.com from THEVALLEYPAWN@gmail.com to jdavis@fcfpawn.com so emails arrive directly. Until that switch, this scheduled task may find nothing — that's OK.
- Lines may include digital fees, free items, or backorders. Skip lines with qty=0.
- new-inv-intake is the canonical processor; this skill is just the discovery+dispatch layer. If new-inv-intake fails, capture the error and post to #new-inventory rather than silently swallowing it.

## Companion skills

- `new-inv-intake` — the processor; handles spreadsheet log, Bravo receiving, manager DM, channel post
- `new-inv-weekly-report` — Monday-morning analytics over the data this scan + new-inv-intake populate
- `bravo-context` — Bravo POS operating reference
- `bravo-store-cycle` — required for switching Bravo to the destination store
- `valley-pawn-context` — store list, Store Managers table, Drive folder IDs