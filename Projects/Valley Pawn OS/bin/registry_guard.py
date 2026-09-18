#!/usr/bin/env python3
"""Registry Guard — Valley Pawn (native Layer-0, additive, 2026-09-16).

WHY: twice now (2026-09-10, 2026-09-16) the Claude desktop app's scheduled-task
registry (scheduled-tasks.json) failed the app's schema validation, the scheduler
loaded ZERO tasks, the sidebar went empty, and the whole Cowork fleet went dark
until a human noticed. On 9/10 the trigger was a `null` written into
lastRunAt/lastScheduledFor (the validator wants string-or-absent). The
`claude-keepalive` agent that should relaunch the app was itself broken (exit 126).

This guard runs OUTSIDE Claude (launchd, pure Python, zero usage) every 5 min:
  1. Locate every registry (local-agent-mode-sessions/*/*/scheduled-tasks.json).
  2. Parse it; count tasks; find any null-valued keys on any task.
  3. Read the app logs (main.log / main1.log) for ZodError since the app started.
  4. If nulls are present -> backup, quiesce app, strip nulls, relaunch, verify.
     If a one-time force flag is present -> quiesce + relaunch (no edit), verify.
  5. Verify recovery: app running AND registry mtime advances (scheduler alive).
  6. DM Joshua (plain language, vp-ops bot) ONLY if recovery failed. Silent when green.

Report (on events / --diag): Valley Pawn OS/fleet/REGISTRY_GUARD.md (newest first)
Heartbeat log:                ~/Library/Logs/valleypawn/registry-guard.log
State:                         ~/Library/Logs/valleypawn/registry_guard_state.json
Force one relaunch:            touch "Valley Pawn OS/fleet/host_queue/.registry_guard_force_relaunch"

Flags: --diag (always write full report)  --dry-run (no edits, no relaunch, no DM)
"""
import datetime as dt
import getpass
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
REPORT = os.path.join(OS_DIR, "fleet/REGISTRY_GUARD.md")
FORCE_FLAG = os.path.join(OS_DIR, "fleet/host_queue/.registry_guard_force_relaunch")
LOG_DIR = os.path.join(HOME, "Library/Logs/valleypawn")
HB_LOG = os.path.join(LOG_DIR, "registry-guard.log")
STATE = os.path.join(LOG_DIR, "registry_guard_state.json")
REGGLOB = os.path.join(HOME, "Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json")
APP_LOGS = [os.path.join(HOME, "Library/Logs/Claude/main.log"),
            os.path.join(HOME, "Library/Logs/Claude/main1.log")]
CLAUDE_BIN = "/Applications/Claude.app/Contents/MacOS/Claude"
JOSHUA_USER = "U03BB52MDSA"
KEYCHAIN_SERVICE = "vp-ops-slack-bot-token"
REPORT_KEEP = 40
RELAUNCH_COOLDOWN_S = 2 * 3600
MIN_TASKS_TO_RELAUNCH = 50   # never relaunch on the strength of a near-empty file
LOG_TAIL_BYTES = 6 * 1024 * 1024

SNAP_DIR = os.path.join(OS_DIR, "fleet/_backups/registry/auto")
LATEST_GOOD = os.path.join(SNAP_DIR, "latest-good.json")
SNAP_KEEP = 60               # rolling snapshots kept (one per change, typically a few per hour)
SNAP_MAX_AGE_DAYS = 7        # never auto-restore from something older than this
WIPE_THRESHOLD = 10          # registry with fewer tasks than this, while latest-good has >=50, is a wipe

DIAG = "--diag" in sys.argv
DRY = "--dry-run" in sys.argv
RESTORE_FROM = None
if "--restore" in sys.argv:
    i = sys.argv.index("--restore")
    RESTORE_FROM = sys.argv[i + 1] if i + 1 < len(sys.argv) else None

os.makedirs(LOG_DIR, exist_ok=True)


def now():
    return dt.datetime.now()


def hb(msg):
    line = now().strftime("%Y-%m-%d %H:%M:%S") + " " + msg
    with open(HB_LOG, "a") as f:
        f.write(line + "\n")
    print(line)


def load_state():
    try:
        return json.load(open(STATE))
    except Exception:
        return {}


def save_state(s):
    if DRY:
        return
    tmp = STATE + ".tmp"
    json.dump(s, open(tmp, "w"), indent=2)
    os.replace(tmp, STATE)


def sh(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return 1, str(e)


# ---------- app process ----------
def app_info():
    rc, out = sh("ps -axo pid=,lstart=,comm= | grep -F '%s' | grep -v grep" % CLAUDE_BIN)
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 7:
            pid = int(parts[0])
            lstart = " ".join(parts[1:6])
            try:
                start = dt.datetime.strptime(lstart, "%a %b %d %H:%M:%S %Y")
            except Exception:
                start = None
            return {"running": True, "pid": pid, "started": start}
    return {"running": False, "pid": None, "started": None}


def scheduled_run_active():
    rc, out = sh("pgrep -f 'claude.*--scheduled|cli_session|claude-code' >/dev/null 2>&1; echo $?")
    return out.strip().endswith("0")


# ---------- registry ----------
def registries():
    return sorted(p for p in glob.glob(REGGLOB) if ".bak" not in os.path.basename(p))


def find_nulls(obj, path="", out=None, depth=0):
    """Return list of dotted paths whose value is None (any depth, capped)."""
    if out is None:
        out = []
    if depth > 6:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = path + "." + str(k) if path else str(k)
            if v is None:
                out.append(p)
            else:
                find_nulls(v, p, out, depth + 1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = "%s[%d]" % (path, i)
            if v is None:
                out.append(p)
            else:
                find_nulls(v, p, out, depth + 1)
    return out


def strip_nulls(obj):
    """Remove None-valued keys from dicts recursively (list elements that are None are left,
    they are not the failure class seen). Returns count removed."""
    n = 0
    if isinstance(obj, dict):
        for k in [k for k, v in obj.items() if v is None]:
            del obj[k]
            n += 1
        for v in obj.values():
            n += strip_nulls(v)
    elif isinstance(obj, list):
        for v in obj:
            n += strip_nulls(v)
    return n


def inspect_registry(path):
    info = {"path": path, "ok": False, "tasks": 0, "enabled": 0, "nulls": [], "error": None,
            "mtime": dt.datetime.fromtimestamp(os.path.getmtime(path)), "size": os.path.getsize(path)}
    try:
        data = json.load(open(path))
        st = data.get("scheduledTasks", [])
        info["ok"] = True
        info["tasks"] = len(st)
        info["enabled"] = sum(1 for t in st if t.get("enabled"))
        info["nulls"] = find_nulls(data)
        info["data"] = data
    except Exception as e:
        info["error"] = "%s: %s" % (type(e).__name__, e)
    return info


# ---------- cron (to know whether the scheduler SHOULD have written since the last write) ----------
def _cron_field_ok(field, value, lo, hi):
    for part in field.split(","):
        step = 1
        if "/" in part:
            part, step = part.split("/", 1)
            try:
                step = int(step)
            except Exception:
                step = 1
        if part == "*":
            a, b = lo, hi
        elif "-" in part:
            try:
                a, b = [int(x) for x in part.split("-", 1)]
            except Exception:
                continue
        else:
            try:
                a = b = int(part)
            except Exception:
                continue
            if step > 1 and "/" in field:
                b = hi
        if a <= value <= b and (value - a) % step == 0:
            return True
    return False


def cron_matches(expr, t):
    f = (expr or "").split()
    if len(f) != 5:
        return False
    mi, h, dom, mon, dow = f
    wd = (t.weekday() + 1) % 7  # cron: 0=Sunday
    dow = dow.replace("7", "0")
    return (_cron_field_ok(mi, t.minute, 0, 59) and _cron_field_ok(h, t.hour, 0, 23)
            and _cron_field_ok(mon, t.month, 1, 12) and _cron_field_ok(dom, t.day, 1, 31)
            and _cron_field_ok(dow, wd, 0, 6))


def expected_dispatch_between(data, start, end):
    """True if any ENABLED task's cron fires in (start, end]. Bounded scan (max 6 h)."""
    tasks = [t for t in data.get("scheduledTasks", []) if t.get("enabled") and t.get("cronExpression")]
    if not tasks:
        return False
    t = end.replace(second=0, microsecond=0)
    floor = max(start, end - dt.timedelta(hours=6))
    while t > floor:
        for task in tasks:
            if cron_matches(task["cronExpression"], t):
                return True
        t -= dt.timedelta(minutes=1)
    return False


# ---------- app logs ----------
TS_RE = re.compile(r"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})(?:\.\d+)?(Z)?")


def parse_ts(line):
    m = TS_RE.search(line[:60])
    if not m:
        return None
    try:
        t = dt.datetime.strptime(m.group(1) + " " + m.group(2), "%Y-%m-%d %H:%M:%S")
        if m.group(3) == "Z":
            t = t + (dt.datetime.now() - dt.datetime.utcnow())
        return t
    except Exception:
        return None


def scan_logs(app_started):
    """Return dict: zod_lines (last 8), zod_total, zod_since_start (bool|None), sched_lines (last 12)."""
    zod, sched = [], []
    for lp in APP_LOGS:
        if not os.path.exists(lp):
            continue
        try:
            size = os.path.getsize(lp)
            with open(lp, "rb") as f:
                if size > LOG_TAIL_BYTES:
                    f.seek(size - LOG_TAIL_BYTES)
                blob = f.read().decode("utf-8", "replace")
        except Exception:
            continue
        for line in blob.splitlines():
            if "ZodError" in line:
                zod.append((lp, line[:400]))
            elif "scheduled-tasks" in line or "scheduledTasks" in line or "Scheduler" in line or "scheduler" in line:
                if "Loaded" in line or "loaded" in line or "tasks" in line or "error" in line.lower():
                    sched.append((lp, line[:300]))
    since = None
    if zod:
        since = False
        for lp, line in zod:
            t = parse_ts(line)
            if t is None:
                since = None if since is False else since
                continue
            if app_started is None or t >= app_started - dt.timedelta(seconds=30):
                since = True
                break
        if since is None:
            since = True  # ZodError present but timestamps unparseable: assume live
    return {"zod_lines": zod[-8:], "zod_total": len(zod), "zod_since_start": since,
            "sched_lines": sched[-12:]}


# ---------- actions ----------
def quiesce_app():
    """Quit Claude.app cleanly, waiting for any active scheduled run first (proven 9/4, 9/10 pattern)."""
    for i in range(6):
        if scheduled_run_active():
            hb("scheduled run active, waiting (%d/6)" % (i + 1))
            time.sleep(60)
        else:
            break
    sh("osascript -e 'tell application \"Claude\" to quit'", timeout=30)
    time.sleep(8)
    sh("pkill -TERM -f 'Claude\\.app' || true")
    time.sleep(6)
    sh("pkill -KILL -f 'Claude\\.app' || true")
    time.sleep(4)
    return not app_info()["running"]


def relaunch_app():
    sh("open -ga Claude")
    for i in range(12):
        time.sleep(5)
        if app_info()["running"]:
            return True
    sh("open -a Claude")
    time.sleep(15)
    return app_info()["running"]


def wait_registry_written(path, old_mtime, wait_s=240):
    """Scheduler alive => it rewrites the registry shortly after launch."""
    deadline = time.time() + wait_s
    while time.time() < deadline:
        time.sleep(10)
        try:
            if os.path.getmtime(path) > old_mtime:
                return True
        except Exception:
            pass
    return False


def backup(path, tag):
    dst = path + ".bak-%s-%s" % (tag, now().strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(path, dst)
    return dst


def write_registry(path, data):
    tmp = path + ".guard-tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


# ---------- snapshots (defense against the app wiping the registry, 2026-09-16) ----------
def snapshot_registry(r):
    """Keep a rolling copy of every good registry state so a wipe can be undone. Returns event or None."""
    if not (r and r["ok"] and r["tasks"] >= MIN_TASKS_TO_RELAUNCH) or DRY:
        return None
    os.makedirs(SNAP_DIR, exist_ok=True)
    try:
        cur = open(r["path"], "rb").read()
        if os.path.exists(LATEST_GOOD) and open(LATEST_GOOD, "rb").read() == cur:
            return None
        stamp = now().strftime("%Y%m%d-%H%M%S")
        dst = os.path.join(SNAP_DIR, "scheduled-tasks-%s.json" % stamp)
        open(dst, "wb").write(cur)
        tmp = LATEST_GOOD + ".tmp"
        open(tmp, "wb").write(cur)
        os.replace(tmp, LATEST_GOOD)
        snaps = sorted(f for f in os.listdir(SNAP_DIR) if f.startswith("scheduled-tasks-"))
        for f in snaps[:-SNAP_KEEP]:
            try:
                os.remove(os.path.join(SNAP_DIR, f))
            except Exception:
                pass
        return "snapshot saved (%d tasks) -> %s" % (r["tasks"], os.path.basename(dst))
    except Exception as e:
        return "snapshot failed: %s" % e


def account_logged_out():
    """True if the newest account line in main.log says the user is logged out (a restore would be wiped again)."""
    lp = APP_LOGS[0]
    if not os.path.exists(lp):
        return False
    try:
        size = os.path.getsize(lp)
        with open(lp, "rb") as f:
            if size > 2 * 1024 * 1024:
                f.seek(size - 2 * 1024 * 1024)
            blob = f.read().decode("utf-8", "replace")
    except Exception:
        return False
    last = None
    for line in blob.splitlines():
        if "[account]" in line or "account details provided" in line or "verified sign-in" in line:
            last = line
    return bool(last) and ("logged out" in last)


# ---------- Slack (failure only) ----------
def slack_token():
    try:
        r = subprocess.run(["security", "find-generic-password", "-s", KEYCHAIN_SERVICE,
                            "-a", getpass.getuser(), "-w"], capture_output=True, text=True, timeout=10)
        t = r.stdout.strip()
        if t.startswith("xoxb-"):
            return t
    except Exception:
        pass
    t = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    return t if t.startswith("xoxb-") else None


def dm_joshua(text):
    if DRY:
        hb("DRY DM: " + text)
        return
    tok = slack_token()
    if not tok:
        hb("no slack token; DM skipped: " + text)
        return
    try:
        req = urllib.request.Request("https://slack.com/api/conversations.open",
                                     data=json.dumps({"users": JOSHUA_USER}).encode(),
                                     headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
        ch = json.load(urllib.request.urlopen(req, timeout=20))["channel"]["id"]
        req = urllib.request.Request("https://slack.com/api/chat.postMessage",
                                     data=json.dumps({"channel": ch, "text": text}).encode(),
                                     headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=20).read()
        hb("DM sent")
    except Exception as e:
        hb("DM failed: %s" % e)


# ---------- report ----------
def write_report(section):
    if DRY:
        print(section)
        return
    head = ("# Registry Guard — rolling log\n\nWritten by `bin/registry_guard.py` (native launchd "
            "`com.valleypawn.registry-guard`, every 5 min, zero Claude usage). Newest first, last %d "
            "event entries kept. Heartbeats go to ~/Library/Logs/valleypawn/registry-guard.log.\n\n" % REPORT_KEEP)
    old = ""
    if os.path.exists(REPORT):
        old = open(REPORT).read()
        i = old.find("\n## ")
        old = old[i + 1:] if i >= 0 else ""
    entries = [e for e in ("\n" + old).split("\n## ") if e.strip()]
    entries = entries[:REPORT_KEEP - 1]
    body = section + "\n\n" + "\n\n".join("## " + e.strip() for e in entries)
    tmp = REPORT + ".tmp"
    open(tmp, "w").write(head + body.strip() + "\n")
    os.replace(tmp, REPORT)


def main():
    state = load_state()
    app = app_info()
    regs = [inspect_registry(p) for p in registries()]
    logs = scan_logs(app["started"])
    force = os.path.exists(FORCE_FLAG)
    lines = []
    events = []
    lines.append("- App running: %s (pid %s, started %s)" % (app["running"], app["pid"], app["started"]))
    lines.append("- Registries found: %d" % len(regs))
    for r in regs:
        if r["ok"]:
            lines.append("- `%s` — %d tasks / %d enabled, %d null value(s), %d bytes, mtime %s"
                         % (r["path"].replace(HOME, "~"), r["tasks"], r["enabled"], len(r["nulls"]), r["size"],
                            r["mtime"].strftime("%Y-%m-%d %H:%M:%S")))
            for n in r["nulls"][:20]:
                lines.append("    - null at `%s`" % n)
        else:
            lines.append("- `%s` — PARSE FAILED: %s" % (r["path"].replace(HOME, "~"), r["error"]))
    lines.append("- ZodError lines in app logs: %d (since app start: %s)" % (logs["zod_total"], logs["zod_since_start"]))
    for lp, l in logs["zod_lines"]:
        lines.append("    - `%s`: %s" % (os.path.basename(lp), l.replace("`", "'")))
    if logs["sched_lines"]:
        lines.append("- Scheduler-related log lines (last %d):" % len(logs["sched_lines"]))
        for lp, l in logs["sched_lines"]:
            lines.append("    - `%s`: %s" % (os.path.basename(lp), l.replace("`", "'")))
    lines.append("- Force-relaunch flag present: %s" % force)

    # ----- decide -----
    nulls_any = any(r["ok"] and r["nulls"] for r in regs)
    parse_fail = [r for r in regs if not r["ok"]]
    biggest = max((r["tasks"] for r in regs if r["ok"]), default=0)
    last_relaunch = state.get("last_relaunch_ts", 0)
    cooled = (time.time() - last_relaunch) > RELAUNCH_COOLDOWN_S
    need_relaunch = False
    reason = ""
    # scheduler-silence signal: a healthy scheduler rewrites the registry every few minutes
    # (lastRunAt/lastScheduledFor of 5-min tasks). App up >20 min with no write for >90 min = dead.
    main_r = max((r for r in regs if r["ok"]), key=lambda r: r["tasks"], default=None)
    stale_min = int((now() - main_r["mtime"]).total_seconds() // 60) if main_r else None
    app_up_min = int((now() - app["started"]).total_seconds() // 60) if app["started"] else None
    lines.append("- Registry last written %s min ago; app up %s min" % (stale_min, app_up_min))
    if not app["running"] and not DRY:
        events.append("Claude.app not running — launching it")
        hb("app down, launching")
        if relaunch_app():
            events.append("Claude.app launched")
            app = app_info()
        else:
            events.append("Claude.app did not start")
    # snapshot every good state; detect a wipe (app logout/login RESET, 2026-09-16) and pick a restore source
    snap_ev = snapshot_registry(main_r)
    if snap_ev:
        events.append(snap_ev)
    restore_src = None
    if RESTORE_FROM:
        restore_src = RESTORE_FROM
    elif main_r and main_r["tasks"] < WIPE_THRESHOLD and os.path.exists(LATEST_GOOD):
        try:
            lg = inspect_registry(LATEST_GOOD)
            age_d = (now() - lg["mtime"]).total_seconds() / 86400
            if lg["ok"] and lg["tasks"] >= MIN_TASKS_TO_RELAUNCH and age_d <= SNAP_MAX_AGE_DAYS:
                restore_src = LATEST_GOOD
                lines.append("- WIPE detected: registry has %d tasks, latest-good has %d (%.1f days old)"
                             % (main_r["tasks"], lg["tasks"], age_d))
            else:
                events.append("registry looks wiped (%d tasks) but latest-good unusable (ok=%s tasks=%d age=%.1fd)"
                              % (main_r["tasks"], lg["ok"], lg["tasks"], age_d))
        except Exception as e:
            events.append("latest-good check failed: %s" % e)
    if restore_src:
        rs = inspect_registry(restore_src)
        if not (rs["ok"] and rs["tasks"] >= MIN_TASKS_TO_RELAUNCH and not rs["nulls"]):
            events.append("restore source rejected: ok=%s tasks=%d nulls=%d" % (rs["ok"], rs["tasks"], len(rs["nulls"])))
            restore_src = None
        elif account_logged_out():
            events.append("restore deferred: app reports the user is logged out (the app resets the registry on login)")
            restore_src = None
    if restore_src:
        need_relaunch, reason = True, "restore registry from %s (%d tasks)" % (os.path.basename(restore_src), rs["tasks"])
    elif nulls_any:
        need_relaunch, reason = True, "null value(s) in registry (validator rejects the whole file)"
    elif force:
        need_relaunch, reason = True, "one-time force flag"
    elif (app_up_min is not None and app_up_min > 20 and stale_min is not None and stale_min > 90
          and main_r and main_r["enabled"] > 0
          and expected_dispatch_between(main_r["data"], main_r["mtime"], now() - dt.timedelta(minutes=15))):
        need_relaunch, reason = True, ("scheduler silent: registry not rewritten for %d min while app up %d min "
                                       "and enabled tasks were due" % (stale_min, app_up_min))
    elif logs["zod_since_start"] and app["running"]:
        # ZodError with no null we can fix: report loudly, do not loop-relaunch
        events.append("ZodError present since app start but no null found — needs a session to read the error text above")
    if need_relaunch and state.get("consecutive_fail", 0) >= 2 and not force:
        events.append("relaunch skipped: 2 consecutive relaunches did not restore the scheduler — waiting for a session")
        need_relaunch = False
    if parse_fail:
        events.append("registry parse failure — NOT auto-repaired, restore from newest .bak by hand")
        need_relaunch = False
    if need_relaunch and biggest < MIN_TASKS_TO_RELAUNCH and not restore_src:
        events.append("relaunch skipped: largest registry has only %d tasks (< %d)" % (biggest, MIN_TASKS_TO_RELAUNCH))
        need_relaunch = False
    if need_relaunch and not cooled and not force:
        events.append("relaunch skipped: cooldown (last relaunch %s)" % dt.datetime.fromtimestamp(last_relaunch))
        need_relaunch = False

    outcome = "green"
    if need_relaunch and not DRY:
        outcome = "repair"
        hb("REPAIR: %s" % reason)
        events.append("Action: quiesce app -> %s -> relaunch (%s)" % (
            "restore" if restore_src else ("strip nulls" if nulls_any else "no edit"), reason))
        if app["running"] and not quiesce_app():
            events.append("could not quit Claude.app cleanly; aborting edit, relaunching")
            relaunch_app()
            outcome = "failed"
        else:
            if restore_src and main_r:
                tgt = main_r["path"]
                m1 = os.path.getmtime(tgt); time.sleep(20); m2 = os.path.getmtime(tgt)
                if m1 != m2:
                    events.append("registry still being written after quit — restore skipped")
                else:
                    lost = [t.get("id") for t in main_r["data"].get("scheduledTasks", [])]
                    b = backup(tgt, "wiped")
                    shutil.copy2(restore_src, tgt)
                    chk = inspect_registry(tgt)
                    events.append("RESTORED %d tasks from %s (backup of wiped file `%s`); re-parse ok=%s; ids that existed only in the wiped file: %s"
                                  % (chk["tasks"], os.path.basename(restore_src), os.path.basename(b), chk["ok"], lost or "none"))
                    state["last_restore"] = {"when": now().isoformat(), "src": restore_src, "tasks": chk["tasks"]}
                    save_state(state)
            elif nulls_any:
                for r in regs:
                    if r["ok"] and r["nulls"]:
                        # make sure nothing is still writing it
                        m1 = os.path.getmtime(r["path"]); time.sleep(20); m2 = os.path.getmtime(r["path"])
                        if m1 != m2:
                            events.append("registry still being written after quit — skipped edit")
                            continue
                        b = backup(r["path"], "nullfix")
                        removed = strip_nulls(r["data"])
                        write_registry(r["path"], r["data"])
                        chk = inspect_registry(r["path"])
                        events.append("stripped %d null(s), backup `%s`, re-parse ok=%s tasks=%d nulls=%d"
                                      % (removed, os.path.basename(b), chk["ok"], chk["tasks"], len(chk["nulls"])))
            pre = {r["path"]: os.path.getmtime(r["path"]) for r in regs}
            if force:
                try:
                    os.remove(FORCE_FLAG)
                except Exception:
                    pass
            ok = relaunch_app()
            state["last_relaunch_ts"] = time.time()
            save_state(state)
            if not ok:
                events.append("Claude.app did NOT come back after relaunch attempts")
                outcome = "failed"
            else:
                # verify the scheduler actually loaded: registry gets rewritten within minutes
                main_reg = max(regs, key=lambda r: r["tasks"])["path"] if regs else None
                alive = wait_registry_written(main_reg, pre.get(main_reg, 0)) if main_reg else False
                post = scan_logs(app_info()["started"])
                events.append("post-relaunch: app running, registry rewritten by scheduler=%s, ZodError since restart=%s"
                              % (alive, post["zod_since_start"]))
                if not alive or post["zod_since_start"]:
                    outcome = "failed"
                    for lp, l in post["zod_lines"][-3:]:
                        events.append("post-relaunch log: %s" % l.replace("`", "'"))
                elif restore_src:
                    dm_joshua("The scheduled-task list had been cleared by the Claude app; I restored it (%d tasks) and "
                              "everything is back on schedule." % inspect_registry(main_reg)["tasks"])
        if outcome == "failed":
            state["consecutive_fail"] = state.get("consecutive_fail", 0) + 1
            save_state(state)
            key = "fail-" + now().strftime("%Y-%m-%d")
            if state.get("last_dm_key") != key:
                dm_joshua("The scheduled-task list did not come back after I restarted the Claude app. "
                          "Details are in Valley Pawn OS/fleet/REGISTRY_GUARD.md — a session needs to look.")
                state["last_dm_key"] = key
                save_state(state)
    elif need_relaunch and DRY:
        events.append("DRY RUN: would repair (%s)" % reason)
    elif outcome == "green" and not need_relaunch and stale_min is not None and stale_min <= 90:
        if state.get("consecutive_fail"):
            state["consecutive_fail"] = 0
            save_state(state)

    # heartbeat / report
    summary = "%s | app=%s | regs=%d | tasks=%d | nulls=%s | zod_since_start=%s" % (
        outcome, app["running"], len(regs), biggest, nulls_any, logs["zod_since_start"])
    hb(summary)
    if DIAG or outcome != "green" or events:
        title = "## %s — %s" % (now().strftime("%Y-%m-%d %H:%M"), outcome.upper())
        sec = title + "\n\n" + "\n".join(lines)
        if events:
            sec += "\n\n**Events**\n" + "\n".join("- " + e for e in events)
        write_report(sec)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        hb("CRASH: %s: %s" % (type(e).__name__, e))
        import traceback
        hb(traceback.format_exc().replace("\n", " | "))
        sys.exit(1)
