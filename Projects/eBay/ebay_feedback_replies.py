#!/usr/bin/env python3
"""Valley Pawn — eBay feedback reply engine (all 5 stores).

Pulls negative/neutral feedback received as seller that has NO seller reply, writes them to
a JSON worklist, and (only with --post) publishes prepared replies via RespondToFeedback.

Default run is READ-ONLY: it writes ~/ebay_feedback_open.json and prints a summary.

  python3 ebay_feedback_replies.py                 # pull open items -> JSON (read-only)
  python3 ebay_feedback_replies.py --post FILE     # publish replies from a prepared JSON

The --post file is a list of {"store","feedback_id","item_id","text"} objects. eBay feedback
replies are PERMANENT and cannot be edited or removed, so replies are never generated and
posted in the same pass — a human approves the text in between.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
from ebay_store_tokens import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # noqa: E402

NS = "urn:ebay:apis:eBLBaseComponents"
URL = "https://api.ebay.com/ws/api.dll"
RANKINGS = os.path.expanduser("~/ebay_weekly_rankings.py")
OUT = os.path.expanduser("~/ebay_feedback_open.json")
# eBay's GetFeedback response does NOT reliably return the seller's own reply, so "has a reply"
# cannot be read back from the API. This file is the record of what has been answered: ids land
# here both when we post successfully and when eBay tells us a reply already exists.
ANSWERED = os.path.expanduser("~/ebay_feedback_answered.json")


def answered_ids():
    if os.path.exists(ANSWERED):
        return set(json.load(open(ANSWERED)))
    return set()


def mark_answered(ids):
    cur = answered_ids() | set(ids)
    json.dump(sorted(cur), open(ANSWERED, "w"), indent=2)


def stores():
    ns = {}
    exec(compile(open(RANKINGS).read(), RANKINGS, "exec"), ns)
    return ns["STORES"]


def call(token, name, inner):
    body = (f'<?xml version="1.0" encoding="utf-8"?><{name}Request xmlns="{NS}">'
            f'<RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>'
            f'{inner}</{name}Request>').encode()
    h = {"X-EBAY-API-SITEID": "0", "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
         "X-EBAY-API-CALL-NAME": name, "X-EBAY-API-APP-NAME": APP, "X-EBAY-API-DEV-NAME": DEV,
         "X-EBAY-API-CERT-NAME": CERT, "X-EBAY-API-IAF-TOKEN": token, "Content-Type": "text/xml"}
    return ET.fromstring(urlopen(Request(URL, data=body, headers=h), timeout=60).read().decode())


def open_items(token, store, pages=3):
    found = []
    known = answered_ids()
    for page in range(1, pages + 1):
        r = call(token, "GetFeedback",
                 "<DetailLevel>ReturnAll</DetailLevel>"
                 "<FeedbackType>FeedbackReceivedAsSeller</FeedbackType>"
                 f"<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination>")
        rows = r.findall(f".//{{{NS}}}FeedbackDetail")
        if not rows:
            break
        for d in rows:
            if d.findtext(f"{{{NS}}}CommentType") not in ("Negative", "Neutral"):
                continue
            # A reply may surface as Responses/*, FollowUp, or an empty-ish Responses node with
            # a Response child — treat ANY populated Responses subtree as already answered.
            resp = d.find(f"{{{NS}}}Responses")
            replied = (d.findtext(f"{{{NS}}}FollowUp")
                       or (resp is not None and len(list(resp)) > 0))
            if replied or d.findtext(f"{{{NS}}}FeedbackID") in known:
                continue
            found.append({
                "store": store,
                "feedback_id": d.findtext(f"{{{NS}}}FeedbackID"),
                "item_id": d.findtext(f"{{{NS}}}ItemID"),
                "item_title": d.findtext(f"{{{NS}}}ItemTitle"),
                "date": d.findtext(f"{{{NS}}}CommentTime"),
                "type": d.findtext(f"{{{NS}}}CommentType"),
                "buyer": d.findtext(f"{{{NS}}}CommentingUser"),
                "text": d.findtext(f"{{{NS}}}CommentText"),
            })
    return found


def post_reply(token, feedback_id, item_id, text, buyer):
    # TargetUserID (the buyer who left the feedback) is REQUIRED by RespondToFeedback.
    inner = (f"<FeedbackID>{feedback_id}</FeedbackID><ItemID>{item_id}</ItemID>"
             f"<TargetUserID>{buyer}</TargetUserID>"
             f"<ResponseType>Reply</ResponseType>"
             f"<ResponseText>{text}</ResponseText>")
    r = call(token, "RespondToFeedback", inner)
    ack = r.findtext(f"{{{NS}}}Ack", "")
    if ack in ("Success", "Warning"):
        return True, None
    return False, (r.findtext(f".//{{{NS}}}LongMessage") or r.findtext(f".//{{{NS}}}ShortMessage") or "error")


def main():
    st = {s["name"]: s["token"] for s in stores()}
    if "--post" in sys.argv:
        prepared = json.load(open(sys.argv[sys.argv.index("--post") + 1]))
        # buyer id is required; fall back to the last read-only pull if not in the prepared file
        lookup = {}
        if os.path.exists(OUT):
            lookup = {i["feedback_id"]: i["buyer"] for i in json.load(open(OUT))}
        ok = bad = 0
        for p in prepared:
            buyer = p.get("buyer") or lookup.get(p["feedback_id"])
            if not buyer:
                print(f"SKIPPED {p['store']} {p['feedback_id']} :: no buyer id")
                bad += 1
                continue
            good, err = post_reply(st[p["store"]], p["feedback_id"], p["item_id"], p["text"], buyer)
            already = (not good) and "already submitted" in (err or "")
            if good or already:
                mark_answered([p["feedback_id"]])
            label = "POSTED " if good else ("ALREADY ANSWERED " if already else "FAILED ")
            print(label + f"{p['store']} {p['feedback_id']}" + ("" if (good or already) else f" :: {err}"))
            ok, bad = ok + int(good), bad + int(not good)
        print(f"replies posted {ok}, failed {bad}")
        return

    allitems = []
    for name, tok in st.items():
        try:
            found = open_items(tok, name)
        except Exception as e:
            print(f"{name}: ERROR {repr(e)[:120]}")
            continue
        allitems += found
        print(f"{name}: {len(found)} unanswered")
    json.dump(allitems, open(OUT, "w"), indent=2)
    print("wrote", OUT, "-", len(allitems), "items")


if __name__ == "__main__":
    main()
