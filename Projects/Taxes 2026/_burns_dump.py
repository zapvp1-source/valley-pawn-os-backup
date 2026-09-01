import sqlite3, os, json

db = os.path.expanduser('~/Documents/Claude/Projects/Unified Search/index.db')
con = sqlite3.connect(db)
out = os.path.expanduser('~/Documents/Claude/Projects/Taxes 2026/_burns')
os.makedirs(out, exist_ok=True)

queries = {
 'burns':      'burns',
 'svcfin':     'svcfin OR "Service Finance"',
 'l3624':      '"3624"',
 'roof':       'roof AND (loan OR finance OR payment OR invoice)',
 'greensky':   'greensky OR "GreenSky" OR synchrony OR foundation OR "home improvement loan" OR aqua OR "Regions" OR "Wells Fargo Retail"',
}
man = []
n = 0
for tag, q in queries.items():
    try:
        rows = con.execute("SELECT subject, sender, recipients, ts, path, body FROM mail WHERE mail MATCH ? ORDER BY ts", (q,)).fetchall()
    except Exception as e:
        man.append({'tag': tag, 'error': str(e)}); continue
    for subj, sndr, rcpt, ts, path, body in rows:
        fn = os.path.join(out, '%s_%05d.txt' % (tag, n))
        with open(fn, 'w') as f:
            f.write('TAG: %s\nSUBJECT: %s\nFROM: %s\nTO: %s\nTS: %s\nPATH: %s\n\n' % (tag, subj, sndr, rcpt, ts, path))
            f.write(body or '')
        man.append({'tag': tag, 'file': os.path.basename(fn), 'subject': subj, 'sender': sndr, 'ts': ts})
        n += 1
json.dump(man, open(os.path.join(out, '_manifest.json'), 'w'), indent=1)
from collections import Counter
print(Counter(m.get('tag') for m in man))
print('total files', n)
