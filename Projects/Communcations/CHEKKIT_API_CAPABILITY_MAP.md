# Chekkit API — Capability Map
**Read from Chekkit's own API reference (dashboard.chekkit.io/automations/api) on 2026-10-21.** Base URL `https://api.chekkit.io`, one Full-access token per store (Keychain `vp-chekkit-token-<CODE>`, created 2026-10-05), 60 requests/minute per token. Supersedes `Ai Optimized Marketing/CHEKKIT_API_STATUS.md` (9/5, written before the API existed).

## What the API can do, and where we use it

| Area | Endpoint | What it does | Used by us today | Opportunity |
|---|---|---|---|---|
| Send a text | `POST /v1/messages` | Texts a customer from the store number (up to 1,600 chars, optional picture/video), creates the customer if new, can assign the conversation to a team member | `winback_texts.py` only | The AI responder and missed-call text still send through the older Chekkit "event" automation (works fine). Moving them to this endpoint would drop the dependency on five Chekkit automations and let each reply be assigned to the store's manager. |
| Scheduled texts | `POST/GET/PATCH/DELETE /v1/scheduled-messages` | Texts one customer at a set time; change or cancel it before it sends; no repeat of the same text to the same customer within 12 h | Not used | Loan due-date and layaway-payment reminders from Bravo (customer-facing — needs Joshua's go). Also: when a customer texts while the store is closed, schedule a staff follow-up for opening time. |
| Conversations | `GET /v1/conversations` (status, search, limit ≤50, `before` paging) · `GET /v1/conversations/{id}/messages` (limit ≤500; sender = customer, business, ai, event, note) | Read every text thread | Unanswered-text alerts, missed-call report, AI responder, nightly AI-reply audit, weekly call review | **Fixed 10/21:** our reader now asks for 50 per page, not the default 20. |
| Assign conversations | `PATCH /v1/conversations/{id}` | Add or remove team members on a thread, with or without a notification | Not used | Auto-assign a customer text to the store's manager when it sits unanswered 10+ minutes. Internal only, no customer impact. |
| Customers | `GET /v1/customers` (by phone/email) · `POST` · `PATCH` (name, phone, email, notes, add/remove tags) | Look up, create, tag customers | `chekkit_tags.py` (nightly 01:10, since 2026-10-23) | Tag customers from Bravo (active loan, layaway, forfeited, gun buyer) so campaigns go only to the right people. That makes blasts smaller, which lowers opt-outs. |
| Review invitations | `POST /v1/review-invitations` | Asks for a review by text or email, at most once a year per customer; credits the employee on the leaderboard | `chekkit_review_invites.py` (Tuesdays) | Working. |
| Reviews | `GET /v1/reviews` (google/facebook, `since`, `rating`, `unanswered=true`, `search`, paging) — returns each review's reply | Read reviews and whether we've replied | Review alert (probe), review-reply agent (ratings) | `unanswered=true` gives an exact "reviews still owed a reply" list per store. That's the daily check that would have caught the 70-review backlog. |
| Leaderboard | `GET /v1/leaderboard` (date range) | Reviews, rating, invitations sent, clicks, reviews per employee, conversations per employee | Weekly reviews report, token checks | Per-employee texting and review numbers for the bonus and training briefs. |
| Team | `GET /v1/team-members` | Active Chekkit users and their access level | `chekkit_ops.py` (manager lookup), `chekkit_roster_check.py` (monthly, since 2026-10-23) | Monthly check: Gusto roster vs Chekkit users (who still has access after leaving, which new hires were never added). |
| Locations | `GET /v1/locations` | Only for all-store tokens | Probe only | — |
| Webhooks (push) | Settings → Webhooks, up to 5 https URLs; events: customer messages, team replies, reviews, review replies, review invitations, pipeline changes; signed (Standard Webhooks) | Chekkit pushes each event the moment it happens | **None set up** | Instant AI answers and instant review alerts instead of polling every 60 seconds. Needs a small always-on public receiver, since the Mac can't take inbound calls from the internet. |

## What the API cannot do (browser or Joshua stays the only path)
1. **Post a reply to a Google/Facebook review.** The reviews endpoint only reads. Posting stays in the browser.
2. **Read the 30-day opt-out rate / carrier trust score** (Settings → Compliance).
3. **Send campaigns/blasts** (the monthly "Shop Us Online" text).
4. **Change settings:** hours, auto-replies, templates, review reminder text, Facebook/Google links.
5. **Create or remove team members.** It can list them, not add them, so new-hire Chekkit setup stays manual.
6. **Read SMS STOP/unsubscribe status per customer.** It returns `emailUnsubscribed` only.

## Recommended next builds (ranked)
**Built and live 2026-10-21:** #1 (`chekkit-reviews-owed`, 19:05 daily, in the texting scorecard) and #2 (`chekkit-assign-stale`, every 5 min).
**Built and live 2026-10-23:** #3 (`chekkit-roster-check`, 3rd of the month 10:10; first run found 4 staff not set up, 0 leftover logins) and #4 (`chekkit-customer-tags`, nightly 01:10; tags `bravo-customer-2yr`, `bravo-visited-60d`, `bravo-borrower`, `bravo-do-not-text`, `bravo-winback`; lookup + PATCH only, never creates a customer). Update a customer is `PATCH /v1/customers/{id}` with `addTags` / `removeTags`, and tags added by hand in Chekkit are kept.

1. **Daily "reviews owed a reply" count** via `GET /v1/reviews?unanswered=true` per store, shown in the texting scorecard. Read-only; prevents another backlog.
2. **Auto-assign stale texts** to the store manager via `PATCH /v1/conversations/{id}`. Internal only.
3. **Gusto vs Chekkit roster check** via `GET /v1/team-members`, monthly, folded into the existing user audit.
4. **Customer tags from Bravo** via `PATCH /v1/customers`. Groundwork for smaller, targeted text campaigns.
5. **Webhooks**: an architecture decision (hosted receiver). Only worth it if 60-second polling ever proves too slow.
6. **Scheduled due-date reminders**: customer-facing, so Joshua's call.
