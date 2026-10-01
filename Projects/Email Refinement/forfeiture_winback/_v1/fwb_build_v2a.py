#!/usr/bin/env python3
"""
Forfeited-Loan Win-Back — audience builder v2 (exact-match, 2026-09-29). stdlib only.

Joshua 9/29: "we need better data, phone contact, 100% accuracy on target audience".
v1 matched on name alone and knew returns only to the week. v2 uses three Bravo views
that share Bravo's own customer fields, and only keeps a customer when every check passes:

  L  {RUN}_{ST}_forfeiture-winback-addr.csv
       Loans/Buys "Claude Forfeiture Winback" with layout "High Dollar Loan Demographic":
       Ticket Number, Disposition, Pull Date, Customer, SMS, Address  (EXPIRED, age < 730)
  C  *_{ST}_forfeiture-winback-comparison-contacts.csv
       Customers "...Comparison" with layout "Customer Address Check":
       Name, Phone, Address, E-Mail, SMS            (Last Time In > the file's date)
  V  *_{ST}_forfeiture-winback-comparison-visits.csv
       same report, layout "Customers First Time In": Name, Zip Code, Last Time In

Identity  = the customer's full name (suffix kept) + their address as Bravo prints it on
            both the ticket and the customer record. Zip is the tie-breaker for visits.
Came back = Bravo's own "Last Time In" is ON or AFTER the forfeit (pull) date. Same-day
            counts as back (never email someone who may have been in that day).
Target    = forfeited, Last Time In verified and before the forfeit, identity unique.
            Anything unverified or ambiguous is EXCLUDED and counted, never guessed.

Outputs: state.json, runs/RUN/{audience.csv, sms.csv, excluded.csv, report.md}
Exit 0 = at least one store built (partial stores are ledgered), 2 = nothing usable.
"""
import csv, glob, json, os, re, sys, datetime as dt
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("FWB_OUT") or os.path.normpath(os.path.join(HERE, "..", "..", "Bravo Data Extraction", "output"))
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
MIN_CAPTURE = 0.995   # grid capture per file; below this the store is skipped (Rule 18)
FULL_DAYS = 700       # a visits/contacts file whose window reaches back >= this far counts as a full directory


def ntoks(name):
    return re.sub(r"[^A-Z ]", " ", (name or "").upper()).split()


def kname(name):
    return " ".join(sorted(ntoks(name)))


def kaddr(a):
    a = (a or "").upper()
    a = re.sub(r"[^A-Z0-9 ]", " ", a)
    rep = {"STREET": "ST", "ROAD": "RD", "AVENUE": "AVE", "DRIVE": "DR", "LANE": "LN", "COURT": "CT",
           "CIRCLE": "CIR", "BOULEVARD": "BLVD", "HIGHWAY": "HWY", "PLACE": "PL", "TERRACE": "TER",
           "APARTMENT": "APT", "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W", "TRAIL": "TRL"}
    return " ".join(rep.get(t, t) for t in a.split())


def zip5(a):
    m = re.findall(r"\b(\d{5})(?:-\d{4})?\b", a or "")
    return m[-1] if m else ""


def pdate(s):
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", s or "")
    return dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2))) if m else None


def phone10(p):
    d = re.sub(r"\D", "", p or "")
    if len(d) == 11 and d[0] == "1":
        d = d[1:]
    return d if len(d) == 10 and d[0] not in "01" else ""


def email_ok(e):
    e = (e or "").strip().lower()
    return e if re.fullmatch(r"[a-z0-9._%+'-]+@[a-z0-9.-]+\.[a-z]{2,}", e) and not re.search(r"\.(con|cm|co\.m|fa)$", e) else ""


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def capture(path):
    m = path + ".meta"
    if not os.path.exists(m):
        return False, "no .meta"
    kv = dict(l.strip().split("=", 1) for l in open(m) if "=" in l)
    e, c = int(kv.get("expected", -1)), int(kv.get("captured", -1))
    if e == 0 and c == 0:
        return True, "0/0"
    return (e > 0 and c / e >= MIN_CAPTURE), f"{c}/{e}"


def fdate(path):
    return dt.date.fromisoformat(os.path.basename(path)[:10])


def main():
    run = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today()
    sp = os.path.join(HERE, "state.json")
    state = json.load(open(sp)) if os.path.exists(sp) else {"version": 2, "customers": {}, "runs": []}
    rd = os.path.join(HERE, "runs", run.isoformat()); os.makedirs(rd, exist_ok=True)
    lines, skipped, excluded = [f"# Forfeiture win-back build v2 — {run}", ""], [], []

    for st in STORES:
        fl = os.path.join(OUT, f"{run}_{st}_forfeiture-winback-addr.csv")
        fcs = sorted(glob.glob(os.path.join(OUT, f"*_{st}_forfeiture-winback-comparison-contacts.csv")))
        fvs = sorted(glob.glob(os.path.join(OUT, f"*_{st}_forfeiture-winback-comparison-visits.csv")))
        def rows_ok(p):  # a full directory can never be empty; an empty one means the pull did not render
            try:
                return sum(1 for _ in open(p, encoding="utf-8-sig")) > 1
            except Exception:
                return False
        full_v = [p for p in fvs if (run - fdate(p)).days >= FULL_DAYS and rows_ok(p)]
        full_c = [p for p in fcs if (run - fdate(p)).days >= FULL_DAYS and rows_ok(p)]
        why = []
        if not os.path.exists(fl): why.append("loans file missing")
        if not full_v: why.append("no full visits directory yet")
        if not full_c: why.append("no full contacts directory yet")
        for p in [fl] + fcs[-2:] + fvs[-2:] + full_v[-1:] + full_c[-1:]:
            if os.path.exists(p):
                ok, cc = capture(p)
                if not ok: why.append(f"{os.path.basename(p)} capture {cc}")
        if why:
            skipped.append(st); lines.append(f"- {st}: SKIPPED — {'; '.join(sorted(set(why)))}"); continue

        # ---- customer directory (contacts): (name,addr) and (name,zip) indexes, newest file wins
        con_na, con_nz = defaultdict(list), defaultdict(list)
        for p in fcs:
            for r in read(p):
                c = {"name": r.get("Name", "").strip(), "addr": r.get("Address", "").strip(),
                     "phone": phone10(r.get("Phone", "")), "email": email_ok(r.get("E-Mail", "")),
                     "sms": (r.get("SMS", "") or "").strip().upper(), "src": os.path.basename(p)}
                kn = kname(c["name"])
                con_na[(kn, kaddr(c["addr"]))].append(c)
                con_nz[(kn, zip5(c["addr"]))].append(c)
        # ---- visits: (name,zip) -> latest Last Time In; count distinct people per key from the full file
        vis_last, vis_people, vis_name_last = {}, Counter(), {}
        for p in fvs:
            is_full = p in full_v
            for r in read(p):
                k = (kname(r.get("Name", "")), (r.get("Zip Code", "") or "").strip()[:5])
                d = pdate(r.get("Last Time In", ""))
                if is_full and p == full_v[-1]:
                    vis_people[k] += 1
                if d and (k not in vis_last or d > vis_last[k]):
                    vis_last[k] = d
                if d and (k[0] not in vis_name_last or d > vis_name_last[k[0]]):
                    vis_name_last[k[0]] = d

        # ---- forfeits per customer identity (name + address on the ticket)
        per = {}
        for r in read(fl):
            if (r.get("Disposition", "") or "").upper() not in ("EXPIRED", "FORFEITED"):
                continue
            nm, ad = (r.get("Customer", "") or "").strip(), (r.get("Address", "") or "").strip()
            ds = [d for d in (pdate(r.get("Pull Date", "")), pdate(r.get("Disposition Date", ""))) if d]
            f = min(ds) if ds else None   # earliest = conservative (any visit after it counts as back)
            if not nm or not f:
                continue
            k = (kname(nm), kaddr(ad))
            p = per.setdefault(k, {"name": nm, "addr": ad, "zip": zip5(ad), "last": f, "tickets": set(), "dnt": False})
            p["last"] = max(p["last"], f); p["tickets"].add(r.get("Ticket Number", ""))
            if (r.get("SMS", "") or "").upper() == "DNT":
                p["dnt"] = True

        cnt = Counter()
        for (kn, ka), p in per.items():
            ck = f"{st}|{kn}|{ka}"
            c = state["customers"].get(ck) or {"store": st, "name": p["name"], "addr": p["addr"], "zip": p["zip"],
                                               "touches": [], "added": run.isoformat()}
            c["last_forfeit"] = max(c.get("last_forfeit", ""), p["last"].isoformat())
            c["tickets"] = sorted(set(c.get("tickets", [])) | p["tickets"])
            c["ticket_dnt"] = bool(c.get("ticket_dnt")) or p["dnt"]
            # visits
            vk = (kn, p["zip"])
            people = vis_people.get(vk, 0)
            lti = vis_last.get(vk)
            if lti:
                c["last_time_in"] = max(c.get("last_time_in") or "", lti.isoformat())
            # contacts: exact name+address first, then name+zip only if it is one person
            hits = con_na.get((kn, ka)) or []
            how = "name+address"
            if not hits:
                z = con_nz.get((kn, p["zip"])) or []
                if len({(h["phone"], h["email"], kaddr(h["addr"])) for h in z}) == 1:
                    hits, how = z, "name+zip"
            ph = {h["phone"] for h in hits if h["phone"]}; em = {h["email"] for h in hits if h["email"]}
            sm = {h["sms"] for h in hits if h["sms"]}
            c["phone"] = next(iter(ph)) if len(ph) == 1 else ""
            c["email"] = next(iter(em)) if len(em) == 1 else ""
            c["sms_status"] = next(iter(sm)) if len(sm) == 1 else ""
            c["contact_match"] = how if hits else "none"
            # verdict
            lf = dt.date.fromisoformat(c["last_forfeit"])
            lt = dt.date.fromisoformat(c["last_time_in"]) if c.get("last_time_in") else None
            if people > 1:
                v = "excluded: two customers share this name and zip"
            elif not lt:
                v = "excluded: no Last Time In found for this customer"
            elif lt >= lf:
                v = "returned"
            elif vis_name_last.get(kn) and vis_name_last[kn] >= lf:
                # someone with the SAME NAME (other zip / duplicate record) was in after the forfeit —
                # could be this person under a second Bravo record; never risk it
                v = "excluded: same name seen in store after the forfeit (possible duplicate record)"
            else:
                v = "target"
            c["status"] = v
            c["checked"] = run.isoformat()
            state["customers"][ck] = c
            cnt[v] += 1
            if v == "target":
                cnt["target_email"] += bool(c["email"])
                cnt["target_sms"] += bool(c["phone"] and c["sms_status"] == "SMS" and not c["ticket_dnt"])
                cnt["target_phone_any"] += bool(c["phone"])
            elif v.startswith("excluded"):
                excluded.append([st, c["name"], c["addr"], c["last_forfeit"], v])
        lines.append(f"- {st}: forfeiters {len(per)} | came back {cnt['returned']} | TARGET {cnt['target']} "
                     f"(email {cnt['target_email']}, textable {cnt['target_sms']}, any phone {cnt['target_phone_any']}) "
                     f"| excluded {sum(v for k, v in cnt.items() if k.startswith('excluded'))}")

    tg = [c for c in state["customers"].values() if c.get("status") == "target" and c["store"] not in skipped]
    cols = ["EMAIL", "FIRSTNAME", "LASTNAME", "FORFEITED_LOAN", "FORFEIT_STORE", "LAST_FORFEIT_DATE", "LAST_TIME_IN", "NEW_THIS_WEEK"]
    seen = {}
    for c in tg:
        if c["email"] and (c["email"] not in seen or c["last_forfeit"] > seen[c["email"]]["last_forfeit"]):
            seen[c["email"]] = c

    def nm(c):
        t = ntoks(c["name"]); return (t[0].title() if t else ""), (t[-1].title() if len(t) > 1 else "")
    with open(os.path.join(rd, "audience.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(cols)
        for c in seen.values():
            a, b = nm(c); w.writerow([c["email"], a, b, "true", c["store"], c["last_forfeit"], c.get("last_time_in", ""), "false" if c["touches"] else "true"])
    with open(os.path.join(rd, "sms.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["PHONE", "FIRSTNAME", "LASTNAME", "STORE", "LAST_FORFEIT_DATE", "LAST_TIME_IN"])
        ph = {}
        for c in tg:
            if c["phone"] and c.get("sms_status") == "SMS" and not c.get("ticket_dnt"):
                ph.setdefault(c["phone"], c)
        for p, c in ph.items():
            a, b = nm(c); w.writerow([p, a, b, c["store"], c["last_forfeit"], c.get("last_time_in", "")])
    # per-store Chekkit upload files (same format as the Shop Us Online text lists); staff phones removed
    staff = set()
    try:
        ros = json.load(open(os.path.normpath(os.path.join(HERE, "..", "..", "Valley Pawn OS", "hr", "ROSTER.json"))))
        staff = {phone10(str(e.get("phone") or "")) for e in ros.get("employees", [])} - {""}
    except Exception:
        pass
    SN = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke", "WAY": "Waynesboro"}
    for code, nmx in SN.items():
        rows = [c for p2, c in ph.items() if c["store"] == code and p2 not in staff]
        with open(os.path.join(rd, f"chekkit_{nmx}.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["First Name", "Last Name", "Phone", "Email"])
            for c in rows:
                a, b = nm(c); p2 = c["phone"]
                w.writerow([a, b, f"({p2[:3]}) {p2[3:6]}-{p2[6:]}", c.get("email", "")])
    with open(os.path.join(rd, "excluded.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["STORE", "NAME", "ADDRESS", "LAST_FORFEIT", "REASON"]); w.writerows(excluded)
    lines += ["", f"Target customers (verified not back): {len(tg)}", f"Unique emails: {len(seen)}",
              f"Textable phones (SMS consent, not DNT): {len(ph)}", f"Stores skipped: {', '.join(skipped) or 'none'}"]
    state["runs"].append({"run": run.isoformat(), "skipped": skipped, "target": len(tg), "emails": len(seen), "sms": len(ph)})
    json.dump(state, open(sp + ".tmp", "w"), indent=1, default=str); os.replace(sp + ".tmp", sp)
    open(os.path.join(rd, "report.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    if skipped and len(skipped) < len(STORES):
        try:
            led = os.path.normpath(os.path.join(HERE, "..", "..", "Valley Pawn OS", "fleet", "FAILURE_LEDGER.md"))
            with open(led, "a") as f:
                f.write(f"| {dt.datetime.now():%Y-%m-%d %H:%M} ET (native) | forfeiture-winback | Win-back audience built without {', '.join(skipped)} (store data not complete yet); picked up next run. | NEEDS_HUMAN: no | OPEN |\n")
        except Exception:
            pass
    sys.exit(2 if len(skipped) == len(STORES) else 0)


if __name__ == "__main__":
    main()
