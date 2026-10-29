# mem — schema and ranking

Synthesized from `../scripts/mem.py`; paths in `../SKILL.md` → Layers.

## Files (committed)
- Trace line: `{n, ts, role, agent?, text, tools?, files?}`; `n` = transcript turn, while an id's `#<line>` = file line. Roles: `user` · `assistant` · `brief` (Agent prompt) · `agent` (agent return, task notification) · `answer` (AskUserQuestion result).
- Capture drops: tool output, thinking, compaction summaries, sidechains, harness tags (`system-reminder`, `ide_*`, `bash-stdout`), files outside the repo, the second copy of a queued command.
- Text: the project root → `<root>`, the home folder → `~`, emails and `.claude/hooks/secret-patterns.txt` matches → `[REDACTED:<kind>]` (a private key with its whole body). Turns over 20000 chars are truncated. No patterns file → nothing is captured.
- Append-only past the highest `n`: a hand edit or deletion of an earlier line is kept.
- `sources.txt`: K globs; `!` excludes; `**` spans folders; `{a,b}` alternatives.

Note frontmatter:
```
name: <slug = file name>      description: <one line>      type: <folder>
tags: [a, b]                  paths: [<files it applies to>]
status: active | superseded   superseded_by: <type>/<slug>  updated: YYYY-MM-DD
```

## Index (`.memory/.index/mem.db`, gitignored, rebuilt from files)
- `doc` (id, layer, type, path, line, title, status, ts, session, turn, hash) · `fts` FTS5 `porter unicode61 remove_diacritics 2` over title/tags/body.
- `entity` (name, kind, stem) · `mention` (entity, doc): the entity-context graph.
- `file` (path, mtime, size): a changed or deleted source is re-read or dropped. Sources: `git ls-files --cached --others --exclude-standard` plus `.memory/` traces and notes on disk; other ignored folders are never read.
- K docs are chunked by `#`-`###` headings (outside code fences), max 6000 chars. A doc whose header says `Status: Superseded` is indexed as superseded.

## Entities (regex, no model)
File paths (generic names like `SKILL.md` keep the parent folder) · PascalCase and `Game.*` types · `BUG-####`, `ADR-n`, `CP1-4` · `com.*` packages · agent, skill and feature names (one-word names only as `/name` or `` `name` ``).

## Ranking
1. FTS5 BM25 (title 8, tags 4, body 1), terms OR-ed with prefix match.
2. Graph: docs mentioning entities linked from the query (exact name, or a stem shared by at most 3 entities; entities in more than 200 docs ignored), then docs of the 5 most co-occurring entities at weight 0.4.
3. Reciprocal-rank fusion (k = 60) x layer prior M 1.3 · K 1.0 · T 0.8 x trace half-life 90 days.
4. Calibration: one copy per content hash, at most 2 turns per session and 3 chunks per file, output cut at `--budget` characters.

Tests: `python -I .claude/skills/mem/scripts/test_mem.py`.
