---
name: monthly-bonus-qualifiers
description: Monthly (10th, 9 AM): pull all bonus qualifiers for the completed month from the live rails (email = Chekkit Invites range, reviews = weekly Monday pulls summed, gold = scrap buckets CLOSED during the bonus month, FB gains = Publer, rev = Bravo EOM), fill VP BONUS FINAL trackers' revenue actuals, append the month tab to VP_Bonus_Tracker_MASTER_2026.xlsx, post to #bonus-goals.
---

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access. That conclusion is false** and is the single most common cause of a false failure on this platform. If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.


> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. **The #bonus-goals post (Output item 2 below) has been simplified — the Bridge 1/Bridge 2/Tier-2-rule/QR-URL-assumption methodology now stays in the tracking spreadsheet and this file only; the channel gets a plain per-store result table.** If anything later in this file conflicts with this standard, this standard wins.


You are pulling the monthly store-level bonus qualifiers for Valley Pawn (Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro), matching Preston Peters' tracker methodology (`store_bonus_tracker_gold_tiebreaker_no_aggregate.xlsx`, shared 2026-07-16 — re-read its Settings/Inputs/Bonus Summary tabs if you need to re-verify). Additive task — doesn't touch monthly-bonus-targets, VP BONUS FINAL Updated.xlsx (read-only), or hardened Bravo infra. Read valley-pawn-context and bravo-context first.

## Standing fact — social platforms
Joshua confirmed 2026-07-16: **Publer is the system of record for Facebook and all other social platforms** (IG, TikTok, X, GBP). The `facebook-post` skill's direct Graph API tokens are dead infrastructure (confirmed by live check 2026-07-16 — every page token session-expired or access-blocked) and NOT how the business actually operates day to day. Never pull follower counts or post via raw FB Graph API tokens for this task or any qualifier calc.

## Standing fact — data source of truth (confirmed 2026-07-16)
**Never use QuickBooks/QBO as a source of truth for any KPI or revenue figure in this task, or anywhere in the bonus program.** Bravo and Bravo-extracted data (Company Performance / KPI reports, End-of-Month reports, Store Rankings exports) are the only source of truth for revenue, transaction volume, and every other business KPI used here. QBO's own categorization isn't reliable for this: a spot-check of June 2025 found the entire month's income sitting in an uncategorized "Ask My Accountant" bucket rather than a real Income account, with no store-level split at all. If Bravo data is unavailable for a given month, report the gap — do not fall back to QBO.

## Standing fact — "Revenue" definition (confirmed 2026-07-16)
The commission-basis "Revenue" figure Preston actually used, verified to match Bravo's own Company Performance report to the penny, is Bravo's native **Net Revenue** KPI: `Net Revenue = Pawn Service Charges (interest & fees, MTD) + Retail Sales Gross Profit Amt (MTD) + Scrap Sales Gross Profit Amt (MTD)`. This is a gross-profit-based figure, NOT raw/gross Sales, and it is NOT the same as VP BONUS FINAL's column D (2026 Revenue), which runs consistently $5,300–$9,900+ higher per store per month (confirmed via the June 2026 Company Performance report matching Preston's Slack commission figures exactly: Culpeper $66,649.27, Harrisonburg $61,666.31, Roanoke $36,906.77, Waynesboro $43,416.44). Pull Net Revenue from Bravo's "Company Performance" / KPI report (Store menu → Company Performance, or the Drive-extracted "BRAVO Company Performance.xlsx" pipeline output) whenever an actual per-employee or per-store commission basis is needed. VP BONUS FINAL's column D is a useful target-tracking figure for the Bridge 1/Bridge 2 gate logic below, but is NOT the number to multiply by a commission rate.

## Thresholds (confirmed 2026-07-16)
- Reviews Threshold: 12/month
- Email Threshold: 50.0%
- Gold Threshold: 100.00 dwt
- Social Media Threshold: per-store, scaled off real monthly transaction volume (see Category 4 — recompute every month, don't reuse fixed numbers)
- Top Performer Bonus pool: $300

## Four categories
1. **Reviews** — Chekkit (dashboard.chekkit.io, Reviews → Leaderboard), same method as `review-obtained-last-week` but summed over the full target calendar month.
2. **Email %** — numerator "Emails Captured" / denominator "Email Opportunities" from the Chekkit Inactives data the Bravo pipeline produces (same source `chekkit-weekly-review-requests` uses). Opportunities = total customer rows for the store that month; Captured = rows with a non-blank valid email. NOTE: "Email Opportunities" is NOT the same thing as total transaction volume — it undercounts real foot traffic (confirmed 2026-07-16, see Category 4). Do not reuse this figure as a transaction-volume proxy for anything else.
3. **Gold (dwt)** — VERIFIED 2026-07-16 by frame-extracting Preston's screen recording and cross-checking against his real Waynesboro number (matched exactly: 70.49 + 31.44 = 101.93). Requires Parallels/Bravo computer-use access — flag and report "NOT PULLED" per store if not granted this run, never guess:
   a. On the store's Bravo Dashboard, click **"Inventory Lookup"** → opens the **Inventory** module.
   b. Right panel → **"Scrap Refining Process"**.
   c. List columns: Created On, Name, Status, Status Date. Find CLOSED rows for the target month — naming isn't perfectly consistent (e.g. "JUNE 26 GOLD SCRAP" vs "GOLD SCRAP APRIL 2026"), match on Name containing the month AND "GOLD", Status=CLOSED. Two relevant rows per month: plain gold ("...GOLD SCRAP") and stone variant ("...GOLD WITH STONE SCRAP" / "GOLD STONES SCRAP..."). Ignore silver buckets.
   d. Open each → "Scrap Bucket Detail" screen → read **"Combined Metal Weight"** (dwt). Ignore "Stones Carat Weight" (different unit, not part of the dwt total).
   e. Store's Gold (dwt) for the month = sum of Combined Metal Weight across both buckets. Use `bravo-store-cycle` to repeat per store.
4. **Social Media** — REDEFINED 2026-07-16 (Joshua). NOT a Facebook/IG/TikTok follower-count metric — those accounts are either single brand-wide (IG @valley_pawn, TikTok @thevalleypawn, X — not store-attributable) or managed via Publer (not directly queryable here). Instead: **QR-code scans per store**, sourced from the front-counter QR sign → store-specific landing page → "$100 Every Month" giveaway entry form (name + email, one entry per person per month, rules live at thevalleypawn.com/giveaway-rules since 2026-07-15). Joshua's own framing 2026-07-16: "even if someone does follow us the goal is for the store to get that QR scanned" — scans (page views), not just eventual entries/follows, is the metric he cares about most.
   - **QR SCAN PROXY — RESOLVED 2026-07-16.** The physical in-store QR sign's exact encoded URL could not be directly confirmed (the Canva "Win $100 Monthly" flyer draft, design ID DAHNUh6fhr8, still has placeholder text "Visit reallygreatsite.com" — it was never finalized/printed, so it isn't proof of the live sign's target). Working assumption, applied until Joshua corrects it: the QR sign for each store points to that store's canonical WordPress page, titled exactly **"Valley Pawn {Store} — Pawn Shop in {Store}, VA"** (created 2026-04-19, one per store, thevalleypawn.com/wp-admin/edit.php?post_type=page). Track scans as that page's view count:
     - **Fastest method:** WP Admin → Pages list (`https://thevalleypawn.com/wp-admin/edit.php?post_type=page`) has a native **"Views: 30 days"** column per page — no Stats module needed. Snapshot as of 2026-07-16: Culpeper 14, Harrisonburg 18, Lexington 17, Roanoke 47, Waynesboro 54. This is a rolling 30-day window, not a calendar-month window.
     - **For an exact calendar-month figure instead of a rolling 30-day count:** use Claude-in-Chrome to navigate to `https://wordpress.com/stats/month/posts/thevalleypawn.com` (log in as needed), set the date-range picker to the target month's 1st–last day, and read each store page's view count from the "Most viewed" Posts & Pages table. The `wpcom-mcp-site` MCP's `statistics.get` operation CANNOT do this (site-wide totals only, confirmed via `describe` 2026-07-16, no per-URL breakdown) — browser navigation is required.
     - Report this as **"QR Landing Page Views"** per store per month — this satisfies Joshua's literal ask (scan volume) and should be treated as measurable and reported as a real number from here forward, not "NOT MEASURABLE."
   - **SEPARATE, still-open gap:** actual giveaway *entries* (name + email submitted through the form after scanning) are not yet confirmed to feed any queryable source (Sheet/Brevo list/etc.) — this is a distinct, narrower metric (conversion from scan → entry) from the scan count above. If Joshua ever wants entry-conversion tracked in addition to scans, that pipeline still needs to be built; report it as "Entries: NOT MEASURABLE YET — capture pipeline not built" separately from the now-resolved QR Landing Page Views figure. Do not substitute Deal-of-the-Week submissions or any other proxy for entries without Joshua's sign-off.
   - **Volume base and target methodology (corrected 2026-07-16 — Joshua flagged that "new customer" counts badly undercount real foot traffic):** pull each store's **End-of-Month (EOM) report** from the Bravo Data Extraction output (files named `{date}_{STORE}_end-of-month.xlsx`, refreshed via the Monday combined run / daily pipeline). Total front-counter transaction volume for the month = sum of:
     - Pawn Activity → "In-Store Total" (Qty of Txns: New Loans + Buys + Trade-Ins + Bought Tickets)
     - In-Store Txns → "Total"/"In-Store Subtotal" (Qty of Txns: Renewals + Partial Payments + Extensions + Redemptions)
     - Sales Activity → "Sales Total" (Qty of Txns)
     Do NOT include MobilePawn Activity qty — that's remote/app-based, not a physical front-counter visit where the QR sign is seen.
     If the EOM report only covers a partial month (e.g. mid-month pull), extrapolate to a full month by multiplying by (days_in_month / days_covered) — do not just use the partial-period raw count as if it were the monthly total.
   - **Target = 5% of that extrapolated monthly transaction volume, floored at 15/store/month.** This is intentionally a smaller percentage than a naive first pass (10%) because a large share of transaction volume is the same loan customers making repeat visits (extensions/renewals) in a single month, and the giveaway caps at one entry per person per month — 5% of the bigger, more accurate base nets out to a comparable, still-meaningful push versus lowballing off "new customer" counts alone.
   - **Reference point set 2026-07-16** using 7/1–7/15/2026 EOM data extrapolated ×2.07: Culpeper 65, Harrisonburg 60, Lexington 40, Roanoke 75, Waynesboro 75. These are a snapshot, NOT a fixed target — recompute fresh from that month's actual EOM transaction volume every time this task runs.
   - Threshold for "Social Threshold Met" going forward: compare **QR Landing Page Views** (the now-measurable scan proxy) against the Target above, since that's the metric Joshua actually wants tracked. If/when the entries pipeline is built, Joshua can decide whether to gate on scans, entries, or both.

## Tier logic
- **Tier 1 — TWO-BRIDGE GATE (redefined 2026-07-16 by Joshua; supersedes the old single-gate rule).** Source: `VP BONUS FINAL Updated.xlsx`, "2025 compared to Bonus" sheet — column B = prior-year (2025) same-month Revenue, column C = 2026 Bonus Target (computed by `monthly-bonus-targets`' Option B yield formula), column D = 2026 Revenue Actual. Note: the live file's binary has intermittently failed to download whole via the Drive connector (reproducible truncation on at least one occasion 2026-07-16) — if download_file_content fails or returns a file that won't open, fall back to `read_file_content` (text/values export), which works reliably, or use the rebuilt copy `VP_BONUS_FINAL_rebuilt.xlsx` as an interim reference.
  - **Bridge 1 (hard gate):** D >= C (store hit its 2026 Bonus Target for the month). **If Bridge 1 fails, the store's bonus is $0, period — do not evaluate anything else, do not fall through to Bridge 2, qualifiers, or Tier 2.**
  - **Bridge 2 (rate selector, only checked if Bridge 1 passes):** D >= B (revenue up year-over-year for that month). This determines which commission rate `monthly-bonus-payout` applies (the higher "hit Tier 2" rate vs the lower "missed Tier 2" rate) — it is NOT a second hard $0 gate on its own.
  - **Verified real-world impact (June 2026):** Roanoke failed Bridge 1 (Actual $42,193.38 < Target $47,164.52) — Benjie's actual June payment of $738.14 was computed under the old single-gate rule and should have been $0 under this corrected rule. Lexington passed BOTH bridges (Actual $24,977.23 >= Target $24,064.52, and >= prior-year $23,134.00) — Uriah was paid $0 in June under the old process but should have qualified for a bonus under this corrected rule. These are known, real discrepancies from before this rule was corrected — record them internally if the target month is June 2026, but do not retroactively re-issue pay yourself; only apply the two-bridge rule going forward from July 2026 onward, and flag any store where Bridge 1 fails in the internal tracker/DM so Joshua sees the $0 result explicitly rather than a silently-dropped row.
- **Tier 2** ("Task Bonus Hit", only evaluated when Bridge 1 has passed): For June 2026 and earlier — Reviews AND Email AND Gold thresholds met (3 qualifiers; Social Media didn't exist yet). **For July 2026 onward — all FOUR qualifiers** (Reviews, Email, Gold, Social Media/QR Landing Page Views). Social Media is now measurable (see Category 4 resolution above) — evaluate it like the other three, do not treat it as N/A going forward.
- **Category Wins**: per category (Email %, Gold dwt, Reviews, and QR Landing Page Views), the store(s) with the highest raw value win; ties = both win.
- **Overall Top Performer**: store with the most category wins; tie-break = highest Gold (dwt).

## Output — REWRITTEN 2026-08-03 per Field Communication Standard
1. Build/update a "Bonus Qualifiers" spreadsheet (columns: Store | Revenue | Goal | Revenue % to Goal | Revenue Goal Hit | Email % | Email Threshold Met | Gold (dwt) | Gold Threshold Met | Reviews | Reviews Threshold Met | Monthly Txn Volume (EOM) | QR Landing Page Views | Social Target (5% of Txn Volume, floor 15) | Social Threshold Met | Bridge 1 (Target Hit) | Bridge 2 (YoY Up) | Tier 2 Qualified | Category Wins | Overall Top Performer) in the Bonus Program Drive folder (id 1nR6j_0IL6Jqtn2pXlc4hqJjo_uahM7Ru), one tab per month. This spreadsheet is where ALL the methodology detail (Bridge 1/2, Tier 2 rule, QR-URL assumption, per-store gold-not-pulled flags) lives.
2. Post a SHORT, plain-language summary to `#bonus-goals` (C04TXF0KGNL) — a per-store table only, no Bridge/Tier/methodology language, no mention of the QR-URL assumption:
```
🎯 *Bonus Qualifiers — {Month Year}*

| Store | Reviews | Email % | Gold | Social | Hit Task Bonus? |
|---|---|---|---|---|---|
| Culpeper | ... | ... | ... | ... | ✅/❌ |
| Harrisonburg | ... | ... | ... | ... | ✅/❌ |
| Lexington | ... | ... | ... | ... | ✅/❌ |
| Roanoke | ... | ... | ... | ... | ✅/❌ |
| Waynesboro | ... | ... | ... | ... | ✅/❌ |

🏆 Top performer: {store}
```
   Any store's revenue target status ("hit" or "not this month") can be folded into the same table as a plain fact — never spell out Bridge 1/Bridge 2 by name in the post. If a store's gold data wasn't pulled this run, just leave that cell blank/dash rather than explaining why in the post — the reason goes in the spreadsheet and, if it needs Joshua's attention, a DM.
3. Keep the schema stable — `monthly-bonus-payout` reads this output directly.

## Failure policy
If Bravo/Parallels access isn't available, still complete Reviews, Email, and QR Landing Page Views target math (none need live access if a recent EOM export already exists in Drive, and WordPress Stats is browser-accessible independent of Bravo) and record Gold as not-pulled in the spreadsheet — partial completion beats silence. Do not narrate this gap in the Slack post; if it's material, DM Joshua instead.

<!-- QR scan tracking resolved via WordPress.com Jetpack Stats / WP Admin Pages view-count 2026-07-16 -->

## AUGUST 2026 REGIME CHANGE (announced by Joshua 2026-07-21 - applies to August earnings, paid September)
Effective with the August 2026 earning month, the task-qualifier set and rate logic change:
1. **New qualifier - Facebook follower gains (per store).** Data rail: **Publer analytics** (system of record for all social - never raw FB Graph tokens). Threshold per store TBD by Joshua/Preston before first August evaluation - flag if unset at run time (internally / via DM, not in the channel post). This REPLACES the QR-landing-page-views social proxy for qualifier purposes.
2. **New qualifier - Revenue YOY.** Store must beat same-month prior-year revenue by at least $1 (this formalizes Bridge 2 as an explicit task goal alongside Reviews/Email/Gold/Facebook).
3. **Penalty rule (symmetric).** Missing task goals is no longer just "no bump" - it is a **-0.5% penalty off the commission rate**. Manager: 2.5% (hit) / 1.5% (miss). Associate/Rep: per Joshua's 2026-07-21 statement the penalty is 0.5%; prior July-regime documentation showed the associate spread as 5%/3% - CONFIRM the associate miss-rate (3.5% vs 3.0%) with Joshua before the first August payout calc and update this line.
4. June/July runs are unaffected - use the regime rules above this section for any month <= July 2026.
## AUGUST 2026 REGIME - CONFIRMED DETAILS (Joshua 2026-07-21, second confirmation)
- **Facebook follower-gain threshold: +15 net new followers per store per month** (via Publer). Not TBD anymore - use 15.
- **Penalty structure confirmed via Manager example: Managers get 2.5% if they hit the task goals, 1.5% if they miss.** (Base 2% +/- 0.5%.) Applying the same symmetric +/-1% around base for Associates/Reps: 5% hit / 3% miss - consistent with the previously documented July+ spread; the "0.5%" figure refers to the Manager swing. The earlier CONFIRM flag in the section above is now RESOLVED: Associate miss-rate = 3.0%.

- **August 2026+: Reviews threshold raises from 12 to 15 per store per month** (Joshua 2026-07-21). June/July stay at 12.

## DATA-RAIL CORRECTIONS + PUBLER VERIFICATION (2026-07-21)
**Email % and Reviews come from the Monday combined run - do NOT re-pull separately:**
- Email %: the Monday combined Bravo run already pulls the "Chekkit Invites" custom report (chekkit-inactives/gridonly cells) weekly - it captures BOTH email and phone. Qualifiers task should read the accumulated Monday CSVs for the target month from the pipeline output / _shared-bravo-data folders (latest pull on/after month-end covers the month).
- Reviews: Chekkit review data is also already pulled every Monday (review-obtained-last-week + weekly digests). Use those weekly pulls summed to the calendar month; only fall back to a direct Chekkit leaderboard month-window read if a week is missing or a store sits on a threshold boundary.
**Publer Facebook follower rail - TESTED LIVE 2026-07-21, WORKS:**
- Path: app.publer.com -> Analytics -> Overview -> pick store account in left rail -> date-range dropdown (top right) -> "Last month" (= prior calendar month). Followers card shows total + net gain/loss badge for the period. Chrome saved session logs in automatically.
- Store account analytics URLs: Culpeper /#/analytics/overview/6a3596d3fe216c70f7e67261 · Harrisonburg /#/analytics/overview/6a3596d807e1b3bf83f1c379 · Lexington /#/analytics/overview/6a3596d4fe216c70f7e67266 · Roanoke /#/analytics/overview/6a3596d2bbd130d6e889bf58 · Waynesboro /#/analytics/overview/6a3596d789dea67771497918
- June 2026 verification values (vs +15 August threshold): Culpeper 876 (+1), Harrisonburg 763 (+1), Lexington 1.6K (0/no badge), Roanoke 35 (+1), Waynesboro 1.2K (-1). Every store would currently MISS the +15 bar - stores need a real follower push before August.

## GOLD ATTRIBUTION RULE - VERIFIED FROM BRAVO DATA 2026-07-21 (supersedes name-based matching)
Gold for bonus month M = gold buckets with Status=CLOSED and **StatusDate falling in month M** (Preston's physical collection run closes them). Attribute by CLOSE DATE, never by bucket name (names are inconsistent per store: WAY named its 7/20-closed buckets "JULY", CUL/ROA named theirs "JUNE") and never by CreatedOn.
Proof: June bonus gold per Preston = buckets closed 6/6 (HAR 66.35+26.10=92.45, ROA 30.61+28.70=59.31, WAY 70.49+31.44=101.93 - exact match to his tracker).
July 2026 bonus gold = buckets closed 7/20 (FINAL): CUL 128.63+148.02=**276.65 PASS** | ROA 53.29+42.37=95.66 | LEX 41.57+23.50=65.07 | HAR 34.80+25.89=60.68 | WAY 27.04+29.50=56.54. Only Culpeper passes the 100dwt bar for July.
Pipeline note: run scrap-refining-gold and filter output rows by StatusDate month = bonus month. The monthly qualifiers run (2nd) captures this correctly as long as Preston's collection happened during the bonus month (it did: 6/6, 7/20).
## SCHEDULE + OUTPUT TARGETS (set 2026-07-21, supersedes the 2nd/3rd schedule)
Both tasks now run on the **10th of every month** (qualifiers 9:00 AM, payout 11:30 AM), computing the just-completed month. The 10th gives time for month-end data to settle and precedes payday (first Friday after the 15th).
Required outputs each run - ALL of these, every month:
1. **VP BONUS FINAL trackers (BOTH copies)**: write the completed month's 2026 Revenue actual into column D of the "2025 compared to Bonus" sheet for all 5 stores, in BOTH files: `VP BONUS FINAL Updated.xlsx` (Drive, id 1AC-LF0gEPDLY0oUWZ7D1hCITt_xECHcx - the live file Preston uses) and the local `/Users/joshuadavis/Documents/Claude/Projects/Optimize Loan Portfolio/_input_VP_BONUS_FINAL.xlsx` reference copy. Revenue = Sales Revenue Profit + Interest & Fees Total from Bravo EOM (the verified methodology).
2. **Master tracker**: `/Users/joshuadavis/Documents/Claude/Projects/Bonus Program/VP_Bonus_Tracker_MASTER_2026.xlsx` - append/fill the month tab (qualifiers run) and payout lines + Trend + Running Totals refresh (payout run). Keep the existing tab schema exactly.
3. Slack: qualifiers summary to #bonus-goals (short plain table per Output section above); payout numbers DRAFT-ONLY to Joshua.

## FILE-ID CORRECTION (2026-07-21): the LIVE VP BONUS FINAL tracker is `VP BONUS FINAL Updated.xlsx` Drive id **1HKTWucLG8R2Yzgdm62vb2rrwYUTpntBB** (has Cumulative Variance + YoY Rev Var columns; targets refreshed monthly by monthly-bonus-targets). Id 1AC-LF0gEPDLY0oUWZ7D1hCITt_xECHcx is the 2026-07-02 BACKUP - do NOT write to it. Monthly runs must write actuals to the LIVE file (edit in Google Sheets via Chrome) + the local `_input_VP_BONUS_FINAL.xlsx` copy, keeping both in sync with live values.