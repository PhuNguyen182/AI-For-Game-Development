# PreToolUse Grep, and grep/rg/git grep/Select-String through a shell: while a XERJ node is up, deny a repo-wide
# content search and name the xerj command instead. A nudge, not security: anything unclear is allowed.
. "$PSScriptRoot/common.ps1"

$in = Read-HookInput
if (-not $in) { exit 0 }
$root = Get-ProjectRoot $in

# A subagent without a shell cannot run xerj: leave its Grep alone. No tools: line means every tool, shell included.
if ($in.agent_type) {
    $def = Join-Path $root ".claude/agents/$($in.agent_type).md"
    if ((Test-Path $def) -and ((Get-Content $def -Raw -Encoding UTF8) -match '(?ms)^tools:(.*?)(?=^[\w-]+:|^---)')) {
        if ($Matches[1] -notmatch '\b(Bash|PowerShell)\b') { exit 0 }
    }
}

# True when $Path is empty, the root, or a folder directly under it.
function Test-Broad([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path) -or $Path -in @('.', './', '*')) { return $true }
    $p = $Path.Trim('"', "'").Replace('\', '/')
    $r = $root.Replace('\', '/').TrimEnd('/')
    if ($p.StartsWith($r, [StringComparison]::OrdinalIgnoreCase)) { $p = $p.Substring($r.Length) }
    $p = ($p -replace '^(\./)+', '').Trim('/')
    if ($p -in @('', '.')) { return $true }
    # XERJ never indexes hidden folders (.claude, .workflow, .memory), so Grep is the only way in.
    if ($p.StartsWith('.') -or $p -match '\.\w{1,8}$' -or $p -match '[*?]') { return $false }
    return ($p.Split('/', [StringSplitOptions]::RemoveEmptyEntries).Count -le 1)
}

$t = $in.tool_input
$pattern = ''
$broad = $false
if ($in.tool_name -eq 'Grep') {
    $pattern = [string]$t.pattern
    $broad = ([string]$t.output_mode -eq 'content') -and (Test-Broad ([string]$t.path))
}
else {
    $cmd = [string]$t.command
    $m = [regex]::Match($cmd, '(?:^|[;&|]\s*)(rg|grep|git\s+grep|Select-String)\b(.*)$')
    if (-not $m.Success) { exit 0 }
    $tool = $m.Groups[1].Value
    $rest = $m.Groups[2].Value -replace '\|.*$', ''
    $tokens = @([regex]::Matches($rest, '"[^"]*"|''[^'']*''|\S+') | ForEach-Object { $_.Value })
    $plain = @($tokens | Where-Object { $_ -notmatch '^-' })
    if ($plain.Count) { $pattern = $plain[0].Trim('"', "'") }
    $paths = @($plain | Select-Object -Skip 1)
    $listOnly = if ($tool -eq 'Select-String') { $rest -match '(^|\s)-(List|Quiet)\b' }
                else { ($rest -match '(^|\s)(--files|--files-with-matches|--count)\b') -or ($rest -cmatch '(^|\s)-[a-zA-Z]*[lc][a-zA-Z]*(\s|$)') }
    $recursive = switch -Regex ($tool) {
        '^grep$' { $rest -match '(^|\s)(-[a-zA-Z]*[rR]|--recursive\b|--dereference-recursive\b)' }
        '^Select-String$' { $cmd -match '-Recurse' }
        default { $true }
    }
    $broad = $recursive -and -not $listOnly -and ($paths.Count -eq 0 -or @($paths | Where-Object { -not (Test-Broad $_) }).Count -eq 0)
}
if (-not $broad -or (Get-XerjState $root) -ne 'up') { exit 0 }

$prefix = Get-XerjPrefix $root
$q = ($pattern -replace '[\\^$.*+?()\[\]{}|]', ' ' -replace '\s+', ' ').Trim()
$reason = "XERJ is up: search with  xerj search `"$q`" --prefix $prefix -k 5  or  xerj def <Symbol> --prefix $prefix  (skill code-search). " +
    "Grep stays allowed on a file, a folder two levels deep, or for file lists/counts."
@{ hookSpecificOutput = @{ hookEventName = 'PreToolUse'; permissionDecision = 'deny'; permissionDecisionReason = $reason } } |
    ConvertTo-Json -Compress -Depth 3
exit 0
