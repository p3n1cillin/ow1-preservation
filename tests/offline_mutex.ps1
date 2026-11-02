param([Parameter(Mandatory=$true)][string]$Launcher)
# E0: named-mutex namespace self-test across two temporary AppContainer
# profiles. No game files, network capabilities or storage mutex names are used.
$ErrorActionPreference = 'Stop'
$folder = Split-Path $Launcher -Parent
$beforeFile = (Get-Acl -LiteralPath $Launcher).Sddl
$beforeFolder = (Get-Acl -LiteralPath $folder).Sddl
$output = & $Launcher $Launcher --self-test-mutex 2>&1 | Out-String
$code = $LASTEXITCODE
Write-Output $output
# GitHub's hosted Windows runners refuse every named-object create from an
# AppContainer (ERR:5 for both the client-SD and default attempts in all
# no-precreate cases), so the probe cannot run there at all. Report that as a
# skip (CTest SKIP_RETURN_CODE 77), never as a pass; anywhere else, and on a
# runner where even one create succeeds, the full checks below apply.
$noPrecreate = @([regex]::Matches($output, 'E0 case=no-precreate-[a-z-]+ (first|second): [^\r\n]*'))
if ($env:GITHUB_ACTIONS -eq 'true' -and $code -ne 0 -and $noPrecreate.Count -eq 4 -and
    @($noPrecreate | Where-Object { $_.Value -notmatch 'client_sd_create=ERR:5 default_create=ERR:5 ' }).Count -eq 0) {
    if ((Get-Acl -LiteralPath $Launcher).Sddl -ne $beforeFile -or
        (Get-Acl -LiteralPath $folder).Sddl -ne $beforeFolder) { throw 'Scoped ACL was not restored' }
    Write-Output 'SKIP: this runner denies AppContainer named-object creation (ERR:5); the E0 probe needs a desktop session.'
    exit 77
}
if ($code -ne 0) { throw "Mutex namespace self-test failed (exit $code)" }
if ((Get-Acl -LiteralPath $Launcher).Sddl -ne $beforeFile -or
    (Get-Acl -LiteralPath $folder).Sddl -ne $beforeFolder) { throw 'Scoped ACL was not restored' }
foreach ($expected in @(
    'Network isolation verified; no network capabilities granted.',
    'E0 second profile network isolation verified.',
    'E0 precreate=OK',
    'E0 objects_absent=1 second_profile_deleted=1',
    'E0 summary same_package_shared=1 ',
    'E0 first_profile_deleted=1',
    'E0 mutex namespace self-test passed.')) {
    if ($output -notlike "*$expected*") { throw "Missing self-test result: $expected" }
}
foreach ($case in @('no-precreate-cross-package', 'no-precreate-same-package', 'precreated-cross-package')) {
    foreach ($role in @('first', 'second')) {
        if ($output -notmatch "E0 case=$case ${role}: app_container=1 client_sd_create=\S+ default_create=\S+ open_synchronize=\S+ attempts=\d already_exists=[01] object=\S+ result=(ACQUIRED|FAILED:\d+)") {
            throw "Malformed or uncontained probe result: $case $role"
        }
    }
    if ($output -notmatch "E0 case=$case host_open_while_held: (OK object=\S+|ERR:\d+)") { throw "Missing host view: $case" }
}
# The probe child refuses any name outside the reserved test prefix.
& $Launcher --mutex-probe 'Global\C:/storage/data' release | Out-Null
if ($LASTEXITCODE -ne 5) { throw 'Mutex probe accepted a non-test name' }
