# Bounds — every loop cap in the layer

The single home of every bound and every counter reset (I8). A loop whose cap is not here has none, and that is a
defect. Pipelines cite these by ID. The numbers were chosen, not measured — `<state-root>/calibration.md` records
what each closed feature actually spent; changing one is the GD's decision, proposed with evidence from real runs.

## Five rules

1. **A counter moves only on what its own row names** — a rejection, a Continuation Debt Record, a re-dispatch, a
   round that opens a bug. `Blocked`, `Needs-decision`, `Needs Confirmation`, coverage that is unrunnable (no
   toolchain, build, device or seam — as *stated* in the return) and a GD change request move no loop counter; B9
   and B17 count those asks on their own.
2. **Every loop gets one root-cause reset of its own (B10).** When B3, B6, B12 or B13 reaches its *Bound*,
   `technical-architect` names the cause and that counter restarts at zero; the fix re-enters
   `feature-development.md` **E3**. A loop never borrows another loop's reset, and nothing is traced across loops.
3. **After the reset, the *After reset* value stops the loop.** The work goes to the GD as a Continuation Debt
   Record (`execution-loop.md` fields, G7): every verdict and report from both runs, the architect's cause — a
   cause that did not hold is itself the finding — the known non-solutions, a safe resume point, and the next best
   action. The GD decides re-spec, cut or drop. A bound without an *After reset* value ends as its own row says.
4. **A GD answer is not re-asked at the boundary it was given.** It holds until the next boundary (B18) — a declined
   gate is re-offered there once, and a gate already authorised is never asked again. One
   follow-up on what an answer left unsettled — a bug no option ruled on — is a new question, not a re-ask.
5. **No bound overrides the GD (G8).** The GD may direct another round; the cost is stated first and the direction
   recorded in the ledger.

A terminated loop never reports closure, never re-dispatches the same brief, and never restarts a counter by
renaming or splitting the work. A fix being a new submission (`orchestration.md` → *Terms*) is not renaming: B6
stays on the bug, and B12, B13 and B15 on the feature.

## The bounds

| ID | Counter | Bound | After reset | Scope | On reaching the bound |
|---|---|---:|---:|---|---|
| **B1** | Attempt budget | 2–5 from **D** | — | One agent, inside one dispatch | Continuation Debt Record; one strike on its submission, where it has one. Home: `task-classification.md` Step 4 |
| **B2** | Advisor⇄Critic rounds | 3 | — | One feature's direction loop | Non-convergence to the GD (G7) |
| **B3** | Review strikes | 3 | 3 | One submission | Rule 2 |
| **B4** | Gated-direct strikes | 2 | — | One gated-direct submission | Escalate to `feature-intake.md` **E1** with both rejection sets and the code |
| **B5** | Test-code strikes | 2 | — | One `qa-automation-engineer` suite at review **E3** | Back to `qa-lead` as unrun coverage — never a feature request |
| **B6** | Bug reopens | 2 | 1 | One bug | Rule 2. An unattached bug has no ledger and no reset: it escalates to `feature-intake.md` **E1** — it was a feature all along |
| **B7** | Measure-and-confirm | 1 | — | One `cto` decision | What is still open goes to the GD (G32) |
| **B8** | Standalone re-decide | 1 | — | One rejected standalone decision | The GD decides directly (G33) |
| **B9** | `Needs Confirmation` asks | 3 | — | One credential-shaped value | Nobody can name a source → treated as a secret, one strike (G54) |
| **B10** | Root-cause reset | 1 | — | One loop: a submission's strikes, a bug's reopens, a feature's CP3 or CP4 rejections | Rule 3 |
| **B11** | CP2 rejections | 3 | — | One Tech Spec | To CP1 if available at this D, else to the GD with all three and what changed between them |
| **B12** | CP3 rejections | 2 | 1 | One feature | Rule 2 |
| **B13** | CP4 defect rejections | 2 | 1 | One feature | Rule 2 |
| **B14** | Sign-off re-dispatch | 2 | — | One feature's coverage loop | The unmet criterion goes to CP4 as a gap only the GD can accept (G64) |
| **B15** | QA rounds that open new bugs — a round is one execution pass (step 2 at **E2**) or one verification (**E3**), however many executors it dispatched; it counts once if any of them opens a bug, and the first execution round never counts | 3 | — | One feature, or one standalone QA run | The GD (G7), with every bug those rounds opened — new defects on every pass say the spec or the design is not holding, which no single fix answers |
| **B16** | Escalation-lane round trips | 1 | — | One implementing agent and one tech lead | A second refusal → `technical-architect`, as a routing question, with both escalations and both refusals attached |
| **B17** | Identical `Blocked` | 2 | — | One dispatch, one missing input | Reported to the GD as unresolved (G6). A different missing input starts its own count |
| **B18** | Gate re-offers | 1 per boundary | — | One artifact | A new boundary is a new fact — the end of implementation after a G40 decline (G42), the next feature on that root, a release, a defect traced to the ungated code, rework after a change request (G74), a defect fix awaiting verification where QA was declined, or the GD asking. Debt at A1–A2 is stated in the reply, never recorded or re-offered |

The assurance gate has no loop: every verdict short of `PASS` goes to the GD (G63 at once for a `FAIL`, CP4 for the
rest), who decides what returns to work.

**Where each counter is written** — before the next dispatch (I4). In the feature's ledger: B2, B11–B15 in
`Rejections:` and `Advisor⇄Critic:`; B3 and B5 per submission in *Submissions*; B6 on the bug's record; B10 in
`Root-cause resets:`; B7 in `Measure-and-confirm:`; B9, B16 and B17 in `Open asks:`, removed once answered. With no
ledger, in `project-state.md`: B4, and B5 for a suite with no ledger, under *Gated-direct counters*; B9, B16, B17 under *Open asks with no ledger*; B14
and B15 under *Standalone QA runs*; B7 and B8 under *Standalone decisions*.

## Resets — the complete list

- **The root-cause reset** (rule 2) — the triggering counter only.
- **A change request (G70)** is never a CP2, CP3 or CP4 rejection. Per submission it invalidates: strikes, attempts
  and that submission's root-cause reset return to zero. Per feature, when it reopens CP2 or CP1: B11, B12, B13,
  B14, B15 and their resets return to zero — the spec they counted against has changed. A **Major** also resets B2;
  the ruled-out options still travel. The author is never charged for the GD's change.
- **The GD directing another round** (rule 5) — recorded as a direction, never as a reset.

Nothing else resets a counter.
