# Valley Pawn Ops Agent — Question Log

Every question the ops agent was asked and how it was handled.

**The NOT-FOUND rows are the most valuable thing in this file.** They are the list of
things Preston knows that the knowledge base does not have yet — the interview list,
written by real questions from real stores instead of guessed at in advance. Reviewed
weekly and fed into the verification batch.

| When | Asker | Store | Question | Outcome |
|---|---|---|---|---|
| 2026-09-07 12:00 | BUILD TEST | — | What is the melt formula for 14k gold? | ANSWERED melt-formula-gold (HIGH) |
| 2026-09-07 12:00 | BUILD TEST | — | What percent of melt do we pay on bullion and silver? | ANSWERED pay-percentage-bullion-silver (HIGH) |
| 2026-09-07 12:00 | BUILD TEST | — | Customer has a gold ring with small diamonds going to scrap — do I pay for the stones? | ANSWERED scrap-rings-do-not-pay-for-diamonds (HIGH) |
| 2026-09-07 12:00 | BUILD TEST | — | What is the estimator set at right now? | CONFLICT SURFACED (50/55 vs 55 vs 65-70) — correctly refused to pick one |
| 2026-09-07 12:00 | BUILD TEST | — | What is the Wi-Fi password at Culpeper? | NOT-FOUND (correct — out of scope, routed to Store Manager) |
| 2026-09-07 12:00 | BUILD TEST | — | What was our net revenue last month? | OUT-OF-SCOPE (correct — financial data, not this agent) |

## Outcome codes

- `ANSWERED <entry-id> (<tier>)` — answered from the knowledge base with a citation.
- `CONTEXT-ONLY` — only MEDIUM/LOW material existed; surfaced as context and routed to Preston.
- `CONFLICT SURFACED` — two entries disagreed; both shown, no winner picked, routed to Preston.
- `NOT-FOUND` — the knowledge base does not cover it. **Goes on the interview list.**
- `OUT-OF-SCOPE` — financial / HR / personal / real-estate. Not this agent's job.
