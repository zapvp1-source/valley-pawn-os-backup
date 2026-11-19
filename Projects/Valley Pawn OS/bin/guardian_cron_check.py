#!/usr/bin/env python3
"""guardian_cron_check.py — Fleet Guardian Step 1: which ENABLED cron tasks missed their most
recent scheduled fire? Read-only. Tries croniter; installs it with --user if missing (falls back
to None if pip has no network here, in which case missed-detection is skipped, not guessed).

MISSED = most recent scheduled fire time is more than 20 minutes ago AND
         (lastRunAt is null OR lastRunAt < that fire time).
Ignore: one-time (fireAt-only) tasks; any task whose last scheduled fire is >48h ago (stale,
not a current outage); fires due within the last 20 minutes (may still be starting).

Usage: guardian_cron_check.py [--json <path>]
"""
import glob, json, os, sys, datetime as dt

HOME = os.path.expanduser("~")
REG_GLOB = os.path.join(HOME, "Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json")

try:
    from croniter import croniter
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--quiet",
                    "--break-system-packages", "croniter"], check=False)
    try:
        from croniter import croniter
    except ImportError:
        croniter = None


def parse_last_run(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        if v > 10**12:
            v = v / 1000.0
        return dt.datetime.fromtimestamp(v, tz=dt.timezone.utc)
    if isinstance(v, str):
        s = v.strip()
        try:
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            d = dt.datetime.fromisoformat(s)
            if d.tzinfo is None:
                d = d.replace(tzinfo=dt.timezone.utc)
            return d.astimezone(dt.timezone.utc)
        except Exception:
            return None
    return None


def most_recent_fire(cron_expr, now_utc):
    if not croniter:
        return None
    try:
        expr = cron_expr.strip()
        tzname = None
        if expr.upper().startswith("CRON_TZ="):
            head, expr = expr.split(" ", 1)
            tzname = head.split("=", 1)[1]
            expr = expr.strip()
        if tzname:
            try:
                from zoneinfo import ZoneInfo
                tz = ZoneInfo(tzname)
            except Exception:
                tz = dt.timezone.utc
            base = now_utc.astimezone(tz).replace(tzinfo=None)
            itr = croniter(expr, base)
            prev_naive = itr.get_prev(dt.datetime)
            return prev_naive.replace(tzinfo=tz).astimezone(dt.timezone.utc)
        else:
            itr = croniter(expr, now_utc.replace(tzinfo=None))
            return itr.get_prev(dt.datetime).replace(tzinfo=dt.timezone.utc)
    except Exception:
        return None


def load_registry():
    paths = sorted(glob.glob(REG_GLOB), key=os.path.getmtime, reverse=True)
    if not paths:
        return None, None
    p = paths[0]
    return p, json.load(open(p))


def main():
    now = dt.datetime.now(dt.timezone.utc)
    path, reg = load_registry()
    out = {"registry_path": path, "now_utc": now.isoformat(), "croniter_available": bool(croniter)}
    if reg is None:
        out["error"] = "registry not found"
        print(json.dumps(out, indent=1))
        return
    tasks = reg.get("scheduledTasks", [])
    out["total_tasks"] = len(tasks)
    out["enabled_tasks"] = sum(1 for t in tasks if t.get("enabled"))
    missed = []
    skipped_no_cron = 0
    for t in tasks:
        if not t.get("enabled"):
            continue
        cron = t.get("cronExpression")
        if not cron:
            skipped_no_cron += 1
            continue
        fire = most_recent_fire(cron, now)
        if fire is None:
            continue
        age_min = (now - fire).total_seconds() / 60.0
        if age_min < 20:
            continue
        if age_min > 48 * 60:
            continue
        last_run = parse_last_run(t.get("lastRunAt"))
        if last_run is not None and last_run >= fire:
            continue
        missed.append({
            "id": t.get("id"),
            "filePath": t.get("filePath"),
            "cron": cron,
            "fire_utc": fire.isoformat(),
            "age_minutes": round(age_min, 1),
            "lastRunAt_raw": t.get("lastRunAt"),
            "lastRunAt_parsed": last_run.isoformat() if last_run else None,
        })
    out["skipped_no_cron"] = skipped_no_cron
    out["missed_count"] = len(missed)
    out["missed"] = missed
    js = json.dumps(out, indent=1)
    print(js)
    if "--json" in sys.argv:
        with open(sys.argv[sys.argv.index("--json") + 1], "w") as f:
            f.write(js)


if __name__ == "__main__":
    main()
