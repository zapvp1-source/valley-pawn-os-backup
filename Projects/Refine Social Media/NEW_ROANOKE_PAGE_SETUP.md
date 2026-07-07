# New Roanoke Classic Page — Setup Guide

**Goal:** Create a fresh Classic Facebook Page for the Roanoke store to replace the 33-follower Pro Mode profile (which can't be converted). Page joins the main Valley Pawn business portfolio. Sandra Hartman Cole keeps admin access.

**Cost being accepted:** 33 followers + 6 reviews lost from the Pro Mode profile. Recoverable in 4-8 weeks. Customers who wrote reviews are local; ask them to re-review on the new page.

**Benefit locked in forever:** Architectural consistency. Every script, every employee onboarding, every consolidation, every audit becomes cleaner.

---

## STEP 1 — Create the Page

Open Chrome. Make sure you're logged in as zapvp1@me.com. Paste:

```
facebook.com/pages/create
```

You'll see a page-creation wizard. Fill in EXACTLY these values:

### Page Name
```
Valley Pawn-Roanoke
```
(Matches your naming pattern: Valley Pawn-Lexington, Valley Pawn-Waynesboro, etc.)

### Category
Start typing: `Pawn Shop` → pick the "Pawn Shop" suggestion from the dropdown. Matches your other 5 stores.

### Description / Bio (paste exactly)
```
Family Owned Pawn Shop since 1988! 30 Day Warranties on Everything we sell. We buy Gold and Silver!
```

### Click "Create Page"

---

## STEP 2 — Add Business Info

After the Page is created, click into Settings → "Page details" or the equivalent. Fill in:

### Phone
```
+1 540-562-0776
```

### Address
```
2362 Peters Creek Road, Roanoke, VA 24017, United States
```

### Website
```
https://thevalleypawn.com
```

### Email
```
roanoke@fcfpawn.com
```
(Adjust if your Roanoke store uses a different email; you can leave blank if unsure.)

### Hours
Use the same hours as your other Valley Pawn locations. If you don't have these memorized, check Settings → Page setup → Hours on Valley Pawn-Lexington for the template, then duplicate. Common pawn shop hours: Mon-Fri 9-6, Sat 9-5, Closed Sunday — but VERIFY against your actual Roanoke operating hours before publishing.

---

## STEP 3 — Profile Picture + Cover Photo

Use the same brand assets the other Valley Pawn Pages use. Likely sitting in:
- `~/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Full Circle Finance/Marketing/` (brand logo)
- Or grab the current Roanoke Pro Mode profile's cover photo (storefront image) by saving it from facebook.com/profile.php?id=61553773147464 → right-click → Save image

Profile picture: Valley Pawn logo (the circular VALLEYPAWN mark — same as your other Pages use)
Cover photo: Roanoke storefront image (same one currently on the Pro Mode profile)

---

## STEP 4 — Add Page to Main Valley Pawn Business Portfolio

This step makes the new Page show up in your business management stack alongside the other 5 stores.

1. Go to `business.facebook.com/settings/pages?business_id=221863965111592`
2. Click `+ Add` (top right)
3. Choose "Add a Page" / "Claim a Page"
4. Search for "Valley Pawn-Roanoke"
5. Confirm

---

## STEP 5 — Connect @vproanoke Instagram

1. While in Business Settings, go to Pages → Valley Pawn-Roanoke → Connected assets tab
2. Add Instagram → pick @vproanoke
3. Authorize the connection
4. Confirm

This binds the IG to the new Classic Page so future cross-posts via vp-content-batch / facebook-post send to both.

---

## STEP 6 — Add Admins

The other Valley Pawn store pages have specific admins. For Roanoke:

- **Sandra Hartman Cole** — currently posts to the old Pro Mode profile. Add her as an Editor or Admin on the new Classic Page so she can continue posting.
- **Joshua Davis (you)** — already admin as the creator.
- **Lainie** (if applicable) — depending on whether she's an admin on the other stores.

To add: Settings → Page roles → Add Person → enter their Facebook account.

---

## STEP 7 — Update tokens.json (I'll do this)

Once you've created the Page and added it to the portfolio, tell me. I'll:
1. Call `/me/accounts` to grab the new Page's Page Access Token
2. Update `~/Library/.../facebook-post/data/tokens.json` Roanoke entry → new Page ID + new token
3. Save backup as `tokens.json.backup.<date>`
4. Run friday_close_engagement.py against the new Page to confirm wiring

---

## STEP 8 — Bridge post on the old Pro Mode profile

To minimize follower loss, post this on the OLD Pro Mode profile (id=61553773147464):

```
📢 We've moved! Follow our new Valley Pawn-Roanoke page for sales, new arrivals, and updates:

[Insert new Page URL]

This page will no longer be updated. Thank you for following us — see you at the new page!
```

Pin the post. Let the old profile sit for ~30 days, then delete it. (Or leave it as a dead pointer — your call.)

---

## STEP 9 — Re-review request to existing customers

The 6 customers who reviewed the old Pro Mode profile are likely local. Ask Sandra Hartman Cole (Roanoke store manager) to text or message them with a re-review request once the new Page is live. Sample message:

> "Hi [name], we set up a new Valley Pawn-Roanoke page on Facebook to keep things organized across our locations. Would you mind re-leaving your review at [new Page URL]? Means a lot — thank you for being a customer!"

That recovers the social proof, just on the new Page.

---

## Reference: existing Valley Pawn Page values for comparison

| Field | Brand | Lexington | Waynesboro | Culpeper | Harrisonburg |
|---|---|---|---|---|---|
| Category | Pawn Shop | Pawn Shop | Pawn Shop | Pawn Shop | Pawn Shop |
| Website | thevalleypawn.com | thevalleypawn.com | thevalleypawn.com | thevalleypawn.com | thevalleypawn.com |

Roanoke entry should follow the same template.

---

## When ready to execute

Tell me "starting Roanoke creation" and I'll watch your screen + guide each click in real-time. Or work through it on your own using this doc — either works. After Step 5 (Page in portfolio), I take over for token generation (Step 7).
