# Cross-session Unity Editor lock in <project>/.workflow/editor.lock.
#   acquire  PreToolUse Agent: an Editor-holding agent takes the lock; blocked if another session holds it.
#            A worktree dispatch (/feature lane A) never touches the Editor and takes no hold.
#   check    PreToolUse Bash/PowerShell `unity ...` and mcp__unity*: blocked if another session holds it,
#            or if the call comes from a linked worktree (lane A must not drive the main checkout's Editor).
#   release  SubagentStop: an Editor holder left in Play Mode or with compile errors is sent back once; else its hold drops.
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

# True when $path sits in a linked git worktree other than the project's own checkout (a /feature lane A agent).
# The project may itself be a linked worktree; only a different checkout counts.
function Get-GitHolder([string]$path) {
    $dir = $path
    while ($dir) {
        if (Test-Path (Join-Path $dir '.git')) { return [IO.Path]::GetFullPath($dir).TrimEnd('\', '/') }
        $parent = Split-Path $dir
        if ($parent -eq $dir) { break }
        $dir = $parent
    }
    return $null
}

function Test-LaneWorktree([string]$path) {
    if (-not $path) { return $false }
    $holder = Get-GitHolder $path
    if (-not $holder -or $holder -ieq (Get-GitHolder $root)) { return $false }
    $git = Join-Path $holder '.git'
    return ((Test-Path $git -PathType Leaf) -and ((Get-Content $git -Raw) -match 'gitdir:.*[\\/]worktrees[\\/]'))
}

# First value of a property anywhere in parsed JSON (the CLI nests results differently per output format).
function Find-Prop($obj, [string]$name) {
    if ($null -eq $obj -or $obj -is [string] -or $obj -is [ValueType]) { return $null }
    foreach ($p in $obj.PSObject.Properties) {
        if ($p.Name -eq $name) { return $p.Value }
        $v = Find-Prop $p.Value $name
        if ($null -ne $v) { return $v }
    }
    return $null
}

function Get-UnityJson([string]$command) {
    $out = (& unity command $command status 2>$null | Out-String)
    $i = $out.IndexOf('{'); $j = $out.LastIndexOf('}')
    if ($i -lt 0 -or $j -le $i) { return $null }
    try { return $out.Substring($i, $j - $i + 1) | ConvertFrom-Json } catch { return $null }
}

# What an Editor-holding agent left wrong, or $null. No reachable Editor means nothing to check.
function Get-EditorProblem {
    if ($env:HOOK_TEST_EDITOR_STATE) {
        switch ($env:HOOK_TEST_EDITOR_STATE) { 'playing' { return 'Play Mode is still on' } 'compile' { return 'the project has compile errors' } default { return $null } }
    }
    if (-not (Get-Command unity -ErrorAction SilentlyContinue)) { return $null }
    Push-Location $root
    try {
        $mode = Find-Prop (Get-UnityJson 'editor') 'playMode'
        if ($mode -and $mode -ne 'stopped') { return "Play Mode is still $mode - run: unity command editor.playmode stop" }
        if ((Find-Prop (Get-UnityJson 'console') 'compilationFailed') -eq $true) { return 'the project has compile errors - see: unity command console get --level error' }
        return $null
    }
    finally { Pop-Location }
}

switch ($Mode) {
    'acquire' {
        $agent = [string]$in.tool_input.subagent_type
        if ($Holders -notcontains $agent -or [string]$in.tool_input.isolation -eq 'worktree') { exit 0 }
        if ($foreign) { Refuse }
        $holds = if ($lock -and $lock.session -eq $session) { @($lock.holds) } else { @() }
        if ($lock -and $lock.session -ne $session) { $lock = $null }
        # @() again: an `if` expression unrolls a one-item array to a string, and string + string concatenates.
        Save (@($holds) + $agent)
    }
    'check' {
        $unityCall = ([string]$in.tool_name -match '^mcp__unity') -or
            ([string]$in.tool_input.command -match '(^|[;&|]\s*|\bcd\b.*?&&\s*)unity\s')
        if (-not $unityCall) { exit 0 }
        if (Test-LaneWorktree ([string]$in.cwd)) {
            Block ('No Unity CLI or MCP call from a worktree: it would drive the main checkout''s Editor while lane B holds it. ' +
                'Verify with dotnet build / dotnet test on the mirror (/feature step 4, Lanes).')
        }
        if ($foreign) { Refuse }
    }
    'release' {
        if (-not $lock -or $lock.session -ne $session) { exit 0 }
        # A lane A agent took no hold; its stop must neither check lane B's Editor nor drop a same-type lane B hold.
        if (Test-LaneWorktree ([string]$in.cwd)) { exit 0 }
        # Exit 2 keeps the agent running so it cleans up; stop_hook_active means it was already told once.
        if (@($lock.holds) -contains [string]$in.agent_type -and -not $in.stop_hook_active) {
            $problem = Get-EditorProblem
            if ($problem) { Block "Before you return: $problem. Leave the Editor clean (skill agent-protocol)." }
        }
        $holds = [System.Collections.Generic.List[string]]@($lock.holds)
        [void]$holds.Remove([string]$in.agent_type)
        Save $holds.ToArray()
    }
    'clear' {
        if ($lock -and $lock.session -eq $session) { Remove-Item $lockPath -ErrorAction SilentlyContinue }
    }
}
exit 0
