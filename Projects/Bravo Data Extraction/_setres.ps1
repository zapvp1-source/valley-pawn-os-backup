$out = 'Y:\Documents\Claude\Projects\Bravo Data Extraction\logs\_setres_result.txt'
if (-not (Test-Path (Split-Path $out))) { $out = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\logs\_setres_result.txt' }
$code = @"
using System;
using System.Runtime.InteropServices;
public class Disp {
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Ansi)]
  public struct DEVMODE {
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string dmDeviceName;
    public short dmSpecVersion; public short dmDriverVersion; public short dmSize;
    public short dmDriverExtra; public int dmFields;
    public int dmPositionX; public int dmPositionY; public int dmDisplayOrientation; public int dmDisplayFixedOutput;
    public short dmColor; public short dmDuplex; public short dmYResolution; public short dmTTOption; public short dmCollate;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string dmFormName;
    public short dmLogPixels; public int dmBitsPerPel; public int dmPelsWidth; public int dmPelsHeight;
    public int dmDisplayFlags; public int dmDisplayFrequency;
    public int dmICMMethod; public int dmICMIntent; public int dmMediaType; public int dmDitherType;
    public int dmReserved1; public int dmReserved2; public int dmPanningWidth; public int dmPanningHeight;
  }
  [DllImport("user32.dll")] public static extern int EnumDisplaySettings(string d, int m, ref DEVMODE dm);
  [DllImport("user32.dll")] public static extern int ChangeDisplaySettings(ref DEVMODE dm, int flags);
  public static string Modes(){
    DEVMODE dm = new DEVMODE(); dm.dmSize=(short)Marshal.SizeOf(typeof(DEVMODE));
    string s=""; int i=0;
    while(EnumDisplaySettings(null, i, ref dm)!=0){ s+=dm.dmPelsWidth+"x"+dm.dmPelsHeight+"@"+dm.dmBitsPerPel+";"; i++; }
    return s;
  }
  public static int Set(int w, int h){
    DEVMODE dm = new DEVMODE(); dm.dmSize=(short)Marshal.SizeOf(typeof(DEVMODE));
    EnumDisplaySettings(null, -1, ref dm);
    dm.dmPelsWidth=w; dm.dmPelsHeight=h; dm.dmFields=0x80000|0x100000;
    return ChangeDisplaySettings(ref dm, 0);
  }
}
"@
Add-Type $code
$log = @()
$log += "AVAILABLE: " + ([Disp]::Modes())
# try, in order of preference, common resolutions that fit Bravo dialogs
$targets = @(@(2516,1792))
$done = $false
foreach ($t in $targets) {
  $r = [Disp]::Set($t[0],$t[1])
  $log += ("try {0}x{1} -> {2}" -f $t[0],$t[1],$r)
  if ($r -eq 0) { $done = $true; break }
}
Add-Type -AssemblyName System.Windows.Forms
Start-Sleep 1
$b = [System.Windows.Forms.SystemInformation]::VirtualScreen
$log += ("RESULT now: {0}x{1} success={2}" -f $b.Width,$b.Height,$done)
$log -join "`r`n" | Set-Content $out
