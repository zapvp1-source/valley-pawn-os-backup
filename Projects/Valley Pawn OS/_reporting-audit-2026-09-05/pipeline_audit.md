# Bravo pipeline audit — 2026-09-05 (Aug 6–Sep 5 window)

Triggers 386: success 236 (61.1%) · partial 134 (34.7%) · aborted 16 (4.1%). Cells 1,237: success 969 (78.3%) · error 203 · skipped 65.
Median successful cell 91 s (p90 253 s). Store failure rates flat (ROA 18.9% … WAY 24.6%) — failures are cell/app-state driven.

Worst cells: jewelry-case-counts-v2 62.7% (46 of its 52 fails are genuinely-empty categories), jewelry-case-counts 42.5%, jewelry-count-audit 38.5%, chekkit-invites 40%, fpd-cohort 33%, nics-transfers 25.6%, intake-detail 24.8%, aged-inventory-summary 25%, post-to-accounting-post 100% (0/17), post-to-accounting-gl 100% (0/6), sold-yesterday 100% (0/5).
Clean: layaways 20/20, employee-activity 20/20, chekkit-invites-range 15/15, loans-75-days-past-due 19/20.

Top causes (268 non-success cells): bravo-not-ready abort 61 · EnsureStore nav cascade 59 · jewelry empty-category 46 · saved-report selection failed 34 · preview/grid render timeout 23 (ROA 11) · GL Post click 12 · grid truncation 10 · ClickByName 8 · BackToDashboard 4 · 45-min hard wall 4.
Infra: 30 watcher restarts (all PASS); foreground-steal spikes 8/12, 8/18–8/21 (Chrome↔VM contention); no ClickOnce events since 7/28.

Structural: single login/VM/serial watcher; 45-min per-trigger wall; two uncoordinated watchers (main + scrap); Continuous-Scrolling toggle still in 8 handlers incl. daily SafeRegisterJournal; DevExpress virtualiser caps large grids (~78/2,331 rows); 4 handlers accept 0 rows silently; ChekkitInactivesV2 lacks 0-row guard; result started_at==finished_at bug; store-hours blind spot outside jewelry; GL step-2 doesn't check step-1; plaintext password fallback in bravo_watcher.ahk and old password in FINDINGS_AND_PLAN.md.

Non-UI: SSRS `ssrs.bravoapplication.com:9176` (see ssrs_probe); WCF EntityService (private, signed, vendor says no); SQL Express stopped; no API/webhooks/scheduled-export references anywhere in the folder. Bravo *does* email Daily/Monthly KPI PDFs per store (noreply-reporting@bravostoresystems.com) — the only scheduled export ever requested.
