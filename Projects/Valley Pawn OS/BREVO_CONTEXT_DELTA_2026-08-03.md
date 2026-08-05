# brevo-context — DELTA 2026-08-03

**Apply in Settings → Capabilities → brevo-context.**
Insert the section below into `## Email Requirements`, immediately **before** the existing
`### Don'ts` subsection. Nothing else in the skill changes.

Reason: Virginia's pay-transparency statute took effect 2026-07-01 and reaches marketing emails
that advertise openings, not just formal job boards. The `## Email Requirements` section had no
hiring rule at all. A programmatic guard already ships in `brevo_preflight.py`; this delta makes
a drafting session aware of the rule *before* it builds the campaign, rather than discovering it
at preflight.

---

### Hiring / recruiting emails — LEGAL REQUIREMENT (added 2026-08-03)

Any campaign that advertises an opening is a **job posting** under Virginia law, not just
marketing. Va. Code § 40.1-28.7:12 (effective 2026-07-01) applies to **every private employer,
with no size threshold**, and requires:

- A **good-faith wage or salary range** — or a single stated wage — in the email itself.
  Current approved range for Sales & Loan Associate / Representative: **$16.50–$21.50 per hour**.
  The CEO approves any change to that range (it is named in policy HR-2026-03 so it cannot drift
  informally).
- The same rule covers postings for **promotions and transfers**, including internal-only sends.

Exposure if omitted: $1,000 first violation / $5,000 subsequent (Attorney General action), plus a
private right of action for **$1,000–$10,000 statutory damages, or actual damages if greater,
plus attorney's fees**. A 15-business-day cure window applies after written notice.

**This is enforced automatically.** `Projects/Email Refinement/brevo_preflight.py` hard-fails any
campaign containing hiring language that states no wage figure, and the daily
`brevo-preflight-watchdog` runs the same check. It is deliberately **not** auto-fixed — where a
range belongs in prose is a judgment call, and inventing a number is worse than blocking the send.
If preflight fails on `paytransparency`, add the range to the body copy and re-run. Do not bypass.

Detection is tuned to avoid crying wolf: it triggers on **one** unambiguous hiring phrase
("we're hiring", "now hiring", "join our team", "open positions", "now accepting applications"),
or on **two** weaker signals together (a `/careers` link, "apply at/now/today", "send your
resume"). A bare `/careers` link in a footer does **not** trigger it on its own.

Related: never ask about an applicant's **pay history** in any channel — email, application form,
or interview. That half of the statute is the one most often missed, and it carries the same
penalty. Asking what compensation someone is *seeking* remains permitted.

---

## Verification record (2026-08-03)

- Ran live against real campaigns: **#51** (hiring, no range) → correctly **FAILS** on
  `paytransparency`; **#52** (non-hiring) → still **PASSES** clean, no regression.
- 10 unit cases covering false-positive and false-negative traps → 0 mismatches.
- Master template 48 confirmed to contain **zero** `/careers` references, so the two-weak-signal
  rule does not misfire on ordinary sends today.
- Correction logged the same day: campaign **#51 never sent** (`status: suspended`,
  `sentDate: None`, 0 sent / 0 delivered / 0 opens). There was no email-side violation.
