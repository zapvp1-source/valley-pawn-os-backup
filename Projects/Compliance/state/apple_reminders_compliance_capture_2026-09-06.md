# Apple Reminders — compliance lists captured 2026-09-06

Pulled directly from the Reminders SQLite store (AppleScript access to Reminders is denied on this
Mac). Lists: **Annual Compliance and Tax Items** (list 16), **Compliance Tasks** (40), **Taxes and
Legal** (47), **Corporate Monthly** (3). This is the first durable capture of the "38-item" list
that `Admin Assitant/Reminders_Backup_2026-07-14.md` flagged as never itemized. Store nicknames:
Pepper = Culpeper · Boro = Waynesboro · Dixie = Harrisonburg (legacy name) · Lex = Lexington ·
PM = precious metals.

## Annual pattern (what the recurring dates say Joshua has actually been doing)

| When | Reminder title(s) | Reads as |
|---|---|---|
| Jan 1 | Pay Annual SCC Fee · Annual Gun Safety Training · PM Lex · Roanoke | SCC annual registration fee; annual employee gun-safety training; Lexington PM permit; Roanoke (unlabeled) |
| Feb 1 | Roanoke ×2 · Boro · Dixie · Lex | Unlabeled annual items — most likely business-license / BPOL filings (due Mar 1 in most VA localities) |
| Feb 15 | Pepper · Lex · Dixie · Boro (2023 titles: "Renew Business License …") | Business license renewals, 4 legacy stores |
| Mar 27 | Boro | Unlabeled (Waynesboro) |
| Apr 1 | Pepper (2023: "Scale Cert Pepper") | Culpeper scale certification |
| Apr 6 | Personal Property Tax (forms) | Business tangible personal-property returns (VA localities, due May 1) |
| Jun 1 | Renewal Workmans Comp Insurance · Renew General Business Insurance · PM Harrisonburg | Insurance renewals (actual: WC 6/13, BOP/GL 7/2); Harrisonburg PM permit |
| Jun 2 | Harrisonburg | Unlabeled |
| Jul 1 | Boro (2022: "Renew Prisons Metals Boro") | Waynesboro PM permit |
| Jul 28 | PM Pepper | Culpeper PM permit (bond term 7/28) |
| Aug 3 | PM Boro | Waynesboro PM permit (bond term 8/3) |
| Nov 1 | Lex · Roanoke | Unlabeled |
| Nov 19 | Harrisonburg · Lexington · Pepper | Unlabeled — three stores same day (2025 all completed) |
| Nov 25 | Roanoke | Unlabeled |
| Dec 1 | Pawnbroker Bond | Augusta County $50K pawnbroker bond |
| Dec 31 | Pepper (2022: "Renew previous Metals Pepper") | Culpeper PM (older cycle) |
| FFL | Culpepper 8/1/2026 ✅ · Salem 10/1/2026 ✅(closed) · **Roanoke 1/1/2027 marked COMPLETED — it is NOT** · Harrisonburg 12/1/2027 · Boro 1/1/2028 · Lexington 6/1/2028 · Culpepper 8/1/2029 · Roanoke 1/1/2030 | Roanoke's 2027 reminder was checked off in error — a live control failure |

Undated open items on list 16: Renew Surety Bond · Renew Business License · Submit Personal
Property Tax · FFL Renewal · Renew Precious Metals License · Scale Certifications.

## Compliance Tasks (list 40) — all completed
Atf move paperwork for pepper move · Send atf biz license, lease, letter · Comcast Review

## Taxes and Legal (list 47) — still open
Get umbrella policy · Consolidate insurance · Cost segregation 282 · Cost seg 14300 · Cost seg 817 ·
Deed 14300 · Deed 148 · Deed 282-DCCU Approval · File Business Return (3/1/2026) · File personal
return (4/1/2026). (Domain 2/3 items — logged here for completeness, owned by Taxes 2026 / Real Estate.)

## Corporate Monthly (list 3) — open
Send out Revenue Goals by store monthly (9/1) · Review Profit and Loss (9/18) · File Sales Tax
(10/2) · Schedule Store Visits (10/3)

**Interpretation rule:** unlabeled store-name reminders are carried into `OBLIGATIONS.json` as
`class: "unknown-annual"` with the date, so the calendar shows them and the brief asks for
identification the first time each comes due — never guessed into a specific obligation.

---

## UPDATE 2026-09-09 — the lists in this capture NO LONGER EXIST; live list is now "Compliance"

A fresh read of Reminders.app on 2026-09-09 (AppleScript, working — see technique note below)
returns exactly **10 lists**: CLAUDE AI (50), Joshua (647), Hillary (17), Madison (47),
Savannah (94), Kennedy (11), Audrey (8), PRIORITY (1074), Preston Joshua (0), Culpeper (4),
Waynesboro (0), Harrisonburg (12), Lexington (0), Roanoke (0).

**None of the four lists this capture documented — "Annual Compliance and Tax Items",
"Compliance Tasks", "Taxes and Legal", "Corporate Monthly" — are present**, and none of their
recurring items ("Pawnbroker Bond", "PM Boro", "PM Pepper", "PM Lex", "Renew Surety Bond",
"Scale Certifications") exist anywhere in the store. The Unified Search reminders index, refreshed
2026-09-09 08:14 UTC, agrees: 1964 reminders across those 10 lists, and only **5** incomplete
reminders carry a due date at all (none compliance-related). Those lists are either deleted or
live in a Reminders account not enabled on this Mac. Do not keep treating this capture's tables as
live state — they are a 2026-09-06 historical snapshot.

**New durable home: the `Compliance` list**, created 2026-09-09, seeded with the six real dated
obligations (5 surety bonds + the Lexington license), each with bond number, obligee, term, broker
contact and the caveats in the body. Due dates are set 60 days BEFORE expiry so they are
actionable, with the true expiration date in the reminder title. `OBLIGATIONS.json` remains the
system of record; this list is the human-facing surface.

### AppleScript technique — Reminders IS scriptable, if you do it right
Earlier sessions concluded "AppleScript access to Reminders is denied on this Mac." That was
wrong. Access works. What fails is the *query shape*: `whose` clauses, and per-item iteration
(`repeat with r in reminders of lst` then `name of r`) hang or time out on the large lists
(Joshua 647, PRIORITY 1074), which reads like a permission failure but is a performance cliff.
The working pattern is already implemented in `Unified Search/remindersindex.py`: **one list per
osascript subprocess with its own timeout, and bulk-fetch each property composed directly**
(`set nms to name of reminders of lst`) — never through an intermediate variable, which breaks
AppleScript's bulk-elements resolution. That is ~6 Apple Events per list instead of ~6 per item.
Creating and editing individual reminders is fast and needs none of this.

Reading the raw Reminders SQLite store is NOT a viable fallback any more — the current
`~/Library/Group Containers/group.com.apple.reminders/.../Data-*.sqlite` files no longer expose
titles or list names to plain SQL (checked 2026-09-09). Use AppleScript with the pattern above.

---

## CORRECTION 2026-09-09 (second pass) — the lists DO exist. AppleScript was lying.

Everything in the "UPDATE 2026-09-09" section above is WRONG and is retained only as a record of
the mistake. Joshua said the compliance lists were still there; he was right.

**Root cause: AppleScript enumerates only a SUBSET of reminder lists on this Mac.**
`tell application "Reminders" to get name of lists` returns **15** lists. EventKit returns **46** —
all in the same single "Personal" (CalDAV/iCloud) source. Every list this capture originally
documented is alive: `Annual Compliance and Tax Items`, `Compliance Tasks`, `Taxes and Legal`,
`Corporate Monthly`, plus ~30 more AppleScript never showed (`Audit`, `Human Resources`,
`Facilities`, `Stores`, `Marketing`, `Real Estate`, `Payables`, `Supervisor Daily/Weekly/Monthly`,
the per-property lists `282 Bald Rock Road` / `817 Richmond Road` / `14300 Woods Walk Lane` /
`148 Hardinberry Street` / `844 Cypress Crossing Trail`, and others).

**NEVER trust AppleScript for Reminders enumeration on this machine.** It silently returns a
partial list — no error, no warning. Two prior sessions drew wrong conclusions from it: first
"AppleScript access is denied" (it is not), then "those lists no longer exist" (they do).

### The tool: `Life OS/bin/ekrem`
A small Swift/EventKit CLI, source at `Life OS/bin/ekrem.swift`.
Rebuild with `swiftc -O -o ekrem ekrem.swift` in that directory.

```
ekrem lists                                  # every list, all sources
ekrem dump "<list>" [all|open]               # id, due date, open/done, recurring
ekrem setdue <itemIdentifier> <yyyy-MM-dd>   # also resets the alarm to that date
ekrem setnotes <itemIdentifier> "<notes>"
ekrem rename <itemIdentifier> "<title>"
ekrem complete <itemIdentifier>
ekrem add "<list>" "<title>" <yyyy-MM-dd> "<notes>"
ekrem dellist "<list>"
```
Run it via `Control your Mac` → `do shell script`. It handles large lists without hanging, and it
reads and writes. Use single quotes around arguments; avoid apostrophes inside note text.

### Bond / licence dates set this pass (all in `Annual Compliance and Tax Items`)
| Reminder | Due | Change |
|---|---|---|
| PM Lex | 2026-11-14 | **CREATED** — Lexington licence renewal; no PM Lex reminder existed |
| PM Harrisonburg | 2027-06-01 | date already right; notes added (3-year term) |
| PM Pepper | 2027-07-28 | **was 2026-07-28**, a year stale |
| PM Boro | 2027-08-03 | date already right; notes added |
| PM Roanoke | 2027-08-28 | **CREATED** — no Roanoke bond reminder existed at all |
| Pawnbroker Bond | 2027-12-01 | **was 2026-12-01**; the 12/1/2026 term was already paid 9/2/2026 |

Each now carries bond number, obligee, amount, term, surety and broker phone in its notes.
The short-lived duplicate `Compliance` list created earlier this session has been deleted.

Still undated in that list, deliberately left alone rather than guessed into a specific
obligation: `Renew Surety Bond`, `Renew Precious Metals License`, `Renew Business Licnese` [sic],
`Submit Personal Property Tax`, `Scale Certifications`, `FFL Renewal`.
