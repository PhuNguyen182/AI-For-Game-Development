# SessionStart: list in-flight features so a new session can resume them.
$root = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { (Get-Location).Path }
$dir = Join-Path $root '.workflow/features'
if (-not (Test-Path $dir)) { exit 0 }

$open = foreach ($f in Get-ChildItem $dir -Filter *.md) {
    $text = Get-Content $f.FullName -Raw -Encoding UTF8
    if ($text -match '(?m)^- Status:\s*Open\b') {
        $cp = if ($text -match '(?m)^- CP:\s*(.+)$') { $Matches[1].Trim() } else { '?' }
        "- $($f.BaseName) - CP: $cp"
    }
}
if ($open) {
    "In-flight features (.workflow/features/). Resume with /feature <slug>:"
    $open
}
exit 0
