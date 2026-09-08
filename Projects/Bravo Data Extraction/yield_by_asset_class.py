#!/usr/bin/env python3
"""
yield_by_asset_class.py -- Yield decomposed by ASSET CLASS (additive, net-new)
------------------------------------------------------------------------------
Requested by Joshua 2026-09-07.

Decomposes the existing, already-verified store "Yield" metric used by
monthly-bonus-targets into its two underlying asset classes, so the blended
number can be explained instead of just observed.

ESTABLISHED (do not redefine -- monthly-bonus-targets, verified to the penny
against Preston's commission basis 2026-07-16):
    Net Revenue   = PSC + Sales Revenue (Profit)
    PSC           = In-Store Subtotal: Interest + Fees + Misc Charges
    Ending Assets = Ending Loan Base + Ending Inventory Base
    Yield(M)      = Net Revenue(M) / Ending Assets(M-1)

THIS SCRIPT ADDS (an exact decomposition of the above -- the two class yields
weight-average back to the blended yield, so nothing is redefined):
    Loan Yield(M)      = PSC(M)          / Ending Loan Base(M-1)
    Inventory Yield(M) = Sales Profit(M) / Ending Inventory Base(M-1)
    Blended Yield(M)   = Net Revenue(M)  / Ending Assets(M-1)   [unchanged]

LAYAWAY -- deliberately NOT a third yield. See LAYAWAY_YIELD_STATUS.md and the
YIELD_BY_ASSET_CLASS.md note. Layaway merchandise sits inside the Inventory
Base and layaway gross profit is already inside Sales Revenue (Profit), so a
separate layaway yield double-counts. Layaway is reported here only as a
COLLECTION VELOCITY sub-metric of the inventory class:
    Layaway Collection Velocity(M) = (Down Pmts + Payments)(M) / Layaway Bal(M-1)
This is the same numerator/denominator the existing layaway_yield_compile.py
uses; only the label and the placement in the hierarchy differ.

DENOMINATOR CONVENTION: prior-month ENDING balance, matching monthly-bonus-
targets exactly. An average-balance variant is also emitted (avg_* fields) for
sanity-checking, but prior-month-ending is the headline figure everywhere so
the numbers tie to the bonus program.

ANNUALIZATION: monthly yield x 12 (simple, not compounded). Yield here is cash
thrown off by a roughly constant asset base, not a reinvested balance, so
simple x12 is the correct and conventional projection.

ADDITIVE (Rule #4): net-new file. Reads only the already-produced
output/<DATE>_<STORE>_end-of-month.xlsx files from the hardened `end-of-month`
pipeline cell. Touches no handler, no saved report, no pipeline cell, no
existing scheduled task, and pulls nothing live from Bravo.

USAGE:
    python3 yield_by_asset_class.py                 # all available month-ends
    python3 yield_by_asset_class.py 2025-01 2026-08 # inclusive month range

OUTPUT (written to output/):
    yield_by_asset_class.csv    -- one row per store per month + COMPANY rows
    yield_by_asset_class.json   -- same data, machine-readable
"""
import sys, os, glob, json, csv, calendar, re
from datetime import date
import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eom_validate as ev   # shared trust layer -- see eom_validate.py header

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, 'output') + os.sep
STORES = ['CUL', 'HAR', 'LEX', 'ROA', 'WAY']
FULL = {'CUL': 'Culpeper', 'HAR': 'Harrisonburg', 'LEX': 'Lexington',
        'ROA': 'Roanoke', 'WAY': 'Waynesboro'}


def money(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace('$', '').replace(',', '')
    if s in ('', '-'):
        return 0.0
    neg = s.startswith('(') and s.endswith(')')
    s = s.strip('()')
    try:
        val = float(s)
        return -val if neg else val
    except ValueError:
        return None


def reporting_range(ws):
    """Return (start, end) as 'M/D/YYYY' strings from the 'Reporting Dates' header."""
    # NOTE: the range string sits far right (col AY/51 on CUL) and drifts per
    # store -- scan the FULL row width, never a truncated window.
    for r in range(1, 10):
        for c in range(1, ws.max_column + 1):
            v = str(ws.cell(r, c).value or '')
            m = re.search(r'(\d+/\d+/\d{4})\s*-\s*(\d+/\d+/\d{4})', v)
            if m:
                return m.group(1), m.group(2)
    return None


def parse_eom(path, expect_month=None):
    """Extract every figure needed for asset-class yield from one EOM xlsx.

    RANGE GUARD (added 2026-09-07): Bravo's EOM export does NOT always honour the
    requested month -- 2025-08-31 and 2026-08-30/31 came back as a TRAILING-12-MONTH
    range (9/1/prior - 8/31) instead of the month, making every FLOW figure (PSC,
    Sales Profit, layaway collections) ~11x too large. Balances are point-in-time
    and stay correct, but flows do not. Any file whose reporting range does not
    start on day 1 of `expect_month` has its flow fields nulled and is marked
    `range_ok: False` -- never silently consumed. Rule 18: withhold, don't caveat.
    """
    if not os.path.exists(path) or os.path.getsize(path) < 500:
        return None
    ws = openpyxl.load_workbook(path, data_only=True).active
    MR, MC = ws.max_row, ws.max_column

    def nn(r):
        if not r:
            return []
        return [x for x in [ws.cell(r, c).value for c in range(1, MC + 1)]
                if x is not None]

    def find(prefix):
        for r in range(1, MR + 1):
            v = ws.cell(r, 1).value
            if v is not None and str(v).strip().startswith(prefix):
                return r
        return 0

    def find_any(prefix):
        """Label can sit in any column (Bravo offsets some sections)."""
        for r in range(1, MR + 1):
            for c in range(1, MC + 1):
                v = ws.cell(r, c).value
                if v is not None and str(v).strip().startswith(prefix):
                    return r
        return 0

    out = {}

    # --- Asset balances (same rows/indices as the verified bonus_kpis_extract.py)
    L = nn(find('Ending Loan Base'))
    I = nn(find('Ending Inventory Base'))
    out['loan_base'] = money(L[2]) if len(L) > 2 else None
    out['inventory_base'] = money(I[2]) if len(I) > 2 else None

    # --- Loan revenue: In-Store Subtotal Interest + Fees + Misc  (= PSC)
    sub = nn(find('In-Store Subtotal'))
    isInt = (money(sub[4]) or 0) if len(sub) > 4 else 0
    isFee = (money(sub[5]) or 0) if len(sub) > 5 else 0
    isMisc = (money(sub[6]) or 0) if len(sub) > 6 else 0
    out['psc'] = round(isInt + isFee + isMisc, 2)
    out['psc_interest'] = round(isInt, 2)
    out['psc_fees'] = round(isFee, 2)
    out['psc_misc'] = round(isMisc, 2)

    # --- Inventory revenue: Sales Revenue (Profit) = gross sales - COGS
    rev = nn(find_any('Sales Revenue (Profit)'))
    out['sales_profit'] = round((money(rev[-1]) or 0), 2) if rev else 0.0

    # --- Context: total sales + COGS (for margin %)
    ts = nn(find_any('Sales Total'))
    out['sales_total'] = round((money(ts[-1]) or 0), 2) if ts else None
    cg = nn(find_any('COGS'))
    out['cogs'] = round((money(cg[-1]) or 0), 2) if cg else None

    # --- Loan flow context
    nl = nn(find_any('New Loans'))
    out['new_loans'] = round((money(nl[-1]) or 0), 2) if nl else None

    # --- SCRAP / refining. 'Refined (Cost of Sales)' is the cost basis of metal
    # sent to the refiner; it leaves the Inventory Base the same way retail COGS
    # does. Bravo does NOT separate the refinery PROCEEDS -- they are commingled
    # into Total Sales (verified empirically 2026-09-07: gross margin does not
    # fall in heavy-refining months, so the revenue is present, just not
    # separable). So scrap is reported as an INTENSITY metric on the inventory
    # asset, never as its own yield. See YIELD_BY_ASSET_CLASS.md "Scrap".
    rf = nn(find_any('Refined (Cost of Sales)'))
    out['refined_cost'] = round(abs(money(rf[-1]) or 0), 2) if rf else None

    # --- Layaway block (proven anchor logic from layaway_yield_compile.py REV 2)
    lay_row = lb_col = ld_col = None
    for r in range(1, MR + 1):
        hit = False
        for c in range(1, MC + 1):
            v = ws.cell(r, c).value
            if v == 'Layaways':
                lay_row, hit = r, True
            elif v == 'Layaway Balance' and lay_row == r:
                lb_col = c
            elif v == 'Layaway Deposits' and lay_row == r:
                ld_col = c
        if hit and lb_col and ld_col:
            break

    out['layaway_balance'] = out['layaway_down'] = out['layaway_payments'] = None
    if lay_row and lb_col and ld_col:
        def span_last(row):
            if not row:
                return None
            vals = [ws.cell(row, c).value for c in range(lb_col, ld_col)]
            nz = [v for v in vals if v is not None]
            return money(nz[-1]) if nz else None

        down_row = pay_row = end_row = None
        for r in range(lay_row + 1, min(lay_row + 25, MR + 1)):
            for c in range(1, MC + 1):
                v = ws.cell(r, c).value
                if v == 'Down Payments' and down_row is None:
                    down_row = r
                elif v == 'Payments via In-Store Transactions' and pay_row is None:
                    pay_row = r
                elif (v is not None and str(v).strip().startswith('Ending Balance')
                      and end_row is None and r > lay_row):
                    end_row = r
        d, p, b = span_last(down_row), span_last(pay_row), span_last(end_row)
        out['layaway_down'] = round(abs(d), 2) if d is not None else None
        out['layaway_payments'] = round(abs(p), 2) if p is not None else None
        out['layaway_balance'] = round(b, 2) if b is not None else None

    out['net_revenue'] = round(out['psc'] + out['sales_profit'], 2)
    out['ending_assets'] = round((out['loan_base'] or 0) + (out['inventory_base'] or 0), 2)

    # --- RANGE GUARD ---------------------------------------------------------
    rng = reporting_range(ws)
    out['reporting_range'] = ' - '.join(rng) if rng else None
    out['range_ok'] = True
    if expect_month:
        y, m = int(expect_month[:4]), int(expect_month[5:7])
        want_start, want_end = f'{m}/1/{y}', f'{m}/{calendar.monthrange(y, m)[1]}/{y}'
        if not rng or rng[0] != want_start or rng[1] != want_end:
            out['range_ok'] = False
            # Balances are point-in-time and remain valid; FLOWS do not.
            for k in ('psc', 'psc_interest', 'psc_fees', 'psc_misc', 'sales_profit',
                      'sales_total', 'cogs', 'new_loans', 'net_revenue',
                      'layaway_down', 'layaway_payments'):
                out[k] = None
    return out


def month_end(ym):
    y, m = int(ym[:4]), int(ym[5:7])
    return date(y, m, calendar.monthrange(y, m)[1]).isoformat()


def prev_month(ym):
    y, m = int(ym[:4]), int(ym[5:7])
    return f"{y-1}-12" if m == 1 else f"{y}-{m-1:02d}"


def pct(num, den):
    if num is None or den in (None, 0):
        return None
    return round(100.0 * num / den, 2)


def main():
    # Keep the archive current, then let the shared resolver decide which file
    # is trustworthy for each (store, month). Never glob for a filename and
    # trust it -- the pipeline's <END_DATE>_<STORE> naming collides whenever two
    # different date windows share an end date (see eom_validate.py header).
    ev.archive_all(quiet=True)

    # Candidate months = every month the archive holds a genuine full-month
    # export for (start == day 1 AND end == that month's last day).
    cand = set()
    for p in glob.glob(os.path.join(ev.ARCHIVE, '*.xlsx')):
        parts = os.path.basename(p)[:-5].split('_')
        if len(parts) != 3:
            continue
        start, end, store = parts
        if store not in STORES or len(start) != 10 or len(end) != 10:
            continue
        if (start, end) == ev.month_bounds(start[:7]):
            cand.add(start[:7])

    months = sorted(cand)
    if len(sys.argv) >= 3:
        lo, hi = sys.argv[1], sys.argv[2]
        months = [m for m in months if lo <= m <= hi]

    # Resolve + parse every needed month once
    cache, sources = {}, {}
    for ym in set(months) | {prev_month(m) for m in months}:
        for s in STORES:
            hit = ev.resolve(s, ym)
            if hit:
                cache[(ym, s)] = parse_eom(hit['path'], ym)
                sources[(ym, s)] = hit['source']
            else:
                cache[(ym, s)] = None

    # A month is usable only if all 5 stores resolved for BOTH it and its prior
    # month (prior month supplies the denominators). Rule 18: a company figure
    # built from 4 clean stores plus one guess is worse than no figure at all.
    rejected, clean = [], []
    for ym in months:
        pm = prev_month(ym)
        miss_cur = [s for s in STORES if not cache.get((ym, s))]
        miss_pri = [s for s in STORES if not cache.get((pm, s))]
        if miss_cur or miss_pri:
            rejected.append({'month': ym, 'stores': miss_cur or miss_pri,
                             'found_range': 'no file covering the exact month'
                                            + (f' (prior month {pm})' if miss_pri and not miss_cur else '')})
        else:
            clean.append(ym)
    months = clean

    rows = []
    for ym in months:
        pm = prev_month(ym)
        comp_cur = {k: 0.0 for k in ('psc', 'sales_profit', 'net_revenue',
                                     'layaway_down', 'layaway_payments',
                                     'sales_total', 'cogs', 'new_loans',
                                     'refined_cost')}
        comp_prior = {k: 0.0 for k in ('loan_base', 'inventory_base',
                                       'ending_assets', 'layaway_balance')}
        comp_ok = True

        for s in STORES:
            cur, pri = cache.get((ym, s)), cache.get((pm, s))
            if cur is None or pri is None:
                comp_ok = False
                continue
            for k in comp_cur:
                comp_cur[k] += (cur.get(k) or 0)
            for k in comp_prior:
                comp_prior[k] += (pri.get(k) or 0)

            rows.append(build_row(ym, s, FULL[s], cur, pri))

        if comp_ok:
            rows.append(build_row(ym, 'COMPANY', 'Valley Pawn (all 5)',
                                  comp_cur, comp_prior))

    with open(BASE + 'yield_by_asset_class.json', 'w') as f:
        json.dump({'generated': date.today().isoformat(),
                   'months': months, 'rejected_months': rejected,
                   'rows': rows}, f, indent=1)

    if rows:
        with open(BASE + 'yield_by_asset_class.csv', 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    print(f"OK months={len(months)} ({months[0] if months else '-'} .. "
          f"{months[-1] if months else '-'}) rows={len(rows)}")
    from collections import Counter
    used = Counter(v for k, v in sources.items() if k[0] in months)
    if used:
        print('  sources: ' + ', '.join(f'{k}={v}' for k, v in sorted(used.items())))
    for r in rejected:
        print(f"  SKIPPED {r['month']}: {r['found_range']} "
              f"({','.join(r['stores'])})")


def build_row(ym, code, name, cur, pri):
    psc = cur.get('psc') or 0
    sp = cur.get('sales_profit') or 0
    nr = (cur.get('net_revenue') if cur.get('net_revenue') is not None
          else psc + sp)
    lb, ib = pri.get('loan_base'), pri.get('inventory_base')
    ea = pri.get('ending_assets') or ((lb or 0) + (ib or 0))
    lay_prior = pri.get('layaway_balance')
    lay_coll = (cur.get('layaway_down') or 0) + (cur.get('layaway_payments') or 0)
    st, cg = cur.get('sales_total'), cur.get('cogs')

    ly, iy, by = pct(psc, lb), pct(sp, ib), pct(nr, ea)
    return {
        'month': ym, 'store': code, 'store_name': name,
        # denominators (prior month ending)
        'prior_loan_base': round(lb, 2) if lb is not None else None,
        'prior_inventory_base': round(ib, 2) if ib is not None else None,
        'prior_total_assets': round(ea, 2) if ea else None,
        'prior_layaway_balance': round(lay_prior, 2) if lay_prior is not None else None,
        # numerators
        'loan_revenue_psc': round(psc, 2),
        'inventory_gross_profit': round(sp, 2),
        'net_revenue': round(nr, 2),
        'layaway_collected': round(lay_coll, 2),
        # yields (monthly %)
        'loan_yield_mo': ly,
        'inventory_yield_mo': iy,
        'blended_yield_mo': by,
        'layaway_collection_velocity_mo': pct(lay_coll, lay_prior),
        # annualized (simple x12)
        'loan_yield_ann': round(ly * 12, 1) if ly is not None else None,
        'inventory_yield_ann': round(iy * 12, 1) if iy is not None else None,
        'blended_yield_ann': round(by * 12, 1) if by is not None else None,
        # mix + context
        'loan_share_of_assets': pct(lb, ea),
        'inventory_share_of_assets': pct(ib, ea),
        'retail_gross_margin_pct': pct(sp, st) if st else None,
        'sales_total': round(st, 2) if st is not None else None,
        'cogs': round(cg, 2) if cg is not None else None,
        # --- scrap / refining intensity (NOT a yield -- see the note in parse_eom)
        'refined_cost': (round(cur.get('refined_cost'), 2)
                         if cur.get('refined_cost') is not None else None),
        'scrap_share_of_cogs': pct(cur.get('refined_cost'), cg) if cg else None,
        'scrap_burn_of_inventory': pct(cur.get('refined_cost'), ib) if ib else None,
        'new_loans': round(cur.get('new_loans'), 2) if cur.get('new_loans') is not None else None,
    }


if __name__ == '__main__':
    main()
