#!/usr/bin/env python3
"""chekkit_optouts_sync.py [--days N] -- READ-ONLY (GET only), 2026-11-21. Chekkit is the only do-not-text source
(Joshua 11/18). Chekkit has no opt-out endpoint, so this reads conversations with activity in the last N days
(default 3) and keeps, per store, every customer phone whose latest keyword reply is an opt-out
(stop / unsubscribe / cancel / end / quit / remove / opt out); a later START / UNSTOP clears it.
Merges into fleet/state/chekkit_optouts/<STORE>.tsv (phone <tab> when <tab> words). Never sends anything."""
import sys, os, re, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_api as ck
UTC = dt.timezone.utc
days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 3
since = dt.datetime.now(UTC) - dt.timedelta(days=days)
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fleet", "state", "chekkit_optouts")
os.makedirs(OUT, exist_ok=True)
OPT = re.compile(r"\b(stop|stopall|unsubscribe|cancel|end|quit|remove|opt.?out)\b", re.I)
BACK = re.compile(r"^\s*(start|unstop|subscribe)\b", re.I)
for code in ("CUL", "HAR", "LEX", "ROA", "WAY"):
    path = os.path.join(OUT, code + ".tsv")
    have = {}
    if os.path.exists(path):
        for l in open(path):
            p = l.rstrip("\n").split("\t")
            if p and p[0]: have[p[0]] = p
    n = add = rem = err = 0
    before = None
    for _ in range(600):
        try:
            b = ck.get(code, "/v1/conversations?limit=50" + ("&before=" + before if before else "")) or {}
        except Exception:
            err += 1; break
        convs = b.get("conversations") or []
        stop = False
        for cv in convs:
            lt = ck.ts(cv.get("lastMessageAt"))
            if lt and lt < since:
                stop = True; continue
            p = ck.digits10((cv.get("customer") or {}).get("phone"))
            if not p: continue
            try:
                ms = (ck.get(code, "/v1/conversations/%s/messages?limit=60" % (cv.get("id") or cv.get("_id"))) or {}).get("messages") or []
            except Exception:
                err += 1; continue
            n += 1
            ev = []
            for m in ms:
                if m.get("sender") != "customer": continue
                t, tx = ck.ts(m.get("createdAt")), (m.get("text") or "").strip()
                if not t or len(tx) >= 60: continue
                if BACK.search(tx): ev.append((t, "in", tx))
                elif OPT.search(tx): ev.append((t, "out", tx))
            if not ev: continue
            t, kind, tx = max(ev)
            if kind == "out":
                if p not in have: add += 1
                have[p] = [p, t.isoformat(), re.sub(r"\s+", " ", tx)[:40]]
            elif p in have:
                del have[p]; rem += 1
        nb = b.get("nextBefore")
        if stop or not nb or nb == before or not convs: break
        before = nb
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        for p in sorted(have): f.write("\t".join(have[p]) + "\n")
    os.replace(tmp, path)
    print("%s days=%d conversations=%d added=%d cleared=%d total=%d errors=%d" % (code, days, n, add, rem, len(have), err), flush=True)
