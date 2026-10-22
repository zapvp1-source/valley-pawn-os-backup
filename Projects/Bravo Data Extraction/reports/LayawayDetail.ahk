; ============================================================================
; reports/LayawayDetail.ahk   (ADDITIVE, 2026-10-21, v5)
;
; Full, row-level layaway list for ONE store. Built because reports/Layaways.ahk
; counts only the grid rows Bravo has rendered on screen (virtualized), so any
; list longer than ~22 rows was reported as 22.
;
; How (v5): the grid's own copy — select a row, Ctrl+A, Ctrl+C — returns EVERY
; row as tab-separated text regardless of virtualization (proven 10/21 HAR:
; 161 rows). Two grids are copied:
;   1. Layaways > All Active             -> <date>_<STORE>_layaway-detail-all-active.tsv
;   2. Layaways > Custom Reports, Active Layaways ticked, Max rows 2000, run
;                                         -> <date>_<STORE>_layaway-detail-custom.tsv
; Each .tsv gets a .meta (expected = grid "Row X of N" total, captured = lines).
; Earlier versions (grid harvest, detail-panel walks) kept as .v1/.v2/.v3 files.
;
; Cell: layaway-detail      date: YYYY-MM-DD (stamp only)
; READ-ONLY: never Save / Expire / Process. Custom report is run, not saved.
; Exits via Cancel. Nothing existing is modified.
; ============================================================================
#Requires AutoHotkey v2.0

PullLayawayDetail(store, dateOrRange, outputDir) {
    started := A_TickCount
    result := Map("report", "layaway-detail", "store", store, "date", dateOrRange,
        "status", "error", "output_path", "", "row_count", 0, "duration_ms", 0, "error", "")
    stamp := Trim(StrSplit(dateOrRange, "..")[1])
    if !RegExMatch(stamp, "^\d{4}-\d{2}-\d{2}$")
        stamp := FormatTime(, "yyyy-MM-dd")
    LogMessage("[" . store . "] layaway-detail v5 stamp=" . stamp)

    if !WaitForIntakeBravoWin(30)
        return Fail(result, started, "Bravo window not found within 30s")
    ActivateBravo()
    DismissPopups()
    global CONFIG
    password := CONFIG.Has("bravo.password") ? CONFIG["bravo.password"] : ""
    if !EnsureStore(store, password)
        return Fail(result, started, "EnsureStore failed for " . store)
    LogMessage("  store confirmed: " . store)
    if !BackToDashboard()
        return Fail(result, started, "BackToDashboard could not return Bravo to Dashboard")
    Sleep(500)
    DismissPopups()

    activePath := outputDir . "\" . stamp . "_" . store . "_layaway-detail-all-active.tsv"
    customPath := outputDir . "\" . stamp . "_" . store . "_layaway-detail-custom.tsv"
    nActive := 0, nCustom := 0
    try {
        LogMessage("  step 1: open Layaways view")
        ClickByName("Layaways", 8000)
        Sleep(3000)
        DismissPopups()
        ClickByName("All Active", 5000)
        Sleep(4000)
        DismissPopups()
        if (LdWaitRows(20) > 0)
            nActive := LdClipDump(activePath)
        LogMessage("  all-active captured=" . nActive)
        if (nActive > 0) {
            panelPath := outputDir . "\" . stamp . "_" . store . "_layaway-detail-panel.csv"
            LdDownWalk(panelPath, activePath, nActive)
        }

        LogMessage("  step 2: Custom Reports (Active Layaways, run without saving)")
        ClickByName("Custom Reports", 5000)
        Sleep(3000)
        FwbDumpCriteria()
        LdEnsureChecked("Active Layaways")
        FwbSetMaxRows("2000")
        Sleep(800)
        IntakeClickOkVerified()
        if !FindByName("Layouts", 60000)
            throw Error("custom grid did not render within 60s")
        Sleep(4000)
        if (LdWaitRows(30) > 0)
            nCustom := LdClipDump(customPath)
        LogMessage("  custom captured=" . nCustom)
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
        if (nActive > 0) {
            result["status"] := "success"
            result["row_count"] := nActive
            result["output_path"] := activePath
            result["error"] := "custom step failed: " . e.Message
            result["duration_ms"] := A_TickCount - started
            LogMessage("  PARTIAL: all-active ok (" . nActive . "), custom failed: " . e.Message)
            return result
        }
        return Fail(result, started, "layaway-detail failed: " . e.Message)
    }
    try BackToDashboard()
    result["status"] := "success"
    result["row_count"] := nActive
    result["output_path"] := activePath
    result["duration_ms"] := A_TickCount - started
    LogMessage("  SUCCESS: all-active=" . nActive . " custom=" . nCustom . " " . result["duration_ms"] . "ms")
    return result
}

LdWaitRows(seconds) {
    Loop seconds * 2 {
        try {
            root := GetBravoRoot()
            items := root.FindElements({Type: "DataItem"})
            if (items && items.Length > 0)
                return items.Length
        }
        Sleep(500)
    }
    return 0
}

; Grid "Row X of N" total from any rendered DataItem.
LdGridTotal() {
    total := 0
    try {
        root := GetBravoRoot()
        for di in root.FindElements({Type: "DataItem"}) {
            for k in di.FindElements({Scope: 2}) {
                kn := ""
                try kn := k.Name
                if RegExMatch(kn, "Row \d+ of (\d+)", &m) {
                    if (Integer(m[1]) > total)
                        total := Integer(m[1])
                    break
                }
            }
            if (total > 0)
                break
        }
    }
    return total
}

LdEnsureChecked(label) {
    try {
        root := GetBravoRoot()
        for cb in root.FindElements({Type: "CheckBox"}) {
            nm := ""
            try nm := cb.Name
            if (nm != label)
                continue
            st := -1
            try st := cb.TogglePattern.CurrentToggleState
            LogMessage("    [check] '" . label . "' state=" . st)
            if (st = 0) {
                try cb.TogglePattern.Toggle()
                Sleep(500)
                try st := cb.TogglePattern.CurrentToggleState
                LogMessage("    [check] '" . label . "' now=" . st)
            }
            return
        }
        LogMessage("    [check] '" . label . "' checkbox not found")
    } catch as ex {
        LogMessage("    [check] failed: " . ex.Message)
    }
}

; Select the first visible row by a real click, Ctrl+A, Ctrl+C; save the
; clipboard text. Returns data lines captured (header excluded).
LdClipDump(path) {
    try FileDelete(path)
    try FileDelete(path . ".meta")
    expected := LdGridTotal()
    lines := 0
    try {
        root := GetBravoRoot()
        first := root.FindElement({Type: "DataItem"})
        r := first.BoundingRectangle
        CoordMode("Mouse", "Screen")
        Click(r.l + 60, r.t + (r.b - r.t) // 2)
        Sleep(800)
        prev := ""
        try prev := A_Clipboard
        A_Clipboard := ""
        Send("^a")
        Sleep(1000)
        Send("^c")
        if ClipWait(8) {
            txt := A_Clipboard
            FileAppend(txt, path, "UTF-8-RAW")
            for ln in StrSplit(Trim(txt, "`r`n"), "`n")
                lines++
            lines := lines - 1
        } else {
            LogMessage("    [clip] clipboard stayed empty")
        }
        try A_Clipboard := prev
        Click(r.l + 60, r.t + (r.b - r.t) // 2)
        Sleep(600)
    } catch as e {
        LogMessage("    [clip] error " . e.Message)
    }
    FileAppend("expected=" . expected . "`r`ncaptured=" . lines . "`r`n", path . ".meta", "UTF-8-RAW")
    LogMessage("    [clip] " . path . " expected=" . expected . " captured=" . lines)
    return lines
}

; Balance lives only in the detail panel. The All Active grid repeats a row
; per unit for quantity items (HAR 10/21: one coin layaway = 85 rows), which
; is what stalled earlier walks. Walk {Down} through EVERY row (row count from
; the copied grid) and record each new Layaway Number's panel.
LdDownWalk(panelPath, tsvPath, rows) {
    try FileDelete(panelPath)
    try FileDelete(panelPath . ".meta")
    want := Map()
    try {
        for ln in StrSplit(FileRead(tsvPath, "UTF-8"), "`n") {
            f := StrSplit(ln, "`t")
            if (f.Length > 1 && f[1] != "Layaway Number")
                want[Trim(f[1], " `r")] := 1
        }
    }
    target := want.Count
    FileAppend("idx,layaway,texts`r`n", panelPath, "UTF-8-RAW")
    seen := Map()
    got := 0
    try {
        root := GetBravoRoot()
        first := root.FindElement({Type: "DataItem"})
        r := first.BoundingRectangle
        CoordMode("Mouse", "Screen")
        Click(r.l + 60, r.t + (r.b - r.t) // 2)
        Sleep(1200)
    }
    Loop rows + 5 {
        snap := LdPanelSnapshot()
        num := RegExMatch(snap, "Layaway Number:@[^|]*\|([^@|]+)@", &mk) ? mk[1] : ""
        if (num != "" && !seen.Has(num)) {
            seen[num] := 1
            got++
            FileAppend(got . "," . num . "," . ToCsvField(snap) . "`r`n", panelPath, "UTF-8-RAW")
            if (got >= target)
                break
        }
        Send("{Down}")
        Sleep(650)
    }
    LogMessage("    [panel] distinct captured " . got . "/" . target . " over " . rows . " rows")
    FileAppend("expected=" . target . "`r`ncaptured=" . got . "`r`n", panelPath . ".meta", "UTF-8-RAW")
    return got
}

LdPanelSnapshot() {
    out := ""
    try {
        root := GetBravoRoot()
        texts := root.FindElements({Type: "Text"})
        anchor := 0
        for t in texts {
            nm := ""
            try nm := t.Name
            if (nm = "Layaway Number:") {
                anchor := t.BoundingRectangle
                break
            }
        }
        if !anchor
            return "(no panel)"
        for t in texts {
            nm := ""
            try nm := t.Name
            if (nm = "")
                continue
            r := 0
            try r := t.BoundingRectangle
            if !r
                continue
            if (r.l < anchor.l - 15 || r.l > anchor.l + 1400 || r.t < anchor.t - 8 || r.t > anchor.t + 1300)
                continue
            out .= (out = "" ? "" : "|") . StrReplace(nm, "|", "/") . "@" . r.l . ":" . r.t
        }
    }
    return out
}
