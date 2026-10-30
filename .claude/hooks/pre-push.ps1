# PreToolUse Bash|PowerShell on `git push`: block a radius-3 push form, and block when a commit not yet on any
# remote adds a secret.
. "$PSScriptRoot/common.ps1"

$in = Read-HookInput
if (-not $in) { exit 0 }
$cmd = [string]$in.tool_input.command
# Any run of git global options may precede `push` (-C dir, -c k=v, --no-pager, --git-dir x, ...).
$arg = '(?:"[^"]*"|''[^'']*''|\S+)'
$opt = "(?:-[Cc]\s+$arg|--(?:git-dir|work-tree|namespace|config-env|exec-path)(?:=|\s+)$arg|--[\w-]+(?:=$arg)?|-[A-Za-z]+)"
$git = [regex]::Match($cmd, "\bgit\b((?:\s+$opt)*)\s+push(?![\w.-])", 'IgnoreCase')
if (-not $git.Success) { exit 0 }

# Radius-3 push forms (Find-PushRadius3 in common.ps1), read through quoting, shell wrappers and aliases.
foreach ($p in (Get-GitCalls $cmd ([string](First $in.cwd (Get-Location).Path)))) {
    $why = if ($p.Why) { $p.Why } elseif ($p.Verb -eq 'push') { Find-PushRadius3 $p.Globals $p.Rest }
    if ($why) { Block "Push blocked: $why (a force, delete, mirror, prune, all-tags or anchor-tag push is blast radius 3). The GD runs it: put the exact command under ``Needs GD``." }
}

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

# `git push` is auto-allowed for the configured remotes; a URL or path sends the code somewhere no one set up.
$remotes = @(git -C $root remote 2>$null)
foreach ($p in @(Get-GitCalls $cmd $cwd | Where-Object { $_.Verb -eq 'push' })) {
    $repo = $null; $skip = $false; $isRepo = $false
    foreach ($t in @(Get-GitWords $p.Rest)) {
        if ($isRepo) { $repo = $t; break }
        if ($skip) { $skip = $false; continue }
        if ($t -match '^--repo=(.+)$') { $repo = $Matches[1]; break }
        if ($t -eq '--repo') { $isRepo = $true; continue }
        if ($t -in '-o', '--push-option', '--recurse-submodules') { $skip = $true; continue }
        if ($t -like '-*') { continue }
        $repo = $t; break
    }
    if ($repo -and $remotes -notcontains $repo -and $repo -match '[:/\\@.]') {
        Block "Push blocked: $repo is not a configured remote ($($remotes -join ', ')). Push to a remote by name; adding one is the GD's call."
    }
}

# A clone made with --mirror, or a forced push refspec in config, turns a plain `git push` into radius 3.
foreach ($row in (git -C $root config --get-regexp '^remote\..+\.(mirror|push)$' 2>$null)) {
    if ($row -match '\.mirror\s+true$' -or $row -match '\.push\s+\+') {
        Block "Push blocked: this repository's config makes every push forced or mirrored ($row). The GD runs it: put the exact command under ``Needs GD``."
    }
}

# Every commit on HEAD, a local branch or a tag and on no remote-tracking ref: whatever this push names is among
# them. backup/* anchors are left out: pushing one is refused above, and they may hold pre-rewrite history.
# --diff-merges=first-parent: a merge commit's own changes (a hand-resolved conflict) are scanned too.
$problems = @(Find-AddedSecrets (Get-GitDiffText $root @('log', 'HEAD', '--branches', '--exclude=backup/*', '--tags', '--not', '--remotes',
            '-p', '--diff-merges=first-parent', '--unified=0', '--no-color', '--text', '--format=')))

if ($problems.Count -gt 0) {
    Block ("Push blocked: unpushed commits add secrets:`n  " + (($problems | Select-Object -Unique) -join "`n  ") + "`nA secret already committed is in git history: stop and route to cto (rule core.md -> Security).")
}
exit 0
