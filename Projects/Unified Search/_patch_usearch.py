import re

with open('usearch.py') as f:
    src = f.read()

# 1) add photos FTS5 table creation, right after the meta table line, before "return c"
anchor = '    c.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")\n    return c'
assert anchor in src, 'init_db anchor not found'
photos_table = (
    '    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS photos USING fts5(\n'
    '        name, ocr_text,\n'
    '        uuid UNINDEXED, date UNINDEXED, album UNINDEXED, kind UNINDEXED,\n'
    '        tokenize="porter unicode61")""")\n'
)
src = src.replace(anchor, photos_table + anchor, 1)

# 2) add --photos CLI flag after --drive flag
old = "    p.add_argument(\"--drive\", action=\"store_true\", dest=\"gdrive\")\n"
assert old in src, 'drive flag anchor not found'
new = old + "    p.add_argument(\"--photos\", action=\"store_true\")\n    p.add_argument(\"--pics\", action=\"store_true\", dest=\"photos\")\n"
src = src.replace(old, new, 1)

# 3) include photos in any_flag / want_photos
old2 = "    any_flag = a.mail or a.files or a.msgs or a.notes or a.reminders or a.gdrive\n"
assert old2 in src
new2 = ("    any_flag = a.mail or a.files or a.msgs or a.notes or a.reminders or a.gdrive or a.photos\n")
src = src.replace(old2, new2, 1)

old3 = "    want_gdrive = a.gdrive or not any_flag\n"
assert old3 in src
new3 = old3 + "    want_photos = a.photos or not any_flag\n"
src = src.replace(old3, new3, 1)

# 4) add the photos query block right after the gdrive query block (before "res.sort")
anchor2 = "    res.sort(key=lambda r: r[7])\n"
assert anchor2 in src, 'res.sort anchor not found'
photos_query = (
    '    if want_photos:\n'
    '        sql = ("SELECT \'photo\',name,album,uuid,date,kind,"\n'
    '               "snippet(photos,1,\'>>\',\'<<\',\' ... \',18),bm25(photos) FROM photos WHERE photos MATCH ?")\n'
    '        prm = [term]\n'
    '        if a.since:\n'
    '            sql += " AND date>=?"; prm.append(epoch(a.since))\n'
    '        if a.until:\n'
    '            sql += " AND date<=?"; prm.append(epoch(a.until))\n'
    '        sql += " ORDER BY bm25(photos) LIMIT ?"\n'
    '        prm.append(a.n)\n'
    '        try:\n'
    '            res += list(c.execute(sql, prm))\n'
    '        except sqlite3.OperationalError as e:\n'
    '            print("photos:", e)\n'
)
src = src.replace(anchor2, photos_query + anchor2, 1)

# 5) add photos row count to stats printout, right after gdrive rows line
old4 = '    print("gdrive rows   :", c.execute("SELECT count(*) FROM gdrive").fetchone()[0])\n'
assert old4 in src
new4 = old4 + '    print("photos rows   :", c.execute("SELECT count(*) FROM photos").fetchone()[0])\n'
src = src.replace(old4, new4, 1)

with open('usearch.py', 'w') as f:
    f.write(src)

print("PATCH OK")
