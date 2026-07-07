# Valley Pawn Asset Audit — In Progress

**Started:** 2026-05-28
**Primary Facebook login:** zapvp1@me.com
**Goal:** Single primary admin login, single central Business portfolio, all IGs linked to corresponding Pages.

---

## Business Portfolios (known)

| Portfolio | business_id | Joshua's access | Notes |
|---|---|---|---|
| Valley Pawn (main) | 221863965111592 | Full control / admin | Central portfolio going forward. Business Verification submitted via domain. |
| Valley Pawn Waynesboro (sub) | 410777556554505 | **Partial access / Basic** | Mystery "IG valley pawn waynesboro" account has Full control. Needs to be reclaimed → decommissioned. |

---

## Facebook Pages — confirmed in tokens.json

| Key (tokens.json) | Page Name | Page ID | Followers | IG Linked (via API) | Notes |
|---|---|---|---:|---|---|
| Brand | Valley Pawn | 1603970336542485 | 1,708 | None | Brand parent page |
| Lexington | Valley Pawn-Lexington | 379605279045904 | 1,619 | None | |
| Waynesboro | Valley Pawn-Waynesboro | 303444680270846 | 1,234 | None | Currently in Waynesboro sub-portfolio. Transfer blocked by Query Error. |
| Culpeper | Valley Pawn- Culpeper | 100478091680300 | 873 | None | Currently in Waynesboro sub-portfolio. "Request Sent" pending. |
| Harrisonburg | Valley Pawn- Harrisonburg Va | 474248069342834 | 761 | None | Renamed from Dixie Pawn 2026-05-28. tokens.json updated. |
| Roanoke | Valley Pawn | 188243497698836 | **33** | None | ⚠️ Tiny audience — confirmed by Joshua as "we started fresh; the previous owner kept the original Page in the store sale." |

## Facebook Pages — additional / unconfirmed

| URL | Page ID | Status | Notes |
|---|---|---|---|
| facebook.com/profile.php?id=61553773147464 | 61553773147464 | **CONFIRMED Roanoke (Pro Mode profile)** | 33 followers, 6 reviews, address 2362 Peters Creek Road Roanoke VA 24017, phone 540-562-0776. SAME underlying entity as tokens.json "Roanoke" (188243497698836) — confirmed by matching follower count. The 18-digit ID is the internal Page ID; the 14-digit one is the URL/profile handle. Both work. Currently being renamed to "Valley Pawn-Roanoke" via Pro Mode profile rename (Meta review pending). Active — Sandra Hartman Cole posted "End of Month Blowout" 2026-05-28. |
| Valley Pawn-Harrisonburg (the 21-follower shell) | 795439020329931 | Decommissioned | Removed from portfolio. Still exists; Joshua is still Page admin via personal account. Should be deleted or left to decay. |
| "See all Pages" in mobile switcher | — | Not yet enumerated | Joshua's mobile switcher showed 8 visible profiles + "See all Pages" button. Click that to confirm complete list. |

---

## Instagram Accounts (known)

| Handle | In Portfolio | Linked to Page? | Notes |
|---|---|---|---|
| @valley_pawn | Main Valley Pawn | NO | "Login needed" |
| @vproanoke | Main Valley Pawn | NO | "Login needed" |
| @vpharrisonburg | Main Valley Pawn | NO | "Login needed". Disconnected from Dixie/renamed-Harrisonburg page 2026-05-28. |
| @valleypawn_waynesboro | Valley Pawn Waynesboro (sub) | Probably yes (to Waynesboro Page) | Causing the Query Error blocking the Waynesboro Page transfer. |

**Likely missing from audit:** @vpculpeper, @vplexington (Joshua said "we have IG pages set up i think on most of these"). Need to enumerate from his mobile IG app or Facebook portfolio sidebar.

---

## Mystery Accounts / Open Questions

1. **"IG valley pawn waynesboro" with Full control on the sub-portfolio** — what Facebook user account is this actually? Need to investigate by clicking on the account name in the sub-portfolio People list. Could be an old/alt Joshua login, an auto-generated identity, or worse — an external account.

2. **The Page at id=61553773147464** — Classic Page or Professional Mode profile? Which account admins it?

3. **Other Facebook accounts Joshua owns?** (jdavis@fcfpawn.com, jdavis@valleypawn.com, or other emails ever used to set up Pages)

4. **Why no IG-Page bindings show via Graph API on any of the 6 Pages?** Some of these IGs presumably are connected somehow if Joshua's been posting. Maybe portfolio-level link instead of Page-level link.

---

---

## Strategic decision REVISED 2026-05-29: Meta has forced the answer

**Update:** Meta has effectively deprecated Classic Page creation through the public flow. Attempting to create a Classic Page via facebook.com/pages/create on 2026-05-29 produced ANOTHER Pro Mode profile (URL `profile.php?id=61590260650279`). Verified by URL format and behavior.

**Implication:** Cannot achieve Classic-Page-only consistency. Your 5 existing Classic Pages (Brand, Lexington, Waynesboro, Culpeper, Harrisonburg) are grandfathered. Any future Page (new store, brand variant, side venture) will be Pro Mode by Meta's enforcement.

**Roanoke decision:** Keep old Pro Mode profile (61553773147464, 33 followers, 6 reviews, renamed to "Valley Pawn-Roanoke"). New empty Pro Mode Page just created was deleted. Mixed architecture (5 Classic + 1 Pro Mode for Roanoke) accepted as operational reality.

**Long-term strategic frame for any future Page:**
- Continue using the 5 Classic Pages as normal until Meta forces them to migrate to NPE
- Accept that ANY new Page will be Pro Mode/NPE — plan workflows accordingly
- Single-admin Pro Mode pages can still be operated via personal-mode workflows; just don't get the Classic Page tooling
- When Meta eventually forces Classic → NPE migration (announced periodically; no date yet), do it on Meta's schedule rather than fighting it

---

## Strategic decision logged 2026-05-28: Classic Pages > Pro Mode profiles for Valley Pawn

**Decision:** Standardize on Classic Pages across all locations.

**Reasoning:**
1. Multi-employee admin model (Sandra, Preston, Chadd post to their stores) — Classic Pages support roles; Pro Mode is single-owner
2. Brand owned by corporate entity (Full Circle Finance Inc), not by Joshua personally — Pro Mode permanently ties Page to personal Facebook account, creating succession/sale risk
3. Tooling stack (facebook-post, vp-content-batch, friday_close_engagement.py) all assume Classic Pages — Pro Mode breaks Graph API endpoints (confirmed: owner_business, /me/accounts behavior)
4. Business Manager portfolios + centralized ads + consolidated insights all assume Classic Pages
5. Compliance/audit cleanliness — Pro Mode bleeds into personal Facebook data; Classic Pages keep corporate-personal separation clean

**Counter not applicable:** Pro Mode would suit a personal-brand-driven business (think Gary Vaynerchuk personal brand). Valley Pawn is a multi-location regional retailer, not a personal brand.

**Roanoke decision:** Convert Pro Mode → Classic Page if Meta offers the option; otherwise create fresh Classic Page and accept 33-follower / 6-review loss as the cost of permanent architectural consistency. 33 followers is recoverable in 4-8 weeks of consistent posting. Permanent Pro/Classic mismatch costs compounding ops friction forever.

**Sub-question — "Business vs Creator" Pro Mode category:** Only relevant if you keep Pro Mode. Valley Pawn would pick Business (you sell goods/services, you're not building personal influence). But the bigger Classic vs Pro decision supersedes this.

---

## Architectural decision logged 2026-06-19: Hybrid stack with Publer as publishing layer

**Existing tools that stay (already paid for, no replacement):**
- Midjourney — hero image generation (vp-hero-image skill)
- Canva — brand template wrap and channel sizing (vp-asset-compose skill)
- vp-content-batch — weekly content plan orchestration, Bravo data integration, caption generation

**New publishing layer:**
- Publer Business tier ($50/mo for the 7-account scale Valley Pawn runs — 6 FB Pages + @valley_pawn IG). Handles scheduling + publishing. API key stored at `publer_config.json`. Account ID map at `publer_accounts.json`.

**Why this works:**
- Sub-portfolio Waynesboro/Culpeper ownership issue is bypassed entirely by Publer's OAuth — all 6 Pages including the previously-stuck Waynesboro (page_id 303444680270846) and Culpeper (page_id 100478091680300) connected successfully.
- Token wall ends — Publer manages Meta tokens internally; vp-content-batch only needs to know Publer's API key.
- friday_close_engagement.py pivots to read metrics from Publer's analytics endpoint (cleaner than direct Meta Graph API, no scope wall).
- Joshua's only ongoing operational task: weekly content review in Publer dashboard (~10 min Sunday night).

**Operational cost:** $50/mo Publer (vs zero before, but vs hours/week of Joshua-time before).

---

## Phase 1 — COMPLETE 2026-05-29

- [x] Enumerated all Pages via facebook.com/pages — 7 total (6 active in tokens.json + 1 shell)
- [x] Confirmed the two "Valley Pawn" profiles in the mobile switcher (the second was the just-deleted empty new Page)
- [x] Investigated 61553773147464 — Pro Mode profile, 33 followers, 6 reviews, renamed to "Valley Pawn-Roanoke"
- [x] Investigated "IG valley pawn waynesboro" admin — it's the @valleypawn_waynesboro IG identity itself, NOT a person. Meta won't show details because there's no human behind it.
- [x] Other Facebook accounts ever used by Joshua: PRIMARY zapvp1@me.com. Possibly an old business email account used at some point (jdavis@fcfpawn.com candidate) — not actively used, not certain. To investigate only if a Page/portfolio later resists his primary login.
- [x] IG accounts enumerated: @valley_pawn, @vproanoke, @vpharrisonburg, @valleypawn_waynesboro confirmed. @vpculpeper / @vplexington presence unconfirmed — TBD when we get to Phase 4 IG rebinding.

---

## Phase 2 PIVOT — abandon sub-portfolio fight, claim Pages directly

**Discovery:** Valley Pawn Waynesboro sub-portfolio has only ONE Full Control admin — the @valleypawn_waynesboro IG identity itself. No human can be contacted to promote Joshua. Meta literally displays: "Contact someone with full control of the business portfolio" — but that someone doesn't exist as a person.

**Path forward:** Don't fight for sub-portfolio ownership. Instead, claim the Pages from the MAIN portfolio side using "Claim a Page I admin" flow. Joshua has personal-account Page admin on Waynesboro and Culpeper Pages, so this should work regardless of sub-portfolio admin chaos. Sub-portfolio becomes empty husk.

**Sub-portfolio decommission strategy:**
- After Pages migrated out: file Meta Business Support ticket (https://www.facebook.com/business/help/support) to delete or reclaim the empty Valley Pawn Waynesboro sub-portfolio
- Until then: leave it dormant. It can't hurt anything once it has no assets.
