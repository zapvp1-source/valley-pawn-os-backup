# Conversion Tracking & Monitoring Plan

The landing pages emit a structured set of events through both `gtag()` and `dataLayer`. This document defines the full tracking architecture, GTM configuration, GA4 setup, and the weekly review process for monitoring conversions and bounces.

---

## 1. Event Schema (Emitted by the Landing Page JS)

| Event | When It Fires | Parameters |
|---|---|---|
| `page_view` | GA4 default | `page_location`, `page_title` |
| `calc_started` | First input change in calculator | `store_id`, `store_city`, `karat`, `unit` |
| `calc_quoted` | Calculator displays an offer (first time per session) | `store_id`, `store_city`, `karat`, `weight_grams`, `offer_low`, `offer_high` |
| `cta_call_click` | Any phone button tap | `store_id`, `location` (header/hero/footer/store_block/mobile_sticky/all_locations_[city]) |
| `cta_text_click` | Any SMS button tap | `store_id`, `location` (same options) |
| `calc_text_offer` | "Text me this offer" button tap (post-calc CTA) | `store_id`, `store_city` |
| `chekkit_open` | Chekkit widget opens (needs Chekkit API hook) | `store_id` |
| `chekkit_message_sent` | Chekkit message submitted | `store_id` |
| `scroll_25` / `scroll_50` / `scroll_75` | Scroll depth thresholds | `store_id` |
| `faq_open` | FAQ accordion opened | `store_id`, `question` |
| `bounce_after_quote` | `calc_quoted` fired, then page unload within 30 seconds | `store_id`, `time_to_bounce_sec` |

All events automatically include `store_id` (slug) and `store_city` (display name) so you can segment any report by store.

---

## 2. GA4 Setup

### 2.1 Conversion Events
Mark these as conversions in GA4 (**Admin → Events → toggle "Mark as conversion"**):
- `cta_call_click`
- `cta_text_click`
- `calc_text_offer` *(highest-intent — the user got a quote AND tapped to text)*
- `chekkit_message_sent`

### 2.2 Custom Dimensions (Admin → Custom Definitions → Custom Dimensions)

Create user/event-scoped dimensions so the parameters are reportable:

| Dimension Name | Event Parameter | Scope |
|---|---|---|
| Store ID | `store_id` | Event |
| Store City | `store_city` | Event |
| Karat | `karat` | Event |
| Weight (g) | `weight_grams` | Event |
| Offer Low | `offer_low` | Event |
| Offer High | `offer_high` | Event |
| CTA Location | `location` | Event |
| Bounce Time (s) | `time_to_bounce_sec` | Event |

After setup it takes GA4 ~24 hours to start showing data in these dimensions.

### 2.3 Audiences
Build these audiences for retargeting and analysis:

- **Quoted, Didn't Convert** — fired `calc_quoted` but not any conversion event in the session
- **High-Value Quotes** — fired `calc_quoted` with `offer_high > 500`
- **Engaged Browsers** — fired `scroll_75` but no `calc_started`
- **Multi-Visit Considerers** — sessions ≥ 2, fired `calc_quoted` at least once

---

## 3. Google Tag Manager Configuration

If you use GTM (recommended), set up the following.

### 3.1 Variables (Variables → User-Defined)

| Variable Name | Type | Configuration |
|---|---|---|
| `DLV - store_id` | Data Layer Variable | `store_id` |
| `DLV - store_city` | Data Layer Variable | `store_city` |
| `DLV - karat` | Data Layer Variable | `karat` |
| `DLV - offer_low` | Data Layer Variable | `offer_low` |
| `DLV - offer_high` | Data Layer Variable | `offer_high` |
| `DLV - location` | Data Layer Variable | `location` |
| `DLV - time_to_bounce_sec` | Data Layer Variable | `time_to_bounce_sec` |

### 3.2 Triggers

For every event listed in Section 1, create a Custom Event trigger:

```
Trigger Name: VP - calc_quoted
Type:         Custom Event
Event Name:   calc_quoted
This trigger fires on: All Custom Events
```

Repeat for: `calc_started`, `cta_call_click`, `cta_text_click`, `calc_text_offer`, `chekkit_open`, `chekkit_message_sent`, `scroll_25`, `scroll_50`, `scroll_75`, `faq_open`, `bounce_after_quote`.

### 3.3 Tags

For each trigger, create a GA4 Event tag:

```
Tag Name:        GA4 - VP - calc_quoted
Tag Type:        Google Analytics: GA4 Event
Configuration:   {{GA4 Config}}    [your existing GA4 config tag]
Event Name:      calc_quoted
Event Parameters:
  store_id      → {{DLV - store_id}}
  store_city    → {{DLV - store_city}}
  karat         → {{DLV - karat}}
  offer_low     → {{DLV - offer_low}}
  offer_high    → {{DLV - offer_high}}
Trigger:         VP - calc_quoted
```

### 3.4 Special — Bounce After Quote (uses sendBeacon)

The bounce event fires on `beforeunload`. GTM's standard trigger can miss this on unload. Set up like this:

```
Tag Name:        GA4 - VP - bounce_after_quote
Tag Type:        Google Analytics: GA4 Event
Event Name:      bounce_after_quote
Event Parameters:
  store_id            → {{DLV - store_id}}
  time_to_bounce_sec  → {{DLV - time_to_bounce_sec}}
Trigger:         VP - bounce_after_quote
Tag Settings:    Enable "Send page view as a separate event" → off
                 Set tag firing priority to 100 (high) to ensure it fires before unload completes
```

---

## 4. Conversion Funnel (GA4 Explorations)

Build a funnel exploration in GA4 (**Explore → Funnel Exploration**):

```
Step 1: page_view          (Any Sell Gold page — filter by URL contains "sell-gold")
Step 2: calc_started
Step 3: calc_quoted
Step 4: ANY of:
        - cta_call_click
        - cta_text_click
        - calc_text_offer
        - chekkit_message_sent
```

Segment by `store_id` to see per-store drop-off.

### Key ratios to watch
- **Visit → Calc Start** target: 25%+
- **Calc Start → Quote** target: 80%+ (anyone who starts should usually finish)
- **Quote → Conversion** target: 8%+
- **Conversion → In-store visit** (manually tracked via "how did you hear about us") target: 30%+

---

## 5. Looker Studio Dashboard

A dashboard makes the weekly review fast. Recommended layout:

### Page 1 — Overview
- **Big numbers:** Total Visits, Quotes Generated, Quotes-to-Action Rate, Texts Sent, Calls Made
- **Trend:** Last 30 days, lines for quotes, calls, texts
- **By store:** bar chart of total conversions by `store_city`

### Page 2 — Calculator Performance
- **Karat distribution:** pie chart by `karat` (where most quotes land — guides marketing)
- **Offer value distribution:** histogram of `offer_high` (what size offers people are getting)
- **Quote-to-action rate by offer range:** does $50–$200 convert at a different rate than $500+?

### Page 3 — Bounce Analysis
- **Bounce after quote rate:** % of `calc_quoted` followed by `bounce_after_quote`
- **Bounce time distribution:** at what time do they bounce?
- **Bounce by karat:** are bounces concentrated on a particular karat? (signal that payout range is off for that karat)

### Page 4 — Source Attribution
- **Conversions by traffic source:** organic, Google Business Profile, email, social, direct
- **Conversions by landing page:** which spoke is converting best?

### Setup
Connect Looker Studio to the GA4 property → import the report template (I can prepare a template file on request) → schedule a weekly email digest every Monday at 7am to `jdavis@fcfpawn.com`.

---

## 6. Weekly Review Cadence

Every Monday morning, scan the dashboard. The numbers you actually care about:

1. **Total conversions this week vs. last week** — are leads going up?
2. **Quote-to-action rate** — if it drops, the offer math is too low OR the CTA isn't compelling
3. **Bounce-after-quote rate** — if it climbs, people are price-shopping; consider:
   - Tightening the offer range (e.g. show a midpoint instead of low/high)
   - Adding a "we'll beat any written offer" line near the quote
   - Adding a time-limited bonus ("text within 1 hour to lock in")
4. **Per-store performance** — which stores are converting best? Which need GBP/local link-building?
5. **Karat distribution** — are most quotes 10k/14k (broken jewelry crowd) or 22k/24k (bullion crowd)? Guides which audience to target in ads.

If any metric is alarming (conversion rate halves, bounces double, page traffic drops 50%), check:
- Did spot price move dramatically? (Update VP_GOLD_SPOT)
- Did a competitor launch a similar page?
- Did Google issue a ranking update? (Search for major SEO news)
- Did the Chekkit widget stop responding? (Test a message from a personal phone)

---

## 7. A/B Testing Roadmap (Optional, Month 2+)

Once you have a baseline, test these variants one at a time using Google Optimize successor (Convert.com, VWO, or even simple URL-parameter splits):

| Test | Variant A | Variant B | Expected Impact |
|---|---|---|---|
| Calculator default karat | 14k (current) | 10k | More broken-jewelry seller engagement |
| Quote display | Range ($295–$359) | Midpoint ($327) | Lower bounce, possibly lower conversion |
| CTA after quote | "Text me this offer" | "Lock in this price" | Stronger urgency framing |
| Hero headline | "Get Your Offer in Seconds" | "Walk Out With Cash Today" | Action vs. speed framing |
| Payout range | 70–85% (current) | 75–88% | More attractive quote = higher engagement, but watch in-store fulfillment cost |

Run each test for at least 2 weeks or 200 conversions, whichever is later.

---

## 8. Privacy & Compliance

- **Cookie consent:** the events fire whether or not the user consents to cookies. If you collect personal data via Chekkit, ensure consent is captured there.
- **GA4 IP anonymization:** on by default.
- **PII rule:** the events do NOT include any user-entered text or phone numbers. They include karat/weight/offer (no PII). Safe.
- **Cal compliance:** if you have any California traffic, ensure the privacy policy on `thevalleypawn.com` is current (mentions GA4, Chekkit, GTM).

---

## 9. Quick-Start Test (Do This After Deploy)

1. Open `thevalleypawn.com/sell-gold-culpeper/` in Chrome with DevTools → Console open
2. Type `window.VP_DEBUG = true` to enable debug logs
3. Click around — should see console messages like:
   ```
   [VP TRACK] calc_started {store_id: "culpeper", ...}
   [VP TRACK] calc_quoted {store_id: "culpeper", offer_low: 295, ...}
   [VP TRACK] cta_text_click {store_id: "culpeper", location: "hero"}
   ```
4. Open GA4 Real-Time → confirm the same events appear within 30 seconds
5. Confirm GTM Preview Mode shows the tags firing

If all four steps pass, tracking is operational.
