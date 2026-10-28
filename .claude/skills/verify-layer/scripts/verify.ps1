<#
.SYNOPSIS
Checks the .claude/ layer: paths resolve, agent and skill frontmatter, skill references, workflows are JS,
size budgets, no retired IDs or agents, table widths. Exit 0 = pass (warnings allowed), 1 = failure.
.PARAMETER File
Check only this file (used by the PostToolUse hook). Omit for the whole layer.
#>
param([string]$File)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$claude = Join-Path $root '.claude'
$fails = [System.Collections.Generic.List[string]]::new()
$warns = [System.Collections.Generic.List[string]]::new()
function Fail($m) { $fails.Add($m) }
function Warn($m) { $warns.Add($m) }
function Rel($p) { [IO.Path]::GetRelativePath($root, $p) -replace '\\', '/' }

$Budget = @{ ClaudeMd = 30; AlwaysRules = 100; PathRule = 40; Desc = 250; AgentBody = 25; Pipeline = 120; Skill = 500 }
$RetiredAgents = 'unity-engineer', 'assurance-evaluator', 'build-run-engineer', 'build-verification-tester'
$RetiredPaths = '\.claude/(standards|workflows/[a-z-]+\.md|workflows/(references|state|tools)/|rules/(orchestration|task-classification|effort-allocation|execution-loop|security|feature-context-reading|implementation-note|commit-message|language-and-comments|shell-preference|unity-tooling-preference|standards-index)\.md)'
$IdPattern = '\b(?:G[0-9]{1,2}|B[0-9]{1,2}|I[0-9]{1,2}|A[1-5]|V[1-5]|EV[0-4])\b'

$agents = @(Get-ChildItem (Join-Path $claude 'agents') -Filter *.md | ForEach-Object BaseName)
$skills = @(Get-ChildItem (Join-Path $claude 'skills') -Directory | ForEach-Object Name)
$pluginSkills = @(Get-ChildItem (Join-Path $HOME '.claude/plugins/cache') -Recurse -Filter SKILL.md -ErrorAction SilentlyContinue |
    ForEach-Object { $_.Directory.Name })

function Get-Frontmatter([string]$text) {
    $m = [regex]::Match($text, '^---\r?\n(.*?)\r?\n---\r?\n', 'Singleline')
    if (-not $m.Success) { return $null }
    $fm = @{ _end = $m.Length; _raw = $m.Groups[1].Value }
    $lines = $m.Groups[1].Value -split '\r?\n'
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^([a-z_-]+):\s*(.*)$') {
            $k, $v = $Matches[1], $Matches[2].Trim()
            if ($v -eq '' -or $v -in '>', '>-', '|', '|-') {
                $items = @()
                while ($i + 1 -lt $lines.Count -and $lines[$i + 1] -match '^\s+(.*)$') { $items += $Matches[1].Trim(); $i++ }
                $fm[$k] = if ($v -eq '') { @($items | ForEach-Object { $_ -replace '^-\s*', '' }) } else { $items -join ' ' }
            } else { $fm[$k] = $v.Trim('"') }
        }
    }
    return $fm
}

function Test-SkillRef([string]$name, [string]$where) {
    if ($name -like 'unity:*') {
        if ($pluginSkills -notcontains $name.Substring(6)) { Warn "${where}: plugin skill '$name' not found locally" }
    } elseif ($name -match ':') {
        # Other plugins (superpowers:..., anthropic-skills:...) are optional.
    } elseif ($skills -notcontains $name) { Fail "${where}: skill '$name' does not exist" }
}

function Test-Tables([string]$path, [string[]]$lines) {
    $width = 0
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $l = $lines[$i]
        if ($l -notmatch '^\s*\|') { $width = 0; continue }
        $cells = (($l -replace '`[^`]*`', 'x') -replace '\\\|', 'x').Trim().Trim('|') -split '\|'
        if ($width -eq 0) { $width = $cells.Count; continue }
        if ($cells.Count -ne $width) { Fail "$(Rel $path):$($i + 1): table row has $($cells.Count) cells, header has $width" }
    }
}

function Test-Paths([string]$path, [string]$text) {
    $dir = Split-Path $path
    foreach ($m in [regex]::Matches($text, '`(\.claude/[^`\s*<>{}…]+)`')) {
        $p = $m.Groups[1].Value.TrimEnd('/', '.', ',')
        if (-not (Test-Path (Join-Path $root $p))) { Fail "$(Rel $path): path '$p' does not exist" }
    }
    foreach ($m in [regex]::Matches($text, '\]\(([^)\s#]+)(?:#[^)]*)?\)')) {
        $p = $m.Groups[1].Value
        if ($p -match '^(https?|mailto):' -or $p -match '[<>*]') { continue }
        if (-not (Test-Path (Join-Path $dir $p))) { Fail "$(Rel $path): link '$p' does not exist" }
    }
    if ($text -match $RetiredPaths) { Fail "$(Rel $path): references retired path '$($Matches[0])'" }
    foreach ($a in $RetiredAgents) { if ($text -match "\b$a\b") { Fail "$(Rel $path): references retired agent '$a'" } }
    foreach ($m in [regex]::Matches($text, '`([a-z]+(?:-[a-z]+)*-(?:engineer|tester|reviewer|lead|investigator|architect|artist|expert))`')) {
        if ($agents -notcontains $m.Groups[1].Value) { Fail "$(Rel $path): agent '$($m.Groups[1].Value)' does not exist" }
    }
}

function Test-File([string]$path) {
    if (-not (Test-Path $path -PathType Leaf)) { return }
    $rel = Rel $path
    if ($rel -match '^\.claude/workflows/') {
        if ($path -notlike '*.js') { Fail "${rel}: .claude/workflows/ holds only .js workflow scripts" }
        elseif ((Get-Content $path -Raw) -notmatch '^\s*export const meta\s*=') { Fail "${rel}: must start with 'export const meta = {...}'" }
        return
    }
    if ($rel -match '^\.claude/.*\.workflow') { Fail "${rel}: state belongs in <project>/.workflow/, never under .claude/" }
    if ($path -notlike '*.md') { return }
    $text = Get-Content $path -Raw
    $lines = $text -split '\r?\n'
    Test-Tables $path $lines
    Test-Paths $path $text

    if ($rel -match '^\.claude/agents/([^/]+)\.md$') {
        $name = $Matches[1]
        $fm = Get-Frontmatter $text
        if (-not $fm) { Fail "${rel}: no frontmatter"; return }
        if ($fm.name -ne $name) { Fail "${rel}: name '$($fm.name)' != filename" }
        if (-not $fm.description) { Fail "${rel}: no description" }
        elseif ($fm.description.Length -gt $Budget.Desc) { Fail "${rel}: description $($fm.description.Length) > $($Budget.Desc) chars" }
        if (-not $fm.tools) { Fail "${rel}: no tools" }
        foreach ($s in @($fm.skills)) { if ($s) { Test-SkillRef $s $rel } }
        $body = ($text.Substring($fm._end).Trim() -split '\r?\n').Count
        if ($body -gt $Budget.AgentBody) { Fail "${rel}: body $body lines > $($Budget.AgentBody)" }
        foreach ($m in [regex]::Matches($text.Substring($fm._end), '`((?:unity:)?[a-z0-9]+(?:-[a-z0-9]+)+)`')) {
            $n = $m.Groups[1].Value
            if ($n -match ':' -or $skills -contains $n -or $agents -contains $n) { if ($n -match ':') { Test-SkillRef $n $rel }; continue }
            if ($n -match '-(engineer|tester|reviewer|lead|investigator|architect|artist|expert)$' -or $n -in 'csharp-standards', 'agent-protocol') { continue }
            Warn "${rel}: '$n' is neither a skill nor an agent"
        }
        if ($text -cmatch $IdPattern) { Fail "${rel}: retired ID '$($Matches[0])'" }
    }
    elseif ($rel -match '^\.claude/skills/([^/]+)/SKILL\.md$') {
        $name = $Matches[1]
        $fm = Get-Frontmatter $text
        if (-not $fm) { Fail "${rel}: no frontmatter"; return }
        if ($fm.name -and $fm.name -ne $name) { Fail "${rel}: name '$($fm.name)' != folder" }
        if (-not $fm.description) { Fail "${rel}: no description" }
        elseif ($fm.description.Length -gt $Budget.Desc) { Fail "${rel}: description $($fm.description.Length) > $($Budget.Desc) chars" }
        $limit = if ($fm.'user-invocable' -eq 'false') { $Budget.Skill } else { $Budget.Pipeline }
        if ($lines.Count -gt $limit) { Fail "${rel}: $($lines.Count) lines > $limit" }
        if ($fm.'user-invocable' -ne 'false' -and $text -cmatch $IdPattern) { Fail "${rel}: retired ID '$($Matches[0])'" }
    }
    elseif ($rel -match '^\.claude/rules/') {
        $fm = Get-Frontmatter $text
        if ($fm -and $fm.paths) {
            if ($lines.Count -gt $Budget.PathRule) { Fail "${rel}: path-scoped rule $($lines.Count) lines > $($Budget.PathRule)" }
        }
        if ($text -cmatch $IdPattern) { Fail "${rel}: retired ID '$($Matches[0])'" }
    }
    elseif ($rel -eq 'CLAUDE.md' -and $lines.Count -gt $Budget.ClaudeMd) { Fail "${rel}: $($lines.Count) lines > $($Budget.ClaudeMd)" }
}

if ($File) {
    $p = if ([IO.Path]::IsPathRooted($File)) { $File } else { Join-Path $root $File }
    Test-File $p
} else {
    $files = @(Get-ChildItem $claude -Recurse -File | Where-Object { $_.FullName -notmatch '[\\/](scripts|assets)[\\/]' -and $_.Extension -in '.md', '.js' -or $_.FullName -match '[\\/]workflows[\\/]' })
    $files += Get-Item (Join-Path $root 'CLAUDE.md'), (Join-Path $root 'README.md') -ErrorAction SilentlyContinue
    foreach ($f in $files) { Test-File $f.FullName }

    $always = 0
    foreach ($r in Get-ChildItem (Join-Path $claude 'rules') -Filter *.md) {
        $fm = Get-Frontmatter (Get-Content $r.FullName -Raw)
        if (-not ($fm -and $fm.paths)) { $always += (Get-Content $r.FullName).Count }
    }
    if ($always -gt $Budget.AlwaysRules) { Fail ".claude/rules: always-loaded rules $always lines > $($Budget.AlwaysRules)" }
    if (Test-Path (Join-Path $claude 'commands')) { Fail ".claude/commands: convert commands to skills" }
}

$warns | ForEach-Object { Write-Output "WARN  $_" }
$fails | ForEach-Object { Write-Output "FAIL  $_" }
if ($fails.Count) { Write-Output "$($fails.Count) failure(s)"; exit 1 }
Write-Output "verify-layer: OK ($($warns.Count) warning(s))"
exit 0
