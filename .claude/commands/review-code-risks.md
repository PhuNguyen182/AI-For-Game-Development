---
description: Static review of C#/Unity code for runtime performance, memory efficiency, and hidden crash/ANR risk — concise report, fix direction only, never edits code
argument-hint: "[file-or-directory-path...]"
allowed-tools: Read, Grep, Glob, Bash, Skill
---

# Review code for performance, memory, and hidden crash/ANR risk

Arguments: `$ARGUMENTS` — optional list of file/directory paths. If omitted, scope from the current
git diff (see Step 1). Never guess the scope silently if both are empty — ask the user.

This command is a **static-analysis risk sweep**, not a substitute for the gates already owned
elsewhere in this project:
- Full Tech-Spec correctness, Shared-Core duplication, bug hunting → `code-reviewer`'s job. This
  command does not re-run that gate; it is narrower and additive.
- A measured, confirmed performance verdict against a budget → `performance-qa-engineer` /
  `tech-lead-performance`. Nothing here is a profiler run, so nothing here may be reported as a
  confirmed regression.
- A confirmed crash/ANR from a real device or production telemetry → `/investigate-device-crash` or
  `crash-anr-investigator`. This command flags *potential* causes visible in source, never a
  confirmed fault.
- A build-only fault already reproduced against a real artifact → `build-verification-tester` /
  `build-fault-triage`. If a finding here looks stripping/AOT/native-library-shaped, name it as a
  risk to verify that way — do not claim it as confirmed.

Work internally in English (reasoning, code excerpts, identifiers), per
`.claude/rules/language-and-comments.md` — the **final report handed back to the user must be
written in Vietnamese**, concise and accurate, with quoted code kept verbatim.

## Step 1 — Determine scope

- If `$ARGUMENTS` gives paths, review exactly those files/directories, restricted to `.cs` files.
- Otherwise, run:
  ```
  git diff --name-only HEAD -- '*.cs'
  git diff --staged --name-only -- '*.cs'
  ```
  and review the union of changed C# files.
- If both are empty, stop and ask the user what to review — do not silently fall back to scanning
  the whole repository.

## Step 2 — Scan against three criteria

Ground every check in this project's own rules rather than generic advice — cite the clause when
reporting. Read each file in scope and grep for the following signal patterns; a match is a
candidate finding, not an automatic one — confirm it actually sits in a hot path / crosses a real
boundary before reporting it.

**Runtime performance** — `.claude/rules/client/performance-and-algorithms.md`
- `new`, string interpolation/concatenation, or LINQ (`.Where(`, `.Select(`, `.OrderBy(`, etc.)
  inside `Update`/`FixedUpdate`/`LateUpdate`.
- `GetComponent<` / `GetComponent(` called inside a per-frame method instead of cached in
  `Awake`/`Start`.
- `GameObject.Find`, `FindObjectOfType`, `FindObjectsOfType` anywhere at runtime.
- `Instantiate(`/`Destroy(` in a per-frame or high-frequency path with no pool nearby.
- `Vector3.Distance`/`Mathf.Sqrt` used for a pure range/threshold comparison instead of
  `sqrMagnitude`.
- `SendMessage`, `BroadcastMessage`, or string-literal `Invoke(` calls.
- `new WaitForSeconds(` (or `WaitForSecondsRealtime`) written inside a coroutine loop instead of
  cached once.
- Repeated `transform.` property reads/writes in the same method instead of a local cache.
- String-overload `Animator.SetFloat/SetBool/SetTrigger("...")` instead of a cached
  `Animator.StringToHash`.
- `foreach` over an `IEnumerable<T>`/`IList<T>`-typed reference or a LINQ-produced sequence in a hot
  path (boxes the enumerator).
- An empty `Update()`/`FixedUpdate()`/`LateUpdate()`/`OnGUI()`/collision-callback body left on a
  MonoBehaviour.
- Nested loops over a collection whose size scales with entity/player/inventory count, with no
  spatial partitioning, indexing, or explicit bound.

**Memory efficiency** — `.claude/rules/client/performance-and-algorithms.md` (Memory discipline)
- `+=` event subscription with no matching `-=` findable in `OnDisable`/`OnDestroy` for the same
  handler.
- `StartCoroutine(` with no visible `StopCoroutine`/stop condition, or one not cleared on
  `OnDisable`/`OnDestroy`.
- A `static` field, or a field on a singleton/service, holding a reference to a MonoBehaviour,
  scene object, or large collection.
- A collection (`List<T>`, `Dictionary<...>`, etc.) that only ever grows (`.Add(`) with no visible
  cap, pool, or clear point tied to a lifecycle boundary.
- A lambda/delegate stored on a long-lived object (event field, static, singleton) that captures
  `this` or a large collection by closure.
- High-frequency `Instantiate`/`Destroy` of the same prefab type with no `ObjectPool<T>`/pooling
  pattern nearby.

**Hidden crash/ANR risk** — `.claude/rules/client/coding-principles.md` (Null safety, Exception
handling) plus the fault-domain reasoning below
- A `[SerializeField]`/public Inspector field dereferenced without a prior null/bool guard.
- The result of `GetComponent<T>()`, `Instantiate(...)`, or another reference-returning Unity API
  used without a guard before the first dereference.
- A `UnityEngine.Object`-derived reference held across frames and dereferenced without a
  `if (this.x)` / `if (!this.x)` guard — a destroyed native object reads as "fake null" here.
- `catch (Exception ...)` or `catch { }` that swallows the error instead of catching a specific
  type with a reason to act on it — especially around signature/token verification or a payment
  callback, where a swallowed failure can fail open.
- Synchronous disk or network I/O, or a large synchronous asset/scene load, reachable from the main
  thread — read `.claude/skills/live-ops/crash-anr-fault-domain-triage/references/anr-classes-and-mitigation.md`
  directly (do not invoke the skill itself — it is gated to confirmed production telemetry and
  would decline a static source read) for the causes table; cite the matching row when a signal
  matches.
- A lock or blocking wait held across a long operation reachable from the main thread — same
  reference file, "A lock held across a long operation" row.
- Reflection, `Activator.CreateInstance`, or a generic virtual method call on a type that looks
  reachable only through serialization/reflection — this is a stripping-risk signal, not a
  confirmed fault; name it and point to `build-fault-triage` for confirmation against a real build
  if one exists.

## Step 3 — Classify what actually matters

- Drop a signal match that isn't actually in a hot path, isn't actually a real boundary crossing,
  or is already guarded a few lines away — a raw grep hit is not a finding by itself.
- For a surviving finding, name the fault domain / cause class using the reference table read in
  Step 2 (e.g. "sustained frame cost", "synchronous load on main thread", "unguarded Inspector
  reference") rather than a generic "could crash".
- If a finding's severity genuinely depends on a runtime number (allocation size, frame cost,
  reproduction rate), say so explicitly and route it to `performance-qa-engineer` /
  `/investigate-device-crash` for confirmation — do not assign it a severity that implies it was
  measured.

## Step 4 — Report

Optimize for a reader who scans in ten seconds: one line per field, no restating the rule text at
length, no filler sentences ("this could potentially maybe cause..."). Every finding still carries
the five elements `.claude/rules/qa/defect-reporting.md` requires, one Severity from its table
(impact *if* the risk materializes, since nothing here is a confirmed shipped defect), and a fix
direction that names the concrete change without writing it:

```
## Code Risk Review — <scope>
- Status: Done | Blocked
- Files reviewed: <count and paths, or the git diff range used>
### Findings
- Category: Performance | Memory | Crash/ANR risk
- Location: <path:line> — the exact line number from Read/Grep output, never "somewhere in this method". If the issue genuinely spans multiple lines, give the start-end range.
- Expected: <the rule clause, named in one short phrase, not quoted at length>
- Actual: <what the code does, one line>
- Evidence: <the quoted line(s) at that exact line number>
- Severity: Critical | High | Medium | Low — impact if this risk materializes at runtime
- Fix direction: <one line naming the concrete change — never a code diff>
- Owner: <agent-id — csharp-engineer / unity-engineer / tech-lead-performance / tech-lead-csharp-unity / tech-lead-sdk-platform>
- Confidence: Static signal only — not measured, not reproduced on device
- Not covered: <files/paths skipped, and anything requiring a runtime measurement or a real device to confirm>
```

Order findings by severity, most severe first. If nothing matches after Step 3 filtering, report
that plainly in one line — a clean sweep is a valid, honest result, not a reason to invent a
finding or pad the report.

Then translate this into the final Vietnamese message to the user: short, accurate, one finding per
block exactly as above, keeping code excerpts, identifiers, file paths, and line numbers verbatim.

## Guardrails

- Never edit the code — this command reviews and reports only; the owning agent (per `Owner`)
  applies any fix.
- Never claim a confirmed performance regression or a confirmed crash/ANR from a static read — that
  requires a measurement or a real device, per `.claude/rules/qa/verification-standards.md`. Every
  finding here is a risk, stated as a risk.
- Never widen scope into full Tech-Spec correctness review, security review, or unrelated
  refactors — note them and route to `code-reviewer`/`security-reviewer` instead of reviewing them
  here.
- Never invoke `crash-anr-reporting-gate`, `crash-anr-symbolication`, or
  `crash-anr-fault-domain-triage` directly — all three are gated to confirmed production telemetry
  and will incorrectly decline a static source read. Read their reference files directly instead,
  as instructed in Step 2.
- Always state `Not covered` — a source-only pass on a subset of files is not a certification of
  the whole codebase.
