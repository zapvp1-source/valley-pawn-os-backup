# HANDOFF — P&P Manual v2026.7 is FINAL. Coordinate before any Gusto send.

**From:** the P&P review session, 2026-09-23 ~1:30 PM ET
**To:** the "Handbook Review and Gusto Onboarding" session (and any session that touches Gusto documents today)
**Joshua's instruction:** the Handbook is being done through Gusto in that session; the P&P session must wait or coordinate — not publish on its own.

## The one fact that matters

**The current Policies & Procedures Manual is `Valley_Pawn_PP_Manual_v2026.7_FINAL.docx` / `.pdf`, effective 2026-09-23.**
Location: this folder (`Human Resources/`). It landed at **1:22 PM ET**.

Every earlier version is in `_archive/2026-09-23/` and must not be sent:
- v2026.3 (this morning's starting point — what `#ask-handbook` used to serve)
- v2026.4, v2026.5, v2026.6 (intermediate, all superseded today; v2026.6 was in this folder from 1:00 to 1:22 PM)

## If you uploaded a P&P or the acknowledgment to Gusto BEFORE 1:22 PM today

It is the wrong version. **v2026.6 and earlier contain two firearms-law errors** (pawn redemption exempting permit holders from the background check and routing it to "ATF"; no Virginia one-handgun-per-30-days gate) that v2026.7 corrects, plus the wrong store hours and a superseded eBay ladder. A signed copy of a superseded version is worse than no signature. Please re-send against v2026.7, or tell Joshua which version went out so it can be re-sent.

## The acknowledgment form

`Valley_Pawn_Handbook_PP_Acknowledgment_HR-2026-04.docx` / `.pdf` (built 09:49 this morning, **HELD** since then) names BOTH manuals by exact version and effective date in its §1. Before it is sent, §1 must read:

- **Employee Handbook** — whatever version YOUR session finalises (it was v2026.2 FINAL this morning; if you bumped it, use the new number)
- **Policies & Procedures Manual — Version 2026.7 FINAL, effective September 23, 2026**

Send once, as a Gusto **Team document**, with **Future hires → All future hires** ticked (that flag is what makes it permanent) plus all current employees, then verify per-person "Needs signing" rows. The P&P session will NOT send it — your session owns the Gusto send so there is exactly one.

## What else changed in the P&P today that touches the Handbook boundary

- **Drug-Free Workplace / Cannabis policy** (eff. 9/2) is in NEITHER governing document and conflicts with the Handbook's cannabis clause. The P&P now carries only a pointer to the Handbook. It belongs in the Handbook — if your session is revising the Handbook, this is the moment to fold it in and supersede the conflicting clause. (`#ask-handbook` currently refuses cannabis questions because of this conflict.)
- **Employee firearms eligibility** is now a hard rule in P&P §10.06: no prohibited person under 18 U.S.C. § 922(g) may handle firearms, and **Va. Code § 18.2-308.2:3 requires a Virginia State Police background check on dealer employees who transfer firearms.** If the Handbook has a hiring/eligibility section, it should say the same thing.
- **PTO exceptions** (P&P §01.11) no longer cite FMLA (company is under 50 employees). If the Handbook's PTO section still cites FMLA, align it.
- **Timekeeping / breaks / dress code / conduct** rules from Joshua's 2025-12-16 staff meeting are now in P&P §01.01, §01.04, §01.05, §03.06 (geofence clock-in, break button, breaks by 2 PM, branded uniform, no phones on the floor, no cursing). Do not restate them in the Handbook with different wording — cross-reference.

## Automation note

`Ask_Handbook/build_sources.py` globs this folder for the HIGHEST-numbered `Valley_Pawn_PP_Manual_v*_FINAL.docx` and `Employee_Handbook_v*_FINAL.docx`. It already selects v2026.7. **If you publish a new Handbook version, drop it in this folder root with the same naming pattern and it is picked up automatically — but do NOT move the current copies in Google Drive; this folder is Drive-synced and a Drive-side move deletes the local file** (see the `drive-sync-file-safety` skill — that happened today and broke #ask-handbook for 43 minutes).

Full record: `Valley Pawn OS/CHANGELOG.md` (2026-09-23) and `Life OS/OPEN_ITEMS_REGISTER.md`.
