# `research-decision.md` — Review, scored against a real run

> **Working note.** Companion to `workflow-layer-assessment.md` and `feature-intake-update.md`. This one is
> different from both: it was not written by reading the layer. It was written by **running** it.

## Part 0 — What was actually run, and what that buys

Five real agent dispatches, in pipeline order, against one hypothetical feature. Every return quoted below
is a real envelope from a real dispatch, not a reconstruction.

**The feature.** The GD's words, unedited, as `feature-intake.md` step 1 requires:

> *"Tôi muốn thêm voice chat trong trận co-op 3 người. Đang đánh boss mà không nói được với nhau thì không
> phối hợp nổi. Nhưng đừng làm tụt FPS hay tốn pin trên máy Android yếu."*

**The project profile** supplied with it (the caller's knowledge, per invariant I1): Unity 6000.0 LTS, URP,
IL2CPP; PC via Steam and Android cross-play; Snapdragon 680 / 4 GB minimum; 33.3 ms budget; Netcode for
GameObjects over Unity Transport on a **client-hosted listen server where the host may be the phone**;
`Game.Core.*` pure C#; no voice capability of any kind; **already live on both stores**.

| # | Step | Agent | Status returned | Cost |
|---|---|---|---|---:|
| 1 | `feature-intake.md` step 2 — classify | `technical-architect` | `Needs-decision` → `cto` | 61k |
| 2 | `feature-intake.md` step 3 — widen | `advisor` | `Done`, 4 options | 47k |
| 3 | `feature-intake.md` step 4 — attack | `critic` | `Done`, 11 findings, 3 Critical | 50k |
| 4 | `research-decision.md` step 1 — sweep | `researcher` | `Needs-decision` → `cto` + `rd-engineer` | 83k |
| 5 | `research-decision.md` step 4 — decide | `cto` | `Needs-decision` → `gd` | 86k |

Step 2's spike gate was offered and **declined** (no reference device exists), which exercised the documented
declined-spike path rather than skipping it. `rd-engineer` (step 3) was therefore not dispatched.

**What this evidence is, stated honestly.** Every defect below was produced by following the files as written
and hitting a wall — that is **E2** on `effort-allocation.md`'s scale for claims about the *specification*,
because the returns are tool output and the walls are reproducible from them. It is **not** evidence that the
layer works in production: no code was written, no gate ran, no ledger was committed, and `.workflow/` still
does not exist. The ceiling this buys is lower than a real feature would buy, and it is stated rather than
rounded up.

**Deliberately not done:** no `.workflow/` directory and no `calibration.md` row were created. A simulated
run's numbers are exactly the "estimated or reconstructed" values `calibration.md` forbids, and a fake
feature in the in-flight index would look real to the next session. The dry run must not become fake state —
a rule the layer does not currently carry.

---

## Part 1 — What the run proved works

Three things earned their cost, and the evidence is in the returns.

**The `researcher` → `cto` split is load-bearing, and it paid off here.** `researcher` returned no
recommendation and flagged Vivox's data policy as *"a secondary aggregation … treat it as a signal to confirm
in writing, not a settled fact."* `cto`, acting on exactly that flag, fetched the primary source and found a
different and disqualifying fact: Unity's own Vivox data-safety page states **"Voice data is not encrypted,
but the signaling is."** That flips the decision — against a C4 privacy constraint, encoding is not
encryption. Neither agent reaches that alone: the one that swept did not commit, and the one that committed
re-checked what the sweep marked unverified. **This is the clearest argument in the layer for why the
consult/gate boundary exists**, and it is now backed by a real return rather than by assertion.

**The declined-spike path works exactly as written.** Step 4's rule — *"A declined spike is not a dead end:
step 4 proceeds, and `cto` makes an explicitly provisional call naming the number it hinges on"* — produced
precisely that: a decision plus *"re-open if voice adds more than ~2 ms to the 33.3 ms main-thread budget, or
more than ~8% sustained additional CPU on the host."* No dead end, no fabricated measurement.

**The dispatch-brief table added last session prevented the `Blocked` it was written for.** `critic` was
dispatched with the whole `### B` block, the goal and the accepted constraints, and returned `Blocked — needs
from caller: none`. `researcher` likewise. Both agents' `If absent` tables would have blocked on a thinner
brief. That fix is now confirmed live, not just reasoned.

---

## Part 2 — Findings

Twelve. Numbered `R1`–`R12`; the ones that land on `feature-intake.md` are marked, because the user asked for
that pipeline to be re-evaluated and the run is what re-evaluated it.

### R1 — The architect's escalation returns a status the pipeline does not handle · *feature-intake*

The live dispatch returned `Status: Needs-decision`, `Routed to: cto`. `feature-intake.md`'s routing table has
exactly one row for this agent and this destination:

> `technical-architect` → **`Rejected`**, `Routed to: cto` | Hand to `research-decision.md` at its **E2** …

`Needs-decision` is not covered. And the agent file is self-contradictory about which it should send:
`technical-architect.md` §4 instructs *"return `Needs-decision` with `Routed to: cto`"*, while its own §6
worked example shows `Status: Rejected`, `Routed to: cto`. Two files, three statements, two values. The run
produced the value the pipeline cannot route.

### R2 — That same row hands a pre-CP1 escalation back at step 6, skipping the loop and CP1 · *feature-intake*

The row sends the work back at **E3 — step 6**, unconditionally. But the architect can escalate to `cto` from
two entirely different places:

| Escalated from | Correct hand-back |
|---|---|
| **Step 2**, at classification — before the loop has run | **E2 — step 3**, where the shape fires the loop, or step 6 where it does not |
| **Step 6**, mid-spec — the loop already ran, CP1 already locked | **E3 — step 6** |

One row covers both and picks the step-6 answer. The live run escalated from **step 2** on a **D4/U3**
feature, so following the table literally would have skipped steps 3, 4 and **CP1** — on the one feature
shape where CP1 is mandatory.

`research-decision.md` inherits the same assumption: its exit table describes E2 as *"step 5, or the
architect **mid-spec**"*. The phrase names only the second origin. Note the file gets the neighbouring case
right — the `advisor` → `cto` row at line 177 correctly says *"**E2** — step 3, **not** step 6"*. The rule
exists; it was applied to one row and not the other.

**This is the I9 family exactly**: an entry whose resume point branches, written as though it did not.

### R3 — `Open design question:` is single-valued; a D4/U3 feature has two kinds at once · *feature-intake*

The field is `<design | architecture | technology | none>` — one word, and the word is what routes. The live
classification legitimately had both: a `technology` question (license or build) **and** three `design`
questions the GD owns (push-to-talk vs open mic, team-wide vs proximity, moderation scope).

The architect returned `technology` and smuggled the design questions into a prose *"Sequencing note for the
caller"* outside the envelope. Had it obeyed the envelope strictly, step 3's dispatch would have carried
`technology` as the only question — and `intake-advisor-critic-loop.md` says `advisor` gets *"the architect's
`Open design question:`, **verbatim**"*. The loop fires on D4 regardless of the field's value, so the trigger
and the payload can diverge. **This is a defect in a field added last session**, found only by running it.

### R4 — The constraint list `advisor` is handed is missing the one that decided the answer · *feature-intake*

The brief table says to attach *"platform, track, genre, monetization, and whatever the GD has already
fixed."* `advisor` returned: *"no matchmaking-with-strangers detail was given, so I flag where a precedent's
moderation posture assumed strangers vs. only known teammates."* The **social graph** — who you play with —
was the single most decision-relevant constraint for the moderation question, and it is not on the list.
Minor, and cheap to fix.

### R5 — `critic`'s Risk Findings have no route out of CP1 · *feature-intake*

`critic` returned 11 ranked findings. At least four are **acceptance-criteria gaps**, not direction risks:
no criterion measures echo or intelligibility at all; mic contention and interruption are outside the failure
model; the Android **host role** — the worst case — is unbounded by any criterion; and a battery pass and the
GD's actual fear (thermal throttling late in a session) are different measurements.

CP1 approves *"the locked direction, and which risks they accept and live with."* Then nothing carries the
findings anywhere. `intake-tech-spec.md` — the file that owns step 6 — **never mentions `critic`, Risk
Findings, or accepted risks.** The architect writing the spec has no specified way to see them, so the
material most likely to fix the acceptance criteria dies at the checkpoint that surfaced it.

### R6 — "CP1 spends U down → drop U to U1" is unconditional, and it disarms `research-decision.md` E4 · *feature-intake*

`feature-intake.md`:

> **CP1 spends U down, so reclassify when it closes.** … drop U to U1, recompute the tier …

`research-decision.md` **E4** is entered when *"Classification returns **U2 or U3** and the open question is a
technology unknown."* At **D4–D5**, CP1 always fires and always precedes step 5. So following the rule
literally sets U1 before the research branch is ever evaluated, and **E4 becomes unreachable for every D4–D5
feature** — the exact shape most likely to need it.

The run is the case: U3 was set by a design unknown **and** a technology unknown. CP1 settles the design half
only. The rule needs to spend down what CP1 actually settled, not the whole axis.

### R7 — `research-decision.md` E1 and E4 both describe the same entry, and they exit to different places

The live branch satisfies both literally: step 5 detected a capability the project lacks (**E1**) *and*
classification returned U3 on a technology unknown (**E4**). Nothing disambiguates them — and step 5's exit
table sends them to **opposite** hand-backs:

| Left from | Hands back at |
|---|---|
| **E3**, **E4** | `feature-intake.md` **E2** — step 3 |
| **E1**, **E2** | `feature-intake.md` **E3** — step 6 |

Picking the wrong door reruns a finished loop or skips an unrun one. The real discriminator is *where in
`feature-intake.md` the branch was taken* — which E1 names and E4 does not.

### R8 — `Routed to:` is singular in every envelope; `researcher` returned two

It returned: *"`cto` for the vendor/infrastructure commitment …; `rd-engineer` for one on-device spike."*
Both are correct and they are sequential. But the envelope declares `Routed to: <agent-id> | gd | none`, and
the routing table lists the two destinations as separate rows with separate actions. A caller reading
top-down matches the first and acts on it alone. The Escalate lane happens to order them correctly by
coincidence, not because anything says so.

### R9 — The pipeline's own deliverable has no route into the Tech Spec

This is the central defect, and it is checkable in one grep. `research-decision.md` step 1 states:

> The report carries a `Picture taken:` date and what would make it stale. **Both are forwarded into the Tech
> Spec**; a later re-entry for the same capability re-checks rather than reuses.

`technical-architect.md`'s envelope has **no field** for either. Neither does `intake-tech-spec.md`. The
mechanism that prevents a stale research result being silently reused has no carrier.

Worse, of the five things this pipeline produces, only one is named in any hand-back row:

| Produced | Named as travelling to step 6? |
|---|---|
| Research Report | **Yes** — `feature-intake.md` E3 row |
| **Technical Decision** — the pipeline's actual deliverable | **No — named nowhere** |
| **`Standard set:`** — project-wide, outlives the feature | **No — appears nowhere in `workflows/` or `rules/`** |
| **`Picture taken:` / staleness** | Asserted as forwarded; no field exists |
| **The provisional re-open threshold** | **No — no ledger row, no field** |

On an Escalate lane the Technical Decision *is* the result and the Research Report is merely its input. The
E3 row names the input and loses the output.

### R10 — A standard `cto` sets has no home, and the pipeline knows it needs one

`cto` returned rule 4 — *"No real-time media vendor is adopted without a vendor-written statement that the
media, not only the signaling, is encrypted in transit"* — and then: *"This rule is precedent-setting and is
owed an ADR … **I have not written it, so the caller should dispatch it.**"*

There is no step, no routing row and no ledger row for that. `engineering-standard-adr-authoring` is a skill
`cto` itself holds, so the dispatch is a second `cto` call nobody is told to make. A project-wide standard
produced by the layer's own gate currently survives only in the conversation that produced it.

### R11 — Research can legitimately move **D**, and the re-entry contract forbids it

`cto`'s rule 2 made encrypted transport a **precondition**: voice ships only over a DTLS-configured Relay
connection, because a direct listen-server connection would require a private key in the shipped client. It
flagged this as *"the one item here that can move the timeline."*

That is potentially a netcode migration the intake classification never covered — a **D** move. But
`entry-index.md` is explicit: *"Only U is re-read on an ordinary re-entry. D, C, R and X do not move because
the work itself did not change."* Here the work did change. The only file that re-reads all five axes is
`change-request.md`, and a research result is not a change request. The scope expansion has no route.

### R12 — "Provisional, then confirm" points at a gate that was already declined

Step 4: *"`cto` may decide provisionally and name one measurement. That runs the step 2 gate, then returns
here."* In this run the step 2 gate had **already been offered and declined** before `cto` was dispatched.
The rule sends the provisional call back to it. Nothing says whether the declined offer consumed the
one-cycle cap, whether re-asking in the same run is the "nagging" `loop-termination.md` forbids, or where the
re-open threshold is recorded so a future session honours it. The most valuable line `cto` produced — the
number that falsifies its own decision — currently has nowhere durable to live.

---

## Part 3 — Score

Five axes carried over from `feature-intake-update.md` so the numbers compare, plus one the run forced into
existence.

| Axis | Score | Why |
|---|---:|---|
| Entry points and addressing | **6.5** | E1/E4 overlap with opposite exits (R7); E2 conflates two origins (R2). Both found live |
| Agent-brief contract | **7.0** | Step 1 and step 2's tables are genuinely good and worked. Step 4 — its only gate agent — has **no** attach spec; the run worked because the brief was written carefully by hand |
| Gate and exit logic | **7.5** | The spike gate and the declined path are excellent. Provisional-then-confirm points at a spent gate (R12) |
| Counters and caps | **6.0** | The one-measure-and-confirm cap is well stated and is **the only cap in the layer with no ledger row** |
| Honesty about its own gaps | **8.0** | Candid throughout — R0/R1 scope, "never entered without a candidate set", "recomputes U". Does not state the custody gap |
| **Result custody** *(new)* | **3.5** | Four of five outputs are named nowhere. The pipeline's own deliverable does not travel |

**`research-decision.md`: 7.0** on the five axes `feature-intake` was scored on — **6.5** including custody.

### `feature-intake.md`, re-evaluated — 9.0 → 8.2

The run was asked to re-test the pipeline scored 9.0 last session without ever being executed. It lowered it.

| Axis | Was | Now | What moved it |
|---|---:|---:|---|
| Entry points and addressing | 9.5 | **7.5** | R2 is the I9 family again, in the one row that was not checked; R1 |
| Agent-brief contract | 8.5 | **8.0** | The loop table **held live** — a real strength. But step 6 has no brief spec at all, and R4 |
| Checkpoint logic | 9.0 | **7.5** | R6 — CP1's U rule is unconditional and disarms a downstream trigger |
| Counters and caps | 9.0 | **9.0** | Held. Nothing found |
| Honesty about its own gaps | 9.0 | **9.0** | Held |
| **Result custody** *(new)* | — | **4.0** | `critic`'s findings die at CP1 (R5) |

**8.2** on the original five axes, **7.5** including custody. The 9.0 was a score on a pipeline that had been
read, not run, and `effort-allocation.md` is explicit that *"reading code is review; running it is
verification."* This is what the difference was worth: **0.8 points of optimism**, plus one axis nobody had
thought to score.

### The layer — 7.8 → 7.7

| Axis | Was | Now | Why |
|---|---:|---:|---|
| Internal consistency | 9.0 | **8.0** | Twelve new inconsistencies, all reproducible |
| Operational readiness | 3.5 | **5.0** | The dispatch layer is now proven end to end with real returns. Still no code, no gate, no ledger, no `.workflow/` |
| Enforceability | 5.5 | 5.5 | Unchanged — no new mechanism yet |

**Running it did not raise the layer's score. It relocated it** — bought readiness, spent consistency. That
is the correct outcome and the honest one: the defects were always there, and the score was measuring how
carefully the layer had been read.

---

## Part 4 — Proposed fixes

Ordered by leverage. A–C are one root cause with several symptoms.

| # | Fix | Closes | Where |
|---|---|---|---|
| **A** | **Specify what the step 6 dispatch carries** — a `## What the Tech Spec dispatch must carry` table: the locked direction and CP1-accepted risks, `critic`'s open findings, the **Technical Decision and its `Standard set:`**, the Research Report with `Picture taken:`, and the four values from `entry-index.md`. Every other dispatch in the layer has one; this is the only one that does not | R5, R9, R10 | `references/intake-tech-spec.md` |
| **B** | Add the envelope fields that table needs a home for: `Inherited decisions:` (the standard, and the staleness date it rests on) to the Tech Spec | R9, R10 | `technical-architect.md` |
| **C** | **Split the architect→`cto` routing row by origin**, and accept both statuses. Fix `technical-architect.md`'s own §4-vs-§6 contradiction so one value is returned | R1, R2 | `feature-intake.md`, `research-decision.md`, `technical-architect.md` |
| **D** | Make CP1's U rule spend down **what CP1 settled** — where the open question was `technology`, the design half only | R6 | `feature-intake.md` |
| **E** | State the E1/E4 discriminator: E1 is entered from step 5 (after the shape's loop ran or was skipped); E4 from step 2 (before it). Their exits then follow | R7 | `research-decision.md` |
| **F** | Four ledger rows: `Measure-and-confirm: 0/1`, `Standards set:`, `Research staleness:`, `Provisional decisions:` with the re-open threshold | R10, R12 | `state/templates/feature-ledger.md` |
| **G** | Allow `Open design question:` to carry both kinds, and say which one routes where | R3 | `technical-architect.md`, `feature-intake.md` |
| **H** | A rule for a research result that **adds scope**: it is not an ordinary re-entry — name it at CP2 and re-read D, or route to `change-request.md` | R11 | `research-decision.md` |
| **I** | Add the social graph to `advisor`'s constraint list | R4 | `references/intake-advisor-critic-loop.md` |
| **J** | **Two new verifier checks** — (1) every artifact a pipeline's agent table declares under `Produces` must be named in at least one entry or hand-back row; (2) every `Routed to:` value an agent file instructs an agent to return must have a matching routing row in each pipeline that dispatches it. Check (2) catches **R1** mechanically | R1, R9 | `tools/verify-workflow-layer.ps1` |

**J is the one that matters most long-term.** R1 and R9 are both "an agent produces something the pipeline
never receives" — a class a machine can check, exactly as the routing checks added last session made I9's
class checkable. Prose fixes close instances; a check closes the class.

---

## Part 5 — Open, for the GD

1. **Should the dry-run rule be written down?** This run deliberately created no `.workflow/` and no
   calibration row, because simulated numbers are the reconstruction `calibration.md` forbids and a fake
   in-flight row would mislead the next session. The layer does not currently say this anywhere.
2. **R11 — does research that expands scope go to `change-request.md`?** It is the only file that re-reads all
   five axes, but a research result is not a GD change. Either it gains a door or `research-decision.md`
   gains a reclassification rule. A structural call, not a defect fix.
3. **Still open from last round:** whether `technical-architect` should gain a `Recommended direction:` field
   for `architecture`-classified questions (I10).

---

## Part 6 — Resume point

Where this stands, so the next session starts from a read rather than a re-derivation.

| | State |
|---|---|
| **Pipelines reviewed** | `feature-intake.md` (twice — read, then run), `research-decision.md` (run) |
| **Still unreviewed** | `feature-development.md`, `review-pipeline.md`, `qa-pipeline.md`, `change-request.md`, `orchestrator.md` |
| **Findings recorded** | I1–I10 in `feature-intake-update.md`; R1–R12 here |
| **Findings fixed** | I1–I9 (last round, committed). **R1–R12: none — proposed only, Part 4** |
| **Verifier** | 78 claims, all passing — **including with all twelve R-findings live in the tree**. That is the argument for fix **J** |
| **`.workflow/`** | Does not exist, deliberately. See Part 5 item 1 |
| **Layer score** | 7.7. Readiness 5.0 is the binding constraint; it does not move without a real feature in a real project |

**The next action, if the fixes are the priority:** A → B → C first. They are one root cause — no file
specifies what the step 6 dispatch carries — and closing it retires R5, R9 and R10 together. **J** is the one
worth doing whether or not the rest happen, because it converts a class of defect into a machine check
instead of a paragraph.

**The alternative next action:** run the same treatment on pipeline 3. The method is now established and
cheap to repeat — dispatch the real agents, follow the files literally, and record where they run out. It
found twelve defects in two pipelines that careful reading had missed, including two in fixes written the
round before.

---

## Part 7 — The standalone half, run and then closed

Parts 0–6 scored this pipeline on its **branch** path. The standalone half — **E5**, **E6**, step 3 and the
gate at the end — had never been entered. It has now, with two more real dispatches, and the pipeline has
been fixed against what they found. This part is the record of both.

### What was run

| Entry | Agent | Returned | What it bought |
|---|---|---|---|
| **E5** — GD asks for research directly | `researcher` | `Done`, `Assessed: Direct`, `Routed to: none`, `Blocked: none` | The **Direct lane** verified at **E2**, first time |
| **E6** — GD summons a spike | `rd-engineer` | `Blocked`, `Routed to: gd`, four named needs | **R17**, below |

**Two of E6's four blockers are this repository, not the specification** — there is no Unity project here and
no device attached, because this repo is the framework. They are not counted as findings. The third is.

**Three contracts held under test.** The pass/fail threshold was deliberately withheld from `rd-engineer`,
and it proposed one from the project's budgets and said so — the `If absent` row working as written.
`researcher` returned `Already in project: nothing confirmed` and stated it *"was not fabricated as 'none
found'"*. Both returned `Blocked — needs from caller: none` where the brief was complete.

### Findings R13–R17

**R17 — the Escalate lane could not complete.** `rd-engineer`'s own guardrail forbids producing a platform
build; a measurement on the one device needs one. `build-run-engineer` appears **0 times** in
`research-decision.md`, and so do `device`, `I7` and the device lock. Worse, the file asserted *"Nothing here
writes to the project … **R0/R1 throughout**, which is why an Escalate lane can afford a spike"* — a
self-justification that is false for exactly the lane it justifies. An on-device spike is R2 and X2.

**R15 — the standalone half had no carrying contract.** `standalone-runs.md`'s "What the GD supplies" table
had rows for four pipelines and not for this one; E6 also has no step 0 and had no attach spec at step 3. The
brief for the run above had to be assembled by hand from the agent contract.

**R14 — `rd-engineer` → `Done` had no routing row**, while the diagram sent it to `cto` unconditionally and
the step table made step 4 conditional. Three sources, two answers, and `Done` is E6's *normal* outcome.
Same class as **R1**, on the other agent.

**R13 — `CPX` was a mermaid node and two sentences.** No checkpoint table, no "Rejecting means", and the name
appeared nowhere else in the layer. E5 then showed it also fires where there is nothing to gate: a Direct
lane never reaches `cto`, so it produces no standard, no commitment and nothing to re-open.

**R16 — `Already in project:` had no value for "could not check".** Harmless on E5; on **E1** it is not, since
`feature-intake.md` step 5 branches here precisely because nobody could name what covers the capability, and
*absent* and *unverified* are different answers to that.

### Fixes applied — 8 files, +93 / −51, and one new reference

| Closes | Change |
|---|---|
| **R17** | `### Step 3` written: the spike splits — `rd-engineer` writes the harness, `build-run-engineer` produces the build on the GD's request, the device lock is claimed and released (**I7**). The `R0/R1 throughout` claim corrected: Direct and Considered are R0/R1, Escalate is **R2 and X2** |
| **R15** | Step 3's attach table, each row keyed to a real `If absent` — including the **current baseline**, which the live `rd-engineer` asked for and no file carried. Plus the missing `research-decision.md` row in `standalone-runs.md` |
| **R14** | Routing row added; the diagram edge split into two conditional edges matching step 4's `Runs for` |
| **R13** | Named the **standalone acceptance gate**; made it conditional on a standard, a commitment or a threshold, so a Direct lane does not fire it; gave both rejections a defined outcome; registered the bound in `loop-termination.md` (16 caps → 17, 9 stated-here → 10) |
| **R7** | The **E1** vs **E4** discriminator stated: E1 enters from step 5, E4 from step 2 — before the loop |
| **R8** | Routing row for a return naming two destinations |
| **R9, R10** | A custody table in the new reference: all five outputs, each with a destination. `Standards set:`, `Research staleness:` and `Provisional decisions:` added to the ledger; a section for standalone results added to `project-state.md` |
| **R11** | A rule for a research result that moves an axis — neither an ordinary re-entry nor a change request |
| **R12** | `Measure-and-confirm: 0/1` in the ledger; step 4 no longer sends a provisional decision back to a gate the GD already declined |
| **R16** | `not checkable` added to `researcher`'s `Already in project:`, with why it differs from `nothing found` |

Two beyond the findings: step 4 gained the **attach spec** Part 3 marked absent, and step 2's table was
folded into step 3's to remove the duplication the step 3 table had just created.

**New reference: `references/research-exit-and-custody.md`** (92 lines) — the exit doors, the discriminator,
the custody table, the scope-expansion rule and the standalone gate. Step 5 in the pipeline is now a pointer.

### Verification

| Check | Result |
|---|---|
| `tools/verify-workflow-layer.ps1` before | **OK — 78 claims, all hold** (E2, baseline) |
| after | **OK — 80 claims, all hold** (E2) |
| The verifier against this session's own work | **It failed the run mid-way**: `engineering-standard-adr-authoring` in backticks read as an agent-id. It is a skill; added to the `$vocabulary` allowlist beside `secret-and-supply-chain-scan`. **E2 that the checker is live on this file, not passing by shape** |
| 200-line cap | `research-decision.md` **199** |

### Score — 5.9 → 8.9, and why not 9.0

| Axis | Part 3 | Now |
|---|---:|---:|
| Entry points and addressing | 5.5 | **9.0** |
| Agent-brief contract | 6.0 | **9.0** |
| Gate and exit logic | 5.5 | **9.0** |
| Counters and caps | 6.0 | **9.0** |
| Honesty about its own gaps | 6.5 | **8.5** |
| Result custody | 3.0 | **8.5** |

**8.9** on five axes, **8.8** on six. The two held at 8.5 fail for one reason each, and it is the same reason:

- **Honesty** — a false claim was replaced by an **unverified** one. The file now describes a build-and-device
  path nobody has executed.
- **Custody** — three of five destinations are rows in a ledger template that has **never been instantiated**.
  `.workflow/` still does not exist. A destination that has never received anything is a specification.

**Prose reached ~8.9 and the rest is not reachable by writing.** Re-running E6 against the new step 3 needs a
real Unity project and a real device. What *is* reachable here is fix **J** — the two verifier checks — which
converts custody from written-down to machine-checked, and is the only remaining path to 9.0 in this repo.

**Scored by the author of the fixes**, which is **E0** on this project's own scale. Awaiting an independent
pass, as in Part 4.
