# Descriptions

| skill | old chars | new chars | new description |
|---|---|---|---|
| ad-mediation-monetization-platform | 230 | 119 | Ad mediation vendor (MAX, ironSource, AdMob), managed vs custom ledger. Use when choosing mediation or economy backend. |
| agent-protocol | 113 | 113 | Return envelope (Status/Summary/Changed/Verified/…), Implementation Note, on-arrival rules for dispatched agents. |
| analytics-telemetry-platform | 206 | 106 | Analytics build-vs-buy: Firebase, BigQuery export, custom pipeline. Use when choosing the analytics stack. |
| anti-cheat-strategy | 244 | 115 | Anti-cheat posture: server authority, detection, anti-tamper, EAC/BattlEye. Use when sizing anti-cheat or exploits. |
| backend-build-vs-buy | 207 | 114 | Backend build-vs-buy: matchmaking, cloud save, hosting, leaderboards; UGS, PlayFab, Nakama. Use to choose backend. |
| build-fault-triage | 225 | 115 | Player-build-only faults: IL2CPP/AOT, link.xml stripping, ABI, logcat. Use when a build fails but the Editor works. |
| ci-pipeline-failure-triage | 210 | 107 | Red Unity CI run triage: licence, editor version, Library damage, flakes, signing. Use when a CI run fails. |
| code-review-method | 179 | 99 | How code-reviewer reviews a diff: spec mapping, bug checklist, severity, verdict, re-review rounds. |
| code-search | 187 | 108 | `xerj search`, `xerj def` BM25 passages instead of repo-wide Grep. Use before any search across the project. |
| compute-shader-vfx | 236 | 117 | Compute shaders for visuals: GPU particles, mesh deformation, flow fields, buffers. Use when an effect needs GPU sim. |
| consent-att-init-order | 243 | 116 | UMP ConsentInformation, CanRequestAds, ATTrackingManager, PrivacyInfo.xcprivacy. Use when ads must wait for consent. |
| core-determinism | 238 | 120 | Core determinism: fixed-point, MathF drift, GetHashCode, Dictionary order. Use when Core must reproduce across machines. |
| core-scene-integration | 241 | 117 | Core-to-scene wiring: one tick owner, IFixedTickable, per-tick input, read-only views. Use to hook Core into a scene. |
| core-tests-without-unity | 240 | 116 | noEngineReferences, Tests/EditMode, dotnet test mirror, LangVersion 9.0. Use when Core tests run outside the Editor. |
| crash-anr-fault-domain-triage | 219 | 117 | Crash/ANR fault domain: game, engine, SDK or system library; routes the fix. Use as stage 3 of a crash investigation. |
| crash-anr-reporting-gate | 213 | 120 | Crash/ANR reporting service check: Play vitals, Crashlytics, App Store Connect. Use as stage 1 of a crash investigation. |
| crash-anr-symbolication | 212 | 112 | Crash/ANR symbolication: IL2CPP symbols, mapping, dSYM, build id match. Use as stage 2 of a crash investigation. |
| cross-platform-expansion-assessment | 214 | 114 | Cost, timeline, risk of a new platform: console SKU, Steam Deck, cross-play. Use before committing a new platform. |
| csharp-standards | 206 | 119 | Detail behind rule `csharp.md`: Core boundary, naming, fake-null, hot-path, Jobs/Burst. Use when the rule leaves a gap. |
| csvhelper-csv-data | 201 | 117 | CsvHelper: CsvReader/CsvWriter, GetRecords, ClassMap, converters, IL2CPP. Use when config or balance data is CSV/TSV. |
| decide | 237 | 115 | Technology decision: researcher sweep, rd spike, cto verdict, ADR. Use for vendors, packages, or what exists for X. |
| design-precedent-sweep | 207 | 117 | How shipped games solved a design problem: 2-4 mechanisms, trade-offs, unranked. Use for every options-mode question. |
| device-test-walkthrough | 213 | 115 | Test cases on a real Android/iOS device: install, input, screenshot, logcat. Use when cases need a physical device. |
| dotnet-concurrency-and-async | 249 | 114 | .NET Task, ValueTask, CancellationToken, Channel<T>, SemaphoreSlim, Interlocked. Use for async outside PlayerLoop. |
| dotnet-memory-and-collections | 193 | 113 | Span, Memory, ArrayPool, stackalloc, immutable collections, collection choice. Use when per-frame code allocates. |
| dotween-tweening | 229 | 119 | DOTween: DOTween.To, DOMove, Sequence, SetEase, OnKill, KillAll, SetRecyclable, DOPath. Use for code tweens on DOTween. |
| engineering-standard-adr-authoring | 200 | 116 | Lightweight ADR for a CTO engineering standard: status, scope, supersession. Use when a decision becomes a standard. |
| fastlane-mobile-delivery | 199 | 115 | Fastlane: Fastfile lanes, gradle APK/AAB, gym, match, CI keychain. Use when automating mobile packaging or signing. |
| feature | 247 | 114 | M/L feature pipeline: CP1, spec, CP2, feature branch, serial build, CP4, change requests. Use for any M/L feature. |
| feature-docs | 234 | 119 | Feature-root docs: README, CONTRACTS, INTEGRATION, ARCHITECTURE, DECISIONS, DEBT, NOTES. Use before changing a feature. |
| firebase-app-distribution | 234 | 119 | `appdistribution:distribute`, `firebase_app_distribution`, groups, UDIDs. Use when shipping builds to internal testers. |
| firebase-unity-sdk | 243 | 119 | Firebase Unity SDK: EDM, google-services.json, Remote Config, Crashlytics, Auth, SetConsent. Use to integrate Firebase. |
| fix | 225 | 93 | Bug fix pipeline: record, reproduce, root-cause, regression test, verify. Use for any defect. |
| flexalon-layouts | 240 | 118 | Flexalon: FlexalonObject, Flexible/Grid/Circle/Curve layouts, Constraint, Cloner, MarkDirty. Use for Flexalon layouts. |
| git-commit | 163 | 98 | Commit message: English imperative subject, why-body, one change per commit. Use for every commit. |
| git-forensics | 203 | 118 | Blame with ignore-revs, log -L, pickaxe -S/-G, bisect run, secret in history. Use when attributing a defect or a leak. |
| git-recovery | 196 | 119 | Recover lost commits, stuck rebase/merge, force-push overwrite, reflog, fsck. Use when work looks lost or git is stuck. |
| git-safety-anchor | 245 | 114 | Blast radius, backup/<op>-<utc> tag, stash create, undo. Use before reset, rebase, force-push, filter-repo, clean. |
| git-unity-repo | 207 | 106 | UnityYAMLMerge, .meta/GUID integrity, Git LFS, .gitattributes. Use for Unity git setup or asset conflicts. |
| iap-server-receipt-ledger | 249 | 114 | Server IAP grants: Play purchases.products, App Store transactions, REFUND, ledger. Use when crediting a purchase. |
| investigate-device-crash | 149 | 110 | Device crash/ANR via adb logcat, idevicecrashreport: fault domain, root cause. Use when a test device crashes. |
| jenkins-pipeline-authoring | 194 | 116 | Declarative Jenkinsfile: agent labels, withCredentials, lock, stash, NUnit reports, input. Use to author Jenkins CI. |
| litmotion-tweening | 245 | 114 | LitMotion: LMotion.Create, MotionHandle, Bind, LSequence, IMotionAdapter. Use for code-driven tweens on LitMotion. |
| live-ops-content-pipeline | 217 | 119 | Remote config for live tuning: Firebase/Unity Remote Config, PlayFab Title Data, rollback. Use to plan live-ops tuning. |
| magiconion-rpc-networking | 202 | 112 | MagicOnion client: gRPC services, StreamingHub, YetAnotherHttpHandler, heartbeats. Use with a MagicOnion server. |
| mem | 221 | 107 | Zero-Mem CLI: query sessions (T), notes (M), docs (K); save lessons. Use before work in an unfamiliar area. |
| memorypack-serialization | 232 | 120 | MemoryPack: [MemoryPackable], MemoryPackOrder, MemoryPackUnion, version-tolerant, IL2CPP. Use for compact serialization. |
| messagepipe-event-messaging | 201 | 113 | MessagePipe: keyed publishers/subscribers, async handlers, filters, VContainer. Use when features talk decoupled. |
| mobile-safe-area | 245 | 113 | Screen.safeArea, cutouts, uGUI Safe Area, RuntimePanelUtils.ScreenToPanel. Use when mobile UI must clear notches. |
| netcode-architecture-decision | 195 | 112 | Multiplayer foundation (Mirror, FishNet, Fusion/Quantum, NGO) and sync model. Use before any netcode is written. |
| netcode-for-entities | 207 | 114 | Netcode for Entities: ghosts, GhostField, IRpcCommand, ICommandData, ClientServerBootstrap. Use on an NfE project. |
| netcode-for-gameobjects | 193 | 112 | NGO: NetworkObject, NetworkBehaviour, NetworkVariable, RPCs, ownership, NetworkTransform. Use on an NGO project. |
| new-project | 238 | 115 | Bootstrap a Unity project: CLAUDE.md, packages, asmdefs, git + LFS, perf budget, .workflow/. Use for a new project. |
| nrandom-random-generation | 197 | 119 | NRandom: IRandom, Xoshiro/PCG, RandomEx, weighted selection, shuffle. Use for reproducible randomness in Core or tests. |
| odin-inspector | 182 | 117 | Odin Inspector: attributes, validation, SerializedMonoBehaviour, custom drawers. Use for Inspector tooling with Odin. |
| osa-optimized-scrollview-adapter | 240 | 102 | OSA<TParams,TItemViewsHolder>, ResetItems, GridAdapter, ScrollTo, Snapper8. Use for long scroll lists. |
| performance-budget-verification | 208 | 117 | Profiler numbers to pass/fail per device tier: frame-time, GC, memory, draw calls. Use when a number needs a verdict. |
| plan-game | 236 | 112 | GDD to production backlog: milestones, S/M/L features, risk flags, .workflow/backlog.md. Use to plan production. |
| plan-test-coverage | 171 | 111 | Test case list (normal + edge), manual flow, impact analysis from a spec; report only. Use when planning tests. |
| playtest-scenario-execution | 203 | 117 | GDD scenario in one Play Mode session: checkpoints, screenshots, console, design flaw. Use for hand-played scenarios. |
| practical-fit-screening | 238 | 116 | Hard-gate a candidate: duplication, C# version, backend, platforms, licence. Use before ranking research candidates. |
| qa | 223 | 114 | QA pipeline: qa-lead plan, automation, playtest, performance, device runs, sign-off. Use after review on M/L work. |
| qa-standards | 151 | 106 | QA verified claims, finding format, severity scale, bug lifecycle. Use when filing or judging QA findings. |
| r3-reactive-extensions | 182 | 116 | R3: Observable, Subject, ReactiveProperty, frame providers, AddTo. Use for event streams; one-shot async is UniTask. |
| release | 249 | 113 | Release candidate per platform: version bump, builds, smoke, perf, store checklist. Use when preparing a release. |
| render-pipeline-urp-hdrp | 175 | 112 | Active render pipeline (URP, HDRP, Built-in) per quality level. Use first in any rendering, shader or post task. |
| resolve-merge-conflicts | 240 | 112 | Merge, rebase, cherry-pick, stash conflicts in C#, Unity YAML, Addressables. Use when a conflict is in progress. |
| review | 218 | 118 | Review pipeline: code-reviewer + security-reviewer in parallel, rework loop. Use for M/L or risk-flagged work, audits. |
| review-code-risks | 139 | 117 | Static C#/Unity review for performance, memory, crash/ANR risk; report only. Use when auditing code for runtime risk. |
| risk-based-test-planning | 218 | 108 | Equivalence partitions, boundaries, decision tables, state transitions, risk ranking. Use to scope QA cases. |
| roslyn-analyzer-codefix | 209 | 118 | Roslyn analyzers and code fixes enforcing rules: Core boundary, determinism, banned APIs. Use when a violation recurs. |
| save-data-versioning-migration | 244 | 120 | Save header (magic, SHA-256), SaveVN DTOs, vN→vN+1 chain, File.Replace, golden fixtures. Use when a save format changes. |
| save-workmemory | 114 | 88 | Summarize the session into WORKMEMORY.md at the feature root. Use when ending a session. |
| secret-and-supply-chain-scan | 226 | 117 | Secrets (keys, keystores, .env) and supply-chain risk (InitializeOnLoad, DLLs). Use before commit, import or release. |
| secret-exposure-response | 222 | 116 | Secret or PII in git history: rotate-then-verify, owner per credential, purge decision. Use when a leak reaches cto. |
| server-authoritative-validation | 241 | 118 | Server checks on client RPCs: SenderClientId, SourceConnection, ConnectionId, rate limit. Use when server takes input. |
| shader-authoring | 186 | 105 | Shader Graph and HLSL/ShaderLab: toon, outline, dissolve, keywords, SRP Batcher. Use for any shader work. |
| shared-core-boundary-audit | 220 | 118 | Core vs Client audit: UnityEngine leaks, Random/Time/DateTime, rules in MonoBehaviours. Use when reviewing boundaries. |
| solution-comparison-report | 216 | 120 | Dated sourced recommendation: fixed axes, deciding axis, runner-up flip condition. Use to close research-mode questions. |
| source-credibility-grading | 227 | 116 | Grade sources T1 docs to T4 unverified, date claims, resolve by tier. Use before any claim enters a research report. |
| source-generator-authoring | 222 | 119 | IIncrementalGenerator for Core boilerplate: codecs, equality, registries; netstandard2.0. Use when boilerplate repeats. |
| spine-animation | 227 | 114 | spine-unity: SkeletonAnimation, SkeletonGraphic, AnimationState, BoneFollower, PMA. Use on Spine characters or UI. |
| stateless-state-machines | 201 | 114 | Stateless: Configure/Permit/PermitIf, guards, substates, DOT export. Use when behaviour is states and transitions. |
| tco-reversibility-scoring | 216 | 114 | CTO rubric: TCO (upfront, ongoing, scaling, exit) and Low/Medium/High reversibility. Use for strategic tech calls. |
| tech-vendor-dependency-risk-assessment | 209 | 113 | Dependency safety: maintenance, cadence, licence, lock-in, exit path. Use when a dependency's future is in doubt. |
| technology-scouting-sweep | 225 | 118 | Tiered search: official docs, maintained repos, Asset Store, forums; stop rule, query cap. Use for research questions. |
| ugui | 215 | 114 | uGUI and TextMeshPro: Canvas, CanvasScaler, RectTransform, Layout Groups, RectMask2D, TMP_Text. Use for Canvas UI. |
| ui-toolkit | 240 | 116 | UI Toolkit: UXML, USS, UxmlElement, ListView, PanelSettings, UIDocument, CreateGUI. Use for UI Toolkit or Editor UI. |
| unitask-async-programming | 196 | 120 | UniTask/UniTaskVoid, PlayerLoop timing, destroy cancellation, Forget. Use for one-shot async in Client code, never Core. |
| unity-2d-physics | 208 | 107 | Box2D: Rigidbody2D, Collider2D, CompositeCollider2D, Effector2D, Joint2D, layer matrix. Use for 2D physics. |
| unity-2d-sprite | 206 | 116 | Sprites: Pixels Per Unit, Mesh Type, slicing, SpriteMask, SortingGroup, Sprite Atlas, 9-slice. Use for sprite setup. |
| unity-2d-spriteshape | 150 | 112 | SpriteShapeController, profiles, corners, fill, colliders, runtime spline edits. Use for spline-built 2D levels. |
| unity-3d-mesh | 221 | 118 | Procedural meshes: Mesh API, SetVertices, MeshData, 32-bit indices, CombineMeshes. Use when generating meshes in code. |
| unity-3d-physics | 216 | 107 | PhysX: Rigidbody, CharacterController, joints, ArticulationBody, Cloth, NonAlloc casts. Use for 3D physics. |
| unity-addressables | 249 | 119 | Addressables 4.0: AssetReference, LoadAssetAsync, Release ref counting, remote catalogs. Use for asset delivery, leaks. |
| unity-animation | 245 | 119 | Mecanim: Animator, Blend Tree, Humanoid Avatar, AvatarMask, root motion, PlayableGraph. Use for clips, Animator graphs. |
| unity-audio-mixer | 239 | 110 | AudioSource, AudioMixer groups, snapshots, SetFloat, clip import, Duck Volume. Use for audio setup and mixing. |
| unity-batchmode-cli | 230 | 112 | -batchmode -executeMethod, BuildPipeline.BuildPlayer, -returnlicense, Hub CLI. Use when Unity CLI cannot run it. |
| unity-burst-compiler | 223 | 120 | Burst itself: HPC# limits, [BurstCompile] FloatMode, FunctionPointer, [NoAlias]. Use when Burst output or settings fail. |
| unity-camera-fundamentals | 207 | 119 | Native Camera: FOV, orthographicSize, Gate Fit, cullingMask, viewport, ScreenToWorldPoint. Use for non-Cinemachine cam. |
| unity-cinemachine-authoring | 227 | 120 | Cinemachine 3: CinemachineBrain, CinemachineCamera, OrbitalFollow, Confiner, Impulse. Use for authored camera behaviour. |
| unity-collections | 228 | 118 | Unity.Collections: NativeArray/List/HashMap, allocators, Dispose, FixedString, ParallelWriter. Use for Job/Burst data. |
| unity-ecs-architecture | 214 | 113 | Entities/ECS 6.6: IComponentData, Baker<T>, ISystem, SystemAPI.Query, IJobEntity, ECB. Use when writing ECS code. |
| unity-entities-graphics | 170 | 114 | Entities Graphics: BatchRendererGroup, RenderMeshArray, MaterialMeshInfo, LODs. Use when ECS entities must render. |
| unity-hdrp-rendering | 230 | 113 | HDRP: Frame Settings, HDAdditionalCameraData, Volumes, CustomPassVolume, ray tracing. Use once HDRP is confirmed. |
| unity-input-system | 216 | 111 | Input System: .inputactions, Interactions, Processors, PlayerInput, rebinding, touch. Use for any player input. |
| unity-job-system-and-burst | 222 | 120 | Worker-thread jobs: IJob/IJobFor, ScheduleParallel, JobHandle, [BurstCompile] jobs. Use after profiling shows CPU bound. |
| unity-lighting | 188 | 115 | Built-in/URP lighting: baked/mixed/realtime GI, Light Probes, Reflection Probes, cascades. Use for lighting, bakes. |
| unity-localization-text | 246 | 120 | Localization 1.5: String Tables, Smart Strings, LocalizedString, pseudo-locale, TMP fallback. Use for multilingual text. |
| unity-mathematics | 179 | 116 | Unity.Mathematics: float3, quaternion, math, noise, Random. Use for Core, Burst, jobs and ECS math instead of Mathf. |
| unity-navmesh-navigation | 206 | 114 | AI Navigation 2.0: NavMeshSurface, NavMeshAgent, NavMeshObstacle, NavMeshLink, area costs. Use for AI pathfinding. |
| unity-physics | 163 | 103 | Unity Physics (DOTS): PhysicsCollider, PhysicsVelocity, collision filters, events. Use for ECS physics. |
| unity-post-processing | 211 | 111 | URP Volume overrides (Bloom, Tonemapping, DoF), FullScreenPassRendererFeature, PPv2. Use for full-screen looks. |
| unity-profiler-diagnostics | 244 | 117 | Profiler CPU/GPU/Memory, GC Alloc, Frame Debugger, Memory Profiler, ProfilerMarker. Use when a perf number is needed. |
| unity-scriptableobject-architecture | 237 | 120 | ScriptableObject architecture: Variable SOs, GameEvent, EventChannelSO, RuntimeSetSO. Use for designer-wired decoupling. |
| unity-test-framework | 221 | 112 | Unity Test Framework 2.0: UnityTest, UnitySetUp, LogAssert, -runTests, TestRunnerApi. Use to write or run tests. |
| unity-tilemap | 213 | 114 | Tilemaps: Grid layouts, Tile Palette, Rule Tile, TilemapRenderer, TilemapCollider2D. Use for tile-based 2D levels. |
| unity-transport | 245 | 114 | Unity Transport 6.6: NetworkDriver, NetworkConnection, NetworkPipeline, Relay, DTLS. Use for low-level networking. |
| unity-urp-rendering | 213 | 112 | URP: ScriptableRendererFeature, Render Graph, Forward+, URP Asset tiers, SRP Batcher. Use once URP is confirmed. |
| vcontainer-dependency-injection | 216 | 113 | VContainer: LifetimeScope, Register, factories, IStartable/ITickable, scope parenting. Use instead of singletons. |
| verify-layer | 109 | 109 | Check the .claude/ layer: paths, frontmatter, skill refs, budgets, retired IDs. Use after any .claude change. |
| vfx-particle-authoring | 221 | 118 | VFX Graph vs ParticleSystem, Capacity, bounds, SendEvent, sub-emitters, overdraw. Use for particle visuals and budget. |
| zlinq-zero-allocation-linq | 144 | 95 | ZLinq: AsValueEnumerable, struct operators, span sources. Use when LINQ is wanted in hot paths. |
| zstring-zero-allocation-strings | 151 | 103 | ZString: Format, Concat, Utf16/Utf8 builders, TMP SetText. Use when building strings per frame or tick. |
