#!/usr/bin/env python3
"""FFL Transfer Trend sheet — duplicate-row check / repair (added 2026-09-29, additive).

The monthly task's ffl_trend_sync.py upserts keyed by Month, yet the sheet carries 2026-08 twice.
  --check  (default) read-only: prints upsert_by_key source, client attributes, and column A in
           FORMATTED and UNFORMATTED render so the key-mismatch cause is visible.
  --apply  deletes rows that are EXACT duplicates (every cell equal, formatted) of an earlier row.
           Never touches a row that differs in any cell. Prints before/after.
"""
import sys, inspect
sys.path.insert(0, '/Users/joshuadavis/Documents/Claude/Scheduled/_shared')
import sheets_helper
from sheets_helper import SheetsClient

SHEET_ID = '1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs'
TAB = 'Monthly'
apply = '--apply' in sys.argv

c = SheetsClient()
print('client attrs:', [a for a in dir(c) if not a.startswith('__')])
try:
    print(inspect.getsource(SheetsClient.upsert_by_key))
except Exception as e:
    print('source unavailable:', e)

svc = None
for name in ('svc', 'service', '_svc', '_service', 'sheets', '_sheets'):
    v = getattr(c, name, None)
    if v is not None and hasattr(v, 'spreadsheets'):
        svc = v; break
if svc is None:
    print('NO_SERVICE_HANDLE — cannot read raw values; stopping without changes.')
    sys.exit(0)

vals = svc.spreadsheets().values()
fmt = vals.get(spreadsheetId=SHEET_ID, range=f'{TAB}!A1:Z200', valueRenderOption='FORMATTED_VALUE').execute().get('values', [])
unf = vals.get(spreadsheetId=SHEET_ID, range=f'{TAB}!A1:A200', valueRenderOption='UNFORMATTED_VALUE').execute().get('values', [])
for i, r in enumerate(fmt):
    print(i + 1, 'A_fmt=%r' % (r[0] if r else None), 'A_raw=%r' % (unf[i][0] if i < len(unf) and unf[i] else None), '|', r[1:])

seen, dups = set(), []
for i, r in enumerate(fmt[1:], start=2):
    key = tuple(r)
    if key in seen:
        dups.append(i)
    seen.add(key)
print('exact duplicate rows (1-based):', dups)
if not apply or not dups:
    sys.exit(0)

meta = svc.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
gid = next(s['properties']['sheetId'] for s in meta['sheets'] if s['properties']['title'] == TAB)
reqs = [{'deleteDimension': {'range': {'sheetId': gid, 'dimension': 'ROWS', 'startIndex': r - 1, 'endIndex': r}}}
        for r in sorted(dups, reverse=True)]
svc.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={'requests': reqs}).execute()
after = vals.get(spreadsheetId=SHEET_ID, range=f'{TAB}!A1:A200', valueRenderOption='FORMATTED_VALUE').execute().get('values', [])
print('deleted rows', dups, '— column A now:', [x[0] if x else '' for x in after])
