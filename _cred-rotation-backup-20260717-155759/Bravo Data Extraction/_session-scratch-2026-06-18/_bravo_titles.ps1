Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class Win {
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool IsHungAppWindow(IntPtr hWnd);
}
"@
$titles = New-Object System.Collections.ArrayList
$cb = [Win+EnumWindowsProc]{ param($h,$l)
  if ([Win]::IsWindowVisible($h)) {
    $sb = New-Object System.Text.StringBuilder 512
    [void][Win]::GetWindowText($h,$sb,512)
    $t = $sb.ToString()
    if ($t -match 'Bravo|VALLEY PAWN|AutoHotkey|Error' -and $t.Trim()) {
      $hung = [Win]::IsHungAppWindow($h)
      [void]$titles.Add(("'{0}' hung={1}" -f $t, $hung))
    }
  }
  return $true
}
[void][Win]::EnumWindows($cb, [IntPtr]::Zero)
if ($titles.Count -eq 0) { "no Bravo/AHK/Error windows" } else { $titles }
