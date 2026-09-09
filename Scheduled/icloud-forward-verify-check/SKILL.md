---
name: icloud-forward-verify-check
description: One-time check: confirm the new iCloud->Gmail forwarding rule (zapvp1@me.com -> jdavis@fcfpawn.com) actually delivered the two test emails, then report to Joshua.
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Using the Gmail MCP connector (search_threads) on jdavis@fcfpawn.com, search broadly (in:anywhere, includeTrash true) for subject "iCloud forwarding test" and "iCloud forwarding test 2" sent to zapvp1@me.com around 2026-08-27 12:45-12:50 UTC.

Goal: determine whether Apple's iCloud Mail forwarding rule (Forward my email to: jdavis@fcfpawn.com, set up today in iCloud Mail > Preferences > Forwarding) actually delivered a forwarded copy of either test message into the jdavis@fcfpawn.com Gmail account (inbox, spam, or trash — check all).

Report back in one plain DM to Joshua via Slack (D03BHQH5VGT), no technical jargon per vp-operating-rules Rule 16:
- If a forwarded copy of either test email is now found in Gmail: forwarding is confirmed working, iCloud mail will now flow into Gmail automatically going forward.
- If neither test email has arrived anywhere in Gmail after this ~20+ minute wait: forwarding still isn't actually delivering despite the setting appearing saved and enabled in iCloud's Forwarding panel. Recommend Joshua re-open iCloud Mail > Preferences > Forwarding, toggle the "Forward my email to" checkbox off, save/close, then back on and re-enter jdavis@fcfpawn.com and save again (a fresh save sometimes triggers activation) — then ask to have this checked again. Do not attempt any further computer-use or Chrome automation of iCloud settings in this task — this is a Gmail-side read-only check and Slack DM only.