# Weekly Email — New Arrivals — 2026-05-28

## Campaign Metadata

| Field | Value |
|---|---|
| Brevo Campaign ID | #12 |
| Campaign Name | Weekly — New Arrivals — 2026-05-28 |
| Theme | New Arrivals (ISO week 22, mod 4 = 2) |
| Recipient list | Valley Pawn Customers #3 |
| Recipient count | 9,692 |
| Sender | Valley Pawn — jdavis@fcfpawn.com |
| Scheduled send | Thursday May 28, 2026 at 10:00 AM ET (America/New_York) |
| Status | Scheduled |
| Brevo URL | https://app.brevo.com/marketing-campaign/edit/12 |

## Copy

- Subject: Just in this week — tools, music & more
- Preview text: Fresh tools, a Jackson guitar, and one collectible we couldn't pass on.
- Hero eyebrow: JUST IN THIS WEEK
- Hero headline: Fresh on the floor across the Valley
- Hero subline: Six picks that just hit the case this week — pulled straight from our store managers' Slack channel.
- Primary CTA: "See what's new in-store →" → https://thevalleypawn.com
- UTM campaign slug: weekly_newarrivals_2026-05-28

## Featured Items (6)

1. Jackson King V Pro — Snow White (Roanoke, $799.99) — submitter Benjie
2. Lenox "Spring" Musical Egg (Lexington, $109.99) — submitter Uriah
3. Milwaukee M18 18V Force Logic Cable Cutter w/ CU/AL Jaws + Hard Case (Culpeper, $1,599 down from $1,899) — submitter Sandi
4. Paslode CFN325XP Cordless Framing Nailer (Culpeper, $249 down from $399) — submitter Sandi
5. DeWalt DCE151 Cable / Wire Stripper (Culpeper, $429.99) — submitter Sandi
6. Snap-On CT861 14.4V 3/8" Cordless Impact Wrench Kit (Roanoke, "Stop in for our best price" — pre-send DM to Benjie not answered before send) — submitter Benjie

## Dropped from this week's send

- Walker (Harrisonburg) — Leupold Rifle Scope, $1,099.94 — firearm-adjacent, Brevo deliverability concern. Coaching DM sent post-send.
- Preston/Waynesboro — photo-only submission, no item details. Coaching DM sent to Chadd with format example.

## Hard Requirements (all verified at pre-send preview)

- Valley Pawn logo in header
- Call AND Text buttons per store, with the actual phone number visible on BOTH (item cards + 5-store directory)
- Full 5-store directory at the bottom (Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke)
- Footer brand line is DBA-only ("Valley Pawn") — never "Full Circle Finance Inc"
- 30-day warranty mentioned (intro + master template trust strip)
- No firearms language anywhere
- No "Dixie Pawn" references

## Build Notes

- Duplicated VP Master Template (ID 11) per the documented flow.
- Replaced all 10 markers via JavaScript using the React-native-setter trick (Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set). Initial dispatchEvent reverted because the Brevo HTML editor textarea is React-controlled; the native-setter bypass persisted correctly.
- Final compiled HTML size: 55,162 chars (~55 KB — well under Gmail's 102 KB clipping threshold).
- Body item cards rendered as styled gradient blocks with item name + price overlaid, per the SKILL last-resort fallback when Slack file IDs aren't email-loadable (no permalink_public toggles on this week's submissions, and the sandbox doesn't have Slack auth tokens to fetch privately-shared files). Cards look intentional, not broken.
- Test email sent to jdavis@fcfpawn.com pre-schedule; preview verified end-to-end (logo, hero, all 6 cards, warranty strip, primary CTA, full 5-store directory, hours line, footer).

## Slack Activity

- 04:11 ET — Pre-send DM to Benjie (Roanoke) asking for Snap-On price; no reply by send time.
- 04:25 ET — Summary post to #email-campiagns: "New email is scheduled — Just in this week — tools, music & more" with link.
- 04:26 ET — Coaching DM to Walker (Harrisonburg) explaining the rifle scope drop.
- 04:26 ET — Coaching DM to Chadd (Waynesboro) with submission format requirements + working example.
- 04:26 ET — Coaching DM to Benjie (Roanoke) — Jackson V ran clean, Snap-On ran with "stop in for price"; include price next week.
