; ============================================================================
; reports/ForfeitureWinback.ahk   (ADDITIVE — 2026-09-29)
;
; Two cells for the Forfeited-Loan Win-Back program
; (master doc: Projects/Email Refinement/15_forfeited_winback_consolidated.md)
;
;   forfeiture-winback             Loans/Buys -> Custom Reports ->
;                                  saved "Claude Forfeiture Winback"
;   forfeiture-winback-comparison  Customers  -> Custom Reports ->
;                                  saved "Claude Forfeiture Winback Comparison"
;
; Both saved reports were built by Joshua/Preston 2026-09-29, shared.
; The Comparison report carries a date criterion that must be updated each
; run; the trigger "date" field drives it:
;   "saved"                     -> run with the saved criteria unchanged
;   "YYYY-MM-DD"                -> set date editor position 1 only
;   "YYYY-MM-DD..YYYY-MM-DD"    -> set positions 1 and 2
; Every run LOGS the date-editor values it found before and after override,
; so the saved criteria are visible in the log (ground truth, Rule 12).
;
; Reuses proven helpers already included by the watcher:
;   IntakeSelectSavedReportCommitted / IntakeGetLoadedReportName /
;   IntakeClickOkVerified / WriteIntakeDetailGrid (IntakeDetail.ahk),
;   SetReportDate (EmployeeActivity.ahk), EnsureStore, BackToDashboard.
; Exits via named "Cancel" x2, never "Done" (KNOWN_ISSUES).
; NOTHING existing is modified.
; ============================================================================
#Requires AutoHotkey v2.0

PullForfeitureWinback(store, dateOrRange, outputDir) {
    return FwbRun(store, dateOrRange, outputDir, "Loans/Buys", "Claude Forfeiture Winback", "forfeiture-winback")
}

PullForfeitureWinbackComparison(store, dateOrRange, outputDir) {
    return FwbRun(store, dateOrRange, outputDir, "Customers", "Claude Forfeiture Winback Comparison", "forfeiture-winback-comparison")
}

FwbRun(store, dateOrRange, outputDir, sidebar, reportName, slug) {
    started := A_TickCount
    result := Map(
        "report",      slug,
        "store",       store,
        "date",        dateOrRange,
        "status",      "error",
        "output_path", "",
        "row_count",   0,
        "duration_ms", 0,
        "error",       ""
    )

    startDate := ""
    endDate := ""
    ; dateOrRange = "<date|saved>[|rows=N][|layout=<exact column-layout label>][|tag=<x>]"
    dr := ""
    wantRows := ""
    wantLayout := ""
    tag := ""
    stampOverride := ""
    rest := dateOrRange
    ; the layout label itself may contain " | " (e.g. "SHARED GLOBALLY | Customer Address Check"),
    ; so cut it out of the string BEFORE splitting the remaining options on "|"
    if RegExMatch(rest, "i)\|?\s*layout=(SHARED [A-Z-]+ \| [^|]+|[^|]+)", &ml) {
        wantLayout := Trim(ml[1])
        rest := StrReplace(rest, ml[0], "")
    }
    for part in StrSplit(rest, "|") {
        part := Trim(part)
        if RegExMatch(part, "i)^rows=(\d+)$", &mr)
            wantRows := mr[1]
        else if RegExMatch(part, "i)^tag=([A-Za-z0-9_-]+)$", &mt)
            tag := mt[1]
        else if RegExMatch(part, "i)^stamp=(\d{4}-\d{2}-\d{2})$", &ms)
            stampOverride := ms[1]
        else if (part != "" && dr = "")
            dr := part
    }
    if (dr = "")
        dr := "saved"
    if (tag != "")
        slug := slug . "-" . tag
    if (dr != "" && dr != "saved") {
        if InStr(dr, "..") {
            parts := StrSplit(dr, "..")
            if (parts.Length != 2)
                return Fail(result, started, "Malformed date range: " . dr)
            startDate := Trim(parts[1])
            endDate := Trim(parts[2])
        } else {
            startDate := dr
        }
    }
    stamp := (endDate != "") ? endDate : ((startDate != "") ? startDate : FormatTime(, "yyyy-MM-dd"))
    if (stampOverride != "")
        stamp := stampOverride
    outputPath := outputDir . "\" . OutputFilename(stamp, store, slug)
    LogMessage("[" . store . "] " . slug . " date=" . dr . " -> " . outputPath)

    if !WaitForIntakeBravoWin(30)
        return Fail(result, started, "Bravo window not found within 30s")
    ActivateBravo()
    DismissPopups()

    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)

    ResetOutputFile(outputPath)
    try FileDelete(outputPath . ".meta")
    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    try {
        LogMessage("  step 1: open " . sidebar)
        ClickByName(sidebar, 8000)
        Sleep(1500)
        DismissPopups()
        LogMessage("  step 2: click Custom Reports")
        ClickByName("Custom Reports", 5000)
        Sleep(2000)

        ; --- resolve the real saved name (exact-case match is load-bearing) --
        realName := FwbResolveSavedName(reportName)
        if (realName = "") {
            LogMessage("    [resolve] not seen in list scan - falling back to the exact name and the proven selector")
            realName := reportName
        }
        if (realName != reportName)
            LogMessage("    [resolve] using actual saved name '" . realName . "'")
        reportName := realName

        ; --- select + verify EXACT name (the two reports share a prefix) ----
        selected := false
        Loop 3 {
            LogMessage("  step 3: select '" . reportName . "' (attempt " . A_Index . ")")
            IntakeSelectSavedReportCommitted("Choose Saved Report", reportName)
            Sleep(1500)
            loaded := Trim(IntakeGetLoadedReportName())
            LogMessage("    [saved-report] BoxReportName='" . loaded . "'")
            if (loaded = reportName) {
                selected := true
                break
            }
            if (loaded = "") {
                ; BoxReportName is sometimes blank even on success (IntakeDetail
                ; note). Accept, and let the logged columns prove it.
                LogMessage("    [saved-report] name box blank — proceeding, columns will be logged")
                selected := true
                break
            }
            Sleep(800)
        }
        if (!selected)
            throw Error("Could not commit '" . reportName . "' after 3 attempts")

        ; layout first: setting dates/rows before it made the list un-openable (9/29)
        if (wantLayout != "") {
            if FwbPickComboItem("BoxColumns", wantLayout)
                LogMessage("    [layout] applied '" . wantLayout . "' (this run only)")
            else
                throw Error("column layout '" . wantLayout . "' not found")
            Sleep(800)
        }
        FwbDumpCriteria()
        FwbLogDateEdits("before override")
        if (startDate != "") {
            LogMessage("  step 4: set date pos1=" . startDate)
            try {
                SetReportDate(1, startDate)
            } catch as e {
                LogMessage("    WARN SetReportDate(1): " . e.Message)
            }
        }
        if (endDate != "") {
            LogMessage("  step 4b: set date pos2=" . endDate)
            try {
                SetReportDate(2, endDate)
            } catch as e {
                LogMessage("    WARN SetReportDate(2): " . e.Message)
            }
        }
        if (startDate != "" || endDate != "")
            FwbLogDateEdits("after override")
        if (wantRows != "")
            FwbSetMaxRows(wantRows)
        Sleep(800)

        LogMessage("  step 5: Ok (verified)")
        IntakeClickOkVerified()
        if !FindByName("Layouts", 60000)
            throw Error("List did not render within 60s (no Layouts caret)")
        Sleep(5000)

        anyRows := false
        Loop 60 {
            try {
                root := GetBravoRoot()
                items := root.FindElements({Type: "DataItem"})
                anyRows := (items && items.Length > 0)
            }
            if (anyRows)
                break
            Sleep(1000)
        }
        try {
            root := GetBravoRoot()
            tes := root.FindElements({Type: "Edit"})
            tcount := 0
            for te in tes {
                tn := ""
                try tn := te.Name
                if (tn = "TextEdit")
                    tcount++
            }
            LogMessage("    [grid] DataItems present=" . (anyRows ? "yes" : "no") . " TextEdit cells=" . tcount)
        }
        if (!anyRows) {
            LogMessage("    [grid] report surface present, zero rows")
            result["row_count"] := 0
            try FileDelete(outputPath)
            FileAppend("(empty)`r`n", outputPath, "UTF-8-RAW")
            FileAppend("expected=0`r`ncaptured=0`r`n", outputPath . ".meta", "UTF-8-RAW")
        } else {
            LogMessage("  step 6: walk grid -> CSV")
            n := FwbWriteGrid(outputPath)
            if (n < 0) {
                LogVisibleNames()
                throw Error("grid walk captured nothing")
            }
            result["row_count"] := n
            LogMessage("    wrote " . n . " rows")
        }

        try ClickByName("Cancel", 3000)
        Sleep(800)
        try ClickByName("Cancel", 3000)
        Sleep(800)
    } catch as e {
        LogVisibleNames()
        try ClickByName("Cancel", 2000)
        Sleep(500)
        try ClickByName("Cancel", 2000)
        Sleep(500)
        try BackToDashboard()
        return Fail(result, started, slug . " failed: " . e.Message)
    }

    result["output_path"] := outputPath
    result["status"]      := "success"
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: " . result["row_count"] . " rows, " . result["duration_ms"] . "ms")
    return result
}

; Log every BravoDateEdit's current value, left-to-right, plus nearby labels.
FwbLogDateEdits(tag) {
    try {
        root := GetBravoRoot()
        edits := root.FindElements({Type: "Edit"})
        out := ""
        for e in edits {
            n := ""
            try n := e.Name
            if (n != "BravoDateEdit")
                continue
            aid := ""
            try aid := e.AutomationId
            if (aid = "PART_Editor")
                continue
            v := ""
            try {
                inner := e.FindElement({Type: "Edit"})
                if inner
                    v := inner.Value
            }
            x := ""
            try x := e.BoundingRectangle.l
            out .= " [x=" . x . " v=" . v . "]"
        }
        LogMessage("    [dates " . tag . "]" . (out = "" ? " (no BravoDateEdit found)" : out))
    } catch as ex {
        LogMessage("    [dates " . tag . "] read failed: " . ex.Message)
    }
}

; ----------------------------------------------------------------------------
; Open the saved-report dropdown and find the entry whose name matches the
; wanted report ignoring case/extra spaces/quote marks. Logs every entry that
; mentions "forfeit" or "Claude" so a naming mismatch is visible in the log.
; Returns the exact on-screen name, or "" if not found. Leaves the dropdown
; closed (re-clicks the combo).
; ----------------------------------------------------------------------------
FwbNorm(s) {
    s := StrLower(s)
    s := RegExReplace(s, "[\x{201C}\x{201D}\x{2018}\x{2019}`"']", "")
    s := RegExReplace(s, "\s+", " ")
    return Trim(s)
}

FwbResolveSavedName(wanted) {
    want := FwbNorm(wanted)
    combo := FindSavedReportCombo()
    if !combo
        return wanted
    CoordMode("Mouse", "Screen")
    ActivateBravo()
    try combo.Click("left")
    Sleep(900)
    crect := 0
    try crect := combo.BoundingRectangle
    seen := Map()
    found := ""
    anyItems := 0
    Loop 70 {
        ; after a store switch the first click sometimes does not open the list:
        ; if nothing list-like has rendered after a few polls, re-open it
        if (A_Index = 4 || A_Index = 12 || A_Index = 24) && (anyItems = 0) {
            LogMessage("    [resolve] dropdown looks closed - re-opening (poll " . A_Index . ")")
            try combo.Click("left")
            Sleep(900)
            if (A_Index = 24) {
                try combo.Focus()
                Send("!{Down}")
                Sleep(900)
            }
        }
        try {
            root := GetBravoRoot()
            for typ in ["ListItem", "Text", "DataItem"] {
                els := 0
                try els := root.FindElements({Type: typ})
                if !els
                    continue
                for el in els {
                    nm := ""
                    try nm := el.Name
                    if (typ = "ListItem" && nm != "")
                        anyItems++
                    if (nm = "" || seen.Has(nm))
                        continue
                    if RegExMatch(nm, "i)forfeit|claude") {
                        seen[nm] := 1
                        LogMessage("    [resolve] list entry: '" . nm . "'")
                    }
                    if (FwbNorm(nm) = want) {
                        found := nm
                        break
                    }
                }
                if (found != "")
                    break
            }
        }
        if (found != "")
            break
        if crect {
            MouseMove((crect.l + crect.r) // 2, crect.t - 120, 0)
            Send("{WheelDown}")
        }
        Sleep(200)
    }
    ; close the dropdown without touching the dialog
    try combo.Click("left")
    Sleep(700)
    LogMessage("    [resolve] wanted='" . wanted . "' found='" . found . "'")
    return found
}

; ----------------------------------------------------------------------------
; Full-capture grid walker. Same row/column harvesting as
; WriteIntakeDetailGrid (IntakeDetail.ahk, untouched) but the scroll step is
; sized from the visible row count so no rows are skipped on long lists
; (the fixed 18% step captured only 121 of 1000 rows on the 9/29 smoke).
; A final sweep re-visits any row indexes still missing.
; ----------------------------------------------------------------------------
FwbHarvest(allRows, columnAutoIds, columnLabels, &totalRows) {
    newRows := 0
    visible := 0
    items := 0
    try {
        root := GetBravoRoot()
        items := root.FindElements({Type: "DataItem"})
    }
    if (!items)
        return [0, 0]
    for di in items {
        kids := 0
        try kids := di.FindElements({Scope: 2})
        if (!kids || kids.Length = 0)
            continue
        visible++
        rowIdx := -1
        for k in kids {
            kn := ""
            try kn := k.Name
            if RegExMatch(kn, "Row (\d+) of (\d+)", &m) {
                rowIdx := Integer(m[1])
                if (Integer(m[2]) > totalRows)
                    totalRows := Integer(m[2])
                break
            }
        }
        if (rowIdx < 0 || allRows.Has(rowIdx))
            continue
        rowMap := Map()
        for k in kids {
            ka := ""
            kn := ""
            try ka := k.AutomationId
            try kn := k.Name
            if (ka = "")
                continue
            if (!columnLabels.Has(ka)) {
                columnAutoIds.Push(ka)
                lbl := ka
                if RegExMatch(kn, "Column ([^,]+), Column \d+ of \d+", &mc)
                    lbl := mc[1]
                columnLabels[ka] := lbl
            }
            v := kn
            cp := InStr(kn, ": ", false, -1)
            if (cp > 0)
                v := SubStr(kn, cp + 2)
            rowMap[ka] := v
        }
        allRows[rowIdx] := rowMap
        newRows++
    }
    return [newRows, visible]
}

FwbWriteGrid(outputPath) {
    allRows := Map()
    columnAutoIds := []
    columnLabels := Map()
    totalRows := -1
    scrollContainer := 0
    try {
        root := GetBravoRoot()
        probe := root.FindElement({Type: "DataItem"})
        if probe {
            try probe.Click("left")
            Sleep(200)
            anc := probe
            Loop 10 {
                anc := anc.Parent
                if !anc
                    break
                if anc.IsScrollPatternAvailable {
                    scrollContainer := anc
                    break
                }
            }
        }
    }
    LogMessage("    [fwb-grid] scroll container: " . (scrollContainer ? "ScrollPattern" : "none - keyboard"))

    res := FwbHarvest(allRows, columnAutoIds, columnLabels, &totalRows)
    visible := res[2]
    if (totalRows <= 0 || visible <= 0) {
        LogMessage("    [fwb-grid] nothing harvested on first pass")
        return -1
    }
    step := (visible * 0.5 / totalRows) * 100
    if (step < 0.1)
        step := 0.1
    if (step > 25)
        step := 25
    LogMessage("    [fwb-grid] total=" . totalRows . " visible=" . visible . " step=" . Round(step, 3) . "%")

    pct := 0
    passes := 0
    while (allRows.Count < totalRows && passes < 3000) {
        passes++
        if scrollContainer {
            pct := pct + step
            if (pct > 100)
                pct := 100
            try scrollContainer.ScrollPattern.SetScrollPercent(pct, -1)
            Sleep(350)
        } else {
            Send("{PgDn}")
            Sleep(450)
        }
        FwbHarvest(allRows, columnAutoIds, columnLabels, &totalRows)
        if (Mod(passes, 20) = 0)
            LogMessage("    [fwb-grid] pass " . passes . " pct=" . Round(pct, 1) . " seen=" . allRows.Count . "/" . totalRows)
        if (pct >= 100 && passes > 5) {
            ; one settle re-read at the bottom, then stop
            Sleep(600)
            FwbHarvest(allRows, columnAutoIds, columnLabels, &totalRows)
            break
        }
    }
    ; targeted fill: jump straight to each missing row's position (a few tries each)
    if (allRows.Count < totalRows && scrollContainer) {
        LogMessage("    [fwb-grid] targeted fill for " . (totalRows - allRows.Count) . " missing rows")
        Loop totalRows {
            mi := A_Index
            if allRows.Has(mi)
                continue
            for off in [0.5, 0.3, 0.7] {
                tp := ((mi - visible * off) / totalRows) * 100
                if (tp < 0)
                    tp := 0
                if (tp > 100)
                    tp := 100
                try scrollContainer.ScrollPattern.SetScrollPercent(tp, -1)
                Sleep(450)
                FwbHarvest(allRows, columnAutoIds, columnLabels, &totalRows)
                if allRows.Has(mi)
                    break
            }
        }
    }
    if (allRows.Count < totalRows && scrollContainer) {
        for tp in [0, 0.5, 1, 99, 99.5, 100] {
            try scrollContainer.ScrollPattern.SetScrollPercent(tp, -1)
            Sleep(700)
            FwbHarvest(allRows, columnAutoIds, columnLabels, &totalRows)
        }
    }
    if (allRows.Count < totalRows) {
        miss := ""
        mc := 0
        Loop totalRows {
            if !allRows.Has(A_Index) {
                mc++
                if (mc <= 25)
                    miss .= A_Index . " "
            }
        }
        LogMessage("    [fwb-grid] missing row idx: " . miss)
    }
    LogMessage("    [fwb-grid] captured " . allRows.Count . "/" . totalRows . " after " . passes . " passes")
    if (allRows.Count < totalRows)
        LogMessage("    WARN [fwb-grid] INCOMPLETE capture: missing " . (totalRows - allRows.Count) . " rows")

    headerLine := ""
    for i, ka in columnAutoIds
        headerLine .= (i > 1 ? "," : "") . ToCsvField(columnLabels[ka])
    FileAppend(headerLine . "`r`n", outputPath, "UTF-8-RAW")
    LogMessage("    [fwb-grid] header: " . headerLine)
    idx := 0
    written := 0
    Loop totalRows {
        idx := A_Index
        if !allRows.Has(idx)
            continue
        r := allRows[idx]
        line := ""
        for i, ka in columnAutoIds
            line .= (i > 1 ? "," : "") . ToCsvField(r.Has(ka) ? r[ka] : "")
        FileAppend(line . "`r`n", outputPath, "UTF-8-RAW")
        written++
    }
    ; expected-vs-captured sidecar so downstream can refuse partial data
    try FileDelete(outputPath . ".meta")
    FileAppend("expected=" . totalRows . "`r`ncaptured=" . written . "`r`n", outputPath . ".meta", "UTF-8-RAW")
    return written
}

; Log the loaded report's criteria surface (every Edit value + Text label),
; so what the saved report actually filters on is on record in the log.
FwbDumpCriteria() {
    try {
        root := GetBravoRoot()
        out := ""
        cnt := 0
        for typ in ["Edit", "Text", "ComboBox", "CheckBox"] {
            els := 0
            try els := root.FindElements({Type: typ})
            if !els
                continue
            for el in els {
                nm := "", aid := "", v := ""
                try nm := el.Name
                try aid := el.AutomationId
                try v := el.Value
                if (typ = "CheckBox") {
                    try v := el.TogglePattern.CurrentToggleState
                }
                if (nm = "" && v = "")
                    continue
                y := ""
                try y := el.BoundingRectangle.t
                LogMessage("    [criteria] " . typ . " y=" . y . " name='" . nm . "' aid='" . aid . "' value='" . v . "'")
                cnt++
                if (cnt > 120)
                    return
            }
        }
    } catch as ex {
        LogMessage("    [criteria] dump failed: " . ex.Message)
    }
}

; Raise the "Initial rows"/"Max rows" cap for THIS RUN ONLY (the saved report
; is never re-saved). Finds the numeric BravoComboBox on the same row as the
; label, sets it, verifies, logs. Failure is logged, never fatal.
FwbSetMaxRows(target) {
    try {
        root := GetBravoRoot()
        labY := -1
        for t in root.FindElements({Type: "Text"}) {
            tn := ""
            try tn := t.Name
            if (tn = "Initial rows" || tn = "Max rows") {
                try labY := t.BoundingRectangle.t
                break
            }
        }
        if (labY < 0) {
            LogMessage("    [rows] no Initial/Max rows label found")
            return
        }
        for e in root.FindElements({Type: "Edit"}) {
            en := "", ev := "", ey := -9999
            try en := e.Name
            try ev := e.Value
            try ey := e.BoundingRectangle.t
            if (en != "BravoComboBox" || !RegExMatch(ev, "^\d+$") || Abs(ey - labY) > 25)
                continue
            LogMessage("    [rows] cap currently " . ev . " -> trying " . target)
            try e.Value := target
            Sleep(400)
            nv := ""
            try nv := e.Value
            if (nv != target) {
                try e.Click("left")
                Sleep(300)
                Send("^a")
                Sleep(100)
                SendText(target)
                Sleep(200)
                Send("{Tab}")
                Sleep(400)
                try nv := e.Value
            }
            LogMessage("    [rows] cap now '" . nv . "'")
            return
        }
        LogMessage("    [rows] numeric cap combo not found near label")
    } catch as ex {
        LogMessage("    [rows] failed: " . ex.Message)
    }
}

; ============================================================================
; forfeiture-winback-discover  (READ-ONLY diagnostic, 2026-09-29)
; Opens each generator with our saved report loaded and LOGS every field the
; criteria picker and the column-layout picker offer, plus the dialog's
; buttons. Saves nothing, runs nothing, Cancels out. Purpose: find customer
; id / phone / email / last-time-in / SMS fields for an exact audience.
; ============================================================================
PullForfeitureWinbackDiscover(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map("report", "forfeiture-winback-discover", "store", store, "date", dateOrRange,
        "status", "error", "output_path", "", "row_count", 0, "duration_ms", 0, "error", "")
    if !WaitForIntakeBravoWin(30)
        return Fail(result, started, "Bravo window not found")
    ActivateBravo()
    DismissPopups()
    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed")
    outPath := outputDir . "\" . FormatTime(, "yyyy-MM-dd") . "_" . store . "_fwb-discover.txt"
    try FileDelete(outPath)
    total := 0
    for pair in [["Loans/Buys", "Claude Forfeiture Winback"], ["Customers", "Claude Forfeiture Winback Comparison"]] {
        sidebar := pair[1], rep := pair[2]
        try {
            BackToDashboard()
            Sleep(800)
            DismissPopups()
            ClickByName(sidebar, 8000)
            Sleep(1500)
            DismissPopups()
            ClickByName("Custom Reports", 5000)
            Sleep(2000)
            IntakeSelectSavedReportCommitted("Choose Saved Report", rep)
            Sleep(1500)
            FileAppend("=== " . sidebar . " / " . rep . " loaded='" . IntakeGetLoadedReportName() . "'`r`n", outPath, "UTF-8-RAW")
            for aid in ["BoxSelectCriteria", "BoxColumns"] {
                names := FwbDumpComboItems(aid)
                FileAppend("--- " . aid . " (" . names.Length . " items)`r`n", outPath, "UTF-8-RAW")
                for n in names
                    FileAppend(n . "`r`n", outPath, "UTF-8-RAW")
                total += names.Length
            }
            ; every button / text label in the dialog
            FileAppend("--- dialog labels`r`n", outPath, "UTF-8-RAW")
            root := GetBravoRoot()
            for typ in ["Button", "Text", "CheckBox"] {
                for el in root.FindElements({Type: typ}) {
                    nm := ""
                    try nm := el.Name
                    if (nm != "")
                        FileAppend(typ . ": " . nm . "`r`n", outPath, "UTF-8-RAW")
                }
            }
        } catch as e {
            FileAppend("ERROR " . e.Message . "`r`n", outPath, "UTF-8-RAW")
        }
        try ClickByName("Cancel", 3000)
        Sleep(800)
        try ClickByName("Cancel", 3000)
        Sleep(800)
    }
    try BackToDashboard()
    result["output_path"] := outPath
    result["row_count"] := total
    result["status"] := "success"
    result["duration_ms"] := A_TickCount - started
    return result
}

; Open a BravoComboBox by AutomationId, collect every list entry name while
; wheeling down, close it again. Returns array of names.
FwbDumpComboItems(aid) {
    out := []
    seen := Map()
    combo := 0
    try {
        root := GetBravoRoot()
        combo := root.FindElement({AutomationId: aid})
    }
    if !combo
        return out
    before := Map()
    try {
        root := GetBravoRoot()
        for el in root.FindElements({Type: "ListItem"}) {
            nm := ""
            try nm := el.Name
            before[nm] := 1
        }
    }
    CoordMode("Mouse", "Screen")
    try combo.Click("left")
    Sleep(1200)
    r := 0
    try r := combo.BoundingRectangle
    stable := 0
    Loop 80 {
        added := 0
        try {
            root := GetBravoRoot()
            for typ in ["ListItem", "DataItem", "TreeItem"] {
                els := 0
                try els := root.FindElements({Type: typ})
                if !els
                    continue
                for el in els {
                    nm := ""
                    try nm := el.Name
                    ; list entries report a class name; the visible label lives in child Text
                    lbl := ""
                    try {
                        for t in el.FindElements({Type: "Text"}) {
                            tn := ""
                            try tn := t.Name
                            if (tn != "")
                                lbl .= (lbl = "" ? "" : " | ") . tn
                        }
                    }
                    key := (lbl != "") ? lbl : nm
                    if (key = "" || seen.Has(key) || (lbl = "" && before.Has(nm)))
                        continue
                    seen[key] := 1
                    out.Push(key)
                    added++
                }
            }
        }
        stable := added ? 0 : stable + 1
        if (stable >= 6)
            break
        if r {
            MouseMove((r.l + r.r) // 2, r.b + 150, 0)
            Send("{WheelDown}")
        }
        Sleep(250)
    }
    Send("{Escape}")
    Sleep(600)
    return out
}

; ============================================================================
; forfeiture-winback-layouts  (READ-ONLY diagnostic, 2026-09-29)
; For each saved COLUMN LAYOUT offered in the Loans and Customers generators,
; run our saved report with that layout applied (this run only, never saved)
; and log the grid's column headers. Finds which layout carries customer id /
; phone / SMS / last-time-in. Customers runs use Last Time In > yesterday to
; stay small. Output: <date>_<STORE>_fwb-layouts.txt
; ============================================================================
PullForfeitureWinbackLayouts(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map("report", "forfeiture-winback-layouts", "store", store, "date", dateOrRange,
        "status", "error", "output_path", "", "row_count", 0, "duration_ms", 0, "error", "")
    if !WaitForIntakeBravoWin(30)
        return Fail(result, started, "Bravo window not found")
    ActivateBravo()
    DismissPopups()
    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed")
    outPath := outputDir . "\" . FormatTime(, "yyyy-MM-dd") . "_" . store . "_fwb-layouts.txt"
    try FileDelete(outPath)
    yday := FormatTime(DateAdd(A_Now, -1, "Days"), "yyyy-MM-dd")
    done := 0
    for pair in [["Customers", "Claude Forfeiture Winback Comparison"], ["Loans/Buys", "Claude Forfeiture Winback"]] {
        sidebar := pair[1], rep := pair[2]
        labels := []
        FwbOpenReport(sidebar, rep)
        labels := FwbDumpComboItems("BoxColumns")
        FileAppend("=== " . sidebar . " layouts: " . labels.Length . "`r`n", outPath, "UTF-8-RAW")
        try ClickByName("Cancel", 3000)
        Sleep(800)
        for lbl in labels {
            try {
                FwbOpenReport(sidebar, rep)
                if !FwbPickComboItem("BoxColumns", lbl) {
                    FileAppend("[" . lbl . "] could not select`r`n", outPath, "UTF-8-RAW")
                } else {
                    if (sidebar = "Customers")
                        try SetReportDate(1, yday)
                    Sleep(600)
                    IntakeClickOkVerified()
                    if FindByName("Layouts", 60000) {
                        Sleep(3000)
                        FileAppend("[" . lbl . "] " . FwbHeaderLine() . "`r`n", outPath, "UTF-8-RAW")
                        done++
                    } else {
                        FileAppend("[" . lbl . "] grid did not render`r`n", outPath, "UTF-8-RAW")
                    }
                }
            } catch as e {
                FileAppend("[" . lbl . "] ERROR " . e.Message . "`r`n", outPath, "UTF-8-RAW")
            }
            try ClickByName("Cancel", 3000)
            Sleep(800)
            try ClickByName("Cancel", 3000)
            Sleep(800)
        }
    }
    try BackToDashboard()
    result["output_path"] := outPath
    result["row_count"] := done
    result["status"] := "success"
    result["duration_ms"] := A_TickCount - started
    return result
}

FwbOpenReport(sidebar, rep) {
    BackToDashboard()
    Sleep(700)
    DismissPopups()
    ClickByName(sidebar, 8000)
    Sleep(1500)
    DismissPopups()
    ClickByName("Custom Reports", 5000)
    Sleep(2000)
    IntakeSelectSavedReportCommitted("Choose Saved Report", rep)
    Sleep(1500)
}

; Open combo (by AutomationId) and real-click the entry whose child-text label = want.
FwbPickComboItem(aid, want) {
    combo := 0
    try combo := GetBravoRoot().FindElement({AutomationId: aid})
    if !combo
        return false
    CoordMode("Mouse", "Screen")
    try combo.Click("left")
    Sleep(1200)
    r := 0
    try r := combo.BoundingRectangle
    Loop 60 {
        try {
            for el in GetBravoRoot().FindElements({Type: "ListItem"}) {
                lbl := ""
                try {
                    for t in el.FindElements({Type: "Text"}) {
                        tn := ""
                        try tn := t.Name
                        if (tn != "")
                            lbl .= (lbl = "" ? "" : " | ") . tn
                    }
                }
                if (lbl != want)
                    continue
                try el.ScrollIntoView()
                Sleep(300)
                er := el.BoundingRectangle
                if (er.b > er.t && er.t > 0) {
                    MouseMove((er.l + er.r) // 2, (er.t + er.b) // 2, 5)
                    Sleep(150)
                    Click((er.l + er.r) // 2, (er.t + er.b) // 2)
                    Sleep(1200)
                    return true
                }
            }
        }
        if r {
            MouseMove((r.l + r.r) // 2, r.b + 150, 0)
            Send("{WheelDown}")
        }
        Sleep(250)
    }
    Send("{Escape}")
    return false
}

; Column headers of the rendered grid: DataItem child column labels (first row)
; plus header PART_Content texts on the top-most row.
FwbHeaderLine() {
    cols := ""
    try {
        di := GetBravoRoot().FindElement({Type: "DataItem"})
        if di {
            for k in di.FindElements({Scope: 2}) {
                kn := "", ka := ""
                try kn := k.Name
                try ka := k.AutomationId
                lb := ka
                if RegExMatch(kn, "Column ([^,]+), Column \d+ of \d+", &m)
                    lb := m[1]
                cols .= lb . " [" . ka . "]; "
            }
        }
    }
    hdr := ""
    try {
        minY := 99999
        items := []
        for t in GetBravoRoot().FindElements({Type: "Text", AutomationId: "PART_Content"}) {
            y := 0, n := ""
            try y := t.BoundingRectangle.t
            try n := t.Name
            if (n = "")
                continue
            items.Push([y, n])
            if (y < minY)
                minY := y
        }
        for it in items
            if (Abs(it[1] - minY) <= 6)
                hdr .= it[2] . "; "
    }
    return "ROWCOLS: " . cols . " || HEADER: " . hdr
}
