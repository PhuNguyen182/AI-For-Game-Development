# Shared — Feature Context Reading

Applies to: every agent and every new session, in every mode — a full pipeline run, a single agent dispatched
directly, or the orchestrator working an input itself. Like `language-and-comments.md`, this file sits above
the `.claude/rules/<group>/` folders rather than inside one.

Source: `.claude/docs/frame/AI Context Reading Flow.md`, adapted to this project's tiers, roles and review
gates; self-contained, doesn't require that document to be present.

Every agent here is isolated and stateless: it sees one dispatch brief and whatever it reads from disk, never
the conversation that produced the code in front of it. Two failure modes follow: **reading nothing** (infers
intent from code alone, re-derives a decision already made, breaks an unstated contract) and **reading
everything** (ingests a whole docset before touching one field, spending context on material that couldn't
change the work). The rule is not "read the documentation" — it's **read the minimum context that makes the
task safe, in an order that reaches the dangerous unknowns first.**

`.claude/standards/client/feature-documentation.md` owns the writing side — which documents a feature root
carries and when each is owed. This file owns the reading side only: which of them a task must open, in what
order, and what to do when they disagree with each other or the code. `orchestration.md` governs what a
dispatch carries; this file governs what the dispatched agent reads on arrival.

## The docset

A feature root can carry up to seven documents; none is guaranteed — each is written only when its trigger
fires, per the authoring rule.

| File | The question it answers | Default |
|---|---|---|
| `README.md` | What is this feature, where does it start, what uses it | Read first, always |
| `INTEGRATION.md` | How do I talk to it from outside, what must I not call | Read, unless the task stays entirely inside the root |
| `CONTRACTS.md` | What must not break | Read before writing anything |
| `ARCHITECTURE.md` | How does it work inside | Only when changing the inside |
| `LEDGER.md` | Why is it built this way — and, in its other half, where this feature's run stands | Only when a design looks wrong |
| `DEBT.md` | What is already known to be wrong | Only when the code looks wrong |
| `NOTES.md` | What is not yet worth a contract | Only when the rest came up short |

**`LEDGER.md` is one file, two halves, only one is yours.** Its `## Decisions` half is the feature's decision
history — what was decided, why, what was rejected — the half this file sends you to. Its `## Run state`
half is the orchestrator's cross-run state (tier/axes, checkpoint position, strike counts, attempts used,
accepted gaps, continuation debt), written at every transition per `.claude/workflows/state/README.md`.
Reading past the heading answering your question means reading someone else's bookkeeping; editing it in a
submission overwrites a counter nothing else holds. There is no longer a second run-state file under
`.claude/` — nothing there is written at runtime, since that directory is the framework every project copies.

**Absent is not empty.** A missing file means its trigger never fired, not that the answer is "nothing" —
fall back to the source rather than concluding no contract/debt/history exists. A file clearly owed on a
feature-complete submission but missing is a finding for `code-reviewer`, never something the reader silently
writes.

## The default flow

`Task → README → INTEGRATION → CONTRACTS → the source those three named.` Covers most tasks — everything
below is a deviation with its own trigger.

## Flow by task shape

| The task | Read, in order | Leave closed unless triggered |
|---|---|---|
| **Use a feature** (call/bind, no change inside) | `README → INTEGRATION → CONTRACTS → implement` | `ARCHITECTURE`, `LEDGER`, `DEBT`, `NOTES` |
| **Change a feature** (logic inside one root) | `README → CONTRACTS → ARCHITECTURE → INTEGRATION → source` | `LEDGER`, `DEBT`, `NOTES` |
| **Connect features** (a seam between two+) | per feature: `README → INTEGRATION → CONTRACTS`; trace `A → integration point → contract → integration point → B` | `ARCHITECTURE` of any feature not changed inside |
| **Debug** | `README → CONTRACTS → reproduce/trace source → ARCHITECTURE → DEBT → LEDGER` | `NOTES`, until the rest comes up short |
| **Review code** (`code-reviewer`, `security-reviewer`) | Tech Spec/brief → `CONTRACTS` → the diff | `ARCHITECTURE`, until the diff moves logic across a boundary |
| **Test** (`qa-lead`, `qa-automation-engineer`, `playtest-tester`) | `README → CONTRACTS` (invariants are the assertions) → `DEBT` (so known debt isn't filed as new) | `ARCHITECTURE`, `LEDGER`, `NOTES` |
| **New feature root**, no docset yet | Tech Spec → `INTEGRATION`/`CONTRACTS` of every feature it touches | its own docset — written at completion, not read at the start |

An **A1/A2** change against a root with no docset reads only the source it touches — opening or inventing a
nonexistent docset is not a step. Tier gates what a change **writes**, never what it **reads**: an A1 change
to a feature with `CONTRACTS.md` still reads it first, since invariants bind the code regardless of editor.

## When to open the conditional four

**`ARCHITECTURE.md`** — logic inside the feature changes, several components are touched at once, a
component is added, data flow changes, it's a refactor, or ownership of logic is unclear from `README`.

**`LEDGER.md`** — a design looks wrong or arbitrary, you're about to change/undo an existing decision, or you
can't tell why the system works this way. Read it *before* changing what looks wrong — the point is catching
a deliberate decision before undoing it. Read the `## Decisions` half and stop; `## Run state` answers a
question you weren't asking.

**`DEBT.md`** — the task touches legacy code, a workaround or a large TODO; the area's architecture looks
unclean; a refactor is being considered; or a defect smells like a known limitation. Settles: *is this a new
bug, or debt someone already accepted?*

**`NOTES.md`** — the other documents didn't explain the behavior in front of you, you need an edge case from
an earlier session, or you hit unformalized behavior. Supplementary context, never a source of truth.

## When sources disagree

Documents state intent; source states what runs. Not ranked against each other — a gap between them is
itself a finding:

- **`CONTRACTS.md` disagrees with the code** — stop, report per `.claude/standards/qa/defect-reporting.md`,
  citing both anchors. Which one is wrong is for the owning agent or `technical-architect`, never a silent
  pick by whoever noticed.
- **A document is stale against the code** — treat like a stale test: report it, don't build on it.
- **Two documents disagree** — take the higher in this order, report the loser as stale:

```text
The Tech Spec/brief for the change in hand → CONTRACTS → ARCHITECTURE → INTEGRATION → README → LEDGER → DEBT → NOTES
```

The Tech Spec outranks the docset because the docset records what was last built and the spec is what's
being built now — but the docset still governs what the spec doesn't speak to; silence doesn't repeal an
invariant. Whatever documents say, the implementation is checked in source before being relied on.

## Stop reading

Stop when the next document couldn't change what you're about to write — concretely, once you know the
entry point, the invariants your change must hold, and which callers see your change. Reading past that is
the avoidable cost KISS (`coding-principles.md`) and the scope discipline in `performance-and-algorithms.md`
both warn against — spent on context instead of code.

Never re-read a document already quoted in the dispatch brief. Never read a feature's docset to decide
whether the task belongs to you — that's the brief's job; `Status: Blocked` is the answer when it didn't
carry what was needed.

## Rules

- Start at `README → INTEGRATION → CONTRACTS`; open anything else only when a trigger here names it.
- Never read the whole docset by default, and never read a document that can't change the work in hand.
- A missing document means its trigger never fired — fall back to the source, never assume "none".
- Read `LEDGER.md`'s `## Decisions` half before undoing a design that looks wrong, and `DEBT.md` before
  filing a defect against code that looks wrong. `## Run state` is the orchestrator's — never read it for
  design history, never edit it in a submission.
- A document disagreeing with the code is a finding to report, not a conflict to resolve silently.
- When two documents disagree, the order above decides, and the loser is reported as stale.
- The Tech Spec in hand outranks the docset; the source outranks every claim about what the code does.
