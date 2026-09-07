# Chekkit — headless access investigation
**Date:** 2026-09-05 · **Status:** BLOCKED on one email to Chekkit support (decision `DEC-CHEKKIT-API`)
**Why this matters:** 4 scheduled tasks drive the Chekkit browser UI today — `nightly-chekkit-review-responses` (nightly, ~2 hrs of clicking), `chekkit-weekly-review-requests` (Tue), `review-obtained-last-week` (Mon), `google-reviews-post-watchdog` (Mon, re-scrapes the same numbers 7½ hrs later). Highest-ROI Chrome retirement in the marketing fleet.

## What was verified today (live, signed-in session)
- `dashboard.chekkit.io` is a React SPA calling its own backend at `dashboard.chekkit.io/api/*`.
- **Auth is a JWT in `localStorage['jwt']`** (271 chars, stored quoted), not an API key and not a header we can mint. Endpoints observed in the live session:
  `/api/current_user` · `/api/business-group` · `/api/google-reviews` · `/api/facebook-reviews` · `/api/review-request` · `/api/review-invitations/tagged-google-review-requests` · `/api/review-response-templates` · `/api/tags/list` · `/api/departments/get-departments` · `/api/automation/message-automations` · `/api/announcements` · plus `chat.chekkit.io/api/webchat/*`, `teams.chekkit.io/api/team/*`, `runner.chekkit.io/api/v1/project/*`.
- Calling those endpoints with the session JWT returns `{"error":true}` / `{"error":false}` shells rather than data, and `/api/review-invitations/tagged-google-review-requests` returns **403 "You do not have permission to tag reviews."** — i.e. the internal API is scoped to the UI's own request shape and this account's permissions. **This is an internal API, not a supported integration surface.** Building against it would be exactly the kind of brittle scraping we are trying to retire.
- Reviews data confirmed present and current in the UI (Lexington: Google 4.8, 190 total, +71 last 12 months, 92% 5-star, 0 awaiting response).

## The supported paths (per Chekkit's own docs, 2026-09-05)
1. **Zapier** — Chekkit is a Zapier partner; documented triggers/actions include sending review requests and creating customers. Docs tell users to email `support@chekkit.io` for the credentials to add Chekkit to a Zapier account.
2. **Webhooks** — "Chekkit Events Handler – Webhook Integration" and a documented Google-Sheet-via-webhook path. This is the cleanest fit for us: Chekkit pushes review events to an endpoint we own, and nothing has to poll or click.
3. **Integration Dashboard** (shipped Fall 2022) — "set up custom integrations based on events from your POS or partner app."
4. There is **no public REST API doc, no OpenAPI spec, no developer portal.** API access is arranged by contacting support.

## Recommendation (expert board, martech + SRE seats)
Do **not** build against the internal `dashboard.chekkit.io/api`. Instead:
- **Ask support directly.** One email to `support@chekkit.io` (draft below) asking for (a) API/webhook credentials for our 5 locations, (b) whether review events can be pushed to a webhook, (c) whether it's included on our plan or needs a tier change. Answer determines the build.
- **Interim, no waiting:** the review *counts and ratings* we report weekly are also obtainable from Google directly, and the Roanoke gap number has been carried unverified since 8/25 for exactly this reason. If Chekkit says no, the reputation lane goes to Google Business Profile API via the same service account as the Website Analytics plan (`LOGIN-GOOGLE-SA`) — same login, one more scope, and it fixes the review-gap metric too.

## Draft email (send from jdavis@fcfpawn.com — Joshua's send, not mine)
> Subject: API / webhook access for our 5 locations
>
> Hi — we run Valley Pawn, five locations on Chekkit (Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke). We've automated most of our back office and the last manual piece is Chekkit: someone signs into the dashboard every night to respond to reviews and every week to send review invitations.
>
> Three questions:
> 1. Can you issue us API credentials to read reviews and send review invitations across all five locations?
> 2. Can review events (new review, new invitation sent, review responded) be pushed to a webhook we host?
> 3. Is either included on our current plan, or does it need a different tier? If it's a tier change, what's the cost?
>
> Thanks,
> Joshua

## Register
`DEC-CHEKKIT-API` (owner: joshua) · `BUILD-CHEKKIT-CLIENT` (owner: claude, blocked on the above).
