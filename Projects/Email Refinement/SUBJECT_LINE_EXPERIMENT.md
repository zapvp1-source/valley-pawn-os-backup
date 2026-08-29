# Valley Pawn — Subject Line Experiment (sequential A/B)

**Started 2026-08-24.** Owned by the `brevo-weekly-efficiency-audit` task (Fri 8 AM).

## Why this is sequential, not a real split test

Brevo's in-send A/B test cannot be fully configured through the API. `abTesting`,
`subjectA`, `subjectB` and `splitRule` all persist via `PUT /emailCampaigns/{id}`,
but **`winnerCriteria` and `winnerDelay` silently do not** — the API returns 204,
then reads back `None`. They appear to be UI-only fields, the same way contact
segments are UI-only on this plan.

Shipping a half-configured A/B test is dangerous here: with a split rule set but
no winner criteria or delay, it is unclear whether Brevo ever sends the remaining
50%. Given the entire point of this project is that *people are not getting our
emails*, a config that might silently drop half a send is not acceptable. So the
A/B flag was reverted on campaign 54 and the test restructured as a sequential
one, which needs no UI and carries no delivery risk.

If someone is ever logged into the Brevo web UI, converting this to a real
in-send split test is a genuine upgrade — the sequential version is confounded by
week-to-week variation in content, season and audience wave.

## The hypothesis

From the 2026-08-22 audit: subject lines carry no number, no deadline and no
concrete value proposition ("What's new at Valley Pawn Roanoke"), and the **logo
out-clicks every offer on nearly every send** — the signature of an offer too weak
to beat idle curiosity.

> **H1 — Concrete beats generic.** A subject naming a specific number, price,
> deadline or object will out-click a generic "what's new / here's our store" subject.

## Measurement rules

- **Score on clicks, never opens.** 481 of 624 "opens" on the Aug 1 blast were
  Apple MPP prefetches. Optimising on opens optimises on bots.
- Use **per-link `linksStats`**, not `globalStats` — `globalStats` reported 193
  clickers on 142 delivered for W8, which is impossible. Per-link counts are the
  only trustworthy figure in this account.
- Primary metric: **calls + texts per 1,000 delivered** (sum of `/c/` and `/t/`
  link clicks ÷ delivered × 1000). Secondary: total link clicks per 1,000.
- **Do not call a winner before 6 sends per style.** The audit found the Friday
  social loop moving the whole content mix on n=8 with single-digit engagement —
  do not repeat that mistake here.

## Assignment

Alternate styles on consecutive weekly sends. CONCRETE on even ISO weeks,
GENERIC on odd, so seasonality spreads across both arms rather than clustering.

| Send date | Campaign | Style | Subject |
|---|---|---|---|
| 2026-08-27 | 28 | CONCRETE | Our Lexington store moved — 125 Walker Street |
| 2026-09-03 | 29 | CONCRETE | Every item we sell is covered for 30 days. Every one. |
| 2026-09-10 | 54 | CONCRETE | 5 things worth the drive to our Roanoke store |
| 2026-09-17 | 55 | CONCRETE | Christmas layaway is open. No fees, no interest, no credit check. |
| 2026-09-24 | 56 | CONCRETE | Generators, chainsaws and pressure washers — before you need them |
| 2026-10-01 | 57 | GENERIC | What's on the shelves at our James Madison Highway store |
| 2026-10-08 | 58 | CONCRETE | The five things people put on layaway most |
| 2026-10-15 | 59 | CONCRETE | We weigh your gold in front of you, against live spot |
| 2026-10-22 | 60 | GENERIC | What's new at our West Broad Street store |
| 2026-10-29 | 61 | GENERIC | Costume week, and a reminder about Christmas layaway |
| 2026-11-05 | 62 | GENERIC | What's on the floor at our East Market Street store |
| 2026-11-12 | 63 | — | *excluded — Veterans Day, community-only, zero CTA* |
| 2026-11-19 | 64 | CONCRETE | The math: layaway vs putting Christmas on a card |
| 2026-11-26 | 65 | GENERIC | Happy Thanksgiving — and Saturday is our day |
| 2026-12-03 | 66 | GENERIC | Gift ideas from our Walker Street store |
| 2026-12-10 | 67 | CONCRETE | Real gold, real diamonds, not-retail prices |
| 2026-12-17 | 68 | CONCRETE | Layaway pickup deadline is Sunday, December 20 |
| 2026-12-24 | 69 | — | *excluded — Christmas, community-only* |
| 2026-12-31 | 70 | CONCRETE | Start the year with cash for the gold you never wear |

Current staged mix is CONCRETE-heavy (10 vs 6). That is deliberate — the audit's
read is that generic subjects are the incumbent failure mode, so the experiment
is weighted toward the challenger while keeping enough GENERIC sends to compare
against. If CONCRETE wins clearly by December, retire GENERIC entirely.

## Running tally

*(the weekly audit appends one row per send here)*

| Date | Campaign | Style | Delivered | Link clicks | Calls+texts | per 1,000 |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |
| 2026-08-27 | 28 | CONCRETE | 169 | 2 | 2 | 11.83 |

## Confounders to keep in mind

- Audience size changes: Aug 27 and Sep 3 go to the engaged list only (~172);
  Sep 10 onward adds a rotating wave (~2,300); Oct 1 onward doubles to two waves
  (~4,400). **Always compare rates, never raw counts.**
- Sender identity changed to `hello@thevalleypawn.com` on 2026-08-24. Sends before
  and after that date are not comparable on deliverability.
- The duplicate SPF record was fixed 2026-08-24. Everything sent before that
  carried a failing authentication leg, so pre-fix engagement is a floor, not a
  baseline.
- Christmas layaway and gold sends have intrinsically different intent than a
  store spotlight. Style is only one variable among several — treat the result as
  directional evidence, not proof.
