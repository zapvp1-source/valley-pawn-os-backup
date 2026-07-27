# Bravo Pipeline Registry

**Single source of truth for every pipeline cell that moves data into or out of Bravo POS for Valley Pawn / Full Circle Finance Inc.**

Read this BEFORE any Bravo-touching work. See `SESSION_PROTOCOL.md` for the mandatory preflight.

- **Last full audit:** 2026-05-26 — skeleton from `bravo-context` skill + scheduled-task inventory. Rows marked ❓ TO VERIFY need to be confirmed against the actual Bravo Data Extraction project.
- **Pipeline source code:** `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`
- **CSV output folder:** `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/`
- **Scheduled tasks folder:** `/Users/joshuadavis/Documents/Claude/Scheduled/`

---

## Status legend

- ✅ Verified working as of audit date
- ⚠️ Cell works but consumer task is disabled or manual-only
- ❌ Broken / not running
- 🔨 Gap — pipeline cell needs to be built
- ❓ Unverified — inferred from skill docs, needs in-session confirmation

---

## How to use this registry

1. **Find the data you need.** Search the OUT tables by domain (Financial, Loans, Layaways, Inventory, Sales, Customer).
2. **Check status.** ✅ means a CSV likely exists in the output folder — `ls` to confirm before re-pulling. ⚠️ means the cell is fine but no automation posts the result; trigger a one-shot pull. 🔨 means it must be built additively.
3. **Reuse before re-pulling.** If a CSV from the last 30 days covers your window, use it.
4. **Never modify existing handlers.** Clone them. See "Additive-Only Rule" in `bravo-context` SKILL.md.
5. **After verifying or changing a row, update "Last verified."** Bump the status if it changed.

---

## OUT — Data extraction (Bravo → CSV)

### Financial / GL

| Cell | Saved report (Bravo path) | Handler | CSV pattern | Consumer task(s) | Channel | Status | Last verified |
|---|---|---|---|---|---|---|---|
| `end-of-month` | Dashboard → Reports → Closing Reports → End of Month | `EndOfMonth.ahk` | `<END_DATE>_<STORE>_end-of-month.csv` | `asset-recovery-daily-refresh`, `monthly-analytics-report`, `eom-bravo-gl-export`, `compile-monthly-minutes` | #store-performance | ✅ canonical | 2026-05-25 |
| `consolidated-gl` | Dashboard → Accounting → Consolidated GL ❓ | ❓ | `<from>_to_<to>_<STORE>_consolidated-gl.csv` ❓ | `eom-bravo-gl-export` | QBO upload | ⚠️ task disabled | — |
| `safe-register-journal` | Safe Register Journal ❓ | ❓ | `<date>_<STORE>_safe-register.csv` ❓ | `daily-funds-verification` | #funds-verification ❓ | ✅ | 2026-05-25 |

### Loans

| Cell | Saved report | Handler | CSV pattern | Consumer task(s) | Channel | Status | Last verified |
|---|---|---|---|---|---|---|---|
| `loan-reviews` | Claude Loan Reviews (Ad Hoc) | `LoanReviews.ahk` | ❓ | `weekly-loan-layaway-review` | #loan-review | ⚠️ task disabled | — |
| `loans75-gridread` | 75 Days Past Due (Ad Hoc) — **GRID-READ, no export** | `Loans75GridRead.ahk` | `<date>_<STORE>_loans75-gridread.csv` | (Phase 0 proof; future loan review) | — | ✅ **VALIDATED 2026-06-17** — shadow-matched existing cell ($80 / 1 past-due loan, WAY) + full row detail, no export, no hang. Uses `SelectSavedReport()` to apply the filter. | 2026-06-17 |
| `low-dollar-loans` | Claude Low Dollar Loans (Ad Hoc) | `LowDollarLoans.ahk` | ❓ | ❓ | — | ❓ | — |
| `seventy-five-day-past-due` | 75 Days Past Due (Ad Hoc) | ❓ | ❓ | `weekly-loan-layaway-review` | #loan-review | ⚠️ task disabled | — |
| `first-payment-default` | Claude First Payment Default | ❓ | ❓ | `weekly-fpd-ranking` | #first-payment-default | ⚠️ task disabled | 2026-05-18 |
| `loan-portfolio-2026` | Claude Loan Portfolio 2026 ❓ | `LoanPortfolio2026.ahk` ❓ | ❓ | `weekly-loan-portfolio-refresh` | Loan Portfolio artifact | ✅ | 2026-05-25 |

### Layaways

| Cell | Saved report | Handler | CSV pattern | Consumer task(s) | Channel | Status | Last verified |
|---|---|---|---|---|---|---|---|
| `layaway` | (layaway saved reports — confirm names) | ❓ | `<date>_<STORE>_layaways.csv` (single summary row) | `monday-bravo-combined-run`/`-compile` | #layaway-review | ✅ | 2026-07-06 |

### Inventory

| Cell | Saved report | Handler | CSV pattern | Consumer task(s) | Channel | Status | Last verified |
|---|---|---|---|---|---|---|---|
| `aged-inventory` | Aged Inventory | ❓ | `<date>_<STORE>_aged-inventory-summary.csv` | `monday-bravo-combined-run`/`-compile` | #aged-inventory-review | ✅ | 2026-07-06 |
| `new-inv-sell-through` | (composite — confirm sources) | ❓ | ❓ | `new-inv-weekly-report` | (Slack) | ⚠️ task disabled | 2026-04-27 |
| `top-sales-monthly` | Sales by Category / Top Items ❓ | ❓ | ❓ | `monthly-top-sales-review` | #store-performance | ⚠️ manual only | — |

### Sales & Employees

| Cell | Saved report | Handler | CSV pattern | Consumer task(s) | Channel | Status | Last verified |
|---|---|---|---|---|---|---|---|
| `employee-activity` | Employee Activity report | `EmployeeActivity.ahk` | `<FIRST_OF_MONTH>_<STORE>_employee-activity.csv` | `monday-bravo-combined-run`/`-compile`, `monthly-employee-sales-rankings` | #employee-performance | ✅ | 2026-07-06 |
| `company-kpi` | Company KPI Dashboard | ❓ | ❓ | `monthly-analytics-report`, `monday-store-rankings` | #store-performance | ⚠️ monthly ✅, weekly manual | — |

### Customer

| Cell | Saved report | Handler | CSV pattern | Consumer task(s) | Channel | Status | Last verified |
|---|---|---|---|---|---|---|---|
| `chekkit-inactives` | (Chekkit Inactives composite) | ❓ | `<date>_<STORE>_chekkit-invites.csv` | `chekkit-weekly-review-requests` | #chekkit-updates | ❌ 2026-07-06: failed all 5 stores in combined run (EnsureStore ×3, render-timeout LEX, 0-row CUL) | 2026-07-06 |
| `customer-segmentation` | **NOT BUILT** | — | — | **NOT BUILT** | (proposed: #customer-tiers) | 🔨 GAP | — |
| `high-value-customer` | **NOT BUILT** | — | — | **NOT BUILT** | (proposed: #vip-customers) | 🔨 GAP | — |
| `customer-ltv` | **NOT BUILT** | — | — | **NOT BUILT** | — | 🔨 GAP | — |
| `dormant-customer` | **NOT BUILT** — last visit >90 days, lifetime value above threshold | — | — | **NOT BUILT** | — | 🔨 GAP | — |

---

## IN — Data push (Outside → Bravo)

| Action | Trigger / Skill | Mechanism | Status |
|---|---|---|---|
| Add new vendor inventory receiving | `new-inv-intake` | computer-use → Stock Management → Add Receiving | ✅ |
| Register new wholesale vendor | `new-inv-intake` | computer-use | ✅ |
| Customer note update | **NOT BUILT** | — | 🔨 GAP |
| Loan extension | **NOT BUILT** | — | 🔨 GAP |
| Layaway extension | **NOT BUILT** | — | 🔨 GAP |
| Aged-inventory price override | **NOT BUILT** | — | 🔨 GAP |
| Bulk markdown push | **NOT BUILT** | — | 🔨 GAP |
| Customer tag / segment back-write | **NOT BUILT** | — | 🔨 GAP |

---

## Pipeline source — files of record (in Bravo Data Extraction project)

- `bravo_watcher.ahk` — file-system watcher + dispatch table (DO NOT EDIT existing entries — additive only)
- `bravo_export.ahk` — export driver + dispatch table (additive only)
- `reports/*.ahk` — one handler per pipeline cell
- `lib/` — shared utilities
- `output/` — CSV outputs (`<date>_<STORE>_<report>.csv` or `<from>_to_<to>_<STORE>_<report>.csv`)
- `SLICE*_STATUS.md` — per-cell development status
- `FINDINGS_AND_PLAN.md` — known issues + roadmap

---

## Saved reports in Bravo (named report registry)

To be enumerated by reading Bravo's saved Ad Hoc reports list on the next session with Parallels grant. Currently known:

- Claude Loan Reviews
- Claude Low Dollar Loans
- 75 Days Past Due
- Claude First Payment Default
- Claude Loan Portfolio 2026 ❓
- (layaway saved reports — confirm names)
- Aged Inventory
- End of Month (closing report)
- Company KPI Dashboard
- Chekkit Inactives composite
- Employee Activity
- Safe Register Journal
- Consolidated GL

---

## Open priorities (highest leverage first)

1. **Re-enable the orchestrator.** `monday-bravo-combined-run` is "Manual only." This is the keystone. Flip to a real Monday cron.
2. **Re-enable consumer tasks for working pipeline cells.** Loan/layaway review, aged inventory, employee rankings, FPD ranking — all the ⚠️ rows above.
3. **Build the customer-segmentation cell.** First new pipeline cell — needs criteria for Good / Mid / Bad / VIP. Joshua to define thresholds.
4. **Build the high-value-customer cell.** Lifetime revenue + last-visit, with contact info. Powers Brevo campaigns and store-manager outreach.
5. **Verify ❓ rows.** Next session with Bravo Data Extraction mounted, fill in handler names + CSV patterns by reading the dispatch tables.
6. **Design the IN side.** No automation today for customer notes, loan extensions, price overrides. Scope which actions are worth automating.
