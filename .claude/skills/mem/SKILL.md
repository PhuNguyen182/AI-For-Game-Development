---
name: mem
description: "Zero-Mem store: query past sessions (T), curated notes (M) and indexed docs (K) with a deterministic CLI — no LLM, nothing preloaded. Use before work in an unfamiliar area, and to save a confirmed lesson or GD preference."
user-invocable: false
---

# mem — Zero-Mem memory

Run `<python> -I .claude/skills/mem/scripts/mem.py <cmd>` (`<python>`: session-start line). The index refreshes on every command; after a pull, just query.

| Reference | Read when |
|---|---|
| [schema.md](references/schema.md) | a hit ranks oddly, a trace needs a hand edit, a file format matters, or tests |

## Layers
| Layer | Id | Path, from the id | Written by |
|---|---|---|---|
| T trace | `t:<date>-<sid8>#<line>` | `.memory/traces/YYYY/MM/<date>-<sid8>.jsonl`, file line `<line>` | Stop hook; never tool output |
| M note | `m:<type>/<slug>` | `.memory/notes/<type>/<slug>.md` | `add`, when the GD confirms a mistake or preference |
| K knowledge | `k:<path>#<heading>` | `<path>` at the hit's `:<line>`; docs matched by `.memory/sources.txt` | nobody new — one fact, one home |

Note types: `feedback` (how the GD wants work done) · `lesson` (error prevention) · `project` (facts not in code or docs) · `reference` (external pointers).

## Query
| Need | Command |
|---|---|
| Ranked hits | `q "<words>" [-l MK] [-t lesson] [-e <entity>] [--since 2026-10-01] [-n 8] [--budget 1200]` |
| Entry with its file path | `get <id> [--full]`; a trace turn with neighbours: `get <id> --ctx 2` |
| What touches a file | `for <path>` |
| Entity card (mentions, co-occurring entities) | `ent <name>` |
| Past sessions | `sessions [--since D]` |

- Query words, file names, symbols, `BUG-0001`, agent/skill names. Vietnamese works without diacritics.
- Hits are snippets: `get` only what you will use. `(+N more)` from `q`/`for`: raise `-n`/`--budget` or narrow with `-l`/`-t`/`-e`. `--all` includes superseded entries.

## Write
- `add <type> <slug> --desc "<one line>" [--tags a b] [--paths <file> ...] --body "<fact. **Why:** ... **How to apply:** ...>"`.
- One fact per note. Same fact changed → edit that note; replaced → new note, old one `status: superseded`, `superseded_by: <type>/<slug>`.
- Never a secret or player PII (`add` refuses secret shapes). `lint` before committing `.memory/`.
- A secret in a trace: replace it in that line by hand, then `lint`. Already committed → rule core.md → Security.
- Never summarise or rewrite traces; never call an LLM to organise memory.
- `MEM_CAPTURE=0` skips capture for a session.
