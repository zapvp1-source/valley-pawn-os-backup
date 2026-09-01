import sqlite3, os, json

db = os.path.expanduser('~/Documents/Claude/Projects/Unified Search/index.db')
con = sqlite3.connect(db)
outdir = os.path.expanduser('~/Documents/Claude/Projects/Taxes 2026/_lodestar')
os.makedirs(outdir, exist_ok=True)

# FTS5 MATCH is instant. Grab every email from lodestar.tax people.
q = "SELECT subject, sender, ts, path, body FROM mail WHERE mail MATCH ? ORDER BY ts"
rows = con.execute(q, ('sender:lodestar',)).fetchall()

manifest = []
for i, (subject, sender, ts, path, body) in enumerate(rows):
    fn = os.path.join(outdir, 'ldr_%04d.txt' % i)
    with open(fn, 'w') as f:
        f.write('SUBJECT: %s\nSENDER: %s\nTS: %s\nPATH: %s\n\n' % (subject, sender, ts, path))
        f.write(body or '')
    manifest.append({'i': i, 'subject': subject, 'sender': sender, 'ts': ts, 'len': len(body or '')})

with open(os.path.join(outdir, '_manifest.json'), 'w') as f:
    json.dump(manifest, f, indent=1)

print('rows', len(rows))
