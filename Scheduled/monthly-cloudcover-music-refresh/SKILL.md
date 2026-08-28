---
name: monthly-cloudcover-music-refresh
description: Monthly (1st of month, 9 AM) — rotate Pandora CloudCover's background music station across all 5 Valley Pawn store zones to the next station in a pre-approved clean/neutral rotation, so the in-store playlist doesn't go stale. Never touches Message Presets/Schedules (commercials stay untouched).
model: claude-sonnet-5
---

Monthly music refresh for Valley Pawn's Pandora CloudCover background music system. Run on the 1st of every month.

## Context
Joshua wants the in-store background music refreshed monthly so stores don't get bored of the same rotation, but the music must stay strictly neutral: NO rap, NO R&B, NO soul, and NO explicit/cussing lyrics — inoffensive to any customer. This task rotates all 5 real store zones to the next station in a pre-approved list. It does NOT touch messaging/commercials (Message Presets, Message Schedules, Message Library) — those are a separate system and must be left completely alone every run.

Load `enterprise-map` and `vp-operating-rules` first per standing instructions (Domain 1 / Valley Pawn). This task is additive and independent of the existing `daily-cloudcover-check` task — do not modify that task or its file.

## The approved rotation (verified clean 2026-08-26 — do not add stations outside this list without first checking them against the exclusion criteria below)
1. Family Friendly (content rating G — "Clean Lyrics for All Ages")
2. Family Friendly Top 40s (content rating G — "Clean Today's Top 40s")
3. Easy Listening
4. Lobby Acoustic Popular

Exclusion criteria for any future additions to this list: no Hip Hop, no R&B/Soul genre tags, no explicit/PG-13+ content rating, nothing that would need a second listen to confirm it's clean. When in doubt, leave it off the list and flag it in the STATE file's notes for Joshua to review — don't guess.

## State tracking
State file: `/Users/joshuadavis/Documents/Claude/Scheduled/monthly-cloudcover-music-refresh/state.json`

Format: `{"lastIndex": 0, "lastStation": "Family Friendly", "lastRunDate": "2026-08-26"}`

On each run: read the state file (if missing, treat lastIndex as -1, i.e. start the rotation at index 0). Compute `nextIndex = (lastIndex + 1) % 4` using the 4-item list above (0-indexed). That is this month's station. After a successful zone update, write the new state file with the updated lastIndex, lastStation, and today's date.

## Steps

**Step 1 — Navigate and log in.** Navigate to `https://tune.cloudcovermusic.com/#/admin/zones` in Chrome. If redirected to `/login`, use the same self-healing autofill login flow documented in the `daily-cloudcover-check` scheduled task (read that task's SKILL.md at `/Users/joshuadavis/Documents/Claude/Scheduled/daily-cloudcover-check/SKILL.md` for the exact coordinate-click + Angular event-dispatch technique — do not type credentials manually, Chrome autofill handles it). If login fails after following that flow, DM Joshua per the Session Expired Fallback pattern in that same file (DM user U03BB52MDSA) and stop — do not proceed further.

**Step 2 — Select the 5 real store zones.** On the Zones table, check the checkboxes for exactly these 5 rows: Harrisonburg, Lexington1, Roanoke1, SandiPepper, Waynesboro1. Do NOT select the `zapvp1` row (that's an internal test/admin zone, not a real store).

**Step 3 — Change the station.** Click the "Music" dropdown button in the toolbar above the table. Click the search input inside the dropdown, type the target station name (from the rotation list, computed above), and click the matching result under "--- Stations ---". Wait 2 seconds, then reload the Zones page and verify the Music column now shows the new station name for all 5 real store zones before proceeding. If any zone still shows the old station after reload, retry the selection once; if it still fails, note it in the Slack summary as a partial failure for that store specifically (no technical jargon — just "the new station didn't take at [Store]").

**Step 4 — Do not touch messaging.** Do not open, click, or modify anything under Music Library, Message Presets, or Message Schedules. The in-store commercial announcements are a separate, already-configured rotation and must keep running exactly as-is — Joshua has explicitly said the commercials must stay in rotation every time the music changes.

**Step 5 — Update state file.** Write the new state.json as described above.

**Step 6 — Post to Slack.** Post ONE message to `#general` (channel `C03BETSS669`) following the Field Communication Standard (`/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md` — plain everyday language, no tool names, no jargon, ~100 words max, lead with the takeaway). Something like:

```
🎵 This month's in-store music has been refreshed at all 5 stores — new station: [Station Name]. Same easy-listening, family-friendly music as always, just a fresh mix so it doesn't get stale. All the usual store announcements are still playing as normal.
```

Adjust the station's plain-language description to match whichever one is live (e.g. "Family Friendly" → "family-friendly hits", "Easy Listening" → "easy listening", "Lobby Acoustic Popular" → "acoustic covers").

## Failure handling
Per the Failure Alert Policy: if this run fails or can't complete, send Joshua ONE plain-language Slack DM (channel D03BHQH5VGT): "⚠️ Scheduled task "monthly-cloudcover-music-refresh" did not complete — [date]." Nothing technical in that DM. Never post failure/error details to #general or any team channel. Do not idle or stop early — retry once on any transient error, then fall through to the DM fallback.

## Do not
- Do not modify `daily-cloudcover-check` or any other existing scheduled task.
- Do not add stations to the rotation list without documenting why they pass the exclusion criteria.
- Do not touch Message Presets, Message Schedules, or Message Library.
- Do not select the `zapvp1` zone.