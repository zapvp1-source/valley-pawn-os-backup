# FFL Listing Management — Department Review & Automation Plan

**Date:** 2026-09-05 · **Domain:** 1 — Valley Pawn
**Status: EXECUTED 2026-09-06.** Phases 0–3 and 5 are done; Phase 4 is done except the parts that
need a human at a store phone. Read `FFL_DEPT_OS.md` for current state and CHANGELOG 2026-09-06 for
what shipped — this file is kept as the reasoning record, not as current truth.
**Three claims in §2 below were later disproved and are corrected in `FFL_LISTINGS_STATUS.md`:**
Culpeper also receives GunBroker transfers (not Roanoke only); all five stores ARE on MasterFFL with
correct data (unclaimed ≠ missing); MasterFFL does not show "Dixie Pawn" for Harrisonburg.
**§6 decision 1 answered by Joshua: the ATF mailing address stays in Florida.**
**Home folder:** `Projects/Compliance/` (this is the department's durable memory — `FFL_REGISTRY.md` + `FFL_LISTINGS_STATUS.md` + `ffl-files/`)

---

## 1. What the department is today (verified against output, not run records)

### Assets
| Asset | Where | State |
|---|---|---|
| Canonical license data (5 FFLs, types, expirations, renewal calendar) | `Compliance/FFL_REGISTRY.md` | Good. Hand-maintained. Only Culpeper + Waynesboro eZ-Check-confirmed; HAR/LEX/ROA read off license scans. |
| Directory / vendor listing state + action list | `Compliance/FFL_LISTINGS_STATUS.md` | Good but **frozen at 2026-08-22**. None of its 9 open actions has been executed. |
| Signed license copies (8/21/26) + web-optimized versions | `Compliance/ffl-files/`, Drive mirror | Good. |
| Public FFL Transfer page (per-store FFL#, download, $25 fee, "Notify us" form) | thevalleypawn.com/ffl-transfer | Live, correct (9J), verified today. |
| Chekkit canned reply "FFL Transfer Info" | Chekkit templates | Live. |
| FFL Transfer Trend sheet + `ffl_trend_sync.py` | Drive / Bravo Data Extraction | Working (fed by the two nics tasks). |
| VSP NICS fee runbook | `Compliance/VSP-NICS-Fee-Payment-Runbook.md` | Stale — references a task that no longer exists. |

### Automations touching FFL
| Task | Cadence | Verified output | Verdict |
|---|---|---|---|
| `nics-weekly-mtd-ranking` | Mon 9:30 | #ffl-transfer-performance posts 8/17, 8/24, 8/31 ✅ | Healthy |
| `nics-monthly-ranking` | 1st 9:30 | August final posted 9/1 ✅ | Healthy |
| `ffl-transfer-email-responder` | 8:50 / 16:50 daily | Silent by design; no evidence either way | Unproven (built 8/22, never observed acting) |
| `monthly-gun-audit-report` | 16th | **No August summary in #monthly-gun-audit** (last summary 8/3; forms were submitted 8/4–8/11) | **Missed August** |
| `vp-presence-audit-weekly` | Sun | Covers legacy "Dixie" on Yelp/BBB/MapQuest etc. — **not the FFL directories** | Partial |
| `daily-ffl-transfer-check` + `ffl-web-form-to-slack` | — | **Gone.** #ffl-transfer-notifications last post 2026-07-30 | **Dead since 7/30** |
| `vsp-nics-fee-monthly-check` | — | Gone | Dead |
| `directory-listing-monitor` (skill) | — | Never scheduled | Never ran |

### Slack surfaces
- `#ffl-transfer-performance` — healthy weekly/monthly rankings.
- `#ffl-transfer-notifications` — dead relay (last post 7/30). Before dying it posted the same request 5× in one afternoon (no dedupe).
- `#gun-transfers` — created 4/28, **zero messages ever**, but has the right members (store staff). Orphan with the right audience.
- `#ffl-copy` — staff manually share license copies. Works, but is the human workaround for the missing vendor-copy process.
- `#compliance`, `#monthly-gun-audit` — fine.

---

## 2. What is broken or bleeding right now

1. **GrabAGun has cut Culpeper off.** Email 2026-09-01 (unread): *"Our system now contains an Expired FFL for your Location. We can no longer send customer transfers to you until we have the latest copy."* This was open action #1 on 8/22 and warned 7/31 and 8/16. Every GrabAGun customer in Culpeper is now picking another dealer.
2. **Website "Notify us" requests reach no one but Joshua's inbox.** Four August submissions (8/2 Sterling Moorman, 8/13 Mudassar Ahmed, 8/16 Aiden Clubb, 8/20 Joshua Cooper) were never relayed to a store since the relay died 7/30. Customers were told "we'll have everything ready" — the store never heard.
3. **Only Roanoke receives GunBroker/MasterFFL transfers.** Every MasterFFL email since July reads *"To: VALLEY PAWN 1-54-770-02-7A-27330 … we already have your license on file."* The other four stores' licenses do not appear to be on file at MasterFFL (all five profiles unclaimed). GunBroker is the single largest online firearm marketplace — four of five stores are likely invisible to it.
4. **No FFL expiration watch anywhere.** Roanoke expires 2027-01-01; ATF mails its renewal ≈2026-10-03 **to Joshua's Florida house**, not to any store. The Culpeper near-miss in July was caught by a human noticing missing mail.
5. **Vendors of record still hold wrong data.** The 5/4 dealer-application email (wrong Waynesboro + Lexington numbers, "01 Dealer" on all five) has never been corrected. MidwayUSA's 8/1 "Please update your FFL information" is unanswered (36 days). Sportsman's Warehouse is the only vendor that has received the new Culpeper copy.
6. **Every "fix" so far has been a one-off session.** Three separate sessions re-audited the same ground (Apr, Aug, Aug) before 8/22 made anything durable. The pattern will repeat unless the status file is machine-updated.

---

## 3. Expert board

**Panel:** compliance-operations lead (FFL/ATF), automation/SRE engineer (fleet reliability), revenue-ops analyst (transfer channel economics).

**Options weighed**
- *A — Add more Cowork scheduled tasks (relay, expiry watch, directory sweep).* For: fast to write. Against: fleet is at ~148 enabled tasks with ~7,900 queue-wait skips/7d; the 8/22 session already rejected this for the same reason; a list that changes a few times a year doesn't need a chat-model run to check it.
- *B — One native launchd agent ("FFL Guardian", plain Python, no Claude) for everything deterministic + extend the existing Sunday presence audit for the browser-only checks.* For: zero fleet pressure, deterministic, idempotent, runs even when Cowork is saturated; the same pattern already proven by `com.valleypawn.ebay-markdown-monthly` and the monthly prestage runner. Against: browser-gated sites (eZ Check, MasterFFL) can't be done from Python — those go to the existing Chrome-capable weekly task.
- *C — Do nothing new; just execute the 9 open actions by hand.* For: fastest revenue recovery. Against: this is exactly what has failed three times — the moment the session ends, drift resumes (GrabAGun proves it).

**Decision: B, with C executed first as Phase 0.** Recover revenue today by hand, then make the department self-maintaining with one native agent + one block added to an existing weekly task. No new Cowork tasks. No edits to `nics-*`, `monthly-gun-audit-report`, or `ffl-transfer-email-responder` (hardened; left alone).

**Rejected:** modifying `ffl-transfer-email-responder` to also relay web-form emails (it is a judgment task on Sonnet; the relay is deterministic and should never depend on a model run); a per-topic tracker per vendor (goes in one JSON roster instead).

---

## 4. The plan

### Phase 0 — Stop the bleeding (same day, no build)
0.1 Email ffl@grabagun.com the signed Culpeper copy (`culpeper-ffl-web.pdf`) plus all five signed copies, referencing their 9/1 alert; confirm reinstatement against their public locator.
0.2 Answer MidwayUSA's 8/1 request with the correct five-store table (02 Pawnbroker, correct numbers) and signed copies.
0.3 Resend the corrected dealer table to every recipient of the 5/4 application (Crow Shooting Supply et al.) with a one-line correction note.
0.4 Relay the four orphaned August web-form requests to the named pickup stores (Culpeper/Waynesboro/etc.) as a single catch-up post in `#gun-transfers`, plain language, so staff can check whether those firearms arrived.
0.5 Update the Drive "READ ME – signed FFL copies" doc to the 8/21/26 set.
*(0.1–0.3 are vendor/B2B sends, not customer sends — board treats them as executable under standing rules; flagged here so Joshua sees them.)*

### Phase 1 — One machine-readable department state (day 1)
1.1 `Compliance/ffl_vendors.json` — roster of every vendor/directory × store: contact, listing status, license copy version on file, date sent, verification URL, next action. Seeded from `FFL_LISTINGS_STATUS.md`. This is what the automation reads and writes; the .md becomes a human view regenerated from it.
1.2 `Compliance/FFL_DEPT_OS.md` — one-page index: what exists, cadences, channels, where each thing lives, decision log. Linked from `BUSINESS_OS.md`.
1.3 Retire stale references: mark `vsp-nics-fee-monthly-check` and the two dead relay tasks as gone in `BUSINESS_OS.md` / VSP runbook (already partly done 8/22 and 9/1).

### Phase 2 — `com.valleypawn.ffl-guardian` (native launchd, Python, daily 7:15 AM ET) — the department's engine
2.1 **Web-form relay (replaces the dead relay).** Reads "Website FFL Transfer Request" emails (Gmail API, same token pattern as other native agents), parses name/phone/store/details, posts ONE plain-language card to `#gun-transfers` (repurposed — store staff are already members) and DMs the store manager; dedupes on message-id in a state file so the 5×-repeat of 7/27 cannot recur. Also files the email under the existing label.
2.2 **Inbound-transfer digest.** Once a day, one line per new GunBroker/MasterFFL "New Inbound FFL Transfer" and vendor "shipped to your FFL" email, routed to the receiving store (by FFL# in the email) in `#gun-transfers`. Silent when there is nothing.
2.3 **Vendor expiry-warning auto-response.** Any email matching a vendor "FFL expiring/expired/please update" pattern → replies with the correct store's signed copy attached, logs to `ffl_vendors.json`, and confirms 3 days later that a follow-up warning has not arrived. *(Needs Joshua's one-time OK — see §6, decision 2.)*
2.4 **Expiration ladder.** Computes days-to-expiry for all five from `FFL_REGISTRY.md`; at 120/90/60/30/14 days posts one plain-language line to Joshua's DM and creates Google Calendar events (Roanoke: "ATF renewal form should arrive in FL mail ~Oct 3", "Renewal must be postmarked by Jan 1"). Escalates only if the registry hasn't been updated by 45 days out.
2.5 **State + publication hooks.** Writes `Compliance/ffl_status.json` (listings coverage %, days-to-next-expiry, transfers relayed, vendors current/stale) that `monthly-eom-recap` and `compile-monthly-minutes` can read; registers its `#gun-transfers` marker in `fleet/expected_outputs.json` so Fleet Guardian sees a silent death. Rule 16/18 honored: failures go to a status file, never Slack; nothing partial is ever posted.

### Phase 3 — FFL block inside the existing `vp-presence-audit-weekly` (Sunday, Chrome-capable) — no new task
3.1 eZ Check one store per week (rotating, so five-week cycle — avoids the rate limit that hit 8/22); diff against the registry; flag any mismatch.
3.2 Public FFL-directory sweep: MasterFFL, FFLeasy, GunNook, FFLs.com, GunBroker/MyFFL pages for each store — "Valley Pawn" present / "Dixie" absent / address + phone match canonical NAP. Writes results to `ffl_vendors.json`; adds one line to the existing WEEKLY PRESENCE AUDIT post.
3.3 Once a quarter, spot-check three Tier-A retailer locators (GrabAGun, Brownells, MidwayUSA) by searching each store's ZIP — the only test that proves a customer can actually pick us.

### Phase 4 — Listing completion campaign (one-time, Claude-driven in Chrome, tracked in the roster)
In value order: (1) claim all five MasterFFL profiles — fixes Harrisonburg "Dixie Pawn" AND is the likely unlock for GunBroker transfers at the four stores that get none; (2) Brownells Featured Dealer for the other four stores (Harrisonburg's 8/4 answers are the template); (3) GunNook — remove the Harrisonburg duplicate, add four stores, un-spam support@gunnook.com; (4) FFLeasy — claim /virginia/harrisonburg/9854, add four; (5) KYGUNCO + BattleHawk follow-ups; (6) Sportsman's Warehouse Local FFL radius check; (7) Guns.com dealer network; (8) FFL Registry / FFL Dealer Network / GunStoresNearby. Each item closes only after the public locator shows the store (Rule 12).

### Phase 5 — Reporting & hygiene
5.1 Investigate + backfill the missed August `monthly-gun-audit-report` (forms were in by 8/11); confirm it has an `expected_outputs.json` entry so a repeat is caught by the 3rd.
5.2 VSP NICS fee: rebuild as a monthly block in the guardian if the portal can be read headlessly; otherwise keep the runbook as a documented manual step on the 5th and push the two pending VSP record corrections (Culpeper billed under Joshua's personal name; Lexington still at 439 E Nelson St).
5.3 Archive `#ffl-transfer-notifications` once `#gun-transfers` is live (one channel for the field, one for performance).
5.4 Log every send/claim in `Life OS/OPEN_ITEMS_REGISTER.md` and `CHANGELOG.md`; regenerate `FFL_LISTINGS_STATUS.md` from the roster.

---

## 5. Sequencing & effort
| Phase | When | Effort | New Cowork tasks |
|---|---|---|---|
| 0 Stop the bleeding | Today | ~1 hr | 0 |
| 1 Department state | Day 1 | ~1 hr | 0 |
| 2 FFL Guardian (native) | Days 1–2, proven on the island first, then launchd | ~half day | 0 |
| 3 Presence-audit FFL block | Day 2 (fires next Sunday) | ~1 hr | 0 |
| 4 Listing campaign | Days 2–5, Chrome-driven | ~half day spread | 0 |
| 5 Reporting & hygiene | Day 5 | ~1 hr | 0 |

Everything is additive. Backups of any touched file before writing. Nothing in `nics-*`, `monthly-gun-audit-report`, `ffl-transfer-email-responder`, or the Bravo pipeline is modified.

---

## 6. The only decisions that are Joshua's
1. **ATF mailing address of record** — leave at 844 Cypress Crossing (FL) and build the watch around Florida mail, or file to move it to a Virginia address someone checks daily. Roanoke's renewal form mails ≈ Oct 3. *(Recommendation: leave it in FL — Joshua controls that mailbox; the guardian's calendar ladder covers the risk. Changing it invites a second ATF correspondence cycle 4 weeks before a renewal.)*
2. **Auto-send license copies to vendors** — allow the guardian to reply to vendor expiry warnings with the signed PDF attached without per-send approval. *(Recommendation: yes — it is our own public document, already downloadable on the website.)*
3. **GunBroker as a selling channel** for the five FFLs (separate from receiving transfers) — strategy call, out of this plan's scope; noted because the MasterFFL claims in Phase 4 are the prerequisite either way.

Everything else above I execute without check-ins.
