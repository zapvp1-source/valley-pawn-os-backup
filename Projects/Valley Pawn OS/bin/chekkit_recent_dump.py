#!/usr/bin/env python3
"""chekkit_recent_dump.py [--days 14] — READ-ONLY (2026-10-21). Writes fleet/state/chekkit_recent.json: per store,
every Chekkit conversation active in the window with customer name/phone, the message channels seen, and the last
customer / last staff message times. The brand+store Facebook inbox sweep reads it so it never answers a customer
the store already answered in Chekkit."""
import sys, os, json, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_api as ck
days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 14
UTC = dt.timezone.utc
since = dt.datetime.now(UTC) - dt.timedelta(days=days)
out = {"generated_at": dt.datetime.now(UTC).isoformat(), "days": days, "stores": {}}
chan = collections.Counter()
for code in ("CUL", "WAY", "HAR", "LEX", "ROA"):
    rows = []
    try:
        convs, before = [], None
        for _ in range(15):                      # own paging: ck.conversations_since keys by phone and drops non-SMS threads
            b = ck.get(code, "/v1/conversations?limit=50" + ("&before=" + before if before else "")) or {}
            page = b.get("conversations") or []
            stop = False
            for c in page:
                t = ck.ts(c.get("lastMessageAt"))
                if t and t < since:
                    stop = True; continue
                convs.append(c)
            nb = b.get("nextBefore")
            if stop or not page or not nb or nb == before:
                break
            before = nb
        for c in convs:
            ms = ck.messages(code, c["id"])
            lc = ls = None; chs = set()
            for m in ms:
                chs.add(str(m.get("channel"))); chan[str(m.get("channel"))] += 1
                t = m.get("createdAt")
                if m.get("sender") == "customer":
                    lc = max(lc or t, t)
                elif m.get("sender") == "business" and m.get("sentBy") and not ck.is_automated(m):
                    ls = max(ls or t, t)
            cu = c.get("customer") or {}
            rows.append({"name": cu.get("name"), "phone": cu.get("phone"), "channels": sorted(chs),
                         "last_customer_at": lc, "last_staff_at": ls, "assignee": c.get("assignee")})
        out["stores"][code] = rows
    except Exception as e:
        out["stores"][code] = {"error": str(e)}
out["channel_counts"] = dict(chan)
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fleet", "state", "chekkit_recent.json")
json.dump(out, open(p, "w"), indent=1, default=str)
print("channels:", dict(chan)); print({k: (len(v) if isinstance(v, list) else v) for k, v in out["stores"].items()})
