# Stop / SessionEnd: copy this session's turns into .memory/traces (deterministic, no LLM). Best effort, never blocks.
. "$PSScriptRoot/common.ps1"

$in = Read-HookInput
if (-not $in -or -not $in.transcript_path -or $env:MEM_CAPTURE -eq '0') { exit 0 }
$root = Get-ProjectRoot $in
Invoke-Mem $root @('capture', '--transcript', [string]$in.transcript_path, '--session', [string]$in.session_id) | Out-Null
exit 0
