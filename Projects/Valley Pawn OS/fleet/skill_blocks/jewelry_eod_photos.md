# PM COUNT SHEETS — READ THEM FROM DISK (added 2026-09-29)

On 9/28 this task found every manager's count-sheet photo in #end-of-day but could not open any of
them (the Slack connector returns file metadata only). A native agent (`com.valleypawn.eod-photo-fetch`,
Mon–Sat 20:15) now downloads each night's #end-of-day images to:

`/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/eod_photos/<YYYY-MM-DD>/`
with `index.json` listing each file, who posted it, when, and the message text.

Read the images with the Read tool (it displays images) — this is the primary way to get the Counted
figures. Match a photo to a store by the poster (store roster) and the message text. Only if the folder
or a store's photo is missing, fall back to the Slack connector. A photo that is present but illegible
or does not add up is an EMPLOYEE issue (post the completed stores, DM that manager) — never a reason
to hold the whole post.
