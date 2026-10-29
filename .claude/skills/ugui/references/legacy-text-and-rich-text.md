# Legacy Text — Rich Text Tags

Only for maintaining an existing legacy `Text` screen. New work uses TMP ([textmeshpro-core-and-rich-text.md](textmeshpro-core-and-rich-text.md)), whose tag set is far larger.

| Tag | Effect |
|---|---|
| `<b>` `<i>` | Bold, italic |
| `<size=N>` | Pixel size |
| `<color=#rrggbbaa>` / `<color=name>` | Hex or one of 17 names (aqua, black, blue, brown, cyan, darkblue, fuchsia, green, grey, lightblue, lime, magenta, maroon, navy, olive, orange, purple, red, silver, teal, white, yellow) |
| `<material=N>`, `<quad .../>` | Text Mesh (3D) only, not UI `Text` |

Tags nest and close in reverse order; parameter values cannot contain spaces; closing tags omit the parameter. The same tags work in `Debug.Log`, `GUIText`, `TextMesh`, and IMGUI only when `GUIStyle.richText` is enabled (off by default).
