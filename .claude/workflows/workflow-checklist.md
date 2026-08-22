# Workflow Build Checklist

> **What this tracks:** the progress of authoring the workflow layer itself — which part of which pipeline is
> written, and which the GD has reviewed and approved. It is not a per-feature runtime checklist.

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

## 1. Feature intake — `feature-intake.md`

| # | Part | Agents | Status | GD |
|---|---|---|---|---|
| 1.1 | Forward the request verbatim + attach track state | — (pipeline) | ✅ | ✔ |
| 1.2 | Triage → Simple / Medium / Complex, unconditional and first | `technical-architect` | ✅ | ✔ |
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
| 3.1 | Three entry points; Simple tier runs one agent and stops | — (pipeline) | ✅ | ✔ |
| 3.2 | Step 0 — the per-agent brief, each row keyed to a `Blocked` | — (pipeline) | ✅ | ✔ |
| 3.3 | Step 0 — the handoff matrix: which returned field feeds which brief | — (pipeline) | ✅ | ✔ |
| 3.4 | Shared Core first, forced by four agents' `Blocked` conditions | `csharp-engineer` | ✅ | ✔ |
| 3.5 | The fan-out waits on the Core submission's review verdict, and only that | `code-reviewer` | ✅ | ✔ |
| 3.6 | Complex tier — the Core contract reaches the GD as a notice, non-blocking | gd | ✅ | ✔ |
| 3.7 | Client fan-out — serial; **settled**, with the three escapes tested and rejected | `technical-artist`, `unity-engineer`, `ui-ux-programmer`, `tech-lead-sdk-platform` | ✅ | ✔ |
| 3.8 | Backend track — protocol before authority; depends on step 1 only | `netcode-engineer`, `server-authoritative-engineer` | ✅ | ✔ |
| 3.9 | Escalation lane, never a first dispatch; the SDK lead is exempt | `tech-lead-csharp-unity`, `tech-lead-performance` | ✅ | ✔ |
| 3.10 | Complex tier `README.md` — final dispatch, one owner per root | `csharp-engineer`, `unity-engineer` | ✅ | ✔ |
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

## Open decisions the GD owes

**None.** All seven are settled.

**Settled and removed:**

- ***G*** — **the passes-review/fails-QA bound is two rounds.** A submission that clears both gates but fails
  QA twice goes to `technical-architect` for root cause instead of a third fix, because three strikes counts
  *review* rejections and this loop would otherwise never terminate. Approved as written, with the file
  stating plainly that the bound is a pipeline decision and not a contract derivation.

- ***A*** — **CP3 gates QA execution, not QA planning.** `qa-lead` in plan mode needs only the Tech Spec and
  the tier, so it runs as soon as both gates clear and nothing it produces is invalidated by a CP3 rejection.
  Lives in `review-pipeline.md` step 6.
- ***D*** — **`review-pipeline.md` owns the two gates.** The reject → author → resubmit loop is a development
  cycle, not QA execution, and `feature-development.md` depends on a verdict from it mid-flight while QA does
  not. `qa-pipeline.md` step 2 is now a pointer.
- ***E*** — **neither `gd` nor `tech-lead-sdk-platform` by default.** `security-reviewer`'s own required-input
  table names what is missing — where the value is sourced from — so `Needs Confirmation` is an input to
  supply and re-run, never a verdict to escalate. The ladder is `tech-lead-sdk-platform` (it owns the config
  source) → the authoring agent → `gd` only when neither can name an origin. In `review-pipeline.md`.
- ***F*** — **the merged checkpoint is CP4.** `feature-intake.md`'s approved tier table already states it:
  Simple skips CP1 and CP2, merges CP3 into the single final checkpoint, and keeps CP4. The only competing
  reading came from the retired legacy roster doc, which the GD ruled out and which has since been deleted.

- ***B*** — a `Routed to: rd-engineer` becomes a GD ask, never an auto-dispatch, and the GD's yes is the
  explicit summon the agent requires. Pipeline 2 gets a GD gate only on its standalone path. Both now live in
  `research-decision.md` steps 2 and 5.
- ***C*** — the client fan-out is **serial, and settled rather than deferred**. One Unity Editor, three agents
  holding `mcp__unity-mcp__*` tools, and any `.cs` write forces a domain reload that ends another agent's Play
  Mode verification. Three escapes were tested and rejected — see `feature-development.md` step 2. The one
  concurrency that does work is review, which holds no Unity tools and writes nothing.

## Known gaps outside the five pipelines

| Gap | Why it matters |
|---|---|
| **No orchestrator file** | Nobody owns cross-run state: retry counters, "same submission" identity, track on/off, acting on `Routed to:` — and 3.11 now makes submission identity load-bearing, since a feature produces several |
| **Legacy roster doc deleted** | `.claude/docs/TEAM_STRUCTURE.md` was removed once its §6 criteria reached `change-request.md` — the only content nothing else carried. Recoverable at `git checkout a33f02b -- .claude/docs/TEAM_STRUCTURE.md` if anything turns out to have been missed |

## Authoring order

Pipeline 1 ✅ → 2 ✅ → 3 ✅ → 4 ✅ → 5 ✅ → `change-request.md` ✅ → **the orchestrator file**. All six are
written and GD-approved. One round per GD approval; this file is updated at the end of each.

**The workflow layer is complete.** What is left is the orchestrator — the one piece that holds cross-run
state, and the only reason the six approved files still name a caller that does not exist yet.
