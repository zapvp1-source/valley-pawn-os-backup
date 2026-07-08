; ============================================================================
; island/source/Loans75_gridread_island.ahk
;
; ISLAND PoC — Step A (grid-read mechanism check, list-view report).
; Proves we can read FULL ROWS off Bravo's on-screen Ad Hoc list grid via UIA,
; WITHOUT opening Bravo's Export Document dialog (the export step is the hang
; trigger; this script never touches it).
;
; ISOLATION:
;   - Includes prod libs READ-ONLY (Bravo Data Extraction/lib). Edits nothing.
;   - Targets the CURRENTLY-ACTIVE store only — NO store switching, NO password,
;     so zero account-lockout risk.
;   - Writes ONLY to island/output/. Never to prod output.
;   - Renders "75 Days Past Due" and reads the grid. No export. No CS toggle.
;
; Output: island/output/<date>_<STORE>_loans75-gridread.csv  (header + one row per grid row)
; Plus a discovery dump in island/output/loans75-gridread.log so we can see the
; exact row/cell UIA structure even if v1 harvest needs refining.
; ============================================================================

#Requires AutoHotkey v2.0
#SingleInstance Force

global CONFIG := Map()
global SCRIPT_DIR := A_ScriptDir

; Run our logic in the auto-execute section FIRST, then ExitApp — BEFORE the
; #Include directives below. An included library's top-level code or hotkey
; definition would otherwise end the auto-execute thread before our Main()
; ever runs (the "task runs but no heartbeat" symptom, 2026-06-17). Functions
; from the includes still resolve at load time regardless of textual order.
Main()
ExitApp()

#Include Y:\Documents\Claude\Projects\Bravo Data Extraction\lib\Json.ahk
#Include Y:\Documents\Claude\Projects\Bravo Data Extraction\lib\Bravo.ahk
#Include Y:\Documents\Claude\Projects\Bravo Data Extraction\lib\StoreCycle.ahk

Main() {
    global CONFIG, SCRIPT_DIR
    ; TEMP DIAGNOSTIC — write heartbeat via BOTH Y: and UNC so we can tell which
    ; drive surface AHK can actually write to in the scheduled-task session.
    try FileAppend(FormatTime(, "HH:mm:ss") . " HB-UNC`r`n", "\\Mac\Home\Documents\Claude\Projects\Bravo Pipeline\island\output\island_heartbeat_unc.txt")
    ; Heartbeat FIRST — absolute path, no dependency on InitLog. Proves the
    ; script actually executed even if later steps fail.
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") . " island AHK STARTED; A_ScriptDir=" . A_ScriptDir . "`r`n", "Y:\Documents\Claude\Projects\Bravo Pipeline\island\output\island_heartbeat.txt", "UTF-8")
    ; ABSOLUTE path — a relative "..\output" silently fails FileAppend on the
    ; mapped Y: drive (LogMessage swallows the error), which produced the
    ; "script runs but no log/CSV" symptom on the 2026-06-17 first runs.
    outputDir := "Y:\Documents\Claude\Projects\Bravo Pipeline\island\output"
    if !DirExist(outputDir)
        DirCreate(outputDir)
    CONFIG["paths.output"] := outputDir
    CONFIG["paths.logs"]   := outputDir

    InitLog(outputDir, "loans75-gridread")
    LogMessage("=== ISLAND Loans75 grid-read PoC starting ===")

    if !WaitForBravoReady(30) {
        LogMessage("FATAL: Bravo not ready within 30s")
        return
    }
    ActivateBravo()
    DismissPopups()

    store := "UNK"
    try store := GetCurrentStoreCode()
    LogMessage("current store (no switching): " . store)

    today := FormatTime(A_Now, "yyyy-MM-dd")
    outputPath := outputDir . "\" . today . "_" . store . "_loans75-gridread.csv"
    LogMessage("output -> " . outputPath)

    try {
        if !BackToDashboard()
            LogMessage("WARN: BackToDashboard imperfect; continuing")
        Sleep(500)
        DismissPopups()

        LogMessage("step 1: open Loans/Buys")
        ClickByName("Loans/Buys", 8000)
        Sleep(1500)
        DismissPopups()

        LogMessage("step 2: open Custom Reports")
        ClickByName("Custom Reports", 6000)
        Sleep(1500)

        LogMessage("step 3: choose saved report '75 Days Past Due'")
        try ClickByName("Choose Saved Report", 4000)
        Sleep(700)
        try ClickByName("75 Days Past Due", 4000)
        Sleep(700)

        LogMessage("step 4: Ok")
        ClickByName("Ok", 5000)
        Sleep(3500)
        DismissPopups()

        ; ---- DISCOVERY: dump the grid structure ----
        root := GetBravoRoot()
        rows := []
        try rows := root.FindElements({Type: "DataItem"})
        rowCount := (rows) ? rows.Length : 0
        LogMessage("DataItem rows found: " . rowCount)

        if (rowCount = 0) {
            LogMessage("0 DataItem rows — dumping type counts + visible names for inspection")
            try DumpAllUiaTypeCounts()
            try LogVisibleNames(60)
        }

        ; Dump the cell structure of the first row so we KNOW the cell layout
        if (rowCount >= 1) {
            first := rows[1]
            for ctype in ["Text", "Edit", "Custom", "DataItem", "Group"] {
                try {
                    kids := first.FindElements({Type: ctype})
                    if (kids && kids.Length > 0) {
                        LogMessage("  row[1] child type=" . ctype . " count=" . kids.Length)
                        shown := 0
                        for k in kids {
                            if (shown >= 25)
                                break
                            nm := "", vl := ""
                            try nm := k.Name
                            try vl := k.Value
                            LogMessage("     cell[" . ctype . "] name='" . nm . "' value='" . vl . "'")
                            shown += 1
                        }
                    }
                }
            }
        }

        ; ---- HARVEST: write CSV, one line per row, cells from Text children ----
        ResetOutputFile(outputPath)
        FileAppend("store,date,row_index,cells`r`n", outputPath, "UTF-8-RAW")
        written := 0
        idx := 0
        for row in rows {
            idx += 1
            cellsTxt := HarvestRowCells(row)
            FileAppend(ToCsvField(store) . "," . ToCsvField(today) . "," . idx . "," . ToCsvField(cellsTxt) . "`r`n", outputPath, "UTF-8-RAW")
            written += 1
            if (written <= 3)
                LogMessage("  harvested row " . idx . ": " . cellsTxt)
        }
        LogMessage("rows written to CSV: " . written)

        ; ---- clean exit, no export ever opened ----
        try ClickByName("Cancel", 3000)
        Sleep(700)
        try ClickByName("Cancel", 3000)
        Sleep(700)
        try BackToDashboard()
        LogMessage("=== DONE. rows=" . rowCount . " written=" . written . " ===")

    } catch as e {
        LogMessage("ERROR: " . e.Message)
        try ScreenshotToFile("loans75-gridread-error")
        try BackToDashboard()
    }
}

; Read all cell text from one grid row, joined with " | ".
HarvestRowCells(row) {
    parts := []
    for ctype in ["Text", "Edit"] {
        try {
            kids := row.FindElements({Type: ctype})
            for k in kids {
                v := ""
                try v := k.Name
                if (v = "") {
                    try v := k.Value
                }
                if (v != "")
                    parts.Push(v)
            }
        }
    }
    out := ""
    for p in parts {
        out := (out = "") ? p : out . " | " . p
    }
    return out
}
