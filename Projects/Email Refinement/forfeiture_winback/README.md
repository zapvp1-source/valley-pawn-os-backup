# Forfeited-Loan Win-Back — how it runs (v2 exact-match, 2026-09-29)

Strategy and copy are unchanged. See `../15_forfeited_winback_consolidated.md` and `Gold and Silver Markeitng/forfeited-winback-copy-pack.md`.

v2 was built because Joshua asked for "better data, phone contact, 100% accuracy on target audience". v1 matched customers on name alone and could only tell to the week whether someone came back. v1 is kept in `_v1/`.

## The rule
- **Identity** = the customer's full name (suffix kept) + the address Bravo prints on both the ticket and the customer record. On the CUL test, all 119 of 119 matches were exact.
- **Came back** = Bravo's own customer **Last Time In** is on or after the forfeit date.
  - The forfeit date is the earlier of Pull Date and Disposition Date.
  - A same-day visit counts as came back.
  - Checked 9/29: the forfeit itself does not update Last Time In. None of 10 fresh forfeits showed up as a visit.
- **Target** = verified not back. If any check can't be verified, the customer is excluded and listed in `runs/<RUN>/excluded.csv` with the reason. We never guess:
  - no Last Time In found for them
  - two customers share the same name and zip
- **Phone**:
  - Customer-record phone is used only when it matches exactly one person.
  - "Textable" means the customer's SMS status is `SMS` (not `DNT`) **and** none of their forfeited tickets is marked DNT.

## Bravo views (all additive; the saved reports are never re-saved)
Column layouts are applied for the run only.

| File | Saved report + column layout | Criteria / columns |
|---|---|---|
| `RUN_ST_forfeiture-winback-addr.csv` | "Claude Forfeiture Winback" + **High Dollar Loan Demographic** | LOAN, EXPIRED, age < 730, rows 5000. Columns: ticket, disposition, dates, customer, SMS, **address** |
| `D_ST_forfeiture-winback-comparison-contacts.csv` | "...Comparison" + **Customer Address Check** | Name, phone, address, e-mail, SMS |
| `D_ST_forfeiture-winback-comparison-visits.csv` | "...Comparison" + **Customers First Time In** | Name, zip, first and **last time in** |

The comparison report's criterion is Last Time In > D:
- **Weekly:** contacts at D = run − 60 and visits at D = run − 7.
- **Every 12 weeks per store (`full_<ST>` marker):** both at D = run − 760 with rows 20000. This is the full directory.

Pipeline cell options (in the `date` field): `<date|saved>|rows=N|stamp=YYYY-MM-DD|layout=<exact label>|tag=<x>`. Every file gets a `.meta` expected/captured sidecar. The builder requires ≥ 99.5% of rows captured, or that store is skipped for the run.

## Schedule
- Native agent `com.valleypawn.forfeiture-winback`, **Sunday 12:30**.
- Script: `Valley Pawn OS/bin/forfeiture_winback_weekly.sh`. Log: `~/Library/Logs/valleypawn/forfeiture-winback.log`.
- Steps: pull, then `fwb_build.py`, then Brevo list 11 import, then send. The send only runs if `SEND_APPROVED` exists in this folder.

## Outputs per run (`runs/<RUN>/`)
- `audience.csv`: email targets.
- `sms.csv`: textable phones.
- `excluded.csv`: who was left out and why.
- `report.md`: per-store counts.
