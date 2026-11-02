# Comparator: batch T2, attempt 1

Base: `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`. Scope: all 124 skills, description lines and the 5 body lines.

**Verdict: fail.** 16 skills: 10 routing losses, 4 lost symbols, 7 rule violations (a skill may count under more than one check).

## Findings
| Skill | Check | Old text | New text | Why it fails | Replacement (chars) |
|---|---|---|---|---|---|
| decide | 1, 2, 3 | Make a technology decision: researcher sweeps sourced candidates, an optional rd-engineer spike measures the blocker, cto decides, an ADR records any standard. Use for vendors, packages, netcode/backend foundations, or what exists for X. | Technology decision: researcher sweep, rd spike, cto verdict, ADR. Use for vendors, packages, or what exists for X. | Step sequence (researcher, rd, cto, ADR). `netcode/backend` foundations is gone and neither word is anywhere in the folder, refuting the author's "lives in the cto flow"; "which netcode foundation?" now matches only `netcode-architecture-decision` and skips the pipeline. | Technology decision by cto on sourced candidates. Use for vendors, packages, netcode/backend, or what exists for X. (115) |
| qa | 1, 3 | QA a feature or existing work: qa-lead plans coverage, then automation, playtest, performance and device runs in order, bugs filed, qa-lead signs off. Use after review on M/L work, or when the GD asks for tests or evidence. | QA pipeline: qa-lead plan, automation, playtest, performance, device runs, sign-off. Use after review on M/L work. | Step sequence. "or when the GD asks for tests or evidence" is gone, while `routing.md` routes "Tests or evidence on existing work" here; the new trigger covers only post-review M/L work. | QA pipeline ending in qa-lead sign-off. Use after review on M/L work, or for tests or evidence on existing work. (112) |
| feature | 3 | Run an M/L feature from request to closure: size, CP1 (per profile), spec + CP2, a feature branch, serial build (optional lanes) with compile check and UTF tests per agent, optional review and QA, CP4. Also handles change requests and abandonment. | M/L feature pipeline: CP1, spec, CP2, feature branch, serial build, CP4, change requests. Use for any M/L feature. | Step sequence (CP1, spec, CP2, branch, build, CP4). | M/L feature pipeline, request to closure, with CP gates and change requests. Use for any M/L feature. (101) |
| fix | 3 | Fix a bug end to end: record it, reproduce, root-cause, fix with the owning agent, add a regression test that fails before and passes after, verify, update the bug. Use for any defect, from QA, the GD or production telemetry. | Bug fix pipeline: record, reproduce, root-cause, regression test, verify. Use for any defect. | Step sequence (record, reproduce, root-cause, test, verify). | Bug fix pipeline with a mandatory regression test. Use for any defect, from QA, the GD or production telemetry. (111) |
| review | 3 | Review a diff, feature or path: code-reviewer and security-reviewer in parallel, findings merged and sent back to the author until both clear. Use for every M/L or risk-flagged submission, or an audit of existing code. | Review pipeline: code-reviewer + security-reviewer in parallel, rework loop. Use for M/L or risk-flagged work, audits. | Ordered procedure: parallel reviewers, then the rework loop. | Review gate by code-reviewer and security-reviewer. Use for M/L or risk-flagged work, or audits of existing code. (113) |
| release | 3 | Prepare a release candidate per platform: version bump, builds, smoke test, perf on the profile's lowest device, build size, analytics/IAP sandbox check, save migration test, store checklist, signing, changelog — then ask before tag, push or submit. | Release candidate per platform: version bump, builds, smoke, perf, store checklist. Use when preparing a release. | Step sequence (bump, builds, smoke, perf, checklist), the gate table's own order. | Release candidate per platform: gate table, store checklist, signing. Use when preparing a release. (99) |
| new-project | 1 | Bootstrap a Unity project for this framework: CLAUDE.md, packages, the Shared feature's asmdefs and test assemblies, git + LFS, per-device-tier perf budget from the profile, .workflow/ state, optional CI. Use for a new or adopted project. | Bootstrap a Unity project: CLAUDE.md, packages, asmdefs, git + LFS, perf budget, .workflow/. Use for a new project. | "or adopted" is gone. The skill handles adopted projects (`SKILL.md:29`); "set the framework up on my existing project" is steered away by "a new project". | Bootstrap a Unity project: CLAUDE.md, asmdefs, git + LFS, perf budget, .workflow/. Use for a new or adopted project. (116) |
| unity-physics | 1 | Unity Physics (DOTS, deterministic): PhysicsCollider/Velocity/Mass, simulation groups, queries, collision filters, events, stateless stepping. Use for ECS physics. | Unity Physics (DOTS): PhysicsCollider, PhysicsVelocity, collision filters, events. Use for ECS physics. | "deterministic" is gone from the listing. It is what separates this skill from PhysX `unity-3d-physics` (`SKILL.md:22` opens with it); "deterministic physics" now reaches `core-determinism` or nothing. The description had 17 spare chars. | Unity Physics (DOTS, deterministic): PhysicsCollider, PhysicsVelocity, collision filters, events. Use for ECS physics. (118) |
| technology-scouting-sweep | 1 | Tiered search for a package, technique or service the project lacks: official docs, then maintained repos and the Asset Store, then forums, version-pinned, with a stop rule and query cap. Use for every research-mode question. | Tiered search: official docs, maintained repos, Asset Store, forums; stop rule, query cap. Use for research questions. | "research-mode" became "research questions" and the subject (package, technique or service the project lacks) is gone. An options-mode question is also a research question, so the boundary with `design-precedent-sweep` is lost; `research-mode` is absent from the folder. | Tiered search for a missing package or service: docs, repos, Asset Store, forums. Use for every research-mode question. (119) |
| design-precedent-sweep | 1 | Find how shipped games solved a design or architecture problem: shipping team's own account first, 2-4 distinct mechanisms, each with trade-off and assumptions, unranked. Use for every options-mode question. | How shipped games solved a design problem: 2-4 mechanisms, trade-offs, unranked. Use for every options-mode question. | "or architecture" is gone and the word is absent from the folder. The `researcher` options mode covers design or architecture problems; an architecture precedent question no longer matches. | How shipped games solved a design or architecture problem: 2-4 mechanisms, unranked. Use for any options-mode question. (119) |
| feature-docs | 1 | Which feature-root docs to read per task and in what order, and which to write at feature completion (README, CONTRACTS, INTEGRATION, ARCHITECTURE, DECISIONS, DEBT, NOTES). Use before changing, using, debugging or reviewing a feature. | Feature-root docs: README, CONTRACTS, INTEGRATION, ARCHITECTURE, DECISIONS, DEBT, NOTES. Use before changing a feature. | Trigger narrowed from "changing, using, debugging or reviewing" to "changing". The body has dedicated Debug and Review rows (`SKILL.md:26-27`) that the listing no longer reaches. | Feature-root docs: README, CONTRACTS, INTEGRATION, ARCHITECTURE, DECISIONS, DEBT, NOTES. Use before work on a feature. (118) |
| consent-att-init-order | 1 | Consent → ATT → SDK init order: UMP ConsentInformation.Update, LoadAndShowConsentFormIfRequired, CanRequestAds, privacy options, ATTrackingManager, PrivacyInfo.xcprivacy, AgeRestrictedTreatment. Use when ads or analytics must wait for consent. | UMP ConsentInformation, CanRequestAds, ATTrackingManager, PrivacyInfo.xcprivacy. Use when ads must wait for consent. | Scope narrowed from "ads or analytics" to "ads". The body orders analytics too (`SKILL.md:21-22`); "analytics must wait for consent" now points at `firebase-unity-sdk`, which this skill names as not owning the order. | UMP ConsentInformation, CanRequestAds, ATTrackingManager, PrivacyInfo.xcprivacy. Use when ads/analytics await consent. (118) |
| zlinq-zero-allocation-linq | 1, 2 | ZLinq allocation-free LINQ: AsValueEnumerable, struct operators, span sources, tree traversal. Use when LINQ readability is wanted in hot paths. | ZLinq: AsValueEnumerable, struct operators, span sources. Use when LINQ is wanted in hot paths. | "tree traversal" is gone and absent from the folder (one SKILL.md, no references), so it was not moved. The description had 25 spare chars. | ZLinq: AsValueEnumerable, struct operators, span sources, tree traversal. Use when LINQ is wanted in hot paths. (111) |
| backend-build-vs-buy | 1, 2 | Per-component build-vs-buy for backend: matchmaking, cloud save, server hosting, leaderboards, social — managed (UGS, PlayFab, Nakama, Firebase) vs custom, with exit cost. Use when choosing backend services. | Backend build-vs-buy: matchmaking, cloud save, hosting, leaderboards; UGS, PlayFab, Nakama. Use to choose backend. | `Firebase` is absent from the folder; the body shortlist never held it, so only the description named it as a managed backend. The token tool cannot see it (a plain capitalised word). "Firebase or custom backend?" now reaches `firebase-unity-sdk`, an integration skill. | Backend build-vs-buy: matchmaking, cloud save, hosting, leaderboards; UGS, PlayFab, Nakama, Firebase. Use to pick one. (118) |
| compute-shader-vfx | 2 | Compute shaders whose output is a visual: GPU particles, procedural mesh/vertex deformation, flow fields, buffers feeding Shader/VFX Graph — dispatch sizing, buffer lifetime, mobile limits. Use when a visual effect needs GPU simulation. | Compute shaders for visuals: GPU particles, mesh deformation, flow fields, buffers. Use when an effect needs GPU sim. | `Shader Graph` from "Shader/VFX Graph" is absent from the folder; only `VFX Graph` remains (`SKILL.md:35`). Refutes the author's "every part survives": the tool saw the compound, and `Shader` survives only as an unrelated substring. | Compute shaders for visuals: GPU particles, mesh deformation, flow fields, Shader/VFX Graph buffers. Use for GPU sim. (117) |
| unity-localization-text | 3 | Localization 1.5: String Tables, Smart Strings plurals, LocalizeStringEvent, LocalizedString, InitializationOperation, SelectedLocaleChanged, pseudo-locale Expander, TMP fallback per script. Use when player-facing text ships in several languages. | Localization 1.5: String Tables, Smart Strings, LocalizedString, pseudo-locale, TMP fallback. Use for multilingual text. | `multilingual`, named a typo by the brief (at best a rare word), replaced the requester's words; "languages" is absent from the folder. Replacement keeps `pseudo-locale` in the body only (still there). | Localization 1.5: String Tables, Smart Strings, LocalizedString, TMP fallback. Use when text ships in several languages. (120) |

## Passed
- **Check 3, mechanical:** 124 double-quoted, 0 over 120 chars, 0 banned phrases. Whole-layer `verify.ps1` exit 0, `verify-layer: OK (21 warning(s))`, no description warning.
- **Check 3, no `Use`:** `agent-protocol`, `code-review-method` only; both preloaded, which `verify.ps1:76-80` exempts.
- **Check 3, name repeated:** 17 descriptions open with their folder name as the package or topic; the template (`skill-template.md:66`) puts the package first, so no rule breaks.
- **Check 4:** 5 body lines, each an insertion only, each correct: `ad-mediation-monetization-platform` step 3, `netcode-architecture-decision` step 3, `netcode-for-entities` Docs, `ui-toolkit` Docs, `unity-animation` Docs. `git diff --numstat`: 118 files 1/1, 5 files 2/2. Other 119 bodies identical to Base.
- **Check 5:** frontmatter keys other than `description` unchanged in all 124. No tracked non-SKILL file changed by T2. `verify-layer/SKILL.md` unchanged, already compliant.
- **Author's table:** `descriptions.md` matches all 124 descriptions and char counts.
- **Line endings:** 107 files are `w/mixed` (description line LF in a CRLF checkout), `i/lf`, `core.autocrlf=true`: no diff beyond the line, no finding.

## Neighbour groups read, no finding
- **`crash-anr-*` / `investigate-device-crash`:** "production" dropped from all three, but the three are preloaded and "Device", "test device" still mark the neighbour.
- **Burst group, `ugui` / `ui-toolkit`, tweening, `review-code-risks` / `code-review-method`, `git-*`:** scope words kept. `git-safety-anchor` dropped `merge`, `checkout`, `branch -D` from its list; preloaded, and the body holds them.
- **`unity-2d-physics`, `unity-3d-physics`:** "on GameObjects" gone; `Rigidbody2D`, `PhysX`, and `unity-physics` "ECS" still separate them.
- **Netcode:** `Fusion/Quantum` still reads as Photon; `Photon` is in the body.

## Description-only clauses traced to the body
- **`source-generator-authoring` "3+ types":** body step 1, "one or two call sites never justify it".
- **`solution-comparison-report` "staleness trigger":** Output `Picture taken: ... restate if`.
- **`code-search` "XERJ is up":** `SKILL.md:9`.
- **`resolve-merge-conflicts`:** steps 4-5, Big and Small.

## Lost symbols: 83 from the description, re-run of `token-survival.ps1` reports 83
| Skill | Token | Disposition |
|---|---|---|
| ad-mediation-monetization-platform | `fill/eCPM` | kept: step 3 |
| anti-cheat-strategy | `Deck/console` | every part in the folder |
| build-fault-triage | `logs/logcat` | cut `logs`, Common knowledge, no number, version or gotcha; `logcat` kept |
| ci-pipeline-failure-triage | `agent/workspace` | every part in the folder |
| ci-pipeline-failure-triage | `Library/package` | every part in the folder |
| compute-shader-vfx | `mesh/vertex` | every part in the folder |
| compute-shader-vfx | `Shader/VFX` | FINDING, see table |
| consent-att-init-order | `LoadAndShowConsentFormIfRequired` | every part in the folder |
| core-determinism | `MathF/Math` | every part in the folder |
| core-determinism | `IL2CPP/Mono` | every part in the folder |
| core-determinism | `Dictionary/HashSet` | every part in the folder |
| crash-anr-reporting-gate | `crash/ANR` | every part in the folder |
| crash-anr-symbolication | `crash/ANR` | every part in the folder |
| csvhelper-csv-data | `GetRecords/WriteRecords` | every part in the folder |
| decide | `netcode/backend` | FINDING, see table |
| device-test-walkthrough | `tap/swipe/type` | every part in the folder |
| dotnet-concurrency-and-async | `async/await` | every part in the folder |
| dotnet-concurrency-and-async | `Parallel.ForEach` | kept: `Parallel.For`/`ForEach` at `SKILL.md:24` |
| dotween-tweening | `DOMove/DOFade` | every part in the folder |
| dotween-tweening | `Append/Join/Insert` | every part in the folder |
| dotween-tweening | `SetEase/SetLoops/SetUpdate` | every part in the folder |
| firebase-unity-sdk | `SetConsent/SetAnalyticsCollectionEnabled` | every part in the folder |
| firebase-unity-sdk | `SetDefaultsAsync/FetchAndActivateAsync` | every part in the folder |
| flexalon-layouts | `Cloner/DataSource` | every part in the folder |
| flexalon-layouts | `Interactable/DragTarget` | every part in the folder |
| git-recovery | `rebase/merge/cherry` | every part in the folder |
| git-unity-repo | `scene/prefab` | every part in the folder |
| iap-server-receipt-ledger | `get/consume/acknowledge` | every part in the folder |
| investigate-device-crash | `Android/iOS` | every part in the folder |
| jenkins-pipeline-authoring | `junit/NUnit` | every part in the folder |
| litmotion-tweening | `Bind/BindTo` | every part in the folder |
| messagepipe-event-messaging | `keyed/keyless` | every part in the folder |
| messagepipe-event-messaging | `request/response` | every part in the folder |
| netcode-architecture-decision | `Transport/LiteNetLib` | moved: `SKILL.md` step 3, `Unity Transport, LiteNetLib` |
| netcode-for-entities | `ICommandData/IInputComponentData` | every part in the folder |
| netcode-for-gameobjects | `NetworkObject/Behaviour/Manager` | every part in the folder |
| odin-inspector | `conditional/grouping/button` | every part in the folder |
| osa-optimized-scrollview-adapter | `list/grid/table` | every part in the folder |
| osa-optimized-scrollview-adapter | `ResetItems/InsertItems` | every part in the folder |
| performance-budget-verification | `GC/frame` | every part in the folder |
| release | `analytics/IAP` | kept: `Analytics + IAP` gate row 7 |
| roslyn-analyzer-codefix | `Core/UnityEngine` | every part in the folder |
| shared-core-boundary-audit | `UnityEngine/asmdef` | every part in the folder |
| source-generator-authoring | `equality/hashing` | cut `hashing`, Common knowledge, no number, version or gotcha; `equality` kept |
| spine-animation | `SkeletonAnimation/SkeletonGraphic/SkeletonMecanim` | every part in the folder |
| spine-animation | `SetSkin/SetupPoseSlots` | every part in the folder |
| stateless-state-machines | `entry/exit` | every part in the folder |
| ui-toolkit | `Renderer/UIDocument` | every part in the folder |
| unity-2d-physics | `GameObjects` | kept: singular `GameObject` in the folder |
| unity-3d-mesh | `SetVertices/SetIndices` | every part in the folder |
| unity-3d-mesh | `MeshFilter/MeshRenderer` | every part in the folder |
| unity-3d-physics | `fixedDeltaTime` | every part in the folder |
| unity-3d-physics | `GameObjects` | kept: singular `GameObject` in the folder |
| unity-addressables | `LoadAssetAsync/InstantiateAsync/LoadSceneAsync` | every part in the folder |
| unity-addressables | `Release/ReleaseInstance` | every part in the folder |
| unity-addressables | `groups/labels` | every part in the folder |
| unity-batchmode-cli | `BuildPipeline.BuildPlayer/BuildReport` | every part in the folder |
| unity-burst-compiler | `FloatMode/CompileSynchronously` | every part in the folder |
| unity-camera-fundamentals | `FOV/orthographicSize` | every part in the folder |
| unity-camera-fundamentals | `follow/shake` | every part in the folder |
| unity-cinemachine-authoring | `Follow/OrbitalFollow/PositionComposer` | every part in the folder |
| unity-cinemachine-authoring | `Confiner2D/3D` | every part in the folder |
| unity-cinemachine-authoring | `TargetGroup` | every part in the folder |
| unity-cinemachine-authoring | `StateDriven/ClearShot` | every part in the folder |
| unity-collections | `NativeArray/List/HashMap/Queue/Stream` | every part in the folder |
| unity-collections | `Temp/TempJob/Persistent/rewindable` | every part in the folder |
| unity-collections | `FixedString/FixedList` | every part in the folder |
| unity-hdrp-rendering | `ray/path` | every part in the folder |
| unity-input-system | `PlayerInput/PlayerInputManager` | every part in the folder |
| unity-job-system-and-burst | `IJob/IJobFor/ScheduleParallel` | every part in the folder |
| unity-mathematics | `float3/float4x4` | every part in the folder |
| unity-mathematics | `Vector3/Mathf/Random` | every part in the folder |
| unity-navmesh-navigation | `NavMeshSurface/Modifier` | every part in the folder |
| unity-physics | `PhysicsCollider/Velocity/Mass` | every part in the folder |
| unity-post-processing | `Volume/VolumeProfile/VolumeComponent` | every part in the folder |
| unity-profiler-diagnostics | `ProfilerMarker/ProfilerRecorder` | every part in the folder |
| unity-scriptableobject-architecture | `Variable/Reference` | every part in the folder |
| unity-test-framework | `Edit/Play` | every part in the folder |
| unity-tilemap | `Rule/Auto/Animated` | every part in the folder |
| unity-urp-rendering | `ScriptableRendererFeature/RenderPass` | every part in the folder |
| unity-urp-rendering | `Forward/Forward` | every part in the folder |
| vfx-particle-authoring | `blend/sorting` | every part in the folder |
| zstring-zero-allocation-strings | `TextMeshPro` | kept: `TextMeshProExtensions` at `SKILL.md:12`; `TMP` in the description |

## Not verified
- Routing findings are judged by reading the listing text; no prompt was run against a real listing.
