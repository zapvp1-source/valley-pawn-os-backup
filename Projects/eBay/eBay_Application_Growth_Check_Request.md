# eBay Application Growth Check — Request

**Application (keyset):** FullCirc-ValleyPa-PRD-[see ~/ebay_weekly_rankings.py] (Production)
**Company:** Full Circle Finance Inc DBA Valley Pawn — 5 retail pawn locations in Virginia (FFL dealer)
**Contact:** Joshua Davis
**APIs used:** Trading API (primary), plus supporting read calls

---

## What the application does
This is a first-party seller tool that manages Valley Pawn's own live eBay inventory across our
five store seller accounts. It is not a multi-tenant/ISV product — every call acts on listings we
own. Current functions:

- Pull active-listing and sales/ranking reports for merchandising decisions.
- Revise our own live listings (price markdowns, title/category cleanup, aged-inventory rules).
- Optimize listing photography: download the seller's own images, enhance and upscale the primary
  photo to 1600px, and re-host via eBay Picture Services, then apply with a single revise.

## Why we need higher limits
We maintain several hundred active listings across five accounts, each with multiple photos. Routine
maintenance (photo optimization, markdown passes, title fixes) legitimately requires a high volume of
`UploadSiteHostedPictures` and `ReviseFixedPriceItem` calls in a short window. We are currently
constrained by the **per-call daily caps** on those two calls (not just the 5,000/day application
total), which forces us to spread routine work across multiple days.

## Efficiency measures already implemented
We have engineered the tool to be a good API citizen and to minimize wasted calls:

- **Pre-flight budgeting:** every run calls `GetAPIAccessRules` first and refuses to start if the
  remaining daily budget for the target calls is below a safety buffer.
- **Primary-photo-only mode:** we revise only the primary image, cutting picture-upload calls ~7x.
- **Auto-stop on limit:** the moment eBay returns a usage-limit or 503 response, the run halts and
  saves state — no blind retry storms against the endpoint.
- **Exponential backoff** on transient 500/502/503 responses; **pacing** between calls.
- **Idempotent resume:** completed items are recorded in state and skipped on the next run, so no
  listing is ever processed twice.
- **Fully reversible:** original image URLs are retained so any change can be rolled back.

## The ask
Please raise our daily call limits — specifically the per-call caps on **UploadSiteHostedPictures**
and **ReviseFixedPriceItem**, and the overall application daily limit — to support routine
maintenance of our own multi-account inventory. We monitor real usage via the Developer Analytics
API `getRateLimits` call and will stay within granted limits.

Thank you for reviewing.
