#!/usr/bin/env python3
"""brevo_draft_guard.py [--render] — native brevo-weekly-draft-guard (Mon 11:50, 2026-10-05).
Guarantees deal_of_week_pick.py (Mon 12:30) finds exactly one draft for this Thursday:
  - exactly one draft named with "Month D, YYYY"  -> verify sender, list 10, Call/Text links, utm_content=primary_cta,
    the DEAL OF THE WEEK placeholder, no unfilled [[MARKERS]]; silent if all good
  - two or more -> rename the extras "<name> [DUPE - do not send]" and say so in #email-campiagns
  - none -> clone the newest SENT weekly campaign (Spotlight/Layaway/Gold/Warranty/Deal), retag utm_campaign,
    insert the placeholder, recipients [7, 10], leave it a DRAFT (never schedules), say so
  - fewer than 8 future-dated weekly drafts -> one plain line that staging is behind
"""
import datetime as dt, json, os, re, sys, urllib.request
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack  # noqa: E402

ET = ZoneInfo("America/New_York")
K = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
CH = "C0APR5WUL2Z"
PH = ('<div style="border: 2px dashed #c97b3a; padding: 24px; margin: 0 0 24px 0; text-align: center; color: #c97b3a; '
      'font-weight: bold;">DEAL OF THE WEEK — POPULATED MONDAY</div>')
MONTHS = "January February March April May June July August September October November December".split()


def b(path, payload=None, method=None):
    r = urllib.request.Request("https://api.brevo.com/v3" + path, data=json.dumps(payload).encode() if payload is not None else None,
                               method=method or ("POST" if payload is not None else "GET"),
                               headers={"api-key": K, "accept": "application/json", "content-type": "application/json"})
    with urllib.request.urlopen(r, timeout=60) as x:
        d = x.read(); return json.loads(d) if d else {}


def main():
    render = "--render" in sys.argv
    today = dt.datetime.now(ET).date()
    thu = today + dt.timedelta(days=(3 - today.weekday()) % 7)
    if "--thursday" in sys.argv:
        thu = dt.date.fromisoformat(sys.argv[sys.argv.index("--thursday") + 1])
    label = "%s %d, %d" % (thu.strftime("%B"), thu.day, thu.year)
    notes = []
    for st in ("queued", "sent"):
        if any(label in (c.get("name") or "") for c in b("/emailCampaigns?status=%s&limit=50&sort=desc" % st).get("campaigns", [])):
            print("already %s for %s" % (st, label)); return 0
    drafts = b("/emailCampaigns?status=draft&limit=100").get("campaigns", [])
    hits = [c for c in drafts if label in (c.get("name") or "") and "[DUPE" not in c.get("name", "")]
    if len(hits) > 1:
        for c in hits[1:]:
            if not render:
                b("/emailCampaigns/%d" % c["id"], {"name": c["name"] + " [DUPE - do not send]"}, "PUT")
        notes.append("Weekly email for %s: found %d drafts for the same date, marked the extras do-not-send." % (label, len(hits)))
    if not hits:
        sent = [c for c in b("/emailCampaigns?status=sent&limit=50&sort=desc").get("campaigns", [])
                if re.search(r"Spotlight|Layaway|Gold|Warranty|Deal", c.get("name") or "")]
        if not sent:
            notes.append("Weekly email for %s: no draft exists and there was nothing to rebuild it from." % label)
        else:
            src = b("/emailCampaigns/%d" % sent[0]["id"])
            h = re.sub(r"utm_campaign=[A-Za-z0-9_\-]+", "utm_campaign=weekly_fallback_%s" % thu.isoformat(), src.get("htmlContent") or "")
            if "DEAL OF THE WEEK — POPULATED MONDAY" not in h:
                h = re.sub(r"(<body[^>]*>)", r"\1" + PH, h, count=1) if "<body" in h else PH + h
            if not render:
                b("/emailCampaigns", {"name": "Weekly — %s" % label, "subject": src.get("subject") or "This week at Valley Pawn",
                                      "sender": {"name": "Valley Pawn", "email": "hello@thevalleypawn.com"}, "replyTo": "jdavis@fcfpawn.com",
                                      "htmlContent": h, "recipients": {"listIds": [7, 10]}})
            notes.append("Weekly email for %s: draft was missing, created and ready for the noon picker." % label)
    else:
        c = b("/emailCampaigns/%d" % hits[0]["id"]); h = c.get("htmlContent") or ""
        lists = [l["id"] if isinstance(l, dict) else l for l in (c.get("recipients", {}).get("lists") or [])]
        fix = {}
        if 10 not in lists:
            fix["recipients"] = {"listIds": lists + [10]}
        bad = []
        if "/c/" not in h or "/t/" not in h: bad.append("call/text links")
        if "utm_content=primary_cta" not in h: bad.append("primary button tracking")
        if "DEAL OF THE WEEK — POPULATED MONDAY" not in h: bad.append("deal placeholder")
        if re.findall(r"\[\[[A-Z_]+\]\]", re.sub(r"<!--.*?-->", "", h, flags=re.S)): bad.append("unfilled template markers")
        if fix and not render:
            b("/emailCampaigns/%d" % c["id"], fix, "PUT")
            notes.append("Weekly email for %s: the internal copy list was missing from the draft — added." % label)
        if bad:
            notes.append("Weekly email for %s: the draft is missing %s — it needs a fix before the noon picker." % (label, ", ".join(bad)))
    future = [c for c in drafts if any(m in (c.get("name") or "") for m in MONTHS) and re.search(r"(\w+ \d{1,2}, \d{4})", c.get("name") or "")]
    n_future = 0
    for c in future:
        try:
            if dt.datetime.strptime(re.search(r"(\w+ \d{1,2}, \d{4})", c["name"]).group(1), "%B %d, %Y").date() > thu:
                n_future += 1
        except ValueError:
            pass
    if n_future < 8:
        notes.append("Weekly email calendar has %d weeks left — staging is behind." % n_future)
    print("\n".join(notes) or "healthy: %s" % label, "| future drafts:", n_future)
    if notes and not render:
        os.environ["VP_TASK"] = "brevo-weekly-draft-guard"
        vp_slack.post(CH, "\n".join(notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
