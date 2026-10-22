#!/usr/bin/env python3
"""hiring_autopost.py [--render] [--live] — auto-post hiring when a store's hiring is ON (2026-10-21).

Joshua 2026-10-21: "when ever preston tells claude to open hiring at a store, make sure we auto post".

Source of truth: Valley Pawn OS/HIRING_SWITCH.md (ACTIVE SCOPE table; the Preston assistant edits it, the
file is Drive-synced). For every store row marked ON:
  * the first run that sees it ON (OFF->ON, or ON with no hiring post in the last CYCLE_DAYS) schedules a
    hiring post on that store's Facebook page + its Google Business Profile at the next 1-3 PM slot;
  * while it stays ON, it re-posts every CYCLE_DAYS days with a different caption (3 rotating variants per
    channel, so the engine's identical-caption guard never trips).
Rows marked OFF get nothing. Publishing goes ONLY through the vp_social engine (QA gates, ledger idempotency:
a re-run can never double-post). No Slack, no DMs (Rule 16); a failure is one FAILURE_LEDGER row.
State: Valley Pawn OS/fleet/state/hiring_autopost.json
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
AGENT = "hiring-autopost"
OS_DIR = os.environ.get("VP_PROJECTS", os.path.expanduser("~/Documents/Claude/Projects")) + ("/Valley Pawn OS")
RSM = os.environ.get("VP_PROJECTS", os.path.expanduser("~/Documents/Claude/Projects")) + ("/Refine Social Media")
SWITCH = os.path.join(OS_DIR, "HIRING_SWITCH.md")
STATE = os.path.join(OS_DIR, "fleet/state/hiring_autopost.json")
LEDGER_MD = os.path.join(OS_DIR, "fleet/FAILURE_LEDGER.md")
PLAN_DIR = os.path.join(RSM, "state/plans")
CYCLE_DAYS = 14
SLOTS = [(13, 50), (14, 50)]          # audit 2026-10-20: FB reach peaks 1-3 PM
MIN_LEAD_MIN = 40

sys.path.insert(0, RSM)

STORE = {
    "Culpeper":     {"addr": "571 James Madison Hwy", "street": "James Madison Highway",
                     "sched": "Every Sunday off, and the doors close by 6 PM"},
    "Waynesboro":   {"addr": "1321 W Broad St", "street": "West Broad Street",
                     "sched": "Every Sunday off, and the doors close by 6 PM"},
    "Harrisonburg": {"addr": "1790 E Market St, Ste 22", "street": "East Market Street",
                     "sched": "Sundays and Wednesdays off, and the doors close at 6 PM"},
    "Lexington":    {"addr": "125 Walker St", "street": "Walker Street",
                     "sched": "Sundays and Wednesdays off, and the doors close at 6 PM"},
    "Roanoke":      {"addr": "2362 Peters Creek Rd, Ste C", "street": "Peters Creek Road",
                     "sched": "Every Sunday off, and the doors close by 6 PM"},
}

FB = [
    "{c}, we're hiring! Valley Pawn on {street} is looking for a Sales & Loan Associate.\n\n"
    "{sched}. Hourly pay plus a monthly store bonus program, paid training, and a family-owned team "
    "(since 2014) that teaches you the business from day one. No pawn experience needed.\n\n"
    "Apply at thevalleypawn.com/careers or stop by and ask for an application.\n\n\U0001F4CD {addr}, {c}",

    "Our {c} store is hiring a Sales & Loan Associate, and we'd love a referral from people who know us.\n\n"
    "The job: helping neighbors with pawn loans, buying and selling everything from jewelry to tools, and "
    "learning to appraise along the way. {sched}, with hourly pay plus a monthly bonus when the store hits "
    "its goals.\n\nApply at thevalleypawn.com/careers or come see us at {addr}.",

    "Now hiring in {c}: Sales & Loan Associate at Valley Pawn.\n\n"
    "What you get: {sched_l}, hourly pay plus a monthly bonus program, paid training, and room to move up. "
    "We promote from within. What we look for: friendly, honest and reliable. We'll teach you the rest.\n\n"
    "Apply at thevalleypawn.com/careers. \U0001F4CD {addr}, {c}",
]
GBP = [
    "Valley Pawn in {c} is hiring a Sales & Loan Associate. The role covers customer service, pawn loans, "
    "buying and selling merchandise, and on-the-job appraisal training. {sched}. Hourly pay plus a monthly "
    "bonus program. No pawn experience required. Apply online at thevalleypawn.com/careers or in person at {addr}.",

    "Join our {c} team. We're hiring a Sales & Loan Associate at {addr}. Paid training, hourly pay plus a "
    "monthly store bonus, and {sched_l}. Family-owned since 2014. Apply at thevalleypawn.com/careers.",

    "Now hiring at Valley Pawn {c}: Sales & Loan Associate. We're looking for friendly, reliable people who "
    "like helping customers, and we train you on loans, sales and appraising. {sched}. Apply at "
    "thevalleypawn.com/careers or ask for an application in the store.",
]


def now():
    return dt.datetime.now(ET)


def ledger_row(sentence):
    with open(LEDGER_MD, "a") as fh:
        fh.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (now().strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))


def read_switch(path=SWITCH):
    """{store: True/False} from the ACTIVE SCOPE table. Raises if the table can't be read (never guess)."""
    txt = open(path, encoding="utf-8").read()
    out = {}
    for line in txt.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0] not in STORE:
            continue
        flag = cells[2].upper()
        if flag in ("ON", "OFF"):
            out[cells[0]] = flag == "ON"
    if not out:
        raise RuntimeError("ACTIVE SCOPE table not found in HIRING_SWITCH.md")
    return out


def load_state():
    try:
        return json.load(open(STATE))
    except Exception:
        return {"stores": {}}


def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    json.dump(st, open(tmp, "w"), indent=1)
    os.replace(tmp, STATE)


def next_slot(t=None):
    t = t or now()
    earliest = t + dt.timedelta(minutes=MIN_LEAD_MIN)
    day = t.date()
    for _ in range(4):
        for h, m in SLOTS:
            s = dt.datetime(day.year, day.month, day.day, h, m, tzinfo=ET)
            if s >= earliest:
                return s
        day += dt.timedelta(days=1)
    raise RuntimeError("no slot")


def captions(store, cycle):
    f = STORE[store]
    v = {"c": store, "street": f["street"], "addr": f["addr"], "sched": f["sched"],
         "sched_l": f["sched"][0].lower() + f["sched"][1:]}
    i = cycle % 3
    return FB[i].format(**v), GBP[i].format(**v)


def recent_hiring_post(store, days):
    """True if Publer already has a hiring post (scheduled or published) for this store's FB in the window."""
    from vp_social import reader
    d_from = (now().date() - dt.timedelta(days=days)).isoformat()
    d_to = (now().date() + dt.timedelta(days=7)).isoformat()
    for r in reader.fetch_window(d_from, d_to, states=("scheduled", "published")):
        if r["account_key"] == store and re.search(r"hiring|careers", r["text"] or "", re.I):
            return r["scheduled_date"]
    return None


def build_plan(store, cycle, when):
    fb, gbp = captions(store, cycle)
    monday = (when.date() - dt.timedelta(days=when.weekday())).isoformat()
    key = "hiring:%s:%s" % (store, when.date().isoformat())
    return {
        "plan_id": "hiring_%s_%s" % (store.lower(), when.strftime("%Y%m%d")),
        "week": monday, "created_at": now().isoformat(), "season": "", "notes": "hiring_autopost",
        "existing_counts": {}, "remaining_after_plan": {},
        "slots": [{
            "slot_id": "hiring-%s" % store, "lane": "hiring", "item_key": key,
            "accounts": [store, "GBP_" + store], "kind": "status",
            "scheduled_at": when.isoformat(), "week": monday,
            "captions": {store: fb, "GBP_" + store: gbp},
        }],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true", help="print what would post; publish nothing, change no state")
    ap.add_argument("--live", action="store_true", help="publish (default when run by launchd wrapper)")
    a = ap.parse_args()
    live = a.live and not a.render

    try:
        flags = read_switch()
    except Exception as e:  # noqa: BLE001
        if live:
            ledger_row("could not read the hiring switch table, so no hiring posts were checked this run (%s)" % e)
        print("SWITCH READ FAILED:", e)
        return 1

    st = load_state()
    st.setdefault("stores", {})
    today = now().date()
    report = []
    for store, on in flags.items():
        rec = st["stores"].setdefault(store, {"on": False, "last_post": None, "cycle": 0})
        was_on = rec.get("on", False)
        rec["on"] = on
        if not on:
            report.append("%s: OFF — nothing" % store)
            continue
        last = rec.get("last_post")
        due = (not was_on) or (not last) or \
            (today - dt.date.fromisoformat(last)).days >= CYCLE_DAYS
        if not due:
            report.append("%s: ON — posted %s, next in %d days" % (store, last, CYCLE_DAYS - (today - dt.date.fromisoformat(last)).days))
            continue
        try:
            already = recent_hiring_post(store, CYCLE_DAYS if was_on else 3)
        except Exception as e:  # noqa: BLE001
            report.append("%s: ON — Publer read failed, will retry (%s)" % (store, e))
            continue
        if already:
            rec["last_post"] = already
            report.append("%s: ON — hiring post already in Publer for %s, skip" % (store, already))
            continue
        when = next_slot()
        plan = build_plan(store, rec.get("cycle", 0), when)
        if not live:
            fb, gbp = plan["slots"][0]["captions"].values()
            report.append("%s: ON — WOULD POST %s\n  FB : %s\n  GBP: %s" % (store, when.strftime("%a %m/%d %I:%M %p"), fb.replace("\n", " / "), gbp))
            continue
        from vp_social import publish as vps_publish
        os.makedirs(PLAN_DIR, exist_ok=True)
        ppath = os.path.join(PLAN_DIR, plan["plan_id"] + ".json")
        json.dump(plan, open(ppath, "w"), indent=1)
        res = vps_publish.publish_plan(__import__("pathlib").Path(ppath), dry_run=False, sleep_between=4.0)
        ok = res.get("scheduled", 0)
        if res.get("blocked") or res.get("failed") or ok == 0:
            why = res.get("blocked") or [i.get("reason") for i in res.get("items", []) if i.get("status") != "scheduled"]
            ledger_row("%s hiring post did not schedule: %s" % (store, "; ".join(str(x) for x in why)[:300]))
            report.append("%s: ON — FAILED %s" % (store, why))
            continue
        rec["last_post"] = when.date().isoformat()
        rec["cycle"] = rec.get("cycle", 0) + 1
        report.append("%s: ON — scheduled %d placements for %s" % (store, ok, when.isoformat()))
    if live:
        st["last_run"] = now().isoformat()
        save_state(st)
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
