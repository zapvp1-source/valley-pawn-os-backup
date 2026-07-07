# Valley Pawn Public-Facing Audit — 2026-06-22

**Source of truth:** valley-pawn-context skill (canonical NAP).
**Scope:** All public-facing surfaces — directories, socials, owned web, email channel.

---

## Phase 1: Top 5 Directories

| Store | Google | Bing | Apple Maps | Facebook | Yelp |
|---|---|---|---|---|---|
| Culpeper | ✅ | ✅ | ✅ | ⏳ defer (low risk) | ⏳ defer (low risk) |
| Waynesboro | ✅ | ✅ | ✅ | ⏳ defer | ⏳ defer |
| Harrisonburg | ⚠️ Ste 22 (CORRECT — see notes) | 🚨 **DIXIE PAWN** | 🚨 **DIXIE PAWN, no VP** | ⏳ defer | ⏳ defer |
| Lexington | ✅ (MapQuest aggregator has stale 439 E Nelson) | ✅ | ✅ | ⏳ defer | ⏳ defer |
| Roanoke | ✅ (Suite C present) | ✅ (Suite C **missing**) | 🚨 **GOLD-N-PAWN, no Suite C** | ⏳ defer | ⏳ defer |

## Phase 2: Social Profiles

| Profile | Status | Notes |
|---|---|---|
| Instagram @valley_pawn | ✅ | "Virginia's modern pawn shop. Fair deals + 30-day warranty. Family-owned since 2014." Link → thevalleypawn.com. 211 posts, 94 followers. |
| TikTok @thevalleypawn | ✅ | Brand bio clean. |
| X @valleypawnva | ✅ | Display name "Valley Pawn" (Joshua-rename stuck). Family-owned since 2014. Joined June 2026. |
| YouTube (search) | ✅ | No legacy names surface. |
| FB brand parent @thevalleypawn | ✅ | Name shows "Valley Pawn". |

## Phase 3: Owned Web

| URL | Status | Notes |
|---|---|---|
| thevalleypawn.com (home) | ✅ | All 5 phones present. No legacy names. |
| /culpeper through /roanoke | ✅ | JSON-LD shows correct NAP per store. Harrisonburg shows "Ste 22" — confirmed correct by Joshua. |
| /follow | ✅ | Works. |
| follow.thevalleypawn.com | ✅ **FIXED** | Was SSL-broken; CNAME deleted this session. |
| /giveaway-rules | ✅ | Works. |

## Phase 4: Other Public

| Channel | Status | Notes |
|---|---|---|
| eBay store | ⏳ defer | Public, not yet audited |
| Brevo email template footer | ⏳ defer | Needs Brevo login |
| BrightLocal multi-directory | ⏳ defer | Joshua's session not visible to MCP |

---

## Critical drift requiring login-gated fixes

| # | Severity | Store | Surface | Issue | Fix path |
|---|---|---|---|---|---|
| 1 | 🚨 Critical | Harrisonburg | Bing | Shows "Dixie Pawn, Inc - Harrisonburg Va" alongside Valley Pawn | Bing Places admin → push name correction. Known chronic — may revert; verify after 24-48 hrs. |
| 2 | 🚨 Critical | Harrisonburg | Apple Maps | Shows "Dixie Pawn" only, NO Valley Pawn | Apple Business Connect admin → claim/update listing |
| 3 | 🚨 Critical | Roanoke | Apple Maps | Shows "Gold-N-Pawn" only, NO Valley Pawn, NO Suite C | Apple Business Connect admin → claim/update listing |
| 4 | ⚠️ Minor | Roanoke | Bing | Address missing "Suite C" | Bing Places admin → add suite |
| 5 | ⚠️ Minor | Lexington | MapQuest (aggregator) | Shows stale "439 East Nelson St" alongside correct address | Aggregator drift — handled via BrightLocal push or wait for Google source-of-truth to propagate |

## Drift requiring Joshua's manual install

| # | Action | Where |
|---|---|---|
| 6 | Install Ste 22 patch | Settings → Capabilities → valley-pawn-context. Delta staged at `VALLEY_PAWN_CONTEXT_DELTA_2026-06-22.md` |

## Fixed this session

| # | Item | Status |
|---|---|---|
| ✓ | follow.thevalleypawn.com SSL error | DELETED broken CNAME via WordPress.com DNS. Subdomain now NXDOMAIN cleanly. |
| ✓ | BUSINESS_OS Addendum 6 | Written, capturing all findings + fixes. |
| ✓ | valley-pawn-context Ste 22 delta | Staged for Joshua to install. |
| ✓ | Harrisonburg "Ste 22" truth | Resolved (Joshua confirmed: Ste 22 IS correct). |

---

## Recommended next steps (handoff sequence)

1. **Joshua: log into Bing Places** at https://www.bingplaces.com/ → search for Harrisonburg listing → push "Valley Pawn" name correction + verify Suite C is correct on Roanoke
2. **Joshua: log into Apple Business Connect** at https://businessconnect.apple.com/ → claim/correct Harrisonburg (Dixie → Valley Pawn) + Roanoke (Gold-N-Pawn → Valley Pawn, add Suite C)
3. **Joshua: install valley-pawn-context Ste 22 delta** via Settings → Capabilities
4. **When ready: get BrightLocal session into MCP-driven Chrome tab** → I drive the 30+ aggregator sweep
5. **Re-audit 24-48 hours after pushes** to confirm Bing/Apple haven't reverted (Harrisonburg has chronic Dixie Pawn reversion history)
