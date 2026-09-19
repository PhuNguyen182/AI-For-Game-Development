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

# Gaps the GD has been shown the cost of and chose to defer. A deferred gap is
# still a real defect: it still FAILs, it still prints, and it is still counted
# as a claim that does not hold. What this list changes is only whether the run
# reads as NEW drift -- because a tool that is permanently red stops being read,
# which is the same failure optional-gates.md names about a re-offered ask.
# Never add a row here to make a run green. A row is the GD's decision, dated,
# and it is removed the moment the underlying defect is fixed.
$acceptedGaps = @{
    'every named skill is registrable' =
        'GD-deferred 2026-09-19: all 90 project skills sit one level too deep to register. Fix is to move skills/<group>/<name>/ up to skills/<name>/ -- mechanical, reversible, deliberately not taken this round. Evidence has since gone past "a gate read its skill by hand": in the QA round qa-lead found risk-based-test-planning unresolvable and SUBSTITUTED a different skill, stating it. An outage that changes which technique an agent applies is no longer only a tooling gap.'
}

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

# ----------------------------------------------------------- custody (fix J)
#
# The two checks below close the class the debt register calls "an agent
# produces something no pipeline row receives". It was closed instance by
# instance before, and recurred every time: R1, R9 and R10 in the research
# round, then four more found by running feature-development. A prose fix
# closes an instance; only a check closes the class.
#
# Scope is all six pipelines -- change-request.md was the last to be reviewed
# against a real run and is now included. Extending scope only after a real
# run, rather than asserting it on inspection alone, is what this comment
# tracks; $custodyUnchecked stays as the record of which ones still need one.

Write-Host ''
Write-Host 'Custody -- every destination an agent can name has a routing row'

$custodyReviewed  = @('feature-intake.md', 'research-decision.md', 'feature-development.md',
                      'review-pipeline.md', 'qa-pipeline.md', 'change-request.md')
$custodyUnchecked = @($pipelineFiles | Where-Object { $custodyReviewed -notcontains $_ })

$refFiles = Get-ChildItem -Path $refs -Filter '*.md' -File

# A pipeline's scope is its own text plus only the references that belong to
# IT -- development-*, intake-*, research-*. The shared references are excluded
# deliberately: entry-index.md, optional-gates.md, loop-termination.md and
# standalone-runs.md between them name most of the roster, so counting them as
# scope would let almost any destination pass on somebody else's sentence.
$refPrefix = @{
    'feature-intake.md'      = 'intake-'
    'research-decision.md'   = 'research-'
    'feature-development.md' = 'development-'
    'review-pipeline.md'     = 'review-'
    'qa-pipeline.md'         = 'qa-'
    'change-request.md'      = 'change-'
}

function Get-PipelineScope
{
    param([string] $Text, [string] $Pipeline, [switch] $RoutingOnly)

    $scope = if ($RoutingOnly)
    {
        [regex]::Match($Text, '(?s)##\s+Routing rules the pipeline owns(.*)$').Groups[1].Value
    }
    else
    {
        $Text
    }

    foreach ($ref in $refFiles)
    {
        if ($ref.Name.StartsWith($refPrefix[$Pipeline]) -and $Text -match [regex]::Escape($ref.Name))
        {
            $scope += (Get-Content -Path $ref.FullName -Raw)
        }
    }

    return $scope
}

$orphanRoutes   = [System.Collections.Generic.List[string]]::new()
$orphanProduces = [System.Collections.Generic.List[string]]::new()

foreach ($name in $custodyReviewed)
{
    $text      = Get-Content -Path (Join-Path $workflows $name) -Raw
    $agentsSec = [regex]::Match($text, '(?s)##\s+The agents this pipeline dispatches(.*?)(\r?\n##\s)').Groups[1].Value
    $routing   = Get-PipelineScope -Text $text -Pipeline $name -RoutingOnly

    # An absent section is a finding, not an exception. Without this guard
    # `$text.Replace('', '')` throws and the run ABORTS at this line, skipping
    # every claim after it -- including the skill and runtime-state checks. Found
    # by negative-testing a renamed heading, not by reading the script.
    if (-not $agentsSec)
    {
        $orphanProduces.Add(('{0}: no "## The agents this pipeline dispatches" section to check' -f $name))
        continue
    }

    # Everything except the agents table itself -- an artifact matching its own
    # declaration is what made the first version of this check pass on a file
    # that received none of its nine.
    $elsewhere = Get-PipelineScope -Text $text.Replace($agentsSec, '') -Pipeline $name

    $dispatched = @(
        [regex]::Matches($agentsSec, '(?m)^\|\s*`([a-z0-9-]+)`') |
            ForEach-Object { $_.Groups[1].Value }
    )

    foreach ($id in $dispatched)
    {
        $file = $agentFiles | Where-Object { $_.BaseName -eq $id }

        if (-not $file)
        {
            continue
        }

        $agentText = Get-Content -Path $file.FullName -Raw

        $destinations = @(
            [regex]::Matches($agentText, 'Routed to:\s*`?([a-z0-9-]+)`?') |
                ForEach-Object { $_.Groups[1].Value }
        ) | Where-Object { ($agentIds -contains $_) -or ($_ -eq 'gd') } | Sort-Object -Unique

        foreach ($destination in $destinations)
        {
            if ($routing -notmatch [regex]::Escape($destination))
            {
                $orphanRoutes.Add(('{0}: {1} -> {2} has no routing row' -f $name, $id, $destination))
            }
        }
    }

    # Every artifact the agents table declares under Produces must be named
    # again somewhere the pipeline actually acts on it.
    # Take the whole Produces cell, then every bolded artifact inside it. The
    # earlier form anchored on a LONE '**x**' filling the cell, so the moment a
    # row declared two artifacts it matched nothing and the row went unchecked
    # in silence -- found by negative test, not by reading.
    $produces = @(
        foreach ($row in [regex]::Matches($agentsSec, '(?m)^\|[^|]*\|[^|]*\|([^|]*)\|'))
        {
            foreach ($hit in [regex]::Matches($row.Groups[1].Value, '\*\*([^*]+)\*\*'))
            {
                $hit.Groups[1].Value.Trim()
            }
        }
    ) | Sort-Object -Unique

    foreach ($artifact in $produces)
    {
        if ($elsewhere -cnotmatch [regex]::Escape($artifact))
        {
            $orphanProduces.Add(('{0}: "{1}" is declared and never received' -f $name, $artifact))
        }
    }
}

Assert-Claim 'no destination without a routing row' ($orphanRoutes.Count -eq 0) ($orphanRoutes -join '; ')
Assert-Claim 'no Produces artifact nothing receives' ($orphanProduces.Count -eq 0) ($orphanProduces -join '; ')

# The check above reads the agents table's THIRD column. qa-pipeline.md's third
# column was 'Runs in', not 'Produces' -- so the check extracted one incidental
# bolded phrase, found it named elsewhere, and PASSED while six of that
# pipeline's eight deliverables were named nowhere in its own text or its own
# references -- which is what the restored-column FAIL actually listed. A check that
# passes for the wrong reason turns an open defect into a green claim, so the
# column the check depends on is now itself asserted.

$missingProduces = @(
    foreach ($name in $pipelineFiles)
    {
        $text      = Get-Content -Path (Join-Path $workflows $name) -Raw
        $agentsSec = [regex]::Match($text,
            '(?s)##\s+The agents this pipeline dispatches(.*?)(\r?\n##\s)').Groups[1].Value

        # No section, or no header row, is a FAILURE and never a skip: the
        # custody checks key to this same heading, so a pipeline that loses it
        # makes BOTH of them pass vacuously. A silent `continue` here is the
        # bypass this check exists to close.
        if (-not $agentsSec)
        {
            '{0}: no "## The agents this pipeline dispatches" section -- both custody checks pass vacuously' -f $name
            continue
        }

        # No `$` anchor: with `[^\r\n]*$` a CRLF file never matches, because `$`
        # wants the position before `\n` and the class stops before `\r`. The
        # first version of this check had it, so two of the six pipelines
        # produced an empty header and were skipped by a silent `continue` --
        # the exact bypass an independent review predicted, confirmed by running
        # it rather than by reading it.
        $header = [regex]::Match($agentsSec, '(?m)^\|\s*Agent\s*\|[^\r\n]*').Value

        # POSITION, not presence. `| Agent | Tier | Owns | Produces |` names the
        # column and still puts `Owns` in the cell the custody check reads, which
        # is the same blindness reached by a column swap.
        if ($header -notmatch '^\|\s*Agent\s*\|[^|]*\|\s*Produces\s*\|')
        {
            '{0}: agents table header is "{1}" -- Produces must be the THIRD column' -f `
                $name, $(if ($header) { $header.Trim() } else { '(no | Agent | header row)' })
            continue
        }

        # And the column has to carry something. The pre-round table held `—`
        # in two rows; a row reverted to `—` passes a column-only check while
        # that deliverable leaves custody in silence.
        foreach ($row in [regex]::Matches($agentsSec, '(?m)^\|\s*`([a-z0-9-]+)`\s*\|[^|]*\|([^|]*)\|'))
        {
            if ($row.Groups[2].Value -notmatch '\*\*[^*]+\*\*')
            {
                '{0}: `{1}` declares no artifact ("{2}")' -f `
                    $name, $row.Groups[1].Value, $row.Groups[2].Value.Trim()
            }
        }
    }
)

Assert-Claim 'every agents table declares a Produces column, third, and fills it' ($missingProduces.Count -eq 0) `
    (($missingProduces -join '; ') + ' -- the custody check reads column 3 positionally, so anything else makes it blind')

if ($custodyUnchecked.Count -gt 0)
{
    Write-Host ("  INFO  custody scope: {0} reviewed; not yet asserted for {1}" -f `
        ($custodyReviewed -join ', '), ($custodyUnchecked -join ', '))
}
else
{
    Write-Host ("  INFO  custody scope: all six pipelines reviewed and asserted")
}

# ------------------------------------------- the gate offer has one owner
#
# optional-gates.md owns the SHAPE of every gate ask; the pipeline that reaches
# a boundary owns WHERE it fires. "The orchestrator asks the GD" is shorthand
# for the one case that belongs to no pipeline, and that file now says outright
# that a pipeline consuming the rule never restates it. It has been corrected in
# the owning file twice and recurred in a consuming file both times -- review
# first, then QA, five rounds after the layer assessment logged it as F6. That
# is a class, not an instance, and only a check has ever closed a class here.

Write-Host ''
Write-Host 'The gate offer -- no pipeline restates the ask as the orchestrator''s'

$restated = [System.Collections.Generic.List[string]]::new()

# Scope is every pipeline AND every reference except optional-gates.md, which
# owns the rule and is the one file allowed to say it. A first version scanned
# the six pipelines only and matched the single recurring sentence; a
# restatement one file over, in a reference, would have passed.
$askScope = @(
    ($pipelineFiles | ForEach-Object { Join-Path $workflows $_ }) +
    (Get-ChildItem -Path $refs -Filter '*.md' -File |
        Where-Object { $_.Name -ne 'optional-gates.md' } |
        ForEach-Object { $_.FullName })
)

foreach ($path in $askScope)
{
    foreach ($line in (Get-Content -Path $path))
    {
        # Naming the orchestrator as the asker is CORRECT for an ask belonging
        # to no pipeline -- that is the third row of optional-gates.md's own
        # ownership table, and review-pipeline.md says exactly that. A first
        # widening flagged it, which is how a check starts being ignored. So the
        # forbidden shape is the orchestrator asking *the GD*, the sentence that
        # has now recurred three times; a line qualifying itself with "no
        # pipeline" is excluded outright.
        if ($line -match '(?i)\bno pipeline\b')
        {
            continue
        }

        if ($line -match '(?i)\borchestrator\b[^.\r\n]{0,40}?\b(asks?|ask|offers?)\b[^.\r\n]{0,25}?\bthe GD\b' -or
            $line -match '(?i)\b(asked|offered)\b[^.\r\n]{0,30}?\bby the orchestrator\b')
        {
            $restated.Add(('{0}: {1}' -f (Split-Path $path -Leaf), $line.Trim()))
        }
    }
}

Assert-Claim 'no consuming file restates the gate ask as the orchestrator''s' ($restated.Count -eq 0) `
    (($restated -join '; ') + ' -- whichever party reached the boundary asks; optional-gates.md owns and states it')

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

# ------------------------------------------- loop-termination counts itself
#
# loop-termination.md opens by claiming it is "the single home for every bound
# in the layer", then states two counts in prose: how many caps the table holds
# and how many are stated only there. Adding a row and not updating the prose
# is a one-line edit away at all times, and this layer has shipped a stale
# self-count before. The claim is checkable, so it is checked.

Write-Host ''
Write-Host 'Loop termination -- the cap table matches the counts stated beside it'

$loopText = Get-Content -Path (Join-Path $refs 'loop-termination.md') -Raw
$capTable = [regex]::Match($loopText, '(?s)\|\s*Counter\s*\|\s*Bound.*?\n\s*\n').Value

$capRows = @([regex]::Matches($capTable, '(?m)^\|.*\|\s*$')) |
    Where-Object { $_.Value -notmatch '^\|\s*Counter\s*\|' -and $_.Value -notmatch '^\|[-\s|:]+\|\s*$' }

$hereRows = @([regex]::Matches($capTable, '\|\s*\*\*here\*\*\s*\|'))

$words = @{
    'ten' = 10; 'eleven' = 11; 'twelve' = 12; 'thirteen' = 13; 'fourteen' = 14
    'fifteen' = 15; 'sixteen' = 16; 'seventeen' = 17; 'eighteen' = 18
    'nineteen' = 19; 'twenty' = 20
}

$stated = [regex]::Match($loopText, '(?i)([a-z]+)\s+of\s+those\s+([a-z]+)\s+are\s+stated\s+here')

Assert-Claim 'loop-termination states its own cap count' `
    ($stated.Success -and $words[$stated.Groups[2].Value.ToLower()] -eq $capRows.Count) `
    ("prose says $($stated.Groups[2].Value), table holds $($capRows.Count)")

Assert-Claim 'loop-termination states its own stated-here count' `
    ($stated.Success -and $words[$stated.Groups[1].Value.ToLower()] -eq $hereRows.Count) `
    ("prose says $($stated.Groups[1].Value), table marks $($hereRows.Count)")

# --------------------------------------------------- skills actually resolve
#
# Every agent's section 5 names skills it is told to invoke, several of them
# "Always". The harness registers a skill at .claude/skills/<name>/SKILL.md --
# one level, not two. A live review round found BOTH gate skills unresolvable
# (Unknown skill), and both gates fell back to reading SKILL.md by hand and
# said so. A gate whose mandatory scan silently does not run still returns a
# verdict, which is the one failure security.md builds that gate to prevent.
# Structural checks cannot see this: the file exists, it is just not where the
# harness looks.

Write-Host ''
Write-Host 'Skills -- every skill an agent is told to invoke must be registrable'

$skillsRoot  = Join-Path $claude 'skills'
$namedSkills = [System.Collections.Generic.List[string]]::new()

foreach ($file in $agentFiles)
{
    $text    = Get-Content -Path $file.FullName -Raw
    $section = [regex]::Match($text, '(?s)##\s+5\.\s+Skills you use(.*?)(\n##\s|\z)').Groups[1].Value

    foreach ($hit in [regex]::Matches($section, '(?m)^\|\s*`([a-z0-9-]+)`\s*\|'))
    {
        if (-not $namedSkills.Contains($hit.Groups[1].Value))
        {
            $namedSkills.Add($hit.Groups[1].Value)
        }
    }
}

$unresolvable = [System.Collections.Generic.List[string]]::new()

foreach ($skill in $namedSkills)
{
    # Registrable means exactly .claude/skills/<name>/SKILL.md.
    if (-not (Test-Path -Path (Join-Path $skillsRoot (Join-Path $skill 'SKILL.md'))))
    {
        $nested = Get-ChildItem -Path $skillsRoot -Recurse -Filter 'SKILL.md' -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Directory.Name -eq $skill }

        $unresolvable.Add($(if ($nested)
            {
                '{0} (present at skills/{1}/{0}/ -- one level too deep to register)' -f $skill, $nested[0].Directory.Parent.Name
            }
            else
            {
                '{0} (no SKILL.md anywhere)' -f $skill
            }))
    }
}

$nestedCount = @($unresolvable | Where-Object { $_ -match 'too deep' }).Count
$missing     = @($unresolvable | Where-Object { $_ -match 'no SKILL.md' })

$skillDetail = if ($nestedCount -eq $unresolvable.Count -and $nestedCount -gt 0)
{
    '{0} of {1} unresolvable -- ALL of them one level too deep. The harness registers skills/<name>/SKILL.md; these sit at skills/<group>/<name>/SKILL.md, so none loads. Example: {2}' -f `
        $unresolvable.Count, $namedSkills.Count, $unresolvable[0]
}
else
{
    '{0} of {1} unresolvable ({2} nested too deep, {3} absent). First few: {4}' -f `
        $unresolvable.Count, $namedSkills.Count, $nestedCount, $missing.Count,
        (($unresolvable | Select-Object -First 3) -join '; ')
}

Assert-Claim ('every named skill is registrable ({0} named)' -f $namedSkills.Count) `
    ($unresolvable.Count -eq 0) $skillDetail

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

$accepted = @($failures | Where-Object { $name = $_; @($acceptedGaps.Keys | Where-Object { $name.StartsWith($_) }).Count -gt 0 })
$drift    = @($failures | Where-Object { $name = $_; @($acceptedGaps.Keys | Where-Object { $name.StartsWith($_) }).Count -eq 0 })

foreach ($gap in $accepted)
{
    $key = @($acceptedGaps.Keys | Where-Object { $gap.StartsWith($_) })[0]
    Write-Host ("ACCEPTED GAP  {0}" -f $key)
    Write-Host ("              {0}" -f $acceptedGaps[$key])
}

if ($drift.Count -eq 0)
{
    Write-Host ("OK  {0} claims checked; {1} hold, {2} accepted gap(s) above and no new drift." -f `
        $checks, ($checks - $accepted.Count), $accepted.Count)
    exit 0
}

Write-Host ("DRIFT  {0} of {1} claims no longer hold:" -f $drift.Count, $checks)

foreach ($failure in $drift)
{
    Write-Host ("  - {0}" -f $failure)
}

exit 1
