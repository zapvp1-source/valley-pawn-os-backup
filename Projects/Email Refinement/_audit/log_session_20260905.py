#!/usr/bin/env python3
"""Write the 2026-09-05 Email Department session record into CHANGELOG + EFFICIENCY_LOG.
Append-only; never rewrites existing content."""
import os, datetime

P = os.path.expanduser("~/Documents/Claude/Projects")
CHANGELOG = os.path.join(P, "Valley Pawn OS/CHANGELOG.md")
EFFLOG = os.path.join(P, "Email Refinement/EFFICIENCY_LOG.md")

changelog_entry = """
## 2026-09-05 (Email Department — full review + Phase 0/1 build, plan file 19)
- **Full review of the email department** (every workflow, cadence, task, list, script and data feed)
  written to `Email Refinement/19_EMAIL_DEPT_AUTOMATION_PLAN_2026-09-05.md` — 11 findings, an expert-board
  deliberation, and a 5-phase plan. Verified against the live Brevo API, the scheduled-task registry,
  the CHANGELOG, EFFICIENCY_LOG and the 8/22 channel audit — not from memory.
- **FIXED — monthly Gold & Silver was sending overnight.** `monthly-we-buy-gold-silver-email` cron was
  `15 2 1 * *`, and the task sends immediately on wake, so the 11k-recipient send landed at 2:20 AM
  (Sep 1) and 3:09 AM (Aug 1) instead of the 9 AM its own description claims. Cron corrected to
  `0 9 1 * *`. First 9 AM send: 2026-10-01. Nothing else about that task changed.
- **FIXED — the dead image endpoint was still Step 5 of the Monday picker.** `vp-deal-of-week-monday-pick`
  STEP 5 still instructed uploading photos via Brevo `POST /v3/media`, the endpoint that does not exist
  and that silently killed W10-W12 in Jul/Aug. The 8/21 hardening addendum contradicted it further down
  the same file, so a fresh run could follow either. STEP 5 rewritten to the proven WordPress media path
  (with the website deal-image mirror as the cheap first option) and the dead endpoint named as
  forbidden. Backup `.bak-pre-20260905-phase0`.
- **FIXED — the picker's public Slack confirmation.** Step 8 named `#deal-of-the-week` but not its ID;
  that post has failed silently every Monday since 7/27 (the 9/4 guardian pass confirmed the sends
  themselves were fine). Step 8 now pins `C0AVCANK7E3` and re-reads the channel to confirm the post
  landed. Root cause of the original failure is still unconfirmed — the ID plus verification is the
  fix-forward; watch Monday 9/7.
- **FIXED — four orphan drafts were aimed at the full list.** Campaigns 43 (Aug gold rebuild), 49
  (Hiring), 23 (W5 July 4) and 1 (TEST) sat as drafts targeting list 3 / no list. All four renamed
  `[PARKED — do not send] …` and repointed to the internal seed list (10), so a stray send can only
  reach staff. Content untouched.
- **NEW (additive) — `brevo-stage-next-quarter`** scheduled task, quarterly on the 25th of Jan/Apr/Jul/Oct
  at 6 AM, sonnet-pinned. Writes and stages the NEXT quarter's 13 Thursday drafts from the live template
  so the weekly calendar can never run out again (calendar exhaustion was one of the two causes of the
  Aug 6/13/20 blackout; the current calendar ends Dec 31). Mechanics in the new committed script
  `Email Refinement/bin/stage_quarter.py` — generalises the one-off `_audit/build_calendar.py`, picks its
  base template from the newest draft still carrying the DEAL placeholder, continues the A-E wave
  rotation, and GET-verifies every draft it creates (name, lists, placeholder, no unfilled markers,
  5x call + 5x text links, primary CTA, no legal-name leak). Dry-run proven against live campaign 70.
  First run 2026-10-25 for Q1 2027.
- **Draft-guard floor raised 4 -> 8 weeks** in `brevo-weekly-efficiency-audit`, and
  `brevo-weekly-draft-guard`'s hardcoded "after Dec 31 the calendar runs out" warning replaced with a
  standing runway check pointed at the new stager. Both backed up.
- **NEW (additive) — Brevo list 19 "Engaged v2 — human-verified"** + the `brevo-engaged-v2-refresh` task
  (Wednesdays 6:20 AM, sonnet-pinned) and `Email Refinement/bin/engaged_v2.py`. Closes the audit's
  Finding 02 / plan Finding F5: list 7 is fed by "any link click -> add", which recruits security
  scanners. **Contrary to the 8/22 audit's assumption, per-contact click data IS available** —
  `GET /contacts/{email}` returns `statistics.clicked` with campaignId, url, eventTime, ip and count,
  and `statistics.delivered` gives the delivery time to pair against. Scoring: an intent click (primary
  CTA, store call/text/map, store finder) within 90 days, at least 45 s after delivery, in a campaign
  where the contact clicked <= 7 distinct URLs and not only chrome links. **First real pass: of 177 on
  list 7, only 87 qualify — 90 are stale or scanner-shaped** (289 no-click, 19 chrome-only, 4 clicked
  within 31 s of delivery, 1 walked 12 URLs). List 19 created and populated with the 87, verified by
  re-read. Nothing sends to it — list 7 remains the live audience; the switch is Joshua's call after
  ~4 weeks of comparison rows in the EFFICIENCY_LOG.
- **Fleet Guardian output manifest** gained `brevo-stage-next-quarter` (the other three Brevo-lane
  entries were already added by the 9/5 publications audit). Backup written.
- **Still needs Joshua (business calls, not technical):** loan-due reminder copy before that flow can
  switch on; confirm the birthday 20% offer; confirm per-store reply-to so store managers own customer
  replies to spotlights. Phases 2-5 of the plan (Bravo customer-contact pipeline cell, triggered flows,
  store-aware sends, single metric source) are unbuilt and sequenced in file 19.
"""

eff_entry = """
## 2026-09-05 (Email Department review — Phase 0 + Phase 1 build)
STATE: Channel healthy going in (W14 on 9/3 delivered 178/183 with 124 unique clicks; Sep 1 Gold &
Silver 11,000 delivered, 1.8% bounce, 0.15% unsub; both domains authenticated). Full department review
run against live Brevo, the task registry and the 8/22 audit — 11 findings, plan written to
`19_EMAIL_DEPT_AUTOMATION_PLAN_2026-09-05.md`.
FIXED THIS RUN:
- Monthly Gold & Silver was sending at 2-3 AM, not the 9 AM its description claims (cron fired at 2:15
  and the task sends on wake). Cron now `0 9 1 * *`; first 9 AM send 10/1.
- Monday picker STEP 5 still told the runner to upload photos to Brevo's non-existent /v3/media
  endpoint (the exact thing that killed W10-W12). Rewritten to the proven website-media path.
- Monday picker STEP 8's Slack confirmation now pins the channel ID and verifies the post landed —
  that post has been silently missing since 7/27 while the sends themselves were fine.
- Four orphan drafts (43, 49, 23, 1) renamed [PARKED] and repointed from the 13k master list to the
  internal seed list, so a stray send can't reach customers.
- Draft-runway floor raised 4 -> 8 weeks; the guard's "calendar ends Dec 31" note now points at the
  new quarterly stager instead of just warning.
BUILT THIS RUN (additive, nothing existing removed):
- `brevo-stage-next-quarter` (quarterly, 25th of Jan/Apr/Jul/Oct 6 AM) + `bin/stage_quarter.py`.
  Stages 13 Thursday drafts per quarter from the live template, continues the wave rotation, and
  verifies every draft it creates. First run 10/25 for Q1 2027. This is the permanent answer to the
  calendar-exhaustion half of the August blackout.
- Brevo list 19 "Engaged v2 — human-verified" + `brevo-engaged-v2-refresh` (Wed 6:20 AM) +
  `bin/engaged_v2.py`. IMPORTANT CORRECTION TO THE 8/22 AUDIT: per-contact click data IS reachable —
  `GET /contacts/{email}` returns statistics.clicked with campaignId/url/eventTime/ip/count plus
  statistics.delivered for pairing. The audit's "scanner purge needs per-contact click data the API
  won't expose" note is wrong and should not be repeated.
  FIRST SCORING PASS: universe 400 of 11,585 (list 7 + v2 + a rotating slice; seeds excluded).
  list7=177, v2=87, both=87, list7-only=90, v2-only=0. Reasons: no-clicks-90d 289, intent-click 87,
  chrome-only 19, clicked-within-31s 4, walked-12-urls 1. List 19 populated with the 87, verified by
  re-read. NOTHING SENDS TO LIST 19 — list 7 is still the live audience.
STILL OPEN (needs Joshua): loan-due reminder copy (customer-facing + legal); confirm the birthday 20%
offer; confirm per-store reply-to. These three are the only decisions in the whole plan that are his.
STILL OPEN (queued, no input needed): Phases 2-5 of plan file 19 — the Bravo customer-contact pipeline
cell (the unlock for names/store/phone/DOB/loan-due), triggered flows (loan-due, layaway-due, forfeited
win-back, 3-step welcome, birthday), store-aware sends + Chekkit SMS orchestration, and collapsing to a
single metric source. Forfeited win-back list 11 still holds 0 contacts.
NEXT RUN SHOULD CHECK: (1) did the Monday 9/7 picker post its confirmation line to #deal-of-the-week —
that is the test of the channel-ID fix; (2) did the 9/10 send (campaign 54) actually jump reach from
~180 to ~2,400 with wave list 14 attached; (3) after the Wed 9/9 v2 refresh, whether the v2 count is
stable — 4 stable weeks is the evidence Joshua needs for the audience switch; (4) 10/1 gold send should
now land at 9 AM, not 2 AM.
"""


def append(path, text):
    """EFFICIENCY_LOG is oldest-first — new entries go at the end."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(text if text.startswith("\n") else "\n" + text)
    print("appended to", os.path.basename(path), len(text), "chars")


def prepend_after_header(path, text):
    """CHANGELOG is NEWEST-FIRST — insert above the first existing '## ' entry, below any file header."""
    s = open(path, encoding="utf-8").read()
    i = s.find("\n## ")
    if i < 0:
        open(path, "a", encoding="utf-8").write("\n" + text)
        print("no '## ' header found — appended to", os.path.basename(path))
        return
    out = s[:i + 1] + text.lstrip("\n") + "\n" + s[i + 1:]
    open(path, "w", encoding="utf-8").write(out)
    print("prepended to", os.path.basename(path), "above first entry at char", i)


prepend_after_header(CHANGELOG, changelog_entry)
append(EFFLOG, eff_entry)
