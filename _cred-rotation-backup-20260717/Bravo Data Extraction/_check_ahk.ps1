$procs = Get-Process AutoHotkey64 -ErrorAction SilentlyContinue
foreach ($p in $procs) {
    $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId=$($p.Id)").CommandLine
    Write-Host ("PID=" + $p.Id + " Session=" + $p.SessionId + " CMD=" + $cmd)
}
if ($procs.Count -eq 0) { Write-Host "No AutoHotkey64 processes" }
