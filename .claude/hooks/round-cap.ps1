# Round caps of the stop rule (routing.md). Brief marker lines: /review, /fix and /qa write them.
#   count     SubagentStop: adds a failed round to the round ledger .workflow/ledger.db (records.py ledger add) when
#             - a review gate fails (code-reviewer Request changes, or Needs-decision with a Critical/High/Medium
#               finding; security-reviewer Blocked), unless the brief says "Mode: audit", "Mode: test-code" or
#               "Mode: workflow" (review-gate's gates: the main session records those rounds itself);
#             - qa-lead returns Not signed off;
#             - a brief with "Verify: BUG-####" returns "Repro: BUG-#### reproduces".
#             Charged only to the brief's "Feature:" line, else its "Bug:" line, else its "Target:" line, else the
#             session. Failed returns are attempts, not rounds: never counted here.
#   dispatch  PreToolUse Agent / Workflow: an adviser always passes; anything else is blocked when the brief's (or the workflow args') feature, bug or target
#             is past a cap. A brief without marker lines falls back to every feature path and bug id it mentions.
#             Each counter checked needs Python: no Python, or any records.py or bugs.py failure, blocks the dispatch.
#             A dispatch with nothing to count (no feature, bug or target found, not a gate agent) starts no Python.
#             A bug ID is one bug whatever its case or padding: bug-0027, BUG-27 and BUG-00027 all mean BUG-0027.
#   edit      PostToolUse Edit/Write under .workflow/, and Bash/PowerShell commands that call bugs.py (for the bug ids in
#             the command) or records.py (for the feature slugs in it): tells Claude when a counter reaches or passes its
#             cap (silent at the cap once a Stop rule names that counter), or an open feature has no Rounds line or no
#             registry record. Any other command exits at once.
# Counters: a feature's file-only rounds from "records.py feature counters <slug> --json" (the feature registry), or, for a
# feature the registry does not hold, its un-migrated file's "- Rounds: review n/cap, QA n/cap, rework n/cap" line; a bug's
# fix and review rounds from "bugs.py counters". Both hold only events this hook cannot see; Used = file or database +
# ledger. A cap above the default counts only with an "extra round" line in the counters' record ("records.py feature
# extra-round" and "bugs.py extra-round" write it; an un-migrated file's Main GD decisions); for target or session work,
# one "extra-<counter>" entry in the ledger per extra round.
# Ledger: "records.py ledger get --json" and "ledger add --json", rooted like bugs.py (a linked worktree reads and writes the
# main checkout's). A busy ledger, no Python or a failed add parks the events in .workflow/rounds.pending-<id>.json, merged
# on the next add; an unreadable ledger.db is moved aside to ledger.corrupt-<utc>.db by the next add, never overwritten;
# dispatch fails closed while the ledger cannot be read or a moved-aside file is left.
param([Parameter(Mandatory)][ValidateSet('count', 'dispatch', 'edit')][string]$Mode)
. "$PSScriptRoot/common.ps1"

$Defaults = @{ review = 3; qa = 2; fix = 2; 'rework-M' = 6; 'rework-L' = 8 }
$Gates = 'code-reviewer', 'security-reviewer', 'qa-lead'

$in = Read-HookInput
if (-not $in) { exit 0 }
# Advisers read and advise: a past-cap feature or a broken ledger must not stop a note (skill advisory-protocol). Before the ledger is read.
if ($Mode -eq 'dispatch' -and [string]$in.tool_name -ne 'Workflow' -and $AdvisoryAgents -ccontains [string]$in.tool_input.subagent_type) { exit 0 }
$root = Get-ProjectRoot $in
$sessionKey = "session:$([string]$in.session_id)"
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfff')
$utf8 = New-Object Text.UTF8Encoding $false
$UnreadableOutput = 'returned unreadable output. Run it by hand to see why, then retry (skill records).'

# The checkout whose .workflow holds the ledger and the registry: the bugs root rule. Resolved once, when first needed; throws.
$script:RecordsRoot = $null
function Get-RecordsRoot { if (-not $script:RecordsRoot) { $script:RecordsRoot = Get-BugsRoot $root }; return $script:RecordsRoot }
function Test-JsonObject($o) { return $null -ne $o -and $o.GetType().FullName -eq 'System.Management.Automation.PSCustomObject' }

# The ledger { key: { counter: [event ids] } }, read once, and only when a counter needs it. Throws the cause and its fix.
$script:Ledger = $null
$script:LedgerBusy = $false
function Get-LedgerView {
    if ($null -ne $script:Ledger) { return $script:Ledger }
    $r = Invoke-Records (Get-RecordsRoot) @('ledger', 'get', '--json')
    if ($r.State -eq 'NoPython') { throw 'no Python 3.10+ with SQLite FTS5 found, so the round ledger .workflow/ledger.db cannot be read. Install it, then retry (skill records).' }
    if ($r.State -ne 'Ok') {
        if ($r.Code -eq 75) { $script:LedgerBusy = $true; throw '.workflow/ledger.db is locked or busy. Retry the dispatch.' }
        if ($r.Code -eq 3) { throw "the round ledger is unreadable ($($r.Err)). Its counts cannot be trusted until that file is resolved: report the stop-rule state to the main GD (skill records)." }
        throw "records.py ledger get failed: $($r.Err). Clear that cause, then retry (skill records)."
    }
    $o = $null
    try { $o = $r.Out | ConvertFrom-Json -ErrorAction Stop } catch {}
    # A shape this hook does not know must not read as 0 rounds.
    if (-not (Test-JsonObject $o)) { throw "records.py ledger get $UnreadableOutput" }
    $l = @{}
    foreach ($k in $o.PSObject.Properties) {
        if (-not (Test-JsonObject $k.Value)) { throw "records.py ledger get $UnreadableOutput" }
        $l[$k.Name] = @{}
        foreach ($c in $k.Value.PSObject.Properties) { $l[$k.Name][$c.Name] = @($c.Value | Where-Object { $null -ne $_ }) }
    }
    $script:Ledger = $l
    return $l
}

# $ledger is kept for the callers' shape: the ledger itself is read lazily, once per run.
function Get-LedgerCount($ledger, [string]$key, [string]$counter) {
    $l = Get-LedgerView
    if (-not $l.ContainsKey($key) -or -not $l[$key].ContainsKey($counter)) { return 0 }
    return @($l[$key][$counter]).Count
}

# Files a broken ledger left for the main GD (records.py ledger get refuses on the same names). Listed without Python, so a
# dispatch with nothing to count still stops on them, as it always has.
function Get-LedgerMarks {
    $dir = Join-Path $root '.workflow'
    try { $dir = Join-Path (Get-RecordsRoot) '.workflow' } catch {}  # a link that leads nowhere blocks once a counter needs the root
    if (-not (Test-Path -LiteralPath $dir -PathType Container)) { return @() }
    return @(Get-ChildItem -LiteralPath $dir -File | Where-Object { $_.Name -like 'ledger.corrupt-*.db' -or $_.Name -like 'rounds.corrupt-*.json' })
}

# Parks events where the next ledger add merges them: [{key, counter, id}], UTF-8 with no BOM.
function Save-Pending([string]$Dir, [string]$Json, [string]$Why) {
    $wf = Join-Path $Dir '.workflow'
    New-Item -ItemType Directory -Force $wf | Out-Null
    $p = Join-Path $wf "rounds.pending-$stamp-$([guid]::NewGuid().ToString('N').Substring(0, 8)).json"
    [IO.File]::WriteAllText($p, $Json, $utf8)
    [Console]::Error.WriteLine("round-cap: $Why; events parked in $p")
}

# One records.py ledger add: INSERT OR IGNORE, so parallel gates stopping at once, or a repeated event, count once.
function Save-Events([object[]]$events) {
    $json = '[' + (@($events | ForEach-Object { ConvertTo-Json -Compress -InputObject ([ordered]@{ key = [string]$_.key; counter = [string]$_.counter; id = [string]$_.id }) }) -join ',') + ']'
    try { $rr = Get-RecordsRoot } catch { Save-Pending $root $json "the ledger's checkout cannot be found ($($_.Exception.Message))"; return }
    $r = Invoke-Records $rr @('ledger', 'add', '--json') 15000 $json
    if ($r.State -eq 'Ok') {
        if ($r.Err) { [Console]::Error.WriteLine("round-cap: $($r.Err)") }  # an unreadable ledger.db moved aside
        return
    }
    $why = if ($r.State -eq 'NoPython') { 'no Python 3.10+ with SQLite FTS5 found' } elseif ($r.Code -eq 75) { 'ledger busy' } else { "records.py ledger add failed: $($r.Err)" }
    Save-Pending $rr $json $why
}

function New-Counter([string]$name, [int]$fileUsed, [int]$cap, [int]$default, [string]$record, [int]$logged) {
    $note = ''
    if ($cap -gt $default -and $record -notmatch '(?i)extra round') {
        $note = " (cap $cap has no recorded main GD extra round; default $default applies)"
        $cap = $default
    }
    if ($logged) { $note += " (file $fileUsed + hook $logged)" }
    $stopped = $record -match "(?im)^- Stop rule:.*\b$name\b"
    return [pscustomobject]@{ Name = $name; Used = $fileUsed + $logged; Cap = $cap; Note = $note; Stopped = $stopped }
}

# The registry's counters of a slug, or $null when the registry cannot hold it: no or an empty features.jsonl (Python
# never starts), or a name records.py refuses. Throws the cause and its fix when the CLI cannot answer.
function Get-RegistryCounters([string]$slug) {
    if ($slug -cnotmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$' -or $slug.Length -gt 100) { return $null }
    $rr = Get-RecordsRoot
    $journal = Join-Path $rr '.workflow/features.jsonl'
    if (-not (Test-Path -LiteralPath $journal -PathType Leaf) -or (Get-Item -LiteralPath $journal).Length -eq 0) { return $null }
    $r = Invoke-Records $rr @('feature', 'counters', $slug, '--json')
    if ($r.State -eq 'NoPython') { throw 'no Python 3.10+ with SQLite FTS5 found. Install it, then retry (skill records).' }
    if ($r.State -ne 'Ok') { throw "records.py feature counters $slug failed: $($r.Err). Clear that cause, then retry (skill records)." }
    $j = $null
    try { $j = $r.Out | ConvertFrom-Json -ErrorAction Stop } catch {}
    # A shape this hook does not know must not read as 0 rounds.
    if (-not (Test-JsonObject $j) -or $j.found -isnot [bool] -or $j.open -isnot [bool] -or $null -eq $j.review.used -or $null -eq $j.review.cap -or
        $null -eq $j.qa.used -or $null -eq $j.qa.cap -or $null -eq $j.rework.used -or $null -eq $j.rework.cap) {
        throw "records.py feature counters $slug $UnreadableOutput"
    }
    return $j
}

# Counters of an open feature, or @(). Each carries its Source: 'registry' (records.py); 'md', an un-migrated feature file's
# header (- Status:, - Rounds:, Main GD decisions, - Stop rule:) for a slug the registry does not hold; 'none', a feature
# file with no such header and no registry record: default caps. No registry record and no file: @().
function Get-FeatureCounters([string]$slug, $ledger) {
    $reg = Get-RegistryCounters $slug
    $out = @()
    if ($reg -and $reg.found) {
        if (-not $reg.open) { return @() }
        $size = First $reg.size 'M'
        foreach ($name in 'review', 'qa', 'rework') {
            $default = if ($name -eq 'rework') { First $Defaults["rework-$size"] $Defaults['rework-M'] } else { $Defaults[$name] }
            $c = New-Counter $name ([int]$reg.$name.used) ([int]$reg.$name.cap) $default ([string]$reg.record) (Get-LedgerCount $ledger "feature:$slug" $name)
            $out += $c | Add-Member -PassThru NoteProperty Source 'registry' | Add-Member -PassThru NoteProperty Slug $slug
        }
        return $out
    }
    $path = Join-Path $root ".workflow/features/$slug.md"
    if (-not (Test-Path -LiteralPath $path)) { return @() }
    $text = Get-Content -LiteralPath $path -Raw -Encoding UTF8
    $legacy = $text -match '(?m)^- (Status|Rounds):'
    if ($legacy -and $text -notmatch '(?m)^- Status:\s*Open') { return @() }
    $line = if ($legacy -and $text -match '(?m)^- Rounds:(.*)$') { $Matches[1] } else { '' }
    $size = if ($legacy -and $text -match '(?m)^- Size:\s*(S|M|L)\b') { $Matches[1] } else { 'M' }
    $record = ''
    if ($legacy) {
        # Every decisions section counts, old heading or new: a game repo's open file may hold both (BUG-0012).
        $gd = (@([regex]::Matches($text, '(?s)## (?:Main )?GD decisions(.*?)(?=\r?\n## |$)') | ForEach-Object { $_.Groups[1].Value })) -join "`n"
        $stop = (([regex]::Matches($text, '(?m)^- Stop rule:.*$') | ForEach-Object { $_.Value }) -join "`n")
        $record = "$gd`n$stop"
    }
    $source = if ($legacy) { 'md' } else { 'none' }
    foreach ($name in 'review', 'qa', 'rework') {
        $default = if ($name -eq 'rework') { First $Defaults["rework-$size"] $Defaults['rework-M'] } else { $Defaults[$name] }
        $used = 0; $cap = $default
        if ($line -match "(?i)\b$name\s*:?\s*(\d+)\s*/\s*(\d+)") { $used = [int]$Matches[1]; $cap = [int]$Matches[2] }
        $c = New-Counter $name $used $cap $default $record (Get-LedgerCount $ledger "feature:$slug" $name)
        $out += $c | Add-Member -PassThru NoteProperty Source $source | Add-Member -PassThru NoteProperty Slug $slug
    }
    return $out
}

# Counters of one unsettled bug from bugs.py, or @() when it is settled or unknown. Throws the cause and its fix when
# the CLI cannot answer. No journal: no bugs yet, and Python never starts.
$script:BugsRoot = $null  # resolved once, and only for a brief that names a bug
function Get-BugCounters([string]$id, $ledger) {
    if (-not $script:BugsRoot) { $script:BugsRoot = Get-BugsRoot $root }
    if (-not (Test-Path -LiteralPath (Join-Path $script:BugsRoot '.workflow/bugs.jsonl'))) { return @() }
    $r = Invoke-Bugs $script:BugsRoot @('counters', $id, '--json')
    if ($r.State -eq 'NoPython') { throw "no Python 3.10+ with SQLite FTS5 found. Install it, then retry (skill bugs)." }
    if ($r.State -ne 'Ok') { throw "bugs.py counters $id failed: $($r.Err). Clear that cause, then retry (skill bugs)." }
    $j = $null
    try { $j = $r.Out | ConvertFrom-Json -ErrorAction Stop } catch {}
    # A shape this hook does not know must not read as 0 rounds.
    if ($null -eq $j -or $j.found -isnot [bool] -or $j.settled -isnot [bool] -or $null -eq $j.fix.used -or $null -eq $j.fix.cap -or $null -eq $j.review.used -or $null -eq $j.review.cap) {
        throw "bugs.py counters $id returned unreadable output. Run it by hand to see why, then retry (skill bugs)."
    }
    if (-not $j.found -or $j.settled) { return @() }
    $out = @()
    foreach ($name in 'fix', 'review') {
        $out += New-Counter $name ([int]$j.$name.used) ([int]$j.$name.cap) $Defaults[$name] ([string]$j.record) (Get-LedgerCount $ledger "bug:$id" $name)
    }
    return $out
}

# Target or session work: ledger only, extra rounds as "extra-<counter>" entries.
function Get-KeyCounters([string]$key, $ledger) {
    foreach ($name in 'review', 'qa') {
        $extra = Get-LedgerCount $ledger $key "extra-$name"
        [pscustomobject]@{ Name = $name; Used = (Get-LedgerCount $ledger $key $name); Cap = $Defaults[$name] + $extra; Note = ''; Stopped = $false }
    }
}

function Get-Marker([string]$text, [string]$name) { if ($text -match "(?im)^[\s*_>-]*$name[*_]*:[*_\s]*(\S[^\r\n]*?)\s*$") { return $Matches[1] }; return $null }
function Get-FeatureMarker([string]$text) {
    $v = Get-Marker $text 'Feature'
    if ($v -and $v -match '\.workflow[\\/]features[\\/]([A-Za-z0-9_-]+)\.md') { return $Matches[1] }
    return $null
}
# One spelling for a matched BUG-<digits>: BUG- plus at least 4 digits, no leading zeros beyond that. The CLI call and the
# ledger key both use it, so a marker, free text, Verify and Repro all reach the same counters.
function ConvertTo-BugId([string]$Text) { return 'BUG-' + $Text.Substring(4).TrimStart('0').PadLeft(4, '0') }
function Get-BugMarker([string]$text) { $v = Get-Marker $text 'Bug'; if ($v -and $v -match '(?i)^(BUG-[0-9]+)\b') { return (ConvertTo-BugId $Matches[1]) }; return $null }
function Get-TargetKey([string]$text) { $v = Get-Marker $text 'Target'; if ($v) { return 'target:' + ($v -replace '\\', '/').ToLowerInvariant() }; return $null }
function Get-VerifyIds([string]$text) { @([regex]::Matches($text, '(?im)^[\s*_>-]*Verify[*_]*:[*_\s]*(BUG-[0-9]+)\b') | ForEach-Object { ConvertTo-BugId $_.Groups[1].Value } | Select-Object -Unique) }
function Get-Slugs([string]$text) { [regex]::Matches($text, '\.workflow[\\/]features[\\/]([A-Za-z0-9_-]+)\.md') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique }
function Get-BugIds([string]$text) { [regex]::Matches($text, '\bBUG-[0-9]+\b', 'IgnoreCase') | ForEach-Object { ConvertTo-BugId $_.Value } | Select-Object -Unique }
# The feature slugs a records.py command acts on: "feature <command> <slug>" and "--feature <slug>".
function Get-CommandSlugs([string]$text) {
    $a = [regex]::Matches($text, '\bfeature\s+(?:round|extra-round|stop-rule|update|set-state|show|counters)\s+["'']?([a-z0-9]+(?:-[a-z0-9]+)*)(?![A-Za-z0-9_-])')
    $b = [regex]::Matches($text, '--feature(?:\s+|=)["'']?([a-z0-9]+(?:-[a-z0-9]+)*)(?![A-Za-z0-9_-])')
    @(@($a) + @($b) | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique)
}
function Format([string]$what, $c) { return "${what}: $($c.Name) $($c.Used)/$($c.Cap)$($c.Note)" }

if ($Mode -eq 'count') {
    $agent = [string]$in.agent_type
    $agentId = [string](First $in.agent_id ([guid]::NewGuid().ToString('N')))
    $exchange = Read-SubagentExchange $in
    $brief = $exchange.Brief
    $ret = $exchange.Return
    $v = '(?im)^[\s*_>-]*Verdict[*_]*:[*_\s]*'
    # Only the marker lines /review writes count; a slug or skill name holding "audit" or "round 2" must not.
    # Mode: workflow - review-gate's gates: the main session records those rounds from the verified verdicts.
    $skip = $brief -match '(?im)^[\s*_>-]*Mode[*_]*:[*_\s]*(audit|test-code|workflow)\b'
    $codeFail = $agent -eq 'code-reviewer' -and ($ret -match "${v}Request changes" -or
        ($ret -match "${v}Needs-decision" -and $ret -match '(?i)\bSeverity[*_`]*:[*_`\s]*(Critical|High|Medium)\b'))
    $reviewFail = -not $skip -and ($codeFail -or ($agent -eq 'security-reviewer' -and $ret -match "${v}Blocked"))
    $qaFail = $agent -eq 'qa-lead' -and $ret -match "${v}Not signed off"
    $verifyIds = @(Get-VerifyIds $brief)
    $repros = @([regex]::Matches($ret, '(?im)^[\s*_>-]*Repro[*_]*:[*_\s]*(BUG-[0-9]+)\s+reproduces') |
        ForEach-Object { ConvertTo-BugId $_.Groups[1].Value } | Select-Object -Unique | Where-Object { $verifyIds -contains $_ })
    if (-not ($reviewFail -or $qaFail -or $repros.Count)) { exit 0 }
    # code-reviewer and security-reviewer failing the same round count once: same Round number on the same Tree.
    # The Tree keeps a repeated number (a resumed session restarting at 1) on new code from merging into an old event.
    $tree = if ($brief -match '(?im)^[\s*_>-]*Tree[*_]*:[*_`\s]*([0-9a-f]{7,64})\b') { "-$($Matches[1].Substring(0, [Math]::Min(12, $Matches[1].Length)))" } else { '' }
    $round = if ($brief -match '(?im)^[\s*_>-]*Round[*_]*:[*_\s]*(\d+)') { "round-$($Matches[1])$tree" } else { $agentId }
    $slug = Get-FeatureMarker $brief; $bug = Get-BugMarker $brief; $tkey = Get-TargetKey $brief
    $events = New-Object System.Collections.Generic.List[object]
    function E([string]$k, [string]$c, [string]$i) { $events.Add([pscustomobject]@{ key = $k; counter = $c; id = $i }) }
    if ($reviewFail) {
        if ($slug) { E "feature:$slug" 'review' $round; E "feature:$slug" 'rework' "review-$round" }
        elseif ($bug) { E "bug:$bug" 'review' $round }
        elseif ($tkey) { E $tkey 'review' $round }
        else { E $sessionKey 'review' $round }
    }
    if ($qaFail) {
        if ($slug) { E "feature:$slug" 'qa' $agentId; E "feature:$slug" 'rework' "qa-$agentId" }
        elseif ($tkey) { E $tkey 'qa' $agentId }
        else { E $sessionKey 'qa' $agentId }
    }
    # One verification run counts once per bug and once for the feature, however many bugs still reproduce.
    foreach ($b in $repros) { E "bug:$b" 'fix' "verify-$agentId" }
    if ($repros.Count -and $slug) { E "feature:$slug" 'rework' "verify-$agentId" }
    Save-Events $events.ToArray()
    exit 0
}

# Runs for every shell command the settings filter lets through: no Python and no ledger before this test.
$shellIds = @()
$shellSlugs = @()
if ($Mode -eq 'edit' -and 'Bash', 'PowerShell' -contains [string]$in.tool_name) {
    $command = [string]$in.tool_input.command
    $callsBugs = $command -match '(?i)\bbugs\.py\b'
    $callsRecords = $command -match '(?i)\brecords\.py\b'
    if (-not ($callsBugs -or $callsRecords)) { exit 0 }
    if ($callsBugs) { $shellIds = @(Get-BugIds $command) }
    if ($callsRecords) { $shellSlugs = @(Get-CommandSlugs $command) }
    if (-not ($shellIds.Count -or $shellSlugs.Count)) { exit 0 }
}

if ($Mode -eq 'dispatch') {
    # A moved-aside ledger holds counts the live one lacks: caps cannot be trusted until the main GD resolves it.
    $marks = @(Get-LedgerMarks)
    if ($marks.Count) {
        Block ("round-cap: $($marks.Count) unreadable ledger file(s) in .workflow/ ($(($marks | ForEach-Object Name) -join ', ')) hold " +
            'round counts the live ledger lacks; caps cannot be checked. Report to the main GD: merge their events into .workflow/ledger.db by hand (records.py ledger add --json, skill records), or delete them on the main GD''s order.')
    }
    $tool = [string]$in.tool_name
    if ($tool -eq 'Workflow') {
        $a = $in.tool_input.args
        if ($a -is [string]) { try { $a = $a | ConvertFrom-Json -ErrorAction Stop } catch { $a = $null } }
        $brief = ''
        if ($a -and $a.feature) { $brief += "Feature: $($a.feature)`n" }
        if ($a -and $a.bug) { $brief += "Bug: $($a.bug)`n" }
        if ($a -and $a.target) { $brief += "Target: $($a.target)`n" }
        if (-not $brief) { exit 0 }
        $agent = 'code-reviewer'
    } else {
        $brief = [string](First $in.tool_input.prompt '')
        $agent = [string]$in.tool_input.subagent_type
    }
    $slug = Get-FeatureMarker $brief; $bug = Get-BugMarker $brief; $tkey = Get-TargetKey $brief
    $marked = $slug -or $bug -or $tkey
    $slugs = @(if ($slug) { $slug } elseif (-not $marked) { Get-Slugs $brief })
    $bugs = @(if ($bug) { $bug } elseif (-not $marked) { Get-BugIds $brief })
    $over = @()
    foreach ($s in $slugs) {
        try { $counters = @(Get-FeatureCounters $s $null) }
        catch { Block "round-cap: the brief names feature $s but its round caps cannot be checked: $($_.Exception.Message)" }
        foreach ($c in $counters) { if ($c.Used -gt $c.Cap) { $over += Format "feature $s" $c } }
    }
    foreach ($b in $bugs) {
        try { $counters = @(Get-BugCounters $b $null) }
        catch { Block "round-cap: the brief names $b but its round caps cannot be checked: $($_.Exception.Message)" }
        foreach ($c in $counters) { if ($c.Used -gt $c.Cap) { $over += Format $b $c } }
    }
    if ($tkey) {
        try { $counters = @(Get-KeyCounters $tkey $null) }
        catch { Block "round-cap: the brief names $tkey but its round caps cannot be checked: $($_.Exception.Message)" }
        foreach ($c in $counters) { if ($c.Used -gt $c.Cap) { $over += Format $tkey $c } }
    }
    if (-not $marked -and -not $slugs.Count -and -not $bugs.Count -and $Gates -contains $agent) {
        try { $counters = @(Get-KeyCounters $sessionKey $null) }
        catch { Block "round-cap: a $agent dispatch is capped per session, but its round caps cannot be checked: $($_.Exception.Message)" }
        foreach ($c in $counters) { if ($c.Used -gt $c.Cap) { $over += Format 'this session (no feature, bug or target named)' $c } }
    }
    if ($over.Count) {
        Block ("Stop rule (routing.md): past the round cap - $($over -join '; '). " +
            'Report to the main GD: what was tried, last verified state, next best action. ' +
            'Another round only on the main GD''s order: for a feature, run records.py feature extra-round <slug> <counter> +n --note <the order> --by "main GD" (skill records; ' +
            'a feature file not yet migrated: record "extra round: <counter> +n" under Main GD decisions and raise that cap); ' +
            'for a bug, run bugs.py extra-round <id> <counter> +n --note <the order> (skill bugs); ' +
            'for target or session work run records.py ledger add --json with one {"key": "<target:path or session:id>", "counter": "extra-<counter>", "id": "<the order>"} per round.')
    }
    exit 0
}

# edit. Exit 2 here only hands Claude the message: the tool has already run. A busy ledger stays silent, as a lock always has.
$msg = @()
$hits = @()
$unread = @()
function Get-Hits([string]$What, [scriptblock]$Read) {
    try { foreach ($c in (& $Read)) { if ($c.Used -ge $c.Cap) { $c | Add-Member -PassThru NoteProperty What $What } } }
    catch { if (-not $script:LedgerBusy) { $script:unread += "round-cap: the round caps of $What could not be read: $($_.Exception.Message)" } }
}
if ($shellIds.Count -or $shellSlugs.Count) {
    $hits = @(foreach ($id in $shellIds) { Get-Hits $id { Get-BugCounters $id $null } }) +
        @(foreach ($s in $shellSlugs) { Get-Hits "feature $s" { Get-FeatureCounters $s $null } })
}
else {
    $path = [string](First $in.tool_input.file_path '')
    if ($path -notmatch '[\\/]\.workflow[\\/]') { exit 0 }
    if ($path -match '[\\/]features[\\/]([A-Za-z0-9_-]+)\.md$') {
        $slug = $Matches[1]
        $counters = @()
        try { $counters = @(Get-FeatureCounters $slug $null) }
        catch { if (-not $script:LedgerBusy) { $unread += "round-cap: the round caps of feature $slug could not be read: $($_.Exception.Message)" } }
        if ($counters.Count -and $counters[0].Source -eq 'md' -and (Get-Content -LiteralPath $path -Raw -Encoding UTF8) -notmatch '(?m)^- Rounds:') {
            $msg += "feature ${slug}: no '- Rounds:' line (template in /feature); default caps apply."
        }
        if ($counters.Count -and $counters[0].Source -eq 'none') {
            $msg += "feature ${slug}: not in the feature registry (records.py feature add, skill records); default caps apply."
        }
        $hits = foreach ($c in $counters) { if ($c.Used -ge $c.Cap) { $c | Add-Member -PassThru NoteProperty What "feature $slug" } }
    }
}
foreach ($c in @($hits | Where-Object { $_ })) {
    $line = Format $c.What $c
    if ($c.Used -gt $c.Cap) { $msg += "$line - past the cap: stop and report to the main GD." }
    elseif (-not $c.Stopped) {
        $record = if ($c.What -match '^BUG-') { "run bugs.py stop-rule $($c.What) $($c.Name) --extra-dispatch unused" }
        elseif ($c.Source -eq 'md') { "record '- Stop rule:'" }
        else { "run records.py feature stop-rule $($c.Slug) $($c.Name) --extra-dispatch unused" }
        $msg += "$line - at the cap: technical-architect root-causes once ($record), the owner gets one more dispatch; another failure stops the work."
    }
}
if ($msg.Count) { $unread += "Stop rule (routing.md):`n" + ($msg -join "`n") }
if (-not $unread.Count) { exit 0 }
Block ($unread -join "`n")
