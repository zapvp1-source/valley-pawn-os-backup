# Fleet Health — rolling sentinel log

Written by `bin/fleet_health_sentinel.py` (native launchd, no Claude usage). Newest first, last 30 runs kept. DM alerts go to Joshua only when an issue is first detected.

## 2026-08-21 22:30 — ISSUES FOUND

- 'weekly-returns-summary' (cron 20 1 * * 1) missed its Mon Aug 17 1:20 AM run — last started Mon Aug 17 1:03 AM
- 'monday-bravo-combined-compile' (cron 0 8 * * 1) missed its Mon Aug 17 8:00 AM run — last started Mon Aug 3 2:15 PM
- 'monthly-capability-drift-audit' (cron 40 7 1 * *) missed its Sat Aug 1 7:40 AM run — last started Sat Aug 1 7:00 AM
- 'vp-hr-policy-monthly-sync' (cron 35 8 1 * *) missed its Sat Aug 1 8:35 AM run — last started Sat Aug 1 8:07 AM
- 'weekly-social-media-recap' (cron 40 9 * * 1) missed its Mon Aug 17 9:40 AM run — last started Mon Aug 17 9:04 AM
- 'vp-follower-growth-monthly-check' (cron 50 9 * * 1) missed its Mon Aug 17 9:50 AM run — last started Mon Aug 17 9:07 AM
- launchd agent com.valleypawn.claude-keepalive last exited with status 126

## 2026-08-21 13:30 — ISSUES FOUND

- 'weekly-returns-summary' (cron 20 1 * * 1) missed its Mon Aug 17 1:20 AM run — last started Mon Aug 17 1:03 AM
- 'monday-bravo-combined-compile' (cron 0 8 * * 1) missed its Mon Aug 17 8:00 AM run — last started Mon Aug 3 2:15 PM
- 'monthly-capability-drift-audit' (cron 40 7 1 * *) missed its Sat Aug 1 7:40 AM run — last started Sat Aug 1 7:00 AM
- 'vp-hr-policy-monthly-sync' (cron 35 8 1 * *) missed its Sat Aug 1 8:35 AM run — last started Sat Aug 1 8:07 AM
- 'weekly-social-media-recap' (cron 40 9 * * 1) missed its Mon Aug 17 9:40 AM run — last started Mon Aug 17 9:04 AM
- 'vp-follower-growth-monthly-check' (cron 50 9 * * 1) missed its Mon Aug 17 9:50 AM run — last started Mon Aug 17 9:07 AM


## 2026-08-21 13:09 — ISSUES FOUND

- 'monday-bravo-combined-compile' (cron 0 8 * * 1) missed its Mon Aug 17 8:00 AM run — last started Mon Aug 3 2:15 PM



## 2026-08-21 13:09 — ISSUES FOUND

- 'monday-bravo-combined-compile' (cron 0 8 * * 1) missed its Mon Aug 17 8:00 AM run — last started Mon Aug 3 2:15 PM




## 2026-08-21 13:03 — ISSUES FOUND

- 'monday-bravo-combined-compile' (cron 0 8 * * 1) missed its Mon Aug 17 8:00 AM run — last started Mon Aug 3 2:15 PM
- launchd agent com.valleypawn.dashboarddatacollector last exited with status 78
- Claude app is NOT running — scheduled tasks cannot fire (keepalive should restart it)

