#!/usr/bin/env python3
"""Patch 2 for IntakeDetail.ahk: verify the saved report actually loaded.

On LEX the ClickByName('Claude Pawn Walks') reported success but the dialog
kept the previously loaded report definition (wrong columns, no date filter),
producing a garbage 250-row export. Verify BoxReportName after selection and
retry once; throw only on a confirmed mismatch (soft-pass if unreadable so
working stores are never broken by the check).
"""
import sys

PATH = "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/reports/IntakeDetail.ahk"
src = open(PATH, encoding="utf-8").read()

old = (
    '        SelectSavedReport(INTAKE_ELEMENTS["saved_report_combo"], INTAKE_ELEMENTS["saved_report_value"])\n'
    '        Sleep(1000)\n'
)
new = (
    '        SelectSavedReport(INTAKE_ELEMENTS["saved_report_combo"], INTAKE_ELEMENTS["saved_report_value"])\n'
    '        Sleep(1000)\n'
    '\n'
    '        ; 2026-06-12: verify the report actually loaded. On LEX the item\n'
    '        ; click can silently fail to commit, leaving the previous report\n'
    '        ; definition loaded (wrong columns, no date filter). Soft check:\n'
    '        ; only throw on a confirmed non-empty mismatch after one retry.\n'
    '        loadedName := IntakeGetLoadedReportName()\n'
    '        LogMessage("    [saved-report] BoxReportName=" . Chr(39) . loadedName . Chr(39))\n'
    '        if (loadedName != "" && !InStr(loadedName, INTAKE_ELEMENTS["saved_report_value"])) {\n'
    '            LogMessage("    WARN: wrong report loaded - retrying selection")\n'
    '            SelectSavedReport(INTAKE_ELEMENTS["saved_report_combo"], INTAKE_ELEMENTS["saved_report_value"])\n'
    '            Sleep(1200)\n'
    '            loadedName := IntakeGetLoadedReportName()\n'
    '            LogMessage("    [saved-report] BoxReportName=" . Chr(39) . loadedName . Chr(39) . " after retry")\n'
    '            if (loadedName != "" && !InStr(loadedName, INTAKE_ELEMENTS["saved_report_value"]))\n'
    '                throw Error("Saved report did not load (BoxReportName=" . Chr(39) . loadedName . Chr(39) . ")")\n'
    '        }\n'
)
if old not in src:
    sys.exit("FAIL: select block not found")
src = src.replace(old, new, 1)

helper = '''

; Read the Custom Reports dialog's report-name box (AutoId=BoxReportName).
; Returns "" if not found / unreadable.
IntakeGetLoadedReportName() {
    try {
        root := GetBravoRoot()
        el := root.FindElement({AutomationId: "BoxReportName"})
        if el {
            v := ""
            try v := el.Value
            return v
        }
    }
    return ""
}
'''
src = src.rstrip("\n") + "\n" + helper
open(PATH, "w", encoding="utf-8", newline="").write(src)
print("PATCH2 OK")
