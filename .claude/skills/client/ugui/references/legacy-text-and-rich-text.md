# Legacy Text — Rich Text Tags

Source: [Rich Text](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/StyledText.html).
Covers: SKILL.md §4 — "Never author a new legacy Text screen — TMP is the default".

## Scope

This file documents the **legacy** `Text` component's rich text markup —
a small, fixed tag set, distinct from and much smaller than TextMeshPro's
(see [textmeshpro-core-and-rich-text.md](textmeshpro-core-and-rich-text.md)).
It's included for reading/maintaining an existing legacy-`Text` screen;
it is not the tag set to reach for on new work.

## Supported tags

| Tag | Effect |
|---|---|
| `<b>...</b>` | Bold |
| `<i>...</i>` | Italic |
| `<size=N>...</size>` | Sets pixel size for the enclosed text |
| `<color=#rrggbbaa>...</color>` or `<color=name>...</color>` | Sets color by hex or one of 17 named colors (aqua, black, blue, brown, cyan, darkblue, fuchsia, green, grey, lightblue, lime, magenta, maroon, navy, olive, orange, purple, red, silver, teal, white, yellow) |
| `<material=N>...</material>` | Applies a material by index — Text Mesh (3D) objects only, not the UI `Text` component |
| `<quad .../>` | Inline image, self-closing — Text Mesh (3D) objects only |

Tags nest, and closing tags must appear in the reverse order of their
opening tags. Tag parameter values cannot contain spaces; closing tags
never repeat the parameter.

## Where rich text applies

Beyond the UI `Text` component itself, the same tag set works in
`Debug.Log`, `GUIText`, `TextMesh`, and (only when explicitly enabled via
`GUIStyle.richText`, since it's off by default) legacy IMGUI.

## Practical guidance

New screens use TextMeshPro, per the project's expectation to default to
`TMP_Text` for anything requiring rich text, style sheets, or more than the
five tags above — see
[textmeshpro-core-and-rich-text.md](textmeshpro-core-and-rich-text.md) for
the full, much larger tag set (alignment, gradients, sprites, links,
per-character rotation, and more). Reach for this file only when the task
is genuinely about an existing legacy `Text` element.
