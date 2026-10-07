# Review Pipeline

One submission through the two review gates, and, once per feature, Checkpoint 3. Optional and separate from
QA: it runs only on what the GD authorised at an ask shaped by G50 (`references/optional-gates.md`), put by
whoever reached the boundary. The one exception is the supply-chain pre-gate (G45), owed whatever the GD
answered. Inputs for every door are in `references/dispatch-brief.md` → *Review gates*; caps are cited from
`references/bounds.md`.

## Entries

| Door | Comes from | Carries |
|---|---|---|
| **E1** | `feature-development.md` after the GD authorised review (G40, G42) — one submission per entry: the Core, each client or backend agent, the README; a tech lead's `Fix:` (I10); a declined gate opted into later, author and brief still identifiable, strikes from zero; **third-party content at the supply-chain pre-gate** (G45) | The review-gate list in `dispatch-brief.md`; its pre-gate row for third-party content |
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

## Hard ordering

1. Third-party content is cleared by `security-reviewer` **before** it lands — an `Editor/` or
   `[InitializeOnLoad]` payload runs on import, before any later gate could judge it.
2. Both gates are dispatched together, and **nothing returns to the author until both verdicts are in** —
   returning findings as they land costs one submission two round trips and two strikes.
3. At B3, `technical-architect` before any further review pass; at a second CP3 rejection, before the drift is
   re-dispatched.
4. CP3 only after **every** submission for the feature is clear.
5. QA execution never before CP3 is approved (D3–D5); QA planning may run during it.

## Steps

1. **Dispatch both gates in parallel**, each told the other runs alongside and is not to be waited on. The
   floor travels as a **V-number** and is never the gate's to derive; absent it, `code-reviewer` reviews and
   says it was not supplied — a finding against the brief, never a strike. Neither gate edits code. The Core
   submission is on the critical path — `feature-development.md`'s fan-out may be waiting on its verdict.
   The pre-gate dispatches `security-reviewer` alone: a go/no-go on the import, not a strike.
2. **Decide on `Verdict:`, never on `Status:`.** A review requesting changes is `Status: Done`.
   `Status: Blocked` means a missing input — supply exactly it, asking the GD when only they hold it (G6,
   B17), no strike. `Verdict: Blocked` on `Status: Done` is a security **rejection**. Route on the whole
   envelope:

   | Return | Action |
   |---|---|
   | `Approve` **and** `Clear` | The submission is clear — the only clear |
   | `Request changes`, or `Verdict: Blocked` | One combined return, step 3. Any `Needs Confirmation` beside it travels with the findings — a rejection outranks the ladder |
   | `Needs Confirmation`, no rejection beside it | The ladder (G54, B9): `tech-lead-sdk-platform` for an SDK or platform integration, else the author, then the GD; re-run the gate on the answer. Never guessed either way — nobody can name a source → a secret, `Request changes`, one strike |
   | `Verification done:` below the floor | `Request changes` and a strike — the author's to close, never QA's to absorb |
   | `code-reviewer` → `Needs-decision`, `Routed to: technical-architect` | The spec is ambiguous about "correct" — a spec problem, not a strike. On a gated-direct **E3** there is no spec: the lane escapes to `feature-intake.md` **E1** (`orchestrator.md`) |
   | `security-reviewer` → `Needs-decision`, `Routed to: cto` (git history) | Straight to `cto` — not a `research-decision.md` entry. Published history is never self-remediated by a code-writing agent |
   | A `cto` remediation outside history — rotation, a burned credential, often inside `Recommendation:` | To `cto` **alongside** the return to the author |
   | A design flaw, on any status | The GD now (G4) — never folded into CP3 |
   | `Rejected` | Mis-dispatch: re-dispatch to the right gate, no strike |
   | `Assessed: Escalate` | Its `Needs-decision` row above; not a verdict |
   | More than one destination named | Record every one; act in the stated order |
   | A gate says its mandatory skill did not resolve | It ran at reduced depth — record that with the verdict |
   | A note field the gate found unsupported | Stays with the submission, for `qa-lead` and `assurance-evaluator` |

3. **Return** — from E1 to `feature-development.md` **E3**, from E3 to the author directly: both finding sets,
   the strike count, every prior verdict, and the known non-solutions of any Continuation Debt Record. Strikes
   per `bounds.md` rule 1: one round trip is one strike whichever gate caused it; a Continuation Debt Record
   is one strike (B1). Write the strike and verdicts to the ledger's submission table — a test suite with its
   `/2` bound — or, for gated-direct, `project-state.md` → *Gated-direct counters*, before the next dispatch;
   a Continuation Debt Record goes to the ledger's *Continuation debt* at the same transition.
4. **At the bound.** **E1, B3:** `technical-architect` with the full rejection history and the code. Its
   known non-solutions go into the return brief, `Next best action:` to the owning agent, the cause on the
   ledger's `Root-cause resets` row, since a later stop must quote it; the fix re-enters
   `feature-development.md` **E3** at zero strikes (B10). A stalled Core stalls the feature, correctly. The
   next bound stops (G7). **E3:** gated-direct at B4 → `feature-intake.md` **E1** with both rejection sets
   and the code; test code at B5 → `qa-lead` as unrun coverage, never intake.
5. **Checkpoint 3 (G51)** — D3–D5 only, once per feature, only when review ran; at D1–D2 it merges into CP4,
   and the A-tier never adds one. `technical-architect` compiles from every cleared submission's
   Implementation Note and both verdicts: `Built:` in the spec's terms; `Matches spec intent:` with **every
   drift named**; `Known limitations:`, each owed in the feature root's `DEBT.md` from A3, appended by the
   submission that produced it. Approve → QA execution unlocks (`qa-pipeline.md` **E2**). Reject as drift →
   the named drift to its owner at `feature-development.md` **E3**, never CP2 (B12). The spec itself wrong →
   not a CP3 rejection: `change-request.md` (G70).
6. **The QA ask (G52)** — when every submission is clear, **not after CP3**, per G50, carrying the V-number.
   Yes → `qa-lead` plans at `qa-pipeline.md` **E1** while CP3 is with the GD; nothing the plan produces is
   invalidated by a CP3 rejection. At D1–D2 execution unlocks at **E2** directly. No → a QA debt row in
   `project-state.md`, never coverage.

## GD touchpoints

- **G45** — third-party content: the pre-gate runs whatever review answer the GD gave; the GD is told so.
- **G50** — the shape of the G52 ask.
- **G51** — CP3, step 5.
- **G52** — the QA ask, step 6.
- **G53** — rejections reach the author silently; the GD hears only G4, a `cto` remediation, or G7.
- **G54** — the `Needs Confirmation` ladder, step 2.
- **G55** — an E2 audit's findings go to the GD as a report: no author, no strike, no CP3.
- **G4** — a design flaw from either gate, at once. **G6** — a `Status: Blocked` only the GD can answer.
  **G7** — any bound below reached.

## Bounds

B1 (a Continuation Debt Record is one strike) · B3 · B4 · B5 · B9 · B10 (shared, one per submission) · B12 ·
B17 · B18 (re-offering a declined review at a later boundary).

## Exits

| Outcome | Control goes to | Written |
|---|---|---|
| A submission clear, others outstanding | Wait for the rest | Ledger: verdicts landed |
| Every submission clear | G52; then CP3 (D3–D5), or `qa-pipeline.md` **E2** on a yes (D1–D2) | Ledger; a QA debt row in `project-state.md` on a no |
| Rejection at E1 | `feature-development.md` **E3** | Ledger: strike +1, verdicts landed |
| Rejection at E3, under its bound | The author | Ledger (test code) or *Gated-direct counters* |
| B3 | `technical-architect`, then `feature-development.md` **E3** | Ledger: `Root-cause resets` 1/1, with the cause |
| B4 | `feature-intake.md` **E1** | *Gated-direct counters* |
| B5 | `qa-pipeline.md` step 4 — `qa-lead`, as unrun coverage | Ledger: the suite's row |
| A bound after the reset; a third CP3 rejection | The GD (G7) | Ledger: *Continuation debt* |
| CP3 approved | `qa-pipeline.md` **E2** | — |
| CP3 rejected as drift | `feature-development.md` **E3** | Ledger: `Rejections` CP3 +1 |
| CP3 objection is the spec | `change-request.md` (G70) | No counter moves |
| Pre-gate verdict | `feature-development.md` — go, or not adopted | — |
| E2 audit finished | The GD (G55) | — |
| Secret in history, or a rotation | `cto`, beside any return to the author | — |
| A design flaw | The GD (G4) | — |
