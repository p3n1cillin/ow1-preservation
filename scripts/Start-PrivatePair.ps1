[CmdletBinding()]
param(
    [string]$ClientFolder = (Join-Path $env:LOCALAPPDATA 'OW1-preservation-build\clients\1.74.0.0.104319-original\Overwatch'),
    [string]$BuildRoot = (Join-Path $env:LOCALAPPDATA 'OW1-preservation-build'),
    [string]$LogRoot,
    [string]$LogName = 'retail-private-pair',
    # Host-loopback ports of the two private services (one per account/client).
    # Client 0 uses container port 1119, client 1 container port 1129.
    [ValidateCount(2,2)][int[]]$HostPorts = @(21119, 21129),
    # Optional bounded datagram diagnostic: one host UDP port shared by both clients.
    [int]$UdpHostPort = 0,
    [Parameter(Mandatory)][ValidateRange(1,300)][int]$RunForSeconds,
    [ValidateRange(0,180)][int]$ClientDelaySeconds = 60,
    [ValidateSet('both','c0','c1','none')][string]$Dump = 'both',
    [string]$TrustCaCertificate,
    [switch]$ObserveTls,
    [switch]$TrustSocketCa,
    [string]$TrustLobbyKey
)
# Two original clients in ONE shared AppContainer profile with no network
# capability. The launcher refuses to start while another launcher or
# Overwatch process exists, restores the scoped ACLs after both clients end,
# and passes each client exactly --BNetServer=127.0.0.1:<its container port>.
$ErrorActionPreference = 'Stop'
$launcher = Join-Path $BuildRoot 'relay\tools\offline-launch\Release\ow1-offline-launch.exe'
$clientExe = Join-Path $ClientFolder '_retail_\Overwatch.exe'
if (!$LogRoot) { $LogRoot = Join-Path (Split-Path $PSScriptRoot -Parent) '.local\runs' }
$LogRoot = [IO.Path]::GetFullPath($LogRoot)
New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
if (!(Test-Path -LiteralPath $launcher -PathType Leaf)) { throw 'Build the offline launcher with scripts/Build.ps1 first.' }
if (!(Test-Path -LiteralPath $clientExe -PathType Leaf)) { throw 'Supply the extracted final retail installation; see FINAL_RETAIL.md.' }
$arguments = @(('"{0}"' -f $clientExe), '--retail-private-pair', '--run-for', $RunForSeconds,
               '--client-delay', $ClientDelaySeconds, '--pair-dump', $Dump)
if ($TrustCaCertificate) { $arguments += @('--trust-ca', ('"{0}"' -f [IO.Path]::GetFullPath($TrustCaCertificate))) }
if ($ObserveTls) { $arguments += '--observe-tls' }
if ($TrustSocketCa) { $arguments += '--trust-socket-ca' }
if ($TrustLobbyKey) { $arguments += @('--trust-lobby-key', ('"{0}"' -f [IO.Path]::GetFullPath($TrustLobbyKey))) }
$containerPorts = @(1119, 1129)
for ($i = 0; $i -lt 2; ++$i) {
    $arguments += @('--client-forward', "$($containerPorts[$i]):$($HostPorts[$i])")
    if ($UdpHostPort) { $arguments += @('--client-udp-forward', "$($containerPorts[$i]):$UdpHostPort") }
}
$process = Start-Process -FilePath $launcher -ArgumentList $arguments -WorkingDirectory $ClientFolder -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $LogRoot "$LogName.log") `
    -RedirectStandardError (Join-Path $LogRoot "$LogName-errors.log")
Write-Host "Private pair launcher PID $($process.Id). Logs: $LogRoot\$LogName.log (lines tagged [c0]/[c1])"
Write-Host "Both clients end after $RunForSeconds seconds from the first client's start; folder permissions are then restored."
