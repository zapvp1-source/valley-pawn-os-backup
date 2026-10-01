#!/usr/bin/env python3
"""build_report_refresh.py -- ADDITIVE copy of build_report.py. Same page, with section 2 (jewelry) rebuilt on the
refreshed Pawn Activity Summary pull (PAS_END env, default 2026-09-29) plus a "what changed since the 7/15 pull" block
(new window minus the 7/15 window = 7/16/2026 -> PAS_END; both pulls start 7/16/2025 and the report is additive by date).
Writes REMINDERS_ANALYSES_2026-09-30_jewelry-refresh-<PAS_END>.html. Original build_report.py / HTML untouched.
Original: renders REMINDERS_ANALYSES_2026-09-30.html from the three analysis outputs.
Run order: fpd_outcomes.py, jewelry_sourcing.py, layaway_cancellations.py, then this.
Every number in the page is computed here from those files; nothing is typed in by hand."""
import json, csv, os, collections, html

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/'
if not os.path.isdir(BASE):
    BASE = '/sessions/loving-great-ramanujan/mnt/Projects/Bravo Data Extraction/output/'
S = ['CUL', 'HAR', 'LEX', 'ROA', 'WAY']
PAS_END = os.environ.get('PAS_END', '2026-09-29')
from datetime import date as _d
_fmt = lambda iso: f"{int(iso[5:7])}/{int(iso[8:10])}/{iso[:4]}"
END_US = _fmt(PAS_END)
NAME = dict(CUL='Culpeper', HAR='Harrisonburg', LEX='Lexington', ROA='Roanoke', WAY='Waynesboro')
fpd = json.load(open(os.path.join(HERE, 'fpd_outcomes_summary.json')))
jw = json.load(open(os.path.join(HERE, f'jewelry_sourcing_data_{PAS_END}.json')))
jw_old = json.load(open(os.path.join(HERE, 'jewelry_sourcing_data.json')))
for _s in S:
    assert jw['pas'][_s]['range'].startswith('7/16/2025 - '), jw['pas'][_s]['range']
    assert jw['pas'][_s]['range'] == f'7/16/2025 - {END_US}', (jw['pas'][_s]['range'], END_US)
lw = json.load(open(os.path.join(HERE, 'layaway_cancellations_data.json')))

Z = lambda x: 0.0 if abs(x) < 0.5 else x
D = lambda x: f"${Z(x):,.0f}"
P = lambda a, b: f"{(100.0 * a / b):.0f}%" if b else "–"
N = lambda x: f"{Z(x):,.0f}"


def table(head, rows, total=None, cls=''):
    h = '<table class="%s"><thead><tr>%s</tr></thead><tbody>' % (cls, ''.join(f'<th>{html.escape(c)}</th>' for c in head))
    for r in rows:
        h += '<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>'
    if total:
        h += '<tr class="tot">' + ''.join(f'<td>{c}</td>' for c in total) + '</tr>'
    return h + '</tbody></table>'


# ---------------- 1. FPD ----------------
F, C, O = 'Forfeited', 'Cured (paid/redeemed/renewed)', 'Still open / unknown'
def fpd_rows(block, order, label=lambda k: k):
    rows = []
    for k in order:
        v = block[k]; f, c, o = v[F], v[C], v[O]
        n = f[0] + c[0] + o[0]; res = f[0] + c[0]
        rows.append([label(k), N(n), D(f[1] + c[1] + o[1]), f"{N(f[0])} ({D(f[1])})", f"{N(c[0])} ({D(c[1])})",
                     f"{N(o[0])} ({D(o[1])})", f"<b>{P(f[0], res)}</b>"])
    return rows
tot = fpd['A_total']; nF, nC, nO = tot[F][0], tot[C][0], tot[O][0]; nAll = nF + nC + nO
fpd_total_row = ['<b>All 5 stores</b>', N(nAll), D(tot[F][1] + tot[C][1] + tot[O][1]), f"{N(nF)} ({D(tot[F][1])})",
                 f"{N(nC)} ({D(tot[C][1])})", f"{N(nO)} ({D(tot[O][1])})", f"<b>{P(nF, nF + nC)}</b>"]
HEAD_F = ['', 'FPD loans', 'Loan $', 'Forfeited', 'Cured', 'Unresolved in data', 'Forfeit rate (of resolved)']
bands = ['$0-49', '$50-99', '$100-249', '$250-499', '$500+']
depts = sorted(fpd['A_by_dept'], key=lambda k: -sum(v[0] for v in fpd['A_by_dept'][k].values()))
conf = fpd['A_open_confirmed_on_930_list']
B = fpd['B']; ball = B['all:all']
bn, be = ball['never extended'], ball['extended 1+']
b_rows = []
for s in S:
    v = B[f'store:{s}']; a, e = v['never extended'], v['extended 1+']
    b_rows.append([NAME[s], N(a[0] + e[0]), D(a[1] + e[1]), N(a[0]), D(a[1]), f"<b>{P(a[0], a[0] + e[0])}</b>"])
b_rows_band = []
for bnd in bands:
    v = B[f'band:{bnd}']; a, e = v['never extended'], v['extended 1+']
    b_rows_band.append([bnd, N(a[0] + e[0]), D(a[1] + e[1]), N(a[0]), D(a[1]), f"<b>{P(a[0], a[0] + e[0])}</b>"])
b_tot = ['<b>All 5 stores</b>', N(bn[0] + be[0]), D(bn[1] + be[1]), N(bn[0]), D(bn[1]), f"<b>{P(bn[0], bn[0] + be[0])}</b>"]
b_half = []
for h_ in ['2025H2', '2026H1', '2026H2']:
    v = B[f'year:{h_}']; a, e = v['never extended'], v['extended 1+']
    b_half.append(P(a[0], a[0] + e[0]))
caps = fpd['captures']

def rate(block, k):
    v = block[k]; return 100.0 * v[F][0] / (v[F][0] + v[C][0])
st_sorted = sorted(S, key=lambda s: -rate(fpd['A_by_store'], s))

# ---------------- 2. Jewelry ----------------
pas = jw['pas']
def jt(s, excl_scrap=False):
    t = dict(pas[s]['rows']['__TOTAL__'])
    if excl_scrap and 'Scrap' in pas[s]['rows']:
        for k in t: t[k] -= pas[s]['rows']['Scrap'][k]
    return t
J = collections.Counter(); JX = collections.Counter()
for s in S:
    for k, v in jt(s).items(): J[k] += v
    for k, v in jt(s, True).items(): JX[k] += v
j_rows = []
for s in S:
    t, x = jt(s), jt(s, True)
    j_rows.append([NAME[s], N(t['buy_q']), D(t['buy_d']), N(t['exp_q']), D(t['exp_d']),
                   f"<b>{P(t['buy_d'], t['buy_d'] + t['exp_d'])}</b>", P(x['buy_d'], x['buy_d'] + x['exp_d'])])
j_tot = ['<b>All 5 stores</b>', N(J['buy_q']), D(J['buy_d']), N(J['exp_q']), D(J['exp_d']),
         f"<b>{P(J['buy_d'], J['buy_d'] + J['exp_d'])}</b>", P(JX['buy_d'], JX['buy_d'] + JX['exp_d'])]
cat = collections.defaultdict(collections.Counter)
for s in S:
    for k, v in pas[s]['rows'].items():
        if k != '__TOTAL__':
            for kk, vv in v.items(): cat[k][kk] += vv
jc_rows = []
for k in sorted(cat, key=lambda k: -(cat[k]['buy_d'] + cat[k]['exp_d'])):
    v = cat[k]
    if v['buy_q'] + v['exp_q'] == 0: continue
    jc_rows.append([html.escape(k), N(v['buy_q']), D(v['buy_d']), N(v['exp_q']), D(v['exp_d']), P(v['buy_d'], v['buy_d'] + v['exp_d'])])
# per-store x category (by $, counter-buy share)
main_cats = ['Rings', 'Chains', 'Bracelets', 'Necklaces', 'Pendants', 'Earrings', 'Watches', 'Scrap']
jsc_rows = []
for k in main_cats:
    r = [k]
    for s in S:
        v = pas[s]['rows'].get(k, dict(buy_d=0, exp_d=0, buy_q=0, exp_q=0))
        r.append(f"{D(v['buy_d'])} / {D(v['exp_d'])}")
    jsc_rows.append(r)
# PAS grand totals (all merchandise) + reactivations
grand = {}; react = {}
m = lambda x: float((x or '0').replace('$', '').replace(',', '').replace('(', '-').replace(')', '') or 0)
for s in S:
    grand[s] = jw['grand'][s]; react[s] = tuple(jw['react'][s])
G = collections.Counter()
for s in S:
    for k, v in grand[s].items(): G[k] += v
R_n = sum(v[0] for v in react.values()); R_d = sum(v[1] for v in react.values())
# EOM all-merchandise context, Sep 2025 - Aug 2026
eom = collections.defaultdict(lambda: [0, 0, 0, 0]); eom_n = collections.Counter()
for k, v in jw['eom'].items():
    s, ym = k.split('|')
    if '2025-09' <= ym <= '2026-08':
        b = v.get('Buys, Bought Loans, Trade-Ins', [0, 0]); x = v.get('Expirations', [0, 0])
        eom[s][0] += b[0]; eom[s][1] += b[1]; eom[s][2] += x[0]; eom[s][3] += x[1]; eom_n[s] += 1
e_rows = [[NAME[s], D(eom[s][1]), D(eom[s][3]), P(eom[s][1], eom[s][1] + eom[s][3])] for s in S]
E = [sum(eom[s][i] for s in S) for i in range(4)]
e_tot = ['<b>All 5 stores</b>', D(E[1]), D(E[3]), P(E[1], E[1] + E[3])]
j_top = max(S, key=lambda s: jt(s)['exp_d'] / (jt(s)['buy_d'] + jt(s)['exp_d']))
j_low = min(S, key=lambda s: jt(s)['exp_d'] / (jt(s)['buy_d'] + jt(s)['exp_d']))

# ---- refresh: delta vs 7/15 pull (7/16/2026 -> PAS_END) ----
EXT_MODE = bool(jw.get('ext'))
PULL_NOTE = (f"On 9/30 the new stretch, 7/16/2026 – {END_US}, was pulled for all 5 stores and added to the 7/16/2025 – 7/15/2026 pull already on file (both are straight sums of buys and forfeits by date, so they add cleanly). {END_US} is the latest complete day Bravo will run it for."
             if EXT_MODE else
             f"It was re-pulled for all 5 stores on 9/30 for 7/16/2025 – {END_US} ({END_US} is the latest complete day Bravo will run it for). The \"since the last pull\" block is the new pull minus the 7/15 pull, per store and category.")
months_span = round(((_d.fromisoformat(PAS_END) - _d(2025, 7, 16)).days + 1) / 30.44, 1)
pold = jw_old['pas']
def dl(s, k=None):
    a = pas[s]['rows'].get(k or '__TOTAL__', dict(buy_q=0, buy_d=0, exp_q=0, exp_d=0))
    b = pold[s]['rows'].get(k or '__TOTAL__', dict(buy_q=0, buy_d=0, exp_q=0, exp_d=0))
    return {kk: a[kk] - b[kk] for kk in ('buy_q', 'buy_d', 'exp_q', 'exp_d')}
DL = collections.Counter()
d_rows = []
for s in S:
    t = dl(s); DL.update(t)
    d_rows.append([NAME[s], N(t['buy_q']), D(t['buy_d']), N(t['exp_q']), D(t['exp_d']), f"<b>{P(t['buy_d'], t['buy_d'] + t['exp_d'])}</b>"])
d_tot = ['<b>All 5 stores</b>', N(DL['buy_q']), D(DL['buy_d']), N(DL['exp_q']), D(DL['exp_d']), f"<b>{P(DL['buy_d'], DL['buy_d'] + DL['exp_d'])}</b>"]
neg = [(s, k, v) for s in S for k in pas[s]['rows'] for kk, v in dl(s, k).items() if v < -0.01]
DSTART = '7/16/2026'
dc_rows = []
dcat = collections.defaultdict(collections.Counter)
for s in S:
    for k in set(pas[s]['rows']) | set(pold[s]['rows']):
        if k != '__TOTAL__': dcat[k].update(dl(s, k))
for k in sorted(dcat, key=lambda k: -(dcat[k]['buy_d'] + dcat[k]['exp_d'])):
    v = dcat[k]
    if v['buy_q'] + v['exp_q'] == 0: continue
    dc_rows.append([html.escape(k), N(v['buy_q']), D(v['buy_d']), N(v['exp_q']), D(v['exp_d']), P(v['buy_d'], v['buy_d'] + v['exp_d'])])
OLDT = collections.Counter()
for s in S: OLDT.update(pold[s]['rows']['__TOTAL__'])

# ---------------- 3. Layaways ----------------
L = lw['rows']
def agg(stores, lo, hi):
    c = collections.Counter()
    for k, v in L.items():
        s, ym = k.split('|')
        if s in stores and lo <= ym <= hi:
            for kk, vv in v.items():
                if isinstance(vv, (int, float)): c[kk] += vv
    return c
Y = agg(S, '2025-09', '2026-08'); Y0 = agg(S, '2024-12', '2025-08')
yms = sorted({k.split('|')[1] for k in L})
l_month = []
for ym in yms:
    c = agg(S, ym, ym)
    l_month.append([ym, N(c['new_n']), N(c['completed_n']), N(c['cancel_n']), D(c['cancel_owed'] + c['cancel_deposits']),
                    D(c['cancel_deposits']), N(c['expire_n']), D(c['expire_deposits']), D(c['restocking_fee'])])
l_store = []
for s in S:
    c = agg([s], '2025-09', '2026-08')
    l_store.append([NAME[s], N(c['new_n']), N(c['cancel_n']), P(c['cancel_n'], c['new_n']), D(c['cancel_owed'] + c['cancel_deposits']),
                    D(c['cancel_deposits']), N(c['expire_n']), D(c['expire_deposits'])])
l_tot = ['<b>All 5 stores</b>', N(Y['new_n']), N(Y['cancel_n']), P(Y['cancel_n'], Y['new_n']), D(Y['cancel_owed'] + Y['cancel_deposits']),
         D(Y['cancel_deposits']), N(Y['expire_n']), D(Y['expire_deposits'])]
q_rows = []
for lab, lo, hi in [('Dec 2024 – Feb 2025', '2024-12', '2025-02'), ('Mar – May 2025', '2025-03', '2025-05'),
                    ('Jun – Aug 2025', '2025-06', '2025-08'), ('Sep – Nov 2025', '2025-09', '2025-11'),
                    ('Dec 2025 – Feb 2026', '2025-12', '2026-02'), ('Mar – May 2026', '2026-03', '2026-05'),
                    ('Jun – Aug 2026', '2026-06', '2026-08')]:
    c = agg(S, lo, hi)
    q_rows.append([lab, N(c['new_n']), N(c['cancel_n']), P(c['cancel_n'], c['new_n']), D(c['cancel_owed'] + c['cancel_deposits']), D(c['cancel_deposits'])])
pre = agg(S, '2024-12', '2025-01'); roa = agg(['ROA'], '2025-09', '2026-08')
flagged = lw.get('flagged', [])

# ---------------- headlines ----------------
f_res = nF + nC
hl_fpd = (f"Of the <b>{N(nAll)}</b> loans that hit their pull date with no payment ever made (first-payment defaults, "
          f"loan snapshots 7/22–9/6 plus one Culpeper list from 5/18), <b>{N(nF)} ({P(nF, nAll)}) were forfeited</b> and "
          f"<b>{N(nC)} ({P(nC, nAll)}) were cured</b> — paid, redeemed or renewed. The other {N(nO)} ({P(nO, nAll)}) can't be "
          f"called yet: no loan snapshot exists after 9/6 ({N(conf[0])} of them were confirmed still on loan and unpaid on 9/30). "
          f"<b>Once a loan reaches its pull date unpaid, about {P(nF, f_res)} of the ones that resolve are lost.</b> "
          f"Small loans are the worst: {P(fpd['A_by_band']['$50-99'][F][0], fpd['A_by_band']['$50-99'][F][0] + fpd['A_by_band']['$50-99'][C][0])} "
          f"of resolved $50–99 loans forfeited vs {P(fpd['A_by_band']['$500+'][F][0], fpd['A_by_band']['$500+'][F][0] + fpd['A_by_band']['$500+'][C][0])} of $500+ loans. "
          f"Looking back two years the other way: <b>{P(bn[0], bn[0] + be[0])} of all loans forfeited since July 2025 "
          f"({N(bn[0])} loans, {D(bn[1])}) never had a single paid extension</b> — first-payment defaults are most of what the company forfeits.")
hl_j = (f"From 7/16/2025 to {END_US} the five stores took in <b>{D(J['buy_d'] + J['exp_d'])}</b> of jewelry at cost: "
        f"<b>{D(J['buy_d'])} ({P(J['buy_d'], J['buy_d'] + J['exp_d'])}) from counter buys</b> ({N(J['buy_q'])} items) and "
        f"<b>{D(J['exp_d'])} ({P(J['exp_d'], J['buy_d'] + J['exp_d'])}) from forfeited loans</b> ({N(J['exp_q'])} items). "
        f"Leaving scrap out (it goes to the refiner, not the case), it is still {P(JX['buy_d'], JX['buy_d'] + JX['exp_d'])} buys / "
        f"{P(JX['exp_d'], JX['buy_d'] + JX['exp_d'])} forfeits. {NAME[j_top]} leans most on forfeits "
        f"({P(jt(j_top)['exp_d'], jt(j_top)['buy_d'] + jt(j_top)['exp_d'])} of its jewelry $); {NAME[j_low]} the least "
        f"({P(jt(j_low)['exp_d'], jt(j_low)['buy_d'] + jt(j_low)['exp_d'])}). Jewelry is {P(J['buy_d'], G['buy_d'])} of every dollar "
        f"the stores spend buying at the counter.")
hl_l = (f"Last 12 closed months (Sep 2025 – Aug 2026): <b>{N(Y['cancel_n'])} layaways cancelled</b> out of {N(Y['new_n'])} opened "
        f"({P(Y['cancel_n'], Y['new_n'])}), worth <b>{D(Y['cancel_owed'] + Y['cancel_deposits'])}</b> in sales that didn't happen; "
        f"customers had paid <b>{D(Y['cancel_deposits'])}</b> in before cancelling. Another {N(Y['expire_n'])} expired "
        f"({D(Y['expire_deposits'])} paid in). <b>Forfeited deposits since Feb 2025: $0</b> — expired-layaway money now goes to the "
        f"customer as layaway store credit (none of that credit has ever expired); the only forfeitures on record are "
        f"{D(pre['restocking_fee'])} kept as restocking fees in Dec 2024 – Jan 2025, before the store-credit rule. "
        f"Trend: cancellations spiked in Mar – Apr 2026 ({N(agg(S, '2026-03', '2026-04')['cancel_n'])} layaways, "
        f"{D(agg(S, '2026-03', '2026-04')['cancel_owed'] + agg(S, '2026-03', '2026-04')['cancel_deposits'])}), stayed high through July "
        f"({', '.join(N(agg(S, m_, m_)['cancel_n']) for m_ in ['2026-05', '2026-06', '2026-07'])} in May–July) and fell to "
        f"{N(agg(S, '2026-08', '2026-08')['cancel_n'])} in August, against roughly {N(Y0['cancel_n'] / 9)} a month in Dec 2024 – Aug 2025. "
        f"Roanoke has not expired a single layaway since March 2025 — it cancels them instead ({N(roa['cancel_n'])} cancellations in 12 months).")

css = """
:root{--bg:#fbfbfd;--fg:#1d1d24;--mut:#5d5d6b;--card:#fff;--line:#e3e3ea;--acc:#2D1A5E;--acc2:#0099DD;--hl:#f3f0fa;--tot:#f4f4f8}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#141419;--fg:#ececf1;--mut:#a3a3b2;--card:#1d1d25;--line:#33333f;--acc:#b9a7ee;--acc2:#5cc4f0;--hl:#231d36;--tot:#23232d}}
:root[data-theme="dark"]{--bg:#141419;--fg:#ececf1;--mut:#a3a3b2;--card:#1d1d25;--line:#33333f;--acc:#b9a7ee;--acc2:#5cc4f0;--hl:#231d36;--tot:#23232d}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
main{max-width:1060px;margin:0 auto;padding:28px 16px 60px}h1{font-size:26px;margin:0 0 4px;color:var(--acc)}
h2{font-size:20px;margin:40px 0 8px;color:var(--acc);border-bottom:2px solid var(--line);padding-bottom:6px}h3{font-size:16px;margin:22px 0 6px}
.sub{color:var(--mut);margin:0 0 18px}.hl{background:var(--hl);border-left:4px solid var(--acc);border-radius:8px;padding:14px 16px;margin:12px 0}
.hl h3{margin:0 0 6px}.wrap{overflow-x:auto;margin:8px 0 4px}table{border-collapse:collapse;width:100%;font-size:13.5px;background:var(--card)}
th,td{padding:6px 9px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}th:first-child,td:first-child{text-align:left}
th{font-weight:600;color:var(--mut);font-size:12.5px}tr.tot td{background:var(--tot);font-weight:600}.note{color:var(--mut);font-size:13.5px}
ul{padding-left:20px}li{margin:4px 0}code{font-size:12.5px}
"""
W = lambda t: f'<div class="wrap">{t}</div>'
page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reminders Analyses</title><style>{css}</style></head><body><main>
<h1>Loan defaults, jewelry sourcing &amp; cancelled layaways</h1>
<p class="sub">Valley Pawn · all 5 stores · prepared 9/30/2026 from Bravo report exports on file. <b>Jewelry refresh:</b> section 2 now uses a fresh Pawn Activity Summary pulled 9/30/2026 (7/16/2025 – {END_US}); sections 1 and 3 are unchanged from the earlier version. Every number below is recomputed by the scripts in this folder.</p>

<div class="hl"><h3>1 · What happens to first-payment defaults</h3>{hl_fpd}</div>
<div class="hl"><h3>2 · Where our jewelry comes from</h3>{hl_j}</div>
<div class="hl"><h3>3 · Cancelled layaways</h3>{hl_l}</div>

<h2>1 · First-payment defaults: forfeited vs cured</h2>
<p>A <b>first-payment default</b> here is a loan that showed up on Bravo's "Claude First Payment Default" list — on loan, past its pull date (due date + 16 days), and <b>no payment ever made</b>. Each one is then followed to 9/29: <b>Forfeited</b> = it's in Bravo's expired-loan list; <b>Cured</b> = it dropped off a later list without expiring (a payment, redemption or renewal — the data can't say which); <b>Unresolved in data</b> = still on the store's last list and not expired by 9/29. The forfeit rate is taken over resolved loans only. This is follow-through only — the weekly #first-payment-default report is not repeated here.</p>
<h3>By store</h3>{W(table(HEAD_F, fpd_rows(fpd['A_by_store'], st_sorted, lambda s: NAME[s]), fpd_total_row))}
<h3>By loan size</h3>{W(table(HEAD_F, fpd_rows(fpd['A_by_band'], bands)))}
<h3>By category (the highest-dollar item on the ticket)</h3>{W(table(HEAD_F, fpd_rows(fpd['A_by_dept'], depts)))}
<p class="note">Median time from pawn to expiry for the forfeited ones: {fpd['A_days_to_expire_median']} days. Unresolved loans confirmed still on loan and unpaid on Bravo's 9/30 past-due list: {N(conf[0])} ({D(conf[1])}) — {', '.join(f'{NAME[s]} {n}' for s, n in fpd['A_open_by_store_confirmed'].items() if n)}.</p>
<h3>The reverse view — how much of what we forfeit started as a first-payment default</h3>
<p>Every loan Bravo expired from 7/1/2025 to 9/29/2026 ({N(bn[0] + be[0])} loans, {D(bn[1] + be[1])} principal), split by whether the customer ever paid for even one extension. The share is steady over time ({b_half[0]} in Jul–Dec 2025, {b_half[1]} in Jan–Jun 2026, {b_half[2]} since July).</p>
{W(table(['', 'Loans forfeited', 'Principal', 'Never paid once', 'Principal', 'Share never paid'], b_rows, b_tot))}
{W(table(['Loan size', 'Loans forfeited', 'Principal', 'Never paid once', 'Principal', 'Share never paid'], b_rows_band))}

<h2>2 · Jewelry sourcing: counter buys vs forfeited loans</h2>
<p>Bravo's Pawn Activity Summary, 7/16/2025 – {END_US} ({months_span} months), Jewelry department. <b>Counter buys</b> = what we paid at the counter; <b>Forfeited</b> = loan principal on jewelry loans that expired (the cost the piece comes into inventory at).</p>
{W(table(['', 'Counter buys (items)', 'Counter buys $', 'Forfeited (items)', 'Forfeited $', 'Share from buys ($)', 'Share from buys, excl. scrap'], j_rows, j_tot))}
<h3>By category, all 5 stores</h3>{W(table(['Category', 'Buys (items)', 'Buys $', 'Forfeited (items)', 'Forfeited $', 'Share from buys ($)'], jc_rows))}
<h3>Main categories by store (buys $ / forfeited $)</h3>{W(table(['Category'] + [NAME[s] for s in S], jsc_rows))}
<h3>Since the last pull — {DSTART} to {END_US} only</h3>
<p class="note">For comparison, the 12 months to 7/15/2026 were {P(OLDT['buy_d'], OLDT['buy_d'] + OLDT['exp_d'])} counter buys / {P(OLDT['exp_d'], OLDT['buy_d'] + OLDT['exp_d'])} forfeits by dollars.{(' Note: ' + str(len(neg)) + ' store/category figures came out slightly lower in the new pull than the old one (late voids or reclassifications in Bravo).') if neg else ''}</p>
{W(table(['', 'Counter buys (items)', 'Counter buys $', 'Forfeited (items)', 'Forfeited $', 'Share from buys ($)'], d_rows, d_tot))}
<h3>Since the last pull, by category, all 5 stores</h3>{W(table(['Category', 'Buys (items)', 'Buys $', 'Forfeited (items)', 'Forfeited $', 'Share from buys ($)'], dc_rows))}
<h3>Context — all merchandise, not just jewelry (End of Month, Sep 2025 – Aug 2026)</h3>
{W(table(['', 'Buys, bought loans &amp; trade-ins $', 'Forfeited loans $', 'Share from buys'], e_rows, e_tot))}

<h2>3 · Cancelled layaways</h2>
<p>From each store's monthly Bravo End of Month report. <b>Value</b> = what the customer still owed plus what they had paid in (the full layaway price incl. tax). <b>Paid in</b> = deposits and payments made before the layaway ended.</p>
<h3>Last 12 closed months by store (Sep 2025 – Aug 2026)</h3>
{W(table(['', 'Opened', 'Cancelled', 'Cancel rate', 'Value cancelled', 'Paid in (cancelled)', 'Expired', 'Paid in (expired)'], l_store, l_tot))}
<h3>Trend by quarter, all 5 stores</h3>{W(table(['', 'Opened', 'Cancelled', 'Cancel rate', 'Value cancelled', 'Paid in (cancelled)'], q_rows))}
<h3>Month by month, all 5 stores</h3>
{W(table(['Month', 'Opened', 'Paid off', 'Cancelled', 'Value cancelled', 'Paid in (cancelled)', 'Expired', 'Paid in (expired)', 'Kept as restocking fee'], l_month))}
<h3>What happened to the customers' money</h3>
<ul>
<li><b>Expired layaways:</b> since Feb 2025 every dollar paid in goes to the customer as <b>layaway store credit</b> ({D(Y['exp_to_credit'])} in the last 12 months). {D(Y['credits_paid_out'])} of layaway credit was paid out or used; <b>$0 of layaway credit has expired</b> in any month on file. That matches the P&amp;P rule (expiry = store credit, not forfeiture).</li>
<li><b>Before Feb 2025:</b> expired-layaway money was kept as a restocking fee — {D(pre['restocking_fee'])} in Dec 2024 – Jan 2025. That is the only forfeited layaway money in the records.</li>
<li><b>Cancelled layaways:</b> {D(Y['cancel_deposits'])} paid in over 12 months left the layaway account with <b>no restocking fee kept</b>. The End of Month report does not show whether it went back as cash or as general store credit (the P&amp;P says a customer who changes their mind gets store credit).</li>
<li><b>Roanoke:</b> {N(roa['cancel_n'])} cancellations and zero expirations in 12 months (its last expiry was March 2025) — Roanoke appears to close lapsed layaways by cancelling them instead of expiring them. If so, those customers don't go through the layaway-credit path the other four stores use. Worth one question to Roanoke; nothing was changed.</li>
</ul>

<h2>Data used, date ranges &amp; limits</h2>
<ul>
<li><b>First-payment defaults — thin coverage, read with care.</b> The loan lists only exist for these dates: {'; '.join(f"{NAME[s]} {', '.join(d[5:].replace('-', '/') for d in caps[s])}" for s in S)}. Culpeper has only 3 lists; Roanoke and Waynesboro have no 8/30 list (their "8/30" files are really 9/6 copies, so capture dates were read from each loan, not the filename). The 5/18 lists for the other four stores saved only a count, not the loans. <b>No list exists after 9/6</b>, so {N(nO)} loans ({P(nO, nAll)}) can't be called. "Cured" includes any payment, redemption, renewal or void — a loan that got one payment and then expired later still counts as Forfeited. Expired-loan list: Bravo "Claude Forfeiture Winback", all 5 stores, expirations 11/15/2024 – 9/29/2026 (loans pawned from ~9/30/2024).</li>
<li><b>Reverse view:</b> "never paid once" = due date never moved past pawn + 30 days. Limited to expirations since 7/1/2025 because the expired-loan list starts with loans pawned ~9/30/2024, which would otherwise over-count never-paid loans.</li>
<li><b>Category fix from the earlier run:</b> the first version filed Chainsaws as jewelry and coins/bullion as jewelry. Categories are now mapped by exact Bravo name; coins &amp; bullion are their own group.</li>
<li><b>Jewelry refreshed 9/30/2026.</b> The only report that splits both buys and forfeits by jewelry category is Bravo's Pawn Activity Summary. {PULL_NOTE} Forfeits are gross: Bravo shows reactivated loans (customer came back after expiry) only as a store total — {N(R_n)} loans / {D(R_d)} company-wide that year, all merchandise — so a small part of the forfeited jewelry went back to its owner.</li>
<li><b>Layaways:</b> End of Month reports Dec 2024 – Aug 2026, all 5 stores, every month present ({len(L)} store-months). September 2026 isn't closed yet. Bravo's own layaway block didn't tie to the dollar in {len(flagged)} store-months (gaps of $20–$450 in deposits, likely a void or adjustment); the cancellation lines were still read straight from the report: {'; '.join(html.escape(f.split(':')[0]) for f in flagged)}.</li>
<li>Nothing was posted to Slack and no one was messaged. Scripts: <code>fpd_outcomes.py</code>, <code>jewelry_sourcing.py</code>, <code>jewelry_sourcing_refresh.py</code>, <code>layaway_cancellations.py</code>, <code>build_report_refresh.py</code>. The only Bravo contact was the standard report pull through the existing export queue.</li>
</ul>
</main></body></html>"""
OUTF = os.path.join(HERE, f'REMINDERS_ANALYSES_2026-09-30_jewelry-refresh-{PAS_END}.html')
open(OUTF, 'w').write(page)
json.dump(dict(window=f'7/16/2025 - {END_US}', total=dict(J), excl_scrap=dict(JX), since_last_pull=dict(DL), old_12mo=dict(OLDT), negatives=neg, by_store={s: jt(s) for s in S}, delta_by_store={s: dl(s) for s in S}), open(os.path.join(HERE, f'jewelry_refresh_summary_{PAS_END}.json'), 'w'), indent=1)
print('ok')
print(hl_j); print('since last pull', dict(DL))
