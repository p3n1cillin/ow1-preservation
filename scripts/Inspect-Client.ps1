[CmdletBinding()]
param([Parameter(Mandatory)][string]$Path)
$ErrorActionPreference = 'Stop'
$resolved = (Resolve-Path -LiteralPath $Path).Path
if ((Get-Item -LiteralPath $resolved).PSIsContainer) {
    $exe = @('GameClientApp.exe','Overwatch.exe','_retail_\Overwatch.exe') |
        ForEach-Object { Join-Path $resolved $_ } | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (!$exe) { throw 'No recognized client executable in this folder.' }
} else { $exe = $resolved }
$stream = [IO.File]::OpenRead($exe)
$reader = [IO.BinaryReader]::new($stream)
try {
    if ($stream.Length -lt 64 -or $reader.ReadUInt16() -ne 0x5a4d) { throw 'Not a DOS/PE executable.' }
    $stream.Position = 0x3c
    $offset = $reader.ReadInt32()
    if ($offset -lt 64 -or $offset -gt ($stream.Length - 26)) { throw 'Invalid PE header offset.' }
    $stream.Position = $offset
    if ($reader.ReadUInt32() -ne 0x4550) { throw 'Missing PE signature.' }
    $machine = $reader.ReadUInt16()
    $sections = $reader.ReadUInt16()
    $stream.Position = $offset + 20
    $optionalSize = $reader.ReadUInt16()
    if ($optionalSize -lt 2 -or ($offset + 24 + $optionalSize + 40 * $sections) -gt $stream.Length) { throw 'Truncated PE header/sections.' }
    $stream.Position = $offset + 24
    $magic = $reader.ReadUInt16()
    $architecture = switch ($machine) { 0x8664 { 'x64' } 0x14c { 'x86' } default { 'unknown' } }
    if (($machine -eq 0x8664 -and $magic -ne 0x20b) -or ($machine -eq 0x14c -and $magic -ne 0x10b)) { throw 'PE machine and optional header disagree.' }
} finally { $reader.Dispose() }
$version = [Diagnostics.FileVersionInfo]::GetVersionInfo($exe)
$signature = Get-AuthenticodeSignature -LiteralPath $exe
$folder = Split-Path $exe -Parent
$storageRoot = $folder
if ((Split-Path $folder -Leaf) -eq '_retail_' -and
    (Test-Path -LiteralPath (Join-Path (Split-Path $folder -Parent) '.build.info'))) {
    $storageRoot = Split-Path $folder -Parent
}
$buildInfo = Join-Path $storageRoot '.build.info'
$declaredVersion = $null
$buildConfigKey = $null
if (Test-Path -LiteralPath $buildInfo -PathType Leaf) {
    $lines = Get-Content -LiteralPath $buildInfo
    if ($lines.Count -ge 2) {
        $names = $lines[0].Split('|')
        foreach ($line in $lines | Select-Object -Skip 1) {
            $values = $line.Split('|')
            if ($values.Count -ne $names.Count) { continue }
            $row = @{}
            for ($n = 0; $n -lt $names.Count; $n++) { $row[$names[$n].Split('!')[0]] = $values[$n] }
            if ($row['Active'] -eq '1') {
                $declaredVersion = $row['Version']; $buildConfigKey = $row['Build Key']; break
            }
        }
    }
}
[pscustomobject]@{
    Path = $exe
    Bytes = (Get-Item -LiteralPath $exe).Length
    SHA256 = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
    Architecture = $architecture
    PESections = $sections
    FileVersion = $version.FileVersion
    FixedFileVersion = if ($version.FileMajorPart -or $version.FileMinorPart -or $version.FileBuildPart -or $version.FilePrivatePart) {
        '{0}.{1}.{2}.{3}' -f $version.FileMajorPart,$version.FileMinorPart,$version.FileBuildPart,$version.FilePrivatePart
    } else { $null }
    ProductVersion = $version.ProductVersion
    SignatureStatus = $signature.Status.ToString()
    Signer = if ($signature.SignerCertificate) { $signature.SignerCertificate.Subject } else { $null }
    StorageRoot = $storageRoot
    BuildInfoPresent = (Test-Path -LiteralPath $buildInfo)
    DeclaredBuildVersion = $declaredVersion
    BuildConfigKey = $buildConfigKey
    Compatibility = 'Unverified; inspection does not establish hook compatibility or launch the client.'
} | ConvertTo-Json
