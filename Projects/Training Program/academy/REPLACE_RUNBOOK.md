# Replace an existing SCORM unit with the latest build (proven 2026-09-28 on 1.1)

Zips: /Users/joshuadavis/Documents/Claude/Projects/Training Program/academy/dist/<file>.zip (see dist/manifest_index.json)
Course IDs: L1=126 L2=127 L3=128 L4=129 L5=130 L6=131 L7=132 L8=133 M=134

Per unit:
1. navigate https://valleypawn.talentlms.com/plus/courses/<ID>/edit — the page is SLOW: wait 25–30 s (3×10 s waits) before `find`. If find sees nothing, wait 10 s more and retry.
2. Click the unit in the left list (titles "<level>.<n> …" / "M.<n> …"); wait ~8 s.
3. Click the "Change" link at the top-right of the unit content (≈ x=1283–1290, y=83 in the 1568×772 frame). It often needs a second click after the page settles. Success = two panels "Upload a SCORM, xAPI, or cmi5 file" / "Select a course file".
4. `find` "file input type=file for SCORM upload" → `file_upload` the zip to that ref. NEVER click the input. Wait 15 s. Success = unit shows "Unpublished changes" + "This type of file cannot be edited directly." If it still shows the two upload panels, `find` the file input again (new ref) and upload once more.
5. If a "Publish changes" button appears top-left (≈ x=118, y=24), click it (it publishes only content changes; it does NOT activate an inactive course). If there is no such button, continue.
6. Next unit.

Never: activate/deactivate courses, add/enroll users, change roles, upgrade, delete units. Do not touch unit 1.1 (unit 2065) — it is already on the final build.
