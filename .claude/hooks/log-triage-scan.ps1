# Secret-shape backstop on a log-triage report (contract C5, feature model-tiers, change 1). Deterministic, no LLM.
# Two events, one explicit -Mode; a missing or unknown mode blocks (exit 2), nothing scanned:
#   handback  PreToolUse, matcher SubagentHandback: scans the report before the tool call delivers it. R is every string
#             leaf of tool_input (recursive, depth cap 5), field-name agnostic. Exit 2 refuses the call; stderr goes to
#             the agent. agent_type absent or empty is scanned (fail closed); present and not in the scan set passes.
#   stop      SubagentStop: R is the SubagentHandback report plus last_assistant_message after the last prompt
#             (Read-SubagentExchange); only when that exchange return is blank is the transcript's last assistant text
#             after the last prompt added. Exit 2 sends the agent back with stderr as its instruction.
# Scans only agent_type 'log-triage' (exact, case-sensitive). Every secret-patterns.txt regex runs over R here, with a
# 1 s timeout, never through Find-Secrets (its hit lines carry a value prefix).
# Fail closed:
# - an unexpected error, an unknown mode, no report text, or a missing, empty or malformed patterns file withholds the
#   report: the agent is told to hand back (or return) only "Status: Blocked / Summary: digest withheld - secret scan
#   unavailable"; the PreToolUse entry also carries onFailure: block;
# - a hit is never let through. handback: stateless, every hit message names both exits (mask and call SubagentHandback
#   again, or the redaction-failed form). stop: the first time the agent masks and returns again; with stop_hook_active
#   set it is told to return only "Status: Blocked / Summary: digest withheld - redaction failed";
# - a withheld form passes before the patterns check, so the loop ends even with no patterns file;
# - unreadable hook input blocks (loud by design, as secret-scan.ps1).
# Never: writes a file, calls mem/records/adv, or prints the report, a match or any part of one. Stderr names pattern
# names only; the trap prints the exception type name only.
param([string]$Mode = '')

# Right after param, so an error while loading common.ps1 also fails closed. Self-contained: Block may not exist yet.
trap {
    # A .NET method's exception (a regex timeout) arrives wrapped: name the inner one.
    $e = $_.Exception
    if ($e -is [Management.Automation.MethodInvocationException] -and $e.InnerException) { $e = $e.InnerException }
    $type = $e.GetType().Name
    if ($Mode -ceq 'handback') {
        [Console]::Error.WriteLine("log-triage-scan: scan failed ($type) - handback withheld. Call SubagentHandback with only these two lines: Status: Blocked / Summary: digest withheld - secret scan unavailable")
    } else {
        [Console]::Error.WriteLine("log-triage-scan: scan failed ($type) - return withheld. Return only these two lines: Status: Blocked / Summary: digest withheld - secret scan unavailable")
    }
    exit 2
}
# Stop: a non-terminating error (an unreadable transcript) reaches the trap instead of scanning less.
$ErrorActionPreference = 'Stop'
# No ValidateSet: a binding error exits 1 before the trap runs, which fails open.
if ($Mode -cne 'handback' -and $Mode -cne 'stop') {
    [Console]::Error.WriteLine('log-triage-scan: unknown -Mode - nothing scanned.')
    exit 2
}
. "$PSScriptRoot/common.ps1"

$ScanAgents = @('log-triage')
$WithheldLines = @('Status: Blocked', 'Summary: digest withheld - redaction failed', 'Summary: digest withheld - secret scan unavailable')

# Text blocks of a transcript line's message content, joined.
function Get-MessageText($Content) {
    if ($Content -is [string]) { return $Content }
    return ((@($Content) | Where-Object { $_.type -eq 'text' } | ForEach-Object { [string]$_.text }) -join "`n")
}

# The transcript's last assistant text after the last prompt (a user line with text, as Read-SubagentExchange reads it).
function Get-LastAssistantText([string]$Path) {
    if (-not $Path -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) { return '' }
    $lines = @(Get-Content -LiteralPath $Path -Encoding UTF8)
    $lastPrompt = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -notmatch '"type"\s*:\s*"user"') { continue }
        try { $o = $lines[$i] | ConvertFrom-Json } catch { continue }
        if ($o.type -ne 'user') { continue }
        if (Get-MessageText $o.message.content) { $lastPrompt = $i }
    }
    for ($i = $lines.Count - 1; $i -gt $lastPrompt; $i--) {
        if ($lines[$i] -notmatch '"type"\s*:\s*"assistant"') { continue }
        try { $o = $lines[$i] | ConvertFrom-Json } catch { continue }
        if ($o.type -ne 'assistant') { continue }
        $text = Get-MessageText $o.message.content
        if (-not [string]::IsNullOrWhiteSpace($text)) { return [string]$text }
    }
    return ''
}

# Every string leaf under $Node into $Into, whatever the field names. Deeper than 5 levels throws: the trap withholds.
function Add-StringLeaves($Node, [int]$Depth, [Collections.Generic.List[string]]$Into) {
    if ($Depth -gt 5) { throw [InvalidOperationException]::new('tool_input nested too deep') }
    if ($null -eq $Node) { return }
    if ($Node -is [string]) { $Into.Add($Node); return }
    if ($Node -is [Collections.IDictionary]) { foreach ($v in @($Node.Values)) { Add-StringLeaves $v ($Depth + 1) $Into }; return }
    if ($Node -is [Collections.IList]) { foreach ($v in $Node) { Add-StringLeaves $v ($Depth + 1) $Into }; return }
    if ($Node -is [Management.Automation.PSCustomObject]) { foreach ($p in @($Node.PSObject.Properties)) { Add-StringLeaves $p.Value ($Depth + 1) $Into } }
}

# Pattern names whose regex matches $Text. A regex that runs past its timeout throws, and the trap withholds.
function Get-PatternHits([string]$Text) {
    $names = @()
    foreach ($name in $script:SecretPatterns.Keys) {
        $rx = [regex]::new($script:SecretPatterns[$name], [Text.RegularExpressions.RegexOptions]::None, [TimeSpan]::FromSeconds(1))
        if ($rx.IsMatch($Text)) { $names += [string]$name }
    }
    return , $names
}

# A withheld form carries no log text: every non-blank trimmed line is a withheld line, with a Status: Blocked line.
function Test-WithheldForm([string]$Text) {
    $lines = @($Text -split '\r?\n' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    return (($lines -ccontains 'Status: Blocked') -and -not @($lines | Where-Object { $WithheldLines -cnotcontains $_ }).Count)
}

if ($Mode -ceq 'handback') {
    $Unavailable = 'Call SubagentHandback with only these two lines: Status: Blocked / Summary: digest withheld - secret scan unavailable'

    # 2. No readable input.
    $in = Read-HookInput
    if (-not $in) { Block 'log-triage-scan: no readable hook input - handback not scanned.' }

    # 3. Scan set. Absent or empty agent_type is scanned (fail closed).
    $agent = [string]$in.agent_type
    if (-not [string]::IsNullOrEmpty($agent) -and $ScanAgents -cnotcontains $agent) { exit 0 }

    # 4. The report: every string leaf of tool_input.
    $leaves = New-Object 'Collections.Generic.List[string]'
    $prop = $in.PSObject.Properties['tool_input']
    if ($prop -and $null -ne $prop.Value) { Add-StringLeaves $prop.Value 1 $leaves }
    $ret = $leaves -join "`n"
    if ([string]::IsNullOrWhiteSpace($ret)) { Block "log-triage-scan: scan failed (no report text) - handback withheld. $Unavailable" }

    # 5. A withheld form passes, patterns file or not.
    if (Test-WithheldForm $ret) { exit 0 }

    # 6. Nothing to scan with.
    if ($script:SecretPatterns.Count -eq 0) {
        Block "log-triage-scan: .claude/hooks/secret-patterns.txt is missing, empty or malformed - handback withheld. $Unavailable"
    }

    # 7. Pattern names that match.
    $names = Get-PatternHits $ret
    if (-not $names.Count) { exit 0 }
    Block "log-triage-scan: the handback carries secret-shaped text ($($names -join ', ')). Mask each match as <redacted:<pattern name>> and call SubagentHandback again. If you cannot mask it, call SubagentHandback with only these two lines: Status: Blocked / Summary: digest withheld - redaction failed"
}

# -Mode stop.
$Unavailable = 'Return only these two lines: Status: Blocked / Summary: digest withheld - secret scan unavailable'

# 2. No readable input.
$in = Read-HookInput
if (-not $in) { Block 'log-triage-scan: no readable hook input - return not scanned.' }

# 3. Scan set.
if ($ScanAgents -cnotcontains [string]$in.agent_type) { exit 0 }

# 4. The return.
$ret = [string](Read-SubagentExchange $in).Return
if ([string]::IsNullOrWhiteSpace($ret)) {
    $ret = $ret + "`n" + (Get-LastAssistantText ([string]$in.agent_transcript_path))
    if ([string]::IsNullOrWhiteSpace($ret)) { Block "log-triage-scan: scan failed (no return text) - return withheld. $Unavailable" }
}

# 5. A withheld form carries no log text: it passes, patterns file or not.
if (Test-WithheldForm $ret) { exit 0 }

# 6. Nothing to scan with.
if ($script:SecretPatterns.Count -eq 0) {
    Block "log-triage-scan: .claude/hooks/secret-patterns.txt is missing, empty or malformed - return withheld. $Unavailable"
}

# 7. Pattern names that match.
$names = Get-PatternHits $ret
if (-not $names.Count) { exit 0 }
$kinds = $names -join ', '
if ($in.stop_hook_active -eq $true) {
    Block "log-triage-scan: still secret-shaped ($kinds). Return only these two lines: Status: Blocked / Summary: digest withheld - redaction failed"
}
Block "log-triage-scan: the return carries secret-shaped text ($kinds). Mask each match as <redacted:<pattern name>> and return again."
