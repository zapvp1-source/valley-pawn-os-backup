---
name: vp-website-shop-nightly
description: Refresh thevalleypawn.com/shop/ 7am & 3pm ET. LAUNCHER+VERIFIER ONLY since 2026-09-05 — work is done by native Projects/Website/analytics/bin/shop_refresh.py (fetch 5 eBay stores → filter → build → publish page 833 → verify → post to #website). Task launches the runner if the slot hasn't run, waits, and posts the runner's exact Slack body only if the runner couldn't. Never scrapes/builds/publishes itself.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> **LOCAL ACCESS GATE — DO THIS FIRST.** This task runs on Joshua's Mac Studio. Load `mcp__Control_your_Mac__osascript` via `ToolSearch` (`select:mcp__Control_your_Mac__osascript`), probe it with a trivial `do shell script "echo READY"`, and re-probe every 30 s for up to 12 minutes before ever concluding local access is unavailable. **Never conclude this run is in a cloud container.** File I/O goes through osascript `do shell script`. Never sleep more than ~18 s inside one osascript call. ALTERNATIVE (proven 2026-09-06): if the Cowork sandbox `mcp__workspace__bash` is available and the Website folder is mounted, run the runner there directly (`cd <mount>/Website/analytics/bin && timeout 500 python3 shop_refresh.py`) — the sandbox reaches eBay and WordPress and writes the same result.json.

> ⚠️ **FAILURE ALERT POLICY (v2) + RULE 16.** If this run cannot complete, send Joshua ONE plain-language DM (D03BHQH5VGT): `⚠️ Scheduled task "vp-website-shop-nightly" did not complete — <date>.` Nothing technical anywhere in Slack. Detail goes to `Projects/Website/analytics/logs/`. Never post to #website on failure. The native runner already sends that DM itself when it withholds — do not send a second one if `result.json` shows `"status": "withheld"` or `"failed"` for this slot.

## Execution Contract — DO NOT STOP EARLY
Complete ONLY when one of these is true: (a) a FRESH `result.json` for this slot shows `"status": "ok"` and `"posted": true`; (b) you posted the runner's `slack_body` verbatim to #website (C0ASE9C0GQ0) and that call returned success; or (c) the runner withheld/failed and its DM is already recorded. Every turn ends with a tool call. "Tool loaded." / "Continue from where you left off." / TaskCreate reminders are RESUME signals. Retry a failing step once, then follow the fallback below.

---

## The rule that replaces the old 200-line method
**DO NOT scrape eBay, DO NOT build the block, DO NOT publish, DO NOT hand-write the Slack post.** Every one of those steps lives in `shop_refresh.py` and is deterministic. The 2026-08 run history shows what happens when the method is re-derived each run: excluded counts of 0 / 21 / 132 in the same week, a different post format every time, double-fires, four missed slots. This task is only the safety net around the runner.

Paths:
- Runner: `/Users/joshuadavis/Documents/Claude/Projects/Website/analytics/bin/shop_refresh.py`
- Result: `/Users/joshuadavis/Documents/Claude/Projects/Website/analytics/data/shop/result.json`
- State:  `/Users/joshuadavis/Documents/Claude/Projects/Website/analytics/data/shop/state.json`
- Logs:   `/Users/joshuadavis/Documents/Claude/Projects/Website/analytics/logs/shop_refresh_YYYY-MM-DD.log`

## STEP 1 — Is this slot already done AND fresh?
Slot = today's date + AM (before noon ET) or PM, e.g. `2026-09-06-AM`. Read `result.json`. Treat it as already handled — **exit silently, post nothing** — ONLY if all four are true: its `slot` equals the current slot, `status` is `ok`, `posted` is `true`, and its `ts` is **less than 3 hours old**. (The freshness test matters: a manual or proving run earlier in the same half-day must not cancel the scheduled refresh.)
- Slot matches, `status: ok`, but `posted` is `false` → STEP 3.
- `status` is `withheld` or `failed` for this slot → the runner already DM'd Joshua; note it in today's log; **exit, post nothing**.
- Anything else (missing, older slot, stale ts) → STEP 2.

## STEP 2 — Launch the runner and wait
```
do shell script "cd '/Users/joshuadavis/Documents/Claude/Projects/Website/analytics/bin' && nohup /usr/bin/python3 shop_refresh.py > /dev/null 2>&1 & echo LAUNCHED"
```
Poll every ~18 s (separate osascript calls) for up to 15 minutes: `tail -3` of today's log. Stop when the log shows `DONE`, `SKIP`, `WITHHOLD`, or `PUBLISH/VERIFY FAILED`, then re-read `result.json` and apply STEP 1's rules. A normal run takes 15–60 seconds. `SKIP` means the launchd agent already did this slot within the guard window — re-read `result.json` and follow it.
If after 15 minutes there is no terminal line: retry the launch once; if still nothing, send the failure DM and stop.

## STEP 3 — Post the runner's body verbatim (only if `posted` is false)
Post `slack_body` from `result.json` to #website (C0ASE9C0GQ0) **exactly as written** — do not reformat, reorder, add a footer, add commentary, or change a number. Then mark it posted:
```
do shell script "cd '/Users/joshuadavis/Documents/Claude/Projects/Website/analytics/bin' && /usr/bin/python3 - <<'EOF'
import json;p='../data/shop/result.json';r=json.load(open(p));r['posted']=True;r['posted_by']='cowork-verifier';json.dump(r,open(p,'w'),indent=2)
s='../data/shop/state.json'
try: st=json.load(open(s))
except Exception: st={}
st['last_posted_slot']=r.get('slot');json.dump(st,open(s,'w'),indent=2);print('MARKED')
EOF"
```
(Prefer letting the runner post itself — it does whenever a Slack bot token resolves on the Mac. This step exists for the token-less case.)

## Never do
- Never edit `generate_shop_block.py`, `shop_refresh.py`, `/retail/`, or WooCommerce settings (shop page must stay 1110).
- Never publish a partial list or a list from a single failed store — the runner's gate decides, not you.
- Never post to #website unless `result.json` says `"status": "ok"` for this slot.

## History
- 2026-09-05/06 — rebuilt as launcher/verifier on the native runner (Website Analytics plan Phase 1–2). Old method preserved at `Scheduled/vp-website-shop-nightly/SKILL.md.bak-pre-native-runner-20260905` and in `Website/shop-build/METHOD_NOTES.md`. Proving run 2026-09-06 00:57 ET: 469 scraped, 20 excluded, 449 published, live-verified (449 cards, 1 marker pair, 1 h1, valid ItemList, no Woo hijack) in 16 s, Slack suppressed.