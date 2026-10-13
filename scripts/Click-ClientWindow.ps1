param([Parameter(Mandatory)][int]$X, [Parameter(Mandatory)][int]$Y, [string]$ProcessName = 'Overwatch', [int]$ProcessId = 0)
# Local diagnostic: post a left click to the owned client's window at client coordinates
# (for use when desktop input/screenshots are unavailable). Pair with Capture-ClientWindow.ps1.
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class ClickWin {
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint msg, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
}
"@
$p = Get-Process -Name $ProcessName -ErrorAction Stop | Where-Object { $_.MainWindowHandle -ne 0 -and ($ProcessId -eq 0 -or $_.Id -eq $ProcessId) } | Sort-Object StartTime -Descending | Select-Object -First 1
if (-not $p) { throw 'no client window' }
$h = $p.MainWindowHandle
$lp = [IntPtr](($Y -shl 16) -bor ($X -band 0xffff))
[void][ClickWin]::SetForegroundWindow($h)
[void][ClickWin]::PostMessage($h, 0x0200, [IntPtr]0, $lp)   # WM_MOUSEMOVE
Start-Sleep -Milliseconds 80
[void][ClickWin]::PostMessage($h, 0x0201, [IntPtr]1, $lp)   # WM_LBUTTONDOWN
Start-Sleep -Milliseconds 80
[void][ClickWin]::PostMessage($h, 0x0202, [IntPtr]0, $lp)   # WM_LBUTTONUP
"clicked pid=$($p.Id) at $X,$Y"
