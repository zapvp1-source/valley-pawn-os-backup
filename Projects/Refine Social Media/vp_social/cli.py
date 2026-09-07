"""`python3 -m vp_social <command>` — every command is safe to re-run."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from . import config, ledger, report, plan as planner, publish


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="vp_social")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sync", help="pull Publer into the ledger"); s.add_argument("--back", type=int, default=21); s.add_argument("--forward", type=int, default=30)
    r = sub.add_parser("recap", help="Weekly Social Recap (Slack body on stdout, exit 2 = withhold)"); r.add_argument("--days", type=int, default=7)
    sub.add_parser("quota", help="per-account 7-day counts (JSON)")
    d = sub.add_parser("digest", help="Friday digest"); d.add_argument("--days", type=int, default=7)
    m = sub.add_parser("month", help="Month in review"); m.add_argument("yyyy_mm")
    pf = sub.add_parser("postflight"); pf.add_argument("plan_id")
    p = sub.add_parser("plan", help="build the week's plan"); p.add_argument("--week", required=True); p.add_argument("--deals", default=None); p.add_argument("--seed", type=int, default=None)
    pub = sub.add_parser("publish", help="publish a plan (THE only writer)"); pub.add_argument("plan_path"); pub.add_argument("--live", action="store_true", help="override DRY_RUN file"); pub.add_argument("--dry-run", action="store_true")
    v = sub.add_parser("validate", help="QA a plan without publishing"); v.add_argument("plan_path")
    sub.add_parser("status", help="ledger status")

    a = ap.parse_args(argv)
    if a.cmd == "sync":
        print(json.dumps(ledger.sync(a.back, a.forward))); return 0
    if a.cmd == "recap":
        return report.emit(report.recap, a.days)
    if a.cmd == "quota":
        return report.emit(report.quota)
    if a.cmd == "digest":
        return report.emit(report.digest, a.days)
    if a.cmd == "month":
        return report.emit(report.month, a.yyyy_mm)
    if a.cmd == "postflight":
        return report.emit(report.postflight, a.plan_id)
    if a.cmd == "plan":
        pl = planner.build(a.week, Path(a.deals) if a.deals else None, seed=a.seed)
        print(planner.summary(pl)); print(f"-> {config.PLANS_DIR / (pl['plan_id'] + '.json')}"); return 0
    if a.cmd == "validate":
        pl = json.loads(Path(a.plan_path).read_text())
        errs = publish.plan_level_checks(pl)
        missing = [(s["slot_id"], acc) for s in pl["slots"] for acc, cap in s["captions"].items() if not cap and not s.get("deferred")]
        caps = []
        for s in pl["slots"]:
            for acc, cap in s["captions"].items():
                if cap:
                    probs = publish.qa_caption(cap, acc, s.get("kind", "photo"), 8)
                    if probs:
                        caps.append(f"{s['slot_id']}/{acc}: {'; '.join(probs)}")
        print(json.dumps({"plan_level": errs, "captions_missing": missing, "caption_problems": caps}, indent=1))
        return 0 if not (errs or caps) else 1
    if a.cmd == "publish":
        dry = True if a.dry_run else (False if a.live else None)
        res = publish.publish_plan(Path(a.plan_path), dry_run=dry)
        print(json.dumps({k: v for k, v in res.items() if k != "items"}, indent=1))
        for it in res["items"]:
            print(f"  {it['status']:10s} {it['slot']}/{it['account']} {it.get('reason','')}")
        return 0 if not res["blocked"] and res["failed"] == 0 else 1
    if a.cmd == "status":
        with ledger.connect() as con:
            n = con.execute("select count(*) from posts").fetchone()[0]
            runs = con.execute("select command, ok, finished_at, summary from runs order by run_id desc limit 5").fetchall()
        print(f"ledger: {config.LEDGER_PATH} posts={n} last_sync={ledger.last_sync_at()} dry_run={config.dry_run_enabled()}")
        for r in runs:
            print(f"  {r[2]} {r[0]:9s} ok={r[1]} {r[3][:120]}")
        return 0
    return 2
