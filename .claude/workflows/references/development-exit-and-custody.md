# Leaving the Development Pipeline — the submission, its exits, and what else must travel

> **Read when any agent returns.** Split out of `feature-development.md` under the promotion rule in
> `client/feature-documentation.md`. It is the counterpart to `references/research-exit-and-custody.md`:
> that file says where a *decision* goes, this one says where **code and everything produced alongside it**
> goes. Nine agents return nine different envelopes here — more than any other pipeline — and an envelope
> field with no destination is a field that stops existing the moment the dispatch closes.

## One submission per agent return, not one bundle per feature

`code-reviewer` counts strikes against "the same submission" and CP3 is what aggregates a feature, so a
return goes out as its own submission the moment it lands — **on the GD's yes**, per
`references/optional-gates.md`. The feature-root documents are simply the last submission, never a bundling
step.

| Carried with every submission | Source |
|---|---|
| The code or diff in scope | The working tree. The pipeline supplies it — several envelopes report what now *works* rather than which paths changed |
| The spec section, or the **E2** direct notes | The same brief step 0 sent; the gate checks against what was actually asked |
| Which agent authored it | The dispatch record. Absent, the reviewer proceeds on a stated assumption that it did not write the code |
| The tier and the verification floor it owes | The ledger. `code-reviewer` judges `Verification done:` against the floor, not against its own expectation |
| The Implementation Note | Assembled here, per `.claude/rules/implementation-note.md` — with the two gaps below closed by the brief rather than guessed |

## The two Note fields no envelope carries — and how the brief closes them

`implementation-note.md` gives every field exactly one source. Two of them have **no source in any envelope
this pipeline dispatches**, so the brief asks for them explicitly per `references/development-brief.md`
rather than the assembler inventing a value:

| Field | Why the envelope cannot supply it | What the assembler writes |
|---|---|---|
| `Attempts:` | No implementing envelope has an attempts field. `orchestration.md` **I4** says attempts-used is knowable only at the return and is recorded by the caller — and `assurance-evaluator`, absent it, **assumes Attempt 1 and scores an iterated submission as a first pass** | What the agent stated back. Never a guess, and never a silent `1` |
| `Verification done:` | The rule names `Performance:`, `Responsiveness verified:`, `Cost:` and `Behaviour under loss and latency:` as its sources. **`csharp-engineer`, `server-authoritative-engineer` and `tech-lead-sdk-platform` carry none of them** — and the first of those is the Core, the one submission the fan-out waits on | What the agent stated back, and **why a check was unavailable when it was**. `effort-allocation.md` requires unavailable to be reported as unavailable; an unmet floor is the author's to close, an *unreachable* one is a stated limitation the GD decides on |

`tech-lead-sdk-platform` additionally has no `Assumptions and known limitations:` field at all — the field
`implementation-note.md` calls the highest-value one, and the field `Known limitations:` carries into
`DEBT.md` from **A3**. Its assumptions and its limitations are asked for in the brief and recorded here, or
an SDK submission reaches the gate with both rows structurally empty.

## The nine deliverables, and what each becomes

`feature-development.md` declares more `Produces` artifacts than any other pipeline, and every one of them
leaves through the same shape: a **submission**. Nothing here produces a document the GD reads directly.

| Produced | Becomes |
|---|---|
| **Shared Core Implementation** | the Core submission — the one the fan-out waits on, and the only one step 1 holds for |
| **Visual Effect** · **Client Integration** · **UI Implementation** · **SDK/Platform Integration** | one client submission each, in the order step 2 sets |
| **Netcode Protocol** · **Server Authority** | one backend submission each; the first's `Message contract:` is also the second's brief |
| **Deep Technical Solution** · **Performance Report** | a submission authored by the tech lead that wrote it — see the last section |

## Exits — this pipeline names its own doors

| What returned | Hands to | Shape |
|---|---|---|
| A submission, review **authorised** | `review-pipeline.md` **E1** | any |
| A submission, review **declined** — no verdict, no CP3 | `qa-pipeline.md` **E1** on a QA yes; otherwise the debt row and CP4 | any |
| A defect fix, review **authorised** | `review-pipeline.md` **E1**, then back to `qa-pipeline.md` **E3** | any |
| A defect fix, review **declined** | `qa-pipeline.md` **E3** directly — that pipeline declares this door as *"straight from the author where it did not [run]"* | any |
| The breakdown names no Core task and no existing API | `feature-intake.md` **E3** — **step 6 at D3–D5, the direct-notes hand-off at D1–D2**. Never step 6 at D1–D2: it does not run for that shape | branches |
| `netcode-engineer` → `Needs-decision`, `Routed to: cto` | `research-decision.md` **E2** — a technology question, never `cto` directly | any |
| `tech-lead-*` → `Needs-decision`, `Routed to: cto` | `research-decision.md` **E2**, same reason | any |
| `tech-lead-*` → `Needs-decision`, `Routed to: technical-architect` | `feature-intake.md` **E3** | branches, as above |

**`research-decision.md` **E2** is the technology door, whichever agent knocks.** Its entry row names
`technical-architect` because that was its first caller; this pipeline is the second, and the brief it sends
is the same one step 0 of that pipeline specifies. Never hand a bare `Routed to: cto` on — `cto` is barred
from returning open options, so it is never entered without a candidate set.

## Custody — what this pipeline produces that outlives the dispatch

Every row below is a field an agent returns that nothing downstream would otherwise receive. The submission
carries the code; this table carries the rest.

| Produced | Recorded in |
|---|---|
| `Public contract:` · `Determinism:` · `Message contract:` · `Authored:`/`Pipeline:` · `Core calls used:` | The next agent's brief — `references/development-brief.md`'s handoff matrix |
| `Assumptions and known limitations:`, from any agent | The Implementation Note, then `DEBT.md` from **A3** per `feature-documentation.md` |
| `Performance:` · `Cost:` · `Before / After:` — every measured number | The ledger's **`Baseline:`** row. `state/README.md` states what that row protects: *a run silently becoming the baseline*. A measurement nobody wrote there is a baseline nobody can compare against next time |
| `Pattern decision:` with **`Scope of pattern: project-wide`** | The feature root's `LEDGER.md` `## Decisions` half **and** `<state-root>/project-state.md`, because it binds submissions in roots this feature will never touch. This is `cto`'s `Standard set:` one level down — and at **A1–A2**, where no document is owed, `project-state.md` is its only home |
| `Root cause:` from either tech lead | The `## Decisions` entry beside the pattern it produced — a fix whose cause is unrecorded is re-escalated by the next session |
| `Config required:` · `Risks flagged:` · `Store policy addressed:` | **Straight to the GD, on any status** — see below |
| `Rejection behaviour:` · `Tick and cadence:` | The submission, and the QA plan: they are what a coverage assignment tests against, and neither is derivable from the code alone |
| Attempts used, and a **Continuation Debt Record** where the budget ran out | The ledger, whole. One strike, never a free retry, per `references/loop-termination.md` |

## Three returns that do not wait for an exit

**A design flaw goes to the GD immediately — invariant I5.** Any of the nine agents can find one, and it is
never folded into a later report or re-filed as an ordinary defect. The live case this rule was written
against came from `tech-lead-sdk-platform` on a *first* dispatch: a client-side feature flag governing an
action the server re-simulates authoritatively, which no SDK-layer decision can fix. Forward it, then resume.

**`Config required:` and `Risks flagged:` travel whatever the status says.** They are the only place a store
rejection, a missing credential source or a compliance gap is stated, and `Blocked` is the status they most
often arrive on — the agent found the hazard *and* something it needed. Answering only the `Blocked` and
dropping the rest is the failure this row exists to prevent.

**Third-party content reaches `security-reviewer` before it lands, not after.** `security.md` §7 is explicit
that a `.unitypackage`, an Asset Store import or a vendored DLL "is never treated as adopted until
`security-reviewer` has cleared it" — and that file carries no tier exemption and no lane exemption. This is
**not** the optional gate: the optional gate judges a submission afterwards, and by then the `Editor/` folder
with its `[InitializeOnLoad]` payload has already run. Route the import at `review-pipeline.md` **E1** as its
own submission before the integration is written, and say so in the ask.

## Code that a tech lead wrote is a submission

Both leads hold `Write`/`Edit` and both return `Fix: <what changed, and where>`. The escalation lane is
silent to the **GD**, which is not the same as silent to the **gates**: `orchestration.md` **I10** says
source that reaches no gate is a hole, not debt, and every agent that writes `.cs` has a route to
`review-pipeline.md`.

A lead's fix returns as its own submission, authored by that lead, and it carries the escalating agent's
brief as its spec section — the gate cannot check "correct" against a task the lead was never given. It
enters the same gate offer as any other submission; the escalation being invisible to the GD is about the
*loop*, never about the code.
