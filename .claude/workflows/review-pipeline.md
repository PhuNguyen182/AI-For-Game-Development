# Review Pipeline

One submission through the two review gates, and, once per feature, Checkpoint 3. Optional and separate from QA: it
runs only on what the GD authorised at an ask shaped by G50 (`references/optional-gates.md`), put by whoever
reached the boundary. The one exception is the supply-chain pre-gate (G45), owed whatever the GD answered. Inputs
for every door are in `references/dispatch-brief.md` → *Review gates*; caps are cited from `references/bounds.md`.

## Entries

| Door | Comes from | Carries |
|---|---|---|
| **E1** | `feature-development.md` after the GD authorised review (G40, G42) — one submission per entry, a defect fix from its **E3** included: the Core, each client or backend agent, the README; a tech lead's `Fix:` (I10); a declined gate opted into later, author and brief still identifiable, strikes from zero; **third-party content at the supply-chain pre-gate** (G45) | The review-gate list in `dispatch-brief.md`; its pre-gate row for third-party content |
| **E2** | The GD asks for an audit of code already in the repo (`orchestrator.md` row 6), or opts into review later on code no submission identifies | The code and what it is audited against — or `security-reviewer` alone. No author, strike, CP3, note or ledger; the audit is classified on its own (`task-classification.md`) |
| **E3** | A gated-direct submission, only once the GD authorised it at G14 (`orchestrator.md`); or a `qa-automation-engineer` suite the GD authorised at G62 (`qa-pipeline.md`) | As E1, with the behaviour it was written against instead of a spec section, and **which origin** it is |

## May dispatch

| Agent | Produces | When |
|---|---|---|
| `code-reviewer` | Review Verdict — correctness against the spec, bugs, Shared-Core duplication | E1, E3; E2 only when the audit names what it checks against |
| `security-reviewer` | Security Verdict — secrets, dangerous files, fraudulent logic | Every door; alone at the pre-gate and wherever E2 names nothing to check against |
| `technical-architect` | Root Cause (`Root cause:`, `Evidence across rejections:`, `Known non-solutions:`, `Next best action:`); Implementation Summary (CP3) | At B3 or a second CP3 rejection; at CP3 |
| `cto` | A remediation decision | A secret in git history, or a rotation the finding calls for — alongside the return, never instead |
| `tech-lead-sdk-platform` | Where a value is sourced from | The G54 ladder, on an SDK or platform integration |
| `assurance-evaluator` | Assurance Verdict | **E3** gated-direct at A3+, once both gates clear, if the GD authorised it at G14 |

## Hard ordering

1. Third-party content is cleared by `security-reviewer` **before** it lands — an `Editor/` or `[InitializeOnLoad]`
   payload runs on import, before any later gate could judge it.
2. Both gates are dispatched together, and **nothing returns to the author until both verdicts are in** — returning
   findings as they land costs one submission two round trips and two strikes.
3. At B3, `technical-architect` before any further review pass; at a second CP3 rejection, before the drift is
   re-dispatched.
4. CP3 only once every submission is clear or its review was declined; it covers the reviewed ones and names the
   rest as unreviewed.
5. QA execution never before CP3 is approved (D3–D5); QA planning may run during it.

## Steps

1. **Dispatch both gates in parallel**, each told the other runs alongside and is not to be waited on. The floor
   travels as a **V-number** and is never the gate's to derive; absent it, `code-reviewer` reviews and says it was
   not supplied — a finding against the brief, never a strike. Neither gate edits code. The Core submission is on
   the critical path — `feature-development.md`'s fan-out may be waiting on its verdict. The pre-gate dispatches
   `security-reviewer` alone: a go/no-go on the import, not a strike.
2. **Decide on `Verdict:`, never on `Status:`.** A review requesting changes is `Status: Done`. `Status: Blocked`
   means a missing input — supply exactly it, asking the GD when only they hold it (G6, B17), no strike.
   `Verdict: Blocked` on `Status: Done` is a security **rejection**. Beyond `orchestrator.md`'s defaults:

   | Return | Action |
   |---|---|
   | `Approve` **and** `Clear` | The submission is clear — the only clear |
   | `Request changes`, or `Verdict: Blocked` | One combined return, step 3. Any `Needs Confirmation` beside it travels with the findings — a rejection outranks the ladder |
   | `Needs Confirmation`, no rejection beside it | The ladder (G54, B9): `tech-lead-sdk-platform` for an SDK or platform integration, else the author, then the GD; re-run the gate on the answer. Never guessed either way — nobody can name a source → a secret, `Request changes`, one strike |
   | `Verification done:` below the floor | `Request changes` and a strike — the author's to close, never QA's to absorb |
   | `code-reviewer` → `Needs-decision`, `Routed to: technical-architect` | The spec is ambiguous about "correct" — a spec problem, not a strike. On a gated-direct **E3** there is no spec: the lane escapes to `feature-intake.md` **E1** (`orchestrator.md`) |
   | `security-reviewer` → `Needs-decision`, `Routed to: cto` (git history) | Straight to `cto` — not a `research-decision.md` entry. Published history is never self-remediated by a code-writing agent |
   | A `cto` remediation outside history — rotation, a burned credential, often inside `Recommendation:` | To `cto` **alongside** the return to the author |
   | `Rejected` | Mis-dispatch: re-dispatch to the right gate — no strike |
   | `Assessed: Escalate` | Its `Needs-decision` row above; not a verdict |
   | A gate says its mandatory skill did not resolve | It ran at reduced depth — record that with the verdict |
   | A note field the gate found unsupported | Stays with the submission, for `qa-lead` and `assurance-evaluator` |

3. **Return** — from E1 to `feature-development.md` **E3**, from E3 to the author directly: both finding sets, the
   strike count, every prior verdict, and the known non-solutions of any Continuation Debt Record. Strikes per
   `bounds.md` rule 1: one round trip is one strike whichever gate caused it; a Continuation Debt Record is one
   strike (B1). Write the strike and verdicts to the ledger's submission table — a test suite with its `/2` bound —
   or, for gated-direct, `project-state.md` → *Gated-direct counters*, before the next dispatch; a Continuation
   Debt Record goes to the ledger's *Continuation debt* at the same transition.
4. **At the bound.** **E1, B3:** `technical-architect` with the full rejection history and the code. Its known
   non-solutions go into the return brief, `Next best action:` to the owning agent, the cause on the ledger's
   `Root-cause resets` row, since a later stop must quote it; the fix re-enters `feature-development.md` **E3**
   with its strikes restarted (B10). A stalled Core stalls the feature, correctly. B3's *After reset* value stops
   it (rule 3, G7). **E3:** gated-direct at B4 → `feature-intake.md` **E1** with both rejection sets and the code;
   test code at B5 → `qa-pipeline.md` step 4, as unrun coverage for `qa-lead` to weigh, never intake.
5. **Checkpoint 3 (G51)** — D3–D5 only, once per feature, only when review ran; at D1–D2 it merges into CP4, and
   the A-tier never adds one. `technical-architect` compiles from every cleared submission's Implementation Note
   and both verdicts: `Built:` in the spec's terms; `Matches spec intent:` with **every drift named**;
   `Known limitations:`, each owed in the feature root's `DEBT.md` from A3, appended by the submission that
   produced it. Approve → QA execution at `qa-pipeline.md` **E2** where QA was authorised, else CP4 (G60). Reject
   as drift → the named drift to its owner at `feature-development.md` **E3**, never CP2 (B12). The spec itself
   wrong → not a CP3 rejection: `change-request.md` (G70).
6. **The QA ask (G52)** — only when G40 authorised review (else G42 asked it), once every **E1** submission is
   clear, **not after CP3** — never on **E3**, whose origins end elsewhere (gated-direct with the GD, test code
   back in `qa-pipeline.md`), per G50, carrying the V-number. Yes → `qa-pipeline.md` **E1**, where `qa-lead` plans
   while CP3 is with the GD (**E4** where no ledger holds the work); nothing the plan produces is invalidated by a
   CP3 rejection. At D1–D2, with no CP3, execution unlocks at **E2** once the plan is in. No → a QA debt row in
   `project-state.md`, never coverage.

## GD touchpoints

Where each fires; what it carries and what happens on no are `gd-touchpoints.md`'s alone.

**G45** at the pre-gate · **G54** step 2 · **G53** step 3 · **G51** step 5 · **G52** step 6, shaped by **G50** ·
**G55** at **E2** · anywhere: **G4**, **G6**, **G7**.

## Bounds

B1 (a Continuation Debt Record is one strike) · B3 · B4 · B5 · B9 · B10 (one per loop) · B12 · B17 · B18
(re-offering a declined review at a later boundary).

## Exits

| Outcome | Control goes to | Written |
|---|---|---|
| A submission clear, others outstanding | Wait for the rest | Ledger: verdicts landed |
| A defect fix clear (from `feature-development.md` **E3**, carrying bug IDs) | Those bugs → `Fixed`; `qa-pipeline.md` **E3** to verify them where QA is authorised for this feature — otherwise the verification is put to the GD per G50, and a no leaves them `Fixed` for CP4 | Bug status in `bug-log.md` and `BUGS.md` |
| A gated-direct submission clear | `assurance-evaluator` if authorised, then the GD (`orchestrator.md`) | *Gated-direct counters* |
| Every **E1** submission clear | G52 where G40 authorised review; then CP3 (D3–D5), or, at D1–D2, `qa-pipeline.md` **E1** on a yes — execution at **E2** once the plan is in | Ledger; a QA debt row in `project-state.md` on a no |
| Rejection at E1 | `feature-development.md` **E3** | Ledger: strike +1, verdicts landed |
| Rejection at E3, under its bound | The author | Ledger (test code) or *Gated-direct counters* |
| B3 | `technical-architect`, then `feature-development.md` **E3** | Ledger: `Root-cause resets` 1/1, with the cause |
| B4 | `feature-intake.md` **E1** | *Gated-direct counters* |
| B5 | `qa-pipeline.md` step 4 — `qa-lead`, as unrun coverage | Ledger: the suite's row |
| An *After reset* value reached — B3 again, or a third CP3 rejection (B12) | The GD (G7) | Ledger: *Continuation debt* |
| CP3 approved | `qa-pipeline.md` **E2** where QA was authorised, else CP4 (G60) | — |
| CP3 rejected as drift | `feature-development.md` **E3** | Ledger: `Rejections` CP3 +1 |
| CP3 objection is the spec | `change-request.md` (G70) | Not a CP3 rejection; resets per `references/bounds.md` → *Resets* |
| Pre-gate verdict | `feature-development.md` — go, or not adopted | — |
| E2 audit finished | The GD (G55) | — |
| Secret in history, or a rotation | `cto`, beside any return to the author | — |
| A design flaw | The GD (G4) | — |
