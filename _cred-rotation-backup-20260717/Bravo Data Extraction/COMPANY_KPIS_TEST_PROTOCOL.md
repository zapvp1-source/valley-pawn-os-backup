# Company KPIs pipeline cell — test protocol

Goal: prove the new `CompanyKpis.ahk` handler can fetch the SSRS Company KPI
report as a CSV via Edge inside the VM, end-to-end, without computer-use.

Once this passes, we wire `company-kpis` into the Monday combined run and
flip `monday-store-rankings/SKILL.md` from computer-use to CSV-parse mode.

## What the handler does

1. Picks any store (defaults to CUL) and confirms Bravo is logged into it.
2. Returns to the Bravo Dashboard.
3. Clicks the **Company KPIs** button in the Reporting Pro section.
4. Sets Start Date / End Date in the resulting dialog via UIA ValuePattern.
   If ValuePattern fails, the dialog still gets submitted — we rely on the
   subsequent direct URL navigation in Edge to override the dates.
5. Clicks **Ok**. Bravo hands off to Edge with the SSRS report URL (HTML
   render). Forms auth completes in Edge — JS sets the Akamai cookies, the
   `.ASPXAUTH` cookie is issued.
6. Snapshots `C:\Users\joshuadavis\Downloads` to remember what `.csv` files
   already exist.
7. Activates Edge, sends `Ctrl+L`, pastes the same URL with `&rs:Format=CSV`
   and the explicit `StartDate=YYYY/M/D&EndDate=YYYY/M/D` we want, hits Enter.
   Edge treats `text/csv` as a download — the CSV lands in Downloads using
   the auth cookies from step 5.
8. Polls Downloads for the new `.csv`, waits for size to stabilize, sanity-
   checks that the first byte isn't `<` (would mean HTML/login redirect), and
   moves the file to
   `output/2026-05-22_ALL_company-kpis.csv`.

## Pre-flight (one-time)

Before dropping the trigger, confirm:

- [ ] Parallels VM is running.
- [ ] `bravo_watcher.ahk` is alive (Ctrl+Alt+W is the safety exit hotkey).
- [ ] `BravoAutoLogin.ahk` is alive — without it, mid-run auto-lock recovery
  is less reliable.
- [ ] Bravo is logged into ANY store (CUL is fine — the handler will switch
  via `EnsureStore` if needed).
- [ ] **Edge is open and you have signed into SSRS at least once this VM
  boot.** Easiest way: from Bravo Dashboard, click "Company KPIs", let Edge
  open the report, dismiss any "Click to Continue" Forms-auth button if it
  appears, then close that tab. This proves the auth path works and seeds
  the cookies the new handler will reuse. (If this step is painful, we'll
  add a boot-time seeding script — that's the documented "future work" in
  CompanyKpis.ahk's header.)
- [ ] `C:\Users\joshuadavis\Downloads` exists.

## Dry-run steps

1. Open this folder in Finder. Drag `test_company_kpis.json` into
   `triggers/`. (The watcher polls every 30s — Ctrl+Alt+R inside the VM
   forces an immediate poll.)
2. Make Parallels visible so you can watch.
3. Tail the log file:
   ```bash
   tail -f '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/company-kpis-test-2026-05-22.log'
   ```
4. Expected sequence (each step prints to the log):
   - `[ALL] CompanyKpis range=2026-05-01..2026-05-22`
   - `store confirmed: CUL`
   - `step 1: click Dashboard 'Company KPIs' button`
   - `step 2a: set Start Date = 2026-05-01`
   - `step 2b: set End Date = 2026-05-22`
   - `step 3: click Ok to launch report in Edge`
   - `step 4: waiting for Edge tab containing 'Company Performance'`
   - `step 5: Ctrl+L + paste CSV URL + Enter`
   - `step 6: waiting for new CSV in C:\Users\joshuadavis\Downloads`
   - `downloaded: C:\Users\joshuadavis\Downloads\BRAVO Company Performance.csv` (or similar)
   - `moved -> ...output\2026-05-22_ALL_company-kpis.csv`
   - `SUCCESS: <N> rows, <ms>ms`
5. After completion, verify:
   - `output/2026-05-22_ALL_company-kpis.csv` exists and is non-empty.
   - First line is a CSV header (column names), not `<html>`.
   - The CSV contains rows for at least the 5 stores (CUL / HAR / LEX / ROA /
     WAY) or 5 store columns + metric rows — we don't yet know the exact
     shape SSRS exports.
6. Send me the CSV so I can write the parser in
   `monday-store-rankings/SKILL.md`.

## Failure modes to watch for

| Symptom | Likely cause | Fix |
|---|---|---|
| Handler errors at "Edge did not show a tab with 'Company Performance'" | Bravo's Dashboard button didn't actually open Edge | Confirm Edge is the default browser for SSRS links; pre-auth Edge once manually |
| `step 6` times out, no new CSV | Edge got an auth/redirect page, didn't download | Re-do the manual pre-auth step; check `Downloads/*.html` for a saved page |
| `downloaded file looks like HTML (first byte '<')` | Auth cookies expired or weren't set | Same as above; verify by manually navigating to the CSV URL in Edge |
| Bravo dialog dates not accepted, ValuePattern errors | UIA fields lack ValuePattern (date picker only) | Add a calendar-pick fallback — see monday-store-rankings step 2 for the manual click path |
| Auth dialog blocks Ctrl+L (focus stolen by SSRS login page) | First-time-this-session Forms auth requires manual click | Click "Click to Continue" on the SSRS Forms-auth page once; re-drop the trigger |

## After success

When the CSV lands correctly:

1. Inspect the column layout. Common SSRS exports flatten the matrix to
   `Metric, Grand Total, CUL, HAR, LEX, ROA, WAY` or to long form
   `Metric, Store, Value`.
2. Update `monday-store-rankings/SKILL.md` Steps 1–3 to read this CSV
   instead of driving Bravo via computer-use. Steps 4–6 (rank, spreadsheet,
   Slack post) stay verbatim.
3. Add the cell to `monday-bravo-combined-run/SKILL.md`'s trigger template:
   ```json
   {"name": "company-kpis", "stores": ["ALL"], "date": "{FIRST_OF_MONTH}..{YESTERDAY}"}
   ```
   and remove the "SKIP store-rankings" branch + the "Still requiring
   computer-use" line from the final DM template.
4. Re-enable `monday-bravo-combined-run` so the full 6-cell run fires
   automatically Monday morning.
