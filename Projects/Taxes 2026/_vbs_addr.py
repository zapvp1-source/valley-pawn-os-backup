import sqlite3, os, re, datetime
from collections import Counter, defaultdict

db = os.path.expanduser('~/Documents/Claude/Projects/Unified Search/index.db')
con = sqlite3.connect(db)
out = []
def p(*a): out.append(' '.join(str(x) for x in a))

rows = con.execute(
  "SELECT subject, sender, recipients, ts, mailbox FROM mail WHERE mail MATCH ? ORDER BY ts",
  ('"valleybuildingsupply" OR "Valley Building Supply"',)).fetchall()
p('matching messages:', len(rows))

addr = Counter()
first_seen = {}
last_seen = {}
inbound = Counter()   # addresses that have EMAILED JOSHUA (proven deliverable/real)
for subj, sndr, rcpt, ts, mb in rows:
    for field, s in (('from', sndr or ''), ('to', rcpt or '')):
        for m in re.findall(r'[\w\.\-\+]+@[\w\.\-]+\.\w+', s):
            m = m.lower().strip('.')
            if 'valleybuilding' not in m and 'vbs' not in m: continue
            addr[m] += 1
            if field == 'from': inbound[m] += 1
            if m not in first_seen or ts < first_seen[m]: first_seen[m] = ts
            if m not in last_seen or ts > last_seen[m]: last_seen[m] = ts

f = lambda t: datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d') if t else '?'
p('')
p('=== VALLEY BUILDING SUPPLY ADDRESSES ===')
p('%-46s %6s %8s   %s -> %s' % ('address', 'total', 'INBOUND', 'first', 'last'))
for a, n in addr.most_common():
    p('%-46s %6d %8d   %s -> %s' % (a, n, inbound[a], f(first_seen[a]), f(last_seen[a])))

p('')
p('=== MOST RECENT 12 VBS MESSAGES (who/subject) ===')
for subj, sndr, rcpt, ts, mb in rows[-12:]:
    p('%s | %-40s | %s' % (f(ts), (sndr or '')[:40], (subj or '')[:70]))

open(os.path.expanduser('~/Documents/Claude/Projects/Taxes 2026/_vbs_addr_out.txt'),'w').write('\n'.join(out))
print('done')
