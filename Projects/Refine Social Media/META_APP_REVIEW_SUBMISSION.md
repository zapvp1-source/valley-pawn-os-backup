# Meta App Review — Written Submission

App: Valley Pawn Content Engine
Owner: Full Circle Finance Inc DBA Valley Pawn
Contact: zapvp1@me.com

**Use this file:** open it side-by-side with the Meta App Review form at developers.facebook.com/apps/<app_id>/app-review/permissions/. For each permission, copy the relevant section into the corresponding form field.

---

## Permission 1 — `pages_read_engagement`

### Use case (paste into "How will your app use this permission?")

Valley Pawn operates 5 brick-and-mortar pawn store locations and 1 brand parent Facebook Page (6 Pages total) under a single Business Manager portfolio. Our internal content management system, "vp-content-batch", publishes 30+ organic posts per week across these Pages on a routed schedule.

We need `pages_read_engagement` to read post-level engagement data (reaction counts, comment counts, share counts, and the comments themselves) on the posts our own app has published. This data drives two internal workflows:

1. **Friday performance close** — every Friday at 5pm ET our system aggregates reactions, comments, shares, and reach across the week's posts to identify which content pillars and creative styles drove the most engagement. The top-performing 20% feeds into our paid-ad amplification queue. Without this permission we cannot run that analysis programmatically and our team has to copy numbers from Meta Business Suite by hand for 30+ posts each week.

2. **First-hour reply alerts** — 30 minutes after each Reel publishes, our system pulls the new comments and DMs our community manager with the unanswered ones so they can reply inside the algorithm's critical first-hour window. Without this permission we miss the comments and the post loses its organic reach lift.

All data read is for posts our app published on Pages we own. We do not read engagement on Pages we don't own, do not aggregate user-level data, and do not share this data with third parties.

### Testing steps (paste into "Step-by-step instructions for the reviewer")

1. Sign in to Facebook as our test user (credentials provided in the test user fields below).
2. Open https://content.valleypawn.internal/dashboard (or screencast).
3. Click "Friday Close" in the left nav.
4. The dashboard pulls the past 7 days of posts from all 6 Pages and shows reactions / comments / shares / reach per post.
5. Click any post row to expand → see the actual comment text for that post.
6. Both views are populated by Graph API calls to `/{page-id}/posts?fields=reactions.summary(true),comments.summary(true),shares,insights.metric(post_impressions,post_reach)`.

### Screencast script (read while recording)

> "Hi, this is the Valley Pawn Content Engine. We manage 6 Facebook Pages for our pawn store chain. I'm logging in now as the Page admin. Here's the Friday Close dashboard — you can see it's pulling the past 7 days of post engagement across all our Pages. These reaction counts, comment counts, and share counts come from the pages_read_engagement permission via the Graph API. If I click into a single post, you can see the actual comment text — that's also pages_read_engagement. This drives our weekly performance review and our first-hour comment-reply alerts. Without this permission we can't run either workflow. Thank you."

---

## Permission 2 — `read_insights`

### Use case (paste into "How will your app use this permission?")

Valley Pawn's content engine uses Page Insights to measure organic reach, impressions, engaged users, and post-level performance metrics that are not available through public engagement counts alone.

Specifically we need:
- `page_impressions` (weekly trend of how often our content was shown)
- `page_post_engagements` (engaged-user counts per post)
- `page_fans_locale` and `page_fans_city` (to align store-local posts with the followers in that store's market)

These metrics flow into the same Friday performance close as above and into our quarterly board report. Without `read_insights` we have organic reach blind spots — we can see engagement actions but not impressions or reach, which prevents us from calculating engagement rate and ROI accurately.

All Insights reads are on Pages we own and operate. Data is stored in our internal analytics database, not shared externally.

### Testing steps

1. Sign in as test user.
2. Open the dashboard, click "Insights" → "Weekly Trend".
3. The view shows page_impressions and page_post_engagements over the past 30 days for each of our 6 Pages.
4. Backed by Graph API calls to `/{page-id}/insights?metric=page_impressions,page_post_engagements&period=week`.

### Screencast script (additional clip — record after permission 1 demo)

> "Now for read_insights — clicking the Insights tab. You can see organic impressions and engaged-user counts trending across the past 30 days for all 6 Pages. These metrics come from the Page Insights API via read_insights. We use them to calculate our true engagement rate and to track week-over-week organic reach trends. The data only covers Pages we own."

---

## Permission 3 — `pages_show_list` (request if not already granted at advanced access)

### Use case

The content engine needs to enumerate which Pages our admin user manages so it can route each scheduled post to the correct Page. Without `pages_show_list` we cannot programmatically know the Page IDs to call other endpoints against.

### Testing steps

1. Sign in as test user.
2. Open the dashboard "Settings" → "Pages connected".
3. The list of all 6 Pages the admin manages is shown, populated by `/me/accounts`.

### Screencast script

> "Finally pages_show_list — the engine calls /me/accounts to enumerate the Pages the signed-in admin manages, which is how we know which Page IDs to route each weekly post to. Here's the list of all 6 Valley Pawn Pages connected."

---

## Privacy Policy URL (Meta requires this field)

If you don't already have one published, draft:
- https://valleypawn.com/privacy
- Or use a free template service (Termly, iubenda) and publish the URL to the site before submitting.

The privacy policy must mention that the app accesses Facebook engagement data, what's stored, how long, and that users can request deletion.

---

## Test user credentials

Create a Meta test user inside the app's dashboard (developers.facebook.com → App → Roles → Test Users → Create test user). Assign that user as an admin of your test Page or use a sandboxed Page Meta provides. Paste the test user's email + password into the form fields.

**Never paste your real account password.**

---

## Final pre-submit checklist

- [ ] Privacy policy URL is live (open it in a new tab to confirm)
- [ ] Test user credentials work (sign in once to confirm)
- [ ] Screencast uploaded OR Loom/Drive URL pasted (must be publicly viewable without login)
- [ ] All three permissions have all three fields filled (use case, screencast, testing steps)
- [ ] Business Verification is at least *submitted* (Task 3 in the playbook) — App Review can be in queue before verification completes, but won't be approved without it.

When all checked, hit **Submit for review** at the App Review summary page.
