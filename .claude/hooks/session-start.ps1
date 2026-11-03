# SessionStart: the framework backlog from its template when missing, in-flight features, then one status line each
# for memory, bugs and code search.
# Zero-Mem: no memory content is preloaded; the agent queries mem.py when it needs something.
$clock = [Diagnostics.Stopwatch]::StartNew()
. "$PSScriptRoot/common.ps1"
$root = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { (Get-Location).Path }

# Each repo keeps its own framework backlog outside .claude/: a fresh clone or install gets an empty one.
$backlog = Join-Path $root '.workflow/framework-backlog.md'
$template = Join-Path $root '.claude/templates/framework-backlog.md'
if (-not (Test-Path $backlog) -and (Test-Path $template)) {
    try {
        New-Item -ItemType Directory -Force (Split-Path $backlog) | Out-Null
        Copy-Item $template $backlog -ErrorAction Stop
        'Framework backlog: created .workflow/framework-backlog.md from .claude/templates/framework-backlog.md.'
    } catch { 'Framework backlog: .workflow/framework-backlog.md is missing and could not be created from the template.' }
}

$dir = Join-Path $root '.workflow/features'
if (Test-Path $dir) {
    $open = foreach ($f in Get-ChildItem $dir -Filter *.md) {
        $text = Get-Content $f.FullName -Raw -Encoding UTF8
        if ($text -match '(?m)^- Status:\s*Open\b') {
            $cp = if ($text -match '(?m)^- CP:\s*(.+)$') { $Matches[1].Trim() } else { '?' }
            "- $($f.BaseName) - CP: $cp"
        }
    }
    if ($open) {
        "In-flight features (.workflow/features/). Resume with /feature <slug>:"
        $open
    }
}

if (Test-Path (Join-Path $root '.claude/skills/mem/scripts/mem.py')) {
    # Bounded: the hook has 15 s; a large first index finishes on later queries.
    $stats = Invoke-Mem $root @('stats', '--seconds', '8')
    if ($null -eq $stats) { 'Memory: unavailable - install Python 3.10+ with SQLite FTS5 (skill mem).' }
    else {
        # The short name resolves on PATH (Resolve-Python found it that way) and matches the permission rules.
        $found = @(Resolve-Python $root)
        $py = (@([IO.Path]::GetFileNameWithoutExtension($found[0])) + @($found | Select-Object -Skip 1)) -join ' '
        "Memory: $stats. Query: $py -I .claude/skills/mem/scripts/mem.py q `"<words>`" (skill mem)."
    }
}

# Bugs: purge past the 90-day window, then one status line, or nothing with no journal. Python starts only for a journal.
function Get-BugsLine([string]$Root) {
    $workflow = Join-Path $Root '.workflow'
    if (Test-Path (Join-Path $workflow 'bugs.md')) { return 'Bugs: .workflow/bugs.md is still present - run bugs.py import-md, then delete the file (skill bugs).' }
    if (-not (Test-Path (Join-Path $workflow 'bugs.jsonl'))) { return $null }
    # The hook has 15 s: the mem call above takes up to 8, the XERJ probe below up to 2. A purge cut short resumes next session.
    $budget = [Math]::Min(3000, 12000 - $clock.ElapsedMilliseconds)
    if ($budget -lt 1000) { return 'Bugs: not checked - the session-start time budget is used up.' }
    $started = $clock.ElapsedMilliseconds
    $purge = Invoke-Bugs $Root @('purge', '--auto') ([int]$budget)
    if ($purge.State -eq 'NoPython') { return 'Bugs: unavailable - install Python 3.10+ with SQLite FTS5 (skill bugs).' }
    $suffix = ''
    if ($purge.State -ne 'Ok') { $suffix = "; purge failed: $(Get-FirstLine $purge.Err)" }
    elseif ($purge.Out -match '(?m)^(purged [1-9]\d*, journal uncommitted)\s*$') { $suffix = "; $($Matches[1])" }
    $stats = Invoke-Bugs $Root @('stats') ([int][Math]::Max(1000, $budget - ($clock.ElapsedMilliseconds - $started)))
    if ($stats.State -ne 'Ok') { return "Bugs: unavailable - $(Get-FirstLine $stats.Err)" }
    return "$($stats.Out.Trim())$suffix"
}
function Get-FirstLine([string]$Text) { $line = ($Text -split '\r?\n')[0]; if ($line.Length -gt 160) { $line.Substring(0, 160) } else { $line } }
try { Get-BugsLine (Get-MainCheckout $root) } catch { "Bugs: unavailable - $(Get-FirstLine $_.Exception.Message)" }

$prefix = Get-XerjPrefix $root
switch (Get-XerjState $root) {
    'up' {
        "Search: XERJ up, prefix $prefix - xerj search/def before Grep (skill code-search)."
        if (-not (Test-LoopbackUrl $env:XERJ_URL)) { "XERJ_URL is not loopback: index not refreshed (it would send file contents off this machine)." }
        elseif (-not $env:HOOK_TEST_XERJ) {
            # Incremental and BM25-only; the node skips unchanged files.
            $log = Join-Path $root '.memory/.state/xerj-autoindex.log'
            # --url pins the destination to the URL the loopback check just passed.
            $url = First $env:XERJ_URL 'http://localhost:9200'
            $xargs = @('autoindex', "`"$root`"", '--url', $url, '--prefix', $prefix, '--plan', 'code-and-docs-no-vectors', '--no-graph')
            try { Start-Process xerj -ArgumentList $xargs -RedirectStandardOutput $log -RedirectStandardError "$log.err" -WindowStyle Hidden | Out-Null }
            catch { try { Start-Process xerj -ArgumentList $xargs -RedirectStandardOutput $log -RedirectStandardError "$log.err" | Out-Null } catch {} }
        }
    }
    'down' { 'Search: XERJ installed, node down - Grep. Start: xerj --data-dir ~/xerj-data (skill code-search).' }
    default {
        if (Test-LoopbackUrl $env:XERJ_URL) { 'Search: Grep.' }
        else { 'Search: Grep. XERJ_URL is not loopback - XERJ is used only on this machine (queries would leave it).' }
    }
}
exit 0
