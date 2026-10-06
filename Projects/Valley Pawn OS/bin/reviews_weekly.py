#!/usr/bin/env python3
"""reviews_weekly.py [--week-ending YYYY-MM-DD] [--render] [--invites] [--probe]
Native replacement for Cowork `review-obtained-last-week` (+ its backstop `google-reviews-post-watchdog`).
READ-ONLY against Chekkit: GET /v1/leaderboard only — never calls a POST endpoint.

The SKILL's steps, nothing re-derived:
  1 prior week = Sunday..Saturday ending the Saturday before the publish Monday (IMMUTABLE)
  2 per store: new reviews in that window (Chekkit leaderboard location.reviews.total, the same number the
    dashboard's Location Leaderboard "Reviews" column shows for the "Last week" preset)
  3 per store overall rating (all-time leaderboard averageRating, one decimal)
  4 rank by new reviews desc, ties alphabetical; store names without the "Valley Pawn –" prefix
  5 post to #google-reviews C04NDE52U2G in the established format; duplicate guard: if a post for this
    week's range is already in the channel, post nothing
All-or-nothing: if any store's pull fails, nothing is posted and one FAILURE_LEDGER row is written.

  --render       print the post instead of sending it
  --invites      add "· N invitations sent" to each store line (not in the legacy format; off by default)
  --probe        print raw per-store numbers used (window, all-time) — for verification, never posted
  --week-ending  override the Saturday that ends the window (default: most recent Saturday before today)
"""
import datetime as dt
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

AGENT = "review-obtained-last-week"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
CH = "C04NDE52U2G"   # #google-reviews
BASE = "https://api.chekkit.io"
ALL_TIME_FROM = "2015-01-01"
STORES = [("CUL", "Culpeper"), ("WAY", "Waynesboro"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke")]


def ledger(sentence):
    try:
        with open(LEDGER, "a") as f:
            f.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                    % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def token(code):
    r = subprocess.run(["security", "find-generic-password", "-s", "vp-chekkit-token-" + code, "-w"],
                       capture_output=True, text=True)
    return r.stdout.strip()


def leaderboard(tok, frm, to):
    url = "%s/v1/leaderboard?from=%s&to=%s" % (BASE, frm, to)
    req = urllib.request.Request(url, method="GET", headers={
        "Authorization": "Bearer " + tok, "User-Agent": "ValleyPawnOps/1.0", "Accept": "application/json"})
    last = None
    for attempt in range(2):                      # retry once, as the SKILL did
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = json.load(r)
            loc = body["location"]
            return body, loc
        except urllib.error.HTTPError as e:
            last = "http %s" % e.code
        except Exception as e:                    # noqa: BLE001
            last = type(e).__name__
        time.sleep(3)
    raise RuntimeError(last)


def week(week_ending=None):
    if week_ending:
        sat = dt.date.fromisoformat(week_ending)
    else:
        today = dt.datetime.now(ET).date()
        sat = today - dt.timedelta(days=(today.weekday() - 5) % 7 or 7)   # most recent Saturday strictly before today
    if sat.weekday() != 5:
        sys.exit("week must end on a Saturday: %s" % sat)
    return sat - dt.timedelta(days=6), sat


def fmt_range(sun, sat):
    return "%s – %s, %d" % (sun.strftime("%b %d"), sat.strftime("%b %d"), sat.year)


def main():
    a = sys.argv[1:]
    render, invites, probe = "--render" in a, "--invites" in a, "--probe" in a
    we = a[a.index("--week-ending") + 1] if "--week-ending" in a else None
    sun, sat = week(we)
    title = "Google Reviews — Week of %s" % fmt_range(sun, sat)
    today = dt.datetime.now(ET).date()

    rows, failed = [], []
    for code, name in STORES:
        tok = token(code)
        if not tok:
            failed.append("%s (no saved key)" % name); continue
        try:
            _, wk = leaderboard(tok, sun.isoformat(), sat.isoformat())
            _, at = leaderboard(tok, ALL_TIME_FROM, today.isoformat())
        except RuntimeError as e:
            failed.append("%s (%s)" % (name, e)); continue
        n = int((wk.get("reviews") or {}).get("total") or 0)
        rating = (at.get("reviews") or {}).get("averageRating")
        rows.append({"code": code, "name": name, "n": n, "rating": rating,
                     "inv": int(wk.get("invitationsSent") or 0)})
        if probe:
            print("PROBE %s window %s..%s reviews=%s google=%s fb=%s avg=%s inv=%s | all-time total=%s avg=%s inv=%s"
                  % (code, sun, sat, n, wk["reviews"].get("google"), wk["reviews"].get("facebook"),
                     wk["reviews"].get("averageRating"), wk.get("invitationsSent"),
                     at["reviews"].get("total"), at["reviews"].get("averageRating"), at.get("invitationsSent")),
                  file=sys.stderr)
        time.sleep(0.5)

    if failed:
        msg = "Weekly Google reviews post for %s held — could not read %s." % (fmt_range(sun, sat), ", ".join(failed))
        if render:
            print("NOT POSTABLE: " + msg); return 1
        ledger(msg); print(msg, file=sys.stderr); return 1

    rows.sort(key=lambda r: (-r["n"], r["name"]))
    lines = ["*%s*" % title, "", "Ranked by new reviews received last week:", ""]
    for i, r in enumerate(rows, 1):
        rt = ("%.1f ★ overall" % float(r["rating"])) if r["rating"] is not None else "no rating yet"
        extra = (" · %d invitation%s sent" % (r["inv"], "" if r["inv"] == 1 else "s")) if invites else ""
        lines.append("%d. *%s* — %d new review%s (%s%s)" % (i, r["name"], r["n"], "" if r["n"] == 1 else "s", rt, extra))
    lines += ["", "Total new reviews this week: %d" % sum(r["n"] for r in rows)]
    text = "\n".join(lines)

    if render:
        print(text); return 0

    os.environ["VP_TASK"] = AGENT
    sys.path.insert(0, BIN)
    import vp_slack
    try:
        if vp_slack.has(CH, title, 24 * 6):
            print("already posted for %s — nothing to do" % fmt_range(sun, sat)); return 0
    except SystemExit as e:
        ledger("Weekly Google reviews post for %s held — could not check the channel for a duplicate." % fmt_range(sun, sat))
        print(e, file=sys.stderr); return 1
    try:
        vp_slack.post(CH, text)
    except SystemExit as e:
        ledger("Weekly Google reviews post for %s was built but did not post." % fmt_range(sun, sat))
        print(e, file=sys.stderr); return 1
    print("posted", title)
    return 0


if __name__ == "__main__":
    sys.exit(main())
