# Meta UI Calendar — Execution Playbook

Four tasks. Execute in this order — each unblocks the next.

**Logged in as:** zapvp1@me.com (Joshua)
**Business portfolio:** Valley Pawn (the one with 9 Pages, NOT "Valley Pawn Waynesboro")
**Legal entity for verification:** Full Circle Finance Inc DBA Valley Pawn — EIN 47-1198118

---

## TASK 1 — Harrisonburg page merge (5 min)

**Why this first:** independent of all others. If anything goes wrong it doesn't block verification.

### Steps

1. Open https://www.facebook.com/pages/merge/ (signed in as zapvp1@me.com).
2. The merger picks **two Pages you admin**. Pick the **Harrisonburg keeper** (the one with more followers / older creation date / more reviews — confirm before continuing) and the **Harrisonburg duplicate** (the one being merged in).
3. Click **Continue**. Meta shows a confirmation panel telling you which Page survives and what dies.
4. ⚠️ **Verify the keeper before confirming.** Followers, reviews, and check-ins transfer to the keeper. The duplicate Page's name, ID, posts, and photos are PERMANENTLY deleted. There is no undo.
5. Click **Request merge**. Some merges are instant; others queue a review by Meta (1–7 days).

### If the merge tool refuses
- Both Pages must be classified the same (e.g. both "Local business > Pawn shop"). Open Settings on each and align categories first.
- You must be a full admin on both — not just editor.
- Pages must represent the same physical location/entity.

---

## TASK 2 — Culpeper / Waynesboro portfolio acceptance (5 min)

**Why second:** also independent, and getting Pages into the right portfolio matters before you submit verification (verification covers the portfolio's contents).

### Steps

1. Open https://business.facebook.com/settings (sign in if prompted).
2. **Choose the "Valley Pawn" portfolio** (the one showing "9 Pages, 5 People"). Do NOT pick "Valley Pawn Waynesboro" — that's the separate sub-portfolio that's the SOURCE of these pending invites.
3. Left sidebar → **Notifications** OR **Requests** (location varies by Meta UI version). Look for the bell icon at top-right of the page if Notifications isn't in the sidebar.
4. You should see pending invites for the **Culpeper** Page and the **Waynesboro** Page asking to be added to the Valley Pawn portfolio.
5. Click **Accept** on each.
6. Verify they now appear under **Pages** in the sidebar (count should go from 9 → 11).

### If you don't see pending invites
- Check https://business.facebook.com/settings/pages — there's sometimes a "Pending" tab at the top of the Pages list.
- Check the "Valley Pawn Waynesboro" portfolio — the invite may need to be **sent FROM** there to the main Valley Pawn portfolio, not just accepted on the main side.

---

## TASK 3 — Meta Business Verification (15 min upload, 2–14 days Meta review)

**Docs are staged.** Three PDFs in `Refine Social Media/Meta Business Verification/`:
- `01_EIN_Letter_47-1198118.pdf`
- `02_Articles_of_Incorporation_FCF.pdf`
- `03_WellsFargo_Statement_Dec2025.pdf`

### Steps

1. Open https://business.facebook.com/settings/security (Valley Pawn portfolio selected).
2. Find the **Business Verification** card. Status should be "Not verified" or "Start verification".
3. Click **Start** / **Get verified**.
4. **Legal business info screen** — fill in EXACTLY as it appears on the EIN letter:
   - **Legal business name:** `Full Circle Finance Inc`
   - **DBA / Trade name:** `Valley Pawn`
   - **EIN (Federal Tax ID):** `47-1198118`
   - **Business address:** [use the address on the EIN letter — open `01_EIN_Letter_47-1198118.pdf` to copy it exactly]
   - **Phone:** business phone of record (must be reachable for the verification call/SMS)
   - **Business website:** valleypawn.com (or whatever's current)
5. **Document upload screen** — Meta typically asks for 1–2 of these. Upload:
   - **Articles of Incorporation:** `02_Articles_of_Incorporation_FCF.pdf`
   - **Tax document / EIN letter:** `01_EIN_Letter_47-1198118.pdf`
   - (Optional, if Meta asks for a third) Bank statement: `03_WellsFargo_Statement_Dec2025.pdf`
6. **Confirmation method** — Meta will offer phone or email. Pick **email** if it lists `zapvp1@me.com` or a business email you check daily. Phone is OK but you'll need to be reachable.
7. Click **Submit**.

### What happens after submit
- Status moves to "Pending review" / "In progress".
- Meta typically responds in 2–7 days, sometimes up to 2 weeks.
- If they reject: the most common reason is legal name mismatch between docs and what you typed. Double-check the EIN letter and re-submit.
- App Review (Task 4) cannot complete until this is verified, BUT you can submit App Review in parallel — Meta queues it and runs both reviews concurrently.

---

## TASK 4 — App Review for engagement metrics (20 min submission, 5–7 days Meta review)

**Goal:** unlock `pages_read_engagement` and `read_insights` so vp-content-batch / Friday close can pull post-level engagement (reactions, comments, shares, reach, impressions) via the Graph API.

**Written submission is drafted in** `Refine Social Media/META_APP_REVIEW_SUBMISSION.md`. Open it side-by-side with the Meta form — copy/paste each section into the matching field.

**Screencast you record yourself** — script is at the bottom of that file. Run through it once with QuickTime > New Screen Recording > capture your screen for ~90 sec while reading the script aloud and clicking through your app demonstrating each permission's use.

### Steps

1. Open https://developers.facebook.com/apps and pick the Valley Pawn app.
2. Left sidebar → **App Review** → **Permissions and Features**.
3. Find `pages_read_engagement` in the list. Click **Request advanced access**.
4. Fill in:
   - **How will you use this permission?** → paste from `META_APP_REVIEW_SUBMISSION.md` § pages_read_engagement → "Use case"
   - **Screencast** → upload your recording, OR paste a Loom/Drive URL
   - **Step-by-step instructions to test** → paste from `§ pages_read_engagement → Testing steps`
   - **Platform** → Web
5. Repeat for `read_insights`.
6. (Optional) If Friday close needs to list Pages programmatically, also request `pages_show_list` (use the third section in the submission doc).
7. At the App Review summary page → click **Submit for review**.
8. Meta confirms receipt by email within an hour. Review takes 5–7 business days typically.

### If the app doesn't exist yet
- Go to https://developers.facebook.com/apps/create/ → "Business" type → name it "Valley Pawn Content Engine" (or similar) → finish setup.
- Add the Facebook Login product (required to request these permissions).
- Then start at step 1 above.

---

## Status tracker — fill in as you go

| Task | Done at | Meta status |
|---|---|---|
| 1. Harrisonburg merge | | Instant / queued? |
| 2. Culpeper/Waynesboro accept | | |
| 3. Business Verification submitted | | Awaiting Meta review |
| 4. App Review submitted | | Awaiting Meta review |

Ping me when you've submitted all four and I'll set up scheduled tasks to check the verification and app review status every 48 hours so you don't have to manually monitor.
