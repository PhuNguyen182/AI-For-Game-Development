# Shared — Task Intake & Classification

Applies to: every agent and the orchestrator, on every input — a feature request, a one-line question, a
direct dispatch, or a returning defect. Like `language-and-comments.md`, this file sits above the
`.claude/rules/<group>/` folders rather than inside one.

Source: `.claude/docs/frame/AAEAS_v4_2_Runtime_Core.md` §§2–4, adapted to this project's roles, tiers and
hazards. Replaces the retired Simple/Medium/Complex triage tier outright — see Step 4. The Full Assurance
Reference beside it is the audit-level expansion — open it only when a classification is genuinely contested,
never as routine input.

An input never states how hard it is or what it costs to get wrong, and both get decided silently by
default otherwise. Two failure modes follow: under-rigor on an easy-looking but costly task (a one-line edit
to a signing config), and over-process on a trivial one (a classification round costing more than a rename).
Difficulty is not consequence — the axes below stop one standing in for the other. Classifying costs no agent
or tool call; it's a judgment from the request itself, stated in one line only when not obvious, so the GD
can correct it at the first turn.

## Relationship to other rules

| File | Owns |
|---|---|
| `orchestration.md` | Which **lane** an input takes — full pipeline, one agent, or handled directly |
| **This file** | The **classification** — the five axes, the A1–A5 tier, what each axis buys |
| `effort-allocation.md` | What that rigor buys, and what it must never buy |
| `execution-loop.md` | What happens when the first attempt is not good enough |
| `.claude/workflows/*` | Acting on the classification — checkpoints, dispatches |

Lane and classification are independent — a direct input can demand the highest rigor, a full-pipeline
feature can have steps needing almost none. **This is the project's only task classification** — the retired
triage tier measured difficulty under a name that read as consequence.

## Step 1 — the requirement baseline

Before substantial work, name what the input asks for:

| Class | Meaning | Rule |
|---|---|---|
| **H** — Hard | Explicit non-negotiable: a stated platform, a GD-fixed budget, a rule file, a safety/security boundary | Violating without authorization is a failed task, never a trade-off |
| **M** — Material | Needed for the result to be useful at all | Dropping silently fails the task; unresolved-but-stated does not |
| **Q** — Quality | Non-functional threshold — frame-time budget, style rules, coverage | Must meet the applicable threshold |
| **P** — Preference | Desirable but tradeable | May drop, with the reason stated |

Past a trivial change, also establish objective, deliverables, scope boundaries, material assumptions,
dependencies, what "done" means, and any GD-stated time/cost limit.

**No silent scope reduction**: never drop a hard part, redefine a requirement as easier, treat a material
requirement as optional, answer with advice instead of doing the work, or call a partial artifact complete.

**When requirements conflict**, resolve in order: platform/safety/security constraints → the GD's explicit
hard constraint → the more specific requirement → the more recent explicit requirement → the accepted
baseline (Tech Spec, GDD, rule files). An unresolved material conflict is never settled by picking the easier
reading — proceed only on the untouched scope, state the conflict, never fabricate the missing input.
`Status: Blocked` on a genuinely missing required input is correct, not a failure, per
`qa/verification-standards.md`.

## Step 2 — the five axes

Classified **independently** — a task is not one number, and the axes disagreeing is the information.

**D — Difficulty** (intrinsic reasoning/implementation complexity)

| D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|
| Read a file, answer from a rule, rename a field, adjust one serialized value | A known-shape change across a few files, one role, no new contract | Several dependencies/edge cases/design choices — several roles, a new screen bound to Core state | Architecture or interacting dependencies — client prediction/reconciliation, a new Shared Core system, a cross-layer refactor | System-level — netcode foundation, Job System/Burst/DOTS adoption, a project-wide migration |

**C — Criticality** (consequence if wrong) — C4 is where `security.md` already applies with no exemption;
this axis is that rule's general form.

| C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| Local/cheap — a comment, scratch file, throwaway query | Limited rework — a wrong Editor setting caught next run | Material — a `Game.Core.*` rule causing client/server divergence, wrong behavior on a normal path | High — a production build, released content, an economy/progression path, save-data migration, a shipped mobile perf budget | Critical — a credential/PII, real-money IAP/billing, a store submission, server authority/anti-cheat, published git history |

**U — Uncertainty** (what unresolved could change the answer) — U2/U3 are never silently asserted as fact;
resolve, bound, state the assumption, or limit the conclusion to what it doesn't touch.

| U0 | U1 | U2 | U3 |
|---|---|---|---|
| Spec, inputs, dependencies established | Minor ambiguity, unlikely to change result | A missing Tech Spec clause, unstated perf budget, unknown track state, unconfirmed C# version | A consequential unknown — GDD hasn't decided the rule, or the work depends on an unverified API shape |

**R — Reversibility** (how hard recovery is)

| R0 | R1 | R2 | R3 |
|---|---|---|---|
| No state change — review, research, a report | A working-tree edit, a local branch commit | A pushed commit, a distributed build, a shared scene/prefab mutation | Rewritten published history, a store submission, a leaked credential, deleted data |

**X — Operational exposure** (how far the action reaches) — X2 is where `orchestration.md` I3/I7 bite: one
Editor and one device, project-wide; two agents at X2 on the same resource is a conflict before a risk.

| X0 | X1 | X2 | X3 |
|---|---|---|---|
| Analysis or a local document | The working tree, a sandboxed Editor change | `git push`, the project's single Unity Editor over MCP, a CI pipeline definition, the one physical test device | A store submission, production/live config, a destructive device operation, anything touching real money/player data |

## Step 3 — the assurance tier

```text
D1→A1  D2→A2  D3→A3  D4→A4  D5→A5
C0→A1  C1→A2  C2→A3  C3→A4  C4→A5
R0→A1  R1→A2  R2→A4  R3→A5
X0→A1  X1→A2  X2→A3  X3→A5
```

The tier is the **highest** required by D, C, R or X — never an average or whatever's convenient. Adjust for
uncertainty: U0/U1 → no change; U2 → one tier higher unless resolved before execution; U3 → A5 until resolved
or explicitly bounded.

**Never inflate the tier** to look thorough, justify more tool calls, produce more documentation, or avoid a
decision — an inflated tier is the same defect as an under-classified one. State the tier in one line only
when not obvious: A3+, or when it came from an axis the GD wouldn't expect. At A1/A2, say nothing and work.

## Step 4 — what each axis buys

The axes producing the tier are not interchangeable — collapsing them turns classification into ceremony. A
D1 edit to a credential is A5 via **C**, buying verification, not a design loop or docset.

| Axis | Buys | Never buys |
|---|---|---|
| **D** | The **shape**: roles, whether a Tech Spec is written, which checkpoints fire, which feature-root docs are owed | Extra verification on its own — a hard, low-consequence problem verifies at its own level |
| **C, R, X** | The **depth**: verification level, evidence strength, how carefully each attempt is prepared | A checkpoint, a document, or an extra agent — consequence means checking harder, never more process |
| **U** | The **direction gate**: an unresolved consequential unknown is what the design loop settles | Anything once resolved/bounded — U is the axis meant to be spent down |

**Shape, set by D:**

| D | Roles | Tech Spec | CP1 | CP2 | CP3 | CP4 | Feature-root docs |
|---|---|---|---|---|---|---|---|
| D1–D2 | one | no — direct notes | — | — | merged into CP4 | ✔ | none |
| D3 | several | ✔ | — | ✔ | ✔ | ✔ | `LEDGER.md`/`DEBT.md`/`NOTES.md`, on trigger |
| D4–D5 | several, often cross-track | ✔ | ✔ | ✔ | ✔ | ✔ | full docset, on trigger |

U3 fires CP1 at any D — an undecided direction is exactly what Advisor⇄Critic exists for, the only non-D
addition. A U2 resolved before execution adds nothing.

**Depth, set by the A-tier** (verification levels are `effort-allocation.md`'s; attempt budget is
`execution-loop.md`'s and keys to **D**, not A — criticality raises care per attempt, never attempt count):

| A | Verification floor | Attempt budget | Scored by `assurance-evaluator` |
|---|---:|---:|---|
| A1 | V1 | 2 | no — overhead `effort-allocation.md` forbids |
| A2 | V1, or V2 once it changes state | 2 | no |
| A3 | V2 | 3 | ✔ |
| A4 | V3 | 4 | ✔ |
| A5 | V4 | 5 | ✔ |

**The tier is assigned once per feature, then per execution unit.** `technical-architect` classifies at
intake and holds it in the ledger; a step inside may classify **higher** for its own dispatch, never lower,
and states why — the feature's tier stays put. A large D-to-tier gap is worth one line to the GD.

## Rules

- Classify before substantial work, from the request itself — never by dispatching an agent to decide it.
- Name H/M/Q/P requirements before executing past a trivial change; never reduce scope silently.
- Classify D, C, U, R, X independently; the tier is the highest of D/C/R/X, adjusted by U.
- Never inflate a tier to appear thorough, never deflate one because the task looks easy.
- A material conflict or missing required input is stated and bounded, never guessed; `Blocked` is correct.
- D sets shape, C/R/X set depth, U fires the direction gate — never let one axis buy another's half.
- State the tier at A3+, or when it came from an unexpected axis; otherwise stay silent and do the work.
