# TextMeshPro — UI Text and Rich Text

"TextMeshPro - Text (UI)" = `RectTransform` + `CanvasRenderer` + `TMP_Text` + a TMP-shader Material ([textmeshpro-assets-and-shaders.md](textmeshpro-assets-and-shaders.md)). The separate 3D "Text Mesh Pro" object is for text outside a Canvas.

| Inspector group | Notable |
|---|---|
| Font Settings | Font asset + material preset, styles, case, small caps, **Auto Size** (min/max point range + character-width reduction limit) |
| Color | Vertex color plus optional gradient (Single, Horizontal, Vertical, Four-Corner); the gradient multiplies the vertex color |
| Spacing & Alignment | Character/word/line/paragraph spacing; horizontal and vertical alignment modes |
| Wrapping & Overflow | Wrapping (no wrap / normal / preserve whitespace); Overflow: extend, ellipsis, mask, truncate, page, link to another TMP object |
| Extra Settings | Margins, sorting order, rich-text toggle, raycast target, masking, escape parsing, emoji, extra padding |

## Rich text tags
Tags nest and close in reverse order.

| Tag | Purpose |
|---|---|
| `<align>` | Horizontal alignment of the run |
| `<allcaps>` / `<uppercase>`, `<lowercase>`, `<smallcaps>` | Case rendering without changing the string |
| `<alpha=#xx>` | Opacity |
| `<b>` `<i>` `<u>` `<s>`/`<strikethrough>` `<sub>` `<sup>` | Style |
| `<br>` | Line break |
| `<color>` | Color (optionally opacity) |
| `<cspace>` `<mspace>` `<space>` `<pos>` | Character spacing, monospace advance, fixed gap, explicit caret position |
| `<font>` `<font-weight>` | Switch font asset/material mid-string; weight variant |
| `<gradient>` | Named gradient preset |
| `<indent>` `<line-indent>` `<line-height>` `<margin>` `<width>` | Indent to next hard break; first-line indent; line height; horizontal margins; text-area width |
| `<link>` | Run ID for hit-testing via `TMP_TextInfo.linkInfo` (clickable links) |
| `<mark>` | Highlight behind text |
| `<nobr>` | No line break inside the run |
| `<noparse>` | Literal `<`/`>` content |
| `<page>` | Page break (with Overflow: Page) |
| `<rotate>` | Rotate each character about its centre |
| `<size>` `<voffset>` | Font size; baseline offset |
| `<sprite>` | Inline sprite |
| `<style>` | Named Style Sheet style |

## Style Sheets
`Assets > Create > TextMesh Pro > Style Sheet` defines named styles, each an opening/closing tag stack plus optional leading/trailing text. Define `H1` once and write `<style="H1">Heading</style>` instead of repeating the tag stack. The default sheet is swappable project-wide in TMP Settings or per object in Extra Settings.
