---
name: qa-standards
description: When a QA claim counts as verified, finding format (location, expected, actual, evidence, owner, severity), severity scale, bug lifecycle and statuses.
user-invocable: false
---

# QA standards

## A claim is verified only when
| Claim | Needs |
|---|---|
| Behaviour correct | An assertion tied to a spec/GDD clause actually ran the path |
| Performance OK | A measurement **and** a budget; state platform, scenario, run spread |
| Works on platform | A real build ran. Editor results are labelled "indicative" every time |
| Repeatable | Seed/clock injected, or repeated runs with spread reported |
| No regression | Same metric, same method, before and after. No baseline → this run is the baseline; say so |

- Every report has `Not covered:` — never "none" unless exhaustive. Name the owner agent of each gap.
- Never: weaken an assertion to go green, report the best run, call an Editor run a device run, infer an unobserved result, reuse an old result, count a skipped check as passed.
- `Blocked` on a missing budget, clause or target is correct. A guessed input is not.
- Consume other gates' verdicts; never re-run their checks.

## A finding has
| Field | Content |
|---|---|
| Location | `path:line`, scene + entry point, artifact path, or scenario + metric |
| Expected | What should happen + its source (spec clause, GDD, budget, rule) |
| Actual | Observed behaviour, not a diagnosis |
| Evidence | Log excerpt, screenshot, measurement with spread, failing assertion, quoted line |
| Owner | The fixing agent; unclear → say so |
| Severity | First match: **Critical** crash/hang, data loss, secret, exploit, primary path blocked · **High** wrong on a normal path, budget breach, regression · **Medium** edge case, recoverable error · **Low** cosmetic |
| Repro | Steps from a known state; attempts and hits (intermittent → rate) |

- One severity per finding; impact if shipped, never cost to fix.
- **Defect** (code ≠ spec) → owner. **Design flaw** (spec itself wrong, including a spec assumption that contradicts an acceptance criterion — the criterion wins) → GD immediately, never downgraded. **As designed** → report it as such.
- No fix code in a finding; name the change if obvious.

## Bugs
Filing, matching, verifying or closing a bug, and every QA sign-off → read [bug-lifecycle.md](references/bug-lifecycle.md) first: writer, statuses, what counts as settled.
