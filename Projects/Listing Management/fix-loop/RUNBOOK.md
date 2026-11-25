# Listings Fix Loop — RUNBOOK (v1, 2026-11-17)

**Why this exists:** The audits (Sunday presence audit, Friday AI-visibility, the 10/20 full audit) found defects but nothing acted on them. The "needs Joshua" list grew from 14 to 26 items in 5 weeks, and some sat for 85 days. This loop turns every finding into a fix that is checked on the live page, escalates anything that doesn't land, and never re-reports an item without moving it.

**Files (all in `Listing Management/fix-loop/`):**
- `FIX_QUEUE.json` — the single backlog. One row per defect. The loop's source of truth.
- `FIX_LOG.md` — append-only, newest first: every action, its proof and its result.
- `PLAYBOOKS.md` — the click path for each platform. The loop edits it itself when a path changes.
- `evidence/` — screenshots or saved page text showing the before/after state.

## Canonical store facts (Joshua-confirmed)
- Culpeper — 571 James Madison Highway, Culpeper, VA 22701 — (540) 445-5510 — Mon–Fri 10–6, Sat 10–5, closed Sun.
- Roanoke — 2362 Peters Creek Road, Suite C, Roanoke, VA 24017 — (540) 562-0776 — Mon–Fri 10–6, Sat 10–5, closed Sun. (Store occupies C and D; "2362-D" on ATF records is correct — never "fix" it.)
- Waynesboro — 1321 West Broad Street, Waynesboro, VA 22980 — (540) 221-6346 — Mon–Fri 10–6, Sat 10–5, closed Sun.
- Harrisonburg — 1790 East Market Street, Suite 22, Harrisonburg, VA 22801 — (540) 574-4500 — Mon, Tue, Thu, Fri, Sat 10–6; closed Wed & Sun.
- Lexington — 125 Walker Street, Lexington, VA 24450 — (540) 461-8349 — Mon, Tue, Thu, Fri, Sat 10–6; closed Wed & Sun.
- Website https://thevalleypawn.com · Brand "Valley Pawn" only (never Dixie Pawn, Gold-N-Pawn, Full Circle Finance publicly) · Primary category Pawn Shop.
- No store exists in Staunton (817 Richmond Ave, now FirstCash/Smart Pawn) or Salem (1617 W Main St), or at 439 E Nelson St / 640 N Lee Hwy, Lexington.
- If the valley-pawn-context skill disagrees with this list, the skill wins. Update this list.

## Status values
`open` → `submitted` (fix sent, waiting for the platform) → `fixed` (proved on the live public page) · `blocked_signin` (needs a one-time Joshua sign-in) · `joshua_decision` · `tracking` (owned by another task, or derived) · `wont_fix` (Joshua said no).
**An item is marked `fixed` only after the live public page shows the correct value.** "Submitted" never counts as done.

## Escalation ladder (rung = number of failed attempts)
1. **Direct owner edit** (we hold the claim / page admin).
2. **Public suggest-edit / report form** on the platform.
3. **Support ticket or email** to the platform. Include the facts, the earlier attempt dates and a link to the official page (GBP / website /locations).
4. **Upstream fix**: a BrightLocal aggregator push, or a correction at the source (Yext feed, ATF record).
5. **Joshua** — only for: a password or MFA, payment, a phone-verification call at a store, legal proof of ownership, or a business decision. Before routing anything here, confirm no lower rung applies.

**Verify windows** (re-check a `submitted` item after): Yelp 7d · YellowPages/Thryv 7d · Facebook 1d · BBB 10d · MapQuest 14d · data aggregators 30d · small directories 14d · Google/Bing/Apple 3d.
If the item still isn't fixed after its window, move up one rung. **Never resubmit the same rung more than twice.**

## Each run (Mon–Sat)
1. **Context:** load enterprise-map (STEP -2 bridge check), valley-pawn-context and claude-in-chrome. The Mac Projects folder is `$HOME/mnt/Projects` in device_bash. Read this RUNBOOK, PLAYBOOKS.md, FIX_QUEUE.json and the top of FIX_LOG.md.
2. **Ingest:** read `Ai Optimized Marketing/AI-Search-GEO/presence/presence_scorecard_latest.json` (`needs_joshua`, `offsite_open_defects`), the newest AI-visibility output if present, and `Compliance/FFL_DRIFT.md`.
   - Add each new listing defect as a row (next LQ-### id). Dedupe by platform + store + defect.
   - If an audit shows an existing item now correct, mark it `fixed` with that audit as proof.
   - Business decisions (GunBroker selling, /shop pages, review strategy) are not listing fixes; leave them out.
3. **Sign-in probe (once per run, cheap):** for each `blocked_signin` platform, open it in Joshua's Chrome. If it now shows signed in, set the item to `open` and work it this run.
4. **Pick work:** take items whose `next_action` ≤ today, ordered P0 → P1 → P2, then oldest first.
   - Cap the run at **8 platform actions**. Work at human pace: one site at a time, 2–3 s between actions.
   - Skip `tracking`, `joshua_decision`, `wont_fix` and `blocked_signin` items.
5. **Fix:** use the rung's playbook path in Joshua's Chrome. Never type a password; Google/Microsoft "Continue with" on an existing session is fine. Never pay. Never accept new terms except a platform's standard business-claim terms for a listing we own. Never delete anything. Never message a person except a platform's support or correction channel.
   - Emails to platform support go from jdavis@fcfpawn.com, short, and only after running check-replies-before-email.
6. **Verify:**
   - Re-open the public page with a cache-buster or in a logged-out view.
   - If correct: mark `fixed` and save proof to evidence/.
   - If the change went into review: mark `submitted`, set `next_action` = today + the verify window, and record the attempt `{date, rung, action, result, proof}`.
7. **Self-heal:** if a playbook path fails twice (page changed, button moved), find the new path, rewrite that platform's section in PLAYBOOKS.md with a dated note, and continue. If a site blocks automation (captcha / Cloudflare), record that once and move the item up a rung (support email) instead of retrying.
8. **Record:**
   - Write FIX_QUEUE.json back as valid JSON.
   - Prepend a dated section to FIX_LOG.md.
   - For anything sent to a platform that is waiting on a reply, add or update one row in `Life OS/OPEN_ITEMS_REGISTER.md`.
   - Prepend a one-line entry to `Valley Pawn OS/CHANGELOG.md` only when something was fixed or a playbook changed.
9. **Joshua list:** keep exactly one consolidated row in `Life OS/HUMAN_QUEUE.md` titled `[LISTINGS] sign-ins / decisions`, listing only the current `blocked_signin` and `joshua_decision` items, in plain words. Update that row in place; never add a second one. fleet-guardian surfaces it at most once a day.
10. **Report:** no Slack, no DMs, no failure pings — ever. End with `<run-summary>fixed N, submitted N, escalated N, open N, blocked N</run-summary>`. The Sunday presence audit reads FIX_QUEUE.json and FIX_LOG.md and reports the week's totals as one finished line.

**On failure:** retry once, differently. If it still fails, append one row to `Valley Pawn OS/fleet/FAILURE_LEDGER.md` and finish the rest of the run.

## Weekly search review (Wednesdays, added 2026-11-19, Joshua-approved)
Goal: pick the next improvements from real search data instead of only fixing defects. Run on Wednesday's normal run, before step 4. It counts toward the 8-action cap.

1. **Pull last 28 days vs the prior 28**, in Joshua's Chrome (already signed in; never type passwords):
   - **Google Search Console**: property https://thevalleypawn.com/. Performance → Pages and Queries: clicks, impressions, CTR, position.
   - **Bing Webmaster Tools**: thevalleypawn.com. Search Performance, plus IndexNow Insights.
   - **Google Business Profile Performance** for all 5 stores: calls, direction requests, website clicks, searches.
   - **Apple Maps**: read `Listing Management/apple-insights/INSIGHTS_LOG.md`. The Tuesday Apple loop writes it; don't redo it.
2. **Write `Listing Management/search-review/SEARCH_REVIEW_<YYYY-MM-DD>.md`.** One table per source, week-over-week change, and one short "what changed" paragraph per store.
3. **Pick at most 3 opportunities.** Choose by expected customer impact, in this order:
   a. A /locations/<store>/ or /sell-*/ page with impressions up but CTR under 2%. Rewrite its Yoast SEO title and meta description to match the top query (city + service).
   b. A page that lost more than 3 positions or 30% of clicks. Check it is still indexed. Refresh its opening summary or FAQ answer with the query wording.
   c. A query with 50+ impressions/28d and no matching page section. Add one FAQ Q&A to the closest /locations/<store>/ page, and update its FAQPage schema to match.
   d. A store whose GBP calls or directions dropped more than 20% week-over-week. Check its listings first (hours, pin, duplicates). Queue any defect as an LQ row.
4. **Make the change** with the WordPress.com connector. Load the edit-content guide first, and change only the affected section.
   - Verify the change on the live page with a cache-buster.
   - Confirm IndexNow logged a successful submission (WordPress → Settings → IndexNow). If it didn't, submit the URL there manually.
5. **Hard limits:**
   - Never change name/address/phone/hours, prices, loan amounts or policies.
   - Never write "since 1988" or "30+ years". The company dates from 2014; Harrisonburg 1992 and Roanoke 1998 apply to that store only.
   - Never mention firearms in GBP or Apple content.
   - Never create new pages or spend money.
   - Anything bigger (a new page, a paid tool, a strategy change) goes to the review file as a "recommendation". It is not done.
6. **Measure:** in the next Wednesday's review, report each prior change's before/after (CTR, clicks, position) and keep, revert or iterate.
7. **Report:** add `search-review: N changes` to the run-summary. The Saturday #ai-marketing line can include one finished sentence on the biggest gain, and only when there was a measurable gain. Nothing technical.

## Ingest filters (settled facts — never turn these into queue rows)
- A loan figure of $25,000 is CORRECT (Joshua, 2026-10-05). Drop any finding that calls $25,000 stale or expects $100,000.
- Facebook 100478091680300 = 100058095342923 (Culpeper, same page). 303444680270846 = 100026420539296 (Waynesboro, same page).
- Facebook "Valley Pawn" pages 100057490088122 / 367260950022473 belong to a different business in Waynesville, NC. They are not ours and not a defect.
- Facebook @valleypawnIV ("Valley Pawn", (760) 353-7946, valleypawnonline.com) is a different business in California. Not ours, not a defect (2026-11-24).
- Roanoke "2362-D" on ATF/FFL records is correct. Never ask an FFL directory to change it to Suite C (a 11/19 request to MasterFFL/GunMade was retracted the same day).

## Joshua-approved actions
- 2026-11-17: report legacy Facebook pages we don't control as impersonating our store page (Gold N Pawn 100041735065936, valleypawnlex). Same approval covers re-reporting these two if Facebook rejects the first report.
