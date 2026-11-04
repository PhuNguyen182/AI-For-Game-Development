# PreToolUse Bash|PowerShell on `git push`: block a radius-3 push form, and block when a commit not yet on any
# remote adds a secret, a secret-bearing file (keystore, .env, service-account JSON) or a raw evidence dump.
. "$PSScriptRoot/common.ps1"
# Fail closed: an unexpected error must block the push, not let it through unscanned.
trap { Block "Blocked: pre-push scan failed ($_) - the push was not scanned." }

$in = Read-HookInput
if (-not $in) { Block 'Blocked: pre-push received no readable hook input - the push was not scanned.' }
$cmd = [string]$in.tool_input.command
$tool = [string]$in.tool_name
$cwd = Get-GateCwd $in $tool

# The closed list of forms (Read-GateCommand in common.ps1): quoted text and heredoc bodies are not commands, anything else
# that pushes is accepted only in a form whose repository is certain, and refused with the way to re-run it.
$form = Read-GateCommand $cmd $tool $cwd 'push'

# Radius-3 push forms (Find-PushRadius3 in common.ps1), read through quoting, shell wrappers and aliases. First, so a force
# push hears that it is one, not that its spelling is unusual.
$radius = 'a force, delete, mirror, prune, all-tags or anchor-tag push is blast radius 3'
foreach ($p in (Get-GitCalls $cmd ([string](First $cwd (Get-Location).Path)))) {
    $why = if ($p.Why) { $p.Why } elseif ($p.Verb -eq 'push') { Find-PushRadius3 $p.Globals $p.Rest }
    if ($why) { Block "Push blocked: $why ($radius). The GD runs it: put the exact command under ``Needs GD``." }
}
if ($form.Kind -eq 'None') {
    # A push through an alias: git-guard refuses it too, but this hook holds the same line when "push" is in the text.
    foreach ($p in (Get-GitCalls $cmd $cwd)) {
        if ($p.Alias -and $p.Verb -eq 'push') { Block 'Push blocked: a push through an alias, which the scan cannot read. Spell out git push.' }
    }
    exit 0
}
if ($form.Why) { Block "Push blocked: $($form.Why)" }
# The parser's words as well: the regex above stops at a heredoc operator, and the rest of that line is still arguments.
$why = Find-PushRadius3 $form.Globals $form.Rest
if ($why) { Block "Push blocked: $why ($radius). The GD runs it: put the exact command under ``Needs GD``." }

$root = Resolve-GitRoot @($form.Dir) 'push' -AllowBare
if (-not $root) { exit 0 }  # an existing folder outside any repository: the push itself cannot run

# `git push` is auto-allowed for the configured remotes; a URL or path sends the code somewhere no one set up.
$remotes = @(git -C $root remote 2>$null)
$repo = $null; $skip = $false; $isRepo = $false
foreach ($t in @(Get-GitWords $form.Rest)) {
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

# A clone made with --mirror, or a forced push refspec in config, turns a plain `git push` into radius 3.
foreach ($row in (git -C $root config --get-regexp '^remote\..+\.(mirror|push)$' 2>$null)) {
    if ($row -match '\.mirror\s+true$' -or $row -match '\.push\s+\+') {
        Block "Push blocked: this repository's config makes every push forced or mirrored ($row). The GD runs it: put the exact command under ``Needs GD``."
    }
}

# Every commit on HEAD, a local branch or a tag and on no remote-tracking ref: whatever this push names is among
# them. backup/* anchors are left out: pushing one is refused above, and they may hold pre-rewrite history.
# --diff-merges=first-parent: a merge commit's own changes (a hand-resolved conflict) are scanned too.
$range = @('log', 'HEAD', '--branches', '--exclude=backup/*', '--tags', '--not', '--remotes', '--diff-merges=first-parent', '--format=')
$problems = @(Find-AddedSecrets (Get-GitDiffText $root ($range + @('-p', '--unified=0', '--no-color', '--text'))))
# The same file rules as pre-commit (keystore, .env, service-account JSON, raw evidence) on every file those commits add.
$problems += @(Find-ForbiddenFiles $root @(Get-GitRawChanges $root $range))

if ($problems.Count -gt 0) {
    Block ("Push blocked: unpushed commits add secrets or secret-bearing files:`n  " + (($problems | Select-Object -Unique) -join "`n  ") + "`nA secret already committed is in git history: stop and route to cto (rule core.md -> Security).")
}
exit 0
