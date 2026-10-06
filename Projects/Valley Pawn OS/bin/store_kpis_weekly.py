#!/usr/bin/env python3
"""store_kpis_weekly.py [--render] [--end YYYY-MM-DD] — native replacement for Cowork `weekly-store-kpis`
(Mon 10:30 ET, 2026-10-05). The SKILL's steps, nothing re-derived:
  1 ENDDATE = yesterday. Reuse the newest complete 5-store output/<D>_<STORE>_end-of-month.xlsx set dated
    ENDDATE..ENDDATE-2 (Bravo stamps a Sunday pull with Saturday's date — see store_rankings.py). None on disk
    -> ONE pull: bin/bravo_pull.sh end-of-month <FIRST>..<ENDDATE> all 5 stores, then look again.
  2 COMPILE with the existing Bravo Data Extraction/store_kpis_compile.py <D> (all 8 metrics + ranks + the
    two message files). "INCOMPLETE" = post nothing, one ledger row.
  3 POST msg1 to #store-performance, msg2 as a thread reply with reply_broadcast — the locked two-message
    format. Text is converted the way Claude's Slack connector converted it (single *bold* -> _italic_,
    emoji -> :shortcode:), so the post is byte-identical to the Cowork-era posts.
De-dupe: the same leaderboard is ALSO posted by the native Monday compile (store_rankings.py, 08:45). If a
"Report Period: <D> (month-to-date)" post is already in the channel in the last 20 h, this run posts nothing.
That is intended: on 2026-10-05 the channel got the same leaderboard three times.
"""
import datetime as dt
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

AGENT = "weekly-store-kpis"
os.environ["VP_TASK"] = AGENT
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
BRAVO = os.environ.get("VP_BRAVO_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
COMPILE = os.environ.get("VP_KPI_COMPILE") or os.path.join(BRAVO, "store_kpis_compile.py")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
CH = "C03CGTN3KN1"   # #store-performance
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
EMOJI = {"🥇": ":first_place_medal:", "🥈": ":second_place_medal:", "🥉": ":third_place_medal:", "📊": ":bar_chart:",
         "🏆": ":trophy:", "💡": ":bulb:", "👇": ":point_down:"}


def ledger(sentence):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def complete_set(end):
    for back in range(0, 3):
        d = (end - dt.timedelta(days=back)).isoformat()
        ps = [os.path.join(BRAVO, "output", "%s_%s_end-of-month.xlsx" % (d, s)) for s in STORES]
        if all(os.path.exists(p) and os.path.getsize(p) >= 500 for p in ps):
            return d
    return None


def connectorize(text):
    """What Claude's Slack connector did to the SKILL's message files: emoji -> :code:, *x* -> _x_,
    with a leading :code: kept outside the italics (raw text of the 2026-10-05 10:37 post)."""
    for k, v in EMOJI.items():
        text = text.replace(k, v)
    text = re.sub(r"(?<![\w*])\*(?=\S)([^*\n]+?)(?<=\S)\*(?![\w*])", r"_\1_", text)
    text = re.sub(r"_(:[a-z_]+:) ", r"\1 _", text)
    return text


def main():
    render = "--render" in sys.argv
    end = dt.datetime.now(ET).date() - dt.timedelta(days=1)
    if "--end" in sys.argv:
        end = dt.date.fromisoformat(sys.argv[sys.argv.index("--end") + 1])
    d = complete_set(end)
    if d is None and not render:
        first = end.replace(day=1)
        subprocess.run(["/bin/bash", os.path.join(BIN, "bravo_pull.sh"), "end-of-month", "%s..%s" % (first, end),
                        ",".join(STORES), "wskpi-native-%s" % dt.datetime.now(ET).strftime("%Y-%m-%dT%H-%M-%S")],
                       capture_output=True, text=True, timeout=7500)
        d = complete_set(end)
    if d is None:
        print("HOLD — no complete 5-store month-end set dated %s or up to 2 days before" % end)
        if not render:
            ledger("Weekly store KPIs for %s not posted — month-end data missing for one or more stores after a pull." % end)
        return 2
    p = subprocess.run(["/usr/bin/python3", COMPILE, d], capture_output=True, text=True, timeout=300)
    out = (p.stdout or "") + (p.stderr or "")
    if not out.startswith("OK"):
        print("HOLD — compile said:", out.strip()[:300])
        if not render:
            ledger("Weekly store KPIs for %s not posted — the compile reported: %s." % (d, out.strip().splitlines()[0][:120] if out.strip() else "no output"))
        return 2
    m1 = connectorize(open(os.path.join(BRAVO, "output", "%s_store_kpis_msg1.txt" % d), encoding="utf-8").read())
    m2 = connectorize(open(os.path.join(BRAVO, "output", "%s_store_kpis_msg2.txt" % d), encoding="utf-8").read())
    if render:
        print("=== RENDER ONLY (data %s) ===\n=== PARENT ===\n%s\n\n=== THREAD REPLY (broadcast) ===\n%s" % (d, m1, m2))
        return 0
    import vp_slack
    if vp_slack.has(CH, "Report Period: %s (month-to-date)" % d, 20):
        print("already posted for %s (Monday compile) — nothing to do" % d)
        return 0
    if vp_slack.dryrun_intercept("slack", CH, m1 + "\n\n--- thread reply ---\n" + m2):
        return 0
    r = vp_slack.call("chat.postMessage", {"channel": CH, "text": m1, "unfurl_links": False})
    if not r.get("ok"):
        ledger("Weekly store KPIs for %s were built but did not post (%s)." % (d, r.get("error")))
        return 1
    r2 = vp_slack.call("chat.postMessage", {"channel": CH, "text": m2, "thread_ts": r["ts"],
                                             "reply_broadcast": True, "unfurl_links": False})
    vp_slack.receipt("slack", CH, True, len(m1.encode()), m1.splitlines()[0][:120])
    if not r2.get("ok"):
        ledger("Weekly store KPIs summary posted for %s but the category breakdown reply failed (%s)." % (d, r2.get("error")))
        return 1
    print("posted weekly store KPIs for", d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
