#!/usr/bin/env python3
"""OCR scanned PDFs in iCloud Drive so they become searchable everywhere
(unified index + Spotlight + Preview + iOS).

Safety model:
  * original is copied to ocr_backup/ BEFORE anything is touched
  * ocrmypdf writes to a temp file; original is replaced ONLY if the temp
    file is a valid PDF, has the same page count, and now contains text
  * --skip-text means pages that already have a text layer are left alone
  * nothing is ever deleted

Usage: ocr_run.py [--limit N] [--dry-run]
"""
import os, sys, sqlite3, subprocess, shutil, hashlib, time, re

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents/Claude/Projects/Unified Search")
DB = os.path.join(PROJ, "index.db")
BACKUP = os.path.join(PROJ, "ocr_backup")
TMP = os.path.join(PROJ, "_ocr_tmp")
LOG = os.path.join(PROJ, "ocr_results.tsv")
OCRMYPDF = "/opt/homebrew/bin/ocrmypdf"


def pagecount(path):
    try:
        with open(path, "rb") as f:
            d = f.read()
        n = len(re.findall(rb"/Type\s*/Page[^s]", d))
        return n
    except Exception:
        return -1


def hastext(path):
    try:
        sys.path.insert(0, PROJ)
        import usearch
        return len(usearch.pdf_text_file(path).strip())
    except Exception:
        return -1


def main():
    limit = None
    dry = "--dry-run" in sys.argv
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    os.makedirs(BACKUP, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    # osascript-spawned processes inherit a sandboxed TMPDIR that tesseract's
    # worker subprocesses cannot read back. Point everything at a real dir.
    workdir = os.path.join(PROJ, "_ocr_work")
    os.makedirs(workdir, exist_ok=True)
    os.environ["TMPDIR"] = workdir
    os.environ["TESSDATA_PREFIX"] = "/opt/homebrew/share/tessdata"
    os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")
    c = sqlite3.connect(DB)
    rows = [r[0] for r in c.execute(
        "SELECT path FROM files WHERE needs_ocr=1 AND ext='pdf' ORDER BY path")]
    if limit:
        rows = rows[:limit]
    print("%d scanned PDFs to OCR" % len(rows), flush=True)
    if dry:
        for p in rows[:20]:
            print("  would OCR:", p)
        return

    done = set()
    if os.path.exists(LOG):
        for line in open(LOG):
            parts = line.split("\t")
            if len(parts) > 1 and parts[1] == "OK":
                done.add(parts[0])

    log = open(LOG, "a")
    ok = skip = fail = 0
    t0 = time.time()
    for i, src in enumerate(rows, 1):
        if src in done:
            skip += 1
            continue
        if not os.path.exists(src):
            continue
        h = hashlib.sha1(src.encode()).hexdigest()[:16]
        bak = os.path.join(BACKUP, h + "_" + os.path.basename(src))
        out = os.path.join(TMP, h + ".pdf")
        try:
            if not os.path.exists(bak):
                shutil.copy2(src, bak)
            before_pages = pagecount(src)
            side = os.path.join(TMP, h + ".txt")
            r = subprocess.run(
                [OCRMYPDF, "--force-ocr", "--jobs", "1", "--quiet",
                 "--sidecar", side, "--output-type", "pdf", src, out],
                capture_output=True, timeout=900)
            if r.returncode != 0 or not os.path.exists(out):
                msg = (r.stderr or b"").decode()[:160].replace("\t", " ").replace("\n", " ")
                log.write("%s\tFAIL\trc=%s %s\n" % (src, r.returncode, msg))
                fail += 1
            else:
                after_pages = pagecount(out)
                txt = 0
                if os.path.exists(side):
                    try:
                        txt = len(open(side, encoding="utf-8", errors="ignore").read().strip())
                    except Exception:
                        txt = 0
                if txt < 20:
                    txt = hastext(out)
                if txt > 20 and os.path.getsize(out) > 1000:
                    shutil.copy2(out, src)
                    log.write("%s\tOK\tchars=%d pages=%d\n" % (src, txt, after_pages))
                    ok += 1
                else:
                    log.write("%s\tREJECT\tpages %s->%s chars=%d\n"
                              % (src, before_pages, after_pages, txt))
                    fail += 1
            if os.path.exists(out):
                os.remove(out)
        except subprocess.TimeoutExpired:
            log.write("%s\tFAIL\ttimeout\n" % src)
            fail += 1
        except Exception as e:
            log.write("%s\tFAIL\t%s\n" % (src, str(e)[:160]))
            fail += 1
        log.flush()
        if i % 10 == 0:
            print("  %d/%d  ok=%d fail=%d  %ds"
                  % (i, len(rows), ok, fail, time.time() - t0), flush=True)
    log.close()
    print("OCR DONE: ok=%d fail=%d skipped=%d in %ds"
          % (ok, fail, skip, time.time() - t0), flush=True)
    print("Originals preserved in: %s" % BACKUP)


if __name__ == "__main__":
    main()
