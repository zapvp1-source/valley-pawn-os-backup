---
name: chekkit-weekly-review-requests
description: Every Tuesday at 4:40 PM — Pull weekly Chekkit Inactives customer data from Bravo POS for all 5 Valley Pawn stores via the Bravo Data Extraction pipeline, send Chekkit review-request campaigns (with Joshua as confirmation recipient) and post per-store counts to #chekkit-updates, then import the email addresses into Brevo's master list tagged "monthly" and post per-store email counts to #email-campaigns. No Parallels grant required.
---

Run the weekly Chekkit review-request campaign across all 5 Valley Pawn stores AND import the email addresses from the same dataset into Brevo. End-to-end, autonomous.

Apply Joshua's working-style rules from the `valley-pawn-context` skill: do the work yourself, never ask Joshua to log in, never ask permission to proceed, use saved Chrome passwords. Read `valley-pawn-context` for store list, brand rules, and team info.

⚠️ **CRITICAL — DO NOT use the Write tool for any file in /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/.** That folder is OUTSIDE this task's sandbox. Use `mcp__Control_your_Mac__osascript` `do shell script` for all filesystem touches against that folder. Same pattern as `daily-funds-verification` SKILL.

═══════════════════════════════════════════════
PHASE 1 — Get customer data via the pipeline (or fall back to the Monday stash)
═══════════════════════════════════════════════

**Step 1A — Check for pre-collected CSVs from monday-bravo-combined-run (preferred)**

The Monday combined run stashes Chekkit Inactives CSVs at:

`/Users/joshuadavis/Documents/Claude/Scheduled/_shared-bravo-data/{YYYY-MM-DD}/chekkit-inactives/{STORE}.csv`

Check for the latest stash via osascript:

```applescript
do shell script "ls -1 /Users/joshuadavis/Documents/Claude/Scheduled/_shared-bravo-data/ 2>/dev/null | sort -r | head -1"
```

If the most recent dated folder is within the last 48 hours and contains CSVs for all 5 stores (CUL.csv, HAR.csv, LEX.csv, ROA.csv, WAY.csv) with First Name, Last Name, Phone, Email columns and at least 1 data row each — load these as Phase 1 output and skip Step 1B.

**Step 1B — Pipeline pull (the new default for Tuesday standalone runs)**

Drop ONE trigger that fetches `chekkit-inactives` for all 5 stores via osascript. The pipeline lives at `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`.

Generate trigger ID `chekkit-weekly-YYYY-MM-DDTHH-MM-SS`. Then:

```applescript
set triggerId to "chekkit-weekly-2026-05-12T16-40-00"
set triggerJson to "{\"id\":\"" & triggerId & "\",\"requested_at\":\"2026-05-12T16:40:00-04:00\",\"reports\":[{\"name\":\"chekkit-inactives\",\"stores\":[\"CUL\",\"HAR\",\"LEX\",\"ROA\",\"WAY\"],\"date\":\"2026-05-12\"}]}"
set triggerPath to "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/" & triggerId & ".json"
do shell script "echo " & quoted form of triggerJson & " > " & quoted form of triggerPath
```

Poll `results/<id>.result.json` every 30 seconds via osascript `test -f`. Timeout 15 minutes (30 polls).

Read the result JSON, parse `cells[]`. For each `status="success"`, read the CSV via:

```applescript
do shell script "cat '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/2026-05-12_CUL_chekkit-inactives.csv'"
```

The CSV columns are: `first_name, last_name, phone, email, last_visit` (last_visit may be blank on the pipeline cell's MVP). Load each row.

If a cell's `status != "success"`, mark that store as failed and proceed without it. If ALL 5 fail OR the result JSON never arrives, post to #chekkit-updates: "⚠️ Chekkit weekly task couldn't pull Bravo data (pipeline failure) — re-run monday-bravo-combined-run or trigger manually." and stop.

═══════════════════════════════════════════════
PHASE 2 — Clean the data
═══════════════════════════════════════════════
Apply the same rules as prior weeks:
- Drop any row where the Email field contains "DNC" / "Do Not Contact" (any casing).
- Drop any row whose phone is invalid: bad area codes (e.g., 826), fewer than 10 digits, all zeros, or obvious junk.
- Normalize phone to 10-digit format for Chekkit.
- Keep a per-store cleanup log (which rows were dropped and why).

═══════════════════════════════════════════════
PHASE 3 — Chekkit review-request campaigns (all 5 stores)
═══════════════════════════════════════════════
For each store, in Chrome via the Claude-in-Chrome MCP:
1. Open Chekkit and switch to that store's profile.
2. Create New Campaign and upload the cleaned phone list.
3. Add Joshua Davis (`804-930-4221`) as a confirmation recipient on every campaign.
4. Send the campaign. Capture: total customers sent, send timestamp.

═══════════════════════════════════════════════
PHASE 4 — Brevo email import
═══════════════════════════════════════════════
1. From the cleaned per-store data, collect every row with a valid, non-blank email. Skip DNC/blank.
2. Track per-store counts for the #email-campaigns post.
3. Build a single combined list across all 5 stores: First Name, Last Name, Email, Store (city) tag.
4. Deduplicate by email (case-insensitive). Note multi-store overlaps for the final count.
5. Open Brevo at `https://app.brevo.com/` in Chrome (saved password).
6. Navigate to Contacts → the master list used for weekly/monthly Valley Pawn campaigns. Do NOT create a new list.
7. Import deduplicated contacts. Map First Name, Last Name, Email correctly.
8. Apply tag **"monthly"** to all imported contacts.
9. Capture: total attempted, new contacts added (overall + per store).

═══════════════════════════════════════════════
PHASE 5 — Slack summaries (TWO posts)
═══════════════════════════════════════════════
Send both posts directly — do NOT save as drafts.

**Post A → `#chekkit-updates` (`C0B0FQZ4FS8`)**:
```
Weekly Chekkit Review Invites
• Culpeper: <n>
• Harrisonburg: <n>
• Lexington: <n>
• Roanoke: <n>
• Waynesboro: <n>
Total messages: <sum>
```

**Post B → `#email-campaigns` (`C0APR5WUL2Z`)**:
```
Weekly Email Upload to Brevo (tag: monthly)
• Culpeper: <emails_uploaded>
• Harrisonburg: <emails_uploaded>
• Lexington: <emails_uploaded>
• Roanoke: <emails_uploaded>
• Waynesboro: <emails_uploaded>
Total new emails added: <count>
```

For Post B, per-store numbers are emails uploaded from that store's data BEFORE dedup. Total = Brevo's confirmed-new count post-dedup.

═══════════════════════════════════════════════
Notes & rules
═══════════════════════════════════════════════
- Never use the legacy "Dixie Pawn" name — Harrisonburg is Valley Pawn.
- Never ask Joshua to log in or click anything. Saved Chrome passwords work for Chekkit and Brevo.
- If a Brevo row is rejected, skip it and tally for the #email-campaigns footer.
- The phone side is unchanged — the Brevo step is additive. If Phase 4 fails, still complete Phases 1–3 and post Post A; then post a single line to #email-campaigns saying Brevo upload failed.

═══════════════════════════════════════════════
Background — why this changed (2026-05-12)
═══════════════════════════════════════════════

Before 2026-05-12 this task pulled Chekkit Inactives by driving Bravo via Parallels + computer-use. The Bravo Data Extraction pipeline now produces the same data as a CSV per store on demand. The pipeline cell uses a UIA grid walk (`WriteChekkitGridToCsv` in `reports/ChekkitInactives.ahk`) since the Bravo Customer list view doesn't expose Export under Layouts — the original SKILL's "manual transcription" Phase 1 path is now automated.
