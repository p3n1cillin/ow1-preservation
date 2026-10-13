param([string]$ProcessName = 'Overwatch', [Parameter(Mandatory)][string]$Out, [int]$ProcessId = 0)
# Local diagnostic: render the owned client's top-level window into a PNG via PrintWindow
# (works when desktop screenshots are masked). Keep captures outside Git: they show game assets.
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class Win {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
}
"@
$p = Get-Process -Name $ProcessName -ErrorAction Stop | Where-Object { $_.MainWindowHandle -ne 0 -and ($ProcessId -eq 0 -or $_.Id -eq $ProcessId) } | Sort-Object StartTime -Descending | Select-Object -First 1
if (-not $p) { throw 'no window' }
$h = $p.MainWindowHandle
$r = New-Object Win+RECT
[void][Win]::GetWindowRect($h, [ref]$r)
$w = [Math]::Max(1, $r.R - $r.L); $hgt = [Math]::Max(1, $r.B - $r.T)
$bmp = New-Object System.Drawing.Bitmap $w, $hgt
$g = [System.Drawing.Graphics]::FromImage($bmp)
$dc = $g.GetHdc()
$ok = [Win]::PrintWindow($h, $dc, 2)
$g.ReleaseHdc($dc); $g.Dispose()
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
# Report whether the frame has any non-uniform content.
$colors = @{}
for ($x = 0; $x -lt $w; $x += [Math]::Max(1, [int]($w / 40))) { for ($y = 0; $y -lt $hgt; $y += [Math]::Max(1, [int]($hgt / 40))) { $colors[$bmp.GetPixel($x, $y).ToArgb()] = 1 } }
$bmp.Dispose()
"window={0}x{1} iconic={2} printwindow={3} distinct_sampled_colours={4}" -f $w, $hgt, [Win]::IsIconic($h), $ok, $colors.Count
