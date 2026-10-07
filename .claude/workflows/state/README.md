# Workflow State

The cross-run state no agent can hold — agents are stateless, cannot count their own rounds, and cannot see
each other's returns. Owned by `orchestrator.md`, written whenever a counter, checkpoint or gate answer
changes, before the next dispatch (I4).

## Where it lives — never under `.claude/`

`.claude/` is the framework, copied unchanged into every project; this folder holds only these rules and the
templates. Any other file appearing here during a run is a defect, and `tools/verify-workflow-layer.ps1` fails
on it.

| State | Path |
|---|---|
| One feature's decisions and run state | `<feature-root>/LEDGER.md` — `## Decisions` and `## Run state` |
| In-flight index, gate debt, gated-direct counters, standalone decisions, project-wide patterns, both locks | `<state-root>/project-state.md` |
| One row per closed or abandoned feature — what the layer's constants actually cost | `<state-root>/calibration.md` |

**`<state-root>` is `.workflow/` at the project root** unless the project's `CLAUDE.md` names another path.
Commit it. Copy from `templates/`; never point a live record back into `.claude/`.

One ledger per feature, never a shared one. The feature root comes from the architect's classification; when
CP1 moves the root, the ledger moves with it and the move is recorded in `## Decisions`. Work with no feature
root has no ledger — its counters live in `project-state.md` until it escalates.

The slug is the feature root's name in kebab-case. Never invent a second slug for a feature that has a ledger.

## Reclaiming a stale lock — I9

`Claim expires` is written at claim time — the expected duration, generously rounded. Past it the lock is
suspect, not free. Reclaim in this order, stopping at the first step that answers:

1. **Is the holder still running?** A dispatch in flight in this session holds its lock whatever the clock
   says.
2. **Does the resource answer?** The Editor via `unity status` (`unity-tooling-preference.md`); a device via
   `adb devices`. Idle and answering means nobody is driving it.
3. **Ask the GD** (G17), naming the holder, the claim time and what is waiting.

Record the reclaim beside the lock in `project-state.md`: who held it, when, and which step answered. Whatever
the stale holder produced is unverified — inspect real state before the next claim (`execution-loop.md`, safe
retry).
