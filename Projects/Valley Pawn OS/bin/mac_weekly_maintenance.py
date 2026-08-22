#!/usr/bin/env python3
"""mac_weekly_maintenance.py — weekly performance maintenance (added 2026-08-21).

Runs Sundays 4:45 AM via launchd com.valleypawn.mac-maintenance (before the
Bravo corridor, after the 3:30 AM index refresh window). Duties:
  1. Health snapshot: load, swap, disk free, process count.
  2. Thin Time Machine local snapshots (frees purgeable space on the 92%-full disk).
  3. Clean known-safe temp/junk: Unified Search _ocr_tmp/_tmp older than 14 days,
     valleypawn logs older than 30 days, /tmp usearch scratch logs.
  4. One short plain-language DM to Joshua with the numbers (weekly heartbeat),
     flagged clearly if disk <40GB free or swap >12GB.
Deliberately does NOT touch: Parallels, Claude app data, Chrome profiles, Trash,
Documents, any .bak-* backups (those are policy), Mail stores.
"""
import os, json, time, subprocess, urllib.request

HOME = os.path.expanduser("~")
LOGDIR = os.path.join(HOME, "Library/Logs/valleypawn")
LOG = os.path.join(LOGDIR, "mac_maintenance.log")
US = os.path.join(HOME, "Documents/Claude/Projects/Unified Search")
JOSHUA_USER = "U03BB52MDSA"
KEYCHAIN_SERVICE = "vp-ops-slack-bot-token"


def log(msg):
    os.makedirs(LOGDIR, exist_ok=True)
    with open(LOG, "a") as f:
        f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg))


def sh(cmd, timeout=600):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              timeout=timeout).stdout.strip()
    except Exception as e:
        log("cmd failed: %s (%s)" % (cmd, e))
        return ""


def gb_free():
    out = sh("df -g /System/Volumes/Data | tail -1")
    try:
        return int(out.split()[3])
    except Exception:
        return -1


def main():
    log("=== weekly maintenance start ===")
    before_free = gb_free()

    # 2) thin TM local snapshots (safe: TM re-creates as needed; frees purgeable)
    thinned = sh("tmutil thinlocalsnapshots / 999999999999 4", timeout=1800)
    log("tmutil thin: %s" % (thinned or "no output"))

    # 3) targeted temp cleanup (age-gated, known-safe paths only)
    cleaned = []
    for path, days in ((os.path.join(US, "_ocr_tmp"), 14),
                       (os.path.join(US, "_tmp"), 14),
                       (os.path.join(US, "_ocr_work"), 14)):
        if os.path.isdir(path):
            n = sh("find '%s' -type f -mtime +%d -delete -print 2>/dev/null | wc -l" % (path, days))
            cleaned.append("%s: %s files" % (os.path.basename(path), n.strip()))
    n = sh("find '%s' -name '*.log' -mtime +30 -delete -print 2>/dev/null | wc -l" % LOGDIR)
    cleaned.append("old vp logs: %s" % n.strip())
    sh("rm -f /tmp/usearch_refresh_run.log /tmp/us1.log /tmp/usstats.log /tmp/dusweep.log /tmp/locktest.log 2>/dev/null")
    log("cleanup: " + "; ".join(cleaned))

    # 1/4) snapshot + DM
    after_free = gb_free()
    load = sh("sysctl -n vm.loadavg").strip("{} ")
    swap = sh("sysctl -n vm.swapusage")
    nproc = sh("ps -Ae | wc -l").strip()
    swap_used_mb = 0.0
    try:
        swap_used_mb = float(swap.split("used = ")[1].split("M")[0])
    except Exception:
        pass
    summary = ("Weekly Mac health: %sGB free (was %sGB), load %s, swap used %.1fGB, "
               "%s processes." % (after_free, before_free, load.split()[0], swap_used_mb / 1024, nproc))
    warn = ""
    if after_free >= 0 and after_free < 40:
        warn += " ⚠️ Disk is getting full (<40GB free) — worth clearing space soon."
    if swap_used_mb > 12288:
        warn += " ⚠️ Memory has been tight this week (heavy swap) — a restart would help."
    log(summary + warn)

    tok = sh("security find-generic-password -s %s -w 2>/dev/null" % KEYCHAIN_SERVICE) \
          or os.environ.get("SLACK_BOT_TOKEN", "").strip()
    if tok:
        try:
            def call(method, payload):
                req = urllib.request.Request(
                    "https://slack.com/api/" + method,
                    data=json.dumps(payload).encode(),
                    headers={"Authorization": "Bearer " + tok,
                             "Content-Type": "application/json; charset=utf-8"})
                return json.load(urllib.request.urlopen(req, timeout=15))
            ch = call("conversations.open", {"users": JOSHUA_USER})
            if ch.get("ok"):
                call("chat.postMessage", {"channel": ch["channel"]["id"],
                                          "text": summary + warn})
        except Exception as e:
            log("DM failed: %s" % e)
    log("=== weekly maintenance done ===")


if __name__ == "__main__":
    main()
