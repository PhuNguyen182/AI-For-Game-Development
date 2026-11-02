# Token survival explanations (T3.3 attempt 1)

Run: `token-survival.ps1 -Base bdf5c9ec70bf217ee9ed2763abd75fa4280b717c` with the 16 T3.3 skills. Final output: "TOTAL 16 skill(s), 1232 tokens, 42 missing". The tool printed "0 found only in scripts/" for every skill. Every miss is explained below.

## Deleted by rule (batch brief "Remove or move"): 29 misses
- 28 misses: `Latent concerns` and `Future remediation` (2 tokens each) in 14 skills: core-determinism, core-scene-integration, core-tests-without-unity, csvhelper-csv-data, dotnet-concurrency-and-async, dotnet-memory-and-collections, memorypack-serialization, roslyn-analyzer-codefix, save-data-versioning-migration, shared-core-boundary-audit, source-generator-authoring, stateless-state-machines, zlinq-zero-allocation-linq, zstring-zero-allocation-strings. The "On request only, add ..." line after `## Output` was deleted in each. No domain-specific limit was in any of them.
- 1 miss: `Known limitations` (shared-core-boundary-audit). The tool printed `backtick [SKILL.md:40]: Known limitations`. It sat in the same deleted "On request only, add `Known limitations`, `Latent concerns` and `Future remediation`" line.
- Also deleted: the `Verified:` and `Known limitations:` lines inside `## Output` fences (envelope owns them). The tool did not flag them. Domain content in them: the Player-run limit in core-determinism is already in step 6 ("cross-platform" is a known limitation, not a claim); the no-device-run limit in save-data-versioning-migration is in steps 7 and 8 (`Known limitations`).

## Description symbols (frontmatter unchanged in T3.3; lost in T2): 11 misses
The tool printed `symbol [SKILL.md:3]` for compounds in the Base description. Each part survives in the body or references:
- core-determinism `MathF/Math`: the current description keeps `MathF`; `Math.Sin` and the `MathF` rows are in float-and-fixed-point.md.
- core-determinism `IL2CPP/Mono`: Docs version caveat names "Mono or IL2CPP".
- core-determinism `Dictionary/HashSet`: the stable-hashing reference bullet keeps `Dictionary`/`HashSet` as two backticked words.
- csvhelper-csv-data `GetRecords/WriteRecords`: step 3 keeps `GetRecords<T>()`/`WriteRecords()`.
- dotnet-concurrency-and-async `async/await`: step 6 and Never keep `await`/`.Wait()`; step 5 keeps `await foreach`.
- dotnet-concurrency-and-async `Parallel.ForEach`: step 6 keeps `Parallel.For`/`ForEach`; Docs keeps `Parallel.ForEachAsync`.
- roslyn-analyzer-codefix `Core/UnityEngine`: step 4 keeps "Core touching `UnityEngine`".
- shared-core-boundary-audit `UnityEngine/asmdef`: steps 1 and 2 keep both words.
- source-generator-authoring `equality/hashing`: the current description keeps "equality"; "hashing" was dropped in T2.
- stateless-state-machines `entry/exit`: steps 8 and 11 keep `OnEntry`/`OnExit`.
- zstring-zero-allocation-strings `TextMeshPro`: step 5 keeps `TextMeshProExtensions`.

## Bold title splits: 2 misses
- nrandom-random-generation step 6. The tool printed `bold [SKILL.md:24]: Weighted rolls use ... GetRandom(IRandom)`, `sequence randomness the NRandom.Linq extensions`, `always with the injected IRandom argument`. The full title is 170 chars, so with the reference link it passes the 200-char item limit. Split kept all three parts: title "Weighted rolls use `WeightedList<T>`/`IWeightedCollection<T>.GetRandom(IRandom)`", then `Sequence randomness: the NRandom.Linq extensions` and `Argument for both: always the injected IRandom`. "For both" keeps the shared scope.
- stateless-state-machines step 1. The tool printed `bold [SKILL.md:12]: Use a machine when a switch grows a branch per feature, bools like ... or a bug reduces to "in two states at once"`. The title is 150 chars. It became "Use a machine when any of the signs below appears" with nested `Switch`, `Bools` and `Bug` bullets that keep the three conditions word for word.

## Earlier misses fixed in this run
- nrandom step 3, roslyn steps 1, 5 and 8, stateless step 5: a first split changed the bold title. Titles were restored to the Base text, and the tool no longer flags them.
