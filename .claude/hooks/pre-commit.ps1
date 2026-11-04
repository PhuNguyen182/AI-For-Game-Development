# PreToolUse Bash|PowerShell on `git commit` (and the commit `merge/rebase/cherry-pick/revert --continue` makes):
# block staged secrets, secret-bearing files (keystore, .env, service-account JSON), raw evidence dumps and broken
# Unity .meta pairing.
. "$PSScriptRoot/common.ps1"
# Fail closed: an unexpected error must block the commit, not let it through unscanned.
trap { Block "Blocked: pre-commit scan failed ($_) - the commit was not scanned." }

$in = Read-HookInput
if (-not $in) { Block 'Blocked: pre-commit received no readable hook input - the commit was not scanned.' }
$cmd = [string]$in.tool_input.command
$tool = [string]$in.tool_name
$cwd = Get-GateCwd $in $tool

# The closed list of forms (Read-GateCommand in common.ps1): quoted text and heredoc bodies are not commands, anything else
# that commits is accepted only in a form whose repository is certain, and refused with the way to re-run it.
$form = Read-GateCommand $cmd $tool $cwd 'commit'
if ($form.Kind -eq 'None') {
    # A commit through an alias: settings.json's filter runs this hook only when "commit" is in the text. git-guard refuses them all.
    foreach ($c in (Get-GitCalls $cmd $cwd)) {
        if ($c.Alias -and $c.Verb -eq 'commit') { Block 'Commit blocked: a commit through an alias, which the scan cannot read. Spell out git commit.' }
    }
    if (Test-GateCallHit $cmd $cwd 'commit') { Block 'Commit blocked: a git commit in a form the scan cannot read. Re-run it in a simple form: git commit ..., git -C <path> commit ..., or cd <path> && git commit ...' }
    exit 0
}
if ($form.Why) { Block "Commit blocked: $($form.Why)" }

# The scan below reads the index as it stands before the command runs. A commit that stages as it commits
# (-a, -i, -o, -p, a pathspec) would record content the scan never saw. A `git add` before it is refused with the form.
function Find-UnscannedCommit([string]$Rest) {
    # Each long option that stages, with the shortest prefix git takes for it (a shorter one is ambiguous, and git refuses it).
    $staging = @{ 'all' = 3; 'include' = 3; 'interactive' = 3; 'only' = 1; 'patch' = 4; 'pathspec-from-file' = 11 }
    $skip = $false
    foreach ($t in @([regex]::Matches($Rest, '\S+') | ForEach-Object { $_.Value })) {
        if ($skip) { $skip = $false; continue }
        if ($t -eq '--') { return '-- <pathspec>' }
        if ($t -match '^\d*[<>]' -or $t -eq '-') { continue }  # a redirection, or stdin for -F
        if ($t -match '^--([^=]+)') {
            $name = $Matches[1]
            foreach ($long in $staging.Keys) { if ($name.Length -ge $staging[$long] -and $long.StartsWith($name, [StringComparison]::OrdinalIgnoreCase)) { return $t } }
        }
        if ($t -match '^--(?:message|file|reuse-message|reedit-message|template|author|date|fixup|squash|trailer|cleanup)$') { $skip = $true; continue }
        if ($t -match '^--') { continue }
        if ($t -cmatch '^-([A-Za-z]\S*)$') {  # \S: -m"a b" is one word, the message attached
            $cluster = $Matches[1]
            for ($i = 0; $i -lt $cluster.Length; $i++) {
                if ('aiop'.Contains([string]$cluster[$i])) { return $t }
                if ('mFCct'.Contains([string]$cluster[$i])) { if ($i -eq $cluster.Length - 1) { $skip = $true }; break }  # takes a value
            }
            continue
        }
        return "$t (a pathspec)"
    }
    return $null
}
if ($form.VerbName -eq 'commit') {
    $u = Find-UnscannedCommit $form.Rest
    if ($u) { Block "Commit blocked: ``git commit $u`` stages as it commits, so the secret and .meta scan cannot see it. ``git add <paths>`` in its own call, then a plain ``git commit`` (skill git-commit)." }
}

$root = Resolve-GitRoot @($form.Dir) 'commit'
if (-not $root) { exit 0 }  # an existing folder outside any repository: the commit itself cannot run
$problems = @()

# 1. Secrets in added lines, per file.
$problems += @(Find-AddedSecrets (Get-GitDiffText $root @('diff', '--cached', '--text', '--unified=0', '--no-color')))

# -z: a path git would quote (non-ASCII, a quote character) is read as itself.
$changes = @(Get-GitRawChanges $root @('diff', '--cached'))
$staged = @{}
foreach ($c in $changes) { $staged[$c.Path] = $c.Status }

# 2. Files that never enter git by path or content (keystore, .env, service-account JSON), and raw evidence dumps.
$problems += @(Find-ForbiddenFiles $root $changes)

# 3. Unity .meta pairing, only in a Unity project. A /feature lane A worktree has no Editor, so its new assets have no
# .meta until the merge (the main session commits them after the post-merge import): that one check is skipped there.
$lane = Test-LaneWorktree $root ([string](First $env:CLAUDE_PROJECT_DIR (Split-Path (Split-Path $PSScriptRoot))))
if (Test-Path -LiteralPath (Join-Path $root 'Assets')) {
    foreach ($p in $staged.Keys) {
        if ($p -notmatch '^Assets/') { continue }
        $s = $staged[$p]
        if ($p.EndsWith('.meta')) {
            $asset = $p.Substring(0, $p.Length - 5)
            if ($s -eq 'A' -and -not (Test-Path -LiteralPath (Join-Path $root $asset))) { $problems += "orphan .meta (no asset): $p" }
            continue
        }
        $meta = "$p.meta"
        $metaTracked = git -C $root ls-files --error-unmatch -- $meta 2>$null
        if ($s -eq 'A' -and -not $lane -and -not $staged.ContainsKey($meta) -and -not $metaTracked) { $problems += "asset without .meta: $p" }
        if ($s -eq 'D' -and $metaTracked -and -not $staged.ContainsKey($meta)) { $problems += ".meta left behind for deleted asset: $meta" }
    }

    # 4. A .meta GUID never changes: every scene and prefab reference to the asset would break.
    foreach ($p in $staged.Keys) {
        if ($staged[$p] -ne 'M' -or -not $p.EndsWith('.meta')) { continue }
        $old = [regex]::Match(((git -C $root show "HEAD:$p" 2>$null) -join "`n"), '(?m)^guid:\s*(\w+)').Groups[1].Value
        $new = [regex]::Match(((git -C $root show ":$p" 2>$null) -join "`n"), '(?m)^guid:\s*(\w+)').Groups[1].Value
        if ($old -and $new -and $old -ne $new) { $problems += "GUID changed in ${p}: $old -> $new (breaks every reference to the asset)" }
    }
}

# 5. Binaries and large files go through Git LFS. Opt out per repo: git config claude.lfs off
$BinaryExt = 'png', 'jpg', 'jpeg', 'tga', 'psd', 'psb', 'tif', 'tiff', 'exr', 'hdr', 'gif', 'bmp', 'fbx', 'obj', 'blend',
    'max', 'ma', 'mb', 'wav', 'mp3', 'ogg', 'aif', 'aiff', 'flac', 'mp4', 'mov', 'webm', 'ttf', 'otf', 'zip', '7z',
    'unitypackage', 'dll', 'so', 'a', 'aar', 'jar', 'bundle', 'apk', 'aab', 'ipa'
$MaxPlainBytes = 5MB
# Text Unity YAML stays out of LFS at any size: merge=lfs would replace the UnityYAMLMerge driver.
# A binary .asset (LightingData, NavMesh) has no %YAML header and still needs LFS when large.
$UnityYamlExt = 'unity', 'prefab', 'asset', 'mat', 'anim', 'controller', 'overridecontroller', 'physicmaterial', 'meta'
if ((git -C $root config --get claude.lfs 2>$null) -ne 'off') {
    foreach ($p in $staged.Keys) {
        if ($staged[$p] -notin 'A', 'M') { continue }
        $ext = [IO.Path]::GetExtension($p).TrimStart('.').ToLowerInvariant()
        $size = [long](First (git -C $root cat-file -s ":$p" 2>$null) 0)
        if ($BinaryExt -notcontains $ext -and $size -le $MaxPlainBytes) { continue }
        if ($UnityYamlExt -contains $ext -and [string](git -C $root show ":$p" 2>$null | Select-Object -First 1) -like '%YAML*') { continue }
        if ((git -C $root check-attr filter -- $p 2>$null) -match 'filter: lfs$') { continue }
        $problems += "not in Git LFS: $p ($([math]::Round($size / 1KB)) KB) - add a .gitattributes rule (skill git-unity-repo), or git config claude.lfs off"
    }
}

if ($problems.Count -gt 0) {
    Block ("Commit blocked:`n  " + ($problems -join "`n  ") + "`nFix and re-stage. Secrets: rule core.md -> Security.")
}
exit 0
