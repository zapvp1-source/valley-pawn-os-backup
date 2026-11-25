#!/usr/bin/env python3
"""icloud_mail_mirror.py — read-only mirror of Joshua's iCloud Mail (Inbox + Sent) for every Claude thread.

WHY (2026-11-24): the cloud "Apple_Mail" connector (Cloud Run, IMAP app-specific password) has returned
AUTHENTICATIONFAILED since 11/12, so threads could not see whether Joshua had already replied and started
cc'ing his iCloud as a workaround. Joshua: "stop copying me on; you have to figure out iCloud, indexed or
otherwise." Apple Mail on the Mac Studio syncs iCloud with the system Apple ID (no app password, no expiry),
and vp-runner can read Mail's Envelope Index (proven 2026-09-21, mail_unread.py). So this agent mirrors that
local store into Life OS/Mail Mirror/, which syncs to Google Drive, so cloud threads read it via the Drive
connector and linked threads read it from disk.

Read-only: opens the Envelope Index with mode=ro and only reads .emlx files. Never touches Mail's data.
Self-healing: if the newest iCloud Inbox message is stale, it launches Mail in the background (open -g) so
it resumes syncing; a persistent stall adds ONE row to Life OS/HUMAN_QUEUE.md (deduped).
"""
import datetime as dt, email, email.policy, glob, hashlib, html, json, os, re, sqlite3, subprocess, sys, time
from urllib.parse import unquote, urlparse

HOME = os.path.expanduser("~")
ROOT = os.path.join(HOME, "Documents/Claude/Projects")
OUT = os.path.join(ROOT, "Life OS/Mail Mirror")
STATE = os.path.join(ROOT, "Valley Pawn OS/fleet/state/icloud-mail-mirror")
HQ = os.path.join(ROOT, "Life OS/HUMAN_QUEUE.md")
os.makedirs(OUT, exist_ok=True); os.makedirs(STATE, exist_ok=True)

ICLOUD_HINTS = ("zapvp1@me.com", "zapvp1@icloud.com", "zapvp1@mac.com", "@luckydavis.com")
INBOX_DAYS, SENT_DAYS, OTHER_SENT_DAYS = 14, 30, 14
INBOX_BODY, SENT_BODY = 1500, 4000
STALE_HOURS = 3
SENT_NAMES = {"sent messages", "sent", "sent items", "sent mail", "[gmail]/sent mail"}
NOW = time.time()


def log(*a):
    print(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), *a, flush=True)


def fmt(ts):
    return dt.datetime.fromtimestamp(ts).astimezone().strftime("%Y-%m-%d %H:%M %Z") if ts else ""


def write_atomic(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def write_if_changed(path, text):
    try:
        if open(path).read() == text:
            return False
    except Exception:
        pass
    write_atomic(path, text)
    return True


envs = sorted(glob.glob(os.path.join(HOME, "Library/Mail/V*/MailData/Envelope Index")))
status = {"run_at": fmt(NOW), "run_epoch": int(NOW), "ok": False}
if not envs:
    status["error"] = "Envelope Index not found (Mail not set up, or no disk access)"
    write_atomic(os.path.join(OUT, "status.json"), json.dumps(status, indent=1))
    log(status["error"]); sys.exit(1)
ENV = envs[-1]
MAILROOT = os.path.dirname(os.path.dirname(ENV))  # ~/Library/Mail/V10
c = sqlite3.connect("file:%s?mode=ro" % ENV.replace(" ", "%20"), uri=True, timeout=30)
mcols = {r[1] for r in c.execute("PRAGMA table_info(messages)")}
rcols = {r[1] for r in c.execute("PRAGMA table_info(recipients)")}
acols = {r[1] for r in c.execute("PRAGMA table_info(addresses)")}
ACOM = "comment" if "comment" in acols else "''"

# ---- mailboxes -> (account uuid, path)
boxes = {}
for rid, url in c.execute("select ROWID, url from mailboxes"):
    if not url:
        continue
    u = urlparse(url)
    boxes[rid] = {"url": url, "acct": u.netloc, "path": unquote(u.path.lstrip("/")), "scheme": u.scheme}


def addr_of(rowid):
    if rowid is None:
        return ""
    r = c.execute("select address, %s from addresses where ROWID=?" % ACOM, (rowid,)).fetchone()
    if not r:
        return ""
    a, n = r
    return ("%s <%s>" % (n, a)) if n else (a or "")


# ---- identify accounts: primary address = most common sender in that account's Sent mailbox
acct_addr, acct_score = {}, {}
for rid, b in boxes.items():
    is_sent = b["path"].lower() in SENT_NAMES
    if is_sent:
        rows = c.execute("select a.address, count(*) n from messages m join addresses a on a.ROWID=m.sender "
                         "where m.mailbox=? group by a.address order by n desc limit 1", (rid,)).fetchone()
        if rows and rows[0]:
            acct_addr.setdefault(b["acct"], rows[0].lower())
    if b["path"].upper() == "INBOX" or is_sent:
        # score iCloud-ness from the last 400 messages' senders + recipients
        mids = [r[0] for r in c.execute("select ROWID from messages where mailbox=? order by date_received desc limit 400", (rid,))]
        if not mids:
            continue
        q = ",".join("?" * len(mids))
        n = 0
        for (a,) in c.execute("select a.address from recipients r join addresses a on a.ROWID=r.address where r.message in (%s)" % q, mids):
            if a and any(h in a.lower() for h in ICLOUD_HINTS):
                n += 1
        for (a,) in c.execute("select a.address from messages m join addresses a on a.ROWID=m.sender where m.ROWID in (%s)" % q, mids):
            if a and any(h in a.lower() for h in ICLOUD_HINTS):
                n += 1
        acct_score[b["acct"]] = acct_score.get(b["acct"], 0) + n
icloud_acct = max(acct_score, key=acct_score.get) if acct_score and max(acct_score.values()) > 0 else None
status["icloud_account_uuid"] = icloud_acct
status["accounts"] = {k: {"address": acct_addr.get(k, "?"), "icloud_score": acct_score.get(k, 0)} for k in acct_score}


# ---- .emlx body reader
_dircache = {}


def mbox_data_dirs(b):
    key = (b["acct"], b["path"])
    if key not in _dircache:
        parts = [p + ".mbox" for p in b["path"].split("/") if p]
        base = os.path.join(MAILROOT, b["acct"], *parts)
        _dircache[key] = glob.glob(os.path.join(glob.escape(base), "*", "Data")) + [os.path.join(base, "Data")]
    return _dircache[key]


def emlx_path(rowid, b):
    k = rowid // 1000
    shard = "/".join(reversed(str(k))) if k else ""
    for d in mbox_data_dirs(b):
        for name in ("%d.emlx" % rowid, "%d.partial.emlx" % rowid):
            p = os.path.join(d, shard, "Messages", name) if shard else os.path.join(d, "Messages", name)
            if os.path.exists(p):
                return p
    return None


TAG = re.compile(r"<[^>]+>")


def body_text(path, limit):
    try:
        raw = open(path, "rb").read()
        nl = raw.index(b"\n")
        n = int(raw[:nl].strip())
        msg = email.message_from_bytes(raw[nl + 1:nl + 1 + n], policy=email.policy.default)
        part = msg.get_body(preferencelist=("plain", "html"))
        if part is None:
            return ""
        t = part.get_content()
        if part.get_content_type() == "text/html":
            t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
            t = html.unescape(TAG.sub(" ", re.sub(r"(?i)<br\s*/?>|</p>|</div>", "\n", t)))
        t = re.sub(r"[ \t\r\f\v]+", " ", t)
        t = re.sub(r"\n\s*\n+", "\n\n", t).strip()
        return t[:limit]
    except Exception as e:
        return ""


def summary_of(sid):
    if sid is None or "summary" not in mcols:
        return ""
    try:
        r = c.execute("select summary from summaries where ROWID=?", (sid,)).fetchone()
        return (r[0] or "") if r else ""
    except Exception:
        return ""


def recips(mid):
    to, cc = [], []
    tcol = "type" if "type" in rcols else None
    for row in c.execute("select r.%s, a.address, a.%s from recipients r join addresses a on a.ROWID=r.address "
                         "where r.message=? order by %s" % (tcol or "0", ACOM if ACOM != "''" else "address", "r.position" if "position" in rcols else "r.ROWID"), (mid,)):
        t, a, n = row
        s = ("%s <%s>" % (n, a)) if n else (a or "")
        (cc if t == 1 else to).append(s)
    return to, cc


deleted_clause = " and m.deleted=0" if "deleted" in mcols else ""
gid = "m.global_message_id" if "global_message_id" in mcols else "m.ROWID"


def pull(rid, days, body_limit):
    b = boxes[rid]
    cutoff = int(NOW - days * 86400)
    sel = ("select m.ROWID, s.subject, m.sender, m.date_received, %s, %s, %s from messages m "
           "left join subjects s on s.ROWID=m.subject where m.mailbox=? and m.date_received>=?%s "
           "order by m.date_received desc limit 2000") % (
        "m.date_sent" if "date_sent" in mcols else "m.date_received",
        "m.summary" if "summary" in mcols else "NULL",
        "m.message_id" if "message_id" in mcols else "NULL", deleted_clause)
    out = []
    for mid, subj, snd, recv, sent, sid, msgid in c.execute(sel, (rid, cutoff)):
        to, cc = recips(mid)
        p = emlx_path(mid, b)
        body = body_text(p, body_limit) if p else ""
        snip = summary_of(sid)
        out.append({
            "folder": "Sent" if b["path"].lower() in SENT_NAMES else b["path"],
            "account": acct_addr.get(b["acct"], b["acct"]),
            "date": fmt(sent if (b["path"].lower() in SENT_NAMES and sent) else recv),
            "epoch": int(sent if (b["path"].lower() in SENT_NAMES and sent) else recv or 0),
            "from": addr_of(snd), "to": to, "cc": cc,
            "subject": subj if isinstance(subj, str) else "(no subject)",
            "snippet": (snip or body[:240]).replace("\n", " ")[:240],
            "body": body, "body_found": bool(p),
        })
    return out


inbox, sent_icloud, sent_other = [], [], []
for rid, b in boxes.items():
    pth = b["path"].lower()
    if b["acct"] == icloud_acct and b["path"].upper() == "INBOX":
        inbox += pull(rid, INBOX_DAYS, INBOX_BODY)
    elif pth in SENT_NAMES:
        if b["acct"] == icloud_acct:
            sent_icloud += pull(rid, SENT_DAYS, SENT_BODY)
        else:
            sent_other += pull(rid, OTHER_SENT_DAYS, SENT_BODY)
for L in (inbox, sent_icloud, sent_other):
    L.sort(key=lambda m: -m["epoch"])

newest_inbox = inbox[0]["epoch"] if inbox else 0
newest_sent = sent_icloud[0]["epoch"] if sent_icloud else 0
data = {"source": "Apple Mail on Mac Studio (Envelope Index + .emlx), read-only",
        "icloud_account": acct_addr.get(icloud_acct, icloud_acct),
        "windows_days": {"icloud_inbox": INBOX_DAYS, "icloud_sent": SENT_DAYS, "other_accounts_sent": OTHER_SENT_DAYS},
        "icloud_inbox": inbox, "icloud_sent": sent_icloud, "other_accounts_sent": sent_other}
changed = write_if_changed(os.path.join(OUT, "icloud_mail_latest.json"), json.dumps(data, indent=1, ensure_ascii=False))


def md_block(m, n):
    s = "### %s — %s\n- From: %s\n- To: %s\n" % (m["date"], m["subject"], m["from"], ", ".join(m["to"]))
    if m["cc"]:
        s += "- Cc: %s\n" % ", ".join(m["cc"])
    s += "\n%s\n\n" % ((m["body"] or m["snippet"])[:n])
    return s


hdr = "_Mirror of Apple Mail on the Mac Studio, refreshed every 10 minutes. Times are Eastern. Mirror run: %s._\n\n" % fmt(NOW)
sent_md = "# Sent mail — last 7 days (iCloud + all other Mail accounts)\n\n" + hdr
week = NOW - 7 * 86400
for m in sorted([x for x in sent_icloud + sent_other if x["epoch"] >= week], key=lambda m: -m["epoch"]):
    sent_md += "**[%s]** " % m["account"] + md_block(m, 1200)
write_if_changed(os.path.join(OUT, "SENT_last7d.md"), sent_md)
inbox_md = "# iCloud Inbox — last 3 days (%s)\n\n" % data["icloud_account"] + hdr
for m in [x for x in inbox if x["epoch"] >= NOW - 3 * 86400]:
    inbox_md += "- %s | %s | %s — %s\n" % (m["date"], m["from"], m["subject"], m["snippet"][:160])
write_if_changed(os.path.join(OUT, "INBOX_last3d.md"), inbox_md)

# ---- health + self-heal
age_h = (NOW - newest_inbox) / 3600 if newest_inbox else 999
status.update({"ok": bool(icloud_acct), "icloud_account": data["icloud_account"],
               "newest_icloud_inbox": fmt(newest_inbox), "newest_icloud_sent": fmt(newest_sent),
               "inbox_age_hours": round(age_h, 2), "counts": {"icloud_inbox": len(inbox), "icloud_sent": len(sent_icloud),
               "other_sent": len(sent_other)}, "bodies_found_pct": round(100.0 * sum(m["body_found"] for m in inbox + sent_icloud + sent_other) / max(1, len(inbox + sent_icloud + sent_other)), 1),
               "json_changed": changed})
mail_running = subprocess.run(["/usr/bin/pgrep", "-x", "Mail"], capture_output=True).returncode == 0
status["mail_app_running"] = mail_running
stall_f = os.path.join(STATE, "stall_count")
stall = int(open(stall_f).read() or 0) if os.path.exists(stall_f) else 0
if (not mail_running) or age_h > STALE_HOURS:
    subprocess.run(["/usr/bin/open", "-g", "-a", "Mail"], capture_output=True)
    status["self_heal"] = "launched Mail in background (running=%s, inbox age %.1fh)" % (mail_running, age_h)
    stall = stall + 1 if age_h > 12 else 0
else:
    stall = 0
open(stall_f, "w").write(str(stall))
flag = os.path.join(STATE, "hq_row_added")
if stall >= 6 and not os.path.exists(flag):
    try:
        with open(HQ, "a") as f:
            f.write("| %s | **iCloud mail mirror stalled** — Apple Mail on the Mac Studio has not received iCloud mail for %d hours even after relaunching. Open Mail on the Mac Studio and check it is signed in to iCloud (Mail > Settings > Accounts). | provider-status-check; every reply check | %s | OPEN |\n" % (dt.date.today().isoformat(), int(age_h), dt.date.today().isoformat()))
        open(flag, "w").write(fmt(NOW))
    except Exception as e:
        log("HQ write failed", e)
elif stall == 0 and os.path.exists(flag):
    os.remove(flag)
if not icloud_acct:
    status["error"] = "could not identify the iCloud account in Mail"
status["mailboxes_seen"] = sorted({"%s/%s" % (acct_addr.get(b["acct"], b["acct"][:8]), b["path"]) for b in boxes.values()
                                   if b["path"].upper() == "INBOX" or b["path"].lower() in SENT_NAMES})
# ---- on-demand deep search (full history, every Mail account). A thread drops
#      Life OS/Mail Mirror/queries/<name>.json = {"text": "...", "from": "...", "subject": "...",
#      "since": "YYYY-MM-DD", "limit": 40, "all_accounts": false}; the next run (<=10 min, or at once after
#      `install_agent.sh com.valleypawn.icloud-mail-mirror --restart-only` via the host queue) writes
#      queries/results/<name>.md and moves the query to queries/done/. Matches subject, sender, recipients
#      and Mail's stored body summary; bodies come from the .emlx.
QD = os.path.join(OUT, "queries"); RD = os.path.join(QD, "results"); DD = os.path.join(QD, "done")
for d in (QD, RD, DD):
    os.makedirs(d, exist_ok=True)
for qf in sorted(glob.glob(os.path.join(QD, "*.json"))):
    name = os.path.splitext(os.path.basename(qf))[0]
    try:
        q = json.load(open(qf))
        lim = max(1, min(int(q.get("limit", 40)), 200))
        conds, args = [], []
        if not q.get("all_accounts"):
            ids = [r for r, b in boxes.items() if b["acct"] == icloud_acct]
            conds.append("m.mailbox in (%s)" % ",".join(str(i) for i in ids or [-1]))
        if q.get("since"):
            conds.append("m.date_received >= ?"); args.append(int(dt.datetime.strptime(q["since"], "%Y-%m-%d").timestamp()))
        if q.get("subject"):
            conds.append("s.subject like ?"); args.append("%" + q["subject"] + "%")
        if q.get("from"):
            conds.append("(sa.address like ? or sa.%s like ?)" % (ACOM if ACOM != "''" else "address")); args += ["%" + q["from"] + "%"] * 2
        if q.get("text"):
            t = "%" + q["text"] + "%"
            sumj = "or su.summary like ?" if "summary" in mcols else ""
            conds.append("(s.subject like ? or sa.address like ? or exists (select 1 from recipients r join addresses ra on ra.ROWID=r.address "
                         "where r.message=m.ROWID and (ra.address like ? or ra.%s like ?)) %s)" % (ACOM if ACOM != "''" else "address", sumj))
            args += [t, t, t, t] + ([t] if sumj else [])
        sql = ("select m.ROWID, m.mailbox from messages m left join subjects s on s.ROWID=m.subject "
               "left join addresses sa on sa.ROWID=m.sender %s where %s%s group by %s order by m.date_received desc limit %d") % (
            "left join summaries su on su.ROWID=m.summary" if "summary" in mcols else "",
            " and ".join(conds) or "1=1", deleted_clause, gid, lim)
        rows = list(c.execute(sql, args))
        md = "# Mail search: %s\n\n_Query %s, run %s, %d match(es), newest first._\n\n" % (name, json.dumps(q), fmt(NOW), len(rows))
        for mid, mbx in rows:
            b = boxes.get(mbx, {"acct": "?", "path": "?"})
            r = c.execute("select s.subject, m.sender, m.date_received from messages m left join subjects s on s.ROWID=m.subject where m.ROWID=?", (mid,)).fetchone()
            to, cc = recips(mid)
            p = emlx_path(mid, b) if b.get("acct") != "?" else None
            body = body_text(p, 2500) if p else ""
            md += "### %s — %s\n- Mailbox: %s / %s\n- From: %s\n- To: %s\n%s\n%s\n\n" % (
                fmt(r[2]), r[0] if isinstance(r[0], str) else "(no subject)", acct_addr.get(b["acct"], b["acct"][:8]), b["path"],
                addr_of(r[1]), ", ".join(to), ("- Cc: %s\n" % ", ".join(cc)) if cc else "", body or "(body not on disk)")
        write_atomic(os.path.join(RD, name + ".md"), md)
        os.replace(qf, os.path.join(DD, os.path.basename(qf)))
        log("query %s: %d matches" % (name, len(rows)))
    except Exception as e:
        write_atomic(os.path.join(RD, name + ".md"), "# Mail search: %s\n\nFAILED: %s\n" % (name, e))
        os.replace(qf, os.path.join(DD, os.path.basename(qf)))
        log("query %s failed: %s" % (name, e))

write_atomic(os.path.join(OUT, "status.json"), json.dumps(status, indent=1))
log("ok=%s inbox=%d sent=%d other_sent=%d newest_inbox=%s changed=%s" % (status["ok"], len(inbox), len(sent_icloud), len(sent_other), status["newest_icloud_inbox"], changed))
