#!/usr/bin/env python3
"""List the lines no test executed, from Unity Code Coverage results.

Merges every OpenCover XML under <results> (all modes, all sessions): a line
counts as covered when any sequence point on it ran in any file. Line level
only: the package does not implement branch coverage.

Exit 0: report printed, gaps or not. Exit 2: no results, or git failed; never
read that as "no gaps".
"""
import argparse
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


def fold(path):
    return path.replace("\\", "/").casefold()


def result_files(root):
    return [
        p for p in Path(root).rglob("*CoverageResults_*.xml")
        if any(part.endswith("-opencov") for part in p.parts)
    ]


def load_lines(files):
    """Return {source path: {line: executed}}, merged across files."""
    lines = defaultdict(dict)
    for xml_file in files:
        for module in ET.parse(xml_file).getroot().iter("Module"):
            sources = {f.get("uid"): f.get("fullPath") for f in module.iter("File")}
            for point in module.iter("SequencePoint"):
                source = sources.get(point.get("fileid"))
                if source is None:
                    continue
                hit = int(point.get("vc", "0")) > 0
                for line in range(int(point.get("sl")), int(point.get("el")) + 1):
                    per_file = lines[source]
                    per_file[line] = per_file.get(line, False) or hit
    return lines


def changed_lines(project, ref):
    """Return {repo-relative path: set of lines added or edited since ref}."""
    cmd = ["git", "-c", "core.quotepath=off", "-C", project, "diff", "-U0",
           "--no-color", "--no-ext-diff", ref, "--", "*.cs"]
    done = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if done.returncode != 0:
        raise RuntimeError(done.stderr.strip())
    changed = defaultdict(set)
    current = None
    for text in done.stdout.splitlines():
        if text.startswith("+++ "):
            current = None if text == "+++ /dev/null" else text[6:]
        elif text.startswith("@@") and current:
            match = re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", text)
            start, count = int(match.group(1)), int(match.group(2) or 1)
            changed[current].update(range(start, start + count))
    return changed


def ranges(numbers):
    out, numbers = [], sorted(numbers)
    for n in numbers:
        if out and out[-1][1] == n - 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return ", ".join(str(a) if a == b else f"{a}-{b}" for a, b in out)


def report_all(lines):
    covered = coverable = 0
    for source in sorted(lines):
        per_file = lines[source]
        missed = [n for n, hit in per_file.items() if not hit]
        covered += len(per_file) - len(missed)
        coverable += len(per_file)
        if missed:
            print(f"{source}: uncovered {ranges(missed)} ({len(missed)}/{len(per_file)})")
    print(f"Total lines: {covered}/{coverable} covered")


def report_changed(lines, changed):
    by_fold = {fold(source): source for source in lines}
    executed = coverable = 0
    outside = []
    for path in sorted(changed):
        wanted = "/" + fold(path)
        source = next((by_fold[k] for k in by_fold if k.endswith(wanted)), None)
        if source is None:
            outside.append(path)
            continue
        hits = lines[source]
        touched = [n for n in changed[path] if n in hits]
        missed = [n for n in touched if not hits[n]]
        executed += len(touched) - len(missed)
        coverable += len(touched)
        if missed:
            print(f"{path}: changed, not executed {ranges(missed)} ({len(missed)}/{len(touched)})")
    print(f"Changed lines: {executed}/{coverable} executed")
    for path in outside:
        print(f"Not in results (assembly filtered out, or no coverable line): {path}")


def warn_stale(lines, files):
    newest = max(os.path.getmtime(f) for f in files)
    for source in sorted(lines):
        if os.path.exists(source) and os.path.getmtime(source) > newest:
            print(f"STALE: edited after the last coverage run: {source}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("results", help="the --coverage-output directory")
    parser.add_argument("--changed", metavar="REF", help="report only lines changed since this git ref")
    parser.add_argument("--project", default=".", help="directory inside the git repository (default: cwd)")
    args = parser.parse_args()

    files = result_files(args.results)
    if not files:
        print(f"No coverage results under {args.results}", file=sys.stderr)
        return 2
    lines = load_lines(files)
    if not lines:
        print(f"Results under {args.results} hold no sequence points; check assemblyFilters", file=sys.stderr)
        return 2
    warn_stale(lines, files)
    if not args.changed:
        report_all(lines)
        return 0
    try:
        changed = changed_lines(args.project, args.changed)
    except (RuntimeError, OSError) as error:
        print(f"git diff failed: {error}", file=sys.stderr)
        return 2
    report_changed(lines, changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
