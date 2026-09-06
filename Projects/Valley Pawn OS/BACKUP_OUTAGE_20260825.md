# Backup Outage — opened 2026-08-25, diagnosed 2026-09-04

**Status: OPEN. Requires one physical action at the Mac Studio's location.**

## What is actually broken

Time Machine has exactly ONE destination: `smb://ValleyPawn@valleypawn-nas.local/TimeMachine`.
That NAS has been off the network since **2026-08-25 13:50 EDT** — the timestamp of the last
successful backup. Since then macOS has retried on its normal hourly cadence and failed every
time with mount error 18.

Verified 2026-09-04 (not inferred from metadata — VP Operating Rule 12):

| Check | Result |
|---|---|
| `tmutil latestbackup` | `Failed to mount destination` (error 18) |
| `ping valleypawn-nas.local` | `cannot resolve` — hostname does not exist on the network |
| Full 10.0.0.0/24 sweep, ports 445 / 548 / 5000 / 5001 | **zero** hosts answer any NAS service |
| `tmutil destinationinfo` | one destination only, the NAS |
| `diskutil list external` | **no external disks attached** |
| TM prefs `SnapshotDates` | 44 restore points, newest `2026-08-25 17:50:28Z` |
| `AutoBackup` | `1` (enabled — Time Machine is trying, it has nowhere to go) |

The NAS is not merely unreachable by name. Nothing on the LAN answers SMB, AFP, or any NAS
management port. The device is powered off, unplugged, on a dead switch port, or has failed.
`10.0.0.214:5000` looked promising in a scan but identifies as an AirPlay receiver, not a NAS.

## What is NOT broken (corrected finding)

The **offsite GitHub backup is healthy** and has been the whole time:

- `origin/main` HEAD = `2026-09-04 00:25:37 -0400`, local and origin at 0/0 divergence.
- Every daily CRIT DM since 2026-07-24 has reported `offsite=~1000h` — **that was false.**
  The watchdog judged offsite freshness by the mtime of `NIGHTLY_BACKUP_STATUS.log`, which is
  only rewritten when the nightly run *fails*. A healthy run leaves it stale forever.
- Fixed 2026-09-04 — the watchdog now reads the actual git commit date. Original preserved as
  `SKILL.md.bak-pre-offsite-fix-20260904`.

So the surviving protection is real but narrow: the GitHub repo covers `.md` files and
hand-written source under `~/Documents/Claude` only. It does **not** cover Bravo pipeline
output, the Parallels VM, Photos, or business documents. Those have had no backup for 10 days.

## Detection worked. Response did not.

`BACKUP_HEALTH.log` shows an unbroken CRIT run from 2026-08-26 to 2026-09-04 — ten consecutive
mornings, each with a DM sent. The alerting was correct and nobody acted. Fixed 2026-09-04 by
adding **Step 3.5** to the watchdog: from the third consecutive CRIT day the DM leads with how
many days have passed and gives exactly one physical instruction.

## Second, separate risk found

The Mac Studio's internal data volume is at **97% full** — 372 GiB used, ~14 GiB free. This
matters twice over: it is a stability risk on its own, and it rules out using internal space as
any kind of stopgap backup target.

## What has to happen

1. **Physical, today — restore or replace the NAS.** Power-cycle it and confirm its network
   cable and switch port. If it does not come back on the LAN, it has failed. Once it is
   reachable again Time Machine resumes on its own; no settings need changing.
2. **Structural — add a second Time Machine destination on a directly-attached external SSD.**
   The current design puts every byte of local backup behind one network device with no
   fallback; that is precisely the failure that has been running for 10 days. A 4 TB USB-C SSD
   at the Mac Studio, added as a second destination, means a NAS outage stops being a total
   backup outage. This needs a purchase decision.
3. **Housekeeping — reclaim space on the internal volume** (97% full).

Until step 1 is done, everything on the Mac Studio that is not a `.md` or source file in the
GitHub repo is one hardware failure away from being gone.
