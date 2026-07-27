; ============================================================================
; reports/Layaways.ahk
;
; Reads the 5 right-panel badge counts from Bravo's Layaways view for a single
; store and writes a single-row CSV.
;
; SKILL it powers: weekly-loan-layaway-review (LAYAWAY side)
;
; UI path:
;   Dashboard -> Layaways (sidebar)
;   -> right panel shows 5 badges:
;       Layaways Overdue
;       Past Payment Due Date
;       Contacted But No Activity
;       No Payment in 30 days
;       Locate Layaways
;   -> read each badge's count from the UIA Name
;   -> Cancel back to Dashboard
;
; Output CSV columns:
;   store, date, overdue, past_pmt_due, contacted_no_activity, no_pmt_30d, locate
; ============================================================================

#Requires AutoHotkey v2.0

global LAYAWAY_ELEMENTS := Map(
    "sidebar_layaways", "Layaways",
    "badge_overdue",    "Layaways Overdue",
    "badge_past_pmt",   "Past Payment Due Date",
    "badge_contacted",  "Contacted But No Activity",
    "badge_30d",        "No Payment in 30 days",
    "badge_locate",     "Locate Layaways",
    "panel_cancel",     "Cancel"
)

PullLayaways(store, date, outputDir) {
    started := A_TickCount
    result := Map(
        "report",      "layaways",
        "store",       store,
        "date",        date,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    outputPath := outputDir . "\" . OutputFilename(date, store, "layaways")
    LogMessage("[" . store . "] Layaways date=" . date . " -> " . outputPath)

    if !WaitForBravoReady(30)
        return Fail(result, started, "Bravo window not found/ready within 30s")
    ActivateBravo()
    DismissPopups()

    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    ResetOutputFile(outputPath)

    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    overdue := pastPmt := contacted := nopmt30 := locate := 0

    try {
        DismissPopups()

        LogMessage("  step 1: open Layaways view")
        ClickByName(LAYAWAY_ELEMENTS["sidebar_layaways"], 8000)
        Sleep(2500)
        DismissPopups()

        ; Each badge appears as a Text or Button with a Name like "Layaways
        ; Overdue · 3" or with the count exposed via a child element. Walk
        ; common patterns.
        ; NEW (2026-05-13 per Preston Peters): click each category radio button
        ; on the right sidebar and read the count from the rendered list. The
        ; old behavior (read right-sidebar badge bubble in place) sometimes
        ; returns stale numbers; clicking forces Bravo to filter and re-render.
        ; If the click-then-count returns -1 (list not detectable), the
        ; ReadBadgeCount fallback runs — matches the old behavior so we never
        ; lose data even if the new code path has trouble.
        overdue   := ClickCategoryAndCountRows(LAYAWAY_ELEMENTS["badge_overdue"])
        pastPmt   := ClickCategoryAndCountRows(LAYAWAY_ELEMENTS["badge_past_pmt"])
        contacted := ClickCategoryAndCountRows(LAYAWAY_ELEMENTS["badge_contacted"])
        nopmt30   := ClickCategoryAndCountRows(LAYAWAY_ELEMENTS["badge_30d"])
        locate    := ClickCategoryAndCountRows(LAYAWAY_ELEMENTS["badge_locate"])

        LogMessage("    counts (click-each-category): overdue=" . overdue . " pastPmt=" . pastPmt . " contacted=" . contacted . " 30d=" . nopmt30 . " locate=" . locate)

        FileAppend("store,date,overdue,past_pmt_due,contacted_no_activity,no_pmt_30d,locate`r`n", outputPath, "UTF-8-RAW")
        FileAppend(store . "," . date . "," . overdue . "," . pastPmt . "," . contacted . "," . nopmt30 . "," . locate . "`r`n", outputPath, "UTF-8-RAW")

        ; Back to Dashboard
        try ClickByName(LAYAWAY_ELEMENTS["panel_cancel"], 3000)
        Sleep(800)

    } catch as e {
        LogVisibleNames()
        return Fail(result, started, "UIA click sequence failed: " . e.Message)
    }

    result["row_count"]   := 1
    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["duration_ms"] . "ms")
    return result
}

; Click a sidebar category radio button, wait for the filter to apply, then
; read the count of rendered rows in the main list. Returns the row count,
; or falls back to ReadBadgeCount() if the list rows can't be determined.
;
; Strategy:
;   1. ClickByName(categoryName) — Bravo filters the list.
;   2. Sleep ~1500ms for Bravo to render the filtered set.
;   3. Try CountLayawayListRows() — count DataItem / TreeViewItem rows.
;   4. If >= 0, return that.
;   5. Otherwise log a fallback notice and return ReadBadgeCount(categoryName).
ClickCategoryAndCountRows(categoryName) {
    try {
        ClickByName(categoryName, 4000)
        Sleep(1500)
        DismissPopups()
        rowCount := CountLayawayListRows()
        if (rowCount >= 0) {
            LogMessage("      [click-count] '" . categoryName . "' -> " . rowCount)
            return rowCount
        }
        LogMessage("      [click-count] '" . categoryName . "' -> rows undetectable, falling back to badge read")
    } catch as e {
        LogMessage("      [click-count] '" . categoryName . "' click failed: " . e.Message . " - falling back to badge read")
    }
    return ReadBadgeCount(categoryName)
}

; Count rendered rows in the Layaways list. Tries DevExpress DataItem first
; (the same pattern used in Loans75DaysPastDue.ahk's CountListViewRows), then
; TreeViewItem with an AutomationId containing "Row". Returns -1 if neither
; pattern matches so the caller can fall back to a badge read.
CountLayawayListRows() {
    try {
        root := GetBravoRoot()
        elems := 0
        try elems := root.FindElements({Type: "DataItem"})
        if (elems && elems.Length > 0)
            return elems.Length
    }
    try {
        root := GetBravoRoot()
        elems := root.FindElements({Type: "TreeViewItem"})
        count := 0
        for e in elems {
            autoId := ""
            try autoId := e.AutomationId
            if (autoId != "" && InStr(autoId, "Row"))
                count++
        }
        if (count > 0)
            return count
    }
    return -1
}

; Read the count from a Bravo "badge" — a Button/RadioButton with the label
; Name and 1-2 Text descendants (one for the label, an optional one for the
; count). If only the label Text exists, count is 0 (no badge bubble shown).
;
; Per uia-discover dump of the Layaways view:
;   [radio button] Name='Layaways Overdue'
;     [text] Name='Layaways Overdue'
;     [text] Name='3'                    <-- the count badge
;   [radio button] Name='All Active'     <-- no count Text means 0
;     [text] Name='All Active'
ReadBadgeCount(badgeLabel) {
    return ReadLabeledCount(badgeLabel)
}

; Shared helper used by ReadBadgeCount AND ParseCountFromTitle (for the
; Loans/Buys saved-report title bar pattern).
; Strategy:
;   1. Walk all elements with Name = labelName.
;   2. For each, look at its descendant Text elements.
;   3. Find the Text whose Name is purely numeric (e.g. "3", "12", "73").
;   4. Return that number; return 0 if no numeric descendant found.
ReadLabeledCount(labelName) {
    try {
        root := GetBravoRoot()
        ; Find candidate parents whose Name matches the label.
        ; The badge is typically a RadioButton or Button; the count is in a
        ; Text child. Walk both types.
        for typeName in ["RadioButton", "Button", "Text"] {
            elems := 0
            try elems := root.FindElements({Type: typeName})
            if !elems
                continue
            for e in elems {
                n := ""
                try n := e.Name
                if (n != labelName)
                    continue
                ; Found a candidate; look for a numeric Text descendant.
                count := ExtractNumericTextChild(e)
                if (count >= 0)
                    return count
            }
        }
    } catch as e {
        LogMessage("    WARN ReadLabeledCount('" . labelName . "'): " . e.Message)
    }
    return 0
}

; Look at the descendants of `parent` for a Text element whose Name is purely
; numeric. Returns the number, or -1 if none found.
ExtractNumericTextChild(parent) {
    try {
        texts := parent.FindElements({Type: "Text"})
        for t in texts {
            n := ""
            try n := t.Name
            if (n = "")
                continue
            ; Skip the label-text (we want the OTHER text — the count).
            if RegExMatch(n, "^\d+$") {
                return Integer(n)
            }
        }
    }
    return -1
}
