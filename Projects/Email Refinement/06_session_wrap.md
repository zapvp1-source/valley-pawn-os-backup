# Email Refinement — End of Session Wrap (2026-05-28)

## What's done

**1. Measurability — fully shipped**
- `/c/<store>` and `/t/<store>` HTTPS redirects live on thevalleypawn.com (WPCode snippet 566)
- VP Master Template (Brevo ID 11) updated: 10 store buttons now produce trackable click data
- Verified via curl + Brevo API re-fetch + segment query

**2. Segmentation — proven, runbook documented**
- Proof segment built ("Prefers Roanoke", ID 2, 3 contacts)
- Pattern + 11 follow-on segment recipes documented in brevo-context

**3. List audit — completed**
- 10-campaign analysis shows true engagement: 2.90% weighted click rate, 1.57% real opens
- Real engaged universe: ~800–1,500 contacts (8–15% of 9,600 deliverable)
- Dormant pool to reactivate: ~8,000+

**4. Reactivation sequence — designed + drafted**
- 3 emails written (Day 0 / 7 / 14)
- Copy in brand voice, Master Template markers filled in
- Single tracked CTA per email → `/keep-in-touch` page (Joshua to create on WP)

**5. Sunset policy — documented**
- 90-day no-click threshold defines dormant
- Post-sequence non-responders move to Sunset list, off list 3
- Policy + KPIs + risk framing baked into brevo-context.md (now 384 lines)

## What's queued but not yet executed

These need your go-ahead before they're irreversible:

| Step | Owner | Effort | When |
|---|---|---|---|
| Build `https://thevalleypawn.com/keep-in-touch` WP page | You (5 min) or me next session | 5 min | Before Email 1 sends |
| Build "Dormant — no click 90d" segment in Brevo UI | Me, next session | 10 min | Before Email 1 sends |
| Stage Email 1 as a Brevo campaign (draft, not sent) | Me, next session | 15 min | Before Email 1 sends |
| Send Email 1 to dormant segment | You approve, me schedule | n/a | Recommended: a Wed or Thu next week |
| 7 days later: Send Email 2 | Auto via Brevo workflow OR manual | n/a | +7 days |
| 14 days later: Send Email 3 | Auto via Brevo workflow OR manual | n/a | +14 days |
| Run suppression sweep (Python script) | Me, scripted | 30 min | +18 days |

## Deliverables in this folder

1. `01_redirect_spec.md` — WP redirect specification
2. `02_phase2_segmentation_plan.md` — original segmentation design (superseded by leaner Phase 2a approach)
3. `03_session_summary.md` — first half of session wrap
4. `04_dormant_list_audit.md` — engagement audit + reactivation theory
5. `05_reactivation_emails_drafts.md` — 3-email copy drafts
6. `06_session_wrap.md` — this file

## The 30-second story

We turned the email program from "blast 11K and pray" into a measurable system with the structural pieces in place to focus sends on the 1,500 contacts who actually care. The biggest needle-mover is still ahead: the reactivation sweep, which will mechanically lift click rate 3-5× by removing ~8K silent contacts who are dragging deliverability down.

Greenlight the reactivation sequence and I'll build segments + stage Email 1 next session.
