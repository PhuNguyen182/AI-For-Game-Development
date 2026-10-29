# PreToolUse Bash|PowerShell on `git push`: block when a commit not yet on any remote adds a secret.
. "$PSScriptRoot/common.ps1"

$in = Read-HookInput
if (-not $in) { exit 0 }
$cmd = [string]$in.tool_input.command
# Any run of git global options may precede `push` (-C dir, -c k=v, --no-pager, --git-dir x, ...).
$arg = '(?:"[^"]*"|''[^'']*''|\S+)'
$opt = "(?:-[Cc]\s+$arg|--(?:git-dir|work-tree|namespace|config-env|exec-path)(?:=|\s+)$arg|--[\w-]+(?:=$arg)?|-[A-Za-z]+)"
$git = [regex]::Match($cmd, "\bgit\b((?:\s+$opt)*)\s+push(?![\w.-])", 'IgnoreCase')
if (-not $git.Success) { exit 0 }

# Resolve the repository the push runs in: `cd <dir> &&`, `git -C <dir>`, else the session cwd.
$cwd = [string](First $in.cwd (Get-Location).Path)
$dir = $cwd
$cd = [regex]::Match($cmd, '^\s*(?:cd|Set-Location)\s+(?:"([^"]+)"|''([^'']+)''|(\S+))\s*(?:&&|;)')
if ($cd.Success) { $dir = @($cd.Groups[1].Value, $cd.Groups[2].Value, $cd.Groups[3].Value | Where-Object { $_ })[0] }
$gc = [regex]::Match($git.Groups[1].Value, '(?:^|\s)-C\s+(?:"([^"]+)"|''([^'']+)''|(\S+))')
if ($gc.Success) { $dir = @($gc.Groups[1].Value, $gc.Groups[2].Value, $gc.Groups[3].Value | Where-Object { $_ })[0] }
# Git Bash spells C:\ as /c/.
if ($env:OS -eq 'Windows_NT' -and $dir -match '^/([a-zA-Z])(/|$)') { $dir = "$($Matches[1]):/" + $dir.Substring(3) }
if ($dir -and -not [IO.Path]::IsPathRooted($dir)) { $dir = Join-Path $cwd $dir }

$root = $null
foreach ($d in @($dir, $cwd)) {
    if ($d -and (Test-Path $d)) { $root = git -C $d rev-parse --show-toplevel 2>$null; if ($root) { break } }
}
if (-not $root) { exit 0 }  # no repository at all: the push itself cannot run

# Every commit reachable from HEAD and from no remote-tracking ref: what this push would publish.
$problems = @()
$file = $null
foreach ($line in (git -C $root log HEAD --not --remotes -p --unified=0 --no-color --text --format= 2>$null)) {
    if ($line -match '^\+\+\+ b/(.+)$') { $file = $Matches[1]; continue }
    if (-not $file -or $line -notmatch '^\+' -or ("/$file" -match $script:SecretScanExempt)) { continue }
    $added = $line.Substring(1)
    if ($file -like '*.jsonl') { $added = $added.Replace('\"', '"') }
    foreach ($h in (Find-Secrets $added)) { $problems += "secret in ${file}: $h" }
}

if ($problems.Count -gt 0) {
    Block ("Push blocked: unpushed commits add secrets:`n  " + (($problems | Select-Object -Unique) -join "`n  ") + "`nA secret already committed is in git history: stop and route to cto (rule core.md -> Security).")
}
exit 0
