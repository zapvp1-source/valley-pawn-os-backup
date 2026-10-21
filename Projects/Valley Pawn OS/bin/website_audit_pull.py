#!/usr/bin/env python3
"""website_audit_pull.py [--days 90] [--end YYYY-MM-DD] [--out PATH]
Read-only GA4 + Search Console deep pull for a full website audit (added 2026-10-20, additive).
Writes one JSON: totals, channels, device, landing pages, lead events by page/device/store, cities,
GSC queries/pages/devices, with a prior-period comparison. Nothing is posted; nothing is written to the site.
"""
import argparse, datetime as dt, json, os, sys
A = os.path.expanduser("~/Documents/Claude/Projects/Website/analytics/bin")
sys.path.insert(0, A)
import ga4_pull as G, gsc_pull as S  # noqa: E402

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--end", default=None)
    ap.add_argument("--out", default=os.path.expanduser("~/Documents/Claude/Projects/Website/AUDIT_2026-10-20/data_90d.json"))
    a = ap.parse_args()
    end = dt.date.fromisoformat(a.end) if a.end else dt.date.today() - dt.timedelta(days=1)
    start = end - dt.timedelta(days=a.days - 1)
    pend = start - dt.timedelta(days=1); pstart = pend - dt.timedelta(days=a.days - 1)
    s, e, ps, pe = map(str, (start, end, pstart, pend))
    LEADS = ["phone_click", "sms_click", "directions_click", "form_submit"]
    def rep(dims, mets, limit=50, filt=None, rng=(s, e)):
        body = {"dateRanges": [{"startDate": rng[0], "endDate": rng[1]}],
                "dimensions": [{"name": d} for d in dims], "metrics": [{"name": m} for m in mets], "limit": limit}
        if filt: body["dimensionFilter"] = filt
        r = G.run_report(body)
        return [[c["value"] for c in row["dimensionValues"]] + [c["value"] for c in row["metricValues"]] for row in r.get("rows", [])]
    inlist = lambda vals: {"filter": {"fieldName": "eventName", "inListFilter": {"values": vals}}}
    out = {"period": [s, e], "prior": [ps, pe]}
    out["totals"] = G.totals(s, e); out["totals_prior"] = G.totals(ps, pe)
    out["channels"] = G.channels(s, e); out["channels_prior"] = G.channels(ps, pe)
    out["top_pages"] = G.top_pages(s, e, 40)
    out["leads"] = G.leads(s, e); out["leads_prior"] = G.leads(ps, pe)
    out["device"] = rep(["deviceCategory"], ["sessions", "engagedSessions", "keyEvents", "averageSessionDuration"])
    out["landing"] = rep(["landingPage"], ["sessions", "engagedSessions", "keyEvents", "bounceRate"], 40)
    out["lead_by_page"] = rep(["pagePath", "eventName"], ["eventCount"], 100, inlist(LEADS))
    out["lead_by_device"] = rep(["deviceCategory", "eventName"], ["eventCount"], 20, inlist(LEADS))
    out["lead_by_channel"] = rep(["sessionDefaultChannelGroup", "eventName"], ["eventCount"], 40, inlist(LEADS))
    out["city"] = rep(["city"], ["sessions", "keyEvents"], 30)
    out["source_medium"] = rep(["sessionSourceMedium"], ["sessions", "keyEvents"], 30)
    out["events"] = rep(["eventName"], ["eventCount"], 50)
    out["commerce"] = rep(["eventName"], ["eventCount", "totalRevenue"], 10, inlist(["purchase", "add_to_cart", "begin_checkout", "view_item"]))
    out["monthly"] = rep(["yearMonth"], ["sessions", "keyEvents"], 24, rng=(str(end - dt.timedelta(days=364)), e))
    out["gsc_tot"] = S.query(s, e, [], 1); out["gsc_tot_prior"] = S.query(ps, pe, [], 1)
    out["gsc_queries"] = S.query(s, e, ["query"], 100)
    out["gsc_pages"] = S.query(s, e, ["page"], 100)
    out["gsc_device"] = S.query(s, e, ["device"], 5)
    out["gsc_queries_prior"] = S.query(ps, pe, ["query"], 100)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)
    print("wrote", a.out)
    return 0

if __name__ == "__main__":
    sys.exit(main())
