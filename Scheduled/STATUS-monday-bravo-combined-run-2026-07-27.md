# monday-bravo-combined-run — FAILED — 2026-07-27

## Root cause
This run executed inside a Cowork sandboxed session, not a native Claude Code session with real Mac shell access. The sandbox's bash tool (`mcp__workspace__bash`) is an isolated Linux container with no access to:
- `/usr/local/bin/prlctl` (Parallels CLI) — command not found, no Parallels tooling in this sandbox at all.
- The Windows 11 VM running Bravo POS / AutoHotkey watchers.
- `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` (triggers, logs, watcher status files) — this path is not mounted into the sandbox. Only `/Users/joshuadavis/Documents/Claude/Scheduled` is mounted (as `Scheduled/`).

Because of this, none of the Step 0 pre-flight checks (VM running, bravo_watcher.ahk alive, BravoAutoLogin.ahk alive, watcher.last_started.txt freshness, trigger queue empty) could be performed, and no trigger file could be dropped to `.../Bravo Data Extraction/triggers/`.

## What did NOT happen
- No pre-flight checks ran.
- No `monday-bravo-combined-YYYY-MM-DD.json` trigger was dropped.
- `monday-bravo-combined-compile` was NOT rescheduled.
- No reports were generated; nothing was posted to any Slack ops channel.

## What DID happen
- Per platform failure policy (v2, set 2026-07-22), a single plain-language failure DM was sent to Joshua's Slack DM channel D03BHQH5VGT. No other channel or person was notified.

## Fix needed for next session
This task needs to run in an execution context that has real filesystem/shell access to Joshua's Mac (native Claude Code / local agent session, not a Cowork sandbox), so it can reach `prlctl`, the Parallels VM, and the Bravo Data Extraction project folder. If this task is being fired as a Cowork scheduled task, it should be re-pointed to run in the local/native agent environment instead, or the Bravo Data Extraction folder and Parallels access need to be exposed into the sandbox (not currently possible via the mounted-folder mechanism, which only exposes one user-selected folder).

Recommend flagging to Joshua (outside of Slack, since this is technical) that the `monday-bravo-combined-run` scheduled task's execution environment needs to be checked/fixed before next Monday's run.
