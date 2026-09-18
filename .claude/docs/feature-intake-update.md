# `feature-intake.md` — Review and Update (working note)

> **Status: scratch.** The record of one pipeline's deep review on 2026-09-17, the ten findings it produced,
> the eight changes made against them, and the re-score afterwards. Kept so none of it has to be
> reconstructed from a conversation. Nothing in the layer points at this file; delete it once the open
> decisions at the end have been answered.

**Companion note.** `workflow-layer-assessment.md` holds the layer-wide review and its findings F1–F7, and
deliberately excludes this pipeline. This file is the other half. Where the two overlap, it is noted.

**Nothing here is committed.** Nine files sit changed in the working tree.

---

## Part 1 — Findings

Numbered I1–I10 in the order they were found. I9 and I10 came later than the rest, from cross-reading
`feature-intake.md` against `research-decision.md` and against the three agent contracts.

### I1 — The pipeline had no brief table

`feature-development.md` carries `references/development-brief.md`: seven rows, each keyed to a real
`If absent` behaviour, plus a handoff matrix naming which returned field feeds which later brief.
`feature-intake.md` had no equivalent. Step 1 mandated two attachments only — the GD's words verbatim, and
track state.

Measured against the agent contracts, that left four required inputs unsupplied.

### I2 — The Advisor/Critic loop blocked on its most common path

`references/intake-advisor-critic-loop.md` describes one round as:

```
advisor → Options → GD picks a direction → critic → Risk Findings → GD decides
```

"The GD picks a direction" is, in practice, one line — *"option B"*. But `critic.md` blocks on two inputs:

| Required input | If absent |
|---|---|
| The direction being proposed, in enough detail to attack | `Blocked` — *"a one-line summary yields only generic objections"* |
| What it is meant to achieve | `Blocked` — *"a risk is only a risk relative to a goal"* |

Nothing required the pipeline to expand the chosen option back into the full `### <Option name>` block
`advisor` returned, or to attach the feature's goal. A predictable, frequent `Blocked` that the caller caused.

`advisor` had a third, softer gap: it requires the constraints that would rule an option out, and absent them
it guesses and says which — producing a shortlist filtered for a project that does not exist.

### I3 — The Tech Spec envelope had no `Assumptions:` field

Verified by grep: the word "assumption" appeared exactly once in `technical-architect.md`, in the track-state
`If absent` row. The envelope carried `Acceptance criteria`, `Open design question`, `Module boundaries`,
`Client-server contract`, `Patterns chosen`, `Task breakdown` and `Documents owed` — and no place to record
what the architect decided for itself where the request was silent.

Every implementing agent's envelope has that field. `implementation-note.md` calls it *"the single
highest-value field: an unstated assumption is indistinguishable from a bug at review time."* The one
document the whole fan-out is measured against was the one without it, and CP2 is where the GD approves it.

### I4 — A Major change did not reset the Advisor/Critic round count

Three statements that did not compose:

- `references/entry-index.md`: the Advisor/Critic round number carries across every door, with two stated
  exceptions, neither of which is this.
- `change-request.md` enumerated what a change request resets — strike count, attempt budget, CP2/CP3/CP4
  rejection counts, root-cause reset. Five counters, and not this one.
- `change-request.md` Major row: the loop re-runs *"inside its 3-round cap."*

So a feature that spent two rounds reaching CP1, was built, and then took a Major change re-entered **E5**
with one round left for a direction that is by definition new — and reported non-convergence on it.

This is the class of defect `references/loop-termination.md` exists to catch: individually bounded loops that
compose into something unbounded or, here, under-bounded.

### I5 — Reclassifying at CP1 destroyed the original tier

The pipeline requires it: *"CP1 spends U down, so reclassify when it closes. Drop U to U1, recompute the
tier, write both into the ledger."* The ledger template carried one `Tier:` line, so the recompute overwrote
the classification that was in force while the loop ran.

Downstream consequence: `assurance-evaluator` scores effort against the tier. Effort spent inside the loop
was A5 effort; a ledger showing only the final A3 makes it read as overspending, and nothing tells the gate
otherwise.

### I6 — The research skip had nowhere to be recorded

Step 5 requires naming the package, API or existing system that covers a capability before skipping the
research branch — *"If you cannot name the package, API or existing system, you are guessing"* — and states
*"A skip is recorded, and travels to CP2."* No row in the ledger template held it. The sole piece of evidence
justifying the skip lived only in conversation context, which `state/README.md` itself calls *"not a safety
mechanism."*

### I7 — CP2 rejections had no taxonomy, while CP3 and CP4 both do

- CP3 splits: drift (→ `feature-development.md` **E3**) versus the spec being wrong (→ `change-request.md`).
- CP4 splits: defect (→ **E3**) versus change request (→ `technical-architect`).
- **CP2 did not split.** It routed everything back to the architect, bounded at 3.

But a CP2 rejection is two different things. *"This is not what I asked for"* is a drafting problem. *"Reading
this, I want something different"* is a direction problem that belongs at CP1 and that no redraft can reach.
The pipeline discovered the second kind only at the bound — three `technical-architect` dispatches to learn
what one question at the first rejection answers.

### I8 — A misquoted agent contract

Step 1 read *"without it the architect **silently** assumes client-only."* The contract says: *"Assume
client-only, write the spec so the Core stays server-reusable, **and state the assumption**."* The agent
declares it. Small — but in a layer whose value rests on quoting `If absent` behaviour precisely, one wrong
quote discounts the correct ones.

### I9 — A D1–D2 feature returning from research had no route back

The sharpest finding, and it spans two pipelines.

| Source | What it said |
|---|---|
| `feature-intake.md` | *"**D1–D2 runs steps 1, 2 and (if needed) 5**"* — so D1–D2 may take the research branch |
| `feature-intake.md`, E3 row | Resumes at **step 6** — unconditional |
| `research-decision.md`, step 5 exit | Hands **E1/E2** back at `feature-intake.md` **E3** — step 6, reaching **CP2** — unconditional |

Step 6 writes the Tech Spec and runs at **D3–D5 only**. CP2 fires at **D3–D5 only**. So a D1–D2 feature that
needed a package the project lacks returned to a step that does not run for it and a checkpoint that does not
fire for it. Followed literally it produces a Tech Spec for a one-role change — `effort-allocation.md`'s own
named example of an artifact-budget violation.

**The diagram in `feature-intake.md` was already correct.** Its `Resume{Resume on the classified shape}` node
branches D1–D2 to the direct notes and D3–D5 to the spec. The two tables did not, and `research-decision.md`
was written against the wrong half.

**`verify-workflow-layer.ps1` passed 75/75 with this defect present.** It checks structural claims — every
door has an index row, no dangling pointer, no orphan reference — and cannot check semantic routing
consistency. This is direct evidence for finding **F5** in the companion note.

### I10 — No agent may rank an architecture direction

A design question, not a defect, and it is still open.

`research-decision.md` draws a clean two-way boundary: design precedent belongs to `advisor`, missing
technology belongs to `researcher`. A third kind falls between them — *how should we structure this, using
what we already have?* It reaches the Advisor/Critic loop because no capability is missing, and there:

- `advisor` is barred from ranking — *"Never conclude, recommend, or rank toward a single right answer."*
- `critic` only attacks the option the GD already leans toward; it never compares.
- `cto` owns strategic *technology*, not structure.
- `technical-architect` — the role that owns module boundaries and can read the codebase — is not consulted
  until step 6, after the direction is locked.

So at D4–D5 a Game Designer chooses between architecture patterns with no ranking and no engineering
recommendation. That may be the intended consequence of the GD being the single decision-maker. It may also
be a misallocated decision. **It is the GD's call, and it has not been made.**

---

## Part 2 — Changes applied

Eight changes across nine files: **+101 / −12 lines**. No new agent call, no new pipeline step, no new
checkpoint.

| # | Change | Closes | Files |
|---|---|---|---|
| 1 | A dispatch-brief table for the loop — six rows, each keyed to a real `If absent`, plus the `advisor`→`critic` handoff row | I1, I2 | `references/intake-advisor-critic-loop.md` |
| 2 | `Assumptions:` added to the Tech Spec envelope, with a binding guardrail and a row in the omissions table | I3 | `technical-architect.md`, `references/intake-tech-spec.md` |
| 3 | The **E3** return branches on shape in both files that state it | **I9** | `feature-intake.md`, `research-decision.md` |
| 4 | A Major change resets the Advisor/Critic round count — stated in all three places that own a counter | I4 | `change-request.md`, `references/entry-index.md`, `references/loop-termination.md` |
| 5 | `Tier history:` and `Research:` rows added to the ledger | I5, I6 | `state/templates/feature-ledger.md` |
| 6 | CP2 rejections split into two kinds, asked on the **first** rejection | I7 | `feature-intake.md`, `references/intake-tech-spec.md` |
| 7 | `Open design question:` classified `design \| architecture \| technology \| none`, and consumed at D3 | D3 hole, I10 visibility | `technical-architect.md`, `feature-intake.md`, loop file |
| 8 | The track-state quote corrected | I8 | `feature-intake.md` |

### Two judgment calls worth recording

**The brief was folded into `intake-advisor-critic-loop.md` rather than given its own file.** The original
proposal was `references/intake-brief.md`, for symmetry with `development-brief.md`. That symmetry is not
load-bearing: the development brief serves seven agents spread across a whole pipeline, while this one serves
two agents that exist only inside a loop which already has its own file with room to spare. Folding it in
keeps the dispatches documented with the loop that makes them, and avoids a new file, a new pointer and a new
README row. It also kept `feature-intake.md` off its 200-line cap, which it is sitting exactly against.

**I10 was documented, not decided.** Granting `technical-architect` a `Recommended direction:` field would
change who decides architecture on this project — a change to its philosophy, not a defect fix, and the GD's
to make. What was written instead is the limitation itself, stated plainly in the loop file, together with
the existing escape: a mode-3 dispatch to `technical-architect` before locking CP1. An invisible hole became
a known constraint with a stated workaround. **The decision remains open.**

---

### Two more, added after the first pass

**9 — Routing is now machine-checked.** `tools/verify-workflow-layer.ps1` gained two claims, and they are the
first semantic ones in it:

- *An entry resuming at a shape-gated step states the shape.* It parses each pipeline's step table, marks any
  step whose `Runs for` cell is gated on **D**, and requires every entry row resuming there to name a shape.
  This is exactly I9's class.
- *No file sends work to a door the target pipeline does not declare.*

**Negative-tested.** Reverting the I9 fix makes the first claim fail with
`step 6 runs at 'D3–D5' and this row names no shape`; restoring it passes. The check is therefore proven to
catch the defect it was written for, at **E2**, rather than asserted to.

**It found two more the moment it ran:**

| Found | What it was |
|---|---|
| `feature-intake.md` **E2** → step 3 | Step 3 is the Advisor/Critic loop, gated at D4–D5 or U3. E2 named no shape. True by implication — the feature is already in the loop — but unstated, and the same latent ambiguity as I9 |
| A sentence naming `change-request.md` **E4**/**E5** | Those are `feature-intake.md`'s own doors. `change-request.md` declares E1 and E2 only, so a reader following the sentence literally looks for a door that does not exist |

Both fixed. The claim count went 75 → 78.

**10 — One owner named for the gate offer** (**F6** in the companion note). `optional-gates.md` now states the
split explicitly: it owns the ask's **shape**, the pipeline that reaches a boundary owns **where** it fires,
and the orchestrator owns every ask belonging to no pipeline. "The orchestrator asks the GD" was shorthand
for the third case and read as if it were all three.

---

## Part 3 — Verification

| Check | Result | Evidence |
|---|---|---|
| `tools/verify-workflow-layer.ps1` | **OK — 78 claims checked, every one holds** | E2, tool output |
| The new routing check against the defect it was written for | **Reverting I9 → FAIL; restoring → PASS** | **E2 — negative-tested, not asserted** |
| 200-line cap | `feature-intake.md` **199**, unchanged — every edit to it was in-place inside a table cell or a sentence | E2 |
| Other files against the cap | `research-decision.md` 193, all references well under | E2 |
| Diff scope | 9 files, +101 / −12 | E2, `git diff --stat` |

**What was not verified.** No pipeline was executed. The routing claim is now negative-tested at **E2**, so
I9 specifically is no longer a matter of inspection — but the other nine findings' fixes remain **E1 —
direct inspection**, and the two structural sections of the verifier passed identically *before* these
changes, with I9 present. A passing run still means the layer's claims about itself hold; it does not mean
the layer works.

---

## Part 4 — Scores

### This pipeline: 7.0 → 9.0

| Axis | Before | After | What moved it |
|---|---:|---:|---|
| Entry points and addressing | 7.5 | **9.5** | I9 closed in both files; the D3 detector now exists |
| Agent-brief contract | 5.0 | **8.5** | I1, I2 — six inputs, each keyed to an `If absent` |
| Checkpoint logic | 7.5 | **9.0** | I7 — CP2 now splits like CP3 and CP4 |
| Counters and caps | 7.0 | **9.0** | I4, I5, I6 |
| Honesty about its own gaps | 9.0 | **9.0** | Held deliberately — see below |

**A correction to the first score.** The original review gave addressing **9.5**, before I9 had been found.
I9 *is* an addressing defect, so the honest pre-fix figure was **7.5**, and the pipeline's honest starting
total was **7.0**, not the 7.5 first reported. Part of the movement above is a corrected grade, not an
improvement.

**Why "honesty" was held flat.** `effort-allocation.md`: *"The author never scores their own work.
Self-review is not independent verification."* Most of the changed lines are the reviewer's own. Scoring them
is **E0 — unsupported assertion** on this project's own scale. The four axes that moved should be read as a
proposed grade awaiting an independent pass, not a verdict.

**Why 9.0 is the ceiling.** `effort-allocation.md` requires **E3 evidence or better** above 9.5, and
*"Reading code is review; running it is verification."* This pipeline cannot pass roughly 9.0 until it has
run once — one D1–D2 feature that takes the research branch would prove I9 closed at E2 instead of E1.

### The layer: 7.5 → 7.5

Unchanged, and not rounded up. Two axes moved back to their originally-stated values after I9 and I4 were
closed — both had been over-graded before those findings existed. **Enforceability (4.5)** and **operational
readiness (3.5)** did not move at all, because no prose change can reach them.

One honest debit: 101 lines of prose were added to a layer already criticised for its prose-to-mechanism
ratio (**F5**). They went into on-demand reference files rather than the always-loaded rules, so no agent
pays more context for them — but it is a cost, not a gain.

---

## Part 5 — The path to a layer score of 9.0

Seven axes averaging 9.0 needs a total of **63**. The current total is **51**.

| # | Work | Axis | Est. |
|---|---|---|---:|
| 1 | A `SessionStart` hook that prints the router's step 0 and reads `project-state.md` — turns **F1** from a sentence into a mechanism | Enforceability | +1.0 |
| 2 | **Extend `verify-workflow-layer.ps1` with semantic routing checks** — the exact class that let I9 through: every entry's `Resumes at` must exist at every D its pipeline permits for that entry | Enforceability | +1.0 |
| 3 | A helper script that appends one transition row to a ledger — turns **F2**'s manual tax into one command | Enforceability | +1.0 |
| 4 | A `PreToolUse` hook warning when a dispatch runs with no ledger row for an in-flight feature — a detector for **F2** | Enforceability | +0.5 |
| 5 | **Run one feature end to end**, even D1–D2. Creates the first `.workflow/` and the first calibration row | **Readiness** | **+4.5** |
| 6 | Finish **F4** — move `commit-message.md` and the iteration half of `execution-loop.md` out of always-loaded | Cost | +1.5 |
| 7 | Close **F6** — one home for who makes the gate offer | Consistency | +0.5 |
| 8 | Give the remaining six pipelines the treatment this one just had | Architecture, coverage | +1.0 |

Roughly **+11**, reaching **62/7 ≈ 8.9**. Item 5 alone is 4.5 of it, and it is not writing. **Until the layer
has run once, its ceiling is about 8.0.**

---

## Part 6 — Open, for the GD

1. **I10** — should `technical-architect` be allowed to recommend on an `architecture` direction, or does the
   GD keep that call unaided? Currently documented as a known limitation with a workaround.
2. **Commit** — nine files are uncommitted in the working tree.
3. **Next** — item 2 in Part 5 was offered and not yet started: write the verifier check that would have
   caught I9, regression-test it by temporarily reverting the fix, then restore.

---

## Part 7 — Re-evaluated against a real run: 9.0 → 8.2

The 9.0 above was scored on a pipeline that had been **read**, never executed. It has now been executed —
five real agent dispatches, steps 1 through 5 plus CP1, on a live-title voice-chat feature classified
A5 / D4 C4 U3 R2 X2. The run record, the full findings and the proposed fixes are in
`research-decision-update.md`. What it did to this pipeline's score:

| Axis | Part 4 | After the run | What moved it |
|---|---:|---:|---|
| Entry points and addressing | 9.5 | **7.5** | **R2** — the `technical-architect` → `cto` row hands a *pre-CP1* escalation back at step 6, skipping the loop and CP1. The I9 family again, in the one row the last pass did not check. Plus **R1**, below |
| Agent-brief contract | 8.5 | **8.0** | The loop brief table **held live** — `critic` returned `Blocked … none`, which is what it was written to prevent. Against that: step 6 has no brief specification at all, and `advisor`'s constraint list omits the social graph (**R4**) |
| Checkpoint logic | 9.0 | **7.5** | **R6** — "CP1 spends U down … drop U to U1" is unconditional. At D4–D5 CP1 always precedes step 5, so it disarms `research-decision.md` **E4** for exactly the shape most likely to need it |
| Counters and caps | 9.0 | **9.0** | Held — nothing found |
| Honesty about its own gaps | 9.0 | **9.0** | Held |
| **Result custody** *(axis the run forced into existence)* | — | **4.0** | **R5** — `critic` returned 11 ranked findings, four of them acceptance-criteria gaps, and `intake-tech-spec.md` never mentions `critic`, Risk Findings or accepted risks. They die at CP1 |

**8.2** on the original five axes, **7.5** including custody.

Two findings land on work done in *this* note, and both are worth stating plainly:

- **I3's `Assumptions:` field worked.** The architect returned eleven of them, including "push-to-talk is
  assumed as the default input mode" — which `critic` then attacked as its Critical #1. That is the field
  doing precisely what Part 1 claimed it would.
- **Change 7's classified `Open design question:` did not.** It is single-valued, and the live D4/U3
  classification legitimately had a `technology` question *and* three `design` questions at once. The
  architect had to put the design half in prose outside the envelope (**R3**). A defect introduced by a fix,
  found only by running it.

The honest reading: **the 9.0 was 0.8 points of optimism plus one unscored axis.** That gap is the difference
`effort-allocation.md` names between review and verification, measured.

---

## Part 8 — R1–R6 closed, and the seam with `research-decision.md` joined

Part 7 re-scored this pipeline **8.2** after running it, and left its six findings proposed rather than
fixed. They are fixed now, in the same round that closed `research-decision.md` — deliberately together,
because three of the six are one half of a join whose other half lives in that file.

### What changed

| Closes | Change | Where |
|---|---|---|
| **R1** | `technical-architect`'s §4-vs-§6 contradiction resolved **without forcing one value**, because both were right for different cases: the *whole request* being a `cto` question is `Rejected` (misaddressed, no feature work held); hitting one part-way through classifying or specifying is `Needs-decision` (the work is real and partly done). §6 now states the distinction; the pipeline routes both | `technical-architect.md`, `feature-intake.md` |
| **R2** | The architect→`cto` routing row **split by origin**. From **step 2** — pre-CP1 — it returns at **E2**, step 3 at D4–D5/U3 and **E3** where that shape fires no loop; from **step 6** it returns at **E3**. One row was covering both and picking the step-6 answer, which on the live D4/U3 run would have skipped steps 3, 4 **and CP1** | `feature-intake.md` |
| **R3** | `Open design question:` is now **one line per question, each tagged**, and the caller **routes per line**. The old field was single-valued while a D4/U3 feature legitimately holds a `technology` question and several `design` ones at once — which is how the loop's trigger and its payload came apart | `technical-architect.md`, `feature-intake.md`, `research-decision.md`, `intake-advisor-critic-loop.md` |
| **R4** | The **social graph** added to `advisor`'s constraint list, with the live return that earned it quoted in the row | `intake-advisor-critic-loop.md` |
| **R5** | `## What the step 6 dispatch must carry` written — the table every other dispatch in the layer already had. CP1's row now states that `critic`'s remaining findings are **not discarded**, because several are routinely acceptance-criteria gaps | `intake-tech-spec.md`, `feature-intake.md` |
| **R6** | **CP1 spends down what CP1 settled**, not the whole axis. A `technology` line still open holds U where it is; dropping to U1 unconditionally disarmed `research-decision.md`'s **E4** for exactly the D4–D5 shape that most needs it, since CP1 always precedes step 5 there | `feature-intake.md` |

### The seam, and a defect found inside this round's own work

The step 6 dispatch table is where `research-decision.md`'s new custody chain lands. Written separately they
would not have met: that pipeline now hands back a Technical Decision, a `Standard set:`, a `Picture taken:`
date and a provisional re-open threshold, and before this round **step 6 had no specification of what it
receives at all**, so all four would have been dropped at the door.

**A cross-check caught R2 still live in the file written to fix it.** `research-exit-and-custody.md`, created
earlier the same session, sent **E2** back at step 6 unconditionally — the same defect, in the same shape, in
new text. It was found by grepping the seam rather than by re-reading, which is the only reason it was found
at all. Both files now split that row the same way, and each names the other.

`intake-advisor-critic-loop.md` was also still describing the question field as single-valued in two places,
and `advisor`'s brief row now says it receives the `design` and `architecture` lines — **all of them, never
one standing in for several, and never the `technology` line**.

### Verification

| Check | Result |
|---|---|
| `tools/verify-workflow-layer.ps1` | **OK — 80 claims, every one holds** (E2) |
| 200-line cap | `feature-intake.md` **199**, `research-decision.md` **199** |
| The seam, both directions | Grepped, not assumed — and that is what found the R2 recurrence |
| The checklist's own stale count | "52 machine-checked claims" corrected to **80** |

### Score — 8.2 → 8.9

| Axis | Part 7 | Now | What moved it |
|---|---:|---:|---|
| Entry points and addressing | 7.5 | **9.0** | R1 and R2, on both sides of the seam |
| Agent-brief contract | 8.0 | **9.0** | Step 6 has a carry table; `advisor`'s constraints and payload both corrected |
| Checkpoint logic | 7.5 | **9.0** | R6 — CP1 spends down only what it settled |
| Counters and caps | 9.0 | **9.0** | Held; nothing found |
| Honesty about its own gaps | 9.0 | **9.0** | Held |
| Result custody | 4.0 | **8.5** | R5 closed; the three-of-five caveat below |

**8.9** on five axes, **8.9** on six. **Not 9.0**, and the reason is the same one that capped
`research-decision.md`: several destinations are rows in a ledger template that has never been instantiated,
and nothing written this round has been executed. **R3's fix in particular replaces a field that a live run
falsified — with a field no live run has yet touched.**

Scored by the author of the fixes: **E0**, awaiting an independent pass.

### What is deliberately still open

- **I10** — whether `technical-architect` may rank an `architecture` direction. Untouched on purpose; it is a
  philosophy decision, and the checklist's debt row still reads `Open`.
- **Fix J** — the two verifier checks that would make the custody class machine-checked rather than written
  down. It is the only remaining route to 9.0 that does not require a real Unity project.
