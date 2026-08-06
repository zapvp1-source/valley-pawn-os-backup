#!/usr/bin/env python3
"""Index iMessage / SMS (~/Library/Messages/chat.db) into the Unified Search index.

Handles the two hard parts:
  1. ~half of modern messages have NULL `text` -- the content lives in the
     `attributedBody` typedstream blob. Decoded via pytypedstream.
  2. Handles are raw phone numbers / emails. Resolved to real contact names
     from the macOS AddressBook (.abcddb) so you can search "Preston" not "+1540...".

Adds/refreshes the `msgs` FTS5 table in index.db. Read-only against chat.db.
"""
import os, re, sqlite3, glob, time, sys

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents/Claude/Projects/Unified Search")
DB = os.path.join(PROJ, "index.db")
CHATDB = os.path.join(HOME, "Library/Messages/chat.db")
AB_GLOB = os.path.join(HOME, "Library/Application Support/AddressBook/Sources/*/AddressBook-v22.abcddb")
APPLE_EPOCH = 978307200

WS = re.compile(r"[ \t\r\f\v]+")
CLASSY = re.compile(r"^(NS|IM|__kIM|streamtyped|bplist|\$null)")


# ---------- attributedBody decoding ----------
def _decoder():
    try:
        from typedstream.stream import TypedStreamReader
    except Exception:
        return None

    def decode(blob):
        try:
            parts = []
            for ev in TypedStreamReader.from_data(blob):
                if isinstance(ev, bytes):
                    try:
                        s = ev.decode("utf-8")
                    except Exception:
                        continue
                    if not s or CLASSY.match(s):
                        continue
                    parts.append(s)
            if not parts:
                return ""
            # the message body is normally the first real string; guard by
            # falling back to the longest if the first looks like a token
            return parts[0] if len(parts[0]) > 3 else max(parts, key=len)
        except Exception:
            return ""
    return decode


def fallback_decode(blob):
    """Crude but serviceable if pytypedstream is unavailable."""
    try:
        b = blob
        if b"NSString" in b:
            b = b.split(b"NSString", 1)[1]
        if b"NSDictionary" in b:
            b = b.split(b"NSDictionary", 1)[0]
        s = b.decode("utf-8", "ignore")
        s = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", " ", s)
        return WS.sub(" ", s).strip(" +*\x01\x02\x84\x94")
    except Exception:
        return ""


# ---------- contacts ----------
def norm_phone(s):
    d = re.sub(r"\D", "", s or "")
    return d[-10:] if len(d) >= 10 else d


def load_contacts():
    book = {}
    for path in glob.glob(AB_GLOB):
        try:
            c = sqlite3.connect("file:%s?mode=ro" % path, uri=True)
            rows = c.execute("""
                SELECT r.ZFIRSTNAME, r.ZLASTNAME, r.ZORGANIZATION, p.ZFULLNUMBER
                FROM ZABCDRECORD r JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK""")
            for fn, ln, org, num in rows:
                name = " ".join(x for x in (fn, ln) if x) or org
                if name and num:
                    k = norm_phone(num)
                    if k:
                        book[k] = name
            rows = c.execute("""
                SELECT r.ZFIRSTNAME, r.ZLASTNAME, r.ZORGANIZATION, e.ZADDRESS
                FROM ZABCDRECORD r JOIN ZABCDEMAILADDRESS e ON e.ZOWNER = r.Z_PK""")
            for fn, ln, org, addr in rows:
                name = " ".join(x for x in (fn, ln) if x) or org
                if name and addr:
                    book[addr.lower().strip()] = name
            c.close()
        except Exception:
            continue
    return book


def resolve(handle, book):
    if not handle:
        return ""
    h = handle.strip()
    if "@" in h:
        return book.get(h.lower(), "")
    return book.get(norm_phone(h), "")


# ---------- main ----------
def build():
    t0 = time.time()
    if not os.path.exists(CHATDB):
        print("no chat.db found"); return
    dec = _decoder()
    if dec is None:
        print("WARN: pytypedstream missing, using fallback decoder", flush=True)
    book = load_contacts()
    print("contacts resolved: %d entries" % len(book), flush=True)

    src = sqlite3.connect("file:%s?mode=ro" % CHATDB, uri=True)
    src.text_factory = bytes
    out = sqlite3.connect(DB, timeout=180)
    out.execute("PRAGMA journal_mode=WAL")
    out.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS msgs USING fts5(
        body, person, chatname,
        handle UNINDEXED, service UNINDEXED, ts UNINDEXED, from_me UNINDEXED, rowid_src UNINDEXED,
        tokenize="porter unicode61")""")
    out.execute("DELETE FROM msgs")
    out.commit()

    q = """
    SELECT m.ROWID, m.date, m.is_from_me, m.text, m.attributedBody, m.service,
           h.id, c.display_name, c.chat_identifier
    FROM message m
    LEFT JOIN handle h ON m.handle_id = h.ROWID
    LEFT JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
    LEFT JOIN chat c ON c.ROWID = cmj.chat_id
    """
    batch = []
    n = 0
    empty = 0
    seen = set()
    for row in src.execute(q):
        rid, date, from_me, text, ab, service, handle, disp, chatid = row

        def s(v):
            if v is None:
                return ""
            if isinstance(v, bytes):
                try:
                    return v.decode("utf-8", "ignore")
                except Exception:
                    return ""
            return str(v)

        body = s(text)
        if not body.strip() and ab:
            blob = ab if isinstance(ab, bytes) else bytes(ab)
            body = (dec(blob) if dec else "") or fallback_decode(blob)
        body = WS.sub(" ", body).strip()
        if not body:
            empty += 1
            continue
        if rid in seen:
            continue
        seen.add(rid)

        try:
            d = int(date)
        except Exception:
            d = 0
        ts = int(d / 1e9) + APPLE_EPOCH if d > 1e11 else (d + APPLE_EPOCH if d > 0 else 0)

        hnd = s(handle)
        person = resolve(hnd, book) or hnd
        chatname = s(disp) or resolve(s(chatid), book) or s(chatid)
        fm = 1 if from_me else 0
        if fm:
            person = "Me -> " + (chatname or person)

        batch.append((body[:20000], person, chatname, hnd, s(service), ts, fm, rid))
        if len(batch) >= 2000:
            out.executemany("INSERT INTO msgs VALUES(?,?,?,?,?,?,?,?)", batch)
            out.commit(); n += len(batch); batch = []
            print("  %d ... %ds" % (n, time.time() - t0), flush=True)
    if batch:
        out.executemany("INSERT INTO msgs VALUES(?,?,?,?,?,?,?,?)", batch); n += len(batch)
    out.execute("INSERT OR REPLACE INTO meta VALUES('msgs_indexed_at',?)", (str(int(time.time())),))
    out.execute("INSERT OR REPLACE INTO meta VALUES('msgs_count',?)", (str(n),))
    out.commit()
    print("MSGS DONE: %d messages (%d empty/attachment-only) in %ds"
          % (n, empty, time.time() - t0), flush=True)


if __name__ == "__main__":
    build()
