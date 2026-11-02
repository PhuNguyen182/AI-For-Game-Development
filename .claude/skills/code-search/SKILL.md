---
name: code-search
description: "`xerj search`, `xerj def` BM25 passages instead of repo-wide Grep. Use before any search across the project."
user-invocable: false
---

# code-search

- **Session start line:** one line is printed: `Search: XERJ up, prefix <p>` · `XERJ installed, node down` · `Grep`.
- **Loopback only:** a `XERJ_URL` on another machine counts as no XERJ; queries and file contents never leave this one.

## XERJ up
| Need | Command |
|---|---|
| Passages for plain words | `xerj search "<words>" --prefix <p> -k 5` (`--full 1200` for longer passages) |
| Where a symbol is defined | `xerj def <Symbol> --prefix <p>` (`--kind class`, `--lang csharp`) |
| Then | `Read` the file:line it returns — only that range |

- **Ranking:** lexical; use the words the code uses (identifiers, log text), not a description.
- **Freshness:** the index is refreshed incrementally at session start; recent edits may lag, so read the file before relying on a hit.
- **Hidden folders:** `.claude/`, `.workflow/`, `.memory/` are never indexed; Grep them, or use skill `mem` for memory and docs.
- **Guard:** the `search-guard` hook denies a repo-wide content Grep while XERJ is up; Grep on a file, a folder two levels deep, or for file lists stays allowed.
- **Never:** `xerj feedback`, `xerj share` or `xerj init`; they publish data or rewrite agent files.
- **Approval:** before any of the three, `AskUserQuestion` in the main session, `Needs-decision` when dispatched.

## XERJ down or absent
- **Fallback:** Grep / Glob, narrowest path first.
- **Starting a node:** the GD's call: `xerj --data-dir ~/xerj-data` (data dir outside the repo).
