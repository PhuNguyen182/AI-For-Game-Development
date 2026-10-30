# PreToolUse Bash|PowerShell on any `git`: block what the settings.json globs cannot pin down, read through quoting,
# sh/bash/pwsh -c wrappers and aliases (Get-GitCalls in common.ps1).
#   reset --hard, clean -f, checkout/switch -f, switch --discard-changes, read-tree -u --reset
#                                       destroy uncommitted or untracked work no anchor holds (radius 3: the GD runs them)
#   push forms Find-PushRadius3 names   radius 3; a push through an alias is refused so pre-push.ps1 sees it spelled out
#   grep -O                             runs a program from an otherwise read-only command
#   --output                            writes an arbitrary file from diff/log/show
#   --upload-pack, --receive-pack, --exec  name a program to run (ls-remote, fetch, pull, clone, archive)
#   -c alias.*, -c core.sshCommand ..., GIT_CONFIG_*  config the hooks cannot read, or that runs a program
# Best effort: a command that hides git behind a variable or $(...) is not seen. The rule in the agent still holds.
. "$PSScriptRoot/common.ps1"

$in = Read-HookInput
if (-not $in) { exit 0 }
$cwd = [string](First $in.cwd (Get-Location).Path)

# True when a long option the call carries is $Name or a prefix of it at least $Min characters long.
function Test-Long([string[]]$Longs, [string]$Name, [int]$Min) {
    return [bool]($Longs | Where-Object { $_.Length -ge $Min -and $Name.StartsWith($_) })
}

foreach ($g in (Get-GitCalls ([string]$in.tool_input.command) $cwd)) {
    $why = $g.Why
    $words = @(Get-GitWords $g.Rest)
    $longs = @($words | Where-Object { $_ -match '^--(?!no-)[\w-]' } | ForEach-Object { ($_.Substring(2) -split '=', 2)[0] })
    $shorts = (@($words | Where-Object { $_ -cmatch '^-[A-Za-z]+$' } | ForEach-Object { $_.Substring(1) }) -join '')
    if (-not $why) {
        switch ($g.Verb) {
            'reset' { if (Test-Long $longs 'hard' 2) { $why = 'git reset --hard (radius 3: destroys uncommitted work)' } }
            'clean' {
                $dry = $shorts -cmatch '[ni]' -or (Test-Long $longs 'dry-run' 2) -or (Test-Long $longs 'interactive' 2)
                $noForce = [string](git -C $cwd config --get clean.requireForce 2>$null) -eq 'false'
                if ($shorts -cmatch 'f' -or (Test-Long $longs 'force' 2) -or ($noForce -and -not $dry)) { $why = 'git clean -f (radius 3: deletes untracked files)' }
            }
            { $_ -in 'ls-remote', 'fetch', 'pull', 'clone', 'archive', 'remote' } {
                # A transport option names the program run on the other end, and a local path runs it here.
                $short = $g.Verb -in 'ls-remote', 'clone' -and $shorts -cmatch 'u'
                if ($short -or (Test-Long $longs 'upload-pack' 2) -or (Test-Long $longs 'receive-pack' 3) -or (Test-Long $longs 'exec' 2)) {
                    $why = "git $($g.Verb) --upload-pack/--exec (runs an arbitrary program)"
                }
            }
            'checkout' { if ($shorts -cmatch 'f' -or (Test-Long $longs 'force' 2)) { $why = 'git checkout -f (radius 3: overwrites uncommitted and untracked files)' } }
            'switch' { if ($shorts -cmatch 'f' -or (Test-Long $longs 'force' 2) -or (Test-Long $longs 'discard-changes' 2)) { $why = 'git switch -f / --discard-changes (radius 3: overwrites uncommitted and untracked files)' } }
            'read-tree' { if ($shorts -cmatch 'u' -and (Test-Long $longs 'reset' 3)) { $why = 'git read-tree -u --reset (radius 3: overwrites the working tree)' } }
            'push' { $why = if ($g.Alias) { 'a push through an alias (spell out git push so the secret scan sees it)' } else { Find-PushRadius3 $g.Globals $g.Rest } }
            'grep' { if ($shorts -cmatch 'O' -or (Test-Long $longs 'open-files-in-pager' 2)) { $why = 'git grep -O (runs a program)' } }
            # `git tag backup/*` is auto-allowed to create an anchor; git also reads options after the name, so
            # `git tag backup/x -d v1.0` would delete another tag without a prompt.
            'tag' {
                $opts = @($words | Where-Object { $_ -like '-*' }); $names = @($words | Where-Object { $_ -notlike '-*' })
                $cleanup = $opts.Count -gt 0 -and -not ($opts | Where-Object { $_ -notin '-d', '--delete' }) -and -not ($names | Where-Object { $_ -notlike 'backup/*' })
                # List mode reads tags; a backup/* pattern there is a filter, not a name. Only these options switch
                # git into list mode (with them `-f` fails); --sort, --format, -i stay in create mode, where -f moves a tag.
                $listing = [bool]($opts | Where-Object { $_ -match '^(?:-l|--list|-n\d*|--(?:no-)?contains|--points-at|--(?:no-)?merged)(?:=|$)' })
                if (($names | Where-Object { $_ -like 'backup/*' }) -and $opts.Count -gt 0 -and -not $cleanup -and -not $listing) {
                    $why = 'git tag backup/... with an option (create an anchor bare: git tag backup/<op>-<utc> [<sha>]; delete with git tag -d backup/... only)'
                }
            }
        }
    }
    if (-not $why -and (Test-Long $longs 'output' 3)) { $why = "git $($g.Verb) --output (writes a file)" }
    if ($why) { Block "Blocked: $why. The GD runs it: put the exact command under ``Needs GD`` (skill git-safety-anchor)." }
}
exit 0
