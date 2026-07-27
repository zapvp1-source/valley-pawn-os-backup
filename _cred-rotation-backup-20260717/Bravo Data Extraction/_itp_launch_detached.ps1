# _itp_launch_detached.ps1
# Launches the validate+restart wrapper DETACHED inside the VM and returns
# immediately, so the caller's prlctl/osascript timeout cannot kill it
# mid-run. The wrapper writes its own status to _itp_restart_status.txt.
Start-Process -FilePath "powershell.exe" -ArgumentList @(
    "-NoProfile","-ExecutionPolicy","Bypass","-File",
    "Y:\Documents\Claude\Projects\Bravo Data Extraction\_itp_validate_and_restart.ps1"
) -WindowStyle Hidden
Write-Host "DETACHED_LAUNCH_ISSUED"
