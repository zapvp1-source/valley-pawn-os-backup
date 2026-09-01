import sqlite3, os, datetime, subprocess, plistlib, json

out = []
def p(*a): out.append(' '.join(str(x) for x in a))

# Map Apple Mail account UUIDs -> email addresses
try:
    r = subprocess.run(['defaults','read','com.apple.mail','MailAccounts'], capture_output=True, text=True)
    p('--- com.apple.mail MailAccounts (raw, truncated) ---')
    p(r.stdout[:6000])
except Exception as e:
    p('defaults error', e)

db = os.path.expanduser('~/Documents/Claude/Projects/Unified Search/index.db')
con = sqlite3.connect(db)
p('')
p('--- per-account TRUE date range (excluding null/zero ts) + sample senders ---')
for (acct,) in con.execute("SELECT DISTINCT account FROM mail").fetchall():
    row = con.execute("SELECT COUNT(*), MIN(ts), MAX(ts) FROM mail WHERE account=? AND ts>0", (acct,)).fetchone()
    n, mn, mx = row
    nulls = con.execute("SELECT COUNT(*) FROM mail WHERE account=? AND (ts IS NULL OR ts<=0)", (acct,)).fetchone()[0]
    f = lambda t: datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d') if t else '?'
    # sample a recipient to identify the account
    rec = con.execute("SELECT recipients FROM mail WHERE account=? AND recipients IS NOT NULL AND recipients!='' LIMIT 40", (acct,)).fetchall()
    import re
    from collections import Counter
    c = Counter()
    for (rr,) in rec:
        for m in re.findall(r'[\w\.\-\+]+@[\w\.\-]+', rr or ''):
            c[m.lower()] += 1
    p('%s  n=%6d nulls=%5d  %s -> %s  top-recipients=%s' % (acct, n, nulls, f(mn), f(mx), [x for x,_ in c.most_common(3)]))

open(os.path.expanduser('~/Documents/Claude/Projects/Taxes 2026/_acctmap_out.txt'),'w').write('\n'.join(out))
print('done')
