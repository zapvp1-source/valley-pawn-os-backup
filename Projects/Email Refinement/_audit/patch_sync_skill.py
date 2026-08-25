#!/usr/bin/env python3
"""Fold the proven enrichment method + hard-won API gotchas into the
bravo-brevo-attribute-sync scheduled task, so a future run doesn't rediscover
them the slow way."""
import os

ADDENDUM = """

---

## PROVEN IMPLEMENTATION (established 2026-08-24 — read this before writing any code)

A full enrichment pass was executed manually on 2026-08-24 and it worked. Reuse
`Email Refinement/_audit/enrich_contacts.py` rather than writing a new one. What
that run established:

### The data source that actually exists
Do NOT assume you need a live Bravo pull. There is a large archive already on
disk at `~/Documents/Claude/Projects/Bravo Data Extraction/output/` —
**117 files** matching `*_chekkit-invites-range.csv`, spanning 2025-01-31 through
2026-08-10, ~7,130 rows, ~5,000 unique emails with names and phone numbers.
Filename encodes the store: `YYYY-MM-DD_XXX_chekkit-invites-range.csv` where XXX
is CUL/HAR/LEX/ROA/WAY. Prefer this archive; only trigger a live Bravo pull if you
need data newer than the newest file there, and run the contention check first.

Note the `_shared-bravo-data/` stash is a DIFFERENT and much thinner source — its
newest dated folder was 2026-07-21 and it holds only per-store campaign upload
CSVs. The output-folder archive above is far richer. Check both, prefer the archive.

### Three API gotchas that will silently waste a run

1. **`POST /contacts/import` requires `listIds` or `newList`.** Without it you get
   `400 missing_parameter` on every chunk. But passing `listIds` CHANGES LIST
   MEMBERSHIP as a side effect, which is not what an attribute sync should do.
   **Use `PUT /contacts/{url-encoded-email}` with `{"attributes": {...}}` instead**
   — it updates attributes only and touches nothing else. Slower (~1s/contact
   under rate limiting, ~70 min for 4,900 contacts) but correct.

2. **The `SMS` attribute demands E.164 with country code.** A bare 10-digit
   string is rejected with `400 invalid_parameter / "Invalid phone number"`.
   Send `+1XXXXXXXXXX`. Brevo then stores it back as `1XXXXXXXXXX`. This single
   issue failed 234 of the first 250 updates before it was caught.

3. **Some Brevo contacts have no `email` key at all** (SMS-only records). Guard
   `c.get("email")` when paging `/contacts` or you get a `KeyError` mid-run.

### Rate limiting
Brevo throttles hard. Use ~0.12s sleep between calls plus exponential backoff
starting at 4s on any 429, up to ~7 attempts. Expect ~0.95s effective per contact.

### Safety rules that must be preserved
- **Enrichment only — never create contacts.** Read all existing Brevo contacts
  first, build a set of known emails, and skip any archive row not already in
  Brevo. On the 2026-08-24 run that skipped 85 rows. This keeps the task clear of
  any consent question: it only enriches people already through the normal path.
- **Never overwrite existing non-empty data with blanks.** Only fill genuine gaps.
- **Fall back gracefully on a bad phone:** if a PUT fails with a phone error,
  retry the same contact with the name fields only rather than losing the whole
  record. Source data contains junk numbers.
- Names arrive UPPERCASE and the upstream handler puts the customer's full
  display name in `first_name` with `last_name` blank. Split on whitespace and
  title-case, or emails will read "Hi ANA ROSELIA MENDEZ".

### Baseline to beat
Before the 2026-08-24 run: FIRSTNAME ~0.1% of file, SMS 0%, STORE ~54%. On the
engaged list (7) specifically — the audience that actually receives the weekly —
FIRSTNAME was 1 of 194 and STORE was blank on 99 of 194, which is why the
`{% if contact.STORE %}` personalised store block rendered empty for half the
audience. Verify with `_audit/verify_enrichment.py`, which samples the real file
at multiple offsets rather than trusting any import's self-reported counts.

### Still unsolved
STORE remains the weakest field. The archive only produced 3 new STORE fills
because most archive contacts already had it — the blanks are on OLDER list-3
contacts that predate the Chekkit flow entirely and appear in no per-store
source. Candidate fix not yet attempted: Brevo list 12 ("Valley Pawn - Lexington
(Store List)", ~2,647 contacts) can supply STORE=Lexington for any of its members
still missing it. There is no equivalent list for the other four stores.
"""

path = os.path.expanduser(
    "~/Documents/Claude/Scheduled/bravo-brevo-attribute-sync/SKILL.md")
with open(path, "r", encoding="utf-8") as f:
    cur = f.read()
if "PROVEN IMPLEMENTATION" in cur:
    print("already patched")
else:
    with open(path, "a", encoding="utf-8") as f:
        f.write(ADDENDUM)
    print(f"appended {len(ADDENDUM)} chars to {path}")
