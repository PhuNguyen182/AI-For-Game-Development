---
name: mem
description: "Zero-Mem CLI: query sessions (T), notes (M), docs (K); save lessons. Use before work in an unfamiliar area."
user-invocable: false
---

# mem — Zero-Mem memory

- **Refresh:** the index refreshes on every command; after a pull, just query.
- **Python:** `<python>` is the interpreter named on the session-start line.

## References
- **[schema.md](references/schema.md):** a hit ranks oddly, a trace needs a hand edit, a file format matters, or tests.

## Scripts
- **[mem.py](scripts/mem.py):** run `<python> -I "${CLAUDE_SKILL_DIR}/scripts/mem.py" <cmd>` → the commands under Query and Write.

## Layers
| Layer | Id | Path, from the id | Written by |
|---|---|---|---|
| T trace | `t:<date>-<sid8>#<line>` | `.memory/traces/YYYY/MM/<date>-<sid8>.jsonl`, file line `<line>` | Stop hook; never tool output |
| M note | `m:<type>/<slug>` | `.memory/notes/<type>/<slug>.md` | `add`, when the GD confirms a mistake or preference |
| K knowledge | `k:<path>#<heading>` | `<path>` at the hit's `:<line>`; docs matched by `.memory/sources.txt` | nobody new — one fact, one home |

- **Note types:** `feedback` (how the GD wants work done) · `lesson` (error prevention) · `project` (facts not in code or docs) · `reference` (external pointers).

## Query
| Need | Command |
|---|---|
| Ranked hits | `q "<words>" [-l MK] [-t lesson] [-e <entity>] [--since 2026-10-01] [-n 8] [--budget 1200]` |
| Entry with its file path | `get <id> [--full]`; a trace turn with neighbours: `get <id> --ctx 2` |
| What touches a file | `for <path>` |
| Entity card (mentions, co-occurring entities) | `ent <name>` |
| Past sessions | `sessions [--since D]` |

- **Query words:** file names, symbols, `BUG-0001`, agent/skill names. Vietnamese works without diacritics.
- **Hits:** snippets; `get` only what you will use.
- **`(+N more)`:** from `q`/`for`: raise `-n`/`--budget` or narrow with `-l`/`-t`/`-e`.
- **Superseded:** `--all` includes superseded entries.

## Write
- **Add:** `add <type> <slug> --desc "<one line>" [--tags a b] [--paths <file> ...] --body "<fact. **Why:** ... **How to apply:** ...>"`.
- **One fact per note:** same fact changed → edit that note; replaced → new note, old one `status: superseded`, `superseded_by: <type>/<slug>`.
- **Secrets and PII:** never a secret or player PII (`add` refuses secret shapes). `lint` before committing `.memory/`.
- **Secret in a trace:** replace it in that line by hand, then `lint`. Already committed → rule core.md → Security.
- **Traces:** never summarise or rewrite them; never call an LLM to organise memory.
- **`MEM_CAPTURE=0`:** skips capture for a session.
