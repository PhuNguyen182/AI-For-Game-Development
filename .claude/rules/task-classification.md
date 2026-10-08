# Shared — Task Intake & Classification

Applies to: every agent and the orchestrator, on every input — a feature request, a one-line question, a direct
dispatch, or a returning defect.

An input never states how hard it is or what it costs to get wrong. Difficulty is not consequence — the five axes
below keep one from standing in for the other. Classifying costs no agent call: it is a judgment from the request
itself. **This is the project's only task classification.** Which lane an input takes is `orchestration.md` /
`workflows/orchestrator.md`; what the rigor buys is `effort-allocation.md`; what happens when an attempt falls
short is `execution-loop.md`.

## Step 1 — the requirement baseline

| Class | Meaning | Rule |
|---|---|---|
| **H** — Hard | Explicit non-negotiable: a stated platform, a GD-fixed budget (G12), a rule file, a safety/security boundary | Violating without authorization is a failed task |
| **M** — Material | Needed for the result to be useful at all | Dropping silently fails the task; unresolved-but-stated does not |
| **Q** — Quality | Non-functional threshold — frame-time budget, style rules, coverage | Must meet the applicable threshold |
| **P** — Preference | Desirable but tradeable | May drop, with the reason stated |

Past a trivial change, also establish the objective, deliverables, scope boundaries, material assumptions,
dependencies, what "done" means, and any GD-stated limit.

**No silent scope reduction**: never drop a hard part, redefine a requirement as easier, treat a material one as
optional, answer with advice instead of doing the work, or call a partial artifact complete.

**Conflicts resolve in order**: platform/safety/security → the GD's explicit hard constraint → the more specific
requirement → the more recent explicit one → the accepted baseline (Tech Spec, GDD, rules). An unresolved material
conflict is never settled by picking the easier reading: proceed on the untouched scope, state the conflict, never
fabricate the missing input. `Status: Blocked` on a genuinely missing input is correct.

## Step 2 — the five axes, classified independently

**D — Difficulty**

| D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|
| Read a file, answer from a rule, rename a field, adjust one serialized value | Known-shape change across a few files, one role, no new contract | Several dependencies/edge cases/design choices — several roles, a new screen bound to Core state | Architecture or interacting dependencies — prediction/reconciliation, a new Shared Core system, a cross-layer refactor | System-level — netcode foundation, Job System/Burst/DOTS adoption, a project-wide migration |

**C — Criticality** (consequence if wrong)

| C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| Local/cheap — a comment, scratch file, throwaway query | Limited rework — a wrong Editor setting caught next run | Material — a `Game.Core.*` rule causing client/server divergence, wrong behavior on a normal path | High — a production build, released content, an economy/progression path, save-data migration, a shipped perf budget | Critical — a credential/PII, real-money IAP/billing, a store submission, server authority/anti-cheat, published git history |

**U — Uncertainty** — U2/U3 are never asserted as fact; resolve, bound, state the assumption, or limit the
conclusion to what it does not touch.

| U0 | U1 | U2 | U3 |
|---|---|---|---|
| Spec, inputs, dependencies established | Minor ambiguity, unlikely to change the result | A missing Tech Spec clause, unstated perf budget, unknown track state, unconfirmed C# version | A consequential unknown — the GDD has not decided the rule, or the work depends on an unverified API shape |

**R — Reversibility**

| R0 | R1 | R2 | R3 |
|---|---|---|---|
| No state change — review, research, a report | A working-tree edit — scenes and prefabs included, git restores them — or a local commit | A pushed commit, a distributed build | Rewritten published history, a store submission, a leaked credential, deleted data |

**X — Operational exposure** — the one Editor and the one device are locked at any X (I3, I7): two agents on either
is a conflict before it is a risk, and the lock — not a higher tier — is what prevents it.

| X0 | X1 | X2 | X3 |
|---|---|---|---|
| Analysis or a local document | The working tree, an Editor change to version-controlled assets — by CLI or MCP | `git push`, a CI pipeline definition, the physical test device | A store submission, production/live config, a destructive device operation, real money or player data |

## Step 3 — the assurance tier

```text
D1→A1  D2→A2  D3→A3  D4→A4  D5→A5
C0→A1  C1→A2  C2→A3  C3→A4  C4→A5
R0→A1  R1→A2  R2→A4  R3→A5
X0→A1  X1→A2  X2→A3  X3→A5
```

The tier is the **highest** of D, C, R and X — never an average. Then U: U0/U1 no change; U2 one tier higher unless
resolved before execution; U3 → A5 until resolved or explicitly bounded.

Never inflate a tier to look thorough, and never deflate one because the work looks easy. State it in one line only
at A3+ or when an unexpected axis set it (G1); at A1/A2, say nothing and work. Never ask the GD to confirm it
(G20).

## Step 4 — what each axis buys

| Axis | Buys | Never buys |
|---|---|---|
| **D** | The **shape**: roles, whether a Tech Spec is written, which checkpoints fire | Extra verification on its own |
| **C, R, X** | The **depth**: verification level, evidence strength, care per attempt | A checkpoint, a plan document, or an extra agent |
| **U** | The **direction gate**: an unresolved consequential unknown is what CP1 settles | Anything once resolved — U is spent down |

**Shape, set by D** (U3 fires CP1 at any D; a resolved U2 adds nothing). Checkpoints are defined in
`orchestration.md` → *Terms*:

| D | Roles | Tech Spec | CP1 | CP2 | CP3 | CP4 |
|---|---|---|---|---|---|---|
| D1–D2 | one | no — direct notes | — | — | merged into CP4 | ✔ |
| D3 | several | ✔ | — | ✔ | ✔ | ✔ |
| D4–D5 | several, often cross-track | ✔ | ✔ | ✔ | ✔ | ✔ |

**Feature-root documents key to A, not D** — a feature earns documentation because getting it wrong is expensive.
The floors and triggers are `.claude/standards/client/feature-documentation.md`'s alone.

**Depth, set by A** — the single home of the verification floor:

| A | Verification floor | Scored by `assurance-evaluator` |
|---|---:|---|
| A1 | V1 | no — unless the GD asks (G80) |
| A2 | V1, or V2 once it changes state | no — unless the GD asks (G80) |
| A3 | V2 | ✔ |
| A4 | V3 | ✔ |
| A5 | V4 | ✔ |

**Attempt budget, set by D** — the single home: **D1–D2 → 2, D3 → 3, D4 → 4, D5 → 5** total attempts, Attempt 1
included. A ceiling, never a target. Criticality raises care per attempt, never the count.

A feature is classified at intake and held in its ledger; it is reclassified only where a pipeline names the
trigger — research moving an axis, a change request, a classification found wrong — and every move is appended to
`Tier history:`. A step inside may classify **higher** for its own dispatch, never lower, and says why; the
feature's tier stays put.
