#!/usr/bin/env python3
"""chekkit_review_backfill.py --store ROA --from YYYY-MM-DD --to YYYY-MM-DD [--send] [--no-pull]

One-store review-invitation catch-up (added 2026-10-21, additive; reuses chekkit_review_invites.py unchanged).
Why: Roanoke trails The PawnShop on Google review volume (~292 vs ~727) while rating is equal; the weekly program
only reaches the prior week's customers and was dark mid-Sept..10/5. This invites the store's customers from an
older window. Same rules as the weekly job: Bravo `chekkit-invites-range` pull, only unusable phones dropped,
one invite per phone, Chekkit enforces one invitation per customer per year (409 = already invited, never retried),
<= 1 request/second. Default = PREVIEW (nothing sent). No Slack post, no Brevo import (Rule: no unapproved posts).
Writes fleet/state/review_backfill_<store>_<from>_<to>.json.
"""
import datetime as dt, json, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_review_invites as W  # noqa: E402

def arg(n):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else None

def main():
    code = (arg("--store") or "").upper(); frm, to = arg("--from"), arg("--to")
    names = dict(W.STORES)
    if code not in names or not frm or not to:
        print("usage: --store CODE --from D --to D [--send] [--no-pull]"); return 2
    send = "--send" in sys.argv
    key = "%s..%s" % (frm, to)
    out = os.path.join(W.OS_DIR, "fleet", "state", "review_backfill_%s_%s_%s.json" % (code, frm, to))
    prior = json.load(open(out)) if os.path.exists(out) else {}
    if send and prior.get("sent_at"):
        print("already sent", prior["sent_at"]); return 0
    t0 = time.time()
    if "--no-pull" not in sys.argv:
        r = subprocess.run(["/bin/bash", os.path.join(W.OS_DIR, "bin", "bravo_pull.sh"), "chekkit-invites-range", key, code,
                            "review-backfill-%s" % dt.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")], capture_output=True, text=True, timeout=7500)
        print("pull rc", r.returncode, (r.stdout or "")[-300:], (r.stderr or "")[-300:])
        since = t0 - 60
    else:
        since = time.time() - 3 * 86400
    rows = W.load(code, since)
    tok = W.token(code)
    if not rows or not tok:
        print("no data" if not rows else "no token"); return 1
    seen, todo, dropped = set(), [], 0
    for r in rows:
        p = W.phone10(r.get("phone"))
        if not p:
            dropped += 1; continue
        if p in seen:
            continue
        seen.add(p)
        nm = " ".join(w.capitalize() for w in (r.get("first_name") or "").split()) or "Valley Pawn customer"
        b = {"name": nm, "phone": p}
        em = (r.get("email") or "").strip()
        if "@" in em and "dnc" not in em.lower():
            b["email"] = em
        todo.append(b)
    c = {"rows": len(rows), "unique_phones": len(todo), "dropped_unusable": dropped, "sent": 0, "already": 0, "failed": 0}
    if send:
        for b in todo:
            s = W.invite(tok, b)
            if 200 <= s < 300: c["sent"] += 1
            elif s == 409: c["already"] += 1
            else: c["failed"] += 1
            time.sleep(1.1)
    res = {"store": names[code], "window": key, "mode": "SEND" if send else "PREVIEW", "counts": c,
           "examples": ["%s ...%s" % (b["name"].split()[0], b["phone"][-4:]) for b in todo[:3]]}
    if send:
        res["sent_at"] = dt.datetime.now(W.ET).isoformat(timespec="seconds")
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(res))
    if send and c["failed"]:
        W.ledger("Roanoke review catch-up %s: %d invitations did not go through." % (key, c["failed"]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
