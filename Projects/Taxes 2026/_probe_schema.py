import sqlite3, os
db = os.path.expanduser('~/Documents/Claude/Projects/Unified Search/index.db')
con = sqlite3.connect(db)
rows = con.execute("SELECT type, name, sql FROM sqlite_master WHERE name NOT LIKE '%_data' AND name NOT LIKE '%_idx' AND name NOT LIKE '%_docsize' AND name NOT LIKE '%_content'").fetchall()
out = []
for t, n, s in rows:
    out.append('%s | %s\n%s\n' % (t, n, (s or '')[:600]))
open(os.path.expanduser('~/Documents/Claude/Projects/Taxes 2026/_probe_out.txt'), 'w').write('\n'.join(out))
print('ok')
