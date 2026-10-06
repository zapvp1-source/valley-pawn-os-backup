#!/usr/bin/env python3
"""chekkit_review_invites.py [--send] [--from D --to D] [--no-pull] — native chekkit-weekly-review-requests (2026-10-05).

Joshua 10/5: "with new API functionality can't we just use Chekkit for now and make sure it's firing." Review
invitations had effectively stopped (0 per store since mid-September — the Cowork task drove the Chekkit website and
died with the Mac connector). Same steps as the SKILL, Chekkit's own API instead of its website:
  1 Bravo `chekkit-invites-range` for the prior 7 days (Tue..Mon), all 5 stores, via bin/bravo_pull.sh
  2 Bravo data stays pure (Joshua 10/5): no DNC/DNT filtering — Chekkit and Brevo manage opt-outs. Only unusable
    phone numbers (<10 digits, all zeros, bad area codes) are skipped; normalize to 10 digits; one invite per phone
  3 POST https://api.chekkit.io/v1/review-invitations {name, phone[, email]} with THAT store's token
    (Keychain vp-chekkit-token-<CODE>). Chekkit enforces one invitation per customer per year (409 = already
    invited — counted, never retried). <= 1 request/second per token (limit is 60/min).
  4 Post A to #chekkit-updates (C0B0FQZ4FS8) in the SKILL's format (+ already-invited line); DM Joshua the same.
Default is a PREVIEW (counts + masked examples, nothing sent). --send sends. A store with no data is skipped and
named; if every store has no data nothing is sent and one ledger line is written.
Phase 4 (Brevo): EVERY customer (email, else phone as SMS contact; Brevo manages do-not-contact, Bravo DNT -> smsBlacklisted) -> lists 3 (master) + 13 ('monthly'), FIRSTNAME/LASTNAME/STORE, post to #email-campaigns; new contacts get the welcome email from brevo-welcome."""
import datetime as dt, glob, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack  # noqa: E402

AGENT = "chekkit-weekly-review-requests"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BRAVO = os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STATE = os.path.join(OS_DIR, "fleet", "chekkit_review_invites_state.json")
CH, JOSHUA = "C0B0FQZ4FS8", "U03BB52MDSA"
STORES = [("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke"), ("WAY", "Waynesboro")]
BAD_AREA = {"000", "111", "555", "826", "880", "999"}


def arg(n):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else None


def ledger(s):
    with open(LEDGER, "a") as fh:
        fh.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, s))


def token(code):
    return subprocess.run(["security", "find-generic-password", "-s", "vp-chekkit-token-" + code, "-w"], capture_output=True, text=True).stdout.strip()


def phone10(p):
    d = re.sub(r"\D", "", p or "")
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    if len(d) != 10 or d[0] in "01" or d[:3] in BAD_AREA or len(set(d)) == 1:
        return None
    return d


def load(code, since):
    c = [p for p in glob.glob(os.path.join(BRAVO, "output", "*_%s_chekkit-invites-range.csv" % code)) if os.path.getmtime(p) >= since]
    if not c:
        return None
    import csv
    with open(max(c, key=os.path.getmtime), newline="", errors="replace") as fh:
        return list(csv.DictReader(fh))


def invite(tok, body):
    req = urllib.request.Request("https://api.chekkit.io/v1/review-invitations", data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json", "User-Agent": "ValleyPawnOps/1.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After") or 5)); continue
            return e.code
        except Exception:
            time.sleep(3)
    return 0


BK = None


def brevo(path, payload=None, method=None):
    global BK
    BK = BK or open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
    req = urllib.request.Request("https://api.brevo.com/v3" + path, data=json.dumps(payload).encode() if payload is not None else None,
                                 method=method or ("POST" if payload is not None else "GET"),
                                 headers={"api-key": BK, "accept": "application/json", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        b = r.read(); return json.loads(b) if b else {}


def brevo_import(contacts):
    """Upsert EVERY customer into lists 3 (master) + 13 ('monthly') with FIRSTNAME/LASTNAME/STORE/SMS. Email is the key
    when there is one; phone-only customers are added as SMS contacts. Opt-outs are Brevo's job (Joshua 10/5:
    "Brevo and Chekkit manage the opt-outs, the Bravo data remains pure") — nothing is filtered or flagged from Bravo. Never blanks data Brevo already has. Returns how many were brand-new contacts."""
    new = 0
    for key, v in contacts.items():
        attrs = {k: x for k, x in (("FIRSTNAME", v["first"]), ("LASTNAME", v["last"]), ("STORE", v["store"]), ("SMS", v["sms"])) if x}
        body = {"attributes": attrs, "listIds": [3, 13], "updateEnabled": True}
        if v["email"]:
            body["email"] = v["email"]
        try:
            r = brevo("/contacts", body)
            new += 1 if r.get("id") else 0
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:200]
            try:
                if "SMS" in msg or "sms" in msg or "phone" in msg:   # number already on another contact
                    if v["email"]:
                        attrs.pop("SMS", None); brevo("/contacts", dict(body, attributes=attrs))
                    else:
                        brevo("/contacts/%s?identifierType=phone_id" % urllib.parse.quote(v["sms"]),
                              {"attributes": {k: x for k, x in attrs.items() if k != "SMS"}, "listIds": [3, 13]}, "PUT")
            except urllib.error.HTTPError:
                pass
        time.sleep(0.15)
    return new


def main():
    send = "--send" in sys.argv
    today = dt.datetime.now(ET).date()
    to = dt.date.fromisoformat(arg("--to")) if arg("--to") else today - dt.timedelta(days=1)
    frm = dt.date.fromisoformat(arg("--from")) if arg("--from") else to - dt.timedelta(days=6)
    st = json.load(open(STATE)) if os.path.exists(STATE) else {}
    key = "%s..%s" % (frm, to)
    if send and key in st.get("sent_windows", []):
        print("already sent for", key); return 0
    t0 = time.time()
    if "--no-pull" not in sys.argv:
        subprocess.run(["/bin/bash", os.path.join(OS_DIR, "bin", "bravo_pull.sh"), "chekkit-invites-range", key,
                        ",".join(c for c, _ in STORES), "chekkit-weekly-%s" % dt.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")],
                       capture_output=True, text=True, timeout=7500)
        since = t0 - 60
    else:
        since = time.time() - 3 * 86400
    # a store that "succeeds" with zero rows is the silent-zero failure this SKILL warns about — re-pull it once
    zero = [c for c, _ in STORES if not (load(c, since) or [])]
    if zero and "--no-pull" not in sys.argv:
        subprocess.run(["/bin/bash", os.path.join(OS_DIR, "bin", "bravo_pull.sh"), "chekkit-invites-range", key, ",".join(zero),
                        "chekkit-weekly-retry-%s" % dt.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")], capture_output=True, text=True, timeout=7500)
    res, missing, examples = {}, [], {}
    emails, per_store_email = {}, {}
    for code, name in STORES:
        rows = load(code, since)
        tok = token(code)
        if not rows or not tok:
            missing.append(name); continue
        seen, todo, dropped = set(), [], 0
        for r in rows:
            email = (r.get("email") or "").strip()
            if re.search(r"dnc|do not contact", email, re.I):
                email = ""
            p = phone10(r.get("phone"))
            if not p:                                   # only an unusable number is dropped — Chekkit manages opt-outs (Joshua 10/5)
                dropped += 1; continue
            if p in seen:
                continue
            seen.add(p)
            nm = " ".join(w.capitalize() for w in (r.get("first_name") or "").split()) or "Valley Pawn customer"
            body = {"name": nm, "phone": p}
            if email and "@" in email:
                body["email"] = email
            todo.append(body)
        for r in rows:   # Brevo gets EVERY customer on the list (Joshua 10/5: Brevo manages do-not-contact itself)
            em = (r.get("email") or "").strip().lower()
            em = em if re.match(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", em) else ""
            ph = phone10(r.get("phone"))
            ckey = em or ("sms:+1" + ph if ph else "")
            if not ckey:
                continue
            parts = (r.get("first_name") or "").split() + (r.get("last_name") or "").split()
            emails.setdefault(ckey, {"email": em, "sms": ("+1" + ph) if ph else "", "store": name,
                                    "first": " ".join(w.capitalize() for w in parts[:1]),
                                    "last": " ".join(w.capitalize() for w in parts[1:]),
                                    "dnt": bool((r.get("dnt") or "").strip())})
            per_store_email[name] = per_store_email.get(name, 0) + 1
        examples[name] = ["%s ...%s" % (b["name"].split()[0], b["phone"][-4:]) for b in todo[:2]]
        counts = {"queued": len(todo), "dropped": dropped, "sent": 0, "already": 0, "failed": 0}
        if send:
            for b in todo:
                s = invite(tok, b)
                if 200 <= s < 300: counts["sent"] += 1
                elif s == 409: counts["already"] += 1
                else: counts["failed"] += 1
                time.sleep(1.1)
        res[name] = counts
    print("window %s | %s" % (key, "SEND" if send else "PREVIEW (nothing sent)"))
    for n, c in res.items():
        print("  %-13s %s  e.g. %s" % (n, json.dumps(c), ", ".join(examples.get(n, []))))
    if missing:
        print("  no data/token:", ", ".join(missing))
    print("  Brevo contacts (everyone with an email or phone):", dict(per_store_email), "unique:", len(emails), "email:", sum(1 for v in emails.values() if v["email"]), "phone-only:", sum(1 for v in emails.values() if not v["email"]))
    if not res:
        ledger("Weekly review invites for %s not sent — no store returned customer data." % key); return 1
    if not send:
        return 0
    lines = ["Weekly Chekkit Review Invites"] + ["• %s: %d" % (n, res[n]["sent"]) for _, n in STORES if n in res]
    lines.append("Total messages: %d" % sum(c["sent"] for c in res.values()))
    already = sum(c["already"] for c in res.values())
    if already:
        lines.append("Already invited within the last year (skipped by Chekkit): %d" % already)
    if missing:
        lines.append("No customer list this week: %s" % ", ".join(missing))
    os.environ["VP_TASK"] = AGENT
    vp_slack.post(CH, "\n".join(lines))
    # PHASE 4 — Brevo: add the same customers' emails to the master list (3) and the "monthly" list (13)
    try:
        new_n = brevo_import(emails)
        vp_slack.post("C0APR5WUL2Z", "Weekly Email Upload to Brevo (tag: monthly)\n" +
                      "\n".join("• %s: %d" % (n, per_store_email.get(n, 0)) for _, n in STORES) + "\nTotal new emails added: %d" % new_n)
    except Exception as e:
        vp_slack.post("C0APR5WUL2Z", "Weekly Email Upload to Brevo did not go through this week.")
        ledger("Weekly Brevo email upload from the review-invite list failed (%s)." % str(e)[:120])
    fails = sum(c["failed"] for c in res.values())
    if fails:
        ledger("Weekly review invites %s: %d invitations did not go through." % (key, fails))
    st.setdefault("sent_windows", []).append(key)
    json.dump(st, open(STATE, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
