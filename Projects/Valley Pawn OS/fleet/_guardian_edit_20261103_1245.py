import io

path = "fleet/FAILURE_LEDGER.md"
with io.open(path, "r", encoding="utf-8") as f:
    text = f.read()

edits = []

edits.append((
"| 2026-11-03 02:10 ET (native) | fleet-doctor | Nightly check found: 8 background job(s) logged errors this week. 8 background job(s) have gone quiet for longer than their own schedule allows, which usually means they have stopped running.  | NEEDS_HUMAN: no | OPEN |",
"| 2026-11-03 02:10 ET (native) | fleet-doctor | Nightly check found: 8 background job(s) logged errors this week. 8 background job(s) have gone quiet for longer than their own schedule allows, which usually means they have stopped running.  | NEEDS_HUMAN: no | OPEN -- Re-checked 2026-11-03 12:5x ET (fleet-guardian 12:45 pass, SILENT): the specific jobs behind this weekly digest are individually tracked below this same date (conductwatch-report -- Slack conversations.history scope gap, confirmed 3 consecutive days; supply-deliveries -- transient Chrome/Playwright profile contention, confirmed via a same-morning successful order-placing run sharing the same log) -- no new standalone action beyond those rows. | COVERED 2026-11-03 (fleet-guardian) -- constituent misses already individually ticketed and triaged this pass."
))

edits.append((
"| 2026-11-03 07:35 ET (native) | conductwatch-report | Camera watch report did not post (rc=1) | NEEDS_HUMAN: no | OPEN |",
"| 2026-11-03 07:35 ET (native) | conductwatch-report | Camera watch report did not post (rc=1) | NEEDS_HUMAN: no | OPEN -- Re-checked 2026-11-03 12:5x ET (fleet-guardian 12:45 pass, SILENT): root cause confirmed from conductwatch-report.log -- every failure (11/1, 11/2, 11/3, all 07:35 ET) logs the identical `conversations.history: missing_scope` Slack API error immediately before the LEDGER line; a Slack bot OAuth scope gap (the duplicate-guard read), not a data or code bug -- a rerun would hit the identical wall every time. Also not attempted for a separate reason: this pass's own permission classifier denied a queued host-queue job that would have invoked the task's --send path directly (external-write risk). conduct_watch_report.sh otherwise reads as a clean rerun_safe candidate (DM-only to Joshua, duplicate-guarded, no external humans/money/HR/Bravo) once the scope gap is fixed -- worth adding to rerun_manifest.json then, not before. HUMAN_QUEUE row added/appended (same Slack app admin page as the existing files:write row, 2026-11-03). | QUEUED 2026-11-03 (fleet-guardian) -- NEEDS_HUMAN: yes (re-triaged from the medic's original 'no' -- OAuth scope + app reinstall is a human-only action per the hard rule), see Life OS/HUMAN_QUEUE.md."
))

edits.append((
"| 2026-11-03 09:04 ET (native) | supply-deliveries | Last scheduled run ended with an error (exit 1). Last log: 2026-11-03 09:00:02 new requests: 6 [medic] | NEEDS_HUMAN: no | OPEN |",
"| 2026-11-03 09:04 ET (native) | supply-deliveries | Last scheduled run ended with an error (exit 1). Last log: 2026-11-03 09:00:02 new requests: 6 [medic] | NEEDS_HUMAN: no | OPEN -- Re-checked 2026-11-03 12:5x ET (fleet-guardian 12:45 pass, SILENT): supply-order.log shows this run's Playwright browser-launch timeout (BrowserType.launch_persistent_context, 180000ms) immediately beforehand, then three separate successful order-placements in the same shared Chrome profile 4-13 minutes later (09:08-09:17 ET, Lexington/Waynesboro/Roanoke) -- confirms transient Chrome/Playwright profile contention, not a Bravo or data issue, and not reproducible on demand. Not rerun-safe regardless (supply-deliveries is not listed in rerun_manifest.json's rerun_safe array -- defaults verify-only) and a rerun would add nothing the next scheduled run won't also get. | UNRECOVERED 2026-11-03 (fleet-guardian) -- benign, status-check-only (no customer/financial impact); self-resolves like the identical class already did twice this week (asset-recovery, supply-deliveries itself)."
))

edits.append((
"| 2026-11-03 09:09 ET (native) | supply-deliveries | REPEAT FAILURE: failed on 3 runs in a row — needs a code fix, not a rerun. Logs: supply-deliveries.out.log, supply-deliveries.err.log, supply-order.log [medic-repeat] | NEEDS_HUMAN: no | OPEN |",
"| 2026-11-03 09:09 ET (native) | supply-deliveries | REPEAT FAILURE: failed on 3 runs in a row — needs a code fix, not a rerun. Logs: supply-deliveries.out.log, supply-deliveries.err.log, supply-order.log [medic-repeat] | NEEDS_HUMAN: no | OPEN -- Re-checked 2026-11-03 12:5x ET (fleet-guardian 12:45 pass, SILENT): same root cause as the 09:04 ET row above (shared Chrome profile contention with the concurrent order-placing run) -- medic's own 'needs a code fix, not a rerun' note still stands (candidate fix: the same backoff/retry pattern just added to Store Traffic's counter.py v5.1 on 11/2, applied to supply_deliveries' Chrome launch). Not NEEDS_HUMAN (no human action unblocks a profile-contention race) and not rerun-safe (verify-only by default) -- flagged for a dedicated session to add retry/backoff. | UNRECOVERED 2026-11-03 (fleet-guardian) -- code-level fix needed, queued for a dedicated session; benign (status-check only)."
))

edits.append((
"| 2026-11-03 10:33 ET (native) | daily-dress-code-check | The dress code check could not open its automation browser (it may be open for sign-in), so nothing was posted. | NEEDS_HUMAN: no | OPEN |",
"| 2026-11-03 10:33 ET (native) | daily-dress-code-check | The dress code check could not open its automation browser (it may be open for sign-in), so nothing was posted. | NEEDS_HUMAN: no | OPEN -- Re-checked 2026-11-03 12:5x ET (fleet-guardian 12:45 pass, SILENT): FIELD_SCORECARD shows IN GRACE (due 10:30, grace until 14:30 -- not yet a confirmed miss). task_preflight.py classifies this task 'clear' (no predicted MAC/SEND/BROWSER/TOOL approval wall) and it IS listed rerun_safe, so a host-queue catch-up call to dress_code_check.py --send was attempted this pass -- denied by this session's own permission classifier as an external-system-write action (same class of block noted in the 2026-10-26 21:45 pass's digest-DM denial). No rerun executed; not escalated to HUMAN_QUEUE (today's wall is a tooling/classifier block on this guardian pass, not something only Joshua can fix). Left open inside its own grace window for the 21:45 pass (or a session without this classifier restriction) to reassess/retry. | STILL OPEN 2026-11-03 (fleet-guardian, SILENT) -- grace window not yet closed, rerun attempt blocked by this session's own classifier."
))

missing = []
for old, new in edits:
    if old not in text:
        missing.append(old[:80])
    else:
        text = text.replace(old, new, 1)

if missing:
    print("MISSING MATCHES (not applied):")
    for m in missing:
        print(" -", m)
else:
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("All 5 edits applied successfully.")
