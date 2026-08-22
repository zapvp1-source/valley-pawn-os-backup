#!/usr/bin/env python3
"""Fleet Health Sentinel — Valley Pawn (additive, 2026-08-21).

Watches the ENTIRE Cowork scheduled-task fleet + native launchd agents from
OUTSIDE Claude (pure Python, zero usage-cap exposure). Catches the failure
class that has burned Joshua repeatedly: a task fires (or silently doesn't)
and nobody notices until a report is missing days later.

Checks, every run:
  1. Every ENABLED registry task with a cron: did it actually start on time?
     (cron-aware "previous expected fire" vs lastRunAt, with grace period;
     new tasks aren't flagged until they've genuinely missed a slot)
  2. Usage-cap skip burst: recordedSkips growth rate since last sentinel run
  3. Native launchd agents: loaded? last exit status 0?
  4. Claude.app process alive (the keepalive agent should keep it up)
  5. Bravo morning-pull certificate for today exists (morning run only)

Output:
  - Rolling report: Valley Pawn OS/FLEET_HEALTH.md (newest first, capped)
  - ONE plain-language Slack DM to Joshua (D03BHQH5VGT) ONLY when something
    is wrong that hasn't already been alerted (per-occurrence dedup).
    Silent when green. Never posts to any team channel (Failure Policy v2).

Token: macOS Keychain service 'vp-ops-slack-bot-token' (same chain as
vp-ops common.py), fallback env SLACK_BOT_TOKEN / known config files.

Run manually:  python3 fleet_health_sentinel.py [--dry-run]
Installed as:  ~/Library/LaunchAgents/com.valleypawn.fleet-health.plist
               (daily 10:15 AM + 9:45 PM local)
"""

import datetime as dt
import getpass
import glob
import json
import os
import re
import subprocess
import sys
import urllib.request

HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
REPORT = os.path.join(OS_DIR, "FLEET_HEALTH.md")
STATE = os.path.join(OS_DIR, ".fleet_health_state.json")
LOG_DIR = os.path.join(OS_DIR, "logs")
REGGLOB = os.path.join(
    HOME, "Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json"
)
BRAVO_LOGS = os.path.join(HOME, "Documents/Claude/Projects/Bravo Data Extraction/logs")
JOSHUA_USER = "U03BB52MDSA"  # DM channel is opened via conversations.open (the
                             # vp-ops bot has its own DM channel with Joshua —
                             # the D03BHQH5VGT id belongs to a different app)
KEYCHAIN_SERVICE = "vp-ops-slack-bot-token"

GRACE_MIN = 90          # minutes after an expected fire before a task is "missed"
MAX_LOOKBACK_DAYS = 400  # cron prev-fire search horizon (covers annual tasks)
SKIP_RATE_ALERT = 40     # skips/hour sustained since last sentinel run
SKIP_MIN_DELTA = 200     # and at least this many new skips, to avoid tiny-window noise
REPORT_KEEP = 30         # rolling report entries to keep

DRY = "--dry-run" in sys.argv     # print DM instead of sending; don't save state
SEED = "--seed" in sys.argv       # real run but suppress DM (baseline known issues)


# ---------------------------------------------------------------- cron engine
def _expand(field, lo, hi):
    """Expand one cron field to a set of ints. Supports * , - / and plain ints."""
    vals = set()
    for part in field.split(","):
        part = part.strip()
        step = 1
        if "/" in part:
            part, s = part.split("/", 1)
            step = int(s)
        if part in ("*", ""):
            start, end = lo, hi
        elif "-" in part:
            a, b = part.split("-", 1)
            start, end = int(a), int(b)
        else:
            start = int(part)
            end = hi if step != 1 else start  # "5/2" means start at 5, step to hi
        vals.update(range(start, end + 1, step))
    return {v for v in vals if lo <= v <= hi}


def parse_cron(expr):
    f = expr.split()
    if len(f) != 5:
        return None
    try:
        minute = _expand(f[0], 0, 59)
        hour = _expand(f[1], 0, 23)
        dom = _expand(f[2], 1, 31)
        mon = _expand(f[3], 1, 12)
        dow = {v % 7 for v in _expand(f[4], 0, 7)}  # 0 and 7 both Sunday
        dom_star = f[2].strip() == "*"
        dow_star = f[4].strip() == "*"
        return minute, hour, dom, mon, dow, dom_star, dow_star
    except (ValueError, TypeError):
        return None


def cron_matches(c, t):
    minute, hour, dom, mon, dow, dom_star, dow_star = c
    if t.minute not in minute or t.hour not in hour or t.month not in mon:
        return False
    dom_ok = t.day in dom
    dow_ok = ((t.weekday() + 1) % 7) in dow  # python Mon=0 -> cron Sun=0
    if dom_star and dow_star:
        return True
    if dom_star:
        return dow_ok
    if dow_star:
        return dom_ok
    return dom_ok or dow_ok  # standard cron OR semantics


def prev_fire(expr, before):
    """Most recent cron fire time strictly before `before` (local). None if none in horizon."""
    c = parse_cron(expr)
    if c is None:
        return None
    t = before.replace(second=0, microsecond=0)
    minute_set, hour_set = c[0], c[1]
    # walk back day by day, then scan matching hours/minutes within the day
    for dback in range(MAX_LOOKBACK_DAYS + 1):
        day = (t - dt.timedelta(days=dback)).date()
        # day-level check (hour/minute drawn from the sets always match themselves)
        if not cron_matches(c, dt.datetime.combine(day, dt.time(min(hour_set), min(minute_set)))):
            continue
        for h in sorted(hour_set, reverse=True):
            for m in sorted(minute_set, reverse=True):
                cand = dt.datetime.combine(day, dt.time(h, m))
                if cand >= t:
                    continue
                if cron_matches(c, cand):
                    return cand
    return None


# ---------------------------------------------------------------- slack
def get_token():
    try:
        r = subprocess.run(
            ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE,
             "-a", getpass.getuser(), "-w"],
            capture_output=True, text=True, timeout=10)
        tok = r.stdout.strip()
        if tok.startswith("xoxb-"):
            return tok
    except Exception:
        pass
    tok = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    if tok.startswith("xoxb-"):
        return tok
    for p in (os.path.join(HOME, "Documents/Claude/Projects/Bravo Data Extraction/slack_config.json"),
              os.path.join(HOME, ".vp_slack_config.json")):
        try:
            d = json.load(open(p))
            t = (d.get("SLACK_BOT_TOKEN") or d.get("slack_bot_token") or "").strip()
            if t.startswith("xoxb-"):
                return t
        except Exception:
            continue
    return None


def _slack_call(token, method, payload):
    req = urllib.request.Request(
        "https://slack.com/api/" + method,
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "application/json; charset=utf-8"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())


def slack_dm(text):
    if DRY:
        print("[dry-run] would DM:\n" + text)
        return True
    token = get_token()
    if not token:
        print("ERROR: no Slack token found; cannot DM. Report file still written.")
        return False
    try:
        opened = _slack_call(token, "conversations.open", {"users": JOSHUA_USER})
        if not opened.get("ok"):
            print("Slack conversations.open error: " + str(opened.get("error")))
            return False
        channel = opened["channel"]["id"]
        body = _slack_call(token, "chat.postMessage", {"channel": channel, "text": text})
        if not body.get("ok"):
            print("Slack API error: " + str(body.get("error")))
            return False
        return True
    except Exception as e:
        print("Slack network error: " + str(e))
        return False


# ---------------------------------------------------------------- checks
def load_registry():
    files = sorted(glob.glob(REGGLOB), key=os.path.getmtime, reverse=True)
    if not files:
        return None, [], {}
    d = json.load(open(files[0]))
    return files[0], d.get("scheduledTasks", []), d.get("recordedSkips", {})


def parse_iso(s):
    if not s:
        return None
    try:
        t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return t.astimezone().replace(tzinfo=None)  # to local naive
    except Exception:
        return None


def check_tasks(tasks, now, state):
    """Return (issues, alerted_updates). Dedup per (task, expected-fire)."""
    issues = []
    already = state.get("alerted", {})
    new_alerted = dict(already)
    for t in tasks:
        if not t.get("enabled"):
            continue
        expr = t.get("cronExpression")
        tid = t.get("id", "?")
        if not expr:
            # one-time task: flag if fireAt long past with no run
            fire_at = parse_iso(t.get("fireAt") or t.get("lastScheduledFor"))
            continue  # one-times routinely keep stale lastScheduledFor; skip
        exp = prev_fire(expr, now - dt.timedelta(minutes=GRACE_MIN))
        if exp is None:
            continue
        created = t.get("createdAt")
        if created:
            created_dt = dt.datetime.fromtimestamp(created / 1000.0)
            if created_dt > exp:
                continue  # task didn't exist yet at that slot
        last = parse_iso(t.get("lastRunAt"))
        if last is not None and last >= exp - dt.timedelta(minutes=10):
            continue  # ran on (or after) the expected slot
        key = tid + "|" + exp.isoformat()
        line = "'{}' (cron {}) missed its {} run — last started {}".format(
            tid, expr, exp.strftime("%a %b %-d %-I:%M %p"),
            last.strftime("%a %b %-d %-I:%M %p") if last else "NEVER")
        issues.append({"key": key, "line": line, "new": key not in already})
        new_alerted[key] = now.isoformat()
    # prune dedup memory older than 14 days
    cutoff = (now - dt.timedelta(days=14)).isoformat()
    new_alerted = {k: v for k, v in new_alerted.items() if v >= cutoff}
    return issues, new_alerted


def check_skips(skips, now, state):
    total = sum(len(v) for v in skips.values())
    prev = state.get("skip_total")
    prev_ts = parse_iso(state.get("skip_ts"))
    line = None
    if prev is not None and prev_ts is not None and total > prev:
        hours = max((now - prev_ts).total_seconds() / 3600.0, 0.1)
        rate = (total - prev) / hours
        if rate >= SKIP_RATE_ALERT and (total - prev) >= SKIP_MIN_DELTA:
            line = ("usage-cap skips climbing: +{} since {} (~{:.0f}/hr) — tasks are being "
                    "throttled right now".format(total - prev, prev_ts.strftime("%a %-I:%M %p"), rate))
    return total, line


def check_launchd():
    issues = []
    try:
        out = subprocess.run(["launchctl", "list"], capture_output=True, text=True, timeout=15).stdout
    except Exception as e:
        return ["could not query launchctl: " + str(e)], set()
    loaded = {}
    for l in out.splitlines():
        parts = l.split()
        if len(parts) == 3 and ("valleypawn" in parts[2] or "vpops" in parts[2]):
            loaded[parts[2]] = parts[1]  # label -> last exit status
    for label, status in loaded.items():
        if status not in ("0", "-"):
            issues.append("launchd agent {} last exited with status {}".format(label, status))
    for p in glob.glob(os.path.join(HOME, "Library/LaunchAgents/com.valleypawn*.plist")):
        label = os.path.basename(p)[:-6]
        if label not in loaded:
            issues.append("launchd agent {} is installed but NOT loaded".format(label))
    return issues, set(loaded)


def check_claude_app():
    try:
        r = subprocess.run(["pgrep", "-f", "Claude.app/Contents"], capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            return "Claude app is NOT running — scheduled tasks cannot fire (keepalive should restart it)"
    except Exception:
        pass
    return None


def check_morning_cert(now):
    if now.hour >= 12 or now.hour < 8:
        return None  # only meaningful on the morning run
    cert = os.path.join(BRAVO_LOGS, "_morning_pull_status_{}.txt".format(now.date().isoformat()))
    if not os.path.exists(cert):
        return "no Bravo morning-pull certificate for today ({}) — morning reports may be missing".format(
            now.date().isoformat())
    return None


# ---------------------------------------------------------------- report
def write_report(now, sections, ok):
    os.makedirs(OS_DIR, exist_ok=True)
    header = "## {} — {}\n\n".format(now.strftime("%Y-%m-%d %H:%M"), "ALL GREEN" if ok else "ISSUES FOUND")
    body = header + ("\n".join("- " + s for s in sections) + "\n\n" if sections else "Nothing to report.\n\n")
    old = ""
    if os.path.exists(REPORT):
        old = open(REPORT, encoding="utf-8", errors="ignore").read()
        # strip title, keep entries
        m = re.split(r"^## ", old, flags=re.M)
        entries = ["## " + e for e in m[1:]][: REPORT_KEEP - 1]
        old = "\n".join(entries)
    title = ("# Fleet Health — rolling sentinel log\n\n"
             "Written by `bin/fleet_health_sentinel.py` (native launchd, no Claude usage). "
             "Newest first, last {} runs kept. DM alerts go to Joshua only when an issue "
             "is first detected.\n\n".format(REPORT_KEEP))
    open(REPORT, "w", encoding="utf-8").write(title + body + old)


def main():
    now = dt.datetime.now()
    state = {}
    if os.path.exists(STATE):
        try:
            state = json.load(open(STATE))
        except Exception:
            state = {}

    reg_path, tasks, skips = load_registry()
    sections = []
    dm_lines = []

    if reg_path is None:
        sections.append("REGISTRY NOT FOUND — cannot check scheduled tasks")
        dm_lines.append("I can't find the scheduled-task registry file at all")
        task_issues, new_alerted = [], state.get("alerted", {})
        skip_total = state.get("skip_total", 0)
    else:
        task_issues, new_alerted = check_tasks(tasks, now, state)
        for i in task_issues:
            sections.append(i["line"])
            if i["new"]:
                dm_lines.append(i["line"])
        skip_total, skip_line = check_skips(skips, now, state)
        if skip_line:
            sections.append(skip_line)
            dm_lines.append(skip_line)

    ld_issues, _loaded = check_launchd()
    for l in ld_issues:
        sections.append(l)
        key = "launchd|" + l
        if key not in state.get("alerted", {}):
            dm_lines.append(l)
            new_alerted[key] = now.isoformat()

    app_issue = check_claude_app()
    if app_issue:
        sections.append(app_issue)
        dm_lines.append(app_issue)

    cert_issue = check_morning_cert(now)
    if cert_issue:
        sections.append(cert_issue)
        key = "cert|" + now.date().isoformat()
        if key not in state.get("alerted", {}):
            dm_lines.append(cert_issue)
            new_alerted[key] = now.isoformat()

    ok = not sections
    write_report(now, sections, ok)

    if dm_lines and not SEED:
        msg = "⚠️ Task fleet check — {}: {} issue{} need attention:\n".format(
            now.strftime("%a %b %-d %-I:%M %p"), len(dm_lines), "" if len(dm_lines) == 1 else "s")
        msg += "\n".join("• " + l for l in dm_lines[:15])
        if len(dm_lines) > 15:
            msg += "\n• …and {} more (see FLEET_HEALTH.md)".format(len(dm_lines) - 15)
        slack_dm(msg)

    state_out = {"alerted": new_alerted, "skip_total": skip_total, "skip_ts": now.isoformat()}
    if not DRY:
        json.dump(state_out, open(STATE, "w"), indent=1)
    print("fleet_health_sentinel: {} — {} issue(s), {} newly alerted".format(
        now.isoformat(timespec="minutes"), len(sections), len(dm_lines)))
    for s in sections:
        print("  - " + s)


if __name__ == "__main__":
    main()
