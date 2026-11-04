#requires -Version 7
# Install or refresh the framework in a Unity project, from this framework checkout.
#   pwsh -File <framework>/.claude/tools/install-framework.ps1 -Target <unity-project-repo-root>
# -Target defaults to the current directory. Later updates: pwsh -File .claude/tools/update-framework.ps1
[CmdletBinding()]
param(
    [string]$Target = (Get-Location).Path,
    [switch]$DryRun,
    [switch]$Force
)
$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$url = (git -C $root remote get-url origin 2>$null)
$url = ([string]$url) -replace '^(https?://)[^/@]+@', '$1'
$ref = ([string](git -C $root branch --show-current 2>$null)).Trim()
$commit = ([string](git -C $root rev-parse HEAD 2>$null)).Trim()
if (-not $url) { Write-Warning 'The framework checkout has no origin remote: update-framework.ps1 will need -Source.' }

& (Join-Path $PSScriptRoot 'framework-sync.ps1') -Mode Install -SourceRoot $root -Target $Target `
    -SourceUrl $url -SourceRef $ref -SourceCommit $commit -DryRun:$DryRun -Force:$Force
