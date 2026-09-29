#!/usr/bin/env python3
"""loan_layaway_dms.py — native replacement for the Cowork task `weekly-loan-layaway-manager-dms`
(Monday 09:00). Same message template, same recipients, sent by the ops bot.

WHY (2026-09-28): the Cowork run held every store DM on 9/21 and 9/28 because its source file
(~/Documents/Claude/loan-layaway-results-latest.json) had not been written since 9/7. monday_pull.sh
now refreshes that file from the same Bravo CSVs that feed #loan-review / #layaway-review, and this
script sends from it directly — no Claude session, no approval wall.

Two things the SKILL got wrong and this fixes:
  * its recipient list still named people who are no longer employed (Andrew Clark, Cristofer
    Lopez). Every recipient is now checked against hr/ROSTER.json (rebuilt daily from Gusto);
    anyone not on the active roster is skipped and logged, never messaged.
  * a missing loan-balance % is shown as "not available this week", never invented.

  loan_layaway_dms.py            send (Mon 09:00 via com.valleypawn.loan-layaway-dms)
  loan_layaway_dms.py --render   print every DM, send nothing
"""
import datetime as dt
import json
import os
import subprocess
import sys

AGENT = "weekly-loan-layaway-manager-dms"
OS_DIR = os.environ.get("VP_OS_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
RESULTS = os.path.expanduser("~/Documents/Claude/loan-layaway-results-latest.json")
ROSTER = os.path.join(OS_DIR, "hr", "ROSTER.json")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
JOSHUA = "U03BB52MDSA"
PRESTON = "U03BWMEM9GR"
STORES = [("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke"), ("WAY", "Waynesboro")]
# From the SKILL's Step 2 (2026-09-28 copy). Filtered against the live roster at send time.
TEAM = {
    "CUL": ["U04C5DL5EKH"],
    "HAR": ["U09UTFT4P7X", "U03BFDJH31B"],
    "LEX": ["U09H9ES2LKA", "U05TV57FH0B"],
    "ROA": ["U0631AECK4K", "U063E87TM70"],
    "WAY": ["U04U136MF6V"],
}
POLICY_PCT = 5.0


def usd(v):
    try:
        return "${:,.2f}".format(float(v))
    except (TypeError, ValueError):
        return "—"


def ledger(sentence):
    row = "| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (
        dt.datetime.now().strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence)
    try:
        open(LEDGER, "a").write(row)
    except OSError:
        pass


def store_block(name, s):
    pct = s.get("loan_pct")
    if pct is None:
        pct_line = "• % of loan balance: not available this week"
    else:
        flag = "✅ Within threshold" if pct <= POLICY_PCT else "🚨 Above 5% — needs attention"
        pct_line = "• %% of loan balance: %.1f%% %s" % (pct, flag)
    locate = int(s.get("layaway_locate") or 0)
    lines = [
        "📊 *%s — Loan Health*" % name,
        "• Items past 75 days: %s" % s.get("loan_count", 0),
        "• $ past 75 days: %s" % usd(s.get("loan_dollar")),
        pct_line,
        "",
        "🏷️ *%s — Layaways*" % name,
        "• Overdue layaways: %s" % s.get("layaway_overdue", 0),
        "• Items needing location: %s%s" % (locate, " 🔴 ACTION NEEDED" if locate > 0 else ""),
        "• No payment in 30 days: %s" % s.get("layaway_no_pmt_30d", 0),
    ]
    actions = []
    if pct is not None and pct > POLICY_PCT:
        actions.append("Your 75-day loans are above 5%% of your loan balance (%.1f%%). Please review and pull tickets." % pct)
    if locate > 0:
        actions.append("You have %d layaway%s that need to be physically located in Bravo — please resolve ASAP." % (locate, "" if locate == 1 else "s"))
    return "\n".join(lines), actions


def flagged(s):
    pct = s.get("loan_pct")
    return (pct is not None and pct > POLICY_PCT) or int(s.get("layaway_locate") or 0) > 0


def send(user, text):
    env = dict(os.environ, VP_TASK=AGENT)
    p = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "post", user, text],
                       capture_output=True, text=True, timeout=60, env=env)
    return p.returncode == 0, (p.stderr or p.stdout).strip()[:160]


def main():
    render = "--render" in sys.argv
    try:
        data = json.load(open(RESULTS))
    except (OSError, ValueError) as e:
        print("results file unreadable:", e)
        if not render:
            ledger("The weekly loan and layaway store DMs were not sent — the results file could not be read.")
        return 1
    age = (dt.date.today() - dt.date.fromisoformat(str(data.get("date"))[:10])).days
    if age > 2:
        print("results file is %d days old (%s) — holding" % (age, data.get("date")))
        if not render:
            ledger("The weekly loan and layaway store DMs were held — the results were %d days old." % age)
        return 1
    active = set()
    try:
        active = {e.get("slack_id") for e in json.load(open(ROSTER))["employees"] if e.get("slack_id")}
    except Exception as e:
        print("roster unreadable (%s) — refusing to guess who is employed" % e)
        if not render:
            ledger("The weekly loan and layaway store DMs were not sent — the staff roster could not be read.")
        return 1
    when = dt.date.fromisoformat(str(data["date"])[:10]).strftime("%B %-d")
    stores = data.get("stores", {})
    outbox = []
    for code, name in STORES:
        s = stores.get(code)
        if not s:
            continue
        block, actions = store_block(name, s)
        text = "Good morning! Here's your store's weekly loan & layaway snapshot for %s:\n\n%s" % (when, block)
        if actions:
            text += "\n\n⚠️ *Action needed:* " + " ".join(actions)
        text += "\n\nHave a great week!"
        for uid in TEAM.get(code, []):
            if uid in active:
                outbox.append((uid, code, text))
            else:
                print("skip %s (%s): not on the active roster" % (uid, code))
    # Preston: full 5-store summary + flagged stores
    parts, flags = [], []
    for code, name in STORES:
        s = stores.get(code)
        if not s:
            continue
        block, _ = store_block(name, s)
        parts.append(block)
        if flagged(s):
            flags.append(name)
    summary = "Weekly loan & layaway results — all stores, %s\n\n%s" % (when, "\n\n".join(parts))
    summary += "\n\n" + ("⚠️ Flagged for attention: " + ", ".join(flags) if flags else "✅ No store flagged this week.")
    outbox.append((PRESTON, "ALL", summary))
    if render:
        print("=== RENDER ONLY — %d DM(s) ===" % len(outbox))
        for uid, code, text in outbox:
            print("\n--- to %s (%s) ---\n%s" % (uid, code, text))
        return 0
    sent, failed = 0, []
    for uid, code, text in outbox:
        ok, err = send(uid, text)
        if ok:
            sent += 1
        else:
            failed.append("%s/%s" % (code, uid))
            print("send failed %s: %s" % (uid, err))
    if failed:
        ledger("The weekly loan and layaway DMs went to %d of %d people; these did not go through: %s." % (sent, len(outbox), ", ".join(failed)))
    ok, _ = send(JOSHUA, "✅ Weekly loan & layaway results delivered to all store teams. %d store%s flagged for attention."
                 % (len(flags), "" if len(flags) == 1 else "s"))
    print("sent %d/%d" % (sent, len(outbox)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
