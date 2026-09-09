---
name: backup-health-watchdog
description: Daily 7 AM — verify Time Machine to valleypawn-nas.local is actually backing up (freshness, coverage gaps, capacity, exclusions, auto-backup enabled) plus offsite GitHub OS backup freshness. Silent on success; DMs Joshua only on WARN/CRIT. Zero computer-use, read-only.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---
You are running the Valley Pawn / Full Circle Finance Inc **Backup Health Watchdog**.

Purpose: nobody currently knows if the backup stopped. This task is the detector. It is READ-ONLY and additive — it changes nothing.

## Step 1 — Run the health check

Use the `mcp__Control_your_Mac__osascript` tool (NOT the sandbox bash tool — the sandbox cannot see the Mac's filesystem or the NAS). Run this as `do shell script "..."`:

```
echo '=== DEST ==='; tmutil destinationinfo 2>&1
echo '=== LATEST ==='; tmutil latestbackup 2>&1
echo '=== AUTOBACKUP ==='; defaults read /Library/Preferences/com.apple.TimeMachine.plist AutoBackup 2>&1
echo '=== BACKUPS ==='; tmutil listbackups -d "/Volumes/Backups of Mac Studio (2)" 2>&1 | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}'
echo '=== SPACE ==='; df -g "/Volumes/Backups of Mac Studio (2)" 2>&1 | tail -2
echo '=== NAS ==='; ping -c 1 -t 3 valleypawn-nas.local 2>&1 | head -2
echo '=== EXCLUSIONS ==='; tmutil isexcluded /Users/joshuadavis/Documents /Users/joshuadavis/Documents/Claude /Users/joshuadavis/Parallels /Users/joshuadavis/Library/Parallels /Users/joshuadavis/Desktop 2>&1
echo '=== GITHUB OS BACKUP ==='; git -C /Users/joshuadavis/Documents/Claude log -1 --format='HEAD %ci %s' 2>&1; git -C /Users/joshuadavis/Documents/Claude log -1 --format='%ct' origin/main 2>&1; echo '--- last failure note (context only, NOT a freshness signal) ---'; tail -3 /Users/joshuadavis/Documents/Claude/NIGHTLY_BACKUP_STATUS.log 2>&1
```

Split into two or three osascript calls if any single call errors. Do NOT use `$` variables or `for` loops inside `do shell script` — AppleScript mangles them.

## Step 2 — Evaluate against these thresholds

Compute today's date first (`date` via osascript) — never assume.

**CRIT** (any one of these):
- NAS unreachable (ping fails)
- Newest backup is more than 48 hours old
- AutoBackup is not `1`
- Any of these paths returns `[Excluded]`: Documents, Documents/Claude, Parallels, Library/Parallels, Desktop
- `tmutil latestbackup` returns nothing / errors

**WARN** (any one of these, and no CRIT):
- Newest backup is 26–48 hours old
- 4 or more of the last 14 calendar days have zero backups (count distinct dates in the BACKUPS list)
- Backup destination is 85% or more full
- The newest commit in `~/Documents/Claude` (git, `origin/main`) is more than 72 hours old
  (offsite OS backup stalled). **Do NOT judge this by the mtime of
  `NIGHTLY_BACKUP_STATUS.log`** — that file is only rewritten when the nightly run
  FAILS, so a healthy backup leaves it stale indefinitely. Judging by its mtime is
  what produced a false `offsite=1008h` in every DM from 2026-07-24 to 2026-09-04
  while the repo was in fact committing nightly (VP Operating Rule 12: verify
  against the output, not the metadata). Read the log only for the text of the last
  recorded failure, never for freshness.

**OK**: none of the above.

## Step 3 — Report

**If status is OK: do nothing. Post nothing. Send nothing. Exit silently.** This follows the same convention as `bravo-health-watchdog` and `funds-verification-watchdog` — noise defeats the purpose.

**If status is WARN or CRIT:** send Joshua a Slack DM using the Slack MCP (`slack_send_message` to Joshua's DM). Format:

```
:floppy_disk: *Backup Health — {CRIT or WARN}*  ({today's date})

*What's wrong*
• {one bullet per problem, plain English, no jargon}

*Current state*
• Last backup: {timestamp} ({N} hours ago)
• Retention: {N} restore points spanning {N} days ({oldest date} → {newest date})
• Days with no backup, last 14: {N}
• Destination: {used} GB used / {avail} GB free ({pct}% full)
• Offsite OS backup (GitHub): last ran {N}h ago

*What to do*
• {concrete next step per problem}
```

If Slack is unavailable, fall back to appending the same report to `/Users/joshuadavis/Documents/Claude/BACKUP_HEALTH.log` via osascript and note that Slack failed.

## Step 3.5 — Escalate a CRIT that is not getting fixed (added 2026-09-04)

A daily DM that reads the same every morning stops being read. Before sending, count
how many consecutive prior days `BACKUP_HEALTH.log` ends in `CRIT`:

`grep -c CRIT /Users/joshuadavis/Documents/Claude/BACKUP_HEALTH.log` is not enough —
read the last 14 lines and count the unbroken CRIT run ending at the most recent entry.

- **1–2 consecutive days:** send the normal DM from Step 3.
- **3 or more consecutive days:** send the normal DM, and make the FIRST line instead:

  `:rotating_light: *No backup has run in {N} days.* Everything on the Mac Studio is currently
  one hardware failure away from being gone.`

  Then, under *What to do*, give exactly one physical instruction and nothing else —
  the person reading this on a phone needs an action, not a diagnosis.

This exists because the NAS went offline 2026-08-25 and this task sent 10 identically
shaped CRIT DMs before anyone acted. Detection was never the problem; the DM not
conveying escalating severity was.

## Step 4 — Always log

Regardless of status, append one line to `/Users/joshuadavis/Documents/Claude/BACKUP_HEALTH.log` via osascript:
`{ISO datetime} | {STATUS} | last={timestamp} age={N}h count={N} span={N}d missed14={N} full={pct}% offsite={N}h`

This builds the historical record that currently does not exist.

## Rules
- Never modify Time Machine settings, never delete backups, never unmount anything. Read-only.
- Never claim a backup "ran" based on a preference-file date alone — verify against `tmutil listbackups` output (VP Operating Rule 12: no diagnosis from metadata).
- If a command fails, retry once, then report the failure as a CRIT rather than guessing.
- Keep the DM short. Joshua reads it on his phone.
## Step 5 — SMB1 regression check (added 2026-08-05)

Run via osascript:

```
smbutil statshares -a 2>&1 | grep -i SMB_VERSION
cat ~/Library/Preferences/nsmb.conf 2>&1
```

On 2026-08-05 SMB1 was eliminated machine-wide by writing ~/Library/Preferences/nsmb.conf with protocol_vers_map=6 (SMB2/SMB3 only), and the Parallels guest share (/Volumes/[C] Windows 11) was unmounted. Parallels may attempt to re-establish that share.

**Raise WARN if either is true:**
- Any share reports SMB_VERSION of SMB_1
- ~/Library/Preferences/nsmb.conf is missing, or no longer contains protocol_vers_map=6

This is a regression detector. Report it in the DM under a heading *SMB1 regression* with the exact share name and the remediation: rewrite nsmb.conf with protocol_vers_map=6 under a [default] section, then unmount the offending share.

Do NOT change nsmb.conf yourself — report only. Editing it is a change, and this task is read-only.
