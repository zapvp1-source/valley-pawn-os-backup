#!/usr/bin/env python3
"""ask_vp_invite_staff.py [--apply] — add every rostered staff member to #ask-goldilocks (built 2026-10-22).

Joshua approved 10/22 ("yes"): Goldilocks LIVE + all staff in the channel before the 11/5 Policy Day.
Reads hr/ROSTER.json (Gusto-sourced, current staff only) and invites each slack_id not already a member,
as the Goldilocks bot (conversations.invite). Posts no message. Default is a dry run that lists who would be added.
Idempotent: re-running adds only new hires, so onboarding can call it again.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vp_slack  # noqa: E402

OS_DIR = os.path.dirname(HERE)
ROSTER = os.path.join(OS_DIR, "hr", "ROSTER.json")
CFG = os.path.join(os.path.dirname(OS_DIR), "Ask Valley Pawn", "config.json")


def members(ch):
    out, cur = set(), None
    for _ in range(20):
        p = {"channel": ch, "limit": 200}
        if cur:
            p["cursor"] = cur
        r = vp_slack.call("conversations.members", params=p)
        if not r.get("ok"):
            print("conversations.members unavailable (%s) — inviting everyone; already-in is skipped by Slack" % r.get("error"))
            return None
        out.update(r.get("members", []))
        cur = (r.get("response_metadata") or {}).get("next_cursor")
        if not cur:
            break
    return out


def main():
    apply = "--apply" in sys.argv
    ch = json.load(open(CFG))["channel"]
    have = members(ch)
    known = have is not None
    have = have or set()
    staff = [(e.get("name"), e.get("department"), e["slack_id"]) for e in json.load(open(ROSTER)).get("employees", [])
             if e.get("slack_id")]
    todo = [s for s in staff if s[2] not in have]
    print("channel %s: %d members now; %d rostered staff with Slack; %d to add" % (ch, len(have), len(staff), len(todo)))
    for n, d, u in todo:
        print("  add: %s (%s) %s" % (n, d, u))
    if not apply or not todo:
        return 0
    bad = 0
    for i in range(0, len(todo), 30):
        ids = ",".join(u for _n, _d, u in todo[i:i + 30])
        r = vp_slack.call("conversations.invite", {"channel": ch, "users": ids})
        if r.get("ok"):
            continue
        print("batch invite failed: %s — trying one by one" % r.get("error"))
        for n, _d, u in todo[i:i + 30]:
            r1 = vp_slack.call("conversations.invite", {"channel": ch, "users": u})
            if not r1.get("ok") and r1.get("error") not in ("already_in_channel", "cant_invite_self"):
                bad += 1
                print("  FAILED %s: %s" % (n, r1.get("error")))
    after = members(ch)
    if after is None:
        print("invites sent; failures: %d" % bad)
        return 1 if bad else 0
    missing = [n for n, _d, u in staff if u not in after]
    print("after: %d members; rostered staff still missing: %s" % (len(after), ", ".join(missing) or "none"))
    return 1 if bad or missing else 0


if __name__ == "__main__":
    sys.exit(main())
