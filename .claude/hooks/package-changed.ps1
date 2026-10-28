# PostToolUse: a Unity package was added, removed or upgraded -> remind the supply-chain check and the tech-stack row.
. "$PSScriptRoot/common.ps1"

$in = Read-HookInput
if (-not $in) { exit 0 }
$path = [string](First $in.tool_input.file_path '')
$cmd = [string](First $in.tool_input.command '')
$changed = ($path -match '[\\/]Packages[\\/]manifest\.json$') -or ($cmd -match '\bunity\s+command\s+package\s+(add|remove)\b')
if (-not $changed) { exit 0 }

$msg = 'A Unity package changed. A third-party package needs security-reviewer (skill secret-and-supply-chain-scan) ' +
    'before it lands (rule core.md), and docs/tech-stack.md needs its row updated in the same commit.'
@{ hookSpecificOutput = @{ hookEventName = 'PostToolUse'; additionalContext = $msg } } | ConvertTo-Json -Compress
exit 0
