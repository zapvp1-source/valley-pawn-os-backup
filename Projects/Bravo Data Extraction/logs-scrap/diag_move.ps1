$ErrorActionPreference = 'Stop'
$base = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\triggers-scrap'
$t0 = Get-Date
try {
    New-Item -Path "$base\zzdiagtest.json" -ItemType File -Force | Out-Null
    $t1 = Get-Date
    Move-Item -Path "$base\zzdiagtest.json" -Destination "$base\claimed\zzdiagtest.json" -Force
    $t2 = Get-Date
    Write-Output "CREATE_SECONDS=$((New-TimeSpan -Start $t0 -End $t1).TotalSeconds)"
    Write-Output "MOVE_SECONDS=$((New-TimeSpan -Start $t1 -End $t2).TotalSeconds)"
    Remove-Item -Path "$base\claimed\zzdiagtest.json" -Force
    Write-Output "OK"
} catch {
    Write-Output "ERROR: $($_.Exception.Message)"
}
