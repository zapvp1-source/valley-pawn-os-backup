#!/usr/bin/env python3
"""slack_channel_trim.py <channel_id> --keep U1,U2 [--apply]  (built 2026-11-16, additive)

Joshua 2026-11-16: #timekeeping-summary is for Joshua and Preston only — take everyone else off.
Lists channel members; removes (conversations.kick, as the Goldilocks bot) every HUMAN not in --keep.
Bots/apps are left alone so the report keeps posting. Default = dry run. Posts no message.
Prints BEFORE / AFTER membership so the result is self-verifying.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack


def members(ch):
    out, cur = [], None
    while True:
        p = {"channel": ch, "limit": 200}
        if cur: p["cursor"] = cur
        r = vp_slack.call("conversations.members", params=p)
        if not r.get("ok"):
            sys.exit("conversations.members failed: %s" % r.get("error"))
        out += r.get("members", [])
        cur = (r.get("response_metadata") or {}).get("next_cursor")
        if not cur: return out


def who(u):
    r = vp_slack.call("users.info", params={"user": u})
    x = r.get("user") or {}
    return (x.get("real_name") or x.get("name") or u), bool(x.get("is_bot") or u == "USLACKBOT")


def main(a):
    ch = a[0]; keep = set(); apply = "--apply" in a
    if "--keep" in a: keep = set(a[a.index("--keep") + 1].split(","))
    me = vp_slack.call("auth.test").get("user_id")
    before = members(ch)
    print("BEFORE (%d):" % len(before))
    todo = []
    for u in before:
        n, bot = who(u)
        tag = "keep" if (u in keep or bot or u == me) else "REMOVE"
        print("  %-6s %s %s%s" % (tag, u, n, " (bot)" if bot else ""))
        if tag == "REMOVE": todo.append((u, n))
    if not apply:
        print("dry run — %d would be removed" % len(todo)); return 0
    bad = 0
    for u, n in todo:
        r = vp_slack.call("conversations.kick", {"channel": ch, "user": u})
        print("  removed %s %s" % (n, "ok" if r.get("ok") else "FAILED " + str(r.get("error"))))
        bad += 0 if r.get("ok") else 1
    after = members(ch)
    print("AFTER (%d): %s" % (len(after), ", ".join(who(u)[0] for u in after)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
