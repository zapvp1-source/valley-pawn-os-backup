---
name: new-inv-weekly-report
description: Weekly new inventory sell-through analysis and Slack report for Valley Pawn
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

Run Valley Pawn's weekly new inventory performance report. Automated Monday morning task that analyzes new inventory sales across all 5 stores, updates the New Inventory Tracker spreadsheet, and posts a dashboard to Slack #new-inventory plus per-store manager DMs.

## File paths (host paths — use Read/Write/Edit directly)

- **Tracker spreadsheet:** `/Users/joshuadavis/Documents/Claude/Projects/New Inventory Procurement/New Inventory Tracker.xlsx`
- **Google Drive copy:** Valley Pawn Drive root (`https://drive.google.com/drive/u/0/folders/0AHw0UROQ5gMdUk9PVA`) — upload the updated xlsx after edits

For bash-only operations (running scripts), the current session's mount path is whatever request_cowork_directory returns for /Users/joshuadavis/Documents/Claude. Don't hardcode a session ID — it changes every session.

## Tracker schema (verified 2026-05-08)

Five sheets in `New Inventory Tracker.xlsx`:

| Sheet | Purpose | Header row | Data starts |
|---|---|---|---|
| Procurement Log | Every wholesale purchase | row 2 | row 3 (rows 7+ are formula-pre-populated for new entries) |
| Par Levels | Min stock per category × store | row 2 | row 3 |
| Weekly Dashboard | Cumulative + week-over-week sell-through | row 7 | row 8 |
| Reorder Queue | Items below par awaiting PO | row 3 | row 4 |
| Setup & Reference | Documentation (don't touch) | — | — |

**Procurement Log columns:** A:Date Purchased, B:Vendor, C:Category, D:Item Description, E:SKU/Model #, F:Store, G:Qty, H:Unit Cost, I:Total Cost (formula =G*H), J:List Price, K:Gross Margin (formula), L:Bravo Item #, M:Status. Status="Active" means in cycle.

**Par Levels columns:** A:Category, B:Item/Description, C:Store, D:Par Qty, E:Current Stock, F:On Order, G:Available (formula =E+F), H:Reorder Needed? (formula), I:Reorder Qty (formula), J:Preferred Vendor.

**Weekly Dashboard sell-through log columns (rows 7+):** A:Week Of, B:Category, C:Items Procured, D:Units Sold, E:Sell-Through % (formula), F:Revenue, G:COGS, H:Gross Profit, I:Gross Margin % (formula), J:Items Below Par, K:Store w/Most Sales, L:Notes.

**Reorder Queue columns (rows 4+):** A:Week Generated, B:Category, C:Item Description, D:Store, E:Par Qty, F:Current Stock, G:Qty to Order, H:Preferred Vendor, I:Status.

## Store codes used in spreadsheet vs Bravo

The Procurement Log Column L sample data uses `HBG-00001` for Harrisonburg, but Bravo's actual store code for Harrisonburg is `HAR`. Use **HAR** when matching against Bravo data going forward (this is documented in `bravo-context`). If you see `HBG` anywhere in the legacy spreadsheet rows, treat it as HAR.

Full mapping: Culpeper=CUL, Harrisonburg=HAR, Lexington=LEX, Roanoke=ROA, Waynesboro=WAY.

## Step 1 — Pull sales data from Bravo (all 5 stores)

Use the `bravo-store-cycle` skill to cycle through CUL/HAR/LEX/ROA/WAY. At each store:

1. Open Bravo's Reports module → Sales Report (or Inventory Sales Report)
2. Date range: previous Monday through Sunday (the 7 days ending yesterday)
3. Filter by Department/Category = "New Inventory" if that department exists, else filter by Bravo Item #s present in Procurement Log Column L
4. Capture per sold item: description, Bravo item/ticket #, qty sold, sale price, date sold, store

Bravo notes (per `bravo-context`):
- Bravo can be slow — wait for list to render before reading
- Title bar shows `VALLEY PAWN - <STORE> (<CODE>)` — verify before reading any list
- Excel export from Custom Reports is the cleanest data path

## Step 2 — Cross-reference with Procurement Log

Load the Procurement Log into pandas/openpyxl. For each Bravo-sold item:
- Match by Bravo Item # (Column L) preferred, else by Item Description (Column D) + Store (Column F)
- Pull Unit Cost (H), List Price (J), Category (C)
- Gross Profit per unit = Sale Price − Unit Cost

## Step 3 — Compute weekly metrics

Both overall and per-category:

| Metric | Formula |
|---|---|
| Units Active | Count of Procurement Log rows where Status="Active" |
| Units Sold | From Bravo data |
| Sell-Through % | Sold / Active |
| Gross Revenue | Sum of sale prices |
| COGS | Sum of (unit cost × qty sold) |
| Gross Profit | Revenue − COGS |
| Gross Margin % | Profit / Revenue |
| Total CapEx (cumulative) | Sum of Procurement Log Column I (Total Cost), all time |
| This-Week CapEx | Sum of Total Cost where Date Purchased is in current week |

## Step 4 — Update tracker spreadsheet

### Weekly Dashboard sheet
Append a new "All Categories" row at first empty row after row 7:
- A: Week Of (Monday date YYYY-MM-DD)
- B: "All Categories"
- C: Units Procured (active count)
- D: Units Sold
- F: Gross Revenue
- G: COGS
- H: Gross Profit
- J: Items Below Par count
- K: Store with most units sold

(Columns E and I have existing formulas for sell-through % and margin %.)

Append per-category rows below.

### Par Levels sheet
Update Column E (Current Stock) for each row: `Current Stock = sum(qty procured for that category × store) − sum(qty sold)`. Leave Columns F (On Order), G/H/I (formulas), and J (Preferred Vendor) alone unless On Order is being explicitly updated.

### Reorder Queue sheet
For every Par Levels row where Column H = "⚠️ YES":
- A: Today's date
- B: Category
- C: Item Description
- D: Store
- E: Par Qty
- F: Current Stock
- G: Qty to Order (= Par − Available)
- H: Preferred Vendor (from Par Levels Column J if set)
- I: "📋 Pending Review"

Append at first empty row after row 3.

### Save and recalc
After writing, recalc formulas. Use the xlsx skill's recalc helper — find the current session's mount path for the xlsx skill scripts at runtime (don't hardcode):

```bash
# Find current session mount, then run recalc
TRACKER="$(echo /sessions/*/mnt/Claude/Projects/'New Inventory Procurement'/'New Inventory Tracker.xlsx')"
RECALC="$(echo /sessions/*/mnt/.claude/skills/xlsx/scripts/recalc.py)"
python "$RECALC" "$TRACKER" 60
```

Then upload the saved xlsx to the Valley Pawn Drive root via Chrome MCP (Drive folder URL above).

## Step 5 — Post Slack dashboard

### Channel: #new-inventory (id `C0B3ES0AE48`) — full dashboard with cost detail

```
📊 *New Inventory Weekly Report* — Week of [Monday Date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 *CapEx Summary*
• Total Invested (All Time): $[cumulative]
• This Week's Purchases: $[this_week]

📈 *Sell-Through Performance*
• Items Active: [count]
• Units Sold This Week: [sold]
• Sell-Through Rate: [X.X%]
• Gross Revenue: $[revenue]
• Gross Profit: $[profit] ([X.X%] margin)

🏆 *Top Performers This Week*
• [Category]: [units] units | $[revenue] | [X%] margin
• [Category]: [units] units | $[revenue] | [X%] margin
• [Category]: [units] units | $[revenue] | [X%] margin

🏪 *By Store*
• Culpeper: [units] units | $[revenue]
• Harrisonburg: [units] units | $[revenue]
• Lexington: [units] units | $[revenue]
• Roanoke: [units] units | $[revenue]
• Waynesboro: [units] units | $[revenue]

🔄 *Reorder Alerts* ([count] items below par)
• [Category] — [Item]: [current] on hand, par = [par], need [qty] more → [Vendor]
[or "✅ All categories above par level" if none]

_Tracker updated on Drive. Reply in thread to approve reorders._
```

### Manager DMs (one per store) — store-specific, no cost data

DM each store manager (per `valley-pawn-context` Store Managers table):

| Store | Manager | Slack user_id |
|---|---|---|
| CUL | Sandi Cole | `U04C5DL5EKH` |
| HAR | Andrew Clark | `U03BFDJH31B` |
| LEX | Uriah Tiglao | `U09H9ES2LKA` |
| ROA | Benjie Moore | `U0631AECK4K` |
| WAY | Chadd McClintic | `U04U136MF6V` |

Format (no $ figures; managers see what their store sold and what's incoming):

```
📊 [Store name] — Weekly New Inventory Recap (Week of [Monday])

Sold this week ([N] units):
• [Item] × [qty]
• [Item] × [qty]

Currently below par ([N] items):
• [Category] — [Item]: [current] on hand, want [par]

[If none below par:] ✅ Everything's above par for your store
```

If a store had zero sales AND nothing below par, skip that store's DM (no need to ping them with an empty report).

## Step 6 — Reorder approval flow

If the Reorder Queue has new "📋 Pending Review" items, post the full reorder list as a thread reply on the #new-inventory dashboard message. Wait for Joshua to reply with approval before drafting any vendor PO emails.

## Notes & gotchas

- "New Inventory" = wholesale/procured stock only — never includes pawn items, customer buyouts, or consignment
- If a Bravo store cycle fails for any store, note it in the dashboard and skip that store's data — don't fail the whole run
- If the tracker has no procurement data (empty Procurement Log), still post a brief "system ready, no data this week" note to #new-inventory so the channel knows the run completed
- Always use the Slack MCP for posts/DMs — never computer use
- Use Chrome MCP for Google Drive upload — navigate directly to the Valley Pawn Drive folder URL
- Bravo's built-in SKU Levels (Reorder Point + Desired Level + Suggested Reorder, in Stock Management → SKU Levels) is a future enhancement we may shift to once par-level data lives there. For now, the spreadsheet's Par Levels sheet is the source of truth.

## Companion skills

- `bravo-context` — Bravo POS reference (Stock Management, SKU Levels, store codes, reports)
- `bravo-store-cycle` — required for cycling between stores in Bravo
- `valley-pawn-context` — store list, Store Managers table, Drive folder IDs
- `mm-merchandisers-daily-scan` — sister scheduled task; auto-detects new M&M orders and feeds them into the Procurement Log
- (existing) `new-inv-intake` — manual reactive logging of vendor purchases
