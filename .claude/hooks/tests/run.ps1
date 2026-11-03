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
    # The reset above removed the folder. Without it nothing is committed and the allow below proves nothing.
    New-Item -ItemType Directory -Force (Join-Path $pf '.workflow/evidence/x') | Out-Null
    Set-Content (Join-Path $pf '.workflow/evidence/x/report.md') '# Report'; PF add -f -- .workflow/evidence/x/report.md; PF commit -q -m report
    Check 'pre-push fixture: the evidence report is committed' (git -C $pf log -1 --format= --name-only) '.workflow/evidence/x/report.md'
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
    # Bugs come from real bugs.py calls: the CLI owns the journal format. A copy of it, beside the mem.py copy it needs.
    $bugsDir = Join-Path $proj '.claude/skills/bugs/scripts'
    New-Item -ItemType Directory -Force $bugsDir | Out-Null
    Copy-Item (Join-Path $hooks '../skills/bugs/scripts/bugs.py') $bugsDir
    $bugPy = @(Resolve-Python $proj)
    $bugRoot = $proj
    $bugFields = '{"title":"HUD bar wrong","description":"The HUD bar shows the wrong value.","priority":"High","repro":"not yet","expected":"Value per the GDD","actual":"Wrong value","evidence":"none yet"}'
    function BugCli([string[]]$CliArgs, [string]$Stdin = '') {
        $rest = @($bugPy | Select-Object -Skip 1)
        $cli = Join-Path $bugRoot '.claude/skills/bugs/scripts/bugs.py'
        $out = if ($Stdin) { $Stdin | & $bugPy[0] @rest -I $cli --root $bugRoot @CliArgs 2>&1 } else { & $bugPy[0] @rest -I $cli --root $bugRoot @CliArgs 2>&1 }
        if ($LASTEXITCODE -ne 0) { Write-Host "FAIL  fixture: bugs.py $($CliArgs -join ' '): $out"; $script:failures++ }
        return ($out | Out-String)
    }
    function ClearBugs { Remove-Item (Join-Path $bugRoot '.workflow/bugs.*') -Force -ErrorAction SilentlyContinue }
    function MoveBug([string]$Id, [string[]]$Statuses) { foreach ($s in $Statuses) { BugCli @('set-status', $Id, $s, '--note', 'test move') | Out-Null } }
    # One bug, BUG-0001, in $Status with $Fix used fix rounds. A Duplicate points at a second bug.
    function Bugs([string]$Status, [int]$Fix) {
        ClearBugs
        BugCli @('add') $bugFields | Out-Null
        if ($Fix) { BugCli @('round', 'BUG-0001', 'fix', "+$Fix", '--note', 'test round') | Out-Null }
        switch ($Status) {
            'Request' {}
            'Reopen' { MoveBug 'BUG-0001' 'Processing', 'Resolved', 'Review', 'Reopen' }
            'Complete' { MoveBug 'BUG-0001' 'Processing', 'Resolved', 'Review', 'Complete' }
            'Duplicate' {
                BugCli @('add') $bugFields | Out-Null
                BugCli @('set-status', 'BUG-0001', 'Duplicate', '--duplicate-of', 'BUG-0002', '--note', 'test move') | Out-Null
            }
            default { BugCli @('set-status', 'BUG-0001', $Status, '--by', 'GD', '--note', 'test move') | Out-Null }
        }
    }
    function DispatchR([string]$Brief) { Invoke-Hook 'round-cap.ps1' @{ tool_name = 'Agent'; tool_input = @{ prompt = $Brief } } @('-Mode', 'dispatch') }
    function ShellEdit([string]$Command, [string]$Tool = 'PowerShell') { Invoke-Hook 'round-cap.ps1' @{ tool_name = $Tool; tool_input = @{ command = $Command } } @('-Mode', 'edit') }
    $bugCall = 'python -I .claude/skills/bugs/scripts/bugs.py round BUG-0001 fix +1 --note x'
    Bugs 'Reopen' 3
    Check 'round-cap: a bug past its cap blocks' (Dispatch 'Fix BUG-0001') 2
    $r = ShellEdit $bugCall
    Check 'round-cap: a bugs.py command warns past the cap' ($r.Code -eq 2 -and $r.Out -match 'BUG-0001: fix 3/2' -and $r.Out -match 'past the cap') $true
    Check 'round-cap: an edit under .workflow names no bug any more' (EditState (Join-Path $proj '.workflow/bugs.md')) 0
    Bugs 'Reopen' 1
    Check 'round-cap: a bug under its cap dispatches' (Dispatch 'Fix BUG-0001') 0
    Check 'round-cap: a bugs.py command under the cap is silent' (ShellEdit $bugCall).Code 0
    Bugs 'Reopen' 2
    Check 'round-cap: a bug at its cap still dispatches' (Dispatch 'Fix BUG-0001') 0
    $r = ShellEdit $bugCall 'Bash'
    Check 'round-cap: a bugs.py command warns at the cap' ($r.Code -eq 2 -and $r.Out -match 'BUG-0001: fix 2/2' -and $r.Out -match 'at the cap') $true
    BugCli @('stop-rule', 'BUG-0001', 'fix', '--extra-dispatch', 'unused', '--note', 'test') | Out-Null
    Check 'round-cap: a Stop rule silences the at-cap message' (ShellEdit $bugCall).Code 0
    BugCli @('round', 'BUG-0001', 'fix', '+1', '--note', 'test') | Out-Null
    Check 'round-cap: ... and never the past-cap message' ((ShellEdit $bugCall).Out -match 'past the cap') $true
    Bugs 'Reopen' 3
    $r = DispatchR 'Fix BUG-0001'
    Check 'round-cap: the past-cap block names bugs.py extra-round' ($r.Out -match 'bugs\.py extra-round') $true
    BugCli @('extra-round', 'BUG-0001', 'fix', '+1', '--note', 'GD order') | Out-Null
    Check 'round-cap: an extra round raises the cap' (Dispatch 'Fix BUG-0001') 0
    Bugs 'Complete' 3
    Check 'round-cap: a Complete bug is not checked' (Dispatch 'Verify BUG-0001') 0
    Check 'round-cap: a settled bug gets no cap message' (ShellEdit $bugCall).Code 0
    Bugs 'Accepted' 3
    Check 'round-cap: an accepted bug is settled, not capped' (Dispatch 'Bug: BUG-0001') 0
    Bugs 'Duplicate' 3
    Check 'round-cap: a duplicate bug is settled' (Dispatch 'Bug: BUG-0001') 0
    Bugs 'Backlog' 3
    Check 'round-cap: a Backlog bug is not capped' (Dispatch 'Bug: BUG-0001') 0
    Check 'round-cap: an unknown id passes' (Dispatch 'Fix BUG-0999') 0
    Bugs 'Reopen' 3
    Check 'round-cap: a QA brief listing a past-cap bug but charging the feature passes' (Dispatch "Feature: .workflow/features/demo.md`nOpen bugs: BUG-0001") 0
    # Decoding: Out is UTF-8 whatever the console code page is. \u escapes keep this file and the stdin pipe ASCII.
    ClearBugs
    BugCli @('add') '{"title":"Gr\u00f6\u00dfe wrong","description":"d","priority":"Low","repro":"not yet","expected":"e","actual":"a","evidence":"n"}' | Out-Null
    $o = Invoke-Bugs $proj @('show', 'BUG-0001', '--json')
    Check 'bugs: Invoke-Bugs decodes non-ASCII stdout as UTF-8' ($o.State -eq 'Ok' -and $o.Out.Contains("Gr$([char]0xF6)$([char]0xDF)e wrong")) $true
    $o = Invoke-Bugs $proj @('show', 'not-an-id')
    Check 'bugs: Invoke-Bugs reports a CLI failure with its stderr' ($o.State -eq 'Failed' -and $o.Code -eq 1 -and $o.Err -match '^bugs: ') $true
    Check 'bugs: Invoke-Bugs reports a missing script as a failure' ((Invoke-Bugs (Join-Path $tmp 'NoSuchProject') @('stats')).State) 'Failed'
    $o = Invoke-Bugs $proj @('stats') 1
    Check 'bugs: Invoke-Bugs kills a call past its timeout and reports it' ($o.State -eq 'Failed' -and $o.Err -match 'timed out') $true
    # Fail closed. An empty PATH and no cached interpreter stand for a machine without Python.
    $noPyDir = Join-Path $tmp 'empty-path'
    New-Item -ItemType Directory -Force $noPyDir | Out-Null
    $pyCache = Join-Path $proj '.memory/.state/python.txt'
    $savedPath = $env:PATH
    function NoPython([scriptblock]$Body) {
        Remove-Item $pyCache -ErrorAction SilentlyContinue
        $env:PATH = $noPyDir
        try { & $Body } finally { $env:PATH = $savedPath }
    }
    Bugs 'Reopen' 1
    $r = NoPython { DispatchR 'Fix BUG-0001' }
    Check 'round-cap: no Python on a bug dispatch blocks, naming the fix' ($r.Code -eq 2 -and $r.Out -match 'BUG-0001' -and $r.Out -match 'Python 3\.10') $true
    $r = NoPython { DispatchR 'Bug: BUG-0001' }
    Check 'round-cap: no Python on a Bug marker blocks' $r.Code 2
    Check 'round-cap: no Python leaves a brief naming no bug alone' (NoPython { Dispatch 'Explain the HUD' }) 0
    $r = NoPython { ShellEdit $bugCall }
    Check 'round-cap: no Python on a bugs.py command gives a message only' ($r.Code -eq 2 -and $r.Out -match 'could not be read' -and $r.Out -notmatch 'Stop rule') $true
    ClearBugs
    Check 'round-cap: no journal and no bugs.md pass without Python' (NoPython { Dispatch 'Fix BUG-0001' }) 0
    Check 'round-cap: a shell command with no journal stays silent without Python' (NoPython { (ShellEdit $bugCall).Code }) 0
    $oldBugs = Join-Path $proj '.workflow/bugs.md'
    Set-Content $oldBugs "# Bugs`n" -Encoding UTF8
    $r = DispatchR 'Fix BUG-0001'
    Check 'round-cap: a remaining bugs.md blocks a bug dispatch, naming import-md' ($r.Code -eq 2 -and $r.Out -match 'import-md') $true
    Check 'round-cap: a remaining bugs.md leaves other dispatches alone' (Dispatch 'Explain the HUD') 0
    Remove-Item $oldBugs
    # A merge of two branches that each filed a bug: two real create lines holding one id.
    BugCli @('add') $bugFields | Out-Null
    $oneLine = Get-Content (Join-Path $proj '.workflow/bugs.jsonl') -Raw
    ClearBugs
    BugCli @('add') $bugFields | Out-Null
    [IO.File]::AppendAllText((Join-Path $proj '.workflow/bugs.jsonl'), $oneLine)
    $r = DispatchR 'Fix BUG-0001'
    Check 'round-cap: a duplicate id blocks, naming doctor --fix' ($r.Code -eq 2 -and $r.Out -match 'doctor --fix') $true
    $r = ShellEdit $bugCall
    Check 'round-cap: a CLI failure on a bugs.py command gives its message' ($r.Code -eq 2 -and $r.Out -match 'could not be read' -and $r.Out -match 'duplicate id') $true
    ClearBugs
    # A shell command that does not call bugs.py: nothing runs, not even the ledger step that moves a corrupt file aside.
    $ledgerProbe = Join-Path $proj '.workflow/rounds.json'
    Set-Content $ledgerProbe '{ broken' -Encoding UTF8
    $r = NoPython { ShellEdit 'git log --grep BUG-0001' }
    Check 'round-cap: another shell command is silent' ($r.Code -eq 0 -and -not $r.Out.Trim()) $true
    Check 'round-cap: ... and leaves the ledger alone' ((Test-Path $ledgerProbe) -and -not @(Get-ChildItem (Split-Path $ledgerProbe) -Filter 'rounds.corrupt-*.json').Count) $true
    $r = NoPython { ShellEdit 'python -I bugs.py list --open' 'Bash' }
    Check 'round-cap: a bugs.py command naming no id is silent' ($r.Code -eq 0 -and -not $r.Out.Trim()) $true
    Remove-Item $ledgerProbe
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
    Bugs 'Reopen' 0
    foreach ($n in 1..3) { SubStop 'gameplay-engineer' "Bug: BUG-0001`n$fm" "Status: Failed`nAttempts: 3/3" "f$n" | Out-Null }
    Check 'count: Failed returns are attempts, not rounds' (Dispatch 'Bug: BUG-0001') 0
    SubStop 'playtest-tester' "Bug: BUG-0001`nReproduce it." "Status: Done`nRepro: BUG-0001 reproduces" 'q1' | Out-Null
    Check 'count: reproducing a bug without Verify is not a fix round' (Test-Path $ledger) $false
    SubStop 'playtest-tester' "Verify: BUG-0001`n$fm" "Status: Done`nRepro: BUG-0001 reproduces" 'p1' | Out-Null
    SubStop 'playtest-tester' "Verify: BUG-0001" "Status: Failed`nRepro: BUG-0001 reproduces" 'p2' | Out-Null
    SubStop 'playtest-tester' "Verify: BUG-0001" "Status: Done`nRepro: BUG-0001 gone" 'p3' | Out-Null
    Check 'count: a verify that still fails counts once per run' (Count 'bug:BUG-0001' 'fix') 2
    Check 'count: a verify that still fails adds feature rework' (Count 'feature:demo' 'rework') 1
    SubStop 'code-reviewer' "Round: 1`nBug: BUG-0001" 'Verdict: Request changes' 'b1' | Out-Null
    Check 'count: a no-feature fix review counts on the bug review counter' (Count 'bug:BUG-0001' 'review') 1
    Check 'count: ... and not on its fix counter' (Count 'bug:BUG-0001' 'fix') 2
    Check 'count: used = database + ledger (0 + 2 is at the cap, still dispatches)' (Dispatch 'Bug: BUG-0001') 0
    SubStop 'playtest-tester' "Verify: BUG-0001" "Status: Done`nRepro: BUG-0001 reproduces" 'p4' | Out-Null
    Check 'count: used = database + ledger (0 + 3 past the cap blocks)' (Dispatch 'Bug: BUG-0001') 2
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

    # session-start: the bug line and the purge trigger, in a real repo holding a journal built by the CLI
    ClearBugs
    $bp = Join-Path $tmp 'BugProject'
    New-Repo $bp
    New-Item -ItemType Directory -Force (Join-Path $bp '.claude/skills/bugs/scripts'), (Join-Path $bp '.claude/skills/mem/scripts'), (Join-Path $bp '.claude/hooks') | Out-Null
    Copy-Item (Join-Path $hooks '../skills/bugs/scripts/bugs.py') (Join-Path $bp '.claude/skills/bugs/scripts')
    Copy-Item (Join-Path $hooks '../skills/mem/scripts/mem.py') (Join-Path $bp '.claude/skills/mem/scripts')
    Copy-Item (Join-Path $hooks 'secret-patterns.txt') (Join-Path $bp '.claude/hooks')
    $bugRoot = $bp
    $bpGit = @('-C', $bp, '-c', 'user.name=t', '-c', 'user.email=t@example.com', '-c', 'core.autocrlf=false')
    $bpJournal = Join-Path $bp '.workflow/bugs.jsonl'
    # BUG-0001 went terminal 100 days ago (BUGS_NOW is the CLI's test clock); BUG-0002 is open, High.
    $env:BUGS_NOW = (Get-Date).ToUniversalTime().AddDays(-100).ToString('yyyy-MM-ddTHH:mm:ss') + 'Z'
    BugCli @('add') $bugFields | Out-Null
    MoveBug 'BUG-0001' 'As designed'
    Remove-Item Env:BUGS_NOW
    BugCli @('add') $bugFields | Out-Null
    git @bpGit add .workflow/bugs.jsonl 2>&1 | Out-Null
    git @bpGit commit -q -m 'journal' 2>&1 | Out-Null
    $env:CLAUDE_PROJECT_DIR = $bp
    $env:HOOK_TEST_XERJ = 'none'
    # Feature branch first: the journal must still hold the expired bug when the purge case runs.
    git @bpGit checkout -q -b feature/x 2>&1 | Out-Null
    $r = Invoke-Hook 'session-start.ps1' @{}
    Check 'session-start: a feature branch skips the purge' ($r.Code -eq 0 -and $r.Out -match '(?m)^Bugs: 1 open \(1 High\+\)\s*$') $true
    Check 'session-start: ... and writes no journal' ((git @bpGit status --porcelain -- .workflow/bugs.jsonl | Out-String).Trim()) ''
    git @bpGit checkout -q - 2>&1 | Out-Null
    # A dirty journal: an uncommitted real write.
    BugCli @('add') $bugFields | Out-Null
    $dirty = [IO.File]::ReadAllText($bpJournal)
    $r = Invoke-Hook 'session-start.ps1' @{}
    Check 'session-start: a dirty journal skips the purge' ($r.Code -eq 0 -and $r.Out -match '(?m)^Bugs: 2 open \(2 High\+\)\s*$') $true
    Check 'session-start: ... and leaves the journal as it was' ([IO.File]::ReadAllText($bpJournal)) $dirty
    git @bpGit checkout -q -- .workflow/bugs.jsonl 2>&1 | Out-Null
    $r = Invoke-Hook 'session-start.ps1' @{}
    Check 'session-start: an expired terminal bug is purged, with the line shown' ($r.Code -eq 0 -and $r.Out -match '(?m)^Bugs: 1 open \(1 High\+\); purged 1, journal uncommitted\s*$') $true
    Check 'session-start: ... the bug is gone' ((BugCli @('counters', 'BUG-0001', '--json')) -match '"found": false') $true
    Check 'session-start: ... and nothing was committed' (@(git @bpGit log --oneline).Count) 1
    Check 'session-start: ... the journal is left uncommitted' ([bool](git @bpGit status --porcelain -- .workflow/bugs.jsonl | Out-String).Trim()) $true
    $saved = [IO.File]::ReadAllText($bpJournal)
    [IO.File]::WriteAllText($bpJournal, "{ not json`n")
    $r = Invoke-Hook 'session-start.ps1' @{}
    Check 'session-start: a CLI error prints a short line and never fails' ($r.Code -eq 0 -and $r.Out -match '(?m)^Bugs: unavailable - bugs: ' -and $r.Out -match 'Search: Grep') $true
    [IO.File]::WriteAllText($bpJournal, $saved)
    $pyCache = Join-Path $bp '.memory/.state/python.txt'
    $r = NoPython { Invoke-Hook 'session-start.ps1' @{} }
    Check 'session-start: no Python with a journal prints a short line and never fails' ($r.Code -eq 0 -and $r.Out -match '(?m)^Bugs: unavailable - install Python') $true
    Remove-Item $bpJournal
    Remove-Item (Join-Path $bp '.workflow/bugs.db*') -Force -ErrorAction SilentlyContinue
    $r = NoPython { Invoke-Hook 'session-start.ps1' @{} }
    Check 'session-start: no journal prints no bug line and needs no Python' ($r.Code -eq 0 -and $r.Out -notmatch 'Bugs:') $true
    Set-Content (Join-Path $bp '.workflow/bugs.md') "# Bugs`n" -Encoding UTF8
    $r = NoPython { Invoke-Hook 'session-start.ps1' @{} }
    Check 'session-start: a remaining bugs.md prints one import-md line' ($r.Code -eq 0 -and @($r.Out -split '\r?\n' | Where-Object { $_ -match '^Bugs: .*import-md' }).Count -eq 1) $true
    $env:CLAUDE_PROJECT_DIR = $proj
    Remove-Item Env:HOOK_TEST_XERJ
    $bugRoot = $proj
    $pyCache = Join-Path $proj '.memory/.state/python.txt'

    # verify-on-edit
    Check 'verify-on-edit ignores files outside .claude' (Invoke-Hook 'verify-on-edit.ps1' @{ tool_input = @{ file_path = "$proj/Assets/A.cs" } }).Code 0
    Check 'verify-on-edit ignores writes inside an agent worktree' (Invoke-Hook 'verify-on-edit.ps1' @{ tool_input = @{ file_path = "$proj/.claude/worktrees/agent-x/.workflow/evidence/r.md" } }).Code 0

    # verify-layer skill format: a copy runs on a planted layer, because the script takes its root from its own path
    $vl = Join-Path $tmp 'VerifyLayer'
    $vlSkills = Join-Path $vl '.claude/skills'
    New-Item -ItemType Directory -Force (Join-Path $vl '.claude/agents'), (Join-Path $vl '.claude/rules'), (Join-Path $vl '.claude/hooks'), (Join-Path $vlSkills 'verify-layer/scripts') | Out-Null
    Copy-Item (Join-Path $hooks '../skills/verify-layer/scripts/verify.ps1') (Join-Path $vlSkills 'verify-layer/scripts')
    Copy-Item (Join-Path $hooks 'common.ps1'), (Join-Path $hooks 'verify-on-edit.ps1') (Join-Path $vl '.claude/hooks')
    Set-Content (Join-Path $vl 'CLAUDE.md') '# Layer'
    Set-Content (Join-Path $vl 'README.md') '# Layer'
    function Verify([string]$File = '') {
        $verifyArgs = if ($File) { @('-File', $File) } else { @() }
        $out = & $shell -NoProfile -NonInteractive -File (Join-Path $vlSkills 'verify-layer/scripts/verify.ps1') @verifyArgs 2>&1
        return @{ Code = $LASTEXITCODE; Out = ($out -join "`n") }
    }
    function VerifyEdit([string]$Path) {
        $json = @{ tool_input = @{ file_path = $Path } } | ConvertTo-Json -Depth 5 -Compress
        $json | & $shell -NoProfile -NonInteractive -File (Join-Path $vl '.claude/hooks/verify-on-edit.ps1') 2>&1 | Out-Null
        $LASTEXITCODE
    }
    $okDesc = 'Clean.Symbol, Other.Member. Use when checking the fixture.'
    # A template-shaped skill. Each plant changes $Desc or appends $Extra, so the planted line is the only violation.
    function VSkill([string]$Name, [string[]]$Extra = @(), [string]$Desc = $okDesc) {
        $dir = Join-Path $vlSkills $Name
        New-Item -ItemType Directory -Force (Join-Path $dir 'references'), (Join-Path $dir 'scripts') | Out-Null
        Set-Content (Join-Path $dir 'references/topic.md') "# Topic`n`n- A fact."
        Set-Content (Join-Path $dir 'scripts/x.ps1') '# Prints x.'
        Set-Content (Join-Path $dir 'scripts/test_x.py') '# The test of x.'
        Set-Content (Join-Path $dir 'checklist.md') "# Checklist`n`n- [ ] **Done:** it ran."
        $text = @('---', "name: $Name", "description: `"$Desc`"", 'user-invocable: false', '---', '', '# Subject', '',
            '- **Not for:** the layer check (`verify-layer`).', '- **Docs:** https://example.com/docs/ - one caveat.', '',
            '## References', '- **[topic.md](references/topic.md):** on a symptom.', '',
            '## Scripts', '- **[x.ps1](scripts/x.ps1):** run `pwsh -NoProfile -File "${CLAUDE_SKILL_DIR}/scripts/x.ps1"` -> prints x.', '',
            '## Steps', '1. **First:** do it.', '   - **Nested:** titled too.', '2. **Final check:** walk [checklist.md](checklist.md) before returning.', '',
            '## Data', '| Axis | Choice |', '|---|---|', '| a | b |', '',
            '## Never', '- **`Verified` evidence:** a backticked title, as in agent-protocol.', '- **Verified before shipping:** no colon after the word.', '',
            '## Output', '```', '## Subject', 'Status: Done', 'Free text a fence may hold.', '- an untitled bullet in a fence', '```', '',
            '## Example', '- **"Wrong request":** declined - why; did this instead.', '') + $Extra
        Set-Content (Join-Path $dir 'SKILL.md') ($text -join "`n")
    }
    function VRel([string]$Name) { ".claude/skills/$Name/SKILL.md" }
    function VFail([string]$Name) { "FAIL  \.claude/skills/$Name/SKILL\.md: " }
    # What a fresh Windows checkout gives under core.autocrlf: the whole skill folder in CRLF.
    function ToCrlf([string]$Name) {
        foreach ($f in Get-ChildItem (Join-Path $vlSkills $Name) -Recurse -File) {
            [IO.File]::WriteAllText($f.FullName, ([IO.File]::ReadAllText($f.FullName) -replace '\r?\n', "`r`n"))
        }
    }

    # verify-layer: a clean template-shaped skill passes, and its exceptions stay exceptions
    VSkill 'clean-skill'
    VSkill 'crlf-skill'
    ToCrlf 'crlf-skill'
    Check 'verify: the CRLF fixture has no bare LF' ([IO.File]::ReadAllText((Join-Path $vlSkills 'crlf-skill/SKILL.md')) -notmatch '(?<!\r)\n') $true
    $r = Verify (VRel 'clean-skill')
    Check 'verify: a clean template-shaped skill passes per file with no output line' ($r.Code -eq 0 -and $r.Out -cnotmatch 'WARN|FAIL') $true
    $r = Verify (VRel 'crlf-skill')
    Check 'verify: a CRLF copy of it passes per file with no output line' ($r.Code -eq 0 -and $r.Out -cnotmatch 'WARN|FAIL') $true
    $r = Verify
    Check 'verify: ... and on a whole-layer run' ($r.Code -eq 0 -and $r.Out -cnotmatch 'WARN|FAIL' -and $r.Out -match 'verify-layer: OK \(0 warning\(s\)\)') $true
    VSkill 'trigger-field' @() 'Foo.Bar and Baz.Qux only.'
    $f = Join-Path $vlSkills 'trigger-field/SKILL.md'
    Set-Content $f ((Get-Content $f -Raw) -replace 'user-invocable: false', "when_to_use: `"checking the fixture`"`nuser-invocable: false")
    Check 'verify: when_to_use counts as the Use trigger' (Verify (VRel 'trigger-field')).Code 0
    VSkill 'preloaded-skill' @() 'Foo.Bar and Baz.Qux only.'
    Set-Content (Join-Path $vl '.claude/agents/fixture-agent.md') "---`nname: fixture-agent`ndescription: A fixture.`ntools: Read`nskills:`n  - preloaded-skill`n---`n`n# Fixture"
    Check 'verify: a skill an agent preloads needs no Use trigger' (Verify (VRel 'preloaded-skill')).Code 0
    VSkill 'named-in-ref'
    Set-Content (Join-Path $vlSkills 'named-in-ref/scripts/y.ps1') '# Prints y.'
    Set-Content (Join-Path $vlSkills 'named-in-ref/references/topic.md') "# Topic`n`n- Adapt ../scripts/y.ps1."
    Check 'verify: a script named only in a reference passes' (Verify (VRel 'named-in-ref')).Code 0
    VSkill 'short-fence'
    Set-Content (Join-Path $vlSkills 'short-fence/references/short.md') (@('# Short', '```') + (1..14 | ForEach-Object { "line $_" }) + '```')
    Check 'verify: a 14-line reference fence passes' (Verify '.claude/skills/short-fence/references/short.md').Code 0
    # An unclosed fence runs to the end of the file; the final newline Set-Content adds is no line, so this is 14.
    VSkill 'short-unclosed'
    Set-Content (Join-Path $vlSkills 'short-unclosed/references/short.md') (@('# Short', '```') + (1..14 | ForEach-Object { "line $_" }))
    Check 'verify: an unclosed 14-line reference fence with a final newline passes' (Verify '.claude/skills/short-unclosed/references/short.md').Code 0
    VSkill 'ref-fences-ok'
    $ref8 = @(1..8 | ForEach-Object { "line $_" })
    Set-Content (Join-Path $vlSkills 'ref-fences-ok/references/nested.md') (@('# Nested', '````', '```') + @(1..12 | ForEach-Object { "line $_" }) + @('```', '````'))
    Check 'verify: a nested reference fence of 14 lines passes' (Verify '.claude/skills/ref-fences-ok/references/nested.md').Code 0
    Set-Content (Join-Path $vlSkills 'ref-fences-ok/references/adjacent.md') (@('# Adjacent', '```') + $ref8 + @('```', '```') + $ref8 + '```')
    Check 'verify: two adjacent reference fences count apart' (Verify '.claude/skills/ref-fences-ok/references/adjacent.md').Code 0

    # verify-layer: fences. Their content would fail if read as body; the plants after them are in $plants below.
    $vlLong = '- **Long:** ' + ('x' * 200)
    $fenceNested = @('````', '```', '- an untitled bullet in the inner fence', $vlLong, '```', '- an untitled bullet after the inner fence', '````')
    $fenceTilde = @('~~~', $vlLong, '```', '- an untitled bullet under a lone backtick line', $vlLong, '~~~')
    # A same-character mark with text after it does not close: closing there reads the bullet as body and hides the plant.
    $fenceTrailing = @('```', '``` not a closer', '- an untitled bullet in the fence', '```')
    # A longer mark closes too: demanding the exact length leaves this open and hides the plant.
    $fenceLonger = @('```', '- an untitled bullet in the fence', '````')
    VSkill 'fence-nested' $fenceNested
    $r = Verify (VRel 'fence-nested')
    Check 'verify: a 4-backtick fence holding a 3-backtick fence passes with no output line' ($r.Code -eq 0 -and $r.Out -cnotmatch 'WARN|FAIL') $true
    VSkill 'fence-tilde' $fenceTilde
    $r = Verify (VRel 'fence-tilde')
    Check 'verify: a tilde fence holding 3 backticks passes with no output line' ($r.Code -eq 0 -and $r.Out -cnotmatch 'WARN|FAIL') $true

    # verify-layer: a backticked star in a title, and script folders that are not the skill's own scripts
    VSkill 'title-backtick' @('- **`*.meta` files:** text.')
    Check 'verify: a title may hold a backticked star' (Verify (VRel 'title-backtick')).Code 0
    VSkill 'title-odd-backtick' @('- **A ``` mark:** the fence `code`.', '- **The ` key:** press `Tab` next.')
    Check 'verify: a title may hold an odd backtick run, with a backticked pair after the title' (Verify (VRel 'title-odd-backtick')).Code 0
    VSkill 'checklist-backtick'
    Set-Content (Join-Path $vlSkills 'checklist-backtick/checklist.md') @('# Checklist', '', '- [ ] **`*.meta` files:** present.', '- [ ] **The ` key:** press `Tab` next.')
    Check 'verify: a checklist title takes what a skill title takes' (Verify '.claude/skills/checklist-backtick/checklist.md').Code 0
    VSkill 'ignored-scripts'
    New-Item -ItemType Directory -Force (Join-Path $vlSkills 'ignored-scripts/scripts/__pycache__'), (Join-Path $vlSkills 'ignored-scripts/scripts/.venv/lib') | Out-Null
    Set-Content (Join-Path $vlSkills 'ignored-scripts/scripts/__pycache__/x.cpython-312.pyc') '# Bytecode.'
    Set-Content (Join-Path $vlSkills 'ignored-scripts/scripts/.venv/lib/dep.py') '# A dependency.'
    Check 'verify: __pycache__ and dot-folder files need no name' (Verify (VRel 'ignored-scripts')).Code 0

    # verify-layer: body size does not depend on line endings. Under the budget in LF, over it only through its CRs.
    VSkill 'crlf-size' @(1..310 | ForEach-Object { "- **Item ${_}:** xxxxxx" })
    $sizeBody = [regex]::Match([IO.File]::ReadAllText((Join-Path $vlSkills 'crlf-size/SKILL.md')), '(?s)^---.*?\n---\r?\n(.*)$').Groups[1].Value
    Check 'verify: the size fixture is over budget only with CRs' (($sizeBody -replace '\r', '').Length -le 8000 -and ($sizeBody -replace '\r?\n', "`r`n").Length -gt 8000) $true
    ToCrlf 'crlf-size'
    $r = Verify (VRel 'crlf-size')
    Check 'verify: CRs do not count toward the body size' ($r.Code -eq 0 -and $r.Out -cnotmatch 'WARN|FAIL') $true

    # verify-layer: soft checks only warn, per file and as one count per check on a whole-layer run
    $softDesc = 'Soft.Symbol ' + ('x' * 110) + ' Use when checking.'
    $softBody = @(1..60 | ForEach-Object { "- **Bulk ${_}:** " + ('x' * 140) }) + ('- **Long:** ' + ('x' * 200))
    VSkill 'soft-one' $softBody $softDesc
    VSkill 'soft-two' $softBody $softDesc
    $softChecks = 'description \+ when_to_use > 120 chars', 'list item > 200 chars', 'body > 8000 chars'
    $r = Verify (VRel 'soft-one')
    Check 'soft: exit 0 per file, no FAIL, no count form' ($r.Code -eq 0 -and $r.Out -notmatch 'FAIL|file\(s\):') $true
    foreach ($s in $softChecks) { Check "soft: per-file form: $s" ($r.Out -match "WARN  \.claude/skills/soft-one/SKILL\.md: $s") $true }
    $r = Verify
    Check 'soft: exit 0 on a whole-layer run, no FAIL, no per-file form' ($r.Code -eq 0 -and $r.Out -notmatch 'FAIL|soft-one|soft-two') $true
    foreach ($s in $softChecks) { Check "soft: count form: $s" ($r.Out -match "WARN  2 file\(s\): $s") $true }

    # verify-layer: each promoted check fails on a planted violation, per file and on a whole-layer run
    $vlFence = @('```', '- Known limitations: none', '```')
    $plants = @(
        @('banned-this-skill', 'This skill checks Foo.Bar. Use when checking.', @(), 'description uses a banned phrase'),
        @('banned-comprehensive', 'Comprehensive Foo.Bar. Use when checking.', @(), 'description uses a banned phrase'),
        @('banned-preloaded', 'Foo.Bar. Preloaded by an agent. Use when checking.', @(), 'description uses a banned phrase'),
        @('no-trigger', 'Foo.Bar and Baz.Qux only.', @(), 'description has no Use trigger'),
        @('lowercase-trigger', 'Foo.Bar. use when checking.', @(), 'description has no Use trigger'),
        @('over-250', ('Foo.Bar ' + ('x' * 250) + ' Use when checking.'), @(), 'description \+ when_to_use \d+ > 250 chars'),
        @('latent-concerns', $okDesc, @('- **Latent concerns:** none.'), 'Latent concerns line'),
        @('verified-title', $okDesc, @('- **Verified:** it ran.'), 'Verified or Known limitations bullet'),
        @('limitations-title', $okDesc, @('- **Known limitations:** none.'), 'Verified or Known limitations bullet'),
        @('limitations-in-fence', $okDesc, $vlFence, 'Verified or Known limitations bullet'),
        @('reference-table', $okDesc, @('| Reference | Read when |', '|---|---|', '| a.md | b |'), 'reference or script table'),
        @('script-table', $okDesc, @('| Script | Run |', '|---|---|', '| a.ps1 | b |'), 'reference or script table'),
        @('hardcoded-path', $okDesc, @('- **Run:** `.claude/skills/hardcoded-path/scripts/x.ps1`.'), 'hardcoded script path'),
        @('prose-line', $okDesc, @('A prose paragraph.'), 'untitled list item or prose line'),
        @('plain-bullet', $okDesc, @('- A plain bullet.'), 'untitled list item or prose line'),
        @('star-bullet', $okDesc, @('* **Star:** a star bullet.'), 'untitled list item or prose line'),
        @('nested-bullet', $okDesc, @('- **Parent:** titled.', '  - A plain nested bullet.'), 'untitled list item or prose line'),
        @('numbered-step', $okDesc, @('3. A plain step.'), 'untitled list item or prose line'),
        @('title-bare-star', $okDesc, @('- **A*B:** text.'), 'untitled list item or prose line'),
        @('fence-nested-plant', $okDesc, ($fenceNested + '- A plain bullet after the fence.'), 'untitled list item or prose line'),
        @('fence-tilde-plant', $okDesc, ($fenceTilde + '- A plain bullet after the fence.'), 'untitled list item or prose line'),
        @('fence-trailing-plant', $okDesc, ($fenceTrailing + '- A plain bullet after the fence.'), 'untitled list item or prose line'),
        @('fence-longer-plant', $okDesc, ($fenceLonger + '- A plain bullet after the fence.'), 'untitled list item or prose line')
    )
    foreach ($p in $plants) {
        VSkill $p[0] $p[2] $p[1]
        $r = Verify (VRel $p[0])
        Check "verify fails per file: $($p[0])" ($r.Code -eq 1 -and $r.Out -match "$(VFail $p[0])$($p[3])") $true
    }
    # In a job, so a title pattern that backtracks exponentially fails here instead of hanging the run. Its process runs the
    # check itself and reports its id first: a regex stuck in .NET ignores Stop-Job, so a timeout kills that process.
    function VerifyInJob([string]$File, [int]$Seconds) {
        $job = Start-Job -ArgumentList (Join-Path $vlSkills 'verify-layer/scripts/verify.ps1'), $File -ScriptBlock {
            param($Script, $Target)
            $PID
            $out = & $Script -File $Target 2>&1
            $LASTEXITCODE
            $out -join "`n"
        }
        $finished = [bool](Wait-Job $job -Timeout $Seconds)
        $got = @(Receive-Job $job)
        if (-not $finished -and $got.Count) { Stop-Process -Id $got[0] -Force -ErrorAction SilentlyContinue }
        Remove-Job $job -Force
        @{ TimedOut = -not $finished; Code = $(if ($finished) { $got[1] }); Out = $(if ($finished) { $got[2] }) }
    }
    # Out of $plants and deleted after, so no whole-layer run below reads it.
    VSkill 'backtick-run' @('- **x ' + ('`a` ' * 30) + 'end')
    $r = VerifyInJob (VRel 'backtick-run') 30
    Check 'verify: 30 backticked pairs with no title end finish within 30 s' $r.TimedOut $false
    Check 'verify fails per file: backtick-run' ($r.Code -eq 1 -and $r.Out -match "$(VFail 'backtick-run')untitled list item or prose line") $true
    Remove-Item -Recurse -Force (Join-Path $vlSkills 'backtick-run')
    $r = Verify (VRel 'prose-line')
    $at = (Select-String -LiteralPath (Join-Path $vlSkills 'prose-line/SKILL.md') -SimpleMatch 'A prose paragraph.').LineNumber
    Check 'verify: the untitled FAIL gives the file line number' ($r.Out -match "lines $at\)") $true
    foreach ($vn in 'fence-nested-plant', 'fence-tilde-plant', 'fence-trailing-plant', 'fence-longer-plant') {
        $r = Verify (VRel $vn)
        $at = (Select-String -LiteralPath (Join-Path $vlSkills "$vn/SKILL.md") -SimpleMatch 'A plain bullet after the fence.').LineNumber
        Check "verify: the fence closed, and only the plant after it fails: $vn" ($r.Out -match "lines $at\)") $true
    }
    VSkill 'crlf-prose-line' @('A prose paragraph.')
    ToCrlf 'crlf-prose-line'
    $r = Verify (VRel 'crlf-prose-line')
    $at = (Select-String -LiteralPath (Join-Path $vlSkills 'crlf-prose-line/SKILL.md') -SimpleMatch 'A prose paragraph.').LineNumber
    Check 'verify: a CRLF prose line fails with its file line number' ($r.Code -eq 1 -and $r.Out -match "$(VFail 'crlf-prose-line')untitled list item or prose line \(lines $at\)") $true
    VSkill 'unnamed-script'
    Set-Content (Join-Path $vlSkills 'unnamed-script/scripts/orphan.ps1') '# Named nowhere.'
    $r = Verify (VRel 'unnamed-script')
    Check 'verify fails per file: script not named' ($r.Code -eq 1 -and $r.Out -match "$(VFail 'unnamed-script')script 'orphan\.ps1' not named") $true
    VSkill 'unnamed-nested-script'
    New-Item -ItemType Directory -Force (Join-Path $vlSkills 'unnamed-nested-script/scripts/sub.dir') | Out-Null
    Set-Content (Join-Path $vlSkills 'unnamed-nested-script/scripts/sub.dir/deep.ps1') '# Named nowhere.'
    $r = Verify (VRel 'unnamed-nested-script')
    Check 'verify fails per file: a folder with a dot inside its name is still read' ($r.Code -eq 1 -and $r.Out -match "$(VFail 'unnamed-nested-script')script 'deep\.ps1' not named") $true
    VSkill 'long-fence'
    Set-Content (Join-Path $vlSkills 'long-fence/references/long.md') (@('# Long', '```') + (1..15 | ForEach-Object { "line $_" }) + '```')
    $r = Verify '.claude/skills/long-fence/references/long.md'
    Check 'verify fails per file: a 15-line reference fence' ($r.Code -eq 1 -and $r.Out -match 'FAIL  \.claude/skills/long-fence/references/long\.md: reference has a fenced block of 15\+ lines') $true
    VSkill 'checklist-plain'
    Set-Content (Join-Path $vlSkills 'checklist-plain/checklist.md') @('# Checklist', '', '- [ ] A plain item.')
    $r = Verify '.claude/skills/checklist-plain/checklist.md'
    Check 'verify fails per file: a checklist item with no title' ($r.Code -eq 1 -and $r.Out -match 'FAIL  \.claude/skills/checklist-plain/checklist\.md:3: not a heading') $true
    $longRefs = @(
        @('long-tilde', (@('# Long', '~~~') + (1..15 | ForEach-Object { "line $_" }) + '~~~')),
        # Toggling pairs the outer mark with the inner one and sees two 8-line blocks.
        @('long-nested', (@('# Long', '````') + $ref8 + '```' + $ref8 + '````')),
        # An unclosed fence runs to the end of the file, so its lines count: exactly 15 here, the final newline being no line.
        @('long-unclosed', (@('# Long', '```') + (1..15 | ForEach-Object { "line $_" })))
    )
    foreach ($p in $longRefs) {
        VSkill $p[0]
        Set-Content (Join-Path $vlSkills "$($p[0])/references/long.md") $p[1]
        $r = Verify ".claude/skills/$($p[0])/references/long.md"
        Check "verify fails per file: $($p[0]) reference fence" ($r.Code -eq 1 -and $r.Out -match "FAIL  \.claude/skills/$($p[0])/references/long\.md: reference has a fenced block of 15\+ lines") $true
    }
    $r = Verify
    Check 'verify: a whole-layer run exits 1 on the plants' $r.Code 1
    foreach ($p in $plants) { Check "verify fails whole-layer: $($p[0])" ($r.Out -match "$(VFail $p[0])$($p[3])") $true }
    Check 'verify fails whole-layer: a CRLF prose line' ($r.Out -match "$(VFail 'crlf-prose-line')untitled list item or prose line") $true
    Check 'verify fails whole-layer: script not named' ($r.Out -match "$(VFail 'unnamed-script')script 'orphan\.ps1' not named") $true
    Check 'verify fails whole-layer: a nested script not named' ($r.Out -match "$(VFail 'unnamed-nested-script')script 'deep\.ps1' not named") $true
    Check 'verify fails whole-layer: a 15-line reference fence' ($r.Out -match 'FAIL  \.claude/skills/long-fence/references/long\.md: reference has a fenced block') $true
    foreach ($p in $longRefs) { Check "verify fails whole-layer: $($p[0]) reference fence" ($r.Out -match "FAIL  \.claude/skills/$($p[0])/references/long\.md: reference has a fenced block") $true }
    Check 'verify fails whole-layer: a checklist item with no title' ($r.Out -match 'FAIL  \.claude/skills/checklist-plain/checklist\.md:3: not a heading') $true
    Check 'verify: the whole-layer failure count is the plants and nothing else' ($r.Out -match "$($plants.Count + $longRefs.Count + 5) failure\(s\)") $true
    foreach ($ok in 'clean-skill', 'crlf-skill', 'crlf-size', 'trigger-field', 'preloaded-skill', 'named-in-ref', 'short-fence', 'short-unclosed', 'ref-fences-ok', 'fence-nested', 'fence-tilde', 'title-backtick', 'title-odd-backtick', 'checklist-backtick', 'ignored-scripts', 'soft-one') {
        Check "verify: no FAIL for $ok among the plants" ($r.Out -match "FAIL  [^\n]*/$ok/") $false
    }
    foreach ($s in $softChecks) { Check "soft: still only a count among the plants: $s" ($r.Out -match "WARN  2 file\(s\): $s") $true }
    Check 'verify-on-edit passes an edit of a clean skill' (VerifyEdit (Join-Path $vlSkills 'clean-skill/SKILL.md')) 0
    Check 'verify-on-edit blocks an edit that plants a violation' (VerifyEdit (Join-Path $vlSkills 'plain-bullet/SKILL.md')) 2
    # The raw path a Windows session can send: a lowercase drive letter and forward slashes. An unshortened path skips every check.
    if ($env:OS -eq 'Windows_NT') {
        $rawPath = (Join-Path $vlSkills 'plain-bullet/SKILL.md') -replace '\\', '/'
        $rawPath = $rawPath.Substring(0, 1).ToLowerInvariant() + $rawPath.Substring(1)
        Check 'verify-on-edit blocks an edit given as a lowercase drive and forward slashes' (VerifyEdit $rawPath) 2
    }

    # verify-layer: a long item after a fence still warns, so the fence closed for the size check too. Last: the whole-layer
    # counts above hold only soft-one and soft-two.
    foreach ($p in @(@('fence-nested-long', $fenceNested), @('fence-tilde-long', $fenceTilde))) {
        VSkill $p[0] ($p[1] + $vlLong)
        $r = Verify (VRel $p[0])
        Check "soft: a long item after the fence warns: $($p[0])" ($r.Code -eq 0 -and $r.Out -match 'list item > 200 chars') $true
    }

    # verify-layer: line endings change nothing in the output. An item of exactly the budget warns only if a CR counts; the
    # prose line gives both runs an output to compare, line number included.
    $eolBody = @(('- **Edge:** ' + ('x' * 188)), 'A prose paragraph.')
    VSkill 'eol-lf' $eolBody
    VSkill 'eol-cr' $eolBody
    ToCrlf 'eol-cr'
    $lfRun = Verify (VRel 'eol-lf')
    $crRun = Verify (VRel 'eol-cr')
    Check 'verify: a CRLF copy gives the output of its LF original, name aside' ($lfRun.Out -match 'lines \d+\)' -and $crRun.Code -eq $lfRun.Code -and ($crRun.Out -replace 'eol-cr', 'eol-lf') -ceq $lfRun.Out) $true

    # verify-layer: the table check matches the old table's header only. Last, as above: no whole-layer count below reads these.
    VSkill 'data-table' @('| Reference | Owner |', '|---|---|', '| Reference | a data row |', '| Script | another |', '| Script | Run later |')
    $r = Verify (VRel 'data-table')
    Check 'verify: a data table with Reference or Script as a first cell passes with no output line' ($r.Code -eq 0 -and $r.Out -cnotmatch 'WARN|FAIL') $true
    VSkill 'crlf-table' @('| Script | Run |', '|---|---|', '| a.ps1 | b |')
    ToCrlf 'crlf-table'
    $r = Verify (VRel 'crlf-table')
    Check 'verify fails per file: the old table header in CRLF' ($r.Code -eq 1 -and $r.Out -match "$(VFail 'crlf-table')reference or script table") $true

    # verify-layer: -File on a reference runs the owning skill's script-named check.
    VSkill 'named-then-dropped'
    Set-Content (Join-Path $vlSkills 'named-then-dropped/scripts/y.ps1') '# Prints y.'
    Set-Content (Join-Path $vlSkills 'named-then-dropped/references/topic.md') "# Topic`n`n- Adapt ../scripts/y.ps1."
    Check 'verify: -File on a reference that names the script passes' (Verify '.claude/skills/named-then-dropped/references/topic.md').Code 0
    Set-Content (Join-Path $vlSkills 'named-then-dropped/references/topic.md') "# Topic`n`n- A fact."
    $r = Verify '.claude/skills/named-then-dropped/references/topic.md'
    Check 'verify fails on -File: a reference edit drops the only name of a script' ($r.Code -eq 1 -and $r.Out -match "$(VFail 'named-then-dropped')script 'y\.ps1' not named") $true
    Check 'verify: -File on a named script passes' (Verify '.claude/skills/clean-skill/scripts/x.ps1').Code 0
    # Production passes the raw absolute path, which the trigger must shorten first.
    $droppedRef = Join-Path $vlSkills 'named-then-dropped/references/topic.md'
    Check 'verify-on-edit blocks a reference edit, by absolute path, that drops the only name of a script' (VerifyEdit $droppedRef) 2
    if ($env:OS -eq 'Windows_NT') {
        $rawPath = $droppedRef -replace '\\', '/'
        $rawPath = $rawPath.Substring(0, 1).ToLowerInvariant() + $rawPath.Substring(1)
        Check 'verify-on-edit blocks that edit given as a lowercase drive and forward slashes' (VerifyEdit $rawPath) 2
    }

    # verify-layer: each contract table names what depends on the lost string. Removed after, so no run below reads them.
    $contractRule = Join-Path $vl '.claude/rules/routing.md'
    Set-Content $contractRule '# Routing'
    $r = Verify '.claude/rules/routing.md'
    Check 'verify fails per file: a file missing a hook contract string' ($r.Code -eq 1 -and $r.Out -match "FAIL  \.claude/rules/routing\.md: lost 'extra round', which hooks/round-cap\.ps1 counts on") $true
    Set-Content $contractRule '# Routing - extra round'
    Check 'verify: the same file with the string passes' (Verify '.claude/rules/routing.md').Code 0
    Remove-Item $contractRule
    $workflows = Join-Path $vl '.claude/workflows'
    New-Item -ItemType Directory -Force $workflows | Out-Null
    $gateMarkers = @('export const meta = {}', "lines.push('Mode: workflow')", 'lines.push(`Round: ${round}`)', 'lines.push(`Tree: ${scope.tree}`)')
    Set-Content (Join-Path $workflows 'review-gate.js') $gateMarkers
    $r = Verify '.claude/workflows/review-gate.js'
    Check 'verify fails per file: a workflow missing its review contract string' ($r.Code -eq 1 -and $r.Out -match "FAIL  \.claude/workflows/review-gate\.js: lost 'roundId: round', which /review and workflow review-gate share" -and $r.Out -notmatch 'round-cap') $true
    Set-Content (Join-Path $workflows 'review-gate.js') ($gateMarkers + 'const x = { roundId: round }')
    Check 'verify: the same workflow with the string passes' (Verify '.claude/workflows/review-gate.js').Code 0
    Remove-Item -Recurse -Force $workflows

    # verify-layer: a parent folder named scripts or assets must not hide the layer from a whole-layer run.
    foreach ($parent in 'scripts', 'assets') {
        $pl = Join-Path $tmp "Parents/$parent/Layer"
        $plSkills = Join-Path $pl '.claude/skills'
        New-Item -ItemType Directory -Force (Join-Path $pl '.claude/agents'), (Join-Path $pl '.claude/rules'), (Join-Path $plSkills 'verify-layer/scripts') | Out-Null
        Copy-Item (Join-Path $vlSkills 'verify-layer/scripts/verify.ps1') (Join-Path $plSkills 'verify-layer/scripts')
        Copy-Item -Recurse (Join-Path $vlSkills 'plain-bullet') $plSkills
        $out = & $shell -NoProfile -NonInteractive -File (Join-Path $plSkills 'verify-layer/scripts/verify.ps1') 2>&1
        Check "verify fails whole-layer under a parent folder named ${parent}: a planted violation" ($LASTEXITCODE -eq 1 -and ($out -join "`n") -match "$(VFail 'plain-bullet')untitled list item or prose line") $true
    }

    # verify-layer: in a clean layer, a whole-layer run skips a violating .md under a skill's own scripts/ or assets/, and a
    # skill folder with no SKILL.md has no script check. -File reads the same .md, which proves the plant violates.
    $il = Join-Path $tmp 'InLayer'
    $ilSkills = Join-Path $il '.claude/skills'
    New-Item -ItemType Directory -Force (Join-Path $il '.claude/agents'), (Join-Path $il '.claude/rules'), (Join-Path $ilSkills 'verify-layer/scripts'), (Join-Path $ilSkills 'no-skill-md/scripts'), (Join-Path $ilSkills 'no-skill-md/references') | Out-Null
    $ilVerifier = Join-Path $ilSkills 'verify-layer/scripts/verify.ps1'
    Copy-Item (Join-Path $vlSkills 'verify-layer/scripts/verify.ps1') $ilVerifier
    Copy-Item -Recurse (Join-Path $vlSkills 'clean-skill') $ilSkills
    # Named, so the script check has nothing to say about the plant under scripts/.
    Set-Content (Join-Path $ilSkills 'clean-skill/references/topic.md') "# Topic`n`n- A fact.`n- See notes.md."
    foreach ($sub in 'scripts', 'assets') {
        New-Item -ItemType Directory -Force (Join-Path $ilSkills "clean-skill/$sub") | Out-Null
        Set-Content (Join-Path $ilSkills "clean-skill/$sub/notes.md") '- [broken](missing.md)'
        $out = & $shell -NoProfile -NonInteractive -File $ilVerifier -File ".claude/skills/clean-skill/$sub/notes.md" 2>&1
        Check "verify fails on -File: the .md planted under in-layer ${sub}/" ($LASTEXITCODE -eq 1 -and ($out -join "`n") -match "link 'missing\.md' does not exist") $true
    }
    Set-Content (Join-Path $ilSkills 'no-skill-md/scripts/orphan.ps1') '# Named nowhere.'
    Set-Content (Join-Path $ilSkills 'no-skill-md/references/topic.md') '# Topic'
    foreach ($f in 'references/topic.md', 'scripts/orphan.ps1') {
        & $shell -NoProfile -NonInteractive -File $ilVerifier -File ".claude/skills/no-skill-md/$f" 2>&1 | Out-Null
        Check "verify: -File on $f in a folder with no SKILL.md passes, an unnamed script beside it" $LASTEXITCODE 0
    }
    $out = & $shell -NoProfile -NonInteractive -File $ilVerifier 2>&1
    Check 'verify: a whole-layer run passes over a violating .md in in-layer scripts/ and assets/ and a folder with no SKILL.md' ($LASTEXITCODE -eq 0 -and ($out -join "`n") -cnotmatch 'FAIL') $true
}
finally {
    Remove-Item Env:CLAUDE_PROJECT_DIR, Env:HOOK_TEST_XERJ, Env:MEM_CAPTURE, Env:XERJ_URL, Env:BUGS_NOW -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}

if ($failures) { Write-Output "$failures failure(s)"; exit 1 }
Write-Output 'hooks: all tests passed'
exit 0
