#!/usr/bin/env python3
"""ebay_ratings_post.py [YYYY-MM] [--render] — native post half of `monthly-ebay-ratings-sweep` (1st 10:00 ET;
Mac-first wave 3, 2026-10-19). The data half already runs natively (bin/ebay_ratings_pull.sh, 09:45 on the 1st,
writes eBay/ebay-ratings-sweep-<YYYY-MM>.md). This reads that file (+ the prior month's), and posts the SKILL's
digest to #ebay-performance in the layout of the real 2026-10-02 post:
  title "eBay Store Ratings Sweep — all 5 accounts — <Month YYYY>", stores ranked by 12-month positive %, one line
  per store (score, 12-mo %, 1/6/12-mo pos/neu/neg, TRS, new neutral/negative flag), Seller Standards sentence with
  the SPECIFIC metrics driving any Below Standard store + next evaluation (~eval + 30 d, SKILL step 4 watch flag),
  "Vs. <prior month> sweep" (score / 12-mo % / level changes), and a rule-based "Bottom line".
Rule 18: a store whose feedback row is missing (PULL FAILED) is named plainly, never filled in. Dedupe on the
title (30 days). No post at all if fewer than 3 stores have data.
"""
import datetime as dt
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vp_slack   # noqa: E402

AGENT = "monthly-ebay-ratings-sweep"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.dirname(HERE)
EBAY = os.path.join(os.path.dirname(OS_DIR), "eBay")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
CH = "C0ANVN5KX4Y"
LEVEL = {"TOP_RATED": "Top Rated", "ABOVE_STANDARD": "Above Standard", "BELOW_STANDARD": "Below Standard"}
METRIC_NAME = {"Late Shipment": "late shipments", "Defect Rate": "defect rate", "Cases w/o Resolution": "cases closed without seller resolution",
               "Tracking On Time": "tracking uploaded on time"}
TARGET = {"Late Shipment": "target under 3%", "Defect Rate": "target under 2%", "Cases w/o Resolution": "target under 0.3%"}


def ledger(sentence):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def parse(path):
    """-> {store: {score, pct, trs, user, counts{1,6,12: (p,n,g)}, level, eval, metrics{}, below[]}} or None"""
    if not os.path.exists(path):
        return None
    t = open(path, encoding="utf-8", errors="replace").read()
    stores = {}
    for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*([A-Za-z]+)\s*\|\s*(\S+)\s*\|\s*([\d,]+|PULL FAILED[^|]*)\s*\|\s*([\d.]+)%?\s*\|\s*([^|]+?)\s*\|$", t, re.M):
        rank, store, user, score, pct, trs = m.groups()
        if "PULL FAILED" in score:
            stores[store] = {"failed": True, "user": user}
            continue
        stores[store] = {"user": user, "score": int(score.replace(",", "")), "pct": float(pct), "trs": trs.lower().startswith("yes"),
                         "counts": {}, "level": None, "eval": None, "metrics": {}, "below": []}
    for m in re.finditer(r"^### ([A-Za-z]+) — \S+\n.*?\n- Positive/Neutral/Negative — 1-mo: (\d+)/(\d+)/(\d+) · 6-mo: (\d+)/(\d+)/(\d+) · 12-mo: (\d+)/(\d+)/(\d+)", t, re.M):
        s = m.group(1)
        if s in stores and not stores[s].get("failed"):
            v = list(map(int, m.groups()[1:]))
            stores[s]["counts"] = {1: tuple(v[0:3]), 6: tuple(v[3:6]), 12: tuple(v[6:9])}
    ss = re.search(r"## Seller Standards\n\n\| Store \| Level \| Evaluated \| ([^\n]+)\|\n\|[-| ]+\|\n((?:\|[^\n]*\|\n?)+)", t)
    if ss:
        cols = [c.strip() for c in ss.group(1).split("|") if c.strip()]
        for line in ss.group(2).strip().splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3 or cells[0] not in stores or stores[cells[0]].get("failed"):
                continue
            d = stores[cells[0]]
            d["level"], d["eval"] = cells[1], cells[2]
            for name, val in zip(cols, cells[3:]):
                d["metrics"][name] = val
    for m in re.finditer(r"^- ([A-Za-z]+): (.+)$", t[t.find("Below standard on"):] if "Below standard on" in t else "", re.M):
        if m.group(1) in stores:
            stores[m.group(1)]["below"] = [x.strip() for x in m.group(2).split(",")]
    return stores


def metric_phrase(d, name):
    v = d["metrics"].get(name, "")
    m = re.match(r"([\d.]+)%\s*\((\d+)/(\d+)\)", v)
    if m:
        return "%s %s%% (%s of %s)" % (METRIC_NAME[name], m.group(1), m.group(2), m.group(3))
    return "%s %s" % (METRIC_NAME[name], v) if v and v != "—" else None


def below_key(txt):
    k = txt.lower()
    if "defect" in k: return "Defect Rate"
    if "case" in k: return "Cases w/o Resolution"
    if "late" in k: return "Late Shipment"
    if "tracking" in k: return "Tracking On Time"
    return None


def fmt_eval(iso):
    try:
        d = dt.date.fromisoformat(iso)
        return d.strftime("%b %-d"), (d + dt.timedelta(days=30)).strftime("%b %-d"), d + dt.timedelta(days=30)
    except ValueError:
        return iso, "", None


def build(ym, cur, prev, today):
    y, m = map(int, ym.split("-"))
    month = dt.date(y, m, 1).strftime("%B %Y")
    pm = dt.date(y, m, 1) - dt.timedelta(days=1)
    ok = [s for s, d in cur.items() if not d.get("failed")]
    failed = [s for s, d in cur.items() if d.get("failed")]
    ranked = sorted(ok, key=lambda s: (-cur[s]["pct"], -cur[s]["score"]))
    L = ["eBay Store Ratings Sweep — all 5 accounts — %s" % month, "", "Ranked by 12-month positive %:", ""]
    for i, s in enumerate(ranked, 1):
        d = cur[s]
        c = d["counts"]
        line = "%d. %s (%s) — Score %s | 12-mo positive: %.2f%%" % (i, s, d["user"], format(d["score"], ","), d["pct"])
        if c:
            line += " | 1-mo: %d/%d/%d · 6-mo: %d/%d/%d · 12-mo: %d/%d/%d" % (c[1] + c[6] + c[12])
        line += " | TRS: %s" % (":white_check_mark: Top Rated" if d["trs"] else "not showing")
        if c and (c[1][1] or c[1][2]):
            kinds = [k for k, n in (("neutral", c[1][1]), ("negative", c[1][2])) if n]
            line += " | :warning: new %s feedback in the past month" % " and ".join(kinds)
        L.append(line)
    if failed:
        L.append("Not pulled this run: %s — no numbers shown rather than a guess." % ", ".join(failed))
    # Seller Standards sentence
    lv = {}
    for s in ranked:
        if cur[s]["level"]:
            lv.setdefault(cur[s]["level"], []).append(s)
    ev = next((cur[s]["eval"] for s in ranked if cur[s]["eval"]), "")
    ev_txt, next_txt, next_date = fmt_eval(ev)
    parts = []
    for lvl in ("TOP_RATED", "ABOVE_STANDARD"):
        if lv.get(lvl):
            parts.append("%s %s" % (" and ".join(lv[lvl]), LEVEL[lvl]))
    for s in lv.get("BELOW_STANDARD", []):
        d = cur[s]
        drivers = [metric_phrase(d, k) for k in [below_key(b) for b in d["below"]] if k]
        drivers = [x for x in drivers if x]
        # also show late shipments if elevated and not already a driver
        if "Late Shipment" not in [below_key(b) for b in d["below"]] and metric_phrase(d, "Late Shipment"):
            drivers.append(metric_phrase(d, "Late Shipment"))
        parts.append("%s Below Standard — %s" % (s, ", ".join(drivers) if drivers else "see the seller level page"))
    if parts:
        L += ["", "Seller Standards (eBay evaluation of %s): %s. Next evaluation around %s." % (ev_txt, " · ".join(parts), next_txt)]
        if next_date and lv.get("BELOW_STANDARD") and 0 <= (next_date - today).days <= 10:
            L.append(":warning: %s re-evaluates within the next 10 days — a near-term one to watch, not just a standing issue."
                     % " and ".join(lv["BELOW_STANDARD"]))
    # vs prior month
    if prev:
        ups = [s for s in ranked if s in prev and not prev[s].get("failed") and cur[s]["score"] > prev[s]["score"]]
        downs = [s for s in ranked if s in prev and not prev[s].get("failed") and cur[s]["score"] < prev[s]["score"]]
        vs = []
        if len(ups) == len(ranked) and ranked:
            vs.append("all %d feedback scores up" % len(ranked))
        else:
            if ups: vs.append("feedback scores up at %s" % ", ".join(ups))
            if downs: vs.append("down at %s" % ", ".join(downs))
        for s in ranked:
            p = prev.get(s)
            if p and not p.get("failed") and p.get("level") and cur[s]["level"] and p["level"] != cur[s]["level"]:
                vs.append("%s moved %s from %s to %s at the %s evaluation"
                          % (s, "up" if ["BELOW_STANDARD", "ABOVE_STANDARD", "TOP_RATED"].index(cur[s]["level"]) > ["BELOW_STANDARD", "ABOVE_STANDARD", "TOP_RATED"].index(p["level"]) else "down",
                             LEVEL[p["level"]], LEVEL[cur[s]["level"]], ev_txt))
        big = max((s for s in ranked if cur[s]["counts"]), key=lambda s: cur[s]["counts"][1][0], default=None)
        if big and cur[big]["counts"][1][0] >= 50:
            vs.append("%s had the busiest month — %d positive feedbacks in the last 30 days" % (big, cur[big]["counts"][1][0]))
        if vs:
            L += ["", "Vs. %s sweep: %s." % (pm.strftime("%B"), ". ".join(v[0].upper() + v[1:] if i else v for i, v in enumerate(vs)))]
    # bottom line (rule-based)
    bl = []
    for s in lv.get("BELOW_STANDARD", []):
        d = cur[s]
        what = [METRIC_NAME[k] for k in [below_key(b) for b in d["below"]] if k]
        only = "the only account below standard" if len(lv["BELOW_STANDARD"]) == 1 else "below standard"
        fix = {"defect rate": "cut defects", "cases closed without seller resolution": "resolve open cases", "late shipments": "ship on time", "tracking uploaded on time": "upload tracking on time"}
        bl.append("• %s — %s; %s before the ~%s evaluation." % (s, only, " and ".join(fix.get(w, w) for w in what) or "see the seller level page", next_txt))
    for s in ranked:
        p = prev.get(s) if prev else None
        if p and p.get("level") == "BELOW_STANDARD" and cur[s]["level"] and cur[s]["level"] != "BELOW_STANDARD":
            worst = None
            for k in ("Late Shipment", "Defect Rate", "Cases w/o Resolution"):
                mm = re.match(r"([\d.]+)%", cur[s]["metrics"].get(k, ""))
                if mm and (worst is None or float(mm.group(1)) > worst[1]):
                    worst = (k, float(mm.group(1)))
            bl.append("• %s — off Below Standard; keep %s down%s to stay there." % (s, METRIC_NAME[worst[0]] if worst else "defects",
                      " (%.2f%%, %s)" % (worst[1], TARGET.get(worst[0], "")) if worst and worst[0] in TARGET else ""))
    for s in ranked:
        c = cur[s]["counts"]
        if c and (c[1][1] or c[1][2]):
            n = c[1][1] + c[1][2]
            bl.append("• %s — reply to the %s new %s feedback." % (s, "one" if n == 1 else n, " and ".join(k for k, v in (("neutral", c[1][1]), ("negative", c[1][2])) if v)))
    for s in ranked:
        if not cur[s]["trs"] and cur[s]["pct"] >= 99.5 and cur[s]["level"] != "BELOW_STANDARD":
            bl.append("• %s — still no Top Rated badge despite near-perfect feedback; worth checking its Seller Level page." % s)
    L += ["", "Bottom line:"] + (bl or ["• No account needs attention this month — keep shipping on time and answering cases."])
    return "\n".join(L), month


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render = "--render" in sys.argv
    today = dt.datetime.now(ET).date()
    ym = args[0] if args else today.strftime("%Y-%m")
    y, m = map(int, ym.split("-"))
    pym = (dt.date(y, m, 1) - dt.timedelta(days=1)).strftime("%Y-%m")
    cur = parse(os.path.join(EBAY, "ebay-ratings-sweep-%s.md" % ym))
    if not cur or len([s for s in cur if not cur[s].get("failed")]) < 3:
        print("HOLD — no usable ratings file for %s" % ym)
        if not render:
            ledger("This month's eBay ratings sweep could not be posted — the ratings data for %s is not on file." % ym)
        return 2
    prev = parse(os.path.join(EBAY, "ebay-ratings-sweep-%s.md" % pym)) or {}
    post, month = build(ym, cur, prev, today)
    if render:
        print("=== RENDER ONLY ===\n" + post)
        return 0
    os.environ["VP_TASK"] = AGENT
    if vp_slack.has(CH, "eBay Store Ratings Sweep — all 5 accounts — %s" % month, 24 * 30):
        print("already posted for", month)
        return 0
    tmp = "/tmp/ebay_ratings_post_%s.txt" % ym
    open(tmp, "w").write(post)
    p = subprocess.run([sys.executable, os.path.join(HERE, "vp_slack.py"), "post", CH, "--file", tmp],
                       capture_output=True, text=True, timeout=60, env=dict(os.environ, VP_TASK=AGENT))
    if p.returncode != 0:
        ledger("This month's eBay ratings sweep was built but did not post.")
        print("post failed:", p.stderr.strip()[:200])
        return 1
    print("posted", month)
    return 0


if __name__ == "__main__":
    sys.exit(main())
