#!/usr/bin/env python3
"""scrap_closeout_monthly.py (2026-11-18) - NATIVE monthly scrap-gold closeout (Joshua 11/17-11/18: close on the
10th of the following month; one approval with gross profit by store; native agents first, Rule 21).

Runs from launchd (com.valleypawn.scrap-closeout-monthly) a few times a day. Each run advances month T (= previous
calendar month, once today >= the 10th) one stage, and is safe to re-run at any point:
  settlements -> read (weights + item costs, read-only) -> split + approval email -> wait for reply ->
  post in store hours (with retries) -> CLOSED.
Approval goes by email from jdavis@fcfpawn.com (Apple Mail) - Joshua replies POST or HOLD; the reply is read from
Apple Mail on this Mac (the Slack bot cannot read DMs: no im:history scope).
Never posts to Slack. A step only Joshua can do -> one row in Life OS/HUMAN_QUEUE.md (deduped by key).
Args: --month YYYY-MM  --dry (no email, no Bravo posting)  --parse-only (just print the settlements found)."""
import datetime as dt, email, glob, json, os, re, shutil, sqlite3, subprocess, sys
from email import policy
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
HOME = os.path.expanduser("~")
P = f"{HOME}/Documents/Claude/Projects"
OS_ = f"{P}/Valley Pawn OS"; BR = f"{P}/Bravo Data Extraction"; PM = f"{P}/Precious Metals Settlements"
BIN = f"{OS_}/bin"; ST_DIR = f"{OS_}/fleet/state/scrap_closeout"; os.makedirs(ST_DIR, exist_ok=True)
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
JOSHUA = ["jdavis@fcfpawn.com", "zapvp1@me.com"]
PDFTOTEXT = next((p for p in ["/opt/homebrew/bin/pdftotext", "/usr/local/bin/pdftotext"] if os.path.exists(p)), "pdftotext")
DRY = "--dry" in sys.argv
NOW = dt.datetime.now(ET)


def log(*a):
    print(NOW.strftime("%Y-%m-%d %H:%M"), *a, flush=True)


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def load(p, d):
    try:
        return json.load(open(p))
    except Exception:
        return d


def save(p, o):
    tmp = p + ".tmp"; json.dump(o, open(tmp, "w"), indent=1); os.replace(tmp, p)


def human(key, text):
    q = f"{P}/Life OS/HUMAN_QUEUE.md"
    try:
        cur = open(q).read()
    except Exception:
        cur = ""
    if f"[{key}]" in cur:
        return
    open(q, "a").write(f"| {NOW.date()} | [{key}] Valley Pawn - scrap gold | {text} | OPEN |\n")


def changelog(line):
    c = f"{OS_}/CHANGELOG.md"; t = open(c).read()
    open(c, "w").write(f"## {NOW.date()} (scrap gold monthly closeout - native)\n\n- {line}\n\n" + t)


# ---------------------------------------------------------------- Apple Mail (read-only)
def mail_db():
    env = glob.glob(f"{HOME}/Library/Mail/V*/MailData/Envelope Index")[0]
    return env, sqlite3.connect("file:%s?mode=ro" % env.replace(" ", "%20"), uri=True)


def mail_rows(where, params):
    env, c = mail_db()
    q = ("select m.ROWID, s.subject, a.address, m.date_received from messages m "
         "left join subjects s on s.ROWID=m.subject left join addresses a on a.ROWID=m.sender where " + where +
         " order by m.date_received")
    return env, list(c.execute(q, params))


def emlx_path(env, rowid):
    base = os.path.dirname(os.path.dirname(env))
    hits = glob.glob(f"{base}/**/{rowid}.emlx", recursive=True) + glob.glob(f"{base}/**/{rowid}.partial.emlx", recursive=True)
    return hits[0] if hits else None


def parse_emlx(path):
    raw = open(path, "rb").read(); raw = raw[raw.index(b"\n") + 1:]
    return email.message_from_bytes(raw, policy=policy.default)


def message_pdfs(env, rowid, outdir):
    """PDF attachments of one message: from the full .emlx, else from Mail's Attachments folder."""
    out = []
    p = emlx_path(env, rowid)
    if "--debug" in sys.argv:
        log("debug rowid", rowid, "emlx", p)
        if p:
            ad = os.path.join(os.path.dirname(os.path.dirname(p)), "Attachments", str(rowid))
            log("debug attdir", ad, os.path.isdir(ad), [f for f in glob.glob(ad + "/**/*", recursive=True)][:10])
            m = parse_emlx(p); log("debug parts", [(x.get_content_type(), x.get_filename()) for x in m.walk()][:12])
    if p:
        msg = parse_emlx(p)
        for part in msg.iter_attachments():
            fn = part.get_filename() or "att.pdf"
            if fn.lower().endswith(".pdf") or part.get_content_type() in ("application/pdf", "application/octet-stream"):
                data = part.get_payload(decode=True)
                if data and data[:4] == b"%PDF":
                    f = f"{outdir}/{rowid}_{len(out)}.pdf"; open(f, "wb").write(data); out.append(f)
        if not out:
            adir = os.path.join(os.path.dirname(os.path.dirname(p)), "Attachments", str(rowid))
            for f in glob.glob(f"{adir}/**/*.pdf", recursive=True) + glob.glob(f"{adir}/**/*.PDF", recursive=True):
                d = f"{outdir}/{rowid}_{len(out)}.pdf"; shutil.copy(f, d); out.append(d)
        if not out:
            out = mail_save_attachments(p, rowid, outdir)
    return out


def mail_save_attachments(emlx, rowid, outdir):
    """Attachment not downloaded yet (Mail keeps a .partial.emlx): ask Mail itself to save it - this downloads it."""
    parts = emlx.split("/")
    try:
        i = next(k for k, x in enumerate(parts) if re.fullmatch(r"V\d+", x))
    except StopIteration:
        return []
    acct = parts[i + 1]
    boxes = []
    for x in parts[i + 2:]:
        if x.endswith(".mbox"):
            boxes.append(x[:-5])
        else:
            break
    mbox = "/".join(boxes)
    dest = f"{outdir}/mail_{rowid}"; os.makedirs(dest, exist_ok=True)
    script = f'''with timeout of 300 seconds
tell application "Mail"
  set acc to first account whose id is "{acct}"
  set mb to mailbox "{mbox}" of acc
  set m to first message of mb whose id is {rowid}
  set n to 0
  repeat with a in (mail attachments of m)
    set n to n + 1
    save a in POSIX file ("{dest}/" & n & ".pdf")
  end repeat
  return n
end tell
end timeout'''
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=330)
    log("mail save", rowid, mbox, r.returncode, r.stdout.strip(), r.stderr.strip()[:200])
    return sorted(f for f in glob.glob(f"{dest}/*.pdf") if open(f, "rb").read(4) == b"%PDF")


def money(s):
    return float(s.replace("$", "").replace(",", ""))


def parse_settlement(txt):
    inv = re.search(r"\b(INV-\d{8}-\d+)\b", txt)
    lot = re.search(r"\b(LOT-\d+)\s+(Scrap Gold [A-Za-z ]+?)\s*$", txt, re.M)
    pre = re.search(r"Pre-Melt:\s+([\d.,]+)\s+([\d.,]+)\s+[\d.,]+\s+[\d.,]+\s+\$([\d,]+\.\d\d)", txt)
    post = re.search(r"Post-Melt:\s+([\d.,]+)\s+([\d.,]+)", txt)
    pay = re.search(r"(\d{2}/\d{2}/\d{4})\s+Wire\s+Settlement\s+(EPAY-\S+)\s+.*?\$([\d,]+\.\d\d)", txt)
    if not (inv and lot and pre and pay):
        return None
    kind = "stones" if "stone" in lot.group(2).lower() else ("gold" if "karat" in lot.group(2).lower() else None)
    if kind is None or "silver" in lot.group(2).lower():
        return None
    return {"kind": kind, "invoice": inv.group(1), "lot": lot.group(1), "lot_desc": lot.group(2).strip(),
            "date": pay.group(1), "wire": pay.group(2), "premelt_dwt": float(pre.group(2).replace(",", "")),
            "postmelt_dwt": float(post.group(2).replace(",", "")) if post else None,
            "gross": money(pre.group(3)), "net": money(pay.group(3))}


def closed_invoices():
    s = set()
    for f in glob.glob(f"{PM}/reviews/*_CLOSED.csv"):
        s |= set(re.findall(r"INV-\d{8}-\d+", open(f, errors="ignore").read()))
    return s


def find_settlements(T):
    y, m = map(int, T.split("-"))
    since = dt.datetime(y, m, 20, tzinfo=ET).timestamp()
    env, rows = mail_rows("lower(a.address) like ? and m.date_received >= ?", ("%elemetal.com%", int(since)))
    tmp = f"{ST_DIR}/pdf_{T}"; os.makedirs(tmp, exist_ok=True)
    seen, found = (set() if "--include-closed" in sys.argv else closed_invoices()), {"gold": [], "stones": []}
    for rowid, subj, addr, ts in rows:
        if "--debug" in sys.argv:
            log("debug mail", rowid, subj, addr, dt.datetime.fromtimestamp(ts))
        if "settlement" not in (subj or "").lower():
            continue
        for pdf in message_pdfs(env, rowid, tmp):
            txt = subprocess.run([PDFTOTEXT, "-layout", pdf, "-"], capture_output=True, text=True).stdout
            s = parse_settlement(txt)
            if s and s["invoice"] not in seen and s["invoice"] not in [x["invoice"] for x in found[s["kind"]]]:
                s["mail_rowid"] = rowid; s["received"] = dt.datetime.fromtimestamp(ts, ET).isoformat(timespec="minutes")
                found[s["kind"]].append(s)
    return found


def send_mail(subject, body):
    if DRY:
        log("[dry] email:", subject, "\n" + body); return True
    def esc(s): return s.replace("\\", "\\\\").replace('"', '\\"')
    lines = ['tell application "Mail"',
             f'  set msg to make new outgoing message with properties {{subject:"{esc(subject)}", content:"{esc(body)}", sender:"jdavis@fcfpawn.com", visible:false}}',
             '  tell msg']
    for a in JOSHUA:
        lines.append(f'    make new to recipient at end of to recipients with properties {{address:"{a}"}}')
    lines += ['  end tell', '  send msg', 'end tell']
    r = subprocess.run(["osascript", "-e", "\n".join(lines)], capture_output=True, text=True, timeout=120)
    log("email sent:", subject, r.returncode, r.stderr.strip()[:200]); return r.returncode == 0


def find_reply(token, after_ts):
    """Joshua's reply (POST/HOLD) to the approval email, read from Apple Mail."""
    env, rows = mail_rows("s.subject like ? and m.date_received > ?", (f"%{token}%", int(after_ts)))
    verdict = None
    for rowid, subj, addr, ts in rows:
        if not (subj or "").lower().startswith("re"):
            continue
        if (addr or "").lower() not in JOSHUA:
            continue
        p = emlx_path(env, rowid)
        if not p:
            continue
        b = parse_emlx(p).get_body(preferencelist=("plain", "html"))
        txt = b.get_content() if b else ""
        txt = re.sub(r"<[^>]+>", " ", txt)
        top = []
        for ln in txt.splitlines():
            if ln.strip().startswith(">") or re.match(r"\s*On .+wrote:\s*$", ln) or "Gold closeout" in ln:
                break
            top.append(ln)
        w = " ".join(top).lower()
        if "--reply-test" in sys.argv:
            log("reply-test", rowid, subj, addr, dt.datetime.fromtimestamp(ts), "| top:", w[:160])
        if re.search(r"\bhold\b|\bwait\b|\bstop\b|\bdon'?t\b", w):
            verdict = "hold"
        elif re.search(r"\bpost\b|\bapprove[d]?\b|\bgo\b|\byes\b", w):
            verdict = "post"
    return verdict


# ---------------------------------------------------------------- Bravo (through the proven runners)
def run_readopen(mid, T):
    man = {"id": mid, "readOnly": True, "buckets": [
        {"store": s, "bucketName": f"{T} {k}", "occurrence": 0, "amountPaid": "0.00", "tenderType": "Cashiers Check"}
        for s in STORES for k in ("GOLD", "GOLD WITH STONES")]}
    json.dump(man, open(f"{BR}/triggers-scrap-open/{mid}.json", "w"), indent=1)
    subprocess.run(["bash", f"{BIN}/scrap_readopen_run.sh", mid, "2400"])
    rp = f"{BR}/results-scrap/{mid}.result.json"
    return json.loads(open(rp, encoding="utf-8-sig").read()) if os.path.exists(rp) else None


def run_close(mid, buckets):
    json.dump({"id": mid, "buckets": buckets}, open(f"{BR}/triggers-scrap/{mid}.json", "w"), indent=2)
    subprocess.run(["bash", f"{BIN}/scrap_closeout_run.sh", mid, "4500"])
    rp = f"{BR}/results-scrap/{mid}.result.json"
    return json.loads(open(rp, encoding="utf-8-sig").read()) if os.path.exists(rp) else None


def store_hours():
    t = NOW
    return t.weekday() in (0, 1, 3, 4, 5) and (t.hour, t.minute) >= (10, 15) and (t.hour, t.minute) <= (16, 0)


# ---------------------------------------------------------------- main state machine
def main():
    if "--month" in sys.argv:
        T = arg("--month")
    else:
        first = NOW.date().replace(day=1)
        T = (first - dt.timedelta(days=1)).strftime("%Y-%m")
    if "--reply-test" in sys.argv:
        log("verdict:", find_reply(arg("--reply-test"), NOW.timestamp() - 20 * 86400)); return 0
    if "--parse-only" in sys.argv:
        print(json.dumps(find_settlements(T), indent=1)); return 0
    if os.path.exists(f"{PM}/reviews/{T}_allocations_CLOSED.csv"):
        log(T, "already CLOSED"); return 0
    if "--month" not in sys.argv and NOW.day < 10:
        log("before the 10th - nothing to do"); return 0
    sp = f"{ST_DIR}/{T}.json"; st = load(sp, {"month": T, "stage": "settlements", "attempts": 0})
    log("month", T, "stage", st["stage"])

    if st["stage"] == "settlements":
        f = find_settlements(T)
        if len(f["gold"]) != 1 or len(f["stones"]) != 1:
            log("settlements found: gold %d stones %d" % (len(f["gold"]), len(f["stones"])))
            if NOW.day >= 20 and not DRY:
                human(f"gold-settlement-{T}", f"The Elemetal settlement emails for {T} scrap are not both in (found gold {len(f['gold'])}, with-stones {len(f['stones'])}). "
                      "The monthly closeout waits for exactly one of each; check with Elemetal.")
            return 0
        st["gold"], st["stones"] = f["gold"][0], f["stones"][0]; st["stage"] = "read"; save(sp, st)

    if st["stage"] == "read":
        mid = f"scrap-{T}-cost-" + NOW.strftime("%Y%m%d%H%M")
        r = run_readopen(mid, T)
        bad = [b for b in (r or {}).get("buckets", []) if b.get("status") != "readonly" or b.get("itemCount") != b.get("itemsExpected")]
        if not r or bad or len(r["buckets"]) != 10:
            log("read incomplete:", mid, [(b["store"], b["bucketName"], b.get("error")) for b in bad])
            st["read_fail"] = st.get("read_fail", 0) + 1; save(sp, st)
            if st["read_fail"] >= 6 and not DRY:
                human(f"gold-read-{T}", f"The {T} gold buckets could not be read in Bravo after several tries "
                      f"({', '.join(b['store'] + ' ' + b['bucketName'] for b in bad) or 'Bravo not answering'}).")
            return 0
        st["read_result"] = f"{BR}/results-scrap/{mid}.result.json"; st["stage"] = "split"; save(sp, st)

    if st["stage"] == "split":
        g, s = st["gold"], st["stones"]
        maps = []
        for x in STORES:
            maps += ["--map", f"{x}:{T} GOLD:gold", "--map", f"{x}:{T} GOLD WITH STONES:stones"]
        r = subprocess.run(["/usr/bin/python3", f"{PM}/bin/build_month_split.py", "--root", P, "--month", T,
                            "--gold-net", "%.2f" % g["net"], "--stones-net", "%.2f" % s["net"],
                            "--gold-premelt", str(g["premelt_dwt"]), "--stones-premelt", str(s["premelt_dwt"]),
                            "--readonly-result", st["read_result"]] + maps, capture_output=True, text=True)
        if r.returncode != 0:
            log("split failed:", r.stdout[-500:], r.stderr[-500:]); return 1
        res = json.loads(open(st["read_result"], encoding="utf-8-sig").read())
        man = json.load(open(f"{BR}/triggers-scrap/pending-approval/scrap-closeout-{T}.json"))
        rows, tot = [], [0.0, 0.0]
        wt = {"gold": 0.0, "stones": 0.0}
        for x in STORES:
            amt = sum(float(b["amountPaid"]) for b in man["buckets"] if b["store"] == x)
            cost = sum(float(b.get("itemCost") or 0) for b in res["buckets"] if b["store"] == x)
            rows.append((x, amt, cost)); tot[0] += amt; tot[1] += cost
        for b in res["buckets"]:
            wt["stones" if "STONES" in b["bucketName"] else "gold"] += float(b["liveWeightDwt"] or 0)
        names = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke", "WAY": "Waynesboro"}
        pct = lambda a, b: (a / b - 1) * 100 if b else 0
        lines = ["Store            Paid        Cost        Gross profit   Margin"]
        for x, a, c in rows:
            lines.append(f"{names[x]:<15} ${a:>10,.2f} ${c:>10,.2f} ${a - c:>11,.2f}   {((a - c) / a * 100 if a else 0):.1f}%")
        lines.append(f"{'Total':<15} ${tot[0]:>10,.2f} ${tot[1]:>10,.2f} ${tot[0] - tot[1]:>11,.2f}   {((tot[0] - tot[1]) / tot[0] * 100):.1f}%")
        wline = (f"Weight check: plain gold {wt['gold']:.1f} dwt in Bravo vs {g['premelt_dwt']:.1f} at Elemetal ({pct(wt['gold'], g['premelt_dwt']):+.1f}%), "
                 f"with stones {wt['stones']:.1f} vs {s['premelt_dwt']:.1f} ({pct(wt['stones'], s['premelt_dwt']):+.1f}%).")
        warn = "" if abs(pct(wt["gold"], g["premelt_dwt"])) <= 10 and abs(pct(wt["stones"], s["premelt_dwt"])) <= 10 else \
            "\nOne lot is more than 10% off what Elemetal weighed - worth a look before posting.\n"
        token = f"GC-{T}"
        mon = dt.date(int(T[:4]), int(T[5:]), 1).strftime("%B %Y")
        subject = f"Gold closeout {mon} - ${tot[0]:,.2f} ready to post [{token}]"
        body = (f"Elemetal paid ${g['net']:,.2f} for the plain gold and ${s['net']:,.2f} for the gold with stones.\n\n"
                + "\n".join(lines) + f"\n\n{wline}\n{warn}\nReply POST to close these in Bravo (runs in store hours). Reply HOLD to pause.\n")
        rev = f"{PM}/reviews/{T}_allocations_REVIEW.csv"
        with open(rev, "a") as fh:
            fh.write(",,,,,,,\nSETTLEMENTS,,,,,,,\n")
            for k, x in (("Gold (Karat)", g), ("Gold with stones (Stone Removal)", s)):
                fh.write(f"{k}:,{x['invoice']},{x['lot']},{x['date']},\"gross ${x['gross']:,.2f}\",\"net wire ${x['net']:,.2f} ({x['wire']})\",pre-melt {x['premelt_dwt']} dwt,mail row {x['mail_rowid']}\n")
            fh.write(f"Weight check:,\"{wline}\",,,,,,\n,,,,,,,\nGROSS PROFIT BY STORE,,,,,,,\nStore,Settlement $,Item cost $,Gross profit $,Margin %,,,\n")
            for x, a, c in rows:
                fh.write(f"{x},{a:.2f},{c:.2f},{a - c:.2f},{((a - c) / a * 100 if a else 0):.1f}%,,,\n")
        if not send_mail(subject, body):
            return 1
        st.update({"stage": "awaiting", "token": token, "sent_ts": NOW.timestamp(), "total": round(tot[0], 2),
                   "gp": round(tot[0] - tot[1], 2)})
        if not DRY:
            save(sp, st); changelog(f"{T}: split staged (${tot[0]:,.2f}, GP ${tot[0] - tot[1]:,.2f}); approval email sent [{token}].")
        return 0

    if st["stage"] in ("awaiting", "held"):
        v = find_reply(st["token"], st["sent_ts"])
        log("reply:", v)
        if v == "hold" and st["stage"] != "held":
            st["stage"] = "held"; save(sp, st); changelog(f"{T}: Joshua replied HOLD - not posting."); return 0
        if v != "post":
            if st["stage"] == "awaiting" and NOW.timestamp() - st["sent_ts"] > 10 * 86400 and not DRY:
                human(f"gold-approve-{T}", f"The {T} gold closeout email [{st['token']}] is waiting for your POST or HOLD reply.")
            return 0
        st["stage"] = "posting"; st["approved_at"] = NOW.isoformat(timespec="minutes"); save(sp, st)

    if st["stage"] == "posting":
        if not store_hours():
            log("approved; outside store hours - will post next run in hours"); return 0
        if DRY:
            log("[dry] would post now"); return 0
        man = json.load(open(f"{BR}/triggers-scrap/pending-approval/scrap-closeout-{T}.json"))
        done = set(tuple(x) for x in st.get("done", []))
        left = [b for b in man["buckets"] if (b["store"], b["bucketName"]) not in done]
        if st.get("attempts_day") != str(NOW.date()):
            st["attempts_day"], st["attempts"] = str(NOW.date()), 0
        if st["attempts"] >= 3:
            log("3 posting attempts today - try again next store day"); return 0
        st["attempts"] += 1; save(sp, st)
        mid = f"scrap-closeout-{T}-" + NOW.strftime("%Y%m%d%H%M")
        r = run_close(mid, left)
        for b in (r or {}).get("buckets", []):
            if b.get("verified") and b.get("status") in ("closed", "already-closed"):
                done.add((b["store"], b["bucketName"]))
            elif "MISMATCH" in (b.get("error") or "") and "WEIGHT" in b.get("error", ""):
                send_mail(f"Gold closeout {T}: {b['store']} {b['bucketName']} changed [{st['token']}-W]",
                          f"{b['store']} {b['bucketName']} weighs differently in Bravo than when you approved it, so it was not posted. "
                          "Everything else is posting normally. Reply POST to the next closeout email once it is rebuilt.")
                human(f"gold-weight-{T}-{b['store']}", f"{b['store']} {b['bucketName']} weight changed after approval; not posted.")
        st["done"] = sorted(done); save(sp, st)
        if len(done) == len(man["buckets"]):
            rev = f"{PM}/reviews/{T}_allocations_REVIEW.csv"
            open(rev, "a").write(f"STATUS:,\"CLOSED {NOW:%Y-%m-%d %H:%M} ET by the native closeout agent after Joshua's POST reply. "
                                 f"All {len(done)} buckets closed and read back. ${st['total']:,.2f} posted.\",,,,,,\n")
            os.replace(rev, f"{PM}/reviews/{T}_allocations_CLOSED.csv")
            os.makedirs(f"{BR}/triggers-scrap/pending-approval/_done", exist_ok=True)
            shutil.move(f"{BR}/triggers-scrap/pending-approval/scrap-closeout-{T}.json", f"{BR}/triggers-scrap/pending-approval/_done/")
            st["stage"] = "closed"; save(sp, st)
            send_mail(f"Re: Gold closeout {T} - posted [{st['token']}-done]",
                      f"All 10 gold buckets for {T} are closed in Bravo: ${st['total']:,.2f}, matching both Elemetal payments.")
            changelog(f"{T}: all {len(done)} gold buckets CLOSED in Bravo, ${st['total']:,.2f}.")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
