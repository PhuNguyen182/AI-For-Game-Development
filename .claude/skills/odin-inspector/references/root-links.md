# Root Links — Sirenix Odin Inspector

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to the live Odin Inspector API documentation
site. Odin's docs are not version-numbered in the URL — the site always
reflects the current published Asset Store release. Anything this skill cites
resolves under one of these roots; anything that does not is out of scope for
the skill, not merely undocumented here.

| Root | Holds | Source |
|---|---|---|
| Sirenix.OdinInspector | Runtime-visible attributes and support types (grouping, conditionals, validation, buttons, serialization base classes) — assembly `Sirenix.OdinInspector.Attributes` | [Sirenix.OdinInspector](https://odininspector.com/documentation/sirenix.odininspector) |
| Sirenix.OdinInspector.Editor | Editor-only extensibility: custom drawers, editors, editor windows, menu trees, validators, value/action resolvers — assembly `Sirenix.OdinInspector.Editor` | [Sirenix.OdinInspector.Editor](https://odininspector.com/documentation/sirenix.odininspector.editor) |
| Sirenix.Serialization | The Odin serializer itself — formatters, `OdinSerializeAttribute`, binary/JSON data readers/writers — assembly `Sirenix.Serialization` | [Sirenix.Serialization](https://odininspector.com/documentation/sirenix.serialization) |
| Sirenix.Utilities.Editor | GUI-drawing helpers used when writing custom drawers (`SirenixEditorGUI`, `GUIHelper`, `EditorIcons`) | [Sirenix.Utilities.Editor](https://odininspector.com/documentation/sirenix.utilities.editor) |

Every other link in this `references/` folder is a specific class page under
these roots. Each URL follows the pattern
`https://odininspector.com/documentation/<lowercase.dotted.namespace.plus.typename>`
(generic arity suffixed as `-1`, e.g. `...odinvaluedrawer-1` for
`OdinValueDrawer<T>`) and was verified to resolve before inclusion. Consult
the live site for anything not covered here — Odin adds attributes and
editor APIs between Asset Store releases, and this skill only distills the
surface that was current when it was written.
