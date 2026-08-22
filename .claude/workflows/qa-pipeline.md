# QA Pipeline

> **Status: draft, owned by the GD.** This file records only what is already derivable from the agents'
> own required-input and "Not for" contracts — nothing here was invented. The GD owns the final process
> and the orchestrator that acts on it. Open slots are marked **TODO** rather than guessed at.

Per `.claude/docs/agent-template.md`, sequence, parallelism, retry loops and checkpoints live here and
**never inside an agent file**. Agents are isolated, stateless and cannot dispatch each other — every
`Routed to:` value in a report is a recommendation this pipeline acts on, not an action the agent took.

## The QA group

| Agent | Tier | Runs in | Owns |
|---|---|---|---|
| `qa-lead` | gate (opus) | — | QA scope, exit criteria, QA sign-off verdict |
| `code-reviewer` | gate (opus) | — | Code correctness against the Tech Spec, Shared-Core duplication |
| `security-reviewer` | gate (opus) | — | Secrets, dangerous files, fraudulent logic |
| `qa-automation-engineer` | executor | Unity Editor | Edit Mode + Play Mode tests, network-condition cases |
| `playtest-tester` | executor | Unity Editor | GDD scenarios played by hand, design-flaw detection |
| `performance-qa-engineer` | executor | Dev build on device, or Editor (indicative) | Frame time, GC, memory, draw calls vs. budget |
| `build-verification-tester` | executor | Real platform build only | Artifact startup, critical paths, suite on standalone Player |

Adjacent, outside the QA group: `build-run-engineer` (devops) produces artifacts on an explicit GD request only;
`crash-anr-investigator` (live-ops) handles released-production telemetry; `producer` (leadership) aggregates
reports for the GD without judging them.

## Gate order

Derived from the agents' stated required inputs and boundaries:

1. **Plan** — `qa-lead` turns the Tech Spec + Triage tier into a coverage assignment and exit criteria.
   Depth scales with tier; a Simple-tier change needs a few lines.
2. **Review gates, in parallel** — `code-reviewer` and `security-reviewer` run on the same submission as
   independent gates. Neither waits on the other's verdict, and neither duplicates the other's lens.
   Both require the submission's Implementation Note (`.claude/rules/implementation-note.md`).
3. **Automated tests** — `qa-automation-engineer`, **hard-blocked until the code-review gate passes**. It
   returns `Blocked` on unreviewed code regardless of how small the change is.
4. **Integration testing** — `playtest-tester` against the GDD's scenarios, once the feature is integrated.
   `performance-qa-engineer` where a budget applies.
5. **Build verification** — `build-verification-tester`, only once `build-run-engineer` has produced an
   artifact, which itself happens only on an explicit GD request.
6. **Sign-off** — `qa-lead` issues `Signed off` or `Not signed off` against step 1's exit criteria, from the
   reports produced. It never returns `Signed off` while any gap remains.
7. **Report** — `producer` aggregates for the GD, leading with anything needing a decision.

Steps 3–5 are independent of each other once step 2 passes; nothing in the agent contracts requires them to
be serialized. **TODO (GD):** confirm whether they run concurrently in practice.

## Routing rules the pipeline owns

- **Retry counts and "same submission" identity are the caller's**, never an agent's — every QA agent states
  it cannot hold this across runs.
- **Three strikes** — after the same submission fails review three times, route to `technical-architect` for
  root cause instead of a fourth review pass. The threshold is counted here, not by `code-reviewer`.
- **Design flaws bypass the cycle** — a `playtest-tester` finding classified as a design flaw returns
  `Routed to: gd` immediately, not at the next report cycle. Never re-route it into the engineering loop.
- **Defects return to the owning agent's own gate** — a fix re-enters at step 2, never straight back to the
  executor that found it.

## Checkpoints — TODO (GD)

`technical-architect` and `producer` both reference four GD checkpoints, but only two have any described content
anywhere in the repo:

| Checkpoint | Defined? | What exists today |
|---|---|---|
| Checkpoint 1 | **No** | Referenced only as a rollback target for a Major spec change. |
| Checkpoint 2 | **No** | Referenced only as a rollback target for a Moderate spec change. |
| Checkpoint 3 | Partial | `technical-architect` compiles an Implementation Summary: `Built:`, `Matches spec intent:`, `Known limitations:`. |
| Checkpoint 4 | Partial | `producer` produces the end-of-feature report. |

**TODO (GD):** define what each checkpoint gates, and where QA sits relative to each. Left open deliberately —
guessing these would put invented process into the agents' contracts.

## Tier gating

- **Complex tier** — full pipeline, all four checkpoints, and a `README.md` at the feature root is a hard gate
  before final code-review sign-off, per `.claude/rules/client/feature-documentation.md`.
- **Medium tier** — multi-role but established patterns; no README required.
- **Simple tier** — single role, no new architecture decision; no README required, and `qa-lead`'s plan is brief.
