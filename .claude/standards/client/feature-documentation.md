# Client Track — Feature Documentation

Applies to: C# Software Engineer, Unity Engineer, UI/UX Programmer, Tech Lead – C# Unity, Tech Lead – SDK/Platform, Tech Lead – Performance, Technical Artist. Also to Netcode Engineer and Server-Authoritative Logic Engineer for a `Game.Server.*` feature root, when the backend track is active.

## Relationship to other rules

This file governs the durable, in-repo documentation a feature carries, on top of the per-submission Implementation Note already required by `coding-principles.md`'s Handoff section. The Implementation Note is a point-in-time handoff to Code Reviewer for one submission; the documents required here stay accurate for as long as the feature exists in the codebase. They do not replace the Tech Spec (what was decided, and why) — they record what actually got built and how to use it.

This file owns the **writing** side: which documents a feature root carries, what goes in each, and when each becomes owed. `.claude/rules/feature-context-reading.md` owns the **reading** side — which of them a new agent or session opens for a given task, in what order, and what happens when they disagree. Neither is a substitute for the other: a document nobody is required to read is waste, and a reading order over documents nobody wrote is empty.

## The docset — seven documents, written one at a time

A feature root can carry up to seven documents. They are **not** a checklist to satisfy at completion. Each exists to answer exactly one question, and each is written only when something in the work has actually produced that answer.

| File | Holds | Never holds |
|---|---|---|
| `README.md` | What the feature does, which Tech Spec it implements, its entry points, the map of its main files/classes, and which features consume it | The Tech Spec's requirements text |
| `CONTRACTS.md` | The external contract: public API, interfaces, events, data schemas, invariants, and the behavior callers are entitled to rely on | Anything internal — that is what makes it a contract |
| `INTEGRATION.md` | How another feature talks to this one: integration points, extension points, which API/event to use, where logic may be added, and which classes must not be called directly | A restatement of the public API — `CONTRACTS.md` owns the signatures, this owns the usage |
| `ARCHITECTURE.md` | The inside: components, data flow, dependency direction, which part owns which logic, and the main processing path | Anything a caller outside the root needs |
| `LEDGER.md` | Decisions that would otherwise be silently undone: what was decided, why, what was rejected, and what it constrains going forward | A changelog — git already has one |
| `DEBT.md` | Known technical debt: current workarounds, limitations, code needing refactor, risky areas, and the intended fix | An open defect — that is `defect-reporting.md`'s job |
| `NOTES.md` | Observations, edge cases, discoveries, and undecided ideas that are not yet a contract and not yet debt | Anything another document already owns |

**One fact, one home.** A fact duplicated across two documents goes stale in one of them, and the reader cannot tell which. Cross-link instead of copying, in both directions.

**Never create an empty or placeholder file.** A `CONTRACTS.md` containing only headings tells a reader the feature has no invariants, which is worse than its absence — `feature-context-reading.md` treats a missing file as "the trigger never fired" and falls back to the source, which is the correct behavior. A file whose trigger has not fired is not written.

## When each document becomes owed

Two conditions, both required: the feature has reached the **tier floor**, and the document's **trigger** has actually fired. Neither alone is enough — an A4 feature with no cross-feature seam does not owe `INTEGRATION.md`, and a real seam inside an A2 change does not owe one either.

The floor is the **assurance tier** from `.claude/rules/task-classification.md`, assigned by `technical-architect` at intake and held in that feature's ledger. It keys to **A**, not to D: a feature earns documentation because getting it wrong is expensive, which is what C, R and X measure — a D2 change to an economy path classifies A4 and is worth documenting, while a genuinely hard D4 refactor of throwaway tooling is not.

| File | Tier floor | Trigger — it becomes owed the moment this is true |
|---|---|---|
| `README.md` | **A4** | The feature is functionally complete and going to Code Reviewer for final sign-off. This is the anchor: no other document in the set exists without it |
| `CONTRACTS.md` | **A4** | Code outside the feature root calls into it, the Tech Spec names a cross-layer or client-server contract, or the feature is multiplayer-relevant — anywhere client and server must agree on the same rule |
| `INTEGRATION.md` | **A4** | A second feature actually integrates with this one, or the feature ships a deliberate extension point somebody else is expected to use |
| `ARCHITECTURE.md` | **A4** | The feature spans more than one physical root or layer (`Game.Core.*` plus `Game.Client.*`), or its internal data flow cannot be stated in a paragraph inside `README.md` |
| `LEDGER.md` | **A3** | A decision was made that a future reader would otherwise undo — a rejected alternative, a non-obvious constraint, the outcome of an Advisor⇄Critic round, or a tech-lead escalation resolved |
| `DEBT.md` | **A3** | A limitation or workaround is carried past review — including a gap the GD accepted at CP4, per invariant I6 in `orchestration.md` — or an obsolete-API call site was flagged and left in place per `coding-principles.md` |
| `NOTES.md` | **A3** | Optional, always. Written when an observation would otherwise be lost, never because the docset "should" have one |

**A1 and A2 owe nothing new.** A change at that tier writes no document under this rule. It still updates any existing document its change makes stale — that is maintenance, not creation.

**`LEDGER.md` and `DEBT.md` drop to the A3 floor on purpose.** They are append-only and cost a few lines, while their absence causes exactly the two failures the reading flow exists to prevent: a deliberate decision undone by the next session, and known debt re-reported as a fresh defect. Every other document stays A4-and-above — writing one for an A3 change is the bureaucratic overhead KISS and YAGNI in `coding-principles.md` warn against, and the artifact budget in `effort-allocation.md` forbids outright.

**Reclassification applies forward.** If a feature's tier rises mid-flight — `change-request.md` re-reads every axis, and new scope or a newly touched economy path genuinely moves D or C — the documents at the new floor are owed from that point, same as the rest of that tier's process. When a tier is genuinely unclear, ask `technical-architect` — never guess a feature down to skip a document, and never write one speculatively. A tier that rose only because **U3** was unresolved falls again when CP1 spends it down, and the documents fall with it.

## Start inside `README.md`, promote out of it

The docset grows from one file, it does not arrive as seven.

1. An A4-or-above feature's first document is `README.md`, and it carries its contract, its integration notes and its internal structure **inline**, as short sections.
2. When one of those sections grows past what a reader can hold — roughly, past the point where it buries the rest of the README — it is **promoted** into its own file from the table above.
3. The README then keeps a one-line pointer to the promoted file, not a copy of it.

Promotion is the mechanism the whole rule turns on: a document exists because content earned it, never because a template listed it. A feature that never outgrows its README is fully documented with one file, and that is a correct outcome, not an incomplete one.

## `README.md` — the required minimum

However small the feature, its README covers these four, each in as little as a sentence:

1. **Overview** — what the feature does, and which Tech Spec it implements. Link the spec; never re-explain its requirements.
2. **Entry points** — where execution starts: the MonoBehaviour, the service, the event that triggers it.
3. **Map** — the main files/classes and what each is responsible for, stated so a reader does not have to reverse-engineer it. Name the dependency direction explicitly: `Game.Client.*` depends on `Game.Core.*`, never the reverse.
4. **Consumers** — which features or systems already use this one, where known.

Everything else — invariants, integration points, internal data flow, decisions, debt — starts as an inline section here and moves out under the promotion rule above.

## Placement

- Documents sit at the **feature root**: the top-level directory holding that feature's code. One set per root, at its top level — never one per class, and never buried where it is not the first thing a reader finds.
- When a feature's Core and Client code live in genuinely separate physical roots (a Shared Core folder and a Unity `Assets/` feature folder), **each root gets its own set**, and each links to the other instead of duplicating it. `CONTRACTS.md` belongs to the root that owns the contract — normally the Core root — and the Client root points at it.
- Filenames are exactly as written above, uppercase, at the root. A reader and an agent both find them by name.

## Ownership and maintenance

- Whoever implemented the feature writes its documents. When a feature spans several roles, they share one set per root and each section states which layer it describes — never split one feature's documentation across disconnected files.
- **`LEDGER.md` and `DEBT.md` are written at the moment, not at the end.** A decision recorded a week later is a reconstruction; a limitation recorded at completion has usually already been forgotten. Both are appended in the same submission that produced them.
- These are living documents. A later Tech Spec change that modifies the feature updates the affected documents **in the same submission** — a stale document is treated as seriously as a stale test. A change that invalidates an entry in `LEDGER.md` supersedes that entry in place rather than deleting it; the superseded reasoning is what stops the next session re-litigating it.
- Content promoted out of `README.md` is moved, not copied — the README is left with a pointer.

## The review gate

`code-reviewer` checks documentation only on a submission that represents a **feature-complete** state, never on an incremental in-progress commit. What it checks:

- Every document whose tier floor and trigger have both fired exists, and is accurate against the code it describes.
- No document contradicts the code. A `CONTRACTS.md` that disagrees with the implementation is a finding against the submission, regardless of which one is wrong.
- No empty or placeholder document was added to look complete.

What it does **not** do: request a document whose trigger has not fired. "The docset is incomplete" is not a finding — the docset is complete when the documents that were earned exist. Missing or stale documentation that *was* earned is grounds for "request changes", same as any other rule in `coding-principles.md`.

## Rules

- Never write a document before both its tier floor and its trigger are met, and never write an empty or placeholder one.
- A1/A2 creates nothing; it only updates what its change made stale.
- `README.md` is the anchor — no other document in the set exists without it, and an A4-or-above feature is not complete without it at each feature root.
- Content starts inline in `README.md` and is promoted into its own file when it outgrows it; promotion moves the content and leaves a pointer, never a copy.
- One fact, one home — cross-link between documents instead of duplicating, and never duplicate the Tech Spec's requirements text into any of them.
- `LEDGER.md` and `DEBT.md` are appended in the submission that produced the decision or the limitation, not reconstructed at the end.
- A Tech Spec change that touches a documented feature updates that feature's affected documents in the same submission.
- Keep each document scoped to its own feature root — never document an unrelated system inside it.
- A reviewer checks the documents that were earned; it never demands one whose trigger has not fired.
