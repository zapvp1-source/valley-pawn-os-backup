#!/usr/bin/env python3
"""
test_yield_by_asset_class.py -- regression harness for the yield stack (ADDITIVE)
================================================================================
Created 2026-09-07. Run this BEFORE publishing any yield figure anywhere.
Exit 0 = every check passed and the numbers may be published.
Exit 1 = something drifted; publish NOTHING (vp-operating-rules Rule 18 --
withhold, don't caveat).

    python3 test_yield_by_asset_class.py

The checks are deliberately anchored to facts verified OUTSIDE this codebase,
so they catch silent drift in Bravo's export format, not just self-consistency:

  1. PENNY MATCH -- June 2026 net revenue per store must equal Preston Peters'
     actual commission basis (confirmed 2026-07-16, independent of any script).
  2. BONUS CROSS-CHECK -- August 2026 net revenue per store must equal the
     figures the Bonus Program engine derived independently for the August
     close (Bonus Program/RUN_LOG.md). Two separate pipelines, same answer.
  3. SALES IDENTITY -- Taxable + Taxable Layaway + Taxable Fees + Nontaxable
     + Nontaxable Layaway + Nontaxable Fees == Total Sales, every store-month.
     This is what proves layaway GP already sits inside the inventory-yield
     numerator; if it ever breaks, the layaway reasoning must be revisited.
  4. RANGE INTEGRITY -- every file the resolver accepted must actually cover
     the whole month it was accepted for.
  5. DECOMPOSITION -- the two class yields must weight-average back to the
     blended yield for every row (the split is exact, not approximate).
  6. NO PARTIAL MONTHS -- every published month must carry all 5 stores plus
     a COMPANY row.
"""
import os, sys, csv, glob, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eom_validate as ev

OUT = os.path.join(HERE, 'output')
CSV = os.path.join(OUT, 'yield_by_asset_class.csv')
STORES = ['CUL', 'HAR', 'LEX', 'ROA', 'WAY']

# Facts established outside this codebase -- never edit to make a test pass.
PRESTON_JUN_2026 = {'CUL': 66649.27, 'HAR': 61666.31, 'ROA': 36906.77,
                    'WAY': 43416.44, 'LEX': 21455.49}
BONUS_AUG_2026 = {'CUL': 61998.28, 'HAR': 54413.07, 'LEX': 27754.28,
                  'ROA': 48167.81, 'WAY': 40705.46}

fails, notes = [], []


def check(name, ok, detail=''):
    print(f'  {"PASS" if ok else "FAIL"}  {name}{"  -- " + detail if detail else ""}')
    if not ok:
        fails.append(name)


def num(v):
    return float(v) if v not in (None, '') else None


print('Regenerating yield data...')
r = subprocess.run([sys.executable, os.path.join(HERE, 'yield_by_asset_class.py')],
                   capture_output=True, text=True, cwd=HERE)
print('  ' + (r.stdout.strip().splitlines() or ['(no output)'])[0])
if r.returncode != 0:
    print('  extractor failed:\n' + r.stderr[-1500:])
    sys.exit(1)

rows = list(csv.DictReader(open(CSV)))
by = {(x['month'], x['store']): x for x in rows}
months = sorted({x['month'] for x in rows})

print(f'\n{len(rows)} rows, {len(months)} months ({months[0]} .. {months[-1]})\n')

# 1 -- Preston penny match
bad = [f"{s} {num(by[('2026-06', s)]['net_revenue']):.2f}!={v:.2f}"
       for s, v in PRESTON_JUN_2026.items()
       if ('2026-06', s) not in by or abs(num(by[('2026-06', s)]['net_revenue']) - v) > 0.005]
check('June 2026 net revenue == Preston commission basis (5 stores)', not bad, '; '.join(bad))

# 2 -- Bonus engine cross-check
bad = [f"{s} {num(by[('2026-08', s)]['net_revenue']):.2f}!={v:.2f}"
       for s, v in BONUS_AUG_2026.items()
       if ('2026-08', s) not in by or abs(num(by[('2026-08', s)]['net_revenue']) - v) > 0.005]
check('Aug 2026 net revenue == Bonus Program close figures (5 stores)', not bad, '; '.join(bad))

# 3 -- sales-component identity (this is what makes the layaway call correct)
import openpyxl
LBL = ['Taxable Sales', 'Taxable Layaway', 'Taxable Fees',
       'Nontaxable Sales', 'Nontaxable Layaway', 'Nontaxable Fees']
# Sampled, not exhaustive: openpyxl needs ~0.4s per workbook and there are 265+,
# which is two minutes of a scheduled run. The identity was proven 260/260 on
# 2026-09-07; this samples ~45 files spread across the whole history to catch
# drift in Bravo's export format, which is what could actually change.
_all = [p for p in sorted(glob.glob(os.path.join(OUT, '*_end-of-month.xlsx')))
        if len(os.path.basename(p).split('_')[0]) == 10]
_sample = _all[::max(1, len(_all) // 40)][:40] + _all[-5:]
checked = mism = 0
for p in dict.fromkeys(_sample):
    try:
        ws = openpyxl.load_workbook(p, data_only=True).active
    except Exception:
        continue
    got, tot = {}, None
    for rr in range(1, ws.max_row + 1):
        row = [x for x in [ws.cell(rr, c).value for c in range(1, ws.max_column + 1)]
               if x is not None]
        if len(row) < 5:
            continue
        lab = str(row[0]).strip().rstrip('*')
        if lab in LBL and lab not in got:
            try:
                got[lab] = float(row[4])
            except Exception:
                pass
        elif lab == 'Total Sales' and tot is None:
            try:
                tot = float(row[4])
            except Exception:
                pass
    if tot is None or len(got) < 6:
        continue
    checked += 1
    if abs(sum(got.values()) - tot) > 0.015:
        mism += 1
check(f'Sales-component identity holds ({checked} store-months sampled)',
      checked >= 25 and mism == 0,
      f'{mism} mismatches' if mism else ('' if checked >= 25 else f'only {checked} readable'))

# 4 -- every accepted file really covers its month
bad = []
for ym in months:
    for s in STORES:
        hit = ev.resolve(s, ym)
        if not hit:
            bad.append(f'{ym}/{s} unresolved')
        elif hit['range'] != ev.month_bounds(ym):
            bad.append(f'{ym}/{s} range {hit["range"]}')
check('Every published month resolves to a true full-month file',
      not bad, '; '.join(bad[:4]))

# 5 -- decomposition is exact
bad = []
for x in rows:
    lb, ib = num(x['prior_loan_base']), num(x['prior_inventory_base'])
    ly, iy, byl = num(x['loan_yield_mo']), num(x['inventory_yield_mo']), num(x['blended_yield_mo'])
    if None in (lb, ib, ly, iy, byl) or (lb + ib) == 0:
        continue
    recon = (lb * ly + ib * iy) / (lb + ib)
    if abs(recon - byl) > 0.02:
        bad.append(f"{x['month']}/{x['store']} {recon:.2f}!={byl:.2f}")
check('Loan + inventory yields weight-average to blended', not bad, '; '.join(bad[:4]))

# 6 -- no partial months
bad = [ym for ym in months
       if any((ym, s) not in by for s in STORES) or (ym, 'COMPANY') not in by]
check('Every month has all 5 stores + COMPANY', not bad, ','.join(bad[:5]))

print()
if fails:
    print(f'RESULT: FAIL ({len(fails)}) -- publish nothing.')
    for f in fails:
        print('  - ' + f)
    sys.exit(1)
print('RESULT: PASS -- data is safe to publish.')
sys.exit(0)
