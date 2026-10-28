---
name: mem
description: "Zero-Mem store: query past sessions (T), curated notes (M) and indexed docs (K) with a deterministic CLI — no LLM, nothing preloaded. Use before work in an unfamiliar area, and to save a confirmed lesson or GD preference."
user-invocable: false
---

# mem — Zero-Mem memory

Run `<python> -I .claude/skills/mem/scripts/mem.py <cmd>`; the session-start line prints `<python>` for this machine.
Index (`.memory/.index/mem.db`, SQLite FTS5) refreshes itself before every command: right after a pull or merge, just query.

## Layers — every hit is labelled
| Layer | Id | Source | Written by |
|---|---|---|---|
| T trace | `t:<date>-<sid8>#<turn>` | `.memory/traces/YYYY/MM/*.jsonl` | Stop hook: prompts, replies, agent briefs/returns, GD answers, files touched. Never tool output |
| M note | `m:<type>/<slug>` | `.memory/notes/<type>/<slug>.md` | `mem add`, when the GD confirms a mistake or preference |
| K knowledge | `k:<path>#<heading>` | docs matched by `.memory/sources.txt`, in place | nobody new — one fact, one home |

Note types: `feedback` (how the GD wants work done) · `lesson` (error prevention) · `project` (facts not in code or docs) · `reference` (external pointers).

## Query
| Need | Command |
|---|---|
| Ranked hits | `q "<words>" [-l MK] [-t lesson] [-e <entity>] [--since 2026-10-01] [-n 8] [--budget 1500]` |
| Full entry | `get <id>`; a trace turn with neighbours: `get <id> --ctx 2` |
| What touches a file | `for <path>` |
| Entity card (mentions, co-occurring entities) | `ent <name>` |
| Past sessions | `sessions [--since D]` |

- Query words, file names, symbols, `BUG-0001`, agent/skill names. Vietnamese works without diacritics.
- Hits are snippets: `get` only what you will use. `--all` includes superseded entries.

## Write
- `add <type> <slug> --desc "<one line>" [--tags a b] [--paths <file> ...] --body "<fact. **Why:** ... **How to apply:** ...>"`.
- One fact per note. Same fact changed → edit that note; replaced → new note, old one `status: superseded`, `superseded_by: <type>/<slug>`.
- Never a secret or player PII (`add` refuses secret shapes). `lint` before committing `.memory/`.
- A secret in a trace: replace it in that line by hand (capture only appends, so the edit stays), then `lint`. Already committed → rule core.md → Security.
- Never summarise or rewrite traces; never call an LLM to organise memory.
- `MEM_CAPTURE=0` in the environment skips capture for a session.

## Reference
Schema, ranking and entity rules: `references/schema.md`. Tests: `python -I .claude/skills/mem/scripts/test_mem.py`.
