# Change Severity — the Major criterion's two shapes, splitting a bundled request, and what each envelope defers

> Promoted from `change-request.md` Step 3. Read when a Major reopens CP1 for a feature that never held one, or
> when one dispatch returns both a severity and a `cto` routing. Both are live-evidenced, not hypothetical: two
> real `technical-architect` dispatches against this pipeline hit exactly these two walls.

## The Major criterion has two shapes, not one

Step 3's original wording — *"it invalidates an assumption `critic` stress-tested, or a risk the GD accepted at
CP1"* — silently assumes every in-flight feature already has a CP1 to invalidate. That is false for any
feature classified **D1–D3 with U0–U1**: `feature-intake.md`'s own loop trigger never fires below D4–D5 or U3,
so `critic` never ran and the GD never accepted a risk at a checkpoint that never happened.

A live dispatch hit this directly: a D3/U1 progression feature took on real-money IAP, an economy dependency
and an open anti-cheat question mid-flight — reclassifying to D4/C4/U3/R3/X3. The architect could not point at
an invalidated CP1 assumption, because none existed, and refused to either force the change into Moderate by
elimination (which would skip the direction-vetting this scope genuinely needs) or invent a CP1 history that
never happened. It classified Major on the *functional* criterion instead: **the reclassified axes now require
CP1 for the first time.** Step 3 now states this as the criterion's second shape, explicitly.

**A first-time CP1 is a legitimate empty history, not an error to paper over.** It carries no prior round
(0 of 3, not "reset from some other number"), no ruled-out options, and no accepted risk to carry into E5 —
state `none` for each rather than fabricating one to fill the field.

## When one dispatch returns both a severity and a `cto` routing

A change can bundle two structurally different asks: a design/mechanic change this pipeline can rate, and a
strategic technology choice (a netcode foundation, a vendor swap) that is `cto`'s call regardless of how the
rest of the request is classified. A live dispatch hit this too: a mid-flight request to redesign a
tick-deterministic ability *and* swap the netcode foundation in the same GD message.

**The technology part gets no Minor/Moderate/Major label at all.** Severity measures how much a Tech Spec's
*structure* changes; a foundation swap is not rated by that scale, it is decided by `cto` and only *then*
acquires a severity for whatever its own downstream rework costs — almost always Major on its own, since it
typically replaces a delivered client-server contract outright, but that is `cto`'s and the next classification
round's call, not this one's.

**Sequencing: settle the technology question first, via `research-decision.md` at its own depth check and
research pass, before finishing the severity-rated part.** `cto` is never entered without a candidate set, so
the technology part enters at `research-decision.md` **E2** like any other strategic-choice route — it is not
a shortcut straight to a decision. The reason for settling it first is not procedural tidiness — a re-stress-
test of the design part (what `critic` re-tests at the reopened CP1) can materially depend on which foundation
is in play: an exploit or desync profile under one netcode foundation is not the same question under another.
Treating the two paths as independent and letting CP1 run before the technology question resolves risks
re-testing a direction against the wrong foundation and having to redo the loop once `cto` answers.

`research-decision.md` **E2** and its own `references/research-exit-and-custody.md` now declare this pipeline
as a fourth origin, with the return address back **here** — never straight into `feature-intake.md`, which has
no way to know a severity is still pending on the other half of the same request.

## What each severity's envelope must defer

The Tech Spec envelope's direction-dependent fields (`Module boundaries:`, `Client-server contract:`,
`Architecture diagram:`, `Patterns chosen:`, `Task breakdown:`, `Acceptance criteria:`) describe a *settled*
direction. At Major, the direction is exactly what the reopened CP1 has not yet settled — writing them now
would preempt the loop.

| Severity | Direction-dependent fields |
|---|---|
| **Minor** | Filled — nothing about the direction changed, only the spec's wording |
| **Moderate** | Filled, revised in place — the original direction and its assumptions still hold, so there is nothing left open to defer |
| **Major** | Written as `Pending CP1` — inventing them now silently forecloses the direction question the reopened loop exists to answer, and a redrafted CP1-locked spec supersedes them anyway at `feature-intake.md` step 6 |

`Change severity:` itself, and the code now needing rework, are never deferred at any severity — they are the
one thing this dispatch exists to produce.

## What travels into E4 and E5

| Item | E4 (Moderate) | E5 (Major) |
|---|---|---|
| The revised or in-progress Tech Spec | Whole | Whole, with direction-dependent fields `Pending CP1` |
| What the change is meant to achieve, in the GD's own words | — | Yes — stands in for `Acceptance criteria:` while it reads `Pending CP1`; `critic` returns `Blocked` at the reopened loop without one or the other |
| The rework list | Yes | Yes |
| Options earlier rounds ruled out | — (no loop reopens) | Yes — `advisor` cannot remember them |
| Which risks the GD accepted at CP1 | — | From the ledger's `## Decisions` half, or `none` on a first-time CP1 |
| The reclassified tier and its five axes | Yes — recorded in the ledger before rework dispatches | Same |

Nothing here is optional custody: an item present above and not carried is a thing the receiving checkpoint
reconstructs from scratch, which is exactly what `LEDGER.md`'s `## Decisions` half exists to make unnecessary.
