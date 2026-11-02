<#
.SYNOPSIS
Checks the .claude/ layer: paths resolve, agent and skill frontmatter, skill references, workflows are JS, skill format, reference fences, checklist files, hook contract strings, no retired IDs, agents, paths or namespaces, table widths.
Warn only: size targets (skill description past 120 chars, list item past 200, body past 8,000, agent, rule and CLAUDE.md lengths), an unknown name in an agent, a unity:* plugin skill not installed. All else fails, including a description past 250 chars. Exit 0 = pass (warnings allowed), 1 = failure.
.PARAMETER File
Check only this file (used by the PostToolUse hook). Omit for the whole layer.
#>
param([string]$File)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$claude = Join-Path $root '.claude'
$fails = [System.Collections.Generic.List[string]]::new()
$warns = [System.Collections.Generic.List[string]]::new()
$soft = [ordered]@{}
function Fail($m) { $fails.Add($m) }
function Warn($m) { $warns.Add($m) }
# Size targets a skill may pass: per file from the edit hook, one count per check on a whole-layer run.
function Soft([string]$rel, [string]$check) {
    if ($File) { Warn "${rel}: $check" } else { $soft[$check] = 1 + [int]$soft[$check] }
}
# Case- and slash-insensitive: the edit hook passes the raw path Claude Code sends (c:\..., C:/...), and an unshortened
# path would skip every agent, skill and rule check.
function Rel($p) {
    $n = ([string]$p) -replace '\\', '/'; $r = ([string]$root) -replace '\\', '/'
    $(if ($n.StartsWith($r, [StringComparison]::OrdinalIgnoreCase)) { $n.Substring($r.Length).TrimStart('/') } else { $n })
}

$Budget = @{ ClaudeMd = 30; AlwaysRules = 100; PathRule = 40; Desc = 250; DescTarget = 120; AgentFile = 50; SkillChars = 8000; BulletChars = 200; RefFence = 15 }
$RetiredAgents = 'unity-engineer', 'assurance-evaluator', 'build-run-engineer', 'build-verification-tester'
$RetiredPaths = '\.claude/(standards|workflows/[a-z-]+\.md|workflows/(references|state|tools)/|rules/(orchestration|task-classification|effort-allocation|execution-loop|security|feature-context-reading|implementation-note|commit-message|language-and-comments|shell-preference|unity-tooling-preference|standards-index)\.md)'
$IdPattern = '\b(?:G[0-9]{1,2}|B[0-9]{1,2}|I[0-9]{1,2}|A[1-5]|V[1-5]|EV[0-4])\b'
# Retired namespace scheme: features use path-derived namespaces (naming-convention.md).
$RetiredNamespace = '\bGame\.(?:Core|Client|Server)\b'
# Return strings hooks/round-cap.ps1 counts on: renaming one silently stops the count.
$HookContracts = @{
    '.claude/agents/code-reviewer.md'        = @('Verdict: Approve | Request changes')
    '.claude/agents/security-reviewer.md'    = @('Verdict: Clear | Blocked')
    '.claude/agents/qa-lead.md'              = @('Verdict: Signed off | Not signed off')
    '.claude/skills/agent-protocol/SKILL.md' = @('Status: Done | Partial | Blocked | Needs-decision | Failed', 'Repro: BUG-#### reproduces | gone', '`Verify: BUG-####`')
    # Brief marker lines and state lines the hook parses.
    '.claude/skills/review/SKILL.md'                        = @('`Round: <n>`', '`Mode: audit`', '`Mode: workflow`', '`Tree: <sha>`', '`Previous tree: <sha>`', '`Target: <path or base>`', '`Bug: BUG-####`')
    '.claude/skills/qa/SKILL.md'                            = @('`Mode: test-code`', '`Verify: BUG-####`', '`Feature: .workflow/features/<slug>.md`')
    '.claude/skills/fix/SKILL.md'                           = @('`Bug: BUG-####`', '`Verify: BUG-####`', '`Feature: .workflow/features/<slug>.md`')
    '.claude/skills/feature/references/feature-template.md' = @('- Status: Open', '- Size:', '- Rounds:', '## GD decisions', '- Stop rule:')
    '.claude/skills/fix/references/bugs-template.md'        = @('- Fix rounds:', '- Review rounds:')
    '.claude/rules/routing.md'                              = @('extra round')
    # Marker literals the workflows emit and round-cap.ps1 reads.
    '.claude/workflows/review-gate.js'                      = @("lines.push('Mode: workflow')", 'lines.push(`Round: ${round}`)', 'lines.push(`Tree: ${scope.tree}`)')
    '.claude/workflows/project-audit.js'                    = @('const AUDIT = ''Mode: audit\n''', '`${AUDIT}Audit ${at(m.path)}', '`${AUDIT}Scan the repository')
}

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

# A preloaded skill is never picked from the listing, so it needs no trigger.
$preloaded = @(Get-ChildItem (Join-Path $claude 'agents') -Filter *.md | ForEach-Object {
    $fm = Get-Frontmatter (Get-Content $_.FullName -Raw -Encoding UTF8)
    if ($fm) { @($fm.skills) }
})

function Test-ChecklistLink([string]$skillDir) {
    $skillMd = Join-Path $skillDir 'SKILL.md'
    if (-not (Test-Path (Join-Path $skillDir 'checklist.md')) -or -not (Test-Path $skillMd)) { return }
    if (-not (Get-Content $skillMd -Raw -Encoding UTF8).Contains('(checklist.md)')) { Fail "$(Rel $skillMd): does not link its checklist.md" }
}

# Outside fences each line is blank, a column-0 heading, a table row or a titled list item ('- **Title:** text', '1. **Title:** text').
# Prose by that rule: wrapped or indented continuation lines, blockquotes, text right after a fence, HTML comments, rules, '*' bullets.
# Nested items are titled too. Fence content is never read. Returns the file line numbers that fail.
function Get-UntitledLines([string]$body, [int]$lineOffset) {
    $fence = ''; $no = $lineOffset
    foreach ($l in $body -split '\r?\n') {
        $no++
        if ($l -match '^\s*(`{3,}|~{3,})(.*)$') {
            $mark, $rest = $Matches[1], $Matches[2]
            if (-not $fence) { $fence = $mark }
            elseif ($mark[0] -eq $fence[0] -and $mark.Length -ge $fence.Length -and -not $rest.Trim()) { $fence = '' }
            continue
        }
        if ($fence -or $l -match '^\s*$|^#{1,6}\s|^\s*\|') { continue }
        if ($l -notmatch '^\s*(?:-|\d+\.)\s+\*\*[^*]+:\*\*') { $no }
    }
}

function Test-SkillFormat([string]$path, [string]$rel, [string]$name, [string]$text, $fm) {
    $trigger = "$($fm.description)$($fm.when_to_use)"
    if ($trigger.Length -gt $Budget.Desc) { Fail "${rel}: description + when_to_use $($trigger.Length) > $($Budget.Desc) chars" }
    elseif ($trigger.Length -gt $Budget.DescTarget) { Soft $rel "description + when_to_use > $($Budget.DescTarget) chars" }
    if ($fm.description -match 'This skill|comprehensive|Preloaded by') { Fail "${rel}: description uses a banned phrase" }
    if ($fm.description -cnotmatch '\bUse ' -and -not $fm.when_to_use -and $preloaded -notcontains $name) { Fail "${rel}: description has no Use trigger" }

    $body = $text.Substring($fm._end)
    if ($body.Length -gt $Budget.SkillChars) { Soft $rel "body > $($Budget.SkillChars) chars" }
    foreach ($m in [regex]::Matches($body, '(?m)^(?:- \*\*)?Not for:.*$')) {
        foreach ($n in [regex]::Matches($m.Value, '`([a-z0-9]+(?:-[a-z0-9]+)+)`')) {
            $v = $n.Groups[1].Value
            if ($skills -notcontains $v -and $agents -notcontains $v) { Fail "${rel}: Not for names '$v', neither a skill nor an agent" }
        }
    }
    $inFence = $false; $long = $false
    foreach ($l in $body -split '\r?\n') {
        if ($l.TrimStart().StartsWith('```')) { $inFence = -not $inFence; continue }
        if (-not $inFence -and $l -match '^\s*(?:[-*]|\d+\.)\s' -and ($l -replace '\]\([^)]*\)', ']').Length -gt $Budget.BulletChars) { $long = $true }
    }
    if ($long) { Soft $rel "list item > $($Budget.BulletChars) chars" }
    if ($body.Contains('Latent concerns')) { Fail "${rel}: Latent concerns line" }
    if ($body -match '(?m)^\s*- (?:\*\*)?(?:Verified|Known limitations):') { Fail "${rel}: Verified or Known limitations bullet (agent-protocol envelope owns them)" }
    if ($body -match '(?m)^\|\s*(?:Reference|Script)\s*\|') { Fail "${rel}: reference or script table" }
    if ($body.Contains(".claude/skills/$name/scripts/")) { Fail "${rel}: hardcoded script path" }
    $untitled = @(Get-UntitledLines $body (($text.Substring(0, $fm._end) -split '\n').Count - 1))
    if ($untitled) {
        $at = " (lines $(@($untitled | Select-Object -First 10) -join ', ')$(if ($untitled.Count -gt 10) { ", ... $($untitled.Count) in all" }))"
        Fail "${rel}: untitled list item or prose line$at"
    }

    $dir = Split-Path $path
    $scripts = Join-Path $dir 'scripts'
    if (Test-Path $scripts) {
        $named = $text
        $refs = Join-Path $dir 'references'
        if (Test-Path $refs) { Get-ChildItem $refs -Recurse -Filter *.md | ForEach-Object { $named += Get-Content $_.FullName -Raw -Encoding UTF8 } }
        foreach ($s in Get-ChildItem $scripts -Recurse -File) {
            if ($s.FullName -match '__pycache__' -or $s.Name -like 'test_*') { continue }
            if (-not $named.Contains($s.Name)) { Fail "${rel}: script '$($s.Name)' not named in SKILL.md or a reference" }
        }
    }
    Test-ChecklistLink $dir
}

function Test-Checklist([string]$path, [string]$rel, [string[]]$lines) {
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -notmatch '^(?:\s*|#{1,6} .+|- \[ \] \*\*[^*]+:\*\* \S.*)$') { Fail "${rel}:$($i + 1): not a heading or '- [ ] **<title>:** <text>' line" }
    }
    # The whole-layer run reaches this through the skill's SKILL.md.
    if ($File) { Test-ChecklistLink (Split-Path $path) }
}

function Test-RefFences([string]$rel, [string[]]$lines) {
    $start = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if (-not $lines[$i].TrimStart().StartsWith('```')) { continue }
        if ($start -lt 0) { $start = $i; continue }
        if ($i - $start - 1 -ge $Budget.RefFence) { Fail "${rel}: reference has a fenced block of $($Budget.RefFence)+ lines (move it to scripts/)"; return }
        $start = -1
    }
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
    foreach ($m in [regex]::Matches($text, '`(\.claude/[^`\s*<>{}]+)`')) {
        $p = $m.Groups[1].Value.TrimEnd('/', '.', ',')
        if ($p.Contains([string][char]0x2026)) { continue }
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
    if ([IO.File]::ReadAllText($path) -cmatch $RetiredNamespace) { Fail "${rel}: references retired namespace '$($Matches[0])'" }
    if ($rel -match '^\.claude/workflows/') {
        if ($path -notlike '*.js') { Fail "${rel}: .claude/workflows/ holds only .js workflow scripts" }
        elseif ((Get-Content $path -Raw -Encoding UTF8) -notmatch '^\s*export const meta\s*=') { Fail "${rel}: must start with 'export const meta = {...}'" }
        $js = Get-Content $path -Raw -Encoding UTF8
        foreach ($s in @($HookContracts[$rel])) {
            if ($s -and -not $js.Contains($s)) { Fail "${rel}: lost '$s', which hooks/round-cap.ps1 counts on - update both together" }
        }
        return
    }
    if ($rel -match '^\.claude/.*\.workflow') { Fail "${rel}: state belongs in <project>/.workflow/, never under .claude/" }
    if ($path -like '*.ps1') {
        # Windows PowerShell 5.1 reads a BOM-less script as ANSI; a UTF-8 dash can become a closing quote.
        foreach ($c in [IO.File]::ReadAllText($path).ToCharArray()) {
            if ([int]$c -gt 127) { Fail "${rel}: non-ASCII character in a PowerShell script"; break }
        }
        return
    }
    if ($path -like '*.sh') {
        if ([IO.File]::ReadAllText($path).Contains("`r")) { Fail "${rel}: CRLF in a shell script" }
        return
    }
    if ($path -notlike '*.md') { return }
    $text = Get-Content $path -Raw -Encoding UTF8
    $lines = $text -split '\r?\n'
    Test-Tables $path $lines
    Test-Paths $path $text
    foreach ($s in @($HookContracts[$rel])) {
        if ($s -and -not $text.Contains($s)) { Fail "${rel}: lost '$s', which hooks/round-cap.ps1 counts on - update both together" }
    }

    if ($rel -match '^\.claude/agents/([^/]+)\.md$') {
        $name = $Matches[1]
        $fm = Get-Frontmatter $text
        if (-not $fm) { Fail "${rel}: no frontmatter"; return }
        if ($fm.name -ne $name) { Fail "${rel}: name '$($fm.name)' != filename" }
        if (-not $fm.description) { Fail "${rel}: no description" }
        elseif ($fm.description.Length -gt $Budget.Desc) { Fail "${rel}: description $($fm.description.Length) > $($Budget.Desc) chars" }
        if (-not $fm.tools) { Fail "${rel}: no tools" }
        foreach ($s in @($fm.skills)) { if ($s) { Test-SkillRef $s $rel } }
        $fileLines = ($text.Trim() -split '\r?\n').Count
        if ($fileLines -gt $Budget.AgentFile) { Warn "${rel}: $fileLines lines > $($Budget.AgentFile) recommended (soft)" }
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
        else { Test-SkillFormat $path $rel $name $text $fm }
        if ($fm.'user-invocable' -ne 'false' -and $text -cmatch $IdPattern) { Fail "${rel}: retired ID '$($Matches[0])'" }
    }
    elseif ($rel -match '^\.claude/skills/[^/]+/checklist\.md$') { Test-Checklist $path $rel $lines }
    elseif ($rel -match '^\.claude/skills/[^/]+/references/') { Test-RefFences $rel $lines }
    elseif ($rel -match '^\.claude/rules/') {
        $fm = Get-Frontmatter $text
        if ($fm -and $fm.paths) {
            if ($lines.Count -gt $Budget.PathRule) { Warn "${rel}: path-scoped rule $($lines.Count) lines > $($Budget.PathRule) recommended" }
        }
        if ($text -cmatch $IdPattern) { Fail "${rel}: retired ID '$($Matches[0])'" }
    }
    elseif ($rel -eq 'CLAUDE.md' -and $lines.Count -gt $Budget.ClaudeMd) { Warn "${rel}: $($lines.Count) lines > $($Budget.ClaudeMd) recommended" }
}

if ($File) {
    $p = if ([IO.Path]::IsPathRooted($File)) { $File } else { Join-Path $root $File }
    Test-File $p
} else {
    $files = @(Get-ChildItem $claude -Recurse -File | Where-Object { $_.FullName -notmatch '[\\/](scripts|assets)[\\/]' -and $_.Extension -in '.md', '.js' -or $_.FullName -match '[\\/]workflows[\\/]' -or $_.Extension -in '.ps1', '.py', '.sh' } |
        # Agent worktrees (/feature lane A, isolation: "worktree") are checkouts of the layer, not part of it.
        # Relative to this layer's root: a layer that itself sits in a worktree is still verified.
        Where-Object { (Rel $_.FullName) -notmatch '^\.claude/worktrees/' })
    $files += Get-Item (Join-Path $root 'CLAUDE.md'), (Join-Path $root 'README.md') -ErrorAction SilentlyContinue
    foreach ($f in $files) { Test-File $f.FullName }

    $always = 0
    foreach ($r in Get-ChildItem (Join-Path $claude 'rules') -Filter *.md) {
        $fm = Get-Frontmatter (Get-Content $r.FullName -Raw -Encoding UTF8)
        if (-not ($fm -and $fm.paths)) { $always += (Get-Content $r.FullName -Encoding UTF8).Count }
    }
    if ($always -gt $Budget.AlwaysRules) { Warn ".claude/rules: always-loaded rules $always lines > $($Budget.AlwaysRules) recommended" }
    if (Test-Path (Join-Path $claude 'commands')) { Fail ".claude/commands: convert commands to skills" }
}

$soft.GetEnumerator() | ForEach-Object { Write-Output "WARN  $($_.Value) file(s): $($_.Key)" }
$warns | ForEach-Object { Write-Output "WARN  $_" }
$fails | ForEach-Object { Write-Output "FAIL  $_" }
if ($fails.Count) { Write-Output "$($fails.Count) failure(s)"; exit 1 }
Write-Output "verify-layer: OK ($($warns.Count) warning(s))"
exit 0
