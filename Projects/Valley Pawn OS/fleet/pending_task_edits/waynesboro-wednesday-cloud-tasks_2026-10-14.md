# Pending edits — cloud task prompts, Waynesboro open Wednesdays (2026-10-14)

Joshua 10/14: Waynesboro is open 6 days (Mon–Sat) from 10/14. "Wednesday should be included in everything."
Wednesday = Culpeper + Roanoke + Waynesboro. Harrisonburg and Lexington stay closed Wednesday.

These tasks run as claude.ai cloud routines. A Mac session can't edit those prompts. Edit each routine's
prompt on claude.ai (or turn the cloud copy off where a native Mac version exists). The local Scheduled/
copies are disabled. They still carry the old text, which only matters if a local copy is ever revived.

## 1. daily-clockin-check — cloud trig_01XtvNrnsuiFkfP2NhUCpcBN (runs Mon–Sat 10:15, posts #general)
- Replace "**Wednesdays:** Culpeper and Roanoke are the only stores open (Roanoke open Wednesdays from 9/30/2026, Joshua 2026-10-01). Harrisonburg, Waynesboro, Lexington are closed. On Wednesday, **filter the report to Culpeper and Roanoke employees only**"
  with "**Wednesdays:** Culpeper, Roanoke and Waynesboro are open (Roanoke from 9/30/2026, Waynesboro from 10/14/2026). Harrisonburg and Lexington are closed. On Wednesday, **filter the report to Culpeper, Roanoke and Waynesboro employees only**"
- Replace "If `3`, apply the Culpeper + Roanoke filter." with "If `3`, apply the Culpeper + Roanoke + Waynesboro filter."
- A3 roster, Wednesday: add a third `list_employees` for the Waynesboro location. Its Gusto location_uuid is not in the repo, so look it up with get_locations, or keep employees whose department = Waynesboro.
- Wednesday format: header "(Culpeper, Roanoke & Waynesboro Only)"; sub-line "_Only Culpeper, Roanoke and Waynesboro are open on Wednesdays — Harrisonburg and Lexington are closed._"; all-clear line "All [N] Culpeper, Roanoke & Waynesboro employees…".
- Replace "**Wednesday = Culpeper + Roanoke only** (Roanoke open Wednesdays from 9/30/2026). Never flag Harrisonburg, Waynesboro or Lexington staff on Wednesday."
  with "**Wednesday = Culpeper + Roanoke + Waynesboro only.** Never flag Harrisonburg or Lexington staff on Wednesday."
- Description: "Wednesdays: Culpeper and Roanoke only" → "Wednesdays: Culpeper, Roanoke and Waynesboro only".

## 2. jewelry-onhand-nightly-pull — cloud trig_01VvvttPGf7VTqK6thQhf36m (Mon–Sat 20:30, #jewlery-counts)
- Replace `- Wednesday -> ["CUL","ROA"] only (Roanoke open Wednesdays from 2026-09-30, Joshua 2026-10-01).`
  with `- Wednesday -> ["CUL","ROA","WAY"] only (Roanoke from 2026-09-30, Waynesboro from 2026-10-14).`
- Replace "a Wednesday run covering only Culpeper and Roanoke is complete." with "a Wednesday run covering only Culpeper, Roanoke and Waynesboro is complete."
- jewelry-onhand-catchup (trig_013aQGcjJYLdEHMMuarXD8HC) has no Wednesday text. It inherits the gate from the nightly task, so no edit is needed.
- Tonight (Wed 10/14), the cloud run will skip Waynesboro unless this is edited first.

## 3. daily-cloudcover-check — cloud trig_017ef3AnQBKcnqSdKUztYWLA (the native bin/cloudcover_check.py is already fixed, but dormant)
- Replace "On Wednesdays, only Culpeper and Roanoke are open (Roanoke open Wednesdays from 9/30/2026). Only check and report on Culpeper and Roanoke. Do not include the other 3 locations."
  with "On Wednesdays, only Culpeper, Roanoke and Waynesboro are open. Only check and report on those three. Do not include Harrisonburg or Lexington."
- Wednesday JS: `STORE_LOCATIONS = ['SandiPepper', 'Roanoke1', 'Waynesboro1']`; `FRIENDLY_NAMES = { 'SandiPepper': 'Culpeper', 'Roanoke1': 'Roanoke', 'Waynesboro1': 'Waynesboro' }`.
- "If today is Wednesday, only check Culpeper's and Roanoke's URLs." → "…Culpeper's, Roanoke's and Waynesboro's URLs."; Wednesday header "(Culpeper, Roanoke & Waynesboro)".
- Or switch the cloud copy off and go native (see the CHANGELOG 2026-10-14 native cloudcover entry).

## Account skills (not editable from a session)
- valley-pawn-context, directory-listing-monitor and daily-clockin-check still say Waynesboro is closed Wednesdays.

## Off and needing no edit
chekkit-unanswered-alert (cloud off 10/14, native live), chekkit-unanswered-eod-followup, daily-store-audit-digest and dress-code (cloud copies off 10/8). Those native versions are already fixed in code.

## ADDENDUM 2026-10-14 evening — Waynesboro also closes 5:00 PM Saturdays (Joshua: 6-day-store rule applies)
Waynesboro = Mon–Fri 10–6, Sat 10–5, closed Sun (first affected Saturday 10/17). Additional cloud-prompt edits:
- jewelry-onhand-nightly-pull (trig_01VvvttPGf7VTqK6thQhf36m): wherever the freeze window / close time says
  "CUL/ROA 5 PM Sat" (or "Culpeper and Roanoke close at 5 PM on Saturday"), make it "CUL/ROA/WAY 5 PM Sat"
  ("Culpeper, Roanoke and Waynesboro close at 5 PM on Saturday").
- jewelry-onhand-catchup (trig_013aQGcjJYLdEHMMuarXD8HC): same Saturday close sentence if present.
- vp-presence-audit-weekly / vp-ai-search-health-check (if run as cloud routines): NAP hours lines → Culpeper,
  Roanoke & Waynesboro Mon–Fri 10–6, Sat 10–5; Harrisonburg & Lexington Mon/Tue/Thu/Fri/Sat 10–6, closed Wed & Sun;
  "only the 6-day stores (Culpeper, Roanoke & Waynesboro) close at 5 PM, and only on Saturday."
- Account skills valley-pawn-context / directory-listing-monitor: Store Hours block + canonical footer line →
  "Culpeper, Roanoke & Waynesboro: Mon–Fri 10am–6pm, Sat 10am–5pm. Harrisonburg & Lexington: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun)."
