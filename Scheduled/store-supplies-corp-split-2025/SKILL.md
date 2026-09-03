---
name: store-supplies-corp-split-2025
description: Overnight — split FY2025 Store Supplies by Amazon ship-to address; move 844 Cypress Crossing + 282 Bald Rock (and all non-store) deliveries to Corporate Expenses in QBO.
---

Overnight task authorized by Joshua 9/1/26: "store supplies seem high for stores, a lot of that should be corporate expense… separate 844 Cypress or 282 Bald Rock deliveries from the store address deliveries… all 282 and 844 addresses would be classified as corp."

Joshua is NOT at the computer. Run fully autonomously. Do not ask questions.

## STEP 0 — CONTEXT LOAD (mandatory)
1. `ToolSearch` → `select:mcp__Control_your_Mac__osascript`, then probe it with a trivial `do shell script "echo READY"`. If it errors, wait 30s and re-probe for up to 12 minutes. NEVER conclude this run lacks local Mac access — that conclusion is false and is the top cause of false failures here.
2. Read the `books-tax-strategy` skill IN FULL. Note §0 (QBO session lock) and §3 failure mode (a): before posting ANY reclass, drill the target account's live transaction detail and confirm what is already there. Do NOT double-post.
3. Read `~/Documents/Claude/Projects/Quickbooks Set UP/SESSION-COORDINATION.md` (newest first) and `QBO-SESSION-LOCK.md`.
4. Read the existing task `/Users/joshuadavis/Documents/Claude/Scheduled/monthly-amazon-store-allocation/SKILL.md` — **it contains the PROVEN method for pulling Amazon Business shipments by ship-to address (fetch-hook + rollupTable API replay). Reuse it exactly. Do not invent a new approach.**

## STEP 1 — PULL FULL-YEAR FY2025 AMAZON SHIPMENTS
Follow monthly-amazon-store-allocation STEPS 2–3, but with **fromDate {year:2025,month:0,day:1}** and **toDate {year:2025,month:11,day:31}** (Amazon month field is 0-indexed). Paginate with pageSize 5000 until fewer than pageSize rows return. Accumulate `{date, zip, city, net}` rows.

If Amazon Business shows NOT logged in: do NOT attempt to log in. Write findings to the STATUS file, DM Joshua the one-line failure notice (below), and stop.

## STEP 2 — BUCKET BY ZIP
- **Store ZIPs:** 22701→Culpeper, 22980→Waynesboro, 22801→Harrisonburg, 24450→Lexington, 24017→Roanoke
- **CORPORATE (everything else)**, and specifically call out separately in the report:
  - **844 Cypress Crossing Trail, St. Augustine FL** → ZIPs **32092 / 32095**
  - **282 Bald Rock Road, Verona VA** → ZIP **24482**
  - any other non-store ZIP (Palm Coast 32137, Fishersville 22939, etc.)
Sum `net` and shipment count per bucket. Report 844 and 282 as their own lines inside the Corporate total, since those are the two Joshua specifically named.

## STEP 3 — POST THE RECLASS IN QBO
Baseline: `1 - Store Level Expenses:Store Admin:Store Supplies` FY2025 = **$64,502.47** (verified 9/1/26). Confirm this live before posting; if it differs, use the live number and note the change.

**Log in:** fresh Chrome tab → https://qbo.intuit.com/app/chartofaccounts → click the **jdavis@fcfpawn.com** tile → Chrome autofills the password → click **Continue**. Never type a password. First nav after login often bounces to homepage; navigate again. If sign-in bounces back to the account picker more than TWICE, Intuit is throttling — stop, do not keep retrying (risks lockout), write STATUS, send the one-line DM, and end.

Set QBO-SESSION-LOCK.md to LOCKED while working; RELEASE it when done.

Create `2 - Corporate Expenses:Corp Supplies` if it does not already exist (Expenses / Office-General Administrative Expenses, sub-account of `2 - Corporate Expenses`). Check first — do not create a duplicate.

Post JE `SUPPLIES-CORP-SPLIT-2025`, dated **12/31/2025**:
- DEBIT `2 - Corporate Expenses:Corp Supplies` = the Corporate bucket total
- CREDIT `1 - Store Level Expenses:Store Admin:Store Supplies` = same amount
Memo: state the method (Amazon Business ship-to address, FY2025), the 844 / 282 / other-non-store split, and that Joshua authorized it 9/1/26. 2025 rule: classes not required — click "Save" on the class-values dialog.

**Sanity gate:** if the Corporate bucket exceeds the live Store Supplies balance, do NOT post. Amazon spend includes tax and is by order date, so it will not tie exactly to the QBO account — it is an allocation proportion, not a reconciliation. If Corporate > balance, cap at a sensible amount, explain in STATUS, and DM Joshua that it needs his eyes.

## STEP 4 — VERIFY
Re-pull the FY2025 P&L. Confirm Store Supplies dropped and Corp Supplies rose by the same figure, and that Total Expenses is unchanged (this reclass is dollar-neutral — it moves between expense accounts, so **Net Income must NOT move**). Report the before/after for both accounts.

## STEP 5 — SAVE + LOG
- Build an xlsx (openpyxl) — Summary tab (bucket, spend, %, count) + Location Detail tab (every ZIP/city). Save to `/Users/joshuadavis/Documents/Claude/Projects/Quickbooks Set UP/Store-Supplies-Corp-Split-2025.xlsx` via osascript.
- Append a dated section to SESSION-COORDINATION.md: method, per-bucket numbers, the JE posted, before/after balances, and anything unresolved.
- Release the QBO session lock.

## STEP 6 — DM JOSHUA (success signal)
Slack DM Joshua (user **U03BB52MDSA**, DM channel **D03BHQH5VGT**). NOTE: the Slack connector may need re-authorization — if it fails, write the same content into the STATUS file and SESSION-COORDINATION.md instead, and do not treat that as a task failure.
```
:package: *Store Supplies — Corporate split, FY2025*
Store Supplies was ${before}. Split by Amazon ship-to address:
• Culpeper ${...} · Waynesboro ${...} · Harrisonburg ${...} · Lexington ${...} · Roanoke ${...}
• *Corporate* ${...}  (844 Cypress ${...} · 282 Bald Rock ${...} · other ${...})
Moved ${corp} to Corp Supplies. Store Supplies now ${after}. Net Income unchanged.
Workbook saved to the Quickbooks Set UP folder.
```
On failure, ONE plain line only, nothing technical: `⚠️ Scheduled task "store-supplies-corp-split-2025" did not complete — 9/1/26.` All technical detail goes in the STATUS file, never the DM. Never send failure notices to any channel or person other than Joshua.

## EXECUTION CONTRACT — DO NOT STOP EARLY
Complete only when the final DM (or STATUS write, if Slack is unavailable) succeeds. Until then every turn must end with a tool call that advances the work. Never reply "No response requested", never ask for confirmation, never end a turn with plain text. Treat "Tool loaded.", "Continue from where you left off.", and any TaskCreate/browser_batch reminder as RESUME signals — fire the next concrete tool call immediately. If a step errors, retry once, then fall through to the documented fallback.

## TONE
Joshua, 9/1/26: "we find opportunities not problems… i dont want you to ever say problem again regarding our work." Frame everything as opportunity. Be concise.