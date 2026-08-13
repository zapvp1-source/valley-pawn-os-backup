import sys
sys.path.insert(0, '/Users/joshuadavis/Documents/Claude/Scheduled/_shared')
from sheets_helper import SheetsClient
SID = '1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs'
c = SheetsClient()
rows = c.read(SID, 'Monthly!A1:N100')
hdr = rows[0]
data = [r for r in rows[1:] if r and str(r[0]).strip()]
data.sort(key=lambda r: str(r[0]))
# write sorted data back starting at A2 (Month col A already text-formatted)
c.update(SID, 'Monthly!A2:N%d' % (len(data) + 1), data)
print('sorted %d month rows chronologically' % len(data))
