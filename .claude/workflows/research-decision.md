# Research & Decision

From a technology, package or technique the project does not yet have, to a settled decision. Usually a branch of
`feature-intake.md`; standalone when the GD asks for research or summons a spike with no feature (G30). This
pipeline exists to spend **U** down. You research, you never integrate.

## Entries

| Door | Comes from | Carries |
|---|---|---|
| **E1** | `feature-intake.md` step 5 — a capability the project lacks, direction already settled | The capability as behaviour, the tier, the feature's constraints |
| **E2** | Any `Routed to: cto` — `technical-architect` at its step 2 or step 6, `feature-development.md` (`netcode-engineer`, a tech lead), `change-request.md` classifying a change | The question, **which caller and which step** (it sets the return door), what is already known |
| **E3** | `advisor` → `Needs-decision`, `Routed to: cto` or `rd-engineer` | The option in question, the options ruled out, the round spent |
| **E4** | `feature-intake.md` step 2 returns U2/U3 on a **technology** unknown — before its loop | The architect's `Open design question:` lines tagged `technology`; `design`/`architecture` lines go to `advisor` in `feature-intake.md`, routed per line |
| **E5** | The GD asks for research, no feature (G30) | The capability as behaviour, the paid/closed-source preference (G34) |
| **E6** | The GD summons a spike, no feature (G30) — asking *is* the summon | The question and the decision waiting on it, threshold, hardware, baseline, any build authorisation (G16) |

E1–E5 start at step 1; E6 starts at step 4, after asking only what the request left out (G31). E2 and E3 never jump straight to `cto`. E5 and E6 classify the run
themselves — they inherit no tier. **U2/U3 on a technology question is the E4 trigger at any D**; a D5 system built
from what the project has is U0.

## May dispatch

| Agent | Returns / owns here |
|---|---|
| `researcher` | **Research Report** — what exists today, sourced and dated (`Picture taken:`), `Assessed:` lane; recommends, never decides |
| `rd-engineer` | **Feasibility Report** — a disposable harness and measured numbers; evidence, never a verdict. Holds Editor tools (I3); never builds |
| `build-run-engineer` | The Development Build an on-device spike measures — only on an explicit GD request (G16) |
| `cto` | **Technical Decision** and any `Standard set:`; again with `engineering-standard-adr-authoring` to write the ADR a standard is owed |

`advisor` is not dispatched here: how comparable games solved a **design** problem is `feature-intake.md`'s.

## Hard ordering

1. **`researcher` runs before `cto` on every path but E6**, which reaches `cto` through a Feasibility Report. `cto`
   is never entered without a candidate set — it is barred from returning open options.
2. **The spike gate (G31) precedes every `rd-engineer` dispatch** except E6. No recommendation from `researcher`,
   `advisor` or `cto` is ever converted into a dispatch.
3. **On a device**: the device lock (I7) is claimed before the harness or the build reaches it and released on
   return; `rd-engineer` writes the harness, `build-run-engineer` builds it, and `rd-engineer` installs that build
   on the locked device and measures it.
4. **Records are written at the transition** (I4), never at closure.

## Steps

1. **Depth check** (E1–E5) — pick the lane; it sets the brief, not only the step list. This is the research
   question's classification, independent of the feature's tier: an A5 feature can carry a Direct question.

   | Lane | Observable at entry | Steps | Brief asks `researcher` to |
   |---|---|---|---|
   | **Direct** | One capability, nothing strategic, nothing to measure | 2 → 6 | Confirm the first-party answer — one named solution, version, licence, caveats |
   | **Considered** | Several plausible approaches, or the first-party answer is missing or deprecated; reversible at known cost | 2 → 5 → 6 | Return a ranked shortlist |
   | **Escalate** | Hard to reverse (R2–R3), costly if wrong (C3–C4), a paid commitment, or a number nobody can settle by reading | 2 → 3 → 4 → 5 → 6 | Sweep all three source tiers and name the deciding criterion |

   Ambiguous starts one lane higher. `researcher`'s `Assessed:` raises the lane, never lowers it.
2. **`researcher`** — never skipped. Attach the capability as behaviour ("research physics" is `Blocked`) and the
   paid/closed-source preference (G34).
3. **Spike gate** — only when a number is the blocker: G31, carrying everything step 4 attaches. Declined → step 5,
   `cto` deciding provisionally on the number it names.
4. **Spike** — `rd-engineer`, attaching the question and the decision waiting on it, the pass/fail threshold, the
   target hardware, and today's baseline. Only a spike writes to the project: the harness is R1; a measurement on
   the device is R2/X2 and splits per ordering 3. The harness is disposable: once the Feasibility Report is in,
   you revert every path its `Built:` names — packages and settings included — under the Editor lock before step
   5, and the hand-back says so. The GD may ask to keep it, never as production code.
5. **`cto`** — carrying the candidate set whole, the decision and what depends on it, the cost/timeline/scale
   constraints, and the spike's evidence **or the fact the gate was declined**.
   - It may decide provisionally and name the one measurement that would falsify it: that runs step 3 — unless the
     GD already declined it this run, in which case the decision stays provisional. One cycle (B7); still open
     after it → G32. A product consequence → G32.
   - A provisional decision keeps its re-open threshold, and it travels into the Tech Spec.
   - A non-empty `Standard set:` is owed an ADR — on a standalone run, only once G33 accepts the standard: dispatch
     `cto` with `engineering-standard-adr-authoring` (it names the log location), and
     record the standard and its ADR in the ledger's *GD decisions* — a standard nobody recorded is a dropped
     project rule.
   - `Rejected`, `Routed to: technical-architect` is a correct result — the question was contained.
   - A working dependency `researcher` refused to justify replacing comes here for keep/mitigate/replace.
6. **Exit** — the Research Report and Technical Decision travel whole to the receiving step; `Picture taken:` and
   what makes it stale go into the Tech Spec beside any re-open threshold, and into the ledger's `Research:` row —
   the only home on a path that writes no new spec. Recompute **U**; an unknown still standing is reported as
   **unresolved**, never as settled because the round ended. A result that moves another axis names it and why in
   the hand-back; `technical-architect` re-reads it at the receiving step, updates the ledger's `Tier:` and appends
   to `Tier history:`. Large enough that the approved direction no longer holds → it surfaces at CP2 (G24) and goes
   to `feature-intake.md` **E5**. Never silently carry forward a tier the research invalidated. Standalone (E5/E6)
   → the result to the GD, and G33 only if it set a standard, made a provisional decision, or commits money; a
   Direct lane produces none and is not gated.

**Every return** — beyond `orchestrator.md`'s defaults:

| Return | Do |
|---|---|
| `researcher` → `Done`, nothing strategic open | Step 6 |
| `researcher` or `advisor` → `Routed to: rd-engineer` | Step 3 — never a direct dispatch |
| `researcher` or `advisor` → `Routed to: cto` | Step 5, candidate set attached |
| `rd-engineer` → `Done` | Step 5 if the choice is strategic or hard to reverse; else step 6 |
| `rd-engineer` → `Needs-decision`, `Routed to: cto` or `gd` | Follow it — not answerable at spike scale |
| `cto` → `Needs-decision`, `Routed to: gd` | G32, then step 6 — a deferred call exits as **unresolved** |
| `researcher`/`rd-engineer` → `Rejected`, `Routed to:` an implementer | Production work: `feature-development.md` **E2** with notes; the GD on a standalone run; `change-request.md` on its origin. Never argue it back |
| A Continuation Debt Record | Record it; its known non-solutions travel into whatever runs next — no review loop counts strikes here; never re-dispatch the same brief |

## GD touchpoints

Where each fires; what it carries and what happens on no are `gd-touchpoints.md`'s alone.

**G30** at **E5**/**E6** · **G34** step 2 · **G31** step 3 · **G32** step 5, or after B7 · **G33** step 6 on a
standalone run · anywhere: **G6**, **G7**, **G16**.

## Bounds

B1 (attempt budget per dispatch) · B7 (measure-and-confirm — the ledger's `Measure-and-confirm:`, or the
**Standalone decisions** row on E5/E6) · B8 (standalone re-decide) · B17 (identical `Blocked`).

## Exits

Set by the door entered, never by the tier.

| Left from | Control goes to | Written |
|---|---|---|
| **E3**; **E4** where the loop waits on it (D4–D5 or U3) | `feature-intake.md` **E2** — step 3, the loop, then CP1 | Ledger `Research:`; `Tier:` if moved |
| **E4** where no loop runs (a U2 line at D1–D3) | `feature-intake.md` **E3** — step 6 at D3, the direct-notes hand-off at D1–D2 | Same |
| **E2** from the architect's step 2 | `feature-intake.md` **E2** at D4–D5 or U3; its **E3** where that shape fires no loop | Same |
| **E1**; **E2** from the architect's step 6 | `feature-intake.md` **E3** — step 6 at D3–D5, the direct-notes hand-off at D1–D2 | Same; staleness and any re-open threshold into the Tech Spec |
| **E2** from `feature-development.md` | That pipeline, resuming the step it left | Ledger `Research:`, `Measure-and-confirm:` |
| **E2** from `change-request.md` | `change-request.md` **E3**, to finish classifying | Same |
| **E5**, **E6** | The GD — G33 where it fires | The ADR for an accepted standard; `project-state.md` **Standalone decisions** — the GD's answer, any re-open threshold, B7 |
| **E2** from `feature-development.md`, with a provisional decision | That pipeline | The re-open threshold into the resuming brief and the ledger's `Research:` — the approved spec is not rewritten |
| A bound reached | The GD (G7) | Continuation debt |
