#!/usr/bin/env python3
"""chekkit_schema_probe.py — READ-ONLY. Shows how the Chekkit API labels conversations/messages
(customer fields, sender/sentBy values) for today's HAR conversations. Phones last-4 only, text
truncated to 40 chars. GET only; never POSTs. Built 2026-10-05 for the missed-call 'handled by text' rule."""
import datetime as dt, json, subprocess, sys, time, urllib.request, urllib.error
BASE = "https://api.chekkit.io"
code = sys.argv[1] if len(sys.argv) > 1 else "HAR"
tok = subprocess.run(["security", "find-generic-password", "-s", "vp-chekkit-token-" + code, "-w"],
                     capture_output=True, text=True).stdout.strip()
def get(path):
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + tok, "Accept": "application/json",
                                                       "User-Agent": "ValleyPawnOps/1.0"})
    try:
        r = urllib.request.urlopen(req, timeout=30); return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, {"_err": e.read().decode(errors="replace")[:200]}
def red(v):
    if isinstance(v, str):
        d = "".join(c for c in v if c.isdigit())
        if len(d) >= 10: return "...%s" % d[-4:]
        if "@" in v: return "<email>"
    return v
def scrub(o):
    if isinstance(o, dict): return {k: (scrub(v) if k not in ("text", "name", "firstName", "lastName") else ("<%s>" % k)) for k, v in o.items()}
    if isinstance(o, list): return [scrub(x) for x in o[:3]]
    return red(o)
s, b = get("/v1/conversations")
convs = b.get("conversations", [])
print("conversations http", s, "count", len(convs), "nextBefore", b.get("nextBefore"))
if convs: print("SAMPLE CONVERSATION (scrubbed):", json.dumps(scrub(convs[0]))[:900])
today = dt.datetime.now(dt.timezone.utc).date().isoformat()
senders = {}
for c in convs[:12]:
    cid = c.get("id"); cust = c.get("customer") or {}
    ph = cust.get("phone") or cust.get("phoneNumber") or cust.get("mobile") or ""
    s2, b2 = get("/v1/conversations/%s/messages" % cid)
    msgs = b2.get("messages", []) if isinstance(b2, dict) else []
    print("\nCONV ...%s open=%s last=%s msgs=%d http=%s keys2=%s" % (str(ph)[-4:], c.get("open"), c.get("lastMessageAt"), len(msgs), s2,
          sorted(b2.keys()) if isinstance(b2, dict) else "-"))
    for m in msgs[-8:]:
        snd = m.get("sender"); sb = m.get("sentBy")
        key = json.dumps([scrub(snd), scrub(sb)], sort_keys=True)[:160]
        senders[key] = senders.get(key, 0) + 1
        print("  %s | ch=%s | status=%s | sender=%s | sentBy=%s | text=%r" % (m.get("createdAt"), m.get("channel"), m.get("status"),
              json.dumps(scrub(snd))[:120], json.dumps(scrub(sb))[:120], (m.get("text") or "")[:40]))
    time.sleep(1.1)
print("\nDISTINCT sender/sentBy shapes:")
for k, v in senders.items(): print(v, k)
