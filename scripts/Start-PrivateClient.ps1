[CmdletBinding()]
param(
    [string]$ClientFolder = (Join-Path $env:LOCALAPPDATA 'OW1-preservation-build\clients\1.74.0.0.104319-original\Overwatch'),
    [string]$BuildRoot = (Join-Path $env:LOCALAPPDATA 'OW1-preservation-build'),
    # Container-loopback port -> host-loopback port where the private service listens.
    [string[]]$Forward = @('1119:21119'),
    [string[]]$ClientArgs = @('--BNetServer=127.0.0.1:1119'),
    [string]$LogName = 'retail-private'
)
$ErrorActionPreference = 'Stop'
$launcher = Join-Path $BuildRoot 'relay\tools\offline-launch\Release\ow1-offline-launch.exe'
$clientExe = Join-Path $ClientFolder '_retail_\Overwatch.exe'
if (!(Test-Path -LiteralPath $launcher -PathType Leaf)) { throw 'Build the offline launcher with scripts/Build.ps1 first.' }
if (!(Test-Path -LiteralPath $clientExe -PathType Leaf)) { throw 'Supply the extracted final retail installation; see FINAL_RETAIL.md.' }
# The client keeps its AppContainer with no network capability. Only the
# listed container-loopback ports are bridged, each to one host-loopback port.
$arguments = @(('"{0}"' -f $clientExe), '--retail-private')
foreach ($f in $Forward) { $arguments += @('--forward', $f) }
$arguments += '--'
$arguments += $ClientArgs
$process = Start-Process -FilePath $launcher -ArgumentList $arguments -WorkingDirectory $ClientFolder -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $BuildRoot "$LogName.log") `
    -RedirectStandardError (Join-Path $BuildRoot "$LogName-errors.log")
Write-Host "Private retail launcher PID $($process.Id). Logs: $BuildRoot\$LogName.log"
Write-Host 'Close the game window normally so the launcher restores folder permissions.'
