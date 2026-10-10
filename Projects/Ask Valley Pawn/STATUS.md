# Ask Valley Pawn — STATUS

**Read `ASK_VP_PLAN.md` first, then `DEMO_PLAN.md`. Resume from the build order; never restart.**

## 2026-10-08 — project opened (plan + demo set up)
- Joshua asked for the plan for a real-time, siloed, Slack-resident "super intelligence" for Valley Pawn built from the training material, P&P/handbook, recorded store phone lines, texts, emails and Preston's recorded Zoom line — answering any team member or Preston, and doing things for the team where it can. Then: "a real world demo of this to the team, set that up next."
- Inventory done (CHANGELOG, #ask-handbook, Ask_Handbook/, Preston Knowledge Base/, Zoom Call Pipeline/, Call Analysis/, Training Program/, Communcations/, Open Items Register, Anthropic's Claude Tag docs). Findings: #ask-handbook has had zero questions since 8/22 and its responder is off since 9/18; the Preston KB responder/capture/verify tasks were staged 9/7 but never registered; Preston's Zoom line (ext 813, 540-202-4200) is recording and in the roster since 10/6, so store↔Preston calls are finally capturable; manager cell numbers are still blank in `Zoom Call Pipeline/internal_roster.json`.
- Decision (board): native always-on responder on the Mac Studio polling the channel with the Goldilocks bot token (15 s), corpus-only answering with cite-check, six knowledge layers, SHADOW → LIVE. Not Claude Tag for the floor (plan/credits, no enforced grounding, cross-channel memory, no Mac reach, beta).
- Demo: Tue 10/20 9:30 AM ET on Zoom with Preston + managers, whole team in-channel; 14-question dry-run gate; announcement DRAFT in DEMO_PLAN.md — **not posted, awaits Joshua's OK**.
- Nothing built yet beyond the plan files. Nothing sent to anyone. No existing task, agent, channel or file modified.
- NEXT (week 1): `corpus_build.py` (layers 1, 2, 3, 6), `ask_vp_responder.py`, `com.valleypawn.ask-vp` launchd agent in SHADOW, 50-question dry run to Joshua's DM. Blocked this session: the device shell was unavailable (device_bash failed 3×), so code is written here and committed, and installation goes through the host job queue when the shell is back.

## 2026-10-08 (evening) — BUILT and running in SHADOW (Joshua: "ok lets do it and build it")
- **Responder live in SHADOW**: native agent `com.valleypawn.ask-vp` (every 15 s, `bin/ask_vp_responder.sh` → `ask_vp_responder.py`), polls #ask-handbook (C0BS11KTYKU) as Goldilocks, answers go to Joshua's DM only. Flip to LIVE = `"mode": "LIVE"` in `Ask Valley Pawn/config.json` (Joshua's call). State: `Valley Pawn OS/fleet/state/ask_vp/state.json` (starts from install time; never answers history).
- **Corpus**: `bin/ask_vp_corpus.py` → `Ask Valley Pawn/corpus/ASK_VP_CORPUS.jsonl`, rebuilt on every run when any source changed. First build: 456 passages → after sub-section split ~500: policy (P&P v2026.8 + Handbook v2026.5, numbered sections AND #### sub-sections, e.g. `pp:04.02/multiple-handgun-sales-protocol`), 219 Preston KB entries, 54 Academy lessons, 4 store-fact blocks (`facts/store_facts.md`). Upstream `build_sources.py` and `kb_build.py` run first and must exit 0.
- **Answer rules in code**: retrieval (BM25 + pawn-jargon synonyms, live melt-math passage from `spot_prices.json`), model may only use retrieved passages, must cite ids; cite-check, machinery-word check, approved-offer check, hedge check ("likely/probably" → routed to Preston), FACT passages override stale manual text on hours/phones/people; source line written by code.
- **Selftests** (`Ask Valley Pawn/selftest/`): run 1 15/18, run 2 16/18 (fixes: sub-section chunks, cite normalisation, FACT precedence); run 3 18/19, run 4 **19/19** (hedge guard + editorial-note instruction). All three agents loaded (launchctl shows ask-vp, ask-vp-capture, ask-vp-verify). The Goldilocks bot is not in #deal-questions, #loans-and-buys or #policy-announcements — capture reads the other nine until it is invited.
- **Capture + verify built** (`ask_vp_capture.py` nightly 22:05 `com.valleypawn.ask-vp-capture`; `ask_vp_verify.py` Mon 09:05 `com.valleypawn.ask-vp-verify`). Capture: Preston + manager messages (12 channels, threads with parent question) + new employee-call transcripts from the Zoom pipeline (runs `zoom_ingest.py --since <2 days> --limit 150`, local whisper) + one-time `Preston Time Review/transcripts` → `_raw_harvest/capture_<date>.md` → `kb_build --force`. `kb_build.py` amended (backup `.bak-pre-zoomcall-20261008`) to accept `SOURCE: zoom-call:<id> | date | store` — the one non-URL source form. Verify: parses Preston's numbered replies → `verified.json`; builds ≤10-item batch (queue + last week's NOT-FOUNDs); **posts to #preston-claude only when `verify_enabled: true`** (default false — writes `Ask Valley Pawn/verify/<date>.md` instead).
- **Roster**: `Zoom Call Pipeline/internal_roster.json` now has the five managers' cells + Joshua's (from hr/ROSTER.json = Gusto; 4 of 5 corroborated by the valley-pawn-context directory; backup `.bak-pre-managercells-20261008`). Store↔manager-cell calls now classify EMPLOYEE.
- Allow-list += ask_vp_corpus.py, ask_vp_responder.py/.sh, ask_vp_capture.py/.sh, ask_vp_verify.py/.sh (backup `.bak-pre-askvp-20261008`).
- **Found while testing**: P&P v2026.8 §01.01 and Handbook "Hours of Business" still show pre-10/1 hours (no Roanoke Wednesday, no Saturday 5 PM) → Open Items row for the policy flow. The channel answers from the store-facts layer meanwhile.
- Nothing posted to any team channel. No DM sent (shadow DMs only fire on a real question in the channel).

## Refresh cadence (how fast new knowledge reaches an answer)
| Source | Refresh | Answerable when |
|---|---|---|
| P&P / Handbook | new FINAL file in Human Resources/ → next run (≤15 s) | immediately |
| Store facts | edit `facts/store_facts.md` → next run | immediately |
| Preston / manager answers in Slack | nightly 22:05 capture | next morning, quoted + dated (HIGH); Preston confirms Monday |
| Employee calls (Preston's line, store↔manager) | nightly 22:05 (Zoom pull + local transcription) | next morning, same tiering |
| Academy lessons | on file change | immediately |
| Spot price (melt math) | 07:00 daily (existing agent) | same day |
| Texts / store email ("how we answer customers" bank) | NOT BUILT YET (week 3) — manager-approved weekly | after approval |

- 2026-10-08 17:35 — Joshua created **#ask-goldilocks** (C0C809Q2JDS). Responder `config.json` channel repointed; capture list += the new channel; #ask-handbook stays readable until launch, then retired. Goldilocks must be invited to #ask-goldilocks for the shadow test to see questions there.

## 2026-10-08 (night) — v2 CONVERSATIONAL (Joshua: "we want this to be conversational")
- Goldilocks now replies **in a thread under the question in #ask-goldilocks** and keeps the conversation going: every follow-up in that thread ("what about 10k?", "what do I say to him?", "what's step 2?") is answered with the thread history; follows a thread for 24 h; steps back when Preston or a store manager replies in the thread (their answer is captured that night).
- Voice rewritten: talks like the company's most experienced coworker; can greet / thank (chat), ask one short question back when the answer depends on it (clarify), offer the obvious next step. Facts still only from the corpus; chat/clarify replies are blocked from carrying numbers or rules.
- Typos: unknown words trigger a quick spelling fix before search ("role wqcthes" → Rolex watches → Academy L8-02).
- Model call: claude-sonnet-5-5 refuses forced tool_choice (HTTP 400), so replies come back in a labelled STATUS/CITES/TOPIC/REPLY format parsed in code; one automatic retry when the model refuses while answerable passages exist.
- 3 passes per 15-s launch → a message is seen within ~5 s; replies land in ~5–10 s.
- Live gate: `config.json` `live_users: [Joshua]` → Joshua gets real in-channel replies now; anyone else still gets shadow (DM to Joshua) until `mode: LIVE`.
- DMs to Goldilocks: code built, OFF — the bot token lacks im:read/im:history (`dm_disabled: missing_scope`). Threads in the channel cover the conversation; DMs light up automatically if those scopes are ever added.
- Selftest 25/25 (incl. 4 follow-up turns, greeting, thanks). Replayed Joshua's 18:33 "do we take role wqcthes?" → answered in-thread from Academy L8-02.
- Deploy note: device_commit_files can deliver a stale copy when the same staged path is reused — always commit from a fresh path (`outputs/deploy/v<epoch>/`). `fleet/state/ask_vp/replay.txt` (one ts per line) makes the agent re-answer specific messages.

## 2026-10-09 — concise voice + Layer 7 industry knowledge (Joshua: "more concise… don't reference Preston"; "we may want to layer in some base pawn industry knowledge")
- Voice: answer first, 1–3 sentences, ≤4 steps; no quotes, no "Preston said", no dates; source line plain ("Valley Pawn practice", "P&P §…", "Academy L5-02: …", "general pawn know-how").
- **Layer 7 `Ask Valley Pawn/industry/pawn_industry_baseline.md`** (12 passages, trust INDUSTRY, lowest precedence): what pawn shops take; Rolex/luxury watch authentication + comping; gold/silver/platinum stamps; trading cards (Pokémon/sports/PSA); autographs; electronics; power tools; instruments; firearms general; deal basics. Never sets pay %/loan/approval; Valley Pawn's own "we don't take" rules win. Retrieval always gives 2 industry passages a seat when they match.
- `facts/ebay_rules.md`: Joshua's four eBay hard rules (9/17).
- Parallel answering (up to 6 at once) for busy mornings.
- Corpus now 546 passages (policy 224, Preston/practice 251 — nightly capture added 32 — Academy 54, facts 5, industry 12). Selftest **35/35** incl. Rolex, Pokémon, autographs, cell phones (correctly "no"), 585 stamp, Gibson, eBay Best Offer. Replayed Joshua's Pokémon question in-thread.

## Open — only Joshua
1. DONE 10/8 — Joshua created #ask-goldilocks (C0C809Q2JDS); responder repointed. Staff get added at launch.
2. Approve the demo announcement (DEMO_PLAN.md) before Fri 10/16.
3. Say the word and the Monday batch to Preston goes live (`verify_enabled: true`) — it is one Slack message a week to him, ≤10 items.
4. Flip to LIVE after the shadow period (`mode: LIVE`).
