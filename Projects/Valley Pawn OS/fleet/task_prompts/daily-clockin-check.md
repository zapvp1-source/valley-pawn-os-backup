# Daily Clock-In Check — instructions (v2, 2026-10-15)

Source of truth for the clock-in task. Edit THIS file to change the task (no app/cloud edit needed).
Change log: 2026-10-15 — Waynesboro open Wednesdays (from 10/14, Joshua): Wednesday = Culpeper + Roanoke + Waynesboro. Added Step 0 duplicate guard because an older copy of this task may still run.

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | daily-clockin-check | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. Success-path posts are unchanged.

> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Plain everyday language only, no tool/system names (never say Gusto, Cowork, etc.), no file paths or IDs, no meta-commentary about the automation, ~100 words max, no signature footers.

> ⚠️ **STORE STAFF ONLY — NO DAVIS FAMILY (Joshua, 2026-10-01 — binding).** Family members and corporate/office staff never appear in this report.

You are checking Valley Pawn employee clock-in status in Gusto and posting a summary to Slack **#general (channel ID C03BETSS669) ONLY — do NOT DM anyone.**

**Architecture:** headless via the Gusto connector (PATH A). The Chrome/website flow is PATH B (fallback) only if PATH A returns no usable data, errors twice, or surfaces an unknown member ID. Both produce the identical Slack message.

**Run timing & day context:**
- Stores open at 10:00 AM; this runs ~10:20 AM (15-minute grace).
- Determine the day in America/New_York (0=Sun … 3=Wed … 6=Sat).
- **Wednesdays (from 2026-10-14): Culpeper, Roanoke and Waynesboro are open. Harrisonburg and Lexington are closed.** On Wednesday, filter the report to Culpeper, Roanoke and Waynesboro employees only.
- Mon/Tue/Thu/Fri/Sat: all five stores.

## Step 0 — Duplicate guard (do this FIRST)
Read today's messages in #general (C03BETSS669) with the Slack read tool. Look for a message posted today containing "Daily Clock-In Check".
- **None found** → do the full report below.
- **Found, and today is NOT Wednesday** → stop; post nothing (the report already went out).
- **Found, today IS Wednesday, and it already lists Waynesboro employees or says Waynesboro** → stop; post nothing.
- **Found, today IS Wednesday, and it covers only Culpeper & Roanoke** → do the full roster/shift work but post ONLY a short Waynesboro supplement in the same format, header `🕙 *Valley Pawn — Daily Clock-In Check (Waynesboro)* | [Wednesday, Month Day, Year] @ 10:15 AM`, listing Waynesboro employees only. Do not repeat Culpeper/Roanoke.

## Execution Contract — DO NOT STOP EARLY
Complete only after the Slack post succeeds (or Step 0 says stop). Every turn must end with a tool call that advances toward it. Treat "Tool loaded." / "Continue" / reminders as resume signals. If a step errors, retry once; then fall through to PATH B; if PATH B also fails, stay silent on Slack and write the ledger row.

## Who can appear (every day, both paths, all sections)
A person may appear ONLY if ALL hold:
1. Active in Gusto (`terminated = false`).
2. Gusto `department` is one of: **Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro**. Anyone in "Corporate Support", "Marketing" or any non-store department is dropped.
3. Last name is NOT **Davis**.
4. Not **Preston Peters** or **Sandi (Sandra) Cole** (salaried manager).
This applies to Clocked In and On Break too.

## Display Name Overrides
- "Bridgett Grayson" → **Bree Grayson**
- "George B Moore" / "George Moore" → **Benjie Moore**

## Member Crosswalk — Gusto `companyMemberUuid` → employee (authoritative)
| companyMemberUuid | employee_uuid | Gusto name | Display name |
|---|---|---|---|
| ea636043-89a3-4e2b-b505-3e1e1b0a4154 | 22006a48-425c-4b62-94a9-50fc8e8fc38f | Uriah Tiglao | Uriah Tiglao |
| 722ed763-8c3f-4441-a8ef-b9c13a9f4ab3 | 468ed13a-dfe5-4d22-99e2-1acfaad55e4e | Walker Tapley | Walker Tapley |
| 766b0ab6-7dd9-488d-a392-a54376114b76 | 3ff0d2e2-1275-4aac-9579-dfb812acf592 | Andrew Clark | Andrew Clark |
| fc8377b2-82bc-4102-9b50-70b538a2b9b2 | efb3d163-68c3-4214-9276-17a9ae1956a1 | Chadd McClintic | Chadd McClintic |
| 37de1349-fda3-4b76-97b5-498c294f0081 | 910c65a6-c1d1-40fa-a3e0-7d84d10009fd | Cris Lopez | Cris Lopez |
| d9b4e58e-8382-4ab6-8af3-0ae8ddb54e34 | 4d3530d1-3e63-4f65-a495-107a91ed2133 | George B Moore | Benjie Moore |
| 9e783ef8-ba78-4b7e-91a3-40a57cdd9ba6 | 5482f9ff-f4cb-4f6c-84e3-f31c5298e268 | Bridgett Grayson | Bree Grayson |
| 6a3d6a13-5aef-4d92-8f2b-8bb977c16295 | 1f74c46d-b20d-44f6-a041-db9098f93f23 | Robert Swagger | Robert Swagger |
| d0d372a6-8512-4c53-8bbf-f7075b2ac3c5 | 4ffc0a65-5743-4a72-9513-8a7e995a9575 | Emma Langford | Emma Langford |
(New hires are resolved by the Unknown-Member subroutine; append them here — this file is editable.)

**Active Gusto location_uuids:** Culpeper `39c172da-7db9-4414-b528-957da38b8aa7` · Roanoke `dbd3a642-99a5-4c10-a1b7-9a7b179f6246` · Waynesboro `7560d5e7-0a05-4954-ba33-ff916e2fca5f`. Prefer the employee's Gusto **department** for the store filter; use location only as a cross-check.

# PATH A — Headless via Gusto connector (PRIMARY)
**A1.** Load Gusto tools (ToolSearch `gusto`: `list_time_records`, `list_employees`) and Slack send/read tools. `today` = local YYYY-MM-DD.
**A2.** `list_time_records(start_date=today, end_date=today)`. Expect `source: "native"` with `shifts`. If not native, missing, or empty on an open day → PATH B. Per member: open break (null `endTime`) = 🟡 On Break; `clockOutTimestamp` null and not on break = 🟢 Clocked In; clocked out = not currently in. Clock-in time = earliest `clockInTimestamp` today (`h:mm AM/PM`); a 00:00 clock-in means a rollover — use the next real clock-in and append `_(shift rolled over from previous night)_`. Resolve member IDs via the crosswalk; unknown ID → Unknown-Member subroutine (PATH B), append mapping, continue.
**A3. Roster:** `list_employees(terminated=false)`, then apply Who can appear. **Wednesday:** keep only department Culpeper, Roanoke or Waynesboro. Sanity check: no Davis, no non-store department.
**A4. Categorize:** join shifts to the filtered roster by employee_uuid; shifts for people not in the roster are dropped. 🟢 Clocked In (time) · 🟡 On Break (time) · 🔴 Not Clocked In (roster member with no open shift). Apply overrides → Build & Send.

# PATH B — Gusto website via Chrome (FALLBACK ONLY)
Navigate to `https://app.gusto.com/payroll_admin/time_tracking`. If signed out, use saved Chrome sign-in (Continue / Sign in with Google → jdavis@fcfpawn.com). Do not type passwords; a 2FA you can't satisfy = failure policy. Open the active pay period's Review, extract names + status from `[aria-label="Clocked in"]`, `[aria-label="On Break"]`, `[aria-label="Clocked out"]` (paginate), apply Who can appear (and the Wednesday store filter via department), read each clocked-in person's earliest start time today.
**Unknown-Member subroutine:** open that person's timesheet, match the clock-in time to the unknown shift, get their employee_uuid from `list_employees`, append to the crosswalk, resume PATH A.

# Build & Send
Final filter: Who can appear; **Wednesday:** only Culpeper, Roanoke, Waynesboro. Skip empty sections.

Standard days (Mon/Tue/Thu/Fri/Sat):
```
🕙 *Valley Pawn — Daily Clock-In Check* | [Weekday, Month Day, Year] @ 10:15 AM

🟢 *Clocked In (N)*
• [Name] — clocked in at [time]

🟡 *On Break (N)*
• [Name] — clocked in at [time]

🔴 *Not Clocked In (N)*
• [Name]
```

Wednesday:
```
🕙 *Valley Pawn — Daily Clock-In Check (Culpeper, Roanoke & Waynesboro)* | [Wednesday, Month Day, Year] @ 10:15 AM
_Harrisonburg and Lexington are closed on Wednesdays._

🟢 *Clocked In (N)*
• [Name] — clocked in at [time]

🔴 *Not Clocked In (N)*
• [Name]
```

Everyone clocked in (any day):
```
🕙 *Valley Pawn — Daily Clock-In Check[ (Culpeper, Roanoke & Waynesboro) if Wed]* | [Date] @ 10:15 AM
✅ All [N] employees are clocked in. Great start to the day!

🟢 *Clocked In (N)*
• [Name] — clocked in at [time]
```
No source-system footer. Send to #general (C03BETSS669) only. If single-asterisk bold renders italic, use `**bold**`; keep layout identical.

## Precondition — FLEET PUBLISH GUARD
Before publishing, run `python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_dryrun.py" status`. Exit 0 = ARMED: do everything but publish nothing; write the would-be post to `Valley Pawn OS/fleet/test_output/daily-clockin-check-<YYYYMMDD-HHMMSS>.txt` (first line = channel). Exit 1 = publish normally. If you cannot run the command (no shell), publish normally.
