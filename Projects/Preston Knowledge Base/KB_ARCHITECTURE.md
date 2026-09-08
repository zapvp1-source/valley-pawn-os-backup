# Valley Pawn Ops Agent — Architecture

**Created:** 2026-09-07 · **Domain:** 1 (Full Circle Finance Inc DBA Valley Pawn)
**Scope:** OPERATIONS ONLY — gold, silver, coins, diamonds, jewelry, watches, scrap,
deal judgment, store procedure. **NOT** financial statements, NOT bookkeeping, NOT QBO,
NOT payroll. Those stay where they are.

---

## The goal, restated

> "If they ask Preston about it, we should gather it, put it in a knowledge database,
> and be able to ask that same question without Preston's involvement and get the same
> or similar answer."

So the system has to do four things, in this order:

1. **Gather** what Preston knows.
2. **Verify** it is actually right and still current.
3. **Answer** from it, without him.
4. **Keep gathering** as he keeps deciding things, forever, without adding work to his day.

Most "build an expert bot" projects die at step 1 because they start with a blank page
and an interview request. This one does not have that problem — see below.

---

## The finding that shaped the design

**Preston's knowledge is already written down.** He has been answering deal questions in
Slack since 2022, in writing, with numbers. A 2026-09-07 sweep of the Joshua↔Preston DM,
the five `*-funds` channels, `#deal-questions`, `#loans-and-buys`, `#general`,
`#scrap-rankings`, `#policy-announcements` and `#preston-claude` pulled **219 sourced
knowledge entries** on the first pass — his melt formula, his pay-percentage bands, his
counterfeit tells, his stone-weight rules, his refiner terms, his testing sequence.

That changes the project from *"interview Preston for 40 hours"* to *"harvest, then have
him confirm."* His time cost drops from weeks to roughly **ten minutes a week**.

It also means the risk profile is different from a normal wiki. The material is real and
specific — 55% of melt, 85% closeout, 15% of watch weight, I1→I2 halves the value. Those
numbers are worth money when right and cost money when wrong. So the whole design is
built around **provenance and refusal**, not around coverage.

---

## The four hard design decisions

### 1. Entries with provenance — never a summarized wiki

Every entry is a quadruple: **claim + Preston's verbatim words + Slack permalink + date**.
An entry missing the quote or the permalink is *dropped by the build script*, not
published. There is no such thing here as a rule nobody can trace.

Why: a summarizing LLM asked to "write up what Preston knows about gold" produces
plausible, fluent, unsourced numbers. On a $20,000 gold lot that is not a documentation
problem, it is a loss. The verbatim quote is what makes a wrong answer *visible* — a
store manager reading "Preston's rule, 2026-01-29: *'we are only paying 50% for all
bullion and silver'*" can judge for themselves whether that still holds. A paraphrase
gives them nothing to judge.

### 2. Tiered trust — the agent answers from some entries and refuses from others

| Tier | What it means | What the agent may do |
|---|---|---|
| **VERIFIED** | Preston personally confirmed it | Answer. Cite it. |
| **HIGH** | He stated it as an explicit rule, in his own words | Answer, but **always** quote him + the date |
| **MEDIUM / LOW** | A judgment on one specific deal | **Never** answer. Surface as context only: "he hasn't set a rule; closest thing he said was…" |
| **SUPERSEDED** | Replaced by a newer rule | Never answer. Point at the replacement. |

Why not "verified only": on day one nothing is verified, the agent is useless, nobody
uses it, and Preston is asked to bulk-approve 219 entries before it earns anything. That
project dies in week two. Starting at HIGH-with-attribution makes it useful immediately
while keeping every answer auditable.

Why not "answer from everything": a one-off call on one ring becomes a standing rule.
That is exactly how a knowledge base starts lying.

### 3. Conflicts publish as conflicts — the build never picks a winner

Preston has said the estimator is at 55%, and at 50/55 loan/buy, and that 65–70% was
acceptable on a falling-gold morning, and that the public calculator assumes 50%. Those
do not reconcile. **All of them publish, with the conflict flagged.** The agent's answer
to a conflicted question is "there are two different answers on record, here they are,
this one needs Preston." Averaging them, or silently preferring the newest, would
manufacture a number Preston never said.

This is Rule 18 (*withhold, don't caveat*) applied to knowledge instead of to reports.

### 4. Generated, never hand-edited

`KB_CURRENT.md` is built by `kb_build.py` from the raw harvest plus `verified.json`, and
rebuilt at the top of **every** responder run. Same contract as
`Human Resources/Ask_Handbook/build_sources.py` — a corpus that can go stale while still
being cited confidently is the single worst failure this class of system produces. If the
build fails, the responder stops rather than answering from a possibly-stale file.

---

## The pieces

```
Preston Knowledge Base/
├── KB_ARCHITECTURE.md      this file
├── kb_build.py             generates the corpus; --queue emits the next verify batch
├── _raw_harvest/*.md       raw sourced entries (append-only; capture task adds here)
├── verified.json           Preston's rulings: verified / corrected / superseded / rejected
├── KB_CURRENT.md           GENERATED. The only thing the agent may answer from.
├── QUESTION_LOG.md         every question asked + outcome. NOT-FOUND rows = the gap list.
└── PRESTON_ASK.md          the short list of what actually needs to come from him
```

**Three scheduled tasks:**

- `vp-ops-agent-responder` — watches the ask channel, rebuilds the corpus, answers with
  citations, refuses on gaps, logs every question.
- `preston-knowledge-capture` — nightly. Reads what Preston said in the last 24h across
  the deal channels, extracts new candidate entries, appends to `_raw_harvest/`.
  **Zero effort from Preston.**
- `preston-knowledge-verify-weekly` — one Slack message a week, ≤10 entries, each a
  yes / no / fix. Writes his answers into `verified.json`.

---

## How the flywheel actually works

1. Someone asks a deal question in the channel.
2. Agent answers **if and only if** the KB covers it — with Preston's words and the date.
3. If it does not cover it → agent says so plainly and routes to Preston. That refusal is
   logged as a NOT-FOUND.
4. Preston answers in the channel (as he does today).
5. The nightly capture turns his answer into a candidate entry.
6. The weekly batch asks him to confirm it.
7. Next time, the agent answers it.

Preston's load goes **down** every week, and every escalation he still gets is by
definition a real gap. The NOT-FOUND log is the interview list — it tells us exactly what
to ask him, instead of guessing.

---

## What this system must never do

- Never compute a specific dollar offer on a live deal and present it as approved. It may
  show the melt **math** and the pay-percentage band Preston has stated. The approval is a
  human decision.
- Never answer a valuation question from general pawn knowledge or from the internet.
- Never touch financials, P&L, QBO, payroll, or anything in the Real Estate or Personal
  domains. Out of scope by design.
- Never blend two conflicting entries into one number.
- Never post system/tool names, file paths, or entry IDs into a team channel
  (Field Communication Standard v3).

## PHASE 2 (identified 2026-09-07, not built) — the recorded phone calls

**Zoom Phone automatic call recording has been ON company-wide since 2026-08-21**, inbound and
outbound, with retention set to keep indefinitely (`Valley Pawn OS/ZOOM_PHONE.md`). Live lines:
**Harrisonburg (ext 802), Waynesboro (803), and Lexington (807)** — Lexington too, which is easy to
miss. Culpeper and Roanoke are still on Verizon and record nothing.

This matters because **phone was the one unrecoverable channel** this whole design was working
around. Preston's own escalation rule is *"call Josh, call Hillary, then call me if no response"* —
so the deal judgments that never make it into Slack are happening on a line that is now recording.

### The scoping rule — employee calls only, never customer calls

The recordings are overwhelmingly **customer** calls ("do you have any PS5s"). Those must stay out
of this knowledge base:

- They are dense with customer PII — names, numbers, what someone is pawning and why they need the
  money. A base that store staff can query must never contain that.
- The knowledge isn't in them. A customer asking a price teaches us nothing about how Preston prices.

**Mine only employee-to-employee calls** — store↔Preston, store↔store-manager. That is where the
judgment lives, and it sidesteps the customer-privacy problem entirely rather than trying to filter
it after the fact. Employees already know these lines are recorded (that was the stated basis for
disabling the outbound announcement on 2026-08-26).

Customer calls are a genuinely valuable *separate* project — what customers ask for, what we turn
away, where sales are lost. Different system, different privacy design. **Do not merge the two.**

### Provenance under the no-permalink problem

A call has no Slack permalink, which the build script requires. The rule for call-sourced entries:

- `SOURCE` cites the Zoom call ID + date + which extension, not a URL. `kb_build.py` needs a small
  amendment to accept that form (it currently requires `http` in SOURCE — deliberate; change it
  knowingly, don't loosen the check generally).
- `VERBATIM` is a tight quote of **the rule being stated**, by Preston or a manager. Never a
  customer's words, never a name, number, or item tied to a person.
- The audio itself stays in Zoom under existing access control. It is never copied into this folder.

### What the build needs

- A **Zoom Server-to-Server OAuth app** with `phone_recording:read:admin` — turns this into a
  headless pipeline instead of driving the admin web UI in Chrome. ~5 minutes for Joshua in the Zoom
  marketplace; credentials go in `~/.vp_secrets/zoom_s2s.json`.
- **Whisper running locally** on the Mac Studio (`brew install whisper-cpp`; ffmpeg is already
  present). Local matters — no call audio should leave the machine.
- A targeting filter so only calls to/from Preston's and the managers' numbers get transcribed.
  Transcribing every call is both wasteful and the privacy problem restated.

### One thing worth a lawyer's glance, once

The inbound announcement says calls may be recorded *"for quality assurance and training purposes."*
Building an internal training knowledge base is a defensible reading of that. But persisting derived
transcripts indefinitely is a larger data footprint than recordings sitting in Zoom, and outbound
calls carry no announcement at all (a considered decision on 2026-08-26 — VA one-party consent,
staff informed). Flagging once for counsel; not re-opening a settled decision.

## How to extend

New topic area → add a prefix to `SECTIONS` in `kb_build.py` and run a harvest agent
against those channels with the same entry format. Never hand-write into `KB_CURRENT.md`.
A rule change → add a `verified.json` row marking the old entry SUPERSEDED and pointing at
the new one. The old entry stays visible so nobody re-harvests it back in.
