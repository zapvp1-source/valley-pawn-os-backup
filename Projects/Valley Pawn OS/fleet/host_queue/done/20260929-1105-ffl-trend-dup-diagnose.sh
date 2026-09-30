#!/bin/bash
# HOST JOB — read-only diagnostic: why does the FFL Transfer Trend sheet show 2026-08 twice?
# ffl_trend_sync.py upserts keyed by Month; a duplicate means the key match failed.
set +e
H="$HOME/Documents/Claude/Scheduled/_shared/sheets_helper.py"
echo "=== upsert_by_key source ==="
/usr/bin/python3 - "$H" <<'PY'
import sys, inspect, importlib.util
spec = importlib.util.spec_from_file_location("sh", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
c = m.SheetsClient
for name in ("upsert_by_key",):
    print(inspect.getsource(getattr(c, name)))
PY
echo "=== raw sheet values (FORMATTED + UNFORMATTED) ==="
/usr/bin/python3 - <<'PY'
import sys
sys.path.insert(0, '/Users/joshuadavis/Documents/Claude/Scheduled/_shared')
from sheets_helper import SheetsClient
c = SheetsClient()
svc = getattr(c, 'svc', None) or getattr(c, 'service', None) or getattr(c, '_svc', None)
print('client attrs:', [a for a in dir(c) if not a.startswith('__')])
if svc is not None:
    for opt in ('FORMATTED_VALUE', 'UNFORMATTED_VALUE'):
        r = svc.spreadsheets().values().get(spreadsheetId='1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs', range='Monthly!A1:A30', valueRenderOption=opt).execute()
        print(opt, r.get('values'))
PY
exit 0
