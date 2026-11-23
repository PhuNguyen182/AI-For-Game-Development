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

function Add-MissingFrameworkLines([string]$Path, [string[]]$FwLines) {
    # Append framework lines the file lacks. Comments and blank lines are context only: they are never a reason to append.
    if (-not (Test-Path -LiteralPath $Path)) {
        # LF and one final newline: Set-Content would end it in the platform's line ending.
        if (-not $DryRun) { [IO.File]::WriteAllText($Path, (($FwLines -join "`n").TrimEnd("`r", "`n") + "`n"), [Text.UTF8Encoding]::new($false)) }
        return 'created with the framework patterns'
    }
    $have = @((Get-Content -LiteralPath $Path) | ForEach-Object { $_.Trim() })
    $missing = @($FwLines | Where-Object { $_.Trim() -and -not $_.StartsWith('#') -and $have -notcontains $_.Trim() })
    if ($missing.Count -eq 0) { return 'already up to date' }
    if (-not $DryRun) {
        # The target's own line ending, by majority: a CRLF file stays CRLF.
        $raw = [IO.File]::ReadAllText($Path)
        $crlf = [regex]::Matches($raw, "`r`n").Count
        $eol = if ($crlf -gt [regex]::Matches($raw, "(?<!`r)`n").Count) { "`r`n" } else { "`n" }
        $block = "$eol# Added by the AI-For-Game framework$eol" + ($missing -join $eol) + $eol
        Add-Content -LiteralPath $Path -Value $block -NoNewline -Encoding utf8NoBOM
    }
    return "$($missing.Count) line(s) appended"
}

# ---------- framework-owned files ----------
$srcRels = [System.Collections.Generic.List[string]]::new()
$excluded = '^\.claude/(settings\.json|settings\.local\.json)$|^\.claude/worktrees/|^\.claude/\.framework-|\.(keystore|jks|p12|pfx|p8|pem|mobileprovision)$|(^|/)\.env(\.|$)'
foreach ($f in (git -c core.quotepath=off -C $SourceRoot ls-files -- .claude)) {
    if ($f -match $excluded) { continue }
    if (Test-Path -LiteralPath (Join-Path $SourceRoot $f) -PathType Leaf) { $srcRels.Add($f) }
}
if ($srcRels.Count -eq 0) { throw "No .claude/ files found in source $SourceRoot" }

# Two target paths are the same file exactly when the target's file system treats them as one: Windows and default
# macOS fold case, Linux does not. One probe, on the first of these the target holds (.git always: checked above), sets
# the comparer of every collection keyed by a target path. A target mixing both kinds of folder is unsupported.
$probeRel = @($ManifestRel, '.claude', '.git') | Where-Object { Test-Path -LiteralPath (Join-Path $Target $_) } | Select-Object -First 1
$caseFolds = Test-Path -LiteralPath (Join-Path $Target $probeRel.ToUpperInvariant())
$pathCmp = if ($caseFolds) { [StringComparer]::OrdinalIgnoreCase } else { [StringComparer]::Ordinal }
$srcSet = [System.Collections.Generic.HashSet[string]]::new([string[]]$srcRels, $pathCmp)

# ---------- state ----------
# Keyed by $pathCmp. Keys one file under it (a manifest written where case does not fold, read where it does): the key
# spelled exactly like a source path wins, else the first in ordinal order. Loaded in ordinal key order, so retirements
# run and report in one order on every run: before PowerShell 7.3, -AsHashtable returns an unordered Hashtable.
$recorded = [System.Collections.Specialized.OrderedDictionary]::new([System.Collections.IEqualityComparer]$pathCmp)
$recordedHooks = @()
if (Test-Path -LiteralPath $ManifestPath) {
    $old = Get-Content -Raw -LiteralPath $ManifestPath | ConvertFrom-Json -AsHashtable
    if ($old.files) {
        $srcExact = [System.Collections.Generic.HashSet[string]]::new([string[]]$srcRels, [StringComparer]::Ordinal)
        $oldKeys = [string[]]@($old.files.Keys); [Array]::Sort($oldKeys, [StringComparer]::Ordinal)
        foreach ($k in $oldKeys) {
            if (-not $recorded.Contains($k)) { $recorded.Add($k, $old.files[$k]) }
            elseif ($srcExact.Contains($k)) { $recorded.Remove($k); $recorded.Add($k, $old.files[$k]) }
        }
    }
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
# What [ordered]@{} is, with $pathCmp in place of PowerShell's case-insensitive default.
$newRecorded = [System.Collections.Specialized.OrderedDictionary]::new([System.Collections.IEqualityComparer]$pathCmp)

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
# $srcSet compares by $pathCmp: where case folds, a case-only rename's old spelling is the source file, not retired.
# The '.claude/' prefix needs no $pathCmp: every recorded key is a path the framework's own `git ls-files -- .claude` gave.
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

# Folders those removals emptied, deepest first. Only an ancestor of a removed file, strictly inside .claude/, and never
# an ancestor of a source file: after a real run that folder holds the file, though a dry run has not written an added
# one yet. Any other entry left in it (an untracked or locally added file, a folder this pass keeps) keeps it. A dry run
# reports the same set: there a removed file still exists, so it counts as gone. Paths, and the entry names read from
# disk, compare by the target file system's rule ($pathCmp).
function Add-Ancestors($Set, [string]$Rel) {
    $d = $Rel.Substring(0, $Rel.LastIndexOf('/'))
    # Ordinal: every path here starts with the '.claude/' that the framework's own `git ls-files -- .claude` spelled.
    while ($d.StartsWith('.claude/', [StringComparison]::Ordinal)) { [void]$Set.Add($d); $d = $d.Substring(0, $d.LastIndexOf('/')) }
}
$removedDirs = [System.Collections.Generic.List[string]]::new()
$removedSet = [System.Collections.Generic.HashSet[string]]::new([string[]]@($removed), $pathCmp)
$dirSet = [System.Collections.Generic.HashSet[string]]::new($pathCmp)
foreach ($rel in $removed) { Add-Ancestors $dirSet $rel }
$srcDirs = [System.Collections.Generic.HashSet[string]]::new($pathCmp)
foreach ($rel in $srcRels) { Add-Ancestors $srcDirs $rel }
$goneDirs = [System.Collections.Generic.HashSet[string]]::new($pathCmp)
foreach ($d in @($dirSet | Sort-Object { ($_ -split '/').Count } -Descending)) {
    if ($srcDirs.Contains($d)) { continue }
    $abs = Join-Path $Target $d
    if (-not (Test-Path -LiteralPath $abs -PathType Container)) { continue }
    $busy = $false
    foreach ($e in [IO.Directory]::EnumerateFileSystemEntries($abs)) {
        $eRel = "$d/" + [IO.Path]::GetFileName($e)
        $gone = if ([IO.Directory]::Exists($e)) { $goneDirs.Contains($eRel) } else { $DryRun -and $removedSet.Contains($eRel) }
        if (-not $gone) { $busy = $true; break }
    }
    if ($busy) { continue }
    # Non-recursive: a folder that is not empty after all stays instead of losing what it holds.
    if (-not $DryRun) { try { [IO.Directory]::Delete($abs, $false) } catch { continue } }
    [void]$goneDirs.Add($d); $removedDirs.Add($d)
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

# ---------- .gitignore, .gitattributes (append missing framework lines) ----------
$giNote = ''
$srcGi = Join-Path $SourceRoot '.gitignore'
if (Test-Path -LiteralPath $srcGi) {
    $fwLines = @(Get-GitignoreFrameworkLines (Get-Content -Raw -LiteralPath $srcGi)) + '.claude/.framework-backup/'
    $giNote = Add-MissingFrameworkLines (Join-Path $Target '.gitignore') $fwLines
}
$gaNote = ''
$srcGa = Join-Path $SourceRoot '.gitattributes'
if (Test-Path -LiteralPath $srcGa) {
    # The framework's own .gitattributes holds only framework lines: a project's Unity and LFS rules live in its copy.
    $gaNote = Add-MissingFrameworkLines (Join-Path $Target '.gitattributes') @((Get-Content -Raw -LiteralPath $srcGa) -split "`r?`n")
}

# ---------- the journals in this target ----------
# Reads git's answer, not the file's text: a later project rule can defeat the framework line, and a project that ignores
# .workflow/ loses a journal from git with no other sign. The project's rules stay the project's: warn, change nothing.
# A game project tracks its framework backlog journal too: only the framework repo ignores its own.
$journals = [ordered]@{
    '.workflow/bugs.jsonl'              = 'the bug journal'
    '.workflow/backlog.jsonl'           = 'the game backlog journal'
    '.workflow/debt.jsonl'              = 'the project debt journal'
    '.workflow/features.jsonl'          = 'the feature registry journal'
    '.workflow/framework-backlog.jsonl' = 'the framework backlog journal'
}
$journalWarnings = [System.Collections.Generic.List[string]]::new()
$srcGaText = if (Test-Path -LiteralPath $srcGa) { Get-Content -Raw -LiteralPath $srcGa } else { '' }
foreach ($journalRel in $journals.Keys) {
    $what = $journals[$journalRel]
    # Only a line the framework ships can be overridden. A dry run that would append lines cannot read their effect yet.
    $shipped = $srcGaText -match "(?m)^$([regex]::Escape($journalRel))\s"
    if ($shipped -and $gaNote -and (-not $DryRun -or $gaNote -eq 'already up to date')) {
        $merge = ([string](git -C $Target check-attr merge -- $journalRel) -split ': ')[-1]
        if ($merge -ne 'union') { $journalWarnings.Add("$journalRel resolves to merge=$merge in this target, not union: a project rule overrides the framework line, so merges of $what can conflict. Move ``$journalRel text eol=lf merge=union`` after that rule.") }
        $eol = ([string](git -C $Target check-attr eol -- $journalRel) -split ': ')[-1]
        if ($eol -ne 'lf') { $journalWarnings.Add("$journalRel resolves to eol=$eol in this target, not lf: a project rule overrides the framework line, so $what can end up with mixed line endings. Move ``$journalRel text eol=lf merge=union`` after that rule.") }
    }
    git -C $Target check-ignore -q -- $journalRel 2>$null
    if ($LASTEXITCODE -eq 0) { $journalWarnings.Add("$journalRel is ignored by this target's git rules: $what is the truth and must stay tracked. Remove the rule that ignores it.") }
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
if ($gaNote) { Write-Host "  .gitattributes: $gaNote" }
foreach ($x in $journalWarnings) { Write-Warning $x }
if ($seeded.Count) { Write-Host "  created (project-owned): $($seeded -join ', ')" }
if ($seedKept.Count) { Write-Host "  kept your existing: $($seedKept -join ', ')" }
foreach ($x in $updated) { Write-Host "  updated  $x" }
foreach ($x in $removed) { Write-Host "  removed  $x (retired by the framework)" }
foreach ($x in $removedDirs) { Write-Host "  removed  $x/ (empty folder)" }
foreach ($x in $obsoleteKept) { Write-Host "  retired but locally edited, kept: $x" }
foreach ($x in $conflicts) { Write-Host "  CONFLICT $x -> new version in $x.framework-new" }
if ($conflicts.Count) {
    Write-Host "Resolve each conflict by merging the .framework-new file into yours and deleting it, or rerun with -Force to take the framework's version (the old file is backed up under .claude/.framework-backup/)."
}
if (-not $DryRun) {
    $tail = if ($Mode -eq 'Install') { ', then /new-project.' } else { '.' }
    Write-Host ('Next: open Claude Code in the project, accept the trust dialog, run /verify-layer' + $tail)
}
