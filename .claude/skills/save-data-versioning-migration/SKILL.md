---
name: save-data-versioning-migration
description: "Save versioning: header (magic, schema version, SHA-256), frozen SaveVN DTOs, sequential vN→vN+1 migration chain, too-new refusal, temp + File.Replace atomic write, pre-migration backup, golden fixtures. Use when a save format changes or ships."
user-invocable: false
---

# Save Data Versioning and Migration

Not for: serializer attributes and version-tolerant layout (`memorypack-serialization`), cloud-save vendor choice (`backend-build-vs-buy`), save tampering and cheat posture (`anti-cheat-strategy`), purchase and currency records held server-side (`iap-server-receipt-ledger`), writing and running Unity tests (`unity-test-framework`), Core tests outside the Editor (`core-tests-without-unity`).
Docs: https://learn.microsoft.com/en-us/dotnet/api/ with `?view=netstandard-2.1` (Unity's default Api Compatibility Level) — `File.Replace`, `FileStream.Flush(bool)`, `SHA256`, `BinaryPrimitives`; `File.Move(string, string, bool)` does not exist at that level.
Rules: `csharp.md` Boundaries (Core is pure; validate save data at the boundary); `core.md` Security (no player PII in fixtures).

| Reference | Read when |
|---|---|
| [version-envelope-and-chain.md](references/version-envelope-and-chain.md) | Laying out the header, classifying a loaded file, adding a migration step, or writing the file-swap code |
| [golden-save-fixtures.md](references/golden-save-fixtures.md) | A schema version ships, a step is added, or `release` step 8 needs its evidence |

## Steps
1. **Decide whether the current format has shipped** — any build that wrote it reached a device outside the team (store, TestFlight, external testers). Not shipped: change the DTO in place, no step. Shipped: steps 3–10 apply. Unknown → `Needs-decision` to the GD; a wrong "no" corrupts live saves.
2. **Put every save behind the fixed envelope**, per [version-envelope-and-chain.md](references/version-envelope-and-chain.md): hand-written header (magic, envelope version, schema version, save counter, payload length, SHA-256 over header and payload), then the payload in the project's serializer, deserialized only into the frozen `SaveV{N}` type the header selects. Local and cloud bytes are untrusted input (`core.md` Security). Done when the header parses without knowing the payload schema.
3. **Change a shipped shape only through a successor type** — add `SaveV{N+1}`, bump `CurrentSchemaVersion`, add one step `V{N}ToV{N+1}`; `SaveV{N}` and every shipped step stay byte-for-byte (agrees with `memorypack-serialization` step 11). A defect in a shipped step gets a new repair step: players already ran the broken one, so editing it splits the population.
4. **Write each step as a pure function in `Game.Core.Save`** — `SaveV{N}` in, `SaveV{N+1}` out; no I/O, clock, `UnityEngine` or unseeded RNG; new-field defaults are named constants in the step. Done when the chain validates contiguous from `MinSupportedVersion` to `CurrentSchemaVersion` and each step passes its fixture test.
5. **Classify before deserializing**, per the load table in [version-envelope-and-chain.md](references/version-envelope-and-chain.md). Schema newer than the build → refuse: no overwrite, no save, no cloud upload this session; tell the player to update. Corrupt → restore from backup, else surface it; never fall through to a new game. Below `MinSupportedVersion` → `Needs-decision` to the GD.
6. **Migrate with the original kept** — copy the untouched bytes to the per-version backup first, migrate in memory, validate the result at the boundary (`csharp.md`), write it atomically, reload and check the hash. The migration counts as done only after that reload; the backup stays until the next clean load of the current version.
7. **Write atomically in `Game.Client.*`** — temp file in the same directory, `Flush(true)`, then `File.Replace` over an existing save or `File.Move` for the first one, per [version-envelope-and-chain.md](references/version-envelope-and-chain.md). Never write over the live file in place. No device run of the interrupted-write test yet → `Known limitations`.
8. **Sync cloud copies as the same envelope bytes, from `Game.Client.*`** — the vendor from `docs/tech-stack.md`; the classifier in `Game.Core.Save` judges cloud bytes exactly like local ones. Schema decides permission only: a client never writes over a copy whose schema is newer than its own. Recency is the save counter, compared after migrating the lower-schema copy in memory; higher wins, a tie is a conflict shown to the player. A counter cannot detect two devices diverging from the same save → `Known limitations`. A cloud save is never the authority for currency or ownership — the server is (`core.md` Security, `iap-server-receipt-ledger`). Done when the conflict rule is stated in Output.
9. **Commit one golden fixture per shipped schema version**, per [golden-save-fixtures.md](references/golden-save-fixtures.md) — written by that version's code as a generated C# `byte[]` constant with its hash pin, synthetic data only, loaded to current by an Edit Mode test in `Game.Core.Tests`. That test is the evidence for `release` step 8.
10. **Fill `Save migration:`** (backend-engineer Return extras) from the Output below.

## Never
- Rely on serializer version tolerance in place of a schema bump — it survives a layout change, not a meaning change (unit, rename, split field), and old saves decode into wrong values with no error.
- Regenerate or delete a committed fixture to turn a test green — it erases the only proof that old saves load.
- Treat the save hash as tamper protection — anyone can recompute SHA-256; it detects corruption only.
- Deserialize a save with `BinaryFormatter`, `NetDataContractSerializer`, `SoapFormatter` or Json.NET `TypeNameHandling` other than `None` — the bytes choose the type, so an edited or synced save becomes code execution.

## Output
```
## Save Versioning — <save file / module>
- Shipped before: yes (<build>) / no
- Schema: v<old> → v<new> | new format v1 | unchanged; MinSupported v<k>
- Chain: <steps added>; shipped steps untouched: yes
- Too-new / corrupt / below-min behaviour: <...>
- Write path: temp + File.Replace / first-save Move; backup <file name>
- Cloud: <vendor, conflict rule (permission by schema, recency by counter)> | n/a
- Fixtures: <SaveFixtureV<N> constants + pins> — test <name> — <result | not run>
- Verified: <Edit Mode run, device interrupted-write run — or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "v3 is out, just append `EnergyCap` to `SaveV3` — MemoryPack is version-tolerant" → declined: v3 saves would load with `EnergyCap = 0` and lock energy; added `SaveV4` and `V3ToV4` defaulting it to the v3 rule's 30, and the v3 fixture now asserts 30 after migration.
