# `qa-pipeline.md` — Review, scored against a real run

> **Historical record — read [`README.md`](README.md) first.** This is the log of one review round, not a
> specification. The layer that runs is `.claude/workflows/`; the current state of it is
> `.claude/workflows/workflow-checklist.md`. **Two things here go stale by design**: every number about the
> layer (verifier claim counts, "still unreviewed" lists, "nothing is committed") is as of this round, and
> **later parts supersede earlier ones** — the last score in the file is the one that stands.

> **Working note.** Fifth in the series, after `feature-intake-update.md`, `research-decision-update.md`,
> `feature-development-update.md` and `review-pipeline-update.md`. Same method as the last three: the
> pipeline was not read into a score, it was **run** — five real dispatches following the files literally,
> recording where they hit a wall.

**Why this one was marked harder than the others.** This is the pipeline that decides whether a feature
passes. A defect in `feature-intake.md` costs a rework round; a defect here lets unverified work close as
verified, which is the one failure `verification-standards.md` calls worse than having no QA at all.

## Part 0 — What was run, and what it buys

**The feature.** *Daily Login Streak* — a `Game.Core.Progression` streak rule plus the client panel that
previews it. Classified **A4 — D3 C3 (progression/economy path) U1 R1 X1**, verification floor **V3**,
attempt budget 3, client track, Android + PC targets, 33.3 ms budget, **no baseline recorded**.

The submission was shaped to load this pipeline's riskiest untested claims rather than to be hard:

- **The review gate was declined by the GD**, because *"it does not require review to have run"* is this
  pipeline's boldest claim and nothing had ever tested it.
- Three planted defects, each against a different acceptance clause and a different lens: a 1-based index
  into a 0-based reward table (crashes at the streak cap), `DateTime.Now` where the spec says UTC, and a
  client deriving a reward the spec says it must read from the Core.
- An Implementation Note claiming *"Edit Mode tests over the streak boundaries — all green"* and
  *"Allocation checked on device"* against an environment with **no toolchain, no build and no device** —
  the exact thing `assurance-evaluator` exists to catch, placed four steps upstream of it.

| # | Step | Agent | Returned |
|---|---|---|---|
| 1 | step 1 — plan mode | `qa-lead` | `Done`, `Verdict: Planned`, **`Routed to: gd`**, 9 exit criteria, 7 gaps |
| 2 | step 2 — the Core suite | `qa-automation-engineer` | `Done`, **`Results: 0 / 0`**, 5 defects at E1, **three** routing destinations |
| 3 | step 4 — sign-off | `qa-lead` | `Done`, `Verdict: Not signed off`, `Routed to: gd`, **8 exit criteria — a different 8** |
| 4 | step 4b — the assurance gate | `assurance-evaluator` | `Done`, **`Acceptance: FAIL`**, three integrity gates failed, `Routed to: gd` |
| 5 | CP4 | `producer` | `Needs-decision`, a complete-looking report **with no Assurance Verdict and no mention that one was owed** |

**What this evidence is.** Findings marked **live** were produced by following the files as written and
hitting a wall — **E2** for claims about the *specification*. It is not evidence the layer works in
production: `playtest-tester`, `performance-qa-engineer` and `build-verification-tester` were never
dispatched, because this repository has no Unity project, no build and no device, so the device lane and the
two Editor-bound executors remain **E1 — inspection**. Stated rather than rounded up. The scratch tree was
deliberately outside the repository and no `.workflow/` was created, per `research-decision-update.md` Part 5.

---

## Part 1 — What the run proved works

**The assurance gate is the best thing in this pipeline, and it earned its cost on first contact.** Handed
the planted note, it failed three non-compensatory gates, refused to compute a weighted score at all
(*"a failed integrity gate is an acceptance state, not a number to average away"*), and found a corroboration
nobody asked it for: a boundary test that had actually run would have hit the streak-7 crash, so the claim
was *"not merely unevidenced — it is inconsistent with the code it describes."* That is E3-grade reasoning
from a gate consuming other gates' verdicts, which is exactly its design.

**The independence of the roles held under pressure.** `qa-automation-engineer` labelled every finding
**E1 hand-trace, explicitly not a run result**, and reported the environment check it actually performed
rather than quietly writing tests and claiming them. `qa-lead` refused to sign off, refused to invent a
criterion for an undefined case (a negative day delta), and routed the UTC question to `technical-architect`
rather than choosing. `producer` presented the verification contradiction as a contradiction and did not
adjudicate it. Every one of those is a guardrail doing its job.

**`Not covered` being mandatory is worth what it costs.** Every report populated it, and the gap list at
step 4 is assembled almost entirely out of that one field.

---

## Part 2 — Findings

Nineteen. **QA1–QA19** — nine High, ten Medium. **live** means a dispatch produced it.

### QA1 — The sign-off routing row skips the gate that checks verification claims · High

The routing table read:

> `qa-lead` `Not signed off`, the gap cannot be closed | To `producer` and CP4 — accepting an unmet criterion
> is the GD's call alone

At **A3 and above, step 4b sits between those two.** The prose in step 4 said so, the mermaid drew it, and
`qa-assurance-gate.md` says the gate *"runs last, after every other verdict is in"* — but a caller reads the
routing table, and the routing table sent the feature straight to `producer` on **exactly the path where an
unmet criterion is being carried to the GD for acceptance**.

**Demonstrated end to end.** Following that row as written produced dispatch 5: a CP4 report with no
Assurance Verdict, which never mentions one was owed, and which offers the GD *"explicitly accept the gap"*
as an option over a finding `effort-allocation.md` puts beyond any waiver. The gate that would have said so
had been routed around by the table that is supposed to route to it.

### QA2 — The exit criteria have no carrier, and sign-off silently re-derived them · High · **live**

Step 4 said `qa-lead` judges the reports against the exit criteria **it wrote itself** at step 1. It cannot:
it is stateless, `qa-entry-inputs.md` had no row for them, the ledger had no row for them, **E2**'s carry
named only the coverage assignment, and its contract has **no `If absent` row** for them — so it does not
block and does not state the substitution.

Run live on one feature, plan mode returned **nine** exit criteria and sign-off returned a different
**eight**:

| Dropped between plan and sign-off | Appeared at sign-off, never planned |
|---|---|
| "The declined review gate is recorded as review debt at closure, per I6" | "V3 regression pass — absent for the whole feature" |
| "Every returning report populates its `Not covered` / `Not measured` field" | "A reward-value assertion per table row" |
| "`DEBT.md` is owed at A4 if any limitation is carried past this cycle" | |

The verdict did not change, because the evidence was zero either way. **On a feature with real evidence, that
difference is the verdict** — and nothing in the layer would have shown it happened.

### QA3 — The agents table had no `Produces` column, so the layer's own custody check was blind and passed · High · **E2**

Every other pipeline declares `| Agent | Tier | Produces | Owns |`. This one declared
`| Agent | Tier | Runs in | Owns |` — and `assurance-evaluator`'s row had an artifact, **Assurance Verdict**,
sitting in the *Runs in* cell.

`verify-workflow-layer.ps1`'s custody check extracts column 3. Extending its scope to this pipeline therefore
produced **PASS** — from one incidental bolded phrase that happened to be named elsewhere. Probed directly,
the check was extracting exactly one artifact out of eight.

Restoring the column made it fail immediately, naming **six** deliverables *"declared and never received"*:
QA Plan, QA Verdict, Test Report, Playtest Report, Performance Verification, Build Verification. The check
had not been wrong — it had been looking at the wrong cell, and reporting success for it. This is the exact
failure mode the standing rule names: *a check that passes for the wrong reason turns an open defect into a
green claim.*

### QA4 — "The orchestrator asks the GD" survived here — fifth recurrence · High

Line 7 read *"the orchestrator asks the GD whether to run it"*. `optional-gates.md` line 25 reads:

> **A pipeline that consumes this rule never restates it as "the orchestrator asks"** — that wording was
> corrected here and then survived in two files that quote it.

Logged as **F6** in the layer assessment, corrected in the owning file, then found again in
`review-pipeline.md` (**RP11**) and fixed there, and still live here. Fixing an instance has never closed
this class; a grep across the layer shows this was the last pipeline carrying it.

### QA5 — Coverage that could not run returns `Status: Done`, and nothing told it from coverage that ran · High · **live**

`qa-automation-engineer` returned `Results: 0 / 0` with five defects, every one labelled E1 inspection. The
routing table's only matching row was *"any executor `Done` with `Defects:` → route each defect to its named
owner at E3"* — which would have fed **inspection findings into the rework loop as QA findings**, in a layer
whose own standard is that reading is review and running is verification.

The Continuation-Debt row does not cover it either: that is an exhausted **attempt budget**, and this is an
environment no further attempt reaches.

### QA6 — `Acceptance: FAIL` presumed a named owner; live it had none · High · **live**

The row said *"To the named owner at **E3**."* The gate returned `Routed to: gd` and stated why: the claims
it failed are in the **Implementation Note**, which `rules/implementation-note.md` says is *pipeline-assembled*
— so the inputs did not identify which implementing agent originated either claim. An integrity finding whose
owner is the assembly had no door, on the one finding type no waiver reaches.

### QA7 — The pipeline declared no exits · High

`feature-development.md` **E3**, `review-pipeline.md` **E3**, **`change-request.md` E2**,
`technical-architect`, `tech-lead-performance`, `/investigate-device-crash`, the GD — and not one declared.
`change-request.md` **E2** names *"`qa-pipeline.md` CP4"* as its origin; this file named neither the door nor
the file. **D1** and **RP5**'s class, fourth recurrence, exactly where the debt register predicted it.

### QA8 — `qa-lead` → `Routed to: gd` has no row, in either mode · High · **live**

Four `qa-lead` rows existed, keyed to `Verdict:`. **Plan mode** returned `Verdict: Planned` *and*
`Routed to: gd` — and the `Routed to:` carried the single most consequential thing in the whole run: the
contradicted verification claim, surfaced **four steps before** the gate that owns it. A caller matching the
`Verdict: Planned` row holds the coverage assignment and drops it.

### QA9 — The one agent for which review is a precondition, in the pipeline that declares itself independent of review · High · **live**

`qa-automation-engineer`'s required-input table: *"The code under test, **and confirmation it passed code
review** → `Status: Blocked` — never test code that has not cleared the review gate"*, with a worked example
returning `Rejected`, `Routed to: code-reviewer`. `qa-pipeline.md` says *"It does not require review to have
run"*, and `qa-entry-inputs.md`'s "When review did not run" section named only `qa-lead` and
`assurance-evaluator` — **not** the one agent whose contract actually blocks.

Live, told plainly that the GD had declined the gate, it proceeded and named the consequence in its report.
**Right behaviour, resting on judgment rather than on the specification** — the D20 family.

### QA10 — A return naming several destinations had no row · Med · **live**

`Routed to: csharp-engineer (Core), unity-engineer (client), technical-architect (the UTC ruling)`. Three
other pipelines carry this rule; this one did not. Fourth pipeline in a row.

### QA11 — E1 and E4 were two doors for one entry · Med

`optional-gates.md`: *"QA, on a feature already closed → `qa-pipeline.md` **E1**, with the spec and tier from
the ledger."* `qa-pipeline.md` **E4**: *"...or after declining the gate earlier."* They differ materially —
E1 reads the tier, floor and counters from the ledger; E4 says *"No ledger is assumed: classify the run
itself."* **R7**'s class.

### QA12 — The sign-off re-dispatch bound counts rounds, not causes · Med · **live**

*"gaps name coverage never run → re-dispatch exactly those agent-ids, bounded at 2."* Live, three of four
assignments were **unrunnable** — no Editor, no build, no device. Re-dispatching spends both rounds proving
the first return was true.

### QA13 — `performance-qa-engineer` has no `Defects:` field · Med · **E2**

Found by the extended custody check, not by reading: it flagged `performance-qa-engineer → unity-engineer` as
a destination with no routing row. The cause is an envelope mismatch — that agent reports
`Regressions: <metric, delta, the evidenced cause, and the owning agent-id>` and **no `Defects:` field at
all**, so the row that routes defects to their owners never matched its returns.

### QA14 — `build-verification-tester`'s escalation names three owners; one had a route · Med

Its Escalate criterion returns `Routed to: build-run-engineer`, `unity-engineer`, **or**
`tech-lead-sdk-platform` by the evidenced cause. The device lane carried only the first — dropping the two
that are usually the actual cause of a build-only fault (client code after IL2CPP or stripping; an SDK or
store integration).

### QA15 — The test-code gate's offer was conditioned on "written and green" · Med · **live**

`qa-test-code-gate.md` offered the review gate *"once the suite is written and green."* Live, the suite was
written and **never executed**. A suite nobody has run is the one most worth reading — so the wording
reopened invariant **I10**'s hole for precisely the submission that needs the gate most.

### QA16 — The gate is told to score iteration, and nothing can carry what a retry improved · Med · **live**

`assurance-evaluator` scores an `Iteration:` dimension. `execution-loop.md` requires a retry to state what
materially improved. `rules/implementation-note.md`'s `Attempts:` field carries **used / budget and nothing
else**. Handed `2 / 3`, the gate reported the iteration *unevidenced* and declined to assume improvement —
correct behaviour, and a gap in the dispatch rather than in the work.

### QA17 — `producer` did not notice the Assurance Verdict was missing, and its input contract permitted it · Med · **live**

`qa-checkpoint-4.md` said producer's input is *"the Assurance Verdict **where A3 or above produced one**"* —
wording that lets the caller omit it silently. Live at A4, with QA1's row having skipped the gate, `producer`
compiled a complete-looking CP4 report that never mentions one was due. Its guardrail *"an unreported item is
reported as unknown"* cannot fire for an input nobody told it to expect.

### QA18 — The plan can assign coverage the pipeline cannot dispatch · Med · **live**

`qa-lead` correctly assigned `build-verification-tester` (B1–B3) and a device build to
`performance-qa-engineer` from the stated Android target. No build exists, and `build-run-engineer` acts only
on an explicit GD request. Nothing in step 2 converted *"the assignment needs a build"* into the GD ask
**before** dispatching — the device lane's rows are reactive, so the pipeline learns it by burning a
`Blocked`.

### QA19 — Three things this pipeline produces had no ledger home · Med

The **coverage assignment and exit criteria** (QA2's durable half); the **baseline**, where the ledger's
`Baseline:` row exists *"to stop a run silently becoming the baseline"* but nothing said who writes it after a
first measurement; and the **test-code strike cap of 2**, registered in `loop-termination.md` while the
ledger's submission table is headed `Strikes /3`.

### Recorded, not counted as a finding

**`risk-based-test-planning` did not resolve, and `qa-lead` substituted a different skill.** It said so
plainly and planned through `plan-test-coverage` instead. This is **RP15**, the GD-deferred skill relocation,
but the evidence has moved: the previous round showed gates *reading a skill by hand*; this one shows an
outage **changing which technique an agent applies** — and the substitute is a skill from outside this
repository, which the project neither owns nor versions. Recorded in the verifier's accepted-gap note. The
relocation is still the GD's call.

---

## Part 3 — What changed

One new reference, eight files amended, three verifier changes. `qa-pipeline.md` is **200** lines against the
200 cap — every addition paid for by promotion or compression, none by deleting reasoning.

| Closes | Change | Where |
|---|---|---|
| QA7, QA2, QA5, QA6, QA3 | **`references/qa-exit-and-custody.md`** — new. The eight deliverables and what each becomes; twelve exit doors; the exit-criteria carrier; the unrunnable-coverage rule; the `FAIL` with no owner; an eleven-row custody table | new reference |
| QA3 | The agents table gains its **`Produces`** column, the misplaced artifact moves out of the `Runs in` cell, and the venue/lock information folds into `qa-execution-order.md`, which already owned it | `qa-pipeline.md` |
| QA4 | The ask's owner restated as **whichever party reached the boundary**, naming both locations | `qa-pipeline.md` |
| QA1, QA8, QA5, QA6, QA10, QA13 | Six routing rows added or rewritten, including `Routed to: gd` in either mode, `Results: 0 / 0`, `Defects:` **or `Regressions:`**, and the unclosable-gap row routed **through 4b** | `qa-pipeline.md` |
| QA2 | The criteria travel back with the sign-off dispatch, are written to the ledger at step 1, and the row is keyed to the live divergence | `qa-pipeline.md`, `qa-entry-inputs.md`, `feature-ledger.md` |
| QA9 | The review-precondition seam stated, with the contract quoted and the dispatch given the resolution | `qa-entry-inputs.md` |
| QA11 | **Told apart by the ledger, not by who asked** — stated on all three sides | `qa-pipeline.md`, `optional-gates.md`, `entry-index.md` |
| QA12 | The bound counts rounds, and only runnable coverage spends one — **read off the report, never judged** | `loop-termination.md`, `qa-pipeline.md` |
| QA14 | The build-only fault's three owners | `qa-device-lane.md` |
| QA15 | "Written" is the trigger, not "written and green" | `qa-test-code-gate.md` |
| QA16 | `Attempts:` now carries **what the last attempt improved**, in the rule, the note's source table and the brief's ask-back | `rules/implementation-note.md`, `development-brief.md`, `qa-assurance-gate.md` |
| QA17 | The Assurance Verdict is **owed** at A3+, and its absence is stated rather than omitted | `qa-checkpoint-4.md` |
| QA18 | Device coverage the plan assigned is asked for **before** it is dispatched | `qa-execution-order.md` |
| QA19 | A `QA plan:` row, a `Baseline:` writer, and the test-code strike bound | `feature-ledger.md` |

### Three verifier changes, all negative-tested

| Change | Negative test | Result |
|---|---|---|
| **Custody extended to `qa-pipeline.md`** — 4 of 6 → **5 of 6** | Rename one deliverable's receiver | **FAIL**, naming `"Playtest Report"` · restore → **PASS** |
| **New: every agents table declares a `Produces` column** | Revert the header to `Runs in` | **FAIL** — *and the old custody check PASSes in the same run*, which is the defect it exists to catch · restore → **PASS** |
| **New: no pipeline restates the gate ask as the orchestrator's** | Plant the forbidden sentence | **FAIL**, quoting the line · restore → **PASS** |

The second is the one worth keeping. It does not check content — it checks that the *other* check can see.
The custody class has now been closed instance by instance four times and by a check once; this is the first
check in the series that guards a check.

### Verification

| Check | Result |
|---|---|
| `verify-workflow-layer.ps1` before | **91 claims; 90 hold, 1 accepted gap** (E2, baseline) |
| after | **95 claims; 94 hold, 1 accepted gap, no new drift** (E2) |
| The three negative tests | **FAIL on the defect, PASS on restore** — E2, not asserted |
| 200-line cap | `qa-pipeline.md` **200**; `loop-termination.md` 176; every reference well under |
| The seam, both directions | Grepped for the stale "criteria it wrote itself", "written and green", any surviving declined-gate→E4 route, and the forbidden ask wording. The only hits are this round's own deliberate quotations of the old text, now marked as past tense |
| Working tree | Every negative test reverted; `.claude/agents` and `.claude/skills` untouched; the scratch tree is outside the repository |

---

## Part 4 — Score, marked strictly

Marked against the ruler `feature-development-update.md` Part 4 established, under which self-marking in this
series runs about **0.8 high**. The numbers are after that discount.

| Axis | Before | After | What moved it, and what holds it down |
|---|---:|---:|---|
| Entry points and addressing | **5.0** | **9.0** | E1/E4 told apart by the ledger on all three sides; E1's real origins declared; every exit door named, including the `change-request.md` **E2** that had an origin never naming it. Held from higher: **no re-entry has ever been taken through any door here**, and E3's rebuilt-artifact rule is unrun |
| Agent-brief contract | **5.5** | **9.0** | The entry table was already strong — ten rows, each keyed to a real `If absent` — and was missing the one row that decides the verdict. That row is in, keyed to a live divergence; the review-precondition seam is stated; and QA16's carrier is closed in the rule rather than deferred again. Held: the criteria carrier is a ledger row that **has never received anything** |
| Gate and exit logic | **4.0** | **9.0** | The worst axis by far, and the one that mattered most: a routing row routed *around* the gate that checks verification claims, on the path that carries an unmet criterion to the GD. Closed, along with the exits, the ownerless `FAIL`, the multi-destination rule and unrunnable coverage. Held: the device lane and the CP4 **approve** path have still never run |
| Counters and caps | **6.5** | **8.5** | The rounds-vs-causes defect is closed in the owning file and made **observable from the report** rather than left to judgment, and the plan and test-code bound gained ledger homes. **Not 9**: no cap in this pipeline has ever been driven to its bound, so "nothing else found" is absence of evidence at E1 — and unlike the other axes, nothing here became machine-checked this round |
| Honesty about its own gaps | **6.5** | **9.0** | The file carried a factually impossible premise (criteria it *wrote itself*) and the one sentence its own authority forbids. Both corrected, the second closed as a class. The round found the defect in **its own extended check** by probing rather than by reading, and says so. Held: the largest standing defect is still deferred, and this round's new evidence for it is recorded rather than acted on |
| Result custody | **3.0** | **9.0** | Worst starting axis: no `Produces` column at all, six of eight deliverables named nowhere in the pipeline or its own references, and the layer's check blind to all of it. Column restored, deliverables named, the check now bites, and a second check guards the first. Held: three destinations are ledger rows nothing has ever written to, and custody is asserted for **5 of 6** pipelines |

### **5.1 → 8.9**

**Two axes moved after the first marking, and it is called out rather than folded in.** The first pass had
*agent-brief contract* at **8.5** (QA16's carrier deferred as "a field on seven envelopes", which the series
has declined twice) and *counters and caps* at **8.5**. Re-examining QA16 showed it is **not** a seven-envelope
change: the Implementation Note is pipeline-assembled and its `Attempts:` row already sources from "what the
agent stated back", so closing it cost one line in the rule and one in the brief. That is a fix, so the axis
moved. *Counters and caps* was re-examined the same way and **stayed at 8.5** — its deduction is specific and
survives.

**8.9, not 9.0**, and the gap is one axis with a stated reason rather than a rounding decision.

**Why not higher.** `effort-allocation.md` requires **E3 or better above 9.5**, and the binding limit is
unchanged and not reachable by writing: three of this pipeline's seven agents were never dispatched, the
device lane has never opened, no cap has ever fired, `.workflow/` does not exist, and every ledger row this
round writes into has received nothing.

**Why not lower.** Nineteen findings, nine of them High and six produced live; the pipeline's most dangerous
defect — a routing row that bypasses the verification-claim gate on the acceptance path — found, demonstrated
end to end through a real `producer` dispatch, and closed; and the custody class advanced from *checked* to
*checked, with the check itself checked*.

**Still scored by the author of the fixes — E0** on this project's own scale, awaiting an independent pass.
`effort-allocation.md` is explicit that a second look by the same reviewer is not independent verification.

---

## Part 4b — The independent review round, and what it cost the score

Parts 0–4 were **self-marked**, which `effort-allocation.md` calls **E0**. The GD then asked for an objective
pass, so the round was put through the layer's own gates in the order the layer prescribes:
`code-reviewer` first, `assurance-evaluator` after it.

**`code-reviewer` returned `Request changes` — ten findings, three High.** It is the first materially
independent verdict in this series. What it found:

| # | Finding | Sev |
|---|---|---|
| **F1** | `qa-assurance-gate.md` still said the `Attempts:` field *"carries used / budget and nothing else"* — which **attempt 2 of this same round made false**. The QA16 fix and the paragraph describing QA16 pointed in opposite directions inside one submission | High |
| **F2** | The new `Produces` check tested the token's **presence**, not its **position**, so `\| Agent \| Tier \| Owns \| Produces \|` would pass while the custody check still read `Owns`. And an unmatched header was skipped by a silent `continue` | High |
| **F3** | It asserted the column, never the **cells** — a row reverted to `—` passed both checks and that deliverable left custody in silence | High |
| **F4** | An inserted paragraph split an existing sentence in `qa-checkpoint-4.md`, leaving a dangling "and" | Med |
| **F5** | QA13 was closed for one agent, not the class: `playtest-tester` has **neither** `Defects:` nor `Regressions:` — its finding is `Classification:`. And the new custody table claimed `Not covered:` is *"mandatory on every report"*, which that contract does not support | Med |
| **F6** | The gate-ask check matched one phrasing, while the record called it a closed class | Med |
| **F7–F9** | "eight of them High" is nine; "seven deliverables" is eight; "received nowhere at all" is stronger than the tool output supports | Low |
| **F10** | A pointer lost its `references/` prefix, and no check can see it | Low |

**It also confirmed the round's load-bearing claim in code rather than accepting the narrative** — tracing
the positional extraction at `:379` and grepping the `qa-*` references to check "six received nowhere" was
true as a naming claim. That is the corroboration a self-score cannot buy.

### What negative-testing the fixes then found, which nobody had predicted

Fixing **F2** and **F3** and re-running the bypass tests exposed two defects that neither the review nor the
original round had seen:

1. **My own `Produces` check was vacuous on two of the six pipelines.** The header regex ended `[^\r\n]*$`,
   and in .NET `$` wants the position before `\n` while the class stops before `\r` — so **every CRLF file
   failed to match**, and the silent `continue` swallowed it. `feature-development.md` and `review-pipeline.md` were
   observed being skipped. An independent run afterwards reported **all six** pipeline files as CRLF, so the
   real blast radius was at least those two and plausibly all six — recorded as observed, not rounded. The review predicted the bypass by inspection; running it
   proved it was already live. The check is now anchored and CRLF-safe, and a column swap on a CRLF file
   **FAILs**, which is what proves it is being read.
2. **A renamed agents heading crashed the verifier outright** — `$text.Replace($agentsSec, '')` throws on an
   empty string, aborting the run at that line and skipping every claim after it, including the skill and
   runtime-state checks. A pre-existing bug from the previous round's fix J, reachable by one heading edit.
   Now a reported finding instead of an exception.

Five bypass paths are now negative-tested: column swap (LF), column swap (CRLF), a blanked cell, a renamed
heading, and the forbidden sentence. All five FAIL loudly and PASS on restore.

**And one of the fixes was wrong on first attempt.** Widening the gate-ask regex as F6 suggested immediately
produced a **false positive** on `review-pipeline.md`, which names the orchestrator as the asker for *"an ask
belonging to no pipeline"* — the legitimate third row of `optional-gates.md`'s own ownership table. A check
that flags correct text is how a check stops being read. The regex now targets the forbidden shape (the
orchestrator asking **the GD**) and excludes any line that qualifies itself with "no pipeline".

**All ten findings are closed**, and the score in Part 4 is unchanged by them — because every one was a
defect *in the fixes*, not a reason the findings behind them were wrong. What changed is the evidence grade.

### The independent score — `assurance-evaluator`, run last

**`Acceptance: CONDITIONAL PASS`.** Weighted **8.8** against the A4 floor of 9.0, and **8.75** on the six
axes this note self-scored at **8.9**.

| Axis | Self | Independent | Why it differed |
|---|---:|---:|---|
| Entry points and addressing | 9.0 | **9.0** | Confirmed — it read the E1/E4 discriminator on all three sides |
| Agent-brief contract | 9.0 | **8.5** | A deduction the self-score did not take: QA16's fix lands in `rules/implementation-note.md`, which is **auto-loaded into every dispatch**, and the `Attempts` cell grew from one line to five sentences. The layer's own open debt row says that directory already costs ~24k words a session |
| Gate and exit logic | 9.0 | **9.0** | Confirmed row by row; *"the strongest evidence in the round"* |
| Counters and caps | 8.5 | **8.5** | Same number, one new reason: the ledger header read `Strikes /3` while the note beside it said to write `1 /2` — *"a header that lies on every other row."* Now fixed |
| Honesty about its own gaps | 9.0 | **8.5** | The sharpest finding against me: the honesty *did not reach the file that survives*. `workflow-checklist.md` §15 carried neither the review round nor the two defects negative-testing exposed. Now §15.13–15.16 |
| Result custody | 9.0 | **9.0** | Verified independently — all six pipelines declare `Produces` third with every row filled, so the new check's precondition holds layer-wide |

Its four residuals — the record gap, two stale self-counts, and *"no independent party has executed the
verifier"* — **are all now closed**. A third dispatch with a shell executed the script, re-ran two negative
tests itself, and reported byte-identical output to the author's run: `OK 95 claims checked; 94 hold`, exit
`0`, working tree matching the expected file list exactly.

That run also corrected a claim of mine: **all six pipeline files are CRLF**, not two, so the `$`-anchor bug
was at least as wide as observed and plausibly total. The text now says observed rather than rounded.

**Self-score 8.9 · independent 8.75 — a gap of 0.15**, against the series' own stated self-marking bias of
~0.8. The gate's reading of that: *"a self-score that survives an independent pass within 0.15 was written to
be true rather than to be accepted."* The 0.2 shortfall against the A4 floor is not mine to waive, and it
goes to the GD as exactly that.

## Part 5 — Deliberately not done

- **RP15, the skill relocation.** Still GD-deferred, still the one failing claim, now with stronger evidence
  behind it (see *Recorded, not counted as a finding*). 90 directories, mechanical, reversible, the GD's call.
- **Custody checks cover 5 of 6.** `change-request.md` is the last, and extending the scope to it belongs
  with its review rather than asserted ahead of one.
- **Nothing was committed.** Every change sits in the working tree.
- **The three undispatched agents.** `playtest-tester`, `performance-qa-engineer` and
  `build-verification-tester` need a Unity project, a build and a device. Their halves of this pipeline are
  fixed by inspection and unrun — stated, not smuggled.

## Part 6 — Resume point

| | State |
|---|---|
| **Pipelines reviewed** | `feature-intake.md` (read, then run), `research-decision.md` (run), `feature-development.md` (run), `review-pipeline.md` (run), **`qa-pipeline.md` (run)** |
| **Still unreviewed** | `change-request.md`, `orchestrator.md` |
| **Findings** | I1–I10, R1–R17, D1–D27, RP1–RP16, **QA1–QA19** — all closed except RP15 (GD-deferred) and Part 5's stated gaps |
| **Verifier** | **95 claims; 94 hold, 1 accepted gap.** Eight checks negative-tested across the series, three of them this round |
| **`.workflow/`** | Still does not exist, deliberately |
| **Next** | `change-request.md`, run the same way — it is the shortest pipeline, the last custody scope to extend, and the only remaining consumer of `qa-pipeline.md` CP4. Then `orchestrator.md`, which is the ignition everything else rests on and has never been reviewed at all |
