# Cross-session Unity Editor lock in <project>/.workflow/editor.lock.
#   acquire  PreToolUse Agent: an Editor-holding agent takes the lock; blocked if another session holds it.
#   check    PreToolUse Bash/PowerShell `unity ...`: blocked if another session holds it.
#   release  SubagentStop: drops that agent's hold.
#   clear    Stop / SessionEnd: drops every hold this session owns.
param([Parameter(Mandatory)][ValidateSet('acquire', 'check', 'release', 'clear')][string]$Mode)
. "$PSScriptRoot/common.ps1"

$Holders = 'csharp-engineer', 'gameplay-engineer', 'ui-engineer', 'unity-performance-engineer', 'technical-artist',
    'netcode-engineer', 'sdk-platform-engineer', 'backend-engineer', 'qa-automation-engineer', 'playtest-tester',
    'performance-qa-engineer', 'build-release-engineer', 'rd-engineer', 'ci-cd-engineer', 'git-expert'
$StaleHours = 3

$in = Read-HookInput
if (-not $in) { exit 0 }
$root = First $env:CLAUDE_PROJECT_DIR ([string]$in.cwd)
if (-not (Test-Path (Join-Path $root 'Assets'))) { exit 0 }
$lockPath = Join-Path $root '.workflow/editor.lock'
$session = [string]$in.session_id

$lock = $null
if (Test-Path $lockPath) { try { $lock = Get-Content $lockPath -Raw -Encoding UTF8 | ConvertFrom-Json } catch { $lock = $null } }
$now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$foreign = $lock -and $lock.session -ne $session -and (($now - [long]$lock.updatedUnix) / 3600) -lt $StaleHours

function Save($holds) {
    if (-not $holds -or $holds.Count -eq 0) { Remove-Item $lockPath -ErrorAction SilentlyContinue; return }
    New-Item -ItemType Directory -Force (Split-Path $lockPath) | Out-Null
    [ordered]@{ session = $session; holds = @($holds); since = (First $lock.since (Get-Date).ToUniversalTime().ToString('o'))
        updated = (Get-Date).ToUniversalTime().ToString('o'); updatedUnix = $now } | ConvertTo-Json | Set-Content $lockPath
}

function Refuse {
    Block ("Unity Editor is held by another Claude session ($($lock.session), agents: $($lock.holds -join ', '), since $($lock.since)). " +
        'One Editor, one holder (rule core.md). Wait for it to finish. If that session is gone: confirm with ' +
        '"unity command editor status", then ask the GD before deleting .workflow/editor.lock.')
}

switch ($Mode) {
    'acquire' {
        $agent = [string]$in.tool_input.subagent_type
        if ($Holders -notcontains $agent) { exit 0 }
        if ($foreign) { Refuse }
        $holds = if ($lock -and $lock.session -eq $session) { @($lock.holds) } else { @() }
        if ($lock -and $lock.session -ne $session) { $lock = $null }
        Save ($holds + $agent)
    }
    'check' {
        if ([string]$in.tool_input.command -notmatch '(^|[;&|]\s*|\bcd\b.*?&&\s*)unity\s') { exit 0 }
        if ($foreign) { Refuse }
    }
    'release' {
        if (-not $lock -or $lock.session -ne $session) { exit 0 }
        $holds = [System.Collections.Generic.List[string]]@($lock.holds)
        [void]$holds.Remove([string]$in.agent_type)
        Save $holds.ToArray()
    }
    'clear' {
        if ($lock -and $lock.session -eq $session) { Remove-Item $lockPath -ErrorAction SilentlyContinue }
    }
}
exit 0
