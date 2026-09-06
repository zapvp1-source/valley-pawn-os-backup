#!/usr/bin/env python3
"""Valley Pawn — READ-ONLY seller-standards + unanswered-feedback probe for all 5 eBay stores.

Replaces the Chrome-dependent half of monthly-ebay-ratings-sweep: pulls Seller Standards
(level, late shipment, defect rate) and recent negative/neutral feedback WITHOUT a seller
reply, per store, via the Trading API using the existing per-store tokens.

Read-only. Makes no changes to any listing or account.

Usage: python3 ebay_seller_standards_probe.py
"""
import os
import sys
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
from ebay_store_tokens import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # noqa: E402

NS = "urn:ebay:apis:eBLBaseComponents"
URL = "https://api.ebay.com/ws/api.dll"
PATHS = [os.path.expanduser("~/ebay_weekly_rankings.py")]


def stores():
    for p in PATHS:
        if os.path.exists(p):
            ns = {}
            exec(compile(open(p).read(), p, "exec"), ns)
            if "STORES" in ns:
                return ns["STORES"]
    raise SystemExit("no tokens")


def call(token, name, inner):
    body = (f'<?xml version="1.0" encoding="utf-8"?><{name}Request xmlns="{NS}">'
            f'<RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>'
            f'{inner}</{name}Request>').encode()
    h = {"X-EBAY-API-SITEID": "0", "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
         "X-EBAY-API-CALL-NAME": name, "X-EBAY-API-APP-NAME": APP, "X-EBAY-API-DEV-NAME": DEV,
         "X-EBAY-API-CERT-NAME": CERT, "X-EBAY-API-IAF-TOKEN": token, "Content-Type": "text/xml"}
    return ET.fromstring(urlopen(Request(URL, data=body, headers=h), timeout=60).read().decode())


def txt(node, path):
    return node.findtext(path.replace("{}", "{" + NS + "}")) if node is not None else None


def dashboard(token):
    r = call(token, "GetSellerDashboard", "")
    out = {"ack": txt(r, "{}Ack")}
    pd = r.find(f".//{{{NS}}}PerformanceDashboard")
    if pd is not None:
        out["site"] = txt(pd, "{}Site")
        out["status"] = txt(pd, "{}Status")
    out["power_seller"] = txt(r, f".//{{{NS}}}PowerSellerStatus/{{{NS}}}Level")
    out["top_rated"] = txt(r, f".//{{{NS}}}PowerSellerStatus/{{{NS}}}TopRatedProgramLevel")
    alerts = [a.findtext(f"{{{NS}}}Text") or "" for a in r.findall(f".//{{{NS}}}Alert")]
    out["alerts"] = [a for a in alerts if a]
    # keep raw tag names around so we can see what this account actually returns
    out["tags"] = sorted({e.tag.split("}")[-1] for e in r.iter()})[:40]
    return out


def unanswered_feedback(token, pages=2):
    """Negative/neutral feedback received with no seller response."""
    open_items = []
    for page in range(1, pages + 1):
        r = call(token, "GetFeedback",
                 "<DetailLevel>ReturnAll</DetailLevel>"
                 "<FeedbackType>FeedbackReceivedAsSeller</FeedbackType>"
                 f"<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination>")
        rows = r.findall(f".//{{{NS}}}FeedbackDetail")
        if not rows:
            break
        for d in rows:
            ctype = d.findtext(f"{{{NS}}}CommentType")
            if ctype in ("Negative", "Neutral"):
                reply = d.findtext(f"{{{NS}}}Responses/{{{NS}}}RespondingUserID") or \
                    d.findtext(f"{{{NS}}}FollowUp")
                if not reply:
                    open_items.append({
                        "date": d.findtext(f"{{{NS}}}CommentTime"),
                        "type": ctype,
                        "text": (d.findtext(f"{{{NS}}}CommentText") or "")[:90],
                        "item": d.findtext(f"{{{NS}}}ItemID"),
                    })
    return open_items


def main():
    for s in stores():
        name, tok = s["name"], s["token"]
        print(f"===== {name} =====")
        try:
            d = dashboard(tok)
            print("  dashboard:", {k: v for k, v in d.items() if k != "tags"})
            print("  tags:", ", ".join(d["tags"]))
        except Exception as e:
            print("  dashboard ERROR:", repr(e)[:200])
        try:
            open_fb = unanswered_feedback(tok)
            print(f"  unanswered negative/neutral feedback: {len(open_fb)}")
            for f in open_fb[:5]:
                print(f"    {f['date']} {f['type']} item {f['item']}: {f['text']}")
        except Exception as e:
            print("  feedback ERROR:", repr(e)[:200])


if __name__ == "__main__":
    main()
