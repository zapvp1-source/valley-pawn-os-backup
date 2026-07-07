# Fully Scheduled — 12 Weeks Locked In, Hands-Free

## What just happened

**Week 1 is SCHEDULED in Brevo** for Thursday June 4 at 10:00 AM EDT. No further action required from you for that send — Brevo's scheduler fires it automatically. Status: `queued`.

**Weeks 2–12 are STAGED as Brevo drafts** with calendar-driven copy already written. Each contains a placeholder block where the Monday automation drops that week's Deal of the Week before scheduling the send.

**Two recurring Monday scheduled tasks** now run automatically:

| Task | When | What |
|---|---|---|
| `vp-deal-of-week-monday-prompt` | Mon 8:00 AM ET (weekly) | Posts the submission prompt to Slack `#deal-of-the-week`, DMs you the heads-up |
| `vp-deal-of-week-monday-pick` | Mon 12:30 PM ET (weekly) | Reads thread replies, scores them, picks the winner, fills the placeholder in that week's Brevo draft, schedules the campaign for Thursday 10 AM, DMs you the confirmation |

## What this means in practice

**The next 12 weeks of email run themselves**, assuming managers submit deals each Monday morning by noon. Specifically:

- **Mon June 1 (this week):** The automation runs, but there's no Deal placeholder in W1, so the picker exits cleanly and DMs you "no deal block to fill this week — W1 (kickoff) already scheduled for Thursday." No action.
- **Mon June 8:** Managers submit → automation picks winner → fills W2 → schedules for Thu June 11.
- **Mon June 15:** Same loop → W3 → Thu June 18.
- ... continuing every week through Mon Aug 17 → W12 → Thu Aug 20.

**If a Monday has zero submissions:** the picker sends the email without the Deal block (just the editorial theme). It will not force a weak deal and will not fail silently.

**If the picker hits an actual error:** you get a Slack DM explaining the failure and the campaign stays as a draft. You can fix manually or skip that week.

## Brevo campaign map

| Week | Send date | Brevo ID | Status now |
|---|---|---|---|
| W1 — Kickoff | Jun 4 (Thu 10am EDT) | **19** | ✅ Queued (scheduled) |
| W2 — Gold Pulse | Jun 11 | 20 | Draft (picker fills Mon Jun 8) |
| W3 — Culpeper | Jun 18 | 21 | Draft (picker fills Mon Jun 15) |
| W4 — Summer Tools | Jun 25 | 22 | Draft (picker fills Mon Jun 22) |
| W5 — Independence Day | Jul 2 | 23 | Draft (picker fills Mon Jun 29) |
| W6 — Waynesboro | Jul 9 | 24 | Draft |
| W7 — Loans 101 | Jul 16 | 25 | Draft |
| W8 — Harrisonburg | Jul 23 | 26 | Draft |
| W9 — Back to School | Jul 30 | 27 | Draft |
| W10 — Lexington | Aug 6 | 28 | Draft |
| W11 — Warranty | Aug 13 | 29 | Draft |
| W12 — Roanoke | Aug 20 | 30 | Draft |

| Reactivation (parked, do not send) | — | 16, 17, 18 | Draft, renamed `[PARKED]` |

## Your only job for the next 12 weeks

**Monitor — don't manage.**

Each Monday at 8 AM you'll see the Slack prompt go out. Each Monday around 12:30 PM you'll get a DM saying "Thursday email is scheduled — here's what's in it." Each Friday morning you'll see the previous Thursday's performance in the existing `email-analytics-weekly` Friday post.

If you want to tweak a draft before its Monday picker run, open Brevo, edit the campaign, save. The picker only fills the Deal block — it won't touch your edits.

If a manager is consistently winning or consistently submitting weak deals, that's worth a private word with them. The Slack `#deal-of-the-week` thread is the visible scoreboard.

## The KPI target for end-of-12-weeks (Aug 20)

| Metric | Today | Target by W12 |
|---|---|---|
| Real click rate | 1.5–3% | 6–8% |
| Calls + Texts per 1,000 | 0 (no data yet) | 10+ |
| Engaged subscribers (90d rolling) | 95 | 1,500+ |
| Unsub rate per send | 0.18% | <0.3% |
| Complaint rate per send | 0.08% | <0.05% |

If we're on track at the 4-week mark (end of W4, June 25), we keep running. If not, we look at what's underperforming — subject lines, theme weeks, manager submissions — and adjust mid-flight.

## Files in your folder (the full set)

- `01_redirect_spec.md`
- `02_phase2_segmentation_plan.md`
- `03_session_summary.md`
- `04_dormant_list_audit.md`
- `05_reactivation_emails_drafts.md`
- `06_session_wrap.md`
- `07_execution_complete.md`
- `10_content_engine_12wk.md` — the 12-week calendar (source of truth)
- `11_deal_of_week_mechanic.md` — the submission/picker mechanic
- `12_execution_ready.md` — wrap of the calendar build
- `13_fully_automated.md` — this file (what's running automatically)
- `sweep_dormant_to_sunset.py` — parked, future-state hygiene script

## One real failure mode to know

The scheduled tasks run **while the Claude desktop app is open on your computer**. If your machine is asleep on a Monday morning, the 8 AM and 12:30 PM tasks will fire as soon as you wake the machine and the app launches — usually fine, but if you don't open the app at all on a Monday, that week's Thursday send won't get scheduled and won't go out.

Practical advice: just keep the app open during business hours, or open it Monday mornings out of habit. The Brevo scheduler itself doesn't depend on your machine — once a campaign is scheduled (W1 is already), it fires on time regardless.
