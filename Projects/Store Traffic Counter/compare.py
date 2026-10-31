"""Daily traffic comparison: door visitors (counts/<Store>.csv) vs Bravo transactions (safe-register-journal
ticket-number span minus the journal's own safe/till tickets) per store, plus conversion.
Usage: python3 compare.py [YYYY-MM-DD ...]   (default: every date that has door counts)
Writes reports/compare.csv (one row per store-day) and prints a table."""
import csv, glob, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
BRAVO = os.path.join(os.path.dirname(HERE), 'Bravo Data Extraction', 'output')
CODES = {'Culpeper': 'CUL', 'Waynesboro': 'WAY', 'Harrisonburg': 'HAR', 'Lexington': 'LEX', 'Roanoke': 'ROA'}
SKIP_BEFORE = {'Waynesboro': '2026-10-28', 'Culpeper': '2026-10-30'}   # earlier days were pre-validation versions (set aside)
TXN = re.compile(r'^([A-Z0-9]{2,4}?)(\d{6,9}),(\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [AP]M)')

def visitors(store):
    p = os.path.join(HERE, 'counts', f'{store}.csv'); out = collections.defaultdict(lambda: {'in': 0, 'out': 0})
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            d = r['hour'][:10]
            if d >= SKIP_BEFORE.get(store, ''): out[d]['in'] += int(r['in']); out[d]['out'] += int(r['out'])
    return out

def tickets(store, day):
    f = os.path.join(BRAVO, f'{day}_{CODES[store]}_safe-register-journal.csv')
    if not os.path.exists(f): return None
    nums = [int(m.group(2)) for line in open(f, errors='ignore') if (m := TXN.match(line))]
    if len(nums) < 2: return None
    return (max(nums) - min(nums) + 1) - len(set(nums))   # customer tickets between open and close

rows = []
for store in CODES:
    v = visitors(store)
    for day in sorted(v):
        if len(sys.argv) > 1 and day not in sys.argv[1:]: continue
        t = tickets(store, day); vi = round((v[day]['in'] + v[day]['out']) / 2)   # visitors = mean of door IN and OUT
        rows.append({'date': day, 'store': store, 'visitors_in': vi, 'visitors_out': v[day]['out'],
                     'bravo_tickets': '' if t is None else t,
                     'tickets_per_visitor': '' if (t is None or not vi) else round(t / vi, 2)})
os.makedirs(os.path.join(HERE, 'reports'), exist_ok=True)
with open(os.path.join(HERE, 'reports', 'compare.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, list(rows[0].keys()) if rows else ['date']); w.writeheader(); [w.writerow(r) for r in rows]
for r in sorted(rows, key=lambda r: (r['date'], r['store'])):
    print(f"{r['date']}  {r['store']:<11} visitors {r['visitors_in']:>3} (out {r['visitors_out']:>3})  Bravo tickets {str(r['bravo_tickets']):>3}  tickets/visitor {r['tickets_per_visitor']}")
