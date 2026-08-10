; ============================================================================
; reports/JewelryCaseCount.ahk
;
; Jewelry Count Reconciliation v3 — COUNT-ONLY on-hand snapshot.
;
; THE POINT (2026-08-09): the manager's EOD sheet is five numbers — Rings,
;   Bracelets, Necklaces, Earrings, Pendants — the physical headcount of the
;   case at open and close. To reconcile, we need five matching numbers from
;   Bravo. We do NOT need the item detail behind them.
;
;   JewelryCaseAudit.ahk (2026-08-06) tried to export every on-hand row and
;   count them. That runs straight into the DevExpress virtualiser paging bug
;   documented in BRAVO_KNOWN_ISSUES.md ("STILL OPEN", 2026-08-03): on grids
;   over ~270 rows the walker stops yielding new rows non-deterministically
;   (78 and 268 captured on two runs of the same 2331-row report). The
;   2026-08-06 WAY probe hung at 22 of 327 Rings for exactly this reason.
;
;   But that same probe log proves Bravo HANDED US THE ANSWER before the walk
;   ever started: every grid row carries an accessibility Name of the form
;     "Row N of TOTAL, Column LABEL, Column X of Y: VALUE"
;   and TOTAL is the full on-hand count for that category — 327 — available
;   from the FIRST rendered page, in ~60s, with zero paging.
;
;   So this handler reads TOTAL and stops. It never walks the grid, which
;   means the paging bug cannot affect it at any inventory size.
;
;   Same technique already proven in production by ItemsToPrice.ahk, which
;   reads Bravo's own "Price Items: N" header counter instead of walking.
;
; DESIGN: ONE cell, ONE store visit, all 5 categories. The store switch is the
;   expensive step (~25s); running five separate cells paid it five times. This
;   switches once, then runs the five saved reports back-to-back and writes a
;   single 5-row CSV per store.
;
; NO FALSE ZEROS (the hardest-won lesson in this project — see STATUS.md
;   "Fix 1 — FALSE ZEROS" 2026-07-30, and JewelryCountAudit's removed
;   empty-grid heuristic). A category that renders no rows is NOT reported as
;   0. It is retried once, then that category is recorded as an ERROR. For a
;   loss-prevention control, a wrong all-clear is worse than no answer.
;
; ADDITIVE (Rule #4): NEW file, ONE new cell name (jewelry-case-counts).
;   Touches nothing. JewelryCaseAudit.ahk and its 5 cells stay registered and
;   unmodified; they are simply not used by the reconciliation any more.
;
; Trigger schema:
;   {"name": "jewelry-case-counts", "stores": ["WAY"], "date": "YYYY-MM-DD"}
;   "date" is captured as the as-of stamp in the filename only — these saved
;   reports are current-state and take no date override.
;
; Output CSV: output/<date>_<STORE>_jewelry-case-counts.csv
;   store,category,as_of,count,status
;   WAY,Rings,2026-08-09,327,ok
;   WAY,Pendants,2026-08-09,88,ok
;   ...
; ============================================================================

#Requires AutoHotkey v2.0

; Category -> saved report name. Same 5 saved reports Joshua built 2026-08-06.
; NOTE the sheet has five buckets: Rings, Bracelets, Necklaces, Earrings,
; Pendants. Bravo splits neck-worn stock into Chains + Necklaces, so those two
; SUM to the sheet's single "Necklaces" line (Joshua, 2026-08-06: "Those
; reports will need combined totals to match the count sheet"). Bracelets has
; no saved report yet — see JEWELRY_CASE_COUNT_SHEET_MAP below.
global JEWELRY_CASE_COUNT_REPORTS := Map(
    "Rings",     "Claude Jewelry Audit - Rings",
    "Pendants",  "Claude Jewelry Audit - Pendants",
    "Earrings",  "Claude Jewelry Audit - Earrings",
    "Chains",    "Claude Jewelry Audit - Chains",
    "Necklaces", "Claude Jewelry Audit - Necklaces"
)

; Deterministic run order — keeps the CSV stable for diffing across days.
global JEWELRY_CASE_COUNT_ORDER := ["Rings", "Pendants", "Earrings", "Chains", "Necklaces"]

global JEWELRY_CASE_COUNT_ELEMENTS := Map(
    "sidebar_inventory",    "Inventory",
    "panel_custom_reports", "Custom Reports",
    "dialog_ok",            "Ok",
    "panel_cancel",         "Cancel"
)

; ----------------------------------------------------------------------------
; ReadGridTotalFromAccessibility()
;
; Reads Bravo's own row total off the first rendered grid page. Returns the
; TOTAL from "Row N of TOTAL", or -1 if no DataItem carried a parseable name.
;
; This is deliberately read-only and does not scroll, click, or page. The
; whole reason this handler is reliable is that it never touches the
; virtualiser.
; ----------------------------------------------------------------------------
ReadGridTotalFromAccessibility() {
    total := -1
    dataItems := 0
    try {
        root := GetBravoRoot()
        dataItems := root.FindElements({Type: "DataItem"})
    } catch as e {
        LogMessage("      [count] enumerate DataItems failed: " . e.Message)
        return -1
    }
    if (!dataItems || dataItems.Length = 0)
        return -1

    for di in dataItems {
        kids := 0
        try kids := di.FindElements({Scope: 2})
        if (!kids || kids.Length = 0)
            continue
        for k in kids {
            kName := ""
            try kName := k.Name
            if RegExMatch(kName, "Row (\d+) of (\d+)", &m) {
                rt := Integer(m[2])
                if (rt > total)
                    total := rt
                break
            }
        }
        if (total > 0)
            break   ; every row reports the same TOTAL; first one is enough
    }
    return total
}

; ----------------------------------------------------------------------------
; RunOneJewelryCategoryCount()
;
; Assumes we are already on the Dashboard of the correct store. Opens
; Inventory -> Custom Reports, selects the category's saved report, runs it,
; reads the row total, and returns Bravo back to the Dashboard.
;
; Returns the count (>=1), or -1 on failure. NEVER returns 0 — see the
; no-false-zeros note in the file header.
; ----------------------------------------------------------------------------
RunOneJewelryCategoryCount(category, wantReport) {
    count := -1

    DismissPopups()
    LogMessage("    step 1: open Inventory")
    ClickByName(JEWELRY_CASE_COUNT_ELEMENTS["sidebar_inventory"], 8000)
    Sleep(1500)
    DismissPopups()

    LogMessage("    step 2: click Custom Reports")
    ClickByName(JEWELRY_CASE_COUNT_ELEMENTS["panel_custom_reports"], 5000)
    Sleep(1500)

    LogMessage("    step 3: select saved report '" . wantReport . "'")
    ; SelectInventorySavedReport (NOT the generic SelectSavedReport) — the
    ; Inventory module needs the combo committed differently. This is the
    ; 2026-08-03 ActiveInvDetails fix; the generic one silently fails here.
    if !SelectInventorySavedReport(wantReport)
        throw Error("SelectInventorySavedReport: could not select " . wantReport)
    Sleep(1000)

    ; No date override — current-state report.
    LogMessage("    step 4: click Ok to run")
    Sleep(2500)
    ActivateBravo()
    Sleep(500)
    try {
        ClickByName("Ok", 5000)
    } catch as okErr {
        ; Bravo 2026.6.0.79 ClickOnce regression: Enter does not always
        ; confirm. Ok-by-name first, Enter only as fallback.
        Send("{Enter}")
        LogMessage("      Ok not found (" . okErr.Message . ") -- sent {Enter} fallback")
    }
    Sleep(2000)

    LogMessage("    step 5: wait for grid, read row total")
    rendCheckStart := A_TickCount
    Loop {
        count := ReadGridTotalFromAccessibility()
        if (count > 0) {
            LogMessage("      [count] " . category . " = " . count
                     . " (read from grid header after "
                     . ((A_TickCount - rendCheckStart) // 1000) . "s, no walk)")
            break
        }
        if (A_TickCount - rendCheckStart > 90000) {
            LogMessage("      [count] " . category . " — no parseable row total after 90s")
            break
        }
        Sleep(2000)
    }

    ; Leave the report editor cleanly regardless of outcome. A stranded
    ; editor wedges the NEXT category and every task after this one — see
    ; BRAVO_KNOWN_ISSUES.md stranded-editor entries.
    try ClickByName(JEWELRY_CASE_COUNT_ELEMENTS["panel_cancel"], 3000)
    Sleep(800)
    try ClickByName(JEWELRY_CASE_COUNT_ELEMENTS["panel_cancel"], 3000)
    Sleep(800)
    if !BackToDashboard()
        throw Error("BackToDashboard failed after category " . category)
    Sleep(500)

    return count
}

; ----------------------------------------------------------------------------
; PullJewelryCaseCounts() — the cell entry point.
; ----------------------------------------------------------------------------
PullJewelryCaseCounts(store, asOfDate, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "jewelry-case-counts",
        "store",       store,
        "date",        asOfDate,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    global JEWELRY_CASE_COUNT_REPORTS, JEWELRY_CASE_COUNT_ORDER

    LogMessage("[" . store . "] JewelryCaseCount — 5 categories, count-only, as-of=" . asOfDate)

    outputFileName := asOfDate . "_" . store . "_jewelry-case-counts.csv"
    outputPath := outputDir . "\" . outputFileName
    LogMessage("  output -> " . outputPath)

    if !WaitForBravoWindowExists(30)
        return Fail(result, started, "Bravo window not found within 30s")

    ActivateBravo()
    DismissPopups()

    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    ; Pre-dismiss stranded dialogs before we start (same defense as
    ; ActiveInvDetails / BuysFromPublic).
    ActivateBravo()
    Loop 4 {
        dismissed := false
        try {
            root := GetBravoRoot()
            cancelEl := root.FindElement({AutomationId: "btnCancel"})
            if cancelEl {
                try {
                    cancelEl.InvokePattern.Invoke()
                    dismissed := true
                } catch as ie {
                    try {
                        cancelEl.Click("left")
                        dismissed := true
                    }
                }
                Sleep(900)
            }
        }
        if (!dismissed)
            break
    }
    Sleep(300)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    ; --- run the five categories ---------------------------------------------
    counts   := Map()
    statuses := Map()
    okCount  := 0

    for category in JEWELRY_CASE_COUNT_ORDER {
        wantReport := JEWELRY_CASE_COUNT_REPORTS[category]
        LogMessage("  --- category " . category . " ('" . wantReport . "') ---")

        got := -1
        Loop 2 {   ; one retry per category before giving up on it
            attempt := A_Index
            try {
                got := RunOneJewelryCategoryCount(category, wantReport)
            } catch as e {
                LogMessage("    attempt " . attempt . " threw: " . e.Message)
                got := -1
                ; Try to get back to a clean Dashboard so the NEXT category
                ; isn't poisoned by this one's failure.
                try {
                    Loop 2 {
                        try ClickByName(JEWELRY_CASE_COUNT_ELEMENTS["panel_cancel"], 2000)
                        Sleep(700)
                    }
                    BackToDashboard()
                }
                Sleep(1000)
            }
            if (got > 0)
                break
            if (attempt = 1)
                LogMessage("    retrying " . category . " once")
        }

        if (got > 0) {
            counts[category]   := got
            statuses[category] := "ok"
            okCount++
        } else {
            counts[category]   := ""
            statuses[category] := "error"
            LogMessage("    " . category . " FAILED after 2 attempts — recorded as error, NOT as zero")
        }
    }

    ; --- write the CSV --------------------------------------------------------
    ; Written even on partial success: the file is the durable record, and a
    ; per-category status column means the consumer can tell a real count from
    ; a missing one. The consumer (jewelry reconciliation) is responsible for
    ; refusing to post a partial comparison — see the never-post-partial-data
    ; rule.
    csv := "store,category,as_of,count,status`n"
    for category in JEWELRY_CASE_COUNT_ORDER {
        csv .= store . "," . category . "," . asOfDate . ","
             . counts[category] . "," . statuses[category] . "`n"
    }

    try {
        ResetOutputFile(outputPath)
        FileAppend(csv, outputPath, "UTF-8")
    } catch as we {
        return Fail(result, started, "Could not write CSV: " . we.Message)
    }

    result["output_path"] := outputPath
    result["row_count"]   := okCount

    if (okCount < JEWELRY_CASE_COUNT_ORDER.Length) {
        failed := ""
        for category in JEWELRY_CASE_COUNT_ORDER
            if (statuses[category] != "ok")
                failed .= (failed = "" ? "" : ", ") . category
        return Fail(result, started
                  , "Only " . okCount . " of " . JEWELRY_CASE_COUNT_ORDER.Length
                  . " categories returned a count. Failed: " . failed
                  . ". Refusing to report a partial jewelry count as success.")
    }

    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: all 5 category counts read, " . result["duration_ms"] . "ms")
    return result
}
