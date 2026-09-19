# The Optional Gates — review and QA are offered, never assumed

> **Read at the moment implementation work is done and a gate would otherwise be dispatched.** `review-pipeline.md`
> and `qa-pipeline.md` are two **separate, optional** processes. Neither runs on its own initiative, in any
> lane or mode. The orchestrator asks the GD, states the cost of skipping, and dispatches only what they
> authorise.

This is the GD's standing direction, and it is consistent with the rule the whole layer already runs on:
*never enforce by blocking — state the cost, then do what the GD asked.* What this file adds is the shape of
the ask, and the one thing that is not optional: **a declined gate is recorded, never silent.**

## Who asks, and where — the two are different questions

Three files each describe an ask, and reading them apart it looks as though three parties own it. They do
not, and the split is the same one the rest of the layer uses:

| Owned by | What |
|---|---|
| **This file** | The **shape** of every ask — the four things it carries, the recommendation, the bound of one offer per boundary, and the record that follows either answer. It is the single home; no pipeline restates it |
| **The pipeline that reaches the boundary** | **Where** each ask fires. `feature-development.md` step 1 asks about the Core contract, because that is the moment four agents are about to build against it. `review-pipeline.md` step 6 asks about QA, because that is the moment both verdicts are in. `qa-pipeline.md` step 3b asks about reviewing a test suite. Neither is a second copy of the rule — each is a location |
| **`orchestrator.md`** | Every ask that belongs to **no** pipeline: a mode-3 dispatch that wrote source, a gated-direct submission, a debt row re-offered at a later boundary |

"The orchestrator asks the GD" above is shorthand for the third row, and it is the one that has no pipeline
to hold it. It has never meant that a pipeline mid-run routes its own boundary back through the router. **A
pipeline that consumes this rule never restates it as "the orchestrator asks"** — that wording was corrected
here and then survived in two files that quote it, which is why the location table above names each asker
rather than leaving it to be inferred.

### The one ask whose location moves

**QA is asked at `review-pipeline.md` step 6 — unless review was declined, and then that step never runs.**
The ask does not disappear with the gate that would have made it; it moves to the boundary that *did* get
reached, which is `feature-development.md`'s end-of-work ask, where it fires alongside the review offer
rather than after it. The rule is the same one in the table: **whichever party reaches the boundary asks**,
and a declined gate removes a location without removing the question. Both gates declined still leaves two
recorded debt rows and a feature that closes at **CP4**.

## The two decision points

```text
implementation returns
        ↓
   ASK — run review?  ──no──→  record review debt  ──┐
        │yes                                         │
   review-pipeline.md (CP3 lives here)               │
        ↓                                            ↓
   ASK — run QA?  ──no──→  record QA debt  ──→  CP4 — the GD closes it
        │yes                                         ↑
   qa-pipeline.md  ──────────────────────────────┘
```

**They are independent.** Review may run without QA, QA may run without review, and either may run later
against work that already shipped. QA is not gated on review having happened — it is gated on the GD saying
so. Where QA runs without review, `qa-lead` and `assurance-evaluator` are told the review verdicts do not
exist rather than left to assume they do; both consume verdicts as given, and *given* now includes *absent*.

## What the ask must carry

An ask that only says "run review?" pushes the judgement onto the GD without giving them what it takes to
make it. Every ask carries four things, in one message, so the decision costs one turn:

| Carry | Why |
|---|---|
| **What was built**, and which paths changed | The GD is deciding about a specific artifact, not about a policy |
| **The tier and the axes that set it** | A5 from C4 and A5 from D5 are different risks and deserve different answers |
| **The cost of running it** — the agent calls, and what still waits on it | Two calls in parallel for review; the QA cost depends on the coverage assignment, which `qa-lead` has not written yet |
| **The cost of skipping it**, named concretely | Not "quality may suffer" — *"nothing has checked that this damage formula stays deterministic, which is what lets the server and the client agree"* |

**Recommend, then defer.** State which answer the tier points to and why, in one line, then take whatever the
GD says. The recommendation is information; it is never a soft block, and it is never repeated after they
answer.

| The work | What to recommend, and say why |
|---|---|
| **C4** — a credential, real money, store submission, player PII, published history | Run the security gate. `security.md` carries no tier exemption and no lane exemption; this is the one place to say plainly that skipping it is the GD overriding a zero-tolerance rule, not tuning a process |
| **C3, R2+, X2+** | Run both. Consequence is what the gates buy evidence against |
| `Game.Core.*`, or multiplayer-relevant | Run review at least. A determinism or authority error is invisible until it diverges, which is exactly what reading the code catches and playing the game does not |
| A1/A2, judgeable by looking | Offer, expect no, and do not argue. The GD can see whether it is right |

## What is never optional

- **The ask itself.** Skipping a gate silently, or deciding on the GD's behalf that it was not worth offering,
  is the one failure this file exists to prevent.
- **Recording the decline.** Per invariant **I2**, review debt attaches to the artifact, not to the run. A
  declined gate writes a row in `<state-root>/project-state.md` — path, who wrote it, when, which gate was
  declined, and that the GD declined it. It blocks nothing and settles in batch whenever they opt in.
- **The verification floor.** V1–V4 is the *author's* obligation from `effort-allocation.md`, discharged
  inside the dispatch. A declined gate means nobody independently checked the claim — it never means the
  claim was not owed. `Verification done:` is still written, and still measured against the floor by whoever
  reads it next.
- **The rule and standard baseline.** The gates detect; the rules prevent. Declining detection does not relax
  `security.md`, `.claude/standards/client/coding-principles.md`, or anything else an agent follows while
  writing — see `rules/standards-index.md` for which agent reads which.
- **Invariant I5.** A design flaw reaches the GD immediately, from any agent, gate or no gate.

## What disappears when a gate is declined, and what takes its place

| Declined | What is lost | What still happens |
|---|---|---|
| **Review** | Both verdicts, **CP3**, the three-strike ladder, and the Core-contract hold in `feature-development.md` step 1 — the fan-out proceeds immediately against an unreviewed public contract | The Implementation Note is still assembled and still handed to the GD. Review debt is recorded |
| **QA** | The coverage assignment, the exit criteria, the device lane, and the assurance gate at A3+ | **CP4 still fires** — see below. `producer` compiles from whatever exists. QA debt is recorded |
| **Both** | Every independent check on the work | The feature still closes at **CP4**, on the GD's own acceptance, with both debts recorded and the accepted gaps written into the feature root's `DEBT.md` from A3 upward, per invariant **I6** |

### CP4 always fires

**CP4 is the GD closing the feature, not QA signing it off.** Those are two different decisions and only one
of them is optional. A feature whose gates were both declined does not trail off unclosed: it reaches CP4
with an Implementation Note, whatever `producer` could compile, and both debt rows stated — and the GD closes
it or does not.

`qa-pipeline.md` owns CP4's mechanics and is where it runs when QA ran. When QA did not, the same gate runs
from here with the same three outcomes, and `producer` is dispatched with **the Implementation Notes** in
place of QA reports — without them it returns `Blocked`, because it is barred from reconstructing status by
inference. If there is not even a note to give it, skip `producer` and put the Implementation Notes to the GD
directly; a one-submission feature does not need a report *about* one document.

**This is not process bought back.** CP4 costs no agent call on its own — it is the GD answering a question
they were going to answer anyway. What it buys is that "done" is something they said, rather than something
the layer stopped mentioning.

### The one loss worth naming out loud at A4 and above

Declining QA at **A4 or A5** also declines `assurance-evaluator`, and that gate is not coverage — it is the
only thing in the layer that checks **whether a verification the submission claimed actually happened**.

`effort-allocation.md` puts a false verification claim beyond any GD waiver: it is not a quality score to
average away, it is a report that is untrue. Declining the gate does not breach that rule — nobody has
claimed anything falsely by choosing not to check. But it does mean the claim goes unchecked, and at A4+ the
ask says so **in those words**, because it is the one consequence a GD reading "skip QA" would not predict.

Recorded as an accepted gap either way, per **I6**. Never as a reason to refuse the GD's answer.

**A feature that closed with a declined gate is never reported as one that passed it.** That distinction is
the whole reason the debt row exists — `verification-standards.md` calls an unrun check reported as coverage
the failure that makes a QA suite worse than none, and the same holds one level up.

## Opting in later

Debt settles in batch. A declined gate is re-offered at a later natural boundary — the next feature touching
the same root, a release, a defect traced to the ungated code, or whenever the GD asks. **Once per boundary,
and never twice in one run**, per `loop-termination.md`: re-asking because the recommendation was not taken
is nagging, and nagging trains the GD to stop reading the ask. The work enters the gate's own standalone
door:

| Opting in later | Enters at |
|---|---|
| Review, on code already in the repo | `review-pipeline.md` **E2** — the audit door. No author, no strike, no CP3; findings are a report |
| Review, on a submission still identifiable with its brief and author | `review-pipeline.md` **E1** or **E3**, with the strike count starting at zero |
| QA, on a feature already closed | `qa-pipeline.md` **E1**, with the spec and tier from the ledger. If the ledger is closed, reopen it rather than opening a second slug. **Not E4**, which that pipeline declares for work no ledger holds: taking it here would discard the tier, the floor and every counter the feature already spent |

Clearing a debt row requires the gate to have actually returned. Marking one settled because the code looks
fine is the fabricated verification `effort-allocation.md` puts beyond any waiver.
