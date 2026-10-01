#!/usr/bin/env python3
"""
lo_outcomes_layaway.py -- Cancelled vs expired layaways by store and month, for the MONTHLY
"Loan & Layaway Outcomes" report. READ-ONLY; reads Bravo End of Month exports already on disk.

Stable copy (2026-09-30) of `Life OS/Reminders Execution 2026-09-30/analyses/layaway_cancellations.py`
(left untouched). The EOM parser `parse()` is byte-for-byte the original's; what changed:
  * importable `compute(month, allow_mtd)` over the report month + the 12 months before it (no fixed range);
  * month files come from `eom_validate.resolve()` exactly as before (wrong-range files are REFUSED);
  * `allow_mtd=True` (used for a mid-month test only) lets the report month fall back to the newest
    month-to-date EOM export whose OWN header starts on the 1st of that month -- labelled "through <date>";
  * a store/month with no trustworthy file is returned in `missing`, never shown as zero.

EOM "Layaways" block, MONTH columns: Balance side = what the customer still OWED; Deposits side = what the
customer had PAID IN. "Kept by us" = Layaway Restocking Fee (Sales section) + Layaway Credit Expirations
(store credit from expired layaways that itself expired). Expired-layaway deposits go to the customer as
layaway store credit (P&P), so they are NOT counted as kept.
"""
import os, sys, glob, re

BASE = '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction'
if not os.path.isdir(BASE):
    _m = glob.glob('/sessions/*/mnt/Projects/Bravo Data Extraction')
    BASE = _m[0] if _m else BASE
sys.path.insert(0, BASE)
import eom_validate as ev, openpyxl

STORES = ['CUL', 'HAR', 'LEX', 'ROA', 'WAY']


def num(v):
    return float(v) if isinstance(v, (int, float)) else 0.0


# ---------------- parse(): copied verbatim from the original (do not edit here without re-verifying) -------------
def parse(path):
    ws = openpyxl.load_workbook(path, data_only=True).active
    R, C = ws.max_row, min(ws.max_column, 70)
    cell = lambda r, c: ws.cell(r, c).value
    # header row: has 'Layaway Balance' and 'Layaway Deposits'
    hr = next(r for r in range(1, R + 1)
              if any(cell(r, c) == 'Layaway Balance' for c in range(1, C + 1))
              and any(cell(r, c) == 'Layaway Deposits' for c in range(1, C + 1)))
    cb = next(c for c in range(1, C + 1) if cell(hr, c) == 'Layaway Balance')
    cd = next(c for c in range(1, C + 1) if cell(hr, c) == 'Layaway Deposits')
    sub = hr + 1
    q = [c for c in range(1, C + 1) if cell(sub, c) == 'Qty']
    mo = [c for c in range(1, C + 1) if cell(sub, c) == 'Month']
    trm = next(c for c in range(1, C + 1) if cell(sub, c) == 'Month' and c < cb)  # Trans QTY month
    bq = [c for c in q if cb <= c < cd][-1]; bm = [c for c in mo if cb <= c < cd][0]
    dq = [c for c in q if c >= cd][-1];      dm = [c for c in mo if c >= cd][0]
    lab_lo = trm - 8
    out = {}
    def label(r):
        for c in range(lab_lo, trm):
            v = cell(r, c)
            if isinstance(v, str) and v.strip() not in ('-', ''):
                return v.strip()
    def side(r, qc, mc, L):
        vals = [cell(r, c) for c in range(qc, mc + 1) if isinstance(cell(r, c), (int, float))]
        if len(vals) >= 2:
            return float(vals[0]), float(vals[-1])
        if len(vals) == 1:
            if L.startswith('Redemptions Sale') and qc == bq:
                return float(vals[0]), 0.0
            return 0.0, float(vals[0])
        return 0.0, 0.0
    end_row = None
    for r in range(sub + 1, sub + 30):
        L = label(r)
        if not L:
            continue
        if L.startswith('Starting Balance') and 'start' not in out:
            out['start'] = dict(bq=num(cell(r, bq)), b=num(cell(r, bm)), dq=num(cell(r, dq)), d=num(cell(r, dm)))
            continue
        if L.startswith('Ending Balance'):
            out['end'] = dict(bq=num(cell(r, bq)), b=num(cell(r, bm)), dq=num(cell(r, dq)), d=num(cell(r, dm)))
            end_row = r
            break
        bqv, bv = side(r, bq, bm, L)
        dqv, dv = side(r, dq, dm, L)
        out[L] = dict(tx=num(cell(r, trm)), bq=bqv, b=bv, dq=dqv, d=dv)
    cr = next((r for r in range(end_row, end_row + 12) if any(cell(r, c) == 'Layaway Credits' for c in range(1, C + 1))), None)
    credits = {}
    if cr:
        for r in range(cr + 2, cr + 20):
            L = label(r)
            if not L:
                continue
            credits[L] = dict(q=num(cell(r, bq)), d=num(cell(r, bm)))
            if L.startswith('Ending Balance'):
                break
    fee = 0.0
    for r in range(1, R + 1):
        if cell(r, 1) == 'Layaway Restocking Fee':
            nums = [cell(r, c) for c in range(2, C + 1) if isinstance(cell(r, c), (int, float))]
            fee = float(nums[-1]) if nums else 0.0
            break
    return out, credits, fee
# ----------------------------------------------------------------------------------------------------------------


def g0(o, k):
    return o.get(k, {}).get('bq', 0)


def gaps(o):
    s, e = o['start'], o['end']
    mov_b = sum(v['b'] for k, v in o.items() if k not in ('start', 'end'))
    mov_d = sum(v['d'] for k, v in o.items() if k not in ('start', 'end'))
    return round(s['b'] + mov_b - e['b'], 2), round(s['d'] + mov_d - e['d'], 2)


def _prev(ym, n=1):
    y, m = map(int, ym.split('-'))
    for _ in range(n):
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    return f'{y}-{m:02d}'


def mtd_file(store, ym):
    """Newest pipeline EOM export whose OWN range starts on the 1st of `ym` and ends inside `ym`."""
    start, end = ev.month_bounds(ym)
    best = None
    for p in glob.glob(os.path.join(BASE, 'output', f'{ym}-*_{store}_end-of-month.xlsx')):
        r = ev.read_range(p)
        if r and r[0] == start and r[1] <= end and (best is None or r[1] > best['range'][1]):
            best = {'path': p, 'source': 'month-to-date', 'range': r}
    return best


def row_from(h):
    o, cr, fee = parse(h['path'])
    gap_n = o['start']['bq'] + sum(g0(o, k) for k in o if k.startswith(('Down Payments', 'Redemptions Sale', 'Expirations', 'Cancellations', 'Reactivations'))) - o['end']['bq']
    gap_b, gap_d = gaps(o)
    g = lambda k: o.get(k, dict(tx=0, bq=0, b=0, dq=0, d=0))
    red = next((v for k, v in o.items() if k.startswith('Redemptions Sale')), dict(bq=0, b=0, d=0))
    return dict(
        source=h['source'], range=list(h['range']), tie_gap=[gap_n, gap_b, gap_d],
        flagged=(abs(gap_n) > 0.5 or abs(gap_b) > 0.02 or abs(gap_d) > 0.02),
        cancel_n=-g('Cancellations')['bq'], cancel_owed=-g('Cancellations')['b'], cancel_deposits=-g('Cancellations')['d'],
        expire_n=-g('Expirations')['bq'], expire_owed=-g('Expirations')['b'], expire_deposits=-g('Expirations')['d'],
        new_n=g('Down Payments')['bq'], new_value=g('New Layaways')['b'],
        completed_n=-red['bq'], completed_value=-red['d'],
        start_n=o['start']['bq'], end_n=o['end']['bq'], end_owed=o['end']['b'], end_deposits=o['end']['d'],
        reactivations_n=g('Reactivations')['bq'],
        exp_to_credit=cr.get('Layaway Expirations to Credit', {}).get('d', 0),
        credits_paid_out=-cr.get('Credits Paid Out', {}).get('d', 0),
        credit_expired=-cr.get('Layaway Credit Expirations', {}).get('d', 0),
        restocking_fee=fee)


def compute(month, allow_mtd=False, history=12):
    months = [_prev(month, i) for i in range(history, -1, -1)]
    rows, missing, failed = {}, [], []
    for ym in months:
        for s in STORES:
            h = ev.resolve(s, ym)
            if not h and allow_mtd and ym == month:
                h = mtd_file(s, ym)
            if not h:
                missing.append(f'{s}|{ym}'); continue
            try:
                rows[f'{s}|{ym}'] = row_from(h)
            except Exception as ex:
                failed.append(f'{s}|{ym}: {ex!r}')
    return dict(month=month, months=months, rows=rows, missing=missing, failed=failed)


if __name__ == '__main__':
    import json
    print(json.dumps(compute(sys.argv[1], allow_mtd='--mtd' in sys.argv), indent=1))
