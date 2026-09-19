# `change-request.md` — Review, scored against a real run and an independent pass

> **Working note.** Sixth in the series, after `feature-intake-update.md`, `research-decision-update.md`,
> `feature-development-update.md`, `review-pipeline-update.md` and `qa-pipeline-update.md`. Same method as the
> last four — the pipeline was not read into a score, it was **run** — plus one step none of the prior five
> took at this point in their own round: an **independent `code-reviewer` pass on the fix itself**, before any
> score was written down, rather than after.

## Part 0 — What was run, and what it buys

**Two real `technical-architect` dispatches**, chosen to hit this pipeline's two riskiest untested claims:

| # | Scenario | Feature shape | What it tested |
|---|---|---|---|
| 1 | A closed D3/U1 progression feature takes on real-money IAP + economy + anti-cheat scope at `qa-pipeline.md` CP4 (**E2**) | Never triggered `feature-intake.md`'s Advisor⇄Critic loop or CP1 | Whether Major's criterion ("invalidates an assumption `critic` stress-tested, or a risk the GD accepted at CP1") can even apply to a feature with no CP1 history |
| 2 | A mid-flight D4 feature (real CP1 history, a real accepted risk) receives one GD message bundling a mechanic redesign with a netcode-foundation swap (**E1**) | CP1 already ran once | Whether `Change severity:` can hold one value when part of a request is `cto`'s strategic call |

Both dispatches returned real, load-bearing findings rather than clean passes — see Part 1. A **third** dispatch,
`code-reviewer`, then reviewed the fixes this round made in response, before any score was written. Its findings
are Part 2b, and every CONFIRMED one is closed in Part 3.

**What this evidence is.** The two `technical-architect` dispatches are **E2** for claims about the
*specification* — real tool output, a reproducible wall. No code was written, no gate ran, no ledger was
committed, `.workflow/` still does not exist, and `feature-development.md`/`review-pipeline.md`/`qa-pipeline.md`
were not re-run with the fixed contract — this pipeline's own scope stops at handing off to them. The
`code-reviewer` pass is materially independent evidence for the *fix*, not for the layer's operational
readiness, which remains the standing limitation this whole series has never closed.

## Part 1 — What the two dispatches proved works, and what they broke

**The dispatch-brief discipline held.** Neither dispatch returned `Blocked`; both refused to force a
classification that did not fit rather than inventing history to make one fit — dispatch 1 explicitly declined
to "silently force this into Moderate by elimination, or invent a CP1 history that never happened," and
dispatch 2 explicitly declined to average two structurally different asks into one severity.

**Both found a real gap and diagnosed it correctly, not just symptomatically.** Dispatch 1 named the exact
clause in Step 3 that assumes every in-flight feature already has a CP1 to invalidate. Dispatch 2 named the
exact reason sequencing matters (`critic`'s re-stress-test can depend on which netcode foundation is chosen) —
not asserted, reasoned from the specific finding a prior CP1 in this same scenario had produced.

**Re-reading all five axes worked exactly as designed.** Dispatch 1 moved D3→D4, C3→C4, U1→U3, R1→R3, X1→X3 —
each cited to a specific `task-classification.md` table entry — and correctly deferred acceptance criteria and
module boundaries as `Pending CP1` rather than inventing a settled direction. That improvisation is now a
stated contract rule (M1/M2 below), not left to a second agent's luck.

## Part 2 — Findings from the two dispatches

Two findings, both structural and both confirmed by the dispatch reasoning itself, not by inspection alone.

### CR1 — The Major criterion assumes a prior CP1 exists

False for any D1–D3/U0–U1 feature — `feature-intake.md`'s loop never fires below D4–D5 or U3, so `critic` never
ran and no risk was ever accepted at a checkpoint that never happened. Dispatch 1 hit this directly and
classified Major on a *functional* ground instead — the reclassified axes now force CP1 for the first time —
flagging the literal criterion as a gap rather than silently reinterpreting it.

### CR2 — `Change severity:` cannot hold one value when a request bundles a severity-ratable part with a `cto`-strategic part

Dispatch 2's netcode-foundation swap is `cto`'s call regardless of the mechanic redesign's own severity, and the
two need sequencing: the technology answer can change what `critic`'s re-stress-test is even testing.

## Part 2b — The independent review, and what it found in the fix itself

Dispatching `code-reviewer` against this round's own diff — before scoring it — is the one thing this round did
that the first five did not do at this stage. It returned **`Verdict: Request changes`**, with four CONFIRMED
High findings and eight CONFIRMED Medium/Low findings, none invented — every one cites the exact conflicting
line on both sides.

| # | Sev | Finding |
|---|---:|---|
| **H1** | High | `change-request.md`, its diagram and the new reference file all sent the `cto` half of a bundled request to `research-decision.md`'s "**`cto` step**" directly — but that pipeline is explicit that `cto` "is never entered without a candidate set" and that entering at step 0 runs the full depth check and research pass first. As written, the new route also named no `E\d`, so the verifier's own cross-file entry check could not see it |
| **H2** | High | `research-decision.md` and its exit reference promised a return **into** `change-request.md`, which declared no such door — recreating, on the same file, the exact class `qa-exit-and-custody.md` cites this file as the historical example of |
| **H3** | High | The new "first-time CP1" Major shape resumes at **CP1** with nothing for CP1 to approve — no `advisor` Options, no `critic` Risk Findings, no locked direction, because the loop that produces all three never ran. Sending it straight to a checkpoint asks the GD to approve a direction nobody proposed |
| **H4** | High | `loop-termination.md` — "**the single home for every bound in the layer**" — still stated Major's *old*, single-shape definition, contradicting the pipeline it claims to only record |
| **M1** | Med | `technical-architect.md`'s "`Module boundaries:` **onward**" and the reference's explicit six-field list disagreed in both directions once checked against the envelope's real field order |
| **M2** | Med | Deferring `Acceptance criteria:` at Major collides with `critic`'s own required input — "a risk is only a risk relative to a goal" — with no stated stand-in |
| **M3** | Med | `feature-intake.md`'s **E5** carried-in cell required "which risks the GD accepted" with no allowance for the legitimate empty case |
| **M4** | Med | `research-decision.md`'s exit mermaid still hard-coded one destination while its own exit table now has five rows across four origins |
| **M5** | Med | The `researcher`/`rd-engineer` → `Rejected` routing row had no answer for a `change-request.md`-origin dispatch, and its generic destinations would have broken this pipeline's own Step 1 halt |
| **M6** | Med | Two live-state rows in `workflow-checklist.md`'s debt register were already stale — the claims count and the custody-coverage fraction |
| **M7** | Med | The verifier's own custody-check comment still described a three-pipeline scope after this round widened it to six |
| **L1** | Low | The extended custody check **passes vacuously** for `producer`'s two destinations in `change-request.md` — a case-insensitive substring match, not a per-agent row check. One of the two destinations was also a genuine missing routing row, independent of the check's precision |
| **L2** | Low | Two more files' *rationale* for the round-count reset (not their definition) still read as though a prior round always existed |
| **L3** | Low | `research-decision.md` sits at exactly 200/200 lines — zero headroom for the next round |
| **L4** | Low | The new cross-pipeline dispatch to `research-decision.md` did not name the four standard values every re-entry carries |

Four items were checked and found sound rather than flagged: the `Pending CP1` convention does not collide with
the CP2 rejection taxonomy; no stale "three origins" claim survives anywhere in `.claude/`; the `Produces`
custody half for this pipeline is genuine, not vacuous, including the two-artifact cell; and entry-point
bookkeeping for **E1**/**E2** was undisturbed.

## Part 3 — What changed in response

Every CONFIRMED H/M finding is closed. L1's concrete instance (the missing `producer` row) is closed; its
general recommendation (tighten the check's matching precision layer-wide) is recorded as a known residual
rather than attempted this round, per the effort-allocation rule against expanding scope mid-fix.

| Closes | Change | Where |
|---|---|---|
| CR1, H3, H4 | Major restated with two shapes; the second shape's resume point corrected to **step 3** (stating the D4–D5/U3 shape explicitly, so the semantic shape-checker can see it) rather than a bare CP1 with nothing to approve; the 0→0 round-reset case stated as legitimate, not vacuous | `change-request.md`, `feature-intake.md` **E5**, `references/entry-index.md`, `references/loop-termination.md`, `references/intake-advisor-critic-loop.md` |
| CR2, H1 | The bundled-severity split, with the `cto` route corrected to **`research-decision.md` E2** (never "the `cto` step" directly) and the sequencing reasoning restated against that entry | `change-request.md`, new `references/change-severity-and-custody.md` |
| H2 | A new **E3** declared on `change-request.md` — the return address `research-decision.md` already promised — mirrored in `references/entry-index.md` | `change-request.md`, `references/entry-index.md` |
| M1, M2 | The agent contract names the same six deferred fields as the reference, by name rather than "onward"; a stand-in for `Acceptance criteria:` (the GD's own words for the change) added so `critic` does not block at the reopened loop | `technical-architect.md`, `references/change-severity-and-custody.md` |
| M3 | `feature-intake.md` **E5**'s carried-in cell states the empty-history case explicitly | `feature-intake.md` |
| M4, M5 | The exit mermaid relabeled to point at the door table rather than one destination; the peer-rejection row gains a `change-request.md`-origin clause | `research-decision.md` |
| M6 | Both stale debt-register rows corrected — claim count and custody fraction | `workflow-checklist.md` |
| M7 | The custody-check comment and the now-always-true INFO line corrected/guarded | `tools/verify-workflow-layer.ps1` |
| L1 (instance) | The missing `producer` → `Needs-decision`, `Routed to: technical-architect` row added; the check's own imprecision recorded rather than silently trusted | `change-request.md`, `workflow-checklist.md` |
| L2 | One clause each, in the two files restating Major's rationale | `references/entry-index.md`, `references/intake-advisor-critic-loop.md` |
| L4 | The four standard values named as part of what the `cto`-route dispatch carries | `change-request.md` |

**One fix caused a real regression, caught before it shipped.** Restating **E5**'s resume point as "step 3"
without also stating the shape made the verifier's own semantic shape-check fail — correctly: that check exists
precisely to catch an entry resuming at a shape-gated step without naming the shape, the exact **I9** class this
whole series keeps re-finding. It was found by re-running the verifier immediately after the edit, not by
re-reading the prose, and fixed by stating the shape in both `feature-intake.md` and `entry-index.md`.

## Verification

| Check | Result |
|---|---|
| `verify-workflow-layer.ps1`, before this round | OK — 95 claims, 94 hold, 1 accepted gap |
| after the first pass (self-authored fix) | OK — 97 claims, 96 hold, 1 accepted gap |
| after the independent-review fixes | **Regression**: 98 claims, 1 new DRIFT (the E5 shape-check) |
| after fixing the regression | **OK — 98 claims checked; 97 hold, 1 accepted gap, no new drift** |
| Negative test: planted an orphan `Produces` artifact in `change-request.md` | **FAIL**, naming it exactly · reverted → PASS |
| Negative test: the E5 shape-check firing on the round's own regression | **FAIL on the actual mistake, PASS once corrected** — not a synthetic plant, a real one caught live |
| 200-line cap | `change-request.md` 151, `research-decision.md` **200/200 — zero headroom**, `feature-intake.md` 199, `entry-index.md` 72, `loop-termination.md` 177, `intake-advisor-critic-loop.md` 76, `change-severity-and-custody.md` 79, `technical-architect.md` 101 |
| The seam, both directions | Grepped for "three origins" (none survive), the stale "cto step" phrasing (none survive), and every cross-file entry reference — the independent reviewer traced these directly rather than trusting the grep alone |

## Part 4 — Score

Marked against the ruler `feature-development-update.md` Part 4 established (self-marking in this series runs
~0.8 high) — but this round's numbers already reflect an independent pass baked into the process, not applied
as an after-the-fact discount. They are reported as landed, not further discounted for an effect already spent.

| Axis | Score | Why |
|---|---:|---|
| Entry points and addressing | **9.0** | Both doors (**E1**/**E2**) were clean from the start; the new **E3** and the E5 resume-point fix closed two real cross-file contradictions (H2, H3), the second one caught live by the verifier regressing on the fix itself. No re-entry has ever actually been taken through any door here — the ceiling this shares with every pipeline in the series |
| Severity/checkpoint logic | **9.0** | The two-shape Major criterion and the bundled-severity split are both grounded in real dispatch reasoning, not invented, and both live contradictions with `feature-intake.md`/`loop-termination.md` (H3, H4) are closed with the same wording on both sides |
| Agent-brief contract | **8.5** | The deferred-fields convention is now precise (M1) and no longer starves `critic` of a goal (M2) — but it is a genuinely new convention verified only through two dispatches and one independent read, never through a second dispatch confirming the *corrected* text produces cleaner output |
| Counters and caps | **8.5** | The 0→0 reset case is stated consistently in four files now, but no cap in this pipeline has ever been driven to its actual bound — "nothing else found" remains E1 evidence for this axis specifically |
| Honesty about its own gaps | **9.0** | An independent gate ran *before* a score was written, not after one was inflated — the first time in this series at this exact point in the round. It found a real regression in this round's own fix and the fix is recorded, not smoothed over. L1's check imprecision is stated as a known residual rather than silently trusted |
| Result custody | **8.5** | Custody coverage reaches all six pipelines with a genuine negative test — but the independent pass also found the extending check itself passes vacuously on short/common destination ids (L1), which is recorded rather than fixed this round |

### **8.8**

**Why not higher.** `effort-allocation.md` requires **E3 or better above 9.5**; the binding limit is unchanged
across this whole series and not reachable by writing: `.workflow/` still does not exist, no cap here has fired,
and the fix was never re-dispatched a second time to confirm the corrected contract text produces output as
clean as the live dispatches that found the original gaps. L1's regex imprecision is a real, if minor, standing
weakness in the one mechanism (`verify-workflow-layer.ps1`) this whole series relies on to keep a fix from
regressing silently.

**Why not lower.** Two real dispatches found two structural defects neither prior reading of this file nor the
prior five rounds' methodology had surfaced; an independent review of the fix — run *before* scoring, which no
prior round in this series did at this stage — found four further CONFIRMED High findings and closed all of
them; and one of those closures caught a live regression in the round's own work via the verifier, not via a
second read.

**Scored by the author of the fixes for the final pass — E0** on this project's own scale, same caveat every
prior round in this series carries. The independent `code-reviewer` pass is real, materially independent
evidence for the *fixes*, but the final aggregation into one number was not itself independently checked.

## Part 5 — Deliberately not done

- **L1's general fix** — tightening the custody check's destination match from a substring test to a
  per-agent-row test. This is a layer-wide change to a mechanism all six pipelines' checks depend on, and
  applying it without re-verifying all six is exactly the "fixing an instance does not close the class, and a
  wide fix without a wide re-check is its own risk" lesson this series has learned twice already. Recorded in
  `workflow-checklist.md`'s debt register as the next fix, not made.
- **`research-decision.md`'s zero line headroom (L3)** — noted, not addressed. The next addition to that file
  needs a promotion or a compression pass first.
- **A third dispatch confirming the corrected contract text** — would raise Agent-brief contract's evidence
  grade from "reasoned about" to "reproduced," and was not run this round for the same reason the other five
  rounds stopped where they did: marginal cost against a result already reasoned through twice.
- **Re-running `feature-development.md`/`review-pipeline.md`/`qa-pipeline.md` against a rework list this
  pipeline actually produced** — out of this pipeline's own scope; it hands off to them and stops.

## Part 6 — Resume point

| | State |
|---|---|
| **Pipelines reviewed** | `feature-intake.md` (read, then run), `research-decision.md` (run), `feature-development.md` (run), `review-pipeline.md` (run), `qa-pipeline.md` (run), **`change-request.md` (run, then independently reviewed before scoring)** |
| **Still unreviewed** | `orchestrator.md` — the last one, and the ignition every other pipeline depends on |
| **Findings** | CR1, CR2 from the live dispatches; H1–H4, M1–M7, L1–L4 from the independent review — all CONFIRMED findings closed except L1's general fix (recorded, deferred) |
| **Verifier** | **98 claims; 97 hold, 1 accepted gap (RP15, GD-deferred), no new drift** — including one regression this round introduced and then caught via the same tool |
| **`.workflow/`** | Still does not exist, deliberately |
| **Next** | `orchestrator.md`, run the same way. It is the one file every mode and every lane in the layer depends on and has never been reviewed at all — the natural close of this series |
