; ============================================================================
; bravo_export.ahk — one-shot manual report runner
;
; Use this to invoke a single report by hand (for testing / dev) without
; writing a trigger file. The output, result, and log all land in the same
; folders the watcher would use.
;
; Usage from the VM command line:
;   AutoHotkey64.exe bravo_export.ahk <report-name> <store> <date>
;
; Examples:
;   AutoHotkey64.exe bravo_export.ahk safe-register-journal CUL 2026-05-11
;   AutoHotkey64.exe bravo_export.ahk loans-75-days-past-due HAR 2026-05-12
;
; If you double-click the .ahk file (no args), a prompt asks for the three
; inputs interactively.
; ============================================================================

#Requires AutoHotkey v2.0
#SingleInstance Off

#Include lib\Json.ahk
#Include lib\Bravo.ahk
; lib\Bravo.ahk transitively includes lib\UIA-v2\UIA.ahk; no need to repeat here.
#Include lib\StoreCycle.ahk
#Include reports\SafeRegisterJournal.ahk
#Include reports\UIADiscover.ahk
#Include reports\AgedInventorySummary.ahk
#Include reports\EmployeeActivity.ahk
#Include reports\ChekkitInactives.ahk
#Include reports\ChekkitInactivesDiag.ahk
#Include reports\ChekkitInactivesV2.ahk
#Include reports\ChekkitInvites.ahk
#Include reports\Loans75DaysPastDue.ahk
#Include reports\Layaways.ahk
#Include reports\FpdCohort.ahk
#Include reports\SalesByVendor.ahk
#Include reports\CompanyKpis.ahk
#Include reports\LowDollarLoans.ahk
#Include reports\LowDollarBuys.ahk
#Include reports\VendorReceiving.ahk
#Include reports\LoanBase.ahk
#Include reports\ItemsToPrice.ahk
; Mirror the #Include list in bravo_watcher.ahk when new reports are added.

global CONFIG := Map()
global REPORT_HANDLERS := Map()

Main() {
    global CONFIG, REPORT_HANDLERS

    ; Slice 1: derive paths from A_ScriptDir. (JSON config parsing turned out
    ; to be flaky because of PowerShell stdout encoding; revisit in slice 2.)
    CONFIG["paths.project_root"] := A_ScriptDir
    CONFIG["paths.triggers"]     := A_ScriptDir . "\triggers"
    CONFIG["paths.output"]       := A_ScriptDir . "\output"
    CONFIG["paths.results"]      := A_ScriptDir . "\results"
    CONFIG["paths.logs"]         := A_ScriptDir . "\logs"
    CONFIG["bravo.username"]     := "FREE1@WAY"
    CONFIG["bravo.password"]     := "Health2035!"

    REPORT_HANDLERS["safe-register-journal"]    := PullSafeRegisterJournal
    REPORT_HANDLERS["uia-discover"]             := PullUiaDiscover
    REPORT_HANDLERS["aged-inventory-summary"]   := PullAgedInventorySummary
    REPORT_HANDLERS["employee-activity"]        := PullEmployeeActivity
    REPORT_HANDLERS["chekkit-inactives"]        := PullChekkitInactives
    REPORT_HANDLERS["chekkit-inactives-diag"]   := PullChekkitInactivesDiag
    REPORT_HANDLERS["chekkit-inactives-v2"]     := PullChekkitInactivesV2
    REPORT_HANDLERS["chekkit-invites"]         := PullChekkitInvites
    REPORT_HANDLERS["loans-75-days-past-due"]   := PullLoans75DaysPastDue
    REPORT_HANDLERS["layaways"]                 := PullLayaways
    REPORT_HANDLERS["fpd-cohort"]               := PullFpdCohort
    REPORT_HANDLERS["sales-by-vendor"]          := PullSalesByVendor
    REPORT_HANDLERS["company-kpis"]             := PullCompanyKpis
    REPORT_HANDLERS["low-dollar-loans"]         := PullLowDollarLoans
    REPORT_HANDLERS["low-dollar-buys"]          := PullLowDollarBuys
    REPORT_HANDLERS["vendor-receiving"]         := PullVendorReceivingFromSidecar
    REPORT_HANDLERS["loan-base"]                := PullLoanBase
    REPORT_HANDLERS["items-to-price"]           := PullItemsToPrice
    ; Add new registrations here.

    ; Parse args. AHK v2 exposes them in A_Args.
    reportName := store := date := ""
    if (A_Args.Length >= 3) {
        reportName := A_Args[1]
        store      := A_Args[2]
        date       := A_Args[3]
    } else {
        ; Interactive prompt
        reportName := InputBox("Report name (e.g. safe-register-journal)", "Bravo Export").Value
        if (reportName = "")
            ExitApp(1)
        store      := InputBox("Store code (CUL/HAR/LEX/ROA/WAY)", "Bravo Export").Value
        if (store = "")
            ExitApp(1)
        date       := InputBox("Date (YYYY-MM-DD)", "Bravo Export", , FormatTime(, "yyyy-MM-dd")).Value
        if (date = "")
            ExitApp(1)
    }

    triggerId := FormatTime(, "yyyy-MM-ddTHH-mm-ss") . "_manual_" . reportName . "_" . store
    InitLog(CONFIG["paths.logs"], triggerId)
    LogMessage("Manual run: " . reportName . " store=" . store . " date=" . date)

    handler := REPORT_HANDLERS.Get(reportName, "")
    if (handler = "") {
        msg := "Unknown report name: " . reportName
        LogMessage(msg)
        MsgBox(msg, "Bravo Export", "OK Icon!")
        ExitApp(2)
    }

    try {
        cell := handler.Call(store, date, CONFIG["paths.output"])
        result := Map(
            "trigger_id",  triggerId,
            "started_at",  FormatTime(, "yyyy-MM-ddTHH:mm:ss"),
            "finished_at", FormatTime(, "yyyy-MM-ddTHH:mm:ss"),
            "status",      cell.Get("status", "error"),
            "cells",       [cell],
            "errors",      []
        )
        resultPath := CONFIG["paths.results"] . "\" . triggerId . ".result.json"
        WriteResult(resultPath, result)
        LogMessage("Result written: " . resultPath)

        ; Show a final summary
        summary := "Report: " . reportName . "`nStore: " . store . "`nDate: " . date . "`n`n"
        summary .= "Status: " . cell.Get("status", "?") . "`n"
        if (cell.Get("status", "") = "success") {
            summary .= "Output: " . cell.Get("output_path", "") . "`n"
            summary .= "Rows: " . cell.Get("row_count", "0") . "`n"
        } else {
            summary .= "Error: " . cell.Get("error", "") . "`n"
        }
        summary .= "Duration: " . cell.Get("duration_ms", "?") . " ms"
        MsgBox(summary, "Bravo Export — Result", "OK")
    } catch as e {
        LogMessage("CRASH: " . e.Message)
        MsgBox("Crash: " . e.Message, "Bravo Export", "OK Icon!")
        ExitApp(3)
    }
}

Main()
