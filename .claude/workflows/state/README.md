# Workflow State

The cross-run state no agent can hold — agents are stateless, cannot count their own rounds, and cannot see each
other's returns. Owned by `orchestrator.md`, written whenever a counter, checkpoint or gate answer changes, before
the next dispatch (I4).

## Where it lives — never under `.claude/`, never inside the Unity project

`.claude/` is the framework, copied unchanged into every project; this folder holds only these rules and the
templates. Any other file appearing here during a run is a defect, and `tools/verify-workflow-layer.ps1` fails on
it. State also stays out of `Assets/`: writing there reimports, which would make every state write an Editor holder
(I3).

| State | Path |
|---|---|
| One feature's run state, GD decisions, gaps and counters | `<state-root>/features/<slug>/LEDGER.md` — from `templates/feature-ledger.md` |
| One feature's test cases and bugs, in full | `<state-root>/features/<slug>/BUGS.md` — from `templates/feature-bugs.md` |
| One feature's Tech Spec, or its D1–D2 direct notes | `<state-root>/features/<slug>/SPEC.md` |
| Each submission's Implementation Note, written as it is assembled | `<state-root>/features/<slug>/notes/S<n>.md` — `<state-root>/direct/S<n>.md` with no feature |
| The project's track, in-flight index, gate debt, gated-direct counters, work with no feature, standalone runs, project-wide patterns, both locks | `<state-root>/project-state.md` |
| The project-wide bug index, the only place bug IDs are allocated, and bugs with no feature | `<state-root>/bug-log.md` |
| One row per closed or abandoned feature — what the layer's constants actually cost | `<state-root>/calibration.md` |

**`<state-root>` is `.workflow/` at the project root** unless the project's `CLAUDE.md` names another path. Commit
it. Copy from `templates/`; never point a live record back into `.claude/`. The first run with something to record
creates it; a direct change that records nothing creates nothing.

The slug names the feature, in kebab-case, from the architect's classification; its feature root — where the code
and the feature documents live — is recorded in the ledger and may move at CP1 without the slug changing. Never
invent a second slug for a feature that has a ledger. Implementation decisions live in the feature root's
`DECISIONS.md`, written by the implementing agents (`.claude/standards/client/feature-documentation.md`); the GD's
decisions — direction, accepted risks, standards — live in the ledger, written by the orchestrator.

## Bugs — one writer, two files

The orchestrator is the only writer of `bug-log.md` and every `BUGS.md`. Agents propose; they never edit either
file and never invent an ID. **The record in `BUGS.md` is the truth**; where the index disagrees — a session
stopped between writes — correct the index from it.

- **Allocating an ID** is the one write that starts in the index: re-read `bug-log.md` immediately before writing,
  take `Next ID`, write the index row and the incremented `Next ID`, then the record. An index row with no record
  gets one from the return that proposed it, or is marked `Void — allocation interrupted` and never reused. A
  duplicate ID found later — two sessions raced — is fixed by renumbering the bug opened second, with a history row
  naming the old ID. Every later change writes the record first, then the index.
- A QA finding or a GD report (G47) opens a bug; a finding citing an existing ID is evidence on it — and reopens it
  when it is `Closed` or `Accepted unverified`.
- A submission whose Implementation Note lists a bug under `Fixes:` moves it to `Fixed` once every gate the GD
  authorised for that work has cleared it. Only a QA verification closes or reopens; only the GD rules `Won't fix`
  or `Accepted unverified` (G9) — and only the GD sends a `Won't fix` bug back to `Open`.
- A test a return names as guarding a bug fills that bug's `Regression test:`. Every QA run replaces the
  `Latest result` of each case it covered.
- **A feature that is `Abandoned`** (G10) marks its unsettled bugs `Won't fix — abandoned with the feature`.
- **An unattached bug** has no CP4: the gate offer ending its fix's lane (G13, G14) also offers its verification at
  `qa-pipeline.md` **E4** and `Accepted unverified` beside it; an **E4** run that leaves one unsettled asks G66.

Statuses, settled and unsettled: `.claude/standards/qa/defect-reporting.md`. The reopen bound: B6.

## Locks

The Editor lock (I3) and the device lock (I7) live in `project-state.md`. A claim is needed only where something
else could contend: if `project-state.md` does not exist, nothing has ever claimed a lock, and a lone direct edit
proceeds without creating it.

`Claim expires` is written at claim time — the expected duration, generously rounded. Past it the lock is suspect,
not free. Reclaim (I9) in this order, stopping at the first step that answers:

1. **Is the holder still running?** A dispatch in flight in this session holds its lock whatever the clock says.
2. **Does the resource answer?** The Editor via `unity status` (`unity-tooling-preference.md`); a device via
   `adb devices`. Idle and answering means nobody is driving it — unless the holder is another session, which only
   the GD can release.
3. **Ask the GD** (G17), naming the holder, the claim time and what is waiting.

Record the reclaim beside the lock: who held it, when, and which step answered. Whatever the stale holder produced
is unverified — inspect real state before the next claim (`execution-loop.md`, safe retry).
