# Shared helpers for the framework's hooks. Dot-source it: . "$PSScriptRoot/common.ps1"

$script:SecretPatterns = [ordered]@{
    'private key'          = '-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY-----'
    'AWS access key'       = '\b(?:AKIA|ASIA)[0-9A-Z]{16}\b'
    'Google API key'       = '\bAIza[0-9A-Za-z_\-]{35}\b'
    'GitHub token'         = '\bgh[pousr]_[A-Za-z0-9]{36,}\b'
    'Slack token'          = '\bxox[abprs]-[0-9A-Za-z\-]{10,}'
    'Stripe live key'      = '\b[rs]k_live_[0-9A-Za-z]{24,}\b'
    'JWT'                  = '\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}'
    'password assignment'  = '(?i)\b(?:password|passwd|secret|api[_-]?key)\s*[:=]\s*["''][^"''\s]{8,}["'']'
}

# Files that legitimately contain the patterns above: the hooks themselves and the scan skill's docs.
$script:SecretScanExempt = '[\\/]\.claude[\\/](?:hooks[\\/]|skills[\\/]secret-and-supply-chain-scan[\\/])'

# First non-empty argument. Stands in for ?? so the hooks also run on Windows PowerShell 5.1.
function First { foreach ($v in $args) { if ($null -ne $v -and [string]$v -ne '') { return $v } }; return $null }

function Read-HookInput {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
    return $raw | ConvertFrom-Json
}

# Returns one "<kind>: <redacted sample>" line per pattern that matches. Never echoes the full value.
function Find-Secrets([string]$Text) {
    $hits = @()
    if ([string]::IsNullOrEmpty($Text)) { return $hits }
    foreach ($name in $script:SecretPatterns.Keys) {
        $m = [regex]::Match($Text, $script:SecretPatterns[$name])
        if ($m.Success) {
            $v = $m.Value
            $sample = if ($v.Length -gt 8) { $v.Substring(0, 6) + '...' } else { '...' }
            $hits += "${name}: $sample"
        }
    }
    return $hits
}

function Block([string]$Message) {
    [Console]::Error.WriteLine($Message)
    exit 2
}
