#!/usr/bin/env python3
"""Unified local search: Apple Mail (.emlx) + iCloud Drive -> SQLite FTS5.
Usage:
  usearch.py mail        # (re)index Apple Mail
  usearch.py files       # (re)index iCloud Drive
  usearch.py query "..." [--mail|--files] [--since YYYY-MM-DD] [--from addr] [--path frag] [-n N]
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
    c.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
    return c


# ---------------- MAIL ----------------
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
        if m.is_multipart():
            plains, htmls = [], []
            for p in m.walk():
                if p.get_filename():
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
            if f.endswith(".emlx") and not f.endswith(".partial.emlx"):
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
            with open(path, "rb") as f:
                raw = f.read()
            body = pdf_text(raw)
            if len(body.strip()) < 40:
                needs_ocr = 1
        elif ext in ("jpg", "jpeg", "png", "heic", "tiff", "tif", "gif"):
            needs_ocr = 1
        body = body[:MAXTEXT]
        folder = os.path.dirname(path)
        folder = folder[len(ICLOUD) + 1:] if folder.startswith(ICLOUD) else folder
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
    print("found %d files" % len(paths), flush=True)
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


# ---------------- QUERY ----------------
def q(args):
    import argparse
    p = argparse.ArgumentParser(prog="usearch query")
    p.add_argument("terms", nargs="+")
    p.add_argument("--mail", action="store_true")
    p.add_argument("--files", action="store_true")
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
    want_mail = a.mail or not a.files
    want_files = a.files or not a.mail

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
    print("mail rows :", c.execute("SELECT count(*) FROM mail").fetchone()[0])
    print("file rows :", c.execute("SELECT count(*) FROM files").fetchone()[0])
    print("need OCR  :", c.execute("SELECT count(*) FROM files WHERE needs_ocr=1").fetchone()[0])
    print("db size   : %.0f MB" % (os.path.getsize(DB) / 1e6))


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
    elif cmd == "query":
        q(sys.argv[2:])
    elif cmd == "ocrlist":
        ocrlist()
    else:
        stats()
