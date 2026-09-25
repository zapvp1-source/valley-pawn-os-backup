# Fleet Health — rolling sentinel log

Written by `bin/fleet_health_sentinel.py` (native launchd, no Claude usage). Newest first, last 30 runs kept. DM alerts go to Joshua only when an issue is first detected.

## 2026-09-24 22:30 — ISSUES FOUND

- 'weekly-analytics-summary' (cron 0 1 * * 1) missed its Mon Sep 21 1:00 AM run — last started Mon Sep 14 1:17 AM
- 'bald-rock-monday-briefing' (cron 15 4 * * 1) missed its Mon Sep 21 4:15 AM run — last started Mon Sep 14 4:50 AM
- 'email-analytics-weekly' (cron 30 3 * * 5) missed its Fri Sep 18 3:30 AM run — last started Fri Sep 11 3:35 AM
- 'vp-ai-search-health-check' (cron 10 6 * * 1) missed its Mon Sep 21 6:10 AM run — last started Mon Sep 14 6:42 AM
- 'vp-ai-visibility-metrics' (cron 30 6 * * 5) missed its Fri Sep 18 6:30 AM run — last started Fri Sep 11 6:31 AM
- 'weekly-social-media-recap' (cron 40 9 * * 1) missed its Mon Sep 21 9:40 AM run — last started Wed Sep 16 3:44 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 21 7:40 AM run — last started Wed Sep 16 4:36 PM
- 'vp-staff-video-prompt' (cron 10 9 * * 2) missed its Tue Sep 22 9:10 AM run — last started Wed Sep 16 4:39 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 21 11:45 AM run — last started Wed Sep 16 4:43 PM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 21 5:15 AM run — last started Wed Sep 16 4:44 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 21 7:26 AM run — last started Wed Sep 16 5:16 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 20 9:00 AM run — last started Wed Sep 16 5:26 PM
- launchd agent com.valleypawn.commandcenter last exited with status -9

## 2026-09-24 13:30 — ISSUES FOUND

- 'weekly-analytics-summary' (cron 0 1 * * 1) missed its Mon Sep 21 1:00 AM run — last started Mon Sep 14 1:17 AM
- 'bald-rock-monday-briefing' (cron 15 4 * * 1) missed its Mon Sep 21 4:15 AM run — last started Mon Sep 14 4:50 AM
- 'email-analytics-weekly' (cron 30 3 * * 5) missed its Fri Sep 18 3:30 AM run — last started Fri Sep 11 3:35 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 21 7:40 AM run — last started Wed Sep 16 4:36 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 21 11:45 AM run — last started Wed Sep 16 4:43 PM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 21 5:15 AM run — last started Wed Sep 16 4:44 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 21 7:26 AM run — last started Wed Sep 16 5:16 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 20 9:00 AM run — last started Wed Sep 16 5:26 PM
- launchd agent com.valleypawn.commandcenter last exited with status -9


## 2026-09-23 22:30 — ISSUES FOUND

- 'weekly-analytics-summary' (cron 0 1 * * 1) missed its Mon Sep 21 1:00 AM run — last started Mon Sep 14 1:17 AM
- 'bald-rock-monday-briefing' (cron 15 4 * * 1) missed its Mon Sep 21 4:15 AM run — last started Mon Sep 14 4:50 AM
- 'email-analytics-weekly' (cron 30 3 * * 5) missed its Fri Sep 18 3:30 AM run — last started Fri Sep 11 3:35 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 21 7:40 AM run — last started Wed Sep 16 4:36 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 21 11:45 AM run — last started Wed Sep 16 4:43 PM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 21 5:15 AM run — last started Wed Sep 16 4:44 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 21 7:26 AM run — last started Wed Sep 16 5:16 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 20 9:00 AM run — last started Wed Sep 16 5:26 PM
- launchd agent com.valleypawn.commandcenter last exited with status -9



## 2026-09-23 13:30 — ISSUES FOUND

- 'weekly-analytics-summary' (cron 0 1 * * 1) missed its Mon Sep 21 1:00 AM run — last started Mon Sep 14 1:17 AM
- 'bald-rock-monday-briefing' (cron 15 4 * * 1) missed its Mon Sep 21 4:15 AM run — last started Mon Sep 14 4:50 AM
- 'email-analytics-weekly' (cron 30 3 * * 5) missed its Fri Sep 18 3:30 AM run — last started Fri Sep 11 3:35 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 21 7:40 AM run — last started Wed Sep 16 4:36 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 21 11:45 AM run — last started Wed Sep 16 4:43 PM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 21 5:15 AM run — last started Wed Sep 16 4:44 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 21 7:26 AM run — last started Wed Sep 16 5:16 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 20 9:00 AM run — last started Wed Sep 16 5:26 PM
- launchd agent com.valleypawn.commandcenter last exited with status -9




## 2026-09-22 22:30 — ISSUES FOUND

- 'weekly-analytics-summary' (cron 0 1 * * 1) missed its Mon Sep 21 1:00 AM run — last started Mon Sep 14 1:17 AM
- 'bald-rock-monday-briefing' (cron 15 4 * * 1) missed its Mon Sep 21 4:15 AM run — last started Mon Sep 14 4:50 AM
- 'email-analytics-weekly' (cron 30 3 * * 5) missed its Fri Sep 18 3:30 AM run — last started Fri Sep 11 3:35 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 21 7:40 AM run — last started Wed Sep 16 4:36 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 21 11:45 AM run — last started Wed Sep 16 4:43 PM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 21 5:15 AM run — last started Wed Sep 16 4:44 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 21 7:26 AM run — last started Wed Sep 16 5:16 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 20 9:00 AM run — last started Wed Sep 16 5:26 PM
- launchd agent com.valleypawn.chrome-tab-hygiene last exited with status 1
- launchd agent com.valleypawn.commandcenter last exited with status -9





## 2026-09-22 13:30 — ISSUES FOUND

- 'weekly-analytics-summary' (cron 0 1 * * 1) missed its Mon Sep 21 1:00 AM run — last started Mon Sep 14 1:17 AM
- 'bald-rock-monday-briefing' (cron 15 4 * * 1) missed its Mon Sep 21 4:15 AM run — last started Mon Sep 14 4:50 AM
- 'email-analytics-weekly' (cron 30 3 * * 5) missed its Fri Sep 18 3:30 AM run — last started Fri Sep 11 3:35 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 21 7:40 AM run — last started Wed Sep 16 4:36 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 21 11:45 AM run — last started Wed Sep 16 4:43 PM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 21 5:15 AM run — last started Wed Sep 16 4:44 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 21 7:26 AM run — last started Wed Sep 16 5:16 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 20 9:00 AM run — last started Wed Sep 16 5:26 PM
- launchd agent com.valleypawn.chrome-tab-hygiene last exited with status 1
- launchd agent com.valleypawn.commandcenter last exited with status -9






## 2026-09-21 22:30 — ISSUES FOUND

- 'weekly-analytics-summary' (cron 0 1 * * 1) missed its Mon Sep 21 1:00 AM run — last started Mon Sep 14 1:17 AM
- 'bald-rock-monday-briefing' (cron 15 4 * * 1) missed its Mon Sep 21 4:15 AM run — last started Mon Sep 14 4:50 AM
- 'email-analytics-weekly' (cron 30 3 * * 5) missed its Fri Sep 18 3:30 AM run — last started Fri Sep 11 3:35 AM
- 'bald-rock-guest-reviews' (cron 0 11 * * *) missed its Mon Sep 21 11:00 AM run — last started Wed Sep 16 4:11 PM
- 'oura-daily-import' (cron 45 8 * * *) missed its Mon Sep 21 8:45 AM run — last started Wed Sep 16 8:51 AM
- 'northwest-registered-agent-daily-check' (cron 40 8 * * *) missed its Mon Sep 21 8:40 AM run — last started Wed Sep 16 8:42 AM
- 'backup-health-watchdog' (cron 0 7 * * *) missed its Mon Sep 21 7:00 AM run — last started Wed Sep 16 8:42 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 21 7:40 AM run — last started Wed Sep 16 4:36 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 21 11:45 AM run — last started Wed Sep 16 4:43 PM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 21 5:15 AM run — last started Wed Sep 16 4:44 PM
- 'morning-brief' (cron 0 8 * * 1-5) missed its Mon Sep 21 8:00 AM run — last started Wed Sep 16 4:57 PM
- 'insurance-inbox-watch' (cron 44 6 * * *) missed its Mon Sep 21 6:44 AM run — last started Wed Sep 16 5:15 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 21 7:26 AM run — last started Wed Sep 16 5:16 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 20 9:00 AM run — last started Wed Sep 16 5:26 PM
- 'connector-health-daily' (cron 40 5 * * *) missed its Mon Sep 21 5:40 AM run — last started Sat Sep 12 5:41 AM
- launchd agent com.valleypawn.chrome-tab-hygiene last exited with status 1
- launchd agent com.valleypawn.commandcenter last exited with status -9







## 2026-09-21 13:30 — ISSUES FOUND

- launchd agent com.valleypawn.chrome-tab-hygiene last exited with status 1
- launchd agent com.valleypawn.commandcenter last exited with status -9








## 2026-09-20 22:30 — ISSUES FOUND

- launchd agent com.valleypawn.chrome-tab-hygiene last exited with status 1
- launchd agent com.valleypawn.commandcenter last exited with status -9









## 2026-09-20 13:30 — ISSUES FOUND

- launchd agent com.valleypawn.chrome-tab-hygiene last exited with status 1
- launchd agent com.valleypawn.commandcenter last exited with status -9










## 2026-09-19 22:30 — ISSUES FOUND

- launchd agent com.valleypawn.chrome-tab-hygiene last exited with status 1
- launchd agent com.valleypawn.commandcenter last exited with status -9











## 2026-09-19 13:30 — ISSUES FOUND

- launchd agent com.valleypawn.chrome-tab-hygiene last exited with status 1
- launchd agent com.valleypawn.commandcenter last exited with status -9












## 2026-09-18 22:30 — ISSUES FOUND

- launchd agent com.valleypawn.chrome-tab-hygiene last exited with status 1
- launchd agent com.valleypawn.field-scorecard last exited with status 1
- launchd agent com.valleypawn.github-backup last exited with status 2
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127
- launchd agent com.valleypawn.commandcenter last exited with status -9
- launchd agent com.valleypawn.bravo-relaunch last exited with status 1













## 2026-09-18 13:30 — ISSUES FOUND

- launchd agent com.valleypawn.chrome-tab-hygiene last exited with status 1
- launchd agent com.valleypawn.github-backup last exited with status 2
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127
- launchd agent com.valleypawn.commandcenter last exited with status -9
- launchd agent com.valleypawn.bravo-relaunch last exited with status 1














## 2026-09-17 22:30 — ISSUES FOUND

- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127
- launchd agent com.valleypawn.commandcenter last exited with status -9















## 2026-09-17 13:30 — ISSUES FOUND

- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127
- launchd agent com.valleypawn.commandcenter last exited with status -9
















## 2026-09-16 22:30 — ISSUES FOUND

- usage-cap skips climbing: +2480 since Wed 1:30 PM (~276/hr) — tasks are being throttled right now
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127
- launchd agent com.valleypawn.commandcenter last exited with status -9

















## 2026-09-16 13:30 — ISSUES FOUND

- 'chekkit-new-review-alert' (cron 10 9-21 * * *) missed its Wed Sep 16 11:10 AM run — last started Wed Sep 16 10:30 AM
- 'daily-cloudcover-check' (cron 25 10 * * 1-6) missed its Wed Sep 16 10:25 AM run — last started Tue Sep 15 12:14 PM
- 'monthly-we-buy-gold-silver-email' (cron 0 9 1 * *) missed its Tue Sep 1 9:00 AM run — last started Tue Sep 1 2:18 AM
- 'daily-dress-code-check' (cron 30 10 * * 1-6) missed its Wed Sep 16 10:30 AM run — last started Tue Sep 15 12:53 PM
- 'bald-rock-guest-reviews' (cron 0 11 * * *) missed its Wed Sep 16 11:00 AM run — last started Tue Sep 15 5:46 PM
- 'zoom-voicemail-alert' (cron 10,30,50 9-19 * * 1-6) missed its Wed Sep 16 11:50 AM run — last started Wed Sep 16 5:13 AM
- 'nics-weekly-mtd-ranking' (cron 30 9 * * 1) missed its Mon Sep 14 9:30 AM run — last started Mon Sep 7 9:39 AM
- 'bravo-prestaging-7am' (cron 30 6 * * *) missed its Wed Sep 16 6:30 AM run — last started Mon Sep 14 6:42 AM
- 'discount-review' (cron 25 8 * * *) missed its Wed Sep 16 8:25 AM run — last started Sun Sep 13 9:47 AM
- 'zoom-voicemail-eod-review' (cron 45 17 * * *) missed its Tue Sep 15 5:45 PM run — last started Sun Sep 13 11:19 PM
- 'sold-review' (cron 45 7 * * *) missed its Wed Sep 16 7:45 AM run — last started Sun Sep 13 9:47 AM
- 'weekly-markdown-verification-review' (cron 35 9 * * 1) missed its Mon Sep 14 9:35 AM run — last started Mon Sep 7 9:44 AM
- 'indeed-applicant-outreach' (cron 0 9-19 * * *) missed its Wed Sep 16 11:00 AM run — last started Mon Sep 14 12:06 AM
- 'bravo-morning-pull' (cron 50 6 * * *) missed its Wed Sep 16 6:50 AM run — last started Mon Sep 14 6:55 AM
- 'jewelry-pull-watchdog' (cron 15 9 * * 2-7,0) missed its Wed Sep 16 9:15 AM run — last started Sun Sep 13 10:00 AM
- 'precious-metals-settlement-handler' (cron 0 9 * * *) missed its Wed Sep 16 9:00 AM run — last started Sun Sep 13 10:29 AM
- 'bravo-preflight-relaunch' (cron 0 4 * * *) missed its Wed Sep 16 4:00 AM run — last started Mon Sep 14 4:50 AM
- 'hiring-inbox-watch' (cron 20 10,12,14,16,18 * * 1-6) missed its Wed Sep 16 10:20 AM run — last started Sat Sep 12 6:39 PM
- 'vp-ai-search-autofix' (cron 30 8 * * 1) missed its Mon Sep 14 8:30 AM run — last started Mon Sep 7 8:36 AM
- 'jewelry-onhand-catchup' (cron 45 7 * * 2-7,0) missed its Wed Sep 16 7:45 AM run — last started Sun Sep 13 10:34 AM
- 'google-reviews-post-watchdog' (cron 45 10 * * 1) missed its Mon Sep 14 10:45 AM run — last started Mon Sep 7 10:57 AM
- 'fleet-guardian' (cron 45 12,21 * * *) missed its Tue Sep 15 9:45 PM run — last started Mon Sep 14 12:06 AM
- 'unified-search-index-refresh' (cron 30 3 * * *) missed its Wed Sep 16 3:30 AM run — last started Mon Sep 14 6:42 AM
- 'shop-in-store-sync' (cron 10 10,16 * * *) missed its Wed Sep 16 10:10 AM run — last started Sun Sep 13 4:42 PM
- 'gusto-keep-alive' (cron 40 */2 * * *) missed its Wed Sep 16 10:40 AM run — last started Mon Sep 14 6:55 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 14 7:40 AM run — last started Mon Sep 7 7:42 AM
- 'ask-handbook-responder' (cron 5,35 10-18 * * 1-6) missed its Wed Sep 16 11:35 AM run — last started Sat Sep 12 7:33 PM
- 'vp-deal-reels-weekly' (cron 30 14 * * 1) missed its Mon Sep 14 2:30 PM run — last started Mon Sep 7 2:38 PM
- 'vp-community-weekly' (cron 10 15 * * 1) missed its Mon Sep 14 3:10 PM run — last started Mon Sep 7 3:17 PM
- 'vp-engagement-weekly' (cron 45 15 * * 1) missed its Mon Sep 14 3:45 PM run — last started Mon Sep 7 3:53 PM
- 'vp-staff-video-prompt' (cron 10 9 * * 2) missed its Tue Sep 15 9:10 AM run — last started Tue Sep 8 9:20 AM
- 'vp-staff-video-chase' (cron 15 11 * * 3) missed its Wed Sep 16 11:15 AM run — last started Wed Sep 9 11:23 AM
- 'ffl-transfer-email-responder' (cron 50 8,16 * * *) missed its Wed Sep 16 8:50 AM run — last started Mon Sep 14 6:55 AM
- 'brevo-weekly-draft-guard' (cron 50 11 * * 1) missed its Mon Sep 14 11:50 AM run — last started Mon Sep 7 12:28 PM
- 'daily-unopened-email-eval' (cron 0 18 * * *) missed its Tue Sep 15 6:00 PM run — last started Sat Sep 12 6:02 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 14 11:45 AM run — last started Mon Sep 7 11:46 AM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 14 5:15 AM run — last started Mon Sep 7 5:23 AM
- 'bravo-brevo-attribute-sync' (cron 30 17 * * 2) missed its Tue Sep 15 5:30 PM run — last started Tue Sep 8 5:40 PM
- 'brevo-welcome-new-contacts' (cron 0 10 * * *) missed its Wed Sep 16 10:00 AM run — last started Sun Sep 13 11:33 AM
- 'ebay-markdown-terminal-weekly' (cron 15 12 * * 1) missed its Mon Sep 14 12:15 PM run — last started Mon Sep 7 12:30 PM
- 'marketing-ceo-briefing-weekly' (cron 30 11 * * 1) missed its Mon Sep 14 11:30 AM run — last started Mon Sep 7 11:33 AM
- 'preston-interactive-assistant' (cron */5 7-21 * * *) missed its Wed Sep 16 11:55 AM run — last started Sun Sep 13 4:46 PM
- 'morning-brief' (cron 0 8 * * 1-5) missed its Wed Sep 16 8:00 AM run — last started Fri Sep 11 8:59 AM
- 'ceo-mail-brief' (cron 0 7,16 * * *) missed its Wed Sep 16 7:00 AM run — last started Sun Sep 13 4:46 PM
- 'mail-brief-reply-executor' (cron 7,37 6-22 * * *) missed its Wed Sep 16 11:37 AM run — last started Sun Sep 13 4:50 PM
- 'scheduled-task-model-audit-weekly' (cron 0 5 * * 1) missed its Mon Sep 14 5:00 AM run — last started Mon Sep 7 5:04 AM
- 'document-photos-index-refresh' (cron 0 5 * * *) missed its Wed Sep 16 5:00 AM run — last started Sun Sep 13 5:58 AM
- 'unified-search-verify' (cron 50 4 * * *) missed its Wed Sep 16 4:50 AM run — last started Sun Sep 13 6:16 AM
- 'monday-bravo-cell-gapfill' (cron 30 20 * * 0) missed its Sun Sep 13 8:30 PM run — last started Sun Sep 6 8:40 PM
- 'insurance-inbox-watch' (cron 44 6 * * *) missed its Wed Sep 16 6:44 AM run — last started Sun Sep 13 1:46 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 14 7:26 AM run — last started Mon Sep 7 7:33 AM
- 'insurance-claims-follow-up' (cron 40 9 * * 3) missed its Wed Sep 16 9:40 AM run — last started Wed Sep 9 9:44 AM
- 'health-episode-capture' (cron 15 9 * * *) missed its Wed Sep 16 9:15 AM run — last started Sat Sep 12 9:34 AM
- 'bonus-pace-monday' (cron 35 9 * * 1) missed its Mon Sep 14 9:35 AM run — last started Mon Sep 7 11:24 AM
- 'health-records-intake' (cron 0 21 * * *) missed its Tue Sep 15 9:00 PM run — last started Sat Sep 12 9:30 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 13 9:00 AM run — last started Sun Sep 6 9:37 AM
- 'bonus-paid-verify' (cron 0 10 * * 1) missed its Mon Sep 14 10:00 AM run — last started Mon Sep 7 11:24 AM
- 'brevo-engaged-v2-refresh' (cron 20 6 * * 3) missed its Wed Sep 16 6:20 AM run — last started Wed Sep 9 6:22 AM
- 'ceo-weekly-scorecard' (cron 15 12 * * 1) missed its Mon Sep 14 12:15 PM run — last started Mon Sep 7 12:39 PM
- 'weekly-training-pipeline' (cron 0 7 * * 1) missed its Mon Sep 14 7:00 AM run — last started Tue Sep 8 12:05 PM
- 'connector-health-daily' (cron 40 5 * * *) missed its Wed Sep 16 5:40 AM run — last started Sat Sep 12 5:41 AM
- launchd agent com.valleypawn.claude-keepalive last exited with status 126
- launchd agent com.valleypawn.compliance-brief last exited with status 1
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127


















## 2026-09-15 22:30 — ISSUES FOUND

- 'monthly-we-buy-gold-silver-email' (cron 0 9 1 * *) missed its Tue Sep 1 9:00 AM run — last started Tue Sep 1 2:18 AM
- 'ebay-weekly-quality-fix' (cron 0 11 * * 1) missed its Mon Sep 14 11:00 AM run — last started Mon Sep 7 11:03 AM
- 'vp-content-batch-preflight' (cron 0 11 * * 1) missed its Mon Sep 14 11:00 AM run — last started Mon Sep 7 11:13 AM
- 'vp-content-batch-postflight' (cron 40 16 * * 1) missed its Mon Sep 14 4:40 PM run — last started Mon Sep 7 4:44 PM
- 'vp-casual-video-daily' (cron 35 19 * * *) missed its Tue Sep 15 7:35 PM run — last started Sun Sep 13 11:19 PM
- 'vp-os-github-nightly-backup' (cron 15 0 * * *) missed its Tue Sep 15 12:15 AM run — last started Mon Sep 14 12:55 AM
- 'weekly-loan-review-canvas-refresh' (cron 20 9 * * 1) missed its Mon Sep 14 9:20 AM run — last started Mon Sep 7 9:23 AM
- 'weekly-layaway-review-canvas-refresh' (cron 22 9 * * 1) missed its Mon Sep 14 9:22 AM run — last started Mon Sep 7 9:25 AM
- 'weekly-employee-perf-canvas-refresh' (cron 24 9 * * 1) missed its Mon Sep 14 9:24 AM run — last started Mon Sep 7 9:27 AM
- 'weekly-aged-inventory-canvas-refresh' (cron 26 9 * * 1) missed its Mon Sep 14 9:26 AM run — last started Mon Sep 7 9:28 AM
- 'weekly-store-perf-canvas-refresh' (cron 28 9 * * 1) missed its Mon Sep 14 9:28 AM run — last started Mon Sep 7 9:30 AM
- 'vp-website-shop-nightly' (cron 0 7,15 * * *) missed its Tue Sep 15 3:00 PM run — last started Mon Sep 14 7:31 AM
- 'layaway-yield-weekly' (cron 15 11 * * 1) missed its Mon Sep 14 11:15 AM run — last started Mon Sep 7 11:18 AM
- 'vp-deal-of-week-monday-reminder' (cron 0 11 * * 1) missed its Mon Sep 14 11:00 AM run — last started Mon Sep 7 11:18 AM
- 'business-os-daily-refresh' (cron 0 5 * * *) missed its Tue Sep 15 5:00 AM run — last started Mon Sep 14 5:01 AM
- 'northwest-registered-agent-daily-check' (cron 40 8 * * *) missed its Tue Sep 15 8:40 AM run — last started Sun Sep 13 9:34 AM
- 'weekly-social-media-recap' (cron 40 9 * * 1) missed its Mon Sep 14 9:40 AM run — last started Mon Sep 7 9:42 AM
- 'vp-content-batch-quota-watchdog' (cron 0 10 * * 2) missed its Tue Sep 15 10:00 AM run — last started Tue Sep 8 10:08 AM
- 'vp-gusto-signature-chase' (cron 5 9 * * 1) missed its Mon Sep 14 9:05 AM run — last started Mon Sep 7 9:14 AM
- 'backup-health-watchdog' (cron 0 7 * * *) missed its Tue Sep 15 7:00 AM run — last started Sun Sep 13 9:34 AM
- 'vp-follower-growth-monthly-check' (cron 50 9 * * 1) missed its Mon Sep 14 9:50 AM run — last started Mon Sep 7 9:59 AM
- 'zoom-voicemail-alert' (cron 10,30,50 9-19 * * 1-6) missed its Tue Sep 15 7:50 PM run — last started Sat Sep 12 7:56 PM
- 'chekkit-unanswered-eod-followup' (cron 0 19 * * 1-6) missed its Tue Sep 15 7:00 PM run — last started Sat Sep 12 7:29 PM
- 'gdrive-cache-refresh' (cron 0 3 * * *) missed its Tue Sep 15 3:00 AM run — last started Mon Sep 14 4:50 AM
- 'jewelry-onhand-nightly-pull' (cron 30 20 * * 1-6) missed its Tue Sep 15 8:30 PM run — last started Sat Sep 12 8:44 PM
- 'nics-weekly-mtd-ranking' (cron 30 9 * * 1) missed its Mon Sep 14 9:30 AM run — last started Mon Sep 7 9:39 AM
- 'bravo-prestaging-7am' (cron 30 6 * * *) missed its Tue Sep 15 6:30 AM run — last started Mon Sep 14 6:42 AM
- 'discount-review' (cron 25 8 * * *) missed its Tue Sep 15 8:25 AM run — last started Sun Sep 13 9:47 AM
- 'zoom-voicemail-eod-review' (cron 45 17 * * *) missed its Tue Sep 15 5:45 PM run — last started Sun Sep 13 11:19 PM
- 'sold-review' (cron 45 7 * * *) missed its Tue Sep 15 7:45 AM run — last started Sun Sep 13 9:47 AM
- 'weekly-markdown-verification-review' (cron 35 9 * * 1) missed its Mon Sep 14 9:35 AM run — last started Mon Sep 7 9:44 AM
- 'indeed-applicant-outreach' (cron 0 9-19 * * *) missed its Tue Sep 15 7:00 PM run — last started Mon Sep 14 12:06 AM
- 'bravo-morning-pull' (cron 50 6 * * *) missed its Tue Sep 15 6:50 AM run — last started Mon Sep 14 6:55 AM
- 'jewelry-pull-watchdog' (cron 15 9 * * 2-7,0) missed its Tue Sep 15 9:15 AM run — last started Sun Sep 13 10:00 AM
- 'precious-metals-settlement-handler' (cron 0 9 * * *) missed its Tue Sep 15 9:00 AM run — last started Sun Sep 13 10:29 AM
- 'bravo-preflight-relaunch' (cron 0 4 * * *) missed its Tue Sep 15 4:00 AM run — last started Mon Sep 14 4:50 AM
- 'hiring-inbox-watch' (cron 20 10,12,14,16,18 * * 1-6) missed its Tue Sep 15 6:20 PM run — last started Sat Sep 12 6:39 PM
- 'vp-ai-search-autofix' (cron 30 8 * * 1) missed its Mon Sep 14 8:30 AM run — last started Mon Sep 7 8:36 AM
- 'jewelry-onhand-catchup' (cron 45 7 * * 2-7,0) missed its Tue Sep 15 7:45 AM run — last started Sun Sep 13 10:34 AM
- 'google-reviews-post-watchdog' (cron 45 10 * * 1) missed its Mon Sep 14 10:45 AM run — last started Mon Sep 7 10:57 AM
- 'fleet-guardian' (cron 45 12,21 * * *) missed its Tue Sep 15 12:45 PM run — last started Mon Sep 14 12:06 AM
- 'unified-search-index-refresh' (cron 30 3 * * *) missed its Tue Sep 15 3:30 AM run — last started Mon Sep 14 6:42 AM
- 'shop-in-store-sync' (cron 10 10,16 * * *) missed its Tue Sep 15 4:10 PM run — last started Sun Sep 13 4:42 PM
- 'gusto-keep-alive' (cron 40 */2 * * *) missed its Tue Sep 15 8:40 PM run — last started Mon Sep 14 6:55 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 14 7:40 AM run — last started Mon Sep 7 7:42 AM
- 'ask-handbook-responder' (cron 5,35 10-18 * * 1-6) missed its Tue Sep 15 6:35 PM run — last started Sat Sep 12 7:33 PM
- 'vp-deal-reels-weekly' (cron 30 14 * * 1) missed its Mon Sep 14 2:30 PM run — last started Mon Sep 7 2:38 PM
- 'vp-community-weekly' (cron 10 15 * * 1) missed its Mon Sep 14 3:10 PM run — last started Mon Sep 7 3:17 PM
- 'vp-engagement-weekly' (cron 45 15 * * 1) missed its Mon Sep 14 3:45 PM run — last started Mon Sep 7 3:53 PM
- 'vp-staff-video-prompt' (cron 10 9 * * 2) missed its Tue Sep 15 9:10 AM run — last started Tue Sep 8 9:20 AM
- 'ffl-transfer-email-responder' (cron 50 8,16 * * *) missed its Tue Sep 15 4:50 PM run — last started Mon Sep 14 6:55 AM
- 'brevo-weekly-draft-guard' (cron 50 11 * * 1) missed its Mon Sep 14 11:50 AM run — last started Mon Sep 7 12:28 PM
- 'daily-unopened-email-eval' (cron 0 18 * * *) missed its Tue Sep 15 6:00 PM run — last started Sat Sep 12 6:02 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 14 11:45 AM run — last started Mon Sep 7 11:46 AM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 14 5:15 AM run — last started Mon Sep 7 5:23 AM
- 'bravo-brevo-attribute-sync' (cron 30 17 * * 2) missed its Tue Sep 15 5:30 PM run — last started Tue Sep 8 5:40 PM
- 'brevo-welcome-new-contacts' (cron 0 10 * * *) missed its Tue Sep 15 10:00 AM run — last started Sun Sep 13 11:33 AM
- 'ebay-markdown-terminal-weekly' (cron 15 12 * * 1) missed its Mon Sep 14 12:15 PM run — last started Mon Sep 7 12:30 PM
- 'marketing-ceo-briefing-weekly' (cron 30 11 * * 1) missed its Mon Sep 14 11:30 AM run — last started Mon Sep 7 11:33 AM
- 'preston-interactive-assistant' (cron */5 7-21 * * *) missed its Tue Sep 15 8:55 PM run — last started Sun Sep 13 4:46 PM
- 'morning-brief' (cron 0 8 * * 1-5) missed its Tue Sep 15 8:00 AM run — last started Fri Sep 11 8:59 AM
- 'ceo-mail-brief' (cron 0 7,16 * * *) missed its Tue Sep 15 4:00 PM run — last started Sun Sep 13 4:46 PM
- 'mail-brief-reply-executor' (cron 7,37 6-22 * * *) missed its Tue Sep 15 8:37 PM run — last started Sun Sep 13 4:50 PM
- 'scheduled-task-model-audit-weekly' (cron 0 5 * * 1) missed its Mon Sep 14 5:00 AM run — last started Mon Sep 7 5:04 AM
- 'document-photos-index-refresh' (cron 0 5 * * *) missed its Tue Sep 15 5:00 AM run — last started Sun Sep 13 5:58 AM
- 'unified-search-verify' (cron 50 4 * * *) missed its Tue Sep 15 4:50 AM run — last started Sun Sep 13 6:16 AM
- 'monday-bravo-cell-gapfill' (cron 30 20 * * 0) missed its Sun Sep 13 8:30 PM run — last started Sun Sep 6 8:40 PM
- 'insurance-inbox-watch' (cron 44 6 * * *) missed its Tue Sep 15 6:44 AM run — last started Sun Sep 13 1:46 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 14 7:26 AM run — last started Mon Sep 7 7:33 AM
- 'health-episode-capture' (cron 15 9 * * *) missed its Tue Sep 15 9:15 AM run — last started Sat Sep 12 9:34 AM
- 'bonus-pace-monday' (cron 35 9 * * 1) missed its Mon Sep 14 9:35 AM run — last started Mon Sep 7 11:24 AM
- 'health-records-intake' (cron 0 21 * * *) missed its Mon Sep 14 9:00 PM run — last started Sat Sep 12 9:30 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 13 9:00 AM run — last started Sun Sep 6 9:37 AM
- 'bonus-paid-verify' (cron 0 10 * * 1) missed its Mon Sep 14 10:00 AM run — last started Mon Sep 7 11:24 AM
- 'ceo-weekly-scorecard' (cron 15 12 * * 1) missed its Mon Sep 14 12:15 PM run — last started Mon Sep 7 12:39 PM
- 'weekly-training-pipeline' (cron 0 7 * * 1) missed its Mon Sep 14 7:00 AM run — last started Tue Sep 8 12:05 PM
- 'connector-health-daily' (cron 40 5 * * *) missed its Tue Sep 15 5:40 AM run — last started Sat Sep 12 5:41 AM
- launchd agent com.valleypawn.claude-keepalive last exited with status 126
- launchd agent com.valleypawn.compliance-brief last exited with status 1
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127



















## 2026-09-15 13:30 — ISSUES FOUND

- 'monthly-we-buy-gold-silver-email' (cron 0 9 1 * *) missed its Tue Sep 1 9:00 AM run — last started Tue Sep 1 2:18 AM
- 'vp-dashboard-refresh' (cron 15 8,19 * * *) missed its Tue Sep 15 8:15 AM run — last started Tue Sep 15 2:33 AM
- 'bald-rock-guest-reviews' (cron 0 11 * * *) missed its Tue Sep 15 11:00 AM run — last started Tue Sep 15 3:09 AM
- 'bravo-health-watchdog' (cron 0 5,17 * * *) missed its Tue Sep 15 5:00 AM run — last started Tue Sep 15 3:09 AM
- 'blog-publisher-watchdog' (cron 0 14 * * 1,4) missed its Mon Sep 14 2:00 PM run — last started Thu Sep 10 2:17 PM
- 'oura-daily-import' (cron 45 8 * * *) missed its Tue Sep 15 8:45 AM run — last started Mon Sep 14 10:49 AM
- 'vp-website-deals-weekly' (cron 5 13 * * 1) missed its Mon Sep 14 1:05 PM run — last started Mon Sep 7 1:06 PM
- 'pawn-walk' (cron 15 7 * * *) missed its Tue Sep 15 7:15 AM run — last started Mon Sep 14 7:31 AM
- 'weekly-store-kpis' (cron 30 10 * * 1) missed its Mon Sep 14 10:30 AM run — last started Mon Sep 7 10:33 AM
- 'brevo-preflight-watchdog' (cron 0 7 * * *) missed its Tue Sep 15 7:00 AM run — last started Mon Sep 14 7:31 AM
- 'ebay-weekly-quality-fix' (cron 0 11 * * 1) missed its Mon Sep 14 11:00 AM run — last started Mon Sep 7 11:03 AM
- 'vp-content-batch-preflight' (cron 0 11 * * 1) missed its Mon Sep 14 11:00 AM run — last started Mon Sep 7 11:13 AM
- 'vp-content-batch-postflight' (cron 40 16 * * 1) missed its Mon Sep 14 4:40 PM run — last started Mon Sep 7 4:44 PM
- 'vp-casual-video-daily' (cron 35 19 * * *) missed its Mon Sep 14 7:35 PM run — last started Sun Sep 13 11:19 PM
- 'vp-os-github-nightly-backup' (cron 15 0 * * *) missed its Tue Sep 15 12:15 AM run — last started Mon Sep 14 12:55 AM
- 'weekly-loan-review-canvas-refresh' (cron 20 9 * * 1) missed its Mon Sep 14 9:20 AM run — last started Mon Sep 7 9:23 AM
- 'weekly-layaway-review-canvas-refresh' (cron 22 9 * * 1) missed its Mon Sep 14 9:22 AM run — last started Mon Sep 7 9:25 AM
- 'weekly-employee-perf-canvas-refresh' (cron 24 9 * * 1) missed its Mon Sep 14 9:24 AM run — last started Mon Sep 7 9:27 AM
- 'weekly-aged-inventory-canvas-refresh' (cron 26 9 * * 1) missed its Mon Sep 14 9:26 AM run — last started Mon Sep 7 9:28 AM
- 'weekly-store-perf-canvas-refresh' (cron 28 9 * * 1) missed its Mon Sep 14 9:28 AM run — last started Mon Sep 7 9:30 AM
- 'vp-website-shop-nightly' (cron 0 7,15 * * *) missed its Tue Sep 15 7:00 AM run — last started Mon Sep 14 7:31 AM
- 'layaway-yield-weekly' (cron 15 11 * * 1) missed its Mon Sep 14 11:15 AM run — last started Mon Sep 7 11:18 AM
- 'vp-deal-of-week-monday-reminder' (cron 0 11 * * 1) missed its Mon Sep 14 11:00 AM run — last started Mon Sep 7 11:18 AM
- 'business-os-daily-refresh' (cron 0 5 * * *) missed its Tue Sep 15 5:00 AM run — last started Mon Sep 14 5:01 AM
- 'northwest-registered-agent-daily-check' (cron 40 8 * * *) missed its Tue Sep 15 8:40 AM run — last started Sun Sep 13 9:34 AM
- 'weekly-social-media-recap' (cron 40 9 * * 1) missed its Mon Sep 14 9:40 AM run — last started Mon Sep 7 9:42 AM
- 'vp-content-batch-quota-watchdog' (cron 0 10 * * 2) missed its Tue Sep 15 10:00 AM run — last started Tue Sep 8 10:08 AM
- 'vp-gusto-signature-chase' (cron 5 9 * * 1) missed its Mon Sep 14 9:05 AM run — last started Mon Sep 7 9:14 AM
- 'backup-health-watchdog' (cron 0 7 * * *) missed its Tue Sep 15 7:00 AM run — last started Sun Sep 13 9:34 AM
- 'vp-follower-growth-monthly-check' (cron 50 9 * * 1) missed its Mon Sep 14 9:50 AM run — last started Mon Sep 7 9:59 AM
- 'zoom-voicemail-alert' (cron 10,30,50 9-19 * * 1-6) missed its Tue Sep 15 11:50 AM run — last started Sat Sep 12 7:56 PM
- 'chekkit-unanswered-eod-followup' (cron 0 19 * * 1-6) missed its Mon Sep 14 7:00 PM run — last started Sat Sep 12 7:29 PM
- 'gdrive-cache-refresh' (cron 0 3 * * *) missed its Tue Sep 15 3:00 AM run — last started Mon Sep 14 4:50 AM
- 'jewelry-onhand-nightly-pull' (cron 30 20 * * 1-6) missed its Mon Sep 14 8:30 PM run — last started Sat Sep 12 8:44 PM
- 'nics-weekly-mtd-ranking' (cron 30 9 * * 1) missed its Mon Sep 14 9:30 AM run — last started Mon Sep 7 9:39 AM
- 'bravo-prestaging-7am' (cron 30 6 * * *) missed its Tue Sep 15 6:30 AM run — last started Mon Sep 14 6:42 AM
- 'discount-review' (cron 25 8 * * *) missed its Tue Sep 15 8:25 AM run — last started Sun Sep 13 9:47 AM
- 'zoom-voicemail-eod-review' (cron 45 17 * * *) missed its Mon Sep 14 5:45 PM run — last started Sun Sep 13 11:19 PM
- 'sold-review' (cron 45 7 * * *) missed its Tue Sep 15 7:45 AM run — last started Sun Sep 13 9:47 AM
- 'weekly-markdown-verification-review' (cron 35 9 * * 1) missed its Mon Sep 14 9:35 AM run — last started Mon Sep 7 9:44 AM
- 'indeed-applicant-outreach' (cron 0 9-19 * * *) missed its Tue Sep 15 11:00 AM run — last started Mon Sep 14 12:06 AM
- 'bravo-morning-pull' (cron 50 6 * * *) missed its Tue Sep 15 6:50 AM run — last started Mon Sep 14 6:55 AM
- 'jewelry-pull-watchdog' (cron 15 9 * * 2-7,0) missed its Tue Sep 15 9:15 AM run — last started Sun Sep 13 10:00 AM
- 'precious-metals-settlement-handler' (cron 0 9 * * *) missed its Tue Sep 15 9:00 AM run — last started Sun Sep 13 10:29 AM
- 'bravo-preflight-relaunch' (cron 0 4 * * *) missed its Tue Sep 15 4:00 AM run — last started Mon Sep 14 4:50 AM
- 'hiring-inbox-watch' (cron 20 10,12,14,16,18 * * 1-6) missed its Tue Sep 15 10:20 AM run — last started Sat Sep 12 6:39 PM
- 'vp-ai-search-autofix' (cron 30 8 * * 1) missed its Mon Sep 14 8:30 AM run — last started Mon Sep 7 8:36 AM
- 'jewelry-onhand-catchup' (cron 45 7 * * 2-7,0) missed its Tue Sep 15 7:45 AM run — last started Sun Sep 13 10:34 AM
- 'google-reviews-post-watchdog' (cron 45 10 * * 1) missed its Mon Sep 14 10:45 AM run — last started Mon Sep 7 10:57 AM
- 'fleet-guardian' (cron 45 12,21 * * *) missed its Mon Sep 14 9:45 PM run — last started Mon Sep 14 12:06 AM
- 'unified-search-index-refresh' (cron 30 3 * * *) missed its Tue Sep 15 3:30 AM run — last started Mon Sep 14 6:42 AM
- 'shop-in-store-sync' (cron 10 10,16 * * *) missed its Tue Sep 15 10:10 AM run — last started Sun Sep 13 4:42 PM
- 'gusto-keep-alive' (cron 40 */2 * * *) missed its Tue Sep 15 10:40 AM run — last started Mon Sep 14 6:55 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 14 7:40 AM run — last started Mon Sep 7 7:42 AM
- 'ask-handbook-responder' (cron 5,35 10-18 * * 1-6) missed its Tue Sep 15 11:35 AM run — last started Sat Sep 12 7:33 PM
- 'vp-deal-reels-weekly' (cron 30 14 * * 1) missed its Mon Sep 14 2:30 PM run — last started Mon Sep 7 2:38 PM
- 'vp-community-weekly' (cron 10 15 * * 1) missed its Mon Sep 14 3:10 PM run — last started Mon Sep 7 3:17 PM
- 'vp-engagement-weekly' (cron 45 15 * * 1) missed its Mon Sep 14 3:45 PM run — last started Mon Sep 7 3:53 PM
- 'vp-staff-video-prompt' (cron 10 9 * * 2) missed its Tue Sep 15 9:10 AM run — last started Tue Sep 8 9:20 AM
- 'ffl-transfer-email-responder' (cron 50 8,16 * * *) missed its Tue Sep 15 8:50 AM run — last started Mon Sep 14 6:55 AM
- 'brevo-weekly-draft-guard' (cron 50 11 * * 1) missed its Mon Sep 14 11:50 AM run — last started Mon Sep 7 12:28 PM
- 'daily-unopened-email-eval' (cron 0 18 * * *) missed its Mon Sep 14 6:00 PM run — last started Sat Sep 12 6:02 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 14 11:45 AM run — last started Mon Sep 7 11:46 AM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 14 5:15 AM run — last started Mon Sep 7 5:23 AM
- 'brevo-welcome-new-contacts' (cron 0 10 * * *) missed its Tue Sep 15 10:00 AM run — last started Sun Sep 13 11:33 AM
- 'ebay-markdown-terminal-weekly' (cron 15 12 * * 1) missed its Mon Sep 14 12:15 PM run — last started Mon Sep 7 12:30 PM
- 'marketing-ceo-briefing-weekly' (cron 30 11 * * 1) missed its Mon Sep 14 11:30 AM run — last started Mon Sep 7 11:33 AM
- 'preston-interactive-assistant' (cron */5 7-21 * * *) missed its Tue Sep 15 11:55 AM run — last started Sun Sep 13 4:46 PM
- 'morning-brief' (cron 0 8 * * 1-5) missed its Tue Sep 15 8:00 AM run — last started Fri Sep 11 8:59 AM
- 'ceo-mail-brief' (cron 0 7,16 * * *) missed its Tue Sep 15 7:00 AM run — last started Sun Sep 13 4:46 PM
- 'mail-brief-reply-executor' (cron 7,37 6-22 * * *) missed its Tue Sep 15 11:37 AM run — last started Sun Sep 13 4:50 PM
- 'scheduled-task-model-audit-weekly' (cron 0 5 * * 1) missed its Mon Sep 14 5:00 AM run — last started Mon Sep 7 5:04 AM
- 'document-photos-index-refresh' (cron 0 5 * * *) missed its Tue Sep 15 5:00 AM run — last started Sun Sep 13 5:58 AM
- 'unified-search-verify' (cron 50 4 * * *) missed its Tue Sep 15 4:50 AM run — last started Sun Sep 13 6:16 AM
- 'monday-bravo-cell-gapfill' (cron 30 20 * * 0) missed its Sun Sep 13 8:30 PM run — last started Sun Sep 6 8:40 PM
- 'insurance-inbox-watch' (cron 44 6 * * *) missed its Tue Sep 15 6:44 AM run — last started Sun Sep 13 1:46 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 14 7:26 AM run — last started Mon Sep 7 7:33 AM
- 'health-episode-capture' (cron 15 9 * * *) missed its Tue Sep 15 9:15 AM run — last started Sat Sep 12 9:34 AM
- 'bonus-pace-monday' (cron 35 9 * * 1) missed its Mon Sep 14 9:35 AM run — last started Mon Sep 7 11:24 AM
- 'health-records-intake' (cron 0 21 * * *) missed its Mon Sep 14 9:00 PM run — last started Sat Sep 12 9:30 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 13 9:00 AM run — last started Sun Sep 6 9:37 AM
- 'bonus-paid-verify' (cron 0 10 * * 1) missed its Mon Sep 14 10:00 AM run — last started Mon Sep 7 11:24 AM
- 'ceo-weekly-scorecard' (cron 15 12 * * 1) missed its Mon Sep 14 12:15 PM run — last started Mon Sep 7 12:39 PM
- 'weekly-training-pipeline' (cron 0 7 * * 1) missed its Mon Sep 14 7:00 AM run — last started Tue Sep 8 12:05 PM
- 'connector-health-daily' (cron 40 5 * * *) missed its Tue Sep 15 5:40 AM run — last started Sat Sep 12 5:41 AM
- launchd agent com.valleypawn.claude-keepalive last exited with status 126
- launchd agent com.valleypawn.compliance-brief last exited with status 1
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127




















## 2026-09-14 22:30 — ISSUES FOUND

- 'chekkit-new-review-alert' (cron 10 9-21 * * *) missed its Mon Sep 14 8:10 PM run — last started Mon Sep 14 6:13 PM
- 'monthly-we-buy-gold-silver-email' (cron 0 9 1 * *) missed its Tue Sep 1 9:00 AM run — last started Tue Sep 1 2:18 AM
- 'nightly-chekkit-review-responses' (cron 30 19 * * *) missed its Mon Sep 14 7:30 PM run — last started Sun Sep 13 8:23 PM
- 'asset-recovery-daily-refresh' (cron 15 19 * * *) missed its Mon Sep 14 7:15 PM run — last started Sun Sep 13 8:59 PM
- 'funds-verification-watchdog' (cron 45 18 * * *) missed its Mon Sep 14 6:45 PM run — last started Sun Sep 13 8:59 PM
- 'vp-dashboard-refresh' (cron 15 8,19 * * *) missed its Mon Sep 14 7:15 PM run — last started Mon Sep 14 10:00 AM
- 'bald-rock-guest-reviews' (cron 0 11 * * *) missed its Mon Sep 14 11:00 AM run — last started Sun Sep 13 11:09 AM
- 'bravo-health-watchdog' (cron 0 5,17 * * *) missed its Mon Sep 14 5:00 PM run — last started Mon Sep 14 5:01 AM
- 'blog-publisher-watchdog' (cron 0 14 * * 1,4) missed its Mon Sep 14 2:00 PM run — last started Thu Sep 10 2:17 PM
- 'vp-website-deals-weekly' (cron 5 13 * * 1) missed its Mon Sep 14 1:05 PM run — last started Mon Sep 7 1:06 PM
- 'weekly-store-kpis' (cron 30 10 * * 1) missed its Mon Sep 14 10:30 AM run — last started Mon Sep 7 10:33 AM
- 'ebay-weekly-quality-fix' (cron 0 11 * * 1) missed its Mon Sep 14 11:00 AM run — last started Mon Sep 7 11:03 AM
- 'vp-content-batch-preflight' (cron 0 11 * * 1) missed its Mon Sep 14 11:00 AM run — last started Mon Sep 7 11:13 AM
- 'vp-content-batch-postflight' (cron 40 16 * * 1) missed its Mon Sep 14 4:40 PM run — last started Mon Sep 7 4:44 PM
- 'vp-casual-video-daily' (cron 35 19 * * *) missed its Mon Sep 14 7:35 PM run — last started Sun Sep 13 11:19 PM
- 'weekly-loan-review-canvas-refresh' (cron 20 9 * * 1) missed its Mon Sep 14 9:20 AM run — last started Mon Sep 7 9:23 AM
- 'weekly-layaway-review-canvas-refresh' (cron 22 9 * * 1) missed its Mon Sep 14 9:22 AM run — last started Mon Sep 7 9:25 AM
- 'weekly-employee-perf-canvas-refresh' (cron 24 9 * * 1) missed its Mon Sep 14 9:24 AM run — last started Mon Sep 7 9:27 AM
- 'weekly-aged-inventory-canvas-refresh' (cron 26 9 * * 1) missed its Mon Sep 14 9:26 AM run — last started Mon Sep 7 9:28 AM
- 'weekly-store-perf-canvas-refresh' (cron 28 9 * * 1) missed its Mon Sep 14 9:28 AM run — last started Mon Sep 7 9:30 AM
- 'vp-website-shop-nightly' (cron 0 7,15 * * *) missed its Mon Sep 14 3:00 PM run — last started Mon Sep 14 7:31 AM
- 'layaway-yield-weekly' (cron 15 11 * * 1) missed its Mon Sep 14 11:15 AM run — last started Mon Sep 7 11:18 AM
- 'vp-deal-of-week-monday-reminder' (cron 0 11 * * 1) missed its Mon Sep 14 11:00 AM run — last started Mon Sep 7 11:18 AM
- 'northwest-registered-agent-daily-check' (cron 40 8 * * *) missed its Mon Sep 14 8:40 AM run — last started Sun Sep 13 9:34 AM
- 'weekly-social-media-recap' (cron 40 9 * * 1) missed its Mon Sep 14 9:40 AM run — last started Mon Sep 7 9:42 AM
- 'vp-gusto-signature-chase' (cron 5 9 * * 1) missed its Mon Sep 14 9:05 AM run — last started Mon Sep 7 9:14 AM
- 'backup-health-watchdog' (cron 0 7 * * *) missed its Mon Sep 14 7:00 AM run — last started Sun Sep 13 9:34 AM
- 'vp-follower-growth-monthly-check' (cron 50 9 * * 1) missed its Mon Sep 14 9:50 AM run — last started Mon Sep 7 9:59 AM
- 'zoom-voicemail-alert' (cron 10,30,50 9-19 * * 1-6) missed its Mon Sep 14 7:50 PM run — last started Sat Sep 12 7:56 PM
- 'chekkit-unanswered-eod-followup' (cron 0 19 * * 1-6) missed its Mon Sep 14 7:00 PM run — last started Sat Sep 12 7:29 PM
- 'jewelry-onhand-nightly-pull' (cron 30 20 * * 1-6) missed its Mon Sep 14 8:30 PM run — last started Sat Sep 12 8:44 PM
- 'nics-weekly-mtd-ranking' (cron 30 9 * * 1) missed its Mon Sep 14 9:30 AM run — last started Mon Sep 7 9:39 AM
- 'discount-review' (cron 25 8 * * *) missed its Mon Sep 14 8:25 AM run — last started Sun Sep 13 9:47 AM
- 'zoom-voicemail-eod-review' (cron 45 17 * * *) missed its Mon Sep 14 5:45 PM run — last started Sun Sep 13 11:19 PM
- 'sold-review' (cron 45 7 * * *) missed its Mon Sep 14 7:45 AM run — last started Sun Sep 13 9:47 AM
- 'weekly-markdown-verification-review' (cron 35 9 * * 1) missed its Mon Sep 14 9:35 AM run — last started Mon Sep 7 9:44 AM
- 'indeed-applicant-outreach' (cron 0 9-19 * * *) missed its Mon Sep 14 7:00 PM run — last started Mon Sep 14 12:06 AM
- 'precious-metals-settlement-handler' (cron 0 9 * * *) missed its Mon Sep 14 9:00 AM run — last started Sun Sep 13 10:29 AM
- 'hiring-inbox-watch' (cron 20 10,12,14,16,18 * * 1-6) missed its Mon Sep 14 6:20 PM run — last started Sat Sep 12 6:39 PM
- 'vp-ai-search-autofix' (cron 30 8 * * 1) missed its Mon Sep 14 8:30 AM run — last started Mon Sep 7 8:36 AM
- 'google-reviews-post-watchdog' (cron 45 10 * * 1) missed its Mon Sep 14 10:45 AM run — last started Mon Sep 7 10:57 AM
- 'fleet-guardian' (cron 45 12,21 * * *) missed its Mon Sep 14 12:45 PM run — last started Mon Sep 14 12:06 AM
- 'shop-in-store-sync' (cron 10 10,16 * * *) missed its Mon Sep 14 4:10 PM run — last started Sun Sep 13 4:42 PM
- 'gusto-keep-alive' (cron 40 */2 * * *) missed its Mon Sep 14 8:40 PM run — last started Mon Sep 14 6:55 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 14 7:40 AM run — last started Mon Sep 7 7:42 AM
- 'ask-handbook-responder' (cron 5,35 10-18 * * 1-6) missed its Mon Sep 14 6:35 PM run — last started Sat Sep 12 7:33 PM
- 'vp-deal-reels-weekly' (cron 30 14 * * 1) missed its Mon Sep 14 2:30 PM run — last started Mon Sep 7 2:38 PM
- 'vp-community-weekly' (cron 10 15 * * 1) missed its Mon Sep 14 3:10 PM run — last started Mon Sep 7 3:17 PM
- 'vp-engagement-weekly' (cron 45 15 * * 1) missed its Mon Sep 14 3:45 PM run — last started Mon Sep 7 3:53 PM
- 'ffl-transfer-email-responder' (cron 50 8,16 * * *) missed its Mon Sep 14 4:50 PM run — last started Mon Sep 14 6:55 AM
- 'brevo-weekly-draft-guard' (cron 50 11 * * 1) missed its Mon Sep 14 11:50 AM run — last started Mon Sep 7 12:28 PM
- 'daily-unopened-email-eval' (cron 0 18 * * *) missed its Mon Sep 14 6:00 PM run — last started Sat Sep 12 6:02 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 14 11:45 AM run — last started Mon Sep 7 11:46 AM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 14 5:15 AM run — last started Mon Sep 7 5:23 AM
- 'brevo-welcome-new-contacts' (cron 0 10 * * *) missed its Mon Sep 14 10:00 AM run — last started Sun Sep 13 11:33 AM
- 'ebay-markdown-terminal-weekly' (cron 15 12 * * 1) missed its Mon Sep 14 12:15 PM run — last started Mon Sep 7 12:30 PM
- 'marketing-ceo-briefing-weekly' (cron 30 11 * * 1) missed its Mon Sep 14 11:30 AM run — last started Mon Sep 7 11:33 AM
- 'preston-interactive-assistant' (cron */5 7-21 * * *) missed its Mon Sep 14 8:55 PM run — last started Sun Sep 13 4:46 PM
- 'morning-brief' (cron 0 8 * * 1-5) missed its Mon Sep 14 8:00 AM run — last started Fri Sep 11 8:59 AM
- 'ceo-mail-brief' (cron 0 7,16 * * *) missed its Mon Sep 14 4:00 PM run — last started Sun Sep 13 4:46 PM
- 'mail-brief-reply-executor' (cron 7,37 6-22 * * *) missed its Mon Sep 14 8:37 PM run — last started Sun Sep 13 4:50 PM
- 'scheduled-task-model-audit-weekly' (cron 0 5 * * 1) missed its Mon Sep 14 5:00 AM run — last started Mon Sep 7 5:04 AM
- 'document-photos-index-refresh' (cron 0 5 * * *) missed its Mon Sep 14 5:00 AM run — last started Sun Sep 13 5:58 AM
- 'unified-search-verify' (cron 50 4 * * *) missed its Mon Sep 14 4:50 AM run — last started Sun Sep 13 6:16 AM
- 'monday-bravo-cell-gapfill' (cron 30 20 * * 0) missed its Sun Sep 13 8:30 PM run — last started Sun Sep 6 8:40 PM
- 'insurance-inbox-watch' (cron 44 6 * * *) missed its Mon Sep 14 6:44 AM run — last started Sun Sep 13 1:46 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 14 7:26 AM run — last started Mon Sep 7 7:33 AM
- 'health-episode-capture' (cron 15 9 * * *) missed its Mon Sep 14 9:15 AM run — last started Sat Sep 12 9:34 AM
- 'bonus-pace-monday' (cron 35 9 * * 1) missed its Mon Sep 14 9:35 AM run — last started Mon Sep 7 11:24 AM
- 'health-records-intake' (cron 0 21 * * *) missed its Sun Sep 13 9:00 PM run — last started Sat Sep 12 9:30 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 13 9:00 AM run — last started Sun Sep 6 9:37 AM
- 'bonus-paid-verify' (cron 0 10 * * 1) missed its Mon Sep 14 10:00 AM run — last started Mon Sep 7 11:24 AM
- 'ceo-weekly-scorecard' (cron 15 12 * * 1) missed its Mon Sep 14 12:15 PM run — last started Mon Sep 7 12:39 PM
- 'weekly-training-pipeline' (cron 0 7 * * 1) missed its Mon Sep 14 7:00 AM run — last started Tue Sep 8 12:05 PM
- 'connector-health-daily' (cron 40 5 * * *) missed its Mon Sep 14 5:40 AM run — last started Sat Sep 12 5:41 AM
- launchd agent com.valleypawn.claude-keepalive last exited with status 126
- launchd agent com.valleypawn.compliance-brief last exited with status 1
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127





















## 2026-09-14 13:30 — ISSUES FOUND

- 'monthly-we-buy-gold-silver-email' (cron 0 9 1 * *) missed its Tue Sep 1 9:00 AM run — last started Tue Sep 1 2:18 AM
- 'bald-rock-guest-reviews' (cron 0 11 * * *) missed its Mon Sep 14 11:00 AM run — last started Sun Sep 13 11:09 AM
- 'weekly-store-kpis' (cron 30 10 * * 1) missed its Mon Sep 14 10:30 AM run — last started Mon Sep 7 10:33 AM
- 'ebay-weekly-quality-fix' (cron 0 11 * * 1) missed its Mon Sep 14 11:00 AM run — last started Mon Sep 7 11:03 AM
- 'vp-content-batch-preflight' (cron 0 11 * * 1) missed its Mon Sep 14 11:00 AM run — last started Mon Sep 7 11:13 AM
- 'weekly-loan-review-canvas-refresh' (cron 20 9 * * 1) missed its Mon Sep 14 9:20 AM run — last started Mon Sep 7 9:23 AM
- 'weekly-layaway-review-canvas-refresh' (cron 22 9 * * 1) missed its Mon Sep 14 9:22 AM run — last started Mon Sep 7 9:25 AM
- 'weekly-employee-perf-canvas-refresh' (cron 24 9 * * 1) missed its Mon Sep 14 9:24 AM run — last started Mon Sep 7 9:27 AM
- 'weekly-aged-inventory-canvas-refresh' (cron 26 9 * * 1) missed its Mon Sep 14 9:26 AM run — last started Mon Sep 7 9:28 AM
- 'weekly-store-perf-canvas-refresh' (cron 28 9 * * 1) missed its Mon Sep 14 9:28 AM run — last started Mon Sep 7 9:30 AM
- 'layaway-yield-weekly' (cron 15 11 * * 1) missed its Mon Sep 14 11:15 AM run — last started Mon Sep 7 11:18 AM
- 'vp-deal-of-week-monday-reminder' (cron 0 11 * * 1) missed its Mon Sep 14 11:00 AM run — last started Mon Sep 7 11:18 AM
- 'northwest-registered-agent-daily-check' (cron 40 8 * * *) missed its Mon Sep 14 8:40 AM run — last started Sun Sep 13 9:34 AM
- 'weekly-social-media-recap' (cron 40 9 * * 1) missed its Mon Sep 14 9:40 AM run — last started Mon Sep 7 9:42 AM
- 'vp-gusto-signature-chase' (cron 5 9 * * 1) missed its Mon Sep 14 9:05 AM run — last started Mon Sep 7 9:14 AM
- 'backup-health-watchdog' (cron 0 7 * * *) missed its Mon Sep 14 7:00 AM run — last started Sun Sep 13 9:34 AM
- 'vp-follower-growth-monthly-check' (cron 50 9 * * 1) missed its Mon Sep 14 9:50 AM run — last started Mon Sep 7 9:59 AM
- 'zoom-voicemail-alert' (cron 10,30,50 9-19 * * 1-6) missed its Mon Sep 14 11:50 AM run — last started Sat Sep 12 7:56 PM
- 'nics-weekly-mtd-ranking' (cron 30 9 * * 1) missed its Mon Sep 14 9:30 AM run — last started Mon Sep 7 9:39 AM
- 'discount-review' (cron 25 8 * * *) missed its Mon Sep 14 8:25 AM run — last started Sun Sep 13 9:47 AM
- 'sold-review' (cron 45 7 * * *) missed its Mon Sep 14 7:45 AM run — last started Sun Sep 13 9:47 AM
- 'weekly-markdown-verification-review' (cron 35 9 * * 1) missed its Mon Sep 14 9:35 AM run — last started Mon Sep 7 9:44 AM
- 'indeed-applicant-outreach' (cron 0 9-19 * * *) missed its Mon Sep 14 11:00 AM run — last started Mon Sep 14 12:06 AM
- 'precious-metals-settlement-handler' (cron 0 9 * * *) missed its Mon Sep 14 9:00 AM run — last started Sun Sep 13 10:29 AM
- 'hiring-inbox-watch' (cron 20 10,12,14,16,18 * * 1-6) missed its Mon Sep 14 10:20 AM run — last started Sat Sep 12 6:39 PM
- 'vp-ai-search-autofix' (cron 30 8 * * 1) missed its Mon Sep 14 8:30 AM run — last started Mon Sep 7 8:36 AM
- 'google-reviews-post-watchdog' (cron 45 10 * * 1) missed its Mon Sep 14 10:45 AM run — last started Mon Sep 7 10:57 AM
- 'shop-in-store-sync' (cron 10 10,16 * * *) missed its Mon Sep 14 10:10 AM run — last started Sun Sep 13 4:42 PM
- 'gusto-keep-alive' (cron 40 */2 * * *) missed its Mon Sep 14 10:40 AM run — last started Mon Sep 14 6:55 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 14 7:40 AM run — last started Mon Sep 7 7:42 AM
- 'ask-handbook-responder' (cron 5,35 10-18 * * 1-6) missed its Mon Sep 14 11:35 AM run — last started Sat Sep 12 7:33 PM
- 'ffl-transfer-email-responder' (cron 50 8,16 * * *) missed its Mon Sep 14 8:50 AM run — last started Mon Sep 14 6:55 AM
- 'brevo-weekly-draft-guard' (cron 50 11 * * 1) missed its Mon Sep 14 11:50 AM run — last started Mon Sep 7 12:28 PM
- 'daily-unopened-email-eval' (cron 0 18 * * *) missed its Sun Sep 13 6:00 PM run — last started Sat Sep 12 6:02 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 14 11:45 AM run — last started Mon Sep 7 11:46 AM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 14 5:15 AM run — last started Mon Sep 7 5:23 AM
- 'brevo-welcome-new-contacts' (cron 0 10 * * *) missed its Mon Sep 14 10:00 AM run — last started Sun Sep 13 11:33 AM
- 'marketing-ceo-briefing-weekly' (cron 30 11 * * 1) missed its Mon Sep 14 11:30 AM run — last started Mon Sep 7 11:33 AM
- 'preston-interactive-assistant' (cron */5 7-21 * * *) missed its Mon Sep 14 11:55 AM run — last started Sun Sep 13 4:46 PM
- 'morning-brief' (cron 0 8 * * 1-5) missed its Mon Sep 14 8:00 AM run — last started Fri Sep 11 8:59 AM
- 'ceo-mail-brief' (cron 0 7,16 * * *) missed its Mon Sep 14 7:00 AM run — last started Sun Sep 13 4:46 PM
- 'mail-brief-reply-executor' (cron 7,37 6-22 * * *) missed its Mon Sep 14 11:37 AM run — last started Sun Sep 13 4:50 PM
- 'scheduled-task-model-audit-weekly' (cron 0 5 * * 1) missed its Mon Sep 14 5:00 AM run — last started Mon Sep 7 5:04 AM
- 'document-photos-index-refresh' (cron 0 5 * * *) missed its Mon Sep 14 5:00 AM run — last started Sun Sep 13 5:58 AM
- 'unified-search-verify' (cron 50 4 * * *) missed its Mon Sep 14 4:50 AM run — last started Sun Sep 13 6:16 AM
- 'monday-bravo-cell-gapfill' (cron 30 20 * * 0) missed its Sun Sep 13 8:30 PM run — last started Sun Sep 6 8:40 PM
- 'insurance-inbox-watch' (cron 44 6 * * *) missed its Mon Sep 14 6:44 AM run — last started Sun Sep 13 1:46 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 14 7:26 AM run — last started Mon Sep 7 7:33 AM
- 'health-episode-capture' (cron 15 9 * * *) missed its Mon Sep 14 9:15 AM run — last started Sat Sep 12 9:34 AM
- 'bonus-pace-monday' (cron 35 9 * * 1) missed its Mon Sep 14 9:35 AM run — last started Mon Sep 7 11:24 AM
- 'health-records-intake' (cron 0 21 * * *) missed its Sun Sep 13 9:00 PM run — last started Sat Sep 12 9:30 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 13 9:00 AM run — last started Sun Sep 6 9:37 AM
- 'bonus-paid-verify' (cron 0 10 * * 1) missed its Mon Sep 14 10:00 AM run — last started Mon Sep 7 11:24 AM
- 'weekly-training-pipeline' (cron 0 7 * * 1) missed its Mon Sep 14 7:00 AM run — last started Tue Sep 8 12:05 PM
- 'connector-health-daily' (cron 40 5 * * *) missed its Mon Sep 14 5:40 AM run — last started Sat Sep 12 5:41 AM
- launchd agent com.valleypawn.claude-keepalive last exited with status 126
- launchd agent com.valleypawn.compliance-brief last exited with status 1
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127






















## 2026-09-13 22:30 — ISSUES FOUND

- 'monthly-we-buy-gold-silver-email' (cron 0 9 1 * *) missed its Tue Sep 1 9:00 AM run — last started Tue Sep 1 2:18 AM
- 'sunday-checklist-summary' (cron 0 20 * * 0) missed its Sun Sep 13 8:00 PM run — last started Sun Sep 6 8:08 PM
- 'vp-casual-video-daily' (cron 35 19 * * *) missed its Sun Sep 13 7:35 PM run — last started Sat Sep 12 7:56 PM
- 'zoom-voicemail-eod-review' (cron 45 17 * * *) missed its Sun Sep 13 5:45 PM run — last started Sat Sep 12 5:47 PM
- 'weekly-markdown-verification-pull' (cron 0 19 * * 0) missed its Sun Sep 13 7:00 PM run — last started Sun Sep 6 7:00 PM
- 'indeed-applicant-outreach' (cron 0 9-19 * * *) missed its Sun Sep 13 7:00 PM run — last started Sun Sep 13 4:31 PM
- 'gusto-keep-alive' (cron 40 */2 * * *) missed its Sun Sep 13 8:40 PM run — last started Sun Sep 13 4:42 PM
- 'ffl-transfer-email-responder' (cron 50 8,16 * * *) missed its Sun Sep 13 4:50 PM run — last started Sun Sep 13 10:58 AM
- 'daily-unopened-email-eval' (cron 0 18 * * *) missed its Sun Sep 13 6:00 PM run — last started Sat Sep 12 6:02 PM
- 'preston-interactive-assistant' (cron */5 7-21 * * *) missed its Sun Sep 13 8:55 PM run — last started Sun Sep 13 4:46 PM
- 'mail-brief-reply-executor' (cron 7,37 6-22 * * *) missed its Sun Sep 13 8:37 PM run — last started Sun Sep 13 4:50 PM
- 'monday-bravo-cell-gapfill' (cron 30 20 * * 0) missed its Sun Sep 13 8:30 PM run — last started Sun Sep 6 8:40 PM
- 'health-episode-capture' (cron 15 9 * * *) missed its Sun Sep 13 9:15 AM run — last started Sat Sep 12 9:34 AM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 13 9:00 AM run — last started Sun Sep 6 9:37 AM
- 'connector-health-daily' (cron 40 5 * * *) missed its Sun Sep 13 5:40 AM run — last started Sat Sep 12 5:41 AM
- launchd agent com.valleypawn.claude-keepalive last exited with status 126
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127























## 2026-09-13 13:30 — ISSUES FOUND

- 'monthly-we-buy-gold-silver-email' (cron 0 9 1 * *) missed its Tue Sep 1 9:00 AM run — last started Tue Sep 1 2:18 AM
- 'mail-brief-reply-executor' (cron 7,37 6-22 * * *) missed its Sun Sep 13 11:37 AM run — last started Sun Sep 13 6:49 AM
- 'insurance-inbox-watch' (cron 44 6 * * *) missed its Sun Sep 13 6:44 AM run — last started Sat Sep 12 6:47 AM
- 'health-episode-capture' (cron 15 9 * * *) missed its Sun Sep 13 9:15 AM run — last started Sat Sep 12 9:34 AM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 13 9:00 AM run — last started Sun Sep 6 9:37 AM
- 'connector-health-daily' (cron 40 5 * * *) missed its Sun Sep 13 5:40 AM run — last started Sat Sep 12 5:41 AM
- launchd agent com.valleypawn.claude-keepalive last exited with status 126
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127
























## 2026-09-12 22:30 — ISSUES FOUND

- 'monthly-we-buy-gold-silver-email' (cron 0 9 1 * *) missed its Tue Sep 1 9:00 AM run — last started Tue Sep 1 2:18 AM
- launchd agent com.valleypawn.claude-keepalive last exited with status 126
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127

























## 2026-09-12 13:30 — ISSUES FOUND

- 'monthly-we-buy-gold-silver-email' (cron 0 9 1 * *) missed its Tue Sep 1 9:00 AM run — last started Tue Sep 1 2:18 AM
- launchd agent com.valleypawn.claude-keepalive last exited with status 126
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127


























## 2026-09-11 22:30 — ISSUES FOUND

- 'monthly-we-buy-gold-silver-email' (cron 0 9 1 * *) missed its Tue Sep 1 9:00 AM run — last started Tue Sep 1 2:18 AM
- launchd agent com.valleypawn.claude-keepalive last exited with status 126
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127



























## 2026-09-11 13:30 — ISSUES FOUND

- 'monthly-we-buy-gold-silver-email' (cron 0 9 1 * *) missed its Tue Sep 1 9:00 AM run — last started Tue Sep 1 2:18 AM
- launchd agent com.valleypawn.claude-keepalive last exited with status 126
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127




























## 2026-09-10 22:30 — ISSUES FOUND

- 'monthly-we-buy-gold-silver-email' (cron 0 9 1 * *) missed its Tue Sep 1 9:00 AM run — last started Tue Sep 1 2:18 AM
- usage-cap skips climbing: +447 since Thu 1:30 PM (~50/hr) — tasks are being throttled right now
- launchd agent com.valleypawn.ffl-guardian last exited with status 2
- launchd agent com.valleypawn.claude-keepalive last exited with status 126
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127





























## 2026-09-10 13:30 — ISSUES FOUND

- 'monthly-we-buy-gold-silver-email' (cron 0 9 1 * *) missed its Tue Sep 1 9:00 AM run — last started Tue Sep 1 2:18 AM
- 'preston-interactive-assistant' (cron */5 7-21 * * *) missed its Thu Sep 10 11:55 AM run — last started Wed Sep 9 5:18 PM
- 'morning-brief' (cron 0 8 * * 1-5) missed its Thu Sep 10 8:00 AM run — last started Wed Sep 9 8:10 AM
- 'ceo-mail-brief' (cron 0 7,16 * * *) missed its Thu Sep 10 7:00 AM run — last started Wed Sep 9 4:07 PM
- 'mail-brief-reply-executor' (cron 7,37 6-22 * * *) missed its Thu Sep 10 11:37 AM run — last started Wed Sep 9 10:46 PM
- 'document-photos-index-refresh' (cron 0 5 * * *) missed its Thu Sep 10 5:00 AM run — last started Wed Sep 9 5:02 AM
- 'unified-search-verify' (cron 50 4 * * *) missed its Thu Sep 10 4:50 AM run — last started Wed Sep 9 4:56 AM
- 'ebay-feedback-reply-weekly' (cron 20 10 * * 4) missed its Thu Sep 10 10:20 AM run — last started Sat Sep 5 3:46 PM
- 'insurance-inbox-watch' (cron 44 6 * * *) missed its Thu Sep 10 6:44 AM run — last started Wed Sep 9 6:49 AM
- 'bonus-month-close' (cron 0 9 10 * *) missed its Thu Sep 10 9:00 AM run — last started NEVER
- 'health-episode-capture' (cron 15 9 * * *) missed its Thu Sep 10 9:15 AM run — last started Wed Sep 9 9:18 AM
- 'connector-health-daily' (cron 40 5 * * *) missed its Thu Sep 10 5:40 AM run — last started NEVER
- usage-cap skips climbing: +5346 since Wed 10:30 PM (~356/hr) — tasks are being throttled right now
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 127
- launchd agent com.valleypawn.disk-health last exited with status 126





























