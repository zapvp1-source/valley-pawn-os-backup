#!/usr/bin/env python3
"""vp_textable.py — who may get a MARKETING text (carrier-safety rules, Joshua 2026-10-23: "yes ... lets insure that
the carriers dont block us"). Shared by the monthly "Shop Us Online" text lists and the forfeiture win-back texts.

  dnt_phones()            10-digit phones Bravo marks DNT (the customer told a store not to text them), from every
                          Bravo customer export on disk that carries the flag: chekkit-invites-range (dnt column)
                          and forfeiture-winback-comparison-contacts (SMS column). Newest row for a phone wins.
  recent_marketing(days)  phones we sent a marketing text to in the last N days (win-back sends + monthly campaign
                          lists already marked sent), so nobody gets two of our marketing texts back to back.
  MAX_PER_STORE_MONTH     2,000 = the texts included per location; Chekkit warns over 3,000 a month may be filtered.
Opt-outs (STOP) are still enforced by Chekkit itself; this only removes people before the upload.
CLI: vp_textable.py --stats
"""
import csv, datetime as dt, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
BRAVO_OUT = os.path.join(PROJ, "Bravo Data Extraction", "output")
FWB_RUNS = os.path.join(PROJ, "Email Refinement", "forfeiture_winback", "runs")
CAMPAIGN_PACKS = os.path.join(PROJ, "eBay Customer Campaign", "packs")
MAX_PER_STORE_MONTH = 2000
FREQ_DAYS = 14


def p10(p):
    d = re.sub(r"\D", "", p or "")
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    return d if len(d) == 10 and d[0] not in "01" else ""


def _fdate(path):
    m = re.match(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
    return m.group(1) if m else "0000-00-00"


def dnt_phones():
    latest = {}   # phone -> (file date, is_dnt)
    pats = [("*_chekkit-invites-range.csv", "phone", "dnt"),
            ("*_forfeiture-winback-comparison-contacts.csv", "Phone", "SMS")]
    for pat, pcol, fcol in pats:
        for f in glob.glob(os.path.join(BRAVO_OUT, pat)):
            d = _fdate(f)
            try:
                with open(f, newline="", encoding="utf-8-sig", errors="replace") as fh:
                    for r in csv.DictReader(fh):
                        p = p10(r.get(pcol))
                        if not p:
                            continue
                        flag = (r.get(fcol) or "").strip().upper() == "DNT"
                        old = latest.get(p)
                        # newest export wins; on the same date a DNT wins
                        if old is None or d > old[0] or (d == old[0] and flag):
                            latest[p] = (d, flag)
            except OSError:
                pass
    return {p for p, (d, flag) in latest.items() if flag}


def recent_marketing(days=FREQ_DAYS):
    cut = (dt.datetime.now() - dt.timedelta(days=days)).timestamp()
    out = set()
    for f in glob.glob(os.path.join(FWB_RUNS, "*", "chekkit_sent_*.txt")):
        if os.path.getmtime(f) >= cut:
            out |= {p10(l) for l in open(f, errors="replace") if p10(l)}
    for f in glob.glob(os.path.join(CAMPAIGN_PACKS, "*", "chekkit_sent.json")):
        if os.path.getmtime(f) >= cut:
            for c in glob.glob(os.path.join(os.path.dirname(f), "chekkit_*.csv")):
                with open(c, newline="", errors="replace") as fh:
                    out |= {p10(r.get("Phone")) for r in csv.DictReader(fh) if p10(r.get("Phone"))}
    return out


if __name__ == "__main__":
    if "--stats" in sys.argv:
        print(json.dumps({"dnt": len(dnt_phones()), "recent_marketing_%dd" % FREQ_DAYS: len(recent_marketing())}))
