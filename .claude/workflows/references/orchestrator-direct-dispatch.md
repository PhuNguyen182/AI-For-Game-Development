# Direct Dispatch — Modes 2 and 3

> **What happens when one agent is dispatched on its own, and what to do with what it returns.** Split out
> of `orchestrator.md` under the promotion rule in `client/feature-documentation.md`: both sections below are
> read only once a mode-2 or mode-3 dispatch is already the chosen lane, never while sizing an input.

## Direct dispatch — the two classes

Derived from each agent's `tools:` frontmatter, the hard sandbox — the same source `feature-development.md`
step 2 and `qa-pipeline.md` step 2 already use for their serialisation rules.

| Class | Who | Rule |
|---|---|---|
| **A — leaves no source** (14) | No `Write`/`Edit`. Reports, measurements, verdicts, build artifacts | Direct dispatch is their **normal** mode. No debt, nothing owed |
| **B — writes source** (14) | Holds `Write`/`Edit` | `technical-architect` writes specs, gated at CP2 rather than by review; `rd-engineer` marks its output disposable. The other **12** accrue review debt |

**A mode-3 dispatch that writes source owes the gate offer, not the gate.** Review and QA are optional, per
`optional-gates.md` — what is owed is the *ask*, with the cost of skipping stated. The GD's answer lands in
`<state-root>/project-state.md` either way: **unoffered** while the ask is still owed, **declined** once
they said no.

**Gate debt is recorded, never enforced.** It blocks no dispatch and settles in batch whenever the GD opts
in. Recording costs nothing — it is the difference between knowing what no gate has seen and not knowing.

**Both global locks live here.** 10 agents hold `mcp__<server>__*` Editor tools against one process; two also
drive one physical device over adb (invariant **I7**). Two holders of the same lock never run at once, whatever
mode started each — the case no single pipeline can see, and `feature-development.md`'s *"no orchestrator to arbitrate"*.

## Acting on `Routed to:` with no pipeline running

Inside a run, that pipeline's own routing table governs. These are the fallbacks for modes 2 and 3.

| Return | Action |
|---|---|
| `Blocked` | Supply exactly the input named. Never retry with a guess — `Blocked` is a correct result |
| `Rejected`, `Routed to: <peer>` | Misdispatched. Re-dispatch to the named agent; never argue it back |
| `Needs-decision`, `Routed to: gd` | To the GD now. A `playtest-tester` design flaw is I5 — immediately, never held |
| `Needs-decision`, `Routed to: cto` | `research-decision.md` step 0 first. `cto` is barred from returning open options, so entering it without a candidate set leaves it nothing to decide |
| `Needs-decision`, `Routed to: rd-engineer` | Ask the GD. The spike needs an explicit summon; a recommendation is never converted into a dispatch |
| `Needs-decision`, `Routed to: technical-architect` | The spec has the gap. If no spec exists, the input was mis-sized — escalate to `feature-intake.md` **E1** |
| `Needs-decision`, `Routed to: git-expert` or `ci-cd-engineer` | Dispatch in mode 3. Neither is reached by sizing — a git or CI/CD task the router sees is a chore lane row until the GD names the agent |
| `Done` carrying `Config required:` or `Risks flagged:` | A `Done` can still need the GD. Forward it; never read it as "continue" |
| Anything with a `Verdict:` | Read `Verdict:`, never `Status:` — a review requesting changes still returns `Status: Done` |
