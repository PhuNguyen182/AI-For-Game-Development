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
if ((git -C $root config --get claude.lfs 2>$null) -ne 'off') {
    foreach ($p in $staged.Keys) {
        if ($staged[$p] -notin 'A', 'M') { continue }
        $ext = [IO.Path]::GetExtension($p).TrimStart('.').ToLowerInvariant()
        $size = [long](First (git -C $root cat-file -s ":$p" 2>$null) 0)
        if ($BinaryExt -notcontains $ext -and $size -le $MaxPlainBytes) { continue }
        if ((git -C $root check-attr filter -- $p 2>$null) -match 'filter: lfs$') { continue }
        $problems += "not in Git LFS: $p ($([math]::Round($size / 1KB)) KB) - add a .gitattributes rule (skill git-unity-repo), or git config claude.lfs off"
    }
}

if ($problems.Count -gt 0) {
    Block ("Commit blocked:`n  " + ($problems -join "`n  ") + "`nFix and re-stage. Secrets: rule core.md -> Security.")
}
exit 0
