# SubagentStop: store an adviser's return verbatim in the advisory store (skill advisory-protocol, adv.py). Deterministic, no LLM.
# Covers the three advisers and any agent whose brief carries an "Advisory-Thread:" line (critic, researcher in /design and /monet).
# Never blocks: exit 2 would send the subagent back to work. A failure goes to stderr, and each workflow checks with "adv list --thread".
. "$PSScriptRoot/common.ps1"

$in = Read-HookInput
if (-not $in) { exit 0 }
$agent = [string]$in.agent_type
$exchange = Read-SubagentExchange $in
if ($AdvisoryAgents -cnotcontains $agent -and $exchange.Brief -notmatch $AdvisoryThreadPattern) { exit 0 }
if ([string]::IsNullOrWhiteSpace($exchange.Return)) { exit 0 }

$root = Get-ProjectRoot $in
$py = @(Resolve-Python $root | Where-Object { $_ })
if (-not $py.Count) { [Console]::Error.WriteLine('advisory-capture: no Python, return not stored'); exit 0 }
$tmp = [IO.Path]::GetTempFileName()
try {
    $payload = @{ agent = $agent; agent_id = [string]$in.agent_id; session = [string]$in.session_id; brief = $exchange.Brief; return = $exchange.Return }
    [IO.File]::WriteAllText($tmp, ($payload | ConvertTo-Json -Compress -Depth 3), (New-Object Text.UTF8Encoding($false)))
    $rest = @($py | Select-Object -Skip 1)
    $out = & $py[0] @rest -I (Join-Path $root '.claude/skills/mem/scripts/adv.py') --root $root ingest --file $tmp 2>&1
    if ($LASTEXITCODE -ne 0) { [Console]::Error.WriteLine("advisory-capture: return not stored: $out") }
} finally {
    Remove-Item -LiteralPath $tmp -ErrorAction SilentlyContinue
}
exit 0
