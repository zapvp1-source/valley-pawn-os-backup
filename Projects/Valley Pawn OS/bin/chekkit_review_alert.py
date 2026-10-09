#!/usr/bin/env python3
"""chekkit_review_alert.py [--render] [--send] [--hours N] [--all] [--api-probe]

Native replacement (Mac-first wave 1, 2026-10-08) for the Cowork task `chekkit-new-review-alert`
(hourly at :10, 09:00-21:00 ET). Same source as the SKILL: Chekkit's "You got a new review for Valley Pawn -
<City>" emails, read natively from Apple Mail (Envelope Index + .emlx, read-only) instead of Gmail. One post
per new review in #google-reviews (C04NDE52U2G), the SKILL's one-liner exactly:

    Nice job Team <City>! You just got a new <N> star review from <Reviewer Name>! :star:

Why not the Chekkit API: GET /v1/reviews exists (reviewerName, rating, createdAt) but on 2026-10-08 it did
not list the 10/7 Waynesboro review (a stars-only review with no comment) that the email — and the live
post — had. The email is the complete list. (--api-probe prints the API's newest reviews per store, initials
only, for comparison.)

SKILL rules kept: look back one day (newer_than:1d -> emails received in the last --hours, default 24);
duplicate check BEFORE posting (the same "review from <Name>!" already in #google-reviews in the last 14
days = skip) plus a local state file of emails already posted/scheduled; business hours 09:00-21:00 ET =
post now, otherwise schedule for 10:00 the next morning (chat.scheduleMessage) and remember it, so the 09:10
run never posts it a second time. Store = short city name. No DMs. Mail not syncing (nothing received in
3 h) or any read failure = nothing posted, one FAILURE_LEDGER row.

--render prints what would be posted (reviewer shown as initials — logs never carry customer names) and
sends nothing; --all (render only) also lists reviews already posted, marked. --send is required to publish.
"""
import datetime as dt, json, os, re, sys, time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chekkit_unanswered as cu  # noqa: E402  (shared Apple Mail readers)

TASK = "chekkit-new-review-alert"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.dirname(HERE)
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STATE = os.path.join(OS_DIR, "fleet", "state", "chekkit_review_alert.json")
CH = "C04NDE52U2G"
CITIES = {"culpeper": "Culpeper", "waynesboro": "Waynesboro", "harrisonburg": "Harrisonburg",
          "lexington": "Lexington", "roanoke": "Roanoke"}
SUBJ_RE = re.compile(r"new review for Valley Pawn ?- ?([A-Za-z]+)", re.I)
NAME_RES = [re.compile(r"You got a new (\d) star review from (.+?)\.(?:\s|$)"),
            re.compile(r"New (?:Google|Facebook|Yelp) review from (.+?)\.(?:\s|$)")]


def ledger(sentence):
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), TASK, sentence))


def initials(n):
    return "".join(w[0].upper() + "." for w in (n or "?").split() if w) or "?"


def parse(subj, txt):
    m = SUBJ_RE.search(subj)
    city = CITIES.get(m.group(1).lower()) if m else None
    stars, name = None, None
    m1 = NAME_RES[0].search(txt)
    if m1:
        stars, name = int(m1.group(1)), m1.group(2).strip()
    else:
        m2 = NAME_RES[1].search(txt)
        if m2:
            name = m2.group(1).strip()
        st = re.search(r"(★{1,5})(?!★)", txt)          # the star row under the store name
        if st:
            stars = len(st.group(1))
    return city, stars, name


def slack_history(days=14):
    import vp_slack
    cutoff = time.time() - days * 86400
    r = vp_slack.call("conversations.history", params={"channel": CH, "limit": 200})
    if not r.get("ok"):
        raise RuntimeError("history: " + r.get("error", "?"))
    return [m.get("text") or "" for m in r.get("messages", []) if float(m.get("ts", 0)) >= cutoff]


def load_state():
    try:
        return json.load(open(STATE))
    except Exception:
        return {"done": {}}


def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(st, open(STATE, "w"), indent=1)


def api_probe():
    import chekkit_api as ck
    for code in ("CUL", "WAY", "HAR", "LEX", "ROA"):
        rs = []
        for page in range(1, 16):
            b = ck.get(code, "/v1/reviews?page=%d" % page, retries=2)
            rs += b.get("reviews") or []
            time.sleep(1.1)
            if not b.get("hasMore"):
                break
        for r in sorted(rs, key=lambda r: r.get("createdAt") or "")[-3:]:
            print("API %s %s %s %s*" % (code, r.get("createdAt"), initials(r.get("reviewerName")), r.get("rating")), file=sys.stderr)


def main(a):
    render, send = "--render" in a, "--send" in a
    dry = render or not send
    hours = float(a[a.index("--hours") + 1]) if "--hours" in a else 24
    if "--api-probe" in a:
        api_probe()
    now = dt.datetime.now(ET)
    try:
        if not cu.mail_fresh():
            raise RuntimeError("Apple Mail has received nothing in 3 hours (not syncing)")
        mails = cu.mail_bodies("%new review%", now - dt.timedelta(hours=hours), now + dt.timedelta(minutes=1))
        hist = slack_history()
    except Exception as e:  # noqa: BLE001
        print("READ FAILED", type(e).__name__, str(e)[:160])
        if send:
            ledger("The new-review check could not read the review emails or #google-reviews this hour, so nothing was posted.")
        return 1
    st = load_state()
    business = 9 <= now.hour < 21
    todo, bad = [], 0
    for rec, subj, txt, gid in mails:
        city, stars, name = parse(subj, txt)
        if not (city and stars and name):
            bad += 1
            continue
        text = "Nice job Team %s! You just got a new %d star review from %s! :star:" % (city, stars, name)
        dup = gid in st["done"] or any(("review from %s!" % name) in h for h in hist)
        if dup and not (dry and "--all" in a):
            continue
        todo.append((rec, gid, name, ("[already posted] " if dup else "") + text, dup))
    if bad:
        print("WARN %d review email(s) could not be parsed" % bad, file=sys.stderr)
    if dry:
        for rec, gid, name, text, dup in todo:
            print("=== %s %s (email %s ET)\n%s" % ("POST" if business else "SCHEDULE 10:00", CH, rec.strftime("%m-%d %H:%M"),
                  text.replace(name, initials(name))))
        print("RENDER: %d review email(s) in the last %gh, %d new to post" % (len(mails), hours, sum(1 for t in todo if not t[4])))
        return 0
    import vp_slack
    for rec, gid, name, text, dup in todo:
        if business:
            vp_slack.post(CH, text)
            st["done"][gid] = {"at": now.isoformat(), "how": "posted"}
        else:
            if vp_slack.dryrun_intercept("slack-scheduled", CH, text):
                continue
            day = (now + dt.timedelta(days=1)).date() if now.hour >= 21 else now.date()
            post_at = int(dt.datetime.combine(day, dt.time(10), ET).timestamp())
            res = vp_slack.call("chat.scheduleMessage", {"channel": CH, "text": text, "post_at": post_at})
            if not res.get("ok"):
                ledger("A new review could not be scheduled for tomorrow morning (%s)." % res.get("error", "?"))
                continue
            vp_slack.receipt("slack-scheduled", CH, True, len(text.encode()), text[:60])
            st["done"][gid] = {"at": now.isoformat(), "how": "scheduled", "post_at": post_at}
        save_state(st)
    cut = (now - dt.timedelta(days=30)).isoformat()
    st["done"] = {k: v for k, v in st["done"].items() if v.get("at", "") >= cut}
    save_state(st)
    print("SENT %d" % len(todo))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
