---
name: code-search
description: "XERJ search (`xerj search`, `xerj def`: BM25 passages, go-to-definition) instead of a repo-wide Grep when the session-start line says XERJ is up. Use before any search across the project."
user-invocable: false
---

# code-search

Session start prints one line: `Search: XERJ up, prefix <p>` · `XERJ installed, node down` · `Grep`.
Loopback only: a `XERJ_URL` on another machine counts as no XERJ — queries and file contents never leave this one.

## XERJ up
| Need | Command |
|---|---|
| Passages for plain words | `xerj search "<words>" --prefix <p> -k 5` (`--full 1200` for longer passages) |
| Where a symbol is defined | `xerj def <Symbol> --prefix <p>` (`--kind class`, `--lang csharp`) |
| Then | `Read` the file:line it returns — only that range |

- Ranking is lexical: use the words the code uses (identifiers, log text), not a description.
- Index is refreshed incrementally at session start; recent edits may lag, so read the file before relying on a hit.
- Hidden folders (`.claude/`, `.workflow/`, `.memory/`) are never indexed: Grep them, or use skill `mem` for memory and docs.
- The `search-guard` hook denies a repo-wide content Grep while XERJ is up; Grep on a file, a folder two levels deep, or for file lists stays allowed.
- Never `xerj feedback`, `xerj share` or `xerj init`: they publish data or rewrite agent files. Ask the GD first.

## XERJ down or absent
Grep / Glob, narrowest path first. Starting a node is the GD's call: `xerj --data-dir ~/xerj-data` (data dir outside the repo).
