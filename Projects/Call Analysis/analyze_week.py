#!/usr/bin/env python3
"""
analyze_week.py — turn a week of structured customer-call records into the weekly rollup.

INPUT is already anonymous. By the time records reach this script the transcripts are gone
(see Zoom Call Pipeline/zoom_ingest.py). There is no name, number or quote to handle here,
and nothing in this file should ever try to reconstruct one.

RULE 18 — completeness gate. If the week's ingest is incomplete (a missing day, a store
whose line was down, a transcription failure run), this exits 1 and publishes NOTHING.
A partial week presented as a whole one sends real money at the wrong inventory. Silence
beats a wrong demand signal.

ONLY 3 OF 5 STORES ARE ON ZOOM PHONE (HAR, WAY, LEX). Culpeper and Roanoke are still on
Verizon and record nothing. Every output labels this. Never present a 3-store figure as a
company figure.

USAGE
    python3 analyze_week.py                  # the week that ended yesterday
    python3 analyze_week.py --week 2026-09-01
    python3 analyze_week.py --json           # machine output, no formatting
"""

import os
import sys
import json
import glob
import argparse
import datetime
from collections import Counter, defaultdict

PIPE = os.path.expanduser("~/Documents/Claude/Projects/Zoom Call Pipeline/out/customer")
OUT = os.path.expanduser("~/Documents/Claude/Projects/Call Analysis/weekly")

RECORDING_STORES = ["HAR", "WAY", "LEX"]        # live on Zoom Phone
NOT_RECORDING = ["CUL", "ROA"]                  # still on Verizon

# HAR/WAY/LEX are closed Wednesday and Sunday (valley-pawn-context, Store Hours).
# A closed day produces zero recordings and therefore no output file — that is
# expected, not a gap. Only flag a missing file on a day the stores were open.
# Python weekday(): Monday=0 ... Wednesday=2 ... Sunday=6.
CLOSED_WEEKDAYS = {2, 6}

CATEGORY_LABEL = {
    "gaming_console": "Gaming consoles", "gold_jewelry": "Gold & jewelry",
    "silver_coins": "Silver & coins", "diamond": "Diamonds", "firearm": "Firearms & ammo",
    "tools": "Tools", "electronics": "Electronics", "instrument": "Instruments",
    "jewelry_watch": "Watches", "other": "Other",
}
STORE_LABEL = {"HAR": "Harrisonburg", "WAY": "Waynesboro", "LEX": "Lexington"}


def week_bounds(anchor=None):
    """Monday..Sunday of the most recently COMPLETED week."""
    if anchor:
        mon = datetime.date.fromisoformat(anchor)
        mon -= datetime.timedelta(days=mon.weekday())
    else:
        today = datetime.date.today()
        mon = today - datetime.timedelta(days=today.weekday() + 7)
    return mon, mon + datetime.timedelta(days=6)


def load(mon, sun):
    """Load the week. Returns (records, missing_days)."""
    recs, missing = [], []
    d = mon
    while d <= sun:
        p = os.path.join(PIPE, d.isoformat() + ".jsonl")
        if not os.path.exists(p):
            if d.weekday() not in CLOSED_WEEKDAYS:
                missing.append(d.isoformat())
        else:
            with open(p, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            recs.append(json.loads(line))
                        except json.JSONDecodeError:
                            missing.append(d.isoformat() + " (corrupt row)")
        d += datetime.timedelta(days=1)
    return recs, missing


def analyze(recs):
    real = [r for r in recs if not r.get("spam")]
    spam_n = len(recs) - len(real)

    asked = Counter(r.get("category", "other") for r in real)
    missed = Counter(r.get("category", "other") for r in real
                     if r.get("outcome") == "not_in_stock")
    turned_away = [r for r in real if r.get("outcome") == "we_dont_take"]

    # Qualifying-script adherence, measured ONLY on calls where the script applies.
    qual_pool = [r for r in real if r.get("intent") in ("sell_or_pawn", "price_quote")]
    qual_yes = sum(1 for r in qual_pool if r.get("qualifying_questions_asked"))

    by_store = defaultdict(lambda: {"calls": 0, "spam": 0})
    for r in recs:
        s = by_store[r.get("store", "UNK")]
        s["calls"] += 1
        if r.get("spam"):
            s["spam"] += 1

    return {
        "total_calls": len(recs),
        "real_calls": len(real),
        "spam_calls": spam_n,
        "spam_pct": round(100.0 * spam_n / len(recs), 1) if recs else 0.0,
        "asked_about": asked.most_common(),
        "not_in_stock": missed.most_common(),
        "turned_away_total": len(turned_away),
        "turned_away_by_category": Counter(
            r.get("category", "other") for r in turned_away).most_common(),
        "qualifying_pool": len(qual_pool),
        "qualifying_asked": qual_yes,
        "qualifying_pct": round(100.0 * qual_yes / len(qual_pool), 1) if qual_pool else None,
        "by_store": {k: v for k, v in sorted(by_store.items())},
        "intents": Counter(r.get("intent", "other") for r in real).most_common(),
    }


def render(a, mon, sun):
    """Plain-language Slack post. Field Communication Standard v3 — no system names, no
    employee names, no customer anything, ~100 words, one takeaway first."""
    stores = ", ".join(STORE_LABEL[s] for s in RECORDING_STORES)
    L = []
    L.append("📞 *Phone — week of %s*  (%s)" % (mon.strftime("%b %-d"), stores))
    L.append("")
    L.append("%d calls · %d%% were spam/robocalls"
             % (a["total_calls"], round(a["spam_pct"])))
    L.append("")
    L.append("*Most asked about*")
    miss = dict(a["not_in_stock"])
    for cat, n in a["asked_about"][:4]:
        m = miss.get(cat, 0)
        L.append("• %s — %d calls%s"
                 % (CATEGORY_LABEL.get(cat, cat), n,
                    (", we had none %d times" % m) if m else ""))
    if a["turned_away_total"]:
        top = ", ".join("%s (%d)" % (CATEGORY_LABEL.get(c, c), n)
                        for c, n in a["turned_away_by_category"][:3])
        L.append("")
        L.append("Turned away %d times — mostly %s" % (a["turned_away_total"], top))
    if a["qualifying_pct"] is not None:
        L.append("")
        L.append("Qualifying questions asked on %d%% of loan/buy calls"
                 % round(a["qualifying_pct"]))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--week")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    mon, sun = week_bounds(args.week)
    recs, missing = load(mon, sun)

    # RULE 18 GATE — withhold, don't caveat.
    if missing:
        sys.stderr.write(
            "INCOMPLETE WEEK %s..%s — missing: %s\nPublishing nothing (Rule 18).\n"
            % (mon, sun, ", ".join(missing)))
        return 1
    if not recs:
        sys.stderr.write("No calls in %s..%s. Publishing nothing.\n" % (mon, sun))
        return 1

    seen = {r.get("store") for r in recs}
    absent = [s for s in RECORDING_STORES if s not in seen]
    if absent:
        sys.stderr.write(
            "INCOMPLETE — no calls at all from %s this week. That is a line outage or an\n"
            "ingest gap, not a quiet store. Publishing nothing (Rule 18).\n"
            % ", ".join(STORE_LABEL[s] for s in absent))
        return 1

    a = analyze(recs)
    a["week_start"] = mon.isoformat()
    a["week_end"] = sun.isoformat()
    a["stores_covered"] = RECORDING_STORES
    a["stores_not_recording"] = NOT_RECORDING

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, mon.isoformat() + ".json"), "w", encoding="utf-8") as f:
        json.dump(a, f, indent=2)

    print(json.dumps(a, indent=2) if args.json else render(a, mon, sun))
    return 0


if __name__ == "__main__":
    sys.exit(main())
