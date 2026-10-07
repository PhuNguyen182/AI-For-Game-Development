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
| One feature's test cases and bugs, in full | `<feature-root>/BUGS.md` — from `templates/feature-bugs.md` |
| The project-wide bug index, the only place bug IDs are allocated, and bugs with no feature | `<state-root>/bug-log.md` |
| One row per closed or abandoned feature — what the layer's constants actually cost | `<state-root>/calibration.md` |

**`<state-root>` is `.workflow/` at the project root** unless the project's `CLAUDE.md` names another path.
Commit it. Copy from `templates/`; never point a live record back into `.claude/`.

One ledger per feature, never a shared one. The feature root comes from the architect's classification; when
CP1 moves the root, the ledger moves with it and the move is recorded in `## Decisions`. Work with no feature
root has no ledger — its counters live in `project-state.md` until it escalates.

The slug is the feature root's name in kebab-case. Never invent a second slug for a feature that has a ledger.

## Bugs — one writer, two files

The orchestrator is the only writer of `bug-log.md` and every `BUGS.md`, and updates a feature bug in both in the
same write. Agents propose; they never edit either file and never invent an ID:

- A QA agent's finding → the orchestrator allocates the next ID in `bug-log.md`, adds the index row, and writes
  the full record in the feature's `BUGS.md` (or under *Unattached bugs* when there is no feature). A finding
  citing an existing ID is evidence on that bug; one citing a closed bug reopens it.
- A GD-reported defect (G47) opens a bug the same way, `Opened by: gd`.
- An implementing agent naming a bug ID as fixed → `Fixed`, once review clears the fix (at once where the GD declined review). Only a QA verification return closes or reopens;
  only the GD marks `Won't fix` (G9). Each move is a row in the bug's history, with its evidence.
- Every QA run that covers a test case replaces that case's `Latest result`.

Statuses and who may cause each: `.claude/standards/qa/defect-reporting.md`. The reopen bound: B6.

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
