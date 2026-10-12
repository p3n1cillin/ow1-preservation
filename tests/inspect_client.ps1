$ErrorActionPreference = 'Stop'
$inspect = Join-Path (Split-Path $PSScriptRoot -Parent) 'scripts\Inspect-Client.ps1'
$folder = Join-Path ([IO.Path]::GetTempPath()) ('ow1-inspect-' + [Guid]::NewGuid())
New-Item -ItemType Directory -Path $folder | Out-Null
try {
    $path = Join-Path $folder 'synthetic.exe'
    $bytes = [byte[]]::new(512)
    [BitConverter]::GetBytes([uint16]0x5a4d).CopyTo($bytes,0)
    [BitConverter]::GetBytes([int32]128).CopyTo($bytes,0x3c)
    [BitConverter]::GetBytes([uint32]0x4550).CopyTo($bytes,128)
    [BitConverter]::GetBytes([uint16]0x8664).CopyTo($bytes,132)
    [BitConverter]::GetBytes([uint16]240).CopyTo($bytes,148)
    [BitConverter]::GetBytes([uint16]0x20b).CopyTo($bytes,152)
    [IO.File]::WriteAllBytes($path,$bytes)
    $result = & $inspect -Path $path | ConvertFrom-Json
    if ($result.Architecture -ne 'x64' -or $result.SHA256.Length -ne 64 -or $result.Bytes -ne 512) { throw 'Valid synthetic PE inspection failed.' }
    $retail = Join-Path $folder '_retail_'
    New-Item -ItemType Directory -Path $retail | Out-Null
    [IO.File]::WriteAllBytes((Join-Path $retail 'Overwatch.exe'),$bytes)
    [IO.File]::WriteAllText((Join-Path $folder '.build.info'), "Active!DEC:1|Version!STRING:0|Build Key!HEX:16`n1|1.74.0.0.104319|786a31729ba1c684a5c80fbaf7cb92b8`n")
    $result = & $inspect -Path $folder | ConvertFrom-Json
    if (!$result.BuildInfoPresent -or $result.StorageRoot -ne $folder -or
        $result.DeclaredBuildVersion -ne '1.74.0.0.104319' -or
        $result.BuildConfigKey -ne '786a31729ba1c684a5c80fbaf7cb92b8') { throw 'Retail parent build metadata was not found.' }
    [IO.File]::WriteAllBytes($path,[byte[]]@(0,1,2))
    $rejected = $false
    try { & $inspect -Path $path | Out-Null } catch { $rejected = $true }
    if (!$rejected) { throw 'Truncated file was accepted.' }
    [IO.File]::WriteAllBytes($path,$bytes)
    [BitConverter]::GetBytes([int32]2147483647).CopyTo($bytes,0x3c)
    [IO.File]::WriteAllBytes($path,$bytes)
    $rejected = $false
    try { & $inspect -Path $path | Out-Null } catch { $rejected = $true }
    if (!$rejected) { throw 'Out-of-file PE offset was accepted.' }
    Write-Host 'PASS: read-only PE inspection, truncated file, invalid offset'
} finally {
    # Only remove the uniquely created temporary fixture files.
    Remove-Item -LiteralPath (Join-Path $folder 'synthetic.exe')
    if (Test-Path -LiteralPath (Join-Path $folder '_retail_\Overwatch.exe')) { Remove-Item -LiteralPath (Join-Path $folder '_retail_\Overwatch.exe') }
    if (Test-Path -LiteralPath (Join-Path $folder '_retail_')) { Remove-Item -LiteralPath (Join-Path $folder '_retail_') }
    if (Test-Path -LiteralPath (Join-Path $folder '.build.info')) { Remove-Item -LiteralPath (Join-Path $folder '.build.info') }
    Remove-Item -LiteralPath $folder
}
