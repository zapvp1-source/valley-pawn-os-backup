---
name: monday-bravo-combined-run
description: Monday morning orchestrator — runs the five existing weekly Valley Pawn Bravo reviews via the Bravo Data Extraction pipeline. ONE trigger drop fetches all required CSVs; the orchestrator then chains the five chained tasks for compilation + Slack posting. No Parallels grant required.
---

You are running Joshua's Monday morning combined Valley Pawn Bravo POS run.

The 2026-05-12 architecture: the data collection no longer drives Bravo's UI. The Bravo Data Extraction pipeline (`/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`) runs inside the Windows VM and produces all required CSVs from a single trigger drop. The orchestrator's job is now: drop ONE multi-report trigger, wait, then chain the five chained SKILLs for compilation + Slack post + file save.

==========================================================================
STEP 1 — Drop ONE multi-report trigger
==========================================================================

Generate trigger ID `monday-bravo-combined-YYYY-MM-DD`. Write to `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/<id>.json`:

```json
{
  "id": "monday-bravo-combined-2026-05-12",
  "requested_at": "2026-05-12T05:30:00-04:00",
  "reports": [
    {"name": "aged-inventory-summary", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-12"},
    {"name": "loans-75-days-past-due", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-12"},
    {"name": "layaways", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-12"},
    {"name": "employee-activity", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-01"},
    {"name": "chekkit-inactives", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-12"}
  ]
}
```

After the result JSON arrives, **copy each chekkit-inactives CSV into the shared stash** so the Tuesday chekkit-weekly-review-requests task can find it without re-pulling:

```applescript
do shell script "mkdir -p '/Users/joshuadavis/Documents/Claude/Scheduled/_shared-bravo-data/2026-05-12/chekkit-inactives' && cp '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/2026-05-12_CUL_chekkit-inactives.csv' '/Users/joshuadavis/Documents/Claude/Scheduled/_shared-bravo-data/2026-05-12/chekkit-inactives/CUL.csv'"
```

Repeat for HAR/LEX/ROA/WAY. The Tuesday task's Step 1A will find this stash and skip its own pull.

(Note: `company-kpis` is not yet pipeline-ready; the orchestrator skips the store-rankings post and notes it in the DM — see below.)

Poll `results/<id>.result.json`. Total run takes ~20-30 minutes (4 reports × 5 stores × ~30-60s each). Time out at 45 minutes.

==========================================================================
STEP 2 — Compile + post via chained SKILLs
==========================================================================

After the result JSON arrives, run each chained SKILL's compile+post phase using the CSVs in `output/`. Read each chained SKILL once at the start of the run to load the format templates:

- `/Users/joshuadavis/Documents/Claude/Scheduled/weekly-aged-inventory-report/SKILL.md`
- `/Users/joshuadavis/Documents/Claude/Scheduled/monday-store-rankings/SKILL.md` (still computer-use until company-kpis is pipeline-ready)
- `/Users/joshuadavis/Documents/Claude/Scheduled/weekly-loan-layaway-review/SKILL.md`
- `/Users/joshuadavis/Documents/Claude/Scheduled/weekly-employee-sales-rankings/SKILL.md`
- `/Users/joshuadavis/Documents/Claude/Scheduled/chekkit-weekly-review-requests/SKILL.md` (Phase 1 still computer-use)

For each, execute its parse-and-post sections using the CSVs already on disk. Do NOT re-drop a per-task trigger — the data is already there.

**Post order (per established convention):**
1. `#aged-inventory-review` (`C04NGH4FF35`) — aged inventory 5-store summary
2. `#store-performance` (`C03CGTN3KN1`) — MTD store rankings summary + thread reply. SKIP if company-kpis pipeline cell isn't available; note in DM that store rankings need to be run separately.
3. `#loan-review` (`C0B08RS2BMK`) — past-due loan post (count + dollar + %)
4. `#layaway-review` (`C04N24STDP1`) — layaway 5-column table
5. `#employee-performance` (`C0ATTLPQHR8`) — ranked employees

Save files:
- `Valley_Pawn_Store_Rankings_{Month}{YYYY}.xlsx` (skip if store rankings skipped)
- `Loan_Layaway_Review_{YYYY-MM-DD}.docx`
- `employee-sales-rankings-{YYYY-MM-DD}.xlsx`
- Chekkit CSVs stashed at `/Users/joshuadavis/Documents/Claude/Scheduled/_shared-bravo-data/{YYYY-MM-DD}/chekkit-inactives/{STORE}.csv` (requires running chekkit Phase 1 via computer-use until that pipeline cell is built)

==========================================================================
STEP 3 — Final DM to Joshua
==========================================================================

DM Joshua (`U03BB52MDSA`) with the roll-up:

```
✅ Monday combined Bravo run complete.

Pipeline-driven (no Parallels grant used this run):
✅ weekly-aged-inventory-report — posted to #aged-inventory-review
✅ weekly-loan-layaway-review — posted to #loan-review + #layaway-review, doc saved
✅ weekly-employee-sales-rankings — posted to #employee-performance, xlsx saved

Still requiring computer-use (pipeline cells not yet built):
⚠️ monday-store-rankings — company-kpis (SSRS) needed; run manually
⚠️ chekkit-weekly-review-requests Phase 1 — chekkit-inactives row-walk needed

Files in /Users/joshuadavis/Documents/Claude/Scheduled/.
```

If any chained task failed at the compile/post phase, replace ✅ with 🚨 and add a one-line reason.

==========================================================================
LEGACY DESIGN — for reference, no longer used
==========================================================================

The previous orchestrator (pre-2026-05-12) drove Bravo via computer-use with a multi-capture-per-store loop and sub-agents firewalling screenshot context. That design is preserved in git history but is not the current path. The pipeline-driven version handles store cycling internally and produces CSVs directly — no screenshots, no sub-agents needed for the data collection phase.

The compile + Slack post + file save phases of each chained SKILL are unchanged — the data sources just moved from on-screen reads to CSV parsing.

==========================================================================
IF PIPELINE FAILS
==========================================================================

- If the result JSON shows any cell as `error`, attempt the chained SKILL's post anyway using whatever CSVs DID succeed — note missing stores in the post footer.
- If the pipeline times out entirely (no result JSON after 45 min), fall back to running each chained task individually via the legacy computer-use path. DM Joshua "Pipeline timed out — running individual tasks via Parallels" and continue.
- If the watcher isn't running (no result JSON AND no CSVs in `output/`), DM Joshua to restart the watcher in the VM and re-trigger this task.
