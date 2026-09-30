#!/usr/bin/env python3
"""mail_latest_body.py — read-only: print the plain-text body of the newest Apple Mail message from a
given sender within the last N hours (default 2). Added 2026-09-29 for one-time claim codes
(e.g. MasterFFL "Your authentication code for MyFFL" to a store inbox), at Joshua's direction.
Usage: mail_latest_body.py <sender-substring> [--hours N]
Opens the Envelope Index read-only; reads the matching .emlx file; never writes anything.
"""
import datetime as dt, email, glob, os, re, sqlite3, sys
from email import policy
HOME = os.path.expanduser("~")
sender = sys.argv[1].lower()
HOURS = int(sys.argv[sys.argv.index("--hours") + 1]) if "--hours" in sys.argv else 2
env = glob.glob(os.path.join(HOME, "Library/Mail/V*/MailData/Envelope Index"))[0]
c = sqlite3.connect("file:%s?mode=ro" % env.replace(" ", "%20"), uri=True)
cutoff = int((dt.datetime.now() - dt.timedelta(hours=HOURS)).timestamp())
rows = list(c.execute(
    "select m.ROWID, s.subject, a.address, m.date_received from messages m "
    "left join subjects s on s.ROWID=m.subject left join addresses a on a.ROWID=m.sender "
    "where lower(a.address) like ? and m.date_received >= ? order by m.date_received desc limit 20",
    ("%" + sender + "%", cutoff)))
if not rows:
    print("no message from", sender, "in last", HOURS, "h"); raise SystemExit(1)
base = os.path.dirname(os.path.dirname(env))
for rowid, subj, addr, ts in rows:
    hits = glob.glob(os.path.join(base, "**", "%d.emlx" % rowid), recursive=True) + \
           glob.glob(os.path.join(base, "**", "%d.partial.emlx" % rowid), recursive=True)
    for h in hits[:1]:
        raw = open(h, "rb").read()
        raw = raw[raw.index(b"\n") + 1:]  # emlx: first line is byte count
        msg = email.message_from_bytes(raw, policy=policy.default)
        if "--to" in sys.argv and sys.argv[sys.argv.index("--to") + 1].lower() not in str(msg.get("To", "")).lower():
            break
        print("==", dt.datetime.fromtimestamp(ts).strftime("%m/%d %H:%M"), addr, "|", subj, "| files:", len(hits))
        part = msg.get_body(preferencelist=("plain", "html"))
        txt = part.get_content() if part else ""
        txt = re.sub(r"(?is)<(style|script|head)[^>]*>.*?</\1>", " ", txt)
        txt = re.sub(r"<[^>]+>", " ", txt)
        print("CODE-LIKE:", sorted(set(re.findall(r"\b[A-Z0-9]{6,8}\b", txt)) - {"MASTERFFL"}))
        txt = re.sub(r"\s+", " ", txt)
        print("To:", msg.get("To"))
        print(txt[:1200])
        if "--to" in sys.argv:
            raise SystemExit(0)
    if "--to" not in sys.argv:
        break
