## 2026-08-03 (eom-bravo-gl-export live run -- GL fix NOT verified solved)- Ran eom-bravo-gl-export for July 2026. Step 1 (post unposted days): all stores clean except 7/31, which failed to post on ALL 5 stores across 2 retries this session ("could not click Post button") -- persistent, not a one-off wedge. Step 2 (GL export): the Continuous-Scrolling toggle-off fix applied to PostToAccountingGL.ahk earlier today did NOT resolve the render hang -- 5/5 stores failed identically to before the fix ("Consolidated GL preview did not render within 60s"). Zero GL CSVs obtained. Do NOT mark that fix SOLVED -- see BRAVO_KNOWN_ISSUES.md 2026-08-03 PM entry. Steps 3-5 (combine workbook, Drive upload, QBO journal entry) skipped -- no source data, per forensic-accountant no-data-no-entry standard. Joshua DMed per failure policy (no Slack channel post). This also blocks sales-tax-monthly-update the same way.

# Valley Pawn - Enterprise Changelog

Newest first. Material changes to the business operating system. Read this BEFORE any build, fix or diagnosis.

## 2026-08-03 (post-to-accounting-gl hang fix + reliability watchdog)
- ROOT CAUSE CONFIRMED for the ~24-26 day per-store unposted-days backlogs seen in eom-bravo-gl-export: NOT a staffing/manager gap (a prior session's Harrisonburg-no-manager theory was checked against live data and doesn't hold — Culpeper, a normally-staffed store, showed the same-size backlog in the same run). Real cause: `reports/PostToAccountingGL.ahk`'s Consolidated General Ledger preview hangs on render for every store (100% failure, ~50 min wasted 2026-08-03 AM) because it never got the "Enable Continuous Scrolling" toggle-off fix already applied to 7 other closing-report handlers on 2026-05-29. See `Bravo Data Extraction/BRAVO_KNOWN_ISSUES.md`.
- FIXED: ported the toggle-off block verbatim into `PostToAccountingGL.ahk` (backup: `.bak-pre-cs-fix-2026-08-03`). NOT YET LIVE-VERIFIED — next `eom-bravo-gl-export` or `sales-tax-monthly-update` run must confirm and stamp SOLVED in BRAVO_KNOWN_ISSUES.md.
- ADDED: `eom-bravo-gl-export-watchdog` scheduled task (day 2 of month, 8 AM) — verifies the GL export actually ran AND produced dated output on the 1st; DMs Joshua only if it didn't. Additive, does not touch the primary task.
- `eom-bravo-gl-export`'s registered cron is already correct (`0 6 1 * *` — the 1st, 6 AM). BUSINESS_OS.md's hand-written infra table still says "5th of month" — doc drift, not yet corrected there.

## 2026-08-03 (sales-tax-monthly-update blocked)
- sales-tax-monthly-update (July 2026) BLOCKED: post-to-accounting-gl (Consolidated General Ledger) hung on preview render for every store attempted (CUL 3/3, HAR 3/3 failed, ~50 min of retries + health-gate recoveries), so zero GL CSVs were obtained and Sales Tax.xlsx was NOT updated this cycle. Root cause matches the known-but-unpatched "Continuous Scrolling" wide-report hang (see bravo-context) — PostToAccountingGL.ahk needs the same toggle-off patch already applied to the 7 closing-report handlers on 2026-05-29. Full writeup in Bravo Data Extraction/BRAVO_KNOWN_ISSUES.md (2026-08-03 CRITICAL entry). Posting phase also left 7/31 unposted for HAR/LEX/ROA/WAY — needs Joshua's/Preston's attention before any other end-of-July report runs.

## 2026-08-03 (comms standard)
- Field Communication Standard v3 created: `Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Governs every scheduled task that posts to a team channel or employee DM — routing test (internal vs field-facing), plain language, no tool/system names, no file paths, ~100-word cap, no failure notices, no signature footers.
- Comms audit found 27 team-facing tasks; worst offenders were #jewlery-counts (build-log content), #weekly-returns-summary (900-word audit posts), #company-performance (methodology narration), #layaway-review (process asides). Cleanest models: #google-reviews, #items-to-price, #deal-of-the-week.
- All 27 team-facing task files updated via `update_scheduled_task` to point at the v3 standard; 4 Tier-1 fixes applied where a file's body contradicted its own failure-routing rule (jewelry-count-reconciliation, pawn-walk, weekly-loan-layaway-manager-dms, vp-new-customer-report); 5 worst-offender output formats rewritten to plain short posts; `vp-hr-policy-monthly-sync` routing fixed so its audit summary goes to Joshua's DM, never #policy-announcements.
- New scheduled task `vp-comms-drift-monthly-check` (3rd of month, 8 AM) added — reads team channels monthly, DMs Joshua a drift digest against the v3 standard. Read-only; never posts to a team channel.
- KNOWN LIMITATION: the "Sent using Claude" footer seen on automated Slack posts is added by the platform/session layer, not by any SKILL.md prompt — it could not be removed via task-file edits in this pass.

## 2026-08-03 (VA pay-transparency remediation)
- ROOT CAUSE FOUND for Publer API 403s: Publer sits behind Cloudflare, which returns `error code: 1010` to requests with no/`Python-urllib` User-Agent. The API key and the `Bearer-API {key}` header format were CORRECT the whole time. FIX: always send a browser User-Agent header. Reproduced 403 from both the sandbox AND the Mac, then 200 immediately on adding UA. Do NOT conclude the Publer key is dead on a 403 — check the User-Agent first.
- COMPLIANCE: Va. Code Sec. 40.1-28.7:12 (pay transparency) took effect 2026-07-01 and applies to ALL private employers with no size threshold. Every posting for a job, promotion or transfer -- public or internal -- must carry a good-faith wage range. Salary-history questions are also banned. The 2026-07-23 recruiting stack predates compliance and lacked ranges everywhere.
- Good-faith range adopted: $16.50-$21.50/hour (actual spread paid to Sales & Loan Associates/Representatives across the 5 stores). Use this range on all future hiring content until pay bands change.
- FIXED: careers page (WordPress page 901) -- added range to body copy, added a Pay line, added `baseSalary` to all 5 JobPosting JSON-LD blocks (also helps Google Jobs), and changed "18 or older" to "21 or older" to match the store postings. Live and verified in the update response.
- PATCHED IN PUBLER: all 11 live hiring posts (6 FB pages + 5 GBP) via `PATCH /api/v1/posts/{id}` with `{"text": ...}`. Publer's record now carries the wage range on all 11.
- VERIFIED AGAINST OUTPUT (Rule 12): Publer's `PATCH /posts/{id}` on a `state: published` post DOES propagate the edited text to the live platform post — confirmed visually on three surfaces: FB Culpeper (195986710), FB Roanoke (195986739, the second-pass wording variant), and GBP Culpeper (195986731). Original post date, likes and shares are preserved; the edit is in place, not a repost. This is the supported route for correcting live copy — no delete/repost needed.
- INCIDENT (self-inflicted, resolved): during capability probing a PATCH was sent to the live Culpeper post (195986710) with the literal text "test". Because PATCH propagates (confirmed above), that text was live on the Culpeper FB page for roughly 60-90 seconds before the corrected copy was restored from cache. Final state verified correct. LESSON: never probe a write endpoint against live production content with junk data — probe with the real intended value, or against a draft/test post.
- HANDBOOK/P&P: Employee Handbook v2026.2 and P&P Manual v2026.2 finalized (see Projects/Human Resources/). Struck unlawful wage-forfeiture language (Sec. 40.1-29), added Pay Transparency policy, resolved FMLA coverage (under 50 employees = not covered), resolved reloan worksheet + refund thresholds per Preston 2026-07-14.
- CONFIRMED: 401(k) is active, so RetirePath Virginia does NOT apply. No Sept 30 registration needed.
- OPEN: Brevo campaign #51 (hiring email, sent 7/23) also lacked a range -- already delivered, cannot be recalled; any resend needs the range. Employment application + interview scripts still need salary-history questions removed.

## 2026-08-03 (manual entries)
- ROOT CAUSE FOUND for the recurring "no Mac bridge / cloud run / no Sheets write" false reports (vp-ai-search-autofix, weekly since ~Jun 29). Three SKILL.md files still carried the retired BRIDGE RETRY POLICY block, which instructed the run to probe for `mcp__remote-devices__*` and `mcp__claude-code-remote__send_later`. Those tools do not exist. The block directly contradicted the LOCAL ACCESS GATE added 2026-08-02, and the older block won: the run probed the phantom bridge, failed, and declared itself access-less.
- FIXED: stale block replaced with an EXECUTION ROUTE block in vp-ai-search-autofix and vp-ai-visibility-autofix; phantom tool name corrected in daily-loan-inventory-text. Backups in Scheduled/_backups/bridgeblock-20260803/. Zero stale refs remain across all task folders.
- CORRECTED (Rule 12): the 8/3 run's claim of "no Google Sheets write access" was false. sheets_helper.SheetsClient() re-verified live and 4 audit rows appended to the AI Search Autofix Log.
- RE-VERIFIED: bingplaces.com still has NO signed-in Chrome session on the Mac (unchanged since 2026-07-22). This is the sole blocker on Roanoke Suite C, Harrisonburg address, and the Lexington About blurb. Needs Joshua once, ~2 minutes.
- RECLASSIFIED: the 3 "needs-you" items are not 3 problems. They are 1 login (Bing Places) + 1 genuine claim/merge dispute (MapQuest owner-verified "Dixie Pawn Inc.").
- BING PLACES SIGNED IN (Joshua, 8/3) — full console audit run same session. MAJOR CORRECTION: all 5 Valley Pawn Bing listings are Published with CORRECT addresses, including Harrisonburg "1790 E Market St STE 22" and Roanoke "2362 Peters Creek Road Suite C". Our Bing listing data was never wrong. Five weeks of "Bing NAP drift" reports were comparing the PUBLIC bing.com/maps surface (rendered from TomTom/OpenStreetMap geodata) against canonical NAP, and attributing the mismatch to our listing.
- FIXED (Bing Places, verified): Lexington description removed a phantom 6th location "Salem" and was 610 chars vs the 500 limit. Harrisonburg description had typo "We by Gold1" and was 566 chars. Both replaced with one canonical 497-char description naming the correct 5 stores. Both re-read after save.
- OPEN, LOW PRIORITY: Roanoke public map drops "Suite C"; Harrisonburg public map shows "1790 Toni St". Not fixable via the listing — correct lever is a Bing Maps data-problem report or an OpenStreetMap address-point fix. Volumes are small (Roanoke 151 views/30d, Lexington 39). Recommend accepting.
- NOTED: no "Dixie Pawn" appears anywhere on Bing — that exposure is MapQuest (owner-verified duplicate) and Apple Business Connect only.
- NOTED: Bing listings SYNC FROM GOOGLE. Google Business Profile is the true source of truth, and the Google account signed into Mac Chrome manages 0 businesses — the GBP account is elsewhere. Bing-side description edits may be overwritten on the next Google sync until GBP is corrected too.
- RETRACTION (same session, 8/3): I claimed Apple Business Connect was unclaimed and that Apple Maps showed "Dixie Pawn only, no Valley Pawn". BOTH FALSE. Apple Business Connect is claimed under Full Circle Finance inc. and all FIVE Valley Pawn locations are listed and Verified. No Dixie Pawn present. I repeated the 2026-07-22 STATUS file instead of opening the console — the exact Rule 12 failure I had just diagnosed in the scheduled task. The 2026-07-22 STATUS-what-went-live.md Apple/MapQuest claims should be treated as UNVERIFIED until re-checked live.
- NEW AND ACTIONABLE (Apple Business Connect, not yet touched): Harrisonburg shows "1790 E Market St" with no Ste 22; Roanoke shows "2362 Peters Creek Rd NW" with no Suite C; Waynesboro shows "1321 US-250" instead of 1321 W Broad St. These are editable in a console we own and Apple Maps feeds Siri and all iOS map queries. vp-ai-search-health-check has NEVER checked Apple — that is the real coverage gap, not Bing.
- NOTED: Google Business Profile lives on a different Google account than the one signed into Mac Chrome (Joshua confirmed). Prior session's "GBP account is unknown" framing was noise.

## 2026-08-02

- Enabled scheduled tasks: 80 -> 81
- Registered scheduled tasks: 120 -> 121
- Task folders on disk: 140 -> 141
- ENABLED: business-os-daily-refresh

## 2026-08-02 (manual entries)

- VP Ops Engine STOOD DOWN. All 12 launchd agents unloaded and plists renamed .disabled; backup copies in Projects/VP Ops Engine/_disabled-plists-20260802. Joshua tabled the project. Reversible via launchctl load.
- LOCAL ACCESS GATE added to 73 scheduled task files. Tasks were quitting early and falsely reporting no access to the Mac. Backups in Scheduled/_backups/localgate-*.
- 17 completed one-shot tasks deregistered, 18 folders archived to Scheduled/_archive/completed-oneshots-20260802.
- Automation audit produced: Projects/Valley Pawn OS/AUTOMATION_AUDIT_2026-08-02.md.
- Live-state auto-refresh built (bin/refresh_live_state.py) - BUSINESS_OS.md LIVE STATE block + this changelog now regenerate daily.
- DISCOVERED: six previously undocumented native launchd agents running outside Cowork - commandcenter, dashboarddatacollector, ebay-daily-listings, ebay-efficiency-weekly, ebay-markdown-monthly, ebay-weekly-rankings. dashboard-data-collector was migrated from Cowork to native, which is why it shows unregistered.

## 2026-07-27

- VP Ops Engine Wave 2 designed (BUILD_SPEC_WAVE2.md): Job H weekly FPD, Job I monthly analytics, Job J monthly gold trend (blocked on missing Bravo scrap handler).
- Preston and Walker flagged the Layaway Yield post as unclear - needs week-over-week comparison, not a point-in-time number. Unresolved.

## 2026-07-26

- VP Ops Engine built and cut over to production in a single day. Native Mac engine, launchd + stdlib Python, zero Claude dependency. Jobs A-D took over store rankings, aged inventory, employee rankings, loan and layaway reviews, posting to the five production channels.
- Phase 0 triage classified all 160 task folders (TRIAGE.md). daily-funds-verification and monday-bravo-combined-run marked DO-NOT-TOUCH.
- NOTE: the cutover assumed the Claude-side Monday tasks were not scheduled. That was wrong - monday-bravo-combined-run stayed enabled and fired 7/27, causing duplicate posts.

## 2026-07-23

- Recruiting stack live: careers page with JobPosting schema, hiring pipeline sheet, FB and GBP hiring posts via Publer, Brevo hiring campaign, $250 referral program.
- facebook-post skill tokens confirmed DEAD (Meta app disabled 7/4). All social publishing must route through vp-social-publisher / Publer.

## 2026-07-22

- Failure Alert Policy v2 set: on failure send Joshua ONE plain-language Slack DM, technical detail to the log only, never notify any team channel or employee.

## 2026-06-19

- Social media stack expanded: Publer becomes the publishing route for all channels.


## 2026-08-02

- Live-state tracking initialised.