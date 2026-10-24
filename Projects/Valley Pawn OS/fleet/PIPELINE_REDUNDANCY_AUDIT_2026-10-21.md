# Pipeline redundancy / contradiction audit — 2026-10-21 (read-only)

Scope: 121 cloud scheduled tasks (58 enabled), 4 enabled local Cowork tasks, ~160 native com.valleypawn.* agents. Nothing changed.
Companion: Admin Assitant/RECORDS_ADMIN_AUDIT_2026-10-21.md (same day; items there not repeated).

## Same job running twice (native replacement built, old copy still enabled)
| Job | Native | Old copy still enabled | Note |
|---|---|---|---|
| Clock-in check | clockin-check Mon-Sat 10:15 | cloud trig_01XtvNrnsuiFkfP2NhUCpcBN Mon-Sat 10:15 | same minute -> duplicate guard can race; 10/21 neither posted (native blocked on Gusto sign-in); cloud copy still lists Jacob Cox (not current) |
| VSP gun-check fees | vsp-fee-pay 5th 10:15 (--pay, unattended) | cloud trig_01Xg3KxKu9Bxx9RxaYbL5Pbc 5th 10:15 (stage + DM "click Pay") | contradictory instructions to Joshua; native login failing since 10/20 |
| Monday reports | monday-compile Mon 8:45 (+monday-pull) | cloud trig_018He1SGinYgMjvop7i5wc4j Mon 8:00, gap-fill trig_01MoiwXW76pFej73eT1G2zPV Sun 20:30 | native built 9/30 as replacement |
| Northwest registered agent | northwest-check 08:49 | local task northwest-registered-agent-daily-check | native built 10/18 as replacement |
| Amazon supply order | supply-run/approvals/watch/deliveries (10/21) | cloud trig_0144mJb4gXUFpvSpsy8Sc66y, trig_01VhiNbw1SKDAvNYL1ZK5eJT; local tuesday-supply-prep | native header says cloud chain was the failing path |
| Quarterly capex sweep | local task | cloud trig_015dhZ98mMtCWkfGJ4g1mUGm | its own text says it moved local |

## Over-polling / overlapping monitors
- #preston-claude: Preston assistant :00 + sentinels :16/:31/:46 (7-21) = ~60 sessions/day; plus native preston-watch.
- Listings/hours: AI search health (Mon), AI visibility (Fri), presence audit (Sun) all check the same listings into #ai-marketing; plus native ffl-guardian/ffl-drift.
- Fleet health: fleet-doctor, fleet-scorecard, registry-guard (native) + cloud fleet guardian + task hygiene sweep (cannot see cloud tasks) + capability drift audit.
- Insurance: inbox watch (daily), renewal runner (Mon), coverage audit (quarterly) on the same files.
- Elemetal settlement emails parsed by settlement handler (daily) and scrap closeout staging (1st-5th).

## Contradictions
1. Store hours (Joshua: Waynesboro open Wed from 10/14, Sat 10-5). Still "closed Wed": AI search health trig_01MMh7SqfdcrqZSZNbEMYL4U, presence audit trig_01RHrweZYmUQodt58ZtKvAGu, blog publisher trig_0185SCjZ7mLBCAKknGvsKrAq, AI visibility trig_01WfZEnR1nK8awK2pQktZU3o, scrap approval watch trig_0175bSLFRwZntmCJ5AchCQee (also says Roanoke closed Wed). Customer impact already seen 10/14 (texts/AI responder said closed).
2. Failure policy v3 (never message on failure) vs tasks still saying DM/post: dashboard refresh (failure line to #general), asset recovery, Monday compile, Bald Rock 15-day contract.
3. "Never call slack_send_message (use outbox)" + calls it anyway: presence audit, AI visibility, AI search health, staff video chase, connector health.
4. Joshua's "never post to #general" vs clock-in, dress code, Cloud Cover (and dashboard failures) posting there — needs Joshua's ruling.
5. Current-staff rule vs cloud clock-in (named Jacob Cox 10/20).
6. Mislabels: gap-fill "RUN NOW ONCE" runs weekly; supply order cron 3:15 vs text 6 AM; Fortis monitor self-disables by local ID; returns summary carries an unrelated Bravo block; dashboard refresh reads #chekkit-unanswered-summary which nothing posts to now.

## Resolution 2026-10-23 (Joshua's calls)
See CHANGELOG 2026-10-23 "pipeline cleanup". Clock-in: cloud copy is live (native dormant). VSP, supply, Monday compile/gap-fill cloud copies OFF. #basics created; nothing posts to #general. AI checks de-duplicated and store facts corrected. Capex rebuilt for the cloud. Preston verified healthy (unchanged). Northwest: native not yet signed in — local task stays the driver until that one sign-in.
