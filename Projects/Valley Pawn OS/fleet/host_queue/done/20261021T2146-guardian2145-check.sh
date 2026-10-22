#!/bin/bash
set -e
VPO="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS"
echo "=== vp_dryrun.py status ==="
python3 "$VPO/bin/vp_dryrun.py" status
echo "DRYRUN_EXIT=$?"
echo "=== task_lastrun.py ==="
python3 "$VPO/bin/task_lastrun.py" 2>&1 || echo "task_lastrun.py failed or not found"
echo "=== task_preflight.py --json (enabled only) ==="
python3 "$VPO/bin/task_preflight.py" --json 2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); 
tasks = d if isinstance(d, list) else d.get('tasks', d)
try:
    enabled = [t for t in tasks if t.get('enabled')]
    print(f'enabled_count={len(enabled)}')
    for t in enabled:
        print(t.get('name'), t.get('cron'), t.get('lastRunAt'))
except Exception as e:
    print('parse-note:', e)
    print(json.dumps(d)[:2000])
" 2>&1
