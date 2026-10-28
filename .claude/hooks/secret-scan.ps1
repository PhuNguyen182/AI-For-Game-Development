# PreToolUse Edit|Write|MultiEdit|NotebookEdit: block content that carries a secret shape.
. "$PSScriptRoot/common.ps1"

$in = Read-HookInput
if (-not $in) { exit 0 }
$t = $in.tool_input
$path = [string]($t.file_path ?? $t.notebook_path ?? '')
if ($path -match $script:SecretScanExempt) { exit 0 }

$parts = @($t.content, $t.new_string, $t.new_source)
if ($t.edits) { $parts += $t.edits | ForEach-Object { $_.new_string } }
$hits = Find-Secrets (($parts | Where-Object { $_ }) -join "`n")

if ($hits.Count -gt 0) {
    Block ("Blocked: secret-shaped value in $path`n  " + ($hits -join "`n  ") +
        "`nReference a credential id or secret store instead (rule core.md -> Security). " +
        "If it is a vendor-documented public id, ask the GD to write it.")
}
exit 0
