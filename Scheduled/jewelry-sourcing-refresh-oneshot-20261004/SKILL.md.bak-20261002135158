---
name: jewelry-sourcing-refresh-oneshot-20261004
description: One-shot Sun 10/4 10:00 AM ET, Type A (one trigger via bravo_pull.sh, gate first). Pulls the ONE missing store (Waynesboro) of Bravo's Pawn Activity Summary for 7/16/2026-9/29/2026, verifies all 5 stores' date headers, re-runs the jewelry-sourcing refresh scripts, writes the dated HTML, and DMs Joshua the buy-vs-forfeit split via the fleet outbox. Created 2026-09-30 by the jewelry-sourcing refresh session.
---

You are finishing the Valley Pawn jewelry-sourcing refresh that a 2026-09-30 session started. Work autonomously; accuracy is paramount. Never drive Bravo's screen or Parallels yourself (no computer-use, no prlctl) — the only Bravo contact allowed is ONE host-queue job calling the allow-listed bin/bravo_pull.sh, which runs the pipeline's own health gate first.

FIRST: invoke the skills anthropic-skills:enterprise-map, anthropic-skills:vp-operating-rules and anthropic-skills:bravo-context. Rules 16 and 18 apply: nothing to Slack channels, no failure messages or technical words to anyone, and no partial numbers ever.

Paths (host). If your shell sees the Projects folder under /sessions/*/mnt/Projects, use that for shell commands but ALWAYS write host paths inside outbox envelopes.
- P = /Users/joshuadavis/Documents/Claude/Projects
- Bravo output: P/Bravo Data Extraction/output/
- Analyses folder: P/Life OS/Reminders Execution 2026-09-30/analyses/
- Host queue: P/Valley Pawn OS/fleet/host_queue/   (allow-listed jobs only; one plain command per line)

STEP 1 — What is already on disk. For each store CUL, HAR, LEX, ROA, WAY check Bravo output file 2026-09-29_<STORE>_pawn-activity-summary.csv: it must be > 1 KB and its 3rd line must contain "Reporting Dates:" and "7/16/2026 - 9/29/2026". On 9/30 CUL, HAR, LEX and ROA were verified good; WAY was missing (0-byte file, export hung). Also confirm the baseline files 2026-07-15_<STORE>_pawn-activity-summary.csv exist for all 5 (range 7/16/2025 - 7/15/2026). List every store that is NOT good.

STEP 2 — Pull only the stores that are not good (normally just WAY). Contention check first: run bash "P/Bravo Data Extraction/_bravo_foreground_guard.sh" check. If BUSY, wait 10 minutes and re-check, up to 4 times; if still busy, stop (go to STEP 6 failure path). If CLEAR, write ONE job file P/Valley Pawn OS/fleet/host_queue/20261004-<HHMM>-jewelry-pas-ext-final.sh containing a comment line and, for each missing store, one line exactly like:
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_pull.sh" pawn-activity-summary 2026-07-16..2026-09-29 WAY jewelry-pas-ext-WAY-r4-2026-10-04
(one store per line, never several stores on one line — a 5-store run hung Bravo on 9/30). Write it as a .tmp file then mv to .sh. Poll P/Bravo Data Extraction/results/<id>.result.json every 60 s for up to 45 minutes per store. Then re-check the STEP 1 header test on the CSV itself — a "success" result can still carry the wrong dates (seen 9/30 on LEX: 9/1 instead of 7/16). If a store fails or has the wrong dates, you may try that store ONE more time with a new job (id suffix -r5) only if the guard is CLEAR; never more.

STEP 3 — If all 5 stores are good: in the analyses folder run
PAS_END=2026-09-29 python3 jewelry_sourcing_refresh.py
PAS_END=2026-09-29 python3 build_report_refresh.py
Both scripts assert the date ranges and stop on any mismatch — if either errors, do NOT edit the numbers by hand; go to the failure path. Success produces REMINDERS_ANALYSES_2026-09-30_jewelry-refresh-2026-09-29.html and jewelry_refresh_summary_2026-09-29.json. Do not modify jewelry_sourcing.py, build_report.py or REMINDERS_ANALYSES_2026-09-30.html (the originals stay as they are).

STEP 4 — Read jewelry_refresh_summary_2026-09-29.json and the headline printed by build_report_refresh.py. From it compute (dollars, rounded to whole dollars and whole percents): for 7/16/2025 - 9/29/2026 all 5 stores, jewelry taken in at cost = total.buy_d + total.exp_d, split into counter buys (buy_d) vs forfeited loans (exp_d), and the same split excluding scrap (excl_scrap); for the new stretch only (since_last_pull) the same split; and the 12 months to 7/15/2026 split (old_12mo) for comparison; plus which store relied most and least on forfeits over the full period (by_store: exp_d/(buy_d+exp_d)). Double-check every figure against the JSON before writing it.

STEP 5 — DM Joshua (plain English, no file names, no report names, no mention of Bravo pulls, pipelines or scripts). Write the message to P/Life OS/Reminders Execution 2026-09-30/analyses/jewelry_refresh_dm_2026-10-04.mrkdwn.txt using Slack *bold*, about 5-8 short lines, e.g.:
"*Jewelry: where it comes from — updated through 9/29*" then the full-period split (e.g. "7/16/25–9/29/26: $X of jewelry in at cost — $A (NN%) bought over the counter, $B (NN%) from forfeited loans; without scrap NN% / NN%"), a line for 7/16–9/29/26 alone vs the prior 12 months' share, and the most/least forfeit-reliant store. End with one line saying the full breakdown by store and category is in the updated jewelry report in the reminders folder.
Send it through the fleet outbox exactly as the daily-store-audit-digest task does — do NOT call slack_send_message. Write the envelope P/Valley Pawn OS/fleet/outbox/jewelry-refresh-joshua-<YYYYMMDD-HHMMSS>.json containing
{"channel": "U03BB52MDSA", "file": "/Users/joshuadavis/Documents/Claude/Projects/Life OS/Reminders Execution 2026-09-30/analyses/jewelry_refresh_dm_2026-10-04.mrkdwn.txt"}
Joshua only. No other recipients, no channels. Do not wait for delivery.

STEP 6 — Log and close. Update the row dated 2026-09-30 about "Jewelry sourcing refresh" in P/Life OS/OPEN_ITEMS_REGISTER.md (edit that row's status in place, or add a dated follow-up row directly under it): DONE with the headline split and the HTML file name — or, on the failure path, "still missing Waynesboro 7/16–9/29 pull; nothing sent" plus what was tried. On the failure path send NOTHING to Slack or Joshua (Rule 16); leave the numbers unpublished (Rule 18). Also append one line to P/Valley Pawn OS/CHANGELOG.md is NOT needed; the register row is the record.