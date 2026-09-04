---
name: bald-rock-vrbo-rate-sync-recheck
description: Re-verify that the Nov/Dec 2026 Bald Rock holiday rates and minimum stays have synced from Guesty to VRBO
---

Re-verify VRBO rate/min-stay sync for 282 Bald Rock Road (Guesty listing "Mountain Luxury", VRBO property 4752473).

BACKGROUND — what happened on 2026-09-03. New seasonal rates were applied in the Guesty multi-calendar for the Bald Rock STR, replacing a flat $850 weekday / $1,250 weekend structure. Guesty values now set (Guesty base rates, before channel markup):
- Nov 5 – Dec 19, 2026 weekdays: $632
- Fri/Sat within that window (Nov 6-7, 13-14, 20-21, Dec 4-5, 11-12, 18-19): $867
- Thanksgiving Nov 23-29: $959, minimum 4 nights
- Christmas Dec 20-27: $1,090, minimum 5 nights
Nov 1-4 is an owner block called "Dad Trip" — DO NOT touch availability there or anywhere else. This task is verification only; do not change any rates unless explicitly told to below.

Channel markups observed 2026-09-03: Airbnb displays Guesty rate x 1.147. VRBO's effective markup appeared to be ~1.383 on shoulder dates.

WHAT WAS VERIFIED WORKING on 2026-09-03: Airbnb had fully picked up both the rates and the minimum stays. Confirmed via the public listing at airbnb.com/rooms/1454500305451091491 — Nov 9-11 (2 nights) $2,025 total; Nov 23-27 (4 nights) $4,975; a 2-night Thanksgiving (Nov 24-26) was correctly REJECTED; Dec 21-26 (5 nights) $6,830.

WHAT WAS NOT WORKING — the reason for this task: VRBO had picked up the shoulder rate but NOT the Thanksgiving or Christmas overrides, and NOT the minimum stays. Evidence: vrbo.com/4752473 with chkin=2026-11-24&chkout=2026-11-26 (a 2-night Thanksgiving stay) showed "Your dates are available" at $2,198 before taxes — identical to the Nov 9-11 shoulder dates — when the 4-night minimum should have blocked it. And chkin=2026-12-21&chkout=2026-12-26 showed $5,502 before taxes (~$1,010/night accommodation after backing out the $450 cleaning fee), far below the ~$1,508/night the new $1,090 Guesty Christmas rate should produce. Most likely cause is VRBO sync lag, since the holiday overrides were the last writes made.

WHAT TO DO NOW:
1. Check the three VRBO URLs below and record the "total before taxes" figure for each:
   - https://www.vrbo.com/4752473?chkin=2026-11-09&chkout=2026-11-11&adults=2  (shoulder, 2 nights)
   - https://www.vrbo.com/4752473?chkin=2026-11-24&chkout=2026-11-26&adults=2  (2-night Thanksgiving — SHOULD now be rejected/unavailable)
   - https://www.vrbo.com/4752473?chkin=2026-12-21&chkout=2026-12-26&adults=2  (Christmas, 5 nights)
   Back out the $450 cleaning fee from each total, divide by nights, to get the effective per-night accommodation rate.
2. Judge the result: sync is GOOD if the 2-night Thanksgiving stay is now unavailable AND the Christmas per-night accommodation rate is materially above the November shoulder rate. Sync is STILL BROKEN if a 2-night Thanksgiving is bookable or Christmas is priced at roughly the same per-night as November.
3. If still broken, open Guesty (app.guesty.com — direct email/password login as fullcirclepawn@gmail.com, let Chrome autofill; NEVER use "Sign in with Google", it hangs) and inspect the VRBO channel at Channels > Vrbo. Compare its sync scope against the Airbnb channel, which is set to sync "Everything". Report what differs. Do NOT change the channel configuration — VRBO is roughly 23% of this property's revenue and a bad config change could take the listing down. Investigate and report only.
4. Confirm the Guesty multi-calendar still holds the values listed above (they should be unchanged).

REPORT: send ONE plain-language Slack DM to Joshua at D03BHQH5VGT. No technical jargon, no error traces, no stack detail — say in plain terms whether VRBO now matches Airbnb on the holiday pricing and minimum stays, and if not, what the single next step is. Write the full technical detail to /Users/joshuadavis/Documents/Claude/Projects/Short Term Rental Optimization/vrbo-sync-recheck-2026-09-04.md instead. Also append a dated update line to the Bald Rock entry in /Users/joshuadavis/Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md.