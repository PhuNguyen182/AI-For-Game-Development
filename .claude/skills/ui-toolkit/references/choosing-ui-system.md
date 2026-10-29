# Choosing a UI system

Sources: [Compare](https://docs.unity3d.com/Manual/UI-system-compare.html), [Intro](https://docs.unity3d.com/Manual/ui-systems/introduction-ui-toolkit.html), [BPG](https://docs.unity3d.com/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/bpg-uiad-index.html) (validated Unity 6.0; cross-check newer facts).

## Runtime game UI: uGUI is still Unity's primary recommendation
| Subject | Fact |
|---|---|
| Animation | UI Toolkit has no Animation Clip/Timeline integration; uGUI does. Keyframed UI → uGUI, or hand-built USS transitions |
| Inspector wiring | uGUI supports serialized `UnityEvent`s; UI Toolkit callbacks are code-registered only |
| Scene authoring | uGUI elements are GameObjects; UI Toolkit elements live only in a virtual tree (UXML/UI Builder) and are queried by name/type, not dragged into a field |
| UI Toolkit strengths | Data binding, SVG, RTL/emoji text, textureless elements, world-space/VR UI (preferred over World Space Canvas) |
| Maturity | UI Toolkit "releases new features frequently"; uGUI/IMGUI are established and rarely updated: expect API movement |
| Roles | Compare table: full support for UI Designers, partial for Technical Artists (uGUI the reverse) |

uGUI fit → route to `ugui`.

## Editor tooling: UI Toolkit primary, IMGUI the fallback
- UI Toolkit is retained-mode (persistent tree re-styled on change); IMGUI re-declares everything in `OnGUI()` each frame.
- UXML = structure, USS = style, C# = behavior.
- Editor and runtime share elements, styling and layout; only hosting differs (`EditorWindow.rootVisualElement` vs `UIDocument`/Panel Renderer).

## Advanced-guide takeaways
- Prepare graphic/font assets before opening UI Builder.
- Prefer UI Builder over pure code; C#-only where content is genuinely dynamic.
- Treat batching/atlas tuning as a separate late pass ([rendering-and-performance.md](rendering-and-performance.md)).
- Use naming conventions at scale (`csharp-standards` → `naming-convention.md` for custom control classes).
