param([Parameter(Mandatory=$true)][string]$Launcher)
# Pair-mode (two or three clients, one shared AppContainer profile) argument guards.
# No game is started: valid arguments must stop at the executable fingerprint
# guard (the launcher passes itself as PATH), before any profile, ACL grant,
# bridge or process is created.
$ErrorActionPreference = 'Stop'
$folder = Split-Path $Launcher -Parent
$beforeFile = (Get-Acl -LiteralPath $Launcher).Sddl
$beforeFolder = (Get-Acl -LiteralPath $folder).Sddl
$fingerprint = 'Retail launch only supports the fingerprinted final OW1 executable'
function Invoke-Pair([string[]]$Arguments) {
    $output = & $Launcher $Launcher --retail-private-pair @Arguments 2>&1 | Out-String
    return @{ code = $LASTEXITCODE; text = $output }
}
function Assert-Rejected([string[]]$Arguments, [string]$Expected, [int]$Code = 2) {
    $result = Invoke-Pair $Arguments
    if ($result.code -ne $Code -or $result.text -notlike "*$Expected*") {
        throw "Pair arguments not rejected as expected ($Expected): $($Arguments -join ' ') -> exit $($result.code): $($result.text)"
    }
}
$pair = @('--client-forward','1119:21119','--client-forward','1129:21129')
$trio = $pair + @('--client-forward','1139:21139')
$trioUdp = @('--client-forward','1119:21119','--client-udp-forward','1119:21120','--client-forward','1129:21129','--client-udp-forward','1129:21120','--client-forward','1139:21139','--client-udp-forward','1139:21120')
$pairUdp = @('--client-forward','1119:21119','--client-udp-forward','1119:21120','--client-forward','1129:21129','--client-udp-forward','1129:21120')

# Accepted shapes reach the fingerprint guard (exit 1), never a launch.
foreach ($arguments in @(
    (@('--run-for','300') + $pair),
    (@('--run-for','14400') + $pair),
    (@('--run-for','30') + $pair),
    (@('--run-for','300','--client-delay','180') + $pair),
    (@('--run-for','240','--client-delay','60','--pair-dump','c1') + $pairUdp),
    (@('--run-for','300','--pair-dump','none','--observe-tls') + $pair),
    (@('--run-for','300','--client-delay','20','--pair-dump','c2') + $trio),
    (@('--run-for','300','--client-delay','60','--pair-dump','all') + $trioUdp))) {
    Assert-Rejected $arguments $fingerprint 1
}
# Duration: mandatory, 1..14400 (four hours), once.
foreach ($duration in @('0','14401','99999','-1','NaN','999999')) {
    Assert-Rejected (@('--run-for',$duration) + $pair) 'Pair diagnostic duration'
}
Assert-Rejected $pair 'Pair diagnostic requires --run-for in 1..14400 seconds'
Assert-Rejected (@('--run-for','100','--run-for','100') + $pair) 'Pair diagnostic duration'
# Two or three clients, fixed container ports 1119, 1129 then 1139.
Assert-Rejected @('--run-for','100','--client-forward','1119:21119') 'two or three clients'
Assert-Rejected @('--run-for','100','--client-forward','1129:21129','--client-forward','1119:21119') 'two or three clients'
Assert-Rejected @('--run-for','100','--client-forward','1119:21119','--client-forward','1120:21129') 'two or three clients'
Assert-Rejected (@('--run-for','100','--client-forward','1119:21119','--client-forward','1139:21139')) 'two or three clients'
Assert-Rejected (@('--run-for','100') + $trio + @('--client-forward','1149:21149')) 'two or three clients'
Assert-Rejected (@('--run-for','100') + $pair + @('--client-forward','1139:21129')) 'TCP host ports must differ'
Assert-Rejected (@('--run-for','100') + $pair + @('--client-forward','1139:1139')) 'differ from the container ports'
Assert-Rejected (@('--run-for','300','--client-delay','30') + $pairUdp + @('--client-forward','1139:21139')) 'both clients or neither'
# The third client starts 2 * delay after the first and needs 30 seconds.
Assert-Rejected (@('--run-for','100','--client-delay','36') + $trio) 'leave at least 30 seconds'
# Host ports: distinct TCP, never the container ports.
Assert-Rejected @('--run-for','100','--client-forward','1119:21119','--client-forward','1129:21119') 'TCP host ports must differ'
Assert-Rejected @('--run-for','100','--client-forward','1119:1129','--client-forward','1129:21129') 'differ from the container ports'
Assert-Rejected @('--run-for','100','--client-forward','1119','--client-forward','1129:21129') 'differ from the container ports'
# UDP: same container port as its client, once, for both or neither.
Assert-Rejected @('--run-for','100','--client-forward','1119:21119','--client-udp-forward','1129:21120','--client-forward','1129:21129','--client-udp-forward','1129:21120') 'Pair UDP forward must follow its client'
Assert-Rejected @('--run-for','100','--client-udp-forward','1119:21120','--client-forward','1119:21119','--client-forward','1129:21129') 'Pair UDP forward must follow its client'
Assert-Rejected @('--run-for','100','--client-forward','1119:21119','--client-udp-forward','1119:21120','--client-udp-forward','1119:21121','--client-forward','1129:21129') 'Pair UDP forward must follow its client'
Assert-Rejected @('--run-for','100','--client-forward','1119:21119','--client-udp-forward','1119:21120','--client-forward','1129:21129') 'both clients or neither'
Assert-Rejected @('--run-for','100','--client-forward','1119:21119','--client-udp-forward','1119:1119','--client-forward','1129:21129','--client-udp-forward','1129:21120') 'differ from the container ports'
# Second-client delay: 0..180 and at least 30 seconds of the shared bound left.
Assert-Rejected (@('--run-for','300','--client-delay','181') + $pair) 'Second-client delay must be 0..180 seconds'
Assert-Rejected (@('--run-for','100','--client-delay','71') + $pair) 'leave at least 30 seconds'
Assert-Rejected (@('--run-for','29') + $pair) 'leave at least 30 seconds'
Assert-Rejected (@('--run-for','300','--client-delay','10','--client-delay','10') + $pair) 'Specify the second-client delay once'
# Client arguments are fixed by the launcher; unknown options are refused.
Assert-Rejected (@('--run-for','100') + $pair + @('--','--BNetServer=127.0.0.1:1119')) 'client arguments are fixed'
Assert-Rejected (@('--run-for','100','--forward','1119:21119') + $pair) 'client arguments are fixed'
Assert-Rejected (@('--run-for','100','--pair-dump','c3') + $pair) 'Pair dump selection must be'
# Dependencies match single mode.
Assert-Rejected (@('--run-for','100','--trust-socket-ca') + $pair) 'Native socket CA installation requires --trust-ca and --observe-tls'
Assert-Rejected (@('--run-for','100','--preload-practice-header') + $pair) 'Practice preload control requires'
Assert-Rejected (@('--run-for','100','--preload-practice-header') + $pairUdp) 'Practice preload control requires'
$modulusFixture = Join-Path ([IO.Path]::GetTempPath()) ('ow1-pair-modulus-test-' + [guid]::NewGuid() + '.modulus')
$certificateFixture = Join-Path ([IO.Path]::GetTempPath()) ('ow1-pair-cert-test-' + [guid]::NewGuid() + '.pem')
try {
    [byte[]]$publicBytes = New-Object byte[] 256
    $publicBytes[0] = 1; $publicBytes[255] = 128
    [IO.File]::WriteAllBytes($modulusFixture, $publicBytes)
    # Author-written framing fixture, not an actual certificate.
    Set-Content -LiteralPath $certificateFixture -Value "-----BEGIN CERTIFICATE-----`nfixture`n-----END CERTIFICATE-----" -Encoding ascii
    Assert-Rejected (@('--run-for','100','--trust-lobby-key',$modulusFixture) + $pair) 'requires bounded loopback'
    $full = @('--run-for','300','--client-delay','60','--trust-ca',$certificateFixture,'--observe-tls','--trust-socket-ca','--trust-lobby-key',$modulusFixture)
    Assert-Rejected ($full + $pair) $fingerprint 1
    Assert-Rejected ($full + @('--preload-practice-header') + $pairUdp) $fingerprint 1
    Assert-Rejected ($full + @('--trust-ca',$certificateFixture) + $pair) 'Specify one public CA certificate'
    Set-Content -LiteralPath $certificateFixture -Value "-----BEGIN CERTIFICATE-----`nfixture PRIVATE KEY`n-----END CERTIFICATE-----" -Encoding ascii
    Assert-Rejected (@('--run-for','100','--trust-ca',$certificateFixture) + $pair) 'without private keys'
    $publicBytes[0] = 0
    [IO.File]::WriteAllBytes($modulusFixture, $publicBytes)
    Assert-Rejected (@('--run-for','100','--trust-lobby-key',$modulusFixture) + $pair) 'must be odd and exactly 2048 bits'
} finally {
    Remove-Item -LiteralPath $modulusFixture -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $certificateFixture -Force -ErrorAction SilentlyContinue
}
if ((Get-Acl -LiteralPath $Launcher).Sddl -ne $beforeFile -or
    (Get-Acl -LiteralPath $folder).Sddl -ne $beforeFolder) { throw 'Rejected pair launch changed ACL' }
Write-Host 'Pair-mode argument guards and fingerprint ordering passed.'
