# SubagentStop: secret-shape backstop on a log-triage return (contract C5, feature model-tiers). Deterministic, no LLM.
# Scans only agent_type 'log-triage' (exact, case-sensitive). The return is the SubagentHandback report plus
# last_assistant_message after the last prompt (Read-SubagentExchange); only when that exchange return is blank (no
# handback report and last_assistant_message missing, empty or blank) is the transcript's last assistant text after the
# last prompt added. Every secret-patterns.txt regex runs over it, here, never through Find-Secrets (its hit lines carry
# a value prefix). Exit 2 sends the agent back with stderr as its instruction.
# Fail closed:
# - an unexpected error, no return text, or a missing, empty or malformed patterns file withholds the return: the agent
#   is told to return only "Status: Blocked / Summary: digest withheld - secret scan unavailable";
# - a hit is never let through: the first time the agent masks and returns again; with stop_hook_active set it is told
#   to return only "Status: Blocked / Summary: digest withheld - redaction failed";
# - a withheld form passes before the patterns check, so the loop ends even with no patterns file;
# - unreadable hook input blocks every subagent stop (loud by design, as secret-scan.ps1).
# Never: writes a file, calls mem/records/adv, or prints the return, a match or any part of one. Stderr names pattern
# names only; the trap prints the exception type name only.

# First, so an error while loading common.ps1 also fails closed. Self-contained: Block may not exist yet.
trap {
    [Console]::Error.WriteLine("log-triage-scan: scan failed ($($_.Exception.GetType().Name)) - return withheld. Return only these two lines: Status: Blocked / Summary: digest withheld - secret scan unavailable")
    exit 2
}
# Stop: a non-terminating error (an unreadable transcript) reaches the trap instead of scanning less.
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/common.ps1"

$ScanAgents = @('log-triage')
$WithheldLines = @('Status: Blocked', 'Summary: digest withheld - redaction failed', 'Summary: digest withheld - secret scan unavailable')
$Unavailable = 'Return only these two lines: Status: Blocked / Summary: digest withheld - secret scan unavailable'

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
$lines = @($ret -split '\r?\n' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
if (($lines -ccontains 'Status: Blocked') -and -not @($lines | Where-Object { $WithheldLines -cnotcontains $_ }).Count) { exit 0 }

# 6. Nothing to scan with.
if ($script:SecretPatterns.Count -eq 0) {
    Block "log-triage-scan: .claude/hooks/secret-patterns.txt is missing, empty or malformed - return withheld. $Unavailable"
}

# 7. Pattern names that match. A regex that runs past its timeout throws, and the trap withholds the return.
if ([string]::IsNullOrWhiteSpace($ret)) { exit 0 }
$names = @()
foreach ($name in $script:SecretPatterns.Keys) {
    $rx = [regex]::new($script:SecretPatterns[$name], [Text.RegularExpressions.RegexOptions]::None, [TimeSpan]::FromSeconds(1))
    if ($rx.IsMatch($ret)) { $names += [string]$name }
}
if (-not $names.Count) { exit 0 }
$kinds = $names -join ', '
if ($in.stop_hook_active -eq $true) {
    Block "log-triage-scan: still secret-shaped ($kinds). Return only these two lines: Status: Blocked / Summary: digest withheld - redaction failed"
}
Block "log-triage-scan: the return carries secret-shaped text ($kinds). Mask each match as <redacted:<pattern name>> and return again."
