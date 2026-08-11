#!/usr/bin/env python3
"""Unified local search: Apple Mail (.emlx) + iCloud Drive + Google Drive cache -> SQLite FTS5.
(Apple Notes and Reminders are indexed by the sibling scripts notesindex.py / remindersindex.py.)
Usage:
  usearch.py mail        # (re)index Apple Mail
  usearch.py files       # (re)index iCloud Drive
  usearch.py gdrive      # ingest gdrive_cache/latest.jsonl into the gdrive table
  usearch.py query "..." [--mail|--files|--msgs|--notes|--reminders|--gdrive]
                          [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--from addr] [--path frag] [-n N] [--json]
  usearch.py stats
  usearch.py ocrlist     # list files needing OCR
"""
import os, sys, re, sqlite3, email, email.utils, html, zipfile, time, json, zlib
from email import policy
from multiprocessing import Pool, cpu_count

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents/Claude/Projects/Unified Search")
DB   = os.path.join(PROJ, "index.db")
MAIL = os.path.join(HOME, "Library/Mail")
ICLOUD = os.path.join(HOME, "Library/Mobile Documents/com~apple~CloudDocs")
MAXTEXT = 60000

TAG = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
TAG2 = re.compile(r"<[^>]+>")
WS = re.compile(r"[ \t\r\f\v]+")
NL = re.compile(r"\n{3,}")


def detag(s):
    s = TAG.sub(" ", s)
    s = TAG2.sub(" ", s)
    s = html.unescape(s)
    return NL.sub("\n\n", WS.sub(" ", s)).strip()


def db_connect():
    os.makedirs(PROJ, exist_ok=True)
    c = sqlite3.connect(DB, timeout=180)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA synchronous=NORMAL")
    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS mail USING fts5(
        subject, sender, recipients, body,
        path UNINDEXED, mailbox UNINDEXED, account UNINDEXED, ts UNINDEXED, msgid UNINDEXED,
        tokenize="porter unicode61")""")
    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS files USING fts5(
        name, folder, body,
        path UNINDEXED, ext UNINDEXED, mtime UNINDEXED, size UNINDEXED, needs_ocr UNINDEXED,
        tokenize="porter unicode61")""")
    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS msgs USING fts5(
        body, person, chatname,
        handle UNINDEXED, service UNINDEXED, ts UNINDEXED, from_me UNINDEXED, rowid_src UNINDEXED,
        tokenize="porter unicode61")""")
    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS notes USING fts5(
        title, body, folder,
        path_or_id UNINDEXED, mtime UNINDEXED, created UNINDEXED,
        tokenize="porter unicode61")""")
    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS reminders USING fts5(
        title, body, list_name,
        due UNINDEXED, completed UNINDEXED, mtime UNINDEXED, path_or_id UNINDEXED,
        tokenize="porter unicode61")""")
    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS gdrive USING fts5(
        name, folder, body,
        path_or_url UNINDEXED, mtime UNINDEXED, size UNINDEXED, mime_type UNINDEXED,
        tokenize="porter unicode61")""")
    c.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
    return c


# ---------------- MAIL ----------------
# Attachment indexing (added 2026-08-05).
# Before this, parse_emlx did `if p.get_filename(): continue` — every attachment
# was skipped, so ~10,600 PDF invoices/statements living in the mail store were
# invisible to search. Attachment text is appended to `body` behind an
# [ATTACHMENT: name] marker rather than added as a new column, so the FTS5 schema
# and every existing query keep working unchanged.
ATTACH_MAX = 40000          # per-message cap on extracted attachment text
ATTACH_MAX_BYTES = 40 * 1024 * 1024
ATTACH_EXT = {"pdf", "docx", "xlsx", "pptx", "txt", "csv", "tsv",
              "rtf", "htm", "html", "eml", "json", "xml", "md"}


def _ext_of(fn):
    return fn.rsplit(".", 1)[-1].lower() if "." in fn else ""


def _text_from_bytes(data, ext):
    """docx/xlsx/pptx and plain-text formats, from an in-memory buffer."""
    if ext in ("docx", "xlsx", "pptx"):
        import io
        chunks = []
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for nm in z.namelist():
                if nm.endswith(".xml") and any(
                        k in nm for k in ("document", "sharedStrings", "sheet",
                                          "slide", "comments", "notes")):
                    try:
                        chunks.append(z.read(nm).decode("utf-8", "ignore"))
                    except Exception:
                        pass
        return detag(" ".join(chunks))
    t = data.decode("utf-8", "ignore")
    if ext in ("htm", "html", "xml", "rtf"):
        t = detag(t)
    return WS.sub(" ", t)


def attach_text(part, fn):
    """Text from a MIME attachment carried inline in the .emlx. '' on any failure."""
    ext = _ext_of(fn)
    if ext not in ATTACH_EXT:
        return ""
    try:
        data = part.get_payload(decode=True)
    except Exception:
        return ""
    if not data or len(data) > ATTACH_MAX_BYTES:
        return ""
    try:
        if ext == "pdf":
            import tempfile
            tp = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
                    tf.write(data)
                    tp = tf.name
                return pdf_text_file(tp)
            finally:
                if tp:
                    try:
                        os.unlink(tp)
                    except Exception:
                        pass
        return _text_from_bytes(data, ext)
    except Exception:
        return ""


def disk_attach_text(path):
    """Text from an attachment already saved to disk by Mail."""
    ext = _ext_of(os.path.basename(path))
    if ext not in ATTACH_EXT:
        return ""
    try:
        if os.path.getsize(path) > ATTACH_MAX_BYTES:
            return ""
        if ext == "pdf":
            return pdf_text_file(path)
        with open(path, "rb") as f:
            return _text_from_bytes(f.read(ATTACH_MAX_BYTES), ext)
    except Exception:
        return ""


def disk_attachments(path):
    """Apple Mail saves downloaded attachments to a sibling tree:
         .../Data/a/b/c/d/Messages/<n>.emlx
         .../Data/a/b/c/d/Attachments/<n>/<part>/<filename>
    Returns [(filename, fullpath), ...] for message <n>."""
    out = []
    try:
        msgdir = os.path.dirname(path)                       # .../Messages
        msgnum = os.path.basename(path).split(".")[0]
        adir = os.path.join(os.path.dirname(msgdir), "Attachments", msgnum)
        if not os.path.isdir(adir):
            return out
        for r, _, fs in os.walk(adir):
            for f in fs:
                if f.startswith("."):
                    continue
                out.append((f, os.path.join(r, f)))
    except Exception:
        pass
    return out


def parse_emlx(path):
    try:
        with open(path, "rb") as f:
            head = f.readline()
            try:
                n = int(head.strip())
            except Exception:
                return None
            raw = f.read(n)
        m = email.message_from_bytes(raw, policy=policy.default)
        body = ""
        atts = []          # [ATTACHMENT: name] + extracted text
        att_budget = ATTACH_MAX
        if m.is_multipart():
            plains, htmls = [], []
            for p in m.walk():
                fn = p.get_filename()
                if fn:
                    fn = str(fn)
                    # always record the filename so name searches work even when
                    # the body can't be extracted (images, encrypted PDFs, stubs)
                    atts.append("\n\n[ATTACHMENT: %s]\n" % fn[:300])
                    if att_budget > 0:
                        t = attach_text(p, fn)
                        if t:
                            t = t[:att_budget]
                            att_budget -= len(t)
                            atts.append(t)
                    continue
                ct = p.get_content_type()
                if ct == "text/plain":
                    try:
                        plains.append(p.get_content())
                    except Exception:
                        pass
                elif ct == "text/html":
                    try:
                        htmls.append(p.get_content())
                    except Exception:
                        pass
            body = "\n".join(plains) if plains else detag("\n".join(htmls))
        else:
            try:
                body = m.get_content()
            except Exception:
                body = ""
            if m.get_content_type() == "text/html":
                body = detag(body)
        if not isinstance(body, str):
            body = str(body)
        body = body[:MAXTEXT]
        # attachments Mail already downloaded to the sibling Attachments/ tree
        seen = set(re.findall(r"\[ATTACHMENT: ([^\]]+)\]", "".join(atts)))
        for fn, fp in disk_attachments(path):
            if fn in seen:
                atts = [a for a in atts if a != "\n\n[ATTACHMENT: %s]\n" % fn[:300]]
            atts.append("\n\n[ATTACHMENT: %s]\n" % fn[:300])
            if att_budget > 0:
                t = disk_attach_text(fp)
                if t:
                    t = t[:att_budget]
                    att_budget -= len(t)
                    atts.append(t)
        if atts:
            body = body + "".join(atts)
        subj = str(m.get("Subject", ""))[:1000]
        snd = str(m.get("From", ""))[:500]
        rcpt = " ".join(str(m.get(h, "")) for h in ("To", "Cc"))[:2000]
        d = m.get("Date")
        ts = 0
        if d:
            try:
                ts = int(email.utils.parsedate_to_datetime(d).timestamp())
            except Exception:
                ts = 0
        rel = path[len(MAIL) + 1:]
        parts = rel.split("/")
        account = parts[1] if len(parts) > 1 else ""
        mbox = "/".join(p[:-5] for p in parts if p.endswith(".mbox")) or "?"
        return (subj, snd, rcpt, body, path, mbox, account, ts,
                str(m.get("Message-Id", ""))[:300])
    except Exception:
        return None


def index_mail():
    t0 = time.time()
    print("scanning .emlx ...", flush=True)
    paths = []
    for root, dirs, fs in os.walk(MAIL):
        for f in fs:
            if f.endswith(".emlx"):
                paths.append(os.path.join(root, f))
    print("found %d messages" % len(paths), flush=True)
    c = db_connect()
    c.execute("DELETE FROM mail")
    c.commit()
    n = 0
    batch = []
    with Pool(max(2, cpu_count() - 1)) as pool:
        for r in pool.imap_unordered(parse_emlx, paths, chunksize=200):
            if r:
                batch.append(r)
            if len(batch) >= 3000:
                c.executemany("INSERT INTO mail VALUES(?,?,?,?,?,?,?,?,?)", batch)
                c.commit()
                n += len(batch)
                batch = []
                print("  %d/%d  %ds" % (n, len(paths), time.time() - t0), flush=True)
    if batch:
        c.executemany("INSERT INTO mail VALUES(?,?,?,?,?,?,?,?,?)", batch)
        n += len(batch)
    c.commit()
    c.execute("INSERT OR REPLACE INTO meta VALUES('mail_indexed_at',?)", (str(int(time.time())),))
    c.execute("INSERT OR REPLACE INTO meta VALUES('mail_count',?)", (str(n),))
    c.commit()
    print("MAIL DONE: %d messages in %ds" % (n, time.time() - t0), flush=True)


# ---------------- FILES ----------------
TEXT_EXT = {"txt", "md", "csv", "tsv", "json", "log", "html", "htm", "xml", "py",
            "sh", "js", "css", "rtf", "vcf", "ics", "eml", "yaml", "yml"}

BT = re.compile(rb"BT(.*?)ET", re.S)
TJ = re.compile(rb"\((?:\\.|[^\\()])*\)")


def pdf_text(raw):
    out = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", raw, re.S):
        s = m.group(1)
        try:
            s = zlib.decompress(s)
        except Exception:
            pass
        if b"BT" not in s:
            continue
        for b in BT.findall(s):
            for t in TJ.findall(b):
                t = t[1:-1]
                t = re.sub(rb"\\([()\\])", rb"\1", t)
                try:
                    out.append(t.decode("latin-1"))
                except Exception:
                    pass
        if sum(len(x) for x in out) > MAXTEXT:
            break
    return WS.sub(" ", " ".join(out)).strip()



PDFTOTEXT = "/opt/homebrew/bin/pdftotext"

def pdf_text_file(path):
    """Real extraction via poppler; fall back to the naive stream parser."""
    if os.path.exists(PDFTOTEXT):
        try:
            import subprocess
            r = subprocess.run([PDFTOTEXT, "-q", "-enc", "UTF-8", "-l", "40", path, "-"],
                               capture_output=True, timeout=90)
            t = r.stdout.decode("utf-8", "ignore")
            if len(t.strip()) >= 20:
                return WS.sub(" ", t)[:MAXTEXT]
        except Exception:
            pass
    try:
        with open(path, "rb") as f:
            return pdf_text(f.read())
    except Exception:
        return ""


def extract_file(path):
    base = os.path.basename(path)
    ext = base.rsplit(".", 1)[-1].lower() if "." in base else ""
    needs_ocr = 0
    body = ""
    try:
        st = os.stat(path)
        if st.st_size > 80 * 1024 * 1024:
            return None
        if ext in TEXT_EXT:
            with open(path, "rb") as f:
                raw = f.read(MAXTEXT * 3)
            body = raw.decode("utf-8", "ignore")
            if ext in ("html", "htm", "xml", "rtf"):
                body = detag(body)
        elif ext in ("docx", "xlsx", "pptx"):
            chunks = []
            with zipfile.ZipFile(path) as z:
                for nm in z.namelist():
                    if nm.endswith(".xml") and any(k in nm for k in
                                                   ("document", "sharedStrings", "sheet", "slide", "comments", "notes")):
                        try:
                            chunks.append(z.read(nm).decode("utf-8", "ignore"))
                        except Exception:
                            pass
                        if sum(len(x) for x in chunks) > MAXTEXT * 3:
                            break
            body = detag(" ".join(chunks))
        elif ext == "pdf":
            body = pdf_text_file(path)
            if len(body.strip()) < 40:
                needs_ocr = 1
        elif ext in ("jpg", "jpeg", "png", "heic", "tiff", "tif", "gif"):
            needs_ocr = 1
        body = body[:MAXTEXT]
        folder = os.path.dirname(path)
        if folder.startswith(ICLOUD):
            folder = folder[len(ICLOUD) + 1:]
        elif folder.startswith(MAIL):
            rel = folder[len(MAIL) + 1:]
            mbox = "/".join(p[:-5] for p in rel.split("/") if p.endswith(".mbox"))
            folder = "MAIL ATTACHMENT " + (mbox or "")
        return (base, folder.replace("/", " "), body, path, ext,
                int(st.st_mtime), st.st_size, needs_ocr)
    except Exception:
        return None


def index_files():
    t0 = time.time()
    paths = []
    for root, dirs, fs in os.walk(ICLOUD):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in fs:
            if f.startswith("."):
                continue
            paths.append(os.path.join(root, f))
    n_icloud = len(paths)
    for root, dirs, fs in os.walk(MAIL):
        if "/Attachments/" not in root + "/":
            continue
        for f in fs:
            if f.startswith("."):
                continue
            paths.append(os.path.join(root, f))
    print("found %d files (%d iCloud + %d mail attachments)"
          % (len(paths), n_icloud, len(paths) - n_icloud), flush=True)
    c = db_connect()
    c.execute("DELETE FROM files")
    c.commit()
    n = 0
    ocr = 0
    batch = []
    with Pool(max(2, cpu_count() - 1)) as pool:
        for r in pool.imap_unordered(extract_file, paths, chunksize=25):
            if r:
                batch.append(r)
                ocr += r[7]
            if len(batch) >= 800:
                c.executemany("INSERT INTO files VALUES(?,?,?,?,?,?,?,?)", batch)
                c.commit()
                n += len(batch)
                batch = []
                print("  %d/%d %ds" % (n, len(paths), time.time() - t0), flush=True)
    if batch:
        c.executemany("INSERT INTO files VALUES(?,?,?,?,?,?,?,?)", batch)
        n += len(batch)
    c.commit()
    c.execute("INSERT OR REPLACE INTO meta VALUES('files_indexed_at',?)", (str(int(time.time())),))
    c.execute("INSERT OR REPLACE INTO meta VALUES('files_count',?)", (str(n),))
    c.commit()
    print("FILES DONE: %d files (%d need OCR) in %ds" % (n, ocr, time.time() - t0), flush=True)


# ---------------- GDRIVE ----------------
# Google Drive can't be crawled from a headless launchd script -- the Google
# Drive MCP connector only exists inside a live Cowork session. Coverage is
# populated by a separate Cowork scheduled task (daily, before this nightly
# rebuild) that writes one JSON object per file to gdrive_cache/latest.jsonl:
#   {"name":..., "folder":..., "body":..., "path_or_url":..., "mtime":...,
#    "size":..., "mime_type":...}
# This function just ingests whatever is currently in that cache file into
# the `gdrive` FTS5 table -- that part IS safe to run locally every night.
GDRIVE_CACHE_DIR = os.path.join(PROJ, "gdrive_cache")
GDRIVE_CACHE = os.path.join(GDRIVE_CACHE_DIR, "latest.jsonl")


def _gdrive_mtime(raw):
    if not raw:
        return 0
    try:
        if isinstance(raw, (int, float)):
            return int(raw)
        import datetime
        s = str(raw).replace("Z", "+00:00")
        return int(datetime.datetime.fromisoformat(s).timestamp())
    except Exception:
        return 0


def index_gdrive():
    t0 = time.time()
    c = db_connect()
    c.execute("DELETE FROM gdrive")
    c.commit()
    n = 0
    bad = 0
    if not os.path.exists(GDRIVE_CACHE):
        print("no gdrive cache at %s (nothing to ingest)" % GDRIVE_CACHE, flush=True)
        c.execute("INSERT OR REPLACE INTO meta VALUES('gdrive_indexed_at',?)", (str(int(time.time())),))
        c.execute("INSERT OR REPLACE INTO meta VALUES('gdrive_count',?)", ("0",))
        c.commit()
        return
    batch = []
    with open(GDRIVE_CACHE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                bad += 1
                continue
            name = str(o.get("name", ""))[:500]
            folder = str(o.get("folder", o.get("path", "")))[:500]
            body = str(o.get("body", ""))[:MAXTEXT]
            path = str(o.get("path_or_url", o.get("webViewLink", o.get("id", ""))))[:1000]
            mtime = _gdrive_mtime(o.get("mtime") or o.get("modifiedTime"))
            try:
                size = int(o.get("size") or 0)
            except Exception:
                size = 0
            mime_type = str(o.get("mime_type", o.get("mimeType", "")))[:200]
            batch.append((name, folder, body, path, mtime, size, mime_type))
            if len(batch) >= 500:
                c.executemany("INSERT INTO gdrive VALUES(?,?,?,?,?,?,?)", batch)
                c.commit()
                n += len(batch)
                batch = []
    if batch:
        c.executemany("INSERT INTO gdrive VALUES(?,?,?,?,?,?,?)", batch)
        n += len(batch)
    c.commit()
    c.execute("INSERT OR REPLACE INTO meta VALUES('gdrive_indexed_at',?)", (str(int(time.time())),))
    c.execute("INSERT OR REPLACE INTO meta VALUES('gdrive_count',?)", (str(n),))
    c.commit()
    print("GDRIVE DONE: %d files ingested from cache (%d bad lines skipped) in %ds"
          % (n, bad, time.time() - t0), flush=True)


# ---------------- QUERY ----------------
def q(args):
    import argparse
    p = argparse.ArgumentParser(prog="usearch query")
    p.add_argument("terms", nargs="+")
    p.add_argument("--mail", action="store_true")
    p.add_argument("--files", action="store_true")
    p.add_argument("--msgs", action="store_true")
    p.add_argument("--texts", action="store_true", dest="msgs")
    p.add_argument("--notes", action="store_true")
    p.add_argument("--reminders", action="store_true")
    p.add_argument("--gdrive", action="store_true")
    p.add_argument("--drive", action="store_true", dest="gdrive")
    p.add_argument("--since")
    p.add_argument("--until")
    p.add_argument("--from", dest="frm")
    p.add_argument("--path")
    p.add_argument("-n", type=int, default=25)
    p.add_argument("--json", action="store_true")
    a = p.parse_args(args)
    term = " ".join(a.terms)
    c = db_connect()
    res = []
    any_flag = a.mail or a.files or a.msgs or a.notes or a.reminders or a.gdrive
    want_mail = a.mail or not any_flag
    want_files = a.files or not any_flag
    want_msgs = a.msgs or not any_flag
    want_notes = a.notes or not any_flag
    want_reminders = a.reminders or not any_flag
    want_gdrive = a.gdrive or not any_flag

    def epoch(s):
        return int(time.mktime(time.strptime(s, "%Y-%m-%d"))) if s else None

    if want_mail:
        sql = ("SELECT 'mail',subject,sender,path,ts,mailbox,"
               "snippet(mail,3,'>>','<<',' ... ',18),bm25(mail) FROM mail WHERE mail MATCH ?")
        prm = [term]
        if a.since:
            sql += " AND ts>=?"; prm.append(epoch(a.since))
        if a.until:
            sql += " AND ts<=?"; prm.append(epoch(a.until))
        if a.frm:
            sql += " AND sender LIKE ?"; prm.append("%" + a.frm + "%")
        sql += " ORDER BY bm25(mail) LIMIT ?"
        prm.append(a.n)
        try:
            res += list(c.execute(sql, prm))
        except sqlite3.OperationalError as e:
            print("mail:", e)
    if want_files:
        sql = ("SELECT 'file',name,folder,path,mtime,ext,"
               "snippet(files,2,'>>','<<',' ... ',18),bm25(files) FROM files WHERE files MATCH ?")
        prm = [term]
        if a.path:
            sql += " AND path LIKE ?"; prm.append("%" + a.path + "%")
        if a.since:
            sql += " AND mtime>=?"; prm.append(epoch(a.since))
        sql += " ORDER BY bm25(files) LIMIT ?"
        prm.append(a.n)
        try:
            res += list(c.execute(sql, prm))
        except sqlite3.OperationalError as e:
            print("files:", e)
    if want_msgs:
        sql = ("SELECT 'text',person,chatname,handle,ts,service,"
               "snippet(msgs,0,'>>','<<',' ... ',18),bm25(msgs) FROM msgs WHERE msgs MATCH ?")
        prm = [term]
        if a.since:
            sql += " AND ts>=?"; prm.append(epoch(a.since))
        if a.until:
            sql += " AND ts<=?"; prm.append(epoch(a.until))
        if a.frm:
            sql += " AND person LIKE ?"; prm.append("%" + a.frm + "%")
        sql += " ORDER BY bm25(msgs) LIMIT ?"
        prm.append(a.n)
        try:
            res += list(c.execute(sql, prm))
        except sqlite3.OperationalError as e:
            print("msgs:", e)
    if want_notes:
        sql = ("SELECT 'note',title,folder,path_or_id,mtime,folder,"
               "snippet(notes,1,'>>','<<',' ... ',18),bm25(notes) FROM notes WHERE notes MATCH ?")
        prm = [term]
        if a.since:
            sql += " AND mtime>=?"; prm.append(epoch(a.since))
        if a.until:
            sql += " AND mtime<=?"; prm.append(epoch(a.until))
        sql += " ORDER BY bm25(notes) LIMIT ?"
        prm.append(a.n)
        try:
            res += list(c.execute(sql, prm))
        except sqlite3.OperationalError as e:
            print("notes:", e)
    if want_reminders:
        sql = ("SELECT 'remind',title,list_name,path_or_id,mtime,list_name,"
               "snippet(reminders,1,'>>','<<',' ... ',18),bm25(reminders) FROM reminders WHERE reminders MATCH ?")
        prm = [term]
        if a.since:
            sql += " AND mtime>=?"; prm.append(epoch(a.since))
        if a.until:
            sql += " AND mtime<=?"; prm.append(epoch(a.until))
        sql += " ORDER BY bm25(reminders) LIMIT ?"
        prm.append(a.n)
        try:
            res += list(c.execute(sql, prm))
        except sqlite3.OperationalError as e:
            print("reminders:", e)
    if want_gdrive:
        sql = ("SELECT 'gdrive',name,folder,path_or_url,mtime,folder,"
               "snippet(gdrive,2,'>>','<<',' ... ',18),bm25(gdrive) FROM gdrive WHERE gdrive MATCH ?")
        prm = [term]
        if a.path:
            sql += " AND path_or_url LIKE ?"; prm.append("%" + a.path + "%")
        if a.since:
            sql += " AND mtime>=?"; prm.append(epoch(a.since))
        sql += " ORDER BY bm25(gdrive) LIMIT ?"
        prm.append(a.n)
        try:
            res += list(c.execute(sql, prm))
        except sqlite3.OperationalError as e:
            print("gdrive:", e)

    res.sort(key=lambda r: r[7])
    if a.json:
        print(json.dumps([dict(kind=r[0], title=r[1], who=str(r[2]), path=r[3],
                               ts=r[4], ctx=r[5], snippet=r[6]) for r in res[:a.n]], indent=1))
        return
    if not res:
        print("no matches")
        return
    for r in res[:a.n]:
        d = time.strftime("%Y-%m-%d", time.localtime(r[4])) if r[4] else "----------"
        print("\n[%-4s] %s  %s" % (r[0], d, str(r[1])[:90]))
        print("       %s" % str(r[2])[:100])
        print("       %s" % r[6])
        print("       %s" % r[3])
    print("\n%d result(s)" % len(res))


def stats():
    c = db_connect()
    for k, v in c.execute("SELECT k,v FROM meta"):
        print("%-20s %s" % (k, v))
    print("mail rows     :", c.execute("SELECT count(*) FROM mail").fetchone()[0])
    print("file rows     :", c.execute("SELECT count(*) FROM files").fetchone()[0])
    print("msg rows      :", c.execute("SELECT count(*) FROM msgs").fetchone()[0])
    print("notes rows    :", c.execute("SELECT count(*) FROM notes").fetchone()[0])
    print("reminders rows:", c.execute("SELECT count(*) FROM reminders").fetchone()[0])
    print("gdrive rows   :", c.execute("SELECT count(*) FROM gdrive").fetchone()[0])
    print("need OCR      :", c.execute("SELECT count(*) FROM files WHERE needs_ocr=1").fetchone()[0])
    print("db size       : %.0f MB" % (os.path.getsize(DB) / 1e6))


def ocrlist():
    c = db_connect()
    for (p,) in c.execute("SELECT path FROM files WHERE needs_ocr=1 ORDER BY path"):
        print(p)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "mail":
        index_mail()
    elif cmd == "files":
        index_files()
    elif cmd == "gdrive":
        index_gdrive()
    elif cmd == "query":
        q(sys.argv[2:])
    elif cmd == "ocrlist":
        ocrlist()
    else:
        stats()
