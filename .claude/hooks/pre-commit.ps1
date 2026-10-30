# PreToolUse Bash|PowerShell on `git commit` (and the commit `merge/rebase/cherry-pick/revert --continue` makes):
# block staged secrets and broken Unity .meta pairing.
. "$PSScriptRoot/common.ps1"

$in = Read-HookInput
if (-not $in) { exit 0 }
$cmd = [string]$in.tool_input.command
# Any run of git global options may precede `commit` (-C dir, -c k=v, --no-pager, --git-dir x, ...).
$arg = '(?:"[^"]*"|''[^'']*''|\S+)'
$opt = "(?:-[Cc]\s+$arg|--(?:git-dir|work-tree|namespace|config-env|exec-path)(?:=|\s+)$arg|--[\w-]+(?:=$arg)?|-[A-Za-z]+)"
# commit(?![\w.-]): not commit-tree, commit-graph or a config key such as commit.gpgsign.
$git = [regex]::Match($cmd, "\bgit(?:\.exe)?\b((?:\s+$opt)*)\s+(?:commit(?![\w.-])|(?:merge|rebase|cherry-pick|revert)\s+--continue\b)", 'IgnoreCase')
if (-not $git.Success) { exit 0 }

# The scan below reads the index as it stands before the command runs. A commit that stages as it commits
# (-a, -i, -o, -p, a pathspec) or a `git add` chained before it would record content the scan never saw.
function Find-UnscannedCommit([string]$Rest) {
    $skip = $false
    foreach ($t in @([regex]::Matches($Rest, '\S+') | ForEach-Object { $_.Value })) {
        if ($skip) { $skip = $false; continue }
        if ($t -eq '--') { return '-- <pathspec>' }
        if ($t -match '^\d*[<>]' -or $t -eq '-') { continue }  # a redirection, or stdin for -F
        if ($t -match '^--(?:all|inc(?:l(?:u(?:de?)?)?)?|onl(?:y)?|pathspec-from-file|interactive|patch)(?:=|$)') { return $t }
        if ($t -match '^--(?:message|file|reuse-message|reedit-message|template|author|date|fixup|squash|trailer|cleanup)$') { $skip = $true; continue }
        if ($t -match '^--') { continue }
        if ($t -cmatch '^-([A-Za-z]+)$') {
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
$seenAdd = $false
foreach ($c in [regex]::Matches((Remove-QuotedText $cmd), "\bgit(?:\.exe)?\b(?:\s+$opt)*\s+(add|stage|commit)(?![\w.-])([^;&|\r\n]*)", 'IgnoreCase')) {
    if ($c.Groups[1].Value -in 'add', 'stage') { $seenAdd = $true; continue }
    if ($seenAdd) { Block 'Commit blocked: `git add` and `git commit` in one call - this scan runs before the add. Stage in its own call, then commit (skill git-commit).' }
    $u = Find-UnscannedCommit $c.Groups[2].Value
    if ($u) { Block "Commit blocked: ``git commit $u`` stages as it commits, so the secret and .meta scan cannot see it. ``git add <paths>`` in its own call, then a plain ``git commit`` (skill git-commit)." }
}

# Resolve the repository the commit runs in: `cd <dir> &&`, `git -C <dir>`, else the session cwd.
$cwd = [string](First $in.cwd (Get-Location).Path)
$dir = $cwd
$cd = [regex]::Match($cmd, '^\s*(?:cd|Set-Location)\s+(?:"([^"]+)"|''([^'']+)''|(\S+))\s*(?:&&|;)')
if ($cd.Success) { $dir = @($cd.Groups[1].Value, $cd.Groups[2].Value, $cd.Groups[3].Value | Where-Object { $_ })[0] }
# -C only among git's own options before `commit`: `commit -C <rev>` reuses a message. Case-sensitive: -c is config.
$gc = [regex]::Match($git.Groups[1].Value, '(?:^|\s)-C\s+(?:"([^"]+)"|''([^'']+)''|(\S+))')
if ($gc.Success) { $dir = @($gc.Groups[1].Value, $gc.Groups[2].Value, $gc.Groups[3].Value | Where-Object { $_ })[0] }
# Git Bash spells C:\ as /c/.
if ($env:OS -eq 'Windows_NT' -and $dir -match '^/([a-zA-Z])(/|$)') { $dir = "$($Matches[1]):/" + $dir.Substring(3) }
# A relative cd/-C path is relative to the session cwd, not to this hook process's directory.
if ($dir -and -not [IO.Path]::IsPathRooted($dir)) { $dir = Join-Path $cwd $dir }

# A directory that does not resolve falls back to the session cwd rather than skipping the scan.
$root = $null
foreach ($d in @($dir, $cwd)) {
    if ($d -and (Test-Path $d)) { $root = git -C $d rev-parse --show-toplevel 2>$null; if ($root) { break } }
}
if (-not $root) { exit 0 }  # no repository at all: the commit itself cannot run
$problems = @()

# 1. Secrets in added lines, per file.
$problems += @(Find-AddedSecrets (Get-GitDiffText $root @('diff', '--cached', '--text', '--unified=0', '--no-color')))

$staged = @{}
foreach ($row in (git -C $root diff --cached --name-status --no-renames 2>$null)) {
    $s, $p = $row -split "`t", 2
    $staged[$p] = $s
}

# 2. Unity .meta pairing, only in a Unity project.
if (Test-Path (Join-Path $root 'Assets')) {
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

    # 3. A .meta GUID never changes: every scene and prefab reference to the asset would break.
    foreach ($p in $staged.Keys) {
        if ($staged[$p] -ne 'M' -or -not $p.EndsWith('.meta')) { continue }
        $old = [regex]::Match(((git -C $root show "HEAD:$p" 2>$null) -join "`n"), '(?m)^guid:\s*(\w+)').Groups[1].Value
        $new = [regex]::Match(((git -C $root show ":$p" 2>$null) -join "`n"), '(?m)^guid:\s*(\w+)').Groups[1].Value
        if ($old -and $new -and $old -ne $new) { $problems += "GUID changed in ${p}: $old -> $new (breaks every reference to the asset)" }
    }
}

# 4. Binaries and large files go through Git LFS. Opt out per repo: git config claude.lfs off
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
