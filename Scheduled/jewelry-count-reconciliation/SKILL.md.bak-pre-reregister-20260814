---
name: jewelry-count-reconciliation
description: Daily jewelry count reconciliation — pulls sold-jewelry counts from Bravo, reads manager AM/PM count sheets from #end-of-day, compares, posts results to #jewlery-counts
model: claude-sonnet-5
---

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access. That conclusion is false** and is the single most common cause of a false failure on this platform. If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.

> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. **TIER-1 FIX + WORST-OFFENDER REWRITE (2026-08-03): #jewlery-counts had become a build log — raw error strings, file paths, .md filenames, and "watchdog"/"Bravo pull"/"CSV" language were posted directly to a store-facing channel. Section 5 below is rewritten: a real reconciliation failure now DMs Joshua ONLY, in plain language, with zero technical detail — the channel either gets the clean per-store reconciliation table, or nothing at all that day.** If anything later in this file conflicts with this standard, this standard wins.


# Daily Jewelry Count Reconciliation (run ~7:45 PM ET)

Business date = today (America/New_York). Compare Bravo sold-jewelry vs the managers' handwritten AM/PM case counts, post to #jewlery-counts (C0BM9NHGTT4). Proven end-to-end 2026-07-31 — follow exactly; do not improvise.

## 0. STORE-HOURS GATE - CHECK THIS FIRST, BEFORE ANYTHING ELSE

Valley Pawn stores are CLOSED on some days. A closed store has zero sales and no manager on
site to count, so there is nothing to reconcile and the report correctly returns an
empty grid. Running anyway produces a guaranteed false alarm - exactly what happened on
Sunday 2026-08-02 (all 5 stores reported "failed"; nothing was actually wrong).

Store hours (source: valley-pawn-context skill):
- Culpeper (CUL): Mon-Sat open. CLOSED SUNDAY.
- Harrisonburg, Waynesboro, Lexington, Roanoke: Mon, Tue, Thu, Fri, Sat open.
  CLOSED WEDNESDAY AND SUNDAY.

Determine today's weekday in America/New_York, then:
- SUNDAY -> every store closed. Do NOT pull Bravo. Do NOT read count sheets. Post NOTHING to
  Slack. End the run silently. The cloud watchdog also skips Sunday, so no alarm fires.
- WEDNESDAY -> run the full protocol for CUL ONLY (trigger stores array = ["CUL"]). Read only
  Culpeper's sheet. Post a normal report covering just CUL plus the footer line:
  "Wed - only Culpeper is open; other stores closed."
- ANY OTHER DAY -> run the full 5-store protocol.
- HOLIDAY / UNEXPECTED CLOSURE: if a store posted no EOD sheet AND its Bravo pull returned an
  empty grid on a normally-open day, report that store internally as "no data - store may have
  been closed" (log/DM only) rather than as a failure, and do not retry its pull.

## 1. Context first
Read the READ-FIRST INDEX (top ~60 lines) of `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/BRAVO_KNOWN_ISSUES.md`. Respect SOLVED / TRIED-AND-FAILED. Method reference: `/Users/joshuadavis/Documents/Claude/Projects/Jewelry Count Reconciliation/jewelry_reconciliation_comparison.py` and STATUS.md.

## 2. Bravo pull
- Confirm no unclaimed .json in `.../Bravo Data Extraction/triggers/` (top level only).
- Write `triggers/jewelry-count-recon-<YYYY-MM-DD>-auto.json` (unique id; append -b/-c if reused):
  {"id":"<id>","requested_at":"<now ISO -0400>","reports":[{"name":"jewelry-count-audit","stores":<ONLY the stores open today, per section 0>,"date":"<date>"}]}
- Poll `results/<id>.result.json` every 30s, up to 20 min (strip UTF-8 BOM). 5 cells, ~2 min each.
- CSVs land at `output/<date>_to_<date>_<STORE>_jewelry-count-audit.csv`. They contain ALL sold items (tools, guns, games) — not just jewelry. Never treat row count as jewelry count.

## 3. Count sheets (vision pass)
Managers post sheet photos to #end-of-day (C03C7HV8L48) ~6:00-7:15 PM ET. Using Chrome (claude-in-chrome; if screenshots return 0x0 viewport, activate/resize Chrome via osascript first), open https://app.slack.com/client/T03BL4W1DCL/C03C7HV8L48 and for each store open the jewelry count photo (AM COUNT / PM COUNT columns: Rings, Bracelets, Necklaces, Earrings, Pendants). Zoom the block dated with the business date; read AM and PM per category.
- SUM-VERIFY every column against its written total; re-zoom if it does not add up.
- Identify store from the EOD summary sheet header ("END OF DAY: <STORE>"), NOT the poster.
  Poster map (verify vs headers): Bree/Bree Grayson=CUL, Walker Tapley=HAR, Uriah=LEX, Benjie Moore=ROA, Martin D./Martin Dowden=WAY, Sandi Cole=CUL (historic), Chadd=WAY (historic).
- Sheet date != business date -> FLAG internally (log/DM), never silently correct, and do not post the discrepancy detail to the channel — only the plain reconciliation line (see section 5).
- Store not posted yet -> wait 30 min once, then proceed marking it "no sheet posted" internally.

## 4. Compute (per store)
Bucket each CSV row via jewelry_reconciliation_comparison.py rules: Category must be in the canonical JEWELRY_CATEGORIES set; then exclude scrap/bullion/wristwatch/pocket watch/watch band/brooch/misc and bare "Diamond"; then bracelet/bangle->Bracelets, earring->Earrings (BEFORE ring), ring/wedding band/solitaire->Rings, necklace/chain->Necklaces, pendant/charm->Pendants.
sold = bucket sum. net = AM_total - PM_total. diff = net - sold. FLAG if |diff| > 5 or date mismatch.

## 5. Post to #jewlery-counts (C0BM9NHGTT4) — REWRITTEN 2026-08-03 per Field Communication Standard

This channel only ever sees ONE of two things: a clean plain-language reconciliation summary, or nothing at all that day. It NEVER sees a technical failure report, an error string, a file path, or a "watchdog" mention.

If the Bravo pull and the count-sheet read both succeeded for all stores being checked today: post a short summary, one line per store —

```
Jewelry Count Check — <date>

✅ <Store>: counts match
⚠️ <Store>: off by <N> pieces — <one plain-English reason, e.g. "likely new buys coming in" or "worth a quick manager check">
```

Keep it to the stores actually checked today (5, or just Culpeper on Wednesday). No dollar figures, no "Bravo sold / AM -> PM / net / diff" breakdown, no mention of the underlying report or file names.

If the Bravo pull failed, or the count-sheet read could not be completed, for ANY store being checked today: **do not post anything to #jewlery-counts.** Instead, DM Joshua (U03BB59EM9GR... use U03BB52MDSA) ONE plain line: "⚠️ Jewelry count check for <date> didn't complete — needs a look." Put all technical detail (which store, what error, retry attempts) in STATUS.md (section 6) only, never in the DM and never in the channel.

## 6. Record
Append run record (date, table, flags, any failure detail) to `.../Jewelry Count Reconciliation/STATUS.md`. This is where all technical detail belongs — retry attempts, error strings, which pipeline step failed.

## Failure rules
An empty grid on an OPEN day is a real failure (this report returns ALL sold items, so 0 rows means the report did not run). An empty grid on a CLOSED day is correct - section 0 should have prevented that pull entirely. Bravo pull fails -> retry ONCE with fresh id; never force-kill anything; never edit lib/ or reports/ files (Rule #4, additive only). On any unresolved failure, follow Section 5's failure path exactly: DM Joshua one plain line, record full detail in STATUS.md, post nothing to the channel. A cloud watchdog checks the channel at 9:30 PM ET and DMs Joshua (not the channel) if nothing posted.