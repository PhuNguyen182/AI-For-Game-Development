---
name: ui-toolkit
description: >
  Unity UI Toolkit (`UnityEngine.UIElements`) technique — UXML structure, UI
  Builder, `VisualElement`/`UxmlElement` custom controls, USS styling
  (Flexbox layout, selectors, pseudo-classes, BEM naming), typed events
  (`RegisterCallback<T>`, trickle-down/bubble-up, Manipulators), runtime
  hosting (`UIDocument`, Panel Renderer, `PanelSettings` scale modes, world
  space, dynamic atlas), data binding (`INotifyBindablePropertyChanged`,
  `SerializedObject.Bind()`), Editor tooling (`CreateGUI`,
  `CreateInspectorGUI`, `CreatePropertyGUI`), text/font assets, and the UI
  Test Framework package. Use for building or debugging a runtime HUD/menu
  or an Editor window/inspector in UI Toolkit. Not for: uGUI/Canvas UI
  (`ugui`), Animator-driven UI (`unity-animation`), input device polling and
  action binding (`unity-input-system`), and any gameplay rule behind the UI
  (`csharp-engineer`).
---

# Unity UI Toolkit — UXML, USS, Events, Runtime Hosting, Editor Tooling

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual/API roots, the Unity 6.5 version pin, topic→file map, disclosed gaps | Starting any task here, or confirming a fact against the installed Editor |
| [choosing-ui-system.md](references/choosing-ui-system.md) | IMGUI/uGUI/UI Toolkit comparison, retained-mode model, advanced-guide takeaways | Deciding whether UI Toolkit is even the right system for this screen |
| [uxml-and-visual-tree.md](references/uxml-and-visual-tree.md) | Visual tree model, the three authoring paths, UI Builder panes, templates, custom controls | Structuring a screen, or writing a custom `VisualElement` |
| [uss-styling-and-layout.md](references/uss-styling-and-layout.md) | USS vs CSS subset, selector precedence, pseudo-classes, Flexbox defaults, inheritance/animatability, variables | Styling anything, or a layout doesn't behave like web CSS |
| [text-and-fonts.md](references/text-and-fonts.md) | TextField behavior, rich text tags, dynamic SDF vs bitmap font assets, fallback fonts | Any text field, label, or font asset decision |
| [events-and-manipulators.md](references/events-and-manipulators.md) | Propagation phases, Pointer/Mouse/Focus events, pointer capture, Manipulators | Wiring interaction behavior to any control |
| [runtime-panels-and-input.md](references/runtime-panels-and-input.md) | `UIDocument` vs Panel Renderer, `PanelSettings` scale modes/atlas, world space, runtime `EventSystem` need | Hosting UI at runtime, or world-space/VR UI |
| [editor-ui-authoring.md](references/editor-ui-authoring.md) | `CreateGUI`/`CreateInspectorGUI`/`CreatePropertyGUI`, state persistence, `ViewData` | Building a custom Editor window, inspector, or property drawer |
| [data-binding.md](references/data-binding.md) | Runtime data binding vs `SerializedObject` binding, modes, update triggers | Syncing UI to gameplay state or serialized data |
| [rendering-and-performance.md](references/rendering-and-performance.md) | Dynamic atlas thresholds, what breaks batching, `UsageHints`, element pooling | Draw calls are high, or an animated UI drops frames |
| [testing-and-migration.md](references/testing-and-migration.md) | UI Test Framework package, migration blockers from uGUI/IMGUI | Writing a UI test, or porting an existing uGUI/IMGUI screen |

## 1. Objective
Build UI Toolkit screens and Editor tooling that render correctly across
devices, stay testable, and don't silently regress performance — avoiding
this system's characteristic silent failures: a `flex-direction` default
that stacks children the opposite way from web CSS, an inline style that
quietly out-prioritizes a whole USS file, a callback left registered on a
pooled element, an animated `width` that rebuilds geometry every frame, a
runtime data source that never notifies because `propertyChanged` was never
raised, and a `UIDocument`/Panel Renderer choice made without checking which
one the installed Editor version actually supports.

## 2. Role
Act as the UI Toolkit specialist for the client track — the skill reached
for whenever a runtime HUD/menu or an Editor window/inspector/property
drawer is being built, styled, wired, bound, or debugged with
`UnityEngine.UIElements`. You decide structure, style, event wiring, hosting,
and binding; you never decide what a UI displays as a game-rule outcome.

## 3. When to invoke this skill
- Building or editing UXML/USS, or working in UI Builder.
- Writing a custom `VisualElement`/`UxmlElement`, or deciding whether one is even needed.
- Wiring `RegisterCallback<T>`, Manipulators, focus, or pointer capture to a control.
- Hosting runtime UI: `UIDocument`/Panel Renderer, `PanelSettings`, world-space or multi-device scaling.
- Binding UI to gameplay state or to `SerializedObject` data.
- Building a custom Editor window, inspector, or property drawer with UI Toolkit.
- Diagnosing high UI draw calls, dropped frames on an animated UI, or a layout that doesn't match a web-CSS assumption.
- Writing UI Toolkit tests, or assessing a uGUI/IMGUI migration.
- Negative trigger: the screen genuinely belongs on uGUI's `Canvas` — per [choosing-ui-system.md](references/choosing-ui-system.md), that's `ugui`; route to it rather than forcing the screen into UI Toolkit.
- Negative trigger: Animator-driven UI animation (keyframed clips, blend trees driving a widget) — that's `unity-animation`; UI Toolkit itself has no Timeline/Animation Clip integration.
- Negative trigger: reading the input device or authoring `.inputactions` — that's `unity-input-system`; this skill only reacts to the events that system (or UI Toolkit's own default runtime input) delivers.
- Negative trigger: whether a button press is currently allowed, what a value on screen means for the game, or any cooldown/resource check — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity section.

## 4. How to use this skill
1. **Confirm UI Toolkit is the right system for this surface before authoring anything** — Unity still recommends uGUI as the *primary* system for runtime game UI and reserves UI Toolkit as the default only for Editor tooling, per [choosing-ui-system.md](references/choosing-ui-system.md). Flag it rather than assuming when the surface needs Animation Clip/Timeline integration or Inspector-wired `UnityEvent`s, since neither exists in UI Toolkit.
2. **Author structure in UXML and UI Builder, not ad-hoc C#-only construction** — per [uxml-and-visual-tree.md](references/uxml-and-visual-tree.md). Build purely in C# only where content is genuinely not known until runtime; even then, query/register inside `OnUIReload`/`CreateGUI`, never `Awake`.
3. **Write a custom `UxmlElement` only once no built-in element or template fits** — per YAGNI in `coding-principles.md` and [uxml-and-visual-tree.md](references/uxml-and-visual-tree.md); it needs a default constructor, and the UXML-first pattern keeps UI Builder able to navigate it, unlike the `CloneTree()` element-first pattern.
4. **Style through USS selectors and BEM-style class names, never one-off inline styles** — per [uss-styling-and-layout.md](references/uss-styling-and-layout.md). Inline C# styles always win the override stack and carry per-element memory cost; reserve them for values genuinely computed at runtime.
5. **Verify a layout or CSS-parity assumption against USS's documented subset before trusting it** — `flex-direction` defaults to `column`, not CSS's `row`, and `!important`, `float`, `calc()`, and sibling selectors do not exist at all, per [uss-styling-and-layout.md](references/uss-styling-and-layout.md).
6. **Author text with dynamic SDF font assets, never a static/bitmap asset** — the Advanced Text Generator does not support static font assets at all, per [text-and-fonts.md](references/text-and-fonts.md); pick SDFAA/SDF16/SDF32 by whether the text is an input field, label, or title.
7. **Wire behavior through typed `RegisterCallback<T>` events and Manipulators, never string-based dispatch** — per [events-and-manipulators.md](references/events-and-manipulators.md) and `coding-principles.md`'s Event handlers rule: use a named method, and unregister it in the same teardown path a MonoBehaviour would use for `OnDisable`.
8. **Pick Panel Renderer or `UIDocument` by the installed Editor version, and set the Scale Mode from the target platform** — Panel Renderer supersedes `UIDocument` only from Unity 6.5 onward; confirm the version pinned in [root-links.md](references/root-links.md) against the installed Editor before assuming it exists, per [runtime-panels-and-input.md](references/runtime-panels-and-input.md). Set Scale With Screen Size for a responsive PC + mobile HUD, per `coding-principles.md`'s responsive-UI expectation.
9. **Add an `EventSystem` only when uGUI shares the scene** — UI Toolkit creates its own default runtime event system with no scene component needed at all, per [runtime-panels-and-input.md](references/runtime-panels-and-input.md); adding one unconditionally just changes which pipeline UI Toolkit runs under, for no benefit in a pure UI Toolkit scene.
10. **Bind gameplay state through runtime data binding, and Editor state through `SerializedObject` binding — never poll a value in `Update`** — per [data-binding.md](references/data-binding.md) and `performance-and-algorithms.md`'s hot-path rules. A source that never raises `propertyChanged` silently never updates its bound controls.
11. **Build Editor tooling through `CreateGUI`/`CreateInspectorGUI`/`CreatePropertyGUI`, and persist state in `[SerializeField]`, not on the `VisualElement`** — per [editor-ui-authoring.md](references/editor-ui-authoring.md); a `VisualElement` is not serializable and does not survive a domain reload.
12. **Keep draw-call batches intact: budget the dynamic atlas, animate transforms not layout, and pool elements with callbacks unregistered first** — per [rendering-and-performance.md](references/rendering-and-performance.md) and `performance-and-algorithms.md`'s Unity-specific optimization section. Textures over 64×64 are excluded from the default dynamic atlas; animating `width`/`left` rebuilds geometry every frame.
13. **Test through the UI Test Framework package, and flag a documented migration blocker before promising a 1:1 port** — hand the written test to `qa-automation-engineer`, per [testing-and-migration.md](references/testing-and-migration.md); UI Toolkit has no anchor/pivot equivalent for a uGUI layout, and several IMGUI calls have no UI Toolkit equivalent at all.
14. **Ask rather than guess when the target Unity version, or the uGUI-vs-UI-Toolkit choice, is not stated** — both gate real decisions (Panel Renderer availability, whether a screen even belongs in this skill); proceed only on a clearly flagged assumption if the requester is unavailable.

## 5. Specific goals / tasks this skill performs
- UXML/USS authoring and UI Builder workflows, including templates and custom `UxmlElement` controls.
- Event wiring, Manipulators, focus, and pointer capture for interactive controls.
- Runtime hosting: `UIDocument`/Panel Renderer, `PanelSettings` scale modes, world-space UI, and runtime input plumbing.
- Editor tooling: custom Editor windows, inspectors, and property drawers built with UI Toolkit.
- Runtime and `SerializedObject` data binding.
- Text and font asset decisions, including migrating off static font assets.
- Draw-call and dynamic-atlas performance diagnosis and fixes.
- UI Toolkit test authoring support and uGUI/IMGUI migration assessment.
- Out of scope: uGUI/Canvas UI (`ugui`), Animator-driven UI animation (`unity-animation`), input device polling and action binding (`unity-input-system`), any gameplay rule or state decision behind the UI (`csharp-engineer`).

## 6. Output format
```
## UI Toolkit Work — <screen/tool name>
- System choice: UI Toolkit confirmed over uGUI/IMGUI — why
- Structure: UXML/UI Builder / hand-written UXML / pure C# — and why; custom controls introduced (if any)
- Styling: USS files and key selectors, BEM classes used, USS variables introduced
- Events: RegisterCallback<T> registrations and Manipulators, with teardown/unregister confirmed
- Hosting (if runtime): UIDocument / Panel Renderer — Editor version confirmed; PanelSettings Scale Mode; world space (yes/no)
- Input plumbing: EventSystem added only if uGUI present — confirmed
- Binding: runtime data binding / SerializedObject binding — source type and update trigger/mode
- Editor tooling (if applicable): CreateGUI/CreateInspectorGUI/CreatePropertyGUI used; state persisted via [SerializeField]
- Performance: dynamic atlas settings checked, animated properties confirmed transform-only, pooling/unregister confirmed
- Testing/migration: UI Test Framework coverage handed to qa-automation-engineer, or migration blockers flagged
- Shared Core boundary: confirmed no gameplay outcome decided in this layer
- Layer: Game.Client.* / Editor-only
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered UI does not cover — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Build a responsive PC + mobile inventory panel with a scrollable item grid."
- Output: authored in UXML/UI Builder with a `ListView` for the item rows (its built-in row recycling avoids per-item pooling code), styled with BEM classes (`inventory-panel__slot`) in a dedicated `.uss` file, and hosted on Panel Renderer (confirmed Unity 6.5+) with `PanelSettings` Scale Mode set to Scale With Screen Size and a reference resolution matching the design mock. No `EventSystem` added, since the scene has no uGUI. Item counts bound via runtime data binding against an `InventoryViewModel` implementing `INotifyBindablePropertyChanged`, not polled in `Update`.

**Example 2**
- Input: "Just poll the player's HP field in `Update` and set the label text every frame, it's simpler than setting up binding."
- Output: declined — per `performance-and-algorithms.md`'s hot-path rules and [data-binding.md](references/data-binding.md), a `.ToString()` plus label update every frame is wasted work even when HP hasn't changed. Wired `INotifyBindablePropertyChanged` on the health view-model instead, raising `propertyChanged` only on an actual change, with `updateTrigger` left on change detection.

**Example 3**
- Input: "The custom Editor window loses its search filter every time a script recompiles."
- Output: root-caused as `VisualElement` state not surviving domain reload, per [editor-ui-authoring.md](references/editor-ui-authoring.md) — the filter string had been kept on the `ToolbarSearchField`'s own field instead of `[SerializeField]` on the `EditorWindow`. Moved it to a serialized field on the window, reapplied inside `CreateGUI()`.

## 8. Edge cases & guardrails
- Never assume `flex-direction` defaults to `row` — it defaults to `column` in USS, the reverse of web CSS.
- Never rely on `!important`, `float`, `calc()`, CSS grid, or a sibling selector (`+`/`~`) — none exist in USS.
- Never leave an event callback registered on an element being returned to a pool — it keeps firing on a "dead" element.
- Never animate `width`/`height`/`left`/`top` every frame for a purely visual effect — animate `translate`/`scale`/`rotate` instead, per [rendering-and-performance.md](references/rendering-and-performance.md).
- Never assume a texture over 64×64 joined the dynamic atlas by default — check `DynamicAtlasSettings` before diagnosing a batching regression elsewhere.
- Never call `.Bind()` a second time on the same element, or call it manually inside `CreateInspectorGUI()`/`CreatePropertyGUI()` — Unity already binds implicitly there.
- Never store UI state that must survive a domain reload on a `VisualElement` — it is not serializable; use `[SerializeField]` on the `EditorWindow`/`Editor`.
- Never add a scene `EventSystem` "just in case" for a pure UI Toolkit scene — it changes the input pipeline UI Toolkit runs under for no benefit.
- Never promise a 1:1 uGUI port without checking the anchor/pivot gap, or a 1:1 IMGUI port without checking the explicit no-equivalent call list, per [testing-and-migration.md](references/testing-and-migration.md).
- Never author a new static/bitmap font asset — the Advanced Text Generator does not support it.
- Never assume Panel Renderer exists without confirming the installed Editor is Unity 6.5 or later; `UIDocument` remains correct on earlier versions.
- If the target Unity version or the uGUI-vs-UI-Toolkit choice is not stated, ask rather than silently pick one — both gate real decisions in this skill.
- Never let this layer decide what a bound value means for gameplay — it displays and reacts to input; `Game.Core.*` decides the outcome, per `coding-principles.md`'s Shared Core integrity section.
