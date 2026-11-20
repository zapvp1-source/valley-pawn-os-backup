#!/usr/bin/env python3
"""messages_shadow.py [days] — READ-ONLY. Pulls buyer questions (one call name: GetMemberMessages),
runs desk_sync.classify_message, and writes counts + the would-be reply to out/messages_shadow_<tag>.csv.
Sends nothing. Buyer names are not written; question text is truncated and kept only for rule tuning."""
import csv, html, os, sys, time
from datetime import datetime, timedelta, timezone
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import ebay_common as ec
import desk_sync as ds
READ_CALL = "GetMemberMessages"
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 30
NOW = datetime.now(timezone.utc); FROM = NOW - timedelta(days=DAYS)
f = lambda d: d.strftime("%Y-%m-%dT%H:%M:%S.000Z")
N = "{%s}" % ec.NS
rows = []
for store in ec.STORE_ORDER:
    tok = ec.token_for(store)
    for status in ("Answered", "Unanswered"):
        page = 1
        while True:
            r = ec.call(tok, READ_CALL, "<MailMessageType>All</MailMessageType><MessageStatus>%s</MessageStatus>"
                        "<StartCreationTime>%s</StartCreationTime><EndCreationTime>%s</EndCreationTime>"
                        "<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>"
                        % (status, f(FROM), f(NOW), page))
            if not ec.ack_ok(r): raise RuntimeError("%s %s %s" % (READ_CALL, store, ec.errors(r)[:1]))
            for mx in r.iter(N + "MemberMessageExchange"):
                q = mx.find(N + "Question"); it = mx.find(N + "Item")
                body = html.unescape((q.findtext(N + "Body") or "") if q is not None else "")
                subj = (q.findtext(N + "Subject") or "") if q is not None else ""
                title = (it.findtext(N + "Title") or "") if it is not None else ""
                metal = any(k in title.lower() for k in ("gold", "silver", "platinum", "bullion", "14k", "10k", "18k", "sterling"))
                kind, key = ds.classify_message(body, has_order=False, is_precious_metal=metal)
                rows.append([store, status, (mx.findtext(N + "CreationDate") or "")[:10], kind, key, title[:50], " ".join(body.split())[:160]])
            if (r.findtext(N + "HasMoreItems") or "false").lower() != "true": break
            page += 1
tag = time.strftime("%Y-%m-%d_%H%M")
dst = os.path.join(HERE, "out", "messages_shadow_%s.csv" % tag)
with open(dst, "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["store", "status", "date", "decision", "key", "item", "question"]); w.writerows(rows)
from collections import Counter
print("total", len(rows), Counter(r[3] for r in rows)); print(Counter((r[3], r[4]) for r in rows).most_common(20)); print("->", dst)
