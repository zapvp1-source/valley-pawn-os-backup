#!/usr/bin/env python3
"""One-time script: writes the initial gdrive_cache/latest.jsonl from content
fetched via the Google Drive MCP in a live Cowork session on 2026-08-10.
Not meant to be re-run automatically -- the daily Cowork scheduled task
appends/refreshes latest.jsonl going forward (see the unified-search skill
for that task's prompt). Run once: python3 build_initial_cache.py
"""
import json, os

HOME = os.path.expanduser("~")
OUT = os.path.join(HOME, "Documents/Claude/Projects/Unified Search/gdrive_cache/latest.jsonl")

ENTRIES = []

def add(name, folder, body, file_id, mtime, size, mime_type, kind):
    if kind == "doc":
        url = "https://docs.google.com/document/d/%s/edit" % file_id
    elif kind == "sheet":
        url = "https://docs.google.com/spreadsheets/d/%s/edit" % file_id
    else:
        url = "https://drive.google.com/file/d/%s/view" % file_id
    ENTRIES.append({
        "name": name,
        "folder": folder,
        "body": body,
        "path_or_url": url,
        "mtime": mtime,
        "size": size,
        "mime_type": mime_type,
    })

add("06 - TY2025 Filing Prep Tracker & Checklist", "MASTER TAX ARCHIVE", """TY2025 FILING PREP TRACKER — Full Circle Finance Inc (Valley Pawn) + Joshua & Hillary Davis

Built 8/4/2026 by Claude (Cowork). Companion to the MASTER TAX ARCHIVE (this folder) and the "Taxes" Claude Project (Tax Optimization Master Plan v19, Entity Structure & Setup Plan v7, Tax Numbers & Models, Tax Correction List, Working Notes). This is the action-oriented tracker scoped specifically to getting TWO returns actually filed for tax year 2025 — everything below still needs Silverline Tax's sign-off before anything is filed or elected.

0. SCOPE & CURRENT STATUS

Two returns in scope: Full Circle Finance Inc 1120-S (TY2025) and Joshua & Hillary Davis 1040 (TY2025, MFJ).

- Personal 1040: on extension, due ~Oct 15, 2026.
- FCF 1120-S: filing status/extension not confirmed in any source reviewed — S-corp original deadline was 3/16/2026; if extended, that runs to 9/15/2026, i.e. BEFORE the personal deadline. Confirm with Silverline whether it's already extended and to what date.
- 2025 FCF books: live QBO balance sheet pulled 8/4/2026, as of 12/31/2025 — internally balanced: Total Assets $1,388,543.66 = Total Liabilities $310,335.36 + Total Equity $1,078,208.30. Current-year Net Income component of equity: $361,100.93. Retained Earnings: $851,440.59. Shareholder Distributions: -$359,333.22.
- CAUTION: a live QBO profit & loss pull (not the balance sheet) in this same session returned internally inconsistent monthly figures — consistent with the MASTER INDEX's own warning that "the live QuickBooks Online API is unreliable for historical years." Use the static exports in "01 - Books & Financial Statements" for full P&L detail, not a fresh live pull, until that's reconciled.
- Open bookkeeping item: Documents/Claude/Projects/Quickbooks Set UP/VENDOR_DECISIONS.md lists ~11 recurring vendors still needing Joshua's categorization call before the 2025 books are truly final. Resolve these before handing off to Silverline.

1. CPA OF RECORD

Silverline Tax (successor to Lodestar Tax & Consulting LLC) — Jonathan Motel, Liana Motel, and Beth (all @silverline.tax). They prepared the 2024 personal and FCF returns (both later amended).

2. WHERE EVERYTHING ALREADY LIVES

- Drive "MASTER TAX ARCHIVE (Personal + FCF, All Years)" (this folder):
    01 - Books & Financial Statements (FCF, All Years 2017-2026)
    02 - FCF Business Tax Returns (1120-S) — filed 2017-2024
    03 - FCF Business IRS Transcripts — TY2021 only
    04 - Personal Tax Returns (1040) — filed 2019, 2021 (orig + amended), 2022, 2023, 2024
    05 - Personal IRS Transcripts
    06 - THIS TRACKER
- Claude Project "Taxes" — Tax Optimization Master Plan v19, Entity Structure & Setup Plan v7, Tax Numbers & Models, Tax Correction List, Working Notes, Retirement Roadmap, Whole-Org Optimization.
- Apple Notes "Taxes 2025" (created 9/27/2024, last edited 7/22/2026).

3. ENTITY MAP AT A GLANCE

- Full Circle Finance Inc (S-corp, EIN 47-1198118), DBA Valley Pawn — 5 VA pawn stores + Roanoke FFL. No real estate inside it.
- Farming Infinity, LLC (single-member, disregarded, on Sch E) — owns 817 Richmond Ave, Staunton, gross-leased to FirstCash.
- Three additional LLCs (Farming Infinity Tennessee / Virginia / Mountains) formed during 2026 for Hardinberry / Woods Walk / Bald Rock respectively.
- Joshua & Hillary Davis — MFJ, established Florida residency Aug 2025. TY2025 is a Virginia part-year resident return (Form 763) plus the federal 1040.

4. BUSINESS RETURN — FCF 1120-S, TY2025 — CHECKLIST

Books & payroll: final reconciled 2025 P&L + Balance Sheet; Bravo POS year-end reports reconciled to QBO; Gusto 2025 W-2s/W-3; any 2025 1099-NECs.

Elections & positions to confirm with Silverline: Virginia PTET election for 2025; reasonable-comp support for Joshua's officer salary; confirm whether FCF's 2025 return is already on extension.

Open questions: Section 179 on two vehicles (~$65K and ~$91K), the "ammo machine" purchase, HSA contribution ($8,500), distribution structure documentation, quarterly estimated-tax process, sale of the Fisker and Porsche in 2025 (Section 179 recapture exposure), QBI/§199A box-17 code-V linkage on the 2025 K-1.

5. PERSONAL RETURN — Joshua & Hillary Davis 1040, TY2025 — CHECKLIST

Income documents: W-2 (Joshua, via Gusto/FCF), FCF Schedule K-1 (2025), 1099-DIV/1099-INT, 1099-B for Porsche/Fisker sales, any 1099-R/1099-SA, Schedule E source docs for 14300 Woods Walk Ln, 148 Hardinberry St, 817 Richmond Ave, 282 Bald Rock Rd (STR conversion Aug 2025), 844 Cypress Crossing Trail (rental-to-primary conversion Aug 2025).

Bald Rock — locked to the 2025 return: FMV appraisal/BPO at conversion date (single most consequential open item); substantiate ~$305,000+ itemized improvements; cost-seg study; $3,200 energy-efficient home improvement credit placed-in-service date.

Virginia/Florida residency: Form 763 part-year resident return; FL homestead filing/DL/voter registration paper trail.

Retirement: confirm 401(k) sponsor/match; ask about retroactive 2025 Cash Balance plan adoption; max out 401(k) for 2025.

Other: First-Time Penalty Abatement (~$1,000-2,500 potential); TY2024 IRS balance was $39,274.54 as of 7/9/2026 transcript pull ($5K/month installment plan).

6. DOCUMENT INTAKE — business income/expense support -> "01 - Books & Financial Statements"; filed returns -> "02"/"04"; Bald Rock appraisal/cost-seg/improvements -> new "07" folder.

7. IMMEDIATE NEXT STEPS (none require a CPA): resolve VENDOR_DECISIONS.md items; chase the Bald Rock FMV appraisal; pull 2025 1099-B for Porsche/Fisker; confirm TY2024 IRS installment balance; send this tracker to Silverline Tax.

Prepared by Claude (Cowork) as an organizing tool, not a filed return or a CPA/legal opinion. Every item needs Silverline Tax's review and sign-off before anything is filed, elected, or claimed.""",
    "1ZTQAijLXKnjo8s36BYNVkJh0PWXmaqqNh0n0rhCoPQo", "2026-08-04T14:48:12.325Z", 6576,
    "application/vnd.google-apps.document", "doc")

add("Valley Pawn — Policies & Procedures", "Policies & Handbook", """Valley Pawn — Policies & Procedures

Full Circle Finance Inc DBA Valley Pawn. Master policy & procedure manual, living document. Owner: Joshua Davis (CEO) & Preston Peters (Operations Manager). Last updated: July 30, 2026.

1. eBay — Precious-Metal Jewelry Listings: Designer/Diamond/Gemstone Only (eff. 7/7/2026). Only designer/branded, diamond, or gemstone jewelry goes on eBay. Plain gold/silver sold by weight stays in the in-store display case. On 7/7/2026, 87 plain gold/silver listings were delisted (Roanoke 76, Lexington 7, Culpeper 4).

2. Jewelry Display — One-In, One-Out Procedure (eff. 8/3/2026, owner Preston Peters). Associates present one piece of jewelry to a customer at a time. Prompted by a July 25, 2026 loss-prevention incident at Waynesboro. Store Manager Roster: Culpeper - Sandra "Sandi" Cole; Waynesboro - Chadd McClintic; Harrisonburg - Walker Tapley; Lexington - Uriah Tiglao; Roanoke - George "Benjie" Moore. Escalation: Store Manager -> Preston Peters (Market Manager) -> Joshua Davis (CEO).

3. Jewelry Count: Daily Open/Close Procedure (eff. July 27, 2026). Jewelry counted at open and close daily; Store Manager and teammate alternate; closing count checked against Bravo activity; discrepancies escalate to Preston Peters same day.""",
    "1E1sJzUEMdI-Fb-nTt-59VfGRVFAuIr5KlVYXkvJSnwI", "2026-08-01T12:15:00.797Z", 6514,
    "application/vnd.google-apps.document", "doc")

add("Lean Model v2 — Key Numbers & Cost Sourcing", "Staunton Cannabis Project", """LEAN CASE v2 — recalibrated 7/22/26 after Joshua's challenge that v1 costs were padded for a 2,500 sq ft store.

Dispensaries average $974/sq ft/yr nationally (MJBizDaily). Model's $2.6M on 2,500 sq ft = $1,040/sq ft, right at the dispensary average. Driver: 350 licenses for 8.7M Virginians = ~1 store per 25,000 people.

What was padded in v1, cut in v2: Buildout $350K->$200K; Security install $75K->$50K; Security opex $85K->$45K/yr; Insurance $45K->$35K; Professional fees $60K->$40K/yr; Marketing $48K->$30K; Staff 8->6 FTE; Working capital $150K->$120K; contingency $60K->$40K.

Lean case results (280E still applied): Startup capital $675,000; 2027 H2: $715K rev, -$165K net; 2028: $2.21M rev, +$191K net; 2029: $2.60M rev, +$320K net; 2030: +$339K; 2031: +$360K. Payback inside Year 4.

Watch items that would make v2 wrong: CCA regs mandate on-site security guards (+$40-55K/yr); buildout/vault specs exceed assumptions; more than ~3 licenses land in Staunton/Augusta trade area; launch supply shortage persists past mid-2028.""",
    "11lCx_Zso2R3jsL2xfWxik4I5DILGSTWkfcGrgDcoIhs", "2026-07-22T20:24:07.556Z", 1688,
    "application/vnd.google-apps.document", "doc")

add("README — Staunton Cannabis Project Status & Open Items", "Staunton Cannabis Project", """STAUNTON CANNABIS RETAIL PROJECT — 817 Richmond Rd. Status as of July 22, 2026. Entity: new single-purpose VA LLC to be formed (separate from Full Circle Finance Inc).

Files: VA_Cannabis_Retail_Business_Plan_Staunton.docx; VA_Cannabis_Retail_Financial_Model_Staunton.xlsx.

Verified facts: framework enacted June 2026 via HB 30 budget compromise; retail sales begin July 1, 2027; 350 retail store license cap statewide before Jan 1, 2028, lottery selection, >=50% for Impact applicants; Staunton cannot opt out; taxes 6% state excise (->8% Jul 2029) + 1-3.5% local + 5.3% sales tax; medical operator dual-use conversion $10M one-time fee; seed-to-sale Metrc; 280E still applies to adult-use.

Fees: VA CCA has not published adult-use fee schedule. Model's $25K application+licensing line is a budget reservation benchmarked to other states (MD $5K+$25K, CT $5K+$25K, NJ $2K+$10K/yr, MO $3K+$11K/yr, OH $5K+$70K). Median VA expectation: $5K app + $10-30K license.

Do-now action items: form single-purpose VA LLC + EIN + bank account; Staunton zoning verification letter; GIS buffer exhibit; begin Labor Peace Agreement negotiation; engage cannabis regulatory counsel + 280E CPA; weekly monitor cca.virginia.gov.

Base-case financials (280E in force): Startup capital $900K; Yr1 (H2 2027) $715K rev, -$275K net; 2028 $2.21M rev, ~breakeven; 2029+ $2.6M rev, $145-175K net.""",
    "1WDLO4EoxF0r-b9Eus5xgBUXegBUMdeyPjQ9cSvVg7h8", "2026-07-22T19:33:45.532Z", 2215,
    "application/vnd.google-apps.document", "doc")

add("00 — MASTER INDEX (start here)", "Farming Infinity Entity Records", """FARMING INFINITY — ENTITY RECORDS MASTER INDEX. Last updated: July 21, 2026.

Sole member/responsible party (all entities): Joshua C. Davis. IRS mailing address: 844 Cypress Crossing Trail, Saint Augustine, FL 32095. Registered agent (VA): Joshua Davis, 282 Bald Rock Rd, Verona, VA 24482.

Quick status — 4 Farming Infinity entities, 3 EINs:
- Farming Infinity, LLC (original) — VA SCC S8306609, formed 05/30/2019, EIN status: confirm (possibly 81-3269313).
- Farming Infinity Virginia LLC — VA SCC 12045876, formed 07/13/2026, EIN 42-3980374 (issued 07/21/2026).
- Farming Infinity Tennessee LLC — VA SCC 12045877, formed 07/13/2026, EIN 42-3788196 (issued 07/13/2026).
- Farming Infinity Mountains LLC — VA SCC 12045879, formed 07/13/2026, EIN pending.

All four are Virginia LLCs, single-member, disregarded entities for federal tax (IRS name control: FARM).

Entity detail:
01 — Farming Infinity, LLC (original): property 817 Richmond Avenue, Staunton VA, acquired ~July 19, 2019. Fed ID 81-3269313 associated with 817 Richmond on property master sheet — needs confirmation.
02 — Farming Infinity Virginia LLC: EIN 42-3980374. Property (intended, confirm by deed): 14300 Woods Walk Lane, Chesterfield County VA.
03 — Farming Infinity Tennessee LLC: EIN 42-3788196. Property (intended): 148 Hardinberry Street, Oak Ridge TN 37830. Formed in Virginia though named Tennessee — may need TN foreign-LLC registration.
04 — Farming Infinity Mountains LLC: EIN pending — only remaining EIN to apply for. Property (confirmed): 282 Bald Rock Road, Verona VA (the Bald Rock short-term rental).
05 — Davis Management LLC (planned, not yet formed): Florida, members Joshua & Hillary Davis, LLC electing S-corp (Form 2553).

Property -> Entity map:
817 Richmond Ave, Staunton VA -> Farming Infinity, LLC (original) [confirmed]
282 Bald Rock Rd, Verona VA -> Farming Infinity Mountains LLC [confirmed — STR]
14300 Woods Walk Lane, Chesterfield County VA -> Farming Infinity Virginia LLC [to confirm/deed]
148 Hardinberry St, Oak Ridge TN -> Farming Infinity Tennessee LLC [to confirm/deed]
844 Cypress Crossing Trail, St Augustine FL -> Joshua's FL residence / IRS mailing address

Open items: apply for Farming Infinity Mountains LLC EIN; confirm deed transfers for FI Virginia and FI Tennessee properties; locate/confirm original Farming Infinity LLC EIN (possibly 81-3269313); draft operating agreements for the three new entities; confirm FI Tennessee TN foreign-registration need; form Davis Management LLC (FL) and file S-election on time.""",
    "17E-sxAieBjoz4wa0faemo5OuBgVqnGMtN7FiFDnZpMk", "2026-07-21T19:40:37.224Z", 2579,
    "application/vnd.google-apps.document", "doc")

add("Management Services Agreement (Template)", "Davis Management LLC", """DRAFT — FOR REVIEW BY LICENSED COUNSEL BEFORE EXECUTION

MANAGEMENT SERVICES AGREEMENT — Template, to be executed separately between the Manager (Davis Management LLC, a Florida LLC) and each Client entity.

Recitals: Manager provides administrative/back-office/management services; fees reflect fair market value at arm's-length.

Key terms: Manager determines means/methods/personnel (1); performs primarily from Florida offices, maintains records of where services performed (2); independent contractor relationship, no employment/partnership/agency (3); Management Fee per Schedule B, payable monthly/quarterly, reviewed annually for arm's-length FMV (4); 1-year term auto-renewing (5); records kept 7+ years (6); professional standard of care (7); confidentiality survives termination (8); mutual indemnification (9); limitation of liability capped at 12 months' fees (10); commercially reasonable insurance (11); compliance with law incl. FFL licensing (12); assignment/governing law/severability (13).

Schedule A — Services by client type:
A-1 Operating company (Full Circle Finance Inc): payroll admin, compliance/licensing admin incl. FFL support, bookkeeping oversight, HR admin, vendor/AP coordination, insurance admin, general back-office.
A-2 Short-term rental (282 Bald Rock / Farming Infinity Mountains LLC): listing/booking/reservation management, guest communications, cleaning/turnover/maintenance coordination, pricing/calendar/revenue management, compliance/tax-collection/insurance admin, bookkeeping.
A-3 Long-term/commercial rentals (Woods Walk, Hardinberry, 817 Richmond): lease/tenant admin, rent collection/bookkeeping, compliance/licensing/insurance admin, vendor/maintenance coordination.

Schedule B — Management Fee: must reflect arm's-length FMV; benchmark and document before execution. Note: do not set fees to hit a tax target — anchor to what an unrelated third party would charge.""",
    "1VfO3OQDI8andougCbNhyApV0sCUdvFdMbscmxwbslL8", "2026-07-21T19:39:32.806Z", 3877,
    "application/vnd.google-apps.document", "doc")

add("Davis Management LLC — Setup Checklist", "Davis Management LLC", """DAVIS MANAGEMENT LLC — SETUP CHECKLIST. Florida LLC taxed as an S-corporation — stand-up sequence for 2026.

Phase 1 — Form the entity (has a clock): file FL Articles of Organization for "Davis Management LLC" with Sunbiz; appoint FL registered agent; obtain EIN from IRS; adopt written LLC Operating Agreement (Joshua and Hillary as members); file IRS Form 2553 S-corp election within 2 months 15 days of formation for 2026 effect (late-election relief available under Rev. Proc. 2013-30 if missed).

Phase 2 — Operational setup: open dedicated business bank account IN THE LLC'S NAME; set up LLC's own bookkeeping (separate QBO file/class); set up Gusto payroll for Joshua and Hillary with reasonable W-2 wages for FL-performed services; benchmark management fees; execute Management Services Agreement with each client (Full Circle Finance Inc, Bald Rock/Mountains LLC, Woods Walk, Hardinberry, 817 Richmond); set invoicing cadence with real money movement.

Phase 3 — Tax & retirement: start FL work-location log/day-count for Joshua and Hillary; engage retirement TPA/actuary for Cash Balance + 401(k) plan design (must be adopted before fiscal year-end for 2026); coordinate VA PTET election for FCF; commission cost-segregation study on Bald Rock; confirm with CPA that 2025 set-aside funds are treated as Full Circle distributions.

Phase 4 — Governance: adopt corporate resolutions/minutes authorizing the management arrangement and fees; keep contemporaneous records of services performed and where (Florida); confirm insurance titled correctly per entity; calendar annual items.

The one rule that makes all of this hold: substance over labels. The Florida company must do real work, charge market-rate fees, move real money, keep its own books, document that work happens in Florida.""",
    "1CKTQZ95Ssi9lvGGVYdagehEVqwPKBJw5be0vHzUhRmI", "2026-07-21T19:38:59.068Z", 2118,
    "application/vnd.google-apps.document", "doc")

add("casual-video-pipeline_first-run-audit_2026-07-17.md", "Marketing / Automation", """Casual-Video Pipeline — First Live Run Audit (2026-07-17). Run context: cloud scheduled task vp-casual-video-daily, Mon/Wed/Fri 7 PM ET, from Claude Cowork.

Outcome: no-op, nothing processed, nothing published. Finding 1 (already known): cloud sessions have no bridge to the Mac Studio — structural for every cloud-scheduled run. Cannot reach project memory, PILLAR_OVERLAY.md, Bravo, Midjourney/Discord, Whisper/ffmpeg. Already reported to Joshua in Slack #vp-studio-queue. Recommendation: recreate as a local scheduled task on the Mac Studio.

Finding 2 (new): the Drive-mirrored SKILL.md for vp-casual-video-daily still drives casual_video_processor.py which imports PublerClient and calls it directly, bypassing vp_social_publisher.py — the exact anti-pattern that caused the 2026-07-11 incident (69% of historical posts shipped with empty caption, 90% blank on store-local pages). Rule #2: all Valley Pawn social publishing goes through vp_social_publisher.py, never call PublerClient.schedule_post() directly. casual_video_processor.py violates this and has no caption QA gate. Recommendation: before enabling local execution, rewrite casual_video_processor.py's publish step to emit a manifest and hand off to vp_social_publisher.py.""",
    "1-KmtSZGfxPyU0Zkp7iASmspINx8xgXQsvBBlRYDzm0g", "2026-07-17T23:11:58.326Z", 4039,
    "application/vnd.google-apps.document", "doc")

add("DRAFT - Giveaway Official Rules", "Marketing", """Valley Pawn "$100 Every Month" Giveaway — Official Rules. NO PURCHASE NECESSARY. Sponsor: Full Circle Finance Inc DBA Valley Pawn, 571 James Madison Highway, Culpeper VA 22701, five locations (Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke).

Eligibility: VA residents 18+; employees/family ineligible. Entry period: 1st-last day of each month. Entry: name + email at thevalleypawn.com/follow, limit 1 entry/person/month. Winner selection: random drawing ~last business day of month. Prize: $100 store credit/cash/gift card. Winner notified by email/phone within 5 business days, must respond within 7 days. General conditions, publicity consent, privacy, limitation of liability standard sweepstakes clauses.

Draft prepared 2026-07-14 to fill the broken "Official Rules" link (thevalleypawn.com/giveaway-rules, 404) referenced on all 5 store QR landing pages. Standard-form template, needs attorney review for VA sweepstakes/gaming law before publishing.""",
    "1NKg3ain-Jmra-W3U8ogEeLKqNtUWwDQOLLK524en3TY", "2026-07-14T22:10:34.068Z", 2462,
    "application/vnd.google-apps.document", "doc")

add("00 - MASTER INDEX (start here)", "MASTER TAX ARCHIVE", """MASTER TAX ARCHIVE — Full Circle Finance Inc (Valley Pawn) + Joshua & Hillary Davis. Built 7/14/2026. The ONE canonical place for books, tax returns, and IRS transcripts. Older scattered "Bank Application - Tax Package" folders (7/11/2026, 7/13/2026) are SUPERSEDED by this folder.

Folder map:
01 - Books & Financial Statements (FCF, All Years 2017-2026): native QBO exports, P&L/Balance Sheet/Trial Balance by year, exported 6/9/2026. Coverage full 2017-2026; 2025 provisional (bookkeeping cleanup ongoing). Live QBO API unreliable for historical years — always use static exports.
02 - FCF Business Tax Returns (1120-S): filed for every year 2017-2024 (8 of 8). 2024 is the amended version (e-filed 10/09/2025). 2025 not yet filed.
03 - FCF Business IRS Transcripts: only TY2021 exists. Gap: 2017-2020, 2022-2024 — requires Joshua's own IRS.gov Business Tax Account login.
04 - Personal Tax Returns (1040): full filed returns for 2019, 2021 (orig+amended), 2022, 2023, 2024 (6 of 7 years 2019-2024, 2020 excepted). Gap: 2020 full return — three password-protected copies exist on iCloud, password unknown; a Return Transcript substitutes.
05 - Personal IRS Transcripts: 2020 Return Transcript, 2022-2024 Return + Record of Account Transcripts (complete).

Live issues (as of 07-09-2026 pull): TY2024 personal IRS balance OPEN — $36,917.01 principal + $1,776.75 interest + $580.78 penalty = $39,274.54 total and growing. TY2022/2023 balances now $0 but history of dishonored payments. 2022 FCF "Total income" per filed 8879-CORP ($925,524) doesn't match QBO-exported 2022 Gross Profit ($1,079,434.70) — ~$154K gap, unreconciled.

What's genuinely missing: FCF business IRS transcripts 2017-2020/2022-2024; 2020 personal 1040 full return; 2025 personal and FCF returns (not yet filed, personal on extension to ~Oct 2026); 2025 FCF books (mid-cleanup).""",
    "15ToxceWn6tYC2dEPEpDRJTPKcoqpNMxMXy8Lt8QN9Aw", "2026-07-14T13:10:13.663Z", 2959,
    "application/vnd.google-apps.document", "doc")

add("Valley Pawn — Policies & Procedures", "Policies & Handbook", """Valley Pawn — Policies & Procedures. Full Circle Finance Inc DBA Valley Pawn. Owner: Joshua Davis (CEO) & Preston Peters (Operations Manager). Last updated: July 7, 2026 (earlier version).

1. eBay — Precious-Metal Jewelry Listings: Designer/Diamond/Gemstone Only (eff. 7/7/2026). Only designer/branded, diamond, or gemstone jewelry goes on eBay; plain gold/silver stays in-store. Trailing-12-month data shows plain gold/silver doesn't sell online. On 7/7/2026, delisted 87 plain gold/silver listings (Roanoke 76, Lexington 7, Culpeper 4). Bravo auto-ends eBay listing when counter sale posts.""",
    "13jivHrPdpkYyyPYDuGTFiSz_nuFnzrMIizSagSPkOGM", "2026-07-07T21:10:20.940Z", 3463,
    "application/vnd.google-apps.document", "doc")

add("WORK_IN_PROGRESS.md", "Valley Pawn Marketing", """Valley Pawn — Work In Progress. Last updated 2026-07-06.

Live and running: Publer-only publishing pipeline (3-layer safeguard); Deals-of-the-Week social flow (Wed 6PM cron); Weekly Brand batch cron (Mon 2:02 AM, incl. Twitter); MJ text-composite fix; memory files auto-loaded every session.

Blockers Joshua owns: Bravo inventory export was stale 2026-07-06, trigger before Sunday 9PM; Meta App restoration disabled at Meta level (unlocks analytics/comment-alert/boost-post when fixed).

Queued strategic build: Community pillar (15-20% weekly mix, local landmarks/events, no CTA); Humor pillar (10%, dry Shenandoah humor); Casual short-form video pipeline (phone-record -> auto-caption via Whisper -> Publer); Publer-native analytics loop (Friday 4PM digest).

Decisions locked: Publer is sole publisher, no Meta Graph API ever; Twitter/X mandatory on every Brand static; GMP policy Option A (Brand skips GBP); Joshua sees success DMs only, failures go to Claude.""",
    "1oJFDqdO4DGQPaOXkVOv4DhmJCx_Tiwr85eCno7Qgij8", "2026-07-06T20:46:55.350Z", 4966,
    "application/vnd.google-apps.document", "doc")

add("Visit_and_Procedure_Totals_2022-2025.md", "Personal / Health", """Healthcare Utilization Totals — 2022-2025. Source: UVA/MyChart encounters + procedures export; some Florida outpatient visits (Borland Groover GI, UF Health cardiology) may not be fully captured. Built 6/22/2026.

Encounters: 195 total. By year: 2022=86, 2023=36, 2024=56, 2025=17. By type: office visits (in person) 52, telephone contacts 79, hospital/imaging-day encounters 40, nurse-only 10, telemedicine 4, pre/post-procedure calls 4, surgical/procedure encounters 6. Actual provider visits (office+telemedicine): 56.

Procedures — 15 distinct: Cardiac (9): EP catheter ablation 8/20/2024; Echocardiograms x4 (6/3/2022, 11/2/2022, 11/6/2023, 3/7/2025); Nuclear stress test 8/5/2022; Holter monitor 6/13/2022; MCOT cardiac event monitor 3/29/2024; ZIO cardiac monitor 3/31/2025. GI (3): Colonoscopy 12/13/2022; Upper endoscopy (EGD) 12/13/2022 and 4/29/2024. Sleep (2): Sleep study 9/23/2024; Polysomnogram 1/7/2025. Vascular (1): Community vascular screening 4/21/2022.

Imaging: HIDA scan, esophageal manometry (3/2023), barium swallow x2, CT chest, cardiac CT/calcium, brain MRI+MRA, RUQ ultrasound, MRCP.

Bottom line: ~56 visits and ~24 procedures/studies over four years; the one untested category (small-fiber: skin biopsy + autonomic reflex testing) is the logical next step.""",
    "1ZhLp2rlQ5J0ljlS214JOVnDcVlNq1sLAFJuKo5JRE3I", "2026-06-23T16:20:13.994Z", 2867,
    "application/vnd.google-apps.document", "doc")

add("VISTAPRINT_PROOF_LEXINGTON.md", "Marketing", """Vistaprint Proof — Valley Pawn Acrylic Counter Sign. Lexington representative proof (4 other stores identical layout, different store name+QR). Product: Custom Acrylic Signs, clear acrylic 3mm, 8x11 vertical, UV-printed. Pricing: qty 5 (one per store) = $233.99 ($46.80/unit, 10% off); qty 10 = $443.99. Shipping: standard free (orders over $100). Mounting: no integrated easel, recommend separate acrylic easel-back stands from Amazon (~$15-20 for 6-pack). Combined cost ~$265-270 for all 5 stores. Remaining stores: Roanoke, Harrisonburg, Waynesboro, Culpeper, each own QR to their store page.""",
    "17_sEXUCwTwl0GY_u-NHIWRKU-1PptvyyqdKlvuSkWgo", "2026-06-22T19:46:36.348Z", 4568,
    "application/vnd.google-apps.document", "doc")

add("Email_UFHealth_RecordsRequest.md", "Personal / Health", """Records Request Email — UF Health Heart & Vascular, Nocatee (DRAFT). To: UF Health Heart & Vascular, 351 Town Plaza Ave Suite 203, Ponte Vedra FL 32081, (904) 342-8300. From: Joshua Davis, zapvp1@me.com. Subject: Medical records request — Joshua Davis (DOB 03/20/1973): recent echocardiogram + cardiac event monitor. Requests copies of most recent echocardiogram report and cardiac event monitor report. Verification: name Joshua Davis, DOB 03/20/1973, email zapvp1@me.com, phone 804-930-4221.""",
    "1winWXacUHLtMdUrC5MoG3xw_DLkDd1pXGooFamB0L8E", "2026-06-20T18:46:44.990Z", 2567,
    "application/vnd.google-apps.document", "doc")

add("META_SUPPORT_FINAL_SUBMISSION.md", "Marketing", """Meta Business Support — Final Submission (paste-ready). Subject: Reassign Admin access on Valley Pawn Waynesboro business portfolio (business_id 410777556554505) — no human admin.

Problem: only Full Control admin on Waynesboro sub-portfolio is an Instagram-derived non-human identity (@valleypawn_waynesboro). Joshua's personal FB account has only Partial/Basic access. Assets affected: Valley Pawn-Waynesboro FB Page (page_id 303444680270846) and Valley Pawn-Culpeper FB Page (page_id 100478091680300), combined ~2,100 followers.

Requested resolutions: (1) transfer both Pages to main Valley Pawn business portfolio (business_id 221863965111592); (2) assign Joshua's personal account Admin/Full Control on the sub-portfolio; (3) recover access to @valleypawn_waynesboro Instagram directly.

Verification offered: EIN 47-1198118 (Full Circle Finance Inc), Articles of Incorporation, recent Wells Fargo statement; main portfolio already Meta-verified. Reference IDs: main portfolio 221863965111592, sub-portfolio 410777556554505, user_id 2859397621061938, email zapvp1@me.com.""",
    "1wltAf2Sfn8oTgSYmTTOR_ArHdi-jnRHwKeKLH41Qo3M", "2026-06-19T18:42:43.449Z", 5472,
    "application/vnd.google-apps.document", "doc")

add("READ ME - signed FFL copies", "Compliance / ATF", """READ ME — Valley Pawn FFL copies (updated 2026-06-18). Signed current FFL copies for all 5 stores hosted on the website, used by the daily FFL transfer process:
Culpeper: FFL 1-54-047-02-6J-25407, exp 2026-09-01.
Waynesboro: FFL 1-54-820-02-8B-24709, exp 2028-02-01, SIGNED.
Harrisonburg: FFL 1-54-165-02-7M-26284, exp 2027-12-01.
Lexington: FFL 1-54-163-02-8F-26584, exp 2028-06-01.
Roanoke: FFL 1-54-770-02-7A-27330, exp 2027-01-01.
Notes: image files renamed 2026-06-18 to match actual license content (Culpeper/Lexington were swapped). Waynesboro unsigned copy in Drive folder — use the website copy (signed by Preston Peters, GM, 2/5/25). Culpeper's FFL expires 2026-09-01 — needs renewal before then.""",
    "1bB6vm77FKorzrbQhcbm5TJvs3TaAoawyivM79jJYaU4", "2026-06-18T13:17:36.346Z", 1123,
    "application/vnd.google-apps.document", "doc")

add("Valley Pawn — May 2026 Monthly Minutes", "Board Minutes", """VALLEY PAWN — MAY 2026 MONTHLY MINUTES. Full Circle Finance Inc. Period May 1-31 2026. Compiled June 9, 2026 by Claude (AI Assistant to Joshua Davis, CEO).

Financial results: PSC -1.3% YoY single-month in May but YTD +11.5%, T12M +12.8%. Early-month snapshot (May 1-3): Total Inventory Value $635,917, Total Loan Balance $599,099, Total Layaway Balance $98,110. Store rankings by net revenue: Culpeper $6,590, Roanoke $5,773, Waynesboro $4,904, Harrisonburg $4,449, Lexington $2,156.

Top employee sales (MTD May 29): Bridgett Grayson (Culpeper) $28,625; Walker Tapley (Harrisonburg) $20,560; Sandra Cole (Culpeper) $18,459; Benjie Moore (Roanoke) $15,895; Uriah Tiglao (Lexington) $15,009.

Loan policy compliance: ROANOKE OUT OF POLICY by May 29 (5.17% past-due vs 5% threshold). Aged inventory: company total $99,390 (15.05%) by May 29, Roanoke worst at 20.10%.

Staffing: new hires Emma Langford (Harrisonburg) and Timothy Thompson (Waynesboro), started ~mid-May. Silverline CPA bookkeeping service TERMINATED as of June 2026 — Joshua reviewing books directly going forward.

Issues: Chekkit hit 2,000-message billing cap May 10; Guesty payment data unreliable for VRBO bookings; Davidson's wholesale dealer application DENIED.

Bald Rock property May bookings: Kevin T. (VRBO, May 24-29, 5 nights, $2,931.17). Upcoming June: Lauren P. (Airbnb) $2,262.04, Heather B. (VRBO).

Note: this document contains sensitive business information, internal use only.""",
    "1rW7v2Fx6ob40MexuqwjVfBukJl20ltRmcjkcpg3NdCA", "2026-06-10T12:01:51.300Z", 6523,
    "application/vnd.google-apps.document", "doc")

add("bravo-report-inventory.md", "Valley Pawn / Bravo", """Bravo Report Inventory. Captured 2026-05-28 from a live Bravo session on Culpeper, Bravo v2026.2.2.3. Plain-English list of every report Bravo can produce.

Bravo reports live in 3 places: (1) master Reports page — 49 built-in reports in 5 categories (Closing 18, Inventory 8, Loan 9, Retail 2, Sales 12); (2) Reporting Pro panel — 4 dashboard tiles (Company KPIs, Store KPIs, Employee Activity, eCommerce Metrics); (3) Custom Reports per module (Loans/Buys has 19 saved reports today, e.g. "Claude Loan Portfolio 2026", "Claude First Payment Default", "75 Days Past Due").

Already-wired reports: Employee Activity (EmployeeActivity.ahk), End of Month (EndOfMonth.ahk, canonical cross-store financial source), Safe Register Journal (daily-funds-verification), Aged Inventory Summary (partial).

Next steps: walk Layaways/Inventory/Sales/Customers Custom Reports lists; decide wire-it vs skip per report; fill gaps with new handlers; schedule + prove unattended overnight runs.""",
    "17u4AU2rMKEG39Ti7FmyrJ6akq0PScauz65V1RivxO_E", "2026-05-28T12:46:45.955Z", 8457,
    "application/vnd.google-apps.document", "doc")

add("Bald Rock — Mountain Luxury Guest Guide", "Bald Rock STR", """MOUNTAIN LUXURY, 282 Bald Rock Road, Verona VA 24482. Guest Information Guide. 5 bed / 4 bath, sleeps 10, 4,200 sq ft, heated pool, hot tub, cold plunge. Hosted by Joshua & Hillary. Urgent contact: text/call Joshua (804) 930-4221.

Check-in 4PM, check-out 10AM, self check-in via garage lockbox, code sent day-of. Wi-Fi network "Mountain Luxury" password "RelaxHere". Well/septic — stagger showers, TP only.

House rules: no smoking/vaping, no pets, no parties, quiet hours 10PM-7AM, max 10 guests, min age to book 30 (ID verified), no shoes inside. Safety: CO/smoke alarms throughout, exterior cameras only (no interior), fire extinguishers under kitchen sink/downstairs/Master Bedroom, first aid kit in laundry cabinet.

Pool heated through Oct 15. 160-inch home theater with Apple TV and Xbox. Kitchen: KitchenAid appliances, Traeger Timberline grill. Nearest hospital: Augusta Health, 78 Medical Center Dr, Fishersville VA (~19 min). Emergency: 911; Host (804) 930-4221.""",
    "11TA_q8lAlcA5wdjqv3_wkpJ0oblfFqbr-NVtqX7Y04Q", "2026-05-24T15:20:07.341Z", 4256,
    "application/vnd.google-apps.document", "doc")

add("VENDOR_DECISIONS.md", "QuickBooks Set Up", """Vendor Decisions — bulk feedback for Session 9 EXTENDED cleanup. Recurring vendors needing categorization: Affirm ($1,619.67+), Jpmorgan Chase (Chase Card, possibly business vehicle lease), Zelle Rachael Ref ($400 x3+, Repairs & Maintenance guess), Sp Aff Aventon ($399.20, e-bike, personal), Sp Saunaspace Sauna ($223.65, personal), Servicemac Mtge Paymt (~$3,086/mo, personal mortgage/rent), Sumter Rental Ho ($2,420/$2,200, Roanoke rent), Applecard Gsbank ($1,000 x multiple), Online Transfer Full (Wells inter-account), PAM*ST JOHNS COUNT FL (Due To Farming Infinity per prior session), PURCHASE AUTHORIZED OTHER ($187.87, unknown).

Ebay Com mystery: ~50 entries in $26-36 range, Money In to WF 2797 — could be eBay sales settling, refunds, or personal eBay sales; needs investigation before categorizing.

Account structure: several $0 legacy loan accounts (Best Egg x3, Dupont Loan 0097, DuPont HELOC #0097) — default is leave active per prior session preference.

Open investigations: OBE at $859,972 (much higher than the ~$430K predicted, ~$429K unexplained, likely from prior plug entries); Bravo POS Clearing -$198,799.30 pending April 2026 Bravo GL re-import.

Expected outcome: another 100-300 rows clear automatically once rules apply, dropping Pending from 585 to ~300 or lower.""",
    "1oDnbncwblRIwGdoQLBLdj12Q7jbU_An2E7W9LqDR5Mc", "2026-05-11T11:57:08.714Z", 7714,
    "application/vnd.google-apps.document", "doc")

add("Valley_Pawn_Books_Cleanup_HANDOFF.md", "QuickBooks Set Up", """Valley Pawn Books Cleanup — Session Handoff. Last updated May 7, 2026. Source of truth: Books_Cleanup_Plan.docx.

Phase 2A.1 COMPLETE (May 7, 2026): AMA-Income contained 1,820 deposits totaling $1,926,926.22, all 2025, all bankcard settlements across 5 store merchant accounts. AMA-RECLASS-TO-CLEARING JE confirmed correct and kept. Fixed QBO rule: "Bankcard Settlements" now routes to Bravo POS Clearing with Auto-add ON (was previously wrongly set to Exclude, causing reconciliation gaps).

2026 Bravo Monthly GL Imports DONE (May 7, 2026): 5 store JEs built and posted, total $1,506,879.04 across CUL/HAR/LEX/ROA/WAY. Bravo POS Clearing went from -$193,152.69 to +$773,924.10.

End-of-session 2026 YTD P&L snapshot (May 7): Total Income $2,459,538.42 (Gold Revenue $557,664.71, Pawn Service Charges $574,876.50, Retail Sales $1,307,583.61); Total COGS $862,766.55; Gross Profit $1,596,771.87; Net Income $931,450.48.

Bank-feed rules saved: SSBTRUSTOPS->401K Traditional, CSS Home Service->Repairs & Maintenance, BEARSMANAGEMENT->Rent & Lease (HAR), Henry Liscio->Rent & Lease (WAY), Palencia->Conference Expenses, SERVICE FINANCE->Due To Farming Infinity, BANKCARD->Merchant Account Fee.

Bulk re-categorization: cleared 111 transactions totaling ~$162,500 (89.2% of $175K 2026 YTD Uncategorized Expense). Final verification: Net Income improved from $931,450.48 to $992,015.41 (+$60,565).

Critical gotchas: QBO journal_no field has 21-char limit; login "Verify it's you" always click "Enter password" not passkey; two QBO accounts — jdavis@fcfpawn.com (work here) vs zapvp1@me.com (READ-ONLY, never modify); MCP first, browser only when no other path exists.""",
    "1PBrJv7Fz654GyaGYlRpCJrXICeSHyaQzv5R7DmsGVwI", "2026-07-29T13:19:58.197Z", 16599,
    "application/vnd.google-apps.document", "doc")

add("Valley_Pawn_2025_Policy_Register", "Board Minutes", """FULL CIRCLE FINANCE INC DBA VALLEY PAWN — OPERATIONAL POLICY REGISTER. Exhibit A, 2025 Annual Board of Directors Review, FY Jan 1 - Dec 31 2025. Virginia S-Corporation.

10 policies issued/revised/reaffirmed in FY2025, all issued by Preston Peters:
VP-POL-2025-001/002/010: Large Loan/Large Buy Worksheet revisions A, B, C (Jan-Apr 2025) — Lending & Acquisition, two-tier review, valuation methodology, photo documentation requirement.
VP-POL-2025-003: Layaway Protocol (Jan 14, 2025) — 20% min down payment, 30-day payment intervals, 90-day full payment, forfeiture on cancellation.
VP-POL-2025-004: Return Policy (Feb 19, 2025) — 7-day return window, no returns on firearms/ammo/consumables, cash refunds over $50 need manager approval.
VP-POL-2025-005: Broken/Non-Functioning Firearm Storage Protocol (Mar 19, 2025) — ATF compliance, chain-of-custody.
VP-POL-2025-006: Multiple Handgun Sales Protocol (Mar 19, 2025) — ATF Form 3310.4 for 2+ handguns to same customer within 5 business days.
VP-POL-2025-007: MHG Acknowledgement Form (Mar 19, 2025) — customer-signed, additional to ATF form.
VP-POL-2025-008: PTO Policy Updated (Apr 9, 2025) — accrual rates, Gusto requests, carryover caps.
VP-POL-2025-009: Person-to-Person Firearm Transfer Clarification (Apr 16, 2025) — full ATF Form 4473 + NICS required, no exceptions.

Board resolution ratifies all 10 policies as formal corporate directives. Signed: Joshua Horne, Director, Full Circle Finance Inc.""",
    "1etO1C1rVE5uKF2MU7yrvWGpRfotxiLXz134tHwdk7x8", "2026-04-29T19:08:53.836Z", 18104,
    "application/vnd.google-apps.document", "doc")

add("_Cleanup_Notes.md", "Full Circle Finance Drive", """Full Circle Finance — Departmental Reorganization. April 27, 2026. Top-level department folders (alphabetical): Compliance, Executive, Finance, Human Resources, Marketing, Operations, Real Estate, Risk & Insurance, Strategy & M&A, Tax.

Compliance/: ATF (FFLs, SP-69As), Active Legal Matters (TimberlakeSmith subpoena), Audit, Bonds, Business License, Gold Buying Reports, Liens, Notices & Filings (BOIR), Pawn Regs, Precious Metals License, Virginia Sales Certs, Weights & Measures.
Executive/: Annual Reports, Articles of Incorporation, EIN, SCC PINS.
Finance/: Bookkeeping, Budget, Government Loans (incl. NEW BEST EGG LOAN.pdf), Monthly P&Ls, Promissory Notes.
Human Resources/: Forms, Gusto, Handbook Acks, Job Description, Legal Forms, Policy Acqs, ROCS, Write Ups, PTO docs.
Real Estate/: Leases, Landlord Letters of Recommendation, Lynchburg (Location) lease + ACORD.
Risk & Insurance/: Workers Comp (consolidated from 3 folders), General Liability, Loss Runs, Applications & Forms.
Strategy & M&A/: Acquisitions, Valuation, Preston Stock Sale (stock sale agreement + related estate docs).
Tax/: Corporate income tax returns 2020-2024, Payroll Tax (VEC), Personal Property Tax, IRS Notices, 2022 1099, W-9 docs, K-1 (JDavis Group), Form 8881, Vehicle docs (Fisker Ocean, Rivian, likely tax-deduction related).

Notes: Tax/Roanoke Adjustments.docx unclear if tax or operational; Tax/IMG_1058.jpeg and Scan2024-11-19_132322.pdf are generic-named scans, probably tax docs but need labeling.""",
    "1C8BVIwJ4uglT9NfwZ8lYppvjNEvH5q-RBkhV6Py_2RY", "2026-04-27T17:54:51.305Z", 7165,
    "application/vnd.google-apps.document", "doc")

add("Weekly KPI 3-23-26.3-28-26", "Valley Pawn / Bravo Reports", """Bravo Store Systems, Preston Peters, Valley Pawn Company KPI Report, Date Range 3/23/2026-3/28/2026.

Entire company: Inventory Base $626.56K, Layaway Balance $107.05K, Loan Balance $615.68K, Net Revenue MTD $228.00K, Net Revenue PTD $38.73K, Net Customers (365 days) 10.30K.

By store (Culpeper/Harrisonburg/Lexington/Roanoke/Waynesboro): Inventory $188,406.45 / $142,236.80 / $80,519.67 / $129,743.03 / $85,649.79. Loan Balance $149,487.17 / $162,376.87 / $74,483.35 / $127,503.95 / $101,824.48. New Buys Written Amt MTD $87,873.41 / $21,887.48 / $24,049.00 / $12,557.00 / $12,825.93. Retail Sales Total Amt $46,455.80 company-wide, Retail Sales Gross Profit % ranges 44-56% by store. Pawn Service Charges $107,049.13 company total. Net Revenue $183,959.20 for the period. Total Transaction Qty 726.""",
    "1ONFe6_myO1coF-4h0DjvNKt62NPi2fD_GYiWodWy4AA", "2026-03-30T18:40:27.056Z", 8011,
    "application/vnd.google-apps.document", "doc")

add("Renewal Alert Review your upcoming autorenewal.pdf", "Email attachments", """GoDaddy Renewal Alert email, August 8, 2026, to zapvp1@me.com. Customer Number: 94568051. Websites + Marketing Premium Renewal, Term 1 Year, connected to thevalleypawn.com. Bills on 8/23/2026, amount $275.89 (plus applicable taxes/fees). Payment method will be charged automatically unless cancelled via My Account before renewal date.""",
    "12p4RO7nMGc_xOmETOQPJbrIeWX1PcAPk", "2026-08-08T16:30:34.065Z", 94722,
    "application/pdf", "pdf")

add("Airbnb_TRUE_FIXED2.pdf", "Bald Rock STR", """Vacation Rental Agreement (Airbnb) — Joshua Davis, 282 Bald Rock Road, Verona VA 24482. Occupancy License Agreement, DocuSign. Check-in 4PM, check-out 10AM. No smoking ($3,000 fee), no pets ($1,000 fee), min age to book 30. Min stay 2 nights. Max occupancy 10. Damage policy: guest responsible, Joshua Davis inspects and charges card on file. Booking/payment via Airbnb. Notice address: 844 Cypress Crossing Trail, St Augustine FL 32095. Governed by Virginia law, venue Augusta County Circuit Court. Pool heater raises temp up to 15 degrees over ambient, max 90F, no refund if not to guest's liking. Firearms/weapons/ammunition prohibited on property, eviction + fee for violation. Pool/hot tub liability waiver and assumption of risk clause (age 30+ certification required). Contagious disease exposure waiver included.""",
    "13R-Nn8mRKgoU5YEKFspM5EKgsYAQDg2n", "2026-08-07T14:33:39.001Z", 143135,
    "application/pdf", "pdf")

add("VRBO_TRUE_FIXED.pdf", "Bald Rock STR", """Vacation Rental Agreement (VRBO) — Joshua Davis, 282 Bald Rock Road, Verona VA 24482. Occupancy License Agreement, DocuSign. Same terms as the Airbnb agreement: check-in 4PM/check-out 10AM, no smoking ($3,000 fee), no pets ($1,000 fee), min age 30, min stay 2 nights, max occupancy 10. Booking/payment via VRBO. Notice address: 844 Cypress Crossing Trail, St Augustine FL 32095. Governed by Virginia law, venue Augusta County Circuit Court. Firearms/weapons/ammunition prohibited. Pool/hot tub liability waiver, contagious disease exposure waiver, $5,000 fee for tampered pool alarm.""",
    "13WnYsILkhfGYLKLqc2cxW7ATbl92A7xr", "2026-08-07T14:34:01.423Z", 143331,
    "application/pdf", "pdf")

add("Valley_Pawn_2025_P_L_Comparison", "Finance / Bookkeeping", """Valley Pawn 2025 P&L Comparison — New Books (jdavis@fcfpawn.com) vs Current Bookkeeper (butterfliesllc).

Income: Gold Revenue $551,214.09, Pawn Service Charges $881,059.87, Retail Sales $1,829,938.12. Total Income $3,262,212.08 (new books) vs $3,276,785.86 (bookkeeper), difference -$14,573.78 (-0.4%, close).

COGS: $1,172,408.34 (new) vs $1,184,427.79 (bookkeeper), -$12,019.45 (-1.0%). Gross Profit $2,089,803.74 vs $2,092,358.07, -$2,554.33 (-0.1%).

Expenses (new books detail): Payroll Expenses $619,650.79, Uncategorized Expense $483,748.28 (857 transactions posted, need review/re-categorization), Taxes Paid $231,024.89, Meals & Entertainment $28,782.76, Subcontractor $28,346.41, Rent & Lease $101,344.75, Repairs & Maintenance $81,913.22, Store Supplies $74,865.56, Software & Apps $50,590.82, Best Egg Interest $21,245.83, Interest Paid $25,328.88, Travel $36,944.60. Total Expenses $1,899,277.45 (new) vs $1,637,926.02 (bookkeeper), +$261,351.43 (+16.0%) — the $261K expense gap is largely the $483,748.28 Uncategorized Expense needing categorization.

Net Operating Income $190,526.29 (new) vs $454,432.05 (bookkeeper), gap -$263,905.76 (-58.1%), driven almost entirely by uncategorized expenses awaiting review.""",
    "1G_5f-c0QuljP2ZoAj9ixtwWYLV_WXWfMlM19GJzsqkY", "2026-04-16T23:35:11.001Z", 3135,
    "application/vnd.google-apps.spreadsheet", "sheet")

add("Chart of Accounts - Valley Pawn - 2026-04-06", "Finance / Bookkeeping", """Chart of Accounts — Valley Pawn, 2026-04-06. Full Circle Finance Inc QBO chart of accounts.

Bank accounts: Business Checking (-S90), Business Checking 209, Business Main Share Savings (8-S0), PayPal Account, Petty Cash-Drawer, WF Checking 2797/3563/6507.
Other Current Assets: Coinbase, Deposits Clearing, Uncategorized Asset, Inventory Asset, Loans Receivable, Undeposited Funds.
Fixed Assets: Accumulated Depreciation, Furniture & Office Equipment, Gold-N-Pawn, Leasehold Improvements.
Credit Cards: Amex Card 3001, WF LOC 4116.
Liabilities: Best Egg Loan 11/07/24, Dupont Loan 0097, Layaway, Payroll Liabilities (incl. 401K Roth/Traditional), Best Egg Loan 3/22, Best Egg Loan 9/13/23, Dupont Loan 0500 ($43,000).
Equity: Capital Contributed - Shareholder, Capital Stock, Opening Balance Equity, Retained Earnings, Shareholder Distributions.
Income: Gold Revenue, Pawn Service Charges, Retail Sales, Sales, Service/Fee Income.
COGS: Cost of Goods Sold, Ebay Purchases, Guns-New, Pawn Payout, Police Confiscations, Shrinkage~Stolen/Broken.
Expenses (full list incl.): Advertising & Marketing, Automotive Expenses, Bank Charges & Fees, Casual Labor, Charitable Contributions, Insurance (incl. Owner's Health/Dependents Insurance payroll items), Interest Paid, Legal & Professional Services, Licenses & Permits, Meals & Entertainment, Office Expenses/Supplies, Payroll Expenses (incl. 401K, Wages), Rent & Lease, Repairs & Maintenance, Software & Apps, Store Supplies, Subcontractor, Taxes Paid, Travel, Uncategorized Expense, Utilities, Work Comp Insurance.
Other Income: Credit Card Rewards, EIDL Grant, Interest Earned, SBA PPP Loan - Forgiven.
Other Expense (needs review): Ask Kris ***, Cap In - Hillary Holmes - ITC, check to look up, CPA To REVIEW, Mortgage - Richmond Road, Officer Life Insurance, Reconciliation Discrepancies, Ring Replacement - ITC, Tuition Reimbursement *ASK CPA, YMCA - Code?.""",
    "1-zeT6aQfYoBdKQxaXJjJkmXMXMMfC6be0dkSaHleq9Q", "2026-04-08T21:46:09.945Z", 3807,
    "application/vnd.google-apps.spreadsheet", "sheet")

if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for e in ENTRIES:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print("wrote %d entries to %s" % (len(ENTRIES), OUT))
