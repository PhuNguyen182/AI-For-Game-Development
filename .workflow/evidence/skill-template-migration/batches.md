# Batches

- **Base:** `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`.
- **Coverage:** 124 skills, each exactly once, checked by the generator. Domain 106; pipelines and named standards 18.
- **Grouping:** primary owning agent from `.claude/agents/*.md` `skills:` and `Skills (on demand)`, then citation links between skills.
- **Citation links:** 376 inside a batch, 219 across batches, counting a backticked skill name in another skill's `SKILL.md` or references, without `csharp-standards`, `agent-protocol`, `qa-standards`. A link across batches is safe: `anchors.md` freezes numbers and headings.
- **Order:** T3.1 to T3.7, then T4.1 and T4.2 last (spec). Writers are serial.

## Summary

| Batch | Theme | Owners | Skills | 15+ fences | Instruction "ask" hits | Skills keeping numbers |
|---|---|---|---|---|---|---|
| T3.1 | Git, delivery, security | git-expert, ci-cd-engineer, build-release-engineer, security-reviewer | 16 | 2 | 12 | 6 |
| T3.2 | Decisions and research | cto, researcher | 15 | 0 | 0 | 3 |
| T3.3 | C# Core and data | csharp-engineer, code-reviewer | 16 | 10 | 1 | 7 |
| T3.4 | Netcode, SDK and backend, QA and crash | netcode-engineer, sdk-platform-engineer, backend-engineer, qa-lead, qa-automation-engineer, playtest-tester, performance-qa-engineer, crash-anr-investigator | 16 | 9 | 3 | 10 |
| T3.5 | UI and client architecture | ui-engineer, gameplay-engineer | 14 | 3 | 4 | 6 |
| T3.6 | Gameplay | gameplay-engineer | 14 | 0 | 0 | 3 |
| T3.7 | Rendering and DOTS | technical-artist, unity-performance-engineer | 15 | 0 | 7 | 2 |
| T4.1 | Hook contract holders and gate methods | main session, all agents | 9 | 1 | 6 | 4 |
| T4.2 | Other pipelines | main session | 9 | 0 | 7 | 4 |

## Skill to batch

| Batch | Skill | Agents (`*` = preloaded) |
|---|---|---|
| T3.1 | `git-commit` | git-expert* |
| T3.1 | `git-forensics` | git-expert |
| T3.1 | `git-recovery` | git-expert |
| T3.1 | `git-safety-anchor` | git-expert* |
| T3.1 | `git-unity-repo` | build-release-engineer, ci-cd-engineer, git-expert |
| T3.1 | `ci-pipeline-failure-triage` | ci-cd-engineer |
| T3.1 | `jenkins-pipeline-authoring` | ci-cd-engineer |
| T3.1 | `fastlane-mobile-delivery` | ci-cd-engineer |
| T3.1 | `firebase-app-distribution` | ci-cd-engineer |
| T3.1 | `unity-batchmode-cli` | build-release-engineer, ci-cd-engineer, performance-qa-engineer, qa-automation-engineer, rd-engineer |
| T3.1 | `build-fault-triage` | build-release-engineer* |
| T3.1 | `device-test-walkthrough` | build-release-engineer |
| T3.1 | `secret-and-supply-chain-scan` | backend-engineer, build-release-engineer, sdk-platform-engineer, security-reviewer* |
| T3.1 | `secret-exposure-response` | cto |
| T3.1 | `code-search` | none: main session |
| T3.1 | `mem` | none: main session |
| T3.2 | `ad-mediation-monetization-platform` | cto |
| T3.2 | `analytics-telemetry-platform` | cto |
| T3.2 | `anti-cheat-strategy` | cto, netcode-engineer |
| T3.2 | `backend-build-vs-buy` | cto |
| T3.2 | `cross-platform-expansion-assessment` | cto |
| T3.2 | `engineering-standard-adr-authoring` | cto |
| T3.2 | `live-ops-content-pipeline` | backend-engineer, cto |
| T3.2 | `netcode-architecture-decision` | cto |
| T3.2 | `tco-reversibility-scoring` | cto* |
| T3.2 | `tech-vendor-dependency-risk-assessment` | cto |
| T3.2 | `design-precedent-sweep` | researcher |
| T3.2 | `practical-fit-screening` | researcher |
| T3.2 | `solution-comparison-report` | researcher |
| T3.2 | `source-credibility-grading` | researcher |
| T3.2 | `technology-scouting-sweep` | researcher |
| T3.3 | `core-determinism` | csharp-engineer, netcode-engineer, qa-automation-engineer |
| T3.3 | `core-scene-integration` | gameplay-engineer, netcode-engineer |
| T3.3 | `core-tests-without-unity` | csharp-engineer, qa-automation-engineer |
| T3.3 | `csvhelper-csv-data` | csharp-engineer |
| T3.3 | `dotnet-concurrency-and-async` | csharp-engineer, netcode-engineer |
| T3.3 | `dotnet-memory-and-collections` | csharp-engineer, unity-performance-engineer |
| T3.3 | `memorypack-serialization` | backend-engineer, csharp-engineer, gameplay-engineer, netcode-engineer, rd-engineer |
| T3.3 | `nrandom-random-generation` | csharp-engineer, qa-automation-engineer |
| T3.3 | `roslyn-analyzer-codefix` | csharp-engineer |
| T3.3 | `save-data-versioning-migration` | backend-engineer, csharp-engineer, qa-automation-engineer |
| T3.3 | `shared-core-boundary-audit` | code-reviewer |
| T3.3 | `source-generator-authoring` | csharp-engineer |
| T3.3 | `stateless-state-machines` | csharp-engineer, gameplay-engineer |
| T3.3 | `zlinq-zero-allocation-linq` | csharp-engineer, unity-performance-engineer |
| T3.3 | `zstring-zero-allocation-strings` | unity-performance-engineer |
| T3.3 | `feature-docs` | backend-engineer, code-reviewer, csharp-engineer, gameplay-engineer, netcode-engineer, sdk-platform-engineer, technical-artist, ui-engineer, unity-performance-engineer |
| T3.4 | `netcode-for-entities` | netcode-engineer, playtest-tester, qa-automation-engineer, rd-engineer |
| T3.4 | `netcode-for-gameobjects` | netcode-engineer, playtest-tester, qa-automation-engineer, rd-engineer |
| T3.4 | `unity-transport` | netcode-engineer, rd-engineer |
| T3.4 | `server-authoritative-validation` | netcode-engineer |
| T3.4 | `magiconion-rpc-networking` | backend-engineer, netcode-engineer |
| T3.4 | `consent-att-init-order` | sdk-platform-engineer |
| T3.4 | `firebase-unity-sdk` | backend-engineer, sdk-platform-engineer |
| T3.4 | `iap-server-receipt-ledger` | backend-engineer, sdk-platform-engineer |
| T3.4 | `crash-anr-reporting-gate` | crash-anr-investigator* |
| T3.4 | `crash-anr-symbolication` | crash-anr-investigator* |
| T3.4 | `crash-anr-fault-domain-triage` | crash-anr-investigator* |
| T3.4 | `risk-based-test-planning` | qa-automation-engineer, qa-lead* |
| T3.4 | `unity-test-framework` | build-release-engineer, ci-cd-engineer, csharp-engineer, gameplay-engineer, netcode-engineer, qa-automation-engineer*, ui-engineer |
| T3.4 | `playtest-scenario-execution` | gameplay-engineer, playtest-tester* |
| T3.4 | `performance-budget-verification` | performance-qa-engineer*, rd-engineer, unity-performance-engineer |
| T3.4 | `unity-profiler-diagnostics` | gameplay-engineer, performance-qa-engineer*, rd-engineer*, technical-artist, ui-engineer, unity-performance-engineer* |
| T3.5 | `ugui` | ui-engineer |
| T3.5 | `ui-toolkit` | ui-engineer |
| T3.5 | `mobile-safe-area` | ui-engineer |
| T3.5 | `flexalon-layouts` | ui-engineer |
| T3.5 | `osa-optimized-scrollview-adapter` | ui-engineer |
| T3.5 | `unity-localization-text` | ui-engineer |
| T3.5 | `litmotion-tweening` | gameplay-engineer, ui-engineer |
| T3.5 | `dotween-tweening` | gameplay-engineer, ui-engineer |
| T3.5 | `odin-inspector` | gameplay-engineer |
| T3.5 | `r3-reactive-extensions` | gameplay-engineer, ui-engineer |
| T3.5 | `unitask-async-programming` | backend-engineer, gameplay-engineer, sdk-platform-engineer, ui-engineer |
| T3.5 | `vcontainer-dependency-injection` | gameplay-engineer |
| T3.5 | `messagepipe-event-messaging` | gameplay-engineer |
| T3.5 | `unity-scriptableobject-architecture` | gameplay-engineer |
| T3.6 | `unity-input-system` | gameplay-engineer, playtest-tester, qa-automation-engineer, ui-engineer |
| T3.6 | `unity-3d-physics` | gameplay-engineer, unity-performance-engineer |
| T3.6 | `unity-2d-physics` | gameplay-engineer |
| T3.6 | `unity-animation` | gameplay-engineer |
| T3.6 | `unity-audio-mixer` | gameplay-engineer |
| T3.6 | `unity-camera-fundamentals` | gameplay-engineer |
| T3.6 | `unity-cinemachine-authoring` | gameplay-engineer |
| T3.6 | `unity-navmesh-navigation` | gameplay-engineer |
| T3.6 | `unity-2d-sprite` | gameplay-engineer |
| T3.6 | `unity-2d-spriteshape` | gameplay-engineer |
| T3.6 | `unity-tilemap` | gameplay-engineer |
| T3.6 | `unity-3d-mesh` | gameplay-engineer, technical-artist |
| T3.6 | `spine-animation` | gameplay-engineer |
| T3.6 | `unity-addressables` | gameplay-engineer, rd-engineer, unity-performance-engineer |
| T3.7 | `render-pipeline-urp-hdrp` | technical-artist, unity-performance-engineer |
| T3.7 | `unity-urp-rendering` | technical-artist, unity-performance-engineer |
| T3.7 | `unity-hdrp-rendering` | technical-artist, unity-performance-engineer |
| T3.7 | `shader-authoring` | technical-artist |
| T3.7 | `vfx-particle-authoring` | technical-artist |
| T3.7 | `compute-shader-vfx` | technical-artist |
| T3.7 | `unity-lighting` | technical-artist, unity-performance-engineer |
| T3.7 | `unity-post-processing` | technical-artist |
| T3.7 | `unity-burst-compiler` | rd-engineer, unity-performance-engineer |
| T3.7 | `unity-job-system-and-burst` | rd-engineer, unity-performance-engineer |
| T3.7 | `unity-collections` | unity-performance-engineer |
| T3.7 | `unity-ecs-architecture` | rd-engineer, unity-performance-engineer |
| T3.7 | `unity-entities-graphics` | unity-performance-engineer |
| T3.7 | `unity-mathematics` | unity-performance-engineer |
| T3.7 | `unity-physics` | unity-performance-engineer |
| T4.1 | `agent-protocol` | backend-engineer*, build-release-engineer*, ci-cd-engineer*, code-reviewer*, crash-anr-investigator*, critic*, csharp-engineer*, cto*, gameplay-engineer*, git-expert*, netcode-engineer*, performance-qa-engineer*, playtest-tester*, qa-automation-engineer*, qa-lead*, rd-engineer*, researcher*, sdk-platform-engineer*, security-reviewer*, technical-architect*, technical-artist*, ui-engineer*, unity-performance-engineer* |
| T4.1 | `feature` | none: main session |
| T4.1 | `fix` | none: main session |
| T4.1 | `qa` | none: main session |
| T4.1 | `review` | none: main session |
| T4.1 | `release` | none: main session |
| T4.1 | `qa-standards` | build-release-engineer*, code-reviewer*, performance-qa-engineer*, playtest-tester*, qa-automation-engineer*, qa-lead*, security-reviewer* |
| T4.1 | `code-review-method` | code-reviewer* |
| T4.1 | `csharp-standards` | backend-engineer*, code-reviewer*, csharp-engineer*, gameplay-engineer*, netcode-engineer*, qa-automation-engineer*, sdk-platform-engineer*, technical-architect*, technical-artist*, ui-engineer*, unity-performance-engineer* |
| T4.2 | `decide` | none: main session |
| T4.2 | `new-project` | none: main session |
| T4.2 | `plan-game` | none: main session |
| T4.2 | `plan-test-coverage` | none: main session |
| T4.2 | `investigate-device-crash` | none: main session |
| T4.2 | `resolve-merge-conflicts` | git-expert |
| T4.2 | `review-code-risks` | code-reviewer |
| T4.2 | `save-workmemory` | none: main session |
| T4.2 | `verify-layer` | none: main session |

## References with a 15+ line fenced block

25 blocks in 23 files, matching the spec. Line = the opening fence at Base.

| Batch | Reference | Line | Language | Lines | Target |
|---|---|---|---|---|---|
| T3.1 | `git-unity-repo/references/ignore-surface-and-lfs.md` | 54 | gitattributes | 38 | `unity.gitattributes` (spec trap) |
| T3.1 | `jenkins-pipeline-authoring/references/declarative-syntax-and-stages.md` | 7 | groovy | 22 | `Jenkinsfile` or .groovy |
| T3.3 | `core-determinism/references/float-and-fixed-point.md` | 28 | csharp | 24 | .cs |
| T3.3 | `core-determinism/references/replay-test.md` | 35 | csharp | 54 | .cs |
| T3.3 | `core-determinism/references/stable-hashing-and-ordering.md` | 22 | csharp | 42 | .cs |
| T3.3 | `core-scene-integration/references/input-and-physics-into-core.md` | 17 | csharp | 34 | .cs |
| T3.3 | `core-scene-integration/references/tick-and-interpolation.md` | 27 | csharp | 46 | .cs |
| T3.3 | `core-tests-without-unity/references/dotnet-test-mirror.md` | 26 | xml | 19 | .csproj or .xml, as the sample is |
| T3.3 | `core-tests-without-unity/references/dotnet-test-mirror.md` | 48 | xml | 22 | .csproj or .xml, as the sample is |
| T3.3 | `dotnet-concurrency-and-async/references/task-types-and-combinators.md` | 20 | csharp | 19 | .cs |
| T3.3 | `nrandom-random-generation/references/rng-algorithms-and-determinism.md` | 39 | csharp | 16 | .cs |
| T3.3 | `save-data-versioning-migration/references/version-envelope-and-chain.md` | 43 | csharp | 63 | .cs |
| T3.4 | `consent-att-init-order/references/google-ump.md` | 19 | csharp | 65 | .cs |
| T3.4 | `firebase-unity-sdk/references/setup-edm4u.md` | 51 | csharp | 27 | .cs |
| T3.4 | `iap-server-receipt-ledger/references/firebase-functions-firestore.md` | 29 | js | 61 | .js |
| T3.4 | `netcode-for-gameobjects/references/serialization.md` | 31 | csharp | 15 | .cs |
| T3.4 | `netcode-for-gameobjects/references/serialization.md` | 95 | csharp | 17 | .cs |
| T3.4 | `server-authoritative-validation/references/rate-limits-and-rejection.md` | 20 | csharp | 55 | .cs |
| T3.4 | `server-authoritative-validation/references/sender-identity-per-stack.md` | 22 | csharp | 23 | .cs |
| T3.4 | `unity-transport/references/core-driver-lifecycle.md` | 65 | csharp | 30 | .cs |
| T3.4 | `unity-transport/references/jobs-and-concurrent-api.md` | 24 | csharp | 22 | .cs |
| T3.5 | `flexalon-layouts/references/custom-layouts.md` | 19 | csharp | 20 | .cs |
| T3.5 | `litmotion-tweening/references/litmotion-animation-component.md` | 26 | csharp | 17 | .cs |
| T3.5 | `osa-optimized-scrollview-adapter/references/pooling-and-performance.md` | 24 | csharp | 23 | .cs |
| T4.1 | `csharp-standards/references/code-style-and-layout.md` | 8 | csharp | 15 | .cs |

- **No moved code:** T3.2, T3.6, T3.7, T4.2.

## Skills without `## Steps`

22 skills: pipeline 8, standard 3, method 4, gains Steps 7.

| Skill | Class | Reason |
|---|---|---|
| `agent-protocol` | standard | Rules every dispatched agent follows, under `On arrival` and `Return`; no single order. T4.1. |
| `code-review-method` | method | Review method under `Mode`, `Read the diff`, `Order`, `Bug checklist`; `Mode` is cited by `code-reviewer`. T4.1. |
| `code-search` | method | Two modes keyed by the session-start line (`XERJ up`, `XERJ down or absent`), not an ordered procedure. T3.1. |
| `csharp-standards` | standard | Detail behind rule `csharp.md`; the `Asset names` label and `Review` are the content, references hold the rest. T4.1. |
| `decide` | pipeline | `/decide` with numbered stage headings `## 1.` to `## 4.`. T4.2. |
| `feature` | pipeline | `/feature` with stage headings `## 0.` to `## 8.`; step 4, 5 and Lanes numbers are cited 25 times. T4.1. |
| `feature-docs` | method | `Read` and `Write` tables keyed by task; no single order. T3.3. |
| `fix` | pipeline | `/fix` with stage headings `## 1.` to `## 7.`, cited by number. T4.1. |
| `git-commit` | gains Steps | Domain skill with one linear procedure under `## Order`, a heading nobody cites; rename it `## Steps`, numbers 1 to 5 stay. T3.1. |
| `investigate-device-crash` | gains Steps | Pipeline, but its numbered list sits directly under the H1 with no heading; numbers 1 and 3 are cited, so they stay. T4.2. |
| `mem` | method | CLI reference under `Layers`, `Query`, `Write`; no single order. T3.1. |
| `new-project` | pipeline | `/new-project` with stage headings `## 1.` to `## 9.`, cited by number. T4.2. |
| `plan-game` | pipeline | `/plan-game` with stage headings `## 1.` to `## 5.` and `Re-plan`. T4.2. |
| `plan-test-coverage` | gains Steps | Pipeline, numbered list directly under the H1, no stage heading to keep. T4.2. |
| `qa` | pipeline | `/qa` with stage headings `## 1.` to `## 5.`, cited by number. T4.1. |
| `qa-standards` | standard | Claim, finding and bug rules; `A claim is verified only when` and `A finding has` are cited headings and stay. T4.1. |
| `release` | pipeline | `/release` gate table with `Store checklist` and `Finish`; the spec keeps the cited step table. T4.1. |
| `resolve-merge-conflicts` | gains Steps | Pipeline, numbered 1 to 12 directly under the H1; add `## Steps` above step 1, numbers stay (8 citations). T4.2. |
| `review` | pipeline | `/review` with stage headings `## 1.` to `## 5.`. T4.1. |
| `review-code-risks` | gains Steps | Pipeline, numbered list directly under the H1, no stage heading to keep. T4.2. |
| `save-workmemory` | gains Steps | Four lines of prose and no heading, and the untitled-item check rejects prose. T4.2. |
| `verify-layer` | gains Steps | No heading; prose plus a command fence becomes `Scripts` and `Steps`, the budget table stays as data. T5 also edits it (docs owed), so T4.2 keeps the table text. T4.2. |

## Traps for batch briefs

- **T3.1 `mem`, `device-test-walkthrough`:** the two hardcoded script paths; hooks keep their own `.claude/skills/mem/scripts/mem.py` paths (`anchors.md`).
- **T3.1 `git-unity-repo`:** the `.gitattributes` sample becomes `unity.gitattributes` (spec).
- **T3.2 `source-credibility-grading`:** `design-precedent-sweep` cites its `Precedent claims` label; the title keeps that exact text.
- **T3.4 `iap-server-receipt-ledger`:** one of the two bodies over 8,000 chars (8,746), and it is a domain skill, so T3.4 carries the fact move, not T4.
- **T3.4 `firebase-unity-sdk`:** body 7,831 chars; a `Missing input` step and titles can push it past 8,000.
- **T3.4 `consent-att-init-order`:** sub-steps (a) to (e) of step 3 are cited from `firebase-unity-sdk`, its own step 8 and the `google-ump.md` sample. A split keeps those letters in the nested titles.
- **T3.5 `dotween-tweening`:** `coexistence-and-migration.md:19` links `../../litmotion-tweening/references/migration-and-rx-integration.md`, out of its folder; the template wants `litmotion-tweening` in backticks plus the file name.
- **T4.1 `feature`:** the other body over 8,000 chars (12,677); `Lanes` numbers are cited separately from the stage numbers.
- **T4.1 `agent-protocol`:** a bullet titled `**Verified:**` or `**Known limitations:**` trips the envelope check; title the `Verified` rule differently. The fence and the three `$HookContracts` strings stay verbatim.
- **T4.1 `csharp-standards`:** `code-review-method` cites its `Asset names` label; the title keeps that exact text. The sample link stays reachable from `code-style-and-layout.md` (spec).
- **T4.2 `verify-layer`:** T5 also edits its table; keep T4.2 to format.
