# TextMeshPro — UI Text Component and Rich Text Tags

Source: [UI Text GameObjects](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/TMPObjectUIText.html), [Rich Text](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/RichText.html), [Supported Rich Text Tags](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/RichTextSupportedTags.html), [Style Sheets](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/StyleSheets.html).
Covers: SKILL.md §4 — "Default new text to `TMP_Text`, not legacy `Text`", "Reach for a style sheet before repeating the same tag stack".

## The TMP UI Text component

A "TextMeshPro - Text (UI)" GameObject carries four pieces: `RectTransform`,
`CanvasRenderer`, the `TMP_Text` component itself, and a Material (one of
TMP's shaders — see [textmeshpro-assets-and-shaders.md](textmeshpro-assets-and-shaders.md)).
This is the UI/Canvas variant — it uses `CanvasRenderer` and `RectTransform`
like every other uGUI Graphic, unlike the separate 3D "Text Mesh Pro"
object variant meant for world-space text outside a Canvas.

Key inspector groups:

| Group | Covers |
|---|---|
| Text Input | The string itself, optional rich text markup, RTL editor toggle, and picking a predefined Style Sheet style |
| Font Settings | Font asset + material preset, Bold/Italic/Underline/Strikethrough, case conversion, small caps, **Auto Size** (shrinks/grows to fit within a min/max point range and a character-width reduction limit) |
| Color | A base vertex color plus an optional gradient — Single Color, Horizontal, Vertical, or Four-Corner modes; the gradient multiplies with the vertex color, it doesn't replace it |
| Spacing & Alignment | Character/word/line/paragraph spacing; horizontal alignment (left/center/right/justified/flush/geometry-center); vertical alignment (top/middle/bottom/baseline/midline/capline) |
| Wrapping & Overflow | Text Wrapping Mode (no wrap / normal / preserve whitespace); Overflow (extend past bounds / ellipsis / mask / truncate / page / link to another TMP object) |
| Extra Settings | Margins, geometry sorting order (normal/reverse), scale, rich-text-enabled toggle, raycast target, masking, escape-character parsing, descender visibility, emoji support, extra padding |

## Rich text tags — the full set

TMP's tag set is much larger than legacy `Text`'s (per
[legacy-text-and-rich-text.md](legacy-text-and-rich-text.md)):

| Tag | Purpose |
|---|---|
| `<align>` | Horizontal alignment for the enclosed run |
| `<allcaps>` / `<uppercase>` | Renders as uppercase without changing the source string |
| `<alpha=#xx>` | Sets opacity |
| `<b>` | Bold |
| `<br>` | Forces a line break |
| `<color>` | Sets color (and optionally opacity) |
| `<cspace>` | Character spacing |
| `<font>` | Switches font asset (and optionally its material) mid-string |
| `<font-weight>` | Selects a typographic weight variant from the font asset |
| `<gradient>` | Applies a named gradient preset |
| `<i>` | Italic |
| `<indent>` | Indents everything up to the next hard line break |
| `<line-height>` | Overrides line height relative to the font default |
| `<line-indent>` | Indents only the first line after a hard break |
| `<link>` | Tags a run with an ID for hit-testing (`TMP_TextInfo.linkInfo`) — the mechanism behind clickable in-text links |
| `<lowercase>` | Renders lowercase |
| `<margin>` | Horizontal margins |
| `<mark>` | Colored highlight behind the text (a text-marker effect) |
| `<mspace>` | Renders as monospace at a given advance width |
| `<nobr>` | Prevents the enclosed run from breaking across lines |
| `<noparse>` | Disables tag parsing for the enclosed text — the escape hatch for literal `<`/`>` content |
| `<page>` | Inserts a page break (paired with Overflow: Page) |
| `<pos>` | Sets an explicit horizontal caret position on the current line |
| `<rotate>` | Rotates each enclosed character about its own center |
| `<s>` / `<strikethrough>` | Strikethrough |
| `<size>` | Font size for the enclosed run |
| `<smallcaps>` | Renders as uppercase at a reduced size for lowercase letters |
| `<space>` | Inserts a fixed horizontal gap |
| `<sprite>` | Inlines a sprite (see [textmeshpro-assets-and-shaders.md](textmeshpro-assets-and-shaders.md)) |
| `<style>` | Applies a named custom style (see Style Sheets below) |
| `<sub>` / `<sup>` | Subscript / superscript |
| `<u>` | Underline |
| `<voffset>` | Vertical baseline offset |
| `<width>` | Constrains the horizontal size of the enclosed text area |

Tags nest and close in reverse order, same as legacy `Text`'s smaller set.

## Style Sheets

A **TextMesh Pro Style Sheet** asset (`Assets > Create > TextMesh Pro >
Style Sheet`) defines named styles, each bundling an opening/closing rich
text tag stack plus optional leading/trailing text — so instead of writing
`<font-weight=700><size=2em><color=#FF0000>Heading</color></size></font-weight>`
inline every time, define an `H1` style once and write
`<style="H1">Heading</style>`. TMP ships a default style sheet (under
TextMesh Pro's Resources/Style Sheets) that can be swapped project-wide via
TMP Settings, or overridden per-object in that object's Extra Settings.

**Prefer a style sheet over repeating the same tag stack across many
strings** — per DRY/KISS in `coding-principles.md`, a style edited in one
place beats hunting down every inline tag combination when a heading style
changes.
