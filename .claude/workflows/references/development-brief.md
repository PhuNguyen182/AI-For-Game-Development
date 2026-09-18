# The Per-Agent Brief — `feature-development.md` step 0

> **Everything a dispatch must carry, and the handoff matrix of which returned field feeds which brief.**
> Split out of `feature-development.md` under the promotion rule in `client/feature-documentation.md`: it is
> a lookup consulted once per dispatch, not part of the sequence the pipeline reads top to bottom.

An agent sees only its brief. Every row below is keyed to what actually happens when the pipeline omits it —
usually a `Blocked`, occasionally something worse, which is a silent assumption nobody stated.

**Nine** things every brief carries. Two of the nine were added after a live run blocked on them, and are
marked as such.

| Attach | If the pipeline omits it |
|---|---|
| That agent's task section, **plus `Module boundaries:` and `Client-server contract:`**, plus the tier and its axes | Four agents return `Blocked` on a missing task section. The two cross-cutting fields are a separate matter: `unity-engineer` is told to *"never reimplement a game rule here"* and `ui-ux-programmer` to *"never compute a game rule in a UI script"*, and no agent can respect a boundary it was never shown. Only the *other* agents' task breakdowns are withheld |
| **The feature root** — the path the code lives under, and where its `LEDGER.md` sits | Every agent here is stateless and sees only this prompt, so a root nobody names is a root it has to find. `feature-intake.md` step 2 makes `technical-architect` name it and opens the ledger there, and until this row existed that name went no further. **Found live**: the first dispatch of a real run returned `Blocked` with *"the Unity project itself"* as its first missing input, having searched the tree to prove the absence |
| **The netcode foundation** — transport, NGO, NfE or custom — on the backend track only | `netcode-engineer` confirms it from the project and, *"if unset, return `Needs-decision` with `Routed to: cto`"*. That is a whole `research-decision.md` round spent on a value the caller already holds in the ledger. Ask the GD once if it genuinely is unset; never let the absence of a row buy a strategic-decision dispatch |
| **The attempt budget** — 2 at D1–D2, 3 at D3, 4 at D4, 5 at D5 | The agent has no bound on its own corrective cycles. `execution-loop.md` is explicit that the first execution is Attempt 1 and the budget is a ceiling, never a target — an agent that does not know the ceiling either stops at the first inadequate result or loops on cosmetic variation |
| **The verification floor** — V1 at A1–A2, V2 at A3, V3 at A4, V4 at A5 | The agent verifies to its own taste and reports it as "verified". A floor is what makes `Verification done:` in the Implementation Note mean the same thing to the reviewer as to the author |
| Track state, stated explicitly on or off | `netcode-engineer` and `server-authoritative-engineer` return `Blocked`; neither ever assumes the track is on |
| The per-platform performance budget | `unity-engineer` and `technical-artist` proceed against a guessed budget and only state the assumption |
| **The track standards that agent must read**, by path — `.claude/standards/client/*` for every client-track agent, per `rules/standards-index.md` | They are no longer auto-loaded into every dispatch: 756 lines of C# style and QA evidence standards were being paid for by the router, `producer` and `researcher`, none of which writes code. Each agent's own required-reading table is now the loading mechanism, and **naming the paths in the brief is what triggers it**. Omit them and the agent may write code that meets no standard while believing it met all of them |
| The strike count, prior findings, **and attempts already spent**, on an **E3** re-entry | Every implementing agent's Escalate criterion is "already came back rejected twice". It cannot count its own retries, so silence reads as a first attempt — and an agent handed a half-spent budget as if it were full will fragment one correction across cycles it does not have |

Plus what an earlier agent already produced for it. Agents cannot see each other's returns, so a field this
pipeline forgets to forward is a field that does not exist:

| Producer → field | Goes to | Why that agent needs it |
|---|---|---|
| `csharp-engineer` → `Public contract:` | `unity-engineer`, `ui-ux-programmer`, `netcode-engineer`, `server-authoritative-engineer` | all four return `Blocked` without the Core types |
| `csharp-engineer` → `Determinism:` | `netcode-engineer`, `server-authoritative-engineer` | netcode Escalates when the Core "is not deterministic enough to reconcile"; server authority assumes the strictest tolerance that determinism supports |
| `csharp-engineer` → `Assumptions and known limitations:` | every downstream agent | they build on the assumption too, and have no other way to see it |
| `technical-artist` → `Authored:` and `Pipeline:` | `unity-engineer` | it integrates that effect into the scene or prefab |
| `unity-engineer` → `Core calls used:` and `Changed:` | `ui-ux-programmer` | when the UI binds to state the integration exposes rather than to Core directly |
| `netcode-engineer` → `Message contract:` | `server-authoritative-engineer` | returns `Blocked` without it |
| `csharp-engineer` → `Assumptions and known limitations:` | **the step 1 gate ask itself** | `optional-gates.md` requires the cost of skipping to be *named concretely*. The Core's own limitations are the most concrete statement of it there will ever be — a live run returned *"the Core was not compiled; no .NET SDK was available"*, which is exactly what four agents would then be building on |

## What the brief asks the agent to state back

Three things `.claude/rules/implementation-note.md` needs have **no field in the envelope that produces
them**, so the brief asks for them in the return rather than the assembler inventing a value. Each is a
sentence in the dispatch, not a new envelope:

| Ask for | Because |
|---|---|
| **Attempts used, out of the budget** | No implementing envelope carries it, and `assurance-evaluator` absent it *assumes Attempt 1* — scoring an iterated submission as a first pass. In one live run of this pipeline, one agent volunteered it and another did not, which is what an unrequired field looks like |
| **What verification actually ran — and, where a check was impossible, that it was impossible and why** | `csharp-engineer`, `server-authoritative-engineer` and `tech-lead-sdk-platform` have no verification field at all. Live, the Core author filed its V3 account under `Assumptions and known limitations:` instead, where the Note reads it as a limitation rather than as evidence. `effort-allocation.md` requires unavailable to be reported as unavailable, and an unreachable floor is a stated limitation for the GD, never a silent pass |
| **Assumptions and known limitations, from `tech-lead-sdk-platform` specifically** | It is the one implementing agent whose envelope has no such field, and `Known limitations:` is what carries into `DEBT.md` from **A3**. Live, it wrote them in prose outside the envelope — which works only because it chose to |

`references/development-exit-and-custody.md` is where those answers land.
