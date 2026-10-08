import sys

def patch(path, replacements):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    for old, new in replacements:
        count = content.count(old)
        if count != 1:
            print(f"ABORT: expected 1 occurrence, found {count}: {old[:80]!r}")
            sys.exit(1)
        content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: patched {path}")

LEDGER = "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md"
HUMANQ = "/Users/joshuadavis/Documents/Claude/Projects/Life OS/HUMAN_QUEUE.md"

ledger_replacements = [
 ("| 2026-10-07 00:00 ET (native) | chekkit-ai-responder | The AI text responder could not read the Chekkit alert emails (ValueError). | NEEDS_HUMAN: no | OPEN |",
  "| 2026-10-07 00:00 ET (native) | chekkit-ai-responder | The AI text responder could not read the Chekkit alert emails (ValueError). | NEEDS_HUMAN: no | COVERED 2026-10-07 12:45 ET (fleet-guardian) — native/recurring ValueError pattern (same as 10/5, 10/6 rows), not a Cowork rerun target, no new action possible |"),
 ("| 2026-10-07 02:10 ET (native) | fleet-doctor | Nightly check found: 1 background job(s) logged errors this week. 1 background job(s) have gone quiet for longer than their own schedule allows, which usually means they have stopped running.  | NEEDS_HUMAN: no | OPEN |",
  "| 2026-10-07 02:10 ET (native) | fleet-doctor | Nightly check found: 1 background job(s) logged errors this week. 1 background job(s) have gone quiet for longer than their own schedule allows, which usually means they have stopped running.  | NEEDS_HUMAN: no | COVERED 2026-10-07 12:45 ET (fleet-guardian) — diagnostic-only, matches the standing fleet-doctor pattern seen every day in this ledger, not independently actionable without more detail on which specific job |"),
 ("| 2026-10-07 08:50 ET | northwest-registered-agent-daily-check | Run blocked before login: this session's auto-mode safety classifier denied the agent dispatch for autonomous portal login + SMS-code handling + outbox Slack post (reason tag: Auto-Mode Bypass); no portal login, document check, or Drive/Slack action was attempted | NEEDS_HUMAN: yes, Joshua should confirm with his Cowork session whether this task is meant to keep running with 2FA auto-entry + outbox Slack routing, or whether it should move to a flow that doesn't need either | OPEN |",
  "| 2026-10-07 08:50 ET | northwest-registered-agent-daily-check | Run blocked before login: this session's auto-mode safety classifier denied the agent dispatch for autonomous portal login + SMS-code handling + outbox Slack post (reason tag: Auto-Mode Bypass); no portal login, document check, or Drive/Slack action was attempted | NEEDS_HUMAN: yes, Joshua should confirm with his Cowork session whether this task is meant to keep running with 2FA auto-entry + outbox Slack routing, or whether it should move to a flow that doesn't need either | QUEUED 2026-10-07 12:45 ET (fleet-guardian) — matches existing 2026-09-09 Northwest Registered Agent HUMAN_QUEUE row (2FA/device-trust wall); bumped Last-hit to 10/7, added today's auto-mode-classifier-denial detail as a new wrinkle on the same standing wall |"),
 ("| 2026-10-07 05:18 ET | gusto-keep-alive | Claude in Chrome not connected; cannot check Gusto session status. | NEEDS_HUMAN: no | OPEN |",
  "| 2026-10-07 05:18 ET | gusto-keep-alive | Claude in Chrome not connected; cannot check Gusto session status. | NEEDS_HUMAN: no | COVERED 2026-10-07 12:45 ET (fleet-guardian) — transient Chrome-extension-connectivity gap, matches recurring gusto-keep-alive pattern seen in earlier rows, self-heals on next successful connection, no HUMAN_QUEUE action warranted |"),
 ("| 2026-10-07 10:36 ET | daily-dress-code-check | Could not open the Google Home camera grid for the Wednesday Culpeper/Roanoke dress code check — the Claude in Chrome browser extension was not connected, and the fallback browser's Google sign-in for fullcirclepawn@gmail.com (the camera account) stopped at a passkey confirmation screen that needs a fingerprint/face/device unlock. | NEEDS_HUMAN: yes, Joshua needs to either open Chrome with the Claude extension on the Mac so this session can reconnect, or complete the fullcirclepawn@gmail.com passkey prompt himself so the cached Google Home session stays usable for future runs | OPEN |",
  "| 2026-10-07 10:36 ET | daily-dress-code-check | Could not open the Google Home camera grid for the Wednesday Culpeper/Roanoke dress code check — the Claude in Chrome browser extension was not connected, and the fallback browser's Google sign-in for fullcirclepawn@gmail.com (the camera account) stopped at a passkey confirmation screen that needs a fingerprint/face/device unlock. | NEEDS_HUMAN: yes, Joshua needs to either open Chrome with the Claude extension on the Mac so this session can reconnect, or complete the fullcirclepawn@gmail.com passkey prompt himself so the cached Google Home session stays usable for future runs | QUEUED 2026-10-07 12:45 ET (fleet-guardian) — matches existing 2026-09-19 Google Home passkey HUMAN_QUEUE row; bumped Last-hit to 10/7, noted today's added Chrome-extension-disconnected symptom |"),
]

sweep_row = (
"\n| 2026-10-07 12:45 ET (fleet-guardian, SILENT pass) | (guardian self) | Session type: Cowork session bound to 'Social Media' project, connected folders limited to 'Refine Social Media' and 'Projects' (same structural gaps as every pass since 9/17 — no mcp__Control_your_Mac__osascript tool loaded or deferred, no scheduled-tasks registry tool, ~/Documents/Claude/Scheduled and the Mac home root outside the mounted folders — confirmed again via ToolSearch and a direct device_bash probe this pass). vp_dryrun.py guard confirmed OFF (exit 1, publications live) via the mounted bin path. Step 1 (registry-based missed-fire croniter scan): SKIPPED, no registry access this session. Step 1b (expected_outputs.json spot-check): deferred to the extensive same-day CHANGELOG 'cloud-move morning watch' entry already covering cloud-vs-local task status through 11:30 ET today in detail — not duplicated here to avoid redundant Slack reads. Step 1c (FAILURE_LEDGER main intake): dispositioned all 5 of today's OPEN rows (221, 222, 224, 225, 226) in place — 3 COVERED (chekkit-ai-responder, fleet-doctor, gusto-keep-alive — all native/recurring/transient, no Cowork action possible), 2 QUEUED (northwest-registered-agent-daily-check, daily-dress-code-check — both matched to existing standing HUMAN_QUEUE rows and bumped rather than duplicated). Step 2/3 reruns: 0 of 5 used — none of today's open items are rerun-safe Cowork misses reachable from this session (all either native-task failures or human-only walls). HUMAN_QUEUE.md: 2 edits (Northwest Registered Agent row bumped to 10/7 with new auto-mode-classifier-denial detail; Google Home passkey / daily-dress-code-check row bumped to 10/7 with new Chrome-extension-disconnected detail). No new HUMAN_QUEUE rows added — both today's human-only findings matched existing standing rows. No Slack DM sent — this is the 12:45 SILENT pass per the one-DM-a-day rule, regardless of findings. | NEEDS_HUMAN: mixed, see HUMAN_QUEUE.md | INFO |\n"
)

patch(LEDGER, ledger_replacements)

with open(LEDGER, "a", encoding="utf-8") as f:
    f.write(sweep_row)
print("Appended sweep row to ledger.")

humanq_replacements = [
 ('unless "remember this device" is ticked during a live sign-in. | northwest-registered-agent-daily-check | 2026-10-04 | OPEN — surfaced 9/16, 9/23, 9/30, resurfaced 10/4 (25 days unresolved, no auto-retry possible — 2FA device trust; separately, the sms-code-relay launchd agent itself looks stale since 10/3 09:39 ET, worth a `launchctl list | grep sms-code-relay` check too) |',
  'unless "remember this device" is ticked during a live sign-in. **Update 10/7 08:50 ET:** a scheduled run\'s own auto-mode safety classifier denied the dispatch for autonomous portal login + SMS-code handling + outbox Slack post before even reaching the 2FA screen — a new wrinkle on the same standing wall (now three distinct blockers: stale session, 2FA device trust, and the classifier denial itself). Worth Joshua confirming with a live Cowork session whether this task should keep attempting 2FA auto-entry or move to a different flow. | northwest-registered-agent-daily-check | 2026-10-07 | OPEN — surfaced 9/16, 9/23, 9/30, resurfaced 10/4, 10/7 (28 days unresolved, no auto-retry possible — 2FA device trust + auto-mode classifier denial; separately, the sms-code-relay launchd agent itself looks stale since 10/3 09:39 ET, worth a `launchctl list | grep sms-code-relay` check too) |'),
 ('so the automated check can reach the camera grid. | daily-dress-code-check | 2026-10-02 | OPEN — surfaced 9/17, hit again 9/23, 9/24 (7th+ occurrence), resurfaced 10/2 (8 days unsurfaced, past the 7-day rule — still blocking the daily dress-code check) |',
  'so the automated check can reach the camera grid. **Update 10/7 10:36 ET:** same passkey wall, plus the Claude in Chrome extension was also not connected this run — two blockers now (extension connectivity + the passkey itself). | daily-dress-code-check | 2026-10-07 | OPEN — surfaced 9/17, hit again 9/23, 9/24, resurfaced 10/2, 10/7 (still blocking the daily dress-code check; today also needs the Chrome extension reconnected) |'),
]
patch(HUMANQ, humanq_replacements)
