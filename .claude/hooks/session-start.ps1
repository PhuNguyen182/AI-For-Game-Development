# SessionStart: in-flight features, then one status line each for memory and code search.
# Zero-Mem: no memory content is preloaded; the agent queries mem.py when it needs something.
. "$PSScriptRoot/common.ps1"
$root = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { (Get-Location).Path }

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
