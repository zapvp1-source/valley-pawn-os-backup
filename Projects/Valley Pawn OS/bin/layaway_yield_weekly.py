#!/usr/bin/env python3
"""layaway_yield_weekly.py --render [--end YYYY-MM-DD] — native port (RENDER ONLY, not installed) of Cowork
`layaway-yield-weekly` (Mon 11:15 ET). Built 2026-10-05; NOT live because the SKILL's Step 5 updates the
#layaway-review Canvas (F0BJ48BMZGQ) and the native bot token has no canvases:write scope (probe 10/5:
users:read, chat:write, im:write, channels:history, groups:history, incoming-webhook, files:read,
chat:write.customize). The channel post says "See the Canvas above", so posting without the Canvas update
would point the stores at last week's numbers. Once the scope is added this script can grow the live path.

What it does today (the SKILL's steps, nothing re-derived):
  1 ENDDATE = yesterday; REV 2.1 fallback = the freshest complete 5-store *_end-of-month.xlsx set.
  2 compile with the existing Bravo Data Extraction/layaway_yield_compile.py <D> -> <D>_layaway_yield.json
  3 print the channel post (format of the 2026-10-05 11:19 post), the Canvas section and the Joshua DM line.
"""
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
BRAVO = os.environ.get("VP_BRAVO_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
COMPILE = os.environ.get("VP_LY_COMPILE") or os.path.join(BRAVO, "layaway_yield_compile.py")
STORES = [("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke"), ("WAY", "Waynesboro")]


def usd(v):
    return "${:,.2f}".format(v)


def freshest(end):
    ok = lambda d: all(os.path.exists(p) and os.path.getsize(p) >= 500 for p in
                       [os.path.join(BRAVO, "output", "%s_%s_end-of-month.xlsx" % (d, c)) for c, _ in STORES])
    if ok(end.isoformat()):
        return end.isoformat()
    dates = sorted({os.path.basename(p).split("_")[0] for p in glob.glob(os.path.join(BRAVO, "output", "*_end-of-month.xlsx"))
                    if re.match(r"\d{4}-\d{2}-\d{2}_", os.path.basename(p))}, reverse=True)
    return next((d for d in dates if d <= end.isoformat() and ok(d)), None)


def main():
    if "--render" not in sys.argv:
        sys.exit("render only — see the docstring (Canvas step needs canvases:write)")
    end = dt.datetime.now(ET).date() - dt.timedelta(days=1)
    if "--end" in sys.argv:
        end = dt.date.fromisoformat(sys.argv[sys.argv.index("--end") + 1])
    d = freshest(end)
    if not d:
        print("HOLD — no complete 5-store month-end set")
        return 2
    p = subprocess.run(["/usr/bin/python3", COMPILE, d], capture_output=True, text=True, timeout=300)
    if not (p.stdout or "").startswith("OK"):
        print("HOLD — compile said:", (p.stdout + p.stderr).strip()[:300])
        return 2
    j = json.load(open(os.path.join(BRAVO, "output", "%s_layaway_yield.json" % d)))
    row = lambda x: (usd(x["down_payments_mtd"]), usd(x["payments_mtd"]), usd(x["collected_mtd"]),
                     usd(x["layaway_balance"]), "%.2f%%" % x["layaway_yield_pct"])
    post = [":moneybag: _Layaway Yield %% (MTD)_ — updated %s" % d, "",
            "| Store | Down Pmts | Payments | Collected | Layaway Bal | Yield % |", "|---|---|---|---|---|---|"]
    canvas = ["# :moneybag: Layaway Yield % (MTD)", "",
              "(Down Payments + Payments) MTD ÷ Layaway Balance. As of ![](slack_date:" + d + ").", "",
              "|Store|Down Pmts MTD|Payments MTD|Collected MTD|Layaway Bal|Layaway Yield %|",
              "|  ---  |  ---  |  ---  |  ---  |  ---  |  ---  |"]
    for code, name in STORES:
        cells = row(j["stores"][code]) if code in j["stores"] else ("—",) * 5
        post.append("| %s | %s |" % (name, " | ".join(cells)))
        canvas.append("|%s|%s|" % (name, "|".join(cells)))
    c = row(j["company"])
    post.append("| _Company_ | %s |" % " | ".join("_%s_" % x for x in c))
    canvas.append("|**Company**|%s|" % "|".join("**%s**" % x for x in c))
    post += ["", "See the Canvas above for the running view."]
    print("=== RENDER ONLY (data %s) ===\n=== #layaway-review post ===\n%s\n\n=== Canvas section ===\n%s\n\n=== DM to Joshua ===\n%s"
          % (d, "\n".join(post), "\n".join(canvas),
             "✅ Layaway Yield Weekly %s: Company %.1f%% MTD, posted to #layaway-review." % (d, j["company"]["layaway_yield_pct"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
