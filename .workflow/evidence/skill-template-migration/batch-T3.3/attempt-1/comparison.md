# Comparison: batch T3.3, attempt 1

- **Base:** `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`.
- **Verdict:** fail. Failing skills: `shared-core-boundary-audit`, `core-tests-without-unity`, `dotnet-concurrency-and-async`.
- **Other 13 skills:** every Base criterion kept or moved as listed below. Kept lines are not listed.
- **Safety-critical skills:** `core-determinism` and `save-data-versioning-migration` pass; no condition, order or consequence was lost.

## Findings

Line numbers: Base at the Base sha, current in the working tree. Every `SKILL.md` fix keeps step numbers, stays under 200 chars and matches the titled-item shape.

| Skill | Check | Base text | Current text | Why it fails | Exact fix |
|---|---|---|---|---|---|
| `shared-core-boundary-audit` | 1, 2 (step 3: shared scope, shifted qualifier) | `:10` "`UnityEngine.Random` ... `new System.Random()` without a seed. Each must arrive via an injected seed or clock. Also: `Dictionary`/`HashSet` iteration order ...; `string.GetHashCode()` ...; `float`/`double` results ... → question for `technical-architect`" | `SKILL.md:22` "...cannot catch:** each hit must arrive via an injected seed or clock." with all six kinds nested under it at `:23`-`:28` | "Each" covered only the ambient APIs; "Also:" opened a separate group. On the title it now covers collection order, hash codes and float agreement, none of which can arrive through a seed or clock, and it competes with the float bullet's own route to `technical-architect`. | Replace `:22`: `3. **Grep Core for non-determinism the compiler cannot catch:** the sources below.` Then insert after `:25` (the `Identity` bullet): `   - **Random, Time and Identity hits:** each must arrive via an injected seed or clock.` |
| `core-tests-without-unity` | 6 (reference link) | Fences at `dotnet-test-mirror.md:26` and `:48`, first line naming the `.csproj` path | `references/dotnet-test-mirror.md:26` and `:28` "Sample: [...xml](...), saved as `.csproj` (...)" | "saved as `.csproj`" states the opposite of what is on disk: the file is saved as `.xml`. It names no target path and no reason for the extension, so the reference does not say how to adapt it. | Replace `:26`: ``Sample: [Combat.Core.Mirror.xml](../scripts/Combat.Core.Mirror.xml) (library over one engine-free asmdef, linked sources). Adapt it into `TestsDotnet/<Feature>/Core/<Feature>.Core.Mirror.csproj`; it is stored as `.xml` only because `*.csproj` is gitignored here.`` Replace `:28`: ``Sample: [Combat.Tests.Mirror.xml](../scripts/Combat.Tests.Mirror.xml) (test project over `Tests/EditMode/`). Adapt it into `TestsDotnet/<Feature>/Tests/<Feature>.Tests.Mirror.csproj`; it is stored as `.xml` only because `*.csproj` is gitignored here.`` |
| `core-tests-without-unity` | 2, 6 (orphan reference; fact the code alone carried) | Fence `:48`-`:69` held `$(TestSdkVersion)`, `$(NUnitVersion)`, `$(NUnitAdapterVersion)` and "Exact versions, recorded in docs/tech-stack.md; NUnit stays on 3.x", directly above "The three version properties live in ..." | `references/dotnet-test-mirror.md:30` "The three version properties live in `TestsDotnet/Directory.Build.props` ..." | With the fence gone, "the three version properties" points at nothing in the reference. "Recorded in `docs/tech-stack.md`" is now only in the script. | Replace `:30`: ``The three version properties (`TestSdkVersion`, `NUnitVersion`, `NUnitAdapterVersion`) live in `TestsDotnet/Directory.Build.props`, so nothing outside `TestsDotnet/` is affected. Exact versions are recorded in `docs/tech-stack.md`; NUnit stays on 3.x.`` |
| `core-tests-without-unity` | 6 (`## Scripts` entry usable without the reference) | Same fence; the properties were explained beside it | `SKILL.md:27` "**Contents:** pinned `LangVersion` and NUnit 3.x packages." | The brief lists a file under `## Scripts` only when usable without the reference. This sample needs those three properties defined elsewhere, and the bullet does not say so. | Replace `:27`: ``  - **Contents:** pinned `LangVersion` and NUnit 3.x packages; version properties per [dotnet-test-mirror.md](references/dotnet-test-mirror.md).`` |
| `dotnet-concurrency-and-async` | 6, 8 (adapt target: invented claim, not a path) | Fence at `task-types-and-combinators.md:20` names no location. `:14` "`<Feature>/Server` code and IO/service wrappers outside the PlayerLoop use the BCL; Unity-side SDK wrappers and PlayerLoop work go to `unitask-async-programming`." | `scripts/BridgeCallbackAsync.cs:2` "Adapt into: a Client or service wrapper class, as a private static method"; `SKILL.md:23` "adapt into the SDK wrapper class as a private static method" | Not precise enough. "Client" is added and contradicts step 1, which sends Unity-side wrappers to UniTask, and step 8, where Client code crosses by interop. The two texts also disagree. A method has no file of its own, so the target names the host. | Replace `BridgeCallbackAsync.cs:2`: `// Adapt into: <Feature>/Server/<SdkWrapper>.cs or an IO/service wrapper outside the PlayerLoop, as a private static method.` Replace `SKILL.md:23`: ``- **[BridgeCallbackAsync.cs](scripts/BridgeCallbackAsync.cs):** adapt into `<Feature>/Server/<SdkWrapper>.cs` or an IO/service wrapper outside the PlayerLoop → a callback API awaited as a `Task`.`` Then insert after it: ``  - **Form:** a private static method of that class, bridged through `TaskCompletionSource`.`` |

## Cuts

| Skill | Base text | Class |
|---|---|---|
| 14 skills: `core-determinism` `:43`, `core-scene-integration` `:45`, `core-tests-without-unity` `:40`, `csvhelper-csv-data` `:50`, `dotnet-concurrency-and-async` `:45`, `dotnet-memory-and-collections` `:40`, `memorypack-serialization` `:43`, `roslyn-analyzer-codefix` `:39`, `save-data-versioning-migration` `:49`, `shared-core-boundary-audit` `:40`, `source-generator-authoring` `:46`, `stateless-state-machines` `:42`, `zlinq-zero-allocation-linq` `:41`, `zstring-zero-allocation-strings` `:39` | "On request only, add ... `Latent concerns` and `Future remediation`, each with its trigger." | Batch brief "Remove or move". All 14 use the plain "each with its trigger", so no named trigger was lost |
| `core-determinism` | `:40` `Verified: <runners that ran ...>`, `:41` `Known limitations: <e.g. no Player run on <platform>>` | Envelope field; the limit stays at step 6 (`:56`, `:57`) |
| `core-scene-integration` | `:42` `Verified: <frame-rate test or playtest ...>`, `:43` `Known limitations` | Envelope field; the limit stays at step 9 (`:62`, `:63`) |
| `core-tests-without-unity` | `:38` `Known limitations: <e.g. no Player run>` | Envelope field; the limit stays at `## Never` (`:59`, `:60`) |
| `save-data-versioning-migration` | `:46` `Verified: <Edit Mode run, device interrupted-write run ...>`, `:47` `Known limitations` | Envelope field; the Edit Mode result stays at Output `Fixtures` (`:89`), the device run at step 7 (`:57`) |
| `csvhelper-csv-data`, `dotnet-concurrency-and-async`, `dotnet-memory-and-collections`, `memorypack-serialization`, `nrandom-random-generation`, `roslyn-analyzer-codefix`, `source-generator-authoring`, `stateless-state-machines`, `zlinq-zero-allocation-linq`, `zstring-zero-allocation-strings` | `Known limitations: <...>` in `## Output` | Envelope field; no domain content |

- **Common knowledge cuts:** none in this batch.
- **`Never` bullets deleted:** none; every Base bullet is kept.

## Moves

| Skill | Base | Now |
|---|---|---|
| `shared-core-boundary-audit` | `:4` "This skill reports and routes; it never rewrites code." | `SKILL.md:42`, `## Never` |
| `roslyn-analyzer-codefix` | `:5` "The project rule files are the specification ..." | `SKILL.md:13`, `Rules:` top line |
| `zlinq-zero-allocation-linq` | `:7` "Usable in a Core assembly ..." | `SKILL.md:13`, `Layer:` top line |
| `zstring-zero-allocation-strings` | `:7` "Usable in Core ...; `TextMeshProExtensions` is Client code only." | `SKILL.md:13`, `Layer:` top line |
| `core-scene-integration` | `:10` VContainer docs URL | `SKILL.md:21`, second `Docs:` bullet |

## Moved code

Bodies compared with `git show <Base>:<reference>` under `core.autocrlf=false`, bytes against the file after its header. All 10 fences listed in `batches.md` are moved, none trimmed, each byte-identical including the final newline.

| Base reference | File | Header lines | Reference link | Result |
|---|---|---|---|---|
| `core-determinism/references/float-and-fixed-point.md:28` | `DistanceUnits.cs` | 3 | `:28` | pass |
| `core-determinism/references/replay-test.md:35` | `MatchReplayTests.cs` | 3 | `:35` | pass |
| `core-determinism/references/stable-hashing-and-ordering.md:22` | `StableHash.cs` | 3 | `:22` | pass |
| `core-scene-integration/references/input-and-physics-into-core.md:17` | `CommandSampler.cs` | 3 | `:17` | pass |
| `core-scene-integration/references/tick-and-interpolation.md:27` | `MatchTickDriver.cs` | 3 | `:27` | pass |
| `core-tests-without-unity/references/dotnet-test-mirror.md:26` | `Combat.Core.Mirror.xml` | 3 | `:26` | body and header pass; link is a finding |
| `core-tests-without-unity/references/dotnet-test-mirror.md:48` | `Combat.Tests.Mirror.xml` | 3 | `:28` | body and header pass; link is a finding |
| `dotnet-concurrency-and-async/references/task-types-and-combinators.md:20` | `BridgeCallbackAsync.cs` | 3 | `:20` | body passes; adapt target is a finding |
| `nrandom-random-generation/references/rng-algorithms-and-determinism.md:39` | `LootRoller.cs` | 3 | `:39` | pass |
| `save-data-versioning-migration/references/version-envelope-and-chain.md:43` | `SaveMigration.cs` | 3 | `:43` | pass |

- **`.xml` tracking:** `git check-ignore --no-index` matches neither file (exit 1); `git add -n` would add both. `.gitignore:47` `*.csproj` does not touch them.
- **`.xml` headers:** each `Adapt into:` names the `.csproj` target, which is enough.
- **Scope of edits:** the 9 reference diffs hold only the fence-to-link swap.
- **Link targets:** all 10 `../scripts/` links resolve.

## Tokens

`token-survival.ps1` from the PowerShell tool: "TOTAL 16 skill(s), 1232 tokens, 42 missing", matching the author's report: 29 deleted by rule, 11 description compounds, 2 bold splits.

| Miss | Result |
|---|---|
| 28 `Latent concerns`, `Future remediation` in 14 skills | Confirmed; see Cuts |
| `Known limitations` in `shared-core-boundary-audit` | Confirmed; same line |
| `MathF/Math`, `IL2CPP/Mono`, `Dictionary/HashSet` | Confirmed; `float-and-fixed-point.md:9`, Docs `SKILL.md:18`, `SKILL.md:24` |
| `GetRecords/WriteRecords` | Confirmed; `SKILL.md` step 3 |
| `async/await` | No loss, but the citation is refuted: step 6 holds no `await`. It is at step 4 (`SKILL.md:32`) and step 5 (`:33`); `.Wait()` is at `:42` |
| `Parallel.ForEach` | Confirmed; step 6 and Docs |
| `Core/UnityEngine`, `UnityEngine/asmdef` | Confirmed |
| `equality/hashing` | Confirmed: "hashing" is gone from the whole skill since T2. It is a use-case word in a frozen description, not a criterion or symbol; not a T3.3 finding |
| `entry/exit`, `TextMeshPro` | Confirmed |
| `nrandom-random-generation` step 6 bold | Confirmed: all three parts at `SKILL.md:36`-`:38`; "for both" keeps the shared scope |
| `stateless-state-machines` step 1 bold | Confirmed: three conditions word for word at `SKILL.md:18`-`:20`; "any of" equals Base's "or" |

## Anchors

Every `anchors.md` row for these skills resolves to the same subject; the 7 skills keeping numbers keep each number.

| Skill | Cited steps | Current subject |
|---|---|---|
| `core-determinism` | 2 | Route float vs fixed-point; never decide it |
| `core-scene-integration` | 8 | Interpolate for rendering only |
| `core-tests-without-unity` | 3, 4, 7 | Mirror-ready tests; mirror only when adopted; run both runners and compare (`feature/SKILL.md:57`, `dotnet-test-mirror.md:52`) |
| `memorypack-serialization` | 9, 11 | Validate at the owning call site; changing a shipped type |
| `save-data-versioning-migration` | 1, 3, 8, 10 | Shipped decision; successor type; cloud sync; `Save migration:` |
| `shared-core-boundary-audit` | 7 | Open every hit and cite `path:line` |
| `zlinq-zero-allocation-linq` | 4, 5 | Capturing lambdas; no `.ToArray()`/`.ToList()` |

## Ask

`ask-check.ps1`: 65 hits, 38 allowlisted, 4 resolved, 23 open, none in these 16 skills.

- **`core-scene-integration` step 7:** "or asks the owner" still matches its allowlist row.
- **`zstring-zero-allocation-strings` step 1:** `Blocked` naming the capture needed, as the inventory says.

## Sections and scope

- **Sections:** `feature-docs` stays method class with `Read` and `Write`; the other 15 use `Steps`.
- **Frontmatter:** first five lines equal `HEAD` in all 16 skills.
- **Files:** 25 modified and 6 new `scripts/` folders, only this batch's paths.
- **Verify:** `verify.ps1 -File` prints 0 warnings for all 16; whole layer `verify-layer: OK (21 warning(s))`, exit 0.
