$ErrorActionPreference = 'Continue'
Add-Type @"
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public class WinEnum {
  public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
  [DllImport(\"user32.dll\")] public static extern bool EnumWindows(EnumProc proc, IntPtr lParam);
  [DllImport(\"user32.dll\")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport(\"user32.dll\", CharSet=CharSet.Auto)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
  [DllImport(\"user32.dll\", CharSet=CharSet.Auto)] public static extern int GetClassName(IntPtr hWnd, StringBuilder text, int count);
  [DllImport(\"user32.dll\")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
  public static List<string> List() {
    var rows = new List<string>();
    EnumWindows((h, l) => {
      if (!IsWindowVisible(h)) return true;
      var t = new StringBuilder(512); GetWindowText(h, t, 512);
      var c = new StringBuilder(256); GetClassName(h, c, 256);
      if (t.Length == 0 && c.Length == 0) return true;
      uint pid = 0; GetWindowThreadProcessId(h, out pid);
      rows.Add(pid + \"|\" + h.ToInt64() + \"|\" + c.ToString() + \"|\" + t.ToString());
      return true;
    }, IntPtr.Zero);
    return rows;
  }
}
"@
[WinEnum]::List() | ForEach-Object { Write-Output $_ }

