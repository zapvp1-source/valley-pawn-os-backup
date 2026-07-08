#Requires AutoHotkey v2.0
#SingleInstance Force
; ============================================================================
; _test_fake_clickonce.ahk  (TEST HARNESS — added 2026-06-22)
; Pops a window that mimics the real Bravo ClickOnce trust prompt: same title
; ("Application Install - Security Warning") and BOTH buttons ("Install" and
; "Don't Install"). Used to PROVE bravo_foreground_keeper.ahk auto-clicks the
; correct button unattended. Writes the outcome to logs/_test_fake_clickonce.log
; and self-destructs after 120s if nothing clicks it. Purely a test; touches
; nothing in the pipeline.
; ============================================================================
logf := A_ScriptDir "\logs\_test_fake_clickonce.log"
Log(m) {
    global logf
    try FileAppend(FormatTime(A_Now, "yyyy-MM-dd HH:mm:ss") " | " m "`n", logf)
}

Log("TEST dialog opening (title='Application Install - Security Warning')")

g := Gui("+AlwaysOnTop", "Application Install - Security Warning")
g.AddText("w340", "Do you want to install this application?  (TEST HARNESS — not real Bravo)")
bInstall := g.AddButton("x40 y70 w130", "Install")
bDont    := g.AddButton("x190 y70 w130", "Don't Install")
bInstall.OnEvent("Click", OnInstall)
bDont.OnEvent("Click", OnDont)
g.Show("w380 h130")

SetTimer(Timeout, -120000)        ; give up after 120s

OnInstall(*) {
    Log("RESULT: PASS — 'Install' button was clicked by the keeper (unattended self-heal works)")
    ExitApp
}
OnDont(*) {
    Log("RESULT: FAIL — 'Don't Install' was clicked instead of 'Install'")
    ExitApp
}
Timeout() {
    Log("RESULT: FAIL — keeper did NOT click within 120s (no self-heal)")
    ExitApp
}
