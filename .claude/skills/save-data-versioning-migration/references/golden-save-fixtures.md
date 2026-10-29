# Golden Save Fixtures

Synthesized from `release` step 8 (owner `qa-automation-engineer`: "Previous release's save loads in this build's code"), `new-project` step 4 (test assembly layout), `core-tests-without-unity` step 3 (fixtures as C# data, no Unity APIs in Core tests), `memorypack-serialization` step 11 and rule `core.md` Security. Test mechanics: `unity-test-framework`.

## What a fixture is

| Subject | Fact that decides |
|---|---|
| One generated C# constant per shipped schema version | `SaveFixtureV<N>.Bytes` (`static readonly byte[]`) in `Assets/Game.Core/Tests/SaveFixtures/SaveFixtureV<N>.cs`, namespace `Game.Core.Tests.SaveFixtures`: the full envelope + payload exactly as the shipped build writes it. No data files: the test reads no disk and runs unchanged in a dotnet mirror |
| Written by version N code | Generate it while `CurrentSchemaVersion == N` — at the release that ships N, at the latest in the commit before `SaveV{N+1}` lands. Missed one for an already-shipped version → check out that release tag and run the writer there; never hand-build bytes with newer code |
| Frozen once committed | A hand-written pin table in the test file (`version → SHA-256 hex`) holds each fixture's hash. It lives outside the generated file, so regenerating bytes without editing the pin fails the run on purpose |
| Writer | An `[Explicit]` NUnit test in `Game.Core.Tests` that serializes one canonical `SaveV{N}` instance through the production envelope writer (not a copy of it) and prints the generated `SaveFixtureV<N>.cs` source plus its hash to `TestContext.Out`. A writer that saves the file through `UnityEditor` lives in an Editor-only assembly outside `Game.Core.Tests` |
| Use in tests | Clone before patching (`(byte[])SaveFixtureV<N>.Bytes.Clone()`); the constant is shared across tests |
| Size | A few KB per version; a source file, so it diffs and reviews like code |

## Canonical content

| Rule | Fact that decides |
|---|---|
| Every field non-default | A field left at its default cannot show a step that drops or mis-maps it |
| Collections non-empty, with an edge entry | At least one item at a boundary value (max stack, zero, last enum member) so range checks after migration are exercised |
| Strings non-ASCII | Synthetic, e.g. `"Fixture Plåyer ñ"`: catches encoding changes |
| Identity and store data synthetic | Player id `"fixture-player-0001"`, transaction ids `"fixture-txn-0001"`; never a real account id, email, device id, advertising id, IP, purchase token or receipt (`core.md` Security: no player PII) |
| No production export | A save pulled from a player or a QA device never becomes a fixture: it carries PII and is not reproducible from code |

## Test matrix (`Game.Core.Tests`, Edit Mode)

| Test | Pass criterion |
|---|---|
| Every shipped version has a fixture | Enumerates `MinSupportedVersion..CurrentSchemaVersion` and asserts a `SaveFixtureV<N>` entry and a pin exist for each — a forgotten fixture fails, not silently skips |
| Fixture hash pinned | SHA-256 of each `Bytes` equals its pin-table entry |
| Each fixture migrates to current | Classify → `NeedsMigration` (or `Current` for the newest), chain runs, boundary validation passes, every field asserted against the expected value written when the fixture was made, plus the default each later step introduced |
| Current round-trip | Serialize → classify → deserialize the canonical current instance; equal field by field |
| Too new is refused | Cloned fixture with schema patched to `CurrentSchemaVersion + 1` (hash recomputed) → `TooNew`. The file-store check (bytes unchanged, no temp left, no backup restore) is a `Game.Client.Tests` test, since it touches disk |
| Corrupt is refused | One flipped payload byte → `Corrupt`; one flipped schema byte → `Corrupt`; truncated → `Corrupt`; none throws |
| Chain contiguity | Building the production chain does not throw |

**Caveat:** assertions for an old fixture grow with each new step (the new field's migrated value); its bytes never change.

## Release step 8 evidence

| Item | Fact that decides |
|---|---|
| Command | The project's test command from `CLAUDE.md`, Edit Mode, filtered to the save fixture tests (`-testFilter`, `unity-test-framework`) |
| Pass | Every fixture from `MinSupportedVersion` through the previous release's schema version migrates to current; result XML attached |
| Gap | The previous release shipped without a fixture → step 8 is not passed until one is generated from that release's tag; state it, never substitute a fresh-code fixture |
| Device | The fixture suite proves code paths, not the file swap on device; the interrupted-write check on a device runs only on the GD's request via `build-release-engineer` |
