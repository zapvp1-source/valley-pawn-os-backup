# Bank Accounts Register — All Entities

Single source of truth for account/routing numbers. Check here FIRST before
searching mail, DocuSign, or asking the bank. Add a row whenever an account is
opened or closed. Last updated: 2026-09-05.

---

## DuPont Community Credit Union (DCCU) — Real Estate LLCs

Opened 2026-07-30 by Stephanie Key, Senior Business Accounts Advisor
(skey@mydccu.com, 540.946.3200 x3161). Business Online Banking registered 2026-08-10.

**ABA / routing number (all DCCU accounts): 251483311**

| Entity | Property | Member # | Full account (ACH/direct deposit) |
|---|---|---|---|
| Farming Infinity Virginia LLC | 14300 Woods Walk Ln, Midlothian VA | 1110918 | 10900001110918 |
| Farming Infinity Mountains LLC | 282 Bald Rock Rd, Verona VA | 1110927 | 10900001110927 |
| Farming Infinity Tennessee LLC | 148 Hardinberry St, Oak Ridge TN | 1110951 | 10900001110951 |

Registered address on all three: 844 Cypress Crossing Trail, Saint Augustine FL 32095
Phone on file: 804-930-4221 · Email on file: zapvp1@gmail.com

**Source documents (saved locally):**
`~/Desktop/New Bank Accounts/`
- VIEW_AND_SAVE_ONLY_OLB_ENROLLMENT_FIVApdf_.pdf  (Virginia)
- VIEW_AND_SAVE_ONLY_OLB_FIMTNpdf_FIMTN_Acco.pdf  (Mountains)
- VIEW_AND_SAVE_ONLY_OLB_FITNpdf_FITN_Accoun.pdf  (Tennessee)

DocuSign envelopes (account 320a0ff8-3001-4e1a-93b4-4fc3004b1116, sender skey@mydccu.com):
- FIVA  d4e91801-516f-8245-8092-44715a474a1f
- FIMTN ce9bd305-0106-8df7-8343-ce6d1be85ae2
- FITN  eab6ff1a-8023-85b3-82c5-4262a84cd6ba

**Notes / open threads:**
- FI Tennessee: TIN lists Joshua as sole member, operating agreement lists Hillary
  at 100%. EIN change submitted to IRS (as of 2026-07-30) — unresolved.
- Daily auto-sweep from Wells Fargo into DCCU: NOT possible. Confirmed 2026-09-03 by
  Stephanie Key — DCCU sweep only moves funds between two DCCU accounts. RTP/FedNow
  not live at DCCU yet. External transfers work but must be initiated manually.
- HELOC: existing line unaffected by the Bald Rock deed transfer into FI Mountains
  (Credit Dept, 2026-07-31). A written consent letter was requested for the operating
  agreement requirement — Credit Dept has never issued one before; still pending.
- Existing older DCCU account referenced in bill pay ends in 2291 (Farming Infinity LLC).
- **Business Online Banking User ID = the member number** (1110918 / 1110927 / 1110951) — per the
  OLB self-enrollment forms; there is no separate username. Five failed attempts locks enrollment.
- **Rent routing / ZILLOW ACCOUNT STRUCTURE (built by Joshua 2026-09-17).** There is now **one Zillow
  Rental Manager account per entity**, because Zillow allows only ONE deposit bank per account and
  changing it changes every property on that account. Accounts (all Apple IDs):

  | Zillow login | Entity | Property | Deposit bank |
  |---|---|---|---|
  | `zapvp1@me.com` | Farming Infinity Virginia LLC (by deposit account) | **14300 Woods Walk Ln — live** | **DCCU ...0918 — changed & verified 9/17** |
  | `fitnsee@icloud.com` | Farming Infinity Tennessee LLC | **148 Hardinberry St — live** | **DCCU ...0951 — verified 9/17** |
  | `fivirginia@icloud.com` | Farming Infinity Virginia LLC | *(empty — intentionally unused)* | — |
  | `fimtn@icloud.com` | Farming Infinity Mountains LLC | *(empty — Bald Rock pays via Airbnb/VRBO)* | — |

  **Bald Rock STR payouts (verified from platform email 2026-09-17):**
  - **Airbnb — correct and flowing.** Payout method switched from "Joshua Davis, Checking 2291" to
    **"Farming Infinity Mountains LLC, Checking 0927"** on **2026-08-14**. Payouts to 0927 since:
    8/14 $2,430.82 · 8/17 $2,883.98 · 8/22 $1,685.86 · 9/4 $4,150.63 = **$11,151.29**.
  - **⚠️ VRBO — pointed at 0927 but DISBURSEMENTS ARE FAILING.** Repeated "Vrbo Online Payments –
    Disbursement Failure" emails (9/2, 9/4, 9/9) on the same $1,399.96 (Debra Henning, res
    HA-TV6MLK), re-issued as a deposit statement 9/11. Text: *"Our recent attempt to deposit funds
    into the bank account you associated with your HomeAway Payments integration has failed."*
    VRBO labels the destination **"Account Name: DUPONT COMMUNITY CREDIT UNION 0927"** — i.e. the
    bank's name, not "Farming Infinity Mountains LLC" as Airbnb shows. A business-account
    name mismatch, or the member number (1110927) entered where the full ACH number
    (**10900001110927**) belongs, are the two likeliest causes. Re-enter VRBO's payout bank details.
    **CONFIRMED 2026-09-17 in the VRBO UI:** Payments → **Payout accounts**
    (`https://www.vrbo.com/p/opo/multiaccount`) lists BOTH payout accounts as
    **"Joshua Davis – ****2291"** and **"Joshua Davis – ****0927"**. The 0927 entry is titled
    **Joshua Davis personally**, but DCCU titles that account **Farming Infinity Mountains LLC** —
    Airbnb shows the LLC name and its deposits clear. **That name mismatch is the likely ACH
    rejection cause.** Fix path: the 0927 row → *Change bank account* → *Add new account*; VRBO
    first asks for the **full existing account number of 0927** as verification before allowing the
    change. Property 4752473 / unit 5326640, disbursement type "Check-in".

  **Why Woods Walk stayed on `zapvp1` instead of moving to `fivirginia`:** once Hardinberry was
  retired from `zapvp1` (9/17), Woods Walk became the ONLY property collecting there, so that
  account's single deposit bank applies to it alone. Switching the bank achieved the entity
  separation with zero tenant re-enrollment. Moving it to `fivirginia` would force Cynthia Stewart
  to re-enroll for no benefit — revisit only at her lease renewal (term ends 2/29/28).
  `zapvp1` also still holds 844 Cypress Crossing, but that is off-market/owner-occupied and
  collects nothing.

  Bald Rock's money actually arrives via Airbnb/VRBO, not Zillow, so `fimtn` matters only if it is ever
  listed for long-term rent.
- **There is NO Hillary Zillow account.** A 2026-09-17 session wrongly inferred one from a "Hi Hillary"
  Zillow setup email dated 8/10 — that email was generated on Joshua's own `zapvp1@me.com` account.
  Corrected by Joshua. Do not repeat it.

---

## How to extend this file

One section per institution. Always record: routing, member/account number, who
opened it, where the source PDF lives, and any unresolved item. Never store online
banking passwords here — those belong in the password manager.
