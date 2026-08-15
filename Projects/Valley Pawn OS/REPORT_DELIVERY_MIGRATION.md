# Report Delivery Migration — Drive links → .xlsx uploaded into Slack

**Created 2026-08-14.** Inventory of every scheduled task that delivers reporting to a human via a
Google Drive/Sheets link or a document handoff, so the delivery layer can be rebuilt on
"generate .xlsx → upload directly into the Slack channel" per `BUSINESS_OS.md` Rule 13.

**Scope of the sweep:** all 106 registered scheduled tasks read in full, plus the 63 unregistered
folders under `~/Documents/Claude/Scheduled/` that registered tasks call as sub-skills.

---

## Headline findings

1. **Nothing emails a spreadsheet.** Category B is empty. There is no email-attachment path to
   retire — every document handoff is Drive-based.
2. **13 tasks post a Drive/Sheets link to a human. 8 more write a Sheet/.xlsx someone is expected
   to open. ~48 are already message-body-only and need no change.**
3. **The link-based delivery has been largely non-functional for staff the whole time.** Valley
   Pawn Drive only ever had 2 members (Joshua, Preston). Every Drive link posted into a staff Slack
   channel resolved to a "Request access" wall for everyone else. This is almost certainly why a
   pending *"Preston Peters asked to be an editor"* request was sitting on the intake-margin sheet.
   The pattern we're replacing wasn't working; it was just failing quietly.
4. **`pawn-walk` re-creates the exposure daily.** It runs 7:22 AM (`15 7 * * *`), uploads
   `{DATE}_intake_margin` to Drive, and posts the Drive link into **#pawn-walks**. That is exactly
   the file found shared to Preston as *writer* on 2026-08-14. **This is a recurring leak vector,
   not a one-off** — left alone it produces a new staff-visible Drive artifact every morning.
5. **Drive is load-bearing infrastructure, not just delivery, for the Monday stack.**
   `monday-bravo-combined-compile` saves 3 files that the five Monday Canvas tasks then read back
   **through the Google Drive connector, by title**. Change the producer without changing the
   consumers and all five Canvas refreshes break. Sequence this first.

---

## Category A — posts a Drive/Sheets link to a human (13)

| taskId | Reports | Cadence (cron) | Destination | Sheet/File |
|---|---|---|---|---|
| `pawn-walk` | Daily intake margin T1/T2/T3, item-level | Daily 7:22 AM `15 7 * * *` | **#pawn-walks** `C0B8WR95N31` + Joshua DM on flags | `{DATE}_intake_margin` (Items/Summary/Flags tabs) |
| `weekly-loan-review-canvas-refresh` | Past-due loans, 75-day rule, 5 stores | Mon 9:29 AM `20 9 * * 1` | Canvas `F0BH6BJ0PK7` in **#loan-review** | `1OwUddmK1BJRBMpnstXw1frFBPW36d6i9nXKVnUdahX8` |
| `weekly-layaway-review-canvas-refresh` | Layaway overdue/past-pmt/locate | Mon 9:24 AM `22 9 * * 1` | Canvas `F0BJ48BMZGQ` in **#layaway-review** `C04N24STDP1` | same Sheet as above |
| `weekly-employee-perf-canvas-refresh` | MTD employee sales leaderboard | Mon 9:26 AM `24 9 * * 1` | Canvas `F0BH9UK284S` in **#employee-performance** `C0ATTLPQHR8` | `1--Kn_2ybJCf6_PGnTdyMjCHBDsoEM4iCYPtokjHRIsg` |
| `weekly-aged-inventory-canvas-refresh` | Aged inventory by bucket, 5 stores | Mon 9:33 AM `26 9 * * 1` | Canvas `F0BHDL6AULU` in **#aged-inventory-review** `C04NGH4FF35` | `1aEatyu3YMfJcjIfcaIVHU9Lq8jOUtpH0Jd77LGDdvPM` |
| `weekly-store-perf-canvas-refresh` | Store rankings + 8 KPIs | Mon 9:37 AM `28 9 * * 1` | Canvas `F0BH6S9U5FX` in **#store-performance** `C03CGTN3KN1` | `1vpcnbR6V4YGHIrqP8GpHDL5LcciekDPA_Dq6FOHbCts` |
| `monthly-analytics-report` | 3 views × 6 metrics × 5 stores + YoY | 1st 1:47 AM `45 1 1 * *` | **#company-performance** `C0B26GD8D2R` AND **#store-performance** `C03CGTN3KN1` | New Sheet `Monthly Analytics - {Month Year}` in `1DYScQQl_dkkf3jGSBqNzGJKKv2uroFoh` |
| `eom-bravo-gl-export` | Consolidated GL, 5 stores | 1st 6:09 AM `0 6 1 * *` | Joshua DM (confirmation link) | `YYYY-MM Consolidated GL.xlsx` → `1FzXIRPNZHaECOwfaKpQDMUTPRY3-d12_` |
| `email-analytics-weekly` | Brevo per-link click KPIs | Fri 3:34 AM `30 3 * * 5` | **#email-campiagns** `C0APR5WUL2Z` | `1EPj22S1zzbSm4B_mRZ4y8TEXXpiCj6YM_75TmVV4d2o` |
| `nics-monthly-ranking` | FFL transfers ranked by revenue | 1st 9:34 AM `30 9 1 * *` | **#ffl-transfer-performance** `C0BPH5T1NFL` | `1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs` |
| `monthly-gun-audit-report` | Gun audit + error rates, rolling 12mo | 16th 2:32 AM `30 2 16 * *` | **#monthly-gun-audit** `C07CPN020G0` | "Valley Pawn Trends" `1sLid9zjLUkH-B8MOE5Fr_aemw35bxyAbtuUz4BTVA6s` (4 tabs, **updated by clipboard paste in Chrome — upload blocked**) |
| `monthly-amazon-store-allocation` | Amazon spend allocated per store | 6th 9:08 AM `0 9 6 * *` | Joshua DM `U03BB52MDSA` | `Amazon-Store-Allocation-{YYYY-MM}.xlsx` |
| `monthly-bonus-targets` | Next month's store bonus targets | 2nd 9:06 AM `0 9 2 * *` | Joshua (link); **#bonus-goals** `C04TXF0KGNL` draft only | `VP BONUS FINAL Updated.xlsx` live id `1HKTWucLG8R2Yzgdm62vb2rrwYUTpntBB` (stale id `1AC-LF0gEPDLY0oUWZ7D1hCITt_xECHcx`) |

## Category C — writes a Sheet/.xlsx a human is expected to open (8)

| taskId | Reports | Cadence (cron) | Destination | Notes |
|---|---|---|---|---|
| `monday-bravo-combined-compile` | Master Monday ops compile | Mon 8:00 AM (re-armed Sundays by `monday-bravo-combined-run` `0 18 * * 0`) | 6 Slack channels, data-only bodies | **Saves the 3 files the Canvas tasks read back via Drive. Fix first.** |
| `weekly-returns-summary` | Returns + refund-policy compliance | Mon 1:02 AM `0 1 * * 1` | **#weekly-returns-summary** `C0B1K4WK2HZ` (private) | Post deliberately short; detail lives in `Valley_Pawn_Returns_Trend.xlsx`. **Clearest single win.** |
| `monthly-employee-sales-rankings` | Final prior-month rankings | 1st 2:02 AM `0 2 1 * *` | **#employee-performance** `C0ATTLPQHR8` | Full ranking already in message body; .xlsx is "permanent record". Skill *forbids* naming the file in Slack |
| `sales-tax-monthly-update` | Taxable sales / eBay / taxes due | 1st 8:06 AM `0 8 1 * *` | Joshua DM | **Live filing workbook with formulas — do NOT replace, only add a Slack copy** |
| `monthly-bonus-qualifiers` | Bonus qualifiers per store | 10th 9:09 AM `0 9 10 * *` | **#bonus-goals** `C04TXF0KGNL` | Writes col D of both VP BONUS copies + `VP_Bonus_Tracker_MASTER_2026.xlsx` |
| `monthly-bonus-payout` | Per-employee bonus payouts | 10th 11:39 AM `30 11 10 * *` | Joshua DM only (dollar figures never public) | `Bonus Payout — {Month} {Year}.xlsx` → Drive `1nR6j_0IL6Jqtn2pXlc4hqJjo_uahM7Ru` |
| `layaway-yield-weekly` | Layaway Yield % MTD | Mon 11:20 AM `15 11 * * 1` | **#layaway-review** `C04N24STDP1` | Sheet-update step is **already a no-op** (no connected tool can edit it in place since 2026-07-15) |
| `vp-ai-visibility-metrics` | AI Visibility Index + GA4 referrals | Fri 9:00 AM `0 9 * * 5` | **#ai-marketing** `C0BCEESUANM` (no link posted) | Appends 1 row/wk to `17gkCl9BpB8yAQZcCs6cg8SDXQfaSGdyKceNJKfwMRMs` |

## Not spreadsheets — flagged, not migrating

| taskId | Cadence | Handoff |
|---|---|---|
| `northwest-registered-agent-daily-check` | Daily 8:03 AM `0 8 * * *` | Legal-notice PDFs → Drive `1WAYRYy2OXJXaVBYagpTrBys4ZYExUVn0`, viewUrls to **#registered-agent** `C0BMN275FD4` |
| `vp-hr-compliance-quarterly-review` | Jan/Apr/Jul/Oct 2nd `0 8 2 1,4,7,10 *` | `.docx` → "Policies & Handbook", summary to **#policy-announcements** `C03BHQ9RLR0` |
| `annual-board-review` | Jan 1 `0 0 1 1 *` | `.pptx` → Corporate Governance folder |

---

---

## DECISION (Joshua, 2026-08-14)

**"Whatever I am getting now I should be getting."** No loss of information in the migration —
every report keeps its existing content, cadence, and destination. Only the *transport* changes.

**Interim delivery = EMAIL ATTACHMENT.** The Slack MCP connector has **no file-upload tool**
(verified: it exposes send_message, send_message_draft, schedule_message, canvas read/create/update,
read_channel, read_thread, read_user_profile, search — and nothing else). There is also **no working
`SLACK_BOT_TOKEN` anywhere on this Mac** (confirmed 2026-08-14 in `pawn-walk`'s own notes), so the
`files.upload` API path is unavailable too. Therefore attaching .xlsx to Slack is impossible today.
Gmail `send_message` **does** support base64 attachments up to 25MB — that is the interim path.

**Joshua will set up a Slack app with `files:write` later.** Once that exists, the email step in
each task swaps to a native Slack upload with no other change. Build the email step so it is easy
to swap.

### Status

| Task | Status | Notes |
|---|---|---|
| `pawn-walk` | **DONE 2026-08-14** | STEP 5.5 rewritten: Drive upload removed entirely, now base64-encodes the .xlsx and emails it to jdavis@fcfpawn.com via the Gmail connector. STEP 6's Slack post keeps the full canonical `slack_message` body but the reference line now reads "📎 _Detailed item-level spreadsheet emailed to Joshua._" instead of a Drive link. Backup: `SKILL.md.bak-pre-email-2026-08-14`. Verified no residual `create_file` / `DRIVE_LINK` / `viewUrl` / `drive.google.com` references. **Not yet observed on a live run — check the 7:22 AM run.** |
| 5 Monday Canvas tasks + `monday-bravo-combined-compile` | Not started | **Must move as one unit** — the compile task's 3 saved files reach the Canvas tasks *through the Drive connector, by title*. |
| `weekly-returns-summary` | Not started | Cleanest standalone win |
| Monthly tasks | Not started | Mostly Joshua-DM-only already |

---

## Recommended sequencing

1. **`pawn-walk` first** — daily cadence, actively re-creating staff-visible Drive artifacts, and
   the proven source of the Preston writer grant. Highest exposure per unit of effort.
2. **`monday-bravo-combined-compile` + the 5 Canvas tasks as one unit** — the producer and its
   consumers must move together or the Monday stack breaks. Do not touch the compile task alone.
3. **`weekly-returns-summary`** — cleanest standalone win; the detail is *already* meant to live in
   a spreadsheet, it just isn't reaching anyone.
4. Monthly bonus/analytics/GL tasks last — lower frequency, mostly Joshua-DM-only already.

**Leave alone:** `sales-tax-monthly-update`'s workbook (live formulas, filing artifact) and
`layaway-yield-weekly`'s Sheet step (already a no-op). Add a Slack copy; don't replace the file.

**Also note:** several Category A tasks deliver only to Joshua's DM (`eom-bravo-gl-export`,
`monthly-amazon-store-allocation`, `monthly-bonus-targets`, `monthly-bonus-payout`). Those are not
staff-exposure problems — they're only in scope if Joshua wants the file in Slack for convenience.
