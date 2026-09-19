# Entry Index

> **Every addressable door into a pipeline.** Mode 2's whole vocabulary, per `orchestrator.md` — a "cluster"
> is one of these rows and never a new grouping invented beside them. Split out of `orchestrator.md` because
> it is the section that grows every time a pipeline gains a door, and it was holding that file at its cap.

**Both gate pipelines are optional and are entered only on the GD's yes**, per `optional-gates.md`; every
door into either one is still addressable in mode 2, per `standalone-runs.md`.

Each row's own file names what the entry carries. **Supply it from the feature's ledger**
(`<feature-root>/LEDGER.md`, its `## Run state` half), never from memory of an earlier run. An entry missing
its inputs returns `Blocked` — or worse, assumes silently, which is the failure every `If absent` row in
every agent file exists to make visible.

| File | Entry | Enters when |
|---|---|---|
| `feature-intake.md` | **E1** | The GD writes a feature request |
| | **E2** | `research-decision.md` settled what the Advisor loop waited on — resumes at step 3 |
| | **E3** | The Tech Spec is written or revised at step 6 — research settled, or a breakdown gap returned |
| | **E4** | `change-request.md` classified **Moderate** — reopens CP2 |
| | **E5** | `change-request.md` classified **Major** — resumes the loop at step 3 (always D4–D5 or U3, by Major's own criterion), concluding at CP1; `none` beyond the GD's words is a legitimate empty history on a feature's first CP1 |
| `research-decision.md` | **E1** | `feature-intake.md` step 5 — a capability the project lacks |
| | **E2** | `technical-architect` returned `Routed to: cto` |
| | **E3** | `advisor` returned `Needs-decision` on an option |
| | **E4** | Classification returned **U2 or U3** on a technology unknown |
| | **E5** | The GD asks for research directly, no feature attached |
| | **E6** | The GD summons a spike, no feature attached — enters at step 3 |
| `feature-development.md` | **E1** | CP2 approved — **D3–D5** |
| | **E2** | **D1–D2** — direct notes to one `agent-id` |
| | **E3** | A defect returns: from review, from QA, or reported by the GD |
| `review-pipeline.md` | **E1** | One submission from `feature-development.md` |
| | **E2** | A standalone audit of code already in the repo |
| | **E3** | A submission with an author but no feature pipeline — the gated-direct lane, or QA's test code |
| `qa-pipeline.md` | **E1** | `review-pipeline.md` step 6, **or `feature-development.md`'s end-of-work ask where review was declined**, **or a declined gate opted into later** — planning only, execution locked |
| | **E2** | CP3 approved, or the gates cleared at **D1–D2** |
| | **E3** | A defect fix came back — through review where it ran, from the author where it did not |
| | **E4** | The GD asks for QA directly and **no ledger holds the work** — shipped code, or work no pipeline built |
| `change-request.md` | **E1** | The GD changes a rule mid-flight |
| | **E2** | `qa-pipeline.md` CP4 — the spec itself should change |
| | **E3** | `research-decision.md` settled the technology half of a bundled change — resumes at step 2 |

## What every entry carries, whatever its own file adds

Four values travel with **every** re-entry into a feature's pipeline, because no agent can derive one of them
and none survives a run on its own:

| Value | Source | Read by |
|---|---|---|
| The **tier and its five axes** — A1–A5, plus D, C, U, R and X separately | The feature's ledger; assigned at `feature-intake.md` step 2 | Each pipeline reads a different axis — never collapse it to one number |
| The **attempt budget** — 2 at D1–D2, 3 at D3, 4 at D4, 5 at D5 | `execution-loop.md`, derived from D | The dispatched agent's own corrective loop |
| The **verification floor** — V1/V1/V2/V3/V4 at A1–A5 | `effort-allocation.md`, derived from A | The agent, then `code-reviewer` and `qa-lead` judging what it claimed |
| **Track state** — client, or client plus multiplayer | The ledger; never re-derived | `netcode-engineer` and `server-authoritative-engineer` block without it |

**Only U is re-read on an ordinary re-entry.** Research settling a capability or the GD locking a direction
spends uncertainty down, so lower U, recompute the tier and record both. D, C, R and X do not move because
the work itself did not change — with one exception: `change-request.md` re-reads **all five**, because new
scope genuinely can move D, and a newly touched economy path genuinely can move C.

## Re-entry does not reset a counter

An entry resumes a pipeline; it does not restart the feature. Strike counts, QA-fail counts, the Advisor⇄Critic
round number and attempts already spent all carry across the door, because the counter is the caller's and
lives in the ledger. The deliberate exceptions are stated in the files that own them: a **GD-reported
defect** enters `feature-development.md` **E3** at zero strikes, and a **change request** resets the strike
count and the attempt budget on every submission it invalidates — in both cases because the author is not
being charged for somebody else's change.

The third is narrower: a **Major** change entering **E5** also resets the **Advisor⇄Critic round count**,
because Major means the direction those rounds settled no longer holds, so they were spent on a different
question — or, on a feature reopening CP1 for the first time, there were no prior rounds and the reset is 0 to
0. `change-request.md` owns it. The **ruled-out options** still travel — they were rejected on their own
merits, and `advisor` cannot hold them across runs either way.
