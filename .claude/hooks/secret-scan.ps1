# PreToolUse Edit|Write|MultiEdit|NotebookEdit: block content that carries a secret shape.
. "$PSScriptRoot/common.ps1"
# Fail closed: an unexpected error must block the write, not let it through unscanned.
trap { Block "Blocked: secret scan failed ($_) - the write was not scanned." }

$in = Read-HookInput
if (-not $in) { Block 'Blocked: secret scan received no readable hook input - the write was not scanned.' }
$t = $in.tool_input
$path = [string](First $t.file_path $t.notebook_path '')
if (Test-SecretScanExempt $path (Get-ProjectRoot $in)) { exit 0 }

$parts = @($t.content, $t.new_string, $t.new_source)
if ($t.edits) { $parts += $t.edits | ForEach-Object { $_.new_string } }
$hits = Find-Secrets (($parts | Where-Object { $_ }) -join "`n")

if ($hits.Count -gt 0) {
    Block ("Blocked: secret-shaped value in $path`n  " + ($hits -join "`n  ") +
        "`nReference a credential id or secret store instead (rule core.md -> Security). " +
        "If it is a vendor-documented public id, ask the GD to write it.")
}
exit 0
