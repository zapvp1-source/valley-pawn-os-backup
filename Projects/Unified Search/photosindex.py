#!/usr/bin/env python3
"""Index Photos.app screenshots into the Unified Search index (`photos` FTS5 table).

Why screenshots only (not the full ~22.7k-photo library): screenshots are the
category that actually contains searchable text (texts, emails, web pages,
confirmation codes...); ordinary camera photos almost never do, and OCR'ing
all of them would be ~15x the work for near-zero return. Scope can be widened
later (see --all-photos) if a real need shows up.

How it works:
  1. Enumerate screenshots via osxphotos (installed in the sibling .venv_photos
     venv -- system/brew Python is externally-managed, so a dedicated venv is
     the additive, non-destructive way to get the dependency).
  2. Skip any uuid already indexed (INCREMENTAL -- only new screenshots since
     the last run get exported+OCR'd; re-running this nightly is cheap).
  3. Export screenshots in ONE batch osxphotos CLI call, filename templated to
     the Photos uuid so results map back cleanly. --download-missing
     --use-photokit pulls down iCloud-only originals (Optimize Mac Storage
     means almost all screenshots aren't stored locally).
  4. Run tesseract OCR on each exported PNG.
  5. Insert (name, ocr_text, uuid, date, album, kind) into the `photos` table.
  6. Delete the exported scratch copies -- the originals in Photos.app are
     never touched, moved, or deleted. Read-only against the Photos library.

Usage: photosindex.py [--limit N] [--dry-run]
"""
import os, sys, sqlite3, subprocess, time, json

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents/Claude/Projects/Unified Search")
DB = os.path.join(PROJ, "index.db")
VENV_PY = os.path.join(PROJ, ".venv_photos/bin/python3")
OSXPHOTOS = os.path.join(PROJ, ".venv_photos/bin/osxphotos")
EXPORT_DIR = os.path.join(PROJ, "_photos_export")
LOG = os.path.join(PROJ, "photosindex.log")
MAXTEXT = 20000

os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")
os.environ["TESSDATA_PREFIX"] = "/opt/homebrew/share/tessdata"


def log(msg):
    line = "%s  %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def already_indexed_uuids(c):
    return {r[0] for r in c.execute("SELECT uuid FROM photos")}


def list_screenshot_uuids():
    """Ask osxphotos (via the venv) for every screenshot uuid + date + album."""
    script = (
        "import osxphotos, json\n"
        "db = osxphotos.PhotosDB()\n"
        "out = []\n"
        "for p in db.photos():\n"
        "    if not p.screenshot:\n"
        "        continue\n"
        "    albums = ', '.join(p.albums) if p.albums else ''\n"
        "    out.append({'uuid': p.uuid, 'date': p.date.isoformat() if p.date else '',\n"
        "                'filename': p.original_filename, 'album': albums})\n"
        "print(json.dumps(out))\n"
    )
    r = subprocess.run([VENV_PY, "-c", script], capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError("osxphotos enumeration failed: %s" % r.stderr[-2000:])
    return json.loads(r.stdout)


def export_batch(uuids, dest):
    """One osxphotos CLI call exports+downloads (from iCloud if needed) all given uuids,
    named by uuid so OCR results map back without a second metadata pass."""
    os.makedirs(dest, exist_ok=True)
    uuid_file = os.path.join(dest, "_uuids.txt")
    with open(uuid_file, "w") as f:
        f.write("\n".join(uuids))
    cmd = [OSXPHOTOS, "export", dest,
           "--uuid-from-file", uuid_file,
           "--filename", "{uuid}",
           "--download-missing", "--use-photokit",
           "--skip-original-if-edited",
           "--update"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60 * 60)
    if r.returncode != 0:
        log("export batch FAILED rc=%s stderr_tail=%s" % (r.returncode, r.stderr[-800:]))
    return r


def ocr_file(path):
    try:
        r = subprocess.run(["tesseract", path, "-"], capture_output=True, text=True, timeout=60)
        return (r.stdout or "").strip()[:MAXTEXT]
    except Exception as e:
        return ""


def main():
    limit = None
    dry = "--dry-run" in sys.argv
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    c = sqlite3.connect(DB)
    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS photos USING fts5(
        name, ocr_text,
        uuid UNINDEXED, date UNINDEXED, album UNINDEXED, kind UNINDEXED,
        tokenize="porter unicode61")""")
    c.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
    c.commit()

    log("enumerating screenshots via osxphotos...")
    all_shots = list_screenshot_uuids()
    log("found %d screenshots in Photos library" % len(all_shots))

    done = already_indexed_uuids(c)
    todo = [s for s in all_shots if s["uuid"] not in done]
    log("%d already indexed, %d new to process" % (len(done), len(todo)))

    if limit:
        todo = todo[:limit]
    if dry:
        for t in todo[:20]:
            log("  would process: %s %s %s" % (t["uuid"], t["date"], t["filename"]))
        log("dry-run: %d total would be processed" % len(todo))
        return

    if not todo:
        log("nothing new to index")
        c.execute("INSERT OR REPLACE INTO meta VALUES('photos_indexed_at',?)", (str(int(time.time())),))
        c.commit()
        return

    BATCH = 100
    ok = fail = 0
    t0 = time.time()
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        uuids = [t["uuid"] for t in chunk]
        meta_by_uuid = {t["uuid"]: t for t in chunk}
        log("batch %d/%d: exporting %d screenshots..." % (i // BATCH + 1, (len(todo) + BATCH - 1) // BATCH, len(uuids)))
        export_batch(uuids, EXPORT_DIR)

        rows = []
        for u in uuids:
            fpath = os.path.join(EXPORT_DIR, u + ".PNG")
            if not os.path.exists(fpath):
                # osxphotos may use different case/ext; edited photos export as
                # "<uuid>_edited.<ext>" (fix 2026-08-21: the old "<uuid>." prefix
                # match missed every edited screenshot -> ok=3 fail=190). Match on
                # bare uuid prefix so both "<uuid>.PNG" and "<uuid>_edited.jpeg" hit.
                cands = [f for f in os.listdir(EXPORT_DIR) if f.startswith(u)]
                fpath = os.path.join(EXPORT_DIR, cands[0]) if cands else None
            if not fpath or not os.path.exists(fpath):
                fail += 1
                continue
            text = ocr_file(fpath)
            m = meta_by_uuid[u]
            date_epoch = 0
            try:
                date_epoch = int(time.mktime(time.strptime(m["date"][:19], "%Y-%m-%dT%H:%M:%S")))
            except Exception:
                pass
            rows.append((m["filename"] or u, text, u, date_epoch, m["album"], "screenshot"))
            ok += 1
            try:
                os.remove(fpath)
            except Exception:
                pass

        if rows:
            c.executemany("INSERT INTO photos VALUES(?,?,?,?,?,?)", rows)
            c.commit()
        log("  batch done: ok=%d fail=%d elapsed=%ds" % (ok, fail, time.time() - t0))

    # clean up any leftover scratch files
    try:
        for f in os.listdir(EXPORT_DIR):
            if f != "_uuids.txt":
                os.remove(os.path.join(EXPORT_DIR, f))
    except Exception:
        pass

    c.execute("INSERT OR REPLACE INTO meta VALUES('photos_indexed_at',?)", (str(int(time.time())),))
    c.execute("INSERT OR REPLACE INTO meta VALUES('photos_count',?)", (str(int(c.execute('SELECT count(*) FROM photos').fetchone()[0])),))
    c.commit()
    log("PHOTOS INDEX DONE: ok=%d fail=%d in %ds" % (ok, fail, time.time() - t0))


if __name__ == "__main__":
    main()
