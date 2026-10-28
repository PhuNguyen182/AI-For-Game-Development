# PreToolUse Bash|PowerShell on `git commit`: block staged secrets and broken Unity .meta pairing.
. "$PSScriptRoot/common.ps1"

$in = Read-HookInput
if (-not $in) { exit 0 }
$cmd = [string]$in.tool_input.command
if ($cmd -notmatch '\bgit\b(?:\s+-C\s+(?:"[^"]*"|''[^'']*''|\S+))?\s+commit\b') { exit 0 }

# Resolve the repository the commit runs in: `cd <dir> &&`, `git -C <dir>`, else the session cwd.
$dir = [string](First $in.cwd (Get-Location).Path)
$cd = [regex]::Match($cmd, '^\s*(?:cd|Set-Location)\s+(?:"([^"]+)"|''([^'']+)''|(\S+))\s*(?:&&|;)')
if ($cd.Success) { $dir = @($cd.Groups[1].Value, $cd.Groups[2].Value, $cd.Groups[3].Value | Where-Object { $_ })[0] }
$gc = [regex]::Match($cmd, '\bgit\s+-C\s+(?:"([^"]+)"|(\S+))')
if ($gc.Success) { $dir = @($gc.Groups[1].Value, $gc.Groups[2].Value | Where-Object { $_ })[0] }
# Git Bash spells C:\ as /c/.
if ($env:OS -eq 'Windows_NT' -and $dir -match '^/([a-zA-Z])(/|$)') { $dir = "$($Matches[1]):/" + $dir.Substring(3) }
if (-not (Test-Path $dir)) { exit 0 }

$root = git -C $dir rev-parse --show-toplevel 2>$null
if (-not $root) { exit 0 }
$problems = @()

# 1. Secrets in added lines, per file.
$file = $null
foreach ($line in (git -C $root diff --cached --unified=0 --no-color 2>$null)) {
    if ($line -match '^\+\+\+ b/(.+)$') { $file = $Matches[1]; continue }
    if (-not $file -or $line -notmatch '^\+' -or ("/$file" -match $script:SecretScanExempt)) { continue }
    foreach ($h in (Find-Secrets $line.Substring(1))) { $problems += "secret in ${file}: $h" }
}

# 2. Unity .meta pairing, only in a Unity project.
if (Test-Path (Join-Path $root 'Assets')) {
    $staged = @{}
    foreach ($row in (git -C $root diff --cached --name-status --no-renames 2>$null)) {
        $s, $p = $row -split "`t", 2
        $staged[$p] = $s
    }
    foreach ($p in $staged.Keys) {
        if ($p -notmatch '^Assets/') { continue }
        $s = $staged[$p]
        if ($p.EndsWith('.meta')) {
            $asset = $p.Substring(0, $p.Length - 5)
            if ($s -eq 'A' -and -not (Test-Path (Join-Path $root $asset))) { $problems += "orphan .meta (no asset): $p" }
            continue
        }
        $meta = "$p.meta"
        $metaTracked = git -C $root ls-files --error-unmatch -- $meta 2>$null
        if ($s -eq 'A' -and -not $staged.ContainsKey($meta) -and -not $metaTracked) { $problems += "asset without .meta: $p" }
        if ($s -eq 'D' -and $metaTracked -and -not $staged.ContainsKey($meta)) { $problems += ".meta left behind for deleted asset: $meta" }
    }
}

if ($problems.Count -gt 0) {
    Block ("Commit blocked:`n  " + ($problems -join "`n  ") + "`nFix and re-stage. Secrets: rule core.md -> Security.")
}
exit 0
