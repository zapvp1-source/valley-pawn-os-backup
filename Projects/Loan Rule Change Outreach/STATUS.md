# Loan Rule Change Outreach — 75+ days late (Domain 1, Valley Pawn)

**Started:** 2026-09-30 · **Owner:** Joshua · **Why:** the 75-day past-due tolerance ends October 1, 2026 (P&P v2026.8 §06.01; Academy L3-06/M-01; HUDDLE_INPUTS F6 notes the expiration date may move to Sat 10/3). Every customer with a loan 75+ days late gets an email, a text and a push about the rule change.

## Status
- [x] 9/30 12:55–1:06 PM — loan-level list pulled from Bravo, all 5 stores (new additive cell `loans75-detail`, see below). 99 item rows, 66 tickets, **14 customers, $14,095**.
- [x] 9/30 — contact info joined (phone / email / address / MobilePawn / SMS flag) from the 9/30 Bravo Customers export. 14 of 14 matched.
- [x] 9/30 1:07–1:14 PM — cross-checked against Bravo's own Sum panel (weekly cell re-run): every store matches to the cent.
- [x] Workbook: `VP_75-Day_Past-Due_Outreach_List_2026-09-30.xlsx` (this folder; also in the session outputs). Rebuild any day with `build_outreach_list.py` after a fresh `loans75-detail` pull.
- [x] 9/30 1:57–2:06 PM — SENT (Joshua's go). 2 emails (Gmail as Joshua) + 10 texts (Chekkit one-to-one). Deadline communicated: **Sat Oct 3, 6 PM**. 4 not texted (Kondelis STOP; Preston/Baldwin/Strother Bravo DNT) → phone calls. Detail: `SEND_LOG_2026-09-30.md`.
- [x] 9/30 2:12 PM — Preston DM'd (ts 1790791964.222449): call Looney + Cooper Thu 10/1, plus the 4 no-text names.
- [ ] Push (Bravo Mobile Messenger) not sent — screen unmapped.
- [x] 9/30 6:08 / 6:12 PM — **Customer Loyalty Report pulled for both through the pipeline (no screen).** Looney: **$15,540 lifetime** (Sales Profit + PSC), $15,235 service charges / 487 charges, 20 loans written $4,715, rank #42 of 141,080, since 2022. Cooper: **$59,050 lifetime**, $49,668 service charges / 864, $3,485 retail GP, 405 loans $71,282 written, 364 redemptions, 5 forfeitures, rank #4, since 2021. Files in this folder. Cell `customer-loyalty` (v6) + saved skill `customer-loyalty-report` — Joshua's deal honored.

## Numbers (9/30)
| Store | Customers | Tickets | $ | Top customer | share |
|---|---|---|---|---|---|
| Culpeper | 0 | 0 | $0 | — | — |
| Harrisonburg | 4 | 19 | $3,090 | Richard Anthony Cooper II (15 tickets) | 64% |
| Lexington | 4 | 11 | $4,000 | Steven Paxton | 38% |
| Roanoke | 3 | 25 | $4,480 | Emmett Looney (14 tickets) | 77% |
| Waynesboro | 3 | 11 | $2,525 | William Boyd Hall Jr | 64% |
| **Company** | **14** | **66** | **$14,095** | Looney + Cooper = 39% of company | |

Monday 9/28's weekly review showed $20,209; the $6,114 drop by Wednesday is real (Bravo Sum panel agrees), i.e. the stores are working the list ahead of 10/1.

## How the pull works (reusable)
- Pipeline cell **`loans75-detail`** → `Bravo Data Extraction/reports/Loans75Detail.ahk` (5 lines; calls the proven generic `FwbRun` from `ForfeitureWinback.ahk` with sidebar "Loans/Buys", saved report "75 Days Past Due", full-capture grid walker + `.meta` expected/captured sidecar). Registered with two ADDED lines in `bravo_watcher.ahk` (backup `bravo_watcher.ahk.bak-pre-loans75-detail-2026-09-30`).
- Run it: host-queue job calling `bin/bravo_pull.sh loans75-detail saved CUL,HAR,LEX,ROA,WAY <id>` — ~1.5 min/store. Output `output/<date>_<STORE>_loans75-detail.csv`.
- New allow-listed host primitive **`bin/bravo_watcher_restart.sh`** (restart only the VM watcher when idle, verify it is back) — needed once, after registering a new handler.
- Contacts: `output/2024-08-30_<STORE>_forfeiture-winback-comparison-contacts.csv` (Customers module export, refreshed weekly by `com.valleypawn.forfeiture-winback` Sun 12:30). Join key = exact customer name within store.

## Caveats
- Bravo's saved criterion is **Past Due Age > 75** (strictly greater). Exactly-75-days loans join the list the next day. Saved report deliberately not edited (feeds the weekly review).
- The weekly `loans-75-days-past-due` cell's **count** is capped at the ~22 rows Bravo draws on screen (dollar Sum is fine). Logged in CHANGELOG + BRAVO_KNOWN_ISSUES 9/30. Fix-forward = use `loans75-detail` for counts.
- Rows are per item; tickets and customers are de-duplicated in the workbook.
