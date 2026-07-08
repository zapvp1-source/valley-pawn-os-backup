$out = @()
Get-Process AutoHotkey64,Bravo,Bravo*,powershell,dfsvc -ErrorAction SilentlyContinue | ForEach-Object {
    $c = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    $age = [math]::Round(((Get-Date) - $_.StartTime).TotalMinutes,1)
    $out += ("{0} PID={1} Sess={2} ageMin={3} :: {4}" -f $_.ProcessName, $_.Id, $_.SessionId, $age, $c)
}
if ($out.Count -eq 0) { "no matching processes" } else { $out }
