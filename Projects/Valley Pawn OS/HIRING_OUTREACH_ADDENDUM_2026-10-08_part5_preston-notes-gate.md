# HIRING_OUTREACH addendum — 2026-10-08 ~1:25-1:45 PM ET — Preston-notes gate (interactive session)

Merge into HIRING_OUTREACH.md "Contact log" and the Preston "ALREADY HANDLED" exclusion list.

## Trigger
Preston, #employee-prospects 1:24 PM: "Claude is recycling into people we already have talked to. Desmond Chick has notes already from the interview. Can you get him to look at those notes before scheduling."

## Root cause
The pipeline's contact check grepped this file and the Indeed message thread only. It never opened the candidate's Indeed **Activity & notes** tab, which is where Preston records interview notes and rejections. The 10/1 addendum had Desmond on the "Preston already interviewed — not a phone screen" list, but later runs did not read the addenda, so he was re-contacted on 10/7 and booked on 10/8.

## Desmond Chick (Harrisonburg)
- Preston phone-interviewed him 9/17. Preston's note: "Moved here from Africa, looking to learn more about business and pawn. 18+, no 2 weeks needed. Has a living situation where he is staying with a friend."
- Booked by the pipeline for Fri 10/9 1:00 PM with Joshua. **The booking was kept** (he confirmed, and canceling would repeat the Stefanie Holloway problem). The calendar event now says ALREADY INTERVIEWED BY PRESTON and includes Preston's note and both numbers: 641-680-0560 (booked) and 240-940-3176 (the number he gave Preston on 9/16).

## Audit of every open or upcoming candidate (Indeed Activity & notes, every application on the account)
| Candidate | Finding | Action |
|---|---|---|
| Caitlin Overbey (Wboro) | Preston interviewed 9/17 (20 yrs customer service, not big on sales pushing, wants Saturdays for daughter's cheer, $16+, 2 weeks). **Marked Rejected 9/18.** | Do not book. This answers Joshua's open "reject vs. book" question. No further contact. |
| Nikki Sprouse (Hburg) | Note 9/17 "No answer", **marked Rejected 9/17** (and on an earlier application 5/1). Re-contacted 10/7. | Do not book. No further contact. |
| Rita Allen (Wboro) | Earlier application marked Rejected 6/24. Current 8/14 application has no notes. | Flagged to Joshua; hold booking until he says. |
| Kylee Bryant (Hburg) | Earlier applications marked Rejected 3/11 and 4/24. Current 7/2 application has no notes. | Flagged to Joshua; hold booking until he says. |
| Trenayce Bridges | Preston said 10/7 he already interviewed her; her 10/8 slot has passed. | No action. |
| Glen Way | Note 10/5 "No answer" only. Not interviewed. | Clean, continue. |
| Stefanie Holloway, Alaska Foote, Logan Burnett, Derek Sandlin, Patrick Franklin, Darrion Corbin, Hannah Bartel, Brad Andrews, Sam Rainey, Celeste Williams | No notes, no rejections. | Clean, continue. |

## Permanent fix
`vp-hiring-pipeline` and `hiring-contact-check` now require a Preston-notes gate before any message, nudge, reschedule or booking: open every application the person has on the account, read Activity & notes, and stop if Preston interviewed or rejected them. Interviewed → no phone screen; the notes go to Joshua and #employee-prospects. Rejected → no contact.

## Preston-handled list (add to the exclusion list)
Desmond Chick (interviewed 9/17, booked with Joshua 10/9 1 PM as a follow-up), Caitlin Overbey (rejected 9/18), Nikki Sprouse (rejected 9/17), Trenayce Bridges (interviewed), plus the 10/1 positive-note list: Anthony Servin Reynoso, Hunter Marks, Heather Hinkle, Ingrid Jimenez, ashleigh leggio, Christopher Crammer.
