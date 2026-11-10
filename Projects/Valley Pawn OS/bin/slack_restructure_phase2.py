#!/usr/bin/env python3
"""slack_restructure_phase2.py — the channel side of the Slack Restructure (2026-11-09).

  setup     rename the 4 report channels, set topics on the 6, add the department canvas as a bookmark,
            post + pin a "moved to" pointer in every merged-away channel. Idempotent (state file).
  archive   archive every merged-away channel that has its pointer pinned (run after the parallel week).
  status    print the state file.

Everything goes through vp_slack.py chan (bot token). Reversible: Slack lets you rename back and
unarchive; the pointer messages are ordinary bot messages. State: fleet/state/slack_restructure.json
"""
import json, os, subprocess, sys, datetime as dt
OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(OS_DIR, "bin"); STATE = os.path.join(OS_DIR, "fleet", "state", "slack_restructure.json")
ROUTES = os.path.join(OS_DIR, "fleet", "slack_routes.json"); CANV = os.path.join(OS_DIR, "fleet", "canvas_state", "dept_canvases.json")

RENAMES = {"C04N24STDP1": "loans-layaways", "C0BMRC2LN3D": "marketing", "C0B26GD8D2R": "leadership-reports", "C0B3R9B3S8H": "daily-checks"}
TOPICS = {
 "C03CGTN3KN1": ("scoreboard", "Monday scoreboard — one headline a week; the full store & employee tables live on the Scoreboard canvas (tab above)."),
 "C04N24STDP1": ("loans", "Loans & layaways — Monday headline; full tables on the canvas (tab above). Store detail still goes to managers by DM."),
 "C04NGH4FF35": ("aged", "Aged inventory & markdowns — Monday headline; full table on the canvas (tab above). Managers reply here when markdowns are done."),
 "C0BMRC2LN3D": ("marketing", "Website, social, email, eBay, reviews, studio — one thread a week; full reports on the Marketing canvas (tab above)."),
 "C0B26GD8D2R": ("leadership", "Leadership reports — daily ops in one thread, weekly/monthly reports as headlines; full tables on the canvas (tab above)."),
 "C0B3R9B3S8H": ("daily", "Daily checks — funds, jewelry counts, unanswered texts, missed calls, registered agent. Exceptions only: a post here means something needs attention."),
}

def sh(*args):
    r = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py")] + list(args), capture_output=True, text=True, timeout=60)
    try:
        return json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"ok": False, "error": r.stderr.strip()[:200]}
    except Exception:
        return {"ok": r.returncode == 0, "raw": (r.stdout + r.stderr).strip()[:200]}

def load():
    try: return json.load(open(STATE))
    except Exception: return {"renamed": {}, "topics": {}, "bookmarks": {}, "pointers": {}, "archived": {}}
def save(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True); json.dump(st, open(STATE, "w"), indent=1)

def setup():
    st = load(); canv = json.load(open(CANV)); routes = json.load(open(ROUTES))
    for ch, name in RENAMES.items():
        if ch in st["renamed"]: continue
        r = sh("chan", "rename", ch, name); print("rename", ch, name, r)
        if r.get("ok") or r.get("error") == "name_taken": st["renamed"][ch] = name; save(st)
    for ch, (dept, topic) in TOPICS.items():
        if ch not in st["topics"]:
            r = sh("chan", "topic", ch, topic); print("topic", ch, r)
            if r.get("ok"): st["topics"][ch] = topic; save(st)
        if ch not in st["bookmarks"] and canv.get(dept, {}).get("url"):
            r = sh("chan", "bookmark", ch, canv[dept]["title"].split(" (live)")[0].replace(":bar_chart: ", "").replace(":clipboard: ", "").replace(":package: ", "").replace(":mega: ", "").replace(":briefcase: ", "").replace(":white_check_mark: ", ""), canv[dept]["url"])
            print("bookmark", ch, r)
            if r.get("ok") or r.get("error") == "bookmark_already_exists": st["bookmarks"][ch] = canv[dept]["id"]; save(st)
    names = {"C03CGTN3KN1": "store-performance", "C04N24STDP1": "loans-layaways", "C04NGH4FF35": "aged-inventory-review", "C0BMRC2LN3D": "marketing", "C0B26GD8D2R": "leadership-reports", "C0B3R9B3S8H": "daily-checks"}
    for rule in routes["rules"]:
        if rule.get("action") != "redirect": continue
        old, to = rule["channel"], rule["to"]
        if old in st["pointers"]: continue
        text = ("This channel's reports moved to <#%s> on Nov 9, 2026 — one headline per report there, with the full tables on that channel's canvas "
                "(the tab at the top). Nothing is lost: history stays here and in Google Drive. This channel will be archived after one week." % to)
        r = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "post", old, text], capture_output=True, text=True, env=dict(os.environ, VP_ROUTE_OFF="1", VP_TASK="slack-restructure"))
        ts = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
        print("pointer", rule["channel_name"], "->", names.get(to, to), "ts=", ts, r.stderr.strip()[:120])
        if ts and ts.replace(".", "").isdigit():
            p = sh("chan", "pin", old, ts); print("  pin", p)
            st["pointers"][old] = {"ts": ts, "to": to, "pinned": bool(p.get("ok")), "at": dt.datetime.now().isoformat(timespec="seconds")}; save(st)
    print("setup done")

def archive():
    st = load()
    for old, info in st["pointers"].items():
        if old in st["archived"]: continue
        r = sh("chan", "archive", old); print("archive", old, r)
        if r.get("ok") or r.get("error") == "already_archived": st["archived"][old] = dt.datetime.now().isoformat(timespec="seconds"); save(st)
    print("archive done")

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["setup"]: setup()
    elif a[:1] == ["archive"]: archive()
    elif a[:1] == ["status"]: print(json.dumps(load(), indent=1))
    else: print(__doc__)
