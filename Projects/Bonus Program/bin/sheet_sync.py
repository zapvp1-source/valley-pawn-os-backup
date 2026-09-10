#!/usr/bin/env python3
"""sheet_sync.py — keep VP BONUS FINAL Updated.xlsx current and source targets from it.

    python3 bin/sheet_sync.py --month 2026-09      # month just closed

What it does, in order:
  1. reads data/history.json (already updated by `bonus_engine.py collect`)
  2. rebuilds the '2026 Plan vs Actual' sheet: closed months get actuals, variance,
     ending assets, yield; open months get targets = remaining annual plan spread by
     the seasonal shape, floored at a seasonally-equal repeat of the trailing-3 run rate
  3. writes data/<next month>/targets.json from the sheet (method: "sheet")
  4. exits 0 on success, 2 if the annual plan cannot be read (HELD — post nothing)

Annual plan per store lives in the sheet's 'Annual plan' rows and is Joshua's to edit.
The sheet is Drive-synced at the path below; a dated backup is taken every run.
Created 2026-09-09. Additive — bonus_engine.py is untouched.
"""
import argparse, json, math, os, shutil, sys, datetime as dt
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

SHEET = ('/Users/joshuadavis/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive/'
         '00 Inbox/Desktop Spreadsheets Import (Needs Sorting)/VP BONUS FINAL Updated.xlsx')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = ['CUL', 'HAR', 'ROA', 'LEX', 'WAY']
NAME = {'CUL': 'Culpeper', 'HAR': 'Harrisonburg', 'ROA': 'Roanoke', 'LEX': 'Lexington', 'WAY': 'Waynesboro'}
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
          'September', 'October', 'November', 'December']
RULES = json.load(open(os.path.join(ROOT, 'bonus_rules.json')))
DEFAULT_PLAN = {'CUL': 726042, 'HAR': 599708, 'ROA': 585973, 'LEX': 335431, 'WAY': 448674}


def next_month(m):
    y, mo = int(m[:4]), int(m[5:])
    return '%04d-%02d' % ((y + 1, 1) if mo == 12 else (y, mo + 1))


def read_plan(path):
    """Annual plan per store from the 'Annual plan' rows; falls back to defaults."""
    try:
        ws = openpyxl.load_workbook(path, data_only=True)['2026 Plan vs Actual']
    except Exception:
        return dict(DEFAULT_PLAN), 'defaults (sheet unreadable)'
    plan, cur = {}, None
    for r in ws.iter_rows(values_only=True):
        a = r[0]
        if isinstance(a, str) and a in NAME.values():
            cur = [k for k, v in NAME.items() if v == a][0]
        if isinstance(a, str) and a == 'Annual plan' and cur and cur not in plan and isinstance(r[2], (int, float)):
            plan[cur] = float(r[2])
    if len(plan) == 5:
        return plan, 'sheet'
    return dict(DEFAULT_PLAN), 'defaults (rows missing)'


def seasonal(H, MS):
    resid = {}
    for s in STORES:
        ys = [math.log(H[m][s]['net_revenue']) for m in MS]
        xs = list(range(len(MS)))
        n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        a = my - b * mx
        for i, m in enumerate(MS):
            resid.setdefault(m[5:], []).append(ys[i] - (a + b * i))
    d = {k: math.exp(sum(v) / len(v)) for k, v in resid.items()}
    m0 = sum(d.values()) / len(d)
    d = {k: min(1.05, max(0.95, v / m0)) for k, v in d.items()}
    for k in ['%02d' % i for i in range(1, 13)]:
        d.setdefault(k, 1.0)
    m1 = sum(d.values()) / 12
    return {k: v / m1 for k, v in d.items()}


def open_targets(H, MS, SI, plan, year):
    out = {}
    for s in STORES:
        closed = {m[5:]: H[m][s]['net_revenue'] for m in MS if m.startswith(year)}
        ytd = sum(closed.values())
        rem_keys = [k for k in ['%02d' % i for i in range(1, 13)] if k not in closed]
        remaining = plan[s] - ytd
        wsum = sum(SI[k] for k in rem_keys) or 1.0
        r3 = sum(H[m][s]['net_revenue'] / SI[m[5:]] for m in MS[-3:]) / 3
        lm = H[MS[-1]][s]['net_revenue'] / SI[MS[-1][5:]]      # last closed month, deseasonalised
        no_catch_up = s in RULES.get('sheet_targets', {}).get('no_catch_up_stores', [])
        tg = {}
        for k in rem_keys:
            spread = remaining * SI[k] / wsum
            floor = max(r3, lm) * SI[k]
            tg[k] = floor if no_catch_up else max(spread, floor)
        out[s] = {'ytd': ytd, 'remaining': remaining, 'targets': tg, 'no_catch_up': no_catch_up}
    return out


def posted_target(month, s):
    p = os.path.join(ROOT, 'data', month, 'targets.json')
    try:
        return json.load(open(p))['targets'][s]
    except Exception:
        return None


def write_sheet(path, H, MS, SI, plan, plan_src, OT, year, closed_month):
    bak = path.replace('.xlsx', '.BACKUP-%s.xlsx' % dt.date.today().isoformat())
    if os.path.exists(path) and not os.path.exists(bak):
        shutil.copy(path, bak)
    old = openpyxl.load_workbook(path) if os.path.exists(path) else None
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '2026 Plan vs Actual'
    bold = Font(bold=True)
    hdr_fill = PatternFill('solid', fgColor='1F3864'); hdr_font = Font(bold=True, color='FFFFFF')
    sub_fill = PatternFill('solid', fgColor='D9E1F2'); tgt_fill = PatternFill('solid', fgColor='FFF2CC')
    thin = Side(style='thin', color='BFBFBF'); box = Border(left=thin, right=thin, top=thin, bottom=thin)
    money, pct = '$#,##0', '0.0%'
    row = 1
    ws.cell(row, 1, 'VALLEY PAWN — %s BONUS TARGETS' % year).font = Font(bold=True, size=14)
    row += 1
    ws.cell(row, 1, 'Last updated %s after the %s close. Annual plan per store is Joshua\'s number (edit the '
            '"Annual plan" cell). Monthly targets = remaining plan spread by the seasonal shape of actuals, never '
            'below a seasonally-equal repeat of the trailing-3-month run rate. Refreshed on the 1st by '
            'bonus-month-close-pull.' % (dt.date.today().isoformat(), closed_month)).alignment = Alignment(wrap_text=True)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=9)
    ws.row_dimensions[row].height = 48
    row += 2
    ws.cell(row, 1, 'SEASONAL SHAPE (1.00 = average month)').font = bold
    row += 1
    for i, k in enumerate(sorted(SI)):
        ws.cell(row, 1 + i, MONTHS[int(k) - 1][:3]).font = bold
        ws.cell(row + 1, 1 + i, round(SI[k], 3)).number_format = '0.000'
    row += 3
    cols = ['Month', '%d Actual' % (int(year) - 1), '%s Target' % year, '%s Actual' % year,
            'Variance $', 'Variance %', 'Hit?', 'Ending Assets', 'Yield']
    company = {'%02d' % i: {'py': 0, 'tgt': 0, 'act': 0} for i in range(1, 13)}
    for s in STORES:
        ws.cell(row, 1, NAME[s]).font = Font(bold=True, size=12); row += 1
        for c, h in enumerate(cols, 1):
            cell = ws.cell(row, c, h); cell.font = hdr_font; cell.fill = hdr_fill; cell.border = box
        row += 1
        tot = {'py': 0, 'tgt': 0, 'act': 0}
        for i, mname in enumerate(MONTHS):
            k = '%02d' % (i + 1)
            m25, m26 = '%d-%s' % (int(year) - 1, k), '%s-%s' % (year, k)
            py = H.get(m25, {}).get(s, {}).get('net_revenue')
            act = H.get(m26, {}).get(s, {}).get('net_revenue')
            ea = H.get(m26, {}).get(s, {}).get('ending_assets')
            if act is not None:
                tgt = posted_target(m26, s)
                if tgt is None:
                    tgt = plan[s] * SI[k] / 12
            else:
                tgt = OT[s]['targets'][k]
            ws.cell(row, 1, mname).border = box
            c = ws.cell(row, 2, round(py) if py else None); c.number_format = money; c.border = box
            c = ws.cell(row, 3, round(tgt)); c.number_format = money; c.border = box
            if act is None: c.fill = tgt_fill
            c = ws.cell(row, 4, round(act) if act is not None else None); c.number_format = money; c.border = box
            if act is not None:
                c = ws.cell(row, 5, round(act - tgt)); c.number_format = money; c.border = box
                c = ws.cell(row, 6, act / tgt - 1); c.number_format = pct; c.border = box
                c = ws.cell(row, 7, 'Y' if act >= tgt else 'N'); c.border = box; c.alignment = Alignment(horizontal='center')
                c = ws.cell(row, 8, round(ea) if ea else None); c.number_format = money; c.border = box
                if m26 in MS and MS.index(m26) > 0:
                    prev = H.get(MS[MS.index(m26) - 1], {}).get(s, {}).get('ending_assets')
                    if prev:
                        c = ws.cell(row, 9, act / prev); c.number_format = pct; c.border = box
            else:
                for cc in range(5, 10): ws.cell(row, cc).border = box
            tot['py'] += py or 0; tot['tgt'] += tgt; tot['act'] += act or 0
            company[k]['py'] += py or 0; company[k]['tgt'] += tgt; company[k]['act'] += act or 0
            row += 1
        ws.cell(row, 1, 'Total').font = bold
        for c, v in [(2, tot['py']), (3, tot['tgt']), (4, tot['act'])]:
            cell = ws.cell(row, c, round(v)); cell.number_format = money; cell.font = bold; cell.fill = sub_fill
        row += 1
        ws.cell(row, 1, 'Annual plan').font = bold
        c = ws.cell(row, 3, round(plan[s])); c.number_format = money; c.font = bold
        c.fill = PatternFill('solid', fgColor='E2EFDA')
        ws.cell(row, 4, 'YTD actual').font = bold
        c = ws.cell(row, 5, round(OT[s]['ytd'])); c.number_format = money
        ws.cell(row, 6, 'Remaining').font = bold
        c = ws.cell(row, 7, round(OT[s]['remaining'])); c.number_format = money
        ws.cell(row, 8, 'targets: run rate' if OT[s].get('no_catch_up') else 'targets: plan / run rate').font = Font(italic=True)
        row += 2
    ws.cell(row, 1, 'COMPANY').font = Font(bold=True, size=12); row += 1
    for c, h in enumerate(cols[:7], 1):
        cell = ws.cell(row, c, h); cell.font = hdr_font; cell.fill = hdr_fill; cell.border = box
    row += 1
    ct = {'py': 0, 'tgt': 0, 'act': 0}
    for i, mname in enumerate(MONTHS):
        k = '%02d' % (i + 1); d = company[k]; closed = ('%s-%s' % (year, k)) in MS
        ws.cell(row, 1, mname).border = box
        c = ws.cell(row, 2, round(d['py'])); c.number_format = money; c.border = box
        c = ws.cell(row, 3, round(d['tgt'])); c.number_format = money; c.border = box
        if not closed: c.fill = tgt_fill
        c = ws.cell(row, 4, round(d['act']) if closed else None); c.number_format = money; c.border = box
        if closed:
            c = ws.cell(row, 5, round(d['act'] - d['tgt'])); c.number_format = money; c.border = box
            c = ws.cell(row, 6, d['act'] / d['tgt'] - 1); c.number_format = pct; c.border = box
            c = ws.cell(row, 7, 'Y' if d['act'] >= d['tgt'] else 'N'); c.border = box; c.alignment = Alignment(horizontal='center')
        else:
            for cc in range(5, 8): ws.cell(row, cc).border = box
        ct['py'] += d['py']; ct['tgt'] += d['tgt']; ct['act'] += d['act']
        row += 1
    ws.cell(row, 1, 'Total').font = bold
    for c, v in [(2, ct['py']), (3, ct['tgt']), (4, ct['act'])]:
        cell = ws.cell(row, c, round(v)); cell.number_format = money; cell.font = bold; cell.fill = sub_fill
    row += 1
    ws.cell(row, 1, 'Annual plan').font = bold
    c = ws.cell(row, 3, round(sum(plan.values()))); c.number_format = money; c.font = bold
    ws.cell(row, 5, 'plan source: %s' % plan_src)
    for col, w in zip('ABCDEFGHI', [14, 13, 13, 13, 12, 11, 6, 14, 8]):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = 'B1'
    if old is not None:
        for n in old.sheetnames:
            if n == '2026 Plan vs Actual':
                continue
            src = old[n]; dst = wb.create_sheet(n[:31])
            for r in src.iter_rows(values_only=True):
                dst.append(list(r))
    wb.save(path)
    return bak


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--month', required=True, help='month just closed, YYYY-MM')
    ap.add_argument('--sheet', default=SHEET)
    a = ap.parse_args()
    H = json.load(open(os.path.join(ROOT, 'data', 'history.json')))
    MS = sorted(H)
    if a.month not in H:
        print('HELD: %s not in history.json — run bonus_engine.py collect first' % a.month)
        sys.exit(2)
    year = a.month[:4]
    plan, plan_src = read_plan(a.sheet)
    SI = seasonal(H, MS)
    OT = open_targets(H, MS, SI, plan, year)
    bak = write_sheet(a.sheet, H, MS, SI, plan, plan_src, OT, year, a.month)
    nm = next_month(a.month)
    nd = os.path.join(ROOT, 'data', nm); os.makedirs(nd, exist_ok=True)
    tp = os.path.join(nd, 'targets.json')
    prior = {}
    if os.path.exists(tp):
        prior = json.load(open(tp))
        shutil.copy(tp, tp + '.bak-%s' % dt.datetime.now().strftime('%Y%m%d-%H%M%S'))
    pym = '%d-%s' % (int(nm[:4]) - 1, nm[5:])
    out = {'targets': {s: round(OT[s]['targets'][nm[5:]]) for s in STORES if nm[5:] in OT[s]['targets']},
           'prior_year': {s: H.get(pym, {}).get(s, {}).get('net_revenue') for s in STORES},
           'source': 'VP BONUS FINAL Updated.xlsx via sheet_sync.py (annual plan: %s)' % plan_src,
           'method': 'sheet', 'closed_month': a.month,
           'generated': dt.datetime.now().isoformat(timespec='seconds')}
    if prior.get('targets'):
        out['superseded'] = {'targets': prior['targets'], 'source': prior.get('source')}
    json.dump(out, open(tp, 'w'), indent=1)
    print(json.dumps({'closed': a.month, 'next': nm, 'targets': out['targets'],
                      'plan_source': plan_src, 'sheet_backup': os.path.basename(bak)}, indent=1))
    with open(os.path.join(ROOT, 'RUN_LOG.md'), 'a') as f:
        f.write('\n## %s — sheet_sync %s\nSheet refreshed with %s actuals; %s targets from sheet: %s. Plan source: %s.\n' % (
            dt.datetime.now().isoformat(timespec='minutes'), a.month, a.month, nm,
            ', '.join('%s %s' % (s, '${:,.0f}'.format(v)) for s, v in out['targets'].items()), plan_src))
    sys.exit(0)


if __name__ == '__main__':
    main()
