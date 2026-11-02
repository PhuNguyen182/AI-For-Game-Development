# Cited anchors at Base

- **Base:** `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`. Files were read through `git show`, never the working tree.
- **Scope searched:** `.claude/` (hooks included), `framework-docs/`, `README.md`, `CLAUDE.md`, `.memory/notes/`, tracked files only.
- **Patterns:** `(?i)\bsteps?\s+\d+` with number lists and ranges expanded; `` `skill` `` then an arrow then a heading or file; `.claude/skills/<x>/(references|scripts)/<y>` paths; `$HookContracts` entries. Lettered sub-steps `step (a)` of `consent-att-init-order` added by hand, because the code sample cites them.
- **Rows:** 341.
- **By kind:** file 109, heading 8, hook 33, internal 3, path 21, step 167.
- **Resolved at Base:** 341 of 341.

## Must keep step numbers

A skill with any inbound or self citation keeps its numbers (spec: Numbers). `New steps` go after the last step.

| Skill | Inbound | Self | Cited numbers |
|---|---|---|---|
| `ad-mediation-monetization-platform` | 3 | 0 | 5, 8 |
| `build-fault-triage` | 1 | 0 | 8 |
| `compute-shader-vfx` | 1 | 0 | 10 |
| `consent-att-init-order` | 5 | 7 | 1, 2, 3, 8 |
| `core-determinism` | 1 | 2 | 2 |
| `core-scene-integration` | 0 | 1 | 8 |
| `core-tests-without-unity` | 3 | 2 | 3, 4, 7 |
| `crash-anr-symbolication` | 0 | 1 | 1 |
| `cross-platform-expansion-assessment` | 0 | 1 | 3 |
| `feature` | 11 | 14 | 1, 2, 3, 4, 5 |
| `firebase-unity-sdk` | 2 | 1 | 3, 4 |
| `fix` | 6 | 1 | 1, 3, 4, 6 |
| `git-forensics` | 1 | 0 | 6 |
| `git-safety-anchor` | 2 | 1 | 1, 5, 8 |
| `git-unity-repo` | 1 | 1 | 9, 10 |
| `iap-server-receipt-ledger` | 1 | 6 | 5, 8, 10 |
| `investigate-device-crash` | 2 | 0 | 1, 3 |
| `jenkins-pipeline-authoring` | 1 | 0 | 6 |
| `litmotion-tweening` | 0 | 1 | 9 |
| `live-ops-content-pipeline` | 5 | 0 | 3, 5, 7, 9 |
| `memorypack-serialization` | 3 | 0 | 9, 11 |
| `mobile-safe-area` | 1 | 3 | 4, 5, 6, 9 |
| `netcode-for-gameobjects` | 0 | 1 | 6 |
| `new-project` | 2 | 1 | 4, 5, 9 |
| `odin-inspector` | 0 | 1 | 7 |
| `performance-budget-verification` | 1 | 0 | 9 |
| `plan-game` | 1 | 1 | 3, 5 |
| `playtest-scenario-execution` | 0 | 1 | 10 |
| `qa` | 4 | 0 | 1, 2 |
| `release` | 11 | 6 | 1, 2, 3, 4, 7, 8, 9, 10, 11 |
| `resolve-merge-conflicts` | 3 | 5 | 1, 3, 5, 6, 9, 10, 11 |
| `risk-based-test-planning` | 1 | 0 | 8 |
| `save-data-versioning-migration` | 1 | 2 | 1, 3, 8, 10 |
| `secret-and-supply-chain-scan` | 5 | 1 | 1, 2, 3, 4, 5, 6, 7 |
| `server-authoritative-validation` | 1 | 4 | 1, 3, 5, 8, 9 |
| `shader-authoring` | 3 | 0 | 3, 4, 9 |
| `shared-core-boundary-audit` | 1 | 0 | 7 |
| `spine-animation` | 0 | 2 | 2, 7 |
| `ugui` | 1 | 2 | 3, 5 |
| `unitask-async-programming` | 0 | 3 | 2, 3, 5 |
| `unity-2d-sprite` | 0 | 1 | 1, 2 |
| `unity-3d-physics` | 1 | 0 | 3 |
| `unity-test-framework` | 4 | 0 | 1, 2, 3, 5, 11 |
| `vcontainer-dependency-injection` | 2 | 0 | 8 |
| `zlinq-zero-allocation-linq` | 0 | 2 | 4, 5 |

- **Keep:** 45 skills, above.
- **No step citation (79):** numbering is free, but a rewrite has no reason to change it: `agent-protocol`, `analytics-telemetry-platform`, `anti-cheat-strategy`, `backend-build-vs-buy`, `ci-pipeline-failure-triage`, `code-review-method`, `code-search`, `crash-anr-fault-domain-triage`, `crash-anr-reporting-gate`, `csharp-standards`, `csvhelper-csv-data`, `decide`, `design-precedent-sweep`, `device-test-walkthrough`, `dotnet-concurrency-and-async`, `dotnet-memory-and-collections`, `dotween-tweening`, `engineering-standard-adr-authoring`, `fastlane-mobile-delivery`, `feature-docs`, `firebase-app-distribution`, `flexalon-layouts`, `git-commit`, `git-recovery`, `magiconion-rpc-networking`, `mem`, `messagepipe-event-messaging`, `netcode-architecture-decision`, `netcode-for-entities`, `nrandom-random-generation`, `osa-optimized-scrollview-adapter`, `plan-test-coverage`, `practical-fit-screening`, `qa-standards`, `r3-reactive-extensions`, `render-pipeline-urp-hdrp`, `review`, `review-code-risks`, `roslyn-analyzer-codefix`, `save-workmemory`, `secret-exposure-response`, `solution-comparison-report`, `source-credibility-grading`, `source-generator-authoring`, `stateless-state-machines`, `tco-reversibility-scoring`, `tech-vendor-dependency-risk-assessment`, `technology-scouting-sweep`, `ui-toolkit`, `unity-2d-physics`, `unity-2d-spriteshape`, `unity-3d-mesh`, `unity-addressables`, `unity-animation`, `unity-audio-mixer`, `unity-batchmode-cli`, `unity-burst-compiler`, `unity-camera-fundamentals`, `unity-cinemachine-authoring`, `unity-collections`, `unity-ecs-architecture`, `unity-entities-graphics`, `unity-hdrp-rendering`, `unity-input-system`, `unity-job-system-and-burst`, `unity-lighting`, `unity-localization-text`, `unity-mathematics`, `unity-navmesh-navigation`, `unity-physics`, `unity-post-processing`, `unity-profiler-diagnostics`, `unity-scriptableobject-architecture`, `unity-tilemap`, `unity-transport`, `unity-urp-rendering`, `verify-layer`, `vfx-particle-authoring`, `zstring-zero-allocation-strings`.

## Rows

`internal` rows cite a numbered list inside the same reference; that list stays in order, and the row does not bind the SKILL.md numbers.

| Citing file:line | Cited skill | Anchor | Subject at Base |
|---|---|---|---|
| `.claude/agents/backend-engineer.md:33` | `live-ops-content-pipeline` | step 3 | Require a safe in-build default for every remote key |
| `.claude/agents/backend-engineer.md:33` | `live-ops-content-pipeline` | step 5 | Measure the rollback blast window in minutes |
| `.claude/agents/backend-engineer.md:33` | `live-ops-content-pipeline` | step 7 | Define schema versioning and old-client behaviour on an unknown or mis… |
| `.claude/agents/backend-engineer.md:44` | `save-data-versioning-migration` | step 1 | Decide whether the current format has shipped |
| `.claude/agents/backend-engineer.md:47` | `iap-server-receipt-ledger` | step 10 | Verify by running, never by reading |
| `.claude/agents/build-release-engineer.md:16` | `build-fault-triage` | step 8 | Route by evidenced cause |
| `.claude/agents/build-release-engineer.md:24` | `qa` | step 1 | ## 1. Plan — `qa-lead` (Plan) |
| `.claude/agents/build-release-engineer.md:37` | `release` | step 4 | gate row: Smoke test |
| `.claude/agents/build-release-engineer.md:43` | `release` | step 7 | gate row: Analytics + IAP |
| `.claude/agents/ci-cd-engineer.md:41` | `jenkins-pipeline-authoring` | step 6 | Publish tests so an empty result set fails |
| `.claude/agents/code-reviewer.md:21` | `code-review-method` | "Mode" | heading `Mode` |
| `.claude/agents/code-reviewer.md:29` | `review-code-risks` | `` references/risk-patterns.md `` | exists at Base |
| `.claude/agents/code-reviewer.md:32` | `code-review-method` | "Mode" | heading `Mode` |
| `.claude/agents/crash-anr-investigator.md:37` | `fix` | step 1 | ## 1. Record |
| `.claude/agents/csharp-engineer.md:22` | `core-tests-without-unity` | `dotnet-test-mirror.md` | `core-tests-without-unity/references/dotnet-test-mirror.md` |
| `.claude/agents/csharp-engineer.md:23` | `feature` | Lanes step 1 | `csharp-engineer` writes the `Contracts:` stubs, the Core/DataModels a… |
| `.claude/agents/csharp-engineer.md:29` | `csharp-standards` | `naming-convention.md` | `csharp-standards/references/naming-convention.md` |
| `.claude/agents/gameplay-engineer.md:21` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.claude/agents/git-expert.md:42` | `git-safety-anchor` | step 8 | Verify the anchor resolves |
| `.claude/agents/git-expert.md:60` | `git-safety-anchor` | step 1 | Classify blast radius before running anything |
| `.claude/agents/git-expert.md:73` | `git-forensics` | step 6 | `bisect` needs a deterministic pass/fail test first |
| `.claude/agents/netcode-engineer.md:46` | `server-authoritative-validation` | step 9 | Test every rejection path in a multi-client run |
| `.claude/agents/qa-automation-engineer.md:20` | `qa` | step 2 | ## 2. Execute — serial on the Editor, serial on the device |
| `.claude/agents/qa-automation-engineer.md:21` | `fix` | step 4 | ## 4. Regression test — mandatory |
| `.claude/agents/qa-automation-engineer.md:37` | `release` | step 8 | gate row: Save migration |
| `.claude/agents/qa-automation-engineer.md:40` | `unity-test-framework` | step 1 | Record the review status of the code under test |
| `.claude/agents/qa-lead.md:21` | `qa` | step 1 | ## 1. Plan — `qa-lead` (Plan) |
| `.claude/agents/qa-lead.md:28` | `qa` | step 1 | ## 1. Plan — `qa-lead` (Plan) |
| `.claude/agents/qa-lead.md:30` | `risk-based-test-planning` | step 8 | Exit criteria are evidence, not effort |
| `.claude/agents/qa-lead.md:32` | `qa-standards` | `bug-lifecycle.md` | `qa-standards/references/bug-lifecycle.md` |
| `.claude/agents/sdk-platform-engineer.md:46` | `consent-att-init-order` | step 3 | Fix the order and write it as one startup sequence |
| `.claude/agents/security-reviewer.md:27` | `secret-and-supply-chain-scan` | step 1 | Sweep for credential file types first |
| `.claude/agents/security-reviewer.md:28` | `secret-and-supply-chain-scan` | step 2 | Sweep contents for credential shapes, not keywords |
| `.claude/agents/security-reviewer.md:30` | `secret-and-supply-chain-scan` | steps 5-6 | 5: Scan imported third-party content for code that runs on import … 6: Flag source-less binaries |
| `.claude/agents/security-reviewer.md:31` | `secret-and-supply-chain-scan` | step 7 | Look for behaviour contradicting stated purpose |
| `.claude/agents/technical-architect.md:35` | `plan-game` | step 3 | ## 3. Features — `technical-architect` (Size mode), one brief for the whole list |
| `.claude/agents/technical-architect.md:43` | `csharp-standards` | `naming-convention.md` "Folders" | `csharp-standards/references/naming-convention.md` heading `Folders` |
| `.claude/agents/technical-architect.md:49` | `core-tests-without-unity` | step 4 | Add a `dotnet test` mirror only when `docs/tech-stack.md` or an ADR ad… |
| `.claude/agents/technical-artist.md:45` | `shader-authoring` | step 3 | Put every material-tunable property in one `UnityPerMaterial` CBUFFER |
| `.claude/agents/technical-artist.md:46` | `shader-authoring` | step 9 | Verify on every platform the Tech Spec targets |
| `.claude/agents/technical-artist.md:58` | `shader-authoring` | step 4 | `MaterialPropertyBlock` breaks the SRP batch for that renderer |
| `.claude/agents/technical-artist.md:59` | `compute-shader-vfx` | step 10 | Release every `ComputeBuffer` on every path |
| `.claude/agents/unity-performance-engineer.md:52` | `performance-budget-verification` | step 9 | State what was not measured |
| `.claude/hooks/common.ps1:310` | `mem` | `` scripts/mem.py `` | exists at Base |
| `.claude/hooks/editor-lock.ps1:124` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.claude/hooks/session-start.ps1:33` | `mem` | `` scripts/mem.py `` | exists at Base |
| `.claude/hooks/session-start.ps1:41` | `mem` | `` scripts/mem.py `` | exists at Base |
| `.claude/rules/core.md:37` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.claude/rules/routing.md:9` | `fix` | step 1 | ## 1. Record |
| `.claude/rules/routing.md:15` | `feature` | "change request" | heading `Change request (open feature; a closed feature takes new work instead)` |
| `.claude/rules/routing.md:34` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.claude/rules/routing.md:50` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.claude/skills/code-review-method/SKILL.md:27` | `review-code-risks` | `` references/risk-patterns.md `` | exists at Base |
| `.claude/skills/code-review-method/SKILL.md:30` | `qa-standards` | "A claim is verified only when" | heading `A claim is verified only when` |
| `.claude/skills/code-review-method/SKILL.md:46` | `csharp-standards` | `naming-convention.md` "Folders" | `csharp-standards/references/naming-convention.md` heading `Folders` |
| `.claude/skills/code-review-method/SKILL.md:47` | `csharp-standards` | "Asset names" | labelled text: Asset names (specs use them too): Prefab `Category_Name` · `… |
| `.claude/skills/code-review-method/SKILL.md:55` | `qa-standards` | "A finding has" | heading `A finding has` |
| `.claude/skills/compute-shader-vfx/SKILL.md:14` | `csharp-standards` | `coding-principles.md` "SOLID" | `csharp-standards/references/coding-principles.md` heading `SOLID` |
| `.claude/skills/compute-shader-vfx/SKILL.md:18` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/compute-shader-vfx/SKILL.md:21` | `csharp-standards` | `performance-and-algorithms.md` "Memory discipline" | `csharp-standards/references/performance-and-algorithms.md` heading `Memory discipline` |
| `.claude/skills/compute-shader-vfx/SKILL.md:23` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/consent-att-init-order/SKILL.md:9` | `ad-mediation-monetization-platform` | step 8 | Consent and audience gate on mediation, before scoring |
| `.claude/skills/consent-att-init-order/SKILL.md:10` | `consent-att-init-order` | step 2 | Fetch current store policy with `WebFetch` before writing |
| `.claude/skills/consent-att-init-order/SKILL.md:19` | `ad-mediation-monetization-platform` | step 8 | Consent and audience gate on mediation, before scoring |
| `.claude/skills/consent-att-init-order/SKILL.md:21` | `firebase-unity-sdk` | step 4 | One bootstrap owns `FirebaseApp.CheckAndFixDependenciesAsync()`; every… |
| `.claude/skills/consent-att-init-order/SKILL.md:21` | `firebase-unity-sdk` | `analytics.md` | `firebase-unity-sdk/references/analytics.md` |
| `.claude/skills/consent-att-init-order/SKILL.md:22` | `firebase-unity-sdk` | `analytics.md` | `firebase-unity-sdk/references/analytics.md` |
| `.claude/skills/consent-att-init-order/SKILL.md:22` | `firebase-unity-sdk` | `crashlytics.md` | `firebase-unity-sdk/references/crashlytics.md` |
| `.claude/skills/consent-att-init-order/SKILL.md:26` | `consent-att-init-order` | step 3(d) | Fix the order and write it as one startup sequence |
| `.claude/skills/consent-att-init-order/SKILL.md:26` | `consent-att-init-order` | step 3(e) | Fix the order and write it as one startup sequence |
| `.claude/skills/consent-att-init-order/SKILL.md:26` | `firebase-unity-sdk` | `crashlytics.md` | `firebase-unity-sdk/references/crashlytics.md` |
| `.claude/skills/consent-att-init-order/references/child-audience-flags.md:63` | `firebase-unity-sdk` | `analytics.md` | `firebase-unity-sdk/references/analytics.md` |
| `.claude/skills/consent-att-init-order/references/google-ump.md:28` | `consent-att-init-order` | step 3(a) | Fix the order and write it as one startup sequence sub-step (a) |
| `.claude/skills/consent-att-init-order/references/google-ump.md:47` | `firebase-unity-sdk` | step 4 | One bootstrap owns `FirebaseApp.CheckAndFixDependenciesAsync()`; every… |
| `.claude/skills/consent-att-init-order/references/google-ump.md:47` | `consent-att-init-order` | step 3(d) | Fix the order and write it as one startup sequence sub-step (d) |
| `.claude/skills/consent-att-init-order/references/google-ump.md:65` | `consent-att-init-order` | step 3(e) | Fix the order and write it as one startup sequence sub-step (e) |
| `.claude/skills/consent-att-init-order/references/google-ump.md:89` | `consent-att-init-order` | step 8 | Privacy-options entry point is required |
| `.claude/skills/core-determinism/SKILL.md:19` | `core-determinism` | step 2 | Route float vs fixed-point; never decide it |
| `.claude/skills/core-determinism/references/float-and-fixed-point.md:5` | `core-determinism` | step 2 | Route float vs fixed-point; never decide it |
| `.claude/skills/core-determinism/references/replay-test.md:3` | `core-scene-integration` | `tick-and-interpolation.md` | `core-scene-integration/references/tick-and-interpolation.md` |
| `.claude/skills/core-scene-integration/SKILL.md:30` | `core-scene-integration` | step 8 | Interpolate for rendering only |
| `.claude/skills/core-scene-integration/references/input-and-physics-into-core.md:3` | `unity-input-system` | `migration-and-settings.md` | `unity-input-system/references/migration-and-settings.md` |
| `.claude/skills/core-scene-integration/references/input-and-physics-into-core.md:12` | `vcontainer-dependency-injection` | step 8 | Sequence startup through entry points, not `Awake`/`Start` order |
| `.claude/skills/core-scene-integration/references/input-and-physics-into-core.md:58` | `unity-3d-physics` | step 3 | Move simulated bodies through the physics API |
| `.claude/skills/core-scene-integration/references/tick-and-interpolation.md:9` | `vcontainer-dependency-injection` | step 8 | Sequence startup through entry points, not `Awake`/`Start` order |
| `.claude/skills/core-scene-integration/references/tick-and-interpolation.md:12` | `netcode-for-gameobjects` | `transform-latency.md` | `netcode-for-gameobjects/references/transform-latency.md` |
| `.claude/skills/core-tests-without-unity/SKILL.md:17` | `csharp-standards` | `naming-convention.md` "Folders" | `csharp-standards/references/naming-convention.md` heading `Folders` |
| `.claude/skills/core-tests-without-unity/SKILL.md:18` | `unity-test-framework` | steps 2-3 | 2: Test Core in Edit Mode … 3: Set up the assembly and mode marker first |
| `.claude/skills/core-tests-without-unity/SKILL.md:19` | `unity-test-framework` | step 5 | Inject the seed and clock production code already takes |
| `.claude/skills/core-tests-without-unity/SKILL.md:22` | `shared-core-boundary-audit` | step 7 | Open every hit and cite `path:line` |
| `.claude/skills/core-tests-without-unity/SKILL.md:23` | `core-tests-without-unity` | step 4 | Add a `dotnet test` mirror only when `docs/tech-stack.md` or an ADR ad… |
| `.claude/skills/core-tests-without-unity/references/dotnet-test-mirror.md:95` | `core-tests-without-unity` | step 7 | Mirror adopted (step 4) → run both runners and compare; a test that pa… |
| `.claude/skills/crash-anr-fault-domain-triage/references/anr-classes-and-mitigation.md:33` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/crash-anr-symbolication/SKILL.md:21` | `crash-anr-symbolication` | step 1 | Check the faulting (top) frame before counting resolved frames |
| `.claude/skills/cross-platform-expansion-assessment/SKILL.md:19` | `cross-platform-expansion-assessment` | step 3 | Check whether the platform invalidates a foundational decision first |
| `.claude/skills/design-precedent-sweep/SKILL.md:15` | `source-credibility-grading` | "Precedent claims" | labelled text: **Precedent claims** (how a shipped game solved a problem):… |
| `.claude/skills/device-test-walkthrough/SKILL.md:20` | `device-test-walkthrough` | `` scripts/device_playtest.py `` | exists at Base |
| `.claude/skills/device-test-walkthrough/scripts/device_playtest.py:17` | `investigate-device-crash` | step 1 | Device |
| `.claude/skills/device-test-walkthrough/scripts/device_playtest.py:17` | `investigate-device-crash` | step 3 | Evidence |
| `.claude/skills/feature/SKILL.md:10` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.claude/skills/feature/SKILL.md:16` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.claude/skills/feature/SKILL.md:19` | `feature` | Lanes step 4 | Merge once, after lane B's last agent: commit each worktree on its bra… |
| `.claude/skills/feature/SKILL.md:30` | `feature` | step 3 | ## 3. Spec + CP2 — `technical-architect` (Spec mode) |
| `.claude/skills/feature/SKILL.md:38` | `feature` | step 2 | ## 2. CP1 — runs per `routing.md` → Profile defaults → CP1 + `critic` |
| `.claude/skills/feature/SKILL.md:38` | `feature` | step 1 | ## 1. Size — `technical-architect` (Size mode) |
| `.claude/skills/feature/SKILL.md:46` | `csharp-standards` | `naming-convention.md` "Folders" | `csharp-standards/references/naming-convention.md` heading `Folders` |
| `.claude/skills/feature/SKILL.md:49` | `unity-test-framework` | step 11 | Scope CI runs with filters and pair `-runTests` with `-batchmode` |
| `.claude/skills/feature/SKILL.md:57` | `core-tests-without-unity` | step 7 | Mirror adopted (step 4) → run both runners and compare; a test that pa… |
| `.claude/skills/feature/SKILL.md:63` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.claude/skills/feature/SKILL.md:66` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.claude/skills/feature/SKILL.md:66` | `feature` | step 5 | ## 5. Gate offer — one `AskUserQuestion`, two questions |
| `.claude/skills/feature/SKILL.md:68` | `feature` | step 5 | ## 5. Gate offer — one `AskUserQuestion`, two questions |
| `.claude/skills/feature/SKILL.md:74` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.claude/skills/feature/SKILL.md:74` | `feature` | step 5 | ## 5. Gate offer — one `AskUserQuestion`, two questions |
| `.claude/skills/feature/SKILL.md:79` | `feature` | step 2 | ## 2. CP1 — runs per `routing.md` → Profile defaults → CP1 + `critic` |
| `.claude/skills/feature/SKILL.md:81` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.claude/skills/firebase-unity-sdk/SKILL.md:21` | `firebase-unity-sdk` | step 3 | CONFIG FILES |
| `.claude/skills/firebase-unity-sdk/SKILL.md:23` | `secret-and-supply-chain-scan` | steps 3-4 | 3: Classify each hit against the public-identifier allowlist … 4: Unresolvable value → `Needs Confirmation` |
| `.claude/skills/firebase-unity-sdk/SKILL.md:24` | `consent-att-init-order` | step 3 | Fix the order and write it as one startup sequence |
| `.claude/skills/firebase-unity-sdk/SKILL.md:26` | `consent-att-init-order` | step 3(d) | Fix the order and write it as one startup sequence |
| `.claude/skills/firebase-unity-sdk/SKILL.md:28` | `live-ops-content-pipeline` | step 3 | Require a safe in-build default for every remote key |
| `.claude/skills/firebase-unity-sdk/SKILL.md:28` | `live-ops-content-pipeline` | step 9 | Set the standard: every config read through one access module |
| `.claude/skills/firebase-unity-sdk/SKILL.md:29` | `consent-att-init-order` | step 1 | Audience and jurisdictions first |
| `.claude/skills/firebase-unity-sdk/references/analytics.md:44` | `consent-att-init-order` | step 1 | Audience and jurisdictions first |
| `.claude/skills/fix/SKILL.md:9` | `qa-standards` | `` references/bug-lifecycle.md `` | exists at Base |
| `.claude/skills/fix/SKILL.md:31` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.claude/skills/fix/SKILL.md:36` | `fix` | step 3 | ## 3. Root cause |
| `.claude/skills/fix/SKILL.md:40` | `release` | step 4 | gate row: Smoke test |
| `.claude/skills/fix/SKILL.md:40` | `release` | step 1 | gate row: Open bugs |
| `.claude/skills/git-recovery/references/history-surgery.md:26` | `git-recovery` | own list step 5 (internal) | this file's numbered list: Hand the GD the push. `filter-repo` removes `origin` on purpose: `git… |
| `.claude/skills/git-recovery/references/history-surgery.md:29` | `git-forensics` | `secret-history-archaeology.md` | `git-forensics/references/secret-history-archaeology.md` |
| `.claude/skills/git-recovery/references/history-surgery.md:30` | `git-recovery` | own list step 1 (internal) | this file's numbered list: Record the remote's refs outside every repo: `git ls-remote --heads --… |
| `.claude/skills/git-safety-anchor/SKILL.md:20` | `git-safety-anchor` | step 5 | Record the pre-state as shas |
| `.claude/skills/git-unity-repo/references/routine-workflows.md:13` | `resolve-merge-conflicts` | step 1 | Context |
| `.claude/skills/git-unity-repo/references/routine-workflows.md:35` | `git-unity-repo` | step 9 | Verify LFS-tracked binaries are content, not pointers |
| `.claude/skills/git-unity-repo/references/scene-and-prefab-conflicts.md:20` | `resolve-merge-conflicts` | step 6 | Unity YAML |
| `.claude/skills/git-unity-repo/references/scene-and-prefab-conflicts.md:56` | `resolve-merge-conflicts` | step 6 | Unity YAML |
| `.claude/skills/iap-server-receipt-ledger/SKILL.md:21` | `ad-mediation-monetization-platform` | step 5 | Ledger authority first |
| `.claude/skills/iap-server-receipt-ledger/SKILL.md:23` | `iap-server-receipt-ledger` | step 5 | Commit grant and ledger entry in one transaction |
| `.claude/skills/iap-server-receipt-ledger/SKILL.md:25` | `iap-server-receipt-ledger` | step 8 | Reverse grants per void event |
| `.claude/skills/iap-server-receipt-ledger/SKILL.md:26` | `iap-server-receipt-ledger` | step 8 | Reverse grants per void event |
| `.claude/skills/iap-server-receipt-ledger/SKILL.md:30` | `release` | step 7 | gate row: Analytics + IAP |
| `.claude/skills/iap-server-receipt-ledger/references/ugs-cloud-code-economy.md:9` | `iap-server-receipt-ledger` | step 5 | Commit grant and ledger entry in one transaction |
| `.claude/skills/iap-server-receipt-ledger/references/ugs-cloud-code-economy.md:9` | `iap-server-receipt-ledger` | step 8 | Reverse grants per void event |
| `.claude/skills/iap-server-receipt-ledger/references/ugs-cloud-code-economy.md:10` | `iap-server-receipt-ledger` | step 5 | Commit grant and ledger entry in one transaction |
| `.claude/skills/investigate-device-crash/SKILL.md:15` | `build-fault-triage` | `` SKILL.md `` | exists at Base |
| `.claude/skills/investigate-device-crash/SKILL.md:15` | `crash-anr-fault-domain-triage` | `` references/fault-domain-signals.md `` | exists at Base |
| `.claude/skills/litmotion-tweening/SKILL.md:27` | `litmotion-tweening` | step 9 | Custom `IMotionAdapter` |
| `.claude/skills/mem/SKILL.md:9` | `mem` | `` scripts/mem.py `` | exists at Base |
| `.claude/skills/mem/references/schema.md:34` | `mem` | `` scripts/test_mem.py `` | exists at Base |
| `.claude/skills/mobile-safe-area/SKILL.md:17` | `mobile-safe-area` | step 5 | UI Toolkit: padding in panel space |
| `.claude/skills/mobile-safe-area/SKILL.md:17` | `mobile-safe-area` | steps 4-6 | 4: uGUI fitter: drive anchors, not offsets … 6: Re-apply only on change |
| `.claude/skills/mobile-safe-area/SKILL.md:20` | `ugui` | step 5 | One owner per `RectTransform` size |
| `.claude/skills/mobile-safe-area/SKILL.md:26` | `mobile-safe-area` | step 9 | Target devices or aspect ratios unstated |
| `.claude/skills/netcode-architecture-decision/SKILL.md:15` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/netcode-for-entities/SKILL.md:33` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/netcode-for-entities/SKILL.md:37` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/netcode-for-entities/SKILL.md:38` | `csharp-standards` | `coding-principles.md` "Handoff" | `csharp-standards/references/coding-principles.md` heading `Handoff` |
| `.claude/skills/netcode-for-entities/references/prediction-caveats.md:31` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/netcode-for-entities/references/testing-and-debugging.md:3` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/netcode-for-gameobjects/SKILL.md:26` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/netcode-for-gameobjects/SKILL.md:51` | `netcode-for-gameobjects` | step 6 | Sync transforms with NetworkTransform, not hand-rolled position Rpcs |
| `.claude/skills/new-project/SKILL.md:20` | `csharp-standards` | `naming-convention.md` "Folders" | `csharp-standards/references/naming-convention.md` heading `Folders` |
| `.claude/skills/new-project/SKILL.md:29` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.claude/skills/new-project/SKILL.md:45` | `new-project` | step 9 | ## 9. Report |
| `.claude/skills/nrandom-random-generation/SKILL.md:21` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/nrandom-random-generation/SKILL.md:24` | `core-determinism` | step 2 | Route float vs fixed-point; never decide it |
| `.claude/skills/nrandom-random-generation/references/numerics-and-unity-integration.md:26` | `csharp-standards` | `naming-convention.md` "Folders" | `csharp-standards/references/naming-convention.md` heading `Folders` |
| `.claude/skills/odin-inspector/SKILL.md:23` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/odin-inspector/SKILL.md:27` | `csharp-standards` | `naming-convention.md` | `csharp-standards/references/naming-convention.md` |
| `.claude/skills/odin-inspector/references/editor-extensibility.md:54` | `odin-inspector` | step 7 | Odin Validator project-wide scans (`Validator<T>`, `RegisterValidatorA… |
| `.claude/skills/odin-inspector/references/serialization.md:33` | `csharp-standards` | `coding-principles.md` "Handoff" | `csharp-standards/references/coding-principles.md` heading `Handoff` |
| `.claude/skills/osa-optimized-scrollview-adapter/SKILL.md:36` | `csharp-standards` | `coding-principles.md` | `csharp-standards/references/coding-principles.md` |
| `.claude/skills/osa-optimized-scrollview-adapter/SKILL.md:36` | `csharp-standards` | `naming-convention.md` | `csharp-standards/references/naming-convention.md` |
| `.claude/skills/performance-budget-verification/SKILL.md:18` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/plan-game/SKILL.md:29` | `plan-game` | steps 3-5 | 3: ## 3. Features — `technical-architect` (Size mode), one brief for the whole list … 5: ## 5. Approve — `AskUserQuestion` |
| `.claude/skills/playtest-scenario-execution/SKILL.md:26` | `playtest-scenario-execution` | step 10 | Multi-client scenario → MPPM virtual players |
| `.claude/skills/practical-fit-screening/SKILL.md:16` | `csharp-standards` | `coding-principles.md` "Modern C# syntax" | `csharp-standards/references/coding-principles.md` heading `Modern C# syntax — check the project's language version first` |
| `.claude/skills/qa/SKILL.md:23` | `fix` | step 6 | ## 6. Verify |
| `.claude/skills/qa/SKILL.md:27` | `fix` | step 1 | ## 1. Record |
| `.claude/skills/release/SKILL.md:9` | `release` | step 2 | gate row: Version bump |
| `.claude/skills/release/SKILL.md:16` | `release` | step 4 | gate row: Smoke test |
| `.claude/skills/release/SKILL.md:16` | `release` | step 4 | gate row: Smoke test |
| `.claude/skills/release/SKILL.md:29` | `release` | steps 3-8 | 3: gate row: Build per platform … 8: gate row: Save migration |
| `.claude/skills/release/SKILL.md:29` | `release` | step 4 | gate row: Smoke test |
| `.claude/skills/resolve-merge-conflicts/SKILL.md:15` | `resolve-merge-conflicts` | step 5 | Small: standards |
| `.claude/skills/resolve-merge-conflicts/SKILL.md:17` | `resolve-merge-conflicts` | step 10 | Verify |
| `.claude/skills/resolve-merge-conflicts/SKILL.md:17` | `resolve-merge-conflicts` | steps 3-5 | 3: Classify scope … 5: Small: standards |
| `.claude/skills/resolve-merge-conflicts/SKILL.md:17` | `git-unity-repo` | `scene-and-prefab-conflicts.md` | `git-unity-repo/references/scene-and-prefab-conflicts.md` |
| `.claude/skills/resolve-merge-conflicts/SKILL.md:18` | `resolve-merge-conflicts` | step 9 | Reference-wiring pass |
| `.claude/skills/resolve-merge-conflicts/SKILL.md:21` | `git-unity-repo` | step 10 | Close the Unity Editor before any command that rewrites the working tr… |
| `.claude/skills/resolve-merge-conflicts/SKILL.md:23` | `resolve-merge-conflicts` | steps 1-11 | 1: Context … 11: Stage and report |
| `.claude/skills/review-code-risks/references/risk-patterns.md:6` | `csharp-standards` | `performance-and-algorithms.md` | `csharp-standards/references/performance-and-algorithms.md` |
| `.claude/skills/review-code-risks/references/risk-patterns.md:20` | `csharp-standards` | `coding-principles.md` "Exception handling" | `csharp-standards/references/coding-principles.md` heading `Exception handling` |
| `.claude/skills/review-code-risks/references/risk-patterns.md:23` | `crash-anr-fault-domain-triage` | `` references/anr-classes-and-mitigation.md `` | exists at Base |
| `.claude/skills/roslyn-analyzer-codefix/SKILL.md:9` | `csharp-standards` | `coding-principles.md` | `csharp-standards/references/coding-principles.md` |
| `.claude/skills/save-data-versioning-migration/SKILL.md:16` | `release` | step 8 | gate row: Save migration |
| `.claude/skills/save-data-versioning-migration/SKILL.md:19` | `save-data-versioning-migration` | steps 3-10 | 3: Change a shipped shape only through a successor type … 10: Fill `Save migration:` |
| `.claude/skills/save-data-versioning-migration/SKILL.md:21` | `memorypack-serialization` | step 11 | Changing a shipped type: whether live saves or in-flight messages exis… |
| `.claude/skills/save-data-versioning-migration/SKILL.md:27` | `release` | step 8 | gate row: Save migration |
| `.claude/skills/save-data-versioning-migration/references/golden-save-fixtures.md:3` | `release` | step 8 | gate row: Save migration |
| `.claude/skills/save-data-versioning-migration/references/golden-save-fixtures.md:3` | `new-project` | step 4 | ## 4. Structure — `gameplay-engineer` |
| `.claude/skills/save-data-versioning-migration/references/golden-save-fixtures.md:3` | `core-tests-without-unity` | step 3 | Write every Core test mirror-ready, mirror or not |
| `.claude/skills/save-data-versioning-migration/references/golden-save-fixtures.md:3` | `memorypack-serialization` | step 11 | Changing a shipped type: whether live saves or in-flight messages exis… |
| `.claude/skills/save-data-versioning-migration/references/golden-save-fixtures.md:40` | `release` | step 8 | gate row: Save migration |
| `.claude/skills/save-data-versioning-migration/references/golden-save-fixtures.md:46` | `release` | step 8 | gate row: Save migration |
| `.claude/skills/save-data-versioning-migration/references/version-envelope-and-chain.md:14` | `save-data-versioning-migration` | step 8 | Sync cloud copies as the same envelope bytes, from Client code |
| `.claude/skills/save-data-versioning-migration/references/version-envelope-and-chain.md:39` | `memorypack-serialization` | step 9 | Validate the payload at the call site that owns the trust decision |
| `.claude/skills/secret-and-supply-chain-scan/SKILL.md:15` | `secret-and-supply-chain-scan` | step 4 | Unresolvable value → `Needs Confirmation` |
| `.claude/skills/secret-and-supply-chain-scan/SKILL.md:19` | `csharp-standards` | `coding-principles.md` | `csharp-standards/references/coding-principles.md` |
| `.claude/skills/server-authoritative-validation/SKILL.md:19` | `server-authoritative-validation` | step 1 | Confirm the server is authoritative for this outcome |
| `.claude/skills/server-authoritative-validation/SKILL.md:19` | `server-authoritative-validation` | steps 3-8 | 3: Take the sender from the transport, never the payload … 8: Reject with authoritative state, leak nothing |
| `.claude/skills/server-authoritative-validation/SKILL.md:19` | `netcode-for-gameobjects` | `core-architecture.md` | `netcode-for-gameobjects/references/core-architecture.md` |
| `.claude/skills/server-authoritative-validation/SKILL.md:22` | `netcode-for-gameobjects` | `serialization.md` | `netcode-for-gameobjects/references/serialization.md` |
| `.claude/skills/server-authoritative-validation/SKILL.md:24` | `server-authoritative-validation` | step 3 | Take the sender from the transport, never the payload |
| `.claude/skills/server-authoritative-validation/SKILL.md:24` | `server-authoritative-validation` | step 5 | Make the decode cost fixed, then bounds-check it |
| `.claude/skills/server-authoritative-validation/references/rate-limits-and-rejection.md:10` | `netcode-for-gameobjects` | `transform-latency.md` | `netcode-for-gameobjects/references/transform-latency.md` |
| `.claude/skills/server-authoritative-validation/references/rate-limits-and-rejection.md:11` | `netcode-for-entities` | `rpcs-and-commands.md` | `netcode-for-entities/references/rpcs-and-commands.md` |
| `.claude/skills/server-authoritative-validation/references/sender-identity-per-stack.md:16` | `netcode-for-gameobjects` | `serialization.md` | `netcode-for-gameobjects/references/serialization.md` |
| `.claude/skills/server-authoritative-validation/references/sender-identity-per-stack.md:53` | `netcode-for-entities` | `transport-and-connection.md` | `netcode-for-entities/references/transport-and-connection.md` |
| `.claude/skills/server-authoritative-validation/references/sender-identity-per-stack.md:76` | `unity-transport` | `core-driver-lifecycle.md` | `unity-transport/references/core-driver-lifecycle.md` |
| `.claude/skills/shader-authoring/SKILL.md:16` | `csharp-standards` | `performance-and-algorithms.md` | `csharp-standards/references/performance-and-algorithms.md` |
| `.claude/skills/shared-core-boundary-audit/SKILL.md:10` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/source-generator-authoring/SKILL.md:15` | `csharp-standards` | `coding-principles.md` "Obsolete APIs" | `csharp-standards/references/coding-principles.md` heading `Obsolete APIs` |
| `.claude/skills/source-generator-authoring/SKILL.md:21` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/spine-animation/SKILL.md:24` | `spine-animation` | step 2 | Pick the component |
| `.claude/skills/spine-animation/SKILL.md:24` | `spine-animation` | step 7 | Match shader family to pipeline |
| `.claude/skills/spine-animation/SKILL.md:36` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/stateless-state-machines/SKILL.md:9` | `csharp-standards` | `coding-principles.md` "YAGNI" | `csharp-standards/references/coding-principles.md` heading `YAGNI — You Aren't Gonna Need It` |
| `.claude/skills/stateless-state-machines/SKILL.md:12` | `csharp-standards` | `coding-principles.md` "SOLID" | `csharp-standards/references/coding-principles.md` heading `SOLID` |
| `.claude/skills/stateless-state-machines/SKILL.md:13` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/stateless-state-machines/SKILL.md:15` | `csharp-standards` | `naming-convention.md` | `csharp-standards/references/naming-convention.md` |
| `.claude/skills/stateless-state-machines/SKILL.md:21` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/ugui/references/canvas-and-scaling.md:22` | `ugui` | step 3 | Use Scale With Screen Size and set Match deliberately |
| `.claude/skills/ugui/references/profiling-performance-and-howtos.md:17` | `ugui` | step 3 | Use Scale With Screen Size and set Match deliberately |
| `.claude/skills/ui-toolkit/references/choosing-ui-system.md:26` | `csharp-standards` | `naming-convention.md` | `csharp-standards/references/naming-convention.md` |
| `.claude/skills/ui-toolkit/references/rendering-and-performance.md:33` | `csharp-standards` | `performance-and-algorithms.md` | `csharp-standards/references/performance-and-algorithms.md` |
| `.claude/skills/unitask-async-programming/SKILL.md:22` | `unitask-async-programming` | step 2 | Cancelable methods take a `CancellationToken` as the last parameter |
| `.claude/skills/unitask-async-programming/SKILL.md:22` | `unitask-async-programming` | step 3 | Pool the `CancellationTokenSource` on repeatable paths |
| `.claude/skills/unitask-async-programming/SKILL.md:22` | `unitask-async-programming` | step 5 | `UniTask` is single-consumption |
| `.claude/skills/unity-2d-physics/SKILL.md:25` | `csharp-standards` | `performance-and-algorithms.md` | `csharp-standards/references/performance-and-algorithms.md` |
| `.claude/skills/unity-2d-physics/SKILL.md:30` | `csharp-standards` | `coding-principles.md` | `csharp-standards/references/coding-principles.md` |
| `.claude/skills/unity-2d-sprite/SKILL.md:31` | `unity-2d-sprite` | steps 1-2 | 1: Settle Pixels Per Unit against the existing visual set first … 2: Pick Mesh Type by 9-slicing, not overdraw instinct |
| `.claude/skills/unity-2d-sprite/references/sorting-sprites.md:13` | `unity-2d-sprite` | own list step 4 (internal) | this file's numbered list: Distance from camera |
| `.claude/skills/unity-2d-spriteshape/SKILL.md:29` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/unity-2d-spriteshape/SKILL.md:31` | `csharp-standards` | `performance-and-algorithms.md` | `csharp-standards/references/performance-and-algorithms.md` |
| `.claude/skills/unity-2d-spriteshape/references/custom-geometry-scripting.md:5` | `csharp-standards` | `performance-and-algorithms.md` "Multithreading" | `csharp-standards/references/performance-and-algorithms.md` heading `Multithreading — escalation territory, not a routine default` |
| `.claude/skills/unity-animation/SKILL.md:31` | `csharp-standards` | `performance-and-algorithms.md` | `csharp-standards/references/performance-and-algorithms.md` |
| `.claude/skills/unity-animation/SKILL.md:33` | `csharp-standards` | `coding-principles.md` "YAGNI" | `csharp-standards/references/coding-principles.md` heading `YAGNI — You Aren't Gonna Need It` |
| `.claude/skills/unity-animation/SKILL.md:34` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/unity-animation/SKILL.md:35` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/unity-animation/references/mecanim-overview.md:32` | `csharp-standards` | `coding-principles.md` | `csharp-standards/references/coding-principles.md` |
| `.claude/skills/unity-animation/references/performance-and-faq.md:21` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/unity-animation/references/playables-api.md:5` | `csharp-standards` | `coding-principles.md` | `csharp-standards/references/coding-principles.md` |
| `.claude/skills/unity-burst-compiler/SKILL.md:21` | `csharp-standards` | `performance-and-algorithms.md` "Multithreading" | `csharp-standards/references/performance-and-algorithms.md` heading `Multithreading — escalation territory, not a routine default` |
| `.claude/skills/unity-burst-compiler/SKILL.md:24` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/unity-burst-compiler/SKILL.md:34` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/unity-camera-fundamentals/SKILL.md:9` | `csharp-standards` | `coding-principles.md` | `csharp-standards/references/coding-principles.md` |
| `.claude/skills/unity-camera-fundamentals/SKILL.md:28` | `csharp-standards` | `coding-principles.md` | `csharp-standards/references/coding-principles.md` |
| `.claude/skills/unity-camera-fundamentals/SKILL.md:37` | `csharp-standards` | `coding-principles.md` "Obsolete APIs" | `csharp-standards/references/coding-principles.md` heading `Obsolete APIs` |
| `.claude/skills/unity-camera-fundamentals/references/culling-and-multi-camera.md:23` | `csharp-standards` | `performance-and-algorithms.md` "Memory discipline" | `csharp-standards/references/performance-and-algorithms.md` heading `Memory discipline` |
| `.claude/skills/unity-collections/SKILL.md:21` | `csharp-standards` | `performance-and-algorithms.md` | `csharp-standards/references/performance-and-algorithms.md` |
| `.claude/skills/unity-collections/SKILL.md:27` | `csharp-standards` | `performance-and-algorithms.md` "Memory discipline" | `csharp-standards/references/performance-and-algorithms.md` heading `Memory discipline` |
| `.claude/skills/unity-entities-graphics/SKILL.md:32` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/unity-input-system/SKILL.md:42` | `csharp-standards` | `coding-principles.md` "Obsolete APIs" | `csharp-standards/references/coding-principles.md` heading `Obsolete APIs` |
| `.claude/skills/unity-input-system/references/rebinding.md:14` | `csharp-standards` | `coding-principles.md` "Exception handling" | `csharp-standards/references/coding-principles.md` heading `Exception handling` |
| `.claude/skills/unity-job-system-and-burst/SKILL.md:20` | `csharp-standards` | `performance-and-algorithms.md` "Multithreading" | `csharp-standards/references/performance-and-algorithms.md` heading `Multithreading — escalation territory, not a routine default` |
| `.claude/skills/unity-job-system-and-burst/SKILL.md:22` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/unity-job-system-and-burst/SKILL.md:30` | `csharp-standards` | `performance-and-algorithms.md` "Memory discipline" | `csharp-standards/references/performance-and-algorithms.md` heading `Memory discipline` |
| `.claude/skills/unity-job-system-and-burst/SKILL.md:31` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/unity-lighting/SKILL.md:46` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/unity-localization-text/SKILL.md:27` | `mobile-safe-area` | step 9 | Target devices or aspect ratios unstated |
| `.claude/skills/unity-localization-text/references/font-fallback-and-expansion.md:26` | `ui-toolkit` | `text-and-fonts.md` | `ui-toolkit/references/text-and-fonts.md` |
| `.claude/skills/unity-localization-text/references/font-fallback-and-expansion.md:39` | `ui-toolkit` | `text-and-fonts.md` | `ui-toolkit/references/text-and-fonts.md` |
| `.claude/skills/unity-mathematics/SKILL.md:19` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/unity-mathematics/SKILL.md:26` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/unity-physics/SKILL.md:24` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/unity-test-framework/SKILL.md:20` | `fix` | step 4 | ## 4. Regression test — mandatory |
| `.claude/skills/unity-urp-rendering/SKILL.md:22` | `csharp-standards` | `coding-principles.md` "Obsolete APIs" | `csharp-standards/references/coding-principles.md` heading `Obsolete APIs` |
| `.claude/skills/unity-urp-rendering/SKILL.md:25` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/unity-urp-rendering/SKILL.md:29` | `csharp-standards` | `coding-principles.md` "Performance discipline" | `csharp-standards/references/coding-principles.md` heading `Performance discipline (both PC and mobile — mobile is the tighter budget)` |
| `.claude/skills/vcontainer-dependency-injection/SKILL.md:9` | `csharp-standards` | `coding-principles.md` "Shared Core integrity" | `csharp-standards/references/coding-principles.md` heading `Shared Core integrity` |
| `.claude/skills/vcontainer-dependency-injection/SKILL.md:21` | `csharp-standards` | `performance-and-algorithms.md` "Update loop & callback overhead" | `csharp-standards/references/performance-and-algorithms.md` heading `Update loop & callback overhead` |
| `.claude/skills/verify-layer/scripts/verify.ps1:40` | `agent-protocol` | `` SKILL.md `` | exists at Base |
| `.claude/skills/verify-layer/scripts/verify.ps1:42` | `review` | `` SKILL.md `` | exists at Base |
| `.claude/skills/verify-layer/scripts/verify.ps1:43` | `qa` | `` SKILL.md `` | exists at Base |
| `.claude/skills/verify-layer/scripts/verify.ps1:44` | `fix` | `` SKILL.md `` | exists at Base |
| `.claude/skills/verify-layer/scripts/verify.ps1:45` | `feature` | `` references/feature-template.md `` | exists at Base |
| `.claude/skills/verify-layer/scripts/verify.ps1:46` | `fix` | `` references/bugs-template.md `` | exists at Base |
| `.claude/skills/vfx-particle-authoring/SKILL.md:27` | `csharp-standards` | `performance-and-algorithms.md` | `csharp-standards/references/performance-and-algorithms.md` |
| `.claude/skills/vfx-particle-authoring/references/particle-system-modules.md:41` | `csharp-standards` | `performance-and-algorithms.md` | `csharp-standards/references/performance-and-algorithms.md` |
| `.claude/skills/vfx-particle-authoring/references/rendering-and-budget.md:28` | `csharp-standards` | `performance-and-algorithms.md` | `csharp-standards/references/performance-and-algorithms.md` |
| `.claude/skills/vfx-particle-authoring/references/vfx-graph-contexts.md:20` | `csharp-standards` | `performance-and-algorithms.md` | `csharp-standards/references/performance-and-algorithms.md` |
| `.claude/skills/zlinq-zero-allocation-linq/SKILL.md:9` | `csharp-standards` | `coding-principles.md` "`var` and LINQ" | `csharp-standards/references/coding-principles.md` heading ``var` and LINQ` |
| `.claude/skills/zlinq-zero-allocation-linq/SKILL.md:14` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/skills/zlinq-zero-allocation-linq/SKILL.md:21` | `zlinq-zero-allocation-linq` | step 4 | Remove capturing lambdas |
| `.claude/skills/zlinq-zero-allocation-linq/SKILL.md:21` | `zlinq-zero-allocation-linq` | step 5 | No `.ToArray()` / `.ToList()` in the hot path |
| `.claude/skills/zstring-zero-allocation-strings/SKILL.md:9` | `csharp-standards` | `coding-principles.md` | `csharp-standards/references/coding-principles.md` |
| `.claude/skills/zstring-zero-allocation-strings/SKILL.md:14` | `csharp-standards` | `performance-and-algorithms.md` "Verification" | `csharp-standards/references/performance-and-algorithms.md` heading `Verification` |
| `.claude/templates/framework-backlog.md:5` | `new-project` | step 5 | ## 5. Git — `git-expert` with skill `git-unity-repo`, before the Editor opens (or with it closed) |
| `.memory/notes/feedback/feature-workflow-git-and-checkpoints.md:3` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.memory/notes/feedback/feature-workflow-git-and-checkpoints.md:6` | `feature` | `` SKILL.md `` | exists at Base |
| `.memory/notes/feedback/feature-workflow-git-and-checkpoints.md:12` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.memory/notes/feedback/feature-workflow-git-and-checkpoints.md:13` | `feature` | step 4 | ## 4. Build — serial, one Editor holder at a time |
| `.memory/notes/feedback/framework-backlog-per-repo.md:6` | `new-project` | `` SKILL.md `` | exists at Base |
| `.claude/skills/verify-layer/scripts/verify.ps1:37` | `.claude/agents/code-reviewer.md` | `` Verdict: Approve \| Request changes `` | hook marker in `.claude/agents/code-reviewer.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:38` | `.claude/agents/security-reviewer.md` | `` Verdict: Clear \| Blocked `` | hook marker in `.claude/agents/security-reviewer.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:39` | `.claude/agents/qa-lead.md` | `` Verdict: Signed off \| Not signed off `` | hook marker in `.claude/agents/qa-lead.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:40` | `agent-protocol` | `` Status: Done \| Partial \| Blocked \| Needs-decision \| Failed `` | hook marker in `.claude/skills/agent-protocol/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:40` | `agent-protocol` | `` Repro: BUG-#### reproduces \| gone `` | hook marker in `.claude/skills/agent-protocol/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:40` | `agent-protocol` | `` `Verify: BUG-####` `` | hook marker in `.claude/skills/agent-protocol/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:42` | `review` | `` `Round: <n>` `` | hook marker in `.claude/skills/review/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:42` | `review` | `` `Mode: audit` `` | hook marker in `.claude/skills/review/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:42` | `review` | `` `Mode: workflow` `` | hook marker in `.claude/skills/review/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:42` | `review` | `` `Tree: <sha>` `` | hook marker in `.claude/skills/review/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:42` | `review` | `` `Previous tree: <sha>` `` | hook marker in `.claude/skills/review/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:42` | `review` | `` `Target: <path or base>` `` | hook marker in `.claude/skills/review/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:42` | `review` | `` `Bug: BUG-####` `` | hook marker in `.claude/skills/review/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:43` | `qa` | `` `Mode: test-code` `` | hook marker in `.claude/skills/qa/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:43` | `qa` | `` `Verify: BUG-####` `` | hook marker in `.claude/skills/qa/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:43` | `qa` | `` `Feature: .workflow/features/<slug>.md` `` | hook marker in `.claude/skills/qa/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:44` | `fix` | `` `Bug: BUG-####` `` | hook marker in `.claude/skills/fix/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:44` | `fix` | `` `Verify: BUG-####` `` | hook marker in `.claude/skills/fix/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:44` | `fix` | `` `Feature: .workflow/features/<slug>.md` `` | hook marker in `.claude/skills/fix/SKILL.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:45` | `feature` | `` - Status: Open `` | hook marker in `.claude/skills/feature/references/feature-template.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:45` | `feature` | `` - Size: `` | hook marker in `.claude/skills/feature/references/feature-template.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:45` | `feature` | `` - Rounds: `` | hook marker in `.claude/skills/feature/references/feature-template.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:45` | `feature` | `` ## GD decisions `` | hook marker in `.claude/skills/feature/references/feature-template.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:45` | `feature` | `` - Stop rule: `` | hook marker in `.claude/skills/feature/references/feature-template.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:46` | `fix` | `` - Fix rounds: `` | hook marker in `.claude/skills/fix/references/bugs-template.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:46` | `fix` | `` - Review rounds: `` | hook marker in `.claude/skills/fix/references/bugs-template.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:47` | `.claude/rules/routing.md` | `` extra round `` | hook marker in `.claude/rules/routing.md` |
| `.claude/skills/verify-layer/scripts/verify.ps1:49` | `.claude/workflows/review-gate.js` | `` lines.push('Mode: workflow') `` | hook marker in `.claude/workflows/review-gate.js` |
| `.claude/skills/verify-layer/scripts/verify.ps1:49` | `.claude/workflows/review-gate.js` | `` lines.push(`Round: ${round}`) `` | hook marker in `.claude/workflows/review-gate.js` |
| `.claude/skills/verify-layer/scripts/verify.ps1:49` | `.claude/workflows/review-gate.js` | `` lines.push(`Tree: ${scope.tree}`) `` | hook marker in `.claude/workflows/review-gate.js` |
| `.claude/skills/verify-layer/scripts/verify.ps1:50` | `.claude/workflows/project-audit.js` | `` const AUDIT = 'Mode: audit\n' `` | hook marker in `.claude/workflows/project-audit.js` |
| `.claude/skills/verify-layer/scripts/verify.ps1:50` | `.claude/workflows/project-audit.js` | `` `${AUDIT}Audit ${at(m.path)} `` | hook marker in `.claude/workflows/project-audit.js` |
| `.claude/skills/verify-layer/scripts/verify.ps1:50` | `.claude/workflows/project-audit.js` | `` `${AUDIT}Scan the repository `` | hook marker in `.claude/workflows/project-audit.js` |
| `.claude/skills/release/SKILL.md:29` | `release` | rows 9, 10, 11 (bare numbers) | gate rows: Store checklist, Signing, Secrets |
| `.claude/skills/release/SKILL.md:29` | `release` | row 0b | gate row: Unchecked work |
| `.claude/skills/dotween-tweening/references/coexistence-and-migration.md:19` | `litmotion-tweening` | `` `../../litmotion-tweening/references/migration-and-rx-integration.md` `` | exists at Base; a relative link out of the skill folder, found by a separate `../../` search |

## Searched and excluded

| File:line | Hit | Why not a row |
|---|---|---|
| `.claude/skills/mem/scripts/test_mem.py:1` | `.claude/skills/mem/scripts/test_mem.py` | test fixture or usage line, not a citation of the live skill |
| `.claude/skills/mem/scripts/test_mem.py:55` | `.claude/skills/fix/SKILL.md` | test fixture or usage line, not a citation of the live skill |
| `README.md:21` | `Step 0` | README section label, no skill |
