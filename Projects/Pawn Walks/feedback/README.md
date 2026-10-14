# Pawn-walk feedback loop (built 2026-10-13)

**Purpose.** Preston (or any manager) annotates the overpay flags in #pawn-walks. The next
morning's walk already knows what he said: values he stated become comps, items he cleared stay
cleared, reloans are tagged, and the flag list gets more accurate over time. Nothing is manual.

## How feedback is given (what the stores do)
Paste the flag block from the walk back into #pawn-walks (top-level or as a thread reply) and add
a note after each line with ` - `:

    • L · $375 · 25% · GLOCK MODEL 41 GEN 4, SERIAL NUMBER BYAT4… - *Used value around 500, okay pay amount.*

What the note says drives what happens:
| In the note | Read as | Effect next morning |
|---|---|---|
| "overpay", "too much", "$10 over" | real overpay | counted as a hit; nothing changes for the item |
| "all good", "okay", "fine", "not an overpay" | false flag | that exact item (store + description + amount) is never flagged again for 180 days (120 if it has no serial) |
| a dollar value ("used value ~$500", "Bravo used sale $130") | manager comp | that model is valued at the stated amount for 180 days (`manager_comps.json`) — the lower-of rule is bypassed |
| "half back", "purchased from us" | our own sale | cleared, logged as HALF_BACK |
| "quantity 2" / "qty 2" | lot | cleared, logged as QUANTITY |
| "reloan", "optic", "battery", "charger" | reason tags | feed the calibration table |

A plain sentence that quotes no flag line is kept as a note (verdict UNCLEAR) and shows in the
spreadsheet's Feedback tab; it changes nothing by itself.

## What runs, and where
* `run_daily_intake.py` (native agent `daily-report-pawn`, 07:15) calls
  `feedback_ingest.run()` first — reads #pawn-walks (bot token from Keychain via
  `Valley Pawn OS/bin/vp_slack.py`), parses new human messages + thread replies, appends to
  `feedback_ledger.jsonl` (idempotent on message ts + line), rebuilds `manager_comps.json`,
  `item_overrides.json`, `calibration.json`. 25 s budget, fail-soft.
* Then `feedback_rules.apply()` adjusts each valued item (all additive, every change written to
  `r['fb_notes']` and the xlsx **Feedback** tab):
  1. **Manager comp** — model key match (text before the first comma, serial + "MODEL" dropped).
  2. **Quantity in the description** ("QUANTITY 3", "x2", "(4 pcs)") × per-unit value.
  3. **Accessory allowance** for tools when the description says a battery/charger/case came with it
     (`feedback_rules.json`: battery $10, charger $5, case $5). "CORDLESS - BATTERY OPERATED" is a
     power type, not an included battery, and is ignored.
  4. **Reloan tag** — serial number seen on an earlier intake-detail pull → kind shows **RL** in the
     flag list, with Preston's standing instruction as a footer. Reloans still flag (a depreciated
     reloan is an overpay).
  5. **Cleared items** — exact item Preston cleared → not flagged while the override is fresh.
  6. **Firearm with a named optic** → moves from FLAGS to a VERIFY line ("write up the optic separately").
  7. **Category self-tuning** — a category whose flags were called wrong ≥3 times at ≥60% in the
     last 90 days is flagged only below 15% until its record improves (`calibration.json → category_tuning`).
* Walk footer: one line the morning after feedback lands ("Preston's feedback on the 10/12 walk is
  in: 10 notes → 3 model values updated, 5 items cleared"); on Tuesdays the running flag accuracy.

## Files
| File | What | Hand-editable? |
|---|---|---|
| `feedback_rules.json` | allowances, expiry days, optic keywords, tuning thresholds, reviewer names | yes |
| `manager_comps.json` | model → stated value | yes (add a model + value + date) |
| `item_overrides.json` | cleared items | yes |
| `feedback_ledger.jsonl` | every annotated line, classified | append-only, don't edit |
| `calibration.json` | accuracy by category / reason / valuation source + active tuning | generated (`--rebuild`) |
| `serial_index.json` | serial → intake dates (incremental cache over intake-detail CSVs) | generated |
| `ingest_state.json` | last Slack ts seen, last run result (the footer reads this) | generated |

## Manual use
    cd "Pawn Walks/feedback"
    python3 feedback_ingest.py --dry-run          # show what would be ingested, write nothing
    python3 feedback_ingest.py                     # ingest now
    python3 feedback_ingest.py --rebuild           # recompute comps/overrides/calibration from the ledger
    python3 feedback_ingest.py --from-text msg.txt --ts 1791913869.934319   # offline parse test

## Limits worth knowing
* The Bravo intake-detail export carries no quantity, accessories, optic or reloan column. Rules 2–6
  work off description text and serial history; anything Bravo doesn't export only becomes knowable
  through feedback — which is exactly what the ledger captures.
* Half-back loans on our own sales cannot be detected from exports (sold descriptions are truncated
  and don't always match); they are cleared by feedback only.
* `run_daily_intake.py.bak-pre-feedback-20261013` is the pre-hook copy (Rule 4 backup).
