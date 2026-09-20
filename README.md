# AI-For-Game-Development

A complete, drop-in **AI game-development team** for [Claude Code](https://claude.com/claude-code), built for
Unity production work. It is not a game and not a library — it is the `.claude/` configuration layer that
turns a single general-purpose assistant into a **28-role studio** with explicit ownership boundaries, review
gates, QA sign-off, and human checkpoints where decisions actually belong to a person.

Everything here is Markdown, JSON and one PowerShell script. No runtime, no build step, no dependency to
install — copy `.claude/` into a Unity project and the behaviour changes.

## Table of contents

- [Why this exists](#why-this-exists)
- [What you get](#what-you-get)
- [Core concepts](#core-concepts)
- [Installation](#installation)
- [Quick start](#quick-start)
- [How work is routed](#how-work-is-routed)
- [The pipelines](#the-pipelines)
- [Checkpoints](#checkpoints)
- [The agent roster](#the-agent-roster)
- [The skill library](#the-skill-library)
- [Rules and standards](#rules-and-standards)
- [Slash commands](#slash-commands)
- [Prompt templates](#prompt-templates)
- [State: the ledger and the two locks](#state-the-ledger-and-the-two-locks)
- [Repository layout](#repository-layout)
- [Extending the framework](#extending-the-framework)
- [Project conventions](#project-conventions)
- [Maintenance and verification](#maintenance-and-verification)
- [Known limitations](#known-limitations)

## Why this exists

A single assistant working on a Unity codebase fails in predictable ways: a damage formula lives inside a
`MonoBehaviour` where the server can never validate it, the author reviews their own work and finds nothing,
"tested" means "read the file". None of that is a knowledge failure — it is a **structure** failure: no
separation of authorship from review, no owner for a decision, no gate where a human says yes.

| Failure | What this framework puts in the way |
|---|---|
| Game rules duplicated between client and server | A hard `Game.Core.*` boundary, plus `shared-core-boundary-audit` |
| The author reviews their own work | `code-reviewer` and `security-reviewer` are always different agents, run in parallel, and cannot edit files |
| "It works" with nothing behind it | `verification-standards.md` — every QA output states what it did **not** cover |
| An expensive process on a trivial ask | Step 0 sizing: over a dozen rows, first match wins, zero agent calls to decide |
| Consequence buying an 8-call pipeline | The **gated-direct lane** — a criterion tripped for consequence alone still costs three calls, not eight |
| A big decision made silently | Four checkpoints where the human, not an agent, approves |
| A loop that never converges | Every cap in the layer is counted and composes into a stop — `references/loop-termination.md` |
| Secrets in code, history, or logs | `security.md` — zero-tolerance, no tier exemption, ever |

The premise throughout: **agents are isolated, stateless, silent and alone** — each sees only its own dispatch
prompt, cannot remember a prior run, and cannot dispatch another agent. Every counter belongs to the caller,
which is why this repository has a workflow layer and a ledger at all.

## What you get

| Layer | Path | Count | What it does |
|---|---|---|---|
| **Rules** | `.claude/rules/` | 12 files, flat | Auto-loaded into every session — standards every agent obeys before it can even read its task |
| **Standards** | `.claude/standards/` | 7 files — `client/` (5), `qa/` (2) | Loaded **on demand**, only by the agents whose track owns them |
| **Agents** | `.claude/agents/` | 28 agents, flat | Each a system prompt: one role, its scope, its refusals, its output envelope |
| **Skills** | `.claude/skills/` | 90 skills, flat | On-demand technique packages, one per `.claude/skills/<name>/SKILL.md` |
| **Workflows** | `.claude/workflows/` | orchestrator + 6 pipelines + a checklist, 29 reference files, 3 state templates, 1 verification script | Sequence, parallelism, retry loops, checkpoints, cross-run state |
| **Commands** | `.claude/commands/` | 5 slash commands | Self-contained investigations — one of which edits code |
| **Docs** | `.claude/docs/` | 3 authoring templates, 3 frame sources, 8 review records, a prompt-template suite | How to extend the framework, how to brief it, and the record of how it got here |
| **Settings** | `.claude/settings.json` | 35 allow-rules | Pre-approved read-only git/lfs commands so routine inspection does not prompt |

**The division of labour is strict**: `rules/`+`standards/` are standards, `agents/` is who owns what,
`skills/` is how a technique works, `workflows/` is what runs when. An agent file that describes sequence is
wrong; a workflow file that explains a technique is wrong; a skill that owns a decision is wrong.

## Core concepts

### The GD

**GD** means the Game Designer / Director — *you*. Agents never decide on the GD's behalf; four checkpoints
exist so direction, spec approval, build acceptance and feature closure are answered by a person.

### Tiers — `task-classification.md`

Every task is classified on **five independent axes** (D difficulty, C criticality, U uncertainty,
R reversibility, X exposure) into an **A1–A5** assurance tier — the retired Simple/Medium/Complex triage tier
appears nowhere in this framework anymore. Tier = the **highest** of D/C/R/X; **U2** raises it one level
unless resolved, **U3** forces **A5** until bounded. **D sets shape** (roles, checkpoints, docset); **C/R/X
set depth** (verification, evidence) and never buy a checkpoint or extra agent alone; **U** is the direction
gate, spent down once resolved. The tier also sets the verification floor (V1→V4) and attempt budget
(2→5) an execution must meet — full axis definitions and the per-tier table are in
[`task-classification.md`](.claude/rules/task-classification.md) and
[`effort-allocation.md`](.claude/rules/effort-allocation.md), not restated here.

### Tracks

The **backend track** (multiplayer / server-authoritative) is *caller state* — `netcode-engineer` and
`server-authoritative-engineer` return `Blocked` rather than assume it's on; `technical-architect` silently
assumes client-only when nobody says otherwise.

### The Shared Core boundary

| Namespace | Contains | May reference `UnityEngine` |
|---|---|---|
| `Game.Core.*` | Every rule that decides an outcome — damage, cooldowns, economy math, state machines | **Never** |
| `Game.Client.*` | MonoBehaviours, scenes, prefabs, UI, rendering, input | Yes |
| `Game.Server.*` | Server-side validation wrapping the Core — backend track only | No |

Shared Core is additionally **deterministic** — no `UnityEngine.Random`, no wall-clock time, no float
operation that can diverge across platforms — which is what lets prediction and authority ever agree.

### The output envelope

Every agent returns a structured value, not a chat message:

```
## [Report name] — <subject>
- Status: Done | Blocked | Rejected | Needs-decision
- Assessed: Direct | Considered | Escalate
- Routed to: <agent-id> | gd | none
- Blocked — needs from caller: <what is missing | none>
[role-specific fields]
```

`Blocked` is a **correct result**, not a failure — supply exactly what is named, never guess. `Routed to:` is
a **recommendation**, never an action taken, since agents cannot dispatch each other. For any review, read
`Verdict:`, never `Status:` — a review requesting changes still returns `Status: Done`.

### Self-assessment

| Level | Criterion | Depth |
|---|---|---|
| **Direct** | Unambiguous, established pattern, contained change | Do it, report briefly |
| **Considered** | Several viable approaches, or it touches a contract others depend on | State the approach, then verify the result |
| **Escalate** | Needs authority this role does not own, or the task already failed twice | Return `Needs-decision` with `Routed to:` |

When uncertain, an agent goes one level **up**, never down.

## Installation

### Requirements

- **Claude Code** (CLI, desktop, web, or an IDE extension).
- A **Unity project** — this framework assumes Unity/C# throughout; the bundled `.gitignore` is the standard
  Unity one, which tells you where `.claude/` is meant to sit: the project root.
- A **Unity Editor MCP server**, for the ten agents that declare Editor tools in their `tools:` frontmatter.

### Steps

```bash
git clone https://github.com/<your-fork>/AI-For-Game-Development /tmp/ai-gamedev
cp -r /tmp/ai-gamedev/.claude .
cp /tmp/ai-gamedev/.gitignore .          # skip if your project has its own
cp /tmp/ai-gamedev/CLAUDE.md .           # then fill in every <!-- TODO -->
claude                                   # from the project root
```

### Connecting the Unity Editor

Editor-driven agents name their MCP tools **exactly** in frontmatter (e.g. `Unity_RunCommand`). A mismatch
with your connected server fails silently at call time. Verify the names line up, then fix any mismatch in
each agent's `tools:` line — nothing else needs changing:

```bash
grep -h '^tools:' .claude/agents/*.md | tr ',' '\n' | grep mcp__ | sort -u
```

### Without a Unity Editor connection

Everything else still works — triage, Tech Specs, Shared Core, both review gates, research, git, CI/CD, and
every planning role. What you lose is Play Mode verification, profiling and in-Editor tests, and QA reports
those as **uncovered** rather than silently passing.

## Quick start

- **Ask a question — costs nothing.** *"How does the ability cooldown flow through `Game.Core.Combat`?"*
  Answered directly, or by one read-only agent.
- **Make a small, visible change — one agent.** *"The camera zoom feels slow — snap it up, judge it by
  playing."* Judgeable by looking → direct, no fan-out, no checkpoint.
- **Build a feature — the full pipeline.** Copy the skeleton in
  [`prompt-templates/single-feature.md`](.claude/docs/prompt-templates/single-feature.md); its
  `<escalation_check>` block checks the same five criteria Step 0 uses, below.
- **Investigate something specific** — `/review-code-risks Assets/Scripts/Combat`,
  `/plan-test-coverage --spec docs/specs/fireball.md`, `/investigate-device-crash android com.studio.game`.
- **Call one role directly — your cost override.** *"Have `unity-engineer` wire the Fireball prefab in."*
  Naming an `agent-id` bypasses Step 0 outright; review debt still accrues, but nothing blocks.

## How work is routed

`orchestrator.md` Step 0 sizes every input the GD did **not** address to an agent or a pipeline — zero agent
calls, stated out loud so you can redirect immediately. **Read top-down, first match wins, specific before
general** — a catch-all takes only what nothing above it claimed.

| Input | Handling | Calls |
|---|---|---|
| A git or version-control task | `git-expert` | 1 |
| A CI/CD task — author a pipeline, or diagnose a failed run | `ci-cd-engineer` | 1 |
| A crash/ANR from **released production telemetry** | `crash-anr-investigator` — a device *under test* is `/investigate-device-crash` instead | 1 |
| A change to a spec the GD already approved | `change-request.md` **E1** — halt new work against it first | 1–3 |
| A bug in something the pipeline built, spec still stands | `feature-development.md` **E3** | 1–3 |
| An audit of code already in the repo — read, never run | `review-pipeline.md` **E2** | 1–2 |
| Coverage/evidence on work already built — run, never only read | `qa-pipeline.md` **E4** | 2–5 |
| "What exists today" for a missing capability | `research-decision.md` **E5** | 1–4 |
| "Measure it on our own hardware first" | `research-decision.md` **E6** — asking *is* the summon | 2–4 |
| **Consequence only** — one role, no contract moves, behaviour already stated | **Gated-direct** — the agent, then both gates | 3 |
| Any of the five escalation criteria below | `feature-intake.md` **E1** — classification sets the tier | 8+ |
| Judgeable by looking — UI, layout, a tuned value, one local behaviour | Directly, or one agent — no fan-out, no checkpoint | 0–1 |
| A chore, or a question | Directly, or one read-only agent | 0–1 |

### The five escalation criteria

Any one of these trips `feature-intake.md` **E1**: touches `Game.Core.*` (C2+), touches a consequence path —
credential/signing, real-money IAP/billing, a store submission, player PII, save-data migration, published
git history, a released build, a shipped perf budget (C3+), needs more than one role (D3+), is
multiplayer-relevant (C2+), or rests on something the GD has not decided yet (U3). Full criteria and axis
definitions live in [`task-classification.md`](.claude/rules/task-classification.md).

**Route by the cost of being wrong, never by whether behaviour changed** — consequence buys the *gates*, never
the pipeline. Tripped for **consequence alone**, with one role and no moving contract, it's the
**gated-direct lane** above: the agent, then both gates, capped at two strikes before escalating anyway.
**D3+ or U3 is different in kind** — that input needs coordination or a direction, which is shape.

### The three modes

| Mode | The GD says | What runs | Cost |
|---|---|---|---|
| **1 — routed** | A feature request, nothing named | Step 0 picks a lane; each optional gate is offered at its own boundary | Whatever the lane costs |
| **2 — a named pipeline** | Names a pipeline, or an entry in one | That file, from that entry, returning **to the GD** | One pipeline's worth |
| **3 — direct agent** | Names one or more `agent-id`s | Exactly those, serialised where the Editor lock applies | One call each |

Naming an `agent-id` is the GD's **cost override** — debt is recorded, nothing is blocked. Modes change
**when** an invariant is satisfied, never **whether** it is owed.

## The pipelines

`orchestrator.md` is not itself a pipeline — it owns Step 0 above, the three modes, and every counter that
survives past one run. The six pipelines own sequence, parallelism, retries and checkpoints; a shared
`references/` folder (29 files) holds detail promoted out of all seven once a file neared the 200-line cap,
read only when its own trigger fires.

| Pipeline | Scope | Dispatches | The mechanic worth knowing |
|---|---|---|---|
| **1. `feature-intake.md`** | Request → approved Tech Spec | `technical-architect`, `advisor`, `critic` | Classification runs first, unconditionally. Advisor⇄Critic fires only at **D4–D5 or U3**, capped 3 rounds → CP1. **D1–D2 skips the Tech Spec** — direct notes to one agent |
| **2. `research-decision.md`** | Missing capability → settled decision | `researcher`, `rd-engineer`, `cto` | Three depth lanes (Direct/Considered/Escalate) that only ever raise. `cto` never runs without a candidate set; `rd-engineer` only on an explicit GD summon; one measure-and-confirm cycle, hard capped |
| **3. `feature-development.md`** | Approved spec → code at the gate offer | The 9 implementing/lead roles | Shared Core first — 4 agents return `Blocked` without its contract. The client fan-out is serial (one Editor). **Review and QA are asked for, never auto-dispatched** |
| **4. `review-pipeline.md`** | One submission, both gates → CP3 | `code-reviewer`, `security-reviewer`, `technical-architect` | Optional. Both gates run in parallel, wait for both, neither edits. Clear only on `Approve` **and** `Clear`; else +1 strike, capped 3 (2 on gated-direct) before root cause |
| **5. `qa-pipeline.md`** | Cleared (or declined) review → CP4 | `qa-lead`, 4 executors, **`assurance-evaluator`** (new, A3+), `producer` | Optional, doesn't require review. `qa-lead` plans early; `assurance-evaluator` checks a claimed verification is actually evidenced — `FAIL` is an integrity finding, beyond any waiver. **CP4 always fires** |
| **6. `change-request.md`** | A change to an approved spec | `technical-architect`, `producer` | Halts new dispatch against the questioned spec first. **Minor** updates in place, no gate; **Moderate** reopens CP2; **Major** reopens CP1. Resets every rejection counter it invalidates |

## Checkpoints

Four checkpoints — each a point where an **agent stops and a person answers.**

| CP | Fires at | The GD approves | Rejecting means |
|---|---|---|---|
| **1** | D4–D5, or U3 at any D | The locked direction, and which risks they accept | Back into the loop, capped at 3 rounds |
| **2** | D3–D5 | The Tech Spec | Back to `technical-architect`, capped at 3 |
| **3** | D3–D5, only when review ran; merged into CP4 at D1–D2 | What was built, against the spec | Drift to its author, capped at 2 |
| **4** | Every shape, always — the only gate that fires whether or not the others did | Closing the feature, gaps and declined gates included | A defect (capped at 2) or a change request (unbounded) |

**Review and QA are both optional** (`references/optional-gates.md`) — whoever reaches the boundary asks,
states the cost of skipping, dispatches only on a yes. A decline is debt, never silence — **CP4 always fires
regardless**: closing a feature is the GD's decision, never a gate's verdict.

## The agent roster

28 agents, **flat** — every one lives at `.claude/agents/<agent-name>.md`, no group subfolder (they were
flattened out for the same reason skills were: the harness resolves an agent one level deep, not two). Model
matches the hardest **Self-assessment** level the role actually reaches. Grouped informally, by concern:

| Group (informal) | Count | Covers |
|---|---:|---|
| **Architecture** | 4 | Tech Spec/triage (`technical-architect`), strategic tech calls (`cto`), research, spikes |
| **Client** | 7 | Shared Core, scene/prefab/perf, UI, shaders/VFX, and 3 tech-lead escalation roles |
| **Backend** | 2 | Sync protocol and server-side validation — multiplayer track only |
| **QA** | 8 | Scope/sign-off, both review gates, independent scoring (A3+ only), 4 execution roles |
| **DevOps** | 3 | Git ops/forensics, CI/CD authoring, builds (GD-summoned only) |
| **Leadership** | 3 | Widening options, attacking a leaning direction, aggregating status |
| **Live-Ops** | 1 | Released production crash/ANR telemetry only |

Every agent's own frontmatter `description` in `.claude/agents/` is the authoritative one-line summary —
not repeated here. **The `tools:` list is the hard sandbox.** 14 agents hold no `Write`/`Edit` — reports
leave no source, so direct dispatch accrues no review debt. 10 hold Editor tools and 2 hold device tools,
neither ever two at once, project-wide. `code-reviewer` and `security-reviewer` cannot edit, ever.

## The skill library

90 skills, **flat** — every one lives at `.claude/skills/<skill-name>/SKILL.md`, no group subfolder (they were
flattened out because the harness resolves a skill one level deep, not two). Frontmatter carries only `name`
and `description`; there is no category field left, so grouping below is informal, read off each skill's own
description rather than off any folder or frontmatter key.

| Area (informal) | Skills |
|---|---|
| **Client/Unity (57)** | Rendering, UI, physics, 2D/3D content, camera & audio, DOTS, networking primitives, architecture patterns, performance, tooling & data — the full Unity/.NET surface, e.g. `render-pipeline-urp-hdrp`, `ugui`, `unity-ecs-architecture`, `netcode-for-gameobjects`, `unity-job-system-and-burst`, `zstring-zero-allocation-strings` |
| **QA (7)** | `shared-core-boundary-audit`, `secret-and-supply-chain-scan`, `risk-based-test-planning`, `playtest-scenario-execution`, `performance-budget-verification`, `device-test-walkthrough`, `build-fault-triage` |
| **Architecture (10)** | `netcode-architecture-decision`, `backend-build-vs-buy`, `anti-cheat-strategy`, `ad-mediation-monetization-platform`, `analytics-telemetry-platform`, `live-ops-content-pipeline`, `cross-platform-expansion-assessment`, `tech-vendor-dependency-risk-assessment`, `tco-reversibility-scoring`, `engineering-standard-adr-authoring` |
| **DevOps (9)** | `git-safety-anchor`, `git-recovery`, `git-forensics`, `git-unity-repo`, `jenkins-pipeline-authoring`, `unity-batchmode-cli`, `fastlane-mobile-delivery`, `firebase-app-distribution`, `ci-pipeline-failure-triage` |
| **Live-Ops (3)** | `crash-anr-fault-domain-triage`, `crash-anr-symbolication`, `crash-anr-reporting-gate` |
| **Research (4)** | `technology-scouting-sweep`, `source-credibility-grading`, `practical-fit-screening`, `solution-comparison-report` |

`shared-core-boundary-audit` is the one to know: it turns the project's one unabsorbable defect class — a rule
duplicated in two places, or a Core that cannot produce the same answer twice — into a mechanical grep,
rather than a judgement that depends on how carefully one person read a diff.

## Rules and standards

`.claude/rules/` is **auto-loaded into every session** — 12 flat files, no subfolders, covering orchestration
and dispatch invariants, task classification, effort/verification budgets, the execution-attempt loop,
feature-context reading order, security (zero tolerance, no tier exemption), the implementation-note handoff,
commit-message convention, working language, shell and Unity-tooling preference. Each file is short and
single-purpose; read the file itself rather than a summary here.

`.claude/standards/` is loaded **on demand**, only by the agents whose track it governs — `client/` (coding
principles, style, naming, performance, feature documentation) and `qa/` (verification standards, defect
reporting). [`standards-index.md`](.claude/rules/standards-index.md) is the authoritative "who reads what,
when" table and the reason these live outside the auto-loaded tree at all.

Three worth knowing without opening a file: **`this.` qualification is mandatory** (`this.health -= damage;`).
**Unity null checks use the implicit `bool`** (`if (this.rb)`) on `UnityEngine.Object`-derived types only;
plain C# and `Game.Core.*` types use `!= null`. **Every QA output states what it did not cover**, never
`none` unless coverage was genuinely exhaustive.

## Slash commands

| Command | Arguments | What it does |
|---|---|---|
| [`/review-code-risks`](.claude/commands/review-code-risks.md) | `[paths...]` | Static C#/Unity review for perf, memory and crash/ANR risk — report only, never edits |
| [`/plan-test-coverage`](.claude/commands/plan-test-coverage.md) | `[paths...] [--spec doc]` | Derives normal + edge test cases and a manual flow — never decides which are owed |
| [`/investigate-device-crash`](.claude/commands/investigate-device-crash.md) | `[android\|ios] [package-id]` | Investigates a crash/ANR on the **currently connected device** |
| [`/resolve-merge-conflicts`](.claude/commands/resolve-merge-conflicts.md) | — | Resolves an in-progress merge across code, prefabs, scenes, SOs, Addressables — **this one edits files** |
| [`/verify-workflow-layer`](.claude/commands/verify-workflow-layer.md) | — | Runs `tools/verify-workflow-layer.ps1` and reports drift in the workflow layer's own claims |

`/plan-test-coverage` also runs inside `qa-pipeline.md`'s device lane, filtered to whatever `qa-lead` assigned.

## Prompt templates

Seven templates in `.claude/docs/prompt-templates/`, split by **purpose**, each a variant of one six-part
frame — Objective, Context, Scope, Constraints, Deliverable, Done when. `Scope` and `Done when` are the two
most often skipped, and the two most expensive to skip.

| You want to | Template | Lane |
|---|---|---|
| Understand code, rename, tune a value | `basic-request.md` | direct |
| Add **one** feature | `single-feature.md` | direct **or** `feature-intake.md` E1 — its `<escalation_check>` decides |
| Add a **batch** of features | `multi-feature.md` | plan first, then loop `single-feature` |
| Prototype or measure feasibility | `prototype.md` | direct |
| Implement from a GDD/spec/vendor doc | `from-documents.md` | map first, then `feature-intake.md` E1 |
| Fix a reproducible bug | `bugfix-debug.md` | direct, or `feature-development.md` E3 |
| Investigate a rare, non-reproducible fault | `rare-case.md` | investigate first, don't fix yet |

Markdown carries instructions, XML wraps anything pasted verbatim, JSON is reserved for tabular data.
`examples/` holds 20 filled-in examples across all 7 templates. `prompt-templates/` is written in Vietnamese,
matching the GD-facing protocol — everything else here is English.

## State: the ledger and the two locks

Cross-run state is what no agent can hold, written **at each transition**, never at a run's end. **None of it
lives under `.claude/`** — that directory is the framework every project copies unchanged.

| State | Where |
|---|---|
| One feature's run state and its decision history | `<feature-root>/LEDGER.md` — one file, two halves: `## Decisions` (read before undoing a design) and `## Run state` (the orchestrator's, written at every transition) |
| The in-flight index, both global locks, gate debt belonging to no feature | `<state-root>/project-state.md` — `.workflow/` at the project root unless `CLAUDE.md` says otherwise |
| One row per closed feature, measuring this layer's own untested constants | `<state-root>/calibration.md` |

**Review debt**: any `Write`/`Edit`-capable agent dispatched outside a gate accrues it — recorded, never
enforced, settling in batch. A **declined** gate is the same kind of debt, per `references/optional-gates.md`.

**The Editor lock**: one Unity Editor, project-wide, 10 agents hold tools against it. **The device lock**: one
physical device, independent of the Editor lock. Two holders of the same lock never run at once; a holder
that dies leaves it *suspect*, never silently free — `state/README.md` carries the three-step reclaim.

## Repository layout

```
.
├── .claude/
│   ├── agents/                     # 28 roles, flat: <agent-name>.md
│   ├── commands/                   # 5 slash commands
│   ├── docs/
│   │   ├── agent-template.md · skill-template.md · skill-reference-template.md
│   │   ├── frame/                  # 3 source documents this project's rules adapt from
│   │   ├── reviews/                # 8 review records + an index, non-normative
│   │   └── prompt-templates/       # 7 templates, 7 .txt skeletons, 20 worked examples
│   ├── rules/                      # 12 auto-loaded files, flat
│   ├── standards/                  # 7 files, loaded on demand — client/ (5), qa/ (2)
│   ├── skills/                     # 90 skills, flat: <name>/SKILL.md
│   ├── workflows/
│   │   ├── orchestrator.md         # the router and cross-run state
│   │   ├── feature-intake.md · research-decision.md · feature-development.md
│   │   ├── review-pipeline.md · qa-pipeline.md · change-request.md
│   │   ├── workflow-checklist.md   # append-only, exempt from the line cap
│   │   ├── references/             # 29 files promoted out of the files above
│   │   ├── state/                  # rules + templates for the state layer — never state itself
│   │   └── tools/                  # verify-workflow-layer.ps1
│   └── settings.json               # 35 pre-approved read-only git/lfs commands
├── .gitignore                      # the standard Unity ignore set
├── CLAUDE.md                       # per-project template — fill in every TODO before first use
└── README.md                       # this file
```

This repository contains no Unity project and no C# source — it is the configuration layer only.

## Extending the framework

**Adding an agent** — copy [`agent-template.md`](.claude/docs/agent-template.md) to
`.claude/agents/<agent-name>.md` — **flat**, no group folder. All 7 sections stay, even at one line; check
for an overlapping owner first. `description` is the only text the dispatcher reads. Model matches the
hardest **Self-assessment** level the role reaches, not how important it sounds.

**Adding a skill** — copy [`skill-template.md`](.claude/docs/skill-template.md) to
`.claude/skills/<skill-name>/SKILL.md` — **flat**, no group folder; `name:` must equal that folder name.
`description` is a retrieval index (SURFACE / WHEN / NOT FOR), 50–100 words. Budget: body under 200 lines,
depth pushed into `references/*.md`.

**Adding a workflow step** — sequence, retries and checkpoints live only in `.claude/workflows/*`. Give a
re-enterable step its own entry point, name every required input and its `Blocked` fallback, add the row to
the routing table, update the mermaid diagram, and log it in `workflow-checklist.md`.

| Concern | Home |
|---|---|
| Sequence, parallelism, retry loops, checkpoints | `.claude/workflows/*` |
| Cross-run state; acting on a `Routed to:` | `orchestrator.md` + `<feature-root>/LEDGER.md` + `<state-root>/project-state.md` |
| How a technique works | the skill |
| Coding standards, naming, working language | `.claude/rules/*` and `.claude/standards/*` |

## Project conventions

| Where | Language |
|---|---|
| Your input | Vietnamese, English, or mixed — parsed as-is |
| All internal work — reasoning, specs, verdicts, code, commit messages, logs | **English, always** |
| The final reply to you | **Vietnamese, always** — every role, without exception |

**Commits**: English, imperative subject, blank line, a body explaining *why* — no `feat:`/`fix:` prefixes.
One commit, one change. **Document length**: every file under `.claude/` holds a 200-line cap, with
`workflow-checklist.md` exempt as append-only by design. This README is the one document meant to be read
whole rather than opened on demand, so it is not bound by that cap — but it stays a summary, pointing at the
rule/standard file for detail rather than restating it.

## Maintenance and verification

Run `.claude/workflows/tools/verify-workflow-layer.ps1` (or `/verify-workflow-layer`) after any change under
`.claude/` — it checks agent-class counts, lock holders, the 200-line cap, entry-point coverage, orphaned
references and cross-reference anchoring; an unchecked claim about this layer is weak evidence.
`.claude/docs/reviews/` is history, never a source of truth — `workflow-checklist.md` is current build state.

## Known limitations

- **Optional gates mean asked, not assumed** — a decline is recorded as debt, but nobody independently
  checked the claim until that debt is paid off.
- **One Editor, one device, project-wide** — Editor-driven work is serial regardless of what runs in
  parallel, and no build means no device lane at all.
- **`assurance-evaluator` only runs at A3+** — below that, no gate independently checks a claimed
  verification.
- **`docs/skill-template.md` and `docs/agent-template.md`'s own authoring comments are stale** — both still
  name a pre-flattening path (`<group>/<skill-name>/SKILL.md`, `<group>/<agent-name>.md`); every real skill
  and agent is flat, at `.claude/skills/<skill-name>/SKILL.md` and `.claude/agents/<agent-name>.md`.
- **`docs/reviews/README.md`'s own index has a dangling row** — round 8 (`skills-layer.md`) is listed but the
  file does not exist; `verify-workflow-layer.ps1` flags this on every run.
- **MCP tool names are project-specific** — a mismatch with your connected server fails silently at call time.
- **`.claude/workflows/*` is not auto-loaded** — only `.claude/rules/**` is; `orchestration.md` is the
  ignition.
- **Vietnamese-facing docs are `prompt-templates/` only** — everything else here is English.

## License

No license file is present in this repository. Add one before distributing.
