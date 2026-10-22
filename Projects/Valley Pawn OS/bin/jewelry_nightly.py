#!/usr/bin/env python3
"""jewelry_nightly.py — native replacement for the jewelry-onhand-nightly-pull + jewelry-onhand-catchup Cowork
tasks (2026-10-14). Same data, same rules, same #jewlery-counts table; no Claude session, no connector.

  jewelry_nightly.py nightly [--date D] [--send] [--no-pull]    Mon-Sat 20:30 slot (agent com.valleypawn.jewelry-nightly)
  jewelry_nightly.py catchup [--date D] [--send]                next-morning catch-up (agent com.valleypawn.jewelry-catchup)
  jewelry_nightly.py --render [--date D] [--catchup]            build tonight's message from what is on disk, print it, post nothing
  jewelry_nightly.py sheets --date D [--stores WAY]             vision-read the PM count sheets only (JSON to stdout)
  jewelry_nightly.py followup --date D --stores WAY [--send]    one extra post for store(s) a run left out (CSV must exist)

Without --send nothing is posted (the message goes to fleet/test_output/). The launchd wrappers pass --send and are
DORMANT behind bin/vp_live.sh until fleet/state/native_live/jewelry-onhand-nightly-pull (resp. -catchup) exists.

RULES (from the cloud SKILL.md, reproduced):
  STEP 0 open-stores gate = bin/vp_lib.sh open_stores (Sun none; Wed CUL+ROA before 10/14, CUL+ROA+WAY from 10/14;
         every other day all 5). "Complete" = every OPEN store.
  Freeze window: Bravo's jewelry report is a LIVE on-hand query. It is only comparable with the PM sheet while the store
         is closed: after that day's close (18:00; 17:00 Saturday at the 6-day stores CUL/ROA/WAY) and before the next
         open day's 10:00 opening. Nightly pulls run from 20:30; the catch-up only pulls before 10:00.
  STEP 2 one trigger per open store, cell jewelry-case-counts-v3 (V3 block 2026-10-06), one at a time via
         bin/bravo_pull.sh (which waits for the watcher, never runs two at once).
  STEP 4 all-or-nothing per store: result success, CSV present for the date. EMPTY-CATEGORY RULE: a Charms/Brooches
         row with status=error counts as 0 ONLY if the same store+category was also error/0 in the most recent
         prior-day CSV. Any other error = that store is not complete. A v3 duplicate error is never overridden.
  STEP 5 PM count sheets: fleet/eod_photos/<date>/ (com.valleypawn.eod-photo-fetch 20:15), read with the Claude API
         (bin/vp_ai.py vision). Store = the sheet's own printed header (END OF DAY: <STORE>), roster as fallback.
         A sheet that is unreadable or whose 5 categories do not add up to its own TOTALS is not used (never guessed).
  STEP 6 table: RINGS=Rings, BRACELETS=Bracelets, EARRINGS=Earrings, PENDANTS=Pendants+Charms+Brooches,
         NECKLACES=Chains+Necklaces. Store rows in CUL, HAR, LEX, ROA, WAY order; a store with no sheet gets the line
         "<Store> — count sheet not posted tonight." under the table.
  STEP 7 DM Joshua only if a store's total is OVER (counted > expected) by more than 5, or the run did not complete.
  STEP 8 run record appended to Jewelry Count Reconciliation/STATUS.md.
"""
import base64
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
BRAVO = os.path.join(HOME, "Documents/Claude/Projects/Bravo Data Extraction")
PHOTOS = os.path.join(OS_DIR, "fleet/eod_photos")
STATE = os.path.join(OS_DIR, "fleet/state/jewelry_nightly")
TEST_OUT = os.path.join(OS_DIR, "fleet/test_output")
STATUS_MD = os.path.join(HOME, "Documents/Claude/Projects/Jewelry Count Reconciliation/STATUS.md")
ROSTER = os.path.join(OS_DIR, "hr/ROSTER.json")
CHANNEL = "C0BM9NHGTT4"            # #jewlery-counts
JOSHUA = "U03BB52MDSA"
CELL = "jewelry-case-counts-v3"
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
NAMES = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke", "WAY": "Waynesboro"}
CATS = ["Rings", "Bracelets", "Earrings", "Pendants", "Necklaces"]          # post order (10/13 live post)
BRAVO_MAP = {"Rings": ["Rings"], "Bracelets": ["Bracelets"], "Earrings": ["Earrings"],
             "Pendants": ["Pendants", "Charms", "Brooches"], "Necklaces": ["Chains", "Necklaces"]}
EMPTY_OK = ("Charms", "Brooches")
OVER_DM = 5
CACHE = True           # --no-cache re-reads every photo (render/testing)

sys.path.insert(0, BIN)


def log(*a):
    print(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), *a, flush=True)


# ---------------------------------------------------------------- STEP 0 — open stores (mirror of vp_lib.sh open_stores)
def open_stores(d):
    r = subprocess.run(["bash", "-c", '. "$1/vp_lib.sh" >/dev/null 2>&1; open_stores "$2"', "_", BIN, d.isoformat()],
                       capture_output=True, text=True, timeout=30)
    out = r.stdout.split()
    if r.returncode == 0 and (out or d.weekday() == 6):
        return [s for s in STORES if s in out]
    # fallback (sandbox / vp_lib unavailable): same calendar as vp_lib.sh
    if d.weekday() == 6:
        return []
    if d.weekday() == 2:
        iso = d.isoformat()
        return ["CUL"] if iso < "2026-09-30" else (["CUL", "ROA"] if iso < "2026-10-14" else ["CUL", "ROA", "WAY"])
    return list(STORES)


def close_time(store, d):
    if d.weekday() == 5:
        wed = d - dt.timedelta(days=3)
        if store in open_stores(wed):
            return dt.time(17, 0)
    return dt.time(18, 0)


def next_open(store, d):
    n = d + dt.timedelta(days=1)
    for _ in range(8):
        if store in open_stores(n):
            return n
        n += dt.timedelta(days=1)
    return n


def in_freeze(store, d, when):
    start = dt.datetime.combine(d, close_time(store, d))
    end = dt.datetime.combine(next_open(store, d), dt.time(10, 0))
    return start <= when < end


# ---------------------------------------------------------------- STEP 2/4 — Bravo
def csv_path(d, s):
    return os.path.join(BRAVO, "output", "%s_%s_jewelry-case-counts.csv" % (d.isoformat(), s))


def result_path(tid):
    return os.path.join(BRAVO, "results", tid + ".result.json")


def read_csv(p):
    rows = {}
    try:
        for i, line in enumerate(open(p, encoding="utf-8-sig")):
            if i == 0:
                continue
            f = line.strip().split(",")
            if len(f) >= 5:
                rows[f[1]] = (int(f[3]) if f[3].strip().isdigit() else None, f[4].strip())
    except OSError:
        return None
    return rows


def prior_csv(d, s):
    for p in sorted(glob.glob(os.path.join(BRAVO, "output", "*_%s_jewelry-case-counts.csv" % s)), reverse=True):
        m = re.match(r"(\d{4}-\d{2}-\d{2})_", os.path.basename(p))
        if m and m.group(1) < d.isoformat():
            return read_csv(p)
    return None


def expected(d, s, fresh_since=None):
    """-> (dict category->count, note) or (None, reason). Applies the EMPTY-CATEGORY RULE."""
    p = csv_path(d, s)
    if not os.path.exists(p):
        return None, "no CSV"
    mt = dt.datetime.fromtimestamp(os.path.getmtime(p))
    if not in_freeze(s, d, mt):
        return None, "CSV written %s, outside the freeze window" % mt.strftime("%m/%d %H:%M")
    if fresh_since and mt < fresh_since:
        return None, "CSV older than this run"
    rows = read_csv(p)
    if not rows or any(c not in rows for c in sum(BRAVO_MAP.values(), [])):
        return None, "CSV incomplete"
    prev = prior_csv(d, s) or {}
    raw, empties = {}, []
    for cat, (n, st) in rows.items():
        if st == "ok" and n is not None:
            raw[cat] = n
            continue
        pv = prev.get(cat)
        if cat in EMPTY_OK and pv is not None and (pv[1] != "ok" or pv[0] == 0):
            raw[cat] = 0
            empties.append(cat)
            continue
        return None, "%s %s (no prior-day empty baseline)" % (cat, st or "error")
    return {k: sum(raw[c] for c in v) for k, v in BRAVO_MAP.items()}, ("empty: " + "+".join(empties)) if empties else ""


def pull(d, s, retry=False):
    tid = "jewelry-onhand-%s-%s%s" % (d.isoformat(), s, "-retry" if retry else "")
    log("pull", s, tid)
    r = subprocess.run(["bash", os.path.join(BIN, "bravo_pull.sh"), CELL, d.isoformat(), s, tid],
                       capture_output=True, text=True, timeout=7800)
    log("bravo_pull rc=%s" % r.returncode, (r.stdout or "")[-400:].replace("\n", " | "))
    try:
        return json.load(open(result_path(tid), encoding="utf-8-sig")).get("status")
    except (OSError, ValueError):
        return None


# ---------------------------------------------------------------- STEP 5 — PM count sheets (vision)
SHEET_SYS = ("You read photos of a pawn shop's handwritten end-of-day paperwork. Report ONLY what is written. "
             "Never estimate, never fill in a number you cannot read with confidence. Answer with JSON only.")
SHEET_Q = """These photos were posted together by one employee in the #end-of-day channel on %(date)s.
One of them is usually the store's END OF DAY sheet with a printed header "END OF DAY: <STORE>". One may be the jewelry
count sheet (Bravo Store Systems form) with blocks of AM COUNT and PM COUNT, each listing RINGS, BRACELETS, NECKLACES,
EARRINGS, PENDANTS and TOTALS, under a handwritten DATE. Sheets stack several days per page; other photos (gun counts,
HG/LG boxes) are not the jewelry sheet.

Find the jewelry block whose handwritten DATE is %(mdy)s and read its PM COUNT column, digit by digit.
Return JSON only:
{"store_header": "<store name printed after END OF DAY:, or null>",
 "count_sheet_found": true|false,
 "date_block_found": true|false,
 "pm_block_date": "<the date written on the block you read, as written, or null>",
 "pm": {"rings": n|null, "bracelets": n|null, "necklaces": n|null, "earrings": n|null, "pendants": n|null, "totals": n|null},
 "all_digits_clear": true|false,
 "notes": "<at most 20 words: anything crossed out, smudged or ambiguous>"}
Use null for any value that is blank or that you cannot read with confidence. Output the JSON object only, no code fence,
and never put a double-quote character inside the notes text (write digits plainly: the 7 in rings)."""
PM_KEYS = ("rings", "bracelets", "earrings", "pendants", "necklaces")   # same order as CATS


def _img_block(path):
    tmp = None
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False).name
        r = subprocess.run(["sips", "-Z", "2000", "-s", "format", "jpeg", path, "--out", tmp],
                           capture_output=True, timeout=60)
        src = tmp if r.returncode == 0 and os.path.getsize(tmp) > 0 else path
    except (OSError, subprocess.SubprocessError):
        src = path
    data = base64.b64encode(open(src, "rb").read()).decode()
    if tmp and os.path.exists(tmp):
        os.unlink(tmp)
    mt = "image/png" if src.lower().endswith(".png") else "image/jpeg"
    return {"type": "image", "source": {"type": "base64", "media_type": mt, "data": data}}


def roster_store(uid):
    try:
        for e in json.load(open(ROSTER)).get("employees") or []:
            if e.get("slack_id") == uid:
                dep = (e.get("department") or "").lower()
                for s, n in NAMES.items():
                    if n.lower() == dep:
                        return s
    except (OSError, ValueError):
        pass
    return None


def _ask_sheet(d, folder, items, reverse=False):
    import vp_ai
    files = [it["file"] for it in items[:4]]
    if reverse:
        files = files[::-1]
    content = [_img_block(os.path.join(folder, f)) for f in files]
    content.append({"type": "text", "text": SHEET_Q % {"date": d.isoformat(), "mdy": "%d/%d/%d" % (d.month, d.day, d.year)}})
    err = None
    for _ in range(3):          # retries: an occasional malformed JSON answer (seen in the 10/12 + 10/13 replays)
        try:
            return vp_ai.ask_json("", SHEET_SYS, max_tokens=1500, content=content)
        except Exception as e:  # noqa: BLE001
            err = str(e)[:200]
    return {"error": err}


TOTAL_Q = """This is the same jewelry count sheet. Look ONLY at the handwritten TOTALS value in the PM COUNT column of the
block dated %(mdy)s. Its five PM category lines add up to %(sum)d. Handwritten digits can be ambiguous (5/8, 7/1, 4/9).
Is the written PM TOTALS value %(sum)d? Answer JSON only: {"total_is_sum": "yes"|"no"|"unclear", "written_total": "<as you read it>"}"""


def _confirm_total(d, folder, items, total):
    import vp_ai
    content = [_img_block(os.path.join(folder, it["file"])) for it in items[:4]]
    content.append({"type": "text", "text": TOTAL_Q % {"mdy": "%d/%d/%d" % (d.month, d.day, d.year), "sum": total}})
    err = None
    for _ in range(3):
        try:
            return vp_ai.ask_json("", SHEET_SYS, max_tokens=600, content=content)
        except Exception as e:  # noqa: BLE001
            err = str(e)[:200]
    return {"error": err}


def judge(ans):
    """-> (ok, short reason for the post line, plain reason for the manager)"""
    pm = ans.get("pm") or {}
    vals = [pm.get(k) for k in PM_KEYS]
    if ans.get("error"):
        return False, "count sheet not readable", None
    if not ans.get("count_sheet_found"):
        return False, "count sheet not posted tonight", "tonight's jewelry daily count sheet wasn't in your end-of-day photos"
    if not ans.get("date_block_found") or all(v is None for v in vals):
        return False, "count sheet not filled in", "the jewelry count sheet in your photos doesn't have a PM count filled in for tonight's date"
    if any(not isinstance(v, int) for v in vals) or not isinstance(pm.get("totals"), int) or not ans.get("all_digits_clear"):
        return False, "count sheet not readable", "part of tonight's PM jewelry count couldn't be read clearly from the photo"
    if sum(vals) != pm["totals"]:
        return False, "count sheet totals don't match", ("tonight's PM jewelry count doesn't add up — the categories come to %d "
                                                         "but the TOTALS line says %d" % (sum(vals), pm["totals"]))
    return True, "", None


def read_sheets(d, want=None, cache=True):
    """-> {store: {"pm": {cat: n, Total: n}, "ok": bool, "why": str, "mgr": str|None, "poster", "ts"}}.
    Each photo group is read TWICE (images in both orders); the two reads must agree exactly or the sheet is not used."""
    folder = os.path.join(PHOTOS, d.isoformat())
    try:
        idx = json.load(open(os.path.join(folder, "index.json")))
    except (OSError, ValueError):
        return {}
    os.makedirs(STATE, exist_ok=True)
    cpath = os.path.join(STATE, "sheets-%s.json" % d.isoformat())
    prev = {}
    if cache and os.path.exists(cpath):
        try:
            prev = json.load(open(cpath))
        except ValueError:
            prev = {}
    groups = {}
    for it in idx:
        if re.search(r"\.(jpe?g|png)$", it.get("file", ""), re.I):
            groups.setdefault((it.get("poster_id"), it.get("ts")), []).append(it)
    out = {}
    for (uid, ts), items in sorted(groups.items(), key=lambda g: g[0][1] or ""):
        key = "%s|%s|%d" % (uid, ts, len(items))
        guess = roster_store(uid)
        if want and guess and guess not in want and key not in prev:
            continue
        reads = [r for r in (prev.get(key) or []) if not r.get("error")]     # a failed call is retried, never trusted
        while len(reads) < 2:
            reads.append(_ask_sheet(d, folder, items, reverse=bool(reads)))
        store = None
        for a in reads:
            hdr = (a.get("store_header") or "").lower()
            for s, n in NAMES.items():
                if n.lower() in hdr:
                    store = store or s
        store = store or guess
        if not store or (want and store not in want):
            prev[key] = reads
            json.dump(prev, open(cpath, "w"), indent=1)
            continue
        # ACCEPTANCE (never guess): two independent reads (images in different orders) must agree on all five PM
        # categories. If the first two disagree, one tie-break read. Then the written TOTALS must equal their sum —
        # read the same by both, or confirmed by one focused look at the TOTALS line only (the SKILL's
        # "disambiguate via total-minus-other-categories"). A clear "no" = the sheet does not add up.
        cats = lambda a: tuple((a.get("pm") or {}).get(k) for k in PM_KEYS) if not a.get("error") else None   # noqa: E731
        def pair(rs):
            for x in range(len(rs)):
                for y in range(x + 1, len(rs)):
                    cx = cats(rs[x])
                    if cx and all(isinstance(v, int) for v in cx) and cx == cats(rs[y]) \
                            and rs[x].get("date_block_found") is not False and rs[y].get("date_block_found") is not False:
                        return rs[x], rs[y]
            return None
        pr = pair(reads)
        if not pr and len(reads) < 3:
            reads.append(_ask_sheet(d, folder, items))
            pr = pair(reads)
        prev[key] = reads
        json.dump(prev, open(cpath, "w"), indent=1)
        a1 = reads[0]
        if not pr:
            ok, why, mgr = judge(a1)
            if ok or any(all(isinstance(v, int) for v in (cats(r) or (None,))) for r in reads):
                ok, why, mgr = False, "count sheet not readable", "part of tonight's PM jewelry count couldn't be read clearly from the photo"
            vals = cats(a1) or (None,) * 5
            total = (a1.get("pm") or {}).get("totals")
        else:
            a1, a2 = pr
            vals = cats(a1)
            tot = sum(vals)
            ok, why, mgr = True, "", None
            if not (a1["pm"].get("totals") == tot and a2["pm"].get("totals") == tot):
                ck = key + "|total"
                if ck not in prev or prev[ck].get("error"):     # an API/parse error is never cached as an answer
                    prev[ck] = _confirm_total(d, folder, items, tot)
                    json.dump(prev, open(cpath, "w"), indent=1)
                ans = (prev[ck].get("total_is_sum") or "").lower()
                if ans == "yes":
                    a1 = dict(a1, notes=(a1.get("notes") or "") + " | TOTALS confirmed = %d on a focused re-read" % tot)
                elif ans == "no":
                    wt = prev[ck].get("written_total") or a1["pm"].get("totals")
                    ok, why, mgr = False, "count sheet totals don't match", (
                        "tonight's PM jewelry count doesn't add up — the categories come to %d but the TOTALS line says %s" % (tot, wt))
                else:
                    ok, why, mgr = False, "count sheet not readable", "the TOTALS line on tonight's PM jewelry count couldn't be read clearly from the photo"
            total = tot if ok else a1["pm"].get("totals")
        pm = dict(zip(PM_KEYS, vals), totals=total)
        rec = {"pm": dict(zip(CATS, [pm.get(k) for k in PM_KEYS]), Total=pm.get("totals")), "ok": ok, "why": why, "mgr": mgr,
               "poster": items[0].get("poster"), "ts": ts, "notes": a1.get("notes", ""), "block_date": a1.get("pm_block_date")}
        # the latest READABLE sheet for a store wins; a later group that is not the count sheet (e.g. a gun-count
        # photo posted separately) never replaces a readable one
        if store not in out or ok or (not out[store]["ok"] and why != "count sheet not posted tonight"):
            out[store] = rec
    return out


# ---------------------------------------------------------------- STEP 6 — message
MANAGERS = {"CUL": ("U04C5DL5EKH", "Sandi"), "HAR": ("U09UTFT4P7X", "Walker"), "LEX": ("U09H9ES2LKA", "Uriah"),
            "ROA": ("U0631AECK4K", "Benjie"), "WAY": ("U04U136MF6V", "Chadd")}   # PARTIAL-POST RULE list (SKILL 2026-09-22)


def fmt_var(v):
    return "+%d" % v if v > 0 else str(v)


def heading(d, catchup=False, only=None):
    wd, md = d.strftime("%A"), "%d/%d" % (d.month, d.day)
    if catchup:
        return ("Jewelry Count — %s %s CATCH-UP (expected = Bravo pulled this morning inside freeze window; "
                "counted = last night's PM sheet)" % (wd, md))
    if only:
        return "Jewelry Count — %s %s — %s (expected = system on-hand, counted = PM count sheet)" % (
            wd, md, ", ".join(NAMES[s] for s in only))
    return "Jewelry Count — %s %s (expected = system on-hand, counted = PM count sheet)" % (wd, md)


def build(d, stores, exp, sheets, catchup=False, only=None):
    rows, left, overs = [], [], []
    for s in stores:
        sh = sheets.get(s)
        if not sh or not sh["ok"]:
            left.append((s, sh["why"] if sh else "count sheet not posted tonight"))
            continue
        e = exp[s]
        te = tc = 0
        for c in CATS:
            v = sh["pm"][c] - e[c]
            rows.append("| %s | %s | %d | %d | %s |" % (s, c, e[c], sh["pm"][c], fmt_var(v)))
            te += e[c]
            tc += sh["pm"][c]
            if v > OVER_DM:
                overs.append("%s %s %s" % (NAMES[s], c, fmt_var(v)))
        rows.append("| **%s Total** | | **%d** | **%d** | **%s** |" % (s, te, tc, fmt_var(tc - te)))
        if tc - te > OVER_DM:
            overs.append("%s total %s" % (NAMES[s], fmt_var(tc - te)))
    lines = [heading(d, catchup, only), ""]
    if rows:
        lines += ["| Store | Category | Expected | Counted | Variance |", "|---|---|---|---|---|"] + rows
    if left:
        lines.append("")
        lines += ["%s — %s." % (NAMES[s], why) for s, why in left]
    return "\n".join(lines).strip() + "\n", left, overs


# ---------------------------------------------------------------- helpers
def slack(*a):
    return subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py")] + list(a),
                          capture_output=True, text=True, timeout=120)


def already_posted(d, hours=40):
    marker = "Jewelry Count — %s %d/%d" % (d.strftime("%A"), d.month, d.day)
    return slack("has", CHANNEL, marker, str(hours)).returncode == 0


def append(path, text):
    try:
        with open(path, "a") as f:
            f.write(text)
    except OSError:
        pass


def ledger(line, task="jewelry-onhand-nightly-pull"):
    subprocess.run(["bash", "-c", 'AGENT="$3"; . "$1/vp_lib.sh" >/dev/null 2>&1; ledger "$3" "$2" no', "_", BIN, line, task],
                   capture_output=True, timeout=30)


def fetch_photos(d):
    subprocess.run(["/usr/bin/python3", os.path.join(BIN, "eod_photo_fetch.py"), d.isoformat()],
                   capture_output=True, text=True, timeout=300)


def run(d, mode, send, do_pull=True, render=False, wait_min=30):
    task = "jewelry-onhand-catchup" if mode == "catchup" else "jewelry-onhand-nightly-pull"
    catchup = mode == "catchup"
    stores = open_stores(d)
    if not stores:
        log("open-stores gate: nobody open on %s — no-op" % d)
        return 0
    now = dt.datetime.now()
    live = send and not render
    if live and already_posted(d):
        log("already posted for %s — no-op" % d)
        return 0
    if catchup and live:
        # catch-up STEP 0: the nightly worked if every open store already has a freeze-window CSV; never start after 9:30
        if all(expected(d, s)[0] is not None for s in stores) and already_posted(d):
            return 0
        if now.time() > dt.time(9, 30):
            log("catch-up: past 9:30 — not starting a pull")
            do_pull = False
    exp, why = {}, {}
    for s in stores:
        e, note = expected(d, s)
        if e is None and do_pull and not render:
            if not in_freeze(s, d, dt.datetime.now()):
                why[s] = "outside the freeze window, not pulled (%s)" % note
                continue
            st = pull_catchup(d, s) if catchup else pull(d, s)
            e, note = expected(d, s)
            if e is None and st != "success" and not catchup:
                pull(d, s, retry=True)
                e, note = expected(d, s)
        if e is None:
            why[s] = note
        else:
            exp[s] = e
            if note:
                log(s, note)
    if why:   # STEP 4: the BRAVO side failed for an open store -> hold everything (PARTIAL-POST RULE item 4)
        notes = "Bravo incomplete: " + "; ".join("%s (%s)" % (k, v) for k, v in why.items())
        log(notes)
        if live:
            ledger(("Last night's" if catchup else "Tonight's") + " jewelry count for %s was not posted — the Bravo on-hand pull "
                   "did not complete for %s." % (d.strftime("%a %-m/%-d"), ", ".join(NAMES[k] for k in why)), task)
            append(status_path(catchup), "\n## RUN RECORD — %s (%s) — native %s\n\nNothing posted. %s\n" % (d, d.strftime("%A"), task, notes))
        return 1
    if live:
        fetch_photos(d)          # pick up any sheet posted after the 20:15 download (overwrites nothing)
    sheets = read_sheets(d, cache=CACHE)
    if live and not catchup and any(not (sheets.get(s) or {}).get("ok") for s in stores) and wait_min:
        # STEP 5: a sheet not posted yet -> wait 30 min once, re-download #end-of-day, read again
        log("waiting %d min once for: %s" % (wait_min, ", ".join(s for s in stores if not (sheets.get(s) or {}).get("ok"))))
        import time
        time.sleep(wait_min * 60)
        fetch_photos(d)
        sheets = read_sheets(d)
    text, left, overs = build(d, stores, exp, sheets, catchup=catchup)
    notes = "Open: %s. Bravo freeze-window CSVs: all open stores. Sheets: %s." % (" ".join(stores), "; ".join(
        "%s %s" % (k, "ok (%s, %s)" % (v["poster"], (v["ts"] or "")[11:16]) if v["ok"] else "NOT USED — " + v["why"])
        for k, v in sorted(sheets.items()) if k in stores) or "none")
    log(notes)
    if not live:
        os.makedirs(TEST_OUT, exist_ok=True)
        p = os.path.join(TEST_OUT, "%s-%s.txt" % (task, d.isoformat()))
        open(p, "w").write("(would post to #jewlery-counts C0BM9NHGTT4)\n" + text)
        print(text)
        if left:
            print("manager DMs that would go out:", ", ".join(MANAGERS[s][1] for s, _ in left if _reportable_uid(MANAGERS[s][0])))
        return 0
    if len(left) == len(stores):
        # no store has a usable sheet: nothing to compare. The post would be only "not posted" lines.
        log("no usable sheet for any open store")
    os.makedirs(STATE, exist_ok=True)
    tmp = os.path.join(STATE, "post-%s%s.txt" % (d.isoformat(), "-catchup" if catchup else ""))
    open(tmp, "w").write(text)
    r = slack("post", CHANNEL, "--file", tmp)
    if r.returncode != 0:
        ledger("The jewelry count for %s could not be posted to #jewlery-counts." % d.strftime("%a %-m/%-d"), task)
        return 1
    log("posted", r.stdout.strip())
    for s, _ in left:   # PARTIAL-POST RULE item 2 — the store's manager gets the specific problem
        sh = sheets.get(s)
        problem = (sh or {}).get("mgr") or "tonight's jewelry daily count sheet wasn't in your end-of-day photos"
        uid, first = MANAGERS[s]
        if not _reportable_uid(uid):   # fleet-wide rule 2026-10-21 (vp_people): current, non-Davis staff only
            log("manager DM for %s skipped: %s is not a current non-Davis employee on hr/ROSTER.json" % (s, uid))
            continue
        msg = ("Hey %s — %s (%s). Tonight's company jewelry count post went out without %s. Can you post a clear photo "
               "of tonight's Jewelry Daily Count sheet when you get a chance?" % (first, problem, d.strftime("%-m/%-d"), NAMES[s]))
        _dm(uid, msg)
    if overs or left:
        bits = []
        if left:
            bits.append("left out: " + ", ".join("%s (%s)" % (NAMES[s], w) for s, w in left))
        if overs:
            bits.append("counted more than the system shows: " + ", ".join(overs))
        _dm(JOSHUA, "Jewelry count %s — %s." % (d.strftime("%-m/%-d"), "; ".join(bits)))
    append(status_path(catchup), "\n## RUN RECORD — %s (%s) — native %s\n\n%s\n\n%s\n" % (d, d.strftime("%A"), task, notes, text))
    return 0


def _reportable_uid(uid):
    """True only if this Slack id is a current (Gusto active), non-Davis employee per bin/vp_people.py."""
    try:
        sys.path.insert(0, BIN)
        import vp_people
        for e in vp_people.current_staff():
            if e.get("slack_id") == uid:
                return vp_people.is_reportable(e.get("name"))
    except Exception as e:   # RosterHold / unreadable roster = do not message anyone by name
        log("roster check failed (%s)" % e)
    return False


def _dm(uid, text):
    """DM one user through the ops bot (vp_slack's own dm_channel + post, so receipts/dry-run apply)."""
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import vp_slack as v; v.post(v.dm_channel(sys.argv[2]), sys.argv[3])")
    return subprocess.run(["/usr/bin/python3", "-c", code, BIN, uid, text], capture_output=True, text=True, timeout=120)


def status_path(catchup):
    return os.path.join(BRAVO, "STATUS.md") if catchup else STATUS_MD


def pull_catchup(d, s):
    tid = "jewelry-onhand-%s-catchup-%s" % (d.isoformat(), s)
    log("pull", s, tid)
    r = subprocess.run(["bash", os.path.join(BIN, "bravo_pull.sh"), CELL, d.isoformat(), s, tid],
                       capture_output=True, text=True, timeout=7800)
    log("bravo_pull rc=%s" % r.returncode, (r.stdout or "")[-400:].replace("\n", " | "))
    try:
        return json.load(open(result_path(tid), encoding="utf-8-sig")).get("status")
    except (OSError, ValueError):
        return None


def followup(d, stores, send):
    """One extra post for store(s) a run left out on the Bravo side (e.g. 10/14 Waynesboro, skipped by the cloud copy's
    old Wednesday gate). No pull here: the store's freeze-window CSV must already exist. Same table format."""
    exp, why = {}, {}
    for s in stores:
        e, note = expected(d, s)
        (exp.__setitem__(s, e) if e is not None else why.__setitem__(s, note))
    if why:
        log("follow-up refused — Bravo not complete: %s" % why)
        return 1
    if send:
        fetch_photos(d)
    sheets = read_sheets(d, want=stores, cache=CACHE)
    text, left, overs = build(d, stores, exp, sheets, only=stores)
    log("sheets:", json.dumps({k: (v["pm"] if v["ok"] else v["why"]) for k, v in sheets.items()}))
    print(text)
    if not send:
        return 0
    os.makedirs(STATE, exist_ok=True)
    tmp = os.path.join(STATE, "followup-%s-%s.txt" % (d.isoformat(), "-".join(stores)))
    open(tmp, "w").write(text)
    r = slack("post", CHANNEL, "--file", tmp)
    log("follow-up post rc=%s %s %s" % (r.returncode, r.stdout.strip(), r.stderr.strip()[-200:]))
    if r.returncode == 0:
        append(STATUS_MD, "\n## RUN RECORD — %s (%s) — follow-up post for %s (native jewelry_nightly.py)\n\n%s\n" % (
            d, d.strftime("%A"), ", ".join(NAMES[s] for s in stores), text))
    return r.returncode


def main(a):
    global CACHE
    d = None
    if "--date" in a:
        d = dt.date.fromisoformat(a[a.index("--date") + 1])
    render = "--render" in a
    mode = "catchup" if ("catchup" in a or "--catchup" in a) else ("sheets" if "sheets" in a else "nightly")
    if d is None:
        today = dt.date.today()
        if mode == "catchup" or dt.datetime.now().hour < 10:
            d = today - dt.timedelta(days=1)          # catch-up = YESTERDAY (Sunday yesterday -> gate no-op)
        else:
            d = today
    if "followup" in a:
        CACHE = "--no-cache" not in a
        return followup(d, a[a.index("--stores") + 1].split(","), "--send" in a)
    if mode == "sheets":
        want = a[a.index("--stores") + 1].split(",") if "--stores" in a else None
        print(json.dumps(read_sheets(d, want, cache="--no-cache" not in a), indent=1))
        return 0
    CACHE = "--no-cache" not in a
    wait = int(a[a.index("--wait") + 1]) if "--wait" in a else 30
    return run(d, mode, "--send" in a, do_pull="--no-pull" not in a, render=render, wait_min=wait)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
