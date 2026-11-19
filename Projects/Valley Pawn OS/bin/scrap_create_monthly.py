#!/usr/bin/env python3
"""scrap_create_monthly.py (2026-11-18) - native monthly gold-bucket creation (Joshua 11/17: Claude creates
the buckets on the 15th). Creates <N> GOLD / <N> GOLD WITH STONES at CUL HAR LEX ROA WAY for N = next month,
and re-asserts the current month's pair (existing names are skipped by the handler - self-heals a miss).
Runs scrap_closeout_run.sh with a createOnly manifest, retries failures once, logs to CHANGELOG, and on a
persistent failure adds ONE row to Life OS/HUMAN_QUEUE.md. Idempotent: a done-marker per month stops re-runs.
No Slack. Never touches items, weights, vendors or money."""
import json, os, subprocess, sys, datetime as dt
P = os.path.expanduser("~/Documents/Claude/Projects")
OS_ = f"{P}/Valley Pawn OS"; BR = f"{P}/Bravo Data Extraction"
STATE = f"{OS_}/fleet/state/scrap_create"; os.makedirs(STATE, exist_ok=True)
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
today = dt.date.today()
nxt = (today.replace(day=1) + dt.timedelta(days=32)).replace(day=1)
N, CUR = nxt.strftime("%Y-%m"), today.strftime("%Y-%m")
if len(sys.argv) > 1: N = sys.argv[1]
done = f"{STATE}/{N}.done"
if os.path.exists(done):
    print(f"{N} already created - nothing to do"); sys.exit(0)

def run(mid, pairs):
    man = {"id": mid, "createOnly": True, "buckets": [
        {"store": s, "bucketName": n, "occurrence": 0, "amountPaid": "0", "tenderType": "Cashiers Check"} for s, n in pairs]}
    json.dump(man, open(f"{BR}/triggers-scrap/{mid}.json", "w"), indent=1)
    subprocess.run(["bash", f"{OS_}/bin/scrap_closeout_run.sh", mid, "3600"])
    rp = f"{BR}/results-scrap/{mid}.result.json"
    if not os.path.exists(rp): return pairs, []
    r = json.loads(open(rp, encoding="utf-8-sig").read())
    ok = [(b["store"], b["bucketName"], b["status"]) for b in r["buckets"] if b.get("verified") and b["status"] in ("created", "exists")]
    okk = {(s, n) for s, n, _ in ok}
    return [p for p in pairs if p not in okk], ok

pairs = [(s, f"{m} {k}") for s in STORES for m in dict.fromkeys([CUR, N]) for k in ("GOLD", "GOLD WITH STONES")]
stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
left, ok1 = run(f"scrap-create-{N}-{stamp}", pairs)
ok2 = []
if left:
    left, ok2 = run(f"scrap-create-{N}-{stamp}-r1", left)
oks = ok1 + ok2
created = [f"{s} {n}" for s, n, st in oks if st == "created"]
line = (f"- {dt.date.today()} scrap-create-monthly: {N} gold buckets - created {len(created)}"
        f" ({', '.join(created) or 'none'}), already existed {sum(1 for o in oks if o[2]=='exists')}, failed {len(left)}"
        f"{' (' + ', '.join(f'{s} {n}' for s, n in left) + ')' if left else ''}.\n")
c = f"{OS_}/CHANGELOG.md"; t = open(c).read()
open(c, "w").write(f"## {dt.date.today()} (scrap gold buckets - native monthly creation)\n\n{line}\n" + t)
if left:
    open(f"{P}/Life OS/HUMAN_QUEUE.md", "a").write(
        f"| {dt.date.today()} | Valley Pawn - scrap gold | Could not create these gold buckets in Bravo after a retry: "
        f"{', '.join(f'{s} {n}' for s, n in left)}. It retries tomorrow automatically; if it is still listed after the 17th, "
        f"create them by hand in Bravo (Inventory > Scrap Refining Process > New Bucket). | OPEN |\n")
    print(line); sys.exit(1)
open(done, "w").write(line); print(line)
