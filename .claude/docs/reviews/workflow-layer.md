# Workflow Layer — Assessment (working note)

> **Historical record — read [`README.md`](README.md) first.** This is the log of one review round, not a
> specification. The layer that runs is `.claude/workflows/`; the current state of it is
> `.claude/workflows/workflow-checklist.md`. **Two things here go stale by design**: every number about the
> layer (verifier claim counts, "still unreviewed" lists, "nothing is committed") is as of this round, and
> **later parts supersede earlier ones** — the last score in the file is the one that stands.

> **Status: scratch.** A working record of the architecture review held on 2026-09-17, kept so the findings
> survive the session that produced them. It is not a rule, not a standard, and nothing in the layer points
> at it. Delete it once its findings have either been acted on or recorded somewhere durable.

**Scope.** The orchestrator, the six pipelines, the 21 reference files, the state layer and its three
templates — the whole of `.claude/workflows/` plus `.claude/rules/orchestration.md`.

**Deliberately excluded: `feature-intake.md`.** That pipeline was taken apart separately and in far more
detail, and it is still under discussion. Its findings are not folded in here, and the score below covers
the layer as a whole rather than that file specifically.

---

## Method and evidence base

| What was done | Evidence level |
|---|---|
| Read every file in `.claude/workflows/` end to end — 3,169 lines across 35 files | E1 — direct inspection |
| Ran `tools/verify-workflow-layer.ps1` | **E2 — tool output: `OK 75 claims checked, every one holds`** |
| Read the 12 auto-loading files in `.claude/rules/` — 1,381 lines | E1 |
| Cross-checked pipeline claims against the agent contracts they cite | E1 |
| Inspected `.claude/settings.json` and `settings.local.json` for hooks | E2 |
| Checked for `CLAUDE.md`, `<state-root>` (`.workflow/`), and calibration data | E2 — filesystem |

Nothing here rests on an unverified claim. Where something could not be checked, it is stated as such.

---

## Score

| Axis | Score | Reason |
|---|---:|---|
| Architecture and separation of concerns | **9.0** | "One fact, one home" held rigorously; the promotion rule is clean and consistently applied |
| Failure-mode coverage | **9.0** | `loop-termination.md` bounds not just every loop but every *composition* of loops |
| Internal consistency | **8.5** | All 75 self-checks hold; one loose seam over gate-offer ownership (F6) |
| **Enforceability / mechanism** | **4.5** | The weakest axis. The layer is prose with no hooks behind it |
| Cost efficiency and proportionality | **7.0** | The direct and gated-direct lanes are a real fix; 1,381 always-loaded rule lines cut against it |
| Honesty about itself | **9.5** | `calibration.md` concedes every constant is E0 on the layer's own scale |
| **Operational readiness** | **3.5** | Never executed end to end, not once |

### **Overall: 7.5 / 10**

Split more honestly: **design 9.0 — operational reality 4.0.** This is the best-argued process document of
its kind I have read. It is also a system that has never met contact with a real run.

---

## What is genuinely excellent

**1. Separating `D` (shape) from `C/R/X` (depth).**
The most valuable idea in the layer. It cures the classic failure where "this matters" buys paperwork
instead of verification. `references/gated-direct-lane.md` is the concrete rung that makes it actionable —
consequence buys the gates, never the pipeline — and it is correct.

**2. `references/loop-termination.md`.**
Sixteen caps, nine of which exist only there because they are *compositions* of loops that were each bounded
individually and jointly were not. `Root-cause resets: 1/1`, shared across every loop that can reach
`technical-architect`, is the detail almost every system of this shape misses.

**3. Required inputs anchored to real `If absent` behaviour.**
Every carried-input row is keyed to what the receiving agent actually does when the field is missing, not to
what the author wished it would do. That is the line between a process document and an executable contract.

**4. Supporting strengths worth keeping.**
State moved out of `.claude/` with the right reason stated (framework vs. project). Optional gates with a
mandatory *ask* and a mandatory *record* is the correct resolution of "never block the GD" against "never let
unverified work look verified". `Read Verdict:, never Status:` is a small rule that prevents a large class of
misreads.

---

## Findings

Numbered so they can be referenced in later discussion. Severity is this note's judgment, not the layer's.

### F1 — Ignition is a single unenforced sentence

All 3,169 lines run only if the model reads `.claude/rules/orchestration.md` (71 lines, auto-loaded) and then
chooses to open `orchestrator.md`. **Verified: `.claude/settings.json` contains permission allowlists and
zero hooks. There is no `CLAUDE.md` at the project root.**

The paradox: `verify-workflow-layer.ps1` can check that the layer *describes itself accurately*, but nothing
can check that the layer *ran at all*. In a system whose central thesis is that an unchecked claim is E0,
this is a verification hole sitting at the very top.

### F2 — The state layer is a manual per-transition tax with no detector

"Write it, then dispatch. Never the other way round." A D4 feature has roughly 30–50 transitions, each one a
hand-edit to a Markdown table in `<feature-root>/LEDGER.md` and sometimes `<state-root>/project-state.md`.
There is no tool, no script, no template filler.

The failure mode is completely silent: the run proceeds normally, the counters simply drift, and **every cap
stops firing**. This is the highest-probability real-world failure in the design, and the layer has no way to
notice it. `verify-workflow-layer.ps1` checks that state is *absent* from `.claude/`; it cannot check that
state is *present and current* where it belongs.

### F3 — The two global locks are not locks

I3 (Editor) and I7 (device) live in `<state-root>/project-state.md` — a Markdown file with no atomicity. Two
sessions can both read "free" and both write "claimed". The I9 reclaim procedure handles a *stale* lock, not
a *race*.

`state/README.md` concedes the point — "a concurrent session on another machine is invisible from here" — and
routes to the GD. That is honest, and it is a mitigation rather than a lock. Calling it an invariant
overstates what the mechanism delivers; it is a convention.

### F4 — A read-cost asymmetry the layer created and has not finished paying

`rules/standards-index.md` correctly moved 756 lines of track standards out of always-loaded context. But
**1,381 lines of rules still load into every dispatch**, including `execution-loop.md` (279 lines) and
`commit-message.md` (88 lines) into agents such as `producer` and `researcher`, which never commit and never
iterate.

The file's own test — *"a rule you must obey before you know it exists is loaded; a standard you consult when
you reach its domain is read"* — would move at least three of those files. The argument that justified the
standards migration was not carried to its conclusion.

### F5 — Prose-to-mechanism ratio

Roughly 7,000 lines govern a system whose entire enforcement surface is one PowerShell verifier plus the
model's own compliance. `references/optional-gates.md` spends 126 lines to say "ask, then record the answer."
The writing is excellent; past some point more prose stops buying more compliance.

### F6 — The one loose ownership seam

`references/optional-gates.md` states that "the orchestrator asks the GD", but the ask actually fires from
*inside* `feature-development.md` step 1 (the Core contract) and `review-pipeline.md` step 6 (QA). Three files
each describe themselves as the asker.

It is not a contradiction in effect, but it is the single place the otherwise-exemplary "one fact, one home"
discipline slips — and it matters because the ask is the one thing declared never optional.

### F7 — "CP4 always fires" is load-bearing and rests on nothing

No mechanism makes it fire. A feature that simply stops being mentioned is precisely the failure CP4 exists
to prevent, and nothing detects it. The intended detector is the in-flight index in `project-state.md` —
which returns to F2.

---

## Verified facts behind the operational-readiness score

- `verify-workflow-layer.ps1` → **OK, 75 claims checked, every one holds.**
- `<state-root>` (`.workflow/`) **does not exist**. No feature has ever opened a ledger.
- `state/templates/calibration.md` exists as a template with **zero data rows**.
- `workflow-checklist.md` still carries `⬜ GD review` on items **12**, **8**, **5.14**, **5.14a**, **5.14b**
  and **5.15**.
- No hooks configured anywhere.

**Conclusion: this layer has never been executed end to end on a real feature.** Every constant in it — three
strikes, three Advisor/Critic rounds, the 2–5 attempt budget, the two-round QA bound — is exactly what
`state/README.md` already admits: *chosen, not measured*.

---

## Where this left off

`feature-intake.md` was reviewed in depth separately; its ten findings, the eight changes made against them
and the re-score afterwards are in **`feature-intake-update.md`**, beside this file. The remaining five
pipelines and the orchestrator have not had that treatment — the scores above are layer-level.

**Nothing in *this* note has been acted on.** F1–F7 all stand. The `feature-intake` work changed nine files
and moved the layer score not at all, which is itself the clearest evidence for F1 and F5: the two axes
holding this layer down are enforceability and operational readiness, and neither is reachable by editing
prose. One finding arrived after this note was written and belongs against **F5** — a routing defect that
spanned two pipelines and survived all 75 automated checks, because the verifier tests structural claims and
not semantic routing. It is recorded as I9 in the companion note.

---

## Continuation Debt Record — as of 2026-09-18

Per `.claude/rules/execution-loop.md`. This is the layer-level record; each pipeline's own note carries its
findings. The GD accepted **8.9** on the two finished pipelines and stated the bar is higher still, so this
is a waypoint, not a close.

**Status:** Partially complete.

**Objective.** Raise the workflow layer to a score of 9.0 or better, pipeline by pipeline as the GD
designates, fixing what each review finds.

**Attempts used / budget.** `feature-intake.md` 3 of 4 (read → run → fix). `research-decision.md` 2 of 4
(run → fix). Neither exhausted; both stopped because acceptance was reached, not because budget ran out.

**Unmet requirements.**

- Neither finished pipeline reaches 9.0 — both sit at **8.9**, and the GD wants better than 9.0.
- Five pipelines are unreviewed: `feature-development.md`, `review-pipeline.md`, `qa-pipeline.md`,
  `change-request.md`, `orchestrator.md`.
- The layer score is unchanged in the axes that bind it: **operational readiness** and **enforceability**.

**Best achieved result.** All 17 findings across the two pipelines closed. `verify-workflow-layer.ps1` at
**80 claims, all holding** — up from 78, and it caught a genuine error in this round's own edits. Both
pipeline files at 199 lines against the 200 cap. One new reference, four new ledger rows, one new
`project-state.md` section, one new bound registered in `loop-termination.md`.

**Last verified state.** Working tree committed at the end of this round; verifier green; no file over cap.

**Likely root cause of what remains.** Every remaining deduction traces to one fact: **nothing written has
been executed.** `<state-root>/.workflow/` does not exist, no ledger has ever been instantiated, and this
repository contains only the framework — no Unity project, no device. Prose cannot reach those axes, and no
amount of further editing will.

**What changed across attempts.** Reading scored `feature-intake.md` 9.0; running it scored 8.2 and produced
twelve defects careful reading had missed, two of them inside fixes written the round before. Running
`research-decision.md`'s standalone half moved it 7.0 → 5.9 before fixes, then 8.9 after. **Running relocates
the score rather than raising it** — it buys readiness and spends consistency, which is the honest direction.

**Residual issues and severity.**

| Issue | Severity |
|---|---|
| Every new destination — ledger rows, carry tables, routing rows — has received nothing, ever | **High**: a destination that has never received is a specification, not a mechanism |
| `rd-engineer → Done → cto`, step 3's build-and-device split, and the standalone gate's conditional firing are written and unrun | **High**: E1 evidence where the same claims elsewhere are E2 |
| `Open design question:` was re-typed to multi-line — replacing a field a live run falsified with one no run has touched | **Medium**: the fix is sound by inspection and untested by execution |
| Fix **J** not done; the custody class closed instance by instance | **Medium**: the class recurs in the four unreviewed pipelines by default |
| **I10** — whether `technical-architect` may rank an `architecture` direction | **Open, GD's call**: documented with a workaround, deliberately not decided |
| Scores are self-assessed by the author of the fixes | **Medium**: **E0** on this project's own scale |

**Known non-solutions — do not retry these.**

- **Fixing an instance does not close its class.** I9 was fixed in one file and recurred as R2 in another;
  R2 was then fixed and recurred *again* in a reference file created minutes earlier to fix it. Only a
  machine check has ever closed a class here.
- **Re-reading a file you just edited cannot find the seam defect**, because the defect is no longer in that
  file. Grep both directions across `workflows/`, `references/` and the agent contracts instead.
- **Adding prose does not move enforceability or readiness.** The `feature-intake` round changed nine files
  and moved the layer score by zero. That is recorded evidence, not a prediction.
- **Structural verifier checks do not catch routing defects.** 78/78 passed with twelve live.

**Next best action.** Fix **J** — the two semantic verifier checks, negative-tested by reverting a known
defect and restoring it. It is the only remaining work that raises a binding axis without a real project,
and it covers the four unreviewed pipelines for free.

**Required input or dependency.** For anything beyond J: a real Unity project with a real device, and one
feature run end to end through a real ledger. Not obtainable in this repository.

**Safe resume point.** Both finished pipelines are committed and verifier-green; start from
`.claude/workflows/tools/verify-workflow-layer.ps1` and add the two checks. No half-applied edit is
outstanding, and no pipeline is mid-review.
