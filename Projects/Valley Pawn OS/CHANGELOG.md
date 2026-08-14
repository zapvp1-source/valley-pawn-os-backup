# Valley Pawn - Enterprise Changelog

## 2026-08-13 (evening — zoom-voicemail-alert routine run, zero new alerts)

- Routine `zoom-voicemail-alert` run. Zoom admin session confirmed live (Joshua Davis / Full
  Circle Finance Inc), no re-login needed. Used the account-wide Phone System Management → Logs
  → Calls source, filtered From/To both 2026-08-13, page 1 (15 per page, 103 total results today,
  sorted newest-first).
- Top-of-log rows per store exactly matched the stored dedupe cutoffs: Waynesboro (540) 221-6346
  top row Aug 13, 6:31:49 PM (Abandoned) = stored cutoff; Lexington (540) 461-8349 top row Aug 13,
  6:19:44 PM (Voicemail) = stored cutoff; Harrisonburg (540) 574-4500 top row Aug 13, 4:51:42 PM
  (Ring Timeout) = stored cutoff. No pagination needed — log is globally sorted newest-first.
- No new candidate rows for any of the 3 live store lines — no Culpeper/Roanoke numbers appeared.
  Per Step 4, stayed silent — no Slack post made. State file left unchanged (all 3 cutoffs
  already current).

## 2026-08-13 (later still — zoom-voicemail-alert routine run, zero new alerts)

- Routine `zoom-voicemail-alert` run. Zoom admin session confirmed live (Joshua Davis / Full
  Circle Finance Inc), no re-login needed. Used the account-wide Phone System Management → Logs
  → Calls source, filtered From/To both 2026-08-13, page 1 (15 per page, 103 total results today,
  sorted newest-first).
- Newest row overall was Waynesboro Store Queue (540) 221-6346, inbound from (540) 448-3591
  (MIKALA HOLMES) at 6:31:49 PM, Abandoned — this exactly matches the stored dedupe cutoff for
  Waynesboro, confirming nothing new has come in since the prior run. Same check for Lexington
  (top row Aug 13, 2026, 6:19:44 PM, Voicemail) and Harrisonburg (top row Aug 13, 2026, 4:51:42
  PM, Ring Timeout) — both also exactly match their stored cutoffs. No pagination needed since the
  log is globally sorted newest-first and the top entry per store already equals its cutoff.
- No new candidate rows for any of the 3 live store lines (Harrisonburg, Waynesboro, Lexington) —
  no Culpeper/Roanoke numbers appeared. Per the task's Step 4, stayed silent — no Slack post made.
  State file left unchanged (all 3 cutoffs already current).

## 2026-08-13 (~19:50 ET — chekkit-unanswered-eod-followup routine run)

- Rebuilt today's Gmail alert list (6 total): 3 were empty-body/attachment-only alerts (Waynesboro
  x2, Culpeper x1 — Christopher Duncan) and skipped per the empty-body rule; 3 were genuine
  in-hours misses (Tyler Crosby/Waynesboro, Jane Nmn Leap/Harrisonburg, Margaret Olympia/Lexington).
  Culpeper and Roanoke had zero genuine flagged misses today.
- Checked the Chekkit dashboard (`/inbox`, phone-number search, per-location switcher) for each:
  Waynesboro (Tyler Crosby) and Lexington (Margaret Olympia) were both answered by staff later in
  the day. Harrisonburg (Jane Nmn Leap, flagged 11:43 AM re: a late payment) got only an automated
  reply plus an unrelated "👍" reaction to a promo blast — no staff ever addressed her question —
  logged as STILL UNANSWERED at close.
- Posted the EOD summary to #chekkit-unanswered-summary (`C0B1PEW0C30`). No employee DMs sent (not
  this task's job — that's `chekkit-unanswered-alert`, tomorrow 8 AM). No login issues encountered.

## 2026-08-13 (later still, ~19:45 ET — zoom-voicemail-alert routine run, 1 new alert)

- Routine `zoom-voicemail-alert` run. Zoom admin session confirmed live (Joshua Davis / Full
  Circle Finance Inc), no re-login needed. Used the account-wide Phone System Management → Logs
  → Calls source (proven approach from earlier runs today), filtered From/To both 2026-08-13,
  paginated via the "Next page" button (103 total results today) down through and past each
  store's existing dedupe cutoff (HAR 4:51:42 PM, WAY 3:32:23 PM, LEX 6:19:44 PM).
- Confirmed only 3 live Zoom Phone store lines today (Harrisonburg, Waynesboro, Lexington) — no
  Culpeper/Roanoke numbers appeared anywhere in the pull, consistent with recent runs.
- Found 1 new candidate: Waynesboro Store Queue (540) 221-6346, inbound from (540) 448-3591
  (MIKALA HOLMES, Virginia) at 6:31:49 PM, Call Result = Abandoned, Voicemail = -- (no VM left).
  This was the newest row in the entire day's log — no later outbound or inbound row for that
  number exists yet, so it's unresolved. Harrisonburg and Lexington cutoffs re-confirmed exactly
  in today's log with zero new candidate rows past them.
- Posted to #voicemails-calls-missed (`C0BP4M3B99R`): "📞 Waynesboro — (540) 448-3591, 6:31 PM —
  missed (no VM), call back ASAP". State file advanced: Waynesboro cutoff → Aug 13, 2026, 6:31:49
  PM. Harrisonburg and Lexington cutoffs left unchanged (no new candidate rows past their marks).

## 2026-08-13 (later still, ~18:27 ET — zoom-voicemail-alert routine run, 1 new alert)

- Routine `zoom-voicemail-alert` run. Zoom admin session confirmed live (Joshua Davis / Full
  Circle Finance Inc). Used the account-wide Phone System Management → Logs → Calls source
  (same approach adopted earlier today), filtered today, page_size 15, paginated via "Next page"
  through all 3 stores' existing dedupe cutoffs (HAR 4:51:42 PM, WAY 3:32:23 PM, LEX 2:35:18/20
  PM — all three re-confirmed exactly on page 1-3, no pagination-bug shortfall this run).
- Found 1 new candidate: Lexington Store Queue (540) 461-8349, inbound from (540) 251-6656
  (Christiansburg VA) at 6:19:44 PM, Voicemail = Y. Checked for a staff callback or customer
  reconnect — confirmed via a dedicated search-box lookup on the number that this is the only row
  for that caller today (no later outbound or inbound row exists yet). Unresolved → alerted.
- Posted to #voicemails-calls-missed (`C0BP4M3B99R`): "📞 Lexington — (540) 251-6656, 6:19 PM —
  🔴 VM left, call back ASAP". State file advanced: Lexington cutoff → Aug 13, 2026, 6:19:44 PM.
  Harrisonburg and Waynesboro cutoffs left unchanged (no new candidate rows past their marks).

## 2026-08-13 (~19:20 ET — Missed Calls & Voicemails trend report built)

- Built a new trend-reporting pipeline for the Zoom missed-call/voicemail data, at Joshua's
  request, on top of today's `zoom-voicemail-eod-review` findings. Lives under
  `Communcations/Trend Reports/Missed Calls & Voicemails/` (Joshua: "keep this in our trend
  reporting folders" — no such folder existed yet anywhere in the Projects tree, so this
  establishes the convention; `Communcations` was empty before this).
- **`daily_log.csv`** — one row per store per day (`date,store,candidates,resolved,unresolved,
  callback_pct`). Backfilled with 2026-08-13, the first tracked day: Harrisonburg 24 candidates/
  22 resolved (91.7%), Waynesboro 3/2 (66.7%), Lexington 8/3 (37.5%).
- **`generate_report.py`** — reads the CSV, writes a self-contained `report.html` (Chart.js via
  CDN, no build step) with: summary cards per store + overall, daily missed-calls-by-store
  (stacked bar), monthly-by-store (grouped bar), running year-to-date cumulative total (line),
  callback % trend (line, overall + per store), and a full data table. Re-run anytime with
  `python3 generate_report.py` (no args, paths resolve relative to its own folder).
- Wired `zoom-voicemail-eod-review` (Step 5, additive) to append today's per-store tallies to
  `daily_log.csv` and regenerate `report.html` automatically after every daily run, from now on —
  so the trend report grows on its own with zero further manual work. Re-run-safe (replaces
  today's rows instead of duplicating if the task ever fires twice in one day). If this step ever
  fails it DMs Joshua directly rather than touching the Slack close-out post or the ops channel.
- Also folded in a fix discovered while pulling today's backfill data: Zoom's Logs → Calls grid
  can silently disable "Next page" a few rows short of the true total (hit this today — missed
  6 rows, including 2 Lexington voicemails from ~9 AM, until caught by spot-checking numbers via
  the search box). Added a note to `zoom-voicemail-eod-review` Step 2 to watch for this.

## 2026-08-13 (later still, ~18:05 ET — zoom-voicemail-alert routine run, zero new alerts)

- Routine `zoom-voicemail-alert` run. Zoom admin session confirmed live (Joshua Davis / Full
  Circle Finance Inc), no re-login needed. Used the account-wide Phone System Management → Logs
  → Calls source, filtered From/To both 2026-08-13, paginated via the "Next page" button (101
  total results today) down through and past each store's existing dedupe cutoff in
  `.zoom_voicemail_alert_state.json` (HAR 4:51:42 PM, WAY 3:32:23 PM, LEX 2:35:20 PM).
- Confirmed only 3 live Zoom Phone store lines today (Harrisonburg, Waynesboro, Lexington) —
  no Culpeper/Roanoke numbers appeared anywhere in the 101-row pull, consistent with recent runs.
- Found each store's exact existing cutoff row again in today's log (HAR 4:51:42 PM Ring Timeout;
  WAY 3:32:23 PM Abandoned; LEX 2:35:18 PM Abandoned — same known 2-second display-variance event
  as the existing 2:35:20 PM cutoff, not a new call) plus several older candidate rows further
  back (all predating their store's cutoff, already accounted for in prior runs). Zero candidate
  rows found strictly newer than any of the three cutoffs — every inbound row after each cutoff
  was Answered/Connected. No Slack alert posted (correct/expected silent-success behavior). State
  file left unchanged (no new candidate rows to advance the cutoffs to).

## 2026-08-13 (~19:05 ET — zoom-voicemail-eod-review first scheduled run, 7 outstanding)

- First run of the new `zoom-voicemail-eod-review` end-of-day task. Confirmed Zoom admin session
  live (Joshua Davis / Full Circle Finance Inc). Pulled the full day's Calls log via
  Phone System Management → Logs → Calls (account-wide, same source `zoom-voicemail-alert`
  adopted earlier today), filtered to today with the non-Answered/Connected result codes
  (Voicemail, Hang Up, No Answer, Invalid Operation, Abandoned, Blocked, Service Unavailable).
- ⚠️ Found a real pagination bug in Zoom's grid: the "Next page" button silently disables after
  2 pages (30 of 36 rows) even though more rows exist — confirmed by cross-checking individual
  phone numbers via the search box, which surfaced 6 more candidate rows (2 for an already-known
  number, 2 new Lexington voicemails from ~9 AM) that the paginated view never reached. Re-ran
  pagination from a clean URL afterward and it correctly returned all 36/36 on the 3rd page this
  time — the earlier truncation looks like a one-off render glitch rather than a hard cap, but
  **future runs should sanity-check the last page's row count against the "N result(s)" label
  and, if short, spot-check via the search box** rather than trusting a disabled Next button.
  Also confirmed: the per-number search box carries over an active Call Result filter from the
  page it was opened on — must clear the `result=` filter (fresh URL, no result param) before
  using search to check resolution, or Answered/Connected rows won't show.
- 35 inbound missed-call/voicemail candidates across Harrisonburg, Waynesboro, Lexington (no
  Culpeper/Roanoke lines yet). Checked each unique caller number for a same-day staff callback
  (outbound Connected) or customer reconnect (inbound Answered) after the missed call. 28 were
  resolved by end of day; 7 were not:
  Harrisonburg (540) 688-9770 (12:52 PM); Waynesboro (540) 649-0865 (12:59 PM); Lexington
  (540) 808-0737 (2:35 PM), (540) 246-0163 (2:29 PM), (540) 301-6098 (2:26 PM, VM),
  (540) 924-3080 (9:23 AM, VM), (540) 944-5030 (9:04 AM).
- Posted the EOD summary to #voicemails-calls-missed (`C0BP4M3B99R`), one line per outstanding
  item with the caller's number inline, per the task's format spec.

## 2026-08-13 (later still, ~17:48 ET — zoom-voicemail-alert routine run, zero new alerts)

- Routine `zoom-voicemail-alert` run. Followed the account-wide Phone System Management → Logs → Calls
  approach (adapted 2026-08-13 ~14:35 ET, confirmed still the right source given the completed DID
  cutover — Harrisonburg/Waynesboro/Lexington Store Queues are all Active with real numbers per the
  ~17:07 ET entry below), filtered to today, paginated via the "Next page" button through all rows back
  to and including each store's existing dedupe cutoff (HAR 4:51:42 PM, WAY 3:32:23 PM, LEX 2:35:20 PM
  in the state file). Zero candidate (non-Answered/Voicemail=Y) rows found strictly newer than any of the
  three cutoffs — every inbound row in the ~2:35 PM–5:38 PM window was Answered. No Slack alert posted
  (correct/expected silent-success behavior). State file left unchanged (no new candidate rows to advance
  the cutoffs to, consistent with the Step 3 rule of only advancing on candidate rows).
- No Culpeper/Roanoke lines appeared in today's log — still only 3 live Zoom Phone store lines
  (Harrisonburg, Waynesboro, Lexington), matching the ~17:07 ET entry below.

## 2026-08-13 (later still, ~17:10 ET — DID cutover confirmed complete for ALL 3 stores; zoom-voicemail-alert routine run, zero surviving alerts)

- CORRECTED the ~14:35 ET entry above, which said only Lexington's live DID cutover was done and Harrisonburg/Waynesboro queues still showed Number(s) "--". A routine `zoom-voicemail-alert` run at ~17:07 ET checked Phone System Management → Call Queues directly (live admin console, not a run record — Rule 12) and found ALL THREE queues now show real numbers: Harrisonburg Store Queue (540) 574-4500, Waynesboro Store Queue (540) 221-6346, Lexington Store Queue (540) 461-8349, all Active. The account-wide Logs → Calls log for today also shows live inbound traffic landing on all three under a mix of queue labels ("Harrisonburg Store Queue Ext.805" for some rows, but still "harrisonburg@fcfpawn.com Ext.802" for most Harrisonburg rows and "Joshua Davis Ext.800" for some Lexington rows) — routing/labeling is inconsistent mid-cutover but calls ARE reaching stores. Unclear who completed the Harrisonburg/Waynesboro leg or exactly when between ~14:35 ET and ~17:07 ET; flagging so the next session doesn't rely on the ~14:35 ET "only Lexington done" claim.
- The account-wide Logs → Calls approach (adopted ~14:35 ET run) continues to work well and was used again this run — paginated via the "Next page" button (JS `.click()` on `[aria-label="Next page"]`; mouse-wheel scroll did not advance the grid, it's true pagination not infinite scroll) rather than per-user History tabs, to correctly capture all 3 stores regardless of which label a given call landed under.
- This run found ZERO net-new missed-call/voicemail rows across all 3 stores after dedupe + resolution check — no Slack alert posted (correct/expected behavior per the skill's "silent success" design). State file (`Valley Pawn OS/.zoom_voicemail_alert_state.json`) advanced Harrisonburg's cutoff to 4:51:42 PM (two Ring Timeouts from the same wireless caller at 4:50:59/4:51:42 PM, both resolved — the same number reached Harrisonburg successfully at 4:52:32 PM). Waynesboro and Lexington cutoffs left unchanged (no new candidate rows past their existing marks; a 2-second display variance on the Lexington 2:35 PM row between the per-user-History source used earlier today and the account-wide Logs source used now was treated as the same event and not regressed).

## 2026-08-13 (later still, ~14:35 ET — Lexington DID cutover found already live; zoom-voicemail-alert adapted)

- CORRECTED a stale claim from this same day's earlier "Timezone Fix + Call Queue Buildout" entry, which said the live DID cutover to the new per-store Call Queues was "NOT done... held back deliberately." A routine `zoom-voicemail-alert` run at ~14:35 ET found, via the live admin console (not a run record — Rule 12), that Lexington's number **(540) 461-8349 has in fact already been reassigned** from Joshua Davis's user extension (800) to the new **Lexington Store Queue** (ext 804): his user's Number(s) field is now empty, and his Outbound Caller ID shows "Lexington Store Queue - (540) 461-8349" instead. Harrisonburg (queue ext 805) and Waynesboro (queue ext 806) remain **not** cut over — both queues still show Number(s) "--" and both stores' calls still land directly on their user extensions (802/803), consistent with the original note. Only the Lexington leg of the cutover happened; unclear whether by Joshua or an unlogged follow-up action. Flagging so the next session doesn't rely on the stale "not done" claim for Lexington specifically.
- ADAPTED (same run, no code/skill file changed — a live judgment call, not a build): the per-user History-tab approach in `zoom-voicemail-alert`'s Step 2 assumes each store's calls land on one user's History. With Lexington's DID now split between "Lexington Store Queue Ext.804" and "Joshua Davis Ext.800" labels for the same number, the run instead pulled the account-wide **Phone System Management → Logs → Calls** log (filtered to today, matched by the "To" phone number rather than by user identity) to correctly capture both labels as one Lexington line. This worked cleanly and is arguably a more robust source than per-user History going forward, especially once Culpeper/Roanoke and the still-inert Harrisonburg/Waynesboro queues eventually cut over too — worth considering as a deliberate rebuild of that skill's Step 2 in a future session (not done here, scope was a routine 20-min alert check, not a rebuild).

## 2026-08-13 (latest, ~13:15 ET — sold-inventory data-integrity bugs fixed)

- FIXED (Bravo pipeline, data integrity): two bugs in the sold-inventory pull that were silently producing WRONG data. Surfaced by Discount Review's first live run; fixed and proven live the same day.
  1. **Zero-sale days wrote no file.** The empty-grid branch returned `status: success` with an `output_path` but never wrote a CSV, so "this store had no sales" was indistinguishable on disk from "this cell never ran." HAR/LEX/ROA all did exactly this for 2026-08-12.
  2. **Wrong grid captured and reported as real data.** `WriteBuysGridToCsv` enumerates `DataItem`s from the *entire* Bravo UIA root, unscoped. On WAY the report grid was slow and the walk latched onto the Global Access **store picker**, writing a CSV with header `DisplayCode,Store` — 5 rows, one per store — reported as "SUCCESS: 5 data rows." Plausible-looking and completely fabricated. Same failure family as the 2026-07-31 false-zero and 2026-08-03 truncation bugs: a partial/incorrect read presented as a complete result.
- Fix is 100% ADDITIVE (Rule #4): NEW `reports/SoldDiscountDetail.ahk` + NEW cell `sold-discount-detail`, registered by appending one `#Include` and one `REPORT_HANDLERS` line at `bravo_watcher.ahk`'s own "add new ones here" anchors. Verified additive: stripping the two new lines reproduces the backup byte-for-byte (`bravo_watcher.ahk.bak-pre-sold-discount-detail-2026-08-13`).
- **The shared `jewelry-margin-sold` cell / `JewelrySoldMargin.ahk` were deliberately NOT modified** — that handler is co-owned by the jewelry-scrap project, so it gets a coordinated fix rather than a unilateral edit. ⚠️ **Both bugs therefore still exist in `jewelry-margin-sold`; any other consumer of that cell is still exposed.**
- New handler classifies grid IDENTITY before accepting any row, re-checks on every scroll pass, applies a final column check before writing, and writes a header-only CSV on a genuine zero-sale day.
- Proven live (trigger `sold-discount-detail-2026-08-13T13-13-41`, 2026-08-12 data): `status: success` 5/5 stores, vs `partial` with 0 usable stores on the broken path. CUL 20 real rows with correct schema header (valid grid detected in 4s, vs the bogus 172s latch); HAR/LEX/ROA/WAY genuine quiet days each writing a 68-byte header-only CSV; no store-picker garbage anywhere; `missing_stores` empty. Report posted to Joshua's DM: 18 rankable items, avg 13% off ticket, $308 total off, 4 flags, 0 sold into a loss.
- `run_daily_discount_review.py`: new filename pattern added to the FRONT of the existing `_FILENAME_CANDIDATES` list, old patterns kept as fallbacks. Corrupt WAY CSV moved to `output/_quarantine/` so those fallbacks can't resurrect it.
- Caveats for the next session: (a) the identity check has NOT yet fired against a real store-picker collision — the picker never appeared this run, so the reject path is coded but unexercised; watch for `[grid] WARN: found a grid that is NOT the sold-details grid`. (b) A quiet day burns the full 180s render timeout per store (~23 min for 5 stores) — correct but slow; an early-exit "no rows" probe is the obvious optimization. (c) `discount-review` remains UNREGISTERED with the scheduler by design.

## 2026-08-13 (later — markdown verification pipeline built)

- BUILT (additive): new pipeline cell `markdown-verification` — clones the proven Custom-Reports saved-report pattern (InventoryDetails.ahk) into a new `reports/MarkdownVerification.ahk`, registered via a new #Include + REPORT_HANDLERS line in both `bravo_watcher.ahk` and `bravo_export.ahk` (no existing lines touched). Pulls Preston Peters's saved Inventory report "Claude Markdown Verification" (built by Preston 2026-08-10 per Joshua's request — Slack DM D03C7RBGY56) for one store at a time: `Number, Status, Category, Description, Price, Sale Price, Cost, Date` per on-hand item. `Sale Price` populated = item has had its price reduced (marked down) at some point; blank = it has not. Confirmed live 2026-08-13 the report has NO date-range fields — it's a live on-hand snapshot, same shape as Preston's other "Claude Aged Sold" report.
- SMOKE-TESTED live, all 5 stores, 2026-08-13: CUL 241 rows / HAR 246 / LEX 250 / ROA 241 / WAY 239, all `status:"success"`, ~2.5-4.5 min/store (serial, ~20 min total for 5 stores — a Type A trigger-drop cell, watcher-queue-protected). Cross-checked the actual CSV content (Rule 12) with a one-off local age calc (today − Date >= 365d, Sale Price blank/non-blank): CUL 42 aged-and-not-marked-down / HAR 56 / LEX 14 / ROA 73 / WAY 47 — real, plausible per-store spread, not fabricated.
- Watcher restart required a 2-attempt one-shot scheduled task: the first attempt (`markdownver-watcher-restart-oneshot`) was built WITHOUT the LOCAL ACCESS GATE pattern and silently did nothing (matches the documented 2026-08-02 "no Mac bridge" false-conclusion failure mode — a fresh scheduled-task session's osascript tool wasn't loaded yet, and the task's own "exit silently regardless" instruction masked the miss). Retry (`-r2`) added the gate + a diagnostic status-file write (not a Slack post) and succeeded — watcher restarted 10:57:36, confirmed `markdown-verification` in its loaded handler list before any trigger was dropped. **Lesson for future one-shot watcher-restart tasks: always include the LOCAL ACCESS GATE (see monday-bravo-combined-run) even for "simple" infra tasks — the silent-on-failure instruction that's correct for Slack/DM noise also hides this specific failure mode if the gate is missing.**
- BUILT (additive, new Cowork scheduled tasks): `weekly-markdown-verification-pull` (Sun 7:00pm ET — drops the 5-store trigger, does not wait, mirrors the monday-bravo-combined-run/compile 2-task split to avoid a long-poll session-context timeout) and `weekly-markdown-verification-review` (Mon ~9:35am ET — reads the CSVs, computes per-store aged-1yr+-and-not-marked-down items/dollars, posts a plain-language summary to #aged-inventory-review per Field Communication Standard v3, DMs Joshua a trend line and appends to a running history CSV so future DMs can show week-over-week instead of a bare snapshot).
- Direct answer to Joshua's 2026-08-10 ask ("how and where do we look... when was it last marked down"): the "where/how" is now automated (this build). The "when was it last marked down" half is **not answerable yet** — Preston's saved report has a Sale Price field but no last-price-change date field, so the new task can only show CURRENT markdown status, not history/frequency. Flagged honestly to Joshua in the weekly DM rather than guessed at. Logged as an open item — closing it needs Preston to add a date column to the saved report, a request outside this session's Bravo access.
- CORRECTED a stale BUSINESS_OS.md claim found while doing this build: the pipeline handlers table listed `aged-jewelry-markdown`/`AgedJewelryMarkdown.ahk` and `aged-general-merch-markdown`/`AgedGeneralMerchMarkdown.ahk` as "⚠️ Built" — verified via `ls reports/` that neither file exists on disk. Corrected in place rather than left to mislead the next session (Rule 12).

## 2026-08-13

- AUDITED + FIXED: full Zoom Phone admin audit across the 3 live store lines (Harrisonburg, Waynesboro,
  Lexington), prompted by Joshua's request. FIXED live: Harrisonburg and Waynesboro were both defaulting
  to Lexington's address for E911 (125 Walker St) — added and activated correct Personal Emergency
  Addresses for each store (Harrisonburg: 1790 E Market St; Waynesboro: 1321 W Broad St), verified/geocoded
  by Zoom on save. NOT fixed (needs physical action): both of Harrisonburg's Grandstream WP822 handsets
  are Offline with "Factory reset needed for provisioning" — no remote reset option exists in the admin
  console — this is a real, current outage (Harrisonburg has zero working phones) and matches the missed-
  call flood seen in #voicemails-calls-missed on 8/12-8/13. Logged as an open item requiring someone
  in-store to power-cycle/factory-reset both handsets. Also flagged (not fixed, recommendations only): zero
  Call Queues configured account-wide (all 3 stores are plain 2-device user extensions with a 30s max
  wait, no overflow/hold), Lexington's desk phone is flagged End-of-Life by Zoom, Harrisonburg's user
  timezone is wrong (Pacific instead of Eastern), an unused Auto Receptionist (ext 801, no numbers
  assigned) exists. Full detail in `ZOOM_PHONE.md` under "Admin Console Audit — 2026-08-13".
- FIXED + BUILT (same-day follow-up to the audit above, per Joshua's approval): Harrisonburg's and
  Waynesboro's user Time Zone bug fixed (both set to Eastern; root cause was the field being unset and
  silently inheriting the account's Pacific default — actual field lives at User Management > Users >
  [name] > Profile, not the Phone System Management > Users & Rooms Profile tab, which only displays it).
  Built 3 new Call Queues (Lexington ext 804, Harrisonburg ext 805, Waynesboro ext 806), one per store,
  existing user as sole member, Business Hours Mon/Tue/Thu/Fri/Sat 10 AM–6 PM (Wed/Sun off) matching real
  store hours, Zoom's default ring/hold/overflow settings unchanged. This replaces the fragile
  single-user/2-device extension model (no overflow path) that left Harrisonburg with zero fallback during
  its hardware outage. **NOT done: the live cutover** — each store's public phone number still rings its
  old user extension, not the new queue; queues are built and correct but inert until Joshua confirms the
  DID reassignment per store (held back deliberately, customer-facing/live-call risk). Full detail in
  `ZOOM_PHONE.md` under "Timezone Fix + Call Queue Buildout — 2026-08-13"; open item logged in
  `Life OS/OPEN_ITEMS_REGISTER.md`.
- BUILT: promoted Bravo contention/collision checking from a standalone runbook (`BRAVO_HEALTH_RUNBOOK.md` §0, added 2026-08-10) into a MANDATORY, first-read section of the `bravo-context` skill itself, plus a new Step 0 in `bravo-store-cycle` — Joshua flagged that a rule living only in a separate doc wasn't being checked by default when building or scheduling something new. New section also adds a "scheduling-spacing rule" for any future Bravo-touching scheduled task: classify Type A (trigger-drop, queue-protected)/B (reads-only)/C (drives Bravo's screen directly, highest risk), give Type A/C tasks a 45-60 min buffer from each other (worst-case, not happy-path), and prefer Sunday for anything that doesn't need same-day freshness.
- FIXED: `bravo-prestaging-7am` (fires 6:34 AM daily) was found, via a full scheduled-task audit, to force-relaunch (kill + restart) Bravo.exe/dfsvc.exe every morning with ZERO check for an in-flight trigger or foreground-held session — a real, previously-undetected gap that could have killed a mid-transaction GL export (worst case: 1st-of-month `eom-bravo-gl-export` at 6:00 AM, only 34 min before prestaging fires). Patched to check/acquire/release `_bravo_foreground_guard.sh` around the relaunch; if BUSY, it now silently skips the relaunch (Bravo already up = goal already met) instead of pushing through.
- AUDITED (full findings, not yet executed): the 5:30-9:00 AM ET daily/Monday cluster remains genuinely overloaded — see Open Items Register row logged today. Confirmed the trigger-drop queue itself IS safely serialized (atomic `FileMove` claim in `bravo_watcher.ahk`, 45-min hard cap) — collision risk is specifically from direct-screen-driving tasks (`prlctl exec`, computer-use) that bypass that queue, which is exactly the class of gap just closed above. Retiming recommendation delivered to Joshua same session; deliberately not auto-executed (changes when live reports land in Slack).
- FIXED (evening): **`sold-review` was silently exposed to a known data-corruption bug while posting to a team channel.** A prior session today built `sold-discount-detail` / `SoldDiscountDetail.ahk` — an additive clone of `jewelry-margin-sold` fixing (a) zero-sale days writing no CSV at all, so quiet stores were misreported as missing, and (b) grid-capture latching onto the wrong UIA grid, which on 2026-08-13 wrote WAY's Global Access store picker (`DisplayCode,Store`) to disk as 5 rows of "sold inventory." It wired `discount-review` to the fix but left `sold-review` on the old buggy cell. Both now read `sold-discount-detail`. `run_daily_sold_review.py` got the new filename pattern at the front of `_FILENAME_CANDIDATES` (old patterns retained, backup taken, `py_compile` clean, path resolution verified against all 5 real CSVs).
- CONSOLIDATED (evening): `sold-review` and `discount-review` were dropping **byte-identical triggers ~36 minutes apart** — same cell, same stores, same date range — burning two complete 5-store Bravo cycles for one dataset. Both now have a REUSE-FIRST step: check for today's CSVs before dropping anything; whichever runs first pulls, the other reuses. Neither *depends* on the other, so each still works standalone if the other fails.
- SHIPPED (evening, Joshua's request): `discount-review` is now **team-visible** in the new private channel `#discount-review` (`C0BQ6JA27MX`, created by Joshua today) instead of his DM, and every daily post now carries **running calendar-year discount totals by store AND company** alongside the day's numbers, with the Top-10-by-discount-% list kept. YTD is *derived* by re-summing the per-day summary JSONs (excluding the target date, which comes from the live run) rather than kept as an accumulating ledger — so a re-run recomputes instead of double-counting and there's nothing to drift. Every store now renders every day (`no sales today | YTD $X`) so a closed-Wednesday or quiet store doesn't vanish from the board. Failure notices still go to Joshua's DM only, never the team channel.
- CORRECTED + CLOSED (follow-up same session): the earlier audit today mischaracterized `eom-bravo-gl-export` and `monday-bravo-combined-run` as having unguarded computer-use paths. Re-reading their actual current SKILL.md showed both were already substantially hardened by prior sessions: `monday-bravo-combined-run` was moved off Monday morning to Sunday evening 2026-08-10 specifically to avoid this exact contention (no computer-use in its normal path at all), and `eom-bravo-gl-export` was rebuilt 2026-08-02 to be fully scripted via the trigger-pipeline, with computer-use only as a rare hang-recovery fallback inside Step 1. That one remaining fallback path did not check the foreground guard — patched it to check/acquire/release around the recovery sequence, same pattern as `bravo-prestaging-7am`. `ScrapBucketCloseoutWatcher.ahk` (a separate, independent AHK process, historically implicated in a 2026-08-06 collision) remains genuinely outside this guard system — it's a different process entirely, not a Cowork scheduled task, and would need its own fix; flagged as a known residual gap, not closed today.
- OBSERVED (self-recovered, logging for pattern-tracking): today's `daily-items-to-price` run hit two distinct handler-level defects on the first pass, both resolved by a targeted re-trigger without any manual intervention: (1) CUL errored with "BackToDashboard could not return Bravo to Dashboard" (the documented Custom-Reports-editor "loops on Done" gotcha) and produced no CSV; (2) ROA's grid wait hung indefinitely (~10+ min with zero log progress) despite the health gate confirming Bravo itself was running/responsive — root cause not yet identified, first occurrence of this exact pattern; (3) HAR's FIRST attempt wrote a "successful" 5-row CSV that was actually the store-picker lookup table (`DisplayCode,Store` columns) instead of real Price-Items data — same class of defect as the `JewelrySoldMargin.ahk` bug logged for `discount-review` today, but in `ItemsToPrice.ahk`/`bravo_watcher.ahk`'s grid-walk, and it self-corrected on a clean re-trigger (21 real rows, correct headers). None of these were caught by the row-count-only integrity check — HAR's corrupted CSV had a plausible row count (5) that matched its own (wrong) grid's row count, so the seen==maxY check passed. Final report posted was verified by reading actual CSV content, not just row counts. Worth a future look: whether `ItemsToPrice.ahk`'s grid-capture has the same "verify report/view identity before trusting the grid" gap that the Custom Reports pattern already guards against (see `bravo-context`'s "THREE LOAD-BEARING GOTCHAS").

## 2026-08-12

- BUILT: `zoom-voicemail-eod-review` scheduled task — daily 5:45 PM close-out companion to `zoom-voicemail-alert`. Per Joshua: alerts should only fire after checking the call logs for an existing callback (already true of the intraday task since 2026-08-10's Step 3.5), and separately, end of day needs a full re-sweep publishing any missed call/voicemail from that day that still never got a callback. Additive, stateless (does not touch the intraday task's dedupe file), posts to #voicemails-missed-calls every run (list of outstanding items, or an explicit all-clear) since it's meant to be a definitive daily record rather than a silent-when-nothing alert. See `Valley Pawn OS/ZOOM_PHONE.md` for full detail. Note: actual dispatch lands ~5:52 PM due to the scheduler's built-in few-minute jitter, not exactly 5:45 — flagged to Joshua in case exact timing matters.
- CORRECTED: `ZOOM_PHONE.md` still listed the archived Slack channel ID (`C0BND1NK65V`) for #voicemails-missed-calls; updated to the live channel `C0BP4M3B99R` (the `zoom-voicemail-alert` task file itself was already correct — only the reference doc was stale).

## 2026-08-04 (later #4 -- full routing redesign: daily store cadence + decoupled shared accounts)

- Joshua reported (correctly, verified against 3 weeks of live Publer data before acting): store Facebook pages and GBP pages were not posting daily/consistently, while shared Brand Instagram (~11.7/wk) and Brand Twitter (~5.3/wk) were overshooting -- because the OLD routing sent every item, store-local included, to the shared IG and Twitter accounts, while store FB/GBP legs were thin and GBP was conditional on a real deal submission existing that week.
- REDESIGNED `vp-content-batch-weekly` routing (supersedes this same day's earlier 26-item doubling, which only fixed volume not distribution): Brand tier now 7 items/week (1/day), EXCLUSIVELY routes to Brand FB + Brand IG + Brand X -- store-local items no longer touch IG or Twitter at all. Store-local tier now 35 items/week (7/store/day), EXCLUSIVELY routes to that store's FB + that store's GBP, both legs MANDATORY every time (GBP no longer conditional on a deal existing). Total 42 items/week, 91 platform posts/week. Content sourcing for the 6 non-deal slots/store/week now draws from daily-fresh Bravo inventory data -- Bravo freshness is now a daily-strength dependency, not a weekly nice-to-have.
- REWRITTEN `vp-content-batch-quota-watchdog` from an aggregate item-count check to a per-account (Brand FB/IG/X + all 10 store FB/GBP pages) check against live Publer data with explicit from/to date params (avoids the 15-result silent cap). DMs Joshua only for an account with a confirmed 2-consecutive-week shortfall (<4/7). Writes `quota_watchdog_result.json` weekly for the trend comparison.
- OPEN ITEM, not yet re-investigated this session: Culpeper's Facebook page is running ~3x every other store's post count (26 posts vs 7-8 for the others over the same 3-week window) -- previously diagnosed 2026-07-20 as Publer auto-sync pulling in direct-to-FB posts outside the pipeline, not a pipeline bug. Worth a fresh check before the new 1/day/store cadence goes fully live, so pipeline posts don't stack on top of an existing unrelated auto-sync and make Culpeper's page look spammy relative to the other four.
- First live test of the full redesign is Monday 2026-08-10's run.


Newest first. Material changes to the business operating system. Read this BEFORE any build, fix or diagnosis.

## 2026-08-11

- Enabled scheduled tasks: 89 -> 94
- Registered scheduled tasks: 132 -> 100
- Task folders on disk: 153 -> 161
- ENABLED: chekkit-unanswered-eod-followup
- ENABLED: gdrive-cache-refresh
- ENABLED: jewelry-onhand-nightly-compare
- ENABLED: jewelry-onhand-nightly-pull
- ENABLED: task-hygiene-sweep
- FLAGGED: registered-with-scheduler count dropped 132 to 100 (32 tasks) overnight while enabled and folder counts grew normally; no explanation found in changelog history; Joshua notified via Slack DM for review.

A scheduled run of `zoom-voicemail-alert` found the destination channel (`C0BND1NK65V`) returned `is_archived` —
Joshua had archived the original `#voicemails-missed-calls` (renamed `#voicemails-missed-calls-archived`) and
recreated it fresh the same day under a new ID, `C0BP4M3B99R`. Per the task's error-handling policy, did not
guess or fall back to `#general`; ran `slack_search_channels` to confirm a live, non-archived channel by the
same name existed, posted the alert there, then updated the task's own SKILL.md (via
`mcp__scheduled-tasks__update_scheduled_task`) to point at the new channel ID so future runs don't hit the
same failure. Also added an explicit recovery step to the task's ERROR HANDLING section for next time this
happens (channel IDs aren't stable if Joshua recreates a channel).

Substantively, the run found one new unresolved voicemail: Lexington (jdavis@fcfpawn.com / ext 800), caller
(540) 960-1878 at 5:25:05 PM, Ring Timeout with Voicemail=Y, no later outbound callback or inbound reconnect
from that number — posted to Slack and updated `.zoom_voicemail_alert_state.json`. Harrisonburg and Waynesboro
had no new candidate rows this run.

## 2026-08-10 (later) — Fixed zoom-voicemail-alert dedupe (was silently broken since enabled) + added callback verification

Joshua asked whether the task was set up correctly, wasn't re-posting old days, and whether callbacks could be
confirmed from the call log. Investigating turned up two real issues, fixed via `mcp__scheduled-tasks__update_scheduled_task`
(the file-edit path was blocked — see below):

1. **Dedupe state file was never persisting.** The task wrote its `state.json` to
   `~/Documents/Claude/Scheduled/zoom-voicemail-alert/` — that whole tree is mounted READ-ONLY in Cowork
   sessions (confirmed via a blocked `request_cowork_directory` call: "overlaps a protected host location").
   Every run's `Write` on `state.json` (and, discovered separately, on the task's own `SKILL.md`) was failing.
   This had been silently broken since the task was enabled 2026-08-08 — the "first run, no state file yet"
   fallback behavior was masking it, because a failed write looks identical to "file didn't exist." Moved the
   state file to `~/Documents/Claude/Projects/Valley Pawn OS/.zoom_voicemail_alert_state.json` (this project
   folder is writable) and confirmed the write succeeds. **Same-day duplicate posting was never actually a risk**
   — the task already scopes every History pull to From/To = today, so it can't surface a prior day's calls —
   but without persistent state it could have re-posted the same TODAY items every 20 minutes indefinitely.
2. **No callback verification — added Step 3.5.** Before today's fix, every missed/voicemail row was alerted
   on even if the store had already called the customer back. Caught a live example: Waynesboro missed Daniel
   Liptrap ((540) 480-0805) at 10:38:42 AM (Busy) but called him back twice within the same minute, one call
   Connected 1:15 — the alert flagged it anyway. New Step 3.5 cross-references the Outbound rows already
   pulled in Step 2: if there's a later Outbound call to the same number that Connected, the row is
   "callback-confirmed" and excluded from the alert.

**Note for future sessions:** `~/Documents/Claude/Scheduled/<task>/` is read-only to both `Write` and `Edit` in
a Cowork chat session — `mcp__scheduled-tasks__update_scheduled_task` (prompt field) is the correct way to
modify an existing task's SKILL.md; direct file edits will fail there even though `Read` and `list_scheduled_tasks`
work fine. Any task that writes its own state/logs needs that state living under `~/Documents/Claude/Projects/`
(or similar writable path), never under `~/Documents/Claude/Scheduled/`.

## 2026-08-10 (manual entry)
- MOVED: monday-bravo-combined-run off Monday 5:30 AM onto Sunday 6:00 PM ET. Root cause: a manual jewelry-reconciliation pull collided with daily-items-to-price during the Monday-morning Bravo cluster ("FREE1 is busy with Inventory") - the whole 5:30-9:00 AM Monday window is dense with Bravo-touching tasks and stores are closed all day Sunday, so the pull is safer there with zero contention and identical data (nothing happens at any store on Sunday).
- CHANGED: monday-bravo-combined-compile (the Slack-posting half) no longer schedules itself as "now + 90 minutes" relative to the pull. It now fires at a FIXED Monday 8:00 AM ET regardless of when the Sunday pull finished, which is what keeps the 5 ops-channel posts landing at the time the team already expects (previously drifted 7-9 AM depending on Bravo recovery delays that morning).
- RETIMED: monday-bravo-postcheck moved 8:15 AM -> 8:30 AM Monday so it sits safely after the new fixed 8:00 AM compile publish instead of racing it.
- NEW STANDING RULE: BRAVO_HEALTH_RUNBOOK.md section 0 - never touch Bravo (manual trigger or computer-use) without checking triggers/claimed/ and upcoming scheduled fires first; stop and DM Joshua on any conflict. Saved as a persistent memory (feedback_bravo_contention_check) so it loads in future sessions automatically.
- NOT YET MOVED (second wave, flagged not executed): monday-store-rankings (EOM, ~10:30 AM Monday) and the individual weekly canvas-refresh/consumer tasks are single-shot (pull+post combined, not split like combined-run/compile) and would need the same pull/publish split before they can move to Sunday without changing when people see them. Bring a specific list before touching those.


Newest first. Material changes to the business operating system. Read this BEFORE any build, fix or diagnosis.

## 2026-08-10 — Built `chekkit-unanswered-eod-followup` (closed-loop check on the 10-minute miss alert)

Joshua asked whether there was a task confirming that messages flagged as 10-minute unanswered
misses were *eventually* answered — `chekkit-unanswered-alert` (8 AM next-day) only counts misses,
it doesn't verify resolution. Built additive: new scheduled task `chekkit-unanswered-eod-followup`
(7 PM Mon–Sat, after all stores close) rebuilds the same day's flagged-miss list using the identical
skip-list/open-hours rules as the AM task, then logs into the Chekkit dashboard per store to check
each flagged thread for a staff reply. Classifies each as answered-by-staff, self-closed by the
customer (same sign-off skip-list, per Joshua's explicit instruction), or still unanswered at close.
Posts to #chekkit-unanswered-summary — no employee DMs, that stays owned by the AM task.

**Not yet verified:** the exact Chekkit dashboard URL/path for the Messages/Conversations inbox
(only `/reviews` and `/settings/team` are documented from other tasks). First live run will need to
discover and confirm it — see Open Items Register.

## 2026-08-08

- Enabled scheduled tasks: 88 -> 89
- Registered scheduled tasks: 131 -> 132
- Task folders on disk: 152 -> 153
- ENABLED: zoom-voicemail-alert

## 2026-08-07 (latest) — Zoom Phone missed-call/voicemail alert built (same gap as Chekkit missed messages)

Joshua flagged that, just like Chekkit customer messages, Zoom Phone voicemails were going unseen — Zoom
emails a notification to whichever mailbox owns each phone line, but nobody at the stores checks that inbox.
Investigated: no Zoom Phone MCP connector exists (only "Zoom for Claude," meetings-only). Found the fix via
the Zoom admin console instead — Joshua's zoom.us login is Owner/Admin, so every phone user's call
history/voicemail is visible centrally (Phone System Management → Users & Rooms → user → History tab).

**Built (net-new, additive):**
- `Valley Pawn OS/ZOOM_PHONE.md` — extension/line map (Lexington=ext 800/Joshua's own login, Harrisonburg=
  802, Waynesboro=803; Culpeper/Roanoke not yet on Zoom Phone). Discovered Joshua's personal Zoom voicemail
  emails are actually Lexington store calls, not calls to him personally.
- `zoom-voicemail-alert` scheduled task — every 20 min, Mon–Sat 9am–7pm, reads the live Users & Rooms roster
  (auto-picks up Culpeper/Roanoke once added, no edit needed), checks each line's admin History for new
  missed-calls/voicemails, dedupes via a state file, posts one consolidated alert to Slack #general.
- **Known limitation:** no per-store Slack channel exists and the Slack connector has no channel-creation
  tool, so alerts go to #general (all-staff) rather than a dedicated channel. Logged in Open Items Register.

## 2026-08-07 — Open Items Register: the scalable fix, not one tracker per topic

Joshua asked, correctly, whether every future gap requires building a new one-off tracker
(leases, insurance, permits...) or whether there's a way to guarantee broad checking without
that. Building a bespoke file per category doesn't scale — built `Life OS/OPEN_ITEMS_REGISTER.md`
instead: one running log every session must write to (Rule #14, added to `enterprise-map`) the
moment it drafts, sends, or starts anything with a pending follow-up, across all 3 domains.
Future sessions check this ONE file (Step 8.5) before falling back to a full Slack/Drive search.
Seeded with 7 known open items pulled from this session's own history (Culpeper lease renewal,
Bald Rock DocuSign contract fix pending upload, ID verification gap, Harrisonburg FB merge, Apple
Business Connect suite numbers, MapQuest Dixie Pawn legacy listing, Meta Business Verification).
`STORE_LEASES.md` stays as the one exception (high-volume, recurring category) — the register is
the default going forward, not a replacement for it.

## 2026-08-07 (later still) — Store Leases tracker created (gap Joshua caught live)

Joshua asked for the Culpeper lease, got it correctly, but the session then told him a renewal
was needed — even though a renewal notice had already been drafted 2026-07-21. Root cause: lease
work lived only as unindexed Drive files; nothing in BUSINESS_OS.md or enterprise-map pointed a
session at lease status, so "check prior work" only works when the session knows to look.

**Built:** `Valley Pawn OS/STORE_LEASES.md` — per-store lease/renewal status tracker, wired into
`enterprise-map`'s Key Paths (Domain 1). Culpeper populated with what was found (executed lease
2024-03-28, renewal notice drafted 2026-07-21) — **send/landlord-response status is NOT yet
confirmed**, flagged explicitly rather than assumed. Other 4 stores are TODO placeholders — not
yet located in Drive.

## 2026-08-07 (later) — Life Map: enterprise-map expanded to all 3 domains

Joshua flagged that every new session starts blank and never checks known context — true not just
for Valley Pawn (where `enterprise-map` already existed) but for his Real Estate and Personal
domains, which had NO equivalent map at all.

**Built (net-new, additive):**
- `Life OS/LIFE_MAP.md` — top-level index across all 3 of Joshua's domains (Valley Pawn, Real
  Estate, Personal), with explicit cross-domain overlap notes (Bald Rock = FCF Inc money but its
  own operating file; Cypress Crossing = personal money tracked in the Real Estate file for
  property reasons).
- `Life OS/REAL_ESTATE_OS.md` — portfolio table (282 Bald Rock Road, 844 Cypress Crossing Trail,
  prospective Jacksonville/St. Augustine acquisitions), acquisition history, capital-improvement
  evidence-log pointers, cost-seg pointers.
- `Life OS/PERSONAL_OS.md` — Joshua's health (Health Optimization folder), personal finance (QBO
  account boundaries, CPA scope unconfirmed for personal returns), family (Hillary Davis).
- Skills: `real-estate-context` and `personal-life-context` created (mirroring
  `valley-pawn-context`'s pattern); `enterprise-map` updated (overwrite) to be domain-agnostic —
  its trigger and load protocol now route to whichever of the 3 domain OS files is relevant,
  instead of assuming Valley Pawn.

**Known limitation, told to Joshua directly:** skill-triggering is probabilistic (based on
description matching), not guaranteed. `enterprise-map`'s description is written as aggressively
as possible, but the only deterministic fix is a line in Joshua's global Cowork instructions
(outside this session's write access) telling every session to invoke `enterprise-map` first,
unconditionally. Flagged for Joshua to add himself — see chat response 2026-08-07.

## 2026-08-07

- BALD ROCK: Found contract-vs-reality bug — DocuSign "Airbnb Rental Contract" and "VRBO Contract" templates (clause 18) told guests to bring their own pool towels ("we do not permit bath towels or linens to be taken from the property"), directly contradicting the Bald Rock Guest Guide, which already tells guests towels are in the laundry room. Confirmed via the exact live template source PDF in Drive (folder matches DocuSign's 2026-05-24 last-modified date), not the stale 2025-09-29 copy. Bundled in two other known bugs from Joshua's own 2026-06-08 Listing Consistency Review that were still unfixed: check-in time said 3:00 PM in the contract vs. 4:00 PM on every platform, and the minimum-stay clause self-contradicted ("three (2) nights").
- FIXED (files staged, not yet live): surgical in-place PDF text edits (redaction + same-font reinsertion, page/line layout otherwise untouched so DocuSign's existing initial/signature tab coordinates stay valid) producing `Airbnb_Rental_Contract_CORRECTED_2026-08-07.pdf` and `VRBO_Rental_Contract_CORRECTED_2026-08-07.pdf` in `Short Term Rental Optimization/`. NOT yet uploaded to the live DocuSign templates (`cf0bdcb8-4476-4d69-a88c-ba6b605a6034` / `c264e23c-5ff7-47eb-b676-fc469048f331`) — DocuSign web UI has no document-replace API, and the account (zapvp1@me.com) is passkey-only with no saved Chrome password, so browser login needs Joshua's physical Touch ID once. Genuine blocker, not a judgment call.
- FLAGGED, NOT YET BUILT: listing already advertises "Minimum age 30 (ID verified)" on Airbnb/VRBO and in the contract, but nothing currently verifies ID. DocuSign ID Verification (IDV) is the natural fit (metered add-on, ~$2.50+/verification) but needs the same DocuSign UI access to turn on per-template recipient authentication. Also blocked on the login above.

- Enabled scheduled tasks: 87 -> 88
- Registered scheduled tasks: 130 -> 131
- Task folders on disk: 151 -> 152
- ENABLED: vp-follower-growth-monthly-check

## 2026-08-06

- Enabled scheduled tasks: 85 -> 87
- Registered scheduled tasks: 127 -> 130
- Task folders on disk: 148 -> 151
- ENABLED: backup-health-watchdog
- ENABLED: vp-gusto-signature-chase
- Native agent appeared: com.valleypawn.unified-search-refresh.plist
- Native agent LOADED: com.valleypawn.unified-search-refresh
- FLAG (daily refresh): the new nightly background job com.valleypawn.unified-search-refresh (created 2026-08-05 09:14, runs 3:30 AM, rebuilds the Unified Search index) is not explained by any prior CHANGELOG entry. Benign on inspection; logged here so the map stays honest. Joshua notified.

## 2026-08-05 (HR) — two policies found announced-but-never-sent in Gusto; both distributed; weekly chase built
- DUPLICATE DEFECT FOUND + GUARDED: a SECOND Gold Scrap Bucket Naming template (7893330, created 06:17:57 PT) appeared 17 min after 7893283 (06:00:29) and was also sent — all 14 employees were asked to sign the identical one-pager twice. Not created by this session; two actors created and sent the same policy without seeing each other. Two live templates for one policy is a defective HR record (cannot prove which version an employee agreed to) and Gusto exposes NO delete/archive via API, so retiring one is a manual UI click. Joshua must pick the record copy: 7893283 vs 7893330, and 6984272 (approved, 11 signed) vs 6984265 (prepared) for Overtime Policy. GUARDS ADDED: (1) DELTA patch now has a DUPLICATE GUARD run before create AND again immediately before send, using a normalised title match that strips parentheticals/version tags/filler so near-titles collide; (2) vp-gusto-signature-chase gained LIST C duplicate detection, collapses dupes to one line in the Slack post, and leads Joshua DM with any NEW duplicate group.
- SCHEDULE + SCOPE (Joshua, same day): recurring chase moved to Mondays 09:05; added one-shot task vp-gusto-signature-chase-firstrun firing 2026-08-06 09:00 so the first reminder lands tomorrow rather than waiting for Monday. Joshua (2f2d61c5-f19e-4d8e-9e4c-d7d6b62f93d6) and Hillary Davis (94fa77de-beeb-4779-b669-4df93199bd05) are now excluded by UUID from BOTH the Slack post and the DM totals, per Joshua. Both tasks pinned model sonnet.

- AUDIT: pulled every Gusto document template via the read-only internal API from a logged-in Chrome tab (`/api/companies/15bc2823-564f-4c1a-8464-9b0e7d79d3e8/document_templates` → `statistics.{signed,unsigned}_request_count`, and `/api/document_templates/<id>/requests` → per-recipient `status` + `target_id`). `target_id` is the Gusto employee UUID and joins directly to `list_employees`. No computer-use, no screenshots, no cookie extraction — the logged-in session is sufficient. Gusto's MCP connector does NOT expose documents; this is the only working path.
- FOUND: **two policies were announced to the whole team in Slack but were sitting in Gusto unsent, with zero recipients.** "eBay Listing-Age Standard (Reprice & Pull)" (template 7723704) was announced 2026-07-04 with the words *"the formal one-page policy is being sent to each of you in Gusto"* and had sat at `mapping_complete` for **31 days**. "Gold Scrap Bucket Naming Standard" (template 7893283) was announced 2026-08-04 and sat at `prepared`. Neither had a single recipient.
- FIXED: both sent as Team documents to Current team members + All future hires. Verified against output (Rule 12), not the send button: 7723704 → `approved`, 14 requests, all `requested`. 7893283 → `approved`, `approved_at` 2026-08-05T06:28:57-07:00, 14 requests, all `requested`. 14 matches the active roster (`list_employees terminated:false`). For 7893283 the signature/full-name/signing-date fields had to be mapped first — measured from the source PDF (US Letter 612×792, signature underscore at y=330, x=60) and placed at (62,323)/(209,322)/(451,323).
- STILL STUCK (needs Joshua's call, not auto-fixable): template 7455446 "ROC - Late to work" (`prepared` since 2026-05-18 — a disciplinary doc that should be an *Individual* document, never Team) and 6984265 "Overtime Policy" (`prepared`, duplicate of 6984272 which is `approved` with 11 signed).
- NEW TASK: `vp-gusto-signature-chase`, Mondays 08:49, model pinned `sonnet`. Posts an employee reminder naming who owes which policy to #policy-announcements (C03BHQ9RLR0), and DMs Joshua (D03BHQH5VGT) any template created-but-never-sent plus his own unsigned list. Terminated employees are filtered out; Joshua is excluded from the public post. Logged-out Gusto → one plain DM and stop, never a partial post to a team channel (Failure Alert Policy v2).
- NOTE: raw `unsigned_request_count` overcounts — terminated employees retain open signature requests forever. Company-wide raw total is 69; the real active-employee figure is far lower. Any report must filter on `terminated_at`.
- ADDITIVE: touches nothing existing. `vp-hr-policy-monthly-sync` (syncs Slack policies into the P&P doc) and `vp-hr-compliance-quarterly-review` (legal review) both remain untouched — neither has ever checked whether anyone actually signed. No overlap. There is no `#human-resources` Slack channel; `#policy-announcements` is the HR-facing channel.
- STAGED FOR JOSHUA: `~/Documents/Claude/Projects/Human Resources/policy-lifecycle_DELTA_2026-08-05.md` — patches the `policy-lifecycle` skill to send in Gusto BEFORE announcing in Slack, and adds a hard send gate (`processing_state === "approved"` + request count == active roster) that blocks the Slack post if distribution didn't happen. Apply in Settings → Capabilities; skills are not editable from a session.

## 2026-08-05

- Enabled scheduled tasks: 82 -> 85
- Registered scheduled tasks: 125 -> 127
- Task folders on disk: 145 -> 148
- ENABLED: eom-bravo-gl-export
- ENABLED: vp-content-batch-quota-watchdog
- ENABLED: weekly-social-media-recap

## 2026-08-04 (later #10) — real bug found in scrap_rankings.py itself: cross-year bucket-name collisions were silently merging records
- While double-checking the #9 HAR pull, caught a second, more serious problem: the pull orchestrator's `ResetOutputFile` step had wiped `output/2025_HAR_scrap-refining-gold.csv` back to just the 12 newly-pulled Feb-Apr rows, silently discarding the previously-recovered Jan/May-Dec 2025 data (10 months). Recovered it from a local Time Machine snapshot taken at 13:56 today (after the #6 fabricated-row cleanup, before the live pull's reset) and merged it back in. Also recovered a genuine independent weight for "APRIL GOLD W/ STONES" (24.5776438437885 dwt) that the live pull had failed to read, confirming (not just assuming) the two overlapping buckets between the recovered snapshot and the live pull match exactly (Jan and April W/O Stones both matched to 13+ significant figures).
- WHILE FIXING THAT, found the actual root cause of the #9 "suspicious matching weight" anomaly: `load_raw()` in `scrap_rankings.py` keys buckets by `(store, bucket_name)` only. Harrisonburg reuses bucket names across calendar years with no year in the name, so a 2025 bucket and a 2026 bucket sharing a name ("FEBRUARY GOLD W/ STONES", etc.) were being silently merged into ONE record — a blank/unverified weight in the 2025 file was getting quietly backfilled from the 2026 file's same-named bucket. This is the exact fabricated-duplicate bug from entry #6, reproduced at the aggregation layer instead of the pull layer — nulling the suspect weight in the CSV didn't actually fix anything, because the build step was re-merging it right back in.
- FIXED: `load_raw()`'s key is now `(store, bucket, source_file_year)`, using the year prefix already present in each raw filename (`2025_HAR...`, `2026_HAR...`). This can never silently merge two different years' buckets again, regardless of naming. Re-running `build()` after the fix bumped total buckets from 173 to 179 and missing-weight from 15 to 20 — the +6 buckets are previously-hidden real records (2025 and 2026 versions of the same name, now correctly counted as two), and Waynesboro turned out to have one historical name collision too ("GOLD STONE 4/26"), not just Harrisonburg. Culpeper's 2026 YTD also moved (1127→1241 dwt) from the same unmerging — no new CUL gap opened, previously-suppressed real weight is now correctly counted.
- HAR's TRUE remaining 2025 gap, now cleanly isolated: exactly 2 collection periods (February and March 2025 collection, posted as periods 2025-03 and 2025-04) have zero verified weight — every bucket that would cover those two periods either failed to read during the live pull or was the still-unverified suspicious-weight case, and neither has an independent backup source. Every other HAR 2025 month (Jan, Apr collection→May posted, May-Dec) is confirmed. `incomplete_prior_stores` still correctly shows only `['HAR']`, now for the right, narrow reason.
- Rebuilt `scrap_history.csv` (179 buckets) and refreshed the trend workbook with the corrected data.
- REMAINING: HAR's Feb/March-2025-collection weight (2 buckets, periods 2025-03/2025-04) is still genuinely missing — would need a careful live re-pull of just those 2 specific bucket instances, verified by screenshot rather than trusting an automated read, to close the last gap and lift the company-wide YoY hold entirely.

## 2026-08-04 (later #9) — HAR 2025 backfill closed out; occurrence-counter fix confirmed live; YTD correction posted
- Live-tested the `ScrapRefiningGold.ahk` occurrence-counter fix from entry #6 by running `bravo_pull_complete.sh scrap-refining-gold 2025-02..2025-04 HAR`. Confirmed working: the newly-pulled Jan/Feb/Mar/Apr 2025 rows have CreatedOn dates genuinely in 2025 (2/3/25, 3/4/25, 4/3/25, 4/28/25), distinct from the 2026 buckets of the same name (1/28/26, 3/2/26, 4/7/26). HAR's real 2025 gap is now filled for Jan, Feb, Mar, Apr.
- FOUND A SECOND ANOMALY before trusting the new data: 2 of the 8 newly-pulled buckets (FEBRUARY GOLD W/ STONES, MARCH GOLD W/O STONES) carry a weight value byte-identical (13-15 significant figures) to their 2026 counterpart, despite having distinct CreatedOn/StatusDate timestamps — the same red-flag signature as the #6 fabricated-row bug, just partial this time (metadata correct, weight field suspect, likely a stale-read on the weight field after a same-named bucket was opened earlier in the same run). Rather than trust an unverified match, blanked those 2 weight values out (treated as missing, same as any other unread bucket) instead of folding a possibly-wrong number into the history. Live verification (opening those 2 specific 2025 buckets fresh in Bravo to confirm the true weight) is still outstanding — not blocking, since the value is excluded from totals until confirmed either way.
- Orchestrator ran 4 rounds (r1-r4) for this single pull — each round's AHK handler actually succeeded, but the orchestrator's internal ~11min timeout kept firing the next round before the result landed, wasting ~50 minutes of redundant re-pulls (each one correctly re-truncates and re-writes the same 12 rows via `ResetOutputFile`, so no data damage, just wasted time). Confirmed clean afterward: no orchestrator process left running, no stuck/claimed triggers. The timeout-vs-actual-duration mismatch in `bravo_pull_complete.sh` is a real bug worth tightening (round timeout is shorter than this handler's real ~15-20min runtime for a full-grid HAR walk) but wasn't fixed this pass — flagging for later.
- Rebuilt `scrap_history.csv`: 157 buckets, 3 unresolved, 16 missing weight (up slightly from 15 — includes the 2 newly-blanked HAR values plus a pre-existing, unrelated gap: CUL/LEX/ROA/WAY each have 1-3 buckets across Feb-June 2026 that were never successfully weight-read by prior pulls, unchanged by today's work). `incomplete_prior_stores` now correctly shows only `['HAR']` — down from flagging all-or-nothing before the #5 fix, HAR is now excluded from company-wide YoY/YTD only because of the 2 still-unverified weight values, not a wholesale data hole.
- July's per-store monthly figures matched the already-posted correction exactly (555 dwt company-wide, same medal order/percentages) — no change needed there. YTD moved from the posted 3,300 dwt to 2,933 dwt after the corrupted-file recovery + duplicate-weight removal settled; posted a follow-up correction to #scrap-rankings with the tightened number, threaded under the original correction rather than a new top-level post.
- Refreshed `Trends/Valley Pawn - Gold Scrap Trend.xlsx` (18 posted months, 5 stores, 2025-2026) with the final data.
- REMAINING: verify the 2 blanked HAR weights live in Bravo (or accept them as permanently missing/re-pull), and separately, the pre-existing 16-bucket missing-weight gap across all 5 stores (Feb-June 2026, unrelated to HAR) would be worth a dedicated cross-store re-pull pass at some point — not urgent, doesn't affect any currently-posted numbers since missing-weight buckets are cleanly excluded rather than zero'd.

## 2026-08-04 (later #8) — 2026 Bravo GL now fully month-by-month, all 5 stores, Jan-Jul. DONE.
- FINISHED the Q1 lump-JE fix: reversed BRAVO-CUL-Q1-2026 and BRAVO-WAY-Q1-2026 (the last 2 stores) and posted 6 more classed monthly JEs (CUL + WAY x Jan/Feb/Mar). Combined with the earlier HAR/LEX/ROA batch: all 5 Q1 lump entries reversed, 15 classed monthly JEs posted, plus July's 5 posted earlier today.
- REDATED all 5 `BRAVO-{STORE}-Q1-2026R` reversals from QBO's 4/1/2026 default to 3/31/2026. This was the missing piece — a reversal dated into the following month leaves the correction in a different period than the error, which had March overstated ~$1.43M and April at roughly -$707K. Correcting entries belong in the period of the error. Date-only change; no amounts, accounts, classes, or descriptions touched.
- VERIFIED INDEPENDENTLY via a direct QBO P&L pull (Rule 12 — not just the posting agent's self-report). Every month Jan-Jul 2026 now lands in a normal band:
  | Month | Income | COGS | Gross Profit |
  |---|---|---|---|
  | Jan | $354,138 | $125,422 | $228,716 |
  | Feb | $340,332 | $111,506 | $228,826 |
  | Mar | $380,033 | $137,215 | $242,818 |
  | Apr | $338,680 | $114,481 | $224,200 |
  | May | $298,339 | $109,611 | $188,728 |
  | Jun | $364,326 | $135,037 | $229,289 |
  | Jul | $331,099 | $114,792 | $216,307 |
  YTD income $2,407,295 / gross profit $1,559,232. No month is an outlier; the March spike and April hole are both gone.
- BRAVO ACCESS LESSON (this cost real time — do not repeat): when Bravo isn't running, the answer is `bash bravo_ensure_healthy.sh <STORE>` from the Bravo Data Extraction folder — the canonical single-flight health gate that handles launch + recovery. Do NOT hand-roll prlctl/ClickOnce launches or conclude "the VM is unresponsive" and stop. Also confirmed again: multi-store GL triggers wedge on EnsureStore — **fire ONE STORE PER TRIGGER** for post-to-accounting-gl, same rule already documented for scrap pulls. CUL and WAY January both succeeded first try once run singly, after 4 prior multi-store retries had failed.
- Reversal class behavior: ROA and WAY reversals are unclassed because their originals were unclassed (QBO mirrors the source entry); CUL/HAR/LEX reversals carry their class. Both correct — reversal nets the original at whatever class level the original used. QBO's "Save without class values?" prompt on ROA/WAY is expected, not an error.
- Minor pre-existing oddities noticed in the Income section, NOT introduced by this work and not addressed: a "Sales (deleted)" row netting to -0.00 across the period (-$19,315.74 May / +$18,024.17 Feb), a "Service/Fee Income (deleted)" row netting 0.00, $6.00 Uncategorized Income in March, $1.00 PayPal Sales in Feb. Immaterial to monthly totals; worth a separate cleanup pass.

## 2026-08-04 (later #7) — Q1 lump-JE fix executed for HAR/LEX/ROA; CUL/WAY blocked on Bravo VM instability
- Reversed BRAVO-HAR-Q1-2026, BRAVO-LEX-Q1-2026, BRAVO-ROA-Q1-2026 (QBO's Reverse action, not delete/void) and posted 9 new classed monthly JEs (BRAVO-{HAR,LEX,ROA}-2026-{01,02,03}) matching the Apr-Jul convention, from real Bravo GL pulls. Independently re-verified via a direct QBO P&L pull (not just trusting the posting agent's report, per Rule 12): Jan income $182,725.20, Feb $192,530.51, Mar $1,253,460.29 — ties to the agent's numbers within rounding.
- CAUGHT MID-FIX: the posting agent accidentally ran QBO's "Reverse" action twice per store (QBO gives no visible signal on the original JE that it's already been reversed), creating 3 duplicate reversal entries that would have double-subtracted revenue. Self-caught via Advanced Transactions Search cross-check, all 3 duplicates deleted, confirmed exactly 2 entries per store remain (original + one reversal). Independently confirmed via P&L math: Jan's $182,725.20 lines up with HAR+LEX+ROA's real Jan revenue (~$179,930) plus a small pre-existing stray income item — if a duplicate had survived, Jan would show ~$362K instead. No duplication in the books.
- KNOWN COSMETIC ARTIFACT: QBO's Reverse action always dates the offsetting entry the 1st of the FOLLOWING month (4/1/2026, not 3/31/2026) — not editable without hand-backdating, which we deliberately did not do. Net effect: April 2026's P&L will show an artificially low/negative Total Income (-$220,013.51) until viewed together with March, because March still carries the full original lump entry's income and April carries the offsetting reversal. Jan-Apr combined is correct at any time; a April-only report pulled by anyone (bank, accountant) before this is understood could look alarming. Flagging for awareness — not a books error, self-resolves once understood, no further action planned unless Joshua wants the reversal manually backdated instead.
- CUL and WAY's Q1 lump JEs (BRAVO-CUL-Q1-2026, BRAVO-WAY-Q1-2026) deliberately NOT touched this pass — their January Consolidated GL pull failed repeatedly (4 retries + a full watcher/Bravo relaunch via `_relaunch_bravo_and_watcher.ps1`, all still hit `Skipped by safety rail: bravo-not-ready (could not reach a logged-in dashboard)`). This is a live Bravo/Parallels VM instability, not a data or automation-logic problem — needs a hands-on look at the VM (screenshot showed it sitting at the bare Windows desktop, Bravo not even open) before retrying blindly again. Until fixed, CUL/WAY stay on their original Q1 lump JEs (correct, safe state — no partial/broken postings).
- Feb 2026 Consolidated GL pulled cleanly for all 5 stores same session (including CUL/WAY) — only the January pull is affected by the VM issue, isolating the blocker to a specific window/state rather than Bravo being universally down.

## 2026-08-04 (later #6) — HAR bucket-name-collision: root cause nailed down, handler bug fixed, gap narrowed to 2 months
- Joshua explained the actual mechanism: on HAR's live Scrap Refining screen, buckets are listed with the newest at the top; when a month NAME repeats further down the scroll, that repeat is the same month from a PRIOR year (HAR names buckets without a year, e.g. "FEBRUARY GOLD W/ STONES" every year). They're renaming buckets to include the year going forward (per the naming-standard post already sent) — this is only a historical-cleanup problem.
- VERIFIED by comparing exact weights: the "2025" HAR file's Feb entries (33.8449667251456 / 42.2) and March-W/O-STONES entry (131.376851461674) are byte-for-byte identical to confirmed-2026 buckets (CreatedOn 3/2/2026 and 4/7/2026 respectively) — those 4 rows were the SAME 2026 record mislabeled as 2025, not real prior-year data. Removed them from `output/2025_HAR_scrap-refining-gold.csv` rather than let fabricated numbers sit in the history. Jan and Apr-Dec 2025 checked the same way and are NOT collisions (different names and/or different weights than anything in the 2026 file) — confirmed genuine. Net effect: HAR's real 2025 gap is exactly 2 months (Feb, Mar collection → periods 2025-03, 2025-04), not the whole year.
- FOUND THE MECHANISM in `reports/ScrapRefiningGold.ahk`'s `ScrapWalkBucketGrid`: when a bucket row's grid position ("Row N of TOTAL") isn't captured, it falls back to deduping by bare bucket name — for a store that reuses names across years, that silently drops every occurrence after the first. Since the grid sorts newest-first, the survivor is always the CURRENT year's bucket and the prior year's identically-named bucket is discarded before it's ever compared against any date window. `ScrapRelocateAndOpenBucket` (the per-bucket weight-read step) had the same blind spot — matches by name only, so even if two same-named candidates were both identified, opening "the older one" would always re-open the newer one instead.
- FIXED (backup at `reports/ScrapRefiningGold.ahk.bak-pre-dupname-fix-20260804`): the name-fallback dedup key now includes a per-name occurrence counter (reset per store pull, not leaked across the watcher's long-running process) so every same-named row survives as its own entry instead of colliding. `ScrapOpenBucketAndReadWeight` / `ScrapRelocateAndOpenBucket` now take an `occurrence` parameter and skip that many matches before opening, so the correct (older) instance actually gets opened when that's the one requested. NOT live-tested yet (Bravo is down) — verify on the next real HAR pull before trusting it fully.
- Caveat for the record: it's not fully confirmed this fallback path is even what HAR's real 2025-02/2025-03 gap runs through — the modern 7-column handler normally captures rows via the "Row N of TOTAL" path, which is already positionally unique and shouldn't collide by name. The old 4-column "2025_HAR" file this session found was very likely produced by an earlier, simpler tool (predates this handler's CreatedOn/Status capture), not this code path. The fix is shipped anyway as a real, confirmed bug in the fallback path (defends any store, not just HAR) — but the actual fix for HAR's 2 missing months is simply a clean live pull once Bravo is back up, scoped to `2025-02..2025-04`.
- `scrap_rankings.py build` re-run after removing the bad rows: 173 buckets, 117 posted / 34+22 LOW-CONF, 15 missing-weight, 3 unresolved. HAR now correctly shows a real 2-month gap (2025-03, 2025-04 periods) instead of fake data. `incomplete_prior_stores` in `report()` still correctly flags HAR until those 2 months are filled.
- NEXT: the moment Bravo is back up, run `bash bravo_pull_complete.sh scrap-refining-gold 2025-02..2025-04 HAR` (small, targeted, not a full-year retry) and rebuild.

## 2026-08-04 (later #5) — scrap rankings: found + fixed a real inflated-YoY bug, recovered lost 2025/2026 history, corrected the public post
- Joshua correctly called out that the July post's "+84%" / "31% ahead YTD" figures couldn't be trusted while HAR/LEX 2025 data was known incomplete. He was right — root-caused and fixed it, not just re-explained the gap.
- FOUND: today's earlier backfill attempts (this session's `bravo_pull_complete.sh` runs, ~09:30-10:20) didn't just fail — several partially wrote, silently TRUNCATING the previously-good `2026_CUL/HAR/LEX/ROA_scrap-refining-gold.csv` raw files down to a few hundred bytes each before Bravo wedged mid-write. This erased real June/July 2026 data for 4 of 5 stores that `scrap_rankings.py build` had correctly captured this morning. Also found LEX's and HAR's full-year 2025 raw exports (24 and 23 buckets respectively) existed on disk as of last night/this morning but had been silently overwritten to near-empty by earlier pull attempts before this session even started.
- RECOVERED all of it from local Time Machine snapshots (mounted `/System/Volumes/Data` at `com.apple.TimeMachine.2026-08-03-234919.local` for HAR's full 2025 file, `...-085353.local` for LEX 2025 and the 4 corrupted 2026 files) — no data was permanently lost. Corrupted/partial versions kept alongside as `.corrupted-20260804` / `.partial-20260804` for audit trail, excluded from the build glob.
- `scrap_rankings.py build` now resolves 173 buckets (117 posted, 34+22 LOW-CONF name-derived) vs 106 right before this fix and 132 at this morning's high point.
- FOUND A SEPARATE LATENT BUG while recovering HAR: HAR names scrap buckets without a year ("FEBRUARY GOLD W/ STONES", "MARCH GOLD W/O STONES", etc. — no 2025/2026 marker), unlike every other store. The canonical `(Store, BucketName)` dedup key silently merges same-named buckets across different years for HAR specifically, so a handful of HAR's true 2025 months (Mar, Apr) are still not distinguishable from same-named 2026 buckets and remain unresolved. This is a genuine open data-quality issue, not a pull failure — fixing it for real requires either HAR staff including the year in bucket names going forward (recommend folding into the naming-standard Slack post already sent) or capturing authoritative CreatedOn/StatusDate on every pull so the date, not the name, disambiguates.
- CODE FIX (the actual bug Joshua flagged): added `year_covered()` / `genesis_period()` gates to `report()` in `scrap_rankings.py`. Company-wide YoY and YTD percentages are now only computed when EVERY store has unbroken monthly coverage back to the data's genesis month (2025-02, the real start of tracking) — previously a store missing most of a year silently contributed ~0 to the prior-year denominator, inflating the company-wide % growth number. Per-store lines already omitted correctly when that one store's own prior value was missing; this fix closes the aggregate-level gap. HAR is currently the only store still flagged incomplete (per the naming-collision issue above) — its own line and the company total both correctly show no % until resolved.
- CORRECTED the public record: posted a follow-up to #scrap-rankings retracting the "+84%"/"31% ahead" figures from Monday's kickoff post and replacing them with honest numbers (CUL +56%, ROA +63%, LEX +144% — now computable since LEX's real 2025 got recovered —, WAY -14%, HAR comparison withheld, YTD 3,300 dwt with no company-wide % claimed). Message: https://valleypawnworkspace.slack.com/archives/C05EHBH4G67/p1785858865756649
- `scrap_trend_sheet.py` NOT yet re-run against this newest history — do that before relying on the Trends workbook for anything beyond what's already in Slack.
- REMAINING: HAR's Mar/Apr 2025 naming collision (see above); Bravo itself was still down/unresponsive as of this fix (see the (later) entry below) so no further live re-pulls were attempted this pass — everything above came from recovering data that already existed on disk, not from a new Bravo pull.

## 2026-08-04 (later #4) — CORRECTION: July Bravo GL JE posted; Jan/Feb GL pulled; Q1 lump-JE misallocation found
- CORRECTION to the "DID NOT post a QBO journal entry" line further below (2026-08-04 later, Step 5 note): that was wrong. Joshua corrected it directly — 2026 books are bank-feed-only for EXPENSES; revenue/COGS/other GL lines from the Bravo Consolidated GL MUST still be posted via JE (this was always the intended exception per `project_2026_books_cleanup` memory, which explicitly lists "Bravo GL revenue imports" alongside Gusto payroll as the two allowed JE types — the earlier entry misread that memory).
- POSTED: BRAVO-CUL-2026-07 ($97,917.93), BRAVO-HAR-2026-07 ($78,213.00), BRAVO-LEX-2026-07 ($35,703.00), BRAVO-ROA-2026-07 ($82,787.97), BRAVO-WAY-2026-07 ($64,122.45) — all classed by store, dated 7/31/2026, via `Quickbooks Set UP/gl_to_je.py` conversion of the July Consolidated GL CSVs. Verified against the live July P&L in QBO: Total Income $331,302.06 (was $0), Total COGS $114,791.93 (was $0), and Retail Sales/Gold Revenue/Pawn Service Charges/COGS lines tie out exactly to the JE totals.
- ROA's JE has a known ~$65 Bravo-side export discrepancy (unmapped GL accounts summed to $53,557.52 but the entry only balances at $53,492.52) — posted using the balancing figure per the converter's established convention (residual, not raw unmapped-sum), noted in the line description. This class of small discrepancy ($11-$375/store-month) recurs most months and is a Bravo data-quality quirk, not a conversion bug.
- JOSHUA FLAGGED, AND CONFIRMED BY DATA: March 2026's QBO income ($1.05M) looked anomalously high vs. April ($338K). Root cause found — before the monthly Bravo pipeline existed, Jan + Feb + Mar 2026 revenue was bundled into one classless `BRAVO-{STORE}-Q1-2026` journal entry dated 3/31/2026 (no per-store class on any line). $1.05M ÷ 3 ≈ $350K/month, right in line with Apr-Jun's real $298K-$364K monthly range — confirming the whole quarter landed in March's column, not that March was actually a 3x month.
- Pulled REAL monthly Bravo Consolidated GL data for Jan and Feb 2026 (all 5 stores) to replace the lump-sum Q1 JE with three clean classed monthly entries (Jan/Feb/Mar), matching the Apr-Jul convention. Jan CUL/WAY needed a retry after Bravo hung mid-run (`could not reach a logged-in dashboard` safety-rail skip) — fixed via `_relaunch_bravo_and_watcher.ps1`, not a blind timeout tweak. March data was already on disk from the original GL-export fix earlier today.
- NEXT (not yet done): pull the actual posted `BRAVO-{STORE}-Q1-2026` JE amounts from QBO to confirm the exact double-count/misallocation, reverse those 5 classless entries, and post 15 new classed monthly JEs (Jan/Feb/Mar x 5 stores) in their place.

## 2026-08-04 (later) — HAR/LEX 2025 scrap backfill (partial; blocked by Bravo instability)
- Attempted to backfill missing 2025 gold-scrap history for Harrisonburg (HAR) and Lexington (LEX) using `bravo_pull_complete.sh` (one store per invocation, per the established rule). ROA LOW-CONF upgrade stretch goal not attempted — blocked before reaching it.
- HAR: PARTIAL SUCCESS. New authoritative (`posted` date-source) data landed for 2025-01 (both buckets, full weights) and 2025-03/Feb-collection (one bucket). HAR still missing 2025-04 through 2026-01 (9-10 months) — unchanged from before this session for those months.
- LEX: NO PROGRESS. Bravo became unresponsive before a clean LEX run could start; LEX 2025 remains only 2025-02 populated, same as this morning.
- ROOT CAUSE: mid-run, Bravo (in the Parallels VM) hung ("Not Responding") during the scrap-refining-gold bucket walk. The pipeline's own `bravo_health_gate.sh` recovery ladder ran its full escalation (guarded kill, relaunch, two recover-to-dashboard attempts, a second forced relaunch, two more recover attempts) and still could not reach a working Dashboard (`FAIL no-dashboard`) — a deeper wedge than the routine EnsureStore cascade seen in the morning's earlier attempts; needs a manual look if it recurs.
- One plain-language Slack DM sent to Joshua (`D03BHQH5VGT`) per Failure Alert Policy v2, describing the blocker in non-technical terms. No public/team channel touched.
- `scrap_rankings.py build` re-run to absorb the partial HAR gains: 106 buckets, 92 posted / 14 LOW-CONF (all pre-existing ROA gaps, unchanged), 3 unresolved, 4 missing-weight. `output/scrap_history.csv` and the Trends workbook (`Valley Pawn - Gold Scrap Trend.xlsx`) both refreshed and confirm the new HAR rows.
- REMAINING GAP: HAR 2025-04..2026-01 and nearly all of LEX 2025 still need a re-pull once Bravo is confirmed stable again. ROA's 14 LOW-CONF 2025/2026 months also still pending the planned upgrade attempt.

## 2026-08-04 (later #3 -- corrected false gap claim, doubled content volume, root-caused the quota-miss pattern)

- CORRECTION (Rule 12): earlier this session I told Joshua Waynesboro's weekly post was completely missing from Publer and Roanoke was missing its Instagram leg. Both claims were FALSE -- caused by Publer's `GET /posts` silently capping results at ~15 when queried without `from`/`to` date-range params (the exact bug the 2026-08-03 manifest had already documented and warned about). Re-verified all 8 items' Publer post IDs directly (`GET /posts/{id}`) -- all 29 platform posts for the 2026-08-03 batch are correctly scheduled/published, including Waynesboro and Roanoke IG. No backfill was needed or performed. Added an explicit warning about this cap to `vp-content-batch-weekly` and to future verification steps.
- ROOT CAUSE (real finding) for "why isn't the weekly batch firing at full volume for all stores every cycle": it was never store-skipping -- every store gets covered. It's that `vp-content-batch-weekly` has shipped BELOW its 20-item target several weeks running: 2026-07-20 13/20 (MJ session glitch), 2026-07-27 10/20 (stale Bravo export + missing manager submissions), 2026-08-03 8/20 (approval-pause bug, self-healed via manual recovery, all 8 verified live). Each week self-healed and everything that shipped was real/verified -- the miss was quantity, not coverage.
- DOUBLED the Brand+store-local weekly footprint per Joshua's direct instruction: 3 Brand + 10 store-local (13) -> 6 Brand + 20 store-local (26). Store-local now 4 items/store/week (was 2). Deals-of-the-Week (5) and Reels (2) unchanged, owned by their own pipelines/cadence. Updated via `update_scheduled_task` on `vp-content-batch-weekly`: added a fabrication-is-never-the-answer restatement at the new target, a Bravo-freshness-matters-more note, an MJ-throughput note, an IG/Twitter stagger-planning note for the larger shared-account load, and the Publer 15-result silent-cap warning.
- ADDED a NO-PAUSE CANARY to `vp-content-batch-weekly` after the unresolved 2026-08-03 approval-pause bug (still not root-caused at the trigger level -- this is a mitigation/backstop, not a fix). If a future run notices itself about to pause for input, it's instructed to recognize that as the bug and self-correct (skip-and-log the one item) rather than pause the whole batch.
- NEW scheduled task `vp-content-batch-quota-watchdog` (Tue 10 AM ET) -- reads the last 2 weeks' manifests, DMs Joshua ONLY if fill rate is below 60% for 2 consecutive weeks (a real pattern, not a one-off dip). Makes future volume misses visible automatically instead of requiring the kind of manual Slack/Publer archaeology this session just did by hand. Read-only; does not touch or retry `vp-content-batch-weekly` itself.


## 2026-08-04 (later #2 — postflight DM consolidated into #social-media)

- Joshua: "only post to social media channel, delete the redundant scheduled post to me." `vp-content-batch-postflight`'s routine weekly success DM ("Week of ... N posts published, no action needed") was duplicating the new `weekly-social-media-recap` post to #social-media. Updated via `update_scheduled_task` (not a raw file edit): postflight is now SILENT on a clean success. It still DMs Joshua on any partial failure, silent platform drop, or backfill needing his go-ahead -- those are alerts, not recaps, and stay on his DM per the standing failure-alert policy.
- Backup of prior postflight prompt kept at `Scheduled/vp-content-batch-postflight/SKILL.md.bak-pre-social-recap-consolidation-2026-08-04`.
- `weekly-social-media-recap` (Mon 9 AM -> #social-media) and `vp-publer-analytics-friday` (Fri 4 PM -> Joshua DM, engagement digest for the Monday adjust loop) are unchanged -- different purposes, not redundant with each other.


## 2026-08-04 (weekly social media recap — new channel + new task)

- NEW Slack channel #social-media (C0BMRC2LN3D) created by Joshua today, previously unused. NEW scheduled task `weekly-social-media-recap` (Mon 9 AM ET) posts a team-visible recap of everything published across all Valley Pawn social channels in the trailing 7 days, straight from Publer's API (Rule 12 — verified against actual output, not a manifest). Spec: `Scheduled/weekly-social-media-recap/SKILL.md`.
- NEW `Refine Social Media/weekly_social_recap.py` — read-only script, `PublerClient.list_posts(state='published')` filtered to last 7 days, grouped by platform + store/page. Additive only; does not touch `publer_weekly_digest.py` or `friday_close_engagement.py`.
- This is DISTINCT from the two existing Publer-output posts, which both stay DM-only to Joshua and are untouched: `vp-publer-analytics-friday` (Friday engagement digest) and `vp-content-batch-postflight` (Monday publish-verification). Joshua asked specifically for a channel-visible "what posted last week" record, not another DM.
- First run done manually (not via the new schedule) and posted live to #social-media same day: 13 posts published Jul 28-Aug 4 (FB 7, IG 2, X 2, Blog 2). Confirmed real data pulled from Publer, not placeholder.


## 2026-08-04 (scrap rankings — new monthly task + data-integrity fix)
- NEW scheduled task `monthly-scrap-rankings` (1st of month, 8 AM ET, trig_018QzLdSAVTub3nfUhp7ExU9, enabled, first fire 2026-09-01). Posts gold scrap weight ranking by store + YoY + YTD to #scrap-rankings. Spec: `Scheduled/monthly-scrap-rankings/SKILL.md`. Net-new; no overlap with any existing task (the `com.valleypawn.vpops.job_gold_trend` launchd agent is DISABLED and not loaded).
- NEW `Bravo Data Extraction/scrap_rankings.py` — canonical scrap history builder + report generator (`build` / `validate` / `report YYYY-MM`). Writes `output/scrap_history.csv`.
- **DATA INTEGRITY — the scrap CSVs cannot be summed naively.** The `Month` column is the QUERY WINDOW, not the bucket's month; 43 of 178 buckets appear under 2-3 different query months. Summing it produced a false 2025 total of 6,773 dwt. Canonical key is `(Store, BucketName)`, deduped. Two wrong figures were reported to Joshua before this was caught and were retracted.
- **PERIOD KEY = the month a bucket was POSTED (closed), from StatusDate.** Confirmed by Joshua: buckets are posted the month AFTER the gold is collected. Validated — 72 of 85 year-bearing bucket names sit exactly one month before their posted date. Reporting on the posted month is what makes a 1st-of-month post possible; last month's COLLECTION has not been posted yet on the 1st. OPEN buckets excluded.
- Bucket NAMES are not a usable date: three conventions found (named for collection month / creation month / Waynesboro 2026 names for the month AHEAD). New naming standard posted to #policy-announcements 2026-08-04: `YYYY-MM GOLD` and `YYYY-MM GOLD WITH STONES`, bucket opened on the 1st of the month it collects. Do not rely on it until it visibly takes hold at all 5 stores.
- Known gap: 14 buckets (HAR/LEX/ROA 2025) still carry LOW-CONF name-derived dates and 15 buckets are missing weights, because those stores were originally pulled with an older handler that did not emit CreatedOn/StatusDate. Backfill pulls queued; re-run `scrap_rankings.py build` after they land. YoY for those stores will be incomplete until then.
- Bravo `EnsureStore` wedge recurred repeatedly during this work — multi-store scrap triggers fail partway through. ALWAYS pull scrap ONE STORE PER TRIGGER. Recovery that works every time: ClickOnce relaunch via `Start-Process ...Bravo.appref-ms` through prlctl, then re-gate.


Newest first. Material changes to the business operating system. Read this BEFORE any build, fix or diagnosis.

## 2026-08-04 (later) - eom-bravo-gl-export root cause FOUND and FIXED (was misdiagnosed as a Continuous-Scrolling render hang)
- The July Consolidated GL export failure (0/5 stores succeeding since 2026-08-01) was NOT a Bravo rendering bug. Two prior fix attempts today chasing a "Continuous Scrolling" theory (reordering a toggle-off block, bumping timeouts to 90s/240s) both failed live-tested — because that was never the cause.
- ACTUAL CAUSE, found by directly watching a live run via computer-use instead of guessing at more timeouts: Bravo's Consolidated GL report refuses to open if any day in the requested range is unposted. It shows a `Warning: There are dates that need to be posted first: <date>` dialog, which the automation's generic popup-dismiss swallows silently, then waits forever for a report window that will never exist. HAR had 7/31/2026 still unposted; the `post-to-accounting-post` step (Step 1) was silently failing to post it ("could not click Post button" - a separate, still-open UI-automation bug, see BRAVO_KNOWN_ISSUES.md).
- Fix applied: manually posted HAR 7/31, confirmed the GL export then succeeds immediately (48 rows, real CSV, ~70s - this report is not slow once unblocked). Re-ran `post-to-accounting-post` for CUL/LEX/ROA/WAY - all 4 succeeded automatically (7/31 was already posted for them; only HAR was stuck). Then ran `post-to-accounting-gl` for all 5 stores for July.
- Full writeup, including the still-open intermittent Post-button-click bug, in `Bravo Data Extraction/BRAVO_KNOWN_ISSUES.md`.
- FINAL VERIFIED STATE (same session, ~09:28 ET): all 5 stores' July Consolidated GL now export cleanly - CUL 52 rows, HAR 48, LEX 47, ROA 46, WAY 48 - real CSVs confirmed on disk in `Bravo Data Extraction/output/`.
- Combined into `2026-07 Consolidated GL.xlsx` (one tab per store + a Combined tab) and uploaded to Drive Accounting Exports: https://drive.google.com/file/d/1u6VtowJncheZh-_rm3yCp2OhaodWwN9s/view - confirmed via the returned file object (real fileSize 26479 bytes, correct parent folder).
- DID NOT post a QBO journal entry (Step 5). Per `project_2026_books_cleanup` memory, 2026 QBO books are being built purely transactionally from the bank feed, not via monthly consolidated Bravo GL journal entries - posting a JE here could conflict with that approach. Flagging for Joshua to decide whether `eom-bravo-gl-export`'s Step 5 (QBO JE posting) is still the intended design or should be retired/changed now that the books are being kept differently.
- Note on the "DISABLED: eom-bravo-gl-export" line in today's earlier entry below: that was a transient state from repeated one-time `fireAt` test triggers during today's live-verification cycle. Confirmed via `list_scheduled_tasks` as of this entry: `enabled: true`, `cronExpression: "0 6 1 * *"` - back to its normal monthly schedule, no action needed.

## 2026-08-04
- FLAGGED (unexplained): eom-bravo-gl-export and weekly-website-kpi-artifact-refresh both went from enabled to disabled today with no matching explanation found in changelog history. Joshua notified via Slack. Needs follow-up.

- Enabled scheduled tasks: 81 -> 82
- Registered scheduled tasks: 121 -> 125
- Task folders on disk: 141 -> 145
- ENABLED: eom-bravo-gl-export-watchdog
- ENABLED: northwest-registered-agent-daily-check
- ENABLED: vp-comms-drift-monthly-check
- DISABLED: eom-bravo-gl-export
- DISABLED: weekly-website-kpi-artifact-refresh

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

## 2026-08-03 (pay-transparency guardrail + correction)
- CORRECTION (Rule 12 — I got this wrong earlier today): Brevo campaign #51 "Hiring — Retail Sales Associates v2" NEVER SENT. Live API check: `status: suspended`, `sentDate: None`, sent 0 / delivered 0 / opens 0. It was scheduled for 2026-07-23 3:00 PM and suspended before it fired. An earlier statement this session that it was "already delivered, cannot be recalled" was wrong — it was inferred from the BUSINESS_OS "queued ... preflight PASS" note instead of read from output. Practical effect: there was NEVER an email-side pay-transparency violation. Exposure was website + social only, and both are fixed and verified.
- CORRECTION: active employee count is 14, not 13. Gusto Step 4 ("All 14 individuals") is authoritative; Michael Chambers started 2026-08-03. The Aug 2026 compliance memo has been corrected. No conclusion changes — every threshold that matters (FMLA, organ-donation leave) is 50.
- ADDED: pay-transparency guardrail in `Projects/Email Refinement/brevo_preflight.py` (backup `.bak-20260804-083919`). New check in `run_checks()` hard-fails any campaign containing hiring language that states no wage/salary. Gates both the manual preflight and the daily `brevo-preflight-watchdog`. Deliberately NOT in FIXABLE — where a range belongs in prose is a judgment call and guessing a number is worse than blocking the send.
- Detection design: ONE strong signal ("we're hiring", "now hiring", "join our team", "open positions", "now accepting applications", "hiring sales/loan/store/full-time/part-time") OR TWO weak signals together (/careers link, "apply at/now/today", "send your resume"). A bare /careers link CANNOT trigger it alone — an earlier draft did, which would have failed every campaign the day someone adds a careers link to the footer, and a preflight that cries wolf gets bypassed. Verified master template 48 currently has zero /careers refs.
- Accepts a range OR a single stated wage, hourly OR salaried, any dash style (- – — "to").
- VERIFIED AGAINST OUTPUT: ran live — #51 now FAILS with the pay-transparency error naming Va. Code 40.1-28.7:12 and the approved $16.50-$21.50/hr range; #52 (non-hiring) still PASSES clean, so no regression. Plus 10 unit cases covering false-positive and false-negative traps, 0 mismatches.
- Approved good-faith range for Sales & Loan Associate/Representative: **$16.50–$21.50/hour** (actual spread paid across the 5 stores). CEO approves any change — it is named in policy HR-2026-03 so it cannot drift informally.
- POLICY SHIPPED: "Pay Transparency & Salary History Policy (HR-2026-03)" — one page, Gusto template 7881310, `processing_state: approved`, 14 signature requests all `requested`, Team document scoped to current team members + all future hires so new hires inherit automatically.

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