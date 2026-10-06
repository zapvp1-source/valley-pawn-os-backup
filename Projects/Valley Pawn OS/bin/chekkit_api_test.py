#!/usr/bin/env python3
"""chekkit_api_test.py — READ-ONLY smoke test of the Chekkit API for every store (GET only; never POSTs).
Per store: leaderboard last 7 / last 30 days, GET /v1/conversations (first page: count + keys of ONE item),
and GET /v1/conversations/{id}/messages for one conversation (status + count only).
Prints no tokens, no customer names, phones or message bodies."""
import datetime as dt, json, subprocess, time, urllib.error, urllib.request

BASE = "https://api.chekkit.io"
STORES = ("CUL", "WAY", "HAR", "LEX", "ROA")


def token(code):
    return subprocess.run(["security", "find-generic-password", "-s", "vp-chekkit-token-" + code, "-w"],
                          capture_output=True, text=True).stdout.strip()


def get(tok, path):
    req = urllib.request.Request(BASE + path, method="GET",
                                 headers={"Authorization": "Bearer " + tok, "User-Agent": "ValleyPawnOps/1.0",
                                          "Accept": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=30)
        return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, {"_err": e.read().decode(errors="replace")[:150]}
    except Exception as e:
        return "ERR", {"_err": str(e)[:150]}


def items(body):
    """Find the list of records in a response, whatever the envelope is called."""
    if isinstance(body, list):
        return body, "<list>"
    if isinstance(body, dict):
        for k in ("data", "conversations", "messages", "items", "results", "records"):
            if isinstance(body.get(k), list):
                return body[k], k
        for k, v in body.items():
            if isinstance(v, list):
                return v, k
    return None, None


today = dt.date.today()
print("chekkit_api_test", today.isoformat())
for code in STORES:
    tok = token(code)
    if not tok:
        print(code, "| NO TOKEN"); continue
    out = [code]
    for days in (7, 30):
        s, b = get(tok, "/v1/leaderboard?from=%s&to=%s" % (today - dt.timedelta(days=days), today))
        loc = b.get("location", {}) if isinstance(b, dict) else {}
        rv = loc.get("reviews", {}) or {}
        out.append("lb%d http %s inv=%s rev=%s g=%s fb=%s avg=%s emp=%s" % (
            days, s, loc.get("invitationsSent"), rv.get("total"), rv.get("google"), rv.get("facebook"),
            rv.get("averageRating"), len(b.get("employees", []) or []) if isinstance(b, dict) else "-"))
        if days == 30 and isinstance(b, dict):
            out.append("lb_keys=%s rev_keys=%s emp_keys=%s" % (sorted(b.keys()), sorted(rv.keys()),
                       sorted((b.get("employees") or [{}])[0].keys()) if b.get("employees") else []))
    s, b = get(tok, "/v1/conversations")
    lst, env = items(b)
    top = sorted(b.keys()) if isinstance(b, dict) else "list"
    out.append("conv http %s count=%s env=%s top_keys=%s item_keys=%s" % (
        s, len(lst) if lst is not None else "-", env, top, sorted(lst[0].keys()) if lst else "-"))
    if isinstance(b, dict) and s == 200:
        meta = {k: v for k, v in b.items() if not isinstance(v, (list, dict))}
        out.append("conv_meta=%s" % json.dumps(meta)[:200])
    if s != 200:
        out.append("conv_err=%s" % b.get("_err", "")[:120])
    if lst:
        cid = lst[0].get("id") or lst[0].get("conversationId") or lst[0].get("_id")
        s2, b2 = get(tok, "/v1/conversations/%s/messages" % cid)
        l2, env2 = items(b2)
        out.append("msgs http %s count=%s env=%s item_keys=%s" % (s2, len(l2) if l2 is not None else "-", env2,
                   sorted(l2[0].keys()) if l2 else "-"))
    print(" | ".join(out))
    time.sleep(1)
print("done")
