# QA Pipeline

One feature from the QA plan through Checkpoint 4 — or, at **E4**, one standalone run on work no ledger holds.
Optional and independent of review: it runs only on what the GD authorised at an ask shaped by G50
(`references/optional-gates.md`), whether or not review ran. CP4 is not optional — it fires for every feature.
Inputs for every door are in `references/dispatch-brief.md` → *QA*; caps are cited from `references/bounds.md`.

## Entries

| Door | Comes from | Carries |
|---|---|---|
| **E1** | QA authorised at `review-pipeline.md` step 6 (G52); at `feature-development.md`'s end-of-work ask where review was declined (G42); or opted into later on a feature with a ledger, even a closed one (reopened). **Plan only — execution locked** | The QA list in `dispatch-brief.md`, with both review verdicts — or that **the GD declined review**, in those words |
| **E2** | CP3 approved (D3–D5); the gates cleared (D1–D2); or review declined, so only the plan gates execution | The ledger's `QA plan` |
| **E3** | A fix came back — through review where it ran, from the author where it did not | The original report and the plan. Only the coverage the fix touched re-runs; device coverage needs a **rebuilt** artifact (G61) |
| **E4** | The GD asks for QA on work **no ledger holds** — shipped code, work no pipeline built, a direct-lane measurement (G15); `orchestrator.md` row 7 | The behaviour and its source, the platform, the budget if performance is judged; review verdicts marked absent. The run is classified on its own |

E1 against E4 is decided by whether a ledger holds the work, never by who asked: E4 on a feature with a ledger
discards its tier, floor and counters.

## May dispatch

| Agent | Produces | Runs |
|---|---|---|
| `qa-lead` | QA Plan (coverage assignment, exit criteria); QA Verdict (sign-off) | Steps 1 and 4; judges, never executes |
| `qa-automation-engineer` | Test Report — Edit/Play Mode suite, network-condition cases | Editor lock |
| `playtest-tester` | Playtest Report — GDD scenarios by hand | Editor lock |
| `performance-qa-engineer` | Performance Verification against a stated budget | Editor lock, or device lock over adb |
| `build-verification-tester` | Build Verification — startup, critical paths, the suite on the Player, the case list on a device | No Editor tooling; device lock |
| `build-run-engineer` | An artifact | Only on an explicit GD request (G16) |
| `assurance-evaluator` | Assurance Verdict | Step 4b |
| `producer` | Status Report | CP4 |

Review verdicts are consumed as given, never re-decided. `crash-anr-investigator` is never dispatched here — it
takes released-production telemetry only.

## Hard ordering

1. The plan before any execution; execution only from **E2**.
2. Locks claimed before dispatch, released on return: the three Editor holders run **serially** under the
   Editor lock (I3); `build-verification-tester` may run alongside them, never beside `performance-qa-engineer`
   on the same device (I7).
3. Device coverage: the build asked for (G61) before any device agent is dispatched; the device confirmed
   before the artifact is touched; a crash stops that case's path.
4. The test-code offer (G62) before a suite's results are used as sign-off evidence.
5. Sign-off, then the assurance gate — after every other verdict — then `producer`. At A3+ a gap that cannot be
   closed passes step 4b before CP4.
6. Accepted gaps written before closure is reported (I6).

## Steps

1. **Plan.** `qa-lead` in plan mode needs only the spec, the tier and the V-number, so it runs while CP3 is
   with the GD. It returns a **coverage assignment** (which `agent-id` covers what) and **exit criteria stated
   at the floor's evidence level** — V2 a targeted direct test; V3 adding edge cases, a dependency pass and a
   regression check; V4 adding the acceptance criteria and a separate final pass. Both go **verbatim** into
   the ledger's `QA plan` now, and travel back verbatim at step 4; where they cannot be recovered, the
   sign-off dispatch says so.
2. **Execute.** Dispatch exactly the `agent-id`s the assignment names. First check it against what exists:
   device coverage with no artifact → G61 now, carrying what that coverage is to prove; declined → unrun from
   the outset, onto the gap list. Default Editor order: `qa-automation-engineer` first (its domain reload lands
   before Play Mode), `performance-qa-engineer` last (a quiet Editor) — a choice, not a contract. Where review
   was declined, tell `qa-automation-engineer` the GD was offered it, declined, and authorised QA anyway.
   **2b — the device lane**, only with a produced build: `build-verification-tester` gets the build's
   `Result:` (path, platform, configuration) and the cases `/plan-test-coverage` derived, filtered to those
   marked `Observe via: build/device` that `qa-lead` assigned — the command never decides what is owed. No
   device → that coverage is unrun; the artifact-only checks still run; the Editor is never a substitute. A
   crash or ANR: logs pulled, no silent relaunch, `/investigate-device-crash`. A fix to a device-found defect
   is never re-verified on the stale build — ask for a rebuild (G61), else that coverage stays unrun.
3. **Read every return's body, not its `Status:`** — `Done` carrying defects is a completed job.

   | Return | Action |
   |---|---|
   | `Defects:`, `Regressions:`, or `Classification: Technical defect` — the envelopes share no field | Each to its owner at `feature-development.md` **E3**; ledger `QA fails` +1 on that submission (B6). A defect on a fix returning at E3: same door, same count |
   | A design flaw, from any agent or the device lane | The GD now (G4) — it never re-enters the engineering loop |
   | A contradicted verification claim | The GD now (G63), and to step 4b if it has not run — never the accepted-gap lane |
   | `Results: 0 / 0`, or findings labelled inspection | Unrunnable: its findings routed as inspection-grade defects, never as coverage that ran; every case to the gap list. Not a Continuation Debt Record; spends no B14 |
   | A Continuation Debt Record | Coverage unrun, not failed: ledger *Continuation debt*, and the gap list |
   | `Not covered:` / `Not measured:` | The gap list. `playtest-tester` has no such field — note what its scenario missed against the plan |
   | `Metrics:` | The ledger's `Baseline:` where none existed, written at the return. `Measured on:` travels with every quotation; an Editor figure is indicative and never satisfies a device claim |
   | `qa-lead` → `Routed to: gd`, either mode | Act on it at the step it arrived (G65) |
   | `qa-lead` → `Needs-decision` — no testable behaviour, or reports contradict | `technical-architect` |
   | `performance-qa-engineer` → `Needs-decision` | Native, GPU or leak → `tech-lead-performance`; budget unachievable for the design → `technical-architect` |
   | `build-verification-tester` → `Blocked`, `Routed to: build-run-engineer` | No artifact: G61, never a build off pipeline state |
   | A build-only fault | By evidenced cause: `build-run-engineer` (the artifact), `unity-engineer` (client code after IL2CPP or stripping), `tech-lead-sdk-platform` (an SDK or store integration) |
   | `build-run-engineer` → `Rejected`, `Routed to: gd` | A correct refusal — get the GD's request or drop the branch |
   | A finding outside the assignment | To its owner, and named to `qa-lead` so the criterion it touches is re-planned |
   | More than one destination named | Record every one; act in the stated order |
   | `Blocked` | Supply exactly the input named (G6, B17); resume at that step |

   **3b — test code.** As soon as `qa-automation-engineer` has written a suite (`Tests added:`), put G62 per
   G50 — saying whether it has run, and that a test asserting the wrong behaviour reports green and advertises
   coverage that does not exist. Yes → `review-pipeline.md` **E3**, test-code origin, paths onto the ledger's
   submission table at `/2`; its results serve as sign-off evidence only once both gates clear it, and at B5
   it returns to `qa-lead` as unrun coverage. No → a review debt row in `project-state.md`; the results are
   still reported, marked as **unreviewed test code** wherever they are quoted.
4. **Sign-off.** `qa-lead` judges against the plan carried back verbatim and the review verdicts as given or
   stated absent, and never signs off while a gap remains. Act on the gap by kind: **not yet run** →
   re-dispatch exactly those `agent-id`s (B14 counts only runnable coverage); **unrunnable**, as the return
   *states* it (an environment check, `0 / 0`, a `Not covered:` naming the missing toolchain, build, device or
   seam) → straight to the gap list; **cannot be closed** → step 4b at A3+, then CP4 (G64). A second QA fail
   on one submission → root cause (B6, B10).
   **4b — the assurance gate**, A3+ or when the GD asks (G80); runs last. Dispatch every verdict as given — or
   that the GD declined review, in those words — the Implementation Notes, the H/M/Q list, the tier, and
   attempts used with, past the first, what improved (unknown is said, and stays unevidenced).

   | Acceptance | Action |
   |---|---|
   | `FAIL` on a submission's claim | Its owner at `feature-development.md` **E3**, as an integrity finding (B15) |
   | `FAIL` on the Implementation Note's own claim, or a contradicted verification claim | The GD now (G63) — beyond any waiver |
   | `REVISE` | Close it if the coverage is still runnable; else the gap list |
   | `CONDITIONAL PASS` | CP4 — only the GD accepts it (G64) |
   | `PASS` and above | `producer` |
   | `Needs-decision` | A verdict contradicts its own evidence → `technical-architect`; correct work told to do the wrong thing → the GD (G4) |
   | `Rejected` on A1/A2 work | Skip to `producer`; never re-dispatch at a raised tier |

   `Iteration:` goes to the ledger's attempts used; `Not scored:` is a gap list.
5. **Checkpoint 4 (G60)** — every shape, whether or not any gate ran. `producer` compiles the Status Report
   from every QA report, `qa-lead`'s verdict as stated, the Assurance Verdict **or why there is none** (A1/A2,
   the gate refused, QA declined), and at D1–D2 both review verdicts — or "review was not run", in words. QA
   declined → compiled from the Implementation Notes; a single note goes to the GD directly, no `producer`.
   An acceptance state is not a sign-off: quote both, never merge them. Every declined gate and every gap the
   GD accepts (G9) is written to the ledger's *Accepted gaps* and, from A3, `DEBT.md` before closure is
   reported (I6); a mobile feature never run on a device says exactly that; a declined gate is never reported
   as passed. The GD names what is wrong; the split decides the door — the spec not met is a defect, the spec
   met but now unwanted is a change request.

## GD touchpoints

- **G60** — CP4, step 5. **G64** — `CONDITIONAL PASS` or an unmeetable criterion, accepted only there (G9).
- **G61** — the build or rebuild, asked up front, step 2 (G16 governs the build itself).
- **G62** — the test-code offer, step 3b, per G50.
- **G63** — a contradicted claim or a `FAIL` on the note's own claim, steps 3 and 4b.
- **G65** — `qa-lead` `Routed to: gd`, step 3.
- **G4** — a design flaw from any agent. **G6** — a `Blocked` only the GD can answer. **G7** — a bound below.
- **G50** — the shape of G61 and G62; G52 and G42 are this pipeline's way in.

## Bounds

B5 (a test suite at review E3) · B6 · B10 (shared) · B13 · B14 · B15 · B17 · B18 (re-offering declined QA or
test-code review at a later boundary).

## Exits

| Outcome | Control goes to | Written |
|---|---|---|
| Plan returned | Hold until **E2** | Ledger `QA plan`, verbatim |
| A defect | `feature-development.md` **E3**, back here at **E3** | Ledger `QA fails` +1 |
| B6, or B13 at its second | `technical-architect`, root cause (B10), then **E3** | Ledger `Root-cause resets` 1/1 |
| A bound after the reset | The GD (G7) | Ledger *Continuation debt* |
| Assurance `FAIL`, first | Owner at **E3** | Ledger `Rejections` assurance FAIL 1/1 |
| Coverage not yet run | Step 2, those agents only | Ledger `Rejections` sign-off re-dispatch +1 |
| Test code authorised | `review-pipeline.md` **E3** | Ledger submission row |
| Test code declined | Sign-off, marked unreviewed | `project-state.md` debt row |
| CP4 approved | Close — `orchestrator.md` → *The ledgers* | *Accepted gaps*, `DEBT.md` from A3, first |
| CP4 rejected as a defect | `feature-development.md` **E3** (B13) | Ledger `Rejections` CP4-as-defect +1 |
| CP4 rejected as a change request | `change-request.md` **E2** (G70) | No counter moves |
| E4 finished | The GD (G18) — no feature to close | `project-state.md` debt rows only |
| A design flaw; a contradicted claim | The GD (G4, G63) | — |
