# _cleanup_stale_claims.ps1 - shipped 2026-08-16 (additive hardening, sold-review incident)
# Moves stale claimed triggers (claimed more than MaxAgeMin minutes ago with NO
# matching result file in results\) from triggers\claimed\ into triggers\failed\
# so a crashed/killed run can never wedge or confuse the queue. NEVER deletes.
# Safe to run any time: 90-min age floor protects any legitimately running cell.
# Run in-VM: powershell -NoProfile -ExecutionPolicy Bypass -File _cleanup_stale_claims.ps1
param([int]$MaxAgeMin = 90)
$root    = "Y:\Documents\Claude\Projects\Bravo Data Extraction"
$claimed = Join-Path $root "triggers\claimed"
$failed  = Join-Path $root "triggers\failed"
$results = Join-Path $root "results"
$log     = Join-Path $root "logs\_stale_claims_cleanup.log"
if (-not (Test-Path $failed)) { New-Item -ItemType Directory -Path $failed | Out-Null }
$cutoff = (Get-Date).AddMinutes(-$MaxAgeMin)
$moved = 0
Get-ChildItem -Path $claimed -Filter *.json -File -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.LastWriteTime -lt $cutoff) {
        $resultFile = Join-Path $results ($_.BaseName + ".result.json")
        if (-not (Test-Path $resultFile)) {
            Move-Item -Path $_.FullName -Destination $failed -Force
            $moved++
            Add-Content -Path $log -Value ("{0} moved stale claim {1} (claimed {2}, no result)" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $_.Name, $_.LastWriteTime)
        }
    }
}
Add-Content -Path $log -Value ("{0} cleanup done - moved {1} stale claim(s)" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $moved)
Write-Host ("stale-claims cleanup: moved " + $moved)
