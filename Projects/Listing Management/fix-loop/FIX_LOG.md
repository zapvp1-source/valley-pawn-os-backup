# Listings Fix Loop — FIX_LOG (newest first)

## 2026-11-20 — daily run (scheduled, unattended, Joshua's Chrome) — 8 actions
- **Ingest:** no new presence scorecard (latest 11/15) or FFL_DRIFT (11/15) since 11/18; nothing new to add. No Thursday AI check (Friday) and no Saturday post.
- **SUBMITTED:** LQ-040 "since 1988" sources → emailed contact@pawnshopatlas.com (Since 1988 + Mon–Sat 10–6 on all our listings; phantom Staunton 817 Richmond, Salem 1617 W Main, Lexington 640 N Lee Hwy; Roanoke missing) and hello@baselocal.com (Roanoke blurb/JSON-LD "Family owned since 1988"). Pawn Spots Lexington re-checked: already clean. LQ-043 MapQuest Culpeper 438523385 verified at 641 James Madison Hwy with the old Yext "Salem / Dixie Pawn / GNP Pawn" description → added to MapQuest ticket #3229823 with LQ-028's Lexington ids 370030847 + 415053384. LQ-028 YP 549753098 (439 E Nelson) → added to the Thryv case (Thryv replied 11/20: forwarded to Client Care). check-replies run before each email (no prior threads except Thryv/MapQuest, replied in-thread).
- **STILL PENDING:** LQ-017 FB Gold N Pawn and LQ-014 valleypawnlex still live; no decision in Support Inbox (not rejected → no re-report yet). Re-check 11/24.
- **BLOCKED:** LQ-044 Bing shows Lexington open Wed 10–6 (regular hours, no holiday marker; Sat also 10–6 which is correct for LEX). Listing is claimed; Bing Places sign-in opens a popup outside the Claude tab group and never completes → blocked_signin, added to the Joshua row.
- **Sign-in probe:** Apple Business ❌ still signed out. Facebook ✅ (clicks work).
- **Note for playbooks:** Bing Places "Continue as Joshua" (Google) and "Microsoft account" both open popups Claude in Chrome can't reach.

## 2026-11-19 — daily run + Thursday AI answer check (scheduled, unattended, Joshua's Chrome) — 8 actions
- **AI answer check (GEO/AEO, first week):** Valley Pawn named in 20 of 20 city/engine checks; all 60 answers had the right name, address (Suite C / Ste 22), phone, hours and Wednesday status. 2 wrong facts, both "since 1988 / 30+ years" (Copilot Roanoke, ChatGPT Lexington). Full table: AI_ANSWERS.md. Copilot run through Bing AI Mode (copilot.microsoft.com redirects to the work M365 Copilot).
- **FIXED (proved live):** LQ-040 part 1: Facebook Valley Pawn-Roanoke (61553773147464, our page) bio said "Family Owned Pawn Shop since 1988!"; edited to drop 1988, re-fetched live. Switched back to Joshua's profile after. LQ-031: all 5 /<store>/ short pages are now noindex,follow (no longer duplicate /locations/).
- **SUBMITTED:** LQ-008 + LQ-009 YellowPages names → emailed support@thryv.com (rung 3, check-replies run, no prior thread). LQ-011 GunNook fee/hours → emailed support@gunnook.com (claim needs a new account; contact form has reCAPTCHA). LQ-013 mallsinamerica "Dixie Pawn" → emailed info@mallsinamerica.com. LQ-030 Google's stale /culpeper snippet → page is noindex now, Request Indexing rejected; waiting for recrawl (re-check 12/3).
- **ESCALATED / DECISION:** LQ-027 Manta Lexington (640 N Lee Hwy, unclaimed) — no contact path; only a new Manta account or aggregator push. LQ-026 BlueBook Roanoke — two listings both NAMED "GOLD-N-PAWN" (bigger than the typo); likely from the ATF license record, else a dealer claim (new account).
- **STILL LIVE:** LQ-028 YP 549753098 (our claim) still 439 E Nelson; MapQuest 370030847 (439 E Nelson) + 415053384 (640 N Lee Hwy). YP owner login needs a password (not used).
- **New rows:** LQ-040 (1988/30+ years, ai-answer), LQ-041 Henry dealer locator hours, LQ-042 Buya/CLOSO/Wheree Waynesboro hours, LQ-043 MapQuest Culpeper at 641 James Madison, LQ-044 Bing Places Lexington Wed (check vs 11/25 special hours).
- **Sign-in probe:** Apple Business ❌ still signed out. Facebook clicks WORK again today (were "permission denied" 11/18). BrightLocal not retried (extension permission).
- **Note:** valley-pawn-context skill still lists Waynesboro as closed Wednesday; RUNBOOK, live website, llms.txt and every AI engine say Waynesboro is a 6-day store (Mon–Fri 10–6, Sat 10–5). Kept the RUNBOOK facts. The skill needs updating.

## 2026-11-18 — daily run (scheduled, unattended, Joshua's Chrome) — 8 actions
- **Sign-in probe:** Yelp for Business ✅ · Facebook ✅ (page text readable; screenshots/clicks on facebook.com now "permission denied" in Claude in Chrome) · Apple Business ❌ · BBB ❌ (Continue with Google asks for the jdavis@fcfpawn.com password — stopped; did not try the gmail identity to avoid creating a new BBB account) · BrightLocal: Claude in Chrome not allowed on tools.brightlocal.com.
- **FIXED (proved live):** LQ-023 Loc8NearMe Roanoke — now Valley Pawn, Ste C, open, Sat 10–5, clean description (evidence/2026-11-18_loc8nearme_roanoke.txt). The 10/20 owner correction landed.
- **SUBMITTED:** LQ-038 (new) Loc8NearMe Harrisonburg description still says "Dixie Pawn … Salem" → owner Suggest an Edit sent. LQ-020 Yelp Staunton ghost → public "Permanently closed" report, Yelp: "moderators will take a look" (listing is claimed by someone else, logo "Valley Pawnbroker Inc", phone 540-885-0018 — check it's not a separate real business before escalating). LQ-010 FFLeasy Harrisonburg → contact form rename request ("Email is sent").
- **STILL PENDING:** LQ-017 FB Gold N Pawn and LQ-014 valleypawnlex both still live; no report decision visible in Support Inbox. Re-check 11/20.
- **BLOCKED / ESCALATED:** LQ-022 Yelp Harrisonburg category — Yelp has no web support form any more (phone only); next = BrightLocal category push (needs Chrome allowed on BrightLocal). LQ-008/009 YellowPages names — YP feedback form has reCAPTCHA, Thryv form requires a privacy-statement checkbox; not done. Next = a Thryv support email, else BrightLocal aggregators (LQ-002). BBB LQ-004–007 → blocked_signin; next run tries rung 3 email to BBB Western VA.
- **Ingest:** presence scorecard 11/15 + FFL_DRIFT 11/15. New rows LQ-038 (Loc8 HAR description), LQ-039 (GunMade HAR "Dixie"). FFLs.com HAR resolved per scorecard (not a queue row). GunMade Salem dropped off drift — watch.

## 2026-11-17 PM — Joshua approved; loop registered
- **Daily task registered:** "Listings fix loop (daily)", Mon–Sat 3:37 PM ET, on the Mac Studio, approvals automatic. First run 11/18.
- **Facebook reports filed** (Joshua OK'd): Gold N Pawn 100041735065936 reported as impersonating Valley Pawn-Roanoke; valleypawnlex reported as impersonating Valley Pawn-Lexington. Both "awaiting review". Re-check 11/18.
- **BrightLocal (now signed in):** 4 of 5 locations have Active Sync with correct data; Waynesboro has none. Aggregators inactive everywhere (paid). Joshua decision.
- **Apple Maps VERIFIED:** Culpeper, Roanoke (Ste C), Waynesboro hours correct; Salem gone from descriptions. Harrisonburg hours correct but missing Ste 22.
- **NEW:** unclaimed Apple duplicates at Roanoke and Harrisonburg (the Harrisonburg one shows Wed open). Needs the Apple Business sign-in.

## 2026-11-17 — first pass (interactive session, Joshua's Chrome)
- Sign-in probe: Yelp for Business ✅ signed in · Facebook ✅ · Apple Business ❌ (Apple Account + 2FA) · BrightLocal ❌ (Google SSO didn't complete) · BBB ❌ (try Continue with Google next run).
- FIXED (proved live): LQ-015 2nd Culpeper FB = same page · LQ-016 dixiepawnhburg FB gone · LQ-018 Waynesboro FB id = same page · LQ-021 Yelp Gold-N-Pawn Roanoke → Valley Pawn, Ste C, right hours · LQ-034 all 5 Yelp hours correct + Waynesboro duplicate merged.
- PARTLY: LQ-017 one Gold-N-Pawn FB page gone; 100041735065936 still live with our Roanoke phone → needs Joshua OK to report it (the report was blocked pending his approval).
- NOT OURS: FB 100057490088122 / 367260950022473 = Valley Pawn, Waynesville NC.
- NEW FINDING: FB valleypawnlex = our old Lexington page, still at 640 N Lee Hwy, and we don't have admin.
- ESCALATE NEXT RUN (rung 3): LQ-022 Yelp Harrisonburg category (2 removals ignored) → Yelp support · LQ-020 Yelp Staunton ghost (not in our account) → Yelp support · LQ-008/009 YP name locks → YP feedback form / Thryv.

- 2026-11-19: LQ-004/005/006/007/012/039 set to tracking - claimed by the BrightLocal/aggregators chat (BBB + FFL directory corrections). Joshua: home address must not appear on any FFL directory; ATF mailing address stays at home.
- 2026-11-19: claims released. LQ-007 FIXED (BBB Bald Rock removed, verified 404). LQ-004/005/006 emailed BBB W.VA (Lesley Shelton). LQ-012 emailed MasterFFL support (hide home mailing address on all profiles; Roanoke phone/suite). LQ-039 + Roanoke 2362-D sent via GunMade contact form.
- 2026-11-19: RUNBOOK v1.1 - added Wednesday weekly search review (GSC, Bing WMT, GBP Performance, Apple insights -> up to 3 SEO improvements/week, measured next week). Retracted the 2362-D change requests to MasterFFL/GunMade.
