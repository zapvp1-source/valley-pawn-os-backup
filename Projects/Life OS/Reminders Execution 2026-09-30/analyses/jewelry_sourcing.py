#!/usr/bin/env python3
"""
jewelry_sourcing.py -- Where does our jewelry come from: counter buys vs. forfeited loans
(READ-ONLY, additive; built 2026-09-30 for Joshua's reminders plan).

Sources (existing Bravo pipeline output only -- never drives Bravo):
 1. output/2026-07-15_<STORE>_pawn-activity-summary.csv  -- Bravo "Pawn Activity Summary",
    7/16/2025 - 7/15/2026, per store, per jewelry sub-category: Buys (qty, $ paid) and
    Expirations (qty, $ loan principal = the cost the item enters inventory at).
    This is the only report in the pipeline that splits BOTH sources by jewelry category.
 2. Trusted monthly End-of-Month files (via eom_validate.resolve) -- ALL merchandise, not just
    jewelry: "Buys, Bought Loans, Trade-Ins" vs "Expirations" added to the Inventory Base,
    Dec 2024 - Aug 2026, used as the longer-run company context.
"""
import csv, os, sys, json, collections, re

OUTDIR = '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction'
if not os.path.isdir(OUTDIR):
    OUTDIR = '/sessions/loving-great-ramanujan/mnt/Projects/Bravo Data Extraction'
OUT = OUTDIR + '/output/'
HERE = os.path.dirname(os.path.abspath(__file__))
STORES = ['CUL', 'HAR', 'LEX', 'ROA', 'WAY']


def m(s):
    s = (s or '').replace('$', '').replace(',', '').strip()
    neg = s.startswith('(')
    s = s.strip('()')
    return (-1 if neg else 1) * float(s or 0)


def pas(store):
    rows = list(csv.reader(open(OUT + f'2026-07-15_{store}_pawn-activity-summary.csv', encoding='utf-8', errors='replace')))
    rng = next((r[-1] for r in rows[:4] if any('Reporting Dates' in c for c in r)), '')
    hdr = next(r for r in rows if r and r[0] == 'Department')
    # column index of each group header
    gi = {h: i for i, h in enumerate(hdr) if h}
    b, e = gi['Buys'], gi['Expirations']
    out, dept = {}, None
    for r in rows:
        if not r or not r[0]:
            continue
        if len(r) == 1 or all(c == '' for c in r[1:]):
            dept = r[0]; continue
        if dept == 'Jewelry' and r[0] != 'Total:':
            out[r[0]] = dict(buy_q=int(m(r[b])), buy_d=m(r[b + 1]), exp_q=int(m(r[e])), exp_d=m(r[e + 1]))
        if dept == 'Jewelry' and r[0] == 'Total:':
            out['__TOTAL__'] = dict(buy_q=int(m(r[b])), buy_d=m(r[b + 1]), exp_q=int(m(r[e])), exp_d=m(r[e + 1]))
            dept = None
    # self-check: sub-rows sum to the Jewelry total
    t = out['__TOTAL__']
    for k in ['buy_q', 'buy_d', 'exp_q', 'exp_d']:
        s = sum(v[k] for n, v in out.items() if n != '__TOTAL__')
        assert abs(s - t[k]) < 0.02, (store, k, s, t[k])
    return rng, out


def eom_context():
    sys.path.insert(0, OUTDIR)
    import eom_validate as ev, openpyxl
    res = {}
    ym = '2024-12'
    while ym <= '2026-08':
        for s in STORES:
            h = ev.resolve(s, ym)
            if not h:
                continue
            ws = openpyxl.load_workbook(h['path'], data_only=True).active
            # month columns = the 'Qty','Month' pair on the Inventory Base header row
            hr = next(r for r in range(1, ws.max_row + 1) if ws.cell(r, 1).value == 'Inventory Base')
            qtys = [c for c in range(2, 30) if ws.cell(hr, c).value == 'Qty']
            dc = next(c for c in range(2, 30) if ws.cell(hr, c).value == 'Month')
            qc = qtys[-1]               # last 'Qty' = month Qty; 'Month' = month $
            vals = {}
            for r in range(hr, hr + 25):
                lab = ws.cell(r, 1).value
                if lab in ('Buys, Bought Loans, Trade-Ins', 'Expirations') and lab not in vals:
                    q = next((ws.cell(r, c).value for c in range(qc, dc) if isinstance(ws.cell(r, c).value, (int, float))), 0)
                    d = next((ws.cell(r, c).value for c in range(dc, dc + 6) if isinstance(ws.cell(r, c).value, (int, float))), 0)
                    vals[lab] = (q, d)
            res[(s, ym)] = vals
        y, mo = int(ym[:4]), int(ym[5:])
        ym = f'{y + 1}-01' if mo == 12 else f'{y}-{mo + 1:02d}'
    return res


if __name__ == '__main__':
    result = {'pas': {}, 'eom': {}}
    for s in STORES:
        rng, d = pas(s)
        result['pas'][s] = {'range': rng, 'rows': d}
    try:
        e = eom_context()
        result['eom'] = {f'{s}|{ym}': v for (s, ym), v in e.items()}
    except Exception as ex:
        result['eom_error'] = repr(ex)
    json.dump(result, open(os.path.join(HERE, 'jewelry_sourcing_data.json'), 'w'), indent=1)
    # console summary
    for s in STORES:
        t = result['pas'][s]['rows']['__TOTAL__']; sc = result['pas'][s]['rows'].get('Scrap', dict(buy_q=0, buy_d=0, exp_q=0, exp_d=0))
        print(s, result['pas'][s]['range'], t, 'scrap', sc)
