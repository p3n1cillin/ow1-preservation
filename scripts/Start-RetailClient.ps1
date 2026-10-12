[CmdletBinding()]
param(
    [string]$ClientFolder = (Join-Path $env:LOCALAPPDATA 'OW1-preservation-build\clients\1.74.0.0.104319-original\Overwatch'),
    [string]$BuildRoot = (Join-Path $env:LOCALAPPDATA 'OW1-preservation-build'),
    [ValidateSet('Startup', 'PracticeRequest', 'PracticeLoad', 'PracticeResources')]
    [string]$Mode = 'Startup'
)
$ErrorActionPreference = 'Stop'
$ClientFolder = [IO.Path]::GetFullPath($ClientFolder)
$BuildRoot = [IO.Path]::GetFullPath($BuildRoot)
$launcher = Join-Path $BuildRoot 'relay\tools\offline-launch\Release\ow1-offline-launch.exe'
$clientExe = Join-Path $ClientFolder '_retail_\Overwatch.exe'
if (!(Test-Path -LiteralPath $launcher -PathType Leaf)) { throw 'Build the offline launcher with scripts/Build.ps1 first.' }
if (!(Test-Path -LiteralPath $clientExe -PathType Leaf)) { throw 'Supply the extracted final retail installation; see FINAL_RETAIL.md.' }
# The helper rejects unknown fingerprints before changing permissions, verifies
# actual network denial, and restores scoped permissions after client exit.
$option = switch ($Mode) {
    'Startup' { '--retail-offline' }
    'PracticeRequest' { '--retail-map-context-probe' }
    'PracticeLoad' { '--retail-map-loader-probe' }
    'PracticeResources' { '--retail-map-resource-probe' }
}
$logName = if ($Mode -eq 'Startup') { 'retail-interactive' } else { "retail-$Mode" }
$process = Start-Process -FilePath $launcher -ArgumentList ('"{0}" {1}' -f $clientExe, $option) `
    -WorkingDirectory $ClientFolder -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $BuildRoot "$logName.log") `
    -RedirectStandardError (Join-Path $BuildRoot "$logName-errors.log")
Write-Host "Offline retail launcher PID $($process.Id); mode $Mode. Logs: $BuildRoot\$logName.log"
if ($Mode -eq 'Startup') { Write-Host 'Close the game to end the isolated startup session.' }
else { Write-Host 'Bounded native Practice diagnostic. Opening cinematic is skipped; map/session success remains unverified.' }
Write-Host 'Private login, controllable heroes and gameplay remain unimplemented for this build.'
