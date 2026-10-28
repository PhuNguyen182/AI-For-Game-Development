# mem — schema and ranking

## Files (committed)
```
.memory/traces/YYYY/MM/<date>-<sid8>.jsonl   one line per turn: {ts, role, agent?, text, tools?, files?}
.memory/notes/<type>/<slug>.md               frontmatter below + body
.memory/sources.txt                          K globs; ! excludes; ** spans folders; {a,b} alternatives
```
Trace roles: `user` · `assistant` · `brief` (Agent prompt) · `agent` (agent return, task notification) · `answer` (AskUserQuestion result).
Capture drops: tool output, thinking, compaction summaries, sidechains, harness tags (`system-reminder`, `ide_*`, `bash-stdout`), files outside the repo, the second copy of a queued command.
Text: the project root → `<root>`, the home folder → `~`, emails and `.claude/hooks/secret-patterns.txt` matches → `[REDACTED:<kind>]` (a private key with its whole body). Turns over 20000 chars are truncated. No patterns file → nothing is captured.
Append-only: each Stop appends turns past the file's line count, so a hand edit to an earlier line is kept.

Note frontmatter:
```
name: <slug = file name>      description: <one line>      type: <folder>
tags: [a, b]                  paths: [<files it applies to>]
status: active | superseded   superseded_by: <type>/<slug>  updated: YYYY-MM-DD
```

## Index (gitignored, rebuilt from files)
- `doc` (id, layer, type, path, line, title, status, ts, session, turn, hash) · `fts` FTS5 `porter unicode61 remove_diacritics 2` over title/tags/body.
- `entity` (name, kind, stem) · `mention` (entity, doc): the entity-context graph.
- `file` (path, mtime, size): a changed or deleted source is re-read or dropped before each command. Sources come from `git ls-files --cached --others --exclude-standard`, so ignored folders are never read.
- K docs are chunked by `#`-`###` headings (outside code fences), max 6000 chars. A doc whose body says `Status: Superseded` is indexed as superseded.

## Entities (regex, no model)
File paths (generic names like `SKILL.md` keep the parent folder) · PascalCase and `Game.*` types · `BUG-####`, `ADR-n`, `CP1-4` · `com.*` packages · agent, skill and feature names (one-word names only as `/name` or `` `name` ``).

## Ranking
1. FTS5 BM25 (title 8, tags 4, body 1), terms OR-ed with prefix match.
2. Graph: docs mentioning entities linked from the query (exact name, or a stem shared by at most 3 entities; entities in more than 200 docs ignored), then docs of the 5 most co-occurring entities at weight 0.4.
3. Reciprocal-rank fusion (k = 60) x layer prior M 1.3 · K 1.0 · T 0.8 x trace half-life 90 days.
4. Calibration: superseded dropped (unless `--all`), one copy per content hash, at most 2 turns per session and 3 chunks per file, output cut at `--budget` characters.
