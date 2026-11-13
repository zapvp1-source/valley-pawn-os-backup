#!/bin/bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/task_preflight.py" --json "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/host_queue/done/20261112-1247-preflight.json" > /dev/null 2>&1
python3 - << 'PYEOF' > "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/host_queue/done/20261112-1247-guardian-missedcheck.log" 2>&1
import glob, json, datetime, sys
try:
    from croniter import croniter
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "--quiet", "croniter"])
    from croniter import croniter

regs = glob.glob("$HOME/Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json".replace("$HOME", __import__("os").path.expanduser("~")))
print("registry files found:", regs)
now = datetime.datetime.now()
for rf in regs:
    try:
        data = json.load(open(rf))
    except Exception as e:
        print("PARSE ERROR", rf, e)
        continue
    tasks = data if isinstance(data, list) else data.get("tasks", data)
    if isinstance(tasks, dict):
        items = list(tasks.values())
    else:
        items = tasks
    for t in items:
        if not isinstance(t, dict):
            continue
        if not t.get("enabled"):
            continue
        cron = t.get("cronExpression") or t.get("cron")
        if not cron:
            continue
        fp = t.get("filePath", "")
        name = fp.rstrip("/").split("/")[-1] if fp else t.get("id", "?")
        last = t.get("lastRunAt")
        last_dt = None
        if last:
            try:
                if isinstance(last, (int, float)) or (isinstance(last, str) and last.isdigit()):
                    last_dt = datetime.datetime.fromtimestamp(int(last)/1000.0)
                else:
                    last_dt = datetime.datetime.fromisoformat(str(last).replace("Z","+00:00")).replace(tzinfo=None)
            except Exception as e:
                last_dt = None
        itr = croniter(cron, now)
        prev_fire = itr.get_prev(datetime.datetime)
        age_min = (now - prev_fire).total_seconds()/60.0
        missed = age_min > 20 and (last_dt is None or last_dt < prev_fire) and age_min < 48*60
        print(f"{name}\tcron={cron}\tprev_fire={prev_fire}\tlast={last}\tlast_dt={last_dt}\tage_min={age_min:.1f}\tMISSED={missed}")
PYEOF
