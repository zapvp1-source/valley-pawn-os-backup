"""Re-score a day's tracks with the CURRENT config.json rules and rewrite that day's rows in counts/<store>.csv.
Usage: python3 rescore.py <Store> <YYYY-MM-DD> [--write]"""
import csv, json, os, sys, collections
sys.argv += [] ; HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('VPST_DIR', os.path.expanduser('~/.vp_secrets/store_traffic'))
import counter
store, day = sys.argv[1], sys.argv[2]; cfg = counter.CFG[store]
H = collections.defaultdict(lambda: {'in': 0, 'out': 0})
for l in open(os.path.join(HERE, 'tracks', store, day + '.jsonl')):
    t = json.loads(l); d = counter.decide(t, cfg)
    if d: H[f"{day} {t['t'][:2]}:00"][d] += 1
tot = {k: sum(h[k] for h in H.values()) for k in ('in', 'out')}
for h in sorted(H): print(h, H[h])
print('TOTAL', tot)
if '--write' in sys.argv:
    path = os.path.join(HERE, 'counts', f'{store}.csv'); rows = {}
    if os.path.exists(path):
        for r in csv.DictReader(open(path)):
            if not r['hour'].startswith(day): rows[r['hour']] = r
    for h, c in H.items(): rows[h] = {'hour': h, 'in': c['in'], 'out': c['out']}
    with open(path + '.tmp', 'w', newline='') as f:
        w = csv.DictWriter(f, ['hour', 'in', 'out']); w.writeheader(); [w.writerow(rows[k]) for k in sorted(rows)]
    os.replace(path + '.tmp', path); print('written', path)
