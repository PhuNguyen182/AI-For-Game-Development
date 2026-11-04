# Shared helpers for the framework's hooks. Dot-source it: . "$PSScriptRoot/common.ps1"

# Secret shapes live in secret-patterns.txt so mem.py scans with the same list.
# Missing, empty or unreadable -> Find-Secrets blocks: the security hooks fail closed.
$script:SecretPatterns = [ordered]@{}
try {
    foreach ($line in [IO.File]::ReadAllLines((Join-Path $PSScriptRoot 'secret-patterns.txt'))) {
        if ($line -match '^\s*(#|$)') { continue }
        $pair = $line -split "`t", 2
        if ($pair.Count -ne 2) { throw "malformed line: $line" }
        [void][regex]::new($pair[1])  # an invalid regex throws here, not silently at match time
        $script:SecretPatterns[$pair[0]] = $pair[1]
    }
} catch { $script:SecretPatterns = [ordered]@{} }

# Files that legitimately contain the patterns above, by repo-relative path anchored at the root: the hook scripts,
# the pattern list, the hook tests and the scan skill's docs. A same-named folder deeper in the tree is scanned.
$script:SecretScanExempt = '(?i)^\.claude/(?:hooks/(?:[^/]+\.ps1|secret-patterns\.txt|tests/run\.ps1)|skills/secret-and-supply-chain-scan/(?:[^/]+/)*[^/]+\.md)$'

# True when $Path (absolute, or relative to $Root) is one of the exempt files above.
function Test-SecretScanExempt([string]$Path, [string]$Root) {
    $rel = $Path -replace '\\', '/'
    if ($Root) {
        $r = (([IO.Path]::GetFullPath($Root)) -replace '\\', '/').TrimEnd('/') + '/'
        if ($rel.StartsWith($r, [StringComparison]::OrdinalIgnoreCase)) { $rel = $rel.Substring($r.Length) }
    }
    return $rel -match $script:SecretScanExempt
}

# First non-empty argument. Stands in for ?? so the hooks also run on Windows PowerShell 5.1.
function First { foreach ($v in $args) { if ($null -ne $v -and [string]$v -ne '') { return $v } }; return $null }

# A command with heredoc / here-string bodies removed and multi-word quoted text blanked to Q, so a commit message
# that mentions `git push --force` is not read as one. A one-word quoted value ('+main', "--force") keeps its text;
# a quoted path to git itself ("C:/Program Files/Git/cmd/git.exe") reads as git.
function Remove-HeredocBody([string]$Command) {
    $c = [regex]::Replace($Command, '<<-?\s*([''"]?)(\w+)\1[^\n]*\n[\s\S]*?\n\s*\2[ \t]*(?=\r?\n|$)', ' ')
    return [regex]::Replace($c, '@([''"])\r?\n[\s\S]*?\r?\n\1@', ' ')
}
function Remove-QuotedText([string]$Command) {
    $c = Remove-HeredocBody $Command
    return [regex]::Replace($c, '"([^"]*)"|''([^'']*)''', { param($m) $v = $m.Groups[1].Value + $m.Groups[2].Value
            if ($v -match '(?i)(?:^|[\\/])git(?:\.exe)?$') { 'git' } elseif ($v -match '^\S+$') { $v } else { 'Q' } })
}

# `-c <key>=<value>` keys that run a program, rewire a transport or drop a safety check: refused on the command line.
$script:GitUnsafeConfig = '(?i)^(?:core\.(?:sshcommand|fsmonitor|pager|editor|hookspath|askpass|gitproxy)|sequence\.editor|diff\.external|' +
    '[\w.-]*\.textconv|credential\.[\w.-]*helper|uploadpack\.[\w.-]+|protocol\.[\w.-]*allow|gpg\.[\w.-]*program|filter\.[\w.-]+|' +
    'merge\.[\w.-]+\.driver|clean\.requireforce|alias\.[\w.-]+|remote\.[\w.-]+\.(?:mirror|push|uploadpack|receivepack))$'

# Git's global options before the verb (-C dir, -c k=v, --no-pager, --git-dir x, ...).
$script:GitArg = '(?:"[^"]*"|''[^'']*''|\S+)'
$script:GitOpt = "(?:-[Cc]\s+$script:GitArg|--(?:git-dir|work-tree|namespace|config-env|exec-path)(?:=|\s+)$script:GitArg|--[\w-]+(?:=$script:GitArg)?|-[A-Za-z]+)"
$script:GitShellScript = '(?i)\b(?:sh|bash|zsh|dash|pwsh|powershell|cmd)(?:\.exe)?\s+(?:-[A-Za-z]*c\b|-Command\b|/c\b)'

# Every `git <verb> <args>` a shell command runs, as { Globals, Verb, Rest, Alias, Why }. Reads through commit-message
# text (blanked), the quoted script of an sh/bash/pwsh/cmd -c wrapper, and an alias configured in $Cwd's repo or
# the user's config. Why is set, and the call refused, for config nothing on disk shows: `-c alias.*`, GIT_CONFIG_*.
function Get-GitCalls([string]$Command, [string]$Cwd, [int]$Depth = 0) {
    $texts = @(Remove-QuotedText $Command)
    if ($Command -match $script:GitShellScript) {
        $texts += ($Command -replace '[\x22\x27]', ' ')
    }
    # Read on the raw command: a quoted `-c "core.sshCommand=..."` is blanked in $texts.
    foreach ($m in [regex]::Matches($Command, '(?:^|\s)(?:-c\s*|--config-env[=\s])[\x22\x27]?([A-Za-z][\w.-]*)=')) {
        if ($m.Groups[1].Value -match $script:GitUnsafeConfig -or $m.Value -match 'config-env') {
            [pscustomobject]@{ Globals = ''; Verb = ''; Rest = ''; Alias = $false; Why = "git -c $($m.Groups[1].Value) (config that runs a program or drops a check)" }
        }
    }
    foreach ($text in $texts) {
        if ($text -match '\bGIT_CONFIG_(?:COUNT|PARAMETERS|KEY_\d+)\b') {
            [pscustomobject]@{ Globals = ''; Verb = ''; Rest = ''; Alias = $false; Why = 'git config set through GIT_CONFIG_* environment variables' }
        }
        foreach ($m in [regex]::Matches($text, "\bgit(?:\.exe)?\b((?:\s+$script:GitOpt)*)\s+([\w-]+)([^;&|\r\n]*)", 'IgnoreCase')) {
            $globals = $m.Groups[1].Value; $verb = $m.Groups[2].Value.ToLowerInvariant(); $rest = $m.Groups[3].Value
            if ($globals -match '(?i)\balias\.') {
                [pscustomobject]@{ Globals = $globals; Verb = $verb; Rest = $rest; Alias = $true; Why = 'an alias defined on the command line (-c alias.*)' }
                continue
            }
            $alias = $null
            # git ignores an alias named after a builtin: `alias.push = status` does not stop `git push --force` being a push.
            if ($verb -notin 'commit', 'push' -and $Depth -lt 3 -and $Cwd -and (Test-Path -LiteralPath $Cwd)) { $alias = [string](git -C $Cwd config --get "alias.$verb" 2>$null) }
            if (-not $alias) { [pscustomobject]@{ Globals = $globals; Verb = $verb; Rest = $rest; Alias = $false; Why = $null }; continue }
            if ($alias.StartsWith('!')) {
                foreach ($c in (Get-GitCalls $alias.Substring(1) $Cwd ($Depth + 1))) { $c.Alias = $true; $c }
                continue
            }
            $parts = @($alias.Trim() -split '\s+', 2)
            [pscustomobject]@{ Globals = $globals; Verb = $parts[0].ToLowerInvariant(); Rest = ' ' + (@($parts[1], $rest) -join ' '); Alias = $true; Why = $null }
        }
    }
}

# The last check on a command Read-GateCommand read as Kind None: does the text still run $Verb? A heredoc body is text, and
# so is quoted text unless a shell -c outside the quotes could run it (a commit message may name both).
function Test-GateCallHit([string]$Command, [string]$Cwd, [string]$Verb) {
    $blank = Remove-QuotedText $Command
    $text = if ($blank -match $script:GitShellScript) { Remove-HeredocBody $Command } else { $blank }
    return [bool]@(Get-GitCalls $text $Cwd | Where-Object { $_.Verb -eq $Verb }).Count
}

# Words of a git call's arguments up to `--` (after it come paths, never options).
function Get-GitWords([string]$Rest) {
    $words = @()
    foreach ($m in [regex]::Matches($Rest, '"[^"]*"|''[^'']*''|\S+')) {
        $t = $m.Value.Trim('"', "'")
        if ($t -eq '--') { break }
        $words += $t
    }
    return $words
}

# Force, delete, mirror, prune, all-tags and anchor-tag pushes are blast radius 3: the GD runs them. A glob deny
# misses combined short flags (-uf), unique long-option prefixes (--mirr) and +/: refspecs, so read the arguments.
$script:PushRadius3 = 'force', 'force-with-lease', 'force-if-includes', 'mirror', 'delete', 'prune', 'tags', 'receive-pack', 'exec'
function Find-PushRadius3([string]$Globals, [string]$Rest) {
    if ($Globals -match '(?i)remote\.\S+\.(?:mirror|push)\b|--config-env') { return 'a remote mirror/push refspec set on the command line' }
    $skip = $false
    foreach ($m in [regex]::Matches($Rest, '"[^"]*"|''[^'']*''|\S+')) {
        $t = $m.Value.Trim('"', "'")
        if ($skip) { $skip = $false; continue }
        if ($t -match '^--(?!no-)([\w-]+)') {
            $name = $Matches[1]
            if ($script:PushRadius3 | Where-Object { $_.StartsWith($name) }) { return $m.Value }
            if ('push-option', 'repo', 'recurse-submodules' -contains $name -and $t -notmatch '=') { $skip = $true }
        } elseif ($t -match '^-([A-Za-z0-9]+)$') {
            $cluster = $Matches[1]
            $flags = ($cluster -csplit 'o', 2)[0]  # -o takes the rest of the cluster, or the next word, as its value
            if ($flags -cmatch '[fd]') { return $m.Value }
            if ($cluster -cmatch '^[^o]*o$') { $skip = $true }
        } elseif ($t -match '^[+:]') { return "$($m.Value) (a + refspec forces, a : refspec deletes)" }
        elseif ($t -match '(?:^|:)(?:refs/tags/)?backup/') { return "$($m.Value) (a backup/* anchor tag stays local)" }
        elseif ($t -match '\*') { return "$($m.Value) (a pattern refspec pushes every matching ref, backup/* anchors included)" }
    }
    return $null
}

# Bytes, decoded as UTF-8: [Console]::In takes the console code page, which turns a non-ASCII path into one that does not exist.
function Read-HookInput {
    $buffer = New-Object IO.MemoryStream
    $stdin = [Console]::OpenStandardInput()
    try { $stdin.CopyTo($buffer) } finally { $stdin.Dispose() }
    $bytes = $buffer.ToArray()
    try { $raw = (New-Object Text.UTF8Encoding $false, $true).GetString($bytes) }
    catch { $raw = [Console]::InputEncoding.GetString($bytes) }
    $raw = $raw.TrimStart([char]0xFEFF)
    if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
    try { return $raw | ConvertFrom-Json } catch { return $null }
}

# Returns one "<kind>: <redacted sample>" line per pattern that matches. Never echoes the full value.
function Find-Secrets([string]$Text) {
    if ($script:SecretPatterns.Count -eq 0) {
        Block 'Blocked: .claude/hooks/secret-patterns.txt is missing, empty or malformed - secrets cannot be scanned. Restore it from git.'
    }
    $hits = @()
    if ([string]::IsNullOrEmpty($Text)) { return $hits }
    foreach ($name in $script:SecretPatterns.Keys) {
        $m = [regex]::Match($Text, $script:SecretPatterns[$name])
        if ($m.Success) {
            $v = $m.Value
            $sample = if ($v.Length -gt 8) { $v.Substring(0, 6) + '...' } else { '...' }
            $hits += "${name}: $sample"
        }
    }
    return $hits
}

# "secret in <file>: <kind>" for each file whose added lines in a unified diff (`git diff`, `git log -p`) match a
# pattern. One regex pass per file and pattern: a per-line loop takes minutes on a multi-megabyte scene and outruns
# the hook timeout.
function Find-AddedSecrets([string]$Diff) {
    $problems = @()
    foreach ($section in [regex]::Split($Diff, '(?m)^\+\+\+ b/')) {
        $nl = $section.IndexOf("`n")
        if ($nl -lt 0) { continue }
        $file = $section.Substring(0, $nl).TrimEnd("`r")
        if ($file -match $script:SecretScanExempt) { continue }
        $added = [regex]::Replace($section.Substring($nl + 1), '(?m)^(?:[^+\n].*)?(?:\n|$)', '')
        $added = [regex]::Replace($added, '(?m)^\+', '')
        # JSON escapes quotes (\"), which hides quoted-value patterns in .jsonl traces.
        if ($file -like '*.jsonl') { $added = $added.Replace('\"', '"') }
        foreach ($h in (Find-Secrets $added)) { $problems += "secret in ${file}: $h" }
    }
    return $problems
}

# A git diff/log command's whole output as one string. git writes it to a temp file (--output): PowerShell reads
# native output one line at a time, which alone takes seconds on a multi-megabyte scene.
# core.quotepath=off: a non-ASCII name stays `+++ b/<name>`, not a quoted header the per-file split would miss.
function Get-GitDiffText([string]$Root, [string[]]$GitArgs) {
    $tmp = [IO.Path]::GetTempFileName()
    try {
        git -C $Root -c core.quotepath=off @GitArgs "--output=$tmp" 2>$null | Out-Null
        # A failed git call leaves an empty file, which would read as "nothing to scan": fail closed instead.
        if ($LASTEXITCODE -ne 0) { Block "Blocked: git $($GitArgs -join ' ') failed (exit $LASTEXITCODE) - the change cannot be scanned for secrets." }
        return [IO.File]::ReadAllText($tmp)
    } finally { Remove-Item -LiteralPath $tmp -ErrorAction SilentlyContinue }
}

# Files that never enter git whatever their content: keystores, certificates and provisioning profiles, .env files,
# SSH keys, the UPM registry auth file, service-account JSON (rule core.md -> Security). Case-insensitive.
# Templates are allowed (GD decision): .env.example / .env.sample / .env.template and public keys (*.pub); their content
# is still secret-scanned like any file.
$script:SecretPathRegex = '(?i)\.(?:keystore|jks|p12|pfx|p8|pem|mobileprovision)$|(?:^|/)\.env(?:$|\.(?!(?:example|sample|template)$))|(?:^|/)id_rsa(?![^/]*\.pub$)|\.upmconfig\.toml$|service[-_]?account[^/]*\.json$'
# Under .workflow/evidence/ only reports and screenshots are committed: raw logcat, syslog and crash dumps carry
# other apps' data, tokens and player PII. They stay local (.gitignore) and a report cites a path or a redacted excerpt.
$script:EvidenceExt = '.md', '.png'
# Unity Editor session data (rule core.md -> Security): the cache folders at a project root, and the files that hold
# session tokens wherever they are copied.
$script:EditorCacheRegex = '(?i)^(?:(?!Assets/|Packages/)[^/]+/)?(?:Library|Temp|Logs|UserSettings)/|(?:^|/)(?:UnityConnectCache\.json|EditorUserSettings\.asset|\.unity-pipeline-port)$'

# Every change in `git diff --raw -z` / `git log --raw -z` output as { Path, Status, Mode, Blob } (the new side).
# Pass --no-renames so each record names one path.
function Get-GitRawChanges([string]$Root, [string[]]$GitArgs) {
    $tokens = (Get-GitDiffText $Root (@($GitArgs) + @('--raw', '-z', '--no-abbrev', '--no-renames'))) -split "`0"
    for ($i = 0; $i -lt $tokens.Count - 1; $i++) {
        $m = [regex]::Match($tokens[$i].Trim(), '^:\d+ (\d+) [0-9a-f]+ ([0-9a-f]+) ([A-Z])\d*$')
        if (-not $m.Success) { continue }
        $i++
        [pscustomobject]@{ Path = $tokens[$i]; Status = $m.Groups[3].Value; Mode = $m.Groups[1].Value; Blob = $m.Groups[2].Value }
    }
}

# One problem line per added or modified file that must not be committed: a secret-bearing path, raw evidence, or a
# .json whose content is a service-account key. A deletion is never a problem: it is how such a file leaves the tree.
function Find-ForbiddenFiles([string]$Root, [object[]]$Changes) {
    $problems = @()
    foreach ($c in $Changes) {
        if (-not $c -or $c.Status -eq 'D') { continue }
        $p = $c.Path
        if ($p -match $script:SecretPathRegex) { $problems += "secret file: $p (keystore, certificate, .env, key or service-account file)"; continue }
        if ($p -match $script:EditorCacheRegex) { $problems += "Editor session data: $p (Library/, Temp/, Logs/, UserSettings/ and their token files never enter git)"; continue }
        if ($p -match '(?i)^\.workflow/evidence/' -and $script:EvidenceExt -notcontains [IO.Path]::GetExtension($p).ToLowerInvariant()) {
            $problems += "raw evidence: $p (only .md reports and .png screenshots are committed under .workflow/evidence/; the dump stays local, a report cites its path or a redacted excerpt)"
            continue
        }
        if ($p -notmatch '(?i)\.json$' -or $c.Mode -notmatch '^100') { continue }
        # A service-account key is about 2 KB; a JSON over 1 MB is data, not a credential.
        if ([long](First (git -C $Root cat-file -s $c.Blob 2>$null) 0) -gt 1MB) { continue }
        if (((git -C $Root cat-file blob $c.Blob 2>$null) -join "`n") -match '"type"\s*:\s*"service_account"') {
            $problems += "service-account key: $p (a Google service-account JSON never enters git; reference it from a secret store)"
        }
    }
    return $problems
}

# The main checkout for a project root: Claude Code creates agent worktrees at <project>/.claude/worktrees/<name>, and a
# hook running for such an agent may get that worktree as its project root. Lane detection and the Editor lock must
# still resolve to the main checkout.
function Get-MainCheckout([string]$Root) {
    if (-not $Root) { return $Root }
    # Only a real agent worktree: the prefix is a checkout (holds .git), so a project whose own path merely contains
    # .claude/worktrees/ keeps its root.
    # The outermost prefix whose .git is a directory (a main checkout; a worktree's .git is a file) wins, so both a project
    # that itself sits under .claude/worktrees/ and a worktree nested in a worktree resolve to their real main checkout.
    $p = $Root -replace '\\', '/'
    foreach ($m in [regex]::Matches($p, '/\.claude/worktrees/[^/]+(?=/|$)')) {
        $prefix = $p.Substring(0, $m.Index)
        if (Test-Path -LiteralPath (Join-Path $prefix '.git') -PathType Container) { return $prefix }
    }
    return $Root
}

# The checkout whose .workflow holds the bug journal, known before any Python starts. $Root is the project root, as the hooks
# pass it, and only its own .git counts: a link planted above a project cannot pick the folder whose script and cached
# interpreter run. A linked worktree anywhere reads its main checkout's, so a branch with no journal cannot hide a past-cap
# bug. main_checkout in bugs.py is the same rule, and tests/run.ps1 drives both over the same layouts. Starts no process: reads the .git file, then <gitdir>/commondir, as UTF-8. Captured git output
# decodes with the console code page, and a wrong folder would read as "no bugs". Throws when the links lead nowhere or the
# common folder is not named .git (a bare repo, a submodule's worktree): a caller naming a bug blocks, a session prints a line.
# A bare repo stored in a folder named .git looks like a checkout: it returns that folder's parent, normally with no journal.
function Get-BugsRoot([string]$Root) {
    $utf8 = New-Object Text.UTF8Encoding $false
    $dir = [IO.Path]::GetFullPath($Root)
    $link = [IO.Path]::Combine($dir, '.git')
    if (-not [IO.File]::Exists($link)) { return $Root }  # a main checkout, or no checkout: its own journal
    $m = [regex]::Match([IO.File]::ReadAllText($link, $utf8), '(?m)^gitdir:\s*(.+?)\s*$')
    if (-not $m.Success) { throw "$link names no gitdir, so the main checkout's bug journal cannot be found" }
    $gitDir = [IO.Path]::GetFullPath([IO.Path]::Combine($dir, $m.Groups[1].Value))
    if (-not [IO.Directory]::Exists($gitDir)) { throw "$gitDir, named by $link, does not exist" }
    $commonFile = [IO.Path]::Combine($gitDir, 'commondir')
    if (-not [IO.File]::Exists($commonFile)) {
        # Objects of its own: a full git dir, a submodule or --separate-git-dir. Without them a worktree's admin folder lost the file.
        if ([IO.Directory]::Exists([IO.Path]::Combine($gitDir, 'objects'))) { return $Root }
        throw "$commonFile is missing and $gitDir holds no objects, so the main checkout's bug journal cannot be found"
    }
    $common = [IO.Path]::GetFullPath([IO.Path]::Combine($gitDir, [IO.File]::ReadAllText($commonFile, $utf8).Trim())).TrimEnd('\', '/')
    if ([IO.Path]::GetFileName($common) -cne '.git') { throw "$common is no checkout's .git, so the bug journal cannot be found" }
    if (-not [IO.Directory]::Exists($common)) { throw "$common, named by $commonFile, does not exist" }
    return [IO.Path]::GetDirectoryName($common)
}

# git's full path from PATH, or $null. A bare 'git' given to Process.Start goes to CreateProcess, which tries the current
# folder before PATH: a git.exe in the hook's working folder would run, and its output would pick the repository to scan.
function Get-GitExe {
    $cmd = Get-Command git -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cmd) { return $cmd.Source }
    return $null
}

# git's trimmed stdout for a query run in $Dir, or $null when git is missing or refuses. A Process, not &: & decodes git's
# UTF-8 stdout with the console code page.
function Get-GitQuery([string]$Dir, [string[]]$GitArgs) {
    $exe = Get-GitExe
    if (-not $exe) { return $null }
    $utf8 = New-Object Text.UTF8Encoding $false
    $psi = New-Object Diagnostics.ProcessStartInfo
    $psi.FileName = $exe
    $psi.Arguments = (@(@('-C', $Dir) + @($GitArgs) | ForEach-Object { ConvertTo-NativeArg $_ }) -join ' ')
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.StandardOutputEncoding = $utf8
    $psi.StandardErrorEncoding = $utf8
    try {
        $p = [Diagnostics.Process]::Start($psi)
        $p.StandardInput.Close()
        $outRead = $p.StandardOutput.ReadToEndAsync()
        $errRead = $p.StandardError.ReadToEndAsync()
        if (-not $p.WaitForExit(10000)) { try { $p.Kill() } catch {}; return $null }
        [void]$errRead.GetAwaiter().GetResult()
        $text = $outRead.GetAwaiter().GetResult().Trim()
        if ($p.ExitCode -eq 0) { return $text }
    } catch {}
    return $null
}

# The working tree git reports for $Dir, or $null.
function Get-GitTopLevel([string]$Dir) {
    $top = Get-GitQuery $Dir @('rev-parse', '--show-toplevel')
    if ($top -and [IO.Directory]::Exists($top)) { return $top }
    return $null
}

# True when git reads $Dir as a bare repository, which has no working tree to name.
function Test-GitBare([string]$Dir) {
    return (Get-GitQuery $Dir @('rev-parse', '--is-bare-repository')) -eq 'true'
}

# True when $Dir or a folder above it is a repository as git reads one: a .git file, a .git folder holding HEAD, or a folder
# laid out as a git directory itself (HEAD, objects, refs), which a bare repository is.
function Test-InsideGitRepo([string]$Dir) {
    $d = $Dir
    while ($d) {
        $git = [IO.Path]::Combine($d, '.git')
        if ([IO.File]::Exists($git) -or [IO.File]::Exists([IO.Path]::Combine($git, 'HEAD'))) { return $true }
        if ([IO.File]::Exists([IO.Path]::Combine($d, 'HEAD')) -and [IO.Directory]::Exists([IO.Path]::Combine($d, 'objects')) -and [IO.Directory]::Exists([IO.Path]::Combine($d, 'refs'))) { return $true }
        $d = [IO.Path]::GetDirectoryName($d)
    }
    return $false
}

# The repository a secret gate must scan: the first of $Dirs git names a root for, or with -AllowBare a bare repository,
# which a push runs from and has no root to name. $null when none of the existing $Dirs holds a repository, which is not
# proof the command cannot run: the caller checks the session cwd exists. An existing folder inside a repository git cannot
# name blocks at once: moving on to the next folder would scan a repository the command never touches.
function Resolve-GitRoot([string[]]$Dirs, [string]$What, [switch]$AllowBare) {
    foreach ($d in $Dirs) {
        if (-not $d -or -not [IO.Directory]::Exists($d)) { continue }
        $top = Get-GitTopLevel $d
        if ($top) { return $top }
        if ($AllowBare -and (Test-GitBare $d)) { return [IO.Path]::GetFullPath($d) }
        if (Test-InsideGitRepo ([IO.Path]::GetFullPath($d))) { Block "Blocked: $d is inside a git repository, but git cannot name its root, so the $What cannot be scanned for secrets. Run git rev-parse --show-toplevel there to see why." }
    }
    return $null
}

# The session cwd, or $null when the hook input names none, or a folder that does not exist (a missing field, a path the
# input's bytes garbled). A secret gate never passes on that: only an existing folder outside any repository proves the
# command cannot run. Git Bash spells C:\ as /c/.
function Get-GateCwd($HookInput, [string]$Tool) {
    $c = ConvertFrom-BashDrive ([string]$HookInput.cwd) $Tool
    if (-not $c -or -not [IO.Path]::IsPathRooted($c) -or -not [IO.Directory]::Exists($c)) { return $null }
    return $c
}

function ConvertFrom-BashDrive([string]$Path, [string]$Tool) {
    if ($env:OS -eq 'Windows_NT' -and $Tool -ne 'PowerShell' -and $Path -match '^/([a-zA-Z])(/|$)') { return "$($Matches[1]):/" + $Path.Substring(3) }
    return $Path
}

# ------------------------------------------------------------------------------------------------------------------------
# The closed list of commit and push forms the secret gates accept. A regex cannot parse a shell, and a form the gate reads
# wrongly scans the wrong repository and passes, so a gate never guesses: it reads the command the way the shell tokenises
# it (quotes, heredocs and here-strings are text, $(...) and backticks are commands), accepts the forms in Read-GateCommand
# and refuses the rest with the way to re-run it.

function Add-ShellText($c, [string]$Text) {
    if (-not $c.W) { $c.W = @{ V = New-Object Text.StringBuilder; Q = $false; D = $false; E = $false } }
    [void]$c.W.V.Append($Text)
}

function Close-ShellWord($c) {
    if (-not $c.W) { return }
    [void]$c.Words.Add([pscustomobject]@{ Value = $c.W.V.ToString(); Quoted = $c.W.Q; Dynamic = $c.W.D; Escaped = $c.W.E })
    $c.W = $null
}

function Close-ShellStatement($c, [string]$Sep) {
    Close-ShellWord $c
    if ($c.Words.Count -eq 0) { return }
    [void]$c.Into.Add([pscustomobject]@{ Words = @($c.Words.ToArray()); Sep = $Sep })
    $c.Words = New-Object Collections.ArrayList
}

# True when text the shell expands (an unquoted heredoc, a double-quoted here-string) holds a substitution near a commit or push.
function Test-ActiveBody([string]$Body) {
    return ($Body -match '\$\(|`') -and ($Body -match '(?i)\bgit\b[^\n]*\b(?:commit|push)\b')
}

# $s.I sits on `<<`. Records the delimiter; the body is skipped at the end of this line, and the rest of the line is commands.
function Read-ShellHeredocStart($s, $c) {
    $t = $s.T; $n = $t.Length
    $s.I += 2
    $strip = $false
    if ($s.I -lt $n -and $t[$s.I] -ceq [char]'-') { $strip = $true; $s.I++ }
    while ($s.I -lt $n -and ($t[$s.I] -ceq [char]' ' -or $t[$s.I] -ceq [char]"`t")) { $s.I++ }
    $delim = New-Object Text.StringBuilder
    $quoted = $false
    while ($s.I -lt $n) {
        $ch = [string]$t[$s.I]
        if ($ch -ceq "'" -or $ch -ceq '"') {
            $end = $t.IndexOf($ch, $s.I + 1, [StringComparison]::Ordinal)
            if ($end -lt 0) { throw 'an unterminated heredoc delimiter' }
            [void]$delim.Append($t.Substring($s.I + 1, $end - $s.I - 1))
            $quoted = $true
            $s.I = $end + 1
        } elseif ($ch -ceq '\' -and $s.I + 1 -lt $n) {
            [void]$delim.Append($t[$s.I + 1]); $quoted = $true; $s.I += 2
        } elseif ($ch -match '[\s;&|<>()]') { break }
        else { [void]$delim.Append($ch); $s.I++ }
    }
    if ($delim.Length -eq 0) { throw 'a heredoc with no delimiter' }
    [void]$s.Heredocs.Add(@{ Delim = $delim.ToString(); Strip = $strip; Quoted = $quoted })
    Add-ShellText $c '<<'
    Close-ShellWord $c
}

# $s.I sits on the newline that ends a line with heredoc operators. Leaves it on the newline after the last body.
function Skip-ShellHeredocs($s) {
    $t = $s.T; $n = $t.Length
    foreach ($h in $s.Heredocs) {
        $start = $s.I + 1
        $pos = $start
        $found = $false
        while ($pos -le $n) {
            # Ordinal: the culture-sensitive overload can miss the `n of a CRLF under ICU.
            $e = if ($pos -lt $n) { $t.IndexOf("`n", $pos, [StringComparison]::Ordinal) } else { -1 }
            if ($e -lt 0) { $e = $n }
            $line = $t.Substring($pos, $e - $pos).TrimEnd("`r")
            if ($h.Strip) { $line = $line.TrimStart("`t") }
            if ($line -ceq $h.Delim) {
                if (-not $h.Quoted -and (Test-ActiveBody $t.Substring($start, $pos - $start))) { throw 'an unquoted heredoc that expands a substitution near a commit or push' }
                $s.I = $e
                $found = $true
                break
            }
            if ($e -ge $n) { break }
            $pos = $e + 1
        }
        if (-not $found) { throw "a heredoc with no closing $($h.Delim) line" }
    }
    $s.Heredocs.Clear()
}

# A double-quoted string; $s.I sits on the opening quote.
function Read-ShellDouble($s, $c) {
    $t = $s.T; $n = $t.Length
    Add-ShellText $c ''
    $c.W.Q = $true
    $s.I++
    while ($s.I -lt $n) {
        $ch = [string]$t[$s.I]
        $nx = if ($s.I + 1 -lt $n) { [string]$t[$s.I + 1] } else { '' }
        if ($ch -ceq '"') {
            if ($s.Ps -and $nx -ceq '"') { Add-ShellText $c '"'; $s.I += 2; continue }
            $s.I++
            return
        }
        if ($ch -ceq '\' -and -not $s.Ps) {
            if ($nx -ceq "`n") { $s.I += 2; continue }
            if ($nx -and '$`"\'.Contains($nx)) { Add-ShellText $c $nx; $s.I += 2; continue }
            Add-ShellText $c $ch; $s.I++
            continue
        }
        if ($ch -ceq '`') {
            $c.W.D = $true
            if ($s.Ps) { Add-ShellText $c $nx; $s.I += 2; continue }
            $s.I++
            Read-ShellStatements $s '`' $s.Nested
            continue
        }
        if ($ch -ceq '$') {
            $c.W.D = $true
            if ($nx -ceq '(') { $s.I += 2; Read-ShellStatements $s ')' $s.Nested; continue }
            Add-ShellText $c $ch; $s.I++
            continue
        }
        Add-ShellText $c $ch
        $s.I++
    }
    throw 'an unterminated double quote'
}

# Reads statements up to $Close (end of text when empty) into $Into. Each is { Words; Sep } where Sep is the separator after it.
function Read-ShellStatements($s, [string]$Close, $Into) {
    if (++$s.Depth -gt 16) { throw 'substitutions nested too deeply' }
    $c = @{ Words = New-Object Collections.ArrayList; W = $null; Into = $Into }
    $t = $s.T; $n = $t.Length
    while ($s.I -lt $n) {
        $ch = [string]$t[$s.I]
        $nx = if ($s.I + 1 -lt $n) { [string]$t[$s.I + 1] } else { '' }
        if ($Close -and $ch -ceq $Close) { $s.I++; Close-ShellStatement $c ''; $s.Depth--; return }
        if ($ch -ceq "`n") {
            Close-ShellStatement $c "`n"
            if ($s.Heredocs.Count) { Skip-ShellHeredocs $s }
            $s.I++
        } elseif ($ch -ceq ' ' -or $ch -ceq "`t" -or $ch -ceq "`r") {
            Close-ShellWord $c; $s.I++
        } elseif ($ch -ceq '#' -and -not $c.W) {
            while ($s.I -lt $n -and $t[$s.I] -cne [char]"`n") { $s.I++ }
        } elseif ($ch -ceq ';') {
            Close-ShellStatement $c ';'; $s.I++
        } elseif ($ch -ceq '&') {
            if ($nx -ceq '&') { Close-ShellStatement $c '&&'; $s.I += 2 }
            elseif ($nx -ceq '>' -and -not $s.Ps) { Add-ShellText $c '&>'; $s.I += 2 }
            elseif (-not $c.W -and $c.Words.Count -eq 0) { [void]$c.Words.Add([pscustomobject]@{ Value = '&'; Quoted = $false; Dynamic = $false; Escaped = $false }); $s.I++ }  # the call operator
            else { Close-ShellStatement $c '&'; $s.I++ }
        } elseif ($ch -ceq '|') {
            if ($nx -ceq '|') { Close-ShellStatement $c '||'; $s.I += 2 }
            elseif ($nx -ceq '&') { Close-ShellStatement $c '|'; $s.I += 2 }
            else { Close-ShellStatement $c '|'; $s.I++ }
        } elseif ($ch -ceq '(') {
            Add-ShellText $c ''; $c.W.D = $true
            $s.I++
            Read-ShellStatements $s ')' $s.Nested
        } elseif ($ch -ceq ')') {
            throw 'an unmatched )'
        } elseif ($ch -ceq '<' -and $nx -ceq '<' -and -not $s.Ps) {
            if ($s.I + 2 -lt $n -and $t[$s.I + 2] -ceq [char]'<') { Add-ShellText $c '<<<'; $s.I += 3 }
            else { Read-ShellHeredocStart $s $c }
        } elseif ($ch -ceq '<' -or $ch -ceq '>') {
            if ($nx -ceq '(' -and -not $s.Ps) {
                Add-ShellText $c ''; $c.W.D = $true
                $s.I += 2
                Read-ShellStatements $s ')' $s.Nested
            } else {
                Add-ShellText $c $ch; $s.I++
                if ($nx -ceq '&' -or $nx -ceq '>') { Add-ShellText $c $nx; $s.I++ }
            }
        } elseif ($ch -ceq '{' -or $ch -ceq '}') {
            Close-ShellWord $c
            [void]$c.Words.Add([pscustomobject]@{ Value = $ch; Quoted = $false; Dynamic = $false; Escaped = $false })
            $s.I++
        } elseif ($ch -ceq '\' -and -not $s.Ps) {
            if ($nx -ceq "`n") { $s.I += 2 }
            elseif ($nx -ceq "`r") { $s.I += 3 }
            else { Add-ShellText $c $nx; $c.W.E = $true; $s.I += 2 }
        } elseif ($ch -ceq '`') {
            if ($s.Ps) {
                if ($nx -ceq "`n") { $s.I += 2 }
                elseif ($nx -ceq "`r") { $s.I += 3 }
                else { Add-ShellText $c $nx; $c.W.D = $true; $s.I += 2 }
            } else {
                Add-ShellText $c ''; $c.W.D = $true
                $s.I++
                Read-ShellStatements $s '`' $s.Nested
            }
        } elseif ($ch -ceq "'") {
            Add-ShellText $c ''; $c.W.Q = $true
            while ($true) {
                $end = $t.IndexOf("'", $s.I + 1, [StringComparison]::Ordinal)
                if ($end -lt 0) { throw 'an unterminated single quote' }
                Add-ShellText $c $t.Substring($s.I + 1, $end - $s.I - 1)
                $s.I = $end + 1
                if ($s.Ps -and $s.I -lt $n -and $t[$s.I] -ceq [char]"'") { Add-ShellText $c "'"; continue }
                break
            }
        } elseif ($ch -ceq '"') {
            Read-ShellDouble $s $c
        } elseif ($ch -ceq '$') {
            Add-ShellText $c ''; $c.W.D = $true
            if ($nx -ceq '(') { $s.I += 2; Read-ShellStatements $s ')' $s.Nested }
            elseif ($nx -ceq '{') {
                $end = $t.IndexOf('}', $s.I)
                if ($end -lt 0) { throw 'an unterminated ${' }
                Add-ShellText $c $t.Substring($s.I, $end - $s.I + 1)
                $s.I = $end + 1
            } else { Add-ShellText $c $ch; $s.I++ }
        } elseif ($ch -ceq '@' -and $s.Ps -and -not $c.W -and ($here = [regex]::new('\G@([''"])[ \t]*\r?\n').Match($t, $s.I)).Success) {
            $q = $here.Groups[1].Value
            $bodyAt = $here.Index + $here.Length
            $end = $t.IndexOf("`n$q@", $bodyAt - 1, [StringComparison]::Ordinal)
            if ($end -lt 0) { throw 'a here-string with no closing line' }
            if ($q -ceq '"' -and $end -gt $bodyAt -and (Test-ActiveBody $t.Substring($bodyAt, $end - $bodyAt))) { throw 'a double-quoted here-string that expands a substitution near a commit or push' }
            Add-ShellText $c 'Q'; $c.W.Q = $true
            $s.I = $end + 3
        } else {
            Add-ShellText $c $ch; $s.I++
        }
    }
    if ($Close) { throw "a substitution with no closing $Close" }
    if ($s.Heredocs.Count) { throw 'a heredoc with no body' }
    Close-ShellStatement $c ''
    $s.Depth--
}

# The commit or push calls a statement runs: { Index; Verb; VerbAt; Class }, Class 'commit', 'push', or 'any' for a verb the
# shell fills in. An echo runs nothing; its words are text.
function Get-StatementCalls($Statement) {
    $ws = @($Statement.Words)
    if ($ws[0].Value -ceq 'echo') { return }
    for ($i = 0; $i -lt $ws.Count; $i++) {
        if ($ws[$i].Value -match '(?i)(?:^|[\\/])git-(commit|push)(?:\.exe)?$') {
            [pscustomobject]@{ Index = $i; VerbAt = $i; Class = $Matches[1].ToLowerInvariant() }
            continue
        }
        if ($ws[$i].Value -notmatch '(?i)(?:^|[\\/])git(?:\.exe)?$') { continue }
        $j = $i + 1
        while ($j -lt $ws.Count) {
            $v = $ws[$j].Value
            if ('-C', '-c', '--git-dir', '--work-tree', '--namespace', '--super-prefix', '--config-env', '--attr-source' -ccontains $v) { $j += 2; continue }
            if ($v.StartsWith('-')) { $j++; continue }
            break
        }
        if ($j -ge $ws.Count) { continue }
        $class = $null
        $verb = $ws[$j].Value
        if ($ws[$j].Dynamic) { $class = 'any' }
        elseif ($verb -ieq 'commit') { $class = 'commit' }
        elseif ($verb -ieq 'push') { $class = 'push' }
        elseif ('merge', 'rebase', 'cherry-pick', 'revert' -contains $verb -and $j + 1 -lt $ws.Count -and $ws[$j + 1].Value -ceq '--continue') { $class = 'commit' }
        if ($class) { [pscustomobject]@{ Index = $i; VerbAt = $j; Class = $class } }
    }
    # A program name the shell fills in: $git commit, $(which git) push, & $git commit.
    $k = if ($ws[0].Value -ceq '&') { 1 } else { 0 }
    if ($k -lt $ws.Count -and $ws[$k].Dynamic) {
        foreach ($w in @($ws | Select-Object -Skip ($k + 1))) {
            if ($w.Value -ceq 'commit' -or $w.Value -ceq 'push') { [pscustomobject]@{ Index = $k; VerbAt = $k; Class = $w.Value }; break }
        }
    }
}

# A directory word of an accepted form as a full path, or a reason it is not one: { Dir; Why }. A literal path has no $, ~, %,
# backtick or subshell and names a folder that exists; a relative one resolves against $Base. $Wildcards: PowerShell's cd and
# Set-Location read wildcards, so `[` there can land in another folder; -LiteralPath and git -C read the path as it is.
function Resolve-GatePath($Word, [string]$Base, [string]$Tool, [bool]$Wildcards) {
    function No([string]$Why) { [pscustomobject]@{ Dir = $null; Why = $Why } }
    $v = $Word.Value
    if (-not $v) { return No 'an empty directory' }
    if ($Word.Dynamic -or $v -match '[$~%`]') { return No "the shell-expanded directory $v" }
    if ($Word.Escaped) { return No 'a backslash outside quotes, which Bash reads as an escape: quote the path or use forward slashes' }
    if (-not $Word.Quoted -and $v -match '[*?\[\]]') { return No "the wildcard directory $v" }
    if ($Wildcards -and $v -match '[*?\[\]]') { return No "the directory $v, which PowerShell's cd and Set-Location read as a wildcard: use Set-Location -LiteralPath or git -C" }
    if ($v.StartsWith('-')) { return No "the directory $v, which reads as an option" }
    $p = ConvertFrom-BashDrive $v $Tool
    if ($env:OS -eq 'Windows_NT' -and ($p -match '^[/\\](?![/\\])' -or $p -match '^[A-Za-z]:(?![/\\])')) { return No "the directory $v, which is not a full path: name the drive (C:/...)" }
    if (-not [IO.Path]::IsPathRooted($p)) { $p = [IO.Path]::Combine($Base, $p) }
    $full = [IO.Path]::GetFullPath($p)
    if (-not [IO.Directory]::Exists($full)) { return No "the directory $v, which does not exist" }
    return [pscustomobject]@{ Dir = $full; Why = $null }
}

# Reads a command for a secret gate, $Verb 'commit' or 'push': { Kind; Why; Dir; Globals; Rest; VerbName }.
# Kind None: no such call, nothing to scan. Kind Refuse: Why says why, and how to re-run it. Kind Scan: scan Dir.
#
# Accepted, exactly:
#   git [-c k=v]... commit|push ...
#   git -C <literal path> [-c k=v]... commit|push ...
#   either after one `cd <literal path> &&` or, in PowerShell, `Set-Location [-LiteralPath] <literal path>;`
#   stdin forms: `git commit -F - <<'EOF'`, `$msg | git commit -F -`, after `$msg = <text>`
#   an `echo <literal text>` before it, and any later statement that holds no second commit or push
#   the skills' prompt switches (Test-GateEnv) as leading NAME=VALUE words in Bash, or `$env:NAME = 'v';` in PowerShell
# Everything else that runs a commit or push is refused.
function Test-GateEnv([string]$Name, [string]$Value) {
    if ($Value -match '[$`%]') { return $false }
    if ($Name -ceq 'GIT_SSH_COMMAND') { return $Value -ceq 'ssh -o BatchMode=yes' }
    if ($Name -ceq 'GIT_EDITOR') { return $Value -ceq 'true' }  # any other value is a program that runs after the scan
    return 'GIT_TERMINAL_PROMPT', 'GCM_INTERACTIVE' -ccontains $Name
}

function Read-GateCommand([string]$Command, [string]$Tool, [string]$Cwd, [string]$Verb) {
    function Refuse([string]$Why) {
        $form = "git $Verb ..., git -C <path> $Verb ..., cd <path> && git $Verb ..."
        [pscustomobject]@{ Kind = 'Refuse'; Why = "$Why. Re-run it in a simple form, one call per command with a literal path: $form (Bash), or Set-Location -LiteralPath <path>; git $Verb ... (PowerShell)." }
    }
    $none = [pscustomobject]@{ Kind = 'None'; Why = $null }
    $gateVerb = if ($Verb -eq 'push') { 'push(?![\w.-])' } else { 'commit(?![\w.-])|(?:merge|rebase|cherry-pick|revert)\s+--continue\b' }

    $s = @{ T = $Command; I = 0; Ps = ($Tool -eq 'PowerShell'); Top = New-Object Collections.ArrayList; Nested = New-Object Collections.ArrayList; Heredocs = New-Object Collections.ArrayList; Depth = 0 }
    try { Read-ShellStatements $s '' $s.Top }
    catch {
        $word = if ($Verb -eq 'push') { 'push' } else { 'commit|--continue' }
        if ($Command -match "(?is)\bgit\b.*(?:$word)") { return Refuse "this command cannot be parsed ($($_.Exception.Message))" }
        return $none
    }
    $top = @($s.Top.ToArray()); $nested = @($s.Nested.ToArray())

    $calls = @()
    for ($i = 0; $i -lt $top.Count; $i++) { foreach ($c in @(Get-StatementCalls $top[$i])) { $calls += [pscustomobject]@{ Call = $c; At = $i; Nested = $false } } }
    foreach ($st in $nested) { foreach ($c in @(Get-StatementCalls $st)) { $calls += [pscustomobject]@{ Call = $c; At = -1; Nested = $true } } }
    $mine = @($calls | Where-Object { $_.Call.Class -eq $Verb -or $_.Call.Class -eq 'any' })

    # The script of a wrapper is one quoted word, so git and the verb are looked for on the raw text, and the wrapper may sit
    # anywhere in its statement (timeout 60 bash -c, { bash -c; }). A statement that is git, or that only prints text or takes
    # a path (echo, cd source), runs no script: its words are arguments. Leading NAME=VALUE words are not the program.
    # Statements after the call are skipped (git push && npm start) unless the text holds the verb beyond the call's own words:
    # bash -c "git push", and a heredoc or an echo fed to a shell, both hold it where the words of the later statement may not.
    $wrapper ='(?i)(?:^|[\\/])(?:sh|bash|zsh|dash|ksh|pwsh|powershell|cmd|eval|xargs|exec|source|iex|invoke-expression|start-process|saps|start)(?:\.exe)?$'
    $inline = '(?i)(?:^|[\\/])(?:python3?|py|node|perl|ruby)(?:\.exe)?$'
    if ($Command -match "(?is)\bgit(?:\.exe)?\b.*\b(?:$gateVerb)") {
        $checked = @($top)
        $topCalls = @($mine | Where-Object { -not $_.Nested })
        if ($topCalls.Count) {
            $callText = @($top[$topCalls[0].At].Words | ForEach-Object { $_.Value }) -join ' '
            $verbs = '(?i)commit|push|--continue'
            if ([regex]::Matches($Command, $verbs).Count -le [regex]::Matches($callText, $verbs).Count) { $checked = @($top | Select-Object -First ($topCalls[0].At + 1)) }
        }
        foreach ($st in $checked + @($nested)) {
            $sw = @($st.Words)
            $at = 0
            while ($at -lt $sw.Count -and $sw[$at].Value -cmatch '^[A-Za-z_]\w*=') { $at++ }
            if ($at -ge $sw.Count) { continue }
            $head = $sw[$at].Value
            if ($head -match '(?i)(?:^|[\\/])git(?:\.exe)?$' -or $head -ceq 'echo' -or $head -ceq 'cd' -or $head -ieq 'Set-Location') { continue }
            for ($i = $at; $i -lt $sw.Count; $i++) {
                $word = $sw[$i].Value
                if ($word -match $wrapper) { return Refuse "a $Verb reached through $word, which the scan cannot read" }
                if ($word -match $inline -and @($sw | Select-Object -Skip ($i + 1) | Where-Object { $_.Value -ceq '-c' -or $_.Value -ceq '-e' }).Count) { return Refuse "a $Verb reached through $word, which the scan cannot read" }
            }
        }
    }
    if (-not $mine.Count) { return $none }
    if (-not $Cwd) { return [pscustomobject]@{ Kind = 'Refuse'; Why = "the hook input names no existing session folder, so the $Verb cannot be scanned for secrets" } }

    foreach ($st in @($top) + @($nested)) {
        foreach ($w in @($st.Words)) {
            if (-not $w.Quoted -and $w.Value -match '(?i)\bGIT_(?:DIR|WORK_TREE|INDEX_FILE|COMMON_DIR)\b') { return Refuse "$($Matches[0]) in the command, which moves the repository away from the one the scan reads" }
        }
    }
    if ($calls.Count -gt 1) { return Refuse 'two commit or push calls in one command' }
    $call = $mine[0]
    if ($call.Nested) { return Refuse "a $Verb inside a subshell or substitution" }
    $ws = @($top[$call.At].Words)
    # Leading NAME=VALUE words the skills prescribe. PowerShell has no such form; there it is `$env:NAME = 'v';`, read below.
    $p = 0
    if (-not $s.Ps) {
        while ($p -lt $ws.Count -and -not $ws[$p].Dynamic -and -not $ws[$p].Escaped -and $ws[$p].Value -cmatch '(?s)^([A-Z_]+)=(.*)$' -and (Test-GateEnv $Matches[1] $Matches[2])) { $p++ }
    }
    if ($call.Call.Index -ne $p) { return Refuse "$($ws[$p].Value) before git on the same statement" }
    $g = $ws[$p]
    if ($g.Value -cne 'git' -or $g.Quoted -or $g.Dynamic -or $g.Escaped) { return Refuse "git spelled $($g.Value)" }
    $verbWord = $ws[$call.Call.VerbAt]
    if ($verbWord.Quoted -or $verbWord.Dynamic -or $verbWord.Escaped -or $verbWord.Value -cne $verbWord.Value.ToLowerInvariant()) { return Refuse "the verb spelled $($verbWord.Value)" }

    # Global options: at most one -C, first, then -c k=v.
    $cWord = $null; $globals = @(); $seenConfig = $false
    for ($j = $p + 1; $j -lt $call.Call.VerbAt; $j++) {
        $v = $ws[$j].Value
        if ($v -ceq '-C') {
            if ($cWord) { return Refuse 'more than one -C' }
            if ($seenConfig) { return Refuse '-C after -c' }
            $j++
            $cWord = $ws[$j]
        } elseif ($v -ceq '-c') {
            $j++
            if ($j -ge $call.Call.VerbAt -or $ws[$j].Value -notmatch '^[A-Za-z][\w.-]*=' -or $ws[$j].Dynamic) { return Refuse 'a -c without a literal key=value' }
            $seenConfig = $true
            $globals += "-c $($ws[$j].Value)"
        } elseif ($v -match '^--(?:git-dir|work-tree)(?:=|$)') { return Refuse "$($Matches[0].TrimEnd('=')), which moves the repository away from the one the scan reads" }
        else { return Refuse "the git option $v" }
    }

    # What runs before the call: `$msg = <text>`, an echo of literal text, the text piped in, one cd.
    $cdWord = $null; $cdWild = $false
    for ($k = 0; $k -lt $call.At; $k++) {
        $st = $top[$k]; $w = @($st.Words); $first = $w[0].Value
        $isVar = $first -match '^\$[A-Za-z_]\w*$'
        if ($isVar -and $w.Count -eq 3 -and $w[1].Value -ceq '=' -and $st.Sep -in ';', "`n") { continue }
        if ($s.Ps -and $first -cmatch '^\$env:(\w+)$' -and $w.Count -eq 3 -and $w[1].Value -ceq '=' -and $w[2].Quoted -and -not $w[2].Dynamic -and $st.Sep -in ';', "`n" -and (Test-GateEnv $Matches[1] $w[2].Value)) { continue }
        if ($w.Count -eq 1 -and $st.Sep -ceq '|' -and $k -eq $call.At - 1 -and ($isVar -or $w[0].Quoted)) { continue }
        if ($first -ceq 'echo' -and $st.Sep -in ';', "`n", '&&', '|' -and -not @($w | Where-Object { $_.Dynamic -or (-not $_.Quoted -and $_.Value -match '[<>]') }).Count) { continue }
        if ($first -match '(?i)^(?:pushd|popd|push-location|pop-location|chdir|sl)$') { return Refuse "$first before the $Verb" }
        $isCd = $first -ceq 'cd'
        $isSl = $s.Ps -and $first -ieq 'Set-Location'
        if ($isCd -or $first -ieq 'Set-Location') {
            if ($cdWord) { return Refuse "more than one cd before the $Verb" }
            $literal = $isSl -and $w.Count -eq 3 -and $w[1].Value -ieq '-LiteralPath'
            $shaped = ($isCd -and $w.Count -eq 2 -and $st.Sep -ceq '&&' -and -not $w[1].Value.StartsWith('/d')) -or ($isSl -and ($w.Count -eq 2 -or $literal) -and $st.Sep -in ';', "`n")
            if (-not $shaped) { return Refuse "the statement $((@($w | ForEach-Object { $_.Value })) -join ' ') $($st.Sep) before the $Verb" }
            $cdWord = $w[$w.Count - 1]
            $cdWild = $s.Ps -and -not $literal
            continue
        }
        if ($Verb -eq 'commit' -and $first -ceq 'git' -and @($w | Where-Object { $_.Value -ceq 'add' -or $_.Value -ceq 'stage' }).Count) {
            return [pscustomobject]@{ Kind = 'Refuse'; Why = '`git add` and `git commit` in one call - this scan runs before the add. Stage in its own call, then commit (skill git-commit).' }
        }
        return Refuse "the statement $first before the $Verb"
    }

    # The repository the form names.
    $dir = $Cwd
    if ($cdWord) {
        $r = Resolve-GatePath $cdWord $Cwd $Tool $cdWild
        if ($r.Why) { return Refuse "cd to $($r.Why)" }
        $dir = $r.Dir
    }
    if ($cWord) {
        $r = Resolve-GatePath $cWord $Cwd $Tool $false
        if ($r.Why) { return Refuse "-C with $($r.Why)" }
        if ($cdWord -and -not [IO.Path]::IsPathRooted((ConvertFrom-BashDrive $cWord.Value $Tool))) { return Refuse 'a cd, then a relative -C' }
        $dir = $r.Dir
    }

    # The arguments as text for the rules that read them, split on spaces: a word keeps its head (--message=a b, -m"a b", +x y).
    $rest = @($ws | Select-Object -Skip ($call.Call.VerbAt + 1) | ForEach-Object { if ($_.Value) { $_.Value -replace '\s+', '_' } else { 'Q' } }) -join ' '
    return [pscustomobject]@{ Kind = 'Scan'; Why = $null; Dir = $dir; Globals = ($globals -join ' '); Rest = " $rest"; VerbName = $verbWord.Value }
}

# The folder above $Path that holds a .git entry (directory or file), or $null.
function Get-GitCheckout([string]$Path) {
    $dir = $Path
    while ($dir) {
        if (Test-Path -LiteralPath (Join-Path $dir '.git')) { return [IO.Path]::GetFullPath($dir).TrimEnd('\', '/') }
        $parent = Split-Path $dir
        if ($parent -eq $dir) { break }
        $dir = $parent
    }
    return $null
}

# True when $Path sits in a linked git worktree other than $Root's own checkout: a /feature lane A worktree. The
# project may itself be a linked worktree; only a different checkout counts. Mirrors editor-lock.ps1.
function Test-LaneWorktree([string]$Path, [string]$Root) {
    if (-not $Path -or -not $Root) { return $false }
    $Root = Get-MainCheckout $Root
    $holder = Get-GitCheckout $Path
    if (-not $holder -or $holder -ieq (Get-GitCheckout $Root)) { return $false }
    $git = Join-Path $holder '.git'
    return ((Test-Path -LiteralPath $git -PathType Leaf) -and ((Get-Content -LiteralPath $git -Raw) -match 'gitdir:.*[\\/]worktrees[\\/]'))
}

function Block([string]$Message) {
    [Console]::Error.WriteLine($Message)
    exit 2
}

function Get-ProjectRoot($HookInput) { return [string](First $env:CLAUDE_PROJECT_DIR $HookInput.cwd (Get-Location).Path) }

# Command prefix (array) of a Python 3.10+ whose sqlite3 has FTS5, or $null.
# The Microsoft Store stub fails the probe: called with arguments it exits 9009 without opening the Store.
# Cached per checkout in .memory/.state/python.txt (one argument per line) while the executable still exists.
function Resolve-Python([string]$Root) {
    $cache = Join-Path $Root '.memory/.state/python.txt'
    if (Test-Path -LiteralPath $cache) {
        try {
            $c = @(Get-Content -LiteralPath $cache -Encoding UTF8 -ErrorAction Stop | Where-Object { $_ })
            if ($c.Count -and (Test-Path -LiteralPath $c[0])) { return $c }
        } catch {}
    }
    $probe = "import sys,sqlite3;sqlite3.connect(':memory:').execute('create virtual table t using fts5(a)');sys.exit(0 if sys.version_info>=(3,10) else 1)"
    foreach ($c in @(@('py', '-3'), @('python3'), @('python'))) {
        $cmd = Get-Command $c[0] -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $cmd) { continue }
        $rest = @($c | Select-Object -Skip 1)
        & $cmd.Source @rest -I -c $probe 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $found = @($cmd.Source) + $rest
            try {
                New-Item -ItemType Directory -Force (Split-Path $cache) | Out-Null
                Set-Content -LiteralPath $cache -Value $found -Encoding UTF8
            } catch {}
            return $found
        }
    }
    return $null
}

# Runs mem.py with the resolved Python; returns its stdout lines, or $null without Python.
function Invoke-Mem([string]$Root, [string[]]$MemArgs) {
    # @() because PowerShell unrolls a one-element array on return.
    $py = @(Resolve-Python $Root | Where-Object { $_ })
    if (-not $py.Count) { return $null }
    $rest = @($py | Select-Object -Skip 1)
    return & $py[0] @rest -I (Join-Path $Root '.claude/skills/mem/scripts/mem.py') --root $Root @MemArgs 2>$null
}

# One argument for ProcessStartInfo.Arguments (Windows PowerShell has no ArgumentList). A plain word stays bare: the py
# launcher reads its own raw command line and does not take a quoted "-3".
function ConvertTo-NativeArg([string]$Arg) {
    if ($Arg -and $Arg -notmatch '[\s"]') { return $Arg }
    return '"' + (($Arg -replace '(\\*)"', '$1$1\"') -replace '(\\+)$', '$1$1') + '"'
}

# Runs bugs.py with the resolved Python. Returns { State; Code; Out; Err }, where State tells the outcomes apart:
# 'NoPython' (nothing started), 'Failed' (non-zero exit, timeout, missing script; Err says why), 'Ok' (Out is all of stdout).
# A Process, not &: & decodes stdout with the console code page while bugs.py writes UTF-8, [Console]::OutputEncoding
# throws in a hook with no console, and Windows PowerShell wraps a native command's stderr lines as errors.
function Invoke-Bugs([string]$Root, [string[]]$BugsArgs, [int]$TimeoutMs = 10000) {
    function Result([string]$State, $Code, [string]$Out, [string]$Err) { [pscustomobject]@{ State = $State; Code = $Code; Out = $Out; Err = $Err } }
    # @() because PowerShell unrolls a one-element array on return.
    $py = @(Resolve-Python $Root | Where-Object { $_ })
    if (-not $py.Count) { return Result 'NoPython' $null '' 'no Python 3.10+ with SQLite FTS5 found' }
    $script = Join-Path $Root '.claude/skills/bugs/scripts/bugs.py'
    if (-not (Test-Path -LiteralPath $script)) { return Result 'Failed' $null '' "$script is missing" }
    $words = @($py | Select-Object -Skip 1) + @('-I', $script, '--root', $Root) + @($BugsArgs)
    $utf8 = New-Object Text.UTF8Encoding $false
    $psi = New-Object Diagnostics.ProcessStartInfo
    $psi.FileName = $py[0]
    $psi.Arguments = (@($words | ForEach-Object { ConvertTo-NativeArg $_ }) -join ' ')
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.StandardOutputEncoding = $utf8
    $psi.StandardErrorEncoding = $utf8
    try {
        $p = [Diagnostics.Process]::Start($psi)
        $p.StandardInput.Close()
        # Both pipes drain at once: a full one would stall the child.
        $outRead = $p.StandardOutput.ReadToEndAsync()
        $errRead = $p.StandardError.ReadToEndAsync()
        if (-not $p.WaitForExit($TimeoutMs)) {
            # A killed write is healed by the next command's hash check. Kill($true) does not exist on Windows PowerShell.
            try { $p.Kill($true) } catch { try { $p.Kill() } catch {} }
            return Result 'Failed' $null '' "timed out after $([int]($TimeoutMs / 1000)) s"
        }
        $out = $outRead.GetAwaiter().GetResult()
        $err = $errRead.GetAwaiter().GetResult().Trim()
        if ($p.ExitCode -ne 0) { return Result 'Failed' $p.ExitCode $out ([string](First $err "exit $($p.ExitCode)")) }
        return Result 'Ok' 0 $out $err
    } catch { return Result 'Failed' $null '' $_.Exception.Message }
}

# 'up' | 'down' | 'none' for the XERJ node at $XERJ_URL. HOOK_TEST_XERJ overrides for tests.
# Only 'down'/'none' are cached (5 min): those probes are the slow ones, and a stale 'up' would deny Grep with no node.
function Get-XerjState([string]$Root) {
    if ($env:HOOK_TEST_XERJ) { return $env:HOOK_TEST_XERJ }
    $cache = Join-Path $Root '.memory/.state/xerj.json'
    $now = [long]([DateTime]::UtcNow - [DateTime]'1970-01-01').TotalSeconds
    if (Test-Path -LiteralPath $cache) {
        try { $c = Get-Content -LiteralPath $cache -Raw | ConvertFrom-Json; if ($c.state -ne 'up' -and $now - [long]$c.at -lt 300) { return [string]$c.state } } catch {}
    }
    $state = 'none'
    # Loopback only (GD decision): a remote node would receive the agents' queries, so it counts as no XERJ.
    if (-not (Test-LoopbackUrl $env:XERJ_URL)) { return 'none' }
    if (Get-Command xerj -CommandType Application -ErrorAction SilentlyContinue) {
        $state = 'down'
        $uri = [Uri](First $env:XERJ_URL 'http://localhost:9200')
        # The node binds 127.0.0.1 by default while "localhost" may resolve to ::1 first.
        $hosts = if ($uri.Host -eq 'localhost') { @('127.0.0.1', '[::1]') } else { @($uri.Host) }
        foreach ($h in $hosts) {
            if (Test-XerjNode "$($uri.Scheme)://${h}:$($uri.Port)/") { $state = 'up'; break }
        }
    }
    try {
        New-Item -ItemType Directory -Force (Split-Path $cache) | Out-Null
        Set-Content -LiteralPath $cache -Value (@{ state = $state; at = $now } | ConvertTo-Json -Compress) -Encoding ASCII
    } catch {}
    return $state
}

# True when $Url answers like a XERJ node: 401 (auth on, the default) or a body naming xerj.
# A plain Elasticsearch/OpenSearch on the same port answers 200 without it and is not taken for XERJ.
function Test-XerjNode([string]$Url) {
    try {
        $req = [Net.HttpWebRequest]::Create($Url)
        $req.Timeout = 800
        $req.ReadWriteTimeout = 800
        $res = $req.GetResponse()
        $body = (New-Object IO.StreamReader($res.GetResponseStream())).ReadToEnd()
        $res.Close()
        return ($body -match 'xerj')
    } catch [Net.WebException] {
        $r = $_.Exception.Response
        return ($null -ne $r -and [int]$r.StatusCode -eq 401)
    } catch { return $false }
}

# Where session-start starts the autoindex: { Log; Start, the splat for Start-Process }, or $null when nothing fits.
# Start-Process has no -LiteralPath: it throws on brackets in a redirect, and on Windows PowerShell in the current folder,
# whatever the escaping. So a checkout with brackets logs under per-user app data and starts in the PowerShell home.
function Get-AutoindexPlace([string]$Root, [string]$Prefix, [string]$AppData = [Environment]::GetFolderPath('LocalApplicationData'), [string]$WorkDir = $PSHOME) {
    if (-not [WildcardPattern]::ContainsWildcardCharacters($Root)) { return @{ Log = (Join-Path $Root '.memory/.state/xerj-autoindex.log'); Start = @{} } }
    if (-not $AppData -or -not $WorkDir -or [WildcardPattern]::ContainsWildcardCharacters($AppData) -or [WildcardPattern]::ContainsWildcardCharacters($WorkDir)) { return $null }
    return @{ Log = (Join-Path $AppData "ai-for-game-framework/xerj-autoindex-$Prefix.log"); Start = @{ WorkingDirectory = $WorkDir } }
}

# Loopback only: autoindex sends file contents to the node.
# Literal hosts only, checked on the raw string that xerj will receive: [Uri].IsLoopback also accepts
# "loopback", decimal/hex IPv4 and userinfo forms that another resolver may send off the machine.
function Test-LoopbackUrl([string]$Url) {
    return ([string](First $Url 'http://localhost:9200')) -match '^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d{1,5})?/?$'
}

# XERJ index prefix: CLAUDE.md row "| Code search | xerj prefix `<p>` |", else the project folder name.
function Get-XerjPrefix([string]$Root) {
    $md = Join-Path $Root 'CLAUDE.md'
    if ((Test-Path -LiteralPath $md) -and ((Get-Content -LiteralPath $md -Raw -Encoding UTF8) -match '(?m)^\|\s*Code search\s*\|[^|\n]*?prefix\s*`?([a-z0-9][a-z0-9-]*)')) { return $Matches[1] }
    return ((Split-Path $Root -Leaf).ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
}
