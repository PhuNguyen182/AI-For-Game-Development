# USS styling and layout

Sources: [USS](https://docs.unity3d.com/Manual/UIE-USS.html), [Selectors](https://docs.unity3d.com/Manual/UIE-USS-Selectors.html), [Precedence](https://docs.unity3d.com/Manual/UIE-uss-selector-precedence.html), [Pseudo-classes](https://docs.unity3d.com/Manual/UIE-USS-Selectors-Pseudo-Classes.html), [Supported props](https://docs.unity3d.com/Manual/UIE-USS-SupportedProperties.html), [Props reference](https://docs.unity3d.com/Manual/UIE-USS-Properties-Reference.html), [Writing](https://docs.unity3d.com/Manual/UIE-USS-WritingStyleSheets.html), [Variables](https://docs.unity3d.com/Manual/UIB-styling-ui-using-uss-variables.html), [TSS](https://docs.unity3d.com/Manual/UIE-tss.html), [Transitions](https://docs.unity3d.com/Manual/UIE-Transitions.html).

## USS vs CSS
- Box model is always `border-box`.
- `display`: effectively `flex` (default) or `none`.
- Unsupported (not in the property/selector reference): `!important`, `float`, `position: fixed`, grid, `calc()`, `:nth-child()`, sibling selectors (`+`/`~`), `box-shadow`, elliptical `border-radius`.
- Identifiers start with a letter or underscore; case-sensitive.
- `-unity-` prefix = Unity-only extension (fonts, 9-slice, background scale, text outline/auto-size, `-unity-material`).

## Selectors and precedence
- Forms: `Button` (C# type, no namespace), `#name`, `.class` (`AddToClassList`), `A B`, `A > B`, `*`, `:root`.
- Specificity: name > class > type > universal; ties → last rule in the file.
- Override stack, low→high: inherited → USS → inline UXML → C# `element.style.*` (always wins).
- Use BEM (`block__element--modifier`). Match cost scales with classes-on-element × applicable sheets: prefer `>` over descendant, avoid trailing `*`.
- `:hover` on elements with many descendants invalidates the subtree on every mouse move: scope it narrowly.

## Pseudo-classes
- `:hover` `:active` `:inactive` `:focus` `:disabled` `:enabled` `:checked` (selected `Toggle`/`RadioButton`; `:selected` does not exist). Chained conditions must all hold.
- `hasFocusPseudoState` and siblings are not yet updated during `FocusInEvent`/`FocusOutEvent`: read after the event ([docs](https://docs.unity3d.com/Manual/ui-systems/check-pseudo-state.html)).

## Flexbox defaults
- `flex-direction` is `column` (web: `row`).
- `flex-grow/shrink/basis` `0/1/auto`, `position: relative`, `justify-content: flex-start`, `align-items: stretch`, `flex-wrap: nowrap`: as web.
- `absolute` removes the element from flex flow; with `left` and `right` set, width = parent − left − right.
- Layout is a Yoga-derived subset: verify lesser-used features (`order`, `gap` on older Unity) against Supported props.

## Inheritance and animatability
| Category | Properties |
|---|---|
| Inherited | `color`, `font-size`, `letter-spacing`, `word-spacing`, `visibility`, `white-space`, `text-shadow`, all `-unity-font*`/`-unity-text*`, `-unity-material`, `-unity-paragraph-spacing` |
| Not inherited | `flex*`, box model, `background-*`, `opacity`, `translate`/`scale`/`rotate`, `cursor`, `transition*` |
| Animatable | `flex*`, box model, `opacity`, `background-color`, transforms, `-unity-material`, `filter`, `all` |
| Discrete (jump) | `flex-direction`, `flex-wrap`, `align-*`, `justify-content`, `position`, `display`, `overflow`, `visibility`, `white-space`, `background-image` |
| Not animatable | `cursor`, `transition*`, `-unity-text-auto-size`, `-unity-text-generator` |

## Variables and themes
- `--name: value;` on `:root` (sheet-wide), used as `var(--name)`; types: Color, Number, Dimension, String, Enum, Resource. Duplicate name → last wins.
- Built-in `--unity-*` variables ship per theme (Professional/dark, Personal/light, Runtime).
- Theme Style Sheet (TSS): a `.uss` typed as a theme, usually `@import`s others; the active TSS wins ties against imported sheets.
- First `UIDocument`/Panel Renderer auto-generates `Assets/UI Toolkit/UnityThemes/UnityDefaultTheme.tss`: import it or built-in controls render wrong.

## Transitions
- Defaults: `transition-property: all`, duration/delay `0s`, timing `ease`. `transition-property` takes a comma list to scope it (e.g. `color, rotate`); duration and delay accept `s` or `ms`; timing-function also takes `linear`, `ease-in`/`ease-out`/`ease-in-out` and named curves.
- Transitioning to/from `auto` needs an explicit unit on both ends or it silently does not animate; no transition plays on the first frame.
- Keep transitions on transform properties; layout properties relayout every frame ([rendering-and-performance.md](rendering-and-performance.md)).
