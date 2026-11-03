---
name: plan-test-coverage
description: "Test case list (normal + edge), manual flow, impact analysis from a spec; report only. Use when planning tests."
argument-hint: "[file-or-directory-path...] [--spec path-to-doc]"
allowed-tools: PowerShell, Read, Grep, Glob, Bash, Skill
---

# Plan test coverage for a feature or change

- **Not for:** sign-off (`qa-lead`), test code (`qa-automation-engineer`), the play session (`playtest-tester`), correctness pass (`code-reviewer`), code risk review (`/review-code-risks`).
- **Input:** `$ARGUMENTS`: code paths, optionally `--spec <path>`.
- **Scope:** static test design only.
- **Final report:** to the GD in Vietnamese, excerpts and line numbers verbatim.

## Steps
1. **Sources:** use these in order, stating which were available:
   - **Docs or spec:** (1) docs/spec (`--spec` or a doc the request points at), read in full.
   - **Request:** (2) the request itself (counts as spec for an S-size change).
   - **Code:** (3) the code (`$ARGUMENTS` paths, else `git diff --name-only HEAD -- '*.cs'` plus staged), always read even with a doc.
   - **Code against doc:** a mismatch between the code and a doc is a finding.
   - **Coverage report:** an existing `CodeCoverage/` of this revision: uncovered lines in scope are leads for cases (`unity-test-framework` → code-coverage.md). Never run one here.
   - **No source:** none resolves → `AskUserQuestion`; never guess scope.
2. **Cases:** invoke `risk-based-test-planning` with the testable claims; do not re-derive by hand.
   - **Doc/code mismatch:** its own finding (`qa-standards` format), never silently tested around.
   - **Order:** by the severity ranking of `risk-based-test-planning`.
3. **Flow:** per case:
   - **Case fields:** starting state, actions, unambiguous expected result, where to observe (Play Mode / automated assertion / build or device / log).
   - **Owner:** recommended owner (`qa-automation-engineer`, `playtest-tester`, `performance-qa-engineer`, `build-release-engineer`).
   - **Owner limit:** the owner is a recommendation, not a dispatch.
4. **Cross-feature impact:** name the changed public surface (class, method, event, Core rule, asset, prefab, scene object).
   - **Search:** grep other callers, subscribers, references.
   - **Search targets:** other call sites, a Core rule used by several Client callers, static/singleton fields, shared prefab/scene/Addressables assets.
   - **Per dependent:** `path:line`, how affected, dangerous yes/no per the `qa-standards` severity scale.
   - **Nothing found:** say so and name the limit (reflection, `Activator.CreateInstance`, event bus, service locator hide dependencies from grep).
   - **Nothing found, isolation:** never imply isolation was proven.
5. **Report:** in the `## Output` form:
   - **Sections:** a section only when it found something.
   - **`Not covered`:** always present.
   - **Order:** most impactful first.

## Never
- **Test code or Editor:** write test code or open the Unity Editor.
- **Sign-off:** issue a QA sign-off or coverage assignment.
- **Exhaustive claim:** claim the impact search is exhaustive.
- **Invention:** invent a case or dependent without a real source.

## Output
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
