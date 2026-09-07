#!/usr/bin/env python3
"""
MARKETING_OPEN_ITEMS — the ONE register for every marketing open item, decision, and login.

Created 2026-09-05 (AI Marketing umbrella plan, §5 contract 3). Replaces five unreconciled lists:
  presence_scorecard_latest.json → needs_joshua
  Gold and Silver Markeitng/ceo-briefing/actions.json
  Website/AUDIT_2026-08-22/weekly-history.json → still_open_from_baseline
  Refine Social Media/engagement_lane/RUN_LOG.md (open loops)
  the six 2026-09-05 department plans' "decisions Joshua owns" sections
Those files keep existing; from now on they are VIEWS of this register, never sources.

Usage (stdlib only, no deps):
  python3 open_items.py list [--owner joshua|claude] [--lane social|email|reputation|geo|blog|website|ebay|comms|all]
                             [--status open|resolved|all] [--aging N]
  python3 open_items.py add  --id ID --title "..." --owner joshua|claude --lane LANE --kind login|decision|fix|build
                             [--source "where it came from"] [--first-seen YYYY-MM-DD] [--note "..."]
  python3 open_items.py resolve --id ID --how "verified how" [--date YYYY-MM-DD]
  python3 open_items.py touch  --id ID            # sets last_checked = today, keeps status
  python3 open_items.py dedupe                    # reports title collisions (case-insensitive), changes nothing
  python3 open_items.py aging [--days 30]         # open items older than N days, oldest first
  python3 open_items.py slack [--owner joshua] [--max 8]   # plain-language block for a Slack post
  python3 open_items.py json                      # dump

Rules:
  - IDs are UPPER-KEBAB, stable forever. Never reuse a resolved ID for a new item.
  - `resolved_do_not_reopen` entries are facts, not tasks — an auditor that "finds" one must NOT add it.
  - Every write is atomic (temp file + rename). A backup of the prior file is kept as .bak-YYYYMMDD-HHMMSS.
  - No task may carry its own copy of an item; it reads this file and writes here.
"""
import argparse, json, os, sys, tempfile, shutil
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "MARKETING_OPEN_ITEMS.json")
LANES = {"social","email","reputation","geo","blog","website","ebay","comms","paid","all"}
KINDS = {"login","decision","fix","build"}

def load():
    with open(PATH, encoding="utf-8") as f:
        return json.load(f)

def save(d):
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    if os.path.exists(PATH):
        shutil.copy(PATH, PATH + f".bak-{ts}")
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".moi-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, PATH)
    # keep only the 10 newest backups
    baks = sorted(p for p in os.listdir(HERE) if p.startswith("MARKETING_OPEN_ITEMS.json.bak-"))
    for p in baks[:-10]:
        os.remove(os.path.join(HERE, p))

def today(): return date.today().isoformat()

def age_days(item):
    try: return (date.today() - date.fromisoformat(item["first_seen"])).days
    except Exception: return None

def find(d, id_):
    for it in d["items"]:
        if it["id"] == id_: return it
    return None

def cmd_list(a):
    d = load(); rows = []
    for it in d["items"]:
        if a.status != "all" and it["status"] != a.status: continue
        if a.owner and it["owner"] != a.owner: continue
        if a.lane and a.lane != "all" and it["lane"] != a.lane: continue
        if a.aging and (age_days(it) or 0) < a.aging: continue
        rows.append(it)
    rows.sort(key=lambda x: (x["owner"], x.get("first_seen","")))
    for it in rows:
        ad = age_days(it)
        print(f'{it["id"]:<26} {it["owner"]:<7} {it["lane"]:<10} {it["kind"]:<8} {it["status"]:<8} {ad if ad is not None else "?":>4}d  {it["title"]}')
    print(f"-- {len(rows)} item(s)")

def cmd_add(a):
    d = load()
    if find(d, a.id): sys.exit(f"ERROR: id {a.id} already exists (use touch/resolve)")
    if a.lane not in LANES: sys.exit(f"ERROR: lane must be one of {sorted(LANES)}")
    if a.kind not in KINDS: sys.exit(f"ERROR: kind must be one of {sorted(KINDS)}")
    low = a.title.strip().lower()
    for it in d["items"]:
        if it["title"].strip().lower() == low:
            sys.exit(f"ERROR: an item with this exact title exists as {it['id']} ({it['status']})")
    d["items"].append({
        "id": a.id, "title": a.title.strip(), "owner": a.owner, "lane": a.lane, "kind": a.kind,
        "status": "open", "first_seen": a.first_seen or today(), "last_checked": today(),
        "source": a.source or "", "note": a.note or "", "resolved": None,
    })
    save(d); print(f"added {a.id}")

def cmd_resolve(a):
    d = load(); it = find(d, a.id)
    if not it: sys.exit(f"ERROR: no item {a.id}")
    it["status"] = "resolved"; it["last_checked"] = today()
    it["resolved"] = {"date": a.date or today(), "how": a.how}
    save(d); print(f"resolved {a.id}")

def cmd_touch(a):
    d = load(); it = find(d, a.id)
    if not it: sys.exit(f"ERROR: no item {a.id}")
    it["last_checked"] = today(); save(d); print(f"touched {a.id}")

def cmd_dedupe(a):
    d = load(); seen = {}
    for it in d["items"]:
        k = it["title"].strip().lower()
        seen.setdefault(k, []).append(it["id"])
    dups = {k: v for k, v in seen.items() if len(v) > 1}
    if not dups: print("no exact-title duplicates"); return
    for k, v in dups.items(): print(f"DUP: {v} -> {k}")

def cmd_aging(a):
    d = load()
    rows = [it for it in d["items"] if it["status"] == "open" and (age_days(it) or 0) >= a.days]
    rows.sort(key=lambda x: x.get("first_seen",""))
    for it in rows: print(f'{age_days(it):>4}d  {it["id"]:<26} {it["owner"]:<7} {it["title"]}')
    print(f"-- {len(rows)} open item(s) >= {a.days} days")

def cmd_slack(a):
    d = load()
    rows = [it for it in d["items"] if it["status"] == "open" and (not a.owner or it["owner"] == a.owner)]
    rows.sort(key=lambda x: x.get("first_seen",""))
    logins = [r for r in rows if r["kind"] == "login"]
    decisions = [r for r in rows if r["kind"] == "decision"]
    out = []
    if logins:
        out.append(f"One-time logins still open ({len(logins)}):")
        for r in logins[:a.max]: out.append(f"• {r['title']} — open {age_days(r)} days")
    if decisions:
        out.append(f"Decisions waiting on you ({len(decisions)}):")
        for r in decisions[:a.max]: out.append(f"• {r['title']} — open {age_days(r)} days")
    print("\n".join(out) if out else "Nothing open.")

def cmd_json(a): print(json.dumps(load(), indent=2, ensure_ascii=False))

def main():
    p = argparse.ArgumentParser(); s = p.add_subparsers(dest="cmd", required=True)
    q = s.add_parser("list"); q.add_argument("--owner"); q.add_argument("--lane"); q.add_argument("--status", default="open"); q.add_argument("--aging", type=int, default=0); q.set_defaults(f=cmd_list)
    q = s.add_parser("add"); q.add_argument("--id", required=True); q.add_argument("--title", required=True); q.add_argument("--owner", required=True, choices=["joshua","claude"]); q.add_argument("--lane", required=True); q.add_argument("--kind", required=True); q.add_argument("--source"); q.add_argument("--first-seen"); q.add_argument("--note"); q.set_defaults(f=cmd_add)
    q = s.add_parser("resolve"); q.add_argument("--id", required=True); q.add_argument("--how", required=True); q.add_argument("--date"); q.set_defaults(f=cmd_resolve)
    q = s.add_parser("touch"); q.add_argument("--id", required=True); q.set_defaults(f=cmd_touch)
    q = s.add_parser("dedupe"); q.set_defaults(f=cmd_dedupe)
    q = s.add_parser("aging"); q.add_argument("--days", type=int, default=30); q.set_defaults(f=cmd_aging)
    q = s.add_parser("slack"); q.add_argument("--owner"); q.add_argument("--max", type=int, default=8); q.set_defaults(f=cmd_slack)
    q = s.add_parser("json"); q.set_defaults(f=cmd_json)
    a = p.parse_args(); a.f(a)

if __name__ == "__main__": main()
