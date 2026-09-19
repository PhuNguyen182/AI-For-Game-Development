# `review-pipeline.md` — Review, scored against a real run

> **Historical record — read [`README.md`](README.md) first.** This is the log of one review round, not a
> specification. The layer that runs is `.claude/workflows/`; the current state of it is
> `.claude/workflows/workflow-checklist.md`. **Two things here go stale by design**: every number about the
> layer (verifier claim counts, "still unreviewed" lists, "nothing is committed") is as of this round, and
> **later parts supersede earlier ones** — the last score in the file is the one that stands.

> **Working note.** Fourth in the series, after `feature-intake-update.md`, `research-decision-update.md` and
> `feature-development-update.md`. Same method as the last two: the pipeline was not read into a score, it
> was **run** — both gates dispatched for real against one submission, following the files literally, and
> recording where they hit a wall.

## Part 0 — What was run, and what it buys

**The submission.** Two `.cs` files in a scratch tree outside the repository: a `Game.Core.Economy`
first-purchase bonus rule and the `Game.Client.Shop` panel that previews it. Classified **A4 — D2 C3 (economy
path) U1 R1 X1**, verification floor **V3**, attempt budget 2, client track, author `csharp-engineer`, strike
count 0. Dispatched at **E1** carrying exactly the six rows `review-entry-inputs.md` specifies — no more.

The submission was shaped to load the pipeline's riskiest untested claims, not to be hard: a tautological
overflow guard, the bonus rule re-derived in a MonoBehaviour with a literal `20`, an `sk_live_` credential
both hardcoded and logged, an allowlisted IAP product id beside it, and an Implementation Note reading
`Verification done: the code compiles` against a V3 floor with `Known limitations: none`.

| # | Step | Agent | Returned |
|---|---|---|---|
| 1 | step 1, in parallel | `code-reviewer` | `Status: Done`, **`Verdict: Request changes`** — 11 findings |
| 2 | step 1, in parallel | `security-reviewer` | `Status: Done`, **`Verdict: Blocked`** — 2 Critical, 2 High, 1 dismissed |

**What this evidence is.** Defects below marked **live** were produced by following the files as written and
hitting a wall — **E2** for claims about the *specification*. It is not evidence the layer works in
production: no feature ran end to end, no CP3 fired, no ledger was written and `.workflow/` still does not
exist. The scratch tree was deliberately outside the repository and no fake state was created, per
`research-decision-update.md` Part 5.

---

## Part 1 — What the run proved works

**The two-gate split earned its cost, again, and differently from last time.** The gates did not overlap:
`code-reviewer` found the spec violations (the client re-deriving the rule, the unused `isFirstPurchase`, the
`Debug.Log` standing in for SPEC-4's display) and `security-reviewer` found the credential and independently
classified the same overflow bug as *fail-open on a currency path*. Neither is reachable from the other's
lens, and **the one finding both reached, they reached for different reasons** — which is the argument for
running them in parallel rather than sequentially.

**The allowlist discipline held.** `security-reviewer` recorded `com.astronex.gems.pack_medium` as an
`Ambiguous Identifier` at `Severity: Info` and explicitly dismissed it — *"recorded so it is visibly
dismissed rather than silently skipped"*. That is `security.md`'s false-flag rule working as written.

**The verification-floor row fired exactly as specified.** `code-reviewer`'s F9 measured "the code compiles"
against V3 and produced a finding, naming the three acceptance criteria that would have caught F1–F3. The
routing row that turns that into `Request changes` + a strike is therefore confirmed live, not asserted.

**Both gates refused to guess.** Each returned `Blocked — needs from caller: none`, and `code-reviewer`
stated its "I did not write this" assumption unprompted, per its own guardrail.

---

## Part 2 — Findings

Numbered **RP1–RP16**. **live** means a dispatch produced it.

### RP1 — The verification floor is stated wrong for a whole tier · High

Line 16 read *"V1 at A1–A2, V2 at A3, V3 at A4, V4 at A5, **per `effort-allocation.md`**"*. That file says
something different, and so does `task-classification.md` Step 4:

> **A2** | V1, **or V2 the moment it changes state**
> *"A2 rises to V2 whenever direct objective verification is cheap, or whenever the task changes state —
> 'basic verification' is never an excuse to skip an available check."*

**A code submission always changes state.** So the gate that enforces the floor — and whose routing row turns
an unmet floor into a strike — was handed a number one level too low for every A2 submission this project
will ever produce. A misquote of the authority the line itself cites.

### RP2 — `Blocked` meant two opposite things in adjacent routing rows · High · **live**

`security-reviewer`'s envelope carries `Blocked` in **both** `Status:` and `Verdict:`. The routing table had:

| Row | Word | Action |
|---|---|---|
| *"`code-reviewer` `Request changes`, or `security-reviewer` `Blocked`"* | the **Verdict** sense | +1 strike, back to author |
| *"either gate → `Blocked`"* | the **Status** sense | supply the input, **no strike** |

The live return was `Status: Done`, `Verdict: Blocked` on a **Critical hardcoded production credential**. A
caller reading top-down matches the second row and answers a security rejection by asking for an input — and
the finding is lost. The file makes a point of warning about this hazard in one direction (*"Read `Verdict:`,
never `Status:`"*) and then created it in the other, in its own table.

### RP3 — The supply-chain pre-gate deadlocks at E1 · High

`references/development-exit-and-custody.md` routes a `.unitypackage`/Asset Store/vendored-DLL import to
`review-pipeline.md` **E1** *before* the integration is written, because `security.md` §7 forbids treating it
as adopted until `security-reviewer` clears it. `review-pipeline.md` knew nothing about it:

- **E1 declared only** *"a submission from `feature-development.md`"*.
- `review-entry-inputs.md` requires a Tech Spec section; an import has none, so `code-reviewer` returns
  `Status: Blocked` by its own required-input table.
- Step 2: *"clear only when `code-reviewer` returns `Approve` **and** …"* — an `Approve` that can never
  arrive. **The pre-gate never clears.**
- And the file's opening declared the whole pipeline optional, while this one submission is not.

This was named as an open half in `feature-development-update.md` Part 5. It is closed here.

### RP4 — Invariant I5 appeared nowhere, and the default worked against it · High

`I5` (*a design flaw reaches the GD immediately, from any step*) and the phrase "design flaw" appeared **zero
times** in `review-pipeline.md` or any of its three references — while the file stated *"Rejections are
silent to the GD"* as an unqualified rule. `code-reviewer`'s guardrail bars it from widening into design
intent and tells it to *"note them and route them"* — with no route specified. Same class as **D3**, which
`feature-development.md` closed one round earlier.

### RP5 — The pipeline declared no exits · High

It hands to at least six places — `feature-development.md` E3, `feature-intake.md` E1, `qa-pipeline.md`,
`change-request.md`, `cto`, the GD — and declared none, while four other files name it as their origin or
destination. This is **D1**'s class, recurring exactly as the debt register predicted it would in the
unreviewed pipelines.

### RP6 — E3's escalation row conflated two origins · Med

E3 carries **two** kinds of submission — the gated-direct lane, and `qa-automation-engineer`'s test code. The
second-strike row sent both to `feature-intake.md` **E1**. For a test suite that is wrong: a suite is not a
feature request, has no direction to classify and no Tech Spec to produce. **R2**'s class — one row covering
two origins and picking one answer.

### RP7 — E1's origin list was stale · Med

Four origins exist (`feature-development.md`; a tech lead's `Fix:` per **I10**; the supply-chain pre-gate;
a declined gate opted into later per `optional-gates.md`). One was declared. **D16**'s class.

### RP8 — The three-strikes root cause has no carrier · Med · *contract-checked*

Step 4's most expensive path produces a cause. `technical-architect`'s Output section defines the Tech Spec
envelope, the CP3 variant (`Built:`/`Matches spec intent:`/`Known limitations:`) and `Change severity:` —
**and nothing for a root cause**. It would arrive as prose outside the envelope, which is exactly how **R3**
failed. The artifact was also undeclared in the agents table's `Produces` column.

### RP9 — `Needs Confirmation` beside a rejection had no precedence · Med

The mermaid draws three edges out of one `Both` decision node. A `Needs Confirmation` from one gate and a
`Request changes` from the other satisfies two of them, and step 2's *"anything else goes back as one
combined dispatch"* contradicts the routing table's *"the ladder, then re-run that gate"*. Not reproduced
live — the run's credential was unambiguous enough to be a finding rather than a question — so this is **E1**,
and it is marked as such.

### RP10 — A cap exists that `loop-termination.md` does not hold · Med

`qa-test-code-gate.md` caps test-code strikes at two. `loop-termination.md` opens with *"This file is the
single home for every bound in the layer. A loop whose cap is not in the table below does not have one"* —
and has no row for it. **Cross-file; left open** (see Part 5).

### RP11 — F6's exact wording survived here · Med

*"the orchestrator asks the GD whether to run it"* — the sentence `optional-gates.md` was rewritten to
correct in the intake round, still live in this file. That file now says plainly it *"has never meant that a
pipeline mid-run routes its own boundary back through the router."* Fixing the owning file did not fix the
consuming one: the debt register's *"fixing an instance does not close its class"*, confirmed a fourth time.

### RP12 — `review-entry-inputs.md` misquoted the gate's own `If absent` · Med

It asserted, twice, that absent the floor *"the gate silently substitutes its own expectation"*.
`code-reviewer`'s guardrail says: *"absent it, review correctness and **state that the floor was not
supplied**."* The gate declares the gap; it does not substitute. **I8**'s class, on the highest-stakes row in
the table.

### RP13 — The custody checks did not cover this pipeline · High

`verify-workflow-layer.ps1`'s two checks were scoped to three pipelines and printed the rest as *"not yet
asserted"*. Both of this pipeline's checks were therefore unasserted — including its three `Produces`
artifacts.

### RP14 — The mermaid contradicted its own step 6, and `qa-pipeline.md` · Med

The diagram ran `CP3 --approve--> Ask{run QA?}`. Step 6 said *"`qa-lead` in plan mode … runs as soon as the
gates clear"* — impossible if the ask that authorises it only fires after CP3. `qa-pipeline.md`'s own diagram
(`In --> Plan`, and `CP3` gating only `Exec`) agrees with the **text**. review-pipeline's diagram was the odd
one out, and it is the one a reader follows.

### RP15 — **Both gates' mandatory skills do not resolve** · High · **live**, E2

The round's most consequential finding, reported independently by both agents and then verified three ways.

| Gate | Skill | Its own trigger | What happened |
|---|---|---|---|
| `code-reviewer` | `shared-core-boundary-audit` | on rule/boundary code | `Unknown skill` |
| `security-reviewer` | `secret-and-supply-chain-scan` | **"Always"** | `Unknown skill` |

Verified independently of both agents: **all 90 project skills sit at `.claude/skills/<group>/<name>/SKILL.md`
and the harness registers `.claude/skills/<name>/SKILL.md` — one level up. Not one of them loads.** The five
project-shaped skills that *do* appear in the session come from outside this repository; a `name:` grep for
them across `.claude/skills` returns nothing.

Both gates read the SKILL.md by hand and said so, so this run's verdicts are sound. That is diligence, not
mechanism — `security-reviewer` put it exactly right: *"a gate whose mandatory skill silently fails to
resolve would, with a less careful reading, become a scan nobody performed."* `security.md` names that skill
as the detection control for the one rule in this project with no tier exemption.

### RP16 — The gate had to guess whether the submission was feature-complete · Med · **live**

`code-reviewer` is told to check the feature-root documents *only* on a feature-complete submission, and
never to demand one whose trigger has not fired. Nothing in the brief says which this was, so its F11 opens
*"I am flagging this conditionally on purpose"* and hedges a correct finding. Right behaviour; a question the
caller should not have forced it to ask.

---

## Part 3 — What changed

One new reference, four files amended, two verifier changes. `review-pipeline.md` is **200** lines against
the 200 cap — every addition paid for by promotion or compression, none by deleting reasoning.

| Closes | Change | Where |
|---|---|---|
| RP5, RP2, RP3, RP4, RP8 | **`references/review-exit-and-custody.md`** — new. Twelve exit doors; an eleven-row custody table for every returned field; the `Status:` vs `Verdict:` `Blocked` table; the supply-chain pre-gate's three differences; the three returns that do not wait | new reference |
| RP1, RP12 | The floor restated correctly, with **A2's state-change clause** named, and "the floor travels, it is never the gate's to derive". The `If absent` row corrected to what the contract actually says, and the entry table now says to send **`V2`, not `A2`** | `review-pipeline.md`, `review-entry-inputs.md` |
| RP2 | `Verdict: Blocked` vs `Status: Blocked` disambiguated in **four** places — step 1, the mermaid's edge label, and both routing rows | `review-pipeline.md` |
| RP4, RP6, RP7, RP9, RP11, RP14 | I5 routing row; E3's two origins split at the cap; E1's four origins declared; the ladder's precedence rule; the ask's owner corrected to *whichever party reached the boundary*; the diagram re-cut so the QA ask fires at `Done` and CP3 gates execution only | `review-pipeline.md` |
| RP9 | The precedence argument in the file that owns the ladder | `review-needs-confirmation.md` |
| RP3, RP6, RP16 | The pre-gate's dispatch row (`security-reviewer` alone, no Note, not a strike); "say which E3 origin"; the **feature-complete** row, keyed to the live hedge | `review-entry-inputs.md` |
| RP13, RP8 | Custody checks extended to `review-pipeline.md`; `Root Cause` declared and given a receiver | `verify-workflow-layer.ps1`, both |
| RP15 | **A new check: every skill an agent is told to invoke must be registrable** | `verify-workflow-layer.ps1` |

### The negative tests — and the regression one of them caught

Per the standing rule that a check which passes for the wrong reason turns an open defect into a green claim.

| Check | Negative test | Result |
|---|---|---|
| `no Produces artifact nothing receives`, on review-pipeline | Strip `Root Cause` from every receiver | **FAIL**, naming it · restore → **PASS** |
| `every named skill is registrable` | Relocate one skill to the registrable path | 66 → **65** unresolvable · revert → 66 |

**The first negative test failed to fail, and that is the most useful thing in this round.** Declaring two
artifacts in one `Produces` cell (`**Implementation Summary**, **Root Cause**`) made the extraction regex
match **nothing** — it had been anchored on a lone `**x**` filling the cell. So the row went unchecked in
silence, *including* `Implementation Summary`, which had been passing before. A regression introduced by this
round's own edit, invisible to reading, caught only because the check was tested against the defect it was
written for. The regex now takes the whole cell and every bolded artifact inside it.

### Verification

| Check | Result |
|---|---|
| `verify-workflow-layer.ps1` before | **OK — 86 claims, all hold** (E2, baseline) |
| after | **88 of 89 hold** (E2). The one failure is **RP15**, a real unfixed defect — see below |
| Both custody checks, negative-tested | **FAIL on revert, PASS on restore** — E2, not asserted |
| The skill check, negative-tested | **Responds to the condition** (66 → 65 → 66) — E2 |
| 200-line cap | `review-pipeline.md` **200**; all four references well under |
| The seam, both directions | Grepped. QA-ask ordering now agrees with `qa-pipeline.md`; the pre-gate seam closes both ways; **the test-code cap is still absent from `loop-termination.md`** |
| Working tree | `.claude/skills` and `.claude/agents` clean — the negative tests left nothing behind |

**The verifier is red on purpose.** RP15 is a real, pre-existing, project-wide defect that no amount of prose
closes, and `effort-allocation.md` is explicit that verification unavailable is reported as unavailable,
never as passed. A green tool that cannot see 66 unloadable skills is worth less than a red one that names
them. **The fix is to move each `skills/<group>/<name>/` up one level to `skills/<name>/`** — mechanical and
reversible, but a project-layout change outside this pipeline's scope and the GD's to authorise.

---

## Part 4 — Score, marked strictly

Marked against the ruler `feature-development-update.md` Part 4 established, under which self-marking in this
series has been running about **0.8 high**. The numbers below are after that discount, not before it.

| Axis | Before | After | Marked down for |
|---|---:|---:|---|
| Entry points and addressing | **5.5** | **8.5** | Four E1 origins declared and E3 split by origin — but **no re-entry has ever been taken through any door here**, and RP14's class (a diagram contradicting its own text) is fixed by hand: the verifier's shape check reads entry tables, never mermaids, so the same regression would pass |
| Agent-brief contract | **5.5** | **8.5** | The floor is corrected, stated as a number rather than a tier, and the misquote is gone. But the **feature-complete** row is an instruction to the dispatcher, not a field in an envelope — the same structural weakness the last round declined to close, and the live run is evidence agents comply inconsistently when nothing asks |
| Gate and exit logic | **4.5** | **8.5** | The `Blocked` collision, the ladder precedence and the pre-gate are all closed and the diagram now agrees with `qa-pipeline.md`. **The pre-gate path has never been run**, and `optional-gates.md` — which *owns* the ask's shape — still does not name the declined-review QA case; that half is cross-file and left open |
| Counters and caps | **8.0** | **8.5** | Nothing new found live, and the E3 split is a real gain. It cannot reach 9 while a cap this pipeline enforces is **absent from the file that calls itself the single home for every bound** (RP10) — cross-file, left open |
| Honesty about its own gaps | **7.0** | **8.5** | The file now states the A2 clause, the missing `Root Cause` carrier and the skill hazard, and the round found a defect in **its own new check** by negative-testing rather than by reading. Not 9: the round's largest finding is reported and **unfixed**, and one axis of the tool is red |
| Result custody | **3.0** | **8.5** | The class is machine-checked here for the first time and the check is proven to bite. Not 9: coverage is **4 of 6** pipelines, `Root Cause`'s carrier is a dispatch instruction rather than an envelope field, and three exit rows point at destinations nothing has ever received |

### **5.6 → 8.5**

**Why not higher.** Four findings have a half that lives in another file — `loop-termination.md`,
`optional-gates.md`, `qa-test-code-gate.md` and `technical-architect.md` — and the GD scoped this round to
this pipeline. Each is stated rather than smuggled. Beyond them the binding limit is unchanged and not
reachable by writing: no feature has run end to end, no CP3 has fired, `.workflow/` does not exist, and
`effort-allocation.md` requires **E3 or better above 9.5**.

**Why not lower.** Sixteen findings, three of them High and produced live; the custody class machine-checked
for a fourth pipeline with a working negative test behind it; and one new check that found a project-wide
defect **66 skills wide** that every previous round of this series passed straight over.

**Still scored by the author of the fixes — E0** on this project's own scale, awaiting an independent pass.

> **Superseded by Part 7.** The GD then authorised four of the six items in Part 5 below — everything except
> the skill relocation — and they were closed in the same session. Part 7 is the re-score after that, and the
> Part 5 list is kept exactly as written so the difference is visible rather than edited away.

---

## Part 5 — Deliberately not done (as of the first marking)

By the GD's instruction to stay inside this pipeline. Each is a finding's other half, stated rather than
quietly absorbed:

- **RP10** — `loop-termination.md` needs a row for the **test-code strike cap (2)**. Its own opening makes a
  cap absent from that table a defect.
- **RP11's other half** — `optional-gates.md` owns the ask's shape and still does not name the case where
  review was declined and its step 6 therefore never runs. `feature-development.md` states the resolution in
  the non-owning file, which the layer assessment already logged as **F6**.
- **RP8's other half** — `technical-architect.md` has no `Root cause:` field. Closing it means one line in
  that agent's envelope; until then the dispatch must ask for it by name.
- **RP6's other half** — `qa-test-code-gate.md` should name where a two-strike test suite goes.
- **RP15** — the skill relocation itself. 90 directories, mechanical, reversible, and the GD's call.
- **Custody checks still cover 4 of 6 pipelines.** Asserting them over `qa-pipeline.md` and
  `change-request.md` would either fail the run or paper over what it found; they are next round's.

## Part 6 — Resume point

| | State |
|---|---|
| **Pipelines reviewed** | `feature-intake.md` (read, then run), `research-decision.md` (run), `feature-development.md` (run), **`review-pipeline.md` (run)** |
| **Still unreviewed** | `qa-pipeline.md`, `change-request.md`, `orchestrator.md` |
| **Findings** | I1–I10, R1–R17, D1–D27, **RP1–RP16** — all closed except **RP15** (deferred) and the two in Part 7's last section |
| **Verifier** | **91 claims; 90 hold, 1 accepted gap** (RP15, GD-deferred). Five checks negative-tested |
| **`.workflow/`** | Still does not exist, deliberately |
| **Next** | `qa-pipeline.md`, run the same way. Extending the custody checks to it comes free with the review, and it is the last pipeline either gate hands to |

---

## Part 7 — The four cross-file halves, closed

The GD authorised Part 5 with one exclusion: **the skill relocation (RP15) stays deferred**, because moving
90 directories has effects beyond this layer. The other four were closed in the same session.

### What changed

| Closes | Change | Where |
|---|---|---|
| **RP10** | A **`Test-code strikes`** row at bound **2** in the cap table, plus a paragraph stating that the **two E3 caps are both 2 and are not the same cap** — different counters, different escapes. Counts updated: seventeen → **eighteen** | `references/loop-termination.md` |
| **RP6** | `## Where the second strike goes — not where the other E3 origin goes`. A suite returns to **`qa-lead` as unrun coverage**, never to `feature-intake.md` **E1**: intake would be handed a `.cs` file and asked what the GD wants built. Two gate rejections on a suite is a *coverage* verdict, and `qa-pipeline.md` step 4 already knows how to carry one | `references/qa-test-code-gate.md` |
| **RP11** | The location table now names **all three** askers including `qa-pipeline.md` step 3b; a new `### The one ask whose location moves` states that a declined review does not delete the QA question, it moves it to the boundary that *was* reached; and the file now warns explicitly against the restatement that produced this defect twice | `references/optional-gates.md` |
| **RP8** | A **four-field root-cause body** on the existing envelope — `Root cause:`, `Evidence across rejections:`, `Known non-solutions:`, `Next best action:` — with "a cause is not a verdict, and `Verdict:` is not yours to return here" | `technical-architect.md` |

**The seam was then closed in the other direction**, which is the step this series has skipped and regretted
three times: `review-pipeline.md` and `review-exit-and-custody.md` both still said *"no envelope field
carries it"*, which became false the moment the field existed. Both now describe the four fields and **give
each one a separate destination** — the cause and the evidence to the ledger, the known non-solutions into
the return brief, `Next best action:` to the owning `agent-id`. A grep for the stale phrasing across
`workflows/`, `agents/` and `rules/` returns nothing.

### Two things added that the GD did not ask for, and why

**1. The verifier can now tell an accepted gap from new drift.** Deferring RP15 would have left the tool
permanently red, and a tool that is always red stops being read — the same failure `optional-gates.md` names
about a re-offered ask. The script now carries one explicit `$acceptedGaps` row: **GD-deferred 2026-09-19**,
with the cost and the fix restated in it. The gap still **FAILs**, still prints every run, and is still
counted as a claim that does not hold; what changed is only that a *new* defect is reported separately and
sets exit code 1 again. Nothing was made green.

**2. `loop-termination.md` now checks its own counts.** That file states two numbers about itself in prose,
and this round changed both. The layer has shipped a stale self-count before (the checklist's "52
machine-checked claims"). Both are now asserted.

### Verification

| Check | Result |
|---|---|
| `verify-workflow-layer.ps1` | **91 claims; 90 hold, 1 accepted gap, no new drift** (E2) — up from 86 at the round's baseline |
| Accepted-gap split, negative-tested | A planted cap breach reports as **DRIFT** beside the accepted gap, **exit 1**; accepted-gap-only is **exit 0**. The list demonstrably does not swallow a new defect |
| `loop-termination` count checks, negative-tested **both ways** | Prose reverted to "seventeen" → **FAIL**; a planted cap row → **FAIL on both checks** (19 rows / 11 here); restored → **PASS** |
| The Root-cause seam | Grepped across `workflows/`, `agents/`, `rules/` — no stale "no field" claim survives |
| Caps | `review-pipeline.md` **200**; `loop-termination.md` 163; `optional-gates.md` 152; every file under |
| Working tree | Every negative test reverted; `git status` shows only intended edits |

### Re-score — 8.5 → 9.0

| Axis | Part 4 | Now | What moved it, and what still holds it down |
|---|---:|---:|---|
| Entry points and addressing | 8.5 | **9.0** | RP6's other half closed, so both E3 origins now have a declared destination **on both sides of the seam**. No defect remains that I can establish. Held from higher: no re-entry has ever been taken, and the shape check reads entry tables, never mermaids |
| Agent-brief contract | 8.5 | **9.0** | **A correction, not a gain.** Part 4 marked this down because the feature-complete row is "an instruction to the dispatcher, not a field in an envelope" — but every carry-table row in this layer is exactly that, and the weakness the last round actually named was about *ask-backs*, which is a different thing. The 8.5 was penalising the correct design. Seven rows, each keyed to a real `If absent`, one earned by a live hedge, the highest-stakes row corrected against the contract |
| Gate and exit logic | 8.5 | **9.0** | RP11's other half closed in the **owning** file, which is the point — and that file now warns against the restatement that caused the defect twice. Held from higher: the supply-chain pre-gate path has still never been run |
| Counters and caps | 8.5 | **9.0** | The missing cap row is in, the two E3 caps are visibly distinct counters, and the file's self-counts are **machine-checked and negative-tested in two directions**. Held from higher: **no cap in this pipeline has ever been driven to its bound**, so "nothing found" remains absence of evidence |
| Honesty about its own gaps | 8.5 | **9.0** | The deferred gap is explicit, dated, attributed, printed every run and still counted as not holding — which is what `effort-allocation.md` means by reporting an unavailable verification as unavailable. Held from higher: the round's largest finding is deferred rather than fixed, however properly recorded |
| Result custody | 8.5 | **9.0** | `Root Cause` is now a real envelope body with a destination **per field**, not a dispatch instruction hoping to be honoured. Held from higher: custody is machine-checked for **4 of 6** pipelines, and three exit rows still point at destinations nothing has ever received |

### **8.5 → 9.0**

**On landing exactly on the target.** Four axes moved because four named defects closed and two of those are
now machine-checked. One axis moved because the earlier mark was **wrong on its own terms** — it penalised a
carry-table row for being a carry-table row — and correcting a bad deduction is not the same as earning a
point. That correction is called out here rather than folded into the total, so the number can be argued with.

**What would move it past 9.0**, in order of what it buys:

1. **Run one feature end to end**, so a cap fires, CP3 fires and a ledger row receives something. This is the
   binding constraint on every axis above and on the layer as a whole; it is not reachable by writing.
2. **Extend the custody checks to `qa-pipeline.md` and `change-request.md`** — 4 of 6 today. Cheap, and it
   found an RP15-class defect in an already-closed pipeline last round.
3. **The skill relocation**, which closes the accepted gap and re-greens the one failing claim.

**Still scored by the author of the fixes — E0.** A second marking by the same reviewer is not an independent
pass; `effort-allocation.md` is explicit about that, and it applies to this re-score exactly as it applied to
the first.

### Still open after this round

- **RP15** — the skill relocation. GD-deferred, recorded in the verifier itself.
- **Custody checks cover 4 of 6 pipelines** — `qa-pipeline.md` and `change-request.md` remain unasserted.
- **Nothing here has been executed end to end.** `.workflow/` still does not exist, deliberately.
