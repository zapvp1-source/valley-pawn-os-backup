import sys
sys.path.insert(0, '/Users/joshuadavis/Documents/Claude/Scheduled/_shared')
from sheets_helper import SheetsClient
c = SheetsClient()
rows = c.read('1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs', 'Monthly!A1:N20')
data = [r for r in rows[1:] if r and str(r[0]).strip()]
data.sort(key=lambda r: str(r[0]))
print('MONTHS:', len(data))
tc = 0; tr = 0.0
print('Month     WAY  CUL  HAR  LEX  ROA   Tot    Revenue')
for r in data:
    r = [str(x) for x in r] + [''] * 14
    print('%-8s %4s %4s %4s %4s %4s %5s %10s' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[12]))
    try:
        tc += int(float(r[6])); tr += float(r[12])
    except Exception:
        pass
print('12-MONTH TOTAL: %d transfers, $%,.0f' % (tc, tr) if False else '12-MONTH TOTAL: %d transfers, $%s' % (tc, format(round(tr), ',')))
