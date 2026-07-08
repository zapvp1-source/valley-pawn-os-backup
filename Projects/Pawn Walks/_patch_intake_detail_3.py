#!/usr/bin/env python3
"""Patch 3 for IntakeDetail.ahk: commit-verified saved-report selection.

Confirmed at LEX 2026-06-12 via one-off UIA test: plain ClickByName on the
saved-report list item does NOT commit on LEX (dropdown stays open, previous
report definition keeps running -> wrong columns, no date filter).
Double-click also fails; {Enter} after the click commits. Replace the bare
SelectSavedReport call with a wrapper that verifies the dropdown actually
closed ('<new report>' list item gone) and escalates click -> double-click
-> Enter.
"""
import sys

PATH = "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/reports/IntakeDetail.ahk"
src = open(PATH, encoding="utf-8").read()

old = '        SelectSavedReport(INTAKE_ELEMENTS["saved_report_combo"], INTAKE_ELEMENTS["saved_report_value"])\n'
new = '        IntakeSelectSavedReportCommitted(INTAKE_ELEMENTS["saved_report_combo"], INTAKE_ELEMENTS["saved_report_value"])\n'
if src.count(old) != 2:
    sys.exit("FAIL: expected 2 SelectSavedReport call sites, found %d" % src.count(old))
src = src.replace(old, new)

helper = '''

; 2026-06-12: commit-verified saved-report selection. On LEX, clicking the
; list item leaves the dropdown open and the selection uncommitted, so the
; previously loaded report definition silently runs instead. Detect an open
; dropdown via the '<new report>' list item and escalate:
; click -> double-click -> {Enter}.
IntakeSelectSavedReportCommitted(comboName, valueName) {
    SelectSavedReport(comboName, valueName)
    Sleep(700)
    if !ExistsByName("<new report>")
        return  ; dropdown closed - committed
    LogMessage("    [saved-report] dropdown still open after click - double-clicking")
    try DoubleClickByName(valueName, 2500)
    Sleep(900)
    if !ExistsByName("<new report>") {
        LogMessage("    [saved-report] committed via double-click")
        return
    }
    LogMessage("    [saved-report] still open - sending Enter")
    Send("{Enter}")
    Sleep(900)
    if !ExistsByName("<new report>") {
        LogMessage("    [saved-report] committed via Enter")
        return
    }
    throw Error("saved-report selection would not commit (dropdown still open)")
}
'''
src = src.rstrip("\n") + "\n" + helper
open(PATH, "w", encoding="utf-8", newline="").write(src)
print("PATCH3 OK")
