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
- Main session is the only writer of `.workflow/bugs.md` and bug records. Agents propose; never invent an ID.
- Check existing bugs first: a match is evidence on that ID; a match on a closed bug reopens it.
- A defect seen out of scope, with evidence but no repro yet → record it `Open`, repro "not yet"; never drop it.
- Status: **Open** → **Fixed** (owner names the ID in `Fixes:`) → **Closed** (only a QA run with evidence) or **Reopened**. **Won't fix** / **Accepted** — only the GD; mirrored into `DEBT.md`. **As designed**, **Duplicate of BUG-####**.
- Settled: Closed, Won't fix, Accepted, As designed, Duplicate. QA sign-off needs zero unsettled. When QA was declined, CP4 lists each `Fixed` bug for the GD to accept unverified (→ Accepted) or send to QA.
- Verifying bugs by ID → one verdict per ID with evidence; unexercised → "unverified".
