#!/usr/bin/env python3
"""
loan_layaway_outcomes.py -- MONTHLY "Loan & Layaway Outcomes" report (Valley Pawn, all 5 stores).
Built 2026-09-30. Type B: reads Bravo pipeline CSVs / End of Month exports already on disk; NEVER drives Bravo,
never drops a trigger, never re-runs a pull.

  Section 1  First-payment-default loans (on loan, past pull date, never paid) -> share forfeited / cured /
             still open, by store and loan-size band; plus the share of loans that EXPIRED in the month
             that never had a single payment.                                 (bin/lo_outcomes_fpd.py)
  Section 2  Cancelled vs expired layaways by store, money paid in, money kept, 13-month trend.
                                                                              (bin/lo_outcomes_layaway.py)
Both modules are stable copies of the 2026-09-30 reminders analyses (`Life OS/Reminders Execution 2026-09-30/
analyses/`), verified to reproduce that report's numbers exactly.

Usage:
  python3 loan_layaway_outcomes.py                     # prior calendar month (the scheduled run on the 2nd)
  python3 loan_layaway_outcomes.py --month 2026-09     # a specific month
  --mtd     allow the report month's layaway numbers to come from a month-to-date export (test / mid-month only)
  --test    label the message "TEST —" and write <month>-TEST.* files (never touches the real .sent marker)
  --send    write the fleet-outbox envelope to Joshua (Goldilocks bot) and the .sent marker; refuses if .sent exists
Prints one line: MONTH=<ym> COMPLETE=<bool> USABLE=<bool> MISSING=<n> FILE=<mrkdwn path> [SENT=<envelope>|ALREADY_SENT]
Writes Valley Pawn OS/loan-layaway-outcomes/<ym>[-TEST].{html,mrkdwn.txt,slack.txt,json} + RUN_LOG.md line.
"""
import os, sys, json, html, glob, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lo_outcomes_fpd as FP
import lo_outcomes_layaway as LW

OS_DIR = os.path.dirname(HERE)
OUTDIR = os.path.join(OS_DIR, 'loan-layaway-outcomes')
HOST_PROJECTS = '/Users/joshuadavis/Documents/Claude/Projects'
JOSHUA = 'U03BB52MDSA'
S = FP.STORES
NAME = dict(CUL='Culpeper', HAR='Harrisonburg', LEX='Lexington', ROA='Roanoke', WAY='Waynesboro')
F, C, O = FP.F, FP.C, FP.O
BANDLAB = {'$0-49': '$0–49', '$50-99': '$50–99', '$100-249': '$100–249', '$250-499': '$250–499', '$500+': '$500+'}


def host_path(p):
    """Envelope paths must be HOST paths even when this runs inside a session mount."""
    i = p.find('/mnt/Projects/')
    return HOST_PROJECTS + p[i + len('/mnt/Projects'):] if p.startswith('/sessions/') and i >= 0 else p


Z = lambda x: 0.0 if abs(x) < 0.5 else x
D = lambda x: f"${Z(x):,.0f}"
N = lambda x: f"{Z(x):,.0f}"
PC = lambda a, b: f"{(100.0 * a / b):.0f}%" if b else "–"
md = lambda d: f"{int(d[5:7])}/{int(d[8:10])}"                 # '2026-09-06' -> '9/6'
mon = lambda ym: dt.date(int(ym[:4]), int(ym[5:]), 1).strftime('%B %Y')
mon3 = lambda ym: dt.date(int(ym[:4]), int(ym[5:]), 1).strftime('%b %Y')


def prior_month(today=None):
    t = today or dt.date.today()
    return (t.replace(day=1) - dt.timedelta(1)).strftime('%Y-%m')


def build(month, mtd=False, test=False):
    fp = FP.compute(month)
    lw = LW.compute(month, allow_mtd=mtd)
    m_last = fp['month_last']
    R = lw['rows']

    # ---------- completeness (Rule 18: name what is missing; never show it as zero) ----------
    missing_notes = []
    lay_missing = [s for s in S if f'{s}|{month}' not in R]
    fpd_missing = fp['stores_missing_fpd']
    exp_missing = fp['stores_missing_expired']
    exp_dates = fp['expired_list_dates']
    exp_through = min(exp_dates.values()) if exp_dates else None
    exp_full = bool(exp_through and exp_through >= m_last)
    lay_ranges = {s: R[f'{s}|{month}']['range'] for s in S if f'{s}|{month}' in R}
    lay_through = min(r[1] for r in lay_ranges.values()) if lay_ranges else None
    lay_full = bool(lay_through and lay_through >= m_last)
    for s in lay_missing:
        missing_notes.append(f"{NAME[s]}: the {mon(month).split()[0]} layaway numbers aren't in yet.")
    for s in exp_missing:
        missing_notes.append(f"{NAME[s]}: the expired-loan list isn't in yet.")
    for s in fpd_missing:
        missing_notes.append(f"{NAME[s]}: no first-payment-default loan lists on file.")
    latest_fpd = max((d for v in fp['fpd_captures'].values() for d in v), default=None)
    complete = not (lay_missing or exp_missing or fpd_missing) and exp_full and lay_full
    usable = len(lay_missing) < 5 or len(exp_missing) < 5

    # ---------- section 1 numbers ----------
    tot = fp['total']; nF, nC, nO = tot[F][0], tot[C][0], tot[O][0]; nAll = nF + nC + nO
    def res_rate(v):
        return PC(v[F][0], v[F][0] + v[C][0])
    LB = fp['lensB']
    def lb(key, ym):
        v = LB.get(f'{key}|{ym}', {'never': [0, 0.0], 'ext': [0, 0.0]})
        return v['never'], v['ext']
    mn, me = lb('all', month)
    prev12 = [m for m in fp['lensB_months'] if m != month]
    pn = sum(lb('all', m)[0][0] for m in prev12); pe = sum(lb('all', m)[1][0] for m in prev12)
    b50, b500 = fp['by_band'].get('$50-99'), fp['by_band'].get('$500+')

    # ---------- section 2 numbers ----------
    def lay(stores, ym):
        c = dict(new_n=0, cancel_n=0, cancel_val=0.0, cancel_dep=0.0, expire_n=0, expire_dep=0.0, kept=0.0,
                 fee=0.0, credit_exp=0.0, completed_n=0, have=0)
        for s in stores:
            v = R.get(f'{s}|{ym}')
            if not v:
                continue
            c['have'] += 1
            c['new_n'] += v['new_n']; c['cancel_n'] += v['cancel_n']; c['cancel_val'] += v['cancel_owed'] + v['cancel_deposits']
            c['cancel_dep'] += v['cancel_deposits']; c['expire_n'] += v['expire_n']; c['expire_dep'] += v['expire_deposits']
            c['fee'] += v['restocking_fee']; c['credit_exp'] += v['credit_expired']; c['completed_n'] += v['completed_n']
        c['kept'] = c['fee'] + c['credit_exp']
        return c
    LM = lay(S, month)
    hist = [m for m in lw['months'] if m != month]
    full_hist = [m for m in hist if all(f'{s}|{m}' in R for s in S)]
    avg_cancel = sum(lay(S, m)['cancel_n'] for m in full_hist) / len(full_hist) if full_hist else None
    avg_expire = sum(lay(S, m)['expire_n'] for m in full_hist) / len(full_hist) if full_hist else None

    lay_label = mon(month).split()[0] if lay_full else f"{mon(month).split()[0]} 1–{int(lay_through[8:])}" if lay_through else mon(month).split()[0]
    exp_label = mon(month).split()[0] if exp_full else f"{mon(month).split()[0]} (through {md(exp_through)})" if exp_through else mon(month).split()[0]
    prefix = 'TEST — ' if test else ''

    # ---------- Slack message (Slack mrkdwn; plain English, one line per store) ----------
    L = [f"*{prefix}Loan & Layaway Outcomes — {mon(month)}*", ""]
    L.append(f"*Loans never paid on:* of {N(nAll)} loans that reached their pull date with no payment made, "
             f"{N(nF)} were forfeited, {N(nC)} were paid, redeemed or renewed, and {N(nO)} can't be called yet — "
             f"*{PC(nF, nF + nC)} of the ones that resolved were lost.* {N(fp['forfeited_in_month'])} of them were forfeited in {mon(month).split()[0]}.")
    if b50 and b500:
        L.append(f"By loan size: {res_rate(b50)} of $50–99 loans were lost vs {res_rate(b500)} of $500+ loans.")
    if mn[0] + me[0]:
        L.append(f"Of the {N(mn[0] + me[0])} loans that expired in {exp_label}, *{N(mn[0])} ({PC(mn[0], mn[0] + me[0])}) never had a single payment* "
                 f"(prior 12 months: {PC(pn, pn + pe)}).")
    if LM['have']:
        trend = f" (about {N(avg_cancel)} cancelled and {N(avg_expire)} expired a month over the prior 12 months)" if avg_cancel is not None else ""
        partial = "" if lay_full else " — month not closed yet"
        L.append(f"*Layaways, {lay_label}{partial}:* {N(LM['cancel_n'])} cancelled ({D(LM['cancel_dep'])} paid in), "
                 f"{N(LM['expire_n'])} expired ({D(LM['expire_dep'])} paid in, returned as store credit), "
                 f"{D(LM['kept'])} kept by us{trend}.")
    L.append("")
    for s in S:
        v = fp['by_store'].get(s)
        parts = []
        if v:
            parts.append(f"no-payment loans lost {res_rate(v)} ({v[F][0]} of {v[F][0] + v[C][0]} resolved, {v[O][0]} still open)")
        else:
            parts.append("no first-payment-default lists on file")
        if s in exp_dates:
            a, e = lb(s, month)
            parts.append(f"{exp_label.split(' (')[0]} expirations never paid {PC(a[0], a[0] + e[0])} ({a[0]} of {a[0] + e[0]})" if a[0] + e[0] else f"no loans expired in {exp_label.split(' (')[0]}")
        else:
            parts.append("expired-loan list not in yet")
        c = lay([s], month)
        if c['have']:
            parts.append(f"layaways {N(c['cancel_n'])} cancelled / {N(c['expire_n'])} expired, {D(c['kept'])} kept")
        else:
            parts.append("layaway numbers not in yet")
        L.append(f"• *{NAME[s]}* — " + " · ".join(parts))
    notes = []
    if latest_fpd and (dt.date.fromisoformat(m_last) - dt.date.fromisoformat(latest_fpd)).days > 10:
        notes.append(f"the no-payment loan lists stop at {md(latest_fpd)}, so defaults since then aren't counted yet")
    elif latest_fpd:
        notes.append(f"no-payment loan lists on file through {md(latest_fpd)}")
    if notes or missing_notes:
        L.append("")
        for n in notes:
            L.append(f"Note: {n}.")
        for n in missing_notes:
            L.append(f"Not available yet — {n}")
    fname = f"{month}{'-TEST' if test else ''}"
    L.append("")
    L.append(f"Full report: Valley Pawn OS › loan-layaway-outcomes › {fname}.html")
    mrkdwn = "\n".join(L)
    std = mrkdwn.replace('*', '**')

    # ---------- HTML ----------
    def table(head, rows, total=None):
        h = '<table><thead><tr>' + ''.join(f'<th>{html.escape(c)}</th>' for c in head) + '</tr></thead><tbody>'
        for r in rows:
            h += '<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>'
        if total:
            h += '<tr class="tot">' + ''.join(f'<td>{c}</td>' for c in total) + '</tr>'
        return '<div class="wrap">' + h + '</tbody></table></div>'
    def frow(lab, v, extra=None):
        n = v[F][0] + v[C][0] + v[O][0]
        r = [lab, N(n), D(v[F][1] + v[C][1] + v[O][1]), f"{N(v[F][0])} ({D(v[F][1])})", f"{N(v[C][0])} ({D(v[C][1])})",
             f"{N(v[O][0])} ({D(v[O][1])})", f"<b>{res_rate(v)}</b>"]
        return r + ([extra] if extra is not None else [])
    s1_store = [frow(NAME[s], fp['by_store'][s], N(fp['forfeited_in_month_by_store'].get(s, 0))) for s in S if s in fp['by_store']]
    s1_tot = frow('<b>All 5 stores</b>', tot, N(fp['forfeited_in_month']))
    s1_band = [frow(BANDLAB[b], fp['by_band'][b]) for b in FP.BANDS if b in fp['by_band']]
    b_store = []
    for s in S:
        a, e = lb(s, month)
        b_store.append([NAME[s], N(a[0] + e[0]), D(a[1] + e[1]), N(a[0]), D(a[1]), f"<b>{PC(a[0], a[0] + e[0])}</b>"] if s in exp_dates
                       else [NAME[s], 'not in yet', '', '', '', ''])
    b_tot = ['<b>All 5 stores</b>', N(mn[0] + me[0]), D(mn[1] + me[1]), N(mn[0]), D(mn[1]), f"<b>{PC(mn[0], mn[0] + me[0])}</b>"]
    b_band = []
    for b in FP.BANDS:
        a, e = lb('band:' + b, month)
        b_band.append([BANDLAB[b], N(a[0] + e[0]), D(a[1] + e[1]), N(a[0]), D(a[1]), f"<b>{PC(a[0], a[0] + e[0])}</b>"])
    b_trend = []
    for m in fp['lensB_months']:
        a, e = lb('all', m)
        lab = mon3(m) + ('' if m != month or exp_full else f' (through {md(exp_through)})')
        b_trend.append([lab, N(a[0] + e[0]), N(a[0]), f"<b>{PC(a[0], a[0] + e[0])}</b>", D(a[1])])
    l_store = []
    for s in S:
        c = lay([s], month)
        l_store.append([NAME[s], N(c['new_n']), N(c['cancel_n']), D(c['cancel_val']), D(c['cancel_dep']), N(c['expire_n']),
                        D(c['expire_dep']), f"<b>{D(c['kept'])}</b>"] if c['have'] else [NAME[s], 'not in yet', '', '', '', '', '', ''])
    l_tot = ['<b>All 5 stores</b>', N(LM['new_n']), N(LM['cancel_n']), D(LM['cancel_val']), D(LM['cancel_dep']), N(LM['expire_n']),
             D(LM['expire_dep']), f"<b>{D(LM['kept'])}</b>"]
    l_trend = []
    for m in lw['months']:
        c = lay(S, m)
        lab = mon3(m) + ('' if c['have'] == 5 else f" ({c['have']} of 5 stores)")
        if m == month and not lay_full and lay_through:
            lab += f" (through {md(lay_through)})"
        l_trend.append([lab, N(c['new_n']), N(c['cancel_n']), PC(c['cancel_n'], c['new_n']), D(c['cancel_dep']), N(c['expire_n']),
                        D(c['expire_dep']), D(c['kept'])])
    l_grid = []
    for s in S:
        l_grid.append([NAME[s]] + [(f"{N(R[f'{s}|{m}']['cancel_n'])} / {N(R[f'{s}|{m}']['expire_n'])}" if f'{s}|{m}' in R else '–') for m in lw['months'][-6:]])
    flagged = [k for k, v in R.items() if v['flagged']]
    caps = fp['fpd_captures']
    css = """
:root{--bg:#fbfbfd;--fg:#1d1d24;--mut:#5d5d6b;--card:#fff;--line:#e3e3ea;--acc:#2D1A5E;--hl:#f3f0fa;--tot:#f4f4f8;--warn:#8a4b00}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#141419;--fg:#ececf1;--mut:#a3a3b2;--card:#1d1d25;--line:#33333f;--acc:#b9a7ee;--hl:#231d36;--tot:#23232d;--warn:#f0b35c}}
:root[data-theme="dark"]{--bg:#141419;--fg:#ececf1;--mut:#a3a3b2;--card:#1d1d25;--line:#33333f;--acc:#b9a7ee;--hl:#231d36;--tot:#23232d;--warn:#f0b35c}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
main{max-width:1060px;margin:0 auto;padding:28px 16px 60px}h1{font-size:26px;margin:0 0 4px;color:var(--acc)}
h2{font-size:20px;margin:40px 0 8px;color:var(--acc);border-bottom:2px solid var(--line);padding-bottom:6px}h3{font-size:16px;margin:22px 0 6px}
.sub{color:var(--mut);margin:0 0 18px}.hl{background:var(--hl);border-left:4px solid var(--acc);border-radius:8px;padding:14px 16px;margin:12px 0}
.warn{color:var(--warn)}.wrap{overflow-x:auto;margin:8px 0 4px}table{border-collapse:collapse;width:100%;font-size:13.5px;background:var(--card)}
th,td{padding:6px 9px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}th:first-child,td:first-child{text-align:left}
th{font-weight:600;color:var(--mut);font-size:12.5px}tr.tot td{background:var(--tot);font-weight:600}.note{color:var(--mut);font-size:13.5px}
ul{padding-left:20px}li{margin:4px 0}
"""
    status = ('<p class="hl">All five stores are in for every section.</p>' if complete else
              '<div class="hl warn"><b>Not everything is in yet:</b><ul>' +
              ''.join(f'<li>{html.escape(n)}</li>' for n in (missing_notes + ([f"Layaway numbers run through {md(lay_through)}; the month is not closed."] if lay_through and not lay_full else [])
                                                               + ([f"The expired-loan list runs through {md(exp_through)}."] if exp_through and not exp_full else []))) + '</ul></div>')
    headline = '<br>'.join(html.escape(x.replace('*', '')) for x in L[2:6] if x)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Loan &amp; Layaway Outcomes</title><style>{css}</style></head><body><main>
<h1>{html.escape(prefix)}Loan &amp; Layaway Outcomes — {mon(month)}</h1>
<p class="sub">Valley Pawn · all 5 stores · built {dt.datetime.now().strftime('%-m/%-d/%Y %-I:%M %p')} from Bravo report exports already on file (nothing new was pulled from Bravo).</p>
{status}
<div class="hl">{headline}</div>

<h2>1 · Loans that never got a payment</h2>
<p>A <b>first-payment default</b> is a loan that showed up on Bravo's "Claude First Payment Default" list — on loan, past its pull date (due date + 16 days), and <b>no payment ever made</b>. Each one is followed to the latest expired-loan list: <b>Forfeited</b> = Bravo expired it; <b>Cured</b> = it dropped off a later list without expiring (a payment, redemption or renewal — the data can't say which); <b>Still open</b> = still on the store's last list and not expired. The loss rate is over resolved loans only. Every such loan on file is included, not just this month's.</p>
<h3>By store</h3>{table(['', 'Loans', 'Loan $', 'Forfeited', 'Cured', 'Still open', 'Lost (of resolved)', f'Forfeited in {mon3(month)}'], s1_store, s1_tot)}
<h3>By loan size</h3>{table(['Loan size', 'Loans', 'Loan $', 'Forfeited', 'Cured', 'Still open', 'Lost (of resolved)'], s1_band)}
<p class="note">Still-open loans confirmed still on loan and unpaid on Bravo's {md(fp['l75_date']) if fp['l75_date'] else ''} past-due list: {N(fp['confirmed_open'][0])} ({D(fp['confirmed_open'][1])}). Median days from pawn to expiry for the forfeited ones: {fp['days_to_expire_median']}.</p>
<h3>Loans that expired in {exp_label}: how many never had a single payment</h3>
<p>"Never paid once" = the due date never moved past pawn date + 30 days (no paid extension, ever).</p>
{table(['', 'Loans expired', 'Principal', 'Never paid once', 'Principal', 'Share never paid'], b_store, b_tot)}
{table(['Loan size', 'Loans expired', 'Principal', 'Never paid once', 'Principal', 'Share never paid'], b_band)}
<h3>Trend — share of expired loans that were never paid once, by month of expiry</h3>
{table(['Month', 'Loans expired', 'Never paid once', 'Share', 'Principal never paid'], b_trend)}

<h2>2 · Cancelled vs expired layaways</h2>
<p>From each store's Bravo End of Month report. <b>Value</b> = full layaway price (what was still owed plus what was paid in). <b>Paid in</b> = deposits and payments made before the layaway ended. Expired-layaway money goes back to the customer as layaway store credit, so it is not kept. <b>Kept by us</b> = restocking fees plus any layaway store credit that itself expired.</p>
<h3>{lay_label} by store{'' if lay_full else ' (month not closed yet)'}</h3>
{table(['', 'Opened', 'Cancelled', 'Value cancelled', 'Paid in (cancelled)', 'Expired', 'Paid in (expired)', 'Kept by us'], l_store, l_tot)}
<h3>Trend — all 5 stores, month by month</h3>
{table(['Month', 'Opened', 'Cancelled', 'Cancel rate', 'Paid in (cancelled)', 'Expired', 'Paid in (expired)', 'Kept by us'], l_trend)}
<h3>Last 6 months by store (cancelled / expired)</h3>
{table(['Store'] + [mon3(m) for m in lw['months'][-6:]], l_grid)}

<h2>Data used &amp; limits</h2>
<ul>
<li><b>No-payment loan lists</b> on file: {'; '.join(f"{NAME[s]} {', '.join(md(d) for d in caps[s])}" for s in S if s in caps)}. Loans on lists after the newest date aren't counted yet.</li>
<li><b>Expired-loan list</b> (Bravo "Claude Forfeiture Winback", all expirations since late 2024): {', '.join(f"{NAME[s]} {md(d)}" for s, d in exp_dates.items())}.</li>
<li><b>Layaways</b>: End of Month reports, {mon3(lw['months'][0])} – {mon3(month)}; a month is only used when the report's own dates cover exactly that month{' (the current month uses a month-to-date report, labelled)' if not lay_full and lay_through else ''}. Months where Bravo's own layaway block didn't tie to the dollar (cancellation lines still read straight from the report): {', '.join(f"{NAME[k[:3]]} {mon3(k[4:])}" for k in flagged) or 'none'}.</li>
<li>Nothing was pulled from Bravo for this report and nobody was messaged besides Joshua.</li>
</ul>
</main></body></html>"""

    data = dict(month=month, test=test, mtd=mtd, complete=complete, usable=usable, missing_notes=missing_notes,
                expired_through=exp_through, layaway_through=lay_through, latest_fpd_list=latest_fpd,
                fpd=dict(total=tot, forfeited_in_month=fp['forfeited_in_month'], by_store=fp['by_store'], by_band=fp['by_band'],
                         expired_in_month=dict(never=mn, extended=me), prior12=dict(never=pn, extended=pe)),
                layaway_month={s: R.get(f'{s}|{month}') for s in S}, layaway_avg_prior=dict(cancel=avg_cancel, expire=avg_expire))
    os.makedirs(OUTDIR, exist_ok=True)
    base = os.path.join(OUTDIR, fname)
    open(base + '.html', 'w').write(page)
    open(base + '.mrkdwn.txt', 'w').write(mrkdwn + "\n")
    open(base + '.slack.txt', 'w').write(std + "\n")
    json.dump(data, open(base + '.json', 'w'), indent=1, default=str)
    return base, data


def send(base, test):
    sent = base + '.sent'
    if os.path.exists(sent):
        return 'ALREADY_SENT'
    ob = os.path.join(OS_DIR, 'fleet', 'outbox')
    stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    env = os.path.join(ob, f"loan-layaway-outcomes{'-test' if test else ''}-joshua-{stamp}.json")
    json.dump({"channel": JOSHUA, "file": host_path(base + '.mrkdwn.txt')}, open(env, 'w'))
    open(sent, 'w').write(f"{dt.datetime.now().isoformat(timespec='seconds')} {JOSHUA} {os.path.basename(env)} via outbox\n")
    return os.path.basename(env)


if __name__ == '__main__':
    a = sys.argv[1:]
    month = a[a.index('--month') + 1] if '--month' in a else prior_month()
    test, mtd = '--test' in a, '--mtd' in a
    base, d = build(month, mtd=mtd, test=test)
    extra = ''
    if '--send' in a:
        extra = ' SENT=' + send(base, test) if d['usable'] else ' SENT=none(nothing-usable)'
    line = f"MONTH={month} COMPLETE={d['complete']} USABLE={d['usable']} MISSING={len(d['missing_notes'])} FILE={base}.mrkdwn.txt{extra}"
    with open(os.path.join(OUTDIR, 'RUN_LOG.md'), 'a') as f:
        if os.path.getsize(os.path.join(OUTDIR, 'RUN_LOG.md')) == 0:
            f.write("# Loan & Layaway Outcomes — run log\n\nOne line per run. Technical detail lives here, never in Slack.\n\n")
        f.write(f"- {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} | {line.replace(OS_DIR, '<OS>')} | test={test} mtd={mtd}\n")
    print(line)
