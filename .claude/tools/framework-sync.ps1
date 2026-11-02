#requires -Version 7
# Sync the framework (.claude/ plus a few seed files) from a source checkout into a target Unity project.
# Called by install-framework.ps1 and update-framework.ps1; run those, not this.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('Install', 'Update')][string]$Mode,
    [Parameter(Mandatory)][string]$SourceRoot,
    [Parameter(Mandatory)][string]$Target,
    [string]$SourceUrl = '',
    [string]$SourceRef = '',
    [string]$SourceCommit = '',
    [switch]$DryRun,
    [switch]$Force
)
$ErrorActionPreference = 'Stop'

$SourceRoot = (Resolve-Path -LiteralPath $SourceRoot).Path
$Target = (Resolve-Path -LiteralPath $Target).Path
if ($SourceRoot -eq $Target) { throw "Target is the framework checkout itself: $Target" }
if (-not (Test-Path -LiteralPath (Join-Path $Target '.git'))) { throw "Target is not a git repository root: $Target" }
if (-not (Test-Path -LiteralPath (Join-Path $Target 'Assets')) -and -not (Test-Path -LiteralPath (Join-Path $Target 'ProjectSettings'))) {
    Write-Warning "No Assets/ or ProjectSettings/ in $Target - is this the Unity project's repo root?"
}

$ManifestRel = '.claude/.framework-manifest.json'
$ManifestPath = Join-Path $Target $ManifestRel
$Stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmss') + 'Z'
$BackupRoot = Join-Path $Target ".claude/.framework-backup/$Stamp"

# ---------- helpers ----------
function Get-NormHash([string]$Path) {
    # SHA-256; text files hash with LF endings so a CRLF checkout does not read as a local edit.
    $bytes = [IO.File]::ReadAllBytes($Path)
    $probe = [Math]::Min($bytes.Length, 8000)
    if ($probe -gt 0 -and [Array]::IndexOf($bytes, [byte]0, 0, $probe) -lt 0) {
        $bytes = [Text.Encoding]::UTF8.GetBytes([Text.Encoding]::UTF8.GetString($bytes).Replace("`r`n", "`n"))
    }
    return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes))
}

function Copy-ToTarget([string]$Rel, [string]$From) {
    if ($DryRun) { return }
    $dst = Join-Path $Target $Rel
    New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
    Copy-Item -LiteralPath $From -Destination $dst -Force
}

function Backup-Target([string]$Rel) {
    if ($DryRun) { return }
    $from = Join-Path $Target $Rel
    if (-not (Test-Path -LiteralPath $from)) { return }
    $to = Join-Path $BackupRoot $Rel
    New-Item -ItemType Directory -Force -Path (Split-Path $to) | Out-Null
    Copy-Item -LiteralPath $from -Destination $to -Force
}

function ConvertTo-Canon($o) {
    if ($null -eq $o) { return 'null' }
    if ($o -is [System.Collections.IDictionary]) {
        return '{' + ((@($o.Keys) | Sort-Object | ForEach-Object { "$_=" + (ConvertTo-Canon $o[$_]) }) -join ',') + '}'
    }
    if ($o -is [System.Collections.IEnumerable] -and $o -isnot [string]) {
        return '[' + ((@($o) | ForEach-Object { ConvertTo-Canon $_ }) -join ',') + ']'
    }
    return ($o | ConvertTo-Json -Compress)
}

function Get-Matcher($g) { if ($g.Contains('matcher')) { [string]$g['matcher'] } else { '' } }

function Get-HookFingerprints($settings) {
    $out = [System.Collections.Generic.List[string]]::new()
    if ($settings -and $settings.Contains('hooks')) {
        foreach ($ev in $settings.hooks.Keys) {
            foreach ($g in $settings.hooks[$ev]) {
                foreach ($e in $g.hooks) { $out.Add("$ev|$(Get-Matcher $g)|$(ConvertTo-Canon $e)") }
            }
        }
    }
    return , $out
}

function Remove-HookEntry($dst, [string]$Ev, [string]$Matcher, [string]$Canon) {
    if (-not $dst.Contains('hooks') -or -not $dst.hooks.Contains($Ev)) { return 0 }
    $removed = 0
    $groups = @()
    foreach ($g in $dst.hooks[$Ev]) {
        if ((Get-Matcher $g) -eq $Matcher) {
            $keep = @($g.hooks | Where-Object { (ConvertTo-Canon $_) -ne $Canon })
            $removed += @($g.hooks).Count - $keep.Count
            $g.hooks = $keep
        }
        if (@($g.hooks).Count -gt 0) { $groups += $g }
    }
    if ($groups.Count -eq 0) { $dst.hooks.Remove($Ev) } else { $dst.hooks[$Ev] = $groups }
    return $removed
}

function Merge-Settings($src, $dst, [string[]]$StaleHookFps) {
    # Additive merge of the framework's settings into the project's. Returns the number of changes.
    $n = 0
    foreach ($k in @($src.Keys)) {
        if (-not $dst.Contains($k)) { $dst[$k] = $src[$k]; $n++; continue }
        if ($k -eq 'permissions') {
            foreach ($pk in @($src.permissions.Keys)) {
                if (-not $dst.permissions.Contains($pk)) { $dst.permissions[$pk] = $src.permissions[$pk]; $n++; continue }
                if ($src.permissions[$pk] -isnot [System.Collections.IEnumerable] -or $src.permissions[$pk] -is [string]) { continue }
                foreach ($e in @($src.permissions[$pk])) {
                    if (@($dst.permissions[$pk]) -notcontains $e) { $dst.permissions[$pk] = @($dst.permissions[$pk]) + $e; $n++ }
                }
            }
        }
        elseif ($k -eq 'env') {
            foreach ($ek in @($src.env.Keys)) {
                if (-not $dst.env.Contains($ek)) { $dst.env[$ek] = $src.env[$ek]; $n++ }
            }
        }
        elseif ($k -eq 'hooks') {
            foreach ($fp in $StaleHookFps) {
                $p = $fp.Split('|', 3)
                $n += Remove-HookEntry $dst $p[0] $p[1] $p[2]
            }
            foreach ($ev in @($src.hooks.Keys)) {
                if (-not $dst.hooks.Contains($ev)) { $dst.hooks[$ev] = @() }
                foreach ($g in $src.hooks[$ev]) {
                    $m = Get-Matcher $g
                    $have = @($dst.hooks[$ev] | Where-Object { (Get-Matcher $_) -eq $m } | ForEach-Object { $_.hooks } | ForEach-Object { ConvertTo-Canon $_ })
                    $new = @($g.hooks | Where-Object { $have -notcontains (ConvertTo-Canon $_) })
                    if ($new.Count -eq 0) { continue }
                    $tg = $dst.hooks[$ev] | Where-Object { (Get-Matcher $_) -eq $m } | Select-Object -First 1
                    if ($tg) { $tg.hooks = @($tg.hooks) + $new }
                    else {
                        $ng = [ordered]@{}
                        foreach ($gk in $g.Keys) { $ng[$gk] = $g[$gk] }
                        $ng.hooks = $new
                        $dst.hooks[$ev] = @($dst.hooks[$ev]) + $ng
                    }
                    $n += $new.Count
                }
            }
        }
    }
    return $n
}

function Get-GitignoreFrameworkLines([string]$Text) {
    # Framework runtime-state patterns: the tail of the source .gitignore minus its "framework repo only" block.
    $lines = $Text -split "`r?`n"
    $start = [Array]::FindIndex($lines, [Predicate[string]] { param($l) $l -like '# Claude Code local runtime state*' })
    if ($start -lt 0) { return @() }
    $out = @(); $skip = $false
    foreach ($l in $lines[$start..($lines.Count - 1)]) {
        if ($l -like '# --- Framework repo only*') { $skip = $true; continue }
        if ($l -like '# --- end framework repo only*') { $skip = $false; continue }
        if (-not $skip) { $out += $l }
    }
    return $out
}

# ---------- state ----------
$recorded = @{}
$recordedHooks = @()
if (Test-Path -LiteralPath $ManifestPath) {
    $old = Get-Content -Raw -LiteralPath $ManifestPath | ConvertFrom-Json -AsHashtable
    if ($old.files) { $recorded = $old.files }
    if ($old.settingsHooks) { $recordedHooks = @($old.settingsHooks) }
}
if ($Mode -eq 'Update' -and -not (Test-Path -LiteralPath $ManifestPath)) { throw "No $ManifestRel in $Target. Run install-framework.ps1 first." }

$added = [System.Collections.Generic.List[string]]::new()
$updated = [System.Collections.Generic.List[string]]::new()
$kept = [System.Collections.Generic.List[string]]::new()
$conflicts = [System.Collections.Generic.List[string]]::new()
$removed = [System.Collections.Generic.List[string]]::new()
$obsoleteKept = [System.Collections.Generic.List[string]]::new()
$unchanged = 0
$newRecorded = [ordered]@{}

# ---------- framework-owned files ----------
$srcRels = [System.Collections.Generic.List[string]]::new()
$excluded = '^\.claude/(settings\.json|settings\.local\.json)$|^\.claude/worktrees/|^\.claude/\.framework-|\.(keystore|jks|p12|pfx|p8|pem|mobileprovision)$|(^|/)\.env(\.|$)'
foreach ($f in (git -c core.quotepath=off -C $SourceRoot ls-files -- .claude)) {
    if ($f -match $excluded) { continue }
    if (Test-Path -LiteralPath (Join-Path $SourceRoot $f) -PathType Leaf) { $srcRels.Add($f) }
}
if ($srcRels.Count -eq 0) { throw "No .claude/ files found in source $SourceRoot" }
$srcSet = [System.Collections.Generic.HashSet[string]]::new([string[]]$srcRels)

foreach ($rel in $srcRels) {
    $from = Join-Path $SourceRoot $rel
    $to = Join-Path $Target $rel
    $s = Get-NormHash $from
    $r = $recorded[$rel]
    if (-not (Test-Path -LiteralPath $to -PathType Leaf)) {
        Copy-ToTarget $rel $from; $added.Add($rel); $newRecorded[$rel] = $s; continue
    }
    $t = Get-NormHash $to
    if ($t -eq $s) {
        $unchanged++; $newRecorded[$rel] = $s
        if (-not $DryRun -and (Test-Path -LiteralPath "$to.framework-new")) { Remove-Item -LiteralPath "$to.framework-new" -Force }
        continue
    }
    if ($r -and $t -eq $r) {
        Backup-Target $rel; Copy-ToTarget $rel $from; $updated.Add($rel); $newRecorded[$rel] = $s; continue
    }
    if ($r -and $s -eq $r) {
        # Local edit, framework unchanged since the last sync: nothing to reconcile.
        $kept.Add($rel); $newRecorded[$rel] = $r; continue
    }
    if ($Force) {
        Backup-Target $rel; Copy-ToTarget $rel $from; $updated.Add("$rel (forced)"); $newRecorded[$rel] = $s; continue
    }
    # Local edit and framework changed, or a pre-existing file with no baseline: keep the project's, offer the new one.
    Copy-ToTarget "$rel.framework-new" $from
    $conflicts.Add($rel)
    if ($r) { $newRecorded[$rel] = $r }
}

# Files the framework retired since the last sync.
foreach ($rel in @($recorded.Keys)) {
    if ($srcSet.Contains($rel) -or $rel -notlike '.claude/*') { continue }
    $to = Join-Path $Target $rel
    if (-not (Test-Path -LiteralPath $to -PathType Leaf)) { continue }
    if ((Get-NormHash $to) -eq $recorded[$rel]) {
        Backup-Target $rel
        if (-not $DryRun) { Remove-Item -LiteralPath $to -Force }
        $removed.Add($rel)
    }
    else { $obsoleteKept.Add($rel); $newRecorded[$rel] = $recorded[$rel] }
}

# ---------- settings.json (merged) ----------
$settingsNote = ''
$srcSettingsPath = Join-Path $SourceRoot '.claude/settings.json'
$dstSettingsPath = Join-Path $Target '.claude/settings.json'
$srcSettings = Get-Content -Raw -LiteralPath $srcSettingsPath | ConvertFrom-Json -AsHashtable
$srcHookFps = Get-HookFingerprints $srcSettings
if (-not (Test-Path -LiteralPath $dstSettingsPath)) {
    Copy-ToTarget '.claude/settings.json' $srcSettingsPath
    $settingsNote = 'created from the framework'
}
else {
    $dstSettings = Get-Content -Raw -LiteralPath $dstSettingsPath | ConvertFrom-Json -AsHashtable
    $before = ConvertTo-Canon $dstSettings
    $stale = @($recordedHooks | Where-Object { -not $srcHookFps.Contains($_) })
    $n = Merge-Settings $srcSettings $dstSettings $stale
    if ((ConvertTo-Canon $dstSettings) -ne $before) {
        Backup-Target '.claude/settings.json'
        if (-not $DryRun) { $dstSettings | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $dstSettingsPath -Encoding utf8NoBOM }
        $settingsNote = "merged ($n change(s))"
    }
    else { $settingsNote = 'already up to date' }
}

# ---------- .gitignore (append missing framework lines) ----------
$giNote = ''
$srcGi = Join-Path $SourceRoot '.gitignore'
$dstGi = Join-Path $Target '.gitignore'
if (Test-Path -LiteralPath $srcGi) {
    $fwLines = @(Get-GitignoreFrameworkLines (Get-Content -Raw -LiteralPath $srcGi)) + '.claude/.framework-backup/'
    if (-not (Test-Path -LiteralPath $dstGi)) {
        if (-not $DryRun) { Set-Content -LiteralPath $dstGi -Value ($fwLines -join "`n") -Encoding utf8NoBOM }
        $giNote = 'created with the framework patterns'
    }
    else {
        $have = @((Get-Content -LiteralPath $dstGi) | ForEach-Object { $_.Trim() })
        $missing = @($fwLines | Where-Object { $_.Trim() -and -not $_.StartsWith('#') -and $have -notcontains $_.Trim() })
        if ($missing.Count -gt 0) {
            if (-not $DryRun) {
                $block = "`n# Added by the AI-For-Game framework`n" + ($missing -join "`n") + "`n"
                Add-Content -LiteralPath $dstGi -Value $block -NoNewline -Encoding utf8NoBOM
            }
            $giNote = "$($missing.Count) line(s) appended"
        }
        else { $giNote = 'already up to date' }
    }
}

# ---------- project-owned seeds (install only, never overwrite) ----------
$seeded = [System.Collections.Generic.List[string]]::new()
$seedKept = [System.Collections.Generic.List[string]]::new()
if ($Mode -eq 'Install') {
    foreach ($rel in 'CLAUDE.md', '.xerjignore', '.memory/sources.txt') {
        $from = Join-Path $SourceRoot $rel
        if (-not (Test-Path -LiteralPath $from)) { continue }
        if (Test-Path -LiteralPath (Join-Path $Target $rel)) { $seedKept.Add($rel) }
        else { Copy-ToTarget $rel $from; $seeded.Add($rel) }
    }
}

# ---------- manifest ----------
if (-not $DryRun) {
    $manifest = [ordered]@{
        version       = 1
        source        = [ordered]@{ url = $SourceUrl; ref = $SourceRef; commit = $SourceCommit }
        syncedAt      = [DateTime]::UtcNow.ToString('o')
        settingsHooks = @($srcHookFps)
        files         = $newRecorded
    }
    New-Item -ItemType Directory -Force -Path (Split-Path $ManifestPath) | Out-Null
    $manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ManifestPath -Encoding utf8NoBOM
}

# ---------- report ----------
$tag = if ($DryRun) { '[dry-run] ' } else { '' }
Write-Host "${tag}Framework $($Mode.ToLower()) -> $Target"
if ($SourceCommit) { Write-Host "  source: $SourceUrl @ $($SourceCommit.Substring(0, [Math]::Min(10, $SourceCommit.Length)))" }
Write-Host ("  added {0} | updated {1} | unchanged {2} | kept local edits {3} | removed {4} | conflicts {5}" -f $added.Count, $updated.Count, $unchanged, $kept.Count, $removed.Count, $conflicts.Count)
Write-Host "  settings.json: $settingsNote"
if ($giNote) { Write-Host "  .gitignore: $giNote" }
if ($seeded.Count) { Write-Host "  created (project-owned): $($seeded -join ', ')" }
if ($seedKept.Count) { Write-Host "  kept your existing: $($seedKept -join ', ')" }
foreach ($x in $updated) { Write-Host "  updated  $x" }
foreach ($x in $removed) { Write-Host "  removed  $x (retired by the framework)" }
foreach ($x in $obsoleteKept) { Write-Host "  retired but locally edited, kept: $x" }
foreach ($x in $conflicts) { Write-Host "  CONFLICT $x -> new version in $x.framework-new" }
if ($conflicts.Count) {
    Write-Host "Resolve each conflict by merging the .framework-new file into yours and deleting it, or rerun with -Force to take the framework's version (the old file is backed up under .claude/.framework-backup/)."
}
if (-not $DryRun) {
    $tail = if ($Mode -eq 'Install') { ', then /new-project.' } else { '.' }
    Write-Host ('Next: open Claude Code in the project, accept the trust dialog, run /verify-layer' + $tail)
}
