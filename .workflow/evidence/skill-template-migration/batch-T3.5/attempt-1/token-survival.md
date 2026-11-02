# Token survival explanations (T3.5 attempt 1)

Run: `token-survival.ps1 -Base bdf5c9ec70bf217ee9ed2763abd75fa4280b717c` with the 14 T3.5 skills. Final output: "TOTAL 14 skill(s), 3162 tokens, 50 missing". The tool printed "0 found only in scripts/" for every skill. Every miss is explained below.

## Deleted by rule (batch brief "Remove or move"): 24 misses
- `Latent concerns` and `Future remediation` (2 tokens each) in 12 skills: ugui, ui-toolkit, flexalon-layouts, osa-optimized-scrollview-adapter, litmotion-tweening, dotween-tweening, odin-inspector, r3-reactive-extensions, unitask-async-programming, vcontainer-dependency-injection, messagepipe-event-messaging, unity-scriptableobject-architecture. The "On request only, add ..." line after `## Output` was deleted in each. (mobile-safe-area and unity-localization-text had no such line.)
- Also deleted, not flagged by the tool: `Known limitations:` lines inside `## Output` fences (envelope owns them) and the `Verified:` / `Verification:` lines in ui-toolkit, flexalon-layouts, osa-optimized-scrollview-adapter, unity-localization-text, litmotion-tweening, dotween-tweening, unitask-async-programming. Domain content in them:
  - unity-localization-text `Known limitations: RTL locales excluded`: now a `## Never` bullet (RTL locales) and still in the `Not for:` bullet.
  - flexalon-layouts `Verified: Profiler numbers vs budget`: step 11 still says to measure and report frame time and allocations.
  - osa `Verified: Profiler evidence, or "not measured"`: step 13 keeps `otherwise report "not measured"`.
  - litmotion-tweening `Verification: Profiler alloc check`: step 11 keeps the 0 GC alloc check.
  - unitask-async-programming `Verification: how an allocation or timing claim was confirmed`: no step carried it; it is generic verification the envelope's `Verified` owns.
  - dotween-tweening, ui-toolkit `Verified: <evidence, or "not run">`: envelope.
- vcontainer-dependency-injection `Resolution verified: <scopes entered...>` stays in `## Output` (step 10 domain field, not the `Verified` bullet).

## Description symbols (frontmatter unchanged in T3.5; lost in T2): 13 misses
The tool printed `symbol [SKILL.md:3]` for slash compounds in the Base description. Each part survives in the body or references:
- ui-toolkit `Renderer/UIDocument`: "Panel Renderer" and `UIDocument` appear in steps 8 and 9; the current description has `UIDocument`.
- flexalon-layouts `Cloner/DataSource`: `FlexalonCloner` in step 6, `DataSource` in `references/cloner-and-data-binding.md`. `Interactable/DragTarget`: in `references/interactions-and-xr.md`.
- osa-optimized-scrollview-adapter `list/grid/table`: steps 7 and the grid reference. `ResetItems/InsertItems`: `ResetItems` in steps 7, `InsertItems` in `references/grid-and-table.md`; the current description has `ResetItems`.
- litmotion-tweening `Bind/BindTo`: `Bind` and `BindTo*` in steps 3 and 4.
- dotween-tweening `DOMove/DOFade`: `references/shortcuts.md`; the current description has `DOMove`. `Append/Join/Insert`, `SetEase/SetLoops/SetUpdate`: `references/sequences-config-control.md`; `SetEase` and `SetUpdate` are in the current description and step 6.
- odin-inspector `conditional/grouping/button`: the Output `Concern:` line and the references list.
- messagepipe-event-messaging `keyed/keyless`, `request/response`: steps 2 and 3, and the Output `Routing:` and `Pattern:` lines.
- unity-scriptableobject-architecture `Variable/Reference`: `references/data-containers-and-variables.md`; the current description has `Variable SOs`.

## Bold title changes: 12 misses
The template needs `**Title:**` with the colon inside the bold, so a title with an arrow, a trailing period or a sentence tail changed form. The wording of the title is kept.
- ui-toolkit step 2 (`bold [SKILL.md:28]`: "Ask when the Unity version or the uGUI-vs-UI-Toolkit choice is unstated"): now "Missing input: the Unity version or the uGUI-vs-UI-Toolkit choice unstated", with the three template branches nested; step number 2 stays (inventory class Lenient).
- osa-optimized-scrollview-adapter step 2 (`bold [SKILL.md:26]`: "Ask if unstated"): step 2 is now "Confirm the inputs that decide the design" and lists the four inputs; the `Missing input` step is new step 14 (inventory class Missing input; number 2 stays, new step last).
- flexalon-layouts step 11 (`bold [SKILL.md:37]`): split into "Never claim layout performance without Profiler numbers" plus a nested "Measure: any layout that dirties every frame (Lerp animator, per-frame property writes, animated `StartAt`)".
- unity-localization-text step 2, dotween-tweening step 12, r3-reactive-extensions step 10, vcontainer-dependency-injection step 11, messagepipe-event-messaging step 10, unitask-async-programming step 9: "X unstated/unclear → `Y`" became "X unstated/unclear: `Y`" (arrow to colon).
- messagepipe-event-messaging step 5: "Multiple independent subscribers → exception-boundary filter" became "Multiple independent subscribers: use an exception-boundary filter". unitask-async-programming step 7 likewise ("→ `Channel<T>` or async LINQ" became a colon).
- unitask-async-programming step 1: the bold "Replace coroutines for one-shot waits; bridge third-party awaitables with `.AsUniTask()`. Return type by who awaits" is split: the first sentence is the title, "Return type by who awaits" is a nested title.

## Link change: 1 miss
- dotween-tweening `references/coexistence-and-migration.md:19` (`link`): the relative link `../../litmotion-tweening/references/migration-and-rx-integration.md` left the skill folder; it is now the file name in backticks after `litmotion-tweening` (batches.md trap), per the template's Portability rule.
