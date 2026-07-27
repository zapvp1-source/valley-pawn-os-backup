; ============================================================================
; bravo_watcher.ahk — persistent trigger poller
;
; Run this in the background on Windows login. It watches the triggers/
; folder; for every new <id>.json file, it parses the trigger, dispatches
; each (report × store) cell to the appropriate report module, and writes
; results/<id>.result.json plus logs/<id>.log.
;
; Trigger file lifecycle:
;   triggers/<id>.json           (Cowork drops here)
;   triggers/processed/<id>.json (we move it here after processing)
;
; Hotkeys:
;   Ctrl+Alt+W = exit watcher cleanly
;   Ctrl+Alt+R = force-run any pending triggers now (don't wait for next poll)
; ============================================================================

#Requires AutoHotkey v2.0
#SingleInstance Force
Persistent

#Include lib\Json.ahk
#Include lib\Bravo.ahk
#Include lib\EnsureDashboard.ahk
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
#Include reports\ChekkitGridOnly.ahk
#Include reports\ChekkitInvitesRange.ahk
#Include reports\Loans75DaysPastDue.ahk
#Include reports\Layaways.ahk
#Include reports\FpdCohort.ahk
#Include reports\FpdLookback12Mo.ahk
#Include reports\SalesByVendor.ahk
#Include reports\CompanyKpis.ahk
#Include reports\BuysFromPublic.ahk
#Include reports\IntakeDetail.ahk
#Include reports\ActiveInvDetails.ahk
#Include reports\SoldInvDetails.ahk
#Include reports\InventoryDetails.ahk
#Include reports\LowDollarLoans.ahk
#Include reports\LowDollarBuys.ahk
#Include reports\LoanReviews.ahk
#Include reports\LoanPortfolio2026.ahk
#Include reports\VendorReceiving.ahk
#Include reports\EndOfMonth.ahk
#Include reports\LoanBase.ahk
#Include reports\EndOfDayConsolidated.ahk
#Include reports\BravoBusinessDashboard.ahk
#Include reports\DepositsAndPaidOuts.ahk
#Include reports\DisbursementJournal.ahk
#Include reports\EndOfDay.ahk
#Include reports\GeneralException.ahk
#Include reports\InterStoreCashTransfer.ahk
#Include reports\LargeCashTransactions.ahk
#Include reports\Transfers.ahk
#Include reports\CostAdjustment.ahk
#Include reports\InventoryBase.ahk
#Include reports\InventoryByLocation.ahk
#Include reports\LostStolenOrDamaged.ahk
#Include reports\VendorPurchase.ahk
#Include reports\VendorRepairs.ahk
#Include reports\LoanDisposition.ahk
#Include reports\LoanHistory.ahk
#Include reports\LoanJournal.ahk
#Include reports\PawnActivitySummary.ahk
#Include reports\ATFADBook.ahk
#Include reports\ATFADCount.ahk
#Include reports\CreditBalance.ahk
#Include reports\CreditJournal.ahk
#Include reports\DigitalMarketingSettlement.ahk
#Include reports\LayawayBalance.ahk
#Include reports\LayawayDeposits.ahk
#Include reports\LayawayJournal.ahk
#Include reports\SalesAccounting.ahk
#Include reports\SoldInventory.ahk
#Include reports\WebSettlement.ahk
#Include reports\DropShipSettlement.ahk
#Include reports\RetailReportsDashboard.ahk
#Include reports\ItemsToPrice.ahk
#Include reports\NicsTransfers.ahk
#Include reports\Loans75GridRead.ahk
#Include reports\PostToAccountingGL.ahk
#Include reports\PostToAccountingPost.ahk
; Add #Include for each new report module here.

; ----- Globals ---------------------------------------------------------------

global CONFIG := Map()
global REPORT_HANDLERS := Map()
global SCRIPT_DIR := A_ScriptDir
global IS_PROCESSING := false  ; mutex so two timer ticks don't overlap

; ----- Boot ------------------------------------------------------------------

Main() {
    global CONFIG, REPORT_HANDLERS

    ; Slice 1: derive paths from SCRIPT_DIR. (JSON config parsing was flaky;
    ; revisit with a proper INI or fixed UTF-8 PS encoding in slice 2.)
    CONFIG["paths.project_root"]      := SCRIPT_DIR
    CONFIG["paths.triggers"]          := SCRIPT_DIR . "\triggers"
    CONFIG["paths.output"]            := SCRIPT_DIR . "\output"
    CONFIG["paths.results"]           := SCRIPT_DIR . "\results"
    CONFIG["paths.logs"]              := SCRIPT_DIR . "\logs"
    CONFIG["bravo.username"]          := "FREE1@WAY"
    CONFIG["bravo.password"]          := "Health2035!"
    CONFIG["watcher.poll_interval_ms"] := "30000"
    CONFIG["watcher.trigger_glob"]    := "*.json"

    ; Make sure target dirs exist
    for key in ["paths.triggers", "paths.output", "paths.results", "paths.logs"] {
        if CONFIG.Has(key) {
            dir := CONFIG[key]
            if !DirExist(dir)
                DirCreate(dir)
        }
    }
    processedDir := CONFIG["paths.triggers"] . "\processed"
    if !DirExist(processedDir)
        DirCreate(processedDir)

    ; Register report handlers — name (matching trigger JSON) -> function ref
    REPORT_HANDLERS["safe-register-journal"]    := PullSafeRegisterJournal
    REPORT_HANDLERS["uia-discover"]             := PullUiaDiscover
    REPORT_HANDLERS["aged-inventory-summary"]   := PullAgedInventorySummary
    REPORT_HANDLERS["employee-activity"]        := PullEmployeeActivity
    REPORT_HANDLERS["chekkit-inactives"]        := PullChekkitInactives
    REPORT_HANDLERS["chekkit-inactives-diag"]   := PullChekkitInactivesDiag
    REPORT_HANDLERS["chekkit-inactives-v2"]     := PullChekkitInactivesV2
    REPORT_HANDLERS["chekkit-invites"]         := PullChekkitInvites
    REPORT_HANDLERS["chekkit-gridonly"]       := PullChekkitGridOnly
    REPORT_HANDLERS["chekkit-invites-range"]  := PullChekkitInvitesRange
    REPORT_HANDLERS["loans-75-days-past-due"]   := PullLoans75DaysPastDue
    REPORT_HANDLERS["loans75-gridread"]         := PullLoans75GridRead
    REPORT_HANDLERS["layaways"]                 := PullLayaways
    REPORT_HANDLERS["fpd-cohort"]               := PullFpdCohort
    REPORT_HANDLERS["fpd-lookback-12mo"]        := PullFpdLookback12Mo
    REPORT_HANDLERS["sales-by-vendor"]          := PullSalesByVendor
    REPORT_HANDLERS["company-kpis"]             := PullCompanyKpis
    REPORT_HANDLERS["buys-from-public"]         := PullBuysFromPublic
    REPORT_HANDLERS["intake-detail"]           := PullIntakeDetail
    REPORT_HANDLERS["active-inv-details"]       := PullActiveInvDetails
    REPORT_HANDLERS["sold-inv-details"]         := PullSoldInvDetails
    REPORT_HANDLERS["inventory-details"]        := PullInventoryDetails
    REPORT_HANDLERS["low-dollar-loans"]         := PullLowDollarLoans
    REPORT_HANDLERS["low-dollar-buys"]          := PullLowDollarBuys
    REPORT_HANDLERS["loan-reviews"]            := PullLoanReviews
    REPORT_HANDLERS["loan-portfolio-2026"]    := PullLoanPortfolio2026
    ; Write-side: vendor-receiving uses the 3-arg watcher dispatch but reads
    ; its full payload from a sidecar JSON at
    ; triggers/payloads/<store>_<payloadKey>.payload.json. The trigger JSON's
    ; "date" field carries <payloadKey> (typically the vendor invoice number).
    ; See reports/VendorReceiving.ahk header comment for the payload schema.
    REPORT_HANDLERS["vendor-receiving"]        := PullVendorReceivingFromSidecar
    REPORT_HANDLERS["end-of-month"]            := PullEndOfMonth
    REPORT_HANDLERS["loan-base"]               := PullLoanBase
    REPORT_HANDLERS["end-of-day-consolidated"] := PullEndOfDayConsolidated
    REPORT_HANDLERS["bravo-business-dashboard"] := PullBravoBusinessDashboard
    REPORT_HANDLERS["deposits-paid-outs"]       := PullDepositsAndPaidOuts
    REPORT_HANDLERS["disbursement-journal"]     := PullDisbursementJournal
    REPORT_HANDLERS["end-of-day"]               := PullEndOfDay
    REPORT_HANDLERS["general-exception"]        := PullGeneralException
    REPORT_HANDLERS["inter-store-cash-transfer"] := PullInterStoreCashTransfer
    REPORT_HANDLERS["large-cash-transactions"]  := PullLargeCashTransactions
    REPORT_HANDLERS["transfers"]                := PullTransfers
    REPORT_HANDLERS["cost-adjustment"]              := PullCostAdjustment
    REPORT_HANDLERS["inventory-base"]               := PullInventoryBase
    REPORT_HANDLERS["inventory-by-location"]        := PullInventoryByLocation
    REPORT_HANDLERS["nics-transfers"]               := PullNicsTransfers
    REPORT_HANDLERS["lost-stolen-or-damaged"]       := PullLostStolenOrDamaged
    REPORT_HANDLERS["vendor-purchase"]              := PullVendorPurchase
    REPORT_HANDLERS["vendor-repairs"]               := PullVendorRepairs
    REPORT_HANDLERS["loan-disposition"]             := PullLoanDisposition
    REPORT_HANDLERS["loan-history"]                 := PullLoanHistory
    REPORT_HANDLERS["loan-journal"]                 := PullLoanJournal
    REPORT_HANDLERS["pawn-activity-summary"]        := PullPawnActivitySummary
    REPORT_HANDLERS["atf-ad-book"]                  := PullATFADBook
    REPORT_HANDLERS["atf-ad-count"]                 := PullATFADCount
    REPORT_HANDLERS["credit-balance"]               := PullCreditBalance
    REPORT_HANDLERS["credit-journal"]               := PullCreditJournal
    REPORT_HANDLERS["digital-marketing-settlement"] := PullDigitalMarketingSettlement
    REPORT_HANDLERS["layaway-balance"]              := PullLayawayBalance
    REPORT_HANDLERS["layaway-deposits"]             := PullLayawayDeposits
    REPORT_HANDLERS["layaway-journal"]              := PullLayawayJournal
    REPORT_HANDLERS["sales-accounting"]             := PullSalesAccounting
    REPORT_HANDLERS["sold-inventory"]               := PullSoldInventory
    REPORT_HANDLERS["web-settlement"]               := PullWebSettlement
    REPORT_HANDLERS["drop-ship-settlement"]         := PullDropShipSettlement
    REPORT_HANDLERS["retail-reports-dashboard"]     := PullRetailReportsDashboard
    REPORT_HANDLERS["items-to-price"]               := PullItemsToPrice
    REPORT_HANDLERS["post-to-accounting-gl"]        := PullPostToAccountingGL
    REPORT_HANDLERS["post-to-accounting-post"]      := PullPostToAccountingPost
    ; Add additional registrations here as we build out reports.

    pollMs := Integer(CONFIG.Get("watcher.poll_interval_ms", "30000"))
    SetTimer(PollTriggers, pollMs)
    PollTriggers()  ; run once immediately too

    ; Write a startup marker so we can confirm a fresh code load is running.
    ; This file is overwritten on every watcher boot.
    markerPath := SCRIPT_DIR . "\logs\watcher.last_started.txt"
    try {
        FileDelete(markerPath)
    }
    try {
        FileAppend(
            "Watcher started: " . FormatTime(, "yyyy-MM-dd HH:mm:ss") . "`r`n" .
            "Build tag: claim-fix-2026-05-13" . "`r`n" .
            "Handlers: " . HandlerListString() . "`r`n",
            markerPath, "UTF-8"
        )
    }

    TrayTip("Bravo Watcher started", "Polling " . CONFIG["paths.triggers"] . " every " . (pollMs / 1000) . "s", 1)
}

; Return a comma-separated list of registered handler names for the boot marker.
HandlerListString() {
    global REPORT_HANDLERS
    names := []
    for k, v in REPORT_HANDLERS
        names.Push(k)
    out := ""
    for i, n in names {
        if (i > 1)
            out .= ", "
        out .= n
    }
    return out
}

; ----- Polling ---------------------------------------------------------------

PollTriggers() {
    global IS_PROCESSING
    if IS_PROCESSING
        return  ; previous tick still running

    IS_PROCESSING := true
    try {
        triggersDir := CONFIG["paths.triggers"]
        glob := CONFIG.Get("watcher.trigger_glob", "*.json")
        files := []
        loop files, triggersDir . "\" . glob {
            files.Push(A_LoopFilePath)
        }
        ; Process oldest first
        files := SortByMTime(files)
        for f in files {
            ProcessTrigger(f)
        }
    } finally {
        IS_PROCESSING := false
    }
}

SortByMTime(arr) {
    pairs := []
    for f in arr {
        try {
            mtime := FileGetTime(f, "M")
            pairs.Push(Map("path", f, "mtime", mtime))
        }
    }
    ; Insertion sort by mtime ascending (small N, fine)
    n := pairs.Length
    i := 2
    while (i <= n) {
        j := i
        while (j > 1 && pairs[j]["mtime"] < pairs[j - 1]["mtime"]) {
            tmp := pairs[j]
            pairs[j] := pairs[j - 1]
            pairs[j - 1] := tmp
            j--
        }
        i++
    }
    out := []
    for p in pairs
        out.Push(p["path"])
    return out
}

; ----- Process one trigger ---------------------------------------------------

ProcessTrigger(triggerPath) {
    triggerId := ""
    claimedPath := ""

    ; --- Atomic filesystem claim (fix 2026-05-13) ------------------------
    ; The IS_PROCESSING boolean is best-effort: AHK v2 timer scheduling and
    ; long UIA waits inside ProcessTrigger can drop the flag prematurely
    ; (or let a queued tick re-enter PollTriggers and re-discover the same
    ; trigger file). Symptom: a single trigger gets run 3-4 times in a row,
    ; appearing on screen as Bravo "continually cycling" through every
    ; store's safe register journal. (See logs/daily-funds-verification-
    ; 2026-05-12T18-07-19.log line 836 — 4 Run-started markers on one
    ; trigger.)
    ;
    ; The real mutex is the filesystem. FileMove(src, dst, false) is atomic
    ; at the OS level. The first invocation wins the race; any concurrent
    ; invocation gets an exception (source vanished OR dest exists) and
    ; bails immediately.
    claimedDir := CONFIG["paths.triggers"] . "\claimed"
    if !DirExist(claimedDir)
        DirCreate(claimedDir)
    SplitPath(triggerPath, &triggerName)
    claimedPath := claimedDir . "\" . triggerName
    try {
        FileMove(triggerPath, claimedPath, false)
    } catch as e {
        ; Lost the race (another tick already claimed this trigger, or
        ; user/tooling moved/deleted the file). Nothing to do — return
        ; quietly so we don't spam the log.
        return
    }

    try {
        trigger := ReadTrigger(claimedPath)
        triggerId := trigger.Get("id", "")
        if (triggerId = "")
            triggerId := "untitled_" . A_TickCount

        InitLog(CONFIG["paths.logs"], triggerId)
        LogMessage("Trigger file: " . claimedPath . " (claimed from " . triggerPath . ")")
        LogMessage("Reports requested: " . trigger["reports"].Length)

        cells := []
        errors := []
        overallStatus := "success"

        ; --- Safety rails (added 2026-05-13) -------------------------------
        ; Two trip conditions short-circuit the rest of the run:
        ;   1) consecutiveAuthFailures >= MAX_CONSECUTIVE_AUTH_FAILURES
        ;      — protects against the lockout cascade where every store in
        ;        a row hits "EnsureStore failed" because Bravo can't accept
        ;        the watcher's credentials (wrong username pre-filled, wrong
        ;        password, account locked, etc.).
        ;   2) elapsed > MAX_TRIGGER_DURATION_MS
        ;      — protects against a single cell hanging inside a UIA call
        ;        for tens of minutes, wedging the whole run. The orchestrator
        ;        already has a hang-detection rule keyed on log mtime; this
        ;        is the in-watcher backstop.
        ; When tripped, remaining cells are written into the result.json as
        ; status="skipped" with an explanatory error string. The trigger is
        ; still moved to processed/ so the orchestrator sees a result and
        ; doesn't keep polling forever.
        MAX_CONSECUTIVE_AUTH_FAILURES := Integer(CONFIG.Get("watcher.max_consecutive_auth_failures", "3"))
        MAX_TRIGGER_DURATION_MS := Integer(CONFIG.Get("watcher.max_trigger_duration_ms", "2700000"))  ; 45 min
        consecutiveAuthFailures := 0
        tripped := false
        trippedReason := ""
        runStartTick := A_TickCount

        ; Determine a single target store for the gate (2026-06-22): if every
        ; report in this trigger targets the same one store, log DIRECTLY into
        ; it at the "Select a store" screen so we never need a store-SWITCH
        ; (the EOM preview-exit/BackToDashboard residual). Multi-store triggers
        ; keep the CUL default and switch per cell as before.
        gateStore := "CUL"
        try {
            _distinct := Map()
            for _rpt in trigger["reports"]
                for _st in _rpt["stores"]
                    _distinct[_st] := 1
            if (_distinct.Count = 1)
                for _st in _distinct
                    gateStore := _st
        }
        ; --- Readiness gate (root-cause fix 2026-06-22) -------------------
        ; Drive Bravo from any cold-start screen (store-select / session list /
        ; login form) to a logged-in dashboard BEFORE running any cells. Root
        ; cause of the chronic Monday failures: overnight Bravo sits on the
        ; "Select a store" screen, which no code handled, so every cell timed
        ; out. If we cannot reach a dashboard, abort the whole run cleanly
        ; instead of failing every cell against a stuck app. No Slack / DM.
        if !EnsureBravoDashboard(CONFIG.Get("bravo.password", ""), gateStore) {
            tripped := true
            trippedReason := "bravo-not-ready (could not reach a logged-in dashboard)"
            overallStatus := "aborted"
            LogMessage("  TRIPPED: " . trippedReason . " - skipping all cells")
        }
        
        for report in trigger["reports"] {
            reportName := report["name"]
            handler := REPORT_HANDLERS.Get(reportName, "")
            if (handler = "") {
                msg := "Unknown report name: " . reportName
                LogMessage("  " . msg)
                errors.Push(msg)
                overallStatus := "partial"
                continue
            }

            for store in report["stores"] {
                ; --- Pre-cell trip checks ----------------------------------
                if (!tripped && (A_TickCount - runStartTick) > MAX_TRIGGER_DURATION_MS) {
                    tripped := true
                    trippedReason := "hard-wall-timeout (>" . (MAX_TRIGGER_DURATION_MS // 1000) . "s elapsed)"
                    LogMessage("  TRIPPED: " . trippedReason . " - skipping remaining cells")
                }
                if (tripped) {
                    LogMessage("  SKIPPED " . reportName . "/" . store . " (" . trippedReason . ")")
                    cells.Push(Map(
                        "report",      reportName,
                        "store",       store,
                        "date",        report["date"],
                        "status",      "skipped",
                        "output_path", "",
                        "row_count",   0,
                        "duration_ms", 0,
                        "error",       "Skipped by safety rail: " . trippedReason
                    ))
                    overallStatus := "aborted"
                    continue
                }

                LogMessage("  Running " . reportName . " for " . store . " (date=" . report["date"] . ")")
                try {
                    cell := handler.Call(store, report["date"], CONFIG["paths.output"])
                    cells.Push(cell)
                    cellStatus := cell.Get("status", "")
                    cellError  := cell.Get("error", "")
                    if (cellStatus != "success")
                        overallStatus := "partial"
                    ; --- Auth-failure tracking --------------------------------
                    ; Increment the lockout counter only on REAL auth failures.
                    ; The global ENSURESTORE_LAST_CAUSE is set by EnsureStore /
                    ; SwitchStore in lib/StoreCycle.ahk and disambiguates between:
                    ;   "login"     -> real wrong-cred / recovery failure. Tick.
                    ;   "nav"       -> BackToDashboard couldn't reach Dashboard.
                    ;   "ready"     -> WaitForBravoReady timed out.
                    ;   "session"   -> Session List / Global Access fail.
                    ;   "store-row" -> couldn't find the target store row.
                    ; Only "login" counts toward the lockout breaker. The other
                    ; causes are logged but do NOT increment — they're navigation
                    ; bugs, not credential bugs, and shouldn't false-trip the
                    ; breaker (which used to skip ROA/WAY on any 3-cell cascade).
                    global ENSURESTORE_LAST_CAUSE
                    if (cellStatus = "error" && InStr(cellError, "EnsureStore failed") && ENSURESTORE_LAST_CAUSE = "login") {
                        consecutiveAuthFailures += 1
                        LogMessage("    consecutiveAuthFailures = " . consecutiveAuthFailures . "/" . MAX_CONSECUTIVE_AUTH_FAILURES . " (cause=login)")
                        if (consecutiveAuthFailures >= MAX_CONSECUTIVE_AUTH_FAILURES) {
                            tripped := true
                            trippedReason := "auth-failure circuit breaker (" . consecutiveAuthFailures . " consecutive login failures - possible lockout, stopping to prevent more bad logins)"
                            LogMessage("  TRIPPED: " . trippedReason)
                        }
                    } else if (cellStatus = "error" && InStr(cellError, "EnsureStore failed")) {
                        ; Non-login EnsureStore failure: log + continue, do NOT trip the breaker.
                        LogMessage("    EnsureStore failure cause=" . ENSURESTORE_LAST_CAUSE . " — NOT a lockout risk; breaker not incremented")
                    } else if (cellStatus = "success") {
                        ; Any clean success resets the auth-failure streak.
                        consecutiveAuthFailures := 0
                    }
                } catch as e {
                    msg := "Handler crashed for " . reportName . "/" . store . ": " . e.Message
                    LogMessage("    " . msg)
                    errors.Push(msg)
                    overallStatus := "partial"
                }

                ; --- Inter-cell cooldown (added 2026-05-28) -----------------
                ; Bravo's UI thread degrades when consecutive Previews are
                ; rendered without breathing room — diagnosed from the
                ; smoke-test-closing-batch-cul-2026-05-28-v3 failure where
                ; Bravo went "(Not Responding)" after cell 2. Yesterday's
                ; EOM × 5 stores worked because each store-cycle login added
                ; ~30s of natural pause; same-store sequential reports skipped
                ; that pause. This explicit 15s sleep restores the breathing
                ; room. Cost: ~15s per cell. For a typical overnight batch
                ; (41 cells), that's +10 minutes total — well within the
                ; overnight window. Don't sleep after the last cell.
                ; (Joshua, 2026-05-28: "typically Bravo does not hang like
                ; this when I drive it — is it the speed?" Yes.)
                LogMessage("    [pacing] cooldown 15s before next cell")
                Sleep(15000)
            }
        }

        ; Write result file
        resultPath := CONFIG["paths.results"] . "\" . triggerId . ".result.json"
        result := Map(
            "trigger_id",  triggerId,
            "started_at",  FormatTime(, "yyyy-MM-ddTHH:mm:ss"),
            "finished_at", FormatTime(, "yyyy-MM-ddTHH:mm:ss"),
            "status",      overallStatus,
            "cells",       cells,
            "errors",      errors
        )
        WriteResult(resultPath, result)
        LogMessage("Result written: " . resultPath)
        LogMessage("Overall status: " . overallStatus)

        ; Move trigger from claimed/ to processed/ (final state).
        processedPath := CONFIG["paths.triggers"] . "\processed\" . triggerId . ".json"
        try {
            FileMove(claimedPath, processedPath, true)
        } catch as e {
            LogMessage("WARNING: could not move trigger to processed/: " . e.Message)
        }

    } catch as e {
        ; Last-resort: write a crash result so Cowork sees something. Leave
        ; the trigger in claimed/ so an admin can see something blew up
        ; mid-run rather than silently moving it to processed/.
        crashPath := CONFIG["paths.results"] . "\" . (triggerId = "" ? "crash_" . A_TickCount : triggerId) . ".crash.json"
        try {
            FileAppend('{"status":"crash","error":"' . StrReplace(e.Message, '"', '\"') . '"}', crashPath, "UTF-8")
        }
    }
}

; ----- Hotkeys ---------------------------------------------------------------

^!w:: {
    TrayTip("Bravo Watcher exiting", "", 1)
    Sleep(500)
    ExitApp(0)
}

^!r:: {
    TrayTip("Bravo Watcher: forcing immediate poll", "", 1)
    PollTriggers()
}

; ----- Entry point -----------------------------------------------------------

Main()
