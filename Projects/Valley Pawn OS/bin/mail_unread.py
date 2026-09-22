#!/usr/bin/env python3
"""mail_unread.py — read Apple Mail's unread state natively. No connector, no AppleScript.

WHY: daily-unopened-email-eval has been the worst task in the fleet (1 of 7 days) because it drove
Mail.app through the Control_your_Mac connector, which is gone from scheduled sessions for good
(probe, 2026-09-21). Apple Mail keeps read-state in its own SQLite Envelope Index, and vp-runner
CAN read it — proven 2026-09-21, contradicting the FDA theory in the CHANGELOG.

Read-only: opens the index with mode=ro and never writes. Mail's own schema is the source of truth.
"""
import datetime as dt, glob, os, sqlite3, sys
HOME = os.path.expanduser("~")
HOURS = int(sys.argv[sys.argv.index("--hours")+1]) if "--hours" in sys.argv else 24
envs = glob.glob(os.path.join(HOME, "Library/Mail/V*/MailData/Envelope Index"))
if not envs:
    print("Envelope Index not found"); raise SystemExit(1)
c = sqlite3.connect("file:%s?mode=ro" % envs[0].replace(" ", "%20"), uri=True)
cols = [r[1] for r in c.execute("PRAGMA table_info(messages)")]
# Apple Mail packs read-state into `flags`; bit 0 = read on V10. Verify against the schema rather
# than assuming: if a plain `read` column exists, prefer it.
has_read = "read" in cols
cutoff = int((dt.datetime.now() - dt.timedelta(hours=HOURS)).timestamp())
where = "read=0" if has_read else "(flags & 1)=0"
# Apple Mail normalises text out of `messages`: subject and sender are INTEGER foreign keys into
# `subjects` and `addresses`. Selecting them raw yields ints, not strings — that is what crashed the
# first run. LEFT JOIN so a missing lookup row degrades to "(no subject)" instead of dropping mail.
q = ("select m.ROWID, s.subject, a.address, m.date_received "
     "from messages m "
     "left join subjects s on s.ROWID = m.subject "
     "left join addresses a on a.ROWID = m.sender "
     "where %s and m.date_received >= ? "
     # One real email appears once per mailbox it lives in (account inbox + All Mail + ...), so a
     # raw count double-reports. Collapse on global_message_id — Apple's own cross-mailbox identity
     # for a message. Without this the 24h figure was 310 when the true number is far lower, and a
     # report Joshua acts on must not inflate his inbox.
     "group by coalesce(m.global_message_id, m.message_id, m.ROWID) "
     "order by m.date_received desc limit 60" % where)
try:
    rows = list(c.execute(q, (cutoff,)))
except Exception as e:
    print("query failed: %s" % e); raise SystemExit(1)
tot = c.execute("select count(distinct coalesce(global_message_id, message_id, ROWID)) from messages where %s and date_received >= ?" % where, (cutoff,)).fetchone()[0]
print("# Unopened mail — last %dh (native read of Apple Mail's Envelope Index)\n" % HOURS)
print("read-state column: %s\n" % ("read" if has_read else "flags bit 0"))
print("**%d unopened in the window.**\n" % tot)
for rid, subj, frm, ts in rows[:25]:
    when = dt.datetime.fromtimestamp(ts).strftime("%m/%d %H:%M") if ts else "?"
    subj = subj if isinstance(subj, str) else "(no subject)"
    frm = frm if isinstance(frm, str) else "(unknown sender)"
    print("- %s  %-34s %s" % (when, frm[:34], subj[:80]))
