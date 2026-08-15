---
name: vp-weekly-spot-price-update
description: Daily 7am update of Valley Pawn metals spot prices in HFCM snippet
model: claude-haiku-4-5
---

---
name: vp-weekly-spot-price-update
description: Daily metals spot price update — writes the canonical spot_prices.json (used by intake valuation) and updates the website calculator snippet.
model: claude-haiku-4-5
---

> ⚠️ **FAILURE ALERT POLICY (v3 — corrected 2026-08-14, binding).** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "vp-weekly-spot-price-update" did not complete — <date>. Nothing technical in the DM. Put all technical detail in the run log for the next session. Joshua's DM is the ONLY place a failure may be mentioned — never a team channel, store manager, or employee, including Preston, in any medium.
>
> **This replaces a contradiction that caused a real, invisible outage.** The previous version of this file carried BOTH the standard "always DM Joshua on failure" banner AND a second block saying "DO NOT POST TO SLACK ON FAILURE — a failed run must stay completely silent." Those directly contradict, and the silent rule won: **no spot-price confirmation was posted between 2026-08-08 and 2026-08-14 while the task reported running daily** — six days of apparent failure that nobody could see. Meanwhile the intake valuation engine was running on hardcoded prices with silver ~4.4% high. Silence is not an acceptable failure mode for this task. Always send the one-line DM.

## Why this task matters more than it looks
The numbers this task produces feed **two** things:
1. The customer-facing gold/silver calculators on thevalleypawn.com (what customers are quoted).
2. **The daily intake valuation engine** (`Pawn Walks/intake_valuation_engine.py`) — melt is the single largest valuation source in the daily intake report. If spot is wrong, every jewelry and bullion valuation Joshua reviews is wrong, in silence.

Until 2026-08-14 this task only did #1 — it updated the website but nothing persisted the price where the valuation engine could read it, so that engine used hardcoded literals frozen since 2026-06-09. STEP 1 below closes that gap.

## STEP 1 — Write the canonical price file (DO THIS FIRST, it is the important half)
Run the deterministic fetcher via `mcp__Control_your_Mac__osascript` (load via ToolSearch `select:mcp__Control_your_Mac__osascript` if not present):

```
do shell script "/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fetch_spot_prices.py' 2>&1; echo EXIT:$?"
```

This script fetches XAU/XAG from a keyless JSON API, validates the result against plausibility bounds and a day-over-day move guard, and atomically writes `Valley Pawn OS/spot_prices.json`. It is deliberately conservative: if it cannot get a trustworthy number it KEEPS the last known good value and reports the rejection rather than writing garbage.

- **EXIT:0** → prices are current. Read the printed gold/silver values; use them in STEP 2 and STEP 3. If the output contains a `LARGE MOVE` or `NOTES:` line, include that plainly in the STEP 3 message.
- **EXIT:1** → no price could be refreshed. Do NOT scrape kitco by hand as a workaround and do NOT invent a number. Send the failure DM per the policy above and stop. A stale file with a known timestamp is safe; a hand-typed guess is not — the valuation engine will treat whatever is in that file as truth.

Do not fetch prices by reading a webpage with the browser. That was the old method and it is not reproducible — the script is the source of truth now.

## STEP 2 — Update the website calculator snippet
Using the exact values from STEP 1, update the HFCM snippet "Valley Pawn Spot Prices" (HFCM ID 2) at thevalleypawn.com/wp-admin so that:
- `window.VP_GOLD_SPOT = <gold>`
- `window.VP_SILVER_SPOT = <silver>`

Then verify: load https://thevalleypawn.com/sell-gold-culpeper/ and confirm in the JS console that `window.VP_GOLD_SPOT` returns the new value. If the site update fails but STEP 1 succeeded, that is a PARTIAL success — the valuation engine is correctly fed but customers see stale numbers. Say exactly that in the DM; don't report it as a clean run and don't report it as a total failure.

## STEP 3 — Confirm
Post a brief confirmation to Joshua's Slack DM (D03BHQH5VGT): "Spot prices updated: gold $X,XXX/oz, silver $XX/oz — calculators and intake valuations are current."

If either metal moved more than 3% from the previous day, add a plain line saying so, because offer amounts shifted meaningfully that day. The script prints the day-over-day percentage for you — use its number, don't recompute from memory.

If STEP 1 reported a `LARGE MOVE` (>25%), do not treat that as routine: say plainly that the price moved sharply and may be worth a look before relying on today's valuations.

## Notes for whoever maintains this
- Canonical file: `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/spot_prices.json`
- Fetcher + full rationale: `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fetch_spot_prices.py` (read its docstring)
- Read-only health check: `python3 fetch_spot_prices.py --check` → exit 0 = fresh, exit 1 = stale/missing
- The file keeps a rolling ~400-entry history, which is what any future work on premium calibration or "what did we think gold was worth on the day of that buy" should use.
- **Never hardcode a spot price anywhere.** That is the exact bug this task now exists to prevent.