# Academy onboarding flow — Gusto → Slack → Academy (proposed 2026-09-28, Grow plan)

## Mechanism (one trigger, no manual steps)
1. **Gusto is the trigger.** Hire lands in Gusto (existing `onboard-employee` flow). OB-2026-01 gets one new line: "Academy login sent / Level 1 assigned."
2. **Academy account auto-created** (native agent `academy-sync`, daily, via TalentLMS API — available on Grow): new Gusto employee → TalentLMS learner (store email or personal email from Gusto), added to their store's **Group**, enrolled in the **New Hire learning path** (L1→L7 in order, each level locked until the prior is complete). Managers also get the Manager Track. TalentLMS sends the "set your password" email.
3. **Slack is where they hear about it.** Same run posts a welcome DM (existing `onboard-employee-slack-chekkit` step): the Academy link, "check your email for the password link," and "Level 1 is due by the end of day 3." The Manager gets a DM: "<name> starts the Academy today — schedule 45 min on the store PC."
4. **Floor Checks** — manager marks them in TalentLMS (instructor role on their store's group) or replies ✅ to the Slack prompt; the agent records it.
5. **Offboarding** — `offboard-employee` deactivates the TalentLMS user (history kept).

## Cadence (new hire, on the clock)
| When | What | Gate |
|---|---|---|
| Day 1–3 | Level 1 (~45 min) + Gun Safety 101 certificate | Condition of employment (HR-2026-05) |
| Week 1 | Level 2 — Open, Close, Count | Before any opening/closing shift |
| Week 2 | Level 3 — The Loan | Before writing loans alone |
| Week 3 | Level 4 — Buying & Pricing | Before buying alone |
| Week 4 | Levels 5 + 6 — Metals; Firearms | No metal quotes / no firearm transaction until passed + Floor Checks |
| Weeks 5–6 | Level 7 — Sell & Serve + phone gate (lesson 7.3 + five practice calls scored by the Manager; no sims) | → Certified by day 45 |
| By day 90 | Level 8 | Keys at 90 days + Certified; 90-day review with Academy record |
| Yearly | Recerts (gun safety by Jan 31; harassment, data security, texting rules) | Assigned automatically |
Pace: ~30–45 min per shift at the store PC in slow periods. All training is done in the store, on the clock — never at home (CEO 2026-10-25; replaces the earlier optional at-home time).

## Accountability (Slack)
- **Daily 9:00** — DM each learner with anything due/overdue; manager gets pending Floor Checks.
- **Day 3 miss on Level 1** — DM to the Market Manager + the CEO only (the one escalation).
- **Contacting the Market Manager** — messages in Slack (never a personal text); calls to the Market Manager's Zoom line, 540-202-4200. Call-outs are a voice call to the Market Manager at least 2 hours before the shift; text or Slack doesn't count.
- **Monday 9:30 scorecard** — #training: positive leaderboard by store (completions, first-try pass rate); per-person detail to each manager privately; exceptions to Joshua's DM.

## Seats (CEO 2026-10-25)
Academy seats rotate **5 learners at a time, newest hire first**. When a learner completes their assigned path or leaves, `academy-sync` gives the seat to the newest hire waiting; everyone else waits in hire-date order (newest first).

## Titles (per Gusto)
Sales and Loan Associate, Sales and Loan Representative, Manager, Market Manager, CEO. No assistant managers. Level 7 certification covers Associates and Representatives.

## Existing staff rollout (at launch)
All current staff assigned Levels 1–7 as seats allow (5 at a time, newest hire first); Level 1 due in 7 days, then one level per week (Certified in ~8 weeks). Managers also take the Manager Track.

## Needs before launch
Grow plan purchased (Joshua) → API key enabled → learning path + store groups built → `academy-sync` / nudge / scorecard agents built and tested on the test learner → notifications re-enabled → Joshua's go.
