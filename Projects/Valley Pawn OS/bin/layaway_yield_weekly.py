#!/usr/bin/env python3
"""layaway_yield_weekly.py [--render] [--end YYYY-MM-DD] [--force] — native port of Cowork `layaway-yield-weekly`
(agent com.valleypawn.layaway-yield-weekly, Mon 11:15 ET). Built render-only 2026-10-05; made live 2026-10-06
once the ops bot got canvases:write.

The SKILL's steps, nothing re-derived:
  1 ENDDATE = yesterday; REV 2.1 fallback = the freshest complete 5-store *_end-of-month.xlsx set.
  2 compile with the existing Bravo Data Extraction/layaway_yield_compile.py <D> -> <D>_layaway_yield.json
    (must say OK = all 5 stores; PARTIAL/ERROR = hold, one ledger row, nothing published)
  5 #layaway-review Canvas (F0BJ48BMZGQ): the "Layaway Yield % (MTD)" section after the Layaway Review table,
    before Full Details. The document is written whole from fleet/canvas_state/F0BJ48BMZGQ.json, which keeps
    the status + Layaway Review part exactly as weekly-layaway-review-canvas-refresh last published it
    (see weekly_canvases.py) — this task never changes that part's numbers.
  6 channel post to #layaway-review (format of the 2026-10-05 11:19 post) — only after the Canvas update
    is confirmed, since the post says "See the Canvas above"; then the one-line DM to Joshua.
Re-run safe: the post is skipped if this date's post is already in the channel (20 h).
"""
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TASK = "layaway-yield-weekly"
ET = ZoneInfo("America/New_York")
BRAVO = os.environ.get("VP_BRAVO_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
COMPILE = os.environ.get("VP_LY_COMPILE") or os.path.join(BRAVO, "layaway_yield_compile.py")
STORES = [("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke"), ("WAY", "Waynesboro")]
CH = "C04N24STDP1"          # #layaway-review
CANVAS = "F0BJ48BMZGQ"


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


def _row(x):
    return (usd(x["down_payments_mtd"]), usd(x["payments_mtd"]), usd(x["collected_mtd"]),
            usd(x["layaway_balance"]), "%.2f%%" % x["layaway_yield_pct"])


def canvas_section(d, j):
    out = ["# :moneybag: Layaway Yield % (MTD)", "",
           "(Down Payments + Payments) MTD ÷ Layaway Balance. As of %s." % dt.date.fromisoformat(d).strftime("%b %-d, %Y"), "",
           "|Store|Down Pmts MTD|Payments MTD|Collected MTD|Layaway Bal|Layaway Yield %|",
           "|  ---  |  ---  |  ---  |  ---  |  ---  |  ---  |"]
    for code, name in STORES:
        cells = _row(j["stores"][code]) if code in j["stores"] else ("—",) * 5
        out.append("|%s|%s|" % (name, "|".join(cells)))
    out.append("|**Company**|%s|" % "|".join("**%s**" % x for x in _row(j["company"])))
    return "\n".join(out)


def post_text(d, j):
    out = [":moneybag: _Layaway Yield %% (MTD)_ — updated %s" % d, "",
           "| Store | Down Pmts | Payments | Collected | Layaway Bal | Yield % |", "|---|---|---|---|---|---|"]
    for code, name in STORES:
        cells = _row(j["stores"][code]) if code in j["stores"] else ("—",) * 5
        out.append("| %s | %s |" % (name, " | ".join(cells)))
    out.append("| _Company_ | %s |" % " | ".join("_%s_" % x for x in _row(j["company"])))
    out += ["", "See the Canvas above for the running view."]
    return "\n".join(out)


def dm_text(d, j):
    return "✅ Layaway Yield Weekly %s: Company %.2f%% MTD, posted to #layaway-review." % (d, j["company"]["layaway_yield_pct"])


def ledger(sentence):
    import weekly_canvases as wc
    wc.ledger(TASK, sentence)


def main():
    os.environ["VP_TASK"] = TASK
    render = "--render" in sys.argv
    end = dt.datetime.now(ET).date() - dt.timedelta(days=1)
    if "--end" in sys.argv:
        end = dt.date.fromisoformat(sys.argv[sys.argv.index("--end") + 1])
    d = freshest(end)
    if not d:
        print("HOLD — no complete 5-store month-end set")
        if not render:
            ledger("Layaway yield for %s was not published because no store set of month-end figures was complete." % end)
        return 2
    p = subprocess.run(["/usr/bin/python3", COMPILE, d], capture_output=True, text=True, timeout=300)
    if not (p.stdout or "").startswith("OK"):
        print("HOLD — compile said:", (p.stdout + p.stderr).strip()[:300])
        if not render:
            ledger("Layaway yield for %s was not published because the figures were not complete for all 5 stores." % d)
        return 2
    j = json.load(open(os.path.join(BRAVO, "output", "%s_layaway_yield.json" % d)))
    if j.get("missing") or len(j.get("stores", {})) != 5:
        print("HOLD — stores missing:", j.get("missing"))
        if not render:
            ledger("Layaway yield for %s was not published because a store's figures were missing." % d)
        return 2
    post, section, dm = post_text(d, j), canvas_section(d, j), dm_text(d, j)

    import weekly_canvases as wc
    os.environ["VP_TASK"] = TASK
    st = wc.load_state(CANVAS)
    lay_md = st.get("layaway")
    if not lay_md:      # no state yet: rebuild the layaway part from the same data the 09:22 task uses
        try:
            lay_md, _ = wc.layaway_part(dt.datetime.now(ET).date().isoformat(), render)
        except wc.Hold as e:
            print("HOLD — layaway part unavailable:", e)
            if not render:
                ledger("Layaway yield for %s was not published because the layaway canvas section could not be rebuilt." % d)
            return 2
    doc = wc.compose_layaway(lay_md, section)
    if render:
        print("=== RENDER ONLY (data %s) ===\n=== #layaway-review post ===\n%s\n\n=== Canvas section ===\n%s\n\n"
              "=== Canvas document (whole) ===\n%s\n\n=== DM to Joshua ===\n%s" % (d, post, section, doc, dm))
        return 0

    import vp_slack
    ok = wc.canvas_write(TASK, CANVAS, doc)
    if ok is not True and ok != "dry":
        ledger("Layaway yield for %s was computed but the canvas update was not accepted (%s); nothing posted." % (d, ok))
        return 1
    if ok is True:
        st.update({"layaway": lay_md, "yield": section, "updated": dt.datetime.now(ET).isoformat()})
        wc.save_state(CANVAS, st)
    if "--force" not in sys.argv and vp_slack.has(CH, "Layaway Yield % (MTD)_ — updated %s" % d, 20):
        print("post for %s already in the channel — canvas refreshed, nothing posted" % d)
        return 0
    vp_slack.post(CH, post)
    vp_slack.post(vp_slack.dm_channel(vp_slack.JOSHUA), dm)
    print("published layaway yield for", d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
