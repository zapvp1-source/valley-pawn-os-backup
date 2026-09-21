#!/usr/bin/env python3
"""Disk Health Sentinel — Valley Pawn OS, added 2026-09-04 as part of
SCHEDULED_TASK_RELIABILITY_PLAN.md Phase 3 ("standing visibility, no Claude usage").

Runs via native launchd (no Cowork/Claude session, zero token cost). Purpose: keep the Mac
Studio's internal data volume from refilling the way it did 8/25-9/4 (94% full -> iCloud started
evicting ~/Documents/Claude files -> 47 scheduled-task prompts went dataless -> nightly watchdogs
died with "Resource deadlock avoided"). This script only ever removes things that are safely
regenerable or literally installer duplicates already superseded — it NEVER touches user
documents, Bravo data, or anything under ~/Documents/Claude/Projects or /Scheduled content files.

Actions each run:
  1. Record df -h for / and /System/Volumes/Data to a rolling log.
  2. If Time Machine reports the last backup to the primary (NAS) destination completed
     successfully (tmutil latestbackup / destinationinfo), thin local TM snapshots older than 24h
     via `tmutil thinlocalsnapshots` (Apple's own safe API for this — snapshots are pure
     redundancy once the network backup landed; this does NOT touch actual files).
  3. Flag installer-looking files (*.dmg, *.pkg) in ~/Downloads older than 14 days and larger than
     100 MB. NEVER auto-delete user Downloads — just list them in the log and, on first sighting
     of a given file, note it so the DM digest can mention a running total. Actual deletion is
     Joshua's call (prohibited action per platform rules) unless he has separately said otherwise.
  4. Check for the eviction failure mode again: count dataless files under
     ~/Documents/Claude/Scheduled (the class that broke tasks last time). If more than 0, that is
     CRITICAL by itself regardless of free space, because it silently breaks running automation.
  5. Escalate to Joshua via a single plain Slack DM (Rule 16 — the sentinel itself cannot post to
     Slack since it has no Claude session; it writes to DISK_HEALTH.md and the next Cowork session
     with Slack access — e.g. business-os-daily-refresh, 5:00 AM — reads and relays it) ONLY when:
       - /System/Volumes/Data free space < 15 GiB, OR
       - any dataless file exists under ~/Documents/Claude/Scheduled, OR
       - a Time Machine backup to the NAS has not completed successfully in the last 72h.
     Otherwise: log only, no escalation flag set.
"""
import subprocess, os, time, json, glob, re, calendar

OS_DIR = os.path.expanduser('~/Documents/Claude/Projects/Valley Pawn OS')
LOG = os.path.join(OS_DIR, 'fleet', 'DISK_HEALTH.md')
STATE = os.path.join(OS_DIR, 'fleet', '.disk_health_state.json')
SCHED = os.path.expanduser('~/Documents/Claude/Scheduled')
NOW = time.strftime('%Y-%m-%d %H:%M')


def sh(cmd, timeout=60):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout).stdout.strip()
    except Exception as e:
        return f'ERROR: {e}'


def df_line(mount):
    out = sh(f"df -h '{mount}' | tail -1")
    parts = out.split()
    return dict(mount=mount, size=parts[0] if parts else '?', used=parts[1] if len(parts) > 1 else '?',
                avail=parts[2] if len(parts) > 2 else '?', pct=parts[4] if len(parts) > 4 else '?', raw=out)


def avail_gib(mount):
    # df -g gives whole GiB blocks; more reliable to parse than the -h string
    out = sh(f"df -g '{mount}' | tail -1")
    parts = out.split()
    try:
        return int(parts[3])
    except Exception:
        return None


def _tm_from_tmutil():
    """Route 1 — the obvious one. REQUIRES Full Disk Access; returns None without it."""
    latest = sh('tmutil latestbackup 2>&1')
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})(\d{2})', latest)
    if not m:
        return None
    ts = '-'.join(m.groups()[:3]) + ' ' + ':'.join(m.groups()[3:])
    try:
        # tmutil prints local time
        return time.mktime(time.strptime(ts, '%Y-%m-%d %H:%M:%S'))
    except Exception:
        return None


def _tm_from_prefs():
    """Route 2 — completed-backup timestamps straight out of Time Machine's own preferences.

    Needs NO Full Disk Access. Reads ONLY the `SnapshotDates` array inside Destinations (those are
    backups that actually completed to that destination) and deliberately ignores
    StableLocalSnapshotDate / ReferenceLocalSnapshotDate, which are LOCAL snapshots — counting
    those would report a healthy backup while the NAS was unreachable, which is the exact failure
    this sentinel exists to catch.
    """
    out = sh('/usr/bin/defaults read /Library/Preferences/com.apple.TimeMachine 2>/dev/null')
    if not out or out.startswith('ERROR'):
        return None
    newest, in_array = None, False
    for line in out.splitlines():
        s = line.strip()
        if re.match(r'^(SnapshotDates|BackupDates)\s*=\s*\(', s):
            in_array = True
            continue
        if in_array:
            if s.startswith(')'):
                in_array = False
                continue
            m = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \+0000', s)
            if m:
                try:
                    t = calendar.timegm(time.strptime(m.group(1), '%Y-%m-%d %H:%M:%S'))  # stored UTC
                    newest = t if newest is None else max(newest, t)
                except Exception:
                    pass
    return newest


def _tm_from_mounts():
    """Route 3 — last resort: the dated .backup snapshot the destination currently has mounted."""
    out = sh("/sbin/mount | grep -oE 'com\\.apple\\.TimeMachine\\.[0-9-]+\\.backup'")
    best = None
    for m in re.finditer(r'(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})(\d{2})', out or ''):
        ts = '-'.join(m.groups()[:3]) + ' ' + ':'.join(m.groups()[3:])
        try:
            t = time.mktime(time.strptime(ts, '%Y-%m-%d %H:%M:%S'))
            best = t if best is None else max(best, t)
        except Exception:
            pass
    return best


def tm_last_success_age_hours():
    """Age in hours of the last COMPLETED Time Machine backup, or None if genuinely unknowable.

    HARDENED 2026-09-20. Previously this called `tmutil latestbackup` and nothing else. That
    command requires Full Disk Access, which the launchd runner does not have, so it returned a
    permission error on every run since 2026-09-04 — and the sentinel turned "I am not allowed to
    look" into "Could not determine ... **CRITICAL**". Sixteen days, ~100 CRITICAL entries, four
    per day, while Time Machine was in fact backing up to the NAS every two hours the whole time
    (proven 2026-09-20: newest completed backup was 71 minutes old). A check that cannot tell
    "broken" apart from "blocked" is worse than no check — it trains everyone to ignore it.
    Three independent routes now; the first one that answers wins.
    """
    for route in (_tm_from_tmutil, _tm_from_prefs, _tm_from_mounts):
        try:
            t = route()
        except Exception:
            t = None
        if t:
            return (time.time() - t) / 3600.0
    return None


def thin_local_snapshots():
    # Apple's supported way to reclaim local TM snapshot space once the network copy has landed.
    # Purge-space semantics: ask for a large amount, thinning proportionally what's safe to drop.
    out = sh('tmutil thinlocalsnapshots / 20000000000 4 2>&1', timeout=120)
    return out


def count_dataless_scheduled():
    out = sh(f"find '{SCHED}' -maxdepth 3 -type f -exec ls -lO {{}} + 2>/dev/null | grep -c dataless")
    try:
        return int(out.strip() or 0)
    except Exception:
        return -1


def big_old_downloads():
    out = sh("find ~/Downloads -maxdepth 1 -type f \\( -name '*.dmg' -o -name '*.pkg' \\) -mtime +14 -size +100M -exec ls -lh {} \\; 2>/dev/null")
    rows = []
    for line in out.splitlines():
        parts = line.split(None, 8)
        if len(parts) >= 9:
            rows.append((parts[4], parts[8]))
    return rows


def main():
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    root = df_line('/')
    data = df_line('/System/Volumes/Data')
    data_avail_gib = avail_gib('/System/Volumes/Data')
    tm_age_h = tm_last_success_age_hours()

    thin_result = None
    if tm_age_h is not None and tm_age_h < 24:
        thin_result = thin_local_snapshots()

    dataless_n = count_dataless_scheduled()
    old_installers = big_old_downloads()

    critical_reasons = []
    if data_avail_gib is not None and data_avail_gib < 15:
        critical_reasons.append(f'Data volume free space is only {data_avail_gib} GiB (< 15 GiB threshold).')
    if dataless_n > 0:
        critical_reasons.append(f'{dataless_n} scheduled-task file(s) under ~/Documents/Claude/Scheduled are iCloud-evicted (dataless) right now — this breaks automation silently.')
    if tm_age_h is not None and tm_age_h > 72:
        critical_reasons.append(f'Last successful Time Machine backup was {tm_age_h:.0f}h ago (> 72h threshold).')
    elif tm_age_h is None:
        critical_reasons.append('Could not determine last successful Time Machine backup time.')

    entry = [f'## {NOW}' + (' — CRITICAL' if critical_reasons else ' — OK')]
    entry.append(f'- / : {root["used"]} used / {root["avail"]} avail ({root["pct"]})')
    entry.append(f'- /System/Volumes/Data : {data["used"]} used / {data["avail"]} avail ({data["pct"]})')
    entry.append(f'- Time Machine last success: {"%.1fh ago" % tm_age_h if tm_age_h is not None else "unknown"}')
    if thin_result is not None:
        entry.append(f'- Local snapshot thinning ran (backup <24h old): {thin_result[:200] or "no output"}')
    entry.append(f'- Dataless (iCloud-evicted) files under Scheduled: {dataless_n}')
    if old_installers:
        entry.append(f'- {len(old_installers)} installer file(s) >100MB, >14d old in ~/Downloads (Joshua-only to delete): ' +
                      ', '.join(f'{sz} {os.path.basename(p)}' for sz, p in old_installers[:8]))
    if critical_reasons:
        entry.append('- **ESCALATE**: ' + ' '.join(critical_reasons))
    entry.append('')

    with open(LOG, 'a') as f:
        f.write('\n'.join(entry) + '\n')

    # Keep only the last ~200 entries so this file doesn't grow unbounded
    try:
        text = open(LOG).read()
        blocks = text.split('\n## ')
        if len(blocks) > 200:
            text = blocks[0] + '\n## ' + '\n## '.join(blocks[-200:])
            open(LOG, 'w').write(text)
    except Exception:
        pass

    state = {'lastRun': NOW, 'criticalOpen': bool(critical_reasons), 'reasons': critical_reasons,
              'dataAvailGiB': data_avail_gib, 'datalessCount': dataless_n}
    with open(STATE, 'w') as f:
        json.dump(state, f, indent=1)

    print('CRITICAL' if critical_reasons else 'OK', state)


if __name__ == '__main__':
    main()
