---
name: code-review-method
description: "How code-reviewer reviews a diff: spec mapping, bug checklist, severity, verdict, re-review rounds."
user-invocable: false
---

# Code review method

## Mode
| Brief has | Mode | Covers |
|---|---|---|
| Spec or acceptance criteria | Submission | Every step below |
| No spec | Audit | Every step but spec drift; say so under `Not verified` |
| Previous findings (round 2+) | Re-review | Previous findings + lines changed since `Previous tree:`; a new finding on unchanged code blocks only at Critical/High |

## Read the diff
- **Working tree:** the working tree, not `HEAD`: `git diff --merge-base <base>` for the change, `--stat` for its spread, `git log <base>..HEAD` for intent.
- **Untracked files:** untracked files (`git ls-files --others --exclude-standard`): read in full.
- **Re-review diff:** `git diff <sha>` from the brief's `Previous tree: <sha>` (working tree vs the previously reviewed snapshot), plus untracked files.
- **Re-review without a tree:** no `Previous tree:` in the brief → re-read the lines the previous findings cite and the whole current diff.
- **Hunks:** read each hunk with enough surrounding code to know its caller and lifecycle; never judge a hunk alone.

## Order
1. **Context:** spec → `CONTRACTS.md` → diff (skill `feature-docs`, Review row).
   - **Deliberate-looking code:** `DECISIONS.md` / `DEBT.md` before flagging code that looks deliberately wrong.
2. **Spec drift:** map every acceptance criterion to the code that meets it.
   - **Drift finding:** unmet, partly met, or code doing what no criterion asks → finding.
   - **Spec flaw:** the spec itself wrong → `Needs-decision`, `Next: gd`.
3. **Contract impact:** every changed public member, event, serialized field or asset name: Grep its callers, subscribers and references, prefabs, scenes and SOs included.
   - **Contract finding:** a changed contract with an unchanged caller is a finding.
4. **Bugs:** the checklist below, per changed hunk.
5. **Boundary:** skill `shared-core-boundary-audit` when the agent's trigger fires.
6. **Runtime risk:** `.claude/skills/review-code-risks/references/risk-patterns.md`.
7. **Standards:** rule `csharp.md` and the `csharp-standards` references.
8. **Simplification:** dead code, an abstraction with one caller, a duplicate of an existing helper (Grep before claiming one exists), a hand-rolled built-in.
9. **Verification claims:** the author's `Verified:` against `qa-standards` → "A claim is verified only when".
   - **Claim finding:** a claim beyond what ran, or an acceptance criterion with neither verification nor a `Not verified` entry, is a finding.

## Bug checklist
- **Null and fake-null:** an empty Inspector slot, a `GetComponent`/`Instantiate` result, a Component held across frames, a destroyed object reached from a callback.
- **Boundaries:** off-by-one, empty and single-element collections, max values, integer overflow in currency/score/timers, float `==`, division by zero.
- **State changes:** every branch and early return leaves state whole; no event raised before the state it reports is consistent.
- **Unity lifecycle:** `Awake`/`OnEnable`/`Start` order across objects, a disabled object, scene reload, `DontDestroyOnLoad` duplicates, release in `OnDisable` vs `OnDestroy`.
- **Async and coroutines:** cancelled on disable/destroy, no continuation after the owner died, re-entrancy (a second call while the first awaits).
- **Async void and exceptions:** no `async void` outside event handlers, no unobserved exception.
- **Events:** subscribe/unsubscribe paired, no double subscription on re-enable, no reliance on handler order.
- **Collections:** no mutation during iteration; an internal list returned to a caller who can mutate it.
- **Saves and serialization:** a renamed or retyped serialized field without `[FormerlySerializedAs]`, a save field without migration.

## Unity assets in the diff
- **Prefab, scene, SO:** a required slot now `{fileID: 0}`, a missing script (`m_Script: {fileID: 0}`), an override that reverts a prefab change.
- **`.meta`:** a changed GUID, or an asset added without its `.meta` — every reference to it breaks.
- **asmdef references:** a reference that makes Core depend on Client, a feature root or a `UnityEngine` module; a reference cycle.
- **asmdef settings:** a Core-layer asmdef without `noEngineReferences`; `name` or `rootNamespace` not equal to its folder path.
- **Layout (new features, `csharp-standards` → naming-convention.md → Folders):**
  - **Placement:** code outside `<Feature>/`'s folders.
  - **Folder names:** a `.` in a folder name.
  - **Namespaces:** a namespace not equal to asmdef `rootNamespace` + relative path.
- **Names:** per `csharp-standards` → Asset names.

## Test code
- **Assertions:** asserts the spec clause, not the implementation; one behaviour per test, named for it.
- **Bans:** no weakened assertion, `[Ignore]`, `Assert.Pass`, try/catch that hides a failure, or real-time sleep; seed and clock injected.
- **Test-code severity:** only a finding that weakens what a test proves is above Low.

## Severity and verdict
- **Severity source:** per `qa-standards` → "A finding has": impact if shipped.
- **Style violations:** a style, layout, naming or comment violation (`code-style-and-layout.md`, `naming-convention.md`, rule `csharp.md` Style and Comments) is **Low**.
- **Runtime violations:** a standards violation with runtime impact (leak, hot-path allocation, Core leak, non-determinism) takes that impact's severity.
- **`Request changes`:** any Critical, High or Medium finding.
- **Re-review verdict:** a Medium/Low on unchanged code is listed for `DEBT.md`, verdict unaffected.
- **`Approve`:** no finding, or Low only.
- **Low findings:** Low findings are listed; the author fixes them without another review round.
- **`Needs-decision`:** a placement question (`shared-core-boundary-audit` "needs placement decision", `Next: technical-architect`) or a spec flaw (`Next: gd`); list any findings alongside.
- **Doubts:** a doubt the files cannot settle is not a finding: drop it, or state it under `Assumptions`.
