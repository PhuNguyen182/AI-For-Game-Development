# C9 — live adviser capture (AC9)

- Run by: main session, 2026-11-06, branch `feature/game-production-agent` at bbeb7e1 (hooks as registered in `.claude/settings.json`).
- Thread: `qa-2026-11-06`. Adviser: `game-designer` (model override haiku: smoke test, not a gate).
- No raw trace in this report: probe strings are named, never quoted with their figures.

## Steps and results
| Check | Result |
|---|---|
| First dispatch with `Advisory-Thread: qa-2026-11-06` and a probe figure | Stored as `adv:2.1` by the registered SubagentStop hook (`advisory-capture.ps1`); nothing else in the session ingests |
| `SendMessage` follow-up to the same agent | Agent recalled the word from the first brief: context kept |
| SubagentStop on the continuation | Fired: stored as `adv:3.1`, thread `qa-2026-11-06` |
| `adv.py list --thread qa-2026-11-06` | 2 returns, `adv:2.1` and `adv:3.1` |
| `adv.py rounds qa-2026-11-06` | `game-designer 1` (one follow-up) |
| Session trace `.memory/traces/2026/11/2026-11-05-6a67d61d.jsonl`, grep for both probe tokens and the remembered word | 0 hits each, checked after several Stop captures; 20 pointer lines |
| Hook registration | Proven by the stored rows: `run.ps1` runs the script directly, while these rows came from the live `settings.json` entry |
| Follow-up default in `/product-review` step 5 | Matches the run: continue the same agent with `SendMessage`; fresh dispatch only as fallback |

## Paths
- **Background dispatch:** exercised (this harness runs every Agent dispatch in the background).
- **Foreground dispatch:** not producible in this harness; covered by `test_mem.py` `test_a_foreground_adviser_continued_by_message_leaves_a_pointer`.
- **Earlier spike (2026-11-05):** found SubagentStop firing twice for one return; ingest is now idempotent (`adv.py` digest index).

## Left in the local store
- `adv:1.1` (live check, 2026-11-05), `adv:2.1`, `adv:3.1` (this run). Local, git-ignored, probe text only; kept as evidence. Delete `.memory/advisory/advisory.db` to clear.
