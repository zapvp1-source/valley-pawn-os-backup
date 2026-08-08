# Valley Pawn — Store Leases Tracker

**Created:** 2026-08-07, in direct response to a gap: a session pulled the Culpeper lease
correctly but had no idea a renewal notice had already been drafted/sent for it, because nothing
in `BUSINESS_OS.md` or `enterprise-map` pointed a session at lease status. This file exists so
that never happens again — read it any time a lease, renewal, landlord, or store real-property
question comes up for any of the 5 Valley Pawn stores.

**Root cause of the gap (for the record):** the renewal work existed only as files sitting in a
Google Drive subfolder with no index pointing to it. `enterprise-map`'s load protocol reads
BUSINESS_OS.md, the domain skills, and project STATUS files — none of which mentioned leases.
Step 8 ("check Slack/Drive before starting") only catches this if the session thinks to search
for that specific topic; a request that's just "give me the Culpeper lease" has no reason to also
go dig for "is there a pending renewal." A tracked list removes the guesswork.

---

## Status by store

| Store | Executed lease | Renewal / option status | Notes |
|---|---|---|---|
| **Culpeper** | `Culpeper Executed Lease.pdf` (Drive, 2024-03-28) | **Renewal Option Notice drafted 2026-07-21** — `Culpeper Lease - Renewal Option Notice (DRAFT - July 2026).docx/.pdf` in Drive. ⚠️ **Filename says DRAFT and send status is not yet confirmed against Gmail Sent — verify before telling Joshua this is fully closed out.** | Two docx revisions exist (base + "(1)"); PDF version also exists. Landlord response not yet located — check Gmail/Slack for a reply before closing this out. |
| **Waynesboro** | *(TODO — locate in Drive)* | *(TODO)* | |
| **Harrisonburg** | *(TODO — locate in Drive)* | *(TODO)* | |
| **Lexington** | *(TODO — locate in Drive)* | *(TODO)* | |
| **Roanoke** | *(TODO — locate in Drive)* | *(TODO)* | |

---

## Drive locations found so far

Search `title contains 'Lease'` in Drive to refresh this — folder IDs below, but don't assume
they're exhaustive; leases may also sit in per-store folders not yet mapped here.

- Culpeper executed lease + renewal drafts: multiple parent folder IDs seen
  (`1Y6yzZ7Xsc1vuJZHjcJokCNIMqRLhiXeY`, `1C73CJWTxoGOxNyDojzL0kGprf_FVfoMN`,
  `1tUwgGOL0LyGWHiUFncqjJy0jpyyXEdyN`) — there appear to be duplicate/legacy copies (a "copy" file
  exists). Consolidate when next touching this store's lease.

---

## How to extend this file

Any time lease work happens for any store — a renewal notice drafted, sent, countersigned, a rent
increase notice received, an option deadline identified — update that store's row here with the
date and a one-line status, not just "done." The two things that matter most: (1) was it actually
**sent**, verified against Gmail Sent or a Slack post, not just drafted, and (2) is there a
landlord response, and if so what it says. A drafted-but-unsent letter and a sent-and-confirmed
letter look identical in a file listing — the date + verified status line is what prevents the
next session from either re-doing work or wrongly assuming it's done.

**Immediate open item:** confirm whether the Culpeper renewal notice was actually sent (Gmail
Sent search for "Culpeper" + "renewal" + landlord contact, or ask Joshua directly if search comes
up empty) and update this table with a real verified date once confirmed.
