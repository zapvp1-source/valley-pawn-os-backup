# Designer Goods Authentication — Findings (2026-09-29)

Question from Joshua: are Entrupy / Authentic Detective worth it, and what is our real designer-bag volume?

## Data used (Bravo pipeline output, read-only; zero Bravo UI contact)
- `buys-from-public` — monthly, all 5 stores, 2024-05-14 → 2026-04-30 (24 months, complete)
- `inventory` (CUL, WAY) + `inventory-details` (HAR, LEX, ROA) — SOLD items 2025-05-17 → 2026-05-17 (12 months, all 5 stores)
- `intake-detail` — daily loans + buys, all 5 stores, 2026-06-04 → 2026-09-28
- `sold-discount-detail` — daily sales 2026-08-12 → 2026-09-28
Bravo categories counted: `Handbag`, `Wallet`. Deduped by ticket/item number.
Tiers: luxury = LV, Gucci, Prada, YSL/Saint Laurent, Chanel, Dior, Hermès, Fendi, Burberry, Celine, Balenciaga, Bottega, Goyard, MCM. Mid = Coach, Michael Kors, Kate Spade, Dooney & Bourke, Tory Burch, Marc Jacobs.

## Buys from the public — 24 months, all stores
| Tier | Items | Paid |
|---|---|---|
| Luxury | 9 | $1,410 |
| Mid (Coach/MK/KS/Dooney etc.) | 62 | $2,111 |
| Other/unbranded | 9 | $186 |
| **Total** | **80** (~3.3/month) | **$3,707** |
By store: CUL 58, LEX 7, ROA 6, WAY 6, HAR 3. Culpeper is ~73% of all handbag buys.
Luxury buys (all Culpeper except one): MCM Aren messenger $240; LV Vernis card holder $60; LV card holder $75; YSL Sac de Jour nano $350; Gucci 85th hobo $250; Prada shoulder bag $150; LV S-Lock vertical wallet $200; Gucci crossbody (faux leather) $65; HAR Gucci bucket $20.

## Sold — 12 months (5/17/2025 → 5/17/2026), all stores
| Tier | Sold | Cost | Sold for | Gross profit |
|---|---|---|---|---|
| Luxury | 6 | $1,700 | $4,129 | $2,429 |
| Mid | 62 | $1,571 | $3,528 | $1,958 |
| Other | 11 | $180 | $438 | $259 |
| **Total** | **79** | **$3,451** | **$8,096** | **$4,645** |
Luxury sold: YSL $350→$1,000; Gucci $250→$700; LV card holder $60→$84; Prada $150→$600; MCM $240→$595; HAR LV Alma BB $650→$1,150. Since then: LV S-Lock wallet $200→$800 (9/5/2026).
Luxury = 8% of handbag units, 52% of handbag gross profit.

## Loans (6/4 → 9/28/2026, ~4 months)
8 handbag loans + 5 buys + 3 untyped. Only 1 luxury loan (HAR, LV bag, $100). One CUL loan note reads "SANDI APPROVED THIS LOAN".

## Economics conclusion
- Luxury volume ≈ 4–5 items/year bought, ~1 loan per quarter. Entrupy Petit ($1,499/yr) ≈ 60% of ALL luxury gross profit last year → does not pay.
- Authentic Detective pay-per-item (~$7–$60; Chanel bag $35, Hermès $60) at ~6–10 items/year ≈ $150–$400/yr → pays if it stops one bad buy every couple of years.
- Mid-tier (Coach/MK/KS/Dooney) average cost ~$34 — below any paid-authentication threshold; Sandi's in-store process covers it.
- Recommendation stands: adopt Authentic Detective for luxury-brand items ≥ ~$150 buy/loan and for eBay listing COAs; no Entrupy. Revisit if luxury volume passes ~15–25/month.
- Caveat: no record of any fake handbag loss was found; write-off data by category was not checked.

## Training
Sandi Cole's handbag verification process (Slack #general 2024-01-22) added to Valley Pawn Academy as lesson **L8-06 "Handbags: check it, price it, or pass"** (`Training Program/academy/lessons/L8/06_handbags_and_designer_goods.json`).
