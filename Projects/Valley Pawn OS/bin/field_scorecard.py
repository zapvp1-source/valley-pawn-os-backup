#!/usr/bin/env python3
"""Field Scorecard — Valley Pawn (native Layer-0, additive, 2026-09-16, Phase 0.4 of the fleet freeze).

WHY: FLEET_FREEZE_2026-09-16.md Rule 6 — "the definition of working" is this file showing every
Tier-1 publication on time and correct for 7 CONSECUTIVE DAYS. Before this script, "is the fleet
fixed" was a judgment call re-litigated every session. This makes it a fact on disk.

Runs OUTSIDE Claude (launchd, pure stdlib Python, zero Claude usage), same trust model as
registry_guard.py: it verifies against real output (Slack channel/DM history, or a file's mtime),
never against a scheduled task's lastRunAt (Rule 12 — the silent-mid-run-death class looks
healthy on lastRunAt alone).

Scope: ONLY the Tier-1 entries in fleet/tier1_tasks.json (the ~66 field-facing tasks that stayed
enabled through the diet). A task's coverage comes from fleet/expected_outputs.json (task,
output, channel_id/path, marker, cadence, grace_hours) — the same manifest fleet-guardian already
uses. This script does not add, remove, or edit expected_outputs.json entries; that stays a
Cowork-session job (additive-only, Rule 4).

Every run:
  1. Load tier1 ids + expected_outputs entries; keep only entries whose task is Tier-1.
  2. For each entry, find the most recent scheduled instance <= now (cadence parser below).
     If deadline (instance + grace_hours) hasn't passed yet -> PENDING (not a miss, don't check).
     If deadline has passed -> check the real output:
       - slack:/slack-dm: -> conversations.history on channel_id since the instance time, marker
         substring match (bot messages included).
       - file -> path exists AND mtime >= instance time (loosely: within grace of the deadline).
     Marker/mtime present -> OK. Absent -> MISSED.
  3. Write fleet/FIELD_SCORECARD.md (current status table, newest run at top note).
  4. Maintain fleet/FIELD_SCORECARD_HISTORY.json — one boolean per calendar date, written only
     once that date's window is fully closed (now >= date + CLOSE_HOURS) so a day is never marked
     clean before every entry's grace has actually elapsed, and never flipped after. This is the
     ledger the 7-consecutive-clean-day freeze-exit criterion reads.
  5. ONE plain-language DM to Joshua (Rule 16 — no task ids/jargon in the DM body itself beyond a
     human label) only when this run finds a NEW miss not already DMed today. Silent when clean.

Retired/unverified/quarterly-not-yet-due entries are reported as SKIPPED, never as a miss.

Report:   Valley Pawn OS/fleet/FIELD_SCORECARD.md
History:  Valley Pawn OS/fleet/FIELD_SCORECARD_HISTORY.json
Heartbeat: ~/Library/Logs/valleypawn/field-scorecard.log
Flags: --dry-run (no DM, no history write, print report to stdout)
"""
import datetime as dt
import getpass
import glob
import json
import os
import re
import subprocess
import sys
import urllib.request

HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
TIER1_PATH = os.path.join(OS_DIR, "fleet/tier1_tasks.json")
OUTPUTS_PATH = os.path.join(OS_DIR, "fleet/expected_outputs.json")
REPORT = os.path.join(OS_DIR, "fleet/FIELD_SCORECARD.md")
HISTORY = os.path.join(OS_DIR, "fleet/FIELD_SCORECARD_HISTORY.json")
LOG_DIR = os.path.join(HOME, "Library/Logs/valleypawn")
HB_LOG = os.path.join(LOG_DIR, "field-scorecard.log")
STATE = os.path.join(LOG_DIR, "field_scorecard_state.json")

JOSHUA_USER = "U03BB52MDSA"
KEYCHAIN_SERVICE = "vp-ops-slack-bot-token"
CLOSE_HOURS = 32          # a calendar date's window is considered fully closed this many hours
                          # after that date's midnight — covers the longest grace_hours (30) plus margin
LOOKBACK_DAYS = {"daily": 2, "weekdays": 4, "weekly": 9, "monthly": 40, "quarterly": 100}
FRESH_MISS_HOURS = 30     # a miss older than this is history (ledger only) — no DM, no channel notice
NOTICES_ENABLED = False   # Phase 0.5 delay notices: OFF (2026-09-17). See the block in main() for why.
                          # The scorecard stays silent in team channels; it reports to the file + Joshua only.

# Plain-language names for the delayed-notice line (Rule 16: no task ids or jargon in team
# channels). Anything not listed falls back to the task id with hyphens replaced.
FRIENDLY = {
    "pawn-walk": "pawn walk", "daily-items-to-price": "items-to-price list",
    "daily-clockin-check": "clock-in check", "daily-dress-code-check": "dress code check",
    "daily-cloudcover-check": "music check", "daily-funds-verification": "funds verification",
    "chekkit-unanswered-alert": "response summary", "chekkit-unanswered-eod-followup": "end-of-day follow-up",
    "daily-unopened-email-eval": "unopened email check", "jewelry-onhand-nightly-pull": "jewelry count",
    "weekly-store-kpis": "store performance rankings", "weekly-returns-summary": "returns summary",
    "weekly-timekeeping-analysis": "timekeeping summary", "review-obtained-last-week": "Google reviews ranking",
    "nics-weekly-mtd-ranking": "FFL transfers month-to-date", "layaway-yield-weekly": "layaway yield",
    "monday-bravo-combined-compile": "store rankings", "monday-bravo-postcheck": "past-due loan review",
    "weekly-markdown-verification-review": "markdown check", "monthly-scrap-rankings": "scrap rankings",
    "monthly-employee-sales-rankings": "employee sales rankings", "nics-monthly-ranking": "FFL transfers monthly",
    "monthly-analytics-report": "monthly business update", "monthly-eom-recap": "month in review",
    "vp-new-customer-report": "new customers report", "monthly-gun-audit-report": "gun audit summary",
}

DRY = "--dry-run" in sys.argv
os.makedirs(LOG_DIR, exist_ok=True)

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def now():
    return dt.datetime.now()


def hb(msg):
    line = now().strftime("%Y-%m-%d %H:%M:%S") + " " + msg
    with open(HB_LOG, "a") as f:
        f.write(line + "\n")
    print(line)


def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def save_json_atomic(path, data):
    if DRY:
        return
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


# ---------------------------------------------------------------- cadence parsing
def parse_hhmm(tok):
    tok = tok.replace("et", "")
    return int(tok[:2]), int(tok[2:4])


def candidates_for(cadence):
    """Return a list of (datetime) scheduled instances in the lookback window, most recent first.
    None if the cadence is retired/unparseable."""
    if not cadence or cadence.startswith("retired"):
        return None
    parts = cadence.split("-")
    kind = parts[0]
    today = now().date()
    try:
        if kind == "daily":
            h, m = parse_hhmm(parts[1])
            days = LOOKBACK_DAYS["daily"]
            return sorted((dt.datetime.combine(today - dt.timedelta(days=d), dt.time(h, m))
                           for d in range(days + 1)), reverse=True)
        if kind in ("weekdays", "monsat"):
            h, m = parse_hhmm(parts[1])
            days = LOOKBACK_DAYS["weekdays"]
            limit = 5 if kind == "weekdays" else 6   # Mon–Fri vs Mon–Sat
            out = []
            for d in range(days + 1):
                day = today - dt.timedelta(days=d)
                if day.weekday() < limit:
                    out.append(dt.datetime.combine(day, dt.time(h, m)))
            return sorted(out, reverse=True)
        if kind == "weekly":
            dayname, hhmm = parts[1], parts[2]
            if dayname not in WEEKDAYS:
                return None
            h, m = parse_hhmm(hhmm)
            target = WEEKDAYS.index(dayname)
            days = LOOKBACK_DAYS["weekly"]
            out = []
            for d in range(days + 1):
                day = today - dt.timedelta(days=d)
                if day.weekday() == target:
                    out.append(dt.datetime.combine(day, dt.time(h, m)))
            return sorted(out, reverse=True)
        if kind == "monthly":
            daytok, hhmm = parts[1], parts[2]
            n = int(re.sub(r"\D", "", daytok) or "1")
            h, m = parse_hhmm(hhmm)
            out = []
            y, mo = today.year, today.month
            for _ in range(3):  # this month + up to 2 back
                try:
                    out.append(dt.datetime(y, mo, n, h, m))
                except ValueError:
                    pass  # e.g. day 30/31 in a short month
                mo -= 1
                if mo == 0:
                    mo, y = 12, y - 1
            return sorted(out, reverse=True)
        if kind == "quarterly":
            daytok, hhmm = parts[1], parts[2]
            n = int(re.sub(r"\D", "", daytok) or "1")
            h, m = parse_hhmm(hhmm)
            out = []
            y, mo = today.year, today.month
            for _ in range(14):  # ~3.5 years back, cheap and simple
                if mo in (1, 4, 7, 10):
                    try:
                        out.append(dt.datetime(y, mo, n, h, m))
                    except ValueError:
                        pass
                mo -= 1
                if mo == 0:
                    mo, y = 12, y - 1
            return sorted(out, reverse=True)
    except Exception:
        return None
    return None


def most_recent_due(cadence):
    cands = candidates_for(cadence)
    if not cands:
        return None
    for c in cands:
        if c <= now():
            return c
    return None


# ---------------------------------------------------------------- output verification
def slack_token():
    try:
        r = subprocess.run(["security", "find-generic-password", "-s", KEYCHAIN_SERVICE,
                            "-a", getpass.getuser(), "-w"], capture_output=True, text=True, timeout=10)
        t = r.stdout.strip()
        if t.startswith("xox"):
            return t
    except Exception:
        pass
    t = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    return t if t.startswith("xox") else None


def slack_join(token, channel_id):
    """Best-effort self-heal: works for PUBLIC channels the bot can see but hasn't joined.
    No-op (silently fails) for private channels or channels the token can't see at all —
    those genuinely need a human to /invite the bot once."""
    try:
        req = urllib.request.Request(
            "https://slack.com/api/conversations.join",
            data=json.dumps({"channel": channel_id}).encode(),
            headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
        res = json.load(urllib.request.urlopen(req, timeout=20))
        return bool(res.get("ok"))
    except Exception:
        return False


def _history_call(token, channel_id, oldest):
    req = urllib.request.Request(
        "https://slack.com/api/conversations.history?" +
        "channel=%s&oldest=%s&limit=200" % (channel_id, oldest),
        headers={"Authorization": "Bearer " + token})
    return json.load(urllib.request.urlopen(req, timeout=20))


def slack_history_has_marker(token, channel_id, since_dt, marker, ci=False):
    oldest = str(since_dt.timestamp())
    if ci:
        marker = marker.lower()
    try:
        res = _history_call(token, channel_id, oldest)
    except Exception as e:
        return None, "history fetch failed: %s" % e
    if not res.get("ok") and res.get("error") == "not_in_channel":
        # self-heal: try to join (public channels only) and retry once
        if slack_join(token, channel_id):
            try:
                res = _history_call(token, channel_id, oldest)
            except Exception as e:
                return None, "history fetch failed after join: %s" % e
    if not res.get("ok"):
        err = res.get("error", "?")
        if err in ("channel_not_found", "not_in_channel"):
            return None, "slack error: %s (bot needs a one-time /invite to this channel, or channel_id is stale)" % err
        return None, "slack error: %s" % err
    for m in res.get("messages", []):
        text = m.get("text") or ""
        if ci:
            text = text.lower()
        if marker in text:
            return True, None
    return False, None


def check_entry(entry, instance):
    out = entry.get("output", "")
    marker = entry.get("marker", "")
    if out == "file":
        p = entry.get("path", "")
        # placeholders are expanded from the EXPECTED instance date, so a dated artifact
        # (guardian_runs/2026-09-16-*.json, monday-gapfill/2026-09-13.md) is looked up exactly
        p = (p.replace("{YYYY-MM-DD}", instance.strftime("%Y-%m-%d"))
              .replace("{YYYY-MM}", instance.strftime("%Y-%m")))
        matches = glob.glob(p) if "*" in p else ([p] if os.path.exists(p) else [])
        if not matches:
            return False, "file missing: %s" % p.replace(HOME, "~")
        try:
            mtime = max(dt.datetime.fromtimestamp(os.path.getmtime(x)) for x in matches)
        except Exception as e:
            return None, "mtime check failed: %s" % e
        if "{" in entry.get("path", ""):
            return True, None          # dated artifact exists for this instance — that is the proof
        if mtime >= instance:
            return True, None
        return False, "file stale (mtime %s, expected since %s)" % (mtime, instance)
    if out.startswith("slack:") or out.startswith("slack-dm:"):
        ch = entry.get("channel_id")
        if not ch:
            return None, "no channel_id on entry"
        tok = slack_token()
        if not tok:
            return None, "no slack token available"
        return slack_history_has_marker(tok, ch, instance, marker, bool(entry.get("marker_ci")))
    return None, "unrecognized output type: %s" % out


def friendly(task_id):
    return FRIENDLY.get(task_id, task_id.replace("-", " "))


def post_delay_notice(entry):
    """Phase 0.5: 'Today's [report] is delayed and will post when ready.' — one line, plain,
    in the publication's own channel. Returns True only if Slack accepted it."""
    text = "Today's %s is delayed and will post when ready." % friendly(entry["task"])
    if DRY:
        hb("DRY NOTICE -> %s: %s" % (entry.get("output"), text))
        return False
    tok = slack_token()
    if not tok:
        return False
    try:
        req = urllib.request.Request("https://slack.com/api/chat.postMessage",
                                     data=json.dumps({"channel": entry["channel_id"], "text": text}).encode(),
                                     headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
        res = json.load(urllib.request.urlopen(req, timeout=20))
        if res.get("ok"):
            hb("delay notice posted -> %s (%s)" % (entry.get("output"), entry["task"]))
            return True
        hb("delay notice NOT posted -> %s: %s" % (entry.get("output"), res.get("error")))
    except Exception as e:
        hb("delay notice failed -> %s: %s" % (entry.get("output"), e))
    return False


# ---------------------------------------------------------------- Slack DM
def dm_joshua(text):
    if DRY:
        hb("DRY DM: " + text)
        return
    tok = slack_token()
    if not tok:
        hb("no slack token; DM skipped: " + text)
        return
    try:
        req = urllib.request.Request("https://slack.com/api/conversations.open",
                                     data=json.dumps({"users": JOSHUA_USER}).encode(),
                                     headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
        ch = json.load(urllib.request.urlopen(req, timeout=20))["channel"]["id"]
        req = urllib.request.Request("https://slack.com/api/chat.postMessage",
                                     data=json.dumps({"channel": ch, "text": text}).encode(),
                                     headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=20).read()
        hb("DM sent")
    except Exception as e:
        hb("DM failed: %s" % e)


# ---------------------------------------------------------------- report + history
def write_report(rows, generated_at):
    lines = ["# Field Scorecard — Tier-1 publications\n",
             "Native, launchd, zero-Claude-usage (`bin/field_scorecard.py`). Verifies real Slack/file "
             "output against each publication's cadence + grace period — never just a scheduled task's "
             "`lastRunAt` (Rule 12). This is the single source of truth for FLEET_FREEZE_2026-09-16.md "
             "Rule 6 (\"working\" = every row here OK for 7 consecutive days).\n",
             "Generated: %s\n" % generated_at.strftime("%Y-%m-%d %H:%M:%S ET"),
             "| Task | Status | Expected | Note |",
             "|---|---|---|---|"]
    for r in rows:
        lines.append("| %s | %s | %s | %s |" % (
            r["task"], r["status"],
            r["instance"].strftime("%a %m/%d %H:%M") if r["instance"] else "—",
            (r["note"] or "").replace("|", "/")[:140]))
    tmp = REPORT + ".tmp"
    with open(tmp, "w") as f:
        f.write("\n".join(lines) + "\n")
    if not DRY:
        os.replace(tmp, REPORT)
    else:
        print(open(tmp).read())
        os.remove(tmp)


def update_history(rows):
    """For each calendar date represented among today's checked instances that is now fully
    closed (>= CLOSE_HOURS past that date's midnight), record clean/miss once, idempotently."""
    hist = load_json(HISTORY, {})
    changed = False
    by_date = {}
    for r in rows:
        # UNVERIFIED counts AGAINST a clean day: a day we could not verify is not a day we can
        # call clean (that is how "7 consecutive clean days" would otherwise be gamed by silence).
        if r["instance"] is None or r["status"] not in ("OK", "MISSED", "UNVERIFIED"):
            continue
        d = r["instance"].date().isoformat()
        by_date.setdefault(d, []).append(r["status"])
    for d, statuses in by_date.items():
        midnight = dt.datetime.strptime(d, "%Y-%m-%d")
        if now() < midnight + dt.timedelta(hours=CLOSE_HOURS):
            continue  # not fully closed yet
        rec = {"clean": all(s == "OK" for s in statuses), "checked": len(statuses),
               "missed": sum(1 for s in statuses if s == "MISSED"),
               "unverified": sum(1 for s in statuses if s == "UNVERIFIED")}
        old = hist.get(d)
        # monotone toward strictness: a recorded date may gain coverage or turn unclean,
        # but a date recorded unclean is never flipped back to clean.
        if old is None or (rec["checked"] > old.get("checked", 0) and not (old.get("clean") is False and rec["clean"])):
            if old is not None and old.get("clean") is False:
                rec["clean"] = False
            hist[d] = rec
            changed = True
    if changed:
        save_json_atomic(HISTORY, hist)
    # streak, most recent date backwards, stopping at the first gap or miss
    streak = 0
    for d in sorted(hist, reverse=True):
        if hist[d]["clean"]:
            streak += 1
        else:
            break
    return streak, hist


def main():
    tier1_doc = load_json(TIER1_PATH, {})
    tier1 = {tid for group in tier1_doc.get("tier1", {}).values() for tid in group}
    # The "infrastructure" group (pipeline pulls, guards, backups, index refreshes) has no
    # field-facing publication by nature — Rule 6 scores PUBLICATIONS, so these are listed
    # as INFRA rather than nagging for a manifest entry that can never be verified in Slack.
    infra = set(tier1_doc.get("tier1", {}).get("infrastructure", []))
    outputs = load_json(OUTPUTS_PATH, {})
    entries = [e for e in outputs.get("entries", []) if e.get("task") in tier1]
    covered = {e["task"] for e in entries}
    uncovered = sorted(tier1 - covered)

    state = load_json(STATE, {"dmed_today": {}, "noticed": {}})
    state.setdefault("noticed", {})
    today_key = now().strftime("%Y-%m-%d")
    if state.get("dmed_today", {}).get("_date") != today_key:
        state["dmed_today"] = {"_date": today_key}
    # keep the delay-notice dedupe from growing forever
    cutoff = (now() - dt.timedelta(days=14)).isoformat()
    state["noticed"] = {k: v for k, v in state["noticed"].items() if k.split("@", 1)[-1] >= cutoff}

    rows = []
    new_misses = []
    for e in entries:
        cadence = e.get("cadence", "")
        instance = most_recent_due(cadence)
        if instance is None:
            rows.append({"task": e["task"], "status": "SKIPPED", "instance": None,
                        "note": "retired, quarterly-not-yet-due, or unparseable cadence (%s)" % cadence})
            continue
        if e.get("output") == "slack-canvas":
            rows.append({"task": e["task"], "status": "CANVAS", "instance": instance,
                        "note": "canvas %s — freshness = its 'as of slack_date:' heading; not scored natively yet (Phase 1)" % e.get("canvas_id", "?")})
            continue
        if e.get("output", "").startswith("slack-dm:") or e.get("channel_id", "").startswith("D"):
            # A DM channel id belongs to ONE bot<->user pair. These tasks DM Joshua through the
            # Cowork Slack app, so the native vp_ops_engine bot can never read that thread.
            # Not a miss, not verifiable here — Phase 1 re-points these to a bot-visible
            # channel or a file artifact. Reported separately so it never pollutes the ledger.
            rows.append({"task": e["task"], "status": "DM-SURFACE", "instance": instance,
                        "note": "DMs Joshua via the Cowork bot; not readable by vp_ops_engine — re-point in Phase 1"})
            continue
        deadline = instance + dt.timedelta(hours=e.get("grace_hours", 4))
        if now() < deadline:
            rows.append({"task": e["task"], "status": "PENDING", "instance": instance,
                        "note": "due %s, grace not yet elapsed" % deadline.strftime("%H:%M")})
            continue
        ok, note = check_entry(e, instance)
        if ok is True:
            rows.append({"task": e["task"], "status": "OK", "instance": instance, "note": note})
        elif ok is False:
            rows.append({"task": e["task"], "status": "MISSED", "instance": instance, "note": note})
            key = "%s@%s" % (e["task"], instance.isoformat())
            fresh = (now() - instance) <= dt.timedelta(hours=FRESH_MISS_HOURS)
            # DM Joshua once per fresh miss. Older misses are history — the ledger records them,
            # nobody needs a message about last week (this is what made the old watchdogs noise).
            if fresh and state["dmed_today"].get(key) != True:
                new_misses.append((e["task"], instance))
                state["dmed_today"][key] = True
            # Phase 0.5 delayed-notice rule — DISABLED 2026-09-17 by Joshua's reaction to it in
            # #pawn-walks ("this is what we are getting"). Why it was wrong, so nobody rebuilds it:
            # the line promises "will post when ready", but NOTHING re-runs a missed publication —
            # there is no retry path — so the promise is false, and it re-posts every day the
            # underlying task stays dark (2 notices in #pawn-walks, 9/16 23:57 + 9/17 11:30, while
            # the real pawn walk had been dark since 9/12). That is Rule 16 (no failure notices to
            # team channels) wearing a friendlier hat, and Rule 18 (never post inaccurate data).
            # A delay notice may only be reconsidered once a publication can actually self-heal,
            # and even then it belongs to the task that will deliver, not to the scorecard.
            if NOTICES_ENABLED and fresh and e.get("output", "").startswith("slack:#") and state["noticed"].get(key) != True:
                if post_delay_notice(e):
                    state["noticed"][key] = True
        else:
            rows.append({"task": e["task"], "status": "UNVERIFIED", "instance": instance, "note": note})

    for tid in uncovered:
        if tid in infra:
            rows.append({"task": tid, "status": "INFRA", "instance": None,
                        "note": "infrastructure task — no field publication to score (registry-guard/fleet-health cover its health)"})
        else:
            rows.append({"task": tid, "status": "NO COVERAGE", "instance": None,
                        "note": "Tier-1 publication with no expected_outputs.json entry yet — add one verified against a real post (additive-only)"})

    rows.sort(key=lambda r: (r["status"] != "MISSED", r["task"]))
    write_report(rows, now())
    streak, hist = update_history(rows)
    save_json_atomic(STATE, state)

    missed_count = sum(1 for r in rows if r["status"] == "MISSED")
    hb("run: %d entries, %d ok, %d missed, %d unverified, %d pending, %d dm-surface, %d skipped, %d no-coverage, streak=%d"
       % (len(entries),
          sum(1 for r in rows if r["status"] == "OK"), missed_count,
          sum(1 for r in rows if r["status"] == "UNVERIFIED"),
          sum(1 for r in rows if r["status"] == "PENDING"),
          sum(1 for r in rows if r["status"] == "DM-SURFACE"),
          sum(1 for r in rows if r["status"] == "SKIPPED"),
          len(uncovered), streak))

    if new_misses:
        if len(new_misses) == 1:
            body = "One of today's reports didn't post on time: %s. Checking again next cycle." % friendly(new_misses[0][0])
        else:
            names = ", ".join(friendly(t) for t, _ in new_misses[:6])
            body = "%d of today's reports didn't post on time: %s. Checking again next cycle." % (len(new_misses), names)
        dm_joshua(body)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        hb("CRASH: %s: %s" % (type(e).__name__, e))
        import traceback
        hb(traceback.format_exc().replace("\n", " | "))
        sys.exit(1)
