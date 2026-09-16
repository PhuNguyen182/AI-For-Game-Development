# Shared — Feature Context Reading

Applies to: every agent and every new session, in every mode — a full pipeline run, a single agent dispatched
directly, or the orchestrator working an input itself. Like `language-and-comments.md`, this file sits above
the `.claude/rules/<group>/` folders rather than inside one.

Source: `.claude/docs/frame/AI Context Reading Flow.md`, adapted to this project's tiers, roles and review
gates. This file is self-contained — it does not require that document to be present.

## Why it exists

Every agent here is isolated and stateless: it sees one dispatch brief and whatever it reads from disk, never
the conversation or the session that produced the code in front of it. Two failure modes follow, and this
file sits between them:

- **Reading nothing** — the agent infers intent from code alone, re-derives a decision somebody already made
  deliberately, and breaks a contract the code never states.
- **Reading everything** — the agent ingests a feature's whole docset and source before touching one field,
  spending context and a dispatch on material that could not have changed the work.

The rule is therefore not "read the documentation". It is: **read the minimum context that makes the task
safe, in an order that reaches the dangerous unknowns first.**

## Relationship to other rules

`.claude/standards/client/feature-documentation.md` owns the writing side — which documents a feature root
carries, what goes in each, and when each becomes owed. This file owns the reading side only: which of them a
given task must open, in what order, and what to do when they disagree with each other or with the code.
`orchestration.md` governs what a dispatch must carry; this file governs what the dispatched agent reads once
it arrives.

## The docset

A feature root can carry up to seven documents. None is guaranteed to exist — each is written only when its
trigger fires, per the authoring rule.

| File | The question it answers | Default |
|---|---|---|
| `README.md` | What is this feature, where does it start, what uses it | Read first, always |
| `INTEGRATION.md` | How do I talk to it from outside, and what must I not call | Read, unless the task stays entirely inside the root |
| `CONTRACTS.md` | What must not break | Read before writing anything |
| `ARCHITECTURE.md` | How does it work inside | Only when changing the inside |
| `LEDGER.md` | Why is it built this way | Only when a design looks wrong |
| `DEBT.md` | What is already known to be wrong | Only when the code looks wrong |
| `NOTES.md` | What is not yet worth a contract | Only when the rest came up short |

`LEDGER.md` at a feature root is that feature's **decision history**. It is not
`.claude/workflows/state/<feature-slug>/ledger.md`, which is that feature's **run state** — tiers, strike
counts, checkpoint position. Both are now per-feature, so the filename alone no longer separates them: the
distinction is **uppercase, beside the code** for documentation versus **lowercase, under `.claude/`** for
state. Reading one for the other wastes a dispatch.

**Absent is not empty.** A file is missing because its trigger never fired, not because the answer is
"nothing" — fall back to the source for that question rather than concluding the feature has no contract, no
debt, or no history. If a file the authoring rule clearly owes is missing on a feature-complete submission,
that is a finding for `code-reviewer`, not something the reader silently writes.

## The default flow

```text
Task
  ↓
README
  ↓
INTEGRATION
  ↓
CONTRACTS
  ↓
the source those three named
```

This covers most tasks. Everything below is a deviation from it, each with its own trigger.

## Flow by task shape

| The task | Read, in this order | Leave closed unless a trigger below fires |
|---|---|---|
| **Use a feature** — call it, bind to it, no change inside | `README` → `INTEGRATION` → `CONTRACTS` → implement | `ARCHITECTURE`, `LEDGER`, `DEBT`, `NOTES` |
| **Change a feature** — logic inside one root | `README` → `CONTRACTS` → `ARCHITECTURE` → `INTEGRATION` → the source | `LEDGER`, `DEBT`, `NOTES` |
| **Connect features** — a seam between two or more | per feature: `README` → `INTEGRATION` → `CONTRACTS`; then trace `Feature A → integration point → contract → integration point → Feature B` | the `ARCHITECTURE` of any feature you are not changing inside |
| **Debug** | `README` → `CONTRACTS` → reproduce and trace the source → `ARCHITECTURE` → `DEBT` → `LEDGER` | `NOTES`, until the rest came up short |
| **Review code** (`code-reviewer`, `security-reviewer`) | the Tech Spec or brief → `CONTRACTS` → the diff | `ARCHITECTURE`, until the diff moves logic between components or across a layer boundary |
| **Test** (`qa-lead`, `qa-automation-engineer`, `playtest-tester`) | `README` → `CONTRACTS` — its invariants are the assertions — then `DEBT`, so known debt is not filed as a fresh defect | `ARCHITECTURE`, `LEDGER`, `NOTES` |
| **New feature root**, no docset yet | the Tech Spec → the `INTEGRATION` and `CONTRACTS` of every feature it touches | its own docset — that is written at completion, not read at the start |

An **A1/A2** change against a root with no docset reads the source it touches and nothing else. Opening a
docset that does not exist is not a step, and inventing one to read is not either. Note that the tier gates
what a change **writes**, never what it **reads**: an A1 change to a feature that carries a `CONTRACTS.md`
still reads it before touching anything, because the invariants bind the code regardless of who is editing.

## When to open the conditional four

**`ARCHITECTURE.md`** — the task changes logic inside the feature, touches several components at once, adds a
component, changes data flow, is a refactor, or the ownership of a piece of logic is unclear from `README`.

**`LEDGER.md`** — a design looks wrong or arbitrary, you are about to change or undo an existing decision, or
you cannot tell why the system works the way it does. Read it *before* changing the thing that looks wrong,
not after: the whole point is catching a deliberate decision before undoing it.

**`DEBT.md`** — the task touches legacy code, a workaround, or a large TODO; the architecture in that area
looks unclean; you are considering a refactor; or a defect smells like an already-known limitation. It
settles one question: *is this a new bug, or debt somebody already accepted?*

**`NOTES.md`** — the other documents did not explain the behavior in front of you, you need an edge case or
an observation from an earlier session, or you hit behavior nobody has formalized. It is supplementary
context, never a source of truth.

## When sources disagree

Documents state intent. Source states what runs. They are not ranked against each other, because a gap
between them is itself a finding:

- **`CONTRACTS.md` disagrees with the code** — stop and report it per `.claude/standards/qa/defect-reporting.md`,
  citing both anchors. Which one is wrong is a decision for the owning agent or `technical-architect`, never
  a silent pick by whoever noticed it.
- **A document is stale against the code** — treat it as a stale test: report it, and do not build on it.
- **Two documents disagree** — take the higher of the two in the order below, and report the loser as stale.

```text
The Tech Spec or brief for the change in hand   ← the current decision
    ↓
CONTRACTS
    ↓
ARCHITECTURE
    ↓
INTEGRATION
    ↓
README
    ↓
LEDGER
    ↓
DEBT
    ↓
NOTES
```

The Tech Spec sits above the docset because the docset records what was built last and the spec is what is
being built now. The docset still governs everything the spec does not speak to — a spec silent on an
invariant does not repeal it.

Whatever the documents say, the implementation is checked in the source before it is relied on.

## Stop reading

Stop when the next document could not change what you are about to write. Concretely: you know the entry
point, you know which invariants your change must hold, and you know which callers your change is visible to.
Reading past that point is the avoidable cost KISS in `coding-principles.md` and the scope discipline in
`performance-and-algorithms.md` both warn about, spent on context instead of code.

Never re-read a document already quoted in the dispatch brief. Never read a feature's docset to decide
whether the task belongs to you — that is the brief's job, and `Status: Blocked` is the answer when it did
not carry what the agent needed.

## Rules

- Start at `README` → `INTEGRATION` → `CONTRACTS`; open anything else only when this file names a trigger for
  it.
- Never read the whole docset by default, and never read a document that cannot change the work in hand.
- A missing document means its trigger never fired — fall back to the source, never assume the answer is
  "none".
- Read `LEDGER.md` before undoing a design that looks wrong, and `DEBT.md` before filing a defect against
  code that looks wrong.
- A document that disagrees with the code is a finding to report, not a conflict to resolve silently.
- When two documents disagree, the order above decides — and the loser is reported as stale.
- The Tech Spec in hand outranks the docset; the source outranks every claim about what the code does.
