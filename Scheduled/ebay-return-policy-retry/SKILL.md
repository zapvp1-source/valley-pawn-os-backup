---
name: ebay-return-policy-retry
description: One-shot retry of 9 eBay return-policy revisions blocked by open Best Offers during the 2026-08-22 online-store audit remediation.
model: claude-sonnet-5
---

One-shot cleanup task from the 2026-08-22 Valley Pawn online-store audit. Runs on Joshua's Mac.

BACKGROUND: On 2026-08-22 a remediation pass set 30-day returns across the eBay estate (Roanoke was on 14-day; 45 listings accepted no returns at all). 332 of 341 revisions succeeded and were verified live. 9 failed with eBay's transient error: "The return policy cannot be changed or removed if an auction-style listing has a bid or ends within 12 hours, or a fixed price listing has a pending Best Offer." Open Best Offers expire within ~48 hours, so these should now succeed.

STEP 0 — LOCAL ACCESS GATE. If `mcp__Control_your_Mac__osascript` is not loaded, load it first with ToolSearch query `select:mcp__Control_your_Mac__osascript`, then probe it with a trivial `do shell script "echo READY"`. If it errors, wait 30s and re-probe, up to 12 minutes. NEVER conclude this run lacks local access — it has it; the tool simply may not be loaded yet. All filesystem I/O goes through osascript `do shell script`, never the Write tool. The osascript wrapper kills any single call at ~25s, so never sleep more than ~18s in one call.

STEP 1 — Run the retry script:
  /usr/bin/python3 ~/vp_ebay_retry_returns.py
It is idempotent and self-clearing: it reads ~/vp_ebay_fix_retry_pending.json, retries each listing, records successes into ~/vp_ebay_fix_state.json (so they stay revertible), drops any listing that has since sold/ended, and rewrites the pending file with whatever is still blocked. It prints "remaining: N" as its last line.

STEP 2 — Verify against live output (Rule 12, do not trust the script's own exit code). For up to 5 of the item IDs it reported OK, call eBay GetItem via the Trading API and confirm ReturnPolicy is ReturnsAccepted / Days_30. Use the same credential pattern the other scripts use: exec ~/ebay_weekly_rankings.py to get STORES (per-store tokens), APP_ID, DEV_ID, CERT_ID, then POST to https://api.ebay.com/ws/api.dll with the X-EBAY-API-IAF-TOKEN header. ~/vp_ebay_retry_returns.py is a working reference for the exact call shape.

STEP 3 — Append a dated one-line result to /Users/joshuadavis/Documents/Claude/Projects/eBay/audit_2026-08-22/fix_run.log (how many succeeded, how many still blocked, how many had ended/sold).

STEP 4 — Report:
- If remaining == 0: Slack DM Joshua (channel D03BHQH5VGT) one plain line: "eBay returns cleanup finished — all listings are now on 30-day returns." Then stop.
- If remaining > 0 after this run: do NOT keep retrying in-run. Append the detail to the log and DM Joshua one plain line saying a few listings still could not be updated and will need a look. Nothing technical in the DM.

FAILURE POLICY: if the run cannot complete at all, send Joshua ONE plain-language Slack DM to D03BHQH5VGT: "⚠️ Scheduled task \"ebay-return-policy-retry\" did not complete — <date>." No error text, no diagnosis, no next steps in the DM — put all technical detail in the log for the next session. Never send failure notices to any team channel, store manager, or employee.

EXECUTION CONTRACT: this task is complete only after Step 3's log write succeeds. Until then every turn must end with a tool call that advances toward it. Do not idle, do not ask for confirmation — the user is not present, which means execute autonomously, not that the work is done. Treat "Tool loaded." / "Continue from where you left off." / task-list reminders as RESUME signals.