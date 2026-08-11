---
name: vp-weekly-spot-price-update
description: Daily 7am update of Valley Pawn metals spot prices in HFCM snippet
model: claude-haiku-4-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.



> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

Run the daily Valley Pawn spot-price update.

1. Fetch current gold spot price from kitco.com (https://www.kitco.com/charts/gold) or apmex.com — look for the live USD/oz number
2. Fetch current silver spot price from the same source
3. Update the HFCM snippet "Valley Pawn Spot Prices" (HFCM ID 2) on thevalleypawn.com/wp-admin so that:
   - `window.VP_GOLD_SPOT = <new gold price>`
   - `window.VP_SILVER_SPOT = <new silver price>`
4. After updating, visit https://thevalleypawn.com/sell-gold-culpeper/ and verify in the JS console that `window.VP_GOLD_SPOT` returns the new value
5. Post a brief confirmation in Joshua's Slack DM (or post to #marketing if that channel exists): "Spot prices updated: gold $X,XXX/oz, silver $XX/oz — calculators are current."

If the price moved more than 3% from the previous day, flag it in the confirmation message so Joshua knows the offer amounts shifted meaningfully today.

<!-- migrated to working model 2026-06-15 -->