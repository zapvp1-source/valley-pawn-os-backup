---
name: weekly-jacksonville-property-search
description: Monday 9:30 AM — Search 8+ platforms for Jacksonville FL RETAIL-ONLY properties (2,500+ SF), compile results, and send email to jdavis@fcfpawn.com
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


## Weekly Jacksonville, FL RETAIL-ONLY Property Search

**Goal:** Find ALL available RETAIL properties in Jacksonville / Duval County, FL suitable for a new pawn shop location (2,500+ SF), email results to jdavis@fcfpawn.com, and draft broker inquiries for new listings.

### CRITICAL FILTER: RETAIL ONLY
- ONLY include properties classified as RETAIL (shopping centers, strip malls, freestanding retail, outparcels, plazas)
- EXCLUDE: flex, industrial, warehouse, office-only, medical-only, business parks, metal buildings

### ZONING NOTE
- Jacksonville may require special use permits for pawn shops in certain zones
- Include a zoning warning in every email so Joshua can verify before signing leases
- Contact Jacksonville Zoning Section (214 N. Hogan St) for confirmation

### Step 1: Search Multiple Platforms
Search ALL of these for Jacksonville / Duval County FL RETAIL properties for lease OR sale, 2,500+ SF:

1. **LoopNet** — "site:loopnet.com Jacksonville FL retail for lease"
2. **CommercialSearch** — https://www.commercialsearch.com/retail/us/fl/jacksonville/
3. **Crexi** — "site:crexi.com Jacksonville FL retail"
4. **CityFeet** — "site:cityfeet.com Jacksonville FL retail"
5. **Brixmor** — https://www.brixmor.com/leasing/retail-space/fl/jacksonville
6. **Regency Centers** — https://www.regencycenters.com/city-pages/jacksonville-florida-retail-space
7. **Kimco Realty** — Jacksonville portfolio
8. **Phillips Edison** — Jacksonville grocery-anchored centers
9. **Sembler Company** — Jacksonville properties
10. **General web search** — "Jacksonville FL retail space for lease 2500 sq ft"

Collect: address, property name, size, rate/price, lease type, source, notes, listing URL. Verify each is RETAIL.

### Step 2: Compose & Send HTML Email
1. Create HTML draft via `gmail_create_draft` to jdavis@fcfpawn.com
2. Subject: "Jacksonville FL RETAIL Properties - Weekly Search ([date])"
3. Include zoning warning prominently
4. Group by type: Grocery-Anchored Centers, Strip/Inline, Outparcels/Freestanding, For Sale
5. Open Gmail drafts in Chrome, click the draft, click Send
6. Verify sent confirmation

**IMPORTANT:** Gmail MCP only creates drafts. You MUST use Chrome to open the draft and click Send.

### Step 3: Draft Broker Inquiries for NEW Listings
For new retail listings without published rates, create Gmail draft inquiry emails introducing Valley Pawn (Joshua Davis, CEO, Full Circle Finance Inc DBA Valley Pawn, family-owned since 2014, 5 VA locations, expanding to FL, 2,500-3,500 SF retail, thevalleypawn.com). Leave "to" field empty.

### Target: jdavis@fcfpawn.com | Size: 2,500+ SF | Type: RETAIL ONLY | Area: Jacksonville / Duval County, FL