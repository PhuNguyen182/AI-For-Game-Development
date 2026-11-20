# Library conventions

Synthesized from project decisions; adds to rule `csharp.md`. Library choice: `docs/tech-stack.md`.

- **API detail:** per `csharp-standards` SKILL.md → Package API (installed version first, then its docs).
- **Unpublished values:** a member, default or number the docs omit comes from the Inspector or source, or is reported unknown; never invented.
- **Adoption:** a new library, DOTS/ECS or a project-wide standard is `cto`'s call (`/decide`); a skill or package at hand never decides it.
- **Assumed cause:** a symptom with several causes → name the assumed layer before editing a shared asset.

## Core boundary
- **Client-only:** tweening, UniTask, R3, DI, Odin, Spine, layout adapters, Addressables, SDKs, SOs and their attributes stay out of Core; Core exposes plain events.
- **Core-safe:** MemoryPack (trusted data only), ZLinq, ZString and NRandom may enter Core; their Unity add-ons stay in Client.
- **Rule leaks:** callbacks, Animation Events, shaders, GPU results and nav agents report or render; Core decides, raising a threshold crossing once, never a per-frame value.
- **Synchronous Core:** Core rules and server-validated state graphs stay synchronous and tick-driven; a Core wait is an interface the Client drives.
- **State machines:** externalise snapshotted state; none on per-entity hot paths; a transition whose legality is a design question → `Needs-decision`, `Next: main-gd`.
- **DI:** register against an interface; lifetime = real lifespan; never widen to Singleton to silence a resolution failure, resolve at a call site, or build a scope per spawn.

## Async and events
- **Mechanism by shape:** one-shot → task (UniTask); observed value → reactive property (R3); fire-once to decoupled code → message bus; designer-wired → SO channel; coupled → interface.
- **Bus discipline:** immutable value messages; keyless before keyed; exception-boundary filter for independent subscribers; never a shared-subject bus.
- **Unstated shape:** event vs value, owning scope, or a timeout, cancellation or concurrency bound unstated → `Needs-decision`, `Next: technical-architect`.
- **No speculative concurrency:** locks, channels, `Parallel`, `ValueTask`, concurrent or immutable collections only for a second writer or a measured need.
- **Fire-and-forget:** no `async void`; a forgotten task has an exception handler; operation state is restored in `finally`.

## Tweening and animation
- **One engine per module:** module convention → project-wide choice → `Needs-decision`, `Next: technical-architect`; never defaulted because a skill was invoked.
- **Sequences:** pure composition; logic that branches or awaits → `async`/`await`; kill only tweens you own; DOTween Safe Mode stays on.
- **No hand-rolling:** no `Update()` lerp past one trivial value; no clamp or shake on a rig-driven camera; Playables only past the state machine.
- **Spine:** ships only with a confirmed licence.

## UI
- **System:** runtime UI is uGUI; UI Toolkit for Editor tooling, or runtime binding, SVG or element-count cost; an Editor window is Odin or UI Toolkit, never both.
- **One driver per property:** a layout engine, Layout Group, fitter or tween never share a `RectTransform` value; replace layout groups, never layer them.
- **UI reads state:** bind or react to change, never poll; gameplay bindings run one way; scaler matches the stable axis, 0.5 only when both orientations ship.
- **Safe area:** inset one content root per Canvas or panel, backgrounds full-bleed; no hard-coded insets or device-model branches.
- **Aspect defaults:** unstated → 16:9 and 19.5:9 (+4:3 with tablets), a notched and a notch-free device, stated.
- **Localization:** locales unstated → `Blocked`, `Next: main-gd`; Core emits ids; never concatenate, persist, send or branch on localized text; RTL is a stated known limitation.
- **Text:** one font asset per script, atlas MB stated; the pseudo-locale pass is the gate; names and chat only as a format argument, rich text off.

## Rendering and VFX
- **Pipeline:** read off Graphics and every Quality level, never the request; spec disagrees → `Blocked`; a switch → state the cost, route to `cto`; no pipeline `#if` in shared HLSL.
- **Scope and tier:** HDRP-only features never enter a mobile spec; platform or tier unstated → `Blocked`; tier values are `unity-performance-engineer`'s.
- **Shaders:** Shader Graph by default, HLSL where nodes cannot; adjective-only intent → `Blocked` until a reference image, comparable or parameter.
- **VFX:** rule-driving collisions use ParticleSystem; GPU sim only where the weakest tier supports it; scale tiers by dropping whole sub-effects.
- **Verify on the shipped tier:** name level and device class; a value written is not a rendered result; APV on Android low-end only within a measured budget.

## Physics and navigation
- **Contacts to Core:** PhysX and Box2D differ across platforms; Core gets contact point, normal and relative velocity.
- **Global knobs last:** fix mass ratios, limits and geometry before solver iterations or timestep.

## Data and serialization
- **Design data:** CSV imports at Editor or build time by default, invariant culture; culture, header or layer unstated → `Blocked`; parsed values are range-checked.
- **Binary formats:** version tolerance decided before storage; explicit member order; union tags never reused; DTOs carry data, never gameplay classes; live data unknown → `Blocked`.
- **Addressables:** one content build system per project; paths from profiles, not code; verified on a full content build.

## Netcode
- **Decisions first:** stack, topology, ownership, tick rate, prediction, encryption or relay unstated → `Needs-decision` (`cto` foundation, `technical-architect` spec).
- **Contracts:** RPC contracts compile on both sides without `UnityEngine`; never redefined or extended client-side (→ `netcode-engineer`).
- **Client wiring:** thin receivers; heartbeats and a player-visible disconnect state; no silent infinite retry or hand-rolled NAT traversal.
- **Built-ins first:** stack state and transform sync over hand-rolled RPCs; never all-reliable; anticipation only on measured need.
- **Verification:** a real multi-client run with emulation on, settings reported.

## DOTS/Jobs/Burst
- **Managed by default:** native containers only where data crosses a job, Burst or ECS; ECS systems call Core; no extra Worlds without a reason.
- **Burst:** never alone; the Burst Inspector is evidence, the attribute is not.
- **Burst float mode:** server-evaluated maths stays `Deterministic` or `Strict` (tolerance unstated → `Strict`, flagged); `Fast` only for presentation.
- **Parallel work:** only provably independent iterations; parallel and ECB writes take a deterministic order.
- **Safety checks:** disabled only on a measurement naming them as the cost; an Editor-clean run never proves safety.
- **Mathematics:** `Unity.Mathematics` alone never fixes determinism; `float3` casing is no naming violation.

## CI and SDK
- **Editor lock:** every stage opening the Unity project holds a named lock and a timeout; job logic lives in the repo and runs the same locally and on CI.
- **Pinned toolchains:** `bundle exec` and pinned CLIs, never floating; the build number is set once, from the CI run, in the Unity build.
- **Evidence:** a pass is a report or release link, never silence or exit 0; a coverage threshold only when the main GD or `docs/tech-stack.md` sets one.
- **Shipping builds:** no debugger, diagnostics window or network simulator enabled; one uploader; testers by group alias.
- **SDK bootstrap:** one bootstrap owns init, every call waits; failure disables the feature, logs once, the game runs; one version and install method.
- **Generators:** only for types needing one today; never chained on another generator; diagnose, never throw; deterministic output.
- **Analyzers:** a decidable rule from the rule files, violated twice; `Error` only for correctness breaks; stable prefixed IDs; mechanical fixes only.
