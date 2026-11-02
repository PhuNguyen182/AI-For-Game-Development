#requires -Version 7
# Update the framework in this Unity project from the source recorded at install time.
#   pwsh -File .claude/tools/update-framework.ps1
# -Source / -Ref override the recorded source (and are recorded in turn).
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Force,
    [string]$Source,
    [string]$Ref
)
$ErrorActionPreference = 'Stop'

$target = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$manifestPath = Join-Path $target '.claude/.framework-manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "No .claude/.framework-manifest.json in $target. Install first: pwsh -File <framework>/.claude/tools/install-framework.ps1 -Target $target"
}
$m = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json -AsHashtable
$url = if ($Source) { $Source } else { [string]$m.source.url }
$ref = if ($PSBoundParameters.ContainsKey('Ref')) { $Ref } else { [string]$m.source.ref }
if (-not $url) { throw 'No source URL recorded. Pass -Source <git url>.' }

$tmp = Join-Path ([IO.Path]::GetTempPath()) ("aigd-framework-" + [guid]::NewGuid().ToString('N'))
try {
    $gitArgs = @('clone', '--depth', '1', '--no-hardlinks', '--quiet')
    if ($ref) { $gitArgs += '--branch', $ref }
    $gitArgs += $url, $tmp
    git @gitArgs
    if ($LASTEXITCODE -ne 0) { throw "git clone failed for $url" }
    $commit = ([string](git -C $tmp rev-parse HEAD)).Trim()
    # Run the fresh copy of the sync script: this project's copy is among the files being replaced.
    & (Join-Path $tmp '.claude/tools/framework-sync.ps1') -Mode Update -SourceRoot $tmp -Target $target `
        -SourceUrl $url -SourceRef $ref -SourceCommit $commit -DryRun:$DryRun -Force:$Force
}
finally {
    if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue }
}
