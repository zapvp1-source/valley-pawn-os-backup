; ============================================================================
; probe_edge.ahk — Launch Edge with the SSRS CSV URL, observe the page state,
; dump diagnostic info to a log so we can see what's happening from outside.
; ============================================================================
#Requires AutoHotkey v2.0
#Include lib\UIA-v2\UIA.ahk

global LOG_PATH := A_ScriptDir . "\logs\probe_edge.log"
global CSV_URL := "https://ssrs.bravoapplication.com:9176/ReportServer/?/Bravo/BRAVO%20Company%20Performance&rs:Command=Render&rs:Format=CSV&rc:parameters=false&StartDate=2026/5/1&EndDate=2026/5/22&IsPawnOn=True"

WriteLog(msg) {
    line := FormatTime(, "yyyy-MM-dd HH:mm:ss") . " " . msg . "`r`n"
    try FileAppend(line, LOG_PATH, "UTF-8")
}

WriteLog("=== probe_edge starting ===")

; Step 1: launch Edge with URL
launchCmd := 'cmd /c start "" "' . CSV_URL . '"'
WriteLog("launching: " . launchCmd)
Run(launchCmd, , "Hide")

; Step 2: wait for any Edge window to appear
WriteLog("waiting up to 30s for Edge window")
edgeHwnd := 0
deadline := A_TickCount + 30000
loop {
    for hwnd in WinGetList("ahk_exe msedge.exe") {
        try {
            t := WinGetTitle("ahk_id " . hwnd)
            if (t != "") {
                edgeHwnd := hwnd
                WriteLog("found Edge window hwnd=" . hwnd . " title='" . t . "'")
                break 2
            }
        }
    }
    if (A_TickCount > deadline) {
        WriteLog("TIMEOUT: no Edge window with a title appeared")
        ExitApp(1)
    }
    Sleep(500)
}

; Step 3: watch the title for 30s to see how it evolves
WriteLog("watching title evolution for 30s")
lastTitle := ""
endWatch := A_TickCount + 30000
loop {
    try {
        t := WinGetTitle("ahk_id " . edgeHwnd)
    } catch {
        t := "<WINDOW_GONE>"
    }
    if (t != lastTitle) {
        WriteLog("  title=" . t)
        lastTitle := t
    }
    if (A_TickCount > endWatch)
        break
    Sleep(1000)
}

; Step 4: dump the UIA tree of the Edge window so we can see what controls exist
WriteLog("dumping Edge UIA tree (top-level named elements)")
try {
    root := UIA.ElementFromHandle(edgeHwnd)
    for typeName in ["Button", "Hyperlink", "Edit", "Document", "Text"] {
        try {
            elems := root.FindElements({Type: typeName})
            if (elems && elems.Length > 0) {
                WriteLog("  --- " . typeName . " (" . elems.Length . " total) ---")
                count := 0
                for elem in elems {
                    try {
                        n := elem.Name
                    } catch {
                        n := "<no-name>"
                    }
                    if (n != "" && StrLen(n) < 200) {
                        WriteLog("    " . typeName . ": '" . n . "'")
                        count++
                        if (count >= 30) {
                            WriteLog("    ...(truncated at 30)")
                            break
                        }
                    }
                }
            }
        }
    }
} catch as e {
    WriteLog("UIA dump failed: " . e.Message)
}

; Step 5: check Downloads to see if anything appeared
WriteLog("checking Downloads")
downloadsDir := "C:\Users\joshuadavis\Downloads"
loop files, downloadsDir . "\*", "F" {
    WriteLog("  download: " . A_LoopFileName . " (" . A_LoopFileSize . " bytes, mtime " . FormatTime(A_LoopFileTimeModified) . ")")
}

WriteLog("=== probe_edge done ===")
ExitApp(0)
