# GD Touchpoints — the registry

Every point where the GD is asked, approves, is told, summons, customizes — and every point where asking is
**forbidden**. This is the behaviour contract of the workflow layer: a rewrite may change how a pipeline gets
somewhere, never which of these fire. Each ID is cited by its owner file; `tools/verify-workflow-layer.ps1`
fails on an ID that is duplicated, uncited by its owner, or cited without existing here.

Types: **ask** (a question the GD answers) · **approve** (a checkpoint) · **notice** (told, nothing waits) ·
**summon** (only the GD can start it) · **customize** (the GD's standing control) · **no-ask** (asking here is
a defect).

**Every ask and every approve is put to the GD as multiple choice (G19)** — never as a question in chat prose
the GD has to answer by typing. A notice is stated, not asked.

## Everywhere — owned by `orchestrator.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G1** | notice | Every input sized at `orchestrator.md` step 0 | The lane picked, in one line, so the GD can redirect. The tier too at A3+, or when an unexpected axis set it | The GD redirects at no cost |
| **G2** | customize | The GD names a pipeline, an entry, or an `agent-id` | Modes 2 and 3 — the GD's cost override. Exactly that runs; review debt is recorded, nothing is blocked | — |
| **G3** | no-ask | Choosing the mode | Never ask which mode; infer it from what the GD named, then state it (G1) | — |
| **G4** | notice | A design flaw surfaces, from any agent, at any step (I5) | To the GD **immediately** — never queued behind the work, never re-filed as an ordinary defect | The GD decides; the work does not route around it |
| **G5** | notice | A return carries `Config required:`, `Risks flagged:` or `Store policy addressed:` — on any status | Forwarded to the GD; a `Done` can still need them | — |
| **G6** | ask | A return is `Blocked` on an input only the GD holds | Exactly the input named, and what it blocks. After two identical `Blocked` (B17): reported as unresolved — what was asked, of whom, what it blocks | Unresolved stays stated, never guessed |
| **G7** | notice | Any bound in `references/bounds.md` is reached | A Continuation Debt Record: verdicts, causes, known non-solutions, safe resume point, next best action. The GD decides re-spec, cut or drop | — |
| **G8** | customize | Any bound | **No cap overrides the GD.** The GD may direct another round; the cost is stated first and the direction recorded | — |
| **G9** | approve | A gap is to be accepted, or a requirement waived | Only the GD accepts; the waiver is explicit and informed (cost stated, then reaffirmed). Written to known limitations / `DEBT.md` **before** closure (I6). Fabricated evidence and a false verification claim are beyond any waiver | Not accepted → it stays an open gap |
| **G10** | customize | The GD drops or supersedes work | The ledger is marked `Abandoned`, with why and the last verified state | — |
| **G11** | customize | Any direction of the layer | Never enforce by blocking: state the cost, then do what the GD asked | — |
| **G12** | customize | The GD states a budget, platform or constraint | It is an **H** requirement unless the GD says otherwise (`task-classification.md`) | — |
| **G19** | customize | Any **ask** or **approve**, from any file, in any mode | Put through the `AskUserQuestion` tool, never in chat prose: **single-select** when the answers exclude each other (a checkpoint's approve / reject as defect / reject as change request; a severity), **multi-select** when they are independent (which gates to run; which coverage to authorise). 2–4 concrete options, each with what it costs or causes; the recommended one first and marked `(Khuyến nghị)`; up to 4 related questions batched in one call. Free text only through the tool's own "Other" — even a `Blocked` input (G6) is offered as choices (supply it now / skip that part / stop) with the value typed in "Other". Question text in Vietnamese | The GD's choice, or their "Other" text, is the answer — recorded like any other |

## `orchestrator.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G13** | ask | A direct or mode-3 dispatch wrote source, outside any pipeline and outside the gated-direct lane (G14) | The gate offer per G50 — the ask is owed, the gate is not | Recorded `declined` in `project-state.md`; while unasked it is `unoffered` |
| **G14** | ask | A gated-direct submission returns from its one agent | Both review gates, in parallel — **recommend yes**, saying why consequence alone routed it here | Recorded `declined`; the Implementation Note goes to the GD |
| **G15** | ask | A direct-lane or mode-3 change owes a measured claim at V3/V4 | The measurement as its own run — `qa-pipeline.md` **E4** | Recorded as a gap; never a number quoted from the agent that made the change |
| **G16** | summon | A platform build, or more than one Editor instance (including a second instance to parallelise the fan-out) | Only on an explicit GD request in the prompt — never pipeline state, readiness or another agent's confidence | Nothing is built; coverage that needed it is a gap |
| **G17** | ask | A lock is suspect and steps 1–2 of the I9 reclaim did not answer | The holder, the claim time, and what is waiting | The lock stays held |
| **G18** | customize | A standalone run (mode 2) | The GD supplies what the upstream would have; the result returns to the GD and hands on to nothing. Chaining by hand is mode 2 twice | — |

## `references/optional-gates.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G50** | ask | Every review or QA offer, wherever it fires | What was built and the paths; the tier and the axes that set it; the cost of running; the cost of skipping, named concretely. **Recommend, then defer** — one line, never repeated. At A4+, declining QA says **in those words** that the assurance check on claimed verification is declined too | A `declined` row in `project-state.md` (I2); re-offered once per later boundary (B18), never twice in a run |

## `feature-intake.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G20** | no-ask | Classification at step 2 | Never ask the GD to confirm the tier first — it is stated (G1); the checkpoints are the check | — |
| **G21** | approve | **CP1** — D4–D5, or U3 at any D | Each round the GD picks an option by name (the pipeline expands it for `critic`); only the GD ends the loop; at CP1 the GD locks the direction and the risks accepted | Back into the loop, within B2; non-convergence at the cap goes to the GD (G7) |
| **G22** | ask | `advisor` was asked to choose for the GD | Return to the GD, and offer `critic` on whichever option they lean toward | — |
| **G23** | customize | Before locking CP1 | The GD may ask `technical-architect` directly (mode 3) for an engineering recommendation; `advisor`'s output is never read as a ranking | — |
| **G24** | approve | **CP2** — D3–D5 | The Tech Spec, with `Assumptions:`, inherited decisions and `critic`'s open findings. On the **first** rejection, ask which kind: the spec misread the request (revise), or the direction is now wrong (reopen CP1 via **E5**) | Within B11; the third goes to CP1 if available, else to the GD with all three |
| **G25** | notice | Step 5 skipped the research branch | The package, API or system named as covering it — shown at CP2 | — |

## `research-decision.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G30** | summon | The GD asks for research (**E5**) or a spike (**E6**) with no feature | Asking for a spike *is* the summon `rd-engineer` requires | — |
| **G31** | ask | The spike gate — before `rd-engineer` is ever dispatched | The specific question, the decision waiting on it, the threshold, the hardware, and the build when the measurement is on a device (G16). Never a recommendation converted into a dispatch; never re-asked once answered | `cto` decides provisionally and names what would confirm it |
| **G32** | ask | `cto` (or anything) returns `Needs-decision`, `Routed to: gd`; or a question is still open after the one measure-and-confirm cycle (B7) | The product call, framed in product terms | — |
| **G33** | approve | A standalone result sets a standard, makes a provisional decision, or commits money | The standard, the decision, the cost | Standard rejected → not recorded, terminal. Decision rejected → back to `cto` once (B8), then the GD decides directly |
| **G34** | customize | Research needs to know whether paid or closed-source options are acceptable | The GD's preference; unstated → paid assumed allowed, its cost flagged, a free maintained option ranked above it at equal fit | — |

## `feature-development.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G40** | ask | The Core contract has returned, before the fan-out builds on it | G50, with the Core's own `Assumptions and known limitations:` as the concrete cost of skipping. The one review ask per feature | Review debt; the fan-out proceeds against the unreviewed contract |
| **G41** | notice | D4–D5: the Core public contract is ready | The contract reaches the GD; nothing waits on it | — |
| **G42** | ask | Implementation is complete | QA per G50 — and review too, if G40 never fired | Debt recorded; CP4 still fires |
| **G43** | notice | The classification moved during development | One line: from what, to what, and why; work verified to the old floor is named as such | — |
| **G44** | ask | Backend track on and the netcode foundation genuinely unset | Ask once, before anything routes to `cto` | Unanswered → `research-decision.md` with a candidate set |
| **G45** | notice | Third-party content — `.unitypackage`, Asset Store import, vendored DLL — is about to land | The supply-chain pre-gate runs **before** it lands, whatever the GD answered about review; say so in the gate ask. Not declinable (`security.md`) | — |
| **G46** | no-ask | Implementing agent ⇄ tech lead escalation | Silent to the GD; it surfaces only as a `Blocked`, at CP3, or as G7 | — |
| **G47** | customize | The GD reports a defect | Enters **E3** at zero strikes. If the spec was right and the GD now wants something else, it is a change request (G70) | — |

## `review-pipeline.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G51** | approve | **CP3** — D3–D5, once per feature, only when review ran; merged into CP4 at D1–D2 | `Built:`, `Matches spec intent:` with every drift named, `Known limitations:` | Drift → **E3**; the spec itself wrong → change request (G70). Within B12 |
| **G52** | ask | Both review gates have cleared | QA per G50 | QA debt; CP4 still fires |
| **G53** | no-ask | A gate rejects a submission | Rejections go to the author silently — the GD hears only of a design flaw (G4), a `cto` remediation, or a reached bound (G7) | — |
| **G54** | ask | A credential-shaped value is `Needs Confirmation` | Asked in order: `tech-lead-sdk-platform`, the author, **then the GD** — only they can say whether a real key exists | Nobody can name a source → treated as a secret, one strike (B9) |
| **G55** | notice | A standalone audit (**E2**) finishes | Findings as a report — no author, no strike, no CP3 | — |

## `qa-pipeline.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G60** | approve | **CP4** — every shape, always, whether or not any gate ran | What was built, the gates that ran or were declined, the assurance verdict or its stated absence, every gap. Three answers: approve, reject as defect, reject as change request | Defect → **E3** within B13; change request → `change-request.md` **E2**, no counter moves |
| **G61** | ask | Device coverage needs a build that does not exist, or a fix needs a rebuilt one | Asked up front, before dispatching device agents (G16) | That coverage is a gap from the outset |
| **G62** | ask | A `qa-automation-engineer` suite has been written | Review of the test code per G50, offered **before** its results are used as sign-off evidence; the ask says whether the suite has run | Review debt; results still reported, marked as unreviewed test code |
| **G63** | notice | A verification claim is contradicted, or `Acceptance: FAIL` lands on the Implementation Note's own claim | To the GD now — beyond any waiver | — |
| **G64** | approve | `CONDITIONAL PASS`, or an exit criterion that cannot be met | Only the GD accepts it, at CP4 (G9) | It stays a gap |
| **G65** | notice | `qa-lead` returns `Routed to: gd`, in either mode | Acted on immediately | — |

## `change-request.md`

| ID | Type | When | Carries / rule | On no, or on reject |
|---|---|---|---|---|
| **G70** | customize | The GD changes an approved rule, GDD passage or requirement — or at CP4 wants something else | Entered in the GD's own words; new work against the spec halts first | — |
| **G71** | no-ask | Severity classification | Never ask the GD to confirm the severity; the reopened checkpoint is the check | — |
| **G72** | notice | **Minor** severity | Reaches the GD in the next status report; the only severity the GD never approves | — |
| **G73** | approve | **Moderate** / **Major** | Moderate reopens CP2 (G24); Major reopens CP1 (G21), carrying the risks already accepted | — |
| **G74** | ask | The rework is done | Its own gate offer per G50 — a new boundary, so asking again is not nagging | Debt recorded |

## Rules

| ID | Type | Owner | Rule |
|---|---|---|---|
| **G80** | customize | `rules/effort-allocation.md` | Scores are produced only when the GD asks, or a rule requires one |
| **G81** | notice | `rules/execution-loop.md` | A mistake the GD confirms becomes an error-prevention memory |
| **G82** | notice | `rules/implementation-note.md` | Where no gate ran, the GD reads `Verification done:` against the floor at CP4 |

## Outside this registry's IDs, listed so nothing is forgotten

These live in files this layer does not own; they keep their own wording.

- `rules/language-and-comments.md` — the final reply to the GD is in Vietnamese.
- `commands/investigate-device-crash.md` — disambiguate the device or the app when more than one matches.
- `commands/plan-test-coverage.md`, `commands/review-code-risks.md` — ask for the scope when it is missing.
- `commands/resolve-merge-conflicts.md` — ask before committing or `merge --continue`.
- `agents/git-expert.md` — a radius-3 operation needs authorization in the prompt, never inferred.
- `CLAUDE.md` — the project's own overrides table.
