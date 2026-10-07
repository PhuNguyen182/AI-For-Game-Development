# QA Track — Defect Reporting

Applies to: QA Lead, Code Reviewer, Security Reviewer, QA Automation Engineer, Playtest Tester, Performance QA Engineer, Build Verification Tester.

This file governs **how a QA agent states a finding** so that whoever receives it can act without asking a follow-up question. It does not change any agent's scope — each still reports in its own output shape from its agent file; this file sets what the fields in that shape must contain. Companion file: `verification-standards.md`, which governs when a claim counts as verified.

## Every finding carries five things

A finding missing any of these is not reportable — either complete it or state plainly that you could not.

| Element | What it must contain |
|---|---|
| **Location** | The exact anchor: `path:line` for code, the scene and entry point for a playtest, the artifact path for a build, the scenario and metric for a measurement. Never "somewhere in the combat system". |
| **Expected** | What should have happened, and the source that says so — a Tech Spec clause, a GDD scenario, a stated budget, a rule file. A finding whose expectation is only the reporter's opinion is a design question, not a defect. |
| **Actual** | What actually happened, stated as observed behaviour rather than as a diagnosis. |
| **Evidence** | The artifact that proves it: a log excerpt, a screenshot, a measurement with its run spread, a failing assertion, or the quoted line of code. Never a recollection, never "I noticed that". |
| **Owner** | The `agent-id` that owns the fix, per that agent's own scope. If no single owner is evident, say so and route the routing question rather than guessing. |

## Severity

Severity describes **impact if shipped**, never effort to fix and never the reporter's confidence. Assign from the first row that matches.

| Severity | Criterion |
|---|---|
| **Critical** | Data loss, a crash or hang, a leaked secret, a security or fraud finding, an economy or progression exploit, or a hard block on the feature's primary path. |
| **High** | The feature's stated behaviour is wrong on a normal path, a stated budget is breached, or a regression appears in previously working behaviour. |
| **Medium** | Wrong behaviour on an edge case, a recoverable error, or a budget breach only under conditions the spec does not require. |
| **Low** | Cosmetic, or a deviation with no behavioural consequence. |

- One severity per finding. Never average several findings into one entry — split them.
- Never raise severity to force attention, and never lower it because a fix looks expensive; the receiving agent decides cost, you state impact.

## Classification before routing

A finding is one of three things, and the distinction decides where it goes:

- **Defect** — the code does not do what its spec says. Routes to the owning implementing agent.
- **Design flaw** — the code does exactly what it was told to do, and what it was told is wrong. Routes to `gd`, immediately. **Never downgrade a design flaw into a defect to keep it inside the routine cycle** — that is the one finding the GD must see without waiting for the next report.
- **As designed** — the behaviour is correct and the expectation was wrong. Report it as such; do not quietly drop it, because the same expectation will be raised again by someone else.

## Bug identity and lifecycle

Every defect a QA agent or the GD reports becomes a tracked bug. Its full record lives in the feature's
`BUGS.md` (or, with no feature, in `<state-root>/bug-log.md`), and its ID — `BUG-0001`, project-wide — is
allocated only in `bug-log.md`. **The orchestrator is the only writer of both files**; an agent never edits
them and never invents an ID. An agent proposes in its own return; the orchestrator records.

| Status | Set when | Who may cause it |
|---|---|---|
| **Open** | A new defect is reported | A QA agent's finding, or the GD |
| **Fixed** | The owner states the fix is in, naming the bug ID — recorded once review clears the fix, or at once where the GD declined review | The implementing agent — never a QA agent, never the orchestrator on its own |
| **Closed** | A QA verification run shows the defect gone, with evidence | **Only a QA verification return** — never the author of the fix |
| **Reopened** | A QA verification run shows it still there, or it comes back later | A QA verification return, or a new finding matching a closed bug |
| **Won't fix** | The GD accepts it as a known limitation | **Only the GD**; mirrored into `DEBT.md` before closure |
| **Accepted unverified** | The GD accepts a `Fixed` bug at CP4 that no QA run verified | **Only the GD**; recorded as an accepted gap, never reported as verified |
| **Escalated** | It is a design flaw, not a defect | Any agent — it goes to the GD immediately. The GD's answer moves it to `Open`, `Won't fix`, or `As designed` once it becomes a change request |
| **Duplicate of BUG-####** | It turns out to be a bug already recorded | The orchestrator, moving its evidence to the original |
| **As designed** | The behaviour is correct and the expectation was wrong | The reporting QA agent, stated as such; or the GD's ruling on an `Escalated` bug |

What this means for a QA agent:

- **Before reporting, check the feature's `BUGS.md`.** A finding that matches an open bug is evidence on that
  bug, named by its ID — not a new one. A finding that matches a **closed** bug is a regression: report it with
  that ID, so it reopens rather than being filed fresh.
- **Every finding carries its severity**, from the table above, so it can be opened without a follow-up.
- **A GD-reported bug** is opened from the GD's own words. The orchestrator sets its owner from the agents' scopes and its severity from the table above, so the fix can be dispatched; the GD may correct either. Any element they did not give is marked not yet established, and the QA agent that first verifies it completes the record.
- **When dispatched to verify bugs by ID**, return a verdict per ID — passes (close) or still fails (reopen) —
  with the evidence for each. A bug you could not exercise is stated as unverified, never as passing.

## Reproduction

- State the steps that produce the finding, from a known starting state, in the order you performed them.
- State how many attempts you made and how many reproduced it. An intermittent finding is reported as intermittent with its rate — never as reliable, and never silently discarded because it did not reproduce on the second try.
- If it did not reproduce at all after the first sighting, report it with that fact stated. An unreproducible finding is still information.

## What never goes in a defect report

- A proposed fix written as code. Name the concrete change if it is obvious; the owning agent writes it.
- A finding outside the scope you were dispatched for — note it and route it separately, per each agent's Handoff and "stay scoped" rules.
- A second agent's verdict restated as your own. Cite it and attribute it.

## Rules

- Every finding carries location, expected, actual, evidence, and an owning `agent-id`.
- Severity states impact if shipped, chosen from the first matching row, one per finding.
- A design flaw goes to `gd` immediately and is never reclassified downward to stay in the routine cycle.
- An intermittent finding is reported with its reproduction rate, never as reliable and never dropped.
- No finding is reported without the evidence that proves it.
- A finding matching a known bug cites its ID; only a QA verification closes or reopens a bug, and only the GD
  marks one Won't fix.