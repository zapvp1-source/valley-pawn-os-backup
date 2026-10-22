#!/usr/bin/env python3
"""monthly_eom_recap.py [YYYY-MM] [--render] [--only C123,...] — native `monthly-eom-recap`
(1st of month 10:30 ET; Mac-first wave 3 second pass, 2026-10-20). Spec: Valley Pawn OS/pending-tasks/monthly-eom-recap/SKILL.md.

Per channel (the 15 in CHANNELS, never #store-performance or a channel with its own monthly producer):
  1  duplicate guard — a "Month in Review" post naming the target month, posted after the month closed = skip
  2  read the target month's history as the ops bot (bot/webhook posts included; join messages dropped)
  3  the model (bin/vp_ai.py, claude-sonnet-5-5) lists the month's REPORT posts (date + one line of the figures) — it
     never sees anything but this channel's own posts; the completeness gate is then applied HERE, in code (weekly:
     >= 3 distinct report weeks; daily: >= 60% of the month's days; count: >= 1). Gate fails = nothing posted (Rule 18)
  4  the model writes the recap in the reference shape (fleet/state/w3b_reference/eom_recap_2026-09.json = the real
     10/1 posts): ":date: *<Month Year> — Month in Review*", 2–4 sentences, <= 8 bullets; month totals only where the
     figures are additive; a one-line month-over-month comparison when last month's recap is in the channel
  5  Rule 16 check in code (no tool/system/file names); one rewrite, else the channel is skipped + ledger row
  6  post as the ops bot; one post per channel
FINISH: Valley Pawn OS/monthly-analytics/<YYYY-MM> Month in Review.md (per channel: posted / skipped-duplicate /
skipped-gate with the count). The SKILL's CHANGELOG line is left to the human-run CHANGELOG (no concurrent writes).
--render: same reads + model calls, writes each would-be post to fleet/test_output/, the duplicate guard is reported
but not applied (so a past month can be re-rendered for parity), nothing is posted, no run log is written.
"""
import calendar
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w3b_lib as L  # noqa: E402
import re  # noqa: E402
import vp_people  # noqa: E402  fleet-wide rule 2026-10-21: current staff only, never a Davis
from ceo_monthly_scorecard import scrub_people, former_named, _METRIC_WORDS  # noqa: E402  (same line scrub as the CEO monthly)

TASK = "monthly-eom-recap"
REF = os.path.join(L.OS_DIR, "fleet", "state", "w3b_reference", "eom_recap_2026-09.json")
RUNLOG_DIR = os.path.join(L.OS_DIR, "monthly-analytics")
# channel id -> (name, cadence, audience)
CHANNELS = {
    "C0B08RS2BMK": ("loan-review", "weekly", "field"),
    "C04N24STDP1": ("layaway-review", "weekly", "field"),
    "C04NGH4FF35": ("aged-inventory-review", "weekly", "field"),
    "C0B17894S2Y": ("first-payment-default", "weekly", "field"),
    "C0AN6TNA4ES": ("timekeeping-summary", "weekly", "leadership"),
    "C0B1K4WK2HZ": ("weekly-returns-summary", "weekly", "field"),
    "C0B3R9B3S8H": ("daily-funds-reconcilation", "daily", "leadership"),
    "C0B8WR95N31": ("pawn-walks", "daily", "field"),
    "C04NDE52U2G": ("google-reviews", "weekly", "field"),
    "C0BMRC2LN3D": ("social-media", "weekly", "leadership"),
    "C0APR5WUL2Z": ("email-campiagns", "weekly", "leadership"),
    "C0ASE9C0GQ0": ("website", "weekly", "leadership"),
    "C0BCEESUANM": ("ai-marketing", "weekly", "leadership"),
    "C0ANVN5KX4Y": ("ebay-performance", "weekly", "leadership"),
    "C0APY6TE604": ("blog-posts", "count", "leadership"),
}
SYSTEM = ("You write Valley Pawn's monthly 'Month in Review' Slack posts from ONE channel's own posts. Use only "
          "numbers that appear in the posts given; never estimate, never fill a gap. Plain everyday language. Never "
          "name software, systems, tools, files, reports, automations, Slack channels or 'pulled automatically'. "
          "No signature footer. Name only current employees, and never name anyone with the last name Davis.")

EXTRACT = """Channel #{name}. Below are every message posted in it during {label} (oldest first; each starts with its ET date).
List the REPORT posts — the recurring automated summaries the channel exists for (weekly/daily reports, published blog posts,
sends, audits). Ignore chit-chat, reactions, join messages, test posts, and empty/placeholder posts with no figures.
Also name the channel's PRIMARY recurring report — the one summary format the channel exists for (e.g. "Weekly Social Recap",
"past-due loan check", "weekly returns summary") — and use EXACTLY that name as "kind" for each of its posts. A channel with
several distinct weekly producers of equal standing (e.g. eBay sales + efficiency + ratings) may list them all in "primary".
Return ONLY JSON: {{"primary": ["<kind name>", ...], "reports": [{{"date": "YYYY-MM-DD", "week_of": "YYYY-MM-DD or null", "kind": "<short name of the report type>",
"figures": "<one line with the key numbers exactly as posted>"}}], "prior_recap": "<the text of last month's Month in Review if one appears, else empty>"}}

MESSAGES:
{msgs}"""

WRITE = """Write the {label} Month in Review for #{name} ({aud} channel{audnote}).
Shape — exactly like the reference posts:
:date: *{label} — Month in Review*
<2–3 sentences: what happened this month, who led, what moved, what to watch>
<blank line>
<compact bullet list of the month's key figures, "• " bullets, 3–5 lines (never more than 6)>
<optional one closing line: a watch item, or a 'Note:' naming a missing week>
Month totals only where the figures are additive (counts, dollars, posts, reviews, returns); otherwise the trajectory
(first vs last figure, best/worst week, which store led or lagged most often).{mom}
LENGTH: match the reference posts — about {words} words in total. Pick the figures that matter; leave the rest out.

REFERENCE POSTS (last month, other channels — match their tone, length and layout, not their numbers):
{refs}

THIS CHANNEL'S REPORT POSTS FOR {label}:
{reports}

FULL TEXT OF THOSE POSTS (for exact figures):
{msgs}

Return ONLY the post text."""


VERIFY = """Check this draft Slack post against the channel's own posts. Every number, date, store claim and "no post for X"
note must be supported by the posts, and the draft must not contradict itself. Return ONLY JSON:
{{"ok": true/false, "problems": ["<short>", ...], "fixed": "<the corrected post — same shape, unsupported or contradictory lines
removed or corrected from the posts — or empty if it cannot be fixed>"}}

DRAFT:
{post}

POSTS:
{msgs}"""


def et_date(ts):
    return dt.datetime.fromtimestamp(float(ts), L.ET).date()


def gate(cadence, reports, first, last):
    if cadence == "count":
        return len(reports) >= 1, "%d posts" % len(reports)
    if cadence == "daily":
        days = {r.get("date") for r in reports if r.get("date")}
        open_days = sum(1 for i in range((last - first).days + 1) if (first + dt.timedelta(i)).weekday() != 6)
        return len(days) >= 0.6 * open_days, "%d of ~%d days" % (len(days), open_days)
    weeks = set()
    for r in reports:
        w = r.get("week_of") or r.get("date")
        try:
            d = dt.date.fromisoformat(w)
            weeks.add((d - dt.timedelta(days=(d.weekday() + 1) % 7)).isoformat())
        except (TypeError, ValueError):
            continue
    return len(weeks) >= 3, "%d weekly posts" % len(weeks)


_PAIR = re.compile(r"\b([A-Z][a-z'.-]+) ([A-Z][a-zA-Z'.-]+)\b")
_CAL = {"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
        "December", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Month", "Review",
        "Black", "Labor", "Memorial", "Day", "Valley", "Virginia", "Facebook", "Instagram", "Google", "Best", "Offer"}


def drop_people_lines(text, source):
    """2026-10-21: drop any line of a written recap that names a Davis, or a 'First Last' pair that looks like a person
    (first name is a known staff/former first name) and is not current staff. Log-only (vp_people dropped.log)."""
    firsts = {vp_people._tokens(e["name"])[0].capitalize() for e in vp_people.current_staff()}
    firsts |= {(vp_people._tokens(n)[:1] or [""])[0].capitalize() for n in _known_people()}
    out, dropped = [], []
    for ln in text.split("\n"):
        if vp_people.mentions_davis(ln):
            dropped.append((ln[:60], "Davis family")); continue
        bad = former_named(ln)
        for a, b in ([] if bad else _PAIR.findall(ln)):
            if a in _CAL or b in _CAL or a in _METRIC_WORDS or b in _METRIC_WORDS or a in L.NAMES.values() or b in L.NAMES.values():
                continue
            if a in firsts and not vp_people.is_reportable("%s %s" % (a, b)):
                bad = "%s %s" % (a, b); break
        if bad:
            dropped.append((bad, vp_people.reason(bad) or "not current")); continue
        out.append(ln)
    vp_people._log(source, dropped)
    return "\n".join(out)


def _known_people():
    """First names of everyone Bravo has ever listed (incl. TERMINATED) — the former-staff side of the line check."""
    try:
        d = json.load(open(vp_people.BRAVO_USERS_PATH))
        return [u.get("name") or "" for u in d.get("users", [])]
    except (OSError, ValueError):
        return []


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render = "--render" in sys.argv
    period = args[0] if args and args[0][:2] == "20" else L.prev_month()
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    _, first, last, label = L.months(period)
    month_word = label.split()[0]
    ref = json.load(open(REF))
    ref_posts = list(ref["posts"].values())
    rows = []
    for ch, (name, cadence, aud) in CHANNELS.items():
        if only and ch not in only:
            continue
        try:
            recent = L.history(ch, L.ts_of(first), "%.6f" % L.now().timestamp())
        except RuntimeError as e:
            rows.append((name, "skipped-unreadable", str(e)))
            L.ledger(TASK, "#%s could not be read for the %s Month in Review" % (name, label)) if not render else None
            continue
        # any recap naming the month posted after the month closed (not just the last 30 messages: a busy channel such as
        # #google-reviews buries the 10/1 recap under alert posts within days)
        dup = any("Month in Review" in L.text_of(m) and month_word in L.text_of(m) for m in recent if float(m["ts"]) >= float(L.ts_of(last)))
        if dup and not render:
            rows.append((name, "skipped-duplicate", ""))
            continue
        msgs = [m for m in L.history(ch, L.ts_of(first), L.ts_of(last, end=True)) if "Month in Review" not in L.text_of(m)]
        prev_first = (first - dt.timedelta(days=1)).replace(day=1)
        prior = [L.text_of(m) for m in L.history(ch, L.ts_of(first), L.ts_of(first + dt.timedelta(days=12), end=True))
                 if "Month in Review" in L.text_of(m) and prev_first.strftime("%B") in L.text_of(m)]
        try:
            blob = "\n\n".join("[%s] %s" % (et_date(m["ts"]).isoformat(), scrub_people(L.text_of(m)[:1800], TASK))
                                for m in msgs if L.text_of(m).strip())
        except vp_people.RosterHold as e:
            rows.append((name, "skipped-roster", str(e)))
            L.ledger(TASK, "#%s Month in Review for %s was held: the current-staff list could not be read" % (name, label)) if not render else None
            continue
        blob = blob[-90000:]
        if not blob:
            rows.append((name, "skipped-gate", "0 posts"))
            continue
        ex = L.ask_json(EXTRACT.format(name=name, label=label, msgs=blob), system=SYSTEM, max_tokens=9000)
        reports = ex.get("reports") or []
        prim = [k.lower() for k in (ex.get("primary") or [])]
        gated = reports
        if prim and cadence == "weekly":
            # the 10/1 cloud run's reading of the SKILL: a weekly channel passes when its OWN recap format posted >= 3 weeks
            # (#social-media had lane updates every week but the Weekly Social Recap only once -> skipped-gate)
            per = {k: [r for r in reports if (r.get("kind") or "").lower() == k] for k in prim}
            gated = max(per.values(), key=lambda v: len({(r.get("week_of") or r.get("date")) for r in v})) if per else reports
        ok, cnt = gate(cadence, gated, first, last)
        if not ok:
            rows.append((name, "skipped-gate", cnt))
            continue
        mom = ("\nLast month's recap in this channel (for ONE month-over-month comparison line):\n" + prior[0][:1500]) if prior else ""
        audnote = ": must read like a store manager wrote it" if aud == "field" else ": may carry a little more detail"
        prompt = WRITE.format(label=label, name=name, aud=aud, audnote=audnote, mom=mom, words=110 if aud == "field" else 150,
                              refs="\n---\n".join(ref_posts[:4] + ref_posts[6:8]),
                              reports=json.dumps(reports, indent=0), msgs=blob[-60000:])
        text = L.ask(prompt, system=SYSTEM, max_tokens=5000).strip()
        check = (lambda t: L.field_clean(t)) if aud == "field" else (lambda t: [b for b in L.field_clean(t) if b in ("claude", "automation", "/users/", "pipeline", "csv")])
        bad = check(text)
        if bad:
            text = L.ask(prompt + "\n\nYour last draft named %s — rewrite without any system/tool/file names:\n%s" % (bad, text),
                         system=SYSTEM, max_tokens=5000).strip()
            bad = check(text)
        if not bad and text.startswith(":date:"):
            # Rule 18 self-check: every figure, date and claim must be in this channel's posts and the draft must not
            # contradict itself (the first render had "busiest day: Sep 21" beside "no walk posted for Sep 21").
            v = L.ask_json(VERIFY.format(post=text, msgs=blob[-60000:] + (("\n\nLAST MONTH'S RECAP IN THIS CHANNEL (valid source for the month-over-month line):\n" + prior[0][:1500]) if prior else "")), system=SYSTEM, max_tokens=6000)
            if not v.get("ok"):
                print("verify #%s: %s" % (name, v.get("problems")))
                fixed = (v.get("fixed") or "").strip()
                if fixed.startswith(":date:"):
                    text = fixed
                else:
                    rows.append((name, "skipped-verify", "; ".join(v.get("problems") or [])[:200]))
                    L.ledger(TASK, "#%s Month in Review for %s was held (figures did not check out)" % (name, label)) if not render else None
                    continue
        text = drop_people_lines(text, TASK)   # never a Davis / former employee (2026-10-21)
        if bad or not text.startswith(":date:"):
            rows.append((name, "skipped-rule16", ",".join(bad) or "shape"))
            L.ledger(TASK, "#%s Month in Review for %s was held (wording check)" % (name, label)) if not render else None
            continue
        sent = L.post(TASK, ch, text, render, label=name)
        rows.append((name, ("RENDERED" if render else ("POSTED" if sent is True else "DRY-RUN (diverted, not posted)")) if sent else "send-failed", cnt + ("; duplicate exists (render ignores)" if dup else "")))
    table = "\n".join("| #%s | %s | %s |" % r for r in rows)
    print(table)
    if not render:
        os.makedirs(RUNLOG_DIR, exist_ok=True)
        p = os.path.join(RUNLOG_DIR, "%s Month in Review.md" % period)
        with open(p, "a") as f:
            f.write("\n# Native run — monthly-eom-recap — %s\n\nTarget month: %s.\n\n| Channel | Result | Note |\n|---|---|---|\n%s\n"
                    % (L.now().strftime("%Y-%m-%d %H:%M ET"), label, table))
    return 0


if __name__ == "__main__":
    sys.exit(main())
