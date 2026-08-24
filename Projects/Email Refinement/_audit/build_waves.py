#!/usr/bin/env python3
"""Two fixes, both additive, neither deletes a contact.

1. PURGE BLACKLISTED FROM LIST 7. 22 of the 194 "engaged" contacts are
   blacklisted (unsubscribed or hard-bounced). They cannot receive mail but they
   inflate the audience count and every rate computed from it.

2. BUILD ROTATING WAVE LISTS. Today the weekly email reaches 194 people while
   13,032 contacts get one blast a month. Splitting the dormant population into
   5 waves and adding one wave per weekly send means every dormant contact hears
   from us every 5 weeks at roughly the same monthly volume as now -- but spread
   into smaller, cleaner sends instead of one 11k spike, and the good content
   (Deal of the Week, spotlights, layaway) reaches ~2,400 instead of 194.

Assignment is by a stable hash of the email, so a contact lands in the same wave
on every re-run and re-running never reshuffles the population.
"""
import json, urllib.request, os, time, hashlib, sys

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"
DRY = "--apply" not in sys.argv
MASTER_LIST = 3
ENGAGED_LIST = 7
FOLDER = 1
WAVES = ["A", "B", "C", "D", "E"]


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
                time.sleep(4 + a * 4)
                continue
            return e.code, e.read().decode()
    return 429, "rate limited"


def page_list(list_id):
    """Every contact on a list, following pagination."""
    out, offset = [], 0
    while True:
        st, d = req("GET", f"/contacts/lists/{list_id}/contacts?limit=500&offset={offset}")
        if st != 200:
            print(f"  page fail list={list_id} offset={offset} status={st}")
            break
        batch = d.get("contacts", [])
        out.extend(batch)
        if len(batch) < 500:
            break
        offset += 500
        time.sleep(0.4)
    return out


print("reading list 7 (engaged) ...")
engaged = page_list(ENGAGED_LIST)
eng_emails = {c["email"].lower() for c in engaged}
bad = [c["email"] for c in engaged if c.get("emailBlacklisted")]
print(f"  list 7: {len(engaged)} contacts, {len(bad)} blacklisted")

print("reading list 3 (master) ...")
master = page_list(MASTER_LIST)
print(f"  list 3: {len(master)} contacts")

dormant = [c["email"] for c in master
           if not c.get("emailBlacklisted") and c["email"].lower() not in eng_emails]
print(f"  mailable dormant (not blacklisted, not engaged): {len(dormant)}")

buckets = {w: [] for w in WAVES}
for e in dormant:
    h = int(hashlib.sha256(e.lower().encode()).hexdigest()[:8], 16)
    buckets[WAVES[h % 5]].append(e)
for w in WAVES:
    print(f"  wave {w}: {len(buckets[w])}")

if DRY:
    print("\nDRY RUN — pass --apply to write. Nothing changed.")
    sys.exit(0)

# ---- 1. purge blacklisted from list 7 -------------------------------------
if bad:
    st, r = req("POST", f"/contacts/lists/{ENGAGED_LIST}/contacts/remove",
                {"emails": bad})
    print(f"\npurge blacklisted from list 7: status={st} removed={len(bad)}")

# ---- 2. create + fill wave lists ------------------------------------------
st, existing = req("GET", "/contacts/lists?limit=50")
by_name = {l["name"]: l["id"] for l in existing.get("lists", [])}

for w in WAVES:
    name = f"Wave {w} — rotating dormant (1 of 5 per weekly send)"
    if name in by_name:
        lid = by_name[name]
        print(f"\nwave {w}: reusing list {lid}")
    else:
        st, r = req("POST", "/contacts/lists", {"name": name, "folderId": FOLDER})
        lid = r.get("id")
        print(f"\nwave {w}: created list {lid} (status {st})")
    if not lid:
        print(f"  !! could not resolve list id for wave {w}; skipping")
        continue
    emails = buckets[w]
    for i in range(0, len(emails), 150):
        chunk = emails[i:i + 150]
        st, r = req("POST", f"/contacts/lists/{lid}/contacts/add", {"emails": chunk})
        if st >= 300:
            print(f"  add {i}-{i+len(chunk)} FAILED {st} {str(r)[:160]}")
        time.sleep(0.35)
    st, chk = req("GET", f"/contacts/lists/{lid}")
    print(f"  wave {w} final uniqueSubscribers = {chk.get('uniqueSubscribers')}")

print("\nDONE")
