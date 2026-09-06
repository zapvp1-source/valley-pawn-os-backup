# Complete Review — Bald Rock Cost Seg Process + Unified Search Capture (2026-09-04)

Joshua asked for a complete review of the process and of unified search, to make sure everything
is being done correctly and everything capturable is being captured. This is that review. Findings
are ordered by how much they can move the actual tax number or break the filing, not by how easy
they are. Each has a status and a fix.

**Headline:** the documentation work is in good shape — the tracker reconciles to the dollar
($565,594.05 + $8,520.65 + $18,623.53 + $28,945.60 = $621,683.83), the appraisal is confirmed for
Tue 9/15 11am, and both cost-seg quote requests are out. But there are two tax-method issues that
can change the number by a lot (items 1 and 2), one appraisal-scope gap that is one email to fix
(item 3), a real deadline squeeze (item 4), and several evidence-capture gaps where the tooling
has holes that have been silently costing us receipts (items 6-10).

---

## A. Tax-method issues — these change the number

### 1. The furniture bucket is being carried at COST, but the law caps converted personal-use property at FMV on 8/1/2025

The memo's Furniture (5-yr) line — $279,650.98 to $284,129.30, almost all of it Pottery Barn /
West Elm / Casper / Signature Hardware bought 2021-2024 — was bought while Bald Rock was Joshua
and Hillary's own home. 26 CFR 1.168(i)-4(b) applies the lesser-of-adjusted-basis-or-FMV rule to
EVERY item converted from personal to business use on 8/1/2025, not just the house. Robbie's
appraisal values the real property only; it does nothing for the furniture. Three-to-four-year-old
furniture's FMV is a fraction of its retail cost (used-furniture markets run roughly 20-50% of
retail; a contents appraiser would put a number on it). That means the year-1 bonus deduction on
the furniture is very likely well under the ~$280K the memo currently implies, and memo §4/§10's
$387,559-$426,014 short-life deduction range is overstated by however much the furniture writes
down.

Two things soften this, neither eliminates it: (a) bonus depreciation itself IS still available on
converted property (Reg. 1.168(k)-2(b)(3)(ii) — a taxpayer who buys new property for personal use
and later converts it is still the "original user"), so the question is basis, not eligibility;
(b) anything bought AFTER 8/1/2025 for the rental (see item 2) is at full cost with no cap.

**Fix:** (1) tag every tracker line with its purchase date relative to 8/1/2025 (see item 2);
(2) for the pre-8/1/2025 furniture/FF&E, get an FMV-as-of-8/1/2025 figure — either a personal
property/contents appraisal (some appraisers do this as an add-on; ask Robbie on the 15th whether
Blue Ridge does contents, or find a personal-property appraiser), or at minimum a documented,
defensible depreciation schedule Silverline is comfortable with; (3) rewrite memo §4's furniture
line as "cost $X / FMV-capped estimate $Y" and carry the memo's deduction range on Y. **Do not
hand a cost-seg vendor $280K of furniture at cost without this** — a fully engineered study will
allocate whatever basis it is given, and the vendor will not catch that the input was wrong.

**Related audit exposure inside the same bucket — confirm these are actually at Bald Rock and
available to guests:** Tonal home gym ($3,924.97), two Platinum red-light therapy panels
($2,166.03), Eight Sleep smart mattress ($2,574.59), Renu Therapy cold plunge ($10,214.09),
Molekule air purifiers ($841.34), Traeger grill ($3,485.78). Roughly $23K of wellness/personal-
flavored equipment. If any of it moved to Florida with the family, it isn't a Bald Rock asset at
all. If it's there and listed as a guest amenity, it's fine — but the listing should say so.

### 2. Pre-conversion vs post-conversion is not split anywhere, and the split matters in both directions

Everything in the $621,683.83 is being treated as one pool that flows into the lesser-of test.
Wrong in both directions:

- Anything placed in service AFTER 8/1/2025 — R.E. Boggs HVAC $29,187.00 (invoiced 9/3/2025),
  Beatbot $1,262.55 (8/8/2025), the later Tyson Boffo pool payments (2024-2026 Venmo stream), any
  2025-26 Casper/Affirm purchases, the Sept-Dec 2025 "Electric 282"/"282 Plumber" work if capital
  — is a SEPARATE asset at actual cost, 100% bonus, no FMV cap at all. Lumping it into the
  conversion pool understates it if the appraisal comes in low.
- Anything BEFORE 8/1/2025 is capped by FMV (real property via Robbie; furniture via item 1).

The quote-request draft sent to Overline/CostSegEZ says "improvements through 8/1/2025" but the
$621,683.83 includes the Sept 2025 HVAC — internally inconsistent. The improvement list sent to
Robbie also lists the HVAC as "Sept 2025," which post-dates his effective date (fixed in item 3).

**Fix:** add a "Placed in service: pre-8/1/2025 / post-8/1/2025" column to the Full Tracker sheet
and produce two totals. Memo §4 then carries: pre-conversion adjusted basis (subject to lesser-of)
+ post-conversion additions (at cost). I can do the tagging from the dates already in the tracker
and evidence log — it's mechanical — but the handful of ambiguous ones (Boffo's multi-year
stream, anything dated exactly around the move) need Joshua's confirmation.

### 3. The appraisal engagement is missing two things the cost-seg firm needs — one email fixes it

The 8/4 order to Blue Ridge correctly asked for a "retrospective fair market value appraisal ...
as of approximately August 2025." Good. But: (a) "approximately August" should be pinned to
exactly 8/1/2025 now that Joshua has confirmed the date; (b) **no land-vs-improvements allocation
as of that date was requested** — the intake package and evidence log both say the cost-seg firm
will bounce the file without it, and the county's $55,000/6.5% land figure is implausibly low for
1.092 acres and is exactly what a cost-seg engineer will refuse to use; (c) the improvement list
I sent Robbie on 9/3 includes the Sept 2025 HVAC, which is after his effective date.

**Fix:** a 3-line email to Robbie. **Drafted and sitting in Gmail Drafts as a reply on the same
thread — not sent.** Joshua sends it or tells me to. This is substantive (it changes what the
report contains), not another scheduling ping.

### 4. The calendar does not close on its own — the 10/15 extension deadline is at risk

Appraisal inspection 9/15 → Blue Ridge's stated 2-week turn → report ~9/29. Fully engineered cost
seg → 3-4 weeks from engagement (R.E. Cost Seg/CostSegEZ) → if engaged only after the appraisal
lands, the study arrives ~10/20-10/27. The 1040 is on extension to **10/15/2026** and Silverline
needs the report by roughly end of September to build the return. That does not work as
sequenced.

**Fix (pick one, or both):** (a) engage the cost-seg vendor NOW on the placeholder basis so the
engineering (site data, asset identification, allocation percentages) runs in parallel with the
appraisal — the allocation percentages apply to whatever final basis is plugged in, and every
vendor contacted can update the basis input late; ask Overline specifically about turnaround,
since their model is the faster one; (b) ask Silverline now whether, if the study slips past
10/15, they'd file the 2025 return with straight-line depreciation and pick up the cost seg via a
Form 3115 change in accounting method on the 2026 return (standard fallback, no amended return) —
so a slip costs timing, not the deduction. Either way the decision belongs in front of Silverline
this week, not in October.

### 5. Whose name goes on the study — 2025 vs 2026 are different answers

Farming Infinity Mountains LLC (SMLLC, disregarded, EIN 42-4031872) was formed 7/13/2026. For
tax year 2025 the property was owned by Joshua individually (recorded 2016 deed in his name); the
LLC did not exist. The cost-seg report and the appraisal should be in **Joshua Davis's** name for
the 2025 return. Whether a 2026 deed into the LLC has actually been recorded is still unconfirmed
in every file (REAL_ESTATE_OS says "owner entity: Farming Infinity Mountains LLC" but the deed
transfer itself isn't documented). Not a 2025 problem; it is a 2026 problem, and the quote draft's
"CONFIRM current title/entity" line is the right flag. Answer: 2025 = Joshua Davis.

### 6. Still the biggest structural unknown: where Bald Rock's 2016-2024 Airbnb income was reported

Unchanged from memo §6 item 1 / register row of 9/3. The 2024 personal return shows no Bald Rock
Schedule E ever, yet the Guesty note says the Airbnb history runs back to 2016. If the property
was a rented vacation home (§280A mixed use) for years before 8/1/2025, then "placed in service
8/1/2025 at full cost basis" is not the right frame — "allowed or allowable" depreciation from
those years reduces basis whether or not it was ever claimed, and the furniture in item 1 may have
been in rental service before 2025. Nothing in this review changes the answer; it raises the
stakes on getting it. This has to be answered before anything is filed, and it is a Joshua +
Silverline question, not a search question.

---

## B. Evidence capture — where the tooling has been leaking

### 7. 54,616 emails (16%) are partial downloads — their attachments are not on the Mac and not in the index

Apple Mail is holding 54,672 of 344,375 messages as `.partial.emlx` stubs: body preview only,
attachments never downloaded. Unified search indexes what's on disk, so those attachments —
invoices, statements, order PDFs — are invisible. Known casualties already documented: **every LL
Flooring dollar figure for the hardwood floors** (`0702794747_Quotation.PDF`,
`0134505377_Invoice.PDF`, `0134879323_Invoice.PDF` — a major structural item with NO number in
the tracker), the Crutchfield "Shipping Confirmation" partials, several vendor threads in the
evidence log flagged "attachment never downloaded."

**Fix (one-time, ~10 minutes of Joshua's time, then overnight):** Mail → Settings → Accounts →
each of the 4 accounts → Account Information → "Download Attachments: **All**". Mail then pulls
every attachment down over the next several hours. Then rebuild `mail` + `files`
(`refresh_hardened.sh` does it nightly; a manual run finishes sooner). I cannot flip that setting
from here — it's a Mail preference on the Mac. Until it's done, any "no invoice found" conclusion
in the evidence log for a vendor whose emails are partials is not a real finding.

### 8. 995 image-only PDF attachments + 203 Bald Rock/Real Estate image files have never been OCR'd

The index flags 30,696 files as `needs_ocr` overall — most are personal photos and can stay that
way — but two slices matter here: **995 PDFs sitting in mail attachments** (image-only PDFs are
almost always scanned invoices, statements, and signed contracts), and **203 files under
`02 Real Estate/282 Bald Rock Rd`** — including the `Valley Building Supply - PlyGEM - Emails &
Media/IMG_13xx-14xx` photos, which are the "10 dated photos of the final invoice batch" the
evidence log cites for the $28,947.87 VBS reclassification. Those invoice photos are cited but
their dollar figures aren't searchable. `ocr_run.py` exists, backs up originals, and is safe.

**Fix:** run `ocr_run.py` scoped to (a) the Real Estate folder and (b) mail-attachment PDFs.
~1,200 files, a few hours unattended. Then re-run the vendor searches that came back empty.

### 9. The nightly photos (screenshots) index has been failing since at least 9/3 — and the log says "success"

`refresh_hardened.log` shows `photosindex.py` dying every night on an osxphotos enumeration
timeout (180s) while the wrapper still prints "hardened success on attempt 1." The `photos`
corpus is frozen at 9/3 04:32. Screenshots are where phone-captured receipts, Affirm/Venmo
confirmations, and text-message photos of invoices tend to live. The separate `doc_photos` pass
(2,741 receipt/document-looking photos) IS working. Also: the launchd agent named in the skill
doc (`com.valleypawn.unified-search-refresh`) has been **disabled since 8/21 (broken TCC)** and
replaced by `refresh_hardened.sh` under a different runner — the skill doc still describes the
old one.

**Fix:** raise the osxphotos timeout (or paginate the enumeration) in `photosindex.py`; make the
wrapper fail loudly when any stage tracebacks; update the `unified-search` skill doc (it says 3
corpora — there are 8: mail, files, msgs, notes, reminders, gdrive, photos, doc_photos — and it
names the wrong scheduler).

### 10. Hillary's email is not indexed at all

The Pottery Barn/West Elm/Williams Sonoma card ($211K) bills to Hillary. The Burns Builders roof
loan is in Hillary's name. Anything a vendor emailed to her — statements, order confirmations,
warranty and financing paperwork — is invisible to this whole process. The single largest
remaining pocket of unrecovered receipts is almost certainly her inbox.

**Fix:** add Hillary's account(s) to Mail on this Mac (read-only is fine) and let the indexer pick
them up, or have her export/forward the relevant vendor folders. Her call and Joshua's; flagging
it because no amount of searching Joshua's mail finds what was sent to hers.

### 11. Bank/card statements — still the open "six-card pull," plus a coverage cliff at June 2024

Unchanged: MC 0305, MC 6246, MC 1689, LCC 1037, AmEx 7115/1005 statements would close Bucket 2
($8,520.65) and firm up several Bucket 1 "P" items. New from this review: the DuPont business
statement archive on file **ends June 2024**; Shreckhise's recurring $500 bill-pay and the Boffo
Venmo stream run past that. Wells Fargo 2797 and DuPont statements from July 2024 forward have
not been pulled. Joshua-only action (or Silverline's bookkeeper).

---

## C. Hygiene — small, but they will confuse the next person

12. Register row dated 9/3 ("Real estate tax-strategy memo built") still quotes the ORIGINAL basis
    range ($906K-$987K adjusted, $317K-$380K short-life). Memo §4 is now $970,594.05-$1,026,683.83
    and $387,559-$426,014. Stale; fixed in this pass.
13. The 7/31 intake package (Google Doc) Section 2 still says basis ≈ $405,000 and Section 8 says
    $502K-$710K. Both superseded; the 9/4 quote-request doc is the current vendor-facing source.
    Left as-is (its own Section 8 already says it's superseded) — don't send it to anyone.
14. Robbie has now CONFIRMED Tue 9/15 11am ("9/15 at 11 am works," 9/4 4:49am). Register said
    "awaiting." Fixed.
15. Bucket discipline: a few Bucket 1 lines are "P" on the payment side (ProjectorScreen, Lowe's
    appliances, Valley Concrete, VBS partial). Documented in the tracker's own notes; fine, but
    Silverline should see the tracker, not just the memo total.
16. Crutchfield theater (Evidence Log §40): Joshua confirmed the install; reconciling the actual
    paid amount from the 2020 order/installment-plan emails is a real add-back opportunity that
    got easier once item 7 (attachment download) is done — the Crutchfield invoice PDFs are
    among the partials.

---

## D. What I did during this review (no approvals needed)

- Verified the tracker reconciles to $621,683.83 exactly, bucket by bucket.
- Verified the nightly index refresh actually ran today (mail 03:46, msgs 04:10, gdrive 04:28,
  doc_photos 05:16, files 14:59 EDT) and found the photos-stage failure and the misleading
  "success" line.
- Pulled the Blue Ridge order chain back to the 8/4 web form and confirmed the retrospective
  effective date IS in the engagement and the land allocation is NOT.
- Drafted the Robbie effective-date/land-split/HVAC email (Gmail Drafts, same thread, not sent).
- Updated the register: appraisal CONFIRMED 9/15 11am; stale basis numbers corrected; this
  review logged.

## E. What needs Joshua (in priority order)

1. Send the Robbie draft (or say go and I send it). Before the 15th.
2. Put the timeline question (item 4) in front of Silverline this week: engage the cost-seg vendor
   now on placeholder basis, and confirm the Form 3115 fallback if it slips past 10/15.
3. Mail → Settings → Accounts → Download Attachments: All (item 7). Ten minutes, then let it run.
4. Answer the personal-vs-guest question on the ~$23K of wellness equipment (item 1).
5. Decide on Hillary's inbox (item 10) and the post-June-2024 statements (item 11).
6. The 2016-2024 Airbnb income question (item 6) — this one is Silverline's, but it can't wait
   for October.

Everything under B.8, B.9, and the pre/post-conversion tagging in A.2 I can do without input and
will start on next, in that order.
