# Bravo Report Inventory

**Captured:** 2026-05-28, from a live Bravo session on CULPEPER (CUL), Bravo version 2026.2.2.3.
**Why this file exists:** plain-English list of every report Bravo can produce, so we can decide which ones to wire up for unattended pulls. The report menus are identical across all 5 stores — what's listed here is what every store can do.

---

## How Bravo's reports are organized

Bravo has reports in **three places**:

1. **The master Reports page** — opened from the right-sidebar "Reports" entry on the Dashboard. 49 built-in reports, organized in 5 categories. These are the "premade" reports — Bravo ships with them.
2. **Reporting Pro panel on the Dashboard** — 4 shortcut tiles to cross-store dashboards (KPIs etc).
3. **Custom Reports inside each module** — saved Ad Hoc reports built by you or Preston. Per module. The Loans/Buys list is captured below; other modules have their own lists I haven't enumerated yet.

---

## 1) Master Reports page (49 built-in reports)

### Closing Reports (18)

| Report | Already wired? | Notes |
|---|---|---|
| 8300 Audit | No | IRS form 8300 (cash transactions >$10k). Compliance. |
| BRAVO Business Dashboard | No | Bravo's own summary view. |
| Deposits and Paid Outs Spreadsheet | No | Cash movement. |
| Disbursement Journal | No | Outgoing money log. |
| **Employee Activity** | **Yes** (handler `EmployeeActivity.ahk`) | Used by weekly/monthly employee sales rankings. |
| End of Day | No | Daily till close. |
| End of Day - Consolidated | No | Daily close across stores. |
| **End of Month** | **Yes** (handler `EndOfMonth.ahk`) | Canonical cross-store financial source. Used by 4+ downstream tasks. |
| Fortis Alignment | No | Payment processor reconciliation. |
| General Exception | No | Audit / exceptions log. |
| Inter-Store Cash Transfer | No | Cash movement between stores. |
| Large Cash Transactions | No | Compliance — cash transactions over a threshold. |
| **Safe Register Journal** | **Yes** (used by `daily-funds-verification`) | Confirms funds you sent landed in the safe. |
| Session Journal | No | User session activity log. |
| Store Register Journal | No | Per-store register movement. |
| Till Cash Balance | No | Current cash in tills. |
| Till Register Journal | No | Till-level transaction log. |
| Transfers | No | Inventory/cash transfers. |

### Inventory Reports (8)

| Report | Already wired? | Notes |
|---|---|---|
| **Aged Inventory Summary** | **Partial** (consumer task disabled, needs verification) | The aged-inventory weekly report depends on this. |
| Cost Adjustment | No | When you change an item's cost. |
| Inventory Base | No | Total inventory snapshot. End of Month already pulls Ending Inventory Base. |
| Inventory by Location | No | Where items are physically located in store. |
| Item History | No | Per-item transaction history. |
| Lost Stolen or Damaged | No | Shrink reporting. |
| Vendor Purchase | No | What you bought from wholesale vendors. (Pairs with new-inv-intake.) |
| Vendor Repairs | No | Items out for repair. |

### Loan Reports (9)

| Report | Already wired? | Notes |
|---|---|---|
| Loan Base | No | Current outstanding loan portfolio snapshot. |
| Loan Disposition | No | What happened to each loan (paid, expired, etc). |
| Loan History | No | Per-customer / per-loan history. |
| Loan Journal | No | All loan transactions in a date range. |
| Loan Notice | No | Loans on notice (already a Dashboard tile). |
| Loans/Buys by Location | No | Where loans/buys were originated. |
| On Hold Listing | No | Items held for customer. |
| Pawn Activity Summary | No | Period activity summary for pawn ops. |
| Supplemental Loan Disposition | No | Detail level of loan disposition. |

### Retail Reports (2)

| Report | Already wired? | Notes |
|---|---|---|
| Drop Ship Settlement | No | Drop-ship sales reconciliation. |
| Retail Reports Dashboard | No | Retail performance dashboard. |

### Sales Reports (12)

| Report | Already wired? | Notes |
|---|---|---|
| ATF A & D Book | No | ATF acquisition & disposition book (firearms compliance). |
| ATF A & D Count | No | ATF count summary. |
| Credit Balance | No | Customer credits owed to customers. |
| Credit Journal | No | Credits issued/applied. |
| Digital Marketing Settlement | No | Online marketing channel reconciliation. |
| Layaway Balance | No | Outstanding layaway balances. |
| Layaway Deposits | No | Layaway payments received. |
| Layaway History | No | Per-layaway history. |
| Layaway Journal | No | All layaway transactions in a date range. |
| Sales Accounting | No | Sales for accounting purposes. |
| Sold Inventory | No | What was sold in a period. |
| Web Settlement | No | Online sales reconciliation. |

---

## 2) Reporting Pro panel (Dashboard, 4 tiles)

These are interactive SSRS-style dashboards Bravo renders in a browser pane. Different shape from the CSV-exporting reports above.

| Tile | What it shows |
|---|---|
| **Company KPIs** | Cross-store KPIs (loan balance, layaway balance, etc) for ALL 5 stores side-by-side. One click, no store cycling. Already used by `loan-layaway-review` for one-shot balance pulls. |
| Store KPIs | Same dashboard, one store at a time. |
| Employee Activity | SSRS-rendered employee performance dashboard (likely overlaps with the Closing Reports → Employee Activity CSV-exporting one). |
| eCommerce Metrics | Online channel performance. |

---

## 3) Saved Custom Reports — Loans/Buys module (19 today)

These are ad hoc reports built and saved by you/Preston inside Loans/Buys → Custom Reports. Visibility: "SHARED COMPANY-WIDE" is saved for all 5 stores; "SHARED GLOBALLY" is system-wide.

| Saved Report | Sharing | Already wired? |
|---|---|---|
| **75 Days Past Due** | COMPANY-WIDE | Yes (consumer disabled) — past-due loans review |
| Buy tickets by Amount | GLOBALLY | No |
| **Claude Buy Reviews** | COMPANY-WIDE | No (named for automation — unknown handler status) |
| **Claude First Payment Default** | COMPANY-WIDE | Yes (consumer disabled) — FPD ranking |
| **Claude Loan Portfolio 2026** | COMPANY-WIDE | Yes (artifact) — weekly portfolio refresh |
| **Claude Loan Reviews** | COMPANY-WIDE | Yes (consumer disabled) — weekly loan review |
| **Claude Low Dollar Buys** | COMPANY-WIDE | No (named for automation — unknown handler status) |
| **Claude Low Dollar Loans** | COMPANY-WIDE | Yes (handler exists, consumer ❓) |
| Disposition by Date | GLOBALLY | No |
| Expired Loans now in Inventory | GLOBALLY | No |
| jewelry | COMPANY-WIDE | No |
| Loan Walk | GLOBALLY | No |
| Loan Walk (Expired) | GLOBALLY | No |
| Loan/Buy Review | COMPANY-WIDE | No |
| Loans By Amount | GLOBALLY | No |
| past 75 days | COMPANY-WIDE | No (duplicate-ish of "75 Days Past Due"?) |
| Past due loans | COMPANY-WIDE | No |
| Redeemed by Category/Customer for Marketing | GLOBALLY | No |

**Observation:** the "Claude " prefix is the convention for reports we built specifically for automation. Of the 8 Claude-prefixed reports, 5 are already wired in some form. **`Claude Buy Reviews` and `Claude Low Dollar Buys` may be wired-but-undocumented** — worth Preston-confirming.

---

## 4) Saved Custom Reports — other modules (NOT yet enumerated)

Each of these modules has its own "Custom Reports" button with its own saved-report list. Today I only walked Loans/Buys. The others to walk on a follow-up session:

- **Layaways → Custom Reports** — known to include layaway aging reports
- **Inventory → Custom Reports** — likely includes aged inventory variants
- **Sales → Custom Reports** — sales by category, top items
- **Customers → Custom Reports** — segmentation, dormant, high-value (these are the GAP cells in `bravo-pipeline-registry.md`)

**Why I stopped here:** the Loans/Buys list demonstrates the pattern. The other modules likely have ~5-15 saved reports each, all enumerable in 2-3 minutes per module. Worth doing on a focused follow-up so we can finalize the wire-up list.

---

## What this inventory makes possible

The plan from the earlier conversation:

1. ✅ **Inventory** — this file. Done for built-in + Reporting Pro + Loans/Buys saved.
2. ⏭ **Decide which reports to wire** — Joshua marks each row above with "wire it" or "skip" so we have a clear target list.
3. ⏭ **Fill the gaps** — for every "wire it" row not already wired, draft a new handler on the island.
4. ⏭ **Schedule + prove** — register each as a scheduled task, run unattended overnight, confirm CSVs land.

**Next time we're in Bravo for ~15 minutes:** walk Layaways, Inventory, Sales, Customers Custom Reports lists to complete the saved-report side.
