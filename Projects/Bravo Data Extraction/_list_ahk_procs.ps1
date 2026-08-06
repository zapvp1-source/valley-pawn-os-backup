Get-CimInstance Win32_Process |
  Where-Object { $_.Name -like 'AutoHotkey*' } |
  ForEach-Object { Write-Host ("{0} :: {1}" -f $_.ProcessId, $_.CommandLine) }

Write-Host "---- scheduled tasks that touch the watcher ----"
Get-ScheduledTask -ErrorAction SilentlyContinue |
  Where-Object { $_.TaskName -match 'watch|bravo|claude|heal' } |
  ForEach-Object {
    $info = $_ | Get-ScheduledTaskInfo -ErrorAction SilentlyContinue
    Write-Host ("{0} | state={1} | last={2} | next={3}" -f $_.TaskName, $_.State, $info.LastRunTime, $info.NextRunTime)
  }
