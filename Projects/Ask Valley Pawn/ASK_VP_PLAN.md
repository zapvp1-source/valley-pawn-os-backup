# Ask Valley Pawn — the company brain in Slack (Plan v1, 2026-10-08)

**Domain:** 1 — Full Circle Finance Inc DBA Valley Pawn · **Owner:** Joshua · **Answers as:** Goldilocks (the existing reports bot) · **Built/run by:** automation on the Mac Studio
**Joshua's ask (10/8):** one agent, living in a Slack channel, that answers in real time anything about Valley Pawn for any team member or Preston — built from the training material, the P&P/handbook, the recorded store phone lines, texts and emails, and Preston's recorded Zoom line; siloed to Valley Pawn only; and, where it can, *does things* for the team. Then a real-world demo to the team.

---

## 1. The one-paragraph version

Every store already has a channel for this (#ask-handbook, created 8/22; 13 people joined that day incl. Preston and the five managers — the three September hires are not in it yet and get added at launch) and nobody has ever asked it a question — because it answered policy only, 30 minutes late, from one document. The plan replaces that with **one real-time responder in that same channel** that answers from six layers of our own material (policy, Preston's rules, the Academy lessons, call-derived rules, the "how we answer customers" bank, and store/system facts), cites where every answer came from, refuses and routes to a human when it is not covered, and can take a growing list of safe actions. Everything it learns comes from what Preston and the managers already say and do every day — in Slack, on the recorded lines, in texts and email — so his time cost is ten minutes a week confirming entries, not hours writing them.

---

## 2. What already exists (verified today, not assumed)

| Piece | State | Reuse |
|---|---|---|
| `#ask-handbook` C0BS11KTYKU | Public, 13 members since 8/22 (Sept hires not yet added), **zero questions ever asked**. Responder `ask-handbook-responder` (30-min poll) DISABLED 9/18. | **Yes — this becomes the channel.** |
| `Human Resources/Ask_Handbook/build_sources.py` → `SOURCES_CURRENT.md` | Working. Rebuilds from the highest-numbered `*_FINAL.docx` P&P + Handbook, 194 KB of cited sections. | Layer 1, as-is |
| `Preston Knowledge Base/` — 219 sourced entries (claim + Preston's verbatim words + Slack permalink + date), tiers VERIFIED/HIGH/MEDIUM/SUPERSEDED, `kb_build.py`, `verified.json` | Built 9/7. The three tasks (responder, nightly capture, weekly verify) were **staged but never registered** (classifier block). MODE = SHADOW. | Layer 2, as-is + the capture/verify loop finally switched on |
| `Training Program/academy/` — 54 Academy lessons (slides, key points, scenario tests, voiceover), huddle inputs, OPEN_ITEMS (114 open questions, 90 for Preston) | Built, loaded in TalentLMS, not launched to staff | Layer 3 (lesson text is the best-written explanation of every procedure we have) |
| `Zoom Call Pipeline/` — pulls every Zoom Phone recording, transcribes **locally** (whisper-cpp small.en), classifies EMPLOYEE vs CUSTOMER by `internal_roster.json`, keeps employee transcripts, reduces customer calls to non-identifying records | Working; 793+ calls processed; Culpeper on Zoom since ~9/28; **Preston's own Zoom line (540) 202-4200 / ext 813 live and in the roster since 10/6**; 5 store↔Preston transcripts in `Preston Time Review/transcripts/` | Layer 4 source |
| `Call Analysis/` — weekly phone+text review, 368 calls read for Sep 21–27, conduct review, best-calls, POLICY_GAPS_top5 | Working by hand (`bin/call_week_review.py`) | Layer 4 + Layer 5 source |
| Chekkit API (`bin/chekkit_api.py`, per-store tokens) and the five store Gmail mailboxes (alive, ~64k messages, read natively via Apple Mail) | Working | Layer 5 source |
| `valley-pawn-context`, `vp-ops-knowledge`, `ZOOM_PHONE.md`, Goldilocks report catalog (Academy L1-07) | Current | Layer 6 |
| `bin/vp_ai.py` + Claude API key in Keychain (`vp-agent-anthropic-key`); Goldilocks bot token on the Mac; host job queue; launchd fleet (81 native agents, fleet-guardian, Mac-first plan 10/7) | Working | The runtime |

Nothing here is rebuilt. The new thing is the **responder + the assembler that stacks the six layers into one corpus**, and the loop that keeps it growing.

---

## 3. The decision: how it runs (expert-board recommendation, not a menu)

**Build it as a native, always-on responder on the Mac Studio — not as Claude Tag (Claude's own Slack app).**

Why not Claude Tag, checked against Anthropic's own docs today: it needs a Team/Enterprise plan and usage credits; "answer only from company material" is a prompt-level instruction there, not an enforced control; memory saved from a public channel leaks into every other channel; it cannot reach anything on the Mac (spot prices, the P&P build, Preston's corpus, Bravo data, the host queue); it is still public beta; and every answer bills the org balance. For a counter clerk asking "do I pay for the stones in a scrap ring?", a wrong fluent answer from general knowledge is the one failure we cannot have. Keep Claude Tag as a *later* option for Joshua/Preston's own working channel — not for the floor.

The native responder instead:
- **Real time.** A persistent process (launchd, KeepAlive) polls the channel every 15 s with the Goldilocks bot token already on the Mac — no new credentials, no hourly cloud limit. (Slack Socket Mode is a later upgrade if we ever want sub-second; it needs one app-level token from Joshua.)
- **Siloed by construction.** The model only ever sees retrieved passages from `ASK_VP_CORPUS.md`; the answer must cite entry ids; a post-check drops any answer that cites nothing. No web, no general knowledge, no memory outside the corpus. If retrieval finds nothing above threshold, it refuses and routes — before the model is even called.
- **Consistent.** Same corpus, same rules, same voice for all five stores. Corpus rebuilt at the top of every run from the source files; if the build fails, it stops rather than answer stale.
- **Fits the fleet.** Same patterns as every other native agent (receipts, ledger, fleet-guardian liveness, Rule 16 silence on failure, Field Communication Standard v3 on every post).

---

## 4. The six knowledge layers (what it answers from)

| # | Layer | Source → builder | Trust / how it's cited |
|---|---|---|---|
| 1 | **Policy** — P&P Manual + Employee Handbook (current FINAL versions, auto-picked by version number) | `Ask_Handbook/build_sources.py` (existing) | Quotes the section: "P&P Manual §05.01" |
| 2 | **Preston's rules** — melt formula, pay bands, counterfeit tells, stone rules, refiner terms, testing sequence, deal judgment (219 entries, growing) | `Preston Knowledge Base/kb_build.py` (existing) | VERIFIED → answer; HIGH → answer + his words + date; MEDIUM/LOW → context only, route to Preston; conflicts → show both, never pick |
| 3 | **Academy lessons** — 54 lessons: the plain-English "how we do it" for every procedure, with the P&P section each cites | NEW `academy_extract.py` reads `academy/lessons/*.json` → key points + "say" lines | "From the Academy, lesson 3.4 — Writing the ticket" |
| 4 | **Call-derived rules** — what Preston and the managers *tell staff* on recorded employee-to-employee calls (store↔Preston on his new Zoom line, store↔store) and in Slack answers | Zoom pipeline `out/employee/` + `Preston Time Review/transcripts/` + the nightly Slack capture → candidate entries in `_raw_harvest/` → Preston confirms weekly | Same tiers as Layer 2; SOURCE = call id + date + extension (kb_build amended to accept it) |
| 5 | **"How we answer customers" bank** — the best real manager replies by phone, Chekkit text and store email (quote-or-capture, firearm on the phone, layaway terms, what we don't take), **customer identifiers stripped, approved by the manager who wrote it** | NEW `answer_bank_build.py` over Chekkit API + store mailboxes + `Call Analysis` best-calls; weekly batch to the manager: keep / fix / drop | "How Walker answered this at Harrisonburg (approved 10/14)" |
| 6 | **Store & systems facts** — hours, phones, addresses, who manages where, what Goldilocks posts and when, Zoom/Chekkit/Academy how-tos, holiday schedule | `valley-pawn-context`, `ZOOM_PHONE.md`, `hr/ROSTER.json`, Academy L1-07, Goldilocks catalog → NEW `facts_build.py` | Plain answer, source noted |

**Customer calls never enter the corpus.** They stay where they are today: reduced to non-identifying records for the weekly #call-insights demand/service report, and used to pick *training* examples. The employee/customer split is the privacy boundary and it fails closed (unknown number = customer).

**What makes Layer 4 real now:** until 10/6 the employee-call vein was almost empty (1 of 793 calls) because managers called Preston's cell. Preston's calls now go out on his Zoom line and the stores are told to call (540) 202-4200, so store↔Preston judgment is finally on a recorded line. One remaining gap — manager cell numbers are still blank in `internal_roster.json` — is one Slack ask to Preston (he has them); nothing else is needed.

**Texts and email:** read-only through the Chekkit API and Apple Mail. Only *manager/staff* replies are candidates for Layer 5; customer messages are context for the reviewer and are never stored.

---

## 5. Answer rules (binding — these are what make it trustworthy)

1. **Corpus only.** Retrieval first; the model sees only retrieved passages; the reply must cite entry ids; uncited replies are dropped. Never the internet, never general pawn knowledge.
2. **Withhold, don't caveat (Rule 18).** Not covered → "That's not written down yet — ask [Store Manager / Preston]" and the question is logged as NOT-FOUND. No hedged answers to someone at a counter.
3. **Tiers decide what may be answered** (Layer 2/4 table above). Conflicts publish as conflicts and route to Preston.
4. **Never a dollar offer on a live deal.** Show the melt math (live spot from `spot_prices.json`) and the band Preston set; the approval is a human's.
5. **Out of scope → route, don't answer:** anyone's pay, schedule, discipline, PTO balance, a dispute (Store Manager → Preston); financials/books/P&L/QBO (Joshua); real estate/personal (never). Exceptions to policy cannot be approved by the bot.
6. **Field Communication Standard v3** on every post: plain language, no system/tool names, no file paths or ids, no meta-commentary, no signature. Attributing to Preston or a manager by name is correct.
7. **Thread etiquette:** reply in a thread under the question; if Preston or a manager already answered, stay silent (their answer becomes a capture candidate); never double-answer; one answer per question.
8. **Every question logged** (`QUESTION_LOG.md`: who, store, question, outcome). NOT-FOUND rows are the interview list.
9. **Rule 16:** failures are silent in Slack; detail to the run log; at most one plain DM to Joshua when only he can unblock.

---

## 6. What it can DO for the team (the actions catalog)

Phase A — read-only, ships with the demo:
- Cite and quote the exact policy section; hand over the link to the current P&P/Handbook PDF on request.
- Melt math on the spot: karat + weight → today's spot, melt value, the pay band Preston set (math shown, no offer).
- Store facts: hours (incl. the Wednesday/Saturday differences), phones, addresses, who the manager is, when Goldilocks posts what.
- Step-by-step procedure checklists (opening, closing, drawer count, 4473 flow, NICS delay/deny, receiving a transfer, layaway firearm, eBay listing/shipping) from the Academy + P&P.
- Escalate: tag Preston (or the store manager) in the thread with a one-line summary of the question so he doesn't have to read up.
- Log a policy gap for the monthly policy review (what was asked, who, store) — automatically on every NOT-FOUND.
- "What lesson covers this?" → the Academy lesson id/name (link once the Academy is live).

Phase B — writes, each behind a guardrail (within 2–3 weeks of launch):
- Draft a customer text reply in our voice for the clerk to paste into Chekkit (draft only; the clerk sends).
- Draft an eBay title/description from a description or photo, applying the four eBay hard rules.
- Put a supply request into #supply-request in the standard format (Tuesday prep picks it up).
- Flag a Handbook-vs-P&P contradiction to Joshua with both quotes (never answers the conflicted topic).
- Create a manager to-do (Apple Reminders) when the clerk asks "remind Chadd to…".

Phase C — systems (needs a key or a decision from Joshua, each one listed on HUMAN_QUEUE once):
- Academy progress ("what's my next lesson?") via the TalentLMS API (Grow plan API key).
- Manager-only lookups from Bravo exports already on disk (overnight data, never the live VM, never customer PII to a clerk).
- Gusto: routing only, never balances — stays out by design.

Everything in B and C posts nothing to a customer and moves no money; anything irreversible stays with a human.

---

## 7. The flywheel (how it gets smarter without anyone's time)

1. Question in the channel → answered with a citation, or refused and routed (logged NOT-FOUND).
2. Preston/manager answers in the thread as they do today.
3. **Nightly capture** (10 PM): new Preston/manager answers from the deal channels, the DM-free Slack set, and the day's employee-call transcripts → candidate entries with verbatim quote + source.
4. **Weekly verify** (Mon 9 AM): one message to Preston, ≤10 entries, yes/no/fix. Writes `verified.json`. Managers get the same for Layer 5 (their own replies only).
5. **Every run rebuilds the corpus** from all six layers. A verified entry is live within 15 seconds of the next question.
6. Monthly: NOT-FOUND list → policy review (what to write down) and Academy additions (what to teach).

Preston's cost: ~10 min/week. Managers: ~5 min/week. Joshua: nothing recurring.

---

## 8. Build order and timeline

| When | What | Done when |
|---|---|---|
| **Wk 1 (10/8–10/14)** | `Projects/Ask Valley Pawn/`: `corpus_build.py` (stacks layers 1–3 and 6 now; 4–5 when their builders land), `ask_vp_responder.py` (poll → retrieve → answer → cite-check → post), launchd agent `com.valleypawn.ask-vp` (KeepAlive), `QUESTION_LOG.md`, receipts/ledger hooks, fleet-guardian registration, SHADOW mode (answers go to Joshua's DM, nothing in the channel) | 50-question dry run from real field questions passes: every answer cited, every out-of-scope routed, every conflict surfaced |
| **Wk 2 (10/15–10/21)** | Team demo (see DEMO_PLAN.md) → flip to LIVE in the renamed channel; register nightly capture + weekly verify (native, not Cowork); Layer 4 builder reads employee transcripts; roster cells from Preston | First real questions answered in the channel; first verify batch to Preston |
| **Wk 3–4** | Layer 5 answer bank (Chekkit + email + best calls, manager-approved); Phase B actions; monthly NOT-FOUND → policy review hook | Managers approved first batch; two Phase B actions live |
| Ongoing | Phase C as keys arrive; Academy links at Academy launch; Claude Tag evaluated for Joshua/Preston only | — |

Additive only: nothing in `Ask_Handbook/`, `Preston Knowledge Base/`, `Zoom Call Pipeline/`, the Academy or any live agent is modified; the new project reads their outputs. `kb_build.py` gets one knowing amendment (accept call-id SOURCE), with a backup.

---

## 9. The only things that need Joshua (one list, surfaced once)

1. **Channel name.** Keep `#ask-handbook` or rename it `#ask-valley-pawn` at launch (membership carries over; rename is reversible). Default if silent: rename at launch.
2. **Approve the demo announcement** (draft in DEMO_PLAN.md) — nothing is posted without his OK.
3. **Later, optional:** Slack app-level token for Socket Mode (sub-second replies); TalentLMS API key (Phase C). Neither blocks launch.

Not needed from him: manager cell numbers (asked of Preston), Zoom (done 10/6), the Claude API key (already in Keychain), Chekkit/Mail access (already native).

---

## 10. What this must never do

Answer from anything but the corpus · compute an approved offer · put a customer's name, number, words or item in the corpus or a channel · answer HR/pay/financial/real-estate/personal · pick a winner between two of Preston's conflicting rules · post tool names, paths or ids to a team channel · message anyone about its own failures.
