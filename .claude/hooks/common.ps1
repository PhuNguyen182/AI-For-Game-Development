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
function Remove-QuotedText([string]$Command) {
    $c = [regex]::Replace($Command, '<<-?\s*([''"]?)(\w+)\1[^\n]*\n[\s\S]*?\n\s*\2[ \t]*(?=\r?\n|$)', ' ')
    $c = [regex]::Replace($c, '@([''"])\r?\n[\s\S]*?\r?\n\1@', ' ')
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

# Every `git <verb> <args>` a shell command runs, as { Globals, Verb, Rest, Alias, Why }. Reads through commit-message
# text (blanked), the quoted script of an sh/bash/pwsh/cmd -c wrapper, and an alias configured in $Cwd's repo or
# the user's config. Why is set, and the call refused, for config nothing on disk shows: `-c alias.*`, GIT_CONFIG_*.
function Get-GitCalls([string]$Command, [string]$Cwd, [int]$Depth = 0) {
    $texts = @(Remove-QuotedText $Command)
    if ($Command -match '(?i)\b(?:sh|bash|zsh|dash|pwsh|powershell|cmd)(?:\.exe)?\s+(?:-[A-Za-z]*c\b|-Command\b|/c\b)') {
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
            if ($Depth -lt 3 -and $Cwd -and (Test-Path -LiteralPath $Cwd)) { $alias = [string](git -C $Cwd config --get "alias.$verb" 2>$null) }
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

# The working tree git reports for $Dir, or $null. A Process, not &: & decodes git's UTF-8 stdout with the console code page.
function Get-GitTopLevel([string]$Dir) {
    $utf8 = New-Object Text.UTF8Encoding $false
    $psi = New-Object Diagnostics.ProcessStartInfo
    $psi.FileName = 'git'
    $psi.Arguments = (@(@('-C', $Dir, 'rev-parse', '--show-toplevel') | ForEach-Object { ConvertTo-NativeArg $_ }) -join ' ')
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
        $top = $outRead.GetAwaiter().GetResult().Trim()
        if ($p.ExitCode -eq 0 -and $top -and [IO.Directory]::Exists($top)) { return $top }
    } catch {}
    return $null
}

# True when $Dir or a folder above it is a repository as git reads one: a .git file, or a .git folder holding HEAD.
function Test-InsideGitRepo([string]$Dir) {
    $d = $Dir
    while ($d) {
        $git = [IO.Path]::Combine($d, '.git')
        if ([IO.File]::Exists($git) -or [IO.File]::Exists([IO.Path]::Combine($git, 'HEAD'))) { return $true }
        $d = [IO.Path]::GetDirectoryName($d)
    }
    return $false
}

# The repository a secret gate must scan: the first of $Dirs git names a root for. $null only when no repository is there,
# so the command itself cannot run. A real repository git cannot name blocks: a gate must never pass on what it cannot read.
function Resolve-GitRoot([string[]]$Dirs, [string]$What) {
    $unnamed = $null
    foreach ($d in $Dirs) {
        if (-not $d -or -not [IO.Directory]::Exists($d)) { continue }
        $top = Get-GitTopLevel $d
        if ($top) { return $top }
        if (-not $unnamed -and (Test-InsideGitRepo ([IO.Path]::GetFullPath($d)))) { $unnamed = $d }
    }
    if ($unnamed) { Block "Blocked: $unnamed is inside a git repository, but git cannot name its root, so the $What cannot be scanned for secrets. Run git rev-parse --show-toplevel there to see why." }
    return $null
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
