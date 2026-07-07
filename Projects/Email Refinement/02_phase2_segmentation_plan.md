# Phase 2 — Click-Based Auto-Tagging & Segmentation Plan

**Goal:** Turn anonymous email clicks into durable subscriber tags + reusable segments, so future campaigns can be sent to *interested* audiences instead of blasted to all 11,159 contacts every time.

**State today (verified via Brevo API):**
- 11,162 total contacts; 11,159 are on "Valley Pawn Customers" (list ID 3) — the master list every send currently goes to.
- Only the global Brevo attributes exist (`BLACKLIST`, `READERS`, `CLICKERS`) plus a handful of empty stock fields. **Zero topic/store tagging today.**
- Three lists exist; only list 3 is meaningful. No segments defined.

**What just unlocked Phase 2:** The Master Template's per-store Call/Text buttons now point at the new `/c/<store>` and `/t/<store>` HTTPS redirects with `utm_content` baked in. Every click is recordable. Combined with `utm_content=primary_cta` on every send's main button, we have enough signal to start tagging.

---

## Design philosophy

Two ways to "tag" in Brevo:
1. **Contact attributes** (boolean / string fields on the contact record). Durable across lists. Best for *persistent interest signals*.
2. **Lists or segments** (membership-based). Best for *audience-of-the-moment* — who to send what to.

**This plan uses attributes for the durable tag, then defines segments that read from those attributes plus from Brevo's built-in click-history index.** Attributes survive list moves; segments stay fresh.

---

## A. Custom contact attributes to create

All boolean unless noted. Category: `normal` (visible in contact UI).

### Topic-interest attributes (6)
Fired when the contact clicks the **primary CTA** of a themed send. The campaign's `utm_campaign` slug carries the theme:

| Attribute | Set when | Use case |
|---|---|---|
| `TOPIC_GOLD` | `utm_campaign` contains `gold` or `silver` AND `utm_content=primary_cta` | Send the next gold/silver-price-spike alert only to these |
| `TOPIC_LOANS` | `utm_campaign` contains `loan` AND `utm_content=primary_cta` | Pre-bill-cycle loan email goes to these |
| `TOPIC_LAYAWAY` | `utm_campaign` contains `layaway` AND `utm_content=primary_cta` | Oct–Dec layaway push goes to these |
| `TOPIC_APP` | `utm_campaign` contains `app` AND `utm_content=primary_cta` | App-adoption nudges to these |
| `TOPIC_RETAIL` | `utm_campaign` contains `retail` or `merchandise` AND `utm_content=primary_cta` | Used-merch deal alerts to these |
| `TOPIC_HOLIDAY` | `utm_campaign` matches any of the 11 holiday slugs AND `utm_content=primary_cta` | Pre-holiday warmups for engaged holiday clickers |

### Store-preference attributes (5)
Fired when the contact clicks **any link tagged with that store's `utm_content`** — call, text, or map:

| Attribute | Set when | Use case |
|---|---|---|
| `PREFERS_CULPEPER` | `utm_content` in `[store_culpeper_call, store_culpeper_text, store_culpeper_map]` | Culpeper-only sends (e.g. Culpeper-specific inventory, Wed-only-open reminders) |
| `PREFERS_WAYNESBORO` | Same pattern, `waynesboro` | — |
| `PREFERS_HARRISONBURG` | Same pattern, `harrisonburg` | — |
| `PREFERS_LEXINGTON` | Same pattern, `lexington` | — |
| `PREFERS_ROANOKE` | Same pattern, `roanoke` | — |

### Behavioral attributes (3)
| Attribute | Set when | Use case |
|---|---|---|
| `HIGH_INTENT` | Clicked any `store_*_call` OR `store_*_text` link in last 90 days (rolling) | Re-engagement reachable by phone — call list for managers |
| `PREFERS_TEXT` | More `store_*_text` clicks than `store_*_call` over rolling 90d | Send SMS-friendly content first |
| `ENGAGED_SOCIAL` | Clicked `utm_content=footer_instagram` | Cross-promote IG-only drops |

**Total: 14 new attributes.**

---

## B. Segments to define (the audiences we'll actually send to)

Once attributes exist, we build these 12 segments. Each is a saved filter on list 3.

| # | Segment name | Filter | Estimated send target |
|---|---|---|---|
| 1 | **All Engaged (90d)** | `READERS > 0` OR `CLICKERS > 0` in last 90d | The real list — replaces "blast to all" |
| 2 | **Gold/Silver Interested** | `TOPIC_GOLD = TRUE` | Gold-price-spike sends |
| 3 | **Loans Interested** | `TOPIC_LOANS = TRUE` | Pre-bill-cycle loan email |
| 4 | **Layaway Interested** | `TOPIC_LAYAWAY = TRUE` | Q4 layaway push |
| 5 | **App Adopters** | `TOPIC_APP = TRUE` | App-feature announcements |
| 6 | **Retail Buyers** | `TOPIC_RETAIL = TRUE` | "Just in" / "new arrivals" |
| 7 | **Holiday Engagers** | `TOPIC_HOLIDAY = TRUE` | Holiday warmups (sends 5–7 days before each holiday) |
| 8 | **High-Intent Callers** | `HIGH_INTENT = TRUE` | Manager call lists; reach-out campaigns |
| 9 | **Culpeper Locals** | `PREFERS_CULPEPER = TRUE` | Culpeper-only news |
| 10 | **Waynesboro Locals** | `PREFERS_WAYNESBORO = TRUE` | Waynesboro-only news |
| 11 | **Harrisonburg Locals** | `PREFERS_HARRISONBURG = TRUE` | Harrisonburg-only news |
| 12 | **Roanoke Locals** | `PREFERS_ROANOKE = TRUE` | Roanoke-only news |

(Lexington gets a segment too — that's 13. Cut the table for readability; spec is the same.)

---

## C. Automations that maintain the tags

For each topic and per-store attribute, one Brevo automation:

**Trigger:** Workflow start = "Clicked an email link"
**Filter:** Link URL contains `<pattern>`
**Action:** Update contact attribute → set field to TRUE
**Then:** End workflow

That's 6 topic automations + 5 store automations + 3 behavioral automations = **14 automations**.

Behavioral attributes (HIGH_INTENT, PREFERS_TEXT) require slightly more complex logic — a periodic scheduled workflow that re-evaluates rolling-90d click history. These can be Phase 2.5 once the simple set is live and producing data.

---

## D. Backfill strategy

A subscriber who clicked the Roanoke Call button two weeks ago — before Phase 2 was live — should still be tagged `PREFERS_ROANOKE`. Brevo's automations only fire forward in time, so we need a one-shot backfill.

**Approach:** Pull the last 90 days of click events from `/v3/smtp/statistics/events?event=clicks` for each campaign, group by contact + URL, derive which attributes should be TRUE, and PATCH each contact via `/v3/contacts/{email}`.

This is a one-time script. Estimate: 10–15 minutes to write, runs in ~5 minutes against the API. **Defer until automations are live — backfill is a fast follow.**

---

## E. Build order (recommended)

1. **Create the 14 attributes** via Brevo API (`POST /v3/contacts/attributes/{category}/{name}`). 14 API calls, ~1 minute.
2. **Build the 11 simple automations** in the Brevo UI under Automation → New Workflow. Each is the same template (click → check URL → update attribute → end). ~45 minutes.
3. **Define the 12 segments** under Contacts → Segments → New segment. ~15 minutes.
4. **Backfill from last 90d click events.** ~30 minutes.
5. **Verify with a test send** to a small internal list — click each tracked link, watch attributes flip within ~5 minutes.

Total build: ~2 hours. After that, every send produces structured audience data automatically.

---

## F. What changes for future sends

- **Send target switches** from "Valley Pawn Customers (all 11,159)" → relevant segment.
- Example: the monthly Gold & Silver email goes to "Gold/Silver Interested" (estimated 1,500–3,000 contacts after 90d of tagging) instead of all 11K. Same number of clicks, half the unsubscribes, better deliverability reputation.
- The weekly newsletter still goes to "All Engaged (90d)" as the broad audience.
- One-off "Culpeper has a Black Friday tools event" goes to Culpeper Locals only — no spammy "this isn't my store" unsubscribes from the other 9,500 contacts.

This is the focus the project instructions called for.

---

## Open questions for Joshua

1. **Approve attribute names?** I've used SCREAMING_SNAKE_CASE per Brevo convention (matches LASTNAME, FIRSTNAME). Any preference otherwise?
2. **Approve the 14-tag list?** Should we add tags I haven't proposed — e.g. `TOPIC_FIREARMS_BUYBACK`, `TOPIC_JEWELRY`?
3. **Backfill: yes or no?** Recommendation = yes; ~30 min one-time cost, unlocks 90 days of behavioral data immediately.
4. **HIGH_INTENT decay rule:** keep as 90d rolling, or shorter (60d) so it stays a fresh signal? Recommendation = 90d to start, tune after 2 months of data.
