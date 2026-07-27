#!/usr/bin/env python3
"""Waynesboro 6-day hours patch for Brevo — Template 11 + draft campaigns 27,28,29,30,43.
Backs up original HTML to files before PUT. Campaign 26 already sent — skipped."""
import json, re, urllib.request
from pathlib import Path

KEY = (Path.home() / ".config" / "valley-pawn" / "brevo_api_key").read_text().strip()
BASE = "https://api.brevo.com/v3"
BK = Path("/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/brevo_backups_2026-07-23")
BK.mkdir(exist_ok=True)

def call(path, method="GET", body=None):
    req = urllib.request.Request(BASE + path, method=method,
        headers={"accept": "application/json", "api-key": KEY, "content-type": "application/json"},
        data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req, timeout=30) as r:
        d = r.read().decode()
        return json.loads(d) if d.strip() else {}

REP1_OLD = "Waynesboro &middot; Mon, Tue, Thu, Fri & Sat 10am–6pm"
REP1_NEW = "Waynesboro &middot; Mon–Sat 10am–6pm"
REP2_OLD = "Culpeper: Mon&ndash;Sat 10am&ndash;6pm. All other stores:"
REP2_NEW = "Culpeper &amp; Waynesboro: Mon&ndash;Sat 10am&ndash;6pm. All other stores:"

def patch_html(html, label):
    out = html
    for old, new, tag in [(REP1_OLD, REP1_NEW, "storeblock"), (REP2_OLD, REP2_NEW, "footer")]:
        n = out.count(old)
        print(f"  {label} {tag}: {n} occurrence(s)")
        if n >= 1:
            out = out.replace(old, new)
    # report remaining closed-Wed contexts for manual eyeball
    for m in re.finditer(r"[Cc]losed Wed", out):
        s = max(0, m.start() - 110)
        ctx = out[s:m.start() + 30].replace("\n", " ")
        print(f"  {label} REMAINING: ...{ctx!r}")
    return out

# Template 11
t = call("/smtp/templates/11")
html = t["htmlContent"]
(BK / "template_11.html").write_text(html)
new_html = patch_html(html, "T11")
if new_html != html:
    call("/smtp/templates/11", "PUT", {"htmlContent": new_html})
    print("T11: UPDATED")
(BK / "template_11_new.html").write_text(new_html)

for cid in [27, 28, 29, 30, 43]:
    try:
        c = call(f"/emailCampaigns/{cid}")
        st = c.get("status")
        html = c.get("htmlContent", "")
        (BK / f"campaign_{cid}.html").write_text(html)
        print(f"C{cid} '{c.get('name')}' [{st}]")
        if st == "sent":
            print(f"C{cid}: SKIP (sent)")
            continue
        new_html = patch_html(html, f"C{cid}")
        if new_html != html:
            call(f"/emailCampaigns/{cid}", "PUT", {"htmlContent": new_html})
            print(f"C{cid}: UPDATED")
    except Exception as e:
        print(f"C{cid}: ERROR {e}")

print("===== LISTS =====")
try:
    ls = call("/contacts/lists?limit=50")
    for l in ls.get("lists", []):
        print(f"  id={l['id']} name={l['name']!r} subs={l.get('totalSubscribers')}")
except Exception as e:
    print("lists error", e)
print("DONE")
