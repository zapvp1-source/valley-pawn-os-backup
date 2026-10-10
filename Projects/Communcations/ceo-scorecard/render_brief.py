#!/usr/bin/env python3
"""render_brief.py — renders the one-page Weekly CEO Brief HTML.  Added 2026-10-09.

Every revenue/loan number comes straight from data/REVENUE_<monday>.json (exact-range Bravo pulls), never retyped,
so the headline numbers cannot drift from the source. The weekly task supplies only the narrative (content.json).

usage: python3 render_brief.py REVENUE.json content.json out.html

content.json keys:
  week_label            "Mon Sep 28 - Sun Oct 4, 2026"
  balances              {loan_balance, inventory, layaway, aged_pct, aged_dollars, past_due_pct, past_due_dollars,
                         markdown_items, markdown_dollars}  each may also have <key>_prev for the arrow
  store_extra           {"CUL": {"aged_pct": 14.52, "past_due_pct": 0.0, "flag": "..."}, ...}
  headline              one sentence: the single most important thing this week (judgment, with a number)
  decisions             [ "..."]  max 3 - things only the CEO can decide
  sections              {"Revenue & Sales": [...], "Loans": [...], "Operations": [...], "People": [...],
                         "Marketing": [...], "Real Estate": [...], "Compliance": [...]}  max 3 each (2 for Compliance)
  actions               [ "... - Owner" ] max 5
  watch                 [ "..." ] max 3
  footer                "Last week's list: ... Not published this week: ..."
"""
import json, sys, html

ORDER = ['CUL', 'HAR', 'ROA', 'LEX', 'WAY']
NAMES = {'CUL': 'Culpeper', 'HAR': 'Harrisonburg', 'LEX': 'Lexington', 'ROA': 'Roanoke', 'WAY': 'Waynesboro'}
E = html.escape


def money(v, k=False):
    if v is None: return '—'
    if k and abs(v) >= 10000: return '$%.1fK' % (v / 1000.0)
    return '${:,.0f}'.format(v)


def arrow(p, invert=False, pts=False):
    if p is None: return '<span class="mut">—</span>'
    good = (p >= 0) != invert
    cls = 'up' if good else 'dn'
    sym = '▲' if p >= 0 else '▼'
    unit = ' pt' if pts else '%'
    return '<span class="%s">%s%s%s</span>' % (cls, sym, ('%.1f' % abs(p)).rstrip('0').rstrip('.') if abs(p) < 100 else '%.0f' % abs(p), unit)


def g(d, *ks):
    for k in ks:
        if d is None: return None
        d = d.get(k) if isinstance(d, dict) else None
    return d


CSS = """
@page { size: letter; margin: 0.38in; }
*{box-sizing:border-box}
body{font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;font-size:8.7pt;line-height:1.24;color:#1b1b1f;margin:0}
.hd{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2.5px solid #2D1A5E;padding-bottom:4px;margin-bottom:5px}
.hd h1{font-size:15pt;margin:0;color:#2D1A5E}
.hd .sub{font-size:8.6pt;color:#555;text-align:right}
.headline{background:#2D1A5E;color:#fff;border-radius:5px;padding:4px 9px;font-size:9.2pt;margin-bottom:5px}
.rev{display:grid;grid-template-columns:1.3fr 1.2fr 1fr 1fr 1fr 1fr;gap:5px;margin-bottom:5px}
.k{background:#f3f1f8;border-radius:5px;padding:4px 7px}
.k.hero{background:#e9e4f6;border:1.5px solid #2D1A5E}
.k b{display:block;font-size:12pt;color:#2D1A5E}
.k.hero b{font-size:16pt}
.k span{font-size:7.4pt;color:#555;display:block}
.k i{font-style:normal;font-size:7.3pt;display:block;line-height:1.2}
.bar{height:6px;background:#ddd;border-radius:3px;position:relative;margin-top:3px}
.bar .f{height:6px;background:#2D1A5E;border-radius:3px}
.bar .m{position:absolute;top:-2px;width:2px;height:10px;background:#e8a317}
.bal{display:grid;grid-template-columns:repeat(6,1fr);gap:4px;margin-bottom:5px}
.bal .k b{font-size:10pt}
.up{color:#1a7f37}.dn{color:#b42318}.mut{color:#888}
h2{font-size:9pt;margin:5px 0 2px;color:#2D1A5E;text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid #d9d4e8;padding-bottom:1px}
table{width:100%;border-collapse:collapse;font-size:8.1pt}
th{background:#2D1A5E;color:#fff;text-align:right;padding:2px 4px;font-weight:600}
th:nth-child(-n+2),td:nth-child(-n+2){text-align:left}
td{padding:1.5px 4px;border-bottom:1px solid #e6e3ee;text-align:right}
tr.tot td{font-weight:700;border-top:1.5px solid #2D1A5E}
.flags{font-size:7.6pt;color:#5a4100;margin:2px 0 0}
.cols2{display:grid;grid-template-columns:1.1fr 1fr;gap:0 8px}
.cols2>div{margin-top:4px}
th{white-space:nowrap}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:0 12px}
ul{margin:0 0 1px 12px;padding:0}li{margin-bottom:1.5px}
ol{margin:0 0 1px 14px;padding:0}
.dec{background:#eef6ff;border-left:3px solid #1f5fbf;padding:3px 8px;margin-top:4px}
.act{background:#fff7e6;border-left:3px solid #e8a317;padding:3px 8px;margin-top:4px}
.watch{background:#fdeceb;border-left:3px solid #b42318;padding:3px 8px;margin-top:4px}
.ft{font-size:7.2pt;color:#666;margin-top:4px;border-top:1px solid #ccc;padding-top:2px}
"""


def main(rev_p, con_p, out_p):
    R = json.load(open(rev_p)); C = json.load(open(con_p))
    co = R.get('company', {}); W = co.get('W', {}); MTD = co.get('MTD', {})
    wow = co.get('wow_pct') or {}; yoy = co.get('yoy_pct') or {}; mly = co.get('mtd_vs_ly_pct') or {}
    mt = R.get('month_target', {}); mtc = mt.get('company', {})
    el = mt.get('elapsed_pct')
    h = []
    h.append('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Valley Pawn — Weekly CEO Brief</title><style>%s</style></head><body>' % CSS)
    h.append('<div class="hd"><h1>Valley Pawn — Weekly CEO Brief</h1><div class="sub"><b>%s</b><br>Valley Pawn · Real Estate</div></div>' % E(C['week_label']))
    if C.get('headline'): h.append('<div class="headline">%s</div>' % E(C['headline']))
    # ---- revenue strip (all from REVENUE json)
    pctT = mtc.get('pct_of_target')
    h.append('<div class="rev">')
    h.append('<div class="k hero"><span>NET REVENUE — WEEK</span><b>%s</b><i>%s vs last week<br>%s vs same week last year</i></div>' % (
        money(W.get('net_revenue_bravo_basis')), arrow(wow.get('net_revenue_bravo_basis')), arrow(yoy.get('net_revenue_bravo_basis'))))
    bar = ''
    if pctT is not None and el is not None:
        bar = '<div class="bar"><div class="f" style="width:%.0f%%"></div><div class="m" style="left:%.0f%%"></div></div>' % (min(pctT, 100), min(el, 100))
    h.append('<div class="k"><span>MONTH TO DATE vs TARGET</span><b>%s</b><i>%s of %s target<br>%s of month gone · %s vs LY</i>%s</div>' % (
        money(MTD.get('net_revenue_bravo_basis')), ('%.0f%%' % pctT) if pctT is not None else '—', money(mtc.get('target')),
        ('%.0f%%' % el) if el is not None else '—', arrow(mly.get('net_revenue_bravo_basis')), bar))
    h.append('<div class="k"><span>LOAN FEES (IN STORE)</span><b>%s</b><i>%s WoW · %s YoY<br>+%s MobilePawn</i></div>' % (
        money(W.get('loan_fees_instore')), arrow(wow.get('loan_fees_instore')), arrow(yoy.get('loan_fees_instore')), money(W.get('loan_fees_mobilepawn'))))
    h.append('<div class="k"><span>RETAIL MERCHANDISE</span><b>%s</b><i>%s WoW · %s YoY<br>all-sales margin %s%%</i></div>' % (
        money(W.get('taxable_retail_sales')), arrow(wow.get('taxable_retail_sales')), arrow(yoy.get('taxable_retail_sales')), W.get('gross_margin_pct', '—')))
    h.append('<div class="k"><span>GOLD &amp; SILVER SOLD</span><b>%s</b><i>%s</i></div>' % (
        money(W.get('precious_metal_sales')), ('refinery settlements<br>scrap cost %s' % money(W.get('refined_cost'))) if W.get('refined_cost') else 'no refinery settlement this week'))
    h.append('<div class="k"><span>NEW LOANS WRITTEN</span><b>%s</b><i>%s loans · %s WoW<br>%s redeemed · %s forfeited</i></div>' % (
        money(W.get('new_loans_amt')), W.get('new_loans_count', '—'), arrow(wow.get('new_loans_amt')),
        W.get('redemptions_count', '—'), W.get('forfeited_loans_count', '—')))
    h.append('</div>')
    # ---- balances strip (from content: published channel figures)
    B = C.get('balances', {})
    def bk(lbl, key, fmt, invert=False, pts=False):
        v = B.get(key); pv = B.get(key + '_prev'); a = ''
        if v is not None and pv not in (None, 0):
            a = arrow((v - pv) if pts else 100.0 * (v - pv) / abs(pv), invert, pts)
        return '<div class="k"><span>%s</span><b>%s</b><i>%s</i></div>' % (lbl, fmt(v) if v is not None else '—', a)
    pc = lambda v: '%.2f%%' % v
    h.append('<div class="bal">%s%s%s%s%s%s</div>' % (
        bk('Loan balance', 'loan_balance', money), bk('Inventory', 'inventory', money), bk('Layaway', 'layaway', money),
        bk('Aged 1yr+ (%s)' % money(B.get('aged_dollars')), 'aged_pct', pc, True, True),
        bk('Past-due loans (%s)' % money(B.get('past_due_dollars')), 'past_due_pct', pc, True, True),
        bk('Markdown backlog (%s)' % money(B.get('markdown_dollars')), 'markdown_items', lambda v: '%d items' % v, True)))
    # ---- stores table, ranked on week net revenue
    S = R.get('stores', {}); X = C.get('store_extra', {}); MS = mt.get('stores', {})
    rows = []
    for s in ORDER:
        n = S.get(s, {}); w = n.get('W')
        if not w: continue
        rows.append((w['net_revenue_bravo_basis'], s, n, w))
    rows.sort(reverse=True)
    h.append('<h2>Stores — ranked on this week\'s net revenue</h2><table><tr><th>#</th><th>Store</th><th>Net rev</th><th>WoW</th><th>YoY</th><th>vs target</th><th>Loan fees</th><th>WoW</th><th>Retail</th><th>WoW</th><th>Gold/silver</th><th>New loans</th><th>Aged</th><th>Past-due</th></tr>')
    for i, (_, s, n, w) in enumerate(rows, 1):
        x = X.get(s, {}); m = MS.get(s, {})
        h.append('<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            i, NAMES[s], money(w['net_revenue_bravo_basis']), arrow(g(n, 'wow_pct', 'net_revenue_bravo_basis')),
            arrow(g(n, 'yoy_pct', 'net_revenue_bravo_basis')),
            ('%.0f%%' % m['pct_of_target']) if m.get('pct_of_target') is not None else '—',
            money(w['loan_fees_instore']), arrow(g(n, 'wow_pct', 'loan_fees_instore')),
            money(w['taxable_retail_sales']), arrow(g(n, 'wow_pct', 'taxable_retail_sales')),
            money(w['precious_metal_sales']), money(w['new_loans_amt']),
            ('%.1f%%' % x['aged_pct']) if x.get('aged_pct') is not None else '—',
            ('%.2f%%' % x['past_due_pct']) if x.get('past_due_pct') is not None else '—'))
    if W:
        h.append('<tr class="tot"><td></td><td>Company</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td></td><td></td></tr>' % (
            money(W['net_revenue_bravo_basis']), arrow(wow.get('net_revenue_bravo_basis')), arrow(yoy.get('net_revenue_bravo_basis')),
            ('%.0f%%' % pctT) if pctT is not None else '—', money(W['loan_fees_instore']), arrow(wow.get('loan_fees_instore')),
            money(W['taxable_retail_sales']), arrow(wow.get('taxable_retail_sales')), money(W['precious_metal_sales']), money(W['new_loans_amt'])))
    h.append('</table>')
    fl = ['<b>%s</b> %s' % (NAMES[s], E(X[s]['flag'])) for _, s, _, _ in rows if X.get(s, {}).get('flag')]
    if fl: h.append('<div class="flags">%s</div>' % ' · '.join(fl))
    # ---- narrative
    sec = C.get('sections', {})
    left = ['Revenue & Sales', 'Loans', 'Operations']
    right = ['People', 'Marketing', 'Real Estate', 'Compliance']
    def col(names):
        o = []
        for nm in names:
            items = sec.get(nm) or []
            if not items: continue
            o.append('<h2>%s</h2><ul>%s</ul>' % (E(nm), ''.join('<li>%s</li>' % E(t) for t in items[:3])))
        return ''.join(o)
    h.append('<div class="cols"><div>%s</div><div>%s</div></div>' % (col(left), col(right)))
    if C.get('decisions'):
        h.append('<div class="dec"><b>Decisions for you</b><ol>%s</ol></div>' % ''.join('<li>%s</li>' % E(t) for t in C['decisions'][:3]))
    h.append('<div class="cols2">')
    if C.get('actions'):
        h.append('<div class="act"><b>Do this week</b><ol>%s</ol></div>' % ''.join('<li>%s</li>' % E(t) for t in C['actions'][:5]))
    if C.get('watch'):
        h.append('<div class="watch"><b>Watch</b><ul>%s</ul></div>' % ''.join('<li>%s</li>' % E(t) for t in C['watch'][:3]))
    h.append('</div>')
    h.append('<div class="ft">Net revenue = loan fees collected in store + gross profit on all sales (same basis as store rankings and bonus targets). Retail = taxable merchandise sales; gold &amp; silver = nontaxable metal sales incl. refinery settlements, which land in lumps. MobilePawn fees shown separately. Week = Monday–Sunday, from Bravo. %s</div>' % E(C.get('footer', '')).replace('&amp;amp;','&amp;'))
    h.append('</body></html>')
    open(out_p, 'w').write('\n'.join(h))


if __name__ == '__main__':
    main(*sys.argv[1:4])
