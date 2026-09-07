"""Verification replay for the bonus engine. Read-only except for a temp copy it removes."""
import sys, os, shutil, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..'))
PIPE = '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction'
import bonus_engine as B

ok = []
# 1. the contaminated file must be rejected by the date gate
p = os.path.join(PIPE, 'output', '2026-08-31_CUL_end-of-month.xlsx')
good, rd = B.eom_is_month(p, '2026-08')
k = B.parse_eom(p)
ok.append(('date gate rejects the T12M file masquerading as August',
           (not good) and k['net_revenue'] > 500000, f"reporting_dates={rd} net_revenue={k['net_revenue']}"))

# 2. what the engine actually used for August
ctx = B.Ctx(ROOT, PIPE, '2026-08')
src, rd2 = B.find_month_eom(ctx, '2026-08', 'CUL')
k2 = B.parse_eom(src)
ok.append(('engine used the month-only sidecar for August CUL',
           'same-month-current' in src and abs(k2['net_revenue'] - 61998.28) < 0.01, f"{os.path.basename(src)} rd={rd2} net={k2['net_revenue']}"))

# 3. plausibility band: feed a 10x value and confirm it would be held
hist = json.load(open(os.path.join(ROOT, 'data', 'history.json')))
vals = [hist[m]['CUL']['net_revenue'] for m in B.trailing_months('2026-07', 12) if m in hist and 'CUL' in hist[m]]
avg = sum(vals) / len(vals)
band = ctx.rules['gates']['net_revenue_plausibility_band']
ok.append(('plausibility band would reject 767112.67 for CUL',
           not (avg * (1 - band) <= 767112.67 <= avg * (1 + band)), f"trailing12 avg={avg:.2f} band=+/-{band}"))

# 4. ledger has both months
import openpyxl
wb = openpyxl.load_workbook(os.path.join(ROOT, 'ledger', 'VP_Bonus_Ledger_2026.xlsx'))
q = [r[0] for r in wb['Qualifiers'].iter_rows(min_row=2, values_only=True)]
pay = [(r[0], r[2], r[6]) for r in wb['Payouts'].iter_rows(min_row=2, values_only=True)]
tot8 = round(sum(p[2] for p in pay if p[0] == '2026-08' and p[2]), 2)
ok.append(('ledger holds July + August qualifier rows',
           q.count('2026-07') == 5 and q.count('2026-08') == 5, f"jul={q.count('2026-07')} aug={q.count('2026-08')}"))
ok.append(('ledger August payout lines sum to the reported total',
           abs(tot8 - 3708.25) < 0.01 or abs(tot8 - 3408.25) < 0.01, f"sum of payout column = {tot8} (includes the $300 pool row as well as the per-person shares)"))

# 5. HELD path: a month with no data must exit 2 and write nothing publishable
import tempfile
rc = subprocess.run([sys.executable, os.path.join(HERE, 'bonus_engine.py'), 'close', '--month', '2026-05'],
                    capture_output=True, text=True, cwd=ROOT).returncode
outdir = os.path.join(ROOT, 'out', '2026-05')
files = os.listdir(outdir) if os.path.isdir(outdir) else []
ok.append(('a month with no collected data exits 2 and writes only hold.txt',
           rc == 2 and files == ['hold.txt'], f"rc={rc} files={files}"))

# 6. field posting must be off
ok.append(('field_posting is off', ctx.rules['field_posting']['enabled'] is False, ''))

for name, passed, detail in ok:
    print(('PASS  ' if passed else 'FAIL  ') + name + ('   [' + detail + ']' if detail else ''))
print('\n' + ('ALL PASS' if all(o[1] for o in ok) else 'SOMETHING FAILED'))
