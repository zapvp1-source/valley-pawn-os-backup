#!/usr/bin/env python3
"""bravo_user_audit.py — monthly Bravo-users vs Gusto-roster check (Type B: never touches Bravo).

Built 2026-09-30 (Joshua: "make sure bravo is clean of all old employees and that should be a part
of our offboarding process"). Additive; reads files only.

Inputs
  hr/ROSTER.json            Gusto ACTIVE roster (regenerated daily from Gusto)
  hr/BRAVO_USERS.json       Bravo user ledger, as last seen ON SCREEN (offboarding Step 4 + sweeps)
  hr/GUSTO_DISMISSED.json   optional: [{"name":..., "last_day":"YYYY-MM-DD"}] written by the task
                            from the Gusto connector just before this runs
  Bravo Data Extraction/output/*_employee-activity.csv   latest per store (already pulled)

Findings
  A. FORMER EMPLOYEE STILL ACTIVE: ledger status CURRENT, not a service account / held account,
     and not on the Gusto active roster.
  B. NEW TRANSACTIONS UNDER A FORMER EMPLOYEE'S NAME: in the latest employee-activity report,
     someone not on the active roster has New Loans / New Buys / New Layaways > 0 and (when the
     dismissed list gives a date) their last day is before the report period started.
     Layaway payments / sales credited to the original salesperson are NOT counted (Bravo keeps
     crediting them after someone leaves).
  C. LIST OUT OF DATE: last on-screen sweep older than 35 days.
  Info only (file, not DM): active roster store staff not found in the ledger.

Usage: bravo_user_audit.py [--month YYYY-MM] [--send]
  --send  writes ONE outbox envelope to Joshua's DM (Goldilocks bot) only when A, B or C is
          non-empty, once per month (marker file). Plain business language, no system names.
Prints: MONTH=.. FORMER_ACTIVE=n NEW_TXN_FLAGS=n STALE=bool FILE=.. [SENT=..|ALREADY_SENT|SENT=none(clean)]
"""
import csv, datetime as dt, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OS_DIR = os.path.dirname(HERE)
PROJ = os.path.dirname(OS_DIR)
HR = os.path.join(OS_DIR, 'hr')
OUT = os.path.join(HR, 'bravo_user_audit')
BDE_OUT = os.path.join(PROJ, 'Bravo Data Extraction', 'output')
HOST_PROJECTS = '/Users/joshuadavis/Documents/Claude/Projects'
JOSHUA = 'U03BB52MDSA'
STORES = ['CUL', 'HAR', 'LEX', 'ROA', 'WAY']
STORE_NAME = {'CUL': 'Culpeper', 'HAR': 'Harrisonburg', 'LEX': 'Lexington', 'ROA': 'Roanoke', 'WAY': 'Waynesboro'}
STALE_DAYS = 35


def host_path(p):
    i = p.find('/mnt/Projects/')
    return HOST_PROJECTS + p[i + len('/mnt/Projects'):] if p.startswith('/sessions/') and i >= 0 else p


def norm(s):
    return re.sub(r'[^a-z ]', '', (s or '').lower()).strip()


def load(p, default=None):
    try:
        return json.load(open(p))
    except Exception:
        return default


def money(v):
    v = (v or '').replace('$', '').replace(',', '').strip()
    neg = v.startswith('(') and v.endswith(')')
    v = v.strip('()')
    try:
        x = float(v)
    except ValueError:
        return 0.0
    return -x if neg else x


def prior_month():
    t = dt.date.today().replace(day=1) - dt.timedelta(days=1)
    return t.strftime('%Y-%m')


def main():
    a = sys.argv[1:]
    month = a[a.index('--month') + 1] if '--month' in a else prior_month()
    send = '--send' in a
    os.makedirs(OUT, exist_ok=True)

    roster = load(os.path.join(HR, 'ROSTER.json'), {}) or {}
    ledger = load(os.path.join(HR, 'BRAVO_USERS.json'), {}) or {}
    dismissed = load(os.path.join(HR, 'GUSTO_DISMISSED.json'), []) or []
    aliases = {norm(k): norm(v) for k, v in (ledger.get('aliases') or {}).items()}

    active = set()
    for e in roster.get('employees', []):
        n = norm(e.get('name'))
        active.add(n)
        if e.get('preferred'):
            parts = n.split()
            active.add(norm(e['preferred'] + ' ' + parts[-1]) if parts else norm(e['preferred']))

    def is_active(name):
        n = norm(name)
        n = aliases.get(n, n)
        return n in active

    if isinstance(dismissed, dict):
        dismissed = dismissed.get('employees', [])
    last_day = {}

    def lkey(n):  # last name + first initial, so "Steve Burch" (Bravo) matches "Steven Burch" (Gusto)
        p = norm(n).split()
        return (p[-1] + ':' + p[0][:1]) if p else ''
    for d in dismissed:
        if d.get('name') and d.get('last_day'):
            last_day[lkey(aliases.get(norm(d['name']), norm(d['name'])))] = d['last_day']

    service = {norm(x) for x in ledger.get('service_accounts', [])}
    held = {norm(h.get('name')) for h in ledger.get('hold_for_joshua', [])}

    # A. former employee still CURRENT in the ledger
    former_active = []
    for u in ledger.get('users', []):
        n = norm(u.get('name'))
        if u.get('status') != 'CURRENT' or n in service or n in held:
            continue
        if not is_active(u.get('name')):
            former_active.append(u)

    # info: active store staff not in the ledger
    ledger_names = {aliases.get(norm(u.get('name')), norm(u.get('name'))) for u in ledger.get('users', [])}
    not_in_ledger = [e['name'] for e in roster.get('employees', [])
                     if e.get('department') in STORE_NAME.values() and norm(e['name']) not in ledger_names]

    # B. employee-activity: originating transactions under a non-roster name
    flags, periods, unverified = [], {}, []
    for s in STORES:
        files = sorted(glob.glob(os.path.join(BDE_OUT, f'*_{s}_employee-activity.csv')), key=os.path.getmtime)
        if not files:
            periods[s] = 'no file'
            continue
        f = files[-1]
        rows = list(csv.reader(open(f, encoding='utf-8-sig', errors='replace')))
        per = ''
        for r in rows[:4]:
            for c in r:
                if re.search(r'\d+/\d+/\d{4}\s*-\s*\d+/\d+/\d{4}', c):
                    per = c.strip()
        periods[s] = f'{per} ({os.path.basename(f)})'
        start = None
        m = re.match(r'(\d+)/(\d+)/(\d{4})', per)
        if m:
            start = dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        hdr = next((r for r in rows if r and r[0] == 'Employee'), None)
        if not hdr:
            continue
        ix = {h: i for i, h in enumerate(hdr)}
        for r in rows:
            if not r or ' - ' not in r[0] or r[0].startswith('Total'):
                continue
            login, name = [x.strip() for x in r[0].split(' - ', 1)]
            if norm(name) in service or norm(name) in held or is_active(name):
                continue
            orig = sum(money(r[ix[c]]) for c in ('New Loans', 'New Buys + Bought Loans', 'New Layaways') if c in ix and ix[c] < len(r))
            if orig <= 0:
                continue
            ld = last_day.get(lkey(aliases.get(norm(name), norm(name))))
            if ld and start and dt.date.fromisoformat(ld) >= start:
                continue  # their own last days fall inside the period — expected
            if not ld:
                unverified.append({'store': s, 'login': login, 'name': name, 'new_txn_dollars': round(orig, 2), 'period': per})
                continue  # no Gusto record to date it — file only, not the DM
            flags.append({'store': s, 'login': login, 'name': name, 'new_txn_dollars': round(orig, 2),
                          'last_day': ld or 'unknown', 'period': per})

    last = ledger.get('last_onscreen_sweep')
    age = (dt.date.today() - dt.date.fromisoformat(last)).days if last else 999
    stale = age > STALE_DAYS

    # message (plain business language — Rule 16)
    lines = [f'*Bravo logins check — {dt.date(int(month[:4]), int(month[5:]), 1):%B %Y}*']
    if former_active:
        lines.append('Former employees who can still log in to Bravo:')
        for u in former_active:
            lines.append(f"• {u['name']} — {STORE_NAME.get(u['store'], u['store'])}")
    if flags:
        lines.append('New loans or buys were written under the name of someone no longer on payroll:')
        for f in flags:
            lines.append(f"• {f['name']} — {STORE_NAME.get(f['store'], f['store'])}, ${f['new_txn_dollars']:,.0f} ({f['period']})")
    if stale:
        lines.append(f'The Bravo login list was last checked on screen {last}; it needs a fresh look at the Bravo screen.')
    clean = not (former_active or flags or stale)
    if clean:
        lines.append('All clear — no former employees can log in to Bravo.')
    msg = '\n'.join(lines) + '\n'

    base = os.path.join(OUT, month)
    report = {'month': month, 'generated': dt.datetime.now().isoformat(timespec='seconds'),
              'former_active': former_active, 'new_txn_flags': flags, 'new_txn_undated': unverified, 'stale': stale,
              'last_onscreen_sweep': last, 'sweep_age_days': age, 'activity_periods': periods,
              'active_store_staff_not_in_ledger': not_in_ledger, 'dismissed_file_used': bool(dismissed),
              'held_for_joshua': ledger.get('hold_for_joshua', [])}
    json.dump(report, open(base + '.json', 'w'), indent=1)
    open(base + '.mrkdwn.txt', 'w').write(msg)
    with open(os.path.join(OUT, 'RUN_LOG.md'), 'a') as lg:
        lg.write(f"- {report['generated']} month={month} former_active={len(former_active)} "
                 f"new_txn_flags={len(flags)} stale={stale} not_in_ledger={len(not_in_ledger)}\n")

    extra = ''
    if send:
        sent = base + '.sent'
        if clean:
            extra = ' SENT=none(clean)'
        elif os.path.exists(sent):
            extra = ' ALREADY_SENT'
        else:
            ob = os.path.join(OS_DIR, 'fleet', 'outbox')
            env = os.path.join(ob, f"bravo-user-audit-joshua-{dt.datetime.now():%Y%m%d-%H%M%S}.json")
            json.dump({'channel': JOSHUA, 'file': host_path(base + '.mrkdwn.txt')}, open(env, 'w'))
            open(sent, 'w').write(f"{dt.datetime.now().isoformat(timespec='seconds')} {JOSHUA} {os.path.basename(env)} via outbox\n")
            extra = ' SENT=' + os.path.basename(env)
    print(f'MONTH={month} FORMER_ACTIVE={len(former_active)} NEW_TXN_FLAGS={len(flags)} STALE={stale} FILE={base}.mrkdwn.txt{extra}')


if __name__ == '__main__':
    main()
