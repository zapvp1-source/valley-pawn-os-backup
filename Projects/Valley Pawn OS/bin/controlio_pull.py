#!/usr/bin/env python3
"""controlio_pull.py — pull Controlio (employee monitoring) data via the official REST API.
Token: env CONTROLIO_TOKEN, else file  Projects/Valley Pawn OS/.secrets/controlio_token
Usage: controlio_pull.py START END [OUTDIR]     dates YYYY-MM-DD (inclusive)
Writes one JSON per endpoint to OUTDIR/<START>_<END>/ . Retries w/ backoff; pages via offset.
"""
import json, os, sys, time, pathlib, urllib.request, urllib.parse, urllib.error

BASE = "https://backend.controlio.net/api/v1"
HERE = pathlib.Path(__file__).resolve().parent.parent  # Valley Pawn OS
TOKEN_FILE = HERE / ".secrets" / "controlio_token"
PAGE = 5000
ENTITY = ["users", "computers", "departments", "categories", "rules", "logins"]
STATS = ["statistics/logons", "statistics/activities", "statistics/detailedActivities",
         "statistics/keystrokes", "statistics/printing", "statistics/searches",
         "statistics/alerts", "statistics/detailedFiles", "statistics/emails",
         "statistics/productivity", "statistics/users", "statistics/categories"]
DATED_EXTRA = ["audit_log"]

def token():
    t = os.environ.get("CONTROLIO_TOKEN") or (TOKEN_FILE.read_text().strip() if TOKEN_FILE.exists() else "")
    if not t: sys.exit("FATAL: no Controlio token")
    return t

def get(path, params, tok):
    url = f"{BASE}/{path}?{urllib.parse.urlencode(params, doseq=True)}"
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read() or b"null")
        except urllib.error.HTTPError as e:
            if e.code in (401, 403): raise
            if e.code in (400, 404, 422): return {"_error": e.code, "_body": e.read().decode()[:500]}
        except Exception:
            pass
        time.sleep(2 ** attempt)
    return {"_error": "retries_exhausted"}

def rows_of(d):
    if isinstance(d, list): return d
    if isinstance(d, dict):
        for k in ("data", "items", "rows", "results"):
            if isinstance(d.get(k), list): return d[k]
    return None

def pull(path, base_params, tok):
    out, off = [], 0
    while True:
        d = get(path, {**base_params, "limit": PAGE, "offset": off}, tok)
        rows = rows_of(d)
        if rows is None: return d  # non-list shape: return raw
        out += rows
        if len(rows) < PAGE: return out
        off += PAGE

def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    s, e = sys.argv[1], sys.argv[2]
    outroot = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else HERE.parent / "Controlio Monitoring" / "data"
    od = outroot / f"{s}_{e}"; od.mkdir(parents=True, exist_ok=True)
    tok = token(); summary = {}
    for p in ENTITY:
        r = pull(p, {}, tok); (od / f"{p}.json").write_text(json.dumps(r, indent=1, default=str))
        summary[p] = len(r) if isinstance(r, list) else "raw"
    for p in STATS + DATED_EXTRA:
        r = pull(p, {"start_time": s, "end_time": e}, tok)
        (od / f"{p.replace('/', '_')}.json").write_text(json.dumps(r, indent=1, default=str))
        summary[p] = len(r) if isinstance(r, list) else (r.get("_error") if isinstance(r, dict) else "raw")
    (od / "_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary))

if __name__ == "__main__":
    main()
