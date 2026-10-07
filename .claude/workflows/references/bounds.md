# Bounds — every loop cap in the layer

The single home of every bound (I8). A loop whose cap is not here has none, and that is a defect. Pipelines
cite these by ID. The numbers were chosen, not measured — `<state-root>/calibration.md` records what each closed feature actually spent; changing one is the GD's decision, proposed with
evidence from real runs.

## Five rules

1. **Only a rejection of the work counts as a round.** `Blocked`, `Needs-decision`, `Needs Confirmation`,
   coverage that is unrunnable (no toolchain, build, device or seam — as *stated* in the return), and a GD
   change request never spend a round.
2. **On reaching B3, B6, B12 or B13, one root-cause reset per submission (B10)** — `technical-architect` names the cause,
   the strike count returns to zero, and the fix re-enters `feature-development.md` **E3**. The reset is shared:
   whichever loop spends it, there is no second.
3. **The next of those bounds after the reset stops the loop.** Every other bound ends as its own row says. The work goes to the GD as a Continuation Debt Record
   (`execution-loop.md` fields, G7): every verdict and report from both runs, the architect's cause — a cause
   that did not hold is itself the finding — the known non-solutions, a safe resume point, and the next best
   action. The GD decides re-spec, cut or drop.
4. **A GD answer is not re-asked in the same run.** A declined gate is re-offered only at a new boundary (B18).
5. **No bound overrides the GD (G8).** The GD may direct another round; the cost is stated first and the
   direction recorded in the ledger.

A terminated loop never reports closure, never restarts a counter by renaming or splitting the work, and never
re-dispatches the same brief.

## The bounds

| ID | Counter | Bound | Scope | On reaching it |
|---|---|---:|---|---|
| **B1** | Attempt budget | 2–5 from **D** | One agent, inside one dispatch | Continuation Debt Record; the return is one strike. Home: `task-classification.md` Step 4 |
| **B2** | Advisor⇄Critic rounds | 3 | One feature's direction loop | Non-convergence to the GD. A **Major** change request resets it; the ruled-out options still travel |
| **B3** | Review strikes | 3 | One submission | Rule 2 (B10) |
| **B4** | Gated-direct strikes | 2 | One gated-direct submission | Escalate to `feature-intake.md` **E1** with both rejection sets and the code |
| **B5** | Test-code strikes | 2 | One `qa-automation-engineer` suite at review **E3** | Back to `qa-lead` as unrun coverage — never a feature request |
| **B6** | QA fails | 2 | One submission that passed review and failed QA | Rule 2 (B10) |
| **B7** | Measure-and-confirm | 1 | One `cto` decision | What is still open goes to the GD (G32) |
| **B8** | Standalone re-decide | 1 | One rejected standalone decision | The GD decides directly (G33) |
| **B9** | `Needs Confirmation` asks | 3 | One credential-shaped value | Nobody can name a source → treated as a secret, one strike (G54) |
| **B10** | Root-cause reset | 1 per submission | Shared by B3, B6, B12, B13 | Rule 3 |
| **B11** | CP2 rejections | 3 | One Tech Spec | To CP1 if available at this D, else to the GD with all three and what changed between them |
| **B12** | CP3 rejections | 2 | One feature | 1st → **E3**; 2nd → root cause first (B10), then **E3**; next → stop (rule 3) |
| **B13** | CP4 defect rejections | 2 | One feature | 1st → **E3**; 2nd → root cause first (B10); 3rd → stop (rule 3) |
| **B14** | Sign-off re-dispatch | 2 | One feature's coverage loop | The unmet criterion goes to CP4 as a gap only the GD can accept (G64) |
| **B15** | Assurance `FAIL` | 1 | One submission | The first returns to its owner at **E3** as an integrity finding; a second counts as a QA fail (B6). Never a waiver |
| **B16** | Escalation-lane round trips | 1 | One implementing agent and one tech lead | A second refusal → `technical-architect`, as a routing question, with both escalations and both refusals attached |
| **B17** | Identical `Blocked` | 2 | One dispatch, one missing input | Reported to the GD as unresolved (G6). A different missing input starts its own count |
| **B18** | Gate re-offers | 1 per boundary | One artifact | A new boundary is a new fact — the next feature on that root, a release, a defect traced to the ungated code, or the GD asking |

A change request (G70) never counts at CP2, CP3 or CP4, and resets the strike counts, attempt budgets, those
three rejection counters and the root-cause reset on every submission it invalidates — the author is not
charged for the GD's change.
