#!/usr/bin/env pwsh
# Verifies the workflow layer's claims about itself.
#
# Every number this layer states about its own shape -- how many agents hold the
# Editor lock, how many accrue review debt, how many entry points exist -- is a
# fact that drifts the moment an agent file changes. Nothing else notices.
# Run it after any change under .claude/, and before reporting the layer
# consistent.
#
# Exit code 0 = every claim holds. 1 = at least one drifted.

param(
    [string] $Root = (Resolve-Path (Join-Path $PSScriptRoot '..' '..' '..')).Path
)

$ErrorActionPreference = 'Stop'

$claude    = Join-Path $Root '.claude'
$workflows = Join-Path $claude 'workflows'
$refs      = Join-Path $workflows 'references'
$agentsDir = Join-Path $claude 'agents'

$failures = [System.Collections.Generic.List[string]]::new()
$checks   = 0

function Assert-Claim
{
    param([string] $Name, [bool] $Holds, [string] $Detail)

    $script:checks++

    if ($Holds)
    {
        Write-Host ("  PASS  {0}" -f $Name)
        return
    }

    Write-Host ("  FAIL  {0} -- {1}" -f $Name, $Detail)
    $script:failures.Add(("{0}: {1}" -f $Name, $Detail))
}

# ---------------------------------------------------------------- the agents

$agentFiles = Get-ChildItem -Path $agentsDir -Recurse -Filter '*.md' -File

$classA        = [System.Collections.Generic.List[string]]::new()
$classB        = [System.Collections.Generic.List[string]]::new()
$editorHolders = [System.Collections.Generic.List[string]]::new()
$agentIds      = [System.Collections.Generic.List[string]]::new()

foreach ($file in $agentFiles)
{
    $lines = Get-Content -Path $file.FullName
    $id    = $file.BaseName
    $agentIds.Add($id)

    $toolsLine = ($lines | Select-Object -First 20 | Where-Object { $_ -match '^tools:' }) -join ' '

    if ($toolsLine -match '\bWrite\b' -or $toolsLine -match '\bEdit\b')
    {
        $classB.Add($id)
    }
    else
    {
        $classA.Add($id)
    }

    if ($toolsLine -match 'mcp__')
    {
        $editorHolders.Add($id)
    }
}

# technical-architect is gated at CP2 rather than by review; rd-engineer marks
# its output disposable. Every other class-B agent accrues review debt.
$debtExempt   = @('technical-architect', 'rd-engineer')
$debtAccruing = @($classB | Where-Object { $debtExempt -notcontains $_ })

Write-Host ''
Write-Host 'Agent classes -- derived from the tools: frontmatter, the hard sandbox'

$dispatchText = Get-Content -Path (Join-Path $refs 'orchestrator-direct-dispatch.md') -Raw

$statedA    = [int]([regex]::Match($dispatchText, 'leaves no source\*\*\s*\((\d+)\)').Groups[1].Value)
$statedB    = [int]([regex]::Match($dispatchText, 'writes source\*\*\s*\((\d+)\)').Groups[1].Value)
$statedDebt = [int]([regex]::Match($dispatchText, 'The other \*\*(\d+)\*\* accrue review debt').Groups[1].Value)

Assert-Claim 'class A count' ($statedA -eq $classA.Count) "states $statedA, actual $($classA.Count)"
Assert-Claim 'class B count' ($statedB -eq $classB.Count) "states $statedB, actual $($classB.Count)"
Assert-Claim 'review-debt count' ($statedDebt -eq $debtAccruing.Count) `
    "states $statedDebt, actual $($debtAccruing.Count): $($debtAccruing -join ', ')"

# ------------------------------------------------------------- the two locks

Write-Host ''
Write-Host 'Global locks -- invariants I3 and I7'

$orchRule     = Get-Content -Path (Join-Path $claude 'rules' 'orchestration.md') -Raw
$statedEditor = [int]([regex]::Match($orchRule, '(\d+)\s+agents hold').Groups[1].Value)

Assert-Claim 'Editor-lock holder count' ($statedEditor -eq $editorHolders.Count) `
    "states $statedEditor, actual $($editorHolders.Count): $($editorHolders -join ', ')"

# -------------------------------------------------------------- the line cap

Write-Host ''
Write-Host 'The 200-line cap -- workflow-checklist.md is exempt by its own header'

$capExempt = @('workflow-checklist.md')

foreach ($file in (Get-ChildItem -Path $workflows -Recurse -Filter '*.md' -File))
{
    if ($capExempt -contains $file.Name)
    {
        continue
    }

    $count = (Get-Content -Path $file.FullName).Count
    Assert-Claim ("cap: {0}" -f $file.Name) ($count -le 200) "$count lines"
}

# ------------------------------------------------------------- entry points

Write-Host ''
Write-Host 'Entry points -- every door a pipeline defines has a row in the index'

$indexText = Get-Content -Path (Join-Path $refs 'entry-index.md') -Raw
$indexRows = [regex]::Matches($indexText, '(?m)^\|[^|]*\|\s*\*\*(E\d)\*\*\s*\|')

$pipelineFiles = @(
    'feature-intake.md', 'research-decision.md', 'feature-development.md',
    'review-pipeline.md', 'qa-pipeline.md', 'change-request.md'
)

$declared = 0

foreach ($name in $pipelineFiles)
{
    $text    = Get-Content -Path (Join-Path $workflows $name) -Raw
    $section = [regex]::Match($text, '(?s)##\s+Entry points(.*?)(\r?\n##\s|\z)').Groups[1].Value
    $doors   = [regex]::Matches($section, '(?m)^\|\s*\*\*(E\d)\*\*\s*\|')
    $declared += $doors.Count
}

Assert-Claim 'entry-index row count' ($indexRows.Count -eq $declared) `
    "index has $($indexRows.Count) rows, pipelines declare $declared"

# ------------------------------------------------------------------ routing
#
# The two checks below are semantic, not structural, and they exist because
# every check above this line passed for months while feature-intake E3 sent
# *every* returning feature to step 6 -- a step that runs at D3-D5 only. A
# D1-D2 feature coming back from the research branch landed on a step that
# does not run for it and a checkpoint that does not fire for it, and the
# literal reading produced a Tech Spec for a one-role change: the artifact
# budget's own named violation. Counting doors and pointers cannot see that.

Write-Host ''
Write-Host 'Routing -- an entry resuming at a shape-gated step states the shape'

foreach ($name in $pipelineFiles)
{
    $text        = Get-Content -Path (Join-Path $workflows $name) -Raw
    $stepSection = [regex]::Match($text, '(?s)##\s+Step order(.*?)(\r?\n##\s|\z)').Groups[1].Value

    if (-not $stepSection)
    {
        continue
    }

    # step number -> its 'Runs for' cell
    $runsFor = @{}

    foreach ($row in [regex]::Matches($stepSection, '(?m)^\|\s*(\d+)\s*\|([^|]*)\|([^|]*)\|'))
    {
        $runsFor[$row.Groups[1].Value] = $row.Groups[3].Value
    }

    # 'same as step N' inherits N's gate
    foreach ($step in @($runsFor.Keys))
    {
        if ($runsFor[$step] -match 'same as step (\d+)')
        {
            $inherited = $Matches[1]

            if ($runsFor.ContainsKey($inherited))
            {
                $runsFor[$step] = $runsFor[$inherited]
            }
        }
    }

    $entrySection = [regex]::Match($text, '(?s)##\s+Entry points(.*?)(\r?\n##\s|\z)').Groups[1].Value

    foreach ($row in [regex]::Matches($entrySection, '(?m)^\|\s*\*\*(E\d)\*\*\s*\|.*$'))
    {
        $door = $row.Groups[1].Value
        $line = $row.Value

        foreach ($hit in [regex]::Matches($line, 'step (\d+)'))
        {
            $step = $hit.Groups[1].Value

            if (-not $runsFor.ContainsKey($step) -or $runsFor[$step] -notmatch 'D[1-5]')
            {
                continue
            }

            Assert-Claim ("{0} {1} -> step {2} states its shape" -f $name, $door, $step) `
                ($line -match 'D[1-5]') `
                ("step $step runs at '$($runsFor[$step].Trim())' and this row names no shape")
        }
    }
}

Write-Host ''
Write-Host 'Routing -- every cross-file entry reference names a door that exists'

$declaredDoors = @{}

foreach ($name in $pipelineFiles)
{
    $text    = Get-Content -Path (Join-Path $workflows $name) -Raw
    $section = [regex]::Match($text, '(?s)##\s+Entry points(.*?)(\r?\n##\s|\z)').Groups[1].Value

    $declaredDoors[$name] = @(
        [regex]::Matches($section, '(?m)^\|\s*\*\*(E\d)\*\*\s*\|') |
            ForEach-Object { $_.Groups[1].Value }
    )
}

$badRefs = [System.Collections.Generic.List[string]]::new()

foreach ($file in (Get-ChildItem -Path $workflows -Recurse -Filter '*.md' -File))
{
    if ($file.Name -eq 'workflow-checklist.md')
    {
        continue
    }

    foreach ($line in (Get-Content -Path $file.FullName))
    {
        foreach ($hit in [regex]::Matches($line, '`([a-z-]+\.md)`[^|`]{0,40}?\*\*(E\d)\*\*'))
        {
            $target = $hit.Groups[1].Value
            $door   = $hit.Groups[2].Value

            if ($declaredDoors.ContainsKey($target) -and $declaredDoors[$target] -notcontains $door)
            {
                $badRefs.Add(('{0} sends work to {1} {2}' -f $file.Name, $target, $door))
            }
        }
    }
}

Assert-Claim 'no reference to an undeclared entry' ($badRefs.Count -eq 0) `
    (($badRefs | Sort-Object -Unique) -join '; ')

# -------------------------------------------------- references are reachable

Write-Host ''
Write-Host 'References -- no orphan, no dangling pointer'

$sourceText = ''

foreach ($file in (Get-ChildItem -Path $workflows -Recurse -Filter '*.md' -File))
{
    $sourceText += (Get-Content -Path $file.FullName -Raw)
}

foreach ($file in (Get-ChildItem -Path $refs -Filter '*.md' -File))
{
    if ($file.Name -eq 'README.md')
    {
        continue
    }

    $pointed = $sourceText -match [regex]::Escape($file.Name)
    Assert-Claim ("pointed at: {0}" -f $file.Name) $pointed 'no workflow file names it'
}

# ------------------------------------------ no line-number cross-references

Write-Host ''
Write-Host 'Cross-references -- anchored to quoted text, never to a line number'

$allLayer = Get-ChildItem -Path $workflows -Recurse -Filter '*.md' -File
$lineRefs = [System.Collections.Generic.List[string]]::new()

foreach ($file in $allLayer)
{
    # workflow-checklist.md is an append-only record and legitimately quotes past
    # mistakes -- including the stale line references this check exists to stop.
    if ($file.Name -eq 'workflow-checklist.md')
    {
        continue
    }

    $matches = [regex]::Matches((Get-Content -Path $file.FullName -Raw), '`([a-z][a-z0-9-]+):(\d{1,4})`')

    foreach ($match in $matches)
    {
        if ($agentIds -contains $match.Groups[1].Value)
        {
            $lineRefs.Add(("{0} -> {1}" -f $file.Name, $match.Value))
        }
    }
}

Assert-Claim 'no agent line-number references' ($lineRefs.Count -eq 0) ($lineRefs -join '; ')

# --------------------------------------------- every named agent-id exists

Write-Host ''
Write-Host 'Agent ids -- every hyphenated id a workflow names is a real agent file'

$unknown = [System.Collections.Generic.List[string]]::new()

# Hyphenated backticked tokens that are vocabulary, not agent ids.
$vocabulary = @(
    'agent-id', 'agent-ids', 'feature-slug', 'feature-root', 'measure-and-confirm',
    'three-strikes', 'Needs-decision', 'Co-Authored-By', 'plan-test-coverage',
    'investigate-device-crash', 'device-test-walkthrough', 'secret-and-supply-chain-scan',
    'engineering-standard-adr-authoring',
    'read-only', 'client-server', 'run-to-run', 'per-case', 'pass-fail', 'Game-Core'
)

foreach ($file in $allLayer)
{
    if ($file.Name -eq 'workflow-checklist.md')
    {
        continue
    }

    $matches = [regex]::Matches((Get-Content -Path $file.FullName -Raw), '`/?([a-z][a-z0-9]+(?:-[a-z0-9]+)+)`')

    foreach ($match in $matches)
    {
        $id = $match.Groups[1].Value

        if ($id -match '\.(md|ps1)$')     { continue }
        if ($vocabulary -contains $id)    { continue }
        if ($agentIds -contains $id)      { continue }

        $unknown.Add(("{0}: {1}" -f $file.Name, $id))
    }
}

$unknown = @($unknown | Sort-Object -Unique)

Assert-Claim 'no unknown agent-id' ($unknown.Count -eq 0) ($unknown -join '; ')

# ----------------------------------------- every agent is reachable by name

Write-Host ''
Write-Host 'Reachability -- every agent is named by at least one workflow file'

$workflowProse = ''

foreach ($file in $allLayer)
{
    if ($file.Name -eq 'workflow-checklist.md')
    {
        continue
    }

    $workflowProse += (Get-Content -Path $file.FullName -Raw)
}

$unreachable = @($agentIds | Where-Object { $workflowProse -notmatch ("``{0}``" -f [regex]::Escape($_)) })

Assert-Claim 'no unreachable agent' ($unreachable.Count -eq 0) `
    ("named by no workflow file, so no lane can route to it: $($unreachable -join ', ')")

# --------------------------------------------- the standards tree is wired

Write-Host ''
Write-Host 'Standards -- loaded on demand, so every one needs a stated reader'

$standardsDir = Join-Path $claude 'standards'
$indexPath    = Join-Path $claude 'rules' 'standards-index.md'

if (Test-Path $standardsDir)
{
    $indexText = Get-Content -Path $indexPath -Raw

    foreach ($file in (Get-ChildItem -Path $standardsDir -Recurse -Filter '*.md' -File))
    {
        $rel = $file.FullName.Substring($claude.Length + 1).Replace('\', '/')
        Assert-Claim ("reader stated: {0}" -f $rel) ($indexText -match [regex]::Escape($rel)) `
            'no row in rules/standards-index.md, so nothing tells an agent to read it'
    }

    # Nothing may still point at the old auto-loaded location.
    $stale = [System.Collections.Generic.List[string]]::new()

    foreach ($file in (Get-ChildItem -Path $claude -Recurse -Filter '*.md' -File))
    {
        # workflow-checklist.md is an append-only record: it states where files
        # used to live, which is history rather than a dangling path.
        if ($file.Name -eq 'workflow-checklist.md')
        {
            continue
        }

        if ((Get-Content -Path $file.FullName -Raw) -match 'rules/(client|qa)/')
        {
            $stale.Add($file.Name)
        }
    }

    Assert-Claim 'no stale rules/client or rules/qa path' ($stale.Count -eq 0) `
        ("still points at the pre-move location: $(($stale | Sort-Object -Unique) -join ', ')")
}

# ------------------------------------ no runtime state written under .claude/

# .claude/ is the framework, copied unchanged into every project that adopts it.
# A ledger, a lock or a calibration row written into it is one project's history
# sitting in the template the next project starts from. workflows/state/ holds
# the state layer's rules and its templates, and nothing else.

Write-Host ''
Write-Host 'Runtime state -- .claude/ is the framework, so no run writes state into it'

$stateDir     = Join-Path $workflows 'state'
$templatesDir = Join-Path $stateDir 'templates'
$stray        = [System.Collections.Generic.List[string]]::new()

foreach ($item in (Get-ChildItem -Path $stateDir -Force))
{
    if ($item.PSIsContainer)
    {
        if ($item.Name -ne 'templates')
        {
            $stray.Add(('{0}/' -f $item.Name))
        }

        continue
    }

    if ($item.Name -ne 'README.md')
    {
        $stray.Add($item.Name)
    }
}

Assert-Claim 'no state under workflows/state' ($stray.Count -eq 0) `
    ("only README.md and templates/ belong here; found: $($stray -join ', ')")

# A template that pipelines cite by name and nobody kept is a dangling copy-from.
foreach ($name in @('feature-ledger.md', 'project-state.md', 'calibration.md'))
{
    Assert-Claim ("template present: {0}" -f $name) (Test-Path (Join-Path $templatesDir $name)) `
        'a pipeline tells the orchestrator to copy this, and it is not there'
}

# Nothing may still route state back into the framework.
$retired = @(
    'workflows/state/<feature-slug>',
    'state/<feature-slug>/ledger.md',
    '`state/project-state.md`',
    '`state/calibration.md`'
)

$pointsBack = [System.Collections.Generic.List[string]]::new()

foreach ($file in (Get-ChildItem -Path $claude -Recurse -Filter '*.md' -File))
{
    # workflow-checklist.md is an append-only record: it states where state used
    # to live, which is history rather than an instruction to write there.
    if ($file.Name -eq 'workflow-checklist.md')
    {
        continue
    }

    $text = Get-Content -Path $file.FullName -Raw

    foreach ($path in $retired)
    {
        if ($text -match [regex]::Escape($path))
        {
            $pointsBack.Add(('{0} -> {1}' -f $file.Name, $path))
        }
    }
}

Assert-Claim 'no pointer at the retired state paths' ($pointsBack.Count -eq 0) `
    ("would send a run to write under .claude/: $(($pointsBack | Sort-Object -Unique) -join '; ')")

# --------------------------------------------------------------- the result

Write-Host ''
Write-Host ('-' * 62)

if ($failures.Count -eq 0)
{
    Write-Host ("OK  {0} claims checked, every one holds." -f $checks)
    exit 0
}

Write-Host ("DRIFT  {0} of {1} claims no longer hold:" -f $failures.Count, $checks)

foreach ($failure in $failures)
{
    Write-Host ("  - {0}" -f $failure)
}

exit 1
