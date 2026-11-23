# Skill pruning

- State: records.py feature show skill-pruning
- Bugs: bugs.py list --feature skill-pruning

<!-- State, rounds and stop rules live in the feature registry; each table below is a CSV the records CLI writes (skill records). -->

## Request (verbatim)
> tôi nhận ra là gần như toàn bộ đống skill của C# và Unity hoàn toàn có thể loại bỏ hết đi, vì bây giờ AI model đã thông minh hơn và có thể quét codebase để hiểu luôn toàn bộ plugin hay package cần dùng đó làm những gì, chỉ nên giữ lại những skill của các agent đặt biệt thuộc nhóm lãnh đạo, leader, security, workflow cùng với các skill đóng vai trò nhập lệnh. Bạn hãy xem xét cùng tôi để loại bớt các skill có thể gây lỗi thời, hoặc bị loại bỏ trong tương lai khi docs nguyên gốc của chính chủ có thể thay đổi hoặc lỗi thời

## Main GD decisions

- Rows: records.py csv render decisions --feature skill-pruning

## Spec
Approved plan (CP1 direction + CP2 list): `C:\Users\Admin\.claude\plans\t-i-nh-n-ra-l-temporal-honey.md`, copied below.

Acceptance criteria:
1. The 61 vendor-doc skill directories listed below are deleted from `.claude/skills/`.
2. House rules found in them (project decisions, not API facts) are kept in `.claude/skills/csharp-standards/references/library-conventions.md` (≤ 8,000 chars), linked from `csharp-standards/SKILL.md`; security-class lines go to `secret-and-supply-chain-scan` or the owning agent.
3. `csharp-standards/SKILL.md` and each engineer agent carry the replacement instruction: installed version first (`Packages/manifest.json`, `packages-lock.json`, package source under `Library/PackageCache/` read only, never copied into evidence), then that version's vendor docs; a `unity:*` plugin skill when installed; per-project library choice in `docs/tech-stack.md`.
4. No file under `.claude/` (outside `verify.ps1`'s retired list) names a deleted skill; agent `Skills (on demand)` lists hold only kept skills and `unity:*` entries.
5. The 6 gate-tooling skills (unity-test-framework, unity-profiler-diagnostics, unity-batchmode-cli, build-fault-triage, ci-pipeline-failure-triage, git-unity-repo) keep Steps, Never, Output, scripts and contract strings; pure API catalogue references are removed.
6. The 8 Core/security skills and all leadership, workflow, command and security skills are unchanged except for references to deleted skills.
7. `verify.ps1` fails on any reference to a retired skill name; the hook suite covers it.
8. `/verify-layer` exits 0; hook suite and the layer's Python tests pass.

Delete list (61):
- .NET / C# libraries (21): csvhelper-csv-data, dotnet-concurrency-and-async, dotnet-memory-and-collections, dotween-tweening, litmotion-tweening, flexalon-layouts, magiconion-rpc-networking, memorypack-serialization, messagepipe-event-messaging, nrandom-random-generation, odin-inspector, osa-optimized-scrollview-adapter, r3-reactive-extensions, stateless-state-machines, unitask-async-programming, vcontainer-dependency-injection, zlinq-zero-allocation-linq, zstring-zero-allocation-strings, spine-animation, source-generator-authoring, roslyn-analyzer-codefix
- Unity engine (27): unity-2d-physics, unity-2d-sprite, unity-2d-spriteshape, unity-3d-mesh, unity-3d-physics, unity-addressables, unity-animation, unity-audio-mixer, unity-burst-compiler, unity-camera-fundamentals, unity-cinemachine-authoring, unity-collections, unity-ecs-architecture, unity-entities-graphics, unity-hdrp-rendering, unity-input-system, unity-job-system-and-burst, unity-lighting, unity-localization-text, unity-mathematics, unity-navmesh-navigation, unity-physics, unity-post-processing, unity-scriptableobject-architecture, unity-tilemap, unity-transport, unity-urp-rendering
- Rendering / UI / VFX (7): render-pipeline-urp-hdrp, shader-authoring, compute-shader-vfx, vfx-particle-authoring, ugui, ui-toolkit, mobile-safe-area
- Netcode vendor (2): netcode-for-entities, netcode-for-gameobjects
- SDK / CI vendor (4): firebase-unity-sdk, firebase-app-distribution, fastlane-mobile-delivery, jenkins-pipeline-authoring

## Log

- Rows: records.py csv render log --feature skill-pruning

## Tests

- Rows: records.py csv render tests --feature skill-pruning

## Known limitations

- Rows: records.py csv render limitations --feature skill-pruning
