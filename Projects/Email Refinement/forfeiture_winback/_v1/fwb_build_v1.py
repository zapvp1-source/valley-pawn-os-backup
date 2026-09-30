#!/usr/bin/env python3
"""
Forfeited-Loan Win-Back — weekly audience builder (stdlib only).

Inputs (Bravo pipeline output, one set per store, written by the
forfeiture-winback / forfeiture-winback-comparison cells):
  {RUN}_{STORE}_forfeiture-winback.csv                 Loans/Buys "Claude Forfeiture Winback"
                                                       (EXPIRED tickets: Customer, Pull Date, SMS ...)
  {RUN-7}_{STORE}_forfeiture-winback-comparison.csv    Customers "...Comparison", Last Time In > RUN-7
                                                       -> who has been in THIS WEEK (returners)
  {RUN-60}_{STORE}_forfeiture-winback-comparison.csv   Last Time In > RUN-60
                                                       -> contact source (Name/Phone/E-Mail) for
                                                          recent forfeits + returners for old forfeits
  optional {DIR}_{STORE}_forfeiture-winback-comparison.csv  one-time directory (old date) for backfill contacts

Joshua's rule (2026-09-29): a forfeiter has "come back" if their name shows on
the Comparison report for a date after their forfeit. We keep a state file so
every weekly run adds to each customer's history — once seen back, they're out.

Outputs (in this folder):
  state.json                          durable per-customer history
  runs/{RUN}/audience.csv             Brevo import rows (email present, not returned, not unsub)
  runs/{RUN}/new_this_week.csv        subset: first-time forfeits -> Month-1 email
  runs/{RUN}/report.md                counts per store + data-completeness gate
Exit code 2 = a store's data failed the completeness gate (do not import/send).
"""
import csv, json, os, re, sys, datetime as dt
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("FWB_OUT") or os.path.normpath(os.path.join(HERE, "..", "..", "Bravo Data Extraction", "output"))
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
MIN_CAPTURE = 0.98  # grid capture ratio required per file (Rule 18)


def norm_tokens(name):
    s = re.sub(r"[^A-Z ]", " ", (name or "").upper())
    toks = [t for t in s.split() if t not in ("JR", "SR", "II", "III", "IV")]
    return toks


def key_full(name):
    return " ".join(sorted(norm_tokens(name)))


def key_fl(name):
    t = norm_tokens(name)
    if len(t) < 2:
        return None
    return " ".join(sorted([t[0], t[-1]]))


def pdate(s):
    try:
        return dt.datetime.strptime(s.strip(), "%m/%d/%Y").date()
    except Exception:
        return None


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def capture_ok(path):
    meta = path + ".meta"
    if not os.path.exists(meta):
        return True, None
    kv = dict(l.strip().split("=", 1) for l in open(meta) if "=" in l)
    exp, cap = int(kv.get("expected", 0)), int(kv.get("captured", 0))
    if exp == 0:
        return True, (0, 0)
    return cap / exp >= MIN_CAPTURE, (cap, exp)


class Directory:
    """name -> contact, built from Comparison CSVs. Ambiguous names dropped."""
    def __init__(self):
        self.full = defaultdict(list)
        self.fl = defaultdict(list)

    def add_rows(self, rows):
        for r in rows:
            c = {"name": r.get("Name", "").strip(), "phone": r.get("Phone", "").strip(),
                 "email": r.get("E-Mail", "").strip().lower()}
            k = key_full(c["name"])
            if k:
                self.full[k].append(c)
            k2 = key_fl(c["name"])
            if k2:
                self.fl[k2].append(c)

    def names(self):
        return set(self.full.keys())

    def lookup(self, name):
        for idx, k in ((self.full, key_full(name)), (self.fl, key_fl(name))):
            if not k or k not in idx:
                continue
            cands = idx[k]
            emails = {c["email"] for c in cands if c["email"]}
            phones = {c["phone"] for c in cands if c["phone"]}
            if len(emails) <= 1 and len(phones) <= 1:
                c = dict(cands[0])
                c["email"] = next(iter(emails), "")
                c["phone"] = next(iter(phones), "")
                return c, "exact" if idx is self.full else "first-last"
            return None, "ambiguous"
        return None, "none"


def valid_email(e):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", e or "")) and not e.endswith((".fa", ".con", ".cm"))


def main():
    run = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today()
    dir_date = sys.argv[2] if len(sys.argv) > 2 else None  # optional one-time directory date
    d7, d60 = run - dt.timedelta(days=7), run - dt.timedelta(days=60)
    state_path = os.path.join(HERE, "state.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {"customers": {}, "runs": []}
    first_run = not state["runs"]
    rundir = os.path.join(HERE, "runs", run.isoformat())
    os.makedirs(rundir, exist_ok=True)

    lines = [f"# Forfeiture win-back build {run}", ""]
    gate_fail = []
    for st in STORES:
        f_loans = os.path.join(OUT, f"{run}_{st}_forfeiture-winback.csv")
        f_ret = os.path.join(OUT, f"{d7}_{st}_forfeiture-winback-comparison.csv")
        f_con = os.path.join(OUT, f"{d60}_{st}_forfeiture-winback-comparison.csv")
        f_dir = os.path.join(OUT, f"{dir_date}_{st}_forfeiture-winback-comparison.csv") if dir_date else None
        missing = [p for p in (f_loans, f_ret, f_con) if not os.path.exists(p)]
        if missing:
            gate_fail.append(st)
            lines.append(f"- {st}: MISSING {', '.join(os.path.basename(m) for m in missing)} -> store skipped")
            continue
        bad = []
        for p in (f_loans, f_ret, f_con):
            ok, cc = capture_ok(p)
            if not ok:
                bad.append(f"{os.path.basename(p)} {cc[0]}/{cc[1]}")
        if bad:
            gate_fail.append(st)
            lines.append(f"- {st}: INCOMPLETE capture ({'; '.join(bad)}) -> store skipped")
            continue

        loans = read_csv(f_loans)
        ret = Directory(); ret.add_rows(read_csv(f_ret))
        con = Directory(); con.add_rows(read_csv(f_con))
        contacts = Directory(); contacts.add_rows(read_csv(f_con)); contacts.add_rows(read_csv(f_ret))
        if f_dir and os.path.exists(f_dir):
            contacts.add_rows(read_csv(f_dir))

        # forfeits per customer (latest pull date)
        per = {}
        for r in loans:
            if r.get("Disposition", "").upper() not in ("EXPIRED", "FORFEITED"):
                continue
            nm = r.get("Customer", "").strip()
            k = key_full(nm)
            if not k:
                continue
            f = pdate(r.get("Pull Date", "")) or pdate(r.get("Disposition Date", ""))
            if not f:
                continue
            p = per.setdefault(k, {"name": nm, "first": f, "last": f, "dnt": False})
            p["first"], p["last"] = min(p["first"], f), max(p["last"], f)
            if r.get("SMS", "").upper() == "DNT":
                p["dnt"] = True

        newc = back = 0
        for k, p in per.items():
            ck = f"{st}|{k}"
            c = state["customers"].get(ck)
            if c is None:
                c = state["customers"][ck] = {"store": st, "name": p["name"], "first_forfeit": p["first"].isoformat(),
                                              "last_forfeit": p["last"].isoformat(), "returned_on": None,
                                              "email": "", "phone": "", "sms_dnt": p["dnt"], "match": "",
                                              "added": run.isoformat(), "touches": []}
                newc += 1
            else:
                if p["last"].isoformat() > c["last_forfeit"]:
                    c["last_forfeit"] = p["last"].isoformat()
                    c["returned_on"] = None  # a new forfeit restarts the clock
                c["sms_dnt"] = c["sms_dnt"] or p["dnt"]
            if not c["email"]:
                hit, how = contacts.lookup(c["name"])
                c["match"] = how
                if hit:
                    c["email"], c["phone"] = hit["email"], hit["phone"]

        # returned? name on Comparison for a date after the forfeit
        for ck, c in state["customers"].items():
            if c["store"] != st or c["returned_on"]:
                continue
            lf = dt.date.fromisoformat(c["last_forfeit"])
            k = key_full(c["name"])
            if lf < d60 and k in con.names():
                c["returned_on"] = f"between {d60} and {run}"
            elif lf < d7 and k in ret.names():
                c["returned_on"] = f"between {d7} and {run}"
            if c["returned_on"]:
                back += 1

        pool = [c for c in state["customers"].values() if c["store"] == st]
        tgt = [c for c in pool if not c["returned_on"] and valid_email(c["email"])]
        lines.append(f"- {st}: forfeiters in report {len(per)} (new to program {newc}) | returned {sum(1 for c in pool if c['returned_on'])}"
                     f" (+{back} this run) | emailable not-returned {len(tgt)} | no email on file {sum(1 for c in pool if not c['returned_on'] and not valid_email(c['email']))}"
                     f" | ambiguous names {sum(1 for c in pool if c['match']=='ambiguous')}")

    # outputs
    aud = [c for c in state["customers"].values() if not c["returned_on"] and valid_email(c["email"])]
    seen = {}
    for c in aud:  # one row per email; keep most recent forfeit
        e = c["email"]
        if e not in seen or c["last_forfeit"] > seen[e]["last_forfeit"]:
            seen[e] = c
    cols = ["EMAIL", "FIRSTNAME", "LASTNAME", "FORFEITED_LOAN", "FORFEIT_STORE", "LAST_FORFEIT_DATE", "NEW_THIS_WEEK"]
    def row(c):
        t = norm_tokens(c["name"])
        return [c["email"], t[0].title() if t else "", t[-1].title() if len(t) > 1 else "", "true", c["store"],
                c["last_forfeit"], "true" if not c["touches"] else "false"]
    with open(os.path.join(rundir, "audience.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(cols); [w.writerow(row(c)) for c in seen.values()]
    with open(os.path.join(rundir, "new_this_week.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(cols); [w.writerow(row(c)) for c in seen.values() if not c["touches"]]

    lines += ["", f"Audience (unique emails, not returned): {len(seen)}",
              f"Never touched yet (gets Month-1 email): {sum(1 for c in seen.values() if not c['touches'])}",
              f"First run (seed): {first_run}", f"Stores failing gate: {', '.join(gate_fail) or 'none'}"]
    state["runs"].append({"run": run.isoformat(), "gate_fail": gate_fail, "audience": len(seen)})
    json.dump(state, open(state_path, "w"), indent=1, default=str)
    open(os.path.join(rundir, "report.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    if gate_fail and len(gate_fail) < len(STORES):
        # partial: good stores still go through; the missing ones are retried next run
        try:
            ledger = os.path.normpath(os.path.join(HERE, "..", "..", "Valley Pawn OS", "fleet", "FAILURE_LEDGER.md"))
            with open(ledger, "a") as f:
                f.write(f"| {dt.datetime.now():%Y-%m-%d %H:%M} ET (native) | forfeiture-winback | Win-back audience updated without {', '.join(gate_fail)} this run (store data missing or incomplete); it will be picked up on the next run. | NEEDS_HUMAN: no | OPEN |\n")
        except Exception:
            pass
    sys.exit(2 if len(gate_fail) == len(STORES) else 0)


if __name__ == "__main__":
    main()
