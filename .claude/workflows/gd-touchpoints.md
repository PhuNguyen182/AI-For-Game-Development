# GD Touchpoints — the registry

Every point where the GD is asked, approves, is told, summons, customizes — and every point where asking is
**forbidden**. This is the behaviour contract of the workflow layer: a rewrite may change how a pipeline gets
somewhere, never which of these fire. Each ID is cited by its owner file; `tools/verify-workflow-layer.ps1` fails
on an ID that is duplicated, uncited by its owner, or cited without existing here.

Types: **ask** (a question the GD answers) · **approve** (a checkpoint) · **notice** (told, nothing waits) ·
**summon** (only the GD can start it) · **customize** (the GD's standing control) · **no-ask** (asking here is a
defect).

**Every ask and every approve is put to the GD as multiple choice (G19)** — never as a question in chat prose the
GD has to answer by typing. A notice is stated, not asked.

## Everywhere — owned by `orchestrator.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G1** | notice | Every input sized at `orchestrator.md` step 0 | The lane picked, in one line, so the GD can redirect. The tier too at A3+, or when an unexpected axis set it | The GD redirects at no cost |
| **G2** | customize | The GD names a pipeline, an entry, or an `agent-id` | Modes 2 and 3 — the GD's cost override. Exactly that runs; review debt is recorded, nothing is blocked | — |
| **G3** | no-ask | Choosing the mode | Never ask which mode; infer it from what the GD named, then state it (G1) | — |
| **G4** | ask | A design flaw surfaces, from any agent, at any step (I5) | To the GD **immediately**, as a ruling on its bug (`Escalated`): a defect after all (→ `Open`, **E3**); accepted as is (`Won't fix`, G9); or the design changes (`As designed`, with a change request, G70). Never queued behind the work, never re-filed as an ordinary defect | Unruled → it stays `Escalated`; the work does not route around it, and the feature cannot close (G60) |
| **G5** | notice | A return carries `Config required:`, `Risks flagged:` or `Store policy addressed:` — on any status | Forwarded to the GD; a `Done` can still need them | — |
| **G6** | ask | A return is `Blocked` on an input only the GD holds | Exactly the input named, and what it blocks. After two identical `Blocked` (B17): reported as unresolved — what was asked, of whom, what it blocks | Unresolved stays stated, never guessed |
| **G7** | ask | Any bound in `references/bounds.md` is reached — except B4, and B6 on an unattached bug — both escalate on their own row | A Continuation Debt Record: verdicts, causes, known non-solutions, safe resume point, next best action. Options fit the stop: before CP1, lock the direction with the risk accepted (G21); with a spec, re-spec through a change request (G70); for a stuck bug, `Won't fix` (G9) — the only "drop" a bug on a closed feature takes; everywhere else, another round (G8) or drop the work (G10) | Unanswered → the work stays stopped; nothing re-dispatches the same brief |
| **G8** | customize | Any bound | **No cap overrides the GD.** The GD may direct another round; the cost is stated first and the direction recorded | — |
| **G9** | approve | A gap is to be accepted, or a requirement waived | Only the GD accepts, by selecting an option whose text states the cost; waiving an **H** requirement adds one confirming question — the reaffirmation (`effort-allocation.md`). A declined gate is debt, not a waiver. Written to known limitations / `DEBT.md` **before** closure (I6). Fabricated evidence and a false verification claim are beyond any waiver | Not accepted → it stays an open gap |
| **G10** | customize | The GD drops or supersedes work | The ledger is marked `Abandoned`, with why and the last verified state; its unsettled bugs become `Won't fix — abandoned with the feature` | — |
| **G11** | customize | Any direction of the layer | Never enforce by blocking: state the cost, then do what the GD asked. It never reaches `security.md` or the supply-chain pre-gate (G45): there the GD may drop the work, never order the violation | — |
| **G12** | customize | The GD states a budget, platform or constraint | It is an **H** requirement unless the GD says otherwise (`task-classification.md`) | — |
| **G19** | customize | Any **ask** or **approve**, from any file, in any mode | Put through the `AskUserQuestion` tool, never in chat prose: **single-select** when the answers exclude each other (a checkpoint's approve / reject as defect / reject as change request; a severity), **multi-select** when they are independent (which gates to run; which coverage to authorise). 2–4 concrete options, each with what it costs or causes; the recommended one first and marked `(Khuyến nghị)` — except the Advisor⇄Critic loop's options, which nothing ranks (G22); up to 4 related questions batched in one call. Free text only through the tool's own "Other" — even a `Blocked` input (G6) is offered as choices (supply it now / skip that part / stop) with the value typed in "Other". Question text in Vietnamese | The GD's choice, or their "Other" text, is the answer — recorded like any other |

## `orchestrator.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G13** | ask | Source (`orchestration.md` → *Terms*) was written outside any pipeline and outside the gated-direct lane (G14) — by a direct or mode-3 dispatch, or by you; or any direct fix, source or not, to a recorded unattached bug. In a mode-3 chain, as each source-writing agent returns | The gate offer per G50 — the ask is owed, the gate is not. When the source fixes an unattached bug, QA verification (`qa-pipeline.md` **E4**) and `Accepted unverified` (G9) are offered beside it | Recorded `declined` in `project-state.md` from A3 — an A1–A2 decline is stated in the reply (B18); while unasked it is `unoffered` |
| **G14** | ask | A gated-direct submission returns from its one agent | Both review gates, in parallel — **recommend yes**, saying why consequence alone routed it here — and `assurance-evaluator` after them, the lane being A3+; declining it is said in G50's words. A fix to an unattached bug adds G13's verification offer | Recorded `declined`; the Implementation Note goes to the GD |
| **G15** | ask | A direct-lane or mode-3 change owes a measured claim at V3/V4 | The measurement as its own run — `qa-pipeline.md` **E4** | Recorded as a gap; never a number quoted from the agent that made the change |
| **G16** | summon | A platform build, or more than one Editor instance (including a second instance to parallelise the fan-out) | Only on an explicit GD request in the prompt — never pipeline state, readiness or another agent's confidence | Nothing is built; coverage that needed it is a gap |
| **G17** | ask | A lock is suspect and another session's — step 3 of the I9 reclaim (`state/README.md` → *Locks*) | The holder, the claim time, what the resource check showed, and what is waiting | The lock stays held; the waiting work is reported `Blocked` on it (G6) and resumes when the GD frees it |
| **G18** | customize | A standalone run (mode 2) | The GD supplies what the upstream would have; the result returns to the GD and hands on to nothing. Chaining by hand is mode 2 twice | — |

## `references/optional-gates.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G50** | ask | Every review or QA offer, wherever it fires | What was built and the paths; the tier and the axes that set it; the cost of running; the cost of skipping, named concretely. **Recommend, then defer** — one line, never repeated. At A3+, declining QA says **in those words** that the assurance check on claimed verification is declined too | A `declined` row in `project-state.md` from A3 (I2); re-offered once per later boundary (B18), never twice at the same one; a gate already authorised is never asked again |

## `feature-intake.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G20** | no-ask | Classification at step 2 | Never ask the GD to confirm the tier first — it is stated (G1); the checkpoints are the check. The one exception is the GD's own request asking to approve it first: then it is asked (G11) | — |
| **G21** | approve | **CP1** — D4–D5, or U3 at any D | Each round the GD picks an option by name (the pipeline expands it for `critic`); only the GD ends the loop; at CP1 the GD locks the direction and the risks accepted | Back into the loop, within B2; non-convergence at the cap goes to the GD (G7) |
| **G22** | ask | `advisor` was asked to choose for the GD — or the GD asks you to pick an option | The options unranked, no `(Khuyến nghị)`: the GD picks one for `critic`, or takes G23 — `technical-architect`'s engineering recommendation — as one of the choices | `critic` declined → the GD decides on the option alone (G21); the round counts as run (B2) |
| **G23** | customize | Before locking CP1 | The GD may ask `technical-architect` directly (mode 3) for an engineering recommendation; `advisor`'s output is never read as a ranking | — |
| **G24** | approve | **CP2** — D3–D5 | The Tech Spec, with `Assumptions:`, inherited decisions and `critic`'s open findings. On the **first** rejection, ask which kind: the spec misread the request (revise), or the direction is now wrong (reopen CP1 via **E5**) | Within B11; the third goes to CP1 if available, else to the GD with all three |
| **G25** | notice | Step 5 skipped the research branch | The package, API or system named as covering it — shown at CP2 | — |
| **G26** | ask | The track is unknown — `CLAUDE.md` states none and the request does not say — and the work could be multiplayer-relevant; at intake step 1, or before any dispatch that needs it | Client-only, or client + multiplayer — asked once per project; the answer is the project's default (`project-state.md` → `Track:`) until `CLAUDE.md` states one. A request that says it itself ("online co-op") is the answer — recorded there the same way, not asked | Unanswered → client-only, stated as an assumption (G1), never silently. Work that cannot be multiplayer-relevant runs client-only without asking, stated the same way |
| **G27** | ask | A `design` question where no Advisor⇄Critic loop runs — intake at D1–D3 (step 2, or the step-6 spec), a change request's classification, or a gated-direct fix needing one undecided value (an economy number) |  The question, the options the line names, and what each costs; one question per line, batched (G19) | Unanswered → the line stays open and step 6 does not start on a guessed design (G6) |

## `research-decision.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G30** | summon | The GD asks for research (**E5**) or a spike (**E6**) with no feature | Asking for a spike *is* the summon `rd-engineer` requires | — |
| **G31** | ask | The spike gate — before `rd-engineer` is ever dispatched. At **E6** the GD's request is the gate, and only what it left out — threshold, baseline, and the build when the measurement is on a device — is asked, once, batched | The specific question, the decision waiting on it, the threshold, the hardware, and the build when the measurement is on a device (G16). Never a recommendation converted into a dispatch; never re-asked once answered | `cto` decides provisionally and names what would confirm it |
| **G32** | ask | `cto` (or anything) returns `Needs-decision`, `Routed to: gd`; or a question is still open after the one measure-and-confirm cycle (B7) | The product call, framed in product terms | Deferred → recorded as open (the ledger's `Research:`, or **Standalone decisions**); U stays unresolved and the work waiting on it is `Blocked` on the GD (G6) — never carried forward on a guessed answer |
| **G33** | approve | A standalone result sets a standard, makes a provisional decision, or commits money | The standard, the decision, the cost | Standard rejected → no ADR, terminal; the refusal is recorded in `project-state.md` → *Standalone decisions*, so no later run re-derives it. Decision rejected → back to `cto` once (B8), then the GD decides directly |
| **G34** | customize | Research needs to know whether paid or closed-source options are acceptable | The GD's preference; unstated → paid assumed allowed, its cost flagged, a free maintained option ranked above it at equal fit | — |

## `feature-development.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G40** | ask | The Core contract has returned, before the fan-out builds on it | G50, with the Core's own `Assumptions and known limitations:` as the concrete cost of skipping. Two answers: review the whole feature — the Core now, each later submission as it lands — or none now | Review debt; the fan-out proceeds against the unreviewed contract, and G42 offers review again, of everything |
| **G41** | notice | D4–D5: the Core public contract is ready | The contract reaches the GD; nothing waits on it | — |
| **G42** | ask | Implementation is complete, and review was not authorised at G40 — declined there, or never asked because the feature entered at **E2** (D1–D2); and again, review only, when a defect fix lands on code whose review was declined (B18) | Review of every submission and QA, per G50, in one multi-select — only what the ledger's `Gates:` leaves open; the feature's QA ask; a later defect fix's verification is a new boundary (B18) | Debt recorded; CP4 still fires |
| **G43** | notice | The classification moved during development | One line: from what, to what, and why; work verified to the old floor is named as such | — |
| **G44** | ask | Track client + multiplayer and the netcode foundation genuinely unset — first met at `feature-intake.md` step 2 as a `technology` line, or here at step 5 | Ask once per project, before anything routes to research or `cto`; a foundation the GD names skips research for it | Unanswered → `research-decision.md` with a candidate set |
| **G45** | notice | Third-party content — `.unitypackage`, Asset Store import, vendored DLL — is about to land | The supply-chain pre-gate runs **before** it lands, whatever the GD answered about review; say so in the gate ask. Not declinable (`security.md`) | — |
| **G46** | no-ask | Implementing agent ⇄ tech lead escalation | Silent to the GD; it surfaces only as a `Blocked`, at CP3, or as G7 | — |
| **G47** | customize | The GD reports a defect | Opens a bug in the bug log (`Opened by: gd`). On a feature with a ledger it enters **E3**, its fix a new submission. With no ledger: redoing what a direct reply just delivered is more direct work, no record; a defect in code no ledger holds is an unattached bug, its fix sized at step 0 and settled by the offer that ends it (G13, G14). If the spec was right and the GD now wants something else, it is a change request (G70) | — |

## `review-pipeline.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G51** | approve | **CP3** — D3–D5, once per feature, only when review ran; merged into CP4 at D1–D2 | `Built:`, `Matches spec intent:` with every drift named, `Known limitations:` | Drift → **E3**; the spec itself wrong → change request (G70). Within B12 |
| **G52** | ask | G40 authorised review, and every submission has cleared both gates | QA per G50 — the feature's QA ask | QA debt; CP4 still fires |
| **G53** | no-ask | A gate rejects a submission | Rejections go to the author silently — the GD hears only of a design flaw (G4), a `cto` remediation, or a reached bound (G7) | — |
| **G54** | ask | A credential-shaped value is `Needs Confirmation` | Asked in order: `tech-lead-sdk-platform`, the author, **then the GD** — only they can say whether a real key exists | Nobody can name a source → treated as a secret, one strike (B9) |
| **G55** | notice | A standalone audit (**E2**) finishes | Findings as a report — no author, no strike, no CP3 | — |

## `qa-pipeline.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G60** | approve | **CP4** — every feature with a ledger, every shape, whether or not any gate ran. Ledger-less direct work closes at the reply instead (`orchestrator.md` → *Direct dispatch*) | What was built, the gates that ran or were declined, the assurance verdict or its stated absence, the ledger's *Open gaps*, and the bug summary. **Every unsettled bug is put to the GD before the closing question**, batched within G19's limits: accepting one — `Won't fix`, `Accepted unverified` — is always an explicit selection, never what silence means; an `Escalated` bug takes G4's ruling. A bug not accepted is fixed now (**E3**) or verified (QA **E3**) — where QA was declined, the option text says it authorises that verification run. Then the closing question: approve, reject as defect, reject as change request. A feature closes only with no bug unsettled (`defect-reporting.md`) | Defect → **E3** within B13; change request → `change-request.md` **E2**, not a CP4 rejection. A bug sent round its loop brings CP4 back — not a re-ask. An `Escalated` bug still unruled at approve gets one follow-up (bounds rule 4); still unruled, the feature waits at `Position:` CP4, like a `Blocked` (G6) — never closed by default |
| **G61** | ask | Device coverage needs a build that does not exist, or a fix needs a rebuilt one | Asked up front, before dispatching device agents (G16) | That coverage is a gap from the outset |
| **G62** | ask | A `qa-automation-engineer` suite has been written | Review of the test code per G50, offered **before** its results are used as sign-off evidence; the ask says whether the suite has run | Review debt; results still reported, marked as unreviewed test code |
| **G63** | ask | An assurance `FAIL`, or any verification claim contradicted | To the GD now, as a ruling: return the work to its owner (**E3**), or drop it (G10). Never an accepted gap — an integrity failure is beyond any waiver | Unruled → the work waits; nothing closes over a standing `FAIL` |
| **G64** | approve | `CONDITIONAL PASS`, or an exit criterion that cannot be met | Only the GD accepts it, at CP4 (G9) | It stays a gap |
| **G65** | notice | `qa-lead` returns `Routed to: gd`, in either mode | Acted on immediately | — |
| **G66** | ask | An **E4** run ends with a bug unsettled — no CP4 will rule on it | Per bug (G19): fix now, through the lane its size fits; `Won't fix` (G9); or leave it open. An `Escalated` one takes G4's ruling | Leave open is a recorded answer: the bug stays `Open` in `bug-log.md`, and the next lane that changes its code carries it |

## `change-request.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G70** | customize | The GD changes an approved rule, GDD passage or requirement — or at CP4 wants something else | Entered in the GD's own words; new work against the spec halts first | — |
| **G71** | no-ask | Severity classification | Never ask the GD to confirm the severity; the reopened checkpoint is the check | — |
| **G72** | notice | **Minor** severity | Reaches the GD in the next status report — or at once, in one line, when none is due (no rework follows, or the feature is closed); the only severity the GD never approves | — |
| **G73** | approve | **Moderate** / **Major** | Moderate reopens CP2 (G24); Major reopens CP1 (G21), carrying the risks already accepted | The reopened checkpoint's own path — G24's at CP2, G21's at CP1. Revised D1–D2 notes rejected → the architect revises them, within B11, or the GD drops the change. Rework waits on the approval |
| **G74** | ask | The rework is done | Its own gate offer per G50 for what the ledger's `Gates:` leaves open — a new boundary, so asking again is not nagging. A gate authorised for the whole feature runs on the rework as it lands, unasked; nothing left open → no ask. One multi-select with G52 when both fall due | Debt recorded |

## Rules

| ID | Type | Owner | Rule |
|---|---|---|---|
| **G80** | customize | `rules/effort-allocation.md` | Scores are produced only when the GD asks, or a rule requires one |
| **G81** | notice | `rules/execution-loop.md` | A mistake the GD confirms becomes an error-prevention memory |
| **G82** | notice | `rules/implementation-note.md` | Where no gate ran, the GD reads `Verification done:` against the floor at CP4 — or in the reply that closes ledger-less work |

## Outside this registry's IDs, listed so nothing is forgotten

These live in files this layer does not own; they keep their own wording.

- `rules/language-and-comments.md` — the final reply to the GD is in Vietnamese.
- `commands/investigate-device-crash.md` — disambiguate the device or the app when more than one matches.
- `commands/plan-test-coverage.md`, `commands/review-code-risks.md` — ask for the scope when it is missing.
- `commands/resolve-merge-conflicts.md` — ask before committing or `merge --continue`.
- `agents/git-expert.md` — a radius-3 operation needs authorization in the prompt, never inferred.
- `CLAUDE.md` — the project's own overrides table.
