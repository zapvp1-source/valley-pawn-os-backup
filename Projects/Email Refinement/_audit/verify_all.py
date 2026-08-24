#!/usr/bin/env python3
"""Verify every staged weekly draft against output, not run records (Rule 12)."""
import json, urllib.request, os, time, re

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"
IDS = [28, 29] + list(range(54, 71))


def req(path, tries=6):
    for a in range(tries):
        r = urllib.request.Request(BASE + path, headers={"api-key": KEY,
                                                         "Accept": "application/json"})
        try:
            with urllib.request.urlopen(r) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(4 + a * 4); continue
            return e.code, e.read().decode()
    return 429, "rate limited"


print(f"{'id':>3}  {'name':44} {'send date':13} {'lists':12} {'sender':26} "
      f"{'c/t':>5} {'cta':>4} {'deal':>5} {'mkr':>4} {'stale':>6}")
print("-" * 145)
issues = []
for cid in IDS:
    st, d = req(f"/emailCampaigns/{cid}")
    if st != 200:
        issues.append(f"{cid}: fetch {st}"); continue
    h = d.get("htmlContent") or ""
    name = d["name"]
    date_m = re.search(r"([A-Z][a-z]+ \d{1,2}, 2026)", name)
    lists = d["recipients"].get("lists")
    sender = d["sender"]["email"]
    ct = h.count("/c/") + h.count("/t/")
    cta = h.count("utm_content=primary_cta")
    deal = "DEAL OF THE WEEK — POPULATED MONDAY" in h
    mkr = len(re.findall(r"\[\[[A-Z_]+\]\]", h))
    stale = "touring our Lexington" in h
    utms = set(re.findall(r"utm_campaign=([a-z0-9_\-]+)", h))

    print(f"{cid:>3}  {name[:44]:44} {(date_m.group(1) if date_m else '??'):13} "
          f"{str(lists):12} {sender:26} {ct:>5} {cta:>4} {str(deal):>5} {mkr:>4} {str(stale):>6}")

    if d["status"] != "draft":       issues.append(f"{cid}: status={d['status']}")
    if not date_m:                   issues.append(f"{cid}: name has no 'Month DD, 2026' — picker cannot find it")
    if sender != "hello@thevalleypawn.com": issues.append(f"{cid}: wrong sender {sender}")
    if d.get("replyTo") != "jdavis@fcfpawn.com": issues.append(f"{cid}: replyTo={d.get('replyTo')}")
    if ct != 20:                     issues.append(f"{cid}: {ct} call/text links (expected 20)")
    if cta != 6:                     issues.append(f"{cid}: {cta} primary_cta links (expected 6)")
    if not deal:                     issues.append(f"{cid}: deal placeholder missing")
    if mkr:                          issues.append(f"{cid}: {mkr} unfilled [[MARKER]]s")
    if stale:                        issues.append(f"{cid}: stale Lexington touring line")
    if len(utms) != 1:               issues.append(f"{cid}: mixed utm_campaign {utms}")
    if not lists or 10 not in lists: issues.append(f"{cid}: internal seed list 10 missing")
    time.sleep(0.4)

print("\nISSUES:" if issues else "\nNo issues found.")
for i in issues:
    print("  !!", i)
