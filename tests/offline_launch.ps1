param([Parameter(Mandatory=$true)][string]$Launcher)
$ErrorActionPreference = 'Stop'
$folder = Split-Path $Launcher -Parent
$beforeFile = (Get-Acl -LiteralPath $Launcher).Sddl
$beforeFolder = (Get-Acl -LiteralPath $folder).Sddl
& $Launcher $Launcher --self-test
if ($LASTEXITCODE -ne 0) { throw 'AppContainer network isolation failed' }
if ((Get-Acl -LiteralPath $Launcher).Sddl -ne $beforeFile -or
    (Get-Acl -LiteralPath $folder).Sddl -ne $beforeFolder) { throw 'Scoped ACL was not restored' }
foreach ($mode in @('--wmi-workaround', '--run-offline', '--map-probe', '--map-probe-no-speech', '--map-probe-preload',
    '--map-probe-voice-request', '--map-probe-stages', '--catalogue-schema-probe', '--catalogue-import-probe',
    '--retail-snapshot', '--retail-offline', '--retail-map-probe', '--retail-map-worker-probe', '--retail-map-tick-probe',
    '--retail-map-context-probe', '--retail-map-context-tick-probe', '--retail-map-context-tick-debug', '--retail-map-loader-probe')) {
    $rejection = & $Launcher $Launcher $mode 2>&1
    if ($LASTEXITCODE -eq 0) { throw 'Unknown executable accepted for in-memory patch' }
    $expected = if ($mode.StartsWith('--retail-')) { 'Retail launch only supports the fingerprinted final OW1 executable' }
        else { 'WMI workaround only supports verified Overwatch 1.0.1.27578' }
    if (($rejection | Out-String) -notlike "*$expected*") {
        throw "Mode $mode did not reach its executable fingerprint guard: $rejection"
    }
}
if ((Get-Acl -LiteralPath $Launcher).Sddl -ne $beforeFile -or
    (Get-Acl -LiteralPath $folder).Sddl -ne $beforeFolder) { throw 'Rejected patch changed ACL' }
Write-Host 'Isolation, ACL restoration and unknown-build rejection passed.'
