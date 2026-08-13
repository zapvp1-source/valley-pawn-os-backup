import sys
sys.path.insert(0, '/Users/joshuadavis/Documents/Claude/Scheduled/_shared')
from sheets_helper import SheetsClient
c = SheetsClient()
rows = c.read('1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs', 'Monthly!A1:N100')
data = [r for r in rows[1:] if r and str(r[0]).strip()]
stores = ['WAY', 'CUL', 'HAR', 'LEX', 'ROA']
names = {'WAY': 'Waynesboro', 'CUL': 'Culpeper', 'HAR': 'Harrisonburg', 'LEX': 'Lexington', 'ROA': 'Roanoke'}
# cols: 0 Month, 1-5 counts (WAY..ROA), 6 total ct, 7-11 revenue (WAY..ROA), 12 total rev
cnt = {s: 0 for s in stores}
rev = {s: 0.0 for s in stores}
def num(x):
    try: return float(str(x).replace('$', '').replace(',', ''))
    except: return 0.0
for r in data:
    r = list(r) + [''] * 14
    for i, s in enumerate(stores):
        cnt[s] += int(num(r[1 + i]))
        rev[s] += num(r[7 + i])
ranked = sorted(stores, key=lambda s: rev[s], reverse=True)
tc = sum(cnt.values()); tr = sum(rev.values())
print('Rank | Store | Revenue | Transfers')
for i, s in enumerate(ranked, 1):
    print('%d | %s | $%s | %d' % (i, names[s], format(int(round(rev[s])), ','), cnt[s]))
print('TOTAL | $%s | %d' % (format(int(round(tr)), ','), tc))
