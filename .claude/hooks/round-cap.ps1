# Round caps of the stop rule (routing.md).
#   count     SubagentStop: a failed gate, a Failed return or "Repro: BUG-#### reproduces" adds a round to the ledger .workflow/rounds.json,
#             keyed by the feature files and bugs the brief names, else by session (gates only).
#   dispatch  PreToolUse Agent: blocked when the brief names an open feature or bug past a cap;
#             with no feature or bug named, a gate agent is blocked past the session's cap.
#   edit      PostToolUse Edit/Write under .workflow/: tells Claude when a counter reaches or passes its cap,
#             or an open feature file has no Rounds line.
# Counters are failed rounds: "- Rounds: review n/cap, QA n/cap, rework n/cap" in a feature file,
# "- Fix rounds: n/cap" in a bugs.md record; a missing line means 0 at the default cap. Used = the
# larger of the file and the ledger, so a counter the main session forgot still counts. A cap above
# the default counts only with an "extra round" line in the feature's GD decisions or the bug's record;
# for session work, one "extra-<counter>" entry in the ledger per extra round.
param([Parameter(Mandatory)][ValidateSet('count', 'dispatch', 'edit')][string]$Mode)
. "$PSScriptRoot/common.ps1"

$Defaults = @{ review = 3; qa = 2; fix = 2; 'rework-M' = 6; 'rework-L' = 8 }
$Gates = 'code-reviewer', 'security-reviewer', 'qa-lead'

$in = Read-HookInput
if (-not $in) { exit 0 }
$root = Get-ProjectRoot $in
$bugsPath = Join-Path $root '.workflow/bugs.md'
$ledgerPath = Join-Path $root '.workflow/rounds.json'
$sessionKey = "session:$([string]$in.session_id)"

# Ledger: { key: { counter: [event ids] } }. Unreadable -> empty: the state files still count.
function ConvertTo-Ledger([string]$raw) {
    $l = @{}
    if ([string]::IsNullOrWhiteSpace($raw)) { return $l }
    try {
        $o = $raw | ConvertFrom-Json
        foreach ($k in $o.PSObject.Properties) {
            $l[$k.Name] = @{}
            foreach ($c in $k.Value.PSObject.Properties) { $l[$k.Name][$c.Name] = @($c.Value) }
        }
    } catch {}
    return $l
}

function Get-Ledger {
    if (-not (Test-Path $ledgerPath)) { return @{} }
    try { return ConvertTo-Ledger ([IO.File]::ReadAllText($ledgerPath)) } catch { return @{} }
}

# Read-modify-write under an exclusive handle: parallel gates stop at the same time.
function Update-Ledger([scriptblock]$Change) {
    New-Item -ItemType Directory -Force (Split-Path $ledgerPath) | Out-Null
    $fs = $null
    for ($i = 0; $i -lt 50 -and -not $fs; $i++) {
        try { $fs = [IO.File]::Open($ledgerPath, 'OpenOrCreate', 'ReadWrite', 'None') } catch { Start-Sleep -Milliseconds 100 }
    }
    if (-not $fs) { return }
    try {
        $sr = New-Object IO.StreamReader($fs, (New-Object Text.UTF8Encoding $false), $true, 4096, $true)
        $l = ConvertTo-Ledger $sr.ReadToEnd()
        & $Change $l
        $bytes = (New-Object Text.UTF8Encoding $false).GetBytes(($l | ConvertTo-Json -Depth 5))
        $fs.SetLength(0)
        $fs.Write($bytes, 0, $bytes.Length)
    } finally { $fs.Dispose() }
}

function Get-LedgerCount($ledger, [string]$key, [string]$counter) {
    if (-not $ledger.ContainsKey($key) -or -not $ledger[$key].ContainsKey($counter)) { return 0 }
    return @($ledger[$key][$counter]).Count
}

function New-Counter([string]$name, [int]$used, [int]$cap, [int]$default, [string]$record, [int]$logged) {
    $note = ''
    if ($cap -gt $default -and $record -notmatch '(?i)extra round') {
        $note = " (cap $cap has no recorded GD extra round; default $default applies)"
        $cap = $default
    }
    if ($logged -gt $used) { $note += " (ledger counted $logged, file says $used)"; $used = $logged }
    return [pscustomobject]@{ Name = $name; Used = $used; Cap = $cap; Note = $note }
}

# Counters of an open feature file, or @(). Missing counters start at 0 with the default cap.
function Get-FeatureCounters([string]$slug, $ledger) {
    $path = Join-Path $root ".workflow/features/$slug.md"
    if (-not (Test-Path $path)) { return @() }
    $text = Get-Content $path -Raw -Encoding UTF8
    if ($text -notmatch '(?m)^- Status:\s*Open') { return @() }
    $line = if ($text -match '(?m)^- Rounds:(.*)$') { $Matches[1] } else { '' }
    $size = if ($text -match '(?m)^- Size:\s*(S|M|L)\b') { $Matches[1] } else { 'M' }
    $gd = if ($text -match '(?s)## GD decisions(.*?)(\r?\n## |$)') { $Matches[1] } else { '' }
    $out = @()
    foreach ($name in 'review', 'qa', 'rework') {
        $default = if ($name -eq 'rework') { First $Defaults["rework-$size"] $Defaults['rework-M'] } else { $Defaults[$name] }
        $used = 0; $cap = $default
        if ($line -match "(?i)\b$name\s*:?\s*(\d+)\s*/\s*(\d+)") { $used = [int]$Matches[1]; $cap = [int]$Matches[2] }
        $out += New-Counter $name $used $cap $default $gd (Get-LedgerCount $ledger "feature:$slug" $name)
    }
    return $out
}

# Counter of one open bug in bugs.md, or @().
function Get-BugCounters([string]$id, $ledger) {
    if (-not (Test-Path $bugsPath)) { return @() }
    $text = Get-Content $bugsPath -Raw -Encoding UTF8
    if ($text -match "(?m)^\|\s*$id\s*\|[^\n]*\|\s*(Closed|Won't fix)\s*\|") { return @() }
    if ($text -notmatch "(?s)\r?\n## $id\b(.*?)(\r?\n## |$)") { return @() }
    $record = $Matches[1]
    $used = 0; $cap = $Defaults.fix
    if ($record -match '(?m)^- Fix rounds:\s*(\d+)\s*/\s*(\d+)') { $used = [int]$Matches[1]; $cap = [int]$Matches[2] }
    return @(New-Counter 'fix' $used $cap $Defaults.fix $record (Get-LedgerCount $ledger "bug:$id" 'fix'))
}

function Get-SessionCounters($ledger) {
    foreach ($name in 'review', 'qa') {
        $extra = Get-LedgerCount $ledger $sessionKey "extra-$name"
        [pscustomobject]@{ Name = $name; Used = (Get-LedgerCount $ledger $sessionKey $name); Cap = $Defaults[$name] + $extra; Note = '' }
    }
}

function Get-Slugs([string]$text) { [regex]::Matches($text, '\.workflow[\\/]features[\\/]([A-Za-z0-9_-]+)\.md') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique }
function Get-BugIds([string]$text) { [regex]::Matches($text, '\bBUG-\d{4,}\b') | ForEach-Object { $_.Value } | Select-Object -Unique }
function Format([string]$what, $c) { return "${what}: $($c.Name) $($c.Used)/$($c.Cap)$($c.Note)" }

if ($Mode -eq 'count') {
    $agent = [string]$in.agent_type
    $agentId = [string](First $in.agent_id ([guid]::NewGuid().ToString('N')))
    $brief = ''
    $ret = [string](First $in.last_assistant_message '')
    $tp = [string]$in.agent_transcript_path
    if ($tp -and (Test-Path $tp)) {
        $lines = @(Get-Content $tp -Encoding UTF8)
        foreach ($l in $lines) {
            try { $o = $l | ConvertFrom-Json } catch { continue }
            if ($o.type -ne 'user') { continue }
            $c = $o.message.content
            $brief = if ($c -is [string]) { $c } else { (@($c) | Where-Object { $_.type -eq 'text' } | ForEach-Object { $_.text }) -join "`n" }
            break
        }
        # The report may arrive through the SubagentHandback tool instead of the closing text.
        for ($i = $lines.Count - 1; $i -ge 0; $i--) {
            if ($lines[$i] -notmatch 'SubagentHandback') { continue }
            try { $o = $lines[$i] | ConvertFrom-Json } catch { continue }
            $h = @($o.message.content) | Where-Object { $_.type -eq 'tool_use' -and $_.name -eq 'SubagentHandback' } | Select-Object -Last 1
            if ($h) { $ret = [string]$h.input.message + "`n" + $ret; break }
        }
    }
    $v = '(?im)^[\s*_>-]*Verdict[*_]*:[*_\s]*'
    $audit = $brief -match '(?i)\baudit\b'
    $reviewFail = -not $audit -and (($agent -eq 'code-reviewer' -and $ret -match "${v}Request changes") -or ($agent -eq 'security-reviewer' -and $ret -match "${v}Blocked"))
    $qaFail = $agent -eq 'qa-lead' -and $ret -match "${v}Not signed off"
    $failed = $ret -match '(?im)^[\s*_>-]*Status[*_]*:[*_\s]*Failed'
    $repros = @([regex]::Matches($ret, '(?im)^[\s*_>-]*Repro[*_]*:[*_\s]*(BUG-\d{4,})\s+reproduces') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique)
    if (-not ($reviewFail -or $qaFail -or $failed -or $repros.Count)) { exit 0 }
    # code-reviewer and security-reviewer blocking the same round count once.
    $round = if ($brief -match '(?i)\bround\s*(\d+)') { "round-$($Matches[1])" } else { $agentId }
    $slugs = @(Get-Slugs $brief); $bugs = @(Get-BugIds $brief)
    Update-Ledger {
        param($l)
        function Add([string]$key, [string]$counter, [string]$id) {
            if (-not $l.ContainsKey($key)) { $l[$key] = @{} }
            if (-not $l[$key].ContainsKey($counter)) { $l[$key][$counter] = @() }
            if (@($l[$key][$counter]) -notcontains $id) { $l[$key][$counter] = @($l[$key][$counter]) + $id }
        }
        foreach ($s in $slugs) {
            if ($reviewFail) { Add "feature:$s" 'review' $round; Add "feature:$s" 'rework' "review-$round" }
            if ($qaFail) { Add "feature:$s" 'qa' $agentId; Add "feature:$s" 'rework' "qa-$agentId" }
            # One failed run counts once, whether it says Failed, a bug still reproduces, or both.
            if ($failed -or $repros.Count) { Add "feature:$s" 'rework' "run-$agentId" }
        }
        foreach ($b in $bugs) {
            if ($reviewFail) { Add "bug:$b" 'fix' "review-$round" }
            if ($failed) { Add "bug:$b" 'fix' "run-$agentId" }
        }
        foreach ($b in $repros) { Add "bug:$b" 'fix' "run-$agentId" }
        if (-not $slugs.Count -and -not $bugs.Count) {
            if ($reviewFail) { Add $sessionKey 'review' $round }
            if ($qaFail) { Add $sessionKey 'qa' $agentId }
        }
    }.GetNewClosure()
    exit 0
}

$ledger = Get-Ledger

if ($Mode -eq 'dispatch') {
    $brief = [string](First $in.tool_input.prompt '')
    $agent = [string]$in.tool_input.subagent_type
    $slugs = @(Get-Slugs $brief); $bugs = @(Get-BugIds $brief)
    $over = @()
    foreach ($s in $slugs) { foreach ($c in Get-FeatureCounters $s $ledger) { if ($c.Used -gt $c.Cap) { $over += Format "feature $s" $c } } }
    foreach ($b in $bugs) { foreach ($c in Get-BugCounters $b $ledger) { if ($c.Used -gt $c.Cap) { $over += Format $b $c } } }
    if (-not $slugs.Count -and -not $bugs.Count -and $Gates -contains $agent) {
        foreach ($c in Get-SessionCounters $ledger) { if ($c.Used -gt $c.Cap) { $over += Format 'this session (no feature or bug named)' $c } }
    }
    if ($over.Count) {
        Block ("Stop rule (routing.md): past the round cap - $($over -join '; '). " +
            'Report to the GD: what was tried, last verified state, next best action. ' +
            'Another round only on the GD''s order: record "extra round: <counter> +n" under GD decisions (or in the bug record) and raise that cap; ' +
            "for session work add one `"extra-<counter>`" entry under `"$sessionKey`" in .workflow/rounds.json per round.")
    }
    exit 0
}

# edit
$path = [string](First $in.tool_input.file_path '')
if ($path -notmatch '[\\/]\.workflow[\\/]') { exit 0 }
$msg = @()
if ($path -match '[\\/]features[\\/]([A-Za-z0-9_-]+)\.md$') {
    $slug = $Matches[1]
    $counters = @(Get-FeatureCounters $slug $ledger)
    if ($counters.Count -and (Get-Content $path -Raw -Encoding UTF8) -notmatch '(?m)^- Rounds:') {
        $msg += "feature ${slug}: no '- Rounds:' line (template in /feature); default caps apply."
    }
    $hits = foreach ($c in $counters) { if ($c.Used -ge $c.Cap) { $c | Add-Member -PassThru NoteProperty What "feature $slug" } }
}
elseif ($path -match '[\\/]bugs\.md$' -and (Test-Path $path)) {
    $text = Get-Content $path -Raw -Encoding UTF8
    $hits = foreach ($id in [regex]::Matches($text, '(?m)^## (BUG-\d{4,})') | ForEach-Object { $_.Groups[1].Value }) {
        foreach ($c in Get-BugCounters $id $ledger) { if ($c.Used -ge $c.Cap) { $c | Add-Member -PassThru NoteProperty What $id } }
    }
}
foreach ($c in @($hits | Where-Object { $_ })) {
    $line = Format $c.What $c
    if ($c.Used -gt $c.Cap) { $msg += "$line - past the cap: stop and report to the GD." }
    else { $msg += "$line - at the cap: technical-architect root-causes once, the owner gets one more dispatch; another failure stops the work." }
}
if (-not $msg.Count) { exit 0 }
Block ("Stop rule (routing.md):`n" + ($msg -join "`n"))
