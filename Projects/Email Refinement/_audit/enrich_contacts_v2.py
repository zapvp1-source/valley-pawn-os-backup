#!/usr/bin/env python3
"""v2 of the Bravo -> Brevo attribute enrichment sync (weekly scheduled run).

Builds on _audit/enrich_contacts.py (the proven 2026-08-24 implementation) with
one added safeguard discovered on this run (2026-08-25): a small number of
Chekkit archive rows share a handful of generic/shared phone numbers
(e.g. +18665403229, +19173877468, +17028052170 each appear against dozens of
unrelated emails) and garbage "first_name" values that are really email
usernames/handles (e.g. "Wigs2002", "Debtheconqueror"). Writing those into
Brevo would corrupt SMS (multiple unrelated customers can't share one phone)
and produce embarrassing "Hi Wigs2002," personalization. This version adds a
data-quality filter before writing:

  - SMS: skip any phone number that appears against >=4 distinct emails in
    the archive (a real personal cell doesn't fan out across dozens of
    unrelated customers - this is almost certainly a shared/default number
    from an upstream form).
  - FIRSTNAME/LASTNAME: skip if the name contains a digit, or if the
    alpha-only lowercase version of the name is a substring of the email's
    local-part (i.e. it's plainly the username, not a real name).

Everything else (enrichment-only, never overwrite non-empty data, PUT
/contacts/{email} not /contacts/import, E.164 phone format, 0.12s pacing +
backoff) is unchanged from v1.
"""
import json, urllib.request, urllib.parse, os, glob, csv, re, time, sys
from collections import defaultdict, Counter

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"
DRY = "--apply" not in sys.argv
OUT = os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction/output")
STORE_MAP = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington",
             "ROA": "Roanoke", "WAY": "Waynesboro"}


def req(method, path, body=None, tries=7):
    data = json.dumps(body).encode() if body is not None else None
    for a in range(tries):
        r = urllib.request.Request(BASE + path, data=data, method=method,
                                    headers={"api-key": KEY,
                                             "Content-Type": "application/json",
                                             "Accept": "application/json"})
        try:
            with urllib.request.urlopen(r) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw else {})
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(4 + a * 4); continue
            return e.code, e.read().decode()
    return 429, "rate limited"


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


def name_is_suspicious(name, email):
    if not name:
        return False
    if re.search(r"\d", name):
        return True
    localpart = email.split("@")[0].lower()
    namecheck = re.sub(r"[^a-z]", "", name.lower())
    return bool(namecheck) and namecheck in localpart


# ---------------------------------------------------- 1. parse the archive
records = {}
rows_total = rows_with_email = 0
per_store = defaultdict(int)
phone_email_map = defaultdict(set)   # phone -> set of emails (to find shared/generic numbers)

files = sorted(glob.glob(os.path.join(OUT, "*_chekkit-invites-range.csv")))
print(f"parsing {len(files)} files ...")

for path in files:
    base = os.path.basename(path)
    m = re.match(r"(\d{4}-\d{2}-\d{2})_([A-Z]{3})_", base)
    if not m:
        continue
    file_date, code = m.group(1), m.group(2)
    store = STORE_MAP.get(code)
    if not store:
        continue
    try:
        with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
            for row in csv.DictReader(f):
                rows_total += 1
                email = (row.get("email") or "").strip().lower()
                if not email or "@" not in email:
                    continue
                rows_with_email += 1
                full = (row.get("first_name") or "").strip()
                last = (row.get("last_name") or "").strip()
                if full and not last:
                    parts = full.split()
                    first, last = parts[0], " ".join(parts[1:])
                else:
                    first = full
                phone = clean_phone(row.get("phone"))
                if phone:
                    phone_email_map[phone].add(email)
                prev = records.get(email)
                if prev and prev["date"] >= file_date:
                    continue
                records[email] = {
                    "date": file_date, "store": store,
                    "first": titlecase(first), "last": titlecase(last),
                    "phone": phone,
                }
    except Exception as e:
        print(f"  !! {base}: {e}")

for r in records.values():
    per_store[r["store"]] += 1

shared_numbers = {p for p, es in phone_email_map.items() if len(es) >= 4}
print(f"  rows scanned      : {rows_total}")
print(f"  rows with email   : {rows_with_email}")
print(f"  unique emails     : {len(records)}")
print(f"  with first name   : {sum(1 for r in records.values() if r['first'])}")
print(f"  with phone        : {sum(1 for r in records.values() if r['phone'])}")
print(f"  shared/generic phone numbers detected (>=4 distinct emails): {len(shared_numbers)}")
for p in sorted(shared_numbers, key=lambda x: -len(phone_email_map[x]))[:10]:
    print(f"    {p} -> {len(phone_email_map[p])} distinct emails (SKIPPING as SMS source)")
print(f"  by store          : {dict(per_store)}")

# ---------------------------------------------- 2. who already exists in Brevo
print("\nreading existing Brevo contacts ...")
existing = {}
offset = 0
while True:
    st, d = req("GET", f"/contacts?limit=500&offset={offset}")
    if st != 200:
        print(f"  page fail offset={offset} status={st}"); break
    batch = d.get("contacts", [])
    for c in batch:
        em = c.get("email")
        if not em:
            continue
        existing[em.lower()] = c.get("attributes", {}) or {}
    if len(batch) < 500:
        break
    offset += 500
    time.sleep(0.3)
print(f"  brevo contacts    : {len(existing)}")

# --------------------------------------------------------- 3. build payload
updates = []
skipped_absent = 0
skipped_bad_name = 0
skipped_shared_phone = 0
for email, r in records.items():
    attrs_now = existing.get(email)
    if attrs_now is None:
        skipped_absent += 1
        continue
    attrs = {}
    if r["first"] and not (attrs_now.get("FIRSTNAME") or "").strip():
        if name_is_suspicious(r["first"], email):
            skipped_bad_name += 1
        else:
            attrs["FIRSTNAME"] = r["first"]
    if r["last"] and not (attrs_now.get("LASTNAME") or "").strip():
        if name_is_suspicious(r["last"], email):
            skipped_bad_name += 1
        else:
            attrs["LASTNAME"] = r["last"]
    if r["store"] and not (attrs_now.get("STORE") or "").strip():
        attrs["STORE"] = r["store"]
    if r["phone"] and not str(attrs_now.get("SMS") or "").strip():
        if r["phone"] in shared_numbers:
            skipped_shared_phone += 1
        else:
            attrs["SMS"] = r["phone"]
    if attrs:
        updates.append({"email": email, "attributes": attrs})

print(f"\n  in archive but not in Brevo (skipped)      : {skipped_absent}")
print(f"  skipped - name looked like a username/handle: {skipped_bad_name}")
print(f"  skipped - phone was a shared/generic number  : {skipped_shared_phone}")
print(f"  contacts with at least one gap to fill        : {len(updates)}")
fld = Counter()
for u in updates:
    for k in u["attributes"]:
        fld[k] += 1
print(f"  field fills queued                            : {dict(fld)}")

if DRY:
    print("\nDRY RUN - pass --apply to write. Sample of 10:")
    for u in updates[:10]:
        print("   ", u)
    sys.exit(0)

# ------------------------------------------------------------- 4. push it
print(f"\nupdating {len(updates)} contacts (attributes only, no list changes) ...")
ok = fail = 0
failures = []
t0 = time.time()
for n, u in enumerate(updates, 1):
    ident = urllib.parse.quote(u["email"], safe="")
    st, res = req("PUT", f"/contacts/{ident}", {"attributes": u["attributes"]})
    resl = str(res).lower()
    if st not in (200, 204) and "SMS" in u["attributes"] and (
        "phone" in resl or "sms" in resl or "duplicate_parameter" in resl
    ):
        # bad number, or this number is already attached to a different Brevo
        # contact (e.g. a shared household phone) - drop SMS, keep name fields
        attrs = {k: v for k, v in u["attributes"].items() if k != "SMS"}
        if attrs:
            st, res = req("PUT", f"/contacts/{ident}", {"attributes": attrs})
    if st in (200, 204):
        ok += 1
    else:
        fail += 1
        if len(failures) < 25:
            failures.append((u["email"], st, str(res)[:120]))
    if n % 250 == 0:
        el = time.time() - t0
        print(f"  {n}/{len(updates)}  ok={ok} fail={fail}  "
              f"{el:.0f}s elapsed, ~{el/n*(len(updates)-n):.0f}s left", flush=True)
    time.sleep(0.12)

print(f"\nDONE  updated={ok}  failed={fail}")
for f in failures:
    print("  !!", f)
