# Execution-Ready — 12-Week Engagement Engine

**Apologies for the earlier "let's sunset 9,600 people" detour.** That was wrong-footed for a list 2 months into its first re-awakening in a decade. The actual play — a content engine that earns engagement back — is now built and ready.

## What's in Brevo right now

### Parked (do not send)
- **[PARKED] Reactivation E1/E2/E3** (campaign IDs 16/17/18) — sitting as drafts, clearly labeled. Available later if ever needed; not the current play.

### Ready to schedule (the new program)
- **W1 — Kickoff** — ID **19** — send June 4, Thu 10am
- **W2 — Gold Pulse + First Deal of the Week** — ID **20** — send June 11
- **W3 — Culpeper Spotlight + Deal** — ID **21** — send June 18
- **W4 — Summer Tools + Deal** — ID **22** — send June 25

All four target list 3 (all 11,159 subscribers — no segment filter; we want full reach while warming). All four pass marker-residual checks. All four have the full 10 trackable store buttons baked in.

Weeks 2-4 contain a clearly-marked Deal of the Week placeholder block — the weekly Monday automation (or Joshua manually until week 5) fills it the day before send.

## The full picture

| Layer | Status | Where |
|---|---|---|
| 12-week content calendar | Documented | `10_content_engine_12wk.md` |
| Deal of the Week mechanic | Documented | `11_deal_of_week_mechanic.md` |
| Weeks 1-4 drafts in Brevo | Staged | Brevo campaign IDs 19-22 |
| Brevo segmentation infrastructure | Live (Engaged + Dormant + Roanoke proof) | Brevo segments 2, 3, 4 |
| WP /c/ and /t/ redirects | Live | WPCode snippet 566 |
| /keep-in-touch confirmation page | Live (parked for now) | thevalleypawn.com/keep-in-touch |
| Suppression sweep script | Built, parked | `sweep_dormant_to_sunset.py` |
| Weekly campaign automation | Spec'd, build queued | weekly skill update |

## What you do this week

**One thing:**

1. Open Brevo → Campaigns → find `W1 — Kickoff — June 4, 2026` (ID 19)
2. Click Schedule → pick **Thursday June 4, 2026, 10:00 AM ET**
3. Confirm. Done.

That's the launch click. Everything else flows from it.

## What I do (next session or scheduled task)

- Build the Monday 8am Slack post that asks managers for Deal of the Week submissions
- Build the Monday 12:30 picker that scores submissions
- Build the Tuesday draft-builder that fills weeks 5+ from the calendar
- Build the Wednesday 9am Slack approval DM
- Schedule the recurring task to run the whole flow

For weeks 2-4, you fill the Deal of the Week block manually in Brevo (or I do it for you) the day before each send.

## The KPI scoreboard

Already running via the Friday `email-analytics-weekly` task. Add these targets to it:

| Metric | Today | 4-week target (end of W4) | 12-week target (end of W12) |
|---|---|---|---|
| Real click rate | 1.5–3% | 4% | 6–8% |
| Calls + Texts per 1,000 | 0 (no data yet) | 5 | 10+ |
| Engaged subscribers (90d) | 95 | 500 | 1,500+ |
| Unsub rate per send | 0.18% | <0.3% | <0.3% |
| Complaint rate per send | 0.08% | <0.05% | <0.05% |

If we hit the 4-week targets, the engine is working. If not, we adjust mid-flight (different theme weeks, A/B subject lines harder, look at which managers' deals win).

## Files in your folder

- `10_content_engine_12wk.md` — the 12-week strategic calendar
- `11_deal_of_week_mechanic.md` — the recurring submission/picker mechanic
- `12_execution_ready.md` — this file (TL;DR)
- (Plus the earlier docs 01-07, the sweep script, and `02` plan from earlier work)
