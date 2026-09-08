#!/usr/bin/env python3
"""
Publish _lane_c/manifest_2026-09-13.json (vp-community-weekly, week of Sept 13-19).

Rule-12 collision guard before every schedule call: pulls live Publer /posts for the
manifest's date window and skips (does not double-book) any slot whose exact
account+timestamp already has something scheduled -- the same landmine
vp-deal-reels-weekly hit against this same lane on 2026-09-07 (Waynesboro FB 11:00am 9/9).
Text-only posts, no media upload needed (community lane is text-only by design).
"""
import json, sys, time, datetime as dt
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from publer_client import PublerClient, PublerError

MANIFEST = Path(__file__).with_name("manifest_2026-09-13.json")
RESULTS = Path(__file__).with_name("manifest_2026-09-13_publish_results.json")


def load_live_window(p, frm, to):
    """acct_id -> set of scheduled_at[:16] strings already live, for collision checks."""
    by_acct = {}
    for st in ("scheduled", "published", "completed"):
        try:
            data = p.get("/posts", params={"from": frm, "to": to, "state": st, "limit": "200"})
            posts = data.get("posts", data) if isinstance(data, dict) else (data or [])
            for po in posts:
                when = (po.get("scheduled_at") or po.get("scheduledAt") or "")[:16]
                ids = po.get("accounts") or po.get("account_ids") or []
                if isinstance(ids, list):
                    ids = [i.get("id", i) if isinstance(i, dict) else i for i in ids]
                for aid in ids:
                    by_acct.setdefault(aid, set()).add(when)
        except Exception as e:
            print(f"  (live window load {st} failed: {e})")
    return by_acct


def main():
    manifest = json.loads(MANIFEST.read_text())
    items = manifest["items"]
    p = PublerClient()

    prior = {}
    if RESULTS.exists():
        prior = {r["id"]: r for r in json.loads(RESULTS.read_text()).get("results", [])}

    live_by_acct = load_live_window(p, "2026-09-12", "2026-09-21")

    results_by_id = dict(prior)

    def checkpoint():
        RESULTS.write_text(json.dumps(
            {"ran_at": dt.datetime.now().isoformat(), "results": list(results_by_id.values())},
            indent=2))

    budget_deadline = time.time() + 130  # leave headroom under the ~150-180s tool-call cap
    for it in items:
        rid = it["id"]
        if results_by_id.get(rid, {}).get("status") in ("SCHEDULED", "PENDING_VERIFY"):
            continue
        if time.time() > budget_deadline:
            print("TIME BUDGET REACHED — stopping this pass, re-run to continue.")
            break

        store_keys = it["store_keys"]
        acct_ids = [p.account_id(k) for k in store_keys]
        when16 = it["scheduled_at"][:16]
        collided = [k for k, aid in zip(store_keys, acct_ids) if when16 in live_by_acct.get(aid, set())]
        if collided:
            new_when = None
            base = dt.datetime.fromisoformat(it["scheduled_at"])
            bumped = base + dt.timedelta(minutes=20)
            bumped_s = bumped.isoformat()
            if bumped_s[:16] not in live_by_acct.get(acct_ids[0], set()):
                new_when = bumped_s
            if new_when:
                print(f"COLLISION {rid} @ {it['scheduled_at']} (accounts {collided}) -> bumped to {new_when}")
                it = dict(it, scheduled_at=new_when)
            else:
                results_by_id[rid] = {"id": rid, "status": "COLLISION_UNRESOLVED", "accounts": collided}
                print(f"COLLISION_UNRESOLVED: {rid}")
                checkpoint()
                continue

        time.sleep(1)
        try:
            job = p.schedule_post(text=it["caption"], store_keys=store_keys,
                                   scheduled_at=it["scheduled_at"])
            jid = job.get("job_id", "")
            # Don't block on wait_for_job here -- Publer job status polling has been
            # slower than the tool-call time budget allows. job_id is recorded and a
            # separate live /posts check (Rule 12) verifies actual outcome afterward.
            results_by_id[rid] = {
                "id": rid, "store_keys": store_keys, "format_id": it.get("_format_id"),
                "hook": it.get("_hook"), "scheduled_at": it["scheduled_at"],
                "job_id": jid, "status": "PENDING_VERIFY",
            }
            print(f"SUBMITTED: {rid} @ {it['scheduled_at']} job={jid}")
        except PublerError as e:
            results_by_id[rid] = {"id": rid, "status": "ERROR", "error": str(e)[:300]}
            print(f"ERROR: {rid}: {e}")
        checkpoint()

    results = list(results_by_id.values())
    n_ok = sum(1 for r in results if r.get("status") == "SCHEDULED")
    n_left = sum(1 for it in items if results_by_id.get(it["id"], {}).get("status") != "SCHEDULED")
    print(f"\n=== {n_ok}/{len(items)} scheduled, {n_left} remaining ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
