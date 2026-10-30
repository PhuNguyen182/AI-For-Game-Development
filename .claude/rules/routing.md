# Routing

## Route every input (first match wins; match the work asked for, not the words)
| Input | Route |
|---|---|
| Question, explanation | Answer, or one read-only agent |
| Git task | `git-expert` |
| CI/CD pipeline, failed CI run | `ci-cd-engineer` |
| Crash/ANR from production telemetry | `crash-anr-investigator` (test device: `/investigate-device-crash`) |
| Bug | `/fix` |
| Audit existing code | `/review` |
| Tests or evidence on existing work | `/qa` |
| Technology, vendor or "what exists for X" | `/decide` |
| New project · GDD → backlog · build/release/store | `/new-project` · `/plan-game` · `/release` |
| Change to an open feature past CP2 | `/feature` → change request |
| Change to a closed feature | New work: size it below (a cosmetic tweak is S) |
| Anything else | Size it ↓ |

## Size
| Size | When | Do |
|---|---|---|
| S | One role; judgeable by looking or one test; no new contract | Directly, or one agent. The reply closes it |
| M | 2+ roles, a new contract or screen, or touches a Core assembly | `/feature` |
| L | New Core system, netcode, architecture, project-wide migration, or a direction the GD has not decided | `/feature` with CP1 |

**Risk flag** — credential/signing, real-money IAP, store submission, player PII, save-data migration, published git history, released build, shipped perf budget, server authority/anti-cheat. Flag set: verification means running, never reading, and the gate offer recommends yes. `/release` has its own gate.

Escalate the size the moment the work turns out bigger; never shrink it to skip a step.

## Gates — offered, never imposed
- Review and QA are the GD's choice: one `AskUserQuestion` when the code is built — recommendation first, the concrete cost of skipping stated. Recommend yes for M/L, the risk flag or a Core assembly.
- S work that changed code: offer `/review` only with the risk flag.
- Declined → `Known limitations` ("not reviewed" / "not QA'd"), shown again at CP4. Never re-ask at the same point.
- Always on, not a gate: the supply-chain check before a third-party package lands, the secret hooks, and the per-criterion UTF tests (`/feature` step 4).

## Profile defaults (`CLAUDE.md` → Profile; unset → ask once, write it there)
| | hyper-casual | mid-core | hard-core |
|---|---|---|---|
| CP1 + `critic` | off | L | L, or M with risk flag |
| Tech Spec (else acceptance criteria only) | L | M, L | M, L |
| Netcode / backend / anti-cheat | off | optional | on if multiplayer |
| Perf-budget device | Android low-end | Android mid + oldest iOS | GD-defined |
| Recommended QA | playtest + device smoke | + Core automation | + automation, perf, netcode |

## Checkpoints — GD approves via `AskUserQuestion`
CP1 direction (L) · CP2 spec or acceptance criteria (M, L) · CP3 built vs spec (L) · CP4 closure (M, L).

## Dispatch
- Brief = goal, acceptance criteria, size + flag, profile, feature file path or bug id, files in scope, earlier agents' outputs, `mem q` hits that bear on it (id + path). Agents see only the brief and the disk.
- One Editor-holding agent at a time. Read-only agents may run in parallel, and so may lane A agents (worktree, no Editor; `/feature` step 4). Never end your turn while a dispatch is still running — a headless session is not woken by it, and the agent dies holding the Editor.
- An agent's `Next:` is a recommendation; you act on it.
- `git-expert` runs on Sonnet; dispatch it with `model: opus` for forensics, recovery or a radius 3 operation.

## Stop rule
- Attempts per dispatch: S 2, M 3, L 4; `/fix` sizes by what the fix touches; other unsized routes 2.
- Round caps, failed rounds counted in the state file: review 3 · QA sign-off 2 · per bug 2 · feature rework M 6, L 8 (work sent back after any gate, CP3 drift or a reopened bug). Hook `round-cap.ps1` also counts failed gates and `Failed` returns itself (per session when no feature or bug is named) and blocks dispatches past a cap.
- Same step fails twice for the same cause (repeated findings, same failing test, reopened bug), or a counter reaches its cap → `technical-architect` root-causes once → the owner gets one more dispatch → fails again → stop. Report to the GD: what was tried, last verified state, next best action.
- `Infeasible:` in a return (a budget, platform, engine or spec limit no retry can change) → no retry; `technical-architect` confirms it → GD: drop, waive the constraint, or change direction.
- The GD may order another round; state the cost first, record "extra round: <counter> +n" under `GD decisions` (or in the bug record), raise that cap.

## State (main session is the only writer)
- `.workflow/features/<slug>.md` per M/L feature — template in `/feature`. `.workflow/bugs.md` — bug index.
- Resume a session from the feature file's `CP:` line.
