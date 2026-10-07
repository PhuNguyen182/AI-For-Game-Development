# The Optional Gates — review and QA are offered, never assumed

`review-pipeline.md` and `qa-pipeline.md` are separate, optional processes. Neither runs on its own initiative,
in any lane or mode: whoever reaches the boundary asks the GD, states the cost of skipping, and dispatches only
what was authorised. This file is the single home of **the shape of every ask (G50)**; each pipeline only says
**where** its ask fires.

| Where an ask fires | Owner |
|---|---|
| The Core contract, before the fan-out (G40); end of implementation (G42); rework after a change request (G74) | `feature-development.md`, `change-request.md` |
| QA, once both review gates clear (G52) | `review-pipeline.md` |
| Test code, once the suite is written (G62); a build for device coverage (G61) | `qa-pipeline.md` |
| A direct or mode-3 dispatch that wrote source (G13); a gated-direct submission (G14); a debt row at a later boundary | `orchestrator.md` |

**When review is declined, the QA question moves, it does not vanish**: it fires at the end-of-work ask,
alongside the review offer. Review and QA are independent — either may run without the other, or later. Where
QA runs without review, `qa-lead` and `assurance-evaluator` are told the review verdicts are **absent**, never
left to assume them.

## What every ask carries — one message, one turn

1. **What was built**, and which paths changed.
2. **The tier and the axes that set it** — A5 from C4 and A5 from D5 are different risks.
3. **The cost of running it** — agent calls, and what waits on it.
4. **The cost of skipping it, named concretely** — not "quality may suffer" but *"nothing has checked that this
   damage formula stays deterministic, which is what lets server and client agree"*.

**Recommend, then defer.** One line on which answer the tier points to and why, then take whatever the GD
says. Never a soft block, never repeated after the answer.

**Asked as multiple choice (G19).** One `AskUserQuestion` call: the four carries go in the question and the
option descriptions, the recommended option first. When review and QA are offered at the same boundary, one
**multi-select** question ("Run which gates?" — review, QA) — never two prose questions.

| The work | Recommend |
|---|---|
| **C4** — a credential, real money, store submission, PII, published history | The security gate at minimum — and say plainly that skipping it overrides a zero-tolerance rule (`security.md`), not a process setting |
| **C3, R2+, X2+** | Both gates |
| `Game.Core.*`, or multiplayer-relevant | Review at least — a determinism or authority error is invisible until it diverges |
| A1/A2, judgeable by looking | Offer, expect no, do not argue |

**At A4 and above, declining QA also declines `assurance-evaluator`** — the only check on whether a claimed
verification actually happened. The ask says so **in those words**.

## What is never optional

- **The ask itself.** Skipping a gate silently, or deciding it was not worth offering, is the failure this
  file exists to prevent.
- **Recording the answer.** A declined gate writes a row in `<state-root>/project-state.md` — path, author,
  when, which gate, `declined` by the GD (I2). It blocks nothing and settles whenever the GD opts in.
- **The verification floor and the Implementation Note.** A declined gate means nobody independently checked
  the claim — never that the claim was not owed.
- **The rule baseline** — `security.md`, the track standards. Declining detection relaxes no prevention.
- **The supply-chain pre-gate (G45)** — third-party content is scanned before it lands, whatever the answer.
- **I5** — a design flaw reaches the GD immediately, gate or no gate.

## What a decline costs

| Declined | Lost | Still happens |
|---|---|---|
| Review | Both verdicts, CP3, the strike ladder, the hold on the Core contract | The note is assembled and handed to the GD; review debt recorded |
| QA | Coverage, exit criteria, the device lane, the assurance gate at A3+ | **CP4 still fires (G60)** — the status report is compiled from the Implementation Notes; QA debt recorded |
| Both | Every independent check | The feature closes at CP4 on the GD's own acceptance, both debts stated, the declined gates written to `DEBT.md` from A3 as accepted gaps (I6) |

A feature closed with a declined gate is **never reported as having passed it**.

## Opting in later

Re-offered once per new boundary (B18) — never twice in a run. Clearing a debt row requires the gate to have
actually returned; marking it settled because the code looks fine is fabricated verification.

| Opting in later | Enters at |
|---|---|
| Review, on code already in the repo | `review-pipeline.md` **E2** — a report, no author, no strike, no CP3 |
| Review, on a submission still identifiable with its brief and author | `review-pipeline.md` **E1** or **E3**, strikes from zero |
| QA, on a feature with a ledger (even a closed one — reopen it) | `qa-pipeline.md` **E1**, never **E4**, which would discard the tier, floor and counters |
