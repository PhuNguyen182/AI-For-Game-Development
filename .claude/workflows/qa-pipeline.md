# QA Pipeline

One feature from the QA plan through Checkpoint 4 — or, at **E4**, one standalone run on work no ledger holds.
Optional and independent of review: it runs only on what the GD authorised at an ask shaped by G50
(`references/optional-gates.md`), whether or not review ran. CP4 is not optional — it fires for every feature.
Inputs for every door are in `references/dispatch-brief.md` → *QA*; caps are cited from `references/bounds.md`.

## Entries

| Door | Comes from | Carries |
|---|---|---|
| **E1** | QA authorised at `review-pipeline.md` step 6 (G52); at `feature-development.md`'s end-of-work ask where review was declined (G42); or opted into later on a feature with a ledger, even a closed one (reopened). **Plan only — execution locked** | The QA list in `dispatch-brief.md`, with both review verdicts — or that **the GD declined review**, in those words |
| **E2** | The plan is in, and: CP3 approved (D3–D5); or, with no CP3 owed — D1–D2, or review declined for every submission — each submission clear or its review declined | The ledger's `QA plan` |
| **E3** | A fix came back — through review where it ran, from the author where it did not | The plan — where QA is authorised only now, for this verification, `qa-lead` plans the bugs' cases first (step 1) — and **the bug IDs the fix marked `Fixed`** with their records — a GD-opened bug has no original report, its record stands in. Those bugs are verified by ID, plus the coverage the fix touched; device coverage needs a **rebuilt** artifact (G61). Reached only when QA was authorised for this feature — otherwise the verification is first put to the GD per G50 |
| **E4** | The GD asks for QA on work **no ledger holds** — shipped code, work no pipeline built, a direct-lane measurement (G15), or the verification of an unattached bug's fix; `orchestrator.md` row 7 | The behaviour and its source, the platform, the budget if performance is judged, and any unattached bug IDs to verify; review verdicts marked absent. The run is classified on its own |

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
| `technical-architect` | Root Cause (B6, B10); an answer where the spec leaves "correct" open | Step 3, step 4b, the B6/B13 exits |
| `tech-lead-performance` | Diagnosis of a native, GPU or leak finding | Step 3; a fix it writes is a bug owner's submission at `feature-development.md` **E3** |

Every other fix goes to its owner as a bug at `feature-development.md` **E3**, never dispatched from here.

Review verdicts are consumed as given, never re-decided. `crash-anr-investigator` is never dispatched here — it
takes released-production telemetry only.

## Hard ordering

1. The plan before any execution; execution only from **E2**, a verification at **E3**, or a standalone **E4**.
2. Locks claimed before dispatch, released on return: the three Editor holders run **serially** under the Editor
   lock (I3); `build-verification-tester` may run alongside them, never beside `performance-qa-engineer` on the
   same device (I7).
3. Device coverage: the build asked for (G61) before any device agent is dispatched; the device confirmed before
   the artifact is touched; a crash stops that case's path.
4. The test-code offer (G62) before a suite's results are used as sign-off evidence.
5. Sign-off, then the assurance gate — after every other verdict — then `producer`. At A3+ a gap that cannot be
   closed passes step 4b before CP4.
6. Every gap written to the ledger's *Open gaps* as it arises — at **E4**, to its *Standalone QA runs* row —
   accepted ones mirrored before closure is reported (I6).

## Steps

1. **Plan.** `qa-lead` in plan mode needs only the spec, the tier and the V-number, so it runs while CP3 is with
   the GD. It returns a **coverage assignment** (which `agent-id` covers what) and **exit criteria stated at the
   floor's evidence level** — V2 a targeted direct test; V3 adding edge cases, a dependency pass and a regression
   check; V4 adding the acceptance criteria and a separate final pass. Both go **verbatim** into the ledger's
   `QA plan` now (at **E4**, `project-state.md` → *Standalone QA runs*), and travel back verbatim at step 4; where
   they cannot be recovered, the sign-off dispatch says so. Open the feature's `BUGS.md`, if the first bug has not
   already opened it, from `state/templates/feature-bugs.md` if it does not exist, and write one *Test cases* row
   per case the assignment names.
2. **Execute.** Dispatch exactly the `agent-id`s the assignment names, each with the path to the feature's
   `BUGS.md` (at **E4**, `bug-log.md` → *Unattached bugs*) and the test-case IDs it covers, so a finding matching a
   known bug cites its ID and every result is keyed to its case. Record each return's bugs **before the next
   dispatch**, so the next executor sees them. At **E3**, each bug to verify goes to the agent whose coverage found
   it; for a GD-opened bug, `qa-lead` in plan mode first adds its case and names the agent, and that agent
   completes the bug's record as it verifies.

   First check the assignment against what exists: device coverage with no artifact → G61 now, carrying what that
   coverage is to prove; declined → unrun from the outset, into *Open gaps*. Default Editor order:
   `qa-automation-engineer` first (its domain reload lands before Play Mode), `performance-qa-engineer` last (a
   quiet Editor) — a choice, not a contract. Where review was declined, tell `qa-automation-engineer` the GD was
   offered it, declined, and authorised QA anyway; at **E4** on code already in the repo, that review is not part
   of this run. **2b — the device lane**, only with a produced build: `build-verification-tester` gets the build's
   `Result:` (path, platform, configuration) and the cases `/plan-test-coverage` derived, filtered to those marked
   `Observe via: build/device` that `qa-lead` assigned — the command never decides what is owed. No device → that
   coverage is unrun; the artifact-only checks still run; the Editor is never a substitute. A crash or ANR: logs
   pulled, no silent relaunch, `/investigate-device-crash`. A fix to a device-found defect is never re-verified on
   the stale build — ask for a rebuild (G61), else that coverage stays unrun.
3. **Read every return's body, not its `Status:`** — `Done` carrying defects is a completed job. Beyond
   `orchestrator.md`'s defaults:

   | Return | Action |
   |---|---|
   | `Defects:`, `Regressions:`, or a finding classified `Technical defect` — the envelopes share no field | Each finding becomes a bug: a new ID in `<state-root>/bug-log.md` and its record in `BUGS.md`, or evidence on the bug it cites (a cited `Closed` or `Accepted unverified` bug → `Reopened`; a cited `Won't fix` bug → evidence only). Every `Open` or `Reopened` bug goes to its owner at `feature-development.md` **E3**, a new submission per fix — unless the GD has ruled it `Won't fix` (G9), which they may do at any point. A round that opens a new bug, after the first execution round, counts once toward B15 |
   | `Bug verification:` | Per ID: passes → `Closed`, unless the evidence is a suite whose test-code review is authorised but not yet cleared — then it stays `Fixed` until it clears; still fails → `Reopened`; not exercised → stays `Fixed`, into *Open gaps*. A bug reaching B6 goes to root cause (B10) **before** it returns to **E3**; an unattached one escalates instead (B6) |
   | Results per test case | That case's `Latest result` in `BUGS.md` |
   | A design flaw, from any agent or the device lane | Opened as a bug, `Escalated`, and put to the GD now as a ruling (G4) — it never re-enters the engineering loop unless that ruling makes it `Open` |
   | A finding classified `As designed` | Recorded as `As designed`, so the expectation is not raised again |
   | A finding later seen to duplicate a recorded bug | Its evidence moves to the original; its row becomes `Duplicate of BUG-####` |
   | A contradicted verification claim | The GD now (G63), and to step 4b if it has not run — never the accepted-gap lane |
   | `Results: 0 / 0`, or findings labelled inspection | Unrunnable: its findings routed as inspection-grade defects, never as coverage that ran; every case into *Open gaps*. Not a Continuation Debt Record; spends no B14 |
   | A Continuation Debt Record | Coverage unrun, not failed: ledger *Continuation debt*, and *Open gaps* |
   | `Not covered:` / `Not measured:` | *Open gaps*. `playtest-tester` has no such field — note what its scenario missed against the plan |
   | `Metrics:` | The ledger's `Baseline:` where none existed, written at the return. `Measured on:` travels with every quotation; an Editor figure is indicative and never satisfies a device claim |
   | `qa-lead` → `Routed to: gd`, either mode | Act on it at the step it arrived (G65) |
   | `qa-lead` → `Needs-decision` — no testable behaviour, or reports contradict | `technical-architect` |
   | `performance-qa-engineer` → `Needs-decision` | Native, GPU or leak → `tech-lead-performance`; budget unachievable for the design → `technical-architect` |
   | `build-verification-tester` → `Blocked`, `Routed to: build-run-engineer` | No artifact: G61, never a build off pipeline state |
   | A build-only fault | By evidenced cause: the artifact → `build-run-engineer`, on the GD's request (G61); client code after IL2CPP or stripping, or an SDK or store integration → a bug owned by `unity-engineer` or `tech-lead-sdk-platform`, fixed at `feature-development.md` **E3** |
   | `build-run-engineer` → `Rejected`, `Routed to: gd` | A correct refusal — get the GD's request or drop the branch |
   | A finding outside the assignment | To its owner, and named to `qa-lead` so the criterion it touches is re-planned |

   **3b — test code.** As soon as `qa-automation-engineer` has written a suite (`Tests added:`), put G62 per G50 —
   saying whether it has run, and that a test asserting the wrong behaviour reports green and advertises coverage
   that does not exist. Yes → `review-pipeline.md` **E3**, test-code origin, paths onto the ledger's submission
   table at `/2`; its results serve as sign-off evidence only once both gates clear it, and at B5 it returns to
   `qa-lead` as unrun coverage. No → a review debt row in `project-state.md`; the results are still reported,
   marked as **unreviewed test code** wherever they are quoted.
4. **Sign-off.** `qa-lead` judges against the plan carried back verbatim, the review verdicts as given or stated
   absent, and the feature's `BUGS.md`; it never signs off while a gap remains or a bug is unsettled
   (`defect-reporting.md`). A bug whose fix exhausts its bounds reaches the GD through G7, where G9 can make it
   `Won't fix`. Act on the gap by kind: **not yet run** → re-dispatch exactly those `agent-id`s (B14 counts only
   runnable coverage); **unrunnable**, as the return *states* it (an environment check, `0 / 0`, a `Not covered:`
   naming the missing toolchain, build, device or seam) → straight into *Open gaps*; **cannot be closed** → step 4b
   at A3+, then CP4 (G64). A bug reopened twice → root cause (B6, B10). **4b — the assurance gate**, A3+ or when
   the GD asks (G80); runs last. Dispatch every verdict as given, and the review status in `dispatch-brief.md`'s
   words, the Implementation Notes, the H/M/Q list, the tier, and attempts used with, past the first, what improved
   (unknown is said, and stays unevidenced).

   | Acceptance | Action |
   |---|---|
   | `FAIL`, on any claim, or a contradicted verification claim | The GD now, as a ruling (G63) — back to its owner at **E3**, or the work dropped; never an accepted gap |
   | `REVISE` | Into *Open gaps*, with what it asks revised; the GD rules on it at CP4 (G64) |
   | `CONDITIONAL PASS` | CP4 — only the GD accepts it (G64) |
   | `PASS` and above | `producer` |
   | `Needs-decision` | A verdict contradicts its own evidence → `technical-architect`; correct work told to do the wrong thing → the GD (G4) |
   | `Rejected` on A1/A2 work | Skip to `producer` — unless the GD asked for the score: then re-dispatch saying so; never at a raised tier |

   `Iteration:` goes to the submission's attempts used; `Not scored:` goes into *Open gaps*.
5. **Checkpoint 4 (G60)** — every feature with a ledger, every shape, whether or not any gate ran. `producer`
   compiles the Status Report from every QA report, `qa-lead`'s verdict as stated, the Assurance Verdict **or why
   there is none** (A1/A2, the gate refused, QA declined), and at D1–D2 both review verdicts — or "review was not
   run", in words. QA declined → compiled from the Implementation Notes; a single note goes to the GD directly, no
   `producer`. An acceptance state is not a sign-off: quote both, never merge them. `producer` is given the
   feature's `BUGS.md`; the report carries its bug summary — counts by status and severity, and every bug not yet
   settled. The CP4 ask rules on every unsettled bug before the closing question, per G60; a bug sent round its
   loop (**E3**, or step 2 at **E3**) brings CP4 back. An `Escalated` bug left unruled gets G60's one follow-up;
   still unruled, the feature waits at CP4. Every declined gate, every gap and every bug the GD accepts (G9) is
   marked accepted in the ledger's *Open gaps* and, from A3, appended by the orchestrator to the feature root's
   `DEBT.md` before closure is reported (I6); a mobile feature never run on a device says exactly that; a declined
   gate is never reported as passed. The GD names what is wrong: the spec not met → reject as a defect; the spec
   met but no longer wanted → reject as a change request. A defect fixed after CP4 comes back through steps 3–5,
   and CP4 asks again.

## GD touchpoints

Where each fires; what it carries and what happens on no are `gd-touchpoints.md`'s alone. **G42** and **G52** are
this pipeline's way in.

**G61** step 2 · **G65** step 3 · **G62** step 3b, shaped by **G50** · **G63** steps 3 and 4b · **G60**, **G64**
step 5 · **G66** at the end of an **E4** run · anywhere: **G4**, **G6**, **G7**.

## Bounds

B5 (a test suite at review E3) · B6 · B10 (one per loop) · B13 · B14 · B15 (rounds that keep opening new bugs) ·
B17 · B18 (re-offering declined QA or test-code review at a later boundary).

## Exits

| Outcome | Control goes to | Written |
|---|---|---|
| Plan returned | Hold until **E2** | Ledger `QA plan`, verbatim |
| A defect | `feature-development.md` **E3**, back here at **E3** | Bug `Open` in `bug-log.md` and `BUGS.md` |
| A bug verified | `Closed` — or `Reopened`, back to **E3** | Status in both files, history row in `BUGS.md`; `Reopens` +1 on a reopen. A pass from test code the GD declined to review still closes, and its history row says so |
| B6 (a bug reopened twice), or B13 at its second | `technical-architect`, root cause (B10), then **E3** | Ledger `Root-cause resets` 1/1 for that loop; for B6, a history row on the bug with the cause, and its `Reopens` restarted at 0/1 in both files |
| An *After reset* value reached | The GD (G7) | Ledger *Continuation debt* |
| B15 reached | The GD (G7), with every bug those rounds opened | Ledger `Rejections` QA rounds 3/3 |
| Assurance `FAIL` | The GD (G63) | Ledger *Open gaps* until the GD rules |
| Coverage not yet run | Step 2, those agents only | Ledger `Rejections` sign-off re-dispatch +1 |
| Test code authorised | `review-pipeline.md` **E3** | Ledger submission row |
| Test code declined | Sign-off, marked unreviewed | `project-state.md` debt row |
| CP4 approved | Close — `orchestrator.md` → *The ledgers* | Accepted gaps marked in *Open gaps*, and `DEBT.md` from A3, first |
| CP4 rejected as a defect | `feature-development.md` **E3** (B13) | Ledger `Rejections` CP4-as-defect +1 |
| CP4 rejected as a change request | `change-request.md` **E2** (G70) | Not a CP4 rejection; resets per `references/bounds.md` → *Resets* |
| E4 finished | The GD (G18) — no feature to close; G66 for any bug left `Open` or `Reopened` | `project-state.md` debt rows; its bugs under *Unattached bugs* in `bug-log.md` |
| A design flaw; a contradicted claim | The GD (G4, G63) | A design flaw: bug `Escalated` in both files |
