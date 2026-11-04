#!/usr/bin/env python3
"""community_share_autopost.py [--render] [--live] — publish queued community SHARES on the store pages (2026-11-02).

Joshua 2026-11-02 ("split version"): the parts Facebook allows through its approved publishing route run on their
own. The daily PREP run ("Social outbound engagement (daily)", Claude in Chrome, no posting) picks local community
posts and drafts share captions into Refine Social Media/engagement_outbound/QUEUE.json. This native agent takes the
share items and schedules them on the store/brand Facebook page through the vp_social engine (Publer = the same
approved route as every scheduled post): caption + the community post's link, which Facebook shows as a preview.
Comments on other pages and follows stay in the on-request "post the community queue" chat (browser-only actions).

Rules: RAMP weekly share cap per page from WATCHLIST.json ramp_level (ledger.jsonl counts this ISO week's shares,
including ones posted by hand); entries older than 48 h are dropped, never posted late; slot = next 1-3 PM slot;
vp_social QA gates + ledger idempotency (re-runs never double-post). No Slack, no DMs (Rule 16); a failure is one
FAILURE_LEDGER row. State lives in QUEUE.json (item status) and ledger.jsonl (action rows).
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
AGENT = "community-share-autopost"
PROJ = os.environ.get("VP_PROJECTS", os.path.expanduser("~/Documents/Claude/Projects"))
OS_DIR = os.path.join(PROJ, "Valley Pawn OS")
RSM = os.path.join(PROJ, "Refine Social Media")
EO = os.path.join(RSM, "engagement_outbound")
QUEUE = os.path.join(EO, "QUEUE.json")
WATCH = os.path.join(EO, "WATCHLIST.json")
LEDGER = os.path.join(EO, "ledger.jsonl")
DAILY = os.path.join(EO, "DAILY_LOG.md")
FAIL_MD = os.path.join(OS_DIR, "fleet/FAILURE_LEDGER.md")
PLAN_DIR = os.path.join(RSM, "state/plans")
SLOTS = [(13, 35), (14, 25), (15, 5)]
MIN_LEAD_MIN = 30
MAX_AGE_H = 48
# RAMP shares/week by level (RUNBOOK §RAMP); Roanoke ceiling 4
SHARE_CAP = {1: 1, 2: 2, 3: 3, 4: 3}
ACCOUNT = {"Culpeper": "Culpeper", "Waynesboro": "Waynesboro", "Harrisonburg": "Harrisonburg",
           "Lexington": "Lexington", "Roanoke": "Roanoke", "Brand": "Brand"}
FB_URL = re.compile(r"^https://(www\.|m\.)?facebook\.com/\S+$")
NO_WORDS = re.compile(r"\b(gun|ammo|firearm|rifle|pistol|election|vote|ballot|candidate|democrat|republican|"
                      r"arrest|shooting|killed|obituary|passed away|pawn|loan|gold|silver|cash|price|\$\d)", re.I)

sys.path.insert(0, RSM)


def now():
    return dt.datetime.now(ET)


def fail_row(sentence):
    with open(FAIL_MD, "a") as fh:
        fh.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (now().strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))


def load(path, default):
    try:
        return json.load(open(path))
    except Exception:
        return default


def save_json(path, obj):
    tmp = path + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def shares_this_week(store):
    start = now().date() - dt.timedelta(days=now().weekday())
    n = 0
    try:
        for line in open(LEDGER):
            r = json.loads(line)
            if r.get("store") == store and r.get("action") == "share" and r.get("ts", "")[:10] >= start.isoformat():
                n += 1
    except FileNotFoundError:
        pass
    return n


def cap_for(store, watch):
    s = watch.get("stores", {}).get(store, {})
    lvl = int(s.get("ramp_level", 1))
    cap = SHARE_CAP.get(lvl, 1)
    if store == "Roanoke" and lvl >= 4:
        cap = 4
    return cap


def next_slot(taken):
    t = now()
    earliest = t + dt.timedelta(minutes=MIN_LEAD_MIN)
    day = t.date()
    for _ in range(4):
        for h, m in SLOTS:
            s = dt.datetime(day.year, day.month, day.day, h, m, tzinfo=ET)
            if s >= earliest and s.isoformat() not in taken:
                return s
        day += dt.timedelta(days=1)
    raise RuntimeError("no slot")


def check_item(it):
    probs = []
    if it.get("store") not in ACCOUNT:
        probs.append("unknown store")
    if not FB_URL.match(it.get("post_url") or ""):
        probs.append("missing/invalid post_url")
    txt = (it.get("text") or "").strip()
    if len(txt.split()) < 6:
        probs.append("caption too short")
    if "#" in txt or "http" in txt:
        probs.append("hashtag/link inside caption")
    if NO_WORDS.search(txt):
        probs.append("blocked word in caption")
    return probs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--live", action="store_true")
    a = ap.parse_args()
    live = a.live and not a.render

    q = load(QUEUE, None)
    if not isinstance(q, dict):
        if live:
            fail_row("QUEUE.json unreadable — no community shares scheduled this run")
        print("QUEUE unreadable"); return 1
    watch = load(WATCH, {})
    items = q.get("items", [])
    report, taken, changed = [], set(), False
    for it in items:
        # 2026-11-03: Publer link-posts of facebook.com URLs publish as a bare URL (no preview card) and do not
        # notify the shared page, so community shares moved to POST mode (real Facebook Share). This agent now only
        # handles items explicitly marked auto=true (none by default).
        if it.get("action") != "share" or it.get("status", "pending") != "pending" or it.get("auto") is not True:
            continue
        try:
            created = dt.datetime.fromisoformat(it["created"])
            if created.tzinfo is None:
                created = created.replace(tzinfo=ET)
        except Exception:
            created = None
        if not created or (now() - created).total_seconds() > MAX_AGE_H * 3600:
            it["status"] = "dropped_stale"; changed = True
            report.append("%s: dropped (older than %dh)" % (it.get("id"), MAX_AGE_H)); continue
        probs = check_item(it)
        if probs:
            it["status"] = "rejected"; it["reject_reason"] = "; ".join(probs); changed = True
            report.append("%s: rejected (%s)" % (it.get("id"), "; ".join(probs))); continue
        store = it["store"]
        used, cap = shares_this_week(store), cap_for(store, watch)
        if used >= cap:
            report.append("%s: %s at weekly share cap (%d/%d) — kept for next week only if still fresh" % (it.get("id"), store, used, cap))
            continue
        when = next_slot(taken)
        caption = it["text"].strip() + "\n\n" + it["post_url"].strip()
        if not live:
            report.append("%s: WOULD SCHEDULE %s %s\n   %s" % (it.get("id"), store, when.strftime("%a %m/%d %I:%M %p"), caption.replace("\n", " / ")))
            taken.add(when.isoformat()); continue
        monday = (when.date() - dt.timedelta(days=when.weekday())).isoformat()
        key = "community_share:%s" % (it.get("id") or it["post_url"])
        plan = {"plan_id": "cshare_%s_%s" % (store.lower(), when.strftime("%Y%m%d%H%M")), "week": monday,
                "created_at": now().isoformat(), "season": "", "notes": AGENT, "existing_counts": {}, "remaining_after_plan": {},
                "slots": [{"slot_id": "cshare-%s" % store, "lane": "community_share", "item_key": key,
                           "accounts": [ACCOUNT[store]], "kind": "status", "scheduled_at": when.isoformat(),
                           "week": monday, "captions": {ACCOUNT[store]: caption}}]}
        from vp_social import publish as vps_publish
        os.makedirs(PLAN_DIR, exist_ok=True)
        ppath = os.path.join(PLAN_DIR, plan["plan_id"] + ".json")
        json.dump(plan, open(ppath, "w"), indent=1, ensure_ascii=False)
        res = vps_publish.publish_plan(pathlib.Path(ppath), dry_run=False, sleep_between=4.0)
        if res.get("blocked") or res.get("failed") or res.get("scheduled", 0) == 0:
            why = res.get("blocked") or [i.get("reason") for i in res.get("items", []) if i.get("status") != "scheduled"]
            it["status"] = "rejected"; it["reject_reason"] = "engine: " + "; ".join(str(x) for x in why)[:300]; changed = True
            fail_row("%s community share did not schedule: %s" % (store, it["reject_reason"]))
            report.append("%s: FAILED %s" % (it.get("id"), why)); continue
        taken.add(when.isoformat())
        it["status"] = "scheduled"; it["scheduled_at"] = when.isoformat(); changed = True
        with open(LEDGER, "a") as fh:
            fh.write(json.dumps({"ts": now().isoformat(timespec="minutes"), "store": store, "action": "share",
                                 "target": it.get("target"), "target_url": it.get("target_url"),
                                 "post_snippet": it.get("post_snippet", "")[:120], "text": it["text"],
                                 "verified": True, "via": "publer", "scheduled_at": when.isoformat(),
                                 "run": "native-%s" % now().date().isoformat()}, ensure_ascii=False) + "\n")
        report.append("%s: scheduled %s for %s" % (it.get("id"), store, when.isoformat()))
    if live and changed:
        save_json(QUEUE, q)
    print("\n".join(report) if report else "nothing to share")
    return 0


if __name__ == "__main__":
    sys.exit(main())
