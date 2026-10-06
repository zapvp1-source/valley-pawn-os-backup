#!/usr/bin/env python3
"""brevo_welcome.py [--render] — native brevo-welcome-new-contacts (daily 10:00, 2026-10-05).
Same steps as the SKILL: contacts created in the last 4 days, not WELCOMED, not blacklisted, with an email
-> POST /smtp/email templateId 72 -> immediately PUT WELCOMED=true (per contact, so an interrupted run never
double-sends) -> re-read up to 5 to confirm the flag persisted -> one EFFICIENCY_LOG entry if anyone was
welcomed. Silent when nobody is new."""
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

K = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
API = "https://api.brevo.com/v3"
LOG = os.path.expanduser("~/Documents/Claude/Projects/Email Refinement/EFFICIENCY_LOG.md")
LEDGER = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md")
DRY = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS/fleet/DRY_RUN.json")


def req(method, path, body=None):
    for a in range(6):
        r = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None, method=method,
                                   headers={"api-key": K, "accept": "application/json", "content-type": "application/json"})
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                b = resp.read()
                return resp.status, (json.loads(b) if b else {})
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(4 * 2 ** a)
                continue
            return e.code, {"error": e.read().decode()[:200]}
    return 429, {}


def main():
    render = "--render" in sys.argv
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=4)
    cands, offset = [], 0
    while True:
        st, r = req("GET", "/contacts?limit=100&offset=%d&sort=desc" % offset)
        if st != 200:
            raise SystemExit("contacts read failed %s" % st)
        page = r.get("contacts", [])
        old = False
        for c in page:
            created = dt.datetime.fromisoformat(c["createdAt"].replace("Z", "+00:00"))
            if created < cutoff:
                old = True
                continue
            if c.get("email") and not c.get("emailBlacklisted") and not (c.get("attributes") or {}).get("WELCOMED"):
                cands.append(c["email"])
        if old or len(page) < 100:
            break
        offset += 100
    print("candidates:", len(cands))
    if render or not cands:
        return 0
    if os.path.exists(DRY) and json.load(open(DRY)).get("active"):
        print("publish guard active — nothing sent")
        return 0
    sent, failed = [], []
    for e in cands:
        st, resp = req("POST", "/smtp/email", {"templateId": 72, "to": [{"email": e}]})
        if st not in (200, 201, 202):
            print("send failed %s: %s" % (st, resp.get("error", "")[:200]))
            failed.append(e)
            continue
        req("PUT", "/contacts/" + urllib.parse.quote(e), {"attributes": {"WELCOMED": True}})
        sent.append(e)
        time.sleep(0.5)
    bad = 0
    for e in sent[:5]:
        st, c = req("GET", "/contacts/" + urllib.parse.quote(e))
        if not (c.get("attributes") or {}).get("WELCOMED"):
            bad += 1
    if sent:
        with open(LOG, "a") as fh:
            fh.write("\n## %s (brevo-welcome-new-contacts, native)\nWelcomed: %d new contacts | Skipped (failed): %d | flag check: %d/%d ok\n"
                     % (dt.date.today(), len(sent), len(failed), min(5, len(sent)) - bad, min(5, len(sent))))
    if bad:
        with open(LEDGER, "a") as fh:
            fh.write("| %s (native) | brevo-welcome-new-contacts | Welcome emails went out but the welcomed flag did not stick on %d contact(s) checked. | NEEDS_HUMAN: no | OPEN |\n"
                     % (dt.datetime.now().strftime("%Y-%m-%d %H:%M ET"), bad))
    print("welcomed %d, failed %d, flag-check bad %d" % (len(sent), len(failed), bad))
    return 0


if __name__ == "__main__":
    sys.exit(main())
