# Bravo Saved Reports & Layouts — Verified Catalog (Loans/Buys)

Started 2026-10-08 (pm-loan-growth build). Every row below was read from Bravo's own criteria dump
(`FwbDumpCriteria`, logged by FwbRun) or from the exported CSV — not guessed. Add to it whenever a
session learns what a saved report actually filters. Exact names are case-sensitive.

## Saved reports (Loans/Buys → Custom Reports → Choose Saved Report)

| Saved report | Verified criteria | Date override (FwbRun `from..to`) | Good for |
|---|---|---|---|
| **Claude Loan Portfolio 2026** | Ticket Kind = LOAN; **Create Date range** (pawn date); every disposition; rows 1000 (raise with rows=5000); sort PawnTime asc | YES — pos1/pos2 = create-date range, verified in CSV (pawn = today − Age) | Every loan written in a window, open or closed. Filter Disposition=ON LOAN for the open book. Keep windows ≈1 month per store (~150–450 rows). |
| **Loan Walk** (SHARED GLOBALLY) | Disposition = ON LOAN **AND Disposition Date = one day** (saved 9/28/2021) | Single date only (operator "=") | Open loans pawned on ONE day. Not a full open-loan list (returns 0 with the saved date). |
| **jewelry** (SHARED COMPANY-WIDE) | Jewelry loans **and buys**, Age 1–30 days; rows 250; sort PawnTime | no | Last-30-day jewelry intake only. |
| **75 Days Past Due** | Past Due Age > 75 | no | Weekly 5% rule (cells `loans-75-days-past-due`, `loans75-detail`). |
| **Claude First Payment Default** | On loan, past pull date, no payment | no | `fpd-cohort`. |
| **Claude Forfeiture Winback** | LOAN, EXPIRED, Age < 730 | no | Weekly win-back. |
| **Claude Loan Reviews** | Ticket Kind = **BUY**, Loan Amount $1–$5 (a clone of Low Dollar) — NOT a loan report despite the name | yes | Avoid for loan work. |
| Loans By Amount (SHARED GLOBALLY) | not yet read (layout pick failed on WAY 10/7) | ? | — |

**Gap (decided 10/8, not built):** no saved report returns *every open loan regardless of age*. Building one
("Claude PM Loan Growth": Disposition = ON LOAN, no date criterion, FDP layout, shared) is a one-time GUI save in
Bravo. Until then the open book = Claude Loan Portfolio 2026 in monthly create-date windows, keep ON LOAN.

## Column layouts (BoxColumns combo — applied per run by FwbRun `layout=`)

| Layout | Columns |
|---|---|
| **SHARED COMPANY-WIDE \| FDP** | Ticket Number, Category, Full Description, Disposition, Disposition Date, Due Date, Pull Date, Customer, Loan Amount, Age, MobilePawn, SMS, Last Payment |
| SHARED COMPANY-WIDE \| Full description and cost | Ticket Number, Category, Full Description, Loan Amount |
| SHARED COMPANY-WIDE \| Pawn Walk | Ticket Kind, Category, Full Description, Loan Amount, Associate |
| SHARED GLOBALLY \| High Dollar Loan Demographic | standard loan cols + Address |
| SHARED GLOBALLY \| Z-Bravo Regulation Escalation | incl. Create Date [PawnDate], Notice/Default dates, Category, Last Payment |
| (Customers) SHARED GLOBALLY \| Customer Address Check | Name, Phone, Address, E-Mail, Total Loans, Last Contact, MobilePawn, SMS |

Full dump of every layout's columns: `output/2026-09-29_CUL_fwb-layouts.txt`.

## Field meanings (verified 10/7–10/8)
- Rows are **per item**; `Loan Amount` is the item's share. Group by Ticket Number for ticket totals.
- `Age` on an ON LOAN row = days since pawn (create). Pawn date = run date − Age.
- `Disposition Date` on an ON LOAN row = the pawn date (it does NOT move when an extension is paid).
- `Due Date` − pawn date = 30 × (1 + paid extensions). `Last Payment` blank = never paid.
- Jewelry `Full Description` starts with weight + metal: `3.4DWT 14K-W/G`, `6.9DWT SILV-925`, `4.4DWT PLAT-950`;
  coins/bullion say e.g. `1 TROY OZ. SILVER ROUND`. Melt is computable from this text (1 dwt = 0.05 ozt).
- Other live dispositions besides ON LOAN: POLICE LOAN HOLD, COURTESY HOLD (exclude from offers).
- Spot prices: `Valley Pawn OS/spot_prices.json` (gold/silver only; daily 7 AM). Never hardcode.

## Running these through the pipeline
- Generic runner: `FwbRun(store, opts, outputDir, sidebar, savedReport, slug)` in `reports/ForfeitureWinback.ahk`.
  opts = `saved` or `YYYY-MM-DD..YYYY-MM-DD`, plus `|rows=N|tag=x|layout=<exact label>|stamp=YYYY-MM-DD`.
- Host-queue job lines may not contain `|` — bake options into a small handler (pattern: `reports/PmLoanGrowth.ahk`,
  cell `pm-loan-growth`, token `p:YYYY-MM-DD..YYYY-MM-DD`).
- `reports/PmLoanGrowth.ahk` has a runtime **pause switch**: while `pm_loan_growth.PAUSED` exists in this folder,
  every pm-loan-growth cell returns "paused" instantly without touching Bravo. Delete the file to resume.
