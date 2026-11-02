# Round caps of the stop rule (routing.md). Brief marker lines: /review, /fix and /qa write them.
#   count     SubagentStop: adds a failed round to the ledger .workflow/rounds.json when
#             - a review gate fails (code-reviewer Request changes, or Needs-decision with a Critical/High/Medium
#               finding; security-reviewer Blocked), unless the brief says "Mode: audit", "Mode: test-code" or
#               "Mode: workflow" (review-gate's gates: the main session records those rounds itself);
#             - qa-lead returns Not signed off;
#             - a brief with "Verify: BUG-####" returns "Repro: BUG-#### reproduces".
#             Charged only to the brief's "Feature:" line, else its "Bug:" line, else its "Target:" line, else the
#             session. Failed returns are attempts, not rounds: never counted here.
#   dispatch  PreToolUse Agent / Workflow: blocked when the brief's (or the workflow args') feature, bug or target
#             is past a cap. A brief without marker lines falls back to every feature path and bug id it mentions.
#   edit      PostToolUse Edit/Write under .workflow/: tells Claude when a counter reaches or passes its cap (silent
#             at the cap once a "- Stop rule:" line names that counter), or an open feature file has no Rounds line.
# Counters: "- Rounds: review n/cap, QA n/cap, rework n/cap" in a feature file; "- Fix rounds: n/cap" and
# "- Review rounds: n/cap" in a bugs.md record. The files hold only events this hook cannot see; Used = file + ledger.
# A cap above the default counts only with an "extra round" line in the feature's GD decisions or the bug's record;
# for target or session work, one "extra-<counter>" entry in the ledger per extra round.
# Ledger safety: an unparsable ledger is moved to rounds.corrupt-<utc>.json (never overwritten); a lock timeout
# parks the events in rounds.pending-<id>.json, merged on the next write; dispatch fails closed on an unreadable ledger.
param([Parameter(Mandatory)][ValidateSet('count', 'dispatch', 'edit')][string]$Mode)
. "$PSScriptRoot/common.ps1"

$Defaults = @{ review = 3; qa = 2; fix = 2; 'rework-M' = 6; 'rework-L' = 8 }
$Gates = 'code-reviewer', 'security-reviewer', 'qa-lead'
$Settled = "Closed|Won't fix|Accepted|As designed|Duplicate[^|]*"

$in = Read-HookInput
if (-not $in) { exit 0 }
$root = Get-ProjectRoot $in
$bugsPath = Join-Path $root '.workflow/bugs.md'
$ledgerPath = Join-Path $root '.workflow/rounds.json'
$ledgerDir = Split-Path $ledgerPath
$sessionKey = "session:$([string]$in.session_id)"
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfff')

# Ledger: { key: { counter: [event ids] } }. Throws on invalid JSON.
function ConvertTo-Ledger([string]$raw) {
    $l = @{}
    if ([string]::IsNullOrWhiteSpace($raw)) { return $l }
    $o = $raw | ConvertFrom-Json -ErrorAction Stop
    foreach ($k in $o.PSObject.Properties) {
        $l[$k.Name] = @{}
        foreach ($c in $k.Value.PSObject.Properties) { $l[$k.Name][$c.Name] = @($c.Value) }
    }
    return $l
}

function Add-Event($l, [string]$key, [string]$counter, [string]$id) {
    if (-not $l.ContainsKey($key)) { $l[$key] = @{} }
    if (-not $l[$key].ContainsKey($counter)) { $l[$key][$counter] = @() }
    if (@($l[$key][$counter]) -notcontains $id) { $l[$key][$counter] = @($l[$key][$counter]) + $id }
}

function Get-PendingFiles { if (Test-Path $ledgerDir) { @(Get-ChildItem $ledgerDir -Filter 'rounds.pending-*.json' -File) } else { @() } }

# Merges parked events into $l. An unparsable parked file is renamed rounds.corrupt-pending-*.json (kept, never
# deleted) and dropped from $files' merged set; the corrupt file then blocks dispatch until the GD resolves it.
function Merge-Pending($l, $files) {
    $merged = @()
    foreach ($f in $files) {
        try {
            foreach ($e in @([IO.File]::ReadAllText($f.FullName) | ConvertFrom-Json -ErrorAction Stop)) {
                Add-Event $l ([string]$e.key) ([string]$e.counter) ([string]$e.id)
            }
            $merged += $f
        } catch {
            try { Move-Item $f.FullName (Join-Path $ledgerDir ("rounds.corrupt-pending-" + $f.Name.Substring(15))) -Force -ErrorAction Stop } catch {}
        }
    }
    return $merged
}

function Get-CorruptFiles { if (Test-Path $ledgerDir) { @(Get-ChildItem $ledgerDir -Filter 'rounds.corrupt-*.json' -File) } else { @() } }

function Move-CorruptLedger {
    $dest = Join-Path $ledgerDir "rounds.corrupt-$stamp.json"
    try { Move-Item $ledgerPath $dest -Force -ErrorAction Stop; return $dest } catch { return $null }
}

# Read-only view: ledger + parked events. Sets $script:LedgerProblem to 'unreadable' or 'corrupt' and returns $null.
$script:LedgerProblem = $null
function Get-Ledger {
    $l = @{}
    if (Test-Path $ledgerPath) {
        $raw = $null
        for ($i = 0; $i -lt 5 -and $null -eq $raw; $i++) {
            try { $raw = [IO.File]::ReadAllText($ledgerPath) } catch { Start-Sleep -Milliseconds 100 }
        }
        if ($null -eq $raw) { $script:LedgerProblem = 'unreadable'; return $null }
        try { $l = ConvertTo-Ledger $raw } catch { $script:LedgerProblem = 'corrupt'; return $null }
    }
    $null = Merge-Pending $l (Get-PendingFiles)
    return $l
}

function Save-Pending([object[]]$events, [string]$why) {
    New-Item -ItemType Directory -Force $ledgerDir | Out-Null
    $p = Join-Path $ledgerDir "rounds.pending-$stamp-$([guid]::NewGuid().ToString('N').Substring(0, 8)).json"
    ConvertTo-Json -InputObject @($events) -Depth 4 | Set-Content $p -Encoding UTF8
    [Console]::Error.WriteLine("round-cap: $why; events parked in $p")
}

# Applies events under an exclusive handle: parallel gates stop at the same time.
function Save-Events([object[]]$events) {
    New-Item -ItemType Directory -Force $ledgerDir | Out-Null
    $fs = $null
    for ($i = 0; $i -lt 50 -and -not $fs; $i++) {
        try { $fs = [IO.File]::Open($ledgerPath, 'OpenOrCreate', 'ReadWrite', 'None') } catch { Start-Sleep -Milliseconds 100 }
    }
    if (-not $fs) { Save-Pending $events 'ledger locked'; return }
    $corrupt = $false
    $merged = @()
    $pending = @(Get-PendingFiles)
    try {
        $sr = New-Object IO.StreamReader($fs, (New-Object Text.UTF8Encoding $false), $true, 4096, $true)
        $l = $null
        try { $l = ConvertTo-Ledger $sr.ReadToEnd() } catch { $corrupt = $true }
        if (-not $corrupt) {
            $merged = @(Merge-Pending $l $pending)
            foreach ($e in $events) { Add-Event $l $e.key $e.counter $e.id }
            $bytes = (New-Object Text.UTF8Encoding $false).GetBytes(($l | ConvertTo-Json -Depth 5))
            $fs.SetLength(0)
            $fs.Write($bytes, 0, $bytes.Length)
        }
    } finally { $fs.Dispose() }
    if ($corrupt) {
        $dest = Move-CorruptLedger
        if (-not $dest) { Save-Pending $events 'ledger unparsable and could not be moved'; return }
        [Console]::Error.WriteLine("round-cap: unparsable ledger moved to $dest; a new one starts")
        Save-Events $events
        return
    }
    foreach ($f in $merged) { Remove-Item $f.FullName -ErrorAction SilentlyContinue }
}

function Get-LedgerCount($ledger, [string]$key, [string]$counter) {
    if (-not $ledger -or -not $ledger.ContainsKey($key) -or -not $ledger[$key].ContainsKey($counter)) { return 0 }
    return @($ledger[$key][$counter]).Count
}

function New-Counter([string]$name, [int]$fileUsed, [int]$cap, [int]$default, [string]$record, [int]$logged) {
    $note = ''
    if ($cap -gt $default -and $record -notmatch '(?i)extra round') {
        $note = " (cap $cap has no recorded GD extra round; default $default applies)"
        $cap = $default
    }
    if ($logged) { $note += " (file $fileUsed + hook $logged)" }
    $stopped = $record -match "(?im)^- Stop rule:.*\b$name\b"
    return [pscustomobject]@{ Name = $name; Used = $fileUsed + $logged; Cap = $cap; Note = $note; Stopped = $stopped }
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
    $stop = (([regex]::Matches($text, '(?m)^- Stop rule:.*$') | ForEach-Object { $_.Value }) -join "`n")
    $out = @()
    foreach ($name in 'review', 'qa', 'rework') {
        $default = if ($name -eq 'rework') { First $Defaults["rework-$size"] $Defaults['rework-M'] } else { $Defaults[$name] }
        $used = 0; $cap = $default
        if ($line -match "(?i)\b$name\s*:?\s*(\d+)\s*/\s*(\d+)") { $used = [int]$Matches[1]; $cap = [int]$Matches[2] }
        $out += New-Counter $name $used $cap $default "$gd`n$stop" (Get-LedgerCount $ledger "feature:$slug" $name)
    }
    return $out
}

# Counters of one unsettled bug in bugs.md, or @().
function Get-BugCounters([string]$id, $ledger) {
    if (-not (Test-Path $bugsPath)) { return @() }
    $text = Get-Content $bugsPath -Raw -Encoding UTF8
    if ($text -match "(?m)^\|\s*$id\s*\|[^\n]*\|\s*($Settled)\s*\|") { return @() }
    if ($text -notmatch "(?s)\r?\n## $id\b(.*?)(\r?\n## |$)") { return @() }
    $record = $Matches[1]
    $out = @()
    foreach ($pair in @(@('fix', 'Fix rounds'), @('review', 'Review rounds'))) {
        $name = $pair[0]; $default = $Defaults[$name]; $used = 0; $cap = $default
        if ($record -match "(?m)^- $($pair[1]):\s*(\d+)\s*/\s*(\d+)") { $used = [int]$Matches[1]; $cap = [int]$Matches[2] }
        $out += New-Counter $name $used $cap $default $record (Get-LedgerCount $ledger "bug:$id" $name)
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
function Get-BugMarker([string]$text) { $v = Get-Marker $text 'Bug'; if ($v -and $v -match '^(BUG-\d{4,})\b') { return $Matches[1] }; return $null }
function Get-TargetKey([string]$text) { $v = Get-Marker $text 'Target'; if ($v) { return 'target:' + ($v -replace '\\', '/').ToLowerInvariant() }; return $null }
function Get-VerifyIds([string]$text) { @([regex]::Matches($text, '(?im)^[\s*_>-]*Verify[*_]*:[*_\s]*(BUG-\d{4,})') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique) }
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
    # Only the marker lines /review writes count; a slug or skill name holding "audit" or "round 2" must not.
    # Mode: workflow - review-gate's gates: the main session records those rounds from the verified verdicts.
    $skip = $brief -match '(?im)^[\s*_>-]*Mode[*_]*:[*_\s]*(audit|test-code|workflow)\b'
    $codeFail = $agent -eq 'code-reviewer' -and ($ret -match "${v}Request changes" -or
        ($ret -match "${v}Needs-decision" -and $ret -match '(?i)\bSeverity[*_`]*:[*_`\s]*(Critical|High|Medium)\b'))
    $reviewFail = -not $skip -and ($codeFail -or ($agent -eq 'security-reviewer' -and $ret -match "${v}Blocked"))
    $qaFail = $agent -eq 'qa-lead' -and $ret -match "${v}Not signed off"
    $verifyIds = @(Get-VerifyIds $brief)
    $repros = @([regex]::Matches($ret, '(?im)^[\s*_>-]*Repro[*_]*:[*_\s]*(BUG-\d{4,})\s+reproduces') |
        ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique | Where-Object { $verifyIds -contains $_ })
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

$ledger = Get-Ledger
if ($script:LedgerProblem -eq 'corrupt') {
    $dest = Move-CorruptLedger
    Block ("round-cap: .workflow/rounds.json could not be parsed; moved to $dest so it is never overwritten. " +
        'Its counts are not in the new ledger: merge them back by hand, or report the stop-rule state to the GD.')
}
if ($script:LedgerProblem -eq 'unreadable') {
    if ($Mode -eq 'dispatch') { Block 'round-cap: .workflow/rounds.json is locked or unreadable; round caps cannot be checked. Retry the dispatch.' }
    exit 0
}
# A moved-aside ledger holds counts the live one lacks: caps cannot be trusted until the GD resolves it.
$corruptFiles = @(Get-CorruptFiles)
if ($Mode -eq 'dispatch' -and $corruptFiles.Count) {
    Block ("round-cap: $($corruptFiles.Count) unreadable ledger file(s) in .workflow/ ($(($corruptFiles | ForEach-Object Name) -join ', ')) hold " +
        'round counts the live ledger lacks; caps cannot be checked. Report to the GD: merge their events into rounds.json by hand, or delete them on the GD''s order.')
}

if ($Mode -eq 'dispatch') {
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
    foreach ($s in $slugs) { foreach ($c in Get-FeatureCounters $s $ledger) { if ($c.Used -gt $c.Cap) { $over += Format "feature $s" $c } } }
    foreach ($b in $bugs) { foreach ($c in Get-BugCounters $b $ledger) { if ($c.Used -gt $c.Cap) { $over += Format $b $c } } }
    if ($tkey) { foreach ($c in Get-KeyCounters $tkey $ledger) { if ($c.Used -gt $c.Cap) { $over += Format $tkey $c } } }
    if (-not $marked -and -not $slugs.Count -and -not $bugs.Count -and $Gates -contains $agent) {
        foreach ($c in Get-KeyCounters $sessionKey $ledger) { if ($c.Used -gt $c.Cap) { $over += Format 'this session (no feature, bug or target named)' $c } }
    }
    if ($over.Count) {
        Block ("Stop rule (routing.md): past the round cap - $($over -join '; '). " +
            'Report to the GD: what was tried, last verified state, next best action. ' +
            'Another round only on the GD''s order: record "extra round: <counter> +n" under GD decisions (or in the bug record) and raise that cap; ' +
            "for target or session work add one `"extra-<counter>`" entry under that key in .workflow/rounds.json per round.")
    }
    exit 0
}

# edit
$path = [string](First $in.tool_input.file_path '')
if ($path -notmatch '[\\/]\.workflow[\\/]') { exit 0 }
$msg = @()
$hits = @()
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
    elseif (-not $c.Stopped) { $msg += "$line - at the cap: technical-architect root-causes once (record '- Stop rule:'), the owner gets one more dispatch; another failure stops the work." }
}
if (-not $msg.Count) { exit 0 }
Block ("Stop rule (routing.md):`n" + ($msg -join "`n"))
