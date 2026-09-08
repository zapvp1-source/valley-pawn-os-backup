#!/usr/bin/env python3
"""
eom_validate.py -- shared trust layer for Bravo End-of-Month exports (ADDITIVE)
==============================================================================
Created 2026-09-07. The single source of truth for the question every EOM
consumer needs answered before it reads a number:

    "Does this file actually cover the period its filename implies?"

WHY THIS EXISTS -- the filename collision
-----------------------------------------
Bravo's EOM handler names its output by END DATE only:

    output/<END_DATE>_<STORE>_end-of-month.xlsx

`monthly-analytics-prestage` pulls SIX different windows per store per month --
same-month / YTD / trailing-12, each for the current and prior year. **Every one
of those windows ends on the same day.** Six pulls, one filename. The last one
written wins, and the canonical month-end file is silently replaced by (usually)
the trailing-12-month pull. Balances survive (point-in-time); every FLOW figure
-- PSC, Sales Profit, layaway collections -- comes back ~11x too large.

Confirmed damage as of 2026-09-07: `2025-08-31_*` holds 9/1/2024-8/31/2025 and
`2026-08-31_*` holds 9/1/2025-8/31/2026, all 5 stores. 245 of 265 EOM files in
output/ are fine -- this is a RACE, not a deterministic bug, so any month can
lose. Independently observed by the Bonus Program engine (see
`Bonus Program/RUN_LOG.md`), which gates on the same thing.

WHAT THIS MODULE DOES (and deliberately does NOT do)
----------------------------------------------------
DOES:
  * read a file's OWN "Reporting Dates:" header and report the true range
  * resolve the best trustworthy file for a (store, month), searching known
    fallbacks in priority order and REFUSING anything whose range is wrong
  * maintain `eom_archive/` -- a range-stamped, collision-proof copy of every
    EOM export found on disk, named <START>_<END>_<STORE>.xlsx

DOES NOT (Rule #4 -- never modify hardened infra):
  * change `OutputFilename()` or any AHK handler
  * rename, move, or delete anything the pipeline wrote
  * touch monthly-analytics-prestage or any existing scheduled task
The archive is a pure add-alongside. Nothing breaks if it is ignored.

GOTCHA worth knowing: the "Reporting Dates:" label and its value are far to the
RIGHT (label ~col T/20, value ~col AY/51) and drift per store. Scan the FULL row
width -- a truncated column window silently finds nothing and every file then
looks unreadable rather than invalid.

USAGE
-----
    import eom_validate as ev
    hit = ev.resolve('CUL', '2026-08')      # -> {'path':..., 'source':..., 'range':...} or None
    ev.archive_all()                        # backfill/update the range-stamped archive

    python3 eom_validate.py archive         # backfill the archive, print a summary
    python3 eom_validate.py audit           # report every file whose range != its filename
    python3 eom_validate.py resolve 2025-01 2026-08
"""
import os, re, sys, glob, shutil, calendar
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'output')
ANALYTICS = os.path.join(OUT, 'monthly-analytics')
ARCHIVE = os.path.join(HERE, 'eom_archive')
STORES = ['CUL', 'HAR', 'LEX', 'ROA', 'WAY']

_RANGE_RE = re.compile(r'(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})')
_range_cache = {}


def _iso(mdy):
    """'8/1/2026' -> '2026-08-01'"""
    m, d, y = mdy.split('/')
    return f'{int(y):04d}-{int(m):02d}-{int(d):02d}'


def read_range(path, _ws=None):
    """Return (start_iso, end_iso) from the file's own header, or None.

    Cached by (path, mtime) -- callers hit this repeatedly across months.
    """
    try:
        key = (path, os.path.getmtime(path))
    except OSError:
        return None
    if key in _range_cache:
        return _range_cache[key]

    result = None
    # FAST PATH: an .xlsx is a zip; the range lives in the shared-string table.
    # openpyxl takes ~0.4s per 186-row workbook -- across 300 files that is two
    # minutes. Reading sharedStrings.xml directly is ~1ms and needs no parsing,
    # because the string is unique enough that a regex over the whole table is
    # unambiguous (it is the only "M/D/YYYY - M/D/YYYY" in an EOM export).
    try:
        import zipfile
        with zipfile.ZipFile(path) as z:
            for name in ('xl/sharedStrings.xml', 'xl/worksheets/sheet1.xml'):
                try:
                    blob = z.read(name).decode('utf-8', 'replace')
                except KeyError:
                    continue
                m = _RANGE_RE.search(blob)
                if m:
                    result = (_iso(m.group(1)), _iso(m.group(2)))
                    break
    except Exception:
        result = None

    if result is None and _ws is not None:
        # SLOW PATH: only when a caller already holds the worksheet.
        # Full row width -- the value sits around col AY and drifts per store.
        try:
            for r in range(1, 10):
                for c in range(1, _ws.max_column + 1):
                    v = _ws.cell(r, c).value
                    if v is None:
                        continue
                    m = _RANGE_RE.search(str(v))
                    if m:
                        result = (_iso(m.group(1)), _iso(m.group(2)))
                        break
                if result:
                    break
        except Exception:
            result = None
    _range_cache[key] = result
    return result


def read_store(path, _ws=None):
    """Store code from the filename if present, else from the sheet (row 2)."""
    base = os.path.basename(path)
    m = re.search(r'(?:^|[_-])(CUL|HAR|LEX|ROA|WAY)(?:[_.]|$)', base)
    if m:
        return m.group(1)
    try:
        import openpyxl
        ws = _ws or openpyxl.load_workbook(path, data_only=True).active
        for c in range(1, ws.max_column + 1):
            v = ws.cell(2, c).value
            if v and str(v).strip() in STORES:
                return str(v).strip()
    except Exception:
        pass
    return None


def month_bounds(ym):
    """'2026-08' -> ('2026-08-01', '2026-08-31')"""
    y, m = int(ym[:4]), int(ym[5:7])
    return f'{y:04d}-{m:02d}-01', f'{y:04d}-{m:02d}-{calendar.monthrange(y, m)[1]:02d}'


def covers_month(path, ym):
    """True only if the file's own range is EXACTLY the whole month."""
    r = read_range(path)
    return bool(r) and r == month_bounds(ym)


def _plus_year(ym):
    return f'{int(ym[:4]) + 1}-{ym[5:7]}'


def resolve(store, ym, verbose=False):
    """Best trustworthy EOM file for (store, month), or None.

    Priority -- first candidate whose OWN range is exactly the month wins:
      1. the canonical pipeline file                output/<lastday>_<STORE>_end-of-month.xlsx
      2. this month's staged same-month pull        monthly-analytics/<ym>/same-month-current_<STORE>.xlsx
      3. next year's staged prior-year pull         monthly-analytics/<ym+1y>/same-month-prior_<STORE>.xlsx
      4. the range-stamped archive                  eom_archive/<start>_<end>_<STORE>.xlsx
    A candidate that exists but carries the wrong range is REJECTED, never used
    with a caveat (vp-operating-rules Rule 18).
    """
    start, end = month_bounds(ym)
    cands = [
        ('pipeline',        os.path.join(OUT, f'{end}_{store}_end-of-month.xlsx')),
        ('analytics-same',  os.path.join(ANALYTICS, ym, f'same-month-current_{store}.xlsx')),
        ('analytics-prior', os.path.join(ANALYTICS, _plus_year(ym), f'same-month-prior_{store}.xlsx')),
        ('archive',         os.path.join(ARCHIVE, f'{start}_{end}_{store}.xlsx')),
    ]
    for src, p in cands:
        if not os.path.exists(p) or os.path.getsize(p) < 500:
            continue
        r = read_range(p)
        if r == (start, end):
            return {'path': p, 'source': src, 'range': r, 'store': store, 'month': ym}
        if verbose:
            print(f'    reject {src}: range={r} wanted={(start, end)}')
    return None


def _all_eom_files():
    yield from glob.glob(os.path.join(OUT, '*_end-of-month.xlsx'))
    yield from glob.glob(os.path.join(ANALYTICS, '*', '*.xlsx'))


def archive_all(quiet=False):
    """Copy every readable EOM export into eom_archive/<START>_<END>_<STORE>.xlsx.

    Collision-proof by construction: two different windows can no longer share a
    name, so a later pull can never destroy an earlier one's data. Additive --
    the source files are copied, never moved or altered.
    """
    os.makedirs(ARCHIVE, exist_ok=True)
    added = skipped = unreadable = 0
    for p in _all_eom_files():
        rng = read_range(p)
        store = read_store(p)
        if not rng or not store:
            unreadable += 1
            continue
        dest = os.path.join(ARCHIVE, f'{rng[0]}_{rng[1]}_{store}.xlsx')
        if os.path.exists(dest) and os.path.getsize(dest) == os.path.getsize(p):
            skipped += 1
            continue
        if not os.path.exists(dest):
            shutil.copy2(p, dest)
            added += 1
        else:
            skipped += 1
    if not quiet:
        print(f'archive: +{added} new, {skipped} already present, {unreadable} unreadable')
    return {'added': added, 'skipped': skipped, 'unreadable': unreadable}


def audit():
    """Report every output/ EOM file whose real range != the month its name implies."""
    bad = []
    for p in sorted(glob.glob(os.path.join(OUT, '*_end-of-month.xlsx'))):
        b = os.path.basename(p)
        parts = b.split('_')
        if len(parts) < 3 or len(parts[0]) != 10:
            continue
        d, store = parts[0], parts[1]
        if store not in STORES:
            continue
        ym = d[:7]
        # only month-END filenames claim to be a whole month
        if d != month_bounds(ym)[1]:
            continue
        r = read_range(p)
        if r != month_bounds(ym):
            bad.append((b, r))
    return bad


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'archive'
    if cmd == 'archive':
        archive_all()
    elif cmd == 'audit':
        bad = audit()
        print(f'month-end files whose range is WRONG: {len(bad)}')
        for b, r in bad:
            print(f'  {b}  ->  {r[0]} .. {r[1]}' if r else f'  {b}  ->  unreadable')
    elif cmd == 'resolve':
        lo = sys.argv[2] if len(sys.argv) > 2 else '2025-01'
        hi = sys.argv[3] if len(sys.argv) > 3 else '2026-12'
        ym = lo
        while ym <= hi:
            hits = {s: resolve(s, ym) for s in STORES}
            n = sum(1 for h in hits.values() if h)
            srcs = ','.join(sorted({h['source'] for h in hits.values() if h}))
            print(f'{ym}: {n}/5 resolved   [{srcs}]')
            y, m = int(ym[:4]), int(ym[5:7])
            ym = f'{y+1}-01' if m == 12 else f'{y}-{m+1:02d}'
    else:
        print(__doc__)
