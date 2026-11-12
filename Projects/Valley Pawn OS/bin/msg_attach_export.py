#!/usr/bin/env python3
"""Copy iMessage/SMS attachments from one sender into the Projects folder so Cowork sessions can read them.
Additive, read-only against chat.db and ~/Library/Messages/Attachments (2026-11-11, approved by Joshua).
Runs on the host via the host_queue (vp-runner holds Full Disk Access).
Usage: msg_attach_export.py <phone digits, e.g. 5403839601> [hours back, default 48]
Output: ~/Documents/Claude/Projects/Unified Search/_msg_attach/<digits>/<YYYYMMDD-HHMM>_<filename>
"""
import os, sys, sqlite3, shutil, time
HOME = os.path.expanduser("~")
digits = "".join(ch for ch in (sys.argv[1] if len(sys.argv) > 1 else "") if ch.isdigit())
hours = float(sys.argv[2]) if len(sys.argv) > 2 else 48
if len(digits) < 7:
    print("need a phone number"); sys.exit(2)
out = os.path.join(HOME, "Documents/Claude/Projects/Unified Search/_msg_attach", digits)
os.makedirs(out, exist_ok=True)
db = sqlite3.connect("file:%s?mode=ro" % os.path.join(HOME, "Library/Messages/chat.db"), uri=True)
APPLE_EPOCH = 978307200
since_ns = int((time.time() - hours * 3600 - APPLE_EPOCH) * 1e9)
rows = db.execute("""
  select m.date, a.filename, a.transfer_name, m.is_from_me
  from message m
  join handle h on h.ROWID = m.handle_id
  join message_attachment_join j on j.message_id = m.ROWID
  join attachment a on a.ROWID = j.attachment_id
  where h.id like ? and m.date > ?
  order by m.date""", ("%" + digits[-10:], since_ns)).fetchall()
n = 0
for d, fn, tn, me in rows:
    if not fn:
        continue
    src = os.path.expanduser(fn)
    ts = time.strftime("%Y%m%d-%H%M", time.localtime(d / 1e9 + APPLE_EPOCH))
    name = "%s_%s%s" % (ts, "ME_" if me else "", os.path.basename(tn or src))
    dst = os.path.join(out, name)
    if os.path.exists(src):
        shutil.copy2(src, dst); n += 1; print("copied", name)
    else:
        print("missing on disk (not downloaded?)", src)
print("done: %d file(s) -> %s" % (n, out))
