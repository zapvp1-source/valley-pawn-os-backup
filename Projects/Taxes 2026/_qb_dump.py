import sqlite3, os, json, re

db = os.path.expanduser('~/Documents/Claude/Projects/Unified Search/index.db')
con = sqlite3.connect(db)
out = os.path.expanduser('~/Documents/Claude/Projects/Taxes 2026/_qb')
os.makedirs(out, exist_ok=True)

rows = con.execute(
  "SELECT subject, sender, ts, path, body FROM mail WHERE mail MATCH ? ORDER BY ts",
  ('sender:intuit OR sender:quickbooks OR sender:joistapp OR sender:payzer OR sender:wepay OR sender:"bill.com"',)
).fetchall()

man = []
for i, (subj, sndr, ts, path, body) in enumerate(rows):
    fn = 'qb_%05d.txt' % i
    with open(os.path.join(out, fn), 'w') as f:
        f.write('SUBJECT: %s\nFROM: %s\nTS: %s\nPATH: %s\n\n' % (subj, sndr, ts, path))
        f.write(body or '')
    man.append({'f': fn, 'subject': subj, 'sender': sndr, 'ts': ts})
json.dump(man, open(os.path.join(out, '_manifest.json'), 'w'), indent=1)
print('quickbooks/intuit/joist/payzer emails:', len(rows))
