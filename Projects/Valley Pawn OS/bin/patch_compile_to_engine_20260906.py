#!/usr/bin/env python3
"""
2026-09-06 — wire monday-bravo-combined-compile Steps 2, 3, 4.5 to the Comms Engine.
Additive to the SKILL: the model-rendered templates are replaced by "run the formatter, obey the
exit code" blocks, exactly the pattern the 2026-09-05 aged-inventory fix used for Step 1.
Backs up the SKILL first. Idempotent (re-running detects the marker and exits 0).
"""
import datetime as dt
import os
import re
import shutil
import sys

SKILL = os.path.expanduser("~/Documents/Claude/Scheduled/monday-bravo-combined-compile/SKILL.md")
MARK = "COMMS ENGINE (hardened 2026-09-06)"
ENGINE = "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/comms_engine.py"

COMMON_RULES = """
**DO NOT HAND-BUILD THIS POST — %s.** The Comms Engine renders it, checks it, and posts it
as the *VP OPS ENGINE* bot (no "Sent using Claude" footer, not under Joshua's name). Run:

```bash
/usr/bin/python3 '%s' post --pub %s \\
  --pipeline-date <PIPELINE_DATE> --post-date <POST_DATE>
```

Then obey the exit code — no judgment calls, no repair attempts, no re-typing:
- **exit 0** → the bot already posted it. Post NOTHING yourself. Record the stderr line for the DM.
- **exit 3** → the bot could not post (stderr says why). stdout carries the validated body —
  post that stdout to %s via `slack_send_message` **verbatim, byte for byte** (it will carry the
  connector footer; that is the only acceptable difference). Do not add, drop, or reflow anything.
- **exit 4** → already posted today (duplicate guard). Post nothing; note `⏭️ skipped — already posted` in the DM.
- **exit 2 or 1** → stdout is empty. **Post NOTHING to the channel this run** — not a partial
  table, not a caveat, not a note about which store is missing (Rules 16 + 18). Copy stderr into
  this run's record; the Step 6 DM carries one plain-language "held pending complete data" line.
- Any `NOTE —` line on stderr is for the Joshua DM only (plain language), never for the channel.

The engine already enforces COMPLETENESS GATE v2 for this report (all 5 stores present and
valid). You do not re-check it by hand and you must never override a withhold.
"""

STEP2 = """==========================================================================
STEP 2 — Post to #loan-review (C0B08RS2BMK) + #layaway-review (C04N24STDP1)
==========================================================================
""" + COMMON_RULES % (MARK, ENGINE, "loan-review", "C0B08RS2BMK") + """
Then the layaway post, same contract:

```bash
/usr/bin/python3 '""" + ENGINE + """' post --pub layaway-review \\
  --pipeline-date <PIPELINE_DATE> --post-date <POST_DATE>
```
(exit 3 fallback channel: C04N24STDP1.)

**Write the results JSON** for the downstream `weekly-loan-layaway-manager-dms` task (fires
Monday 9 AM and reads `/Users/joshuadavis/Documents/Claude/loan-layaway-results-latest.json`):

```bash
/usr/bin/python3 '""" + ENGINE + """' results-json \\
  --pipeline-date <PIPELINE_DATE> --post-date <POST_DATE>
```
exit 0 = written. exit 2 = not written (a store's loan or layaway data is missing) — say so in
the Step 6 DM in plain language so Joshua knows the manager DMs will not have fresh numbers.

Reference only — what the engine computes: loans from `output/<PIPELINE_DATE>_<STORE>_loans-75-days-past-due.csv`
(`store,date,count,dollar_sum`); denominators from the freshest complete 5-store
`output/<DATE>_<STORE>_end-of-month.xlsx` set no more than 8 days old (`Ending Loan Base` row,
last numeric) — never from a Slack post, never hard-coded; ✅ ≤ 5%, 🔴 > 5%; the as-of date is
stated in the post. Item counts are omitted automatically when they hit the 22-row grid display
cap (a NOTE line explains it). Layaways from `output/<PIPELINE_DATE>_<STORE>_layaways.csv`
(`store,date,overdue,past_pmt_due,contacted_no_activity,no_pmt_30d,locate`) — each count shown
as `N (P%)` share of company total, Locate as a plain count with a 🔴 action line per store.

"""

STEP3 = """==========================================================================
STEP 3 — Post to #employee-performance (C0ATTLPQHR8)
==========================================================================
""" + COMMON_RULES % (MARK, ENGINE, "employee-performance", "C0ATTLPQHR8") + """
Reference only — what the engine computes: reads `output/<FIRST_OF_MONTH>_<STORE>_employee-activity.csv`
for all 5 stores and refuses any file older than PIPELINE_DATE (stale-month guard); column
`Retail Sales Excluding Fees`; name = text after the first ` - `; skips `Total Store`, `SYSTEM`,
`Report printed on`, PRESTON PETERS, and $0.00; sums multi-store employees and shows
`STORE1+STORE2`; 🥇🥈🥉 then 4th, 5th…; period `<FIRST_OF_MONTH>–<PIPELINE_DATE>`.

"""

STEP45 = """==========================================================================
STEP 4.5 — Post FPD ranking to #first-payment-default (C0B17894S2Y)
==========================================================================
""" + COMMON_RULES % (MARK, ENGINE, "first-payment-default", "C0B17894S2Y") + """
Reference only — what the engine computes: reads `output/<PIPELINE_DATE>_<STORE>_fpd-cohort.csv`
for all 5 stores (header-only = zero FPD, valid); store ranking best→worst by count then $;
company total; top-3 categories this week; chronic top-3 from the 12-month archive
`Scheduled/_fpd-archive/fpd-history.csv`, which the engine appends to (deduped by ticket) only
after a successful bot post. The old "Source: Bravo saved report…" line and the "not included —
pipeline cell failed" line are gone for good — system names and partial-store notes never go to
a team channel. The Word doc is NOT produced in this run.

"""


def replace_section(text, start_pat, end_pat, new):
    m1 = re.search(start_pat, text)
    m2 = re.search(end_pat, text)
    if not m1 or not m2 or m2.start() <= m1.start():
        raise SystemExit("could not locate section %r .. %r" % (start_pat, end_pat))
    return text[:m1.start()] + new + text[m2.start():]


def main():
    with open(SKILL, encoding="utf-8") as fh:
        text = fh.read()
    if MARK in text:
        print("already patched")
        return 0
    bak = SKILL + ".bak-pre-comms-engine-" + dt.date.today().strftime("%Y%m%d")
    shutil.copy2(SKILL, bak)
    sep = r"={10,}\n"
    text = replace_section(text, sep + r"STEP 2 — Post to #loan-review", sep + r"STEP 3 — Post to #employee-performance", STEP2)
    text = replace_section(text, sep + r"STEP 3 — Post to #employee-performance", sep + r"STEP 4 — Post to #store-performance", STEP3)
    text = replace_section(text, sep + r"STEP 4\.5 — Post FPD ranking", sep + r"STEP 5 — Save files", STEP45)
    # Step 5: the Loan_Layaway docx referenced a retired SKILL; keep the line but mark optional.
    text = text.replace(
        "- `Loan_Layaway_Review_<TODAY>.docx` — combined loan + layaway doc per weekly-loan-layaway-review SKILL",
        "- `Loan_Layaway_Review_<TODAY>.docx` — OPTIONAL / best-effort (the channel posts in Step 2 are the record of truth; never let this step block Step 6)")
    with open(SKILL, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("patched; backup at " + bak)
    return 0


if __name__ == "__main__":
    sys.exit(main())
