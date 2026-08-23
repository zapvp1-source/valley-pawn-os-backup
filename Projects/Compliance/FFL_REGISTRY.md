# FFL REGISTRY — Full Circle Finance Inc DBA Valley Pawn

**The single source of truth for FFL numbers, types, expirations, and where each license is
listed.** Read this before sending an FFL number to any vendor, directory, or transfer partner.

Created 2026-08-22. Every number below was read off the ATF license itself (image/PDF in
`Compliance/ffl-files/`) and, where noted, confirmed live against ATF FFL eZ Check.
**Do not copy FFL numbers out of old emails — two of the five were wrong in a vendor email
sent 2026-05-04 (see "Known bad data in circulation" below).**

---

## Canonical license table

| Store | FFL # | Type | Expires | Premise address | Source verified |
|---|---|---|---|---|---|
| Culpeper | **1-54-047-02-9J-25407** | 02 Pawnbroker | **2029-09-01** | 571 James Madison Hwy Unit C, Culpeper, VA 22701 | ✅ eZ Check live 2026-08-22 + renewed license PDF |
| Waynesboro | 1-54-820-02-8B-24709 | 02 Pawnbroker | 2028-02-01 | 1321 W Broad St, Waynesboro, VA 22980 | ✅ eZ Check live 2026-08-22 |
| Harrisonburg | 1-54-165-02-7M-26284 | 02 Pawnbroker | 2027-12-01 | 1790 E Market St Unit 22, Harrisonburg, VA 22801 | License PDF (eZ Check not re-run) |
| Lexington | 1-54-163-02-8F-26584 | 02 Pawnbroker | 2028-06-01 | 125 Walker St, Lexington, VA 24450 | License scan (eZ Check not re-run) |
| Roanoke | 1-54-770-02-7A-27330 | 02 Pawnbroker | **2027-01-01** | 2362-D Peters Creek Rd, Roanoke, VA 24017 | License scan (eZ Check not re-run) |

**All five are Type 02 — Pawnbroker in Firearms Other Than Destructive Devices. None is a
Type 01 Dealer.** Vendor forms that ask "01 or 02" get **02** for every store.

Licensee name on every license: `FULL CIRCLE FINANCE INC` · Trade name: `VALLEY PAWN`.

### ⚠️ Culpeper's number CHANGED at renewal — `6J` → `9J`

The renewal issued a new license with a different suffix. Old: `1-54-047-02-**6J**-25407`
(exp 2026-09-01). Current: `1-54-047-02-**9J**-25407` (exp 2029-09-01), signed by Joshua Davis
2026-03-21, responsible person changed from Preston Peters to Joshua Davis.

Anything still publishing `6J` is publishing a superseded number. Known locations corrected
2026-08-22: `Compliance/FFL-Transfer-page.html`, this file, `ffl-files/culpeper-ffl.pdf` (the
renewed license, pulled from Drive; the old scan is kept as
`culpeper-ffl.SUPERSEDED-6J-exp2026.jpg`).

**Still carrying `6J` and NOT yet corrected — needs a human or an approved publish:**
- The **live FFL transfer page on thevalleypawn.com** and the license image it links
  (`/wp-content/uploads/2026/06/culpeper-ffl.jpg`) — this is the page vendors use for the daily
  transfer process, so this is the highest-impact stale copy.
- The Google Drive doc **"READ ME - signed FFL copies"**
  (`docs.google.com/document/d/1bB6vm77FKorzrbQhcbm5TJvs3TaAoawyivM79jJYaU4`), last updated
  2026-06-18, still says Culpeper exp 2026-09-01.
- Every vendor holding a copy sent before 2026-03-21.

### ATF mailing address of record — ⚠️ not a store

eZ Check shows ATF's mailing address for Culpeper and Waynesboro as:

```
844 CYPRESS CROSSING TRAIL, ST AUGUSTINE, FL 32095
```

That is Joshua's **personal residence in Florida**, not 282 Bald Rock Rd and not any store.
The paper licenses on file still print `282 BALD ROCK RD, VERONA, VA 24482` — so ATF's record
was changed after those copies were signed.

**This is the root cause of the July 2026 "missing renewal" scramble.** ATF mailed Culpeper's
renewal form on 2026-06-03; Preston was watching Virginia mail for it and escalated to FFLC on
7/13 when it never showed. It went to Florida.

Consequence going forward: **every future renewal form and every ATF notice for all five
licenses lands in St. Augustine.** Roanoke's renewal form should mail around **2026-10-03**
(≈90 days before its 2027-01-01 expiration) — watch the Florida mail, not the store mail.
Either accept that and build the watch around it, or file to change the mailing address of
record back to a Virginia address that someone checks daily.

---

## Known bad data in circulation

A dealer-account application sent to wholesale vendors on **2026-05-04** (subject: *"New Dealer
Account Application — Full Circle Finance Inc DBA Valley Pawn (5 VA locations)"*, sent to Crow
Shooting Supply and others) contained a store/FFL table with these errors:

| Field | What was sent | What is correct |
|---|---|---|
| Waynesboro FFL # | 1-54-820-02-**5B**-24709 | 1-54-820-02-**8B**-24709 |
| Lexington FFL # | 1-54-**678**-02-**5F**-26584 | 1-54-**163**-02-**8F**-26584 |
| License type, all 5 stores | "01 Dealer" (except Roanoke) | **02 Pawnbroker** on all five |

Any vendor who ran those two numbers through eZ Check got **no match**, which reads as a
fraudulent or invalid license. That is a silent-kill failure mode: the application does not get
rejected with a reason, it just never progresses. Assume every dealer application sent with
that table needs to be resent with corrected data.

Also stale: **the license copies in `Compliance/ffl-files/` are the pre-renewal Culpeper
license showing a 2026-09-01 expiration.** Any vendor holding that copy believes Valley Pawn's
Culpeper FFL expires in days — GrabAGun sent expiration warnings on 2026-07-31 and 2026-08-16
for exactly this reason. Re-scan the current Culpeper license and re-send to every vendor of
record.

---

## Renewal calendar

| Store | Expires | ATF mails renewal ≈ | Must be postmarked by |
|---|---|---|---|
| Roanoke | 2027-01-01 | 2026-10-03 | 2027-01-01 |
| Harrisonburg | 2027-12-01 | 2027-09-02 | 2027-12-01 |
| Waynesboro | 2028-02-01 | 2027-11-03 | 2028-02-01 |
| Lexington | 2028-06-01 | 2028-03-03 | 2028-06-01 |
| Culpeper | 2029-09-01 | 2029-06-03 | 2029-09-01 |

ATF rule confirmed in writing by FFLC (2026-07-14): a duplicate renewal form **must be
postmarked before the license expires** to be accepted. Duplicate-form request line:
**304-616-4590**. General FFLC: FFLC@atf.gov / 866-662-2750.

If a renewal application is submitted on or before expiration, the FFL may keep operating while
it is processed (27 CFR 478.45) — eZ Check will show an LOA date until the new license issues.

---

## Where the licenses are listed

See `FFL_LISTINGS_STATUS.md` in this folder for the live directory/vendor listing state and the
open action list.

## Maintenance rules

1. **Never re-derive an FFL number from an email or a prior audit.** Read the license, or run
   eZ Check (https://fflezcheck.atf.gov/FFLEzCheck/ — accept the DOJ banner, then enter the
   first three digits and last five).
2. **Re-scan and replace the copies in `ffl-files/` the day a renewed license arrives**, and
   push the new copy to every vendor holding one.
3. Update this file the same day anything changes. It is the index other work reads.
