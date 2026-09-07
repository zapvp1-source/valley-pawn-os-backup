# FFL DEPARTMENT — OPERATING MAP

**Domain 1 — Full Circle Finance Inc DBA Valley Pawn.** One page. Start here for anything FFL:
licenses, transfers, directory listings, vendor copies, renewals, NICS fees, gun audits.

Created 2026-09-05. Update this file the same day anything structural changes.

---

## The four files that ARE this department

| File | What it holds | Who writes it |
|---|---|---|
| `FFL_REGISTRY.md` | Canonical FFL numbers, types, expirations, renewal calendar, ATF mailing address of record, known-bad data in circulation | Humans/sessions. **Never derive an FFL number from anything else.** |
| `ffl_vendors.json` | Machine-readable roster: every directory / retail locator / wholesale vendor × store — listed status, which copy version they hold, when it was sent, what's next | `ffl_guardian.py` + sessions |
| `FFL_LISTINGS_STATUS.md` | Human narrative view of the same ground + why each item matters | Sessions (regenerate from the roster) |
| `ffl-files/` | The licenses themselves. `{store}-ffl.pdf` = full-res master, `{store}-ffl-web.pdf` = ~250KB email-friendly. `*.SUPERSEDED-*` = never send | Sessions, on each renewal |

Everything else FFL-related is downstream of these.

---

## Standing decisions

- **ATF mailing address of record stays 844 Cypress Crossing Trail, St. Augustine FL 32095**
  (Joshua, 2026-09-05). All five licenses' renewal forms and every ATF notice arrive at Joshua's
  Florida house, not at any store and not at 282 Bald Rock Rd. Do not "fix" this. The expiration
  ladder in `ffl_guardian.py` is what covers the risk.
- **Roanoke's premise address is `2362-D Peters Creek Rd`** on the ATF record and that is CORRECT —
  Roanoke occupies both Suite C and Suite D. Customer-facing NAP says "Suite C". Never "correct"
  the FFL record to match the website.
- **All five licenses are Type 02 Pawnbroker.** Any vendor form asking 01 vs 02 gets 02.
- **Never use "Dixie Pawn" or "GNP Pawn"** in any submission (hard rule, `valley-pawn-context`).
- Vendors get the **signed 8/21/26 copies** (`*-ffl-web.pdf`), never the older unsigned scans.

## Known blockers — do not burn a session re-attempting these

- **Claiming a MasterFFL profile cannot be automated.** The claim modal requires a reCAPTCHA plus an
  SMS or voice code to that store's own phone number. All five profiles exist with correct data and
  are unclaimed; claiming is a two-minute job for whoever is standing at each store phone.
- **MidwayUSA is portal-upload only** — their notices come from an outgoing-only address. Updating
  the license means signing into https://www.midwayusa.com/ffl-dealer/register in Chrome.
- **Bill Hicks & Co** needs their dealer application form filled (credit and bank references) — not
  an FFL-copy matter, and not something a session should invent answers for.

## The sixth license — Salem (closed store)

`1-54-161-02-6K-27258`, 1617 W Main Street, Salem VA 24153, **expires 2026-10-01**, still ACTIVE on
ATF eZ Check as of 2026-09-06, ATF mailing address 282 Bald Rock Rd Verona (not Florida). The store
is closed. It is in the roster as `SAL` with `closed: true` and no license file, so the guardian
warns on the date but will never send it to a vendor. Open questions in `FFL_REGISTRY.md` — the one
that matters is whether the acquisition-and-disposition records were dispositioned to ATF under
27 CFR 478.127, not the expiration itself.

## Renewal calendar (from FFL_REGISTRY.md)

| Store | Expires | ATF mails form ≈ | Postmark deadline |
|---|---|---|---|
| **Roanoke** | **2027-01-01** | **2026-10-03** (to FL) | 2027-01-01 |
| Harrisonburg | 2027-12-01 | 2027-09-02 | 2027-12-01 |
| Waynesboro | 2028-02-01 | 2027-11-03 | 2028-02-01 |
| Lexington | 2028-06-01 | 2028-03-03 | 2028-06-01 |
| Culpeper | 2029-09-01 | 2029-06-03 | 2029-09-01 |

A duplicate renewal form must be **postmarked before expiration** (FFLC, in writing 2026-07-14).
Duplicate-form line **304-616-4590**; FFLC@atf.gov / 866-662-2750.

---

## Automations

### Native launchd (no Claude usage, runs even when the fleet is saturated)
| Agent | When | Does |
|---|---|---|
| `com.valleypawn.ffl-guardian` | Daily 7:15 AM ET | Relays website transfer requests to `#gun-transfers`; digests new inbound GunBroker/MasterFFL transfers by store; auto-replies to vendor "FFL expiring/expired" mail with the correct signed copy; runs the 120/90/60/30/14-day expiration ladder to Joshua's DM; writes `ffl_status.json` |

Script: `Valley Pawn OS/bin/ffl_guardian.py` · wrapper `ffl_guardian_run.sh` (vp-runner pattern)
State: `Compliance/.ffl_guardian_state.json` (dedupe — every relay/reply keyed by message id)
Log: `~/Library/Logs/valleypawn/ffl-guardian.log`

### Cowork scheduled tasks (do not modify — hardened)
| Task | When | Channel |
|---|---|---|
| `nics-weekly-mtd-ranking` | Mon 9:30 AM | #ffl-transfer-performance |
| `nics-monthly-ranking` | 1st 9:30 AM | #ffl-transfer-performance |
| `monthly-gun-audit-report` | 16th 2:30 AM | #monthly-gun-audit |
| `ffl-transfer-email-responder` | 8:50 AM / 4:50 PM | replies in Chekkit/Gmail, silent otherwise |
| `vp-presence-audit-weekly` | Sun 4:20 PM | #ai-marketing — carries the weekly FFL directory block |

### Retired / gone (do not resurrect)
`daily-ffl-transfer-check`, `ffl-web-form-to-slack` (deleted; the guardian replaces both),
`vsp-nics-fee-monthly-check` (gone; VSP fee is a documented manual step, see below).

---

## Channels

| Channel | Purpose |
|---|---|
| `#gun-transfers` (C0B08U7AC7P) | **Field channel.** Website transfer requests + inbound transfer digests, routed to the pickup store. Store staff are members. |
| `#ffl-transfer-performance` (C0BPH5T1NFL) | Weekly MTD + monthly transfer rankings by store |
| `#monthly-gun-audit` (C07CPN020G0) | The 5 monthly 4473 audit forms + the trend summary |
| `#compliance` (C04NZ3GGMPH) | Staff compliance questions (assault-weapon classification, suppressors, etc.) |
| `#ffl-copy` (C07U8MVTK37) | Staff pulling a license copy — the website is now the better source |
| `#ffl-transfer-notifications` (C0BA6SXL8AK) | **Dead** (last post 2026-07-30). Superseded by `#gun-transfers`. Archive. |

---

## Other recurring FFL obligations

- **Monthly gun audit** — each store submits its 4473 audit form by the **15th**; the task compiles
  on the 16th. Trend sheet: `1sLid9zjLUkH-B8MOE5Fr_aemw35bxyAbtuUz4BTVA6s`.
- **VSP NICS fee** — invoices post the 1st, pay from the 5th at https://ebilling.vsp.virginia.gov
  (user X009686). Full flow in `VSP-NICS-Fee-Payment-Runbook.md`. Two record corrections still
  pending with VSP: Culpeper billed under "Joshua Christian Davis" (should be the corporation);
  Lexington still shows 439 E Nelson St (should be 125 Walker St).
- **Transfer trend sheet** — `1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs`, fed by the nics tasks.

## Public surface

- FFL Transfer page: https://thevalleypawn.com/ffl-transfer/ — per-store FFL#, downloadable signed
  copy, $25 fee, and the "Notify us" form whose submissions the guardian relays.
- Signed copies live at `/wp-content/uploads/2026/08/{store}-ffl-signed-2026-08.pdf`.
- Drive: "READ ME - signed FFL copies" (`1l4NM1eQaERLEMt6t7uwzkVowXdJaoWDbh1YS2sbzsiA`).

## The failure mode this department keeps having

A license renews, the local copy gets updated, and **the vendors of record are never told** — so
retailers silently drop us from their FFL locators and the customer picks another dealer. It
happened with Culpeper in Aug–Sep 2026 (GrabAGun cut Culpeper off entirely on 9/1 after warning
7/31 and 8/16). The guardian's expiry-auto-reply and the roster's `copy_version` field exist for
exactly this. **On any renewal: update the master, the website, the registry, and every vendor in
`ffl_vendors.json` the same day.**
