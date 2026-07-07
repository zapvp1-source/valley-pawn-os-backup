---
name: postmaster-reputation-check-2026-06-23
description: One-time check of fcfpawn.com Gmail Postmaster reputation + Brevo send stats, DM'd to Joshua
---

One-time reputation check for Valley Pawn (Full Circle Finance Inc). Run autonomously; the user is not present. Goal: now that the win-back (Email 1 sent June 22) and recent weekly/monthly sends have given Google volume to measure, pull the provider-side reputation for fcfpawn.com plus the Brevo-side engagement numbers, and DM Joshua a concise summary. Do NOT post to any channel; DM only.

== PART 1 — Brevo send stats ==
- Brevo API key is on the Mac at ~/.config/valley-pawn/brevo_api_key (the sandbox cannot read it). Use the "Control your Mac" osascript tool: `do shell script "cat > /tmp/x.py <<'PYEOF' ... PYEOF; python3 /tmp/x.py"` to run Python with urllib against https://api.brevo.com/v3 using header `api-key: <key>`.
- CRITICAL Brevo quirk: for list/segment-targeted campaigns, the top-level `statistics.globalStats` is ALL ZEROS. The real numbers live in `statistics.campaignStats` (per-list array) — read THAT, not globalStats.
- GET /emailCampaigns/{id} for the win-back campaigns: id 32 (Win-back 01, sent 6/22), and also id 19 (W1), 20 (W2), 31 (monthly G&S) for comparison. Also check id 21 (W3, sent ~6/18) if sent. For each, report from campaignStats: delivered, uniqueViews (opens), uniqueClicks/clickers, complaints, unsubscriptions, soft/hard bounces — and compute open%, click%, complaint% off delivered.
- Flag any campaign with complaint rate ≥ 0.10% (the danger threshold).

== PART 2 — Gmail Postmaster Tools (fcfpawn.com) ==
- fcfpawn.com is already added & verified in Google Postmaster Tools under the logged-in Google account.
- Use the Claude-in-Chrome browser tools. Navigate to https://postmaster.google.com/managedomains , open fcfpawn.com, and read each dashboard via the URL pattern:
  - Domain reputation: https://postmaster.google.com/u/0/dashboards#do=fcfpawn.com&st=domainReputation&dr=7
  - IP reputation: ...&st=ipReputation&dr=7
  - Spam rate: ...&st=userReportedSpamRate&dr=7
  - Authentication (SPF/DKIM/DMARC): ...&st=auth&dr=7
- Take a screenshot of each and report the values. If a chart still says "No data to display at this time," report that the domain hasn't yet cleared Google's volume threshold and to re-check after the next large send.

== PART 3 — Report ==
DM Joshua on Slack (channel_id U03BB52MDSA, his account = zapvp1@me.com). Concise:
- Postmaster: domain reputation grade (High/Medium/Low/Bad), IP reputation, spam rate, auth pass rates — or "no data yet" with the reason.
- Brevo: a short table of the win-back E1 (id 32) vs the recent weeklies/monthly — open%, click%, complaint%.
- One-line takeaway on whether reputation/engagement is healthy or needs action, and whether the win-back E1 is performing better than the broadcast sends (it should, since it targets dormant contacts who re-engaged).
If anything fails irrecoverably, DM Joshua a short failure note instead.