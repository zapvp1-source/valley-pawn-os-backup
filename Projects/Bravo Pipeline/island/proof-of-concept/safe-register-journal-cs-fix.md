# PoC — Safe Register Journal Continuous Scrolling Fix

**Status:** ⚙️ Built on island. Not yet promoted to prod.
**Created:** 2026-06-08 (during the on-demand 2026-06-06 funds verification run).

## Problem

`reports/SafeRegisterJournal.ahk` fails its Preview-render wait roughly 50% of the time. Every failed cell logs:

```
[diag] cannot get Bravo root: (0x800705B4) This operation returned because the timeout period expired.
ERROR: UIA click sequence failed: Preview did not render within 30s (Export Document button never appeared)
```

Same handler call eventually succeeds after retry. Three-of-five stores failed on the first manual trigger of 2026-06-06; took three trigger drops to get all five CSVs.

## Root cause

Bravo's Report Preview has an "Enable Continuous Scrolling" toggle in the toolbar. When ON (the default after every Bravo restart), Bravo renders the entire Safe Register Journal as one giant canvas instead of paginating. During that render Bravo's UIA tree becomes unresponsive and `GetBravoRoot()` returns `0x800705B4` (RPC timeout). The Export Document button is technically present in the tree but unreachable.

`reports/DepositsAndPaidOuts.ahk` and `reports/DisbursementJournal.ahk` were patched 2026-05-29 to detect the CS toggle state and flip it OFF before clicking Export. `SafeRegisterJournal.ahk` was missed — it's the only export handler in `reports/` that doesn't toggle CS.

## Patch (additive)

Cloned `reports/SafeRegisterJournal.ahk` to `island/source/SafeRegisterJournal_island.ahk` and made two surgical changes:

1. **Step 5 wait extended:** `FindByName(preview_export, 30000)` → `60000`. Matches the 2026-05-29 patch on the other two handlers.
2. **Step 5b added:** the verbatim CS-toggle-off block from `reports/DepositsAndPaidOuts.ahk` lines 170–211. Inserted between the preview-render wait and the Export click. Wrapped in try/catch so it can never itself throw.

No other code path changed. Constants, UIA element map, Export Document dialog setters, Done sequence — all untouched.

## How to verify on the island

The island has no scheduled task wired to drive this handler (we'd need to copy the watcher + dispatch table to truly run it standalone). Two practical verification paths:

**Path A — read-only diff verification.**
Diff the island handler against prod and confirm only the two intended hunks changed:

```bash
diff -u \
  "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/reports/SafeRegisterJournal.ahk" \
  "/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/island/source/SafeRegisterJournal_island.ahk"
```

Expected: file-header block (purely doc) + the two surgical patches inside `PullSafeRegisterJournal`.

**Path B — single-cell smoke after deploy.**
After step 1 of the deployment checklist below, drop a one-store trigger for an arbitrary recent date and watch the log:

```json
{
  "id": "srj-cs-smoke-2026-06-08T00-00-00",
  "requested_at": "2026-06-08T00:00:00-04:00",
  "reports": [{"name": "safe-register-journal", "stores": ["WAY"], "date": "2026-06-07"}]
}
```

Look for `[pre-export] Continuous Scrolling is ON — calling Toggle()` followed by `post-toggle state = 0 (0=Off)` in `logs/srj-cs-smoke-...log`. If both lines appear and the cell hits SUCCESS, the fix is confirmed.

## Deployment checklist (island → prod)

Once verified (or accepted by Joshua based on the diff alone — the change is mechanical):

1. **Pre-flight diff.** Run the diff above. Confirm the change matches what's in this PoC.
2. **Copy with prod filename.** Drop the `_island` suffix:
   ```bash
   cp "/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/island/source/SafeRegisterJournal_island.ahk" \
      "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/reports/SafeRegisterJournal.ahk.candidate-2026-06-08"
   ```
   Note: copied to a `.candidate` filename first so prod's handler is never overwritten mid-watcher-loop. Joshua moves it into place when the watcher is idle.
3. **Move into place when watcher idle.** `mv ...candidate-2026-06-08 SafeRegisterJournal.ahk`. Watcher picks up new handler code on the next trigger claim (no dispatch table change — same cell name).
4. **Reload watcher.** Per `bravo-context` SKILL.md restart procedure — relaunch `bravo_watcher.ahk` so the new handler is loaded into memory.
5. **First-run smoke.** Drop the single-store trigger from Path B above. Watch the log for the two CS-toggle lines + SUCCESS.
6. **Five-store smoke.** Drop a full-store trigger for the same date. Verify all 5 cells hit SUCCESS without any retries.
7. **Update prod registry.** Bump `bravo-pipeline-registry.md` row for `safe-register-journal`: "Last verified" → today's date.
8. **Update island registry.** Bump status to 🚀 deployed with today's date.

## Rollback

If first-run smoke fails:

```bash
cp "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/reports/SafeRegisterJournal.ahk.candidate-2026-06-08" \
   /tmp/srj-island-attempt-2026-06-08.ahk

# The original handler is preserved in git via the lib/* and reports/* .bak-*
# convention. Restore from the most recent backup, OR pull from git.
cd "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction"
git log --oneline reports/SafeRegisterJournal.ahk | head -5
git checkout HEAD -- reports/SafeRegisterJournal.ahk
```

Reload watcher. Drop the smoke trigger. Confirm pre-patch behavior restored (i.e. confirms rollback worked, even if it means re-introducing the intermittent failure).

## Out of scope for this PoC (parked for later)

- **Bravo not running at all.** The 2026-06-06 run first failed because Bravo wasn't open in the VM — the watcher's `WaitForBravoReady(30)` fails before any recovery path is reachable. Fix would be a launcher script: detect Bravo not running, launch via Search → Bravo from taskbar (per memory), then proceed. Separate PoC.
- **Session-selection-screen handling on cold-start.** Already implemented in `lib/Bravo.ahk` `RecoverFromAutoLock` (Session List → Resume Session / New User branches with username failsafe). Verified working in the 2026-06-07 23:39 retry log. No change needed.
- **`Export Document` button selector confusion.** Error message text says "Export Document" but `SRJ_ELEMENTS["preview_export"]` actually looks for `"Export..."`. The handler is correct; only the error string is misleading. Cosmetic only.
