---
name: jewelry-freeze-test-compare
description: ONE-TIME 9:45 PM 2026-08-10 — compare tonight's freeze-window Bravo jewelry counts against tonight's Monday PM manager sheets (same period), and report the true per-category variance.
model: claude-sonnet-5
---

ONE-TIME TEST RUN — part 2 of 2. The companion task `jewelry-freeze-test-pull` fired at 8:30 PM tonight and pulled 5-store jewelry on-hand counts from Bravo inside the overnight freeze window. Your job is to compare those against tonight's manager sheets and report the TRUE variance.

WHY THIS IS THE FIRST VALID TEST:
Bravo's jewelry report is a live on-hand query with no as-of-date capability — it always returns the current moment. The manager's sheet is a physical count at 6 PM close. Those only line up if the Bravo pull happens while nothing is moving. All stores close at 6 PM and reopen at 10 AM, so tonight's 8:30 PM pull and tonight's 6 PM manager count describe the SAME frozen state. Every prior comparison mixed time periods (a Monday-morning live pull vs a Friday sheet) and was therefore meaningless. Treat tonight's result as the first real signal.

STEP 1 — Load the Bravo side.
Read all 5 CSVs (osascript shell; the Write/Read tools cannot reach this folder):
/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/2026-08-10_<STORE>_jewelry-case-counts.csv for STORE in CUL, HAR, LEX, ROA, WAY.

Verify each file was modified TONIGHT after 8:30 PM (check mtime) — if any file is older, it is stale data from the earlier invalid morning run, NOT tonight's freeze-window pull. Also verify every row has status=ok.

HARD RULE — never post partial or unverified data. If any store is missing, stale, or has a non-ok row, do NOT compare and do NOT publish numbers. DM Joshua one plain line saying the test didn't complete and stop. All-or-nothing.

STEP 2 — Load the manager side.
Tonight's Monday 2026-08-10 PM sheets are in Slack #end-of-day (channel C03C7HV8L48), posted roughly 6:15-8:15 PM by the store managers (typically Sandi=Culpeper, Walker=Harrisonburg, Martin D.=Lexington, Benjie=Roanoke, Preston/Chadd=Waynesboro — but confirm from each sheet's printed header, do not assume).

These sheets are PHOTOGRAPHS of paper. Slack's API cannot read image pixels — you must use the Claude-in-Chrome browser tools and read them visually. Navigate to https://app.slack.com/client/T03BL4W1DCL/C03C7HV8L48 and zoom into each "JEWELRY DAILY COUNT" image. Use the PM COUNT column, and confirm the handwritten DATE on the sheet actually reads 8/10/26 — the handwritten date sometimes differs from the Slack post date, and some sheets contain several days stacked on one page. If you cannot find a legible Monday 8/10 sheet for a store, treat that store as missing per the all-or-nothing rule above.

STEP 3 — Compare, with the correct category mapping.
The manager sheet has 5 lines: RINGS, BRACELETS, NECKLACES, EARRINGS, PENDANTS.
Bravo reports 6 categories. The mapping is:
- Rings -> RINGS
- Bracelets -> BRACELETS
- Earrings -> EARRINGS
- Pendants -> PENDANTS
- **Chains + Necklaces summed -> NECKLACES** (Bravo splits what the sheet counts as one line; this was confirmed on 2026-08-09)

Build a per-store table: category, Bravo count, sheet count, variance. Note the store totals too.

STEP 4 — Interpret honestly.
Inside a true freeze window, a well-functioning process should be at or near zero variance. Small deltas of 1-3 are normal (a manager miscount, an item mid-repair). Call out anything larger as a real exception worth investigating.

Pay specific attention to ROANOKE PENDANTS. The earlier invalid comparison showed Bravo 88 vs sheet 149 — a 61-unit gap. That comparison was time-mismatched and cannot be trusted, which is exactly why tonight's test exists. If the gap largely closes tonight, the earlier number was a timing artifact and nothing is wrong at Roanoke. If a large gap persists inside the freeze window, it is a genuine physical-vs-system discrepancy at that store and needs real attention. Report which of those two it is, plainly, without overstating confidence either way.

STEP 5 — Report to Joshua only.
Send Joshua ONE Slack DM (channel D03BHQH5VGT). This is a loss-prevention audit — never post it to a shared channel, never to a store manager or employee. Plain everyday language, no jargon, no file paths, no system or tool names. Lead with the bottom line: whether the counts matched, and any store/category that genuinely looks off. Keep it short enough to read on a phone.

Also append a dated RUN RECORD to /Users/joshuadavis/Documents/Claude/Projects/Jewelry Count Reconciliation/STATUS.md capturing the full per-store table, the freeze-window methodology used, and the ROA Pendants conclusion — so the next session has the paper trail and knows whether the method is proven enough to wire into the live `jewelry-count-reconciliation` scheduled task. Do NOT modify that live task tonight (Rule #4, additive only — it stays on its existing sold-based flow until this method is proven across multiple runs).

Standard failure policy: if this run fails or cannot complete, send Joshua exactly ONE plain-language Slack DM saying tonight's jewelry count comparison did not complete. No technical detail in the DM; put it in your run output instead.