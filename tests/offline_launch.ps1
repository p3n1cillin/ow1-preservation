param([Parameter(Mandatory=$true)][string]$Launcher)
$ErrorActionPreference = 'Stop'
$folder = Split-Path $Launcher -Parent
$beforeFile = (Get-Acl -LiteralPath $Launcher).Sddl
$beforeFolder = (Get-Acl -LiteralPath $folder).Sddl
& $Launcher $Launcher --self-test
if ($LASTEXITCODE -ne 0) { throw 'AppContainer network isolation failed' }
if ((Get-Acl -LiteralPath $Launcher).Sddl -ne $beforeFile -or
    (Get-Acl -LiteralPath $folder).Sddl -ne $beforeFolder) { throw 'Scoped ACL was not restored' }
# Fresh runner directories can have legacy DACLs without AUTO_INHERITED.
# Exercise both protected and inherited child ACLs in an owned fixture.
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class OfflineAclFixture {
    [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern bool ConvertStringSecurityDescriptorToSecurityDescriptorW(string sddl, uint revision, out IntPtr descriptor, out uint size);
    [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern bool SetFileSecurityW(string path, uint information, IntPtr descriptor);
    [DllImport("kernel32.dll")]
    static extern IntPtr LocalFree(IntPtr memory);
    public static void Set(string path, string sddl) {
        IntPtr descriptor; uint size;
        if (!ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, out descriptor, out size))
            throw new System.ComponentModel.Win32Exception();
        try {
            if (!SetFileSecurityW(path, 4, descriptor)) throw new System.ComponentModel.Win32Exception();
        } finally { LocalFree(descriptor); }
    }
}
'@
$fixture = Join-Path ([IO.Path]::GetTempPath()) ('ow1-acl-test-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $fixture | Out-Null
try {
    $fixtureExe = Join-Path $fixture 'ow1-offline-launch.exe'
    Copy-Item -LiteralPath $Launcher -Destination $fixtureExe
    $ownerSid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    foreach ($protectedChild in @($true, $false)) {
        [OfflineAclFixture]::Set($fixture, "D:P(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;FA;;;$ownerSid)")
        $childSddl = if ($protectedChild) { "D:P(A;;FA;;;SY)(A;;FA;;;BA)(A;;FA;;;$ownerSid)" }
            else { "D:(A;ID;FA;;;SY)(A;ID;FA;;;BA)(A;ID;FA;;;$ownerSid)" }
        [OfflineAclFixture]::Set($fixtureExe, $childSddl)
        $fixtureBeforeFolder = (Get-Acl -LiteralPath $fixture).Sddl
        $fixtureBeforeFile = (Get-Acl -LiteralPath $fixtureExe).Sddl
        & $fixtureExe $fixtureExe --self-test
        if ($LASTEXITCODE -ne 0) { throw 'Legacy ACL isolation fixture failed' }
        if ((Get-Acl -LiteralPath $fixtureExe).Sddl -ne $fixtureBeforeFile -or
            (Get-Acl -LiteralPath $fixture).Sddl -ne $fixtureBeforeFolder) {
            throw "Legacy ACL was not restored (protected child: $protectedChild)"
        }
    }
} finally {
    # The only recursive cleanup is the exact newly created temporary fixture.
    $resolvedFixture = [IO.Path]::GetFullPath($fixture)
    $tempPrefix = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
    if (!$resolvedFixture.StartsWith($tempPrefix, [StringComparison]::OrdinalIgnoreCase) -or
        (Split-Path $resolvedFixture -Leaf) -notlike 'ow1-acl-test-*') { throw 'Unsafe ACL fixture cleanup path' }
    Remove-Item -LiteralPath $resolvedFixture -Recurse -Force
}
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
