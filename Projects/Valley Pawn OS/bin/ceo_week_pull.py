#!/usr/bin/env python3
"""ceo_week_pull.py — native (no-Claude) revenue data for the Weekly CEO Brief.  Added 2026-10-09, additive.

WHY: the brief withheld revenue on 10/5 because the only weekly figure available was a month-to-date
counter that resets on the 1st. A CEO's first number is revenue, so this pulls EXACT date ranges from
Bravo's End of Month report instead of subtracting MTD snapshots:
   W    = the reported week (Mon..Sun)            PW   = the week before (for week-over-week)
   LY   = the same Mon..Sun 364 days earlier      MTD  = 1st of W's end month .. W's Sunday
   LYMTD= the same calendar dates one year back   (for month-to-date vs last year)
Every file is validated by its OWN "Reporting Dates" header (eom_validate.read_range) before use, and copied
to Communcations/ceo-scorecard/data/eom/<start>_<end>_<STORE>.xlsx (collision-proof). Bravo writes range pulls
to output/<end>_<STORE>_end-of-month.xlsx — the same name the Monday store rankings use — so any existing
file there is backed up first and restored afterwards: output/ is left exactly as it was (Rule 4).
Then writes data/REVENUE_<W-monday>.json. Missing data is marked incomplete, never estimated (Rule 18).

usage: ceo_week_pull.py [--week YYYY-MM-DD(monday)] [--no-pull]
"""
import os, sys, json, shutil, subprocess, datetime as dt
HOME = os.path.expanduser('~')
PROJ = os.path.join(HOME, 'Documents/Claude/Projects')
BRAVO = os.path.join(PROJ, 'Bravo Data Extraction')
BIN = os.path.join(PROJ, 'Valley Pawn OS/bin')
OUTDIR = os.path.join(PROJ, 'Communcations/ceo-scorecard/data')
EOMDIR = os.path.join(OUTDIR, 'eom')
STORES = ['CUL', 'HAR', 'LEX', 'ROA', 'WAY']
NAMES = {'CUL': 'Culpeper', 'HAR': 'Harrisonburg', 'LEX': 'Lexington', 'ROA': 'Roanoke', 'WAY': 'Waynesboro'}
sys.path.insert(0, BRAVO)
import eom_validate as ev  # noqa: E402
import openpyxl  # noqa: E402

def log(*a): print(dt.datetime.now().strftime('%F %T'), *a, flush=True)

def ranges(week_mon):
    m = dt.date.fromisoformat(week_mon); s = m + dt.timedelta(days=6)
    pm, ps = m - dt.timedelta(days=7), s - dt.timedelta(days=7)
    lm, ls = m - dt.timedelta(days=364), s - dt.timedelta(days=364)
    mtd0 = s.replace(day=1)
    try: lymtd0, lys = mtd0.replace(year=mtd0.year - 1), s.replace(year=s.year - 1)
    except ValueError: lymtd0, lys = mtd0.replace(year=mtd0.year - 1), s.replace(year=s.year - 1, day=28)
    f = lambda a, b: (a.isoformat(), b.isoformat())
    return {'W': f(m, s), 'PW': f(pm, ps), 'LY': f(lm, ls), 'MTD': f(mtd0, s), 'LYMTD': f(lymtd0, lys)}

def have(rng, st):
    p = os.path.join(EOMDIR, f'{rng[0]}_{rng[1]}_{st}.xlsx')
    if os.path.exists(p) and ev.read_range(p) == rng: return p
    a = os.path.join(BRAVO, 'eom_archive', f'{rng[0]}_{rng[1]}_{st}.xlsx')
    if os.path.exists(a) and ev.read_range(a) == rng:
        shutil.copy2(a, p); return p
    return None

def pull(rng, stores):
    end = rng[1]; bk = {}
    for st in stores:
        o = os.path.join(BRAVO, 'output', f'{end}_{st}_end-of-month.xlsx')
        if os.path.exists(o):
            b = o + '.ceobrief-hold'; shutil.copy2(o, b); bk[st] = (o, b)
    tid = f'ceo-week-eom-{rng[0]}-{rng[1]}-{dt.datetime.now():%H%M%S}'
    rc = subprocess.run(['/bin/bash', os.path.join(BIN, 'bravo_pull.sh'), 'end-of-month', f'{rng[0]}..{rng[1]}',
                         ','.join(stores), tid], capture_output=True, text=True, timeout=7500)
    log('bravo_pull', rng, stores, 'rc=%d' % rc.returncode)
    for st in stores:
        o = os.path.join(BRAVO, 'output', f'{end}_{st}_end-of-month.xlsx')
        if os.path.exists(o) and ev.read_range(o) == rng:
            shutil.copy2(o, os.path.join(EOMDIR, f'{rng[0]}_{rng[1]}_{st}.xlsx'))
        else:
            log('  no valid file for', st, rng, 'got', ev.read_range(o) if os.path.exists(o) else None)
        if st in bk:  # put the pipeline's own file back exactly as it was
            shutil.copy2(bk[st][1], bk[st][0]); os.remove(bk[st][1])

def N(v):
    if v is None: return None
    s = str(v).strip().replace('$', '').replace(',', '')
    neg = s.startswith('(') and s.endswith(')'); s = s.strip('()')
    try: return -float(s) if neg else float(s)
    except ValueError: return None

def parse(p):
    """Column positions DRIFT between exports (seen: same row, 1-2 columns apart on two ranges), so every value is
    read by its position among the row's NON-EMPTY cells - the method store_kpis_compile.py verified to the penny."""
    ws = openpyxl.load_workbook(p, data_only=True).active
    MC = ws.max_column
    def nn(r):
        return [x for x in (ws.cell(r, c).value for c in range(1, MC + 1)) if x not in (None, '')] if r else []
    def row(lbl, exact=False, after=0):
        for r in range(after + 1, ws.max_row + 1):
            v = ws.cell(r, 1).value
            if v is None: continue
            sv = str(v).strip()
            if (sv == lbl if exact else sv.startswith(lbl)): return r
        return 0
    def at(lst, i):
        return (N(lst[i]) or 0.0) if len(lst) > i else 0.0
    def last(lst):
        return (N(lst[-1]) or 0.0) if lst else 0.0
    sub = nn(row('In-Store Subtotal')); mob = nn(row('Totals from'))
    psc_in = at(sub, 4) + at(sub, 5) + at(sub, 6)
    psc_mob = at(mob, 3) + at(mob, 4) + at(mob, 5)
    pa = row('Pawn Activity', exact=True); ist = row('In-Store Txns')
    nl = nn(row('New Loans', exact=True, after=pa)); by = nn(row('Buys', exact=True, after=pa))
    red = nn(row('Redemptions', exact=True, after=ist)); exl = nn(row('Expired Loans', exact=True, after=ist))
    net_sales = last(nn(row('Net Sales Subtotal'))); profit = last(nn(row('Sales Revenue (Profit)')))
    sa = row('Sales Activity', exact=True)
    taxable = last(nn(row('Taxable Sales', exact=True, after=sa))); nontax = last(nn(row('Nontaxable Sales', exact=True, after=sa)))
    refined = 0.0
    for r in range(1, ws.max_row + 1):
        if any(str(ws.cell(r, c).value or '').strip().startswith('Refined') for c in (1, 2, 3)):
            refined = abs(last(nn(r))); break
    loan_end = at(nn(row('Ending Loan Base')), 2); inv_end = at(nn(row('Ending Inventory Base')), 2)
    d = {
        'retail_sales': round(net_sales, 2),
        'gross_profit': round(profit, 2),
        'gross_margin_pct': round(100 * profit / net_sales, 1) if net_sales else None,
        'loan_fees_instore': round(psc_in, 2),
        'loan_fees_mobilepawn': round(psc_mob, 2),
        'net_revenue_bravo_basis': round(psc_in + profit, 2),      # = #store-performance / bonus "Net Revenue"
        'net_revenue_total': round(psc_in + psc_mob + profit, 2),  # + MobilePawn loan fees
        'taxable_retail_sales': round(taxable, 2),                 # merchandise sold over the counter/web (taxed)
        'precious_metal_sales': round(nontax, 2),                  # nontaxable: gold/silver/bullion incl. refinery settlements
        'refined_cost': round(refined, 2),                         # cost of scrap sent out in refinery settlements
        'new_loans_count': int(at(nl, 1)), 'new_loans_amt': round(at(nl, 2), 2),
        'buys_count': int(at(by, 1)), 'buys_amt': round(at(by, 2), 2),
        'redemptions_count': int(at(red, 1)), 'redemptions_principal': round(at(red, 2), 2),
        'forfeited_loans_count': int(at(exl, 1)), 'forfeited_loans_amt': round(at(exl, 2), 2),
        'loan_balance_end': round(loan_end, 2), 'inventory_end': round(inv_end, 2),
    }
    # biggest single day of sales (flags one large ticket skewing the week) - columns located by header text
    hdr = row('Date', exact=True); tc = nc = None
    for c in range(1, MC + 1):
        t = str(ws.cell(hdr, c).value or '').strip()
        if t == 'Taxable Sales': tc = c
        if t == 'Nontax Sales': nc = c
    best = (0.0, None)
    for r in range(hdr + 1, (row('Total:') or hdr + 1)):
        v = ws.cell(r, 1).value
        if hasattr(v, 'date') and tc and nc:
            day = (N(ws.cell(r, tc).value) or 0) + (N(ws.cell(r, nc).value) or 0)
            if day > best[0]: best = (day, v.date().isoformat())
    d['max_day_sales'] = round(best[0], 2); d['max_day_date'] = best[1]
    return d

def pct(a, b):
    return None if not b else round(100.0 * (a - b) / abs(b), 1)

def main():
    args = sys.argv[1:]
    if '--week' in args: wk = args[args.index('--week') + 1]
    else:
        t = dt.date.today()
        # Sunday evening -> this week (stores are closed Sunday); any other day -> last completed week
        wk = (t - dt.timedelta(days=6)).isoformat() if t.weekday() == 6 else (t - dt.timedelta(days=t.weekday() + 7)).isoformat()
    os.makedirs(EOMDIR, exist_ok=True)
    # self-heal: a run killed mid-pull leaves the pipeline's own file in a .ceobrief-hold copy - put it back first
    import glob as _g
    for b in _g.glob(os.path.join(BRAVO, 'output', '*_end-of-month.xlsx.ceobrief-hold')):
        shutil.copy2(b, b[:-len('.ceobrief-hold')]); os.remove(b); log('restored leftover', os.path.basename(b))
    R = ranges(wk); log('week', wk, R)
    if '--no-pull' not in args:
        for k, rng in R.items():
            need = [s for s in STORES if not have(rng, s)]
            if need: pull(rng, need)
            again = [s for s in STORES if not have(rng, s)]   # self-heal: one retry for stores that failed (e.g. a store switch miss)
            if again: log('retrying', rng, again); pull(rng, again)
    out = {'week_monday': wk, 'ranges': R, 'generated': dt.datetime.now().isoformat(timespec='seconds'),
           'basis': 'Bravo End of Month report, exact date ranges. HEADLINE = net_revenue_bravo_basis (in-store loan fees + gross profit on sales) - the same basis as #store-performance and the bonus targets. net_revenue_total adds MobilePawn loan fees.',
           'stores': {}, 'company': {}, 'incomplete': []}
    for k, rng in R.items():
        tot = {}
        for s in STORES:
            p = have(rng, s)
            if not p: out['incomplete'].append(f'{k}:{s}'); continue
            d = parse(p); out['stores'].setdefault(s, {'name': NAMES[s]})[k] = d
            for f, v in d.items():
                if isinstance(v, (int, float)) and not f.endswith('_pct'): tot[f] = round(tot.get(f, 0) + v, 2)
        if tot and all(f'{k}:{s}' not in out['incomplete'] for s in STORES):
            if tot.get('retail_sales'): tot['gross_margin_pct'] = round(100 * tot['gross_profit'] / tot['retail_sales'], 1)
            out['company'][k] = tot
    def deltas(node):
        w = node.get('W'); 
        if not w: return
        node['wow_pct'] = {f: pct(w[f], node['PW'][f]) for f in ('net_revenue_bravo_basis', 'net_revenue_total', 'retail_sales', 'gross_profit', 'loan_fees_instore', 'taxable_retail_sales', 'precious_metal_sales', 'new_loans_amt')} if node.get('PW') else None
        node['yoy_pct'] = {f: pct(w[f], node['LY'][f]) for f in ('net_revenue_bravo_basis', 'net_revenue_total', 'retail_sales', 'gross_profit', 'loan_fees_instore', 'taxable_retail_sales', 'precious_metal_sales', 'new_loans_amt')} if node.get('LY') else None
        node['mtd_vs_ly_pct'] = {f: pct(node['MTD'][f], node['LYMTD'][f]) for f in ('net_revenue_bravo_basis', 'net_revenue_total', 'retail_sales')} if node.get('MTD') and node.get('LYMTD') else None
    deltas(out['company'])
    # month target pace — same revenue basis as the bonus program (in-store loan fees + gross profit on sales)
    mtd_end = dt.date.fromisoformat(R['MTD'][1]); ym = mtd_end.strftime('%Y-%m')
    tp = os.path.join(PROJ, 'Bonus Program', 'data', ym, 'targets.json')
    if os.path.exists(tp):
        T = json.load(open(tp)); import calendar
        dim = calendar.monthrange(mtd_end.year, mtd_end.month)[1]; elapsed = mtd_end.day / dim
        out['month_target'] = {'month': ym, 'elapsed_pct': round(100 * elapsed, 1), 'stores': {}}
        for st, t in T.get('targets', {}).items():
            node = out['stores'].get(st, {}).get('MTD')
            if node: out['month_target']['stores'][st] = {'target': t, 'mtd': node['net_revenue_bravo_basis'],
                     'pct_of_target': round(100 * node['net_revenue_bravo_basis'] / t, 1), 'prior_year_month': T.get('prior_year', {}).get(st)}
        if out['company'].get('MTD') and T.get('company_target'):
            ct = T['company_target']; cm = out['company']['MTD']['net_revenue_bravo_basis']
            out['month_target']['company'] = {'target': ct, 'mtd': cm, 'pct_of_target': round(100 * cm / ct, 1)}
    for s in out['stores'].values(): deltas(s)
    dst = os.path.join(OUTDIR, f'REVENUE_{wk}.json')
    json.dump(out, open(dst + '.tmp', 'w'), indent=1); os.replace(dst + '.tmp', dst)
    log('wrote', dst, 'incomplete=', out['incomplete'] or 'none')
    return 0 if not out['incomplete'] else 3

if __name__ == '__main__':
    sys.exit(main())
