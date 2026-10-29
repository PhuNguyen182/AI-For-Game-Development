---
name: odin-inspector
description: "Odin Inspector: conditional/grouping/button attributes, validation, SerializedMonoBehaviour and its serializer caveats, custom drawers. Use when building Inspector tooling with Odin."
user-invocable: false
---

# Odin Inspector

Not for: gameplay rules (`Game.Core.*`, `csharp-engineer`), runtime UGUI/UI Toolkit UI (`ugui`, `ui-toolkit`), Editor windows/drawers in UXML/USS (`ui-toolkit`; one window uses Odin or UI Toolkit, never both), ScriptableObject architecture patterns (`unity-scriptableobject-architecture`).
Docs: `https://odininspector.com/documentation/<lowercase.dotted.namespace.typename>` (generic arity as `-1`). Unversioned: tracks the current Asset Store release, so attribute overloads may differ from the installed Odin. Roots: `sirenix.odininspector` (attributes, serialization bases), `.editor` (drawers, windows, validators, resolvers), `sirenix.serialization`, `sirenix.utilities.editor` (`SirenixEditorGUI`).

| Reference | Read when |
|---|---|
| [attributes-layout-display.md](references/attributes-layout-display.md) | Grouping, order, spacing, titles, info boxes, labels or colours |
| [attributes-conditional-validation.md](references/attributes-conditional-validation.md) | Visibility, editability or legal values depend on other state; resolved-string syntax |
| [attributes-selection-references.md](references/attributes-selection-references.md) | Constraining or previewing the object, asset, type or path a field holds |
| [attributes-collections-tables.md](references/attributes-collections-tables.md) | Rendering a list, table, 2-D array or dictionary |
| [attributes-buttons-misc.md](references/attributes-buttons-misc.md) | Inspector-only button/menu action, `ShowInInspector`, enum/toggle/string display |
| [serialization.md](references/serialization.md) | A field type Unity cannot serialize (interface, `Dictionary`, polymorphic, `T[,]`) |
| [editor-extensibility.md](references/editor-extensibility.md) | No attribute combination fits: `OdinEditor`, windows, drawers, attribute processors, self-validation |

## Steps
1. Confirm the work is Inspector tooling. Odin attributes outside the serialization bases carry `[Conditional("UNITY_EDITOR")]`, so `ValidateInput`/`OnValueChanged` callbacks never run in a build. A rule that must hold at runtime goes in `Game.Core.*` (`csharp-standards` -> `coding-principles.md`, Shared Core integrity).
2. Compose built-in attributes via the matching reference. Escalate to a custom drawer only when none fits.
3. Type Unity cannot serialize: inherit `SerializedMonoBehaviour`/`SerializedScriptableObject`; `[OdinSerialize]` only marks members inside a type Odin already serializes.
4. Every resolved-string argument (`ShowIf`, `ValidateInput`, `OnValueChanged`, `ValueDropdown`, ...) is reflection-resolved with no compile check: a typo silently no-ops. Verify each names a real member, and again after any rename.
5. Inspector-editable `public`/`[SerializeField]` fields stay camelCase (`csharp-standards` -> `naming-convention.md`).
6. Attribute constructors are heavily overloaded: confirm the signature in the live docs when the reference does not list it. Check the project's C# version before using `nameof` in a string argument.
7. Odin Validator project-wide scans (`Validator<T>`, `RegisterValidatorAttribute`, `GlobalValidator`): a project-wide standard, route to `cto`; do not guess the API.

## Never
- Add Odin attributes to a `Game.Core.*` type without `technical-architect` sign-off: even attribute-only use pulls in `Sirenix.OdinInspector.Attributes` and blurs the Core/Client boundary.

## Output
```
## Odin Inspector Work — <field/type/window>
- Concern: <layout | conditional-validation | selection | collection | button-misc | serialization | editor-extensibility>
- Attributes/APIs used: <names with key constructor args>
- Layer: Game.Client.* (Editor-only where noted)
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Clamp the value inside `[OnValueChanged]` so it holds at runtime too" -> declined: the callback is stripped from builds; the clamp lives in `Game.Core.*`.
