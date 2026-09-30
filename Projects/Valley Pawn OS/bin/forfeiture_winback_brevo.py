#!/usr/bin/env python3
"""
forfeiture_winback_brevo.py — Brevo side of the Forfeited-Loan Win-Back (host only; stdlib).

  forfeiture_winback_brevo.py import <RUN_DATE> [--dry]
      Upsert every row of runs/<RUN>/audience.csv into Brevo list 11 "Forfeited Loan Win-Back"
      with FORFEITED_LOAN / FORFEIT_STORE / LAST_FORFEIT_DATE (+FIRSTNAME/LASTNAME when blank).
      Contacts who have come back (dropped out of the audience) are REMOVED from list 11.
  forfeiture_winback_brevo.py send <RUN_DATE> [--dry]
      Only if Email Refinement/forfeiture_winback/SEND_APPROVED exists (Joshua's go).
      (a) weekly: new forfeiters (never touched) get Email 1 "Here whenever you need us".
      (b) first run of a month: the rolling pool (touched >= 28 days ago, not returned) gets the
          next email in rotation (Email 2 "How pawn protects your credit", then Email 1, ...).
      Each send = a fresh Brevo list + campaign built from VP Master Template 11, checked by
      brevo_preflight.py (mandatory), then sent. Touches are written back to state.json.
      Health brake: if the last win-back campaign's unsubscribe rate > 0.5%, the rolling pool is
      skipped that month (new forfeiters still get their first email).

Copy is the approved copy pack (Gold and Silver Markeitng/forfeited-winback-copy-pack.md) —
relationship-only, no discount, never names the lost item.
"""
import csv, datetime as dt, json, os, re, subprocess, sys, time, urllib.error, urllib.request

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents", "Claude", "Projects")
FWB = os.path.join(PROJ, "Email Refinement", "forfeiture_winback")
PREFLIGHT = os.path.join(PROJ, "Email Refinement", "brevo_preflight.py")
KEYF = os.path.join(HOME, ".config", "valley-pawn", "brevo_api_key")
API = "https://api.brevo.com/v3"
LIST_MASTER = 11
FOLDER = 1
TEMPLATE_MASTER = 11
SENDER = {"name": "Valley Pawn", "email": "hello@thevalleypawn.com"}
REPLY_TO = "jdavis@fcfpawn.com"
DRY = "--dry" in sys.argv

EMAILS = {
    1: {"subject": "Whenever you need us, we're here", "slug": "winback_here_for_you",
        "eyebrow": "STILL HERE FOR YOU", "headline": "No judgment. Just help when you need it.",
        "subline": "A pawn loan is the rare kind of borrowing that never follows you home — and our door is open the same as it always was.",
        "cta_label": "Find your store", "cta_url": "https://thevalleypawn.com/locations",
        "cta_sub": "Walk in any time — no appointment, no pressure.",
        "body": """<p style="margin:0 0 16px;">Hey there,</p>
<p style="margin:0 0 16px;">We wanted to reach out for one simple reason: to say the door at Valley Pawn is always open to you — same as it's ever been.</p>
<p style="margin:0 0 16px;">Sometimes a loan works out one way, sometimes another. Either way, you walked out that day with what you needed — and that's exactly what we're here for. There's nothing to feel funny about, and nothing to make up for.</p>
<p style="margin:0 0 8px;"><strong>A pawn loan is one of the most honest ways to borrow there is:</strong></p>
<ul style="margin:0 0 16px; padding-left:20px;">
<li style="margin:0 0 6px;">No credit check, and it never touches your credit score.</li>
<li style="margin:0 0 6px;">No collections, no debt that lingers — when a loan ends, it ends.</li>
<li style="margin:0 0 6px;">A fair, straight look at what you bring in, every time.</li>
</ul>
<p style="margin:0 0 16px;">So whether you ever need a hand again, or you just want to come browse and see what's new, we'd be glad to see you. You're always welcome here.</p>
<p style="margin:0 0 4px;">Warmly,</p>
<p style="margin:0;">Your Valley Pawn family</p>"""},
    2: {"subject": "The one loan that can't hurt your credit", "slug": "winback_protects_credit",
        "eyebrow": "GOOD TO KNOW", "headline": "The loan that can't hurt your credit",
        "subline": "Most people don't realize a pawn loan is the safest borrowing they have access to. Here's why.",
        "cta_label": "See how it works", "cta_url": "https://thevalleypawn.com/how-pawn-loans-work",
        "cta_sub": "Two-minute read. No sign-in, no catch.",
        "body": """<p style="margin:0 0 16px;">A bank loan, a card, a payday advance — every one of them can follow you: a credit pull, a balance, a collections call if things go sideways.</p>
<p style="margin:0 0 16px;">A pawn loan doesn't work like that. You bring in something of value, we give you a fair loan against it, and the item sits safe with us. Pay it back and it's yours again. If life takes a different turn, the loan simply ends — <strong>no credit hit, no collections, nothing chasing you.</strong></p>
<p style="margin:0 0 16px;">That's not a loophole. That's the whole idea — borrowing that can't snowball on you. It's why folks across the Valley have trusted us for over a decade.</p>
<p style="margin:0 0 16px;">If you ever need it again, we're right here. Same fair look, same open door.</p>
<p style="margin:0;">— Your Valley Pawn family</p>"""},
}


def key():
    return open(KEYF).read().strip()


def req(method, path, body=None, tries=6):
    data = json.dumps(body).encode() if body is not None else None
    for a in range(tries):
        r = urllib.request.Request(API + path, data=data, method=method,
                                   headers={"api-key": key(), "Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw else {})
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(4 * (2 ** a)); continue
            return e.code, e.read().decode(errors="replace")
        except Exception as e:
            time.sleep(3); last = str(e)
    return 599, "network/rate-limit"


def log(*a):
    print(dt.datetime.now().strftime("%H:%M:%S"), *a, flush=True)


def load_state():
    return json.load(open(os.path.join(FWB, "state.json")))


def save_state(s):
    p = os.path.join(FWB, "state.json")
    json.dump(s, open(p + ".tmp", "w"), indent=1, default=str)
    os.replace(p + ".tmp", p)


def read_rows(run, name):
    p = os.path.join(FWB, "runs", run, name)
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


# ------------------------------------------------------------------ import
def do_import(run):
    rows = read_rows(run, "audience.csv")
    log(f"import: {len(rows)} audience rows -> list {LIST_MASTER}")
    ok = bad = 0
    for r in rows:
        attrs = {"FORFEITED_LOAN": True, "FORFEIT_STORE": r["FORFEIT_STORE"], "LAST_FORFEIT_DATE": r["LAST_FORFEIT_DATE"]}
        st, cur = req("GET", "/contacts/" + urllib.request.quote(r["EMAIL"]))
        if st == 200:
            a = cur.get("attributes", {})
            if not a.get("FIRSTNAME") and r["FIRSTNAME"]:
                attrs["FIRSTNAME"] = r["FIRSTNAME"]
            if not a.get("LASTNAME") and r["LASTNAME"]:
                attrs["LASTNAME"] = r["LASTNAME"]
            if cur.get("emailBlacklisted"):
                continue  # never re-subscribe anyone
        else:
            attrs["FIRSTNAME"], attrs["LASTNAME"] = r["FIRSTNAME"], r["LASTNAME"]
        body = {"email": r["EMAIL"], "attributes": attrs, "listIds": [LIST_MASTER], "updateEnabled": True}
        if DRY:
            ok += 1; continue
        st, res = req("POST", "/contacts", body)
        if st in (200, 201, 204):
            ok += 1
        else:
            bad += 1; log("  upsert failed", r["EMAIL"], st, str(res)[:160])
        time.sleep(0.12)
    # remove people who came back (in list 11 but no longer in the audience)
    keep = {r["EMAIL"].lower() for r in rows}
    removed = 0
    off = 0
    while True:
        st, res = req("GET", f"/contacts/lists/{LIST_MASTER}/contacts?limit=500&offset={off}")
        if st != 200:
            break
        cs = res.get("contacts", [])
        gone = [c["email"] for c in cs if c["email"].lower() not in keep]
        if gone and not DRY:
            for i in range(0, len(gone), 150):
                req("POST", f"/contacts/lists/{LIST_MASTER}/contacts/remove", {"emails": gone[i:i + 150]})
        removed += len(gone)
        if len(cs) < 500:
            break
        off += 500
    log(f"import done: upserted {ok}, failed {bad}, removed (came back) {removed}{' [DRY]' if DRY else ''}")
    return bad == 0


# ------------------------------------------------------------------ send
def build_html(n, run):
    st, t = req("GET", f"/smtp/templates/{TEMPLATE_MASTER}")
    if st != 200:
        raise SystemExit(f"cannot read master template {TEMPLATE_MASTER}: {st}")
    html = t["htmlContent"]
    e = EMAILS[n]
    fill = {"CAMPAIGN_SLUG": f"{e['slug']}_{run[:7]}", "HERO_EYEBROW": e["eyebrow"], "HERO_HEADLINE": e["headline"],
            "HERO_SUBLINE": e["subline"], "BODY_HTML": e["body"], "PRIMARY_CTA_LABEL": e["cta_label"],
            "PRIMARY_CTA_URL": e["cta_url"], "PRIMARY_CTA_SUB": e["cta_sub"], "SUBJECT_FALLBACK": e["subject"]}
    for k, v in fill.items():
        html = html.replace(f"[[{k}]]", v)
    left = set(re.findall(r"\[\[([A-Z_]+)\]\]", html)) - {"PRIMARY_CTA_SEP"}  # preflight auto-fixes SEP
    if left:
        raise SystemExit(f"unfilled markers in master template: {sorted(left)}")
    return html


def last_unsub_rate():
    st, res = req("GET", "/emailCampaigns?status=sent&limit=50&sort=desc")
    if st != 200:
        return None
    for c in res.get("campaigns", []):
        if c.get("name", "").startswith("Forfeiture Win-Back"):
            gs = c.get("statistics", {}).get("globalStats", {})
            dlv = gs.get("delivered") or 0
            return (gs.get("unsubscriptions", 0) / dlv) if dlv else None
    return None


def send_group(run, emails, n, label):
    if not emails:
        log(f"send {label}: nobody to send"); return []
    name = f"Forfeiture Win-Back — {label} — {run}"
    if DRY:
        log(f"[DRY] would send Email {n} to {len(emails)} ({label})"); return []
    st, lst = req("POST", "/contacts/lists", {"name": name, "folderId": FOLDER})
    if st >= 300:
        raise SystemExit(f"list create failed {st} {lst}")
    lid = lst["id"]
    for i in range(0, len(emails), 150):
        req("POST", f"/contacts/lists/{lid}/contacts/add", {"emails": emails[i:i + 150]})
    time.sleep(5)
    body = {"name": name, "subject": EMAILS[n]["subject"], "sender": SENDER, "replyTo": REPLY_TO,
            "htmlContent": build_html(n, run), "recipients": {"listIds": [lid]},
            "inlineImageActivation": False, "mirrorActive": True}
    st, camp = req("POST", "/emailCampaigns", body)
    if st >= 300:
        raise SystemExit(f"campaign create failed {st} {camp}")
    cid = camp["id"]
    pf = subprocess.run(["/usr/bin/python3", PREFLIGHT, str(cid)], capture_output=True, text=True)
    log(f"preflight campaign {cid}: rc={pf.returncode}\n{pf.stdout[-1500:]}")
    if pf.returncode != 0:
        raise SystemExit(f"preflight FAILED for campaign {cid} — not sent")
    st, res = req("POST", f"/emailCampaigns/{cid}/sendNow")
    if st >= 300:
        raise SystemExit(f"sendNow failed {st} {res}")
    log(f"SENT campaign {cid} Email {n} to {len(emails)} ({label})")
    return [cid]


def do_send(run):
    if not os.path.exists(os.path.join(FWB, "SEND_APPROVED")):
        log("send skipped: SEND_APPROVED not present (waiting on Joshua's go)"); return True
    state = load_state()
    aud = {r["EMAIL"].lower(): r for r in read_rows(run, "audience.csv")}
    by_email = {}
    for c in state["customers"].values():
        if c.get("email") and c.get("status") == "target":
            by_email.setdefault(c["email"].lower(), []).append(c)
    today = dt.date.fromisoformat(run)
    new = [e for e in aud if e in by_email and all(not c["touches"] for c in by_email[e])]
    cids = send_group(run, new, 1, "New forfeits")
    for e in new:
        for c in by_email[e]:
            c["touches"].append({"date": run, "email": 1, "campaign": cids[0] if cids else None})
    # monthly rolling-pool touch (first run of the month)
    if today.day <= 7:
        rate = last_unsub_rate()
        if rate is not None and rate > 0.005:
            log(f"health brake: last win-back unsub rate {rate:.3%} > 0.5% — rolling pool skipped this month")
        else:
            pool = {}
            for e, cs in by_email.items():
                if e not in aud or e in new:
                    continue
                last = max((t["date"] for c in cs for t in c["touches"]), default=None)
                if last and (today - dt.date.fromisoformat(last)).days >= 28:
                    k = sum(len(c["touches"]) for c in cs)
                    pool.setdefault(2 if k % 2 == 1 else 1, []).append(e)
            for n, es in pool.items():
                ids = send_group(run, es, n, f"Monthly pool E{n}")
                for e in es:
                    for c in by_email[e]:
                        c["touches"].append({"date": run, "email": n, "campaign": ids[0] if ids else None})
    if not DRY:
        save_state(state)
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("import", "send"):
        sys.exit(__doc__)
    ok = do_import(sys.argv[2]) if sys.argv[1] == "import" else do_send(sys.argv[2])
    sys.exit(0 if ok else 1)
