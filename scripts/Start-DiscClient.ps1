[CmdletBinding()]
param(
    [string]$ClientFolder = (Join-Path $env:LOCALAPPDATA 'OW1-preservation-build\clients\1.0.1.27578'),
    [string]$BuildRoot = (Join-Path $env:LOCALAPPDATA 'OW1-preservation-build')
)
$ErrorActionPreference = 'Stop'
$ClientFolder = [IO.Path]::GetFullPath($ClientFolder)
$BuildRoot = [IO.Path]::GetFullPath($BuildRoot)
$launcher = Join-Path $BuildRoot 'relay\tools\offline-launch\Release\ow1-offline-launch.exe'
$clientExe = Join-Path $ClientFolder 'Overwatch.exe'
if (!(Test-Path -LiteralPath $launcher -PathType Leaf)) { throw 'Build the offline launcher with scripts/Build.ps1 first.' }
if (!(Test-Path -LiteralPath $clientExe -PathType Leaf)) { throw 'Prepare and reconstruct the disc client first; see DISC_RUNTIME.md.' }
# The helper verifies the exact fingerprint, network isolation and patch bytes.
# It owns the client job and restores temporary permissions when the game exits.
$process = Start-Process -FilePath $launcher -ArgumentList ('"{0}" --run-offline' -f $clientExe) `
    -WorkingDirectory $ClientFolder -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $BuildRoot 'offline-interactive.log') `
    -RedirectStandardError (Join-Path $BuildRoot 'offline-interactive-errors.log')
Write-Host "Offline launcher PID $($process.Id). Close the game to end the isolated session."
Write-Host 'This opens the original title/login screen; private login and gameplay remain unavailable.'
