# Shared — Task Intake & Classification

Applies to: every agent and the orchestrator, on every input — a feature request, a one-line question, a
direct dispatch, or a returning defect. Like `language-and-comments.md`, this file sits above the
`.claude/rules/<group>/` folders rather than inside one.

Source: `.claude/docs/frame/AAEAS_v4_2_Runtime_Core.md` §§2–4, adapted to this project's roles, tiers and
hazards. The Full Assurance Reference beside it is the audit-level expansion — open it only when a
classification is genuinely contested, never as routine input.

## Why it exists

An input never states how hard it is or what it costs to get it wrong, and both of those are decided before
any work happens — usually silently, usually by default. Two failure modes follow:

- **Under-rigor on an easy-looking task.** A one-line edit to a signing config, a currency formula, or a
  published branch is trivial to write and expensive to get wrong. Difficulty is not consequence.
- **Over-process on a trivial one.** A triage, a spec and a verification plan over a rename costs more than
  the rename and produces nothing the rename needed.

Classifying takes no agent call and no tool call. It is a judgment made from the request itself, stated in
one line when it is not obvious, so the GD can correct it at the first turn instead of after the work.

## Relationship to other rules

| File | Owns |
|---|---|
| `orchestration.md` | Which **lane** an input takes — the full pipeline, one agent, or handled directly |
| `technical-architect`'s Triage | The **process weight** a feature carries — Simple/Medium/Complex, how many roles and checkpoints |
| **This file** | The **rigor** one execution unit runs at — how much care, verification and evidence |
| `effort-allocation.md` | What that rigor buys, and what it must never buy |
| `execution-loop.md` | What happens when the first attempt is not good enough |

Lane, process weight and rigor are three independent decisions. A Simple-tier change handled directly can
still demand the highest rigor in this file, and a Complex-tier feature can contain tasks that need almost
none.

## Step 1 — the requirement baseline

Before substantial work, name what the input actually asks for.

| Class | Meaning | Rule |
|---|---|---|
| **H** — Hard | An explicit non-negotiable constraint: a stated platform, a budget the GD fixed, a rule file, a safety or security boundary | Violating one without authorization is a failed task, never a trade-off |
| **M** — Material | Needed for the result to be useful at all | Dropping one silently is a failed task; leaving one unresolved **and saying so** is not |
| **Q** — Quality | A non-functional threshold — a frame-time budget, the style rules, test coverage | Must meet the applicable threshold |
| **P** — Preference | Desirable but tradeable | May be dropped, with the reason stated |

Past a trivial change, also establish: the objective, the deliverables, the scope boundaries, the material
assumptions, the dependencies, what "done" means, and any time or cost limit the GD stated.

**No silent scope reduction.** Never drop a hard part, redefine a requirement into an easier one, treat a
material requirement as optional, answer with advice about how to do the work instead of doing it, or call a
partial artifact complete.

**When requirements conflict**, resolve in this order:

```text
Platform, safety and security constraints
    ↓
The GD's explicit hard constraint
    ↓
The more specific requirement
    ↓
The more recent explicit requirement
    ↓
The accepted baseline — Tech Spec, GDD, the rule files
```

A material conflict that stays unresolved does not get resolved by picking the easier reading. Proceed only
on the scope the conflict does not touch, state the conflict, and never fabricate the missing input.
`Status: Blocked` on a genuinely missing required input is a correct result, not a failed run — per
`qa/verification-standards.md`, which says the same thing for the QA track.

## Step 2 — the five axes

Classified **independently**. A task is not one number: the axes routinely disagree, and that disagreement
is the information.

### D — Difficulty: intrinsic reasoning and implementation complexity

| Level | In this project |
|---|---|
| D1 | Read a file, answer from a rule, rename a field, adjust one serialized value |
| D2 | A known-shape change across a few files; most Simple-tier work |
| D3 | Several dependencies, edge cases or design choices — a Medium-tier feature, a new screen bound to Core state |
| D4 | Architecture or interacting dependencies — client prediction and reconciliation, a new Shared Core system, a cross-layer refactor |
| D5 | System-level — the netcode foundation, Job System/Burst/DOTS adoption, a project-wide migration |

### C — Criticality: consequence if it is wrong

| Level | In this project |
|---|---|
| C0 | Local and cheap — a comment, a scratch file, a throwaway query |
| C1 | Limited rework — a wrong Editor setting caught on the next run |
| C2 | Material — a `Game.Core.*` rule that makes client and server diverge, a feature behaving wrongly on a normal path |
| C3 | High — a production build, released content, an economy or progression path, save-data migration, a shipped mobile performance budget |
| C4 | Critical — a credential or player PII, real-money IAP or billing, a store submission, server authority or anti-cheat, published git history |

C4 is where `security.md` already applies with no tier exemption. This axis is the general form of that rule,
not a softer version of it.

### U — Uncertainty: what is unresolved that could change the answer

| Level | In this project |
|---|---|
| U0 | The spec, the inputs and the dependencies are established |
| U1 | Minor ambiguity, unlikely to change the result |
| U2 | A missing Tech Spec clause, an unstated performance budget, unknown track state (client-only vs. backend), an unconfirmed C# language version |
| U3 | A consequential unknown — the GDD has not decided the rule yet, or the API's current shape is unverified and the work depends on it |

U2 and U3 are never silently converted into asserted fact. Resolve it, bound it, state the assumption, or
limit the conclusion to what it does not touch.

### R — Reversibility: how hard recovery is

| Level | In this project |
|---|---|
| R0 | No state change — review, research, a report |
| R1 | A working-tree edit, a local commit on a branch |
| R2 | A pushed commit, a distributed build, a shared scene or prefab mutation |
| R3 | Rewritten published history, a store submission, a leaked credential, deleted data |

### X — Operational exposure: how far the action reaches

| Level | In this project |
|---|---|
| X0 | Analysis or a local document |
| X1 | The working tree, a sandboxed Editor change |
| X2 | `git push`, the project's single Unity Editor over MCP, a CI pipeline definition, the one physical test device |
| X3 | A store submission, production or live config, a destructive device operation, anything touching real money or real player data |

X2 is where invariants I3 and I7 in `orchestration.md` bite — one Editor and one device, project-wide. Two
agents at X2 on the same resource is a conflict before it is a risk.

## Step 3 — the assurance tier

```text
D1→A1  D2→A2  D3→A3  D4→A4  D5→A5
C0→A1  C1→A2  C2→A3  C3→A4  C4→A5
R0→A1  R1→A2  R2→A4  R3→A5
X0→A1  X1→A2  X2→A3  X3→A5
```

The tier is the **highest** required by D, C, R or X — never an average, and never the one that happens to
be convenient. Then adjust for uncertainty:

```text
U0 / U1 → no change
U2      → one tier higher, unless resolved before execution
U3      → A5 until the unknown is resolved or explicitly bounded
```

**Never inflate the tier** to look thorough, to justify more tool calls, to produce more documentation, or
to avoid making a decision. An inflated tier is the same defect as an under-classified one, pointed the other
way.

State the tier in one line only when it is not obvious from the work — at A3 and above, or whenever the tier
came from an axis the GD would not expect (a D1 edit that lands at A5 because it is R3). At A1/A2, say
nothing; the classification still happened.

## Step 4 — reconciling with the Triage tier

`technical-architect`'s Simple/Medium/Complex and this file's A1–A5 measure different things and neither
overrides the other.

| | Triage tier | Assurance tier |
|---|---|---|
| Scope | One feature, across its whole pipeline | One execution unit — this turn, or one agent's dispatch |
| Decides | How many roles, which checkpoints, which documents are owed | How much verification, evidence and care |
| Owned by | `technical-architect` | Whoever is executing |

Three rules hold the seam:

- **A Triage tier never lowers an assurance tier.** "It is only Simple tier" does not reduce the verification
  a C3 or X3 action demands. `security.md` already states this for its own scope; it is general.
- **An assurance tier never adds process.** A5 rigor inside a directly-handled lane means more verification
  and more evidence — not a Tech Spec, not a checkpoint, not an extra agent. Only `orchestration.md` and the
  workflow files add process.
- **A large mismatch is worth one line to the GD.** Something Triage called Simple that classifies A4/A5 is
  usually a sign the triage missed a consequence — say so before doing it, not after.

## Rules

- Classify before substantial work, from the request itself — never by dispatching an agent to decide it.
- Name the H/M/Q/P requirements before executing anything past a trivial change, and never reduce scope
  silently.
- Classify D, C, U, R and X independently; the tier is the highest of D/C/R/X, adjusted by U.
- Never inflate a tier to appear thorough, and never deflate one because the task looks easy — difficulty is
  not consequence.
- A material conflict or a missing required input is stated and bounded, never guessed; `Blocked` is a
  correct result.
- A Triage tier never lowers an assurance tier, and an assurance tier never adds a pipeline step.
- State the tier at A3 and above, or whenever it came from an axis the GD would not expect. Below that, stay
  silent and just do the work.
