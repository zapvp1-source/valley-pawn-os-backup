#!/usr/bin/env python3
"""Folder cleanup 2026-08-21 (Joshua: "clean up folders").
Archives never-registered task folders from ~/Documents/Claude/Scheduled into
Scheduled/_archive-20260821/ UNLESS another live file references them.
Move-only (reversible). Never touches registered tasks, _shared-bravo-data, or anything not on the list."""
import os, subprocess, shutil

SCHED = os.path.expanduser("~/Documents/Claude/Scheduled")
ARCH = os.path.join(SCHED, "_archive-20260821")
CANDIDATES = [
 "bald-rock-auto-contract","bald-rock-signing-status","brightlocal-weekly-sync-alerts-check",
 "chekkit-review-responder","chekkit-watcher-heal-2026-06-10","cloud-cover-keep-alive",
 "controlio-offline-agent-check","daily-distributor-application-monitor","daily-intake-margin",
 "daily-intake-prestage","daily-loan-inventory-text","daily-mail-unsubscribe",
 "daily-social-media-content","dashboard-data-collector","distributor-setup-monitor",
 "domain-transfer-check","ebay-photo-enhance-done-notify","ebay-title-enrichment-backlog",
 "fb-token-health-check-daily","gusto-keep-alive","jewelry-freeze-test-compare",
 "jewelry-freeze-test-pull","markdownver-watcher-restart-oneshot","markdownver-watcher-restart-oneshot-r2",
 "mm-merchandisers-daily-scan","monday-bravo-reminder","monday-store-rankings","monthly-cpa-report",
 "monthly-gun-audit-summary","monthly-reconciliation-report","monthly-sold-inventory-refresh",
 "monthly-top-sales-review","new-inv-weekly-report","nics-selector-autofix",
 "nics-transfers-nightly-validation","nics-ttm-baseline-compile","salt-run-monthly-seo-audit",
 "salt-run-quarterly-phase-check","salt-run-weekly-analytics","saturday-facebook-posts",
 "scheduled-task-history-logger","thursday-youtube-employee-clips","vp-bing-places-signin-watcher",
 "vp-gusto-signature-chase-firstrun","vp-social-publisher","wednesday-facebook-posts",
 "weekly-aged-inventory-report","weekly-ebay-sales-ranking","weekly-email-cleanup",
 "weekly-employee-sales-rankings","weekly-fpd-ranking","weekly-jacksonville-property-search",
 "weekly-loan-layaway-review","weekly-loan-portfolio-refresh","weekly-new-deal-request",
 "weekly-payroll-to-qbo","weekly-st-augustine-property-search","weekly-timekeeping-analysis-mcp",
 "weekly-valley-pawn-email-campaign","weekly-youtube-shorts",
]
# grep domains where a mention means "still referenced by something live"
GREP_DIRS = [SCHED, os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction"),
             os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS/bin")]

os.makedirs(ARCH, exist_ok=True)
moved, referenced, absent = [], [], []
for name in CANDIDATES:
    src = os.path.join(SCHED, name)
    if not os.path.isdir(src):
        absent.append(name); continue
    hits = []
    for gd in GREP_DIRS:
        try:
            r = subprocess.run(["grep","-rl","--include=*.md","--include=*.ps1","--include=*.ahk","--include=*.py",
                                name, gd], capture_output=True, text=True, timeout=120)
            for line in r.stdout.splitlines():
                # ignore hits inside the candidate's own folder, the archive, and pure-inventory docs
                if src in line or "_archive-20260821" in line: continue
                if line.endswith(("BUSINESS_OS.md","CHANGELOG.md")): continue
                hits.append(line)
        except Exception as e:
            hits.append(f"GREP-ERROR {gd}: {e}")
    if hits:
        referenced.append((name, hits[:4]))
    else:
        dst = os.path.join(ARCH, name)
        if os.path.exists(dst): dst = dst + "-dup"
        shutil.move(src, dst)
        moved.append(name)

print("MOVED TO ARCHIVE (%d):" % len(moved))
for m in moved: print("  ", m)
print("KEPT — still referenced (%d):" % len(referenced))
for n,h in referenced:
    print("  ", n)
    for x in h: print("      ->", x)
print("NOT FOUND ON DISK (%d):" % len(absent), absent)
