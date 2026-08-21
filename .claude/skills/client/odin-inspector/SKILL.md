---
name: odin-inspector
description: >
  Sirenix Odin Inspector: attributes like ShowIf, HideIf, EnableIf,
  DisableIf, BoxGroup, TabGroup, FoldoutGroup, HorizontalGroup, Button,
  ButtonGroup, ValueDropdown, AssetSelector, InlineEditor, PreviewField,
  ListDrawerSettings, TableList, TableMatrix, DictionaryDrawerSettings,
  ValidateInput, Required, and OnValueChanged; Odin serialization
  (SerializedMonoBehaviour, SerializedScriptableObject, [OdinSerialize]);
  and editor extensibility (OdinEditor, OdinEditorWindow,
  OdinMenuEditorWindow, OdinValueDrawer<T>, OdinAttributeDrawer<TAttribute>,
  OdinAttributeProcessor, PropertyTree, InspectorProperty). Use when
  decorating a MonoBehaviour, ScriptableObject, or [Serializable] field for
  the Inspector, serializing a type Unity can't (interfaces, dictionaries,
  polymorphic references), or writing a custom Odin drawer or menu-based
  editor window. Not for: runtime gameplay rules (`csharp-engineer`'s
  Shared Core), Unity's native UGUI or UI Toolkit runtime UI
  (`ui-ux-programmer`), MonoBehaviour lifecycle and profiling
  (`unity-engineer`).
---

# Sirenix Odin Inspector — Attributes, Serialization & Editor Extensibility

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short. Each file
follows `skill-reference-template.md`. "Read when" is a real condition, not a
restatement of the topic.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Upstream doc roots this skill was built from | Starting any Odin task, or resolving a link not covered below |
| [attributes-layout-display.md](references/attributes-layout-display.md) | Grouping/layout attributes (`BoxGroup`, `TabGroup`, `FoldoutGroup`, `Horizontal/VerticalGroup`, `ToggleGroup`, `TitleGroup`), ordering/spacing, label/tooltip/color cosmetics | Organizing or restyling how fields lay out in the Inspector |
| [attributes-conditional-validation.md](references/attributes-conditional-validation.md) | `ShowIf`/`HideIf`/`EnableIf`/`DisableIf`, play-mode gating, `Required`/`ValidateInput`/`OnValueChanged`, numeric constraints (`MinValue`/`MaxValue`/`PropertyRange`/`MinMaxSlider`/`Wrap`/`Unit`) | Making a field's visibility, editability, or legal value range depend on other state |
| [attributes-selection-references.md](references/attributes-selection-references.md) | `ValueDropdown`, `AssetSelector`/`AssetList`/`AssetsOnly`, `TypeFilter`, `InlineEditor`, `PreviewField`, `FilePath`/`FolderPath`, `ColorPalette` | Constraining or previewing what object/asset/type a field can reference |
| [attributes-collections-tables.md](references/attributes-collections-tables.md) | `ListDrawerSettings`, `TableList`, `TableColumnWidth`, `TableMatrix`, `DictionaryDrawerSettings` | Customizing how a list, 2-D array, or dictionary renders |
| [attributes-buttons-misc.md](references/attributes-buttons-misc.md) | `Button`/`ButtonGroup`/`InlineButton`, `CustomContextMenu`, `ShowInInspector`, enum/toggle/string display attributes (`EnumToggleButtons`, `EnumPaging`, `Toggle`, `DisplayAsString`, `MultiLineProperty`) | Adding an inspector-only action, or changing how a value's raw type is displayed |
| [serialization.md](references/serialization.md) | `SerializedMonoBehaviour`, `SerializedScriptableObject`, `[OdinSerialize]`, what Odin's serializer adds over Unity's | A field's type can't survive Unity's own serializer |
| [editor-extensibility.md](references/editor-extensibility.md) | `OdinEditor`, `OdinEditorWindow`, `OdinMenuEditorWindow`/`OdinMenuTree`, `OdinDrawer`/`OdinValueDrawer<T>`/`OdinAttributeDrawer<TAttribute>`/`OdinGroupDrawer`, `OdinAttributeProcessor`, `PropertyTree`/`InspectorProperty`, `ValueResolver<T>`, `SelfValidationResult` | No combination of built-in attributes covers the requirement — writing custom editor code |

## 1. Objective
Use Odin Inspector's attribute surface, serialization layer, and editor-extensibility APIs to build correct, maintainable Unity Inspector tooling — without leaking Editor-only behavior into runtime logic, without duplicating game-rule decisions that belong in Shared Core, and without reaching for a custom drawer when a declarative attribute combination already solves the problem.

## 2. Role
Act as the Odin Inspector specialist for the client track — the tool reached for whenever a MonoBehaviour, ScriptableObject, or `[Serializable]` type needs its Inspector presentation customized, its data made serializable beyond Unity's own capabilities, or its editor tooling extended with a custom drawer or window.

## 3. When to invoke this skill
- Decorating a field/property/method with an Odin attribute (`[ShowIf]`, `[BoxGroup]`, `[Button]`, `[ValueDropdown]`, etc.) to change how it appears or behaves in the Inspector.
- A field's type can't be serialized by Unity (an interface, `Dictionary<K,V>`, a polymorphic reference, a multi-dimensional array) and needs `SerializedMonoBehaviour`/`SerializedScriptableObject` or `[OdinSerialize]`.
- Writing a custom `OdinEditor`, `OdinEditorWindow`, `OdinMenuEditorWindow`, or a custom `OdinDrawer`/`OdinAttributeProcessor` because attributes alone can't express the requirement.
- Debugging why an Odin attribute's conditional string (`ShowIf`, `ValidateInput`, `OnValueChanged`) isn't firing, or why a type isn't drawing as expected.
- Negative trigger: the actual damage/cooldown/economy decision an `[OnValueChanged]` callback would trigger — that decision belongs in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity section, not `csharp-engineer`'s domain via this skill.
- Negative trigger: building runtime (in-game, player-facing) UI with UGUI or UI Toolkit — that is `ui-ux-programmer`'s domain, not the Inspector.
- Negative trigger: general MonoBehaviour performance work (pooling, `Update()` allocations, profiler passes) unrelated to Inspector/editor tooling — that is `unity-engineer`'s domain.

## 4. How to use this skill
1. **Confirm the task is Inspector/editor tooling, not gameplay logic** — every Odin attribute in `Sirenix.OdinInspector` outside the serialization base classes carries `[Conditional("UNITY_EDITOR")]`, so any callback it triggers (`ValidateInput`, `OnValueChanged`) never runs in a build. A rule that must hold at runtime belongs in `Game.Core.*`, per `coding-principles.md`'s Shared Core integrity section — never rely on an Odin attribute to enforce it.
2. **Route to the narrowest reference file for the concern**: layout/organization → [attributes-layout-display.md](references/attributes-layout-display.md); visibility/editability/validation → [attributes-conditional-validation.md](references/attributes-conditional-validation.md); object/asset/type selection or preview → [attributes-selection-references.md](references/attributes-selection-references.md); lists/dictionaries/2-D arrays → [attributes-collections-tables.md](references/attributes-collections-tables.md); buttons/inspector-only actions/raw-value display → [attributes-buttons-misc.md](references/attributes-buttons-misc.md).
3. **Default to composing built-in attributes; escalate to a custom drawer only once no attribute combination covers the requirement** — per [editor-extensibility.md](references/editor-extensibility.md), per KISS/YAGNI in `coding-principles.md`. A custom `OdinValueDrawer<T>` or `OdinAttributeDrawer<TAttribute>` is justified by a genuinely new visual/interaction pattern, not by convenience.
4. **When the field's type can't survive Unity's own serializer** (an interface, `Dictionary<K,V>`, a polymorphic reference, a multi-dimensional array like the one `TableMatrix` renders) — inherit `SerializedMonoBehaviour`/`SerializedScriptableObject`, or mark the individual member `[OdinSerialize]` on a type that already serializes normally, per [serialization.md](references/serialization.md).
5. **Apply `naming-convention.md`'s Inspector-serialized-field rule to every field an Odin attribute decorates** — camelCase for any `public`/`[SerializeField]` field the Inspector can edit, exactly as for Unity's own attributes; Odin attributes do not change that convention.
6. **Verify every resolved-string argument names a real member before shipping** — `ShowIf`, `ValidateInput`, `OnValueChanged`, `ValueDropdown`, and similar string-based conditions are resolved by reflection at edit time with no compile-time check, so a typo fails silently as a no-op in the Inspector rather than a build error.
7. **When writing a custom drawer, pick the narrowest base class the requirement needs** — `OdinValueDrawer<T>` for a type-driven drawer, `OdinAttributeDrawer<TAttribute>`/`OdinAttributeDrawer<TAttribute, TValue>` for an attribute-driven one, `OdinGroupDrawer<TGroupAttribute>` for a new group layout — and call `CallNextDrawer(label)` unless intentionally terminating the draw chain, per [editor-extensibility.md](references/editor-extensibility.md).
8. **If the required attribute, resolver syntax, or editor API isn't covered by the bundled references**, consult the live site via [root-links.md](references/root-links.md)'s roots rather than guessing a constructor signature — Odin's attribute constructors are frequently overloaded, and an incorrect overload compiles only when the argument types happen to coincide.

## 5. Specific goals / tasks this skill performs
- Select and correctly parameterize the Odin attribute(s) that solve a given Inspector-presentation requirement.
- Decide whether Odin serialization (`SerializedMonoBehaviour`/`SerializedScriptableObject`/`[OdinSerialize]`) is actually needed for a given field's type, versus Unity's own serializer already handling it.
- Scaffold a custom `OdinEditor`, `OdinEditorWindow`, `OdinMenuEditorWindow`, `OdinDrawer`, or `OdinAttributeProcessor` when attributes alone are insufficient.
- Diagnose a non-firing conditional string, a missing drawer, or an unexpected serialization gap.
- Out of scope: the runtime behavior an Inspector button or callback triggers (`csharp-engineer`'s Shared Core), Odin Validator project-wide validation rule authoring beyond `SelfValidator<T>`/`ISelfValidator` basics (`tech-lead-csharp-unity` for deep custom validator systems), player-facing runtime UI (`ui-ux-programmer`).

## 6. Output format
```
## Odin Inspector Work — <field/type/window name>
- Concern: <layout / conditional-validation / selection-reference / collection / button-misc / serialization / editor-extensibility>
- Attributes/APIs used: <exact attribute or class names with key constructor args>
- Naming-convention compliance: <camelCase Inspector-serialized fields confirmed, per naming-convention.md>
- Shared Core boundary: <confirmed no gameplay-rule logic lives inside an Odin callback/attribute>
- Layer: Game.Client.* (Editor-only where noted)
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Add a `Speed` field to `PlayerMovement` that only shows up when `UseCustomSpeed` is true, and must stay between 0 and 20."
- Output: `[ShowIf(nameof(useCustomSpeed))] [PropertyRange(0, 20)] public float speed;` on the camelCase Inspector-serialized field, per [attributes-conditional-validation.md](references/attributes-conditional-validation.md) and `naming-convention.md`'s Inspector override; no change to the actual speed-clamping game logic, which stays in `Game.Core.*`.

**Example 2**
- Input: "Just clamp the value inside the `[OnValueChanged]` callback so it's always valid at runtime too."
- Output: declined — `[OnValueChanged]` (and every other Odin attribute here) carries `[Conditional("UNITY_EDITOR")]`, so that callback is stripped from builds and never runs at runtime; the clamp must live in `Game.Core.*` gameplay logic instead, per `coding-principles.md`'s Shared Core integrity section.

**Example 3**
- Input: "A ScriptableObject needs a `Dictionary<string, AbilityConfig>` field that Unity refuses to serialize."
- Output: inherit `SerializedScriptableObject` (or mark just that field `[OdinSerialize]` if the type otherwise serializes fine with Unity), per [serialization.md](references/serialization.md); confirm the dictionary drawer's key/value labels via `[DictionaryDrawerSettings]` if the default labels are unclear.

## 8. Edge cases & guardrails
- Never let an Odin attribute's resolved-string condition stand in for a compile-time contract — a renamed member silently breaks the attribute with no build error; re-verify after any rename touching a decorated type.
- Never add Odin attributes to a `Game.Core.*` type by default — even attribute-only usage pulls in the `Sirenix.OdinInspector.Attributes` assembly and blurs the Core/Client boundary `naming-convention.md`'s namespace-boundary section protects; get explicit sign-off from `technical-architect` before doing so.
- Never write a custom `OdinDrawer` as the first attempt — that is the escalation path §4's "Default to composing built-in attributes" step defines, not the default; a growing pile of custom drawers where attributes would do is the speculative-complexity YAGNI already forbids.
- If the target Unity/C# language version is unconfirmed, do not assume a modern Odin usage pattern (e.g. relying on `nameof` in an older C# target) compiles — check per `coding-principles.md`'s Modern C# syntax caveat before writing the resolved-string argument.
- If a requirement seems to need Odin Validator's project-wide validation scans (custom `Validator<T>`/`RegisterValidatorAttribute` systems) rather than a simple `ISelfValidator` on one type, flag it to `tech-lead-csharp-unity` rather than guessing at an undocumented API surface — do not fabricate a constructor or method signature not confirmed in [editor-extensibility.md](references/editor-extensibility.md) or the live docs.
