# Bravo AHK Handler — Open Data-Accuracy Bugs

These are known data-accuracy bugs in the watcher's report handlers, surfaced 2026-05-13 by Preston Peters (store manager) reviewing the Slack posts. They affect the numbers that go to the operations channels, NOT the watcher's ability to complete a run. Both require Bravo access to verify the fix.

Until each is fixed, the corresponding Slack post should either be held back or annotated. See `weekly-loan-layaway-review/SKILL.md` for the current hold rules.

---

## Bug 1 — `Layaways.ahk` reads stale red-bubble badges

**Status (2026-05-13):** click-each-category patch APPLIED, awaiting live verification. The handler now calls `ClickCategoryAndCountRows()` for each of the 5 categories — clicks the category, waits 1500ms, then counts rendered list rows. Falls back to the old `ReadBadgeCount()` if the list rows can't be detected. Backup at `reports/Layaways.ahk.bak-pre-click-each-category-2026-05-13`.

**Verification needed on next live run:** check the watcher log for `[click-count] '<category>' -> <N>` lines (new method worked) vs `[click-count] '<category>' -> rows undetectable, falling back to badge read` (fallback fired). If all 5 categories use the new method, great — compare numbers to badge counts to see if they ever disagree (which is what Preston's concern would predict). If the fallback fires on any category, we know the list-row detection pattern needs adjustment (likely a different UIA element type than DataItem/TreeViewItem on the Layaways view).

**File:** `reports\Layaways.ahk` (Windows VM path) — invoked by the `layaways` report handler in `bravo_watcher.ahk`.

**Old behavior (now in fallback path only):** the handler captures the five badge counts from the right-sidebar of the Bravo Layaways view directly from the red-bubble indicators next to each category name:
- Layaways Overdue
- Past Payment Due Date
- Contacted But No Activity
- No Payment in 30 days
- Locate Layaways

It writes those five numbers into `output/<DATE>_<STORE>_layaways.csv` columns `overdue, past_pmt_due, contacted_no_activity, no_pmt_30d, locate`.

**The bug:** the red-bubble badge counts are not always up to date. They can lag behind the actual filtered list. Preston's words (relayed by Joshua, 2026-05-13): "He's just pulling the red bubble part from what I can tell which isn't always up to date."

**Correct method:** for each of the five categories, click the category name on the right sidebar. Bravo will then filter the main list to just that category. Read the count displayed at the **TOP of the screen** for that filtered view (this is the authoritative number — Bravo computes it from the actual filtered set on each click). Move to the next category, click, read the top-of-screen number, etc. After all five are captured, return to the unfiltered Layaways view.

**Patch spec for the next code change:**
1. For each category in the canonical order `["Layaways Overdue", "Past Payment Due Date", "Contacted But No Activity", "No Payment in 30 days", "Locate Layaways"]`:
   - `ClickByName(<category>, 4000)` on the right-sidebar element.
   - `Sleep(800)` for the list to re-render.
   - Find the top-of-screen count element. UIA element name is TBD — needs to be captured in the VM with the UIA inspector once Joshua is back. Likely candidates: a TextBlock or Label near the page header showing `"Showing N of M results"` or similar.
   - Parse out the integer.
   - `DismissPopups()` defensively.
2. After all five are captured, click an "All" or "Clear filter" button (or navigate back to the Layaways landing view) so the next store-switch finds a clean state.
3. Write the five integers to the CSV in the same column order the post template expects.

**Cannot verify without Bravo access** — the UIA element names for the top-of-screen count and the unfiltered/clear-filter button are unknown. Run `uia-discover` on the Layaways view to find them.

**Test plan once patched:**
- Drop a single-store layaway trigger (e.g. `{stores: ["CUL"], date: ...}`) and compare the CSV output against what Bravo shows when you manually click each category. Numbers should match.
- Compare against the historical red-bubble output for the same date — they should be the same when bubbles happen to be up to date, and different when they're stale (the patched version should be the authoritative one).

---

## Bug 2 — `Loans75DaysPastDue.ahk` may not be using the saved custom report

**File:** `reports\Loans75DaysPastDue.ahk` (Windows VM path) — invoked by the `loans-75-days-past-due` report handler.

**Current behavior (suspected):** the handler synthesizes the 75-day-past-due count by running an Ad Hoc loans query and filtering. The result has been showing 0 items / $0.00 for every store, which is plausible for a clean week but also plausible for a handler bug.

**What Preston says (2026-05-13):** "There is a 75 days past due report saved in the loans/buys custom reports already." The handler should be running THAT saved custom report and reading its output, not building the query from scratch each time.

**Patch spec for the next code change:**
1. Navigate to Loans / Buys → Custom Reports in Bravo.
2. Find and click the saved report named (TBD — Preston would know the exact name; likely "75 Days Past Due" or "75-day Past Due Loans"). Capture the exact name with `uia-discover` on the Custom Reports view.
3. Wait for the report to render.
4. Capture the rendered list count (top-of-screen, same pattern as the layaway fix) for the `count` field.
5. Capture the total $ from the report's summary panel for the `dollar_sum` field.
6. Write to CSV in the same `store, date, count, dollar_sum` format.

**Cannot verify without Bravo access** — the exact saved-report name and its UIA path are unknown.

**Test plan once patched:**
- Drop a single-store loan trigger and compare against what Preston sees when he opens the saved custom report manually. Numbers should match.
- If yesterday's all-zero result is a real clean week, the patched handler should also produce all-zeros for the same date. If it produces non-zero numbers, the original handler was buggy and we now have correct data.

---

## Bug 3 — `CompanyKpis.ahk` is a stub (blocks `monday-store-rankings`)

**File:** `reports\CompanyKpis.ahk` (Windows VM path).

**Current state:** stub. The handler returns a controlled `error` with `"Company KPIs SSRS URL template not yet captured — see reports/CompanyKpis.ahk header for setup steps."` Any trigger that asks for `company-kpis` gets a clean failure rather than a crash, and the watcher continues to the next report.

**Why:** Company KPIs renders in an SSRS browser tab rather than native Bravo UI. The header comment in the stub proposes a direct HTTPS fetch (`&rs:Format=CSV` against the SSRS URL), which is the cleanest path *if* we can capture the URL and any auth cookies.

**Two implementation paths, pick one:**

### Path A — Direct SSRS CSV fetch (preferred if it works)

Joshua's role (5 minutes, requires Bravo access):
1. Inside the VM, open Edge.
2. Navigate to Bravo → Reports → Company KPIs.
3. Run the report for the current month (or whatever timespan we want).
4. Once it renders, copy the FULL URL from Edge's address bar — it'll contain parameters like `StartDate`, `EndDate`, possibly `StoreCode`, and the SSRS path.
5. Paste that URL here (or DM it).
6. Also confirm whether you have to log in to SSRS separately — if so, we need to capture the auth cookie too.

Once captured, the SKILL update is small: paste the URL template into `SSRS_URL_TEMPLATE`, parameterize date fields, and add a PowerShell `Invoke-WebRequest` call to fetch the CSV.

### Path B — UI-drive the Company KPIs report (fallback if SSRS auth is too messy)

Same pattern as `Loans75DaysPastDue.ahk` and other handlers — navigate via UIA to the Reports tile, click Company KPIs, parse the rendered table via UIA `FindElements({Type: "DataItem"})`.

Joshua's role (15 minutes, requires Bravo access):
1. Inside the VM, run Company KPIs and get the report rendered.
2. Run `uia-discover` (the existing handler in `reports\UIADiscover.ahk`) to dump the UIA tree.
3. Share the dump. We'll write the handler to navigate to and parse the relevant cells.

### Until either path is implemented

The orchestrator SKILL already skips the `#store-performance` post and notes in the DM that store rankings need to be run manually. No data loss — just a manual step.

## Why these aren't blocking the watcher

Both bugs produce *wrong* numbers, not crashes. The watcher completes its run, writes the CSVs, and the orchestrator chains the Slack posts. The numbers just may not reflect reality. The new safety rails (auth-failure circuit breaker + hard-wall timeout) don't help here because nothing is timing out — the handlers happily return wrong data quickly.

The mitigation is procedural until the code fix is in:
1. The orchestrator should DM Joshua before publishing the loan and layaway posts when their handlers haven't been verified.
2. Joshua can manually verify by opening the right Bravo views and comparing.
3. Once verified once, the operational team can trust subsequent runs of the same handler.

---

## Patch workflow notes (lesson from 2026-05-13)

Any patch to these handlers MUST follow the safer-edit rules established in `recovery.md`:
- No keystrokes (Send / Ctrl+V) without first verifying focus actually moved.
- Use UIA `Value :=` assignment or `ClickByName` (with built-in retry) instead of blind Focus + Send.
- Dry-run-test in the VM against a non-production Bravo state before letting the watcher run the patch over real reports.
- Apply ONE change at a time. Yesterday's lockout came from layering a second broken patch on top of a first sound patch.
- Always make a `.bak-YYYY-MM-DD` copy of the file before any change.
- The watcher's auth-failure circuit breaker (default 3 consecutive failures) is the final backstop — keep it armed at all times.
