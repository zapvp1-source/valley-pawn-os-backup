#!/usr/bin/env python3
"""monthly_analytics_watchdog.py [YYYY-MM] [--render] — native `monthly-analytics-watchdog` (1st of month 07:00 ET;
Mac-first wave 3, 2026-10-19). The SKILL's corrected (2026-09-01, Rule 16/18) steps:
  2 scan #company-performance for today's "Monthly Business Update — <Month YYYY>" (the report's header since the
    2026-08-03 condensed layout; the SKILL's older "Monthly Analytics — <Month YYYY>" string is also accepted)
    -> found = exit silently
  3 missing -> diagnostics (prestage status, 30-file inventory, the report's working file, stuck claims) into
  5 monthly-analytics/<YYYY-MM> Watchdog.md (always written)
  4 ONE plain DM to Joshua only when the post is missing: "The <Month YYYY> company performance report needs another
    pull before it can go out — will post once it's ready." (once per month: fleet/state/analytics_watchdog_<ym>)
--render: everything except the DM and the state marker; prints the finding.
"""
import datetime as dt
import glob
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vp_slack   # noqa: E402

AGENT = "monthly-analytics-watchdog"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.dirname(HERE)
PROJ = os.path.dirname(OS_DIR)
BRAVO = os.environ.get("VP_BRAVO_DIR") or os.path.join(PROJ, "Bravo Data Extraction")
CH = "C0B26GD8D2R"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render = "--render" in sys.argv
    now = dt.datetime.now(ET)
    ym = args[0] if args else (now.date().replace(day=1) - dt.timedelta(days=1)).strftime("%Y-%m")
    y, m = map(int, ym.split("-"))
    month = dt.date(y, m, 1).strftime("%B %Y")
    found = False
    try:
        hist = vp_slack.call("conversations.history", params={"channel": CH, "limit": 20}).get("messages", [])
        midnight = dt.datetime.combine(now.date(), dt.time(), ET).timestamp()
        for msg in hist:
            t = msg.get("text") or ""
            if float(msg.get("ts", 0)) >= midnight and ("Monthly Business Update — %s" % month in t or "Monthly Analytics — %s" % month in t):
                found = True
    except Exception as e:   # noqa: BLE001
        read_err = str(e)
    else:
        read_err = ""
    wf_dir = os.path.join(OS_DIR, "monthly-analytics")
    os.makedirs(wf_dir, exist_ok=True)
    wf = os.path.join(wf_dir, "%s Watchdog.md" % ym)
    L = ["# Monthly Analytics Watchdog — %s (native)" % ym, "", "Run: %s | report month %s" % (now.strftime("%Y-%m-%d %H:%M ET"), month), ""]
    if found:
        L.append("Result: post found in #company-performance today — watchdog exited clean.")
        open(wf, "w").write("\n".join(L) + "\n")
        print("post found — clean")
        return 0
    L.append("Result: POST MISSING%s" % (" (channel read failed: %s)" % read_err if read_err else ""))
    pre = os.path.join(wf_dir, "%s Prestage.md" % ym)
    L += ["", "## Pre-stage", "", (open(pre).read()[:1500] if os.path.exists(pre) else "no Prestage.md for %s" % ym)]
    folder = os.path.join(BRAVO, "output", "monthly-analytics", ym)
    files = sorted(glob.glob(os.path.join(folder, "*.xlsx")))
    good = [f for f in files if os.path.getsize(f) >= 2048]
    L += ["", "## Sidecars: %d/30 present, %d >= 2 KB (%s)" % (len(files), len(good), folder)]
    rep = os.path.join(wf_dir, "%s Monthly Analytics.md" % ym)
    L += ["", "## Report working file", "", (open(rep).read()[-2500:] if os.path.exists(rep) else "none — the report never got as far as writing its working file")]
    stuck = [os.path.basename(p) for p in glob.glob(os.path.join(BRAVO, "triggers", "claimed", "*monthly-analytics*")) + glob.glob(os.path.join(BRAVO, "triggers", "claimed", "*prestage*"))]
    L += ["", "## Claimed triggers: %s" % (", ".join(stuck) or "none")]
    marker = os.path.join(OS_DIR, "fleet", "state", "analytics_watchdog_%s" % ym)
    dm = "The %s company performance report needs another pull before it can go out — will post once it's ready." % month
    if render:
        L.append("\n(render: DM not sent) would DM: %s" % dm)
        open(wf, "w").write("\n".join(L) + "\n")
        print("POST MISSING — would DM: %s" % dm)
        return 0
    if os.path.exists(marker):
        L.append("\nDM already sent this month — not repeated.")
    else:
        p = subprocess.run([sys.executable, os.path.join(HERE, "vp_slack.py"), "dm", dm], capture_output=True, text=True, timeout=60,
                           env=dict(os.environ, VP_TASK=AGENT))
        os.makedirs(os.path.dirname(marker), exist_ok=True)
        real = p.returncode == 0 and "DRY RUN" not in p.stdout   # a guard-diverted DM must not set the once-a-month marker
        if real:
            open(marker, "w").write(now.isoformat())
        L.append("\nDM %s" % ("sent" if real else "DRY RUN — diverted, not sent" if p.returncode == 0 else "failed: %s" % p.stderr.strip()[:200]))
    open(wf, "w").write("\n".join(L) + "\n")
    print("POST MISSING — diagnostics in %s" % wf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
