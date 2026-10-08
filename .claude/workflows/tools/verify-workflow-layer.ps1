#!/usr/bin/env pwsh
# Verifies the integrity of the workflow layer.
#
# Integrity: every reference resolves, every ID cited exists where it is
# defined, every GD touchpoint is cited by the file that owns it, and nothing
# outside .claude/docs/ depends on it. Meaning (section 10): every cited door
# exists, a pipeline routes only to agents it may dispatch, every ask has a
# decline path, every cited state field exists in its template, the bug
# statuses agree, and every pre-filled counter matches its bound. No exact
# phrases, no line caps -- a file over 200 lines is a warning, never a failure.
#
# Run after any change under .claude/. Exit 0 = every check holds, 1 = a failure.

param(
    [string] $Root = (Resolve-Path (Join-Path $PSScriptRoot '..' '..' '..')).Path
)

$ErrorActionPreference = 'Stop'

$claude    = Join-Path $Root '.claude'
$workflows = Join-Path $claude 'workflows'
$docsDir   = Join-Path $claude 'docs'
$agentsDir = Join-Path $claude 'agents'
$self      = $PSCommandPath

$failures = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()
$checks   = 0

function Assert-Check
{
    param([string] $Name, [string[]] $Problems)

    $script:checks++
    $Problems = @($Problems | Where-Object { $_ })

    if ($Problems.Count -eq 0)
    {
        Write-Host ("  PASS  {0}" -f $Name)
        return
    }

    Write-Host ("  FAIL  {0}" -f $Name)
    foreach ($p in $Problems) { Write-Host ("          - {0}" -f $p) }
    $script:failures.Add(("{0} ({1})" -f $Name, $Problems.Count))
}

function Get-RelPath
{
    param([string] $Path)
    return [IO.Path]::GetRelativePath($Root, $Path).Replace('\', '/')
}

function Get-Files
{
    param([string] $Dir, [string] $Filter = '*.md')
    if (-not (Test-Path $Dir)) { return @() }
    return @(Get-ChildItem -Path $Dir -Recurse -Filter $Filter -File)
}

# The layer: what the router, the pipelines and the always-loaded rules consist of.
$layerFiles = @(Get-Files $workflows) + @(Get-Files (Join-Path $claude 'rules'))
$agentFiles = @(Get-Files $agentsDir)
$agentIds   = @($agentFiles | ForEach-Object { $_.BaseName })

# Every file a reference may resolve to: the repository minus .git and .claude/docs.
$resolvable = @(Get-ChildItem -Path $Root -Recurse -File |
    Where-Object { $_.FullName -notmatch '[\\/]\.git[\\/]' -and -not $_.FullName.StartsWith($docsDir) } |
    ForEach-Object { Get-RelPath $_.FullName })

# Names that are project runtime files or placeholders, never framework files.
$runtimeNames = @('LEDGER.md', 'DEBT.md', 'NOTES.md', 'README.md', 'ARCHITECTURE.md', 'INTEGRATION.md',
                  'CONTRACTS.md', 'DECISIONS.md', 'SPEC.md', 'WORKMEMORY.md', 'CLAUDE.md', 'SKILL.md', 'CHANGELOG.md', 'BUGS.md')

function Test-Resolves
{
    param([string] $Token, [string] $FromDir)

    $t = $Token.Trim().Replace('\', '/')
    if ($t.StartsWith('./')) { $t = $t.Substring(2) }
    if ($t -match '[<>*{}]' -or $t -match '^https?:') { return $true }
    if ($runtimeNames -contains (Split-Path $t -Leaf)) { return $true }
    if ($t.StartsWith('.workflow/')) { return $true }

    $local = Join-Path $FromDir $Token
    if (Test-Path $local) { return $true }

    foreach ($r in $resolvable)
    {
        if ($r -eq $t -or $r.EndsWith('/' + $t)) { return $true }
    }
    return $false
}

# ------------------------------------------------------------------ 1. paths

Write-Host ''
Write-Host '1. References resolve'

$pathProblems = [System.Collections.Generic.List[string]]::new()
$pathScope    = $layerFiles + $agentFiles + @(Get-Files (Join-Path $claude 'commands')) +
                @(Get-Files (Join-Path $claude 'standards')) + @(Get-Item (Join-Path $Root 'README.md'))

foreach ($file in $pathScope)
{
    $text = Get-Content -Path $file.FullName -Raw
    $dir  = $file.DirectoryName
    $rel  = Get-RelPath $file.FullName

    foreach ($m in [regex]::Matches($text, '`([^`\s]+\.(?:md|ps1))`'))
    {
        if (-not (Test-Resolves $m.Groups[1].Value $dir)) { $pathProblems.Add("$rel -> $($m.Groups[1].Value)") }
    }
    foreach ($m in [regex]::Matches($text, '\]\(([^)\s#]+)(?:#[^)]*)?\)'))
    {
        $target = $m.Groups[1].Value
        if ($target -match '^(https?|mailto):') { continue }
        if (-not (Test-Path (Join-Path $dir $target))) { $pathProblems.Add("$rel -> link $target") }
    }
}

Assert-Check 'every backticked path and relative link resolves' $pathProblems

# ------------------------------------------------------------------ 2. agents

Write-Host ''
Write-Host '2. Agent ids'

$rolePattern  = '`((?:tech-lead-[a-z-]+)|(?:[a-z]+(?:-[a-z]+)*-(?:engineer|tester|reviewer|lead|architect|investigator|evaluator|expert|artist|programmer)))`'
$unknown      = [System.Collections.Generic.List[string]]::new()

foreach ($file in $layerFiles)
{
    foreach ($m in [regex]::Matches((Get-Content -Path $file.FullName -Raw), $rolePattern))
    {
        $id = $m.Groups[1].Value
        if ($agentIds -notcontains $id) { $unknown.Add("$(Get-RelPath $file.FullName) -> $id") }
    }
}

Assert-Check 'every agent id named in the layer exists' ($unknown | Sort-Object -Unique)

$routingText = (@(Get-Files $workflows) | ForEach-Object { Get-Content -Path $_.FullName -Raw }) -join "`n"
$unreachable = @($agentIds | Where-Object { $routingText -notmatch ('`' + [regex]::Escape($_) + '`') })

Assert-Check 'every agent is reachable from the router or a pipeline' ($unreachable | ForEach-Object { "$_ is named by no workflow file" })

# ------------------------------------------------------------------ 3. skills

Write-Host ''
Write-Host '3. Skills'

$skillProblems = [System.Collections.Generic.List[string]]::new()

foreach ($file in $agentFiles)
{
    $text    = Get-Content -Path $file.FullName -Raw
    $section = [regex]::Match($text, '(?s)##\s+5\.\s+Skills you use(.*?)(\n##\s|\z)').Groups[1].Value

    foreach ($row in [regex]::Matches($section, '(?m)^\|([^|\n]+)\|'))
    {
        foreach ($m in [regex]::Matches($row.Groups[1].Value, '`([a-z0-9-]+)`'))
        {
            $skill = $m.Groups[1].Value
            if (-not (Test-Path (Join-Path $claude "skills/$skill/SKILL.md")))
            {
                $skillProblems.Add("$($file.BaseName) -> $skill")
            }
        }
    }
}

Assert-Check 'every skill an agent names exists at skills/<name>/SKILL.md' $skillProblems

# ------------------------------------------------------------------ 4. standards

Write-Host ''
Write-Host '4. Standards and their readers'

$indexText    = Get-Content -Path (Join-Path $claude 'rules/standards-index.md') -Raw
$stdProblems  = [System.Collections.Generic.List[string]]::new()
$readProblems = [System.Collections.Generic.List[string]]::new()
$indexed      = @{}
$prevReaders  = @()

foreach ($row in [regex]::Matches($indexText, '(?m)^\|\s*`(\.claude/standards/[^`]+)`\s*\|([^|]*)\|'))
{
    $path    = $row.Groups[1].Value
    $cell    = $row.Groups[2].Value
    $readers = @([regex]::Matches($cell, '`([a-z-]+)`') | ForEach-Object { $_.Groups[1].Value } |
                 Where-Object { $agentIds -contains $_ })

    if ($cell -match 'tech-lead-\*') { $readers += @($agentIds | Where-Object { $_ -like 'tech-lead-*' }) }
    if ($cell -match '\bthe same\b') { $readers += $prevReaders }

    $readers          = @($readers | Sort-Object -Unique)
    $prevReaders      = $readers
    $indexed[$path]   = $true

    if (-not (Test-Path (Join-Path $Root $path))) { $stdProblems.Add("indexed but missing: $path") }

    $leaf = Split-Path $path -Leaf
    foreach ($agent in $readers)
    {
        $agentText = Get-Content -Path (Join-Path $agentsDir "$agent.md") -Raw
        if ($agentText -notmatch [regex]::Escape($leaf)) { $readProblems.Add("$agent is listed as a reader of $leaf but never cites it") }
    }
}

foreach ($file in Get-Files (Join-Path $claude 'standards'))
{
    $path = '.claude/' + [IO.Path]::GetRelativePath($claude, $file.FullName).Replace('\', '/')
    if (-not $indexed.ContainsKey($path)) { $stdProblems.Add("no row in standards-index.md: $path") }
}

Assert-Check 'every standard has an index row, and every indexed path exists' $stdProblems
Assert-Check 'every listed reader cites the standard in its own file' $readProblems

# ------------------------------------------------------------------ 5. state

Write-Host ''
Write-Host '5. No runtime state under .claude/'

$stateDir      = Join-Path $workflows 'state'
$stateProblems = @(Get-ChildItem -Path $stateDir -Recurse -File |
    Where-Object { -not ($_.Name -eq 'README.md' -and $_.DirectoryName -eq $stateDir) -and
                   -not ($_.DirectoryName -eq (Join-Path $stateDir 'templates') -and $_.Extension -eq '.md') } |
    ForEach-Object { "unexpected file: $(Get-RelPath $_.FullName)" })

$stateProblems += @(Get-ChildItem -Path $claude -Recurse -File -Include 'LEDGER.md', 'project-state.md', 'bug-log.md', 'BUGS.md', 'calibration.md' |
    Where-Object { $_.DirectoryName -ne (Join-Path $stateDir 'templates') } |
    ForEach-Object { "runtime record inside the framework: $(Get-RelPath $_.FullName)" })

if (Test-Path (Join-Path $claude '.workflow')) { $stateProblems += 'a .workflow/ state root exists under .claude/' }

Assert-Check 'workflows/state/ holds only README.md and templates; no ledger, bug log or state root under .claude/' $stateProblems

# ------------------------------------------------------------------ 6. GD touchpoints

Write-Host ''
Write-Host '6. GD touchpoint registry'

$registryPath = Join-Path $workflows 'gd-touchpoints.md'
$registry     = Get-Content -Path $registryPath
$defined      = @{}
$regProblems  = [System.Collections.Generic.List[string]]::new()
$owner        = $null

foreach ($line in $registry)
{
    if ($line -match '^##\s+(.*)$')
    {
        $heading = $Matches[1]
        $owner   = if ($heading -match '`([^`]+\.md)`') { $Matches[1] }
                   elseif ($heading -match '^Everywhere') { 'orchestrator.md' }
                   else { $null }
        continue
    }

    if ($line -match '^\|\s*\*\*G(\d+)\*\*\s*\|')
    {
        $id = 'G' + $Matches[1]
        if ($defined.ContainsKey($id)) { $regProblems.Add("$id is defined twice") }

        $rowOwner = $owner
        if ($line -match '\|\s*`((?:rules|commands)/[^`]+\.md)`\s*\|') { $rowOwner = $Matches[1] }
        $defined[$id] = $rowOwner
    }
}

foreach ($id in $defined.Keys)
{
    $own = $defined[$id]
    if (-not $own) { $regProblems.Add("$id has no owner"); continue }

    $ownerFile = @(Get-ChildItem -Path $claude -Recurse -File -Filter (Split-Path $own -Leaf) |
        Where-Object { (Get-RelPath $_.FullName).EndsWith($own) -and -not $_.FullName.StartsWith($docsDir) })

    if ($ownerFile.Count -eq 0) { $regProblems.Add("$id owner $own does not exist"); continue }
    if ((Get-Content -Path $ownerFile[0].FullName -Raw) -notmatch ('\b' + $id + '\b'))
    {
        $regProblems.Add("$id is not cited by its owner $own")
    }
}

foreach ($file in $layerFiles + $agentFiles)
{
    if ($file.FullName -eq $registryPath) { continue }
    foreach ($m in [regex]::Matches((Get-Content -Path $file.FullName -Raw), '\bG(\d+)\b'))
    {
        if (-not $defined.ContainsKey('G' + $m.Groups[1].Value))
        {
            $regProblems.Add("$(Get-RelPath $file.FullName) cites G$($m.Groups[1].Value), which the registry does not define")
        }
    }
}

Assert-Check 'every touchpoint is unique, owned, cited by its owner, and every cited G-id exists' ($regProblems | Sort-Object -Unique)

# ------------------------------------------------------------------ 7. invariants and bounds

Write-Host ''
Write-Host '7. Invariant and bound IDs'

$invariants = @([regex]::Matches((Get-Content -Path (Join-Path $claude 'rules/orchestration.md') -Raw), '(?m)^\|\s*\*\*(I\d+)\*\*') |
    ForEach-Object { $_.Groups[1].Value })
$bounds     = @([regex]::Matches((Get-Content -Path (Join-Path $workflows 'references/bounds.md') -Raw), '(?m)^\|\s*\*\*(B\d+)\*\*') |
    ForEach-Object { $_.Groups[1].Value })
$idProblems = [System.Collections.Generic.List[string]]::new()

foreach ($file in $layerFiles + $agentFiles)
{
    $text = Get-Content -Path $file.FullName -Raw
    $rel  = Get-RelPath $file.FullName
    foreach ($m in [regex]::Matches($text, '\b(I\d+)\b')) { if ($invariants -notcontains $m.Groups[1].Value) { $idProblems.Add("$rel cites $($m.Groups[1].Value)") } }
    foreach ($m in [regex]::Matches($text, '\b(B\d+)\b')) { if ($bounds -notcontains $m.Groups[1].Value)     { $idProblems.Add("$rel cites $($m.Groups[1].Value)") } }
}

Assert-Check 'every cited I-id exists in orchestration.md and every B-id in bounds.md' ($idProblems | Sort-Object -Unique)

# ------------------------------------------------------------------ 8. docs is reference-only

Write-Host ''
Write-Host '8. Nothing outside .claude/docs/ references it'

$outsideNames = @($resolvable | ForEach-Object { Split-Path $_ -Leaf }) | Sort-Object -Unique
$docsOnly     = @(Get-Files $docsDir '*' | ForEach-Object { $_.Name } | Sort-Object -Unique |
    Where-Object { $outsideNames -notcontains $_ })
$docsPattern  = '\.claude[\\/]docs|(?<![\w.-])docs/(?:reviews|frame|prompt-templates)'
$docsProblems = [System.Collections.Generic.List[string]]::new()

foreach ($rel in $resolvable)
{
    $full = Join-Path $Root $rel
    if ($full -eq $self -or $rel -notmatch '\.(md|ps1|json|txt|yml|yaml|cs)$') { continue }

    $text = Get-Content -Path $full -Raw
    if (-not $text) { continue }

    if ($text -match $docsPattern) { $docsProblems.Add("$rel mentions the docs folder") }
    foreach ($name in $docsOnly)
    {
        if ($text -match ('(?<![\w.-])' + [regex]::Escape($name))) { $docsProblems.Add("$rel names $name") }
    }
}

Assert-Check 'no file outside .claude/docs/ references a file inside it' ($docsProblems | Sort-Object -Unique)

# ------------------------------------------------------------------ 9. agent frontmatter

Write-Host ''
Write-Host '9. Agent frontmatter'

$fmProblems = [System.Collections.Generic.List[string]]::new()

foreach ($file in $agentFiles)
{
    $head = (Get-Content -Path $file.FullName -TotalCount 12) -join "`n"
    if ($head -notmatch '(?m)^name:\s*(\S+)' -or $Matches[1] -ne $file.BaseName) { $fmProblems.Add("$($file.Name): name does not match the filename") }
    if ($head -notmatch '(?m)^description:\s*\S')                                 { $fmProblems.Add("$($file.Name): no description") }
    if ($head -notmatch '(?m)^tools:\s*\S')                                       { $fmProblems.Add("$($file.Name): no tools") }
}

Assert-Check 'every agent has name = filename, a description and tools' $fmProblems

# ------------------------------------------------------------------ 10. meaning

Write-Host ''
Write-Host '10. Cross-file meaning'

$pipelines = @('feature-intake', 'research-decision', 'feature-development', 'review-pipeline', 'qa-pipeline', 'change-request')
$doors     = @{}
$dispatch  = @{}

foreach ($p in $pipelines)
{
    $text         = Get-Content -Path (Join-Path $workflows "$p.md") -Raw
    $doors[$p]    = @([regex]::Matches($text, '(?m)^\|\s*\*\*(E\d)\*\*\s*\|') | ForEach-Object { $_.Groups[1].Value })
    $section      = [regex]::Match($text, '(?s)## May dispatch(.*?)\n## ').Groups[1].Value
    $dispatch[$p] = @([regex]::Matches($section, '(?m)^\|[^|\n]*\|') | ForEach-Object {
                        [regex]::Matches($_.Value, '`([a-z-]+)`') | ForEach-Object { $_.Groups[1].Value } })
}

# 10a. Every "`<pipeline>.md` ... **En**" names a door that pipeline's Entries table defines.
$doorProblems = [System.Collections.Generic.List[string]]::new()
foreach ($file in $layerFiles + $agentFiles)
{
    $text = Get-Content -Path $file.FullName -Raw
    foreach ($m in [regex]::Matches($text, '`((?:' + ($pipelines -join '|') + '))\.md`(?:''s)?\s+\*\*(E\d)\*\*'))
    {
        if ($doors[$m.Groups[1].Value] -notcontains $m.Groups[2].Value)
        {
            $doorProblems.Add("$(Get-RelPath $file.FullName) -> $($m.Groups[1].Value).md $($m.Groups[2].Value)")
        }
    }
}
Assert-Check 'every cited pipeline door exists in that pipeline''s Entries' ($doorProblems | Sort-Object -Unique)

# 10b. A pipeline routes work only to agents its May-dispatch table names ("→ `agent`", "dispatch `agent`").
$routeProblems = [System.Collections.Generic.List[string]]::new()
foreach ($p in $pipelines)
{
    $text = Get-Content -Path (Join-Path $workflows "$p.md") -Raw
    foreach ($m in [regex]::Matches($text, '(?:→|[Dd]ispatch(?:es)?)\s+`([a-z]+(?:-[a-z]+)+)`'))
    {
        $id = $m.Groups[1].Value
        if ($agentIds -contains $id -and $dispatch[$p] -notcontains $id) { $routeProblems.Add("$p.md routes to $id, absent from its May dispatch") }
    }
}
Assert-Check 'every agent a pipeline routes to is in its May dispatch table' ($routeProblems | Sort-Object -Unique)

# 10c. Every ask or approve touchpoint defines what happens on no.
$declineProblems = @($registry | Where-Object { $_ -match '^\|\s*\*\*(G\d+)\*\*\s*\|\s*(ask|approve)\s*\|' } | ForEach-Object {
    $id    = $Matches[1]
    $cells = $_.Trim().Trim('|').Split('|')
    if ($cells[-1].Trim() -in @('', '—', '-')) { "$id is an $($cells[1].Trim()) with no decline path" }
})
Assert-Check 'every ask and approve touchpoint has a decline path' $declineProblems

# 10d. State a pipeline cites exists in its template.
$templates  = Join-Path $stateDir 'templates'
$ledgerText = Get-Content -Path (Join-Path $templates 'feature-ledger.md') -Raw
$psText     = Get-Content -Path (Join-Path $templates 'project-state.md') -Raw
$ledgerKeys = @([regex]::Matches($ledgerText, '(?m)^-\s+([^:<\n]+):') | ForEach-Object { $_.Groups[1].Value.Trim() }) +
              @([regex]::Matches($ledgerText, '(?m)^##+\s+(.+)$') | ForEach-Object { $_.Groups[1].Value.Trim() })
$psKeys     = @([regex]::Matches($psText, '(?m)^##\s+(.+)$') | ForEach-Object { $_.Groups[1].Value.Trim() }) +
              @([regex]::Matches($psText, '(?m)^([A-Z][\w ]+):') | ForEach-Object { $_.Groups[1].Value.Trim() })
$stateProblems2 = [System.Collections.Generic.List[string]]::new()
foreach ($file in $layerFiles + $agentFiles)
{
    $text = Get-Content -Path $file.FullName -Raw
    $rel  = Get-RelPath $file.FullName
    foreach ($m in [regex]::Matches($text, 'ledger''s\s+(?:`([^`]+?):?`|\*([^*]+)\*)'))
    {
        $key = ($m.Groups[1].Value + $m.Groups[2].Value).Trim().TrimEnd(':') -replace '\s+', ' '
        
        if (-not ($ledgerKeys | Where-Object { $_ -ieq $key })) { $stateProblems2.Add("$rel -> ledger field '$key'") }
    }
    foreach ($m in [regex]::Matches($text, '`project-state\.md`\s*→\s*(?:\*([^*]+)\*|\*\*([^*]+)\*\*|`([^`]+?):?`)'))
    {
        $key = ($m.Groups[1].Value + $m.Groups[2].Value + $m.Groups[3].Value).Trim().TrimEnd(':') -replace '\s+', ' '
        if (-not ($psKeys | Where-Object { $_ -ieq $key })) { $stateProblems2.Add("$rel -> project-state section '$key'") }
    }
}
Assert-Check 'every ledger field and project-state section cited exists in its template' ($stateProblems2 | Sort-Object -Unique)

# 10e. The bug statuses agree across the standard and both templates.
$drText   = Get-Content -Path (Join-Path $claude 'standards/qa/defect-reporting.md') -Raw
$lifecycle = [regex]::Match($drText, '(?s)## Bug identity and lifecycle(.*?)\n## ').Groups[1].Value
$statusStd = @([regex]::Matches($lifecycle, '(?m)^\|\s*\*\*([^*]+)\*\*\s*\|') | ForEach-Object { $_.Groups[1].Value.Trim() } | Sort-Object)
$fbText    = Get-Content -Path (Join-Path $templates 'feature-bugs.md') -Raw
$statusRaw = [regex]::Match($fbText, '(?ms)^- Status:\s*(.+?)(?=^- |^\S)').Groups[1].Value -replace '\s+', ' '
$statusFb  = @(($statusRaw -split '\|') | ForEach-Object { $_.Trim() } | Where-Object { $_ } | Sort-Object)
$blText    = Get-Content -Path (Join-Path $templates 'bug-log.md') -Raw
$blCell    = ([regex]::Match($blText, '(?m)^\|\s*_none_\s*\|.*$').Value -split '(?<!\\)\|')[5]
$statusBl  = @(($blCell -split '\\\|') | ForEach-Object { $_.Trim() } | Where-Object { $_ -and $_ -notlike 'Void*' } | Sort-Object)
$statusProblems = @()
if (($statusStd -join ',') -ne ($statusFb -join ',')) { $statusProblems += "defect-reporting.md [$($statusStd -join ', ')] vs feature-bugs.md [$($statusFb -join ', ')]" }
if (($statusStd -join ',') -ne ($statusBl -join ',')) { $statusProblems += "defect-reporting.md [$($statusStd -join ', ')] vs bug-log.md [$($statusBl -join ', ')]" }
Assert-Check 'the bug statuses agree across defect-reporting.md and both bug templates' $statusProblems

# 10f. Every counter a template pre-fills matches its bound in bounds.md.
$boundsText = Get-Content -Path (Join-Path $workflows 'references/bounds.md') -Raw
$boundOf    = @{}
$afterOf    = @{}
foreach ($m in [regex]::Matches($boundsText, '(?m)^\|\s*\*\*(B\d+)\*\*\s*\|[^|]*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|'))
{
    $boundOf[$m.Groups[1].Value] = $m.Groups[2].Value
    $afterOf[$m.Groups[1].Value] = $m.Groups[3].Value
}
$counterChecks = @(
    @('feature-ledger.md', 'CP2 0/(\d+)', 'B11', 'bound'),
    @('feature-ledger.md', 'CP3 0/(\d+)', 'B12', 'bound'),
    @('feature-ledger.md', 'CP4-as-defect 0/(\d+)', 'B13', 'bound'),
    @('feature-ledger.md', 'sign-off re-dispatch 0/(\d+)', 'B14', 'bound'),
    @('feature-ledger.md', 'QA rounds opening new bugs 0/(\d+)', 'B15', 'bound'),
    @('feature-ledger.md', 'Measure-and-confirm: 0/(\d+)', 'B7', 'bound'),
    @('feature-ledger.md', 'round <n> of (\d+)', 'B2', 'bound'),
    @('feature-ledger.md', '\| 0 /(\d+) \|', 'B3', 'bound'),
    @('feature-ledger.md', 'n/(\d+) \(B9\)', 'B9', 'bound'),
    @('feature-ledger.md', 'n/(\d+) \(B16\)', 'B16', 'bound'),
    @('feature-ledger.md', 'n/(\d+) \(B17\)', 'B17', 'bound'),
    @('project-state.md', 'Strikes /(\d+)', 'B4', 'bound'),
    @('project-state.md', 'QA rounds opening new bugs /(\d+)', 'B15', 'bound'),
    @('feature-bugs.md', 'Reopens: 0/(\d+)', 'B6', 'bound'),
    @('feature-bugs.md', 'restarted at 0/(\d+)', 'B6', 'after'),
    @('bug-log.md', 'Reopens /(\d+)', 'B6', 'bound')
)
$counterProblems = [System.Collections.Generic.List[string]]::new()
foreach ($c in $counterChecks)
{
    $text = (Get-Content -Path (Join-Path $templates $c[0]) -Raw) -replace '\s+', ' '
    $m    = [regex]::Match($text, $c[1])
    $want = if ($c[3] -eq 'after') { $afterOf[$c[2]] } else { $boundOf[$c[2]] }
    if (-not $m.Success) { $counterProblems.Add("$($c[0]) no longer holds the $($c[2]) counter ('$($c[1])')"); continue }
    if ($m.Groups[1].Value -ne $want) { $counterProblems.Add("$($c[0]) pre-fills $($c[2]) as $($m.Groups[1].Value), bounds.md says $want") }
}
Assert-Check 'every counter a template pre-fills matches bounds.md' $counterProblems

# 10g. Every table row has as many cells as its header -- an inserted row that lost or gained a cell
# silently drops the column a reader routes on.
function Get-CellCount([string] $line)
{
    $bare = $line.Trim() -replace '\\\|', ''
    return ([regex]::Matches($bare, '\|')).Count - 1
}
$tableProblems = [System.Collections.Generic.List[string]]::new()
foreach ($file in $layerFiles + $agentFiles + @(Get-Files (Join-Path $claude 'standards')) + @(Get-Files (Join-Path $claude 'commands')))
{
    $lines   = Get-Content -Path $file.FullName
    $width   = 0
    $inFence = $false
    for ($k = 0; $k -lt $lines.Count; $k++)
    {
        $line = $lines[$k]
        if ($line -match '^\s*```') { $inFence = -not $inFence; $width = 0; continue }
        if ($line -notmatch '^\s*\|') { $width = 0; continue }
        if ($k + 1 -lt $lines.Count -and $lines[$k + 1] -match '^\s*\|\s*:?-{3,}') { $width = Get-CellCount $line; continue }
        if ($width -gt 0 -and $line -notmatch '^\s*\|\s*:?-{3,}')
        {
            $n = Get-CellCount $line
            if ($n -ne $width) { $tableProblems.Add("$(Get-RelPath $file.FullName):$($k + 1) has $n cells, its header $width") }
        }
    }
}
Assert-Check 'every table row has as many cells as its header' $tableProblems

# ------------------------------------------------------------------ 11. size (warning only)

Write-Host ''
Write-Host '11. Size -- under 200 lines is recommended, never required'

foreach ($file in @(Get-Files $workflows))
{
    $n = (Get-Content -Path $file.FullName).Count
    if ($n -gt 200) { $warnings.Add(("{0} is {1} lines" -f (Get-RelPath $file.FullName), $n)) }
}

if ($warnings.Count -eq 0) { Write-Host '  OK    every workflow file is under 200 lines' }
foreach ($w in $warnings) { Write-Host ("  WARN  {0}" -f $w) }

# ------------------------------------------------------------------ result

Write-Host ''
Write-Host ('-' * 62)

if ($failures.Count -eq 0)
{
    Write-Host ("OK  {0} checks hold, {1} size warning(s)." -f $checks, $warnings.Count)
    exit 0
}

Write-Host ("FAIL  {0} of {1} checks do not hold:" -f $failures.Count, $checks)
foreach ($f in $failures) { Write-Host ("  - {0}" -f $f) }
exit 1
