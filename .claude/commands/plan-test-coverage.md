---
description: Derive a full test case list (normal + edge cases), a manual test flow, and a cross-feature impact analysis from docs/spec, the request itself, or the code — reports only, never writes or runs tests
argument-hint: "[file-or-directory-path...] [--spec path-to-doc]"
allowed-tools: Powershell, Read, Grep, Glob, Bash, Skill
---

# Plan test coverage for a feature or change

`$ARGUMENTS`: code paths, optionally `--spec <path>`. Docs/request/code may each be the only source available (below); ask if none resolves, never guess scope. Static test-design only — not `qa-lead`'s sign-off, `qa-automation-engineer`'s test code, `playtest-tester`'s play session, `code-reviewer`'s correctness pass, or `/review-code-risks`'s risk lens. Reason in English (`language-and-comments.md`); final report to the user is in Vietnamese, detailed but direct.

**1 — Gather the source of truth**, in order, stating which were actually available: (1) docs/spec — `--spec` or a doc the request points at, read in full; (2) the request itself — a direct description counts as spec for a D1–D2 change; (3) the code — `$ARGUMENTS` paths, else `git diff --name-only HEAD -- '*.cs'` (+staged), always read even with a doc since a mismatch is itself a finding. None resolves → ask the user.

**2 — Derive the test case list**: invoke `risk-based-test-planning` directly with the testable claims from Step 1 — it already covers equivalence partitions, boundary values, decision tables, state-transition coverage; don't re-derive by hand. Doc/code mismatch → record as its own finding, routed per `defect-reporting.md`, don't silently test around it. Carry the skill's severity ranking into the report, most-impactful first.

**3 — Write the test flow**, per case: starting state, actions, expected result (unambiguous pass/fail), where to observe it (Editor Play Mode / automated assertion / build/device / log), and a recommended owner (`qa-automation-engineer`, `playtest-tester`, `performance-qa-engineer`, `build-verification-tester`) — a recommendation for the reader, not a dispatch this command performs.

**4 — Cross-feature impact analysis**: name the changed public surface (class/method/event/Shared Core rule/asset/prefab/scene object), grep for other callers/subscribers/references — other call sites, a `Game.Core.*` rule used by more than one `Game.Client.*` caller, a static/singleton field, a shared prefab/scene/Addressables asset. Per dependent: `path:line`, how it's affected, dangerous yes/no per `defect-reporting.md`'s Severity table. Nothing found → say so, naming the limit (reflection, `Activator.CreateInstance`, event bus, service locator can hide a dependency from grep) rather than implying isolation was proven.

**5 — Report**, only a section when it found something — no "none" placeholders except `Not covered`, always present. Most-impactful first:
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
Translate to Vietnamese for the user, excerpts and line numbers verbatim.

**Guardrails**: never write test code or open the Unity Editor; never issue a QA sign-off or coverage assignment; never claim the impact search is exhaustive, or invent a case/dependent not grounded in a real source; always state which of the three sources were actually available.
