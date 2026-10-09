#!/usr/bin/env python3
"""deal_of_week_monday.py prompt|reminder [--render] [--send] [--day YYYY-MM-DD] [--at HH:MM (render replay)]

Native replacement (Mac-first wave 1, 2026-10-08) for the two local Cowork tasks
  prompt   = `vp-deal-of-week-monday-prompt`    Mon 08:10 ET
  reminder = `vp-deal-of-week-monday-reminder`  Mon 11:00 ET
both around #deal-of-the-week (C0AVCANK7E3). The 12:30 compiler is already native (deal_of_week_pick.py).

prompt   1 post the fixed submission prompt (the text the live posts show) — FIRST, never blocked by step 2
         2 DM Joshua the one-line confirmation with the upcoming Thursday's Brevo DRAFT name (a draft whose
           name contains "Month D, YYYY"); no match / key unreadable -> the SKILL's fallback wording.
         Duplicate guard: a prompt already in the channel today = post nothing.
reminder 1 freshness guard: today's prompt must be in the channel, else silent
         2 who has submitted: every manager message after today's prompt (thread replies AND channel messages —
           the managers post in the channel, and the compiler counts both) that has a photo AND a price;
           store/price read by the compiler's own extractor (deal_of_week_pick.extract, Claude + verify)
         3 all 5 in -> silent. Else ONE channel post @mentioning the missing stores' managers (looked up by
           name in Slack each run; not found -> the store is named without a mention).
         Duplicate guard: a reminder already in the channel today = post nothing.
--render prints what would be posted and sends nothing. --send is required to publish.
"""
import datetime as dt, os, re, sys, time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vp_slack  # noqa: E402

ET = ZoneInfo("America/New_York")
OS_DIR = os.path.dirname(HERE)
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
CH = "C0AVCANK7E3"
JOSHUA = "U03BB52MDSA"
ORDER = ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]
MANAGERS = {"Culpeper": ["Sandi Cole", "Sandi"], "Waynesboro": ["Chadd McClintic", "Chadd"],
            "Harrisonburg": ["Walker Tapley", "Walker"], "Lexington": ["Uriah Tiglao", "Uriah"],
            "Roanoke": ["Benjie Moore", "Benjie"]}
PROMPT = """:wave: Good morning, managers — Deal of the Week submissions open now.

Submit by 12:00 PM ET today. Reply in this thread with:
1. Photo (clear, well-lit, item is the focus)
2. Item name + brand
3. Your price (under retail — that's the whole point)
4. Your store + your name
5. One sentence on why it's a good deal

Every store's deal goes in Thursday's email to ~11K subscribers — one submission per store, all featured. Get yours in."""
DM = ("Deal of the Week submission window is open. Compiler runs at 12:30 PM today and will feature every qualifying "
      "store submission. Scheduled Thursday send: %s")
NO_DRAFT = "(no draft staged for this Thursday — will create from calendar at 12:30 PM)"
REMIND_HEAD = ":alarm_clock: One hour left — Deal of the Week closes at 12:00 PM ET."
REMIND = ("%s, we haven't gotten your store's submission yet (%s). Reply in the thread above with a photo, item + brand, "
          "your price, store + name, and one line on why it's a good deal — or your store won't be featured in Thursday's email.")


def ledger(task, sentence):
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), task, sentence))


def today_has(marker, day):
    r = vp_slack.call("conversations.history", params={"channel": CH, "limit": 100})
    if not r.get("ok"):
        raise RuntimeError("history: " + r.get("error", "?"))
    return any(marker in (m.get("text") or "") and dt.datetime.fromtimestamp(float(m["ts"]), ET).date() == day
               for m in r.get("messages", []))


def thursday_draft(day):
    import json, urllib.request
    thu = day + dt.timedelta(days=(3 - day.weekday()) % 7)
    label = "%s %d, %d" % (thu.strftime("%B"), thu.day, thu.year)
    try:
        k = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
        req = urllib.request.Request("https://api.brevo.com/v3/emailCampaigns?status=draft&limit=30",
                                     headers={"api-key": k, "accept": "application/json"})
        camps = json.load(urllib.request.urlopen(req, timeout=30)).get("campaigns", [])
    except Exception as e:  # noqa: BLE001
        print("brevo lookup skipped:", type(e).__name__)
        return NO_DRAFT
    hit = next((c.get("name") for c in camps if label in (c.get("name") or "")), None)
    return hit or NO_DRAFT


def prompt(day, live):
    task = "vp-deal-of-week-monday-prompt"
    if live and today_has("Deal of the Week submissions open now", day):
        print("prompt already in the channel today — nothing posted"); return 0
    if not live:
        print("=== POST %s\n%s" % (CH, PROMPT))
    else:
        vp_slack.post(CH, PROMPT)
    dm = DM % thursday_draft(day)
    if not live:
        print("=== DM %s\n%s" % (JOSHUA, dm)); return 0
    try:
        vp_slack.post(vp_slack.dm_channel(JOSHUA), dm)
    except SystemExit as e:
        ledger(task, "The Deal of the Week prompt posted, but the confirmation DM to Joshua did not go out (%s)." % e)
    print("SENT prompt + DM"); return 0


def resolve(names):
    """Slack user id for a manager, by real/display name (users.list). None if not found."""
    users, cur = [], None
    for _ in range(10):
        r = vp_slack.call("users.list", params={"limit": 500, **({"cursor": cur} if cur else {})})
        if not r.get("ok"):
            return {}
        users += r.get("members", [])
        cur = (r.get("response_metadata") or {}).get("next_cursor")
        if not cur:
            break
    out = {}
    for store, cands in names.items():
        for cand in cands:
            c = cand.lower()
            hit = [u for u in users if not u.get("deleted") and not u.get("is_bot") and c in (
                (u.get("real_name") or "").lower(), (u.get("profile", {}).get("display_name") or "").lower(),
                (u.get("profile", {}).get("real_name") or "").lower())]
            if len(hit) == 1:
                out[store] = hit[0]["id"]; break
    return out


def reminder(day, live, at=None):
    import deal_of_week_pick as pick
    p_ts, msgs = pick.submissions(day)
    if at is not None:                      # replay: only what had been posted by that time
        msgs = [m for m in msgs if float(m["ts"]) <= at.timestamp()]
    if not p_ts:
        print("no prompt posted today — silent (freshness guard)"); return 0
    if live and today_has("One hour left — Deal of the Week closes", day):
        print("reminder already in the channel today — nothing posted"); return 0
    have = set()
    if msgs:
        for d in pick.extract(msgs):
            img = any((f.get("mimetype") or "").startswith("image/") for f in (d["msg"].get("files") or []))
            if d["store"] and img and d["price"]:
                have.add(d["store"])
    missing = [s for s in ORDER if s not in have]
    print("submitted: %s | missing: %s" % (", ".join(s for s in ORDER if s in have) or "none", ", ".join(missing) or "none"))
    if not missing:
        print("all 5 stores already in — no reminder needed"); return 0
    ids = resolve({s: MANAGERS[s] for s in missing})
    tagged = [s for s in missing if s in ids]
    lines = [REMIND_HEAD, ""]
    if tagged:
        lines.append(REMIND % (", ".join("<@%s>" % ids[s] for s in tagged), ", ".join(tagged)))
    for s in missing:
        if s not in ids:
            lines.append("%s — we haven't gotten your submission yet. Reply in the thread above with a photo, item + brand, "
                         "your price, store + name, and one line on why it's a good deal — or your store won't be featured "
                         "in Thursday's email." % s)
    text = "\n".join(lines)
    if not live:
        print("=== POST %s\n%s" % (CH, text)); return 0
    vp_slack.post(CH, text)
    print("SENT reminder for", ", ".join(missing)); return 0


def main(a):
    if not a or a[0] not in ("prompt", "reminder"):
        sys.exit(__doc__)
    day = dt.date.fromisoformat(a[a.index("--day") + 1]) if "--day" in a else dt.datetime.now(ET).date()
    live = "--send" in a and "--render" not in a
    if a[0] == "prompt":
        return prompt(day, live)
    at = None
    if "--at" in a and not live:
        hh, mm = a[a.index("--at") + 1].split(":")
        at = dt.datetime.combine(day, dt.time(int(hh), int(mm)), ET)
    return reminder(day, live, at)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
