#!/usr/bin/env python3
"""
lo_outcomes_fpd.py -- First-payment-default outcomes for the MONTHLY "Loan & Layaway Outcomes" report.
READ-ONLY. Reads Bravo pipeline CSVs only; never drives Bravo.

Stable copy (2026-09-30) of `Life OS/Reminders Execution 2026-09-30/analyses/fpd_outcomes.py`, which is
left untouched. Logic is the same; what changed:
  * no hard-coded dates -- the expired-loan list is the LATEST complete `<date>_<STORE>_forfeiture-winback.csv`
    per store (weekly native pull, Sunday 12:30), and each file's own date is its capture date (the original
    used a fixed 2026-09-29);
  * the 9/30 past-due cross-check uses the latest `loans75-detail` set on disk (positive check only);
  * the expired list is keyed by (store, ticket) rather than ticket alone (identical result on 9/30 data;
    safer if ticket numbers ever repeat across stores);
  * importable: `compute(month)` returns a dict; nothing is written by the module itself;
  * adds month-specific cuts: FPD loans forfeited in the report month, and the "never had a payment" share
    for loans that EXPIRED in the report month (plus the prior 12 months for trend).

Definitions (unchanged, verified 2026-09-30 in the original):
  * Age = days since the ORIGINAL pawn date as of the capture date.
  * Due Date - pawn date = 30 x (1 + number of paid 30-day extensions); == 30 means never paid.
  * fpd-cohort saved report ("Claude First Payment Default") = on loan, NO payment ever, 46+ days old.
  * Lens A outcome: FORFEITED (ticket in the expired list, expired on/after pawn) / CURED (dropped off a later
    snapshot without expiring) / OPEN (still on the store's latest snapshot, not expired).
  * Lens B: of expired loans, the share whose due date never moved past pawn+30 ("never paid once").
"""
import csv, glob, os, re, collections, datetime as dt

OUT = '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/'
if not os.path.isdir(OUT):
    _m = glob.glob('/sessions/*/mnt/Projects/Bravo Data Extraction/output/')
    OUT = _m[0] if _m else OUT
STORES = ['CUL', 'HAR', 'LEX', 'ROA', 'WAY']
BANDS = ['$0-49', '$50-99', '$100-249', '$250-499', '$500+']
F, C, O = 'Forfeited', 'Cured (paid/redeemed/renewed)', 'Still open / unknown'
OUTS = [F, C, O]
P = lambda s: dt.datetime.strptime(s.strip(), '%m/%d/%Y').date()
money = lambda s: float(s.replace('$', '').replace(',', '').replace('(', '-').replace(')', '') or 0)


def band(a):
    for lo, hi, lab in [(0, 50, '$0-49'), (50, 100, '$50-99'), (100, 250, '$100-249'),
                        (250, 500, '$250-499'), (500, 1e12, '$500+')]:
        if lo <= a < hi:
            return lab


def _meta_ok(path):
    """A pipeline CSV is complete when its .meta says captured == expected (grid fully walked)."""
    m = path + '.meta'
    if not os.path.exists(m):
        return True   # older handlers wrote no .meta; the CSV header check below still applies
    kv = dict(l.strip().split('=', 1) for l in open(m) if '=' in l)
    return 'captured' in kv and (kv.get('expected') in (None, kv['captured']))


def latest_expired_files(on_or_before=None):
    """store -> (date, path) of the newest complete forfeiture-winback list (not -addr / -comparison)."""
    res = {}
    for s in STORES:
        best = None
        for p in glob.glob(OUT + f'*_{s}_forfeiture-winback.csv'):
            d = os.path.basename(p)[:10]
            if not re.match(r'\d{4}-\d{2}-\d{2}$', d):
                continue
            if on_or_before and d > on_or_before:
                continue
            if os.path.getsize(p) < 200 or not _meta_ok(p):
                continue
            if best is None or d > best[0]:
                best = (d, p)
        if best:
            res[s] = best
    return res


def load_expired(files):
    exp = {}
    for s, (d, f) in files.items():
        cap = dt.date.fromisoformat(d)
        allrows = collections.defaultdict(list)
        for x in csv.DictReader(open(f, encoding='utf-8-sig')):
            allrows[x['Ticket Number']].append(x)
        for t, rows in allrows.items():
            x = rows[0]
            pawn = cap - dt.timedelta(int(x['Age']))
            exp[(s, t)] = dict(store=s, ticket=t, exp=P(x['Disposition Date']), due=P(x['Due Date']), pawn=pawn,
                               amt=sum(money(r['Loan Amount']) for r in rows))
    return exp


def latest_l75():
    ds = sorted({os.path.basename(p)[:10] for p in glob.glob(OUT + '*_loans75-detail.csv')})
    if not ds:
        return set(), None
    d = ds[-1]
    s = set()
    for f in glob.glob(OUT + f'{d}_*_loans75-detail.csv'):
        s |= {x['Ticket Number'] for x in csv.DictReader(open(f, encoding='utf-8-sig'))}
    return s, d


def lens_a(exp, l75):
    tickets = {}
    captures = collections.defaultdict(set)
    for f in sorted(glob.glob(OUT + '20*-*_fpd-cohort.csv')):
        s = os.path.basename(f)[11:14]
        if s not in STORES:
            continue
        rows = list(csv.DictReader(open(f, encoding='utf-8-sig')))
        if not rows or 'Ticket Number' not in rows[0]:
            continue   # count-only files (e.g. 5/18 for 4 stores) carry no loans
        cap = collections.Counter(P(x['Disposition Date']) + dt.timedelta(int(x['Age']))
                                  for x in rows).most_common(1)[0][0]
        for x in rows:
            pawn = cap - dt.timedelta(int(x['Age']))
            captures[s].add(cap)
            t = tickets.setdefault(x['Ticket Number'], dict(store=s, pawn=pawn, due=P(x['Due Date']),
                                                           items={}, first=cap, last=cap))
            t['first'] = min(t['first'], cap); t['last'] = max(t['last'], cap)
            key = (x.get('Full Description', ''), x['Loan Amount'], x.get('Category', ''))
            t['items'][key] = (money(x['Loan Amount']), x.get('Category', ''))
    res = []
    for tk, t in tickets.items():
        amt = sum(v[0] for v in t['items'].values())
        last_store_cap = max(captures[t['store']])
        e = exp.get((t['store'], tk))
        exp_date = None
        if e and e['exp'] >= t['pawn']:
            out = F; exp_date = e['exp']
        elif t['last'] < last_store_cap:
            out = C
        else:
            out = O
        res.append(dict(ticket=tk, store=t['store'], amount=round(amt, 2), band=band(amt), outcome=out,
                        exp_date=exp_date, days_to_expire=(exp_date - t['pawn']).days if exp_date else None,
                        confirmed_open=(out == O and tk in l75)))
    return res, {s: sorted(str(c) for c in captures[s]) for s in captures}


def _mbounds(ym):
    y, m = map(int, ym.split('-'))
    first = dt.date(y, m, 1)
    nxt = dt.date(y + (m == 12), m % 12 + 1, 1)
    return first, nxt - dt.timedelta(1)


def _prev(ym, n=1):
    y, m = map(int, ym.split('-'))
    for _ in range(n):
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    return f'{y}-{m:02d}'


def compute(month):
    """month = 'YYYY-MM' (the report month). Returns a plain dict of everything the report needs."""
    files = latest_expired_files()
    exp = load_expired(files)
    l75, l75_date = latest_l75()
    A, caps = lens_a(exp, l75)
    m_first, m_last = _mbounds(month)

    def tab(key):
        g = {}
        for r in A:
            k = r[key]
            g.setdefault(k, {o: [0, 0.0] for o in OUTS})
            g[k][r['outcome']][0] += 1; g[k][r['outcome']][1] += r['amount']
        return g
    tot = {o: [0, 0.0] for o in OUTS}
    for r in A:
        tot[r['outcome']][0] += 1; tot[r['outcome']][1] += r['amount']
    in_month = [r for r in A if r['exp_date'] and m_first <= r['exp_date'] <= m_last]
    fm_store = collections.Counter(r['store'] for r in in_month)
    dte = sorted(r['days_to_expire'] for r in A if r['days_to_expire'] is not None)

    # Lens B -- by EXPIRY month, last 13 months (report month + 12 before it)
    months = [_prev(month, i) for i in range(12, -1, -1)]
    lb = {}
    for t in exp.values():
        k = (t['due'] - t['pawn']).days
        if k % 30 != 0:
            continue
        ym = t['exp'].strftime('%Y-%m')
        if ym not in months:
            continue
        z = 'never' if k // 30 - 1 == 0 else 'ext'
        for key in (('all', ym), (t['store'], ym), ('band:' + band(t['amt']), ym)):
            lb.setdefault(key, {'never': [0, 0.0], 'ext': [0, 0.0]})
            lb[key][z][0] += 1; lb[key][z][1] += t['amt']
    through = {s: d for s, (d, _) in files.items()}
    return dict(month=month, month_first=str(m_first), month_last=str(m_last),
                expired_list_dates=through, stores_missing_expired=[s for s in STORES if s not in files],
                fpd_captures=caps, stores_missing_fpd=[s for s in STORES if s not in caps],
                n_fpd=len(A), total=tot, by_store=tab('store'), by_band=tab('band'),
                forfeited_in_month=len(in_month), forfeited_in_month_amt=round(sum(r['amount'] for r in in_month), 2),
                forfeited_in_month_by_store=dict(fm_store),
                confirmed_open=[sum(1 for r in A if r['confirmed_open']), round(sum(r['amount'] for r in A if r['confirmed_open']), 2)],
                confirmed_open_by_store={s: sum(1 for r in A if r['confirmed_open'] and r['store'] == s) for s in STORES},
                l75_date=l75_date, days_to_expire_median=dte[len(dte) // 2] if dte else None,
                lensB={f'{k[0]}|{k[1]}': v for k, v in lb.items()}, lensB_months=months)


if __name__ == '__main__':
    import json, sys
    print(json.dumps(compute(sys.argv[1] if len(sys.argv) > 1 else dt.date.today().strftime('%Y-%m')), indent=1, default=str))
