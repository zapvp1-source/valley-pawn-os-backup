# Sales Tax Automation — Plan of Record (DAVO-equivalent for Valley Pawn)

**Created:** 2026-07-20 · **Owner:** Joshua Davis · **Status:** Plan approved, Phase 1 ready to build

> **Canonical documentation home (Joshua directive 2026-07-20):** ALL Sales Tax Automation docs are
> saved to Google Drive → **Valley Pawn Drive / Bookkeeping / Sales Tax Automation /**. Mirror any
> new doc for this project there, not just in this local folder.

> Goal (Joshua, 2026-07-20): "A sales tax program that acts like DAVO but for my own business —
> take the money out daily based off the Bravo numbers, then submit the filing and funds to the
> Virginia Department of Taxation."

---

## The core reframe (why this shapes everything)

Virginia does **not** accept daily sales-tax filings. Form **ST-9 is monthly, e-filed, due the 20th**
of the following month, with electronic payment. DAVO itself does not file daily either — it only
**sets money aside daily** and files once a month. So this system mirrors DAVO exactly:

- **DAILY:** read yesterday's taxable sales from Bravo → sweep that tax amount from operating → a
  dedicated **Sales Tax Reserve** account.
- **MONTHLY (by the 20th):** file the ST-9 for the prior month and pay from the reserve.

## Decisions locked (2026-07-20)

| Decision | Choice |
|---|---|
| Build vs buy | **Build DIY** (DAVO can't read Bravo; we already extract the exact numbers) |
| Daily money movement | **Fully autonomous** sweep via programmable-bank API (own-account → reserve; not money transmission) |
| Daily amount sizing | **Fixed amount = prior month's total tax ÷ business days** (from the monthly workbook, eBay already netted). Not a daily data pull — "doesn't have to be exact," monthly filing squares it up |
| Monthly VA filing | **Hold-and-notify, 48h veto** — system stages the ST-9 + payment and files itself in 48 hrs unless Joshua replies STOP |
| Bank | **None opened yet** — board recommendation below; Joshua opens the account (Claude cannot open accounts or enter banking credentials) |

## What already exists (reuse — do NOT rebuild)

- `Sales Tax.xlsx` — monthly workbook, per store `Taxable Sales | Ebay | Taxes Due`, rate cell G1 = **5.3%** (4.3% state + 1.0% local).
- `sales-tax-monthly-update` task (6th of month) — already computes tax owed per store from the GL. **This becomes the monthly true-up reference.** Do not modify.
- `eom-bravo-gl-export` (5th) + `post-to-accounting-gl` pipeline cell — monthly GL tap. Do not modify.
- `EndOfDay.ahk` / `SalesAccounting.ahk` pipeline handlers — **the daily taxable-sales tap for Phase 1.** Reuse via the existing `end-of-day` cell, 1-day window.
- `daily-funds-verification` (6pm) — proven daily-cadence + trigger pattern to model on. Do not modify.

## Phased build (all additive — Rule #4)

### DESIGN SIMPLIFICATION (Joshua, 2026-07-20) — daily sweep sized from the MONTHLY number
The daily amount does **not** need to be exact — the goal is just "take the money out daily so the
reserve builds." So do **NOT** drive Bravo or the eBay API daily. Instead:
- **Daily sweep amount** = (most recent month's total Taxes Due, all 5 stores, straight from
  `Sales Tax.xlsx` / `sales-tax-monthly-update` — which **already backs out eBay**) ÷ business days in
  the month. Recomputed once a month when the new monthly figure lands; held fixed for the month.
- Because the source is the monthly number, **eBay is already netted out — no daily eBay backout, no
  daily Bravo pull, no computer-use.** The daily job is just: move a fixed amount + post to Slack.
- Accuracy is squared up by the **monthly true-up + ST-9 filing** (the exact number). Reserve lands
  approximately right daily; filing is exact.

### Phase 1 — Daily dry-run ledger (NO money moves) — READY TO BUILD
- New task `daily-sales-tax-sweep` in dry-run mode: each business day, post to a new `#sales-tax`
  channel: "would sweep $X today, reserve would be $Y" using the monthly-derived fixed amount.
  Appends to `Sales_Tax_Reserve_Ledger.xlsx`. Zero risk; proves the cadence while the bank is set up.
- Recompute the daily amount monthly from the latest `Sales Tax.xlsx` total.

### Phase 1.5 — Monthly daily-rate recompute
- Small step (or fold into `sales-tax-monthly-update` consumer side, additively): when a new monthly
  tax total is available, update the fixed daily sweep amount = total ÷ business days.

### Phase 2 — Autonomous daily sweep (money moves) — BLOCKED on bank account
- Flip Phase 1 out of dry-run: daily task calls the bank API to move the **fixed monthly-derived daily
  amount** operating → Sales Tax Reserve (instant internal own-account transfer).
- **Monthly true-up** reconciles swept total vs the official `sales-tax-monthly-update` ST-9 figure;
  corrects reserve for rounding / voids / refunds / eBay handling.
- Claude builds the logic + wires the API to a token Joshua provisions. Claude does not hand-execute
  transfers in-session or type banking credentials.

### Phase 3 — Assisted monthly ST-9 filing (hold-and-notify, 48h veto)
- New task `monthly-va-st9-prep` (~15th): assemble ST-9 with per-locality local tax, stage in VA Tax
  Online Services (Chrome, saved-password login), post "filing $X for [month] — submitting in 48h
  unless you reply STOP." Files + pays from reserve if no veto.

## Expert board — banking recommendation (Joshua hasn't opened one)

**PANEL:** sales-tax compliance CPA · fintech/payments engineer · pawn-shop operator · SRE.

- **⚠️ LOAD-BEARING CAVEAT:** most fintechs (Mercury, and many others) list **pawnbroking / lending /
  MSB as prohibited or restricted businesses.** The operating account that sweeps *from* belongs to
  the pawn business, and instant internal transfers require both accounts at the same institution —
  so the fintech must actually accept a pawnbroker. **Verify acceptance BEFORE relying on this path.**
- **Recommended primary: Mercury** — cleanest, best-documented API; instant free internal transfers
  between sub-accounts ("vaults"); no per-transfer ACH/NSF risk. *Contingent on pawn acceptance.*
- **Runner-up: Relay** — purpose-built for envelope/reserve budgeting (up to 20 checking + reserve
  accounts); API is newer/partner-gated. Also confirm pawn acceptance.
- **Fallback if fintechs decline the pawn business:** keep the existing traditional bank and add a
  treasury-API layer (Increase / Column / Modern Treasury) to originate the sweep, OR run Phase 1
  ledger + move the reserve manually once a month. Least automation, always works.

## What Claude will NOT do (safety boundary, stated plainly)
- Not open bank accounts; not enter banking or VA-Tax credentials into forms; not hand-execute a
  funds transfer or a tax payment inside a session. The deployed automation moves money under
  Joshua's standing pre-authorization using a token he provisions; the 48h veto gates the one
  irreversible government submission.

## JULY 2026 = go-live line (Joshua directive 2026-07-20)
Delinquency is real and is **why** we're automating. Joshua handles the **back-months himself**
(Sep–Dec 2025, Apr–May 2026). This system owns **July 2026 forward.**
- **July reserve target ≈ $7,750** (trailing-3-mo avg $7,723: Apr $7,702 / May $7,727 / June $7,739).
  Exact July figure computed ~Aug 6 by `sales-tax-monthly-update`; **file the actual, not the estimate.**
- **Deadline: file + pay July by Aug 18, 2026** (VA due date is the 20th; Joshua wants the 18th).
- **✅ Mercury APPROVED 2026-07-20 (Full Circle Finance) — Phase 2 UNBLOCKED.** Mercury `/transfer` API
  moves money between own accounts (minutes, same partner bank), gated behind a **Send Money write scope**.
  Pending from Joshua: (1) create a "Sales Tax Reserve" account/vault in Mercury; (2) generate an API token
  with Send Money scope, saved to `~/.vp_secrets/mercury_token` (NEVER pasted in chat). Then Claude pulls
  account IDs via API, builds the sweep, flips MODE→LIVE.
- **July catch-up:** one-time transfer to fund July to-date (~$7,750 target), then daily; true up to July's
  actual in early Aug. First live transfer is verified by Joshua before it moves.
- **`july-va-sales-tax-filing-prep`** one-time task (fires ~Aug 10): reads July's per-locality figures
  from the workbook and DMs Joshua the exact filing numbers + file-by-Aug-18 checklist.
- VA facts confirmed: monthly filer, due the 20th, per-locality allocation required, dealer discount for
  on-time filing (VA moved ST-9 → unified **Form ST-1** ~Apr 2025 period; portal shows the right form).

## Build log
- **2026-07-20 — Phase 1 BUILT & running (DRY-RUN).**
  - Engine: `Projects/Sales Tax/sales_tax_daily_sweep.py` — reads latest month from `Sales Tax.xlsx`,
    computes daily = total ÷ days-in-month, appends to `Sales_Tax_Reserve_Ledger.xlsx` (idempotent per
    date, running cumulative), mirrors ledger to the Drive folder.
  - Scheduled task: `daily-sales-tax-sweep` — daily 8:02 AM, DMs Joshua (U03BB52MDSA). No money moves.
  - First figure: **$249.63/day** (JUNE $7,738.56 ÷ 31). Verified end-to-end; DM sent.
  - `#sales-tax` channel not created (no channel-create tool); dry-run reports go to Joshua's DM until
    the channel exists, then the task repoints to it automatically.

## Mercury setup — LIVE (2026-07-20)
- **Token:** stored at `~/.vp_secrets/mercury_token` (Read+Write scope, IP-whitelisted 71.203.139.141 + IPv6 /64). Verified HTTP 200.
- **Accounts:** Checking ••7081 (`11a6d4d6-8466-11f1-956d-57e4581852be`), Savings ••2221 (`11e14cb0-8466-11f1-956d-7fc5d4b0fc93`), Checking ••3861 (`b757dabc-8469-11f1-bfb2-e31730d507ec`).
- **Sales Tax Reserve = Mercury Checking ••3861** (dedicated; clean for VA ACH debit).
- **Wells ...2797 linked** in Mercury as funding source (does NOT appear in API `/recipients` — that's expected; Plaid funding sources aren't recipients).
- **KEY CONSTRAINT:** banks don't expose external *pulls* to code. So the Wells→Mercury sweep is a **recurring transfer set up once in Mercury's UI**, NOT API-driven. Mercury API is used read-only (watch reserve balance) + internal transfers if ever needed.

## Funding cadence (Joshua directive 2026-07-20) — CONTINUOUS DAILY, starting today
- **Recurring transfer in Mercury: Wells ...2797 → ••3861, $250/day, start = 2026-07-20, no end date.**
- Sweep daily continuously — including right up through each payment. $250/day × ~31 days ≈ $7,750 in the
  reserve by the July due date (Aug 20). Each subsequent month accumulates before its 20th-of-next-month due
  date, pays out, refills. NO lump-sum needed; the daily cadence makes the timing line up.
- Daily amount resized monthly from the fresh `Sales Tax.xlsx` total ÷ days.

## Confirmed money flow (2026-07-20)
`Wells Fargo ...2797 (operating — sales + collected tax)` → daily ACH pull sized = month tax ÷ days,
Mercury-originated → `Mercury "Sales Tax Reserve"` (holds tax, separate) → at filing Joshua designates the
Mercury account as the VA payment source → `Virginia Dept of Taxation debits Mercury on the 20th`.
- Wells→Mercury is external ACH (settles ~1–3 business days) — fine; money still leaves Wells daily.
- Mercury does NOT auto-file/auto-pay: it holds the cash; Joshua files and VA debits Mercury.
- Joshua links Wells ...2797 as an external account in Mercury (his action; needs Wells login).

## Roles (Joshua directive 2026-07-20)
- **Claude = the sales-tax accountant:** compute, reserve, track, and hand Joshua the exact per-locality
  numbers each month. **NEVER contact Silverline / the outside CPA about anything.**
- **Joshua files the VA returns himself** and pays by the 20th of the following month from the reserve.
  So the automation reserves the cash + reports numbers; Joshua executes the filing + payment.

## Next action
- **Joshua (Mercury):** create "Sales Tax Reserve" account + generate API token (Send Money write scope)
  → save to `~/.vp_secrets/mercury_token`. Then ping Claude.
- **Claude (once token is in place):** pull account IDs via API, build the Mercury sweep (`/transfer`,
  SendMoney scope), flip MODE→LIVE, run the July catch-up (first live transfer verified by Joshua).
- **Phase 3 = monthly "here are your exact filing numbers" DM** (Joshua files). July version already
  scheduled: `july-va-sales-tax-filing-prep` (~Aug 10).
