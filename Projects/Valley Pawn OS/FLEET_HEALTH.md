# Fleet Health — rolling sentinel log

Written by `bin/fleet_health_sentinel.py` (native launchd, no Claude usage). Newest first, last 30 runs kept. DM alerts go to Joshua only when an issue is first detected.

## 2026-09-30 22:30 — ISSUES FOUND

- 'daily-supply-order' (cron 15 3 * * 2) missed its Tue Sep 29 3:15 AM run — last started Tue Sep 15 7:04 AM
- 'tuesday-supply-summary' (cron 45 10 * * 2) missed its Tue Sep 29 10:45 AM run — last started Tue Sep 15 11:03 AM
- 'vp-deal-of-week-monday-prompt' (cron 10 8 * * 1) missed its Mon Sep 28 8:10 AM run — last started Mon Sep 14 9:29 AM
- 'vp-deal-of-week-monday-pick' (cron 30 12 * * 1) missed its Mon Sep 28 12:30 PM run — last started Mon Sep 14 4:57 PM
- 'vp-publer-analytics-friday' (cron 0 16 * * 5) missed its Fri Sep 25 4:00 PM run — last started Fri Sep 11 4:01 PM
- 'vp-deal-of-week-monday-reminder' (cron 0 11 * * 1) missed its Mon Sep 28 11:00 AM run — last started Wed Sep 16 3:38 AM
- 'vp-gusto-signature-chase' (cron 5 9 * * 1) missed its Mon Sep 28 9:05 AM run — last started Wed Sep 16 4:04 AM
- 'vp-follower-growth-monthly-check' (cron 50 9 * * 1) missed its Mon Sep 28 9:50 AM run — last started Wed Sep 16 4:55 AM
- 'vp-thursday-email-watchdog' (cron 30 10 * * 4) missed its Thu Sep 24 10:30 AM run — last started Thu Sep 10 12:39 PM
- 'weekly-online-store-audit' (cron 0 8 * * 0) missed its Sun Sep 27 8:00 AM run — last started Sun Sep 13 10:58 AM
- 'vp-presence-audit-weekly' (cron 20 16 * * 0) missed its Sun Sep 27 4:20 PM run — last started Sun Sep 13 4:46 PM
- 'marketing-ceo-briefing-weekly' (cron 30 11 * * 1) missed its Mon Sep 28 11:30 AM run — last started Wed Sep 16 4:47 PM
- 'scheduled-task-model-audit-weekly' (cron 0 5 * * 1) missed its Mon Sep 28 5:00 AM run — last started Wed Sep 16 5:04 PM
- 'qbo-api-token-refresh' (cron 0 5 * * 0) missed its Sun Sep 27 5:00 AM run — last started Sun Sep 13 6:16 AM
- launchd agent com.valleypawn.taskperms-oneshot last exited with status 1

## 2026-09-30 13:30 — ISSUES FOUND

- 'daily-supply-order' (cron 15 3 * * 2) missed its Tue Sep 29 3:15 AM run — last started Tue Sep 15 7:04 AM
- 'tuesday-supply-summary' (cron 45 10 * * 2) missed its Tue Sep 29 10:45 AM run — last started Tue Sep 15 11:03 AM
- 'vp-deal-of-week-monday-prompt' (cron 10 8 * * 1) missed its Mon Sep 28 8:10 AM run — last started Mon Sep 14 9:29 AM
- 'vp-deal-of-week-monday-pick' (cron 30 12 * * 1) missed its Mon Sep 28 12:30 PM run — last started Mon Sep 14 4:57 PM
- 'vp-publer-analytics-friday' (cron 0 16 * * 5) missed its Fri Sep 25 4:00 PM run — last started Fri Sep 11 4:01 PM
- 'vp-deal-of-week-monday-reminder' (cron 0 11 * * 1) missed its Mon Sep 28 11:00 AM run — last started Wed Sep 16 3:38 AM
- 'vp-gusto-signature-chase' (cron 5 9 * * 1) missed its Mon Sep 28 9:05 AM run — last started Wed Sep 16 4:04 AM
- 'vp-follower-growth-monthly-check' (cron 50 9 * * 1) missed its Mon Sep 28 9:50 AM run — last started Wed Sep 16 4:55 AM
- 'vp-thursday-email-watchdog' (cron 30 10 * * 4) missed its Thu Sep 24 10:30 AM run — last started Thu Sep 10 12:39 PM
- 'weekly-online-store-audit' (cron 0 8 * * 0) missed its Sun Sep 27 8:00 AM run — last started Sun Sep 13 10:58 AM
- 'vp-presence-audit-weekly' (cron 20 16 * * 0) missed its Sun Sep 27 4:20 PM run — last started Sun Sep 13 4:46 PM
- 'marketing-ceo-briefing-weekly' (cron 30 11 * * 1) missed its Mon Sep 28 11:30 AM run — last started Wed Sep 16 4:47 PM
- 'scheduled-task-model-audit-weekly' (cron 0 5 * * 1) missed its Mon Sep 28 5:00 AM run — last started Wed Sep 16 5:04 PM
- 'qbo-api-token-refresh' (cron 0 5 * * 0) missed its Sun Sep 27 5:00 AM run — last started Sun Sep 13 6:16 AM
- launchd agent com.valleypawn.taskperms-oneshot last exited with status 1


## 2026-09-29 22:30 — ISSUES FOUND

- 'daily-supply-order' (cron 15 3 * * 2) missed its Tue Sep 29 3:15 AM run — last started Tue Sep 15 7:04 AM
- 'tuesday-supply-summary' (cron 45 10 * * 2) missed its Tue Sep 29 10:45 AM run — last started Tue Sep 15 11:03 AM
- 'vp-website-trend-daily-refresh' (cron 45 0 * * *) missed its Tue Sep 29 12:45 AM run — last started Wed Sep 16 1:22 AM
- 'vp-deal-of-week-monday-prompt' (cron 10 8 * * 1) missed its Mon Sep 28 8:10 AM run — last started Mon Sep 14 9:29 AM
- 'vp-deal-of-week-monday-pick' (cron 30 12 * * 1) missed its Mon Sep 28 12:30 PM run — last started Mon Sep 14 4:57 PM
- 'nightly-desktop-cleanup' (cron 0 3 * * *) missed its Tue Sep 29 3:00 AM run — last started Wed Sep 16 3:38 AM
- 'vp-publer-analytics-friday' (cron 0 16 * * 5) missed its Fri Sep 25 4:00 PM run — last started Fri Sep 11 4:01 PM
- 'preston-ebay-feedback-watch' (cron 0 9 * * *) missed its Tue Sep 29 9:00 AM run — last started Wed Aug 26 9:09 AM
- 'vp-deal-of-week-monday-reminder' (cron 0 11 * * 1) missed its Mon Sep 28 11:00 AM run — last started Wed Sep 16 3:38 AM
- 'vp-gusto-signature-chase' (cron 5 9 * * 1) missed its Mon Sep 28 9:05 AM run — last started Wed Sep 16 4:04 AM
- 'vp-follower-growth-monthly-check' (cron 50 9 * * 1) missed its Mon Sep 28 9:50 AM run — last started Wed Sep 16 4:55 AM
- 'gdrive-cache-refresh' (cron 0 3 * * *) missed its Tue Sep 29 3:00 AM run — last started Wed Sep 16 6:15 AM
- 'vp-thursday-email-watchdog' (cron 30 10 * * 4) missed its Thu Sep 24 10:30 AM run — last started Thu Sep 10 12:39 PM
- 'vp-staff-video-chase' (cron 15 11 * * 3) missed its Wed Sep 23 11:15 AM run — last started Wed Sep 16 4:40 PM
- 'weekly-online-store-audit' (cron 0 8 * * 0) missed its Sun Sep 27 8:00 AM run — last started Sun Sep 13 10:58 AM
- 'vp-presence-audit-weekly' (cron 20 16 * * 0) missed its Sun Sep 27 4:20 PM run — last started Sun Sep 13 4:46 PM
- 'marketing-ceo-briefing-weekly' (cron 30 11 * * 1) missed its Mon Sep 28 11:30 AM run — last started Wed Sep 16 4:47 PM
- 'scheduled-task-model-audit-weekly' (cron 0 5 * * 1) missed its Mon Sep 28 5:00 AM run — last started Wed Sep 16 5:04 PM
- 'document-photos-index-refresh' (cron 0 5 * * *) missed its Tue Sep 29 5:00 AM run — last started Wed Sep 16 5:04 PM
- 'qbo-api-token-refresh' (cron 0 5 * * 0) missed its Sun Sep 27 5:00 AM run — last started Sun Sep 13 6:16 AM



## 2026-09-29 13:30 — ISSUES FOUND

- 'vp-staff-video-chase' (cron 15 11 * * 3) missed its Wed Sep 23 11:15 AM run — last started Wed Sep 16 4:40 PM
- 'weekly-online-store-audit' (cron 0 8 * * 0) missed its Sun Sep 27 8:00 AM run — last started Sun Sep 13 10:58 AM
- 'vp-presence-audit-weekly' (cron 20 16 * * 0) missed its Sun Sep 27 4:20 PM run — last started Sun Sep 13 4:46 PM




## 2026-09-28 22:30 — ISSUES FOUND

- 'vp-staff-video-prompt' (cron 10 9 * * 2) missed its Tue Sep 22 9:10 AM run — last started Wed Sep 16 4:39 PM
- 'vp-staff-video-chase' (cron 15 11 * * 3) missed its Wed Sep 23 11:15 AM run — last started Wed Sep 16 4:40 PM
- 'weekly-online-store-audit' (cron 0 8 * * 0) missed its Sun Sep 27 8:00 AM run — last started Sun Sep 13 10:58 AM
- 'vp-presence-audit-weekly' (cron 20 16 * * 0) missed its Sun Sep 27 4:20 PM run — last started Sun Sep 13 4:46 PM
- 'health-episode-capture' (cron 15 9 * * *) missed its Mon Sep 28 9:15 AM run — last started Wed Sep 16 5:22 PM
- launchd agent com.valleypawn.commandcenter last exited with status -9





## 2026-09-28 13:30 — ISSUES FOUND

- 'vp-website-shop-nightly' (cron 0 7,15 * * *) missed its Mon Sep 28 7:00 AM run — last started Wed Sep 16 4:11 PM
- 'vp-staff-video-prompt' (cron 10 9 * * 2) missed its Tue Sep 22 9:10 AM run — last started Wed Sep 16 4:39 PM
- 'vp-staff-video-chase' (cron 15 11 * * 3) missed its Wed Sep 23 11:15 AM run — last started Wed Sep 16 4:40 PM
- 'weekly-online-store-audit' (cron 0 8 * * 0) missed its Sun Sep 27 8:00 AM run — last started Sun Sep 13 10:58 AM
- 'vp-presence-audit-weekly' (cron 20 16 * * 0) missed its Sun Sep 27 4:20 PM run — last started Sun Sep 13 4:46 PM
- 'health-episode-capture' (cron 15 9 * * *) missed its Mon Sep 28 9:15 AM run — last started Wed Sep 16 5:22 PM
- launchd agent com.valleypawn.commandcenter last exited with status -9






## 2026-09-27 22:30 — ISSUES FOUND

- 'weekly-analytics-summary' (cron 0 1 * * 1) missed its Mon Sep 21 1:00 AM run — last started Mon Sep 14 1:17 AM
- 'bald-rock-monday-briefing' (cron 15 4 * * 1) missed its Mon Sep 21 4:15 AM run — last started Mon Sep 14 4:50 AM
- 'vp-ai-search-health-check' (cron 10 6 * * 1) missed its Mon Sep 21 6:10 AM run — last started Mon Sep 14 6:42 AM
- 'weekly-social-media-recap' (cron 40 9 * * 1) missed its Mon Sep 21 9:40 AM run — last started Wed Sep 16 3:44 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 21 7:40 AM run — last started Wed Sep 16 4:36 PM
- 'vp-staff-video-prompt' (cron 10 9 * * 2) missed its Tue Sep 22 9:10 AM run — last started Wed Sep 16 4:39 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 21 11:45 AM run — last started Wed Sep 16 4:43 PM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 21 5:15 AM run — last started Wed Sep 16 4:44 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 21 7:26 AM run — last started Wed Sep 16 5:16 PM
- launchd agent com.valleypawn.commandcenter last exited with status -9
- launchd agent com.valleypawn.taskperms-oneshot is installed but NOT loaded







## 2026-09-27 13:30 — ISSUES FOUND

- 'weekly-analytics-summary' (cron 0 1 * * 1) missed its Mon Sep 21 1:00 AM run — last started Mon Sep 14 1:17 AM
- 'bald-rock-monday-briefing' (cron 15 4 * * 1) missed its Mon Sep 21 4:15 AM run — last started Mon Sep 14 4:50 AM
- 'vp-ai-search-health-check' (cron 10 6 * * 1) missed its Mon Sep 21 6:10 AM run — last started Mon Sep 14 6:42 AM
- 'weekly-social-media-recap' (cron 40 9 * * 1) missed its Mon Sep 21 9:40 AM run — last started Wed Sep 16 3:44 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 21 7:40 AM run — last started Wed Sep 16 4:36 PM
- 'vp-staff-video-prompt' (cron 10 9 * * 2) missed its Tue Sep 22 9:10 AM run — last started Wed Sep 16 4:39 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 21 11:45 AM run — last started Wed Sep 16 4:43 PM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 21 5:15 AM run — last started Wed Sep 16 4:44 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 21 7:26 AM run — last started Wed Sep 16 5:16 PM
- launchd agent com.valleypawn.commandcenter last exited with status -9
- launchd agent com.valleypawn.taskperms-oneshot is installed but NOT loaded








## 2026-09-26 22:30 — ISSUES FOUND

- 'weekly-analytics-summary' (cron 0 1 * * 1) missed its Mon Sep 21 1:00 AM run — last started Mon Sep 14 1:17 AM
- 'bald-rock-monday-briefing' (cron 15 4 * * 1) missed its Mon Sep 21 4:15 AM run — last started Mon Sep 14 4:50 AM
- 'vp-ai-search-health-check' (cron 10 6 * * 1) missed its Mon Sep 21 6:10 AM run — last started Mon Sep 14 6:42 AM
- 'weekly-social-media-recap' (cron 40 9 * * 1) missed its Mon Sep 21 9:40 AM run — last started Wed Sep 16 3:44 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 21 7:40 AM run — last started Wed Sep 16 4:36 PM
- 'vp-staff-video-prompt' (cron 10 9 * * 2) missed its Tue Sep 22 9:10 AM run — last started Wed Sep 16 4:39 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 21 11:45 AM run — last started Wed Sep 16 4:43 PM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 21 5:15 AM run — last started Wed Sep 16 4:44 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 21 7:26 AM run — last started Wed Sep 16 5:16 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 20 9:00 AM run — last started Wed Sep 16 5:26 PM
- launchd agent com.valleypawn.commandcenter last exited with status -9
- launchd agent com.valleypawn.taskperms-oneshot is installed but NOT loaded









## 2026-09-26 13:30 — ISSUES FOUND

- 'weekly-analytics-summary' (cron 0 1 * * 1) missed its Mon Sep 21 1:00 AM run — last started Mon Sep 14 1:17 AM
- 'bald-rock-monday-briefing' (cron 15 4 * * 1) missed its Mon Sep 21 4:15 AM run — last started Mon Sep 14 4:50 AM
- 'vp-ai-search-health-check' (cron 10 6 * * 1) missed its Mon Sep 21 6:10 AM run — last started Mon Sep 14 6:42 AM
- 'weekly-social-media-recap' (cron 40 9 * * 1) missed its Mon Sep 21 9:40 AM run — last started Wed Sep 16 3:44 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 21 7:40 AM run — last started Wed Sep 16 4:36 PM
- 'vp-staff-video-prompt' (cron 10 9 * * 2) missed its Tue Sep 22 9:10 AM run — last started Wed Sep 16 4:39 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 21 11:45 AM run — last started Wed Sep 16 4:43 PM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 21 5:15 AM run — last started Wed Sep 16 4:44 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 21 7:26 AM run — last started Wed Sep 16 5:16 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 20 9:00 AM run — last started Wed Sep 16 5:26 PM
- launchd agent com.valleypawn.commandcenter last exited with status -9
- launchd agent com.valleypawn.taskperms-oneshot is installed but NOT loaded










## 2026-09-25 22:30 — ISSUES FOUND

- 'weekly-analytics-summary' (cron 0 1 * * 1) missed its Mon Sep 21 1:00 AM run — last started Mon Sep 14 1:17 AM
- 'bald-rock-monday-briefing' (cron 15 4 * * 1) missed its Mon Sep 21 4:15 AM run — last started Mon Sep 14 4:50 AM
- 'vp-ai-search-health-check' (cron 10 6 * * 1) missed its Mon Sep 21 6:10 AM run — last started Mon Sep 14 6:42 AM
- 'weekly-social-media-recap' (cron 40 9 * * 1) missed its Mon Sep 21 9:40 AM run — last started Wed Sep 16 3:44 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 21 7:40 AM run — last started Wed Sep 16 4:36 PM
- 'vp-staff-video-prompt' (cron 10 9 * * 2) missed its Tue Sep 22 9:10 AM run — last started Wed Sep 16 4:39 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 21 11:45 AM run — last started Wed Sep 16 4:43 PM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 21 5:15 AM run — last started Wed Sep 16 4:44 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 21 7:26 AM run — last started Wed Sep 16 5:16 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 20 9:00 AM run — last started Wed Sep 16 5:26 PM
- launchd agent com.valleypawn.commandcenter last exited with status -9
- launchd agent com.valleypawn.taskperms-oneshot is installed but NOT loaded











## 2026-09-25 13:30 — ISSUES FOUND

- 'weekly-analytics-summary' (cron 0 1 * * 1) missed its Mon Sep 21 1:00 AM run — last started Mon Sep 14 1:17 AM
- 'bald-rock-monday-briefing' (cron 15 4 * * 1) missed its Mon Sep 21 4:15 AM run — last started Mon Sep 14 4:50 AM
- 'vp-ai-search-health-check' (cron 10 6 * * 1) missed its Mon Sep 21 6:10 AM run — last started Mon Sep 14 6:42 AM
- 'weekly-social-media-recap' (cron 40 9 * * 1) missed its Mon Sep 21 9:40 AM run — last started Wed Sep 16 3:44 AM
- 'vp-website-shop-weekly-report' (cron 40 7 * * 1) missed its Mon Sep 21 7:40 AM run — last started Wed Sep 16 4:36 PM
- 'vp-staff-video-prompt' (cron 10 9 * * 2) missed its Tue Sep 22 9:10 AM run — last started Wed Sep 16 4:39 PM
- 'ebay-weekly-channel-audit' (cron 45 11 * * 1) missed its Mon Sep 21 11:45 AM run — last started Wed Sep 16 4:43 PM
- 'weekly-website-health-audit' (cron 15 5 * * 1) missed its Mon Sep 21 5:15 AM run — last started Wed Sep 16 4:44 PM
- 'insurance-renewal-runner' (cron 26 7 * * 1) missed its Mon Sep 21 7:26 AM run — last started Wed Sep 16 5:16 PM
- 'health-weekly-digest' (cron 0 9 * * 0) missed its Sun Sep 20 9:00 AM run — last started Wed Sep 16 5:26 PM
- launchd agent com.valleypawn.commandcenter last exited with status -9
- launchd agent com.valleypawn.taskperms-oneshot is installed but NOT loaded












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





























