#!/usr/bin/env python3
"""The personalised YOUR-STORE block in W13 carries a hardcoded sentence
'This week we're touring our Lexington location - everything below works at your
<CITY> store too.' It was cloned into all 17 new drafts, where it is wrong for
every send that is not the Lexington spotlight.

Rewrite it per campaign: spotlight sends name the correct featured store,
non-spotlight sends get a neutral line.
"""
import json, urllib.request, os, re, time

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"


def req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"api-key": KEY, "Content-Type": "application/json",
                                        "Accept": "application/json"})
    try:
        with urllib.request.urlopen(r) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


# campaign id -> featured store, or None for a non-spotlight send
SPOTLIGHT = {
    54: "Roanoke", 57: "Culpeper", 60: "Waynesboro", 62: "Harrisonburg", 66: "Lexington",
    55: None, 56: None, 58: None, 59: None, 61: None, 63: None,
    64: None, 65: None, 67: None, 68: None, 69: None, 70: None,
}

PAT = re.compile(
    r"This week we&rsquo;re touring our \w+ location &mdash; everything below works at your "
    r"(\w+) store too\.|"
    r"This week we&rsquo;re touring our \w+ location — everything below works at your "
    r"(\w+) store too\."
)

for cid, feat in SPOTLIGHT.items():
    for attempt in range(6):                     # Brevo rate-limits hard; back off
        st, c = req("GET", f"/emailCampaigns/{cid}")
        if st == 200:
            break
        time.sleep(3 + attempt * 3)
    if st != 200:
        print(cid, "FETCH FAIL", st); continue
    h = c["htmlContent"]

    def repl(m):
        branch = m.group(1) or m.group(2)
        if feat and feat != branch:
            return (f"This week we&rsquo;re featuring our {feat} store &mdash; "
                    f"everything below works at your {branch} store too.")
        if feat and feat == branch:
            return "That&rsquo;s the store we&rsquo;re featuring this week."
        return f"Everything below applies at your {branch} store."

    new, n = PAT.subn(repl, h)
    if n == 0:
        print(f"{cid}: no occurrences "
              f"(has 'touring'={'touring' in h}, html len={len(h)})")
        continue
    time.sleep(1)
    st2, res = req("PUT", f"/emailCampaigns/{cid}", {"htmlContent": new})
    time.sleep(1)
    st3, chk = req("GET", f"/emailCampaigns/{cid}")
    stale = "touring our Lexington location" in (chk.get("htmlContent") or "")
    print(f"{cid:>3} {c['name'][:44]:46} rewrote {n}  PUT {st2}  stale-left={stale}")
    time.sleep(1)
