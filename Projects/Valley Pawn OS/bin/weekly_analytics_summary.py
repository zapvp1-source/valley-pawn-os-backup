#!/usr/bin/env python3
"""weekly_analytics_summary.py — native weekly-analytics-summary (2026-10-14, Google re-grant prep).

Same pipeline the SKILL's STEP 1 + STEP 3 describe, minus the browser fallback and minus Claude:
ga4_pull.py --week -> gsc_pull.py --week (merged as "search") -> format_weekly_website.py -> post the
formatter's stdout VERBATIM to #website (C0ASE9C0GQ0). Formatter exit 2 = post nothing.

    weekly_analytics_summary.py --render [--cached]   # print the post; --cached = use the week files already on disk
    weekly_analytics_summary.py --send                 # pull, render, post once per week (Mon 09:00 agent)

Failure policy v3: no DM. GA4 scope missing -> ONE ledger row "Google access needs one approval".
Anything else -> one ledger row. Dedupe: state file + "Weekly Website Analytics" already in #website (100 h).
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
OS_DIR = HOME / "Documents/Claude/Projects/Valley Pawn OS"
A = HOME / "Documents/Claude/Projects/Website/analytics"
PY = "/usr/bin/python3"
TASK = "weekly-analytics-summary"
CHANNEL = "C0ASE9C0GQ0"
MARKER = "Weekly Website Analytics"
LEDGER = OS_DIR / "fleet/FAILURE_LEDGER.md"
STATE = OS_DIR / "fleet/state/weekly_analytics_summary.json"
RENDER_DIR = OS_DIR / "fleet/test_output/weekly_analytics_render"


def now() -> dt.datetime:
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("America/New_York"))
    except Exception:
        return dt.datetime.now()


def ledger(sentence: str, needs: str = "no") -> None:
    with LEDGER.open("a") as f:
        f.write(f"| {now():%Y-%m-%d %H:%M ET} (native) | {TASK} | {sentence} | NEEDS_HUMAN: {needs} | OPEN |\n")


def run(args: list[str]) -> tuple[int, str, str]:
    p = subprocess.run([PY] + args, capture_output=True, text=True, timeout=600)
    return p.returncode, p.stdout, p.stderr


def build(cached: bool) -> tuple[int, str, str, str]:
    """-> (rc, body, period_end, why). rc 0 ok, 1 no Google access, 2 withhold/failure."""
    if not cached:
        rc, o, e = run([str(A / "bin/ga4_pull.py"), "--week"])
        if rc == 1:
            return 1, "", "", e.strip()
        if rc != 0:
            rc, o, e = run([str(A / "bin/ga4_pull.py"), "--week"])  # retry once
            if rc != 0:
                return (1 if rc == 1 else 2), "", "", "ga4_pull: " + e.strip()[-300:]
        grc, _, ge = run([str(A / "bin/gsc_pull.py"), "--week"])
    week = json.loads((A / "data/ga4/week_latest.json").read_text())
    end = week["period"]["end"]
    gpath = A / f"data/gsc/week_{end}.json"   # same last-full-week window as ga4_pull; absent = no Search block
    if gpath.exists():
        g = json.loads(gpath.read_text())
        if g.get("search"):
            week["search"] = g["search"]
    merged = A / f"data/ga4/week_merged_{end}.json"
    merged.write_text(json.dumps(week, indent=2))
    rc, body, err = run([str(A / "bin/format_weekly_website.py"), str(merged)])
    if rc != 0:
        return 2, "", end, "formatter: " + err.strip()[-300:]
    return 0, body, end, ""


def already_posted(end: str) -> bool:
    try:
        if end in json.loads(STATE.read_text()).get("sent", []):
            return True
    except (OSError, ValueError):
        pass
    r = subprocess.run([PY, str(OS_DIR / "bin/vp_slack.py"), "has", CHANNEL, MARKER, "100"],
                       capture_output=True, text=True, timeout=60)
    return r.returncode == 0


def main() -> int:
    send = "--send" in sys.argv
    cached = "--cached" in sys.argv and not send
    rc, body, end, why = build(cached)
    if rc == 1:
        print("NO ACCESS — " + why, file=sys.stderr)
        if send:
            ledger("Google access needs one approval — the weekly website numbers were not posted to #website.",
                   "yes, double-click 'Grant Google Access.command' in Valley Pawn OS and click Allow once")
        return 1
    if rc != 0:
        print("WITHHELD — " + why, file=sys.stderr)
        if send:
            ledger("The weekly website analytics post was withheld (numbers failed a check); nothing was posted to #website.")
        return 2
    if not send:
        RENDER_DIR.mkdir(parents=True, exist_ok=True)
        (RENDER_DIR / f"week_{end}.txt").write_text(body)
        sys.stdout.write(body)
        return 0
    if already_posted(end):
        print(f"already posted for week ending {end} — skip")
        return 0
    tmp = RENDER_DIR / f"send_{end}.txt"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(body)
    r = subprocess.run([PY, str(OS_DIR / "bin/vp_slack.py"), "post", CHANNEL, "--file", str(tmp)],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        ledger("The weekly website analytics post did not go out to #website (Slack refused it).")
        print("POST FAILED " + r.stderr.strip(), file=sys.stderr)
        return 2
    st = {}
    try:
        st = json.loads(STATE.read_text())
    except (OSError, ValueError):
        pass
    st.setdefault("sent", []).append(end)
    st["last"] = now().isoformat()
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=1))
    print(f"POSTED week ending {end}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
