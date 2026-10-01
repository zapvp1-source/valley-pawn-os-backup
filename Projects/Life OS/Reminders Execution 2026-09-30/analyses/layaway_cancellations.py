#!/usr/bin/env python3
"""
layaway_cancellations.py -- Cancelled (and expired) layaways by store and month (READ-ONLY, additive).
Built 2026-09-30 for Joshua's reminders plan item "cancelled layaways report".
NOT a layaway-yield fix (that is diagnosed in CHANGELOG and awaiting Joshua's call).

Source: the trusted monthly Bravo End of Month report per store (eom_validate.resolve picks the file
whose own date range is exactly the month; wrong-range files are rejected, never used).
From the EOM "Layaways" block, MONTH columns:
  Layaway Balance side  (what the customer still OWED)      -> Qty (layaways) and $ for each line
  Layaway Deposits side (what the customer had PAID IN)     -> Qty and $ for each line
Lines used: Cancellations, Expirations, New Layaways, Redemptions Sale Price (completed), plus the
Layaway Credits block (Layaway Expirations to Credit, Credits Paid Out, Layaway Credit Expirations)
and the Sales-section "Layaway Restocking Fee".
Self-check: count, Balance and Deposit roll-forwards (start + movements = end) are tested for every
store-month; a month that does not tie is KEPT (the cancellation lines are read directly) but flagged
with the size of the gap in `flagged`.
"""
import os, sys, json, datetime as dt

BASE = '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction'
if not os.path.isdir(BASE):
    BASE = '/sessions/loving-great-ramanujan/mnt/Projects/Bravo Data Extraction'
sys.path.insert(0, BASE)
import eom_validate as ev, openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
STORES = ['CUL', 'HAR', 'LEX', 'ROA', 'WAY']
FIRST, LAST = '2024-12', '2026-08'   # Sept 2026 not closed on 9/30


def months():
    y, m = map(int, FIRST.split('-'))
    while f'{y}-{m:02d}' <= LAST:
        yield f'{y}-{m:02d}'
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def num(v):
    return float(v) if isinstance(v, (int, float)) else 0.0


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
    # label lookup: first text cell in the label area (cols before Trans QTY) of each row
    lab_lo = trm - 8
    out = {}
    def label(r):
        for c in range(lab_lo, trm):
            v = cell(r, c)
            if isinstance(v, str) and v.strip() not in ('-', ''):
                return v.strip()
    def side(r, qc, mc, L):
        # Bravo merges cells: a row with no quantity puts its $ in the Qty column. Two numbers in
        # [Qty..Month] = (qty, $); one number = $ -- except 'Redemptions Sale Price' on the
        # Balance side, where the lone number is the count (a paid-off layaway owes $0).
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
    # Layaway Credits block (below)
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
    # restocking fee (Sales Activity section, 'Total' = last numeric in row)
    fee = 0.0
    for r in range(1, R + 1):
        if cell(r, 1) == 'Layaway Restocking Fee':
            nums = [cell(r, c) for c in range(2, C + 1) if isinstance(cell(r, c), (int, float))]
            fee = float(nums[-1]) if nums else 0.0
            break
    return out, credits, fee


def g0(o, k):
    return o.get(k, {}).get('bq', 0)


def gaps(o):
    s, e = o['start'], o['end']
    mov_b = sum(v['b'] for k, v in o.items() if k not in ('start', 'end'))
    mov_d = sum(v['d'] for k, v in o.items() if k not in ('start', 'end'))
    return round(s['b'] + mov_b - e['b'], 2), round(s['d'] + mov_d - e['d'], 2)


if __name__ == '__main__':
    res, missing, failed = {}, [], []
    for ym in months():
        for s in STORES:
            h = ev.resolve(s, ym)
            if not h:
                missing.append(f'{s} {ym}'); continue
            try:
                o, cr, fee = parse(h['path'])
            except Exception as ex:
                failed.append(f'{s} {ym}: parse {ex!r}'); continue
            gap_n = o['start']['bq'] + sum(g0(o, k) for k in o if k.startswith(('Down Payments', 'Redemptions Sale', 'Expirations', 'Cancellations', 'Reactivations'))) - o['end']['bq']
            gap_b, gap_d = gaps(o)
            if abs(gap_n) > 0.5 or abs(gap_b) > 0.02 or abs(gap_d) > 0.02:
                # Bravo's own block does not fully tie (a void/adjustment line the block does not
                # show). The Cancellations/Expirations lines are still read straight from the
                # report; the month is kept but FLAGGED with the size of the gap.
                failed.append(f'{s} {ym}: block off by {gap_n:+.0f} layaways / ${gap_b:+,.2f} owed / ${gap_d:+,.2f} deposits (kept, flagged)')
            g = lambda k: o.get(k, dict(tx=0, bq=0, b=0, dq=0, d=0))
            red = next((v for k, v in o.items() if k.startswith('Redemptions Sale')), dict(bq=0, b=0, d=0))
            res[f'{s}|{ym}'] = dict(
                source=h['source'], tie_gap=[gap_n, gap_b, gap_d],
                cancel_n=-g('Cancellations')['bq'], cancel_owed=-g('Cancellations')['b'], cancel_deposits=-g('Cancellations')['d'],
                expire_n=-g('Expirations')['bq'], expire_owed=-g('Expirations')['b'], expire_deposits=-g('Expirations')['d'],
                new_n=g('Down Payments')['bq'],   # every new layaway takes one down payment
                new_value=g('New Layaways')['b'],
                completed_n=-red['bq'], completed_value=-red['d'],
                start_n=o['start']['bq'], end_n=o['end']['bq'], end_owed=o['end']['b'], end_deposits=o['end']['d'],
                reactivations_n=g('Reactivations')['bq'],
                exp_to_credit=cr.get('Layaway Expirations to Credit', {}).get('d', 0),
                credits_paid_out=-cr.get('Credits Paid Out', {}).get('d', 0),
                credit_expired=-cr.get('Layaway Credit Expirations', {}).get('d', 0),
                restocking_fee=fee)
    json.dump(dict(rows=res, missing=missing, flagged=failed), open(os.path.join(HERE, 'layaway_cancellations_data.json'), 'w'), indent=1)
    print('rows', len(res), 'missing', missing, 'failed', failed)
