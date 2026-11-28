param([string]$Path)
# layshot.ps1 (2026-11-27, Bravo Warehouse): full-resolution screenshot (DPI aware). Read only.
Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;public class DpiA{[DllImport("user32.dll")]public static extern bool SetProcessDPIAware();}'
[DpiA]::SetProcessDPIAware() | Out-Null
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$vs = [System.Windows.Forms.SystemInformation]::VirtualScreen
$b = New-Object System.Drawing.Bitmap($vs.Width, $vs.Height)
$g = [System.Drawing.Graphics]::FromImage($b)
$g.CopyFromScreen($vs.Location, [System.Drawing.Point]::Empty, $b.Size)
$b.Save($Path, 'Png')
$g.Dispose(); $b.Dispose()
