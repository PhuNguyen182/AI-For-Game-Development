# SessionStart: empty records journals when missing, in-flight features, then one status line each for memory, bugs,
# records and code search, and one line naming the migrate command while a markdown store is left.
# Zero-Mem: no memory content is preloaded; the agent queries mem.py when it needs something.
$clock = [Diagnostics.Stopwatch]::StartNew()
. "$PSScriptRoot/common.ps1"
$root = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { (Get-Location).Path }

function Get-FirstLine([string]$Text) { $line = ($Text -split '\r?\n')[0]; if ($line.Length -gt 160) { $line.Substring(0, 160) } else { $line } }
# The checkout whose .workflow holds the journals: a session in a linked worktree reads its main checkout's (bugs root rule).
$main = $null; $mainError = $null
try { $main = Get-BugsRoot $root } catch { $mainError = Get-FirstLine $_.Exception.Message }

# Each store's journal is the truth (skill records): a fresh clone or install gets empty ones. Never from a linked
# worktree: it reads the main checkout's, and its own tracked copies come from git.
$recordsCli = '.claude/skills/records/scripts/records.py'
if ($main -and $main -eq $root -and (Test-Path -LiteralPath (Join-Path $root $recordsCli))) {
    $failed = @()
    foreach ($name in 'backlog.jsonl', 'debt.jsonl', 'features.jsonl', 'framework-backlog.jsonl') {
        $path = Join-Path $root ".workflow/$name"
        if (Test-Path -LiteralPath $path) { continue }
        try {
            New-Item -ItemType Directory -Force (Split-Path $path) | Out-Null
            [IO.File]::WriteAllBytes($path, [byte[]]@())
        } catch { $failed += $name }
    }
    if ($failed.Count) { "Records: .workflow/$($failed -join ', .workflow/') could not be created." }
}

# One Python start for the Records line and the registry's in-flight features. Bounded: the hook has 15 s.
$recordsLine = $null
$registryOpen = @()
if ($mainError) { $recordsLine = "Records: unavailable - $mainError" }
elseif (Test-Path -LiteralPath (Join-Path $main $recordsCli)) {
    $r = Invoke-Records $main @('stats', '--json') 3000
    if ($r.State -eq 'NoPython') { $recordsLine = 'Records: unavailable - install Python 3.10+ with SQLite FTS5 (skill records).' }
    elseif ($r.State -ne 'Ok') { $recordsLine = "Records: unavailable - $(Get-FirstLine $r.Err)" }
    else {
        $j = $null
        try { $j = $r.Out | ConvertFrom-Json -ErrorAction Stop } catch {}
        if ($null -eq $j -or $j.line -isnot [string]) { $recordsLine = 'Records: unavailable - records.py stats returned unreadable output.' }
        else {
            # ASCII on every console code page: the CLI's middle-dot separators become commas.
            $recordsLine = $j.line -replace ('\s*' + [char]0x00B7 + '\s*'), ', '
            $registryOpen = @($j.open_features | Where-Object { $_ -and $_.slug })
        }
    }
}

# In-flight features: the registry, and un-migrated feature files with an Open status line. The registry wins a slug both hold.
$inFlight = [ordered]@{}
$dir = Join-Path $root '.workflow/features'
$unmigratedFeatures = 0
if (Test-Path -LiteralPath $dir) {
    foreach ($f in Get-ChildItem -LiteralPath $dir -Filter *.md -File) {
        if ($f.Name -like '*.spec.md' -or $f.Name -like '*.migrated-*') { continue }
        $text = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8
        if ($text -match '(?m)^- Status:') { $unmigratedFeatures++ }
        if ($text -match '(?m)^- Status:\s*Open\b') {
            $cp = if ($text -match '(?m)^- CP:\s*(.+)$') { $Matches[1].Trim() } else { '?' }
            $inFlight[$f.BaseName] = "- $($f.BaseName) - CP: $cp"
        }
    }
}
foreach ($f in $registryOpen) {
    $cp = First $f.cp '?'
    $next = if ($f.next_step) { " - next step: $($f.next_step)" } else { '' }
    $inFlight[[string]$f.slug] = "- $($f.slug) - CP: $cp$next"
}
if ($inFlight.Count) {
    "In-flight features (.workflow/features/). Resume with /feature <slug>:"
    $inFlight.Values
}

# The interpreter's short name resolves on PATH (Resolve-Python found it that way) and matches the permission rules.
function Get-PythonWords([string]$Root) {
    $found = @(Resolve-Python $Root | Where-Object { $_ })
    if (-not $found.Count) { return 'python' }
    return (@([IO.Path]::GetFileNameWithoutExtension($found[0])) + @($found | Select-Object -Skip 1)) -join ' '
}

if (Test-Path -LiteralPath (Join-Path $root '.claude/skills/mem/scripts/mem.py')) {
    # Bounded: the hook has 15 s; a large first index finishes on later queries.
    $stats = Invoke-Mem $root @('stats', '--seconds', '8')
    if ($null -eq $stats) { 'Memory: unavailable - install Python 3.10+ with SQLite FTS5 (skill mem).' }
    else { "Memory: $stats. Query: $(Get-PythonWords $root) -I .claude/skills/mem/scripts/mem.py q `"<words>`" (skill mem)." }
}

# Bugs: purge past the 90-day window, then one status line, or nothing with no journal. Python starts only for a journal.
function Get-BugsLine([string]$Root, [bool]$SkipPurge) {
    $workflow = Join-Path $Root '.workflow'
    if (-not (Test-Path -LiteralPath (Join-Path $workflow 'bugs.jsonl'))) { return $null }
    # The hook has 15 s: the records call above takes up to 3, mem up to 8, the XERJ probe below up to 2. A purge cut short resumes next session.
    $budget = [Math]::Min(3000, 12000 - $clock.ElapsedMilliseconds)
    if ($budget -lt 1000) { return 'Bugs: not checked - the session-start time budget is used up.' }
    $started = $clock.ElapsedMilliseconds
    $noPython = 'Bugs: unavailable - install Python 3.10+ with SQLite FTS5 (skill bugs).'
    $suffix = ''
    if (-not $SkipPurge) {
        $purge = Invoke-Bugs $Root @('purge', '--auto') ([int]$budget)
        if ($purge.State -eq 'NoPython') { return $noPython }
        if ($purge.State -ne 'Ok') { $suffix = "; purge failed: $(Get-FirstLine $purge.Err)" }
        else {
            if ($purge.Out -match '(?m)^(purged [1-9]\d*, journal uncommitted)\s*$') { $suffix = "; $($Matches[1])" }
            elseif ($purge.Out -match '(?m)^purge skipped: journal not clean') { $suffix = '; purge skipped, journal uncommitted' }
            elseif ($purge.Out -match '(?m)^purge skipped: git failed') { $suffix = '; purge skipped, git failed' }
            # Exit 0 with stderr is a warning, such as a leftover BUGS_NOW: this is the one unattended purge, so show it.
            if ($purge.Err) { $suffix += "; $(Get-FirstLine $purge.Err)" }
        }
    }
    $stats = Invoke-Bugs $Root @('stats') ([int][Math]::Max(1000, $budget - ($clock.ElapsedMilliseconds - $started)))
    if ($stats.State -eq 'NoPython') { return $noPython }
    if ($stats.State -ne 'Ok') { return "Bugs: unavailable - $(Get-FirstLine $stats.Err)" }
    return "$($stats.Out.Trim())$suffix"
}
# The journal checks and stats use the main checkout, but the CLI then sees --root as a main checkout, so its own worktree
# guard cannot fire: a session in a linked worktree must not purge. Get-BugsRoot changes $root only for such a worktree.
if ($mainError) { "Bugs: unavailable - $mainError" }
else { try { Get-BugsLine $main ($main -ne $root) } catch { "Bugs: unavailable - $(Get-FirstLine $_.Exception.Message)" } }

if ($recordsLine) { $recordsLine }
# Markdown stores records.py has not converted yet. migrate runs on the main checkout only, so the line names its root.
$migrateRoot = if ($main) { $main } else { $root }
$left = @(foreach ($name in 'framework-backlog.md', 'backlog.md', 'DEBT.md', 'rounds.json') {
        if (Test-Path -LiteralPath (Join-Path $migrateRoot ".workflow/$name") -PathType Leaf) { ".workflow/$name" }
    })
if ($migrateRoot -ne $root) {
    # The feature files counted above are this worktree's: count the main checkout's.
    $unmigratedFeatures = 0
    $mainFeatures = Join-Path $migrateRoot '.workflow/features'
    if (Test-Path -LiteralPath $mainFeatures) {
        foreach ($f in Get-ChildItem -LiteralPath $mainFeatures -Filter *.md -File) {
            if ($f.Name -like '*.spec.md' -or $f.Name -like '*.migrated-*') { continue }
            if ((Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8) -match '(?m)^- Status:') { $unmigratedFeatures++ }
        }
    }
}
if ($unmigratedFeatures) { $left += "$unmigratedFeatures feature file(s) with a '- Status:' line" }
if ($left.Count -and (Test-Path -LiteralPath (Join-Path $migrateRoot $recordsCli))) {
    "Records: not migrated - $($left -join ', '). Preview: $(Get-PythonWords $migrateRoot) -I $recordsCli --root `"$migrateRoot`" migrate --from-md --dry-run, then the same without --dry-run (skill records)."
}

$prefix = Get-XerjPrefix $root
switch (Get-XerjState $root) {
    'up' {
        "Search: XERJ up, prefix $prefix - xerj search/def before Grep (skill code-search)."
        if (-not (Test-LoopbackUrl $env:XERJ_URL)) { "XERJ_URL is not loopback: index not refreshed (it would send file contents off this machine)." }
        elseif (-not $env:HOOK_TEST_XERJ) {
            # Incremental and BM25-only; the node skips unchanged files.
            $autoindex = Get-AutoindexPlace $root $prefix
            if (-not $autoindex) { 'XERJ index not refreshed: no folder without brackets for its log.' }
            else {
                $log = $autoindex.Log
                $place = $autoindex.Start
                # --url pins the destination to the URL the loopback check just passed.
                $url = First $env:XERJ_URL 'http://localhost:9200'
                $xargs = @('autoindex', "`"$root`"", '--url', $url, '--prefix', $prefix, '--plan', 'code-and-docs-no-vectors', '--no-graph')
                try { New-Item -ItemType Directory -Force (Split-Path $log) | Out-Null } catch {}
                try { Start-Process xerj -ArgumentList $xargs -RedirectStandardOutput $log -RedirectStandardError "$log.err" -WindowStyle Hidden @place | Out-Null }
                catch { try { Start-Process xerj -ArgumentList $xargs -RedirectStandardOutput $log -RedirectStandardError "$log.err" @place | Out-Null } catch {} }
            }
        }
    }
    'down' { 'Search: XERJ installed, node down - Grep. Start: xerj --data-dir ~/xerj-data (skill code-search).' }
    default {
        if (Test-LoopbackUrl $env:XERJ_URL) { 'Search: Grep.' }
        else { 'Search: Grep. XERJ_URL is not loopback - XERJ is used only on this machine (queries would leave it).' }
    }
}
exit 0
