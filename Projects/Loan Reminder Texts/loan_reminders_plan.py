#!/usr/bin/env python3
"""loan_reminders_plan.py [--send-date YYYY-MM-DD] [--pull-date YYYY-MM-DD] -- NO-SEND trial planner (2026-11-21).
OFFLINE: no network import, no send function. For each store it reads the Bravo list pulled by the pipeline cell
`loan-reminders` (<pull-date>_<STORE>_loan-reminders.csv), the phone list already on disk (weekly Bravo customer
exports), Chekkit opt-outs (fleet/state/chekkit_optouts) and dead numbers (fleet/state/chekkit_failed), and writes
what WOULD be texted on the send date (default: tomorrow, the day Bravo would send at 10:00 AM):
  trial/<send-date>/plan_<STORE>.csv, skipped_<STORE>.csv, summary.json   and one line per store in trial/SUMMARY.csv
Customers with the MobilePawn app activated are left to Bravo's free app notice (cutover design 11/19)."""
import csv, glob, json, os, sys, collections
from datetime import date, datetime, timedelta
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reminder_core as rc
PROJ = os.path.dirname(HERE)
BRAVO_OUT = os.path.join(PROJ, "Bravo Data Extraction", "output")
STATE = os.path.join(PROJ, "Valley Pawn OS", "fleet", "state")
STORES = [("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke"), ("WAY", "Waynesboro")]


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def fdate(p):
    return os.path.basename(p)[:10]


def contacts_for(code, optouts):
    """{norm_name: [{'phone','dnt'}]} - for each name, the phone(s) in the NEWEST export that lists that name."""
    best = {}   # name -> (file date, set(phones))
    pats = [("*_%s_forfeiture-winback-comparison-contacts.csv" % code, "Name", "Phone"),
            ("*_%s_chekkit-invites-range.csv" % code, "first_name", "phone")]
    for pat, ncol, pcol in pats:
        for f in glob.glob(os.path.join(BRAVO_OUT, pat)):
            d = fdate(f)
            try:
                with open(f, newline="", encoding="utf-8-sig", errors="replace") as fh:
                    for r in csv.DictReader(fh):
                        n, p = rc.norm_name(r.get(ncol)), rc.phone10(r.get(pcol))
                        if not n or not p: continue
                        old = best.get(n)
                        if old is None or d > old[0]: best[n] = (d, {p})
                        elif d == old[0]: old[1].add(p)
            except OSError:
                pass
    return {n: [{"phone": p, "dnt": p in optouts} for p in ph] for n, (d, ph) in best.items()}


def lines(path):
    try:
        return {l.split("\t")[0].strip()[-10:] for l in open(path) if l.strip()}
    except OSError:
        return set()


def no_send_dates():
    """Days on which nothing is texted (holidays), from fleet/state/loan_reminders_no_send_dates.txt."""
    out = set()
    try:
        for l in open(os.path.join(STATE, "loan_reminders_no_send_dates.txt")):
            l = l.strip()
            if l and not l.startswith("#"):
                try: out.add(datetime.strptime(l[:10], "%Y-%m-%d").date())
                except ValueError: pass
    except OSError:
        pass
    return out


def send_window_ok(list_path, send, now=None):
    """NO REMINDER AFTER A PAYMENT (Joshua 2026-11-21). A text may only go out when BOTH hold:
      1. the Bravo list was pulled after every store closed the evening before the send date (stores close 6 PM;
         list must be from 6:30 PM or later that evening), and
      2. it is still before the stores open on the send date (they open 10 AM; sending stops 9:45 AM).
    Between those two moments no store is open, so no loan on the list can have been paid at a counter or by phone.
    Customers who can pay in the app overnight are not on the text side at all (Bravo's app notice covers them).
    A future sender MUST call this per store and send nothing when it is False (the day is skipped, never sent late)."""
    now = now or datetime.now()
    try:
        pulled = datetime.fromtimestamp(os.path.getmtime(list_path))
    except OSError:
        return False, "no list"
    earliest = datetime.combine(send - timedelta(days=1), datetime.min.time()).replace(hour=18, minute=30)
    cutoff = datetime.combine(send, datetime.min.time()).replace(hour=9, minute=45)
    if pulled < earliest: return False, "list pulled before close (%s)" % pulled.strftime("%m/%d %H:%M")
    if now > cutoff: return False, "past 9:45 AM on the send date"
    return True, "list pulled %s, after close" % pulled.strftime("%m/%d %I:%M %p")


def plan_layaways(code, town, pull, send, contacts, dead, sent_keys):
    """Layaway reminders from the pipeline cell layaway-detail (<pull>_<STORE>_layaway-detail-all-active.tsv).
    Schedule = Bravo's (reminder_core.layaway_kind). One text per customer per kind per day. App-activated
    customers are left to Bravo's app notice. Returns (texts, skipped, stats) or None when there is no list."""
    f = os.path.join(BRAVO_OUT, "%s_%s_layaway-detail-all-active.tsv" % (pull, code))
    if not os.path.exists(f):
        return None
    rows = list(csv.DictReader(open(f, newline="", encoding="utf-8-sig", errors="replace"), delimiter="\t"))
    groups, skipped, due_n, app_n = {}, [], 0, 0
    for r in rows:
        nd = rc.parse_date(r.get("Next Due"))
        kind = rc.layaway_kind(nd, send) if nd else None
        if not kind: continue
        due_n += 1
        lay = (r.get("Layaway Number") or "").strip()
        if (r.get("MobilePawn") or "").strip().lower() == "activated":
            app_n += 1; continue
        cust = (r.get("Customer") or "").strip()
        c = contacts.get(rc.norm_name(cust), [])
        phones = {x["phone"] for x in c}
        key = "%s|%s|%s|%s" % (lay, kind, nd.isoformat(), send.isoformat() if kind == "layaway_late" else "")
        if not c: why = "no phone on file"
        elif any(x.get("dnt") for x in c): why = "opted out in Chekkit"
        elif len(phones) != 1: why = "name matches %d phone numbers" % len(phones)
        elif phones & dead: why = "number failed delivery before (dead or landline)"
        elif key in sent_keys: why = "already sent"
        else:
            groups.setdefault((next(iter(phones)), kind), {"name": cust, "due": nd, "keys": []})
            g = groups[(next(iter(phones)), kind)]; g["keys"].append(key); g["due"] = min(g["due"], nd)
            continue
        skipped.append({"store": town, "ticket": lay, "reason": why})
    texts = []
    for (phone, kind), g in sorted(groups.items()):
        first = (g["name"].split() or [""])[0].title()
        body = rc.TEMPLATES[kind].format(name=first, store=town, due=g["due"].strftime("%-m/%-d"))
        if len(body) > 160 or not first:      # 160 rule: drop the name rather than pay for two texts
            body = "Your" + body[body.index(" Valley Pawn"):]
        texts.append({"store": town, "phone": phone, "kind": kind, "text": body, "name": g["name"].title(), "keys": g["keys"], "segments": -(-len(body) // 153) if len(body) > 160 else 1})
    return texts, skipped, {"active_layaways": len(rows), "layaway_reminders_due": due_n, "layaway_left_to_app": app_n}


def plan_occasions(code, town, send, optouts, dead, sent_keys):
    """Birthday and first-visit-anniversary texts (marketing: 15% off). Offline, from Bravo exports already on disk:
    birthdays  <D>_<STORE>_forfeiture-winback-comparison-birthdays.csv (Name, Birthday)   [bin/birthday_list_pull.sh]
    visits     <D>_<STORE>_forfeiture-winback-comparison-visits.csv    (Name, First Time In)  [weekly win-back job]
    contacts   <D>_<STORE>_forfeiture-winback-comparison-contacts.csv  (Name, Phone, MobilePawn, SMS)
    Covers customers seen in the last ~760 days. Because it is marketing, Bravo's DNT flag is honored as well as
    Chekkit opt-outs (carrier-safety rule 10/23). App-activated customers are left to Bravo's app notice.
    One text per customer per kind per year. Returns (texts, stats). Written to occasions_<STORE>.csv, which the
    sender does NOT read - nothing here can go out until Joshua approves it."""
    def newest(pattern, ncol, vcol):
        best = {}
        for f in glob.glob(os.path.join(BRAVO_OUT, pattern % code)):
            d = "%014d" % os.path.getmtime(f)
            try:
                with open(f, newline="", encoding="utf-8-sig", errors="replace") as fh:
                    for r in csv.DictReader(fh):
                        n = rc.norm_name(r.get(ncol))
                        if n and (n not in best or d >= best[n][0]): best[n] = (d, r)
            except OSError:
                pass
        return {n: r for n, (d, r) in best.items()}
    con = newest("*_%s_forfeiture-winback-comparison-contacts.csv", "Name", "Phone")
    vis = newest("*_%s_forfeiture-winback-comparison-visits.csv", "Name", "First Time In")
    bd = newest("*_%s_forfeiture-winback-comparison-birthdays.csv", "Name", "Birthday")
    texts, why = [], collections.Counter()
    seen_phone = set()
    for kind, src, col in (("birthday", bd, "Birthday"), ("anniversary", vis, "First Time In")):
        for n, r in sorted(src.items()):
            raw = (r.get(col) or "").strip()
            if kind == "birthday":            # Bravo shows birthdays as "August 9" (no year)
                try: d = datetime.strptime(raw + " 2000", "%B %d %Y").date()
                except ValueError: d = None
                if not d or (d.month, d.day) != (send.month, send.day): continue
            else:
                d = rc.parse_date(raw)
                if not d or (d.month, d.day) != (send.month, send.day) or d.year >= send.year: continue
            c = con.get(n)
            phone = rc.phone10(c.get("Phone")) if c else ""
            key = "%s|%s|%d" % (kind, phone, send.year)
            if not phone: why[kind + ": no phone on file"] += 1
            elif (c.get("SMS") or "").strip().upper() == "DNT": why[kind + ": store marked do-not-text"] += 1
            elif phone in optouts: why[kind + ": opted out in Chekkit"] += 1
            elif phone in dead: why[kind + ": dead number"] += 1
            elif (c.get("MobilePawn") or "").strip().lower() == "activated": why[kind + ": left to app notice"] += 1
            elif key in sent_keys or (phone, kind) in seen_phone: why[kind + ": already sent this year"] += 1
            else:
                seen_phone.add((phone, kind))
                first = ((r.get(col and "Name") or "").split() or [""])[0].title()
                body = rc.TEMPLATES[kind].format(name=first)
                if len(body) > 160 or not first: body = body.replace(", " + first + "!", "!").replace(", !", "!")
                texts.append({"store": town, "phone": phone, "kind": kind, "text": body, "name": (r.get("Name") or "").title(), "keys": [key], "segments": 1 if len(body) <= 160 else 2})
    return texts, {"customers_with_phone_list": len(con), "birthdays_on_file": len(bd), "first_visits_on_file": len(vis), "why_not": dict(why)}


def plan_invites(code, town, pull, send, rows, optouts, dead, ledger_path):
    """App invitation texts (replaces Bravo's "MobilePawn New Loan" / "New Layaway" invitations). Who: customer
    whose loan was written, or layaway started, in the last 7 days, MobilePawn "Not Activated", phone on file, not
    store-marked do-not-text, not opted out in Chekkit, not a dead number. At most one invitation per phone per 7
    days (Bravo's own rule), tracked in the store ledger as  invite|<phone>  <tab> <send date>."""
    con = {}
    for f in glob.glob(os.path.join(BRAVO_OUT, "*_%s_forfeiture-winback-comparison-contacts.csv" % code)):
        d = "%014d" % os.path.getmtime(f)
        try:
            with open(f, newline="", encoding="utf-8-sig", errors="replace") as fh:
                for r in csv.DictReader(fh):
                    n = rc.norm_name(r.get("Name"))
                    if n and (n not in con or d >= con[n][0]): con[n] = (d, r)
        except OSError:
            pass
    recent = {}
    if os.path.exists(ledger_path):
        for l in open(ledger_path):
            p = l.rstrip("\n").split("\t")
            if len(p) == 2 and p[0].startswith("invite|"):
                try:
                    if (send - datetime.strptime(p[1], "%Y-%m-%d").date()).days < 7 and p[1] != send.isoformat(): recent[p[0]] = p[1]
                except ValueError:
                    pass
    cands = []     # (customer name, MobilePawn status)
    for r in rows:
        if (r.get("Disposition") or "").strip().upper() != "ON LOAN": continue
        try: age = int((r.get("Age") or "").strip())
        except ValueError: continue
        if 0 <= age <= 6: cands.append(((r.get("Customer") or "").strip(), (r.get("MobilePawn") or "").strip()))
    lf = os.path.join(BRAVO_OUT, "%s_%s_layaway-detail-all-active.tsv" % (pull, code))
    if os.path.exists(lf):
        for r in csv.DictReader(open(lf, newline="", encoding="utf-8-sig", errors="replace"), delimiter="\t"):
            try: age = int((r.get("Age") or "").strip())
            except ValueError: continue
            if 0 <= age <= 7: cands.append(((r.get("Customer") or "").strip(), (r.get("MobilePawn") or "").strip()))
    texts, why, seen = [], collections.Counter(), set()
    for name, mp in cands:
        n = rc.norm_name(name)
        if not n or n in seen: continue
        seen.add(n)
        c = con.get(n, (None, None))[1]
        phone = rc.phone10(c.get("Phone")) if c else ""
        key = "invite|%s" % phone
        if mp.lower() != "not activated": why["has the app or not eligible"] += 1
        elif not phone: why["no phone on file yet"] += 1
        elif (c.get("SMS") or "").strip().upper() == "DNT": why["store marked do-not-text"] += 1
        elif phone in optouts: why["opted out in Chekkit"] += 1
        elif phone in dead: why["dead number"] += 1
        elif key in recent: why["invited in the last 7 days"] += 1
        else:
            body = rc.TEMPLATES["app_invite"].format(store=town)
            texts.append({"store": town, "phone": phone, "kind": "app_invite", "text": body, "name": name.title(), "keys": [key], "segments": 1 if len(body) <= 160 else 2})
    return texts, {"new_loan_or_layaway_customers": len(seen), "why_not": dict(why)}


def main():
    pull = arg("--pull-date", date.today().isoformat())
    send = datetime.strptime(arg("--send-date", (datetime.strptime(pull, "%Y-%m-%d").date() + timedelta(days=1)).isoformat()), "%Y-%m-%d").date()
    out = os.path.join(HERE, "trial", send.isoformat()); os.makedirs(out, exist_ok=True)
    summary = {"send_date": send.isoformat(), "pull_date": pull, "generated_at": datetime.now().isoformat(timespec="seconds"), "mode": "NO-SEND", "stores": {}}
    for code, town in STORES:
        f = os.path.join(BRAVO_OUT, "%s_%s_loan-reminders.csv" % (pull, code))
        if not os.path.exists(f):
            summary["stores"][code] = {"error": "no Bravo list for %s" % pull}; continue
        rows = list(csv.DictReader(open(f, newline="", encoding="utf-8-sig", errors="replace")))
        app = {}
        for r in rows:
            app.setdefault((r.get("Ticket Number") or "").strip(), (r.get("MobilePawn") or "").strip().lower() == "activated")
        tickets = rc.tickets_from_rows(rows)
        live = [t for t in tickets if t["disposition"] in rc.LIVE_DISPOSITIONS]
        due_today = [t for t in live if t["due"] and rc.loan_kind(t["due"], send)]
        text_side = [t for t in tickets if not app.get(t["ticket"])]
        optouts = lines(os.path.join(STATE, "chekkit_optouts", code + ".tsv"))
        dead = lines(os.path.join(STATE, "chekkit_failed", code + ".txt"))
        contacts = contacts_for(code, optouts)
        ledger = os.path.join(HERE, "trial", "ledger_%s.txt" % code)
        # ledger line = key <tab> send date; a re-run for the same send date does not count as already sent
        sent_keys = frozenset(l.split("\t")[0].strip() for l in open(ledger) if l.strip() and l.rstrip("\n").split("\t")[-1] != send.isoformat()) if os.path.exists(ledger) else frozenset()
        mine = set(l.split("\t")[0].strip() for l in open(ledger) if l.rstrip("\n").split("\t")[-1] == send.isoformat()) if os.path.exists(ledger) else set()
        texts, skipped = rc.build_plan(town, text_side, contacts, send, sent_keys)
        # No-send day tomorrow (holiday): the "due tomorrow" notice it would have carried goes out today instead,
        # so nobody loses the heads-up. Past-due texts are simply not sent on the holiday.
        hol = no_send_dates()
        nxt = send + timedelta(days=1)
        if nxt in hol:
            early, _ = rc.build_plan(town, text_side, contacts, nxt, sent_keys)
            texts += [t for t in early if t["kind"] == "courtesy"]
        keep = []
        for t in texts:
            if t["phone"] in dead:
                skipped += [{"store": town, "ticket": k.split("|")[0], "reason": "number failed delivery before (dead or landline)"} for k in t["keys"]]
            else:
                keep.append(t)
        texts = keep
        cust_of = {t["ticket"]: t["customer"] for t in tickets}
        for t in texts: t["name"] = cust_of.get(t["keys"][0].split("|")[0], "").title()
        lay = plan_layaways(code, town, pull, send, contacts, dead, sent_keys)
        lay_stats = {"layaway_list": "none for %s" % pull}
        if lay:
            texts += lay[0]; skipped += lay[1]; lay_stats = lay[2]
        occ, occ_stats = plan_occasions(code, town, send, optouts, dead, sent_keys)
        back = send - timedelta(days=1)
        while back in hol:                      # birthdays/anniversaries that fell on a no-send day go out the day after
            more, _ = plan_occasions(code, town, back, optouts, dead, sent_keys)
            have_ = {(t["phone"], t["kind"]) for t in occ}
            occ += [t for t in more if (t["phone"], t["kind"]) not in have_]
            back -= timedelta(days=1)
        with open(os.path.join(out, "occasions_%s.csv" % code), "w", newline="") as fh:   # NOT read by the sender
            w = csv.writer(fh); w.writerow(["phone", "kind", "characters", "counts_as", "text", "tickets", "name"])
            for t in occ: w.writerow([t["phone"], t["kind"], len(t["text"]), t["segments"], t["text"], t["keys"][0], t["name"]])
        # birthday / anniversary go into the sendable plan only for stores switched on for them (Joshua OK 11/24:
        # wording approved, customers seen in the last two years only). Flag: fleet/state/loan_reminders_live/<STORE>.occasions
        occ_live = os.path.exists(os.path.join(STATE, "loan_reminders_live", code + ".occasions"))
        if occ_live: texts += occ
        inv, inv_stats = plan_invites(code, town, pull, send, rows, optouts, dead, ledger)
        inv_live = os.path.exists(os.path.join(STATE, "loan_reminders_live", code + ".invites"))
        with open(os.path.join(out, "invites_%s.csv" % code), "w", newline="") as fh:   # record; sent only when .invites flag exists
            w = csv.writer(fh); w.writerow(["phone", "kind", "characters", "text", "name"])
            for t in inv: w.writerow([t["phone"], t["kind"], len(t["text"]), t["text"], t["name"]])
        if inv_live: texts += inv
        with open(os.path.join(out, "plan_%s.csv" % code), "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["phone", "kind", "characters", "counts_as", "text", "tickets", "name"])
            for t in texts:
                w.writerow([t["phone"], t["kind"], len(t["text"]), t["segments"], t["text"], " ".join(k.split("|")[0] for k in t["keys"]), t.get("name", "")])
        with open(os.path.join(out, "skipped_%s.csv" % code), "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["ticket", "reason"])
            for s in skipped: w.writerow([s["ticket"], s["reason"]])
        new_keys = [k for t in texts for k in t["keys"] if k not in mine]
        if new_keys and "--no-ledger" not in sys.argv:
            with open(ledger, "a") as fh: fh.write("".join("%s\t%s\n" % (k, send.isoformat()) for k in new_keys))
        kinds = collections.Counter(t["kind"] for t in texts)
        why = collections.Counter(s["reason"].split(" (")[0] for s in skipped if not s["reason"].startswith("not on loan"))
        summary["stores"][code] = {
            "open_loans_in_list": len(live), "loans_with_a_reminder_today": len(due_today),
            "left_to_bravo_app_notice": sum(1 for t in due_today if app.get(t["ticket"])),
            "texts_planned": len(texts), "courtesy": kinds.get("courtesy", 0), "past_due": kinds.get("past_due", 0),
            "counted_texts": sum(t["segments"] for t in texts), "longest": max([len(t["text"]) for t in texts] or [0]),
            "skipped": dict(why), "chekkit_optouts_known": len(optouts), "bravo_rows": len(rows),
            "would_be_allowed_to_send": list(send_window_ok(f, send))}
        summary["stores"][code].update(lay_stats)
        summary["stores"][code]["app_invites_in_plan" if inv_live else "app_invites_NOT_SENT"] = dict(inv_stats, texts=len(inv))
        ok_ = collections.Counter(t["kind"] for t in occ)
        summary["stores"][code]["occasions_in_plan" if occ_live else "occasions_NOT_SENT"] = dict(occ_stats, birthday_texts=ok_.get("birthday", 0), anniversary_texts=ok_.get("anniversary", 0), longest=max([len(t["text"]) for t in occ] or [0]))
        summary["stores"][code].update({"layaway_notice": kinds.get("layaway_notice", 0), "layaway_late": kinds.get("layaway_late", 0)})
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1)
    sp = os.path.join(HERE, "trial", "SUMMARY.csv")
    new = not os.path.exists(sp) or os.path.getsize(sp) == 0
    with open(sp, "a", newline="") as fh:
        w = csv.writer(fh)
        if new: w.writerow(["send_date", "weekday", "store", "open_loans_in_list", "reminders_due", "app_notice_by_bravo", "texts_planned", "courtesy", "past_due", "counted_texts", "longest", "skipped", "layaway_notice", "layaway_late"])
        for code, s in summary["stores"].items():
            if "error" in s: w.writerow([send, send.strftime("%a"), code, "ERROR", s["error"]]); continue
            w.writerow([send, send.strftime("%a"), code, s["open_loans_in_list"], s["loans_with_a_reminder_today"], s["left_to_bravo_app_notice"], s["texts_planned"], s["courtesy"], s["past_due"], s["counted_texts"], s["longest"], json.dumps(s["skipped"]), s.get("layaway_notice", ""), s.get("layaway_late", "")])
    print(json.dumps(summary["stores"], indent=1))
    return 0 if all("error" not in s for s in summary["stores"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
