#!/usr/bin/env python3
"""store_rankings.py <END-DATE YYYY-MM-DD> [--render] [--post-date D] — weekly store performance rankings
to #store-performance, natively. Replaces Step 4 of the Cowork Monday compile (2026-10-02).

FORMAT IS LOCKED (Joshua 2026-05-11: "Has to be same every week"). Two messages: the summary post, then a
thread reply (reply_broadcast) with all 8 categories + Company Totals — templates copied from the archived
monday-store-rankings SKILL and the real 2026-09-21 / 09-28 posts (italic `_..._` styling, as posted).

DEFINITIONS — verified to the penny against the 2026-09-28 post (data 9/1–9/27, CUL/HAR/WAY, all 6
numeric metrics) on 2026-10-02:
  Loan Balance       Ending Loan Base row, col 15        Inventory Balance  Ending Inventory Base, col 15
  Total Assets       loan + inventory                    Retail Sales       Taxable + Nontaxable Sales totals
  Pawn Service Chg   daily-summary "Total:" row, Interest+Fees column (col 6)
  Scrap Sales        |Refined (Cost of Sales)| Month column (col 23)
  Layaway Balance    Layaways block "Ending Balance" row, col 40
  Net Revenue MTD    service charges (Total: row) + Sales Revenue (Profit) total
Ranking: highest = #1; ties keep store order CUL, HAR, LEX, ROA, WAY (reproduces the posted averages);
a category where every store is equal counts in averages but awards no win; "out of 8" on every line.
Completeness: all 5 files present and >= 500 bytes, or nothing is posted (Rule 18).
"""
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.request

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack  # noqa: E402

AGENT = "monday-store-rankings"
BRAVO = os.environ.get("VP_BRAVO_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
CH = "C03CGTN3KN1"
STORES = [("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke"), ("WAY", "Waynesboro")]
CATS = ["Loan Balance", "Inventory Balance", "Total Assets (Inventory + Loan)", "Retail Sales Total Amt",
        "Pawn Service Charges", "Scrap Sales", "Layaway Balance", "Net Revenue MTD"]
MEDAL = {1: ":first_place_medal:", 2: ":second_place_medal:", 3: ":third_place_medal:", 4: "4th", 5: "5th"}


def money(v):
    s = str(v if v is not None else "").replace("$", "").replace(",", "").strip()
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try:
        f = float(s)
    except ValueError:
        return 0.0
    return -f if neg else f


def parse(path):
    """Values are read by ORDER within their labelled row, never by fixed column: Bravo shifts the whole
    sheet by a column between exports (9/27 vs 10/3 files differ by +1 everywhere)."""
    ws = openpyxl.load_workbook(path, data_only=True).active
    def nn(r):
        return [ws.cell(r, c).value for c in range(1, ws.max_column + 1) if ws.cell(r, c).value not in (None, "")]
    def find(pred, after=0, right=False):
        for r in range(after + 1, ws.max_row + 1):
            for c in range(1, ws.max_column + 1):
                v = ws.cell(r, c).value
                if isinstance(v, str) and pred(v.strip()) and (not right or c > 20):
                    return r
        return 0
    def at(r, i):
        v = nn(r) if r else []
        return money(v[i]) if len(v) > abs(i) - (0 if i >= 0 else 1) else 0.0
    loan = at(find(lambda v: v.startswith("Ending Loan Base")), 2)
    inv = at(find(lambda v: v.startswith("Ending Inventory Base")), 2)
    sa = find(lambda v: v == "Sales Activity")
    tx = at(find(lambda v: v == "Taxable Sales", after=sa), -1)
    ntx = at(find(lambda v: v == "Nontaxable Sales", after=sa), -1)
    psc = at(find(lambda v: v == "Total:"), 2)
    profit = at(find(lambda v: v.startswith("Sales Revenue (Profit)")), -1)
    scrap = abs(at(find(lambda v: v.startswith("Refined (Cost of Sales")), -1))
    lh = find(lambda v: v == "Layaways", right=True)
    lay = at(find(lambda v: v.startswith("Ending Balance"), after=lh, right=True), 4)
    vals = [loan, inv, loan + inv, tx + ntx, psc, scrap, lay, psc + profit]
    return [round(x, 2) for x in vals], ""


def usd(v):
    return "${:,.2f}".format(v)


def build(end):
    data, missing = {}, []
    for code, name in STORES:
        p = os.path.join(BRAVO, "output", "%s_%s_end-of-month.xlsx" % (end, code))
        if not os.path.exists(p) or os.path.getsize(p) < 500:
            missing.append(name)
            continue
        data[code], _ = parse(p)
    if missing:
        return None, None, missing
    order = [c for c, _ in STORES]
    ranks = {c: [] for c in order}
    wins = {c: 0 for c in order}
    per_cat = []
    for i, cat in enumerate(CATS):
        ranked = sorted(order, key=lambda c: -data[c][i])            # stable: ties keep store order
        all_tied = len({data[c][i] for c in order}) == 1
        for pos, c in enumerate(ranked, 1):
            ranks[c].append(pos)
        if not all_tied:
            wins[ranked[0]] += 1
        per_cat.append((cat, ranked, all_tied, i))
    avg = {c: sum(ranks[c]) / len(CATS) for c in order}
    overall = sorted(order, key=lambda c: avg[c])                     # stable on ties
    names = dict(STORES)
    lead, second, last = overall[0], overall[1], overall[-1]
    won = {c: [cat for cat, ranked, tied, i in per_cat if not tied and ranked[0] == c] for c in order}
    if "Loan Balance" in won[lead] and "Inventory Balance" in won[lead]:
        anchor = "the top loan book (%s) and inventory" % usd(data[lead][0])
    elif "Loan Balance" in won[lead]:
        anchor = "the top loan book (%s)" % usd(data[lead][0])
    elif won[lead]:
        anchor = "the top %s (%s)" % (won[lead][0], usd(data[lead][CATS.index(won[lead][0])]))
    else:
        anchor = "the best average rank"
    s2 = ("_%s_ pushed hardest on %s for 2nd." % (names[second], " and ".join(won[second])) if won[second]
          else "_%s_ held 2nd on consistency across the board." % names[second])
    worst_everywhere = all(ranked[-1] == last for cat, ranked, tied, i in per_cat if not tied)
    s3 = ("_%s_ finished 5th across the board — the focus for the week." if worst_everywhere
          else "_%s_ finished 5th overall — the focus for the week.") % names[last]
    summary = "_%s_ led the month with %d of 8 category wins, anchored by %s. %s %s" % (
        names[lead], wins[lead], anchor, s2, s3)
    parent = ["_Valley Pawn — Weekly Store Performance Rankings_",
              ":bar_chart: Report Period: %s (month-to-date)" % end, "",
              ":trophy: _Overall Store Rankings:_"]
    for pos, c in enumerate(overall, 1):
        parent.append("%s _%s_ — Avg Rank %.2f | %d category wins out of 8" % (MEDAL[pos], names[c], avg[c], wins[c]))
    parent += ["", ":bulb: _Quick Summary:_", summary, "", "Full ranked breakdown in thread :point_down:"]
    thread = [":bar_chart: _Full Category Rankings_", ""]
    for cat, ranked, tied, i in per_cat:
        thread.append("_%s_" % cat)
        if tied and data[ranked[0]][i] == 0:
            thread.append("All stores at $0.00 (no scrap activity for the period)" if cat == "Scrap Sales"
                          else "All stores at $0.00")
        else:
            for pos, c in enumerate(ranked, 1):
                thread.append("%s %s — %s" % (MEDAL[pos], names[c], usd(data[c][i])))
        thread.append("")
    tot = lambda i: sum(data[c][i] for c in order)
    thread += ["_Company Totals_",
               "Loan Balance: %s | Inventory Balance: %s | Layaway Balance: %s | Net Revenue MTD: %s" % (
                   usd(tot(0)), usd(tot(1)), usd(tot(6)), usd(tot(7)))]
    return "\n".join(parent), "\n".join(thread), []


def ledger(sentence):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                                % (dt.datetime.now().strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    end = args[0] if args else (dt.date.today() - dt.timedelta(days=1)).isoformat()
    # Bravo's End-of-Month export stops at the last CLOSED day, so a Sunday pull is stamped Saturday
    # (seen 2026-10-04: requested 10/1..10/4, files written as 2026-10-03_*). Use the newest complete
    # 5-store set dated END or up to 2 days before it, and label the period with THAT date (truthful).
    for back in range(0, 3):
        d = (dt.date.fromisoformat(end) - dt.timedelta(days=back)).isoformat()
        if all(os.path.exists(os.path.join(BRAVO, "output", "%s_%s_end-of-month.xlsx" % (d, c))) for c, _ in STORES):
            end = d
            break
    parent, thread, missing = build(end)
    if missing:
        print("HOLD — missing/undersized EOM files: %s" % ", ".join(missing))
        if "--render" not in sys.argv:
            ledger("Store rankings for %s held — month-end data missing for %s." % (end, ", ".join(missing)))
        return 2
    if "--render" in sys.argv:
        print("=== PARENT ===\n%s\n\n=== THREAD REPLY ===\n%s" % (parent, thread))
        return 0
    if vp_slack.has(CH, "Report Period: %s (month-to-date)" % end, 20) if hasattr(vp_slack, "has") else False:
        print("already posted for %s" % end)
        return 0
    r = vp_slack.call("chat.postMessage", {"channel": CH, "text": vp_slack.to_mrkdwn(parent), "unfurl_links": False})
    if not r.get("ok"):
        ledger("Store rankings for %s were built but did not post (%s)." % (end, r.get("error")))
        return 1
    r2 = vp_slack.call("chat.postMessage", {"channel": CH, "text": vp_slack.to_mrkdwn(thread), "thread_ts": r["ts"],
                                             "reply_broadcast": True, "unfurl_links": False})
    os.environ["VP_TASK"] = AGENT
    try:
        vp_slack.receipt("slack", CH, True, len(parent.encode()), parent.splitlines()[0][:120])
    except Exception:
        pass
    if not r2.get("ok"):
        ledger("Store rankings summary posted for %s but the category breakdown reply failed (%s)." % (end, r2.get("error")))
        return 1
    print("posted rankings for", end)
    return 0


if __name__ == "__main__":
    sys.exit(main())
