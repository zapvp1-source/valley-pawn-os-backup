#!/usr/bin/env python3
"""chekkit_tags.py — Bravo customer facts -> Chekkit customer tags (comms review build #4, 2026-10-23).

WHY: every Chekkit text blast goes to the whole contact list, including people who have not been in for years.
Those are the people who reply STOP, and opt-outs are over the carrier line at 4 of 5 stores (ROA 14%). With
these tags a campaign can be aimed at real, recent customers instead of everyone. Tags only describe; nothing
here sends, filters or blocks anything.

Tags (all start with "bravo-"; this script never adds, removes or reads any other tag):
  bravo-visited-60d   in the newest weekly Bravo "contacts, last time in within 60 days" pull (forfeiture-winback
                      agent, Sundays) — only used while that pull is under 15 days old
  bravo-customer-2yr  in the newest full Bravo customer directory (last time in within ~2 years; refreshed every
                      84 days by the same agent)
  bravo-borrower      Bravo "Total Loans" above $0
  bravo-do-not-text   Bravo's SMS column says DNT (the customer asked the store not to text them)
  bravo-winback       in the newest forfeiture win-back list (forfeited a loan, has not been back) under 15 days old
A tag that no longer applies (e.g. 60 days passed) is removed from that customer on the next run.

API (per store token, 60 req/min): GET /v1/customers?phone= (lookup only) and PATCH /v1/customers/{id}
{addTags, removeTags}. NEVER POST: a Bravo customer who is not already in Chekkit is not created (that would
grow the blast list). Not-found phones are re-checked every 28 days.

  chekkit_tags.py sync [--render] [--store CODE] [--max-minutes N]   (default 50 min, stores run in parallel)
  chekkit_tags.py summary                                            counts from the state files
  chekkit_tags.py verify                                             read back 3 tagged customers per store
  chekkit_tags.py probe                                              read-only API shape check
State fleet/state/chekkit_tags/<CODE>.json, summary fleet/state/chekkit_tags/summary.json. Logs: counts only,
never names or numbers. Failure policy v3: one FAILURE_LEDGER row a day, never a ping.
"""
import csv, datetime as dt, glob, json, os, re, sys, threading, time, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chekkit_ops as co  # noqa: E402

OS_DIR = os.path.dirname(HERE)
PROJ = os.path.dirname(OS_DIR)
BRAVO_OUT = os.path.join(PROJ, "Bravo Data Extraction", "output")
FWB_RUNS = os.path.join(PROJ, "Email Refinement", "forfeiture_winback", "runs")
STATE = os.path.join(OS_DIR, "fleet", "state", "chekkit_tags")
PREFIX = "bravo-"
T60, T2Y, TBOR, TDNT, TWB = "bravo-visited-60d", "bravo-customer-2yr", "bravo-borrower", "bravo-do-not-text", "bravo-winback"
FRESH_DAYS = 15
RECHECK_MISS_DAYS = 28
GAP = 1.1          # seconds between calls on one token (60/min limit)
TODAY = dt.date.today()


def phone10(p):
    d = re.sub(r"\D", "", p or "")
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    return d if len(d) == 10 and d[0] not in "01" else ""


def money(v):
    try:
        return float(re.sub(r"[^\d.\-]", "", v or "") or 0)
    except ValueError:
        return 0.0


def fdate(path):
    try:
        return dt.date.fromisoformat(os.path.basename(path)[:10])
    except ValueError:
        return None


def rows(path):
    with open(path, newline="", errors="replace") as f:
        return list(csv.DictReader(f))


def sources(code):
    """(desired: phone -> set(tags), notes: dict) for one store, from files already on disk."""
    files = sorted(glob.glob(os.path.join(BRAVO_OUT, "*_%s_forfeiture-winback-comparison-contacts.csv" % code)), key=fdate)
    files = [f for f in files if fdate(f)]
    full = [f for f in files if (TODAY - fdate(f)).days > 365]
    d60 = [f for f in files if (TODAY - fdate(f)).days <= 365]
    notes = {"full": None, "d60": None, "winback": None}
    want, dnt = {}, {}
    if full and len(rows(full[-1])) >= 500:
        notes["full"] = os.path.basename(full[-1])
        for r in rows(full[-1]):
            p = phone10(r.get("Phone"))
            if p:
                s = want.setdefault(p, set()); s.add(T2Y)
                if money(r.get("Total Loans")) > 0:
                    s.add(TBOR)
                dnt[p] = (r.get("SMS") or "").strip().upper() == "DNT"
    # the 60-day file is named RUN-60; the run that wrote it is 60 days after its file date
    if d60 and (TODAY - (fdate(d60[-1]) + dt.timedelta(days=60))).days <= FRESH_DAYS:
        notes["d60"] = os.path.basename(d60[-1])
        for r in rows(d60[-1]):
            p = phone10(r.get("Phone"))
            if p:
                s = want.setdefault(p, set()); s.update({T60, T2Y})
                if money(r.get("Total Loans")) > 0:
                    s.add(TBOR)
                dnt[p] = (r.get("SMS") or "").strip().upper() == "DNT"   # newer file wins
    for p, flag in dnt.items():
        if flag:
            want[p].add(TDNT)
    runs = sorted(d for d in glob.glob(os.path.join(FWB_RUNS, "20??-??-??")) if os.path.isdir(d))
    if runs and (TODAY - dt.date.fromisoformat(os.path.basename(runs[-1]))).days <= FRESH_DAYS:
        f = os.path.join(runs[-1], "chekkit_%s.csv" % co.NAMES[code])
        if os.path.exists(f):
            notes["winback"] = os.path.basename(runs[-1])
            for r in rows(f):
                p = phone10(r.get("Phone"))
                if p:
                    want.setdefault(p, set()).add(TWB)
    return want, notes


def load_state(code):
    return co.load(os.path.join(STATE, "%s.json" % code), {"customers": {}, "miss": {}})


def save_state(code, st):
    co.save(os.path.join(STATE, "%s.json" % code), st)


class Gate:
    def __init__(self):
        self.t = 0.0

    def wait(self):
        d = self.t + GAP - time.time()
        if d > 0:
            time.sleep(d)
        self.t = time.time()


def sync_store(code, render, deadline, out):
    want, notes = sources(code)
    st = load_state(code)
    res = {"desired": len(want), "notes": notes, "looked_up": 0, "not_in_chekkit": 0, "patched": 0, "unchanged": 0,
           "errors": 0, "done": True, "by_tag": {}}
    if not notes["full"] and not notes["d60"]:
        res["done"] = False; res["error"] = "no Bravo customer file on disk"; out[code] = res; return
    for s in want.values():
        for t in s:
            res["by_tag"][t] = res["by_tag"].get(t, 0) + 1
    if render:
        out[code] = res; return
    custs, miss = st["customers"], st["miss"]
    # phones to visit: everyone wanted + everyone we tagged before (their tags may need removing)
    todo = list(want.keys()) + [p for p, c in custs.items() if c.get("tags") and p not in want]
    # cheapest first: already-known customers whose tags did not change are skipped without a call
    gate, n = Gate(), 0
    for p in todo:
        desired = sorted(want.get(p, set()))
        known = custs.get(p)
        if known and sorted(known.get("tags", [])) == desired:
            res["unchanged"] += 1; continue
        m = miss.get(p)
        if not known and m and (TODAY - dt.date.fromisoformat(m)).days < RECHECK_MISS_DAYS:
            continue
        if time.time() > deadline:
            res["done"] = False; break
        try:
            gate.wait()
            b = co.req(code, "GET", "/v1/customers?phone=" + urllib.parse.quote(p)); res["looked_up"] += 1
            cl = b.get("customers") or []
            if not cl:
                miss[p] = TODAY.isoformat(); custs.pop(p, None); res["not_in_chekkit"] += 1
            else:
                c = cl[0]
                have = sorted(t for t in (c.get("tags") or []) if str(t).startswith(PREFIX))
                add = [t for t in desired if t not in have]
                rem = [t for t in have if t not in desired]
                if add or rem:
                    gate.wait()
                    body = {}
                    if add:
                        body["addTags"] = add
                    if rem:
                        body["removeTags"] = rem
                    co.req(code, "PATCH", "/v1/customers/%s" % c["id"], body); res["patched"] += 1
                else:
                    res["unchanged"] += 1
                miss.pop(p, None)
                if desired:
                    custs[p] = {"id": c["id"], "tags": desired, "at": TODAY.isoformat()}
                else:
                    custs.pop(p, None)
        except Exception as e:  # noqa: BLE001
            res["errors"] += 1; res["last_error"] = str(e)[:160]
            if res["errors"] >= 25:
                res["done"] = False; break
        n += 1
        if n % 50 == 0:
            save_state(code, st)
    save_state(code, st)
    tagged = {}
    for c in custs.values():
        for t in c.get("tags", []):
            tagged[t] = tagged.get(t, 0) + 1
    res["tagged_in_chekkit"] = tagged
    res["customers_tagged"] = len(custs)
    out[code] = res


def sync(a):
    render = "--render" in a
    stores = [a[a.index("--store") + 1].upper()] if "--store" in a else co.STORES
    mins = float(a[a.index("--max-minutes") + 1]) if "--max-minutes" in a else 50.0
    deadline = time.time() + mins * 60
    out, th = {}, []
    for code in stores:
        t = threading.Thread(target=sync_store, args=(code, render, deadline, out), daemon=True)
        t.start(); th.append(t)
    for t in th:
        t.join(mins * 60 + 300)
    summ = {"run_at": co.now_et().isoformat(timespec="seconds"), "render": render, "stores": out}
    if not render:
        co.save(os.path.join(STATE, "summary.json"), summ)
    for code in stores:
        r = out.get(code, {"error": "did not finish"})
        print(code, json.dumps({k: v for k, v in r.items() if k != "notes"}))
        print("   sources:", r.get("notes"))
    bad = [c for c in stores if out.get(c, {}).get("error") or out.get(c, {}).get("errors", 0) >= 25]
    if bad and not render:
        co.ledger_once("chekkit-customer-tags", "Chekkit customer tags were not updated for %s." % ", ".join(co.NAMES[c] for c in bad))
    return 0


def summary():
    for code in co.STORES:
        st = load_state(code)
        tagged = {}
        for c in st["customers"].values():
            for t in c.get("tags", []):
                tagged[t] = tagged.get(t, 0) + 1
        print(code, "tagged:", len(st["customers"]), tagged, "not in Chekkit:", len(st["miss"]))
    return 0


def verify(n=3):
    """Read back a few customers this script tagged and confirm Chekkit holds exactly those bravo- tags."""
    ok = bad = 0
    for code in co.STORES:
        st = load_state(code)
        for p, c in list(st["customers"].items())[-n:]:
            r = co.req(code, "GET", "/v1/customers/%s" % c["id"])
            cu = r.get("customer") or r
            have = sorted(t for t in (cu.get("tags") or []) if str(t).startswith(PREFIX))
            if have == sorted(c["tags"]):
                ok += 1
            else:
                bad += 1
            time.sleep(GAP)
    print("VERIFY ok=%d mismatch=%d" % (ok, bad))
    return 0 if not bad else 1


def probe():
    code = "CUL"
    b = co.req(code, "GET", "/v1/conversations?limit=1")
    ph = ((b.get("conversations") or [{}])[0].get("customer") or {}).get("phone") or ""
    r = co.req(code, "GET", "/v1/customers?phone=" + urllib.parse.quote(ph))
    c = (r.get("customers") or [{}])[0]
    print("customer keys:", sorted(c.keys()), "tag count:", len(c.get("tags") or []))
    return 0


def main(a):
    if not a:
        print(__doc__); return 2
    if a[0] == "sync":
        return sync(a[1:])
    if a[0] == "verify":
        return verify()
    if a[0] == "summary":
        return summary()
    if a[0] == "probe":
        return probe()
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]) or 0)
