import sqlite3, os, datetime, json

db = os.path.expanduser('~/Documents/Claude/Projects/Unified Search/index.db')
con = sqlite3.connect(db)
out = []
def p(*a): out.append(' '.join(str(x) for x in a))

p('DB size MB:', round(os.path.getsize(db)/1e6, 1))
p('DB mtime  :', datetime.datetime.fromtimestamp(os.path.getmtime(db)).isoformat())

try:
    for k, v in con.execute("SELECT k, v FROM meta").fetchall():
        vv = v
        try:
            iv = int(v)
            if iv > 1_000_000_000:
                vv = '%s  (%s)' % (v, datetime.datetime.fromtimestamp(iv).isoformat())
        except Exception: pass
        p('meta:', k, '=', vv)
except Exception as e:
    p('meta error', e)

p('')
p('=== MAIL BY ACCOUNT ===')
rows = con.execute("SELECT account, COUNT(*), MIN(ts), MAX(ts) FROM mail GROUP BY account ORDER BY 2 DESC").fetchall()
tot = 0
for acct, n, mn, mx in rows:
    tot += n
    f = lambda t: datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d') if t else '?'
    p('%-46s %7d   %s -> %s' % ((acct or '(none)')[:46], n, f(mn), f(mx)))
p('TOTAL MAIL ROWS:', tot)

p('')
p('=== MAIL BY MAILBOX (top 30) ===')
for mb, n in con.execute("SELECT mailbox, COUNT(*) FROM mail GROUP BY mailbox ORDER BY 2 DESC LIMIT 30").fetchall():
    p('%-56s %7d' % ((mb or '(none)')[:56], n))

p('')
p('=== MESSAGES PER YEAR ===')
for y in range(2016, 2027):
    a = int(datetime.datetime(y,1,1).timestamp()); b = int(datetime.datetime(y+1,1,1).timestamp())
    n = con.execute("SELECT COUNT(*) FROM mail WHERE ts>=? AND ts<?", (a,b)).fetchone()[0]
    p(y, n)

p('')
p('=== OTHER CORPORA ===')
for t in ('files','msgs','notes','reminders','gdrive','photos'):
    try:
        n = con.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0]
        p('%-12s %7d' % (t, n))
    except Exception as e:
        p('%-12s ERROR %s' % (t, e))

open(os.path.expanduser('~/Documents/Claude/Projects/Taxes 2026/_coverage_out.txt'),'w').write('\n'.join(out))
print('done')
