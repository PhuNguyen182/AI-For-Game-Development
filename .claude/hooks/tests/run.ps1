<#
.SYNOPSIS
End-to-end tests for the framework hooks: feeds each hook the JSON Claude Code sends and checks the exit code.
Runs under the same PowerShell that runs it (pwsh 7 on Windows/macOS/Linux, or Windows PowerShell 5.1). Exit 1 on any failure.
#>
# Continue, not Stop: Windows PowerShell 5.1 turns a native command's stderr into a terminating error under Stop.
$ErrorActionPreference = 'Continue'
$hooks = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$shell = (Get-Process -Id $PID).Path
$tmp = Join-Path ([IO.Path]::GetTempPath()) ('hooktest-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
$failures = 0
# Built at runtime so this file never holds a secret-shaped literal.
$fakeKey = 'AK' + 'IA' + ('Q' * 16)

function Invoke-Hook([string]$Script, [hashtable]$Payload, [string[]]$HookArgs = @()) {
    $json = $Payload | ConvertTo-Json -Depth 5 -Compress
    $out = $json | & $shell -NoProfile -NonInteractive -File (Join-Path $hooks $Script) @HookArgs 2>&1
    return @{ Code = $LASTEXITCODE; Out = ($out | Out-String) }
}

function Check([string]$Name, $Actual, $Expected) {
    if ($Actual -eq $Expected) { Write-Output "PASS  $Name" }
    else { Write-Output "FAIL  $Name (got $Actual, expected $Expected)"; $script:failures++ }
}

function New-Repo([string]$Path) {
    New-Item -ItemType Directory -Force (Join-Path $Path 'Assets') | Out-Null
    git -C $Path init -q 2>&1 | Out-Null
}

try {
    New-Item -ItemType Directory -Force $tmp | Out-Null
    Write-Output "Shell: $shell ($($PSVersionTable.PSVersion))"

    # secret-scan
    $r = Invoke-Hook 'secret-scan.ps1' @{ tool_name = 'Write'; tool_input = @{ file_path = "$tmp/Assets/Cfg.cs"; content = "var k = `"$fakeKey`";" } }
    Check 'secret-scan blocks a key shape' $r.Code 2
    $r = Invoke-Hook 'secret-scan.ps1' @{ tool_name = 'Write'; tool_input = @{ file_path = "$tmp/Assets/Cfg.cs"; content = 'var appId = "ca-app-pub-123";' } }
    Check 'secret-scan allows clean content' $r.Code 0
    $r = Invoke-Hook 'secret-scan.ps1' @{ tool_name = 'Edit'; tool_input = @{ file_path = "$tmp/.claude/hooks/x.ps1"; new_string = $fakeKey } }
    Check 'secret-scan exempts the hooks folder' $r.Code 0

    # secret patterns: missing or empty file fails closed (run against a copy of the hooks)
    $hk = Join-Path $tmp 'hookcopy'
    New-Item -ItemType Directory -Force $hk | Out-Null
    Copy-Item (Join-Path $hooks 'common.ps1'), (Join-Path $hooks 'secret-scan.ps1') $hk
    $clean = @{ tool_name = 'Write'; tool_input = @{ file_path = "$tmp/Assets/C.cs"; content = 'class C {}' } }
    function ScanCopy { $json = $clean | ConvertTo-Json -Depth 5 -Compress; $json | & $shell -NoProfile -NonInteractive -File (Join-Path $hk 'secret-scan.ps1') 2>&1 | Out-Null; $LASTEXITCODE }
    Check 'secret-scan blocks when the patterns file is missing' (ScanCopy) 2
    Set-Content (Join-Path $hk 'secret-patterns.txt') '# only a comment'
    Check 'secret-scan blocks when the patterns file is empty' (ScanCopy) 2
    Set-Content (Join-Path $hk 'secret-patterns.txt') ((Get-Content (Join-Path $hooks 'secret-patterns.txt')) + "broken`t([unclosed")
    Check 'secret-scan blocks when a pattern is an invalid regex' (ScanCopy) 2
    Copy-Item (Join-Path $hooks 'secret-patterns.txt') $hk -Force
    Check 'secret-scan passes clean content with the real file' (ScanCopy) 0
    $r = 'not json' | & $shell -NoProfile -NonInteractive -File (Join-Path $hooks 'secret-scan.ps1') 2>&1 | Out-String
    Check 'malformed hook input exits quietly' ($LASTEXITCODE -eq 0 -and [string]::IsNullOrWhiteSpace($r)) $true
    . (Join-Path $hooks 'common.ps1')
    Check 'loopback: [::1] counts' (Test-LoopbackUrl 'http://[::1]:9200') $true
    Check 'loopback: localhost@evil.test does not' (Test-LoopbackUrl 'http://localhost@evil.test:9200') $false
    Check 'loopback: unparsable URL does not' (Test-LoopbackUrl 'http:\\bad url') $false
    Check 'loopback: the name "loopback" does not' (Test-LoopbackUrl 'http://loopback:9200') $false
    Check 'loopback: decimal IPv4 does not' (Test-LoopbackUrl 'http://2130706433:9200') $false
    Check 'loopback: 127.0.0.1 with port counts' (Test-LoopbackUrl 'http://127.0.0.1:9200/') $true

    # pre-commit (path with a space, as Unity project folders often have)
    $repo = Join-Path $tmp 'Pilot Project'
    New-Repo $repo
    $commit = @{ tool_name = 'Bash'; cwd = $tmp; tool_input = @{ command = "git -C `"$repo`" commit -m x" } }
    Set-Content (Join-Path $repo 'Assets/A.cs') 'class A {}'
    git -C $repo add Assets/A.cs 2>&1 | Out-Null
    Check 'pre-commit blocks an asset without .meta' (Invoke-Hook 'pre-commit.ps1' $commit).Code 2
    Set-Content (Join-Path $repo 'Assets/A.cs.meta') 'guid: 1'
    git -C $repo add Assets/A.cs.meta 2>&1 | Out-Null
    Check 'pre-commit allows a paired asset' (Invoke-Hook 'pre-commit.ps1' $commit).Code 0
    Set-Content (Join-Path $repo 'Assets/Orphan.png.meta') 'guid: 2'
    git -C $repo add Assets/Orphan.png.meta 2>&1 | Out-Null
    Check 'pre-commit blocks an orphan .meta' (Invoke-Hook 'pre-commit.ps1' $commit).Code 2
    git -C $repo rm -q --cached Assets/Orphan.png.meta 2>&1 | Out-Null
    Set-Content (Join-Path $repo 'Assets/K.cs') "var k = `"$fakeKey`";"
    Set-Content (Join-Path $repo 'Assets/K.cs.meta') 'guid: 3'
    git -C $repo add Assets/K.cs Assets/K.cs.meta 2>&1 | Out-Null
    Check 'pre-commit blocks a staged secret' (Invoke-Hook 'pre-commit.ps1' $commit).Code 2
    git -C $repo rm -q --cached Assets/K.cs Assets/K.cs.meta 2>&1 | Out-Null
    New-Item -ItemType Directory -Force (Join-Path $repo '.memory/traces') | Out-Null
    $pw = 'pass' + 'word'
    Set-Content (Join-Path $repo '.memory/traces/t.jsonl') "{`"text`":`"$pw = \`"hunter2hunter2\`"`"}"
    git -C $repo add .memory/traces/t.jsonl 2>&1 | Out-Null
    Check 'pre-commit sees a quoted secret through JSON escaping' (Invoke-Hook 'pre-commit.ps1' $commit).Code 2
    git -C $repo rm -q --cached .memory/traces/t.jsonl 2>&1 | Out-Null
    git -C $repo add Assets/K.cs Assets/K.cs.meta 2>&1 | Out-Null
    foreach ($form in @(
            "git -C `"$repo`" -c user.name=t -c user.email=t@t commit -m x",
            "git -c core.x=y -C `"$repo`" commit -m x",
            "git -C `"$repo`" --no-pager commit -m x",
            "git --git-dir `"$repo/.git`" -C `"$repo`" commit -m x")) {
        Check "pre-commit sees through global options: $($form -replace [regex]::Escape($repo), '<repo>')" (Invoke-Hook 'pre-commit.ps1' @{ tool_name = 'PowerShell'; cwd = $tmp; tool_input = @{ command = $form } }).Code 2
    }
    Check 'pre-commit ignores git -c k=v log' (Invoke-Hook 'pre-commit.ps1' @{ tool_name = 'Bash'; cwd = $tmp; tool_input = @{ command = "git -C `"$repo`" -c a=b log" } }).Code 0
    Check 'pre-commit: commit -C <rev> is not a directory' (Invoke-Hook 'pre-commit.ps1' @{ tool_name = 'Bash'; cwd = $repo; tool_input = @{ command = 'git commit -C HEAD -m x' } }).Code 2
    Check 'pre-commit: an unresolvable -C falls back to cwd' (Invoke-Hook 'pre-commit.ps1' @{ tool_name = 'PowerShell'; cwd = $repo; tool_input = @{ command = 'git -C nowhere commit -m x' } }).Code 2
    Check 'pre-commit: plain commit from cwd' (Invoke-Hook 'pre-commit.ps1' @{ tool_name = 'Bash'; cwd = $repo; tool_input = @{ command = 'git commit -m x' } }).Code 2
    $leaf = Split-Path $repo -Leaf
    Check 'pre-commit: relative -C resolves against the session cwd' (Invoke-Hook 'pre-commit.ps1' @{ tool_name = 'Bash'; cwd = $tmp; tool_input = @{ command = "git -C `"$leaf`" commit -m x" } }).Code 2
    Check 'pre-commit: relative cd resolves against the session cwd' (Invoke-Hook 'pre-commit.ps1' @{ tool_name = 'Bash'; cwd = $tmp; tool_input = @{ command = "cd `"$leaf`" && git commit -m x" } }).Code 2
    foreach ($nc in @('git -c commit.gpgsign=false log -1', 'git commit-tree HEAD^{tree} -m x', 'git commit-graph write')) {
        Check "pre-commit ignores: $nc" (Invoke-Hook 'pre-commit.ps1' @{ tool_name = 'Bash'; cwd = $repo; tool_input = @{ command = $nc } }).Code 0
    }
    $cdForm = @{ tool_name = 'Bash'; cwd = $tmp; tool_input = @{ command = "cd `"$repo`" && git commit -m x" } }
    Check 'pre-commit resolves cd <dir> && git commit' (Invoke-Hook 'pre-commit.ps1' $cdForm).Code 2
    Check 'pre-commit ignores non-commit commands' (Invoke-Hook 'pre-commit.ps1' @{ tool_name = 'Bash'; tool_input = @{ command = 'git status' } }).Code 0

    # pre-commit: Git LFS for binaries and large files
    $lfs = Join-Path $tmp 'LfsRepo'
    New-Repo $lfs
    $lfsCommit = @{ tool_name = 'Bash'; cwd = $lfs; tool_input = @{ command = 'git commit -m x' } }
    [IO.File]::WriteAllBytes((Join-Path $lfs 'Assets/Icon.png'), [byte[]](137, 80, 78, 71, 13, 10, 26, 10))
    Set-Content (Join-Path $lfs 'Assets/Icon.png.meta') 'guid: 4'
    git -C $lfs add Assets/Icon.png Assets/Icon.png.meta 2>&1 | Out-Null
    Check 'pre-commit blocks a binary outside LFS' (Invoke-Hook 'pre-commit.ps1' $lfsCommit).Code 2
    git -C $lfs config claude.lfs off
    Check 'pre-commit honours claude.lfs off' (Invoke-Hook 'pre-commit.ps1' $lfsCommit).Code 0
    git -C $lfs config --unset claude.lfs
    Set-Content (Join-Path $lfs '.gitattributes') '*.png filter=lfs diff=lfs merge=lfs -text'
    git -C $lfs add .gitattributes 2>&1 | Out-Null
    Check 'pre-commit allows a binary tracked by LFS' (Invoke-Hook 'pre-commit.ps1' $lfsCommit).Code 0
    [IO.File]::WriteAllBytes((Join-Path $lfs 'big.txt'), (New-Object byte[] (6MB)))
    git -C $lfs add big.txt 2>&1 | Out-Null
    Check 'pre-commit blocks a large file outside LFS' (Invoke-Hook 'pre-commit.ps1' $lfsCommit).Code 2

    # pre-commit: .meta GUID changes
    $guid = Join-Path $tmp 'GuidRepo'
    New-Repo $guid
    $guidCommit = @{ tool_name = 'Bash'; cwd = $guid; tool_input = @{ command = 'git commit -m x' } }
    Set-Content (Join-Path $guid 'Assets/G.cs') 'class G {}'
    Set-Content (Join-Path $guid 'Assets/G.cs.meta') "fileFormatVersion: 2`nguid: 0123456789abcdef0123456789abcdef"
    git -C $guid add -A 2>&1 | Out-Null
    git -C $guid -c user.name=t -c user.email=t@t commit -q -m base 2>&1 | Out-Null
    Set-Content (Join-Path $guid 'Assets/G.cs.meta') "fileFormatVersion: 2`nguid: fedcba9876543210fedcba9876543210"
    git -C $guid add Assets/G.cs.meta 2>&1 | Out-Null
    Check 'pre-commit blocks a changed .meta GUID' (Invoke-Hook 'pre-commit.ps1' $guidCommit).Code 2
    Set-Content (Join-Path $guid 'Assets/G.cs.meta') "fileFormatVersion: 2`nguid: 0123456789abcdef0123456789abcdef`nlabels: []"
    git -C $guid add Assets/G.cs.meta 2>&1 | Out-Null
    Check 'pre-commit allows other .meta edits' (Invoke-Hook 'pre-commit.ps1' $guidCommit).Code 0

    # package-changed
    $r = Invoke-Hook 'package-changed.ps1' @{ tool_name = 'Edit'; tool_input = @{ file_path = "$tmp/Packages/manifest.json" } }
    Check 'package-changed reminds on a manifest edit' ($r.Out -match 'additionalContext') $true
    $r = Invoke-Hook 'package-changed.ps1' @{ tool_name = 'Bash'; tool_input = @{ command = 'unity command package add com.example.sdk' } }
    Check 'package-changed reminds on unity package add' ($r.Out -match 'additionalContext') $true
    $r = Invoke-Hook 'package-changed.ps1' @{ tool_name = 'Edit'; tool_input = @{ file_path = "$tmp/Assets/A.cs" } }
    Check 'package-changed stays quiet otherwise' ($r.Out -match 'additionalContext') $false

    # editor-lock
    $proj = Join-Path $tmp 'LockProject'
    New-Item -ItemType Directory -Force (Join-Path $proj 'Assets') | Out-Null
    $env:CLAUDE_PROJECT_DIR = $proj
    $lock = Join-Path $proj '.workflow/editor.lock'
    function Lock([string]$Session, [string]$Agent, [string]$Mode, [string]$Command = '') {
        (Invoke-Hook 'editor-lock.ps1' @{ session_id = $Session; agent_type = $Agent; tool_input = @{ subagent_type = $Agent; command = $Command } } @('-Mode', $Mode)).Code
    }
    Check 'lock: A takes it for an Editor holder' (Lock 'A' 'ui-engineer' 'acquire') 0
    Check 'lock: file written' (Test-Path $lock) $true
    Check 'lock: read-only agent passes' (Lock 'A' 'code-reviewer' 'acquire') 0
    Check 'lock: B blocked from an Editor holder' (Lock 'B' 'gameplay-engineer' 'acquire') 2
    Check 'lock: B blocked from unity commands' (Lock 'B' 'x' 'check' 'cd /p && unity command script recompile') 2
    Check 'lock: B free for other commands' (Lock 'B' 'x' 'check' 'git status') 0
    Lock 'A' 'code-reviewer' 'release' | Out-Null
    Check 'lock: read-only stop keeps it' (Test-Path $lock) $true
    Lock 'A' 'ui-engineer' 'release' | Out-Null
    Check 'lock: holder stop releases it' (Test-Path $lock) $false
    Check 'lock: B takes it after release' (Lock 'B' 'gameplay-engineer' 'acquire') 0
    Lock 'B' 'x' 'clear' | Out-Null
    Check 'lock: clear at turn end' (Test-Path $lock) $false
    Set-Content $lock (@{ session = 'C'; holds = @('ui-engineer'); since = 'old'; updated = 'old'; updatedUnix = 0 } | ConvertTo-Json)
    Check 'lock: stale lock can be taken' (Lock 'D' 'ui-engineer' 'acquire') 0
    Remove-Item $lock

    # editor-lock: an Editor holder must leave the Editor clean before it stops
    $stop = { param($active) (Invoke-Hook 'editor-lock.ps1' @{ session_id = 'E'; agent_type = 'playtest-tester'; stop_hook_active = $active } @('-Mode', 'release')).Code }
    Lock 'E' 'playtest-tester' 'acquire' | Out-Null
    $env:HOOK_TEST_EDITOR_STATE = 'playing'
    Check 'stop: holder left in Play Mode is sent back' (& $stop $false) 2
    Check 'stop: lock kept while it cleans up' (Test-Path $lock) $true
    Check 'stop: second stop is let through' (& $stop $true) 0
    Lock 'E' 'playtest-tester' 'acquire' | Out-Null
    $env:HOOK_TEST_EDITOR_STATE = 'compile'
    Check 'stop: holder with compile errors is sent back' (& $stop $false) 2
    $env:HOOK_TEST_EDITOR_STATE = 'clean'
    Check 'stop: clean Editor releases' (& $stop $false) 0
    Check 'stop: lock gone after a clean stop' (Test-Path $lock) $false
    Remove-Item Env:HOOK_TEST_EDITOR_STATE

    # session-start
    New-Item -ItemType Directory -Force (Join-Path $proj '.workflow/features') | Out-Null
    Set-Content (Join-Path $proj '.workflow/features/open-one.md') "# Open one`n`n- Status: Open`n- CP: build"
    Set-Content (Join-Path $proj '.workflow/features/done-one.md') "# Done one`n`n- Status: Closed`n- CP: CP4"
    $env:HOOK_TEST_XERJ = 'none'
    $r = Invoke-Hook 'session-start.ps1' @{}
    Check 'session-start lists the open feature' ($r.Out -match 'open-one') $true
    Check 'session-start skips closed features' ($r.Out -match 'done-one') $false
    Check 'session-start reports Grep without XERJ' ($r.Out -match 'Search: Grep') $true

    # memory: capture (Stop hook) and the session-start status line, against a copy of mem.py
    $memDir = Join-Path $proj '.claude/skills/mem/scripts'
    New-Item -ItemType Directory -Force $memDir, (Join-Path $proj '.claude/hooks') | Out-Null
    Copy-Item (Join-Path $hooks '../skills/mem/scripts/mem.py') $memDir
    Copy-Item (Join-Path $hooks 'secret-patterns.txt') (Join-Path $proj '.claude/hooks')
    $tr = Join-Path $tmp 'transcript.jsonl'
    $lines = @(
        @{ type = 'user'; timestamp = '2026-10-28T01:00:00Z'; message = @{ content = "Remember key $fakeKey" } },
        @{ type = 'assistant'; timestamp = '2026-10-28T01:00:01Z'; message = @{ content = @(@{ type = 'text'; text = 'Noted.' }) } }
    ) | ForEach-Object { $_ | ConvertTo-Json -Depth 6 -Compress }
    [IO.File]::WriteAllLines($tr, [string[]]$lines)
    $stopIn = @{ session_id = 'cafe0123-x'; transcript_path = $tr; cwd = $proj }
    $env:MEM_CAPTURE = '0'
    Invoke-Hook 'memory-capture.ps1' $stopIn | Out-Null
    Check 'capture honours MEM_CAPTURE=0' (Test-Path (Join-Path $proj '.memory/traces')) $false
    Remove-Item Env:MEM_CAPTURE
    Check 'capture exits 0' (Invoke-Hook 'memory-capture.ps1' $stopIn).Code 0
    $trace = Join-Path $proj '.memory/traces/2026/10/2026-10-28-cafe0123.jsonl'
    Check 'capture writes the session trace' (Test-Path $trace) $true
    $traceText = if (Test-Path $trace) { Get-Content $trace -Raw } else { '' }
    Check 'capture redacts the secret' ($traceText -match 'REDACTED' -and $traceText -notmatch $fakeKey) $true
    $env:HOOK_TEST_XERJ = 'up'
    $r = Invoke-Hook 'session-start.ps1' @{}
    Check 'session-start reports memory counts' ($r.Out -match 'Memory: T 2 turns/1 sessions') $true
    Check 'session-start reports XERJ up' ($r.Out -match 'Search: XERJ up, prefix lockproject') $true

    # search-guard: deny repo-wide content search while XERJ is up
    function Guard([hashtable]$Payload) { ((Invoke-Hook 'search-guard.ps1' $Payload).Out -match '"permissionDecision":"deny"') }
    function GrepIn([string]$Path, [string]$Mode = 'content') { @{ tool_name = 'Grep'; cwd = $proj; tool_input = @{ pattern = 'Foo'; path = $Path; output_mode = $Mode } } }
    function Shell([string]$Tool, [string]$Command) { @{ tool_name = $Tool; cwd = $proj; tool_input = @{ command = $Command } } }
    Check 'guard: Grep content over the repo denied' (Guard (GrepIn '')) $true
    Check 'guard: Grep content over a top folder denied' (Guard (GrepIn 'Assets')) $true
    Check 'guard: Grep content in a deep folder allowed' (Guard (GrepIn 'Assets/_Project/Scripts')) $false
    Check 'guard: ./Assets/ is a top folder, denied' (Guard (GrepIn './Assets/')) $true
    Check 'guard: .\ is the root, denied' (Guard (GrepIn '.\')) $true
    Check 'guard: Grep content in a file allowed' (Guard (GrepIn "$proj/Assets/A.cs")) $false
    Check 'guard: Grep in a hidden folder allowed' (Guard (GrepIn '.claude/skills')) $false
    Check 'guard: Grep file list allowed' (Guard (GrepIn '' 'files_with_matches')) $false
    Check 'guard: rg over the repo denied' (Guard (Shell 'Bash' 'rg -n Foo')) $true
    Check 'guard: cd && grep -rn . denied' (Guard (Shell 'Bash' 'cd /p && grep -rn Foo .')) $true
    Check 'guard: git grep denied' (Guard (Shell 'PowerShell' 'git grep Foo')) $true
    Check 'guard: Select-String -Recurse denied' (Guard (Shell 'PowerShell' 'Get-ChildItem -Recurse | Select-String Foo')) $true
    Check 'guard: rg in a file allowed' (Guard (Shell 'Bash' 'rg Foo Assets/A.cs')) $false
    Check 'guard: grep without -r allowed' (Guard (Shell 'Bash' 'grep Foo notes.txt')) $false
    Check 'guard: rg -l allowed' (Guard (Shell 'Bash' 'rg -l Foo')) $false
    Check 'guard: rg --files allowed' (Guard (Shell 'Bash' 'rg --files')) $false
    Check 'guard: grep -rl allowed' (Guard (Shell 'Bash' 'grep -rl Foo .')) $false
    Check 'guard: grep --recursive denied' (Guard (Shell 'Bash' 'grep --recursive Foo .')) $true
    Check 'guard: rg -C 3 still denied' (Guard (Shell 'Bash' 'rg -C 3 Foo')) $true
    Check 'guard: Select-String -SimpleMatch -Recurse denied' (Guard (Shell 'PowerShell' 'Get-ChildItem -Recurse | Select-String -SimpleMatch Foo')) $true
    Check 'guard: Select-String -List allowed' (Guard (Shell 'PowerShell' 'Get-ChildItem -Recurse | Select-String Foo -List')) $false
    New-Item -ItemType Directory -Force (Join-Path $proj '.claude/agents') | Out-Null
    Set-Content (Join-Path $proj '.claude/agents/code-reviewer.md') "---`nname: code-reviewer`ntools: Read, Grep, Glob`n---"
    Set-Content (Join-Path $proj '.claude/agents/ui-engineer.md') "---`nname: ui-engineer`ntools: Read, Grep, PowerShell`n---"
    $sub = GrepIn ''
    $sub.agent_type = 'code-reviewer'
    Check 'guard: shell-less subagent allowed' (Guard $sub) $false
    $sub.agent_type = 'ui-engineer'
    Check 'guard: subagent with a shell denied' (Guard $sub) $true
    Set-Content (Join-Path $proj '.claude/agents/all-tools.md') "---`nname: all-tools`nmodel: x`n---"
    $sub.agent_type = 'all-tools'
    Check 'guard: agent without a tools line has a shell' (Guard $sub) $true
    Set-Content (Join-Path $proj '.claude/agents/listed.md') "---`nname: listed`ntools:`n  - Read`n  - Grep`nmodel: x`n---"
    $sub.agent_type = 'listed'
    Check 'guard: YAML-list tools without a shell allowed' (Guard $sub) $false
    $env:HOOK_TEST_XERJ = 'down'
    Check 'guard: XERJ down allows everything' (Guard (GrepIn '')) $false
    Remove-Item Env:HOOK_TEST_XERJ
    $now = [long]([DateTime]::UtcNow - [DateTime]'1970-01-01').TotalSeconds
    Set-Content (Join-Path $proj '.memory/.state/xerj.json') "{`"state`":`"none`",`"at`":$now}"
    Check 'probe: a fresh none/down result is reused' ((Invoke-Hook 'session-start.ps1' @{}).Out -match 'Search: Grep\.') $true
    Set-Content (Join-Path $proj '.memory/.state/xerj.json') "{`"state`":`"none`",`"at`":$($now - 600)}"
    $env:XERJ_URL = 'http://127.0.0.1:1'
    $r = (Invoke-Hook 'session-start.ps1' @{}).Out
    $expect = if (Get-Command xerj -CommandType Application -ErrorAction SilentlyContinue) { 'node down' } else { 'Search: Grep\.' }
    Check 'probe: an expired result is probed again' ($r -match $expect) $true
    Set-Content (Join-Path $proj '.memory/.state/xerj.json') "{`"state`":`"up`",`"at`":$now}"
    Check 'probe: a cached up is never trusted' (Guard (GrepIn '')) $false
    $env:XERJ_URL = 'http://10.0.0.5:9200'
    Remove-Item (Join-Path $proj '.memory/.state/xerj.json')
    Check 'probe: a non-loopback node counts as no XERJ' ((Invoke-Hook 'session-start.ps1' @{}).Out -match 'not loopback') $true
    Remove-Item Env:XERJ_URL

    # round-cap ($proj is CLAUDE_PROJECT_DIR)
    $feat = Join-Path $proj '.workflow/features/demo.md'
    New-Item -ItemType Directory -Force (Split-Path $feat) | Out-Null
    function Feature([string]$Rounds, [string]$Gd = '', [string]$Status = 'Open') {
        Set-Content $feat "# Demo`n`n- Status: $Status`n- Size: M, Risk flag: no`n- Rounds: $Rounds`n`n## GD decisions`n$Gd`n`n## Spec`n" -Encoding UTF8
    }
    function Dispatch([string]$Brief) { (Invoke-Hook 'round-cap.ps1' @{ tool_name = 'Agent'; tool_input = @{ prompt = $Brief } } @('-Mode', 'dispatch')).Code }
    function EditState([string]$Path) { (Invoke-Hook 'round-cap.ps1' @{ tool_name = 'Edit'; tool_input = @{ file_path = $Path } } @('-Mode', 'edit')).Code }
    $brief = 'Fix the HUD. Feature file: .workflow/features/demo.md'
    Feature 'review 1/3, QA 0/2, rework 1/6'
    Check 'round-cap: under every cap dispatches' (Dispatch $brief) 0
    Check 'round-cap: under every cap edits quietly' (EditState $feat) 0
    Feature 'review 3/3, QA 0/2, rework 3/6'
    Check 'round-cap: at a cap still dispatches (architect + one more)' (Dispatch $brief) 0
    Check 'round-cap: at a cap the edit warns' (EditState $feat) 2
    Feature 'review 4/3, QA 0/2, rework 4/6'
    Check 'round-cap: past the review cap blocks' (Dispatch $brief) 2
    Feature 'review 1/3, QA 0/2, rework 7/6'
    Check 'round-cap: past the feature rework cap blocks' (Dispatch $brief) 2
    Feature 'review 4/5, QA 0/2, rework 4/6'
    Check 'round-cap: a raised cap without a GD record blocks' (Dispatch $brief) 2
    Feature 'review 4/5, QA 0/2, rework 4/6' '- 2026-10-29 extra round: review +2'
    Check 'round-cap: a raised cap with a GD record dispatches' (Dispatch $brief) 0
    Feature 'review 9/3, QA 0/2, rework 9/6' '' 'Closed'
    Check 'round-cap: a closed feature is not checked' (Dispatch $brief) 0
    Check 'round-cap: a brief naming no state passes' (Dispatch 'Explain the HUD') 0
    $bugs = Join-Path $proj '.workflow/bugs.md'
    function Bugs([string]$Status, [string]$Rounds) {
        Set-Content $bugs "# Bugs`n`n| ID | Title | Severity | Status | Feature | Owner | Regression test |`n|---|---|---|---|---|---|---|`n| BUG-0007 | HUD | Low | $Status | demo | ui | t |`n`n## BUG-0007 - HUD`n- Repro: x`n- Fix rounds: $Rounds`n" -Encoding UTF8
    }
    Bugs 'Reopened' '3/2'
    Check 'round-cap: a bug past its cap blocks' (Dispatch 'Fix BUG-0007') 2
    Check 'round-cap: bugs.md edit warns past the cap' (EditState $bugs) 2
    Bugs 'Reopened' '1/2'
    Check 'round-cap: a bug under its cap dispatches' (Dispatch 'Fix BUG-0007') 0
    Bugs 'Closed' '3/2'
    Check 'round-cap: a closed bug is not checked' (Dispatch 'Verify BUG-0007') 0
    Check 'round-cap: edits outside .workflow are ignored' (EditState "$proj/Assets/A.cs") 0

    # round-cap count: the ledger counts failed gates the state files missed
    $ledger = Join-Path $proj '.workflow/rounds.json'
    Remove-Item $ledger -ErrorAction SilentlyContinue
    function SubStop([string]$Agent, [string]$Brief, [string]$Return, [string]$Id, [switch]$Handback) {
        $t = Join-Path $tmp "agent-$Id.jsonl"
        $first = @{ type = 'user'; message = @{ role = 'user'; content = $Brief } } | ConvertTo-Json -Depth 5 -Compress
        $lines = @($first)
        $last = ''
        if ($Handback) { $lines += (@{ type = 'assistant'; message = @{ role = 'assistant'; content = @(@{ type = 'tool_use'; name = 'SubagentHandback'; input = @{ message = $Return } }) } } | ConvertTo-Json -Depth 6 -Compress) }
        else { $last = $Return }
        Set-Content $t $lines -Encoding UTF8
        (Invoke-Hook 'round-cap.ps1' @{ session_id = 'sess-1'; agent_type = $Agent; agent_id = $Id; agent_transcript_path = $t; last_assistant_message = $last } @('-Mode', 'count')).Code
    }
    function Count([string]$Key, [string]$Counter) { $o = Get-Content $ledger -Raw | ConvertFrom-Json; @($o.$Key.$Counter).Count }
    Feature 'review 0/3, QA 0/2, rework 0/6'
    $rb = 'Review round 1. Feature file: .workflow/features/demo.md'
    SubStop 'code-reviewer' $rb "Status: Done`nVerdict: Request changes" 'a1' | Out-Null
    SubStop 'security-reviewer' $rb "Status: Done`nVerdict: Blocked" 'a2' | Out-Null
    Check 'count: two gates blocking one round count once' (Count 'feature:demo' 'review') 1
    Check 'count: a blocked review round adds one rework' (Count 'feature:demo' 'rework') 1
    SubStop 'qa-lead' 'Sign-off. .workflow/features/demo.md' "Verdict: Not signed off" 'a3' -Handback | Out-Null
    Check 'count: a handback report is read' (Count 'feature:demo' 'qa') 1
    SubStop 'code-reviewer' $rb "Verdict: Approve" 'a4' | Out-Null
    Check 'count: an approval adds nothing' (Count 'feature:demo' 'review') 1
    SubStop 'code-reviewer' 'Audit Assets/. .workflow/features/demo.md' "Verdict: Request changes" 'a5' | Out-Null
    Check 'count: an audit is not a review round' (Count 'feature:demo' 'review') 1
    SubStop 'security-reviewer' $rb "Status: Blocked`nmissing diff" 'a6' | Out-Null
    Check 'count: Status Blocked is not a verdict' (Count 'feature:demo' 'review') 1
    foreach ($n in 2..4) { SubStop 'code-reviewer' "Review round $n. .workflow/features/demo.md" 'Verdict: Request changes' "r$n" | Out-Null }
    Check 'count: the ledger blocks although the file says 0' (Dispatch $brief) 2
    Remove-Item $ledger
    Bugs 'Reopened' '0/2'
    foreach ($n in 1..3) { SubStop 'gameplay-engineer' 'Fix BUG-0007' "Status: Failed`nAttempts: 3/3" "f$n" | Out-Null }
    Check 'count: Failed returns count as bug rounds' (Dispatch 'Fix BUG-0007') 2
    Remove-Item $ledger
    SubStop 'playtest-tester' 'Re-run BUG-0007. .workflow/features/demo.md' "Status: Done`nRepro: BUG-0007 reproduces" 'p1' | Out-Null
    SubStop 'playtest-tester' 'Re-run BUG-0007' "Status: Failed`nRepro: BUG-0007 reproduces" 'p2' | Out-Null
    SubStop 'playtest-tester' 'Re-run BUG-0007' "Status: Done`nRepro: BUG-0007 gone" 'p3' | Out-Null
    Check 'count: a repro that still fails counts once per run' (Count 'bug:BUG-0007' 'fix') 2
    Check 'count: a repro that still fails adds feature rework' (Count 'feature:demo' 'rework') 1
    Remove-Item $ledger
    foreach ($n in 1..4) { SubStop 'code-reviewer' "Review round $n of the HUD diff" 'Verdict: Request changes' "s$n" | Out-Null }
    $gate = @{ session_id = 'sess-1'; tool_name = 'Agent'; tool_input = @{ subagent_type = 'code-reviewer'; prompt = 'Review round 5 of the HUD diff' } }
    Check 'count: session work past the cap blocks the gate' (Invoke-Hook 'round-cap.ps1' $gate @('-Mode', 'dispatch')).Code 2
    $gate.tool_input.subagent_type = 'Explore'
    Check 'count: session cap leaves non-gate agents alone' (Invoke-Hook 'round-cap.ps1' $gate @('-Mode', 'dispatch')).Code 0
    $gate.tool_input.subagent_type = 'code-reviewer'; $gate.session_id = 'sess-2'
    Check 'count: another session starts clean' (Invoke-Hook 'round-cap.ps1' $gate @('-Mode', 'dispatch')).Code 0
    Remove-Item $ledger
    Set-Content $feat "# Demo`n`n- Status: Open`n- Size: L, Risk flag: no`n`n## GD decisions`n" -Encoding UTF8
    Check 'round-cap: an open feature without Rounds warns on edit' (EditState $feat) 2
    Check 'round-cap: an open feature without Rounds still dispatches' (Dispatch $brief) 0

    # verify-on-edit
    Check 'verify-on-edit ignores files outside .claude' (Invoke-Hook 'verify-on-edit.ps1' @{ tool_input = @{ file_path = "$proj/Assets/A.cs" } }).Code 0
}
finally {
    Remove-Item Env:CLAUDE_PROJECT_DIR, Env:HOOK_TEST_XERJ, Env:MEM_CAPTURE, Env:XERJ_URL -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}

if ($failures) { Write-Output "$failures failure(s)"; exit 1 }
Write-Output 'hooks: all tests passed'
exit 0
