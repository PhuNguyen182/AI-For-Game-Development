# Workflow Build Checklist

> **What this tracks:** the progress of authoring the workflow layer itself — which part of which pipeline is
> written, and which the GD has reviewed and approved. It is not a per-feature runtime checklist.

**This file is exempt from the 200-line cap** that governs every other document under `.claude/`. It is an
append-only record — one row per authored part, one row per debt — so it grows by design and a cap would
force it to start forgetting. Never compress it to fit a line count; add the row.

Status: `⬜ Not started` · `🔄 In progress` · `✅ Written` · `⛔ Blocked on GD`.
The **GD** column is a separate axis: a part can be written but not yet approved.

| Pipeline | File | State |
|---|---|---|
| 1. Feature intake | `feature-intake.md` | ✅ Written · GD approved |
| 2. Research & decision | `research-decision.md` | ✅ Written · GD approved |
| 3. Feature development | `feature-development.md` | ✅ Written · GD approved |
| 4. Review | `review-pipeline.md` | ✅ Written · GD approved |
| 5. QA | `qa-pipeline.md` | ✅ Written · GD approved |
| — Change request | `change-request.md` | ✅ Written · GD approved |
| 7. Orchestrator | `orchestrator.md` + `references/` + `orchestration.md` + `state/` | ✅ Written · GD approved |
| 12. State out of the framework | per-feature `LEDGER.md`, `<state-root>/`, `state/templates/` | ✅ Written · ⬜ GD review |
| 8. Classification migration | every file above, retiring Simple/Medium/Complex | ✅ Written · ⬜ GD review |

## 1. Feature intake — `feature-intake.md`

| # | Part | Agents | Status | GD |
|---|---|---|---|---|
| 1.1 | Forward the request verbatim + attach track state | — (pipeline) | ✅ | ✔ |
| 1.2 | Classification → A1–A5 with its five axes, unconditional and first (was Simple/Medium/Complex — see §8) | `technical-architect` | ✅ | ⬜ |
| 1.3 | Advisor⇄Critic loop, GD-in-the-middle, hard cap of 3 rounds | `advisor`, `critic` | ✅ | ✔ |
| 1.4 | **CHECKPOINT 1** — direction locked, accepted risks recorded | gd | ✅ | ✔ |
| 1.5 | Research branch — any tier, with the name-the-coverage skip test | → pipeline 2 | ✅ | ✔ |
| 1.6 | Tech Spec | `technical-architect` | ✅ | ✔ |
| 1.7 | **CHECKPOINT 2** — Tech Spec approved; reject returns to 1.6, not 1.4 | gd | ✅ | ✔ |
| 1.8 | Routing table + `Blocked` handling + non-convergence stop | — (pipeline) | ✅ | ✔ |
| 1.9 | Block diagram | — | ✅ | ✔ |
| 1.10 | `Open design question:` added to the architect's output envelope | `technical-architect` | ✅ | ✔ |

## 2. Research & decision — `research-decision.md`

| # | Part | Agents | Status | GD |
|---|---|---|---|---|
| 2.1 | Six entry points; E2–E4 never jump straight to `cto` | — (pipeline) | ✅ | ✔ |
| 2.2 | Step 0 depth check — Direct / Considered / Escalate lanes | — (pipeline) | ✅ | ✔ |
| 2.3 | The lane sets the brief; `Assessed:` overrides upward only | — (pipeline) | ✅ | ✔ |
| 2.4 | Tiered source sweep → **Research Report**, sourced and dated | `researcher` | ✅ | ✔ |
| 2.5 | Spike gate — the GD authorises, the pipeline never auto-dispatches | gd | ✅ | ✔ |
| 2.6 | Spike and measurement → **Feasibility Report** | `rd-engineer` | ✅ | ✔ |
| 2.7 | Strategic, hard-to-reverse call → **Technical Decision** | `cto` | ✅ | ✔ |
| 2.8 | One measure-and-confirm cycle, then `Needs-decision: gd` | `cto`, `rd-engineer` | ✅ | ✔ |
| 2.9 | Exit: a branch rides CP1/CP2, standalone gets its own GD gate | gd | ✅ | ✔ |
| 2.10 | Hand-back into `feature-intake.md` at step 6 | — (pipeline) | ✅ | ✔ |
| 2.11 | Boundary: `advisor` = design precedent vs `researcher` = technology | — | ✅ | ✔ |
| 2.12 | Block diagram | — | ✅ | ✔ |

## 3. Feature development — `feature-development.md`

| # | Part | Agents | Status | GD |
|---|---|---|---|---|
| 3.1 | Three entry points; **D1–D2** runs one agent and stops | — (pipeline) | ✅ | ✔ |
| 3.2 | Step 0 — the per-agent brief, each row keyed to a `Blocked` | — (pipeline) | ✅ | ✔ |
| 3.3 | Step 0 — the handoff matrix: which returned field feeds which brief | — (pipeline) | ✅ | ✔ |
| 3.4 | Shared Core first, forced by four agents' `Blocked` conditions | `csharp-engineer` | ✅ | ✔ |
| 3.5 | The fan-out waits on the Core submission's review verdict, and only that | `code-reviewer` | ✅ | ✔ |
| 3.6 | **D4–D5** — the Core contract reaches the GD as a notice, non-blocking | gd | ✅ | ✔ |
| 3.7 | Client fan-out — serial; **settled**, with the three escapes tested and rejected | `technical-artist`, `unity-engineer`, `ui-ux-programmer`, `tech-lead-sdk-platform` | ✅ | ✔ |
| 3.8 | Backend track — protocol before authority; depends on step 1 only | `netcode-engineer`, `server-authoritative-engineer` | ✅ | ✔ |
| 3.9 | Escalation lane, never a first dispatch; the SDK lead is exempt | `tech-lead-csharp-unity`, `tech-lead-performance` | ✅ | ✔ |
| 3.10 | Feature-root documents at the **A4** floor (`LEDGER.md`/`DEBT.md` at **A3**) — final dispatch, one owner per root | `csharp-engineer`, `unity-engineer` | ✅ | ✔ |
| 3.11 | **One submission per agent return**, not one bundle per feature | — (pipeline) | ✅ | ✔ |
| 3.12 | Implementation Note assembled by the pipeline, with its one gap stated | — (rule) | ✅ | ✔ |
| 3.13 | Routing table, `Blocked` handling, a `Done` that still needs the GD, strike ladder | — (pipeline) | ✅ | ✔ |
| 3.14 | Block diagram | — | ✅ | ✔ |

## 4. Review — `review-pipeline.md`

| # | Part | Agents | Status | GD |
|---|---|---|---|---|
| 4.1 | One submission per entry; a feature produces several | — (pipeline) | ✅ | ✔ |
| 4.2 | Two gates in parallel, neither waiting on the other | `code-reviewer`, `security-reviewer` | ✅ | ✔ |
| 4.3 | Read `Verdict:`, never `Status:` — `Request changes` returns `Done` | — (pipeline) | ✅ | ✔ |
| 4.4 | Wait for both verdicts, act once — one dispatch back, one strike | — (pipeline) | ✅ | ✔ |
| 4.5 | Reject returns to the author at `feature-development.md` **E3** — silent to the GD | — (pipeline) | ✅ | ✔ |
| 4.6 | Three strikes → root cause with the full rejection history, never just the count | `technical-architect` | ✅ | ✔ |
| 4.7 | The `Needs Confirmation` ladder — an input to supply, not a verdict to escalate | `security-reviewer`, `tech-lead-sdk-platform`, gd | ✅ | ✔ |
| 4.8 | **CHECKPOINT 3** — once per feature, when every submission is clear | `technical-architect`, gd | ✅ | ✔ |
| 4.9 | A CP3 rejection returns the named drift to E3, not to CP2 | — (pipeline) | ✅ | ✔ |
| 4.10 | CP3 gates QA **execution**; `qa-lead`'s plan runs as soon as the gates clear | `qa-lead` | ✅ | ✔ |
| 4.11 | Routing table, incl. the `cto` git-history route that bypasses pipeline 2 | — (pipeline) | ✅ | ✔ |
| 4.12 | Block diagram | — | ✅ | ✔ |

## 5. QA — `qa-pipeline.md`

| # | Part | Agents | Status | GD |
|---|---|---|---|---|
| 5.1 | Three entry points; E1 plans, E2 unlocks execution, E3 re-runs only what the fix touched | — (pipeline) | ✅ | ✔ |
| 5.2 | Entry table — every carried input keyed to an agent's own `If absent` | — (pipeline) | ✅ | ✔ |
| 5.3 | The plan runs early — CP3 gates execution, never planning | `qa-lead` | ✅ | ✔ |
| 5.4 | Dispatch only the agent-ids the coverage assignment names, never all four | — (pipeline) | ✅ | ✔ |
| 5.5 | Three Editor executors serial, the build verifier alongside — forced by `tools:` | `qa-automation-engineer`, `playtest-tester`, `performance-qa-engineer` | ✅ | ✔ |
| 5.6 | Their internal order is the pipeline's choice, with the reason stated as such | — (pipeline) | ✅ | ✔ |
| 5.7 | The build branch exists only on an explicit GD request | `build-run-engineer`, `build-verification-tester` | ✅ | ✔ |
| 5.8 | What comes back — defect, design flaw, Editor-only number, `Not covered` | — (pipeline) | ✅ | ✔ |
| 5.9 | Sign-off against its own exit criteria; the two kinds of gap split | `qa-lead` | ✅ | ✔ |
| 5.10 | **CHECKPOINT 4** — three outcomes, and an accepted gap must be recorded durably | `producer`, gd | ✅ | ✔ |
| 5.11 | A CP4 rejection splits: drift → E3, or a change request → `technical-architect` | — (pipeline) | ✅ | ✔ |
| 5.12 | Routing table; three strikes stays in pipeline 4; the passes-review/fails-QA bound | — (pipeline) | ✅ | ✔ |
| 5.13 | Block diagram | — | ✅ | ✔ |
| 5.14 | The device lane — Step 2b: `/plan-test-coverage` derives the runnable cases, `device-test-walkthrough` runs them on the artifact, no device is a stated gap and never an Editor substitute, and a crash routes to `/investigate-device-crash` and never to the live-ops agent. The device lock it depends on is row **7.10a** | `build-verification-tester` | ✅ | ⬜ |
| 5.14b | **E3 re-entry needs a rebuilt artifact.** The build that found a device defect still contains it, so re-running the walkthrough against it proves nothing — and `build-run-engineer` cannot rebuild without a fresh GD request. Without one, that coverage stays unrun and joins the gap list rather than passing silently | `build-verification-tester`, `build-run-engineer` | ✅ | ⬜ |
| 5.14a | Both round-trip gaps closed in the agent files: `qa-lead` gained an `If absent` row for target platform (assume Editor-only, state it), and `build-run-engineer`'s `Result:` now carries the platform and configuration the verifier needs | `qa-lead`, `build-run-engineer` | ✅ | ⬜ |
| 5.15 | Approved prose compressed to hold the 200-line cap — Step 2, the CP table, CP4, Step 4, closing bullets. Called out, not slipped in | — (pipeline) | ✅ | ⬜ |

## Change request — `change-request.md`

| # | Part | Agents | Status | GD |
|---|---|---|---|---|
| 6.1 | Two entry points; a change before CP2 is not a change request at all | — (pipeline) | ✅ | ✔ |
| 6.2 | Halt new dispatches first, then classify — a running agent cannot be recalled | — (pipeline) | ✅ | ✔ |
| 6.3 | The architect classifies and never asks the GD to confirm the tier first | `technical-architect` | ✅ | ✔ |
| 6.4 | Minor / Moderate / Major — **criteria salvaged from the retired roster doc §6** | `technical-architect` | ✅ | ✔ |
| 6.5 | Minor is the one to get wrong: any boundary or interface move makes it Moderate | — (pipeline) | ✅ | ✔ |
| 6.6 | The rework list re-enters at `feature-development.md` E3, in serial order | — (pipeline) | ✅ | ✔ |
| 6.7 | A change request resets the strike count on every submission it invalidates | — (pipeline) | ✅ | ✔ |
| 6.8 | Routing table, incl. the `cto` hand-off when the change forces a tech choice | — (pipeline) | ✅ | ✔ |
| 6.9 | Block diagram | — | ✅ | ✔ |

## 7. Orchestrator — `orchestrator.md`, `references/`, `orchestration.md`, `state/`

| # | Part | Agents | Status | GD |
|---|---|---|---|---|
| 7.1 | `.claude/rules/orchestration.md` — the auto-loaded rule that gives the whole layer ignition | — (rule) | ✅ | ✔ |
| 7.2 | Step 0 — **14 lanes** read top-down, first match wins, **ordered specific before general**; **five** escalation criteria covering every C3/C4 path, not two; zero agent calls. Both counts are machine-checked | — (pipeline) | ✅ | ⬜ |
| 7.2a | The defect lane is scoped to what the pipeline built — no approved spec means nothing to measure | — (pipeline) | ✅ | ✔ |
| 7.3 | Route by the **cost of being wrong** — the C axis deciding the lane. The lane is never the tier | — (pipeline) | ✅ | ✔ |
| 7.4 | Sizing classifies the **input**, never a tier — the one interpreted boundary, stated as such | — (pipeline) | ✅ | ✔ |
| 7.5 | Escape upward the moment an escalation criterion turns out to apply | — (pipeline) | ✅ | ✔ |
| 7.6 | Three modes — full run / entry point / direct agent; the router infers and states, never asks | — (pipeline) | ✅ | ✔ |
| 7.6a | **Mode 3 is the GD's cost override, and the only one** — sizing is a proposal, stated so it can be overruled | — (pipeline) | ✅ | ✔ |
| 7.7 | Entry index — **24** addressable entries, machine-checked against what the pipelines declare; a "cluster" is one of these rows, never a new grouping. **Now its own file**, `references/entry-index.md`, per the cap debt below | — (pipeline) | ✅ | ⬜ |
| 7.8 | Direct dispatch — two classes derived from `tools:`; **14 / 14**, of which **12** accrue gate debt. Counts now machine-checked by `tools/verify-workflow-layer.ps1`, not asserted | — (pipeline) | ✅ | ⬜ |
| 7.9 | Review debt attaches to the artifact, is recorded, never enforced, and settles in batch | — (pipeline) | ✅ | ✔ |
| 7.10 | The global Editor lock — ten agents, one process, across concurrent runs | — (pipeline) | ✅ | ✔ |
| 7.10a | The global **device lock** — invariant **I7** in `orchestration.md`, with its table in `state/project-state.md`. One physical device: `build-verification-tester` walking cases over adb and `performance-qa-engineer` profiling a Development Build over adb are the same wire. Independent of the Editor lock — an agent can hold both | — (rule + state) | ✅ | ⬜ |
| 7.11 | The ledger — written at each transition, not at run end. **Now one per feature**, per §8 | — (state) | ✅ | ⬜ |
| 7.12 | `Routed to:` fallback for when no pipeline is running | — (pipeline) | ✅ | ✔ |
| 7.13 | Block diagram | — | ✅ | ✔ |

**Edits this round made to already-approved files** — called out, not slipped in:

| # | File | Change | GD |
|---|---|---|---|
| 7.14 | `feature-intake.md` | Its entry labelled **E1**; sizing vs. classification boundary stated | ✔ |
| 7.15 | `review-pipeline.md` | Existing entry labelled **E1**; **E2** added for a standalone audit | ✔ |
| 7.16 | `feature-development.md` | **E3** now names all three defect reporters — the row was already stale | ✔ |

**Closing the re-entry debt** — giving every re-entry an address, so mode 2 can name it and the ledger can feed it:

| # | File | Change | GD |
|---|---|---|---|
| 7.17 | `feature-intake.md` | **E2**–**E5** added: research back into the loop (step 3) or into the spec (step 6); `change-request.md` reopening CP2 and CP1. Each states what it carries and that triage does **not** re-run | ⬜ |
| 7.18 | `research-decision.md` | The single "back to step 6" node was **wrong for E3 and E4** — both leave mid-loop on Complex and must return at step 3, or the Advisor⇄Critic loop is skipped. Step 5 now maps each exit to its entry | ⬜ |
| 7.19 | `change-request.md` | Moderate → **E4**, Major → **E5**, in the diagram and the routing table | ⬜ |
| 7.19a | `feature-development.md` | Its own spec-gap return was a **fifth** unaddressed door. Folded into **E3** rather than given a sixth label — both mean "the architect writes step 6", and only the carried-in differs | ⬜ |
| 7.20 | `orchestrator.md` | Entry index 17 → **21** rows | ⬜ |
| 7.21 | `workflow-checklist.md` | The settled-decisions archive became a table — the file was **202 lines**, over the 200 cap, and the bullets duplicated reasoning the pipeline files already hold | ⬜ |

## 8. Classification migration — retiring Simple/Medium/Complex

The GD directed that the triage tier be replaced outright by the standard committed in `dd19ae7`, and that
each feature carry its own ledger. This section is that round. Nothing here is GD-reviewed yet.

**The design decision that made it work.** `task-classification.md` as committed kept both tiers side by side
and said neither overrides the other. Collapsing them naively would have given a one-line credential edit
(C4 → A5) an Advisor⇄Critic loop and a full docset, which is exactly the over-process that file exists to
prevent. So the migration splits what the single number buys, in **Step 4** of that file:

- **D sets the shape** — roles, Tech Spec, which checkpoints fire, which feature-root documents are owed.
- **C, R and X set the depth** — verification floor, evidence strength, safe-retry discipline. Never a step.
- **U3 fires CP1 at any D** — an undecided direction is the one thing outside D that adds a step, and it is
  the more honest trigger of the two, because it names what a design loop actually settles.

| # | Part | Files | Status | GD |
|---|---|---|---|---|
| 8.1 | Step 4 of `task-classification.md` rewritten as the single tier model — the axis-buys table, the D shape table, the A depth table | `task-classification.md` | ✅ | ⬜ |
| 8.2 | Checkpoints re-keyed to **D**, with U3 firing CP1 independently; CP1 spends U down and the tier is recomputed when it closes | `feature-intake.md` | ✅ | ⬜ |
| 8.3 | The **attempt budget** (`execution-loop.md`, keyed to D) and the **verification floor** (`effort-allocation.md`, keyed to A) added to every dispatch brief, every entry, and the ledger | `feature-development.md`, `references/entry-index.md`, `state/README.md` | ✅ | ⬜ |
| 8.4 | A Continuation Debt Record is **one strike**, never a free retry, and its known non-solutions travel into the next brief | `feature-development.md`, `review-pipeline.md`, `qa-pipeline.md`, `research-decision.md` | ✅ | ⬜ |
| 8.5 | `execution-loop.md`'s "persisting the record is not wired up yet" closed — it now lands in the feature ledger's **Continuation debt** table | `execution-loop.md` | ✅ | ⬜ |
| 8.6 | **`assurance-evaluator` wired into a pipeline** as `qa-pipeline.md` step 4b, A3+ only, after every other verdict. It had no home in any workflow when it was committed | `qa-pipeline.md` | ✅ | ⬜ |
| 8.7 | Docset floors re-keyed: full docset at **A4**, `LEDGER.md`/`DEBT.md`/`NOTES.md` at **A3**, A1/A2 owes none — keyed to A, not D, because documentation is earned by consequence | `feature-documentation.md`, `coding-principles.md` | ✅ | ⬜ |
| 8.8 | The artifact budget made operational — what the direct lane and each tier **must not** produce, stated where the work happens rather than only in the rule | `orchestrator.md`, `feature-intake.md`, `effort-allocation.md` | ✅ | ⬜ |
| 8.9 | Step 0's four escalation criteria re-grounded on the axes (C2+, D3+, C2+, U3), and "the lane is not the tier" stated — a direct-lane A5 still runs at V4 | `orchestrator.md`, `orchestration.md` | ✅ | ⬜ |
| 8.10 | `technical-architect`'s self-assessment re-keyed to **D**, with the envelope now returning the tier, all five axes, the floor, the budget and the acceptance criteria | `technical-architect.md` | ✅ | ⬜ |
| 8.11 | `qa-lead` plans against the A-tier **and the verification floor**; `code-reviewer` measures `Verification done:` against that floor | `qa-lead.md`, `code-reviewer.md` | ✅ | ⬜ |
| 8.12 | Implementation Note gains `Tier:` and `Attempts:`, and `Known limitations:` now carries into `DEBT.md` from **A3** | `implementation-note.md` | ✅ | ⬜ |
| 8.13 | `research-decision.md` **E4** re-grounded on **U2/U3** instead of "Triage returns Complex" — the axis it was always approximating | `research-decision.md` | ✅ | ⬜ |
| 8.14 | `change-request.md` re-reads **all five axes** — the one re-entry where D and C genuinely move — and blast radius is stated as a separate classification from the tier | `change-request.md` | ✅ | ⬜ |
| 8.15 | **One ledger per feature** at `state/<feature-slug>/ledger.md`; `state/project-state.md` holds the in-flight index, open review debt and both global locks; `state/ledger.md` deleted | `state/README.md`, `state/project-state.md`, `orchestrator.md`, `orchestration.md` | ✅ | ⬜ |
| 8.16 | The two-files-named-ledger collision restated now that both are per-feature: **uppercase beside the code** is documentation, **lowercase under `.claude/`** is state | `state/README.md`, `feature-context-reading.md`, `orchestrator.md` | ✅ | ⬜ |
| 8.17 | Entry index split into `references/entry-index.md`, closing the `orchestrator.md` cap debt as that row already planned | `references/entry-index.md`, `orchestrator.md` | ✅ | ⬜ |

**What deliberately did not change.** `security.md` keeps its no-exemption wording (the axes only reinforce
it — anything it covers is C4, therefore A5). `change-request.md` keeps Minor/Moderate/Major, which is blast
radius, not task difficulty. The Advisor⇄Critic 3-round cap, the three-strikes rule and the two-round QA
bound are unchanged — they count returns between agents, which the attempt budget does not.

## 9. Holding the line cap — promotion into `references/`

§8's content pushed five pipeline files past the 200-line cap. The GD directed that they be split into
separate files **grouped into folders, not left loose at the top level** — so the layer now carries one
`references/` folder, mirroring how skills in this repo are laid out (`SKILL.md` plus `references/*.md`) and
applying the same promotion rule `client/feature-documentation.md` sets for a feature's own docset: content
moves when it earns a file, the source keeps a **pointer and never a copy**, one fact has one home.

**What was promoted, and why each was the right cut.** In every case the section is read only in a situation
its source names — never while following that pipeline top to bottom. That is the test a section had to pass
to move; the line count only decided how many had to.

| # | Promoted | From | Read only when | GD |
|---|---|---|---|---|
| 9.1 | `references/entry-index.md` | `orchestrator.md` | A mode-2 dispatch needs an address | ⬜ |
| 9.2 | `references/orchestrator-direct-dispatch.md` | `orchestrator.md` | Mode 2 or 3 is the lane, or one returns with no pipeline running | ⬜ |
| 9.3 | `references/intake-advisor-critic-loop.md` | `feature-intake.md` | **D4–D5 or U3** — most features never enter the loop | ⬜ |
| 9.4 | `references/research-depth-lanes.md` | `research-decision.md` | Entering the pipeline, to pick the lane | ⬜ |
| 9.5 | `references/development-brief.md` | `feature-development.md` | Writing a dispatch brief — a per-dispatch lookup, not a step | ⬜ |
| 9.6 | `references/development-feature-documents.md` | `feature-development.md` | Every task in a root has returned | ⬜ |
| 9.7 | `references/qa-device-lane.md` | `qa-pipeline.md` | A build exists — `build-run-engineer` refuses anything but a GD request, so most runs never open it. Took the six device routing rows with it | ⬜ |
| 9.8 | `references/qa-assurance-gate.md` | `qa-pipeline.md` | **A3 and above**, every other verdict in | ⬜ |
| 9.9 | `references/qa-checkpoint-4.md` | `qa-pipeline.md` | Closing a feature. **`qa-pipeline.md` still owns CP4** — it keeps the three outcomes inline and promotes only the detail, so ownership did not move with the prose | ⬜ |
| 9.10 | `references/README.md` | — | The folder index: what each file is, what it was promoted from, and the rule against creating one speculatively | ⬜ |

**Result.** Every file in `.claude/workflows/` is now at or under the cap — `feature-intake.md` 199,
`qa-pipeline.md` 199, `review-pipeline.md` 199, `feature-development.md` 191, `research-decision.md` 186,
`orchestrator.md` 182, `change-request.md` 132. `workflow-checklist.md` stays exempt by its own header.

**Two things deliberately did not move.** Each pipeline's **routing table** stays with its pipeline — it is
the operational heart of the file, not a lookup consulted elsewhere; only the six device rows left, and only
because they are unreachable unless that lane is open. And **cross-run state is not documentation**: it stays
in `state/`, which is why the layer has two folders rather than one.

## 10. Contradiction round — optional gates, standalone runs, and a check that runs

The GD directed three things in one round: raise the layer to a uniform standard, make **review and QA
optional and separately asked for**, and make **every pipeline callable on its own**. Everything below is
that round. Nothing here is GD-reviewed yet.

**The 200-line cap stays, by the GD's explicit direction** — promotion into `references/` is the flexible
architecture, not a workaround. Five files needed room this round and all five got it by promoting, never by
deleting reasoning. Six new reference files, and the cap holds at 200 across all of `workflows/`.

### The contradictions closed

| # | Contradiction | How it was closed | GD |
|---|---|---|---|
| 10.1 | **C bought process.** `task-classification.md` Step 4 says C/R/X never buys a checkpoint, a document or an extra agent — yet two of Step 0's four criteria are **C2+** and routed to an 8-call pipeline with a mandatory CP4. A one-constant `Game.Core.*` change is D1 and still cost 6+ calls | The **gated-direct lane**: one agent, then both gates at `review-pipeline.md` **E3**, no pipeline and no checkpoint. Four qualifying conditions, a 2-strike bound, escape upward on any failure. `references/gated-direct-lane.md` | ⬜ |
| 10.2 | **Every inner loop was capped; their composition was not.** Three strikes → architect → **E3** never said what the strike count became, so a second three-strike run was legal forever. Same for the QA bound and CP4 rejections | `references/loop-termination.md` — **one root-cause reset per submission**, shared across every loop, then a feature-level Continuation Debt Record to the GD. CP4 defect rejections bounded at 2 before root cause, 3 before stopping. Invariant **I8** | ⬜ |
| 10.3 | **Locks were invariants with no recovery path.** I3 and I7 said "never two at once" but nothing released a lock whose holder died — an invariant that cannot be restored stops being one | `Claim expires` on both lock tables, and a three-step reclaim procedure in `state/project-state.md` that stops at the first step to answer. The reclaim is recorded, and whatever the stale holder produced is treated as unverified per `execution-loop.md`'s safe-retry rule. Invariant **I9** | ⬜ |
| 10.4 | **No terminal state for abandoned work**, though `execution-loop.md` calls `Blocked` and `Partially complete` legitimate outcomes | `Status: In flight \| Closed \| Abandoned`, with why and the last verified state. A feature with no terminal state is one a later session cannot tell from one still running | ⬜ |
| 10.5 | **Test code reached no gate.** `qa-automation-engineer` writes `.cs`, but `review-pipeline.md` **E1** accepted submissions only from `feature-development.md` — so I2 recorded debt with no route to settle it | `review-pipeline.md` **E3** and `qa-pipeline.md` step 3b. Invariant **I10**. A weakened assertion advertises coverage that does not exist, which `verification-standards.md` calls worse than no suite. **Reverses a previously accepted debt** — see the register | ⬜ |
| 10.6 | **`orchestration.md` duplicated `orchestrator.md`'s Step 0**, violating the one-fact-one-home rule the layer sets for itself — and did it in the one file that is auto-loaded into every session | The criteria table stays in the router; the rule keeps four lines saying why reading it is not optional. `rules/orchestration.md` is 10 lines shorter in every session | ⬜ |
| 10.7 | **The layer's self-description had already drifted** — class A stated 13 against an actual 14, the checklist said 11 debt-accruing against the reference's 12, and `unity-engineer:92` / `ui-ux-programmer:81` pointed at **blank lines** | Counts corrected; every line-number cross-reference replaced with quoted text that cannot silently move. Then automated: `tools/verify-workflow-layer.ps1`, **52 claims, all passing**, plus `/verify-workflow-layer` | ⬜ |
| 10.8 | **Every constant was E0** by the layer's own evidence scale, while it required E2 of everything else | `state/calibration.md` — one row per closed ledger, copied from numbers already recorded, never estimated. It does not make the constants right; it makes them knowable, and says so plainly until they are | ⬜ |

### The GD's three directions

| # | Direction | What it changed | GD |
|---|---|---|---|
| 10.9 | **Review and QA are optional and separate** | `references/optional-gates.md` — the two decision points, what the ask must carry (what was built, the tier, the cost of running, **the concrete cost of skipping**), recommend-then-defer by tier, what disappears when each is declined, and how to opt in later. Both pipeline files restate it in their own scope. CP3 and CP4 now fire **only when their gate ran**; `feature-development.md` asks at the Core return rather than at the end, because that is where the cost is highest | ⬜ |
| 10.10 | **The one thing that stayed mandatory** | **The ask itself, and recording the answer.** `project-state.md`'s debt table now separates **unoffered** from **declined**, with who declined and when. A declined gate is an accepted gap under **I6** and lands in `DEBT.md` before closure is reported. A feature that closed without a gate is never reported as one that passed it | ⬜ |
| 10.11 | **Every pipeline callable alone** | `references/standalone-runs.md` — what each of the six is worth alone, what the GD supplies in place of the missing upstream, and what comes back instead of a hand-on. Two doors were missing and are now open: `qa-pipeline.md` **E4** (QA on shipped code, or after declining earlier) and `feature-development.md` **E2** broadened to the GD's own notes. Entry index 21 → **23** | ⬜ |

### Promoted this round — the cap held by moving content, never by cutting reasoning

| Promoted | From | Read only when |
|---|---|---|
| `optional-gates.md` | `orchestrator.md` | Implementation returned and a gate would otherwise be dispatched |
| `standalone-runs.md` | `orchestrator.md` | The GD named a pipeline instead of describing a feature |
| `gated-direct-lane.md` | `orchestrator.md` | An input trips a C2+ criterion and nothing else |
| `loop-termination.md` | every pipeline with a counter | A cap has been reached |
| `review-needs-confirmation.md` | `review-pipeline.md` | `security-reviewer` returned that verdict |
| `review-checkpoint-3.md` | `review-pipeline.md` | Compiling or rejecting CP3 |
| `qa-entry-inputs.md` | `qa-pipeline.md` | Taking any entry into QA |
| `qa-execution-order.md` | `qa-pipeline.md` | Dispatching the coverage assignment |

Also moved: the ledger's **what each row protects** table, from `orchestrator.md` into `state/README.md`
beside the template it describes. One fact, one home — the same rule, applied to the layer's own prose.

### What this round could not fix

**The layer has still never run.** No feature has passed through a ledger, no constant has been measured, and
no checkpoint has been observed changing an outcome. §10 makes the layer internally consistent and
machine-checkably so; it cannot make it *validated*. `state/calibration.md` is the instrument, and only real
features fill it.

## 11. Audit round — reachability, loop closure, and the context tax

Three questions the GD asked, answered with data rather than reading: **which agents does no lane reach**,
**which checkpoints can be skipped entirely**, and **which loops have no ceiling**. Plus the context tax,
which §10 had measured and left as a GD decision. Nothing here is GD-reviewed yet.

### Reachability — three agents no lane could reach

Traced mechanically: for each of the 28 agents, does any workflow file name it?

| # | Found | Fixed | GD |
|---|---|---|---|
| 11.1 | **`git-expert`** was named by **no workflow file at all** — reachable only if the GD typed its name. §7's debt register had recorded this as "closing it means adding a lane row"; the row was never added | Step 0 lane: a git or version-control task → `git-expert`, mode 3 | ⬜ |
| 11.2 | **`ci-cd-engineer`** appeared in one reference file and no lane | Step 0 lane: authoring a pipeline, or diagnosing a failed run | ⬜ |
| 11.3 | **`crash-anr-investigator`** appeared only as "owned elsewhere" inside `qa-pipeline.md`. A GD saying *"Play Console shows a crash spike"* had **no row to land on** — the agent existed for a purpose the router could not route to | Step 0 lane for released-production telemetry, with the `/investigate-device-crash` split stated inline so the two are never confused | ⬜ |
| 11.4 | Nothing was checking for this | Verifier gains a **reachability check**: every agent must be named by at least one workflow file. It immediately caught a *phantom* id too — prose in a new file referred to an agent that does not exist | ⬜ |

### Checkpoints — one could disappear entirely

| # | Found | Fixed | GD |
|---|---|---|---|
| 11.5 | **§10 made CP4 conditional on QA running** — so a D1–D2 feature with both gates declined could close with **no GD gate at any point**. That is worse than the over-process the round was fixing: a feature stops being mentioned rather than being closed | **CP4 always fires.** Closing a feature is the GD's decision; QA signing it off is a different one, and only the second is optional. QA now changes what CP4 *rests on*, never whether it happens. `producer` takes Implementation Notes in place of QA reports, and where there is not even a note it is skipped rather than sent to return `Blocked` | ⬜ |
| 11.6 | **The assurance gate was buried.** `assurance-evaluator` is the only thing in the layer that checks whether a claimed verification actually happened — and §10 put it behind an optional gate, so at A5 with QA declined, nothing checks it | Kept inside QA — inventing a third mandatory process would violate the GD's own direction — but the ask at **A4+** must now name **this specific loss in these words**. `effort-allocation.md` puts a false claim beyond any waiver, and a GD reading "skip QA" would not predict that this is what they are skipping | ⬜ |
| 11.7 | CP2 and CP3 rejections had no bound while CP4 had one — an asymmetry introduced by §10 | CP2 bounded at 3, CP3 at 2, both in `loop-termination.md` | ⬜ |

### Loops — eight were individually capped and jointly unbounded

Every loop in the layer had a cap. **The compositions did not.** `loop-termination.md` is now the single home
for all sixteen bounds, and nine of them are stated there and nowhere else.

| # | The loop that could run forever | Bound | GD |
|---|---|---|---|
| 11.8 | `qa-lead` `Not signed off` → re-dispatch step 2 → sign-off → `Not signed off` → … | **2**, then the gap goes to CP4 | ⬜ |
| 11.9 | `assurance-evaluator` `FAIL` → E3 → review → QA → `FAIL` → … | First `FAIL` is an integrity finding; a **second** is a QA fail and spends that counter | ⬜ |
| 11.10 | CP2 reject → revise → CP2 → … | **3**, then it is a direction problem, not a drafting one | ⬜ |
| 11.11 | CP3 reject → E3 → CP3 → … | **2**, sharing the single root-cause reset | ⬜ |
| 11.12 | implementing agent → tech lead → `Rejected` back → same agent → … | **1 round trip.** A second identical refusal is a disagreement about ownership, which neither party can settle — to `technical-architect` as a routing question | ⬜ |
| 11.13 | `Blocked` → ask → cannot supply → re-dispatch → `Blocked` → … | **2** on the same missing input. Past it the missing input *is* the finding | ⬜ |
| 11.14 | Gate declined → re-offered → declined → re-offered … | **1 per boundary, never twice in a run.** A new boundary is a new fact, not a new mood. Nagging trains the GD to stop reading the ask, which costs more than the gate | ⬜ |
| 11.15 | The root-cause reset was per-submission but not per-*loop-family* | One reset, **shared** across review strikes, the QA bound, CP3 and CP4 — not one each | ⬜ |

### The context tax — closed

§10 measured it (2,071 lines auto-loaded before the GD types) and left it as a decision. The GD took it.

| # | Change | GD |
|---|---|---|
| 11.16 | `.claude/rules/client/` and `.claude/rules/qa/` → **`.claude/standards/`**, which is not auto-loaded. **2,071 → 1,366 lines: −34%**, paid back on every session *and* every subagent dispatch. 91 cross-references rewritten | ⬜ |
| 11.17 | The test for where a file belongs, stated once in `rules/standards-index.md`: **a rule you must obey before you know it exists is loaded; a standard you consult when you reach its domain is read** | ⬜ |
| 11.18 | Nothing was weakened — every governed agent already carried a required-reading table naming its own files. That table is now the **loading mechanism** rather than a citation, and `development-brief.md` gains a **seventh required field**: the brief names the standards by path | ⬜ |
| 11.19 | Verifier gains two checks: every standard has a stated reader in the index, and **no file anywhere still points at the pre-move location** | ⬜ |

### Verifier: 52 → **69** machine-checked claims

New this round: reachability, phantom agent ids, standards-have-readers, no-stale-standards-path, and the
four new reference files under the cap. It caught two real defects while being written — the phantom
`sdk-engineer` id, and three cap breaches from this round's own additions.

### Promoted this round

`review-entry-inputs.md`, `qa-test-code-gate.md`, `intake-tech-spec.md`, `development-escalation-lane.md` —
four files, each read only in a situation its source names. Every workflow file is at or under 200.

### Still open, deliberately

**The layer has still never run.** §11 removed every structural conflict it could find and made 69 claims
machine-checkable. It did not, and cannot, make a single constant measured. `state/calibration.md` remains
the instrument and real features remain the only thing that fills it.

## 12. State moves out of the framework

The GD's direction: **a real run must never create or write a file under `.claude/`**, because this repository
is a template applied to every project — and each feature's ledger belongs at that feature's own root, as
`feature-context-reading.md` already had it. §7 had put per-feature run state at
`.claude/workflows/state/<feature-slug>/ledger.md`, which made the framework the place one project's strike
counts accumulated. Nothing here is GD-reviewed yet.

| # | Part | Where it landed | GD |
|---|---|---|---|
| 12.1 | **Per-feature run state moved to the feature root**, merged into `LEDGER.md` as a `## Run state` half beside its `## Decisions` half. One ledger per feature, and now literally one file | `state/README.md`, `state/templates/feature-ledger.md`, `feature-context-reading.md`, `feature-documentation.md` | ⬜ |
| 12.2 | **The two-files-named-ledger distinction is deleted, not restated.** §8 row 8.16 had separated them by letter case — uppercase beside the code, lowercase under `.claude/` — which is not a distinction a reader can act on, and which Windows would not even let sit in one directory. **This supersedes 8.16** | `state/README.md`, `orchestrator.md`, `feature-context-reading.md` | ⬜ |
| 12.3 | **Everything that cannot be per-feature moved to `<state-root>`** — `.workflow/` at the project root unless a project's `CLAUDE.md` says otherwise. The in-flight index, open gate debt, the gated-direct counters and both global locks | `<state-root>/project-state.md`, from `state/templates/project-state.md` | ⬜ |
| 12.4 | **`workflows/state/` now holds rules and templates only.** `project-state.md` and `calibration.md` became templates under `state/templates/`; the lock-reclaim procedure and the what-each-row-protects table stayed in `state/README.md`, which is framework rule rather than project record | `state/README.md`, `state/templates/` | ⬜ |
| 12.5 | **The architect's return now names the feature root**, because the ledger has nowhere to live until somebody states it. At **U3** the root is provisional and the ledger moves with the feature rather than a second one being opened | `technical-architect.md` output envelope, `feature-intake.md` step 2 | ⬜ |
| 12.6 | **The rule is machine-checked, not just written.** Two new claims: nothing but `README.md` and `templates/` under `workflows/state/`, and no file under `.claude/` still pointing at a retired state path. Both were negative-tested — a planted `state/my-feature/ledger.md` and a planted pointer each fail the run. 75 claims, all passing | `tools/verify-workflow-layer.ps1` | ⬜ |

### What this round deliberately did not do

**Work with no feature root still has no ledger**, and that is unchanged rather than overlooked: a
gated-direct submission, a mode-3 dispatch and a standalone gate run have nowhere to put one, so their
counters stay in `<state-root>/project-state.md`. Opening a ledger for them would be the paperwork
`effort-allocation.md`'s artifact budget forbids.

**No existing ledger was migrated**, because none exists — the layer has still never run. The first real
feature writes the first `LEDGER.md` under the new shape, and that is also the first evidence any of it
works.

## 13. `feature-intake.md` review round — ten findings, and a check that sees routing

An adversarial per-pipeline review of `feature-intake.md`, read against the three agent contracts it
dispatches and against `research-decision.md`. Ten findings, eight of them closed here. Nothing GD-reviewed
yet. The full record, with the evidence behind each finding, is in `.claude/docs/feature-intake-update.md`.

| # | Part | Where it landed | GD |
|---|---|---|---|
| 13.1 | **A D1–D2 feature returning from research had no route back.** `feature-intake.md`'s **E3** row and `research-decision.md`'s exit table both sent it to step 6 — which runs at D3–D5 only, reaching a CP2 that fires at D3–D5 only. Followed literally it produces a Tech Spec for a one-role change, the artifact budget's own named violation. **The mermaid was already correct**: its `Resume` node branches on shape and both tables did not | `feature-intake.md` E3 row, `research-decision.md` step 5 | ⬜ |
| 13.2 | **The loop had no dispatch brief.** `critic` blocks without the direction *in detail* and without the goal, and the GD picks a direction by name — so the loop's most ordinary path was a `Blocked` the caller caused. Six rows, each keyed to a real `If absent`, plus the `advisor`→`critic` handoff row. Folded into the loop's own file rather than given a new one: it serves two agents inside one loop, where `development-brief.md` serves seven across a pipeline | `references/intake-advisor-critic-loop.md` | ⬜ |
| 13.3 | **The Tech Spec envelope had no `Assumptions:` field.** Every implementing agent has one; the document the whole fan-out is measured against did not, and CP2 is where the GD approves it unseen | `technical-architect.md` envelope + guardrail, `references/intake-tech-spec.md` | ⬜ |
| 13.4 | **A Major change now resets the Advisor⇄Critic round count**, and it is the one cap a re-entry clears. Major invalidates the direction those rounds settled, so charging them to the new one left a feature that spent two rounds with one. The ruled-out options still travel | `change-request.md`, `references/entry-index.md`, `references/loop-termination.md` | ⬜ |
| 13.5 | **`Tier history:` and `Research:` added to the ledger.** CP1's reclassification overwrote the tier in force while the loop ran, so `assurance-evaluator` scored A5 effort against a final A3. And the named coverage that justifies skipping research had no home but conversation context | `state/templates/feature-ledger.md` | ⬜ |
| 13.6 | **A CP2 rejection now splits before it is acted on**, as CP3 and CP4 already did: the spec misread the request (redraft) versus the direction is now wrong (**CP1** at **E5**). The bound at three was finding the second kind after three architect dispatches | `feature-intake.md` CP table, `references/intake-tech-spec.md` | ⬜ |
| 13.7 | **`Open design question:` is now classified `design \| architecture \| technology \| none`.** At D3, where no loop runs, that field is the only thing that raises a missing capability — a hole step 5 already admitted and nothing closed | `technical-architect.md`, `feature-intake.md` step 5 | ⬜ |
| 13.8 | **Routing is now machine-checked, not only structure.** Two claims: an entry resuming at a shape-gated step must state the shape, and no file may send work to a door the target pipeline does not declare. **Negative-tested** — reverting 13.1 fails the first; the second found a live second instance (**E2** → step 3, the loop, stated no shape) and a sentence naming `change-request.md` **E4**/**E5**, which are this pipeline's doors and not that one's. 78 claims, all passing | `tools/verify-workflow-layer.ps1`, `feature-intake.md` | ⬜ |
| 13.9 | **One owner named for the gate offer.** `optional-gates.md` owns the ask's *shape*; the pipeline that reaches a boundary owns *where* it fires; the orchestrator owns every ask belonging to no pipeline. Three files each read as the asker before this | `references/optional-gates.md` | ⬜ |

### What this round deliberately did not do

**`technical-architect` was not given authority to recommend a direction.** At D4–D5 an `architecture`
question — how to structure something with what the project already has — reaches the Advisor⇄Critic loop,
where `advisor` is barred from ranking, `critic` only attacks the leaning option, `cto` owns technology
rather than structure, and the architect is not consulted until step 6. **No agent may say which option fits
this codebase.** That may be the intended price of the GD deciding alone, or a misallocated decision — it is
the GD's call, so the limitation was written down with its existing escape (a mode-3 dispatch to
`technical-architect` before locking CP1) rather than silently resolved. Recorded in the debt register.

**No enforcement was added beyond the verifier.** The hooks and the ledger-append helper that would close
`F1` and `F2` in `.claude/docs/workflow-layer-assessment.md` change harness behaviour and belong to the GD.

## 14. `feature-development.md` review round — run, not read, and the custody class finally machine-checked

The third per-pipeline review, by the same method as §13's second half: the pipeline was **run**, not read —
four real dispatches (`csharp-engineer`, `tech-lead-sdk-platform`, `netcode-engineer`, then `code-reviewer`
on the Core submission) following the files literally. Twenty-six findings, **D1–D26**, all closed except
four halves that live in pipelines this round was told not to touch. The full record is in
`.claude/docs/feature-development-update.md`. Nothing GD-reviewed yet.

**One root cause under most of them.** The routing table read `Status:` and `Routed to:` and nothing else, so
in all three implementing returns the highest-value content sat in a field no row mentioned: six risks on a
`Blocked`, a V3 verification account on a `Done`, a complete message contract on a `Needs-decision`.

| # | Part | Where it landed | GD |
|---|---|---|---|
| 14.1 | **The pipeline declared no exits** — the only one of six without a hand-on table, while `review-pipeline.md` **E1** and `qa-pipeline.md` **E1**/**E3** each name it as their origin. Its nine `Produces` artifacts were named nowhere else either | `references/development-exit-and-custody.md` (new) | ⬜ |
| 14.2 | **Two Implementation Note fields have no source in any envelope.** `Attempts:` — no envelope has one, and `assurance-evaluator` absent it assumes Attempt 1. `Verification done:` — `csharp-engineer`, `server-authoritative-engineer` and `tech-lead-sdk-platform` carry none of the four fields the rule names. Live, the Core filed its V3 account under `Assumptions` and the **gate itself reported the split** | `development-brief.md`, `development-exit-and-custody.md`, `rules/implementation-note.md` | ⬜ |
| 14.3 | **Both tech leads write code that reached no gate** — invariant **I10**'s named hole. "Silent to the GD" was being read as silent to the gates. Their `Scope of pattern: project-wide` had no home either, which is `cto`'s `Standard set:` one level down | `development-escalation-lane.md`, `development-exit-and-custody.md` | ⬜ |
| 14.4 | **No route for a design flaw** — invariant **I5** appeared nowhere in a pipeline dispatching nine agents, and the live run raised one on its first dispatch. **Third-party content** was also being adopted before the `security.md` §7 gate that must clear it | `feature-development.md`, `development-exit-and-custody.md` | ⬜ |
| 14.5 | **An axis moving mid-development had no route.** The gate found two textbook **U2**s on a feature classified U1 and said the tier should be A5/V4; `entry-index.md` freezes D/C/R/X on re-entry and `change-request.md` is for a GD change. It was neither | `feature-development.md` routing table | ⬜ |
| 14.6 | The brief goes **seven rows → nine**: the **feature root** (the first live dispatch blocked on it) and the **netcode foundation** (whose absence buys a `cto` escalation for a value the caller holds) | `development-brief.md` | ⬜ |
| 14.7 | **E2's "no documents" was keyed to D while step 4 keys them to A** — a D1 credential change is A5 and owes `LEDGER.md` decisions and `DEBT.md`. The **mermaid never branched on shape** either, so E2 could fall through to `feature-intake.md` **E3 — step 6**, which runs at D3–D5 only: I9's family in this pipeline's own diagram | `feature-development.md` | ⬜ |
| 14.8 | **The other half of the seam, found by grepping both directions.** `research-exit-and-custody.md` had no exit row for a development-originated escalation, so both `cto` routes would have been handed back into `feature-intake.md` — reopening a Tech Spec the fan-out is already building against | `research-exit-and-custody.md`, `research-decision.md` | ⬜ |
| 14.9 | **Fix J, done and negative-tested.** Two semantic checks: every `Produces` artifact must be received somewhere, and every `Routed to:` destination must have a routing row. **Three defects had to be driven out of them, all found by negative-testing rather than by reading**: scope included the agents table so artifacts matched their own declaration; scope pulled in the shared references so a destination could pass on somebody else's sentence; and the artifact match was case-insensitive, so `Server Authority` was "received" by an incidental lowercase phrase. Tightening it immediately produced **D27** in `research-decision.md`, a pipeline already closed at 8.9. **86 claims**, scoped to the three reviewed pipelines and printing the other three as not-yet-asserted | `tools/verify-workflow-layer.ps1` | ⬜ |
| 14.10 | Self-description drift fixed: `{{ }}` claimed twice and present once; the escalation lane "not drawn above" while drawn; `implementation-note.md` citing a **step 5** that did not exist and "all **six** fields" of an eight-field note; E3's origin list stale **again** at three of five | `feature-development.md`, `rules/implementation-note.md` | ⬜ |
| 14.11 | The fan-out seriality argument promoted, to pay for the additions without deleting reasoning. **Open decision C now lives in `references/development-fan-out.md`**, not in step 2 — called out, not slipped in. All three pipelines hold at **199** lines | `development-fan-out.md` (new) | ⬜ |

**What this round could not reach.** The three Editor-holding agents were never dispatched — this repository
has no Unity project — so step 2's serial claim is still **E1 — inspection**, and the ledger rows this round
writes into have still received nothing. The score is **6.2 → 8.2** — marked once at 9.0, then re-marked strictly at the GD's request, which cost 0.8. Self-assessed either way, which is **E0**. The strict pass also found **D27** in `research-decision.md`, so neither earlier **8.9** is safe under this ruler.

## 15. `qa-pipeline.md` review round — the gate that decides pass or fail, run rather than read

The fifth per-pipeline review, same method as §13's second half and §14: the pipeline was **run** — five real
dispatches (`qa-lead` plan, `qa-automation-engineer`, `qa-lead` sign-off, `assurance-evaluator`, `producer`)
following the files literally, on an A4 feature with the **review gate declined**, which is this pipeline's
riskiest untested claim. Nineteen findings, **QA1–QA19**, nine of them High. The full record is in
`.claude/docs/qa-pipeline-update.md`. Nothing GD-reviewed yet.

**The finding that matters most.** Step 4 said `qa-lead` judges against the exit criteria *it wrote itself* at
step 1 — but it is stateless, nothing carried them back, and no `If absent` row makes it say so. Run live, the
same feature's plan and sign-off returned **different criteria lists**. The bar moved silently inside the gate
that decides whether a feature passes.

| # | Part | Where it landed | GD |
|---|---|---|---|
| 15.1 | The exit criteria now travel back with the sign-off dispatch and are written to the ledger at step 1 | `qa-pipeline.md`, `qa-entry-inputs.md`, `qa-exit-and-custody.md`, `feature-ledger.md` | ⬜ |
| 15.2 | **The agents table had no `Produces` column at all** — its third column was `Runs in`, so the layer's own custody check read the wrong cell, found one incidental artifact and **passed** while six of its eight deliverables were named nowhere in the pipeline or its own references | `qa-pipeline.md`, new `references/qa-exit-and-custody.md` | ⬜ |
| 15.3 | A new check asserts the column itself, because a check that passes for the wrong reason turns an open defect into a green claim. Negative-tested: reverting the header FAILs the new check while the old one still PASSes | `tools/verify-workflow-layer.ps1` | ⬜ |
| 15.4 | **"The orchestrator asks the GD" survived here** — the exact wording `optional-gates.md` was rewritten to forbid, fifth recurrence of **F6**. Fixed, then machine-checked across all six pipelines and every reference but the owning file — the recurring wording, not every possible phrasing of it | `qa-pipeline.md`, `tools/verify-workflow-layer.ps1` | ⬜ |
| 15.5 | The routing row for an unclosable gap sent the feature to `producer` and CP4, **skipping step 4b** — the gate that checks whether a claimed verification happened, on the one path where an unmet criterion is being carried to the GD. The prose above it said the opposite | `qa-pipeline.md` | ⬜ |
| 15.6 | Custody extended to this pipeline: **5 of 6** now asserted. `change-request.md` remains unasserted | `tools/verify-workflow-layer.ps1` | ⬜ |
| 15.7 | Coverage that **could not be executed** returns `Status: Done` with `Results: 0 / 0`; nothing distinguished it from coverage that ran, and the bound on re-dispatch counted rounds rather than causes | `qa-pipeline.md`, `qa-exit-and-custody.md`, `loop-termination.md` | ⬜ |
| 15.8 | `qa-automation-engineer`'s contract makes a review verdict a **precondition**, against a pipeline that declares itself independent of review. The dispatch states the decline so the `If absent` never fires | `qa-entry-inputs.md` | ⬜ |
| 15.9 | An `Acceptance: FAIL` presumed a named owner; live it had none, because the Implementation Note it failed is pipeline-assembled | `qa-pipeline.md`, `qa-assurance-gate.md` | ⬜ |
| 15.10 | E1/E4 were two doors for one entry — `optional-gates.md` sent a declined gate opted into later to **E1**, this pipeline declared **E4**. Told apart by the ledger now | `qa-pipeline.md`, `optional-gates.md`, `entry-index.md` | ⬜ |
| 15.11 | Multi-destination `Routed to:` had no row here, fourth pipeline running. Live, one executor returned **three** | `qa-pipeline.md` | ⬜ |
| 15.12 | **95 claims**, 94 holding, one accepted gap (the skill relocation, still GD-deferred). **Six negative tests over five bypass paths**, all failing on the defect and passing on restore | `tools/verify-workflow-layer.ps1` | ⬜ |
| 15.13 | **The round was then put through the layer's own gates.** `code-reviewer` returned **`Request changes`** — ten findings, three High — against the fixes above: the `Produces` check tested the token's *presence* rather than its *position* and never checked the cells; a reference contradicted a rule file this same round had changed; `playtest-tester` has neither `Defects:` nor `Regressions:`, so QA13 was closed for one agent and not the class. All ten closed | `.claude/docs/qa-pipeline-update.md` Part 4b | ⬜ |
| 15.14 | **Negative-testing those fixes exposed two defects nobody predicted.** (1) The new check's header regex ended `[^\r\n]*$`, which never matches a CRLF file — so it shipped **vacuous on every CRLF file**, silently skipped by its own `continue`. Two pipelines were observed being skipped; an independent run afterwards found **all six** files CRLF, so the blast radius was at least two and plausibly all six — stated as observed rather than rounded either way. (2) A renamed agents heading **crashed the verifier** at `$text.Replace($agentsSec, '')`, aborting the run and skipping every later claim, including the skill and runtime-state checks — a pre-existing bug from §14's fix J. Both fixed; a column swap **on a CRLF file** is now one of the five tested bypass paths, which is what proves those two files are read at all | `tools/verify-workflow-layer.ps1` | ⬜ |
| 15.15 | **A fix was wrong on first attempt and is recorded as such.** Widening the gate-ask check flagged `review-pipeline.md`'s *correct* sentence naming the orchestrator as the asker for an ask belonging to no pipeline — the legitimate third row of `optional-gates.md`'s ownership table. A check that flags correct text is how a check stops being read. It now targets the forbidden shape only | `tools/verify-workflow-layer.ps1` | ⬜ |
| 15.16 | **Scored independently, not only self-marked.** `assurance-evaluator` ran last and returned **`CONDITIONAL PASS`** — weighted **8.8** against the A4 floor of 9.0, and **8.75** on the six axes against the round's self-score of 8.9. It confirmed four axes and marked two down. **No independent party has executed the verifier**: both gates lack a shell, so the claim counts rest on the author's run plus one shell-capable re-run | `.claude/docs/qa-pipeline-update.md` Part 4b | ⬜ |

## Open decisions the GD owes

**None.** All seven are settled, and each one's full reasoning now lives in the pipeline file named below —
that file is the durable record, not this row.

| | Settled as | Now lives in |
|---|---|---|
| **A** | CP3 gates QA **execution**, not QA planning — `qa-lead` in plan mode needs only the spec and the tier, so a CP3 rejection invalidates nothing it produced | `review-pipeline.md` step 6 |
| **B** | A `Routed to: rd-engineer` becomes a GD ask, never an auto-dispatch — the GD's yes is the explicit summon the agent requires. A GD gate only on the standalone path | `research-decision.md` steps 2, 5 |
| **C** | The client fan-out is **serial, settled not deferred** — one Editor, three Editor-holding agents, and any `.cs` write forces a domain reload that ends another's Play Mode run. Three escapes tested and rejected | `feature-development.md` step 2 |
| **D** | `review-pipeline.md` owns both gates — the reject → author → resubmit loop is a development cycle, not QA execution | `qa-pipeline.md` step 2 points at it |
| **E** | Neither `gd` nor `tech-lead-sdk-platform` by default — `Needs Confirmation` is an input to supply and re-run, never a verdict to escalate. Ladder: `tech-lead-sdk-platform` → the authoring agent → `gd` | `review-pipeline.md` |
| **F** | The merged checkpoint is **CP4** — the approved tier table already said so; the competing reading came only from the retired roster doc | `feature-intake.md` |
| **G** | The passes-review/fails-QA bound is **two rounds** — three strikes counts *review* rejections, so this loop would otherwise never terminate. A pipeline decision, not a contract derivation | `qa-pipeline.md` |

## Debt register

`Open` = owed · `Settled` = paid, kept for the record · `Deferred` = seen, priced, declined · `Recorded` = a fact, not work. None blocks the layer.

| Debt | State | What closing it takes |
|---|---|---|
| **Test code meets no review gate** | Settled | Closed in §10 by `review-pipeline.md` **E3** and `qa-pipeline.md` step 3b, plus invariant **I10**. **This reverses a debt the GD had previously read and chosen to leave open** — called out rather than slipped in, and revertible by deleting those three additions |
| **Re-entry targets are unaddressable** | Settled | Closed by rows 7.17–7.21. Turned out to be **four** doors, not three: the research hand-back is two addresses, not one, because **E3** and **E4** leave mid-loop on Complex and returning them at step 6 would skip the Advisor⇄Critic loop the tier exists for. That was a live defect in an approved diagram, not just a missing label |
| **`orchestrator.md` is at the 200-line cap** | Settled | Closed in §9 — the entry index moved out exactly as this row planned, and direct dispatch followed it. `orchestrator.md` is 182 lines |
| **The ledger has never been exercised** | Recorded | No feature has run through a feature-root `LEDGER.md` (a `state/<slug>/ledger.md` before §12 moved it), so its column contract is designed rather than proven. Expect the first real run to reshape it; that is normal, not a defect |
| **Every constant in the layer is E0** | Recorded, now instrumented | 3 strikes, 3 rounds, the 2-round QA bound, budgets 2–5, 1 reset, 2 gated-direct strikes — all **chosen, none measured**, which is the weakest grade `effort-allocation.md` recognises. `state/calibration.md` harvests one row per closed ledger from numbers already recorded, so the constants become knowable without inventing telemetry. **Nothing can close this but real runs** |
| **`.claude/rules/` carries ~24k words, auto-loaded unconditionally** | Recorded | Measured, not estimated: 2,071 lines across 18 files enter every session before the GD types. ~650 of them are C# client style rules a router, `qa-lead` or `producer` never needs — the `Applies to:` headers are documentation, not a loading mechanism. §10 cut the `orchestration.md`/`orchestrator.md` duplication; the rest needs a scoping decision that is the GD's, not a silent restructure |
| **Five files exceeded the 200-line cap** | Settled | Closed in §9 by promotion into `workflows/references/`, not by compressing prose. `.claude/rules/` still exceeds it (`execution-loop.md` 279, `task-classification.md` 214 as committed) — out of scope for this round, and recorded here rather than silently fixed |
| **No agent may rank an architecture direction** | Open | §13 found it and wrote it down rather than resolving it. A `design` question is `advisor`'s and the GD's by right; an `architecture` question reaches the same loop, where nothing is permitted to say which option fits this codebase. Closing it means either a `Recommended direction:` field on `technical-architect` for `architecture`-classified questions, or accepting the mode-3 escape as sufficient. **A philosophy decision, not a defect fix** |
| **Enforcement is advisory only** | Partly settled | This row said "reopen only when a miss supplies the evidence". A miss did: four self-describing counts had drifted and two cross-references pointed at blank lines, all found by audit rather than by any check. `tools/verify-workflow-layer.ps1` and `/verify-workflow-layer` close the **self-description** half at **107** machine-checked claims, with **21 negative tests** behind the router round's seven — 19 planted defects all failing, 2 must-still-PASS controls, 6 restores, output preserved to a log — 52 structural, then two semantic routing checks, one more per promoted reference, in §15 two more (every agents table must declare `Produces` as its third column and fill it — the property the custody check silently depends on — and no consuming file may restate the gate ask as the orchestrator asking the GD), and in the `change-request.md` round the custody check's scope reaching all six pipelines. The semantic checks are the only part that has ever caught a *behavioural* defect, and each round has caught at least one in its own edits. A `PreToolUse` hook blocking a dispatch that skips the router stays **Deferred** — still no evidence of that miss |
| **The Implementation Note's `Deliberately out of scope` is a proxy** | Deferred | Per `.claude/rules/implementation-note.md`: an agent that sets a nearby problem aside may record it under `Assumptions` and never return `Routed to:`, so the field can be silently empty. Closing it means adding a field to seven agent envelopes — declined until a real round trip proves it worth it |
| **Legacy roster doc deleted** | Recorded | `.claude/docs/TEAM_STRUCTURE.md` was removed once its §6 criteria reached `change-request.md` — the only content nothing else carried. Recover with `git checkout a33f02b -- .claude/docs/TEAM_STRUCTURE.md` if something turns out to have been missed |
| **`git-expert` and `ci-cd-engineer` were reachable only in mode 3** | Settled | Both now have a step-0 lane row, and the router round corrected what the rows said about themselves: sizing landing on one agent is **mode 1**, not the GD's mode-3 override, so the rows no longer claim a mode the GD alone can enter. `orchestrator-direct-dispatch.md` had carried *"neither is reached by sizing"* for two rounds after the rows were added — stale in the file a router reads **on a return**, which is the worst place for it. Both debt rows above were the other half of that staleness and are replaced by this one |
| **Three pipelines are fixed and only partly executed** | Open | `feature-intake.md` and `research-decision.md` closed all 17 of their findings and score **8.9** each — scored by the author of the fixes, which is **E0**. Most of what closed them is a destination: a ledger row, a carry table, a routing row. **No ledger has ever been instantiated**, so every one of those destinations has received nothing. The `rd-engineer → Done → cto` path, step 3's build-and-device split, the standalone acceptance gate's conditional firing and the re-typed `Open design question:` field are all **written and unrun** — and that last one replaces a field a live run falsified with one no run has touched. Closing it needs a real Unity project; this repo has none |
| **The custody class is written down, not machine-checked** | Settled for all six | Seventeen findings across two pipelines reduced to four classes, and the largest — *an agent produces something no pipeline row receives* — was closed **instance by instance**. `verify-workflow-layer.ps1` passed 78/78 with twelve of them live. Fix **J** closed the class: (1) every artifact a pipeline declares under `Produces` must be named in at least one entry or hand-back row; (2) every `Routed to:` value an agent file instructs an agent to return must have a matching routing row in each pipeline that dispatches it. §15 found the check itself could be **blind** — one pipeline's third column was not `Produces`, so it passed while six deliverables went unreceived — and asserted that column too. The `change-request.md` round extended scope to all six and found the last residual weakness: check (1) does a case-insensitive **substring** match, so a destination already mentioned elsewhere in the same routing section (`gd`, or an agent named for an unrelated row) can pass without a row of its own — confirmed live against `producer`'s two destinations in `change-request.md`. Tightening it to require the destination inside a row naming the dispatching agent is recorded as the next fix, not yet made |
| **Class A/B does not measure destructive power** | Recorded | The two classes derive from `Write`/`Edit` in `tools:`, which `git-expert` breaks either way: with only `Bash` it would file as **A — leaves no source** while holding `git reset --hard`, and `Write`/`Edit` files it as B for reasons unrelated to that risk. It is classed B because its `.gitattributes`/`.gitignore` writes are genuinely reviewable config. A classifier that counts git's blast radius would need a third axis — not worth adding for one agent |

## Authoring order

Pipeline 1 ✅ → 2 ✅ → 3 ✅ → 4 ✅ → 5 ✅ → `change-request.md` ✅ → orchestrator ✅. Every file is written
and all seven are GD-approved; rows **5.14–5.15** and **7.17–7.21** are still awaiting review.

**The workflow layer is complete, and now has ignition.** `.claude/rules/orchestration.md` is the only
piece loaded automatically — without it the other seven files take effect only when something reads them,
which is why the layer could be finished and still never run.
