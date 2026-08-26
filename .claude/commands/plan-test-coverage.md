---
description: Derive a full test case list (normal + edge cases), a manual test flow, and a cross-feature impact analysis from docs/spec, the request itself, or the code — reports only, never writes or runs tests
argument-hint: "[file-or-directory-path...] [--spec path-to-doc]"
allowed-tools: Read, Grep, Glob, Bash, Skill
---

# Plan test coverage for a feature or change

Arguments: `$ARGUMENTS` — file/directory paths to the code under test, optionally with
`--spec <path>` pointing at a Tech Spec/GDD/design doc to read alongside the code. Any of the three
sources (docs, the request text itself, the code) may be the only one available — see Step 1. Never
guess the scope silently if none is resolvable — ask the user.

This command is a **static test-design pass**, not a substitute for the QA gates already owned
elsewhere in this project:
- Deciding official QA scope, exit criteria, and sign-off → `qa-lead`'s job. This command's case
  list can feed that plan; it is not the plan itself and issues no sign-off verdict.
- Writing and running actual Edit Mode / Play Mode tests → `qa-automation-engineer`. This command
  never writes test code and never opens the Unity Editor.
- Playing a scenario by hand and judging feel against the GDD → `playtest-tester`. This command
  documents *what* to test and *how*, it does not perform the play session.
- Tech-Spec correctness / Shared-Core duplication → `code-reviewer`. Runtime performance, memory,
  and hidden crash/ANR risk → `/review-code-risks`. Neither is this command's lens; this one is
  about test coverage and blast radius, not code quality.

Work internally in English (reasoning, code/doc excerpts, identifiers), per
`.claude/rules/language-and-comments.md` — the **final report handed back to the user must be
written in Vietnamese**, detailed but direct, no filler.

## Step 1 — Gather the source of truth

Resolve, in this order, and state which were actually available — never invent a source that wasn't
given:
1. **Docs/spec** — `--spec <path>` if given, or a Tech Spec/GDD/design note the user's request
   points at. Read it in full.
2. **The request itself** — if the user described the intended behavior directly in the prompt
   (no doc, Simple-tier change), treat that description as the spec.
3. **The code** — if `$ARGUMENTS` gives paths, read them; otherwise derive scope from
   `git diff --name-only HEAD -- '*.cs'` + `git diff --staged --name-only -- '*.cs'`. The code is
   always read even when a doc exists — a doc states intent, the code states what actually runs,
   and a mismatch between the two is itself a finding (see Step 2).
- If none of the three resolves to anything concrete, stop and ask the user what to plan tests for.

## Step 2 — Derive the test case list

Invoke the `risk-based-test-planning` skill directly with the testable claims extracted from Step 1
(from the doc/request where available, cross-checked against what the code as written actually
does). This skill already owns exactly what "list every test case, normal and edge" requires:
equivalence partitions, boundary values on both sides of every range, a decision table when an
outcome depends on more than one condition, and state-transition coverage for anything with a
lifecycle. Do not re-derive this reasoning by hand — the skill produces it directly.

- If the code implements behavior the doc/request never mentioned, or vice versa, record that gap
  explicitly as its own finding before deriving cases from it — an unstated behavior needs a case
  too, and a documented behavior the code doesn't have is a defect, not a test-planning problem
  (name it, route it to the owning agent per `defect-reporting.md`, don't silently test around it).
- Carry the skill's severity/impact ranking into the final report's ordering — most-impactful case
  first, per `.claude/rules/qa/defect-reporting.md`'s Severity table.

## Step 3 — Write the test flow (how to actually run each case)

For every case the skill produced, turn it into steps someone can follow without guessing:
- **Starting state** — what must be true before the case begins (scene, save state, config value).
- **Actions** — the exact steps, in order.
- **Expected result** — the observable outcome, stated so pass/fail is unambiguous.
- **Where to observe it** — Editor Play Mode, an automated assertion, a build/device, or a log line;
  name it, don't leave it implied.
- **Recommended coverage owner** — `qa-automation-engineer` for deterministic Shared Core logic,
  `playtest-tester` for feel/GDD scenarios, `performance-qa-engineer` for anything needing a
  measured budget, `build-verification-tester` for real-artifact-only behavior. This is a
  recommendation for the reader to act on, not a dispatch — this command does not assign or hand
  off work itself.

## Step 4 — Cross-feature impact analysis

Identify what else in the codebase touches the same surface, and say plainly whether that's
dangerous. This is the step most test plans skip, and it's the one the user explicitly asked for.

1. Name the public surface the change/feature actually exposes — class, method, event, Shared Core
   rule, ScriptableObject/config asset, prefab, or scene object.
2. Grep the codebase for other call sites, subscribers, or references to that surface — do not
   assume isolation. Specifically check for:
   - Other classes calling the same public method/property, or subscribing to the same event.
   - The same `Game.Core.*` rule consumed by more than one `Game.Client.*` caller (a Shared Core
     change affects every caller at once, per `.claude/rules/client/coding-principles.md`'s Shared
     Core integrity section).
   - A `static`/singleton field or service that this code reads or writes, and who else touches it.
   - A shared prefab, scene, or Addressables asset referenced from more than one feature.
3. For every dependent found, report exactly where (`path:line`), how it would be affected (what
   changes for that caller if this code's behavior changes), and whether it's dangerous — using
   `defect-reporting.md`'s Severity table for the "if this breaks" impact, not a confirmed defect.
4. If grep-based search finds nothing, say so plainly — but state it as a static-search result, not
   a proof of isolation: reflection, `Activator.CreateInstance`, event buses, or a service locator
   can create a dependency this method of search cannot see. Name that limitation under
   `Not covered` rather than implying isolation was confirmed.

## Step 5 — Report

Detailed but direct — every section exists because the user needs it, but no restated rule text,
no filler sentences, no padding a thin result to look thorough. Every impact finding still carries
the elements `.claude/rules/qa/defect-reporting.md` requires, with an exact line number.

**Only include a section or field when there's something to put in it.** `Status`, `Sources used`,
and `Test cases` are always present — there's no report without them. Every other section
(`Doc/code mismatch`, `Cross-feature impact`) appears only when it actually found something; drop
it entirely rather than writing "none"/"no dependents found" as a placeholder. `Not covered` is the
one exception that stays even when empty-looking, per `.claude/rules/qa/verification-standards.md`
— but keep it to the real gaps (unavailable sources, what static search can't see), not a restated
boilerplate line.

```
## Test Coverage Plan — <scope>
- Status: Done | Blocked
- Sources used: docs (<path>) | request text | code (<paths>) — state which were actually available
- Doc/code mismatch: <behavior in one but not the other, with path:line>   [omit if none found]

### Test cases
- [N] <Normal | Edge> — <short name>
  - Starting state: <...>
  - Actions: <...>
  - Expected: <...>
  - Observe via: <Editor Play Mode | automated assertion | build/device | log>
  - Recommended owner: <agent-id>
  - Impact if this breaks: Critical | High | Medium | Low

### Cross-feature impact                                    [omit section if no dependents found]
- Surface: <class/method/event/rule/asset changed or under test>
- Affected: <path:line — the dependent call site, subscriber, or reference>
- How: <what changes for that caller if this behavior changes>
- Dangerous: yes/no, and why — cite the Severity row this maps to
(repeat per dependent found)

- Not covered: <sources unavailable, dependency paths static search can't see (reflection/event bus/
  service locator), and anything needing a runtime measurement or device to confirm>
```

Order test cases and impact findings most-impactful first. If Step 1 found nothing to plan against,
say so in `Status: Blocked` rather than fabricating cases from assumptions.

Then translate this into the final Vietnamese message to the user: detailed, accurate, straight to
the point, keeping code/doc excerpts, identifiers, file paths, and line numbers verbatim.

## Guardrails

- Never write test code — the case list and flow are handed to `qa-automation-engineer` /
  `playtest-tester` to execute; this command produces neither an automated test nor a manual play
  session.
- Never open the Unity Editor or run anything — this is a static read of docs/request/code only.
- Never issue a QA sign-off, exit-criteria verdict, or official coverage assignment — that is
  `qa-lead`'s job; this command's output is an input to that plan, not a replacement for it.
- Never claim the cross-feature impact search is exhaustive — a grep-based sweep cannot see
  reflection, dynamic dispatch, or a service locator; state that limit under `Not covered` instead
  of implying isolation was proven.
- Never invent a test case or a dependent that isn't grounded in an actual doc clause, request
  sentence, or line of code — cite the source for every case and every impact finding.
- Always state which of the three sources (docs/request/code) were actually available; a plan built
  from code alone with no spec is weaker evidence than one cross-checked against a doc, and the
  reader needs to know which they got.
