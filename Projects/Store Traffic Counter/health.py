"""Nightly self-check for the door counters (native agent com.valleypawn.storetraffic-nightly, Mon-Sat 21:35 ET).
For each store open that day: video coverage, IN/OUT balance, agent restarts, Bravo tickets/visitor.
Writes reports/health/<date>.json + reports/health.csv, maintains reports/excluded_days.json (compare.py skips
those days), applies retention (audit/ 14 d, evidence/ 60 d). Exit 2 = at least one store DEGRADED (wrapper logs
one Failure Ledger row; nothing goes to Slack).  Usage: python3 health.py [YYYY-MM-DD]"""
import csv, datetime as dt, json, os, re, shutil, sys, time, zoneinfo
HERE = os.path.dirname(os.path.abspath(__file__)); TZ = zoneinfo.ZoneInfo('America/New_York')
CFG = json.load(open(os.path.join(HERE, 'config.json')))
STORES = ['Waynesboro', 'Culpeper', 'Roanoke', 'Lexington', 'Harrisonburg']
sys.path.insert(0, HERE)
day = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now(TZ).strftime('%Y-%m-%d')
D = dt.datetime.strptime(day, '%Y-%m-%d').replace(tzinfo=TZ); wd = D.strftime('%a')

def tickets(store):
    import importlib.util
    spec = importlib.util.spec_from_file_location('cmp_t', os.path.join(HERE, 'compare.py'))
    src = open(os.path.join(HERE, 'compare.py')).read().split('rows = []')[0]   # helpers only, no report run
    ns = {'__file__': os.path.join(HERE, 'compare.py')}; exec(src, ns)
    return ns['tickets'](store, day)

res = {}
for s in STORES:
    hrs = CFG[s].get('hours', {}).get(wd)
    if not hrs: continue
    o = D.replace(hour=int(hrs[0][:2]), minute=int(hrs[0][3:])); c = D.replace(hour=int(hrs[1][:2]), minute=int(hrs[1][3:]))
    open_min = (c - o).total_seconds() / 60; r = {'open_min': round(open_min)}
    p = os.path.join(HERE, 'dets', s, day + '.jsonl'); ts = []
    if os.path.exists(p):
        for l in open(p):
            try: t = json.loads(l)[0]
            except Exception: continue
            if o.timestamp() <= t <= c.timestamp(): ts.append(t)
    lost = 0; prev = o.timestamp()
    for t in ts + [c.timestamp()]:
        if t - prev > 60: lost += (t - prev)
        prev = t
    r['coverage_pct'] = round(100 * (1 - lost / 60 / open_min), 1) if open_min else 0
    ci = co = 0
    cp = os.path.join(HERE, 'counts', f'{s}.csv')
    if os.path.exists(cp):
        for row in csv.DictReader(open(cp)):
            if row['hour'].startswith(day): ci += int(row['in']); co += int(row['out'])
    r['in'], r['out'] = ci, co; vis = round((ci + co) / 2); r['visitors'] = vis
    r['imbalance_pct'] = round(100 * abs(ci - co) / max(1, max(ci, co)), 1)
    try: t = tickets(s)
    except Exception: t = None
    r['tickets'] = t; r['tickets_per_visitor'] = round(t / vis, 2) if (t and vis) else None
    why = []
    if r['coverage_pct'] < 95: why.append(f"video coverage {r['coverage_pct']}%")
    if vis >= 20 and r['imbalance_pct'] > 25: why.append(f"in/out off by {r['imbalance_pct']}%")
    if r['tickets_per_visitor'] is not None and not (0.4 <= r['tickets_per_visitor'] <= 1.0): why.append(f"tickets/visitor {r['tickets_per_visitor']}")
    if vis == 0: why.append('no visitors counted')
    r['status'] = 'DEGRADED' if why else 'OK'; r['why'] = why; res[s] = r

os.makedirs(os.path.join(HERE, 'reports', 'health'), exist_ok=True)
json.dump({'date': day, 'generated': dt.datetime.now(TZ).isoformat(timespec='seconds'), 'stores': res},
          open(os.path.join(HERE, 'reports', 'health', day + '.json'), 'w'), indent=1)
hp = os.path.join(HERE, 'reports', 'health.csv'); rows = []
if os.path.exists(hp): rows = [x for x in csv.DictReader(open(hp)) if x['date'] != day]
for s, r in res.items():
    rows.append({'date': day, 'store': s, 'status': r['status'], 'coverage_pct': r['coverage_pct'], 'in': r['in'], 'out': r['out'],
                 'visitors': r['visitors'], 'tickets': r['tickets'] or '', 'tickets_per_visitor': r['tickets_per_visitor'] or '', 'why': '; '.join(r['why'])})
with open(hp, 'w', newline='') as f:
    w = csv.DictWriter(f, ['date', 'store', 'status', 'coverage_pct', 'in', 'out', 'visitors', 'tickets', 'tickets_per_visitor', 'why'])
    w.writeheader(); w.writerows(sorted(rows, key=lambda x: (x['date'], x['store'])))
# degraded store-days are excluded from reporting automatically (coverage or zero count only; ratio alone just flags)
ep = os.path.join(HERE, 'reports', 'excluded_days.json')
ex = set(json.load(open(ep))) if os.path.exists(ep) else set()
for s, r in res.items():
    k = f'{s} {day}'
    if r['coverage_pct'] < 90 or r['visitors'] == 0: ex.add(k)
    else: ex.discard(k)
json.dump(sorted(ex), open(ep, 'w'), indent=1)
# retention
now = time.time()
for sub, days in (('audit', 14), ('evidence', 60)):
    for s in STORES:
        base = os.path.join(HERE, sub, s)
        if not os.path.isdir(base): continue
        for dd in os.listdir(base):
            if re.match(r'\d{4}-\d\d-\d\d$', dd) and (D - dt.datetime.strptime(dd, '%Y-%m-%d').replace(tzinfo=TZ)).days > days:
                shutil.rmtree(os.path.join(base, dd), ignore_errors=True)
# camera API access: a revoked/expired Google consent stops every counter -> one deduped Human Queue row
try:
    import nest_stream as _ns
    _ns.token()
except Exception as e:
    if 'invalid_grant' in repr(e) or 'HTTP Error 400' in repr(e) or 'HTTP Error 401' in repr(e):
        hq = os.path.join(os.path.dirname(HERE), 'Life OS', 'HUMAN_QUEUE.md')
        tag = 'Nest door counters — re-approve camera access'
        if os.path.exists(hq) and tag not in open(hq).read():
            row = (f"| {day} | [SIGN-IN] **{tag} (~2 min).** Sign in to Google as fullcirclepawn@gmail.com and open the Partner Connections "
                   "link in the Tech Stack Agent project doc \"Store Foot-Traffic Counter (Nest API) — PLAN + STATUS\" (Accounts & IDs) and click Allow. "
                   "All 5 store door counters are stopped until then. | Store visitor counts | " + day + " | OPEN |\n")
            open(hq, 'a').write(row)
        print('DEGRADED: camera API access refused - Human Queue row added'); sys.exit(2)
bad = {s: r['why'] for s, r in res.items() if r['status'] != 'OK'}
print(day, json.dumps({s: (r['status'], r['visitors'], r['tickets_per_visitor'], r['coverage_pct']) for s, r in res.items()}))
if bad: print('DEGRADED: ' + '; '.join(f"{s}: {', '.join(w)}" for s, w in bad.items())); sys.exit(2)
