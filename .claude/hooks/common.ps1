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

# Files that legitimately contain the patterns above: the hooks themselves and the scan skill's docs.
$script:SecretScanExempt = '[\\/]\.claude[\\/](?:hooks[\\/]|skills[\\/]secret-and-supply-chain-scan[\\/])'

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
            if ($Depth -lt 3 -and $Cwd -and (Test-Path $Cwd)) { $alias = [string](git -C $Cwd config --get "alias.$verb" 2>$null) }
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

function Read-HookInput {
    $raw = [Console]::In.ReadToEnd()
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
        if ("/$file" -match $script:SecretScanExempt) { continue }
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
function Get-GitDiffText([string]$Root, [string[]]$GitArgs) {
    $tmp = [IO.Path]::GetTempFileName()
    try {
        git -C $Root @GitArgs "--output=$tmp" 2>$null | Out-Null
        return [IO.File]::ReadAllText($tmp)
    } finally { Remove-Item $tmp -ErrorAction SilentlyContinue }
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
    if (Test-Path $cache) {
        try {
            $c = @(Get-Content $cache -Encoding UTF8 -ErrorAction Stop | Where-Object { $_ })
            if ($c.Count -and (Test-Path $c[0])) { return $c }
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
                Set-Content $cache $found -Encoding UTF8
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

# 'up' | 'down' | 'none' for the XERJ node at $XERJ_URL. HOOK_TEST_XERJ overrides for tests.
# Only 'down'/'none' are cached (5 min): those probes are the slow ones, and a stale 'up' would deny Grep with no node.
function Get-XerjState([string]$Root) {
    if ($env:HOOK_TEST_XERJ) { return $env:HOOK_TEST_XERJ }
    $cache = Join-Path $Root '.memory/.state/xerj.json'
    $now = [long]([DateTime]::UtcNow - [DateTime]'1970-01-01').TotalSeconds
    if (Test-Path $cache) {
        try { $c = Get-Content $cache -Raw | ConvertFrom-Json; if ($c.state -ne 'up' -and $now - [long]$c.at -lt 300) { return [string]$c.state } } catch {}
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
        Set-Content $cache (@{ state = $state; at = $now } | ConvertTo-Json -Compress) -Encoding ASCII
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

# Loopback only: autoindex sends file contents to the node.
# Literal hosts only, checked on the raw string that xerj will receive: [Uri].IsLoopback also accepts
# "loopback", decimal/hex IPv4 and userinfo forms that another resolver may send off the machine.
function Test-LoopbackUrl([string]$Url) {
    return ([string](First $Url 'http://localhost:9200')) -match '^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d{1,5})?/?$'
}

# XERJ index prefix: CLAUDE.md row "| Code search | xerj prefix `<p>` |", else the project folder name.
function Get-XerjPrefix([string]$Root) {
    $md = Join-Path $Root 'CLAUDE.md'
    if ((Test-Path $md) -and ((Get-Content $md -Raw -Encoding UTF8) -match '(?m)^\|\s*Code search\s*\|[^|\n]*?prefix\s*`?([a-z0-9][a-z0-9-]*)')) { return $Matches[1] }
    return ((Split-Path $Root -Leaf).ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
}
