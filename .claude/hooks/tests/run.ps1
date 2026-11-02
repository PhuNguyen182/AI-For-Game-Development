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
    $r = Invoke-Hook 'secret-scan.ps1' @{ cwd = $tmp; tool_name = 'Edit'; tool_input = @{ file_path = "$tmp/.claude/hooks/x.ps1"; new_string = $fakeKey } }
    Check 'secret-scan exempts the hook scripts' $r.Code 0
    $r = Invoke-Hook 'secret-scan.ps1' @{ cwd = $tmp; tool_name = 'Edit'; tool_input = @{ file_path = "$tmp/.claude/hooks/keys.json"; new_string = $fakeKey } }
    Check 'secret-scan does not exempt other files in the hooks folder' $r.Code 2
    $r = Invoke-Hook 'secret-scan.ps1' @{ cwd = $tmp; tool_name = 'Edit'; tool_input = @{ file_path = "$tmp/Assets/X/.claude/hooks/x.ps1"; new_string = $fakeKey } }
    Check 'secret-scan does not exempt a hooks folder deeper in the tree' $r.Code 2

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
    Check 'malformed hook input fails closed' ($LASTEXITCODE -eq 2 -and $r -match 'no readable hook input') $true
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

    # pre-commit: the commit an in-progress operation's --continue makes is scanned too
    Set-Content (Join-Path $guid 'Assets/G.cs.meta') "fileFormatVersion: 2`nguid: fedcba9876543210fedcba9876543210"
    git -C $guid add Assets/G.cs.meta 2>&1 | Out-Null
    foreach ($verb in 'merge', 'rebase', 'cherry-pick', 'revert') {
        Check "pre-commit runs on git $verb --continue" (Invoke-Hook 'pre-commit.ps1' @{ tool_name = 'Bash'; cwd = $guid; tool_input = @{ command = "git $verb --continue" } }).Code 2
    }
    Check 'pre-commit ignores git rebase --abort' (Invoke-Hook 'pre-commit.ps1' @{ tool_name = 'Bash'; cwd = $guid; tool_input = @{ command = 'git rebase --abort' } }).Code 0
    git -C $guid reset -q 2>&1 | Out-Null

    # pre-commit: large text Unity YAML stays out of LFS (merge=lfs would replace UnityYAMLMerge); a large binary .asset does not
    git -C $lfs rm -q --cached big.txt 2>&1 | Out-Null
    [IO.File]::WriteAllText((Join-Path $lfs 'Assets/Big.unity'), "%YAML 1.1`n" + ("a: 1`n" * 1300000))
    Set-Content (Join-Path $lfs 'Assets/Big.unity.meta') 'guid: 5'
    git -C $lfs add Assets/Big.unity Assets/Big.unity.meta 2>&1 | Out-Null
    Check 'pre-commit allows a large text scene outside LFS' (Invoke-Hook 'pre-commit.ps1' $lfsCommit).Code 0
    [IO.File]::WriteAllBytes((Join-Path $lfs 'Assets/LightingData.asset'), (New-Object byte[] (6MB)))
    Set-Content (Join-Path $lfs 'Assets/LightingData.asset.meta') 'guid: 6'
    git -C $lfs add Assets/LightingData.asset Assets/LightingData.asset.meta 2>&1 | Out-Null
    Check 'pre-commit blocks a large binary .asset outside LFS' (Invoke-Hook 'pre-commit.ps1' $lfsCommit).Code 2

    # pre-commit: files refused by path or content, raw evidence dumps, token shapes and credential assignments
    $sec = Join-Path $tmp 'SecretFiles'
    New-Repo $sec
    $secCommit = @{ tool_name = 'Bash'; cwd = $sec; tool_input = @{ command = 'git commit -m x' } }
    function StagedCode([string]$Path, [string]$Content) {
        $f = Join-Path $sec $Path
        New-Item -ItemType Directory -Force (Split-Path $f) | Out-Null
        Set-Content $f $Content
        git -C $sec add -f -- $Path 2>&1 | Out-Null
        $code = (Invoke-Hook 'pre-commit.ps1' $secCommit).Code
        git -C $sec rm -q --cached -- $Path 2>&1 | Out-Null
        return $code
    }
    foreach ($bad in @('release.keystore', 'Signing/upload.JKS', 'certs/dist.p12', 'AuthKey_ABC.p8', 'ios/Game.mobileprovision',
            '.env', 'server/.env.production', 'keys/id_rsa', '.upmconfig.toml', 'Tools/my-service-account.json',
            '.workflow/evidence/x/attempt-1/logcat_full.txt', '.workflow/evidence/x/attempt-1/syslog.txt', '.workflow/evidence/x/App.ips')) {
        Check "pre-commit blocks the file: $bad" (StagedCode $bad 'x') 2
    }
    foreach ($bad in @('Library/ArtifactDB', 'Temp/UnityLockfile', 'UserSettings/EditorUserSettings.asset', 'Logs/x.log',
            'Game/Library/x.asset', '.workflow/evidence/x/UnityConnectCache.json', 'docs/.unity-pipeline-port')) {
        Check "pre-commit blocks Editor session data: $bad" (StagedCode $bad 'x') 2
    }
    New-Item -ItemType Directory -Force (Join-Path $sec 'Assets/Library') | Out-Null
    Set-Content (Join-Path $sec 'Assets/Library/Notes.txt') 'x'
    Set-Content (Join-Path $sec 'Assets/Library/Notes.txt.meta') "fileFormatVersion: 2`nguid: 0123456789abcdef0123456789abcdef"
    git -C $sec add -f -- Assets/Library/Notes.txt Assets/Library/Notes.txt.meta 2>&1 | Out-Null
    Check 'pre-commit allows a project folder named Library under Assets' (Invoke-Hook 'pre-commit.ps1' $secCommit).Code 0
    git -C $sec rm -q --cached -- Assets/Library/Notes.txt Assets/Library/Notes.txt.meta 2>&1 | Out-Null
    Check 'pre-commit scans a .claude/hooks folder deeper in the tree' (StagedCode 'Assets/X/.claude/hooks/key.txt' "k = `"$fakeKey`"") 2
    Set-Content (Join-Path $sec 'release.keystore') 'x'
    git -C $sec add -f release.keystore 2>&1 | Out-Null
    foreach ($form in @('"C:/Program Files/Git/cmd/git.exe" commit -m x', 'git.exe commit -m x', '& "/c/Program Files/Git/cmd/git" commit -m x')) {
        Check "pre-commit sees a quoted or .exe git: $form" (Invoke-Hook 'pre-commit.ps1' @{ tool_name = 'PowerShell'; cwd = $sec; tool_input = @{ command = $form } }).Code 2
    }
    git -C $sec rm -q --cached release.keystore 2>&1 | Out-Null
    Remove-Item (Join-Path $sec 'release.keystore')
    $raw = '' | & $shell -NoProfile -NonInteractive -File (Join-Path $hooks 'pre-commit.ps1') 2>&1; $rawCode = $LASTEXITCODE
    Check 'pre-commit fails closed on unreadable hook input' $rawCode 2
    Check 'pre-commit allows an evidence report' (StagedCode '.workflow/evidence/x/attempt-1/report.md' '# Report') 0
    foreach ($ok in @('.env.example', 'server/.env.sample', '.env.template', 'keys/id_rsa.pub')) {
        Check "pre-commit allows the template: $ok" (StagedCode $ok 'KEY=') 0
    }
    Check 'pre-commit still blocks .env.example.bak' (StagedCode '.env.example.bak' 'x') 2
    Check 'pre-commit allows an ordinary JSON' (StagedCode 'Tools/settings.json' '{ "type": "config" }') 0
    Check 'pre-commit blocks a service-account JSON by content' (StagedCode 'Tools/creds.json' "{`n  `"type`": `"service_account`",`n  `"project_id`": `"x`"`n}") 2
    Set-Content (Join-Path $sec 'old.keystore') 'x'
    git -C $sec add -f old.keystore 2>&1 | Out-Null
    git -C $sec -c user.name=t -c user.email=t@t commit -q -m ks 2>&1 | Out-Null
    git -C $sec rm -q --cached old.keystore 2>&1 | Out-Null
    Check 'pre-commit allows removing a tracked keystore' (Invoke-Hook 'pre-commit.ps1' $secCommit).Code 0
    git -C $sec reset -q 2>&1 | Out-Null
    # Built at runtime so this file never holds a secret-shaped literal.
    $shapes = [ordered]@{
        'Google OAuth token' = 'ya' + '29.' + ('a' * 24); 'Google client secret' = 'GOC' + 'SPX-' + ('a' * 24)
        'GitHub fine-grained token' = 'github' + '_pat_' + ('A' * 40); 'GitLab token' = 'gl' + 'pat-' + ('a' * 20)
        'npm token' = 'np' + 'm_' + ('a' * 36); 'OpenAI key' = 's' + 'k-proj-' + ('a' * 24); 'Anthropic key' = 's' + 'k-ant-api03-' + ('a' * 24)
        'Bearer token' = 'Authorization: Bear' + 'er ' + ('a' * 24); 'Azure storage key' = 'Account' + 'Key=' + ('a' * 24) + '=='
        'Azure SAS' = 'SharedAccess' + 'Signature=sv=2020&sig=' + ('a' * 20); 'Slack webhook' = 'https://hooks.' + 'slack.com/services/T' + ('A' * 24)
        'Discord webhook' = 'https://discord.com/api/' + 'webhooks/' + ('1' * 18) + '/' + ('a' * 40)
    }
    foreach ($k in $shapes.Keys) { Check "pre-commit blocks a new token shape: $k" (StagedCode 'notes.txt' $shapes[$k]) 2 }
    $PW = 'PASS' + 'WORD'
    foreach ($bad in @("DB_$PW=abcdefghijklmnop", "client_se$('cret'): abcdefghijkl12", "store$('Pass')word=android12345", "SECRET_KEY = abcdefghijklmnopqr")) {
        Check "pre-commit blocks a credential assignment: $($bad.Substring(0, 6))..." (StagedCode 'app.env.txt' $bad) 2
    }
    foreach ($ok in @("$PW=`$$PW", "$PW=`${$PW}", "set $PW=%$PW%", 'var token = this.GetCancellationTokenOnDestroy();', 'token = destroyCancellationToken;',
            'api_key: <your-api-key>')) {
        Check "pre-commit allows a lookup or code: $ok" (StagedCode 'app.env.txt' $ok) 0
    }

    # pre-commit: a /feature lane A worktree commits new assets without .meta; every other check still runs there
    $laneMain = Join-Path $tmp 'LaneMain'
    New-Repo $laneMain
    Set-Content (Join-Path $laneMain 'Assets/Base.cs') 'class Base {}'
    Set-Content (Join-Path $laneMain 'Assets/Base.cs.meta') 'guid: 7'
    git -C $laneMain add -A 2>&1 | Out-Null
    git -C $laneMain -c user.name=t -c user.email=t@t commit -q -m base 2>&1 | Out-Null
    $laneWt = Join-Path $laneMain '.claude/worktrees/lane-a'
    git -C $laneMain worktree add -q -b lane-a $laneWt 2>&1 | Out-Null
    $savedProject = $env:CLAUDE_PROJECT_DIR
    $env:CLAUDE_PROJECT_DIR = $laneMain
    $laneCommit = @{ tool_name = 'Bash'; cwd = $laneWt; tool_input = @{ command = 'git commit -m x' } }
    Set-Content (Join-Path $laneWt 'Assets/A.cs') 'class A {}'
    git -C $laneWt add Assets/A.cs 2>&1 | Out-Null
    Check 'lane: worktree commit of an asset without .meta passes' (Invoke-Hook 'pre-commit.ps1' $laneCommit).Code 0
    $env:CLAUDE_PROJECT_DIR = $laneWt
    Check 'lane: ... also when the hook gets the agent worktree as its project dir' (Invoke-Hook 'pre-commit.ps1' $laneCommit).Code 0
    $env:CLAUDE_PROJECT_DIR = $laneMain
    Set-Content (Join-Path $laneWt 'Assets/K.cs') "var k = `"$fakeKey`";"
    git -C $laneWt add Assets/K.cs 2>&1 | Out-Null
    Check 'lane: worktree commit still blocks a staged secret' (Invoke-Hook 'pre-commit.ps1' $laneCommit).Code 2
    git -C $laneWt rm -q --cached Assets/K.cs 2>&1 | Out-Null
    Set-Content (Join-Path $laneWt 'lane.keystore') 'x'
    git -C $laneWt add lane.keystore 2>&1 | Out-Null
    Check 'lane: worktree commit still blocks a keystore' (Invoke-Hook 'pre-commit.ps1' $laneCommit).Code 2
    git -C $laneWt rm -q --cached lane.keystore 2>&1 | Out-Null
    Set-Content (Join-Path $laneMain 'Assets/A.cs') 'class A {}'
    git -C $laneMain add Assets/A.cs 2>&1 | Out-Null
    Check 'lane: the main checkout still blocks an asset without .meta' (Invoke-Hook 'pre-commit.ps1' @{ tool_name = 'Bash'; cwd = $laneMain; tool_input = @{ command = 'git commit -m x' } }).Code 2
    if ($null -eq $savedProject) { Remove-Item Env:CLAUDE_PROJECT_DIR -ErrorAction SilentlyContinue } else { $env:CLAUDE_PROJECT_DIR = $savedProject }

    # pre-push: radius-3 forms are blocked however they are spelled
    function Push([string]$Command, [string]$Cwd = $tmp) { (Invoke-Hook 'pre-push.ps1' @{ tool_name = 'Bash'; cwd = $Cwd; tool_input = @{ command = $Command } }).Code }
    foreach ($bad in @('git push --force origin main', 'git push -f', 'git push -uf origin main', 'git push --mirr origin',
            'git push --del origin x', 'git push -d origin x', 'git push origin +main', 'git push origin "+main"', 'git push origin :old',
            'git push --tags', 'git push --tag origin', 'git push --pru origin', 'git -C . push --force-with-lease',
            'git push --receive-pack=x .', 'git -c remote.origin.mirror=true push', 'cd x && git push -f', 'git status; git push --force origin main')) {
        Check "pre-push blocks: $bad" (Push $bad) 2
    }
    foreach ($ok in @('git push origin main', 'git push -u origin feature', 'git push --follow-tags origin main', 'git push origin main:main',
            'git push --no-force origin x', 'git push -o ci.skip origin main', 'git commit -m "never git push --force here"',
            "git commit -F - <<'EOF'`nNever git push --force or git push origin +main.`nEOF")) {
        Check "pre-push allows: $($ok -replace "`n", ' ')" (Push $ok) 0
    }
    $mir = Join-Path $tmp 'MirrorRepo'
    git init -q $mir 2>&1 | Out-Null
    git -C $mir config remote.origin.mirror true
    Check 'pre-push blocks a plain push from a mirror clone' (Push 'git push' $mir) 2

    # pre-push: a secret added only by a merge commit, or only on another local branch, is found
    $pp = Join-Path $tmp 'PushRepo'
    git init -q -b main $pp 2>&1 | Out-Null
    function G { git -C $pp -c user.name=t -c user.email=t@t @args 2>&1 | Out-Null }
    Set-Content (Join-Path $pp 'a.txt') 'a'; G add a.txt; G commit -q -m base
    G checkout -q -b side; Set-Content (Join-Path $pp 'b.txt') 'b'; G add b.txt; G commit -q -m side
    G checkout -q main; G merge -q --no-ff --no-commit side
    Set-Content (Join-Path $pp 'k.txt') "var k = `"$fakeKey`";"; G add k.txt; G commit -q -m merge
    Check 'pre-push sees a secret added by a merge commit' (Push 'git push origin main' $pp) 2
    G reset -q --hard HEAD~1
    G checkout -q side; Set-Content (Join-Path $pp 'k.txt') "var k = `"$fakeKey`";"; G add k.txt; G commit -q -m key; G checkout -q main
    Check 'pre-push sees a secret on another local branch' (Push 'git push origin side' $pp) 2

    # pre-push: the pre-commit file rules on every file an unpushed commit adds
    $pf = Join-Path $tmp 'PushFiles'
    git init -q -b main $pf 2>&1 | Out-Null
    function PF { git -C $pf -c user.name=t -c user.email=t@t @args 2>&1 | Out-Null }
    Set-Content (Join-Path $pf 'a.txt') 'a'; PF add a.txt; PF commit -q -m base
    Check 'pre-push allows clean unpushed commits' (Push 'git push origin main' $pf) 0
    foreach ($case in @(@('release.keystore', 'x'), @('.env', 'X=1'), @('.workflow/evidence/x/logcat_full.txt', 'log'),
            @('cfg/creds.json', "{ `"type`": `"service_account`" }"))) {
        $f = Join-Path $pf $case[0]
        New-Item -ItemType Directory -Force (Split-Path $f) | Out-Null
        Set-Content $f $case[1]; PF add -f -- $case[0]; PF commit -q -m add
        Check "pre-push blocks an unpushed $($case[0])" (Push 'git push origin main' $pf) 2
        PF reset -q --hard HEAD~1
    }
    Set-Content (Join-Path $pf '.workflow/evidence/x/report.md') '# Report'; PF add -f -- .workflow/evidence/x/report.md; PF commit -q -m report
    Check 'pre-push allows an unpushed evidence report' (Push 'git push origin main' $pf) 0

    # git-guard
    function Guarded([string]$Command, [string]$Tool = 'Bash') { (Invoke-Hook 'git-guard.ps1' @{ tool_name = $Tool; cwd = $tmp; tool_input = @{ command = $Command } }).Code }
    foreach ($bad in @('git reset --hard', 'git reset HEAD~3 --hard', 'git -C . reset --hard', 'git reset --ha', 'cd x && git reset --hard origin/main',
            'git clean -fdx', 'git clean -xdf', 'git clean --force', 'git grep -O vim foo', 'git grep -nOvim foo', 'git grep -O/usr/bin/true foo', 'git grep -1Oecho foo', 'git grep -i -n3Ovim foo', 'git grep --open-files-in-pager foo',
            'git diff --output=x.txt', 'git log --outp=x.txt')) {
        Check "git-guard blocks: $bad" (Guarded $bad) 2
    }
    foreach ($ok in @('git reset --soft HEAD~1', 'git reset --keep backup/x', 'git clean -xdn', 'git grep -n foo', 'git diff --output-indicator-new=+',
            'git log --oneline', 'git commit -m "use git reset --hard sparingly"', "git commit -F - <<'EOF'`nWhy git clean -fdx is denied.`nEOF")) {
        Check "git-guard allows: $($ok -replace "`n", ' ')" (Guarded $ok) 0
    }
    Check 'git-guard reads a PowerShell here-string as text' (Guarded "`$msg = @'`nNever git reset --hard.`n'@; `$msg | git commit -F -" 'PowerShell') 0

    # git-guard: discarding checkouts, wrappers, aliases, injected config, pushes through it
    foreach ($bad in @('git checkout -f other', 'git checkout --force other', 'git switch -f other', 'git switch --discard-changes other',
            'git read-tree -u --reset HEAD', 'sh -c "git reset --hard"', "bash -c 'git push --force origin main'",
            'pwsh -Command "git clean -fdx"', 'git -c alias.r="reset --hard" r', 'git -c alias.p="push --force" p origin main',
            'GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=remote.origin.mirror GIT_CONFIG_VALUE_0=true git push',
            'git push origin refs/tags/backup/merge-20261030T000000Z', 'git push origin backup/merge-20261030T000000Z', 'git push -uf origin main')) {
        Check "git-guard blocks: $bad" (Guarded $bad) 2
    }
    foreach ($ok in @('git checkout -b feature', 'git checkout -- file-f', 'git switch -c feature', 'git read-tree -m -u HEAD',
            'git push origin feature', 'sh -c "git status"')) {
        Check "git-guard allows: $ok" (Guarded $ok) 0
    }
    $al = Join-Path $tmp 'AliasRepo'
    git init -q $al 2>&1 | Out-Null
    git -C $al config alias.nuke 'reset --hard'
    git -C $al config alias.wipe '!git clean -fdx'
    git -C $al config alias.pp 'push'
    git -C $al config alias.st 'status'
    function GuardedIn([string]$Command) { (Invoke-Hook 'git-guard.ps1' @{ tool_name = 'Bash'; cwd = $al; tool_input = @{ command = $Command } }).Code }
    Check 'git-guard expands a configured alias' (GuardedIn 'git nuke') 2
    Check 'git-guard expands a configured shell alias' (GuardedIn 'git wipe') 2
    Check 'git-guard refuses a push through an alias' (GuardedIn 'git pp origin main') 2
    Check 'git-guard allows a harmless alias' (GuardedIn 'git st') 0
    git -C $al config clean.requireForce false
    Check 'git-guard treats clean as clean -f when clean.requireForce is false' (GuardedIn 'git clean -xd') 2
    Check 'git-guard still allows a clean dry run then' (GuardedIn 'git clean -xdn') 0

    # git-guard: spellings of git, transport programs, config that runs a program
    foreach ($bad in @('git.exe reset --hard', '"C:/Program Files/Git/cmd/git.exe" reset --hard', 'git ls-remote --upload-pack=x .',
            'git ls-remote -u x .', 'git fetch --upload-pack=x origin', 'git clone -u x src dst', 'git -c core.sshCommand=x fetch',
            'git -c "core.sshCommand=ssh -i k" fetch', 'git -c clean.requireForce=false clean -xd', 'git -c core.fsmonitor=x status',
            "git ls-remote --upload-pack='touch x; git reset --hard' .")) {
        Check "git-guard blocks: $bad" (Guarded $bad) 2
    }
    foreach ($ok in @('git ls-remote origin', 'git fetch -u origin', 'git -c rerere.enabled=true rebase --continue', 'git -c gc.auto=0 fetch',
            'git -c user.name=t commit -m x')) {
        Check "git-guard allows: $ok" (Guarded $ok) 0
    }

    # pre-push: pattern refspecs, and a secret reachable only from a tag
    Check 'pre-push blocks a pattern refspec' (Push 'git push origin "refs/tags/*"') 2
    Check 'pre-push blocks refs/*:refs/*' (Push "git push origin 'refs/*:refs/*'") 2
    $tg = Join-Path $tmp 'TagRepo'
    git init -q -b main $tg 2>&1 | Out-Null
    function T { git -C $tg -c user.name=t -c user.email=t@t @args 2>&1 | Out-Null }
    Set-Content (Join-Path $tg 'a.txt') 'a'; T add a.txt; T commit -q -m base; T checkout -q --detach
    Set-Content (Join-Path $tg 'k.txt') "var k = `"$fakeKey`";"; T add k.txt; T commit -q -m key; T tag v1; T checkout -q main
    Check 'pre-push sees a secret reachable only from a tag' (Push 'git push origin v1' $tg) 2
    $keySha = [string](git -C $tg rev-parse v1)
    T tag -d v1; T tag backup/x $keySha
    Check 'pre-push leaves backup/* anchors out of the scan' (Push 'git push origin main' $tg) 0
    Check 'pre-push blocks a push to a URL that is not a remote' (Push 'git push https://elsewhere.example/x.git HEAD:main' $tg) 2
    Check 'pre-push blocks --repo <url>' (Push 'git push --repo https://elsewhere.example/x.git main' $tg) 2
    Check 'pre-push blocks a push to a local path' (Push 'git push ../copy main' $tg) 2
    Check 'pre-push still reads -o values as values' (Push 'git push -o ci.skip origin main' $tg) 0

    # git-guard: the auto-allowed `git tag backup/*` creates anchors only
    foreach ($bad in @('git tag backup/x -d v1.0', 'git tag -f backup/x', 'git tag backup/x -f HEAD', 'git tag -d backup/x v1.0',
            'git tag --sort=refname -f backup/x HEAD', 'git tag --format=x -f backup/x', 'git tag -i -f backup/x')) {
        Check "git-guard blocks: $bad" (Guarded $bad) 2
    }
    foreach ($ok in @('git tag backup/merge-20261030T000000Z', 'git tag backup/x abc1234', 'git tag -d backup/x', 'git tag -a v1.2.0 -m release',
            "git tag -l 'backup/*'", 'git tag --list backup/* --sort=-creatordate')) {
        Check "git-guard allows: $ok" (Guarded $ok) 0
    }

    # pre-commit: forms that stage as they commit
    $guidPlain = @{ tool_name = 'Bash'; cwd = $guid; tool_input = @{ command = '' } }
    foreach ($bad in @('git commit -am x', 'git commit -a -m x', 'git commit --all -m x', 'git commit -m x -- Assets/G.cs', 'git commit -m x Assets/G.cs',
            'git commit -o -m x', 'git add Assets/G.cs && git commit -m x', 'git add -A; git commit -m x')) {
        $guidPlain.tool_input.command = $bad
        Check "pre-commit blocks: $bad" (Invoke-Hook 'pre-commit.ps1' $guidPlain).Code 2
    }
    foreach ($ok in @('git commit -m x', 'git commit -qm x', 'git commit -m "two words" 2>&1', 'git commit -F - -v', "git commit -F - <<'EOF'`nWhy git add -A is wrong.`nEOF",
            'git commit --author "A B <a@b>" -m x', 'git commit -C HEAD')) {
        $guidPlain.tool_input.command = $ok
        Check "pre-commit allows: $($ok -replace "`n", ' ')" (Invoke-Hook 'pre-commit.ps1' $guidPlain).Code 0
    }
    Check 'pre-push blocks a force push in a shell wrapper' (Push "bash -c 'git push --force origin main'") 2
    Check 'pre-push blocks pushing an anchor tag' (Push 'git push origin refs/tags/backup/merge-20261030T000000Z') 2

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
    Check 'lock: B may read editor status to confirm a stale lock' (Lock 'B' 'x' 'check' 'unity command editor status') 0
    Check 'lock: a status call chained to a mutation is still blocked' (Lock 'B' 'x' 'check' 'unity status && unity command script recompile') 2
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

    # editor-lock: the main session's own compile check / test run holds the Editor until its turn ends
    Check 'main: own unity call passes' (Lock 'M' 'x' 'check' 'unity command script recompile') 0
    Check 'main: it takes a main hold' (@((Get-Content $lock -Raw | ConvertFrom-Json).holds) -contains 'main') $true
    Check 'main: another session is kept out meanwhile' (Lock 'N' 'gameplay-engineer' 'acquire') 2
    Lock 'M' 'ui-engineer' 'acquire' | Out-Null
    Lock 'M' 'ui-engineer' 'release' | Out-Null
    Check 'main: an agent stop keeps the main hold' (Test-Path $lock) $true
    Lock 'M' 'x' 'clear' | Out-Null
    Check 'main: turn end releases it' (Test-Path $lock) $false
    function WriteFile([string]$Session, [string]$Path) { (Invoke-Hook 'editor-lock.ps1' @{ session_id = $Session; tool_name = 'Write'; cwd = $proj; tool_input = @{ file_path = $Path } } @('-Mode', 'check')).Code }
    Check 'write: a direct Assets write takes a main hold' (WriteFile 'W' (Join-Path $proj 'Assets/A.cs')) 0
    Check 'write: ... recorded in the lock' (@((Get-Content $lock -Raw | ConvertFrom-Json).holds) -contains 'main') $true
    Check 'write: another session writing into Assets is refused' (WriteFile 'X' (Join-Path $proj 'ProjectSettings/TagManager.asset')) 2
    Check 'write: a write outside Assets/Packages/ProjectSettings passes' (WriteFile 'X' (Join-Path $proj '.workflow/features/x.md')) 0
    Lock 'W' 'x' 'clear' | Out-Null

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

    # editor-lock: lane A worktree agents never hold or drive the Editor
    $wt = Join-Path $proj 'wt'
    New-Item -ItemType Directory -Force $wt | Out-Null
    Set-Content (Join-Path $wt '.git') 'gitdir: C:/repo/.git/worktrees/wt'
    $iso = (Invoke-Hook 'editor-lock.ps1' @{ session_id = 'F'; tool_input = @{ subagent_type = 'csharp-engineer'; isolation = 'worktree' } } @('-Mode', 'acquire')).Code
    Check 'lane: worktree dispatch passes' $iso 0
    Check 'lane: worktree dispatch takes no hold' (Test-Path $lock) $false
    Check 'lane: unity CLI from a worktree blocked' (Invoke-Hook 'editor-lock.ps1' @{ session_id = 'F'; cwd = $wt; tool_input = @{ command = 'unity command script recompile' } } @('-Mode', 'check')).Code 2
    Check 'lane: unity MCP from a worktree blocked' (Invoke-Hook 'editor-lock.ps1' @{ session_id = 'F'; cwd = $wt; tool_name = 'mcp__unity-mcp__Unity_RunCommand'; tool_input = @{} } @('-Mode', 'check')).Code 2
    Check 'lane: unity MCP from the main checkout passes' (Invoke-Hook 'editor-lock.ps1' @{ session_id = 'F'; cwd = $proj; tool_name = 'mcp__unity-mcp__Unity_RunCommand'; tool_input = @{} } @('-Mode', 'check')).Code 0
    Lock 'F' 'x' 'clear' | Out-Null
    Lock 'G' 'gameplay-engineer' 'acquire' | Out-Null
    $env:HOOK_TEST_EDITOR_STATE = 'playing'
    $laneStop = (Invoke-Hook 'editor-lock.ps1' @{ session_id = 'G'; agent_type = 'csharp-engineer'; cwd = $wt; stop_hook_active = $false } @('-Mode', 'release')).Code
    Check 'lane: worktree agent stop ignores lane B Play Mode' $laneStop 0
    Check 'lane: lane B hold kept' (Test-Path $lock) $true
    Lock 'G' 'backend-engineer' 'acquire' | Out-Null
    $env:HOOK_TEST_EDITOR_STATE = 'clean'
    $laneSame = (Invoke-Hook 'editor-lock.ps1' @{ session_id = 'G'; agent_type = 'backend-engineer'; cwd = $wt; stop_hook_active = $false } @('-Mode', 'release')).Code
    Check 'lane: lane A stop of a same-type agent passes' $laneSame 0
    Check 'lane: lane A stop keeps a same-type lane B hold' (@((Get-Content $lock -Raw | ConvertFrom-Json).holds) -contains 'backend-engineer') $true
    $env:HOOK_TEST_EDITOR_STATE = 'playing'
    Lock 'G' 'x' 'clear' | Out-Null
    # The project itself checked out as a linked worktree is the main checkout, not a lane
    Set-Content (Join-Path $proj '.git') 'gitdir: C:/repo/.git/worktrees/proj'
    Check 'lane: project in a linked worktree may call unity' (Invoke-Hook 'editor-lock.ps1' @{ session_id = 'H'; cwd = $proj; tool_input = @{ command = 'unity command script recompile' } } @('-Mode', 'check')).Code 0
    Lock 'H' 'playtest-tester' 'acquire' | Out-Null
    Check 'lane: project-worktree holder still sent back from Play Mode' (Invoke-Hook 'editor-lock.ps1' @{ session_id = 'H'; agent_type = 'playtest-tester'; cwd = $proj; stop_hook_active = $false } @('-Mode', 'release')).Code 2
    Check 'lane: a lane worktree under that project is still blocked' (Invoke-Hook 'editor-lock.ps1' @{ session_id = 'H'; cwd = $wt; tool_input = @{ command = 'unity command script recompile' } } @('-Mode', 'check')).Code 2
    Lock 'H' 'x' 'clear' | Out-Null
    Remove-Item (Join-Path $proj '.git')
    # Claude Code agent worktrees live at <project>/.claude/worktrees/<name>; a hook may get that worktree as its project dir
    New-Item -ItemType Directory -Force (Join-Path $proj '.git') | Out-Null
    $cw = Join-Path $proj '.claude/worktrees/agent-x'
    New-Item -ItemType Directory -Force (Join-Path $cw 'Assets') | Out-Null
    Set-Content (Join-Path $cw '.git') 'gitdir: C:/repo/.git/worktrees/agent-x'
    $env:CLAUDE_PROJECT_DIR = $cw
    Check 'lane: agent worktree as project dir still blocks unity' (Invoke-Hook 'editor-lock.ps1' @{ session_id = 'J'; cwd = $cw; tool_input = @{ command = 'unity command script recompile' } } @('-Mode', 'check')).Code 2
    Check 'lane: ... and takes no hold in the worktree' (Test-Path (Join-Path $cw '.workflow/editor.lock')) $false
    $env:CLAUDE_PROJECT_DIR = $proj
    Remove-Item -Recurse -Force (Join-Path $proj '.claude'), (Join-Path $proj '.git')
    # A standalone project whose own path contains .claude/worktrees/ keeps its root (no checkout above it)
    $odd = Join-Path $tmp 'Odd/.claude/worktrees/game'
    New-Item -ItemType Directory -Force (Join-Path $odd 'Assets') | Out-Null
    $env:CLAUDE_PROJECT_DIR = $odd
    Lock 'K' 'ui-engineer' 'acquire' | Out-Null
    Check 'lane: a project path merely containing .claude/worktrees keeps its own lock' (Test-Path (Join-Path $odd '.workflow/editor.lock')) $true
    $env:CLAUDE_PROJECT_DIR = $proj
    # Root resolution: main checkouts hold a .git directory, worktrees a .git file
    New-Item -ItemType Directory -Force (Join-Path $odd '.git') | Out-Null
    $oddWt = Join-Path $odd '.claude/worktrees/b'; New-Item -ItemType Directory -Force $oddWt | Out-Null; Set-Content (Join-Path $oddWt '.git') 'gitdir: x/.git/worktrees/b'
    $mainR = Join-Path $tmp 'MainR'; New-Item -ItemType Directory -Force (Join-Path $mainR '.git') | Out-Null
    $wtA = Join-Path $mainR '.claude/worktrees/a'; $wtC = Join-Path $wtA '.claude/worktrees/c'
    New-Item -ItemType Directory -Force $wtC | Out-Null; Set-Content (Join-Path $wtA '.git') 'gitdir: x/.git/worktrees/a'; Set-Content (Join-Path $wtC '.git') 'gitdir: x/.git/worktrees/c'
    . (Join-Path $hooks 'common.ps1')
    $norm = { param($x) ($x -replace '\\', '/').TrimEnd('/') }
    Check 'root: an agent worktree of a project under .claude/worktrees resolves to that project' (& $norm (Get-MainCheckout $oddWt)) (& $norm $odd)
    Check 'root: a worktree nested in a worktree resolves to the main checkout' (& $norm (Get-MainCheckout $wtC)) (& $norm $mainR)
    Check 'root: a plain agent worktree resolves to the main checkout' (& $norm (Get-MainCheckout $wtA)) (& $norm $mainR)
    # A Unity project in a subfolder of a repo that is a linked worktree is still the main checkout
    $sub = Join-Path $tmp 'Repo/Game'
    New-Item -ItemType Directory -Force (Join-Path $sub 'Assets') | Out-Null
    Set-Content (Join-Path $tmp 'Repo/.git') 'gitdir: C:/repo/.git/worktrees/repo'
    $env:CLAUDE_PROJECT_DIR = $sub
    Check 'lane: project in a worktree subfolder may call unity' (Invoke-Hook 'editor-lock.ps1' @{ session_id = 'I'; cwd = $sub; tool_input = @{ command = 'unity command script recompile' } } @('-Mode', 'check')).Code 0
    $env:CLAUDE_PROJECT_DIR = $proj
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

    # session-start: the framework backlog comes from its template when missing, and an existing one is kept
    New-Item -ItemType Directory -Force (Join-Path $proj '.claude/templates') | Out-Null
    Copy-Item (Join-Path $hooks '../templates/framework-backlog.md') (Join-Path $proj '.claude/templates/framework-backlog.md')
    $fb = Join-Path $proj '.workflow/framework-backlog.md'
    $r = Invoke-Hook 'session-start.ps1' @{}
    Check 'session-start creates the framework backlog from its template' ((Test-Path $fb) -and ($r.Out -match 'Framework backlog: created')) $true
    Add-Content $fb '| A row this repo found | Open |'
    $r = Invoke-Hook 'session-start.ps1' @{}
    Check 'session-start keeps an existing framework backlog' (((Get-Content $fb -Raw) -match 'A row this repo found') -and ($r.Out -notmatch 'Framework backlog')) $true

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
    Bugs 'Accepted' '3/2'
    Check 'round-cap: an accepted bug is settled, not capped' (Dispatch 'Bug: BUG-0007') 0
    Bugs 'Duplicate of BUG-0001' '3/2'
    Check 'round-cap: a duplicate bug is settled' (Dispatch 'Bug: BUG-0007') 0
    Bugs 'Reopened' '3/2'
    Check 'round-cap: a QA brief listing a past-cap bug but charging the feature passes' (Dispatch "Feature: .workflow/features/demo.md`nOpen bugs: BUG-0007") 0
    Feature 'review 1/3, QA 0/2, rework 1/6'
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
    $fm = 'Feature: .workflow/features/demo.md'
    $rb = "Round: 1`n$fm`nReview the HUD diff (skill shared-core-boundary-audit)."
    SubStop 'code-reviewer' $rb "Status: Done`nVerdict: Request changes" 'a1' | Out-Null
    SubStop 'security-reviewer' $rb "Status: Done`nVerdict: Blocked" 'a2' | Out-Null
    Check 'count: two gates blocking one round count once' (Count 'feature:demo' 'review') 1
    Check 'count: a blocked review round adds one rework' (Count 'feature:demo' 'rework') 1
    SubStop 'qa-lead' "Sign-off.`n$fm" "Verdict: Not signed off" 'a3' -Handback | Out-Null
    Check 'count: a handback report is read' (Count 'feature:demo' 'qa') 1
    SubStop 'code-reviewer' $rb "Verdict: Approve" 'a4' | Out-Null
    Check 'count: an approval adds nothing' (Count 'feature:demo' 'review') 1
    SubStop 'code-reviewer' "Mode: audit`n$fm`nAudit Assets/." "Verdict: Request changes" 'a5' | Out-Null
    Check 'count: an audit is not a review round' (Count 'feature:demo' 'review') 1
    SubStop 'code-reviewer' "Mode: test-code`n$fm`nReview the new tests." "Verdict: Request changes" 'a5b' | Out-Null
    Check 'count: a test-code review is not a review round' (Count 'feature:demo' 'review') 1
    SubStop 'code-reviewer' "Round: 2`nMode: workflow`nTree: 4444444444444444`n$fm" "Verdict: Request changes" 'a5c' | Out-Null
    Check 'count: a workflow gate is left to the main session' (Count 'feature:demo' 'review') 1
    SubStop 'code-reviewer' "- **Mode:** audit`n$fm" "Verdict: Request changes" 'a5d' | Out-Null
    Check 'count: a bulleted Mode marker is read' (Count 'feature:demo' 'review') 1
    SubStop 'security-reviewer' $rb "Status: Blocked`nmissing diff" 'a6' | Out-Null
    Check 'count: Status Blocked is not a verdict' (Count 'feature:demo' 'review') 1
    SubStop 'code-reviewer' "Round: 2`n$fm" "Verdict: Needs-decision`nFile: A.cs:3 Severity: High Issue: x" 'a7' | Out-Null
    Check 'count: Needs-decision with a High finding is a failed round' (Count 'feature:demo' 'review') 2
    SubStop 'code-reviewer' "Round: 3`n$fm" "Verdict: Needs-decision`nFile: A.cs:3 Severity: Low Issue: x" 'a8' | Out-Null
    Check 'count: Needs-decision with only Low findings is not' (Count 'feature:demo' 'review') 2
    foreach ($n in 3..4) { SubStop 'code-reviewer' "Round: $n`n$fm`nPrevious: round 1 findings." 'Verdict: Request changes' "r$n" | Out-Null }
    Check 'count: the ledger blocks although the file says 0' (Dispatch $brief) 2
    Feature 'review 1/3, QA 0/2, rework 1/6'
    Remove-Item $ledger
    SubStop 'code-reviewer' "Round: 1`n$fm" 'Verdict: Request changes' 'u1' | Out-Null
    SubStop 'code-reviewer' "Round: 2`n$fm" 'Verdict: Request changes' 'u2' | Out-Null
    SubStop 'code-reviewer' "Round: 3`n$fm" 'Verdict: Request changes' 'u3' | Out-Null
    Check 'count: used = file + hook (1 + 3 > 3) blocks' (Dispatch "$fm`nNext attempt") 2
    Feature 'review 0/3, QA 0/2, rework 0/6'
    Remove-Item $ledger
    Bugs 'Reopened' '0/2'
    foreach ($n in 1..3) { SubStop 'gameplay-engineer' "Bug: BUG-0007`n$fm" "Status: Failed`nAttempts: 3/3" "f$n" | Out-Null }
    Check 'count: Failed returns are attempts, not rounds' (Dispatch 'Bug: BUG-0007') 0
    SubStop 'playtest-tester' "Bug: BUG-0007`nReproduce it." "Status: Done`nRepro: BUG-0007 reproduces" 'q1' | Out-Null
    Check 'count: reproducing a bug without Verify is not a fix round' (Test-Path $ledger) $false
    SubStop 'playtest-tester' "Verify: BUG-0007`n$fm" "Status: Done`nRepro: BUG-0007 reproduces" 'p1' | Out-Null
    SubStop 'playtest-tester' "Verify: BUG-0007" "Status: Failed`nRepro: BUG-0007 reproduces" 'p2' | Out-Null
    SubStop 'playtest-tester' "Verify: BUG-0007" "Status: Done`nRepro: BUG-0007 gone" 'p3' | Out-Null
    Check 'count: a verify that still fails counts once per run' (Count 'bug:BUG-0007' 'fix') 2
    Check 'count: a verify that still fails adds feature rework' (Count 'feature:demo' 'rework') 1
    SubStop 'code-reviewer' "Round: 1`nBug: BUG-0007" 'Verdict: Request changes' 'b1' | Out-Null
    Check 'count: a no-feature fix review counts on the bug review counter' (Count 'bug:BUG-0007' 'review') 1
    Check 'count: ... and not on its fix counter' (Count 'bug:BUG-0007' 'fix') 2
    Remove-Item $ledger
    foreach ($n in 1..4) { SubStop 'code-reviewer' "Round: $n`nTarget: Assets/Shop" 'Verdict: Request changes' "t$n" | Out-Null }
    Check 'count: target work past the cap blocks the gate' (Dispatch "Round: 5`nTarget: Assets/Shop") 2
    Check 'count: another target starts clean' (Dispatch "Round: 1`nTarget: Assets/Hud") 0
    Remove-Item $ledger
    # Ledger safety
    New-Item -ItemType Directory -Force (Split-Path $ledger) | Out-Null
    Set-Content $ledger '{ not json' -Encoding UTF8
    Check 'ledger: an unparsable ledger blocks the dispatch' (Dispatch $brief) 2
    Check 'ledger: ... and is moved aside, not overwritten' (@(Get-ChildItem (Split-Path $ledger) -Filter 'rounds.corrupt-*.json').Count) 1
    Check 'ledger: dispatch stays blocked while the moved-aside ledger exists' (Dispatch $brief) 2
    Get-ChildItem (Split-Path $ledger) -Filter 'rounds.corrupt-*.json' | Remove-Item
    Check 'ledger: once the GD resolves it, dispatch runs again' (Dispatch $brief) 0
    Set-Content $ledger '{ broken' -Encoding UTF8
    SubStop 'code-reviewer' "Round: 1`n$fm" 'Verdict: Request changes' 'c1' | Out-Null
    Check 'ledger: a count on a corrupt ledger keeps the old file' (@(Get-ChildItem (Split-Path $ledger) -Filter 'rounds.corrupt-*.json').Count) 1
    Check 'ledger: ... and records the new event' (Count 'feature:demo' 'review') 1
    Get-ChildItem (Split-Path $ledger) -Filter 'rounds.corrupt-*.json' | Remove-Item
    Set-Content (Join-Path (Split-Path $ledger) 'rounds.pending-x.json') '[{"key":"feature:demo","counter":"review","id":"round-9"}]' -Encoding UTF8
    Check 'ledger: parked events count before they are merged' ((Invoke-Hook 'round-cap.ps1' @{ tool_name = 'Edit'; tool_input = @{ file_path = $feat } } @('-Mode', 'edit')).Code) 0
    SubStop 'code-reviewer' "Round: 2`n$fm" 'Verdict: Request changes' 'c2' | Out-Null
    Check 'ledger: parked events merge on the next write' (Count 'feature:demo' 'review') 3
    Check 'ledger: ... and the parked file is removed' (Test-Path (Join-Path (Split-Path $ledger) 'rounds.pending-x.json')) $false
    Set-Content (Join-Path (Split-Path $ledger) 'rounds.pending-bad.json') '[{ broken' -Encoding UTF8
    SubStop 'code-reviewer' "Round: 9`n$fm" 'Verdict: Approve' 'c9' | Out-Null
    SubStop 'code-reviewer' "Round: 9`nTree: aaaaaaaaaaaa`n$fm" 'Verdict: Request changes' 'c9b' | Out-Null
    Check 'ledger: an unparsable parked file is kept as corrupt, not deleted' (Test-Path (Join-Path (Split-Path $ledger) 'rounds.corrupt-pending-bad.json')) $true
    Check 'ledger: ... and blocks dispatch until resolved' (Dispatch $brief) 2
    Remove-Item (Join-Path (Split-Path $ledger) 'rounds.corrupt-pending-bad.json')
    # A repeated Round number on new code (a resumed session restarting at 1) still counts.
    Remove-Item $ledger
    SubStop 'code-reviewer' "Round: 1`nTree: 1111111111111111`n$fm" 'Verdict: Request changes' 'rt1' | Out-Null
    SubStop 'security-reviewer' "Round: 1`nTree: 1111111111111111`n$fm" 'Verdict: Blocked' 'rt2' | Out-Null
    SubStop 'code-reviewer' "Round: 1`nTree: 2222222222222222`n$fm" 'Verdict: Request changes' 'rt3' | Out-Null
    Check 'round: two gates on the same round and tree count once, a repeated number on a new tree counts again' (Count 'feature:demo' 'review') 2
    SubStop 'code-reviewer' "Round: 2`nTree: 3333333333333333`nPrevious tree: 2222222222222222`n$fm" 'Verdict: Request changes' 'rt4' | Out-Null
    Check 'round: the dedupe key is the current Tree, never the Previous tree line' (@((Get-Content $ledger -Raw | ConvertFrom-Json).'feature:demo'.review) -contains 'round-2-333333333333') $true
    Check 'round: a short Tree sha does not break the count' (SubStop 'code-reviewer' "Round: 3`nTree: abcdef1`n$fm" 'Verdict: Request changes' 'rt5') 0
    Check 'round: ... and keys on the whole short sha' (@((Get-Content $ledger -Raw | ConvertFrom-Json).'feature:demo'.review) -contains 'round-3-abcdef1') $true
    SubStop 'code-reviewer' "Round: 4`nTree: $('a1' * 20)`n$fm" 'Verdict: Request changes' 'rt6' | Out-Null
    SubStop 'code-reviewer' "Round: 5`nTree: $('b2' * 32)`n$fm" 'Verdict: Request changes' 'rt7' | Out-Null
    $ids = @((Get-Content $ledger -Raw | ConvertFrom-Json).'feature:demo'.review)
    Check 'round: a 40- and a 64-char sha both key on their first 12 chars' (($ids -contains 'round-4-a1a1a1a1a1a1') -and ($ids -contains 'round-5-b2b2b2b2b2b2')) $true
    SubStop 'code-reviewer' "- Round: 6`n- Tree: cccccccccccc`n$fm" 'Verdict: Request changes' 'rt8' | Out-Null
    SubStop 'security-reviewer' "- **Round:** 6`n- **Tree:** cccccccccccc`n$fm" 'Verdict: Blocked' 'rt9' | Out-Null
    $ids = @((Get-Content $ledger -Raw | ConvertFrom-Json).'feature:demo'.review)
    Check 'round: bulleted Round/Tree markers dedupe the two gates of one round' (@($ids | Where-Object { $_ -eq 'round-6-cccccccccccc' }).Count) 1
    # Workflow launches and the stop-rule record (fresh ledger: 3 failed rounds is at the cap, 4 is past it)
    Remove-Item $ledger
    foreach ($n in 1..3) { SubStop 'code-reviewer' "Round: $n`n$fm" 'Verdict: Request changes' "w$n" | Out-Null }
    Check 'workflow: a launch under the feature cap passes' (Invoke-Hook 'round-cap.ps1' @{ tool_name = 'Workflow'; tool_input = @{ name = 'review-gate'; args = @{ feature = '.workflow/features/demo.md'; round = 4 } } } @('-Mode', 'dispatch')).Code 0
    SubStop 'code-reviewer' "Round: 4`n$fm" 'Verdict: Request changes' 'c4' | Out-Null
    Check 'workflow: a launch past the feature cap blocks' (Invoke-Hook 'round-cap.ps1' @{ tool_name = 'Workflow'; tool_input = @{ name = 'review-gate'; args = @{ feature = '.workflow/features/demo.md'; round = 5 } } } @('-Mode', 'dispatch')).Code 2
    Check 'workflow: a launch naming no target is not checked' (Invoke-Hook 'round-cap.ps1' @{ tool_name = 'Workflow'; tool_input = @{ name = 'project-audit'; args = @{ root = '.' } } } @('-Mode', 'dispatch')).Code 0
    Remove-Item $ledger
    Feature 'review 3/3, QA 0/2, rework 3/6'
    Check 'stop rule: at the cap the edit warns' (EditState $feat) 2
    Add-Content $feat "`n- Stop rule: review root-caused 2026-10-30 - extra dispatch: unused" -Encoding UTF8
    Check 'stop rule: a recorded root cause silences the at-cap warning' (EditState $feat) 0
    Feature 'review 0/3, QA 0/2, rework 0/6'
    foreach ($n in 1..4) { SubStop 'code-reviewer' "Round: $n`nReview the HUD diff" 'Verdict: Request changes' "s$n" | Out-Null }
    $gate = @{ session_id = 'sess-1'; tool_name = 'Agent'; tool_input = @{ subagent_type = 'code-reviewer'; prompt = "Round: 5`nReview the HUD diff" } }
    Check 'count: session work past the cap blocks the gate' (Invoke-Hook 'round-cap.ps1' $gate @('-Mode', 'dispatch')).Code 2
    $gate.tool_input.subagent_type = 'Explore'
    Check 'count: session cap leaves non-gate agents alone' (Invoke-Hook 'round-cap.ps1' $gate @('-Mode', 'dispatch')).Code 0
    $gate.tool_input.subagent_type = 'code-reviewer'; $gate.session_id = 'sess-2'
    Check 'count: another session starts clean' (Invoke-Hook 'round-cap.ps1' $gate @('-Mode', 'dispatch')).Code 0
    $gate.session_id = 'sess-1'; $gate.tool_input.prompt = "Round: 5`nTarget: Assets/Other"
    Check 'count: a named target is not charged with session rounds' (Invoke-Hook 'round-cap.ps1' $gate @('-Mode', 'dispatch')).Code 0
    Remove-Item $ledger
    Set-Content $feat "# Demo`n`n- Status: Open`n- Size: L, Risk flag: no`n`n## GD decisions`n" -Encoding UTF8
    Check 'round-cap: an open feature without Rounds warns on edit' (EditState $feat) 2
    Check 'round-cap: an open feature without Rounds still dispatches' (Dispatch $brief) 0

    # verify-on-edit
    Check 'verify-on-edit ignores files outside .claude' (Invoke-Hook 'verify-on-edit.ps1' @{ tool_input = @{ file_path = "$proj/Assets/A.cs" } }).Code 0
    Check 'verify-on-edit ignores writes inside an agent worktree' (Invoke-Hook 'verify-on-edit.ps1' @{ tool_input = @{ file_path = "$proj/.claude/worktrees/agent-x/.workflow/evidence/r.md" } }).Code 0
}
finally {
    Remove-Item Env:CLAUDE_PROJECT_DIR, Env:HOOK_TEST_XERJ, Env:MEM_CAPTURE, Env:XERJ_URL -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}

if ($failures) { Write-Output "$failures failure(s)"; exit 1 }
Write-Output 'hooks: all tests passed'
exit 0
