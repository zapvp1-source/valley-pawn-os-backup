; ============================================================================
; seed_ssrs_auth.ahk — one-shot helper to complete the SSRS Forms login in Edge
;
; Run this AFTER ck-test-e (or any company-kpis trigger) has launched Edge to
; the SSRS report URL and Edge is sitting on the logon.aspx page. This script
; activates that Edge window and sends Enter to submit the Forms login (which
; uses the pre-filled reportuser/empty-password + "Click to Continue" button).
;
; After it succeeds, Edge has .ASPXAUTH cookies in its profile and subsequent
; runs of the CompanyKpis pipeline cell will download CSV directly without
; further interaction (until the cookies expire, which is typically days).
; ============================================================================
#Requires AutoHotkey v2.0

; Find any Edge window titled with SSRS
edgeHwnd := 0
for hwnd in WinGetList("ahk_exe msedge.exe") {
    try {
        t := WinGetTitle("ahk_id " . hwnd)
        if (InStr(t, "SQL Server Reporting Services") || InStr(t, "BRAVO Company Performance") || InStr(t, "Reporting Services")) {
            edgeHwnd := hwnd
            break
        }
    }
}

if !edgeHwnd {
    MsgBox("No Edge window with SSRS title found.")
    ExitApp(1)
}

WinActivate("ahk_id " . edgeHwnd)
WinWaitActive("ahk_id " . edgeHwnd, , 5)
Sleep(800)

; The SSRS Forms login page has the "Click to Continue" button as the default
; submit on the form. Pressing Enter while the form has focus triggers it.
; Click into the page body first to make sure focus is on the document, then
; Tab to land on the button, then Enter.
Send("{F6}")    ; focus the page (away from address bar)
Sleep(400)
Send("{Tab}")   ; first interactive element — usually the user field
Sleep(200)
Send("{Tab}")   ; next — password field
Sleep(200)
Send("{Tab}")   ; next — Click to Continue button
Sleep(200)
Send("{Enter}")
Sleep(500)

ExitApp(0)
