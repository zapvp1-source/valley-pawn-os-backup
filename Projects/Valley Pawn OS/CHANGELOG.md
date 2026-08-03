# Valley Pawn - Enterprise Changelog

Newest first. Material changes to the business operating system. Read this BEFORE any build, fix or diagnosis.

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

