# USS Styling & Flexbox Layout — Selectors, Precedence, Defaults

Sources: [Style UI](https://docs.unity3d.com/Manual/UIE-USS.html), [About USS](https://docs.unity3d.com/Manual/UIE-about-uss.html), [USS selectors](https://docs.unity3d.com/Manual/UIE-USS-Selectors.html), [Selector precedence](https://docs.unity3d.com/Manual/UIE-uss-selector-precedence.html), [Pseudo-classes](https://docs.unity3d.com/Manual/UIE-USS-Selectors-Pseudo-Classes.html), [Supported properties](https://docs.unity3d.com/Manual/UIE-USS-SupportedProperties.html), [Properties reference](https://docs.unity3d.com/Manual/UIE-USS-Properties-Reference.html), [Data types](https://docs.unity3d.com/Manual/UIE-USS-PropertyTypes.html), [Layout Engine](https://docs.unity3d.com/Manual/UIE-LayoutEngine.html), [Writing style sheets](https://docs.unity3d.com/Manual/UIE-USS-WritingStyleSheets.html), [USS variables (Builder)](https://docs.unity3d.com/Manual/UIB-styling-ui-using-uss-variables.html), [Built-in variable reference](https://docs.unity3d.com/Manual/UIE-uss-built-in-variable-reference.html), [Theme Style Sheets](https://docs.unity3d.com/Manual/UIE-tss.html), [Transitions](https://docs.unity3d.com/Manual/UIE-Transitions.html), [Positioning (Builder)](https://docs.unity3d.com/Packages/com.unity.ui.builder@1.0/manual/uib-styling-ui-positioning.html).
Covers: SKILL.md §4 — **"Style through USS selectors and BEM-style class names, never one-off inline styles"**, **"Verify a layout or CSS-parity assumption against USS's documented subset before trusting it"**.

USS is a documented **subset** of CSS with Unity-specific extensions and a
Flexbox layout engine whose defaults diverge from the web in one
frequently-costly way. This file is the authority on what that subset
actually supports; do not assume standard CSS behavior for anything not
listed here.

## Table of contents
- [USS vs CSS — the subset boundary](#uss-vs-css--the-subset-boundary)
- [Selectors and precedence](#selectors-and-precedence)
- [Pseudo-classes](#pseudo-classes)
- [Flexbox layout defaults](#flexbox-layout-defaults)
- [Property inheritance and animatability](#property-inheritance-and-animatability)
- [Variables and themes](#variables-and-themes)
- [Transitions](#transitions)

## USS vs CSS — the subset boundary

| Subject | What it decides | Source |
|---|---|---|
| Box model | Always equivalent to CSS `box-sizing: border-box` — width/height include padding and border; there is no `content-box` option | [Supported properties](https://docs.unity3d.com/Manual/UIE-USS-SupportedProperties.html) |
| `display` | Only a small subset of CSS values — effectively `flex` (default) or `none` | [Supported properties](https://docs.unity3d.com/Manual/UIE-USS-SupportedProperties.html) |
| `!important` | Not supported at all — no override-priority keyword exists in USS | [Selector precedence](https://docs.unity3d.com/Manual/UIE-uss-selector-precedence.html) |
| Not documented anywhere in the property/selector reference | `float`, `position: fixed`, CSS grid, `calc()`, `:nth-child()`, sibling selectors (`+`/`~`), `box-shadow`, elliptical `border-radius` — treat all as unsupported | [Supported properties](https://docs.unity3d.com/Manual/UIE-USS-SupportedProperties.html), [Selectors](https://docs.unity3d.com/Manual/UIE-USS-Selectors.html) |
| Identifier rules | Selector/class/variable names must start with a letter or underscore, never a digit; case-sensitive | [About USS](https://docs.unity3d.com/Manual/UIE-about-uss.html) |
| `-unity-` prefix | Marks a Unity-specific extension with no CSS analog at all — fonts, 9-slice, background scale mode, text outline/auto-size, `-unity-material` | [Properties reference](https://docs.unity3d.com/Manual/UIE-USS-Properties-Reference.html) |

## Selectors and precedence

| Selector | Form | Source |
|---|---|---|
| Type | `Button { }` — matches by C# type name, no namespace | [USS selectors](https://docs.unity3d.com/Manual/UIE-USS-Selectors.html) |
| Name | `#name { }` — analogous to a CSS ID selector | [USS selectors](https://docs.unity3d.com/Manual/UIE-USS-Selectors.html) |
| Class | `.class { }` — matches elements carrying that class via `AddToClassList` | [USS selectors](https://docs.unity3d.com/Manual/UIE-USS-Selectors.html) |
| Descendant / child | `A B` (anywhere under) / `A > B` (direct child) | [USS selectors](https://docs.unity3d.com/Manual/UIE-USS-Selectors.html) |
| Universal / `:root` | `*` matches any element; `:root` is the highest element the stylesheet applies to | [Pseudo-classes](https://docs.unity3d.com/Manual/UIE-USS-Selectors-Pseudo-Classes.html) |

| Precedence rule | What it decides | Source |
|---|---|---|
| Specificity order | Name selector > class selector > type selector > universal selector | [Selector precedence](https://docs.unity3d.com/Manual/UIE-uss-selector-precedence.html) |
| Tie-break within one file | Equal specificity → the **last** rule in the file wins | [Selector precedence](https://docs.unity3d.com/Manual/UIE-uss-selector-precedence.html) |
| Full override stack, low→high | Inherited styles → USS selector styles → inline UXML styles → C# `element.style.*` (always wins) | [Selector precedence](https://docs.unity3d.com/Manual/UIE-uss-selector-precedence.html) |
| Naming convention | Unity recommends **BEM** (`block`, `block__element`, `block__element--modifier`) to cap selector complexity and cost | [Writing style sheets](https://docs.unity3d.com/Manual/UIE-USS-WritingStyleSheets.html) |
| Selector cost model | Matching cost scales as classes-on-element × applicable-stylesheets; prefer `>` over descendant selectors and avoid trailing `*` | [Writing style sheets](https://docs.unity3d.com/Manual/UIE-USS-WritingStyleSheets.html) |

**Critical caveat**: prefer USS files over inline C# styles for anything
reused — inline styles carry per-element memory overhead, and `:hover`
selectors on elements with many descendants invalidate that entire subtree
on every mouse move; scope `:hover` narrowly.

## Pseudo-classes

| Class | Meaning | Source |
|---|---|---|
| `:hover` / `:active` / `:inactive` | Pointer over / actively pressed / interaction stopped | [Pseudo-classes](https://docs.unity3d.com/Manual/UIE-USS-Selectors-Pseudo-Classes.html) |
| `:focus` / `:disabled` / `:enabled` | Focus and enabled-state matching | [Pseudo-classes](https://docs.unity3d.com/Manual/UIE-USS-Selectors-Pseudo-Classes.html) |
| `:checked` | Matches a selected `Toggle` or `RadioButton` — **`:selected` does not exist**, this is the replacement | [Pseudo-classes](https://docs.unity3d.com/Manual/UIE-USS-Selectors-Pseudo-Classes.html) |
| Chaining | `Toggle:checked:hover` requires every chained condition simultaneously | [Pseudo-classes](https://docs.unity3d.com/Manual/UIE-USS-Selectors-Pseudo-Classes.html) |
| C# pseudo-state read gotcha | `hasFocusPseudoState` (and siblings) reads live state, but is **not yet updated** during `FocusInEvent`/`FocusOutEvent` itself — read it after the event finishes | [Check pseudo-state](https://docs.unity3d.com/Manual/ui-systems/check-pseudo-state.html) |

## Flexbox layout defaults

| Property | Unity default | Divergence from web CSS | Source |
|---|---|---|---|
| `flex-direction` | **`column`** | Web CSS defaults to `row` — the single most common "why did my children stack vertically" surprise | [Layout Engine](https://docs.unity3d.com/Manual/UIE-LayoutEngine.html) |
| `flex-grow` / `flex-shrink` / `flex-basis` | `0` / `1` / `auto` | Matches web Flexbox | [Properties reference](https://docs.unity3d.com/Manual/UIE-USS-Properties-Reference.html) |
| `position` | `relative` | Matches CSS; `absolute` removes the element from flex flow entirely | [Supported properties](https://docs.unity3d.com/Manual/UIE-USS-SupportedProperties.html) |
| `justify-content` / `align-items` / `flex-wrap` | `flex-start` / `stretch` / `nowrap` | Matches web Flexbox | [Supported properties](https://docs.unity3d.com/Manual/UIE-USS-SupportedProperties.html) |
| Absolute width formula | With both `left` and `right` set: `computed-width = parent-width - left - right` | Same as CSS absolute positioning | [Positioning (Builder)](https://docs.unity3d.com/Packages/com.unity.ui.builder@1.0/manual/uib-styling-ui-positioning.html) |

**Critical caveat**: Unity's layout engine implements a documented *subset*
of Flexbox (Yoga-derived) — every value above must be re-verified against
[Supported properties](https://docs.unity3d.com/Manual/UIE-USS-SupportedProperties.html)
before assuming a lesser-used Flexbox feature (e.g. `order`, `gap` on older
Unity versions) is present.

## Property inheritance and animatability

| Category | Behavior | Source |
|---|---|---|
| Inherited | `color`, `font-size`, `letter-spacing`, `word-spacing`, `visibility`, `white-space`, `text-shadow`, every `-unity-font*`/`-unity-text*` property, `-unity-material`, `-unity-paragraph-spacing` | [Properties reference](https://docs.unity3d.com/Manual/UIE-USS-Properties-Reference.html) |
| Not inherited | `flex*`, box-model properties, `background-*`, `opacity`, transform properties (`translate`/`scale`/`rotate`), `cursor`, `transition*` | [Properties reference](https://docs.unity3d.com/Manual/UIE-USS-Properties-Reference.html) |
| Fully animatable | `flex*`, box-model, `opacity`, `background-color`, transform properties, `-unity-material`, `filter`, `all` | [Properties reference](https://docs.unity3d.com/Manual/UIE-USS-Properties-Reference.html) |
| Discrete (jumps, does not tween) | `flex-direction`, `flex-wrap`, `align-*`, `justify-content`, `position`, `display`, `overflow`, `visibility`, `white-space`, `background-image` | [Properties reference](https://docs.unity3d.com/Manual/UIE-USS-Properties-Reference.html) |
| Non-animatable | `cursor`, `transition*` itself, `-unity-text-auto-size`, `-unity-text-generator` | [Properties reference](https://docs.unity3d.com/Manual/UIE-USS-Properties-Reference.html) |

## Variables and themes

| Subject | What it decides | Source |
|---|---|---|
| Custom property syntax | `--variable-name: <value>;`, referenced via `var(--variable-name)`; six supported value types — Color, Number, Dimension, String, Enum, Resource | [USS variables](https://docs.unity3d.com/Manual/UIB-styling-ui-using-uss-variables.html) |
| Scope | Define on `:root` for sheet-wide availability | [USS variables](https://docs.unity3d.com/Manual/UIB-styling-ui-using-uss-variables.html) |
| Duplicate name resolution | The variable defined **last** in the sheet wins | [USS variables](https://docs.unity3d.com/Manual/UIB-styling-ui-using-uss-variables.html) |
| Built-in `--unity-*` variables | Ship per-theme (Professional/dark, Personal/light, Runtime) — e.g. `--unity-metrics-default-border_radius: 3px`, `--unity-colors-button-background: #585858` (Professional) | [Built-in variable reference](https://docs.unity3d.com/Manual/UIE-uss-built-in-variable-reference.html) |
| Theme Style Sheet (TSS) | A regular `.uss` file typed as a theme asset, usually aggregating others via `@import`; the current/active TSS wins ties against sheets it imports | [Theme Style Sheets](https://docs.unity3d.com/Manual/UIE-tss.html) |
| Default runtime theme | The first UIDocument/Panel Renderer added auto-generates `Assets/UI Toolkit/UnityThemes/UnityDefaultTheme.tss` — import it or built-in controls render incorrectly | [Theme Style Sheets](https://docs.unity3d.com/Manual/UIE-tss.html) |

```css
/* USS custom property, root-scoped, then consumed */
:root {
    --accent-color: #2C5D87;
}
.hud-badge {
    background-color: var(--accent-color);
}
```

## Transitions

| Property | Default | Gotcha | Source |
|---|---|---|---|
| `transition-property` | `all` | Comma-separated list to scope it, e.g. `color, rotate` | [Transitions](https://docs.unity3d.com/Manual/UIE-Transitions.html) |
| `transition-duration` / `transition-delay` | `0s` | Both accept `s`/`ms` | [Transitions](https://docs.unity3d.com/Manual/UIE-Transitions.html) |
| `transition-timing-function` | `ease` | Also `linear`, `ease-in/out/in-out`, named curves (`ease-in-bounce`, etc.) | [Transitions](https://docs.unity3d.com/Manual/UIE-Transitions.html) |

**Critical caveat**: transitioning to/from `auto` requires an explicit unit
on both ends or the transition silently does not animate; a transition also
cannot play on the very first frame (no prior state to interpolate from).
Restrict transitions to transform properties (`translate`/`scale`/`rotate`)
where possible — animating layout properties triggers relayout every frame,
per [rendering-and-performance.md](rendering-and-performance.md).
