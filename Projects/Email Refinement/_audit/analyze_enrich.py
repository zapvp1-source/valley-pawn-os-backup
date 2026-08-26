#!/usr/bin/env python3
"""One-off quality check before applying enrich_contacts.py: flag FIRSTNAME
fills that look like usernames/handles rather than real names (contains a
digit, or the alpha-only version of the name is a substring of the email's
local-part) so we don't push junk personalization into customer emails."""
import json, urllib.request, os, glob, csv, re, time

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"
OUT = os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction/output")
STORE_MAP = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington",
             "ROA": "Roanoke", "WAY": "Waynesboro"}


def req(path):
    r = urllib.request.Request(BASE + path, headers={"api-key": KEY, "Accept": "application/json"})
    with urllib.request.urlopen(r) as resp:
        return resp.status, json.loads(resp.read())


def clean_phone(p):
    d = re.sub(r"\D", "", p or "")
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    if len(d) != 10 or d[0] in "01":
        return ""
    return "+1" + d


def titlecase(n):
    out = []
    for w in (n or "").split():
        if "'" in w:
            out.append("'".join(p.capitalize() for p in w.split("'")))
        elif w.startswith("MC") and len(w) > 3:
            out.append("Mc" + w[2:].capitalize())
        else:
            out.append(w.capitalize())
    return " ".join(out)


records = {}
files = sorted(glob.glob(os.path.join(OUT, "*_chekkit-invites-range.csv")))
for path in files:
    base = os.path.basename(path)
    m = re.match(r"(\d{4}-\d{2}-\d{2})_([A-Z]{3})_", base)
    if not m:
        continue
    file_date, code = m.group(1), m.group(2)
    store = STORE_MAP.get(code)
    if not store:
        continue
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
        for row in csv.DictReader(f):
            email = (row.get("email") or "").strip().lower()
            if not email or "@" not in email:
                continue
            full = (row.get("first_name") or "").strip()
            last = (row.get("last_name") or "").strip()
            if full and not last:
                parts = full.split()
                first, last = parts[0], " ".join(parts[1:])
            else:
                first = full
            prev = records.get(email)
            if prev and prev["date"] >= file_date:
                continue
            records[email] = {"date": file_date, "store": store,
                               "first": titlecase(first), "last": titlecase(last),
                               "phone": clean_phone(row.get("phone"))}

existing = {}
offset = 0
while True:
    st, d = req(f"/contacts?limit=500&offset={offset}")
    if st != 200:
        break
    batch = d.get("contacts", [])
    for c in batch:
        em = c.get("email")
        if em:
            existing[em.lower()] = c.get("attributes", {}) or {}
    if len(batch) < 500:
        break
    offset += 500
    time.sleep(0.3)

suspicious = []
clean = []
for email, r in records.items():
    attrs_now = existing.get(email)
    if attrs_now is None:
        continue
    if r["first"] and not (attrs_now.get("FIRSTNAME") or "").strip():
        localpart = email.split("@")[0].lower()
        namecheck = re.sub(r"[^a-z]", "", r["first"].lower())
        is_suspicious = bool(re.search(r"\d", r["first"])) or (namecheck and namecheck in localpart)
        entry = (email, r["first"], r["last"], r["phone"])
        (suspicious if is_suspicious else clean).append(entry)

print(f"total FIRSTNAME fills queued: {len(suspicious) + len(clean)}")
print(f"suspicious (digit or matches email localpart): {len(suspicious)}")
for e in suspicious[:60]:
    print("  SUSPECT:", e)
print(f"clean-looking: {len(clean)}")
for e in clean[:20]:
    print("  OK:", e)
