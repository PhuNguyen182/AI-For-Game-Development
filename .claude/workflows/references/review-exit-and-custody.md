# Review Exits & Custody — `review-pipeline.md`

> **Read when a verdict is in and something has to leave this pipeline.** Split out of `review-pipeline.md`
> under the promotion rule in `client/feature-documentation.md`. That file owns the sequence; this one owns
> **where each result goes** and **which returned field would otherwise be dropped**.

Three rounds of this series closed the same class one instance at a time: *an agent produces something no
pipeline row receives.* It is closed here as a class — the table below has a row for every field either gate
can return, not only for the ones `Status:` and `Verdict:` name.

## The doors this pipeline hands to

`review-pipeline.md` declared none of these until this file existed, while four other files named it as their
origin or their destination.

| What leaves | Goes to | When |
|---|---|---|
| A cleared submission, feature still open | nowhere — wait for the feature's others | any |
| Both finding sets + the strike count | `feature-development.md` **E3** | a rejection at **E1** |
| Both finding sets + the strike count | the author directly, per `references/gated-direct-lane.md` | a rejection at **E3**, strike 1 |
| Both rejection sets + the code | `feature-intake.md` **E1** | strike 2 on a **gated-direct** E3 submission |
| Both rejection sets + the code | `qa-pipeline.md`, as unrun coverage | strike 2 on a **test-code** E3 submission — a suite is not a feature request |
| The rejection history + the code | `technical-architect` | third strike, **E1** only |
| The Implementation Summary | **CP3**, then the GD | every submission clear, D3–D5 |
| The named drift | `feature-development.md` **E3** | CP3 rejected as drift |
| The spec itself | `change-request.md` | CP3 rejected because the *spec* is wrong — not a CP3 rejection at all |
| The QA ask, then the feature | `qa-pipeline.md` **E1**, or a recorded QA debt | step 6 |
| A findings report, no strike | the GD | **E2**, the standalone audit |
| A feature-level Continuation Debt Record | the GD | any cap in `loop-termination.md` reached |

## Custody — every returned field, and where it goes

**Route on the envelope, not on `Status:` alone.** A live run returned the round's highest-value content in
fields no status row mentions.

| Returned | Destination |
|---|---|
| `Verdict: Approve` / `Clear` | Step 2's clear test. Both, or it is not clear |
| `Verdict: Request changes` / `Verdict: Blocked` | Back to the author, +1 strike. **`Verdict: Blocked` is a rejection, never a missing input** — see below |
| `Status: Blocked` | Supply the input named. Never a strike, and bounded at two identical returns |
| `Verdict: Needs Confirmation` | `references/review-needs-confirmation.md`. Never a strike |
| A **design flaw**, on any status, from either gate | **The GD, immediately** — invariant **I5**. `code-reviewer`'s guardrail bars it from widening into design intent, so it *notes and routes*; this is the route. Never folded into CP3 |
| A finding whose remediation is a **`cto` decision** — key rotation, a history rewrite | `cto`, **alongside** the return to the author. Live, `security-reviewer` put "the rotation decision belongs to `cto`" inside a `Recommendation:` while its `Routed to:` said `csharp-engineer`; the pipeline's only `cto` row was for git-history exposure, and history was clean |
| A **second destination** named anywhere in the return | Record every one and act in the order the return states. `Routed to:` is single-valued, so each one after the first is what gets dropped. `feature-development.md` and `research-decision.md` both carry this row for the same reason |
| `Assessed: Escalate` from either gate | Its own routing row — `technical-architect` for an ambiguous spec, `cto` for git history. Not a verdict, and not a strike |
| A **Root Cause** from `technical-architect` at strike three | `feature-development.md` **E3** with the fix brief. It is a **four-field body** on the usual envelope — `Root cause:`, `Evidence across rejections:`, `Known non-solutions:`, `Next best action:` — and each field has a different destination: the cause and the evidence go into the ledger, the **known non-solutions into the return brief** so the next cycle does not re-buy a proven failure, and `Next best action:` addressed to the owning `agent-id`. Until this round the envelope defined no body for this path at all and the cause arrived as prose, which is how **R3** failed |
| An Implementation Note field the gate found **unsupported** | Stays with the submission. `qa-lead` and `assurance-evaluator` read it next, and a claim the gate already doubted is not re-cleaned on the way |

## `Blocked` is two different returns, and they are opposite

`security-reviewer`'s envelope carries **both** `Status: Blocked | Done | …` and `Verdict: Clear | Blocked |
Needs Confirmation`. The word is the same and the actions are opposite:

| Read | Means | Action |
|---|---|---|
| `Status: Blocked` | The gate could not review — an input is missing | Supply it. **No strike** |
| `Verdict: Blocked` (on `Status: Done`) | The gate reviewed and **rejected** it | Back to the author. **+1 strike** |

A live run returned `Status: Done`, `Verdict: Blocked` on a Critical hardcoded credential. A caller matching
a bare `Blocked` against the wrong row answers a security rejection by asking for an input — and the finding
is lost. This is the same hazard as `Status: Done` on a review that requests changes, which the pipeline
already warns about; it runs in both directions.

## The supply-chain pre-gate — the one submission that is not optional

`security.md` §7 forbids treating a `.unitypackage`, an Asset Store import or a vendored DLL as adopted until
`security-reviewer` has cleared it, and `references/development-exit-and-custody.md` routes it here at **E1**
*before* the integration is written. Three things about it differ from every other E1 submission:

- **It is not the optional gate.** `security.md` carries no tier and no lane exemption, so this one is owed
  whatever the GD answered about review. The optional gate judges afterwards; by then the `Editor/` folder's
  `[InitializeOnLoad]` payload has already run.
- **`security-reviewer` runs alone.** There is no spec and no intended behaviour, so `code-reviewer` returns
  `Status: Blocked` by its own required-input table — exactly as at **E2**. Dispatching both and waiting for
  an `Approve` that cannot arrive deadlocks step 2's clear test.
- **Its verdict is a go/no-go on the import**, not a strike against an author. Nobody wrote it.

## The three returns that do not wait for an exit

- **A design flaw** — to the GD the moment it lands, per **I5**.
- **A secret that may already be in git history** — to `cto`, per the routing table. No code-writing agent
  self-remediates published history.
- **A Continuation Debt Record** — recorded in the ledger at the transition, not at closure, or the known
  non-solutions are gone by the time the next cycle needs them.
