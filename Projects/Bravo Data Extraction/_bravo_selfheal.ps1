# _bravo_selfheal.ps1 -- invoked every 2 min by _watchdog.ps1 (BravoWatcherWatchdog task,
# native Windows Session 1, interactive). Keeps BRAVO itself alive, which the watchdog
# never did (it only healed bravo_watcher.ahk). Built 2026-11-11 after Bravo stayed dead
# from a 11/10 18:31 VM reboot until the next day while every Mac-side gate failed.
#
# Rules: never touch Bravo while it has a real window (healthy or mid-run);
#        launch via the supported ClickOnce entrypoint (rundll32 dfshim) - no shell assoc;
#        cooldowns so it can never thrash; everything logged to logs\_selfheal.log;
#        diagnostics (window list + screenshot) captured whenever Bravo is windowless.
param([string]$Root)
$logs  = Join-Path $Root 'logs'
$slog  = Join-Path $logs '_selfheal.log'
$state = Join-Path $logs '_selfheal_lastlaunch.txt'
try { Set-Content (Join-Path $logs '_selfheal_heartbeat.txt') (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') } catch {}   # proves the hook is alive
# Append via read+Set-Content: Add-Content / AppendAllText silently fail on this Parallels share.
function Write-SHLog($m) {
  $line = "{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
  try { $cur = @(); if (Test-Path $slog) { $cur = @(Get-Content $slog -Tail 400) }; Set-Content $slog ($cur + $line) }
  catch { try { Set-Content (Join-Path $logs '_selfheal_logerr.txt') ($line + ' || ' + $_.Exception.Message) } catch {} }
}

# One-time: turn on ClickOnce's own verbose log (HKCU, no admin) so launch failures are visible.
$coKey = 'HKCU:\Software\Classes\Software\Microsoft\Windows\CurrentVersion\Deployment'
$coLog = "$env:USERPROFILE\clickonce_bravo.log"
try {
  if (-not (Test-Path $coKey)) { New-Item -Path $coKey -Force | Out-Null }
  if ((Get-ItemProperty $coKey -ErrorAction SilentlyContinue).LogFilePath -ne $coLog) {
    Set-ItemProperty $coKey -Name LogFilePath -Value $coLog
    Set-ItemProperty $coKey -Name LogVerbosityLevel -Value '1'
    Write-SHLog "enabled ClickOnce verbose logging -> $coLog"
  }
} catch { Write-SHLog ("clickonce log enable failed: " + $_.Exception.Message) }

if (-not ('WinEnumSH' -as [type])) {
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices; using System.Collections.Generic;
public class WinEnumSH {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc f, IntPtr l);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  public static List<string> List(bool all) {
    var r = new List<string>();
    EnumWindows(delegate(IntPtr h, IntPtr l) {
      bool v = IsWindowVisible(h);
      if (all || v) {
        var t = new StringBuilder(512); GetWindowText(h, t, 512);
        var c = new StringBuilder(256); GetClassName(h, c, 256);
        uint pid; GetWindowThreadProcessId(h, out pid); RECT rc; GetWindowRect(h, out rc);
        r.Add(pid + "|" + h.ToInt64() + "|" + (v ? "VIS" : "hid") + (IsIconic(h) ? ",MIN" : "") + "|" + rc.L + "," + rc.T + "," + rc.R + "," + rc.B + "|" + c + "|" + t);
      }
      return true; }, IntPtr.Zero);
    return r;
  }
}
"@
}

function Capture([string]$why) {
  $stamp = Join-Path $logs '_selfheal_diag.stamp'
  if ((Test-Path $stamp) -and (((Get-Date) - (Get-Item $stamp).LastWriteTime).TotalMinutes -lt 10)) { return }
  Set-Content $stamp (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
  $out = New-Object System.Collections.Generic.List[string]
  $out.Add("captured: " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + "  reason=" + $why)
  Get-Process | Where-Object { $_.ProcessName -match 'Bravo|dfsvc|AutoHotkey|WerFault|rundll32' } | ForEach-Object {
    $st = ''; try { $st = $_.StartTime.ToString('HH:mm:ss') } catch {}
    $out.Add(("{0} pid={1} resp={2} start={3} cpu={4} wsMB={5} title=[{6}]" -f $_.ProcessName,$_.Id,$_.Responding,$st,[int]$_.CPU,[int]($_.WorkingSet64/1MB),$_.MainWindowTitle))
  }
  $names = @{}; Get-Process | ForEach-Object { $names[[uint32]$_.Id] = $_.ProcessName }
  $out.Add("--- windows (visible all procs + hidden of Bravo/dfsvc/WerFault): proc :: pid|hwnd|vis|rect|class|title ---")
  foreach ($w in [WinEnumSH]::List($true)) {
    $p = [uint32]($w.Split('|')[0]); $n = $names[$p]
    if ($w.Split('|')[2] -like 'VIS*' -or $n -match 'Bravo|dfsvc|WerFault') { $out.Add("$n :: $w") }
  }
  $out.Add("--- Application event log, last 6h (Bravo/.NET/ClickOnce/crash sources) ---")
  try {
    Get-WinEvent -FilterHashtable @{LogName='Application'; StartTime=(Get-Date).AddHours(-6)} -ErrorAction Stop |
      Where-Object { $_.ProviderName -match 'NET Runtime|Application Error|Application Hang|Windows Error Reporting|Deployment|ClickOnce' -or $_.Message -match 'Bravo' } |
      Select-Object -First 15 | ForEach-Object { $out.Add(("{0} [{1}] {2}: {3}" -f $_.TimeCreated.ToString('MM-dd HH:mm:ss'), $_.LevelDisplayName, $_.ProviderName, (($_.Message -replace "`r|`n",' ') -replace '\s+',' ').Substring(0, [Math]::Min(600, $_.Message.Length)))) }
  } catch { $out.Add("eventlog: " + $_.Exception.Message) }
  $out.Add("--- ClickOnce reg ---")
  try { $r = Get-ItemProperty $coKey -ErrorAction Stop; $out.Add("LogFilePath=" + $r.LogFilePath + " Verbosity=" + $r.LogVerbosityLevel) } catch { $out.Add("reg read failed") }
  $out.Add("--- network ---")
  try { $out.Add("dns bravoinstall.com -> " + (([System.Net.Dns]::GetHostAddresses('bravoinstall.com') | ForEach-Object { $_.IPAddressToString }) -join ',')) } catch { $out.Add("dns FAIL: " + $_.Exception.Message) }
  foreach ($u in @('http://bravoinstall.com/BravoInstall/Bravo.application','https://www.google.com')) {
    try { $resp = Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 12; $out.Add("GET $u -> " + $resp.StatusCode + " bytes=" + $resp.RawContentLength) } catch { $out.Add("GET $u FAIL: " + $_.Exception.Message) }
  }
  try { Get-NetIPConfiguration | ForEach-Object { $out.Add("if " + $_.InterfaceAlias + " ip=" + ($_.IPv4Address.IPAddress -join ',') + " gw=" + ($_.IPv4DefaultGateway.NextHop -join ',') + " dns=" + ($_.DNSServer.ServerAddresses -join ',')) } } catch {}
  try { $lb = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime; $out.Add("last boot: $lb") } catch {}
  try { Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 4 | ForEach-Object { $out.Add("hotfix " + $_.HotFixID + " " + $_.InstalledOn) } } catch {}
  $out.Add("--- ClickOnce log tail ---")
  if (Test-Path $coLog) { Get-Content $coLog -Tail 60 | ForEach-Object { $out.Add($_) } } else { $out.Add("(no clickonce log yet)") }
  $out | Set-Content (Join-Path $logs '_selfheal_diag.txt') -Encoding UTF8
  try {
    Add-Type -AssemblyName System.Windows.Forms,System.Drawing
    $b = [System.Windows.Forms.SystemInformation]::VirtualScreen
    $bmp = New-Object System.Drawing.Bitmap $b.Width,$b.Height
    $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($b.X,$b.Y,0,0,$bmp.Size)
    $bmp.Save((Join-Path $logs '_selfheal_diag.png')); $g.Dispose(); $bmp.Dispose()
  } catch {}
  Write-SHLog ("diag captured (" + $why + ")")
}

# ============================ HEAL LOGIC ===================================
# ROOT CAUSE (2026-11-11): after the 11/10 Patch Tuesday reboot (KB5127648/KB5127690) the
# ClickOnce service host dfsvc.exe is no longer COM-activated on demand. Every launch of
# Bravo.appref-ms then exits 0 and does NOTHING - no Bravo, no error, no ClickOnce log - so
# Bravo stayed dead ~20h while every gate retried. Starting dfsvc.exe explicitly first makes
# the normal ClickOnce launch work (proven 14:15 -> gate PASS 14:17).
function Start-Dfsvc {
  if (@(Get-Process dfsvc -ErrorAction SilentlyContinue).Count -gt 0) { return }
  $dfExe = @("$env:windir\Microsoft.NET\Framework64\v4.0.30319\dfsvc.exe", "$env:windir\Microsoft.NET\Framework\v4.0.30319\dfsvc.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
  if ($dfExe) { Start-Process -FilePath $dfExe; Start-Sleep -Seconds 4; Write-SHLog "started dfsvc ($dfExe)" }
}
function Launch-Bravo([string]$why) {
  Set-Content $state (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
  Start-Dfsvc
  $sc = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms"
  Write-SHLog "LAUNCH ($why) -> ClickOnce shortcut"
  Start-Process -FilePath $sc
}

$bravo = @(Get-Process -Name Bravo -ErrorAction SilentlyContinue)
$hasWindow = $false
foreach ($p in $bravo) { if ($p.MainWindowTitle -like 'Bravo *') { $hasWindow = $true } }
if ($hasWindow) { return }   # healthy or mid-run: never touch it

# The Mac-side health gate is mid-recovery -> let it own Bravo, never race it.
$gl = Join-Path $logs '_health_gate.lock'
if ((Test-Path $gl) -and (((Get-Date) - (Get-Item $gl).LastWriteTime).TotalMinutes -lt 15)) { return }   # stale lock (>15m) is ignored

$lastLaunch = [datetime]::MinValue
if (Test-Path $state) { try { $lastLaunch = [datetime]::Parse((Get-Content $state -Raw).Trim()) } catch {} }
$sinceLaunch = ((Get-Date) - $lastLaunch).TotalMinutes

if ($bravo.Count -eq 0) {
  if ($sinceLaunch -lt 6) { Capture "no Bravo $([int]$sinceLaunch)m after launch"; return }
  Launch-Bravo "Bravo not running"
  return
}

# Bravo.exe exists but has no 'Bravo ...' window.
$youngest = ($bravo | ForEach-Object { try { $_.StartTime } catch { Get-Date } } | Sort-Object -Descending | Select-Object -First 1)
$ageMin = ((Get-Date) - $youngest).TotalMinutes
Capture "Bravo running ${ageMin}m with no main window"
if ($ageMin -lt 8 -or $sinceLaunch -lt 8) { return }   # still starting / ClickOnce updating - give it time
# Windowless for 8+ min = wedged (KNOWN_ISSUES: kill Bravo AND dfsvc, then relaunch).
Write-SHLog ("Bravo windowless " + [int]$ageMin + "m -> kill Bravo + dfsvc, relaunch")
Get-Process Bravo,dfsvc -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Launch-Bravo "windowless recovery"
