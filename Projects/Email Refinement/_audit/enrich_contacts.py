#!/usr/bin/env python3
"""Fill in Brevo contact attributes from the real Bravo customer archive.

THE PROBLEM (2026-08-22 audit): Brevo contact attributes are nearly empty -
FIRSTNAME on ~0.1% of the file, STORE on ~54%, phone/SMS on 0%. That blanks out
the personalised "YOUR VALLEY PAWN STORE" block for half the audience (it is a
{% if contact.STORE %} Liquid block - the logic is fine, the data feeding it is
missing) and makes SMS impossible.

THE DATA: 117 chekkit-invites-range CSVs in the Bravo Data Extraction output
folder, Jan 2025 -> Aug 2026, ~7,130 rows. Columns: first_name, last_name, phone,
email, dnt, last_visit. Store comes from the filename (YYYY-MM-DD_XXX_...).

KNOWN UPSTREAM QUIRK (documented in chekkit-weekly-review-requests SKILL.md):
the handler writes the customer's full display name into `first_name` and leaves
`last_name` blank. So split it here. Names arrive UPPERCASE, which would render
as "Hi ANA ROSELIA MENDEZ" - title-case them.

SAFETY: this is ENRICHMENT ONLY. It updates contacts that already exist in Brevo
and never creates new ones, so it cannot import anyone who has not already been
through the normal consent path. It also never overwrites existing non-empty data
with blanks.
"""
import json, urllib.request, urllib.parse, os, glob, csv, re, time, sys
from collections import defaultdict

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
    """Brevo's SMS attribute demands E.164 with country code - a bare 10-digit
    string is rejected with 'Invalid phone number' (400). Verified 2026-08-24."""
    d = re.sub(r"\D", "", p or "")
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    if len(d) != 10 or d[0] in "01":          # area code can't start 0/1
        return ""
    return "+1" + d


def titlecase(n):
    out = []
    for w in (n or "").split():
        if "'" in w:                      # O'BRIEN -> O'Brien
            out.append("'".join(p.capitalize() for p in w.split("'")))
        elif w.startswith("MC") and len(w) > 3:
            out.append("Mc" + w[2:].capitalize())
        else:
            out.append(w.capitalize())
    return " ".join(out)


# ---------------------------------------------------- 1. parse the archive
records = {}                              # email -> record (newest wins)
rows_total = rows_with_email = 0
per_store = defaultdict(int)

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
                if full and not last:            # upstream quirk: full name in first_name
                    parts = full.split()
                    first, last = parts[0], " ".join(parts[1:])
                else:
                    first = full
                prev = records.get(email)
                if prev and prev["date"] >= file_date:
                    continue                     # keep the newer sighting
                records[email] = {
                    "date": file_date, "store": store,
                    "first": titlecase(first), "last": titlecase(last),
                    "phone": clean_phone(row.get("phone")),
                }
    except Exception as e:
        print(f"  !! {base}: {e}")

for r in records.values():
    per_store[r["store"]] += 1

print(f"  rows scanned      : {rows_total}")
print(f"  rows with email   : {rows_with_email}")
print(f"  unique emails     : {len(records)}")
print(f"  with first name   : {sum(1 for r in records.values() if r['first'])}")
print(f"  with phone        : {sum(1 for r in records.values() if r['phone'])}")
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
        em = c.get("email")            # a few records carry no email (SMS-only)
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
for email, r in records.items():
    attrs_now = existing.get(email)
    if attrs_now is None:
        skipped_absent += 1
        continue                              # enrichment only - never create
    attrs = {}
    # only fill genuine gaps; never downgrade existing data to blank
    if r["first"] and not (attrs_now.get("FIRSTNAME") or "").strip():
        attrs["FIRSTNAME"] = r["first"]
    if r["last"] and not (attrs_now.get("LASTNAME") or "").strip():
        attrs["LASTNAME"] = r["last"]
    if r["store"] and not (attrs_now.get("STORE") or "").strip():
        attrs["STORE"] = r["store"]
    if r["phone"] and not str(attrs_now.get("SMS") or "").strip():
        attrs["SMS"] = r["phone"]
    if attrs:
        updates.append({"email": email, "attributes": attrs})

print(f"\n  in archive but not in Brevo (skipped) : {skipped_absent}")
print(f"  contacts with at least one gap to fill: {len(updates)}")
from collections import Counter
fld = Counter()
for u in updates:
    for k in u["attributes"]:
        fld[k] += 1
print(f"  field fills queued                    : {dict(fld)}")

if DRY:
    print("\nDRY RUN - pass --apply to write. Sample of 5:")
    for u in updates[:5]:
        print("   ", u)
    sys.exit(0)

# ------------------------------------------------------------- 4. push it
# NOT /contacts/import - that endpoint requires listIds and would change list
# membership as a side effect. PUT /contacts/{email} updates attributes only,
# which is exactly the intent: enrich, touch nothing else.
print(f"\nupdating {len(updates)} contacts (attributes only, no list changes) ...")
ok = fail = 0
failures = []
t0 = time.time()
for n, u in enumerate(updates, 1):
    ident = urllib.parse.quote(u["email"], safe="")
    st, res = req("PUT", f"/contacts/{ident}", {"attributes": u["attributes"]})
    if st not in (200, 204) and "phone" in str(res).lower():
        # bad number in the source data - keep the name fields, drop the phone
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
