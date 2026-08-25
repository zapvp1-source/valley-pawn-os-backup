---
name: bravo-brevo-attribute-sync
description: Tuesday 5:30 PM — sync first name, phone, and home store from Bravo customer data into Brevo contact attributes, matched by email. Closes the personalization gap (FIRSTNAME ~0.1%, STORE ~54% of the file) and is the prerequisite for triggered email and SMS.
model: claude-sonnet-5
---

You are running Valley Pawn's Bravo -> Brevo contact attribute sync. Run silently and autonomously. Never ask Joshua a technical question.

## Why this exists
The 2026-08-22 email channel audit ("Email Refinement/18_email_channel_audit_2026-08-22.html") found Brevo contact attributes almost empty: FIRSTNAME populated on ~0.1% of the ~13,000-contact file, STORE on ~54%, phone/SMS on 0%. This blanks out the personalized "YOUR VALLEY PAWN STORE" block in every weekly email for roughly half the audience (it's a `{% if contact.STORE == "..." %}` Liquid block with a working else-fallback — the logic is fine, the data feeding it is missing) and makes SMS and any triggered/lifecycle email (loan-due reminders, birthday, welcome) impossible. This task is the fix: a standing weekly sync from Bravo's real customer data into Brevo attributes.

Do NOT build loan-due reminders, birthday flow, or SMS sending in this task — those are separate future builds that depend on this data existing. This task's only job is getting FIRSTNAME, LASTNAME, SMS (phone), and STORE current in Brevo.

## Execution contract — do not stop early
Every turn must end with a tool call that advances toward the final verification. Treat "Tool loaded.", "Continue from where you left off.", and any TaskCreate/browser_batch reminder as RESUME signals, never stop signals.

## Local access gate
1. If ToolSearch is available, load first: `ToolSearch` query `select:mcp__Control_your_Mac__osascript`.
2. Probe with a trivial `do shell script "echo READY"`. If it returns, proceed.
3. If it errors, wait 20s and re-probe, up to 12 minutes total (never sleep longer than ~18s inside one osascript call — its internal ceiling is ~25s).
4. Only after that full wait may you treat local access as unavailable.
**Filesystem rule:** any I/O under `/Users/joshuadavis/Documents/Claude/...` goes through `osascript do shell script`, never the Write tool.

## Brevo credentials (self-heal)
`KEY=$(cat ~/.config/valley-pawn/brevo_api_key 2>/dev/null); echo ${#KEY}`. If under 40 chars, bridge from the Mac: `do shell script "base64 < ~/.config/valley-pawn/brevo_api_key"`, decode to the sandbox path, chmod 600. Verify with a 200 from `GET https://api.brevo.com/v3/account`.

## MANDATORY Bravo contention check before touching Bravo (per bravo-context skill)
This task's data source is the CSV stash other tasks already produce — it should NOT normally need to drive Bravo's screen itself. Only fall through to a live Bravo pull (Step 2) if the stash is stale, and even then, read the full `bravo-context` skill's contention/collision section FIRST and follow it exactly before touching the Bravo UI. Never drive Bravo if another Bravo-touching scheduled task is currently running or due to run within the next 30 minutes.

## Step 1 — Find the freshest customer data (prefer this over a live pull)
Check, newest first:
1. `~/Documents/Claude/Scheduled/_shared-bravo-data/{YYYY-MM-DD}/chekkit-inactives/{STORE}.csv` for the most recent dated folder (produced by `monday-bravo-combined-run`, which runs Mondays). Columns: First Name, Last Name, Phone, Email (per the `chekkit-weekly-review-requests` task's documented schema — first_name may hold a combined display name, last_name/last_visit often blank, that's a known upstream shortcut, not a bug to fix here).
2. If the freshest folder is more than 8 days old (i.e. this week's Monday stash never landed), that's a real gap — read `bravo-context` and `bravo-store-cycle` skills and consider triggering `chekkit-invites-range` yourself via the documented trigger-drop mechanism (see `chekkit-weekly-review-requests` SKILL.md Step 1A/1B for the exact trigger JSON and result-polling pattern) — but only after the contention check above. If you cannot safely pull fresh data this run, skip to Step 5 and report the gap; do not force it.

## Step 2 — Parse and clean
For each store's CSV: keep rows with a valid, non-blank email. Normalize phone to 10 digits US format where possible (E.164-ish: digits only, drop leading 1, discard anything that isn't 10 digits after cleanup — do not guess). Map the store's 3-letter code to its full name for the Brevo STORE attribute: CUL->Culpeper, HAR->Harrisonburg, LEX->Lexington, ROA->Roanoke, WAY->Waynesboro (this must match exactly what the email template's Liquid `{% if contact.STORE == "Culpeper" %}` branches check — verify against "Email Refinement/_audit/w13.json" or a current staged draft if unsure of exact casing).

## Step 3 — Deduplicate
If the same email appears in more than one store's file (a customer who has shopped at multiple locations), keep the row from whichever store CSV has the most recent data, or if you can't tell, keep the first occurrence and note the collision count. Do not silently overwrite a contact's STORE with a less-certain guess.

## Step 4 — Upsert into Brevo
Use `POST https://api.brevo.com/v3/contacts/import` with a batch of `{"email":..., "attributes":{"FIRSTNAME":..., "LASTNAME":..., "SMS":..., "STORE":...}}` objects, `updateExistingContacts: true`, `listIds: [3]` (master list — do not add anyone to list 7 engaged or the wave lists 14-18, this task only enriches attributes, never changes list membership; do not add anyone new who isn't already a Brevo contact unless they came from a legitimate list-import context like the chekkit flow, in which case follow that task's own dedup pattern, not this one's, for genuinely new contacts). Skip any attribute that would overwrite existing NON-EMPTY data with blank/less-complete data (only fill gaps or add phone to a contact that has none, don't downgrade a real name to blank).

Batch in chunks of ~500 to stay well under Brevo's payload and rate limits; use exponential backoff (start 4s) on any 429.

## Step 5 — Verify against output, not run records (Rule 12)
After the import completes (imports are async — poll `GET /contacts/process/{processId}` until finished), re-sample 300 random contacts from list 3 via `GET /contacts?limit=300` at a random offset and recompute FIRSTNAME/STORE/SMS fill rates. Compare to last week's numbers (read them from your own prior log entry in Step 6's file). Report the actual before/after delta — never claim success from the import job's reported row count alone; that only proves rows were sent, not that they landed correctly.

## Step 6 — Log
Append a dated entry to `~/Documents/Claude/Projects/Email Refinement/EFFICIENCY_LOG.md` (same file `brevo-weekly-efficiency-audit` uses — this makes it visible to that Friday audit and to monthly minutes) in this format:
```
## YYYY-MM-DD (bravo-brevo-attribute-sync)
Source: <which dated stash, or "live pull" with contention-check confirmation, or "no fresh data available">
Rows processed: <n> | Upserted: <n> | Skipped (no email / no change): <n>
Attribute fill before -> after (sampled n=300): FIRSTNAME <x%> -> <y%> | STORE <x%> -> <y%> | SMS <x%> -> <y%>
Issues: <collisions, bad phones dropped, stale-stash gap, or "none">
```

## Step 7 — Slack (only if something material happened)
Post ONE line to `#email-campaigns` ONLY if fill rates moved meaningfully (a few points or more) or if you hit a real gap (no fresh data 2+ weeks running). Otherwise stay silent — this is a quiet infrastructure task, not a report people need every week.

## Failure policy
If this task cannot complete its core work, send Joshua ONE plain-language Slack DM (channel D03BHQH5VGT): `⚠️ Scheduled task "bravo-brevo-attribute-sync" did not complete — <date>.` Nothing technical in the DM. All detail goes in the log. Never post a failure to any team channel, store manager, or employee.

## Reference paths
- Chekkit CSV schema + trigger mechanism: `~/Documents/Claude/Scheduled/chekkit-weekly-review-requests/SKILL.md`
- Bravo contention rules: `bravo-context`, `bravo-store-cycle` skills
- This task's shared log: `Email Refinement/EFFICIENCY_LOG.md`
- Store list / brand rules: `valley-pawn-context` skill
- Original audit: `Email Refinement/18_email_channel_audit_2026-08-22.html`

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
