# PostToolUse Edit|Write: after a change under .claude/, run the layer verifier on that file.
. "$PSScriptRoot/common.ps1"

$in = Read-HookInput
if (-not $in) { exit 0 }
$raw = [string](First $in.tool_input.file_path '')
if (-not $raw) { exit 0 }
# Resolved before every match: '.claude/worktrees/../agents/x.md' is the agent file, not a worktree write.
$path = [IO.Path]::GetFullPath($raw)
if ($path -notmatch '[\\/]\.claude[\\/]') { exit 0 }
# A write inside an agent worktree of this layer (/feature lane A) is that checkout's own work, not a change to the
# layer. Relative to this layer's root, so a layer that itself sits in a worktree is still verified on edit.
$layerRoot = (([IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))) -replace '\\', '/').TrimEnd('/') + '/'
$rel = $path -replace '\\', '/'
if ($rel.StartsWith($layerRoot, [StringComparison]::OrdinalIgnoreCase) -and $rel.Substring($layerRoot.Length) -match '^\.claude/worktrees/') { exit 0 }

$verifier = Join-Path $PSScriptRoot '../skills/verify-layer/scripts/verify.ps1'
if (-not (Test-Path -LiteralPath $verifier)) { exit 0 }

$out = & $verifier -File $path *>&1
if ($LASTEXITCODE -ne 0) {
    Block ("verify-layer failed after editing ${raw}:`n" + ($out -join "`n"))
}
exit 0
