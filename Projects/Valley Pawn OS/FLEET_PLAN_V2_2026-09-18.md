# FLEET PLAN V2 — measured, gated, and testable in isolation
**2026-09-18. Supersedes the planning sections of `FLEET_DEEP_DIVE_2026-09-16.md` and `FLEET_FREEZE_2026-09-16.md`.**
Those two were written from impressions. This one is written from counts. Keep the freeze rules; replace the plan.

> **Joshua, 2026-09-18 (verbatim intent):** "we should be able to test everything and see if its working in
> isolation without publishing a bunch of bullshit to slack. We should take each task, evaluate the performance
> of it since inception, decide if its good to go or not based off accuracy and consistency. Then after we do
> that we should look at the fleet design and insure its scheduled or allocated with proper resources and or
> timing and or new hardware to have everything just running along without instance or interruption."

---

## 0. Why the old plan kept failing

Every prior plan — including mine on 9/16 — set out to *fix* things before anything *measured* them. "Is it
working" was answered by opening a channel and forming an impression. That is exactly how, this week, three
running checks (clock-in, Cloud Cover, dress code) were reported to Joshua as broken, and a Wednesday with one
store open was reported as a pipeline defect.

V2 inverts the order: **measure → gate → fix → re-measure.** Nothing is declared good because it looks good.

---

## 1. THE MEASUREMENT (built, running, repeatable)

`bin/vp_audit.py [--days N]` — read-only, publishes nothing. For every Tier-1 entry it expands the cadence into
every instance that should have fired since **that publication's own inception**, pulls the real channel
history, and counts how many instances actually delivered a message carrying the entry's marker.

**It already caught its own false negative.** `review-obtained-last-week` first read **0/8, "never"** — because
the manifest marker was lowercase `ranked` and the real post says `Ranked`. The tool now refuses to report a
delivery rate when a marker never matched anything; it returns **MARKER SUSPECT** instead. With the marker
fixed the same task reads **57.1%**. Any 0% must be treated as a marker bug until proven otherwise.

### 1.1 The actual record (60 days, to 2026-09-18)

| Task | Cadence | Since | Expected | Delivered | Rate | Longest dark | Accuracy notes |
|---|---|---|---:|---:|---:|---:|---:|
| monthly-scrap-rankings | monthly d1 | 08/12 | 1 | 0 | 0% | 1 | 0 |
| vp-new-customer-report | monthly d3 | 08/03 | 1 | 0 | 0% | 1 | 0 |
| weekly-timekeeping-analysis | weekly Mon | 08/03 | 6 | 2 | 33% | 2 | 1 |
| daily-cloudcover-check | Mon–Sat | 07/21 | 52 | 19 | **37%** | **13** | 0 |
| pawn-walk | daily | 07/21 | 59 | 22 | **37%** | **22** | 0 |
| discount-review | daily | 08/14 | 36 | 19 | 53% | 5 | 1 |
| review-obtained-last-week | weekly Mon | 07/27 | 7 | 4 | 57% | 2 | 2 |
| daily-items-to-price | daily | 07/21 | 59 | 34 | 58% | 5 | 0 |
| weekly-markdown-verification-review | weekly Mon | 08/13 | 5 | 3 | 60% | 1 | 0 |
| daily-dress-code-check | weekdays | 07/21 | 43 | 26 | 61% | 8 | 0 |
| sold-review | daily | 08/13 | 36 | 22 | 61% | 5 | 1 |
| chekkit-unanswered-eod-followup | Mon–Sat | 08/10 | 34 | 21 | 62% | 4 | 0 |
| layaway-yield-weekly | weekly Mon | 07/20 | 8 | 5 | 63% | 2 | 0 |
| daily-funds-verification | daily | 07/23 | 56 | 38 | 68% | 4 | 0 |
| daily-clockin-check | weekdays | 07/21 | 43 | 31 | 72% | 5 | 1 |
| monday-bravo-combined-compile | weekly Mon | 07/26 | 8 | 6 | 75% | 1 | 1 |
| monday-bravo-postcheck | weekly Mon | 07/26 | 8 | 6 | 75% | 1 | 0 |
| nics-weekly-mtd-ranking | weekly Mon | 08/17 | 4 | 3 | 75% | 1 | 0 |
| weekly-store-kpis | weekly Mon | 07/26 | 8 | 6 | 75% | 1 | 0 |
| daily-unopened-email-eval | daily | 08/24 | 25 | 19 | 76% | 6 | 0 |
| weekly-returns-summary | weekly Mon | 08/10 | 5 | 4 | 80% | 1 | 0 |
| chekkit-unanswered-alert | Mon–Sat | 08/04 | 39 | 32 | **82%** | 4 | 0 |
| monthly-analytics-report / employee-sales / eom-recap / nics-monthly | monthly | 09/01–09/05 | 0–1 | — | insufficient | — | 0 |

**The three findings that matter:**

1. **Nothing is above 82%. The median is ~62%.** That is the concrete answer to "why have we never had a clean
   week." A clean week needs ~35 consecutive daily deliveries; at 62% per-instance the odds are effectively zero.
   The fleet was never one bug away from clean — it was *systemically* at two-thirds.
2. **Two different failure shapes, and they need different fixes.** *Long dark runs* (pawn-walk 22 days,
   cloudcover 13, dress-code 8) are infrastructure outages — the osascript disappearance, registry wipes, VM
   wedges. *Scattered single misses* (chekkit 4, funds 4, store-kpis 1) are per-run flakiness. Fixing the
   infrastructure lifts the floor; it does not fix the flakiness, and vice versa.
3. **21 of 47 Tier-1 entries (45%) are NOT MEASURABLE** — they publish to Joshua's DM, a canvas, or a file the
   bot can't read. We cannot score nearly half the fleet. That is not a reporting gap; it is a **design defect**:
   a publication that cannot be verified cannot be trusted, and its silence is indistinguishable from success.

---

## 2. ISOLATION TESTING (built today)

**Rule: no task is ever tested by letting it publish.** `bin/daily_report.sh <kind> <date> --render` compiles the
real report from real data and prints the exact bytes that *would* be posted, writes them to
`fleet/test_output/<task>-<date>.txt`, and **publishes nothing** — no channel, no DM, no file upload. Verified
2026-09-18 14:29 on the 9/17 pawn walk (2,474 bytes, 5 stores, 9 flags, zero side effects).

**To extend to the rest (next build):** every publication gets the same three verbs, which `comms_engine.py`
already proved out — `render` (produce, publish nothing), `check` (has today's already posted?), `post`
(publish). A task that cannot render without publishing is not finished.

---

## 3. THE GATE — how a task earns "good to go"

No task returns to normal service on a feeling. Each is scored on a rolling **14-day measured window**:

| | Criterion | Threshold |
|---|---|---|
| **Consistency** | delivery rate from `vp_audit.py` | **≥ 95%** |
| **Consistency** | longest dark run | **≤ 1** |
| **Accuracy** | new `_corrected` incidents in the window | **0** |
| **Verifiability** | output is a channel or file the bot can read | **required** |
| **Testability** | `--render` produces the output with zero side effects | **required** |

Three verdicts, and every task gets exactly one:
- **GO** — meets all five. Runs unattended; scorecard watches it.
- **REMEDIATE** — fails one or more, with a *named* defect and an owner. Stays running; does not count toward clean.
- **RETIRE** — cannot meet Verifiability/Testability, or nobody reads its output. Disable it rather than carry it.

**Today's verdicts: 0 GO, 22 REMEDIATE, 21 blocked on Verifiability.** That is the honest starting line.

---

## 4. FLEET DESIGN — resources, timing, hardware

### 4.1 The binding constraint is serial, and it is not CPU
Every Bravo report funnels through **one Windows VM, one Bravo instance, one watcher, one screen**. Bravo is
driven by UI automation, so two reports cannot run at once — they queue. Measured cost: a single store-report
cell runs **80–275 seconds**; the full morning pull (15 cells) took **29 minutes** on 9/18 and **48** on 9/17.
More hardware does not relieve this. **The only levers are fewer Bravo touches, better batching, and
scheduling that respects the serial queue.** The 9/17 combined morning pull (one trigger, 15 cells, all
downstream reports compiling from disk) is the correct pattern and should be the *only* pattern.

### 4.2 The morning window is the whole game
06:50 pull (~30 min) → 07:15 pawn walk → 07:45 sold → 08:00 items-to-price → 08:25 discount. Four publications
depend on one 30-minute serial job finishing on time. On 9/18 it worked and all four landed. **Design rule: no
new Bravo-touching task may be scheduled between 06:30 and 09:00.** That window is spoken for.

### 4.3 Hardware — what is and isn't a real constraint
- **Mac Studio 2022 M1 Max**, 494 GB internal, **46 GB free**. Thunderbolt 4 (not 5); 3 of 4 rear ports used by
  the Studio Displays, **1 free**.
- **Thunderbolt SSD ordered, not yet arrived.** On arrival: move the Parallels VM + Bravo output archives off
  the internal disk. That is a *disk-pressure* fix, not a speed fix — it will not make Bravo faster, and nothing
  in the audit above is caused by disk speed.
- **Honest conclusion: hardware is not why the fleet is at 62%.** Software gaps are. Buy no more hardware for
  reliability reasons until the gate in §3 is being met.

### 4.4 Execution-layer rule, settled
Anything deterministic runs as a **native launchd agent** (no model, cannot die silently). A model is used only
where judgement is genuinely required: reading free-text Slack for the funds ledger, and vision-reading the
handwritten jewelry count sheets. 11 tasks were converted 9/17; the remaining Cowork tasks are converted or
retired, never left in place "for now."

---

## 5. SEQUENCE — in this order, no skipping

### STEP 1 PROGRESS — 2026-09-18, same day
- **Measurable went 26 → 34 of 48.** Unmeasurable 21 → 14.
- File-based artifacts are now measured on disk per instance (`vp_audit.py` expands `{YYYY-MM-DD}` in the path and checks each dated artifact). That alone scored fleet-guardian **82.8% / 82.1%**, monday-bravo-cell-gapfill **66.7%**, monthly-publication-audit **never on its day2/day4 schedule** (the only two artifacts on disk are 9/6 and 9/7 manual runs).
- Bot added to **#jewlery-counts** and **#monthly-gun-audit** — immediately revealed `jewelry-onhand-nightly-pull` **46.7%** (14/30) and `monthly-gun-audit-report` **0/2 since 08/03**. Both were invisible an hour ago.
- An undated artifact (`precious-metals .../state.json`, rewritten in place) is reported **MTIME ONLY** — its history is genuinely unrecoverable; it needs a dated receipt before it can ever be scored.

**REMAINING 14, and the fix for each:** 8 publish only to Joshua's DM and 5 only to a canvas — the vp_ops_engine bot cannot read either, and never will (a DM belongs to the bot/user pair that created it). **Do NOT solve this by moving them out of Joshua's DM** — the DM is where he wants them. Solve it with a **delivery receipt**: each of these writes `fleet/receipts/<task>/<YYYY-MM-DD>.txt` containing exactly what it sent, at the moment it sends. The audit then measures the receipt. Zero change to what Joshua sees, full measurability. The 4 bonus tasks are the priority — they move money and are currently the least visible things in the fleet.

**Step 1 (original) — Make the fleet measurable (unblocks 21 tasks).** Re-point every DM-only publication to a readable
channel or a marked file. Validate every marker in `expected_outputs.json` against a real post; fix the case
bugs. *Exit test:* `vp_audit.py` reports zero `NOT MEASURABLE` and zero `MARKER SUSPECT`.

**Step 2 — Give every publication `render`/`check`/`post`.** *Exit test:* each one renders its real output with
no side effects.

**Step 3 — Attack the two failure shapes separately.** Long dark runs: finish the native conversion (done for 11)
and keep the registry-guard/keepalive layer. Flakiness: for each task below 95%, read its own dark dates from the
audit JSON and fix the named defect — starting with the known one, the items-to-price "Show More" grid stall that
cost Waynesboro 6 of 247 rows on 9/18.

**Step 4 — Re-measure and gate.** Run `vp_audit.py --days 14`. Every task gets GO / REMEDIATE / RETIRE in writing.

**Step 5 — Only then, re-expand.** Tier 2 → 3 → 4, one tier per week, and **a task may not be re-enabled until it
passes the §3 gate**. This replaces "one tier per clean week," which let unmeasured tasks back in.

---

## 6. What changes about how this is reported

1. Never call a publication broken unless the scorecard's **TODAY** block says `MISSED TODAY` — i.e. its
   scheduled time *plus grace* has actually elapsed. (Dress code was declared dead four minutes before it posted.)
2. Never repeat a cause a failed run invented about itself. (A 1Password extension was blamed for software Valley
   Pawn does not use.)
3. A 0% rate is a **marker bug** until proven otherwise.
4. Check the store calendar before calling any zero wrong — **Wednesday is Culpeper only; Sunday is closed.**
5. Rates get quoted with their window and their denominator, or not at all.

---

## 7. Standing status — one command, no interpretation

| Question | Source of truth |
|---|---|
| Is it working right now? | `fleet/FIELD_SCORECARD.md` → **TODAY** block |
| Is it reliable over time? | `bin/vp_audit.py` → rate, longest dark, accuracy |
| Are we allowed to call it done? | §3 gate, in writing, per task |
| What broke and what needs a human? | `fleet/FAILURE_LEDGER.md` |
