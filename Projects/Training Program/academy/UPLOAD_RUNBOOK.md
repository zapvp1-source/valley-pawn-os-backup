# TalentLMS upload runbook (proven 2026-09-28 on L1-01)

Portal: https://valleypawn.talentlms.com (Joshua signed in as Administrator in Chrome).
Zips: /Users/joshuadavis/Documents/Claude/Projects/Training Program/academy/dist/<file>.zip

Course IDs: L1=126 L2=127 L3=128 L4=129 L5=130 L6=131 L7=132 L8=133 M=134

Per lesson (in lesson order within a course):
1. navigate https://valleypawn.talentlms.com/plus/courses/<ID>/edit ; wait ~8 s (page is slow; screenshots time out while it loads — wait and retry).
2. Click blue "+ Add" (left panel, ≈ x=42,y=134 in the 1568x772 frame) → click "Learning Activities" (≈ x=180,y=245) → click "SCORM | xAPI | cmi5" (≈ x=440,y=365). A new unit "Scorm unit" opens at /plus/courses/<ID>/units/<unitId>/edit.
3. `find` "file input for SCORM upload" → file_upload that ref with the zip path. NEVER click the file input. Wait ~10 s; success = "This type of file cannot be edited directly."
4. Rename: click the unit title "Scorm unit" at top (≈ x=610,y=38), cmd+a, type "<n.m> <Lesson title>" (e.g. "1.1 Welcome to Valley Pawn"), Enter, click empty area.
5. Next lesson: repeat from step 2 on the same course page (unit list shows on the left; new units append at the bottom — keep lesson order).

Unit title format: "<level>.<order> <title>"; Manager track uses "M.<order> <title without the 'Manager track: ' prefix>".

Never: Publish/activate the course, add users, enroll anyone, upgrade, delete.
