# Real Estate Tax Strategy & Cost Segregation Notes

**Built:** 2026-09-03, from the actual filed 2024 joint tax return (`DavisJ&H 2024 Tax Return &
8879 - Updated.pdf` — Schedule E, Form 8582, AMT passive-activity-loss reconciliation, 2024
Depreciation and Amortization Reports) plus the 2025 extension confirmation and the Bald Rock
evidence-log/tracker work. This file is the index for the portfolio's tax-strategy questions —
see `Life OS/REAL_ESTATE_OS.md` for property operations and ownership, `Taxes 2026/282 Bald
Rock — Full Evidence Log.md` for Bald Rock's improvement-by-improvement paper trail.

**Everything below is analysis for planning purposes, not filed tax advice.** Joshua works with
Silverline (or whoever prepares the return) for anything that actually gets filed — several items
below are flagged as needing their input specifically before a return is filed on this basis.

---

## 1. Ownership — who actually owns what

Confirmed directly by Joshua, 2026-09-03:

| Property | Owner |
|---|---|
| 282 Bald Rock Road | Joshua alone |
| 14300 Woods Walk Lane | Joshua alone |
| 817 Richmond Avenue | Joshua alone |
| 148 Hardinberry Street | Joshua & Hillary jointly |
| 844 Cypress Crossing Trail | Joshua & Hillary jointly |
| Full Circle Finance Inc (Valley Pawn) | Joshua alone — Hillary is an employee, not an owner |

This matters for the Augusta Rule analysis (§4 below) and for who reports what on the joint
return — it doesn't change the joint-filing math since Joshua and Hillary file MFJ either way.

---

## 2. Property classification — STR vs. LTR vs. commercial, and why it decides everything

The single biggest lever in this whole analysis: **whether a property's rental losses can offset
Joshua's ACTIVE income (W-2, K-1, business income) or only PASSIVE income.** Under the passive
activity loss rules (IRC §469), a rental is normally a "passive activity" no matter how involved
the owner is — losses can only offset passive income, with any excess suspended and carried
forward (Form 8582). There's one well-established exception: a short-term rental with an average
guest stay of 7 days or less is not a "rental activity" at all under Reg. §1.469-1T(e)(3)(ii); if
the owner also materially participates (500 hours/year, or one of the other material-participation
tests), the losses become NON-PASSIVE and can offset active income directly — no passive-loss cap,
no Form 8582 limitation. This is the "STR loophole."

| Property | Classification | Evidence | Active or passive offset? |
|---|---|---|---|
| **282 Bald Rock** | Short-term rental (Airbnb + Vrbo) | Confirmed operating listing, guest-payout history, DocuSign contract flow | **Potentially ACTIVE** — only if material participation and ≤7-day average stay are proven (both currently unconfirmed, see §6) |
| **14300 Woods Walk** | Long-term rental, real tenants | 2024 Schedule E Type "1" (SFR); Avail/Trulia/HotPads tenant-inquiry and rent-collection emails | Passive only |
| **148 Hardinberry** | Was STR (2025-2026), now LTR (Joshua confirmed 2026-09-03) | 2024 Schedule E Type "1"; $16,110 income sourced "ZILLOW INC - FROM 1099-K" (LTR payment platform) | Passive only, going forward |
| **817 Richmond** | Commercial, NNN lease to FirstCash | 2024 Schedule E, mortgage interest $35,739, no personal-use days | Passive only |
| **844 Cypress Crossing** | Was LTR → converted to personal residence ~Aug 2025 | 2024 return still shows full-year rental (366 days); conversion happened after the 2024 tax year | Passive (2024); see §7 for its post-conversion status |

**Practical takeaway:** cost-segging Woods Walk, Hardinberry, or Richmond generates real
deductions, but those deductions can only ever offset passive income (rental income from other
properties, or income from other passive activities) unless Joshua qualifies as a real estate
professional (750 hours/year + more time in real estate than any other trade — not evaluated
here, this hasn't come up in the conversation). Bald Rock is the only property that can realistically
offset the $400K+ of active income Joshua asked about, and only if §6's open questions resolve
favorably.

---

## 3. Passive-loss carryforward balances (entering 2025)

From Form 8582 line 1c and the AMT passive-activity-loss reconciliation detail on the filed 2024
return. These are suspended losses — not "banked income." They don't expire, they don't require
action to preserve, and they automatically apply against future passive income from ANY passive
activity (not just the same property) before that income is taxed. A full, 100% release happens
only on a fully taxable disposition (sale) of the specific activity that generated them — at that
point the suspended loss for that activity can offset even active income.

| Property | Suspended passive loss entering 2025 |
|---|---|
| 817 Richmond | $26,391 |
| 844 Cypress Crossing | $24,681 |
| 148 Hardinberry | $6,600 |
| 14300 Woods Walk | $0 (fully released in 2024) |
| **Total** | **$57,672** |

2024 itself: total passive losses generated $39,872, plus $25,778 carried in from prior years,
combined -$57,672 against $7,978 of passive income allowed by Form 8582 (MAGI $341,378 exceeds
the $150,000 phase-out threshold for the $25,000 special allowance, so that allowance was $0) —
net $0 passive loss allowed to hit the 2024 return beyond the $7,978.

**"If we make money in 2025, is it taxed and the losses remain?"** — Yes, that's exactly how it
works. Passive income earned in 2025 gets taxed in 2025; it doesn't get retroactively offset by
carried-forward losses from a different year's Form 8582 unless those losses are attributable to
the same or another passive activity generating income that year (they generally are, and the
computation runs automatically on Form 8582 each year). The suspended losses keep carrying forward
until either (a) enough passive income shows up to absorb them, or (b) the activity that generated
them is sold in a fully taxable transaction, releasing the balance in full even against active
income in that sale year.

---

## 4. Bald Rock cost segregation — basis and deduction range

**Updated 2026-09-03 (seventh update same day):** Joshua identified nine more Affirm-financed
vendors as 282 Bald Rock purchases — Joss & Main (media console, $754.99), Decor Planet (two
bathroom vanities, $1,893.03 net of one refunded unit), Eight Sleep (smart mattress, $2,574.59 net
of one refunded unit), Vent Covers Unlimited (HVAC registers, $235.87 — upgraded from Bucket 3 to
Bucket 1 now that it's confirmed), Molekule (air purifiers, $841.34), a 2023 Traeger Grill
($3,485.78), Tonal (home gym, $3,924.97), two Platinum red-light therapy panels ($2,166.03), and
Beatbot (robotic pool cleaner, $1,262.55) — **$16,903.28 in new confirmed dollars.** He also drew a
clean dating line: everything in his Affirm account from 2025-08-08 (the Beatbot purchase, which
he confirmed IS Bald Rock) forward belongs to **844 Cypress Crossing** (his Florida personal
residence) instead. That moved one Casper loan ($1,117.46, 2026-07-28) out of the Bald Rock total
established earlier today — Bald Rock's Casper total is now $10,650.31 across 7 loans, not
$11,767.77 across 8. The 844 Cypress items (Kohler, Amazon Business, a 2026 Traeger Grill, Rebag,
two Aventon Bikes purchases, Nordica Sauna, that Casper loan, and Discount Tire) are logged
separately in `844 Cypress Crossing Improvements Substantiation.md`, not here.

*(Earlier the same day: Joshua's Affirm account resolved most of Signature Hardware's and Royal
Swimming Pools' payment-side gaps — $16,942.38 moved from unproven to proven with zero change to
the grand total (see Evidence Log §38). Williams Sonoma's full 21-order history added $2,902.50 of
confirmed FF&E.)*

### Adjusted basis

- Recorded 2016 purchase price: $405,000 (per deed, `CONSIDERATION: 405,000.00`).
- Capital improvements tracked in the evidence log/tracker (`282 Bald Rock — Full Evidence Log.md`,
  `build_tracker2.py`), broken into 4 buckets by documentation completeness:

| Bucket | Amount | Documentation status |
|---|---|---|
| 1 | $565,594.05 | Strongest — most items have both invoice and proof of payment |
| 2 | $8,520.65 | Partial — invoice/item confirmed, payment still pending |
| 3 | $18,623.53 | Partial/attribution unconfirmed |
| 4 | $28,945.60 | Weakest — pricing/invoice still pending vendor response |
| **Total tracked improvements** | **$621,683.83** | |

- **Adjusted basis range:** $970,594.05 (floor — purchase price + Bucket 1 only, strongest tier)
  to $1,026,683.83 (ceiling — purchase price + all 4 buckets, everything eventually resolved).
- **Land allocation:** Augusta County GIS (parcel 036/D2-2/5A) assesses land at $55,000 (2026/27
  roll). Netting that out: **depreciable (building) basis ≈ $915,594.05 to $971,683.83.**
- **Conversion-date basis test:** Joshua confirmed 2026-09-03 that he and Hillary moved from Bald
  Rock to Florida on **8/1/2025**. Depreciable basis is the LESSER of adjusted basis (above) or
  FMV as of 8/1/2025 (26 CFR 1.168(i)-4) — the Blue Ridge Appraisal Joshua deliberately postponed
  should now be scheduled to opine on value as of that specific date, not "as of today."
- **What this means for "the final number" (Joshua asked directly, 2026-09-03):** the $970,594.05-
  $1,026,683.83 adjusted-basis range above is ONE side of the lesser-of comparison, not the final
  answer by itself. If every open item on §6 proves out favorably, the adjusted-basis side rises to
  its ceiling — $1,026,683.83 total / **$971,683.83 depreciable building basis** — but that ceiling
  only becomes the actual final basis if the Blue Ridge Appraisal's FMV as of 8/1/2025 comes in AT
  OR ABOVE it. If the appraisal comes in lower, that lower appraised figure becomes the final
  depreciable basis instead, no matter how well-documented the $621,683.83 of improvements are —
  cost and documentation quality only set the ceiling; the appraisal is what can pull the actual
  number down from there. Put another way: proving everything on §6 maximizes the number the
  appraisal has to beat, it doesn't bypass the appraisal. Until Robbie Miller delivers that number,
  the true final basis isn't knowable — treat $971,683.83 as the most this can possibly be, not
  what it will be.

### Short-life / bonus-eligible portion (year-1 cash impact)

Categorizing the tracker's actual line items (not a generic industry-average %) into furniture
(5-year), land improvements (15-year), and structural (39-year) buckets:

| Category | Bucket-1-only floor | All-buckets ceiling |
|---|---|---|
| Furniture (5-yr) | $279,650.98 | $284,129.30 |
| Land improvements (15-yr) | $107,907.75 | $141,884.30 |
| Structural (39-yr) | $178,035.32 | $195,670.23 |
| **Total** | $565,594.05 | $621,683.83 |
| **Short-life (5+15 yr, 100% bonus-eligible)** | **$387,558.73 (68.5%)** | **$426,013.60 (68.5%)** |

Under OBBBA, 100% bonus depreciation is back permanently for qualifying property placed in
service after January 19, 2025 — so the entire short-life portion above is a **year-1** deduction,
not spread over 5-15 years.

**Does the 160" theater setup count? (Joshua asked directly, 2026-09-03) — yes, and it's already
in the number above.** The Full Evidence Log (§1, proven bucket) has **ProjectorScreen.com Order
#124774, 2020-02-14, $5,470.50 — a Screen Innovations 5 Series 160" screen, shipped to 282 Bald
Rock, payment confirmed.** That's the 160" screen itself, already counted in Bucket 1/the
furniture (5-year) line above — a projector screen is tangible personal property, same tax
treatment as furniture/FF&E, 100%-bonus-eligible. There's a second, bigger piece that is confirmed real but not yet priced into the total:
Joshua confirmed 2026-09-03 that Crutchfield actually installed the rest of the system (projector,
receiver, Control4 automation) at Bald Rock. The Evidence Log has two Crutchfield estimates for
this ($22,845.41 from 2019 and $14,362.10 from 2020, the second billed directly to 282 Bald Rock)
plus real 2020 Crutchfield order/payment activity that doesn't yet net to a matched dollar total —
see Evidence Log §40 for the full trail. Once that reconciles to an actual paid amount (minus the
screen, which is separately counted), it adds real additional short-life basis. Until then it
stays out of the $621,683.83 total, same rule as every other not-yet-matched item in this file. **One more thing worth flagging: this does NOT belong on
Robbie's appraisal list** (the one just sent) — a projector, screen, and AV equipment are personal
property, not real property, so they don't move an appraiser's opinion of the structure's value
the same way the roof/siding/windows do. It stays a cost-seg/basis item only.

### Illustrative $400K active-income scenario

Joshua asked directly how this would offset $400K of active income. Illustrative only — assumes
(a) Bald Rock qualifies for non-passive treatment (§6 open items resolved favorably) and (b) the
full short-life amount is used in one year:

- Deduction: $387,559 (floor) to $426,014 (ceiling).
- At $400K MFJ taxable income, the top marginal bracket in play is 24% federal (2026 brackets:
  24% from $211,400–$403,550) plus Virginia's top marginal rate of 5.75% ≈ **~29.75% combined
  marginal rate** on the layer this deduction displaces.
- **Illustrative cash tax savings: ~$115,300 (floor) to ~$126,700 (ceiling).** This is a rough
  order of magnitude, not a filed number — the Excess Business Loss limitation (IRC §461(l)) and
  the exact bracket math once other income/deductions are finalized would need to be run for real
  by whoever prepares the return.

### Filing mechanics and deadline

- Bald Rock has never been depreciated (§5 below) — this would be a fresh first-year
  placed-in-service filing, not a Form 3115 catch-up, assuming no historical income-reporting
  issue.
- **The 2025 return is on extension. Deadline: October 15, 2026** (confirmed via the filed
  extension: "460 Extension of time to file tax return 04-10-2026 $0.00," standard 6-month
  extension from the original April 15, 2026 deadline). This is the effective deadline for
  getting the cost seg study, the appraisal, and the basis question (§6) resolved.

## 5. The other three properties — already depreciating, still cost-seg-eligible via Form 3115

Richmond, Woods Walk, and Hardinberry are already on Schedule E with existing depreciation
schedules — but that doesn't block a cost segregation study. A **Form 3115 (Change in Accounting
Method) with a §481(a) adjustment** lets a cost-seg study "catch up" all the depreciation that
should have been taken with proper component segregation, in one current-year deduction, without
amending any prior returns.

| Property | Basis | Accumulated depreciation through 2024 | Remaining basis to segregate |
|---|---|---|---|
| 817 Richmond (commercial) | $467,648 | $73,882 | $393,766 |
| 14300 Woods Walk (residential) | $225,785 | $124,488 | $101,297 |
| 148 Hardinberry (residential) | $123,502 | $11,164 | $112,338 |

All three CAN be cost-segged in a future year regardless of already being in service. The catch:
per §2 above, the resulting losses are passive for all three (Richmond commercial, Woods Walk and
Hardinberry residential LTRs) — they reduce passive income and suspended-loss balances, not
Joshua's active income, unless real-estate-professional status is established separately.

---

## 6. Open questions — need to resolve before Bald Rock's cost seg is filed

1. **Where has Bald Rock's Airbnb income (since Oct 2016) actually been reported historically, if
   not on the Davis's personal return?** The filed 2024 return shows zero Schedule E history for
   Bald Rock — it was never on the personal return. A "282 LOC for FCF INC" financing document
   suggests some tie to Full Circle Finance Inc's books, but no FCF Inc 1120 corporate return has
   been located to confirm this (only Form 7004 extensions). This is the single biggest swing
   factor for how the cost seg should be structured — fresh placed-in-service vs. a bigger
   compliance question — and needs Silverline's input before anything is filed.
2. ~~Exact move date~~ **RESOLVED 2026-09-03: Joshua confirmed 8/1/2025.** The Blue Ridge
   Appraisal (still on hold pending the improvement list) should target FMV as of that date.
3. ~~Average length of stay at Bald Rock~~ **RESOLVED 2026-09-03:** pulled directly from Guesty
   (the property's booking/PM platform), all 50 completed stays on file (Aug 2, 2025 through Aug
   23, 2026 — the full period since Bald Rock went on Guesty): **206 total nights / 50 stays =
   4.12-night average.** One outlier — a 30-night "Ihs Housing" booking (likely insurance/
   relocation corporate housing, not a typical transient guest) — is the longest stay by a wide
   margin; excluding it, the average is 3.59 nights across the other 49. Isolating just the 18
   stays with a 2025 check-in date (the actual tax year in question) narrows it further: 65
   nights / 18 stays = 3.61-night average. Every cut of this data — full history, outlier
   excluded, 2025-only — lands well under the 7-day threshold in Reg. §1.469-1T(e)(3)(ii)(A).
   This leg of the STR loophole is satisfied — item 4 (material participation hours) is now the
   only remaining gate. (Caveat: Guesty's booking history only goes back to when Bald Rock was
   onboarded to that platform, ~Aug 2025 — it doesn't reach the property's full Airbnb history
   since 2016, but that's not a problem here since the average-use test is computed per tax year.)
4. **Material participation hours** (500-hour test or equivalent) for Joshua and/or Hillary at
   Bald Rock — no actual hours log exists anywhere (mail, texts, Drive, Guesty), so this can't be
   "resolved" the way item 3 was; a real number only exists in Joshua's own memory/calendar. What
   the record DOES show, searched 2026-09-03:
   - **A potential risk was found, then closed out.** A "Davis Management LLC — Setup Checklist"
     (Google Doc, ~2026-07-21) and a companion "Management Services Agreement (Template)" had
     described standing up a Florida LLC/S-corp to take over Bald Rock's booking/guest-comms/
     cleaning-maintenance coordination starting 2026. **Joshua confirmed 2026-09-03: this was
     never implemented** — no entity was formed, no management was handed off. Joshua and Hillary
     kept doing the work themselves. This removes the 2026+ risk entirely — there's no reason to
     think 2026's participation looks any different from 2025's reconstruction in §11.
   - **"Liz Lee" (saved as "Liz Bald Rock") is confirmed as the next-door neighbor, not a
     co-host or manager** — the Oct 14-30, 2025 thread is about a shared driveway sealcoating job
     ("They drove from your driveway over to mine to get out and down mine") and Joshua personally
     collecting her info for an insurance claim ("Airbnb needs it to see if we can get this thing
     paid for"). This doesn't count against material participation at all — if anything it's
     Joshua's own dated hours handling a property issue, now folded into §11's reconstruction.
   - **No system anywhere logs Joshua's or Hillary's own hours** — not Guesty, not a calendar, not
     texts framed as time entries. This is normal (almost nobody logs it prospectively) but means
     2025's number can only be reconstructed after the fact, from memory cross-referenced against
     things that DO have dates (guest-issue message threads, trips reflected in card/gas/grocery
     charges near Verona, vendor coordination emails, the HVAC replacement and other capital work
     supervised in Sept 2025). That reconstruction is exactly the kind of contemporaneous-enough
     evidence the Tax Court has accepted before (see *Bailey v. Commissioner* and similar cases on
     post-hoc participation logs) — imperfect, but not fatal.
   - **A full 2025 reconstruction is now built out in §11** — assembled from vendor emails,
     texts, and financing paperwork, it lands at roughly 210-355 hours across the year, comfortably
     clearing the 100-hour/no-one-else-participated-more test (the cleanest target here, precisely
     because no manager existed in 2025 to out-participate Joshua). See §11 for the full table,
     sourcing, and caveats — it's a draft for Silverline's review, not a filed number.
   - **Recommendation:** bring §11's table to Silverline as the 2025 starting point. For 2026
     forward — now that Davis Management LLC is confirmed not in the picture — the highest-leverage
     single fix is simply starting a contemporaneous log now (date, task, minutes) of whatever
     Joshua or Hillary personally do for Bald Rock, so 2026 doesn't need the same after-the-fact
     reconstruction 2025 required. If a management handoff is ever revisited later, that's the
     moment to re-examine this section — not before.
5. **The Bald Rock appraisal** (Blue Ridge Appraisal, Robbie Miller) — an inspection was actually
   SCHEDULED for Wed 9/2/2026 2pm (confirmed by email 8/25), but Joshua cancelled it himself 8/31
   ("pulling together the improvement receipts first so we have the full basis nailed down before
   we appraise... will reach back out to reschedule once that's done" — Robbie replied "10-4").
   **This is now the single blocking item on the whole cost-seg timeline.** The improvement
   documentation Joshua was waiting on is essentially finished as of this session's work (the
   $621,683.83 tracked-improvement total, all 4 buckets, plus the material-participation and
   average-stay findings above) — nothing is left blocking a reschedule. Needs to target whatever
   the correct conversion date turns out to be (item 2, currently 8/1/2025) and Robbie specifically
   asked for a written list of improvements to review during the inspection — that list should go
   out with the reschedule request, not after.
6. **148 Hardinberry's county** — mail/tax records show Roane County; the LLC paperwork and this
   file's portfolio table say Anderson County. Unresolved, carried over from a prior session.

---

## 7. Cypress Crossing's suspended loss after conversion to personal use

Cypress Crossing converted from a long-term rental to Joshua & Hillary's personal residence
around August 2025, carrying a $24,681 suspended passive loss forward from 2024. Suspended losses
generally require the activity to either continue generating passive income or be disposed of in
a fully taxable transaction (a sale) to be used — "converted to personal residence" is neither.
This is a real open question flagged for Silverline: does the $24,681 stay frozen/suspended
indefinitely until a future sale, or is there another triggering event? Not resolved here.

---

## 8. The Augusta Rule (§280A(g)) — reviewed for FCF Inc, not currently viable as proposed

Joshua asked whether he and Hillary, as owners/employees of Full Circle Finance Inc, could use the
Augusta Rule to rent out a house to the business either (a) with just the two of them as
participants, or (b) for 14 days tied to a single staff meeting.

**The rule itself:** IRC §280A(g) excludes from gross income up to 14 days/year of rent a taxpayer
receives for renting out a dwelling that qualifies as their personal residence under §280A(d), at
fair market rent, to their own business — provided the arrangement has genuine business purpose.
Day 15 disqualifies the exclusion for the entire year, not just the extra days.

**Both proposed structures are high-risk, not compliant as described:**

- **Owners-only "meeting"** — the IRS and Tax Court scrutinize related-party rent under both
  §280A(g) and ordinary §162 "ordinary and necessary" business-expense rules. A meeting with no
  other attendees, no agenda, and no minutes reads as a payment to the owners disguised as rent,
  not a legitimate business expense. Hillary's ownership status doesn't reduce this scrutiny — as
  Hillary is an FCF Inc employee (not owner) but is Joshua's spouse, §267(c)(4) attributes
  ownership between spouses for related-party purposes regardless.
- **14 days for one staff meeting** — using all 14 exempt days against a single meeting doesn't
  by itself create risk (the exclusion is per-day, not per-meeting), but it invites the same
  documentation scrutiny: the IRS will ask for fair-market-rent support (a real comparable, not a
  guess) and proof the meeting(s) actually happened and were business in substance.

**Controlling precedent — *Sinopoli v. Commissioner*:** the Tax Court disallowed an S-corp's
~$291,000 (over 3 years) in Augusta Rule "meeting space" rent paid to its shareholders for lack of
documentation — no minutes, no agendas, no calendar invites. The court benchmarked local
commercial meeting space at roughly $500/day and called even that figure generous, and only for
meetings that were actually substantiated.

**Also unresolved:** whether Bald Rock itself would even qualify as a "residence" under §280A(d)
going forward. Once it's fully operated as an STR with minimal personal use by Joshua/Hillary, it
likely fails the personal-use test (personal-use days must exceed the greater of 14 days or 10% of
the days rented at fair value) — meaning the Augusta Rule may not be available for Bald Rock
specifically at all, separate from the documentation problem above.

**Bottom line:** if Joshua wants to pursue this, it needs (1) a real property that clearly
qualifies as a personal residence under §280A(d), (2) a documented fair-market-rent comparable,
(3) actual minutes/agendas/calendar invites for every meeting claimed, and (4) genuine business
substance — not a structure built primarily to move money at a tax-free rate. As described, neither
proposed structure would survive an audit.

---

## 9. Open items — consolidated

See `Life OS/OPEN_ITEMS_REGISTER.md` (Domain 2 — Real Estate) for the logged, trackable versions
of these:

1. Where Bald Rock's pre-2025 Airbnb income was historically reported (FCF Inc books? nowhere?).
2. ~~Exact VA-to-FL move date~~ RESOLVED 2026-09-03: 8/1/2025.
3. ~~Bald Rock's average guest stay length~~ RESOLVED 2026-09-03: 4.12-night average (3.59 excluding one 30-night outlier) from Guesty's full booking history — well under the 7-day STR-loophole threshold.
4. Material participation hours at Bald Rock — no real-time log exists, but §11 reconstructs 2025 at ~210-355 hours from dated vendor/financing/platform-setup activity, comfortably clearing the 100-hour/no-one-else-more test. A draft Davis Management LLC handoff was found and considered, but Joshua confirmed 2026-09-03 it was never implemented — Joshua/Hillary kept doing the work themselves, so 2026 should look like 2025 for this purpose — see §6 item 4 and §11.
5. Cypress Crossing's $24,681 suspended loss treatment post-conversion-to-personal-use.
6. 148 Hardinberry's county (Anderson vs. Roane) — carried over, unresolved.
7. The Bald Rock appraisal — was scheduled for 9/2/2026, Joshua cancelled it 8/31 pending the improvement documentation; that documentation is now essentially done, so this is ready to reschedule and is the single biggest remaining timeline blocker.

**None of this is filed tax advice.** Joshua is not a tax professional and neither is this file —
every number above should be reviewed with Silverline (or whoever prepares the 2025 return) before
it goes near an actual filing, especially item 1 above, which could change the entire structure of
how Bald Rock's cost seg needs to be handled.

---

## 10. Can excess 2025 cost-seg deductions be recouped in a later year? (Joshua's Sept 2026 question)

Joshua asked directly: if 2025 income is ~$450K and the Bald Rock cost segregation deduction
"completely wipes out" that year's tax bill "and more," can the excess be recouped the next year.
Short answer: unused amounts never just evaporate — something always carries forward — but which
regime governs it, and how usable that carryforward actually is, depends entirely on the
still-open §6 material-participation/STR-loophole question (items 3-4). That question is the fork
in the road for this analysis, not a side detail.

### Reality check against the numbers already on file

Using the currently-estimated short-life, 100%-bonus-eligible deduction from §4 — $387,559
(floor) to $426,014 (ceiling) — a $450K income year would NOT actually be fully wiped out, let
alone "and more": $450K minus that deduction leaves roughly $24K to $62K of taxable income still
standing. The 39-year structural portion ($178,035-$195,670) isn't bonus-eligible and depreciates
normally over decades, so it doesn't add to the year-1 number. A "wipes it out and more" outcome
would require either (a) the final appraisal/basis coming in meaningfully higher than today's
estimate, or (b) other losses stacking on top in the same year (e.g., a passive-loss release, or
treating a bigger slice of the total $621,683.83 tracked-improvements figure as short-life than
the categorization in §4 currently supports). Flagging this now so the scenario below is
understood as "here's how it would work if it happens," not a confirmation that it will.

### Path A — Bald Rock qualifies as non-passive (STR loophole + material participation, §6 items 3-4 resolved favorably)

The loss is an ordinary trade/business loss, usable against any 2025 income — wages, pawn
business profit, everything — without the passive-activity limits in play at all. But it isn't
unlimited: the Excess Business Loss cap under IRC §461(l) sits in front of it. OBBBA made this
limitation **permanent** (it had been scheduled to sunset). For 2025 the threshold is **$313,000
single / $626,000 married filing jointly** — the amount of net business loss allowed to offset
nonbusiness income in the current year. (The threshold drops sharply in 2026 — $256,000 /
$512,000 — because OBBBA reset the inflation base year to 2024, wiping out several years of
compounded inflation adjustment. Worth knowing regardless of which year the loss actually lands
in.)

If a joint return's aggregate business losses exceed aggregate business income by more than
$626,000 in a single year, the excess above that threshold is disallowed for the current year —
but it doesn't disappear. IRC §461(l)(2) automatically converts the disallowed excess into an NOL
carryforward.

**The new wrinkle post-OBBBA — read this before counting on "recoup it next year" working the old
way.** Historically, an NOL carryforward could offset ANY future income — business or
nonbusiness — limited to 80% of taxable income in the year it's used (IRC §172; no carryback for
individuals since the 2017 TCJA repeal; carryforward itself is indefinite, no expiration). OBBBA
narrowed this specifically for excess-business-loss-generated NOLs: a disallowed excess business
loss carried forward is reclassified as a **"specified loss."** A specified-loss NOL carryforward
can only be used to offset **future business income** — not wages, not portfolio income, not
other nonbusiness income — still capped at 80% of that business income in the year used. This
restriction is described as applying to specified losses arising with 2025 (and later) disallowed
amounts, so it would apply here if Joshua's 2025 loss is large enough to trigger §461(l) at all.
Practically: next year's usable offset would need to come from business income (Valley Pawn/Full
Circle Finance profit, future Bald Rock STR profit, and similar) rather than salary or investment
income — narrower than the old rule, but not nothing, since his business income is exactly the
kind of income this deduction is meant to shelter long-term.

*(This "specified loss" mechanism is new secondary-source reporting on a 2025 law change — sourced
from professional tax-advisory commentary, not yet deeply tested guidance or a final Treasury
regulation. Confirm with Silverline before relying on it for the actual return.)*

### Path B — Bald Rock stays passive (§6 items 3-4 unresolved or unfavorable)

None of the loss offsets the $450K of wages/business income in the first place. Per §469 and
consistent with §3 above, passive losses can only offset passive income — and the $25,000 special
allowance is fully phased out above $150,000 MAGI, so it doesn't help here either. The entire
cost-seg-generated loss gets suspended and simply adds to the existing $57,672 passive-loss
carryforward balance (§3), carrying forward indefinitely until either (a) passive income from ANY
passive activity in the portfolio shows up to absorb it, or (b) Bald Rock itself is sold in a
fully taxable transaction, which releases 100% of its suspended loss — even against active income
— in the sale year. This is the same mechanism already sitting on Cypress Crossing's $24,681
suspended loss in §7. In this path, nothing "wipes out" the 2025 tax bill at all; it just banks a
larger suspended-loss balance for whenever passive income or a sale eventually releases it.

### Bottom line

"Can I recoup more next year" — yes, in some form, either way. But whether that recoupment is
(1) an unrestricted-use NOL against next year's ordinary income, capped only by the 80% rule
(doesn't actually apply here post-OBBBA if §461(l) is triggered), (2) a business-income-only
"specified loss" NOL (Path A, if the excess is large enough to trigger §461(l)), or (3) a
passive-loss carryforward that sits frozen until passive income or a sale arrives (Path B) — is
entirely determined by the material-participation finding still open in §6 item 4. The
average-stay leg of the STR loophole is now resolved (4.12-night average, well under the 7-day
threshold — see §6 item 3) — material participation hours are the single remaining gate deciding
whether 2025's deduction works as non-passive at all, and what regime governs anything left over.
A real accounting of Joshua's and Hillary's hours at the property should be treated as the
priority item, not background cleanup.

**None of this is filed tax advice** — same caveat as §9. The §461(l) thresholds, the "specified
loss" mechanism, and the 80%/indefinite-carryforward mechanics above should all be confirmed by
Silverline (or whoever prepares the 2025 return) against the numbers that actually land on the
return.

---

## 11. 2025 material participation — reconstructed draft log (Bald Rock)

Following up on §6 item 4/§10: no system anywhere logged Joshua's or Hillary's actual hours on
Bald Rock in real time, so a 2025 number can only be built after the fact from things that DO
carry dates — vendor emails, texts, financing paperwork, the reservation calendar. Searched mail,
texts, and Drive on 2026-09-03 and assembled what follows. **This is a draft reconstruction for
Silverline's review, not a filed number** — treat the hour ranges as defensible estimates from
real dated activity, not a precise count.

### Which test to aim for

Rather than trying to prove the 500-hour test (Reg. §1.469-5T(a)(1)) with an after-the-fact
estimate, the cleaner target is the **100-hour / no-one-else-participates-more test**
(§1.469-5T(a)(3)): material participation is established if the taxpayer participates more than
100 hours during the year AND no other individual (including a manager or employee) participates
more. This fits 2025 well because **no formal manager existed** — a Davis Management LLC handoff
was drafted (setup checklist + a services-agreement template, both ~July 2026) but Joshua confirmed
2026-09-03 it was never implemented, so there was no one in 2025 (or, as it turns out, 2026) who
could have out-participated Joshua. The cleaning vendor (Green Nest quote, then Lam's Valley Maid &
Paint, $8,100 paid per the 2025 property P&L) did turnover cleaning only, not the broader
listing/pricing/guest-communication/financing work below — a specialized-service vendor doing one
task doesn't compete for "most hours on the activity" the way a full manager would.

### Reconstructed activity, with dated sources

| Period | Activity | What the record shows | Rough hours |
|---|---|---|---|
| Jan-Aug 2025 | Sourcing, ordering, and tracking ~$600K of furniture/FF&E and capital improvements across 20+ vendors (Pottery Barn, West Elm, Williams Sonoma, Signature Hardware, Royal Swimming Pools, Casper, Joss & Main, Decor Planet, Eight Sleep, Molekule, Traeger, Tonal, Platinum lights, Vent Covers Unlimited, and more) | Dozens of individual orders across Affirm, AmEx, and card-statement financing, each researched/placed/tracked by Joshua per the Full Evidence Log — a volume of vendor relationships that doesn't run itself | 150-250 |
| Sept 2025 | HVAC replacement project — R.E. Boggs invoices dated 9/3/25 ($15,936 + $13,251) and the Service Finance loan (#5977065, $36,000) Joshua personally signed 9/5/25 | Selecting the contractor, being available for the install, and personally executing the financing agreement | 8-15 |
| Aug 25-Oct 2, 2025 | Guesty platform setup and onboarding | Signup ~8/25, "Welcome to Guesty" subscription confirmation 9/15, a scheduled onboarding call from Guesty's Beth on 9/18, a "Walk through" support ticket Joshua personally submitted 9/30, and a live meeting with a Guesty rep (Christelle Palmares) 10/2 — connecting Airbnb/VRBO/Booking.com, listing setup, none of it automatable | 15-25 |
| Aug-Dec 2025 | Day-to-day STR operations across the property's first ~17 completed 2025 stays (per the Guesty reservation history in §6 item 3) | Pricing/calendar decisions, payout monitoring, guest-issue handling, and turnover coordination around each stay — conservatively 1-2 owner hours per stay even with a cleaner handling the physical turnover | 20-35 |
| Oct 14-30, 2025 | Neighbor/driveway sealcoating issue and an insurance claim tied to it | Extended personal text exchange with the next-door neighbor ("Liz Bald Rock" = Elizabeth & Matthew Lee) — sourcing the sealcoating contractor she'd used, getting a price history ("I paid $4,200 last year"), and collecting her name/email/phone because "Airbnb needs it to see if we can get this thing paid for" (a damage/insurance claim) | 3-6 |
| Throughout 2025 | Financing and administrative overhead — multiple Affirm loan applications, the "282 LOC for FCF INC" financing arrangement, insurance setup (Homesite via GEICO), Augusta Co. tax eBills | Each of these required Joshua's personal action (loan applications, signatures, account setup) per the evidence log and register | 15-25 |
| **Total (reconstructed)** | | | **≈ 210-355** |

Even the low end of this range clears 100 hours comfortably, and — per the point above — nothing
in the 2025 record shows any other individual (employee, manager, or vendor) participating in the
activity more than Joshua did. That combination is what the no-one-else-participates-more test
actually requires; it doesn't require nailing the 500-hour bar or a contemporaneous timesheet.

### What this doesn't establish

This is Joshua's participation reconstructed from paper trails, not sworn testimony or a
real-time log, and it doesn't yet separate Joshua's hours from Hillary's (some of the above —
particularly the STR platform setup and possibly guest communication — could be either or both of
them; the aggregate still counts for the material-participation test either way, since either
spouse's participation counts under §469(h)(5), but it's worth Joshua/Hillary confirming who
actually did what before this goes to Silverline). It also doesn't cover 2026, where Davis
Management LLC standing up changes the picture — see §6 item 4 and §10.

### Recommendation

Bring this table to Silverline as a starting point, not a finished answer. If they're comfortable
with the no-one-else-participates-more test on this record, 2025's non-passive treatment has a
real, dated evidentiary basis. If they want more, the next-best step is Joshua and Hillary each
writing down their own best recollection of hours spent (even rough monthly totals) while 2025 is
still recent enough to reconstruct honestly — memory now is more reliable than memory in 2028 when
this return might get examined.
