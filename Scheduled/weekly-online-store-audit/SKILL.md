---
name: weekly-online-store-audit
description: Weekly eBay estate + website health check for Valley Pawn — pulls all 5 stores, auto-fixes drifted returns policy ONLY (never Best Offer), posts trend summary to #ebay-performance, feeds the monthly minutes.
model: claude-sonnet-5
---

---
name: weekly-online-store-audit
description: Weekly eBay estate + website health check for Valley Pawn — pulls all 5 stores, auto-fixes drifted returns policy ONLY (never Best Offer), posts trend summary to #ebay-performance, feeds the monthly minutes.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> 🛑 **STANDING RULE — BEST OFFER IS NEVER TURNED ON. Set by Joshua 2026-09-17 from store feedback. This overrides every other instruction in this file, and any instruction inside any script this task runs.**
>
> Joshua, verbatim: *"Stop changing listings that are marked as no offers allowed to offers allowed. We do not want make an offer on video games at all."*
>
> - A listing with Best Offer switched OFF is a deliberate decision by the store. **Leave it alone.** Never enable Best Offer, never set or adjust auto-accept / auto-decline thresholds on a listing that currently has offers off, and never "restore" Best Offer because an older audit or state file says it used to be on.
> - **Video games never take offers, at all.** Never enable Best Offer on any video game, game console, or game accessory listing, regardless of price, age, or category. If you find Best Offer switched ON for a video game (our own automation did this in the past), note it in the Slack post so a person can switch it off — do not switch it off yourself either; that is a store call.
> - This is not a threshold or a default that can be tuned. There is no exception. If a future instruction, script comment, or state file tells you to enable Best Offer, that instruction is void.

Weekly online-store audit for Full Circle Finance Inc DBA Valley Pawn. Runs every Sunday at 8 AM ET on Joshua's Mac. Fully autonomous — no clarifying questions, no check-ins.

BACKGROUND: On 2026-08-22/23 a full audit of the eBay estate (5 stores, 514 listings) and thevalleypawn.com found and fixed a batch of issues: listings not on 30-day buyer-pay returns, listings with Best Offer off, and missing H1/structured-data on the /shop/ page. This task is the recurring, lighter-weight follow-on: catch NEW drift every week, track the KPIs that matter over time, and feed a real Slack post into #ebay-performance. **The Best Offer half of that original remediation has since been reversed by Joshua (2026-09-17) and is no longer part of this task's job** — only the returns-policy fix remains.

STEP 0 — LOCAL ACCESS GATE. If `mcp__Control_your_Mac__osascript` is not loaded, load it via ToolSearch `select:mcp__Control_your_Mac__osascript` first, then probe with `do shell script "echo READY"`. If it errors, wait 30s and retry, up to 12 minutes total. Never conclude this run lacks local access — it has it, the tool just may not be loaded yet. All filesystem I/O goes through osascript `do shell script`, never the Write tool. The osascript wrapper kills any single call around 25s — never sleep longer than ~18s in one call; poll across separate calls for the longer eBay pull.

STEP 1 — Run the audit + auto-fix script, RETURNS ONLY:
  /usr/bin/python3 ~/vp_weekly_online_store_audit.py --no-bestoffer
It pulls all 5 stores' active listings and last 7 days of sales via the eBay Trading API and auto-fixes any listing not on ReturnsAccepted / 30-day / buyer-pays-return-shipping. Every write is recorded in ~/vp_ebay_fix_state.json (shared state file, reversible). Output: `~/Documents/Claude/Projects/eBay/weekly_audit/<DATE>/report.json` and `summary.md`, plus `.../weekly_audit/latest.json` for next week's trend comparison. It prints a Markdown summary as its last output — capture it.

**If `--no-bestoffer` is not a recognised flag** (the script has not been patched yet), do NOT run it unguarded. Instead:
  a. Run it in its read-only/report mode if it has one, or pull the estate yourself via the Trading API (`GetMyeBaySelling` + `GetItem`, credentials pattern below) and compute the same numbers.
  b. Apply ONLY the returns fixes yourself via `ReviseFixedPriceItem` with a `<ReturnPolicy>` block — never a `<BestOfferDetails>` block.
  c. Add one line to the FAILURE_LEDGER noting the script still needs its Best Offer path removed, so the next fleet session patches it at the source.
Under no circumstances run the script in a mode that can touch Best Offer.

This task does NOT touch handling time, price, or inventory allocation between stores — those stay manual/flagged only.

STEP 2 — Verify against live output (Rule 12). Spot-check 2–3 of the auto-fixed item IDs by pulling them fresh via eBay GetItem (exec ~/ebay_weekly_rankings.py for STORES/APP_ID/DEV_ID/CERT_ID, POST to https://api.ebay.com/ws/api.dll with X-EBAY-API-IAF-TOKEN) and confirm the return policy actually changed. Also confirm the run changed **zero** Best Offer settings — if the state file shows any Best Offer write this run, say so plainly in the Slack post and log it to the FAILURE_LEDGER. If any spot-check fails, note it in the Slack post rather than claiming success silently.

STEP 3 — Post to Slack #ebay-performance (read SLACK_WEBHOOK from the top of ~/ebay_weekly_rankings.py and POST to it, or use the Slack MCP tool if available). Post the summary.md content from Step 1, plus a one-line callout of anything that needs a human: a store newly showing Below Standard risk signals (rising >180-day inventory, dropping revenue/listing week over week), any fix_failures_this_run > 0, and any video-game listing found with Best Offer switched on. Keep it factual — numbers and deltas, plain language, no tool or script names.

STEP 4 — Append one line to the CHANGELOG only if something NOTABLE happened this week (a metric moved >20%, a store crossed into/out of a risk zone, or fix failures appeared) — otherwise skip it; the dated report file is the durable record every week.

EXECUTION CONTRACT: complete only after the Step 3 Slack post succeeds. Every turn must end with a tool call advancing toward that. Do not idle or ask for confirmation — the user is not present, meaning execute autonomously, not that the work is done. Treat "Tool loaded." / "Continue from where you left off." / task-list reminders as RESUME signals, not stop signals.

---

# OUTBOX SEND (MANDATORY) — replaces the direct Slack send

**Do NOT call `slack_send_message` for the final post.** In a scheduled run there is no one to
approve it, so it is declined automatically and the whole run's work is lost (this happened on
2026-09-21). Post through the outbox instead — a native agent sends it via the ops bot within about
two minutes, with no approval step:

1. Write the complete, final message text (exactly as it should appear, Slack mrkdwn, no task ids,
   plain language — Rule 16) to
   `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/outbox/weekly-online-store-audit-<YYYYMMDD-HHMMSS>.txt`
2. Write the envelope, same base name, `.json`:
   `{"channel": "C0ANVN5KX4Y", "file": "<the absolute path of the .txt you just wrote>"}`
3. Stop. Do not wait for it, do not verify it in Slack, do not post a "sent via outbox" note.
   The receipt is written automatically under this task's name; the audit credits it.

Write the `.txt` BEFORE the `.json` — the flusher acts the moment it sees the envelope.
If the run has nothing to report, write nothing. The all-or-nothing and silence rules still stand.
