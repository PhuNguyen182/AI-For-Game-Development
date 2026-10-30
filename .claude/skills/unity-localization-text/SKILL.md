---
name: unity-localization-text
description: "Localization 1.5: String Tables, Smart Strings plurals, LocalizeStringEvent, LocalizedString, InitializationOperation, SelectedLocaleChanged, pseudo-locale Expander, TMP fallback per script. Use when player-facing text ships in several languages."
user-invocable: false
---

# Unity Localization Text

Not for: Editor table automation, batch component wiring, CJK font asset creation and Asset Table font swaps (`unity:localization`), TMP atlas tuning — padding, sampling size, AutoSize, Dynamic OS, Clear Dynamic Data (`unity:optimize-text-mesh-pro`), TMP rich text and Style Sheets (`ugui`), UI Toolkit font assets (`ui-toolkit`), Addressables groups and content builds (`unity-addressables`), allocation-free string building (`zstring-zero-allocation-strings`), RTL shaping and mirrored layout (no owner — known limitation).
Docs: https://docs.unity3d.com/Packages/com.unity.localization@1.5/ — package 1.5.13. Unity 6.7+ ships a built-in Localization Runtime with different components: re-check every API name there. TMP: https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/ (uGUI 2.6.0, as in `ugui`).

| Reference | Read when |
|---|---|
| [string-tables-and-smart-strings.md](references/string-tables-and-smart-strings.md) | Reading a string from code, binding a label, a string shows late or as a missing-translation message, writing a plural or variable entry |
| [font-fallback-and-expansion.md](references/font-fallback-and-expansion.md) | Adding a locale with a new script, tofu or atlas memory growth, or text clips in a longer language |

## Steps
1. **Confirm the stack and version.** `com.unity.localization` 1.5.x in `Packages/packages-lock.json` → this skill. Unity 6.7+ built-in Localization Runtime → read its manual before applying any name here, per [string-tables-and-smart-strings.md](references/string-tables-and-smart-strings.md). Package absent → install and settings per `unity:localization` §0–1.
2. **Locale list unstated → `Blocked` naming the locale list (`Next: gd`).** It decides scripts, fonts and atlas memory; the GD names the shipped locales.
3. **Keep text out of Core.** Core emits ids, enums and counts; Client code maps them to table entries (`csharp.md` → Boundaries). Criterion: no table key, `LocalizedString` or player-facing literal in Core.
4. **Every player-facing string comes from a String Table.** Authored uGUI labels: `LocalizeStringEvent`; UI Toolkit: a `LocalizedString` binding; code-composed text: a `LocalizedString` with Smart arguments — never concatenated localized fragments (word order differs per language). Find literals with the `unity:localization` §6 scan. Criterion: every site found is converted or listed as GD-accepted; debug-only text is exempt.
5. **Await `LocalizationSettings.InitializationOperation` before the first code read**, and check it succeeded. Components wait on their own; scripts do not. Prefer the async read; WebGL has no `WaitForCompletion`. Per [string-tables-and-smart-strings.md](references/string-tables-and-smart-strings.md). A table needed on the first frame of a screen → mark it Preload.
6. **React to a locale change by subscription.** `LocalizedString.StringChanged` for one string, `LocalizationSettings.SelectedLocaleChanged` for anything else; unsubscribe in `OnDisable` (`csharp.md` → Hot paths). Switch locale only by assigning `SelectedLocale` (`unity:localization` §3).
7. **Write variables and plurals as Smart entries.** Mark the entry Smart; plurals use the CLDR forms of every target locale, not English's two; pass raw numbers so the table culture formats them. Give translators a comment per entry. The default parse error action throws, so render every Smart entry in every locale before shipping.
8. **One font asset per script, with its atlas cost stated.** List the scripts each shipped locale needs. The locale's own UI text → per-locale font swap through an Asset Table (`unity:localization` §4). Text that can mix scripts in any locale (player names, chat, user content) → one dynamic fallback per script on the primary's local list. Never two assets covering one script. Criterion: Output lists script → asset → mode → atlas size → MB, per [font-fallback-and-expansion.md](references/font-fallback-and-expansion.md).
9. **Size containers for expansion.** Labels wrap or grow from anchors and layout (`ugui`, `ui-toolkit`); AutoSize only on static labels (`unity:optimize-text-mesh-pro`). The expansion table in [font-fallback-and-expansion.md](references/font-fallback-and-expansion.md) is a hint, the pseudo-locale pass is the gate.
10. **Run the pseudo-locale check on every screen at each target aspect ratio** (aspect set per `mobile-safe-area` step 9): Preserve Tags first, then Accenter, Expander (default rules), Encapsulator. Criterion: no clipping, overflow or overlap; every visible string bracketed — a missing bracket is a hard-coded, concatenated or truncated string. Then the table completeness check (`unity:localization` §5) and a tofu check in each real locale.

## Never
- Persist or send a localized string (save data, network, analytics): the value changes with the locale; store the key or id.
- Branch on displayed text (`label.text == "OK"`): it breaks in every other locale.
- Format a value with `ToString()` or `$"..."` before passing it to a Smart String: it bypasses the table culture and plural rules.
- Use user content (player names, chat) as the format string or render it with TMP rich text on: it is only ever a Smart String argument, with `richText` off on its text object or its `<` escaped — otherwise a name injects tags or a malformed placeholder throws.

## Output
```
## Localization — <screen / feature>
- Package: <com.unity.localization version, or built-in Localization Runtime>
- Locales: <list>; tables: <collections, preload behaviour>
- Initialization: <where InitializationOperation is awaited and its failure path>
- Strings: <LocalizeStringEvent / LocalizedString binding / Smart entries; §6 scan: found N, converted M, accepted K>
- Fonts: <script → font asset, mode, atlas size, MB; swap or fallback>
- Expansion: <pseudo-locale result per screen × aspect ratio, screenshot path>
- Completeness: <§5 check output>
- Verified: <evidence, or "not run">
- Known limitations: RTL locales excluded; <...>
```

## Example
- "Use one Arial Unicode font asset for every language, it is simpler" → declined: one dynamic asset for all scripts grows multi-atlas pages in every locale; split per script so each locale loads only its own atlas, and stated the MB per asset.
