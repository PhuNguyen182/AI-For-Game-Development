---
name: plan-test-coverage
description: Derive a test case list (normal + edge), manual test flow and cross-feature impact analysis from a spec, the request, or the code — report only, never writes or runs tests
argument-hint: "[file-or-directory-path...] [--spec path-to-doc]"
allowed-tools: PowerShell, Read, Grep, Glob, Bash, Skill
---

# Plan test coverage for a feature or change

`$ARGUMENTS`: code paths, optionally `--spec <path>`. Static test design only: not `qa-lead`'s sign-off, `qa-automation-engineer`'s test code, `playtest-tester`'s session, `code-reviewer`'s correctness pass or `/review-code-risks`. Final report to the GD in Vietnamese, excerpts and line numbers verbatim.

1. **Sources**, in order, stating which were available: (1) docs/spec (`--spec` or a doc the request points at), read in full; (2) the request itself (counts as spec for an S-size change); (3) the code (`$ARGUMENTS` paths, else `git diff --name-only HEAD -- '*.cs'` plus staged), always read even with a doc: a mismatch is a finding. None resolves → ask; never guess scope.
2. **Cases** — invoke `risk-based-test-planning` with the testable claims; do not re-derive by hand. Doc/code mismatch → its own finding (`qa-standards` format), never silently tested around. Order by that skill's severity ranking.
3. **Flow** — per case: starting state, actions, unambiguous expected result, where to observe (Play Mode / automated assertion / build or device / log), recommended owner (`qa-automation-engineer`, `playtest-tester`, `performance-qa-engineer`, `build-release-engineer`). A recommendation, not a dispatch.
4. **Cross-feature impact** — name the changed public surface (class, method, event, `Game.Core.*` rule, asset, prefab, scene object); grep other callers, subscribers, references: other call sites, a Core rule used by several `Game.Client.*` callers, static/singleton fields, shared prefab/scene/Addressables assets. Per dependent: `path:line`, how affected, dangerous yes/no per the `qa-standards` severity scale. Nothing found → say so and name the limit (reflection, `Activator.CreateInstance`, event bus, service locator hide dependencies from grep); never imply isolation was proven.
5. **Report** — a section only when it found something; `Not covered` always present; most impactful first.
```
## Test Coverage Plan — <scope>
- Status: Done | Blocked  |  Sources used: docs (<path>) | request text | code (<paths>)
- Doc/code mismatch: <path:line>                          [omit if none]
### Test cases
- [N] <Normal|Edge> — starting state / actions / expected / observe via / owner / impact if broken
### Cross-feature impact                                    [omit if none]
- Surface / Affected (path:line) / How / Dangerous (yes/no + why)
- Not covered: <unavailable sources, dependency paths static search can't see, needed measurements>
```

## Never
- Write test code or open the Unity Editor.
- Issue a QA sign-off or coverage assignment.
- Claim the impact search is exhaustive, or invent a case or dependent without a real source.
