# Weekly Phone & Text Review — scheduled-task prompt (Mondays 6:00 AM)

Paste everything below the line into a new task (Scheduled -> New task), schedule "Every Monday 6:00 AM". It must run on THIS Mac (it drives the local Zoom transcription). Built 2026-10-18 from the Sep 28–Oct 18 run (reference folder: Call Analysis/week_2026-09-28/).

---

Weekly Phone & Text Review for Full Circle Finance Inc DBA Valley Pawn (5 VA stores). Owner Joshua asked for this every Monday. Run autonomously. Load enterprise-map first, then vp-operating-rules. Output is for Joshua ONLY (names staff and customers): never post findings to a Slack channel or to staff.

WEEK = the Monday–Sunday just ended (compute with `date`). SINCE=that Monday, UNTIL=that Sunday. Folder: ~/Documents/Claude/Projects/Call Analysis/week_<SINCE>/. Reference run with all scripts: Call Analysis/week_2026-09-28/ — copy make_batches.py, stats.py, aggregate.py, build_pdf.py and replace the folder name week_2026-09-28 with week_<SINCE>.

1) PULL + TRANSCRIBE: drop ~/Documents/Claude/Projects/Valley Pawn OS/fleet/host_queue/<YYYYMMDD>-callweek-<SINCE>.sh with exactly:
#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/call_week_review.py" --since <SINCE> --until <UNTIL> --detach
Poll Call Analysis/week_<SINCE>/status.json until phase = done (~19 calls/min, allow 3 h). Start reading finished days with make_batches.py <first_day> <last_day> <tag>.

2) STATS: stats.py (missed while open, callbacks, never-reached, by store/week). Hours (confirm in valley-pawn-context): CUL/ROA/WAY Mon–Fri 10–6, Sat 10–5; HAR/LEX Mon/Tue/Thu/Fri/Sat 10–6. Ext: 802/805 HAR, 803/806 WAY, 807/804 LEX, 808/810 CUL, 809/812 ROA, 813 Preston.

3) READ EVERY CALL: parallel subagents, ~48 calls each, same JSON schema and policy context as review_*.json in the reference folder (Oct 1 no-hold rule; no cell phones; handguns 21+/long guns 18+; no firearm returns; layaway tiers; hours; account details only to the verified holder). Reviewed count must equal recordings.

4) TEXTS: one read-only subagent audits Chekkit (dashboard.chekkit.io) per store for the week -> chekkit_texts.md; plus fleet/missed_call_text_results.csv.

5) DELIVER: 2–3 page PDF "Phone & Text Review — by Store" in the reference style (numbers table, cross-store themes, per-store issues with one short verbatim quote each, praise, texts, week-over-week change). Verify every number in code; spot-check the 3 most serious quotes in the transcripts. Then write fleet/outbox/weekly-phone-text-review-joshua-<YYYYMMDD-HHMMSS>.json = {"channel":"U03BB52MDSA","file":"<host path to .txt>"}; the .txt is 3–5 plain lines (3 biggest items + where the PDF is). No jargon. If a step failed, deliver what's complete and say plainly what's missing.

6) LOG one dated line in Valley Pawn OS/CHANGELOG.md.
