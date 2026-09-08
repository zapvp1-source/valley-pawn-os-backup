# Customer Call Analysis — what the phone is telling us

**Created:** 2026-09-07 · **Domain:** 1 (Full Circle Finance Inc DBA Valley Pawn)
**Source:** `Projects/Zoom Call Pipeline/out/customer/*.jsonl` — structured records only.
**Publishes to:** `#call-insights` (Slack) — its own channel, separate from everything else.

Completely separate from the Preston Knowledge Base: different data, different channel, different
audience, different privacy rules. The two share only the ingest layer. Neither reads the other's
output.

---

## What this answers that nothing else does

Valley Pawn currently measures what customers **did** — every KPI comes out of Bravo, which by
definition only sees completed transactions. The phone is the one place we can hear what customers
**wanted** and didn't get. Five questions worth real money:

1. **What are people asking for that we don't have?** Forty calls a month asking for PS5s is a
   buying instruction, and today it is invisible — no Bravo report can show a sale that never
   happened.
2. **What are we turning away?** Every "we don't take that" is either a correct policy call or lost
   margin. Right now nobody knows the ratio or the mix.
3. **Is the qualifying script actually being used?** Preston's rule (#general, 2026-02-02) is three
   questions *before* looking anything up — prior business, loan vs sell, how much they need. Whether
   that happens has never been measurable.
4. **Are we presenting buy above pawn?** Also Preston's rule, also unmeasurable until now.
5. **How much of our inbound volume is spam?** The 8/21 call-log review found 7 of 11 answered
   Lexington calls were ≤15 seconds and looked like neighbor-spoofing robocalls. If that pattern
   holds, staff are being interrupted dozens of times a day and the "missed call" numbers are
   partly fiction.

Only 3 of 5 stores are on Zoom Phone (Harrisonburg, Waynesboro, Lexington). Culpeper and Roanoke
are still on Verizon, so **every figure here covers 3 stores, not 5.** Say so on every publish —
never present a 3-store number as a company number.

---

## Privacy: this system never sees a customer's words

By the time anything reaches this project, the transcript is already gone. The pipeline reduces each
customer call to a record with no name, no number, no quote, no identifier:

```json
{"date":"2026-09-08","store":"HAR","direction":"inbound","duration_s":94,
 "intent":"item_availability","category":"gaming_console","item":"PS5",
 "outcome":"not_in_stock","qualifying_questions_asked":false,"spam":false}
```

That is the entire input. It is enough to answer all five questions above and it cannot leak a
customer. **Never add a "sample quotes" section to this report** — the quotes do not exist, and
recreating them would defeat the design.

## The staff-performance rule — this is a management tool, handle it like one

Two of the five questions are about whether employees follow procedure. That is a legitimate use —
it is literally the "quality assurance and training purposes" the recording notice states. But how
it is published decides whether it helps or poisons the well:

- **Aggregate patterns → `#call-insights`.** "Qualifying questions were asked on 34% of loan/buy
  calls" is a coaching signal for the whole company.
- **Individual performance → Preston, privately. Never a channel, never a name in `#call-insights`.**
  Naming an employee's call stats in a room their coworkers can read is how you get staff who resent
  the phone system, and it converts a coaching tool into a surveillance one.
- **Never rank employees by call metrics, and never feed these numbers into bonus qualifiers.**
  Transcription is imperfect, call mix is not evenly distributed, and the moment a number affects
  someone's pay, people optimize the number instead of the customer.

## Cadence

**Weekly, Monday.** Not daily — daily call volume is noisy and a daily post trains people to ignore
the channel. The demand signal ("we keep getting asked for X") only becomes trustworthy at a week's
volume anyway.

Monthly, a longer cut goes into the CEO scorecard's Operations block rather than its own post.

## What a weekly post looks like

```
📞 Phone — week of Sep 1  (Harrisonburg, Waynesboro, Lexington)

412 calls · 71% answered · 24% spam

Most asked about
• Gaming consoles — 38 calls, we had none 29 times
• Gold buying — 31 calls
• Tools — 22 calls, we had none 14 times

Turned away 44 times — mostly cell phones (18) and TVs over 65" (9)

Qualifying questions asked on 34% of loan/buy calls
```

Plain language, one takeaway, under ~100 words (Field Communication Standard v3). No system names,
no file paths, no employee names, no customer anything.

## Rule 18 applies

If a week's ingest is incomplete — a store's line was down, transcription failed on a chunk of
calls, the pipeline missed a day — **publish nothing** rather than a partial week presented as a
whole one. A wrong demand signal sends real money at the wrong inventory. Silence, then a note in
the run log.

## Layout

```
Call Analysis/
├── CALL_ANALYSIS_ARCHITECTURE.md   this file
├── analyze_week.py                 reads the pipeline's customer records -> weekly rollup
├── weekly/<YYYY-MM-DD>.json        each week's computed numbers, kept for trend
└── pending-tasks/                  staged scheduled task (registration blocked, see below)
```

## Status

**NOT RUNNING.** Blocked on the same two things as the Preston KB Phase 2: the Zoom
Server-to-Server OAuth credentials, and local Whisper. Once ingest produces its first
`out/customer/*.jsonl`, this side needs only the weekly task registered and the `#call-insights`
channel created.
