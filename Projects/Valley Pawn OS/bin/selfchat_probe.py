#!/usr/bin/env python3
"""selfchat_probe.py (2026-11-20) read-only: shows the last messages in Joshua's self-chat (+18049304221) in chat.db
so joshua_text_alert can tell its own alert texts from Joshua's replies. Prints rows; changes nothing."""
import os, sqlite3, datetime
DB = os.path.expanduser('~/Library/Messages/chat.db')
con = sqlite3.connect('file:%s?mode=ro' % DB, uri=True)
rows = con.execute("""SELECT m.ROWID, m.guid, m.is_from_me, m.service, m.date, h.id, c.chat_identifier, c.ROWID,
  m.thread_originator_guid, m.associated_message_type, m.text, m.attributedBody
  FROM message m LEFT JOIN handle h ON m.handle_id=h.ROWID
  LEFT JOIN chat_message_join cmj ON cmj.message_id=m.ROWID LEFT JOIN chat c ON c.ROWID=cmj.chat_id
  WHERE (h.id LIKE '%8049304221%' OR c.chat_identifier LIKE '%8049304221%')
  ORDER BY m.ROWID DESC LIMIT 12""").fetchall()
def body(text, blob):
    if text: return text
    if not blob: return None
    try:
        b = blob.split(b'NSString', 1)[1][5:]
        if b[0] == 0x81:
            n = int.from_bytes(b[1:3], 'little'); return b[3:3+n].decode('utf-8', 'replace')
        n = b[0]; return b[1:1+n].decode('utf-8', 'replace')
    except Exception as e:
        return '<undecoded %s>' % e
for r in rows:
    d = datetime.datetime(2001,1,1) + datetime.timedelta(seconds=(r[4] or 0)/1e9) - datetime.timedelta(hours=5)
    print(r[0], r[2], r[3], d.strftime('%m-%d %H:%M:%S'), r[5], r[6], 'chat', r[7], 'thr', r[8], 'assoc', r[9], '|', (body(r[10], r[11]) or '')[:90].replace(chr(10),' / '))
