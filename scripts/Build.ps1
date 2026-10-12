[CmdletBinding()]
param(
    [string]$BuildRoot = (Join-Path $env:LOCALAPPDATA 'OW1-preservation-build'),
    [switch]$SkipDependencies,
    [switch]$ServerOnly
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$BuildRoot = [IO.Path]::GetFullPath($BuildRoot)
New-Item -ItemType Directory -Force -Path $BuildRoot | Out-Null
function Invoke-Checked([string]$Program, [string[]]$Arguments, [string]$Log) {
    Write-Host "Running $Program (log: $Log)"
    & $Program @Arguments *> $Log
    if ($LASTEXITCODE -ne 0) {
        Get-Content -LiteralPath $Log -Tail 60
        throw "$Program failed with exit code $LASTEXITCODE"
    }
}
Push-Location $repo
try {
    $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
    if (!(Test-Path -LiteralPath $vswhere)) { throw 'Install Visual Studio 2022 C++ build tools and Windows SDK.' }
    $vs = & $vswhere -products '*' -version '[17.0,18.0)' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath -latest
    if (!$vs) { throw 'Visual Studio 2022 with the x64 C++ tools is required.' }
    $vcpkgRoot = Join-Path $BuildRoot 'vcpkg'
    $installed = Join-Path $BuildRoot 'installed'
    if (!$SkipDependencies) {
        Invoke-Checked 'git' @('submodule','update','--init','external/vcpkg','external/imnodes') (Join-Path $BuildRoot 'submodules.log')
        $pinned = (& git rev-parse HEAD:external/vcpkg).Trim()
        if ($LASTEXITCODE) { throw 'Cannot resolve pinned vcpkg revision.' }
        if (!(Test-Path -LiteralPath $vcpkgRoot)) {
            # Local executables avoid Windows restrictions on launching from UNC/mapped drives.
            Invoke-Checked 'git' @('-C','external/vcpkg','worktree','add','--detach',$vcpkgRoot,$pinned) (Join-Path $BuildRoot 'vcpkg-worktree.log')
        }
        $gitMarker = Get-Item -Force -LiteralPath (Join-Path $vcpkgRoot '.git')
        if (!$gitMarker.PSIsContainer) {
            # A detached worktree may inherit the network share's owner SID.
            # Read its revision without changing Git's global ownership checks.
            $gitDirectory = (Get-Content -LiteralPath $gitMarker.FullName -Raw).Trim() -replace '^gitdir: ', ''
            $actual = (Get-Content -LiteralPath (Join-Path $gitDirectory 'HEAD') -Raw).Trim()
        } else {
            $revision = & git -C $vcpkgRoot rev-parse HEAD
            if ($LASTEXITCODE -ne 0) { throw 'Cannot read cached vcpkg revision.' }
            $actual = $revision.Trim()
        }
        if ($actual -ne $pinned) { throw "Cached vcpkg is $actual, expected $pinned. Choose a fresh BuildRoot." }
        if (!(Test-Path -LiteralPath (Join-Path $vcpkgRoot 'vcpkg.exe'))) {
            Invoke-Checked 'powershell.exe' @('-NoProfile','-ExecutionPolicy','Bypass','-File',(Join-Path $vcpkgRoot 'scripts\bootstrap.ps1'),'-disableMetrics') (Join-Path $BuildRoot 'vcpkg-bootstrap.log')
        }
        $manifest = if ($ServerOnly) { $repo } else { Join-Path $repo 'prometheus' }
        Invoke-Checked (Join-Path $vcpkgRoot 'vcpkg.exe') @('install','--triplet','x64-windows',"--x-manifest-root=$manifest","--x-install-root=$installed",'--disable-metrics') (Join-Path $BuildRoot 'dependencies.log')
    }
    Invoke-Checked 'cmake' @('-S',$repo,'-B',(Join-Path $BuildRoot 'relay'),'-G','Visual Studio 17 2022','-A','x64',"-DCMAKE_TOOLCHAIN_FILE=$vcpkgRoot/scripts/buildsystems/vcpkg.cmake","-DVCPKG_INSTALLED_DIR=$installed",'-DVCPKG_MANIFEST_INSTALL=OFF') (Join-Path $BuildRoot 'configure.log')
    Invoke-Checked 'cmake' @('--build',(Join-Path $BuildRoot 'relay'),'--config','Release','--parallel','4') (Join-Path $BuildRoot 'relay-build.log')
    Invoke-Checked 'ctest' @('--test-dir',(Join-Path $BuildRoot 'relay'),'-C','Release','--output-on-failure') (Join-Path $BuildRoot 'tests.log')
    if (!$ServerOnly) {
        Invoke-Checked (Join-Path $vs 'MSBuild\Current\Bin\MSBuild.exe') @('prometheus/prometheus.vcxproj','/p:Configuration=Release','/p:Platform=x64',"/p:VcpkgRoot=$vcpkgRoot\","/p:VcpkgInstalledDir=$installed\",'/p:VcpkgManifestInstall=false',"/p:IntDir=$BuildRoot\prometheus-obj\","/p:OutDir=$BuildRoot\client\",'/m','/nologo','/verbosity:minimal') (Join-Path $BuildRoot 'client-build.log')
        Invoke-Checked 'dotnet' @('build','patcher/patcher.csproj','-c','Release','--nologo','-o',(Join-Path $BuildRoot 'patcher')) (Join-Path $BuildRoot 'patcher-build.log')
    }
    Write-Host "Build and tests passed. Relay: $BuildRoot\relay\Release\ow1-relay.exe"
} finally { Pop-Location }
