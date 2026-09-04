#!/usr/bin/env python3
"""
Index Photos.app CAMERA photos that Apple's on-device Vision classifier tagged as
document-like (receipts, invoices, printed pages, paper, business cards, currency,
menus, books) into the same `photos` FTS5 table that photosindex.py uses for
screenshots. New rows get kind='document_photo' so they're distinguishable from
kind='screenshot' but are searched together via `vpfind --photos` with zero changes
to the query engine.

Why a SEPARATE script instead of widening photosindex.py (2026-09-02):
photosindex.py deliberately scopes to screenshots only — its own docstring says OCR'ing
the full ~22.7k-photo library would be "~15x the work for near-zero return." That's true
for the library as a WHOLE, but Joshua's actual complaint is narrower: Photos.app's search
can't usefully surface photos HE TOOK OF PAPER (invoices, receipts, documentation) mixed in
with the rest of the camera roll. Apple's own on-device classifier (exposed via osxphotos'
`.labels`) already tags these — a one-time probe of the library found:
    2925 Document | 831 Printed Page | 113 Receipt | 40 Money | 39 Book | 33 Paper | 33 Currency
  -> 2,957 unique candidate photos (union of labels, ~14% of the 21,501 non-screenshot photos)
Filtering to that set before exporting+OCR'ing keeps this cheap and targeted instead of
brute-forcing the whole library, and never touches photosindex.py (Rule #4 — additive only,
hardened infra untouched). Rerunning this script is incremental and cheap: it skips any uuid
already in the table, so a nightly run only processes photos taken/tagged since the last run.

Usage: photosindex_documents.py [--limit N] [--dry-run]
"""
import os, sys, sqlite3, subprocess, time, json

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents/Claude/Projects/Unified Search")
DB = os.path.join(PROJ, "index.db")
VENV_PY = os.path.join(PROJ, ".venv_photos/bin/python3")
OSXPHOTOS = os.path.join(PROJ, ".venv_photos/bin/osxphotos")
EXPORT_DIR = os.path.join(PROJ, "_docphotos_export")
LOG = os.path.join(PROJ, "photosindex_documents.log")
MAXTEXT = 20000

# Apple Vision / Photos.app scene-classifier labels that indicate "this photo is of a
# document," not a person/place/thing. Deliberately conservative — false positives just
# mean a harmless extra OCR pass, but wide enough to actually catch the target use case
# (invoices, receipts, paperwork, business cards, printed contracts).
DOC_LABELS = {
    "Document", "Receipt", "Printed Page", "Paper", "Text",
    "Business Card", "Currency", "Money", "Book", "Menu",
}

os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")
os.environ["TESSDATA_PREFIX"] = "/opt/homebrew/share/tessdata"


def log(msg):
    line = "%s  %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def already_indexed_uuids(c):
    return {r[0] for r in c.execute("SELECT uuid FROM photos WHERE kind='document_photo'")}


def list_document_candidates():
    """Ask osxphotos (via the venv) for every non-screenshot photo whose Vision labels
    intersect DOC_LABELS. Cheap — reads cached Photos library metadata, no export/OCR."""
    script = (
        "import osxphotos, json\n"
        "DOC_LABELS = " + repr(DOC_LABELS) + "\n"
        "db = osxphotos.PhotosDB()\n"
        "out = []\n"
        "for p in db.photos():\n"
        "    if p.screenshot or p.ismovie:\n"
        "        continue\n"
        "    labels = set(p.labels or [])\n"
        "    hit = labels & DOC_LABELS\n"
        "    if not hit:\n"
        "        continue\n"
        "    albums = ', '.join(p.albums) if p.albums else ''\n"
        "    out.append({'uuid': p.uuid, 'date': p.date.isoformat() if p.date else '',\n"
        "                'filename': p.original_filename, 'album': albums,\n"
        "                'labels': sorted(hit),\n"
        "                'ismissing': bool(p.ismissing), 'iscloudasset': bool(p.iscloudasset)})\n"
        "print(json.dumps(out))\n"
    )
    r = subprocess.run([VENV_PY, "-c", script], capture_output=True, text=True, timeout=300)
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


import re
_WORD_RE = re.compile(r"[A-Za-z]{3,}")


def _tesseract_text(img_path):
    try:
        r = subprocess.run(["tesseract", img_path, "-"], capture_output=True, text=True, timeout=60)
        return (r.stdout or "").strip()[:MAXTEXT]
    except Exception:
        return ""


def _score(text):
    """Crude but effective: count plausible English-letter word tokens. Garbled/wrong-orientation
    OCR output scores near zero (leptonica reads scrambled runs, few 3+ letter alpha tokens);
    correctly-oriented text scores in the dozens+. Used to pick the best of 4 rotations."""
    if not text:
        return -1
    return len(_WORD_RE.findall(text))


def ocr_file(path):
    """OCR one exported photo.

    Two fixes layered on top of the naive `tesseract path -` call photosindex.py uses for
    screenshots (screenshots are already upright and PNG, so they don't need either fix):

    1. HEIC (2026-09-02): tesseract's leptonica build here has no HEIC decoder -- it fails
       SILENTLY (empty stdout, not an exception) on .HEIC input, which is the format nearly
       all iPhone camera photos export as. A first pass against 20 real "Document"-labeled
       photos came back 9/10 empty for exactly this reason. Fix: convert to PNG first via
       macOS's built-in `sips` (no extra dependency, handles HEIC natively).

    2. Orientation (2026-09-02): unlike screenshots, camera photos of paper are frequently
       held sideways/upside-down relative to how they photograph -- sips' orientation-tag
       handling did not reliably correct this, and tesseract on a wrong-orientation image
       doesn't error, it just returns scrambled garbage (verified: same document scored
       ~0 real words at 0 rotation, ~40 real words at the correct 90 degree rotation). Fix:
       run OCR at all 4 rotations and keep whichever produced the most plausible text via
       _score(). ~4x the tesseract calls, but tesseract itself is fast (<1s/image) so this
       is a worthwhile trade for not silently indexing garbage.
    """
    tmp_png = path + ".ocr.png"
    r = subprocess.run(["sips", "-s", "format", "png", path, "--out", tmp_png],
                        capture_output=True, text=True, timeout=60)
    if r.returncode != 0 or not os.path.exists(tmp_png):
        return ""  # unconvertable -- name field (with labels) still makes it findable

    best_text, best_score = "", -1
    rotated_tmp = None
    try:
        for deg in (0, 90, 180, 270):
            cand = tmp_png
            if deg:
                rotated_tmp = path + (".ocr_r%d.png" % deg)
                rr = subprocess.run(["sips", "--rotate", str(deg), tmp_png, "--out", rotated_tmp],
                                     capture_output=True, text=True, timeout=60)
                if rr.returncode != 0 or not os.path.exists(rotated_tmp):
                    continue
                cand = rotated_tmp
            text = _tesseract_text(cand)
            sc = _score(text)
            if sc > best_score:
                best_text, best_score = text, sc
            if rotated_tmp and os.path.exists(rotated_tmp):
                os.remove(rotated_tmp)
                rotated_tmp = None
            if best_score >= 25:  # already clearly upright and legible -- stop early
                break
        return best_text
    finally:
        for p in (tmp_png, rotated_tmp):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass


def main():
    limit = None
    dry = "--dry-run" in sys.argv
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    c = sqlite3.connect(DB)
    # Reuses the SAME `photos` FTS5 table photosindex.py created (kind column already exists,
    # UNINDEXED) — no schema change needed. Belt-and-suspenders CREATE in case this ever runs
    # standalone against a fresh db.
    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS photos USING fts5(
        name, ocr_text,
        uuid UNINDEXED, date UNINDEXED, album UNINDEXED, kind UNINDEXED,
        tokenize="porter unicode61")""")
    c.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
    c.commit()

    log("enumerating document-like candidate photos via osxphotos labels...")
    candidates = list_document_candidates()
    log("found %d document-like candidates (labels: %s)" % (len(candidates), sorted(DOC_LABELS)))

    done = already_indexed_uuids(c)
    todo = [p for p in candidates if p["uuid"] not in done]
    log("%d already indexed, %d new to process" % (len(done), len(todo)))

    if limit:
        todo = todo[:limit]

    if dry:
        for t in todo[:30]:
            log("  would process: %s %s %s labels=%s" % (t["uuid"], t["date"], t["filename"], t["labels"]))
        log("dry-run: %d total would be processed" % len(todo))
        return

    if not todo:
        log("nothing new to index")
        c.execute("INSERT OR REPLACE INTO meta VALUES('doc_photos_indexed_at',?)", (str(int(time.time())),))
        c.commit()
        return

    BATCH = 100
    ok = fail = skipped_missing = 0
    t0 = time.time()
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        uuids = [t["uuid"] for t in chunk]
        meta_by_uuid = {t["uuid"]: t for t in chunk}
        log("batch %d/%d: exporting %d document photos..." % (
            i // BATCH + 1, (len(todo) + BATCH - 1) // BATCH, len(uuids)))
        export_batch(uuids, EXPORT_DIR)

        rows = []
        for u in uuids:
            m = meta_by_uuid[u]
            cands = [f for f in os.listdir(EXPORT_DIR) if f.startswith(u)]
            fpath = os.path.join(EXPORT_DIR, cands[0]) if cands else None
            if not fpath or not os.path.exists(fpath):
                # 2026-09-03 fix: a photo can be permanently unexportable -- Photos.app has a
                # metadata row (so it still surfaces via db.photos()/labels) but no local file
                # AND it isn't a cloud asset either, so there is nothing for osxphotos to ever
                # download (confirmed via `p.ismissing=True, p.iscloudasset=False, p.path=None`
                # on a real case, F9B761E7-811B-43AF-B49D-61E123CD51E8 -- likely an orphaned
                # library reference, e.g. original deleted outside Photos). Retrying that case
                # nightly is pointless -- it will never succeed -- and it silently inflated
                # `fail` forever (fail=1 every single run since 2026-09-02) while never getting
                # marked done. Genuine cloud-asset-not-yet-downloaded cases (ismissing=True,
                # iscloudasset=True) are still transient and stay in `fail` so they retry.
                if m.get("ismissing") and not m.get("iscloudasset"):
                    label_tag = " ".join(m["labels"])
                    name = "%s [%s] (unexportable -- no local file, not in iCloud)" % (m["filename"] or u, label_tag)
                    date_epoch = 0
                    try:
                        date_epoch = int(time.mktime(time.strptime(m["date"][:19], "%Y-%m-%dT%H:%M:%S")))
                    except Exception:
                        pass
                    rows.append((name, "", u, date_epoch, m["album"], "document_photo"))
                    skipped_missing += 1
                else:
                    fail += 1
                continue
            text = ocr_file(fpath)
            date_epoch = 0
            try:
                date_epoch = int(time.mktime(time.strptime(m["date"][:19], "%Y-%m-%dT%H:%M:%S")))
            except Exception:
                pass
            # Prefix the labels into the name field too, so "receipt" or "document" alone
            # can surface a match even on photos where OCR came back thin/empty (blurry shot,
            # handwriting tesseract can't read, etc.) — degrade gracefully instead of silently
            # dropping the photo from search entirely.
            label_tag = " ".join(m["labels"])
            name = "%s [%s]" % (m["filename"] or u, label_tag)
            rows.append((name, text, u, date_epoch, m["album"], "document_photo"))
            ok += 1
            try:
                os.remove(fpath)
            except Exception:
                pass
        if rows:
            c.executemany("INSERT INTO photos VALUES(?,?,?,?,?,?)", rows)
            c.commit()
        log("  batch done: ok=%d fail=%d skipped_missing=%d elapsed=%ds" % (ok, fail, skipped_missing, time.time() - t0))

    try:
        for f in os.listdir(EXPORT_DIR):
            if f != "_uuids.txt":
                os.remove(os.path.join(EXPORT_DIR, f))
    except Exception:
        pass

    c.execute("INSERT OR REPLACE INTO meta VALUES('doc_photos_indexed_at',?)", (str(int(time.time())),))
    c.execute("INSERT OR REPLACE INTO meta VALUES('doc_photos_count',?)",
              (str(int(c.execute("SELECT count(*) FROM photos WHERE kind='document_photo'").fetchone()[0])),))
    c.commit()
    log("DOCUMENT PHOTOS INDEX DONE: ok=%d fail=%d skipped_missing=%d in %ds" % (ok, fail, skipped_missing, time.time() - t0))


if __name__ == "__main__":
    main()
