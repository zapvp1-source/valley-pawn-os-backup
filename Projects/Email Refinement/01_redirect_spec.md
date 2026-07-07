# Email Measurability — WordPress Call/Text Redirects

**Goal:** Make every Call and Text click in a Valley Pawn email measurable in Brevo, so the north-star metric (Calls + Texts per 1,000 recipients) actually has data behind it.

**The problem:** Brevo's click tracking only wraps `http://` and `https://` links. `tel:` and `sms:` links bypass tracking entirely — invisible in Brevo stats. Today, when a subscriber taps "Call Roanoke" in an email, we have no record it happened.

**The fix:** Put a tiny HTTPS redirect on `thevalleypawn.com` between Brevo and the dialer. Email links point to `https://thevalleypawn.com/c/<store>?utm_content=...`. Brevo logs the click. WordPress 302-redirects to `tel:+1<phone>`. Customer's phone dials. We get the click count, the UTM tag, and the auto-tagging trigger — all from one HTTPS URL.

---

## Redirect Table — 10 URLs

| Path | Destination | Store | Phone |
|---|---|---|---|
| `/c/culpeper` | `tel:+15404455510` | Culpeper | (540) 445-5510 |
| `/t/culpeper` | `sms:+15404455510` | Culpeper | (540) 445-5510 |
| `/c/waynesboro` | `tel:+15402216346` | Waynesboro | (540) 221-6346 |
| `/t/waynesboro` | `sms:+15402216346` | Waynesboro | (540) 221-6346 |
| `/c/harrisonburg` | `tel:+15405744500` | Harrisonburg | (540) 574-4500 |
| `/t/harrisonburg` | `sms:+15405744500` | Harrisonburg | (540) 574-4500 |
| `/c/lexington` | `tel:+15404618349` | Lexington | (540) 461-8349 |
| `/t/lexington` | `sms:+15404618349` | Lexington | (540) 461-8349 |
| `/c/roanoke` | `tel:+15405620776` | Roanoke | (540) 562-0776 |
| `/t/roanoke` | `sms:+15405620776` | Roanoke | (540) 562-0776 |

All redirects: **HTTP 302** (so users can retry; not permanent in case a phone number changes).

---

## UTM Convention

Brevo auto-appends UTM params from the campaign settings, but for store-attribution to work, each link also needs `utm_content` baked in.

**Pattern:** `?utm_content=store_<store>_<channel>`

Examples:
- Culpeper Call button → `https://thevalleypawn.com/c/culpeper?utm_content=store_culpeper_call`
- Roanoke Text button → `https://thevalleypawn.com/t/roanoke?utm_content=store_roanoke_text`

Brevo fills in `utm_source=brevo`, `utm_medium=email`, `utm_campaign=<send-slug>` automatically based on campaign config — no need to hand-stamp those.

`utm_content` values used in the master template:
- `store_<name>_call` — Call button (5 variants)
- `store_<name>_text` — Text button (5 variants)
- `store_<name>_map` — Maps directory link (5 variants)
- `primary_cta` — main button
- `footer_instagram` — IG icon
- `footer_website` — site button

---

## Implementation Options (pick one)

### Option A — Redirection plugin *(recommended)*
- **If installed:** add 10 source/target rules via the plugin UI or REST API
- **If not installed:** install it (free, 2M+ active installs, maintained by John Godley)
- Supports `tel:` and `sms:` as redirect targets out of the box
- Logs each redirect (bonus second layer of click data, useful for cross-check against Brevo)

### Option B — Tiny mu-plugin
- Single PHP file at `/wp-content/mu-plugins/valley-pawn-redirects.php`
- ~20 lines: read `$_SERVER['REQUEST_URI']`, match `/c/<store>` or `/t/<store>`, call `wp_redirect()` with appropriate `tel:`/`sms:` scheme
- Needs `allowed_redirect_hosts` filter or `wp_redirect` to bypass scheme validation
- Pro: no plugin dependency. Con: requires file upload access.

### Option C — `.htaccess` rewrite *(if Apache)*
- 10 `RewriteRule` lines
- Pro: zero PHP, fastest. Con: requires SFTP/SSH access and Apache.

**Recommendation:** A. Already a well-supported plugin most WP installs have. If the site doesn't have it, install + configure takes ~3 minutes.

---

## Verification Plan

After build, test these in order:

1. **Curl test (sandbox):** `curl -I https://thevalleypawn.com/c/culpeper` → expect `HTTP/2 302` and `Location: tel:+15404455510`.
2. **Desktop browser:** Chrome on Mac → URL bar should prompt "Open Phone app?" (no errors).
3. **iOS Safari:** Tap link → FaceTime / Phone app opens with number filled.
4. **Android Chrome:** Tap link → dialer opens with number filled.
5. **Brevo click stat:** Send test campaign, click each link, confirm a click registers within 10 minutes against the expected `utm_content`.

---

## What this unlocks

Once live, every weekly + monthly + holiday send produces structured click data Brevo can split by:
- Store (Culpeper Calls vs Roanoke Calls)
- Channel (Call vs Text intent ratio per store)
- Theme (gold-email subscriber → which store?)

Which becomes the Phase 2 auto-tagging feedstock: subscribers who keep clicking Culpeper get tagged `prefers_culpeper`. Subscribers who click the gold email's primary CTA get tagged `interested_gold`. Etc.

No measurability → no segmentation → no focus. This is the unlock.
