#!/usr/bin/env python3
"""
render_yield_artifact.py -- regenerate the Yield artifact's data block (ADDITIVE)
================================================================================
Created 2026-09-07.

The published Yield-by-Asset-Class page renders EVERY number -- headline tiles,
tables, chart, and the narrative sentences -- from one embedded JSON blob. This
script recomputes that blob from `output/yield_by_asset_class.csv` and splices it
into the HTML between the /*DATA-START*/ and /*DATA-END*/ markers.

WHY: the first version of the page had ~40 numbers hand-written into prose. A
month later they would all be stale, and stale-but-confident is the failure mode
`vp-operating-rules` Rule 18 exists to prevent. Nothing in the page is hand-typed
any more -- if a figure appears on the page, it came through here.

USAGE:
    python3 render_yield_artifact.py <path-to-html>
    (writes in place; prints OK + the headline figures)

Run AFTER test_yield_by_asset_class.py passes. Never before.
"""
import os, sys, csv, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, 'output', 'yield_by_asset_class.csv')
STORES = ['CUL', 'HAR', 'LEX', 'ROA', 'WAY']
FULL = {'CUL': 'Culpeper', 'HAR': 'Harrisonburg', 'LEX': 'Lexington',
        'ROA': 'Roanoke', 'WAY': 'Waynesboro', 'CO': 'All five stores'}
MONTH = ['', 'January', 'February', 'March', 'April', 'May', 'June',
         'July', 'August', 'September', 'October', 'November', 'December']


def n(v):
    return float(v) if v not in (None, '') else None


def build():
    rows = list(csv.DictReader(open(CSV)))
    months = sorted({r['month'] for r in rows})
    y25 = [m for m in months if m.startswith('2025-')]
    y26 = [m for m in months if m.startswith('2026-')]
    # like-for-like window = the months present in BOTH years
    common = sorted({m[5:7] for m in y25} & {m[5:7] for m in y26})

    def agg(store, mons):
        rs = [r for r in rows if r['store'] == store and r['month'] in mons]
        if not rs:
            return None
        k = len(rs)
        psc = sum(n(r['loan_revenue_psc']) for r in rs)
        igp = sum(n(r['inventory_gross_profit']) for r in rs)
        lb = sum(n(r['prior_loan_base']) for r in rs) / k
        ib = sum(n(r['prior_inventory_base']) for r in rs) / k
        st = sum(n(r['sales_total']) or 0 for r in rs)
        lay = [n(r['prior_layaway_balance']) for r in rs if n(r['prior_layaway_balance'])]
        lc = [n(r['layaway_collected']) for r in rs if n(r['prior_layaway_balance'])]
        laybal = sum(lay) / len(lay) if lay else None
        laycol = sum(lc) / len(lc) if lc else None
        # scrap: refined cost is real; refinery PROCEEDS are not separable in
        # Bravo, so this is intensity, never a yield.
        rf = [n(r['refined_cost']) for r in rs if n(r['refined_cost']) is not None]
        refined = sum(rf) if rf else None
        cogs = sum(n(r['cogs']) or 0 for r in rs)
        return {
            'n': k, 'ly': 100 * psc / lb / k, 'iy': 100 * igp / ib / k,
            'by': 100 * (psc + igp) / (lb + ib) / k, 'share': lb / (lb + ib),
            'lb': lb, 'ib': ib, 'psc': psc, 'igp': igp,
            'mgn': (100 * igp / st) if st else None,
            'laybal': laybal, 'laycol': laycol,
            'layv': (100 * laycol / laybal) if laybal else None,
            'refined': refined, 'cogs': cogs,
            'scrapShare': (100 * refined / cogs) if (refined and cogs) else None,
            'scrapBurn': (100 * (refined / k) / ib) if (refined and ib) else None,
        }

    def rnd(d, keys, p=2):
        # 'share' drives the on-page reconciliation line (share x yield = the
        # blended figure), so it needs 4dp -- 2dp rounds 49.74% to 50% and the
        # arithmetic shown to the reader stops adding up.
        return {k: (round(d[k], 4 if k == 'share' else p)
                    if d.get(k) is not None else None) for k in keys}

    Y = ['ly', 'iy', 'by', 'share']
    like25 = [m for m in y25 if m[5:7] in common]
    like26 = [m for m in y26 if m[5:7] in common]

    stores = []
    for code in STORES + ['COMPANY']:
        a, b = agg(code, like25), agg(code, like26)
        A, B = agg(code, y25), agg(code, y26)
        stores.append({
            'code': 'CO' if code == 'COMPANY' else code,
            'name': FULL['CO' if code == 'COMPANY' else code],
            'l25': rnd(a, Y), 'l26': rnd(b, Y),
            'f25': rnd(A, ['ly', 'iy', 'by']), 'f26': rnd(B, ['ly', 'iy', 'by']),
            'mgn': [round(A['mgn'], 1), round(B['mgn'], 1)],
            'lay': [round(A['laybal']), round(B['laybal']),
                    round(A['laycol']), round(B['laycol']),
                    round(A['layv'], 1), round(B['layv'], 1)],
            # [refined25, refined26, share25, share26, burn25, burn26]
            'scrap': [round(A['refined'] or 0), round(B['refined'] or 0),
                      round(A['scrapShare'] or 0, 1), round(B['scrapShare'] or 0, 1),
                      round(A['scrapBurn'] or 0, 1), round(B['scrapBurn'] or 0, 1)],
        })

    co = next(s for s in stores if s['code'] == 'CO')
    C26, C25 = agg('COMPANY', y26), agg('COMPANY', y25)
    last = months[-1]
    lastrow = [r for r in rows if r['store'] == 'COMPANY' and r['month'] == last][0]

    series = [[r['month'], n(r['loan_yield_mo']), n(r['inventory_yield_mo']),
               n(r['blended_yield_mo'])]
              for r in rows if r['store'] == 'COMPANY']
    series.sort(key=lambda x: x[0])

    # loan-yield band across every store-month (for the "utility not a lever" line)
    ly_all = [n(r['loan_yield_mo']) for r in rows
              if r['store'] != 'COMPANY' and n(r['loan_yield_mo'])]
    st_ly = [s['l26']['ly'] for s in stores if s['code'] != 'CO']
    st_iy = [s['l26']['iy'] for s in stores if s['code'] != 'CO']

    return {
        'span': f'{MONTH[int(months[0][5:7])][:3]} {months[0][:4]} – '
                f'{MONTH[int(last[5:7])][:3]} {last[:4]}',
        'nMonths': len(months),
        'lastMonth': f'{MONTH[int(last[5:7])]} {last[:4]}',
        'like': f'{MONTH[int(common[0])]}–{MONTH[int(common[-1])]}',
        'likeShort': f'Jan–{MONTH[int(common[-1])][:3]}',
        'nLike': len(common),
        'n25': len(y25), 'n26': len(y26),
        'stores': stores,
        'series': series,
        'co': {
            'f26': co['f26'], 'f25': co['f25'], 'l25': co['l25'], 'l26': co['l26'],
            'lb26': round(C26['lb']), 'ib26': round(C26['ib']),
            'tot26': round(C26['lb'] + C26['ib']),
            'share26': round(C26['share'], 4),
            'mgn': co['mgn'], 'layv': [co['lay'][4], co['lay'][5]],
            'layGrowth': round(100 * (co['lay'][1] / co['lay'][0] - 1)),
        },
        'lyBand': [round(min(ly_all), 1), round(max(ly_all), 1)],
        'lyStoreBand': [round(min(st_ly), 1), round(max(st_ly), 1)],
        'iyStoreBand': [round(min(st_iy), 1), round(max(st_iy), 1)],
        'chan': channels(),
        'latest': {
            'asOf': lastrow['month'],
            'lb': round(n(lastrow['prior_loan_base'])),
            'ib': round(n(lastrow['prior_inventory_base'])),
            'lay': round(n(lastrow['prior_layaway_balance'])),
        },
    }


def channels():
    """Channel/sub-channel split from the Company KPI pulls, if present.

    EOM cannot split retail GP from scrap GP -- only Bravo's Company KPI report
    carries that. channel_growth.py writes output/channel_growth.json from the
    `company-kpis` pulls. Absent that file this returns None and the page simply
    omits the section rather than showing a stale or invented split.
    """
    p = os.path.join(HERE, 'output', 'channel_growth.json')
    if not os.path.exists(p):
        return None
    try:
        P = {x['range'][1]: x for x in json.load(open(p))}
    except Exception:
        return None
    # like-for-like: same start month, same end month, one year apart
    pairs = []
    for end, cur in P.items():
        s, e = cur['range']
        if not s or not e:
            continue
        prior_end = f'{int(e[:4])-1}{e[4:]}'
        if prior_end in P and P[prior_end]['range'][0] == f'{int(s[:4])-1}{s[4:]}':
            pairs.append((P[prior_end], cur))
    if not pairs:
        return None
    prior, cur = max(pairs, key=lambda pr: pr[1]['range'][1])

    def nr(d):
        return (d.get('psc') or 0) + (d.get('retail_gp') or 0) + (d.get('scrap_gp') or 0)

    out = {'prior': prior['range'], 'cur': cur['range'], 'stores': []}
    for code in ['TOTAL'] + STORES:
        a, b = prior['data'].get(code), cur['data'].get(code)
        if not a or not b:
            continue
        out['stores'].append({
            'code': code,
            'name': 'All five stores' if code == 'TOTAL' else FULL[code],
            'a': {k: round(a.get(k) or 0) for k in
                  ('psc', 'retail_gp', 'scrap_gp', 'retail_sales', 'scrap_sales')},
            'b': {k: round(b.get(k) or 0) for k in
                  ('psc', 'retail_gp', 'scrap_gp', 'retail_sales', 'scrap_sales')},
            'nrA': round(nr(a)), 'nrB': round(nr(b)),
        })
    return out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path or not os.path.exists(path):
        print('usage: render_yield_artifact.py <path-to-html>')
        sys.exit(1)
    data = build()
    html = open(path, encoding='utf-8').read()
    blob = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    new, cnt = re.subn(r'/\*DATA-START\*/.*?/\*DATA-END\*/',
                       '/*DATA-START*/' + blob + '/*DATA-END*/',
                       html, flags=re.S)
    if cnt != 1:
        print(f'ERROR: found {cnt} data blocks, expected exactly 1 -- not written')
        sys.exit(1)
    open(path, 'w', encoding='utf-8').write(new)
    c = data['co']
    print(f"OK {data['span']} ({data['nMonths']} months) -> {os.path.basename(path)}")
    print(f"   2026 YTD: loan {c['f26']['ly']}% / inv {c['f26']['iy']}% / blended {c['f26']['by']}%")
    print(f"   {data['like']} YoY: {c['l25']['by']}% -> {c['l26']['by']}%")


if __name__ == '__main__':
    main()
