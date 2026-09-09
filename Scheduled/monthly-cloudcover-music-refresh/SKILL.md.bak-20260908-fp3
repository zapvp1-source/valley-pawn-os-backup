---
name: monthly-cloudcover-music-refresh
description: Monthly (1st of month, 9 AM) — rotate Pandora CloudCover's background music station across all 5 Valley Pawn store zones to the next station in a pre-approved clean/neutral rotation, so the in-store playlist doesn't go stale. Never touches Message Presets/Schedules (commercials stay untouched).
model: claude-sonnet-5
---

Monthly music refresh for Valley Pawn's Pandora CloudCover background music system. Run on the 1st of every month.

## Context
Joshua wants the in-store background music refreshed monthly so stores don't get bored of the same rotation, but the music must stay strictly neutral: NO rap, NO R&B, NO soul, and NO explicit/cussing lyrics — inoffensive to any customer. It must ALSO be upbeat and energetic — on 2026-09-02 the store teams complained the music was "dull" after the rotation landed on Easy Listening (Burt Bacharach / Guy Lombardo territory), and Joshua had it fixed same day. Low-energy stations (Easy Listening, acoustic/lobby/spa stations, instrumental-only, jazz standards) are now BANNED from this rotation. The bar: clean AND energetic. This task rotates all 5 real store zones to the next station in the pre-approved list below. It does NOT touch messaging/commercials (Message Presets, Message Schedules, Message Library) — those are a separate system and must be left completely alone every run.

Load `enterprise-map` and `vp-operating-rules` first per standing instructions (Domain 1 / Valley Pawn). This task is additive and independent of the existing `daily-cloudcover-check` task — do not modify that task or its file.

## The approved rotation (revised 2026-09-02 after the "dull music" complaint — do not add stations outside this list without checking them against the criteria below)
1. Family Friendly Top 40s (content rating G — "Clean Today's Top 40s" — upbeat current pop)
2. '90s Country (upbeat 90s country hits)
3. 2010s Country (modern country hits)
4. Family Friendly (content rating G — "Clean Lyrics for All Ages")

Criteria for any future additions: no Hip Hop, no R&B/Soul genre tags, no explicit/PG-13+ content rating, AND genuinely upbeat — nothing sleepy, instrumental-only, acoustic-lounge, or "easy listening" adjacent. When in doubt, leave it off and note it in the state file for Joshua to review — don't guess.

## State tracking
State file: `/Users/joshuadavis/Documents/Claude/Scheduled/monthly-cloudcover-music-refresh/state.json`

Format: `{"lastIndex": 0, "lastStation": "Family Friendly Top 40s", "lastRunDate": "2026-09-02"}`

On each run: read the state file (if missing, treat lastIndex as -1, i.e. start at index 0). Compute `nextIndex = (lastIndex + 1) % 4` against the 4-item list above (0-indexed). That is this month's station. After a successful zone update, write the new state file with the updated lastIndex, lastStation, and today's date. (If the Scheduled folder isn't writable via the Write tool, use the `mcp__Control_your_Mac__osascript` tool with a `do shell script "cat > ... << 'EOF' ..."` heredoc — that path always works.)

## Steps

**Step 1 — Navigate and log in.** Navigate to `https://tune.cloudcovermusic.com/#/admin/zones` in Chrome. If redirected to `/login`, use the same self-healing autofill login flow documented in the `daily-cloudcover-check` scheduled task (read that task's SKILL.md at `/Users/joshuadavis/Documents/Claude/Scheduled/daily-cloudcover-check/SKILL.md` for the exact coordinate-click + Angular event-dispatch technique — do not type credentials manually, Chrome autofill handles it). If login fails after following that flow, DM Joshua per the Session Expired Fallback pattern in that same file (DM user U03BB52MDSA) and stop — do not proceed further.

**Step 2 — Select the 5 real store zones.** On the Zones table, check the checkboxes for exactly these 5 rows: Harrisonburg, Lexington1, Roanoke1, SandiPepper, Waynesboro1. Do NOT select the `zapvp1` row (internal test/admin zone, not a real store). Verify the count reads "5 selected" before proceeding — if it reads 6, the zapvp1 row got included; deselect it.

**Step 3 — Change the station.** Click the "Music" dropdown button in the toolbar above the table. Click the search input inside the dropdown, type the target station name (from the rotation list, computed above), and click the matching result under "--- Stations ---". CAUTION: the search input sometimes retains stale characters — if "No results found" appears for a name you know exists, clear the field with the × and retype. Wait 2 seconds, then reload the Zones page and verify the Music column shows the new station for all 5 real store zones. If any zone still shows the old station after reload, retry the selection once; if it still fails, note it in the Slack summary as "the new station didn't take at [Store]" (no technical jargon).

**Step 4 — Do not touch messaging.** Do not open, click, or modify anything under Message Library, Message Presets, or Message Schedules. The in-store commercial announcements are a separate, already-configured rotation and must keep running exactly as-is.

**Step 5 — Update state file.**

**Step 6 — Post to Slack.** Post ONE message to `#general` (channel `C03BETSS669`) following the Field Communication Standard (`/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md` — plain everyday language, no tool/system names, ~100 words max, lead with the takeaway):

```
🎵 This month's in-store music has been switched up at all 5 stores — now playing: [plain-language description]. Fresh, upbeat, and family-friendly as always. All the usual store announcements are still playing as normal.
```

Plain-language descriptions: "Family Friendly Top 40s" → "today's top 40 hits, clean versions"; "'90s Country" → "90s country hits"; "2010s Country" → "2010s country hits"; "Family Friendly" → "upbeat family-friendly hits".

## Failure handling
Per the Failure Alert Policy: if this run fails or can't complete, send Joshua ONE plain-language Slack DM (channel D03BHQH5VGT): "⚠️ Scheduled task "monthly-cloudcover-music-refresh" did not complete — [date]." Nothing technical in that DM. Never post failure/error details to #general or any team channel. Retry once on any transient error, then fall through to the DM fallback.

## Do not
- Do not modify `daily-cloudcover-check` or any other existing scheduled task.
- Do not add stations to the rotation without documenting why they pass BOTH the clean criteria and the upbeat criteria.
- Do not ever select Easy Listening, Lobby Acoustic, Spa, or any low-energy/instrumental station — banned 2026-09-02 after store complaints.
- Do not touch Message Presets, Message Schedules, or Message Library.
- Do not select the `zapvp1` zone.