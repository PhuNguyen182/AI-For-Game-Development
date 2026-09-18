# `feature-development.md` — Review, scored against a real run

> **Working note.** Third in the series, after `feature-intake-update.md` and `research-decision-update.md`.
> Same method as the second: the pipeline was not read into a score, it was **run** — four real agent
> dispatches following the files literally, recording where they hit a wall.

## Part 0 — What was run, and what it buys

The previous round's resume point said the next action was *"run the same treatment on pipeline 3"*. This is
that. Every return quoted below is a real envelope from a real dispatch.

**The feature.** A Tech Spec section for *Stamina & Dodge Roll (co-op, server-authoritative)* — a stamina
pool with a 0.6 s regen delay, a 35-cost dodge roll, an 18-tick duration with i-frames on ticks 3–11, all
tick-deterministic so the client predicts it and the server re-simulates it. Classified **A4 — D4 C3 U1 R1
X1**, attempt budget 4, verification floor **V3**, backend track **on**. That shape was chosen because it is
the only one that fires step 1, step 2, step 3 and step 4 at once.

| # | Step | Agent | Returned |
|---|---|---|---|
| 1 | step 1 — Shared Core | `csharp-engineer` | `Done` — three files, a full public contract, written into a scratch tree |
| 2 | step 2 — the SDK slot | `tech-lead-sdk-platform` | `Blocked` — plus six risks it had nowhere to put |
| 3 | step 3 — the protocol | `netcode-engineer` | `Needs-decision` → `cto`, plus a complete message contract |
| 4 | step 5 — the submission | `code-reviewer` | `Request changes` — ten findings, **three** routing destinations |

**What this evidence is.** Every defect below was produced by following the files as written and hitting a
wall, which is **E2** for claims about the *specification*. It is not evidence the layer works in production:
no Unity project exists in this repository, so the three Editor-holding agents in step 2 were never
dispatched and step 2's serial claim remains **E1 — inspection**. Stated rather than rounded up.

**The scratch tree was deliberately outside the repository** and no `.workflow/` was created, for the reason
`research-decision-update.md` Part 5 gives: a dry run must not become fake state.

---

## Part 1 — What the run proved works

**The handoff matrix held, live and two hops deep.** `netcode-engineer` was given exactly what
`development-brief.md` says to forward — `Public contract:`, `Determinism:`, `Assumptions and known
limitations:` — and returned `Blocked — needs from caller:` naming *only* the netcode foundation. It designed
its wire format directly off the Core's public restore constructors, which is the matrix doing precisely what
it was written for.

**The Core-first ordering is not a preference, and the run showed why.** The reviewer's F3 found that
`DodgeRollState`'s restore constructor does not clamp, so a client at an out-of-range tick and a server at
zero *behave* identically but compare unequal forever. Four agents would have built on that contract.

**The review gate independently found the defect this review had predicted.** Its F10 reads: *"`Verification
done:` … while the actual verification story … sits under `Known limitations:` … The known-gap row in that
file's own table predicted exactly this."* That is corroboration from a materially different source, not a
second pass of the same reasoning.

---

## Part 2 — Findings

Numbered **D1–D26**. The ones marked **live** were produced by a dispatch, not by reading.

### The root cause under most of them

**This pipeline's routing table read `Status:` and `Routed to:`, and nothing else.** Three live returns,
three different statuses, and in every one the highest-value content sat in a field no routing row mentions:

| Return | Status the table routes on | What the table would have discarded |
|---|---|---|
| `tech-lead-sdk-platform` | `Blocked` → "ask for the input named" | Six risks, including a **cross-track design flaw** (a client-side Remote Config flag governing an action the server re-simulates) and a **`security.md` §7 supply-chain gate** on a `.unitypackage` |
| `csharp-engineer` | `Done` → "submit it, hold the fan-out" | A V3 verification account filed under `Assumptions`, and a stated precondition on the fan-out |
| `netcode-engineer` | `Needs-decision` → "hand to `research-decision.md`" | A complete `Message contract:` that `server-authoritative-engineer` returns `Blocked` without |

This is the **custody class** the debt register says was closed instance by instance and never as a class:
*an agent produces something no pipeline row receives.* It is the same class as R1, R9 and R10 one pipeline
over.

### The findings

| # | Finding | Sev |
|---|---|---|
| **D1** | **The pipeline declared no exits**, while `review-pipeline.md` **E1** and `qa-pipeline.md` **E1** and **E3** each name it as their origin. *(The first draft of this row claimed it was "the only one of six" without one. That is false — checked afterwards, **five of six** have no hand-on section, `feature-intake.md` alone does. The defect is real; the comparison was invented, and it is left here corrected rather than deleted.)* | High |
| **D2** | **live** — `Risks flagged:`/`Config required:` routed only on `Done`; they arrived on a `Blocked` | High |
| **D3** | **No route for a design flaw.** Invariant **I5** appeared nowhere in a pipeline dispatching nine agents. The live run raised one on its *first* dispatch | High |
| **D4** | **Third-party content is adopted before the gate that must clear it.** `security.md` §7 forbids treating a `.unitypackage` as adopted until `security-reviewer` clears it; the optional gate judges afterwards, by which time the `Editor/` `[InitializeOnLoad]` payload has run | High |
| **D5** | **live** — the Implementation Note's `Attempts:` and `Verification done:` have **no source in any envelope**. One agent volunteered attempts, another did not; the Core filed its V3 account under `Assumptions`; the gate reported the split as F10 | High |
| **D6** | `tech-lead-sdk-platform` has no `Assumptions and known limitations:` field — the one `implementation-note.md` calls highest-value, and the one that feeds `DEBT.md` from A3. Live, it wrote them outside the envelope | Med |
| **D7** | **Both tech leads write code that reached no gate.** Both hold `Write`/`Edit`, both return `Fix:`, and "silent to the GD" was being read as silent to the gates — invariant **I10**'s named hole | High |
| **D8** | `Scope of pattern: project-wide` had no home. It is `cto`'s `Standard set:` one level down, and R10 already established that a project-wide rule with no ledger row survives only in its own conversation | Med |
| **D9** | Measured numbers — `Performance:`, `Cost:`, `Before / After:` — never reached the ledger's `Baseline:` row, which `state/README.md` says exists to stop *a run silently becoming the baseline* | Med |
| **D10** | **live** — the **feature root** never travelled. Intake makes the architect name it; the brief's rows did not carry it. The first dispatch blocked on it | Med |
| **D11** | Step 0 said "the **six** things", listed seven, and omitted the **track-standards-by-path** row — the row that *is* the loading mechanism now standards are no longer auto-loaded | Med |
| **D12** | **E2 said "no documents" (keyed to D) while step 4 keys them to A.** A D1 credential change is A5 and owes `LEDGER.md` decisions and `DEBT.md` — the exact direction §8's split exists to prevent | Med |
| **D13** | **The mermaid never branched on shape.** E2 entered the same node as E1 and could fall through to `feature-intake.md` **E3 — step 6**, which runs at D3–D5 only. I9's family, in this pipeline's own diagram, where the verifier's shape check does not look | Med |
| **D14** | `netcode-engineer → cto` named a *step*, not a door; `tech-lead-* → cto` named **E2**, declared as the architect's | Med |
| **D15** | Self-description drift: `{{ }}` claimed twice and present once; the escalation lane "not drawn above" while drawn; `implementation-note.md` citing a **step 5** that did not exist, and "all **six** fields" of an eight-field note | Low |
| **D16** | E3's origin list was stale **again** — three named, five real (gated-direct and `change-request.md` missing). The same row checklist 7.16 already corrected once | Med |
| **D17** | The review ask fired in two places while the file said *"ask once for the feature … the answer is about the work, not the artifact"*, against `optional-gates.md`'s bound worded per **artifact** | Med |
| **D18** | The QA ask had no owner when review was declined: `optional-gates.md` puts it at `review-pipeline.md` step 6, which never runs | Med |
| **D19** | **live** — no netcode-foundation row anywhere, and the agent's absent-behaviour is `Needs-decision → cto`: a strategic-decision pipeline spent on a lookup | Med |
| **D20** | An **unreachable** verification floor is undefined. Live, the floor could not be met because no toolchain existed; the author reported it honestly and the gate answered *"the caller owns the environment gap"* | Med |
| **D21** | **live** — the Core's own limitations never reached the gate ask they are the answer to. `optional-gates.md` wants the cost of skipping *named concretely*, and *"the Core was not compiled"* is that name | Med |
| **D22** | **live** — `Needs-decision → cto` did not distinguish *undecided* from *not carried* | Med |
| **D23** | **live** — returns naming more than one destination had no row. The gate returned **three**, each owning a different finding set. `research-decision.md` already had this rule; this pipeline did not | Med |
| **D24** | **live** — **an axis moving mid-development had no route.** The gate found two textbook **U2**s on a feature classified U1 and said the tier should be A5/V4. `entry-index.md` freezes D/C/R/X on re-entry, `change-request.md` is for a GD change, and this was neither | High |
| **D25** | **All nine declared `Produces` artifacts were named nowhere else.** Found by the new verifier check, not by reading — intake and research pass the same check | High |
| **D26** | **The other half of the seam.** `research-exit-and-custody.md`'s exit table had no row for a development-originated escalation, so both `cto` routes would have been handed back into `feature-intake.md` — reopening a Tech Spec the fan-out is already building against | High |
| **D27** | **Found by the tightened check, in `research-decision.md` — a pipeline this series already scored 8.9.** `researcher` and `rd-engineer` both return `Rejected`, `Routed to: unity-engineer` when handed production work (*"you research, you never integrate"*), and that pipeline had no peer-rejection row at all. It bites hardest at **E5**/**E6**, where the GD names the task directly | Med |

---

## Part 3 — What changed

Two new reference files, four amended, three pipelines' worth of seam, one rule corrected, two new
machine checks. `feature-development.md` went **197 → 199** lines against a 200 cap — everything else was
paid for by promotion or compression, never by deleting reasoning.

| Closes | Change | Where |
|---|---|---|
| D1, D5, D6, D7, D8, D9, D20, D25 | **`references/development-exit-and-custody.md`** — new. The nine deliverables and what each becomes; the five things a submission carries; the two Note fields no envelope can source; the exit doors; the custody table; and the three returns that do not wait for an exit | new reference |
| D10, D19, D5, D6, D21 | The brief goes **seven rows → nine**, gaining the **feature root** and the **netcode foundation**, plus a `## What the brief asks the agent to state back` block for attempts, verification and the SDK lead's assumptions | `development-brief.md` |
| D2, D3, D22, D23, D24, D7, D14 | Seven routing rows added or rewritten, including *route on the envelope, not on `Status:` alone* and *a return says the classification is wrong* | `feature-development.md` |
| D11, D12, D13, D15, D16, D17, D18 | Step 0's count and its missing row; E2's document clause re-keyed to **A**; E3's five origins; the mermaid branching on shape and naming both shapes at the `Gap` node; the ask shapes; the legend | `feature-development.md` |
| D4 | The supply-chain pre-gate stated: third-party content reaches `security-reviewer` **before** it lands, as its own submission — not the optional gate | `development-exit-and-custody.md` |
| D26 | The exit table gains a third origin and names it; `research-decision.md`'s **E2** row and its upstream table admit `feature-development.md` | `research-exit-and-custody.md`, `research-decision.md` |
| D15 | `step 5` now exists as a heading; the rule's "six fields" corrected to eight, and the `Attempts:`/`Verification done:` source rows corrected to point at the return | `feature-development.md`, `rules/implementation-note.md` |
| cap | The seriality argument promoted — read only when somebody proposes parallelising | `development-fan-out.md` (new) |

### Fix **J**, done and negative-tested

Both previous notes named **J** as *"the only remaining route to 9.0 that does not require a real Unity
project"*. It is now in `tools/verify-workflow-layer.ps1`:

| Check | Negative test |
|---|---|
| **No `Produces` artifact nothing receives** | Removing the nine-deliverables table → **FAIL**, naming all nine orphans. Restoring → PASS |
| **No destination without a routing row** | Planting `Routed to: qa-lead` in `researcher.md` → **FAIL**. Removing it → PASS. `qa-lead` was chosen deliberately: it *is* named in the shared references, so this test only passes if the scope was actually tightened |

**Three defects had to be driven out of these two checks, and all three were found by negative-testing rather
than by reading them.** They are recorded because they are the exact failure this layer keeps having — a
check that looks right and tests nothing:

1. **Scope included the agents table**, so every artifact matched its own declaration. Both checks passed
   with their fixes deleted.
2. **Scope pulled in every reference the pipeline mentions**, including `entry-index.md`,
   `optional-gates.md` and `standalone-runs.md` — which between them name most of the roster, so a
   destination could pass on somebody else's sentence. Now only the pipeline's **own** `development-*`,
   `intake-*` or `research-*` references count.
3. **The artifact match was case-insensitive**, so `Server Authority` was being "received" by the incidental
   phrase *"server authority assumes the strictest tolerance"* in an unrelated row of
   `development-brief.md`. Nine orphans were being reported as eight.

Tightening it immediately produced **D27** — a missing routing row in `research-decision.md`, a pipeline this
series had already scored and closed. That is the check earning its place rather than ratifying the author.

**Scope is the three reviewed pipelines.** The verifier prints the other three as *not yet asserted* rather
than silently claiming them — extending it is the next round's work.

### Verification

| Check | Result |
|---|---|
| `tools/verify-workflow-layer.ps1` | **OK — 86 claims, every one holds** (E2) — up from 80 |
| Both new checks against the defects they were written for | **FAIL on revert, PASS on restore** — E2, negative-tested, not asserted |
| 200-line cap | `feature-development.md` **199**, `feature-intake.md` **199**, `research-decision.md` **199** |
| The seam, both directions | Grepped, not assumed — which is what found **D26**, in the file the last round created |
| The planted negative tests | `git status .claude/agents` clean; the scratch tree is outside the repository |

---

## Part 4 — Score, marked strictly

**This section was rewritten.** The first version of it scored **9.0**. The GD then asked for a stricter
pass, which was spent re-auditing this round's own output rather than re-weighting numbers — and it found
three defects in the two new checks, one false comparative claim, and a legend this round re-broke after
fixing. The 9.0 did not survive that. What follows is the second marking, and the first is quoted at the end
rather than deleted.

| Axis | Before | After | Marked down for |
|---|---:|---:|---|
| Entry points and addressing | **5.5** | **8.5** | The doors are named and the seam is closed both ways, but **no re-entry has ever been taken** through any of them. D13's class — a diagram that does not branch on shape — is fixed **by hand**: the verifier's shape check reads entry tables only, so a regression in the mermaid would pass |
| Agent-brief contract | **6.5** | **8.0** | The three ask-backs are **instructions to the dispatcher, not fields in an envelope** — the same kind of thing that already failed here, since the live run showed agents comply inconsistently when nothing asks. `implementation-note.md`'s own Deferred debt names the real fix (a field on seven envelopes), and this round declined it |
| Gate and ask logic | **6.0** | **8.0** | The "one review ask per feature" resolution is stated in `feature-development.md` while `optional-gates.md` — which *owns* the ask's shape — still words its bound per **artifact**. Resolving a contradiction in the non-owning file is the one-fact-one-home slip the layer assessment already logged as **F6**. The supply-chain pre-gate also routes into `review-pipeline.md`, which was out of scope and has not been told it will receive a package import |
| Counters and caps | **9.0** | **8.5** | Two passes found nothing, one of them live — but **no cap was ever driven to its bound**. "Nothing found" here is absence of evidence at **E1**, and it was scored 9.0 twice on that basis |
| Honesty about its own gaps | **7.0** | **7.5** | The *file* is more honest and now partly machine-enforced. The *round* was not: a false comparative ("the only one of six") shipped in a round about self-description drift; two checks shipped with three defects **after** a memory was written saying to negative-test everything; and the legend fix was re-broken by a later edit in the same round |
| Result custody | **3.0** | **8.5** | The class is machine-checked and the check now bites — but it covers **3 of 6** pipelines, three destinations are ledger rows that have never received anything, and the `Attempts:`/`Verification done:` closure is a brief instruction rather than a carrier |

### **6.2 → 8.2**

**The strict pass cost 0.8**, which is the third time in this series that a harder look has cost roughly that
much: `feature-intake.md` went 9.0 → 8.2 when it was run, `research-decision.md` 7.0 → 5.9 when its
standalone half was run, and this one 9.0 → 8.2 when its own output was audited. **Self-marking in this
series has been running about 0.8 high, consistently.** That is the most useful number in this note.

**It also re-prices the other two pipelines.** They were marked **8.9** under the looser ruler, and one of
them has now been shown to be worth less: **D27** — a missing peer-rejection routing row in
`research-decision.md` — was found by the tightened check, in a pipeline this series had already closed.
Under this ruler neither earlier 8.9 is safe, and only the one with evidence is being restated here.

**Why not lower.** The findings are real and closed, the seam is closed in both directions, and the custody
class is the first thing in this layer ever closed as a *class* with a working negative test behind it. Three
of the six axes rest on machine checks that have been shown to fail on the defect they were written for.

**Why not higher.** `effort-allocation.md` requires **E3 or better above 9.5**, and the binding limitation is
unchanged: no Unity project exists here, the three Editor-holding agents were never dispatched, step 2's
serial claim is still **E1**, and every ledger row this round writes into has still received nothing.

**Still scored by the author of the fixes** — **E0**. A second self-marking is not an independent pass; it is
the same reviewer being stricter, which is exactly what `effort-allocation.md` says does not count as
independent verification. The number moved because the *audit* found new facts, not because the scale did.

> **Superseded, kept for the record.** The first marking of this round read: *Entry points 9.0 · Agent-brief
> 9.0 · Gate and ask 9.0 · Counters 9.0 · Honesty 9.0 · Custody 9.0 — **6.2 → 9.0***. Every one of those six
> was written before the re-audit that produced D27 and the three check defects.

---

## Part 5 — Deliberately not done

- **`review-pipeline.md`, `qa-pipeline.md`, `change-request.md` and `orchestrator.md` were not touched**, by
  the GD's explicit instruction to stay inside the three pipelines under review. Two findings have a half
  that lives there and is therefore left open, stated rather than smuggled:
  - **D20's review half** — `review-pipeline.md` turns a `Verification done:` below the floor into
    `Request changes` **+ a strike**, and says nothing about a floor that was *unreachable*. The live gate
    handled it correctly by judgment (*"do not close as verified"*, no strike), so the behaviour is right and
    the rule is unwritten.
  - **D23's gate half** — `review-pipeline.md` has no row for a return naming several destinations either,
    and the live gate returned three.
- **The custody checks cover three of six pipelines.** Asserting them over the unreviewed three would either
  fail the run or paper over what it found.
- **`implementation-note.md`'s `Deliberately out of scope` proxy** stays Deferred, unchanged — closing it
  still means a field on seven agent envelopes, and no round trip has yet proved that worth paying.

## Part 6 — Resume point

| | State |
|---|---|
| **Pipelines reviewed** | `feature-intake.md` (read, then run), `research-decision.md` (run), `feature-development.md` (run) |
| **Still unreviewed** | `review-pipeline.md`, `qa-pipeline.md`, `change-request.md`, `orchestrator.md` |
| **Findings** | I1–I10, R1–R17, **D1–D26** — all closed except the four in Part 5 |
| **Verifier** | **86 claims**, all passing; the two custody checks negative-tested |
| **`.workflow/`** | Still does not exist, deliberately |
| **Next** | `review-pipeline.md`, run the same way. It is the natural next target: it is where two of this round's open halves live, and extending the custody checks to it comes free with the review |
