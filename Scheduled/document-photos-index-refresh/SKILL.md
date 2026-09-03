---
name: document-photos-index-refresh
description: Nightly incremental OCR index of Photos.app camera photos classified as documents/receipts (invoices, receipts, paperwork) into the Unified Search index — separate from and additive to unified-search-index-refresh.
---

This is an automated scheduled run. The user (Joshua) is not present — execute autonomously, no clarifying questions. FIX-FORWARD: if something breaks mid-run, try to overcome it in-run rather than just reporting failure.

## Background
Joshua's Photos.app search is poor at surfacing photos he's taken of invoices, receipts, and documentation mixed into his regular camera roll. On 2026-09-02 a companion indexer, `photosindex_documents.py`, was built at `~/Documents/Claude/Projects/Unified Search/` to OCR just the document-like subset of his photo library (identified via Apple's own on-device Vision/scene-classifier labels — Document, Receipt, Printed Page, Paper, Text, Business Card, Currency, Money, Book, Menu) into the SAME `photos` FTS5 table in `index.db` that the existing `photosindex.py` (screenshots-only) populates, distinguished by `kind='document_photo'`. Results are searchable immediately via `vpfind --photos "term"` — no query-engine changes needed.

This is a SEPARATE, INDEPENDENT task from `unified-search-index-refresh` (which runs at 3:30 AM and owns `refresh.sh`/`refresh_hardened.sh`) — deliberately, so this never touches that hardened pipeline (Rule #4, additive only). Scheduled 90 minutes after it (5:00 AM) purely to avoid resource contention, not because they're coupled.

Two non-obvious fixes are baked into `photosindex_documents.py`'s `ocr_file()` — do not "simplify" them if you ever touch this file:
1. Tesseract's leptonica build here has NO HEIC decoder and fails SILENTLY (empty output, not an error) on .HEIC input, which is what nearly all iPhone photos are. Every photo is converted to PNG via macOS's built-in `sips` before OCR.
2. Camera photos (unlike screenshots) are often sideways/upside-down. Wrong-orientation OCR doesn't error, it just returns scrambled garbage. The script tries all 4 rotations (0/90/180/270 via `sips --rotate`) and keeps whichever produced the most real-looking words (simple word-count heuristic), stopping early once a rotation scores well.

The script is INCREMENTAL by design: it skips any photo `uuid` already present in the `photos` table with `kind='document_photo'`, so a nightly run only processes photos newly taken/tagged since the last run — normally a handful, not the full backlog. The initial backfill (~2,957 candidate photos) was run once manually on 2026-09-02 and takes a long time (each photo can take several seconds due to iCloud download + 4x OCR passes); nightly incremental runs should be fast (well under 10 minutes) unless Joshua took a lot of document photos that day.

## What to do
1. Launch in the BACKGROUND via `mcp__Control_your_Mac__osascript` (a foreground call risks the tool's own timeout on a big run):
   ```
   do shell script "(cd '/Users/joshuadavis/Documents/Claude/Projects/Unified Search' && .venv_photos/bin/python3 photosindex_documents.py) > /tmp/docphotos_nightly.log 2>&1 < /dev/null & echo launched"
   ```
2. Poll every ~2-3 minutes (sleep in chunks, the osascript tool itself can't sleep long) by tailing `~/Documents/Claude/Projects/Unified Search/photosindex_documents.log` and checking `pgrep -laf photosindex_documents`.
3. Time budget: up to 30 minutes for a normal incremental run. If it's still processing a large batch past that (e.g. Joshua bulk-imported old photos), let it keep running up to 60 minutes total before treating it as slow-but-fine — do not kill it.
4. Success = the log contains `DOCUMENT PHOTOS INDEX DONE:` with `fail=0` or a small fail count relative to `ok`. Verify against that literal output, not just that the process exited (Rule #12).
5. On success: silent, no Slack post — this mirrors the existing `unified-search-index-refresh` task's silent-success convention (Rule #16 — no routine success/failure noise to Slack). Just end your turn.
6. On failure (process died, or `DOCUMENT PHOTOS INDEX DONE` never appears): read the log, try ONE fix-forward retry if the cause looks transient (e.g. a stale `.osxphotos_export.db` lock in `_docphotos_export/`, or a partial `_docphotos_export/` directory left over from a killed run — safe to delete and retry). If it fails a second time, send ONE plain-language Slack DM to Joshua (`D03BHQH5VGT`): "⚠️ Scheduled task \"document-photos-index-refresh\" did not complete — <date>." No technical detail in the DM; that goes in your final report only. Never post failure detail to any team channel.
7. Constraints: this task's script (`photosindex_documents.py`) is additive infra of its own now — do not modify `photosindex.py`, `refresh.sh`, or `refresh_hardened.sh` from this task under any circumstance. If `photosindex_documents.py` itself needs a surgical bug fix during fix-forward, make it, and log the fix in the Valley Pawn OS CHANGELOG (`~/Documents/Claude/Projects/Valley Pawn OS/CHANGELOG.md`) before ending your turn.
