# Email Refinement — Session Findings 2026-06-29

Context-load + two requested fixes. Net result: one fix was redundant (caught and reverted),
the other turned out to need an architecture decision, not a code patch. Full detail below.

## 1. Deal of the Week — firing consistently ✅

Both scheduled tasks are live and ran this morning (Mon 6/29):
- `vp-deal-of-week-monday-prompt` — lastRun 06-29 08:01, next 07-06
- `vp-deal-of-week-monday-pick` — lastRun 06-29 12:33, next 07-06

Submissions land every Monday in `#deal-of-the-week`. June 25 send went out with 3 deals
(Tiffany dish/Culpeper, RYOBI band saw/Lexington, Dyson/Roanoke). Weeks W1–W4 (campaigns
19–22) all show status `sent`. System is healthy — no action needed.

## 2. REDUNDANCY CAUGHT — duplicate reactivation sequence (reverted)

A complete **Win-back sequence** is already live, built by another session and never logged
in this project folder:

| Campaign | Status | Sent/Sched | Recipients | Open | Click | Unsub |
|---|---|---|---|---|---|---|
| #32 Win-back 01 "Miss You" | sent | Jun 22 | 9,514 | 4.09% | 0.29% | 0.14% |
| #33 Win-back 02 "What's New" | sent | Jun 29 (today) | 9,467 | 1.48% | 0.21% | 0.04% |
| #34 Win-back 03 "Last Call" | scheduled | Jul 6 | — | — | — | — |

This is the SAME job as the parked Reactivation sequence (#16/17/18). The reason 16/17/18 were
`[PARKED]` is they were **superseded** by this Win-back set — they should NOT have been un-parked.

**Action taken:** I had scheduled #16/17/18 (6/30, 7/7, 7/14, dormant segment only). On
discovering the live Win-back sequence, I **suspended all three** and renamed them
`[PARKED - superseded by Win-back 32/33/34]`. No duplicate will fire. Dormant contacts get only
the one Win-back series (finishes Jul 6), not two overlapping ones.

**Root cause of the near-miss:** the Win-back work left no trail in this project folder or in
brevo-context — the "invisible work" gap. Lesson: before touching email campaigns, search Brevo
campaigns directly (UI/API), not just the project docs.

## 3. Analytics blind spot — confirmed, and it's a Brevo limitation

`email-analytics-weekly` reads per-list stats, which are 0 for segment-targeted sends. I checked
deeper: for segment-targeted campaigns the Brevo API returns **all zeros across the entire
statistics object** — `globalStats` too (sent:0, delivered:0, opens:0). Verified on campaign 22
(W4, sent to segment 5): `campaignStats: []`, `globalStats` all zero. The real numbers exist
**only in the Brevo web dashboard UI**.

So a "different endpoint" does NOT fix this — the data isn't exposed via API for bare-segment
sends. There are two real options:

- **Option A (durable, recommended): send to a LIST, not a bare segment.** Maintain an
  "Engaged" *list* (synced from the engaged segment) and point the weekly deal sends at the
  list. Then both the API and `email-analytics-weekly` see real numbers again. Requires a small
  sync job to keep the list current AND retargeting campaigns 19–30 — which the
  `vp-deal-of-week-monday-pick` task fills/schedules. **This touches the deal-of-week picker, so
  it's a decision to make deliberately (Rule #4 additive), not a silent change.**
- **Option B (brittle): scrape the dashboard** on a schedule via Chrome. Not recommended —
  fragile, and adds redundant infra alongside `email-analytics-weekly`.

Note: large list-based sends (e.g., the Win-back sends above) DO show in the dashboard and are
readable there; the API-zero problem hits anything targeted at a bare segment.

## 4. The "massive open rates" question — answered

The deal emails go to the small Engaged segment (~95–115), so the % looks huge while actual human
reach is small. The win-back sends to the full ~9,500 dormant show low opens (1.5–4%) — expected
for dormant. Judge performance by clicks + Calls/Texts, not opens. Nothing is broken; it's the
segmentation math working as designed.

## 5. Analytics fix — BUILT (expert board approved, additive)

Board ruled: send weekly deals to a maintained Engaged *list* instead of a bare segment, so the
API (and `email-analytics-weekly`) can read real stats. Built end-to-end on 2026-06-29:

- **Engaged List = list ID 7** ("Engaged List (clicked 90d) - measurable send audience"). Created
  via API.
- **Seeded** from segment 5 (Engaged - 90d clicked): 128 contacts added, 113 active.
- **Brevo Automation "Clicker to Engaged List (measurable)"** — ACTIVE. Trigger: any email link
  click → Action: add contact to list 7. Re-entry after exit enabled. Keeps the list self-current
  (also captures win-back re-engagers into the measurable list).
- **Deal drafts W5–W12 (campaigns 23–30) repointed** from segment 5 → list 7. They now report real
  opens/clicks via the API, so the Friday `#email-campiagns` analytics post fixes itself with NO
  edit to the hardened picker or analytics task (Rule #4 additive).
- W1–W4 (already sent) stay as-is. Segment 5 still exists as the source of truth.

**Watch on first send (W5, Thu Jul 2):** confirm it goes to ~113 and that the Friday analytics post
shows non-zero numbers. Also confirm the `vp-deal-of-week-monday-pick` picker left the list-7
recipient intact when it filled/scheduled W5 (it should — it only fills the deal block).

**Known limitation:** list 7 only grows from clicks (no auto-removal of people who go quiet). Quarterly
re-sync from segment 5 keeps it tight, or add a "no click 90d → remove from list" automation later.

## Still open (not done)
1. Widen "Engaged" definition (opened OR clicked, 90–180d) to grow the weekly audience beyond ~128 —
   it's small partly because the win-back (#32/33/34) is still mid-flight and regrowing engagement.
2. Growth (new customers) is a separate track per the marketing board: local search + reviews +
   the gold campaign. Email is retention.
