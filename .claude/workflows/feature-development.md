# Feature Development

From an approved Tech Spec, or direct notes, to code standing at the gate offer. Intake is
`feature-intake.md`'s; review and QA are `review-pipeline.md`'s and `qa-pipeline.md`'s, and both are optional —
this pipeline ends by asking (`references/optional-gates.md`), never by dispatching a gate itself. It spends two
budgets it does not set: the attempt budget from **D** (B1) and the verification floor from **A**.

## Entries

| Door | Comes from | Carries |
|---|---|---|
| **E1** | `feature-intake.md` CP2 approved — D3–D5 | The Tech Spec, its per-`agent-id` task breakdown, the tier and its axes |
| **E2** | `feature-intake.md` step 2 at D1–D2; `orchestrator.md` step 0 row 12; or the GD naming the work (G18) | Direct notes addressed to one `agent-id`, and the tier |
| **E3** | Rework: a defect from `review-pipeline.md`, `qa-pipeline.md` or the GD; a gated-direct rejection (within B4); a root-cause reset (B10); `change-request.md`'s rework list | The findings or rework list — a QA or GD defect **by bug ID**, with its `BUGS.md` record — the original brief, the strike count, attempts already spent |

Every door also carries the four values in `references/dispatch-brief.md`, read from the ledger. A GD-reported
defect enters **E3** at zero strikes; if the spec was right and the GD now wants something else, it is a change
request instead (G47).

## May dispatch

| Agent | Returns / owns here |
|---|---|
| `csharp-engineer` | `Game.Core.*` — the rules and the `Public contract:` every other layer builds on; the Core root's documents |
| `technical-artist` | Shaders, VFX, visual compute — authors the effect, never integrates it |
| `unity-engineer` | Scenes, prefabs, physics, rendering, assets, input, the routine optimisation pass |
| `ui-ux-programmer` | Screens, bound to state they read and never own |
| `tech-lead-sdk-platform` | Every third-party SDK and store integration — not an escalation target, so it starts from the spec |
| `netcode-engineer` | The sync protocol and its `Message contract:` — backend track only |
| `server-authoritative-engineer` | Validation wrapping the Core — backend track only |
| `tech-lead-csharp-unity`, `tech-lead-performance` | Escalation only — `Fix:`, `Root cause:`, `Pattern decision:` |
| `security-reviewer` | The supply-chain pre-gate (G45) only, run as `review-pipeline.md`'s pre-gate — a go/no-go on an import, not a strike |

## Hard ordering

1. **Core first.** When the breakdown names a Core task, `csharp-engineer` runs before anything that consumes its
   contract; four agents return `Blocked` without it. With no Core task, the brief names the existing Core or
   integration API instead; with neither, hand back to `feature-intake.md` **E3** — no downstream agent invents
   a game rule.
2. **If review was authorised at G40, the fan-out waits on the Core's verdict — and on no other.**
3. **The client fan-out is serial, one agent at a time** (I3 — one Editor, and every `.cs` write's domain reload
   ends another agent's Play Mode session): `technical-artist` → `unity-engineer` → `ui-ux-programmer`, the
   spec's own dependencies overriding, rows the breakdown omits skipped. `tech-lead-sdk-platform` takes any slot.
   A second Editor instance exists only on an explicit GD request (G16), never arranged by this pipeline.
4. **Protocol before authority**: `netcode-engineer` → `server-authoritative-engineer`, which blocks without the
   message contract. The backend chain depends on the Core alone, so it — and review of any piece already
   submitted — may run concurrently with the fan-out; none of them holds Editor tools.
5. **Third-party content clears the supply-chain pre-gate before it lands** (G45), before the integration is
   written.
6. **Feature-root documents follow every implementation task in their root** — except `LEDGER.md` decisions and
   `DEBT.md`, appended in the submission that produced them, never reconstructed at the end — except the accepted gaps and GD-ruled bugs the orchestrator appends at closure. `BUGS.md` is not a feature document: only the orchestrator writes it.

## Steps

1. **Brief every dispatch** per `references/dispatch-brief.md` — the four values, the feature root, the track
   standards by path, the handoff fields earlier agents produced, and the three things to state back (attempts
   used and, past the first, what improved; what verification ran and what was impossible, and why;
   `tech-lead-sdk-platform`'s assumptions and limitations). Claim the Editor lock before dispatching any holder
   of Editor tools; release it on return.
2. **E2 runs one agent and stops** — no fan-out, no ordering. A high A buys a higher floor and a more careful
   target check, never a second agent. If the notes name no rule the agent needs, hand back as in ordering 1.
3. **Core** (E1). On return: the G40 ask, carrying the Core's `Assumptions and known limitations:` as the cost of
   skipping; at D4–D5 also the G41 notice. Declined → review debt recorded, fan-out proceeds immediately.
4. **Client fan-out**, per ordering 3. Each return is a submission the moment it lands.
5. **Backend track**, only when the brief states it **on** — never "probably off". The netcode foundation comes
   from the ledger; genuinely unset → G44, once.
6. **Feature-root documents**, keyed to **A**, never D, per `.claude/standards/client/feature-documentation.md`.
   A1–A2 owes and writes nothing. A3: `LEDGER.md` `## Decisions`, `DEBT.md`, `NOTES.md`, each on its trigger.
   A4+: the full docset on its triggers. The floor is necessary, never sufficient — no empty document to look
   complete. `LEDGER.md` is already on disk; append to it, never create one. One owner per root, dispatched
   with every envelope returned for that root; each root's `README.md` links the other:

   | Root | Owner |
   |---|---|
   | `Game.Core.*` | `csharp-engineer` |
   | Unity `Assets/` | `unity-engineer` if the breakdown names it, else `ui-ux-programmer`, else `technical-artist` |

7. **Submit and ask.** One submission per agent return, never one per feature; the documents are simply the
   last. Each carries the code or diff, its spec section or notes, its author, the tier and V-number, and the
   Implementation Note assembled per `references/dispatch-brief.md`. Submissions go to whichever gates the GD
   authorised. When implementation is complete, the G42 ask, read off the ledger's `Gates:` row: QA where
   review was declined, review and QA where G40 never fired; where review is running, its own pipeline asks QA.
   Every answer is written to `Gates:` (and a decline to `project-state.md`). A change-request rework list ends at
   `change-request.md`'s ask (G74) instead. On **E3**, a fix returns to the gates that rejected it; an
   unasked-for gate is re-offered only at a new boundary (B18).

**Every return** — route on the whole envelope, never on `Status:` alone:

| Return | Do |
|---|---|
| A design flaw, any status, any step | To the GD now (G4), then resume |
| `Config required:` / `Risks flagged:` / `Store policy addressed:`, any status | To the GD (G5), as well as whatever the status asks |
| `Blocked` | Exactly the input named — the GD's (G6) or `technical-architect`'s when the spec has the gap; B17 |
| More than one destination | Record all; act in the order the return states |
| `Rejected`, `Routed to: <peer>` | Misassigned — re-dispatch to that peer, never argue it back |
| `Needs-decision`, `Routed to:` a tech lead | The escalation lane (G46): `tech-lead-performance` refuses while obvious fixes are open, `tech-lead-csharp-unity` names a misroute; a second refusal of the same problem is B16. Resume at the step it left |
| A lead's `Fix:` | A submission authored by the lead, carrying the escalating agent's brief as its spec (I10) — owes the gate offer like any other |
| `Pattern decision:` with `Scope of pattern: project-wide` | `LEDGER.md` `## Decisions` (with the `Root cause:` beside it) **and** `project-state.md` "Project-wide patterns" (the only home at A1–A2), before the step it left resumes |
| `server-authoritative-engineer` → `Blocked`, `Routed to: csharp-engineer` | A rule missing from the Core: back to step 3, then resume |
| `netcode-engineer` → `Needs-decision`, `Routed to: cto` | Ledger first, then G44. Only a genuinely undecided foundation goes to `research-decision.md` **E2**, with a candidate set; keep the `Message contract:` it returned |
| The classification is wrong | Recompute; update the ledger's `Tier:` and append to `Tier history:`; re-derive budget and floor; G43. Not a change request |
| A measured number (`Performance:`, `Cost:`, `Before / After:`) | The ledger's `Baseline:` |
| `Rejection behaviour:`, `Tick and cadence:` | The submission and the QA plan |
| A Continuation Debt Record | Into the ledger whole; one strike; re-dispatch only with its `Next best action:` — never the same brief |

Strikes are counted by `review-pipeline.md` and arrive through **E3**: strike 2 fires the agent's own Escalate
criterion toward a tech lead, strike 3 is B3. Self-verification is evidence for a gate, never a substitute.

## GD touchpoints

- **G40** — the Core contract has returned; the feature's one review ask.
- **G41** — D4–D5 Core contract notice; nothing waits.
- **G42** — implementation complete; the end-of-work ask.
- **G43** — the classification moved; one line.
- **G44** — backend on, netcode foundation unset; asked once.
- **G45** — third-party content about to land; the pre-gate runs whatever the review answer.
- **G46** — the escalation lane stays silent to the GD.
- **G47** — a GD-reported defect opens a bug (`Opened by: gd`) and enters **E3** at zero strikes.
- Also fires G4 (design flaw), G5 (config/risk fields), G6 (`Blocked`), G7 (a bound reached), G16 (a second
  Editor instance).

## Bounds

B1 (attempt budget per dispatch) · B3 (strikes, forwarded via **E3**) · B4 and B10 (rework that enters **E3**) ·
B16 (escalation round trips) · B17 (identical `Blocked`) · B18 (gate re-offers).

## Exits

| Outcome | Control goes to | Written |
|---|---|---|
| A submission, review authorised | `review-pipeline.md` **E1** | Submission row in the ledger |
| A submission, review declined | `qa-pipeline.md` **E1** on a QA yes; else CP4 (G60) on the Implementation Notes | `declined` row in `project-state.md` (I2) |
| A defect fix, review authorised | `review-pipeline.md` **E1**, then `qa-pipeline.md` **E3** | Strikes, attempts; each bug the agent names as fixed goes `Fixed` only once review clears it |
| A defect fix, review declined | `qa-pipeline.md` **E3** where QA is authorised; otherwise the verification put to the GD per G50, a no leaving the bugs `Fixed` for CP4 | Strikes, attempts; each bug the agent names as fixed → `Fixed` in `bug-log.md` and `BUGS.md` |
| No Core task, no named API; or a lead → `Routed to: technical-architect` | `feature-intake.md` **E3** — step 6 at D3–D5, the direct-notes hand-off at D1–D2 | The gap named |
| A lead or `netcode-engineer` → `Routed to: cto` | `research-decision.md` **E2** with a candidate set; it resumes the step it left | — |
| A bound reached | The GD (G7) | Continuation debt in the ledger |
| A design flaw | The GD (G4) | — |
